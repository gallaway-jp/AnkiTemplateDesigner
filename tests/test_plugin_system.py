"""
Unit tests for Plugin System (Plan 16).

Tests for PluginRegistry, PluginLifecycleManager, HookSystem,
DependencyResolver, and CompatibilityChecker.
"""

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anki_template_designer.services.plugin_system import (
    Plugin,
    PluginInfo,
    PluginState,
    PluginContext,
    PluginRegistry,
    PluginLifecycleManager,
    HookSystem,
    DependencyResolver,
    CompatibilityChecker,
    PluginManager,
    HookRegistration,
    FilterRegistration,
    init_plugin_manager,
    get_plugin_manager
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def plugins_dir(temp_dir):
    """Create plugins directory."""
    path = Path(temp_dir) / "plugins"
    path.mkdir()
    return str(path)


@pytest.fixture
def data_dir(temp_dir):
    """Create data directory."""
    path = Path(temp_dir) / "data"
    path.mkdir()
    return str(path)


@pytest.fixture
def hook_system():
    """Create hook system."""
    return HookSystem()


@pytest.fixture
def registry(plugins_dir):
    """Create plugin registry."""
    return PluginRegistry(plugins_dir)


@pytest.fixture
def plugin_info():
    """Create sample plugin info."""
    return PluginInfo(
        plugin_id="test_plugin",
        name="Test Plugin",
        version="1.0.0",
        author="Test Author",
        description="A test plugin",
        entry_point="plugin:TestPlugin",
        dependencies=[],
        compatibility={"python": "3.8+"},
        enabled=False
    )


@pytest.fixture
def sample_manifest(plugins_dir):
    """Create sample plugin directory with manifest."""
    plugin_dir = Path(plugins_dir) / "sample_plugin"
    plugin_dir.mkdir()
    
    manifest = {
        "pluginId": "sample_plugin",
        "name": "Sample Plugin",
        "version": "1.0.0",
        "author": "Sample Author",
        "description": "A sample plugin for testing",
        "entryPoint": "plugin:SamplePlugin",
        "dependencies": [],
        "compatibility": {"python": "3.8+"}
    }
    
    (plugin_dir / "plugin.json").write_text(json.dumps(manifest))
    
    # Create plugin.py
    plugin_code = '''
from anki_template_designer.services.plugin_system import Plugin

class SamplePlugin(Plugin):
    def on_load(self):
        return True
    
    def on_enable(self):
        return True
    
    def on_disable(self):
        return True
    
    def on_unload(self):
        return True
'''
    (plugin_dir / "plugin.py").write_text(plugin_code)
    
    return str(plugin_dir)


# ============================================================================
# PluginInfo Tests
# ============================================================================

class TestPluginInfo:
    """Tests for PluginInfo dataclass."""
    
    def test_create_plugin_info(self):
        """Test creating PluginInfo."""
        info = PluginInfo(
            plugin_id="test",
            name="Test",
            version="1.0.0"
        )
        assert info.plugin_id == "test"
        assert info.name == "Test"
        assert info.version == "1.0.0"
        assert info.state == PluginState.NOT_LOADED
    
    def test_to_dict(self, plugin_info):
        """Test converting to dictionary."""
        result = plugin_info.to_dict()
        assert result["pluginId"] == "test_plugin"
        assert result["name"] == "Test Plugin"
        assert result["version"] == "1.0.0"
        assert result["state"] == "not_loaded"
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "pluginId": "from_dict",
            "name": "From Dict",
            "version": "2.0.0",
            "author": "Author",
            "state": "loaded"
        }
        info = PluginInfo.from_dict(data)
        assert info.plugin_id == "from_dict"
        assert info.name == "From Dict"
        assert info.state == PluginState.LOADED
    
    def test_from_dict_with_snake_case(self):
        """Test from_dict handles snake_case keys."""
        data = {
            "plugin_id": "snake_case",
            "name": "Snake Case",
            "version": "1.0.0",
            "entry_point": "mod:Class"
        }
        info = PluginInfo.from_dict(data)
        assert info.plugin_id == "snake_case"
        assert info.entry_point == "mod:Class"
    
    def test_from_manifest_json(self, plugins_dir):
        """Test loading from JSON manifest."""
        plugin_dir = Path(plugins_dir) / "json_plugin"
        plugin_dir.mkdir()
        
        manifest = {
            "pluginId": "json_plugin",
            "name": "JSON Plugin",
            "version": "1.0.0"
        }
        (plugin_dir / "plugin.json").write_text(json.dumps(manifest))
        
        info = PluginInfo.from_manifest(str(plugin_dir / "plugin.json"))
        assert info is not None
        assert info.plugin_id == "json_plugin"
        assert info.path == str(plugin_dir)
    
    def test_from_manifest_nonexistent(self, temp_dir):
        """Test loading from nonexistent manifest."""
        info = PluginInfo.from_manifest(str(Path(temp_dir) / "nonexistent.json"))
        assert info is None
    
    def test_default_values(self):
        """Test default values."""
        info = PluginInfo(
            plugin_id="minimal",
            name="Minimal",
            version="1.0.0"
        )
        assert info.author == ""
        assert info.description == ""
        assert info.dependencies == []
        assert info.compatibility == {}


