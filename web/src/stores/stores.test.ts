/**
 * Zustand Stores Unit Tests
 * Tests for editorStore, ankiStore, and uiStore
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useEditorStore } from './editorStore';
import { useAnkiStore } from './ankiStore';
import { useUiStore } from './uiStore';
import { Template, TemplateSnapshot } from '@types';

// ============================================================================
// Editor Store Tests
// ============================================================================

describe('useEditorStore', () => {
  beforeEach(() => {
    useEditorStore.setState({
      currentTemplate: null,
      isDirty: false,
      selectedComponentId: null,
      selectedComponentPath: [],
      history: [],
      historyIndex: -1,
      maxHistorySize: 100,
      isLoading: false,
      loadError: null,
    });
  });

  describe('Template Management', () => {
    it('should set a template', () => {
      const template: Template = {
        id: 'tpl-1',
        name: 'Test Template',
        html: '<div>Test</div>',
        css: 'body { color: black; }',
        meta: {
          version: '1.0',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      };

      useEditorStore.getState().setTemplate(template);
      expect(useEditorStore.getState().currentTemplate).toEqual(template);
      expect(useEditorStore.getState().isDirty).toBe(false);
    });

    it('should update template', () => {
      const template: Template = {
        id: 'tpl-1',
        name: 'Test',
        html: '<div>Test</div>',
        css: '',
        meta: {
          version: '1.0',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      };

      useEditorStore.getState().setTemplate(template);
      useEditorStore.getState().updateTemplate({ name: 'Updated Test' });

      const updated = useEditorStore.getState().currentTemplate;
      expect(updated?.name).toBe('Updated Test');
      expect(useEditorStore.getState().isDirty).toBe(true);
    });

    it('should mark dirty and clean', () => {
      useEditorStore.getState().markDirty();
      expect(useEditorStore.getState().isDirty).toBe(true);

      useEditorStore.getState().markClean();
      expect(useEditorStore.getState().isDirty).toBe(false);
    });
  });

  describe('Selection Management', () => {
    it('should select a component', () => {
      useEditorStore.getState().selectComponent('comp-1', ['parent', 'child']);

      const state = useEditorStore.getState();
      expect(state.selectedComponentId).toBe('comp-1');
      expect(state.selectedComponentPath).toEqual(['parent', 'child']);
    });

    it('should clear selection', () => {
      useEditorStore.getState().selectComponent('comp-1', ['parent']);
      useEditorStore.getState().clearSelection();

      const state = useEditorStore.getState();
      expect(state.selectedComponentId).toBeNull();
      expect(state.selectedComponentPath).toEqual([]);
    });
  });

  describe('History Management', () => {
    const createSnapshot = (name: string): TemplateSnapshot => ({
      id: `snap-${name}`,
      timestamp: Date.now(),
      template: {
        id: 'tpl-1',
        name,
        html: `<div>${name}</div>`,
        css: '',
        meta: {
          version: '1.0',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      },
      description: `Snapshot ${name}`,
    });

    it('should push to history', () => {
      const snap1 = createSnapshot('v1');
      const snap2 = createSnapshot('v2');

      useEditorStore.getState().pushToHistory(snap1);
      useEditorStore.getState().pushToHistory(snap2);

      const state = useEditorStore.getState();
      expect(state.history).toHaveLength(2);
      expect(state.historyIndex).toBe(1);
    });

    it('should undo', () => {
      const snap1 = createSnapshot('v1');
      const snap2 = createSnapshot('v2');

      useEditorStore.getState().pushToHistory(snap1);
      useEditorStore.getState().pushToHistory(snap2);
      useEditorStore.getState().undo();

      const state = useEditorStore.getState();
      expect(state.currentTemplate?.name).toBe('v1');
      expect(state.historyIndex).toBe(0);
    });

    it('should redo', () => {
      const snap1 = createSnapshot('v1');
      const snap2 = createSnapshot('v2');

      useEditorStore.getState().pushToHistory(snap1);
      useEditorStore.getState().pushToHistory(snap2);
      useEditorStore.getState().undo();
      useEditorStore.getState().redo();

      const state = useEditorStore.getState();
      expect(state.currentTemplate?.name).toBe('v2');
      expect(state.historyIndex).toBe(1);
    });

    it('should know when undo/redo is available', () => {
      const snap1 = createSnapshot('v1');
      const snap2 = createSnapshot('v2');

      useEditorStore.getState().pushToHistory(snap1);
      expect(useEditorStore.getState().canUndo()).toBe(true);
      expect(useEditorStore.getState().canRedo()).toBe(false);

      useEditorStore.getState().pushToHistory(snap2);
      useEditorStore.getState().undo();

      expect(useEditorStore.getState().canUndo()).toBe(true);
      expect(useEditorStore.getState().canRedo()).toBe(true);
    });

    it('should clear history after undo when new snapshot pushed', () => {
      const snap1 = createSnapshot('v1');
      const snap2 = createSnapshot('v2');
      const snap3 = createSnapshot('v3');

      useEditorStore.getState().pushToHistory(snap1);
      useEditorStore.getState().pushToHistory(snap2);
      useEditorStore.getState().undo();
      useEditorStore.getState().pushToHistory(snap3);

      const state = useEditorStore.getState();
      expect(state.history).toHaveLength(2);
      expect(state.history[1].template.name).toBe('v3');
    });

    it('should respect max history size', () => {
      useEditorStore.getState().setMaxHistorySize(5);

      for (let i = 0; i < 10; i++) {
        useEditorStore.getState().pushToHistory(createSnapshot(`v${i}`));
      }

      const state = useEditorStore.getState();
      expect(state.history.length).toBeLessThanOrEqual(5);
    });

    it('should clear history', () => {
      const snap1 = createSnapshot('v1');
      useEditorStore.getState().pushToHistory(snap1);
      useEditorStore.getState().clearHistory();

      const state = useEditorStore.getState();
      expect(state.history).toHaveLength(0);
      expect(state.historyIndex).toBe(-1);
    });
  });

  describe('Loading State', () => {
    it('should manage loading state', () => {
      useEditorStore.getState().startLoading();
      expect(useEditorStore.getState().isLoading).toBe(true);

      useEditorStore.getState().finishLoading();
      expect(useEditorStore.getState().isLoading).toBe(false);
    });

    it('should set and clear load error', () => {
      const error = 'Failed to load template';
      useEditorStore.getState().setLoadError(error);
      expect(useEditorStore.getState().loadError).toBe(error);

      useEditorStore.getState().setLoadError(null);
      expect(useEditorStore.getState().loadError).toBeNull();
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', () => {
      useEditorStore.getState().markDirty();
      useEditorStore.getState().selectComponent('comp-1', ['parent']);
      useEditorStore.getState().reset();

      const state = useEditorStore.getState();
      expect(state.isDirty).toBe(false);
      expect(state.selectedComponentId).toBeNull();
      expect(state.history).toHaveLength(0);
    });
  });
});

// ============================================================================
// Anki Store Tests
// ============================================================================

describe('useAnkiStore', () => {
  beforeEach(() => {
    useAnkiStore.setState({
      config: null,
      fields: [],
      behaviors: [],
      isInitialized: false,
      isLoading: false,
      error: null,
      isConnected: false,
      lastSyncTime: null,
    });
  });

  describe('Configuration', () => {
    it('should set config', () => {
      const config = {
        ankiVersion: '2.1.54',
        notetypeId: 123,
        notetypeName: 'Basic',
        isDroidCompatible: true,
      };

      useAnkiStore.getState().setConfig(config);
      expect(useAnkiStore.getState().config).toEqual(config);
    });
  });

  describe('Field Management', () => {
    it('should set fields', () => {
      const fields = [
        { name: 'Front', description: 'Front' },
        { name: 'Back', description: 'Back' },
      ];

      useAnkiStore.getState().setFields(fields);
      expect(useAnkiStore.getState().fields).toEqual(fields);
    });

    it('should add field', () => {
      useAnkiStore.getState().setFields([]);
      useAnkiStore.getState().addField({ name: 'Extra', description: 'Extra field' });

      expect(useAnkiStore.getState().fields).toHaveLength(1);
      expect(useAnkiStore.getState().fields[0].name).toBe('Extra');
    });

    it('should remove field', () => {
      useAnkiStore.getState().setFields([
        { name: 'Front', description: 'Front' },
        { name: 'Back', description: 'Back' },
      ]);

      useAnkiStore.getState().removeField('Front');
      const fields = useAnkiStore.getState().fields;
      expect(fields).toHaveLength(1);
      expect(fields[0].name).toBe('Back');
    });

    it('should update field', () => {
      useAnkiStore.getState().setFields([
        { name: 'Front', description: 'Front side' },
      ]);

      useAnkiStore.getState().updateField('Front', { description: 'Front of card' });

      const field = useAnkiStore.getState().fields[0];
      expect(field.description).toBe('Front of card');
    });
  });

  describe('Behavior Management', () => {
    it('should add behavior', () => {
      useAnkiStore.getState().setBehaviors([]);
      useAnkiStore.getState().addBehavior({ name: 'reveal', description: 'Reveal answer' });

      expect(useAnkiStore.getState().behaviors).toHaveLength(1);
    });

    it('should remove behavior', () => {
      useAnkiStore.getState().setBehaviors([
        { name: 'reveal', description: 'Reveal' },
        { name: 'mark', description: 'Mark' },
      ]);

      useAnkiStore.getState().removeBehavior('reveal');
      expect(useAnkiStore.getState().behaviors).toHaveLength(1);
    });
  });

  describe('Connection', () => {
    it('should set connected state', () => {
      useAnkiStore.getState().setConnected(true);
      expect(useAnkiStore.getState().isConnected).toBe(true);
    });

    it('should update last sync time', () => {
      useAnkiStore.getState().updateLastSyncTime();
      expect(useAnkiStore.getState().lastSyncTime).not.toBeNull();
    });
  });
});

// ============================================================================
// UI Store Tests
// ============================================================================

describe('useUiStore', () => {
  beforeEach(() => {
    useUiStore.setState({
      panels: { blocks: true, properties: true, layers: false, history: false },
      sidebarWidth: 300,
      sidebarCollapsed: false,
      theme: 'dark',
      zoomLevel: 100,
      notifications: [],
    });
  });

  describe('Panel Management', () => {
    it('should toggle panel', () => {
      useUiStore.getState().togglePanel('layers');
      expect(useUiStore.getState().panels.layers).toBe(true);

      useUiStore.getState().togglePanel('layers');
      expect(useUiStore.getState().panels.layers).toBe(false);
    });

    it('should set panel visibility', () => {
      useUiStore.getState().setPanelVisibility('properties', false);
      expect(useUiStore.getState().panels.properties).toBe(false);
    });

    it('should show all panels', () => {
      useUiStore.getState().hideAllPanels();
      useUiStore.getState().showAllPanels();

      const panels = useUiStore.getState().panels;
      expect(panels.blocks).toBe(true);
      expect(panels.properties).toBe(true);
      expect(panels.layers).toBe(true);
      expect(panels.history).toBe(true);
    });
  });

  describe('Layout Management', () => {
    it('should set sidebar width within bounds', () => {
      useUiStore.getState().setSidebarWidth(400);
      expect(useUiStore.getState().sidebarWidth).toBe(400);

      useUiStore.getState().setSidebarWidth(100);
      expect(useUiStore.getState().sidebarWidth).toBe(200);

      useUiStore.getState().setSidebarWidth(600);
      expect(useUiStore.getState().sidebarWidth).toBe(500);
    });

    it('should toggle sidebar collapse', () => {
      useUiStore.getState().toggleSidebarCollapse();
      expect(useUiStore.getState().sidebarCollapsed).toBe(true);

      useUiStore.getState().toggleSidebarCollapse();
      expect(useUiStore.getState().sidebarCollapsed).toBe(false);
    });
  });

  describe('Theme Management', () => {
    it('should set theme', () => {
      useUiStore.getState().setTheme('light');
      expect(useUiStore.getState().theme).toBe('light');
    });

    it('should toggle theme', () => {
      useUiStore.getState().setTheme('light');
      useUiStore.getState().toggleTheme();
      expect(useUiStore.getState().theme).toBe('dark');

      useUiStore.getState().toggleTheme();
      expect(useUiStore.getState().theme).toBe('auto');
    });
  });

  describe('Zoom Management', () => {
    it('should set zoom level within bounds', () => {
      useUiStore.getState().setZoomLevel(150);
      expect(useUiStore.getState().zoomLevel).toBe(150);

      useUiStore.getState().setZoomLevel(30);
      expect(useUiStore.getState().zoomLevel).toBe(50);

      useUiStore.getState().setZoomLevel(250);
      expect(useUiStore.getState().zoomLevel).toBe(200);
    });

    it('should zoom in and out', () => {
      useUiStore.getState().resetZoom();
      useUiStore.getState().zoomIn();
      expect(useUiStore.getState().zoomLevel).toBe(110);

      useUiStore.getState().zoomOut();
      expect(useUiStore.getState().zoomLevel).toBe(100);
    });

    it('should reset zoom', () => {
      useUiStore.getState().setZoomLevel(150);
      useUiStore.getState().resetZoom();
      expect(useUiStore.getState().zoomLevel).toBe(100);
    });
  });

  describe('Notification Management', () => {
    it('should add notification', (done) => {
      useUiStore.getState().addNotification('Test message', 'info', 100);

      const notif = useUiStore.getState().notifications[0];
      expect(notif.message).toBe('Test message');
      expect(notif.type).toBe('info');

      // Wait for auto-removal
      setTimeout(() => {
        expect(useUiStore.getState().notifications).toHaveLength(0);
        done();
      }, 150);
    });

    it('should remove notification', () => {
      useUiStore.getState().addNotification('Test', 'info', 0);
      const id = useUiStore.getState().notifications[0].id;

      useUiStore.getState().removeNotification(id);
      expect(useUiStore.getState().notifications).toHaveLength(0);
    });

    it('should clear all notifications', () => {
      useUiStore.getState().addNotification('Test 1', 'info', 0);
      useUiStore.getState().addNotification('Test 2', 'error', 0);

      useUiStore.getState().clearNotifications();
      expect(useUiStore.getState().notifications).toHaveLength(0);
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', () => {
      useUiStore.getState().setTheme('light');
      useUiStore.getState().setPanelVisibility('layers', true);
      useUiStore.getState().setZoomLevel(150);

      useUiStore.getState().reset();

      const state = useUiStore.getState();
      expect(state.theme).toBe('dark');
      expect(state.panels.layers).toBe(false);
      expect(state.zoomLevel).toBe(100);
    });
  });
});
