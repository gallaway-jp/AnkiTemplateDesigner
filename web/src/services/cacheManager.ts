/**
 * Cache Manager - Pluggable caching strategies
 * Supports LRU, TTL, and custom cache implementations
 */

/**
 * Cache strategy interface
 * Implement this to create custom cache strategies
 */
export interface CacheStrategy<K, V> {
  get(key: K): V | undefined;
  set(key: K, value: V, ttl?: number): void;
  remove(key: K): void;
  clear(): void;
  has(key: K): boolean;
  size(): number;
}

/**
 * LRU (Least Recently Used) Cache Strategy
 * Evicts least recently used item when max size exceeded
 */
export class LRUCacheStrategy<K, V> implements CacheStrategy<K, V> {
  private cache: Map<K, V> = new Map();

  constructor(private maxSize: number = 100) {
    if (maxSize <= 0) {
      throw new Error('maxSize must be greater than 0');
    }
  }

  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }
    // Move to end (most recently used)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  set(key: K, value: V): void {
    // Remove if exists
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    // Evict LRU if at capacity
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }

  remove(key: K): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  has(key: K): boolean {
    return this.cache.has(key);
  }

  size(): number {
    return this.cache.size;
  }

  /**
   * Get all entries (for debugging)
   */
  getEntries(): Array<[K, V]> {
    return Array.from(this.cache.entries());
  }
}

/**
 * TTL (Time-To-Live) Cache Strategy
 * Automatically expires entries after specified TTL
 */
export class TTLCacheStrategy<K, V> implements CacheStrategy<K, V> {
  private cache: Map<K, { value: V; expiry: number }> = new Map();
  private timers: Map<K, NodeJS.Timeout> = new Map();

  constructor(private defaultTtlMs: number = 60000) {
    if (defaultTtlMs <= 0) {
      throw new Error('defaultTtlMs must be greater than 0');
    }
  }

  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    if (!entry) {
      return undefined;
    }

    if (entry.expiry < Date.now()) {
      this.remove(key);
      return undefined;
    }

    return entry.value;
  }

  set(key: K, value: V, ttl?: number): void {
    // Clear existing timer
    const existingTimer = this.timers.get(key);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    const ttlMs = ttl ?? this.defaultTtlMs;
    const expiry = Date.now() + ttlMs;

    this.cache.set(key, { value, expiry });

    // Set expiry timer
    const timer = setTimeout(() => {
      this.remove(key);
    }, ttlMs);

    this.timers.set(key, timer);
  }

  remove(key: K): void {
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
    }
    this.cache.delete(key);
  }

  clear(): void {
    this.timers.forEach((timer) => clearTimeout(timer));
    this.timers.clear();
    this.cache.clear();
  }

  has(key: K): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }
    if (entry.expiry < Date.now()) {
      this.remove(key);
      return false;
    }
    return true;
  }

  size(): number {
    // Count non-expired entries
    let count = 0;
    this.cache.forEach((entry, key) => {
      if (entry.expiry >= Date.now()) {
        count++;
      } else {
        this.remove(key);
      }
    });
    return count;
  }
}

/**
 * Hybrid Cache Strategy
 * Combines LRU with TTL expiration
 */
export class HybridCacheStrategy<K, V> implements CacheStrategy<K, V> {
  private cache: Map<K, { value: V; expiry: number }> = new Map();
  private timers: Map<K, NodeJS.Timeout> = new Map();
  private lru: K[] = [];

  constructor(
    private maxSize: number = 100,
    private defaultTtlMs: number = 60000
  ) {
    if (maxSize <= 0) {
      throw new Error('maxSize must be greater than 0');
    }
    if (defaultTtlMs <= 0) {
      throw new Error('defaultTtlMs must be greater than 0');
    }
  }

  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    if (!entry) {
      return undefined;
    }

    if (entry.expiry < Date.now()) {
      this.remove(key);
      return undefined;
    }

    // Update LRU order
    const index = this.lru.indexOf(key);
    if (index !== -1) {
      this.lru.splice(index, 1);
    }
    this.lru.push(key);

    return entry.value;
  }

  set(key: K, value: V, ttl?: number): void {
    const ttlMs = ttl ?? this.defaultTtlMs;
    const expiry = Date.now() + ttlMs;

    // Clear existing timer
    const existingTimer = this.timers.get(key);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Update LRU
    const index = this.lru.indexOf(key);
    if (index !== -1) {
      this.lru.splice(index, 1);
    }
    this.lru.push(key);

    // Evict LRU if at capacity
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const lruKey = this.lru.shift();
      if (lruKey) {
        this.remove(lruKey);
      }
    }

    this.cache.set(key, { value, expiry });

    // Set expiry timer
    const timer = setTimeout(() => {
      this.remove(key);
    }, ttlMs);

    this.timers.set(key, timer);
  }

  remove(key: K): void {
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
    }
    this.cache.delete(key);
    const index = this.lru.indexOf(key);
    if (index !== -1) {
      this.lru.splice(index, 1);
    }
  }

  clear(): void {
    this.timers.forEach((timer) => clearTimeout(timer));
    this.timers.clear();
    this.cache.clear();
    this.lru = [];
  }

  has(key: K): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }
    if (entry.expiry < Date.now()) {
      this.remove(key);
      return false;
    }
    return true;
  }

  size(): number {
    return this.cache.size;
  }
}

/**
 * Simple in-memory cache strategy
 * No size limits or TTL
 */
export class SimpleMemoryCacheStrategy<K, V>
  implements CacheStrategy<K, V>
{
  private cache: Map<K, V> = new Map();

  get(key: K): V | undefined {
    return this.cache.get(key);
  }

  set(key: K, value: V): void {
    this.cache.set(key, value);
  }

  remove(key: K): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  has(key: K): boolean {
    return this.cache.has(key);
  }

  size(): number {
    return this.cache.size;
  }
}

/**
 * Cache Manager
 * Manages multiple cache strategies
 */
export class CacheManager {
  private strategies: Map<string, CacheStrategy<any, any>> = new Map();

  /**
   * Register a cache strategy
   */
  register<K, V>(
    name: string,
    strategy: CacheStrategy<K, V>
  ): void {
    this.strategies.set(name, strategy);
  }

  /**
   * Get a cache strategy
   */
  get<K, V>(name: string): CacheStrategy<K, V> {
    const strategy = this.strategies.get(name);
    if (!strategy) {
      throw new Error(`Cache strategy '${name}' not registered`);
    }
    return strategy as CacheStrategy<K, V>;
  }

  /**
   * Check if strategy exists
   */
  has(name: string): boolean {
    return this.strategies.has(name);
  }

  /**
   * Remove a cache strategy
   */
  unregister(name: string): void {
    const strategy = this.strategies.get(name);
    if (strategy) {
      strategy.clear();
    }
    this.strategies.delete(name);
  }

  /**
   * Get list of registered cache names
   */
  getStrategyNames(): string[] {
    return Array.from(this.strategies.keys());
  }

  /**
   * Clear all caches
   */
  clearAll(): void {
    this.strategies.forEach((strategy) => strategy.clear());
  }

  /**
   * Destroy all caches
   */
  destroy(): void {
    this.clearAll();
    this.strategies.clear();
  }
}

// Global instance
export const cacheManager = new CacheManager();
