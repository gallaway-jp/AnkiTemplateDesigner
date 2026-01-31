# Architecture Improvement Roadmap

## Overview

This document provides a concrete roadmap for enhancing the AnkiTemplateDesigner architecture over the next 12 months.

---

## Phase 1: Foundation (Weeks 1-4) - High Priority

### 1.1 Implement Event Bus Pattern

**Objective**: Decouple components via event-driven architecture

**Implementation**:
```typescript
// src/utils/eventBus.ts
export class EventBus {
  private listeners: Map<string, Function[]> = new Map();
  
  on<T>(event: string, handler: (data: T) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.listeners.get(event) || [];
      handlers.splice(handlers.indexOf(handler), 1);
    };
  }
  
  emit<T>(event: string, data: T): void {
    this.listeners.get(event)?.forEach(handler => handler(data));
  }
  
  off(event: string): void {
    this.listeners.delete(event);
  }
}

// Global instance
export const eventBus = new EventBus();
```

**Event Types to Define**:
```typescript
// src/types/events.ts
export interface AppEvents {
  'template:loaded': Template;
  'template:updated': Template;
  'template:saved': Template;
  'component:selected': { id: string; path: string[] };
  'component:updated': CraftComponent;
  'error:occurred': Error;
  'notification:show': Notification;
}
```

**Usage in Components**:
```typescript
function TemplatePanel() {
  useEffect(() => {
    const unsubscribe = eventBus.on('template:updated', (template) => {
      // React to template updates without direct dependency
      refreshPreview();
    });
    
    return unsubscribe;
  }, []);
  
  const handleUpdate = (updates: Partial<Template>) => {
    // ...update logic
    eventBus.emit('template:updated', updatedTemplate);
  };
}
```

**Benefits**:
- ✅ Reduces tight coupling
- ✅ Easier to test
- ✅ Simpler cross-component communication
- ✅ Easier to add new subscribers

---

### 1.2 Implement Service Registry Pattern

**Objective**: Centralize service initialization and lifecycle

**Implementation**:
```typescript
// src/services/registry.ts
import { ServiceConfig } from '@/types';

export class ServiceRegistry {
  private services: Map<string, any> = new Map();
  private initializers: Map<string, () => Promise<void>> = new Map();
  
  register<T>(name: string, factory: () => T, config?: ServiceConfig): void {
    const instance = factory();
    this.services.set(name, instance);
    
    if (config?.onInit) {
      this.initializers.set(name, config.onInit);
    }
  }
  
  async initialize(name: string): Promise<void> {
    const initializer = this.initializers.get(name);
    if (initializer) {
      await initializer();
    }
  }
  
  async initializeAll(): Promise<void> {
    const promises = Array.from(this.initializers.entries()).map(
      ([name, fn]) => fn().catch(e => {
        console.error(`Failed to initialize ${name}:`, e);
      })
    );
    await Promise.all(promises);
  }
  
  get<T>(name: string): T {
    const service = this.services.get(name);
    if (!service) {
      throw new Error(`Service ${name} not registered`);
    }
    return service;
  }
}

export const registry = new ServiceRegistry();
```

**Service Registration**:
```typescript
// src/main.tsx
import { registry } from '@/services/registry';

// Register all services
registry.register('bridge', () => PythonBridgeProvider.getInstance());
registry.register('tracing', () => globalTraceRecorder);
registry.register('metrics', () => globalMetricsAggregator);
registry.register('eventBus', () => eventBus);
registry.register('logger', () => logger);

// Initialize all services
registry.initializeAll().then(() => {
  // App is ready
  createRoot(document.getElementById('root')!).render(<App />);
});
```

**Usage**:
```typescript
function useServices() {
  return {
    bridge: registry.get('bridge'),
    tracing: registry.get('tracing'),
    metrics: registry.get('metrics'),
  };
}
```

**Benefits**:
- ✅ Centralized service management
- ✅ Easier to add/remove services
- ✅ Lifecycle management
- ✅ Better testability

---

### 1.3 Add Middleware Pipeline Pattern

**Objective**: Standardize async operation handling

