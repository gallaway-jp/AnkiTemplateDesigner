/**
 * Keyboard Navigation System - Phase 5
 * Full keyboard control for canvas: arrow keys, enter, space, delete, etc.
 */

import { CraftNode, findNodeById, getNodeParent } from './canvasNodeRenderer';
import { canvasOptimization } from './canvasOptimization';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Keyboard navigation context
 */
export interface NavigationContext {
  currentNodeId: string | null;
  parentNodeId: string | null;
  nextSiblingId: string | null;
  prevSiblingId: string | null;
  firstChildId: string | null;
  canNavigateUp: boolean;
  canNavigateDown: boolean;
  canNavigateLeft: boolean;
  canNavigateRight: boolean;
}

/**
 * Keyboard action mapping
 */
export interface KeyboardAction {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: (context: NavigationContext, root: CraftNode) => void;
  description: string;
}

/**
 * Keyboard shortcuts configuration
 */
export interface KeyboardConfig {
  enableArrowNavigation: boolean;
  enableCharacterShortcuts: boolean;
  enableModifierShortcuts: boolean;
  wrapAroundNavigation: boolean;
  loopOnBounds: boolean;
}

// ============================================================================
// Navigation Helpers
// ============================================================================

/**
 * Get all siblings of a node (for navigation)
 */
function getSiblings(root: CraftNode, nodeId: string): CraftNode[] {
  const node = findNodeById(root, nodeId);
  if (!node) return [];

  const parent = getNodeParent(root, nodeId);
  if (!parent) return [];

  return Object.values(parent.nodes);
}

/**
 * Get sibling at specific index relative to current node
 */
function getSiblingAtIndex(root: CraftNode, nodeId: string, indexOffset: number): CraftNode | null {
  const node = findNodeById(root, nodeId);
  if (!node) return null;

  const parent = getNodeParent(root, nodeId);
  if (!parent) return null;

  const siblings = Object.values(parent.nodes);
  const currentIndex = siblings.findIndex(s => s.id === nodeId);
  const newIndex = currentIndex + indexOffset;

  if (newIndex >= 0 && newIndex < siblings.length) {
    return siblings[newIndex];
  }

  return null;
}

/**
 * Get next visible sibling (skips hidden nodes)
 */
function getNextVisibleSibling(root: CraftNode, nodeId: string): CraftNode | null {
  const parent = getNodeParent(root, nodeId);
  if (!parent) return null;

  const siblings = Object.values(parent.nodes);
  const currentIndex = siblings.findIndex(s => s.id === nodeId);

  for (let i = currentIndex + 1; i < siblings.length; i++) {
    if (!siblings[i].hidden) {
      return siblings[i];
    }
  }

  return null;
}

/**
 * Get previous visible sibling (skips hidden nodes)
 */
function getPrevVisibleSibling(root: CraftNode, nodeId: string): CraftNode | null {
  const parent = getNodeParent(root, nodeId);
  if (!parent) return null;

  const siblings = Object.values(parent.nodes);
  const currentIndex = siblings.findIndex(s => s.id === nodeId);

  for (let i = currentIndex - 1; i >= 0; i--) {
    if (!siblings[i].hidden) {
      return siblings[i];
    }
  }

  return null;
}

/**
 * Get first child (if any)
 */
function getFirstChild(node: CraftNode): CraftNode | null {
  const children = Object.values(node.nodes);
  return children.length > 0 ? children[0] : null;
}

/**
 * Get last child (if any)
 */
function getLastChild(node: CraftNode): CraftNode | null {
  const children = Object.values(node.nodes);
  return children.length > 0 ? children[children.length - 1] : null;
}

/**
 * Get deepest node in tree (for End key)
 */
function getDeepestNode(root: CraftNode): CraftNode {
  let current = root;
  let lastChild = getLastChild(current);

  while (lastChild) {
    current = lastChild;
    lastChild = getLastChild(current);
  }

  return current;
}

