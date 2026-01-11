# 04a - Component Library: Layout & Navigation Blocks

> **Purpose**: Define GrapeJS blocks for Layout, Structure, and Study Action Bar components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026
> **Updated**: Based on COMPONENT-AUDIT.md - removed generic navigation, added study-action-bar

---

## Overview

This document defines the first set of GrapeJS blocks covering:
- **Layout & Structure Elements** (25 components)
- **Study Action Bar** (1 specialized component for review sessions)

Each block includes HTML template, default styles, traits (properties), and Anki-specific attributes.

---

## Component Type Registration (Required First)

### Component Registration Order

**CRITICAL**: GrapeJS checks component types in **REVERSE registration order**.
- Register generic/base components FIRST
- Register specific/custom components LAST (checked first)

### `web/components/index.js`

```javascript
/**
 * Register all custom component types
 * MUST be called before block registration
 */
export function registerComponentTypes(editor) {
    // Register in order: generic first, specific last
    // (GrapeJS checks in reverse order)
    
    // 1. Base layout components (generic)
    registerBaseComponents(editor);
    
    // 2. Anki-specific components (checked first)
    registerStudyActionBarComponent(editor);
}

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
                    { type: 'select', name: 'device', label: 'Device', options: [
                        { id: 'mobile', label: 'Mobile (375x667)' },
                        { id: 'tablet', label: 'Tablet (768x1024)' },
                        { id: 'desktop', label: 'Desktop (1920x1080)' }
                    ]},
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
                    { type: 'select', name: 'elevation', label: 'Elevation', options: [
                        { id: '1', label: 'Low' },
                        { id: '2', label: 'Medium' },
                        { id: '3', label: 'High' }
                    ]},
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
```

**CSS for Responsive Behavior**:

```css
/* Add to generated styles */
@media (max-width: 768px) {
    .atd-study-action-bar--responsive {
        flex-direction: column !important;
        align-items: stretch;
    }
    
    .atd-study-action-bar--responsive button {
        width: 100%;
    }
}
```

---

## Block Registration Pattern

### `web/blocks/index.js`

```javascript
/**
 * Register all Anki Template Designer blocks
 * IMPORTANT: Must call registerComponentTypes() FIRST
 */
(function() {
    // Wait for GrapeJS to be available
    if (typeof grapesjs === 'undefined') {
        console.error('GrapeJS not loaded');
        return;
    }
    
    // Block category configuration
    const categories = {
        // Core content
        layout: { label: 'Layout & Structure', order: 1, open: true },
        typography: { label: 'Text & Typography', order: 2, open: true },
        
        // Data display
        data: { label: 'Data Display', order: 3, open: false },
        charts: { label: 'Charts (Advanced)', order: 4, open: false },
        
        // UI elements
        buttons: { label: 'Buttons', order: 5, open: false },
        inputs: { label: 'Inputs', order: 6, open: false },
        feedback: { label: 'Feedback & Status', order: 7, open: false },
        overlays: { label: 'Overlays & Popups', order: 8, open: false },
        
        // Enhanced functionality
        animations: { label: 'Animations', order: 9, open: false },
        accessibility: { label: 'Accessibility', order: 10, open: false },
        
        // Anki specific
        anki: { label: 'Anki Special', order: 0, open: true }
    };
    
    window.ankiBlockCategories = categories;
})();
```

---

## 1. Layout & Structure Elements

### `web/blocks/layout.js`

