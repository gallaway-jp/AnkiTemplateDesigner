/**
 * Validation Error Suggestions
 * Provides helpful suggestions when validation fails
 */

/**
 * Type union of all valid error codes for compile-time safety
 */
export type ErrorCode =
  | 'INVALID_TEMPLATE_SYNTAX'
  | 'MISSING_REQUIRED_FIELD'
  | 'INVALID_CSS_SYNTAX'
  | 'INVALID_HTML_SYNTAX'
  | 'FIELD_NAME_MISMATCH'
  | 'CIRCULAR_DEPENDENCY'
  | 'INVALID_PYTHON_BRIDGE_REQUEST'
  | 'PYTHON_BRIDGE_TIMEOUT'
  | 'PYTHON_BRIDGE_CONNECTION_FAILED';

export interface ValidationErrorSuggestion {
  code: ErrorCode;
  message: string;
  suggestions: string[];
  examples?: string[];
}

/**
 * Service for providing helpful suggestions for validation errors
 */
export class ValidationErrorSuggester {
  private suggestionMap: Map<string, ValidationErrorSuggestion> = new Map([
    [
      'INVALID_TEMPLATE_SYNTAX',
      {
        code: 'INVALID_TEMPLATE_SYNTAX',
        message: 'Template contains invalid syntax',
        suggestions: [
          'Check for unclosed braces or brackets',
          'Ensure all HTML tags are properly closed',
          'Verify CSS selector syntax is correct',
          'Check for escaped characters that should not be escaped',
        ],
        examples: [
          'Valid: <div>{{content}}</div>',
          'Invalid: <div>{{content</div>',
        ],
      }
    ],
    [
      'MISSING_REQUIRED_FIELD',
      {
        code: 'MISSING_REQUIRED_FIELD',
        message: 'Template is missing a required field',
        suggestions: [
          'Check template specification for required fields',
          'Add missing field with proper syntax',
          'Refer to Anki documentation for field requirements',
        ],
        examples: [
          'Required fields: Front, Back',
          'Add: <div class="front">{{Front}}</div>',
        ],
      }
    ],
    [
      'INVALID_CSS_SYNTAX',
      {
        code: 'INVALID_CSS_SYNTAX',
        message: 'CSS contains syntax errors',
        suggestions: [
          'Check for unclosed braces in CSS rules',
          'Verify property: value format',
          'Ensure commas are used correctly in selectors',
          'Validate CSS property names are spelled correctly',
        ],
        examples: [
          'Valid: .card { font-size: 16px; }',
          'Invalid: .card { font-size 16px }',
        ],
      }
    ],
    [
      'UNDEFINED_VARIABLE',
      {
        code: 'UNDEFINED_VARIABLE',
        message: 'Template references undefined variable',
        suggestions: [
          'Check variable name spelling',
          'Verify variable is defined in the model',
          'Look for typos in field names',
          'Check if variable should be wrapped in conditional',
        ],
        examples: [
          'Valid: {{FieldName}}',
          'Invalid: {{fieldname}} (case-sensitive)',
        ],
      }
    ],
    [
      'CIRCULAR_DEPENDENCY',
      {
        code: 'CIRCULAR_DEPENDENCY',
        message: 'Component has circular dependency',
        suggestions: [
          'Review component imports',
          'Move shared logic to a common module',
          'Use lazy loading for dependent components',
          'Consider splitting components differently',
        ],
        examples: [
          'A imports B, B imports A = circular',
          'Solution: Create module C with shared code',
        ],
      }
    ],
    [
      'INVALID_PYTHON_BRIDGE_REQUEST',
      {
        code: 'INVALID_PYTHON_BRIDGE_REQUEST',
        message: 'Request to Python backend is malformed',
        suggestions: [
          'Verify request type is valid (compile, validate, convert)',
          'Check all required parameters are included',
          'Ensure parameter types match specification',
          'Verify timeout is reasonable (5000-30000 ms)',
        ],
        examples: [
          'Valid: { type: "compile", template: "..." }',
          'Invalid: { method: "compile" } (type not "method")',
        ],
      }
    ],
    [
      'PYTHON_BRIDGE_TIMEOUT',
      {
        code: 'PYTHON_BRIDGE_TIMEOUT',
        message: 'Python backend request timed out',
        suggestions: [
          'Check if Python backend is running',
          'Try increasing timeout value',
          'Verify network connectivity',
          'Check for large templates that may take longer to process',
          'Review Python backend logs for errors',
        ],
        examples: [
          'Increase timeout: { timeout: 15000 }',
          'Check backend: python launch_and_test.py',
        ],
      }
    ],
    [
      'PYTHON_BRIDGE_CONNECTION_FAILED',
      {
        code: 'PYTHON_BRIDGE_CONNECTION_FAILED',
        message: 'Cannot connect to Python backend',
        suggestions: [
          'Ensure Python backend is running on correct port',
          'Check firewall settings',
          'Verify backend address (localhost:5000)',
          'Check browser console for CORS errors',
          'Restart the backend service',
        ],
        examples: [
          'Backend URL: http://localhost:5000',
          'Start backend: python launch_and_test.py',
        ],
      }
    ],
  ]);

