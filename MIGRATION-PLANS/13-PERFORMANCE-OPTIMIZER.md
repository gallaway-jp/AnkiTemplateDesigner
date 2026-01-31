# Plan 13: Performance Optimization (ISSUE-54)

## Objective
Implement the Performance Optimization Engine from ISSUE-54 specification, providing multi-level caching, async operations, and performance analytics.

---

## Prerequisites
- [ ] Plans 01-12 completed and tested
- [ ] Core addon functionality working
- [ ] Template service operational

---

## Feature Specification Reference

From ISSUE-54-SPECIFICATION.md:
- Multi-level caching system (memory, disk)
- Performance metrics tracking and analysis
- Async operations manager with batching
- Rendering optimization
- Performance dashboard and alerts

---

## Step 13.1: Implement Memory Cache

### Task
Create an efficient memory cache with TTL and size limits.

### Implementation

**anki_template_designer/services/performance/cache.py**
```python
"""Caching system for performance optimization.

Provides multi-level caching with memory and disk storage,
TTL support, and automatic invalidation.
"""

import time
import threading
from typing import Any, Callable, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger("anki_template_designer.services.performance.cache")


@dataclass
class CacheEntry:
    """A single cache entry with metadata.
    
    Attributes:
        value: The cached value.
        created_at: Timestamp when entry was created.
        expires_at: Timestamp when entry expires (0 = never).
        hits: Number of times entry was accessed.
        size: Estimated size in bytes.
    """
    value: Any
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0
    hits: int = 0
    size: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at == 0:
            return False
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """Cache statistics.
    
    Attributes:
        hits: Total cache hits.
        misses: Total cache misses.
        entries: Current number of entries.
        size_bytes: Total size of cached data.
        evictions: Number of entries evicted.
    """
    hits: int = 0
    misses: int = 0
    entries: int = 0
    size_bytes: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache:
    """Thread-safe in-memory cache with TTL and size limits.
    
    Implements LRU eviction when size limit is reached.
    
    Attributes:
        max_size_mb: Maximum cache size in megabytes.
        default_ttl: Default time-to-live in seconds.
    """
    
    def __init__(
        self, 
        max_size_mb: int = 100,
        default_ttl: int = 3600
    ) -> None:
        """Initialize memory cache.
        
        Args:
            max_size_mb: Maximum cache size in MB.
            default_ttl: Default TTL in seconds.
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._default_ttl = default_ttl
        self._stats = CacheStats()
        self._access_order: list = []  # For LRU tracking
        
        logger.info(f"MemoryCache initialized: max_size={max_size_mb}MB, ttl={default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found/expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            if entry.is_expired():
                self._remove(key)
                self._stats.misses += 1
                return None
            
            # Update access tracking
            entry.hits += 1
            self._stats.hits += 1
            self._update_access_order(key)
            
            return entry.value
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds. Uses default if None.
            
        Returns:
            True if stored successfully.
        """
        with self._lock:
            # Estimate size
            size = self._estimate_size(value)
            
            # Check if we need to evict
            while self._stats.size_bytes + size > self._max_size_bytes:
                if not self._evict_lru():
                    logger.warning("Cannot store: cache full and nothing to evict")
                    return False
            
            # Remove existing entry if present
            if key in self._cache:
                self._remove(key)
            
            # Create entry
            ttl_value = ttl if ttl is not None else self._default_ttl
            expires_at = time.time() + ttl_value if ttl_value > 0 else 0
            
            entry = CacheEntry(
                value=value,
                expires_at=expires_at,
                size=size
            )
            
            self._cache[key] = entry
            self._stats.entries += 1
            self._stats.size_bytes += size
            self._access_order.append(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """Remove entry from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if entry was removed.
        """
        with self._lock:
            return self._remove(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._stats = CacheStats()
            logger.info("Cache cleared")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern.
        
        Args:
            pattern: Pattern to match (supports * wildcard).
            
        Returns:
            Number of entries invalidated.
        """
        import fnmatch
        
        with self._lock:
            keys_to_remove = [
                k for k in self._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            
            for key in keys_to_remove:
                self._remove(key)
            
            return len(keys_to_remove)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            Current cache statistics.
        """
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                entries=self._stats.entries,
                size_bytes=self._stats.size_bytes,
                evictions=self._stats.evictions
            )
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed.
        """
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            
            for key in expired_keys:
                self._remove(key)
            
            return len(expired_keys)
    
    def _remove(self, key: str) -> bool:
        """Internal removal method."""
        if key in self._cache:
            entry = self._cache[key]
            self._stats.size_bytes -= entry.size
            self._stats.entries -= 1
            del self._cache[key]
            
            if key in self._access_order:
                self._access_order.remove(key)
            
            return True
        return False
    
    def _evict_lru(self) -> bool:
        """Evict least recently used entry."""
        if not self._access_order:
            return False
        
        key = self._access_order[0]
        self._remove(key)
        self._stats.evictions += 1
        
        logger.debug(f"Evicted LRU entry: {key}")
        return True
    
    def _update_access_order(self, key: str) -> None:
        """Update LRU tracking for key."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value."""
        try:
            # Use JSON serialization as rough size estimate
            return len(json.dumps(value, default=str).encode())
        except (TypeError, ValueError):
            return 1024  # Default estimate for non-serializable
```

