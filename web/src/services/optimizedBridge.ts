/**
 * Optimized Python Bridge with Request Batching & Deduplication
 * Performance enhancements for Phase 1 optimization
 */

import { RequestDeduplicator, LRUCache } from '@/utils/performance';

/**
 * Batch configuration
 */
interface BatchConfig {
  windowMs: number; // Time window to collect requests
  maxSize: number; // Max requests per batch
  enabled: boolean; // Enable batching
}

/**
 * Batched request container
 */
interface BatchedRequest {
  method: string;
  params: Record<string, any>;
  id: string;
  resolve: (value: any) => void;
  reject: (error: any) => void;
}

/**
 * Extended bridge with batching and deduplication
 */
export class OptimizedPythonBridge {
  private deduplicator = new RequestDeduplicator();
  private requestCache = new LRUCache<string, Promise<any>>(500);

  // Batching configuration
  private batchConfig: BatchConfig = {
    windowMs: 50, // 50ms window for collecting requests
    maxSize: 5, // Max 5 requests per batch
    enabled: true,
  };

  private currentBatch: BatchedRequest[] = [];
  private batchTimer: NodeJS.Timeout | null = null;
  private isBatchProcessing = false;

  /**
   * Send request with automatic batching and deduplication
   */
  async sendRequest(
    method: string,
    params: Record<string, any> = {}
  ): Promise<any> {
    if (!this.batchConfig.enabled) {
      return this.sendDirect(method, params);
    }

    // Create dedup key
    const dedupKey = `${method}:${JSON.stringify(params)}`;

    // Check cache for recent successful requests
    const cached = this.requestCache.get(dedupKey);
    if (cached) {
      return cached;
    }

    // Use deduplicator to prevent duplicate in-flight requests
    const promise = this.deduplicator.deduplicate(dedupKey, async () => {
      return new Promise<any>((resolve, reject) => {
        const request: BatchedRequest = {
          method,
          params,
          id: this.generateId(),
          resolve,
          reject,
        };

        this.currentBatch.push(request);

        // Start batching window if this is first request
        if (this.currentBatch.length === 1) {
          this.batchTimer = setTimeout(() => {
            this.flushBatch();
          }, this.batchConfig.windowMs);
        }

        // Flush immediately if batch is full
        if (this.currentBatch.length >= this.batchConfig.maxSize) {
          if (this.batchTimer) {
            clearTimeout(this.batchTimer);
          }
          this.flushBatch();
        }
      });
    });

    // Cache the promise
    this.requestCache.set(dedupKey, promise);

    return promise;
  }

  /**
   * Send multiple independent requests in parallel
   */
  async sendParallel(
    requests: Array<{ method: string; params?: Record<string, any> }>
  ): Promise<any[]> {
    return Promise.all(
      requests.map((req) => this.sendRequest(req.method, req.params || {}))
    );
  }

  /**
   * Direct send without batching (for time-sensitive operations)
   */
  private async sendDirect(
    method: string,
    params: Record<string, any>
  ): Promise<any> {
    // This would be implemented based on your bridge
    // For now, return mock data
    return { success: true, data: null };
  }

  /**
   * Flush current batch and send to Python
   */
  private async flushBatch(): Promise<void> {
    if (this.isBatchProcessing || this.currentBatch.length === 0) {
      return;
    }

    this.isBatchProcessing = true;
    const batch = this.currentBatch.splice(0);
    this.batchTimer = null;

    try {
      // Send batch as single request
      const batchResult = await this.sendBatch(batch);

      // Process results and resolve/reject individual promises
      batch.forEach((request, index) => {
        const result = batchResult[index];
        if (result.error) {
          request.reject(new Error(result.error));
        } else {
          request.resolve(result.data);
        }
      });
    } catch (error) {
      // Reject all requests in batch on error
      batch.forEach((request) => {
        request.reject(error);
      });
    } finally {
      this.isBatchProcessing = false;
    }
  }

  /**
   * Send batch of requests to Python
   */
  private async sendBatch(
    requests: BatchedRequest[]
  ): Promise<Array<{ data?: any; error?: string }>> {
    // This would call your actual bridge
    // For now, return mock successful responses
    return requests.map(() => ({ data: null }));
  }

  /**
   * Generate unique request ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Configure batching behavior
   */
  setBatchConfig(config: Partial<BatchConfig>): void {
    this.batchConfig = { ...this.batchConfig, ...config };
  }

  /**
   * Get batching statistics
   */
  getBatchStats(): {
    currentBatchSize: number;
    cacheSize: number;
    pendingRequests: number;
  } {
    return {
      currentBatchSize: this.currentBatch.length,
      cacheSize: this.requestCache.size(),
      pendingRequests: 0, // Would track in-flight requests
    };
  }

  /**
   * Clear all caches
   */
  clearCaches(): void {
    this.requestCache.clear();
    this.deduplicator.clear();
  }
}

// Export singleton instance
export const optimizedBridge = new OptimizedPythonBridge();
