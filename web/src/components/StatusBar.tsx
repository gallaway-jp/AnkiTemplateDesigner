/**
 * Status Bar Component
 * Bottom status bar showing template info, save status, and metrics
 */

import React, { useMemo } from 'react';

interface StatusBarProps {
  templateName: string;
  isDirty: boolean;
  isSaving: boolean;
  lastSaveTime: number | null;
  fieldCount: number;
  zoomLevel: number;
}

function StatusBar({
  templateName,
  isDirty,
  isSaving,
  lastSaveTime,
  fieldCount,
  zoomLevel,
}: StatusBarProps) {
  const saveTimeFormatted = useMemo(() => {
    if (!lastSaveTime) return 'Never';
    const now = Date.now();
    const diff = now - lastSaveTime;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return 'Earlier';
  }, [lastSaveTime]);

  return (
    <div className="status-bar">
      <div className="status-section">
        <div className="status-item">
          <span className="status-label">Template:</span>
          <span className="status-value">{templateName}</span>
        </div>
      </div>

      <div className="status-section">
        <div className="status-item">
          <span className={`status-dot ${isDirty ? 'unsaved' : 'saved'}`} />
          <span className="status-value">
            {isSaving ? 'Saving...' : isDirty ? 'Unsaved' : 'Saved'}
          </span>
        </div>

        {lastSaveTime && !isDirty && (
          <div className="status-item">
            <span className="status-label">Last save:</span>
            <span className="status-value">{saveTimeFormatted}</span>
          </div>
        )}
      </div>

      <div className="status-section">
        <div className="status-item">
          <span className="status-label">Fields:</span>
          <span className="status-value">{fieldCount}</span>
        </div>

        <div className="status-item">
          <span className="status-label">Zoom:</span>
          <span className="status-value">{zoomLevel}%</span>
        </div>
      </div>

      <style>{`
        .status-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.5rem 1rem;
          background: var(--color-bg-tertiary);
          border-top: 1px solid var(--color-border);
          font-size: 0.75rem;
          height: 2rem;
          gap: 2rem;
        }

        .status-section {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .status-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          white-space: nowrap;
        }

        .status-label {
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          font-weight: 500;
        }

        .status-value {
          color: var(--color-text-primary);
          font-family: monospace;
          font-size: 0.7rem;
        }

        .status-dot {
          display: inline-flex;
          width: 0.375rem;
          height: 0.375rem;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .status-dot.saved {
          background: var(--color-success);
        }

        .status-dot.unsaved {
          background: var(--color-warning);
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @media (max-width: 768px) {
          .status-bar {
            padding: 0.4rem 0.75rem;
            gap: 1rem;
            flex-wrap: wrap;
          }

          .status-section {
            gap: 1rem;
          }

          .status-item {
            font-size: 0.65rem;
            gap: 0.25rem;
          }

          .status-label {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}

export default StatusBar;
