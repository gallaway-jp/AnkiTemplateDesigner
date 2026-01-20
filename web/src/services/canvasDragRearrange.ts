/**
 * Canvas Drag-to-Rearrange Service
 * Handles moving nodes within canvas to reorganize tree structure
 */

import {
  CraftNode,
  findNodeById,
  getNodeParent,
  moveNode,
  addChildNode,
  removeChildNode,
  updateNodeInTree,
} from './canvasNodeRenderer';
import { editorStore } from '@/stores';
import { logger } from '@/utils/logger';

/**
 * Drag state during rearrange
 */
export interface DragRearrangeState {
  draggedNodeId: string | null;
  draggedNode: CraftNode | null;
  targetParentId: string | null;
  targetIndex: number | null;
  isValidDrop: boolean;
  dragOverIndicator: 'before' | 'after' | 'inside' | null;
}

let dragRearrangeState: DragRearrangeState = {
  draggedNodeId: null,
  draggedNode: null,
  targetParentId: null,
  targetIndex: null,
  isValidDrop: false,
  dragOverIndicator: null,
};

/**
 * Start dragging a node for rearrangement
 */
export function startDragRearrange(
  rootNode: CraftNode,
  nodeId: string
): boolean {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.error(`Node not found: ${nodeId}`);
      return false;
    }

    // Can't drag root node
    if (!node.parent) {
      logger.warn('Cannot drag root node');
      return false;
    }

    dragRearrangeState = {
      draggedNodeId: nodeId,
      draggedNode: node,
      targetParentId: null,
      targetIndex: null,
      isValidDrop: false,
      dragOverIndicator: null,
    };

    logger.debug(`Started dragging node: ${nodeId}`);
    return true;
  } catch (error) {
    logger.error('Failed to start drag', error);
    return false;
  }
}

/**
 * Validate if node can be dropped at target location
 */
export function validateDropTarget(
  rootNode: CraftNode,
  parentId: string | null,
  index: number | null
): { valid: boolean; reason?: string } {
  try {
    if (!dragRearrangeState.draggedNodeId) {
      return { valid: false, reason: 'No node being dragged' };
    }

    const draggedNode = dragRearrangeState.draggedNode;
    if (!draggedNode) {
      return { valid: false, reason: 'Dragged node not found' };
    }

    // Can't drop on itself
    if (parentId === draggedNode.id) {
      return { valid: false, reason: 'Cannot drop node on itself' };
    }

    // Can't drop inside its own children
    if (draggedNode.nodes[parentId || '']) {
      return { valid: false, reason: 'Cannot move node inside its children' };
    }

    // Validate index if provided
    if (index !== null && index < 0) {
      return { valid: false, reason: 'Invalid drop index' };
    }

    return { valid: true };
  } catch (error) {
    logger.error('Drop validation error', error);
    return { valid: false, reason: 'Validation error' };
  }
}

/**
 * Handle drag over for visual feedback
 */
export function handleDragOver(
  rootNode: CraftNode,
  parentId: string | null,
  index: number | null,
  position: 'before' | 'after' | 'inside' = 'inside'
): boolean {
  try {
    const validation = validateDropTarget(rootNode, parentId, index);
    if (!validation.valid) {
      dragRearrangeState.isValidDrop = false;
      dragRearrangeState.dragOverIndicator = null;
      return false;
    }

    dragRearrangeState.targetParentId = parentId;
    dragRearrangeState.targetIndex = index;
    dragRearrangeState.isValidDrop = true;
    dragRearrangeState.dragOverIndicator = position;

    logger.debug(`Drag over valid target: parent=${parentId}, index=${index}`);
    return true;
  } catch (error) {
    logger.error('Drag over error', error);
    return false;
  }
}

/**
 * Complete drag and drop, moving node to new location
 */
export function completeDragRearrange(
  rootNode: CraftNode
): CraftNode | null {
  try {
    if (!dragRearrangeState.isValidDrop || !dragRearrangeState.draggedNodeId) {
      logger.warn('Drag rearrange cancelled: invalid target');
      clearDragState();
      return null;
    }

    const nodeId = dragRearrangeState.draggedNodeId;
    const newParentId = dragRearrangeState.targetParentId;
    const insertIndex = dragRearrangeState.targetIndex;

    // If parentId is null, drag to root is not allowed
    if (!newParentId) {
      logger.warn('Cannot move node to root level');
      clearDragState();
      return null;
    }

    // Move the node
    const updatedRoot = moveNode(rootNode, nodeId, newParentId, insertIndex);
    if (!updatedRoot) {
      logger.error('Failed to move node');
      clearDragState();
      return null;
    }

    logger.info(`Node moved: ${nodeId} → parent=${newParentId}, index=${insertIndex}`);
    clearDragState();
    return updatedRoot;
  } catch (error) {
    logger.error('Failed to complete drag rearrange', error);
    clearDragState();
    return null;
  }
}

/**
 * Cancel drag operation
 */
export function cancelDragRearrange(): void {
  clearDragState();
  logger.debug('Drag rearrange cancelled');
}

/**
 * Clear drag state
 */
function clearDragState(): void {
  dragRearrangeState = {
    draggedNodeId: null,
    draggedNode: null,
    targetParentId: null,
    targetIndex: null,
    isValidDrop: false,
    dragOverIndicator: null,
  };
}

/**
 * Get current drag state
 */
export function getDragRearrangeState(): DragRearrangeState {
  return { ...dragRearrangeState };
}

/**
 * Move node up in parent's children list
 */
