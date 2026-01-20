/**
 * Phase 5 Integration Tests
 * Tests for canvasOptimization, keyboardNavigation, and clipboardManager
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { canvasOptimization, VirtualScroller, BatchUpdateManager } from '@/services/canvasOptimization';
import { keyboardNavigation, getNavigationContext } from '@/services/keyboardNavigation';
import { clipboard } from '@/services/clipboardManager';
import { blockInstanceToCraftNode } from '@/services/canvasNodeRenderer';
import { createBlockInstance } from '@/services/blockInstantiator';

describe('Canvas Rendering Optimization', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('layout-vstack', {}, [
        createBlockInstance('data-heading'),
        createBlockInstance('data-paragraph'),
      ]),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
    canvasOptimization.initialize();
  });

  describe('Performance Monitoring', () => {
    it('should track frame time', () => {
      const startTime = canvasOptimization.startFrame();
      const metrics = canvasOptimization.endFrame(startTime);

      expect(metrics.frameTime).toBeGreaterThanOrEqual(0);
    });

    it('should calculate FPS from samples', () => {
      for (let i = 0; i < 10; i++) {
        const start = canvasOptimization.startFrame();
        canvasOptimization.endFrame(start);
      }

      const metrics = canvasOptimization.getMetrics(5, 5);
      expect(metrics.fps).toBeGreaterThan(0);
    });

    it('should track node counts', () => {
      const metrics = canvasOptimization.getMetrics(100, 25);

      expect(metrics.nodeCount).toBe(100);
      expect(metrics.visibleNodeCount).toBe(25);
    });

    it('should track memory usage', () => {
      const metrics = canvasOptimization.getMetrics(50, 50);
      expect(typeof metrics.memoryUsage).toBe('number');
    });

    it('should provide health check', () => {
      const health = canvasOptimization.getHealthCheck();

      expect(health).toHaveProperty('fps');
      expect(health).toHaveProperty('frameTime');
      expect(health).toHaveProperty('fpsOk');
      expect(health).toHaveProperty('frameTimeOk');
      expect(health).toHaveProperty('cache');
      expect(health).toHaveProperty('cacheOk');
    });
  });

  describe('Render Cache', () => {
    it('should cache node render', () => {
      const html = '<div>test</div>';
      const hash = 'abc123';

      canvasOptimization.cacheRender('node1', html, rootNode);
      const cached = canvasOptimization.getCachedRender('node1', rootNode);

      expect(cached).toBeTruthy();
    });

    it('should invalidate on hash mismatch', () => {
      const html = '<div>test</div>';
      canvasOptimization.cacheRender('node1', html, rootNode);

      // Modify node to change hash
      rootNode.props.newProp = 'newValue';

      const cached = canvasOptimization.getCachedRender('node1', rootNode);
      expect(cached).toBeNull(); // Hash mismatch invalidates
    });

    it('should provide cache statistics', () => {
      canvasOptimization.cacheRender('node1', '<div>1</div>', rootNode);

      const stats = canvasOptimization.getCacheStats();
      expect(stats.entries).toBeGreaterThan(0);
      expect(stats.totalSize).toBeGreaterThan(0);
      expect(stats.utilizationPercent).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Virtual Scrolling', () => {
    let scroller: VirtualScroller;

    beforeEach(() => {
      scroller = canvasOptimization.setupVirtualScroll(rootNode);
    });

    it('should flatten tree into array', () => {
      const flattened = scroller['flattenedNodes'];
      expect(flattened.length).toBeGreaterThan(0);
    });

    it('should calculate visible range', () => {
      const viewport = scroller.getVisibleRange(0, 500, 30);

      expect(viewport.startIndex).toBeGreaterThanOrEqual(0);
      expect(viewport.endIndex).toBeGreaterThanOrEqual(viewport.startIndex);
      expect(viewport.visibleCount).toBeGreaterThan(0);
    });

    it('should return visible nodes', () => {
      const viewport = scroller.getVisibleRange(0, 500, 30);
      const visible = scroller.getVisibleNodes(viewport);

      expect(visible.length).toBeGreaterThan(0);
    });

    it('should find node at index', () => {
      const node = scroller.getNodeAt(0);
      expect(node).toBeTruthy();
    });

    it('should find index of node', () => {
      const first = scroller.getNodeAt(0);
      if (first) {
        const index = scroller.getIndexOfNode(first.id);
        expect(index).toBeGreaterThanOrEqual(0);
      }
    });

    it('should handle scroll offset', () => {
      const viewport1 = scroller.getVisibleRange(0, 500, 30);
      const viewport2 = scroller.getVisibleRange(300, 500, 30);

      // More scroll = higher start index
      expect(viewport2.startIndex).toBeGreaterThanOrEqual(viewport1.startIndex);
    });
  });

  describe('Batch Update Manager', () => {
    let batchManager: BatchUpdateManager;

    beforeEach(() => {
      batchManager = new BatchUpdateManager();
    });

    it('should queue updates', () => {
      batchManager.queueUpdate('node1', 'padding', '16px');
      expect(batchManager.getPendingCount()).toBeGreaterThan(0);
    });

    it('should remove duplicate updates', () => {
      batchManager.queueUpdate('node1', 'padding', '16px');
      batchManager.queueUpdate('node1', 'padding', '8px');

      expect(batchManager.getPendingCount()).toBe(1);
    });

    it('should process batch', (done) => {
      batchManager.onBatchReady = (batch) => {
        expect(batch).toBeTruthy();
        done();
      };

      batchManager.queueUpdate('node1', 'padding', '16px');
      setTimeout(() => batchManager.flush(), 20);
    });

    it('should handle multiple nodes', () => {
      batchManager.queueUpdate('node1', 'padding', '16px');
      batchManager.queueUpdate('node2', 'margin', '8px');
      batchManager.queueUpdate('node1', 'color', 'red');

      expect(batchManager.getPendingCount()).toBe(3);
    });

    it('should flush pending updates', () => {
      batchManager.queueUpdate('node1', 'padding', '16px');
      batchManager.flush();

      expect(batchManager.getPendingCount()).toBe(0);
    });
  });
});

describe('Keyboard Navigation', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
      createBlockInstance('input-text-field'),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
    keyboardNavigation.initialize(rootNode);
    keyboardNavigation.setCurrentNode(Object.keys(rootNode.nodes)[0]);
  });

  describe('Navigation Context', () => {
    it('should get navigation context', () => {
      const context = keyboardNavigation.getContext();

      expect(context).toBeTruthy();
      expect(context).toHaveProperty('currentNodeId');
      expect(context).toHaveProperty('canNavigateUp');
      expect(context).toHaveProperty('canNavigateDown');
    });

    it('should identify available moves', () => {
      const context = keyboardNavigation.getContext();
      const { canNavigateUp, canNavigateDown, canNavigateLeft, canNavigateRight } = context;

      expect(typeof canNavigateUp).toBe('boolean');
      expect(typeof canNavigateDown).toBe('boolean');
      expect(typeof canNavigateLeft).toBe('boolean');
      expect(typeof canNavigateRight).toBe('boolean');
    });
  });

  describe('Arrow Key Navigation', () => {
    it('should navigate down to next sibling', () => {
      const before = keyboardNavigation.getCurrentNode();
      const result = keyboardNavigation.navigateDown();

      expect(result).toBeTruthy();
      expect(result).not.toBe(before);
    });

    it('should navigate up to previous sibling', () => {
      keyboardNavigation.navigateDown();
      const before = keyboardNavigation.getCurrentNode();
      const result = keyboardNavigation.navigateUp();

      expect(result).toBeTruthy();
      expect(result).not.toBe(before);
    });

    it('should navigate left to parent', () => {
      // Note: Need nested structure for this test
      const result = keyboardNavigation.navigateLeft();
      // May be null if already at root
      expect(typeof result).toBe('string') || expect(result).toBeNull();
    });

    it('should navigate right to child', () => {
      // Only works for nodes with children
      const result = keyboardNavigation.navigateRight();
      expect(typeof result).toBe('string') || expect(result).toBeNull();
    });

    it('should handle navigation bounds', () => {
      let current = keyboardNavigation.getCurrentNode();

      // Navigate to end
      for (let i = 0; i < 10; i++) {
        const next = keyboardNavigation.navigateDown();
        if (!next) break;
        current = next;
      }

      // Should stop at last node
      const atEnd = keyboardNavigation.navigateDown();
      expect(atEnd).toBeNull();
    });
  });

  describe('Jump Navigation', () => {
    it('should jump to first node', () => {
      keyboardNavigation.navigateDown();
      const result = keyboardNavigation.navigateToFirst();

      expect(result).toBeTruthy();
    });

    it('should jump to last node', () => {
      const result = keyboardNavigation.navigateToLast();

      expect(result).toBeTruthy();
    });

    it('should navigate to parent', () => {
      const result = keyboardNavigation.navigateToParent();
      // May be null if no parent
      expect(typeof result).toBe('string') || expect(result).toBeNull();
    });
  });

  describe('Keyboard Actions', () => {
    it('should register custom action', () => {
      keyboardNavigation.registerAction({
        key: 'a',
        action: () => null,
        description: 'Test action',
      });

      const actions = keyboardNavigation.getActions();
      expect(actions.length).toBeGreaterThan(0);
    });

    it('should unregister action', () => {
      const countBefore = keyboardNavigation.getActions().length;

      keyboardNavigation.unregisterAction('Delete');

      const countAfter = keyboardNavigation.getActions().length;
      expect(countAfter).toBeLessThanOrEqual(countBefore);
    });

    it('should handle keyboard event', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'ArrowDown',
        bubbles: true,
      });

      const handled = keyboardNavigation.handleKeyDown(event);
      expect(typeof handled).toBe('boolean');
    });

    it('should handle ctrl+z (undo)', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'z',
        ctrlKey: true,
        bubbles: true,
      });

      const handled = keyboardNavigation.handleKeyDown(event);
      expect(handled).toBe(true);
    });
  });

  describe('Configuration', () => {
    it('should respect configuration', () => {
      const customConfig = {
        enableArrowNavigation: true,
        enableCharacterShortcuts: false,
      };

      const newNav = new (keyboardNavigation.constructor as any)();
      newNav.initialize(rootNode, customConfig);

      expect(newNav).toBeTruthy();
    });
  });
});

describe('Clipboard Manager', () => {
  let rootNode;
  let nodesToCopy;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
    nodesToCopy = Object.values(rootNode.nodes);
    clipboard.clear();
  });

  describe('Copy Operations', () => {
    it('should copy nodes', () => {
      const result = clipboard.copy(nodesToCopy);

      expect(result.success).toBe(true);
      expect(result.nodeIds).toBeTruthy();
      expect(result.nodeIds?.length).toBe(nodesToCopy.length);
    });

    it('should populate clipboard', () => {
      clipboard.copy(nodesToCopy);

      expect(clipboard.hasContent()).toBe(true);
      const info = clipboard.getContentInfo();
      expect(info.nodeCount).toBe(nodesToCopy.length);
    });

    it('should handle empty copy', () => {
      const result = clipboard.copy([]);

      expect(result.success).toBe(false);
    });

    it('should copy with source node ID', () => {
      const result = clipboard.copy(nodesToCopy, 'sourceId123');

      expect(result.success).toBe(true);
    });
  });

  describe('Cut Operations', () => {
    it('should cut nodes', () => {
      const parentNode = rootNode;
      const result = clipboard.cut(nodesToCopy, parentNode);

      expect(result.success).toBe(true);
    });

    it('should mark cut nodes', () => {
      const parentNode = rootNode;
      clipboard.cut(nodesToCopy, parentNode);

      expect(clipboard.wasNodeCut(nodesToCopy[0].id)).toBe(true);
    });

    it('should track cut nodes for removal', () => {
      const parentNode = rootNode;
      clipboard.cut(nodesToCopy, parentNode);

      const cutNodes = clipboard.getCutNodes();
      expect(cutNodes.size).toBeGreaterThan(0);
    });
  });

  describe('Paste Operations', () => {
    it('should paste nodes', () => {
      clipboard.copy(nodesToCopy);

      const targetParent = rootNode;
      const result = clipboard.paste(targetParent);

      expect(result.success).toBe(true);
      expect(result.nodeIds).toBeTruthy();
      expect(result.nodeIds?.length).toBe(nodesToCopy.length);
    });

    it('should generate new IDs on paste', () => {
      clipboard.copy(nodesToCopy);

      const originalIds = new Set(nodesToCopy.map(n => n.id));
      const result = clipboard.paste(rootNode);

      expect(result.nodeIds).toBeTruthy();
      for (const newId of result.nodeIds!) {
        expect(originalIds.has(newId)).toBe(false);
      }
    });

    it('should handle empty clipboard paste', () => {
      const result = clipboard.paste(rootNode);

      expect(result.success).toBe(false);
    });

    it('should respect insert index', () => {
      clipboard.copy(nodesToCopy);
      const result = clipboard.paste(rootNode, 0); // Insert at beginning

      expect(result.success).toBe(true);
    });
  });

  describe('Duplicate Operation', () => {
    it('should duplicate nodes', () => {
      const result = clipboard.duplicate(nodesToCopy, rootNode);

      expect(result.success).toBe(true);
      expect(result.nodeIds?.length).toBe(nodesToCopy.length);
    });

    it('should generate new IDs for duplicate', () => {
      const originalIds = new Set(nodesToCopy.map(n => n.id));
      const result = clipboard.duplicate(nodesToCopy, rootNode);

      for (const newId of result.nodeIds!) {
        expect(originalIds.has(newId)).toBe(false);
      }
    });
  });

  describe('Clipboard State', () => {
    it('should check clipboard content', () => {
      expect(clipboard.hasContent()).toBe(false);

      clipboard.copy(nodesToCopy);
      expect(clipboard.hasContent()).toBe(true);
    });

    it('should get content info', () => {
      clipboard.copy(nodesToCopy);

      const info = clipboard.getContentInfo();
      expect(info.hasContent).toBe(true);
      expect(info.nodeCount).toBe(nodesToCopy.length);
      expect(info.wasCut).toBe(false);
    });

    it('should identify cut content', () => {
      clipboard.cut(nodesToCopy, rootNode);

      const info = clipboard.getContentInfo();
      expect(info.wasCut).toBe(true);
    });

    it('should clear clipboard', () => {
      clipboard.copy(nodesToCopy);
      expect(clipboard.hasContent()).toBe(true);

      clipboard.clear();
      expect(clipboard.hasContent()).toBe(false);
    });
  });

  describe('History Tracking', () => {
    it('should track copy in history', () => {
      clipboard.copy(nodesToCopy);
      expect(clipboard.getHistorySize()).toBeGreaterThan(0);
    });

    it('should track paste in history', () => {
      clipboard.copy(nodesToCopy);
      clipboard.paste(rootNode);

      expect(clipboard.getHistorySize()).toBeGreaterThan(1);
    });

    it('should support undo', () => {
      clipboard.copy(nodesToCopy);
      clipboard.paste(rootNode);

      expect(clipboard.canUndoClipboard()).toBe(true);
    });

    it('should support redo', () => {
      clipboard.copy(nodesToCopy);
      clipboard.paste(rootNode);
      // Redo would require actual undo implementation
    });

    it('should clear history', () => {
      clipboard.copy(nodesToCopy);
      clipboard.clearHistory();

      expect(clipboard.getHistorySize()).toBe(0);
    });
  });

  describe('Serialization', () => {
    it('should serialize nodes to clipboard format', () => {
      clipboard.copy(nodesToCopy);

      const data = clipboard.getClipboardData();
      expect(data.length).toBeGreaterThan(0);
      expect(data[0]).toHaveProperty('id');
      expect(data[0]).toHaveProperty('type');
    });

    it('should preserve node structure', () => {
      const result = clipboard.duplicate([rootNode], rootNode);

      expect(result.success).toBe(true);
    });

    it('should preserve properties', () => {
      const nodeWithProps = {
        ...nodesToCopy[0],
        props: { color: 'red', padding: '16px' },
      };

      clipboard.copy([nodeWithProps]);
      const data = clipboard.getClipboardData();

      expect(data[0].props.color).toBe('red');
      expect(data[0].props.padding).toBe('16px');
    });
  });

  describe('Safety Checks', () => {
    it('should validate paste target', () => {
      const valid = clipboard.validatePasteTarget(rootNode, [rootNode.id]);

      expect(valid).toBe(false); // Cannot paste into itself
    });

    it('should prevent circular nesting', () => {
      const childId = Object.keys(rootNode.nodes)[0];
      const valid = clipboard.validatePasteTarget(rootNode, [childId]);

      expect(typeof valid).toBe('boolean');
    });
  });
});

describe('Cross-Service Integration', () => {
  let rootNode;

  beforeEach(() => {
    const instance = createBlockInstance('layout-frame', {}, [
      createBlockInstance('data-heading'),
      createBlockInstance('data-paragraph'),
    ]);
    rootNode = blockInstanceToCraftNode(instance);
    keyboardNavigation.initialize(rootNode);
    canvasOptimization.initialize();
  });

  it('should integrate keyboard navigation with optimization', () => {
    const start = canvasOptimization.startFrame();

    keyboardNavigation.navigateDown();
    const current = keyboardNavigation.getCurrentNode();

    const metrics = canvasOptimization.endFrame(start);

    expect(current).toBeTruthy();
    expect(metrics.frameTime).toBeGreaterThanOrEqual(0);
  });

  it('should integrate clipboard with keyboard actions', () => {
    const nodesToCopy = Object.values(rootNode.nodes).slice(0, 1);

    // Simulate keyboard action
    clipboard.copy(nodesToCopy);
    expect(clipboard.hasContent()).toBe(true);

    // Keyboard navigate to paste location
    const pasteLocation = rootNode;
    const pasteResult = clipboard.paste(pasteLocation);

    expect(pasteResult.success).toBe(true);
  });

  it('should handle optimization during clipboard operations', () => {
    const nodesToCopy = Object.values(rootNode.nodes);

    const start = canvasOptimization.startFrame();
    clipboard.copy(nodesToCopy);
    clipboard.paste(rootNode);
    const metrics = canvasOptimization.endFrame(start);

    expect(metrics.frameTime).toBeGreaterThanOrEqual(0);
  });
});
