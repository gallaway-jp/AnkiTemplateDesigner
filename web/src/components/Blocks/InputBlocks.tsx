/**
 * Input & Form Blocks
 * Form input components for Craft.js with full integration
 */

import React, { InputHTMLAttributes } from 'react';
import { useNode } from '@craftjs/core';
import { CraftBlock } from '@/services/blockRegistry';

// ============= INPUT COMPONENTS =============

/**
 * TextField - Single-line text input
 */
export const TextField: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Text Field',
  placeholder = 'Enter text...',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <input
        type="text"
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          transition: 'border-color 0.2s',
        }}
        {...props}
      />
    </div>
  );
};

TextField.craft = {
  displayName: 'TextField',
  rules: { canMoveIn: () => false },
};

/**
 * TextArea - Multi-line text input
 */
export const TextArea: React.FC<
  React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label?: string; rows?: number }
> = ({ label = 'Text Area', placeholder = 'Enter text...', rows = 4, ...props }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <textarea
        placeholder={placeholder}
        rows={rows}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          resize: 'vertical',
          transition: 'border-color 0.2s',
        }}
        {...props}
      />
    </div>
  );
};

TextArea.craft = {
  displayName: 'TextArea',
  rules: { canMoveIn: () => false },
};

/**
 * EmailField - Email input with validation
 */
export const EmailField: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Email',
  placeholder = 'Enter email...',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <input
        type="email"
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          transition: 'border-color 0.2s',
        }}
        {...props}
      />
    </div>
  );
};

EmailField.craft = {
  displayName: 'EmailField',
  rules: { canMoveIn: () => false },
};

/**
 * PasswordField - Password input with masking
 */
export const PasswordField: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Password',
  placeholder = 'Enter password...',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <input
        type="password"
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          transition: 'border-color 0.2s',
        }}
        {...props}
      />
    </div>
  );
};

PasswordField.craft = {
  displayName: 'PasswordField',
  rules: { canMoveIn: () => false },
};

/**
 * CheckBox - Single checkbox input
 */
export const CheckBox: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Checkbox',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}
    >
      <input
        type="checkbox"
        style={{
          width: '18px',
          height: '18px',
          cursor: 'pointer',
          accentColor: '#1976d2',
        }}
        {...props}
      />
      {label && (
        <label style={{ cursor: 'pointer', fontSize: '14px' }}>{label}</label>
      )}
    </div>
  );
};

CheckBox.craft = {
  displayName: 'CheckBox',
  rules: { canMoveIn: () => false },
};

/**
 * RadioButton - Single radio input
 */
export const RadioButton: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Radio Option',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}
    >
      <input
        type="radio"
        style={{
          width: '18px',
          height: '18px',
          cursor: 'pointer',
          accentColor: '#1976d2',
        }}
        {...props}
      />
      {label && (
        <label style={{ cursor: 'pointer', fontSize: '14px' }}>{label}</label>
      )}
    </div>
  );
};

RadioButton.craft = {
  displayName: 'RadioButton',
  rules: { canMoveIn: () => false },
};

/**
 * SelectInput - Dropdown select input
 */
export const SelectInput: React.FC<
  React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string; options?: string[] }
> = ({ label = 'Select', options = ['Option 1', 'Option 2', 'Option 3'], ...props }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <select
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          cursor: 'pointer',
          backgroundColor: '#ffffff',
        }}
        {...props}
      >
        {options.map((opt, idx) => (
          <option key={idx} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
};

SelectInput.craft = {
  displayName: 'SelectInput',
  rules: { canMoveIn: () => false },
};

/**
 * RangeSlider - Numeric range input
 */
export const RangeSlider: React.FC<
  InputHTMLAttributes<HTMLInputElement> & { label?: string; min?: number; max?: number; step?: number }
> = ({ label = 'Slider', min = 0, max = 100, step = 1, ...props }) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        style={{
          width: '100%',
          height: '6px',
          borderRadius: '3px',
          background: '#d0d0d0',
          outline: 'none',
          accentColor: '#1976d2',
          cursor: 'pointer',
        }}
        {...props}
      />
      <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
        Range: {min} - {max}
      </div>
    </div>
  );
};

RangeSlider.craft = {
  displayName: 'RangeSlider',
  rules: { canMoveIn: () => false },
};

/**
 * FileInput - File upload input
 */
export const FileInput: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Choose file',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div ref={(ref) => ref && connect(drag(ref))} style={{ marginBottom: '12px' }}>
      {label && (
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
          {label}
        </label>
      )}
      <input
        type="file"
        style={{
          width: '100%',
          padding: '8px',
          border: '1px solid #d0d0d0',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px',
        }}
        {...props}
      />
    </div>
  );
};

FileInput.craft = {
  displayName: 'FileInput',
  rules: { canMoveIn: () => false },
};

/**
 * ToggleSwitch - iOS-style toggle switch
 */
