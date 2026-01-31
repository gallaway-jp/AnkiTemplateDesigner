# Error Handling & Fault Tolerance - Developer Guide

**Quick Reference for Developers**  
**Date**: January 21, 2026

---

## Table of Contents

1. [Using Circuit Breaker](#1-using-circuit-breaker)
2. [Error Type Safety](#2-error-type-safety)
3. [Configuration Validation](#3-configuration-validation)
4. [Error Recovery](#4-error-recovery)
5. [Testing Error Scenarios](#5-testing-error-scenarios)
6. [Common Patterns](#6-common-patterns)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Using Circuit Breaker

### Basic Usage

```typescript
import { CircuitBreaker } from '@/services/circuitBreaker';

// Create circuit breaker with operation and config
const breaker = new CircuitBreaker<string>(
  async () => {
    // Your async operation
    return await pythonBridge.sendRequest({ /* ... */ });
  },
  {
    failureThreshold: 5,    // Open after 5 failures
    successThreshold: 2,    // Close after 2 successes
    timeout: 60000,         // Wait 60s before retry
  }
);

// Execute with circuit breaker protection
try {
  const result = await breaker.execute();
  console.log('Success:', result);
} catch (error) {
  if (error instanceof CircuitBreakerError) {
    if (error.code === 'CIRCUIT_BREAKER_OPEN') {
      // Service temporarily unavailable
      console.log('Retry in:', error.details.timeUntilRetry, 'ms');
      // Show user: "Service is temporarily unavailable, please try again in a moment"
    }
  } else {
    // Other errors from the operation
    console.error('Operation failed:', error);
  }
}
```

### With State Change Monitoring

```typescript
const breaker = new CircuitBreaker(
  operation,
  config,
  (newState, metrics) => {
    // Called when circuit state changes
    console.log(`Circuit state changed to: ${newState}`);
    
    if (newState === 'OPEN') {
      // Notify user that service is temporarily down
      showNotification('Service temporarily unavailable');
      
      // Log for monitoring
      logMetric('circuit_opened', {
        failureCount: metrics.failureCount,
        failureRate: metrics.failureCount / metrics.totalRequests,
      });
    }
    
    if (newState === 'CLOSED') {
      // Service recovered
      showNotification('Service recovered');
    }
  }
);
```

### Checking Metrics

```typescript
// Get current metrics
const metrics = breaker.getMetrics();

console.log(`State: ${metrics.state}`);
console.log(`Success rate: ${metrics.successRate}%`);
console.log(`Total requests: ${metrics.totalRequests}`);
console.log(`Failures: ${metrics.failureCount}`);

// Performance metrics
console.log(`Response times (ms):`);
console.log(`  p50: ${metrics.p50ResponseTime}`);
console.log(`  p95: ${metrics.p95ResponseTime}`);
console.log(`  p99: ${metrics.p99ResponseTime}`);
console.log(`  avg: ${metrics.averageResponseTime}`);

// State duration
console.log(`Avg time in OPEN state: ${breaker.getAverageStateDuration('OPEN')}ms`);
```

### Real-World Example: API Call with Circuit Breaker

```typescript
class TemplateService {
  private breaker: CircuitBreaker<TemplateResult>;

  constructor(private pythonBridge: PythonBridge) {
    // Create breaker once, reuse for all template operations
    this.breaker = new CircuitBreaker(
      () => pythonBridge.sendRequest({ type: 'validate' }),
      {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 60000,
      },
      this.onCircuitStateChange.bind(this)
    );
  }

  async validateTemplate(template: string): Promise<TemplateResult> {
    try {
      // CircuitBreaker protects against cascading failures
      const result = await this.breaker.execute();
      return result;
    } catch (error) {
      if (error instanceof CircuitBreakerError) {
        if (error.code === 'CIRCUIT_BREAKER_OPEN') {
          // Service is down - use cached result or show message
          return this.getLastKnownGoodResult() || {
            valid: false,
            errors: ['Service temporarily unavailable'],
          };
        }
      }
      // Re-throw other errors
      throw error;
    }
  }

  private onCircuitStateChange(
    state: CircuitBreakerState,
    metrics: CircuitBreakerMetrics
  ) {
    console.log(`Circuit breaker changed to ${state}`);
    
    // Send metrics to monitoring system
    this.sendToMonitoring({
      event: 'circuit_state_changed',
      state,
      metrics: {
        totalRequests: metrics.totalRequests,
        failureCount: metrics.failureCount,
        successRate: (metrics.successCount / metrics.totalRequests) * 100,
      },
    });
  }

  private getLastKnownGoodResult(): TemplateResult | null {
    // Could cache last successful result
    return null;
  }

  private sendToMonitoring(data: any) {
    // Send to Datadog, New Relic, etc.
  }
}
```

---

## 2. Error Type Safety

### Using ErrorCode Union

```typescript
import {
  ValidationErrorSuggester,
  type ErrorCode,
} from '@/services/validationErrorSuggester';

const suggester = new ValidationErrorSuggester();

// ✅ Correct - TypeScript knows this is valid
const suggestion = suggester.getSuggestion('PYTHON_BRIDGE_TIMEOUT');

// ❌ Error - TypeScript prevents typo
// const bad = suggester.getSuggestion('PYTHON_BRIDGE_TIMEOUT_ERROR'); // Type error!

// ❌ Error - TypeScript prevents invalid code
// const wrong = suggester.getSuggestion('RANDOM_ERROR'); // Type error!
```

### Working with Error Codes

```typescript
// Define error code as constant for reuse
const timeoutErrorCode: ErrorCode = 'PYTHON_BRIDGE_TIMEOUT';

// Get suggestion
const suggestion = suggester.getSuggestion(timeoutErrorCode);

// All error codes available:
type AllErrorCodes =
  | 'INVALID_TEMPLATE_SYNTAX'
  | 'MISSING_REQUIRED_FIELD'
  | 'INVALID_CSS_SYNTAX'
  | 'INVALID_HTML_SYNTAX'
  | 'FIELD_NAME_MISMATCH'
  | 'CIRCULAR_DEPENDENCY'
  | 'INVALID_PYTHON_BRIDGE_REQUEST'
  | 'PYTHON_BRIDGE_TIMEOUT'
  | 'PYTHON_BRIDGE_CONNECTION_FAILED';
```

### Error Handling with Type Safety

```typescript
interface ApiError {
  code: ErrorCode;
  message: string;
  context?: Record<string, any>;
}

function handleError(error: unknown): ApiError {
  if (error instanceof CircuitBreakerError) {
    // Can safely access error.code
    return {
      code: 'PYTHON_BRIDGE_CONNECTION_FAILED',
      message: error.message,
      context: error.details,
    };
  }

  if (error instanceof Error && error.message.includes('syntax')) {
    return {
      code: 'INVALID_TEMPLATE_SYNTAX',
      message: error.message,
    };
  }

  // Default to generic error
  return {
    code: 'INVALID_PYTHON_BRIDGE_REQUEST',
    message: String(error),
  };
}
```

### Using ErrorCode in Custom Error Classes

```typescript
// Define custom error with type-safe code
export class TemplateError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public context?: Record<string, any>
  ) {
    super(message);
    this.name = 'TemplateError';
  }
}

// Usage
throw new TemplateError(
  'INVALID_TEMPLATE_SYNTAX',
  'Template contains unclosed braces',
  { line: 5, column: 10 }
);

// Handling
try {
  validateTemplate(template);
} catch (error) {
  if (error instanceof TemplateError) {
    const suggestion = suggester.getSuggestion(error.code);
    displayRecoverySuggestions(suggestion);
  }
}
```

---

## 3. Configuration Validation

### Validating Configuration at Startup

```typescript
import {
  validateAndGetConfig,
  BRIDGE_CONFIG,
} from '@/utils/config';

// At application startup
async function initializeApp() {
  // Validate configuration
  const validation = validateAndGetConfig(BRIDGE_CONFIG);

  if (!validation.isValid) {
    console.error('Configuration errors:');
    validation.errors.forEach((err) => {
      console.error(`  ❌ ${err.field}: ${err.message}`);
      console.error(`     Current value: ${err.value}`);
      console.error(`     Expected: number between 1000 and 300000`);
    });
    process.exit(1); // Fail fast
  }

  // Warn about suboptimal but valid configurations
  if (validation.warnings.length > 0) {
    console.warn('⚠️  Configuration warnings:');
    validation.warnings.forEach((w) => console.warn(`  - ${w}`));
  }

  // Use validated configuration
  initializeServices(validation.config);
}
```

### Custom Configuration Validation

```typescript
import { validateBridgeConfig, ConfigValidationError } from '@/utils/config';

// Validate custom configuration object
function validateCustomConfig(config: any): {
  isValid: boolean;
  errors: ConfigValidationError[];
} {
  const errors = validateBridgeConfig(config);

  // Add custom validations
  if (config.maxConcurrentRequests && config.maxConcurrentRequests > 100) {
    errors.push({
      field: 'maxConcurrentRequests',
      value: config.maxConcurrentRequests,
      message: 'maxConcurrentRequests should not exceed 100 for stability',
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
```

### Configuration Best Practices

```typescript
// ✅ DO: Validate at startup
async function main() {
  const validation = validateAndGetConfig(config);
  if (!validation.isValid) throw new Error('Invalid config');
  
  // Initialize with validated config
  app.initialize(validation.config);
}

// ✅ DO: Use typed configuration
interface AppConfig {
  timeout: number;
  retry: {
    maxRetries: number;
    baseDelay: number;
    maxDelay: number;
  };
}

// ❌ DON'T: Skip validation
const config = require('./config.json'); // No validation!

// ❌ DON'T: Use raw values
const timeout = 100; // Too small, should validate

// ✅ DO: Use validated constants
const { timeout } = validateAndGetConfig(BRIDGE_CONFIG).config;
```

---

## 4. Error Recovery

### Getting Recovery Suggestions

```typescript
import { ValidationErrorSuggester } from '@/services/validationErrorSuggester';

const suggester = new ValidationErrorSuggester();

// Get suggestion for error
const suggestion = suggester.getSuggestion('PYTHON_BRIDGE_TIMEOUT');

if (suggestion) {
  console.log('Error:', suggestion.message);
  console.log('How to fix:');
  suggestion.suggestions.forEach((s, i) => {
    console.log(`  ${i + 1}. ${s}`);
  });

  if (suggestion.examples) {
    console.log('Examples:');
    suggestion.examples.forEach((ex) => {
      console.log(`  • ${ex}`);
    });
  }
}

// Output:
// Error: Python backend request timed out
// How to fix:
//   1. Check if Python backend is running
//   2. Try increasing timeout value
//   3. Verify network connectivity
//   4. Check for large templates that may take longer to process
//   5. Review Python backend logs for errors
// Examples:
//   • Increase timeout: { timeout: 15000 }
//   • Check backend: python launch_and_test.py
```

### Context-Aware Recovery

```typescript
// Provide context to get personalized suggestions
const suggestion = suggester.getSuggestionWithContext(
  'PYTHON_BRIDGE_TIMEOUT',
  {
    timeout: 5000,        // Current timeout value
    templateSize: 50000,  // Size of template being processed
  }
);

// Suggestions will include:
// "Current timeout is 5000ms - consider increasing it"
// "Large template detected (50000 bytes) - may need longer timeout"
```

### Using Suggestions in UI

```typescript
function displayErrorRecovery(errorCode: ErrorCode) {
  const suggestion = suggester.getSuggestion(errorCode);

  if (!suggestion) {
    console.error(`No recovery suggestion for ${errorCode}`);
    return;
  }

  // Build UI for recovery
  const element = document.createElement('div');
  element.className = 'error-recovery';
  element.innerHTML = `
    <h3>${suggestion.message}</h3>
    <div class="suggestions">
      <strong>What to do:</strong>
      <ul>
        ${suggestion.suggestions.map((s) => `<li>${s}</li>`).join('')}
      </ul>
    </div>
    ${
      suggestion.examples
        ? `
      <div class="examples">
        <strong>Examples:</strong>
        <ul>
          ${suggestion.examples.map((e) => `<li><code>${e}</code></li>`).join('')}
        </ul>
      </div>
    `
        : ''
    }
  `;

  document.body.appendChild(element);
}
```

### Implementing Fallback Strategies

```typescript
// Pattern 1: Fallback to cached data
async function getTemplateWithFallback(id: string) {
  try {
    return await breaker.execute();
  } catch (error) {
    if (error instanceof CircuitBreakerError) {
      const cached = cache.get(id);
      if (cached) {
        console.log('Using cached template');
        return cached;
      }
    }
    throw error;
  }
}

// Pattern 2: Fallback to default/empty
async function validateTemplateWithFallback(template: string) {
  try {
    return await breaker.execute();
  } catch (error) {
    if (error instanceof CircuitBreakerError) {
      // Return safe default
      return { valid: false, errors: ['Service unavailable'] };
    }
    throw error;
  }
}

// Pattern 3: Fallback with retry
async function executeWithRetry(
  operation: () => Promise<any>,
  maxRetries: number = 3
) {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // Wait before retrying
      const delay = Math.pow(2, i) * 100; // Exponential backoff
      await new Promise((r) => setTimeout(r, delay));
    }
  }

  throw lastError;
}
```

---

## 5. Testing Error Scenarios

### Testing Circuit Breaker

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CircuitBreaker, CircuitBreakerError } from '@/services/circuitBreaker';

describe('Circuit Breaker Error Handling', () => {
  let operation: any;

  beforeEach(() => {
    operation = vi.fn();
  });

  // Test 1: Errors are propagated
  it('should propagate operation errors', async () => {
    const error = new Error('Operation failed');
    operation.mockRejectedValue(error);

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 3,
      successThreshold: 2,
      timeout: 1000,
    });

    await expect(breaker.execute()).rejects.toThrow('Operation failed');
  });

  // Test 2: Circuit opens on failures
  it('should open circuit on repeated failures', async () => {
    operation.mockRejectedValue(new Error('Failed'));

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 2,
      successThreshold: 2,
      timeout: 1000,
    });

    // First failure
    try {
      await breaker.execute();
    } catch {}
    expect(breaker.getState()).toBe('CLOSED');

    // Second failure opens circuit
    try {
      await breaker.execute();
    } catch {}
    expect(breaker.getState()).toBe('OPEN');
  });

  // Test 3: Circuit rejects requests when open
  it('should reject requests when circuit is open', async () => {
    operation.mockRejectedValue(new Error('Failed'));

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 1,
      successThreshold: 2,
      timeout: 1000,
    });

    // Open the circuit
    try {
      await breaker.execute();
    } catch {}

    // Further requests rejected
    await expect(breaker.execute()).rejects.toThrow(CircuitBreakerError);
    await expect(breaker.execute()).rejects.toThrow('CIRCUIT_BREAKER_OPEN');
  });

  // Test 4: Circuit recovers
  it('should recover from circuit open state', async () => {
    operation.mockRejectedValueOnce(new Error('Failed'));
    operation.mockResolvedValueOnce('Success');

    const breaker = new CircuitBreaker(operation, {
      failureThreshold: 1,
      successThreshold: 1,
      timeout: 100, // Short timeout for testing
    });

    // Open circuit
    try {
      await breaker.execute();
    } catch {}
    expect(breaker.getState()).toBe('OPEN');

    // Wait for timeout
    await new Promise((r) => setTimeout(r, 150));

    // Should transition to HALF_OPEN and allow retry
    const result = await breaker.execute();
    expect(result).toBe('Success');
    expect(breaker.getState()).toBe('CLOSED');
  });
});
```

### Testing Error Suggestions

```typescript
describe('Error Suggestions', () => {
  const suggester = new ValidationErrorSuggester();

  it('should provide suggestions for known errors', () => {
    const suggestion = suggester.getSuggestion('PYTHON_BRIDGE_TIMEOUT');
    expect(suggestion).toBeDefined();
    expect(suggestion.message).toContain('timeout');
    expect(suggestion.suggestions.length).toBeGreaterThan(0);
  });

  it('should include examples in suggestions', () => {
    const suggestion = suggester.getSuggestion('PYTHON_BRIDGE_TIMEOUT');
    expect(suggestion.examples).toBeDefined();
    expect(suggestion.examples.length).toBeGreaterThan(0);
  });

  it('should enhance suggestions with context', () => {
    const suggestion = suggester.getSuggestionWithContext(
      'PYTHON_BRIDGE_TIMEOUT',
      { timeout: 5000 }
    );
    expect(suggestion.suggestions.some((s) => s.includes('5000'))).toBe(true);
  });
});
```

---

## 6. Common Patterns

### Pattern 1: Error Logging with Context

```typescript
async function executeWithLogging<T>(
  operation: () => Promise<T>,
  context: { operationName: string; userId?: string }
): Promise<T> {
  const startTime = Date.now();

  try {
    const result = await operation();
    const duration = Date.now() - startTime;

    console.log(`✓ ${context.operationName} succeeded in ${duration}ms`);

    return result;
  } catch (error) {
    const duration = Date.now() - startTime;

    console.error(
      `✗ ${context.operationName} failed after ${duration}ms`,
      {
        userId: context.userId,
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      }
    );

    throw error;
  }
}

