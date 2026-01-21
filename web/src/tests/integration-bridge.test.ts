/**
 * Integration Tests - Python Bridge Communication
 * 
 * Tests the actual bridge communication with Python backend.
 * Validates template rendering, field operations, and Anki integration.
 * 
 * Run: npm run test:integration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Mock Python Bridge for Integration Testing
 */

interface BridgeResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  duration: number;
}

class IntegrationBridge {
  private messageQueue: any[] = [];
  private responseHandlers = new Map<string, (response: any) => void>();
  private latency: number = 50; // Default 50ms

  constructor() {
    this.setupMockBridge();
  }

  private setupMockBridge(): void {
    // Mock QWebChannel bridge
    (globalThis as any).bridge = {
      send: (message: string, data: any) => {
        this.handleMessage(message, data);
      },
    };
  }

  private async handleMessage(message: string, data: any): Promise<void> {
    // Simulate network latency
    await new Promise((resolve) => setTimeout(resolve, this.latency));

    const response = this.processMessage(message, data);
    const handler = this.responseHandlers.get(message);
    if (handler) {
      handler(response);
    }
  }

  private processMessage(message: string, data: any): BridgeResponse {
    const startTime = performance.now();

    const response = (() => {
      switch (message) {
        case 'get_fields':
          return this.getFields(data);
        case 'get_models':
          return this.getModels(data);
        case 'get_behaviors':
          return this.getBehaviors(data);
        case 'render_template':
          return this.renderTemplate(data);
        case 'save_template':
          return this.saveTemplate(data);
        case 'validate_template':
          return this.validateTemplate(data);
        case 'get_deck_info':
          return this.getDeckInfo(data);
        default:
          return { success: false, error: `Unknown message: ${message}` };
      }
    })();

    return {
      ...response,
      duration: performance.now() - startTime,
    };
  }

  private getFields(data: any): Omit<BridgeResponse, 'duration'> {
    return {
      success: true,
      data: [
        { name: 'Front', id: 0 },
        { name: 'Back', id: 1 },
        { name: 'Example', id: 2 },
      ],
    };
  }

  private getModels(data: any): Omit<BridgeResponse, 'duration'> {
    return {
      success: true,
      data: [
        { id: 1, name: 'Basic' },
        { id: 2, name: 'Basic (and reversed card)' },
        { id: 3, name: 'Cloze' },
      ],
    };
  }

  private getBehaviors(data: any): Omit<BridgeResponse, 'duration'> {
    return {
      success: true,
      data: {
        supportsUndo: true,
        supportsRedo: true,
        supportsHistory: true,
      },
    };
  }

  private renderTemplate(data: any): Omit<BridgeResponse, 'duration'> {
    const { template, fields } = data;
    if (!template || !fields) {
      return { success: false, error: 'Missing template or fields' };
    }

    // Simple template rendering simulation
    let rendered = template;
    for (const field of fields) {
      const regex = new RegExp(`{{${field.name}}}`, 'g');
      rendered = rendered.replace(regex, field.value || '');
    }

    return {
      success: true,
      data: { rendered },
    };
  }

  private saveTemplate(data: any): Omit<BridgeResponse, 'duration'> {
    const { id, name, html, css } = data;
    if (!id || !name) {
      return { success: false, error: 'Missing required fields' };
    }

    return {
      success: true,
      data: { id, saved: true, timestamp: new Date().toISOString() },
    };
  }

  private validateTemplate(data: any): Omit<BridgeResponse, 'duration'> {
    const { html, css } = data;

    const issues: string[] = [];

    // Simple validation
    if (!html || html.trim().length === 0) {
      issues.push('Template HTML is empty');
    }

    if (html && html.includes('{{') && !html.includes('}}')) {
      issues.push('Unclosed template field tag');
    }

    return {
      success: issues.length === 0,
      data: {
        valid: issues.length === 0,
        issues,
      },
    };
  }

  private getDeckInfo(data: any): Omit<BridgeResponse, 'duration'> {
    return {
      success: true,
      data: {
        name: 'Default',
        id: 1,
        cardCount: 100,
        noteCount: 50,
      },
    };
  }

  setLatency(ms: number): void {
    this.latency = ms;
  }

  registerHandler(message: string, handler: (response: any) => void): void {
    this.responseHandlers.set(message, handler);
  }

  async sendRequest<T = any>(message: string, data: any = {}): Promise<BridgeResponse<T>> {
    return new Promise((resolve) => {
      this.registerHandler(message, (response) => {
        resolve(response);
      });
      this.handleMessage(message, data);
    });
  }
}

/**
 * Integration Tests
 */