```javascript
/**
 * Layout & Structure Blocks
 * Containers, spacing, and alignment components
 */

export function registerLayoutBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Layout & Structure';
    
    // ========== CONTAINERS ==========
    
    // Frame / Artboard
    bm.add('frame', {
        label: 'Frame',
        category,
        attributes: { class: 'gjs-block-frame' },
        content: {
            type: 'frame',
            tagName: 'div',
            classes: ['atd-frame'],
            style: {
                width: '375px',
                height: '667px',
                margin: '0 auto',
                background: '#ffffff',
                'box-shadow': '0 4px 20px rgba(0,0,0,0.15)',
                overflow: 'hidden'
            },
            components: []
        }
    });
    
    // Section
    bm.add('section', {
        label: 'Section',
        category,
        attributes: { class: 'gjs-block-section' },
        content: {
            type: 'section',
            tagName: 'section',
            classes: ['atd-section'],
            style: {
                padding: '20px',
                'margin-bottom': '10px'
            },
            components: [
                { type: 'text', content: 'Section content' }
            ]
        }
    });
    
    // Panel
    bm.add('panel', {
        label: 'Panel',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-panel'],
            style: {
                padding: '16px',
                border: '1px solid #e0e0e0',
                'border-radius': '8px',
                background: '#ffffff'
            },
            components: [
                { type: 'text', content: 'Panel content' }
            ]
        }
    });
    
    // Card
    bm.add('card', {
        label: 'Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-card'],
            style: {
                padding: '16px',
                'border-radius': '12px',
                background: '#ffffff',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.1)'
            },
            components: [
                {
                    tagName: 'div',
                    classes: ['atd-card-header'],
                    components: [{ type: 'text', content: 'Card Title' }]
                },
                {
                    tagName: 'div', 
                    classes: ['atd-card-body'],
                    components: [{ type: 'text', content: 'Card content goes here' }]
                }
            ]
        }
    });
    
    // Surface
    bm.add('surface', {
        label: 'Surface',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-surface'],
            style: {
                padding: '12px',
                background: '#f5f5f5',
                'border-radius': '4px'
            },
            components: []
        }
    });
    
    // Modal Container
    bm.add('modal-container', {
        label: 'Modal Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-modal-container'],
            style: {
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                'min-width': '300px',
                'max-width': '90%',
                padding: '24px',
                background: '#ffffff',
                'border-radius': '12px',
                'box-shadow': '0 10px 40px rgba(0,0,0,0.2)',
                'z-index': '1000'
            },
            components: [
                { tagName: 'h3', content: 'Modal Title' },
                { tagName: 'p', content: 'Modal content' }
            ]
        }
    });
    
    // Drawer / Sidebar
    bm.add('drawer', {
        label: 'Drawer',
        category,
        content: {
            tagName: 'aside',
            classes: ['atd-drawer'],
            style: {
                width: '280px',
                height: '100%',
                padding: '16px',
                background: '#ffffff',
                'border-right': '1px solid #e0e0e0'
            },
            components: [
                { tagName: 'h4', content: 'Drawer Menu' }
            ]
        }
    });
    
    // Split View
    bm.add('split-view', {
        label: 'Split View',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-split-view'],
            style: {
                display: 'flex',
                gap: '1px',
                background: '#e0e0e0'
            },
            components: [
                {
                    tagName: 'div',
                    classes: ['atd-split-pane'],
                    style: { flex: '1', padding: '16px', background: '#fff' },
                    components: [{ type: 'text', content: 'Left pane' }]
                },
                {
                    tagName: 'div',
                    classes: ['atd-split-pane'],
                    style: { flex: '1', padding: '16px', background: '#fff' },
                    components: [{ type: 'text', content: 'Right pane' }]
                }
            ]
        }
    });
    
    // Accordion Container
    bm.add('accordion', {
        label: 'Accordion',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-accordion'],
            components: [
                {
                    tagName: 'details',
                    classes: ['atd-accordion-item'],
                    style: { 'border-bottom': '1px solid #e0e0e0' },
                    components: [
                        { tagName: 'summary', content: 'Section 1', style: { padding: '12px', cursor: 'pointer' } },
                        { tagName: 'div', content: 'Content 1', style: { padding: '12px' } }
                    ]
                },
                {
                    tagName: 'details',
                    classes: ['atd-accordion-item'],
                    components: [
                        { tagName: 'summary', content: 'Section 2', style: { padding: '12px', cursor: 'pointer' } },
                        { tagName: 'div', content: 'Content 2', style: { padding: '12px' } }
                    ]
                }
            ]
        }
    });
    
    // Tab Container
    bm.add('tab-container', {
        label: 'Tab Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-tabs'],
            components: [
                {
                    tagName: 'div',
                    classes: ['atd-tab-list'],
                    style: { display: 'flex', 'border-bottom': '2px solid #e0e0e0' },
                    components: [
                        { tagName: 'button', content: 'Tab 1', classes: ['atd-tab', 'active'], style: { padding: '12px 24px', border: 'none', background: 'transparent', 'border-bottom': '2px solid #1976d2', 'margin-bottom': '-2px' } },
                        { tagName: 'button', content: 'Tab 2', classes: ['atd-tab'], style: { padding: '12px 24px', border: 'none', background: 'transparent' } }
                    ]
                },
                {
                    tagName: 'div',
                    classes: ['atd-tab-panel'],
                    style: { padding: '16px' },
                    components: [{ type: 'text', content: 'Tab content' }]
                }
            ]
        }
    });
    
    // Grid
    bm.add('grid', {
        label: 'Grid',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-grid'],
            style: {
                display: 'grid',
                'grid-template-columns': 'repeat(3, 1fr)',
                gap: '16px'
            },
            components: [
                { tagName: 'div', classes: ['atd-grid-item'], style: { padding: '16px', background: '#f0f0f0', 'border-radius': '4px' }, components: [{ type: 'text', content: 'Item 1' }] },
                { tagName: 'div', classes: ['atd-grid-item'], style: { padding: '16px', background: '#f0f0f0', 'border-radius': '4px' }, components: [{ type: 'text', content: 'Item 2' }] },
                { tagName: 'div', classes: ['atd-grid-item'], style: { padding: '16px', background: '#f0f0f0', 'border-radius': '4px' }, components: [{ type: 'text', content: 'Item 3' }] }
            ]
        }
    });
    
    // Horizontal Stack
    bm.add('h-stack', {
        label: 'H-Stack',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-hstack'],
            style: {
                display: 'flex',
                'flex-direction': 'row',
                gap: '8px',
                'align-items': 'center'
            },
            components: []
        }
    });
    
    // Vertical Stack
    bm.add('v-stack', {
        label: 'V-Stack',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-vstack'],
            style: {
                display: 'flex',
                'flex-direction': 'column',
                gap: '8px'
            },
            components: []
        }
    });
    
    // Flow Layout
    bm.add('flow-layout', {
        label: 'Flow Layout',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-flow'],
            style: {
                display: 'flex',
                'flex-wrap': 'wrap',
                gap: '8px'
            },
            components: []
        }
    });
    
    // Masonry Layout
    bm.add('masonry', {
        label: 'Masonry',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-masonry'],
            style: {
                'column-count': '3',
                'column-gap': '16px'
            },
            components: [
                { tagName: 'div', style: { 'break-inside': 'avoid', 'margin-bottom': '16px', padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Item 1' }] },
                { tagName: 'div', style: { 'break-inside': 'avoid', 'margin-bottom': '16px', padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Item 2 with more content' }] }
            ]
        }
    });
    
    // ========== SPACING & ALIGNMENT ==========
    
    // Spacer
    bm.add('spacer', {
        label: 'Spacer',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-spacer'],
            style: {
                height: '24px',
                width: '100%'
            }
        }
    });
    
    // Divider
    bm.add('divider', {
        label: 'Divider',
        category,
        content: {
            tagName: 'hr',
            classes: ['atd-divider'],
            style: {
                border: 'none',
                'border-top': '1px solid #e0e0e0',
                margin: '16px 0'
            }
        }
    });
    
    // Padding Wrapper
    bm.add('padding-wrapper', {
        label: 'Padding Box',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-padding-wrapper'],
            style: {
                padding: '16px'
            },
            components: []
        }
    });
    
    // Margin Wrapper
    bm.add('margin-wrapper', {
        label: 'Margin Box',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-margin-wrapper'],
            style: {
                margin: '16px'
            },
            components: []
        }
    });
    
    // Center Container
    bm.add('center', {
        label: 'Center',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-center'],
            style: {
                display: 'flex',
                'justify-content': 'center',
                'align-items': 'center'
            },
            components: []
        }
    });
}
```

