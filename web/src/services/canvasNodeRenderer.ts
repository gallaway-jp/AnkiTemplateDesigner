/**
 * Canvas Node Renderer Service
 * Converts BlockInstance trees to Craft.js nodes and vice versa
 */

import { BlockInstance } from './blockInstantiator';
import { blockRegistry } from './blockRegistry';
import { logger } from '@/utils/logger';

/**
 * Represents a Craft.js node with all necessary metadata
 */
export interface CraftNode {
  id: string;
  type: string;
  displayName: string;
  isCanvas: boolean;
  linkedNodes: Record<string, string>; // id -> nodeId mappings for children
  props: Record<string, any>;
  hidden: boolean;
  nodes: Record<string, CraftNode>; // child nodes by ID
  parent: string | null;
  depth: number;
}

/**
 * Convert BlockInstance to Craft.js node format
 */
export function blockInstanceToCraftNode(
  instance: BlockInstance,
  parentId: string | null = null,
  depth: number = 0
): CraftNode {
  try {
    const block = blockRegistry.get(instance.name);
    if (!block) {
      logger.error(`Block not found in registry: ${instance.name}`);
      throw new Error(`Unknown block type: ${instance.name}`);
    }

    // Build child nodes
    const childNodes: Record<string, CraftNode> = {};
    const linkedNodes: Record<string, string> = {};

    instance.children.forEach((child, idx) => {
      const childNode = blockInstanceToCraftNode(child, instance.id, depth + 1);
      childNodes[childNode.id] = childNode;
      linkedNodes[`child-${idx}`] = childNode.id;
    });

    const craftNode: CraftNode = {
      id: instance.id,
      type: block.component.name || 'Unknown',
      displayName: block.label,
      isCanvas: instance.children.length > 0,
      props: instance.props,
      linkedNodes,
      hidden: false,
      nodes: childNodes,
      parent: parentId,
      depth,
    };

    logger.debug(`Created Craft node: ${craftNode.id}`, {
      type: craftNode.type,
      children: Object.keys(childNodes).length,
    });

    return craftNode;
  } catch (error) {
    logger.error(`Failed to convert BlockInstance to CraftNode`, error);
    throw error;
  }
}

/**
 * Convert Craft.js node back to BlockInstance
 */
export function craftNodeToBlockInstance(node: CraftNode): BlockInstance {
  try {
    // Reconstruct children from linked nodes
    const children: BlockInstance[] = [];
    Object.entries(node.linkedNodes).forEach(([key, childId]) => {
      if (node.nodes[childId]) {
        children.push(craftNodeToBlockInstance(node.nodes[childId]));
      }
    });

    const instance: BlockInstance = {
      id: node.id,
      name: getBlockNameFromCraftType(node.type),
      type: node.type,
      props: node.props,
      children,
      metadata: {
        createdAt: Date.now(),
      },
    };

    return instance;
  } catch (error) {
    logger.error(`Failed to convert CraftNode to BlockInstance`, error);
    throw error;
  }
}

/**
 * Map Craft component type to block name
 */
function getBlockNameFromCraftType(craftType: string): string {
  // This would need a reverse lookup from block registry
  // For now, using a simple heuristic
  if (craftType.includes('Frame')) return 'layout-frame';
  if (craftType.includes('VStack')) return 'layout-vstack';
  if (craftType.includes('HStack')) return 'layout-hstack';
  if (craftType.includes('Container')) return 'layout-container';
  if (craftType.includes('Section')) return 'layout-section';
  if (craftType.includes('Grid')) return 'layout-grid';
  if (craftType.includes('Heading')) return 'data-heading';
  if (craftType.includes('Paragraph')) return 'data-paragraph';
  if (craftType.includes('Field')) return 'input-text-field';
  if (craftType.includes('Button')) return 'button-primary';
  
  return 'layout-container'; // Default fallback
}

/**
 * Serialize node tree to JSON
 */
export function serializeNodeTree(node: CraftNode): string {
  try {
    return JSON.stringify(node, null, 2);
  } catch (error) {
    logger.error('Failed to serialize node tree', error);
    return '';
  }
}

