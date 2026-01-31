/**
 * i18n-enabled Error Messages Helper
 * 
 * This module provides functions to retrieve translated error messages
 * and validation messages. It works with both vanilla JS and React.
 */

import i18next from './config';

/**
 * Get translated user-friendly message for an error
 */
function getUserFriendlyErrorMessage(ruleId) {
    const t = (key) => i18next?.t(key) || key;

    const messageMap = {
        // HTML Structure
        'html-1': t('errors.html.html-1'),
        'html-2': t('errors.html.html-2'),
        'html-3': t('errors.html.html-3'),
        'html-4': t('errors.html.html-4'),
        'html-5': t('errors.html.html-5'),

        // Anki Fields
        'anki-1': t('errors.anki.anki-1'),
        'anki-2': t('errors.anki.anki-2'),
        'anki-3': t('errors.anki.anki-3'),
        'anki-4': t('errors.anki.anki-4'),
        'anki-5': t('errors.anki.anki-5'),

        // Accessibility
        'a11y-1': t('errors.a11y.a11y-1'),
        'a11y-2': t('errors.a11y.a11y-2'),
        'a11y-3': t('errors.a11y.a11y-3'),
        'a11y-4': t('errors.a11y.a11y-4'),
        'a11y-5': t('errors.a11y.a11y-5'),

        // CSS & Styling
        'css-1': t('errors.css.css-1'),
        'css-2': t('errors.css.css-2'),
        'css-3': t('errors.css.css-3'),
        'css-4': t('errors.css.css-4'),

        // Validation
        'validation-1': t('errors.validation.validation-1'),
        'validation-2': t('errors.validation.validation-2'),
        'validation-3': t('errors.validation.validation-3'),
        'validation-4': t('errors.validation.validation-4'),

        // Performance
        'performance-1': t('errors.performance.performance-1'),
        'performance-2': t('errors.performance.performance-2'),
        'performance-3': t('errors.performance.performance-3'),
        'performance-4': t('errors.performance.performance-4'),

        // Mobile
        'mobile-1': t('errors.mobile.mobile-1'),
        'mobile-2': t('errors.mobile.mobile-2'),
        'mobile-3': t('errors.mobile.mobile-3'),
        'mobile-4': t('errors.mobile.mobile-4'),

        // Security
        'security-1': t('errors.security.security-1'),
        'security-2': t('errors.security.security-2'),
        'security-3': t('errors.security.security-3'),

        // Default fallback
        'default': t('messages.error')
    };

    return messageMap[ruleId] || messageMap['default'];
}

/**
 * Get translated suggestions for an error
 */
function getSuggestionsForError(ruleId) {
    const t = (key) => i18next?.t(key) || key;

    const suggestions = {
        // HTML Structure
        'html-1': [
            t('errors.suggestions.addAltText')
        ],
        'html-2': [
            'Check that all opening tags have corresponding closing tags',
            'Ensure tags are properly nested (no crossing tag boundaries)'
        ],
        'html-3': [
            'Remove empty containers that serve no purpose',
            'If the container is intentional (spacing), add a comment explaining its purpose'
        ],
        'html-4': [
            t('errors.suggestions.useSemanticHtml')
        ],

        // Anki Fields
        'anki-1': [
            'Surround field references with double curly braces: {{FieldName}}',
            'Check that field names match exactly (case-sensitive)'
        ],
        'anki-2': [
            'Remove or fix incorrect field syntax',
            'Field references should be like {{Field}}, not {Field} or {{field}}'
        ],
        'anki-3': [
            'Add conditional statements for optional fields',
            'Use {{#Optional}}content{{/Optional}} syntax'
        ],

        // CSS & Styling
        'css-1': [
            'Check CSS syntax for typos or missing semicolons',
            'Use valid CSS property names and values'
        ],
        'css-2': [
            'Use shorthand CSS properties when applicable',
            'Consolidate related CSS rules to reduce size'
        ],

        // Performance
        'perf-1': [
            'Reduce the number of nested elements',
            'Use CSS classes instead of inline styles',
            'Consider using CSS Grid or Flexbox for layout'
        ],
        'perf-2': [
            'Use relative units (em, rem) instead of absolute pixels',
            'This makes the template more responsive and accessible'
        ],

        // Accessibility
        'a11y-1': [
            t('errors.suggestions.addAltText'),
            'Describe what the image shows, not just "image"'
        ],
        'a11y-2': [
            'Use proper heading hierarchy (h1, h2, h3, etc.)',
            'Don\'t skip heading levels'
        ],
        'a11y-3': [
            'Add descriptive labels to form inputs',
            'Use aria-label if visible label isn\'t appropriate'
        ],

        // Default
        'default': [
            'Review the error message to understand what needs to be fixed',
            'Check the Anki Template Designer documentation for guidance',
            'Run validation again after making changes'
        ]
    };

    return suggestions[ruleId] || suggestions['default'];
}

