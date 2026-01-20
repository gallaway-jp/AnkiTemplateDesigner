/**
 * Block Property Updater Service
 * Handles real-time property changes with validation and undo/redo support
 */

import { CraftNode, updateNodeProps, findNodeById } from './canvasNodeRenderer';
import { editorStore } from '@/stores';
import { logger } from '@/utils/logger';

/**
 * Property change history for undo/redo
 */
export interface PropertyChangeHistory {
  changes: PropertyChange[];
  currentIndex: number;
  maxHistory: number;
}

/**
 * Single property change
 */
export interface PropertyChange {
  nodeId: string;
  timestamp: number;
  before: Record<string, any>;
  after: Record<string, any>;
}

let propertyChangeHistory: PropertyChangeHistory = {
  changes: [],
  currentIndex: -1,
  maxHistory: 50,
};

/**
 * Update property with validation and history
 */
export function updateProperty(
  rootNode: CraftNode,
  nodeId: string,
  propName: string,
  newValue: any,
  validate?: (value: any) => boolean
): boolean {
  try {
    // Validate if validator provided
    if (validate && !validate(newValue)) {
      logger.warn(`Property validation failed: ${propName}`, { value: newValue });
      return false;
    }

    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.error(`Node not found: ${nodeId}`);
      return false;
    }

    const oldValue = node.props[propName];

    // Don't record change if value hasn't actually changed
    if (oldValue === newValue) {
      return true;
    }

    // Record change in history
    recordPropertyChange(nodeId, { [propName]: oldValue }, { [propName]: newValue });

    // Update store
    editorStore.setState((state) => {
      if (state.selectedNodeId === nodeId && state.selectedNode) {
        return {
          ...state,
          selectedNode: updateNodeProps(state.selectedNode, { [propName]: newValue }),
        };
      }
      return state;
    });

    logger.debug(`Property updated: ${nodeId}.${propName}`, {
      old: oldValue,
      new: newValue,
    });

    return true;
  } catch (error) {
    logger.error(`Failed to update property: ${propName}`, error);
    return false;
  }
}

/**
 * Update multiple properties at once
 */
export function updateProperties(
  rootNode: CraftNode,
  nodeId: string,
  updates: Record<string, any>
): boolean {
  try {
    const node = findNodeById(rootNode, nodeId);
    if (!node) {
      logger.error(`Node not found: ${nodeId}`);
      return false;
    }

    const before = { ...node.props };
    const after = { ...before, ...updates };

    // Filter out unchanged values
    const actualChanges: Record<string, any> = {};
    Object.entries(updates).forEach(([key, value]) => {
      if (before[key] !== value) {
        actualChanges[key] = value;
      }
    });

    if (Object.keys(actualChanges).length === 0) {
      logger.debug('No properties changed');
      return true;
    }

    // Record change in history
    const beforeOnly: Record<string, any> = {};
    Object.keys(actualChanges).forEach((key) => {
      beforeOnly[key] = before[key];
    });
    recordPropertyChange(nodeId, beforeOnly, actualChanges);

    // Update store
    editorStore.setState((state) => {
      if (state.selectedNodeId === nodeId && state.selectedNode) {
        return {
          ...state,
          selectedNode: updateNodeProps(state.selectedNode, actualChanges),
        };
      }
      return state;
    });

    logger.debug(`Properties updated: ${nodeId}`, {
      changes: Object.keys(actualChanges),
    });

    return true;
  } catch (error) {
    logger.error('Failed to update properties', error);
    return false;
  }
}

/**
 * Record property change in history for undo/redo
 */
function recordPropertyChange(
  nodeId: string,
  before: Record<string, any>,
  after: Record<string, any>
): void {
  // Remove any changes after current index (when user makes new change after undo)
  propertyChangeHistory.changes = propertyChangeHistory.changes.slice(
    0,
    propertyChangeHistory.currentIndex + 1
  );

  // Add new change
  propertyChangeHistory.changes.push({
    nodeId,
    timestamp: Date.now(),
    before,
    after,
  });

  // Maintain max history size
  if (propertyChangeHistory.changes.length > propertyChangeHistory.maxHistory) {
    propertyChangeHistory.changes.shift();
  } else {
    propertyChangeHistory.currentIndex++;
  }
}

/**
 * Undo last property change
 */
export function undoPropertyChange(
  rootNode: CraftNode
): PropertyChange | null {
  try {
    if (propertyChangeHistory.currentIndex < 0) {
      logger.debug('Nothing to undo');
      return null;
    }

    const change = propertyChangeHistory.changes[propertyChangeHistory.currentIndex];
    propertyChangeHistory.currentIndex--;

    // Revert to previous values
    updateProperties(rootNode, change.nodeId, change.before);

    logger.debug(`Undo: reverted ${change.nodeId}`);
    return change;
  } catch (error) {
    logger.error('Failed to undo property change', error);
    return null;
  }
}

/**
 * Redo last undone property change
 */
