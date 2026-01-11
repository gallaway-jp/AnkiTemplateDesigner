# 04b - Component Library: Input, Form & Button Blocks

> **Purpose**: Define GrapeJS blocks for Input, Form, and Button components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026
> **Updated**: Based on VALIDATION-REPORT.md - Added component types with validation traits

---

## Overview

This document defines blocks for:
- **Basic Inputs** (3 components: text, textarea, password)
- **Selection Inputs** (4 components: checkbox, radio, toggle, dropdown)
- **Advanced Inputs** (3 components: date, slider, rating)
- **Form Structure** (3 components: form, field-group, required indicator)
- **Buttons & Actions** (5 components: primary, secondary, icon, destructive, link)

**Updated**: Based on COMPONENT-AUDIT.md - removed email/url/phone/search field variants (consolidate to text-field), removed advanced pickers (color, file, range-slider), removed redundant button variants (tertiary, text, ghost, FAB, loading, split, toggle, button-group). Added validation traits per VALIDATION-REPORT.md.

---

## Component Type Registration

### `web/components/inputs.js`

```javascript
/**
 * Register input component types with validation traits
 */
export function registerInputComponentTypes(editor) {
    // Text Input Component Type (with validation traits)
    editor.DomComponents.addType('text-input', {
        isComponent: el => el.tagName === 'INPUT' && el.type === 'text',
        model: {
            defaults: {
                tagName: 'input',
                draggable: true,
                droppable: false,
                attributes: { type: 'text' },
                traits: [
                    { type: 'text', name: 'name', label: 'Name' },
                    { type: 'text', name: 'placeholder', label: 'Placeholder' },
                    { type: 'checkbox', name: 'required', label: 'Required' },
                    { type: 'text', name: 'pattern', label: 'Pattern (regex)' },
                    { type: 'number', name: 'minlength', label: 'Min Length', min: 0 },
                    { type: 'number', name: 'maxlength', label: 'Max Length', min: 0 }
                ]
            }
        }
    });
    
    // Textarea Component Type
    editor.DomComponents.addType('textarea-input', {
        isComponent: el => el.tagName === 'TEXTAREA',
        model: {
            defaults: {
                tagName: 'textarea',
                draggable: true,
                droppable: false,
                traits: [
                    { type: 'text', name: 'name', label: 'Name' },
                    { type: 'text', name: 'placeholder', label: 'Placeholder' },
                    { type: 'checkbox', name: 'required', label: 'Required' },
                    { type: 'number', name: 'rows', label: 'Rows', min: 1, max: 20 },
                    { type: 'number', name: 'minlength', label: 'Min Length', min: 0 },
                    { type: 'number', name: 'maxlength', label: 'Max Length', min: 0 }
                ]
            }
        }
    });
    
    // Select Component Type
    editor.DomComponents.addType('select-input', {
        isComponent: el => el.tagName === 'SELECT',
        model: {
            defaults: {
                tagName: 'select',
                draggable: true,
                droppable: false,
                traits: [
                    { type: 'text', name: 'name', label: 'Name' },
                    { type: 'checkbox', name: 'required', label: 'Required' },
                    { type: 'checkbox', name: 'multiple', label: 'Multiple Selection' }
                ]
            }
        }
    });
    
    // Checkbox Component Type
    editor.DomComponents.addType('checkbox-input', {
        isComponent: el => el.tagName === 'INPUT' && el.type === 'checkbox',
        model: {
            defaults: {
                tagName: 'input',
                draggable: true,
                droppable: false,
                attributes: { type: 'checkbox' },
                traits: [
                    { type: 'text', name: 'name', label: 'Name' },
                    { type: 'text', name: 'value', label: 'Value' },
                    { type: 'checkbox', name: 'checked', label: 'Checked by Default' },
                    { type: 'checkbox', name: 'required', label: 'Required' }
                ]
            }
        }
    });
    
    // Radio Button Component Type
    editor.DomComponents.addType('radio-input', {
        isComponent: el => el.tagName === 'INPUT' && el.type === 'radio',
        model: {
            defaults: {
                tagName: 'input',
                draggable: true,
                droppable: false,
                attributes: { type: 'radio' },
                traits: [
                    { type: 'text', name: 'name', label: 'Group Name' },
                    { type: 'text', name: 'value', label: 'Value' },
                    { type: 'checkbox', name: 'checked', label: 'Selected by Default' },
                    { type: 'checkbox', name: 'required', label: 'Required' }
                ]
            }
        }
    });
}
```

