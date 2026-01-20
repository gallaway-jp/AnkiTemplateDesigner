/**
 * Canvas Rendering Optimization Service - Phase 5
 * Virtual scrolling, memoization, batched updates, and performance metrics
 */

import { CraftNode } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Performance metrics for canvas rendering
 */
export interface PerformanceMetrics {
  frameTime: number; // ms per frame
  fps: number; // frames per second
  nodeRenderTime: number; // ms to render all nodes
  selectionRenderTime: number; // ms to render selection
  previewRenderTime: number; // ms to render preview
  memoryUsage: number; // bytes
  nodeCount: number; // total nodes rendered
  visibleNodeCount: number; // visible nodes only
}

/**
 * Virtual scroll viewport information
 */
export interface VirtualViewport {
  startIndex: number;
  endIndex: number;
  visibleCount: number;
  totalCount: number;
  itemHeight: number;
  scrollOffset: number;
  viewportHeight: number;
}

/**
 * Node render cache entry
 */
export interface CachedNodeRender {
  html: string;
  timestamp: number;
  hash: string; // hash of node data to detect changes
  size: number; // bytes
}

/**
 * Batch update operation
 */
export interface BatchUpdate {
  nodeId: string;
  property: string;
  value: any;
  timestamp: number;
}

/**
 * Render performance profile
 */
export interface RenderProfile {
  operation: string;
  startTime: number;
  endTime: number;
  duration: number;
  nodeCount: number;
  allocatedMemory: number;
}

// ============================================================================
// Performance Monitoring
// ============================================================================

class PerformanceMonitor {
  private frameCount = 0;
  private lastFrameTime = 0;
  private frameTimeSamples: number[] = [];
  private renderProfiles: RenderProfile[] = [];
  private readonly sampleSize = 60; // samples for FPS calculation

  recordFrame(frameTime: number) {
    this.frameTimeSamples.push(frameTime);
    if (this.frameTimeSamples.length > this.sampleSize) {
      this.frameTimeSamples.shift();
    }
    this.lastFrameTime = frameTime;
  }

  getAverageFPS(): number {
    if (this.frameTimeSamples.length === 0) return 0;
    const avgFrameTime = this.frameTimeSamples.reduce((a, b) => a + b, 0) / this.frameTimeSamples.length;
    return Math.round(1000 / avgFrameTime);
  }

  recordProfile(profile: RenderProfile) {
    this.renderProfiles.push(profile);
    if (this.renderProfiles.length > 100) {
      this.renderProfiles.shift();
    }
  }

  getMetrics(nodeCount: number, visibleNodeCount: number): PerformanceMetrics {
    const avgFrameTime = this.frameTimeSamples.length > 0
      ? this.frameTimeSamples.reduce((a, b) => a + b, 0) / this.frameTimeSamples.length
      : 0;

    const fps = avgFrameTime > 0 ? 1000 / avgFrameTime : 0;

    const nodeRenderTime = this.renderProfiles
      .filter(p => p.operation.includes('renderNode'))
      .reduce((sum, p) => sum + p.duration, 0) / Math.max(this.renderProfiles.filter(p => p.operation.includes('renderNode')).length, 1);

    return {
      frameTime: Math.round(avgFrameTime * 100) / 100,
      fps: Math.round(fps),
      nodeRenderTime: Math.round(nodeRenderTime * 100) / 100,
      selectionRenderTime: 0,
      previewRenderTime: 0,
      memoryUsage: (performance.memory?.usedJSHeapSize || 0),
      nodeCount,
      visibleNodeCount,
    };
  }

  reset() {
    this.frameTimeSamples = [];
    this.renderProfiles = [];
  }
}

// ============================================================================
// Render Cache
// ============================================================================

class RenderCache {
  private cache = new Map<string, CachedNodeRender>();
  private readonly maxSize = 1000; // max cache entries
  private readonly ttl = 5 * 60 * 1000; // 5 minute TTL

