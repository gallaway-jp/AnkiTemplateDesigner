/**
 * Python Bridge Communication Types
 * Defines message formats for Python ↔ JavaScript communication
 */

/**
 * Base bridge message structure
 */
export interface BridgeMessage {
  method: string;
  requestId?: string;
  params?: Record<string, any>;
  result?: any;
  error?: string;
}

/**
 * Request sent from JavaScript to Python
 */
export interface BridgeRequest extends BridgeMessage {
  method: string;
  requestId: string;
  params: Record<string, any>;
}

/**
 * Response returned from Python to JavaScript
 */
export interface BridgeResponse extends BridgeMessage {
  requestId: string;
  result?: any;
  error?: string;
}

/**
 * Available bridge methods
 */
export type BridgeMethod = 
  | 'saveTemplate'
  | 'loadTemplate'
  | 'exportTemplate'
  | 'previewTemplate'
  | 'getAnkiFields'
  | 'getAnkiBehaviors'
  | 'getAnkiConfig'
  | 'validateTemplate'
  | 'importTemplate'
  | 'log'
  | 'showError';

/**
 * Specialized request types for common operations
 */

export interface SaveTemplateRequest extends BridgeRequest {
  method: 'saveTemplate';
  params: {
    id: string;
    name: string;
    html: string;
    css: string;
    metadata?: Record<string, any>;
  };
}

export interface LoadTemplateRequest extends BridgeRequest {
  method: 'loadTemplate';
  params: {
    templateId: string;
  };
}

export interface ExportTemplateRequest extends BridgeRequest {
  method: 'exportTemplate';
  params: {
    id: string;
    format: 'html' | 'json';
    minify?: boolean;
  };
}

export interface PreviewTemplateRequest extends BridgeRequest {
  method: 'previewTemplate';
  params: {
    html: string;
    css: string;
    fields: Record<string, string>;
    side: 'front' | 'back';
  };
}

export interface ValidateTemplateRequest extends BridgeRequest {
  method: 'validateTemplate';
  params: {
    html: string;
    css: string;
  };
}

/**
 * Specialized response types
 */

export interface SaveTemplateResponse extends BridgeResponse {
  result: {
    success: boolean;
    templateId: string;
    timestamp: number;
  };
}

export interface LoadTemplateResponse extends BridgeResponse {
  result: {
    id: string;
    name: string;
    html: string;
    css: string;
    metadata?: Record<string, any>;
  };
}

export interface ExportTemplateResponse extends BridgeResponse {
  result: {
    data: string;
    format: string;
    mimeType: string;
  };
}

export interface GetFieldsResponse extends BridgeResponse {
  result: Array<{
    name: string;
    ordinal: number;
  }>;
}

/**
 * Bridge error details
 */
export interface BridgeError {
  code: string;
  message: string;
  details?: any;
  stack?: string;
}

/**
 * Bridge configuration
 */
export interface BridgeConfig {
  timeout: number;
  retries: number;
  debug: boolean;
}

/**
 * Listener callback type
 */
export type BridgeListener = (data: any) => void;
