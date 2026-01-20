/**
 * Anki-Specific Blocks
 * Components for rendering Anki template syntax (fields, cloze, conditionals)
 */

import React, { useNode } from '@craftjs/core';
import { blockRegistry } from '@/services/blockRegistry';
import '@/styles/AnkiBlocks.css';

/**
 * AnkiField - Renders {{field}} syntax
 */
export const AnkiField: React.FC<{
  fieldName?: string;
  fallback?: string;
}> = ({ fieldName = 'Field', fallback = '' }) => {
  const { connectors } = useNode();

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className="anki-field"
      data-field={fieldName}
      title={`Anki Field: ${fieldName}`}
    >
      <code className="anki-syntax">
        {`{{${fieldName}}}`}
      </code>
      {fallback && <span className="anki-fallback">{fallback}</span>}
    </div>
  );
};

AnkiField.craft = {
  displayName: 'Anki Field',
  props: {
    fieldName: 'Field',
    fallback: '',
  },
};

/**
 * AnkiCloze - Renders {{cloze:field}} syntax
 */
export const AnkiCloze: React.FC<{
  fieldName?: string;
  clozeNumber?: number;
}> = ({ fieldName = 'Text', clozeNumber = 1 }) => {
  const { connectors } = useNode();

  return (
    <span
      ref={(ref) => connectors.connect(ref)}
      className="anki-cloze"
      data-field={fieldName}
      data-cloze={clozeNumber}
      title={`Cloze Deletion: {{cloze:${fieldName}}}`}
    >
      <code className="anki-syntax">{`{{cloze:${fieldName}}}`}</code>
    </span>
  );
};

AnkiCloze.craft = {
  displayName: 'Anki Cloze',
  props: {
    fieldName: 'Text',
    clozeNumber: 1,
  },
};

/**
 * AnkiHint - Renders {{hint:field}} syntax
 */
export const AnkiHint: React.FC<{
  fieldName?: string;
  label?: string;
}> = ({ fieldName = 'Hint', label = 'Hint' }) => {
  const { connectors } = useNode();

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className="anki-hint"
      data-field={fieldName}
      title={`Anki Hint: {{hint:${fieldName}}}`}
    >
      <button type="button" className="anki-hint-button">
        {label}
      </button>
      <div className="anki-hint-content">
        <code className="anki-syntax">{`{{hint:${fieldName}}}`}</code>
      </div>
    </div>
  );
};

AnkiHint.craft = {
  displayName: 'Anki Hint',
  props: {
    fieldName: 'Hint',
    label: 'Hint',
  },
};

/**
 * AnkiConditional - Renders {{#field}}...{{/field}} syntax
 */
export const AnkiConditional: React.FC<{
  fieldName?: string;
  children?: React.ReactNode;
}> = ({ fieldName = 'Field', children }) => {
  const { connectors } = useNode();

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className="anki-conditional"
      data-field={fieldName}
      title={`Conditional: {{#${fieldName}}}...{{/${fieldName}}}`}
    >
      <div className="anki-conditional-label">
        <code className="anki-syntax">{`{{#${fieldName}}}`}</code>
      </div>
      <div className="anki-conditional-content">{children || 'Content if field is present'}</div>
      <div className="anki-conditional-label">
        <code className="anki-syntax">{`{{/${fieldName}}}`}</code>
      </div>
    </div>
  );
};

AnkiConditional.craft = {
  displayName: 'Anki Conditional',
  props: {
    fieldName: 'Field',
  },
  rules: {
    canDrop: () => true,
  },
};

/**
 * AnkiFieldReference - Smart field picker component
 */
export const AnkiFieldReference: React.FC<{
  availableFields?: string[];
  onSelect?: (field: string) => void;
}> = ({ availableFields = [], onSelect }) => {
  const { connectors } = useNode();

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className="anki-field-reference"
    >
      <select
        onChange={(e) => onSelect?.(e.target.value)}
        defaultValue={availableFields[0] || ''}
        className="anki-field-select"
      >
        <option value="">Select a field...</option>
        {availableFields.map((field) => (
          <option key={field} value={field}>
            {field}
          </option>
        ))}
      </select>
    </div>
  );
};

