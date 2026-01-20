/**
 * Data Display & Media Blocks
 * Text, list, table, image, and media components for Craft.js with full integration
 */

import React, { ImgHTMLAttributes } from 'react';
import { useNode } from '@craftjs/core';
import { CraftBlock } from '@/services/blockRegistry';

// ============= TEXT COMPONENTS =============

/**
 * Heading - H2 heading element
 */
export const Heading: React.FC<{
  children?: React.ReactNode;
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  text?: string;
}> = ({ children, level = 2, text = 'Heading Text' }) => {
  const {
    connectors: { connect, drag },
  } = useNode();
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;

  return React.createElement(
    Tag,
    {
      ref: (ref) => ref && connect(drag(ref)),
      style: {
        fontSize: level === 1 ? '32px' : level === 2 ? '24px' : level === 3 ? '20px' : '16px',
        fontWeight: '600',
        margin: '0 0 16px 0',
        lineHeight: '1.2',
      },
    },
    children || text
  );
};

Heading.craft = {
  displayName: 'Heading',
  rules: { canMoveIn: () => false },
};

/**
 * Paragraph - Text paragraph
 */
export const Paragraph: React.FC<{ children?: React.ReactNode; text?: string }> = ({
  children,
  text = 'This is a paragraph of text.',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <p
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        lineHeight: '1.6',
        margin: '0 0 16px 0',
        fontSize: '16px',
      }}
    >
      {children || text}
    </p>
  );
};

Paragraph.craft = {
  displayName: 'Paragraph',
  rules: { canMoveIn: () => false },
};

/**
 * Caption - Small caption text
 */
export const Caption: React.FC<{ children?: React.ReactNode; text?: string }> = ({
  children,
  text = 'Caption text',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <span
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        fontSize: '12px',
        color: '#666',
      }}
    >
      {children || text}
    </span>
  );
};

Caption.craft = {
  displayName: 'Caption',
  rules: { canMoveIn: () => false },
};

/**
 * Label - Styled label text
 */
export const Label: React.FC<{ children?: React.ReactNode; text?: string }> = ({
  children,
  text = 'Label',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <span
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        fontSize: '14px',
        fontWeight: '500',
      }}
    >
      {children || text}
    </span>
  );
};

Label.craft = {
  displayName: 'Label',
  rules: { canMoveIn: () => false },
};

/**
 * CodeBlock - Multi-line code block
 */
export const CodeBlock: React.FC<{ code?: string; language?: string }> = ({
  code = 'const greeting = "Hello, World!";\nconsole.log(greeting);',
  language = 'javascript',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <pre
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '16px',
        background: '#1e1e1e',
        color: '#d4d4d4',
        borderRadius: '8px',
        overflow: 'auto',
        fontFamily: 'monospace',
        fontSize: '14px',
        margin: '0 0 16px 0',
      }}
    >
      <code>{code}</code>
    </pre>
  );
};

CodeBlock.craft = {
  displayName: 'CodeBlock',
  rules: { canMoveIn: () => false },
};

/**
 * InlineCode - Single-line inline code
 */
export const InlineCode: React.FC<{ code?: string }> = ({ code = 'inline code' }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <code
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '2px 6px',
        background: '#f5f5f5',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '14px',
      }}
    >
      {code}
    </code>
  );
};

InlineCode.craft = {
  displayName: 'InlineCode',
  rules: { canMoveIn: () => false },
};

/**
 * Blockquote - Quoted text block
 */
export const Blockquote: React.FC<{ quote?: string; author?: string }> = ({
  quote = 'This is a quote.',
  author = '',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <blockquote
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        margin: '16px 0',
        padding: '12px 20px',
        borderLeft: '4px solid #1976d2',
        background: '#f5f5f5',
        fontStyle: 'italic',
      }}
    >
      <p style={{ margin: '0 0 8px 0' }}>"{quote}"</p>
      {author && <p style={{ margin: '0', fontSize: '12px' }}>— {author}</p>}
    </blockquote>
  );
};

Blockquote.craft = {
  displayName: 'Blockquote',
  rules: { canMoveIn: () => false },
};

// ============= LIST COMPONENTS =============

/**
 * UnorderedList - Bullet list
 */
export const UnorderedList: React.FC<{ items?: string[] }> = ({
  items = ['List item 1', 'List item 2', 'List item 3'],
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <ul
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        paddingLeft: '24px',
        margin: '0 0 16px 0',
      }}
    >
      {items.map((item, idx) => (
        <li key={idx} style={{ marginBottom: '8px' }}>
          {item}
        </li>
      ))}
    </ul>
  );
};

UnorderedList.craft = {
  displayName: 'UnorderedList',
  rules: { canMoveIn: () => false },
};

/**
 * OrderedList - Numbered list
 */
