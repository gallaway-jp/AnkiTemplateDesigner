"""
Performance metrics tracking.

Plan 13: Track timing, counts, and performance analytics.
"""

import time
import threading
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import deque

logger = logging.getLogger("anki_template_designer.services.performance.metrics")


class MetricType(Enum):
    """Types of metrics that can be tracked."""
    COUNTER = "counter"      # Incrementing count
    GAUGE = "gauge"          # Current value
    TIMING = "timing"        # Duration in milliseconds
    HISTOGRAM = "histogram"  # Distribution of values


@dataclass
class Metric:
    """A single metric measurement.
    
    Attributes:
        name: Metric name.
        type: Type of metric.
        value: Current value.
        timestamp: When metric was recorded.
        tags: Optional tags for categorization.
    """
    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags
        }


@dataclass
class TimingStats:
    """Statistics for timing metrics.
    
    Attributes:
        count: Number of measurements.
        total_ms: Total time in milliseconds.
        min_ms: Minimum time.
        max_ms: Maximum time.
        avg_ms: Average time.
        last_ms: Most recent measurement.
    """
    count: int = 0
    total_ms: float = 0
    min_ms: float = float('inf')
    max_ms: float = 0
    last_ms: float = 0
    
    @property
    def avg_ms(self) -> float:
        """Calculate average time."""
        return self.total_ms / self.count if self.count > 0 else 0
    
    def record(self, duration_ms: float) -> None:
        """Record a new timing measurement."""
        self.count += 1
        self.total_ms += duration_ms
        self.min_ms = min(self.min_ms, duration_ms)
        self.max_ms = max(self.max_ms, duration_ms)
        self.last_ms = duration_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "totalMs": round(self.total_ms, 2),
            "minMs": round(self.min_ms, 2) if self.min_ms != float('inf') else 0,
            "maxMs": round(self.max_ms, 2),
            "avgMs": round(self.avg_ms, 2),
            "lastMs": round(self.last_ms, 2)
        }


class MetricsTracker:
    """Track and analyze performance metrics.
    
    Features:
    - Counter metrics (incrementing counts)
    - Gauge metrics (current values)
    - Timing metrics (durations)
    - Histograms (value distributions)
    - Metric aggregation and statistics
    
    Example:
        tracker = MetricsTracker()
        
        # Count events
        tracker.increment("api.calls")
        
        # Track timing
        with tracker.time("render.template"):
            do_rendering()
        
        # Set gauge
        tracker.set_gauge("active.connections", 42)
        
        # Get stats
        stats = tracker.get_timing_stats("render.template")
    """
    
    def __init__(self, history_size: int = 1000) -> None:
        """Initialize metrics tracker.
        
        Args:
            history_size: Maximum number of recent metrics to keep.
        """
        self._lock = threading.RLock()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._timings: Dict[str, TimingStats] = {}
        self._history: deque = deque(maxlen=history_size)
        self._history_size = history_size
        
        logger.debug(f"MetricsTracker initialized: history_size={history_size}")
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> int:
        """Increment a counter metric.
        
        Args:
            name: Counter name.
            value: Amount to increment (default 1).
            tags: Optional tags.
            
        Returns:
            New counter value.
        """
        with self._lock:
            current = self._counters.get(name, 0)
            new_value = current + value
            self._counters[name] = new_value
            
            self._record_metric(Metric(
                name=name,
                type=MetricType.COUNTER,
                value=new_value,
                tags=tags or {}
            ))
            
            return new_value
    
    def decrement(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> int:
        """Decrement a counter metric.
        
        Args:
            name: Counter name.
            value: Amount to decrement (default 1).
            tags: Optional tags.
            
        Returns:
            New counter value.
        """
        return self.increment(name, -value, tags)
    
    def get_counter(self, name: str) -> int:
        """Get counter value.
        
        Args:
            name: Counter name.
            
        Returns:
            Current counter value.
        """
        with self._lock:
            return self._counters.get(name, 0)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric.
        
        Args:
            name: Gauge name.
            value: Current value.
            tags: Optional tags.
        """
        with self._lock:
            self._gauges[name] = value
            
            self._record_metric(Metric(
                name=name,
                type=MetricType.GAUGE,
                value=value,
                tags=tags or {}
            ))
    
    def get_gauge(self, name: str) -> Optional[float]:
        """Get gauge value.
        
        Args:
            name: Gauge name.
            
        Returns:
            Current gauge value or None.
        """
        with self._lock:
            return self._gauges.get(name)
    
    def record_timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing measurement.
        
        Args:
            name: Timing name.
            duration_ms: Duration in milliseconds.
            tags: Optional tags.
        """
        with self._lock:
            if name not in self._timings:
                self._timings[name] = TimingStats()
            
            self._timings[name].record(duration_ms)
            
            self._record_metric(Metric(
                name=name,
                type=MetricType.TIMING,
                value=duration_ms,
                tags=tags or {}
            ))
    
    @contextmanager
    def time(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing a block of code.
        
        Args:
            name: Timing name.
            tags: Optional tags.
            
        Example:
            with tracker.time("database.query"):
                result = db.execute(query)
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.record_timing(name, duration_ms, tags)
    
    def timed(self, name: str, tags: Optional[Dict[str, str]] = None) -> Callable:
        """Decorator for timing function execution.
        
        Args:
            name: Timing name.
            tags: Optional tags.
            
        Returns:
            Decorator function.
            
        Example:
            @tracker.timed("render.template")
            def render_template(template):
                return process(template)
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                with self.time(name, tags):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_timing_stats(self, name: str) -> Optional[TimingStats]:
        """Get timing statistics.
        
        Args:
            name: Timing name.
            
        Returns:
            TimingStats or None if not tracked.
        """
        with self._lock:
            return self._timings.get(name)
    
    def get_all_counters(self) -> Dict[str, int]:
        """Get all counter values.
        
        Returns:
            Dictionary of counter names to values.
        """
        with self._lock:
            return dict(self._counters)
    
    def get_all_gauges(self) -> Dict[str, float]:
        """Get all gauge values.
        
        Returns:
            Dictionary of gauge names to values.
        """
        with self._lock:
            return dict(self._gauges)
    
    def get_all_timings(self) -> Dict[str, Dict[str, Any]]:
        """Get all timing statistics.
        
        Returns:
            Dictionary of timing names to stats.
        """
        with self._lock:
            return {name: stats.to_dict() for name, stats in self._timings.items()}
    
    def get_recent_metrics(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics.
        
        Args:
            count: Maximum number to return.
            
        Returns:
            List of recent metrics as dictionaries.
        """
        with self._lock:
            recent = list(self._history)[-count:]
            return [m.to_dict() for m in recent]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics.
        
        Returns:
            Dictionary with counters, gauges, and timing stats.
        """
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timings": {name: stats.to_dict() for name, stats in self._timings.items()},
                "historySize": len(self._history)
            }
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._timings.clear()
            self._history.clear()
            logger.debug("Metrics reset")
    
    def reset_counter(self, name: str) -> None:
        """Reset a specific counter.
        
        Args:
            name: Counter name.
        """
        with self._lock:
            self._counters.pop(name, None)
    
    def reset_timing(self, name: str) -> None:
        """Reset a specific timing.
        
        Args:
            name: Timing name.
        """
        with self._lock:
            self._timings.pop(name, None)
    
    def _record_metric(self, metric: Metric) -> None:
        """Internal: Record metric to history."""
        self._history.append(metric)
