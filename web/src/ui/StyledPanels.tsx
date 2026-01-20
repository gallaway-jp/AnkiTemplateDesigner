/**
 * Styled Panels - Production Components with Full Styling
 * PropertiesPanel, LayersPanel, BlocksPanel with responsive design
 */

import React, { useMemo } from 'react';
import { componentStyles } from '../styles/components';

/**
 * PropertiesPanel - Styled Version
 * Property editor with responsive layout
 */
export const StyledPropertiesPanel: React.FC<{
  selectedBlock?: any;
  onPropertyChange?: (property: string, value: any) => void;
}> = ({ selectedBlock, onPropertyChange }) => {
  const panelStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    padding: 'var(--spacing-md)',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-md)',
    height: '100%',
    overflowY: 'auto',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 'var(--spacing-md)',
    marginBottom: 'var(--spacing-md)',
    borderBottom: '1px solid var(--color-border)',
    gap: 'var(--spacing-md)',
  };

  const propertyGroupStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-sm)',
  };

  const labelStyle: React.CSSProperties = {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: 'var(--color-text)',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: 'var(--spacing-sm)',
    fontSize: '0.875rem',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    backgroundColor: 'var(--color-surfaceHover)',
    color: 'var(--color-text)',
    transition: 'all var(--transition-fast)',
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600 }}>
          Properties
        </h3>
        {selectedBlock && (
          <span style={{
            fontSize: '0.75rem',
            padding: 'var(--spacing-xs) var(--spacing-sm)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            color: 'var(--color-primary)',
            borderRadius: 'var(--radius-full)',
          }}>
            {selectedBlock.type}
          </span>
        )}
      </div>

      {!selectedBlock ? (
        <div style={{
          padding: 'var(--spacing-lg)',
          textAlign: 'center',
          color: 'var(--color-textSecondary)',
        }}>
          <p>Select a block to edit properties</p>
        </div>
      ) : (
        <div style={propertyGroupStyle}>
          {/* Label Property */}
          <div>
            <label style={labelStyle}>Label</label>
            <input
              type="text"
              placeholder="Block label"
              defaultValue={selectedBlock.label || ''}
              onChange={(e) => onPropertyChange?.('label', e.target.value)}
              style={inputStyle}
            />
          </div>

          {/* Type Property */}
          <div>
            <label style={labelStyle}>Type</label>
            <select
              defaultValue={selectedBlock.type || ''}
              onChange={(e) => onPropertyChange?.('type', e.target.value)}
              style={inputStyle}
            >
              <option value="container">Container</option>
              <option value="button">Button</option>
              <option value="input">Input</option>
              <option value="text">Text</option>
              <option value="image">Image</option>
            </select>
          </div>

          {/* Disabled Checkbox */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)',
          }}>
            <input
              type="checkbox"
              id="disabled"
              defaultChecked={selectedBlock.disabled || false}
              onChange={(e) => onPropertyChange?.('disabled', e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <label htmlFor="disabled" style={{ ...labelStyle, marginBottom: 0, cursor: 'pointer' }}>
              Disabled
            </label>
          </div>

          {/* CSS Classes */}
          <div>
            <label style={labelStyle}>CSS Classes</label>
            <textarea
              placeholder="e.g., p-4 bg-blue-500 rounded"
              defaultValue={selectedBlock.className || ''}
              onChange={(e) => onPropertyChange?.('className', e.target.value)}
              style={{
                ...inputStyle,
                minHeight: '80px',
                fontFamily: 'monospace',
                fontSize: '0.8125rem',
              }}
            />
          </div>

          {/* Width & Height */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-sm)' }}>
            <div>
              <label style={labelStyle}>Width</label>
              <input
                type="text"
                placeholder="100%"
                defaultValue={selectedBlock.width || ''}
                onChange={(e) => onPropertyChange?.('width', e.target.value)}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Height</label>
              <input
                type="text"
                placeholder="auto"
                defaultValue={selectedBlock.height || ''}
                onChange={(e) => onPropertyChange?.('height', e.target.value)}
                style={inputStyle}
              />
            </div>
          </div>

          {/* Padding & Margin */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-sm)' }}>
            <div>
              <label style={labelStyle}>Padding</label>
              <input
                type="text"
                placeholder="1rem"
                defaultValue={selectedBlock.padding || ''}
                onChange={(e) => onPropertyChange?.('padding', e.target.value)}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Margin</label>
              <input
                type="text"
                placeholder="0"
                defaultValue={selectedBlock.margin || ''}
                onChange={(e) => onPropertyChange?.('margin', e.target.value)}
                style={inputStyle}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * LayersPanel - Styled Version
 * Hierarchy visualization with responsive design
 */
export const StyledLayersPanel: React.FC<{
  blocks?: any[];
  selectedId?: string;
  onSelect?: (id: string) => void;
}> = ({ blocks = [], selectedId, onSelect }) => {
  const panelStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    padding: 'var(--spacing-md)',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-md)',
    height: '100%',
    overflowY: 'auto',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 'var(--spacing-md)',
    marginBottom: 'var(--spacing-md)',
    borderBottom: '1px solid var(--color-border)',
  };

  const listStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-xs)',
    listStyle: 'none',
    padding: 0,
    margin: 0,
  };

  const itemStyle = (isSelected: boolean): React.CSSProperties => ({
    padding: 'var(--spacing-sm) var(--spacing-md)',
    borderRadius: 'var(--radius-md)',
    backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.1)' : 'var(--color-surfaceHover)',
    border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: isSelected ? 'var(--color-primary)' : 'var(--color-text)',
  });

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600 }}>
          Layers
        </h3>
        <span style={{
          fontSize: '0.75rem',
          color: 'var(--color-textSecondary)',
          padding: 'var(--spacing-xs) var(--spacing-sm)',
          backgroundColor: 'var(--color-backgroundAlt)',
          borderRadius: 'var(--radius-full)',
        }}>
          {blocks.length} items
        </span>
      </div>

      {blocks.length === 0 ? (
        <div style={{
          padding: 'var(--spacing-lg)',
          textAlign: 'center',
          color: 'var(--color-textSecondary)',
        }}>
          <p>No blocks added yet</p>
        </div>
      ) : (
        <ul style={listStyle}>
          {blocks.map((block) => (
            <li
              key={block.id}
              onClick={() => onSelect?.(block.id)}
              style={itemStyle(block.id === selectedId)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>📦</span>
                <span>{block.label || block.type}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

/**
 * BlocksPanel - Styled Version
 * Block library with categories and drag-drop support
 */
export const StyledBlocksPanel: React.FC<{
  blocks?: any[];
  onBlockDrag?: (blockType: string) => void;
}> = ({ blocks = [], onBlockDrag }) => {
  // Group blocks by category
  const groupedBlocks = useMemo(() => {
    const groups: Record<string, any[]> = {
      Layout: [],
      Input: [],
      Button: [],
      Data: [],
    };

    blocks.forEach((block) => {
      const category = block.category || 'Data';
      if (groups[category]) {
        groups[category].push(block);
      }
    });

    return groups;
  }, [blocks]);

  const panelStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    padding: 'var(--spacing-md)',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-md)',
    height: '100%',
    overflowY: 'auto',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 'var(--spacing-md)',
    marginBottom: 'var(--spacing-md)',
    borderBottom: '1px solid var(--color-border)',
  };

  const categoryStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-sm)',
  };

  const categoryTitleStyle: React.CSSProperties = {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: 'var(--color-primary)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const blockGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 'var(--spacing-sm)',
  };

  const blockItemStyle: React.CSSProperties = {
    padding: 'var(--spacing-sm)',
    backgroundColor: 'var(--color-surfaceHover)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    cursor: 'grab',
    transition: 'all var(--transition-fast)',
    fontSize: '0.8125rem',
    textAlign: 'center',
    fontWeight: 500,
    color: 'var(--color-text)',
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600 }}>
          Blocks
        </h3>
        <span style={{
          fontSize: '0.75rem',
          color: 'var(--color-textSecondary)',
          padding: 'var(--spacing-xs) var(--spacing-sm)',
          backgroundColor: 'var(--color-backgroundAlt)',
          borderRadius: 'var(--radius-full)',
        }}>
          {blocks.length} available
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
        {Object.entries(groupedBlocks).map(([category, categoryBlocks]) => (
          categoryBlocks.length > 0 && (
            <div key={category} style={categoryStyle}>
              <div style={categoryTitleStyle}>{category}</div>
              <div style={blockGridStyle}>
                {categoryBlocks.map((block) => (
                  <div
                    key={block.id}
                    draggable
                    onDragStart={() => onBlockDrag?.(block.type)}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--color-primary)';
                      (e.currentTarget as HTMLElement).style.color = '#ffffff';
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                      (e.currentTarget as HTMLElement).style.boxShadow = 'var(--shadow-md)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--color-surfaceHover)';
                      (e.currentTarget as HTMLElement).style.color = 'var(--color-text)';
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                      (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                    }}
                    style={blockItemStyle}
                  >
                    {block.label}
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
};

export default {
  PropertiesPanel: StyledPropertiesPanel,
  LayersPanel: StyledLayersPanel,
  BlocksPanel: StyledBlocksPanel,
};