### Quality Checks

#### Security
- [ ] Thread-safe operations (RLock)
- [ ] No information leakage in logs
- [ ] Pattern matching doesn't allow regex DoS

#### Performance
- [ ] O(1) get/set operations (dict-based)
- [ ] LRU eviction for memory management
- [ ] Size limits prevent memory exhaustion

#### Best Practices
- [ ] Type hints throughout
- [ ] Dataclasses for structured data
- [ ] Property for derived values

#### Maintainability
- [ ] Clear separation of concerns
- [ ] Statistics tracking
- [ ] Comprehensive logging

#### Documentation
- [ ] All classes and methods documented
- [ ] Attributes documented

#### Testing
- [ ] Thread safety testable
- [ ] TTL behavior testable
- [ ] Eviction behavior testable

#### Accessibility
- [ ] N/A (backend service)

#### Scalability
- [ ] Configurable size limits
- [ ] Disk cache extension point

#### Compatibility
- [ ] Python 3.9+ compatible
- [ ] No external dependencies

#### Error Handling
- [ ] Graceful handling of size estimation failure
- [ ] Safe eviction when full

#### Complexity
- [ ] Simple LRU implementation
- [ ] Clear flow

#### Architecture
- [ ] Single responsibility
- [ ] Interface suitable for disk cache extension

#### License
- [ ] N/A

#### Specification
- [ ] Matches ISSUE-54 caching requirements

---

## Step 13.2: Implement Performance Metrics

### Task
Create metrics collection and analysis system.

### Implementation

