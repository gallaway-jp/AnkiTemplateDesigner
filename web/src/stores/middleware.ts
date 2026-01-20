/**
 * Zustand Store Middleware and Utilities
 * Provides localStorage persistence, devtools integration, and common patterns
 */

import { StateCreator, StoreMutatorIdentifier } from 'zustand';
import { devtools, persist, PersistOptions } from 'zustand/middleware';

/**
 * Logger middleware - logs all state changes
 */
export const createLoggerMiddleware =
  (name: string) =>
  <T,>(f: StateCreator<T>) => (set: any, get: any, store: any) => {
    const setState = set;
    const wrappedSet = (partial: any, replace?: any) => {
      if (process.env.NODE_ENV === 'development') {
        console.group(`[${name}] State Update`);
        console.log('Previous State:', get());
        console.log('Update:', partial);
        console.groupEnd();
      }
      return setState(partial, replace);
    };
    return f(wrappedSet, get, store);
  };

/**
 * Persist options for localStorage
 */
export const createPersistConfig = <T extends Record<string, any>>(
  name: string,
  allowlist?: (keyof T)[],
): PersistOptions<T, T> => ({
  name: `anki-template-designer-${name}`,
  storage: {
    getItem: (key: string) => {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    },
    setItem: (key: string, value: any) => {
      localStorage.setItem(key, JSON.stringify(value));
    },
    removeItem: (key: string) => {
      localStorage.removeItem(key);
    },
  },
  // Only persist specific fields
  ...(allowlist && { partialize: (state) => {
    const result = {} as Record<string, any>;
    allowlist.forEach((key) => {
      result[key as string] = (state as any)[key];
    });
    return result as T;
  }}),
  // Version for migrations
  version: 1,
  // Migration handler
  migrate: (persistedState: any, version: number) => {
    if (version === 0) {
      // v0 migration logic (if needed)
    }
    return persistedState as T;
  },
});

/**
 * Storage interface for type safety
 */
export interface StorageOptions {
  key: string;
  version?: number;
  migrate?: (persistedState: any, version: number) => any;
}

/**
 * Custom hydration check to avoid hydration mismatch in Next.js
 */
let hydrated = false;

export const setHydrated = () => {
  hydrated = true;
};

export const isHydrated = () => hydrated;

/**
 * Hook to check if store is hydrated
 */
export const useIsHydrated = () => {
  const [isHydrated, setIsHydrated] = React.useState(false);
  
  React.useEffect(() => {
    setIsHydrated(true);
  }, []);
  
  return isHydrated;
};

/**
 * Store subscription utilities
 */
export interface Subscription<T> {
  unsubscribe: () => void;
}

/**
 * Watch a specific field in the store
 */
export const watchField = <T, K extends keyof T>(
  store: { getState: () => T; subscribe: (cb: (state: T) => void) => () => void },
  field: K,
  callback: (newValue: T[K], oldValue: T[K]) => void,
): Subscription<T> => {
  let previousValue = store.getState()[field];
  
  const unsubscribe = store.subscribe((state: T) => {
    const newValue = state[field];
    if (newValue !== previousValue) {
      callback(newValue, previousValue);
      previousValue = newValue;
    }
  });
  
  return { unsubscribe };
};

/**
 * Batch multiple state updates
 */
export const batchUpdates = <T>(
  store: any,
  updates: Array<(draft: any) => void>,
) => {
  const state = store.getState();
  const newState = { ...state };
  
  updates.forEach((update) => {
    update(newState);
  });
  
  return newState;
};

/**
 * Reset store to initial state with confirmation
 */
export const resetStoreWithConfirmation = (
  storeName: string,
  resetFn: () => void,
  message = `Are you sure you want to reset ${storeName}? This cannot be undone.`,
): void => {
  if (typeof window !== 'undefined' && window.confirm(message)) {
    resetFn();
  }
};

/**
 * Export store state to JSON
 */
export const exportStoreState = <T,>(
  store: { getState: () => T },
  filename: string,
): void => {
  const state = store.getState();
  const json = JSON.stringify(state, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

/**
 * Import store state from JSON
 */
export const importStoreState = <T,>(
  store: any,
  file: File,
): Promise<T> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const state = JSON.parse(e.target?.result as string);
        store.setState(state);
        resolve(state);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
};

/**
 * Middleware composition helper
 */
export type WithPersist<T> = T & { _persist?: { version: number } };

/**
 * Create a store with persistence and devtools
 */
export const createPersistentStore = <
  T,
  M1 extends [StoreMutatorIdentifier, unknown] = never,
  M2 extends [StoreMutatorIdentifier, unknown] = never,
>(
  name: string,
  initializer: StateCreator<T, [['zustand/devtools', never], ['zustand/persist', T]]>,
  persistConfig?: Partial<PersistOptions<T, T>>,
) => {
  return devtools(
    persist(initializer, {
      name: `anki-template-designer-${name}`,
      version: 1,
      ...persistConfig,
    }),
    {
      name: `AnkiDesigner/${name}`,
      enabled: process.env.NODE_ENV === 'development',
    },
  );
};

/**
 * Debug helper to log state changes
 */
export const enableStoreDebugging = <T,>(
  store: any,
  name: string,
): void => {
  if (process.env.NODE_ENV === 'development') {
    store.subscribe((state: T) => {
      console.log(`[${name}]`, state);
    });
  }
};

/**
 * Validate state before persistence
 */
export const validateState = <T,>(
  state: any,
  schema: Record<string, any>,
): boolean => {
  for (const [key, validator] of Object.entries(schema)) {
    if (!validator(state[key])) {
      console.warn(`State validation failed for ${key}:`, state[key]);
      return false;
    }
  }
  return true;
};

// Import React for useIsHydrated
import React from 'react';
