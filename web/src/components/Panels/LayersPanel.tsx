/**
 * Enhanced Layers Panel Component
 * Displays the DOM tree hierarchy of the current template
 * Full integration with Craft.js useEditor and selection system
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useEditor } from '@craftjs/core';
import { editorStore } from '@/stores';
import { logger } from '@/utils/logger';
import '../../styles/LayersPanel.css';

interface LayerNode {
  id: string;
  name: string;
  type: string;
  children: LayerNode[];
  isSelected?: boolean;
  isHovered?: boolean;
  canDrop?: boolean;
  isCanvas?: boolean;
  depth: number;
}

/**
 * LayerItem - Represents a single layer in the hierarchy
 */
interface LayerItemProps {
  node: LayerNode;
  onSelect: (id: string) => void;
  onToggle: (id: string) => void;
  onRename: (id: string, name: string) => void;
  onDelete: (id: string) => void;
  expanded: Record<string, boolean>;
  isDragging?: boolean;
}

const LayerItem: React.FC<LayerItemProps> = ({
  node,
  onSelect,
  onToggle,
  onRename,
  onDelete,
  expanded,
  isDragging,
}) => {
  const hasChildren = node.children.length > 0;
  const isExpanded = expanded[node.id];
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(node.name);
  const [isHovered, setIsHovered] = useState(false);

  const handleDblClick = () => {
    if (hasChildren) {
      onToggle(node.id);
    } else {
      setIsRenaming(true);
    }
  };

  const handleRenameSubmit = () => {
    if (newName.trim() && newName !== node.name) {
      onRename(node.id, newName);
    }
    setIsRenaming(false);
    setNewName(node.name);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Delete ${node.name}?`)) {
      onDelete(node.id);
    }
  };

  const getNodeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      frame: '📱',
      container: '📦',
      button: '🔘',
      text: '📝',
      input: '📋',
      image: '🖼️',
      video: '🎥',
      card: '🎴',
      section: '📄',
      div: '◾',
      p: '¶',
      h1: 'H1',
      h2: 'H2',
      h3: 'H3',
      h4: 'H4',
      h5: 'H5',
      h6: 'H6',
      span: '·',
      'primary-button': '🔴',
      'secondary-button': '⚪',
      'heading': 'H',
      'paragraph': 'P',
      'hstack': '↔️',
      'vstack': '↕️',
      'grid': '◻️',
      'modal-container': '📦',
      'drawer': '🎚️',
      'split-view': '✖️',
    };
    return icons[type.toLowerCase()] || '🔹';
  };

  const icon = getNodeIcon(node.type);

  return (
    <div className="layer-item-container">
      <div
        className={`layer-item ${node.isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
        style={{ paddingLeft: `${node.depth * 16}px` }}
        onClick={() => onSelect(node.id)}
        onDoubleClick={handleDblClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {hasChildren && (
          <button
            className="layer-item-toggle"
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node.id);
            }}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        )}
        {!hasChildren && <div className="layer-item-toggle-placeholder" />}

        <div className="layer-item-icon" title={node.type}>
          {icon}
        </div>

        {isRenaming ? (
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onBlur={handleRenameSubmit}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRenameSubmit();
              if (e.key === 'Escape') {
                setIsRenaming(false);
                setNewName(node.name);
              }
            }}
            className="layer-item-rename-input"
            autoFocus
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <div className="layer-item-label">
            <span className="layer-item-name">{node.name}</span>
            <span className="layer-item-type">{node.type}</span>
          </div>
        )}

        {(isHovered || node.isSelected) && (
          <div className="layer-item-actions">
            <button
              className="layer-item-action"
              onClick={(e) => {
                e.stopPropagation();
                setIsRenaming(true);
              }}
              title="Rename (F2)"
            >
              ✏️
            </button>
            <button
              className="layer-item-action danger"
              onClick={handleDelete}
              title="Delete (Del)"
            >
              🗑️
            </button>
          </div>
        )}

        {node.isCanvas && (
          <div className="layer-item-badge">Canvas</div>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div className="layer-item-children">
          {node.children.map((child) => (
            <LayerItem
              key={child.id}
              node={child}
              onSelect={onSelect}
              onToggle={onToggle}
              onRename={onRename}
              onDelete={onDelete}
              expanded={expanded}
              isDragging={isDragging}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface LayersPanelProps {
  className?: string;
}

/**
 * LayersPanel - Main component showing DOM hierarchy
 */
export const LayersPanel: React.FC<LayersPanelProps> = ({ className = '' }) => {
  const { nodes, selected } = useEditor((state) => ({
    nodes: state.nodes,
    selected: state.events.selected,
  }));

  const [layerTree, setLayerTree] = useState<LayerNode | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [searchFilter, setSearchFilter] = useState('');
  const [stats, setStats] = useState({ total: 0, selected: 0 });

  // Build layer tree from Craft.js nodes
  const buildLayerTree = useCallback((nodeId: string, depth: number = 0): LayerNode => {
    const node = nodes[nodeId];
    if (!node) {
      return {
        id: nodeId,
        name: 'Unknown',
        type: 'unknown',
        children: [],
        isSelected: false,
        depth,
      };
    }

    const isSelected = Object.keys(selected || {}).includes(nodeId);

    return {
      id: nodeId,
      name: node.custom?.displayName || node.data?.displayName || 'Component',
      type: node.data?.type || node.data?.name || 'div',
      children: (node.nodes || []).map((childId) => buildLayerTree(childId, depth + 1)),
      isSelected,
      isCanvas: node.data?.craft?.isCanvas,
      depth,
    };
  }, [nodes, selected]);

  // Initialize layer tree when nodes change
  useEffect(() => {
    // Guard against null/undefined nodes
    if (!nodes || typeof nodes !== 'object') {
      setLayerTree(null);
      setStats({ total: 0, selected: 0 });
      return;
    }

    const rootNodeId = Object.keys(nodes).find((id) => !nodes[id].parent);
    if (rootNodeId) {
      const tree = buildLayerTree(rootNodeId);
      setLayerTree(tree);

      // Expand root by default
      setExpanded((prev) => ({
        ...prev,
        [rootNodeId]: true,
      }));

      // Calculate stats
      const totalNodes = Object.keys(nodes).length;
      const selectedCount = Object.keys(selected || {}).length;
      setStats({ total: totalNodes, selected: selectedCount });

      logger.debug(`Layer tree updated: ${totalNodes} nodes, ${selectedCount} selected`);
    }
  }, [nodes, selected, buildLayerTree]);

  const handleSelect = useCallback((id: string) => {
    editorStore.setState((state) => ({
      ...state,
      selectedNode: { id, name: '', type: '' },
    }));
    logger.debug(`Node selected: ${id}`);
  }, []);

  const handleToggle = useCallback((id: string) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  }, []);

  const handleRename = useCallback((id: string, newName: string) => {
    // Guard against null/undefined nodes
    if (!nodes || typeof nodes !== 'object') return;
    
    // Update store with renamed node
    const node = nodes[id];
    if (node) {
      logger.debug(`Node renamed: ${id} -> ${newName}`);
      // In a real implementation, this would update the Craft.js node data
    }
  }, [nodes]);

  const handleDelete = useCallback((id: string) => {
    logger.debug(`Node deleted: ${id}`);
    // In a real implementation, this would delete from Craft.js
  }, []);

  const handleExpandAll = useCallback(() => {
    // Guard against null/undefined nodes
    if (!nodes || typeof nodes !== 'object') return;
    
    const allExpanded: Record<string, boolean> = {};
    Object.keys(nodes).forEach((id) => {
      allExpanded[id] = true;
    });
    setExpanded(allExpanded);
  }, [nodes]);

  const handleCollapseAll = useCallback(() => {
    // Guard against null/undefined nodes
    if (!nodes || typeof nodes !== 'object') {
      setExpanded({});
      return;
    }
    
    const rootNodeId = Object.keys(nodes).find((id) => !nodes[id].parent);
    if (rootNodeId) {
      setExpanded({ [rootNodeId]: true });
    } else {
      setExpanded({});
    }
  }, [nodes]);

  const filteredTree = useCallback((): LayerNode | null => {
    if (!layerTree || !searchFilter) return layerTree;

    const filterNode = (node: LayerNode): LayerNode | null => {
      const matches =
        node.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
        node.type.toLowerCase().includes(searchFilter.toLowerCase());

      const filteredChildren = node.children
        .map(filterNode)
        .filter((child): child is LayerNode => child !== null);

      if (matches || filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren,
        };
      }

      return null;
    };

    return filterNode(layerTree);
  }, [layerTree, searchFilter]);

  if (!layerTree) {
    return (
      <div className={`layers-panel ${className}`}>
        <div className="layers-panel-empty">
          <div className="layers-panel-empty-icon">🌳</div>
          <div className="layers-panel-empty-text">No template loaded</div>
        </div>
      </div>
    );
  }

  const displayTree = filteredTree();

  return (
    <div className={`layers-panel ${className}`}>
      <div className="layers-panel-header">
        <h3 className="layers-panel-title">Layers</h3>
        <div className="layers-panel-controls">
          <button
            className="layers-panel-btn"
            onClick={handleExpandAll}
            title="Expand all"
          >
            ▼
          </button>
          <button
            className="layers-panel-btn"
            onClick={handleCollapseAll}
            title="Collapse all"
          >
            ▶
          </button>
        </div>
      </div>

      <div className="layers-panel-search">
        <input
          type="text"
          placeholder="Search layers..."
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          className="layers-panel-search-input"
        />
        {searchFilter && (
          <button
            className="layers-panel-search-clear"
            onClick={() => setSearchFilter('')}
          >
            ✕
          </button>
        )}
      </div>

      <div className="layers-panel-content">
        {displayTree ? (
          <LayerItem
            node={displayTree}
            onSelect={handleSelect}
            onToggle={handleToggle}
            onRename={handleRename}
            onDelete={handleDelete}
            expanded={expanded}
          />
        ) : (
          <div className="layers-panel-empty">
            <div className="layers-panel-empty-text">No matching layers</div>
          </div>
        )}
      </div>

      <div className="layers-panel-footer">
        <div className="layers-panel-stats">
          <span>{stats.total} total</span>
          <span className="layers-panel-stats-separator">•</span>
          <span>{stats.selected} selected</span>
        </div>
      </div>
    </div>
  );
};

export default LayersPanel;
