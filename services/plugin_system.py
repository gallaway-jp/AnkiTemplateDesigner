"""
Plugin System - Issue #58

Comprehensive plugin architecture enabling third-party extensions with:
- Plugin discovery and lifecycle management
- Hook and filter system for extensibility
- Dependency resolution and version checking
- Sandboxed plugin execution context
- Plugin marketplace integration
"""

import os
import json
import importlib
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Tuple, Any
from collections import defaultdict, deque
from enum import Enum
import hashlib


# ============================================================================
# Data Models
# ============================================================================

class PluginState(Enum):
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNLOADING = "unloading"
    ERROR = "error"


@dataclass
class PluginInfo:
    """Plugin metadata"""
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    compatibility: Dict[str, str] = field(default_factory=dict)
    enabled: bool = False
    path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)


@dataclass
class Hook:
    """Hook registration"""
    hook_name: str
    callback: Callable
    priority: int = 10
    plugin_id: str = ""


@dataclass
class Filter:
    """Filter registration"""
    filter_name: str
    callback: Callable
    priority: int = 10
    plugin_id: str = ""


@dataclass
class PluginContext:
    """Execution context for plugins"""
    plugin_id: str
    plugin_info: PluginInfo
    data_store: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    logger: Optional[logging.Logger] = None
    hook_system: Optional['HookSystem'] = None


# ============================================================================
# Plugin Registry
# ============================================================================

