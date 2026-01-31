/**
 * Editor Component Snapshot Tests
 * Ensures UI consistency and catches unintended visual changes
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import Editor from './Editor';
import { useEditorStore, useAnkiStore, useUiStore } from '@stores';

// Mock stores
vi.mock('@stores', () => ({
  useEditorStore: vi.fn(),
  useAnkiStore: vi.fn(),
  useUiStore: vi.fn(),
}));

// Mock Python bridge
vi.mock('@services/pythonBridge', () => ({
  bridge: {
    saveTemplate: vi.fn().mockResolvedValue({ success: true }),
    loadTemplate: vi.fn().mockResolvedValue({}),
    exportHTML: vi.fn().mockResolvedValue('<div>exported</div>'),
  },
}));

// Mock child components to isolate Editor
vi.mock('./CraftEditor', () => ({
  default: () => <div data-testid="craft-editor">Mock CraftEditor</div>,
}));

vi.mock('./EditorToolBar', () => ({
  default: () => <div data-testid="toolbar">Mock Toolbar</div>,
}));

vi.mock('./TemplatePreview', () => ({
  default: () => <div data-testid="preview">Mock Preview</div>,
}));

vi.mock('./StatusBar', () => ({
  default: () => <div data-testid="status-bar">Mock StatusBar</div>,
}));

describe('Editor Snapshot Tests', () => {
  beforeEach(() => {
    // Setup default store states
    (useEditorStore as any).mockImplementation((selector: any) => {
      const state = {
        currentTemplate: { id: 1, name: 'Test Template', content: '{}' },
        isDirty: false,
        canUndo: () => false,
        canRedo: () => false,
        undo: vi.fn(),
        redo: vi.fn(),
        markClean: vi.fn(),
        serializeTemplate: vi.fn().mockReturnValue('{}'),
      };
      return selector(state);
    });

    (useAnkiStore as any).mockImplementation((selector: any) => {
      const state = {
        fields: ['Front', 'Back', 'Extra'],
      };
      return selector(state);
    });

    (useUiStore as any).mockImplementation((selector: any) => {
      const state = {
        theme: 'dark',
        zoomLevel: 100,
        sidebarWidth: 250,
      };
      return selector(state);
    });
  });

  it('matches snapshot with default state', () => {
    const { container } = render(<Editor />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot when template is dirty', () => {
    (useEditorStore as any).mockImplementation((selector: any) => {
      const state = {
        currentTemplate: { id: 1, name: 'Test Template', content: '{}' },
        isDirty: true,
        canUndo: () => true,
        canRedo: () => false,
        undo: vi.fn(),
        redo: vi.fn(),
        markClean: vi.fn(),
        serializeTemplate: vi.fn().mockReturnValue('{}'),
      };
      return selector(state);
    });

    const { container } = render(<Editor />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with light theme', () => {
    (useUiStore as any).mockImplementation((selector: any) => {
      const state = {
        theme: 'light',
        zoomLevel: 100,
        sidebarWidth: 250,
      };
      return selector(state);
    });

    const { container } = render(<Editor />);
    expect(container).toMatchSnapshot();
  });
});