/**
 * Get translated error context
 */
function getErrorContext(ruleId) {
    const contexts = {
        'anki-1': 'in field reference',
        'anki-2': 'in field syntax',
        'anki-3': 'in optional field',
        'html-1': 'in template structure',
        'html-2': 'in HTML tags',
        'css-1': 'in stylesheet'
    };

    return contexts[ruleId] || '';
}

/**
 * Get translated error severity type
 */
function getErrorSeverityLabel(severity) {
    const t = (key) => i18next?.t(key) || key;

    const types = {
        'error': t('errors.types.error'),
        'warning': t('errors.types.warning'),
        'info': t('errors.types.info'),
        'success': t('errors.types.success'),
        'critical': t('errors.types.critical')
    };

    return types[severity] || severity;
}

/**
 * Get translated validation error message
 */
function getValidationErrorMessage(field, errorType) {
    const t = (key) => i18next?.t(key) || key;

    const messages = {
        // Required fields
        'fieldName.required': t('validation.required.fieldName'),
        'templateName.required': t('validation.required.templateName'),
        'componentName.required': t('validation.required.componentName'),

        // Field name validation
        'fieldName.invalid': t('validation.fieldName.invalid'),
        'fieldName.duplicate': t('validation.fieldName.duplicate'),
        'fieldName.reserved': t('validation.fieldName.reserved'),

        // Template name validation
        'templateName.invalid': t('validation.templateName.invalid'),
        'templateName.duplicate': t('validation.templateName.duplicate'),

        // HTML content validation
        'htmlContent.invalid': t('validation.htmlContent.invalid'),
        'htmlContent.unmatched': t('validation.htmlContent.unmatched'),

        // CSS content validation
        'cssContent.invalid': t('validation.cssContent.invalid'),

        // Field reference validation
        'fieldReference.invalid': t('validation.fieldReference.invalid'),

        // Cloze delete validation
        'clozeDelete.syntax': t('validation.clozeDelete.syntax'),

        // Conditional validation
        'conditional.unclosed': t('validation.conditional.unclosed'),
        'conditional.invalid': t('validation.conditional.invalid'),

        // Generic validation
        'general.required': t('validation.general.required'),
        'general.invalid': t('validation.general.invalid')
    };

    const key = `${field}.${errorType}`;
    return messages[key] || messages['general.invalid'];
}

/**
 * Get translated field validation error with interpolation
 */
function getFieldValidationError(field, errorType, data = {}) {
    const t = (key, opts) => i18next?.t(key, opts) || key;

    const key = `validation.${field}.${errorType}`;
    return t(key, data);
}

// Export for global usage
if (typeof window !== 'undefined') {
    window.i18nErrors = {
        getUserFriendlyErrorMessage,
        getSuggestionsForError,
        getErrorContext,
        getErrorSeverityLabel,
        getValidationErrorMessage,
        getFieldValidationError
    };
}
