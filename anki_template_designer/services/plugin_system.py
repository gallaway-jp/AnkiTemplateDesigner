"""
Plugin System for Anki Template Designer.

Plan 16: Extensible plugin architecture with hooks, filters,
lifecycle management, and dependency resolution.
"""

import importlib
import importlib.util
import json
import logging
import os
import re
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger("anki_template_designer.services.plugin_system")


class PluginState(Enum):
    """Plugin lifecycle states."""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNLOADING = "unloading"
    ERROR = "error"


@dataclass
class PluginInfo:
    """Plugin metadata and configuration."""
    plugin_id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    entry_point: str = ""
    dependencies: List[str] = field(default_factory=list)
    compatibility: Dict[str, str] = field(default_factory=dict)
    enabled: bool = False
    path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    state: PluginState = PluginState.NOT_LOADED
    config_schema: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pluginId": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "entryPoint": self.entry_point,
            "dependencies": self.dependencies,
            "compatibility": self.compatibility,
            "enabled": self.enabled,
            "path": self.path,
            "metadata": self.metadata,
            "state": self.state.value,
            "configSchema": self.config_schema,
            "capabilities": self.capabilities
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginInfo":
        """Create from dictionary."""
        state_str = data.get("state", "not_loaded")
        try:
            state = PluginState(state_str)
        except ValueError:
            state = PluginState.NOT_LOADED
        
        return cls(
            plugin_id=data.get("pluginId", data.get("plugin_id", "")),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            description=data.get("description", ""),
            entry_point=data.get("entryPoint", data.get("entry_point", "")),
            dependencies=data.get("dependencies", []),
            compatibility=data.get("compatibility", {}),
            enabled=data.get("enabled", False),
            path=data.get("path", ""),
            metadata=data.get("metadata", {}),
            state=state,
            config_schema=data.get("configSchema", data.get("config_schema", {})),
            capabilities=data.get("capabilities", [])
        )
    
    @classmethod
    def from_manifest(cls, manifest_path: str) -> Optional["PluginInfo"]:
        """Create from manifest file."""
        try:
            path = Path(manifest_path)
            if not path.exists():
                return None
            
            content = path.read_text(encoding="utf-8")
            
            if path.suffix == ".json":
                data = json.loads(content)
            else:
                # Simple YAML-like parsing for .yaml files
                data = cls._parse_simple_yaml(content)
            
            info = cls.from_dict(data)
            info.path = str(path.parent)
            return info
            
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            return None
    
    @staticmethod
    def _parse_simple_yaml(content: str) -> Dict[str, Any]:
        """Simple YAML-like parser for basic key: value pairs."""
        result = {}
        current_key = None
        current_list = None
        
        for line in content.split("\n"):
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            
            # Handle list items
            if line.startswith("  - "):
                if current_list is not None:
                    current_list.append(line[4:].strip().strip('"\''))
                continue
            
            # Handle key: value
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"\'')
                
                # Check if starting a list
                if not value:
                    result[key] = []
                    current_list = result[key]
                    current_key = key
                else:
                    result[key] = value
                    current_list = None
        
        return result


@dataclass
class HookRegistration:
    """A registered hook callback."""
    hook_name: str
    callback: Callable
    priority: int = 10
    plugin_id: Optional[str] = None
    
    def __lt__(self, other: "HookRegistration") -> bool:
        """Compare by priority for sorting."""
        return self.priority < other.priority


@dataclass
class FilterRegistration:
    """A registered filter callback."""
    filter_name: str
    callback: Callable
    priority: int = 10
    plugin_id: Optional[str] = None
    
    def __lt__(self, other: "FilterRegistration") -> bool:
        """Compare by priority for sorting."""
        return self.priority < other.priority


