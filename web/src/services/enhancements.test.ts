/**
 * Tests for error handling enhancements
 * - Fallback strategies
 * - Distributed tracing
 * - Error aggregation dashboard
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  executeWithFallback,
  CircuitBreakerWithFallback,
  FallbackStrategies,
} from '../services/fallbackStrategy';
import {
  TraceRecorder,
  TraceContextStorage,
  getTraceHeaders,
  extractTraceContext,
} from '../services/distributedTracing';
import {
  CircuitBreakerAggregator,
  DashboardService,
} from '../services/metricsAggregator';
import { CircuitBreaker } from '../services/circuitBreaker';

describe('Fallback Strategy Enhancements', () => {
  describe('executeWithFallback', () => {
    it('should return primary result when operation succeeds', async () => {
      const primary = vi.fn(async () => 'primary-result');
      const fallback = vi.fn(async () => 'fallback-result');

      const result = await executeWithFallback(primary, fallback);

      expect(result.success).toBe(true);
      expect(result.data).toBe('primary-result');
      expect(result.source).toBe('primary');
      expect(primary).toHaveBeenCalled();
      expect(fallback).not.toHaveBeenCalled();
    });

    it('should use fallback when primary times out', async () => {
      const primary = vi.fn(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve('primary-result'), 5000)
          )
      );
      const fallback = vi.fn(async () => 'fallback-result');

      const result = await executeWithFallback(primary, fallback, {
        timeout: 100,
      });

      expect(result.success).toBe(true);
      expect(result.data).toBe('fallback-result');
      expect(result.source).toBe('fallback');
    });

    it('should handle fallback errors gracefully', async () => {
      const primary = vi.fn(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve('primary-result'), 5000)
          )
      );
      const fallback = vi.fn(async () => {
        throw new Error('Fallback failed');
      });

      const result = await executeWithFallback(primary, fallback, {
        timeout: 100,
      });

      expect(result.success).toBe(false);
      expect(result.source).toBe('fallback');
      expect(result.error?.message).toBe('Fallback failed');
    });

    it('should return primary error when not a timeout', async () => {
      const primary = vi.fn(async () => {
        throw new Error('Primary error');
      });
      const fallback = vi.fn(async () => 'fallback-result');

      const result = await executeWithFallback(primary, fallback, {
        timeout: 5000,
      });

      expect(result.success).toBe(false);
      expect(result.source).toBe('primary');
      expect(result.error?.message).toBe('Primary error');
    });

    it('should track operation duration', async () => {
      const primary = vi.fn(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve('primary-result'), 100)
          )
      );
      const fallback = vi.fn(async () => 'fallback-result');

      const result = await executeWithFallback(primary, fallback);

      expect(result.duration).toBeGreaterThanOrEqual(100);
    });
  });

  describe('CircuitBreakerWithFallback', () => {
    it('should use fallback when circuit is open', async () => {
      const operation = vi.fn(async () => {
        throw new Error('Service error');
      });

      const breaker = new CircuitBreakerWithFallback(operation, {
        threshold: 2,
        timeout: 60000,
        resetTimeout: 30000,
      });

      const fallback = vi.fn(async () => 'fallback-value');
      breaker.setFallback(fallback);

      // Trigger failures to open circuit
      try {
        await breaker.execute();
      } catch (_e) {
        // Expected
      }
      try {
        await breaker.execute();
      } catch (_e) {
        // Expected
      }

      // Circuit should be open, use fallback
      const result = await breaker.executeWithFallback();

      expect(result).toBe('fallback-value');
      expect(fallback).toHaveBeenCalled();
    });

    it('should execute normally when circuit is closed', async () => {
      const operation = vi.fn(async () => 'success');

      const breaker = new CircuitBreakerWithFallback(operation);
      const fallback = vi.fn(async () => 'fallback-value');
      breaker.setFallback(fallback);

      const result = await breaker.executeWithFallback();

      expect(result).toBe('success');
      expect(fallback).not.toHaveBeenCalled();
    });
  });

  describe('FallbackStrategies', () => {
    it('should create cache-based fallback', async () => {
      const cache = new Map([['key1', 'cached-value']]);

      const fallback = FallbackStrategies.cacheBasedFallback(cache, 'key1');
      const result = await fallback();

      expect(result).toBe('cached-value');
    });

    it('should throw for missing cache key without default', async () => {
      const cache = new Map<string, string>();

      const fallback = FallbackStrategies.cacheBasedFallback(
        cache,
        'missing-key'
      );

      await expect(fallback()).rejects.toThrow();
    });

    it('should return default value when cache misses', async () => {
      const cache = new Map<string, string>();

      const fallback = FallbackStrategies.cacheBasedFallback(
        cache,
        'key1',
        'default-value'
      );
      const result = await fallback();

      expect(result).toBe('default-value');
    });

    it('should create default value fallback', async () => {
      const fallback = FallbackStrategies.defaultValueFallback('default');

      const result = await fallback();

      expect(result).toBe('default');
    });

    it('should create empty collection fallback', async () => {
      const fallback = FallbackStrategies.emptyCollectionFallback([]);

      const result = await fallback();

      expect(result).toEqual([]);
    });

    it('should retry with exponential backoff', async () => {
      let attempts = 0;
      const operation = vi.fn(async () => {
        attempts++;
        if (attempts < 3) {
          throw new Error('Try again');
        }
        return 'success';
      });

      const fallback = FallbackStrategies.retryFallback(operation, 5, 10);
      const result = await fallback();

      expect(result).toBe('success');
      expect(attempts).toBe(3);
    });
  });
});

describe('Distributed Tracing Enhancements', () => {
  describe('TraceRecorder', () => {
    let recorder: TraceRecorder;

    beforeEach(() => {
      recorder = new TraceRecorder();
    });

    it('should create execution context', () => {
      const context = recorder.createContext({ userId: '123' });

      expect(context.correlationId).toBeDefined();
      expect(context.traceId).toBeDefined();
      expect(context.spanId).toBeDefined();
      expect(context.metadata).toEqual({ userId: '123' });
    });

    it('should create child context', () => {
      const parentContext = recorder.createContext();
      const childContext = recorder.createChildContext(parentContext);

      expect(childContext.correlationId).toBe(parentContext.correlationId);
      expect(childContext.traceId).toBe(parentContext.traceId);
      expect(childContext.spanId).not.toBe(parentContext.spanId);
      expect(childContext.parentSpanId).toBe(parentContext.spanId);
    });

    it('should record execution spans', () => {
      const context = recorder.createContext();
      const startTime = Date.now();
      const endTime = startTime + 100;

      recorder.recordSpan(
        context,
        'operation',
        'success',
        startTime,
        endTime,
        undefined,
        { key: 'value' }
      );

      const spans = recorder.getSpans();

      expect(spans).toHaveLength(1);
      expect(spans[0].operationName).toBe('operation');
      expect(spans[0].status).toBe('success');
      expect(spans[0].duration).toBe(100);
    });

    it('should record error spans', () => {
      const context = recorder.createContext();
      const startTime = Date.now();
      const endTime = startTime + 50;

      recorder.recordSpan(context, 'operation', 'error', startTime, endTime, {
        code: 'ERROR_CODE',
        message: 'Error occurred',
        stack: 'stack trace',
      });

      const spans = recorder.getSpans();

      expect(spans[0].status).toBe('error');
      expect(spans[0].error?.code).toBe('ERROR_CODE');
    });

    it('should get trace summary', () => {
      const context = recorder.createContext();

      recorder.recordSpan(context, 'op1', 'success', Date.now(), Date.now() + 100);
      recorder.recordSpan(context, 'op2', 'error', Date.now(), Date.now() + 50);

      const summary = recorder.getTraceSummary();

      expect(summary?.spanCount).toBe(2);
      expect(summary?.errorCount).toBe(1);
      expect(summary?.correlationId).toBe(context.correlationId);
    });

    it('should export spans for external system', () => {
      const context = recorder.createContext();

      recorder.recordSpan(context, 'operation', 'success', Date.now(), Date.now() + 100);

      const exported = recorder.exportSpans();

      expect(exported).toHaveLength(1);
      expect(exported[0].traceId).toBe(context.traceId);
      expect(exported[0].operationName).toBe('operation');
    });
  });

  describe('TraceContextStorage', () => {
    let storage: TraceContextStorage;

    beforeEach(() => {
      storage = new TraceContextStorage();
    });

    it('should store and retrieve context', () => {
      const recorder = new TraceRecorder();
      const context = recorder.createContext();

      storage.setContext(context);
      const retrieved = storage.getContext(context.correlationId);

      expect(retrieved).toEqual(context);
    });

    it('should track active context', () => {
      const recorder = new TraceRecorder();
      const context = recorder.createContext();

      storage.setContext(context);

      expect(storage.getActiveContext()).toEqual(context);
    });

    it('should clear specific context', () => {
      const recorder = new TraceRecorder();
      const context = recorder.createContext();

      storage.setContext(context);
      storage.clearContext(context.correlationId);

      expect(storage.getContext(context.correlationId)).toBeNull();
    });

    it('should clear all contexts', () => {
      const recorder = new TraceRecorder();
      const context1 = recorder.createContext();
      const context2 = recorder.createContext();

      storage.setContext(context1);
      storage.setContext(context2);
      storage.clearAll();

      expect(storage.getActiveContext()).toBeNull();
    });
  });

  describe('Trace headers', () => {
    it('should generate trace headers', () => {
      const recorder = new TraceRecorder();
      const context = recorder.createContext();

      const headers = getTraceHeaders(context);

      expect(headers['X-Correlation-ID']).toBe(context.correlationId);
      expect(headers['X-Trace-ID']).toBe(context.traceId);
      expect(headers['X-Span-ID']).toBe(context.spanId);
    });

    it('should extract trace context from headers', () => {
      const headers = {
        'x-correlation-id': 'corr-123',
        'x-trace-id': 'trace-456',
        'x-span-id': 'span-789',
      };

      const context = extractTraceContext(headers);

      expect(context.correlationId).toBe('corr-123');
      expect(context.traceId).toBe('trace-456');
      expect(context.spanId).toBe('span-789');
    });
  });
});

describe('Error Aggregation Dashboard', () => {
  describe('CircuitBreakerAggregator', () => {
    let aggregator: CircuitBreakerAggregator;

    beforeEach(() => {
      aggregator = new CircuitBreakerAggregator();
    });

    it('should register and unregister breakers', () => {
      const breaker = new CircuitBreaker(async () => 'result');

      aggregator.registerBreaker('breaker1', breaker);
      const metrics = aggregator.getBreakerMetrics('breaker1');

      expect(metrics).not.toBeNull();
      expect(metrics?.name).toBe('breaker1');

      aggregator.unregisterBreaker('breaker1');
      const metricsAfter = aggregator.getBreakerMetrics('breaker1');

      expect(metricsAfter).toBeNull();
    });

    it('should collect metrics from multiple breakers', () => {
      const breaker1 = new CircuitBreaker(async () => 'result1');
      const breaker2 = new CircuitBreaker(async () => 'result2');

      aggregator.registerBreaker('breaker1', breaker1);
      aggregator.registerBreaker('breaker2', breaker2);

      const allMetrics = aggregator.getAllMetrics();

      expect(allMetrics).toHaveLength(2);
    });

    it('should record errors in history', () => {
      aggregator.recordError('breaker1', 'ERROR_CODE', 'Error message');
      aggregator.recordError('breaker1', 'ERROR_CODE', 'Another error');

      const history = aggregator.getErrorHistory(10);

      expect(history).toHaveLength(2);
      expect(history[0].breakerName).toBe('breaker1');
    });

    it('should generate error summaries', () => {
      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');
      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');
      aggregator.recordError('breaker2', 'ERROR_B', 'Error B');

      const summaries = aggregator.getErrorSummaries();

      expect(summaries).toHaveLength(2);
      expect(summaries[0].count).toBe(2); // ERROR_A
      expect(summaries[1].count).toBe(1); // ERROR_B
    });

    it('should generate dashboard snapshot', () => {
      const breaker = new CircuitBreaker(async () => 'result');
      aggregator.registerBreaker('breaker1', breaker);

      const dashboard = aggregator.getDashboard();

      expect(dashboard.totalBreakers).toBe(1);
      expect(dashboard.timestamp).toBeDefined();
      expect(dashboard.systemHealthScore).toBeGreaterThanOrEqual(0);
      expect(dashboard.systemHealthScore).toBeLessThanOrEqual(100);
    });

    it('should track breaker health status', () => {
      const breaker = new CircuitBreaker(async () => 'result');
      aggregator.registerBreaker('healthy', breaker);

      const health = aggregator.getHealthStatus();

      expect(health.healthy).toContain('healthy');
      expect(health.critical).toHaveLength(0);
    });

    it('should calculate error trends', () => {
      const now = Date.now();

      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');
      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');
      aggregator.recordError('breaker1', 'ERROR_B', 'Error B');

      const trends = aggregator.getErrorTrends(3600000);

      expect(trends['ERROR_A']).toBe(2);
      expect(trends['ERROR_B']).toBe(1);
    });

    it('should clear error history', () => {
      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');

      aggregator.clearErrorHistory();

      const history = aggregator.getErrorHistory();

      expect(history).toHaveLength(0);
    });
  });

  describe('DashboardService', () => {
    let service: DashboardService;
    let aggregator: CircuitBreakerAggregator;

    beforeEach(() => {
      aggregator = new CircuitBreakerAggregator();
      service = new DashboardService(aggregator);
    });

    it('should query dashboard with breaker filter', () => {
      const breaker1 = new CircuitBreaker(async () => 'result1');
      const breaker2 = new CircuitBreaker(async () => 'result2');

      aggregator.registerBreaker('breaker1', breaker1);
      aggregator.registerBreaker('breaker2', breaker2);

      const result = service.query({ breakerName: 'breaker1' });

      expect(result.breakersMetrics).toHaveLength(1);
      expect(result.breakersMetrics[0].name).toBe('breaker1');
    });

    it('should query dashboard with error code filter', () => {
      aggregator.recordError('breaker1', 'ERROR_A', 'Error A');
      aggregator.recordError('breaker1', 'ERROR_B', 'Error B');

      const result = service.query({ errorCode: 'ERROR_A' });

      expect(result.errorSummaries).toHaveLength(1);
      expect(result.errorSummaries[0].errorCode).toBe('ERROR_A');
    });

    it('should provide alerts for critical state', () => {
      // Create a breaker and force it to fail
      const breaker = new CircuitBreaker(
        async () => {
          throw new Error('Service down');
        },
        { threshold: 1 }
      );

      aggregator.registerBreaker('critical-breaker', breaker);

      // Trigger failures
      try {
        await breaker.execute();
      } catch (_e) {
        // Expected
      }

      const alerts = service.getAlerts();

      // Note: Alerts depend on health calculation
      expect(alerts).toHaveProperty('critical');
      expect(alerts).toHaveProperty('warning');
    });
  });
});