---

## 2. Study Action Bar Component

### `web/blocks/study-action-bar.js`

```javascript
/**
 * Study Action Bar Component
 * Specialized toolbar for Anki review session controls
 */

export function registerStudyActionBar(editor) {
    const bm = editor.BlockManager;
    const category = 'Anki Special';
    
    // Study Action Bar - Flexible control bar for review sessions
    // NOTE: Component type must be registered first via registerStudyActionBarComponent()
    bm.add('study-action-bar', {
        label: 'Study Action Bar',
        category,
        content: {
            type: 'study-action-bar', // Uses custom component type defined above
            components: [
                {
                    tagName: 'button',
                    content: 'Show Answer',
                    classes: ['study-btn'],
                    attributes: { 'data-action': 'showAnswer' },
                    style: { padding: '8px 16px', background: '#1976d2', color: '#fff', border: 'none', 'border-radius': '4px', cursor: 'pointer' }
                },
                {
                    tagName: 'button',
                    content: 'Play Audio',
                    classes: ['study-btn'],
                    attributes: { 'data-action': 'playAudio' },
                    style: { padding: '8px 16px', background: '#757575', color: '#fff', border: 'none', 'border-radius': '4px', cursor: 'pointer' }
                }
            ]
            // Traits are inherited from component type definition
        }
    });
}
```

