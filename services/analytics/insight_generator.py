"""Insight generation from analytics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import RLock
import uuid
from .event_collector import Event
from .metrics_analyzer import MetricsAnalyzer
from .template_intelligence import TemplateIntelligence
from .anomaly_detector import AnomalyDetector, Anomaly


@dataclass
class Insight:
    """Represents an actionable insight."""
    insight_id: str
    title: str
    description: str
    category: str  # performance, usage, recommendations, anomalies
    severity: str  # low, medium, high
    confidence: float  # 0-1
    timestamp: datetime
    recommended_actions: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'insight_id': self.insight_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'recommended_actions': self.recommended_actions,
            'data': self.data,
        }


class InsightGenerator:
    """Generates actionable insights from analytics data."""

    def __init__(
        self,
        metrics_analyzer: Optional[MetricsAnalyzer] = None,
        template_intelligence: Optional[TemplateIntelligence] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
    ):
        """Initialize insight generator.
        
        Args:
            metrics_analyzer: Optional MetricsAnalyzer instance
            template_intelligence: Optional TemplateIntelligence instance
            anomaly_detector: Optional AnomalyDetector instance
        """
        self.lock = RLock()
        self.metrics_analyzer = metrics_analyzer or MetricsAnalyzer()
        self.template_intelligence = template_intelligence or TemplateIntelligence()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.insights: List[Insight] = []

    def generate_all_insights(self, events: List[Event]) -> List[Insight]:
        """Generate all types of insights.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of generated insights
        """
        with self.lock:
            self.insights.clear()

            insights = []
            insights.extend(self.generate_performance_insights(events))
            insights.extend(self.generate_usage_insights(events))
            insights.extend(self.generate_recommendations(events))
            insights.extend(self.generate_anomaly_insights(events))

            self.insights = insights
            return insights

    def generate_performance_insights(self, events: List[Event]) -> List[Insight]:
        """Generate performance insights.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of performance insights
        """
        with self.lock:
            insights = []

            # Calculate metrics
            self.metrics_analyzer.analyze_events(events)

            # Latency insights
            durations = [e.duration_ms for e in events if e.duration_ms is not None]

            if durations:
                import statistics
                mean_latency = statistics.mean(durations)
                max_latency = max(durations)

                if mean_latency > 500:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        title='High Average Latency Detected',
                        description=f'Average operation latency is {mean_latency:.0f}ms',
                        category='performance',
                        severity='high',
                        confidence=0.95,
                        timestamp=datetime.now(),
                        recommended_actions=[
                            'Review template complexity and optimize large templates',
                            'Check system resource usage during operations',
                            'Consider using simpler component structures',
                        ],
                        data={'mean_latency': mean_latency, 'max_latency': max_latency},
                    ))

                if max_latency > 1000:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        title='Extreme Latency Spike Observed',
                        description=f'Maximum operation latency reached {max_latency:.0f}ms',
                        category='performance',
                        severity='high',
                        confidence=0.9,
                        timestamp=datetime.now(),
                        recommended_actions=[
                            'Check for specific operations causing spikes',
                            'Monitor memory and CPU usage',
                            'Review recent changes to slow operations',
                        ],
                        data={'max_latency': max_latency},
                    ))

            # Error rate insights
            error_count = sum(1 for e in events if e.error)
            if events:
                error_rate = (error_count / len(events)) * 100

                if error_rate > 5:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        title='Elevated Error Rate',
                        description=f'Error rate is {error_rate:.1f}%',
                        category='performance',
                        severity='high',
                        confidence=0.9,
                        timestamp=datetime.now(),
                        recommended_actions=[
                            'Review error logs and identify patterns',
                            'Check for compatibility issues',
                            'Validate template structure',
                        ],
                        data={'error_rate': error_rate, 'error_count': error_count},
                    ))

            return insights

    def generate_usage_insights(self, events: List[Event]) -> List[Insight]:
        """Generate usage insights.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of usage insights
        """
        with self.lock:
            insights = []

            if not events:
                return insights

            # Template usage
            template_opens = sum(
                1 for e in events
                if e.event_type == 'template_opened'
            )
            template_saves = sum(
                1 for e in events
                if e.event_type == 'template_saved'
            )

            if template_opens > 100:
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    title='Highly Active Template Usage',
                    description=f'{template_opens} template open operations detected',
                    category='usage',
                    severity='low',
                    confidence=0.95,
                    timestamp=datetime.now(),
                    recommended_actions=[
                        'Consider saving frequently used templates as favorites',
                        'Create template collections for better organization',
                    ],
                    data={'template_opens': template_opens},
                ))

            # Modification patterns
            modifications = sum(
                1 for e in events
                if e.event_type in ['component_added', 'component_removed', 'component_modified']
            )

            if modifications > 50:
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    title='High Template Modification Activity',
                    description=f'{modifications} template modifications recorded',
                    category='usage',
                    severity='low',
                    confidence=0.9,
                    timestamp=datetime.now(),
                    recommended_actions=[
                        'Document your template changes for future reference',
                        'Consider version control for important templates',
                    ],
                    data={'modifications': modifications},
                ))

            # Session analysis
            session_events = len(events)
            if session_events > 200:
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    title='Productive Session Detected',
                    description=f'Session included {session_events} events',
                    category='usage',
                    severity='low',
                    confidence=0.85,
                    timestamp=datetime.now(),
                    recommended_actions=[
                        'Save important templates to preserve your work',
                        'Take breaks to maintain productivity',
                    ],
                    data={'session_events': session_events},
                ))

            return insights

    def generate_recommendations(self, events: List[Event]) -> List[Insight]:
        """Generate optimization recommendations.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of recommendations
        """
        with self.lock:
            insights = []

            if not events:
                return insights

            # Component usage recommendations
            component_types = {}
            for event in events:
                ctype = event.data.get('component_type')
                if ctype:
                    component_types[ctype] = component_types.get(ctype, 0) + 1

            # Skill level assessment
            action_types = set(e.event_type for e in events)
            undo_count = sum(1 for e in events if e.event_type == 'undo_executed')
            redo_count = sum(1 for e in events if e.event_type == 'redo_executed')

            skill_level = 'intermediate'
            if undo_count < 5 and len(action_types) > 10:
                skill_level = 'advanced'
            elif undo_count > 30:
                skill_level = 'beginner'

            insights.append(Insight(
                insight_id=str(uuid.uuid4()),
                title=f'{skill_level.capitalize()} User Pattern Detected',
                description=f'Based on action patterns, you appear to be a {skill_level} user',
                category='recommendations',
                severity='low',
                confidence=0.8,
                timestamp=datetime.now(),
                recommended_actions=self._get_skill_recommendations(skill_level),
                data={
                    'skill_level': skill_level,
                    'undo_count': undo_count,
                    'redo_count': redo_count,
                    'action_variety': len(action_types),
                },
            ))

            # Component diversity recommendation
            if len(component_types) > 15:
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    title='Template Complexity Opportunity',
                    description=f'Templates use {len(component_types)} different component types',
                    category='recommendations',
                    severity='low',
                    confidence=0.75,
                    timestamp=datetime.now(),
                    recommended_actions=[
                        'Consolidate similar components where possible',
                        'Document specialized component usage',
                        'Consider creating component sets',
                    ],
                    data={'component_types': len(component_types)},
                ))

            return insights

    def generate_anomaly_insights(self, events: List[Event]) -> List[Insight]:
        """Generate insights from anomalies.
        
        Args:
            events: Events to analyze
            
        Returns:
            List of anomaly insights
        """
        with self.lock:
            insights = []

            # Detect anomalies
            anomalies = self.anomaly_detector.detect_statistical_anomalies(events)
            anomalies.extend(self.anomaly_detector.detect_temporal_anomalies(events))
            anomalies.extend(self.anomaly_detector.detect_error_spike(events))

            # Convert anomalies to insights
            for anomaly in anomalies:
                if anomaly.severity in ['high', 'critical']:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        title=f'{anomaly.anomaly_type.replace("_", " ").title()} Alert',
                        description=anomaly.description,
                        category='anomalies',
                        severity=anomaly.severity.lower() if anomaly.severity != 'critical' else 'high',
                        confidence=0.85,
                        timestamp=anomaly.timestamp,
                        recommended_actions=[
                            f'Review {anomaly.metric_name} metrics',
                            'Check for recent system changes',
                            'Investigate affected operations',
                        ],
                        data=anomaly.to_dict(),
                    ))

            return insights

    def get_insights(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Insight]:
        """Get generated insights with optional filtering.
        
        Args:
            category: Filter by category
            severity: Filter by severity
            
        Returns:
            List of insights
        """
        with self.lock:
            insights = self.insights

            if category:
                insights = [i for i in insights if i.category == category]

            if severity:
                insights = [i for i in insights if i.severity == severity]

            return insights

    def get_actionable_insights(self) -> List[Insight]:
        """Get high-confidence, actionable insights.
        
        Returns:
            List of actionable insights
        """
        with self.lock:
            return [
                i for i in self.insights
                if i.confidence >= 0.8 and i.recommended_actions
            ]

    def clear(self) -> None:
        """Clear generated insights."""
        with self.lock:
            self.insights.clear()

    @staticmethod
    def _get_skill_recommendations(skill_level: str) -> List[str]:
        """Get recommendations based on skill level.
        
        Args:
            skill_level: User skill level
            
        Returns:
            List of recommendations
        """
        recommendations = {
            'beginner': [
                'Explore template gallery for inspiration',
                'Use keyboard shortcuts to speed up workflow',
                'Review documentation for common patterns',
                'Practice with simple templates first',
            ],
            'intermediate': [
                'Explore advanced component combinations',
                'Try creating template variations',
                'Document your template strategies',
                'Share templates with the community',
            ],
            'advanced': [
                'Consider creating custom component libraries',
                'Optimize templates for specific use cases',
                'Mentor other users in best practices',
                'Contribute to the Anki community',
            ],
        }

        return recommendations.get(skill_level, [])

    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'total_insights': len(self.insights),
                'actionable_insights': len(self.get_actionable_insights()),
                'by_category': {
                    cat: len([i for i in self.insights if i.category == cat])
                    for cat in ['performance', 'usage', 'recommendations', 'anomalies']
                },
            }
