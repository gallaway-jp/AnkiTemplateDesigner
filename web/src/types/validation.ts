/**
 * Validation Schema and Rules
 * Comprehensive type definitions for property and data validation
 */

/**
 * Validator function signature
 */
export type ValidatorFn = (value: any) => ValidationStatus;

/**
 * Validation status result
 */
export interface ValidationStatus {
  valid: boolean;
  error?: string;
  warnings?: string[];
  coerced?: any;
}

/**
 * Property validation rules
 */
export interface ValidationRule {
  type: 'required' | 'type' | 'pattern' | 'min' | 'max' | 'minLength' | 'maxLength' | 'custom' | 'enum' | 'unique';
  value?: any;
  message?: string;
  validator?: ValidatorFn;
}

/**
 * Complete validator for a field
 */
export interface FieldValidator {
  name: string;
  rules: ValidationRule[];
  sanitize?: (value: any) => any;
  coerce?: (value: any) => any;
}

/**
 * HTML validation rules
 */
export interface HTMLValidationRules {
  allowedTags?: string[];
  forbiddenTags?: string[];
  allowedAttributes?: Record<string, string[]>;
  allowScripts?: boolean;
  allowStyles?: boolean;
  allowDataAttributes?: boolean;
  maxLength?: number;
}

/**
 * CSS validation rules
 */
export interface CSSValidationRules {
  allowedProperties?: string[];
  forbiddenProperties?: string[];
  allowImports?: boolean;
  allowMediaQueries?: boolean;
  allowAnimations?: boolean;
  allowTransitions?: boolean;
  maxFileSize?: number;
  allowCustomProperties?: boolean;
}

/**
 * Template validation profile
 */
export interface TemplateValidationProfile {
  name: string;
  description?: string;
  htmlRules: HTMLValidationRules;
  cssRules: CSSValidationRules;
  ankiDroidCompatible?: boolean;
  minAnkiVersion?: string;
  customValidators?: Record<string, ValidatorFn>;
}

/**
 * Anki field type
 */
export type AnkiFieldType = 'text' | 'html' | 'media' | 'code' | 'latex';

/**
 * Anki field validator
 */
export interface AnkiFieldValidator {
  fieldName: string;
  fieldType: AnkiFieldType;
  rules: ValidationRule[];
  maxLength?: number;
  encoding?: string;
}

/**
 * Block property validation
 */
export interface BlockPropertyValidator {
  propertyName: string;
  propertyType: string;
  rules: ValidationRule[];
  description?: string;
  examples?: any[];
}

/**
 * Export format validation
 */
export interface ExportFormatValidator {
  format: 'html' | 'json' | 'css' | 'anki';
  rules: ValidationRule[];
  requiredFields?: string[];
  maxFileSize?: number;
  encoding?: string;
}

/**
 * Validation result with detailed information
 */
export interface DetailedValidationResult {
  valid: boolean;
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  suggestions: ValidationSuggestion[];
  performance?: {
    renderTime?: number;
    fileSize?: number;
  };
}

/**
 * Validation issue (error or warning)
 */
export interface ValidationIssue {
  type: 'error' | 'warning';
  code: string;
  message: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  location?: {
    line?: number;
    column?: number;
    offset?: number;
  };
  context?: {
    before?: string;
    current?: string;
    after?: string;
  };
  fix?: string;
  relatedIssues?: string[];
}

/**
 * Validation suggestion for improvement
 */
export interface ValidationSuggestion {
  category: 'performance' | 'accessibility' | 'compatibility' | 'best-practice' | 'security';
  message: string;
  priority: 'low' | 'medium' | 'high';
  autoFixable: boolean;
  fix?: string;
}

/**
 * Presets for common validation scenarios
 */
export const VALIDATION_PRESETS = {
  /**
   * Strict mode - all rules enabled
   */
  strict: {
    allowScripts: false,
    allowImports: false,
    ankiDroidCompatible: true,
    minAnkiVersion: '2.1.0',
  } as TemplateValidationProfile['htmlRules'],

  /**
   * Permissive mode - fewer restrictions
   */
  permissive: {
    allowScripts: true,
    allowImports: true,
    ankiDroidCompatible: false,
  } as TemplateValidationProfile['htmlRules'],

  /**
   * AnkiDroid compatible mode
   */
  ankidroid: {
    allowScripts: false,
    allowImports: false,
    allowDataAttributes: false,
    ankiDroidCompatible: true,
  } as TemplateValidationProfile['htmlRules'],
};

/**
 * Common validators as singletons
 */
export const COMMON_VALIDATORS = {
  /**
   * Email validator
   */
  email: (value: any): ValidationStatus => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const valid = typeof value === 'string' && emailRegex.test(value);
    return {
      valid,
      error: valid ? undefined : 'Invalid email address',
    };
  },

  /**
   * URL validator
   */
  url: (value: any): ValidationStatus => {
    try {
      new URL(value);
      return { valid: true };
    } catch {
      return {
        valid: false,
        error: 'Invalid URL',
      };
    }
  },

  /**
   * Color validator (hex, rgb, hsl, named)
   */
  color: (value: any): ValidationStatus => {
    const colorRegex = /^(#[0-9a-f]{3}|#[0-9a-f]{6}|rgb\(|hsl\()/i;
    const isNamedColor = /^(red|blue|green|yellow|black|white|gray|transparent)$/i.test(value);
    const valid = typeof value === 'string' && (colorRegex.test(value) || isNamedColor);
    return {
      valid,
      error: valid ? undefined : 'Invalid color value',
    };
  },

  /**
   * Integer validator
   */
  integer: (value: any): ValidationStatus => {
    const valid = Number.isInteger(value);
    return {
      valid,
      error: valid ? undefined : 'Must be an integer',
    };
  },

  /**
   * Number validator
   */
  number: (value: any): ValidationStatus => {
    const valid = typeof value === 'number' && !isNaN(value);
    return {
      valid,
      error: valid ? undefined : 'Must be a number',
    };
  },

  /**
   * Non-empty string validator
   */
  nonEmptyString: (value: any): ValidationStatus => {
    const valid = typeof value === 'string' && value.trim().length > 0;
    return {
      valid,
      error: valid ? undefined : 'Must be a non-empty string',
    };
  },

  /**
   * Array validator
   */
  array: (value: any): ValidationStatus => {
    const valid = Array.isArray(value);
    return {
      valid,
      error: valid ? undefined : 'Must be an array',
    };
  },

  /**
   * Object validator
   */
  object: (value: any): ValidationStatus => {
    const valid = typeof value === 'object' && value !== null && !Array.isArray(value);
    return {
      valid,
      error: valid ? undefined : 'Must be an object',
    };
  },
};
