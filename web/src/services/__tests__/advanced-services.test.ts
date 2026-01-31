/**
 * Unit Tests for CircuitBreaker, Dependency Injection, and ValidationErrorSuggester
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CircuitBreaker, CircuitBreakerError, type CircuitBreakerState } from '../services/circuitBreaker';
import { PythonBridgeProvider, MockPythonBridgeFactory } from '../services/pythonBridgeProvider';
import { ValidationErrorSuggester, type ErrorCode, type ValidationErrorSuggestion } from '../services/validationErrorSuggester';

/**
 * CircuitBreaker Tests
 */
describe('CircuitBreaker', () => {
  let breaker: CircuitBreaker;
  let operation: any;
  let stateChanges: CircuitBreakerState[] = [];

  beforeEach(() => {
    stateChanges = [];
    operation = vi.fn();
  });

  describe('Basic Operation', () => {
    it('should execute successful operations', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 3,
        successThreshold: 2,
        timeout: 1000,
      });

      const result = await breaker.execute();
      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(1);
    });

    it('should allow multiple successful operations', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 3,
        successThreshold: 2,
        timeout: 1000,
      });

      await breaker.execute();
      await breaker.execute();
      await breaker.execute();

      expect(operation).toHaveBeenCalledTimes(3);
    });

    it('should pass through operation errors', async () => {
      const error = new Error('Operation failed');
      operation.mockRejectedValue(error);
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 3,
        successThreshold: 2,
        timeout: 1000,
      });

      await expect(breaker.execute()).rejects.toThrow('Operation failed');
    });
  });

  describe('CLOSED to OPEN Transition', () => {
    it('should transition to OPEN after failure threshold', async () => {
      operation.mockRejectedValue(new Error('Failed'));
      breaker = new CircuitBreaker(
        operation,
        { failureThreshold: 3, successThreshold: 2, timeout: 1000 },
        (state) => stateChanges.push(state)
      );

      // First 2 failures should keep it CLOSED
      for (let i = 0; i < 2; i++) {
        try {
          await breaker.execute();
        } catch {}
      }
      expect(breaker.getState()).toBe('CLOSED');

      // 3rd failure should open circuit
      try {
        await breaker.execute();
      } catch {}
      expect(breaker.getState()).toBe('OPEN');
      expect(stateChanges).toContain('OPEN');
    });

    it('should reject requests when OPEN', async () => {
      operation.mockRejectedValue(new Error('Failed'));
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 1,
        successThreshold: 2,
        timeout: 1000,
      });

      // Open the circuit
      try {
        await breaker.execute();
      } catch {}
      expect(breaker.getState()).toBe('OPEN');

      // Next request should fail with CircuitBreakerError
      await expect(breaker.execute()).rejects.toThrow(CircuitBreakerError);
    });
  });

  describe('OPEN to HALF_OPEN Transition', () => {
    it('should transition to HALF_OPEN after timeout', async () => {
      operation.mockRejectedValue(new Error('Failed'));
      const timeout = 100;
      breaker = new CircuitBreaker(
        operation,
        { failureThreshold: 1, successThreshold: 2, timeout },
        (state) => stateChanges.push(state)
      );

      // Open circuit
      try {
        await breaker.execute();
      } catch {}
      expect(breaker.getState()).toBe('OPEN');

      // Wait for timeout
      await new Promise(resolve => setTimeout(resolve, timeout + 50));

      // Next attempt should transition to HALF_OPEN
      operation.mockResolvedValue('success');
      await breaker.execute();
      expect(breaker.getState()).toBe('HALF_OPEN');
      expect(stateChanges).toContain('HALF_OPEN');
    });
  });

  describe('HALF_OPEN to CLOSED Transition', () => {
    it('should transition to CLOSED after success threshold', async () => {
      operation.mockRejectedValue(new Error('Failed'));
      breaker = new CircuitBreaker(
        operation,
        { failureThreshold: 1, successThreshold: 2, timeout: 100 },
        (state) => stateChanges.push(state)
      );

      // Open circuit
      try {
        await breaker.execute();
      } catch {}

      // Wait for timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      // Succeed twice to close
      operation.mockResolvedValue('success');
      await breaker.execute();
      await breaker.execute();

      expect(breaker.getState()).toBe('CLOSED');
      expect(stateChanges).toContain('CLOSED');
    });
  });

  describe('Metrics', () => {
    it('should track metrics correctly', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 1000,
      });

      await breaker.execute();
      await breaker.execute();
      operation.mockRejectedValue(new Error('Failed'));
      try {
        await breaker.execute();
      } catch {}

      const metrics = breaker.getMetrics();
      expect(metrics.totalRequests).toBe(3);
      expect(metrics.successCount).toBe(2);
      expect(metrics.failureCount).toBe(1);
    });

    it('should calculate success rate', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 1000,
      });

      await breaker.execute();
      await breaker.execute();
      operation.mockRejectedValue(new Error('Failed'));
      try {
        await breaker.execute();
      } catch {}

      expect(breaker.getSuccessRate()).toBe(66.66666666666666);
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', async () => {
      operation.mockRejectedValue(new Error('Failed'));
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 1,
        successThreshold: 2,
        timeout: 1000,
      });

      try {
        await breaker.execute();
      } catch {}
      expect(breaker.getState()).toBe('OPEN');

      breaker.reset();
      expect(breaker.getState()).toBe('CLOSED');
      const metrics = breaker.getMetrics();
      expect(metrics.totalRequests).toBe(0);
      expect(metrics.successCount).toBe(0);
      expect(metrics.failureCount).toBe(0);
    });
  });
});

