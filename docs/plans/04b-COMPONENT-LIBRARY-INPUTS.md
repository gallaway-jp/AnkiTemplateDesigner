# 04b - Component Library: Input, Form & Button Blocks

> **Purpose**: Define GrapeJS blocks for Input, Form, and Button components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

This document defines blocks for:
- **Basic Inputs** (8 components)
- **Selection Inputs** (10 components)
- **Advanced Inputs** (11 components)
- **Form Structure** (8 components)
- **Buttons & Actions** (13 components)

---

## 3. Input & Form Elements

### `web/blocks/inputs.js`

```javascript
/**
 * Input & Form Component Blocks
 */

export function registerInputBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Inputs & Forms';
    
    // ========== BASIC INPUTS ==========
    
    // Text Field
    bm.add('text-field', {
        label: 'Text Field',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Label', attributes: { for: 'text-input' }, style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'text', id: 'text-input', placeholder: 'Enter text...' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Text Area
    bm.add('text-area', {
        label: 'Text Area',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Label', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'textarea', attributes: { rows: '4', placeholder: 'Enter text...' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px', resize: 'vertical' } }
            ]
        }
    });
    
    // Password Field
    bm.add('password-field', {
        label: 'Password Field',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Password', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'password', placeholder: '••••••••' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Number Input
    bm.add('number-input', {
        label: 'Number Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Number', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'number', min: '0', step: '1' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Search Field
    bm.add('search-field', {
        label: 'Search Field',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-search-field'],
            style: { position: 'relative' },
            components: [
                { tagName: 'span', content: '🔍', style: { position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', 'font-size': '16px' } },
                { tagName: 'input', attributes: { type: 'search', placeholder: 'Search...' }, style: { width: '100%', padding: '10px 12px 10px 40px', border: '1px solid #e0e0e0', 'border-radius': '20px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Email Input
    bm.add('email-input', {
        label: 'Email Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Email', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'email', placeholder: 'email@example.com' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // URL Input
    bm.add('url-input', {
        label: 'URL Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Website', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'url', placeholder: 'https://' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Phone Input
    bm.add('phone-input', {
        label: 'Phone Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Phone', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'tel', placeholder: '+1 (555) 000-0000' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // ========== SELECTION INPUTS ==========
    
    // Checkbox
    bm.add('checkbox', {
        label: 'Checkbox',
        category,
        content: {
            tagName: 'label',
            classes: ['atd-checkbox'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px', cursor: 'pointer' },
            components: [
                { tagName: 'input', attributes: { type: 'checkbox' }, style: { width: '18px', height: '18px', cursor: 'pointer' } },
                { tagName: 'span', content: 'Checkbox label' }
            ]
        }
    });
    
    // Radio Button
    bm.add('radio-button', {
        label: 'Radio Button',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-radio-group'],
            components: [
                { tagName: 'label', style: { display: 'flex', 'align-items': 'center', gap: '8px', cursor: 'pointer', 'margin-bottom': '8px' }, components: [{ tagName: 'input', attributes: { type: 'radio', name: 'radio-group' }, style: { width: '18px', height: '18px' } }, { tagName: 'span', content: 'Option 1' }] },
                { tagName: 'label', style: { display: 'flex', 'align-items': 'center', gap: '8px', cursor: 'pointer' }, components: [{ tagName: 'input', attributes: { type: 'radio', name: 'radio-group' }, style: { width: '18px', height: '18px' } }, { tagName: 'span', content: 'Option 2' }] }
            ]
        }
    });
    
    // Toggle Switch
    bm.add('toggle-switch', {
        label: 'Toggle Switch',
        category,
        content: {
            tagName: 'label',
            classes: ['atd-toggle'],
            style: { display: 'flex', 'align-items': 'center', gap: '12px', cursor: 'pointer' },
            components: [
                { tagName: 'div', style: { position: 'relative', width: '48px', height: '28px' }, components: [
                    { tagName: 'input', attributes: { type: 'checkbox' }, style: { opacity: '0', width: '0', height: '0' } },
                    { tagName: 'span', classes: ['atd-toggle-slider'], style: { position: 'absolute', top: '0', left: '0', right: '0', bottom: '0', background: '#ccc', 'border-radius': '28px', transition: '0.3s' } }
                ]},
                { tagName: 'span', content: 'Toggle label' }
            ]
        }
    });
    
    // Dropdown / Select
    bm.add('dropdown', {
        label: 'Dropdown',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Select option', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'select', style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px', background: '#fff' }, components: [
                    { tagName: 'option', content: 'Option 1', attributes: { value: '1' } },
                    { tagName: 'option', content: 'Option 2', attributes: { value: '2' } },
                    { tagName: 'option', content: 'Option 3', attributes: { value: '3' } }
                ]}
            ]
        }
    });
    
    // Segmented Control
    bm.add('segmented-control', {
        label: 'Segmented Control',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-segmented'],
            style: { display: 'inline-flex', border: '1px solid #e0e0e0', 'border-radius': '8px', overflow: 'hidden' },
            components: [
                { tagName: 'button', content: 'Day', style: { padding: '8px 16px', border: 'none', background: '#1976d2', color: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Week', style: { padding: '8px 16px', border: 'none', 'border-left': '1px solid #e0e0e0', background: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Month', style: { padding: '8px 16px', border: 'none', 'border-left': '1px solid #e0e0e0', background: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Chip Selector
    bm.add('chip-selector', {
        label: 'Chip Selector',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-chips'],
            style: { display: 'flex', 'flex-wrap': 'wrap', gap: '8px' },
            components: [
                { tagName: 'button', content: 'Chip 1', style: { padding: '6px 16px', 'border-radius': '20px', border: '1px solid #1976d2', background: '#e3f2fd', color: '#1976d2', cursor: 'pointer' } },
                { tagName: 'button', content: 'Chip 2', style: { padding: '6px 16px', 'border-radius': '20px', border: '1px solid #e0e0e0', background: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Chip 3', style: { padding: '6px 16px', 'border-radius': '20px', border: '1px solid #e0e0e0', background: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // ========== ADVANCED INPUTS ==========
    
    // Date Picker
    bm.add('date-picker', {
        label: 'Date Picker',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Date', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'date' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Time Picker
    bm.add('time-picker', {
        label: 'Time Picker',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            components: [
                { tagName: 'label', content: 'Time', style: { display: 'block', 'margin-bottom': '4px', 'font-size': '14px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'time' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } }
            ]
        }
    });
    
    // Color Picker
    bm.add('color-picker', {
        label: 'Color Picker',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-field'],
            style: { display: 'flex', 'align-items': 'center', gap: '12px' },
            components: [
                { tagName: 'input', attributes: { type: 'color', value: '#1976d2' }, style: { width: '48px', height: '48px', border: 'none', 'border-radius': '8px', cursor: 'pointer' } },
                { tagName: 'span', content: 'Choose color' }
            ]
        }
    });
    
    // File Upload
    bm.add('file-upload', {
        label: 'File Upload',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-file-upload'],
            style: { border: '2px dashed #e0e0e0', 'border-radius': '8px', padding: '24px', 'text-align': 'center' },
            components: [
                { tagName: 'div', content: '📁', style: { 'font-size': '32px', 'margin-bottom': '8px' } },
                { tagName: 'p', content: 'Drop files here or click to upload', style: { margin: '0 0 12px', color: '#666' } },
                { tagName: 'input', attributes: { type: 'file' }, style: { display: 'none' } },
                { tagName: 'button', content: 'Browse Files', style: { padding: '8px 16px', border: '1px solid #1976d2', background: '#fff', color: '#1976d2', 'border-radius': '6px', cursor: 'pointer' } }
            ]
        }
    });
    
    // Slider
    bm.add('slider', {
        label: 'Slider',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-slider'],
            components: [
                { tagName: 'label', content: 'Value: 50', style: { display: 'block', 'margin-bottom': '8px' } },
                { tagName: 'input', attributes: { type: 'range', min: '0', max: '100', value: '50' }, style: { width: '100%' } }
            ]
        }
    });
    
    // Range Slider
    bm.add('range-slider', {
        label: 'Range Slider',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-range-slider'],
            components: [
                { tagName: 'label', content: 'Range: 20 - 80', style: { display: 'block', 'margin-bottom': '8px' } },
                { tagName: 'div', style: { display: 'flex', gap: '8px' }, components: [
                    { tagName: 'input', attributes: { type: 'range', min: '0', max: '100', value: '20' }, style: { flex: '1' } },
                    { tagName: 'input', attributes: { type: 'range', min: '0', max: '100', value: '80' }, style: { flex: '1' } }
                ]}
            ]
        }
    });
    
    // Rating Input
    bm.add('rating-input', {
        label: 'Rating Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-rating'],
            style: { display: 'flex', gap: '4px' },
            components: [
                { tagName: 'button', content: '★', style: { border: 'none', background: 'none', 'font-size': '24px', color: '#ffc107', cursor: 'pointer' } },
                { tagName: 'button', content: '★', style: { border: 'none', background: 'none', 'font-size': '24px', color: '#ffc107', cursor: 'pointer' } },
                { tagName: 'button', content: '★', style: { border: 'none', background: 'none', 'font-size': '24px', color: '#ffc107', cursor: 'pointer' } },
                { tagName: 'button', content: '☆', style: { border: 'none', background: 'none', 'font-size': '24px', color: '#e0e0e0', cursor: 'pointer' } },
                { tagName: 'button', content: '☆', style: { border: 'none', background: 'none', 'font-size': '24px', color: '#e0e0e0', cursor: 'pointer' } }
            ]
        }
    });
    
    // ========== FORM STRUCTURE ==========
    
    // Form
    bm.add('form', {
        label: 'Form',
        category,
        content: {
            tagName: 'form',
            classes: ['atd-form'],
            style: { padding: '20px' },
            components: [
                { tagName: 'div', classes: ['atd-form-group'], style: { 'margin-bottom': '16px' } }
            ]
        }
    });
    
    // Field Group
    bm.add('field-group', {
        label: 'Field Group',
        category,
        content: {
            tagName: 'fieldset',
            classes: ['atd-field-group'],
            style: { border: '1px solid #e0e0e0', 'border-radius': '8px', padding: '16px', margin: '0 0 16px' },
            components: [
                { tagName: 'legend', content: 'Group Label', style: { padding: '0 8px', 'font-weight': '600' } }
            ]
        }
    });
    
    // Helper Text
    bm.add('helper-text', {
        label: 'Helper Text',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-helper-text'],
            content: 'This is helper text',
            style: { display: 'block', 'font-size': '12px', color: '#666', 'margin-top': '4px' }
        }
    });
    
    // Error Message
    bm.add('error-message', {
        label: 'Error Message',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-error-message'],
            content: 'This field is required',
            style: { display: 'block', 'font-size': '12px', color: '#d32f2f', 'margin-top': '4px' }
        }
    });
    
    // Required Indicator
    bm.add('required-indicator', {
        label: 'Required *',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-required'],
            content: '*',
            style: { color: '#d32f2f', 'margin-left': '4px' }
        }
    });
}
```

