/**
 * Anki State Store (Zustand)
 * Manages Anki-specific configuration and data
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { AnkiField, AnkiBehavior, AnkiConfig } from '@/types';

export interface AnkiState {
  // Configuration
  config: AnkiConfig | null;
  
  // Data
  fields: AnkiField[];
  behaviors: AnkiBehavior[];
  
  // UI state
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Anki integration
  isConnected: boolean;
  lastSyncTime: number | null;
  
  // Actions
  setConfig: (config: AnkiConfig) => void;
  setFields: (fields: AnkiField[]) => void;
  addField: (field: AnkiField) => void;
  removeField: (fieldName: string) => void;
  updateField: (fieldName: string, field: Partial<AnkiField>) => void;
  
  setBehaviors: (behaviors: AnkiBehavior[]) => void;
  addBehavior: (behavior: AnkiBehavior) => void;
  removeBehavior: (behaviorName: string) => void;
  updateBehavior: (behaviorName: string, behavior: Partial<AnkiBehavior>) => void;
  
  initialize: (config: AnkiConfig, fields: AnkiField[], behaviors: AnkiBehavior[]) => void;
  
  // Connection actions
  setConnected: (connected: boolean) => void;
  updateLastSyncTime: () => void;
  
  // Loading/error
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Reset
  reset: () => void;
}

const defaultConfig: AnkiConfig = {
  ankiVersion: 'unknown',
  notetypeId: 0,
  notetypeName: 'Default',
  isDroidCompatible: true,
};

const defaultFields: AnkiField[] = [
  { name: 'Front', description: 'Front of the card' },
  { name: 'Back', description: 'Back of the card' },
];

export const useAnkiStore = create<AnkiState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        config: defaultConfig,
        fields: defaultFields,
        behaviors: [],
        isInitialized: false,
        isLoading: false,
        error: null,
        isConnected: false,
        lastSyncTime: null,
        
        // Configuration actions
        setConfig: (config: AnkiConfig) => set({ config }),
        
        // Field actions
        setFields: (fields: AnkiField[]) => set({ fields }),
        
        addField: (field: AnkiField) =>
          set((state) => ({
            fields: [...state.fields, field],
          })),
        
        removeField: (fieldName: string) =>
          set((state) => ({
            fields: state.fields.filter((f) => f.name !== fieldName),
          })),
        
        updateField: (fieldName: string, field: Partial<AnkiField>) =>
          set((state) => ({
            fields: state.fields.map((f) =>
              f.name === fieldName ? { ...f, ...field } : f,
            ),
          })),
        
        // Behavior actions
        setBehaviors: (behaviors: AnkiBehavior[]) => set({ behaviors }),
        
        addBehavior: (behavior: AnkiBehavior) =>
          set((state) => ({
            behaviors: [...state.behaviors, behavior],
          })),
        
        removeBehavior: (behaviorName: string) =>
          set((state) => ({
            behaviors: state.behaviors.filter((b) => b.name !== behaviorName),
          })),
        
        updateBehavior: (behaviorName: string, behavior: Partial<AnkiBehavior>) =>
          set((state) => ({
            behaviors: state.behaviors.map((b) =>
              b.name === behaviorName ? { ...b, ...behavior } : b,
            ),
          })),
        
        // Initialization
        initialize: (config: AnkiConfig, fields: AnkiField[], behaviors: AnkiBehavior[]) =>
          set({
            config,
            fields,
            behaviors,
            isInitialized: true,
            isConnected: true,
          }),
        
        // Connection actions
        setConnected: (connected: boolean) => set({ isConnected: connected }),
        
        updateLastSyncTime: () => set({ lastSyncTime: Date.now() }),
        
        // Loading/error actions
        setLoading: (loading: boolean) => set({ isLoading: loading }),
        
        setError: (error: string | null) => set({ error }),
        
        // Reset
        reset: () =>
          set({
            config: defaultConfig,
            fields: defaultFields,
            behaviors: [],
            isInitialized: false,
            isLoading: false,
            error: null,
            isConnected: false,
            lastSyncTime: null,
          }),
      }),
      {
        name: 'anki-template-designer-anki', // localStorage key
        version: 1,
        // Only persist these fields
        partialize: (state) => ({
          config: state.config,
          fields: state.fields,
          behaviors: state.behaviors,
          isInitialized: state.isInitialized,
        }),
        // Migration handler
        migrate: (persistedState: any, version: number) => {
          if (version === 0) {
            // v0 migration logic
          }
          return persistedState as AnkiState;
        },
      },
    ),
    {
      name: 'AnkiStore',
      enabled: process.env.NODE_ENV === 'development',
    },
  ),
);