# ============================================================================
# HookSystem Tests
# ============================================================================

class TestHookSystem:
    """Tests for HookSystem."""
    
    def test_register_hook(self, hook_system):
        """Test registering a hook."""
        callback = MagicMock()
        result = hook_system.register_hook("test_hook", callback)
        assert result is True
        assert len(hook_system._hooks.get("test_hook", [])) == 1
    
    def test_execute_hook(self, hook_system):
        """Test executing a hook."""
        callback = MagicMock(return_value="result")
        hook_system.register_hook("test_hook", callback)
        
        results = hook_system.execute_hook("test_hook", "arg1", key="value")
        
        callback.assert_called_once_with("arg1", key="value")
        assert results == ["result"]
    
    def test_hook_priority(self, hook_system):
        """Test hooks execute in priority order."""
        results = []
        
        hook_system.register_hook("ordered", lambda: results.append(3), priority=30)
        hook_system.register_hook("ordered", lambda: results.append(1), priority=10)
        hook_system.register_hook("ordered", lambda: results.append(2), priority=20)
        
        hook_system.execute_hook("ordered")
        assert results == [1, 2, 3]
    
    def test_unregister_hook(self, hook_system):
        """Test unregistering a hook."""
        callback = MagicMock()
        hook_system.register_hook("test", callback)
        
        result = hook_system.unregister_hook("test", callback)
        assert result is True
        assert len(hook_system._hooks.get("test", [])) == 0
    
    def test_unregister_hook_nonexistent(self, hook_system):
        """Test unregistering nonexistent hook."""
        result = hook_system.unregister_hook("nonexistent", lambda: None)
        assert result is False
    
    def test_unregister_plugin_hooks(self, hook_system):
        """Test unregistering all hooks for a plugin."""
        hook_system.register_hook("hook1", lambda: None, plugin_id="plugin1")
        hook_system.register_hook("hook2", lambda: None, plugin_id="plugin1")
        hook_system.register_hook("hook3", lambda: None, plugin_id="plugin2")
        
        removed = hook_system.unregister_plugin_hooks("plugin1")
        
        assert removed == 2
        assert len(hook_system._hooks.get("hook1", [])) == 0
        assert len(hook_system._hooks.get("hook3", [])) == 1
    
    def test_register_filter(self, hook_system):
        """Test registering a filter."""
        callback = lambda x: x.upper()
        result = hook_system.register_filter("test_filter", callback)
        assert result is True
    
    def test_apply_filter(self, hook_system):
        """Test applying a filter."""
        hook_system.register_filter("uppercase", lambda x: x.upper())
        
        result = hook_system.apply_filter("uppercase", "hello")
        assert result == "HELLO"
    
    def test_filter_chain(self, hook_system):
        """Test filter chaining."""
        hook_system.register_filter("chain", lambda x: x + "B", priority=20)
        hook_system.register_filter("chain", lambda x: x + "A", priority=10)
        hook_system.register_filter("chain", lambda x: x + "C", priority=30)
        
        result = hook_system.apply_filter("chain", "")
        assert result == "ABC"
    
    def test_unregister_filter(self, hook_system):
        """Test unregistering a filter."""
        callback = lambda x: x
        hook_system.register_filter("test", callback)
        
        result = hook_system.unregister_filter("test", callback)
        assert result is True
    
    def test_unregister_plugin_filters(self, hook_system):
        """Test unregistering all filters for a plugin."""
        hook_system.register_filter("f1", lambda x: x, plugin_id="plugin1")
        hook_system.register_filter("f2", lambda x: x, plugin_id="plugin2")
        
        removed = hook_system.unregister_plugin_filters("plugin1")
        assert removed == 1
    
    def test_get_hooks(self, hook_system):
        """Test getting registered hooks."""
        hook_system.register_hook("hook1", lambda: None, priority=5, plugin_id="p1")
        
        hooks = hook_system.get_hooks()
        assert len(hooks) == 1
        assert hooks[0]["hookName"] == "hook1"
        assert hooks[0]["priority"] == 5
        assert hooks[0]["pluginId"] == "p1"
    
    def test_get_filters(self, hook_system):
        """Test getting registered filters."""
        hook_system.register_filter("filter1", lambda x: x, plugin_id="p1")
        
        filters = hook_system.get_filters()
        assert len(filters) == 1
        assert filters[0]["filterName"] == "filter1"
    
    def test_clear(self, hook_system):
        """Test clearing all hooks and filters."""
        hook_system.register_hook("hook", lambda: None)
        hook_system.register_filter("filter", lambda x: x)
        
        hook_system.clear()
        
        assert len(hook_system._hooks) == 0
        assert len(hook_system._filters) == 0
    
    def test_hook_error_handling(self, hook_system):
        """Test hook error handling."""
        def failing_callback():
            raise ValueError("Error")
        
        hook_system.register_hook("failing", failing_callback)
        results = hook_system.execute_hook("failing")
        
        assert results == [None]  # Error returns None