**Implementation**:
```typescript
// src/utils/middleware.ts
export type Next<T> = () => Promise<T>;
export type Middleware<T> = (next: Next<T>) => Promise<T>;

export class Pipeline<T> {
  private middlewares: Middleware<T>[] = [];
  
  use(middleware: Middleware<T>): this {
    this.middlewares.push(middleware);
    return this;
  }
  
  async execute(handler: () => Promise<T>): Promise<T> {
    let index = -1;
    
    const dispatch = async (i: number): Promise<T> => {
      if (i <= index) {
        throw new Error('next() called multiple times');
      }
      index = i;
      
      const middleware = this.middlewares[i];
      if (!middleware) {
        return handler();
      }
      
      return middleware(async () => dispatch(i + 1));
    };
    
    return dispatch(0);
  }
}

// Built-in middleware
export function loggingMiddleware<T>(name: string): Middleware<T> {
  return async (next) => {
    const start = Date.now();
    console.log(`[${name}] Starting...`);
    try {
      const result = await next();
      const duration = Date.now() - start;
      console.log(`[${name}] Completed in ${duration}ms`);
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      console.error(`[${name}] Failed after ${duration}ms:`, error);
      throw error;
    }
  };
}

export function errorHandlingMiddleware<T>(
  handler: (error: Error) => void
): Middleware<T> {
  return async (next) => {
    try {
      return await next();
    } catch (error) {
      handler(error as Error);
      throw error;
    }
  };
}

export function metricsMiddleware<T>(
  aggregator: CircuitBreakerAggregator
): Middleware<T> {
  return async (next) => {
    const start = Date.now();
    try {
      const result = await next();
      const duration = Date.now() - start;
      // Record success metric
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      // Record error metric
      throw error;
    }
  };
}
```

**Usage**:
```typescript
const pipeline = new Pipeline<Response>();
pipeline
  .use(loggingMiddleware('api-call'))
  .use(errorHandlingMiddleware((e) => logger.error(e)))
  .use(metricsMiddleware(aggregator));

const response = await pipeline.execute(() => 
  fetch('/api/template')
);
```

**Benefits**:
- ✅ Standardized async handling
- ✅ Composable concerns
- ✅ Easy to add/remove middleware
- ✅ Consistent error handling

---

## Phase 2: Enhancement (Weeks 5-8) - Medium Priority

### 2.1 Add Caching Layer Abstraction

**Objective**: Formalize cache management

**Implementation**:
```typescript
// src/services/cacheManager.ts
export interface CacheStrategy<K, V> {
  get(key: K): V | undefined;
  set(key: K, value: V, ttl?: number): void;
  remove(key: K): void;
  clear(): void;
  has(key: K): boolean;
}

export class LRUCacheStrategy<K, V> implements CacheStrategy<K, V> {
  private cache: Map<K, V> = new Map();
  
  constructor(private maxSize: number = 100) {}
  
  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }
    // Move to end (most recently used)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }
  
  set(key: K, value: V): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
  
  // ... other methods
}

export class CacheManager {
  private strategies: Map<string, CacheStrategy<any, any>> = new Map();
  
  register<K, V>(
    name: string,
    strategy: CacheStrategy<K, V>
  ): void {
    this.strategies.set(name, strategy);
  }
  
  get<K, V>(name: string): CacheStrategy<K, V> {
    const strategy = this.strategies.get(name);
    if (!strategy) {
      throw new Error(`Cache strategy ${name} not registered`);
    }
    return strategy;
  }
}

export const cacheManager = new CacheManager();
```

**Usage**:
```typescript
// Setup
cacheManager.register('templates', new LRUCacheStrategy<string, Template>(50));

// Usage
const templateCache = cacheManager.get<string, Template>('templates');
const cached = templateCache.get('template-123');
if (cached) {
  return cached;
}
const template = await fetchTemplate('template-123');
templateCache.set('template-123', template);
```

**Benefits**:
- ✅ Pluggable cache strategies
- ✅ Easy to test
- ✅ Consistent cache management
- ✅ TTL support

---

### 2.2 Add API Abstraction Layer

**Objective**: Separate business logic from transport

**Implementation**:
```typescript
// src/services/api/apiClient.ts
export interface ApiRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  body?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ApiResponse<T> {
  status: number;
  data: T;
  headers: Record<string, string>;
}

export interface ApiTransport {
  send<T>(request: ApiRequest): Promise<ApiResponse<T>>;
}

// HTTP transport
export class HttpTransport implements ApiTransport {
  constructor(
    private baseUrl: string,
    private defaultHeaders: Record<string, string> = {}
  ) {}
  
  async send<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${request.path}`;
    
    const response = await fetch(url, {
      method: request.method,
      headers: { ...this.defaultHeaders, ...request.headers },
      body: request.body ? JSON.stringify(request.body) : undefined,
    });
    
    const data = await response.json();
    
    return {
      status: response.status,
      data,
      headers: Object.fromEntries(response.headers)
    };
  }
}

