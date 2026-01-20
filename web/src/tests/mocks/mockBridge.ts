/**
 * Python Bridge Mock
 * Mock implementation for testing without QWebChannel
 */

import { BridgeResponse } from '@types';

export class MockPythonBridge {
  private requestCount = 0;
  private delayMs = 50;

  constructor(delayMs: number = 50) {
    this.delayMs = delayMs;
  }

  async sendMessage(message: string): Promise<string> {
    this.requestCount++;

    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, this.delayMs));

    const request = JSON.parse(message);
    const response = this.generateResponse(request);

    return JSON.stringify(response);
  }

  private generateResponse(request: any): BridgeResponse {
    const { method, requestId } = request;

    return {
      requestId,
      method,
      result: this.getMockResult(method, request.params),
    };
  }

  private getMockResult(method: string, params: any): any {
    switch (method) {
      case 'getAnkiFields':
        return [
          { name: 'Front', description: 'Front of card' },
          { name: 'Back', description: 'Back of card' },
          { name: 'Extra', description: 'Extra information' },
        ];

      case 'getAnkiBehaviors':
        return [
          { name: 'sound', description: 'Play sound' },
          { name: 'hint', description: 'Show hint' },
        ];

      case 'saveTemplate':
        return {
          success: true,
          templateId: params.id || 'template-' + Date.now(),
          timestamp: Date.now(),
        };

      case 'loadTemplate':
        return {
          id: params.templateId,
          name: 'Sample Template',
          html: '<div class="card"><p>{{Front}}</p></div>',
          css: '.card { padding: 20px; }',
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

      case 'previewTemplate':
        return {
          html: `<div>${params.html}</div>`,
          css: params.css,
        };

      default:
        return { success: true };
    }
  }

  getRequestCount(): number {
    return this.requestCount;
  }

  reset(): void {
    this.requestCount = 0;
  }
}