export const OrderedList: React.FC<{ items?: string[] }> = ({
  items = ['First item', 'Second item', 'Third item'],
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <ol
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        paddingLeft: '24px',
        margin: '0 0 16px 0',
      }}
    >
      {items.map((item, idx) => (
        <li key={idx} style={{ marginBottom: '8px' }}>
          {item}
        </li>
      ))}
    </ol>
  );
};

OrderedList.craft = {
  displayName: 'OrderedList',
  rules: { canMoveIn: () => false },
};

/**
 * DefinitionList - Term-definition list
 */
export const DefinitionList: React.FC<{
  items?: { term: string; definition: string }[];
}> = ({
  items = [
    { term: 'Term 1', definition: 'Definition 1' },
    { term: 'Term 2', definition: 'Definition 2' },
  ],
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <dl
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        margin: '0 0 16px 0',
      }}
    >
      {items.map((item, idx) => (
        <div key={idx}>
          <dt
            style={{
              fontWeight: '600',
              marginBottom: '4px',
            }}
          >
            {item.term}
          </dt>
          <dd
            style={{
              marginLeft: '0',
              marginBottom: '12px',
              color: '#666',
            }}
          >
            {item.definition}
          </dd>
        </div>
      ))}
    </dl>
  );
};

DefinitionList.craft = {
  displayName: 'DefinitionList',
  rules: { canMoveIn: () => false },
};

// ============= MEDIA COMPONENTS =============

/**
 * Image - Image element
 */
export const Image: React.FC<ImgHTMLAttributes<HTMLImageElement> & { src?: string }> = ({
  src = 'https://via.placeholder.com/400x300',
  alt = 'Image',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <img
      ref={(ref) => ref && connect(drag(ref))}
      src={src}
      alt={alt}
      style={{
        maxWidth: '100%',
        height: 'auto',
        borderRadius: '8px',
        marginBottom: '16px',
      }}
      {...props}
    />
  );
};

Image.craft = {
  displayName: 'Image',
  rules: { canMoveIn: () => false },
};

/**
 * Video - Embedded video
 */
export const Video: React.FC<{
  src?: string;
  title?: string;
  width?: number;
  height?: number;
}> = ({ src = '', title = 'Video', width = 560, height = 315 }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '16px' }}>
      {src ? (
        <iframe
          width={width}
          height={height}
          src={src}
          title={title}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          style={{
            borderRadius: '8px',
            maxWidth: '100%',
          }}
        />
      ) : (
        <div
          style={{
            width: '100%',
            maxWidth: `${width}px`,
            height: '315px',
            background: '#e0e0e0',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999',
          }}
        >
          Video Placeholder
        </div>
      )}
    </div>
  );
};

Video.craft = {
  displayName: 'Video',
  rules: { canMoveIn: () => false },
};

/**
 * HorizontalRule / Divider - Visual separator
 */
export const HorizontalRule: React.FC = () => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <hr
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        border: 'none',
        borderTop: '2px solid #e0e0e0',
        margin: '24px 0',
      }}
    />
  );
};

HorizontalRule.craft = {
  displayName: 'HorizontalRule',
  rules: { canMoveIn: () => false },
};

/**
 * Badge - Small label badge
 */
export const Badge: React.FC<{ text?: string; color?: string }> = ({
  text = 'Badge',
  color = '#1976d2',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <span
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'inline-block',
        padding: '4px 12px',
        background: color,
        color: '#ffffff',
        borderRadius: '16px',
        fontSize: '12px',
        fontWeight: '600',
        marginRight: '8px',
      }}
    >
      {text}
    </span>
  );
};

Badge.craft = {
  displayName: 'Badge',
  rules: { canMoveIn: () => false },
};

/**
 * Chip - Compact informational chip
 */
export const Chip: React.FC<{ text?: string; variant?: 'filled' | 'outlined' }> = ({
  text = 'Chip',
  variant = 'filled',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <span
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'inline-block',
        padding: '6px 12px',
        background: variant === 'filled' ? '#e0e0e0' : 'transparent',
        border: variant === 'outlined' ? '1px solid #d0d0d0' : 'none',
        borderRadius: '20px',
        fontSize: '13px',
        marginRight: '8px',
        marginBottom: '8px',
      }}
    >
      {text}
    </span>
  );
};

Chip.craft = {
  displayName: 'Chip',
  rules: { canMoveIn: () => false },
};

/**
 * Alert - Alert/notification box
 */
export const Alert: React.FC<{
  message?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
}> = ({ message = 'Alert message', type = 'info' }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  const colors = {
    info: { bg: '#e3f2fd', border: '#2196f3', text: '#1976d2' },
    success: { bg: '#e8f5e9', border: '#4caf50', text: '#388e3c' },
    warning: { bg: '#fff3e0', border: '#ff9800', text: '#f57c00' },
    error: { bg: '#ffebee', border: '#f44336', text: '#d32f2f' },
  };

  const color = colors[type];

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 16px',
        background: color.bg,
        border: `1px solid ${color.border}`,
        borderRadius: '6px',
        color: color.text,
        marginBottom: '16px',
        fontSize: '14px',
      }}
    >
      {message}
    </div>
  );
};

