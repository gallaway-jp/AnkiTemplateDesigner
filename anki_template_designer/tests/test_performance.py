"""
Tests for performance optimization services.

Plan 13: Tests for cache, metrics, and optimizer.
"""

import time
import pytest
from unittest.mock import Mock, patch

from anki_template_designer.services.performance.cache import (
    CacheEntry,
    CacheStats,
    MemoryCache
)
from anki_template_designer.services.performance.metrics import (
    Metric,
    MetricType,
    TimingStats,
    MetricsTracker
)
from anki_template_designer.services.performance.optimizer import (
    PerformanceOptimizer,
    PerformanceReport,
    get_optimizer,
    init_optimizer
)


class TestCacheEntry:
    """Tests for CacheEntry class."""
    
    def test_default_values(self):
        """Test default entry values."""
        entry = CacheEntry(value="test")
        assert entry.value == "test"
        assert entry.hits == 0
        assert entry.expires_at == 0
    
    def test_is_expired_never(self):
        """Test entry that never expires."""
        entry = CacheEntry(value="test", expires_at=0)
        assert not entry.is_expired()
    
    def test_is_expired_future(self):
        """Test entry with future expiration."""
        entry = CacheEntry(value="test", expires_at=time.time() + 100)
        assert not entry.is_expired()
    
    def test_is_expired_past(self):
        """Test expired entry."""
        entry = CacheEntry(value="test", expires_at=time.time() - 1)
        assert entry.is_expired()
    
    def test_time_to_live(self):
        """Test TTL calculation."""
        entry = CacheEntry(value="test", expires_at=time.time() + 60)
        ttl = entry.time_to_live()
        assert 59 <= ttl <= 60