AnkiFieldReference.craft = {
  displayName: 'Field Reference',
  props: {
    availableFields: [],
    onSelect: () => {},
  },
};

/**
 * AnkiSyntaxHighlight - Shows raw Anki syntax
 */
export const AnkiSyntaxHighlight: React.FC<{
  syntax?: string;
  description?: string;
}> = ({ syntax = '{{field}}', description = 'Anki Syntax' }) => {
  const { connectors } = useNode();

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className="anki-syntax-highlight"
    >
      <div className="anki-syntax-label">{description}</div>
      <code className="anki-syntax-code">{syntax}</code>
    </div>
  );
};

AnkiSyntaxHighlight.craft = {
  displayName: 'Anki Syntax',
  props: {
    syntax: '{{field}}',
    description: 'Anki Syntax',
  },
};

/**
 * AnkiBehaviorBlock - Represents behavior/scripting
 */
export const AnkiBehaviorBlock: React.FC<{
  type?: 'script' | 'style' | 'template';
  content?: string;
}> = ({ type = 'script', content = '' }) => {
  const { connectors } = useNode();

  const typeLabel = {
    script: '📜 Script',
    style: '🎨 Style',
    template: '📋 Template',
  }[type];

  return (
    <div
      ref={(ref) => connectors.connect(ref)}
      className={`anki-behavior-block anki-behavior-${type}`}
      data-behavior-type={type}
    >
      <div className="anki-behavior-header">{typeLabel}</div>
      <pre className="anki-behavior-content">{content || `// ${type} code here`}</pre>
    </div>
  );
};

AnkiBehaviorBlock.craft = {
  displayName: 'Anki Behavior',
  props: {
    type: 'script',
    content: '',
  },
};

/**
 * Register all Anki blocks
 */
export function registerAnkiBlocks(): void {
  blockRegistry.register({
    name: 'anki-field',
    label: 'Field',
    icon: '🏷️',
    category: 'anki',
    component: AnkiField,
    defaultProps: {
      fieldName: 'Field',
      fallback: '',
    },
  });

  blockRegistry.register({
    name: 'anki-cloze',
    label: 'Cloze Deletion',
    icon: '❓',
    category: 'anki',
    component: AnkiCloze,
    defaultProps: {
      fieldName: 'Text',
      clozeNumber: 1,
    },
  });

  blockRegistry.register({
    name: 'anki-hint',
    label: 'Hint',
    icon: '💡',
    category: 'anki',
    component: AnkiHint,
    defaultProps: {
      fieldName: 'Hint',
      label: 'Hint',
    },
  });

  blockRegistry.register({
    name: 'anki-conditional',
    label: 'Conditional',
    icon: '🔀',
    category: 'anki',
    component: AnkiConditional,
    defaultProps: {
      fieldName: 'Field',
    },
  });

  blockRegistry.register({
    name: 'anki-field-reference',
    label: 'Field Reference',
    icon: '🔗',
    category: 'anki',
    component: AnkiFieldReference,
    defaultProps: {
      availableFields: [],
      onSelect: () => {},
    },
  });

  blockRegistry.register({
    name: 'anki-syntax-highlight',
    label: 'Syntax Highlight',
    icon: '✨',
    category: 'anki',
    component: AnkiSyntaxHighlight,
    defaultProps: {
      syntax: '{{field}}',
      description: 'Anki Syntax',
    },
  });

  blockRegistry.register({
    name: 'anki-behavior',
    label: 'Behavior Block',
    icon: '⚙️',
    category: 'anki',
    component: AnkiBehaviorBlock,
    defaultProps: {
      type: 'script',
      content: '',
    },
  });
}

export default {
  AnkiField,
  AnkiCloze,
  AnkiHint,
  AnkiConditional,
  AnkiFieldReference,
  AnkiSyntaxHighlight,
  AnkiBehaviorBlock,
  registerAnkiBlocks,
};
