"""Analytics module for AnkiTemplateDesigner."""

from .event_collector import EventCollector, Event
from .metrics_analyzer import MetricsAnalyzer, Metric, TimeSeriesMetric
from .template_intelligence import TemplateIntelligence
from .anomaly_detector import AnomalyDetector, Anomaly
from .insight_generator import InsightGenerator, Insight
from .analytics_storage import AnalyticsStorage

__all__ = [
    'EventCollector',
    'Event',
    'MetricsAnalyzer',
    'Metric',
    'TimeSeriesMetric',
    'TemplateIntelligence',
    'AnomalyDetector',
    'Anomaly',
    'InsightGenerator',
    'Insight',
    'AnalyticsStorage',
]
