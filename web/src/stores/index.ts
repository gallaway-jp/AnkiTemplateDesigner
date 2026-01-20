/**
 * Central store exports
 * Import all stores from this file
 */

export { useEditorStore, useEditorStore as editorStore } from './editorStore';
export { useAnkiStore, useAnkiStore as ankiStore } from './ankiStore';
export { useUiStore, useUiStore as uiStore } from './uiStore';

// Middleware and utilities
export {
  createLoggerMiddleware,
  createPersistConfig,
  setHydrated,
  isHydrated,
  useIsHydrated,
  watchField,
  batchUpdates,
  resetStoreWithConfirmation,
  exportStoreState,
  importStoreState,
  createPersistentStore,
  enableStoreDebugging,
  validateState,
} from './middleware';

export type {
  StorageOptions,
  Subscription,
} from './middleware';

// Type exports for store states
export type { EditorState } from './editorStore';
export type { AnkiState } from './ankiStore';
export type { UiState } from './uiStore';
