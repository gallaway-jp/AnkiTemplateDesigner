/**
 * AnkiBlocks Component Snapshot Tests
 * Ensures Anki-specific block rendering remains consistent
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { AnkiField, AnkiCloze, AnkiConditional } from './AnkiBlocks';

// Mock Craft.js useNode hook
vi.mock('@craftjs/core', () => ({
  useNode: () => ({
    connectors: {
      connect: (ref: any) => ref,
      drag: (ref: any) => ref,
    },
    actions: {
      setProp: vi.fn(),
    },
  }),
}));

// Mock block registry
vi.mock('@/services/blockRegistry', () => ({
  blockRegistry: {
    register: vi.fn(),
  },
}));

describe('AnkiBlocks Snapshot Tests', () => {
  describe('AnkiField', () => {
    it('matches snapshot with default props', () => {
      const { container } = render(<AnkiField />);
      expect(container).toMatchSnapshot();
    });

    it('matches snapshot with custom field name', () => {
      const { container } = render(
        <AnkiField fieldName="Front" />
      );
      expect(container).toMatchSnapshot();
    });

    it('matches snapshot with fallback text', () => {
      const { container } = render(
        <AnkiField 
          fieldName="Extra" 
          fallback="(No extra content)"
        />
      );
      expect(container).toMatchSnapshot();
    });
  });

  describe('AnkiCloze', () => {
    it('matches snapshot with default props', () => {
      const { container } = render(<AnkiCloze />);
      expect(container).toMatchSnapshot();
    });

    it('matches snapshot with custom cloze number', () => {
      const { container } = render(
        <AnkiCloze 
          fieldName="Text" 
          clozeNumber={3}
        />
      );
      expect(container).toMatchSnapshot();
    });
  });

  describe('AnkiConditional', () => {
    it('matches snapshot with default props', () => {
      const { container } = render(
        <AnkiConditional>
          <div>Conditional Content</div>
        </AnkiConditional>
      );
      expect(container).toMatchSnapshot();
    });

    it('matches snapshot with custom field name', () => {
      const { container } = render(
        <AnkiConditional fieldName="Extra">
          <div>Show when Extra exists</div>
        </AnkiConditional>
      );
      expect(container).toMatchSnapshot();
    });

    it('matches snapshot with negated condition', () => {
      const { container } = render(
        <AnkiConditional 
          fieldName="Front" 
          negate={true}
        >
          <div>Show when Front is empty</div>
        </AnkiConditional>
      );
      expect(container).toMatchSnapshot();
    });
  });
});
