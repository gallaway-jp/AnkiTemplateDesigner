# Code Maintenance & Development Guide

**For**: Developers maintaining and extending the codebase  
**Date**: January 21, 2026  
**Scope**: 6 newly implemented services and tests

---

## 🎯 Quick Reference

### Service Locations
```
src/services/
├── circuitBreaker.ts              ← Resilience pattern
├── pythonBridgeProvider.ts        ← Dependency injection
├── validationErrorSuggester.ts    ← Error guidance
└── __tests__/
    ├── advanced-services.test.ts  ← Unit tests
    └── integration.test.ts        ← Integration tests

src/utils/
└── config.ts                      ← Configuration constants
```

### Test Execution
```bash
npm test                        # Run all tests
npm test -- --watch            # Watch mode
npm test -- --coverage         # With coverage
npm test -- advanced-services  # Specific file
```

---

## 📝 How to Add Features

### Adding a New Error Type

```typescript
// In: src/services/validationErrorSuggester.ts

// 1. Add to the suggestion map in the constructor
private suggestionMap: Map<string, ValidationErrorSuggestion> = new Map([
  // ... existing suggestions ...
  [
    'NEW_ERROR_CODE',
    {
      code: 'NEW_ERROR_CODE',
      message: 'Description of the error',
      suggestions: [
        'First suggestion',
        'Second suggestion',
        'Third suggestion',
      ],
      examples: [
        'Valid example',
        'Invalid example',
      ],
    }
  ],
]);

// 2. Add test for the new error
describe('ValidationErrorSuggester', () => {
  it('should provide suggestion for NEW_ERROR_CODE', () => {
    const suggester = new ValidationErrorSuggester();
    const suggestion = suggester.getSuggestion('NEW_ERROR_CODE');
    expect(suggestion).toBeDefined();
    expect(suggestion?.code).toBe('NEW_ERROR_CODE');
  });
});

// 3. Use in your error handling
try {
  // ... your code ...
} catch (error) {
  const suggestion = validationErrorSuggester.getSuggestion('NEW_ERROR_CODE');
  console.log(validationErrorSuggester.formatSuggestion(suggestion));
}
```

### Adjusting Circuit Breaker Thresholds

```typescript
// In: src/utils/config.ts

export const BRIDGE_CONFIG = {
  circuitBreaker: {
    failureThreshold: 5,      // <- Adjust this
    successThreshold: 2,      // <- Or this
    timeout: 60000,           // <- Or this (in ms)
  },
} as const;

// Then in your code:
const breaker = new CircuitBreaker(
  operation,
  {
    failureThreshold: BRIDGE_CONFIG.circuitBreaker.failureThreshold,
    successThreshold: BRIDGE_CONFIG.circuitBreaker.successThreshold,
    timeout: BRIDGE_CONFIG.circuitBreaker.timeout,
  }
);
```

### Custom Factory for Dependency Injection

```typescript
// In your test file:
import { PythonBridgeProvider, MockPythonBridgeFactory } from './services/pythonBridgeProvider';

// Create mock
const mockBridge = {
  initialize: vi.fn().mockResolvedValue(undefined),
  sendRequest: vi.fn().mockResolvedValue({ result: 'data' }),
  disconnect: vi.fn(),
  isConnected: vi.fn().mockReturnValue(true),
  health: vi.fn().mockResolvedValue({ status: 'ok' }),
  requestQueue: vi.fn().mockReturnValue([]),
  requestMetrics: vi.fn().mockReturnValue({}),
};

// Inject it
beforeEach(() => {
  PythonBridgeProvider.setFactory(new MockPythonBridgeFactory(mockBridge));
});

// Use it
const bridge = PythonBridgeProvider.getInstance();
// Now uses mock instead of real bridge
```

---

## 🐛 Debugging Guide

### Check Circuit Breaker State

```typescript
import { CircuitBreaker } from './services/circuitBreaker';

const breaker = new CircuitBreaker(
  operation,
  config,
  (state, metrics) => {
    // This callback is called when state changes
    console.log(`State changed to: ${state}`);
    console.log(`Metrics:`, metrics);
  }
);

// Manually check state
const metrics = breaker.getMetrics();
console.log(`Current state: ${metrics.state}`);
console.log(`Success rate: ${breaker.getSuccessRate()}%`);
```

### Check Suggestion Quality

```typescript
import { validationErrorSuggester } from './services/validationErrorSuggester';

// Get all suggestions to verify
const allSuggestions = validationErrorSuggester.getAllSuggestions();
allSuggestions.forEach(suggestion => {
  console.log(validationErrorSuggester.formatSuggestion(suggestion));
});

// Verify specific error
const suggestion = validationErrorSuggester.getSuggestion('INVALID_CSS_SYNTAX');
console.log(suggestion?.suggestions);  // Should have 3+ suggestions
```

### Verify Dependency Injection

```typescript
// In development:
const bridge = PythonBridgeProvider.getInstance();
console.log(bridge.constructor.name);  // Should be 'PythonBridge'

// In tests:
PythonBridgeProvider.setFactory(mockFactory);
const bridge = PythonBridgeProvider.getInstance();
console.log(bridge.constructor.name);  // Should be your mock object
```

