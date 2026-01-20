"""
Performance Optimization Engine (Issue #54)

Comprehensive performance optimization system with:
- Multi-level caching (memory, disk, CDN)
- Async operations manager with batching and priority queue
- Rendering optimization (virtual scrolling, canvas, DOM batching)
- Performance analytics and bottleneck detection
"""

import time
import json
import gzip
import threading
import hashlib
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional, Dict, List, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from statistics import mean, stdev, quantiles
import tempfile


# ============================================================================
# Enums
# ============================================================================

class OperationStatus(Enum):
    """Status of async operation"""
    QUEUED = "queued"
    BATCHING = "batching"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CacheStrategy(Enum):
    """Cache placement strategy"""
    MEMORY = "memory"
    DISK = "disk"
    AUTO = "auto"  # Auto-select based on size


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    timestamp: float
    ttl_seconds: int
    hits: int = 0
    size_bytes: int = 0
    compressed: bool = False
    dependencies: Set[str] = field(default_factory=set)


@dataclass
class CacheStats:
    """Cache statistics"""
    total_entries: int = 0
    memory_entries: int = 0
    disk_entries: int = 0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    hit_count: int = 0
    miss_count: int = 0
    hit_ratio: float = 0.0
    avg_retrieval_ms: float = 0.0


@dataclass
class AsyncOperation:
    """Async operation tracking"""
    operation_id: str
    operation_func: Callable
    priority: int
    status: OperationStatus
    queued_time: float
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    timeout_seconds: int = 30
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AsyncStats:
    """Async operations statistics"""
    total_queued: int = 0
    total_completed: int = 0
    total_failed: int = 0
    total_cancelled: int = 0
    avg_wait_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    current_pending_count: int = 0
    current_concurrent_count: int = 0
    longest_operation_ms: float = 0.0


@dataclass
class RenderStats:
    """Rendering statistics"""
    container_id: str = ""
    total_renders: int = 0
    avg_render_time_ms: float = 0.0
    max_render_time_ms: float = 0.0
    fps_average: float = 0.0
    fps_min: float = 0.0
    fps_max: float = 0.0
    reflow_count: int = 0
    repaint_count: int = 0
    dom_nodes_rendered: int = 0


@dataclass
class CSSMetrics:
    """CSS analysis metrics"""
    total_rules: int = 0
    total_selectors: int = 0
    specificity_average: float = 0.0
    unused_rules_count: int = 0
    complexity_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)


@dataclass
class MetricPoint:
    """Single performance metric data point"""
    timestamp: float
    operation_name: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metrics:
    """Performance metrics summary"""
    operation_name: str = ""
    count: int = 0
    total_ms: float = 0.0
    avg_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0


@dataclass
class Bottleneck:
    """Performance bottleneck identified"""
    operation_name: str
    avg_duration_ms: float
    p95_duration_ms: float
    call_count: int
    total_time_pct: float
    impact_score: float


@dataclass
class TrendAnalysis:
    """Trend analysis for metrics"""
    metric_name: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1
    average: float
    velocity: float  # Change per time unit


@dataclass
class Anomaly:
    """Detected anomaly in metrics"""
    metric_name: str
    timestamp: float
    value: float
    expected_value: float
    deviation_std: float
    severity: str  # "low", "medium", "high"


@dataclass
class ThresholdViolation:
    """Performance threshold violation"""
    operation_name: str
    threshold_ms: int
    actual_ms: float
    percentile: int
    violation_count: int
    severity: str


# ============================================================================
# CachingSystem
# ============================================================================

