/**
 * Anki Plugin for GrapeJS
 * Custom plugin that adds Anki-specific functionality to GrapeJS
 */

(function() {
    'use strict';
    
    /**
     * Anki Plugin for GrapeJS
     * @param {object} editor - GrapeJS editor instance
     * @param {object} opts - Plugin options
     */
    grapesjs.plugins.add('anki-plugin', function(editor, opts) {
        const options = {
            ...{
                // Default options
                validateOnSave: true,
                autoSaveInterval: 30000,
                showFieldNames: true,
                showBehaviorMarkers: true
            },
            ...opts
        };
        
        console.log('[Anki Plugin] Initializing with options:', options);
        
        // ========== Component Type Definitions ========== 
        
        const domc = editor.DomComponents;
        const defaultType = domc.getType('default');
        const defaultModel = defaultType.model;
        
        // Anki Field Component Type
        domc.addType('anki-field', {
            model: defaultModel.extend({
                defaults: {
                    ...defaultModel.prototype.defaults,
                    name: 'Anki Field',
                    droppable: false,
                    editable: true,
                    traits: [
                        {
                            type: 'anki-field-select',
                            label: 'Field',
                            name: 'data-anki-field'
                        }
                    ]
                },
                
                init() {
                    this.on('change:attributes:data-anki-field', this.handleFieldChange);
                },
                
                handleFieldChange() {
                    const field = this.getAttributes()['data-anki-field'];
                    if (field && this.components().length === 0) {
                        this.components(`{{${field}}}`);
                    }
                }
            }, {
                isComponent(el) {
                    if (el.hasAttribute && el.hasAttribute('data-anki-field')) {
                        return { type: 'anki-field' };
                    }
                }
            })
        });
        
        // Anki Behavior Component (for components with behaviors)
        domc.addType('anki-behavior', {
            model: defaultModel.extend({
                defaults: {
                    ...defaultModel.prototype.defaults,
                    name: 'Interactive Component',
                    traits: [
                        {
                            type: 'trigger-select',
                            label: 'Trigger',
                            name: 'trigger'
                        },
                        {
                            type: 'anki-behavior',
                            label: 'Action',
                            name: 'behavior'
                        }
                    ]
                }
            }, {
                isComponent(el) {
                    if (el.hasAttribute && (
                        el.hasAttribute('data-anki-click') ||
                        el.hasAttribute('data-anki-dblclick') ||
                        el.hasAttribute('data-anki-mouseover')
                    )) {
                        return { type: 'anki-behavior' };
                    }
                }
            })
        });
        
        // ========== Validation ========== 
        
        /**
         * Validate template before saving
         */
        function validateTemplate() {
            const wrapper = editor.DomComponents.getWrapper();
            const errors = [];
            
            // Check for required fields
            const components = wrapper.findType('anki-field');
            if (components.length === 0) {
                errors.push('No Anki fields found. Add at least one field.');
            }
            
            // Check for duplicate field bindings on same card side
            const fieldNames = {};
            components.forEach(comp => {
                const field = comp.getAttributes()['data-anki-field'];
                const cardSide = comp.getAttributes()['data-card-side'] || 'front';
                const key = `${cardSide}:${field}`;
                
                if (fieldNames[key]) {
                    errors.push(`Field ${field} is used multiple times on ${cardSide} side`);
                }
                fieldNames[key] = true;
            });
            
            return {
                valid: errors.length === 0,
                errors
            };
        }
        
        // ========== Auto-save ========== 
        
        if (options.autoSaveInterval > 0) {
            setInterval(() => {
                if (window.saveProject) {
                    console.log('[Anki Plugin] Auto-saving...');
                    window.saveProject();
                }
            }, options.autoSaveInterval);
        }
        
        // ========== Event Handlers ========== 
        
        // Component selected - show Anki-specific panels
        editor.on('component:selected', (component) => {
            const type = component.get('type');
            console.log('[Anki Plugin] Component selected:', type);
            
            // Show relevant traits based on component type
            if (type === 'anki-field') {
                // Highlight field selector in traits panel
            }
        });
        
        // Before save - validate template
        editor.on('storage:store', (storageData) => {
            if (options.validateOnSave) {
                const validation = validateTemplate();
                if (!validation.valid) {
                    console.error('[Anki Plugin] Validation errors:', validation.errors);
                    
                    if (window.bridge) {
                        window.bridge.showError('Validation errors:\n' + validation.errors.join('\n'));
                    }
                    
                    return false; // Prevent save
                }
            }
        });
        
        // Canvas frame loaded
        editor.on('canvas:ready', () => {
            console.log('[Anki Plugin] Canvas ready');
            
            // Inject custom styles into canvas
            const frame = editor.Canvas.getFrameEl();
            if (frame && frame.contentWindow) {
                const doc = frame.contentWindow.document;
                const style = doc.createElement('style');
                style.textContent = `
                    [data-anki-field]::before {
                        content: "{{" attr(data-anki-field) "}}";
                        background: #4CAF50;
                        color: white;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: 600;
                        margin-right: 6px;
                        font-family: monospace;
                    }
                    
                    [data-anki-behaviors]::after {
                        content: "⚡";
                        position: absolute;
                        top: 2px;
                        right: 2px;
                        background: #FF9800;
                        color: white;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                `;
                doc.head.appendChild(style);
            }
        });
        
        // ========== Commands ========== 
        
        editor.Commands.add('validate-template', {
            run(editor) {
                const validation = validateTemplate();
                
                if (validation.valid) {
                    if (window.bridge) {
                        window.bridge.log('Template validation passed ✓');
                    }
                    console.log('[Anki Plugin] Validation passed');
                } else {
                    if (window.bridge) {
                        window.bridge.showError('Validation errors:\n' + validation.errors.join('\n'));
                    }
                    console.error('[Anki Plugin] Validation errors:', validation.errors);
                }
            }
        });
        
        // ========== Public API ========== 
        
        // Expose validation function
        editor.AnkiPlugin = {
            validate: validateTemplate,
            options: options
        };
        
        console.log('[Anki Plugin] Initialization complete');
    });
})();