---

## 🔍 Code Review Checklist

When reviewing code that uses these services:

### CircuitBreaker Usage
- [ ] Circuit breaker is created with sensible thresholds
- [ ] State change callback is provided (for monitoring)
- [ ] Circuit breaker is reused (not created per request)
- [ ] Errors are properly caught and handled
- [ ] Tests verify state transitions

### PythonBridgeProvider Usage
- [ ] Using `getInstance()` not `new PythonBridge()`
- [ ] Tests use `setFactory()` to inject mocks
- [ ] Reset is called in test cleanup
- [ ] No hardcoded dependencies

### ValidationErrorSuggester Usage
- [ ] Error codes are correct (match defined types)
- [ ] Suggestions are shown to users
- [ ] Error codes are logged for analytics
- [ ] Custom errors use `addSuggestion()`

### Configuration Usage
- [ ] Hard-coded values are replaced with `BRIDGE_CONFIG`
- [ ] Configuration is not modified at runtime
- [ ] Environment-specific configs are handled

---

## 📊 Monitoring Checklist

In production, monitor these:

### Circuit Breaker Metrics
```typescript
// Track these metrics
const metrics = breaker.getMetrics();
- totalRequests        // Should steadily increase
- successCount         // Should be high (>95%)
- failureCount         // Should be low (<5%)
- state                // Should be mostly CLOSED
- stateChangeTime      // When state changed
```

**Alert if**:
- State is OPEN for > 2 minutes
- Failure rate > 10% for sustained period
- State cycling frequently (OPEN → HALF_OPEN → OPEN)

### Error Suggestion Analytics
```typescript
// Track which errors users encounter most
// Use error codes:
const errorCodes = [
  'INVALID_TEMPLATE_SYNTAX',
  'UNDEFINED_VARIABLE',
  'INVALID_CSS_SYNTAX',
  // ... others
];

// Monitor:
- Which error codes appear most
- How often suggestions are shown
- Which suggestions help users most
```

### Health Metrics
```typescript
// From Python bridge health check
const health = await bridge.health();
- Response time (should be < 500ms)
- Success rate (should be > 95%)
- Queue depth (should be < 10)
```

---

## 🚀 Performance Optimization

### Current Performance
- ✅ Circuit breaker: O(1) operations
- ✅ Error suggestions: O(1) map lookups
- ✅ Dependency injection: Singleton pattern, no re-creation
- ✅ Configuration: `as const` prevents copies

### If You Need to Optimize

**Scenario 1: Too many state transitions**
```typescript
// Increase thresholds to reduce sensitivity
circuitBreaker: {
  failureThreshold: 10,  // Was 5
  successThreshold: 3,   // Was 2
  timeout: 120000,       // Was 60000
}
```

**Scenario 2: Slow error suggestions**
```typescript
// Current is already O(1), but if needed:
// - Add caching for formatted suggestions
// - Lazy-load suggestions instead of Map in constructor
```

**Scenario 3: Memory usage**
```typescript
// Suggestions are small, but if needed:
// - Move rarely-used suggestions to external file
// - Load on-demand instead of at startup
```

---

## 🔐 Security Considerations

### Current Security Measures ✅
- ✅ No user input evaluation (safe configuration)
- ✅ No remote code execution vectors
- ✅ Type-safe (no arbitrary property access)
- ✅ Immutable configuration (`as const`)

### When Adding New Features
- [ ] Don't allow runtime config changes via user input
- [ ] Validate error codes before looking them up
- [ ] Sanitize error messages before displaying
- [ ] Don't log sensitive data
- [ ] Validate factory implementations before use

---

## 📚 Documentation Standards

When adding code:

### Required Documentation
```typescript
/**
 * Brief one-line description
 * 
 * Longer explanation of what this does,
 * why it exists, and when to use it.
 * 
 * @example
 * ```typescript
 * // Show real usage here
 * const result = await service.method();
 * ```
 * 
 * @throws {ErrorType} Description of when this is thrown
 * @returns {ReturnType} Description of return value
 */
publicMethod() { }
```

### Required Tests
```typescript
describe('FeatureName', () => {
  describe('Happy path', () => {
    it('should do the expected thing', () => {
      // Test passes when working correctly
    });
  });
  
  describe('Error cases', () => {
    it('should handle specific error', () => {
      // Test fails gracefully
    });
  });
  
  describe('Edge cases', () => {
    it('should handle boundary conditions', () => {
      // Test handles limits
    });
  });
});
```

---

## 🔄 Common Patterns

### Pattern 1: Using Circuit Breaker with Error Suggestions

