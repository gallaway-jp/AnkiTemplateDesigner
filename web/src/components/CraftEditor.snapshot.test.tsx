/**
 * CraftEditor Component Snapshot Tests
 * Validates Craft.js editor rendering consistency
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import CraftEditor from './CraftEditor';
import { Editor, Frame } from '@craftjs/core';

// Mock the Craft.js Editor and Frame
vi.mock('@craftjs/core', () => ({
  Editor: ({ children }: any) => <div data-testid="craft-editor-wrapper">{children}</div>,
  Frame: ({ children }: any) => <div data-testid="craft-frame">{children}</div>,
  useEditor: () => ({
    selected: null,
    hovered: null,
    actions: {
      deserialize: vi.fn(),
    },
    query: {
      serialize: vi.fn().mockReturnValue('{}'),
    },
  }),
}));

// Mock block registry
vi.mock('@/services/blockRegistry', () => ({
  blockRegistry: {
    getAllComponents: () => ({
      TextBlock: ({ children }: any) => <div>{children}</div>,
      ContainerBlock: ({ children }: any) => <div>{children}</div>,
    }),
  },
}));

// Mock logger
vi.mock('@/utils/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
  },
}));

// Mock editor store
vi.mock('@/stores', () => ({
  editorStore: vi.fn((selector) => {
    const state = {
      template: null,
      loading: false,
      error: null,
    };
    return selector ? selector(state) : state;
  }),
}));

// Mock block instantiator
vi.mock('@/services/blockInstantiator', () => ({
  createBlockFromDropEvent: vi.fn(),
}));

describe('CraftEditor Snapshot Tests', () => {
  it('matches snapshot with basic setup', () => {
    const onEditorReady = vi.fn();
    const { container } = render(
      <CraftEditor onEditorReady={onEditorReady} />
    );
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with custom className', () => {
    const onEditorReady = vi.fn();
    const { container } = render(
      <CraftEditor 
        onEditorReady={onEditorReady}
        className="custom-editor-class"
      />
    );
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with initial content', () => {
    const onEditorReady = vi.fn();
    const initialContent = '{"ROOT":{"type":"Container","nodes":[]}}';
    
    const { container } = render(
      <CraftEditor 
        onEditorReady={onEditorReady}
        initialContent={initialContent}
      />
    );
    expect(container).toMatchSnapshot();
  });
});
