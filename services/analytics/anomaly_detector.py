"""Anomaly detection for analytics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from threading import RLock
import statistics
import uuid
from .event_collector import Event


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    metric_name: str
    expected_value: float
    actual_value: float
    z_score: float
    timestamp: datetime
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'anomaly_id': self.anomaly_id,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'metric_name': self.metric_name,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'z_score': self.z_score,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
        }


class AnomalyDetector:
    """Detects anomalies in metrics and events."""

    def __init__(self, z_score_threshold: float = 2.5):
        """Initialize anomaly detector.
        
        Args:
            z_score_threshold: Z-score threshold for detection (default 2.5)
        """
        self.lock = RLock()
        self.z_score_threshold = z_score_threshold
        self.anomalies: List[Anomaly] = []
        self.baseline_data: Dict[str, List[float]] = {}

    def detect_statistical_anomalies(
        self,
        events: List[Event],
        threshold: Optional[float] = None,
    ) -> List[Anomaly]:
        """Detect statistical anomalies using Z-score.
        
        Args:
            events: Events to analyze
            threshold: Optional Z-score threshold override
            
        Returns:
            List of detected anomalies
        """
        with self.lock:
            threshold = threshold or self.z_score_threshold
            anomalies = []

            # Collect latencies
            durations = [e.duration_ms for e in events if e.duration_ms is not None]

            if len(durations) < 3:
                return anomalies

            mean = statistics.mean(durations)
            stdev = statistics.stdev(durations) if len(durations) > 1 else 0

            if stdev == 0:
                return anomalies

            # Find anomalies
            for event in events:
                if event.duration_ms is None:
                    continue

                z_score = abs((event.duration_ms - mean) / stdev)

                if z_score > threshold:
                    anomalies.append(Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        anomaly_type='statistical',
                        severity=self._calculate_severity(z_score),
                        metric_name='latency',
                        expected_value=mean,
                        actual_value=event.duration_ms,
                        z_score=z_score,
                        timestamp=event.timestamp,
                        description=f'Latency anomaly: {event.duration_ms:.2f}ms (expected ~{mean:.2f}ms)',
                    ))

            self.anomalies.extend(anomalies)
            return anomalies

    def detect_temporal_anomalies(
        self,
        events: List[Event],
        window_size: int = 10,
    ) -> List[Anomaly]:
        """Detect temporal anomalies (unusual patterns).
        
        Args:
            events: Events to analyze
            window_size: Time window size
            
        Returns:
            List of detected anomalies
        """
        with self.lock:
            anomalies = []

            if len(events) < window_size:
                return anomalies

            # Group events by time windows
            from collections import defaultdict
            time_windows = defaultdict(int)

            for event in events:
                window = event.timestamp.replace(minute=0, second=0, microsecond=0)
                time_windows[window] += 1

            if not time_windows:
                return anomalies

            # Analyze patterns
            counts = list(time_windows.values())
            if len(counts) > 2:
                mean_count = statistics.mean(counts)
                stdev_count = statistics.stdev(counts)

                for window, count in time_windows.items():
                    if stdev_count > 0:
                        z_score = abs((count - mean_count) / stdev_count)

                        if z_score > 2.0:
                            anomalies.append(Anomaly(
                                anomaly_id=str(uuid.uuid4()),
                                anomaly_type='temporal',
                                severity=self._calculate_severity(z_score),
                                metric_name='event_frequency',
                                expected_value=mean_count,
                                actual_value=float(count),
                                z_score=z_score,
                                timestamp=datetime.now(),
                                description=f'Unusual event frequency at {window}: {count} events',
                            ))

            self.anomalies.extend(anomalies)
            return anomalies

    def detect_performance_degradation(
        self,
        events: List[Event],
        degradation_threshold: float = 20.0,
    ) -> List[Anomaly]:
        """Detect performance degradation.
        
        Args:
            events: Events to analyze
            degradation_threshold: Percentage threshold
            
        Returns:
            List of detected anomalies
        """
        with self.lock:
            anomalies = []

            if len(events) < 5:
                return anomalies

            # Split events into recent and historical
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            split_index = len(sorted_events) // 2

            historical = sorted_events[:split_index]
            recent = sorted_events[split_index:]

            # Calculate average latencies
            historical_durations = [
                e.duration_ms for e in historical
                if e.duration_ms is not None
            ]
            recent_durations = [
                e.duration_ms for e in recent
                if e.duration_ms is not None
            ]

            if not historical_durations or not recent_durations:
                return anomalies

            historical_avg = statistics.mean(historical_durations)
            recent_avg = statistics.mean(recent_durations)

            # Check for degradation
            degradation = ((recent_avg - historical_avg) / historical_avg) * 100

            if degradation > degradation_threshold:
                anomalies.append(Anomaly(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type='performance_degradation',
                    severity='high',
                    metric_name='latency',
                    expected_value=historical_avg,
                    actual_value=recent_avg,
                    z_score=degradation / 10.0,
                    timestamp=datetime.now(),
                    description=f'Performance degradation detected: {degradation:.1f}% increase in latency',
                ))

            self.anomalies.extend(anomalies)
            return anomalies

    def detect_error_spike(self, events: List[Event]) -> List[Anomaly]:
        """Detect error rate spikes.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of detected anomalies
        """
        with self.lock:
            anomalies = []

            if not events:
                return anomalies

            # Count errors by time window
            from collections import defaultdict
            time_windows = defaultdict(int)
            total_by_window = defaultdict(int)

            for event in events:
                window = event.timestamp.replace(minute=0, second=0, microsecond=0)
                total_by_window[window] += 1

                if event.error:
                    time_windows[window] += 1

            if not time_windows:
                return anomalies

            # Calculate error rates
            error_rates = {}
            for window in total_by_window:
                if window in time_windows:
                    error_rates[window] = (
                        time_windows[window] / total_by_window[window]
                    ) * 100

            if len(error_rates) < 2:
                return anomalies

            # Find anomalous error rates
            rates = list(error_rates.values())
            mean_rate = statistics.mean(rates)
            stdev_rate = statistics.stdev(rates) if len(rates) > 1 else 0

            for window, rate in error_rates.items():
                if stdev_rate > 0:
                    z_score = abs((rate - mean_rate) / stdev_rate)

                    if z_score > 2.0:
                        anomalies.append(Anomaly(
                            anomaly_id=str(uuid.uuid4()),
                            anomaly_type='error_spike',
                            severity='high' if z_score > 3.0 else 'medium',
                            metric_name='error_rate',
                            expected_value=mean_rate,
                            actual_value=rate,
                            z_score=z_score,
                            timestamp=datetime.now(),
                            description=f'Error rate spike at {window}: {rate:.1f}%',
                        ))

            self.anomalies.extend(anomalies)
            return anomalies

    def is_anomalous(
        self,
        metric_name: str,
        value: float,
        threshold: Optional[float] = None,
    ) -> Tuple[bool, float]:
        """Check if a value is anomalous.
        
        Args:
            metric_name: Name of metric
            value: Value to check
            threshold: Optional threshold override
            
        Returns:
            Tuple of (is_anomalous, z_score)
        """
        with self.lock:
            threshold = threshold or self.z_score_threshold

            if metric_name not in self.baseline_data:
                return False, 0.0

            baseline = self.baseline_data[metric_name]

            if len(baseline) < 2:
                return False, 0.0

            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline)

            if stdev == 0:
                return False, 0.0

            z_score = abs((value - mean) / stdev)

            return z_score > threshold, z_score

    def get_anomalies(
        self,
        severity: Optional[str] = None,
        anomaly_type: Optional[str] = None,
    ) -> List[Anomaly]:
        """Get detected anomalies with optional filtering.
        
        Args:
            severity: Filter by severity
            anomaly_type: Filter by type
            
        Returns:
            List of anomalies
        """
        with self.lock:
            anomalies = self.anomalies

            if severity:
                anomalies = [a for a in anomalies if a.severity == severity]

            if anomaly_type:
                anomalies = [a for a in anomalies if a.anomaly_type == anomaly_type]

            return anomalies

    def clear_anomalies(self) -> None:
        """Clear detected anomalies."""
        with self.lock:
            self.anomalies.clear()

    def set_baseline(self, metric_name: str, values: List[float]) -> None:
        """Set baseline data for a metric.
        
        Args:
            metric_name: Metric name
            values: Baseline values
        """
        with self.lock:
            self.baseline_data[metric_name] = values

    @staticmethod
    def _calculate_severity(z_score: float) -> str:
        """Calculate severity from Z-score.
        
        Args:
            z_score: Z-score value
            
        Returns:
            Severity level
        """
        if z_score > 4.0:
            return 'critical'
        elif z_score > 3.0:
            return 'high'
        elif z_score > 2.5:
            return 'medium'
        else:
            return 'low'

    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'total_anomalies': len(self.anomalies),
                'baseline_metrics': len(self.baseline_data),
                'z_score_threshold': self.z_score_threshold,
            }