```typescript
import { CircuitBreaker } from './services/circuitBreaker';
import { validationErrorSuggester } from './services/validationErrorSuggester';

const breaker = new CircuitBreaker(
  async () => await bridge.sendRequest(request),
  config,
  (state) => {
    if (state === 'OPEN') {
      const suggestion = validationErrorSuggester.getSuggestion(
        'PYTHON_BRIDGE_TIMEOUT'
      );
      console.error(validationErrorSuggester.formatSuggestion(suggestion));
    }
  }
);

try {
  const result = await breaker.execute();
} catch (error) {
  const suggestion = validationErrorSuggester.getSuggestion(error.code);
  if (suggestion) {
    showToUser(validationErrorSuggester.formatSuggestion(suggestion));
  }
}
```

### Pattern 2: Testing with Mocks

```typescript
import { PythonBridgeProvider, MockPythonBridgeFactory } from './services/pythonBridgeProvider';

describe('Feature that uses PythonBridge', () => {
  beforeEach(() => {
    // Setup
    const mockBridge = createMockBridge();
    PythonBridgeProvider.setFactory(new MockPythonBridgeFactory(mockBridge));
  });
  
  afterEach(() => {
    // Cleanup
    PythonBridgeProvider.reset();
  });
  
  it('should work with mocked bridge', async () => {
    const result = await myFeature();
    expect(result).toBeDefined();
  });
});
```

### Pattern 3: Monitoring in Production

```typescript
const breaker = new CircuitBreaker(operation, config, (state, metrics) => {
  // Log to monitoring service
  monitoring.recordMetric('circuit_breaker_state', state);
  monitoring.recordMetric('success_rate', breaker.getSuccessRate());
  
  if (state === 'OPEN') {
    monitoring.alert('Circuit breaker opened!');
  }
});
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't

```typescript
// 1. Create CircuitBreaker per request
for (request of requests) {
  const breaker = new CircuitBreaker(op, config);  // ❌ Wrong!
}

// 2. Modify configuration at runtime
BRIDGE_CONFIG.timeout = 5000;  // ❌ Wrong! It's const

// 3. Use 'any' types with the services
const result: any = await breaker.execute();  // ❌ Wrong!

// 4. Catch all errors without checking code
try {
  await breaker.execute();
} catch (error) {
  // Assuming it's always CircuitBreakerError - ❌ Wrong!
}

// 5. Reset PythonBridgeProvider in production
PythonBridgeProvider.reset();  // ❌ Production code only!
```

### ✅ Do

```typescript
// 1. Reuse CircuitBreaker
const breaker = new CircuitBreaker(op, config);
for (request of requests) {
  await breaker.execute();  // ✅ Correct!
}

// 2. Use configuration as-is
const timeout = BRIDGE_CONFIG.timeout;  // ✅ Correct!

// 3. Preserve types
const result: Data = await breaker.execute<Data>();  // ✅ Correct!

// 4. Check error codes
try {
  await breaker.execute();
} catch (error) {
  if (error.code === 'CIRCUIT_BREAKER_OPEN') {
    // Handle appropriately
  }  // ✅ Correct!
}

// 5. Reset only in tests
afterEach(() => {
  PythonBridgeProvider.reset();  // ✅ Correct!
});
```

---

## 🎓 Learning Resources

**For understanding the patterns used**:
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [State Pattern](https://refactoring.guru/design-patterns/state)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)

**For understanding TypeScript features used**:
- [Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [Interfaces](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [const assertion](https://www.typescriptlang.org/docs/handbook/const-assertions.html)
- [Optional chaining](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#optional-chaining)

**For testing**:
- [Vitest Documentation](https://vitest.dev/)
- [Jest/Vitest Mocking](https://vitest.dev/guide/mocking.html)

---

## 📞 Troubleshooting

### Q: My tests are failing when I use the bridge

**A**: You likely forgot to mock it. Add this before your test:
```typescript
beforeEach(() => {
  const mockBridge = { /* ... */ };
  PythonBridgeProvider.setFactory(new MockPythonBridgeFactory(mockBridge));
});
```

### Q: Circuit breaker is always OPEN

**A**: Check these:
1. Are failure thresholds too low?
2. Is the timeout too short to recover?
3. Is the backend actually working?

Monitor the metrics to debug.

### Q: Error suggestions aren't showing up

**A**: Check these:
1. Are you calling `getSuggestion()` with correct error code?
2. Is the error code registered in the suggester?
3. Are you calling `formatSuggestion()` to display it?

### Q: Type errors with CircuitBreaker

**A**: Specify the generic type:
```typescript
const result = await breaker.execute<YourType>();
```

---

## ✅ Pre-Release Checklist

Before deploying code changes:

- [ ] All tests pass: `npm test`
- [ ] No TypeScript errors: `tsc --noEmit`
- [ ] No console errors: `npm run build`
- [ ] Code follows patterns shown above
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Performance verified
- [ ] Security reviewed
- [ ] Error handling is complete
- [ ] Monitoring hooks added

---

## 📅 Maintenance Schedule

**Weekly**:
- Check test coverage hasn't decreased
- Review error logs for new patterns

**Monthly**:
- Review circuit breaker metrics
- Analyze error suggestion usage
- Update documentation if needed

**Quarterly**:
- Full code review of changes
- Performance profiling
- Security audit

---

This guide ensures the codebase remains **maintainable, secure, and performant** over time.

