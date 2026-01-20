/**
 * Button & Action Blocks
 * Button components for Craft.js with full integration
 */

import React, { ButtonHTMLAttributes } from 'react';
import { useNode } from '@craftjs/core';
import { CraftBlock } from '@/services/blockRegistry';

// ============= BUTTON COMPONENTS =============

/**
 * PrimaryButton - Main call-to-action button
 */
export const PrimaryButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Primary Action',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 24px',
        background: '#1976d2',
        color: '#ffffff',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'background 0.2s',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

PrimaryButton.craft = {
  displayName: 'PrimaryButton',
  rules: { canMoveIn: () => false },
};

/**
 * SecondaryButton - Secondary action button
 */
export const SecondaryButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Secondary Action',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 24px',
        background: '#ffffff',
        color: '#1976d2',
        border: '1px solid #1976d2',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'background 0.2s',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

SecondaryButton.craft = {
  displayName: 'SecondaryButton',
  rules: { canMoveIn: () => false },
};

/**
 * DestructiveButton - Delete/destructive action button
 */
export const DestructiveButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Delete',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 24px',
        background: '#d32f2f',
        color: '#ffffff',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'background 0.2s',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

DestructiveButton.craft = {
  displayName: 'DestructiveButton',
  rules: { canMoveIn: () => false },
};

/**
 * SuccessButton - Success/confirm action button
 */
export const SuccessButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Confirm',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 24px',
        background: '#4caf50',
        color: '#ffffff',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'background 0.2s',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

SuccessButton.craft = {
  displayName: 'SuccessButton',
  rules: { canMoveIn: () => false },
};

/**
 * WarningButton - Warning/caution action button
 */
export const WarningButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Warning',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '12px 24px',
        background: '#ff9800',
        color: '#ffffff',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'background 0.2s',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

WarningButton.craft = {
  displayName: 'WarningButton',
  rules: { canMoveIn: () => false },
};

/**
 * LinkButton - Button styled as a link
 */
export const LinkButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Link Action',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '0',
        background: 'none',
        color: '#1976d2',
        border: 'none',
        fontSize: '16px',
        textDecoration: 'underline',
        cursor: 'pointer',
        fontFamily: 'inherit',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

LinkButton.craft = {
  displayName: 'LinkButton',
  rules: { canMoveIn: () => false },
};

/**
 * TextButton - Minimal text-only button
 */
export const TextButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Text Button',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '8px 12px',
        background: 'transparent',
        color: '#1976d2',
        border: 'none',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'color 0.2s',
        fontFamily: 'inherit',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

TextButton.craft = {
  displayName: 'TextButton',
  rules: { canMoveIn: () => false },
};

/**
 * OutlineButton - Button with outline style
 */
export const OutlineButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }> = ({
  label = 'Outline Button',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        padding: '10px 20px',
        background: 'transparent',
        color: '#424242',
        border: '2px solid #424242',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'all 0.2s',
        fontFamily: 'inherit',
      }}
      {...props}
    >
      {label}
    </button>
  );
};

OutlineButton.craft = {
  displayName: 'OutlineButton',
  rules: { canMoveIn: () => false },
};

/**
 * IconButton - Compact circular button for icons
 */
export const IconButton: React.FC<ButtonHTMLAttributes<HTMLButtonElement> & { icon?: string }> = ({
  icon = '⭐',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        width: '40px',
        height: '40px',
        padding: '0',
        background: '#f5f5f5',
        color: '#424242',
        border: 'none',
        borderRadius: '50%',
        fontSize: '20px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background 0.2s',
        fontFamily: 'inherit',
      }}
      {...props}
    >
      {icon}
    </button>
  );
};

IconButton.craft = {
  displayName: 'IconButton',
  rules: { canMoveIn: () => false },
};

/**
 * FloatingActionButton (FAB) - Circular action button
 */
export const FloatingActionButton: React.FC<
  ButtonHTMLAttributes<HTMLButtonElement> & { icon?: string }