/**
 * PythonBridgeProvider Tests
 */
describe('PythonBridgeProvider', () => {
  beforeEach(() => {
    PythonBridgeProvider.reset();
  });

  describe('Basic Injection', () => {
    it('should create default instance', () => {
      const instance = PythonBridgeProvider.getInstance();
      expect(instance).toBeDefined();
    });

    it('should return same instance', () => {
      const instance1 = PythonBridgeProvider.getInstance();
      const instance2 = PythonBridgeProvider.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Custom Factory', () => {
    it('should use custom factory', () => {
      const mockBridge = {
        initialize: vi.fn(),
        sendRequest: vi.fn(),
        disconnect: vi.fn(),
        isConnected: vi.fn(),
        health: vi.fn(),
        requestQueue: vi.fn(),
        requestMetrics: vi.fn(),
      };

      const factory = new MockPythonBridgeFactory(mockBridge);
      PythonBridgeProvider.setFactory(factory);

      const instance = PythonBridgeProvider.getInstance();
      expect(instance).toBe(mockBridge);
    });

    it('should reset to default factory', () => {
      const mockBridge = {
        initialize: vi.fn(),
        sendRequest: vi.fn(),
        disconnect: vi.fn(),
        isConnected: vi.fn(),
        health: vi.fn(),
        requestQueue: vi.fn(),
        requestMetrics: vi.fn(),
      };

      PythonBridgeProvider.setFactory(new MockPythonBridgeFactory(mockBridge));
      PythonBridgeProvider.reset();

      const instance = PythonBridgeProvider.getInstance();
      expect(instance).not.toBe(mockBridge);
    });
  });
});

/**
 * ValidationErrorSuggester Tests
 */
describe('ValidationErrorSuggester', () => {
  let suggester: ValidationErrorSuggester;

  beforeEach(() => {
    suggester = new ValidationErrorSuggester();
  });

  describe('Basic Suggestions', () => {
    it('should return suggestion for known error code', () => {
      const suggestion = suggester.getSuggestion('INVALID_TEMPLATE_SYNTAX');
      expect(suggestion).toBeDefined();
      expect(suggestion?.code).toBe('INVALID_TEMPLATE_SYNTAX');
      expect(suggestion?.suggestions.length).toBeGreaterThan(0);
    });

    it('should return null for unknown error code', () => {
      const suggestion = suggester.getSuggestion('UNKNOWN_ERROR');
      expect(suggestion).toBeNull();
    });

    it('should return all suggestions', () => {
      const all = suggester.getAllSuggestions();
      expect(all.length).toBeGreaterThan(0);
    });
  });

  describe('Context-Aware Suggestions', () => {
    it('should enhance suggestions with context', () => {
      const suggestion = suggester.getSuggestionWithContext('UNDEFINED_VARIABLE', {
        fieldName: 'CustomField',
      });
      expect(suggestion).toBeDefined();
      expect(suggestion?.suggestions.some(s => s.includes('CustomField'))).toBe(true);
    });

    it('should enhance timeout error with timeout context', () => {
      const suggestion = suggester.getSuggestionWithContext('PYTHON_BRIDGE_TIMEOUT', {
        timeout: 5000,
      });
      expect(suggestion).toBeDefined();
      expect(suggestion?.suggestions.some(s => s.includes('5000ms'))).toBe(true);
    });
  });

  describe('Custom Suggestions', () => {
    it('should add custom suggestion', () => {
      suggester.addSuggestion({
        code: 'CUSTOM_ERROR',
        message: 'Custom error',
        suggestions: ['Suggestion 1', 'Suggestion 2'],
      });

      const suggestion = suggester.getSuggestion('CUSTOM_ERROR');
      expect(suggestion).toBeDefined();
      expect(suggestion?.code).toBe('CUSTOM_ERROR');
    });
  });

  describe('Formatting', () => {
    it('should format suggestion for display', () => {
      const suggestion = suggester.getSuggestion('INVALID_TEMPLATE_SYNTAX');
      expect(suggestion).toBeDefined();

      const formatted = suggester.formatSuggestion(suggestion!);
      expect(formatted).toContain('Template contains invalid syntax');
      expect(formatted).toContain('Suggestions:');
    });

    it('should include examples in formatted output', () => {
      const suggestion = suggester.getSuggestion('INVALID_TEMPLATE_SYNTAX');
      expect(suggestion).toBeDefined();

      const formatted = suggester.formatSuggestion(suggestion!);
      expect(formatted).toContain('Examples:');
    });

    it('should provide type-safe error code checking', () => {
      // This test verifies compile-time type safety
      // TypeScript will catch invalid codes at compile time
      const validCode: ErrorCode = 'INVALID_TEMPLATE_SYNTAX';
      const suggestion = suggester.getSuggestion(validCode);
      expect(suggestion).toBeDefined();
    });

    it('should validate error codes when adding suggestions', () => {
      const validSuggestion: ValidationErrorSuggestion = {
        code: 'INVALID_TEMPLATE_SYNTAX',
        message: 'Test',
        suggestions: ['test'],
      };

      expect(() => {
        suggester.addSuggestion(validSuggestion);
      }).not.toThrow();
    });

    it('should handle runtime error code lookup', () => {
      const suggestion = suggester.getSuggestionRuntime('INVALID_TEMPLATE_SYNTAX');
      expect(suggestion).toBeDefined();

      const invalidSuggestion = suggester.getSuggestionRuntime('NONEXISTENT_CODE');
      expect(invalidSuggestion).toBeNull();
    });
  });

  describe('Error Code Type Safety', () => {
    let suggester: ValidationErrorSuggester;

    beforeEach(() => {
      suggester = new ValidationErrorSuggester();
    });

    it('should reject invalid error codes', () => {
      const invalidSuggestion = {
        code: 'INVALID_CODE_TYPE' as any,
        message: 'Test',
        suggestions: [],
      };

      expect(() => {
        suggester.addSuggestion(invalidSuggestion);
      }).toThrow();
    });

    it('should accept all valid error codes', () => {
      const validCodes = [
        'INVALID_TEMPLATE_SYNTAX',
        'MISSING_REQUIRED_FIELD',
        'INVALID_CSS_SYNTAX',
        'INVALID_HTML_SYNTAX',
        'FIELD_NAME_MISMATCH',
        'CIRCULAR_DEPENDENCY',
        'INVALID_PYTHON_BRIDGE_REQUEST',
        'PYTHON_BRIDGE_TIMEOUT',
        'PYTHON_BRIDGE_CONNECTION_FAILED',
      ] as const;

      validCodes.forEach((code) => {
        const suggestion = suggester.getSuggestion(code);
        expect(suggestion).toBeDefined();
      });
    });
  });
});

describe('CircuitBreaker - Enhanced Metrics', () => {
  let breaker: CircuitBreaker<string>;
  let operation: any;

  beforeEach(() => {
    operation = vi.fn();
  });

  describe('Response Time Tracking', () => {
    it('should track response times', async () => {
      operation.mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve('success'), 50);
        });
      });

      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      await breaker.execute();
      const metrics = breaker.getMetrics();
      expect(metrics.p50ResponseTime).toBeGreaterThanOrEqual(0);
    });

    it('should calculate response time percentiles', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      // Execute multiple times
      for (let i = 0; i < 10; i++) {
        await breaker.execute();
      }

      const metrics = breaker.getMetrics();
      expect(metrics.p50ResponseTime).toBeDefined();
      expect(metrics.p95ResponseTime).toBeDefined();
      expect(metrics.p99ResponseTime).toBeDefined();
      expect(metrics.averageResponseTime).toBeGreaterThanOrEqual(0);
    });

    it('should maintain percentile order', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      for (let i = 0; i < 10; i++) {
        await breaker.execute();
      }

      const metrics = breaker.getMetrics();
      expect(metrics.p50ResponseTime).toBeLessThanOrEqual(metrics.p95ResponseTime);
      expect(metrics.p95ResponseTime).toBeLessThanOrEqual(metrics.p99ResponseTime);
    });

    it('should return 0 for empty response times', () => {
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      const metrics = breaker.getMetrics();
      expect(metrics.p50ResponseTime).toBe(0);
      expect(metrics.p95ResponseTime).toBe(0);
      expect(metrics.p99ResponseTime).toBe(0);
      expect(metrics.averageResponseTime).toBe(0);
    });
  });

  describe('State Duration Tracking', () => {
    it('should track time spent in CLOSED state', async () => {
      operation.mockResolvedValue('success');
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      await breaker.execute();
      const closedDuration = breaker.getAverageStateDuration('CLOSED');
      expect(closedDuration).toBeGreaterThanOrEqual(0);
    });

    it('should track time spent in OPEN state', async () => {
      operation.mockRejectedValue(new Error('fail'));
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 2,
        successThreshold: 2,
        timeout: 10000,
      });

      // Trigger failures to open circuit
      for (let i = 0; i < 2; i++) {
        try {
          await breaker.execute();
        } catch {}
      }

      const openDuration = breaker.getAverageStateDuration('OPEN');
      expect(openDuration).toBeGreaterThanOrEqual(0);
    });

    it('should track time spent in HALF_OPEN state', async () => {
      operation.mockRejectedValue(new Error('fail'));
      breaker = new CircuitBreaker(operation, {
        failureThreshold: 2,
        successThreshold: 1,
        timeout: 100,
      });

      // Trigger failures to open circuit
      for (let i = 0; i < 2; i++) {
        try {
          await breaker.execute();
        } catch {}
      }

      // Wait for timeout to transition to HALF_OPEN
      await new Promise(resolve => setTimeout(resolve, 150));

      // Try again to trigger HALF_OPEN
      operation.mockResolvedValue('success');
      await breaker.execute();

      const halfOpenDuration = breaker.getAverageStateDuration('HALF_OPEN');
      expect(halfOpenDuration).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Generic Type Parameter', () => {
    it('should support generic type parameter', async () => {
      interface CustomResult {
        status: string;
        data: number;
      }

      const customOp = vi.fn<[], Promise<CustomResult>>();
      customOp.mockResolvedValue({ status: 'ok', data: 42 });

      const typedBreaker = new CircuitBreaker<CustomResult>(customOp, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      const result = await typedBreaker.execute();
      expect(result.status).toBe('ok');
      expect(result.data).toBe(42);
    });

    it('should infer generic type from operation', async () => {
      const stringOp = vi.fn<[], Promise<string>>();
      stringOp.mockResolvedValue('test result');

      const stringBreaker = new CircuitBreaker(stringOp, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      const result = await stringBreaker.execute();
      expect(typeof result).toBe('string');
      expect(result).toBe('test result');
    });

    it('should work with custom types', async () => {
      interface RequestResult {
        requestId: string;
        timestamp: number;
        success: boolean;
      }

      const op = vi.fn<[], Promise<RequestResult>>();
      op.mockResolvedValue({
        requestId: 'abc123',
        timestamp: Date.now(),
        success: true,
      });

      const breaker = new CircuitBreaker<RequestResult>(op, {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 10000,
      });

      const result = await breaker.execute();
      expect(result.requestId).toBe('abc123');
      expect(result.success).toBe(true);
    });
  });
});