// ============================================================================
// Navigation Context Builder
// ============================================================================

/**
 * Build navigation context for current node
 */
export function getNavigationContext(root: CraftNode, nodeId: string | null): NavigationContext {
  if (!nodeId) {
    return {
      currentNodeId: null,
      parentNodeId: null,
      nextSiblingId: null,
      prevSiblingId: null,
      firstChildId: null,
      canNavigateUp: false,
      canNavigateDown: false,
      canNavigateLeft: false,
      canNavigateRight: false,
    };
  }

  const node = findNodeById(root, nodeId);
  if (!node) {
    return {
      currentNodeId: nodeId,
      parentNodeId: null,
      nextSiblingId: null,
      prevSiblingId: null,
      firstChildId: null,
      canNavigateUp: false,
      canNavigateDown: false,
      canNavigateLeft: false,
      canNavigateRight: false,
    };
  }

  const parent = getNodeParent(root, nodeId);
  const nextSibling = getNextVisibleSibling(root, nodeId);
  const prevSibling = getPrevVisibleSibling(root, nodeId);
  const firstChild = getFirstChild(node);

  return {
    currentNodeId: nodeId,
    parentNodeId: parent?.id || null,
    nextSiblingId: nextSibling?.id || null,
    prevSiblingId: prevSibling?.id || null,
    firstChildId: firstChild?.id || null,
    canNavigateUp: !!prevSibling || (parent && parent !== root),
    canNavigateDown: !!nextSibling,
    canNavigateLeft: !!parent && parent !== root, // Up in hierarchy
    canNavigateRight: !!firstChild, // Down into children
  };
}

// ============================================================================
// Keyboard Navigation Manager
// ============================================================================

export class KeyboardNavigationManager {
  private root: CraftNode | null = null;
  private currentNodeId: string | null = null;
  private config: KeyboardConfig = {
    enableArrowNavigation: true,
    enableCharacterShortcuts: true,
    enableModifierShortcuts: true,
    wrapAroundNavigation: false,
    loopOnBounds: true,
  };

  private actions: Map<string, KeyboardAction> = new Map();

  /**
   * Initialize navigation with root node
   */
  initialize(root: CraftNode, config?: Partial<KeyboardConfig>): void {
    this.root = root;
    if (config) {
      this.config = { ...this.config, ...config };
    }

    this.setupDefaultActions();
    logger.info('[KeyboardNavigation] Initialized');
  }

  /**
   * Set current navigation node
   */
  setCurrentNode(nodeId: string | null): void {
    this.currentNodeId = nodeId;
  }

  /**
   * Get current navigation node ID
   */
  getCurrentNode(): string | null {
    return this.currentNodeId;
  }

  /**
   * Navigate up (previous sibling or up in hierarchy)
   */
  navigateUp(): string | null {
    if (!this.root || !this.currentNodeId) return null;

    const context = getNavigationContext(this.root, this.currentNodeId);

    if (context.canNavigateUp) {
      const nextNodeId = context.prevSiblingId || context.parentNodeId;
      if (nextNodeId) {
        this.setCurrentNode(nextNodeId);
        logger.debug(`[KeyboardNavigation] Navigated up to ${nextNodeId}`);
        return nextNodeId;
      }
    }

    return null;
  }

  /**
   * Navigate down (next sibling or down in hierarchy)
   */
  navigateDown(): string | null {
    if (!this.root || !this.currentNodeId) return null;

    const context = getNavigationContext(this.root, this.currentNodeId);

    // Prefer next sibling, then first child
    if (context.canNavigateDown) {
      const nextNodeId = context.nextSiblingId;
      if (nextNodeId) {
        this.setCurrentNode(nextNodeId);
        logger.debug(`[KeyboardNavigation] Navigated down to ${nextNodeId}`);
        return nextNodeId;
      }
    }

    return null;
  }

