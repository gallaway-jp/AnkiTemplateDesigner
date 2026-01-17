"""
Performance Analytics Module

Provides real-time performance metrics, analysis, and optimization recommendations
for Anki template templates. Features include:

- Real-time CSS/HTML size metrics
- Load time estimation
- Performance optimization recommendations
- Performance warnings and alerts
- Memory usage tracking
- Benchmark comparisons
- Performance trend analysis
- Comprehensive reporting
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
from enum import Enum


class SeverityLevel(Enum):
    """Performance warning severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ImpactLevel(Enum):
    """Optimization recommendation impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(Enum):
    """Performance trend direction."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


@dataclass
class PerformanceMetrics:
    """Container for performance metrics snapshot."""
    
    html_size: int  # Size in bytes
    css_size: int  # Size in bytes
    total_size: int  # Total size in bytes
    load_time_ms: float  # Load time in milliseconds
    memory_usage_mb: float  # Memory usage in megabytes
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class PerformanceWarning:
    """Container for performance warning."""
    
    message: str
    severity: str
    metric_type: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert warning to dictionary."""
        return {
            "message": self.message,
            "severity": self.severity,
            "metric_type": self.metric_type,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class OptimizationRecommendation:
    """Container for optimization recommendation."""
    
    suggestion: str
    expected_impact_percent: Any  # Can be string or number
    priority: str
    implementation_effort: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "suggestion": self.suggestion,
            "expected_impact_percent": self.expected_impact_percent,
            "priority": self.priority,
            "implementation_effort": self.implementation_effort,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PerformanceTrend:
    """Container for performance trend."""
    
    metric_name: str
    direction: str
    change_percent: float
    time_period: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trend to dictionary."""
        return {
            "metric_name": self.metric_name,
            "direction": self.direction,
            "change_percent": self.change_percent,
            "time_period": self.time_period,
            "timestamp": self.timestamp.isoformat(),
        }


