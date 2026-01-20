/**
 * Templates Library Manager - Phase 5 Task 5
 * Save, load, manage, and categorize reusable templates
 */

import { CraftNode } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Template category for organization
 */
export type TemplateCategory = 
  | 'basic'
  | 'flashcard'
  | 'vocabulary'
  | 'study-guide'
  | 'quiz'
  | 'reference'
  | 'custom'
  | 'imported';

/**
 * Template metadata
 */
export interface TemplateMetadata {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  created: number; // timestamp
  modified: number; // timestamp
  version: string;
  tags: string[];
  author?: string;
  isPublic: boolean;
  usageCount: number;
  rating: number; // 0-5
  downloads: number;
}

/**
 * Complete template with data and metadata
 */
export interface Template {
  metadata: TemplateMetadata;
  frontNode: CraftNode;
  backNode: CraftNode;
  styleNode?: CraftNode;
  previewData?: {
    fieldValues: Record<string, string>;
    sampleSize: number;
  };
}

/**
 * Template preview for library display
 */
export interface TemplatePreview {
  metadata: TemplateMetadata;
  frontPreviewHtml: string;
  backPreviewHtml: string;
  thumbnail?: string; // Base64 encoded
}

/**
 * Template library statistics
 */
export interface LibraryStats {
  totalTemplates: number;
  byCategory: Record<TemplateCategory, number>;
  mostUsed: TemplateMetadata[];
  topRated: TemplateMetadata[];
  recentlyModified: TemplateMetadata[];
}

/**
 * Template search result
 */
export interface TemplateSearchResult {
  templates: TemplatePreview[];
  total: number;
  pageSize: number;
  page: number;
}

/**
 * Template export format
 */
export interface TemplateExportFormat {
  version: string;
  exportDate: number;
  templates: Template[];
  metadata: {
    exporterVersion: string;
    templateCount: number;
  };
}

/**
 * Template import result
 */
export interface TemplateImportResult {
  success: boolean;
  imported: string[]; // template IDs
  skipped: string[]; // template IDs that couldn't be imported
  errors: Array<{ templateName: string; error: string }>;
  message: string;
}

// ============================================================================
// Template Library Manager
// ============================================================================

export class TemplateLibraryManager {
  private templates: Map<string, Template> = new Map();
  private categories: Map<TemplateCategory, string[]> = new Map();
  private tags: Map<string, string[]> = new Map();
  private storageKey = 'anki-template-library';
  private readonly maxTemplates = 1000;