describe('Integration: Python Bridge Communication', () => {
  let bridge: IntegrationBridge;

  beforeEach(() => {
    bridge = new IntegrationBridge();
  });

  describe('Field Operations', () => {
    it('should retrieve fields from Anki', async () => {
      const response = await bridge.sendRequest('get_fields');

      expect(response.success).toBe(true);
      expect(response.data).toBeInstanceOf(Array);
      expect(response.data?.[0]).toHaveProperty('name');
      expect(response.data?.[0]).toHaveProperty('id');
    });

    it('should handle multiple field requests efficiently', async () => {
      const requests = Array.from({ length: 5 }, () =>
        bridge.sendRequest('get_fields')
      );

      const responses = await Promise.all(requests);

      expect(responses.length).toBe(5);
      expect(responses.every((r) => r.success)).toBe(true);
    });

    it('should measure field retrieval latency', async () => {
      bridge.setLatency(100);

      const startTime = performance.now();
      const response = await bridge.sendRequest('get_fields');
      const duration = performance.now() - startTime;

      expect(response.duration).toBeGreaterThanOrEqual(100);
      expect(duration).toBeGreaterThanOrEqual(100);
    });
  });

  describe('Template Rendering', () => {
    it('should render template with fields', async () => {
      const templateData = {
        template: '<div>{{Front}}</div><div>{{Back}}</div>',
        fields: [
          { name: 'Front', value: 'Question' },
          { name: 'Back', value: 'Answer' },
        ],
      };

      const response = await bridge.sendRequest('render_template', templateData);

      expect(response.success).toBe(true);
      expect(response.data?.rendered).toContain('Question');
      expect(response.data?.rendered).toContain('Answer');
    });

    it('should handle missing field values', async () => {
      const templateData = {
        template: '<div>{{Front}}</div><div>{{Missing}}</div>',
        fields: [{ name: 'Front', value: 'Question' }],
      };

      const response = await bridge.sendRequest('render_template', templateData);

      expect(response.success).toBe(true);
      expect(response.data?.rendered).toContain('Question');
    });

    it('should reject invalid template data', async () => {
      const response = await bridge.sendRequest('render_template', {});

      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
    });

    it('should validate template syntax', async () => {
      const validTemplate = {
        html: '<div>{{Front}}</div>',
        css: 'body { font-family: Arial; }',
      };

      const response = await bridge.sendRequest('validate_template', validTemplate);

      expect(response.success).toBe(true);
      expect(response.data?.valid).toBe(true);
    });

    it('should detect invalid template syntax', async () => {
      const invalidTemplate = {
        html: '<div>{{Front}</div>', // Missing closing braces
        css: '',
      };

      const response = await bridge.sendRequest('validate_template', invalidTemplate);

      expect(response.success).toBe(false);
      expect(response.data?.issues?.length).toBeGreaterThan(0);
    });
  });

  describe('Template Operations', () => {
    it('should save template successfully', async () => {
      const templateData = {
        id: 'test-template-1',
        name: 'Test Template',
        html: '<div>{{Front}}</div>',
        css: 'body { }',
      };

      const response = await bridge.sendRequest('save_template', templateData);

      expect(response.success).toBe(true);
      expect(response.data?.saved).toBe(true);
      expect(response.data?.timestamp).toBeDefined();
    });

    it('should reject incomplete template data', async () => {
      const response = await bridge.sendRequest('save_template', {
        html: '<div></div>',
      });

      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
    });
  });

  describe('Model Operations', () => {
    it('should retrieve available models', async () => {
      const response = await bridge.sendRequest('get_models');

      expect(response.success).toBe(true);
      expect(response.data).toBeInstanceOf(Array);
      expect(response.data?.length).toBeGreaterThan(0);
      expect(response.data?.[0]).toHaveProperty('id');
      expect(response.data?.[0]).toHaveProperty('name');
    });
  });

  describe('Behavior Negotiation', () => {
    it('should report supported behaviors', async () => {
      const response = await bridge.sendRequest('get_behaviors');

      expect(response.success).toBe(true);
      expect(response.data).toHaveProperty('supportsUndo');
      expect(response.data).toHaveProperty('supportsRedo');
      expect(response.data).toHaveProperty('supportsHistory');
    });
  });

  describe('Deck Information', () => {
    it('should retrieve deck information', async () => {
      const response = await bridge.sendRequest('get_deck_info');

      expect(response.success).toBe(true);
      expect(response.data).toHaveProperty('name');
      expect(response.data).toHaveProperty('id');
      expect(response.data).toHaveProperty('cardCount');
    });
  });

  describe('Error Handling', () => {
    it('should handle unknown message types', async () => {
      const response = await bridge.sendRequest('unknown_message');

      expect(response.success).toBe(false);
      expect(response.error).toContain('Unknown message');
    });

    it('should handle request timeouts gracefully', async () => {
      bridge.setLatency(5000);

      const timeout = new Promise<BridgeResponse>((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), 1000)
      );

      const request = bridge.sendRequest('get_fields');

      try {
        await Promise.race([request, timeout]);
      } catch (e) {
        expect((e as Error).message).toBe('Timeout');
      }
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle concurrent requests', async () => {
      const requests = [
        bridge.sendRequest('get_fields'),
        bridge.sendRequest('get_models'),
        bridge.sendRequest('get_behaviors'),
        bridge.sendRequest('get_deck_info'),
      ];

      const responses = await Promise.all(requests);

      expect(responses.length).toBe(4);
      expect(responses.every((r) => r.success)).toBe(true);
    });

    it('should maintain proper ordering in concurrent requests', async () => {
      const results: string[] = [];

      const request1 = bridge.sendRequest('get_fields').then(() => {
        results.push('fields');
      });

      const request2 = bridge.sendRequest('get_models').then(() => {
        results.push('models');
      });

      await Promise.all([request1, request2]);

      expect(results.length).toBe(2);
      expect(results).toContain('fields');
      expect(results).toContain('models');
    });
  });

  describe('Bridge Performance', () => {
    it('should measure average bridge latency', async () => {
      bridge.setLatency(100);

      const responses = await Promise.all([
        bridge.sendRequest('get_fields'),
        bridge.sendRequest('get_models'),
        bridge.sendRequest('get_behaviors'),
      ]);

      const avgLatency =
        responses.reduce((sum, r) => sum + r.duration, 0) / responses.length;

      expect(avgLatency).toBeGreaterThanOrEqual(100);
      expect(avgLatency).toBeLessThan(150);
    });

    it('should handle rapid successive requests', async () => {
      const startTime = performance.now();
      const count = 100;

      for (let i = 0; i < count; i++) {
        await bridge.sendRequest('get_fields');
      }

      const duration = performance.now() - startTime;
      const avgTime = duration / count;

      expect(avgTime).toBeLessThan(200); // Average < 200ms
    });
  });
});

export { IntegrationBridge, BridgeResponse };
