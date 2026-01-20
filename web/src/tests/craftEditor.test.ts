/**
 * Craft.js Editor Integration Tests
 * Tests editor initialization, block rendering, and interaction
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CraftEditor } from '@/components/CraftEditor';
import { blockRegistry, initializeBlocks } from '@/services/blockRegistry';
import { editorStore } from '@/stores';

// Mock Craft.js
vi.mock('@craftjs/core', () => ({
  Editor: ({ children }: any) => <div data-testid="craft-editor">{children}</div>,
  Frame: ({ children }: any) => <div data-testid="craft-frame">{children}</div>,
  useEditor: () => ({
    nodes: {},
    selected: null,
    hovered: null,
  }),
}));

describe('CraftEditor', () => {
  beforeEach(() => {
    // Reset state
    editorStore.setState({
      currentTemplate: null,
      isDirty: false,
      selectedComponentId: null,
      selectedComponentPath: [],
      history: [],
      historyIndex: -1,
      isLoading: false,
      loadError: null,
    });
    blockRegistry.clear();
  });

  describe('Initialization', () => {
    it('should render the editor container', () => {
      render(<CraftEditor />);
      expect(screen.getByTestId('craft-editor')).toBeInTheDocument();
    });

    it('should show loading state initially', () => {
      editorStore.setState({ isLoading: true });
      render(<CraftEditor />);
      expect(screen.getByText(/loading editor/i)).toBeInTheDocument();
    });

    it('should show error state when error exists', () => {
      editorStore.setState({ error: new Error('Test error'), isLoading: false });
      render(<CraftEditor />);
      expect(screen.getByText(/editor error/i)).toBeInTheDocument();
      expect(screen.getByText(/test error/i)).toBeInTheDocument();
    });

    it('should display craft frame', () => {
      render(<CraftEditor />);
      expect(screen.getByTestId('craft-frame')).toBeInTheDocument();
    });
  });

  describe('Block Registry', () => {
    it('should initialize blocks on mount', async () => {
      await initializeBlocks();
      const stats = blockRegistry.getStats();
      expect(stats.totalBlocks).toBeGreaterThan(0);
    });

    it('should register layout blocks', async () => {
      await initializeBlocks();
      const layoutBlocks = blockRegistry.getByCategory('Layout & Structure');
      expect(layoutBlocks.length).toBeGreaterThan(0);
      expect(layoutBlocks.some((b) => b.name === 'layout-frame')).toBe(true);
    });

    it('should register input blocks', async () => {
      await initializeBlocks();
      const inputBlocks = blockRegistry.getByCategory('Inputs & Forms');
      expect(inputBlocks.length).toBeGreaterThan(0);
      expect(inputBlocks.some((b) => b.name === 'input-text')).toBe(true);
    });

    it('should register button blocks', async () => {
      await initializeBlocks();
      const buttonBlocks = blockRegistry.getByCategory('Buttons & Actions');
      expect(buttonBlocks.length).toBeGreaterThan(0);
      expect(buttonBlocks.some((b) => b.name === 'button-primary')).toBe(true);
    });

    it('should register data blocks', async () => {
      await initializeBlocks();
      const dataBlocks = blockRegistry.getByCategory('Data Display');
      expect(dataBlocks.length).toBeGreaterThan(0);
      expect(dataBlocks.some((b) => b.name === 'data-heading')).toBe(true);
    });

    it('should provide resolver for all blocks', async () => {
      await initializeBlocks();
      const resolver = blockRegistry.getResolver();
      expect(Object.keys(resolver).length).toBeGreaterThan(0);
      expect(resolver['layout-frame']).toBeDefined();
    });
  });

  describe('Block Properties', () => {
    it('should have proper craft configuration for canvas blocks', async () => {
      await initializeBlocks();
      const frameBlock = blockRegistry.get('layout-frame');
      expect(frameBlock?.craft?.isCanvas).toBe(true);
    });

    it('should have default props for blocks with configurable options', async () => {
      await initializeBlocks();
      const buttonBlock = blockRegistry.get('button-primary');
      expect(buttonBlock?.defaultProps?.label).toBeDefined();
    });

    it('should prevent non-canvas blocks from accepting drops', async () => {
      await initializeBlocks();
      const spacerBlock = blockRegistry.get('layout-spacer');
      expect(spacerBlock?.craft?.rules?.canDrop?.()).toBe(false);
    });
  });

  describe('Editor Store Integration', () => {
    it('should update selectedNode when component is selected', async () => {
      const testNode = { id: 'test-1', type: 'button', label: 'Test Button' };
      editorStore.setState((state) => ({
        ...state,
        selectedNode: testNode,
        selectedNodeId: 'test-1',
      }));

      const state = editorStore.getState();
      expect(state.selectedNodeId).toBe('test-1');
      expect(state.selectedNode?.label).toBe('Test Button');
    });

    it('should track template changes', () => {
      const template = {
        id: 'temp-1',
        name: 'Test Template',
        html: '<div>Test</div>',
        css: '',
        fields: [],
      };

      editorStore.setState((state) => ({
        ...state,
        template,
      }));

      const state = editorStore.getState();
      expect(state.template?.name).toBe('Test Template');
    });
  });

  describe('Block Categories', () => {
    it('should have all expected categories', async () => {
      await initializeBlocks();
      const categories = blockRegistry.getCategories();
      expect(categories).toContain('Layout & Structure');
      expect(categories).toContain('Inputs & Forms');
      expect(categories).toContain('Buttons & Actions');
      expect(categories).toContain('Data Display');
    });

    it('should allow filtering blocks by category', async () => {
      await initializeBlocks();
      const layoutBlocks = blockRegistry.getByCategory('Layout & Structure');
      const inputBlocks = blockRegistry.getByCategory('Inputs & Forms');

      expect(layoutBlocks.length).toBeGreaterThan(0);
      expect(inputBlocks.length).toBeGreaterThan(0);
      expect(layoutBlocks[0]?.category).toBe('Layout & Structure');
    });
  });

  describe('Block Statistics', () => {
    it('should provide correct statistics', async () => {
      await initializeBlocks();
      const stats = blockRegistry.getStats();

      expect(stats.totalBlocks).toBeGreaterThan(40);
      expect(stats.categories).toBeGreaterThan(0);
      expect(stats.byCategory['Layout & Structure']).toBeGreaterThan(0);
    });
  });

  describe('Editor Styling', () => {
    it('should apply correct CSS class', () => {
      const { container } = render(<CraftEditor />);
      expect(container.querySelector('.craft-editor')).toBeInTheDocument();
    });

    it('should support custom className', () => {
      const { container } = render(<CraftEditor className="custom-class" />);
      expect(container.querySelector('.craft-editor.custom-class')).toBeInTheDocument();
    });
  });
});