**anki_template_designer/services/performance/metrics.py**
```python
"""Performance metrics collection and analysis.

Tracks operation timing, resource usage, and provides
analysis and alerting capabilities.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
import statistics
import logging

logger = logging.getLogger("anki_template_designer.services.performance.metrics")


@dataclass
class MetricSample:
    """A single metric measurement.
    
    Attributes:
        value: The measured value.
        timestamp: When the measurement was taken.
        labels: Additional labels/tags.
    """
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Statistical summary of metric samples.
    
    Attributes:
        count: Number of samples.
        min: Minimum value.
        max: Maximum value.
        mean: Average value.
        median: Median value.
        p95: 95th percentile.
        p99: 99th percentile.
        std_dev: Standard deviation.
    """
    count: int = 0
    min: float = 0
    max: float = 0
    mean: float = 0
    median: float = 0
    p95: float = 0
    p99: float = 0
    std_dev: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "min": round(self.min, 3),
            "max": round(self.max, 3),
            "mean": round(self.mean, 3),
            "median": round(self.median, 3),
            "p95": round(self.p95, 3),
            "p99": round(self.p99, 3),
            "stdDev": round(self.std_dev, 3),
        }


class MetricsCollector:
    """Collects and analyzes performance metrics.
    
    Provides timing measurement, aggregation, and analysis
    for performance monitoring.
    """
    
    # Default retention period (1 hour)
    DEFAULT_RETENTION_SECONDS = 3600
    
    # Performance thresholds (ms)
    DEFAULT_THRESHOLDS = {
        "fast": 50,
        "acceptable": 100,
        "slow": 500,
        "critical": 1000,
    }
    
    def __init__(
        self,
        retention_seconds: int = DEFAULT_RETENTION_SECONDS
    ) -> None:
        """Initialize metrics collector.
        
        Args:
            retention_seconds: How long to keep samples.
        """
        self._metrics: Dict[str, List[MetricSample]] = defaultdict(list)
        self._lock = threading.RLock()
        self._retention_seconds = retention_seconds
        self._thresholds: Dict[str, Dict[str, float]] = {}
        self._active_timers: Dict[str, float] = {}
        
        logger.info(f"MetricsCollector initialized: retention={retention_seconds}s")
    
    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional labels/tags.
        """
        with self._lock:
            sample = MetricSample(
                value=value,
                labels=labels or {}
            )
            self._metrics[name].append(sample)
            
            # Check threshold
            self._check_threshold(name, value)
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation.
        
        Args:
            operation: Operation identifier.
            
        Returns:
            Timer ID for stopping.
        """
        timer_id = f"{operation}_{time.time_ns()}"
        
        with self._lock:
            self._active_timers[timer_id] = time.time()
        
        return timer_id
    
    def stop_timer(
        self,
        timer_id: str,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Stop a timer and record the duration.
        
        Args:
            timer_id: Timer ID from start_timer.
            labels: Optional labels for the metric.
            
        Returns:
            Duration in milliseconds.
        """
        end_time = time.time()
        
        with self._lock:
            if timer_id not in self._active_timers:
                logger.warning(f"Timer not found: {timer_id}")
                return 0
            
            start_time = self._active_timers.pop(timer_id)
        
        duration_ms = (end_time - start_time) * 1000
        
        # Extract operation name from timer_id
        operation = timer_id.rsplit("_", 1)[0]
        self.record(f"{operation}_duration_ms", duration_ms, labels)
        
        return duration_ms
    
    def time_operation(self, name: str) -> Callable:
        """Decorator for timing operations.
        
        Args:
            name: Operation name for the metric.
            
        Returns:
            Decorator function.
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                timer_id = self.start_timer(name)
                try:
                    return func(*args, **kwargs)
                finally:
                    self.stop_timer(timer_id)
            return wrapper
        return decorator
    
    def get_summary(
        self,
        name: str,
        time_window_seconds: Optional[int] = None
    ) -> MetricSummary:
        """Get statistical summary for a metric.
        
        Args:
            name: Metric name.
            time_window_seconds: Only include samples from this window.
            
        Returns:
            Statistical summary.
        """
        with self._lock:
            samples = self._get_samples_in_window(name, time_window_seconds)
        
        if not samples:
            return MetricSummary()
        
        values = [s.value for s in samples]
        sorted_values = sorted(values)
        
        return MetricSummary(
            count=len(values),
            min=min(values),
            max=max(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            p95=self._percentile(sorted_values, 95),
            p99=self._percentile(sorted_values, 99),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0,
        )
    
    def set_threshold(
        self,
        metric_name: str,
        warning: float,
        critical: float
    ) -> None:
        """Set alerting thresholds for a metric.
        
        Args:
            metric_name: Name of the metric.
            warning: Warning threshold value.
            critical: Critical threshold value.
        """
        self._thresholds[metric_name] = {
            "warning": warning,
            "critical": critical,
        }
    
    def get_all_metrics(self) -> Dict[str, MetricSummary]:
        """Get summaries for all metrics.
        
        Returns:
            Dictionary of metric name to summary.
        """
        with self._lock:
            return {
                name: self.get_summary(name)
                for name in self._metrics.keys()
            }
    
    def cleanup_old_samples(self) -> int:
        """Remove samples older than retention period.
        
        Returns:
            Number of samples removed.
        """
        cutoff = time.time() - self._retention_seconds
        removed = 0
        
        with self._lock:
            for name in self._metrics:
                original_len = len(self._metrics[name])
                self._metrics[name] = [
                    s for s in self._metrics[name]
                    if s.timestamp >= cutoff
                ]
                removed += original_len - len(self._metrics[name])
        
        if removed > 0:
            logger.debug(f"Cleaned up {removed} old metric samples")
        
        return removed
    
    def _get_samples_in_window(
        self,
        name: str,
        window_seconds: Optional[int]
    ) -> List[MetricSample]:
        """Get samples within time window."""
        samples = self._metrics.get(name, [])
        
        if window_seconds is None:
            return samples
        
        cutoff = time.time() - window_seconds
        return [s for s in samples if s.timestamp >= cutoff]
    
    def _percentile(self, sorted_values: List[float], p: int) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0
        
        k = (len(sorted_values) - 1) * p / 100
        f = int(k)
        c = f + 1 if f < len(sorted_values) - 1 else f
        
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])
    
    def _check_threshold(self, name: str, value: float) -> None:
        """Check if value exceeds thresholds."""
        if name not in self._thresholds:
            return
        
        thresholds = self._thresholds[name]
        
        if value >= thresholds["critical"]:
            logger.warning(f"CRITICAL: {name} = {value:.2f} (threshold: {thresholds['critical']})")
        elif value >= thresholds["warning"]:
            logger.info(f"WARNING: {name} = {value:.2f} (threshold: {thresholds['warning']})")
```

