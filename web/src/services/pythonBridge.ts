/**
 * Type-Safe Python Bridge Service with Advanced Features
 * Manages bidirectional communication with Python via QWebChannel
 * Features: Retry logic, timeout handling, request batching, performance metrics
 */

import {
  BridgeMessage,
  BridgeRequest,
  BridgeResponse,
  BridgeMethod,
  BridgeConfig,
  BridgeError,
  BridgeListener,
  AnkiField,
  AnkiBehavior,
  Template,
} from '@/types';

/**
 * Performance metrics for bridge requests
 */
interface RequestMetrics {
  startTime: number;
  endTime?: number;
  duration?: number;
  retries: number;
  success: boolean;
}

/**
 * Request queue item
 */
interface QueuedRequest {
  method: BridgeMethod;
  params: Record<string, any>;
  priority: number;
  timestamp: number;
}

/**
 * Health check status
 */
interface HealthStatus {
  isConnected: boolean;
  lastResponseTime?: number;
  consecutiveFailures: number;
  totalRequests: number;
  successRate: number;
}

/**
 * Error class for bridge communication failures
 */
export class BridgeError implements BridgeError {
  code: string;
  message: string;
  details?: any;
  stack?: string;

  constructor(code: string, message: string, details?: any) {
    this.code = code;
    this.message = message;
    this.details = details;
    this.stack = new Error().stack;
  }
}

/**
 * Main PythonBridge class for communication with Python
 */
