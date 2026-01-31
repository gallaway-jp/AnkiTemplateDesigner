/**
 * Central export for all TypeScript type definitions
 * Import from this file to access all types
 */

// Editor domain types
export type {
  AnkiField,
  AnkiBehavior,
  CraftComponent,
  Template,
  TemplateSnapshot,
  BlockDefinition,
  PropertyDefinition,
  Device,
  ExportOptions,
  ExportResult,
  CraftNodeData,
  CraftNodeRules,
  CraftCanvasConfig,
  SelectionState,
  HistoryEntry,
  PropertySchema,
  PropertySchemaField,
  ComponentMetadata,
  NodePath,
  PropertyUpdateEvent,
  LayerTreeItem,
  ZoomState,
  CraftStoreState,
} from './editor';

export type { BlockCategory } from './editor';

// Anki-specific types
export type {
  AnkiConfig,
  CardSide,
  CardStyling,
  CardTemplate,
  PreviewContext,
  ValidationResult,
  ValidationError,
  ValidationWarning,
  DeviceSimulationSettings,
  RenderResult,
} from './anki';

// Python bridge API types
export type {
  BridgeMessage,
  BridgeRequest,
  BridgeResponse,
  BridgeMethod,
  SaveTemplateRequest,
  LoadTemplateRequest,
  ExportTemplateRequest,
  PreviewTemplateRequest,
  ValidateTemplateRequest,
  SaveTemplateResponse,
  LoadTemplateResponse,
  ExportTemplateResponse,
  GetFieldsResponse,
  BridgeError,
  BridgeConfig,
  BridgeListener,
} from './api';

// Validation and schema types
export type {
  ValidatorFn,
  ValidationStatus,
  ValidationRule,
  FieldValidator,
  HTMLValidationRules,
  CSSValidationRules,
  TemplateValidationProfile,
  AnkiFieldType,
  AnkiFieldValidator,
  BlockPropertyValidator,
  ExportFormatValidator,
  DetailedValidationResult,
  ValidationIssue,
  ValidationSuggestion,
} from './validation';

export { VALIDATION_PRESETS, COMMON_VALIDATORS } from './validation';

// Format and export types
export type {
  ExportFormat,
  FormatSpecification,
  ExportConfig,
  CraftjsTemplate,
  GrapejsTemplate,
  HtmlTemplate,
  JsonTemplate,
  AnkiTemplate,
  SerializedTemplate,
  ImportOptions,
  ImportResult,
  StyleExtractionResult,
  NodeSerializer,
  SerializedNode,
  BatchExportJob,
  ExportResult as ExportResultType,
  ConversionOptions,
  FormatConverter,
  CompatibilityInfo,
} from './formats';

// Utility and helper types
export type {
  Result,
  AsyncResult,
  PaginatedList,
  SortConfig,
  FilterConfig,
  QueryConfig,
  KeyboardShortcut,
  ThemeConfig,
  Notification,
  DialogConfig,
  ContextMenuItem,
  AsyncState,
  Dimensions,
  Position,
  Rectangle,
  Spacing,
  ShadowConfig,
  BorderConfig,
  FontConfig,
  ColorScheme,
  Breakpoints,
  ResponsiveValue,
  EventHandler,
  Callback,
  DeepPartial,
  DeepReadonly,
  Omit,
  Extends,
  Literal,
  KeyValuePair,
  LocalizationStrings,
  PerformanceMetric,
  ErrorDetails,
} from './utils';

export type {
  Locale,
} from './utils';

// Phase 1 Architecture Enhancements
export type {
  Notification as EventNotification,
  CraftComponent as EventCraftComponent,
  TemplateEvent,
  AppEvents,
} from './events';
export { TypedEventBus } from './events';


