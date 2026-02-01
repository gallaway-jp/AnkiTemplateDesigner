/**
 * Anki-Specific Block Definitions for GrapeJS
 * 
 * Provides 6 blocks for Anki template syntax:
 * - anki-field: Field placeholder {{FieldName}}
 * - cloze: Cloze deletion {{c1::answer}}
 * - hint-field: Hint field {{hint:FieldName}}
 * - type-answer: Type answer {{type:FieldName}}
 * - conditional: Conditional content {{#Front}}...{{/Front}}
 * - tags-display: Tags {{Tags}}
 * 
 * All blocks are registered with "Anki Fields" category for UI organization.
 */

export function registerAnkiBlocks(editor) {
  const bm = editor.BlockManager;

  /**
   * ANKI FIELD BLOCK
   * Represents {{FieldName}} syntax
   */
  bm.add('anki-field', {
    label: 'Field',
    category: 'Anki Fields',
    attributes: { class: 'anki-field-block' },
    content: {
      type: 'text',
      content: '{{FieldName}}',
      style: {
        padding: '8px 12px',
        backgroundColor: '#e3f2fd',
        border: '2px solid #2196f3',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '14px',
        color: '#1565c0',
        fontWeight: '500',
        display: 'inline-block',
      },
    },
  });

  /**
   * CLOZE DELETION BLOCK
   * Represents {{c1::answer}} syntax
   */
  bm.add('cloze', {
    label: 'Cloze',
    category: 'Anki Fields',
    attributes: { class: 'cloze-block' },
    content: {
      type: 'text',
      content: '{{c1::answer}}',
      style: {
        padding: '8px 12px',
        backgroundColor: '#ffe0b2',
        border: '2px solid #ff9800',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '14px',
        color: '#e65100',
        fontWeight: '500',
        display: 'inline-block',
      },
    },
  });

  /**
   * HINT FIELD BLOCK
   * Represents {{hint:FieldName}} syntax
   */
  bm.add('hint-field', {
    label: 'Hint',
    category: 'Anki Fields',
    attributes: { class: 'hint-field-block' },
    content: {
      type: 'text',
      content: '{{hint:FieldName}}',
      style: {
        padding: '8px 12px',
        backgroundColor: 'transparent',
        border: 'none',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '14px',
        color: '#1976d2',
        fontWeight: '500',
        textDecoration: 'underline',
        cursor: 'pointer',
        display: 'inline-block',
      },
    },
  });

  /**
   * TYPE ANSWER BLOCK
   * Represents {{type:FieldName}} syntax
   */
  bm.add('type-answer', {
    label: 'Type Answer',
    category: 'Anki Fields',
    attributes: { class: 'type-answer-block' },
    content: {
      type: 'text',
      content: '{{type:FieldName}}',
      style: {
        padding: '8px 12px',
        backgroundColor: '#f5f5f5',
        border: '2px solid #9e9e9e',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '14px',
        color: '#424242',
        fontWeight: '500',
        display: 'inline-block',
      },
    },
  });

  /**
   * CONDITIONAL BLOCK
   * Represents {{#FrontSide}}...{{/FrontSide}} syntax
   * Canvas-enabled to accept children content
   */
  bm.add('conditional', {
    label: 'Conditional',
    category: 'Anki Fields',
    attributes: { class: 'conditional-block' },
    content: {
      type: 'div',
      style: {
        padding: '12px',
        backgroundColor: '#f3e5f5',
        border: '2px dashed #9c27b0',
        borderRadius: '4px',
      },
      content: [
        {
          type: 'text',
          content: '{{#FrontSide}}',
          style: {
            fontFamily: 'monospace',
            fontSize: '12px',
            color: '#6a1b9a',
            fontWeight: '600',
          },
        },
        {
          type: 'div',
          style: {
            padding: '8px 0',
            minHeight: '40px',
            borderLeft: '2px solid #9c27b0',
            paddingLeft: '8px',
            marginLeft: '8px',
          },
          content: 'Content here...',
        },
        {
          type: 'text',
          content: '{{/FrontSide}}',
          style: {
            fontFamily: 'monospace',
            fontSize: '12px',
            color: '#6a1b9a',
            fontWeight: '600',
          },
        },
      ],
    },
  });

  /**
   * TAGS DISPLAY BLOCK
   * Represents {{Tags}} syntax
   */
  bm.add('tags-display', {
    label: 'Tags',
    category: 'Anki Fields',
    attributes: { class: 'tags-display-block' },
    content: {
      type: 'text',
      content: '{{Tags}}',
      style: {
        padding: '4px 8px',
        backgroundColor: 'transparent',
        border: 'none',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '12px',
        color: '#bdbdbd',
        fontStyle: 'italic',
        display: 'inline-block',
      },
    },
  });
}

/**
 * Export function for module usage
 * Usage: import { registerAnkiBlocks } from './anki-blocks.js'
 */
export default registerAnkiBlocks;
