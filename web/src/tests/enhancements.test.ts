/**
 * Tests for Event Bus, Service Registry, and Middleware Pipeline
 * Comprehensive test coverage for Phase 1 architecture enhancements
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { EventBus, eventBus } from '@/utils/eventBus';
import { ServiceRegistry, registry } from '@/services/registry';
import {
  Pipeline,
  loggingMiddleware,
  errorHandlingMiddleware,
  timeoutMiddleware,
  retryMiddleware,
  cachingMiddleware,
  metricsMiddleware,
} from '@/utils/middleware';

// ============================================================================
// EventBus Tests
// ============================================================================

describe('EventBus', () => {
  let bus: EventBus;

  beforeEach(() => {
    bus = new EventBus();
  });

  describe('on/emit', () => {
    it('should subscribe and emit events', () => {
      const handler = vi.fn();
      bus.on('test', handler);
      bus.emit('test', { data: 'hello' });

      expect(handler).toHaveBeenCalledWith({ data: 'hello' });
    });

    it('should call multiple handlers for same event', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      bus.on('test', handler1);
      bus.on('test', handler2);
      bus.emit('test', { value: 1 });

      expect(handler1).toHaveBeenCalledWith({ value: 1 });
      expect(handler2).toHaveBeenCalledWith({ value: 1 });
    });

    it('should not call handler after unsubscribe', () => {
      const handler = vi.fn();
      const unsubscribe = bus.on('test', handler);

      bus.emit('test', { data: 1 });
      expect(handler).toHaveBeenCalledTimes(1);

      unsubscribe();
      bus.emit('test', { data: 2 });
      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should handle errors in handlers without breaking others', () => {
      const handler1 = vi.fn(() => {
        throw new Error('handler1 error');
      });
      const handler2 = vi.fn();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      bus.on('test', handler1);
      bus.on('test', handler2);
      bus.emit('test', { value: 1 });

      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('off', () => {
    it('should remove all listeners for event', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      bus.on('test', handler1);
      bus.on('test', handler2);
      bus.off('test');
      bus.emit('test', { data: 1 });

      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).not.toHaveBeenCalled();
    });
  });

  describe('clear', () => {
    it('should remove all listeners for all events', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      bus.on('test1', handler1);
      bus.on('test2', handler2);
      bus.clear();

      bus.emit('test1', { data: 1 });
      bus.emit('test2', { data: 2 });

      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).not.toHaveBeenCalled();
    });
  });

  describe('hasListeners', () => {
    it('should return true if event has listeners', () => {
      bus.on('test', () => {});
      expect(bus.hasListeners('test')).toBe(true);
    });

    it('should return false if event has no listeners', () => {
      expect(bus.hasListeners('test')).toBe(false);
    });
  });

  describe('getListenerCount', () => {
    it('should return correct listener count', () => {
      bus.on('test', () => {});
      bus.on('test', () => {});
      bus.on('test', () => {});

      expect(bus.getListenerCount('test')).toBe(3);
    });

    it('should return 0 for non-existent event', () => {
      expect(bus.getListenerCount('nonexistent')).toBe(0);
    });
  });

  describe('type safety', () => {
    it('should work with typed events', () => {
      interface TypedEvents {
        'user:created': { id: string; name: string };
        'user:deleted': { id: string };
      }

      const typedBus = new EventBus() as any;
      const handler = vi.fn();

      typedBus.on<TypedEvents['user:created']>('user:created', handler);
      typedBus.emit('user:created', { id: '123', name: 'John' });

      expect(handler).toHaveBeenCalledWith({ id: '123', name: 'John' });
    });
  });
});

// ============================================================================
// ServiceRegistry Tests
// ============================================================================

describe('ServiceRegistry', () => {
  let reg: ServiceRegistry;

  beforeEach(() => {
    reg = new ServiceRegistry();
  });

  describe('register/get', () => {
    it('should register and retrieve service', () => {
      const service = { name: 'test-service' };
      reg.register('test', () => service);

      const retrieved = reg.get('test');
      expect(retrieved).toBe(service);
    });

    it('should throw error for unregistered service', () => {
      expect(() => reg.get('nonexistent')).toThrow(
        'Service nonexistent not registered'
      );
    });

    it('should allow registering multiple services', () => {
      reg.register('service1', () => ({ id: 1 }));
      reg.register('service2', () => ({ id: 2 }));

      expect(reg.get('service1')).toEqual({ id: 1 });
      expect(reg.get('service2')).toEqual({ id: 2 });
    });
  });

  describe('initialize', () => {
    it('should call initializer on init', async () => {
      const initializer = vi.fn();
      reg.register('test', () => ({}), { onInit: initializer });

      await reg.initialize('test');
      expect(initializer).toHaveBeenCalled();
    });

    it('should not call initializer twice', async () => {
      const initializer = vi.fn();
      reg.register('test', () => ({}), { onInit: initializer });

      await reg.initialize('test');
      await reg.initialize('test');

      expect(initializer).toHaveBeenCalledTimes(1);
    });

    it('should handle initialization errors', async () => {
      const initializer = vi.fn().mockRejectedValue(new Error('init failed'));
      reg.register('test', () => ({}), { onInit: initializer });

      await expect(reg.initialize('test')).rejects.toThrow(
        'Failed to initialize service test'
      );
    });
  });

  describe('initializeAll', () => {
    it('should initialize all services with initializers', async () => {
      const init1 = vi.fn();
      const init2 = vi.fn();
      const init3 = vi.fn();

      reg.register('service1', () => ({}), { onInit: init1 });
      reg.register('service2', () => ({}), { onInit: init2 });
      reg.register('service3', () => ({}));

      await reg.initializeAll();

      expect(init1).toHaveBeenCalled();
      expect(init2).toHaveBeenCalled();
      expect(init3).not.toHaveBeenCalled();
    });

    it('should continue initializing on error', async () => {
      const init1 = vi.fn().mockRejectedValue(new Error('error'));
      const init2 = vi.fn();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      reg.register('service1', () => ({}), { onInit: init1 });
      reg.register('service2', () => ({}), { onInit: init2 });

      await reg.initializeAll();

      expect(init1).toHaveBeenCalled();
      expect(init2).toHaveBeenCalled();
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('has', () => {
    it('should return true for registered service', () => {
      reg.register('test', () => ({}));
      expect(reg.has('test')).toBe(true);
    });

    it('should return false for unregistered service', () => {
      expect(reg.has('nonexistent')).toBe(false);
    });
  });

  describe('destroy', () => {
    it('should call destroyer on destroy', async () => {
      const destroyer = vi.fn();
      reg.register('test', () => ({ id: 1 }), { onDestroy: destroyer });

      await reg.destroy('test');
      expect(destroyer).toHaveBeenCalled();
    });

    it('should remove service after destroy', async () => {
      reg.register('test', () => ({}), { onDestroy: async () => {} });

      await reg.destroy('test');
      expect(reg.has('test')).toBe(false);
    });

    it('should handle destroyer errors', async () => {
      const destroyer = vi.fn().mockRejectedValue(new Error('destroy failed'));
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      reg.register('test', () => ({}), { onDestroy: destroyer });

      await reg.destroy('test');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('destroyAll', () => {
    it('should destroy all services', async () => {
      const destroy1 = vi.fn();
      const destroy2 = vi.fn();

      reg.register('service1', () => ({}), { onDestroy: destroy1 });
      reg.register('service2', () => ({}), { onDestroy: destroy2 });

      await reg.destroyAll();

      expect(destroy1).toHaveBeenCalled();
      expect(destroy2).toHaveBeenCalled();
    });
  });

  describe('getServiceNames', () => {
    it('should return all registered service names', () => {
      reg.register('service1', () => ({}));
      reg.register('service2', () => ({}));
      reg.register('service3', () => ({}));

      const names = reg.getServiceNames();
      expect(names).toContain('service1');
      expect(names).toContain('service2');
      expect(names).toContain('service3');
      expect(names).toHaveLength(3);
    });
  });

  describe('getInitializationStatus', () => {
    it('should return initialization status', async () => {
      reg.register('service1', () => ({}), { onInit: async () => {} });
      reg.register('service2', () => ({}));

      let status = reg.getInitializationStatus();
      expect(status['service1']).toBe(false);
      expect(status['service2']).toBe(false);

      await reg.initialize('service1');
      status = reg.getInitializationStatus();
      expect(status['service1']).toBe(true);
      expect(status['service2']).toBe(false);
    });
  });
});

// ============================================================================
// Pipeline Tests
// ============================================================================

describe('Pipeline', () => {
  describe('use/execute', () => {
    it('should execute handler without middleware', async () => {
      const handler = vi.fn().mockResolvedValue('result');
      const pipeline = new Pipeline<string>();

      const result = await pipeline.execute(handler);

      expect(result).toBe('result');
      expect(handler).toHaveBeenCalled();
    });

    it('should execute middleware in order', async () => {
      const order: number[] = [];

      const middleware1: any = async (next) => {
        order.push(1);
        const result = await next();
        order.push(2);
        return result;
      };

      const middleware2: any = async (next) => {
        order.push(3);
        const result = await next();
        order.push(4);
        return result;
      };

      const handler = vi.fn().mockResolvedValue('result');
      const pipeline = new Pipeline<string>();

      pipeline.use(middleware1).use(middleware2);
      await pipeline.execute(handler);

      expect(order).toEqual([1, 3, 4, 2]);
    });

    it('should return result from handler', async () => {
      const handler = vi.fn().mockResolvedValue({ id: 1, name: 'test' });
      const pipeline = new Pipeline<{ id: number; name: string }>();

      const result = await pipeline.execute(handler);

      expect(result).toEqual({ id: 1, name: 'test' });
    });

    it('should propagate errors', async () => {
      const error = new Error('handler error');
      const handler = vi.fn().mockRejectedValue(error);
      const pipeline = new Pipeline<string>();

      await expect(pipeline.execute(handler)).rejects.toThrow('handler error');
    });

    it('should throw if next called multiple times', async () => {
      const middleware: any = async (next) => {
        await next();
        return next();
      };

      const handler = vi.fn().mockResolvedValue('result');
      const pipeline = new Pipeline<string>();
      pipeline.use(middleware);

      await expect(pipeline.execute(handler)).rejects.toThrow(
        'next() called multiple times'
      );
    });
  });

  describe('middleware chaining', () => {
    it('should allow method chaining', () => {
      const pipeline = new Pipeline<string>();
      const result = pipeline
        .use(async (next) => next())
        .use(async (next) => next());

      expect(result).toBe(pipeline);
    });
  });

  describe('getMiddlewareCount', () => {
    it('should return correct count', () => {
      const pipeline = new Pipeline<string>();
      expect(pipeline.getMiddlewareCount()).toBe(0);

      pipeline.use(async (next) => next());
      expect(pipeline.getMiddlewareCount()).toBe(1);

      pipeline.use(async (next) => next());
      expect(pipeline.getMiddlewareCount()).toBe(2);
    });
  });

  describe('clear', () => {
    it('should remove all middleware', () => {
      const pipeline = new Pipeline<string>();
      pipeline.use(async (next) => next());
      pipeline.use(async (next) => next());

      expect(pipeline.getMiddlewareCount()).toBe(2);

      pipeline.clear();
      expect(pipeline.getMiddlewareCount()).toBe(0);
    });
  });
});

// ============================================================================
// Middleware Function Tests
// ============================================================================

describe('Middleware Functions', () => {
  describe('loggingMiddleware', () => {
    it('should log operation', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline.use(loggingMiddleware('test-op'));

      await pipeline.execute(handler);

      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('[test-op]'));
      consoleSpy.mockRestore();
    });

    it('should log errors', async () => {
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => {});
      const handler = vi.fn().mockRejectedValue(new Error('test error'));

      const pipeline = new Pipeline<string>();
      pipeline.use(loggingMiddleware('test-op'));

      try {
        await pipeline.execute(handler);
      } catch (e) {
        // Expected
      }

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });

  describe('errorHandlingMiddleware', () => {
    it('should call error handler on error', async () => {
      const errorHandler = vi.fn();
      const error = new Error('test error');
      const handler = vi.fn().mockRejectedValue(error);

      const pipeline = new Pipeline<string>();
      pipeline.use(errorHandlingMiddleware(errorHandler));

      try {
        await pipeline.execute(handler);
      } catch (e) {
        // Expected
      }

      expect(errorHandler).toHaveBeenCalledWith(error);
    });

    it('should re-throw error', async () => {
      const errorHandler = vi.fn();
      const error = new Error('test error');
      const handler = vi.fn().mockRejectedValue(error);

      const pipeline = new Pipeline<string>();
      pipeline.use(errorHandlingMiddleware(errorHandler));

      await expect(pipeline.execute(handler)).rejects.toThrow('test error');
    });
  });

  describe('timeoutMiddleware', () => {
    it('should reject on timeout', async () => {
      const handler = () =>
        new Promise((resolve) => setTimeout(() => resolve('result'), 200));

      const pipeline = new Pipeline<string>();
      pipeline.use(timeoutMiddleware(50));

      await expect(pipeline.execute(handler as any)).rejects.toThrow(
        'timed out'
      );
    });

    it('should succeed within timeout', async () => {
      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline.use(timeoutMiddleware(100));

      const result = await pipeline.execute(handler);
      expect(result).toBe('result');
    });
  });

  describe('retryMiddleware', () => {
    it('should retry on failure', async () => {
      let attempts = 0;
      const handler = vi.fn().mockImplementation(() => {
        attempts++;
        if (attempts < 3) {
          return Promise.reject(new Error('fail'));
        }
        return Promise.resolve('success');
      });

      const pipeline = new Pipeline<string>();
      pipeline.use(retryMiddleware(3, 10));

      const result = await pipeline.execute(handler);
      expect(result).toBe('success');
      expect(handler).toHaveBeenCalledTimes(3);
    });

    it('should fail after max retries', async () => {
      const handler = vi.fn().mockRejectedValue(new Error('always fails'));

      const pipeline = new Pipeline<string>();
      pipeline.use(retryMiddleware(2, 10));

      await expect(pipeline.execute(handler)).rejects.toThrow('always fails');
      expect(handler).toHaveBeenCalledTimes(3);
    });
  });

  describe('cachingMiddleware', () => {
    it('should cache successful result', async () => {
      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline.use(cachingMiddleware('test-key'));

      const result1 = await pipeline.execute(handler);
      const result2 = await pipeline.execute(handler);

      expect(result1).toBe('result');
      expect(result2).toBe('result');
      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should respect TTL', async () => {
      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline.use(cachingMiddleware('test-key', 50));

      await pipeline.execute(handler);
      expect(handler).toHaveBeenCalledTimes(1);

      await new Promise((resolve) => setTimeout(resolve, 100));
      await pipeline.execute(handler);

      expect(handler).toHaveBeenCalledTimes(2);
    });
  });

  describe('metricsMiddleware', () => {
    it('should record success metrics', async () => {
      const metricsHandler = vi.fn();
      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline.use(metricsMiddleware(metricsHandler));

      await pipeline.execute(handler);

      expect(metricsHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          duration: expect.any(Number),
        })
      );
    });

    it('should record failure metrics', async () => {
      const metricsHandler = vi.fn();
      const handler = vi.fn().mockRejectedValue(new Error('fail'));

      const pipeline = new Pipeline<string>();
      pipeline.use(metricsMiddleware(metricsHandler));

      try {
        await pipeline.execute(handler);
      } catch (e) {
        // Expected
      }

      expect(metricsHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          success: false,
          duration: expect.any(Number),
        })
      );
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('Integration Tests', () => {
  describe('EventBus + ServiceRegistry', () => {
    it('should allow service to use event bus', async () => {
      const handler = vi.fn();

      const bus = new EventBus();
      const reg = new ServiceRegistry();

      reg.register(
        'bus',
        () => bus,
        {
          onInit: async () => {
            bus.on('test', handler);
          },
        }
      );

      await reg.initialize('bus');
      const busService = reg.get<EventBus>('bus');
      busService.emit('test', { value: 1 });

      expect(handler).toHaveBeenCalledWith({ value: 1 });
    });
  });

  describe('Pipeline + ErrorHandling + Metrics', () => {
    it('should combine multiple middleware', async () => {
      const errors: Error[] = [];
      const metrics: any[] = [];

      const handler = vi.fn().mockResolvedValue('result');

      const pipeline = new Pipeline<string>();
      pipeline
        .use(errorHandlingMiddleware((e) => errors.push(e)))
        .use(metricsMiddleware((m) => metrics.push(m)))
        .use(loggingMiddleware('test'));

      const result = await pipeline.execute(handler);

      expect(result).toBe('result');
      expect(metrics).toHaveLength(1);
      expect(metrics[0].success).toBe(true);
    });
  });

  describe('Complex scenario', () => {
    it('should handle real-world usage', async () => {
      const bus = new EventBus();
      const reg = new ServiceRegistry();

      // Register services
      reg.register('eventBus', () => bus);

      // Initialize
      await reg.initializeAll();

      // Use pipeline
      const pipeline = new Pipeline<{ id: string }>();
      pipeline.use(loggingMiddleware('api-call'));

      const handler = async () => {
        const event = { id: '123' };
        bus.emit('data:fetched', event);
        return event;
      };

      const handler_fn = vi.fn(handler);
      const result = await pipeline.execute(handler_fn);

      expect(result).toEqual({ id: '123' });
    });
  });
});
