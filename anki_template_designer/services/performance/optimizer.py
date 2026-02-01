"""
Performance optimizer service.

Plan 13: Main service coordinating caching, metrics, and optimization.
"""

import time
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass

from .cache import MemoryCache, CacheStats
from .metrics import MetricsTracker, TimingStats

logger = logging.getLogger("anki_template_designer.services.performance.optimizer")

T = TypeVar('T')


@dataclass
class PerformanceReport:
    """Performance report with cache and timing data.
    
    Attributes:
        cache_stats: Cache statistics.
        timing_stats: Timing statistics.
        counters: Counter values.
        gauges: Gauge values.
        recommendations: Performance recommendations.
    """
    cache_stats: Dict[str, Any]
    timing_stats: Dict[str, Any]
    counters: Dict[str, int]
    gauges: Dict[str, float]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cacheStats": self.cache_stats,
            "timingStats": self.timing_stats,
            "counters": self.counters,
            "gauges": self.gauges,
            "recommendations": self.recommendations
        }


class PerformanceOptimizer:
    """Central service for performance optimization.
    
    Coordinates:
    - Memory caching with TTL and LRU eviction
    - Performance metrics tracking
    - Timing measurements
    - Performance reporting and recommendations
    
    Example:
        optimizer = PerformanceOptimizer()
        
        # Use cache
        optimizer.cache_set("key", value, ttl=300)
        value = optimizer.cache_get("key")
        
        # Track metrics
        optimizer.track_timing("render", 45.5)
        optimizer.increment("api.calls")
        
        # Get report
        report = optimizer.get_performance_report()
    """
    
    def __init__(
        self,
        cache_size_mb: int = 50,
        cache_ttl: int = 600,
        metrics_history: int = 1000
    ) -> None:
        """Initialize performance optimizer.
        
        Args:
            cache_size_mb: Maximum cache size in MB.
            cache_ttl: Default cache TTL in seconds.
            metrics_history: Number of recent metrics to keep.
        """
        self._cache = MemoryCache(
            max_size_mb=cache_size_mb,
            default_ttl=cache_ttl,
            name="main"
        )
        self._metrics = MetricsTracker(history_size=metrics_history)
        self._start_time = time.time()
        
        # Separate caches for different purposes
        self._template_cache = MemoryCache(
            max_size_mb=20,
            default_ttl=1800,  # 30 minutes
            name="templates"
        )
        self._preview_cache = MemoryCache(
            max_size_mb=10,
            default_ttl=60,  # 1 minute
            name="previews"
        )
        
        logger.debug(f"PerformanceOptimizer initialized: cache={cache_size_mb}MB, ttl={cache_ttl}s")
    
    # ===== Cache Operations =====
    
    def cache_get(self, key: str, default: Any = None) -> Any:
        """Get value from main cache.
        
        Args:
            key: Cache key.
            default: Default value if not found.
            
        Returns:
            Cached value or default.
        """
        self._metrics.increment("cache.get")
        result = self._cache.get(key, default)
        if result != default:
            self._metrics.increment("cache.hit")
        else:
            self._metrics.increment("cache.miss")
        return result
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in main cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds.
            
        Returns:
            True if stored successfully.
        """
        self._metrics.increment("cache.set")
        return self._cache.set(key, value, ttl)
    
    def cache_delete(self, key: str) -> bool:
        """Delete from main cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        self._metrics.increment("cache.delete")
        return self._cache.delete(key)
    
    def cache_clear(self) -> int:
        """Clear main cache.
        
        Returns:
            Number of entries cleared.
        """
        self._metrics.increment("cache.clear")
        return self._cache.clear()
    
    def cache_invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern with * wildcard.
            
        Returns:
            Number of entries invalidated.
        """
        return self._cache.invalidate_pattern(pattern)
    
    def get_cache_stats(self) -> CacheStats:
        """Get main cache statistics.
        
        Returns:
            CacheStats object.
        """
        return self._cache.get_stats()
    
    # ===== Template Cache =====
    
    def cache_template(self, template_id: str, content: str) -> bool:
        """Cache template content.
        
        Args:
            template_id: Template identifier.
            content: Template content.
            
        Returns:
            True if cached.
        """
        return self._template_cache.set(f"template:{template_id}", content)
    
    def get_cached_template(self, template_id: str) -> Optional[str]:
        """Get cached template content.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            Cached content or None.
        """
        return self._template_cache.get(f"template:{template_id}")
    
    def invalidate_template(self, template_id: str) -> bool:
        """Invalidate cached template.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            True if invalidated.
        """
        return self._template_cache.delete(f"template:{template_id}")
    
    # ===== Preview Cache =====
    
    def cache_preview(self, preview_key: str, html: str) -> bool:
        """Cache rendered preview.
        
        Args:
            preview_key: Preview identifier.
            html: Rendered HTML.
            
        Returns:
            True if cached.
        """
        return self._preview_cache.set(preview_key, html)
    
    def get_cached_preview(self, preview_key: str) -> Optional[str]:
        """Get cached preview.
        
        Args:
            preview_key: Preview identifier.
            
        Returns:
            Cached HTML or None.
        """
        return self._preview_cache.get(preview_key)
    
    def invalidate_previews(self) -> int:
        """Clear all cached previews.
        
        Returns:
            Number of previews cleared.
        """
        return self._preview_cache.clear()
    
    # ===== Metrics Operations =====
    
    def increment(self, name: str, value: int = 1) -> int:
        """Increment a counter.
        
        Args:
            name: Counter name.
            value: Amount to increment.
            
        Returns:
            New counter value.
        """
        return self._metrics.increment(name, value)
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge value.
        
        Args:
            name: Gauge name.
            value: Current value.
        """
        self._metrics.set_gauge(name, value)
    
    def track_timing(self, name: str, duration_ms: float) -> None:
        """Record a timing measurement.
        
        Args:
            name: Timing name.
            duration_ms: Duration in milliseconds.
        """
        self._metrics.record_timing(name, duration_ms)
    
    def time(self, name: str):
        """Context manager for timing.
        
        Args:
            name: Timing name.
            
        Example:
            with optimizer.time("render"):
                do_render()
        """
        return self._metrics.time(name)
    
    def timed(self, name: str) -> Callable:
        """Decorator for timing functions.
        
        Args:
            name: Timing name.
            
        Returns:
            Decorator.
        """
        return self._metrics.timed(name)
    
    def get_timing_stats(self, name: str) -> Optional[TimingStats]:
        """Get timing statistics.
        
        Args:
            name: Timing name.
            
        Returns:
            TimingStats or None.
        """
        return self._metrics.get_timing_stats(name)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics.
        
        Returns:
            Metrics summary dictionary.
        """
        return self._metrics.get_summary()
    
    # ===== Performance Analysis =====
    
    def get_performance_report(self) -> PerformanceReport:
        """Generate comprehensive performance report.
        
        Returns:
            PerformanceReport with stats and recommendations.
        """
        cache_stats = self._cache.get_stats()
        metrics_summary = self._metrics.get_summary()
        
        # Generate recommendations
        recommendations = self._analyze_performance(cache_stats, metrics_summary)
        
        return PerformanceReport(
            cache_stats=cache_stats.to_dict(),
            timing_stats=metrics_summary.get("timings", {}),
            counters=metrics_summary.get("counters", {}),
            gauges=metrics_summary.get("gauges", {}),
            recommendations=recommendations
        )
    
    def _analyze_performance(
        self, 
        cache_stats: CacheStats,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Analyze performance and generate recommendations."""
        recommendations = []
        
        # Cache hit rate analysis
        if cache_stats.hit_rate < 0.5 and cache_stats.total_requests > 100:
            recommendations.append(
                f"Low cache hit rate ({cache_stats.hit_rate:.1%}). "
                "Consider increasing cache size or TTL."
            )
        
        # Eviction analysis
        if cache_stats.evictions > cache_stats.entries * 2:
            recommendations.append(
                f"High eviction rate ({cache_stats.evictions} evictions). "
                "Consider increasing cache size."
            )
        
        # Timing analysis
        timings = metrics.get("timings", {})
        for name, stats in timings.items():
            if stats.get("avgMs", 0) > 1000:
                recommendations.append(
                    f"Slow operation: {name} (avg {stats['avgMs']:.0f}ms). "
                    "Consider optimization."
                )
        
        if not recommendations:
            recommendations.append("Performance looks good!")
        
        return recommendations
    
    def get_uptime(self) -> float:
        """Get optimizer uptime in seconds.
        
        Returns:
            Uptime in seconds.
        """
        return time.time() - self._start_time
    
    def reset_metrics(self) -> None:
        """Reset all metrics (not cache)."""
        self._metrics.reset()
        logger.info("Metrics reset")
    
    def reset_all(self) -> None:
        """Reset everything including caches."""
        self._cache.clear()
        self._template_cache.clear()
        self._preview_cache.clear()
        self._metrics.reset()
        logger.info("All caches and metrics reset")
    
    def cleanup(self) -> Dict[str, int]:
        """Cleanup expired cache entries.
        
        Returns:
            Dictionary with cleanup counts per cache.
        """
        return {
            "main": self._cache.cleanup_expired(),
            "templates": self._template_cache.cleanup_expired(),
            "previews": self._preview_cache.cleanup_expired()
        }
    
    def get_all_cache_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all caches.
        
        Returns:
            Dictionary of cache names to stats.
        """
        return {
            "main": self._cache.get_stats().to_dict(),
            "templates": self._template_cache.get_stats().to_dict(),
            "previews": self._preview_cache.get_stats().to_dict()
        }


# Global instance
_optimizer: Optional[PerformanceOptimizer] = None


def get_optimizer() -> Optional[PerformanceOptimizer]:
    """Get the global optimizer instance.
    
    Returns:
        PerformanceOptimizer instance or None.
    """
    return _optimizer


def init_optimizer(
    cache_size_mb: int = 50,
    cache_ttl: int = 600
) -> PerformanceOptimizer:
    """Initialize the global optimizer.
    
    Args:
        cache_size_mb: Maximum cache size in MB.
        cache_ttl: Default cache TTL in seconds.
        
    Returns:
        Initialized PerformanceOptimizer.
    """
    global _optimizer
    _optimizer = PerformanceOptimizer(
        cache_size_mb=cache_size_mb,
        cache_ttl=cache_ttl
    )
    logger.debug("Global optimizer initialized")
    return _optimizer
