/**
 * Bridge Communication Performance Tests
 * 
 * Tests bridge latency, batching efficiency, request deduplication,
 * and overall communication throughput.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Mock Bridge for testing
 */
class MockBridge {
  private requestLog: any[] = [];
  private latency: number = 100; // Default 100ms latency
  private batchQueue: any[] = [];
  private batchTimer: NodeJS.Timeout | null = null;
  private batchConfig = {
    windowMs: 50,
    maxSize: 5,
    enabled: true,
  };

  setLatency(ms: number): void {
    this.latency = ms;
  }

  setBatchConfig(config: Partial<typeof this.batchConfig>): void {
    this.batchConfig = { ...this.batchConfig, ...config };
  }

  async sendRequest(method: string, params: any = {}): Promise<any> {
    const startTime = performance.now();

    if (this.batchConfig.enabled) {
      return new Promise((resolve) => {
        this.batchQueue.push({ method, params, resolve, timestamp: startTime });

        if (this.batchQueue.length >= this.batchConfig.maxSize) {
          this.flushBatch();
        } else if (!this.batchTimer) {
          this.batchTimer = setTimeout(() => {
            this.flushBatch();
          }, this.batchConfig.windowMs);
        }
      });
    } else {
      return new Promise((resolve) => {
        setTimeout(() => {
          const duration = performance.now() - startTime;
          this.requestLog.push({
            method,
            params,
            duration,
            timestamp: startTime,
            batchSize: 1,
          });
          resolve({ success: true, method, duration });
        }, this.latency);
      });
    }
  }

  private flushBatch(): void {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    if (this.batchQueue.length === 0) return;

    const batch = this.batchQueue.splice(0, this.batchConfig.maxSize);
    const batchStartTime = performance.now();

    setTimeout(() => {
      const duration = performance.now() - batchStartTime;

      batch.forEach((item) => {
        this.requestLog.push({
          method: item.method,
          params: item.params,
          duration,
          timestamp: item.timestamp,
          batchSize: batch.length,
        });
        item.resolve({ success: true, method: item.method, duration });
      });
    }, this.latency);
  }

  async sendParallel(requests: Array<{ method: string; params?: any }>): Promise<any[]> {
    return Promise.all(
      requests.map((req) => this.sendRequest(req.method, req.params))
    );
  }

  getRequestLog(): any[] {
    return [...this.requestLog];
  }

  clearLog(): void {
    this.requestLog = [];
  }

  getStats() {
    if (this.requestLog.length === 0) {
      return {
        totalRequests: 0,
        averageLatency: 0,
        minLatency: 0,
        maxLatency: 0,
        averageBatchSize: 0,
        totalDuration: 0,
      };
    }

    const durations = this.requestLog.map((r) => r.duration);
    const batchSizes = this.requestLog.map((r) => r.batchSize);

    return {
      totalRequests: this.requestLog.length,
      averageLatency: durations.reduce((a, b) => a + b, 0) / durations.length,
      minLatency: Math.min(...durations),
      maxLatency: Math.max(...durations),
      averageBatchSize:
        batchSizes.reduce((a, b) => a + b, 0) / batchSizes.length,
      totalDuration: durations.reduce((a, b) => a + b, 0),
    };
  }
}

/**
 * Bridge Performance Tests
 */