// Usage
await executeWithLogging(
  () => breaker.execute(),
  { operationName: 'validateTemplate', userId: 'user123' }
);
```

### Pattern 2: Error Recovery with Retry

```typescript
async function executeWithRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  backoffMs: number = 100
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      if (attempt > 0) {
        console.log(`Retry attempt ${attempt} of ${maxRetries}`);
      }

      return await operation();
    } catch (error) {
      lastError = error as Error;

      if (attempt < maxRetries - 1) {
        // Calculate exponential backoff: 100ms, 200ms, 400ms, etc.
        const delay = backoffMs * Math.pow(2, attempt);
        console.log(`Error: ${lastError.message}, retrying in ${delay}ms`);
        await new Promise((r) => setTimeout(r, delay));
      }
    }
  }

  throw lastError;
}

// Usage
const result = await executeWithRetry(() => breaker.execute(), 3, 100);
```

### Pattern 3: Error Handling with User Feedback

```typescript
async function executeWithUserFeedback<T>(
  operation: () => Promise<T>,
  operationName: string
): Promise<T> {
  try {
    showLoadingSpinner(true);
    const result = await operation();
    showLoadingSpinner(false);
    return result;
  } catch (error) {
    showLoadingSpinner(false);

    if (error instanceof CircuitBreakerError) {
      if (error.code === 'CIRCUIT_BREAKER_OPEN') {
        showError(
          `${operationName} is temporarily unavailable. Please try again in a moment.`,
          'warning'
        );
      }
    } else if (error instanceof Error) {
      const suggestion = suggester.getSuggestionRuntime(error.message);

      if (suggestion) {
        showError(suggestion.message, 'error');
        showRecoverySuggestions(suggestion.suggestions);
      } else {
        showError(
          `${operationName} failed: ${error.message}`,
          'error'
        );
      }
    }

    throw error;
  }
}
```

---

## 7. Troubleshooting

### Problem: Circuit stays OPEN indefinitely

```typescript
// ❌ Problem: timeout is too long
const breaker = new CircuitBreaker(operation, {
  failureThreshold: 5,
  successThreshold: 2,
  timeout: 3600000, // 1 hour - too long!
});

