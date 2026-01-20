/**
 * Canvas Selection Handler Service
 * Manages node selection, highlighting, and property updates
 */

import { editorStore } from '@/stores';
import { CraftNode, findNodeById, updateNodeProps } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

/**
 * Selection state
 */
export interface SelectionState {
  selectedNodeId: string | null;
  selectedNode: CraftNode | null;
  hoveredNodeId: string | null;
  multiSelectedIds: string[];
  selectionHistory: string[];
  currentSelectionIndex: number;
}

/**
 * Select a single node
 */
export function selectNode(rootNode: CraftNode, nodeId: string): void {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.warn(`Node not found for selection: ${nodeId}`);
      return;
    }

    editorStore.setState((state) => ({
      ...state,
      selectedNodeId: nodeId,
      selectedNode: node,
    }));

    logger.debug(`Node selected: ${nodeId}`, { displayName: node.displayName });
  } catch (error) {
    logger.error('Failed to select node', error);
  }
}

/**
 * Deselect current node
 */
export function deselectNode(): void {
  editorStore.setState((state) => ({
    ...state,
    selectedNodeId: null,
    selectedNode: null,
  }));

  logger.debug('Node deselected');
}

/**
 * Multi-select: add node to selection
 */
export function addToSelection(rootNode: CraftNode, nodeId: string): void {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.warn(`Node not found for multi-select: ${nodeId}`);
      return;
    }

    editorStore.setState((state) => {
      const multiSelected = state.multiSelectedIds || [];
      if (!multiSelected.includes(nodeId)) {
        multiSelected.push(nodeId);
      }
      return {
        ...state,
        multiSelectedIds: multiSelected,
      };
    });

    logger.debug(`Node added to selection: ${nodeId}`);
  } catch (error) {
    logger.error('Failed to add node to selection', error);
  }
}

/**
 * Multi-select: remove node from selection
 */
export function removeFromSelection(nodeId: string): void {
  editorStore.setState((state) => ({
    ...state,
    multiSelectedIds: (state.multiSelectedIds || []).filter(
      (id) => id !== nodeId
    ),
  }));

  logger.debug(`Node removed from selection: ${nodeId}`);
}

/**
 * Clear multi-selection
 */
export function clearMultiSelection(): void {
  editorStore.setState((state) => ({
    ...state,
    multiSelectedIds: [],
  }));

  logger.debug('Multi-selection cleared');
}

/**
 * Toggle node selection (add if not selected, remove if selected)
 */
export function toggleSelection(rootNode: CraftNode, nodeId: string): void {
  const state = editorStore.getState?.();
  const multiSelected = state?.multiSelectedIds || [];

  if (multiSelected.includes(nodeId)) {
    removeFromSelection(nodeId);
  } else {
    addToSelection(rootNode, nodeId);
  }
}

/**
 * Set hovered node
 */
export function setHoveredNode(nodeId: string | null): void {
  editorStore.setState((state) => ({
    ...state,
    hoveredNodeId: nodeId,
  }));
}

/**
 * Update selected node props and refresh store
 */
export function updateSelectedNodeProps(
  rootNode: CraftNode,
  updates: Record<string, any>
): CraftNode | null {
  try {
    const state = editorStore.getState?.();
    const selectedId = state?.selectedNodeId;

    if (!selectedId) {
      logger.warn('No node selected for property update');
      return null;
    }

    const updatedNode = updateNodeProps(
      findNodeById(rootNode, selectedId) || rootNode,
      updates
    );

    if (!updatedNode) {
      logger.error('Failed to update node props');
      return null;
    }

    // Update store with new node
    editorStore.setState((state) => ({
      ...state,
      selectedNode: updatedNode,
    }));

    logger.debug(`Node props updated: ${selectedId}`, { updates });
    return updatedNode;
  } catch (error) {
    logger.error('Failed to update selected node props', error);
    return null;
  }
}

/**
 * Get all selected nodes (single + multi)
 */
export function getAllSelectedIds(): string[] {
  const state = editorStore.getState?.();
  const ids: string[] = [];

  if (state?.selectedNodeId) {
    ids.push(state.selectedNodeId);
  }

  if (state?.multiSelectedIds) {
    ids.push(...state.multiSelectedIds.filter((id) => id !== state.selectedNodeId));
  }

  return ids;
}

/**
 * Select all nodes in tree
 */
export function selectAll(rootNode: CraftNode): void {
  function collectIds(node: CraftNode): string[] {
    const ids = [node.id];
    Object.values(node.nodes).forEach((child) => {
      ids.push(...collectIds(child));
    });
    return ids;
  }

  const allIds = collectIds(rootNode);
  editorStore.setState((state) => ({
    ...state,
    multiSelectedIds: allIds,
    selectedNodeId: rootNode.id,
    selectedNode: rootNode,
  }));

  logger.info(`Selected all nodes (${allIds.length} total)`);
}

