/**
 * Anki-Specific Domain Types
 * Types related to Anki integration and card generation
 */

/**
 * Represents the state of Anki configuration
 */
export interface AnkiConfig {
  ankiVersion: string;
  notetypeId: number;
  notetypeName: string;
  isDroidCompatible: boolean;
}

/**
 * Represents a card side (front/back)
 */
export type CardSide = 'front' | 'back';

/**
 * Represents the styling section of a card template
 */
export interface CardStyling {
  css: string;
  fontSize?: number;
  fontFamily?: string;
  textColor?: string;
  backgroundColor?: string;
}

/**
 * Represents a complete card template (front + back)
 */
export interface CardTemplate {
  name: string;
  front: string;
  back: string;
  styling: CardStyling;
}

/**
 * Preview context for rendering cards
 */
export interface PreviewContext {
  fields: Record<string, string>;
  notetype: string;
  side: CardSide;
  isAnkiDroid?: boolean;
  deviceWidth?: number;
}

/**
 * Result of template validation
 */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

/**
 * Single validation error
 */
export interface ValidationError {
  type: 'syntax' | 'compatibility' | 'field-missing' | 'invalid-tag';
  message: string;
  lineNumber?: number;
  context?: string;
}

/**
 * Single validation warning
 */
export interface ValidationWarning {
  type: 'deprecated' | 'performance' | 'compatibility' | 'best-practice';
  message: string;
  suggestion?: string;
}

/**
 * Settings for device/platform simulation
 */
export interface DeviceSimulationSettings {
  isAnkiDroid: boolean;
  deviceWidth?: number;
  pixelRatio?: number;
  fontSize?: number;
  lineHeight?: number;
}

/**
 * HTML rendering result from template
 */
export interface RenderResult {
  html: string;
  css: string;
  isValid: boolean;
  errors?: string[];
}