  /**
   * Navigate left (out of children, to parent)
   */
  navigateLeft(): string | null {
    if (!this.root || !this.currentNodeId) return null;

    const context = getNavigationContext(this.root, this.currentNodeId);

    if (context.canNavigateLeft) {
      const nextNodeId = context.parentNodeId;
      if (nextNodeId) {
        this.setCurrentNode(nextNodeId);
        logger.debug(`[KeyboardNavigation] Navigated left to ${nextNodeId}`);
        return nextNodeId;
      }
    }

    return null;
  }

  /**
   * Navigate right (into children)
   */
  navigateRight(): string | null {
    if (!this.root || !this.currentNodeId) return null;

    const context = getNavigationContext(this.root, this.currentNodeId);

    if (context.canNavigateRight) {
      const nextNodeId = context.firstChildId;
      if (nextNodeId) {
        this.setCurrentNode(nextNodeId);
        logger.debug(`[KeyboardNavigation] Navigated right to ${nextNodeId}`);
        return nextNodeId;
      }
    }

    return null;
  }

  /**
   * Navigate to first node (Home key)
   */
  navigateToFirst(): string | null {
    if (!this.root) return null;

    const firstChild = getFirstChild(this.root);
    if (firstChild) {
      this.setCurrentNode(firstChild.id);
      logger.debug(`[KeyboardNavigation] Navigated to first node ${firstChild.id}`);
      return firstChild.id;
    }

    return null;
  }

  /**
   * Navigate to last node (End key)
   */
  navigateToLast(): string | null {
    if (!this.root) return null;

    const lastNode = getDeepestNode(this.root);
    if (lastNode && lastNode !== this.root) {
      this.setCurrentNode(lastNode.id);
      logger.debug(`[KeyboardNavigation] Navigated to last node ${lastNode.id}`);
      return lastNode.id;
    }

    return null;
  }

  /**
   * Navigate to parent
   */
  navigateToParent(): string | null {
    if (!this.root || !this.currentNodeId) return null;

    const parent = getNodeParent(this.root, this.currentNodeId);
    if (parent && parent !== this.root) {
      this.setCurrentNode(parent.id);
      logger.debug(`[KeyboardNavigation] Navigated to parent ${parent.id}`);
      return parent.id;
    }

    return null;
  }

  /**
   * Setup default keyboard actions
   */
  private setupDefaultActions(): void {
    // Arrow key navigation
    if (this.config.enableArrowNavigation) {
      this.registerAction({
        key: 'ArrowUp',
        action: () => this.navigateUp(),
        description: 'Navigate to previous sibling',
      });

      this.registerAction({
        key: 'ArrowDown',
        action: () => this.navigateDown(),
        description: 'Navigate to next sibling',
      });

      this.registerAction({
        key: 'ArrowLeft',
        action: () => this.navigateLeft(),
        description: 'Navigate to parent',
      });

      this.registerAction({
        key: 'ArrowRight',
        action: () => this.navigateRight(),
        description: 'Navigate to first child',
      });
    }

    // Navigation keys
    this.registerAction({
      key: 'Home',
      action: () => this.navigateToFirst(),
      description: 'Navigate to first node',
    });

    this.registerAction({
      key: 'End',
      action: () => this.navigateToLast(),
      description: 'Navigate to last node',
    });

    // Selection actions
    this.registerAction({
      key: 'Enter',
      action: (ctx) => {
        logger.info(`[KeyboardNavigation] Selected node ${ctx.currentNodeId}`);
        return null;
      },
      description: 'Select current node',
    });

    this.registerAction({
      key: ' ', // Space
      action: (ctx) => {
        logger.info(`[KeyboardNavigation] Toggled selection on ${ctx.currentNodeId}`);
        return null;
      },
      description: 'Toggle selection on current node',
    });

    // Common shortcuts
    if (this.config.enableModifierShortcuts) {
      this.registerAction({
        key: 'Delete',
        action: (ctx) => {
          logger.info(`[KeyboardNavigation] Delete node ${ctx.currentNodeId}`);
          return null;
        },
        description: 'Delete current node',
      });

      this.registerAction({
        key: 'z',
        ctrlKey: true,
        action: () => {
          logger.info('[KeyboardNavigation] Undo');
          return null;
        },
        description: 'Undo last action',
      });

      this.registerAction({
        key: 'y',
        ctrlKey: true,
        action: () => {
          logger.info('[KeyboardNavigation] Redo');
          return null;
        },
        description: 'Redo last action',
      });

      this.registerAction({
        key: 'x',
        ctrlKey: true,
        action: (ctx) => {
          logger.info(`[KeyboardNavigation] Cut node ${ctx.currentNodeId}`);
          return null;
        },
        description: 'Cut current node',
      });

      this.registerAction({
        key: 'c',
        ctrlKey: true,
        action: (ctx) => {
          logger.info(`[KeyboardNavigation] Copy node ${ctx.currentNodeId}`);
          return null;
        },
        description: 'Copy current node',
      });

      this.registerAction({
        key: 'v',
        ctrlKey: true,
        action: () => {
          logger.info('[KeyboardNavigation] Paste');
          return null;
        },
        description: 'Paste from clipboard',
      });

      this.registerAction({
        key: 'd',
        ctrlKey: true,
        action: (ctx) => {
          logger.info(`[KeyboardNavigation] Duplicate node ${ctx.currentNodeId}`);
          return null;
        },
        description: 'Duplicate current node',
      });
    }
  }

