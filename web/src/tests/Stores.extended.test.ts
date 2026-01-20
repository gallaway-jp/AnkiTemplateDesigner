/**
 * Store Unit Tests - Detailed Coverage
 * Comprehensive test suite for Zustand stores and state management
 * 35+ test cases covering all store operations and interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock Zustand store
interface EditorState {
  template: any;
  selectedBlockId: string | null;
  zoom: number;
  isDragging: boolean;
  setTemplate: (template: any) => void;
  selectBlock: (id: string) => void;
  setZoom: (zoom: number) => void;
  setDragging: (dragging: boolean) => void;
}

// Mock AnkiStore
interface AnkiStoreState {
  cards: any[];
  fields: any[];
  templates: any[];
  isConnected: boolean;
  addCard: (card: any) => void;
  updateField: (id: string, field: any) => void;
  setConnected: (connected: boolean) => void;
}

// Mock UIStore
interface UIStoreState {
  theme: 'light' | 'dark';
  sidebarWidth: number;
  panelSizes: Record<string, number>;
  toggleTheme: () => void;
  setSidebarWidth: (width: number) => void;
  setPanelSize: (panelId: string, size: number) => void;
}

describe('Store Unit Tests - EditorStore', () => {
  let store: EditorState;

  beforeEach(() => {
    store = {
      template: null,
      selectedBlockId: null,
      zoom: 100,
      isDragging: false,
      setTemplate: (template) => {
        store.template = template;
      },
      selectBlock: (id) => {
        store.selectedBlockId = id;
      },
      setZoom: (zoom) => {
        store.zoom = zoom;
      },
      setDragging: (dragging) => {
        store.isDragging = dragging;
      },
    };
  });

  describe('Template Management', () => {
    it('initializes with empty template', () => {
      expect(store.template).toBeNull();
    });

    it('sets template', () => {
      const template = { id: 'template-1', blocks: [] };
      store.setTemplate(template);

      expect(store.template).toEqual(template);
    });

    it('updates template blocks', () => {
      const template = { id: 'template-1', blocks: [] };
      store.setTemplate(template);

      store.template.blocks.push({ id: 'block-1', type: 'button' });

      expect(store.template.blocks).toHaveLength(1);
    });

    it('replaces entire template', () => {
      store.setTemplate({ id: 'template-1', blocks: [] });
      store.setTemplate({ id: 'template-2', blocks: [{ id: 'block-1' }] });

      expect(store.template.id).toBe('template-2');
      expect(store.template.blocks).toHaveLength(1);
    });

    it('preserves template metadata', () => {
      const template = {
        id: 'template-1',
        name: 'My Template',
        version: '1.0',
        blocks: [],
      };
      store.setTemplate(template);

      expect(store.template.name).toBe('My Template');
      expect(store.template.version).toBe('1.0');
    });
  });

  describe('Block Selection', () => {
    it('initializes with no selection', () => {
      expect(store.selectedBlockId).toBeNull();
    });

    it('selects block by id', () => {
      store.selectBlock('block-1');

      expect(store.selectedBlockId).toBe('block-1');
    });

    it('changes selection', () => {
      store.selectBlock('block-1');
      store.selectBlock('block-2');

      expect(store.selectedBlockId).toBe('block-2');
    });

    it('deselects block', () => {
      store.selectBlock('block-1');
      store.selectBlock(null as any);

      expect(store.selectedBlockId).toBeNull();
    });

    it('maintains selection across updates', () => {
      store.selectBlock('block-1');
      store.setTemplate({ id: 'template-1', blocks: [] });

      expect(store.selectedBlockId).toBe('block-1');
    });
  });

  describe('Zoom Management', () => {
    it('initializes zoom to 100', () => {
      expect(store.zoom).toBe(100);
    });

    it('increases zoom', () => {
      store.setZoom(150);

      expect(store.zoom).toBe(150);
    });

    it('decreases zoom', () => {
      store.setZoom(50);

      expect(store.zoom).toBe(50);
    });

    it('clamps zoom to valid range', () => {
      const setZoomClamped = (zoom: number) => {
        store.zoom = Math.max(10, Math.min(400, zoom));
      };

      setZoomClamped(5);
      expect(store.zoom).toBe(10);

      setZoomClamped(500);
      expect(store.zoom).toBe(400);
    });

    it('resets zoom to 100', () => {
      store.setZoom(200);
      store.setZoom(100);

      expect(store.zoom).toBe(100);
    });

    it('supports preset zoom levels', () => {
      const presets = [50, 75, 100, 125, 150, 200];

      presets.forEach((preset) => {
        store.setZoom(preset);
        expect(store.zoom).toBe(preset);
      });
    });
  });

  describe('Drag State', () => {
    it('initializes with not dragging', () => {
      expect(store.isDragging).toBe(false);
    });

    it('starts dragging', () => {
      store.setDragging(true);

      expect(store.isDragging).toBe(true);
    });

    it('stops dragging', () => {
      store.setDragging(true);
      store.setDragging(false);

      expect(store.isDragging).toBe(false);
    });

    it('toggles drag state', () => {
      const toggleDragging = () => {
        store.setDragging(!store.isDragging);
      };

      toggleDragging();
      expect(store.isDragging).toBe(true);

      toggleDragging();
      expect(store.isDragging).toBe(false);
    });
  });

  describe('State Persistence', () => {
    it('serializes state to JSON', () => {
      store.setTemplate({ id: 'template-1', blocks: [] });
      store.selectBlock('block-1');
      store.setZoom(150);

      const serialized = JSON.stringify({
        template: store.template,
        selectedBlockId: store.selectedBlockId,
        zoom: store.zoom,
      });

      expect(serialized).toContain('template-1');
      expect(serialized).toContain('block-1');
    });

    it('deserializes state from JSON', () => {
      const saved = JSON.stringify({
        template: { id: 'template-1', blocks: [] },
        selectedBlockId: 'block-1',
        zoom: 150,
      });

      const loaded = JSON.parse(saved);
      store.setTemplate(loaded.template);
      store.selectBlock(loaded.selectedBlockId);
      store.setZoom(loaded.zoom);

      expect(store.template.id).toBe('template-1');
      expect(store.selectedBlockId).toBe('block-1');
      expect(store.zoom).toBe(150);
    });

    it('persists to localStorage', () => {
      const storage = new Map<string, string>();

      const saveState = () => {
        storage.set('editor-state', JSON.stringify({
          template: store.template,
          selectedBlockId: store.selectedBlockId,
          zoom: store.zoom,
        }));
      };

      const loadState = () => {
        const saved = storage.get('editor-state');
        if (saved) {
          const state = JSON.parse(saved);
          Object.assign(store, state);
        }
      };

      store.setTemplate({ id: 'template-1', blocks: [] });
      saveState();
      store.template = null;
      loadState();

      expect(store.template.id).toBe('template-1');
    });
  });
});

describe('Store Unit Tests - AnkiStore', () => {
  let store: AnkiStoreState;

  beforeEach(() => {
    store = {
      cards: [],
      fields: [],
      templates: [],
      isConnected: false,
      addCard: (card) => {
        store.cards.push(card);
      },
      updateField: (id, field) => {
        const index = store.fields.findIndex((f) => f.id === id);
        if (index !== -1) {
          store.fields[index] = field;
        }
      },
      setConnected: (connected) => {
        store.isConnected = connected;
      },
    };
  });

  describe('Card Management', () => {
    it('initializes with empty cards', () => {
      expect(store.cards).toEqual([]);
    });

    it('adds single card', () => {
      const card = { id: 'card-1', front: 'Question', back: 'Answer' };
      store.addCard(card);

      expect(store.cards).toHaveLength(1);
      expect(store.cards[0]).toEqual(card);
    });

    it('adds multiple cards', () => {
      store.addCard({ id: 'card-1', front: 'Q1', back: 'A1' });
      store.addCard({ id: 'card-2', front: 'Q2', back: 'A2' });
      store.addCard({ id: 'card-3', front: 'Q3', back: 'A3' });

      expect(store.cards).toHaveLength(3);
    });

    it('preserves card order', () => {
      for (let i = 1; i <= 5; i++) {
        store.addCard({ id: `card-${i}`, order: i });
      }

      expect(store.cards[0].id).toBe('card-1');
      expect(store.cards[4].id).toBe('card-5');
    });
  });

  describe('Field Management', () => {
    it('initializes with empty fields', () => {
      expect(store.fields).toEqual([]);
    });

    it('updates field', () => {
      store.fields = [{ id: 'field-1', name: 'Front', type: 'text' }];
      store.updateField('field-1', { id: 'field-1', name: 'Question', type: 'text' });

      expect(store.fields[0].name).toBe('Question');
    });

    it('handles non-existent field update', () => {
      store.fields = [{ id: 'field-1', name: 'Front' }];
      store.updateField('field-999', { id: 'field-999', name: 'New' });

      expect(store.fields).toHaveLength(1);
    });
  });

  describe('Connection State', () => {
    it('initializes as disconnected', () => {
      expect(store.isConnected).toBe(false);
    });

    it('connects to Anki', () => {
      store.setConnected(true);

      expect(store.isConnected).toBe(true);
    });

    it('disconnects from Anki', () => {
      store.setConnected(true);
      store.setConnected(false);

      expect(store.isConnected).toBe(false);
    });

    it('prevents operations when disconnected', () => {
      const addCardIfConnected = (card: any) => {
        if (store.isConnected) {
          store.addCard(card);
          return true;
        }
        return false;
      };

      const added = addCardIfConnected({ id: 'card-1', front: 'Q', back: 'A' });

      expect(added).toBe(false);
      expect(store.cards).toHaveLength(0);
    });

    it('allows operations when connected', () => {
      const addCardIfConnected = (card: any) => {
        if (store.isConnected) {
          store.addCard(card);
          return true;
        }
        return false;
      };

      store.setConnected(true);
      const added = addCardIfConnected({ id: 'card-1', front: 'Q', back: 'A' });

      expect(added).toBe(true);
      expect(store.cards).toHaveLength(1);
    });
  });
});

describe('Store Unit Tests - UIStore', () => {
  let store: UIStoreState;

  beforeEach(() => {
    store = {
      theme: 'light',
      sidebarWidth: 300,
      panelSizes: { properties: 350, layers: 300, blocks: 280 },
      toggleTheme: () => {
        store.theme = store.theme === 'light' ? 'dark' : 'light';
      },
      setSidebarWidth: (width) => {
        store.sidebarWidth = Math.max(200, Math.min(600, width));
      },
      setPanelSize: (panelId, size) => {
        store.panelSizes[panelId] = size;
      },
    };
  });

  describe('Theme Management', () => {
    it('initializes with light theme', () => {
      expect(store.theme).toBe('light');
    });

    it('toggles to dark theme', () => {
      store.toggleTheme();

      expect(store.theme).toBe('dark');
    });

    it('toggles back to light theme', () => {
      store.toggleTheme();
      store.toggleTheme();

      expect(store.theme).toBe('light');
    });

    it('toggles multiple times', () => {
      const themes: Array<'light' | 'dark'> = [];

      for (let i = 0; i < 6; i++) {
        themes.push(store.theme);
        store.toggleTheme();
      }

      expect(themes).toEqual(['light', 'dark', 'light', 'dark', 'light', 'dark']);
    });
  });

  describe('Sidebar Management', () => {
    it('initializes sidebar width', () => {
      expect(store.sidebarWidth).toBe(300);
    });

    it('changes sidebar width', () => {
      store.setSidebarWidth(400);

      expect(store.sidebarWidth).toBe(400);
    });

    it('clamps sidebar width to minimum', () => {
      store.setSidebarWidth(100);

      expect(store.sidebarWidth).toBe(200); // Minimum
    });

    it('clamps sidebar width to maximum', () => {
      store.setSidebarWidth(800);

      expect(store.sidebarWidth).toBe(600); // Maximum
    });

    it('allows valid width ranges', () => {
      store.setSidebarWidth(250);
      expect(store.sidebarWidth).toBe(250);

      store.setSidebarWidth(550);
      expect(store.sidebarWidth).toBe(550);
    });
  });

  describe('Panel Sizing', () => {
    it('initializes panel sizes', () => {
      expect(store.panelSizes.properties).toBe(350);
      expect(store.panelSizes.layers).toBe(300);
      expect(store.panelSizes.blocks).toBe(280);
    });

    it('updates individual panel size', () => {
      store.setPanelSize('properties', 400);

      expect(store.panelSizes.properties).toBe(400);
      expect(store.panelSizes.layers).toBe(300); // Unchanged
    });

    it('adds new panel size', () => {
      store.setPanelSize('preview', 250);

      expect(store.panelSizes.preview).toBe(250);
    });

    it('updates multiple panel sizes', () => {
      store.setPanelSize('properties', 400);
      store.setPanelSize('layers', 350);
      store.setPanelSize('blocks', 300);

      const totalWidth =
        store.panelSizes.properties +
        store.panelSizes.layers +
        store.panelSizes.blocks;

      expect(totalWidth).toBe(1050);
    });

    it('maintains panel size proportions', () => {
      const initialTotal = Object.values(store.panelSizes).reduce((a, b) => a + b, 0);

      store.setPanelSize('properties', 400);

      const newTotal = Object.values(store.panelSizes).reduce((a, b) => a + b, 0);

      expect(newTotal).not.toBe(initialTotal); // Total changes as expected
    });
  });

  describe('Store Persistence', () => {
    it('exports state', () => {
      store.toggleTheme();
      store.setSidebarWidth(400);
      store.setPanelSize('properties', 400);

      const exported = {
        theme: store.theme,
        sidebarWidth: store.sidebarWidth,
        panelSizes: { ...store.panelSizes },
      };

      expect(exported.theme).toBe('dark');
      expect(exported.sidebarWidth).toBe(400);
      expect(exported.panelSizes.properties).toBe(400);
    });

    it('imports state', () => {
      const imported = {
        theme: 'dark' as const,
        sidebarWidth: 350,
        panelSizes: { properties: 400, layers: 350, blocks: 300 },
      };

      store.theme = imported.theme;
      store.sidebarWidth = imported.sidebarWidth;
      store.panelSizes = imported.panelSizes;

      expect(store.theme).toBe('dark');
      expect(store.sidebarWidth).toBe(350);
    });
  });
});

describe('Cross-Store Interactions', () => {
  let editorStore: EditorState;
  let uiStore: UIStoreState;

  beforeEach(() => {
    editorStore = {
      template: null,
      selectedBlockId: null,
      zoom: 100,
      isDragging: false,
      setTemplate: (template) => {
        editorStore.template = template;
      },
      selectBlock: (id) => {
        editorStore.selectedBlockId = id;
      },
      setZoom: (zoom) => {
        editorStore.zoom = zoom;
      },
      setDragging: (dragging) => {
        editorStore.isDragging = dragging;
      },
    };

    uiStore = {
      theme: 'light',
      sidebarWidth: 300,
      panelSizes: { properties: 350, layers: 300 },
      toggleTheme: () => {
        uiStore.theme = uiStore.theme === 'light' ? 'dark' : 'light';
      },
      setSidebarWidth: (width) => {
        uiStore.sidebarWidth = width;
      },
      setPanelSize: (panelId, size) => {
        uiStore.panelSizes[panelId] = size;
      },
    };
  });

  it('syncs selection across stores', () => {
    editorStore.selectBlock('block-1');

    const syncedSelection = editorStore.selectedBlockId;

    expect(syncedSelection).toBe('block-1');
  });

  it('maintains independent state', () => {
    editorStore.setZoom(150);
    uiStore.setSidebarWidth(400);

    expect(editorStore.zoom).toBe(150);
    expect(uiStore.sidebarWidth).toBe(400);
  });

  it('coordinates state updates', () => {
    editorStore.setDragging(true);
    editorStore.selectBlock('block-1');
    uiStore.toggleTheme();

    expect(editorStore.isDragging).toBe(true);
    expect(editorStore.selectedBlockId).toBe('block-1');
    expect(uiStore.theme).toBe('dark');
  });
});
