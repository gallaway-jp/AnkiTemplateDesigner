/**
 * Utility and Helper Types
 * Common types used across the application
 */

/**
 * Generic result type for operations
 */
export type Result<T, E = string> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

/**
 * Async result type
 */
export type AsyncResult<T, E = string> = Promise<Result<T, E>>;

/**
 * Paginated list
 */
export interface PaginatedList<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
  totalPages: number;
}

/**
 * Sorting configuration
 */
export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

/**
 * Filter configuration
 */
export interface FilterConfig {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'nin' | 'contains' | 'startsWith' | 'endsWith';
  value: any;
}

/**
 * Query configuration
 */
export interface QueryConfig<T> {
  filters?: FilterConfig[];
  sorts?: SortConfig[];
  page?: number;
  pageSize?: number;
  search?: string;
}

/**
 * Keyboard shortcut
 */
export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  action: string;
  description?: string;
  category?: string;
}

/**
 * Theme configuration
 */
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  primaryColor?: string;
  secondaryColor?: string;
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
  borderColor?: string;
  customVariables?: Record<string, string>;
}

/**
 * Notification/Toast
 */
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
  dismissible?: boolean;
}

/**
 * Dialog/Modal configuration
 */
export interface DialogConfig {
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'confirm' | 'prompt';
  buttons?: Array<{
    label: string;
    action: 'accept' | 'cancel' | 'custom';
    handler?: (value?: any) => void;
  }>;
  defaultValue?: string;
}

/**
 * Context menu item
 */
export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: string;
  action: () => void;
  enabled?: boolean | (() => boolean);
  separator?: boolean;
  submenu?: ContextMenuItem[];
}

/**
 * Async operation state
 */
export interface AsyncState<T> {
  status: 'idle' | 'loading' | 'success' | 'error';
  data?: T;
  error?: Error | string;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
}

/**
 * Dimension measurements
 */
export interface Dimensions {
  width: number;
  height: number;
}

/**
 * Position coordinates
 */
export interface Position {
  x: number;
  y: number;
}

/**
 * Rectangle (position + dimensions)
 */
export interface Rectangle extends Position, Dimensions {
  top?: number;
  left?: number;
  right?: number;
  bottom?: number;
}

/**
 * Spacing (margin/padding)
 */
export interface Spacing {
  top?: number;
  right?: number;
  bottom?: number;
  left?: number;
}

/**
 * Shadow configuration
 */
export interface ShadowConfig {
  offsetX: number;
  offsetY: number;
  blurRadius: number;
  spreadRadius?: number;
  color: string;
  opacity?: number;
}

/**
 * Border configuration
 */
export interface BorderConfig {
  width: number;
  color: string;
  style: 'solid' | 'dashed' | 'dotted' | 'double';
  radius?: number;
}

/**
 * Font configuration
 */
export interface FontConfig {
  family: string;
  size: number;
  weight: 'normal' | 'bold' | 'lighter' | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900;
  style: 'normal' | 'italic' | 'oblique';
  lineHeight?: number;
  letterSpacing?: number;
  textDecoration?: string;
}

/**
 * Color scheme
 */
export interface ColorScheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  border: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

/**
 * Responsive breakpoints
 */
export interface Breakpoints {
  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;
  xxl?: number;
}

/**
 * Responsive value (can be different per breakpoint)
 */
export type ResponsiveValue<T> = T | Record<string, T>;

/**
 * Event handler type
 */
export type EventHandler<E = Event> = (event: E) => void;

/**
 * Callback function
 */
export type Callback<T = void> = (value?: T) => void;

/**
 * Deep partial type
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Deep readonly type
 */
export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

/**
 * Omit type utility
 */
export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

/**
 * Extends type utility for conditional types
 */
export type Extends<T, U> = T extends U ? true : false;

/**
 * Literal union type
 */
export type Literal<T> = T extends string ? T : T extends number ? T : never;

/**
 * Key value pair
 */
export interface KeyValuePair<K = string, V = any> {
  key: K;
  value: V;
}

/**
 * Locale identifier
 */
export type Locale = 'en' | 'es' | 'fr' | 'de' | 'ja' | 'zh' | string;

/**
 * Localization strings
 */
export interface LocalizationStrings {
  [key: string]: string | LocalizationStrings;
}

/**
 * Performance metric
 */
export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
}

/**
 * Error details for error tracking
 */
export interface ErrorDetails {
  message: string;
  code?: string;
  name?: string;
  stack?: string;
  context?: Record<string, any>;
  timestamp: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}
