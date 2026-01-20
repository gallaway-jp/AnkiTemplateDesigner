/**
 * Styled Editor - Main Application Component
 * Responsive, themeable editor with full styling
 */

import React, { useState, useEffect } from 'react';
import { useUiStore } from '../stores';
import { useTheme } from '../styles/StyleProvider';
import { StyledPropertiesPanel, StyledLayersPanel, StyledBlocksPanel } from './StyledPanels';

/**
 * Main Editor Layout Component
 */
export const StyledEditor: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const sidebarWidth = useUIStore((state) => state.sidebarWidth);
  const setSidebarWidth = useUIStore((state) => state.setSidebarWidth);
  const [selectedBlock, setSelectedBlock] = useState<any | null>(null);
  const [blocks, setBlocks] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Mock blocks for demo
  useEffect(() => {
    setBlocks([
      { id: 'block-1', type: 'Container', label: 'Root Container', category: 'Layout' },
      { id: 'block-2', type: 'Section', label: 'Section', category: 'Layout' },
      { id: 'block-3', type: 'Button', label: 'Button', category: 'Button' },
      { id: 'block-4', type: 'Input', label: 'Text Input', category: 'Input' },
    ]);
  }, []);

  const mainContainerStyle: React.CSSProperties = {
    display: 'flex',
    width: '100%',
    height: '100vh',
    backgroundColor: 'var(--color-background)',
    color: 'var(--color-text)',
    fontFamily: 'inherit',
    transition: 'all var(--transition-base)',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 'var(--spacing-md)',
    backgroundColor: 'var(--color-surface)',
    borderBottom: '1px solid var(--color-border)',
    boxShadow: 'var(--shadow-sm)',
    gap: 'var(--spacing-md)',
    zIndex: 10,
  };

  const logoStyle: React.CSSProperties = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: 'var(--color-primary)',
  };

  const toolbarStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--spacing-md)',
  };

  const buttonStyle: React.CSSProperties = {
    padding: 'var(--spacing-sm) var(--spacing-md)',
    backgroundColor: 'var(--color-primary)',
    color: '#ffffff',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    transition: 'all var(--transition-fast)',
  };

  const sidebarStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-md)',
    width: sidebarOpen ? `${sidebarWidth}px` : '60px',
    backgroundColor: 'var(--color-background)',
    borderRight: '1px solid var(--color-border)',
    padding: sidebarOpen ? 'var(--spacing-md)' : 'var(--spacing-sm)',
    transition: 'all var(--transition-base)',
    overflowY: 'auto',
    zIndex: 9,
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  };

  const canvasStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'var(--color-backgroundAlt)',
    border: '2px dashed var(--color-border)',
    margin: 'var(--spacing-md)',
    borderRadius: 'var(--radius-lg)',
    overflow: 'auto',
  };

  const statusBarStyle: React.CSSProperties = {
    padding: 'var(--spacing-sm) var(--spacing-md)',
    backgroundColor: 'var(--color-surface)',
    borderTop: '1px solid var(--color-border)',
    fontSize: '0.8125rem',
    color: 'var(--color-textSecondary)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const tabButtonStyle = (isActive: boolean): React.CSSProperties => ({
    padding: 'var(--spacing-sm) var(--spacing-md)',
    backgroundColor: isActive ? 'var(--color-surface)' : 'transparent',
    color: isActive ? 'var(--color-primary)' : 'var(--color-textSecondary)',
    border: isActive ? '1px solid var(--color-border)' : 'none',
    borderBottom: isActive ? '2px solid var(--color-primary)' : 'none',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    transition: 'all var(--transition-fast)',
    width: '100%',
    textAlign: 'left',
  });

  const [activeTab, setActiveTab] = useState<'properties' | 'layers' | 'blocks'>('properties');

  return (
    <div style={mainContainerStyle}>
      {/* Header */}
      <div style={{ ...headerStyle, position: 'fixed', top: 0, left: 0, right: 0, height: '60px' }}>
        <div style={logoStyle}>✨ Anki Template Designer</div>
        <div style={toolbarStyle}>
          <button
            onClick={toggleTheme}
            style={{
              ...buttonStyle,
              backgroundColor: 'transparent',
              color: 'var(--color-text)',
              border: '1px solid var(--color-border)',
            }}
            title="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={buttonStyle}>
            {sidebarOpen ? '◀' : '▶'}
          </button>
          <button style={buttonStyle}>💾 Save</button>
          <button style={buttonStyle}>📤 Export</button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', flex: 1, marginTop: '60px' }}>
        {/* Sidebar */}
        <div style={sidebarStyle}>
          {sidebarOpen && (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <button
                  onClick={() => setActiveTab('properties')}
                  style={tabButtonStyle(activeTab === 'properties')}
                >
                  ⚙️ Properties
                </button>
                <button
                  onClick={() => setActiveTab('layers')}
                  style={tabButtonStyle(activeTab === 'layers')}
                >
                  📑 Layers
                </button>
                <button
                  onClick={() => setActiveTab('blocks')}
                  style={tabButtonStyle(activeTab === 'blocks')}
                >
                  🧩 Blocks
                </button>
              </div>

              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                {activeTab === 'properties' && (
                  <StyledPropertiesPanel
                    selectedBlock={selectedBlock}
                    onPropertyChange={(property, value) => {
                      if (selectedBlock) {
                        setSelectedBlock({
                          ...selectedBlock,
                          [property]: value,
                        });
                      }
                    }}
                  />
                )}
                {activeTab === 'layers' && (
                  <StyledLayersPanel
                    blocks={blocks}
                    selectedId={selectedBlock?.id}
                    onSelect={(id) => {
                      const block = blocks.find((b) => b.id === id);
                      setSelectedBlock(block || null);
                    }}
                  />
                )}
                {activeTab === 'blocks' && (
                  <StyledBlocksPanel blocks={blocks} />
                )}
              </div>
            </>
          )}
        </div>

        {/* Canvas Area */}
        <div style={contentStyle}>
          <div style={canvasStyle}>
            <div
              style={{
                textAlign: 'center',
                color: 'var(--color-textSecondary)',
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }}>🎨</div>
              <p>Drag blocks here to design your template</p>
              <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                {selectedBlock ? `Selected: ${selectedBlock.label}` : 'No block selected'}
              </p>
            </div>
          </div>

          {/* Status Bar */}
          <div style={statusBarStyle}>
            <span>Blocks: {blocks.length}</span>
            <span>Theme: {theme === 'light' ? '☀️ Light' : '🌙 Dark'}</span>
            <span>Selected: {selectedBlock?.label || 'None'}</span>
          </div>
        </div>
      </div>

      {/* Responsive Styles */}
      <style>{`
        @media (max-width: 1024px) {
          /* Reduce sidebar width on tablets */
        }

        @media (max-width: 768px) {
          /* Mobile layout */
          body {
            font-size: 14px;
          }
        }

        @media (max-width: 480px) {
          /* Small mobile layout */
          body {
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default StyledEditor;
