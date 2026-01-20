/**
 * Editor State Store (Zustand)
 * Manages template data, selection, and history
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Template, TemplateSnapshot } from '@/types';

export interface EditorState {
  // Template data
  currentTemplate: Template | null;
  isDirty: boolean;
  
  // Selection
  selectedComponentId: string | null;
  selectedComponentPath: string[];
  selectedNodeId?: string;
  selectedNode?: any;
  
  // History (undo/redo)
  history: TemplateSnapshot[];
  historyIndex: number;
  maxHistorySize: number;
  
  // Loading state
  isLoading: boolean;
  loadError: string | null;
  
  // Actions
  setTemplate: (template: Template) => void;
  updateTemplate: (updates: Partial<Template>) => void;
  selectComponent: (id: string, path: string[]) => void;
  clearSelection: () => void;
  markDirty: () => void;
  markClean: () => void;
  
  // History actions
  pushToHistory: (snapshot: TemplateSnapshot) => void;
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;
  clearHistory: () => void;
  setMaxHistorySize: (size: number) => void;
  
  // Loading actions
  startLoading: () => void;
  finishLoading: () => void;
  setLoadError: (error: string | null) => void;
  
  // Reset
  reset: () => void;
}

const initialTemplate: Template = {
  id: '',
  name: 'Untitled Template',
  html: '',
  css: '',
  meta: {
    version: '2.0.0',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
};

export const useEditorStore = create<EditorState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentTemplate: initialTemplate,
        isDirty: false,
        selectedComponentId: null,
        selectedComponentPath: [],
        history: [],
        historyIndex: -1,
        maxHistorySize: 100,
        isLoading: false,
        loadError: null,
        
        // Template actions
        setTemplate: (template: Template) =>
          set({
            currentTemplate: template,
            isDirty: false,
            selectedComponentId: null,
          }),
        
        updateTemplate: (updates: Partial<Template>) =>
          set((state) => ({
            currentTemplate: state.currentTemplate
              ? {
                  ...state.currentTemplate,
                  ...updates,
                  meta: {
                    ...state.currentTemplate.meta,
                    updatedAt: new Date().toISOString(),
                  },
                }
              : null,
            isDirty: true,
          })),
        
        // Selection actions
        selectComponent: (id: string, path: string[]) =>
          set({
            selectedComponentId: id,
            selectedComponentPath: path,
          }),
        
        clearSelection: () =>
          set({
            selectedComponentId: null,
            selectedComponentPath: [],
          }),
        
        // Dirty state
        markDirty: () => set({ isDirty: true }),
        markClean: () => set({ isDirty: false }),
        
        // History actions
        pushToHistory: (snapshot: TemplateSnapshot) =>
          set((state) => {
            // Remove any history after current index
            const newHistory = state.history.slice(0, state.historyIndex + 1);
            newHistory.push(snapshot);
            
            // Limit history size
            if (newHistory.length > state.maxHistorySize) {
              newHistory.shift();
            }
            
            return {
              history: newHistory,
              historyIndex: newHistory.length - 1,
            };
          }),
        
        undo: () => {
          const state = get();
          if (state.historyIndex > 0) {
            const previousSnapshot = state.history[state.historyIndex - 1];
            set({
              currentTemplate: previousSnapshot.template,
              historyIndex: state.historyIndex - 1,
              isDirty: true,
            });
          }
        },
        
        redo: () => {
          const state = get();
          if (state.historyIndex < state.history.length - 1) {
            const nextSnapshot = state.history[state.historyIndex + 1];
            set({
              currentTemplate: nextSnapshot.template,
              historyIndex: state.historyIndex + 1,
              isDirty: true,
            });
          }
        },
        
        canUndo: () => get().historyIndex > 0,
        canRedo: () => get().historyIndex < get().history.length - 1,
        
        clearHistory: () =>
          set({
            history: [],
            historyIndex: -1,
          }),
        
        setMaxHistorySize: (size: number) =>
          set({ maxHistorySize: Math.max(10, Math.min(size, 500)) }),
        
        // Loading actions
        startLoading: () => set({ isLoading: true, loadError: null }),
        finishLoading: () => set({ isLoading: false }),
        setLoadError: (error: string | null) => set({ loadError: error }),
        
        // Reset
        reset: () =>
          set({
            currentTemplate: initialTemplate,
            isDirty: false,
            selectedComponentId: null,
            selectedComponentPath: [],
            history: [],
            historyIndex: -1,
            isLoading: false,
            loadError: null,
          }),
      }),
      {
        name: 'anki-template-designer-editor', // localStorage key
        version: 1,
        // Only persist these fields
        partialize: (state) => ({
          currentTemplate: state.currentTemplate,
          history: state.history,
          isDirty: state.isDirty,
        }),
        // Migration handler for future versions
        migrate: (persistedState: any, version: number) => {
          if (version === 0) {
            // v0 migration logic
          }
          return persistedState as EditorState;
        },
      },
    ),
    {
      name: 'EditorStore',
      enabled: process.env.NODE_ENV === 'development',
    },
  ),
);