Alert.craft = {
  displayName: 'Alert',
  rules: { canMoveIn: () => false },
};

// ============= EXPORT BLOCK DEFINITIONS =============

/**
 * Get all data display blocks as CraftBlock definitions
 */
export function getBlocks(): CraftBlock[] {
  return [
    // Text
    {
      name: 'data-heading',
      label: 'Heading',
      category: 'Data Display',
      description: 'Heading element (H1-H6)',
      Component: Heading,
      defaultProps: { level: 2, text: 'Heading Text' },
      craft: Heading.craft,
    },
    {
      name: 'data-paragraph',
      label: 'Paragraph',
      category: 'Data Display',
      description: 'Text paragraph',
      Component: Paragraph,
      defaultProps: { text: 'This is a paragraph of text.' },
      craft: Paragraph.craft,
    },
    {
      name: 'data-caption',
      label: 'Caption',
      category: 'Data Display',
      description: 'Small caption text',
      Component: Caption,
      defaultProps: { text: 'Caption text' },
      craft: Caption.craft,
    },
    {
      name: 'data-label',
      label: 'Label',
      category: 'Data Display',
      description: 'Styled label text',
      Component: Label,
      defaultProps: { text: 'Label' },
      craft: Label.craft,
    },
    {
      name: 'data-code-block',
      label: 'Code Block',
      category: 'Data Display',
      description: 'Multi-line code block with syntax highlighting',
      Component: CodeBlock,
      defaultProps: { language: 'javascript', code: 'const x = 1;' },
      craft: CodeBlock.craft,
    },
    {
      name: 'data-inline-code',
      label: 'Inline Code',
      category: 'Data Display',
      description: 'Single-line inline code',
      Component: InlineCode,
      defaultProps: { code: 'code' },
      craft: InlineCode.craft,
    },
    {
      name: 'data-blockquote',
      label: 'Blockquote',
      category: 'Data Display',
      description: 'Quoted text block',
      Component: Blockquote,
      defaultProps: { quote: 'This is a quote.', author: '' },
      craft: Blockquote.craft,
    },

    // Lists
    {
      name: 'data-ul',
      label: 'Unordered List',
      category: 'Data Display',
      description: 'Bullet point list',
      Component: UnorderedList,
      defaultProps: { items: ['Item 1', 'Item 2', 'Item 3'] },
      craft: UnorderedList.craft,
    },
    {
      name: 'data-ol',
      label: 'Ordered List',
      category: 'Data Display',
      description: 'Numbered list',
      Component: OrderedList,
      defaultProps: { items: ['First', 'Second', 'Third'] },
      craft: OrderedList.craft,
    },
    {
      name: 'data-dl',
      label: 'Definition List',
      category: 'Data Display',
      description: 'Term-definition list',
      Component: DefinitionList,
      defaultProps: {
        items: [
          { term: 'Term 1', definition: 'Definition 1' },
          { term: 'Term 2', definition: 'Definition 2' },
        ],
      },
      craft: DefinitionList.craft,
    },

    // Media
    {
      name: 'data-image',
      label: 'Image',
      category: 'Data Display',
      description: 'Image element with responsive sizing',
      Component: Image,
      defaultProps: { src: 'https://via.placeholder.com/400x300', alt: 'Image' },
      craft: Image.craft,
    },
    {
      name: 'data-video',
      label: 'Video',
      category: 'Data Display',
      description: 'Embedded video player',
      Component: Video,
      defaultProps: { title: 'Video', width: 560, height: 315 },
      craft: Video.craft,
    },
    {
      name: 'data-divider',
      label: 'Divider',
      category: 'Data Display',
      description: 'Horizontal separator line',
      Component: HorizontalRule,
      craft: HorizontalRule.craft,
    },

    // Feedback & Status
    {
      name: 'data-badge',
      label: 'Badge',
      category: 'Data Display',
      description: 'Small label badge for status/tags',
      Component: Badge,
      defaultProps: { text: 'Badge', color: '#1976d2' },
      craft: Badge.craft,
    },
    {
      name: 'data-chip',
      label: 'Chip',
      category: 'Data Display',
      description: 'Compact informational chip',
      Component: Chip,
      defaultProps: { text: 'Chip', variant: 'filled' },
      craft: Chip.craft,
    },
    {
      name: 'data-alert',
      label: 'Alert',
      category: 'Data Display',
      description: 'Alert/notification box (info, success, warning, error)',
      Component: Alert,
      defaultProps: { message: 'Alert message', type: 'info' },
      craft: Alert.craft,
    },
  ];
}
