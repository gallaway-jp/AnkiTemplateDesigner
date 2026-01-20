/**
 * Preview Renderer Service
 * Renders block trees as HTML preview with live updates
 */

import { CraftNode, findNodeById } from './canvasNodeRenderer';
import { BlockInstance } from './blockInstantiator';
import { blockRegistry } from './blockRegistry';
import { logger } from '@/utils/logger';

/**
 * Preview render options
 */
export interface PreviewRenderOptions {
  showFieldPlaceholders?: boolean;
  showGuides?: boolean;
  responsive?: boolean;
  previewMode?: 'desktop' | 'mobile' | 'tablet';
  fieldValues?: Record<string, string>;
  cssOverrides?: Record<string, string>;
}

/**
 * Render CraftNode tree to HTML string
 */
export function renderNodeToHtml(node: CraftNode, options?: PreviewRenderOptions): string {
  try {
    const block = blockRegistry.get(node.displayName.toLowerCase().replace(/\s+/g, '-'));
    const html = renderNodeAsHtml(node, options);
    return html || '<div>Unable to render preview</div>';
  } catch (error) {
    logger.error('Failed to render node preview', error);
    return '<div style="color: red;">Preview error</div>';
  }
}

/**
 * Internal node to HTML rendering
 */
function renderNodeAsHtml(
  node: CraftNode,
  options: PreviewRenderOptions = {}
): string {
  try {
    const {
      showFieldPlaceholders = true,
      showGuides = false,
      fieldValues = {},
      cssOverrides = {},
    } = options;

    // Build inline styles
    const styles: string[] = [];
    Object.entries(node.props).forEach(([key, value]) => {
      if (key.startsWith('style') || key === 'padding' || key === 'margin') {
        styles.push(`${camelToKebab(key)}: ${value}`);
      }
    });

    if (showGuides) {
      styles.push('outline: 1px dashed #ccc;');
      styles.push('outline-offset: -1px;');
    }

    // Apply CSS overrides
    Object.entries(cssOverrides).forEach(([key, value]) => {
      styles.push(`${key}: ${value}`);
    });

    const styleAttr = styles.length > 0 ? ` style="${styles.join('; ')}"` : '';

    // Get element tag and attributes
    const tag = getHtmlTagForNode(node);
    const attrs: string[] = [];

    // Add data attributes
    attrs.push(`data-node-id="${node.id}"`);
    attrs.push(`data-node-type="${node.type}"`);

    // Add class if provided
    if (node.props.className) {
      attrs.push(`class="${node.props.className}"`);
    }

    // Add other attributes
    if (node.props.title) attrs.push(`title="${escapeHtml(node.props.title)}"`);
    if (node.props.placeholder) {
      attrs.push(`placeholder="${escapeHtml(node.props.placeholder)}"`);
    }

    // Handle special content
    let content = '';

    // Anki field blocks
    if (node.type.includes('AnkiField')) {
      const fieldName = node.props.fieldName || 'Field';
      if (showFieldPlaceholders) {
        const fieldValue = fieldValues[fieldName] || `[${fieldName}]`;
        content = escapeHtml(fieldValue);
      } else {
        content = `{{${fieldName}}}`;
      }
    }
    // Anki cloze blocks
    else if (node.type.includes('AnkiCloze')) {
      const fieldName = node.props.fieldName || 'Text';
      content = `{{cloze:${fieldName}}}`;
    }
    // Anki hint blocks
    else if (node.type.includes('AnkiHint')) {
      const fieldName = node.props.fieldName || 'Hint';
      content = `{{hint:${fieldName}}}`;
    }
    // Text content
    else if (node.props.text) {
      content = escapeHtml(node.props.text);
    } else if (node.props.label) {
      content = escapeHtml(node.props.label);
    } else if (node.props.title) {
      content = escapeHtml(node.props.title);
    }

    // Render children
    const children = Object.values(node.nodes)
      .map((child) => renderNodeAsHtml(child, options))
      .join('\n');

    const attrStr = attrs.concat(styleAttr.slice(1)).join(' ');

    if (children || content) {
      return `<${tag} ${attrStr}>${content}${children}</${tag}>`;
    } else {
      return `<${tag} ${attrStr} />`;
    }
  } catch (error) {
    logger.error('Node render error', error);
    return '<div>Render error</div>';
  }
}

/**
 * Render with inline CSS from styles
 */