  set(nodeId: string, html: string, hash: string): void {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(nodeId, {
      html,
      timestamp: Date.now(),
      hash,
      size: html.length,
    });
  }

  get(nodeId: string, currentHash: string): string | null {
    const cached = this.cache.get(nodeId);
    if (!cached) return null;

    // Check TTL
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(nodeId);
      return null;
    }

    // Check if node data changed
    if (cached.hash !== currentHash) {
      this.cache.delete(nodeId);
      return null;
    }

    return cached.html;
  }

  invalidate(nodeId: string): void {
    this.cache.delete(nodeId);
  }

  invalidatePattern(pattern: (id: string) => boolean): void {
    for (const key of this.cache.keys()) {
      if (pattern(key)) {
        this.cache.delete(key);
      }
    }
  }

  clear(): void {
    this.cache.clear();
  }

  getSize(): number {
    let totalSize = 0;
    for (const cached of this.cache.values()) {
      totalSize += cached.size;
    }
    return totalSize;
  }

  getStats() {
    return {
      entries: this.cache.size,
      totalSize: this.getSize(),
      maxSize: this.maxSize,
      utilizationPercent: Math.round((this.cache.size / this.maxSize) * 100),
    };
  }
}

// ============================================================================
// Virtual Scrolling
// ============================================================================

/**
 * Virtual scroll manager for rendering large lists efficiently
 * Only renders visible items in viewport
 */
export class VirtualScroller {
  private flattenedNodes: CraftNode[] = [];
  private indexMap = new Map<string, number>();

  /**
   * Flatten node tree into array for virtual scrolling
   */
  flattenTree(root: CraftNode, maxDepth = 10): CraftNode[] {
    const result: CraftNode[] = [];
    const queue: { node: CraftNode; depth: number }[] = [{ node: root, depth: 0 }];

    while (queue.length > 0) {
      const { node, depth } = queue.shift()!;

      if (depth > maxDepth) continue;

      result.push(node);
      this.indexMap.set(node.id, result.length - 1);

      // Add children in reverse order for correct queue processing
      const children = Object.values(node.nodes);
      for (let i = children.length - 1; i >= 0; i--) {
        queue.unshift({ node: children[i], depth: depth + 1 });
      }
    }

    this.flattenedNodes = result;
    return result;
  }

  /**
   * Calculate visible range for virtual scrolling
   */
  getVisibleRange(scrollOffset: number, viewportHeight: number, itemHeight: number): VirtualViewport {
    const totalCount = this.flattenedNodes.length;
    const visibleCount = Math.ceil(viewportHeight / itemHeight) + 2; // +2 for buffer

    let startIndex = Math.max(0, Math.floor(scrollOffset / itemHeight));
    let endIndex = Math.min(totalCount, startIndex + visibleCount);

    // Ensure at least some visible items
    if (endIndex - startIndex < visibleCount / 2) {
      startIndex = Math.max(0, endIndex - visibleCount);
    }

    return {
      startIndex,
      endIndex,
      visibleCount,
      totalCount,
      itemHeight,
      scrollOffset,
      viewportHeight,
    };
  }

  /**
   * Get visible nodes only
   */
  getVisibleNodes(viewport: VirtualViewport): CraftNode[] {
    return this.flattenedNodes.slice(viewport.startIndex, viewport.endIndex);
  }

  /**
   * Get node at specific index
   */
  getNodeAt(index: number): CraftNode | null {
    return this.flattenedNodes[index] || null;
  }

  /**
   * Find index of node by ID
   */
  getIndexOfNode(nodeId: string): number {
    return this.indexMap.get(nodeId) ?? -1;
  }

  /**
   * Clear flattened tree
   */
  reset(): void {
    this.flattenedNodes = [];
    this.indexMap.clear();
  }
}

// ============================================================================
// Batch Update Manager
// ============================================================================

/**
 * Batch multiple property updates for efficient processing
 */
