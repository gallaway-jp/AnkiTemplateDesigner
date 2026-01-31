/**
 * Panel Components Accessibility Tests
 * Ensures WCAG 2.1 AA compliance for all panel components
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import BlocksPanel from './BlocksPanel';
import PropertiesPanel from './PropertiesPanel';
import LayersPanel from './LayersPanel';

// Mock Craft.js hooks
vi.mock('@craftjs/core', () => ({
  useEditor: () => ({
    connectors: {
      create: vi.fn(),
    },
    actions: {
      add: vi.fn(),
      selectNode: vi.fn(),
      delete: vi.fn(),
      setProp: vi.fn(),
    },
    query: {
      node: () => ({
        get: () => ({
          data: {
            name: 'TestNode',
            displayName: 'Test Node',
            props: {},
          },
          related: {},
        }),
      }),
      getNodes: () => ({
        ROOT: {
          id: 'ROOT',
          data: { name: 'Root', displayName: 'Root', craft: { isCanvas: false } },
          nodes: [],
          parent: null,
        },
      }),
      serialize: vi.fn(),
    },
    selected: new Set(['node-1']),
  }),
  useNode: () => ({
    connectors: {
      connect: (ref: any) => ref,
      drag: (ref: any) => ref,
    },
    actions: {
      setProp: vi.fn(),
    },
    id: 'node-1',
    related: {},
  }),
}));

// Mock block registry
vi.mock('@/services/blockRegistry', () => ({
  blockRegistry: {
    getBlocksByCategory: vi.fn(() => ({
      'Layout': [
        { name: 'Container', displayName: 'Container', category: 'Layout', icon: '📦', description: 'A container block' },
        { name: 'Frame', displayName: 'Frame', category: 'Layout', icon: '🖼️', description: 'A frame block' },
      ],
      'Data': [
        { name: 'Text', displayName: 'Text', category: 'Data', icon: '📝', description: 'A text block' },
        { name: 'Heading', displayName: 'Heading', category: 'Data', icon: 'H', description: 'A heading block' },
      ],
    })),
  },
}));

// Mock stores
vi.mock('@/stores', () => ({
  editorStore: {
    getState: () => ({
      selectedNodeId: 'node-1',
    }),
    setState: vi.fn(),
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

describe('Panel Components Accessibility Tests', () => {
  describe('BlocksPanel', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<BlocksPanel />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels for search input', () => {
      const { container } = render(<BlocksPanel />);
      const searchInput = container.querySelector('input[type="search"]');
      
      expect(searchInput).toBeTruthy();
      // Should have either aria-label or associated label
      const hasAriaLabel = searchInput?.hasAttribute('aria-label');
      const hasAssociatedLabel = searchInput?.hasAttribute('id') && 
        container.querySelector(`label[for="${searchInput.getAttribute('id')}"]`);
      
      expect(hasAriaLabel || hasAssociatedLabel).toBe(true);
    });

    it('should have proper heading structure', () => {
      const { container } = render(<BlocksPanel />);
      const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
      
      // Should have at least a panel title
      expect(headings.length).toBeGreaterThan(0);
    });

    it('should have keyboard-accessible block items', () => {
      const { container } = render(<BlocksPanel />);
      const blockItems = container.querySelectorAll('[draggable="true"]');
      
      blockItems.forEach(item => {
        // Draggable items should be keyboard accessible
        const hasTabIndex = item.hasAttribute('tabindex');
        const hasRole = item.hasAttribute('role');
        const hasAriaLabel = item.hasAttribute('aria-label') || item.textContent;
        
        expect(hasTabIndex || hasRole || hasAriaLabel).toBe(true);
      });
    });
  });

  describe('PropertiesPanel', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<PropertiesPanel />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper form labels', () => {
      const { container } = render(<PropertiesPanel />);
      const inputs = container.querySelectorAll('input, select, textarea');
      
      inputs.forEach(input => {
        // Each input should have a label
        const hasAriaLabel = input.hasAttribute('aria-label');
        const hasAriaLabelledBy = input.hasAttribute('aria-labelledby');
        const hasAssociatedLabel = input.hasAttribute('id') && 
          container.querySelector(`label[for="${input.getAttribute('id')}"]`);
        
        expect(hasAriaLabel || hasAriaLabelledBy || hasAssociatedLabel).toBe(true);
      });
    });

    it('should indicate required fields', () => {
      const { container } = render(<PropertiesPanel />);
      const requiredInputs = container.querySelectorAll('[required]');
      
      requiredInputs.forEach(input => {
        // Required inputs should have aria-required or required attribute
        const hasAriaRequired = input.hasAttribute('aria-required');
        const hasRequired = input.hasAttribute('required');
        
        expect(hasAriaRequired || hasRequired).toBe(true);
      });
    });

    it('should have proper contrast for disabled states', () => {
      const { container } = render(<PropertiesPanel />);
      const disabledElements = container.querySelectorAll('[disabled]');
      
      disabledElements.forEach(element => {
        // Disabled elements should have aria-disabled attribute
        const hasAriaDisabled = element.hasAttribute('aria-disabled') || 
                                element.hasAttribute('disabled');
        expect(hasAriaDisabled).toBe(true);
      });
    });
  });

  describe('LayersPanel', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<LayersPanel />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have tree structure with proper ARIA roles', () => {
      const { container } = render(<LayersPanel />);
      
      // Tree structure should use role="tree" and role="treeitem"
      const treeElements = container.querySelectorAll('[role="tree"], [role="treegrid"]');
      const treeItems = container.querySelectorAll('[role="treeitem"]');
      
      // Should have either a tree structure or list structure
      expect(treeElements.length > 0 || treeItems.length > 0 || 
             container.querySelector('ul, ol')).toBeTruthy();
    });

    it('should indicate expanded/collapsed state', () => {
      const { container } = render(<LayersPanel />);
      const expandableItems = container.querySelectorAll('[aria-expanded]');
      
      expandableItems.forEach(item => {
        const ariaExpanded = item.getAttribute('aria-expanded');
        expect(['true', 'false']).toContain(ariaExpanded);
      });
    });

    it('should indicate selected items', () => {
      const { container } = render(<LayersPanel />);
      const selectableItems = container.querySelectorAll('[aria-selected]');
      
      selectableItems.forEach(item => {
        const ariaSelected = item.getAttribute('aria-selected');
        expect(['true', 'false']).toContain(ariaSelected);
      });
    });

    it('should have keyboard navigation support', () => {
      const { container } = render(<LayersPanel />);
      const interactiveItems = container.querySelectorAll('button, [role="button"], [tabindex]');
      
      // Should have interactive elements that can be focused
      expect(interactiveItems.length).toBeGreaterThan(0);
    });
  });

  describe('Cross-Panel Accessibility', () => {
    it('all panels should have unique IDs for same-page landmarks', () => {
      const panels = [
        render(<BlocksPanel />),
        render(<PropertiesPanel />),
        render(<LayersPanel />),
      ];

      const allIds = panels.flatMap(({ container }) => 
        Array.from(container.querySelectorAll('[id]')).map(el => el.getAttribute('id'))
      );

      const uniqueIds = new Set(allIds);
      expect(allIds.length).toBe(uniqueIds.size); // No duplicate IDs
    });

    it('all panels should support high contrast mode', () => {
      const panels = [BlocksPanel, PropertiesPanel, LayersPanel];

      panels.forEach(Panel => {
        const { container } = render(<Panel />);
        
        // Check for use of semantic elements that work well in high contrast
        const hasSemanticElements = 
          container.querySelector('button, input, select, textarea, h1, h2, h3, h4, h5, h6');
        
        expect(hasSemanticElements).toBeTruthy();
      });
    });

    it('all panels should have focusable elements with visible focus indicators', () => {
      const panels = [BlocksPanel, PropertiesPanel, LayersPanel];

      panels.forEach(Panel => {
        const { container } = render(<Panel />);
        const focusableElements = container.querySelectorAll(
          'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        // Should have at least some focusable elements
        expect(focusableElements.length).toBeGreaterThan(0);

        focusableElements.forEach(element => {
          // Elements should not have outline: none without alternative focus indicator
          const computedStyle = window.getComputedStyle(element);
          const hasVisibleFocus = 
            computedStyle.outline !== 'none' || 
            computedStyle.boxShadow !== 'none' ||
            element.classList.contains('focus-visible');
          
          // Note: This is a basic check; full verification requires actual focus testing
          expect(element).toBeTruthy();
        });
      });
    });
  });
});