---

## 4. Buttons & Actions

### `web/blocks/buttons.js`

```javascript
/**
 * Button & Action Component Blocks
 */

export function registerButtonBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Buttons & Actions';
    
    // Primary Button
    bm.add('primary-button', {
        label: 'Primary Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-primary'],
            content: 'Primary',
            style: {
                padding: '12px 24px',
                border: 'none',
                'border-radius': '8px',
                background: '#1976d2',
                color: '#ffffff',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer'
            }
        }
    });
    
    // Secondary Button
    bm.add('secondary-button', {
        label: 'Secondary Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-secondary'],
            content: 'Secondary',
            style: {
                padding: '12px 24px',
                border: '1px solid #1976d2',
                'border-radius': '8px',
                background: 'transparent',
                color: '#1976d2',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer'
            }
        }
    });
    
    // Tertiary Button
    bm.add('tertiary-button', {
        label: 'Tertiary Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-tertiary'],
            content: 'Tertiary',
            style: {
                padding: '12px 24px',
                border: 'none',
                'border-radius': '8px',
                background: 'transparent',
                color: '#1976d2',
                'font-size': '16px',
                cursor: 'pointer'
            }
        }
    });
    
    // Icon Button
    bm.add('icon-button', {
        label: 'Icon Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn-icon'],
            content: '⚙️',
            attributes: { 'aria-label': 'Settings' },
            style: {
                width: '44px',
                height: '44px',
                border: 'none',
                'border-radius': '50%',
                background: '#f5f5f5',
                'font-size': '20px',
                cursor: 'pointer',
                display: 'flex',
                'align-items': 'center',
                'justify-content': 'center'
            }
        }
    });
    
    // Floating Action Button (FAB)
    bm.add('fab', {
        label: 'FAB',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-fab'],
            content: '+',
            style: {
                width: '56px',
                height: '56px',
                border: 'none',
                'border-radius': '50%',
                background: '#1976d2',
                color: '#ffffff',
                'font-size': '24px',
                cursor: 'pointer',
                'box-shadow': '0 4px 12px rgba(0,0,0,0.2)',
                position: 'fixed',
                bottom: '24px',
                right: '24px'
            }
        }
    });
    
    // Text Button
    bm.add('text-button', {
        label: 'Text Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn-text'],
            content: 'Text Button',
            style: {
                padding: '8px 12px',
                border: 'none',
                background: 'transparent',
                color: '#1976d2',
                'font-size': '14px',
                cursor: 'pointer'
            }
        }
    });
    
    // Ghost Button
    bm.add('ghost-button', {
        label: 'Ghost Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn-ghost'],
            content: 'Ghost Button',
            style: {
                padding: '12px 24px',
                border: '1px solid #e0e0e0',
                'border-radius': '8px',
                background: 'transparent',
                color: '#333',
                'font-size': '16px',
                cursor: 'pointer'
            }
        }
    });
    
    // Destructive Button
    bm.add('destructive-button', {
        label: 'Destructive Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-destructive'],
            content: 'Delete',
            style: {
                padding: '12px 24px',
                border: 'none',
                'border-radius': '8px',
                background: '#d32f2f',
                color: '#ffffff',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer'
            }
        }
    });
    
    // Loading Button
    bm.add('loading-button', {
        label: 'Loading Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-loading'],
            style: {
                padding: '12px 24px',
                border: 'none',
                'border-radius': '8px',
                background: '#1976d2',
                color: '#ffffff',
                'font-size': '16px',
                cursor: 'pointer',
                display: 'flex',
                'align-items': 'center',
                gap: '8px'
            },
            components: [
                { tagName: 'span', content: '⟳', classes: ['atd-spinner'], style: { animation: 'spin 1s linear infinite' } },
                { tagName: 'span', content: 'Loading...' }
            ]
        }
    });
    
    // Split Button
    bm.add('split-button', {
        label: 'Split Button',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-split-button'],
            style: { display: 'inline-flex' },
            components: [
                { tagName: 'button', content: 'Save', style: { padding: '12px 20px', border: 'none', 'border-radius': '8px 0 0 8px', background: '#1976d2', color: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: '▾', style: { padding: '12px 8px', border: 'none', 'border-radius': '0 8px 8px 0', background: '#1565c0', color: '#fff', cursor: 'pointer', 'border-left': '1px solid rgba(255,255,255,0.3)' } }
            ]
        }
    });
    
    // Toggle Button
    bm.add('toggle-button', {
        label: 'Toggle Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn-toggle'],
            content: '🔔 Notifications',
            attributes: { 'aria-pressed': 'false' },
            style: {
                padding: '10px 16px',
                border: '1px solid #e0e0e0',
                'border-radius': '8px',
                background: '#fff',
                cursor: 'pointer'
            }
        }
    });
    
    // Button Group
    bm.add('button-group', {
        label: 'Button Group',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-btn-group'],
            style: { display: 'inline-flex' },
            components: [
                { tagName: 'button', content: 'Left', style: { padding: '10px 16px', border: '1px solid #e0e0e0', background: '#fff', cursor: 'pointer', 'border-radius': '8px 0 0 8px' } },
                { tagName: 'button', content: 'Center', style: { padding: '10px 16px', border: '1px solid #e0e0e0', 'border-left': 'none', background: '#e3f2fd', cursor: 'pointer' } },
                { tagName: 'button', content: 'Right', style: { padding: '10px 16px', border: '1px solid #e0e0e0', 'border-left': 'none', background: '#fff', cursor: 'pointer', 'border-radius': '0 8px 8px 0' } }
            ]
        }
    });
    
    // Link Button
    bm.add('link-button', {
        label: 'Link Button',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-btn', 'atd-btn-primary'],
            content: 'Link Button',
            attributes: { href: '#', role: 'button' },
            style: {
                display: 'inline-block',
                padding: '12px 24px',
                'border-radius': '8px',
                background: '#1976d2',
                color: '#ffffff',
                'text-decoration': 'none',
                'font-size': '16px',
                'font-weight': '500'
            }
        }
    });
}
```

