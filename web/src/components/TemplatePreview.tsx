/**
 * Template Preview Component
 * Shows a live preview of the template with sample data
 */

import React, { useEffect, useState, useCallback } from 'react';
import { Template, AnkiField } from '@types';
import { bridge } from '@services/pythonBridge';
import { createLogger } from '@utils/logger';

const logger = createLogger('TemplatePreview');

interface TemplatePreviewProps {
  template: Template | null;
  fields: AnkiField[];
  onClose: () => void;
}

function TemplatePreview({ template, fields, onClose }: TemplatePreviewProps) {
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [previewCss, setPreviewCss] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [side, setSide] = useState<'front' | 'back'>('front');

  // Generate sample field data
  const sampleFields = useCallback(() => {
    const samples: Record<string, string> = {};
    fields.forEach((field) => {
      samples[field.name] = `Sample ${field.name}`;
    });
    return samples;
  }, [fields]);

  // Update preview when template changes
  useEffect(() => {
    if (!template) {
      setPreviewHtml('');
      setPreviewCss('');
      return;
    }

    const updatePreview = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await bridge.previewTemplate(
          template.html,
          template.css || '',
          sampleFields(),
          side
        );

        setPreviewHtml(result.html);
        setPreviewCss(result.css || template.css || '');
      } catch (err) {
        logger.error('Failed to generate preview', { error: err });
        setError('Failed to generate preview');
        // Fallback to raw template
        setPreviewHtml(template.html);
        setPreviewCss(template.css || '');
      } finally {
        setIsLoading(false);
      }
    };

    updatePreview();
  }, [template, side, sampleFields]);

  return (
    <div className="template-preview">
      <div className="preview-header">
        <h3>Preview</h3>
        <button className="close-btn" onClick={onClose} aria-label="Close preview">
          ×
        </button>
      </div>

      <div className="preview-controls">
        <div className="side-toggle">
          <button
            className={`side-btn ${side === 'front' ? 'active' : ''}`}
            onClick={() => setSide('front')}
          >
            Front
          </button>
          <button
            className={`side-btn ${side === 'back' ? 'active' : ''}`}
            onClick={() => setSide('back')}
          >
            Back
          </button>
        </div>
      </div>

      {error && <div className="preview-error">{error}</div>}

      {isLoading && (
        <div className="preview-loading">
          <div className="spinner" />
          <span>Generating preview...</span>
        </div>
      )}

      <div className="preview-iframe-container">
        <iframe
          className="preview-iframe"
          title={`Template ${side} side preview`}
          srcDoc={`
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="UTF-8">
              <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                  font-family: Arial, sans-serif;
                  padding: 1rem;
                  background: white;
                }
                ${previewCss}
              </style>
            </head>
            <body>
              ${previewHtml}
            </body>
            </html>
          `}
        />
      </div>

      <style>{`
        .template-preview {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: var(--color-bg-secondary);
        }

        .preview-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid var(--color-border);
        }

        .preview-header h3 {
          margin: 0;
          font-size: 0.95rem;
          font-weight: 600;
          color: var(--color-text-primary);
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--color-text-secondary);
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0;
          width: 1.5rem;
          height: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .close-btn:hover {
          color: var(--color-text-primary);
          background: var(--color-bg-tertiary);
          border-radius: 4px;
        }

        .preview-controls {
          padding: 0.5rem 1rem;
          border-bottom: 1px solid var(--color-border);
        }

        .side-toggle {
          display: flex;
          gap: 0.25rem;
          border: 1px solid var(--color-border);
          border-radius: var(--border-radius-sm);
          background: var(--color-bg-primary);
          overflow: hidden;
        }

        .side-btn {
          flex: 1;
          padding: 0.4rem 0.75rem;
          background: transparent;
          border: none;
          color: var(--color-text-primary);
          font-size: 0.8rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .side-btn:hover {
          background: var(--color-bg-tertiary);
        }

        .side-btn.active {
          background: var(--color-accent);
          color: white;
        }

        .preview-error {
          padding: 0.75rem 1rem;
          background: var(--color-error);
          color: white;
          font-size: 0.8rem;
          text-align: center;
          margin: 0.5rem;
          border-radius: var(--border-radius-sm);
        }

        .preview-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          flex: 1;
          gap: 1rem;
          color: var(--color-text-secondary);
        }

        .spinner {
          width: 24px;
          height: 24px;
          border: 2px solid var(--color-border);
          border-top-color: var(--color-accent);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .preview-iframe-container {
          flex: 1;
          overflow: hidden;
          display: flex;
        }

        .preview-iframe {
          flex: 1;
          border: none;
          background: white;
          width: 100%;
          height: 100%;
        }

        @media (max-width: 768px) {
          .preview-header h3 {
            font-size: 0.85rem;
          }

          .side-btn {
            font-size: 0.7rem;
            padding: 0.3rem 0.5rem;
          }
        }
      `}</style>
    </div>
  );
}

export default TemplatePreview;
