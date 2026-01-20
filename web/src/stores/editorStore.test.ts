/**
 * EditorStore Tests
 * Unit tests for editor state management
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useEditorStore } from '@stores/editorStore';
import { createMockTemplate } from '@tests/test-utils';

describe('EditorStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    useEditorStore.setState({
      currentTemplate: null,
      isDirty: false,
      selectedComponentId: null,
      selectedComponentPath: [],
      history: [],
      historyIndex: -1,
      isLoading: false,
      loadError: null,
    });
  });

  describe('Template Management', () => {
    it('should set a new template', () => {
      const template = createMockTemplate();

      useEditorStore.getState().setTemplate(template);

      const state = useEditorStore.getState();
      expect(state.currentTemplate).toEqual(template);
      expect(state.isDirty).toBe(false);
    });

    it('should update template properties', () => {
      const template = createMockTemplate();
      useEditorStore.getState().setTemplate(template);

      useEditorStore.getState().updateTemplate({ name: 'Updated Name' });

      const state = useEditorStore.getState();
      expect(state.currentTemplate?.name).toBe('Updated Name');
      expect(state.isDirty).toBe(true);
    });

    it('should mark template as dirty', () => {
      const template = createMockTemplate();
      useEditorStore.getState().setTemplate(template);

      useEditorStore.getState().markDirty();

      expect(useEditorStore.getState().isDirty).toBe(true);
    });

    it('should mark template as clean', () => {
      const template = createMockTemplate();
      useEditorStore.getState().setTemplate(template);
      useEditorStore.getState().markDirty();

      useEditorStore.getState().markClean();

      expect(useEditorStore.getState().isDirty).toBe(false);
    });
  });

  describe('Selection Management', () => {
    it('should select a component', () => {
      useEditorStore.getState().selectComponent('comp-1', ['ROOT', 'comp-1']);

      const state = useEditorStore.getState();
      expect(state.selectedComponentId).toBe('comp-1');
      expect(state.selectedComponentPath).toEqual(['ROOT', 'comp-1']);
    });

    it('should clear selection', () => {
      useEditorStore.getState().selectComponent('comp-1', ['ROOT', 'comp-1']);

      useEditorStore.getState().clearSelection();

      const state = useEditorStore.getState();
      expect(state.selectedComponentId).toBeNull();
      expect(state.selectedComponentPath).toEqual([]);
    });
  });

  describe('History Management', () => {
    it('should add to history', () => {
      const snapshot = {
        id: 'snap-1',
        timestamp: Date.now(),
        template: createMockTemplate(),
        description: 'Initial',
      };

      useEditorStore.getState().pushToHistory(snapshot);

      const state = useEditorStore.getState();
      expect(state.history).toHaveLength(1);
      expect(state.historyIndex).toBe(0);
    });

    it('should support undo', () => {
      const template1 = createMockTemplate();
      const template2 = { ...createMockTemplate(), name: 'Template 2' };

      useEditorStore.getState().pushToHistory({
        id: 'snap-1',
        timestamp: Date.now(),
        template: template1,
        description: 'First',
      });

      useEditorStore.getState().pushToHistory({
        id: 'snap-2',
        timestamp: Date.now() + 1000,
        template: template2,
        description: 'Second',
      });

      useEditorStore.getState().undo();

      const state = useEditorStore.getState();
      expect(state.historyIndex).toBe(0);
      expect(state.currentTemplate?.name).toBe(template1.name);
    });
  });

  describe('Loading State', () => {
    it('should manage loading state', () => {
      useEditorStore.getState().startLoading();

      expect(useEditorStore.getState().isLoading).toBe(true);

      useEditorStore.getState().finishLoading();

      expect(useEditorStore.getState().isLoading).toBe(false);
    });

    it('should handle load errors', () => {
      const error = 'Template not found';

      useEditorStore.getState().setLoadError(error);

      expect(useEditorStore.getState().loadError).toBe(error);

      useEditorStore.getState().setLoadError(null);

      expect(useEditorStore.getState().loadError).toBeNull();
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', () => {
      const template = createMockTemplate();
      useEditorStore.getState().setTemplate(template);
      useEditorStore.getState().markDirty();

      useEditorStore.getState().reset();

      const state = useEditorStore.getState();
      expect(state.currentTemplate?.name).toBe('Untitled Template');
      expect(state.isDirty).toBe(false);
      expect(state.selectedComponentId).toBeNull();
    });
  });
});