> = ({ icon = '+', ...props }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <button
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        width: '56px',
        height: '56px',
        padding: '0',
        background: '#1976d2',
        color: '#ffffff',
        border: 'none',
        borderRadius: '50%',
        fontSize: '28px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(25, 118, 210, 0.4)',
        transition: 'all 0.2s',
        fontFamily: 'inherit',
      }}
      {...props}
    >
      {icon}
    </button>
  );
};

FloatingActionButton.craft = {
  displayName: 'FloatingActionButton',
  rules: { canMoveIn: () => false },
};

/**
 * ButtonGroup - Container for multiple buttons
 */
export const ButtonGroup: React.FC<{
  children?: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
}> = ({ children, orientation = 'horizontal' }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        display: 'flex',
        flexDirection: orientation === 'horizontal' ? 'row' : 'column',
        gap: '12px',
        flexWrap: 'wrap',
        alignItems: 'center',
      }}
    >
      {children}
    </div>
  );
};

ButtonGroup.craft = {
  displayName: 'ButtonGroup',
  isCanvas: true,
};

// ============= EXPORT BLOCK DEFINITIONS =============

/**
 * Get all button blocks as CraftBlock definitions
 */
export function getBlocks(): CraftBlock[] {
  return [
    {
      name: 'button-primary',
      label: 'Primary Button',
      category: 'Buttons & Actions',
      description: 'Main call-to-action button',
      Component: PrimaryButton,
      defaultProps: { label: 'Primary Action' },
      craft: PrimaryButton.craft,
    },
    {
      name: 'button-secondary',
      label: 'Secondary Button',
      category: 'Buttons & Actions',
      description: 'Secondary action button',
      Component: SecondaryButton,
      defaultProps: { label: 'Secondary Action' },
      craft: SecondaryButton.craft,
    },
    {
      name: 'button-destructive',
      label: 'Destructive Button',
      category: 'Buttons & Actions',
      description: 'Delete or destructive action button',
      Component: DestructiveButton,
      defaultProps: { label: 'Delete' },
      craft: DestructiveButton.craft,
    },
    {
      name: 'button-success',
      label: 'Success Button',
      category: 'Buttons & Actions',
      description: 'Success or confirm action button',
      Component: SuccessButton,
      defaultProps: { label: 'Confirm' },
      craft: SuccessButton.craft,
    },
    {
      name: 'button-warning',
      label: 'Warning Button',
      category: 'Buttons & Actions',
      description: 'Warning or caution action button',
      Component: WarningButton,
      defaultProps: { label: 'Warning' },
      craft: WarningButton.craft,
    },
    {
      name: 'button-link',
      label: 'Link Button',
      category: 'Buttons & Actions',
      description: 'Button styled as a link',
      Component: LinkButton,
      defaultProps: { label: 'Link Action' },
      craft: LinkButton.craft,
    },
    {
      name: 'button-text',
      label: 'Text Button',
      category: 'Buttons & Actions',
      description: 'Minimal text-only button',
      Component: TextButton,
      defaultProps: { label: 'Text Button' },
      craft: TextButton.craft,
    },
    {
      name: 'button-outline',
      label: 'Outline Button',
      category: 'Buttons & Actions',
      description: 'Button with outline style',
      Component: OutlineButton,
      defaultProps: { label: 'Outline Button' },
      craft: OutlineButton.craft,
    },
    {
      name: 'button-icon',
      label: 'Icon Button',
      category: 'Buttons & Actions',
      description: 'Compact circular button for icons',
      Component: IconButton,
      defaultProps: { icon: '⭐' },
      craft: IconButton.craft,
    },
    {
      name: 'button-fab',
      label: 'Floating Action Button',
      category: 'Buttons & Actions',
      description: 'Circular FAB for primary actions',
      Component: FloatingActionButton,
      defaultProps: { icon: '+' },
      craft: FloatingActionButton.craft,
    },
    {
      name: 'button-group',
      label: 'Button Group',
      category: 'Buttons & Actions',
      description: 'Container for multiple buttons',
      Component: ButtonGroup,
      defaultProps: { orientation: 'horizontal' },
      craft: ButtonGroup.craft,
    },
  ];
}
