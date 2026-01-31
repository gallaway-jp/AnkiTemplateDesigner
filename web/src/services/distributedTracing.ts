/**
 * Distributed Error Tracing Support
 * Adds correlation IDs and execution spans for distributed tracing
 */

/**
 * Execution context for tracing
 */
export interface ExecutionContext {
  /** Unique correlation ID for tracing across services */
  correlationId: string;
  /** Trace ID from distributed tracing system */
  traceId?: string;
  /** Span ID for this operation */
  spanId?: string;
  /** Parent span ID for nested operations */
  parentSpanId?: string;
  /** Additional metadata for tracing */
  metadata?: Record<string, any>;
  /** Timestamp when context was created */
  timestamp: number;
}

/**
 * Execution span record
 */
export interface ExecutionSpan {
  spanId: string;
  parentSpanId?: string;
  operationName: string;
  status: 'success' | 'error' | 'timeout';
  startTime: number;
  endTime: number;
  duration: number;
  error?: {
    code: string;
    message: string;
    stack?: string;
  };
  metadata?: Record<string, any>;
}

/**
 * Trace recorder for collecting execution spans
 */
export class TraceRecorder {
  private spans: Map<string, ExecutionSpan> = new Map();
  private rootContext: ExecutionContext | null = null;

  /**
   * Create new execution context
   */
  createContext(metadata?: Record<string, any>): ExecutionContext {
    const context: ExecutionContext = {
      correlationId: this.generateId(),
      traceId: this.generateId(),
      spanId: this.generateId(),
      metadata,
      timestamp: Date.now(),
    };

    this.rootContext = context;
    return context;
  }

  /**
   * Create child context for nested operation
   */
  createChildContext(
    parentContext: ExecutionContext,
    metadata?: Record<string, any>
  ): ExecutionContext {
    return {
      correlationId: parentContext.correlationId,
      traceId: parentContext.traceId,
      spanId: this.generateId(),
      parentSpanId: parentContext.spanId,
      metadata,
      timestamp: Date.now(),
    };
  }

  /**
   * Record execution span
   */
  recordSpan(
    context: ExecutionContext,
    operationName: string,
    status: 'success' | 'error' | 'timeout',
    startTime: number,
    endTime: number,
    error?: { code: string; message: string; stack?: string },
    metadata?: Record<string, any>
  ): void {
    const span: ExecutionSpan = {
      spanId: context.spanId!,
      parentSpanId: context.parentSpanId,
      operationName,
      status,
      startTime,
      endTime,
      duration: endTime - startTime,
      error,
      metadata: {
        ...context.metadata,
        ...metadata,
      },
    };

    this.spans.set(span.spanId, span);
  }

  /**
   * Get all recorded spans
   */
  getSpans(): ExecutionSpan[] {
    return Array.from(this.spans.values());
  }

  /**
   * Get trace as tree structure
   */
  getTraceTree(): ExecutionSpan | null {
    if (!this.rootContext) {
      return null;
    }

    const rootSpan = this.spans.get(this.rootContext.spanId!);
    if (!rootSpan) {
      return null;
    }

    return this.buildSpanTree(rootSpan);
  }

  /**
   * Get trace summary
   */
  getTraceSummary(): {
    correlationId: string;
    spanCount: number;
    totalDuration: number;
    errorCount: number;
    timeoutCount: number;
  } | null {
    if (!this.rootContext) {
      return null;
    }

    const spans = this.getSpans();
    const totalDuration =
      Math.max(...spans.map((s) => s.endTime), 0) -
      Math.min(...spans.map((s) => s.startTime), Date.now());
    const errorCount = spans.filter((s) => s.status === 'error').length;
    const timeoutCount = spans.filter((s) => s.status === 'timeout').length;

    return {
      correlationId: this.rootContext.correlationId,
      spanCount: spans.length,
      totalDuration,
      errorCount,
      timeoutCount,
    };
  }

  /**
   * Clear recorded spans
   */
  clear(): void {
    this.spans.clear();
    this.rootContext = null;
  }

  /**
   * Export spans for external tracing system
   */
  exportSpans(): any[] {
    return this.getSpans().map((span) => ({
      traceId: this.rootContext?.traceId,
      spanId: span.spanId,
      parentSpanId: span.parentSpanId,
      operationName: span.operationName,
      status: span.status,
      startTime: span.startTime,
      endTime: span.endTime,
      duration: span.duration,
      tags: span.metadata,
      logs: span.error
        ? [
            {
              timestamp: span.endTime,
              event: 'error',
              'error.code': span.error.code,
              'error.message': span.error.message,
              'error.stack': span.error.stack,
            },
          ]
        : [],
    }));
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Build span tree recursively
   */
  private buildSpanTree(rootSpan: ExecutionSpan): ExecutionSpan {
    const children = this.getSpans().filter(
      (s) => s.parentSpanId === rootSpan.spanId
    );

    // Add children info to metadata
    if (children.length > 0) {
      return {
        ...rootSpan,
        metadata: {
          ...rootSpan.metadata,
          childSpans: children.length,
          children: children.map((c) => this.buildSpanTree(c)),
        },
      };
    }

    return rootSpan;
  }
}

/**
 * Distributed trace context storage
 * Thread-safe storage for execution contexts
 */
export class TraceContextStorage {
  private contexts: Map<string, ExecutionContext> = new Map();
  private activeContext: ExecutionContext | null = null;

  /**
   * Store context
   */
  setContext(context: ExecutionContext): void {
    this.contexts.set(context.correlationId, context);
    this.activeContext = context;
  }

  /**
   * Get stored context by ID
   */
  getContext(correlationId: string): ExecutionContext | null {
    return this.contexts.get(correlationId) || null;
  }

  /**
   * Get active context
   */
  getActiveContext(): ExecutionContext | null {
    return this.activeContext;
  }

  /**
   * Clear context
   */
  clearContext(correlationId: string): void {
    this.contexts.delete(correlationId);
    if (this.activeContext?.correlationId === correlationId) {
      this.activeContext = null;
    }
  }

  /**
   * Clear all contexts
   */
  clearAll(): void {
    this.contexts.clear();
    this.activeContext = null;
  }
}

/**
 * Global trace context storage instance
 */
export const traceContextStorage = new TraceContextStorage();

/**
 * Global trace recorder instance
 */
export const globalTraceRecorder = new TraceRecorder();

/**
 * Helper to add correlation ID header to requests
 */
export function getTraceHeaders(context: ExecutionContext): Record<string, string> {
  return {
    'X-Correlation-ID': context.correlationId,
    'X-Trace-ID': context.traceId || '',
    'X-Span-ID': context.spanId || '',
    'X-Parent-Span-ID': context.parentSpanId || '',
  };
}

/**
 * Helper to extract trace headers from request
 */
export function extractTraceContext(headers: Record<string, string>): Partial<ExecutionContext> {
  return {
    correlationId: headers['x-correlation-id'] || headers['X-Correlation-ID'],
    traceId: headers['x-trace-id'] || headers['X-Trace-ID'],
    spanId: headers['x-span-id'] || headers['X-Span-ID'],
    parentSpanId: headers['x-parent-span-id'] || headers['X-Parent-Span-ID'],
  };
}