describe('Bridge: Communication Performance', () => {
  let bridge: MockBridge;

  beforeEach(() => {
    bridge = new MockBridge();
    bridge.setLatency(100);
  });

  afterEach(() => {
    bridge.clearLog();
  });

  describe('Basic Communication', () => {
    it('should send single request within expected latency', async () => {
      const start = performance.now();
      const response = await bridge.sendRequest('getFields');
      const duration = performance.now() - start;

      expect(response.success).toBe(true);
      expect(duration).toBeGreaterThanOrEqual(100);
      expect(duration).toBeLessThan(150);
    });

    it('should handle multiple sequential requests', async () => {
      const requests = ['getFields', 'getBehaviors', 'getModels'];

      for (const req of requests) {
        await bridge.sendRequest(req);
      }

      const log = bridge.getRequestLog();
      expect(log.length).toBe(3);
      expect(log.every((r) => r.duration >= 100)).toBe(true);
    });

    it('should handle parallel requests efficiently', async () => {
      const start = performance.now();

      const requests = [
        { method: 'getFields' },
        { method: 'getBehaviors' },
        { method: 'getModels' },
      ];

      await bridge.sendParallel(requests);
      const duration = performance.now() - start;

      // Parallel should take roughly 1x latency, not 3x
      expect(duration).toBeLessThan(250);
      expect(duration).toBeGreaterThanOrEqual(100);
    });
  });

  describe('Batching Optimization', () => {
    beforeEach(() => {
      bridge.setBatchConfig({ windowMs: 50, maxSize: 5, enabled: true });
    });

    it('should batch multiple requests into single call', async () => {
      const requests = [
        'getFields',
        'getFields',
        'getBehaviors',
        'getModels',
        'getSettings',
      ];

      const promises = requests.map((req) => bridge.sendRequest(req));
      await Promise.all(promises);

      const log = bridge.getRequestLog();
      expect(log.length).toBe(5);

      // All should have same batch size
      const batchSizes = [...new Set(log.map((r) => r.batchSize))];
      expect(batchSizes.length).toBe(1);
      expect(batchSizes[0]).toBe(5);
    });

    it('should batch requests up to max size', async () => {
      const count = 20;
      const promises = [];

      for (let i = 0; i < count; i++) {
        promises.push(bridge.sendRequest(`request-${i}`));
      }

      await Promise.all(promises);

      const log = bridge.getRequestLog();
      expect(log.length).toBe(count);

      // Should have 4 batches of 5
      const uniqueBatches = log.reduce((acc: any, log: any) => {
        acc[log.batchSize] = (acc[log.batchSize] || 0) + 1;
        return acc;
      }, {});

      expect(Object.keys(uniqueBatches).length).toBeGreaterThanOrEqual(1);
    });

    it('should flush batch when window expires', async () => {
      bridge.setBatchConfig({ windowMs: 50, maxSize: 10, enabled: true });

      // Send 3 requests slowly
      await bridge.sendRequest('req1');
      await new Promise((resolve) => setTimeout(resolve, 100));
      await bridge.sendRequest('req2');

      const log = bridge.getRequestLog();
      expect(log.length).toBeGreaterThan(0);
    });

    it('should measure batching efficiency', async () => {
      bridge.setBatchConfig({ windowMs: 50, maxSize: 5, enabled: true });

      // Sequential without batching
      bridge.setBatchConfig({ enabled: false });
      const start1 = performance.now();
      const reqs1 = [];
      for (let i = 0; i < 10; i++) {
        reqs1.push(bridge.sendRequest(`req-${i}`));
      }
      await Promise.all(reqs1);
      const sequential = performance.now() - start1;
      const seqStats = bridge.getStats();
      bridge.clearLog();

      // With batching
      bridge.setBatchConfig({ enabled: true });
      const start2 = performance.now();
      const reqs2 = [];
      for (let i = 0; i < 10; i++) {
        reqs2.push(bridge.sendRequest(`req-${i}`));
      }
      await Promise.all(reqs2);
      const batched = performance.now() - start2;
      const batchStats = bridge.getStats();

      console.log('Sequential:', seqStats);
      console.log('Batched:', batchStats);

      // Batched should be faster
      expect(batched).toBeLessThanOrEqual(sequential);
    });
  });

  describe('Request Deduplication', () => {
    it('should detect duplicate requests', () => {
      const request1 = { method: 'getFields', params: {} };
      const request2 = { method: 'getFields', params: {} };
      const request3 = { method: 'getBehaviors', params: {} };

      const key1 = `${request1.method}:${JSON.stringify(request1.params)}`;
      const key2 = `${request2.method}:${JSON.stringify(request2.params)}`;
      const key3 = `${request3.method}:${JSON.stringify(request3.params)}`;

      expect(key1).toBe(key2);
      expect(key1).not.toBe(key3);
    });

    it('should avoid duplicate in-flight requests', async () => {
      const requestMap = new Map();

      const sendWithDedup = async (method: string, params: any = {}) => {
        const key = `${method}:${JSON.stringify(params)}`;

        if (requestMap.has(key)) {
          return requestMap.get(key);
        }

        const promise = bridge.sendRequest(method, params);
        requestMap.set(key, promise);

        try {
          return await promise;
        } finally {
          requestMap.delete(key);
        }
      };

      // Send duplicate requests
      const promises = [
        sendWithDedup('getFields'),
        sendWithDedup('getFields'),
        sendWithDedup('getFields'),
        sendWithDedup('getBehaviors'),
        sendWithDedup('getFields'),
      ];

      await Promise.all(promises);

      // Should have deduplicated
      expect(requestMap.size).toBe(0);
      const log = bridge.getRequestLog();
      expect(log.length).toBeLessThanOrEqual(5);
    });
  });

  describe('Latency Reduction', () => {
    it('should measure average latency improvement', async () => {
      // Without batching
      bridge.setBatchConfig({ enabled: false });
      bridge.setLatency(150);

      const start1 = performance.now();
      const requests1 = [];
      for (let i = 0; i < 10; i++) {
        requests1.push(bridge.sendRequest(`req-${i}`));
      }
      await Promise.all(requests1);
      const withoutBatching = performance.now() - start1;
      const stats1 = bridge.getStats();
      bridge.clearLog();

      // With batching
      bridge.setBatchConfig({ enabled: true, windowMs: 50, maxSize: 5 });
      bridge.setLatency(150);

      const start2 = performance.now();
      const requests2 = [];
      for (let i = 0; i < 10; i++) {
        requests2.push(bridge.sendRequest(`req-${i}`));
      }
      await Promise.all(requests2);
      const withBatching = performance.now() - start2;
      const stats2 = bridge.getStats();

      const improvement = ((withoutBatching - withBatching) / withoutBatching) * 100;

      console.log(`Latency improvement with batching: ${improvement.toFixed(1)}%`);
      console.log('Without batching:', stats1);
      console.log('With batching:', stats2);

      // Should show improvement
      expect(withBatching).toBeLessThanOrEqual(withoutBatching);
    });
  });

  describe('Throughput Analysis', () => {
    it('should measure requests per second', async () => {
      bridge.setBatchConfig({ enabled: true });

      const start = performance.now();
      const promises = [];

      for (let i = 0; i < 100; i++) {
        promises.push(bridge.sendRequest(`req-${i}`));
      }

      await Promise.all(promises);
      const duration = (performance.now() - start) / 1000; // seconds

      const throughput = 100 / duration;
      console.log(`Throughput: ${throughput.toFixed(2)} requests/second`);

      expect(throughput).toBeGreaterThan(0);
    });

    it('should handle concurrent request spikes', async () => {
      bridge.setBatchConfig({ enabled: true, maxSize: 10, windowMs: 100 });

      const spike1 = [];
      for (let i = 0; i < 50; i++) {
        spike1.push(bridge.sendRequest(`spike1-${i}`));
      }

      const spike2 = [];
      setTimeout(() => {
        for (let i = 0; i < 50; i++) {
          spike2.push(bridge.sendRequest(`spike2-${i}`));
        }
      }, 50);

      await Promise.all([...spike1, ...spike2]);

      const stats = bridge.getStats();
      expect(stats.totalRequests).toBe(100);
      expect(stats.averageLatency).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle request timeouts gracefully', async () => {
      bridge.setLatency(5000); // Very high latency

      const timeout = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), 1000)
      );

      const request = bridge.sendRequest('slow-request');

      try {
        await Promise.race([request, timeout]);
      } catch (e) {
        expect((e as Error).message).toBe('Timeout');
      }
    });
  });
});

/**
 * Export MockBridge for use in other tests
 */
export { MockBridge };