### Quality Checks

Same categories as Step 13.1 - refer to the standard checklist.

---

## Step 13.3: Create Performance Optimizer Facade

### Task
Create the main PerformanceOptimizer class that orchestrates all components.

### Implementation

**anki_template_designer/services/performance_optimizer.py**
```python
"""Performance Optimization Engine.

Main orchestrator for caching, metrics, and optimization features.
Implements ISSUE-54 specification.
"""

import logging
from typing import Any, Dict, Optional

from .performance.cache import MemoryCache, CacheStats
from .performance.metrics import MetricsCollector, MetricSummary

logger = logging.getLogger("anki_template_designer.services.performance_optimizer")


class PerformanceOptimizer:
    """Main performance optimization orchestrator.
    
    Coordinates caching, metrics collection, and optimization
    features for the template designer.
    
    Example usage:
        optimizer = PerformanceOptimizer()
        
        # Caching
        optimizer.cache_set("key", value, ttl=300)
        value = optimizer.cache_get("key")
        
        # Timing
        timer = optimizer.start_timing("operation")
        # ... do work ...
        duration = optimizer.stop_timing(timer)
        
        # Metrics
        stats = optimizer.get_performance_summary()
    """
    
    # Default configuration
    DEFAULT_MAX_CACHE_MB = 100
    DEFAULT_CACHE_TTL = 3600
    DEFAULT_METRICS_RETENTION = 3600
    
    def __init__(
        self,
        max_cache_mb: int = DEFAULT_MAX_CACHE_MB,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        metrics_retention: int = DEFAULT_METRICS_RETENTION
    ) -> None:
        """Initialize the performance optimizer.
        
        Args:
            max_cache_mb: Maximum cache size in MB.
            cache_ttl: Default cache TTL in seconds.
            metrics_retention: Metrics retention in seconds.
        """
        self._cache = MemoryCache(
            max_size_mb=max_cache_mb,
            default_ttl=cache_ttl
        )
        
        self._metrics = MetricsCollector(
            retention_seconds=metrics_retention
        )
        
        # Set default performance thresholds
        self._setup_default_thresholds()
        
        logger.info("PerformanceOptimizer initialized")
    
    # ===== Caching Methods =====
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None.
        """
        return self._cache.get(key)
    
    def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Optional TTL in seconds.
            
        Returns:
            True if stored successfully.
        """
        return self._cache.set(key, value, ttl)
    
    def cache_delete(self, key: str) -> bool:
        """Delete from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        return self._cache.delete(key)
    
    def cache_clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
    
    def cache_invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Glob pattern (supports *).
            
        Returns:
            Number of entries invalidated.
        """
        return self._cache.invalidate_pattern(pattern)
    
    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            Cache statistics.
        """
        return self._cache.get_stats()
    
    # ===== Metrics Methods =====
    
    def start_timing(self, operation: str) -> str:
        """Start timing an operation.
        
        Args:
            operation: Operation name.
            
        Returns:
            Timer ID.
        """
        return self._metrics.start_timer(operation)
    
    def stop_timing(
        self,
        timer_id: str,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Stop timing and record metric.
        
        Args:
            timer_id: Timer ID from start_timing.
            labels: Optional labels.
            
        Returns:
            Duration in milliseconds.
        """
        return self._metrics.stop_timer(timer_id, labels)
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional labels.
        """
        self._metrics.record(name, value, labels)
    
    def get_metric_summary(
        self,
        name: str,
        window_seconds: Optional[int] = None
    ) -> MetricSummary:
        """Get summary for a metric.
        
        Args:
            name: Metric name.
            window_seconds: Time window to analyze.
            
        Returns:
            Statistical summary.
        """
        return self._metrics.get_summary(name, window_seconds)
    
    def get_all_metrics(self) -> Dict[str, MetricSummary]:
        """Get summaries for all metrics.
        
        Returns:
            Dictionary of metric summaries.
        """
        return self._metrics.get_all_metrics()
    
    def set_metric_threshold(
        self,
        metric_name: str,
        warning: float,
        critical: float
    ) -> None:
        """Set alerting thresholds.
        
        Args:
            metric_name: Metric name.
            warning: Warning threshold.
            critical: Critical threshold.
        """
        self._metrics.set_threshold(metric_name, warning, critical)
    
    # ===== Combined Operations =====
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary.
        
        Returns:
            Dictionary with cache and metrics summaries.
        """
        cache_stats = self.get_cache_stats()
        all_metrics = self.get_all_metrics()
        
        return {
            "cache": {
                "hits": cache_stats.hits,
                "misses": cache_stats.misses,
                "hitRate": round(cache_stats.hit_rate * 100, 1),
                "entries": cache_stats.entries,
                "sizeBytes": cache_stats.size_bytes,
                "evictions": cache_stats.evictions,
            },
            "metrics": {
                name: summary.to_dict()
                for name, summary in all_metrics.items()
            },
            "health": self._calculate_health_status(),
        }
    
    def cleanup(self) -> Dict[str, int]:
        """Perform cleanup operations.
        
        Returns:
            Cleanup statistics.
        """
        expired_cache = self._cache.cleanup_expired()
        old_metrics = self._metrics.cleanup_old_samples()
        
        return {
            "expiredCacheEntries": expired_cache,
            "oldMetricSamples": old_metrics,
        }
    
    def _setup_default_thresholds(self) -> None:
        """Set up default performance thresholds."""
        # Template operations
        self.set_metric_threshold("template_load_duration_ms", 100, 500)
        self.set_metric_threshold("template_save_duration_ms", 200, 1000)
        
        # Rendering
        self.set_metric_threshold("render_duration_ms", 50, 200)
        
        # Bridge communication
        self.set_metric_threshold("bridge_call_duration_ms", 50, 200)
    
    def _calculate_health_status(self) -> str:
        """Calculate overall health status.
        
        Returns:
            Health status: 'healthy', 'degraded', or 'unhealthy'.
        """
        cache_stats = self.get_cache_stats()
        
        # Check cache health
        if cache_stats.hit_rate < 0.5 and cache_stats.hits + cache_stats.misses > 100:
            return "degraded"
        
        # Check for slow operations
        all_metrics = self.get_all_metrics()
        for name, summary in all_metrics.items():
            if "_duration_ms" in name and summary.p95 > 500:
                return "degraded"
            if "_duration_ms" in name and summary.p99 > 1000:
                return "unhealthy"
        
        return "healthy"
```

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_performance.py
"""Tests for performance optimization."""