class PluginRegistry:
    """Manages plugin discovery and registration"""

    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.enabled_plugins: set = set()
        self._lock = threading.RLock()

    def discover_plugins(self, path: str) -> List[Dict]:
        """Discover plugins in directory"""
        plugins = []
        if not os.path.exists(path):
            return plugins

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if not os.path.isdir(item_path):
                continue

            manifest_path = os.path.join(item_path, 'plugin.json')
            if not os.path.exists(manifest_path):
                continue

            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    manifest['path'] = item_path
                    plugins.append(manifest)
            except (json.JSONDecodeError, IOError):
                continue

        return plugins

    def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """Register a plugin"""
        with self._lock:
            if plugin_info.plugin_id in self.plugins:
                return False
            self.plugins[plugin_info.plugin_id] = plugin_info
            return True

    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin"""
        with self._lock:
            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
                self.enabled_plugins.discard(plugin_id)
                return True
            return False

    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin info"""
        with self._lock:
            return self.plugins.get(plugin_id)

    def list_plugins(self) -> List[PluginInfo]:
        """List all plugins"""
        with self._lock:
            return list(self.plugins.values())

    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search plugins by name/description"""
        query_lower = query.lower()
        with self._lock:
            return [
                p for p in self.plugins.values()
                if query_lower in p.name.lower()
                or query_lower in p.description.lower()
            ]

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        with self._lock:
            if plugin_id in self.plugins:
                self.enabled_plugins.add(plugin_id)
                self.plugins[plugin_id].enabled = True
                return True
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        with self._lock:
            if plugin_id in self.plugins:
                self.enabled_plugins.discard(plugin_id)
                self.plugins[plugin_id].enabled = False
                return True
            return False

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """Check if plugin is enabled"""
        with self._lock:
            return plugin_id in self.enabled_plugins


# ============================================================================
# Hook System
# ============================================================================

class HookSystem:
    """Manages hooks and filters for plugin extensibility"""

    def __init__(self):
        self.hooks: Dict[str, List[Hook]] = defaultdict(list)
        self.filters: Dict[str, List[Filter]] = defaultdict(list)
        self._lock = threading.RLock()
        self.hook_stats: Dict[str, Dict] = {}

    def register_hook(self, hook_name: str, callback: Callable,
                     priority: int = 10, plugin_id: str = "") -> bool:
        """Register a hook callback"""
        with self._lock:
            hook = Hook(hook_name, callback, priority, plugin_id)
            self.hooks[hook_name].append(hook)
            # Sort by priority (lower = higher priority)
            self.hooks[hook_name].sort(key=lambda h: h.priority)
            return True

    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """Unregister a hook"""
        with self._lock:
            if hook_name in self.hooks:
                self.hooks[hook_name] = [
                    h for h in self.hooks[hook_name]
                    if h.callback != callback
                ]
                return True
            return False

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Execute all hooks for an event"""
        with self._lock:
            if hook_name not in self.hooks:
                return None

            hooks_list = list(self.hooks[hook_name])

        result = None
        for hook in hooks_list:
            try:
                result = hook.callback(*args, **kwargs)
            except Exception as e:
                logging.error(f"Hook {hook.plugin_id}.{hook_name} failed: {e}")

        return result

    def register_filter(self, filter_name: str, callback: Callable,
                       priority: int = 10, plugin_id: str = "") -> bool:
        """Register a filter callback"""
        with self._lock:
            filter_obj = Filter(filter_name, callback, priority, plugin_id)
            self.filters[filter_name].append(filter_obj)
            self.filters[filter_name].sort(key=lambda f: f.priority)
            return True

    def unregister_filter(self, filter_name: str, callback: Callable) -> bool:
        """Unregister a filter"""
        with self._lock:
            if filter_name in self.filters:
                self.filters[filter_name] = [
                    f for f in self.filters[filter_name]
                    if f.callback != callback
                ]
                return True
            return False

    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Apply all filters to a value"""
        with self._lock:
            filters_list = list(self.filters.get(filter_name, []))

        result = value
        for filter_obj in filters_list:
            try:
                result = filter_obj.callback(result, *args, **kwargs)
            except Exception as e:
                logging.error(f"Filter {filter_obj.plugin_id}.{filter_name} failed: {e}")

        return result

    def get_hooks(self, pattern: str = None) -> List[Dict]:
        """Get registered hooks"""
        with self._lock:
            hooks_list = []
            for name, hooks in self.hooks.items():
                if pattern and pattern not in name:
                    continue
                for hook in hooks:
                    hooks_list.append({
                        'name': name,
                        'plugin': hook.plugin_id,
                        'priority': hook.priority
                    })
            return hooks_list

    def get_filters(self, pattern: str = None) -> List[Dict]:
        """Get registered filters"""
        with self._lock:
            filters_list = []
            for name, filters in self.filters.items():
                if pattern and pattern not in name:
                    continue
                for filter_obj in filters:
                    filters_list.append({
                        'name': name,
                        'plugin': filter_obj.plugin_id,
                        'priority': filter_obj.priority
                    })
            return filters_list


# ============================================================================
# Dependency Resolver
# ============================================================================

class DependencyResolver:
    """Resolves plugin dependencies and load order"""

    @staticmethod
    def resolve_dependencies(plugins: List[PluginInfo]) -> List[str]:
        """Get load order based on dependencies"""
        # Build dependency graph
        graph = {}
        plugin_map = {p.plugin_id: p for p in plugins}

        for plugin in plugins:
            graph[plugin.plugin_id] = []
            for dep in plugin.dependencies:
                dep_id = dep.split()[0] if ' ' in dep else dep
                if dep_id in plugin_map:
                    graph[plugin.plugin_id].append(dep_id)

        # Topological sort
        visited = set()
        order = []

        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            order.append(node)

        for plugin_id in graph:
            visit(plugin_id)

        return order

    @staticmethod
    def check_dependencies(plugin: PluginInfo, installed: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Check if all dependencies are satisfied"""
        missing = []
        for dep in plugin.dependencies:
            dep_id = dep.split()[0] if ' ' in dep else dep
            if dep_id not in installed:
                missing.append(dep_id)
        return len(missing) == 0, missing

    @staticmethod
    def detect_circular_dependencies(plugins: List[PluginInfo]) -> List[List[str]]:
        """Detect circular dependencies"""
        graph = {}
        for plugin in plugins:
            graph[plugin.plugin_id] = set()
            for dep in plugin.dependencies:
                dep_id = dep.split()[0] if ' ' in dep else dep
                graph[plugin.plugin_id].add(dep_id)

        cycles = []
        visited = set()
        rec_stack = set()

        def visit(node: str, path: List[str]):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                visit(neighbor, path + [node])
            rec_stack.remove(node)

        for plugin_id in graph:
            if plugin_id not in visited:
                visit(plugin_id, [])

        return cycles


# ============================================================================
# Compatibility Checker
# ============================================================================

