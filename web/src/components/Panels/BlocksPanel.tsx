/**
 * Enhanced Blocks Panel Component
 * Displays available blocks organized by category
 * Allows dragging blocks onto the canvas with full Craft.js integration
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useEditor } from '@craftjs/core';
import { blockRegistry, CraftBlock } from '@/services/blockRegistry';
import { logger } from '@/utils/logger';
import '../../styles/BlocksPanel.css';

interface BlocksCategoryProps {
  category: string;
  blocks: CraftBlock[];
  onBlockDrag: (block: CraftBlock) => void;
  isExpanded: boolean;
  onToggle: (category: string) => void;
}

/**
 * BlocksCategory - Collapsible category of blocks
 */
const BlocksCategory: React.FC<BlocksCategoryProps> = ({
  category,
  blocks,
  onBlockDrag,
  isExpanded,
  onToggle,
}) => {
  return (
    <div className="blocks-category">
      <div
        className="blocks-category-header"
        onClick={() => onToggle(category)}
      >
        <span className="blocks-category-chevron">{isExpanded ? '▼' : '▶'}</span>
        <span className="blocks-category-title">{category}</span>
        <span className="blocks-category-count">{blocks.length}</span>
      </div>

      {isExpanded && (
        <div className="blocks-category-items">
          {blocks.map((block) => (
            <BlockItem
              key={block.name}
              block={block}
              onDrag={() => onBlockDrag(block)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface BlockItemProps {
  block: CraftBlock;
  onDrag: () => void;
}

/**
 * BlockItem - Individual draggable block with preview
 */
const BlockItem: React.FC<BlockItemProps> = ({ block, onDrag }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    e.dataTransfer.effectAllowed = 'copy';

    // Set multiple data formats for compatibility
    e.dataTransfer.setData('application/json', JSON.stringify(block));
    e.dataTransfer.setData('application/block-name', block.name);
    e.dataTransfer.setData('blockName', block.name);

    // Create and set custom drag image
    const dragImage = document.createElement('div');
    dragImage.className = 'block-drag-image';
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-9999px';
    dragImage.style.padding = '12px 16px';
    dragImage.style.background = 'linear-gradient(135deg, #2196F3, #1976D2)';
    dragImage.style.color = 'white';
    dragImage.style.borderRadius = '6px';
    dragImage.style.fontWeight = '600';
    dragImage.style.fontSize = '13px';
    dragImage.style.zIndex = '10000';
    dragImage.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    dragImage.textContent = `${block.icon || '📦'} ${block.label}`;

    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);

    setIsDragging(true);
    onDrag();

    logger.debug(`Dragging block: ${block.name}`, {
      label: block.label,
      category: block.category,
    });
  };

  const handleDragEnd = () => {
    setIsDragging(false);

    // Clean up drag image elements
    document.querySelectorAll('.block-drag-image').forEach((el) => {
      el.remove();
    });
  };

  return (
    <div
      className={`block-item ${isDragging ? 'dragging' : ''}`}
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      title={block.description || block.label}
      role="button"
      tabIndex={0}
    >
      <div className="block-item-icon">{block.icon || '📦'}</div>
      <div className="block-item-content">
        <div className="block-item-label">{block.label}</div>
        {block.description && (
          <div className="block-item-description">{block.description}</div>
        )}
      </div>
      <div className="block-item-drag-indicator">⋮⋮</div>
    </div>
  );
};

interface BlocksPanelProps {
  className?: string;
}

/**
 * BlocksPanel - Main component showing all available blocks
 */
export const BlocksPanel: React.FC<BlocksPanelProps> = ({ className = '' }) => {
  const { canvasNode } = useEditor((state) => ({
    canvasNode: state.nodes.ROOT,
  }));

  const [categories, setCategories] = useState<string[]>([]);
  const [blocksByCategory, setBlocksByCategory] = useState<Map<string, CraftBlock[]>>(new Map());
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [stats, setStats] = useState({ total: 0, categories: 0 });

  // Initialize blocks from registry
  useEffect(() => {
    const initializeCategories = async () => {
      try {
        setLoading(true);

        // Get all blocks from registry
        const allBlocks = blockRegistry.getAll();

        if (allBlocks.length === 0) {
          logger.warn('No blocks found in registry');
          setLoading(false);
          return;
        }

        // Get unique categories
        const cats = Array.from(new Set(allBlocks.map((b) => b.category))).sort();
        setCategories(cats);

        // Group blocks by category
        const grouped = new Map<string, CraftBlock[]>();
        cats.forEach((cat) => {
          const catBlocks = allBlocks.filter((b) => b.category === cat);
          grouped.set(cat, catBlocks);
        });
        setBlocksByCategory(grouped);

        // Expand first category by default
        if (cats.length > 0) {
          setExpandedCategories({
            [cats[0]]: true,
          });
        }

        setStats({
          total: allBlocks.length,
          categories: cats.length,
        });

        logger.info(`Initialized block panel: ${cats.length} categories, ${allBlocks.length} blocks`);
        setLoading(false);
      } catch (error) {
        logger.error('Failed to initialize blocks panel', error);
        setLoading(false);
      }
    };

    initializeCategories();
  }, []);

  const handleBlockDrag = useCallback((block: CraftBlock) => {
    logger.debug(`Block drag initiated: ${block.name}`, {
      label: block.label,
      category: block.category,
    });
  }, []);

  const handleCategoryToggle = useCallback((category: string) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  }, []);

  const handleExpandAll = useCallback(() => {
    const expanded: Record<string, boolean> = {};
    categories.forEach((cat) => {
      expanded[cat] = true;
    });
    setExpandedCategories(expanded);
  }, [categories]);

  const handleCollapseAll = useCallback(() => {
    setExpandedCategories({});
  }, []);

  // Filter blocks and categories
  const filteredCategories = categories.filter((cat) => {
    if (!filter) return true;
    const blocks = blocksByCategory.get(cat) || [];
    const categoryMatches = cat.toLowerCase().includes(filter.toLowerCase());
    const blockMatches = blocks.some(
      (b) =>
        b.label.toLowerCase().includes(filter.toLowerCase()) ||
        b.name.toLowerCase().includes(filter.toLowerCase()) ||
        (b.description && b.description.toLowerCase().includes(filter.toLowerCase()))
    );
    return categoryMatches || blockMatches;
  });

  if (loading) {
    return (
      <div className={`blocks-panel ${className}`}>
        <div className="blocks-panel-loading">
          <div className="blocks-panel-loading-spinner">⟳</div>
          <div>Loading blocks...</div>
        </div>
      </div>
    );
  }

  const totalBlocks = Array.from(blocksByCategory.values()).reduce((sum, blocks) => sum + blocks.length, 0);

  return (
    <div className={`blocks-panel ${className}`}>
      <div className="blocks-panel-header">
        <h3 className="blocks-panel-title">Blocks</h3>
        <div className="blocks-panel-controls">
          <button
            className="blocks-panel-control-btn"
            onClick={handleExpandAll}
            title="Expand all"
          >
            ▼
          </button>
          <button
            className="blocks-panel-control-btn"
            onClick={handleCollapseAll}
            title="Collapse all"
          >
            ▶
          </button>
        </div>
      </div>

      <div className="blocks-panel-search">
        <input
          type="text"
          placeholder="Search blocks..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="blocks-panel-search-input"
          aria-label="Search blocks"
        />
        {filter && (
          <button
            className="blocks-panel-search-clear"
            onClick={() => setFilter('')}
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      <div className="blocks-panel-content">
        {filteredCategories.length === 0 ? (
          <div className="blocks-panel-empty">
            <div className="blocks-panel-empty-icon">📭</div>
            <div className="blocks-panel-empty-text">
              {filter ? 'No blocks matching your search' : 'No blocks available'}
            </div>
          </div>
        ) : (
          filteredCategories.map((category) => (
            <BlocksCategory
              key={category}
              category={category}
              blocks={blocksByCategory.get(category) || []}
              onBlockDrag={handleBlockDrag}
              isExpanded={expandedCategories[category] || false}
              onToggle={handleCategoryToggle}
            />
          ))
        )}
      </div>

      <div className="blocks-panel-footer">
        <div className="blocks-panel-stats">
          <span>{stats.categories} categories</span>
          <span className="blocks-panel-stats-separator">•</span>
          <span>{stats.total} blocks</span>
        </div>
      </div>
    </div>
  );
};

export default BlocksPanel;
