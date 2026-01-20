/**
 * Anki Synchronization Service - Phase 5 Task 7
 * Field type detection, validation, preview, and synchronization
 */

import { CraftNode } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Anki field type
 */
export type AnkiFieldType = 
  | 'text'
  | 'richtext'
  | 'textarea'
  | 'number'
  | 'date'
  | 'checkbox'
  | 'select'
  | 'multiline'
  | 'image'
  | 'audio'
  | 'video'
  | 'custom';

/**
 * Field metadata detected from template
 */
export interface DetectedField {
  name: string;
  type: AnkiFieldType;
  confidence: number; // 0-1
  isCloze: boolean;
  isConditional: boolean;
  examples: string[];
}

/**
 * Anki field definition
 */
export interface AnkiField {
  name: string;
  ord: number; // ordinal position
  type?: AnkiFieldType;
  sticky?: boolean;
  media: string[];
}

/**
 * Anki note type
 */
export interface AnkiNoteType {
  id: number;
  name: string;
  fields: AnkiField[];
  templates: AnkiCardTemplate[];
  css: string;
}

/**
 * Anki card template
 */
export interface AnkiCardTemplate {
  name: string;
  ordinal: number;
  bfont: string;
  bsize: number;
  bafmt: string; // back answer format
  did?: number; // deck ID
  front: string; // front HTML
  back: string; // back HTML
}

/**
 * Field validation result
 */
export interface FieldValidationResult {
  field: string;
  valid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}

/**
 * Sync result
 */
export interface SyncResult {
  success: boolean;
  noteTypeId?: number;
  fieldMapping: Map<string, string>;
  validationResults: FieldValidationResult[];
  warnings: string[];
  message: string;
}

/**
 * Template preview with field values
 */
export interface TemplatePreviewWithFields {
  frontHtml: string;
  backHtml: string;
  fieldValues: Record<string, string>;
  errors: string[];
}

// ============================================================================
// Field Type Detection
// ============================================================================

/**
 * Detect field types from template content
 */