export function redoPropertyChange(
  rootNode: CraftNode
): PropertyChange | null {
  try {
    if (
      propertyChangeHistory.currentIndex >=
      propertyChangeHistory.changes.length - 1
    ) {
      logger.debug('Nothing to redo');
      return null;
    }

    propertyChangeHistory.currentIndex++;
    const change = propertyChangeHistory.changes[propertyChangeHistory.currentIndex];

    // Apply new values
    updateProperties(rootNode, change.nodeId, change.after);

    logger.debug(`Redo: reapplied ${change.nodeId}`);
    return change;
  } catch (error) {
    logger.error('Failed to redo property change', error);
    return null;
  }
}

/**
 * Check if undo is available
 */
export function canUndo(): boolean {
  return propertyChangeHistory.currentIndex >= 0;
}

/**
 * Check if redo is available
 */
export function canRedo(): boolean {
  return propertyChangeHistory.currentIndex < propertyChangeHistory.changes.length - 1;
}

/**
 * Clear history
 */
export function clearHistory(): void {
  propertyChangeHistory = {
    changes: [],
    currentIndex: -1,
    maxHistory: 50,
  };
  logger.debug('Property change history cleared');
}

/**
 * Get history stats
 */
export function getHistoryStats(): {
  totalChanges: number;
  currentIndex: number;
  canUndo: boolean;
  canRedo: boolean;
} {
  return {
    totalChanges: propertyChangeHistory.changes.length,
    currentIndex: propertyChangeHistory.currentIndex,
    canUndo: canUndo(),
    canRedo: canRedo(),
  };
}

/**
 * Validate property value
 */
export function validatePropertyValue(
  propName: string,
  value: any
): { valid: boolean; error?: string } {
  try {
    // Type-based validation
    if (propName.includes('Width') || propName.includes('Height')) {
      if (typeof value !== 'string' && typeof value !== 'number') {
        return { valid: false, error: 'Must be string or number' };
      }
    }

    if (propName.includes('Color') || propName.includes('Background')) {
      if (typeof value !== 'string') {
        return { valid: false, error: 'Must be string' };
      }
      // Basic hex/rgb validation
      const colorRegex = /^(#[0-9A-F]{6}|rgb\(|rgba\()/i;
      if (!colorRegex.test(value)) {
        return { valid: false, error: 'Invalid color format' };
      }
    }

    if (propName.includes('Padding') || propName.includes('Margin')) {
      if (typeof value !== 'string' && typeof value !== 'number') {
        return { valid: false, error: 'Must be string or number' };
      }
    }

    if (propName === 'text' || propName === 'label') {
      if (typeof value !== 'string') {
        return { valid: false, error: 'Must be string' };
      }
    }

    return { valid: true };
  } catch (error) {
    logger.error('Validation error', error);
    return { valid: false, error: 'Validation failed' };
  }
}

/**
 * Reset property to default value
 */
export function resetPropertyToDefault(
  rootNode: CraftNode,
  nodeId: string,
  propName: string,
  defaultValue: any
): boolean {
  return updateProperty(rootNode, nodeId, propName, defaultValue);
}

/**
 * Batch update properties with single history entry
 */
export function batchUpdateProperties(
  rootNode: CraftNode,
  updates: Record<string, Record<string, any>>
): boolean {
  try {
    const allSuccess = Object.entries(updates).every(([nodeId, props]) =>
      updateProperties(rootNode, nodeId, props)
    );

    if (allSuccess) {
      logger.info(`Batch update completed: ${Object.keys(updates).length} nodes`);
    }

    return allSuccess;
  } catch (error) {
    logger.error('Batch update failed', error);
    return false;
  }
}

/**
 * Copy property from one node to another
 */
export function copyProperty(
  rootNode: CraftNode,
  fromNodeId: string,
  toNodeId: string,
  propName: string
): boolean {
  try {
    const fromNode = findNodeById(rootNode, fromNodeId);
    const toNode = findNodeById(rootNode, toNodeId);

    if (!fromNode || !toNode) {
      logger.error('Source or target node not found');
      return false;
    }

    const value = fromNode.props[propName];
    return updateProperty(rootNode, toNodeId, propName, value);
  } catch (error) {
    logger.error('Failed to copy property', error);
    return false;
  }
}

/**
 * Copy all matching properties from one node to another
 */
export function copyAllProperties(
  rootNode: CraftNode,
  fromNodeId: string,
  toNodeId: string
): number {
  try {
    const fromNode = findNodeById(rootNode, fromNodeId);
    const toNode = findNodeById(rootNode, toNodeId);

    if (!fromNode || !toNode) {
      logger.error('Source or target node not found');
      return 0;
    }

    let copiedCount = 0;
    Object.entries(fromNode.props).forEach(([propName, value]) => {
      if (updateProperty(rootNode, toNodeId, propName, value)) {
        copiedCount++;
      }
    });

    logger.info(`Copied ${copiedCount} properties from ${fromNodeId} to ${toNodeId}`);
    return copiedCount;
  } catch (error) {
    logger.error('Failed to copy all properties', error);
    return 0;
  }
}

export default {
  updateProperty,
  updateProperties,
  undoPropertyChange,
  redoPropertyChange,
  canUndo,
  canRedo,
  clearHistory,
  getHistoryStats,
  validatePropertyValue,
  resetPropertyToDefault,
  batchUpdateProperties,
  copyProperty,
  copyAllProperties,
};
