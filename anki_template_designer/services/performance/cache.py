"""
Caching system for performance optimization.

Plan 13: Provides memory cache with TTL, size limits, and LRU eviction.
"""

import time
import threading
import fnmatch
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field

logger = logging.getLogger("anki_template_designer.services.performance.cache")

T = TypeVar('T')


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
    
    def time_to_live(self) -> float:
        """Get remaining time to live in seconds."""
        if self.expires_at == 0:
            return float('inf')
        return max(0, self.expires_at - time.time())


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
    
    @property
    def total_requests(self) -> int:
        """Get total number of cache requests."""
        return self.hits + self.misses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "entries": self.entries,
            "sizeBytes": self.size_bytes,
            "evictions": self.evictions,
            "hitRate": round(self.hit_rate, 4),
            "totalRequests": self.total_requests
        }


class MemoryCache:
    """Thread-safe in-memory cache with TTL and size limits.
    
    Implements LRU eviction when size limit is reached.
    
    Example:
        cache = MemoryCache(max_size_mb=50, default_ttl=300)
        
        # Store value
        cache.set("key1", {"data": "value"}, ttl=60)
        
        # Retrieve value
        value = cache.get("key1")
        
        # Use decorator
        @cache.cached("user:{user_id}")
        def get_user(user_id):
            return expensive_lookup(user_id)
    """
    
    def __init__(
        self, 
        max_size_mb: int = 100,
        default_ttl: int = 3600,
        name: str = "default"
    ) -> None:
        """Initialize memory cache.
        
        Args:
            max_size_mb: Maximum cache size in MB.
            default_ttl: Default TTL in seconds (0 = never expire).
            name: Cache name for logging.
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._default_ttl = default_ttl
        self._stats = CacheStats()
        self._access_order: List[str] = []  # For LRU tracking
        self._name = name
        
        logger.debug(f"MemoryCache '{name}' initialized: max_size={max_size_mb}MB, ttl={default_ttl}s")
    
    @property
    def name(self) -> str:
        """Get cache name."""
        return self._name
    
    @property
    def size(self) -> int:
        """Get current number of entries."""
        return len(self._cache)
    
    @property
    def size_bytes(self) -> int:
        """Get current size in bytes."""
        return self._stats.size_bytes
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key.
            default: Default value if not found.
            
        Returns:
            Cached value or default if not found/expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return default
            
            if entry.is_expired():
                self._remove(key)
                self._stats.misses += 1
                return default
            
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
                    logger.warning(f"Cache '{self._name}': Cannot store, cache full")
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
    
    def has(self, key: str) -> bool:
        """Check if key exists and is not expired.
        
        Args:
            key: Cache key.
            
        Returns:
            True if key exists and is valid.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                self._remove(key)
                return False
            return True
    
    def clear(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of entries cleared.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            self._stats = CacheStats()
            logger.debug(f"Cache '{self._name}' cleared: {count} entries")
            return count
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern.
        
        Args:
            pattern: Pattern to match (supports * wildcard).
            
        Returns:
            Number of entries invalidated.
        """
        with self._lock:
            keys_to_remove = [
                k for k in self._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            
            for key in keys_to_remove:
                self._remove(key)
            
            logger.debug(f"Cache '{self._name}' invalidated pattern '{pattern}': {len(keys_to_remove)} entries")
            return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed.
        """
        with self._lock:
            expired = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            
            for key in expired:
                self._remove(key)
            
            if expired:
                logger.debug(f"Cache '{self._name}' cleanup: {len(expired)} expired entries removed")
            
            return len(expired)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            CacheStats object with current statistics.
        """
        with self._lock:
            # Return a copy
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                entries=self._stats.entries,
                size_bytes=self._stats.size_bytes,
                evictions=self._stats.evictions
            )
    
    def get_or_set(
        self, 
        key: str, 
        factory: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """Get value from cache or compute and store it.
        
        Args:
            key: Cache key.
            factory: Function to compute value if not cached.
            ttl: Time-to-live in seconds.
            
        Returns:
            Cached or computed value.
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = factory()
        self.set(key, value, ttl)
        return value
    
    def cached(
        self, 
        key_template: str,
        ttl: Optional[int] = None
    ) -> Callable:
        """Decorator for caching function results.
        
        Args:
            key_template: Key template with {arg} placeholders.
            ttl: Time-to-live in seconds.
            
        Returns:
            Decorator function.
            
        Example:
            @cache.cached("user:{user_id}", ttl=300)
            def get_user(user_id):
                return expensive_lookup(user_id)
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Build key from template
                key = key_template.format(*args, **kwargs)
                
                # Try cache first
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Compute and cache
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def _remove(self, key: str) -> bool:
        """Internal: Remove entry without locking."""
        if key not in self._cache:
            return False
        
        entry = self._cache.pop(key)
        self._stats.entries -= 1
        self._stats.size_bytes -= entry.size
        
        if key in self._access_order:
            self._access_order.remove(key)
        
        return True
    
    def _evict_lru(self) -> bool:
        """Internal: Evict least recently used entry."""
        if not self._access_order:
            return False
        
        # Get LRU key
        lru_key = self._access_order[0]
        self._remove(lru_key)
        self._stats.evictions += 1
        
        logger.debug(f"Cache '{self._name}' evicted LRU entry: {lru_key}")
        return True
    
    def _update_access_order(self, key: str) -> None:
        """Internal: Update LRU access order."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def _estimate_size(self, value: Any) -> int:
        """Internal: Estimate size of value in bytes."""
        try:
            import sys
            return sys.getsizeof(value)
        except (TypeError, AttributeError):
            # Fallback estimate
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                import json
                return len(json.dumps(value).encode('utf-8'))
            else:
                return 100  # Default estimate
    
    def keys(self) -> List[str]:
        """Get all cache keys.
        
        Returns:
            List of cache keys.
        """
        with self._lock:
            return list(self._cache.keys())
    
    def items(self) -> List[tuple]:
        """Get all cache items.
        
        Returns:
            List of (key, value) tuples.
        """
        with self._lock:
            return [(k, v.value) for k, v in self._cache.items() if not v.is_expired()]
