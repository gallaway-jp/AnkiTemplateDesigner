/**
 * Block Registry Service
 * Registers all Anki Template Designer blocks with Craft.js
 * Provides type-safe block management and serialization
 */

import { Component } from 'react';
import { logger } from '@/utils/logger';

/**
 * Block configuration that matches Craft.js requirements
 */
export interface CraftBlock {
  name: string; // Unique identifier
  label: string; // Display name
  category: string; // Category grouping
  description?: string;
  icon?: string;
  Component: React.ComponentType<any>;
  defaultProps?: Record<string, any>;
  craft?: {
    rules?: {
      canDrag?: () => boolean;
      canDrop?: () => boolean;
      canMoveIn?: () => boolean;
      canMoveOut?: () => boolean;
    };
    props?: Record<string, any>;
    displayName?: string;
    isCanvas?: boolean;
    related?: string[];
  };
  serialize?: (element: HTMLElement) => Record<string, any>;
  deserialize?: (data: Record<string, any>) => void;
}

/**
 * Block registry - centralized management of all available blocks
 */
class BlockRegistry {
  private blocks: Map<string, CraftBlock> = new Map();
  private categories: Set<string> = new Set();

  /**
   * Register a single block
   */
  register(block: CraftBlock): void {
    if (this.blocks.has(block.name)) {
      logger.warn(`Block "${block.name}" is already registered, overwriting`);
    }

    this.blocks.set(block.name, block);
    this.categories.add(block.category);

    logger.info(`Block registered: ${block.name}`, {
      category: block.category,
      displayName: block.label,
    });
  }

  /**
   * Register multiple blocks
   */
  registerMany(blocks: CraftBlock[]): void {
    blocks.forEach((block) => this.register(block));
  }

  /**
   * Get all blocks
   */
  getAll(): CraftBlock[] {
    return Array.from(this.blocks.values());
  }

  /**
   * Get blocks by category
   */
  getByCategory(category: string): CraftBlock[] {
    return Array.from(this.blocks.values()).filter((b) => b.category === category);
  }

  /**
   * Get all categories
   */
  getCategories(): string[] {
    return Array.from(this.categories.values()).sort();
  }

  /**
   * Get a single block by name
   */
  get(name: string): CraftBlock | undefined {
    return this.blocks.get(name);
  }

  /**
   * Check if block exists
   */
  has(name: string): boolean {
    return this.blocks.has(name);
  }

  /**
   * Get resolver object for Craft.js Editor component
   * Maps block names to their React components
   */
  getResolver(): Record<string, React.ComponentType<any>> {
    const resolver: Record<string, React.ComponentType<any>> = {};

    this.blocks.forEach((block) => {
      resolver[block.name] = block.Component;
    });

    return resolver;
  }

  /**
   * Clear all registered blocks (mainly for testing)
   */
  clear(): void {
    this.blocks.clear();
    this.categories.clear();
    logger.info('Block registry cleared');
  }

  /**
   * Get statistics about registered blocks
   */
  getStats(): {
    totalBlocks: number;
    categories: number;
    byCategory: Record<string, number>;
  } {
    const stats: Record<string, number> = {};

    this.categories.forEach((cat) => {
      stats[cat] = this.getByCategory(cat).length;
    });

    return {
      totalBlocks: this.blocks.size,
      categories: this.categories.size,
      byCategory: stats,
    };
  }
}

// Export singleton instance
export const blockRegistry = new BlockRegistry();

/**
 * Helper function to create a basic Craft.js component wrapper
 * Handles serialization and craft properties
 */
export function createCraftBlock<P extends Record<string, any>>(
  Component: React.ComponentType<P>,
  options: {
    name: string;
    label: string;
    category: string;
    description?: string;
    icon?: string;
    defaultProps?: P;
    isCanvas?: boolean;
    canDrag?: () => boolean;
    canDrop?: () => boolean;
    canMoveIn?: () => boolean;
    canMoveOut?: () => boolean;
    serialize?: (element: HTMLElement) => any;
    deserialize?: (data: any) => void;
  }
): CraftBlock {
  const {
    name,
    label,
    category,
    description,
    icon,
    defaultProps = {},
    isCanvas = false,
    canDrag,
    canDrop,
    canMoveIn,
    canMoveOut,
    serialize,
    deserialize,
  } = options;

  // Add Craft.js configuration to component
  const WrappedComponent = Component as any;
  WrappedComponent.craft = {
    rules: {
      canDrag: canDrag || (() => true),
      canDrop: canDrop || (() => true),
      canMoveIn: canMoveIn || (() => true),
      canMoveOut: canMoveOut || (() => true),
    },
    props: defaultProps,
    displayName: label,
    isCanvas,
  };

  return {
    name,
    label,
    category,
    description,
    icon,
    Component: WrappedComponent,
    defaultProps,
    craft: WrappedComponent.craft,
    serialize,
    deserialize,
  };
}

/**
 * Export register function for use in block modules
 */
export function registerBlocks(blocks: CraftBlock[]): void {
  blockRegistry.registerMany(blocks);
}

/**
 * Hook-like function to initialize all blocks in the Craft.js editor
 * Should be called during editor initialization
 */
export async function initializeBlocks(): Promise<void> {
  try {
    // Dynamically import all block modules from components/Blocks
    const [layoutBlocks, inputBlocks, buttonBlocks, dataBlocks] = await Promise.all([
      import('../components/Blocks/LayoutBlocks').then((m) => m.getBlocks?.()).catch((e) => {
        logger.warn('Failed to load layout blocks', e);
        return [];
      }),
      import('../components/Blocks/InputBlocks').then((m) => m.getBlocks?.()).catch((e) => {
        logger.warn('Failed to load input blocks', e);
        return [];
      }),
      import('../components/Blocks/ButtonBlocks').then((m) => m.getBlocks?.()).catch((e) => {
        logger.warn('Failed to load button blocks', e);
        return [];
      }),
      import('../components/Blocks/DataBlocks').then((m) => m.getBlocks?.()).catch((e) => {
        logger.warn('Failed to load data blocks', e);
        return [];
      }),
    ]);

    const allBlocks = [
      ...(layoutBlocks || []),
      ...(inputBlocks || []),
      ...(buttonBlocks || []),
      ...(dataBlocks || []),
    ];

    blockRegistry.registerMany(allBlocks);

    const stats = blockRegistry.getStats();
    logger.info('Blocks initialized', stats);
  } catch (error) {
    logger.error('Failed to initialize blocks', error);
    throw error;
  }
}

export default blockRegistry;
