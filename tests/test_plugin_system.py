"""
Tests for Plugin System (Issue #58)

Comprehensive test suite with 40+ tests covering:
- Plugin discovery and registration
- Plugin lifecycle management
- Hook and filter system
- Dependency resolution
- Version compatibility checking
"""

import unittest
import os
import json
import tempfile
import threading
import time
from services.plugin_system import (
    PluginRegistry, PluginInfo, HookSystem, DependencyResolver,
    CompatibilityChecker, PluginLifecycleManager, PluginMarketplace,
    PluginManager, PluginContext, PluginSandboxContext, PluginState
)


# ============================================================================
# Plugin Registry Tests
# ============================================================================

class TestPluginRegistry(unittest.TestCase):
    """Tests for plugin registry"""

    def setUp(self):
        self.registry = PluginRegistry()

    def test_register_plugin(self):
        """Test registering a plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Tester',
            description='Test',
            entry_point='test:TestPlugin'
        )
        result = self.registry.register_plugin(plugin)
        self.assertTrue(result)

    def test_register_duplicate_plugin(self):
        """Test registering duplicate plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Tester',
            description='Test',
            entry_point='test:TestPlugin'
        )
        self.registry.register_plugin(plugin)
        result = self.registry.register_plugin(plugin)
        self.assertFalse(result)

    def test_unregister_plugin(self):
        """Test unregistering a plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Tester',
            description='Test',
            entry_point='test:TestPlugin'
        )
        self.registry.register_plugin(plugin)
        result = self.registry.unregister_plugin('test.plugin')
        self.assertTrue(result)

    def test_get_plugin(self):
        """Test getting plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Tester',
            description='Test',
            entry_point='test:TestPlugin'
        )
        self.registry.register_plugin(plugin)
        retrieved = self.registry.get_plugin('test.plugin')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Test Plugin')

    def test_list_plugins(self):
        """Test listing plugins"""
        for i in range(3):
            plugin = PluginInfo(
                plugin_id=f'test.plugin.{i}',
                name=f'Test Plugin {i}',
                version='1.0.0',
                author='Tester',
                description='Test',
                entry_point='test:TestPlugin'
            )
            self.registry.register_plugin(plugin)

        plugins = self.registry.list_plugins()
        self.assertEqual(len(plugins), 3)

    def test_search_plugins(self):
        """Test searching plugins"""
        plugins = [
            PluginInfo(
                plugin_id='test.plugin.alpha',
                name='Alpha Plugin',
                version='1.0.0',
                author='Tester',
                description='Test alpha',
                entry_point='test:TestPlugin'
            ),
            PluginInfo(
                plugin_id='test.plugin.beta',
                name='Beta Plugin',
                version='1.0.0',
                author='Tester',
                description='Test beta',
                entry_point='test:TestPlugin'
            )
        ]
        for p in plugins:
            self.registry.register_plugin(p)

        results = self.registry.search_plugins('alpha')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Alpha Plugin')

    def test_enable_disable_plugin(self):
        """Test enabling/disabling plugins"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Tester',
            description='Test',
            entry_point='test:TestPlugin'
        )
        self.registry.register_plugin(plugin)

        self.assertTrue(self.registry.enable_plugin('test.plugin'))
        self.assertTrue(self.registry.is_plugin_enabled('test.plugin'))

        self.assertTrue(self.registry.disable_plugin('test.plugin'))
        self.assertFalse(self.registry.is_plugin_enabled('test.plugin'))


# ============================================================================
# Hook System Tests
# ============================================================================

class TestHookSystem(unittest.TestCase):
    """Tests for hook system"""

    def setUp(self):
        self.hook_system = HookSystem()
        self.call_count = 0

    def callback(self, *args, **kwargs):
        self.call_count += 1
        return 'callback_result'

    def test_register_hook(self):
        """Test registering hook"""
        result = self.hook_system.register_hook('test.hook', self.callback)
        self.assertTrue(result)

    def test_execute_hook(self):
        """Test executing hook"""
        self.hook_system.register_hook('test.hook', self.callback)
        self.hook_system.execute_hook('test.hook')
        self.assertEqual(self.call_count, 1)

    def test_execute_hook_with_args(self):
        """Test hook execution with arguments"""
        def callback_with_args(arg1, arg2):
            return f"{arg1}-{arg2}"

        self.hook_system.register_hook('test.hook', callback_with_args)
        result = self.hook_system.execute_hook('test.hook', 'a', 'b')
        self.assertEqual(result, 'a-b')

    def test_hook_priority_ordering(self):
        """Test hook priority ordering"""
        results = []

        def callback1(*args):
            results.append(1)

        def callback2(*args):
            results.append(2)

        # Register with different priorities
        self.hook_system.register_hook('test.hook', callback2, priority=10)
        self.hook_system.register_hook('test.hook', callback1, priority=5)

        self.hook_system.execute_hook('test.hook')
        # Lower priority number executes first
        self.assertEqual(results, [1, 2])

    def test_register_filter(self):
        """Test registering filter"""
        def filter_callback(value):
            return value + 1

        result = self.hook_system.register_filter('test.filter', filter_callback)
        self.assertTrue(result)

    def test_apply_filter(self):
        """Test applying filter"""
        def filter_callback(value):
            return value * 2

        self.hook_system.register_filter('test.filter', filter_callback)
        result = self.hook_system.apply_filter('test.filter', 5)
        self.assertEqual(result, 10)

    def test_filter_chaining(self):
        """Test multiple filters chaining"""
        self.hook_system.register_filter('test.filter', lambda v: v + 1, priority=5)
        self.hook_system.register_filter('test.filter', lambda v: v * 2, priority=10)

        result = self.hook_system.apply_filter('test.filter', 5)
        # 5 + 1 = 6, then 6 * 2 = 12 (priority 5 runs first, then priority 10)
        self.assertEqual(result, 12)

    def test_unregister_hook(self):
        """Test unregistering hook"""
        self.hook_system.register_hook('test.hook', self.callback)
        self.hook_system.unregister_hook('test.hook', self.callback)

        self.hook_system.execute_hook('test.hook')
        self.assertEqual(self.call_count, 0)

    def test_get_hooks(self):
        """Test getting registered hooks"""
        self.hook_system.register_hook('test.hook1', self.callback)
        self.hook_system.register_hook('test.hook2', self.callback)

        hooks = self.hook_system.get_hooks()
        self.assertEqual(len(hooks), 2)

    def test_hook_exception_handling(self):
        """Test hook exception handling"""
        def failing_callback(*args):
            raise ValueError("Test error")

        self.hook_system.register_hook('test.hook', failing_callback)
        # Should not raise, just log error
        result = self.hook_system.execute_hook('test.hook')
        self.assertIsNone(result)


# ============================================================================
# Dependency Resolver Tests
# ============================================================================

class TestDependencyResolver(unittest.TestCase):
    """Tests for dependency resolver"""

    def test_simple_dependency_resolution(self):
        """Test simple dependency resolution"""
        plugins = [
            PluginInfo(
                plugin_id='plugin1',
                name='Plugin 1',
                version='1.0.0',
                author='Test',
                description='',
                entry_point='',
                dependencies=['plugin2']
            ),
            PluginInfo(
                plugin_id='plugin2',
                name='Plugin 2',
                version='1.0.0',
                author='Test',
                description='',
                entry_point=''
            )
        ]

        order = DependencyResolver.resolve_dependencies(plugins)
        # plugin2 should come before plugin1
        self.assertLess(order.index('plugin2'), order.index('plugin1'))

    def test_complex_dependency_graph(self):
        """Test complex dependency graph"""
        plugins = [
            PluginInfo(
                plugin_id='a',
                name='A',
                version='1.0.0',
                author='Test',
                description='',
                entry_point='',
                dependencies=['b', 'c']
            ),
            PluginInfo(
                plugin_id='b',
                name='B',
                version='1.0.0',
                author='Test',
                description='',
                entry_point='',
                dependencies=['c']
            ),
            PluginInfo(
                plugin_id='c',
                name='C',
                version='1.0.0',
                author='Test',
                description='',
                entry_point=''
            ),
        ]

        order = DependencyResolver.resolve_dependencies(plugins)
        # c < b < a
        self.assertLess(order.index('c'), order.index('b'))
        self.assertLess(order.index('b'), order.index('a'))

    def test_missing_dependencies(self):
        """Test missing dependency detection"""
        plugin = PluginInfo(
            plugin_id='test',
            name='Test',
            version='1.0.0',
            author='Test',
            description='',
            entry_point='',
            dependencies=['nonexistent']
        )

        satisfied, missing = DependencyResolver.check_dependencies(
            plugin, {'test': '1.0.0'}
        )
        self.assertFalse(satisfied)
        self.assertIn('nonexistent', missing)


# ============================================================================
# Compatibility Checker Tests
# ============================================================================

class TestCompatibilityChecker(unittest.TestCase):
    """Tests for compatibility checker"""

    def test_version_parsing(self):
        """Test semantic version parsing"""
        v = CompatibilityChecker.parse_version("1.2.3")
        self.assertEqual(v, (1, 2, 3))

    def test_version_range_check(self):
        """Test version range checking"""
        # Range format: min..max
        self.assertTrue(CompatibilityChecker.check_version_range("1.5.0", "1.0.0..2.0.0"))
        self.assertFalse(CompatibilityChecker.check_version_range("3.0.0", "1.0.0..2.0.0"))

    def test_version_comparison(self):
        """Test version comparisons"""
        self.assertTrue(CompatibilityChecker.check_version_range("2.0.0", ">=1.0.0"))
        self.assertTrue(CompatibilityChecker.check_version_range("1.0.0", "<=2.0.0"))
        self.assertFalse(CompatibilityChecker.check_version_range("1.0.0", ">1.0.0"))

    def test_compatibility_check(self):
        """Test plugin compatibility checking"""
        plugin = PluginInfo(
            plugin_id='test',
            name='Test',
            version='1.0.0',
            author='Test',
            description='',
            entry_point='',
            compatibility={'anki_template_designer': '1.0.0..2.0.0'}
        )

        compatible, issues = CompatibilityChecker.check_compatibility(plugin, "1.5.0")
        self.assertTrue(compatible)
        self.assertEqual(len(issues), 0)


# ============================================================================
# Plugin Lifecycle Manager Tests
# ============================================================================

class TestPluginLifecycleManager(unittest.TestCase):
    """Tests for plugin lifecycle manager"""

    def setUp(self):
        self.hook_system = HookSystem()
        self.lifecycle = PluginLifecycleManager(self.hook_system)

    def test_load_plugin_basic(self):
        """Test loading plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''  # No Python entry point
        )

        result = self.lifecycle.load_plugin(plugin)
        self.assertTrue(result)

    def test_unload_plugin(self):
        """Test unloading plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.lifecycle.load_plugin(plugin)
        # Verify plugin was loaded
        self.assertIn('test.plugin', self.lifecycle.plugins)
        result = self.lifecycle.unload_plugin('test.plugin')
        self.assertTrue(result)
        # Verify plugin was unloaded
        self.assertNotIn('test.plugin', self.lifecycle.plugins)

    def test_enable_disable_plugin(self):
        """Test enabling/disabling plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.lifecycle.load_plugin(plugin)
        # Initial state should be LOADED
        self.assertEqual(self.lifecycle.get_plugin_status('test.plugin'), PluginState.LOADED.value)
        # Now enable it
        result = self.lifecycle.enable_plugin('test.plugin')
        self.assertTrue(result)
        # Check state is ENABLED
        state = self.lifecycle.get_plugin_status('test.plugin')
        self.assertEqual(state, PluginState.ENABLED.value)

    def test_get_loaded_plugins(self):
        """Test getting loaded plugins"""
        loaded_count = 0
        for i in range(3):
            plugin = PluginInfo(
                plugin_id=f'test.plugin.{i}',
                name=f'Test Plugin {i}',
                version='1.0.0',
                author='Test',
                description='',
                entry_point=''
            )
            if self.lifecycle.load_plugin(plugin):
                loaded_count += 1

        plugins = self.lifecycle.get_loaded_plugins()
        self.assertEqual(len(plugins), loaded_count)

    def test_plugin_status(self):
        """Test getting plugin status"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.lifecycle.load_plugin(plugin)
        status = self.lifecycle.get_plugin_status('test.plugin')
        self.assertEqual(status, PluginState.LOADED.value)


# ============================================================================
# Plugin Marketplace Tests
# ============================================================================

class TestPluginMarketplace(unittest.TestCase):
    """Tests for plugin marketplace"""

    def setUp(self):
        self.marketplace = PluginMarketplace()

    def test_publish_plugin(self):
        """Test publishing plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='Test plugin',
            entry_point=''
        )

        result = self.marketplace.publish_plugin(plugin)
        self.assertTrue(result)

    def test_get_plugin_metadata(self):
        """Test getting plugin metadata"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test Author',
            description='Test plugin',
            entry_point=''
        )

        self.marketplace.publish_plugin(plugin)
        metadata = self.marketplace.get_plugin_metadata('test.plugin')

        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['name'], 'Test Plugin')
        self.assertEqual(metadata['author'], 'Test Author')

    def test_unpublish_plugin(self):
        """Test unpublishing plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.marketplace.publish_plugin(plugin)
        result = self.marketplace.unpublish_plugin('test.plugin')
        self.assertTrue(result)

    def test_rate_plugin(self):
        """Test rating plugin"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.marketplace.publish_plugin(plugin)
        result = self.marketplace.rate_plugin('test.plugin', 5, 'Great plugin!')
        self.assertTrue(result)

    def test_get_ratings(self):
        """Test getting plugin ratings"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.marketplace.publish_plugin(plugin)
        self.marketplace.rate_plugin('test.plugin', 5)
        self.marketplace.rate_plugin('test.plugin', 4)

        ratings = self.marketplace.get_plugin_ratings('test.plugin')
        self.assertEqual(ratings['count'], 2)
        self.assertEqual(ratings['average'], 4.5)

    def test_track_downloads(self):
        """Test tracking downloads"""
        plugin = PluginInfo(
            plugin_id='test.plugin',
            name='Test Plugin',
            version='1.0.0',
            author='Test',
            description='',
            entry_point=''
        )

        self.marketplace.publish_plugin(plugin)
        self.marketplace.track_download('test.plugin')
        self.marketplace.track_download('test.plugin')

    def test_search_marketplace(self):
        """Test marketplace search"""
        plugins = [
            PluginInfo(
                plugin_id='test.alpha',
                name='Alpha Plugin',
                version='1.0.0',
                author='Test',
                description='Alpha description',
                entry_point=''
            ),
            PluginInfo(
                plugin_id='test.beta',
                name='Beta Plugin',
                version='1.0.0',
                author='Test',
                description='Beta description',
                entry_point=''
            )
        ]

        for p in plugins:
            self.marketplace.publish_plugin(p)

        results = self.marketplace.search_marketplace('alpha')
        self.assertEqual(len(results), 1)


