/**
 * Middleware Pipeline - Standardized async operation handling
 * Provides composable middleware for consistent operation handling
 */

export type Next<T> = () => Promise<T>;
export type Middleware<T> = (next: Next<T>) => Promise<T>;

/**
 * Pipeline for executing async operations with middleware
 */
export class Pipeline<T> {
  private middlewares: Middleware<T>[] = [];

  /**
   * Add middleware to pipeline
   * @param middleware Middleware function
   * @returns This pipeline for chaining
   */
  use(middleware: Middleware<T>): this {
    this.middlewares.push(middleware);
    return this;
  }

  /**
   * Execute handler with middleware chain
   * @param handler Main handler function
   * @returns Result from handler
   */
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

  /**
   * Get number of middlewares
   */
  getMiddlewareCount(): number {
    return this.middlewares.length;
  }

  /**
   * Clear all middlewares
   */
  clear(): void {
    this.middlewares = [];
  }
}

/**
 * Logging middleware
 * Logs operation start, completion, and duration
 */
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

/**
 * Error handling middleware
 * Catches errors and calls handler before re-throwing
 */
export function errorHandlingMiddleware<T>(
  handler: (error: Error) => void
): Middleware<T> {
  return async (next) => {
    try {
      return await next();
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      handler(err);
      throw error;
    }
  };
}

/**
 * Timeout middleware
 * Rejects if operation takes longer than specified time
 */
export function timeoutMiddleware<T>(timeoutMs: number): Middleware<T> {
  return async (next) => {
    let timeoutId: NodeJS.Timeout;

    const timeoutPromise = new Promise<T>((_, reject) => {
      timeoutId = setTimeout(
        () => reject(new Error(`Operation timed out after ${timeoutMs}ms`)),
        timeoutMs
      );
    });

    try {
      const result = await Promise.race([next(), timeoutPromise]);
      clearTimeout(timeoutId);
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  };
}

/**
 * Retry middleware
 * Retries operation on failure
 */
export function retryMiddleware<T>(
  maxRetries: number = 3,
  delayMs: number = 1000
): Middleware<T> {
  return async (next) => {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await next();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, delayMs));
        }
      }
    }

    throw lastError || new Error('Max retries exceeded');
  };
}

/**
 * Caching middleware
 * Caches successful results
 */
export function cachingMiddleware<T>(
  key: string,
  ttlMs?: number
): Middleware<T> {
  const cache = new Map<string, { value: T; expiry: number }>();

  return async (next) => {
    const cached = cache.get(key);

    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }

    const result = await next();
    cache.set(key, {
      value: result,
      expiry: ttlMs ? Date.now() + ttlMs : Infinity,
    });

    return result;
  };
}

/**
 * Request deduplication middleware
 * Prevents duplicate concurrent requests
 */
export function deduplicationMiddleware<T>(): Middleware<T> {
  const pending = new Map<string, Promise<T>>();
  let requestId = 0;

  return async (next) => {
    const id = String(++requestId);

    if (pending.has(id)) {
      return pending.get(id)!;
    }

    const promise = next()
      .then((result) => {
        pending.delete(id);
        return result;
      })
      .catch((error) => {
        pending.delete(id);
        throw error;
      });

    pending.set(id, promise);
    return promise;
  };
}

/**
 * Metrics middleware
 * Records operation metrics
 */
export interface OperationMetrics {
  duration: number;
  success: boolean;
  timestamp: number;
}

export function metricsMiddleware<T>(
  onMetrics: (metrics: OperationMetrics) => void
): Middleware<T> {
  return async (next) => {
    const start = Date.now();
    try {
      const result = await next();
      onMetrics({
        duration: Date.now() - start,
        success: true,
        timestamp: Date.now(),
      });
      return result;
    } catch (error) {
      onMetrics({
        duration: Date.now() - start,
        success: false,
        timestamp: Date.now(),
      });
      throw error;
    }
  };
}

/**
 * Context middleware
 * Passes context through middleware chain
 */
export function contextMiddleware<T>(context: Record<string, any>): Middleware<T> {
  return async (next) => {
    const original = globalThis as any;
    Object.assign(globalThis, context);

    try {
      return await next();
    } finally {
      Object.keys(context).forEach((key) => {
        delete (globalThis as any)[key];
      });
    }
  };
}
