/**
 * Core Editor Domain Types
 * Represents the logical structure of templates and components
 */

/**
 * Represents an Anki field that can be referenced in templates
 */
export interface AnkiField {
  name: string;
  description?: string;
  required?: boolean;
}

/**
 * Represents an AnkiJSApi behavior available in templates
 */
export interface AnkiBehavior {
  name: string;
  description?: string;
  parameters?: string[];
}

/**
 * Represents an editable component in the Craft.js canvas
 */
export interface CraftComponent {
  id: string;
  type: string;
  displayName: string;
  props: Record<string, any>;
  custom?: Record<string, any>;
  parent?: string;
  children?: string[];
}

/**
 * Represents a full template design
 * Maps to GrapeJS project data format
 */
export interface Template {
  id: string;
  name: string;
  description?: string;
  html: string;
  css: string;
  meta?: {
    version: string;
    createdAt: string;
    updatedAt: string;
    creator?: string;
  };
  craftData?: {
    ROOT?: {
      type: string;
      props: Record<string, any>;
      children?: string[];
    };
    [key: string]: any;
  };
}

/**
 * Represents a snapshot of template state for undo/redo
 */
export interface TemplateSnapshot {
  id: string;
  timestamp: number;
  template: Template;
  description: string;
}

/**
 * Block definition for draggable components in the palette
 */
export interface BlockDefinition {
  id: string;
  label: string;
  category: 'layout' | 'anki' | 'input' | 'button' | 'data' | 'feedback' | 'overlay' | 'animation' | 'accessibility';
  description?: string;
  icon?: string;
  defaultProps?: Record<string, any>;
  craft: {
    displayName: string;
    props?: Record<string, any>;
    defaultProps?: Record<string, any>;
    rules?: {
      canDrag?: () => boolean;
      canDrop?: () => boolean;
      canMoveIn?: () => boolean;
      canMoveOut?: () => boolean;
    };
    related?: {
      settings?: React.ComponentType<any>;
      toolbar?: React.ComponentType<any>;
    };
  };
}

/**
 * Component property definition for the properties panel
 */
export interface PropertyDefinition {
  name: string;
  label: string;
  type: 'text' | 'color' | 'number' | 'select' | 'checkbox' | 'textarea';
  defaultValue?: any;
  options?: Array<{ label: string; value: any }>;
  description?: string;
  required?: boolean;
  validator?: (value: any) => boolean;
}

/**
 * Device configuration for preview panes
 */
export interface Device {
  id: string;
  name: string;
  width: string;
  height?: string;
  icon?: string;
  isDefault?: boolean;
}

/**
 * Export format configuration
 */
export interface ExportOptions {
  format: 'html' | 'json' | 'css';
  includeStyles?: boolean;
  minify?: boolean;
  includeMetadata?: boolean;
}

/**
 * Represents the result of exporting a template
 */
export interface ExportResult {
  success: boolean;
  data: string;
  mimeType: string;
  filename: string;
  error?: string;
}

export type React = typeof import('react');
/**
 * Craft.js specific node types for the designer
 */
export interface CraftNodeData {
  type: string;
  displayName: string;
  props: Record<string, any>;
  custom?: Record<string, any>;
  rules?: CraftNodeRules;
  parent?: string;
  children?: string[];
  hidden?: boolean;
  isCanvas?: boolean;
}

/**
 * Craft.js node rules for behavior
 */
export interface CraftNodeRules {
  canDrag?: boolean | (() => boolean);
  canDrop?: boolean | (() => boolean);
  canMoveIn?: boolean | (() => boolean);
  canMoveOut?: boolean | (() => boolean);
  canDelete?: boolean | (() => boolean);
  canClone?: boolean | (() => boolean);
}

/**
 * Craft.js canvas configuration
 */
export interface CraftCanvasConfig {
  enabled?: boolean;
  displayGrid?: boolean;
  snapToGrid?: boolean;
  gridSize?: number;
  zoomLevel?: number;
  maxZoom?: number;
  minZoom?: number;
  showRulers?: boolean;
  showMargins?: boolean;
}

/**
 * Selection state in the canvas
 */
export interface SelectionState {
  selectedNodeId?: string;
  selectedNodeIds: string[];
  hoveredNodeId?: string;
  isDragging: boolean;
  isResizing: boolean;
}

/**
 * History entry for undo/redo
 */
export interface HistoryEntry {
  id: string;
  action: 'insert' | 'delete' | 'update' | 'move' | 'resize' | 'style';
  timestamp: number;
  nodeId?: string;
  nodeType?: string;
  changes?: Record<string, any>;
  previousState?: any;
  nextState?: any;
  canUndo: boolean;
  canRedo: boolean;
}

/**
 * Validation schema for component properties
 */
export interface PropertySchema {
  [key: string]: PropertySchemaField;
}

/**
 * Individual property schema field
 */
export interface PropertySchemaField {
  type: 'string' | 'number' | 'boolean' | 'color' | 'select' | 'array' | 'object';
  label: string;
  description?: string;
  required?: boolean;
  defaultValue?: any;
  minValue?: number;
  maxValue?: number;
  pattern?: string;
  options?: Array<{ label: string; value: any }>;
  items?: PropertySchema;
  validate?: (value: any) => boolean | string;
}

/**
 * Component metadata for the Craft.js registry
 */
export interface ComponentMetadata {
  id: string;
  name: string;
  category: BlockCategory;
  description?: string;
  icon?: string;
  thumbnail?: string;
  tags?: string[];
  relatedBlocks?: string[];
  propertySchema?: PropertySchema;
  defaultProps?: Record<string, any>;
  craft?: {
    displayName: string;
    props?: PropertySchema;
    defaultProps?: Record<string, any>;
    rules?: CraftNodeRules;
    related?: {
      settings?: React.ComponentType<any>;
      toolbar?: React.ComponentType<any>;
    };
  };
}

/**
 * Block category type
 */
export type BlockCategory = 
  | 'layout' 
  | 'anki' 
  | 'input' 
  | 'button' 
  | 'data' 
  | 'feedback' 
  | 'overlay' 
  | 'animation' 
  | 'accessibility';

/**
 * Node path for deep property access
 */
export type NodePath = (string | number)[];

/**
 * Property update event
 */
export interface PropertyUpdateEvent {
  nodeId: string;
  path: NodePath;
  value: any;
  previousValue?: any;
  timestamp: number;
}

/**
 * Layer tree item for the layers panel
 */
export interface LayerTreeItem {
  id: string;
  name: string;
  type: string;
  expanded: boolean;
  visible: boolean;
  locked: boolean;
  level: number;
  parent?: string;
  children: LayerTreeItem[];
  selected: boolean;
}

/**
 * Zoom state for the canvas
 */
export interface ZoomState {
  level: number;
  minZoom: number;
  maxZoom: number;
  fit: 'width' | 'height' | 'page' | 'custom';
  custom?: {
    x: number;
    y: number;
  };
}

/**
 * Craft.js store state shape
 */
export interface CraftStoreState {
  nodes: Record<string, CraftNodeData>;
  selectedNodeId?: string;
  hoveredNodeId?: string;
  isDragging: boolean;
  canvasConfig: CraftCanvasConfig;
  zoomState: ZoomState;
  layerTree: LayerTreeItem[];
}