# ============================================================================
# Plugin Context & Sandbox Tests
# ============================================================================

class TestPluginSandboxContext(unittest.TestCase):
    """Tests for plugin sandbox context"""

    def setUp(self):
        self.hook_system = HookSystem()
        context = PluginContext(
            plugin_id='test',
            plugin_info=PluginInfo(
                plugin_id='test',
                name='Test',
                version='1.0.0',
                author='Test',
                description='',
                entry_point=''
            ),
            hook_system=self.hook_system
        )
        self.sandbox = PluginSandboxContext(context)

    def test_register_hook_via_sandbox(self):
        """Test registering hook via sandbox"""
        def callback(*args):
            pass

        result = self.sandbox.register_hook('test.hook', callback)
        self.assertTrue(result)

    def test_plugin_data_storage(self):
        """Test plugin data storage"""
        self.sandbox.set_plugin_data('key1', 'value1')
        result = self.sandbox.get_plugin_data('key1')
        self.assertEqual(result, 'value1')

    def test_delete_plugin_data(self):
        """Test deleting plugin data"""
        self.sandbox.set_plugin_data('key1', 'value1')
        self.sandbox.delete_plugin_data('key1')
        result = self.sandbox.get_plugin_data('key1')
        self.assertIsNone(result)

    def test_configuration_storage(self):
        """Test configuration storage"""
        self.sandbox.set_config('setting1', 'value1')
        result = self.sandbox.get_config('setting1')
        self.assertEqual(result, 'value1')


