/**
 * TemplatePreview Component Snapshot Tests
 * Validates preview rendering consistency
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import TemplatePreview from './TemplatePreview';
import type { Template, AnkiField } from '@types';

// Mock Python bridge
vi.mock('@services/pythonBridge', () => ({
  bridge: {
    previewTemplate: vi.fn().mockResolvedValue({
      html: '<div>Preview</div>',
      css: '.preview { color: red; }',
    }),
  },
}));

// Mock logger
vi.mock('@utils/logger', () => ({
  createLogger: () => ({
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
  }),
}));

describe('TemplatePreview Snapshot Tests', () => {
  const mockFields: AnkiField[] = [
    { name: 'Front', ordinal: 0 },
    { name: 'Back', ordinal: 1 },
    { name: 'Extra', ordinal: 2 },
  ];

  const mockTemplate: Template = {
    id: 1,
    name: 'Test Template',
    html: '<div>{{Front}}</div>',
    css: '.card { background: white; }',
    fields: ['Front', 'Back'],
  };

  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('matches snapshot with null template', () => {
    const { container } = render(
      <TemplatePreview 
        template={null}
        fields={mockFields}
        onClose={mockOnClose}
      />
    );
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with template', () => {
    const { container } = render(
      <TemplatePreview 
        template={mockTemplate}
        fields={mockFields}
        onClose={mockOnClose}
      />
    );
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with empty fields', () => {
    const { container } = render(
      <TemplatePreview 
        template={mockTemplate}
        fields={[]}
        onClose={mockOnClose}
      />
    );
    expect(container).toMatchSnapshot();
  });
});