class CompatibilityChecker:
    """Checks version compatibility"""

    @staticmethod
    def parse_version(version_str: str) -> Tuple[int, int, int]:
        """Parse semantic version"""
        parts = version_str.strip().split('.')
        return (
            int(parts[0]) if len(parts) > 0 else 0,
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0,
        )

    @staticmethod
    def check_version_range(version: str, requirement: str) -> bool:
        """Check if version satisfies requirement"""
        v = CompatibilityChecker.parse_version(version)

        if '..' in requirement:
            min_v, max_v = requirement.split('..')
            min_parsed = CompatibilityChecker.parse_version(min_v)
            max_parsed = CompatibilityChecker.parse_version(max_v)
            return min_parsed <= v <= max_parsed

        if requirement.startswith('>='):
            req_v = CompatibilityChecker.parse_version(requirement[2:])
            return v >= req_v

        if requirement.startswith('>'):
            req_v = CompatibilityChecker.parse_version(requirement[1:])
            return v > req_v

        if requirement.startswith('<='):
            req_v = CompatibilityChecker.parse_version(requirement[2:])
            return v <= req_v

        if requirement.startswith('<'):
            req_v = CompatibilityChecker.parse_version(requirement[1:])
            return v < req_v

        if requirement.startswith('=='):
            req_v = CompatibilityChecker.parse_version(requirement[2:])
            return v == req_v

        return True

    @staticmethod
    def check_compatibility(plugin: PluginInfo, host_version: str = "1.0.0") -> Tuple[bool, List[str]]:
        """Check if plugin is compatible"""
        issues = []

        if 'anki_template_designer' in plugin.compatibility:
            req = plugin.compatibility['anki_template_designer']
            if not CompatibilityChecker.check_version_range(host_version, req):
                issues.append(f"Incompatible with host version {host_version}")

        return len(issues) == 0, issues


# ============================================================================
# Plugin Lifecycle Manager
# ============================================================================

class PluginLifecycleManager:
    """Manages plugin loading and lifecycle"""

    def __init__(self, hook_system: HookSystem):
        self.plugins: Dict[str, Any] = {}
        self.plugin_states: Dict[str, PluginState] = {}
        self.plugin_contexts: Dict[str, PluginContext] = {}
        self.hook_system = hook_system
        self._lock = threading.RLock()

    def load_plugin(self, plugin_info: PluginInfo) -> bool:
        """Load a plugin"""
        with self._lock:
            if plugin_info.plugin_id in self.plugins:
                return False

            try:
                self.plugin_states[plugin_info.plugin_id] = PluginState.LOADING

                # Create context
                context = PluginContext(
                    plugin_id=plugin_info.plugin_id,
                    plugin_info=plugin_info,
                    hook_system=self.hook_system
                )
                self.plugin_contexts[plugin_info.plugin_id] = context

                # Try to load plugin class
                instance = None
                if plugin_info.entry_point:
                    try:
                        module_name, class_name = plugin_info.entry_point.rsplit(':', 1)
                        module = importlib.import_module(module_name)
                        plugin_class = getattr(module, class_name)
                        instance = plugin_class(context)
                        
                        # Call lifecycle method
                        if hasattr(instance, 'on_load'):
                            if not instance.on_load():
                                self.plugin_states[plugin_info.plugin_id] = PluginState.ERROR
                                return False
                    except (ImportError, AttributeError):
                        # Plugin doesn't have Python entry point
                        pass

                # Store the instance (even if None)
                self.plugins[plugin_info.plugin_id] = instance

                self.plugin_states[plugin_info.plugin_id] = PluginState.LOADED
                return True

            except Exception as e:
                logging.error(f"Failed to load plugin {plugin_info.plugin_id}: {e}")
                self.plugin_states[plugin_info.plugin_id] = PluginState.ERROR
                return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        with self._lock:
            if plugin_id not in self.plugins:
                return False

            try:
                self.plugin_states[plugin_id] = PluginState.UNLOADING
                
                instance = self.plugins[plugin_id]
                if instance and hasattr(instance, 'on_unload'):
                    instance.on_unload()

                del self.plugins[plugin_id]
                del self.plugin_states[plugin_id]
                del self.plugin_contexts[plugin_id]
                return True

            except Exception as e:
                logging.error(f"Failed to unload plugin {plugin_id}: {e}")
                return False

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a loaded plugin"""
        with self._lock:
            if plugin_id not in self.plugins:
                return False

            try:
                instance = self.plugins[plugin_id]
                if instance and hasattr(instance, 'on_enable'):
                    if not instance.on_enable():
                        return False

                self.plugin_states[plugin_id] = PluginState.ENABLED
                return True

            except Exception as e:
                logging.error(f"Failed to enable plugin {plugin_id}: {e}")
                return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        with self._lock:
            if plugin_id not in self.plugins:
                return False

            try:
                instance = self.plugins[plugin_id]
                if instance and hasattr(instance, 'on_disable'):
                    if not instance.on_disable():
                        return False

                self.plugin_states[plugin_id] = PluginState.DISABLED
                return True

            except Exception as e:
                logging.error(f"Failed to disable plugin {plugin_id}: {e}")
                return False

    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        """Get plugin instance"""
        with self._lock:
            return self.plugins.get(plugin_id)

    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugins"""
        with self._lock:
            return list(self.plugins.keys())

    def get_plugin_status(self, plugin_id: str) -> str:
        """Get plugin state"""
        with self._lock:
            return self.plugin_states.get(plugin_id, PluginState.NOT_LOADED).value


