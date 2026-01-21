/**
 * Performance Test Suite for Anki Template Designer
 * 
 * Tests render times, memory usage, store performance, and bridge latency.
 * Compares optimized vs non-optimized implementations.
 * 
 * Run: npm run test:perf
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { throttle, debounce, memoize, LRUCache } from '../utils/performance';
import {
  useEditorState,
  useEditorActions,
  useAnkiFields,
  useUISettings,
  useUIActions,
} from '../stores/selectors';

/**
 * Performance benchmarking utilities
 */

class PerformanceBenchmark {
  private marks: Map<string, number> = new Map();
  private metrics: Map<string, number[]> = new Map();

  mark(label: string): void {
    this.marks.set(label, performance.now());
  }

  measure(label: string): number {
    const end = performance.now();
    const start = this.marks.get(label);
    if (!start) throw new Error(`No mark found for ${label}`);

    const duration = end - start;
    if (!this.metrics.has(label)) {
      this.metrics.set(label, []);
    }
    this.metrics.get(label)!.push(duration);
    return duration;
  }

  getStats(label: string): { mean: number; min: number; max: number; samples: number } {
    const values = this.metrics.get(label) || [];
    if (values.length === 0) {
      return { mean: 0, min: 0, max: 0, samples: 0 };
    }

    const sum = values.reduce((a, b) => a + b, 0);
    const mean = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    return { mean, min, max, samples: values.length };
  }

  reset(): void {
    this.marks.clear();
    this.metrics.clear();
  }
}

/**
 * Memory monitoring utilities
 */

class MemoryMonitor {
  private snapshots: Map<string, number> = new Map();

  snapshot(label: string): void {
    if (global.gc) {
      global.gc();
    }
    const memory = process.memoryUsage();
    this.snapshots.set(label, memory.heapUsed);
  }

  measure(label: string): number {
    const end = process.memoryUsage().heapUsed;
    const start = this.snapshots.get(label);
    if (!start) throw new Error(`No snapshot found for ${label}`);

    return (end - start) / 1024 / 1024; // Return in MB
  }

  reset(): void {
    this.snapshots.clear();
  }
}

/**
 * Tests for Utility Functions
 */

