/**
 * BlocksPanel Component Snapshot Tests
 * Ensures blocks panel UI consistency
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import BlocksPanel from './BlocksPanel';

// Mock Craft.js useEditor hook
vi.mock('@craftjs/core', () => ({
  useEditor: () => ({
    connectors: {
      create: vi.fn(),
    },
    actions: {
      add: vi.fn(),
    },
    query: {
      node: vi.fn(),
    },
  }),
}));

// Mock block registry
vi.mock('@/services/blockRegistry', () => ({
  blockRegistry: {
    getBlocksByCategory: vi.fn(() => ({
      'Layout': [
        { name: 'Container', displayName: 'Container', category: 'Layout', icon: '📦' },
        { name: 'Frame', displayName: 'Frame', category: 'Layout', icon: '🖼️' },
      ],
      'Data': [
        { name: 'Text', displayName: 'Text', category: 'Data', icon: '📝' },
        { name: 'Heading', displayName: 'Heading', category: 'Data', icon: 'H' },
      ],
      'Anki Special': [
        { name: 'AnkiField', displayName: 'Anki Field', category: 'Anki Special', icon: '{{' },
      ],
    })),
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

describe('BlocksPanel Snapshot Tests', () => {
  it('matches snapshot with default state', () => {
    const { container } = render(<BlocksPanel />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with search query', () => {
    const { container } = render(<BlocksPanel />);
    
    // Simulate search input
    const searchInput = container.querySelector('input[type="search"]');
    if (searchInput) {
      (searchInput as HTMLInputElement).value = 'text';
    }
    
    expect(container).toMatchSnapshot();
  });
});
