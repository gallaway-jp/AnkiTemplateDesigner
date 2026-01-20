/**
 * Layout & Structure Blocks
 * Container and layout components for Craft.js with full integration
 */

import React, { ReactNode } from 'react';
import { useNode } from '@craftjs/core';
import { CraftBlock } from '@/services/blockRegistry';

// ============= CONTAINER COMPONENTS =============

/**
 * Frame - Top-level container for card/device mockups
 */
export const Frame: React.FC<{ children?: ReactNode; title?: string }> = ({ children, title = 'Frame' }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        width: '375px',
        height: '667px',
        margin: '0 auto',
        background: '#ffffff',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
        overflow: 'hidden',
        borderRadius: '12px',
        position: 'relative',
      }}
    >
      <div style={{ width: '100%', height: '100%', overflowY: 'auto' }}>
        {children || <div style={{ padding: '20px', color: '#999' }}>{title} content</div>}
      </div>
    </div>
  );
};

Frame.craft = {
  displayName: 'Frame',
  isCanvas: true,
  rules: { canMoveIn: () => true, canMoveOut: () => false },
};

/**
 * Section - Semantic section container
 */
export const Section: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <section
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '20px',
        marginBottom: '10px',
        borderBottom: '1px solid #e0e0e0',
      }}
    >
      {children || <div style={{ color: '#999' }}>Section content</div>}
    </section>
  );
};

Section.craft = {
  displayName: 'Section',
  isCanvas: true,
};

/**
 * Panel - Simple bordered container
 */
export const Panel: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '16px',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        background: '#ffffff',
      }}
    >
      {children || <div style={{ color: '#999' }}>Panel content</div>}
    </div>
  );
};

Panel.craft = {
  displayName: 'Panel',
  isCanvas: true,
};

/**
 * Card - Material design card with shadow
 */
export const Card: React.FC<{ children?: ReactNode; title?: string }> = ({
  children,
  title = 'Card Title',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '16px',
        borderRadius: '12px',
        background: '#ffffff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '16px',
      }}
    >
      <div style={{ fontWeight: '600', marginBottom: '8px', fontSize: '16px' }}>{title}</div>
      <div>{children || <div style={{ color: '#666' }}>Card content goes here</div>}</div>
    </div>
  );
};

Card.craft = {
  displayName: 'Card',
  isCanvas: true,
  props: { title: 'Card Title' },
};

/**
 * Surface - Simple surface container
 */
export const Surface: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px',
        background: '#f5f5f5',
        borderRadius: '4px',
      }}
    >
      {children}
    </div>
  );
};

Surface.craft = {
  displayName: 'Surface',
  isCanvas: true,
};

/**
 * Modal Container - Fixed positioned modal
 */
export const ModalContainer: React.FC<{ children?: ReactNode; title?: string }> = ({
  children,
  title = 'Modal Title',
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        minWidth: '300px',
        maxWidth: '90%',
        padding: '24px',
        background: '#ffffff',
        borderRadius: '12px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
        zIndex: 1000,
      }}
    >
      <h3 style={{ margin: '0 0 16px 0' }}>{title}</h3>
      {children || <p style={{ color: '#999' }}>Modal content</p>}
    </div>
  );
};

ModalContainer.craft = {
  displayName: 'Modal',
  isCanvas: true,
  rules: { canMoveOut: () => false },
};

/**
 * Drawer - Sidebar drawer container
 */
export const Drawer: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <aside
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        width: '280px',
        height: '100%',
        padding: '16px',
        background: '#ffffff',
        borderRight: '1px solid #e0e0e0',
        overflowY: 'auto',
      }}
    >
      <h4 style={{ margin: '0 0 16px 0' }}>Menu</h4>
      {children}
    </aside>
  );
};

Drawer.craft = {
  displayName: 'Drawer',
  isCanvas: true,
};

/**
 * SplitView - Two-pane split layout
 */
export const SplitView: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'flex',
        gap: '1px',
        background: '#e0e0e0',
        height: '100%',
      }}
    >
      <div style={{ flex: '1', padding: '16px', background: '#fff' }}>
        {children || <div style={{ color: '#999' }}>Left pane</div>}
      </div>
      <div style={{ flex: '1', padding: '16px', background: '#fff' }}>
        <div style={{ color: '#999' }}>Right pane</div>
      </div>
    </div>
  );
};

SplitView.craft = {
  displayName: 'SplitView',
  isCanvas: true,
};

// ============= GRID LAYOUTS =============

/**
 * Grid - 3-column CSS grid layout
 */
export const Grid: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '16px',
      }}
    >
      {children || (
        <>
          <div style={{ padding: '16px', background: '#f0f0f0', borderRadius: '4px', color: '#999' }}>
            Item 1
          </div>
          <div style={{ padding: '16px', background: '#f0f0f0', borderRadius: '4px', color: '#999' }}>
            Item 2
          </div>
          <div style={{ padding: '16px', background: '#f0f0f0', borderRadius: '4px', color: '#999' }}>
            Item 3
          </div>
        </>
      )}
    </div>
  );
};

Grid.craft = {
  displayName: 'Grid',
  isCanvas: true,
};

/**
 * Row2Col - 2-column layout
 */
export const Row2Col: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
      }}
    >
      {children || (
        <>
          <div style={{ padding: '16px', background: '#f0f0f0' }}>
            <div style={{ color: '#999' }}>Column 1</div>
          </div>
          <div style={{ padding: '16px', background: '#f0f0f0' }}>
            <div style={{ color: '#999' }}>Column 2</div>
          </div>
        </>
      )}
    </div>
  );
};

Row2Col.craft = {
  displayName: 'Row2Col',
  isCanvas: true,
};

