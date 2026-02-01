/**
 * Properties Panel
 * Component property editor with type-specific properties
 */

// Component property schemas - define which properties each component type has
const componentSchemas = {
    // Text components
    'anki-field': {
        label: 'Anki Field',
        categories: [
            {
                name: 'Field Options',
                properties: [
                    { name: 'fieldName', label: 'Field Name', type: 'text', placeholder: 'e.g., Front, Back' },
                    { name: 'required', label: 'Required Field', type: 'checkbox' }
                ]
            },
            {
                name: 'Text Properties',
                properties: [
                    { name: 'fontSize', label: 'Font Size', type: 'number', min: 8, max: 72, unit: 'px' },
                    { name: 'fontColor', label: 'Font Color', type: 'color' },
                    { name: 'fontWeight', label: 'Font Weight', type: 'select', options: ['normal', 'bold', 'lighter'] },
                    { name: 'textAlign', label: 'Text Alignment', type: 'select', options: ['left', 'center', 'right'] }
                ]
            },
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'minWidth', label: 'Min Width', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Styling',
                properties: [
                    { name: 'backgroundColor', label: 'Background Color', type: 'color' },
                    { name: 'borderWidth', label: 'Border Width', type: 'number', min: 0, unit: 'px' },
                    { name: 'borderColor', label: 'Border Color', type: 'color' },
                    { name: 'borderRadius', label: 'Border Radius', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'text': {
        label: 'Text',
        categories: [
            {
                name: 'Text Content',
                properties: [
                    { name: 'content', label: 'Content', type: 'textarea', placeholder: 'Enter text content...' }
                ]
            },
            {
                name: 'Text Properties',
                properties: [
                    { name: 'fontSize', label: 'Font Size', type: 'number', min: 8, max: 72, unit: 'px', defaultValue: 14 },
                    { name: 'fontColor', label: 'Font Color', type: 'color', defaultValue: '#000000' },
                    { name: 'fontWeight', label: 'Font Weight', type: 'select', options: ['normal', 'bold', 'lighter'] },
                    { name: 'textAlign', label: 'Text Alignment', type: 'select', options: ['left', 'center', 'right'] }
                ]
            },
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'height', label: 'Height', type: 'dimension' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Styling',
                properties: [
                    { name: 'backgroundColor', label: 'Background Color', type: 'color', defaultValue: '#ffffff' },
                    { name: 'borderWidth', label: 'Border Width', type: 'number', min: 0, unit: 'px' },
                    { name: 'borderColor', label: 'Border Color', type: 'color' },
                    { name: 'borderRadius', label: 'Border Radius', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'heading': {
        label: 'Heading',
        categories: [
            {
                name: 'Text Content',
                properties: [
                    { name: 'content', label: 'Content', type: 'textarea', placeholder: 'Enter heading text...' }
                ]
            },
            {
                name: 'Text Properties',
                properties: [
                    { name: 'fontSize', label: 'Font Size', type: 'number', min: 12, max: 72, unit: 'px', defaultValue: 24 },
                    { name: 'fontColor', label: 'Font Color', type: 'color', defaultValue: '#000000' },
                    { name: 'fontWeight', label: 'Font Weight', type: 'select', options: ['normal', 'bold', 'bolder'], defaultValue: 'bold' },
                    { name: 'textAlign', label: 'Text Alignment', type: 'select', options: ['left', 'center', 'right'] }
                ]
            },
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px', defaultValue: 16 }
                ]
            }
        ]
    },
    'image': {
        label: 'Image',
        categories: [
            {
                name: 'Image Options',
                properties: [
                    { name: 'src', label: 'Source', type: 'text', placeholder: 'Image field or URL' },
                    { name: 'alt', label: 'Alt Text', type: 'text', placeholder: 'Alternative text' },
                    { name: 'maxWidth', label: 'Max Width', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'height', label: 'Height', type: 'dimension' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Styling',
                properties: [
                    { name: 'borderWidth', label: 'Border Width', type: 'number', min: 0, unit: 'px' },
                    { name: 'borderColor', label: 'Border Color', type: 'color' },
                    { name: 'borderRadius', label: 'Border Radius', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'audio': {
        label: 'Audio',
        categories: [
            {
                name: 'Audio Options',
                properties: [
                    { name: 'src', label: 'Source', type: 'text', placeholder: 'Audio field' },
                    { name: 'autoplay', label: 'Autoplay', type: 'checkbox' },
                    { name: 'controls', label: 'Show Controls', type: 'checkbox', defaultValue: true }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'container': {
        label: 'Container',
        categories: [
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'height', label: 'Height', type: 'dimension' },
                    { name: 'display', label: 'Display', type: 'select', options: ['block', 'flex', 'grid'], defaultValue: 'block' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px', defaultValue: 16 },
                    { name: 'gap', label: 'Gap (children)', type: 'number', min: 0, unit: 'px' }
                ]
            },
            {
                name: 'Styling',
                properties: [
                    { name: 'backgroundColor', label: 'Background Color', type: 'color', defaultValue: '#ffffff' },
                    { name: 'borderWidth', label: 'Border Width', type: 'number', min: 0, unit: 'px' },
                    { name: 'borderColor', label: 'Border Color', type: 'color' },
                    { name: 'borderRadius', label: 'Border Radius', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'conditional': {
        label: 'Conditional',
        categories: [
            {
                name: 'Conditional Options',
                properties: [
                    { name: 'conditionField', label: 'Field to Check', type: 'text', placeholder: 'e.g., {{Field}}' },
                    { name: 'conditionType', label: 'Condition Type', type: 'select', options: ['not-empty', 'empty', 'contains'] }
                ]
            },
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' }
                ]
            }
        ]
    },
    'cloze': {
        label: 'Cloze',
        categories: [
            {
                name: 'Text Properties',
                properties: [
                    { name: 'fontSize', label: 'Font Size', type: 'number', min: 8, max: 72, unit: 'px' },
                    { name: 'fontColor', label: 'Font Color', type: 'color' }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px' }
                ]
            }
        ]
    },
    'divider': {
        label: 'Divider',
        categories: [
            {
                name: 'Divider Style',
                properties: [
                    { name: 'color', label: 'Color', type: 'color', defaultValue: '#ddd' },
                    { name: 'thickness', label: 'Thickness', type: 'number', min: 1, max: 10, unit: 'px', defaultValue: 1 },
                    { name: 'margin', label: 'Margin', type: 'number', min: 0, unit: 'px', defaultValue: 16 }
                ]
            }
        ]
    },
    'spacer': {
        label: 'Spacer',
        categories: [
            {
                name: 'Spacer Size',
                properties: [
                    { name: 'height', label: 'Height', type: 'number', min: 0, unit: 'px', defaultValue: 16 }
                ]
            }
        ]
    },
    'h-stack': {
        label: 'H-Stack (Horizontal)',
        categories: [
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'height', label: 'Height', type: 'dimension' },
                    { name: 'alignItems', label: 'Align Items', type: 'select', options: ['flex-start', 'center', 'flex-end', 'stretch'] }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'gap', label: 'Gap', type: 'number', min: 0, unit: 'px', defaultValue: 16 }
                ]
            }
        ]
    },
    'v-stack': {
        label: 'V-Stack (Vertical)',
        categories: [
            {
                name: 'Layout',
                properties: [
                    { name: 'width', label: 'Width', type: 'dimension' },
                    { name: 'height', label: 'Height', type: 'dimension' },
                    { name: 'alignItems', label: 'Align Items', type: 'select', options: ['flex-start', 'center', 'flex-end', 'stretch'] }
                ]
            },
            {
                name: 'Spacing',
                properties: [
                    { name: 'padding', label: 'Padding', type: 'number', min: 0, unit: 'px' },
                    { name: 'gap', label: 'Gap', type: 'number', min: 0, unit: 'px', defaultValue: 16 }
                ]
            }
        ]
    }
};

// Store component properties
let componentProperties = {};

function initializePropertiesPanel() {
    console.log('Initializing properties panel...');
    
    const propertiesPanel = document.querySelector('.properties-panel');
    if (!propertiesPanel) {
        console.error('Properties panel not found');
        return false;
    }
    
    // Add event delegation for property changes
    propertiesPanel.addEventListener('change', handlePropertyChange);
    propertiesPanel.addEventListener('input', handlePropertyInput);
    
    console.log('Properties panel initialized');
    return true;
}

function clearPropertiesPanel() {
    const propertiesContent = document.querySelector('.properties-content');
    if (!propertiesContent) return;
    
    propertiesContent.innerHTML = `
        <div class="no-selection">
            Select a component to view its properties
        </div>
    `;
}

function getPropertyEditorHTML(component) {
    const type = component.type || 'unknown';
    const schema = componentSchemas[type];
    
    if (!schema) {
        return `<div class="properties-group"><div class="property-value">No properties defined for ${type}</div></div>`;
    }
    
    const props = componentProperties[component.id] || {};
    
    let html = `
        <div class="properties-group">
            <div class="properties-group-title">Component Info</div>
            <div class="property-field">
                <label class="property-label">Type</label>
                <div class="property-value">${schema.label}</div>
            </div>
            <div class="property-field">
                <label class="property-label">ID</label>
                <input type="text" class="property-input" data-property="id" value="${component.id || ''}" readonly>
            </div>
        </div>
    `;
    
    // Generate property fields based on schema
    schema.categories.forEach(category => {
        html += `<div class="properties-group">
            <div class="properties-group-title">${category.name}</div>`;
        
        category.properties.forEach(propDef => {
            const value = props[propDef.name] !== undefined ? props[propDef.name] : (propDef.defaultValue || '');
            html += generatePropertyField(propDef, value);
        });
        
        html += `</div>`;
    });
    
    return html;
}

function generatePropertyField(propDef, value) {
    let html = `<div class="property-field">`;
    
    switch (propDef.type) {
        case 'text':
            html += `
                <label class="property-label">${propDef.label}</label>
                <input type="text" class="property-input" data-property="${propDef.name}" placeholder="${propDef.placeholder || ''}" value="${value}">
            `;
            break;
            
        case 'textarea':
            html += `
                <label class="property-label">${propDef.label}</label>
                <textarea class="property-textarea" data-property="${propDef.name}" placeholder="${propDef.placeholder || ''}">${value}</textarea>
            `;
            break;
            
        case 'number':
            html += `
                <label class="property-label">${propDef.label}</label>
                <div class="property-input-row">
                    <input type="number" class="property-input" data-property="${propDef.name}" min="${propDef.min || 0}" max="${propDef.max || ''}" value="${value}">
                    ${propDef.unit ? `<span class="property-unit">${propDef.unit}</span>` : ''}
                </div>
            `;
            break;
            
        case 'color':
            html += `
                <label class="property-label">${propDef.label}</label>
                <input type="color" class="property-color-input" data-property="${propDef.name}" value="${value}">
            `;
            break;
            
        case 'select':
            html += `
                <label class="property-label">${propDef.label}</label>
                <select class="property-select" data-property="${propDef.name}">
            `;
            propDef.options.forEach(option => {
                html += `<option value="${option}" ${value === option ? 'selected' : ''}>${option}</option>`;
            });
            html += `</select>`;
            break;
            
        case 'checkbox':
            html += `
                <label class="property-checkbox">
                    <input type="checkbox" data-property="${propDef.name}" ${value ? 'checked' : ''}>
                    <span>${propDef.label}</span>
                </label>
            `;
            break;
            
        case 'dimension':
            html += `
                <label class="property-label">${propDef.label}</label>
                <div class="property-input-row">
                    <input type="number" class="property-input" data-property="${propDef.name}" placeholder="auto" value="${value}">
                    <select class="property-unit-select" data-property="${propDef.name}_unit">
                        <option value="px">px</option>
                        <option value="%">%</option>
                        <option value="auto">auto</option>
                    </select>
                </div>
            `;
            break;
    }
    
    html += `</div>`;
    return html;
}

function showComponentProperties(component) {
    const propertiesContent = document.querySelector('.properties-content');
    if (!propertiesContent) return;
    
    // Store component ID for property updates
    propertiesContent.dataset.componentId = component.id;
    
    const html = getPropertyEditorHTML(component);
    propertiesContent.innerHTML = html;
    
    console.log(`[Properties] Showing properties for component: ${component.label} (${component.type})`);
}

function handlePropertyChange(event) {
    const target = event.target;
    const property = target.dataset.property;
    
    if (!property) return;
    
    const content = document.querySelector('.properties-content');
    const componentId = content.dataset.componentId;
    
    if (!componentId) return;
    
    // Initialize component properties if not exists
    if (!componentProperties[componentId]) {
        componentProperties[componentId] = {};
    }
    
    // Store property value based on input type
    if (target.type === 'checkbox') {
        componentProperties[componentId][property] = target.checked;
    } else if (target.type === 'color') {
        componentProperties[componentId][property] = target.value;
    } else {
        componentProperties[componentId][property] = target.value;
    }
    
    // Update canvas if available
    updateCanvasComponentStyle(componentId, property, target.value, target.type);
    
    console.log(`[Properties] Updated ${property}:`, componentProperties[componentId][property]);
}

function handlePropertyInput(event) {
    const target = event.target;
    const property = target.dataset.property;
    
    if (!property || target.type === 'checkbox' || target.type === 'color') return;
    
    const content = document.querySelector('.properties-content');
    const componentId = content.dataset.componentId;
    
    if (!componentId) return;
    
    // Initialize component properties if not exists
    if (!componentProperties[componentId]) {
        componentProperties[componentId] = {};
    }
    
    componentProperties[componentId][property] = target.value;
    
    // Update canvas in real-time
    updateCanvasComponentStyle(componentId, property, target.value, target.type);
}

function updateCanvasComponentStyle(componentId, property, value, inputType) {
    const componentElement = document.querySelector(`[data-component-id="${componentId}"]`);
    if (!componentElement) return;
    
    // Map property names to CSS properties
    const cssMap = {
        'fontSize': 'fontSize',
        'fontColor': 'color',
        'fontWeight': 'fontWeight',
        'textAlign': 'textAlign',
        'width': 'width',
        'height': 'height',
        'minWidth': 'minWidth',
        'minHeight': 'minHeight',
        'padding': 'padding',
        'margin': 'margin',
        'gap': 'gap',
        'backgroundColor': 'backgroundColor',
        'borderWidth': 'borderWidth',
        'borderColor': 'borderColor',
        'borderRadius': 'borderRadius',
        'color': 'color',
        'display': 'display',
        'alignItems': 'alignItems',
        'thickness': 'borderWidth'
    };
    
    const cssProperty = cssMap[property];
    if (!cssProperty) return;
    
    // Apply CSS property based on type
    if (property.includes('Color') || property === 'backgroundColor') {
        componentElement.style[cssProperty] = value;
    } else if (property.includes('Width') || property.includes('Height') || property === 'borderRadius' || property === 'thickness') {
        componentElement.style[cssProperty] = value ? `${value}px` : '';
    } else if (property === 'padding' || property === 'margin' || property === 'gap') {
        componentElement.style[cssProperty] = value ? `${value}px` : '';
    } else {
        componentElement.style[cssProperty] = value;
    }
    
    console.log(`[Canvas Style] Applied ${cssProperty}: ${value}`);
}

// Export functions
window.propertiesModule = {
    initializePropertiesPanel,
    clearPropertiesPanel,
    showComponentProperties,
    getComponentProperties: (componentId) => componentProperties[componentId] || {},
    setComponentProperties: (componentId, props) => {
        componentProperties[componentId] = { ...componentProperties[componentId], ...props };
    }
};
