/**
 * Export and Format Types
 * Defines export formats, serialization, and data transformation
 */

/**
 * Supported export formats
 */
export type ExportFormat = 'html' | 'json' | 'css' | 'craftjs' | 'grapejs' | 'anki' | 'zip';

/**
 * Export format specification
 */
export interface FormatSpecification {
  format: ExportFormat;
  mimeType: string;
  fileExtension: string;
  description: string;
  supportsStyles: boolean;
  supportsMetadata: boolean;
  compressible: boolean;
  maxFileSize?: number;
}

/**
 * Export configuration
 */
export interface ExportConfig {
  format: ExportFormat;
  includeStyles?: boolean;
  includeMetadata?: boolean;
  minify?: boolean;
  compress?: boolean;
  prettyPrint?: boolean;
  charset?: string;
  lineEndings?: 'lf' | 'crlf';
  indentation?: number;
  customOptions?: Record<string, any>;
}

/**
 * Craftjs template format
 */
export interface CraftjsTemplate {
  id: string;
  name: string;
  description?: string;
  version: string;
  nodes: Record<string, any>;
  ROOT?: {
    type: string;
    props: Record<string, any>;
    children?: string[];
  };
  metadata?: {
    createdAt: string;
    updatedAt: string;
    creator?: string;
    tags?: string[];
  };
}

/**
 * GrapeJS format (legacy support)
 */
export interface GrapejsTemplate {
  id: string;
  name: string;
  pages: Array<{
    id: string;
    name: string;
    component: any;
  }>;
  styles: string;
  assets: Array<{
    type: string;
    src: string;
  }>;
}

/**
 * HTML export format
 */
export interface HtmlTemplate {
  html: string;
  css?: string;
  metadata?: Record<string, any>;
  assets?: Array<{
    type: 'css' | 'js' | 'image';
    content: string;
    url?: string;
  }>;
}

/**
 * JSON export format
 */
export interface JsonTemplate {
  template: {
    id: string;
    name: string;
    description?: string;
    html: string;
    css: string;
    metadata?: Record<string, any>;
  };
  nodes?: Record<string, any>;
  blocks?: Array<{
    id: string;
    type: string;
    props: Record<string, any>;
  }>;
}

/**
 * Anki format
 */
export interface AnkiTemplate {
  name: string;
  qfmt: string; // Front template
  afmt: string; // Back template
  bafmt?: string; // Browser appearance format
  did?: number; // Deck ID
  ord?: number; // Order
  brid?: number; // Browser field ID
}

/**
 * Serialized template data
 */
export interface SerializedTemplate {
  version: number;
  format: ExportFormat;
  compressed: boolean;
  checksum?: string;
  data: string;
  metadata?: {
    exportedAt: string;
    exportedBy?: string;
    sourceVersion?: string;
  };
}

/**
 * Template import options
 */
export interface ImportOptions {
  format: ExportFormat;
  overwrite?: boolean;
  merge?: boolean;
  validateBeforeImport?: boolean;
  autoUpgrade?: boolean;
  customMapping?: Record<string, any>;
}

/**
 * Import result
 */
export interface ImportResult {
  success: boolean;
  templateId?: string;
  templateName?: string;
  warnings?: string[];
  errors?: string[];
  mergedNodes?: number;
  createdNodes?: number;
  updatedNodes?: number;
}

/**
 * Style extraction result
 */
export interface StyleExtractionResult {
  globalStyles: string;
  componentStyles: Record<string, string>;
  variables: Record<string, string>;
  keyframes?: string;
  media?: Array<{
    query: string;
    styles: string;
  }>;
}

/**
 * Node serializer interface
 */
export interface NodeSerializer {
  serialize(node: any): SerializedNode;
  deserialize(data: SerializedNode): any;
}

/**
 * Serialized node data
 */
export interface SerializedNode {
  id: string;
  type: string;
  displayName: string;
  props: Record<string, any>;
  custom?: Record<string, any>;
  parent?: string;
  children?: string[];
  hidden?: boolean;
}

/**
 * Batch export job
 */
export interface BatchExportJob {
  id: string;
  templateIds: string[];
  format: ExportFormat;
  config: ExportConfig;
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  results: ExportResult[];
  error?: string;
  startTime?: number;
  endTime?: number;
}

/**
 * Export result for single template
 */
export interface ExportResult {
  templateId: string;
  templateName: string;
  success: boolean;
  format: ExportFormat;
  data?: string | Buffer;
  filename?: string;
  fileSize?: number;
  mimeType?: string;
  checksum?: string;
  error?: string;
  warnings?: string[];
  timestamp: number;
}

/**
 * Format conversion options
 */
export interface ConversionOptions {
  sourceFormat: ExportFormat;
  targetFormat: ExportFormat;
  preserveIds?: boolean;
  preserveMetadata?: boolean;
  validateAfterConversion?: boolean;
  customTransforms?: Record<string, (data: any) => any>;
}

/**
 * Format converter interface
 */
export interface FormatConverter {
  canConvert(from: ExportFormat, to: ExportFormat): boolean;
  convert(data: any, options: ConversionOptions): any;
}

/**
 * Template compatibility information
 */
export interface CompatibilityInfo {
  format: ExportFormat;
  minAnkiVersion?: string;
  minDesignerVersion?: string;
  ankiDroidCompatible?: boolean;
  requiresPlugins?: string[];
  unsupportedFeatures?: string[];
  warnings?: string[];
}
