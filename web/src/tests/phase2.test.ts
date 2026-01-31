/**
 * Tests for Cache Manager and API Client
 * Phase 2 architecture enhancements
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  CacheManager,
  LRUCacheStrategy,
  TTLCacheStrategy,
  HybridCacheStrategy,
  SimpleMemoryCacheStrategy,
  cacheManager,
} from '@/services/cacheManager';
import {
  ApiClient,
  HttpTransport,
  WebSocketTransport,
  ApiRequest,
  ApiResponse,
  ApiTransport,
  ApiError,
} from '@/services/apiClient';

// ============================================================================
// Cache Manager Tests
// ============================================================================

describe('CacheManager', () => {
  let manager: CacheManager;

  beforeEach(() => {
    manager = new CacheManager();
  });

  describe('register/get', () => {
    it('should register and retrieve cache strategy', () => {
      const cache = new SimpleMemoryCacheStrategy<string, string>();
      manager.register('test', cache);

      const retrieved = manager.get('test');
      expect(retrieved).toBe(cache);
    });

    it('should throw error for unregistered strategy', () => {
      expect(() => manager.get('nonexistent')).toThrow(
        "Cache strategy 'nonexistent' not registered"
      );
    });

    it('should allow multiple strategies', () => {
      const cache1 = new LRUCacheStrategy<string, any>(100);
      const cache2 = new TTLCacheStrategy<string, any>(60000);

      manager.register('lru', cache1);
      manager.register('ttl', cache2);

      expect(manager.get('lru')).toBe(cache1);
      expect(manager.get('ttl')).toBe(cache2);
    });
  });

  describe('has', () => {
    it('should return true for registered strategy', () => {
      manager.register('test', new SimpleMemoryCacheStrategy());
      expect(manager.has('test')).toBe(true);
    });

    it('should return false for unregistered strategy', () => {
      expect(manager.has('nonexistent')).toBe(false);
    });
  });

  describe('unregister', () => {
    it('should remove strategy and clear cache', () => {
      const cache = new SimpleMemoryCacheStrategy<string, string>();
      cache.set('key', 'value');

      manager.register('test', cache);
      expect(manager.has('test')).toBe(true);

      manager.unregister('test');
      expect(manager.has('test')).toBe(false);
      expect(cache.get('key')).toBeUndefined();
    });
  });

  describe('getStrategyNames', () => {
    it('should return all registered strategy names', () => {
      manager.register('cache1', new SimpleMemoryCacheStrategy());
      manager.register('cache2', new SimpleMemoryCacheStrategy());
      manager.register('cache3', new SimpleMemoryCacheStrategy());

      const names = manager.getStrategyNames();
      expect(names).toContain('cache1');
      expect(names).toContain('cache2');
      expect(names).toContain('cache3');
    });
  });

  describe('clearAll', () => {
    it('should clear all caches', () => {
      const cache1 = new SimpleMemoryCacheStrategy<string, string>();
      const cache2 = new SimpleMemoryCacheStrategy<string, string>();

      cache1.set('key1', 'value1');
      cache2.set('key2', 'value2');

      manager.register('cache1', cache1);
      manager.register('cache2', cache2);

      manager.clearAll();

      expect(cache1.get('key1')).toBeUndefined();
      expect(cache2.get('key2')).toBeUndefined();
    });
  });
});

// ============================================================================
// LRU Cache Strategy Tests
// ============================================================================

describe('LRUCacheStrategy', () => {
  let cache: LRUCacheStrategy<string, string>;

  beforeEach(() => {
    cache = new LRUCacheStrategy(3);
  });

  describe('basic operations', () => {
    it('should set and get values', () => {
      cache.set('key1', 'value1');
      expect(cache.get('key1')).toBe('value1');
    });

    it('should return undefined for missing key', () => {
      expect(cache.get('nonexistent')).toBeUndefined();
    });

    it('should handle has', () => {
      cache.set('key1', 'value1');
      expect(cache.has('key1')).toBe(true);
      expect(cache.has('nonexistent')).toBe(false);
    });
  });

  describe('LRU eviction', () => {
    it('should evict least recently used item', () => {
      cache.set('a', '1');
      cache.set('b', '2');
      cache.set('c', '3');
      // Cache is full: [a, b, c]

      cache.set('d', '4');
      // a should be evicted

      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('b')).toBe('2');
      expect(cache.get('c')).toBe('3');
      expect(cache.get('d')).toBe('4');
    });

    it('should mark accessed item as recently used', () => {
      cache.set('a', '1');
      cache.set('b', '2');
      cache.set('c', '3');

      cache.get('a'); // Access a, making it recently used

      cache.set('d', '4');
      // b should be evicted instead of a

      expect(cache.get('a')).toBe('1');
      expect(cache.get('b')).toBeUndefined();
    });
  });

  describe('remove', () => {
    it('should remove item', () => {
      cache.set('key1', 'value1');
      cache.remove('key1');
      expect(cache.get('key1')).toBeUndefined();
    });
  });

  describe('clear', () => {
    it('should clear all items', () => {
      cache.set('a', '1');
      cache.set('b', '2');

      cache.clear();

      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('b')).toBeUndefined();
      expect(cache.size()).toBe(0);
    });
  });

  describe('size', () => {
    it('should return current size', () => {
      expect(cache.size()).toBe(0);

      cache.set('a', '1');
      expect(cache.size()).toBe(1);

      cache.set('b', '2');
      expect(cache.size()).toBe(2);

      cache.remove('a');
      expect(cache.size()).toBe(1);
    });
  });
});

// ============================================================================
// TTL Cache Strategy Tests
// ============================================================================

describe('TTLCacheStrategy', () => {
  let cache: TTLCacheStrategy<string, string>;

  beforeEach(() => {
    cache = new TTLCacheStrategy(100); // 100ms TTL
  });

  afterEach(() => {
    cache.clear();
  });

  describe('basic operations', () => {
    it('should set and get values', () => {
      cache.set('key1', 'value1');
      expect(cache.get('key1')).toBe('value1');
    });

    it('should expire values after TTL', async () => {
      cache.set('key1', 'value1', 50);

      expect(cache.get('key1')).toBe('value1');

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(cache.get('key1')).toBeUndefined();
    });
  });

  describe('TTL renewal', () => {
    it('should reset TTL when value is updated', async () => {
      cache.set('key1', 'value1', 100);

      await new Promise((resolve) => setTimeout(resolve, 60));

      cache.set('key1', 'value2', 100);

      await new Promise((resolve) => setTimeout(resolve, 60));

      expect(cache.get('key1')).toBe('value2');
    });
  });
});

// ============================================================================
// Hybrid Cache Strategy Tests
// ============================================================================

describe('HybridCacheStrategy', () => {
  let cache: HybridCacheStrategy<string, string>;

  beforeEach(() => {
    cache = new HybridCacheStrategy(3, 100); // LRU size 3, TTL 100ms
  });

  afterEach(() => {
    cache.clear();
  });

  describe('LRU + TTL combined', () => {
    it('should evict LRU when at capacity', () => {
      cache.set('a', '1');
      cache.set('b', '2');
      cache.set('c', '3');

      cache.set('d', '4');

      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('d')).toBe('4');
    });

    it('should expire after TTL', async () => {
      cache.set('key1', 'value1', 50);
      expect(cache.get('key1')).toBe('value1');

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(cache.get('key1')).toBeUndefined();
    });
  });
});

// ============================================================================
// API Client Tests
// ============================================================================

describe('ApiClient', () => {
  let mockTransport: ApiTransport;
  let client: ApiClient;

  beforeEach(() => {
    mockTransport = {
      send: vi.fn(),
    };
    client = new ApiClient(mockTransport);
  });

  describe('GET', () => {
    it('should send GET request', async () => {
      const expectedResponse = { id: 1, name: 'test' };
      (mockTransport.send as any).mockResolvedValue({
        status: 200,
        data: expectedResponse,
        headers: {},
      });

      const result = await client.get('/api/test');

      expect(result).toEqual(expectedResponse);
      expect(mockTransport.send).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'GET',
          path: '/api/test',
        })
      );
    });
  });

  describe('POST', () => {
    it('should send POST request with body', async () => {
      const body = { name: 'test' };
      const expectedResponse = { id: 1, ...body };

      (mockTransport.send as any).mockResolvedValue({
        status: 201,
        data: expectedResponse,
        headers: {},
      });

      const result = await client.post('/api/test', body);

      expect(result).toEqual(expectedResponse);
      expect(mockTransport.send).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'POST',
          path: '/api/test',
          body,
        })
      );
    });
  });

  describe('PUT', () => {
    it('should send PUT request', async () => {
      const body = { name: 'updated' };
      const expectedResponse = { id: 1, ...body };

      (mockTransport.send as any).mockResolvedValue({
        status: 200,
        data: expectedResponse,
        headers: {},
      });

      const result = await client.put('/api/test/1', body);

      expect(result).toEqual(expectedResponse);
    });
  });

  describe('DELETE', () => {
    it('should send DELETE request', async () => {
      (mockTransport.send as any).mockResolvedValue({
        status: 204,
        data: null,
        headers: {},
      });

      const result = await client.delete('/api/test/1');

      expect(mockTransport.send).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'DELETE',
          path: '/api/test/1',
        })
      );
    });
  });

  describe('PATCH', () => {
    it('should send PATCH request', async () => {
      const body = { status: 'active' };
      const expectedResponse = { id: 1, ...body };

      (mockTransport.send as any).mockResolvedValue({
        status: 200,
        data: expectedResponse,
        headers: {},
      });

      const result = await client.patch('/api/test/1', body);

      expect(result).toEqual(expectedResponse);
    });
  });

  describe('default headers', () => {
    it('should set and get default headers', () => {
      client.setDefaultHeaders({ 'X-Custom': 'value' });
      const headers = client.getDefaultHeaders();
      expect(headers['X-Custom']).toBe('value');
    });

    it('should include default headers in requests', async () => {
      client.setDefaultHeaders({ Authorization: 'Bearer token' });

      (mockTransport.send as any).mockResolvedValue({
        status: 200,
        data: {},
        headers: {},
      });

      await client.get('/api/test');

      expect(mockTransport.send).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer token',
          }),
        })
      );
    });
  });
});

// ============================================================================
// HTTP Transport Tests
// ============================================================================

describe('HttpTransport', () => {
  let transport: HttpTransport;

  beforeEach(() => {
    transport = new HttpTransport('http://api.example.com');
    global.fetch = vi.fn();
  });

  describe('URL building', () => {
    it('should build correct URL', async () => {
      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map(),
        json: async () => ({ data: 'test' }),
      });

      await transport.send({ method: 'GET', path: '/users' });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://api.example.com/users',
        expect.any(Object)
      );
    });

    it('should add query parameters to URL', async () => {
      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map(),
        json: async () => ({ data: 'test' }),
      });

      await transport.send({
        method: 'GET',
        path: '/users',
        query: { page: 1, limit: 10 },
      });

      const callArgs = (global.fetch as any).mock.calls[0][0];
      expect(callArgs).toContain('page=1');
      expect(callArgs).toContain('limit=10');
    });
  });

  describe('request handling', () => {
    it('should send JSON body', async () => {
      const body = { name: 'test' };

      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map(),
        json: async () => ({ id: 1, ...body }),
      });

      await transport.send({
        method: 'POST',
        path: '/users',
        body,
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify(body),
        })
      );
    });

    it('should handle custom headers', async () => {
      const headers = { 'X-Custom': 'value' };

      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map(),
        json: async () => ({}),
      });

      await transport.send({
        method: 'GET',
        path: '/test',
        headers,
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining(headers),
        })
      );
    });
  });

  describe('response handling', () => {
    it('should parse JSON response', async () => {
      const responseData = { id: 1, name: 'test' };

      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => responseData,
      });

      const response = await transport.send({
        method: 'GET',
        path: '/test',
      });

      expect(response.data).toEqual(responseData);
    });

    it('should handle text response', async () => {
      const responseText = 'plain text response';

      (global.fetch as any).mockResolvedValue({
        status: 200,
        headers: new Map([['content-type', 'text/plain']]),
        text: async () => responseText,
      });

      const response = await transport.send({
        method: 'GET',
        path: '/test',
      });

      expect(response.data).toBe(responseText);
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('Phase 2 Integration', () => {
  describe('CacheManager + HttpTransport', () => {
    it('should cache API responses', async () => {
      const cache = new LRUCacheStrategy<string, any>(100);
      const mockTransport: ApiTransport = {
        send: vi.fn().mockResolvedValue({
          status: 200,
          data: { id: 1, name: 'test' },
          headers: {},
        }),
      };

      const client = new ApiClient(mockTransport);

      // First request
      const result1 = await client.get('/api/test');

      // Cache result
      cache.set('/api/test', result1);

      // Verify cache hit
      const cached = cache.get('/api/test');
      expect(cached).toEqual(result1);
      expect((mockTransport.send as any).mock.calls).toHaveLength(1);
    });
  });

  describe('ApiClient + CacheManager workflow', () => {
    it('should implement complete caching workflow', async () => {
      const manager = new CacheManager();
      manager.register('api', new LRUCacheStrategy<string, any>(50));

      const mockTransport: ApiTransport = {
        send: vi.fn().mockResolvedValue({
          status: 200,
          data: { id: 1 },
          headers: {},
        }),
      };

      const client = new ApiClient(mockTransport);
      const cache = manager.get<string, any>('api');

      // Helper function
      const getWithCache = async (path: string) => {
        const cached = cache.get(path);
        if (cached) return cached;

        const data = await client.get(path);
        cache.set(path, data);
        return data;
      };

      // First call - hits API
      const result1 = await getWithCache('/api/test');
      expect((mockTransport.send as any).mock.calls).toHaveLength(1);

      // Second call - hits cache
      const result2 = await getWithCache('/api/test');
      expect((mockTransport.send as any).mock.calls).toHaveLength(1);
      expect(result1).toEqual(result2);
    });
  });
});

// ============================================================================
// Error Handling Tests
// ============================================================================

describe('Error Handling', () => {
  describe('ApiClient error handling', () => {
    it('should handle transport errors', async () => {
      const mockTransport: ApiTransport = {
        send: vi
          .fn()
          .mockRejectedValue(new Error('Network error')),
      };

      const client = new ApiClient(mockTransport);

      await expect(client.get('/api/test')).rejects.toThrow(
        'Network error'
      );
    });
  });

  describe('Cache manager edge cases', () => {
    it('should handle max size validation', () => {
      expect(() => new LRUCacheStrategy(0)).toThrow(
        'maxSize must be greater than 0'
      );
    });

    it('should handle TTL validation', () => {
      expect(() => new TTLCacheStrategy(0)).toThrow(
        'defaultTtlMs must be greater than 0'
      );
    });
  });
});
