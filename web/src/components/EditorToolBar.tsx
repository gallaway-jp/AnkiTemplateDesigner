/**
 * Editor ToolBar Component
 * Top toolbar with undo/redo, save, zoom, and view toggle buttons
 */

import React, { useState } from 'react';
import { useUiStore } from '@stores';

interface EditorToolBarProps {
  canUndo: boolean;
  canRedo: boolean;
  isDirty: boolean;
  isSaving: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onSave: () => void;
  onShowPreview: () => void;
  previewVisible: boolean;
  templateName: string;
}

function EditorToolBar({
  canUndo,
  canRedo,
  isDirty,
  isSaving,
  onUndo,
  onRedo,
  onSave,
  onShowPreview,
  previewVisible,
  templateName,
}: EditorToolBarProps) {
  const [showZoomMenu, setShowZoomMenu] = useState(false);

  const zoomLevel = useUiStore((state) => state.zoomLevel);
  const setZoomLevel = useUiStore((state) => state.setZoomLevel);
  const zoomIn = useUiStore((state) => state.zoomIn);
  const zoomOut = useUiStore((state) => state.zoomOut);
  const resetZoom = useUiStore((state) => state.resetZoom);

  return (
    <div className="editor-toolbar">
      <div className="toolbar-section toolbar-left">
        <div className="template-title">
          <span className="title">{templateName}</span>
          {isDirty && <span className="dirty-indicator" title="Unsaved changes">●</span>}
        </div>
      </div>

      <div className="toolbar-section toolbar-center">
        <div className="button-group">
          <button
            className="toolbar-btn"
            onClick={onUndo}
            disabled={!canUndo}
            title="Undo (Ctrl+Z)"
            aria-label="Undo"
          >
            ↶
          </button>
          <button
            className="toolbar-btn"
            onClick={onRedo}
            disabled={!canRedo}
            title="Redo (Ctrl+Shift+Z)"
            aria-label="Redo"
          >
            ↷
          </button>
        </div>

        <div className="separator" />

        <div className="button-group">
          <button
            className="toolbar-btn primary"
            onClick={onSave}
            disabled={isSaving || !isDirty}
            title="Save (Ctrl+S)"
            aria-label="Save"
          >
            {isSaving ? '⏳' : '💾'} Save
          </button>
        </div>

        <div className="separator" />

        <div className="zoom-control">
          <button
            className="toolbar-btn sm"
            onClick={zoomOut}
            title="Zoom out (−10%)"
            aria-label="Zoom out"
          >
            −
          </button>

          <div className="zoom-display" role="button" onClick={() => setShowZoomMenu(!showZoomMenu)}>
            <span>{zoomLevel}%</span>
          </div>

          {showZoomMenu && (
            <div className="zoom-menu">
              {[50, 75, 100, 125, 150, 200].map((level) => (
                <button
                  key={level}
                  className={`zoom-option ${zoomLevel === level ? 'active' : ''}`}
                  onClick={() => {
                    setZoomLevel(level);
                    setShowZoomMenu(false);
                  }}
                >
                  {level}%
                </button>
              ))}
              <div className="zoom-menu-separator" />
              <button className="zoom-option" onClick={() => resetZoom()}>
                Reset
              </button>
            </div>
          )}

          <button
            className="toolbar-btn sm"
            onClick={zoomIn}
            title="Zoom in (+10%)"
            aria-label="Zoom in"
          >
            +
          </button>
        </div>

        <div className="separator" />

        <button
          className={`toolbar-btn ${previewVisible ? 'active' : ''}`}
          onClick={onShowPreview}
          title="Toggle Preview (Ctrl+P)"
          aria-label="Toggle Preview"
        >
          👁 Preview
        </button>
      </div>

      <div className="toolbar-section toolbar-right">
        <span className="status-text">
          {isSaving ? 'Saving...' : isDirty ? 'Modified' : 'Saved'}
        </span>
      </div>

      <style>{`
        .editor-toolbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.75rem 1rem;
          background: var(--color-bg-secondary);
          border-bottom: 1px solid var(--color-border);
          gap: 1rem;
          height: 3.5rem;
        }

        .toolbar-section {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .toolbar-left {
          flex: 0 0 200px;
        }

        .toolbar-center {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          justify-content: center;
        }

        .toolbar-right {
          flex: 0 0 150px;
          justify-content: flex-end;
        }

        .template-title {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          overflow: hidden;
        }

        .title {
          font-weight: 600;
          font-size: 0.95rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          color: var(--color-text-primary);
        }

        .dirty-indicator {
          display: inline-flex;
          width: 0.5rem;
          height: 0.5rem;
          background: var(--color-warning);
          border-radius: 50%;
          flex-shrink: 0;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .button-group {
          display: flex;
          gap: 0;
          border: 1px solid var(--color-border);
          border-radius: var(--border-radius-sm);
          background: var(--color-bg-primary);
          overflow: hidden;
        }

        .toolbar-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0.5rem 0.75rem;
          background: transparent;
          border: none;
          color: var(--color-text-primary);
          font-size: 0.9rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .toolbar-btn.sm {
          padding: 0.5rem;
          font-size: 1rem;
        }

        .toolbar-btn:hover:not(:disabled) {
          background: var(--color-bg-tertiary);
          color: var(--color-accent);
        }

        .toolbar-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .toolbar-btn.primary {
          background: var(--color-accent);
          color: white;
          border-radius: var(--border-radius-sm);
          margin: 0;
          border: 1px solid var(--color-accent);
        }

        .toolbar-btn.primary:hover:not(:disabled) {
          background: var(--color-accent-hover);
          border-color: var(--color-accent-hover);
        }

        .toolbar-btn.active {
          background: var(--color-accent);
          color: white;
          border-radius: var(--border-radius-sm);
        }

        .separator {
          width: 1px;
          height: 1.5rem;
          background: var(--color-border);
        }

        .zoom-control {
          display: flex;
          align-items: center;
          gap: 0;
          border: 1px solid var(--color-border);
          border-radius: var(--border-radius-sm);
          background: var(--color-bg-primary);
          overflow: hidden;
          position: relative;
        }

        .zoom-display {
          padding: 0.5rem 0.75rem;
          min-width: 3.5rem;
          text-align: center;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          background: transparent;
          color: var(--color-text-primary);
          user-select: none;
          transition: background 0.2s;
        }

        .zoom-display:hover {
          background: var(--color-bg-tertiary);
        }

        .zoom-menu {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--color-bg-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--border-radius-sm);
          margin-top: 0.25rem;
          z-index: 1000;
          min-width: 80px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }

        .zoom-option {
          display: block;
          width: 100%;
          padding: 0.5rem 0.75rem;
          background: none;
          border: none;
          color: var(--color-text-primary);
          text-align: left;
          cursor: pointer;
          font-size: 0.85rem;
          transition: all 0.2s;
        }

        .zoom-option:hover {
          background: var(--color-bg-tertiary);
          color: var(--color-accent);
        }

        .zoom-option.active {
          background: var(--color-accent);
          color: white;
          font-weight: 600;
        }

        .zoom-menu-separator {
          height: 1px;
          background: var(--color-border);
          margin: 0.25rem 0;
        }

        .status-text {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          white-space: nowrap;
        }

        @media (max-width: 768px) {
          .editor-toolbar {
            flex-wrap: wrap;
            height: auto;
            gap: 0.5rem;
          }

          .toolbar-center {
            width: 100%;
            justify-content: flex-start;
            flex-wrap: wrap;
          }

          .title {
            font-size: 0.85rem;
          }

          .toolbar-btn {
            font-size: 0.8rem;
            padding: 0.4rem 0.6rem;
          }
        }
      `}</style>
    </div>
  );
}

export default EditorToolBar;
