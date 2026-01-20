/**
 * Template Loader Service
 * Loads HTML templates and converts them to block instances
 */

import { BlockInstance, createBlockInstance } from './blockInstantiator';
import { blockRegistry } from './blockRegistry';
import { logger } from '@/utils/logger';

/**
 * Parse HTML element to BlockInstance tree
 */
export function parseHtmlElement(
  element: Element,
  blockNameMap?: Map<string, string>
): BlockInstance | null {
  try {
    // Get block name from element data attribute or tag name
    const dataBlockName = element.getAttribute('data-block-name');
    let blockName = dataBlockName || getBlockNameFromElement(element);

    // Apply custom mapping if provided
    if (blockNameMap?.has(blockName)) {
      blockName = blockNameMap.get(blockName)!;
    }

    // Verify block exists
    if (!blockRegistry.get(blockName)) {
      logger.warn(`Block not found in registry: ${blockName}, using generic container`);
      blockName = 'layout-container';
    }

    // Extract props from data attributes
    const props: Record<string, any> = {};
    Array.from(element.attributes).forEach((attr) => {
      if (attr.name.startsWith('data-prop-')) {
        const propName = attr.name.replace('data-prop-', '');
        props[propName] = attr.value;
      }
    });

    // Extract inline styles
    const styles: Record<string, string> = {};
    if (element.style.cssText) {
      element.style.cssText.split(';').forEach((style) => {
        const [key, value] = style.split(':');
        if (key && value) {
          styles[key.trim()] = value.trim();
        }
      });
    }

    // Parse children
    const children: BlockInstance[] = [];
    Array.from(element.children).forEach((child) => {
      const childInstance = parseHtmlElement(child, blockNameMap);
      if (childInstance) {
        children.push(childInstance);
      }
    });

    // Create block instance
    const instance = createBlockInstance(blockName, props, children);
    if (instance && Object.keys(styles).length > 0) {
      instance.styles = styles;
    }

    return instance;
  } catch (error) {
    logger.error(`Failed to parse HTML element`, error);
    return null;
  }
}

/**
 * Load template from HTML string
 */
export function loadTemplateFromHtml(
  htmlString: string,
  blockNameMap?: Map<string, string>
): BlockInstance | null {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');

    // Look for template root element
    let rootElement = doc.documentElement.querySelector('[data-template-root]');
    if (!rootElement) {
      rootElement = doc.body.firstElementChild || doc.documentElement;
    }

    if (!rootElement) {
      logger.error('No root element found in HTML');
      return null;
    }

    const template = parseHtmlElement(rootElement as Element, blockNameMap);
    if (template) {
      logger.info('Template loaded successfully from HTML');
    }
    return template;
  } catch (error) {
    logger.error('Failed to load template from HTML', error);
    return null;
  }
}

/**
 * Load template from JSON representation
 */
export function loadTemplateFromJson(json: string): BlockInstance | null {
  try {
    const data = JSON.parse(json);
    return validateAndRestoreInstance(data);
  } catch (error) {
    logger.error('Failed to parse template JSON', error);
    return null;
  }
}

/**
 * Load template from file (async)
 */
export async function loadTemplateFromFile(file: File): Promise<BlockInstance | null> {
  try {
    const content = await file.text();

    // Determine format by file extension
    if (file.name.endsWith('.html')) {
      return loadTemplateFromHtml(content);
    } else if (file.name.endsWith('.json')) {
      return loadTemplateFromJson(content);
    } else {
      // Try both formats
      if (content.trim().startsWith('<')) {
        return loadTemplateFromHtml(content);
      } else {
        return loadTemplateFromJson(content);
      }
    }
  } catch (error) {
    logger.error(`Failed to load template from file: ${file.name}`, error);
    return null;
  }
}

/**
 * Validate and restore BlockInstance from serialized data
 */
function validateAndRestoreInstance(data: any): BlockInstance | null {
  try {
    if (!data || typeof data !== 'object') {
      return null;
    }

    if (!data.id || !data.name || !data.type) {
      logger.warn('Invalid instance data - missing required fields');
      return null;
    }

    // Verify block exists in registry
    if (!blockRegistry.get(data.name)) {
      logger.warn(`Block not in registry: ${data.name}`);
      return null;
    }

    // Restore children recursively
    const children: BlockInstance[] = [];
    if (Array.isArray(data.children)) {
      data.children.forEach((child: any) => {
        const restored = validateAndRestoreInstance(child);
        if (restored) children.push(restored);
      });
    }

    const instance: BlockInstance = {
      id: data.id,
      name: data.name,
      type: data.type,
      props: data.props || {},
      children,
      styles: data.styles,
      attributes: data.attributes,
      metadata: data.metadata,
    };

    return instance;
  } catch (error) {
    logger.error('Failed to validate and restore instance', error);
    return null;
  }
}

/**
 * Infer block name from HTML element
 */
function getBlockNameFromElement(element: Element): string {
  const tagName = element.tagName.toLowerCase();
  const classList = Array.from(element.classList);

  // Map HTML tags to block names
  const tagBlockMap: Record<string, string> = {
    div: 'layout-container',
    section: 'layout-section',
    article: 'layout-panel',
    main: 'layout-frame',
    header: 'layout-section',
    footer: 'layout-section',
    aside: 'layout-drawer',
    form: 'layout-form',
    fieldset: 'layout-form-group',
    input: 'input-text-field',
    textarea: 'input-text-area',
    button: 'button-primary',
    select: 'input-select',
    label: 'data-label',
    h1: 'data-heading',
    h2: 'data-heading',
    h3: 'data-heading',
    h4: 'data-heading',
    h5: 'data-heading',
    h6: 'data-heading',
    p: 'data-paragraph',
    span: 'data-label',
    img: 'data-image',
    video: 'data-video',
    ul: 'data-unordered-list',
    ol: 'data-ordered-list',
    table: 'data-table',
    code: 'data-inline-code',
  };

  // Check class-based block names
  for (const cls of classList) {
    if (cls.includes('block-')) {
      return cls;
    }
  }

  // Check tag-based mapping
  if (tagBlockMap[tagName]) {
    return tagBlockMap[tagName];
  }

  // Default container
  return 'layout-container';
}

/**
 * Create custom block name mapping for import
 */
export function createBlockNameMapping(mapping: Record<string, string>): Map<string, string> {
  return new Map(Object.entries(mapping));
}

/**
 * Get all block names used in a template
 */
export function getUsedBlockNames(instance: BlockInstance): Set<string> {
  const names = new Set<string>();
  names.add(instance.name);

  if (instance.children) {
    instance.children.forEach((child) => {
      const childNames = getUsedBlockNames(child);
      childNames.forEach((name) => names.add(name));
    });
  }

  return names;
}

/**
 * Validate template compatibility with current registry
 */
export function validateTemplateCompatibility(instance: BlockInstance): {
  compatible: boolean;
  missing: string[];
  warnings: string[];
} {
  const missing: string[] = [];
  const warnings: string[] = [];
  const usedBlocks = getUsedBlockNames(instance);

  usedBlocks.forEach((blockName) => {
    if (!blockRegistry.get(blockName)) {
      missing.push(blockName);
    }
  });

  return {
    compatible: missing.length === 0,
    missing,
    warnings,
  };
}

export default {
  parseHtmlElement,
  loadTemplateFromHtml,
  loadTemplateFromJson,
  loadTemplateFromFile,
  createBlockNameMapping,
  getUsedBlockNames,
  validateTemplateCompatibility,
};