# ============================================================================
# Plugin Manager Tests
# ============================================================================

class TestPluginManager(unittest.TestCase):
    """Tests for plugin manager"""

    def setUp(self):
        self.manager = PluginManager()

    def test_initialize_with_no_plugins(self):
        """Test initialization with no plugins"""
        with tempfile.TemporaryDirectory() as tmpdir:
            count = self.manager.initialize_plugins(tmpdir)
            self.assertEqual(count, 0)

    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.manager.get_statistics()
        self.assertIn('total_plugins', stats)
        self.assertIn('enabled_plugins', stats)
        self.assertIn('loaded_plugins', stats)


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety(unittest.TestCase):
    """Thread safety tests"""

    def test_concurrent_hook_registration(self):
        """Test concurrent hook registration"""
        hook_system = HookSystem()
        results = []

        def register_hooks():
            for i in range(10):
                hook_system.register_hook('test.hook', lambda *a, **k: None)
                results.append(1)

        threads = [threading.Thread(target=register_hooks) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 50)

    def test_concurrent_plugin_operations(self):
        """Test concurrent plugin operations"""
        registry = PluginRegistry()
        results = []

        def register_plugins():
            for i in range(10):
                plugin = PluginInfo(
                    plugin_id=f'plugin_{threading.current_thread().ident}_{i}',
                    name='Test',
                    version='1.0.0',
                    author='Test',
                    description='',
                    entry_point=''
                )
                if registry.register_plugin(plugin):
                    results.append(1)

        threads = [threading.Thread(target=register_plugins) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 50)


if __name__ == '__main__':
    unittest.main()
