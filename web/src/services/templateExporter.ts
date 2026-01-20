/**
 * Template Exporter Service
 * Exports block trees to HTML, CSS, and Anki template formats
 */

import { BlockInstance } from './blockInstantiator';
import { blockRegistry } from './blockRegistry';
import { logger } from '@/utils/logger';

/**
 * Export block tree to HTML string
 */
export function exportToHtml(instance: BlockInstance): string {
  try {
    const html = blockInstanceToHtml(instance);
    logger.info('Template exported to HTML');
    return html;
  } catch (error) {
    logger.error('Failed to export template to HTML', error);
    return '';
  }
}

/**
 * Convert block instance to HTML element
 */
function blockInstanceToHtml(instance: BlockInstance): string {
  const block = blockRegistry.get(instance.name);
  const tagName = getHtmlTagForBlock(instance.name);

  // Build attributes
  const attrs: string[] = [
    `data-block-name="${instance.name}"`,
    `data-block-id="${instance.id}"`,
  ];

  // Add props as data attributes
  Object.entries(instance.props).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      attrs.push(`data-prop-${key}="${escapeHtml(String(value))}"`);
    }
  });

  // Add styles as inline style attribute
  if (instance.styles && Object.keys(instance.styles).length > 0) {
    const styleStr = Object.entries(instance.styles)
      .map(([k, v]) => `${k}:${v}`)
      .join(';');
    attrs.push(`style="${escapeHtml(styleStr)}"`);
  }

  // Add custom attributes
  if (instance.attributes) {
    Object.entries(instance.attributes).forEach(([key, value]) => {
      attrs.push(`${key}="${escapeHtml(value)}"`);
    });
  }

  // Build children
  const childrenHtml = instance.children
    .map((child) => blockInstanceToHtml(child))
    .join('\n  ');

  const attrStr = attrs.join(' ');
  if (childrenHtml) {
    return `<${tagName} ${attrStr}>\n  ${childrenHtml}\n</${tagName}>`;
  } else {
    return `<${tagName} ${attrStr} />`;
  }
}

/**
 * Export block tree to CSS
 */
export function exportToCss(instance: BlockInstance): string {
  try {
    const styles: string[] = [];
    collectCssRules(instance, styles);
    const css = styles.join('\n\n');
    logger.info('Template CSS exported');
    return css;
  } catch (error) {
    logger.error('Failed to export template CSS', error);
    return '';
  }
}

/**
 * Collect CSS rules from block tree
 */
function collectCssRules(instance: BlockInstance, styles: string[]): void {
  const block = blockRegistry.get(instance.name);

  // Add block-specific styles
  if (instance.styles && Object.keys(instance.styles).length > 0) {
    const selector = `[data-block-id="${instance.id}"]`;
    const styleDecl = Object.entries(instance.styles)
      .map(([key, value]) => `  ${key}: ${value};`)
      .join('\n');
    styles.push(`${selector} {\n${styleDecl}\n}`);
  }

  // Recursively process children
  if (instance.children) {
    instance.children.forEach((child) => {
      collectCssRules(child, styles);
    });
  }
}

/**
 * Export to JSON format
 */
export function exportToJson(instance: BlockInstance, pretty: boolean = true): string {
  try {
    const json = pretty
      ? JSON.stringify(instance, null, 2)
      : JSON.stringify(instance);
    logger.info('Template exported to JSON');
    return json;
  } catch (error) {
    logger.error('Failed to export template to JSON', error);
    return '';
  }
}

/**
 * Export to Anki template format
 */
export function exportToAnkiTemplate(
  instance: BlockInstance,
  templateName: string = 'Front'
): AnkiTemplateExport {
  try {
    const html = exportToHtml(instance);
    const css = exportToCss(instance);

    const template: AnkiTemplateExport = {
      name: templateName,
      html,
      css,
      fields: extractFieldsFromTemplate(instance),
      metadata: {
        version: '1.0',
        exportedAt: new Date().toISOString(),
      },
    };

    logger.info(`Anki template exported: ${templateName}`);
    return template;
  } catch (error) {
    logger.error('Failed to export Anki template', error);
    return {
      name: templateName,
      html: '',
      css: '',
      fields: [],
      metadata: {},
    };
  }
}