/**
 * Invert selection in tree
 */
export function invertSelection(rootNode: CraftNode): void {
  function collectIds(node: CraftNode): string[] {
    const ids = [node.id];
    Object.values(node.nodes).forEach((child) => {
      ids.push(...collectIds(child));
    });
    return ids;
  }

  const state = editorStore.getState?.();
  const currentSelected = getAllSelectedIds();
  const allIds = collectIds(rootNode);
  const inverted = allIds.filter((id) => !currentSelected.includes(id));

  editorStore.setState((state) => ({
    ...state,
    multiSelectedIds: inverted,
    selectedNodeId: inverted.length > 0 ? inverted[0] : null,
  }));

  logger.debug(`Selection inverted (${inverted.length} nodes selected)`);
}

/**
 * Select node and its children
 */
export function selectNodeAndChildren(
  rootNode: CraftNode,
  nodeId: string
): void {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.warn(`Node not found: ${nodeId}`);
      return;
    }

    function collectIds(n: CraftNode): string[] {
      const ids = [n.id];
      Object.values(n.nodes).forEach((child) => {
        ids.push(...collectIds(child));
      });
      return ids;
    }

    const allIds = collectIds(node);
    editorStore.setState((state) => ({
      ...state,
      multiSelectedIds: allIds,
      selectedNodeId: nodeId,
      selectedNode: node,
    }));

    logger.debug(`Selected node and children: ${nodeId} (${allIds.length} total)`);
  } catch (error) {
    logger.error('Failed to select node and children', error);
  }
}

/**
 * Select node's siblings
 */
export function selectSiblings(
  rootNode: CraftNode,
  nodeId: string
): void {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node || !node.parent) {
      logger.warn(`Node or parent not found: ${nodeId}`);
      return;
    }

    const parent = findNodeById(rootNode, node.parent);
    if (!parent) return;

    const siblingIds = Object.values(parent.nodes)
      .map((child) => child.id)
      .filter((id) => id !== nodeId);

    editorStore.setState((state) => ({
      ...state,
      multiSelectedIds: siblingIds,
    }));

    logger.debug(`Selected siblings: ${siblingIds.length}`);
  } catch (error) {
    logger.error('Failed to select siblings', error);
  }
}

/**
 * Get selection context info
 */
export function getSelectionContext(rootNode: CraftNode): {
  selectedCount: number;
  canDelete: boolean;
  canDuplicate: boolean;
  canMove: boolean;
  commonParent: string | null;
  commonType: string | null;
} {
  const selectedIds = getAllSelectedIds();
  if (selectedIds.length === 0) {
    return {
      selectedCount: 0,
      canDelete: false,
      canDuplicate: false,
      canMove: false,
      commonParent: null,
      commonType: null,
    };
  }

  let commonParent: string | null = null;
  let commonType: string | null = null;
  let canDelete = true;

  selectedIds.forEach((id, idx) => {
    const node = findNodeById(rootNode, id);
    if (!node) return;

    // Check if root node is selected (can't delete root)
    if (node.parent === null) {
      canDelete = false;
    }

    // Track common parent
    if (idx === 0) {
      commonParent = node.parent;
    } else if (commonParent !== node.parent) {
      commonParent = null; // Not common
    }

    // Track common type
    if (idx === 0) {
      commonType = node.type;
    } else if (commonType !== node.type) {
      commonType = null; // Not common
    }
  });

  return {
    selectedCount: selectedIds.length,
    canDelete,
    canDuplicate: true,
    canMove: canDelete && commonParent !== null,
    commonParent,
    commonType,
  };
}

/**
 * Focus on node (scroll to it, select it)
 */
export function focusNode(rootNode: CraftNode, nodeId: string): void {
  try {
    selectNode(rootNode, nodeId);
    
    // Dispatch focus event that UI can listen to
    const event = new CustomEvent('node-focus', {
      detail: { nodeId },
    });
    window.dispatchEvent(event);

    logger.debug(`Focus requested for node: ${nodeId}`);
  } catch (error) {
    logger.error('Failed to focus node', error);
  }
}

/**
 * Clear all selection
 */
export function clearAllSelection(): void {
  editorStore.setState((state) => ({
    ...state,
    selectedNodeId: null,
    selectedNode: null,
    multiSelectedIds: [],
    hoveredNodeId: null,
  }));

  logger.debug('All selection cleared');
}

export default {
  selectNode,
  deselectNode,
  addToSelection,
  removeFromSelection,
  clearMultiSelection,
  toggleSelection,
  setHoveredNode,
  updateSelectedNodeProps,
  getAllSelectedIds,
  selectAll,
  invertSelection,
  selectNodeAndChildren,
  selectSiblings,
  getSelectionContext,
  focusNode,
  clearAllSelection,
};
