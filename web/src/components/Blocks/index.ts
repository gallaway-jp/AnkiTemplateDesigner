/**
 * Block Components Index
 * Exports all block components and block definitions
 * Integrates with Craft.js for visual editing
 */

// Layout Blocks
export * from './LayoutBlocks';

// Input & Form Blocks
export * from './InputBlocks';

// Button & Action Blocks
export * from './ButtonBlocks';

// Data Display & Media Blocks
export * from './DataBlocks';

/**
 * Register all blocks with Craft.js
 */
export function registerAllBlocks(): void {
  // Import the block registry
  const { blockRegistry } = require('@/services/blockRegistry');

  // Import getBlocks functions from each category
  const { getBlocks: getLayoutBlocks } = require('./LayoutBlocks');
  const { getBlocks: getInputBlocks } = require('./InputBlocks');
  const { getBlocks: getButtonBlocks } = require('./ButtonBlocks');
  const { getBlocks: getDataBlocks } = require('./DataBlocks');

  // Register all blocks
  blockRegistry.registerMany([
    ...getLayoutBlocks(),
    ...getInputBlocks(),
    ...getButtonBlocks(),
    ...getDataBlocks(),
  ]);
}