export function renderWithStyles(
  node: CraftNode,
  styles: Record<string, Record<string, string>> = {},
  options?: PreviewRenderOptions
): string {
  try {
    const withCss = renderNodeToHtml(node, options);

    // Build CSS string from node tree
    const cssRules: string[] = [];
    function collectStyles(n: CraftNode) {
      const selector = `[data-node-id="${n.id}"]`;
      if (styles[n.id]) {
        const declarations = Object.entries(styles[n.id])
          .map(([k, v]) => `${k}: ${v};`)
          .join('\n  ');
        cssRules.push(`${selector} {\n  ${declarations}\n}`);
      }
      Object.values(n.nodes).forEach(collectStyles);
    }

    collectStyles(node);

    const css = cssRules.length > 0 ? `<style>${cssRules.join('\n')}</style>` : '';
    return `${css}${withCss}`;
  } catch (error) {
    logger.error('Failed to render with styles', error);
    return renderNodeToHtml(node, options);
  }
}

/**
 * Create preview container with responsive wrapper
 */
export function createResponsivePreview(
  node: CraftNode,
  mode: 'desktop' | 'mobile' | 'tablet' = 'desktop',
  options?: PreviewRenderOptions
): string {
  try {
    const html = renderNodeToHtml(node, options);

    const dimensions = {
      desktop: { width: '100%', height: 'auto' },
      mobile: { width: '375px', height: '667px' },
      tablet: { width: '768px', height: '1024px' },
    };

    const dim = dimensions[mode];

    return `
      <div style="
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 20px;
        background: #f5f5f5;
        overflow: auto;
      ">
        <div style="
          width: ${dim.width};
          height: ${dim.height};
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          ${mode !== 'desktop' ? 'border: 1px solid #999;' : ''}
        ">
          ${html}
        </div>
      </div>
    `;
  } catch (error) {
    logger.error('Failed to create responsive preview', error);
    return renderNodeToHtml(node, options);
  }
}

/**
 * Get HTML tag for node type
 */
function getHtmlTagForNode(node: CraftNode): string {
  const type = node.type.toLowerCase();

  if (type.includes('heading')) return 'h2';
  if (type.includes('paragraph')) return 'p';
  if (type.includes('label')) return 'label';
  if (type.includes('button')) return 'button';
  if (type.includes('input') || type.includes('text-field')) return 'input';
  if (type.includes('textarea')) return 'textarea';
  if (type.includes('select')) return 'select';
  if (type.includes('image')) return 'img';
  if (type.includes('video')) return 'video';
  if (type.includes('list') || type.includes('row')) return 'ul';
  if (type.includes('item')) return 'li';
  if (type.includes('link')) return 'a';
  if (type.includes('frame')) return 'main';
  if (type.includes('section')) return 'section';
  if (type.includes('panel')) return 'article';
  if (type.includes('form')) return 'form';
  if (type.includes('field')) return 'fieldset';
  if (type.includes('grid')) return 'div';
  if (type.includes('stack')) return 'div';
  if (type.includes('container')) return 'div';
  if (type.includes('anki')) return 'span';

  return 'div'; // Default
}

/**
 * Escape HTML special characters
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
 * Convert camelCase to kebab-case
 */
function camelToKebab(str: string): string {
  return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
}

/**
 * Render node with field substitution
 */
export function renderWithFieldValues(
  node: CraftNode,
  fieldValues: Record<string, string>,
  options?: PreviewRenderOptions
): string {
  return renderNodeToHtml(node, {
    ...options,
    fieldValues,
    showFieldPlaceholders: true,
  });
}

/**
 * Generate preview with sample data
 */
export function generateSamplePreview(node: CraftNode): string {
  const sampleFieldValues: Record<string, string> = {
    Front: 'What is the capital of France?',
    Back: 'Paris',
    Example: 'The capital of France is Paris.',
    Definition: 'A city that is the seat of government.',
    Notes: 'Remember the Eiffel Tower!',
    Hint: 'Starts with P',
  };

  return renderWithFieldValues(node, sampleFieldValues, {
    showFieldPlaceholders: true,
    showGuides: false,
  });
}

/**
 * Get preview HTML safe for iframe
 */
export function getIframePreviewHtml(
  node: CraftNode,
  options?: PreviewRenderOptions,
  additionalCss?: string
): string {
  const html = renderNodeToHtml(node, options);

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    [data-node-id] { display: block; }
    input, textarea, select { font-family: inherit; }
    ${additionalCss || ''}
  </style>
</head>
<body>
  ${html}
</body>
</html>`;
}

/**
 * Extract text content from node tree for preview
 */
export function extractPreviewText(node: CraftNode): string {
  const texts: string[] = [];

  function traverse(n: CraftNode) {
    if (n.props.text) texts.push(n.props.text);
    if (n.props.label) texts.push(n.props.label);
    if (n.props.title) texts.push(n.props.title);
    Object.values(n.nodes).forEach(traverse);
  }

  traverse(node);
  return texts.join(' ');
}

export default {
  renderNodeToHtml,
  renderWithStyles,
  createResponsivePreview,
  renderWithFieldValues,
  generateSamplePreview,
  getIframePreviewHtml,
  extractPreviewText,
};
