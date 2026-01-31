/**
 * Unit Tests for Configuration Validation
 */

import { describe, it, expect } from 'vitest';
import {
  validateBridgeConfig,
  validateAndGetConfig,
  type ConfigValidationError,
  BRIDGE_CONFIG,
  VALIDATION_CONFIG,
} from '../config';

describe('Configuration Validation', () => {
  describe('validateBridgeConfig - Timeout Validation', () => {
    it('should accept valid timeout values', () => {
      const config = { timeout: 30000 };
      const errors = validateBridgeConfig(config);
      expect(errors.filter(e => e.field === 'timeout')).toHaveLength(0);
    });

    it('should reject timeout less than 1000ms', () => {
      const config = { timeout: 500 };
      const errors = validateBridgeConfig(config);
      const timeoutError = errors.find(e => e.field === 'timeout');
      expect(timeoutError).toBeDefined();
      expect(timeoutError?.message).toContain('at least 1000ms');
    });

    it('should reject timeout greater than 300000ms', () => {
      const config = { timeout: 400000 };
      const errors = validateBridgeConfig(config);
      const timeoutError = errors.find(e => e.field === 'timeout');
      expect(timeoutError).toBeDefined();
      expect(timeoutError?.message).toContain('should not exceed 300000ms');
    });

    it('should reject non-numeric timeout', () => {
      const config = { timeout: '30000' };
      const errors = validateBridgeConfig(config);
      const timeoutError = errors.find(e => e.field === 'timeout');
      expect(timeoutError).toBeDefined();
      expect(timeoutError?.message).toContain('must be a number');
    });

    it('should accept timeout at boundaries', () => {
      const configMin = { timeout: 1000 };
      const configMax = { timeout: 300000 };

      const errorsMin = validateBridgeConfig(configMin);
      const errorsMax = validateBridgeConfig(configMax);

      expect(errorsMin.filter(e => e.field === 'timeout')).toHaveLength(0);
      expect(errorsMax.filter(e => e.field === 'timeout')).toHaveLength(0);
    });
  });

  describe('validateBridgeConfig - Retry Configuration', () => {
    it('should validate maxRetries range', () => {
      const validConfig = { retry: { maxRetries: 5 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'retry.maxRetries')).toHaveLength(0);

      const invalidConfig = { retry: { maxRetries: 15 } };
      const invalidErrors = validateBridgeConfig(invalidConfig);
      expect(invalidErrors.filter(e => e.field === 'retry.maxRetries')).toHaveLength(1);
    });

    it('should validate baseDelay range', () => {
      const validConfig = { retry: { baseDelay: 500 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'retry.baseDelay')).toHaveLength(0);

      const tooSmallConfig = { retry: { baseDelay: 5 } };
      const tooSmallErrors = validateBridgeConfig(tooSmallConfig);
      expect(tooSmallErrors.filter(e => e.field === 'retry.baseDelay')).toHaveLength(1);
    });

    it('should validate maxDelay >= baseDelay', () => {
      const validConfig = { retry: { baseDelay: 100, maxDelay: 5000 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'retry.maxDelay')).toHaveLength(0);

      const invalidConfig = { retry: { baseDelay: 5000, maxDelay: 100 } };
      const invalidErrors = validateBridgeConfig(invalidConfig);
      expect(invalidErrors.filter(e => e.field === 'retry.maxDelay')).toHaveLength(1);
    });

    it('should validate backoffMultiplier range', () => {
      const validConfig = { retry: { backoffMultiplier: 2 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'retry.backoffMultiplier')).toHaveLength(0);

      const invalidConfig = { retry: { backoffMultiplier: 15 } };
      const invalidErrors = validateBridgeConfig(invalidConfig);
      expect(invalidErrors.filter(e => e.field === 'retry.backoffMultiplier')).toHaveLength(1);
    });
  });

  describe('validateBridgeConfig - Circuit Breaker', () => {
    it('should validate failureThreshold range', () => {
      const validConfig = { circuitBreaker: { failureThreshold: 5 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'circuitBreaker.failureThreshold')).toHaveLength(0);

      const invalidConfig = { circuitBreaker: { failureThreshold: 150 } };
      const invalidErrors = validateBridgeConfig(invalidConfig);
      expect(invalidErrors.filter(e => e.field === 'circuitBreaker.failureThreshold')).toHaveLength(1);
    });

    it('should validate successThreshold range', () => {
      const validConfig = { circuitBreaker: { successThreshold: 2 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'circuitBreaker.successThreshold')).toHaveLength(0);

      const invalidConfig = { circuitBreaker: { successThreshold: 100 } };
      const invalidErrors = validateBridgeConfig(invalidConfig);
      expect(invalidErrors.filter(e => e.field === 'circuitBreaker.successThreshold')).toHaveLength(1);
    });

    it('should validate circuit breaker timeout range', () => {
      const validConfig = { circuitBreaker: { timeout: 60000 } };
      const errors = validateBridgeConfig(validConfig);
      expect(errors.filter(e => e.field === 'circuitBreaker.timeout')).toHaveLength(0);

      const tooSmallConfig = { circuitBreaker: { timeout: 5000 } };
      const tooSmallErrors = validateBridgeConfig(tooSmallConfig);
      expect(tooSmallErrors.filter(e => e.field === 'circuitBreaker.timeout')).toHaveLength(1);

      const tooLargeConfig = { circuitBreaker: { timeout: 700000 } };
      const tooLargeErrors = validateBridgeConfig(tooLargeConfig);
      expect(tooLargeErrors.filter(e => e.field === 'circuitBreaker.timeout')).toHaveLength(1);
    });
  });

  describe('validateAndGetConfig - Complete Validation', () => {
    it('should return valid config with no errors', () => {
      const config = {
        timeout: 30000,
        retry: { maxRetries: 3, baseDelay: 100, maxDelay: 5000, backoffMultiplier: 2 },
        circuitBreaker: { failureThreshold: 5, successThreshold: 2, timeout: 60000 },
      };

      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.config).toEqual(config);
    });

    it('should report errors', () => {
      const config = {
        timeout: 500, // Invalid
        retry: { maxRetries: 20 }, // Invalid
        circuitBreaker: { failureThreshold: 200 }, // Invalid
      };

      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should provide warnings for suboptimal configurations', () => {
      const config = {
        timeout: 3000, // Warning: < 5000ms
        circuitBreaker: { failureThreshold: 1 }, // Warning: too quick to open
      };

      const result = validateAndGetConfig(config);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings.some(w => w.includes('5000ms'))).toBe(true);
      expect(result.warnings.some(w => w.includes('failureThreshold'))).toBe(true);
    });

    it('should validate config with only timeout', () => {
      const config = { timeout: 30000 };
      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate config with only retry settings', () => {
      const config = { retry: { maxRetries: 5, baseDelay: 100 } };
      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate circuit breaker settings', () => {
      const config = {
        circuitBreaker: {
          failureThreshold: 5,
          successThreshold: 2,
          timeout: 60000,
        },
      };

      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('Default Configuration Validation', () => {
    it('should validate default BRIDGE_CONFIG', () => {
      const result = validateAndGetConfig(BRIDGE_CONFIG);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate default VALIDATION_CONFIG', () => {
      // VALIDATION_CONFIG doesn't need bridge validation but should be well-formed
      expect(VALIDATION_CONFIG).toBeDefined();
      expect(VALIDATION_CONFIG.field).toBeDefined();
      expect(VALIDATION_CONFIG.html).toBeDefined();
      expect(VALIDATION_CONFIG.css).toBeDefined();
    });
  });

  describe('Configuration Error Details', () => {
    it('should include field name in error', () => {
      const config = { timeout: 500 };
      const errors = validateBridgeConfig(config);
      const timeoutError = errors[0];

      expect(timeoutError.field).toBe('timeout');
      expect(timeoutError.value).toBe(500);
      expect(timeoutError.message).toBeDefined();
    });

    it('should include value in error for debugging', () => {
      const config = { retry: { maxRetries: 25 } };
      const errors = validateBridgeConfig(config);
      const retryError = errors.find(e => e.field === 'retry.maxRetries');

      expect(retryError?.value).toBe(25);
      expect(typeof retryError?.message).toBe('string');
    });

    it('should provide actionable error messages', () => {
      const config = { timeout: 100 };
      const errors = validateBridgeConfig(config);
      const timeoutError = errors[0];

      // Error message should tell user what the constraint is
      expect(timeoutError.message).toMatch(/\d+/); // Contains number
      expect(timeoutError.message.toLowerCase()).toMatch(/timeout|millisecond|ms|second/);
    });
  });

  describe('Boundary Testing', () => {
    it('should accept minimum valid values', () => {
      const config = {
        timeout: 1000,
        retry: { maxRetries: 0, baseDelay: 10, maxDelay: 10, backoffMultiplier: 1 },
        circuitBreaker: { failureThreshold: 1, successThreshold: 1, timeout: 10000 },
      };

      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
    });

    it('should accept maximum valid values', () => {
      const config = {
        timeout: 300000,
        retry: { maxRetries: 10, baseDelay: 5000, maxDelay: 5000, backoffMultiplier: 10 },
        circuitBreaker: { failureThreshold: 100, successThreshold: 50, timeout: 600000 },
      };

      const result = validateAndGetConfig(config);
      expect(result.isValid).toBe(true);
    });

    it('should reject values just outside boundaries', () => {
      const tooSmall = { timeout: 999 };
      const tooLarge = { timeout: 300001 };

      expect(validateBridgeConfig(tooSmall).length).toBeGreaterThan(0);
      expect(validateBridgeConfig(tooLarge).length).toBeGreaterThan(0);
    });
  });
});