export class PythonBridge {
  private static instance: PythonBridge;
  private bridge: any = null;
  private requestMap: Map<string, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
    timer: NodeJS.Timeout;
    metrics: RequestMetrics;
  }> = new Map();
  private listeners: Map<string, Set<BridgeListener>> = new Map();
  private config: BridgeConfig;
  private isInitialized: boolean = false;
  
  // Advanced features
  private requestQueue: QueuedRequest[] = [];
  private isProcessingQueue: boolean = false;
  private metrics: Map<BridgeMethod, RequestMetrics[]> = new Map();
  private health: HealthStatus = {
    isConnected: false,
    consecutiveFailures: 0,
    totalRequests: 0,
    successRate: 100,
  };
  private retryConfig = {
    maxRetries: 3,
    baseDelay: 100,
    maxDelay: 5000,
  };
  private healthCheckInterval: NodeJS.Timeout | null = null;

  private constructor(config: Partial<BridgeConfig> = {}) {
    this.config = {
      timeout: config.timeout ?? 5000,
      retries: config.retries ?? 3,
      debug: config.debug ?? false,
    };
    
    // Update retry config from provided config
    if (config.timeout) {
      this.retryConfig.maxDelay = config.timeout;
    }
    if (config.retries) {
      this.retryConfig.maxRetries = config.retries;
    }
  }

  /**
   * Get or create singleton instance
   */
  static getInstance(config?: Partial<BridgeConfig>): PythonBridge {
    if (!PythonBridge.instance) {
      PythonBridge.instance = new PythonBridge(config);
    }
    return PythonBridge.instance;
  }

  /**
   * Initialize bridge connection with Python
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.logInternal('warn', 'Bridge initialization timeout - using mock bridge');
        this.useMockBridge();
        this.isInitialized = true;
        this.startHealthCheck();
        resolve();
      }, this.config.timeout);

      try {
        // Check for QWebChannel (Qt WebEngine)
        if (typeof (window as any).QWebChannel === 'undefined') {
          this.logInternal('warn', 'QWebChannel not available - using mock bridge');
          clearTimeout(timeout);
          this.useMockBridge();
          this.isInitialized = true;
          this.startHealthCheck();
          resolve();
          return;
        }

        // Set up QWebChannel
        new (window as any).QWebChannel((window as any).qt.webChannelTransport, (channel: any) => {
          clearTimeout(timeout);
          this.bridge = channel.objects.bridge;
          
          if (!this.bridge) {
            throw new Error('Bridge object not found in QWebChannel');
          }

          this.setupBridgeListeners();
          this.isInitialized = true;
          this.health.isConnected = true;
          this.logInternal('info', 'Bridge initialized successfully');
          this.startHealthCheck();
          resolve();
        });
      } catch (error) {
        clearTimeout(timeout);
        this.logInternal('error', `Bridge initialization failed: ${error}`);
        this.useMockBridge();
        this.isInitialized = true;
        this.startHealthCheck();
        resolve();
      }
    });
  }

  /**
   * Start periodic health check
   */
  private startHealthCheck(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(() => {
      this.checkHealth();
    }, 30000); // Check every 30 seconds
  }

  /**
   * Check bridge health and recover if needed
   */
  private async checkHealth(): Promise<void> {
    try {
      // Send ping request
      await this.sendRequest('ping', {}, true); // true = skip queue
      
      this.health.isConnected = true;
      this.health.consecutiveFailures = 0;
      
      this.logInternal('info', `Health check passed. Success rate: ${this.health.successRate.toFixed(2)}%`);
    } catch (error) {
      this.health.consecutiveFailures++;
      
      if (this.health.consecutiveFailures >= 3) {
        this.health.isConnected = false;
        this.logInternal('error', 'Health check failed - bridge may be disconnected');
        this.attemptRecovery();
      }
    }
  }

  /**
   * Attempt to recover from connection failure
   */
  private async attemptRecovery(): Promise<void> {
    this.logInternal('warn', 'Attempting bridge recovery...');
    
    try {
      await this.initialize();
      this.logInternal('info', 'Bridge recovery successful');
    } catch (error) {
      this.logInternal('error', `Bridge recovery failed: ${error}`);
    }
  }

  /**
   * Set up listeners for bridge messages from Python
   */
  private setupBridgeListeners(): void {
    if (!this.bridge) return;

    // Listen for responses
    if (this.bridge.messageReceived) {
      this.bridge.messageReceived.connect((messageStr: string) => {
        this.handleMessage(JSON.parse(messageStr));
      });
    }

    // Listen for field updates
    if (this.bridge.fieldsUpdated) {
      this.bridge.fieldsUpdated.connect((fieldsStr: string) => {
        this.emitEvent('fieldsUpdated', JSON.parse(fieldsStr));
      });
    }

    // Listen for settings updates
    if (this.bridge.settingsUpdated) {
      this.bridge.settingsUpdated.connect((settingsStr: string) => {
        this.emitEvent('settingsUpdated', JSON.parse(settingsStr));
      });
    }
  }

  /**
   * Handle incoming message from Python
   */
  private handleMessage(message: BridgeResponse): void {
    if (!message.requestId) return;

    const pending = this.requestMap.get(message.requestId);
    if (!pending) return;

    clearTimeout(pending.timer);
    
    // Record metrics
    pending.metrics.endTime = Date.now();
    pending.metrics.duration = pending.metrics.endTime - pending.metrics.startTime;
    pending.metrics.success = !message.error;
    
    this.recordMetrics(pending.metrics);
    this.requestMap.delete(message.requestId);

    if (message.error) {
      this.health.consecutiveFailures++;
      pending.reject(new BridgeError('BRIDGE_ERROR', message.error, message));
    } else {
      this.health.consecutiveFailures = 0;
      this.health.lastResponseTime = Date.now();
      pending.resolve(message.result);
    }
    
    // Process next item in queue
    this.processQueue();
  }

  /**
   * Record request metrics for analytics
   */
  private recordMetrics(metrics: RequestMetrics): void {
    this.health.totalRequests++;
    
    // Calculate success rate
    const totalAttempts = this.health.totalRequests;
    const totalRetries = Array.from(this.metrics.values())
      .flat()
      .reduce((sum, m) => sum + m.retries, 0);
    
    this.health.successRate = 100 * (this.health.totalRequests - this.health.consecutiveFailures) / totalAttempts;
  }

  /**
   * Get performance metrics for a method
   */
  getMetrics(method?: BridgeMethod): { method?: string; averageLatency: number; totalRequests: number; successCount: number } {
    if (method) {
      const methodMetrics = this.metrics.get(method) || [];
      const totalRequests = methodMetrics.length;
      const successCount = methodMetrics.filter(m => m.success).length;
      const totalDuration = methodMetrics.reduce((sum, m) => sum + (m.duration || 0), 0);
      const averageLatency = totalRequests > 0 ? totalDuration / totalRequests : 0;
      
      return { method, averageLatency, totalRequests, successCount };
    }

    // All methods
    const allMetrics = Array.from(this.metrics.values()).flat();
    const totalRequests = allMetrics.length;
    const successCount = allMetrics.filter(m => m.success).length;
    const totalDuration = allMetrics.reduce((sum, m) => sum + (m.duration || 0), 0);
    const averageLatency = totalRequests > 0 ? totalDuration / totalRequests : 0;
    
    return { averageLatency, totalRequests, successCount };
  }

  /**
   * Get health status
   */
  getHealthStatus(): HealthStatus {
    return { ...this.health };
  }

  /**
   * Send request to Python with retry logic
   */
  private async sendRequest(
    method: BridgeMethod,
    params: Record<string, any> = {},
    skipQueue: boolean = false,
    retryCount: number = 0
  ): Promise<any> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // Add to queue if not skipping
    if (!skipQueue && this.isProcessingQueue) {
      return new Promise((resolve, reject) => {
        this.requestQueue.push({ method, params, priority: 0, timestamp: Date.now() });
      });
    }

    const requestId = this.generateRequestId();
    const metrics: RequestMetrics = {
      startTime: Date.now(),
      retries: retryCount,
      success: false,
    };

    const request: BridgeRequest = {
      method,
      requestId,
      params,
    };

    return new Promise((resolve, reject) => {
      // Set up timeout with exponential backoff
      const timeout = Math.min(
        this.config.timeout * Math.pow(1.5, retryCount),
        this.retryConfig.maxDelay
      );

      const timer = setTimeout(async () => {
        this.requestMap.delete(requestId);
        metrics.endTime = Date.now();
        metrics.duration = metrics.endTime - metrics.startTime;
        metrics.success = false;
        this.recordMetrics(metrics);

        // Retry with exponential backoff
        if (retryCount < this.retryConfig.maxRetries) {
          const delay = Math.min(
            this.retryConfig.baseDelay * Math.pow(2, retryCount),
            this.retryConfig.maxDelay
          );

          this.logInternal('warn', `Request ${method} timed out, retrying in ${delay}ms (attempt ${retryCount + 1}/${this.retryConfig.maxRetries})`);

          setTimeout(async () => {
            try {
              const result = await this.sendRequest(method, params, skipQueue, retryCount + 1);
              resolve(result);
            } catch (error) {
              reject(error);
            }
          }, delay);
        } else {
          reject(new BridgeError(
            'TIMEOUT',
            `Request ${method} failed after ${this.retryConfig.maxRetries} retries`,
            { method, attempts: retryCount + 1, totalDuration: metrics.duration }
          ));
        }
      }, timeout);

      // Store pending request
      this.requestMap.set(requestId, { resolve, reject, timer, metrics });

      // Send request
      try {
        if (this.bridge && typeof this.bridge.sendMessage === 'function') {
          this.bridge.sendMessage(JSON.stringify(request));
        } else {
          // Mock bridge
          setTimeout(() => {
            this.handleMockResponse(request);
          }, 50);
        }
      } catch (error) {
        clearTimeout(timer);
        this.requestMap.delete(requestId);
        metrics.endTime = Date.now();
        metrics.duration = metrics.endTime - metrics.startTime;
        this.recordMetrics(metrics);
        reject(new BridgeError('SEND_ERROR', `Failed to send request: ${error}`));
      }
    });
  }

  /**
   * Add request to queue for batch processing
   */
  queueRequest(method: BridgeMethod, params: Record<string, any> = {}, priority: number = 0): void {
    this.requestQueue.push({
      method,
      params,
      priority,
      timestamp: Date.now(),
    });

    // Sort by priority (higher = first)
    this.requestQueue.sort((a, b) => b.priority - a.priority);

    // Start processing if not already
    if (!this.isProcessingQueue) {
      this.processQueue();
    }
  }

  /**
   * Process queued requests
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    while (this.requestQueue.length > 0) {
      const queued = this.requestQueue.shift();
      if (!queued) break;

      try {
        await this.sendRequest(queued.method, queued.params, false);
      } catch (error) {
        this.logInternal('error', `Failed to process queued request: ${error}`);
      }

      // Small delay between queue items
      await new Promise(resolve => setTimeout(resolve, 10));
    }

    this.isProcessingQueue = false;
  }

  /**
   * Batch multiple requests together
   */
  async batchRequests(requests: Array<{ method: BridgeMethod; params: Record<string, any> }>): Promise<any[]> {
    const promises = requests.map(req => this.sendRequest(req.method, req.params));
    return Promise.all(promises);
  }

  /**
   * Handle mock bridge responses
   */
  private handleMockResponse(request: BridgeRequest): void {
    const response: BridgeResponse = {
      requestId: request.requestId!,
      method: request.method,
      result: this.getMockResult(request.method, request.params),
    };

    setTimeout(() => {
      this.handleMessage(response);
    }, Math.random() * 100);
  }

  /**
   * Get mock result for testing
   */
  private getMockResult(method: BridgeMethod, params: Record<string, any>): any {
    switch (method) {
      case 'getAnkiFields':
        return [
          { name: 'Front', description: 'Front of card' },
          { name: 'Back', description: 'Back of card' },
        ];

      case 'getAnkiBehaviors':
        return [
          { name: 'sound', description: 'Play sound' },
          { name: 'hint', description: 'Show hint' },
        ];

      case 'saveTemplate':
        return {
          success: true,
          templateId: params.id || 'template-123',
          timestamp: Date.now(),
        };

      case 'loadTemplate':
        return {
          id: params.templateId,
          name: 'Sample Template',
          html: '<div>Sample</div>',
          css: '',
        };

      case 'exportTemplate':
        return {
          data: params.format === 'html' ? '<div>Template</div>' : '{}',
          format: params.format,
          mimeType: params.format === 'html' ? 'text/html' : 'application/json',
        };

      case 'validateTemplate':
        return {
          isValid: true,
          errors: [],
          warnings: [],
        };

      case 'ping':
        return { success: true, timestamp: Date.now() };

      default:
        return { success: true };
    }
  }

  /**
   * Use mock bridge when QWebChannel unavailable
   */
  private useMockBridge(): void {
    this.bridge = {
      sendMessage: (msg: string) => {
        const request = JSON.parse(msg);
        this.handleMockResponse(request);
      },
    };
  }

  // ===== Public API Methods =====

  /**
   * Save template to Anki
   */
  async saveTemplate(template: Template): Promise<{ success: boolean; templateId: string; timestamp: number }> {
    return this.sendRequest('saveTemplate', {
      id: template.id,
      name: template.name,
      html: template.html,
      css: template.css,
      metadata: template.meta,
    });
  }

  /**
   * Load template from Anki
   */
  async loadTemplate(templateId: string): Promise<Template> {
    return this.sendRequest('loadTemplate', { templateId });
  }

  /**
   * Export template in specified format
   */
  async exportTemplate(
    templateId: string,
    format: 'html' | 'json',
    minify: boolean = false
  ): Promise<{ data: string; format: string; mimeType: string }> {
    return this.sendRequest('exportTemplate', {
      id: templateId,
      format,
      minify,
    });
  }

  /**
   * Request preview of template
   */
  async previewTemplate(
    html: string,
    css: string,
    fields: Record<string, string>,
    side: 'front' | 'back'
  ): Promise<{ html: string; css: string }> {
    return this.sendRequest('previewTemplate', {
      html,
      css,
      fields,
      side,
    });
  }

  /**
   * Get available Anki fields
   */
  async getAnkiFields(): Promise<AnkiField[]> {
    return this.sendRequest('getAnkiFields');
  }

  /**
   * Get available Anki behaviors
   */
  async getAnkiBehaviors(): Promise<AnkiBehavior[]> {
    return this.sendRequest('getAnkiBehaviors');
  }

  /**
   * Validate template
   */
  async validateTemplate(
    html: string,
    css: string
  ): Promise<{ isValid: boolean; errors: any[]; warnings: any[] }> {
    return this.sendRequest('validateTemplate', { html, css });
  }

  /**
   * Import template from HTML/JSON
   */
  async importTemplate(data: string, format: 'html' | 'json'): Promise<Template> {
    return this.sendRequest('importTemplate', { data, format });
  }

  /**
   * Log message to Python console
   */
  async log(message: string, level: 'info' | 'warn' | 'error' = 'info'): Promise<void> {
    return this.sendRequest('log', { message, level });
  }

  /**
   * Show error dialog
   */
  async showError(message: string, title?: string): Promise<void> {
    return this.sendRequest('showError', { message, title });
  }

  /**
   * Ping bridge to check connection
   */
  async ping(): Promise<{ success: boolean; timestamp: number }> {
    return this.sendRequest('ping', {}, true); // Skip queue for health checks
  }

  // ===== Event Listener Methods =====

  /**
   * Register listener for field updates
   */
  onFieldsUpdated(callback: (fields: AnkiField[]) => void): () => void {
    return this.addEventListener('fieldsUpdated', callback);
  }

  /**
   * Register listener for settings updates
   */
  onSettingsUpdated(callback: (settings: any) => void): () => void {
    return this.addEventListener('settingsUpdated', callback);
  }

  /**
   * Register listener for template loaded event
   */
  onTemplateLoaded(callback: (template: Template) => void): () => void {
    return this.addEventListener('templateLoaded', callback);
  }

  /**
   * Add event listener
   */
  private addEventListener(event: string, callback: BridgeListener): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }

    this.listeners.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  /**
   * Emit event to all listeners
   */
  private emitEvent(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (!callbacks) return;

    callbacks.forEach((callback) => {
      try {
        callback(data);
      } catch (error) {
        this.logInternal('error', `Error in ${event} listener: ${error}`);
      }
    });
  }

  /**
   * Disconnect and cleanup
   */
  disconnect(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    this.requestMap.forEach(({ timer }) => clearTimeout(timer));
    this.requestMap.clear();
    this.requestQueue = [];
    this.listeners.clear();
    this.isInitialized = false;
    this.health.isConnected = false;
  }

  // ===== Utility Methods =====

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Internal logging
   */
  private logInternal(level: 'info' | 'warn' | 'error', message: string): void {
    if (this.config.debug) {
      const prefix = `[Bridge] [${level.toUpperCase()}]`;
      if (level === 'error') {
        console.error(prefix, message);
      } else if (level === 'warn') {
        console.warn(prefix, message);
      } else {
        console.log(prefix, message);
      }
    }
  }
}

/**
 * Export singleton instance for easy importing
 */
export const bridge = PythonBridge.getInstance();
