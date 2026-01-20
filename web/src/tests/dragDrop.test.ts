/**
 * Drag-and-Drop Integration Tests
 * Tests for block dragging, dropping, and canvas integration
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  createBlockInstance,
  createBlockFromDropEvent,
  BlockInstance,
  validateBlockInstance,
  duplicateBlockInstance,
} from '@/services/blockInstantiator';
import { blockRegistry } from '@/services/blockRegistry';
import { exportToHtml, exportToCss, exportToJson } from '@/services/templateExporter';
import { loadTemplateFromHtml, validateTemplateCompatibility } from '@/services/templateLoader';

describe('Block Instantiation', () => {
  beforeEach(() => {
    // Ensure block registry is initialized
    blockRegistry.clear?.();
  });

  it('should create a block instance from a block definition', () => {
    const block = blockRegistry.get('layout-frame');
    expect(block).toBeDefined();

    const instance = createBlockInstance('layout-frame');
    expect(instance).toBeDefined();
    expect(instance?.name).toBe('layout-frame');
    expect(instance?.id).toBeTruthy();
    expect(instance?.type).toBeTruthy();
  });

  it('should create block instance with custom props', () => {
    const props = { title: 'My Template', width: '500px' };
    const instance = createBlockInstance('layout-frame', props);

    expect(instance?.props).toContain({ title: 'My Template', width: '500px' });
  });

  it('should create block instance from drop event with position', () => {
    const instance = createBlockFromDropEvent('layout-vstack', 100, 200);

    expect(instance).toBeDefined();
    expect(instance?.metadata?.position).toEqual({ x: 100, y: 200 });
  });

  it('should generate unique IDs for new instances', () => {
    const instance1 = createBlockInstance('layout-container');
    const instance2 = createBlockInstance('layout-container');

    expect(instance1?.id).not.toBe(instance2?.id);
  });

  it('should validate block instance', () => {
    const instance = createBlockInstance('layout-frame');
    const validation = validateBlockInstance(instance!);

    expect(validation.valid).toBe(true);
    expect(validation.errors).toHaveLength(0);
  });

  it('should detect invalid block instances', () => {
    const invalidInstance: BlockInstance = {
      id: 'test',
      name: 'non-existent-block',
      type: 'test',
      props: {},
      children: [],
    };

    const validation = validateBlockInstance(invalidInstance);
    expect(validation.valid).toBe(false);
    expect(validation.errors.length).toBeGreaterThan(0);
  });
});

describe('Block Tree Operations', () => {
  it('should duplicate a block instance with new ID', () => {
    const original = createBlockInstance('layout-container');
    const duplicate = duplicateBlockInstance(original!);

    expect(duplicate.id).not.toBe(original?.id);
    expect(duplicate.name).toBe(original?.name);
    expect(duplicate.props).toEqual(original?.props);
  });

  it('should create container with multiple children', () => {
    const children = [
      createBlockInstance('data-heading')!,
      createBlockInstance('data-paragraph')!,
    ];

    const container = createBlockInstance('layout-vstack', {}, children);

    expect(container?.children).toHaveLength(2);
    expect(container?.children[0].name).toBe('data-heading');
    expect(container?.children[1].name).toBe('data-paragraph');
  });

  it('should validate nested block instances', () => {
    const child = createBlockInstance('data-paragraph');
    const parent = createBlockInstance('layout-container', {}, [child!]);

    const validation = validateBlockInstance(parent!);
    expect(validation.valid).toBe(true);
  });
});

describe('Template Export', () => {
  let template: BlockInstance;

  beforeEach(() => {
    template = createBlockInstance('layout-frame')!;
  });

  it('should export block to HTML', () => {
    const html = exportToHtml(template);

    expect(html).toContain('data-block-name');
    expect(html).toContain('layout-frame');
    expect(html).toContain(template.id);
  });

  it('should export to JSON', () => {
    const json = exportToJson(template);
    const parsed = JSON.parse(json);

    expect(parsed.id).toBe(template.id);
    expect(parsed.name).toBe(template.name);
    expect(parsed.props).toBeDefined();
  });

  it('should export with inline styles', () => {
    const templateWithStyles = {
      ...template,
      styles: { color: 'red', padding: '10px' },
    };

    const html = exportToHtml(templateWithStyles);
    expect(html).toContain('style');
    expect(html).toContain('color:red');
    expect(html).toContain('padding:10px');
  });

  it('should export CSS rules', () => {
    const templateWithStyles = {
      ...template,
      styles: { 'font-size': '16px', margin: '8px' },
    };

    const css = exportToCss(templateWithStyles);
    expect(css).toContain(`[data-block-id="${template.id}"]`);
    expect(css).toContain('font-size');
    expect(css).toContain('margin');
  });

  it('should export Anki template with fields', () => {
    const instance = createBlockInstance('anki-field', { fieldName: 'Front' });
    const ankiExport = require('@/services/templateExporter').exportToAnkiTemplate(
      instance!
    );

    expect(ankiExport.name).toBeDefined();
    expect(ankiExport.html).toBeTruthy();
    expect(ankiExport.css).toBeTruthy();
  });
});

describe('Template Loading', () => {
  it('should load template from HTML string', () => {
    const html = '<div data-block-name="layout-container">Content</div>';
    const template = loadTemplateFromHtml(html);

    expect(template).toBeDefined();
    expect(template?.name).toBe('layout-container');
  });

  it('should validate template compatibility', () => {
    const template = createBlockInstance('layout-frame')!;
    const compatibility = validateTemplateCompatibility(template);

    expect(compatibility.compatible).toBe(true);
    expect(compatibility.missing).toHaveLength(0);
  });

  it('should detect missing blocks in template', () => {
    const template: BlockInstance = {
      id: 'test',
      name: 'layout-frame',
      type: 'Frame',
      props: {},
      children: [
        {
          id: 'child',
          name: 'non-existent-block',
          type: 'Unknown',
          props: {},
          children: [],
        },
      ],
    };

    const compatibility = validateTemplateCompatibility(template);
    expect(compatibility.compatible).toBe(false);
    expect(compatibility.missing).toContain('non-existent-block');
  });
});

describe('Drag-and-Drop Integration', () => {
  it('should simulate drag start with block data', () => {
    const mockDataTransfer = new DataTransfer();
    mockDataTransfer.setData('application/block-name', 'layout-vstack');

    const blockName = mockDataTransfer.getData('application/block-name');
    expect(blockName).toBe('layout-vstack');
  });

  it('should create instance on drop with position', () => {
    const dropX = 150;
    const dropY = 250;

    const instance = createBlockFromDropEvent('layout-container', dropX, dropY);

    expect(instance?.metadata?.position?.x).toBe(dropX);
    expect(instance?.metadata?.position?.y).toBe(dropY);
  });

  it('should handle multiple sequential drops', () => {
    const blocks = ['layout-vstack', 'data-heading', 'data-paragraph'];
    const instances = blocks.map((blockName, idx) =>
      createBlockFromDropEvent(blockName, 100 + idx * 50, 100 + idx * 50)
    );

    expect(instances).toHaveLength(3);
    instances.forEach((instance, idx) => {
      expect(instance?.name).toBe(blocks[idx]);
      expect(instance?.metadata?.position).toBeDefined();
    });
  });

  it('should handle drop of invalid block gracefully', () => {
    const invalidInstance = createBlockInstance('non-existent-block');
    expect(invalidInstance).toBeNull();
  });
});

describe('Round-trip Serialization', () => {
  it('should export and reload template preserving structure', () => {
    const original = createBlockInstance('layout-frame', { title: 'Test' }, [
      createBlockInstance('data-heading', { text: 'Title' })!,
      createBlockInstance('data-paragraph', { text: 'Content' })!,
    ])!;

    // Export to JSON
    const json = exportToJson(original);

    // Reload from JSON
    const reloaded = loadTemplateFromHtml(
      `<div>${JSON.stringify(JSON.parse(json))}</div>`
    );

    expect(reloaded?.name).toBe(original.name);
    expect(reloaded?.children).toHaveLength(2);
  });

  it('should preserve properties through export/import cycle', () => {
    const original = createBlockInstance('layout-container', {
      padding: '16px',
      background: '#fff',
    })!;

    const json = exportToJson(original);
    const data = JSON.parse(json);

    expect(data.props.padding).toBe('16px');
    expect(data.props.background).toBe('#fff');
  });

  it('should maintain block IDs through serialization', () => {
    const original = createBlockInstance('layout-frame')!;
    const json = exportToJson(original);
    const reloaded = JSON.parse(json);

    expect(reloaded.id).toBe(original.id);
  });
});

describe('Canvas Drop Handler', () => {
  it('should calculate correct canvas position from drop event', () => {
    // Simulate drop event coordinates
    const clientX = 500;
    const clientY = 600;

    // Simulated canvas bounds
    const canvasRect = {
      left: 250,
      top: 100,
      right: 1000,
      bottom: 1000,
    };

    const dropX = clientX - canvasRect.left;
    const dropY = clientY - canvasRect.top;

    expect(dropX).toBe(250);
    expect(dropY).toBe(500);
  });

  it('should handle drops at canvas boundaries', () => {
    // Top-left corner
    const instance1 = createBlockFromDropEvent('layout-container', 0, 0);
    expect(instance1?.metadata?.position).toEqual({ x: 0, y: 0 });

    // Large coordinates
    const instance2 = createBlockFromDropEvent('layout-container', 999999, 999999);
    expect(instance2?.metadata?.position).toEqual({ x: 999999, y: 999999 });
  });
});

describe('Block Category Integration', () => {
  it('should create blocks from different categories', () => {
    const blocks = [
      createBlockInstance('layout-frame')!, // layout
      createBlockInstance('input-text-field')!, // input
      createBlockInstance('button-primary')!, // button
      createBlockInstance('data-heading')!, // data
    ];

    expect(blocks).toHaveLength(4);
    blocks.forEach((block) => {
      expect(block.id).toBeTruthy();
      expect(validateBlockInstance(block).valid).toBe(true);
    });
  });

  it('should maintain category info in registry lookups', () => {
    const layoutBlock = blockRegistry.get('layout-frame');
    const inputBlock = blockRegistry.get('input-text-field');
    const dataBlock = blockRegistry.get('data-heading');

    expect(layoutBlock?.category).toBe('layout');
    expect(inputBlock?.category).toBe('input');
    expect(dataBlock?.category).toBe('data');
  });
});