// ✅ Solution: use reasonable timeout
const breaker = new CircuitBreaker(operation, {
  failureThreshold: 5,
  successThreshold: 2,
  timeout: 60000, // 1 minute
});
```

### Problem: Circuit opens too quickly

```typescript
// ❌ Problem: threshold too low
const breaker = new CircuitBreaker(operation, {
  failureThreshold: 1, // Opens on first failure!
  successThreshold: 2,
  timeout: 60000,
});

// ✅ Solution: allow transient failures
const breaker = new CircuitBreaker(operation, {
  failureThreshold: 5, // Allow 5 failures before opening
  successThreshold: 2,
  timeout: 60000,
});
```

### Problem: Error message not helpful

```typescript
// ❌ Problem: generic error
throw new Error('Failed');

// ✅ Solution: use type-safe error with context
throw new CircuitBreakerError(
  'PYTHON_BRIDGE_TIMEOUT',
  'Python backend request timed out after 5000ms',
  {
    timeout: 5000,
    endpoint: '/validate',
    requestId: '123',
  }
);
```

### Problem: Testing doesn't catch errors

```typescript
// ❌ Problem: not awaiting async operations
it('should handle errors', () => {
  breaker.execute().catch((e) => {
    expect(e).toBeDefined(); // Never runs!
  });
});

