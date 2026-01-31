/**
 * Vitest Setup
 * Configure test environment, mocks, and utilities
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import { toHaveNoViolations } from 'jest-axe';

// Extend Vitest matchers with jest-axe
expect.extend(toHaveNoViolations);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock QWebChannel for Python bridge testing
(window as any).QWebChannel = undefined;
(window as any).qt = undefined;

// Mock import.meta.env
Object.defineProperty(import.meta, 'env', {
  value: {
    DEV: true,
    PROD: false,
    SSR: false,
  },
});

// Suppress console errors in tests
global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
};

// Setup DOM utilities
export const renderWithProviders = (component: any) => {
  // Will be used in component tests
  return component;
};
