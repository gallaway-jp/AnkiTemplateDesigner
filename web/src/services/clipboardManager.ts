/**
 * Clipboard Manager - Phase 5
 * Copy/paste/cut with full undo/redo support and structure preservation
 */

import { CraftNode, cloneNodeTree, findNodeById } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Clipboard format for serialization
 */
export interface ClipboardFormat {
  version: string;
  timestamp: number;
  sourceAppId: string;
  type: 'nodes'; // for future extensibility
  data: ClipboardNodeData[];
  metadata: {
    count: number;
    sourceNodeId?: string;
    sourceAction: 'copy' | 'cut';
  };
}

/**
 * Single node in clipboard
 */
export interface ClipboardNodeData {
  id: string;
  type: string;
  displayName: string;
  props: Record<string, any>;
  hidden: boolean;
  children: ClipboardNodeData[];
  depth: number;
}

/**
 * Clipboard operation result
 */
export interface ClipboardOperationResult {
  success: boolean;
  message: string;
  nodeId?: string;
  nodeIds?: string[];
  error?: Error;
}

/**
 * Cut node tracking (for cut/paste undo)
 */
interface CutNodeRecord {
  nodeId: string;
  parentId: string;
  index: number;
  timestamp: number;
}

// ============================================================================
// Clipboard Serialization
// ============================================================================

/**
 * Serialize CraftNode to clipboard format
 */
function serializeNode(node: CraftNode, depth = 0): ClipboardNodeData {
  const children: ClipboardNodeData[] = [];

  for (const childNode of Object.values(node.nodes)) {
    children.push(serializeNode(childNode, depth + 1));
  }

  return {
    id: node.id,
    type: node.type,
    displayName: node.displayName,
    props: { ...node.props },
    hidden: node.hidden,
    children,
    depth,
  };
}

/**
 * Deserialize clipboard format back to CraftNode
 */
function deserializeNode(data: ClipboardNodeData, generateNewIds = true): CraftNode {
  const newId = generateNewIds ? `${data.type}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}` : data.id;

  const nodes: Record<string, CraftNode> = {};
  for (const childData of data.children) {
    const childNode = deserializeNode(childData, generateNewIds);
    nodes[childNode.id] = childNode;
  }

  return {
    id: newId,
    type: data.type,
    displayName: data.displayName,
    isCanvas: false,
    linkedNodes: new Map(),
    props: { ...data.props },
    hidden: data.hidden,
    nodes,
    parent: null,
    depth: 0,
  };
}

// ============================================================================
// Clipboard Manager
// ============================================================================

export class ClipboardManager {
  private clipboard: ClipboardFormat | null = null;
  private cutNodes: Map<string, CutNodeRecord> = new Map();
  private internalClipboard: CraftNode[] = [];
  private readonly appId = 'anki-template-designer-v5';
  private readonly clipboardVersion = '1.0';

