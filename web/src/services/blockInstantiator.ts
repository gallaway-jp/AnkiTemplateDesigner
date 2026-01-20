/**
 * Block Instantiator Service
 * Creates block instances from definitions with proper initialization
 */

import { v4 as uuidv4 } from 'crypto';
import { blockRegistry, CraftBlock } from './blockRegistry';
import { logger } from '@/utils/logger';

/**
 * Represents a block instance in the canvas
 */
export interface BlockInstance {
  id: string; // Unique identifier
  name: string; // Block name (e.g., 'layout-frame')
  type: string; // Component type
  props: Record<string, any>; // Component props
  children: BlockInstance[]; // Nested children
  styles?: Record<string, string>; // Inline styles
  attributes?: Record<string, string>; // HTML attributes
  metadata?: {
    createdAt: number;
    position?: { x: number; y: number };
    size?: { width: number; height: number };
  };
}

/**
 * Generate unique ID for block instance
 */
function generateBlockId(blockName: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${blockName}-${timestamp}-${random}`;
}

/**
 * Create a block instance from a block definition
 */
export function createBlockInstance(
  blockName: string,
  props?: Record<string, any>,
  children?: BlockInstance[]
): BlockInstance | null {
  try {
    const block = blockRegistry.get(blockName);
    if (!block) {
      logger.error(`Block not found: ${blockName}`);
      return null;
    }

    const instance: BlockInstance = {
      id: generateBlockId(blockName),
      name: blockName,
      type: block.label,
      props: {
        ...block.defaultProps,
        ...props,
      },
      children: children || [],
      metadata: {
        createdAt: Date.now(),
      },
    };

    logger.debug(`Created block instance: ${instance.id}`, {
      blockName,
      props: instance.props,
    });

    return instance;
  } catch (error) {
    logger.error(`Failed to create block instance: ${blockName}`, error);
    return null;
  }
}

/**
 * Create a block instance from canvas drop event
 */
export function createBlockFromDropEvent(
  blockName: string,
  dropX: number,
  dropY: number
): BlockInstance | null {
  const instance = createBlockInstance(blockName);
  if (instance) {
    instance.metadata = {
      ...instance.metadata,
      position: {
        x: dropX,
        y: dropY,
      },
    };
  }
  return instance;
}

/**
 * Duplicate a block instance (with new ID)
 */
export function duplicateBlockInstance(instance: BlockInstance): BlockInstance {
  const copy: BlockInstance = {
    ...instance,
    id: generateBlockId(instance.name),
    children: instance.children.map(duplicateBlockInstance),
    metadata: {
      ...instance.metadata,
      createdAt: Date.now(),
    },
  };

  logger.debug(`Duplicated block instance: ${instance.id} -> ${copy.id}`);
  return copy;
}

/**
 * Create a container with initial children
 */
export function createContainerWithChildren(
  containerName: string,
  childrenBlocks: string[],
  props?: Record<string, any>
): BlockInstance | null {
  const children = childrenBlocks
    .map((blockName) => createBlockInstance(blockName))
    .filter((child): child is BlockInstance => child !== null);

  const container = createBlockInstance(containerName, props, children);
  if (container) {
    logger.info(`Created container: ${containerName} with ${children.length} children`);
  }
  return container;
}

/**
 * Validate a block instance
 */
export function validateBlockInstance(instance: BlockInstance): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check required fields
  if (!instance.id) errors.push('Missing id');
  if (!instance.name) errors.push('Missing name');
  if (!instance.type) errors.push('Missing type');

  // Check block exists in registry
  const block = blockRegistry.get(instance.name);
  if (!block) {
    errors.push(`Block not registered: ${instance.name}`);
  }

  // Validate children are also valid
  if (instance.children && Array.isArray(instance.children)) {
    instance.children.forEach((child, idx) => {
      const childValidation = validateBlockInstance(child);
      if (!childValidation.valid) {
        errors.push(`Child ${idx}: ${childValidation.errors.join(', ')}`);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Get all instance IDs in a tree (depth-first)
 */
export function getAllInstanceIds(instance: BlockInstance): string[] {
  const ids = [instance.id];
  if (instance.children) {
    instance.children.forEach((child) => {
      ids.push(...getAllInstanceIds(child));
    });
  }
  return ids;
}

/**
 * Find instance by ID in tree
 */
export function findInstanceById(root: BlockInstance, id: string): BlockInstance | null {
  if (root.id === id) return root;

  if (root.children) {
    for (const child of root.children) {
      const found = findInstanceById(child, id);
      if (found) return found;
    }
  }

  return null;
}

/**
 * Clone entire block tree
 */
export function cloneBlockTree(instance: BlockInstance): BlockInstance {
  return {
    ...instance,
    id: generateBlockId(instance.name),
    children: instance.children.map(cloneBlockTree),
    metadata: {
      ...instance.metadata,
      createdAt: Date.now(),
    },
  };
}

/**
 * Update block instance props
 */
export function updateBlockInstanceProps(
  instance: BlockInstance,
  updates: Record<string, any>
): BlockInstance {
  return {
    ...instance,
    props: {
      ...instance.props,
      ...updates,
    },
  };
}

/**
 * Create a frame (root container) for a new template
 */
export function createTemplateFrame(title: string = 'Untitled'): BlockInstance | null {
  const frame = createBlockInstance('layout-frame', { title });
  if (frame) {
    // Add a default VStack container
    const vStack = createBlockInstance('layout-vstack');
    if (vStack) {
      frame.children = [vStack];
    }
  }
  return frame;
}

/**
 * Statistics about a block tree
 */
export function getBlockTreeStats(instance: BlockInstance): {
  totalBlocks: number;
  maxDepth: number;
  blockTypes: Record<string, number>;
} {
  let totalBlocks = 1;
  let maxDepth = 1;
  const blockTypes: Record<string, number> = {
    [instance.name]: 1,
  };

  function traverse(node: BlockInstance, depth: number) {
    if (depth > maxDepth) maxDepth = depth;
    if (node.children) {
      node.children.forEach((child) => {
        totalBlocks++;
        blockTypes[child.name] = (blockTypes[child.name] || 0) + 1;
        traverse(child, depth + 1);
      });
    }
  }

  traverse(instance, 1);

  return {
    totalBlocks,
    maxDepth,
    blockTypes,
  };
}

export default {
  createBlockInstance,
  createBlockFromDropEvent,
  duplicateBlockInstance,
  createContainerWithChildren,
  validateBlockInstance,
  getAllInstanceIds,
  findInstanceById,
  cloneBlockTree,
  updateBlockInstanceProps,
  createTemplateFrame,
  getBlockTreeStats,
};
