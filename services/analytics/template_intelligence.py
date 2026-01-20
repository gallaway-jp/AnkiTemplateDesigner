"""Template intelligence and recommendations."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from threading import RLock
from collections import defaultdict, Counter
from .event_collector import Event


class TemplateIntelligence:
    """Analyzes templates and generates intelligence insights."""

    def __init__(self):
        """Initialize template intelligence."""
        self.lock = RLock()
        self.template_stats: Dict[str, Dict[str, Any]] = {}
        self.component_usage: Counter = Counter()
        self.modification_history: List[Dict[str, Any]] = []

    def analyze_template(self, template_id: str, events: List[Event]) -> Dict[str, Any]:
        """Analyze a template based on events.
        
        Args:
            template_id: Template identifier
            events: Events related to template
            
        Returns:
            Analysis dictionary
        """
        with self.lock:
            template_events = [
                e for e in events
                if e.data.get('template_id') == template_id
            ]

            analysis = {
                'template_id': template_id,
                'event_count': len(template_events),
                'modification_count': sum(
                    1 for e in template_events
                    if e.event_type in ['component_added', 'component_removed', 'component_modified']
                ),
                'open_count': sum(
                    1 for e in template_events
                    if e.event_type == 'template_opened'
                ),
                'save_count': sum(
                    1 for e in template_events
                    if e.event_type == 'template_saved'
                ),
                'complexity_score': 0.0,
                'usage_frequency': 'low',
                'last_modified': None,
                'components': defaultdict(int),
            }

            # Calculate complexity
            component_count = sum(
                1 for e in template_events
                if e.event_type == 'component_added'
            )
            analysis['complexity_score'] = min(100.0, component_count * 5.0)

            # Calculate usage frequency
            total_events = len(template_events)
            if total_events > 50:
                analysis['usage_frequency'] = 'high'
            elif total_events > 20:
                analysis['usage_frequency'] = 'medium'
            else:
                analysis['usage_frequency'] = 'low'

            # Track last modified
            modified_events = [
                e for e in template_events
                if e.event_type == 'component_modified'
            ]
            if modified_events:
                analysis['last_modified'] = modified_events[-1].timestamp.isoformat()

            # Track components
            for event in template_events:
                component_type = event.data.get('component_type')
                if component_type:
                    analysis['components'][component_type] += 1
                    self.component_usage[component_type] += 1

            self.template_stats[template_id] = analysis
            return analysis

    def get_component_popularity(self) -> Dict[str, int]:
        """Get popularity ranking of components.
        
        Returns:
            Dictionary of component type -> usage count
        """
        with self.lock:
            return dict(self.component_usage.most_common())

    def get_usage_patterns(self, template_id: str) -> Dict[str, Any]:
        """Get usage patterns for a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Usage patterns dictionary
        """
        with self.lock:
            if template_id not in self.template_stats:
                return {}

            stats = self.template_stats[template_id]
            return {
                'template_id': template_id,
                'modification_frequency': stats['modification_count'] / max(1, stats['event_count']),
                'save_frequency': stats['save_count'] / max(1, stats['open_count'], 1),
                'component_diversity': len(stats['components']),
                'most_used_components': dict(
                    sorted(
                        stats['components'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                ),
            }

    def generate_recommendations(
        self,
        template_id: str,
        events: Optional[List[Event]] = None,
    ) -> List[str]:
        """Generate improvement recommendations.
        
        Args:
            template_id: Template identifier
            events: Optional events for context
            
        Returns:
            List of recommendations
        """
        with self.lock:
            recommendations = []

            if template_id not in self.template_stats:
                if events:
                    self.analyze_template(template_id, events)
                else:
                    return recommendations

            stats = self.template_stats[template_id]

            # Complexity recommendation
            if stats['complexity_score'] > 50:
                recommendations.append(
                    'Consider breaking this complex template into smaller, '
                    'more focused templates for better maintainability'
                )

            # Usage frequency recommendation
            if stats['usage_frequency'] == 'high':
                recommendations.append(
                    'This template is frequently used - document it well '
                    'and consider saving custom versions'
                )

            # Component diversity
            if len(stats['components']) > 10:
                recommendations.append(
                    'Template has many different component types - '
                    'consider if all are necessary'
                )

            # Modification patterns
            if stats['modification_count'] == 0 and stats['open_count'] > 5:
                recommendations.append(
                    'Template is viewed frequently but rarely modified - '
                    'it appears to be well-finalized'
                )

            return recommendations

    def classify_user_skill_level(self, events: List[Event]) -> str:
        """Classify user skill level based on events.
        
        Args:
            events: User events
            
        Returns:
            Skill level (beginner, intermediate, advanced)
        """
        with self.lock:
            if not events:
                return 'beginner'

            # Count different action types
            action_types = set(e.event_type for e in events)
            modification_count = sum(
                1 for e in events
                if e.event_type in ['component_added', 'component_removed', 'component_modified']
            )
            undo_count = sum(1 for e in events if e.event_type == 'undo_executed')

            skill_score = 0

            # More modifications = higher skill
            if modification_count > 50:
                skill_score += 3
            elif modification_count > 20:
                skill_score += 2
            elif modification_count > 5:
                skill_score += 1

            # More action variety = higher skill
            if len(action_types) > 10:
                skill_score += 2
            elif len(action_types) > 5:
                skill_score += 1

            # Fewer undo operations = higher skill
            if undo_count < 5:
                skill_score += 1

            if skill_score >= 5:
                return 'advanced'
            elif skill_score >= 2:
                return 'intermediate'
            else:
                return 'beginner'

    def calculate_template_complexity(
        self,
        template_id: str,
        component_count: int = 0,
    ) -> float:
        """Calculate template complexity score.
        
        Args:
            template_id: Template identifier
            component_count: Number of components (optional)
            
        Returns:
            Complexity score (0-100)
        """
        with self.lock:
            if template_id in self.template_stats:
                return self.template_stats[template_id]['complexity_score']

            # Calculate based on component count
            return min(100.0, component_count * 5.0)

    def get_template_metrics(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get all metrics for a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Metrics dictionary or None
        """
        with self.lock:
            return self.template_stats.get(template_id)

    def get_all_templates_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all templates.
        
        Returns:
            Dictionary of template_id -> metrics
        """
        with self.lock:
            return dict(self.template_stats)

    def clear(self) -> None:
        """Clear all template data."""
        with self.lock:
            self.template_stats.clear()
            self.component_usage.clear()
            self.modification_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get intelligence statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'tracked_templates': len(self.template_stats),
                'unique_components': len(self.component_usage),
                'total_component_uses': sum(self.component_usage.values()),
                'modification_history_size': len(self.modification_history),
            }