/**
 * Extract field references from template
 */
function extractFieldsFromTemplate(instance: BlockInstance): string[] {
  const fields = new Set<string>();
  const fieldPattern = /\{\{([^}:]+)(?::[^}]*)?\}\}/g;

  // Check current instance
  const htmlSnippet = blockInstanceToHtml(instance);
  let match;
  while ((match = fieldPattern.exec(htmlSnippet)) !== null) {
    fields.add(match[1].trim());
  }

  // Check children
  if (instance.children) {
    instance.children.forEach((child) => {
      extractFieldsFromTemplate(child).forEach((field) => {
        fields.add(field);
      });
    });
  }

  return Array.from(fields).sort();
}

/**
 * Export complete deck template (front + back)
 */
export function exportDeckTemplate(
  front: BlockInstance,
  back: BlockInstance,
  styling: string = ''
): DeckTemplateExport {
  return {
    front: exportToAnkiTemplate(front, 'Front'),
    back: exportToAnkiTemplate(back, 'Back'),
    styling: styling || defaultAnkiStyling(),
    metadata: {
      version: '1.0',
      exportedAt: new Date().toISOString(),
    },
  };
}

/**
 * Export as downloadable package
 */
export async function exportAsPackage(
  instance: BlockInstance,
  filename: string
): Promise<void> {
  try {
    const json = exportToJson(instance);
    const html = exportToHtml(instance);
    const css = exportToCss(instance);

    const packageContent = {
      filename,
      html,
      css,
      json: JSON.parse(json),
      createdAt: new Date().toISOString(),
    };

    // Create blob and trigger download
    const blob = new Blob([JSON.stringify(packageContent, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.json`;
    link.click();
    URL.revokeObjectURL(url);

    logger.info(`Package exported: ${filename}`);
  } catch (error) {
    logger.error('Failed to export package', error);
  }
}

/**
 * Get HTML tag for block type
 */
function getHtmlTagForBlock(blockName: string): string {
  const tagMap: Record<string, string> = {
    'layout-frame': 'main',
    'layout-section': 'section',
    'layout-panel': 'article',
    'layout-container': 'div',
    'layout-drawer': 'aside',
    'layout-form': 'form',
    'layout-form-group': 'fieldset',
    'layout-grid': 'div',
    'layout-vstack': 'div',
    'layout-hstack': 'div',
    'input-text-field': 'input',
    'input-text-area': 'textarea',
    'input-select': 'select',
    'button-primary': 'button',
    'button-secondary': 'button',
    'data-heading': 'h2',
    'data-paragraph': 'p',
    'data-label': 'label',
    'data-image': 'img',
    'data-video': 'video',
  };

  return tagMap[blockName] || 'div';
}

/**
 * Escape HTML entities
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (char) => map[char]);
}

/**
 * Default Anki styling
 */
function defaultAnkiStyling(): string {
  return `.card {
  font-family: Segoe UI, Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #333;
  background-color: #fff;
  padding: 20px;
}

.night_mode .card {
  background-color: #313131;
  color: #fff;
}

b { color: #0066cc; }
strong { color: #0066cc; }
`;
}

/**
 * Anki template export type
 */
export interface AnkiTemplateExport {
  name: string;
  html: string;
  css: string;
  fields: string[];
  metadata?: Record<string, any>;
}

/**
 * Deck template export type
 */
export interface DeckTemplateExport {
  front: AnkiTemplateExport;
  back: AnkiTemplateExport;
  styling: string;
  metadata?: Record<string, any>;
}

export default {
  exportToHtml,
  exportToCss,
  exportToJson,
  exportToAnkiTemplate,
  exportDeckTemplate,
  exportAsPackage,
};