/**
 * Deserialize node tree from JSON
 */
export function deserializeNodeTree(json: string): CraftNode | null {
  try {
    return JSON.parse(json) as CraftNode;
  } catch (error) {
    logger.error('Failed to deserialize node tree', error);
    return null;
  }
}

/**
 * Get all node IDs in tree (depth-first)
 */
export function getAllNodeIds(node: CraftNode): string[] {
  const ids = [node.id];
  Object.values(node.nodes).forEach((child) => {
    ids.push(...getAllNodeIds(child));
  });
  return ids;
}

/**
 * Find node by ID in tree
 */
export function findNodeById(root: CraftNode, targetId: string): CraftNode | null {
  if (root.id === targetId) return root;

  for (const child of Object.values(root.nodes)) {
    const found = findNodeById(child, targetId);
    if (found) return found;
  }

  return null;
}

/**
 * Get node's parent from root
 */
export function getNodeParent(root: CraftNode, targetId: string): CraftNode | null {
  if (root.id === targetId) return null; // Root has no parent

  for (const child of Object.values(root.nodes)) {
    if (child.id === targetId) return root;
    const found = getNodeParent(child, targetId);
    if (found) return found;
  }

  return null;
}

/**
 * Get node's siblings from root
 */
export function getNodeSiblings(
  root: CraftNode,
  targetId: string
): CraftNode[] {
  const parent = getNodeParent(root, targetId);
  if (!parent) return [];

  return Object.values(parent.nodes).filter((node) => node.id !== targetId);
}

/**
 * Update node props in tree
 */
export function updateNodeProps(
  node: CraftNode,
  updates: Record<string, any>
): CraftNode {
  return {
    ...node,
    props: {
      ...node.props,
      ...updates,
    },
  };
}

/**
 * Add child node to parent
 */
export function addChildNode(
  parent: CraftNode,
  child: CraftNode,
  atIndex?: number
): CraftNode {
  const newNodes = { ...parent.nodes };
  newNodes[child.id] = {
    ...child,
    parent: parent.id,
    depth: parent.depth + 1,
  };

  const newLinkedNodes = { ...parent.linkedNodes };
  const childIndex = atIndex ?? Object.keys(newLinkedNodes).length;
  newLinkedNodes[`child-${childIndex}`] = child.id;

  return {
    ...parent,
    nodes: newNodes,
    linkedNodes: newLinkedNodes,
    isCanvas: true, // Parent becomes a canvas once it has children
  };
}

/**
 * Remove child node from parent
 */
export function removeChildNode(parent: CraftNode, childId: string): CraftNode {
  const newNodes = { ...parent.nodes };
  delete newNodes[childId];

  const newLinkedNodes = { ...parent.linkedNodes };
  Object.entries(newLinkedNodes).forEach(([key, id]) => {
    if (id === childId) {
      delete newLinkedNodes[key];
    }
  });

  return {
    ...parent,
    nodes: newNodes,
    linkedNodes: newLinkedNodes,
    isCanvas: Object.keys(newNodes).length > 0,
  };
}

/**
 * Move node from one parent to another
 */
export function moveNode(
  root: CraftNode,
  nodeId: string,
  newParentId: string,
  atIndex?: number
): CraftNode | null {
  try {
    // Find node to move
    const nodeToMove = findNodeById(root, nodeId);
    if (!nodeToMove) {
      logger.error(`Node not found: ${nodeId}`);
      return null;
    }

    // Find old parent
    const oldParent = getNodeParent(root, nodeId);
    if (!oldParent) {
      logger.error(`Cannot move root node`);
      return null;
    }

    // Find new parent
    const newParent = findNodeById(root, newParentId);
    if (!newParent) {
      logger.error(`New parent not found: ${newParentId}`);
      return null;
    }

    // Remove from old parent
    const afterRemoval = updateNodeInTree(root, oldParent.id, (node) =>
      removeChildNode(node, nodeId)
    );

    if (!afterRemoval) return null;

    // Add to new parent
    const afterAddition = updateNodeInTree(afterRemoval, newParentId, (node) =>
      addChildNode(node, nodeToMove, atIndex)
    );

    return afterAddition;
  } catch (error) {
    logger.error('Failed to move node', error);
    return null;
  }
}

