/**
 * Optimized CraftEditor Component with Performance Improvements
 * - Memoized RenderNode with React.memo
 * - Throttled Craft.js subscription updates
 * - Debounced drop handler
 * - Efficient state selectors
 */

import React, { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { Editor as CraftEditor, Frame, useEditor } from '@craftjs/core';
import { useEditorStore } from '@/stores';
import { useEditorSelection } from '@/stores/selectors';
import { createLogger } from '@/utils/logger';
import { throttle, debounce, domBatchReader } from '@/utils/performance';
import { createBlockFromDropEvent } from '@/services/blockInstantiator';
import { blockRegistry } from '@/services/blockRegistry';
import '../styles/CraftEditor.css';

const logger = createLogger('CraftEditor');

/**
 * Optimized RenderNode - Only re-renders when selection/hover actually changes
 */
const RenderNode = React.memo(
  function RenderNodeComponent() {
    const { selected, hovered } = useEditor(
      (state) => ({
        selected: state.nodes[state.selected],
        hovered: state.nodes[state.hovered],
      }),
      (prev, next) => {
        // Only re-render if selected or hovered DOM elements actually changed
        return prev.selected?.dom === next.selected?.dom && 
               prev.hovered?.dom === next.hovered?.dom;
      }
    );

    // Memoize rect calculation to avoid getBoundingClientRect() on every render
    const rect = useMemo(() => {
      if (selected?.dom) {
        return selected.dom.getBoundingClientRect();
      }
      if (hovered?.dom) {
        return hovered.dom.getBoundingClientRect();
      }
      return null;
    }, [selected?.dom, hovered?.dom]);

    const style = useMemo(
      () => ({
        position: 'fixed' as const,
        pointerEvents: 'none' as const,
        zIndex: 999,
        border: selected
          ? '2px solid #4CAF50'
          : hovered
          ? '2px dashed #2196F3'
          : 'none',
        backgroundColor: selected
          ? 'rgba(76, 175, 80, 0.1)'
          : hovered
          ? 'rgba(33, 150, 243, 0.05)'
          : 'transparent',
        ...(rect && {
          top: `${rect.top}px`,
          left: `${rect.left}px`,
          width: `${rect.width}px`,
          height: `${rect.height}px`,
        }),
      }),
      [selected, hovered, rect]
    );

    return <div style={style} />;
  },
  (prevProps, nextProps) => {
    // Custom comparison - only re-render if props changed
    return true; // Props never change, so skip re-render
  }
);

/**
 * Inner editor with optimized Craft.js integration
 */
interface InnerEditorProps {
  onEditorReady: (editor: any) => void;
  onDrop?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragOver?: (e: React.DragEvent<HTMLDivElement>) => void;
}

const InnerEditor = React.memo(
  function InnerEditorComponent({
    onEditorReady,
    onDrop,
    onDragOver,
  }: InnerEditorProps) {
    const craftEditor = useEditor();
    const editorRef = useRef(craftEditor);
    const previousSelectedRef = useRef<string | null>(null);

    // Initialize editor
    useEffect(() => {
      if (craftEditor) {
        editorRef.current = craftEditor;
        onEditorReady(craftEditor);
      }
    }, [craftEditor, onEditorReady]);

    // Throttled update for Craft.js selection changes
    const throttledUpdateSelection = useCallback(
      throttle((selectedId: string, node: any) => {
        useEditorStore.setState((state) => ({
          ...state,
          selectedNodeId: selectedId,
          selectedNode: node,
        }));
      }, 100), // Only update max every 100ms
      []
    );

    // Subscribe to Craft.js events with filtering
    useEffect(() => {
      const subscription = craftEditor.subscribe?.(() => {
        const currentSelected = craftEditor.selected;

        // Only update if selection actually changed (not just hover)
        if (currentSelected !== previousSelectedRef.current) {
          const node = craftEditor.query
            ?.node(currentSelected)
            ?.toNodeTree?.();

          if (node) {
            throttledUpdateSelection(currentSelected, node);
          }

          previousSelectedRef.current = currentSelected;
        }
      });

      return () => {
        subscription?.();
      };
    }, [craftEditor, throttledUpdateSelection]);

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
  }
);

/**
 * Main CraftEditor wrapper component
 */
interface CraftEditorProps {
  className?: string;
}

const CraftEditorWrapper = React.memo(
  function CraftEditorComponent({ className = '' }: CraftEditorProps) {
    const editorRef = useRef<any>(null);
    const canvasRef = useRef<HTMLDivElement>(null);

    // Use optimized selectors instead of multiple hooks
    const selection = useEditorSelection();
    const { currentTemplate, isDirty, isLoading, loadError } =
      useEditorStore((state) => ({
        currentTemplate: state.currentTemplate,
        isDirty: state.isDirty,
        isLoading: state.isLoading,
        loadError: state.loadError,
      }));

    // Debounced drop handler to prevent rapid succession drops
    const debouncedHandleDrop = useCallback(
      debounce((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();

        logger.info('Block dropped');

        try {
          const block = createBlockFromDropEvent(e);
          if (block && editorRef.current) {
            editorRef.current.addBlock(block);
          }
        } catch (error) {
          logger.error('Failed to create block from drop', { error });
        }
      }, 100),
      []
    );

    const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
    }, []);

    const handleEditorReady = useCallback((editor: any) => {
      editorRef.current = editor;
      logger.info('Craft.js editor initialized');
    }, []);

    if (isLoading) {
      return <div className="craft-editor-loading">Loading editor...</div>;
    }

    if (loadError) {
      return (
        <div className="craft-editor-error">
          Failed to load editor: {loadError}
        </div>
      );
    }

    return (
      <div className={`craft-editor-wrapper ${className}`}>
        <CraftEditor
          onRender={() => {}}
          resolver={blockRegistry.getResolver()}
        >
          <InnerEditor
            onEditorReady={handleEditorReady}
            onDrop={debouncedHandleDrop}
            onDragOver={handleDragOver}
          />
        </CraftEditor>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Skip re-render if props haven't changed
    return prevProps.className === nextProps.className;
  }
);

CraftEditorWrapper.displayName = 'CraftEditor';

export default CraftEditorWrapper;