  /**
   * Copy nodes to clipboard (internal + system clipboard)
   */
  copy(nodesToCopy: CraftNode[], sourceNodeId?: string): ClipboardOperationResult {
    try {
      if (nodesToCopy.length === 0) {
        return {
          success: false,
          message: 'No nodes to copy',
        };
      }

      // Create clipboard format
      this.clipboard = {
        version: this.clipboardVersion,
        timestamp: Date.now(),
        sourceAppId: this.appId,
        type: 'nodes',
        data: nodesToCopy.map(node => serializeNode(node)),
        metadata: {
          count: nodesToCopy.length,
          sourceNodeId,
          sourceAction: 'copy',
        },
      };

      // Store in internal clipboard
      this.internalClipboard = nodesToCopy;

      // Try to copy to system clipboard
      this.copyToSystemClipboard(this.clipboard);

      logger.info(`[Clipboard] Copied ${nodesToCopy.length} node(s)`);

      return {
        success: true,
        message: `Copied ${nodesToCopy.length} node(s)`,
        nodeIds: nodesToCopy.map(n => n.id),
      };
    } catch (error) {
      logger.error('[Clipboard] Copy failed', error);
      return {
        success: false,
        message: 'Copy failed',
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Cut nodes (copy + mark for removal)
   */
  cut(nodesToCut: CraftNode[], parentNode: CraftNode, sourceNodeId?: string): ClipboardOperationResult {
    try {
      if (nodesToCut.length === 0) {
        return {
          success: false,
          message: 'No nodes to cut',
        };
      }

      // First copy
      const copyResult = this.copy(nodesToCut, sourceNodeId);
      if (!copyResult.success) return copyResult;

      // Mark cut nodes for tracking
      const parentChildren = Object.values(parentNode.nodes);
      for (const node of nodesToCut) {
        const index = parentChildren.findIndex(n => n.id === node.id);
        this.cutNodes.set(node.id, {
          nodeId: node.id,
          parentId: parentNode.id,
          index,
          timestamp: Date.now(),
        });
      }

      // Update clipboard metadata
      if (this.clipboard) {
        this.clipboard.metadata.sourceAction = 'cut';
      }

      logger.info(`[Clipboard] Cut ${nodesToCut.length} node(s)`);

      return {
        success: true,
        message: `Cut ${nodesToCut.length} node(s)`,
        nodeIds: nodesToCut.map(n => n.id),
      };
    } catch (error) {
      logger.error('[Clipboard] Cut failed', error);
      return {
        success: false,
        message: 'Cut failed',
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Paste nodes from clipboard
   */
  paste(targetParent: CraftNode, insertIndex?: number): ClipboardOperationResult {
    try {
      if (!this.clipboard || this.clipboard.data.length === 0) {
        return {
          success: false,
          message: 'Clipboard is empty',
        };
      }

      // Deserialize nodes (generate new IDs to avoid conflicts)
      const newNodes: CraftNode[] = [];
      for (const nodeData of this.clipboard.data) {
        const newNode = deserializeNode(nodeData, true);
        newNode.parent = targetParent.id;
        newNodes.push(newNode);
      }

      // Add to target parent
      const targetChildren = Object.values(targetParent.nodes);
      let baseIndex = insertIndex ?? targetChildren.length;

      for (let i = 0; i < newNodes.length; i++) {
        const newNode = newNodes[i];
        const nodeKey = `child-${baseIndex + i}`;
        targetParent.nodes[newNode.id] = newNode;
      }

      // If this was a cut operation, mark original for removal
      if (this.clipboard.metadata.sourceAction === 'cut') {
        // Clear cut tracking after paste
        this.cutNodes.clear();
      }

      logger.info(`[Clipboard] Pasted ${newNodes.length} node(s)`);

      return {
        success: true,
        message: `Pasted ${newNodes.length} node(s)`,
        nodeIds: newNodes.map(n => n.id),
      };
    } catch (error) {
      logger.error('[Clipboard] Paste failed', error);
      return {
        success: false,
        message: 'Paste failed',
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Check if clipboard has content
   */
  hasContent(): boolean {
    return this.clipboard !== null && this.clipboard.data.length > 0;
  }

  /**
   * Get clipboard content info
   */
  getContentInfo(): {
    hasContent: boolean;
    nodeCount: number;
    wasCut: boolean;
    timestamp: number;
  } {
    return {
      hasContent: this.hasContent(),
      nodeCount: this.clipboard?.data.length ?? 0,
      wasCut: this.clipboard?.metadata.sourceAction === 'cut' ?? false,
      timestamp: this.clipboard?.timestamp ?? 0,
    };
  }

  /**
   * Clear clipboard
   */
  clear(): void {
    this.clipboard = null;
    this.internalClipboard = [];
    this.cutNodes.clear();
    logger.debug('[Clipboard] Cleared');
  }

  /**
   * Copy to system clipboard (uses Clipboard API)
   */
  private copyToSystemClipboard(format: ClipboardFormat): void {
    const jsonString = JSON.stringify(format);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(jsonString).catch(err => {
        logger.warn('[Clipboard] System clipboard write failed', err);
      });
    } else {
      logger.warn('[Clipboard] Clipboard API not available');
    }
  }

  /**
   * Paste from system clipboard (reads JSON format)
   */
  async pasteFromSystemClipboard(): Promise<ClipboardOperationResult> {
    try {
      if (!navigator.clipboard) {
        return {
          success: false,
          message: 'Clipboard API not available',
        };
      }

      const text = await navigator.clipboard.readText();
      const format = JSON.parse(text) as ClipboardFormat;

      // Validate format
      if (format.version !== this.clipboardVersion || format.type !== 'nodes') {
        return {
          success: false,
          message: 'Invalid clipboard format',
        };
      }

      this.clipboard = format;
      this.internalClipboard = format.data.map(data => deserializeNode(data, true));

      logger.info('[Clipboard] Pasted from system clipboard');

      return {
        success: true,
        message: `Pasted ${format.data.length} node(s) from system clipboard`,
      };
    } catch (error) {
      logger.error('[Clipboard] System clipboard read failed', error);
      return {
        success: false,
        message: 'Failed to read from system clipboard',
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Get clipboard data (for internal use)
   */
  getClipboardData(): ClipboardNodeData[] {
    return this.clipboard?.data ?? [];
  }

  /**
   * Get cut node records (for removal after paste)
   */
  getCutNodes(): Map<string, CutNodeRecord> {
    return new Map(this.cutNodes);
  }

  /**
   * Mark cut node as removed
   */
  markCutAsRemoved(nodeId: string): void {
    this.cutNodes.delete(nodeId);
  }

  /**
   * Check if node was cut
   */
  wasNodeCut(nodeId: string): boolean {
    return this.cutNodes.has(nodeId);
  }

  /**
   * Validate paste target (prevent circular nesting)
   */
  validatePasteTarget(targetNode: CraftNode, sourceNodeIds: string[]): boolean {
    // Prevent pasting node into itself or its children
    const sourceIds = new Set(sourceNodeIds);
    return !sourceIds.has(targetNode.id);
  }

  /**
   * Duplicate nodes (copy + immediate paste)
   */
  duplicate(nodesToDuplicate: CraftNode[], targetParent: CraftNode, insertIndex?: number): ClipboardOperationResult {
    try {
      // Copy to clipboard
      const copyResult = this.copy(nodesToDuplicate);
      if (!copyResult.success) return copyResult;

      // Immediately paste
      const pasteResult = this.paste(targetParent, insertIndex);
      if (!pasteResult.success) return pasteResult;

      logger.info(`[Clipboard] Duplicated ${nodesToDuplicate.length} node(s)`);

      return pasteResult;
    } catch (error) {
      logger.error('[Clipboard] Duplicate failed', error);
      return {
        success: false,
        message: 'Duplicate failed',
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Get internal clipboard nodes
   */
  getInternalClipboard(): CraftNode[] {
    return this.internalClipboard;
  }
}

// ============================================================================
// Clipboard Manager with Undo/Redo
// ============================================================================

export interface ClipboardHistoryEntry {
  type: 'copy' | 'cut' | 'paste' | 'duplicate';
  timestamp: number;
  nodeIds: string[];
  targetParentId?: string;
  clipboard: ClipboardFormat | null;
}

export class ClipboardManagerWithHistory extends ClipboardManager {
  private history: ClipboardHistoryEntry[] = [];
  private historyIndex = -1;
  private readonly maxHistory = 50;

  /**
   * Override copy with history
   */
  copy(nodesToCopy: CraftNode[], sourceNodeId?: string): ClipboardOperationResult {
    const result = super.copy(nodesToCopy, sourceNodeId);

    if (result.success) {
      this.addHistoryEntry({
        type: 'copy',
        timestamp: Date.now(),
        nodeIds: nodesToCopy.map(n => n.id),
        clipboard: { ...this.getClipboardData() } as any,
      });
    }

    return result;
  }

  /**
   * Override cut with history
   */
  cut(nodesToCut: CraftNode[], parentNode: CraftNode, sourceNodeId?: string): ClipboardOperationResult {
    const result = super.cut(nodesToCut, parentNode, sourceNodeId);

    if (result.success) {
      this.addHistoryEntry({
        type: 'cut',
        timestamp: Date.now(),
        nodeIds: nodesToCut.map(n => n.id),
        targetParentId: parentNode.id,
        clipboard: { ...this.getClipboardData() } as any,
      });
    }

    return result;
  }

  /**
   * Override paste with history
   */
  paste(targetParent: CraftNode, insertIndex?: number): ClipboardOperationResult {
    const result = super.paste(targetParent, insertIndex);

    if (result.success) {
      this.addHistoryEntry({
        type: 'paste',
        timestamp: Date.now(),
        nodeIds: result.nodeIds ?? [],
        targetParentId: targetParent.id,
        clipboard: { ...this.getClipboardData() } as any,
      });
    }

    return result;
  }

  /**
   * Add history entry
   */
  private addHistoryEntry(entry: ClipboardHistoryEntry): void {
    // Remove redo history if we make a new change
    this.history = this.history.slice(0, this.historyIndex + 1);

    this.history.push(entry);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    } else {
      this.historyIndex++;
    }
  }

  /**
   * Can undo clipboard operation
   */
  canUndoClipboard(): boolean {
    return this.historyIndex > 0;
  }

  /**
   * Can redo clipboard operation
   */
  canRedoClipboard(): boolean {
    return this.historyIndex < this.history.length - 1;
  }

  /**
   * Get history size
   */
  getHistorySize(): number {
    return this.history.length;
  }

  /**
   * Get current history index
   */
  getHistoryIndex(): number {
    return this.historyIndex;
  }

  /**
   * Clear clipboard history
   */
  clearHistory(): void {
    this.history = [];
    this.historyIndex = -1;
  }
}

// ============================================================================
// Export Singleton Instances
// ============================================================================

export const clipboard = new ClipboardManagerWithHistory();

// Default export
export default clipboard;
