/**
 * Integration Tests for Advanced Services with PythonBridge
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CircuitBreaker } from '../services/circuitBreaker';
import { PythonBridgeProvider, MockPythonBridgeFactory } from '../services/pythonBridgeProvider';
import { ValidationErrorSuggester } from '../services/validationErrorSuggester';

/**
 * CircuitBreaker + PythonBridge Integration
 */
describe('CircuitBreaker with PythonBridge', () => {
  let mockBridge: any;
  let breaker: CircuitBreaker;
  let suggester: ValidationErrorSuggester;

  beforeEach(() => {
    mockBridge = {
      initialize: vi.fn().mockResolvedValue(undefined),
      sendRequest: vi.fn(),
      disconnect: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true),
      health: vi.fn().mockResolvedValue({ status: 'healthy' }),
      requestQueue: vi.fn().mockReturnValue([]),
      requestMetrics: vi.fn().mockReturnValue({}),
    };

    PythonBridgeProvider.setFactory(new MockPythonBridgeFactory(mockBridge));
    suggester = new ValidationErrorSuggester();
  });

  it('should protect against cascading Python bridge failures', async () => {
    // Setup circuit breaker for Python bridge
    const bridge = PythonBridgeProvider.getInstance();
    mockBridge.sendRequest.mockRejectedValue(new Error('Backend unavailable'));

    breaker = new CircuitBreaker(
      () => bridge.sendRequest({ type: 'compile', template: '<div></div>' }),
      { failureThreshold: 2, successThreshold: 2, timeout: 100 }
    );

    // First two requests fail
    for (let i = 0; i < 2; i++) {
      try {
        await breaker.execute();
      } catch (e) {
        expect(e).toBeDefined();
      }
    }

    // Circuit should be OPEN
    expect(breaker.getState()).toBe('OPEN');

    // Next request should fail with CircuitBreakerError, not call backend
    try {
      await breaker.execute();
    } catch (error: any) {
      expect(error.code).toBe('CIRCUIT_BREAKER_OPEN');
      // Should not call sendRequest again
      expect(mockBridge.sendRequest).toHaveBeenCalledTimes(2);
    }
  });

  it('should recover from backend temporary failure', async () => {
    const bridge = PythonBridgeProvider.getInstance();
    mockBridge.sendRequest
      .mockRejectedValueOnce(new Error('Failed'))
      .mockResolvedValue({ success: true });

    breaker = new CircuitBreaker(
      () => bridge.sendRequest({ type: 'compile', template: '<div></div>' }),
      { failureThreshold: 1, successThreshold: 1, timeout: 50 }
    );

    // Fail once to open
    try {
      await breaker.execute();
    } catch {}
    expect(breaker.getState()).toBe('OPEN');

    // Wait for timeout
    await new Promise(resolve => setTimeout(resolve, 100));

    // Succeed to close
    const result = await breaker.execute();
    expect(breaker.getState()).toBe('CLOSED');
    expect(result).toEqual({ success: true });
  });

  it('should handle validation errors with suggestions', async () => {
    const bridge = PythonBridgeProvider.getInstance();
    const validationError = new Error('UNDEFINED_VARIABLE');
    (validationError as any).code = 'UNDEFINED_VARIABLE';
    mockBridge.sendRequest.mockRejectedValue(validationError);

    breaker = new CircuitBreaker(
      () => bridge.sendRequest({ type: 'validate', template: '<div>{{Undefined}}</div>' }),
      { failureThreshold: 3, successThreshold: 2, timeout: 1000 }
    );

    try {
      await breaker.execute();
    } catch (error: any) {
      const suggestion = suggester.getSuggestionWithContext('UNDEFINED_VARIABLE', {
        fieldName: 'Undefined',
      });
      expect(suggestion).toBeDefined();
      expect(suggestion?.suggestions.some(s => s.includes('Undefined'))).toBe(true);
    }
  });
});

/**
 * Error Handling Flow Integration
 */
describe('Complete Error Handling Flow', () => {
  let suggester: ValidationErrorSuggester;

  beforeEach(() => {
    suggester = new ValidationErrorSuggester();
  });

  it('should provide comprehensive error guidance', () => {
    const errorCode = 'PYTHON_BRIDGE_CONNECTION_FAILED';
    const suggestion = suggester.getSuggestion(errorCode);

    expect(suggestion).toBeDefined();
    expect(suggestion?.suggestions.length).toBeGreaterThan(0);
    expect(suggestion?.examples).toBeDefined();

    const formatted = suggester.formatSuggestion(suggestion!);
    expect(formatted).toContain('Cannot connect to Python backend');
    expect(formatted).toContain('Suggestions:');
    expect(formatted).toContain('Examples:');
  });

  it('should handle multiple error types', () => {
    const errorCodes = [
      'INVALID_TEMPLATE_SYNTAX',
      'INVALID_CSS_SYNTAX',
      'UNDEFINED_VARIABLE',
      'CIRCULAR_DEPENDENCY',
    ];

    errorCodes.forEach(code => {
      const suggestion = suggester.getSuggestion(code);
      expect(suggestion).toBeDefined();
      expect(suggestion?.code).toBe(code);
      expect(suggestion?.suggestions.length).toBeGreaterThan(0);
    });
  });
});

/**
 * Performance and Resilience Tests
 */
describe('Performance and Resilience', () => {
  it('should handle rapid circuit breaker state changes', async () => {
    let callCount = 0;
    const operation = vi.fn().mockImplementation(async () => {
      callCount++;
      if (callCount % 3 === 0) throw new Error('Fail');
      return 'success';
    });

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 2,
      successThreshold: 1,
      timeout: 10,
    });

    const results = [];
    for (let i = 0; i < 20; i++) {
      try {
        results.push(await breaker.execute());
      } catch (e) {
        results.push('error');
      }
    }

    expect(results.length).toBe(20);
    expect(breaker.getMetrics().totalRequests).toBe(20);
  });

  it('should track metrics under load', async () => {
    let successCount = 0;
    const operation = vi.fn().mockImplementation(async () => {
      successCount++;
      if (successCount > 5 && successCount < 8) throw new Error('Temporary failure');
      return 'success';
    });

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 2,
      successThreshold: 2,
      timeout: 10,
    });

    for (let i = 0; i < 15; i++) {
      try {
        await breaker.execute();
      } catch {}
    }

    const metrics = breaker.getMetrics();
    expect(metrics.totalRequests).toBeGreaterThan(10);
  });

  it('should efficiently provide error suggestions for large batches', () => {
    const suggester = new ValidationErrorSuggester();
    const errors = Array(1000).fill('INVALID_TEMPLATE_SYNTAX');

    const startTime = performance.now();
    errors.forEach(error => {
      suggester.getSuggestion(error);
    });
    const endTime = performance.now();

    expect(endTime - startTime).toBeLessThan(100); // Should complete in < 100ms
  });
});
