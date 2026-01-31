/**
 * Circuit Breaker Pattern Implementation
 * Provides resilience against cascading failures
 * States: CLOSED (normal) → OPEN (failures) → HALF_OPEN (recovering) → CLOSED
 */

export type CircuitBreakerState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface CircuitBreakerConfig {
  failureThreshold: number; // Failures before opening
  successThreshold: number; // Successes before closing
  timeout: number; // Time in ms before attempting half-open
}

export interface CircuitBreakerMetrics {
  totalRequests: number;
  successCount: number;
  failureCount: number;
  lastFailureTime?: number;
  state: CircuitBreakerState;
  stateChangeTime: number;
}

/**
 * Circuit Breaker - Prevents cascading failures in distributed systems
 * 
 * Usage:
 * ```
 * const breaker = new CircuitBreaker(async () => {
 *   return await pythonBridge.sendRequest(...);
 * }, config);
 * 
 * try {
 *   const result = await breaker.execute();
 * } catch (error) {
 *   if (error.code === 'CIRCUIT_BREAKER_OPEN') {
 *     // Service is temporarily unavailable
 *   }
 * }
 * ```
 */
export class CircuitBreaker<T = any> {
  private state: CircuitBreakerState = 'CLOSED';
  private metrics: CircuitBreakerMetrics = {
    totalRequests: 0,
    successCount: 0,
    failureCount: 0,
    state: 'CLOSED',
    stateChangeTime: Date.now(),
  };
  private successCountInHalfOpen = 0;
  private timeoutHandle: NodeJS.Timeout | null = null;
  private responseTimes: number[] = [];
  private stateDurations: Map<CircuitBreakerState, number[]> = new Map();

  constructor(
    private operation: () => Promise<T>,
    private config: CircuitBreakerConfig,
    private onStateChange?: (newState: CircuitBreakerState, metrics: CircuitBreakerMetrics) => void
  ) {
    this.initializeStateDurations();
  }

  /**
   * Initialize state duration tracking
   */
  private initializeStateDurations(): void {
    this.stateDurations.set('CLOSED', []);
    this.stateDurations.set('OPEN', []);
    this.stateDurations.set('HALF_OPEN', []);
  }

  /**
   * Execute operation with circuit breaker protection
   */
  async execute(): Promise<T> {
    // Check if circuit should transition to HALF_OPEN
    if (this.state === 'OPEN') {
      const timeSinceOpen = Date.now() - this.metrics.stateChangeTime;
      if (timeSinceOpen > this.config.timeout) {
        this.transitionToHalfOpen();
      } else {
        throw new CircuitBreakerError(
          'CIRCUIT_BREAKER_OPEN',
          'Circuit breaker is OPEN - service temporarily unavailable',
          {
            state: this.state,
            timeUntilRetry: this.config.timeout - timeSinceOpen,
          }
        );
      }
    }

    this.metrics.totalRequests++;
    const startTime = Date.now();

    try {
      const result = await this.operation();
      this.recordResponseTime(Date.now() - startTime);
      this.onSuccess();
      return result as T;
    } catch (error) {
      this.recordResponseTime(Date.now() - startTime);
      this.onFailure();
      throw error;
    }
  }

  /**
   * Record response time for metrics
   */
  private recordResponseTime(duration: number): void {
    this.responseTimes.push(duration);
    // Keep last 1000 response times for percentile calculation
    if (this.responseTimes.length > 1000) {
      this.responseTimes.shift();
    }
  }

