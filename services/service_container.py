"""
Dependency Injection Container

Provides centralized service registration and resolution.
Eliminates tight coupling and improves testability.
"""

from typing import Dict, Callable, Any, Optional


class ServiceContainer:
    """
    Simple dependency injection container.
    
    Supports both singleton and factory-based service registration.
    
    Example:
        >>> container = ServiceContainer()
        >>> container.register_singleton('config', {'auto_refresh': True})
        >>> container.register_factory('renderer', lambda: DesktopRenderer())
        >>> config = container.get('config')
        >>> renderer = container.get('renderer')  # Creates new instance
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton service.
        
        The same instance will be returned for all get() calls.
        
        Args:
            name: Service name (e.g., 'config', 'security_validator')
            instance: Pre-created instance to use
        """
        if name in self._singletons:
            raise ValueError(f"Singleton '{name}' already registered")
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory for creating service instances.
        
        A new instance will be created for each get() call.
        
        Args:
            name: Service name (e.g., 'desktop_renderer')
            factory: Callable that creates and returns a service instance
        """
        if name in self._factories:
            raise ValueError(f"Factory '{name}' already registered")
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name: Service name to resolve
            
        Returns:
            Service instance (singleton or newly created from factory)
            
        Raises:
            KeyError: If service is not registered
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Then check factories
        if name in self._factories:
            return self._factories[name]()
        
        raise KeyError(
            f"Service '{name}' not registered. "
            f"Available services: {', '.join(self.list_services())}"
        )
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name to check
            
        Returns:
            True if service is registered, False otherwise
        """
        return name in self._singletons or name in self._factories
    
    def list_services(self) -> list[str]:
        """
        Get list of all registered service names.
        
        Returns:
            List of service names
        """
        return sorted(set(self._singletons.keys()) | set(self._factories.keys()))
    
    def clear(self) -> None:
        """
        Clear all registered services.
        
        Useful for testing to reset the container state.
        """
        self._singletons.clear()
        self._factories.clear()
    
    def override(self, name: str, instance: Any) -> None:
        """
        Override an existing service (useful for testing).
        
        Args:
            name: Service name to override
            instance: New instance to use
        """
        if name in self._singletons:
            self._singletons[name] = instance
        elif name in self._factories:
            # Convert factory to singleton with new instance
            del self._factories[name]
            self._singletons[name] = instance
        else:
            raise KeyError(f"Cannot override non-existent service '{name}'")