class PerformanceAnalytics:
    """
    Main performance analytics engine.
    
    Tracks metrics, generates warnings, recommendations, and trends.
    """
    
    # Size thresholds (in bytes)
    HTML_SIZE_WARNING = 50 * 1024  # 50KB
    CSS_SIZE_WARNING = 50 * 1024  # 50KB
    TOTAL_SIZE_WARNING = 100 * 1024  # 100KB
    
    # Load time thresholds (in milliseconds)
    LOAD_TIME_WARNING = 1000  # 1 second
    LOAD_TIME_CRITICAL = 2000  # 2 seconds
    
    # Memory thresholds (in MB)
    MEMORY_WARNING = 100  # 100MB
    MEMORY_CRITICAL = 200  # 200MB
    
    def __init__(self):
        """Initialize analytics engine."""
        self.metrics_history: List[PerformanceMetrics] = []
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        self.warnings_history: List[PerformanceWarning] = []
        self.performance_score: float = 100.0
    
    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record a new metrics snapshot."""
        self.metrics_history.append(metrics)
        self._update_performance_score()
    
    def set_baseline(self, metrics: PerformanceMetrics) -> None:
        """Set baseline metrics for comparison."""
        self.baseline_metrics = metrics
    
    def get_latest_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics snapshot."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def check_performance_warnings(self) -> List[PerformanceWarning]:
        """Check for performance issues and generate warnings."""
        warnings = []
        latest = self.get_latest_metrics()
        
        if not latest:
            return warnings
        
        # Check HTML size
        if latest.html_size > self.HTML_SIZE_WARNING:
            severity = "critical" if latest.html_size > self.HTML_SIZE_WARNING * 3 else "warning"
            warnings.append(PerformanceWarning(
                message=f"HTML size ({self._format_bytes(latest.html_size)}) exceeds recommended limit",
                severity=severity,
                metric_type="html_size",
                current_value=latest.html_size,
                threshold=self.HTML_SIZE_WARNING,
            ))
        
        # Check CSS size
        if latest.css_size > self.CSS_SIZE_WARNING:
            severity = "critical" if latest.css_size > self.CSS_SIZE_WARNING * 3 else "warning"
            warnings.append(PerformanceWarning(
                message=f"CSS size ({self._format_bytes(latest.css_size)}) exceeds recommended limit",
                severity=severity,
                metric_type="css_size",
                current_value=latest.css_size,
                threshold=self.CSS_SIZE_WARNING,
            ))
        
        # Check total size
        if latest.total_size > self.TOTAL_SIZE_WARNING:
            severity = "critical" if latest.total_size > self.TOTAL_SIZE_WARNING * 2 else "warning"
            warnings.append(PerformanceWarning(
                message=f"Total size ({self._format_bytes(latest.total_size)}) exceeds recommended limit",
                severity=severity,
                metric_type="total_size",
                current_value=latest.total_size,
                threshold=self.TOTAL_SIZE_WARNING,
            ))
        
        # Check load time
        if latest.load_time_ms > self.LOAD_TIME_CRITICAL:
            warnings.append(PerformanceWarning(
                message=f"Load time ({latest.load_time_ms}ms) is critically slow",
                severity="critical",
                metric_type="load_time_ms",
                current_value=latest.load_time_ms,
                threshold=self.LOAD_TIME_CRITICAL,
            ))
        elif latest.load_time_ms > self.LOAD_TIME_WARNING:
            warnings.append(PerformanceWarning(
                message=f"Load time ({latest.load_time_ms}ms) is slow",
                severity="warning",
                metric_type="load_time_ms",
                current_value=latest.load_time_ms,
                threshold=self.LOAD_TIME_WARNING,
            ))
        
        # Check memory usage
        if latest.memory_usage_mb > self.MEMORY_CRITICAL:
            warnings.append(PerformanceWarning(
                message=f"Memory usage ({latest.memory_usage_mb}MB) is critically high",
                severity="critical",
                metric_type="memory_usage_mb",
                current_value=latest.memory_usage_mb,
                threshold=self.MEMORY_CRITICAL,
            ))
        elif latest.memory_usage_mb > self.MEMORY_WARNING:
            warnings.append(PerformanceWarning(
                message=f"Memory usage ({latest.memory_usage_mb}MB) is high",
                severity="warning",
                metric_type="memory_usage_mb",
                current_value=latest.memory_usage_mb,
                threshold=self.MEMORY_WARNING,
            ))
        
        self.warnings_history.extend(warnings)
        return warnings
    
    def estimate_load_time(self, metrics: PerformanceMetrics) -> float:
        """Estimate load time based on template size and complexity."""
        # Base load time: 50ms for minimal template
        base_time = 50.0
        
        # Size factor: ~1ms per KB
        size_factor = metrics.total_size / 1024
        
        # Complexity factor: CSS is more complex to parse
        complexity_factor = (metrics.css_size / 1024) * 0.5
        
        estimated_time = base_time + size_factor + complexity_factor
        
        # Account for actual measured time if available
        if metrics.load_time_ms > 0:
            # Average with measured time (80% measured, 20% estimated)
            estimated_time = (metrics.load_time_ms * 0.8) + (estimated_time * 0.2)
        
        return max(estimated_time, 10.0)  # Minimum 10ms
    
    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on current metrics."""
        recommendations = []
        latest = self.get_latest_metrics()
        
        if not latest:
            return recommendations
        
        # HTML size recommendations
        if latest.html_size > self.HTML_SIZE_WARNING:
            recommendations.append(OptimizationRecommendation(
                suggestion="Consider splitting large HTML templates into smaller components",
                expected_impact_percent="high",
                priority="high",
                implementation_effort="medium",
            ))
            recommendations.append(OptimizationRecommendation(
                suggestion="Remove unused HTML elements and clean up whitespace",
                expected_impact_percent="medium",
                priority="high",
                implementation_effort="low",
            ))
        
        # CSS size recommendations
        if latest.css_size > self.CSS_SIZE_WARNING:
            recommendations.append(OptimizationRecommendation(
                suggestion="Minify CSS to reduce file size",
                expected_impact_percent="high",
                priority="high",
                implementation_effort="low",
            ))
            recommendations.append(OptimizationRecommendation(
                suggestion="Remove unused CSS classes and selectors",
                expected_impact_percent="medium",
                priority="high",
                implementation_effort="medium",
            ))
        
        # Load time recommendations
        if latest.load_time_ms > self.LOAD_TIME_WARNING:
            recommendations.append(OptimizationRecommendation(
                suggestion="Optimize CSS selectors for faster parsing",
                expected_impact_percent="medium",
                priority="high",
                implementation_effort="medium",
            ))
            recommendations.append(OptimizationRecommendation(
                suggestion="Defer loading of non-critical CSS and JavaScript",
                expected_impact_percent="high",
                priority="high",
                implementation_effort="high",
            ))
        
        # Memory usage recommendations
        if latest.memory_usage_mb > self.MEMORY_WARNING:
            recommendations.append(OptimizationRecommendation(
                suggestion="Profile and optimize DOM manipulation code",
                expected_impact_percent="medium",
                priority="high",
                implementation_effort="high",
            ))
            recommendations.append(OptimizationRecommendation(
                suggestion="Implement lazy loading for images and heavy resources",
                expected_impact_percent="high",
                priority="high",
                implementation_effort="high",
            ))
        
        # General best practices
        if latest.total_size > 0:  # Always applicable
            recommendations.append(OptimizationRecommendation(
                suggestion="Enable gzip compression for better transport efficiency",
                expected_impact_percent="high",
                priority="medium",
                implementation_effort="low",
            ))
            recommendations.append(OptimizationRecommendation(
                suggestion="Implement caching strategies for static assets",
                expected_impact_percent="medium",
                priority="medium",
                implementation_effort="medium",
            ))
        
        return recommendations
    
    def calculate_trends(self) -> List[PerformanceTrend]:
        """Calculate performance trends over time."""
        trends = []
        
        if len(self.metrics_history) < 2:
            return trends
        
        # Use last 2 samples
        previous = self.metrics_history[-2]
        current = self.metrics_history[-1]
        
        # Calculate total size trend
        size_change = ((current.total_size - previous.total_size) / previous.total_size) * 100
        if abs(size_change) < 2:
            direction = "stable"
        elif size_change > 0:
            direction = "degrading"
        else:
            direction = "improving"
        
        trends.append(PerformanceTrend(
            metric_name="total_size",
            direction=direction,
            change_percent=size_change,
            time_period="recent",
        ))
        
        # Calculate load time trend
        if previous.load_time_ms > 0 and current.load_time_ms > 0:
            time_change = ((current.load_time_ms - previous.load_time_ms) / previous.load_time_ms) * 100
            if abs(time_change) < 5:
                direction = "stable"
            elif time_change > 0:
                direction = "degrading"
            else:
                direction = "improving"
            
            trends.append(PerformanceTrend(
                metric_name="load_time",
                direction=direction,
                change_percent=time_change,
                time_period="recent",
            ))
        
        # Calculate memory trend
        mem_change = ((current.memory_usage_mb - previous.memory_usage_mb) / previous.memory_usage_mb) * 100
        if abs(mem_change) < 3:
            direction = "stable"
        elif mem_change > 0:
            direction = "degrading"
        else:
            direction = "improving"
        
        trends.append(PerformanceTrend(
            metric_name="memory_usage",
            direction=direction,
            change_percent=mem_change,
            time_period="recent",
        ))
        
        return trends
    
    def compare_with_baseline(self, current: PerformanceMetrics) -> Dict[str, float]:
        """Compare current metrics with baseline."""
        if not self.baseline_metrics:
            return {}
        
        baseline = self.baseline_metrics
        comparison = {
            "html_size_diff_percent": self._calc_diff_percent(baseline.html_size, current.html_size),
            "css_size_diff_percent": self._calc_diff_percent(baseline.css_size, current.css_size),
            "total_size_diff_percent": self._calc_diff_percent(baseline.total_size, current.total_size),
            "load_time_diff_percent": self._calc_diff_percent(baseline.load_time_ms, current.load_time_ms),
            "memory_diff_percent": self._calc_diff_percent(baseline.memory_usage_mb, current.memory_usage_mb),
        }
        
        return comparison
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        latest = self.get_latest_metrics()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "performance_score": self.performance_score,
            "metrics": latest.to_dict() if latest else None,
            "warnings": [w.to_dict() for w in self.check_performance_warnings()],
            "recommendations": [r.to_dict() for r in self.generate_recommendations()],
            "trends": [t.to_dict() for t in self.calculate_trends()],
            "baseline_comparison": self.compare_with_baseline(latest) if latest else None,
        }
        
        return report
    
    def export_to_json(self) -> str:
        """Export analytics report to JSON."""
        report = self.generate_report()
        return json.dumps(report, indent=2, default=str)
    
    def _update_performance_score(self) -> None:
        """Update overall performance score based on current metrics."""
        latest = self.get_latest_metrics()
        if not latest:
            self.performance_score = 100.0
            return
        
        score = 100.0
        
        # Deduct for size violations
        if latest.html_size > self.HTML_SIZE_WARNING:
            score -= min(20, (latest.html_size - self.HTML_SIZE_WARNING) / 1024)
        if latest.css_size > self.CSS_SIZE_WARNING:
            score -= min(20, (latest.css_size - self.CSS_SIZE_WARNING) / 1024)
        if latest.total_size > self.TOTAL_SIZE_WARNING:
            score -= min(20, (latest.total_size - self.TOTAL_SIZE_WARNING) / 1024)
        
        # Deduct for load time
        if latest.load_time_ms > self.LOAD_TIME_WARNING:
            score -= min(15, (latest.load_time_ms - self.LOAD_TIME_WARNING) / 100)
        
        # Deduct for memory usage
        if latest.memory_usage_mb > self.MEMORY_WARNING:
            score -= min(15, (latest.memory_usage_mb - self.MEMORY_WARNING) / 10)
        
        self.performance_score = max(0, min(100, score))
    
    def _calc_diff_percent(self, baseline: float, current: float) -> float:
        """Calculate percentage difference between baseline and current."""
        if baseline == 0:
            return 0.0
        return ((current - baseline) / baseline) * 100
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable format."""
        for unit in ["B", "KB", "MB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}GB"