class HookSystem:
    """Manages hooks and filters for plugin extensibility."""
    
    def __init__(self):
        """Initialize hook system."""
        self._hooks: Dict[str, List[HookRegistration]] = {}
        self._filters: Dict[str, List[FilterRegistration]] = {}
        self._lock = threading.RLock()
    
    def register_hook(self, hook_name: str, callback: Callable,
                     priority: int = 10, plugin_id: Optional[str] = None) -> bool:
        """Register a hook callback.
        
        Args:
            hook_name: Name of hook to register for.
            callback: Function to call when hook fires.
            priority: Execution order (lower = earlier).
            plugin_id: Optional ID of registering plugin.
            
        Returns:
            True if registered successfully.
        """
        with self._lock:
            if hook_name not in self._hooks:
                self._hooks[hook_name] = []
            
            registration = HookRegistration(
                hook_name=hook_name,
                callback=callback,
                priority=priority,
                plugin_id=plugin_id
            )
            
            self._hooks[hook_name].append(registration)
            self._hooks[hook_name].sort()  # Sort by priority
            
            logger.debug(f"Hook registered: {hook_name} (priority={priority})")
            return True
    
    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """Unregister a hook callback.
        
        Args:
            hook_name: Name of hook.
            callback: Callback to remove.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if hook_name not in self._hooks:
                return False
            
            original_count = len(self._hooks[hook_name])
            self._hooks[hook_name] = [
                h for h in self._hooks[hook_name]
                if h.callback != callback
            ]
            
            return len(self._hooks[hook_name]) < original_count
    
    def unregister_plugin_hooks(self, plugin_id: str) -> int:
        """Unregister all hooks for a plugin.
        
        Args:
            plugin_id: Plugin ID.
            
        Returns:
            Number of hooks removed.
        """
        with self._lock:
            removed = 0
            for hook_name in list(self._hooks.keys()):
                original = len(self._hooks[hook_name])
                self._hooks[hook_name] = [
                    h for h in self._hooks[hook_name]
                    if h.plugin_id != plugin_id
                ]
                removed += original - len(self._hooks[hook_name])
            return removed
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all callbacks for a hook.
        
        Args:
            hook_name: Hook to execute.
            *args: Positional arguments for callbacks.
            **kwargs: Keyword arguments for callbacks.
            
        Returns:
            List of return values from callbacks.
        """
        with self._lock:
            hooks = self._hooks.get(hook_name, []).copy()
        
        results = []
        for hook in hooks:
            try:
                result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_name} error ({hook.plugin_id}): {e}")
                results.append(None)
        
        return results
    
    def register_filter(self, filter_name: str, callback: Callable,
                       priority: int = 10, plugin_id: Optional[str] = None) -> bool:
        """Register a filter callback.
        
        Args:
            filter_name: Name of filter.
            callback: Function to transform value.
            priority: Execution order (lower = earlier).
            plugin_id: Optional ID of registering plugin.
            
        Returns:
            True if registered.
        """
        with self._lock:
            if filter_name not in self._filters:
                self._filters[filter_name] = []
            
            registration = FilterRegistration(
                filter_name=filter_name,
                callback=callback,
                priority=priority,
                plugin_id=plugin_id
            )
            
            self._filters[filter_name].append(registration)
            self._filters[filter_name].sort()
            
            logger.debug(f"Filter registered: {filter_name} (priority={priority})")
            return True
    
    def unregister_filter(self, filter_name: str, callback: Callable) -> bool:
        """Unregister a filter callback.
        
        Args:
            filter_name: Name of filter.
            callback: Callback to remove.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if filter_name not in self._filters:
                return False
            
            original_count = len(self._filters[filter_name])
            self._filters[filter_name] = [
                f for f in self._filters[filter_name]
                if f.callback != callback
            ]
            
            return len(self._filters[filter_name]) < original_count
    
    def unregister_plugin_filters(self, plugin_id: str) -> int:
        """Unregister all filters for a plugin.
        
        Args:
            plugin_id: Plugin ID.
            
        Returns:
            Number of filters removed.
        """
        with self._lock:
            removed = 0
            for filter_name in list(self._filters.keys()):
                original = len(self._filters[filter_name])
                self._filters[filter_name] = [
                    f for f in self._filters[filter_name]
                    if f.plugin_id != plugin_id
                ]
                removed += original - len(self._filters[filter_name])
            return removed
    
    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Apply all filters to a value.
        
        Args:
            filter_name: Filter to apply.
            value: Initial value to transform.
            *args: Additional arguments for filters.
            **kwargs: Keyword arguments for filters.
            
        Returns:
            Transformed value after all filters.
        """
        with self._lock:
            filters = self._filters.get(filter_name, []).copy()
        
        result = value
        for flt in filters:
            try:
                result = flt.callback(result, *args, **kwargs)
            except Exception as e:
                logger.error(f"Filter {filter_name} error ({flt.plugin_id}): {e}")
        
        return result
    
    def get_hooks(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get registered hooks.
        
        Args:
            pattern: Optional filter pattern.
            
        Returns:
            List of hook info dictionaries.
        """
        with self._lock:
            result = []
            for hook_name, hooks in self._hooks.items():
                if pattern and pattern not in hook_name:
                    continue
                for hook in hooks:
                    result.append({
                        "hookName": hook_name,
                        "priority": hook.priority,
                        "pluginId": hook.plugin_id
                    })
            return result
    
    def get_filters(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get registered filters.
        
        Args:
            pattern: Optional filter pattern.
            
        Returns:
            List of filter info dictionaries.
        """
        with self._lock:
            result = []
            for filter_name, filters in self._filters.items():
                if pattern and pattern not in filter_name:
                    continue
                for flt in filters:
                    result.append({
                        "filterName": filter_name,
                        "priority": flt.priority,
                        "pluginId": flt.plugin_id
                    })
            return result
    
    def clear(self) -> None:
        """Clear all hooks and filters."""
        with self._lock:
            self._hooks.clear()
            self._filters.clear()


class PluginContext:
    """Execution context provided to plugins."""
    
    def __init__(self, plugin_id: str, hook_system: HookSystem,
                 data_dir: str):
        """Initialize plugin context.
        
        Args:
            plugin_id: ID of the plugin.
            hook_system: Shared hook system.
            data_dir: Directory for plugin data storage.
        """
        self._plugin_id = plugin_id
        self._hook_system = hook_system
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self._plugin_id
    
    # Hook/Filter API
    def register_hook(self, hook_name: str, callback: Callable,
                     priority: int = 10) -> bool:
        """Register a hook callback."""
        return self._hook_system.register_hook(
            hook_name, callback, priority, self._plugin_id
        )
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute a hook."""
        return self._hook_system.execute_hook(hook_name, *args, **kwargs)
    
    def register_filter(self, filter_name: str, callback: Callable,
                       priority: int = 10) -> bool:
        """Register a filter callback."""
        return self._hook_system.register_filter(
            filter_name, callback, priority, self._plugin_id
        )
    
    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Apply a filter."""
        return self._hook_system.apply_filter(filter_name, value, *args, **kwargs)
    
    # Data Storage API
    def get_plugin_data(self, key: str) -> Optional[Any]:
        """Get plugin-specific data.
        
        Args:
            key: Data key.
            
        Returns:
            Stored value or None.
        """
        with self._lock:
            data_file = self._data_dir / f"{self._plugin_id}_data.json"
            if not data_file.exists():
                return None
            
            try:
                data = json.loads(data_file.read_text(encoding="utf-8"))
                return data.get(key)
            except Exception:
                return None
    
    def set_plugin_data(self, key: str, value: Any) -> bool:
        """Set plugin-specific data.
        
        Args:
            key: Data key.
            value: Value to store (must be JSON serializable).
            
        Returns:
            True if stored successfully.
        """
        with self._lock:
            data_file = self._data_dir / f"{self._plugin_id}_data.json"
            
            try:
                if data_file.exists():
                    data = json.loads(data_file.read_text(encoding="utf-8"))
                else:
                    data = {}
                
                data[key] = value
                data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                return True
            except Exception as e:
                logger.error(f"Failed to save plugin data: {e}")
                return False
    
    def delete_plugin_data(self, key: str) -> bool:
        """Delete plugin-specific data.
        
        Args:
            key: Data key to delete.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            data_file = self._data_dir / f"{self._plugin_id}_data.json"
            if not data_file.exists():
                return False
            
            try:
                data = json.loads(data_file.read_text(encoding="utf-8"))
                if key in data:
                    del data[key]
                    data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    return True
                return False
            except Exception:
                return False
    
    # Logging API
    def log_info(self, message: str) -> None:
        """Log info message."""
        logger.info(f"[{self._plugin_id}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        logger.warning(f"[{self._plugin_id}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        logger.error(f"[{self._plugin_id}] {message}")
    
    # Configuration API
    def get_config(self, key: str) -> Optional[Any]:
        """Get configuration value."""
        with self._lock:
            return self._config.get(key)
    
    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        with self._lock:
            self._config[key] = value
            return True
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        with self._lock:
            self._config = config.copy()


class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, context: PluginContext):
        """Initialize plugin.
        
        Args:
            context: Plugin execution context.
        """
        self.context = context
    
    def on_load(self) -> bool:
        """Called when plugin is first loaded.
        
        Returns:
            True if loaded successfully.
        """
        return True
    
    def on_enable(self) -> bool:
        """Called when plugin is enabled.
        
        Returns:
            True if enabled successfully.
        """
        return True
    
    def on_disable(self) -> bool:
        """Called when plugin is disabled.
        
        Returns:
            True if disabled successfully.
        """
        return True
    
    def on_unload(self) -> bool:
        """Called when plugin is unloaded.
        
        Returns:
            True if unloaded successfully.
        """
        return True
    
    def register_hooks(self) -> None:
        """Register plugin hooks and filters.
        
        Override to register custom hooks.
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema.
        
        Returns:
            JSON Schema for plugin configuration.
        """
        return {}


class DependencyResolver:
    """Resolves plugin dependencies and load order."""
    
    def __init__(self):
        """Initialize resolver."""
        self._lock = threading.RLock()
    
    def resolve_dependencies(self, plugins: List[PluginInfo]) -> List[str]:
        """Resolve dependencies and return load order.
        
        Args:
            plugins: List of plugins to resolve.
            
        Returns:
            List of plugin IDs in load order.
        """
        with self._lock:
            # Build dependency graph
            graph: Dict[str, Set[str]] = {}
            available = {p.plugin_id for p in plugins}
            
            for plugin in plugins:
                deps = set()
                for dep in plugin.dependencies:
                    # Parse dependency string (e.g., "plugin_id >= 1.0.0")
                    dep_id = dep.split()[0]
                    if dep_id in available:
                        deps.add(dep_id)
                graph[plugin.plugin_id] = deps
            
            # Topological sort
            return self._topological_sort(graph)
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort on dependency graph.
        
        Args:
            graph: Dependency graph (node -> dependencies).
            
        Returns:
            Sorted list of nodes.
        """
        # Kahn's algorithm
        in_degree = {node: 0 for node in graph}
        for node, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[node] += 1
        
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for other, deps in graph.items():
                if node in deps:
                    in_degree[other] -= 1
                    if in_degree[other] == 0 and other not in result:
                        queue.append(other)
        
        # Check for cycles
        if len(result) != len(graph):
            logger.warning("Circular dependency detected")
        
        return result
    
    def get_load_order(self, plugins: List[PluginInfo]) -> List[str]:
        """Get optimal plugin load order.
        
        Args:
            plugins: Available plugins.
            
        Returns:
            Plugin IDs in load order.
        """
        return self.resolve_dependencies(plugins)
    
    def check_dependencies(self, plugin: PluginInfo,
                          available: Set[str]) -> Tuple[bool, List[str]]:
        """Check if plugin dependencies are satisfied.
        
        Args:
            plugin: Plugin to check.
            available: Set of available plugin IDs.
            
        Returns:
            Tuple of (satisfied, missing_deps).
        """
        missing = []
        for dep in plugin.dependencies:
            dep_id = dep.split()[0]
            if dep_id not in available:
                missing.append(dep_id)
        
        return len(missing) == 0, missing
    
    def detect_circular_dependencies(self, plugins: List[PluginInfo]) -> List[List[str]]:
        """Detect circular dependencies.
        
        Args:
            plugins: List of plugins.
            
        Returns:
            List of cycles (each cycle is a list of plugin IDs).
        """
        with self._lock:
            # Build graph
            graph: Dict[str, Set[str]] = {}
            for plugin in plugins:
                deps = set()
                for dep in plugin.dependencies:
                    dep_id = dep.split()[0]
                    deps.add(dep_id)
                graph[plugin.plugin_id] = deps
            
            # Find cycles using DFS
            cycles = []
            visited = set()
            rec_stack = set()
            path = []
            
            def dfs(node: str) -> None:
                if node not in graph:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in graph.get(node, set()):
                    if neighbor not in visited:
                        dfs(neighbor)
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        cycles.append(path[cycle_start:] + [neighbor])
                
                path.pop()
                rec_stack.remove(node)
            
            for node in graph:
                if node not in visited:
                    dfs(node)
            
            return cycles
    
    def validate_versions(self, plugin: PluginInfo,
                         available_versions: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate version constraints.
        
        Args:
            plugin: Plugin with dependencies.
            available_versions: Map of plugin_id -> version.
            
        Returns:
            Tuple of (valid, errors).
        """
        errors = []
        
        for dep in plugin.dependencies:
            parts = dep.split()
            dep_id = parts[0]
            
            if dep_id not in available_versions:
                errors.append(f"Missing dependency: {dep_id}")
                continue
            
            if len(parts) >= 3:
                operator = parts[1]
                required_version = parts[2]
                actual_version = available_versions[dep_id]
                
                if not self._check_version(actual_version, operator, required_version):
                    errors.append(f"{dep_id}: requires {operator} {required_version}, got {actual_version}")
        
        return len(errors) == 0, errors
    
    def _check_version(self, actual: str, operator: str, required: str) -> bool:
        """Check version against requirement.
        
        Args:
            actual: Actual version string.
            operator: Comparison operator.
            required: Required version string.
            
        Returns:
            True if requirement satisfied.
        """
        try:
            actual_parts = [int(x) for x in actual.split(".")[:3]]
            required_parts = [int(x) for x in required.split(".")[:3]]
            
            # Pad to same length
            while len(actual_parts) < 3:
                actual_parts.append(0)
            while len(required_parts) < 3:
                required_parts.append(0)
            
            if operator == ">=":
                return actual_parts >= required_parts
            elif operator == "<=":
                return actual_parts <= required_parts
            elif operator == ">":
                return actual_parts > required_parts
            elif operator == "<":
                return actual_parts < required_parts
            elif operator == "==":
                return actual_parts == required_parts
            elif operator == "!=":
                return actual_parts != required_parts
            else:
                return True
        except (ValueError, IndexError):
            return True


class CompatibilityChecker:
    """Checks plugin compatibility with host system."""
    
    HOST_VERSION = "2.0.0"
    API_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize checker."""
        self._lock = threading.RLock()
    
    def check_compatibility(self, plugin: PluginInfo) -> Tuple[bool, List[str]]:
        """Check overall plugin compatibility.
        
        Args:
            plugin: Plugin to check.
            
        Returns:
            Tuple of (compatible, issues).
        """
        issues = []
        
        # Check host version compatibility
        if "anki_template_designer" in plugin.compatibility:
            version_range = plugin.compatibility["anki_template_designer"]
            if not self._check_version_range(self.HOST_VERSION, version_range):
                issues.append(f"Incompatible with host version {self.HOST_VERSION}")
        
        # Check Python version
        if "python" in plugin.compatibility:
            python_req = plugin.compatibility["python"]
            if not self.check_python_version(python_req):
                import sys
                issues.append(f"Requires Python {python_req}, got {sys.version_info.major}.{sys.version_info.minor}")
        
        return len(issues) == 0, issues
    
    def check_api_compatibility(self, plugin: PluginInfo) -> bool:
        """Check API version compatibility.
        
        Args:
            plugin: Plugin to check.
            
        Returns:
            True if API compatible.
        """
        if "api_version" in plugin.compatibility:
            return self._check_version_range(
                self.API_VERSION,
                plugin.compatibility["api_version"]
            )
        return True
    
    def check_python_version(self, requirement: str) -> bool:
        """Check Python version requirement.
        
        Args:
            requirement: Version requirement (e.g., "3.8+").
            
        Returns:
            True if satisfied.
        """
        import sys
        
        # Handle "3.8+" format
        if requirement.endswith("+"):
            min_version = requirement[:-1]
            min_parts = [int(x) for x in min_version.split(".")]
            actual_parts = [sys.version_info.major, sys.version_info.minor]
            return actual_parts >= min_parts[:2]
        
        # Handle exact version
        req_parts = [int(x) for x in requirement.split(".")[:2]]
        actual_parts = [sys.version_info.major, sys.version_info.minor]
        return actual_parts >= req_parts
    
    def check_dependency_version(self, dependency: str, version: str) -> bool:
        """Check if dependency version is compatible.
        
        Args:
            dependency: Dependency name.
            version: Version string.
            
        Returns:
            True if compatible.
        """
        # Could be extended to check against known dependency versions
        return True
    
    def get_compatibility_info(self, plugin: PluginInfo) -> Dict[str, Any]:
        """Get detailed compatibility information.
        
        Args:
            plugin: Plugin to analyze.
            
        Returns:
            Compatibility report dictionary.
        """
        compatible, issues = self.check_compatibility(plugin)
        
        return {
            "pluginId": plugin.plugin_id,
            "compatible": compatible,
            "issues": issues,
            "hostVersion": self.HOST_VERSION,
            "apiVersion": self.API_VERSION,
            "pluginRequirements": plugin.compatibility
        }
    
    def _check_version_range(self, version: str, range_str: str) -> bool:
        """Check if version is in range.
        
        Args:
            version: Version to check.
            range_str: Range like "1.0.0..2.0.0" or ">= 1.0.0".
            
        Returns:
            True if in range.
        """
        # Handle range format "1.0.0..2.0.0"
        if ".." in range_str:
            parts = range_str.split("..")
            if len(parts) == 2:
                min_ver, max_ver = parts
                return (self._version_gte(version, min_ver) and
                       self._version_lte(version, max_ver))
        
        # Handle comparison format ">= 1.0.0"
        if range_str.startswith(">="):
            return self._version_gte(version, range_str[2:].strip())
        elif range_str.startswith("<="):
            return self._version_lte(version, range_str[2:].strip())
        elif range_str.startswith(">"):
            return self._version_gt(version, range_str[1:].strip())
        elif range_str.startswith("<"):
            return self._version_lt(version, range_str[1:].strip())
        
        return True
    
    def _parse_version(self, version: str) -> List[int]:
        """Parse version string to list of ints."""
        try:
            return [int(x) for x in version.split(".")[:3]]
        except ValueError:
            return [0, 0, 0]
    
    def _version_gte(self, v1: str, v2: str) -> bool:
        return self._parse_version(v1) >= self._parse_version(v2)
    
    def _version_lte(self, v1: str, v2: str) -> bool:
        return self._parse_version(v1) <= self._parse_version(v2)
    
    def _version_gt(self, v1: str, v2: str) -> bool:
        return self._parse_version(v1) > self._parse_version(v2)
    
    def _version_lt(self, v1: str, v2: str) -> bool:
        return self._parse_version(v1) < self._parse_version(v2)


class PluginRegistry:
    """Discovers and catalogs available plugins."""
    
    def __init__(self, plugins_dir: str):
        """Initialize registry.
        
        Args:
            plugins_dir: Directory containing plugins.
        """
        self._plugins_dir = Path(plugins_dir)
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, PluginInfo] = {}
        self._lock = threading.RLock()
    
    def discover_plugins(self, path: Optional[str] = None) -> List[PluginInfo]:
        """Discover plugins in directory.
        
        Args:
            path: Optional path to scan (defaults to plugins_dir).
            
        Returns:
            List of discovered plugins.
        """
        with self._lock:
            scan_path = Path(path) if path else self._plugins_dir
            discovered = []
            
            if not scan_path.exists():
                return discovered
            
            for item in scan_path.iterdir():
                if not item.is_dir():
                    continue
                
                # Look for manifest
                for manifest_name in ["plugin.json", "plugin.yaml", "manifest.json"]:
                    manifest_path = item / manifest_name
                    if manifest_path.exists():
                        info = PluginInfo.from_manifest(str(manifest_path))
                        if info:
                            discovered.append(info)
                            self._plugins[info.plugin_id] = info
                        break
            
            logger.info(f"Discovered {len(discovered)} plugins")
            return discovered
    
    def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """Register a plugin.
        
        Args:
            plugin_info: Plugin metadata.
            
        Returns:
            True if registered.
        """
        with self._lock:
            self._plugins[plugin_info.plugin_id] = plugin_info
            logger.debug(f"Plugin registered: {plugin_info.plugin_id}")
            return True
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin.
        
        Args:
            plugin_id: Plugin to remove.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if plugin_id in self._plugins:
                del self._plugins[plugin_id]
                logger.debug(f"Plugin unregistered: {plugin_id}")
                return True
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin info.
        
        Args:
            plugin_id: Plugin identifier.
            
        Returns:
            PluginInfo or None.
        """
        with self._lock:
            return self._plugins.get(plugin_id)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all registered plugins.
        
        Returns:
            List of plugin info.
        """
        with self._lock:
            return list(self._plugins.values())
    
    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search plugins by query.
        
        Args:
            query: Search query (matches name, description, author).
            
        Returns:
            Matching plugins.
        """
        with self._lock:
            query_lower = query.lower()
            results = []
            
            for plugin in self._plugins.values():
                if (query_lower in plugin.name.lower() or
                    query_lower in plugin.description.lower() or
                    query_lower in plugin.author.lower() or
                    query_lower in plugin.plugin_id.lower()):
                    results.append(plugin)
            
            return results
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin.
        
        Args:
            plugin_id: Plugin to enable.
            
        Returns:
            True if enabled.
        """
        with self._lock:
            if plugin_id in self._plugins:
                self._plugins[plugin_id].enabled = True
                return True
            return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_id: Plugin to disable.
            
        Returns:
            True if disabled.
        """
        with self._lock:
            if plugin_id in self._plugins:
                self._plugins[plugin_id].enabled = False
                return True
            return False
    
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """Check if plugin is enabled.
        
        Args:
            plugin_id: Plugin to check.
            
        Returns:
            True if enabled.
        """
        with self._lock:
            plugin = self._plugins.get(plugin_id)
            return plugin.enabled if plugin else False


class PluginLifecycleManager:
    """Manages plugin loading and lifecycle."""
    
    def __init__(self, registry: PluginRegistry, hook_system: HookSystem,
                 data_dir: str):
        """Initialize lifecycle manager.
        
        Args:
            registry: Plugin registry.
            hook_system: Hook system.
            data_dir: Directory for plugin data.
        """
        self._registry = registry
        self._hook_system = hook_system
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        self._instances: Dict[str, Plugin] = {}
        self._contexts: Dict[str, PluginContext] = {}
        self._dependency_resolver = DependencyResolver()
        self._compatibility_checker = CompatibilityChecker()
        self._lock = threading.RLock()
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin.
        
        Args:
            plugin_id: Plugin to load.
            
        Returns:
            True if loaded successfully.
        """
        with self._lock:
            info = self._registry.get_plugin(plugin_id)
            if info is None:
                logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            if info.state in [PluginState.LOADED, PluginState.ENABLED]:
                return True  # Already loaded
            
            info.state = PluginState.LOADING
            
            try:
                # Check compatibility
                compatible, issues = self._compatibility_checker.check_compatibility(info)
                if not compatible:
                    logger.error(f"Plugin {plugin_id} incompatible: {issues}")
                    info.state = PluginState.ERROR
                    return False
                
                # Check dependencies
                available = {p.plugin_id for p in self._registry.list_plugins()}
                satisfied, missing = self._dependency_resolver.check_dependencies(info, available)
                if not satisfied:
                    logger.error(f"Plugin {plugin_id} missing dependencies: {missing}")
                    info.state = PluginState.ERROR
                    return False
                
                # Create context
                context = PluginContext(
                    plugin_id=plugin_id,
                    hook_system=self._hook_system,
                    data_dir=str(self._data_dir)
                )
                self._contexts[plugin_id] = context
                
                # Load plugin class
                plugin_class = self._load_plugin_class(info)
                if plugin_class is None:
                    info.state = PluginState.ERROR
                    return False
                
                # Instantiate plugin
                instance = plugin_class(context)
                
                # Call on_load
                if not instance.on_load():
                    logger.error(f"Plugin {plugin_id} on_load failed")
                    info.state = PluginState.ERROR
                    return False
                
                self._instances[plugin_id] = instance
                info.state = PluginState.LOADED
                
                # Execute hook
                self._hook_system.execute_hook("plugin:loaded", plugin_id)
                
                logger.info(f"Plugin loaded: {plugin_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
                info.state = PluginState.ERROR
                return False
    
    def _load_plugin_class(self, info: PluginInfo) -> Optional[Type[Plugin]]:
        """Load plugin class from entry point.
        
        Args:
            info: Plugin info with entry point.
            
        Returns:
            Plugin class or None.
        """
        try:
            if not info.entry_point:
                # Default to plugin.py:Plugin
                module_path = Path(info.path) / "plugin.py"
                class_name = "Plugin"
            else:
                # Parse entry point like "module.main:PluginClass"
                module_part, class_name = info.entry_point.rsplit(":", 1)
                module_path = Path(info.path) / f"{module_part.replace('.', '/')}.py"
            
            if not module_path.exists():
                logger.error(f"Plugin module not found: {module_path}")
                return None
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{info.plugin_id}",
                module_path
            )
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get class
            plugin_class = getattr(module, class_name, None)
            if plugin_class is None:
                logger.error(f"Plugin class not found: {class_name}")
                return None
            
            return plugin_class
            
        except Exception as e:
            logger.error(f"Failed to load plugin class: {e}")
            return None
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin.
        
        Args:
            plugin_id: Plugin to unload.
            
        Returns:
            True if unloaded.
        """
        with self._lock:
            info = self._registry.get_plugin(plugin_id)
            if info is None:
                return False
            
            if info.state == PluginState.NOT_LOADED:
                return True
            
            info.state = PluginState.UNLOADING
            
            try:
                # Disable first if enabled
                if plugin_id in self._instances:
                    instance = self._instances[plugin_id]
                    
                    # Call on_disable if was enabled
                    if info.enabled:
                        instance.on_disable()
                    
                    # Call on_unload
                    instance.on_unload()
                    
                    del self._instances[plugin_id]
                
                # Remove hooks/filters
                self._hook_system.unregister_plugin_hooks(plugin_id)
                self._hook_system.unregister_plugin_filters(plugin_id)
                
                # Remove context
                if plugin_id in self._contexts:
                    del self._contexts[plugin_id]
                
                info.state = PluginState.NOT_LOADED
                info.enabled = False
                
                logger.info(f"Plugin unloaded: {plugin_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to unload plugin {plugin_id}: {e}")
                info.state = PluginState.ERROR
                return False
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a loaded plugin.
        
        Args:
            plugin_id: Plugin to enable.
            
        Returns:
            True if enabled.
        """
        with self._lock:
            info = self._registry.get_plugin(plugin_id)
            if info is None:
                return False
            
            # Load if not loaded
            if info.state == PluginState.NOT_LOADED:
                if not self.load_plugin(plugin_id):
                    return False
            
            if info.state != PluginState.LOADED:
                return False
            
            if plugin_id not in self._instances:
                return False
            
            instance = self._instances[plugin_id]
            
            try:
                # Register hooks
                instance.register_hooks()
                
                # Call on_enable
                if not instance.on_enable():
                    logger.error(f"Plugin {plugin_id} on_enable failed")
                    return False
                
                info.state = PluginState.ENABLED
                self._registry.enable_plugin(plugin_id)
                
                self._hook_system.execute_hook("plugin:enabled", plugin_id)
                
                logger.info(f"Plugin enabled: {plugin_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to enable plugin {plugin_id}: {e}")
                return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an enabled plugin.
        
        Args:
            plugin_id: Plugin to disable.
            
        Returns:
            True if disabled.
        """
        with self._lock:
            info = self._registry.get_plugin(plugin_id)
            if info is None:
                return False
            
            if info.state != PluginState.ENABLED:
                return False
            
            if plugin_id not in self._instances:
                return False
            
            instance = self._instances[plugin_id]
            
            try:
                # Call on_disable
                if not instance.on_disable():
                    logger.error(f"Plugin {plugin_id} on_disable failed")
                
                # Unregister hooks
                self._hook_system.unregister_plugin_hooks(plugin_id)
                self._hook_system.unregister_plugin_filters(plugin_id)
                
                info.state = PluginState.LOADED
                self._registry.disable_plugin(plugin_id)
                
                self._hook_system.execute_hook("plugin:disabled", plugin_id)
                
                logger.info(f"Plugin disabled: {plugin_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to disable plugin {plugin_id}: {e}")
                return False
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin.
        
        Args:
            plugin_id: Plugin to reload.
            
        Returns:
            True if reloaded.
        """
        was_enabled = self._registry.is_plugin_enabled(plugin_id)
        
        if not self.unload_plugin(plugin_id):
            return False
        
        if not self.load_plugin(plugin_id):
            return False
        
        if was_enabled:
            return self.enable_plugin(plugin_id)
        
        return True
    
    def get_plugin_instance(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin instance.
        
        Args:
            plugin_id: Plugin identifier.
            
        Returns:
            Plugin instance or None.
        """
        with self._lock:
            return self._instances.get(plugin_id)
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin IDs.
        
        Returns:
            List of plugin IDs.
        """
        with self._lock:
            return list(self._instances.keys())
    
    def get_plugin_status(self, plugin_id: str) -> str:
        """Get plugin status.
        
        Args:
            plugin_id: Plugin identifier.
            
        Returns:
            Status string.
        """
        with self._lock:
            info = self._registry.get_plugin(plugin_id)
            if info:
                return info.state.value
            return "unknown"


class PluginManager:
    """Main plugin system coordinator."""
    
    def __init__(self, plugins_dir: str, data_dir: str):
        """Initialize plugin manager.
        
        Args:
            plugins_dir: Directory containing plugins.
            data_dir: Directory for plugin data storage.
        """
        self._plugins_dir = plugins_dir
        self._data_dir = data_dir
        
        self._hook_system = HookSystem()
        self._registry = PluginRegistry(plugins_dir)
        self._lifecycle = PluginLifecycleManager(
            self._registry, self._hook_system, data_dir
        )
        
        self._lock = threading.RLock()
        
        logger.info("Plugin manager initialized")
    
    @property
    def hook_system(self) -> HookSystem:
        """Get hook system."""
        return self._hook_system
    
    @property
    def registry(self) -> PluginRegistry:
        """Get plugin registry."""
        return self._registry
    
    @property
    def lifecycle(self) -> PluginLifecycleManager:
        """Get lifecycle manager."""
        return self._lifecycle
    
    def discover_and_load(self) -> int:
        """Discover and load all plugins.
        
        Returns:
            Number of plugins loaded.
        """
        with self._lock:
            plugins = self._registry.discover_plugins()
            
            # Get load order
            resolver = DependencyResolver()
            load_order = resolver.get_load_order(plugins)
            
            loaded = 0
            for plugin_id in load_order:
                if self._lifecycle.load_plugin(plugin_id):
                    loaded += 1
            
            return loaded
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins.
        
        Returns:
            List of plugin info dictionaries.
        """
        return [p.to_dict() for p in self._registry.list_plugins()]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get plugin info.
        
        Args:
            plugin_id: Plugin identifier.
            
        Returns:
            Plugin info dictionary or None.
        """
        info = self._registry.get_plugin(plugin_id)
        return info.to_dict() if info else None
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin."""
        return self._lifecycle.load_plugin(plugin_id)
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        return self._lifecycle.unload_plugin(plugin_id)
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin."""
        return self._lifecycle.enable_plugin(plugin_id)
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        return self._lifecycle.disable_plugin(plugin_id)
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin."""
        return self._lifecycle.reload_plugin(plugin_id)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute a hook."""
        return self._hook_system.execute_hook(hook_name, *args, **kwargs)
    
    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Apply a filter."""
        return self._hook_system.apply_filter(filter_name, value, *args, **kwargs)
    
    def get_hooks(self) -> List[Dict[str, Any]]:
        """Get all registered hooks."""
        return self._hook_system.get_hooks()
    
    def get_filters(self) -> List[Dict[str, Any]]:
        """Get all registered filters."""
        return self._hook_system.get_filters()


# Global instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> Optional[PluginManager]:
    """Get the global plugin manager.
    
    Returns:
        PluginManager or None if not initialized.
    """
    return _plugin_manager


def init_plugin_manager(plugins_dir: str, data_dir: str) -> PluginManager:
    """Initialize the global plugin manager.
    
    Args:
        plugins_dir: Directory for plugins.
        data_dir: Directory for plugin data.
        
    Returns:
        Initialized PluginManager.
    """
    global _plugin_manager
    _plugin_manager = PluginManager(plugins_dir, data_dir)
    return _plugin_manager
