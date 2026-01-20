/**
 * UI State Store (Zustand)
 * Manages UI-related state (panels, theme, layout)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface PanelVisibility {
  blocks: boolean;
  properties: boolean;
  layers: boolean;
  history: boolean;
}

export interface UiState {
  // Panel visibility
  panels: PanelVisibility;
  
  // Layout
  sidebarWidth: number;
  sidebarCollapsed: boolean;
  
  // Theme
  theme: 'light' | 'dark' | 'auto';
  
  // Zoom
  zoomLevel: number;
  
  // Notifications
  notifications: Array<{
    id: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    duration?: number;
  }>;
  
  // Actions - Panels
  togglePanel: (panel: keyof PanelVisibility) => void;
  setPanelVisibility: (panel: keyof PanelVisibility, visible: boolean) => void;
  showAllPanels: () => void;
  hideAllPanels: () => void;
  
  // Actions - Layout
  setSidebarWidth: (width: number) => void;
  toggleSidebarCollapse: () => void;
  
  // Actions - Theme
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  toggleTheme: () => void;
  
  // Actions - Zoom
  setZoomLevel: (level: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  
  // Actions - Notifications
  addNotification: (
    message: string,
    type: 'info' | 'success' | 'warning' | 'error',
    duration?: number
  ) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Reset
  reset: () => void;
}

const defaultPanels: PanelVisibility = {
  blocks: true,
  properties: true,
  layers: false,
  history: false,
};

export const useUiStore = create<UiState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        panels: defaultPanels,
        sidebarWidth: 300,
        sidebarCollapsed: false,
        theme: 'dark',
        zoomLevel: 100,
        notifications: [],
        
        // Panel actions
        togglePanel: (panel: keyof PanelVisibility) =>
          set((state) => ({
            panels: {
              ...state.panels,
              [panel]: !state.panels[panel],
            },
          })),
        
        setPanelVisibility: (panel: keyof PanelVisibility, visible: boolean) =>
          set((state) => ({
            panels: {
              ...state.panels,
              [panel]: visible,
            },
          })),
        
        showAllPanels: () =>
          set({
            panels: {
              blocks: true,
              properties: true,
              layers: true,
              history: true,
            },
          }),
        
        hideAllPanels: () =>
          set({
            panels: {
              blocks: false,
              properties: false,
              layers: false,
              history: false,
            },
          }),
        
        // Layout actions
        setSidebarWidth: (width: number) =>
          set({
            sidebarWidth: Math.max(200, Math.min(width, 500)),
          }),
        
        toggleSidebarCollapse: () =>
          set((state) => ({
            sidebarCollapsed: !state.sidebarCollapsed,
          })),
        
        // Theme actions
        setTheme: (theme: 'light' | 'dark' | 'auto') => {
          set({ theme });
          // Apply theme to document
          if (typeof document !== 'undefined') {
            document.documentElement.setAttribute('data-theme', theme);
            
            // Handle 'auto' theme
            if (theme === 'auto') {
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
            }
          }
        },
        
        toggleTheme: () => {
          const state = get();
          const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];
          const currentIndex = themes.indexOf(state.theme);
          const newTheme = themes[(currentIndex + 1) % themes.length];
          get().setTheme(newTheme);
        },
        
        // Zoom actions
        setZoomLevel: (level: number) =>
          set({
            zoomLevel: Math.max(50, Math.min(level, 200)),
          }),
        
        zoomIn: () => {
          const state = get();
          const newLevel = state.zoomLevel + 10;
          get().setZoomLevel(newLevel);
        },
        
        zoomOut: () => {
          const state = get();
          const newLevel = state.zoomLevel - 10;
          get().setZoomLevel(newLevel);
        },
        
        resetZoom: () => get().setZoomLevel(100),
        
        // Notification actions
        addNotification: (
          message: string,
          type: 'info' | 'success' | 'warning' | 'error',
          duration = 3000
        ) => {
          const id = `notif-${Date.now()}`;
          set((state) => ({
            notifications: [
              ...state.notifications,
              { id, message, type, duration },
            ],
          }));
          
          // Auto-remove after duration
          if (duration > 0) {
            setTimeout(() => {
              get().removeNotification(id);
            }, duration);
          }
        },
        
        removeNotification: (id: string) =>
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          })),
        
        clearNotifications: () =>
          set({
            notifications: [],
          }),
        
        // Reset
        reset: () =>
          set({
            panels: defaultPanels,
            sidebarWidth: 300,
            sidebarCollapsed: false,
            theme: 'dark',
            zoomLevel: 100,
            notifications: [],
          }),
      }),
      {
        name: 'anki-template-designer-ui', // localStorage key
        version: 1,
        // Only persist these fields
        partialize: (state) => ({
          panels: state.panels,
          sidebarWidth: state.sidebarWidth,
          sidebarCollapsed: state.sidebarCollapsed,
          theme: state.theme,
          zoomLevel: state.zoomLevel,
        }),
        // Migration handler
        migrate: (persistedState: any, version: number) => {
          if (version === 0) {
            // v0 migration logic
          }
          return persistedState as UiState;
        },
      },
    ),
    {
      name: 'UiStore',
      enabled: process.env.NODE_ENV === 'development',
    },
  ),
);

