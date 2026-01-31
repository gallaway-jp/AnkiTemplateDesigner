/**
 * Application Configuration Constants
 * Centralized configuration for bridge, performance, and behavior settings
 */

/**
 * Configuration validation errors
 */
export interface ConfigValidationError {
  field: string;
  value: unknown;
  message: string;
}

/**
 * Validate configuration values for sensible thresholds
 */
export function validateBridgeConfig(config: any): ConfigValidationError[] {
  const errors: ConfigValidationError[] = [];

  // Timeout validation
  if (config.timeout !== undefined) {
    if (typeof config.timeout !== 'number') {
      errors.push({
        field: 'timeout',
        value: config.timeout,
        message: 'timeout must be a number (milliseconds)',
      });
    } else if (config.timeout < 1000) {
      errors.push({
        field: 'timeout',
        value: config.timeout,
        message: 'timeout must be at least 1000ms (1 second)',
      });
    } else if (config.timeout > 300000) {
      errors.push({
        field: 'timeout',
        value: config.timeout,
        message: 'timeout should not exceed 300000ms (5 minutes)',
      });
    }
  }

  // Retry configuration validation
  if (config.retry !== undefined) {
    if (config.retry.maxRetries !== undefined) {
      if (config.retry.maxRetries < 0 || config.retry.maxRetries > 10) {
        errors.push({
          field: 'retry.maxRetries',
          value: config.retry.maxRetries,
          message: 'maxRetries must be between 0 and 10',
        });
      }
    }
    if (config.retry.baseDelay !== undefined) {
      if (config.retry.baseDelay < 10 || config.retry.baseDelay > 5000) {
        errors.push({
          field: 'retry.baseDelay',
          value: config.retry.baseDelay,
          message: 'baseDelay must be between 10ms and 5000ms',
        });
      }
    }
    if (config.retry.maxDelay !== undefined) {
      if (config.retry.maxDelay < config.retry.baseDelay) {
        errors.push({
          field: 'retry.maxDelay',
          value: config.retry.maxDelay,
          message: 'maxDelay must be greater than or equal to baseDelay',
        });
      }
    }
    if (config.retry.backoffMultiplier !== undefined) {
      if (config.retry.backoffMultiplier < 1 || config.retry.backoffMultiplier > 10) {
        errors.push({
          field: 'retry.backoffMultiplier',
          value: config.retry.backoffMultiplier,
          message: 'backoffMultiplier must be between 1 and 10',
        });
      }
    }
  }

  // Circuit breaker validation
  if (config.circuitBreaker !== undefined) {
    if (config.circuitBreaker.failureThreshold !== undefined) {
      if (config.circuitBreaker.failureThreshold < 1 || config.circuitBreaker.failureThreshold > 100) {
        errors.push({
          field: 'circuitBreaker.failureThreshold',
          value: config.circuitBreaker.failureThreshold,
          message: 'failureThreshold must be between 1 and 100',
        });
      }
    }
    if (config.circuitBreaker.successThreshold !== undefined) {
      if (config.circuitBreaker.successThreshold < 1 || config.circuitBreaker.successThreshold > 50) {
        errors.push({
          field: 'circuitBreaker.successThreshold',
          value: config.circuitBreaker.successThreshold,
          message: 'successThreshold must be between 1 and 50',
        });
      }
    }
    if (config.circuitBreaker.timeout !== undefined) {
      if (config.circuitBreaker.timeout < 10000 || config.circuitBreaker.timeout > 600000) {
        errors.push({
          field: 'circuitBreaker.timeout',
          value: config.circuitBreaker.timeout,
          message: 'timeout must be between 10000ms (10s) and 600000ms (10m)',
        });
      }
    }
  }

  return errors;
}

/**
 * Validate and return configuration with validation report
 */