export class BatchUpdateManager {
  private updates: BatchUpdate[] = [];
  private timeout: NodeJS.Timeout | null = null;
  private readonly batchDelay = 16; // ~60 FPS

  /**
   * Queue an update
   */
  queueUpdate(nodeId: string, property: string, value: any): void {
    // Remove previous update to same property on same node
    this.updates = this.updates.filter(
      u => !(u.nodeId === nodeId && u.property === property)
    );

    this.updates.push({
      nodeId,
      property,
      value,
      timestamp: Date.now(),
    });

    this.scheduleBatch();
  }

  /**
   * Schedule batch processing
   */
  private scheduleBatch(): void {
    if (this.timeout) return;

    this.timeout = setTimeout(() => {
      this.processBatch();
      this.timeout = null;
    }, this.batchDelay);
  }

  /**
   * Process all queued updates
   */
  private processBatch(): void {
    if (this.updates.length === 0) return;

    logger.debug(`[CanvasOptimization] Processing batch of ${this.updates.length} updates`);

    // Group updates by node
    const byNode = new Map<string, BatchUpdate[]>();
    for (const update of this.updates) {
      if (!byNode.has(update.nodeId)) {
        byNode.set(update.nodeId, []);
      }
      byNode.get(update.nodeId)!.push(update);
    }

    // Emit batch event or callback
    const batchData = Object.fromEntries(byNode);
    this.onBatchReady?.(batchData);

    this.updates = [];
  }

  /**
   * Force process pending updates
   */
  flush(): void {
    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
    this.processBatch();
  }

  /**
   * Get pending update count
   */
  getPendingCount(): number {
    return this.updates.length;
  }

  /**
   * Callback when batch is ready
   */
  onBatchReady?: (batch: Record<string, BatchUpdate[]>) => void;
}

// ============================================================================
// Node Hash/Memoization
// ============================================================================

/**
 * Generate hash for node to detect changes
 */