export function moveNodeUp(rootNode: CraftNode, nodeId: string): CraftNode | null {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.warn('Cannot move node up');
      return null;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) return null;

    const childIds = Object.keys(parent.nodes);
    const currentIndex = childIds.indexOf(nodeId);

    if (currentIndex <= 0) {
      logger.debug('Node is already at top');
      return null;
    }

    // Remove and re-add at new position
    const newRoot = updateNodeInTree(rootNode, node.parent, (p) =>
      removeChildNode(p, nodeId)
    );

    if (!newRoot) return null;

    return updateNodeInTree(newRoot, node.parent, (p) =>
      addChildNode(p, node, currentIndex - 1)
    );
  } catch (error) {
    logger.error('Failed to move node up', error);
    return null;
  }
}

/**
 * Move node down in parent's children list
 */
export function moveNodeDown(rootNode: CraftNode, nodeId: string): CraftNode | null {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.warn('Cannot move node down');
      return null;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) return null;

    const childIds = Object.keys(parent.nodes);
    const currentIndex = childIds.indexOf(nodeId);

    if (currentIndex >= childIds.length - 1) {
      logger.debug('Node is already at bottom');
      return null;
    }

    // Remove and re-add at new position
    const newRoot = updateNodeInTree(rootNode, node.parent, (p) =>
      removeChildNode(p, nodeId)
    );

    if (!newRoot) return null;

    return updateNodeInTree(newRoot, node.parent, (p) =>
      addChildNode(p, node, currentIndex + 1)
    );
  } catch (error) {
    logger.error('Failed to move node down', error);
    return null;
  }
}

/**
 * Move node to specific index
 */
export function moveNodeToIndex(
  rootNode: CraftNode,
  nodeId: string,
  newIndex: number
): CraftNode | null {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.error('Cannot move node');
      return null;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) return null;

    const childIds = Object.keys(parent.nodes);
    if (newIndex < 0 || newIndex >= childIds.length) {
      logger.error('Invalid target index');
      return null;
    }

    // Remove from current position
    const afterRemove = updateNodeInTree(rootNode, node.parent, (p) =>
      removeChildNode(p, nodeId)
    );

    if (!afterRemove) return null;

    // Add at new position
    return updateNodeInTree(afterRemove, node.parent, (p) =>
      addChildNode(p, node, newIndex)
    );
  } catch (error) {
    logger.error('Failed to move node to index', error);
    return null;
  }
}

/**
 * Indent node (move as child of previous sibling)
 */
export function indentNode(rootNode: CraftNode, nodeId: string): CraftNode | null {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.warn('Cannot indent node');
      return null;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) return null;

    const childIds = Object.keys(parent.nodes);
    const currentIndex = childIds.indexOf(nodeId);

    if (currentIndex === 0) {
      logger.debug('Cannot indent first child');
      return null;
    }

    // Get previous sibling
    const prevSiblingId = childIds[currentIndex - 1];
    const prevSibling = parent.nodes[prevSiblingId];

    if (!prevSibling) return null;

    // Remove from current parent
    const afterRemove = updateNodeInTree(rootNode, node.parent, (p) =>
      removeChildNode(p, nodeId)
    );

    if (!afterRemove) return null;

    // Add to previous sibling
    return updateNodeInTree(afterRemove, prevSiblingId, (p) =>
      addChildNode(p, node)
    );
  } catch (error) {
    logger.error('Failed to indent node', error);
    return null;
  }
}

/**
 * Outdent node (move to parent's level)
 */
export function outdentNode(rootNode: CraftNode, nodeId: string): CraftNode | null {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.warn('Cannot outdent node');
      return null;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent || !parent.parent) {
      logger.warn('Cannot outdent node without grandparent');
      return null;
    }

    // Find position in grandparent's children
    const grandparent = findNodeById(rootNode, parent.parent);
    if (!grandparent) return null;

    const parentIndex = Object.keys(grandparent.nodes).indexOf(parent.id);

    // Remove from parent
    let newRoot = updateNodeInTree(rootNode, node.parent, (p) =>
      removeChildNode(p, nodeId)
    );

    if (!newRoot) return null;

    // Add to grandparent after parent
    return updateNodeInTree(newRoot, parent.parent, (p) =>
      addChildNode(p, node, parentIndex + 1)
    );
  } catch (error) {
    logger.error('Failed to outdent node', error);
    return null;
  }
}

/**
 * Get rearrange operations available for a node
 */
export function getAvailableRearrangeOps(
  rootNode: CraftNode,
  nodeId: string
): {
  canMoveUp: boolean;
  canMoveDown: boolean;
  canIndent: boolean;
  canOutdent: boolean;
} {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      return {
        canMoveUp: false,
        canMoveDown: false,
        canIndent: false,
        canOutdent: false,
      };
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) {
      return {
        canMoveUp: false,
        canMoveDown: false,
        canIndent: false,
        canOutdent: false,
      };
    }

    const childIds = Object.keys(parent.nodes);
    const currentIndex = childIds.indexOf(nodeId);

    const canMoveUp = currentIndex > 0;
    const canMoveDown = currentIndex < childIds.length - 1;
    const canIndent = currentIndex > 0; // Need a previous sibling
    const canOutdent = !!parent.parent; // Need a grandparent

    return { canMoveUp, canMoveDown, canIndent, canOutdent };
  } catch (error) {
    logger.error('Failed to get rearrange operations', error);
    return {
      canMoveUp: false,
      canMoveDown: false,
      canIndent: false,
      canOutdent: false,
    };
  }
}

export default {
  startDragRearrange,
  validateDropTarget,
  handleDragOver,
  completeDragRearrange,
  cancelDragRearrange,
  getDragRearrangeState,
  moveNodeUp,
  moveNodeDown,
  moveNodeToIndex,
  indentNode,
  outdentNode,
  getAvailableRearrangeOps,
};
