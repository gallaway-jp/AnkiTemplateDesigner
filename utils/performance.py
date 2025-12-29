"""
Performance optimization utilities.

Provides caching, lazy evaluation, and optimization helpers for template operations.
"""

from functools import lru_cache, wraps
from typing import Callable, Any, Dict, List
import hashlib
import time
from .logging_config import get_logger

logger = get_logger(__name__)


def performance_timer(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        elapsed = (end_time - start_time) * 1000  # Convert to ms
        logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
        
        return result
    
    return wrapper


class ComponentCache:
    """
    LRU cache for component rendering.
    
    Caches CSS and HTML generation for identical components
    to avoid redundant work.
    """
    
    def __init__(self, maxsize: int = 256):
        """
        Initialize component cache.
        
        Args:
            maxsize: Maximum number of entries to cache
        """
        self.maxsize = maxsize
        self._css_cache: Dict[str, str] = {}
        self._html_cache: Dict[str, str] = {}
        self._access_order: List[str] = []
    
    def get_component_hash(self, component) -> str:
        """
        Generate a hash for a component based on its properties.
        
        Args:
            component: Component to hash
            
        Returns:
            str: Hash string
        """
        # Create hash from component properties
        props = {
            'type': component.component_type.value,
            'width': component.width,
            'height': component.height,
            'font_size': getattr(component, 'font_size', None),
            'font_family': getattr(component, 'font_family', None),
            'text_color': getattr(component, 'text_color', None),
            'background_color': getattr(component, 'background_color', None),
            'alignment': getattr(component, 'alignment', None),
            'padding': getattr(component, 'padding', None),
            'margin': getattr(component, 'margin', None),
            'border_width': getattr(component, 'border_width', None),
            'border_color': getattr(component, 'border_color', None),
        }
        
        # Convert to string and hash
        props_str = str(sorted(props.items()))
        return hashlib.md5(props_str.encode()).hexdigest()
    
    def get_css(self, component_hash: str) -> str:
        """
        Get cached CSS for a component.
        
        Args:
            component_hash: Component hash
            
        Returns:
            str: Cached CSS or empty string if not found
        """
        if component_hash in self._css_cache:
            # Update access order
            self._access_order.remove(component_hash)
            self._access_order.append(component_hash)
            return self._css_cache[component_hash]
        
        return ""
    
    def set_css(self, component_hash: str, css: str):
        """
        Cache CSS for a component.
        
        Args:
            component_hash: Component hash
            css: CSS to cache
        """
        # Evict oldest if at capacity
        if len(self._css_cache) >= self.maxsize and component_hash not in self._css_cache:
            oldest = self._access_order.pop(0)
            del self._css_cache[oldest]
        
        self._css_cache[component_hash] = css
        
        if component_hash in self._access_order:
            self._access_order.remove(component_hash)
        self._access_order.append(component_hash)
    
    def get_html(self, component_hash: str) -> str:
        """
        Get cached HTML for a component.
        
        Args:
            component_hash: Component hash
            
        Returns:
            str: Cached HTML or empty string if not found
        """
        if component_hash in self._html_cache:
            self._access_order.remove(component_hash)
            self._access_order.append(component_hash)
            return self._html_cache[component_hash]
        
        return ""
    
    def set_html(self, component_hash: str, html: str):
        """
        Cache HTML for a component.
        
        Args:
            component_hash: Component hash
            html: HTML to cache
        """
        if len(self._html_cache) >= self.maxsize and component_hash not in self._html_cache:
            oldest = self._access_order.pop(0)
            if oldest in self._html_cache:
                del self._html_cache[oldest]
        
        self._html_cache[component_hash] = html
        
        if component_hash in self._access_order:
            self._access_order.remove(component_hash)
        self._access_order.append(component_hash)
    
    def clear(self):
        """Clear all cached data."""
        self._css_cache.clear()
        self._html_cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        return {
            'css_entries': len(self._css_cache),
            'html_entries': len(self._html_cache),
            'total_entries': len(set(self._css_cache.keys()) | set(self._html_cache.keys())),
            'max_size': self.maxsize
        }


# Global component cache instance
_component_cache = ComponentCache(maxsize=256)


def get_component_cache() -> ComponentCache:
    """Get the global component cache instance."""
    return _component_cache


class BatchProcessor:
    """
    Batch processing utilities for efficient bulk operations.
    
    Collects operations and processes them in batches to reduce overhead.
    """
    
    @staticmethod
    def batch_generate_css(components: List, generator_func: Callable) -> List[str]:
        """
        Generate CSS for multiple components in batch.
        
        Args:
            components: List of components
            generator_func: Function to generate CSS for a single component
            
        Returns:
            List of CSS strings
        """
        cache = get_component_cache()
        results = []
        
        for component in components:
            # Try cache first
            component_hash = cache.get_component_hash(component)
            cached_css = cache.get_css(component_hash)
            
            if cached_css:
                results.append(cached_css)
            else:
                # Generate and cache
                css = generator_func(component)
                cache.set_css(component_hash, css)
                results.append(css)
        
        return results
    
    @staticmethod
    def batch_generate_html(components: List, generator_func: Callable) -> List[str]:
        """
        Generate HTML for multiple components in batch.
        
        Args:
            components: List of components
            generator_func: Function to generate HTML for a single component
            
        Returns:
            List of HTML strings
        """
        cache = get_component_cache()
        results = []
        
        for component in components:
            # Try cache first
            component_hash = cache.get_component_hash(component)
            cached_html = cache.get_html(component_hash)
            
            if cached_html:
                results.append(cached_html)
            else:
                # Generate and cache
                html = generator_func(component)
                cache.set_html(component_hash, html)
                results.append(html)
        
        return results


class LazyRenderer:
    """
    Lazy rendering for components.
    
    Only renders components when they're actually needed (e.g., visible in viewport).
    """
    
    def __init__(self):
        """Initialize lazy renderer."""
        self._rendered_components: Dict[str, Any] = {}
    
    def should_render(self, component, viewport_bounds: Dict) -> bool:
        """
        Check if component should be rendered based on viewport.
        
        Args:
            component: Component to check
            viewport_bounds: Dict with 'x', 'y', 'width', 'height'
            
        Returns:
            bool: True if component is in viewport
        """
        # Simple bounding box check
        comp_right = component.x + component.width
        comp_bottom = component.y + component.height
        
        viewport_right = viewport_bounds['x'] + viewport_bounds['width']
        viewport_bottom = viewport_bounds['y'] + viewport_bounds['height']
        
        # Check if bounding boxes overlap
        if (component.x > viewport_right or
            comp_right < viewport_bounds['x'] or
            component.y > viewport_bottom or
            comp_bottom < viewport_bounds['y']):
            return False
        
        return True
    
    def mark_rendered(self, component_id: str, rendered_data: Any):
        """
        Mark a component as rendered and store its data.
        
        Args:
            component_id: Unique component identifier
            rendered_data: Rendered component data
        """
        self._rendered_components[component_id] = rendered_data
    
    def get_rendered(self, component_id: str) -> Any:
        """
        Get rendered data for a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Rendered data or None if not rendered
        """
        return self._rendered_components.get(component_id)
    
    def clear_rendered(self, component_id: str = None):
        """
        Clear rendered data.
        
        Args:
            component_id: Specific component to clear, or None to clear all
        """
        if component_id:
            self._rendered_components.pop(component_id, None)
        else:
            self._rendered_components.clear()


@lru_cache(maxsize=128)
def optimize_css(css: str) -> str:
    """
    Optimize CSS by removing unnecessary whitespace and comments.
    
    Args:
        css: CSS to optimize
        
    Returns:
        str: Optimized CSS
    """
    # Remove comments
    import re
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Remove extra whitespace
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    
    return css.strip()


def debounce(wait_ms: int):
    """
    Decorator to debounce function calls.
    
    Prevents function from being called more than once in specified time window.
    
    Args:
        wait_ms: Wait time in milliseconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        last_call = [0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time() * 1000
            
            if current_time - last_call[0] >= wait_ms:
                last_call[0] = current_time
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