  /**
   * Register keyboard action
   */
  registerAction(action: KeyboardAction): void {
    const key = this.getActionKey(action);
    this.actions.set(key, action);
  }

  /**
   * Unregister keyboard action
   */
  unregisterAction(key: string, ctrlKey?: boolean, shiftKey?: boolean): void {
    const actionKey = this.getKeyCode(key, ctrlKey, shiftKey);
    this.actions.delete(actionKey);
  }

  /**
   * Handle keyboard event
   */
  handleKeyDown(event: KeyboardEvent): boolean {
    if (!this.root) return false;

    const key = this.getActionKey({
      key: event.key,
      ctrlKey: event.ctrlKey,
      shiftKey: event.shiftKey,
      altKey: event.altKey,
      action: () => {},
      description: '',
    });

    const action = this.actions.get(key);
    if (!action) return false;

    const context = getNavigationContext(this.root, this.currentNodeId);
    action.action(context, this.root);

    event.preventDefault();
    return true;
  }

  /**
   * Get action key string for mapping
   */
  private getActionKey(action: KeyboardAction): string {
    return this.getKeyCode(action.key, action.ctrlKey, action.shiftKey);
  }

  /**
   * Generate key code string
   */
  private getKeyCode(key: string, ctrlKey?: boolean, shiftKey?: boolean): string {
    const parts = [];
    if (ctrlKey) parts.push('ctrl');
    if (shiftKey) parts.push('shift');
    parts.push(key.toLowerCase());
    return parts.join('+');
  }

  /**
   * Get all registered actions
   */
  getActions(): KeyboardAction[] {
    return Array.from(this.actions.values());
  }

  /**
   * Get navigation context for current node
   */
  getContext(): NavigationContext {
    if (!this.root) {
      return {
        currentNodeId: null,
        parentNodeId: null,
        nextSiblingId: null,
        prevSiblingId: null,
        firstChildId: null,
        canNavigateUp: false,
        canNavigateDown: false,
        canNavigateLeft: false,
        canNavigateRight: false,
      };
    }

    return getNavigationContext(this.root, this.currentNodeId);
  }

  /**
   * Reset navigation state
   */
  reset(): void {
    this.currentNodeId = null;
    this.root = null;
    this.actions.clear();
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const keyboardNavigation = new KeyboardNavigationManager();

// Default export
export default keyboardNavigation;
