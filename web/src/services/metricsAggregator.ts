/**
 * Error Aggregation and Monitoring Dashboard
 * Aggregates metrics and errors across multiple circuit breakers
 */

import { CircuitBreaker } from './circuitBreaker';

/**
 * Aggregated metrics for a single circuit breaker
 */
export interface BreakerMetrics {
  name: string;
  state: string;
  successCount: number;
  errorCount: number;
  timeoutCount: number;
  openedAt?: number;
  successRate: number;
  averageResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  totalRequests: number;
  health: 'healthy' | 'degraded' | 'critical';
}

/**
 * Error summary for dashboard
 */
export interface ErrorSummary {
  errorCode: string;
  count: number;
  lastOccurrence: number;
  affectedBreakers: string[];
  recentErrors: {
    timestamp: number;
    message: string;
    breakerName: string;
  }[];
}

/**
 * Dashboard snapshot at a point in time
 */
export interface DashboardSnapshot {
  timestamp: number;
  totalBreakers: number;
  healthyBreakers: number;
  degradedBreakers: number;
  criticalBreakers: number;
  totalRequests: number;
  totalErrors: number;
  totalTimeouts: number;
  systemHealthScore: number; // 0-100
  breakersMetrics: BreakerMetrics[];
  errorSummaries: ErrorSummary[];
  topErrors: string[];
}

/**
 * Error history entry
 */
export interface ErrorHistoryEntry {
  timestamp: number;
  breakerName: string;
  errorCode: string;
  message: string;
  stackTrace?: string;
}

/**
 * Circuit Breaker Metrics Aggregator
 * Monitors and aggregates metrics from multiple circuit breakers
 */
export class CircuitBreakerAggregator {
  private breakers: Map<string, CircuitBreaker<any>> = new Map();
  private errorHistory: ErrorHistoryEntry[] = [];
  private maxHistorySize: number = 10000;
  private lastSnapshot: DashboardSnapshot | null = null;

  /**
   * Register a circuit breaker for monitoring
   */
  registerBreaker(name: string, breaker: CircuitBreaker<any>): void {
    this.breakers.set(name, breaker);
  }

  /**
   * Unregister a circuit breaker
   */
  unregisterBreaker(name: string): void {
    this.breakers.delete(name);
  }

  /**
   * Get metrics for a specific breaker
   */
  getBreakerMetrics(name: string): BreakerMetrics | null {
    const breaker = this.breakers.get(name);
    if (!breaker) {
      return null;
    }

    const metrics = breaker.getMetrics();
    const totalRequests = metrics.successCount + metrics.errorCount;
    const successRate = totalRequests > 0 ? metrics.successCount / totalRequests : 1;
    const health = this.calculateHealth(
      successRate,
      breaker.getState(),
      metrics.averageResponseTime
    );

    return {
      name,
      state: breaker.getState(),
      successCount: metrics.successCount,
      errorCount: metrics.errorCount,
      timeoutCount: metrics.timeoutCount,
      openedAt: (breaker as any).openedAt,
      successRate: successRate * 100,
      averageResponseTime: metrics.averageResponseTime,
      p95ResponseTime: metrics.p95ResponseTime,
      p99ResponseTime: metrics.p99ResponseTime,
      totalRequests,
      health,
    };
  }

  /**
   * Get all breaker metrics
   */
  getAllMetrics(): BreakerMetrics[] {
    const metrics: BreakerMetrics[] = [];
    this.breakers.forEach((breaker, name) => {
      const breakerMetrics = this.getBreakerMetrics(name);
      if (breakerMetrics) {
        metrics.push(breakerMetrics);
      }
    });
    return metrics;
  }