// WebSocket transport
export class WebSocketTransport implements ApiTransport {
  // ... implementation
}
```

**Usage**:
```typescript
const apiClient = new ApiClient(new HttpTransport('http://api.example.com'));

const response = await apiClient.get<Template>('/templates/123');
const templates = await apiClient.list<Template>('/templates');
```

**Benefits**:
- ✅ Easy to switch transports
- ✅ Better testing
- ✅ Separation of concerns
- ✅ Multiple transport support

---

## Phase 3: Advanced Patterns (Weeks 9-12) - Lower Priority

### 3.1 CQRS Pattern (Optional)

**For**: Complex queries and writes with different requirements

```typescript
// src/services/commands/createTemplate.ts
export class CreateTemplateCommand {
  constructor(private store: EditorStore) {}
  
  async execute(data: CreateTemplateData): Promise<Template> {
    // Command implementation
  }
}

// src/services/queries/getTemplates.ts
export class GetTemplatesQuery {
  constructor(private cacheManager: CacheManager) {}
  
  async execute(filters: TemplateFilters): Promise<Template[]> {
    // Query implementation (cached)
  }
}
```

### 3.2 Event Sourcing (Optional)

**For**: Complete audit trail and replay capabilities

```typescript
// src/services/eventStore.ts
export interface Event {
  id: string;
  type: string;
  timestamp: number;
  aggregateId: string;
  data: any;
}

export class EventStore {
  private events: Event[] = [];
  
  append(event: Event): void {
    this.events.push(event);
  }
  
  getEvents(aggregateId: string): Event[] {
    return this.events.filter(e => e.aggregateId === aggregateId);
  }
}
```

---

## Implementation Priority Matrix

```
Impact
  ^
  │
9 │  Event Bus        Service Registry    Middleware
  │  (High Impact)    (High Impact)       (High Impact)
  │
6 │                   Caching Layer      API Abstraction
  │                   (Medium Impact)    (Medium Impact)
  │
3 │                                      CQRS
  │                                      Event Sourcing
  │                                      (Low Impact)
  │
  └─────────────────────────────────────────→ Effort
    Low        Medium        High
```

---

## 12-Month Timeline

### Q1 (Weeks 1-12)
- Week 1-4: Phase 1 (Event Bus, Service Registry, Middleware)
- Week 5-8: Phase 2 (Caching Layer, API Abstraction)
- Week 9-12: Testing & integration

### Q2 (Weeks 13-24)
- Stabilization
- Performance optimization
- Documentation updates
- Community feedback

### Q3-Q4
- Advanced patterns (optional)
- Performance tuning
- Long-term maintenance

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Event bus fully integrated
- ✅ Service registry in use
- ✅ Middleware pipeline standardized
- ✅ All tests passing
- ✅ Documentation updated

### Overall Success When:
- ✅ Coupling reduced by 30%
- ✅ Test coverage maintained at 100%
- ✅ Build times reduced by 20%
- ✅ Team satisfaction improved
- ✅ Feature velocity increased

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation**: 
- Gradual rollout
- Feature flags
- Backwards compatibility layer

### Risk 2: Learning Curve
**Mitigation**:
- Team training sessions
- Documentation
- Code examples
- Gradual adoption

### Risk 3: Performance Regression
**Mitigation**:
- Continuous benchmarking
- Performance monitoring
- Load testing

---

## Conclusion

This roadmap provides a structured approach to enhancing your architecture:

1. **Phase 1** (4 weeks): Foundation patterns for better decoupling
2. **Phase 2** (4 weeks): Utility patterns for common concerns
3. **Phase 3** (Optional): Advanced patterns for complex scenarios

**Estimated Effort**: 80-120 hours across team

**Expected Benefits**:
- 30% reduction in coupling
- Easier testing and debugging
- Better code organization
- Improved maintainability
- Stronger foundation for growth

**Next Steps**:
1. Review and approve roadmap
2. Allocate team resources
3. Begin Phase 1 implementation
4. Conduct regular reviews

---

**Approved by**: Architecture Review Team
**Date**: January 2026
**Status**: Ready for Implementation ✅