export const ToggleSwitch: React.FC<InputHTMLAttributes<HTMLInputElement> & { label?: string }> = ({
  label = 'Toggle',
  ...props
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <div
      ref={(ref) => ref && connect(drag(ref))}
      style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}
    >
      <input
        type="checkbox"
        style={{
          appearance: 'none',
          width: '44px',
          height: '24px',
          background: '#ccc',
          borderRadius: '12px',
          cursor: 'pointer',
          outline: 'none',
          transition: 'background 0.3s',
        }}
        {...props}
      />
      {label && (
        <label style={{ cursor: 'pointer', fontSize: '14px' }}>{label}</label>
      )}
    </div>
  );
};

ToggleSwitch.craft = {
  displayName: 'ToggleSwitch',
  rules: { canMoveIn: () => false },
};

/**
 * FormGroup - Container for form inputs
 */
export const FormGroup: React.FC<{ children?: React.ReactNode; title?: string }> = ({
  children,
  title,
}) => {
  const {
    connectors: { connect, drag },
  } = useNode();

  return (
    <fieldset
      ref={(ref) => ref && connect(drag(ref))}
      style={{
        border: '1px solid #e0e0e0',
        borderRadius: '6px',
        padding: '16px',
        marginBottom: '16px',
      }}
    >
      {title && (
        <legend style={{ padding: '0 8px', fontSize: '16px', fontWeight: '600' }}>
          {title}
        </legend>
      )}
      <div>{children}</div>
    </fieldset>
  );
};

FormGroup.craft = {
  displayName: 'FormGroup',
  isCanvas: true,
};

// ============= EXPORT BLOCK DEFINITIONS =============

/**
 * Get all input blocks as CraftBlock definitions
 */
export function getBlocks(): CraftBlock[] {
  return [
    {
      name: 'input-text',
      label: 'Text Field',
      category: 'Inputs & Forms',
      description: 'Single-line text input',
      Component: TextField,
      defaultProps: { label: 'Text Field', placeholder: 'Enter text...' },
      craft: TextField.craft,
    },
    {
      name: 'input-textarea',
      label: 'Text Area',
      category: 'Inputs & Forms',
      description: 'Multi-line text input',
      Component: TextArea,
      defaultProps: { label: 'Text Area', placeholder: 'Enter text...', rows: 4 },
      craft: TextArea.craft,
    },
    {
      name: 'input-email',
      label: 'Email Field',
      category: 'Inputs & Forms',
      description: 'Email input with validation',
      Component: EmailField,
      defaultProps: { label: 'Email', placeholder: 'Enter email...' },
      craft: EmailField.craft,
    },
    {
      name: 'input-password',
      label: 'Password Field',
      category: 'Inputs & Forms',
      description: 'Password input with masking',
      Component: PasswordField,
      defaultProps: { label: 'Password', placeholder: 'Enter password...' },
      craft: PasswordField.craft,
    },
    {
      name: 'input-checkbox',
      label: 'Checkbox',
      category: 'Inputs & Forms',
      description: 'Single checkbox input',
      Component: CheckBox,
      defaultProps: { label: 'Checkbox' },
      craft: CheckBox.craft,
    },
    {
      name: 'input-radio',
      label: 'Radio Button',
      category: 'Inputs & Forms',
      description: 'Single radio input',
      Component: RadioButton,
      defaultProps: { label: 'Radio Option' },
      craft: RadioButton.craft,
    },
    {
      name: 'input-select',
      label: 'Select Dropdown',
      category: 'Inputs & Forms',
      description: 'Dropdown select input',
      Component: SelectInput,
      defaultProps: { label: 'Select', options: ['Option 1', 'Option 2', 'Option 3'] },
      craft: SelectInput.craft,
    },
    {
      name: 'input-range',
      label: 'Range Slider',
      category: 'Inputs & Forms',
      description: 'Numeric range input',
      Component: RangeSlider,
      defaultProps: { label: 'Slider', min: 0, max: 100, step: 1 },
      craft: RangeSlider.craft,
    },
    {
      name: 'input-file',
      label: 'File Input',
      category: 'Inputs & Forms',
      description: 'File upload input',
      Component: FileInput,
      defaultProps: { label: 'Choose file' },
      craft: FileInput.craft,
    },
    {
      name: 'input-toggle',
      label: 'Toggle Switch',
      category: 'Inputs & Forms',
      description: 'iOS-style toggle switch',
      Component: ToggleSwitch,
      defaultProps: { label: 'Toggle' },
      craft: ToggleSwitch.craft,
    },
    {
      name: 'input-form-group',
      label: 'Form Group',
      category: 'Inputs & Forms',
      description: 'Container for form inputs',
      Component: FormGroup,
      defaultProps: { title: 'Form Section' },
      craft: FormGroup.craft,
    },
  ];
}