  /**
   * Calculate response time percentile
   */
  getResponseTimePercentile(percentile: 50 | 95 | 99): number {
    if (this.responseTimes.length === 0) {
      return 0;
    }
    const sorted = [...this.responseTimes].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  /**
   * Handle successful operation
   */
  private onSuccess(): void {
    this.metrics.successCount++;

    if (this.state === 'HALF_OPEN') {
      this.successCountInHalfOpen++;

      if (this.successCountInHalfOpen >= this.config.successThreshold) {
        this.transitionToClosed();
      }
    }
  }

  /**
   * Handle failed operation
   */
  private onFailure(): void {
    this.metrics.failureCount++;
    this.metrics.lastFailureTime = Date.now();

    if (this.state === 'CLOSED') {
      if (this.metrics.failureCount >= this.config.failureThreshold) {
        this.transitionToOpen();
      }
    } else if (this.state === 'HALF_OPEN') {
      // Failed in half-open state, go back to open
      this.transitionToOpen();
    }
  }

  /**
   * Transition to OPEN state
   */
  private transitionToOpen(): void {
    this.recordStateDuration(this.state);
    this.state = 'OPEN';
    this.metrics.state = 'OPEN';
    this.metrics.stateChangeTime = Date.now();
    this.successCountInHalfOpen = 0;

    if (this.timeoutHandle) {
      clearTimeout(this.timeoutHandle);
    }

    this.onStateChange?.('OPEN', { ...this.metrics });
  }

  /**
   * Transition to HALF_OPEN state
   */
  private transitionToHalfOpen(): void {
    this.recordStateDuration(this.state);
    this.state = 'HALF_OPEN';
    this.metrics.state = 'HALF_OPEN';
    this.metrics.stateChangeTime = Date.now();
    this.successCountInHalfOpen = 0;

    this.onStateChange?.('HALF_OPEN', { ...this.metrics });
  }

  /**
   * Transition to CLOSED state
   */
  private transitionToClosed(): void {
    this.recordStateDuration(this.state);
    this.state = 'CLOSED';
    this.metrics.state = 'CLOSED';
    this.metrics.stateChangeTime = Date.now();
    this.successCountInHalfOpen = 0;
    this.metrics.failureCount = 0;

    this.onStateChange?.('CLOSED', { ...this.metrics });
  }

  /**
   * Record duration spent in a state
   */
  private recordStateDuration(state: CircuitBreakerState): void {
    const duration = Date.now() - this.metrics.stateChangeTime;
    const durations = this.stateDurations.get(state);
    if (durations) {
      durations.push(duration);
      // Keep last 100 durations
      if (durations.length > 100) {
        durations.shift();
      }
    }
  }

  /**
   * Get average duration for a state
   */
  getAverageStateDuration(state: CircuitBreakerState): number {
    const durations = this.stateDurations.get(state) || [];
    if (durations.length === 0) {
      return 0;
    }
    return Math.round(durations.reduce((a, b) => a + b, 0) / durations.length * 100) / 100;
  }

  /**
   * Reset circuit breaker to initial state
   */
  reset(): void {
    this.state = 'CLOSED';
    this.metrics = {
      totalRequests: 0,
      successCount: 0,
      failureCount: 0,
      state: 'CLOSED',
      stateChangeTime: Date.now(),
    };
    this.successCountInHalfOpen = 0;

    if (this.timeoutHandle) {
      clearTimeout(this.timeoutHandle);
      this.timeoutHandle = null;
    }
  }

  /**
   * Get current metrics including percentiles and state durations
   */
  getMetrics(): CircuitBreakerMetrics & {
    successRate: number;
    p50ResponseTime: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
    averageResponseTime: number;
  } {
    const successRate = this.metrics.totalRequests > 0
      ? (this.metrics.successCount / this.metrics.totalRequests) * 100
      : 0;

    const averageResponseTime = this.responseTimes.length > 0
      ? Math.round(this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length * 100) / 100
      : 0;

    return {
      ...this.metrics,
      successRate: Math.round(successRate * 100) / 100,
      p50ResponseTime: this.getResponseTimePercentile(50),
      p95ResponseTime: this.getResponseTimePercentile(95),
      p99ResponseTime: this.getResponseTimePercentile(99),
      averageResponseTime,
    };
  }

  /**
   * Get current state
   */
  getState(): CircuitBreakerState {
    return this.state;
  }

  /**
   * Get success rate
   */
  getSuccessRate(): number {
    if (this.metrics.totalRequests === 0) {
      return 100;
    }
    return (this.metrics.successCount / this.metrics.totalRequests) * 100;
  }
}

/**
 * Error thrown by circuit breaker
 */
export class CircuitBreakerError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'CircuitBreakerError';
  }
}