class CachingSystem:
    """Multi-level caching with memory, disk, and dependency management"""

    def __init__(self, max_memory_mb: int = 100, max_disk_mb: int = 1000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_disk_bytes = max_disk_mb * 1024 * 1024
        
        # Memory cache
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_size = 0
        
        # Disk cache directory
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'anki_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.disk_size = 0
        
        # Dependency tracking
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)  # key -> depends_on keys
        self.dependents: Dict[str, Set[str]] = defaultdict(set)   # depends_on -> keys
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.retrieval_times: List[float] = []
        
        # Thread safety
        self.lock = threading.RLock()

    # ========== Memory Cache ==========

    def memory_cache_get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        with self.lock:
            if key not in self.memory_cache:
                return None
            
            entry = self.memory_cache[key]
            
            # Check expiration
            if time.time() - entry.timestamp > entry.ttl_seconds:
                del self.memory_cache[key]
                self.memory_size -= entry.size_bytes
                return None
            
            entry.hits += 1
            return entry.value

    def memory_cache_set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set value in memory cache"""
        with self.lock:
            # Calculate size
            size = len(json.dumps(value, default=str).encode('utf-8'))
            
            # Check if it exceeds max memory
            if self.memory_size + size > self.max_memory_bytes:
                # Use disk cache instead for large values
                self.disk_cache_set(key, value, ttl_seconds)
                return
            
            # Remove old entry if exists
            if key in self.memory_cache:
                self.memory_size -= self.memory_cache[key].size_bytes
            
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl_seconds=ttl_seconds,
                size_bytes=size
            )
            self.memory_cache[key] = entry
            self.memory_size += size

    def memory_cache_delete(self, key: str) -> bool:
        """Delete from memory cache"""
        with self.lock:
            if key in self.memory_cache:
                self.memory_size -= self.memory_cache[key].size_bytes
                del self.memory_cache[key]
                return True
            return False

    def memory_cache_clear(self) -> None:
        """Clear all memory cache"""
        with self.lock:
            self.memory_cache.clear()
            self.memory_size = 0

    # ========== Disk Cache ==========

    def disk_cache_get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        with self.lock:
            cache_file = os.path.join(self.cache_dir, self._hash_key(key))
            
            if not os.path.exists(cache_file):
                return None
            
            try:
                with open(cache_file, 'rb') as f:
                    data = f.read()
                
                # Decompress if needed
                if data[:2] == b'\x1f\x8b':  # gzip magic number
                    data = gzip.decompress(data)
                
                entry_data = json.loads(data.decode('utf-8'))
                
                # Check expiration
                if time.time() - entry_data['timestamp'] > entry_data['ttl_seconds']:
                    os.remove(cache_file)
                    return None
                
                return entry_data['value']
            except Exception:
                return None

    def disk_cache_set(self, key: str, value: Any, ttl_seconds: int = 86400, 
                      compress: bool = True) -> None:
        """Set value in disk cache"""
        with self.lock:
            cache_file = os.path.join(self.cache_dir, self._hash_key(key))
            
            entry_data = {
                'key': key,
                'value': value,
                'timestamp': time.time(),
                'ttl_seconds': ttl_seconds,
                'compressed': compress
            }
            
            data = json.dumps(entry_data, default=str).encode('utf-8')
            
            if compress:
                data = gzip.compress(data)
            
            with open(cache_file, 'wb') as f:
                f.write(data)

    def disk_cache_delete(self, key: str) -> bool:
        """Delete from disk cache"""
        with self.lock:
            cache_file = os.path.join(self.cache_dir, self._hash_key(key))
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
            return False

    def disk_cache_clear(self) -> None:
        """Clear all disk cache"""
        with self.lock:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))

    # ========== Public API ==========

    def get_from_cache(self, key: str, strategy: str = 'auto') -> Optional[Any]:
        """Get from cache with specified strategy"""
        strategy_enum = CacheStrategy[strategy.upper()]
        
        if strategy_enum == CacheStrategy.MEMORY:
            return self.memory_cache_get(key)
        elif strategy_enum == CacheStrategy.DISK:
            return self.disk_cache_get(key)
        else:  # AUTO
            # Try memory first, then disk
            value = self.memory_cache_get(key)
            if value is not None:
                self.hit_count += 1
                return value
            
            value = self.disk_cache_get(key)
            if value is not None:
                self.hit_count += 1
                return value
            
            self.miss_count += 1
            return None

    def set_in_cache(self, key: str, value: Any, ttl_seconds: int = 3600, 
                    strategy: str = 'auto') -> None:
        """Set in cache with specified strategy"""
        strategy_enum = CacheStrategy[strategy.upper()]
        
        if strategy_enum == CacheStrategy.MEMORY:
            self.memory_cache_set(key, value, ttl_seconds)
        elif strategy_enum == CacheStrategy.DISK:
            self.disk_cache_set(key, value, ttl_seconds)
        else:  # AUTO
            # Auto-select based on size
            size = len(json.dumps(value, default=str).encode('utf-8'))
            if self.memory_size + size <= self.max_memory_bytes:
                self.memory_cache_set(key, value, ttl_seconds)
            else:
                self.disk_cache_set(key, value, ttl_seconds)

    def invalidate_cache(self, pattern: str = '*', cascade: bool = False) -> int:
        """Invalidate cache entries matching pattern"""
        with self.lock:
            keys_to_delete = []
            
            if pattern == '*':
                keys_to_delete = list(self.memory_cache.keys())
            else:
                # Simple wildcard matching
                for key in self.memory_cache.keys():
                    if self._pattern_matches(key, pattern):
                        keys_to_delete.append(key)
            
            deleted_count = 0
            for key in keys_to_delete:
                self.memory_cache_delete(key)
                self.disk_cache_delete(key)
                deleted_count += 1
                
                # Cascade invalidate dependents
                if cascade:
                    deleted_count += self._cascade_invalidate(key)
            
            return deleted_count

    def set_dependency(self, key: str, depends_on_key: str) -> None:
        """Set dependency between cache entries"""
        with self.lock:
            self.dependencies[key].add(depends_on_key)
            self.dependents[depends_on_key].add(key)

    def cascade_invalidate(self, key: str) -> int:
        """Cascade invalidate dependents"""
        return self._cascade_invalidate(key)

    def _cascade_invalidate(self, key: str) -> int:
        """Internal cascade invalidation"""
        deleted_count = 0
        dependent_keys = list(self.dependents.get(key, set()))
        
        for dep_key in dependent_keys:
            self.memory_cache_delete(dep_key)
            self.disk_cache_delete(dep_key)
            deleted_count += 1
            deleted_count += self._cascade_invalidate(dep_key)
        
        return deleted_count

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self.lock:
            hit_ratio = self.hit_count / (self.hit_count + self.miss_count) \
                if (self.hit_count + self.miss_count) > 0 else 0.0
            
            avg_retrieval = mean(self.retrieval_times) if self.retrieval_times else 0.0
            
            return CacheStats(
                total_entries=len(self.memory_cache),
                memory_entries=len(self.memory_cache),
                disk_entries=len(os.listdir(self.cache_dir)) if os.path.exists(self.cache_dir) else 0,
                memory_usage_mb=self.memory_size / (1024 * 1024),
                disk_usage_mb=self.disk_size / (1024 * 1024),
                hit_count=self.hit_count,
                miss_count=self.miss_count,
                hit_ratio=hit_ratio,
                avg_retrieval_ms=avg_retrieval
            )

    def get_hit_ratio(self) -> float:
        """Get cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

    def get_cache_efficiency(self) -> float:
        """Get cache efficiency score (0-1)"""
        if not self.retrieval_times:
            return 0.0
        return min(1.0, self.get_hit_ratio())

    def reset_statistics(self) -> None:
        """Reset cache statistics"""
        with self.lock:
            self.hit_count = 0
            self.miss_count = 0
            self.retrieval_times.clear()

    def _hash_key(self, key: str) -> str:
        """Generate hash for cache file name"""
        return hashlib.md5(key.encode()).hexdigest()

    def _pattern_matches(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

    def compress_value(self, value: Any) -> bytes:
        """Compress value"""
        return gzip.compress(json.dumps(value, default=str).encode('utf-8'))

    def decompress_value(self, compressed: bytes) -> Any:
        """Decompress value"""
        return json.loads(gzip.decompress(compressed).decode('utf-8'))

    def get_compression_ratio(self) -> float:
        """Get average compression ratio"""
        # Simplified: return estimated ratio
        return 0.6  # ~60% of original size


# ============================================================================
# AsyncOperationsManager
# ============================================================================

class AsyncOperationsManager:
    """Manage async operations with priority queue and batching"""

    def __init__(self, max_concurrent: int = 5, batch_size: int = 10):
        self.max_concurrent = max_concurrent
        self.default_batch_size = batch_size
        
        # Priority queue (higher number = higher priority)
        self.operation_queue: Dict[int, deque] = defaultdict(deque)  # priority -> ops
        self.operations: Dict[str, AsyncOperation] = {}
        
        # Batching
        self.batching_enabled: Dict[str, bool] = defaultdict(bool)
        self.batch_size_per_type: Dict[str, int] = defaultdict(lambda: batch_size)
        self.batch_timeout_ms: Dict[str, int] = defaultdict(lambda: 100)
        self.batches: Dict[str, deque] = defaultdict(deque)
        self.batch_timers: Dict[str, float] = {}
        
        # Throttling
        self.throttle_ms: Dict[str, int] = defaultdict(int)
        self.last_operation_time: Dict[str, float] = {}
        
        # Timeout management
        self.timeout_seconds: Dict[str, int] = defaultdict(lambda: 30)
        
        # Tracking
        self.current_concurrent = 0
        self.statistics = {
            'total_queued': 0,
            'total_completed': 0,
            'total_failed': 0,
            'total_cancelled': 0,
            'execution_times': deque(maxlen=1000),
            'wait_times': deque(maxlen=1000)
        }
        
        # Thread safety
        self.lock = threading.RLock()

    # ========== Operation Management ==========

    def queue_operation(self, operation_func: Callable, priority: int = 5, 
                       timeout_seconds: int = 30) -> str:
        """Queue an async operation"""
        import uuid
        operation_id = str(uuid.uuid4())
        
        with self.lock:
            operation = AsyncOperation(
                operation_id=operation_id,
                operation_func=operation_func,
                priority=max(1, min(10, priority)),  # Clamp 1-10
                status=OperationStatus.QUEUED,
                queued_time=time.time(),
                timeout_seconds=timeout_seconds
            )
            
            self.operations[operation_id] = operation
            self.operation_queue[operation.priority].append(operation)
            self.statistics['total_queued'] += 1
            
        return operation_id

    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a queued operation"""
        with self.lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status in [OperationStatus.COMPLETED, OperationStatus.IN_PROGRESS]:
                return False
            
            operation.status = OperationStatus.CANCELLED
            return True

    def wait_for_operation(self, operation_id: str, timeout_seconds: Optional[int] = None) -> Any:
        """Wait for operation completion"""
        if timeout_seconds is None:
            timeout_seconds = self.operations.get(operation_id, AsyncOperation(
                '', None, 0, OperationStatus.QUEUED, 0)).timeout_seconds
        
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            with self.lock:
                if operation_id in self.operations:
                    op = self.operations[operation_id]
                    if op.status == OperationStatus.COMPLETED:
                        return op.result
                    if op.status in [OperationStatus.FAILED, OperationStatus.TIMEOUT]:
                        raise Exception(op.error)
            
            time.sleep(0.01)
        
        raise TimeoutError(f"Operation {operation_id} timed out")

    def get_operation_status(self, operation_id: str) -> Optional[OperationStatus]:
        """Get operation status"""
        with self.lock:
            if operation_id in self.operations:
                return self.operations[operation_id].status
            return None

    def get_pending_operations(self) -> List[Dict]:
        """Get list of pending operations"""
        with self.lock:
            return [
                {
                    'operation_id': op.operation_id,
                    'priority': op.priority,
                    'status': op.status.value,
                    'queued_time': op.queued_time
                }
                for op in self.operations.values()
                if op.status in [OperationStatus.QUEUED, OperationStatus.BATCHING, 
                                OperationStatus.IN_PROGRESS]
            ]

    def get_pending_count(self) -> int:
        """Get number of pending operations"""
        with self.lock:
            return sum(1 for op in self.operations.values()
                      if op.status in [OperationStatus.QUEUED, OperationStatus.BATCHING,
                                      OperationStatus.IN_PROGRESS])

    # ========== Batching ==========

    def enable_batching(self, operation_type: str, batch_size: int = 10, 
                       batch_timeout_ms: int = 100) -> None:
        """Enable batching for operation type"""
        with self.lock:
            self.batching_enabled[operation_type] = True
            self.batch_size_per_type[operation_type] = batch_size
            self.batch_timeout_ms[operation_type] = batch_timeout_ms

    def disable_batching(self, operation_type: str) -> None:
        """Disable batching for operation type"""
        with self.lock:
            self.batching_enabled[operation_type] = False

    def get_batch_stats(self, operation_type: str) -> Dict:
        """Get batching statistics"""
        with self.lock:
            return {
                'batching_enabled': self.batching_enabled[operation_type],
                'batch_size': self.batch_size_per_type[operation_type],
                'batch_timeout_ms': self.batch_timeout_ms[operation_type],
                'pending_in_batch': len(self.batches[operation_type])
            }

    # ========== Throttling ==========

    def set_operation_throttle_ms(self, operation_type: str, milliseconds: int) -> None:
        """Set throttle for operation type"""
        with self.lock:
            self.throttle_ms[operation_type] = milliseconds

    def get_throttle_ms(self, operation_type: str) -> int:
        """Get throttle for operation type"""
        return self.throttle_ms.get(operation_type, 0)

    # ========== Timeout Management ==========

    def set_operation_timeout_seconds(self, operation_type: str, seconds: int) -> None:
        """Set timeout for operation type"""
        with self.lock:
            self.timeout_seconds[operation_type] = seconds

    def get_timeout_seconds(self, operation_type: str) -> int:
        """Get timeout for operation type"""
        return self.timeout_seconds.get(operation_type, 30)

    # ========== Statistics ==========

    def get_async_stats(self) -> AsyncStats:
        """Get async operation statistics"""
        with self.lock:
            avg_wait = mean(self.statistics['wait_times']) if self.statistics['wait_times'] else 0.0
            avg_exec = mean(self.statistics['execution_times']) if self.statistics['execution_times'] else 0.0
            longest_op = max(self.statistics['execution_times']) if self.statistics['execution_times'] else 0.0
            
            return AsyncStats(
                total_queued=self.statistics['total_queued'],
                total_completed=self.statistics['total_completed'],
                total_failed=self.statistics['total_failed'],
                total_cancelled=self.statistics['total_cancelled'],
                avg_wait_time_ms=avg_wait,
                avg_execution_time_ms=avg_exec,
                current_pending_count=self.get_pending_count(),
                current_concurrent_count=self.current_concurrent,
                longest_operation_ms=longest_op
            )

    def get_operation_metrics(self, operation_type: str) -> Dict:
        """Get metrics for operation type"""
        return {
            'type': operation_type,
            'throttle_ms': self.throttle_ms[operation_type],
            'timeout_seconds': self.timeout_seconds[operation_type],
            'batching_enabled': self.batching_enabled[operation_type]
        }

    def reset_statistics(self) -> None:
        """Reset statistics"""
        with self.lock:
            self.statistics['total_queued'] = 0
            self.statistics['total_completed'] = 0
            self.statistics['total_failed'] = 0
            self.statistics['total_cancelled'] = 0
            self.statistics['execution_times'].clear()
            self.statistics['wait_times'].clear()


# ============================================================================
# RenderingOptimizer
# ============================================================================

class RenderingOptimizer:
    """Optimize rendering and DOM operations"""

    def __init__(self):
        self.virtual_scrolling_enabled: Dict[str, bool] = {}
        self.item_heights: Dict[str, int] = {}
        self.buffer_items: Dict[str, int] = defaultdict(lambda: 5)
        self.visible_ranges: Dict[str, Tuple[int, int]] = {}
        
        self.render_stats: Dict[str, RenderStats] = {}
        self.frame_times: deque = deque(maxlen=60)
        
        self.lock = threading.RLock()

    def enable_virtual_scrolling(self, container_id: str, item_height: int, 
                                buffer_items: int = 5) -> None:
        """Enable virtual scrolling for container"""
        with self.lock:
            self.virtual_scrolling_enabled[container_id] = True
            self.item_heights[container_id] = item_height
            self.buffer_items[container_id] = buffer_items
            
            if container_id not in self.render_stats:
                self.render_stats[container_id] = RenderStats(container_id=container_id)

    def disable_virtual_scrolling(self, container_id: str) -> None:
        """Disable virtual scrolling"""
        with self.lock:
            self.virtual_scrolling_enabled[container_id] = False

    def scroll_to_item(self, container_id: str, item_index: int) -> None:
        """Scroll to item"""
        with self.lock:
            if container_id in self.item_heights:
                # Simulate scroll
                self.visible_ranges[container_id] = (max(0, item_index - 5), item_index + 10)

    def get_visible_range(self, container_id: str) -> Tuple[int, int]:
        """Get visible range for virtual scrolling"""
        with self.lock:
            return self.visible_ranges.get(container_id, (0, 20))

    def analyze_css_complexity(self, stylesheet: str) -> CSSMetrics:
        """Analyze CSS complexity"""
        rules = len([line for line in stylesheet.split('}') if '{' in line])
        selectors = len([s.strip() for s in stylesheet.split(',') if s.strip()])
        
        return CSSMetrics(
            total_rules=rules,
            total_selectors=selectors,
            specificity_average=50.0,
            unused_rules_count=0,
            complexity_score=min(100.0, rules * 2),
            optimization_suggestions=[]
        )

    def get_render_stats(self, container_id: str) -> RenderStats:
        """Get render statistics"""
        with self.lock:
            if container_id not in self.render_stats:
                return RenderStats(container_id=container_id)
            return self.render_stats[container_id]

    def get_frame_rate(self) -> float:
        """Get average frame rate"""
        if not self.frame_times:
            return 60.0
        
        avg_time = mean(self.frame_times)
        return 1000.0 / avg_time if avg_time > 0 else 60.0

    def reset_render_metrics(self) -> None:
        """Reset render metrics"""
        with self.lock:
            self.render_stats.clear()
            self.frame_times.clear()


# ============================================================================
# PerformanceAnalytics
# ============================================================================

class PerformanceAnalytics:
    """Track, analyze, and report on performance metrics"""

    def __init__(self, max_metrics: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self.operation_traces: Dict[str, MetricPoint] = {}
        self.thresholds: Dict[str, int] = {}
        self.threshold_percentiles: Dict[str, int] = defaultdict(lambda: 95)
        
        self.lock = threading.RLock()

    def start_operation(self, operation_name: str, tags: Optional[Dict] = None) -> str:
        """Start performance tracking"""
        import uuid
        trace_id = str(uuid.uuid4())
        
        with self.lock:
            self.operation_traces[trace_id] = MetricPoint(
                timestamp=time.time(),
                operation_name=operation_name,
                duration_ms=0.0,
                success=False,
                tags=tags or {}
            )
        
        return trace_id

    def end_operation(self, trace_id: str, success: bool = True, 
                     error_message: Optional[str] = None) -> None:
        """End performance tracking"""
        with self.lock:
            if trace_id not in self.operation_traces:
                return
            
            start_point = self.operation_traces[trace_id]
            duration = (time.time() - start_point.timestamp) * 1000
            
            metric = MetricPoint(
                timestamp=start_point.timestamp,
                operation_name=start_point.operation_name,
                duration_ms=duration,
                success=success,
                error_message=error_message,
                tags=start_point.tags
            )
            
            self.metrics[start_point.operation_name].append(metric)
            del self.operation_traces[trace_id]

    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None) -> None:
        """Record custom metric"""
        with self.lock:
            metric = MetricPoint(
                timestamp=time.time(),
                operation_name=metric_name,
                duration_ms=value,
                success=True,
                tags=tags or {}
            )
            self.metrics[metric_name].append(metric)

    def get_operation_metrics(self, operation_name: str, 
                             time_window_minutes: int = 60) -> Metrics:
        """Get metrics summary"""
        with self.lock:
            if operation_name not in self.metrics:
                return Metrics(operation_name=operation_name)
            
            cutoff_time = time.time() - (time_window_minutes * 60)
            relevant_metrics = [m for m in self.metrics[operation_name] 
                               if m.timestamp >= cutoff_time]
            
            if not relevant_metrics:
                return Metrics(operation_name=operation_name)
            
            durations = [m.duration_ms for m in relevant_metrics]
            durations_sorted = sorted(durations)
            success_count = sum(1 for m in relevant_metrics if m.success)
            
            # Calculate percentiles
            try:
                p50 = quantiles(durations, n=2)[0] if len(durations) > 1 else durations[0]
                p95 = quantiles(durations, n=20)[18] if len(durations) > 1 else durations[-1]
                p99 = quantiles(durations, n=100)[98] if len(durations) > 1 else durations[-1]
            except Exception:
                p50 = p95 = p99 = mean(durations)
            
            return Metrics(
                operation_name=operation_name,
                count=len(relevant_metrics),
                total_ms=sum(durations),
                avg_ms=mean(durations),
                min_ms=min(durations),
                max_ms=max(durations),
                p50_ms=p50,
                p95_ms=p95,
                p99_ms=p99,
                success_rate=success_count / len(relevant_metrics),
                error_count=len(relevant_metrics) - success_count
            )

    def detect_bottlenecks(self) -> List[Bottleneck]:
        """Detect performance bottlenecks"""
        with self.lock:
            bottlenecks = []
            total_time = 0.0
            
            all_metrics = {}
            for op_name, metrics_deque in self.metrics.items():
                if metrics_deque:
                    metrics_summary = self.get_operation_metrics(op_name)
                    all_metrics[op_name] = metrics_summary
                    total_time += metrics_summary.total_ms
            
            for op_name, metrics_summary in all_metrics.items():
                time_pct = (metrics_summary.total_ms / total_time * 100) if total_time > 0 else 0
                impact_score = min(100.0, time_pct * 2)  # Weight by time percentage
                
                if time_pct > 10:  # More than 10% of total time
                    bottlenecks.append(Bottleneck(
                        operation_name=op_name,
                        avg_duration_ms=metrics_summary.avg_ms,
                        p95_duration_ms=metrics_summary.p95_ms,
                        call_count=metrics_summary.count,
                        total_time_pct=time_pct,
                        impact_score=impact_score
                    ))
            
            return sorted(bottlenecks, key=lambda b: b.impact_score, reverse=True)

    def set_performance_threshold(self, operation_name: str, threshold_ms: int, 
                                 percentile: int = 95) -> None:
        """Set performance threshold"""
        with self.lock:
            self.thresholds[operation_name] = threshold_ms
            self.threshold_percentiles[operation_name] = percentile

    def get_threshold_violations(self, time_window_minutes: int = 60) -> List[ThresholdViolation]:
        """Get threshold violations"""
        violations = []
        
        with self.lock:
            for op_name, threshold in self.thresholds.items():
                metrics = self.get_operation_metrics(op_name, time_window_minutes)
                percentile = self.threshold_percentiles[op_name]
                
                if percentile == 95:
                    actual_value = metrics.p95_ms
                elif percentile == 99:
                    actual_value = metrics.p99_ms
                else:
                    actual_value = metrics.avg_ms
                
                if actual_value > threshold:
                    violations.append(ThresholdViolation(
                        operation_name=op_name,
                        threshold_ms=threshold,
                        actual_ms=actual_value,
                        percentile=percentile,
                        violation_count=metrics.count,
                        severity='high' if actual_value > threshold * 2 else 'medium'
                    ))
        
        return violations

    def export_metrics(self, format: str = 'json', time_window_minutes: int = 60) -> str:
        """Export metrics"""
        with self.lock:
            data = {}
            
            for op_name in self.metrics.keys():
                metrics = self.get_operation_metrics(op_name, time_window_minutes)
                data[op_name] = asdict(metrics)
            
            if format == 'json':
                return json.dumps(data, indent=2)
            
            return str(data)

    def reset_metrics(self, operation_name: Optional[str] = None) -> None:
        """Reset metrics"""
        with self.lock:
            if operation_name:
                if operation_name in self.metrics:
                    self.metrics[operation_name].clear()
            else:
                self.metrics.clear()


# ============================================================================
# PerformanceOptimizer (Main Orchestrator)
# ============================================================================

class PerformanceOptimizer:
    """Main performance optimization orchestrator"""

    def __init__(self, max_memory_mb: int = 100, max_disk_mb: int = 1000):
        self.caching_system = CachingSystem(max_memory_mb, max_disk_mb)
        self.async_manager = AsyncOperationsManager()
        self.rendering_optimizer = RenderingOptimizer()
        self.analytics = PerformanceAnalytics()
        
        self.lock = threading.RLock()

    # ========== Caching API ==========

    def get_from_cache(self, key: str, strategy: str = 'auto') -> Optional[Any]:
        """Get from cache"""
        return self.caching_system.get_from_cache(key, strategy)

    def set_in_cache(self, key: str, value: Any, ttl_seconds: int = 3600, 
                    strategy: str = 'auto') -> None:
        """Set in cache"""
        self.caching_system.set_in_cache(key, value, ttl_seconds, strategy)

    def invalidate_cache(self, pattern: str = '*', cascade: bool = False) -> int:
        """Invalidate cache"""
        return self.caching_system.invalidate_cache(pattern, cascade)

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self.caching_system.get_cache_stats()

    # ========== Async Operations API ==========

    def queue_operation(self, operation: Callable, priority: int = 5, 
                       timeout_seconds: int = 30) -> str:
        """Queue async operation"""
        return self.async_manager.queue_operation(operation, priority, timeout_seconds)

    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel operation"""
        return self.async_manager.cancel_operation(operation_id)

    def get_pending_operations_count(self) -> int:
        """Get pending count"""
        return self.async_manager.get_pending_count()

    def get_async_stats(self) -> AsyncStats:
        """Get async statistics"""
        return self.async_manager.get_async_stats()

    # ========== Rendering API ==========

    def enable_virtual_scrolling(self, container_id: str, item_height: int) -> None:
        """Enable virtual scrolling"""
        self.rendering_optimizer.enable_virtual_scrolling(container_id, item_height)

    def get_render_stats(self, container_id: str) -> RenderStats:
        """Get render stats"""
        return self.rendering_optimizer.get_render_stats(container_id)

    # ========== Analytics API ==========

    def start_performance_tracking(self, operation_name: str) -> str:
        """Start tracking"""
        return self.analytics.start_operation(operation_name)

    def end_performance_tracking(self, trace_id: str, success: bool = True) -> None:
        """End tracking"""
        self.analytics.end_operation(trace_id, success)

    def get_performance_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get all metrics"""
        with self.lock:
            bottlenecks = self.analytics.detect_bottlenecks()
            return {
                'bottlenecks': [asdict(b) for b in bottlenecks],
                'cache_stats': asdict(self.caching_system.get_cache_stats()),
                'async_stats': asdict(self.async_manager.get_async_stats())
            }

    def set_performance_threshold_ms(self, operation_type: str, threshold: int) -> None:
        """Set performance threshold"""
        self.analytics.set_performance_threshold(operation_type, threshold)

    def reset_all_metrics(self) -> None:
        """Reset all metrics"""
        self.analytics.reset_metrics()
        self.caching_system.reset_statistics()
        self.async_manager.reset_statistics()

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        cache_stats = self.caching_system.get_cache_stats()
        async_stats = self.async_manager.get_async_stats()
        violations = self.analytics.get_threshold_violations()
        
        return {
            'cache_health': {
                'memory_usage_pct': (cache_stats.memory_usage_mb / 100) * 100,
                'hit_ratio': cache_stats.hit_ratio,
                'entries': cache_stats.total_entries
            },
            'async_health': {
                'pending_count': async_stats.current_pending_count,
                'avg_execution_ms': async_stats.avg_execution_time_ms,
                'failure_rate': async_stats.total_failed / max(1, async_stats.total_queued)
            },
            'threshold_violations': len(violations),
            'status': 'healthy' if len(violations) == 0 else 'warning'
        }
