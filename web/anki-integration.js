/**
 * Anki Integration Module
 *
 * Handles browser-side Anki integration including:
 * - Real-time field synchronization
 * - Field validation and type checking
 * - Conditional field rendering
 * - Model change detection
 * - Template validation
 * - Card type detection
 */

class AnkiIntegration {
  constructor() {
    this.currentModel = null;
    this.previousModel = null;
    this.modelCache = new Map();
    this.connected = false;
    this.syncInterval = null;
    this.listeners = new Map();
  }

  /**
   * Initialize Anki integration
   * Sets up event listeners and sync mechanism
   */
  initialize() {
    this.setupEventListeners();
    this.startSync();
    this.dispatchEvent('initialized');
  }

  /**
   * Setup event listeners for model changes
   */
  setupEventListeners() {
    window.addEventListener('ankiModelChanged', (e) => this.onModelChanged(e));
    window.addEventListener('ankiFieldsUpdated', (e) => this.onFieldsUpdated(e));
    window.addEventListener('ankiTemplateChanged', (e) => this.onTemplateChanged(e));
  }

  /**
   * Start real-time sync with Anki
   */
  startSync() {
    // DISABLED: This tries to fetch from an API endpoint that doesn't exist in development
    // The error "Failed to fetch" was being logged repeatedly every 2 seconds
    // Re-enable this when running within Anki with proper backend API
    /*
    this.syncInterval = setInterval(() => {
      this.syncCurrentModel();
    }, 2000); // Sync every 2 seconds
    */
    console.log('[AnkiIntegration] Sync disabled in this environment (no backend API available)');
  }

  /**
   * Stop real-time sync
   */
  stopSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * Sync current model from Anki
   */
  async syncCurrentModel() {
    try {
      const model = await this.fetchCurrentModel();
      if (model) {
        this.setCurrentModel(model);
      }
    } catch (error) {
      console.error('Failed to sync model:', error);
    }
  }

  /**
   * Fetch current model from backend
   */
  async fetchCurrentModel() {
    try {
      const response = await fetch('/api/anki/model/current');
      if (!response.ok) return null;

      const data = await response.json();
      return this.parseModel(data);
    } catch (error) {
      console.error('Error fetching current model:', error);
      return null;
    }
  }

  /**
   * Parse raw model data into AnkiModel object
   */
  parseModel(data) {
    return {
      id: data.id,
      name: data.name,
      fields: (data.fields || []).map(f => this.parseField(f)),
      templates: (data.templates || []).map(t => this.parseTemplate(t)),
      css: data.css || '',
      did: data.did,
      tags: data.tags || [],
    };
  }

  /**
   * Parse field data
   */
  parseField(fieldData) {
    return {
      name: fieldData.name,
      type: fieldData.type || 'text',
      ord: fieldData.ord,
      size: fieldData.size || 20,
      sticky: fieldData.sticky || false,
      rtl: fieldData.rtl || false,
      prefix: fieldData.prefix || '',
      suffix: fieldData.suffix || '',
      options: fieldData.options || [],
      minValue: fieldData.minValue,
      maxValue: fieldData.maxValue,
    };
  }

  /**
   * Parse template data
   */
  parseTemplate(templateData) {
    return {
      name: templateData.name,
      ord: templateData.ord,
      qfmt: templateData.qfmt, // question format
      afmt: templateData.afmt, // answer format
      bafmt: templateData.bafmt || '',
      bqfmt: templateData.bqfmt || '',
    };
  }

  /**
   * Set current model and track previous
   */
  setCurrentModel(model) {
    const changed = this.detectModelChange(this.currentModel, model);

    this.previousModel = this.currentModel;
    this.currentModel = model;
    this.modelCache.set(model.id, model);

    if (changed) {
      this.dispatchEvent('modelChanged', { changes: changed });
    }

    this.dispatchEvent('modelUpdated', { model });
  }

  /**
   * Detect changes between two models
   */
  detectModelChange(oldModel, newModel) {
    if (!oldModel) return null;

    const oldNames = new Set(oldModel.fields.map(f => f.name));
    const newNames = new Set(newModel.fields.map(f => f.name));

    const added = newModel.fields.filter(f => !oldNames.has(f.name));
    const removed = oldModel.fields.filter(f => !newNames.has(f.name));

    if (added.length > 0 || removed.length > 0) {
      return {
        added,
        removed,
        timestamp: new Date().toISOString(),
      };
    }

    return null;
  }