export function generateNodeHash(node: CraftNode): string {
  const data = {
    id: node.id,
    type: node.type,
    props: node.props,
    childCount: Object.keys(node.nodes).length,
    hidden: node.hidden,
  };

  // Simple hash using JSON stringification
  const json = JSON.stringify(data);
  let hash = 0;
  for (let i = 0; i < json.length; i++) {
    const char = json.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
}

/**
 * Memoized node properties
 */
export function memoizeNodeRender(node: CraftNode, renderFn: (node: CraftNode) => string): string {
  const hash = generateNodeHash(node);
  // This should be connected to RenderCache in actual implementation
  return renderFn(node);
}

// ============================================================================
// Debounce/Throttle Utilities
// ============================================================================

/**
 * Debounce function - execute after delay of inactivity
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => {
      fn(...args);
      timeout = null;
    }, delay);
  };
}

/**
 * Throttle function - execute at most once per interval
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  interval: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;

  return function executedFunction(...args: Parameters<T>) {
    const now = Date.now();
    if (now - lastCall >= interval) {
      fn(...args);
      lastCall = now;
    }
  };
}

/**
 * Request animation frame throttle - execute once per frame
 */
export function rafThrottle<T extends (...args: any[]) => any>(
  fn: T
): (...args: Parameters<T>) => void {
  let frameId: number | null = null;

  return function executedFunction(...args: Parameters<T>) {
    if (frameId !== null) return;

    frameId = requestAnimationFrame(() => {
      fn(...args);
      frameId = null;
    });
  };
}

// ============================================================================
// Main Optimization Service
// ============================================================================

export class CanvasOptimizationService {
  private monitor = new PerformanceMonitor();
  private cache = new RenderCache();
  private scroller = new VirtualScroller();
  private batchManager = new BatchUpdateManager();

  /**
   * Initialize optimization service
   */
  initialize(): void {
    logger.info('[CanvasOptimization] Service initialized');
    this.monitor.reset();
    this.cache.clear();
    this.scroller.reset();
  }

  /**
   * Start performance monitoring frame
   */
  startFrame(): number {
    return performance.now();
  }

  /**
   * End performance monitoring frame
   */
  endFrame(startTime: number): PerformanceMetrics {
    const frameTime = performance.now() - startTime;
    this.monitor.recordFrame(frameTime);

    if (frameTime > 16) {
      logger.warn(`[CanvasOptimization] Frame took ${frameTime.toFixed(2)}ms (exceeds 16ms budget)`);
    }

    return this.getMetrics(0, 0); // Will be updated with actual counts
  }

  /**
   * Get current performance metrics
   */
  getMetrics(nodeCount: number, visibleNodeCount: number): PerformanceMetrics {
    return this.monitor.getMetrics(nodeCount, visibleNodeCount);
  }

  /**
   * Cache node render result
   */
  cacheRender(nodeId: string, html: string, node: CraftNode): void {
    const hash = generateNodeHash(node);
    this.cache.set(nodeId, html, hash);
  }

  /**
   * Get cached render if available and current
   */
  getCachedRender(nodeId: string, node: CraftNode): string | null {
    const hash = generateNodeHash(node);
    return this.cache.get(nodeId, hash);
  }

  /**
   * Invalidate cache for node and children
   */
  invalidateCache(nodeId: string, node: CraftNode): void {
    this.cache.invalidate(nodeId);
    // Invalidate all children
    this.cache.invalidatePattern(id => id.startsWith(nodeId));
  }

  /**
   * Get render cache statistics
   */
  getCacheStats() {
    return this.cache.getStats();
  }

  /**
   * Setup virtual scrolling
   */
  setupVirtualScroll(root: CraftNode): VirtualScroller {
    this.scroller.flattenTree(root);
    return this.scroller;
  }

  /**
   * Get visible range for virtual scrolling
   */
  getVisibleRange(scrollOffset: number, viewportHeight: number, itemHeight: number): VirtualViewport {
    return this.scroller.getVisibleRange(scrollOffset, viewportHeight, itemHeight);
  }

  /**
   * Get visible nodes
   */
  getVisibleNodes(viewport: VirtualViewport): CraftNode[] {
    return this.scroller.getVisibleNodes(viewport);
  }

  /**
   * Queue property update for batching
   */
  queueUpdate(nodeId: string, property: string, value: any): void {
    this.batchManager.queueUpdate(nodeId, property, value);
  }

  /**
   * Process all pending updates
   */
  flushUpdates(): void {
    this.batchManager.flush();
  }

  /**
   * Get pending update count
   */
  getPendingUpdateCount(): number {
    return this.batchManager.getPendingCount();
  }

  /**
   * Set batch ready callback
   */
  onBatchReady(callback: (batch: Record<string, any>) => void): void {
    this.batchManager.onBatchReady = callback;
  }

  /**
   * Record render profile
   */
  recordProfile(operation: string, duration: number, nodeCount: number): void {
    this.monitor.recordProfile({
      operation,
      startTime: 0,
      endTime: 0,
      duration,
      nodeCount,
      allocatedMemory: performance.memory?.usedJSHeapSize || 0,
    });
  }

  /**
   * Get optimization health check
   */
  getHealthCheck() {
    const metrics = this.monitor.getMetrics(0, 0);
    const cacheStats = this.cache.getStats();

    return {
      fps: metrics.fps,
      targetFps: 60,
      fpsOk: metrics.fps >= 55,
      frameTime: metrics.frameTime,
      frameTimeBudget: 16,
      frameTimeOk: metrics.frameTime <= 16,
      cache: cacheStats,
      cacheOk: cacheStats.utilizationPercent < 80,
      pendingUpdates: this.batchManager.getPendingCount(),
      pendingUpdatesOk: this.batchManager.getPendingCount() < 100,
    };
  }

  /**
   * Reset optimization state
   */
  reset(): void {
    this.monitor.reset();
    this.cache.clear();
    this.scroller.reset();
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const canvasOptimization = new CanvasOptimizationService();

// Default export
export default canvasOptimization;