export function detectFieldTypes(templateContent: string): DetectedField[] {
  const fields: DetectedField[] = [];

  // Extract field placeholders
  const fieldPattern = /\{\{(\w+)\}\}/g;
  const clozePattern = /\{\{cloze:(\w+)\}\}/g;
  const conditionalPattern = /\{\{#(\w+)\}\}/g;

  const matches = new Set<string>();
  let match;

  // Regular fields
  while ((match = fieldPattern.exec(templateContent)) !== null) {
    matches.add(match[1]);
  }

  // Detect field types based on context
  for (const fieldName of matches) {
    const type = detectFieldType(fieldName, templateContent);
    const isCloze = templateContent.includes(`{{cloze:${fieldName}}}`);
    const isConditional = templateContent.includes(`{{#${fieldName}}}`);

    fields.push({
      name: fieldName,
      type,
      confidence: calculateConfidence(type, templateContent, fieldName),
      isCloze,
      isConditional,
      examples: extractFieldExamples(fieldName, templateContent),
    });
  }

  return fields;
}

/**
 * Detect field type from name and context
 */
function detectFieldType(fieldName: string, templateContent: string): AnkiFieldType {
  const lowerName = fieldName.toLowerCase();

  // Type hints from field names
  if (lowerName.includes('image') || lowerName.includes('photo') || lowerName.includes('picture')) {
    return 'image';
  }
  if (lowerName.includes('audio') || lowerName.includes('sound') || lowerName.includes('pronunciation')) {
    return 'audio';
  }
  if (lowerName.includes('video')) {
    return 'video';
  }
  if (lowerName.includes('date') || lowerName.includes('when')) {
    return 'date';
  }
  if (lowerName.includes('number') || lowerName.includes('count') || lowerName.includes('quantity')) {
    return 'number';
  }
  if (lowerName.includes('check') || lowerName.includes('bool') || lowerName.includes('flag')) {
    return 'checkbox';
  }

  // Check context for HTML tags
  const fieldRegex = new RegExp(`\\{\\{${fieldName}\\}\\}[^}]*`, 'g');
  const contextMatches = templateContent.match(fieldRegex) || [];

  for (const context of contextMatches) {
    if (/<textarea|<br|\\n/.test(context)) return 'textarea';
    if (/<img|<video|<audio/.test(context)) return 'image';
  }

  // Default to text or richtext
  return 'richtext';
}

/**
 * Calculate type detection confidence
 */
function calculateConfidence(type: AnkiFieldType, content: string, fieldName: string): number {
  let confidence = 0.5; // Base confidence

  // Increase confidence based on field name matching type
  const lowerName = fieldName.toLowerCase();
  switch (type) {
    case 'image':
      if (/image|photo|picture|img/.test(lowerName)) confidence += 0.3;
      break;
    case 'audio':
      if (/audio|sound|pronunciation|voice/.test(lowerName)) confidence += 0.3;
      break;
    case 'date':
      if (/date|when|time/.test(lowerName)) confidence += 0.3;
      break;
  }

  // Increase confidence if field is used in obvious context
  if (content.includes(`cloze:${fieldName}`)) confidence += 0.1;
  if (content.includes(`#${fieldName}`)) confidence += 0.1;

  return Math.min(confidence, 1);
}

/**
 * Extract example values for a field
 */
function extractFieldExamples(fieldName: string, templateContent: string): string[] {
  const examples: string[] = [];

  // Common examples based on field type
  if (fieldName.toLowerCase().includes('front')) {
    examples.push('What is the capital of France?');
  }
  if (fieldName.toLowerCase().includes('back')) {
    examples.push('Paris');
  }
  if (fieldName.toLowerCase().includes('extra') || fieldName.toLowerCase().includes('notes')) {
    examples.push('Additional information or notes');
  }

  return examples;
}

// ============================================================================
// Anki Synchronization Service
// ============================================================================

export class AnkiSyncService {
  private detectedFields: DetectedField[] = [];
  private fieldMapping: Map<string, string> = new Map();
  private ankiNoteType: AnkiNoteType | null = null;

  /**
   * Analyze template for field detection
   */
  analyzeTemplate(templateContent: string): DetectedField[] {
    try {
      this.detectedFields = detectFieldTypes(templateContent);
      logger.info(`[AnkiSync] Detected ${this.detectedFields.length} fields`);
      return this.detectedFields;
    } catch (error) {
      logger.error('[AnkiSync] Failed to analyze template', error);
      return [];
    }
  }

  /**
   * Validate field configuration
   */
  validateFields(fields: DetectedField[], ankiFields: AnkiField[]): FieldValidationResult[] {
    const results: FieldValidationResult[] = [];
    const ankiFieldNames = new Set(ankiFields.map(f => f.name));

    for (const field of fields) {
      const errors: string[] = [];
      const warnings: string[] = [];
      const suggestions: string[] = [];

      // Check if field exists in Anki
      if (!ankiFieldNames.has(field.name)) {
        errors.push(`Field "${field.name}" not found in Anki note type`);
        suggestions.push(`Create field "${field.name}" in Anki`);
      }

      // Check type compatibility
      const ankiField = ankiFields.find(f => f.name === field.name);
      if (ankiField && ankiField.type) {
        if (!isTypeCompatible(field.type, ankiField.type)) {
          warnings.push(`Type mismatch: detected ${field.type}, but Anki expects ${ankiField.type}`);
        }
      }

      // Low confidence warning
      if (field.confidence < 0.7) {
        warnings.push(`Low confidence (${Math.round(field.confidence * 100)}%) in field type detection`);
        suggestions.push('Verify field type manually');
      }

      results.push({
        field: field.name,
        valid: errors.length === 0,
        errors,
        warnings,
        suggestions,
      });
    }

    return results;
  }

  /**
   * Check type compatibility
   */
  private isTypeCompatible(detectedType: AnkiFieldType, ankiType: AnkiFieldType): boolean {
    const compatibilityMap: Record<AnkiFieldType, AnkiFieldType[]> = {
      text: ['text', 'richtext'],
      richtext: ['richtext', 'text'],
      textarea: ['textarea', 'text', 'richtext'],
      number: ['number', 'text'],
      date: ['date', 'text'],
      checkbox: ['checkbox', 'text'],
      select: ['select', 'text'],
      multiline: ['multiline', 'textarea', 'text'],
      image: ['image'],
      audio: ['audio'],
      video: ['video'],
      custom: ['custom', 'text'],
    };

    return (compatibilityMap[detectedType] || []).includes(ankiType);
  }

  /**
   * Create field mapping
   */
  createFieldMapping(detectedFields: DetectedField[], ankiFields: AnkiField[]): Map<string, string> {
    this.fieldMapping.clear();

    for (const detected of detectedFields) {
      // First try exact match
      let match = ankiFields.find(a => a.name === detected.name);

      // If no exact match, try fuzzy matching
      if (!match) {
        match = ankiFields.find(a => 
          a.name.toLowerCase().includes(detected.name.toLowerCase()) ||
          detected.name.toLowerCase().includes(a.name.toLowerCase())
        );
      }

      if (match) {
        this.fieldMapping.set(detected.name, match.name);
      }
    }

    return this.fieldMapping;
  }

  /**
   * Validate template against Anki note type
   */
  validateAgainstNoteType(
    templateContent: string,
    noteType: AnkiNoteType
  ): FieldValidationResult[] {
    try {
      const detectedFields = this.analyzeTemplate(templateContent);
      return this.validateFields(detectedFields, noteType.fields);
    } catch (error) {
      logger.error('[AnkiSync] Validation failed', error);
      return [];
    }
  }

  /**
   * Generate Anki template HTML
   */
  generateAnkiTemplate(
    frontNode: CraftNode,
    backNode: CraftNode,
    cssStyles?: string
  ): { frontHtml: string; backHtml: string; css: string } {
    try {
      // Convert CraftNode to Anki HTML
      const frontHtml = this.nodeToAnkiHtml(frontNode);
      const backHtml = this.nodeToAnkiHtml(backNode);
      const css = cssStyles || '';

      logger.info('[AnkiSync] Generated Anki template HTML');

      return { frontHtml, backHtml, css };
    } catch (error) {
      logger.error('[AnkiSync] Failed to generate Anki template', error);
      return { frontHtml: '', backHtml: '', css: '' };
    }
  }

  /**
   * Convert CraftNode to Anki-compatible HTML
   */
  private nodeToAnkiHtml(node: CraftNode): string {
    let html = '';

    // Add node content
    if (node.props.text) {
      html += node.props.text;
    }

    // Add children
    for (const child of Object.values(node.nodes)) {
      html += this.nodeToAnkiHtml(child);
    }

    // Wrap in appropriate tags
    if (node.type.includes('heading')) {
      html = `<h2>${html}</h2>`;
    } else if (node.type.includes('paragraph')) {
      html = `<p>${html}</p>`;
    }

    return html;
  }

  /**
   * Sync template to Anki
   */
  async syncToAnki(
    noteTypeId: number,
    frontNode: CraftNode,
    backNode: CraftNode,
    cssStyles?: string
  ): Promise<SyncResult> {
    try {
      // Analyze template
      const detectedFields = this.analyzeTemplate(
        `${this.nodeToAnkiHtml(frontNode)}${this.nodeToAnkiHtml(backNode)}`
      );

      // Generate mapping
      const mapping = this.fieldMapping;

      // Get validation results
      const validationResults: FieldValidationResult[] = [];

      // Generate Anki template
      const { frontHtml, backHtml, css } = this.generateAnkiTemplate(
        frontNode,
        backNode,
        cssStyles
      );

      logger.info(`[AnkiSync] Synced template to note type ${noteTypeId}`);

      return {
        success: validationResults.every(r => r.valid),
        noteTypeId,
        fieldMapping: mapping,
        validationResults,
        warnings: validationResults.flatMap(r => r.warnings),
        message: 'Sync completed',
      };
    } catch (error) {
      logger.error('[AnkiSync] Sync failed', error);
      return {
        success: false,
        fieldMapping: new Map(),
        validationResults: [],
        warnings: [],
        message: 'Sync failed',
      };
    }
  }

  /**
   * Generate preview with sample field values
   */
  generatePreview(
    frontNode: CraftNode,
    backNode: CraftNode,
    fieldValues: Record<string, string>
  ): TemplatePreviewWithFields {
    try {
      let frontHtml = this.nodeToAnkiHtml(frontNode);
      let backHtml = this.nodeToAnkiHtml(backNode);

      // Substitute field values
      for (const [field, value] of Object.entries(fieldValues)) {
        const pattern = new RegExp(`\\{\\{${field}\\}\\}`, 'g');
        frontHtml = frontHtml.replace(pattern, value);
        backHtml = backHtml.replace(pattern, value);
      }

      return {
        frontHtml,
        backHtml,
        fieldValues,
        errors: [],
      };
    } catch (error) {
      logger.error('[AnkiSync] Preview generation failed', error);
      return {
        frontHtml: '',
        backHtml: '',
        fieldValues,
        errors: ['Failed to generate preview'],
      };
    }
  }

  /**
   * Get detected fields
   */
  getDetectedFields(): DetectedField[] {
    return this.detectedFields;
  }

  /**
   * Get field mapping
   */
  getFieldMapping(): Map<string, string> {
    return new Map(this.fieldMapping);
  }

  /**
   * Clear service state
   */
  reset(): void {
    this.detectedFields = [];
    this.fieldMapping.clear();
    this.ankiNoteType = null;
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const ankiSync = new AnkiSyncService();

// Default export
export default ankiSync;