class TestCacheStats:
    """Tests for CacheStats class."""
    
    def test_hit_rate_zero(self):
        """Test hit rate with no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=75, misses=25)
        assert stats.hit_rate == 0.75
    
    def test_total_requests(self):
        """Test total requests calculation."""
        stats = CacheStats(hits=50, misses=30)
        assert stats.total_requests == 80
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = CacheStats(hits=10, misses=5, entries=8, evictions=2)
        d = stats.to_dict()
        assert d["hits"] == 10
        assert d["misses"] == 5
        assert d["hitRate"] == pytest.approx(0.6667, rel=0.01)


class TestMemoryCache:
    """Tests for MemoryCache class."""
    
    def test_basic_get_set(self):
        """Test basic get/set operations."""
        cache = MemoryCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_missing_returns_default(self):
        """Test get with missing key returns default."""
        cache = MemoryCache()
        assert cache.get("missing") is None
        assert cache.get("missing", "default") == "default"
    
    def test_set_with_ttl(self):
        """Test set with TTL."""
        cache = MemoryCache(default_ttl=3600)
        cache.set("key", "value", ttl=1)
        assert cache.get("key") == "value"
        # Can't easily test expiration without sleeping
    
    def test_delete(self):
        """Test delete operation."""
        cache = MemoryCache()
        cache.set("key", "value")
        assert cache.delete("key") is True
        assert cache.get("key") is None
    
    def test_delete_missing(self):
        """Test delete missing key."""
        cache = MemoryCache()
        assert cache.delete("missing") is False
    
    def test_has(self):
        """Test has operation."""
        cache = MemoryCache()
        cache.set("key", "value")
        assert cache.has("key") is True
        assert cache.has("missing") is False
    
    def test_clear(self):
        """Test clear operation."""
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        count = cache.clear()
        assert count == 2
        assert cache.size == 0
    
    def test_invalidate_pattern(self):
        """Test pattern invalidation."""
        cache = MemoryCache()
        cache.set("user:1", "data1")
        cache.set("user:2", "data2")
        cache.set("post:1", "data3")
        
        count = cache.invalidate_pattern("user:*")
        assert count == 2
        assert not cache.has("user:1")
        assert cache.has("post:1")
    
    def test_stats_tracking(self):
        """Test statistics tracking."""
        cache = MemoryCache()
        cache.set("key", "value")
        cache.get("key")  # Hit
        cache.get("key")  # Hit
        cache.get("missing")  # Miss
        
        stats = cache.get_stats()
        assert stats.hits == 2
        assert stats.misses == 1
        assert stats.entries == 1
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Create tiny cache
        cache = MemoryCache(max_size_mb=1, default_ttl=0)
        
        # Fill with large values
        large_value = "x" * 100000  # ~100KB
        for i in range(20):
            cache.set(f"key{i}", large_value)
        
        # Some keys should have been evicted
        stats = cache.get_stats()
        assert stats.evictions > 0
    
    def test_get_or_set(self):
        """Test get_or_set operation."""
        cache = MemoryCache()
        factory = Mock(return_value="computed")
        
        # First call computes
        result = cache.get_or_set("key", factory)
        assert result == "computed"
        assert factory.called
        
        # Second call uses cache
        factory.reset_mock()
        result = cache.get_or_set("key", factory)
        assert result == "computed"
        assert not factory.called
    
    def test_keys_and_items(self):
        """Test keys and items methods."""
        cache = MemoryCache()
        cache.set("a", 1)
        cache.set("b", 2)
        
        assert set(cache.keys()) == {"a", "b"}
        items = dict(cache.items())
        assert items == {"a": 1, "b": 2}


class TestTimingStats:
    """Tests for TimingStats class."""
    
    def test_record_single(self):
        """Test recording single timing."""
        stats = TimingStats()
        stats.record(50.0)
        
        assert stats.count == 1
        assert stats.total_ms == 50.0
        assert stats.min_ms == 50.0
        assert stats.max_ms == 50.0
        assert stats.last_ms == 50.0
    
    def test_record_multiple(self):
        """Test recording multiple timings."""
        stats = TimingStats()
        stats.record(10.0)
        stats.record(30.0)
        stats.record(20.0)
        
        assert stats.count == 3
        assert stats.total_ms == 60.0
        assert stats.min_ms == 10.0
        assert stats.max_ms == 30.0
        assert stats.avg_ms == 20.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = TimingStats()
        stats.record(25.5)
        
        d = stats.to_dict()
        assert d["count"] == 1
        assert d["avgMs"] == 25.5


class TestMetricsTracker:
    """Tests for MetricsTracker class."""
    
    def test_increment(self):
        """Test counter increment."""
        tracker = MetricsTracker()
        tracker.increment("requests")
        tracker.increment("requests")
        assert tracker.get_counter("requests") == 2
    
    def test_increment_by_value(self):
        """Test increment by specific value."""
        tracker = MetricsTracker()
        tracker.increment("bytes", 1024)
        tracker.increment("bytes", 2048)
        assert tracker.get_counter("bytes") == 3072
    
    def test_decrement(self):
        """Test counter decrement."""
        tracker = MetricsTracker()
        tracker.increment("active", 10)
        tracker.decrement("active", 3)
        assert tracker.get_counter("active") == 7
    
    def test_set_gauge(self):
        """Test gauge setting."""
        tracker = MetricsTracker()
        tracker.set_gauge("memory", 256.5)
        assert tracker.get_gauge("memory") == 256.5
    
    def test_gauge_overwrite(self):
        """Test gauge overwrites previous value."""
        tracker = MetricsTracker()
        tracker.set_gauge("cpu", 50.0)
        tracker.set_gauge("cpu", 75.0)
        assert tracker.get_gauge("cpu") == 75.0
    
    def test_record_timing(self):
        """Test timing recording."""
        tracker = MetricsTracker()
        tracker.record_timing("render", 25.5)
        tracker.record_timing("render", 30.0)
        
        stats = tracker.get_timing_stats("render")
        assert stats.count == 2
        assert stats.avg_ms == 27.75
    
    def test_time_context_manager(self):
        """Test timing context manager."""
        tracker = MetricsTracker()
        
        with tracker.time("operation"):
            time.sleep(0.01)  # 10ms
        
        stats = tracker.get_timing_stats("operation")
        assert stats.count == 1
        assert stats.avg_ms >= 10  # At least 10ms
    
    def test_get_all_counters(self):
        """Test getting all counters."""
        tracker = MetricsTracker()
        tracker.increment("a")
        tracker.increment("b", 5)
        
        counters = tracker.get_all_counters()
        assert counters == {"a": 1, "b": 5}
    
    def test_get_summary(self):
        """Test getting summary."""
        tracker = MetricsTracker()
        tracker.increment("counter")
        tracker.set_gauge("gauge", 1.5)
        tracker.record_timing("timing", 10.0)
        
        summary = tracker.get_summary()
        assert "counters" in summary
        assert "gauges" in summary
        assert "timings" in summary
    
    def test_reset(self):
        """Test reset all metrics."""
        tracker = MetricsTracker()
        tracker.increment("counter")
        tracker.set_gauge("gauge", 1.0)
        
        tracker.reset()
        
        assert tracker.get_counter("counter") == 0
        assert tracker.get_gauge("gauge") is None
    
    def test_recent_metrics_history(self):
        """Test recent metrics history."""
        tracker = MetricsTracker(history_size=5)
        
        for i in range(10):
            tracker.increment(f"metric{i}")
        
        recent = tracker.get_recent_metrics(3)
        assert len(recent) == 3


class TestPerformanceOptimizer:
    """Tests for PerformanceOptimizer class."""
    
    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = PerformanceOptimizer()
        assert optimizer.get_uptime() >= 0
    
    def test_cache_operations(self):
        """Test cache get/set/delete."""
        optimizer = PerformanceOptimizer()
        
        optimizer.cache_set("key", "value")
        assert optimizer.cache_get("key") == "value"
        
        optimizer.cache_delete("key")
        assert optimizer.cache_get("key") is None
    
    def test_cache_with_ttl(self):
        """Test cache with TTL."""
        optimizer = PerformanceOptimizer(cache_ttl=3600)
        optimizer.cache_set("key", "value", ttl=60)
        assert optimizer.cache_get("key") == "value"
    
    def test_cache_clear(self):
        """Test cache clear."""
        optimizer = PerformanceOptimizer()
        optimizer.cache_set("key1", "value1")
        optimizer.cache_set("key2", "value2")
        
        count = optimizer.cache_clear()
        assert count == 2
    
    def test_template_cache(self):
        """Test template caching."""
        optimizer = PerformanceOptimizer()
        
        optimizer.cache_template("tmpl1", "<div>{{content}}</div>")
        content = optimizer.get_cached_template("tmpl1")
        assert "{{content}}" in content
        
        optimizer.invalidate_template("tmpl1")
        assert optimizer.get_cached_template("tmpl1") is None
    
    def test_preview_cache(self):
        """Test preview caching."""
        optimizer = PerformanceOptimizer()
        
        optimizer.cache_preview("preview:1", "<html>test</html>")
        assert optimizer.get_cached_preview("preview:1") == "<html>test</html>"
        
        count = optimizer.invalidate_previews()
        assert count == 1
    
    def test_metrics_tracking(self):
        """Test metrics tracking through optimizer."""
        optimizer = PerformanceOptimizer()
        
        optimizer.increment("requests")
        optimizer.increment("requests")
        optimizer.set_gauge("connections", 5)
        optimizer.track_timing("render", 25.0)
        
        summary = optimizer.get_metrics_summary()
        assert summary["counters"]["requests"] == 2
        assert summary["gauges"]["connections"] == 5
    
    def test_timing_context_manager(self):
        """Test timing context manager."""
        optimizer = PerformanceOptimizer()
        
        with optimizer.time("operation"):
            time.sleep(0.01)
        
        stats = optimizer.get_timing_stats("operation")
        assert stats.count == 1
    
    def test_performance_report(self):
        """Test performance report generation."""
        optimizer = PerformanceOptimizer()
        
        # Generate some activity
        for i in range(10):
            optimizer.cache_set(f"key{i}", f"value{i}")
            optimizer.cache_get(f"key{i}")
        
        optimizer.track_timing("render", 50.0)
        
        report = optimizer.get_performance_report()
        assert report.cache_stats is not None
        assert report.timing_stats is not None
        assert len(report.recommendations) > 0
    
    def test_get_all_cache_stats(self):
        """Test getting all cache stats."""
        optimizer = PerformanceOptimizer()
        
        all_stats = optimizer.get_all_cache_stats()
        assert "main" in all_stats
        assert "templates" in all_stats
        assert "previews" in all_stats
    
    def test_cleanup(self):
        """Test cleanup operation."""
        optimizer = PerformanceOptimizer()
        
        result = optimizer.cleanup()
        assert "main" in result
        assert "templates" in result
        assert "previews" in result
    
    def test_reset_metrics(self):
        """Test resetting metrics only."""
        optimizer = PerformanceOptimizer()
        optimizer.increment("counter")
        optimizer.cache_set("key", "value")
        
        optimizer.reset_metrics()
        
        # Metrics reset, cache preserved
        assert optimizer.get_metrics_summary()["counters"] == {}
        assert optimizer.cache_get("key") == "value"
    
    def test_reset_all(self):
        """Test resetting everything."""
        optimizer = PerformanceOptimizer()
        optimizer.increment("counter")
        optimizer.cache_set("key", "value")
        
        optimizer.reset_all()
        
        assert optimizer.get_metrics_summary()["counters"] == {}
        assert optimizer.cache_get("key") is None


class TestGlobalFunctions:
    """Tests for global optimizer functions."""
    
    def test_init_optimizer(self):
        """Test initializing global optimizer."""
        optimizer = init_optimizer(cache_size_mb=25, cache_ttl=300)
        
        assert optimizer is not None
        assert isinstance(optimizer, PerformanceOptimizer)
    
    def test_get_optimizer(self):
        """Test getting global optimizer."""
        init_optimizer()
        
        optimizer = get_optimizer()
        assert optimizer is not None


class TestPerformanceReport:
    """Tests for PerformanceReport class."""
    
    def test_to_dict(self):
        """Test report to dictionary."""
        report = PerformanceReport(
            cache_stats={"hits": 10},
            timing_stats={"render": {"avgMs": 25}},
            counters={"requests": 100},
            gauges={"memory": 256.0},
            recommendations=["All good!"]
        )
        
        d = report.to_dict()
        assert d["cacheStats"]["hits"] == 10
        assert d["recommendations"] == ["All good!"]