/**
 * Row3Col - 3-column layout
 */
export const Row3Col: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '16px',
      }}
    >
      {children || (
        <>
          <div style={{ padding: '16px', background: '#f0f0f0' }}>
            <div style={{ color: '#999' }}>Col 1</div>
          </div>
          <div style={{ padding: '16px', background: '#f0f0f0' }}>
            <div style={{ color: '#999' }}>Col 2</div>
          </div>
          <div style={{ padding: '16px', background: '#f0f0f0' }}>
            <div style={{ color: '#999' }}>Col 3</div>
          </div>
        </>
      )}
    </div>
  );
};

Row3Col.craft = {
  displayName: 'Row3Col',
  isCanvas: true,
};

// ============= FLEXBOX LAYOUTS =============

/**
 * HStack - Horizontal stack (flexbox row)
 */
export const HStack: React.FC<{ children?: ReactNode; gap?: number }> = ({ children, gap = 8 }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'flex',
        flexDirection: 'row',
        gap: `${gap}px`,
        alignItems: 'center',
      }}
    >
      {children}
    </div>
  );
};

HStack.craft = {
  displayName: 'HStack',
  isCanvas: true,
  props: { gap: 8 },
};

/**
 * VStack - Vertical stack (flexbox column)
 */
export const VStack: React.FC<{ children?: ReactNode; gap?: number }> = ({ children, gap = 8 }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: `${gap}px`,
      }}
    >
      {children}
    </div>
  );
};

VStack.craft = {
  displayName: 'VStack',
  isCanvas: true,
  props: { gap: 8 },
};

/**
 * Spacer - Flexible spacing element
 */
export const Spacer: React.FC<{ size?: number }> = ({ size = 16 }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        height: `${size}px`,
        width: '100%',
      }}
    />
  );
};

Spacer.craft = {
  displayName: 'Spacer',
  props: { size: 16 },
  rules: { canMoveIn: () => false },
};

/**
 * Divider - Horizontal divider
 */
export const Divider: React.FC = () => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <hr
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        border: 'none',
        borderTop: '1px solid #e0e0e0',
        margin: '16px 0',
      }}
    />
  );
};

Divider.craft = {
  displayName: 'Divider',
  rules: { canMoveIn: () => false },
};

/**
 * Container - Generic flexible container
 */
export const Container: React.FC<{ children?: ReactNode }> = ({ children }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '16px',
        maxWidth: '1200px',
        margin: '0 auto',
      }}
    >
      {children}
    </div>
  );
};

Container.craft = {
  displayName: 'Container',
  isCanvas: true,
};

// ============= EXPORT BLOCK DEFINITIONS =============

/**
 * Get all layout blocks as CraftBlock definitions
 */
export function getBlocks(): CraftBlock[] {
  return [
    {
      name: 'frame',
      label: 'Frame',
      category: 'Layout',
      description: 'Device mockup frame container',
      Component: Frame,
      craft: Frame.craft,
    },
    {
      name: 'section',
      label: 'Section',
      category: 'Layout',
      description: 'Semantic section container',
      Component: Section,
      craft: Section.craft,
    },
    {
      name: 'panel',
      label: 'Panel',
      category: 'Layout',
      description: 'Simple bordered panel',
      Component: Panel,
      craft: Panel.craft,
    },
    {
      name: 'card',
      label: 'Card',
      category: 'Layout',
      description: 'Material design card',
      Component: Card,
      craft: Card.craft,
    },
    {
      name: 'surface',
      label: 'Surface',
      category: 'Layout',
      description: 'Simple surface container',
      Component: Surface,
      craft: Surface.craft,
    },
    {
      name: 'modal',
      label: 'Modal',
      category: 'Layout',
      description: 'Fixed positioned modal dialog',
      Component: ModalContainer,
      craft: ModalContainer.craft,
    },
    {
      name: 'drawer',
      label: 'Drawer',
      category: 'Layout',
      description: 'Sidebar drawer container',
      Component: Drawer,
      craft: Drawer.craft,
    },
    {
      name: 'splitview',
      label: 'SplitView',
      category: 'Layout',
      description: 'Two-pane split layout',
      Component: SplitView,
      craft: SplitView.craft,
    },
    {
      name: 'grid',
      label: 'Grid',
      category: 'Layout',
      description: '3-column grid layout',
      Component: Grid,
      craft: Grid.craft,
    },
    {
      name: 'row2col',
      label: 'Row2Col',
      category: 'Layout',
      description: '2-column grid layout',
      Component: Row2Col,
      craft: Row2Col.craft,
    },
    {
      name: 'row3col',
      label: 'Row3Col',
      category: 'Layout',
      description: '3-column grid layout',
      Component: Row3Col,
      craft: Row3Col.craft,
    },
    {
      name: 'hstack',
      label: 'HStack',
      category: 'Layout',
      description: 'Horizontal flex stack',
      Component: HStack,
      craft: HStack.craft,
    },
    {
      name: 'vstack',
      label: 'VStack',
      category: 'Layout',
      description: 'Vertical flex stack',
      Component: VStack,
      craft: VStack.craft,
    },
    {
      name: 'spacer',
      label: 'Spacer',
      category: 'Layout',
      description: 'Flexible spacing element',
      Component: Spacer,
      craft: Spacer.craft,
    },
    {
      name: 'divider',
      label: 'Divider',
      category: 'Layout',
      description: 'Horizontal divider line',
      Component: Divider,
      craft: Divider.craft,
    },
    {
      name: 'container',
      label: 'Container',
      category: 'Layout',
      description: 'Generic content container',
      Component: Container,
      craft: Container.craft,
    },
  ];
}