# ============================================================================
# PluginContext Tests
# ============================================================================

class TestPluginContext:
    """Tests for PluginContext."""
    
    def test_create_context(self, hook_system, data_dir):
        """Test creating context."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        assert context.plugin_id == "test_plugin"
    
    def test_register_hook_through_context(self, hook_system, data_dir):
        """Test registering hook through context."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        callback = MagicMock()
        
        context.register_hook("test_hook", callback)
        
        # Verify hook is registered with plugin_id
        hooks = hook_system.get_hooks()
        assert len(hooks) == 1
        assert hooks[0]["pluginId"] == "test_plugin"
    
    def test_plugin_data_storage(self, hook_system, data_dir):
        """Test plugin data storage."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        
        # Set data
        result = context.set_plugin_data("key1", {"value": 42})
        assert result is True
        
        # Get data
        value = context.get_plugin_data("key1")
        assert value == {"value": 42}
    
    def test_plugin_data_delete(self, hook_system, data_dir):
        """Test deleting plugin data."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        context.set_plugin_data("to_delete", "value")
        
        result = context.delete_plugin_data("to_delete")
        assert result is True
        
        assert context.get_plugin_data("to_delete") is None
    
    def test_config_operations(self, hook_system, data_dir):
        """Test configuration operations."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        
        context.set_config("setting1", "value1")
        assert context.get_config("setting1") == "value1"
        assert context.get_config("nonexistent") is None
    
    def test_load_config(self, hook_system, data_dir):
        """Test loading configuration."""
        context = PluginContext("test_plugin", hook_system, data_dir)
        
        config = {"key1": "value1", "key2": "value2"}
        context.load_config(config)
        
        assert context.get_config("key1") == "value1"
        assert context.get_config("key2") == "value2"


# ============================================================================
# DependencyResolver Tests
# ============================================================================

class TestDependencyResolver:
    """Tests for DependencyResolver."""
    
    def test_no_dependencies(self):
        """Test resolving with no dependencies."""
        resolver = DependencyResolver()
        plugins = [
            PluginInfo("a", "A", "1.0.0"),
            PluginInfo("b", "B", "1.0.0"),
        ]
        
        order = resolver.resolve_dependencies(plugins)
        assert set(order) == {"a", "b"}
    
    def test_linear_dependencies(self):
        """Test linear dependency chain."""
        resolver = DependencyResolver()
        plugins = [
            PluginInfo("a", "A", "1.0.0", dependencies=["b"]),
            PluginInfo("b", "B", "1.0.0", dependencies=["c"]),
            PluginInfo("c", "C", "1.0.0"),
        ]
        
        order = resolver.resolve_dependencies(plugins)
        
        # c before b before a
        assert order.index("c") < order.index("b")
        assert order.index("b") < order.index("a")
    
    def test_detect_circular_dependencies(self):
        """Test detecting circular dependencies."""
        resolver = DependencyResolver()
        plugins = [
            PluginInfo("a", "A", "1.0.0", dependencies=["b"]),
            PluginInfo("b", "B", "1.0.0", dependencies=["c"]),
            PluginInfo("c", "C", "1.0.0", dependencies=["a"]),
        ]
        
        cycles = resolver.detect_circular_dependencies(plugins)
        assert len(cycles) > 0
    
    def test_check_dependencies_satisfied(self):
        """Test checking satisfied dependencies."""
        resolver = DependencyResolver()
        plugin = PluginInfo("a", "A", "1.0.0", dependencies=["b", "c"])
        available = {"b", "c", "d"}
        
        satisfied, missing = resolver.check_dependencies(plugin, available)
        
        assert satisfied is True
        assert missing == []
    
    def test_check_dependencies_missing(self):
        """Test checking missing dependencies."""
        resolver = DependencyResolver()
        plugin = PluginInfo("a", "A", "1.0.0", dependencies=["b", "missing"])
        available = {"b"}
        
        satisfied, missing = resolver.check_dependencies(plugin, available)
        
        assert satisfied is False
        assert "missing" in missing
    
    def test_validate_versions(self):
        """Test version validation."""
        resolver = DependencyResolver()
        plugin = PluginInfo("a", "A", "1.0.0", dependencies=["b >= 2.0.0"])
        
        valid, errors = resolver.validate_versions(plugin, {"b": "2.1.0"})
        assert valid is True
        
        valid, errors = resolver.validate_versions(plugin, {"b": "1.0.0"})
        assert valid is False
    
    def test_get_load_order(self):
        """Test getting load order."""
        resolver = DependencyResolver()
        plugins = [
            PluginInfo("a", "A", "1.0.0", dependencies=["b"]),
            PluginInfo("b", "B", "1.0.0"),
        ]
        
        order = resolver.get_load_order(plugins)
        assert order.index("b") < order.index("a")


# ============================================================================
# CompatibilityChecker Tests
# ============================================================================

class TestCompatibilityChecker:
    """Tests for CompatibilityChecker."""
    
    def test_check_compatibility_basic(self):
        """Test basic compatibility check."""
        checker = CompatibilityChecker()
        plugin = PluginInfo("test", "Test", "1.0.0")
        
        compatible, issues = checker.check_compatibility(plugin)
        assert compatible is True
        assert issues == []
    
    def test_check_python_version(self):
        """Test Python version checking."""
        checker = CompatibilityChecker()
        
        # Current Python version should satisfy 3.8+
        assert checker.check_python_version("3.8+") is True
        assert checker.check_python_version("3.6+") is True
        
        # Very high version should fail
        assert checker.check_python_version("99.0+") is False
    
    def test_check_api_compatibility(self):
        """Test API version compatibility."""
        checker = CompatibilityChecker()
        
        plugin = PluginInfo(
            "test", "Test", "1.0.0",
            compatibility={"api_version": ">= 1.0.0"}
        )
        
        assert checker.check_api_compatibility(plugin) is True
    
    def test_get_compatibility_info(self):
        """Test getting compatibility info."""
        checker = CompatibilityChecker()
        plugin = PluginInfo("test", "Test", "1.0.0")
        
        info = checker.get_compatibility_info(plugin)
        
        assert info["pluginId"] == "test"
        assert "compatible" in info
        assert "hostVersion" in info
        assert "apiVersion" in info
    
    def test_version_range_check(self):
        """Test version range checking."""
        checker = CompatibilityChecker()
        
        assert checker._check_version_range("1.5.0", "1.0.0..2.0.0") is True
        assert checker._check_version_range("0.5.0", "1.0.0..2.0.0") is False
        assert checker._check_version_range("2.5.0", "1.0.0..2.0.0") is False
    
    def test_version_comparison_operators(self):
        """Test version comparison operators."""
        checker = CompatibilityChecker()
        
        assert checker._check_version_range("2.0.0", ">= 1.0.0") is True
        assert checker._check_version_range("0.5.0", ">= 1.0.0") is False
        assert checker._check_version_range("1.0.0", "<= 2.0.0") is True
        assert checker._check_version_range("1.0.0", "> 0.5.0") is True
        assert checker._check_version_range("1.0.0", "< 2.0.0") is True


# ============================================================================
# PluginRegistry Tests
# ============================================================================

class TestPluginRegistry:
    """Tests for PluginRegistry."""
    
    def test_create_registry(self, plugins_dir):
        """Test creating registry."""
        registry = PluginRegistry(plugins_dir)
        assert registry._plugins_dir == Path(plugins_dir)
    
    def test_discover_plugins(self, registry, sample_manifest):
        """Test discovering plugins."""
        plugins = registry.discover_plugins()
        
        assert len(plugins) == 1
        assert plugins[0].plugin_id == "sample_plugin"
    
    def test_register_plugin(self, registry, plugin_info):
        """Test registering plugin."""
        result = registry.register_plugin(plugin_info)
        
        assert result is True
        assert registry.get_plugin("test_plugin") is not None
    
    def test_unregister_plugin(self, registry, plugin_info):
        """Test unregistering plugin."""
        registry.register_plugin(plugin_info)
        
        result = registry.unregister_plugin("test_plugin")
        
        assert result is True
        assert registry.get_plugin("test_plugin") is None
    
    def test_list_plugins(self, registry, plugin_info):
        """Test listing plugins."""
        registry.register_plugin(plugin_info)
        
        plugins = registry.list_plugins()
        
        assert len(plugins) == 1
        assert plugins[0].plugin_id == "test_plugin"
    
    def test_search_plugins(self, registry, plugin_info):
        """Test searching plugins."""
        registry.register_plugin(plugin_info)
        
        # Search by name
        results = registry.search_plugins("Test")
        assert len(results) == 1
        
        # Search by author
        results = registry.search_plugins("Author")
        assert len(results) == 1
        
        # No match
        results = registry.search_plugins("nonexistent")
        assert len(results) == 0
    
    def test_enable_disable_plugin(self, registry, plugin_info):
        """Test enabling and disabling plugin."""
        registry.register_plugin(plugin_info)
        
        result = registry.enable_plugin("test_plugin")
        assert result is True
        assert registry.is_plugin_enabled("test_plugin") is True
        
        result = registry.disable_plugin("test_plugin")
        assert result is True
        assert registry.is_plugin_enabled("test_plugin") is False


# ============================================================================
# PluginLifecycleManager Tests (Integration)
# ============================================================================

class TestPluginLifecycleManager:
    """Tests for PluginLifecycleManager."""
    
    def test_create_manager(self, registry, hook_system, data_dir):
        """Test creating lifecycle manager."""
        manager = PluginLifecycleManager(registry, hook_system, data_dir)
        assert manager._registry == registry
        assert manager._hook_system == hook_system
    
    def test_get_plugin_status(self, registry, hook_system, data_dir, plugin_info):
        """Test getting plugin status."""
        manager = PluginLifecycleManager(registry, hook_system, data_dir)
        registry.register_plugin(plugin_info)
        
        status = manager.get_plugin_status("test_plugin")
        assert status == "not_loaded"
    
    def test_get_loaded_plugins_empty(self, registry, hook_system, data_dir):
        """Test getting loaded plugins when empty."""
        manager = PluginLifecycleManager(registry, hook_system, data_dir)
        
        loaded = manager.get_loaded_plugins()
        assert loaded == []


# ============================================================================
# PluginManager Tests
# ============================================================================

class TestPluginManager:
    """Tests for PluginManager."""
    
    def test_create_manager(self, plugins_dir, data_dir):
        """Test creating plugin manager."""
        manager = PluginManager(plugins_dir, data_dir)
        
        assert manager.hook_system is not None
        assert manager.registry is not None
        assert manager.lifecycle is not None
    
    def test_list_plugins_empty(self, plugins_dir, data_dir):
        """Test listing plugins when empty."""
        manager = PluginManager(plugins_dir, data_dir)
        
        plugins = manager.list_plugins()
        assert plugins == []
    
    def test_get_plugin_info_nonexistent(self, plugins_dir, data_dir):
        """Test getting nonexistent plugin info."""
        manager = PluginManager(plugins_dir, data_dir)
        
        info = manager.get_plugin_info("nonexistent")
        assert info is None
    
    def test_get_hooks_empty(self, plugins_dir, data_dir):
        """Test getting hooks when empty."""
        manager = PluginManager(plugins_dir, data_dir)
        
        hooks = manager.get_hooks()
        assert hooks == []
    
    def test_get_filters_empty(self, plugins_dir, data_dir):
        """Test getting filters when empty."""
        manager = PluginManager(plugins_dir, data_dir)
        
        filters = manager.get_filters()
        assert filters == []
    
    def test_execute_hook_no_handlers(self, plugins_dir, data_dir):
        """Test executing hook with no handlers."""
        manager = PluginManager(plugins_dir, data_dir)
        
        results = manager.execute_hook("nonexistent_hook")
        assert results == []
    
    def test_apply_filter_no_filters(self, plugins_dir, data_dir):
        """Test applying filter with no filters."""
        manager = PluginManager(plugins_dir, data_dir)
        
        result = manager.apply_filter("nonexistent", "original")
        assert result == "original"


# ============================================================================
# Global Function Tests
# ============================================================================

class TestGlobalFunctions:
    """Tests for global initialization functions."""
    
    def test_init_and_get_plugin_manager(self, plugins_dir, data_dir):
        """Test initializing and getting plugin manager."""
        manager = init_plugin_manager(plugins_dir, data_dir)
        
        assert manager is not None
        
        retrieved = get_plugin_manager()
        assert retrieved is manager


# ============================================================================
# Hook Registration Tests
# ============================================================================

class TestHookRegistration:
    """Tests for HookRegistration dataclass."""
    
    def test_priority_comparison(self):
        """Test priority-based comparison."""
        hook1 = HookRegistration("hook", lambda: None, priority=10)
        hook2 = HookRegistration("hook", lambda: None, priority=20)
        
        assert hook1 < hook2
        assert not hook2 < hook1


class TestFilterRegistration:
    """Tests for FilterRegistration dataclass."""
    
    def test_priority_comparison(self):
        """Test priority-based comparison."""
        filter1 = FilterRegistration("filter", lambda x: x, priority=10)
        filter2 = FilterRegistration("filter", lambda x: x, priority=20)
        
        assert filter1 < filter2


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety:
    """Tests for thread safety."""
    
    def test_concurrent_hook_registration(self, hook_system):
        """Test concurrent hook registration."""
        errors = []
        
        def register_hooks(prefix):
            try:
                for i in range(10):
                    hook_system.register_hook(f"{prefix}_hook_{i}", lambda: None)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=register_hooks, args=(f"thread{i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_concurrent_hook_execution(self, hook_system):
        """Test concurrent hook execution."""
        results = []
        lock = threading.Lock()
        
        def callback():
            with lock:
                results.append(threading.current_thread().name)
        
        hook_system.register_hook("concurrent", callback)
        
        threads = [
            threading.Thread(target=lambda: hook_system.execute_hook("concurrent"))
            for _ in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 5


# ============================================================================
# Plugin Base Class Tests
# ============================================================================

class TestPlugin:
    """Tests for Plugin base class."""
    
    def test_default_lifecycle_methods(self, hook_system, data_dir):
        """Test default lifecycle methods return True."""
        context = PluginContext("test", hook_system, data_dir)
        plugin = Plugin(context)
        
        assert plugin.on_load() is True
        assert plugin.on_enable() is True
        assert plugin.on_disable() is True
        assert plugin.on_unload() is True
    
    def test_default_config_schema(self, hook_system, data_dir):
        """Test default config schema is empty."""
        context = PluginContext("test", hook_system, data_dir)
        plugin = Plugin(context)
        
        assert plugin.get_config_schema() == {}
    
    def test_register_hooks_noop(self, hook_system, data_dir):
        """Test default register_hooks does nothing."""
        context = PluginContext("test", hook_system, data_dir)
        plugin = Plugin(context)
        
        # Should not raise
        plugin.register_hooks()