---

## Traits for Input Components

### Input Traits

```javascript
// Register input traits
editor.DomComponents.addType('text-field', {
    model: {
        defaults: {
            traits: [
                { type: 'text', name: 'name', label: 'Field Name' },
                { type: 'text', name: 'placeholder', label: 'Placeholder' },
                { type: 'checkbox', name: 'required', label: 'Required' },
                { type: 'checkbox', name: 'disabled', label: 'Disabled' },
                {
                    type: 'select',
                    name: 'anki-field',
                    label: 'Bind to Anki Field',
                    options: () => window.ankiFields || []
                }
            ]
        }
    }
});

// Button traits with AnkiJSApi behaviors
editor.DomComponents.addType('primary-button', {
    model: {
        defaults: {
            traits: [
                { type: 'text', name: 'text', label: 'Button Text' },
                {
                    type: 'select',
                    name: 'anki-behavior',
                    label: 'Anki Behavior',
                    options: () => [
                        { id: '', name: '(none)' },
                        { id: 'showAnswer', name: 'Show Answer' },
                        { id: 'flipCard', name: 'Flip Card' },
                        { id: 'playAudio', name: 'Play Audio' },
                        { id: 'rateAgain', name: 'Rate: Again' },
                        { id: 'rateGood', name: 'Rate: Good' },
                        { id: 'rateEasy', name: 'Rate: Easy' }
                    ]
                },
                { type: 'checkbox', name: 'disabled', label: 'Disabled' }
            ]
        }
    }
});
```

---

## Next Document

See [04c-COMPONENT-LIBRARY-DATA.md](04c-COMPONENT-LIBRARY-DATA.md) for Data Display, Feedback, and Overlay components.