  /**
   * Initialize library from storage
   */
  initialize(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const data = JSON.parse(stored);
        this.loadFromExportFormat(data);
        logger.info(`[TemplateLibrary] Loaded ${this.templates.size} templates from storage`);
      } else {
        // Initialize with empty categories
        this.initializeCategories();
        logger.info('[TemplateLibrary] Initialized empty library');
      }
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to initialize from storage', error);
      this.initializeCategories();
    }
  }

  /**
   * Initialize empty categories
   */
  private initializeCategories(): void {
    const categories: TemplateCategory[] = [
      'basic',
      'flashcard',
      'vocabulary',
      'study-guide',
      'quiz',
      'reference',
      'custom',
      'imported',
    ];

    for (const category of categories) {
      this.categories.set(category, []);
    }
  }

  /**
   * Save template to library
   */
  saveTemplate(template: Template): { success: boolean; message: string; templateId: string } {
    try {
      if (this.templates.size >= this.maxTemplates) {
        return {
          success: false,
          message: `Library limit reached (${this.maxTemplates} templates)`,
          templateId: '',
        };
      }

      const templateId = template.metadata.id;

      // Check if updating existing
      const isUpdate = this.templates.has(templateId);

      // Update metadata timestamps
      template.metadata.modified = Date.now();
      if (!isUpdate) {
        template.metadata.created = Date.now();
      }

      // Store template
      this.templates.set(templateId, template);

      // Update category index
      const category = template.metadata.category;
      if (!this.categories.has(category)) {
        this.categories.set(category, []);
      }
      const categoryTemplates = this.categories.get(category)!;
      if (!categoryTemplates.includes(templateId)) {
        categoryTemplates.push(templateId);
      }

      // Update tags index
      for (const tag of template.metadata.tags) {
        if (!this.tags.has(tag)) {
          this.tags.set(tag, []);
        }
        const tagTemplates = this.tags.get(tag)!;
        if (!tagTemplates.includes(templateId)) {
          tagTemplates.push(templateId);
        }
      }

      // Persist to storage
      this.persistToStorage();

      const action = isUpdate ? 'Updated' : 'Saved';
      logger.info(`[TemplateLibrary] ${action} template: ${template.metadata.name}`);

      return {
        success: true,
        message: `${action} template: ${template.metadata.name}`,
        templateId,
      };
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to save template', error);
      return {
        success: false,
        message: 'Failed to save template',
        templateId: '',
      };
    }
  }

  /**
   * Load template by ID
   */
  getTemplate(templateId: string): Template | null {
    return this.templates.get(templateId) ?? null;
  }

  /**
   * Get all templates in category
   */
  getTemplatesByCategory(category: TemplateCategory): Template[] {
    const templateIds = this.categories.get(category) ?? [];
    return templateIds
      .map(id => this.templates.get(id))
      .filter((t): t is Template => t !== undefined);
  }

  /**
   * Get templates by tag
   */
  getTemplatesByTag(tag: string): Template[] {
    const templateIds = this.tags.get(tag) ?? [];
    return templateIds
      .map(id => this.templates.get(id))
      .filter((t): t is Template => t !== undefined);
  }

  /**
   * Search templates
   */
  searchTemplates(
    query: string,
    filters?: {
      category?: TemplateCategory;
      tags?: string[];
      minRating?: number;
      sortBy?: 'recent' | 'popular' | 'rating' | 'name';
    }
  ): TemplateSearchResult {
    let results = Array.from(this.templates.values());

    // Text search
    if (query) {
      const lowerQuery = query.toLowerCase();
      results = results.filter(
        t =>
          t.metadata.name.toLowerCase().includes(lowerQuery) ||
          t.metadata.description.toLowerCase().includes(lowerQuery) ||
          t.metadata.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
      );
    }

    // Category filter
    if (filters?.category) {
      results = results.filter(t => t.metadata.category === filters.category);
    }

    // Tag filters
    if (filters?.tags && filters.tags.length > 0) {
      results = results.filter(t =>
        filters.tags!.every(tag => t.metadata.tags.includes(tag))
      );
    }

    // Rating filter
    if (filters?.minRating) {
      results = results.filter(t => t.metadata.rating >= filters.minRating!);
    }

    // Sorting
    if (filters?.sortBy) {
      switch (filters.sortBy) {
        case 'recent':
          results.sort((a, b) => b.metadata.modified - a.metadata.modified);
          break;
        case 'popular':
          results.sort((a, b) => b.metadata.usageCount - a.metadata.usageCount);
          break;
        case 'rating':
          results.sort((a, b) => b.metadata.rating - a.metadata.rating);
          break;
        case 'name':
          results.sort((a, b) => a.metadata.name.localeCompare(b.metadata.name));
          break;
      }
    }

    return {
      templates: results.map(t => this.createPreview(t)),
      total: results.length,
      pageSize: results.length,
      page: 1,
    };
  }

  /**
   * Create preview from template
   */
  private createPreview(template: Template): TemplatePreview {
    return {
      metadata: template.metadata,
      frontPreviewHtml: '', // Would be generated by previewRenderer
      backPreviewHtml: '', // Would be generated by previewRenderer
      thumbnail: undefined,
    };
  }

  /**
   * Duplicate template
   */
  duplicateTemplate(templateId: string): { success: boolean; newTemplate?: Template; message: string } {
    try {
      const original = this.getTemplate(templateId);
      if (!original) {
        return {
          success: false,
          message: 'Template not found',
        };
      }

      const newId = `${original.metadata.id}-copy-${Date.now()}`;
      const newTemplate: Template = {
        metadata: {
          ...original.metadata,
          id: newId,
          name: `${original.metadata.name} (Copy)`,
          created: Date.now(),
          modified: Date.now(),
          usageCount: 0,
        },
        frontNode: this.deepCloneNode(original.frontNode),
        backNode: this.deepCloneNode(original.backNode),
        styleNode: original.styleNode ? this.deepCloneNode(original.styleNode) : undefined,
      };

      this.saveTemplate(newTemplate);

      logger.info(`[TemplateLibrary] Duplicated template: ${original.metadata.name}`);

      return {
        success: true,
        newTemplate,
        message: `Duplicated: ${original.metadata.name}`,
      };
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to duplicate template', error);
      return {
        success: false,
        message: 'Failed to duplicate template',
      };
    }
  }

  /**
   * Deep clone a node
   */
  private deepCloneNode(node: CraftNode): CraftNode {
    return {
      ...node,
      nodes: Object.fromEntries(
        Object.entries(node.nodes).map(([key, child]) => [key, this.deepCloneNode(child)])
      ),
    };
  }

  /**
   * Delete template
   */
  deleteTemplate(templateId: string): { success: boolean; message: string } {
    try {
      const template = this.templates.get(templateId);
      if (!template) {
        return { success: false, message: 'Template not found' };
      }

      // Remove from main map
      this.templates.delete(templateId);

      // Remove from category index
      const category = template.metadata.category;
      const categoryTemplates = this.categories.get(category);
      if (categoryTemplates) {
        const index = categoryTemplates.indexOf(templateId);
        if (index > -1) {
          categoryTemplates.splice(index, 1);
        }
      }

      // Remove from tag indexes
      for (const tag of template.metadata.tags) {
        const tagTemplates = this.tags.get(tag);
        if (tagTemplates) {
          const index = tagTemplates.indexOf(templateId);
          if (index > -1) {
            tagTemplates.splice(index, 1);
          }
        }
      }

      this.persistToStorage();

      logger.info(`[TemplateLibrary] Deleted template: ${template.metadata.name}`);

      return {
        success: true,
        message: `Deleted: ${template.metadata.name}`,
      };
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to delete template', error);
      return {
        success: false,
        message: 'Failed to delete template',
      };
    }
  }

  /**
   * Update template metadata
   */
  updateMetadata(templateId: string, updates: Partial<TemplateMetadata>): { success: boolean; message: string } {
    try {
      const template = this.templates.get(templateId);
      if (!template) {
        return { success: false, message: 'Template not found' };
      }

      // Prevent changing ID
      const { id, created, ...safeupdates } = updates;

      template.metadata = {
        ...template.metadata,
        ...safeupdates,
        modified: Date.now(),
      };

      this.persistToStorage();

      logger.info(`[TemplateLibrary] Updated template metadata: ${template.metadata.name}`);

      return {
        success: true,
        message: 'Template updated',
      };
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to update metadata', error);
      return {
        success: false,
        message: 'Failed to update metadata',
      };
    }
  }

  /**
   * Get library statistics
   */
  getStatistics(): LibraryStats {
    const byCategory: Record<TemplateCategory, number> = {
      basic: 0,
      flashcard: 0,
      vocabulary: 0,
      'study-guide': 0,
      quiz: 0,
      reference: 0,
      custom: 0,
      imported: 0,
    };

    for (const [category, ids] of this.categories.entries()) {
      byCategory[category] = ids.length;
    }

    const all = Array.from(this.templates.values());
    const mostUsed = all
      .sort((a, b) => b.metadata.usageCount - a.metadata.usageCount)
      .slice(0, 5)
      .map(t => t.metadata);

    const topRated = all
      .sort((a, b) => b.metadata.rating - a.metadata.rating)
      .slice(0, 5)
      .map(t => t.metadata);

    const recentlyModified = all
      .sort((a, b) => b.metadata.modified - a.metadata.modified)
      .slice(0, 5)
      .map(t => t.metadata);

    return {
      totalTemplates: this.templates.size,
      byCategory,
      mostUsed,
      topRated,
      recentlyModified,
    };
  }

  /**
   * Export templates
   */
  exportTemplates(templateIds?: string[]): TemplateExportFormat {
    const templates = templateIds
      ? templateIds.map(id => this.templates.get(id)).filter((t): t is Template => t !== undefined)
      : Array.from(this.templates.values());

    return {
      version: '1.0',
      exportDate: Date.now(),
      templates,
      metadata: {
        exporterVersion: '1.0',
        templateCount: templates.length,
      },
    };
  }

  /**
   * Import templates
   */
  importTemplates(data: TemplateExportFormat): TemplateImportResult {
    const imported: string[] = [];
    const skipped: string[] = [];
    const errors: Array<{ templateName: string; error: string }> = [];

    for (const template of data.templates) {
      try {
        // Check if template already exists (by name)
        const exists = Array.from(this.templates.values()).some(
          t => t.metadata.name === template.metadata.name
        );

        if (exists) {
          skipped.push(template.metadata.id);
          continue;
        }

        // Generate new ID for imported template
        const newId = `imported-${template.metadata.id}-${Date.now()}`;
        template.metadata.id = newId;
        template.metadata.category = 'imported';

        this.saveTemplate(template);
        imported.push(newId);
      } catch (error) {
        errors.push({
          templateName: template.metadata.name,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    logger.info(
      `[TemplateLibrary] Imported ${imported.length} templates, skipped ${skipped.length}, errors: ${errors.length}`
    );

    return {
      success: imported.length > 0,
      imported,
      skipped,
      errors,
      message: `Imported ${imported.length}, skipped ${skipped.length}, errors ${errors.length}`,
    };
  }

  /**
   * Record template usage
   */
  recordUsage(templateId: string): void {
    const template = this.templates.get(templateId);
    if (template) {
      template.metadata.usageCount++;
      template.metadata.modified = Date.now();
      this.persistToStorage();
    }
  }

  /**
   * Rate template
   */
  rateTemplate(templateId: string, rating: number): { success: boolean; message: string } {
    try {
      if (rating < 0 || rating > 5) {
        return { success: false, message: 'Rating must be between 0 and 5' };
      }

      const template = this.templates.get(templateId);
      if (!template) {
        return { success: false, message: 'Template not found' };
      }

      template.metadata.rating = rating;
      this.persistToStorage();

      return { success: true, message: 'Template rated' };
    } catch (error) {
      logger.error('[TemplateLibrary] Failed to rate template', error);
      return { success: false, message: 'Failed to rate template' };
    }
  }

  /**
   * Get all tags
   */
  getAllTags(): Array<{ tag: string; count: number }> {
    return Array.from(this.tags.entries()).map(([tag, ids]) => ({
      tag,
      count: ids.length,
    }));
  }

  /**
   * Get all categories with counts
   */
  getAllCategories(): Array<{ category: TemplateCategory; count: number }> {
    return Array.from(this.categories.entries()).map(([category, ids]) => ({
      category,
      count: ids.length,
    }));
  }

  /**
   * Persist library to storage
   */
  private persistToStorage(): void {
    try {
      const data = this.exportTemplates();
      localStorage.setItem(this.storageKey, JSON.stringify(data));
    } catch (error) {
      logger.warn('[TemplateLibrary] Failed to persist to storage', error);
    }
  }

  /**
   * Load from export format
   */
  private loadFromExportFormat(data: TemplateExportFormat): void {
    this.initializeCategories();

    for (const template of data.templates) {
      this.templates.set(template.metadata.id, template);

      // Index by category
      const category = template.metadata.category;
      if (!this.categories.has(category)) {
        this.categories.set(category, []);
      }
      this.categories.get(category)!.push(template.metadata.id);

      // Index by tags
      for (const tag of template.metadata.tags) {
        if (!this.tags.has(tag)) {
          this.tags.set(tag, []);
        }
        this.tags.get(tag)!.push(template.metadata.id);
      }
    }
  }

  /**
   * Clear entire library
   */
  clear(): void {
    this.templates.clear();
    this.categories.clear();
    this.tags.clear();
    localStorage.removeItem(this.storageKey);
    logger.warn('[TemplateLibrary] Cleared entire library');
  }

  /**
   * Get library size
   */
  getSize(): { templates: number; bytes: number } {
    const json = JSON.stringify(this.exportTemplates());
    return {
      templates: this.templates.size,
      bytes: new Blob([json]).size,
    };
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const templateLibrary = new TemplateLibraryManager();

// Default export
export default templateLibrary;