  /**
   * Record error in history
   */
  recordError(
    breakerName: string,
    errorCode: string,
    message: string,
    stackTrace?: string
  ): void {
    this.errorHistory.push({
      timestamp: Date.now(),
      breakerName,
      errorCode,
      message,
      stackTrace,
    });

    // Keep history size bounded
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(-this.maxHistorySize);
    }
  }

  /**
   * Get error summaries
   */
  getErrorSummaries(): ErrorSummary[] {
    const summaries: Map<string, ErrorSummary> = new Map();

    this.errorHistory.forEach((entry) => {
      if (!summaries.has(entry.errorCode)) {
        summaries.set(entry.errorCode, {
          errorCode: entry.errorCode,
          count: 0,
          lastOccurrence: 0,
          affectedBreakers: [],
          recentErrors: [],
        });
      }

      const summary = summaries.get(entry.errorCode)!;
      summary.count++;
      summary.lastOccurrence = Math.max(summary.lastOccurrence, entry.timestamp);

      if (!summary.affectedBreakers.includes(entry.breakerName)) {
        summary.affectedBreakers.push(entry.breakerName);
      }

      summary.recentErrors.push({
        timestamp: entry.timestamp,
        message: entry.message,
        breakerName: entry.breakerName,
      });

      // Keep only recent errors
      if (summary.recentErrors.length > 10) {
        summary.recentErrors = summary.recentErrors.slice(-10);
      }
    });

    return Array.from(summaries.values()).sort((a, b) => b.count - a.count);
  }

  /**
   * Get dashboard snapshot
   */
  getDashboard(): DashboardSnapshot {
    const metrics = this.getAllMetrics();
    const errorSummaries = this.getErrorSummaries();

    const healthyCounts = metrics.filter((m) => m.health === 'healthy').length;
    const degradedCounts = metrics.filter((m) => m.health === 'degraded').length;
    const criticalCounts = metrics.filter((m) => m.health === 'critical').length;

    const totalRequests = metrics.reduce((sum, m) => sum + m.totalRequests, 0);
    const totalErrors = metrics.reduce((sum, m) => sum + m.errorCount, 0);
    const totalTimeouts = metrics.reduce((sum, m) => sum + m.timeoutCount, 0);

    const systemHealthScore = this.calculateSystemHealth(metrics);

    const snapshot: DashboardSnapshot = {
      timestamp: Date.now(),
      totalBreakers: metrics.length,
      healthyBreakers: healthyCounts,
      degradedBreakers: degradedCounts,
      criticalBreakers: criticalCounts,
      totalRequests,
      totalErrors,
      totalTimeouts,
      systemHealthScore,
      breakersMetrics: metrics,
      errorSummaries,
      topErrors: errorSummaries
        .slice(0, 5)
        .map((e) => `${e.errorCode} (${e.count} occurrences)`),
    };

    this.lastSnapshot = snapshot;
    return snapshot;
  }

  /**
   * Get last cached snapshot
   */
  getLastSnapshot(): DashboardSnapshot | null {
    return this.lastSnapshot;
  }

  /**
   * Get health status for all breakers
   */
  getHealthStatus(): {
    healthy: string[];
    degraded: string[];
    critical: string[];
  } {
    const metrics = this.getAllMetrics();
    return {
      healthy: metrics.filter((m) => m.health === 'healthy').map((m) => m.name),
      degraded: metrics.filter((m) => m.health === 'degraded').map((m) => m.name),
      critical: metrics.filter((m) => m.health === 'critical').map((m) => m.name),
    };
  }

  /**
   * Get error trends over time
   */
  getErrorTrends(windowMs: number = 3600000): Record<string, number> {
    const now = Date.now();
    const cutoff = now - windowMs;

    const trends: Record<string, number> = {};

    this.errorHistory
      .filter((entry) => entry.timestamp > cutoff)
      .forEach((entry) => {
        if (!trends[entry.errorCode]) {
          trends[entry.errorCode] = 0;
        }
        trends[entry.errorCode]++;
      });

    return trends;
  }

  /**
   * Clear error history
   */
  clearErrorHistory(): void {
    this.errorHistory = [];
  }

  /**
   * Get error history
   */
  getErrorHistory(limit: number = 100): ErrorHistoryEntry[] {
    return this.errorHistory.slice(-limit);
  }

  /**
   * Calculate health score for a breaker
   */
  private calculateHealth(
    successRate: number,
    state: string,
    avgResponseTime: number
  ): 'healthy' | 'degraded' | 'critical' {
    // Critical conditions
    if (state === 'OPEN' || successRate < 0.5) {
      return 'critical';
    }

    // Degraded conditions
    if (successRate < 0.8 || avgResponseTime > 5000) {
      return 'degraded';
    }

    return 'healthy';
  }

  /**
   * Calculate overall system health
   */
  private calculateSystemHealth(metrics: BreakerMetrics[]): number {
    if (metrics.length === 0) {
      return 100;
    }

    let score = 0;
    metrics.forEach((m) => {
      if (m.health === 'healthy') {
        score += 100;
      } else if (m.health === 'degraded') {
        score += 50;
      } else {
        score += 0;
      }
    });

    return Math.round(score / metrics.length);
  }
}

/**
 * Global metrics aggregator instance
 */
export const globalMetricsAggregator = new CircuitBreakerAggregator();

/**
 * Dashboard query interface
 */
export interface DashboardQuery {
  breakerName?: string;
  errorCode?: string;
  timeWindow?: number;
}

/**
 * Dashboard service for querying metrics
 */
export class DashboardService {
  constructor(private aggregator: CircuitBreakerAggregator) {}

  /**
   * Query dashboard data
   */
  query(query: DashboardQuery): any {
    const dashboard = this.aggregator.getDashboard();

    let metrics = dashboard.breakersMetrics;
    if (query.breakerName) {
      metrics = metrics.filter((m) => m.name === query.breakerName);
    }

    let errors = dashboard.errorSummaries;
    if (query.errorCode) {
      errors = errors.filter((e) => e.errorCode === query.errorCode);
    }

    return {
      ...dashboard,
      breakersMetrics: metrics,
      errorSummaries: errors,
      trends: this.aggregator.getErrorTrends(query.timeWindow),
    };
  }

  /**
   * Get alert thresholds
   */
  getAlerts(): {
    critical: string[];
    warning: string[];
  } {
    const alerts: string[] = [];
    const warnings: string[] = [];

    const health = this.aggregator.getHealthStatus();
    if (health.critical.length > 0) {
      alerts.push(`${health.critical.length} breakers in critical state`);
    }

    if (health.degraded.length > 0) {
      warnings.push(`${health.degraded.length} breakers in degraded state`);
    }

    return { critical: alerts, warning: warnings };
  }
}