  /**
   * Get suggestion for error code with compile-time type safety
   */
  getSuggestion(errorCode: ErrorCode): ValidationErrorSuggestion | null {
    return this.suggestionMap.get(errorCode) || null;
  }

  /**
   * Get suggestion with runtime error code (for dynamic errors)
   */
  getSuggestionRuntime(errorCode: string): ValidationErrorSuggestion | null {
    if (this.isValidErrorCode(errorCode)) {
      return this.suggestionMap.get(errorCode as ErrorCode) || null;
    }
    return null;
  }

  /**
   * Check if error code is valid
   */
  private isValidErrorCode(code: string): code is ErrorCode {
    const validCodes: ErrorCode[] = [
      'INVALID_TEMPLATE_SYNTAX',
      'MISSING_REQUIRED_FIELD',
      'INVALID_CSS_SYNTAX',
      'INVALID_HTML_SYNTAX',
      'FIELD_NAME_MISMATCH',
      'CIRCULAR_DEPENDENCY',
      'INVALID_PYTHON_BRIDGE_REQUEST',
      'PYTHON_BRIDGE_TIMEOUT',
      'PYTHON_BRIDGE_CONNECTION_FAILED',
    ];
    return validCodes.includes(code as ErrorCode);
  }

  /**
   * Get suggestion with custom context
   */
  getSuggestionWithContext(
    errorCode: ErrorCode,
    context: { [key: string]: any }
  ): ValidationErrorSuggestion | null {
    const baseSuggestion = this.getSuggestion(errorCode);
    if (!baseSuggestion) {
      return null;
    }

    // Enhance suggestions based on context
    const enhanced = { ...baseSuggestion };

    if (context.fieldName) {
      enhanced.suggestions.push(`Check if field "${context.fieldName}" exists in your model`);
    }

    if (context.timeout && errorCode === 'PYTHON_BRIDGE_TIMEOUT') {
      enhanced.suggestions.push(`Current timeout is ${context.timeout}ms - consider increasing it`);
    }

    return enhanced;
  }

  /**
   * Format suggestion for display
   */
  formatSuggestion(suggestion: ValidationErrorSuggestion): string {
    let output = `${suggestion.message}\n\nSuggestions:\n`;
    suggestion.suggestions.forEach((s, i) => {
      output += `${i + 1}. ${s}\n`;
    });

    if (suggestion.examples && suggestion.examples.length > 0) {
      output += `\nExamples:\n`;
      suggestion.examples.forEach(ex => {
        output += `• ${ex}\n`;
      });
    }

    return output;
  }

  /**
   * Add custom suggestion with validation
   */
  addSuggestion(suggestion: ValidationErrorSuggestion): void {
    if (!this.isValidErrorCode(suggestion.code)) {
      throw new Error(
        `Invalid error code "${suggestion.code}". Must be one of: ${
          ['INVALID_TEMPLATE_SYNTAX', 'MISSING_REQUIRED_FIELD', 'INVALID_CSS_SYNTAX',
           'INVALID_HTML_SYNTAX', 'FIELD_NAME_MISMATCH', 'CIRCULAR_DEPENDENCY',
           'INVALID_PYTHON_BRIDGE_REQUEST', 'PYTHON_BRIDGE_TIMEOUT',
           'PYTHON_BRIDGE_CONNECTION_FAILED'].join(', ')
        }`
      );
    }
    this.suggestionMap.set(suggestion.code, suggestion);
  }

  /**
   * Get all suggestions
   */
  getAllSuggestions(): ValidationErrorSuggestion[] {
    return Array.from(this.suggestionMap.values());
  }
}

/**
 * Global singleton instance
 */
export const validationErrorSuggester = new ValidationErrorSuggester();
