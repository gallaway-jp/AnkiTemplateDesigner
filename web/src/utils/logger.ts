/**
 * Logging Utilities
 * Structured logging for the entire application
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  module: string;
  message: string;
  data?: any;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000;
  private isDevelopment = typeof import.meta !== 'undefined' ? (import.meta.env as any)?.DEV : false;

  /**
   * Create a logger for a specific module
   */
  createModuleLogger(moduleName: string) {
    return {
      debug: (message: string, data?: any) => this.log('debug', moduleName, message, data),
      info: (message: string, data?: any) => this.log('info', moduleName, message, data),
      warn: (message: string, data?: any) => this.log('warn', moduleName, message, data),
      error: (message: string, data?: any) => this.log('error', moduleName, message, data),
    };
  }

  /**
   * Log message
   */
  private log(level: LogLevel, module: string, message: string, data?: any) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      module,
      message,
      data,
    };

    this.logs.push(entry);

    // Maintain max log size
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Console output in development
    if (this.isDevelopment) {
      const prefix = `[${module}]`;
      if (level === 'error') {
        console.error(prefix, message, data || '');
      } else if (level === 'warn') {
        console.warn(prefix, message, data || '');
      } else if (level === 'debug') {
        console.debug(prefix, message, data || '');
      } else {
        console.log(prefix, message, data || '');
      }
    }
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Clear logs
   */
  clear(): void {
    this.logs = [];
  }

  /**
   * Get logs for a specific module
   */
  getModuleLogs(module: string): LogEntry[] {
    return this.logs.filter((log) => log.module === module);
  }

  /**
   * Export logs as JSON
   */
  export(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

// Export singleton
export const globalLogger = new Logger();

/**
 * Create module logger
 */
export function createLogger(moduleName: string) {
  return globalLogger.createModuleLogger(moduleName);
}

/**
 * Export all logs
 */
export function exportLogs(): string {
  return globalLogger.export();
}

// Export default module logger for convenience
export const logger = globalLogger.createModuleLogger('Global');
