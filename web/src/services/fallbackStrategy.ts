/**
 * Timeout Fallback Strategy Implementation
 * Provides graceful degradation when operations timeout
 */

import { CircuitBreaker, CircuitBreakerError } from './circuitBreaker';

/**
 * Fallback strategy result
 */
export interface FallbackResult<T, F> {
  success: boolean;
  data: T | F;
  source: 'primary' | 'fallback';
  error?: Error;
  duration: number;
}

/**
 * Options for fallback execution
 */
export interface FallbackOptions<T, F> {
  /** Timeout in milliseconds before using fallback */
  timeout?: number;
  /** Custom error to use for timeout */
  timeoutError?: Error;
  /** Whether to log fallback usage */
  logFallback?: boolean;
}

/**
 * Execute operation with fallback strategy
 * Returns result from primary operation, or fallback if timeout occurs
 */
export async function executeWithFallback<T, F = T>(
  primary: () => Promise<T>,
  fallback: () => Promise<F>,
  options: FallbackOptions<T, F> = {}
): Promise<FallbackResult<T, F>> {
  const startTime = Date.now();
  const timeout = options.timeout || 30000; // 30s default

  try {
    // Create timeout promise
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => {
        reject(options.timeoutError || new Error('Operation timeout'));
      }, timeout)
    );

    // Race between primary operation and timeout
    const data = await Promise.race([primary(), timeoutPromise]);

    return {
      success: true,
      data,
      source: 'primary',
      duration: Date.now() - startTime,
    };
  } catch (error) {
    // Check if error is a timeout
    const isTimeout = error instanceof Error && 
      (error.message.includes('timeout') || error.message === 'Operation timeout');

    if (isTimeout) {
      if (options.logFallback) {
        console.log(`Primary operation timed out after ${timeout}ms, using fallback`);
      }

      try {
        const data = await fallback();
        return {
          success: true,
          data,
          source: 'fallback',
          duration: Date.now() - startTime,
        };
      } catch (fallbackError) {
        return {
          success: false,
          data: undefined as any,
          source: 'fallback',
          error: fallbackError as Error,
          duration: Date.now() - startTime,
        };
      }
    }

    // Not a timeout, return error
    return {
      success: false,
      data: undefined as any,
      source: 'primary',
      error: error as Error,
      duration: Date.now() - startTime,
    };
  }
}

/**
 * Circuit breaker with fallback strategy
 * Uses fallback when circuit is open
 */
export class CircuitBreakerWithFallback<T, F = T> extends CircuitBreaker<T> {
  private fallbackFn?: () => Promise<F>;

  /**
   * Set fallback function to use when circuit is open
   */
  setFallback(fallback: () => Promise<F>): void {
    this.fallbackFn = fallback;
  }

  /**
   * Execute with fallback strategy
   * If circuit is open, uses fallback instead of failing
   */
  async executeWithFallback(): Promise<T | F> {
    try {
      return await this.execute();
    } catch (error) {
      if (
        error instanceof CircuitBreakerError &&
        error.code === 'CIRCUIT_BREAKER_OPEN' &&
        this.fallbackFn
      ) {
        // Circuit is open, use fallback
        return await this.fallbackFn();
      }
      // Not a circuit breaker error or no fallback, re-throw
      throw error;
    }
  }
}

/**
 * Fallback strategies for common patterns
 */
export class FallbackStrategies {
  /**
   * Cache-based fallback
   * Returns last successful result from cache
   */
  static cacheBasedFallback<T>(
    cache: Map<string, T>,
    key: string,
    defaultValue?: T
  ) {
    return async (): Promise<T> => {
      const cached = cache.get(key);
      if (cached) {
        return cached;
      }
      if (defaultValue) {
        return defaultValue;
      }
      throw new Error(`No cached value for key: ${key}`);
    };
  }

  /**
   * Default value fallback
   * Returns safe default when operation fails
   */
  static defaultValueFallback<T>(defaultValue: T) {
    return async (): Promise<T> => {
      return defaultValue;
    };
  }

  /**
   * Empty collection fallback
   * Returns empty array/object when operation fails
   */
  static emptyCollectionFallback<T>(emptyValue: T) {
    return async (): Promise<T> => {
      return emptyValue;
    };
  }

  /**
   * Retry-based fallback
   * Retries operation with exponential backoff
   */
  static retryFallback<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 100
  ) {
    return async (): Promise<T> => {
      let lastError: Error;

      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          return await operation();
        } catch (error) {
          lastError = error as Error;

          if (attempt < maxRetries - 1) {
            const delay = baseDelay * Math.pow(2, attempt);
            await new Promise((r) => setTimeout(r, delay));
          }
        }
      }

      throw lastError;
    };
  }
}