export function validateAndGetConfig(config: any): {
  config: any;
  isValid: boolean;
  errors: ConfigValidationError[];
  warnings: string[];
} {
  const errors = validateBridgeConfig(config);
  const warnings: string[] = [];

  // Add warnings for suboptimal but valid configurations
  if (config.timeout && config.timeout < 5000) {
    warnings.push('timeout < 5000ms may cause timeouts on slow networks');
  }
  if (config.circuitBreaker?.failureThreshold === 1) {
    warnings.push('failureThreshold of 1 may cause circuit to open too quickly on transient errors');
  }

  return {
    config,
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Bridge Configuration
 * Settings for Python-JavaScript communication
 */
export const BRIDGE_CONFIG = {
  // Request timeout settings
  timeout: 30000, // 30 seconds default timeout
  requestTimeout: 5000, // Individual request timeout
  
  // Retry configuration
  retry: {
    maxRetries: 3,
    baseDelay: 100, // ms
    maxDelay: 5000, // ms
    backoffMultiplier: 2,
  },
  
  // Health check settings
  healthCheck: {
    interval: 30000, // Check every 30 seconds
    failureThreshold: 3, // Mark unhealthy after 3 failures
    recoveryAttempts: 3,
  },
  
  // Circuit breaker settings
  circuitBreaker: {
    failureThreshold: 5, // Open after 5 failures
    successThreshold: 2, // Close after 2 successes
    timeout: 60000, // 60 seconds before attempting half-open
  },
  
  // Request queue settings
  queue: {
    maxSize: 100,
    processingDelay: 10, // ms between queue items
  },
  
  // Debug settings
  debug: process.env.NODE_ENV === 'development',
} as const;

/**
 * Validation Configuration
 * Settings for template and field validation
 */
export const VALIDATION_CONFIG = {
  // Field validation
  field: {
    minLength: 1,
    maxLength: 100,
    pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, // Variable name pattern
  },
  
  // HTML validation
  html: {
    maxLength: 100000,
    allowedTags: ['div', 'span', 'p', 'img', 'br', 'hr', 'b', 'i', 'u', 'style', 'script'],
    blockedPatterns: [
      /on\w+\s*=/gi, // Event handlers (onclick, etc.)
      /<script[^>]*>.*?<\/script>/gi, // Script tags
    ],
  },
  
  // CSS validation
  css: {
    maxLength: 50000,
    blockedProperties: ['behavior', 'binding', 'javascript'],
    blockedPatterns: [
      /import\s+/gi, // CSS imports
      /expression\s*\(/gi, // IE expressions
    ],
  },
  
  // Template validation
  template: {
    minName: 1,
    maxName: 100,
    maxBlocks: 1000,
    maxNestingDepth: 10,
  },
} as const;

/**
 * Performance Configuration
 * Settings for rendering and optimization
 */
export const PERFORMANCE_CONFIG = {
  // Virtual scrolling
  virtualScroll: {
    itemHeight: 40,
    bufferSize: 5,
    maxVisibleItems: 100,
  },
  
  // Rendering
  rendering: {
    maxFPS: 60,
    debounceMs: 100,
    throttleMs: 50,
  },
  
  // Caching
  cache: {
    maxSize: 500,
    ttl: 5 * 60 * 1000, // 5 minutes
    enabled: true,
  },
  
  // Memory limits
  memory: {
    maxNodes: 10000,
    maxHistorySize: 100,
    maxLogSize: 1000,
  },
} as const;

/**
 * UI Configuration
 * Settings for user interface behavior
 */
export const UI_CONFIG = {
  // Panel settings
  panel: {
    minWidth: 200,
    maxWidth: 800,
    defaultWidth: 300,
    collapsible: true,
  },
  
  // Editor settings
  editor: {
    autoSave: true,
    autoSaveDelay: 5000,
    showGrid: true,
    gridSize: 10,
    snapToGrid: true,
  },
  
  // Keyboard shortcuts
  shortcuts: {
    undo: 'Ctrl+Z',
    redo: 'Ctrl+Y',
    save: 'Ctrl+S',
    delete: 'Delete',
    selectAll: 'Ctrl+A',
    copy: 'Ctrl+C',
    paste: 'Ctrl+V',
    cut: 'Ctrl+X',
  },
  
  // Toast/notification settings
  toast: {
    duration: 3000,
    maxStack: 3,
  },
} as const;

/**
 * Error Messages
 * Localized error messages with suggestions
 */
export const ERROR_MESSAGES = {
  // Validation errors
  INVALID_FIELD_NAME: {
    message: 'Invalid field name: {value}',
    suggestions: [
      'Field names must start with a letter or underscore',
      'Use only alphanumeric characters and underscores',
      'Examples: {{Front}}, {{Back}}, {{Examples}}',
    ],
  },
  
  INVALID_HTML: {
    message: 'Invalid HTML content: {detail}',
    suggestions: [
      'Check for unclosed tags',
      'Ensure all attributes are properly quoted',
      'Avoid using script tags or event handlers',
    ],
  },
  
  INVALID_CSS: {
    message: 'Invalid CSS syntax: {detail}',
    suggestions: [
      'Check for syntax errors in CSS rules',
      'Ensure all properties end with semicolons',
      'Avoid using imports or IE expressions',
    ],
  },
  
  // Bridge errors
  BRIDGE_TIMEOUT: {
    message: 'Request to Python timed out',
    suggestions: [
      'Check if Python process is running',
      'Verify QWebChannel connection',
      'Try again in a few moments',
    ],
  },
  
  BRIDGE_DISCONNECTED: {
    message: 'Bridge connection lost',
    suggestions: [
      'Restart the application',
      'Check Python process status',
      'Verify Qt WebChannel is available',
    ],
  },
  
  CIRCUIT_BREAKER_OPEN: {
    message: 'Service temporarily unavailable',
    suggestions: [
      'The bridge has experienced multiple failures',
      'System will attempt to recover automatically',
      'Try again in a few moments',
    ],
  },
} as const;

/**
 * Type guard to check if a key exists in config
 */
export function isValidConfigKey<T extends Record<string, any>>(config: T, key: string): key is keyof T {
  return key in config;
}

/**
 * Get configuration value with fallback
 */
export function getConfig<T extends Record<string, any>>(config: T, path: string, fallback?: any): any {
  const keys = path.split('.');
  let value: any = config;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return fallback;
    }
  }
  
  return value;
}
