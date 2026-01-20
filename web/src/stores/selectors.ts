/**
 * Zustand Store Selectors
 * Optimized selectors to reduce re-renders and improve performance
 * Groups related state together to minimize subscription overhead
 */

import { useEditorStore } from './editorStore';
import { useAnkiStore } from './ankiStore';
import { useUiStore } from './uiStore';
import { shallow } from 'zustand/react';

/**
 * Editor state selector - groups template, dirty flag, and history actions
 * Only triggers re-render if one of these values actually changes
 */
export const useEditorState = () => 
  useEditorStore((state) => ({
    currentTemplate: state.currentTemplate,
    isDirty: state.isDirty,
    selectedComponentId: state.selectedComponentId,
    selectedComponentPath: state.selectedComponentPath,
    canUndo: state.canUndo(),
    canRedo: state.canRedo(),
    isLoading: state.isLoading,
    loadError: state.loadError,
  }), shallow);

/**
 * Editor actions selector - groups all template manipulation actions
 * Stable across renders, only update when store methods change
 */
export const useEditorActions = () =>
  useEditorStore((state) => ({
    setTemplate: state.setTemplate,
    updateTemplate: state.updateTemplate,
    selectComponent: state.selectComponent,
    clearSelection: state.clearSelection,
    markDirty: state.markDirty,
    markClean: state.markClean,
    undo: state.undo,
    redo: state.redo,
    pushToHistory: state.pushToHistory,
  }), shallow);

/**
 * Anki fields selector - groups field list and methods
 */
export const useAnkiFields = () =>
  useAnkiStore((state) => ({
    fields: state.fields,
    behaviors: state.behaviors,
    notetype: state.notetype,
    isDroidCompatible: state.isDroidCompatible,
  }), shallow);

/**
 * Anki actions selector - groups field manipulation methods
 */
export const useAnkiActions = () =>
  useAnkiStore((state) => ({
    initialize: state.initialize,
    updateFields: state.updateFields,
    updateBehaviors: state.updateBehaviors,
  }), shallow);

/**
 * UI settings selector - groups all UI-related state
 */
export const useUISettings = () =>
  useUiStore((state) => ({
    activePanels: state.activePanels,
    theme: state.theme,
    sidebarWidth: state.sidebarWidth,
    zoomLevel: state.zoomLevel,
    showGrid: state.showGrid,
    showRulers: state.showRulers,
  }), shallow);

/**
 * UI actions selector - groups all UI manipulation methods
 */
export const useUIActions = () =>
  useUiStore((state) => ({
    togglePanel: state.togglePanel,
    setTheme: state.setTheme,
    setSidebarWidth: state.setSidebarWidth,
    setZoomLevel: state.setZoomLevel,
    resetUI: state.resetUI,
  }), shallow);

/**
 * Selection-only selector - for components that only need selection info
 */
export const useEditorSelection = () =>
  useEditorStore((state) => ({
    selectedComponentId: state.selectedComponentId,
    selectedComponentPath: state.selectedComponentPath,
  }), shallow);

/**
 * Template-only selector - for components that only need template
 */
export const useCurrentTemplate = () =>
  useEditorStore((state) => state.currentTemplate);

/**
 * Dirty flag selector - for components that only need dirty state
 */
export const useIsDirty = () =>
  useEditorStore((state) => state.isDirty);

/**
 * Undo/Redo capability selector - for toolbar components
 */
export const useHistoryCapabilities = () =>
  useEditorStore((state) => ({
    canUndo: state.canUndo(),
    canRedo: state.canRedo(),
  }), shallow);

/**
 * Panel visibility selector - for layout components
 */
export const useActivePanels = () =>
  useUiStore((state) => state.activePanels);

/**
 * Theme selector - for style/theme components
 */
export const useTheme = () =>
  useUiStore((state) => state.theme);
