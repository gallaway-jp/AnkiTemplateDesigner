"""Metrics analysis from collected events."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from threading import RLock
import statistics
from .event_collector import Event


@dataclass
class Metric:
    """Represents a computed metric."""
    metric_name: str
    value: float
    timestamp: datetime
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    percentile: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'unit': self.unit,
            'tags': self.tags,
            'percentile': self.percentile,
        }


@dataclass
class TimeSeriesMetric:
    """Represents time-series metric data."""
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    aggregation: str  # hourly, daily, weekly

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'values': self.values,
            'timestamps': [ts.isoformat() for ts in self.timestamps],
            'aggregation': self.aggregation,
        }


class MetricsAnalyzer:
    """Analyzes events and computes metrics."""

    def __init__(self):
        """Initialize metrics analyzer."""
        self.lock = RLock()
        self.metrics: Dict[str, Metric] = {}
        self.metric_cache: Dict[str, Tuple[Metric, float]] = {}
        self.cache_ttl_seconds = 300

    def analyze_events(self, events: List[Event]) -> Dict[str, Metric]:
        """Analyze events and compute metrics.
        
        Args:
            events: List of events to analyze
            
        Returns:
            Dictionary of computed metrics
        """
        with self.lock:
            metrics = {}

            # Duration metrics
            durations = [e.duration_ms for e in events if e.duration_ms is not None]
            if durations:
                metrics['latency_mean'] = Metric(
                    metric_name='latency_mean',
                    value=statistics.mean(durations),
                    timestamp=datetime.now(),
                    unit='ms',
                )
                metrics['latency_p95'] = Metric(
                    metric_name='latency_p95',
                    value=self._percentile(durations, 95),
                    timestamp=datetime.now(),
                    unit='ms',
                    percentile=95,
                )
                metrics['latency_p99'] = Metric(
                    metric_name='latency_p99',
                    value=self._percentile(durations, 99),
                    timestamp=datetime.now(),
                    unit='ms',
                    percentile=99,
                )

            # Event count metrics
            event_counts = defaultdict(int)
            for event in events:
                event_counts[event.event_type] += 1

            for event_type, count in event_counts.items():
                metrics[f'event_count_{event_type}'] = Metric(
                    metric_name=f'event_count_{event_type}',
                    value=float(count),
                    timestamp=datetime.now(),
                    unit='count',
                )

            # Error rate
            error_count = sum(1 for e in events if e.error is not None)
            if events:
                error_rate = (error_count / len(events)) * 100
                metrics['error_rate'] = Metric(
                    metric_name='error_rate',
                    value=error_rate,
                    timestamp=datetime.now(),
                    unit='%',
                )

            # Category metrics
            category_counts = defaultdict(int)
            for event in events:
                category_counts[event.category] += 1

            for category, count in category_counts.items():
                metrics[f'category_{category}'] = Metric(
                    metric_name=f'category_{category}',
                    value=float(count),
                    timestamp=datetime.now(),
                    unit='count',
                )

            # Store in cache
            for name, metric in metrics.items():
                self.metrics[name] = metric

            return metrics

    def get_metric(self, metric_name: str) -> Optional[Metric]:
        """Get a metric by name.
        
        Args:
            metric_name: Name of metric
            
        Returns:
            Metric or None
        """
        with self.lock:
            return self.metrics.get(metric_name)

    def get_metrics(self, metric_names: Optional[List[str]] = None) -> Dict[str, Metric]:
        """Get multiple metrics.
        
        Args:
            metric_names: List of metric names (all if None)
            
        Returns:
            Dictionary of metrics
        """
        with self.lock:
            if metric_names is None:
                return dict(self.metrics)

            return {
                name: metric
                for name, metric in self.metrics.items()
                if name in metric_names
            }

    def calculate_percentiles(
        self,
        values: List[float],
        percentiles: List[float],
    ) -> Dict[float, float]:
        """Calculate percentiles for values.
        
        Args:
            values: Values to analyze
            percentiles: Percentiles to calculate (0-100)
            
        Returns:
            Dictionary of percentile -> value
        """
        with self.lock:
            if not values:
                return {}

            result = {}
            for p in percentiles:
                result[p] = self._percentile(values, p)

            return result

    def get_time_series_metrics(
        self,
        events: List[Event],
        metric_name: str,
        aggregation: str = 'hourly',
    ) -> Optional[TimeSeriesMetric]:
        """Get time series metrics for events.
        
        Args:
            events: Events to aggregate
            metric_name: Name of metric (e.g., 'latency', 'error_rate')
            aggregation: Aggregation period (hourly, daily, weekly)
            
        Returns:
            TimeSeriesMetric or None
        """
        with self.lock:
            if not events:
                return None

            # Group by time period
            periods = defaultdict(list)
            for event in events:
                if aggregation == 'hourly':
                    key = event.timestamp.replace(minute=0, second=0, microsecond=0)
                elif aggregation == 'daily':
                    key = event.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                else:  # weekly
                    key = event.timestamp - timedelta(days=event.timestamp.weekday())
                    key = key.replace(hour=0, minute=0, second=0, microsecond=0)

                periods[key].append(event)

            # Compute metric for each period
            values = []
            timestamps = []

            for period in sorted(periods.keys()):
                period_events = periods[period]

                if metric_name == 'latency_mean':
                    durations = [
                        e.duration_ms for e in period_events
                        if e.duration_ms is not None
                    ]
                    if durations:
                        values.append(statistics.mean(durations))
                        timestamps.append(period)

                elif metric_name == 'error_rate':
                    error_count = sum(1 for e in period_events if e.error)
                    error_rate = (error_count / len(period_events)) * 100
                    values.append(error_rate)
                    timestamps.append(period)

                elif metric_name == 'event_count':
                    values.append(float(len(period_events)))
                    timestamps.append(period)

            if not values:
                return None

            return TimeSeriesMetric(
                metric_name=metric_name,
                values=values,
                timestamps=timestamps,
                aggregation=aggregation,
            )

    def get_aggregate(
        self,
        events: List[Event],
        metric_name: str,
        operation: str = 'count',
    ) -> float:
        """Calculate aggregate metric.
        
        Args:
            events: Events to aggregate
            metric_name: Type of metric
            operation: count, sum, mean, min, max, median
            
        Returns:
            Computed value
        """
        with self.lock:
            if not events:
                return 0.0

            if metric_name == 'latency':
                durations = [
                    e.duration_ms for e in events
                    if e.duration_ms is not None
                ]
                if not durations:
                    return 0.0

                if operation == 'mean':
                    return statistics.mean(durations)
                elif operation == 'median':
                    return statistics.median(durations)
                elif operation == 'min':
                    return min(durations)
                elif operation == 'max':
                    return max(durations)
                elif operation == 'sum':
                    return sum(durations)
                else:  # count
                    return float(len(durations))

            elif metric_name == 'error_count':
                count = sum(1 for e in events if e.error)
                return float(count)

            elif metric_name == 'event_count':
                return float(len(events))

            return 0.0

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile.
        
        Args:
            values: Values to analyze
            percentile: Percentile (0-100)
            
        Returns:
            Percentile value
        """
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1

        if upper >= len(sorted_values):
            return float(sorted_values[-1])

        fraction = index - lower
        return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction

    def clear(self) -> None:
        """Clear all metrics."""
        with self.lock:
            self.metrics.clear()
            self.metric_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'total_metrics': len(self.metrics),
                'cached_metrics': len(self.metric_cache),
                'cache_ttl_seconds': self.cache_ttl_seconds,
            }
