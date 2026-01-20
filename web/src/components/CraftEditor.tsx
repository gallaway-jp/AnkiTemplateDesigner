import React, { useEffect, useRef, useCallback, useState } from 'react';
import { Editor as CraftEditor, Frame, useEditor } from '@craftjs/core';
import { editorStore } from '@/stores';
import { logger } from '@/utils/logger';
import { createBlockFromDropEvent } from '@/services/blockInstantiator';
import { blockRegistry } from '@/services/blockRegistry';
import '../styles/CraftEditor.css';

// Component for rendering selected/hovering elements
const RenderNode: React.FC = () => {
  const { selected, hovered } = useEditor((state) => ({
    selected: state.nodes[state.selected],
    hovered: state.nodes[state.hovered],
  }));

  return (
    <div
      style={{
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: 999,
        border: selected ? '2px solid #4CAF50' : hovered ? '2px dashed #2196F3' : 'none',
        backgroundColor:
          selected ? 'rgba(76, 175, 80, 0.1)' : hovered ? 'rgba(33, 150, 243, 0.05)' : 'transparent',
        ...(() => {
          if (selected?.dom) {
            const rect = selected.dom.getBoundingClientRect();
            return {
              top: `${rect.top}px`,
              left: `${rect.left}px`,
              width: `${rect.width}px`,
              height: `${rect.height}px`,
            };
          }
          return {};
        })(),
      }}
    />
  );
};

// Inner editor component that uses Craft.js hooks
interface InnerEditorProps {
  onEditorReady: (editor: any) => void;
  onDrop?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragOver?: (e: React.DragEvent<HTMLDivElement>) => void;
}

const InnerEditor: React.FC<InnerEditorProps> = ({ 
  onEditorReady, 
  onDrop,
  onDragOver 
}) => {
  const craftEditor = useEditor();
  const editorRef = useRef(craftEditor);

  useEffect(() => {
    if (craftEditor) {
      editorRef.current = craftEditor;
      onEditorReady(craftEditor);
    }
  }, [craftEditor, onEditorReady]);

  // Sync selection to Zustand store
  useEffect(() => {
    const subscription = craftEditor.subscribe?.(() => {
      const selected = craftEditor.selected?.getCurrentNodeDOM?.();
      if (selected) {
        // Store selected node info for properties panel
        const node = craftEditor.query?.node(craftEditor.selected)?.toNodeTree?.();
        if (node) {
          editorStore.setState((state) => ({
            ...state,
            selectedNodeId: craftEditor.selected,
            selectedNode: node,
          }));
        }
      }
    });

    return () => {
      subscription?.();
    };
  }, [craftEditor]);

  return (
    <div 
      className="craft-editor-viewport"
      onDrop={onDrop}
      onDragOver={onDragOver}
    >
      <Frame>
        <div 
          className="craft-canvas-container"
          onDrop={onDrop}
          onDragOver={onDragOver}
        >
          {/* Canvas area - blocks will be dropped here */}
        </div>
      </Frame>
      <RenderNode />
    </div>
  );
};

// Main CraftEditor component wrapper
interface CraftEditorProps {
  className?: string;
}

export const CraftEditor: React.FC<CraftEditorProps> = ({ className = '' }) => {
  const editorRef = useRef<any>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const [draggedBlock, setDraggedBlock] = useState<string | null>(null);
  
  const { template, loading, error } = editorStore((state) => ({
    template: state.template,
    loading: state.loading,
    error: state.error,
  }));

  const handleEditorReady = useCallback(async (editor: any) => {
    editorRef.current = editor;
    logger.info('CraftEditor initialized', { nodeCount: Object.keys(editor.nodes || {}).length });

    // Load existing template into canvas if available
    if (template && template.html) {
      try {
        // Parse and load template
        const html = template.html;
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // TODO: Convert DOM to Craft.js nodes and load them
        logger.info('Template loaded into canvas');
      } catch (err) {
        logger.error('Failed to load template into canvas', err);
      }
    }
  }, [template]);

  // Handle drag over to show visual feedback
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Set drag effect
    e.dataTransfer.dropEffect = 'copy';
    
    // Add visual feedback
    if (canvasRef.current) {
      canvasRef.current.classList.add('canvas-drag-over');
    }
    
    logger.debug('Drag over canvas', { 
      x: e.clientX, 
      y: e.clientY 
    });
  }, []);

  // Handle drop to instantiate block
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (canvasRef.current) {
      canvasRef.current.classList.remove('canvas-drag-over');
    }

    try {
      // Get dropped block name from data transfer
      const blockName = e.dataTransfer.getData('application/block-name');
      if (!blockName) {
        logger.warn('No block name in drop event');
        return;
      }

      // Verify block exists
      if (!blockRegistry.get(blockName)) {
        logger.error(`Block not found: ${blockName}`);
        return;
      }

      // Get canvas position
      const canvasRect = canvasRef.current?.getBoundingClientRect();
      if (!canvasRect) {
        logger.error('Canvas ref not available');
        return;
      }

      const dropX = e.clientX - canvasRect.left;
      const dropY = e.clientY - canvasRect.top;

      // Create block instance
      const instance = createBlockFromDropEvent(blockName, dropX, dropY);
      if (instance) {
        logger.info(`Block dropped: ${blockName}`, {
          position: { x: dropX, y: dropY },
          instanceId: instance.id,
        });

        // TODO: Add instance to Craft.js editor
        // This requires converting BlockInstance to Craft.js nodes

        // Show notification
        editorStore.setState((state) => ({
          ...state,
          notifications: [
            ...state.notifications,
            {
              id: Date.now().toString(),
              message: `Added ${blockRegistry.get(blockName)?.label}`,
              type: 'success',
            },
          ],
        }));
      }
    } catch (err) {
      logger.error('Drop error:', err);
    }
  }, []);

  // Handle drag leave
  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    // Only remove class if leaving the canvas area
    if (e.currentTarget === e.target) {
      if (canvasRef.current) {
        canvasRef.current.classList.remove('canvas-drag-over');
      }
    }
  }, []);

  // Handle save on keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+S or Cmd+S
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (editorRef.current) {
          const json = editorRef.current.getOptions()?.onSerialize?.();
          logger.info('Template saved', { json });
          // TODO: Sync to Python backend via bridge
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (error) {
    return (
      <div className="craft-editor-error">
        <h3>Editor Error</h3>
        <p>{error.message}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="craft-editor-loading">
        <div className="spinner" />
        <p>Loading editor...</p>
      </div>
    );
  }

  return (
    <div className={`craft-editor ${className}`}>
      <CraftEditor
        onRender={({ renderNode }) => renderNode}
        resolver={{
          // Blocks will be registered here
          // See blockRegistry.ts
        }}
        options={{
          // Craft.js configuration
          stabilizationTimeout: 200,
          onSerialize: (json) => {
            // Serialize to JSON when needed
            return json;
          },
          onDeserialize: (json) => {
            // Deserialize from JSON when loading
            return json;
          },
        }}
      >
        <InnerEditor 
          onEditorReady={handleEditorReady}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        />
      </CraftEditor>
    </div>
  );
};

export default CraftEditor;
