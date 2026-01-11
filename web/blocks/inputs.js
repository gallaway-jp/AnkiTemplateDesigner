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
                    type: 'text-input',
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
                    type: 'textarea-input',
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
                { tagName: 'div', style: { position: 'relative', width: '48px', height: '28px', background: '#ccc', 'border-radius': '28px' }, components: [
                    { type: 'checkbox-input', style: { opacity: '0', width: '0', height: '0' } },
                    { tagName: 'span', classes: ['atd-toggle-slider'], style: { position: 'absolute', top: '4px', left: '4px', width: '20px', height: '20px', background: '#fff', 'border-radius': '50%', transition: '0.3s' } }
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