---

## 3. Input & Form Elements

### `web/blocks/inputs.js`

```javascript
/**
 * Input & Form Component Blocks
 * NOTE: Call registerInputComponentTypes() before registering blocks
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
                { 
                    type: 'text-input', // Uses component type with validation traits
                    attributes: { type: 'text', id: 'text-input', placeholder: 'Enter text...' }, 
                    style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px' } 
                }
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
                { 
                    type: 'textarea-input', // Uses component type with validation traits
                    attributes: { rows: '4', placeholder: 'Enter text...' }, 
                    style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px', resize: 'vertical' } 
                }
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
                { type: 'checkbox-input', style: { width: '18px', height: '18px', cursor: 'pointer' } },
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
                { tagName: 'label', style: { display: 'flex', 'align-items': 'center', gap: '8px', cursor: 'pointer', 'margin-bottom': '8px' }, components: [
                    { type: 'radio-input', attributes: { name: 'radio-group' }, style: { width: '18px', height: '18px' } }, 
                    { tagName: 'span', content: 'Option 1' }
                ]},
                { tagName: 'label', style: { display: 'flex', 'align-items': 'center', gap: '8px', cursor: 'pointer' }, components: [
                    { type: 'radio-input', attributes: { name: 'radio-group' }, style: { width: '18px', height: '18px' } }, 
                    { tagName: 'span', content: 'Option 2' }
                ]}
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
                    { type: 'checkbox-input', style: { opacity: '0', width: '0', height: '0' } },
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
                { 
                    type: 'select-input', 
                    style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'font-size': '16px', background: '#fff' }, 
                    components: [
                        { tagName: 'option', content: 'Option 1', attributes: { value: '1' } },
                        { tagName: 'option', content: 'Option 2', attributes: { value: '2' } },
                        { tagName: 'option', content: 'Option 3', attributes: { value: '3' } }
                    ]
                }
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

## Buttons & Actions

### `web/blocks/buttons.js`

Consolidated button variants for Anki review workflow:

```javascript
/**
 * Button & Action Component Blocks (Consolidated)
 */

export function registerButtonBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Buttons & Actions';
    
    // Primary Button (Primary action, Answer reveal, etc.)
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
    
    // Secondary Button (Alternative action)
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
    
    // Icon Button (Compact action, settings, etc.)
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
    
    // Destructive Button (Delete, Hard, etc.)
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
    
    // Link Button (Text-only link styled as button)
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

## Removed Components

The following components are NOT needed for Anki templates:
- **Email/URL/Phone inputs** (consolidate to text-field with type attribute)
- **Search field** (can be done with text-field)
- **Number input** (rarely needed in Anki)
- **Segmented control** (use buttons or tabs)
- **Chip selector** (not applicable to study flow)
- **Time picker** (not commonly needed)
- **Color picker** (no color selection in templates)
- **File upload** (can't upload in review mode)
- **Range slider** (single slider sufficient)

**Button variants consolidated to 5 core types**:
- ~~Tertiary~~ → Secondary handles this
- ~~Text Button~~ → Use link styling or secondary
- ~~Ghost Button~~ → Secondary variant
- ~~FAB~~ → Use icon-button or primary in study action bar
- ~~Loading Button~~ → Use state management
- ~~Split Button~~ → Use separate buttons
- ~~Toggle Button~~ → Use state management
- ~~Button Group~~ → Use flexbox layout

---

## Component Traits (Properties)

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
                        { id: 'ankiShowAnswer', name: 'Show Answer' },
                        { id: 'ankiMarkCard', name: 'Mark Card' },
                        { id: 'ankiSuspendCard', name: 'Suspend Card' },
                        { id: 'ankiBuryCard', name: 'Bury Card' },
                        { id: 'ankiAnswerEase1', name: 'Rate: Again' },
                        { id: 'ankiAnswerEase2', name: 'Rate: Hard' },
                        { id: 'ankiAnswerEase3', name: 'Rate: Good' },
                        { id: 'ankiAnswerEase4', name: 'Rate: Easy' },
                        { id: 'ankiToggleFlag', name: 'Toggle Flag' },
                        { id: 'ankiTtsSpeak', name: 'Speak Text (TTS)' }
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
