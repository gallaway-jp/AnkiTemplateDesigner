/**
 * Performance Optimization Utilities
 * Throttling, debouncing, memoization helpers for React components
 */

/**
 * Throttle function calls - ensures function is called at most once per delay
 * @param func - Function to throttle
 * @param delay - Minimum milliseconds between calls
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;

    if (timeSinceLastCall >= delay) {
      // Execute immediately if enough time has passed
      func(...args);
      lastCall = now;
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    } else {
      // Schedule for later
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => {
        func(...args);
        lastCall = Date.now();
        timeoutId = null;
      }, delay - timeSinceLastCall);
    }
  };
}

/**
 * Debounce function calls - wait for delay after last call before executing
 * @param func - Function to debounce
 * @param delay - Milliseconds to wait after last call
 * @returns Debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Simple memoization cache for expensive computations
 * @param fn - Function to memoize
 * @param keyGenerator - Function to generate cache key from arguments
 * @returns Memoized function
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyGenerator: (...args: Parameters<T>) => string = JSON.stringify
): T {
  const cache = new Map<string, any>();

  return ((...args: Parameters<T>) => {
    const key = keyGenerator(...args);

    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn(...args);
    cache.set(key, result);

    // Limit cache size
    if (cache.size > 100) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }

    return result;
  }) as T;
}

/**
 * Batch DOM reads to avoid layout thrashing
 * Collects all reads, performs them together, then releases for layout
 */
export class DOMBatchReader {
  private reads: Array<() => any> = [];
  private scheduled = false;

  read<T>(fn: () => T): T {
    let result: T;

    this.reads.push(() => {
      result = fn();
    });

    if (!this.scheduled) {
      this.scheduled = true;
      requestAnimationFrame(() => {
        this.reads.forEach((read) => read());
        this.reads = [];
        this.scheduled = false;
      });
    }

    return result!;
  }
}

/**
 * LRU (Least Recently Used) Cache for expensive computations
 */
export class LRUCache<K, V> {
  private cache = new Map<K, V>();
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.maxSize = maxSize;
  }

  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }

    const value = this.cache.get(key)!;

    // Move to end (most recently used)
    this.cache.delete(key);
    this.cache.set(key, value);

    return value;
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    this.cache.set(key, value);

    // Remove oldest if exceeds max size
    if (this.cache.size > this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

/**
 * Request deduplication cache
 * Prevents duplicate requests from being sent
 */
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();

  async deduplicate<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    // If request is already in flight, return same promise
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!;
    }

    // Create new promise and cache it
    const promise = requestFn().finally(() => {
      // Clean up after request completes
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, promise);

    return promise;
  }

  clear(): void {
    this.pendingRequests.clear();
  }
}

/**
 * Performance profiler for development
 */
export class PerformanceProfiler {
  private marks = new Map<string, number>();

  start(label: string): void {
    this.marks.set(label, performance.now());
  }

  end(label: string): number {
    const startTime = this.marks.get(label);

    if (!startTime) {
      console.warn(`No start mark found for "${label}"`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.marks.delete(label);

    // Log slow operations (>16ms is frame boundary)
    if (duration > 16) {
      console.warn(`[PERF] ${label} took ${duration.toFixed(2)}ms`);
    }

    return duration;
  }

  measure(label: string, fn: () => void): number {
    this.start(label);
    fn();
    return this.end(label);
  }

  async measureAsync<T>(label: string, fn: () => Promise<T>): Promise<T> {
    this.start(label);
    const result = await fn();
    this.end(label);
    return result;
  }
}

/**
 * Weak subscription manager - automatically cleans up with GC
 */
export class WeakSubscriptionManager {
  private subscriptions = new WeakMap<object, Set<Function>>();

  subscribe(target: object, callback: Function): () => void {
    if (!this.subscriptions.has(target)) {
      this.subscriptions.set(target, new Set());
    }

    this.subscriptions.get(target)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.subscriptions.get(target)?.delete(callback);
    };
  }

  emit(target: object, ...args: any[]): void {
    const callbacks = this.subscriptions.get(target);
    if (callbacks) {
      callbacks.forEach((callback) => callback(...args));
    }
  }

  clear(target: object): void {
    if (this.subscriptions.has(target)) {
      this.subscriptions.delete(target);
    }
  }
}

// Export singleton instances
export const domBatchReader = new DOMBatchReader();
export const performanceProfiler = new PerformanceProfiler();
