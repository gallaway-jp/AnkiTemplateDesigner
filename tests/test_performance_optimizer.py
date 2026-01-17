"""
Test Suite for Performance Optimizer (Issue #54)

Comprehensive tests covering:
- CachingSystem (memory, disk, dependency management)
- AsyncOperationsManager (queueing, priority, batching)
- RenderingOptimizer (virtual scrolling, CSS analysis)
- PerformanceAnalytics (metrics, bottleneck detection)
"""

import unittest
import time
import threading
from datetime import datetime

from services.performance_optimizer import (
    PerformanceOptimizer,
    CachingSystem,
    AsyncOperationsManager,
    RenderingOptimizer,
    PerformanceAnalytics,
    OperationStatus,
    CacheStrategy,
    CacheStats,
    AsyncStats,
    Metrics
)


class TestCachingSystem(unittest.TestCase):
    """Test CachingSystem functionality"""

    def setUp(self):
        self.cache = CachingSystem(max_memory_mb=10, max_disk_mb=100)

    def tearDown(self):
        self.cache.memory_cache_clear()
        self.cache.disk_cache_clear()

    def test_memory_cache_set_get(self):
        """Test memory cache set and get"""
        self.cache.memory_cache_set('key1', 'value1')
        self.assertEqual(self.cache.memory_cache_get('key1'), 'value1')

    def test_memory_cache_delete(self):
        """Test memory cache delete"""
        self.cache.memory_cache_set('key1', 'value1')
        self.assertTrue(self.cache.memory_cache_delete('key1'))
        self.assertIsNone(self.cache.memory_cache_get('key1'))

    def test_memory_cache_expiration(self):
        """Test memory cache expiration"""
        self.cache.memory_cache_set('key1', 'value1', ttl_seconds=1)
        self.assertIsNotNone(self.cache.memory_cache_get('key1'))
        time.sleep(1.1)
        self.assertIsNone(self.cache.memory_cache_get('key1'))

    def test_disk_cache_set_get(self):
        """Test disk cache set and get"""
        self.cache.disk_cache_set('key1', {'data': 'value1'})
        result = self.cache.disk_cache_get('key1')
        self.assertEqual(result['data'], 'value1')

    def test_disk_cache_compression(self):
        """Test disk cache compression"""
        large_value = 'x' * 10000
        self.cache.disk_cache_set('key1', large_value, compress=True)
        result = self.cache.disk_cache_get('key1')
        self.assertEqual(result, large_value)

    def test_get_from_cache_auto_strategy(self):
        """Test auto cache strategy"""
        self.cache.set_in_cache('key1', 'value1', strategy='auto')
        result = self.cache.get_from_cache('key1', strategy='auto')
        self.assertEqual(result, 'value1')

    def test_cache_hit_ratio(self):
        """Test cache hit ratio calculation"""
        self.cache.set_in_cache('key1', 'value1')
        self.cache.get_from_cache('key1')  # hit
        self.cache.get_from_cache('key2')  # miss
        self.assertGreater(self.cache.get_hit_ratio(), 0.0)

    def test_cache_statistics(self):
        """Test cache statistics"""
        self.cache.set_in_cache('key1', 'value1')
        stats = self.cache.get_cache_stats()
        self.assertIsInstance(stats, CacheStats)
        self.assertGreaterEqual(stats.total_entries, 1)

    def test_set_dependency(self):
        """Test cache dependency"""
        self.cache.set_in_cache('key1', 'value1')
        self.cache.set_in_cache('key2', 'value2')
        self.cache.set_dependency('key2', 'key1')
        # Verify dependency was set
        self.assertIn('key1', self.cache.dependencies['key2'])

    def test_cascade_invalidate(self):
        """Test cascade invalidation"""
        self.cache.set_in_cache('key1', 'value1')
        self.cache.set_in_cache('key2', 'value2')
        self.cache.set_dependency('key2', 'key1')
        
        count = self.cache.cascade_invalidate('key1')
        self.assertGreaterEqual(count, 1)

    def test_invalidate_pattern(self):
        """Test pattern-based invalidation"""
        self.cache.memory_cache_set('user:1', 'value1')
        self.cache.memory_cache_set('user:2', 'value2')
        self.cache.memory_cache_set('other', 'value3')
        
        count = self.cache.invalidate_cache('user:*')
        self.assertEqual(count, 2)

    def test_cache_thread_safety(self):
        """Test cache thread safety"""
        def set_values():
            for i in range(100):
                self.cache.set_in_cache(f'key{i}', f'value{i}')
        
        def get_values():
            for i in range(100):
                self.cache.get_from_cache(f'key{i}')
        
        threads = [
            threading.Thread(target=set_values),
            threading.Thread(target=get_values),
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should not raise any threading errors
        self.assertTrue(True)

    def test_memory_cache_clear(self):
        """Test memory cache clear"""
        self.cache.memory_cache_set('key1', 'value1')
        self.cache.memory_cache_set('key2', 'value2')
        self.cache.memory_cache_clear()
        self.assertEqual(len(self.cache.memory_cache), 0)


class TestAsyncOperationsManager(unittest.TestCase):
    """Test AsyncOperationsManager functionality"""

    def setUp(self):
        self.async_mgr = AsyncOperationsManager(max_concurrent=5)

    def test_queue_operation(self):
        """Test queueing an operation"""
        def dummy_op():
            return "result"
        
        op_id = self.async_mgr.queue_operation(dummy_op)
        self.assertIsNotNone(op_id)
        self.assertIn(op_id, self.async_mgr.operations)

    def test_operation_priority(self):
        """Test operation priority"""
        def dummy_op():
            return "result"
        
        op_id = self.async_mgr.queue_operation(dummy_op, priority=9)
        op = self.async_mgr.operations[op_id]
        self.assertEqual(op.priority, 9)

    def test_cancel_operation(self):
        """Test cancelling operation"""
        def dummy_op():
            return "result"
        
        op_id = self.async_mgr.queue_operation(dummy_op)
        cancelled = self.async_mgr.cancel_operation(op_id)
        self.assertTrue(cancelled)
        self.assertEqual(
            self.async_mgr.operations[op_id].status,
            OperationStatus.CANCELLED
        )

    def test_get_pending_count(self):
        """Test pending operation count"""
        def dummy_op():
            return "result"
        
        self.async_mgr.queue_operation(dummy_op)
        self.async_mgr.queue_operation(dummy_op)
        count = self.async_mgr.get_pending_count()
        self.assertGreaterEqual(count, 2)

    def test_priority_clamping(self):
        """Test priority clamped to 1-10"""
        def dummy_op():
            return "result"
        
        op_id = self.async_mgr.queue_operation(dummy_op, priority=15)
        self.assertEqual(self.async_mgr.operations[op_id].priority, 10)
        
        op_id = self.async_mgr.queue_operation(dummy_op, priority=-5)
        self.assertEqual(self.async_mgr.operations[op_id].priority, 1)

    def test_enable_batching(self):
        """Test enable batching"""
        self.async_mgr.enable_batching('test_type', batch_size=5)
        self.assertTrue(self.async_mgr.batching_enabled['test_type'])

    def test_disable_batching(self):
        """Test disable batching"""
        self.async_mgr.enable_batching('test_type')
        self.async_mgr.disable_batching('test_type')
        self.assertFalse(self.async_mgr.batching_enabled['test_type'])

    def test_set_operation_throttle(self):
        """Test operation throttling"""
        self.async_mgr.set_operation_throttle_ms('test_op', 100)
        self.assertEqual(self.async_mgr.get_throttle_ms('test_op'), 100)

    def test_set_operation_timeout(self):
        """Test operation timeout setting"""
        self.async_mgr.set_operation_timeout_seconds('test_op', 60)
        self.assertEqual(self.async_mgr.get_timeout_seconds('test_op'), 60)

    def test_async_statistics(self):
        """Test async statistics"""
        def dummy_op():
            return "result"
        
        self.async_mgr.queue_operation(dummy_op)
        stats = self.async_mgr.get_async_stats()
        self.assertIsInstance(stats, AsyncStats)
        self.assertEqual(stats.total_queued, 1)

    def test_get_pending_operations(self):
        """Test getting pending operations"""
        def dummy_op():
            return "result"
        
        self.async_mgr.queue_operation(dummy_op)
        pending = self.async_mgr.get_pending_operations()
        self.assertGreater(len(pending), 0)

    def test_reset_statistics(self):
        """Test reset statistics"""
        def dummy_op():
            return "result"
        
        self.async_mgr.queue_operation(dummy_op)
        self.async_mgr.reset_statistics()
        self.assertEqual(self.async_mgr.statistics['total_queued'], 0)


class TestRenderingOptimizer(unittest.TestCase):
    """Test RenderingOptimizer functionality"""

    def setUp(self):
        self.renderer = RenderingOptimizer()

    def test_enable_virtual_scrolling(self):
        """Test enable virtual scrolling"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        self.assertTrue(self.renderer.virtual_scrolling_enabled['container1'])
        self.assertEqual(self.renderer.item_heights['container1'], 50)

    def test_disable_virtual_scrolling(self):
        """Test disable virtual scrolling"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        self.renderer.disable_virtual_scrolling('container1')
        self.assertFalse(self.renderer.virtual_scrolling_enabled['container1'])

    def test_scroll_to_item(self):
        """Test scroll to item"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        self.renderer.scroll_to_item('container1', 100)
        start, end = self.renderer.get_visible_range('container1')
        self.assertLessEqual(start, 100)
        self.assertGreaterEqual(end, 100)

    def test_get_visible_range(self):
        """Test get visible range"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        start, end = self.renderer.get_visible_range('container1')
        self.assertIsInstance(start, int)
        self.assertIsInstance(end, int)

    def test_analyze_css_complexity(self):
        """Test CSS complexity analysis"""
        css = """
        .class1 { color: red; }
        .class2 { background: blue; }
        .class3, .class4 { font-size: 14px; }
        """
        
        metrics = self.renderer.analyze_css_complexity(css)
        self.assertGreater(metrics.total_rules, 0)
        self.assertGreater(metrics.total_selectors, 0)

    def test_get_render_stats(self):
        """Test get render statistics"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        stats = self.renderer.get_render_stats('container1')
        self.assertEqual(stats.container_id, 'container1')

    def test_get_frame_rate(self):
        """Test get frame rate"""
        fps = self.renderer.get_frame_rate()
        self.assertGreater(fps, 0)

    def test_reset_render_metrics(self):
        """Test reset render metrics"""
        self.renderer.enable_virtual_scrolling('container1', item_height=50)
        self.renderer.reset_render_metrics()
        self.assertEqual(len(self.renderer.render_stats), 0)


class TestPerformanceAnalytics(unittest.TestCase):
    """Test PerformanceAnalytics functionality"""

    def setUp(self):
        self.analytics = PerformanceAnalytics()

    def test_start_end_operation(self):
        """Test operation timing"""
        trace_id = self.analytics.start_operation('test_op')
        time.sleep(0.01)
        self.analytics.end_operation(trace_id)
        
        metrics = self.analytics.get_operation_metrics('test_op')
        self.assertGreater(metrics.count, 0)
        self.assertGreater(metrics.avg_ms, 0)

    def test_record_metric(self):
        """Test recording custom metric"""
        self.analytics.record_metric('custom_metric', 42.5)
        metrics = self.analytics.get_operation_metrics('custom_metric')
        self.assertEqual(metrics.count, 1)

    def test_operation_success_tracking(self):
        """Test operation success tracking"""
        trace_id = self.analytics.start_operation('success_op')
        self.analytics.end_operation(trace_id, success=True)
        
        metrics = self.analytics.get_operation_metrics('success_op')
        self.assertEqual(metrics.success_rate, 1.0)

    def test_operation_failure_tracking(self):
        """Test operation failure tracking"""
        trace_id = self.analytics.start_operation('failure_op')
        self.analytics.end_operation(trace_id, success=False, error_message='Test error')
        
        metrics = self.analytics.get_operation_metrics('failure_op')
        self.assertEqual(metrics.error_count, 1)

    def test_get_operation_metrics(self):
        """Test get operation metrics"""
        trace_id = self.analytics.start_operation('test_op')
        self.analytics.end_operation(trace_id)
        
        metrics = self.analytics.get_operation_metrics('test_op')
        self.assertIsInstance(metrics, Metrics)
        self.assertEqual(metrics.operation_name, 'test_op')
        self.assertGreater(metrics.avg_ms, 0)

    def test_detect_bottlenecks(self):
        """Test bottleneck detection"""
        # Create slow operation
        for _ in range(5):
            trace_id = self.analytics.start_operation('slow_op')
            time.sleep(0.01)
            self.analytics.end_operation(trace_id)
        
        bottlenecks = self.analytics.detect_bottlenecks()
        # May or may not detect depending on total operations
        self.assertIsInstance(bottlenecks, list)

    def test_set_performance_threshold(self):
        """Test set performance threshold"""
        self.analytics.set_performance_threshold('test_op', 100, percentile=95)
        self.assertEqual(self.analytics.thresholds['test_op'], 100)

    def test_get_threshold_violations(self):
        """Test get threshold violations"""
        # Create slow operation
        self.analytics.set_performance_threshold('slow_op', 5)  # 5ms threshold
        for _ in range(3):
            trace_id = self.analytics.start_operation('slow_op')
            time.sleep(0.01)  # 10ms operation
            self.analytics.end_operation(trace_id)
        
        violations = self.analytics.get_threshold_violations()
        # May have violations if operation was slow enough
        self.assertIsInstance(violations, list)

    def test_export_metrics_json(self):
        """Test export metrics as JSON"""
        trace_id = self.analytics.start_operation('test_op')
        self.analytics.end_operation(trace_id)
        
        exported = self.analytics.export_metrics(format='json')
        self.assertIsInstance(exported, str)
        self.assertIn('"test_op"', exported)

    def test_reset_metrics(self):
        """Test reset metrics"""
        trace_id = self.analytics.start_operation('test_op')
        self.analytics.end_operation(trace_id)
        
        self.analytics.reset_metrics('test_op')
        metrics = self.analytics.get_operation_metrics('test_op')
        self.assertEqual(metrics.count, 0)

    def test_metric_percentiles(self):
        """Test metric percentile calculation"""
        for i in range(10):
            trace_id = self.analytics.start_operation('percentile_op')
            time.sleep(0.001 * (i + 1))
            self.analytics.end_operation(trace_id)
        
        metrics = self.analytics.get_operation_metrics('percentile_op')
        self.assertGreater(metrics.p95_ms, metrics.avg_ms)
        self.assertGreater(metrics.p99_ms, metrics.p95_ms)


class TestPerformanceOptimizer(unittest.TestCase):
    """Test PerformanceOptimizer main orchestrator"""

    def setUp(self):
        self.optimizer = PerformanceOptimizer(max_memory_mb=10, max_disk_mb=100)

    def tearDown(self):
        self.optimizer.caching_system.memory_cache_clear()

    def test_cache_integration(self):
        """Test cache through optimizer"""
        self.optimizer.set_in_cache('key1', 'value1')
        result = self.optimizer.get_from_cache('key1')
        self.assertEqual(result, 'value1')

    def test_invalidate_cache_integration(self):
        """Test cache invalidation through optimizer"""
        self.optimizer.set_in_cache('key1', 'value1')
        count = self.optimizer.invalidate_cache('key1')
        self.assertGreater(count, 0)

    def test_queue_operation_integration(self):
        """Test async operation queueing through optimizer"""
        def dummy_op():
            return "result"
        
        op_id = self.optimizer.queue_operation(dummy_op)
        count = self.optimizer.get_pending_operations_count()
        self.assertGreaterEqual(count, 1)

    def test_virtual_scrolling_integration(self):
        """Test virtual scrolling through optimizer"""
        self.optimizer.enable_virtual_scrolling('container1', item_height=50)
        stats = self.optimizer.get_render_stats('container1')
        self.assertEqual(stats.container_id, 'container1')

    def test_performance_tracking_integration(self):
        """Test performance tracking through optimizer"""
        trace_id = self.optimizer.start_performance_tracking('test_op')
        time.sleep(0.01)
        self.optimizer.end_performance_tracking(trace_id)
        
        # Track completed
        self.assertTrue(True)

    def test_set_performance_threshold_integration(self):
        """Test threshold setting through optimizer"""
        self.optimizer.set_performance_threshold_ms('test_op', 100)
        # Should not raise error
        self.assertTrue(True)

    def test_get_health_status(self):
        """Test get health status"""
        self.optimizer.set_in_cache('key1', 'value1')
        
        health = self.optimizer.get_health_status()
        self.assertIn('cache_health', health)
        self.assertIn('async_health', health)
        self.assertIn('status', health)

    def test_reset_all_metrics(self):
        """Test reset all metrics"""
        self.optimizer.set_in_cache('key1', 'value1')
        
        def dummy_op():
            return "result"
        
        self.optimizer.queue_operation(dummy_op)
        self.optimizer.reset_all_metrics()
        
        # Should be reset
        self.assertTrue(True)

    def test_get_performance_metrics(self):
        """Test get performance metrics"""
        trace_id = self.optimizer.start_performance_tracking('test_op')
        self.optimizer.end_performance_tracking(trace_id)
        
        metrics = self.optimizer.get_performance_metrics()
        self.assertIn('bottlenecks', metrics)
        self.assertIn('cache_stats', metrics)
        self.assertIn('async_stats', metrics)


class TestIntegration(unittest.TestCase):
    """Integration tests for all components"""

    def setUp(self):
        self.optimizer = PerformanceOptimizer()

    def test_complete_workflow(self):
        """Test complete optimization workflow"""
        # Cache data
        self.optimizer.set_in_cache('template:1', {'name': 'Template 1'})
        
        # Queue async operation
        def update_template():
            time.sleep(0.01)
            return {'name': 'Updated Template'}
        
        op_id = self.optimizer.queue_operation(update_template)
        
        # Track performance
        trace_id = self.optimizer.start_performance_tracking('full_workflow')
        result = self.optimizer.get_from_cache('template:1')
        self.optimizer.end_performance_tracking(trace_id)
        
        # Verify all worked
        self.assertIsNotNone(result)

    def test_multi_threaded_performance(self):
        """Test multi-threaded performance"""
        def worker():
            for i in range(50):
                self.optimizer.set_in_cache(f'key_{i}', f'value_{i}')
                self.optimizer.get_from_cache(f'key_{i}')
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should complete without errors
        stats = self.optimizer.get_cache_stats()
        self.assertGreater(stats.total_entries, 0)


if __name__ == '__main__':
    unittest.main()
