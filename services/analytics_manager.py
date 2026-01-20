"""Analytics manager - main orchestrator for analytics system."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from threading import RLock
import json
from services.analytics import (
    EventCollector,
    Event,
    MetricsAnalyzer,
    Metric,
    TemplateIntelligence,
    AnomalyDetector,
    InsightGenerator,
    AnalyticsStorage,
)


class AnalyticsManager:
    """Main orchestrator for analytics system."""

    def __init__(self, db_path: Optional[str] = None, user_id: Optional[str] = None):
        """Initialize analytics manager.
        
        Args:
            db_path: Path to analytics database
            user_id: User identifier
        """
        self.lock = RLock()
        self.enabled = True
        self.retention_days = 90
        self.event_sampling_rate = 1.0

        # Initialize components
        self.event_collector = EventCollector(user_id=user_id)
        self.metrics_analyzer = MetricsAnalyzer()
        self.template_intelligence = TemplateIntelligence()
        self.anomaly_detector = AnomalyDetector()
        self.insight_generator = InsightGenerator(
            metrics_analyzer=self.metrics_analyzer,
            template_intelligence=self.template_intelligence,
            anomaly_detector=self.anomaly_detector,
        )
        self.storage = AnalyticsStorage(db_path=db_path)

    # ========== Event Management ==========

    def track_event(
        self,
        event_type: str,
        category: str,
        data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> str:
        """Track an analytics event.
        
        Args:
            event_type: Type of event
            category: Event category
            data: Event data
            duration_ms: Optional duration
            
        Returns:
            Event ID
        """
        with self.lock:
            if not self.enabled:
                return ""

            event_id = self.event_collector.track(
                event_type=event_type,
                category=category,
                data=data or {},
                duration_ms=duration_ms,
            )

            if event_id:
                # Get the full event from collector
                events = self.event_collector.peek_events(size=1)
                if events:
                    self.storage.save_event(events[0])

            return event_id

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event.
        
        Args:
            event_id: Event identifier
            
        Returns:
            Event dictionary or None
        """
        with self.lock:
            return self.storage.get_event(event_id)

    def query_events(
        self,
        event_type: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 7,
    ) -> List[Event]:
        """Query events with filtering.
        
        Args:
            event_type: Filter by event type
            category: Filter by category
            days: Number of days to look back
            
        Returns:
            List of events
        """
        with self.lock:
            start_time = datetime.now() - timedelta(days=days)

            raw_events = self.storage.query_events(
                event_type=event_type,
                category=category,
                start_time=start_time,
            )

            events = []
            for raw in raw_events:
                events.append(Event(
                    event_type=raw['event_type'],
                    timestamp=datetime.fromisoformat(raw['timestamp']),
                    event_id=raw['event_id'],
                    user_id=raw['user_id'],
                    category=raw['category'],
                    data=json.loads(raw['data']),
                    duration_ms=raw['duration_ms'],
                    error=raw['error'],
                    metadata=json.loads(raw['metadata'] or '{}'),
                ))

            return events

    # ========== Metrics Management ==========

    def get_metrics(
        self,
        metric_names: Optional[List[str]] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get computed metrics.
        
        Args:
            metric_names: Optional metric names filter
            days: Number of days to analyze
            
        Returns:
            Dictionary of metrics
        """
        with self.lock:
            events = self.query_events(days=days)

            if not events:
                return {}

            # Analyze events to compute metrics
            metrics = self.metrics_analyzer.analyze_events(events)

            # Filter if names provided
            if metric_names:
                metrics = {
                    name: metric
                    for name, metric in metrics.items()
                    if name in metric_names
                }

            # Store metrics
            for metric in metrics.values():
                self.storage.save_metric(metric)

            return {name: m.to_dict() for name, m in metrics.items()}

    def get_time_series_metrics(
        self,
        metric_name: str,
        aggregation: str = 'daily',
        days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """Get time series metrics.
        
        Args:
            metric_name: Name of metric
            aggregation: Aggregation period (hourly, daily, weekly)
            days: Number of days
            
        Returns:
            Time series data or None
        """
        with self.lock:
            events = self.query_events(days=days)

            if not events:
                return None

            ts_metric = self.metrics_analyzer.get_time_series_metrics(
                events=events,
                metric_name=metric_name,
                aggregation=aggregation,
            )

            if ts_metric:
                return ts_metric.to_dict()

            return None

    # ========== Insights & Intelligence ==========

    def get_insights(
        self,
        category: Optional[str] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get generated insights.
        
        Args:
            category: Filter by category
            days: Number of days to analyze
            
        Returns:
            List of insights
        """
        with self.lock:
            # Get recent events
            events = self.query_events(days=days)

            if not events:
                return []

            # Generate insights
            insights = self.insight_generator.generate_all_insights(events)

            # Store and filter
            for insight in insights:
                self.storage.save_insight(insight.to_dict())

            if category:
                insights = [i for i in insights if i.category == category]

            return [i.to_dict() for i in insights]

    def generate_insights(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate fresh insights.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of generated insights
        """
        with self.lock:
            events = self.query_events(days=days)

            if not events:
                return []

            insights = self.insight_generator.generate_all_insights(events)

            return [i.to_dict() for i in insights]

    def get_template_intelligence(self, template_id: str, days: int = 7) -> Dict[str, Any]:
        """Get intelligence for a specific template.
        
        Args:
            template_id: Template identifier
            days: Number of days to analyze
            
        Returns:
            Template intelligence data
        """
        with self.lock:
            events = self.query_events(days=days)
            template_events = [e for e in events if e.data.get('template_id') == template_id]

            if not template_events:
                return {}

            analysis = self.template_intelligence.analyze_template(
                template_id=template_id,
                events=template_events,
            )

            patterns = self.template_intelligence.get_usage_patterns(template_id)
            recommendations = self.template_intelligence.generate_recommendations(
                template_id=template_id,
                events=template_events,
            )

            return {
                'analysis': analysis,
                'patterns': patterns,
                'recommendations': recommendations,
            }

    # ========== Anomalies ==========

    def detect_anomalies(self, days: int = 7) -> List[Dict[str, Any]]:
        """Detect anomalies in data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of anomalies
        """
        with self.lock:
            events = self.query_events(days=days)

            if not events:
                return []

            # Detect various anomalies
            anomalies = self.anomaly_detector.detect_statistical_anomalies(events)
            anomalies.extend(self.anomaly_detector.detect_temporal_anomalies(events))
            anomalies.extend(self.anomaly_detector.detect_error_spike(events))

            return [a.to_dict() for a in anomalies]

    def get_anomalies(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get detected anomalies.
        
        Args:
            severity: Filter by severity
            
        Returns:
            List of anomalies
        """
        with self.lock:
            anomalies = self.anomaly_detector.get_anomalies(severity=severity)
            return [a.to_dict() for a in anomalies]

    # ========== Reports & Export ==========

    def generate_report(
        self,
        report_type: str = 'summary',
        days: int = 30,
    ) -> Dict[str, Any]:
        """Generate analytics report.
        
        Args:
            report_type: Type of report (summary, detailed, performance)
            days: Number of days to include
            
        Returns:
            Report data
        """
        with self.lock:
            events = self.query_events(days=days)

            report = {
                'type': report_type,
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'event_count': len(events),
            }

            if report_type in ['summary', 'detailed']:
                # Get metrics
                metrics = self.get_metrics(days=days)
                report['metrics'] = metrics

                # Get insights
                insights = self.get_insights(days=days)
                report['insights'] = insights

            if report_type in ['detailed', 'performance']:
                # Get anomalies
                anomalies = self.detect_anomalies(days=days)
                report['anomalies'] = anomalies

                # Performance breakdown
                if events:
                    durations = [e.duration_ms for e in events if e.duration_ms]
                    if durations:
                        import statistics
                        report['performance'] = {
                            'avg_latency_ms': statistics.mean(durations),
                            'p95_latency_ms': self._percentile(durations, 95),
                            'p99_latency_ms': self._percentile(durations, 99),
                            'max_latency_ms': max(durations),
                        }

            return report

    def export_data(
        self,
        format: str = 'json',
        filename: Optional[str] = None,
        days: int = 30,
    ) -> bool:
        """Export analytics data.
        
        Args:
            format: Export format (json, csv)
            filename: Output filename
            days: Number of days to export
            
        Returns:
            True if exported successfully
        """
        with self.lock:
            if format == 'csv':
                filename = filename or f'analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                return self.storage.export_csv(filename)

            else:  # json
                filename = filename or f'analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                return self.storage.export_json(filename)

    # ========== Dashboard Data ==========

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard.
        
        Returns:
            Dashboard data
        """
        with self.lock:
            events = self.query_events(days=7)

            if not events:
                return {
                    'summary': {},
                    'metrics': {},
                    'insights': [],
                }

            # Calculate summary statistics
            summary = self._calculate_summary_stats(events)

            # Get metrics
            metrics = self.get_metrics(days=7)

            # Get insights
            insights = self.get_insights(days=7)

            return {
                'timestamp': datetime.now().isoformat(),
                'summary': summary,
                'metrics': metrics,
                'insights': insights[:5],  # Top 5 insights
            }

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics.
        
        Returns:
            Summary statistics
        """
        with self.lock:
            events = self.query_events(days=7)

            if not events:
                return {}

            return self._calculate_summary_stats(events)

    # ========== Configuration ==========

    def set_analytics_enabled(self, enabled: bool) -> bool:
        """Enable/disable analytics collection.
        
        Args:
            enabled: Whether to collect analytics
            
        Returns:
            True if set successfully
        """
        with self.lock:
            self.enabled = enabled
            return True

    def is_analytics_enabled(self) -> bool:
        """Check if analytics is enabled.
        
        Returns:
            Whether analytics is enabled
        """
        with self.lock:
            return self.enabled

    def set_retention_days(self, days: int) -> bool:
        """Set data retention policy.
        
        Args:
            days: Number of days to retain
            
        Returns:
            True if set successfully
        """
        with self.lock:
            if days > 0:
                self.retention_days = days
                return True
            return False

    def set_event_sampling_rate(self, rate: float) -> bool:
        """Set event sampling rate.
        
        Args:
            rate: Sampling rate (0.0 to 1.0)
            
        Returns:
            True if set successfully
        """
        with self.lock:
            if 0.0 <= rate <= 1.0:
                self.event_sampling_rate = rate
                self.event_collector.set_sampling_rate(rate)
                return True
            return False

    # ========== Maintenance ==========

    def cleanup_old_data(self) -> int:
        """Delete data older than retention period.
        
        Returns:
            Number of events deleted
        """
        with self.lock:
            return self.storage.delete_old_events(self.retention_days)

    def optimize_storage(self) -> bool:
        """Optimize database storage.
        
        Returns:
            True if optimization successful
        """
        with self.lock:
            success = self.storage.cleanup_database()
            success = self.storage.vacuum_database() and success
            return success

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'event_collector': self.event_collector.get_stats(),
                'metrics_analyzer': self.metrics_analyzer.get_stats(),
                'template_intelligence': self.template_intelligence.get_stats(),
                'anomaly_detector': self.anomaly_detector.get_stats(),
                'insight_generator': self.insight_generator.get_stats(),
                'storage': self.storage.get_stats(),
                'configuration': {
                    'enabled': self.enabled,
                    'retention_days': self.retention_days,
                    'sampling_rate': self.event_sampling_rate,
                },
            }

    # ========== Utility Methods ==========

    @staticmethod
    def _calculate_summary_stats(events: List[Event]) -> Dict[str, Any]:
        """Calculate summary statistics from events.
        
        Args:
            events: Events to summarize
            
        Returns:
            Summary statistics
        """
        if not events:
            return {}

        import statistics
        from collections import Counter

        durations = [e.duration_ms for e in events if e.duration_ms is not None]
        event_types = Counter(e.event_type for e in events)
        error_count = sum(1 for e in events if e.error)

        stats = {
            'total_events': len(events),
            'unique_event_types': len(event_types),
            'error_count': error_count,
            'error_rate_percent': (error_count / len(events)) * 100 if events else 0,
        }

        if durations:
            stats['latency_stats'] = {
                'mean_ms': statistics.mean(durations),
                'median_ms': statistics.median(durations),
                'min_ms': min(durations),
                'max_ms': max(durations),
                'stdev_ms': statistics.stdev(durations) if len(durations) > 1 else 0,
            }

        stats['event_breakdown'] = dict(event_types.most_common(10))

        return stats

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
