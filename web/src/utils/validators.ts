/**
 * Validators
 * Data validation utilities
 */

import { Template, AnkiField, CraftComponent } from '@/types';

/**
 * Validate template structure
 */
export function validateTemplate(template: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!template) {
    errors.push('Template is null or undefined');
    return { isValid: false, errors };
  }

  if (!template.name) {
    errors.push('Template missing name');
  }

  if (typeof template.html !== 'string') {
    errors.push('Template html must be string');
  }

  if (typeof template.css !== 'string') {
    errors.push('Template css must be string');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate HTML string
 */
export function validateHtml(html: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!html || typeof html !== 'string') {
    errors.push('HTML must be a non-empty string');
  }

  // Check for common issues
  const unclosedTags = html.match(/<[^>]+(?!>)/g);
  if (unclosedTags) {
    errors.push(`Found unclosed HTML tags: ${unclosedTags.join(', ')}`);
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate CSS string
 */
export function validateCss(css: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (typeof css !== 'string') {
    errors.push('CSS must be a string');
  }

  // Very basic validation
  const unclosedBraces = (css.match(/{/g) || []).length !== (css.match(/}/g) || []).length;
  if (unclosedBraces) {
    errors.push('Unbalanced CSS braces');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate Anki field
 */
export function validateField(field: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!field) {
    errors.push('Field is null or undefined');
    return { isValid: false, errors };
  }

  if (!field.name || typeof field.name !== 'string') {
    errors.push('Field name must be a non-empty string');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate component
 */
export function validateComponent(component: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!component) {
    errors.push('Component is null or undefined');
    return { isValid: false, errors };
  }

  if (!component.id || typeof component.id !== 'string') {
    errors.push('Component id must be a non-empty string');
  }

  if (!component.type || typeof component.type !== 'string') {
    errors.push('Component type must be a non-empty string');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate email
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate JSON string
 */
export function validateJson(jsonString: string): { isValid: boolean; error?: string } {
  try {
    JSON.parse(jsonString);
    return { isValid: true };
  } catch (error: any) {
    return { isValid: false, error: error.message };
  }
}
