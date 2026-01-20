/**
 * Component Type Registration
 * 
 * CRITICAL: GrapeJS checks component types in REVERSE registration order.
 * - Register generic/base components FIRST
 * - Register specific/custom components LAST (checked first)
 * 
 * This file must be loaded and called BEFORE block registration.
 */

// Load input components if available
function loadInputComponents() {
    // Check if registerInputComponentTypes is already loaded
    if (typeof registerInputComponentTypes === 'function') {
        return true;
    }
    // Otherwise, we'll use a no-op
    return false;
}

/**
 * Register all custom component types
 * MUST be called before block registration
 */
function registerComponentTypes(editor) {
    // Register in order: generic first, specific last
    // (GrapeJS checks in reverse order)
    
    // 1. Base layout components (generic)
    registerBaseComponents(editor);
    
    // 2. Input components (if available)
    if (typeof registerInputComponentTypes === 'function') {
        registerInputComponentTypes(editor);
    }
    
    // 3. Anki-specific components (checked first)
    registerStudyActionBarComponent(editor);
}

// Make available globally for non-module scripts
window.registerComponentTypes = registerComponentTypes;

// Signal that the module is ready
window.ankiComponentsModuleReady = true;
console.log('[Modules] Components module loaded');

/**
 * Register base layout component types
 */
function registerBaseComponents(editor) {
    // Frame component type
    editor.DomComponents.addType('frame', {
        isComponent: el => el.classList?.contains('atd-frame'),
        model: {
            defaults: {
                tagName: 'div',
                draggable: true,
                droppable: true,
                traits: [
                    { type: 'text', name: 'id', label: 'ID' },
                    { 
                        type: 'select', 
                        name: 'device', 
                        label: 'Device', 
                        options: [
                            { id: 'mobile', label: 'Mobile (375x667)' },
                            { id: 'tablet', label: 'Tablet (768x1024)' },
                            { id: 'desktop', label: 'Desktop (1920x1080)' }
                        ]
                    },
                    { type: 'color', name: 'background', label: 'Background' }
                ]
            }
        }
    });
    
    // Card component type
    editor.DomComponents.addType('card', {
        isComponent: el => el.classList?.contains('atd-card'),
        model: {
            defaults: {
                tagName: 'div',
                draggable: true,
                droppable: true,
                traits: [
                    { type: 'text', name: 'id', label: 'ID' },
                    { 
                        type: 'select', 
                        name: 'elevation', 
                        label: 'Elevation', 
                        options: [
                            { id: '1', label: 'Low' },
                            { id: '2', label: 'Medium' },
                            { id: '3', label: 'High' }
                        ]
                    },
                    { type: 'checkbox', name: 'clickable', label: 'Clickable' }
                ]
            }
        }
    });
}

/**
 * Register Study Action Bar Component
 * Specialized toolbar for Anki review session controls
 */
function registerStudyActionBarComponent(editor) {
    editor.DomComponents.addType('study-action-bar', {
        // Recognize existing elements when importing HTML
        isComponent: el => {
            // Check by class
            if (el.classList?.contains('atd-study-action-bar')) {
                return { type: 'study-action-bar' };
            }
            // Check by data attribute
            if (el.getAttribute?.('data-gjs-type') === 'study-action-bar') {
                return { type: 'study-action-bar' };
            }
            return false;
        },
        
        model: {
            defaults: {
                tagName: 'div',
                draggable: true,
                droppable: true,
                attributes: { class: 'atd-study-action-bar' },
                style: {
                    display: 'flex',
                    'align-items': 'center',
                    'justify-content': 'flex-start',
                    padding: '12px 16px',
                    background: '#f5f5f5',
                    border: '1px solid #e0e0e0',
                    'border-radius': '8px',
                    gap: '8px',
                    'flex-direction': 'row'
                },
                traits: [
                    {
                        type: 'select',
                        name: 'placement',
                        label: 'Position',
                        changeProp: true, // Bind to property instead of attribute
                        options: [
                            { id: 'top', label: 'Top' },
                            { id: 'bottom', label: 'Bottom' },
                            { id: 'inline', label: 'Inline' }
                        ]
                    },
                    {
                        type: 'select',
                        name: 'direction',
                        label: 'Layout Direction',
                        changeProp: true,
                        options: [
                            { id: 'horizontal', label: 'Horizontal' },
                            { id: 'vertical', label: 'Vertical' }
                        ]
                    },
                    {
                        type: 'checkbox',
                        name: 'sticky',
                        label: 'Sticky Positioning',
                        changeProp: true,
                        valueTrue: 'true',
                        valueFalse: 'false'
                    },
                    {
                        type: 'checkbox',
                        name: 'responsive',
                        label: 'Stack on Mobile',
                        changeProp: true,
                        valueTrue: 'true',
                        valueFalse: 'false'
                    }
                ],
                // Default property values
                placement: 'inline',
                direction: 'horizontal',
                sticky: false,
                responsive: true
            },
            
            // Initialize trait behavior
            init() {
                // Listen to trait changes (properties since changeProp: true)
                this.on('change:placement', this.handlePlacementChange);
                this.on('change:sticky', this.handleStickyChange);
                this.on('change:direction', this.handleDirectionChange);
                this.on('change:responsive', this.handleResponsiveChange);
                
                // Apply initial state
                this.handlePlacementChange();
                this.handleDirectionChange();
                this.handleResponsiveChange();
            },
            
            // Handle placement changes (top/bottom/inline)
            handlePlacementChange() {
                const placement = this.get('placement') || 'inline';
                const sticky = this.get('sticky');
                
                if (placement === 'top' && sticky) {
                    this.setStyle({ position: 'sticky', top: '0', bottom: 'auto' });
                } else if (placement === 'bottom' && sticky) {
                    this.setStyle({ position: 'sticky', top: 'auto', bottom: '0' });
                } else {
                    this.setStyle({ position: 'static', top: 'auto', bottom: 'auto' });
                }
            },
            
            // Handle sticky positioning changes
            handleStickyChange() {
                const sticky = this.get('sticky');
                const placement = this.get('placement') || 'inline';
                
                if (sticky && (placement === 'top' || placement === 'bottom')) {
                    const pos = placement === 'bottom' ? 'bottom' : 'top';
                    this.setStyle({ position: 'sticky', [pos]: '0' });
                } else {
                    this.setStyle({ position: 'static', top: 'auto', bottom: 'auto' });
                }
            },
            
            // Handle layout direction changes (horizontal/vertical)
            handleDirectionChange() {
                const direction = this.get('direction') || 'horizontal';
                this.setStyle({ 
                    'flex-direction': direction === 'horizontal' ? 'row' : 'column' 
                });
            },
            
            // Handle responsive behavior (stack on mobile)
            handleResponsiveChange() {
                const responsive = this.get('responsive');
                if (responsive) {
                    this.addClass('atd-study-action-bar--responsive');
                } else {
                    this.removeClass('atd-study-action-bar--responsive');
                }
            }
        }
    });
}