# ============================================================================
# Plugin Marketplace
# ============================================================================

class PluginMarketplace:
    """Plugin registry and marketplace"""

    def __init__(self):
        self.published: Dict[str, Dict] = {}
        self.ratings: Dict[str, List[Dict]] = defaultdict(list)
        self.downloads: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()

    def publish_plugin(self, plugin_info: PluginInfo) -> bool:
        """Publish a plugin"""
        with self._lock:
            self.published[plugin_info.plugin_id] = {
                'name': plugin_info.name,
                'version': plugin_info.version,
                'author': plugin_info.author,
                'description': plugin_info.description,
                'published_at': time.time(),
                'versions': [plugin_info.version]
            }
            return True

    def unpublish_plugin(self, plugin_id: str) -> bool:
        """Unpublish a plugin"""
        with self._lock:
            if plugin_id in self.published:
                del self.published[plugin_id]
                return True
            return False

    def get_plugin_metadata(self, plugin_id: str) -> Optional[Dict]:
        """Get published plugin metadata"""
        with self._lock:
            return self.published.get(plugin_id)

    def search_marketplace(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search marketplace"""
        query_lower = query.lower()
        with self._lock:
            results = []
            for pid, info in self.published.items():
                if query_lower in info['name'].lower() or query_lower in info['description'].lower():
                    results.append({**info, 'plugin_id': pid})
            return results

    def rate_plugin(self, plugin_id: str, rating: int, review: str = "") -> bool:
        """Rate a plugin"""
        with self._lock:
            if plugin_id not in self.published:
                return False
            
            self.ratings[plugin_id].append({
                'rating': max(1, min(5, rating)),
                'review': review,
                'timestamp': time.time()
            })
            return True

    def get_plugin_ratings(self, plugin_id: str) -> Dict:
        """Get plugin ratings summary"""
        with self._lock:
            if plugin_id not in self.ratings or len(self.ratings[plugin_id]) == 0:
                return {'average': 0, 'count': 0, 'distribution': {}}

            ratings_list = self.ratings[plugin_id]
            avg = sum(r['rating'] for r in ratings_list) / len(ratings_list)
            
            distribution = defaultdict(int)
            for r in ratings_list:
                distribution[r['rating']] += 1

            return {
                'average': round(avg, 1),
                'count': len(ratings_list),
                'distribution': dict(distribution)
            }

    def track_download(self, plugin_id: str) -> bool:
        """Track plugin download"""
        with self._lock:
            if plugin_id in self.published:
                self.downloads[plugin_id] += 1
                return True
            return False

    def get_featured_plugins(self, limit: int = 10) -> List[Dict]:
        """Get featured plugins (by downloads)"""
        with self._lock:
            sorted_plugins = sorted(
                self.published.items(),
                key=lambda x: self.downloads.get(x[0], 0),
                reverse=True
            )
            return [
                {**info, 'plugin_id': pid}
                for pid, info in sorted_plugins[:limit]
            ]


# ============================================================================
# Plugin Sandbox Context API
# ============================================================================

class PluginSandboxContext:
    """Sandboxed execution environment for plugins"""

    def __init__(self, context: PluginContext, templates_storage: Dict = None):
        self.context = context
        self.templates = templates_storage or {}
        self._lock = threading.RLock()

    # Hook/Filter API
    def register_hook(self, hook_name: str, callback: Callable, priority: int = 10) -> bool:
        """Register a hook"""
        if self.context.hook_system:
            return self.context.hook_system.register_hook(
                hook_name, callback, priority, self.context.plugin_id
            )
        return False

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Execute a hook"""
        if self.context.hook_system:
            return self.context.hook_system.execute_hook(hook_name, *args, **kwargs)
        return None

    def register_filter(self, filter_name: str, callback: Callable, priority: int = 10) -> bool:
        """Register a filter"""
        if self.context.hook_system:
            return self.context.hook_system.register_filter(
                filter_name, callback, priority, self.context.plugin_id
            )
        return False

    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Apply a filter"""
        if self.context.hook_system:
            return self.context.hook_system.apply_filter(filter_name, value, *args, **kwargs)
        return value

    # Template API
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get template"""
        with self._lock:
            return self.templates.get(template_id)

    def save_template(self, template: Dict) -> bool:
        """Save template"""
        with self._lock:
            if 'id' in template:
                self.templates[template['id']] = template
                return True
            return False

    def list_templates(self) -> List[Dict]:
        """List all templates"""
        with self._lock:
            return list(self.templates.values())

    # Data Storage API
    def get_plugin_data(self, key: str) -> Optional[Any]:
        """Get plugin data"""
        with self._lock:
            return self.context.data_store.get(key)

    def set_plugin_data(self, key: str, value: Any) -> bool:
        """Set plugin data"""
        with self._lock:
            self.context.data_store[key] = value
            return True

    def delete_plugin_data(self, key: str) -> bool:
        """Delete plugin data"""
        with self._lock:
            if key in self.context.data_store:
                del self.context.data_store[key]
                return True
            return False

    # Configuration API
    def get_config(self, key: str) -> Optional[Any]:
        """Get configuration"""
        with self._lock:
            return self.context.config.get(key)

    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration"""
        with self._lock:
            self.context.config[key] = value
            return True


# ============================================================================
# Plugin Manager (Orchestrator)
# ============================================================================

class PluginManager:
    """Main plugin management orchestrator"""

    def __init__(self):
        self.registry = PluginRegistry()
        self.hook_system = HookSystem()
        self.lifecycle = PluginLifecycleManager(self.hook_system)
        self.marketplace = PluginMarketplace()
        self.sandbox_contexts: Dict[str, PluginSandboxContext] = {}
        self._lock = threading.RLock()
        self.plugin_stats = {
            'loaded': deque(maxlen=100),
            'enabled': deque(maxlen=100),
            'errors': deque(maxlen=100)
        }

    def initialize_plugins(self, plugin_dir: str) -> int:
        """Discover and initialize plugins"""
        discovered = self.registry.discover_plugins(plugin_dir)
        count = 0

        for manifest in discovered:
            plugin_info = PluginInfo(**manifest)
            if self.registry.register_plugin(plugin_info):
                count += 1

        return count

    def load_all_enabled_plugins(self) -> int:
        """Load all enabled plugins"""
        loaded_count = 0
        plugins = self.registry.list_plugins()

        # Resolve dependencies
        load_order = DependencyResolver.resolve_dependencies(plugins)

        for plugin_id in load_order:
            plugin_info = self.registry.get_plugin(plugin_id)
            if plugin_info and plugin_info.enabled:
                if self.lifecycle.load_plugin(plugin_info):
                    loaded_count += 1
                    self.plugin_stats['loaded'].append({'id': plugin_id, 'time': time.time()})
                    
                    # Create sandbox context
                    context = self.lifecycle.plugin_contexts.get(plugin_id)
                    if context:
                        self.sandbox_contexts[plugin_id] = PluginSandboxContext(context)

        return loaded_count

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        self.registry.enable_plugin(plugin_id)
        if self.lifecycle.enable_plugin(plugin_id):
            self.plugin_stats['enabled'].append({'id': plugin_id, 'time': time.time()})
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        return self.lifecycle.disable_plugin(plugin_id)

    def get_statistics(self) -> Dict:
        """Get plugin system statistics"""
        with self._lock:
            return {
                'total_plugins': len(self.registry.plugins),
                'enabled_plugins': len(self.registry.enabled_plugins),
                'loaded_plugins': len(self.lifecycle.plugins),
                'recent_loads': list(self.plugin_stats['loaded']),
                'recent_enables': list(self.plugin_stats['enabled']),
                'recent_errors': list(self.plugin_stats['errors'])
            }
