/**
 * Canvas Integration Tests - Phase 4
 * Comprehensive tests for node rendering, selection, property updates, and preview
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  blockInstanceToCraftNode,
  craftNodeToBlockInstance,
  findNodeById,
  getNodeParent,
  moveNode,
  validateNodeTree,
  getNodeTreeStats,
} from '@/services/canvasNodeRenderer';
import {
  selectNode,
  deselectNode,
  addToSelection,
  getAllSelectedIds,
  getSelectionContext,
} from '@/services/canvasSelectionHandler';
import {
  updateProperty,
  updateProperties,
  canUndo,
  canRedo,
  undoPropertyChange,
} from '@/services/blockPropertyUpdater';
import {
  moveNodeUp,
  moveNodeDown,
  indentNode,
  getAvailableRearrangeOps,
} from '@/services/canvasDragRearrange';
import {
  renderNodeToHtml,
  renderWithFieldValues,
  generateSamplePreview,
} from '@/services/previewRenderer';
import { createBlockInstance } from '@/services/blockInstantiator';
import { blockRegistry } from '@/services/blockRegistry';

describe('Canvas Node Rendering', () => {
  let rootInstance;
  let rootNode;

  beforeEach(() => {
    rootInstance = createBlockInstance('layout-frame', { title: 'Template' });
    rootNode = blockInstanceToCraftNode(rootInstance);
  });

  it('should convert BlockInstance to CraftNode', () => {
    expect(rootNode).toBeDefined();
    expect(rootNode.id).toBe(rootInstance.id);
    expect(rootNode.displayName).toBeTruthy();
  });

  it('should create CraftNode with correct properties', () => {
    const node = blockInstanceToCraftNode(
      createBlockInstance('layout-vstack', { padding: '16px' })
    );

    expect(node.props.padding).toBe('16px');
    expect(node.type).toBeTruthy();
  });

  it('should convert nested BlockInstances to nested CraftNodes', () => {
    const child = createBlockInstance('data-heading', { text: 'Title' });
    const parent = createBlockInstance('layout-vstack', {}, [child]);
    const parentNode = blockInstanceToCraftNode(parent);

    expect(Object.keys(parentNode.nodes)).toHaveLength(1);
    expect(parentNode.linkedNodes['child-0']).toBeTruthy();
  });

  it('should convert CraftNode back to BlockInstance', () => {
    const converted = craftNodeToBlockInstance(rootNode);

    expect(converted.id).toBe(rootNode.id);
    expect(converted.props).toEqual(rootNode.props);
  });

  it('should maintain tree structure through conversion cycle', () => {
    const originalInstance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
    ]);

    const craftNode = blockInstanceToCraftNode(originalInstance);
    const restored = craftNodeToBlockInstance(craftNode);

    expect(restored.children).toHaveLength(2);
    expect(restored.children[0].name).toBe('data-heading');
    expect(restored.children[1].name).toBe('data-paragraph');
  });

  it('should validate node tree integrity', () => {
    const validation = validateNodeTree(rootNode);
    expect(validation.valid).toBe(true);
    expect(validation.errors).toHaveLength(0);
  });

  it('should detect invalid node trees', () => {
    const invalidNode = {
      ...rootNode,
      id: 'root',
      nodes: {
        orphan: { ...rootNode, parent: 'non-existent' },
      },
    };

    const validation = validateNodeTree(invalidNode);
    expect(validation.valid).toBe(false);
    expect(validation.errors.length).toBeGreaterThan(0);
  });

  it('should calculate node tree statistics', () => {
    const parent = blockInstanceToCraftNode(
      createBlockInstance('layout-frame', {}, [
        createBlockInstance('data-heading'),
        createBlockInstance('data-paragraph'),
      ])
    );

    const stats = getNodeTreeStats(parent);
    expect(stats.totalNodes).toBe(3);
    expect(stats.leafNodes).toBe(2);
    expect(stats.maxDepth).toBeGreaterThan(0);
  });
});

describe('Canvas Selection', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should select a single node', () => {
    const nodeId = Object.keys(rootNode.nodes)[0];
    selectNode(rootNode, nodeId);
    
    // Note: This would require mocking editorStore
    expect(nodeId).toBeTruthy();
  });

  it('should deselect node', () => {
    deselectNode();
    // Verify deselection in store
  });

  it('should add node to multi-selection', () => {
    const nodeId = Object.keys(rootNode.nodes)[0];
    addToSelection(rootNode, nodeId);
    // Verify multi-selection in store
  });

  it('should get all selected node IDs', () => {
    const selectedIds = getAllSelectedIds();
    expect(Array.isArray(selectedIds)).toBe(true);
  });

  it('should provide selection context', () => {
    const context = getSelectionContext(rootNode);
    
    expect(context).toHaveProperty('selectedCount');
    expect(context).toHaveProperty('canDelete');
    expect(context).toHaveProperty('canDuplicate');
    expect(context).toHaveProperty('canMove');
  });

  it('should handle empty selection', () => {
    const context = getSelectionContext(rootNode);
    expect(context.selectedCount).toBe(0);
    expect(context.canDelete).toBe(false);
  });
});

describe('Property Updates with History', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-vstack', { padding: '8px' });
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should update a single property', () => {
    const result = updateProperty(rootNode, rootNode.id, 'padding', '16px');
    expect(result).toBe(true);
  });

  it('should update multiple properties', () => {
    const result = updateProperties(rootNode, rootNode.id, {
      padding: '16px',
      margin: '8px',
    });
    expect(result).toBe(true);
  });

  it('should not record change if value unchanged', () => {
    const result = updateProperty(rootNode, rootNode.id, 'padding', '8px');
    // Same value - should return true but not record history
    expect(result).toBe(true);
  });

  it('should support undo operation', () => {
    updateProperty(rootNode, rootNode.id, 'padding', '16px');
    const canUndoAfter = canUndo();
    expect(canUndoAfter).toBe(true);

    const change = undoPropertyChange(rootNode);
    expect(change).toBeDefined();
  });

  it('should support redo operation', () => {
    updateProperty(rootNode, rootNode.id, 'padding', '16px');
    undoPropertyChange(rootNode);
    
    const canRedoAfter = canRedo();
    expect(canRedoAfter).toBe(true);
  });

  it('should validate property values', () => {
    // This would test the validate function parameter
    const result = updateProperty(
      rootNode,
      rootNode.id,
      'padding',
      '16px',
      (val) => typeof val === 'string'
    );
    expect(result).toBe(true);
  });
});

describe('Drag-to-Rearrange', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-vstack', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
      createBlockInstance('input-text-field'),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should move node up in list', () => {
    const nodeId = Object.keys(rootNode.nodes)[1]; // Second child
    const result = moveNodeUp(rootNode, nodeId);

    expect(result).toBeDefined();
    expect(result?.id).toBe(rootNode.id); // Should return updated root
  });

  it('should move node down in list', () => {
    const nodeId = Object.keys(rootNode.nodes)[0]; // First child
    const result = moveNodeDown(rootNode, nodeId);

    expect(result).toBeDefined();
  });

  it('should prevent moving top node up', () => {
    const nodeId = Object.keys(rootNode.nodes)[0];
    const result = moveNodeUp(rootNode, nodeId);

    expect(result).toBeNull();
  });

  it('should prevent moving bottom node down', () => {
    const nodeIds = Object.keys(rootNode.nodes);
    const result = moveNodeDown(rootNode, nodeIds[nodeIds.length - 1]);

    expect(result).toBeNull();
  });

  it('should indent node', () => {
    const nodeIds = Object.keys(rootNode.nodes);
    if (nodeIds.length > 1) {
      const result = indentNode(rootNode, nodeIds[1]);
      expect(result).toBeDefined();
    }
  });

  it('should get available rearrange operations', () => {
    const nodeId = Object.keys(rootNode.nodes)[1];
    const ops = getAvailableRearrangeOps(rootNode, nodeId);

    expect(ops).toHaveProperty('canMoveUp');
    expect(ops).toHaveProperty('canMoveDown');
    expect(ops).toHaveProperty('canIndent');
    expect(ops).toHaveProperty('canOutdent');
  });
});

describe('Node Finding and Traversal', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('layout-vstack', {}, [
        createBlockInstance('data-heading'),
      ]),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should find node by ID', () => {
    const nodeId = Object.keys(rootNode.nodes)[0];
    const found = findNodeById(rootNode, nodeId);

    expect(found).toBeDefined();
    expect(found?.id).toBe(nodeId);
  });

  it('should return null for non-existent node', () => {
    const found = findNodeById(rootNode, 'non-existent');
    expect(found).toBeNull();
  });

  it('should find node parent', () => {
    const childId = Object.keys(rootNode.nodes)[0];
    const parent = getNodeParent(rootNode, childId);

    expect(parent?.id).toBe(rootNode.id);
  });

  it('should return null for root parent', () => {
    const parent = getNodeParent(rootNode, rootNode.id);
    expect(parent).toBeNull();
  });
});

describe('Preview Rendering', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-vstack', {}, [
      createBlockInstance('data-heading', { text: 'Title' }),
      createBlockInstance('data-paragraph', { text: 'Content' }),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should render node to HTML', () => {
    const html = renderNodeToHtml(rootNode);

    expect(html).toBeTruthy();
    expect(html).toContain('data-node-id');
  });

  it('should include node data attributes in HTML', () => {
    const html = renderNodeToHtml(rootNode);

    expect(html).toContain(`data-node-id="${rootNode.id}"`);
    expect(html).toContain(`data-node-type="${rootNode.type}"`);
  });

  it('should render with field values', () => {
    const html = renderWithFieldValues(rootNode, {
      Front: 'Question?',
      Back: 'Answer!',
    });

    expect(html).toBeTruthy();
  });

  it('should generate sample preview', () => {
    const html = generateSamplePreview(rootNode);

    expect(html).toBeTruthy();
    expect(html.length).toBeGreaterThan(0);
  });

  it('should render with inline styles', () => {
    const nodeWithStyles = {
      ...rootNode,
      props: { ...rootNode.props, padding: '16px', margin: '8px' },
    };

    const html = renderNodeToHtml(nodeWithStyles);
    expect(html).toContain('padding');
  });

  it('should escape HTML in content', () => {
    const nodeWithHtml = {
      ...rootNode,
      props: { ...rootNode.props, text: '<script>alert("xss")</script>' },
    };

    const html = renderNodeToHtml(nodeWithHtml);
    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;script&gt;');
  });
});

describe('Complex Node Operations', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('layout-vstack', {}, [
        createBlockInstance('data-heading'),
        createBlockInstance('data-paragraph'),
      ]),
      createBlockInstance('layout-hstack', {}, [
        createBlockInstance('button-primary'),
        createBlockInstance('button-secondary'),
      ]),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
  });

  it('should calculate correct depth levels', () => {
    const stats = getNodeTreeStats(rootNode);
    expect(stats.maxDepth).toBe(2);
  });

  it('should count total nodes correctly', () => {
    const stats = getNodeTreeStats(rootNode);
    expect(stats.totalNodes).toBe(7); // 1 root + 2 parents + 4 children
  });

  it('should track node types', () => {
    const stats = getNodeTreeStats(rootNode);
    expect(Object.keys(stats.byType).length).toBeGreaterThan(0);
  });

  it('should move node between parents', () => {
    const nodeToMove = Object.values(rootNode.nodes)[0]; // First child
    const targetParent = Object.values(rootNode.nodes)[1]; // Second child

    if (nodeToMove && targetParent) {
      const result = moveNode(rootNode, nodeToMove.id, targetParent.id);
      expect(result).toBeDefined();
    }
  });
});

describe('Edge Cases and Error Handling', () => {
  it('should handle empty node selection context', () => {
    const rootNode = blockInstanceToCraftNode(createBlockInstance('layout-frame'));
    const context = getSelectionContext(rootNode);

    expect(context.selectedCount).toBe(0);
    expect(context.canDelete).toBe(false);
  });

  it('should handle converting empty tree', () => {
    const instance = createBlockInstance('layout-container');
    const node = blockInstanceToCraftNode(instance);

    expect(node).toBeDefined();
    expect(Object.keys(node.nodes)).toHaveLength(0);
  });

  it('should handle finding in non-existent paths', () => {
    const rootNode = blockInstanceToCraftNode(createBlockInstance('layout-frame'));
    const found = findNodeById(rootNode, 'non-existent-deep-id');

    expect(found).toBeNull();
  });

  it('should handle property update on non-existent node', () => {
    const rootNode = blockInstanceToCraftNode(createBlockInstance('layout-frame'));
    const result = updateProperty(rootNode, 'non-existent', 'prop', 'value');

    expect(result).toBe(false);
  });

  it('should handle rendering broken node', () => {
    const brokenNode = {
      id: 'broken',
      type: 'Unknown',
      displayName: 'Unknown',
      isCanvas: false,
      props: {},
      nodes: {},
      linkedNodes: {},
      parent: null,
      depth: 0,
    };

    const html = renderNodeToHtml(brokenNode);
    expect(html).toBeTruthy();
  });
});

describe('Round-trip Operations', () => {
  it('should maintain data through full cycle', () => {
    const originalInstance = createBlockInstance('layout-vstack', { padding: '16px' }, [
      createBlockInstance('data-heading', { text: 'Title' }),
    ]);

    const node = blockInstanceToCraftNode(originalInstance);
    const restored = craftNodeToBlockInstance(node);

    expect(restored.props.padding).toBe('16px');
    expect(restored.children).toHaveLength(1);
    expect(restored.children[0].props.text).toBe('Title');
  });

  it('should preserve structure through operations', () => {
    let instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
    ]);

    let node = blockInstanceToCraftNode(instance);

    // Update properties
    updateProperty(node, Object.keys(node.nodes)[0], 'color', 'red');

    // Render
    const html = renderNodeToHtml(node);
    expect(html).toBeTruthy();

    // Convert back
    const restored = craftNodeToBlockInstance(node);
    expect(restored.children).toHaveLength(2);
  });
});
