/**
 * Test Utilities
 */

export * from './mockBridge';

// Additional test helpers can be added here
export function waitFor(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function createMockTemplate() {
  return {
    id: 'test-template',
    name: 'Test Template',
    html: '<div>Test</div>',
    css: '.test { color: red; }',
    meta: {
      version: '2.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  };
}

export function createMockFields() {
  return [
    { name: 'Front', description: 'Front of card' },
    { name: 'Back', description: 'Back of card' },
  ];
}