  /**
   * Get current model
   */
  getCurrentModel() {
    return this.currentModel;
  }

  /**
   * Get current model fields
   */
  getCurrentFields() {
    if (!this.currentModel) return [];
    return this.currentModel.fields;
  }

  /**
   * Get field by name
   */
  getFieldByName(name) {
    if (!this.currentModel) return null;
    return this.currentModel.fields.find(f => f.name === name);
  }

  /**
   * Get all field names
   */
  getFieldNames() {
    if (!this.currentModel) return [];
    return this.currentModel.fields.map(f => f.name);
  }

  /**
   * Validate field configuration
   */
  validateField(field) {
    const validTypes = ['text', 'number', 'select', 'email', 'image', 'audio', 'date', 'checkbox'];

    if (!field || !field.name || !field.type) {
      return false;
    }

    if (!validTypes.includes(field.type)) {
      return false;
    }

    if (field.type === 'select' && (!field.options || field.options.length === 0)) {
      return false;
    }

    if (field.type === 'number') {
      if (field.minValue !== undefined && field.maxValue !== undefined) {
        if (field.minValue > field.maxValue) {
          return false;
        }
      }
    }

    return true;
  }

  /**
   * Validate field references in template
   */
  validateFieldReferences(template, fieldNames = null) {
    const fields = fieldNames || this.getFieldNames();
    const pattern = /\{\{[#/^]?(\w+)[^}]*\}\}/g;
    const matches = [...template.matchAll(pattern)].map(m => m[1]);
    const uniqueFields = new Set(matches);

    const errors = [];
    for (const field of uniqueFields) {
      if (!fields.includes(field)) {
        errors.push(`Field '${field}' not found in model`);
      }
    }

    return errors;
  }

  /**
   * Render template with field values
   */
  renderTemplate(template, fieldValues, escapeHtml = true) {
    let result = template;

    // Process conditionals
    result = this.renderConditionals(result, fieldValues);

    // Replace field references
    for (const [fieldName, fieldValue] of Object.entries(fieldValues)) {
      const value = escapeHtml ? this.escapeHtml(String(fieldValue)) : String(fieldValue);
      result = result.replace(new RegExp(`\\{\\{${fieldName}\\}\\}`, 'g'), value);
    }

    return result;
  }

  /**
   * Render conditional blocks in template
   */
  renderConditionals(template, fieldValues) {
    let result = template;
    let maxIterations = 10;
    let iteration = 0;

    while (iteration < maxIterations) {
      // Match innermost conditionals first
      const pattern = /\{\{[#^](\w+)\}\}((?:(?!\{\{[#^]).)*?)\{\{\/\1\}\}/s;
      const match = pattern.exec(result);

      if (!match) break;

      const fullMatch = match[0];
      const fieldName = match[1];
      const content = match[2];
      const isPositive = match[0].startsWith('{{#');

      const fieldValue = fieldValues[fieldName] || '';
      const isTruthy = Boolean(fieldValue);

      let replacement = '';
      if ((isPositive && isTruthy) || (!isPositive && !isTruthy)) {
        replacement = content;

        // Replace nested field references
        for (const [fname, fvalue] of Object.entries(fieldValues)) {
          replacement = replacement.replace(
            new RegExp(`\\{\\{${fname}\\}\\}`, 'g'),
            this.escapeHtml(String(fvalue))
          );
        }
      }

      result = result.substring(0, match.index) + replacement + result.substring(match.index + fullMatch.length);
      iteration++;
    }

    return result;
  }

  /**
   * Extract field names from template
   */
  extractFields(template) {
    const pattern = /\{\{[#/^]?(\w+)[^}]*\}\}/g;
    const matches = [...template.matchAll(pattern)].map(m => m[1]);
    return [...new Set(matches)];
  }

  /**
   * Detect card type from template
   */
  detectCardType(template) {
    const hasHr = template.includes('<hr>');
    const hasFields = this.extractFields(template).length > 0;

    if (!hasFields) {
      return 'unknown';
    }

    return hasHr ? 'back' : 'front';
  }

  /**
   * Scope CSS to specific field
   */
  scopeCssForField(css, fieldName) {
    const lines = css.trim().split('\n');
    const scopedLines = lines.map(line => {
      if (line.includes('{')) {
        const [selector, ...rest] = line.split('{');
        return `.field-${fieldName} ${selector.trim()} {${rest.join('{')}`;
      }
      return line;
    });

    return scopedLines.join('\n');
  }

  /**
   * Apply field-specific styles
   */
  applyFieldStyles(fieldName, css) {
    const scopedCss = this.scopeCssForField(css, fieldName);

    // Create or update style element
    let styleElement = document.getElementById(`field-style-${fieldName}`);
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = `field-style-${fieldName}`;
      document.head.appendChild(styleElement);
    }

    styleElement.textContent = scopedCss;
  }

  /**
   * Get field metadata
   */
  getFieldMetadata(fieldName) {
    const field = this.getFieldByName(fieldName);
    if (!field) return null;

    return {
      name: field.name,
      type: field.type,
      ord: field.ord,
      size: field.size,
      sticky: field.sticky,
      rtl: field.rtl,
      prefix: field.prefix,
      suffix: field.suffix,
      options: field.options,
      constraints: this.getFieldConstraints(field),
      validationRules: this.getValidationRules(field),
    };
  }

  /**
   * Get field constraints
   */
  getFieldConstraints(field) {
    const constraints = {};

    if (field.type === 'number') {
      if (field.minValue !== undefined) {
        constraints.min = field.minValue;
      }
      if (field.maxValue !== undefined) {
        constraints.max = field.maxValue;
      }
    }

    if (field.type === 'select') {
      constraints.options = field.options || [];
    }

    return constraints;
  }

  /**
   * Get validation rules for field
   */
  getValidationRules(field) {
    const rules = [];

    if (field.type === 'email') {
      rules.push('email_format', 'required');
    }

    if (field.type === 'number') {
      rules.push('numeric');
    }

    if (field.sticky) {
      rules.push('sticky');
    }

    return rules;
  }

  /**
   * Export model configuration
   */
  exportModelConfig() {
    if (!this.currentModel) {
      return null;
    }

    return {
      id: this.currentModel.id,
      name: this.currentModel.name,
      fields: this.currentModel.fields,
      templates: this.currentModel.templates,
      css: this.currentModel.css,
      did: this.currentModel.did,
      tags: this.currentModel.tags,
    };
  }

  /**
   * Import model configuration
   */
  importModelConfig(config) {
    const model = this.parseModel(config);
    this.setCurrentModel(model);
    return model;
  }

  /**
   * Listen to Anki events
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  /**
   * Dispatch custom event
   */
  dispatchEvent(eventType, detail = {}) {
    const event = new CustomEvent(`anki:${eventType}`, { detail });
    window.dispatchEvent(event);

    // Call registered listeners
    if (this.listeners.has(eventType)) {
      for (const callback of this.listeners.get(eventType)) {
        callback(detail);
      }
    }
  }

  /**
   * Handle model change event
   */
  onModelChanged(event) {
    console.log('Model changed:', event.detail);
    this.dispatchEvent('modelChangeDetected', event.detail);
  }

  /**
   * Handle fields update event
   */
  onFieldsUpdated(event) {
    console.log('Fields updated:', event.detail);
  }

  /**
   * Handle template change event
   */
  onTemplateChanged(event) {
    console.log('Template changed:', event.detail);
  }

  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  /**
   * Destroy and cleanup
   */
  destroy() {
    this.stopSync();
    this.listeners.clear();
    this.modelCache.clear();
  }
}

// Global instance
let ankiIntegration = null;

/**
 * Get or create AnkiIntegration instance
 */
function getAnkiIntegration() {
  if (!ankiIntegration) {
    ankiIntegration = new AnkiIntegration();
    ankiIntegration.initialize();
  }
  return ankiIntegration;
}

/**
 * Initialize on DOM ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    getAnkiIntegration();
  });
} else {
  getAnkiIntegration();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AnkiIntegration, getAnkiIntegration };
}
