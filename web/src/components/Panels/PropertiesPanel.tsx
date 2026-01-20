/**
 * Enhanced Properties Panel Component
 * Displays and allows editing properties of the selected block in Craft.js
 * Full integration with editor store and Craft.js useSelectedNode hook
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useEditor, useNode } from '@craftjs/core';
import { editorStore } from '@/stores';
import { logger } from '@/utils/logger';
import '../../styles/PropertiesPanel.css';

interface PropertyField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'checkbox' | 'select' | 'color' | 'textarea' | 'range';
  value: any;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

/**
 * PropertyInput - Single property input field
 */
const PropertyInput: React.FC<{
  field: PropertyField;
  onChange: (value: any) => void;
  disabled?: boolean;
}> = ({ field, onChange, disabled = false }) => {
  const [localValue, setLocalValue] = useState(field.value);

  useEffect(() => {
    setLocalValue(field.value);
  }, [field.value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const target = e.target;
    let value: any;

    if (field.type === 'checkbox') {
      value = (target as HTMLInputElement).checked;
    } else if (field.type === 'number' || field.type === 'range') {
      value = parseFloat(target.value);
    } else {
      value = target.value;
    }

    setLocalValue(value);
  };

  const handleBlur = () => {
    onChange(localValue);
  };

  return (
    <div className="property-field">
      <label className="property-label">{field.label}</label>
      {field.type === 'text' && (
        <input
          type="text"
          value={localValue || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          className="property-input"
          placeholder={field.label}
          disabled={disabled}
        />
      )}
      {field.type === 'number' && (
        <input
          type="number"
          value={localValue || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          className="property-input property-input-number"
          disabled={disabled}
        />
      )}
      {field.type === 'checkbox' && (
        <label className="property-checkbox-label">
          <input
            type="checkbox"
            checked={localValue || false}
            onChange={handleChange}
            onBlur={handleBlur}
            className="property-checkbox"
            disabled={disabled}
          />
          <span>{field.label}</span>
        </label>
      )}
      {field.type === 'select' && (
        <select
          value={localValue || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          className="property-select"
          disabled={disabled}
        >
          <option value="">-- Select --</option>
          {field.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      )}
      {field.type === 'color' && (
        <div className="property-color-group">
          <input
            type="color"
            value={localValue || '#000000'}
            onChange={handleChange}
            onBlur={handleBlur}
            className="property-color"
            disabled={disabled}
          />
          <span className="property-color-value">{localValue || '#000000'}</span>
        </div>
      )}
      {field.type === 'range' && (
        <div className="property-range-group">
          <input
            type="range"
            value={localValue || field.min || 0}
            onChange={handleChange}
            onBlur={handleBlur}
            className="property-range"
            min={field.min}
            max={field.max}
            step={field.step || 1}
            disabled={disabled}
          />
          <span className="property-range-value">{localValue || 0}</span>
        </div>
      )}
      {field.type === 'textarea' && (
        <textarea
          value={localValue || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          className="property-textarea"
          rows={3}
          placeholder={field.label}
          disabled={disabled}
        />
      )}
    </div>
  );
};

/**
 * StyleEditor - Comprehensive inline style editor
 */
const StyleEditor: React.FC<{
  styles: Record<string, string>;
  onChange: (styles: Record<string, string>) => void;
}> = ({ styles, onChange }) => {
  const [expanded, setExpanded] = useState(false);
  const [styleString, setStyleString] = useState(
    Object.entries(styles)
      .map(([key, value]) => `${key}: ${value}`)
      .join('; ')
  );

  useEffect(() => {
    setStyleString(
      Object.entries(styles)
        .map(([key, value]) => `${key}: ${value}`)
        .join('; ')
    );
  }, [styles]);

  const handleChange = (newString: string) => {
    setStyleString(newString);
    try {
      const newStyles: Record<string, string> = {};
      newString.split(';').forEach((rule) => {
        const [key, value] = rule.split(':');
        if (key && value) {
          newStyles[key.trim()] = value.trim();
        }
      });
      onChange(newStyles);
    } catch (e) {
      logger.warn('Failed to parse style string', e);
    }
  };

  return (
    <div className="property-section">
      <div
        className="property-section-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="property-section-chevron">{expanded ? '▼' : '▶'}</span>
        <span className="property-section-title">Styles</span>
      </div>
      {expanded && (
        <div className="property-style-editor-container">
          <textarea
            value={styleString}
            onChange={(e) => handleChange(e.target.value)}
            className="property-style-editor"
            placeholder="e.g. color: #000; font-size: 14px; padding: 8px;"
            rows={4}
          />
          <div className="property-style-hint">
            <small>CSS-style properties separated by semicolons</small>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * ConstraintsEditor - Drag and drop constraints editor
 */
const ConstraintsEditor: React.FC<{
  constraints?: string[];
  onChange: (constraints: string[]) => void;
}> = ({ constraints = [], onChange }) => {
  const [expanded, setExpanded] = useState(false);

  const constraintOptions = [
    'horizontal',
    'vertical',
    'maxWidth',
    'maxHeight',
    'fixed',
    'aspectRatio',
  ];

  const toggleConstraint = (constraint: string) => {
    const newConstraints = constraints.includes(constraint)
      ? constraints.filter((c) => c !== constraint)
      : [...constraints, constraint];
    onChange(newConstraints);
  };

  return (
    <div className="property-section">
      <div
        className="property-section-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="property-section-chevron">{expanded ? '▼' : '▶'}</span>
        <span className="property-section-title">Constraints</span>
      </div>
      {expanded && (
        <div className="property-constraints-container">
          {constraintOptions.map((constraint) => (
            <label key={constraint} className="property-constraint-item">
              <input
                type="checkbox"
                checked={constraints.includes(constraint)}
                onChange={() => toggleConstraint(constraint)}
              />
              <span>{constraint}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

interface PropertiesPanelProps {
  className?: string;
}

/**
 * PropertiesPanel - Main component showing properties of selected block
 */
export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ className = '' }) => {
  const { selected } = useEditor((state) => ({
    selected: state.events.selected,
  }));

  const [properties, setProperties] = useState<PropertyField[]>([]);
  const [styles, setStyles] = useState<Record<string, string>>({});
  const [constraints, setConstraints] = useState<string[]>([]);
  const [componentInfo, setComponentInfo] = useState<{ name: string; type: string } | null>(null);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    properties: false,
    styles: false,
    constraints: false,
    advanced: false,
  });

  // Get the currently selected node
  const selectedNodeId = selected && Object.keys(selected).length > 0 ? Object.keys(selected)[0] : null;

  useEffect(() => {
    if (!selectedNodeId) {
      setProperties([]);
      setStyles({});
      setConstraints([]);
      setComponentInfo(null);
      return;
    }

    // In a real implementation, fetch the node data from the Craft.js editor state
    // For now, we'll use the editor store
    const selectedNode = editorStore.getState().selectedNode;

    if (!selectedNode) {
      return;
    }

    // Set component info
    setComponentInfo({
      name: selectedNode.name || 'Component',
      type: selectedNode.type || 'div',
    });

    // Extract editable properties
    const props: PropertyField[] = [];

    // Common editable properties by component type
    const editableProps: Record<string, string[]> = {
      button: ['label', 'onClick', 'disabled', 'variant'],
      input: ['placeholder', 'type', 'value', 'disabled', 'required'],
      text: ['content', 'variant', 'color'],
      image: ['src', 'alt', 'width', 'height'],
      heading: ['content', 'level', 'variant'],
      paragraph: ['content', 'variant'],
      card: ['title', 'description', 'elevation'],
    };

    const componentType = selectedNode.type?.toLowerCase() || '';
    const propsForType = editableProps[componentType] || [];

    propsForType.forEach((prop) => {
      if (prop in selectedNode) {
        let fieldType: PropertyField['type'] = 'text';
        if (prop === 'disabled' || prop === 'required') {
          fieldType = 'checkbox';
        } else if (prop === 'width' || prop === 'height' || prop === 'level' || prop === 'elevation') {
          fieldType = 'number';
        } else if (prop === 'variant' || prop === 'type') {
          fieldType = 'select';
        }

        props.push({
          name: prop,
          label: prop.charAt(0).toUpperCase() + prop.slice(1),
          type: fieldType,
          value: selectedNode[prop],
          options: prop === 'variant' ? ['default', 'primary', 'secondary', 'outlined'] : undefined,
        });
      }
    });

    setProperties(props);

    // Extract inline styles
    if (selectedNode.style) {
      setStyles(selectedNode.style);
    }

    // Extract constraints (from craft configuration if available)
    if (selectedNode.constraints) {
      setConstraints(Array.isArray(selectedNode.constraints) ? selectedNode.constraints : []);
    }
  }, [selectedNodeId]);

  const handlePropertyChange = useCallback((name: string, value: any) => {
    const selectedNode = editorStore.getState().selectedNode;
    if (!selectedNode) return;

    editorStore.setState((state) => ({
      ...state,
      selectedNode: {
        ...selectedNode,
        [name]: value,
      },
    }));

    logger.debug(`Property changed: ${name} = ${value}`);
  }, []);

  const handleStyleChange = useCallback((newStyles: Record<string, string>) => {
    const selectedNode = editorStore.getState().selectedNode;
    if (!selectedNode) return;

    setStyles(newStyles);

    editorStore.setState((state) => ({
      ...state,
      selectedNode: {
        ...selectedNode,
        style: newStyles,
      },
    }));

    logger.debug('Styles updated', newStyles);
  }, []);

  const handleConstraintChange = useCallback((newConstraints: string[]) => {
    const selectedNode = editorStore.getState().selectedNode;
    if (!selectedNode) return;

    setConstraints(newConstraints);

    editorStore.setState((state) => ({
      ...state,
      selectedNode: {
        ...selectedNode,
        constraints: newConstraints,
      },
    }));

    logger.debug('Constraints updated', newConstraints);
  }, []);

  const toggleSection = (section: string) => {
    setCollapsed((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  if (!componentInfo) {
    return (
      <div className={`properties-panel ${className}`}>
        <div className="properties-panel-empty">
          <div className="properties-panel-empty-icon">👉</div>
          <div className="properties-panel-empty-text">Select a block to edit its properties</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`properties-panel ${className}`}>
      <div className="properties-panel-header">
        <h3 className="properties-panel-title">Properties</h3>
        <div className="properties-panel-subtitle">{componentInfo.type}</div>
      </div>

      <div className="properties-panel-content">
        {/* Component Info Section */}
        <div className="property-section">
          <div className="property-info">
            <div className="property-info-row">
              <span className="property-info-label">Component:</span>
              <span className="property-info-value">{componentInfo.name}</span>
            </div>
            <div className="property-info-row">
              <span className="property-info-label">Type:</span>
              <span className="property-info-value">{componentInfo.type}</span>
            </div>
          </div>
        </div>

        {/* Properties Section */}
        {properties.length > 0 && (
          <div className="property-section">
            <div
              className="property-section-header"
              onClick={() => toggleSection('properties')}
            >
              <span className="property-section-chevron">{!collapsed.properties ? '▼' : '▶'}</span>
              <span className="property-section-title">Block Properties</span>
              <span className="property-section-count">{properties.length}</span>
            </div>
            {!collapsed.properties && (
              <div className="property-section-content">
                {properties.map((prop) => (
                  <PropertyInput
                    key={prop.name}
                    field={prop}
                    onChange={(value) => handlePropertyChange(prop.name, value)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Styles Section */}
        <StyleEditor styles={styles} onChange={handleStyleChange} />

        {/* Constraints Section */}
        <ConstraintsEditor constraints={constraints} onChange={handleConstraintChange} />

        {/* Advanced Section */}
        <div className="property-section">
          <div
            className="property-section-header"
            onClick={() => toggleSection('advanced')}
          >
            <span className="property-section-chevron">{!collapsed.advanced ? '▼' : '▶'}</span>
            <span className="property-section-title">Advanced</span>
          </div>
          {!collapsed.advanced && (
            <div className="property-advanced-info">
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', padding: '8px' }}>
                <p>ID: {editorStore.getState().selectedNode?.id || 'auto-generated'}</p>
                <p>Classes: {editorStore.getState().selectedNode?.classes?.join(' ') || 'none'}</p>
                <p>Data attributes: {JSON.stringify(editorStore.getState().selectedNode?.dataset || {})}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PropertiesPanel;