// ✅ Solution: use async/await
it('should handle errors', async () => {
  await expect(breaker.execute()).rejects.toBeDefined();
});

// ✅ Alternative: use done callback
it('should handle errors', (done) => {
  breaker.execute().catch((e) => {
    expect(e).toBeDefined();
    done();
  });
});
```

---

## Quick Reference

### CircuitBreaker

```typescript
const breaker = new CircuitBreaker<T>(operation, config, onStateChange?);

// Configuration
config.failureThreshold;  // Failures before OPEN
config.successThreshold;  // Successes before CLOSED
config.timeout;          // Before retry (HALF_OPEN)

// Methods
await breaker.execute();
breaker.getState();
breaker.getMetrics();
breaker.getResponseTimePercentile(95);
breaker.getAverageStateDuration('OPEN');
breaker.reset();
```

### ErrorCode

```typescript
type ErrorCode = 
  | 'INVALID_TEMPLATE_SYNTAX'
  | 'MISSING_REQUIRED_FIELD'
  | 'INVALID_CSS_SYNTAX'
  | 'INVALID_HTML_SYNTAX'
  | 'FIELD_NAME_MISMATCH'
  | 'CIRCULAR_DEPENDENCY'
  | 'INVALID_PYTHON_BRIDGE_REQUEST'
  | 'PYTHON_BRIDGE_TIMEOUT'
  | 'PYTHON_BRIDGE_CONNECTION_FAILED';

const suggestion = suggester.getSuggestion(errorCode);
```

### Config Validation

```typescript
const validation = validateAndGetConfig(config);
// validation.isValid: boolean
// validation.errors: ConfigValidationError[]
// validation.warnings: string[]
// validation.config: validated config
```

---

**For more details, see ERROR-HANDLING-FAULT-TOLERANCE-ANALYSIS.md**