import pytest
import time
from anki_template_designer.services.performance.cache import MemoryCache
from anki_template_designer.services.performance.metrics import MetricsCollector
from anki_template_designer.services.performance_optimizer import PerformanceOptimizer


class TestMemoryCache:
    def test_set_and_get(self):
        cache = MemoryCache(max_size_mb=1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_ttl_expiration(self):
        cache = MemoryCache(default_ttl=1)
        cache.set("key1", "value1", ttl=0.1)
        time.sleep(0.2)
        assert cache.get("key1") is None
    
    def test_lru_eviction(self):
        cache = MemoryCache(max_size_mb=0.001)  # Very small
        cache.set("key1", "x" * 500)
        cache.set("key2", "x" * 500)
        # key1 should be evicted
        stats = cache.get_stats()
        assert stats.evictions > 0


class TestMetrics:
    def test_record_and_summary(self):
        metrics = MetricsCollector()
        metrics.record("test_metric", 10)
        metrics.record("test_metric", 20)
        metrics.record("test_metric", 30)
        
        summary = metrics.get_summary("test_metric")
        assert summary.count == 3
        assert summary.mean == 20
    
    def test_timer(self):
        metrics = MetricsCollector()
        timer_id = metrics.start_timer("test_op")
        time.sleep(0.01)
        duration = metrics.stop_timer(timer_id)
        assert duration >= 10  # At least 10ms


class TestPerformanceOptimizer:
    def test_initialization(self):
        optimizer = PerformanceOptimizer()
        assert optimizer is not None
    
    def test_cache_operations(self):
        optimizer = PerformanceOptimizer()
        optimizer.cache_set("test", {"data": 123})
        assert optimizer.cache_get("test") == {"data": 123}
    
    def test_performance_summary(self):
        optimizer = PerformanceOptimizer()
        summary = optimizer.get_performance_summary()
        assert "cache" in summary
        assert "metrics" in summary
        assert "health" in summary
```

Run:
```bash
python -m pytest anki_template_designer/tests/test_performance.py -v
```

### Manual Verification

1. [ ] Open Template Designer
2. [ ] Perform multiple operations
3. [ ] Check performance summary via bridge
4. [ ] Verify cache hit rates improve on repeated operations
5. [ ] Check console for performance warnings

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Cache operations work correctly
- [ ] Metrics collection accurate
- [ ] TTL expiration works
- [ ] LRU eviction works
- [ ] Performance summary available

---

## Next Step

After successful completion, proceed to [14-BACKUP-MANAGER.md](14-BACKUP-MANAGER.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