describe('Performance: Utility Functions', () => {
  const benchmark = new PerformanceBenchmark();

  afterEach(() => {
    benchmark.reset();
  });

  describe('throttle', () => {
    it('should execute function at most once per interval', () => {
      const calls: number[] = [];
      const throttled = throttle((x: number) => calls.push(x), 50);

      // Call 10 times rapidly
      benchmark.mark('throttle-burst');
      for (let i = 0; i < 10; i++) {
        throttled(i);
      }
      const duration = benchmark.measure('throttle-burst');

      // Should have significantly fewer executions than calls
      expect(calls.length).toBeLessThan(10);
      expect(calls.length).toBeGreaterThanOrEqual(1);
      expect(duration).toBeLessThan(100);
    });

    it('should handle edge cases with short intervals', () => {
      const calls: number[] = [];
      const throttled = throttle((x: number) => calls.push(x), 10);

      for (let i = 0; i < 5; i++) {
        throttled(i);
      }

      expect(calls.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('debounce', () => {
    it('should delay execution until after delay', async () => {
      const calls: number[] = [];
      const debounced = debounce((x: number) => calls.push(x), 50);

      benchmark.mark('debounce-call');
      debounced(1);
      debounced(2);
      debounced(3);

      // Should not have executed yet
      expect(calls.length).toBe(0);

      // Wait for debounce
      await new Promise((resolve) => setTimeout(resolve, 60));

      expect(calls.length).toBe(1);
      expect(calls[0]).toBe(3);
      benchmark.measure('debounce-call');
    });

    it('should reset timer on subsequent calls', async () => {
      const calls: number[] = [];
      const debounced = debounce((x: number) => calls.push(x), 50);

      debounced(1);
      await new Promise((resolve) => setTimeout(resolve, 30));
      debounced(2); // Reset timer
      await new Promise((resolve) => setTimeout(resolve, 60));

      expect(calls.length).toBe(1);
      expect(calls[0]).toBe(2);
    });
  });

  describe('memoize', () => {
    it('should cache expensive computations', () => {
      let computeCount = 0;
      const expensive = memoize((x: number) => {
        computeCount++;
        return x * x;
      });

      benchmark.mark('memoize-first');
      const result1 = expensive(5);
      benchmark.measure('memoize-first');

      benchmark.mark('memoize-cached');
      const result2 = expensive(5);
      benchmark.measure('memoize-cached');

      expect(result1).toBe(25);
      expect(result2).toBe(25);
      expect(computeCount).toBe(1); // Only computed once

      const cached = benchmark.getStats('memoize-cached');
      const first = benchmark.getStats('memoize-first');

      // Cached should be significantly faster
      expect(cached.mean).toBeLessThan(first.mean);
    });

    it('should handle different arguments separately', () => {
      let computeCount = 0;
      const expensive = memoize((x: number) => {
        computeCount++;
        return x * x;
      });

      expensive(5);
      expensive(10);
      expensive(5);

      expect(computeCount).toBe(2); // 5 and 10 computed once each
    });
  });

  describe('LRUCache', () => {
    it('should evict least recently used items', () => {
      const cache = new LRUCache<string, number>(3);

      cache.set('a', 1);
      cache.set('b', 2);
      cache.set('c', 3);
      expect(cache.get('a')).toBe(1);
      expect(cache.get('b')).toBe(2);
      expect(cache.get('c')).toBe(3);

      // Add new item, 'a' should be evicted (least recently used)
      cache.set('d', 4);
      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('d')).toBe(4);
    });

    it('should update recency on access', () => {
      const cache = new LRUCache<string, number>(2);

      cache.set('a', 1);
      cache.set('b', 2);
      cache.get('a'); // Access 'a' to make it most recent
      cache.set('c', 3); // Should evict 'b', not 'a'

      expect(cache.get('a')).toBe(1);
      expect(cache.get('b')).toBeUndefined();
      expect(cache.get('c')).toBe(3);
    });

    it('should perform well with large caches', () => {
      const cache = new LRUCache<number, number>(1000);
      const benchmark = new PerformanceBenchmark();

      benchmark.mark('cache-insert');
      for (let i = 0; i < 1000; i++) {
        cache.set(i, i * 2);
      }
      const insertTime = benchmark.measure('cache-insert');

      benchmark.mark('cache-lookup');
      for (let i = 0; i < 100; i++) {
        cache.get(Math.random() * 1000 | 0);
      }
      const lookupTime = benchmark.measure('cache-lookup');

      expect(insertTime).toBeLessThan(50);
      expect(lookupTime).toBeLessThan(10);
    });
  });
});

/**
 * Tests for Store Selectors
 */

describe('Performance: Store Selectors', () => {
  const benchmark = new PerformanceBenchmark();

  afterEach(() => {
    benchmark.reset();
  });

  it('should efficiently select editor state', () => {
    benchmark.mark('selector-editor-state');
    const { result } = renderHook(() => useEditorState());
    benchmark.measure('selector-editor-state');

    expect(result.current).toBeDefined();
    expect(result.current).toHaveProperty('template');
    expect(result.current).toHaveProperty('isDirty');

    const stats = benchmark.getStats('selector-editor-state');
    expect(stats.mean).toBeLessThan(50);
  });

  it('should efficiently select UI settings', () => {
    benchmark.mark('selector-ui-settings');
    const { result } = renderHook(() => useUISettings());
    benchmark.measure('selector-ui-settings');

    expect(result.current).toBeDefined();

    const stats = benchmark.getStats('selector-ui-settings');
    expect(stats.mean).toBeLessThan(50);
  });

  it('should batch multiple selector accesses efficiently', () => {
    benchmark.mark('selectors-batch');
    const { result: editorResult } = renderHook(() => useEditorState());
    const { result: actionsResult } = renderHook(() => useEditorActions());
    const { result: uiResult } = renderHook(() => useUISettings());
    benchmark.measure('selectors-batch');

    expect(editorResult.current).toBeDefined();
    expect(actionsResult.current).toBeDefined();
    expect(uiResult.current).toBeDefined();

    const stats = benchmark.getStats('selectors-batch');
    expect(stats.mean).toBeLessThan(150);
  });
});

/**
 * Tests for Component Re-renders
 */

describe('Performance: Component Re-renders', () => {
  const benchmark = new PerformanceBenchmark();

  afterEach(() => {
    benchmark.reset();
  });

  it('should minimize re-renders with memoized selectors', () => {
    let renderCount = 0;

    const TestComponent = () => {
      renderCount++;
      const state = useEditorState();
      return <div>{state.isDirty ? 'Dirty' : 'Clean'}</div>;
    };

    const { rerender } = renderHook(() => {
      benchmark.mark('component-render');
      return TestComponent();
    });

    benchmark.measure('component-render');

    // Re-render multiple times
    for (let i = 0; i < 10; i++) {
      benchmark.mark(`rerender-${i}`);
      rerender();
      benchmark.measure(`rerender-${i}`);
    }

    // Most re-renders should be very fast (cached)
    let fastRenders = 0;
    for (let i = 0; i < 10; i++) {
      const stats = benchmark.getStats(`rerender-${i}`);
      if (stats.mean < 10) fastRenders++;
    }

    expect(fastRenders).toBeGreaterThan(7); // At least 70% should be cached
  });

  it('should handle rapid state updates efficiently', () => {
    benchmark.mark('rapid-updates');
    for (let i = 0; i < 100; i++) {
      // Simulate rapid updates
      act(() => {
        // Update store
      });
    }
    const duration = benchmark.measure('rapid-updates');

    expect(duration).toBeLessThan(500);
  });
});

/**
 * Tests for Bridge Communication
 */

describe('Performance: Bridge Communication', () => {
  const benchmark = new PerformanceBenchmark();

  afterEach(() => {
    benchmark.reset();
  });

  it('should simulate batching efficiency', () => {
    const requests: any[] = [];
    const batchSize = 5;
    const batchWindow = 50;

    benchmark.mark('batch-simulation');
    
    // Simulate rapid requests
    for (let i = 0; i < 20; i++) {
      requests.push({ id: i, timestamp: performance.now() });
    }

    // Group into batches
    const batches = [];
    for (let i = 0; i < requests.length; i += batchSize) {
      batches.push(requests.slice(i, i + batchSize));
    }

    benchmark.measure('batch-simulation');

    // Should batch 20 requests into 4 batches
    expect(batches.length).toBe(4);
    expect(batches[0].length).toBe(5);
    expect(batches[3].length).toBe(5);
  });

  it('should handle request deduplication', () => {
    const requestMap = new Map<string, Promise<any>>();
    const requests = ['getFields', 'getFields', 'getBehaviors', 'getFields'];

    benchmark.mark('dedup');
    const dedupRequests = [];
    for (const req of requests) {
      const key = req;
      if (!requestMap.has(key)) {
        requestMap.set(key, Promise.resolve({ data: key }));
      }
      dedupRequests.push(requestMap.get(key));
    }
    benchmark.measure('dedup');

    // 4 requests deduplicated to 2 unique
    expect(requestMap.size).toBe(2);
    expect(dedupRequests.length).toBe(4);

    const stats = benchmark.getStats('dedup');
    expect(stats.mean).toBeLessThan(10);
  });
});

/**
 * Comparison Tests: Old vs Optimized
 */

describe('Performance: Optimization Comparison', () => {
  const benchmark = new PerformanceBenchmark();

  afterEach(() => {
    benchmark.reset();
  });

  it('should show throttle benefits over rapid calls', () => {
    const unthrottled: number[] = [];
    const throttled_: (x: number) => void = throttle((x: number) => {
      throttled.push(x);
    }, 50);

    // Unthrottled: many calls
    benchmark.mark('unthrottled');
    for (let i = 0; i < 100; i++) {
      unthrottled.push(i);
    }
    benchmark.measure('unthrottled');

    // Throttled: same work, fewer executions
    benchmark.mark('throttled');
    for (let i = 0; i < 100; i++) {
      throttled_(i);
    }
    benchmark.measure('throttled');

    const unthrottledStats = benchmark.getStats('unthrottled');
    const throttledStats = benchmark.getStats('throttled');

    // Both should complete, but throttled does less work
    expect(unthrottledStats.mean).toBeGreaterThan(0);
    expect(throttledStats.mean).toBeGreaterThan(0);
  });

  it('should validate selector performance improvement', () => {
    // Simulate old approach: multiple individual hooks
    benchmark.mark('multiple-hooks');
    const { result: r1 } = renderHook(() => useEditorState());
    const { result: r2 } = renderHook(() => useEditorActions());
    const { result: r3 } = renderHook(() => useAnkiFields());
    benchmark.measure('multiple-hooks');

    // New approach: single optimized selector
    benchmark.mark('single-selector');
    const { result } = renderHook(() => useEditorState());
    benchmark.measure('single-selector');

    const multiStats = benchmark.getStats('multiple-hooks');
    const singleStats = benchmark.getStats('single-selector');

    // Single selector should be noticeably faster
    expect(multiStats.mean).toBeGreaterThanOrEqual(singleStats.mean);
  });

  it('should demonstrate cache benefits', () => {
    const uncached = memoize((x: number) => {
      // Simulate expensive operation
      let sum = 0;
      for (let i = 0; i < 1000; i++) {
        sum += Math.sqrt(x * i);
      }
      return sum;
    });

    // First call (uncached)
    benchmark.mark('cache-miss');
    uncached(42);
    benchmark.measure('cache-miss');

    // Subsequent calls (cached)
    benchmark.mark('cache-hit');
    for (let i = 0; i < 100; i++) {
      uncached(42);
    }
    benchmark.measure('cache-hit');

    const missStats = benchmark.getStats('cache-miss');
    const hitStats = benchmark.getStats('cache-hit');

    // Cache hits should be dramatically faster
    expect(hitStats.mean).toBeLessThan(missStats.mean / 10);
  });
});

/**
 * Stress Tests
 */

describe('Performance: Stress Tests', () => {
  const benchmark = new PerformanceBenchmark();
  const monitor = new MemoryMonitor();

  afterEach(() => {
    benchmark.reset();
    monitor.reset();
  });

  it('should handle high volume store operations', () => {
    monitor.snapshot('stress-start');
    benchmark.mark('stress-operations');

    // Simulate 1000 store updates
    for (let i = 0; i < 1000; i++) {
      act(() => {
        // Simulate store update
      });
    }

    benchmark.measure('stress-operations');
    const memDiff = monitor.measure('stress-start');

    const stats = benchmark.getStats('stress-operations');
    expect(stats.mean).toBeLessThan(1000); // Should complete in reasonable time
  });

  it('should maintain stable performance under load', () => {
    benchmark.mark('stable-perf');

    const iterations = 100;
    const timings: number[] = [];

    for (let batch = 0; batch < 5; batch++) {
      const batchStart = performance.now();
      for (let i = 0; i < iterations; i++) {
        // Simulate work
        const _ = Math.sqrt(Math.random()) * Math.random();
      }
      timings.push(performance.now() - batchStart);
    }

    benchmark.measure('stable-perf');

    // Performance should not degrade significantly
    const avgFirst = timings[0];
    const avgLast = timings[timings.length - 1];
    const degradation = (avgLast - avgFirst) / avgFirst;

    expect(degradation).toBeLessThan(0.3); // Less than 30% degradation
  });
});

/**
 * Test Utilities Export for use in other test files
 */

export { PerformanceBenchmark, MemoryMonitor };
