/**
 * Input Component Types
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