**Use Cases**:
- Custom action buttons (linked via AnkiJSApi behaviors)
- Audio playback controls
- Study helpers (timer, hint reveal, card flags)
- Card rating/review buttons
- Note-taking shortcuts
- Field-specific actions

---

## Navigation Helper Components

Remaining navigation components that support card flow:

### Tabs Component
Useful for showing multiple sections (e.g., Front/Back, Definition/Example):

```javascript
bm.add('tabs-nav', {
    label: 'Tabs',
    category: 'Layout & Structure',
    content: {
        tagName: 'div',
        classes: ['atd-tabs-nav'],
        style: { display: 'flex', 'border-bottom': '2px solid #e0e0e0' },
        components: [
            { tagName: 'button', content: 'Tab 1', classes: ['atd-tab', 'active'], style: { padding: '12px 24px', border: 'none', background: 'transparent', 'border-bottom': '2px solid #1976d2', 'margin-bottom': '-2px', cursor: 'pointer' } },
            { tagName: 'button', content: 'Tab 2', classes: ['atd-tab'], style: { padding: '12px 24px', border: 'none', background: 'transparent', cursor: 'pointer' } }
        ]
    }
});
```

### Stepper Component
Useful for showing progress or step-by-step information:

```javascript
bm.add('stepper', {
    label: 'Stepper',
    category: 'Layout & Structure',
    content: {
        tagName: 'div',
        classes: ['atd-stepper'],
        style: { display: 'flex', 'justify-content': 'space-between', 'align-items': 'center', padding: '20px' },
        components: [
            { tagName: 'div', classes: ['atd-step', 'completed'], style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '✓', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#4caf50', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', margin: '0 auto 8px' } }, { tagName: 'span', content: 'Step 1' }] },
            { tagName: 'div', classes: ['atd-step-line'], style: { flex: '1', height: '2px', background: '#4caf50', margin: '0 8px' } },
            { tagName: 'div', classes: ['atd-step', 'active'], style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '2', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', margin: '0 auto 8px' } }, { tagName: 'span', content: 'Step 2' }] }
        ]
    }
});
```

### Anchor Link Component
Useful for internal navigation within long card content:

```javascript
bm.add('anchor-link', {
    label: 'Anchor Link',
    category: 'Layout & Structure',
    content: {
        tagName: 'a',
        classes: ['atd-anchor-link'],
        content: 'Jump to section',
        attributes: { href: '#section-id' },
        style: { color: '#1976d2', 'text-decoration': 'none' }
    }
});
```

---

## Removed Components

The following generic navigation components are not applicable to Anki templates:
- top-nav, bottom-nav (app navigation, not card-specific)
- sidebar-nav (no sidebar space in card templates)
- breadcrumbs (no hierarchical navigation in cards)
- pagination (no multi-page cards in Anki)
- back-button (Anki has built-in navigation)
- hamburger-menu (no app-style menus needed)
- overflow-menu (no action overflow menus)
- tree-nav (complex navigation not useful in cards)
- floating-nav (floating UI not appropriate for study)
- nav-rail (sidebar navigation not applicable)

---

## Component Traits (Properties)

**Note**: Component traits are now defined in the component type registration section above.

See `registerBaseComponents()` and `registerStudyActionBarComponent()` for trait definitions.

**Key Trait Concepts**:
- `changeProp: true` - Binds trait to component property instead of attribute
- `options` array for select traits uses `{ id: 'value', label: 'Display' }` format
- `valueTrue`/`valueFalse` for checkbox traits
- Trait changes trigger component listeners via `change:propertyName` events

---

## Anki-Specific Block

### Anki Field Placeholder Block

```javascript
// Special block for Anki field placeholder
bm.add('anki-field', {
    label: 'Anki Field',
    category: 'Anki Special',
    content: {
        tagName: 'span',
        classes: ['anki-field-placeholder'],
        content: '{{Field}}',
        attributes: {
            'data-anki-field': 'Field'
        },
        style: {
            display: 'inline-block',
            padding: '4px 8px',
            background: 'rgba(77, 171, 247, 0.2)',
            border: '1px dashed #4dabf7',
            'border-radius': '4px',
            'font-family': 'monospace'
        }
    }
});
```

---

## Next Document

See [04b-COMPONENT-LIBRARY-INPUTS.md](04b-COMPONENT-LIBRARY-INPUTS.md) for Input, Form, and Button components.