/**
 * Update a specific node in tree and return new tree
 */
export function updateNodeInTree(
  root: CraftNode,
  targetId: string,
  updater: (node: CraftNode) => CraftNode
): CraftNode {
  if (root.id === targetId) {
    return updater(root);
  }

  const newNodes = { ...root.nodes };
  Object.entries(newNodes).forEach(([id, child]) => {
    newNodes[id] = updateNodeInTree(child, targetId, updater);
  });

  return {
    ...root,
    nodes: newNodes,
  };
}

/**
 * Clone a node tree with new IDs
 */
export function cloneNodeTree(
  node: CraftNode,
  idMap: Map<string, string> = new Map()
): CraftNode {
  const newId = `${node.id}-clone-${Date.now()}`;
  idMap.set(node.id, newId);

  const newNodes: Record<string, CraftNode> = {};
  Object.entries(node.nodes).forEach(([oldId, child]) => {
    const clonedChild = cloneNodeTree(child, idMap);
    newNodes[clonedChild.id] = clonedChild;
  });

  const newLinkedNodes: Record<string, string> = {};
  Object.entries(node.linkedNodes).forEach(([key, oldChildId]) => {
    const newChildId = idMap.get(oldChildId) || oldChildId;
    newLinkedNodes[key] = newChildId;
  });

  return {
    ...node,
    id: newId,
    nodes: newNodes,
    linkedNodes: newLinkedNodes,
    parent: null,
  };
}

/**
 * Get node statistics
 */
export function getNodeTreeStats(node: CraftNode): {
  totalNodes: number;
  maxDepth: number;
  byType: Record<string, number>;
  leafNodes: number;
} {
  let totalNodes = 1;
  let maxDepth = node.depth;
  let leafNodes = Object.keys(node.nodes).length === 0 ? 1 : 0;
  const byType: Record<string, number> = { [node.type]: 1 };

  function traverse(child: CraftNode) {
    totalNodes++;
    if (child.depth > maxDepth) maxDepth = child.depth;
    if (Object.keys(child.nodes).length === 0) leafNodes++;
    byType[child.type] = (byType[child.type] || 0) + 1;

    Object.values(child.nodes).forEach(traverse);
  }

  Object.values(node.nodes).forEach(traverse);

  return {
    totalNodes,
    maxDepth,
    byType,
    leafNodes,
  };
}

/**
 * Validate node tree integrity
 */
export function validateNodeTree(node: CraftNode): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  const seen = new Set<string>();

  function validate(n: CraftNode, expectedParent: string | null) {
    // Check for duplicates
    if (seen.has(n.id)) {
      errors.push(`Duplicate node ID: ${n.id}`);
    }
    seen.add(n.id);

    // Check parent reference
    if (n.parent !== expectedParent) {
      errors.push(`Node ${n.id}: parent mismatch (expected ${expectedParent}, got ${n.parent})`);
    }

    // Check linked nodes
    Object.entries(n.linkedNodes).forEach(([key, childId]) => {
      if (!n.nodes[childId]) {
        errors.push(`Node ${n.id}: linked node not found: ${childId}`);
      }
    });

    // Validate children
    Object.values(n.nodes).forEach((child) => {
      validate(child, n.id);
    });
  }

  validate(node, null);

  return {
    valid: errors.length === 0,
    errors,
  };
}

export default {
  blockInstanceToCraftNode,
  craftNodeToBlockInstance,
  serializeNodeTree,
  deserializeNodeTree,
  getAllNodeIds,
  findNodeById,
  getNodeParent,
  getNodeSiblings,
  updateNodeProps,
  addChildNode,
  removeChildNode,
  moveNode,
  updateNodeInTree,
  cloneNodeTree,
  getNodeTreeStats,
  validateNodeTree,
};
