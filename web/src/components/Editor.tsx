/**
 * Main Editor Component
 * Root editor component with toolbar, canvas, panels, and preview
 * Integrates Craft.js, Zustand stores, and Python bridge
 */

import React, { useEffect, useCallback, useState } from 'react';
import { useEditorStore, useAnkiStore, useUiStore } from '@stores';
import { bridge } from '@services/pythonBridge';
import { createLogger } from '@utils/logger';
import CraftEditor from './CraftEditor';
import EditorToolBar from './EditorToolBar';
import TemplatePreview from './TemplatePreview';
import StatusBar from './StatusBar';

const logger = createLogger('Editor');

interface EditorState {
  isSaving: boolean;
  isLoading: boolean;
  error: string | null;
  lastSaveTime: number | null;
}

function Editor() {
  const [editorState, setEditorState] = useState<EditorState>({
    isSaving: false,
    isLoading: false,
    error: null,
    lastSaveTime: null,
  });

  const [showPreview, setShowPreview] = useState(false);

  // Editor Store
  const template = useEditorStore((state) => state.currentTemplate);
  const isDirty = useEditorStore((state) => state.isDirty);
  const canUndo = useEditorStore((state) => state.canUndo());
  const canRedo = useEditorStore((state) => state.canRedo());
  const undo = useEditorStore((state) => state.undo);
  const redo = useEditorStore((state) => state.redo);
  const markClean = useEditorStore((state) => state.markClean);

  // Anki Store
  const fields = useAnkiStore((state) => state.fields);

  // UI Store
  const theme = useUiStore((state) => state.theme);
  const zoomLevel = useUiStore((state) => state.zoomLevel);
  const sidebarWidth = useUiStore((state) => state.sidebarWidth);

  // Initialization
  useEffect(() => {
    const initializeEditor = async () => {
      try {
        await bridge.initialize();
        logger.info('Editor initialized successfully', {
          templateName: template?.name,
          fieldCount: fields.length,
        });
      } catch (error) {
        logger.error('Failed to initialize editor', { error });
        setEditorState((prev) => ({
          ...prev,
          error: 'Failed to initialize editor',
        }));
      }
    };

    initializeEditor();
  }, [template?.name, fields.length]);

  // Save template
  const handleSave = useCallback(async () => {
    if (!template) return;

    setEditorState((prev) => ({ ...prev, isSaving: true }));

    try {
      const result = await bridge.saveTemplate(template);
      setEditorState((prev) => ({
        ...prev,
        isSaving: false,
        lastSaveTime: Date.now(),
        error: null,
      }));
      markClean();
      logger.info('Template saved successfully', { templateId: result.templateId });
    } catch (error) {
      setEditorState((prev) => ({
        ...prev,
        isSaving: false,
        error: 'Failed to save template',
      }));
      logger.error('Failed to save template', { error });
    }
  }, [template, markClean]);

  // Load template
  const handleLoad = useCallback(async (templateId: string) => {
    setEditorState((prev) => ({ ...prev, isLoading: true }));

    try {
      const loadedTemplate = await bridge.loadTemplate(templateId);
      setEditorState((prev) => ({ ...prev, isLoading: false, error: null }));
      logger.info('Template loaded', { templateId });
    } catch (error) {
      setEditorState((prev) => ({
        ...prev,
        isLoading: false,
        error: 'Failed to load template',
      }));
      logger.error('Failed to load template', { error });
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Z: Undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        if (canUndo) undo();
      }
      // Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y: Redo
      else if (
        ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z') ||
        ((e.ctrlKey || e.metaKey) && e.key === 'y')
      ) {
        e.preventDefault();
        if (canRedo) redo();
      }
      // Ctrl/Cmd + S: Save
      else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      // Ctrl/Cmd + P: Toggle preview
      else if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        setShowPreview((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canUndo, canRedo, undo, redo, handleSave]);

  // Clear error messages
  useEffect(() => {
    if (editorState.error) {
      const timer = setTimeout(() => {
        setEditorState((prev) => ({ ...prev, error: null }));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [editorState.error]);

  return (
    <div
      className="editor-container"
      data-theme={theme}
      style={{ '--zoom-level': `${zoomLevel / 100}` } as React.CSSProperties}
    >
      <EditorToolBar
        canUndo={canUndo}
        canRedo={canRedo}
        isDirty={isDirty}
        isSaving={editorState.isSaving}
        onUndo={undo}
        onRedo={redo}
        onSave={handleSave}
        onShowPreview={() => setShowPreview(!showPreview)}
        previewVisible={showPreview}
        templateName={template?.name || 'Untitled'}
      />

      {editorState.error && (
        <div className="error-banner">
          <span>{editorState.error}</span>
          <button onClick={() => setEditorState((prev) => ({ ...prev, error: null }))}>×</button>
        </div>
      )}

      <div className="editor-layout">
        <div className="editor-main" style={{ '--sidebar-width': `${sidebarWidth}px` } as React.CSSProperties}>
          <CraftEditor template={template} fields={fields} />
        </div>

        {showPreview && (
          <div className="preview-panel">
            <TemplatePreview
              template={template}
              fields={fields}
              onClose={() => setShowPreview(false)}
            />
          </div>
        )}
      </div>

      <StatusBar
        templateName={template?.name || 'Untitled'}
        isDirty={isDirty}
        isSaving={editorState.isSaving}
        lastSaveTime={editorState.lastSaveTime}
        fieldCount={fields.length}
        zoomLevel={zoomLevel}
      />

      <style>{`
        .editor-container {
          --zoom-level: 1;
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: var(--color-bg-primary);
          color: var(--color-text-primary);
        }

        .error-banner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.75rem 1rem;
          background: var(--color-error);
          color: white;
          font-size: 0.875rem;
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }

        .error-banner button {
          background: none;
          border: none;
          color: white;
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0;
          line-height: 1;
        }

        .error-banner button:hover {
          opacity: 0.8;
        }

        .editor-layout {
          display: flex;
          flex: 1;
          gap: 0;
          overflow: hidden;
        }

        .editor-main {
          flex: 1;
          display: flex;
          overflow: hidden;
        }

        .preview-panel {
          width: 400px;
          background: var(--color-bg-secondary);
          border-left: 1px solid var(--color-border);
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        @media (max-width: 1024px) {
          .preview-panel {
            width: 300px;
          }
        }
      `}</style>
    </div>
  );
}

export default Editor;
