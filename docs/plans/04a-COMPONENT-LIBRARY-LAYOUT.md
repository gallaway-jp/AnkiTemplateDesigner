# 04a - Component Library: Layout & Navigation Blocks

> **Purpose**: Define GrapeJS blocks for Layout, Structure, and Navigation components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

This document defines the first set of GrapeJS blocks covering:
- **Layout & Structure Elements** (22 components)
- **Navigation Components** (15 components)

Each block includes HTML template, default styles, traits (properties), and Anki-specific attributes.

---

## Block Registration Pattern

### `web/blocks/index.js`

```javascript
/**
 * Register all Anki Template Designer blocks
 */
(function() {
    // Wait for GrapeJS to be available
    if (typeof grapesjs === 'undefined') {
        console.error('GrapeJS not loaded');
        return;
    }
    
    // Block category configuration
    const categories = {
        layout: { label: 'Layout & Structure', order: 1, open: true },
        navigation: { label: 'Navigation', order: 2, open: false },
        inputs: { label: 'Inputs & Forms', order: 3, open: false },
        buttons: { label: 'Buttons & Actions', order: 4, open: false },
        data: { label: 'Data Display', order: 5, open: false },
        feedback: { label: 'Feedback & Status', order: 6, open: false },
        overlays: { label: 'Overlays & Popups', order: 7, open: false },
        search: { label: 'Search & Filter', order: 8, open: false },
        commerce: { label: 'Commerce', order: 9, open: false },
        social: { label: 'Social', order: 10, open: false },
        charts: { label: 'Charts', order: 11, open: false },
        accessibility: { label: 'Accessibility', order: 12, open: false },
        system: { label: 'System & Meta', order: 13, open: false },
        motion: { label: 'Motion & Interaction', order: 14, open: false },
        advanced: { label: 'Advanced', order: 15, open: false },
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

## 2. Navigation Components

### `web/blocks/navigation.js`

```javascript
/**
 * Navigation Component Blocks
 */

export function registerNavigationBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Navigation';
    
    // Top Navigation Bar
    bm.add('top-nav', {
        label: 'Top Nav Bar',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-top-nav'],
            style: {
                display: 'flex',
                'justify-content': 'space-between',
                'align-items': 'center',
                padding: '12px 20px',
                background: '#1976d2',
                color: '#ffffff'
            },
            components: [
                { tagName: 'div', classes: ['atd-nav-brand'], components: [{ type: 'text', content: 'Brand' }] },
                {
                    tagName: 'div',
                    classes: ['atd-nav-links'],
                    style: { display: 'flex', gap: '20px' },
                    components: [
                        { tagName: 'a', content: 'Home', attributes: { href: '#' }, style: { color: '#fff', 'text-decoration': 'none' } },
                        { tagName: 'a', content: 'About', attributes: { href: '#' }, style: { color: '#fff', 'text-decoration': 'none' } },
                        { tagName: 'a', content: 'Contact', attributes: { href: '#' }, style: { color: '#fff', 'text-decoration': 'none' } }
                    ]
                }
            ]
        }
    });
    
    // Bottom Navigation Bar
    bm.add('bottom-nav', {
        label: 'Bottom Nav Bar',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-bottom-nav'],
            style: {
                display: 'flex',
                'justify-content': 'space-around',
                'align-items': 'center',
                padding: '8px 0',
                background: '#ffffff',
                'border-top': '1px solid #e0e0e0',
                position: 'fixed',
                bottom: '0',
                left: '0',
                right: '0'
            },
            components: [
                { tagName: 'button', classes: ['atd-nav-item'], style: { border: 'none', background: 'none', padding: '8px 16px', 'text-align': 'center' }, components: [{ tagName: 'span', content: '🏠' }, { tagName: 'div', content: 'Home', style: { 'font-size': '12px' } }] },
                { tagName: 'button', classes: ['atd-nav-item'], style: { border: 'none', background: 'none', padding: '8px 16px', 'text-align': 'center' }, components: [{ tagName: 'span', content: '🔍' }, { tagName: 'div', content: 'Search', style: { 'font-size': '12px' } }] },
                { tagName: 'button', classes: ['atd-nav-item'], style: { border: 'none', background: 'none', padding: '8px 16px', 'text-align': 'center' }, components: [{ tagName: 'span', content: '👤' }, { tagName: 'div', content: 'Profile', style: { 'font-size': '12px' } }] }
            ]
        }
    });
    
    // Sidebar Navigation
    bm.add('sidebar-nav', {
        label: 'Sidebar Nav',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-sidebar-nav'],
            style: {
                width: '240px',
                padding: '16px 0',
                background: '#f5f5f5'
            },
            components: [
                { tagName: 'a', classes: ['atd-sidebar-item', 'active'], content: '📊 Dashboard', attributes: { href: '#' }, style: { display: 'block', padding: '12px 20px', 'text-decoration': 'none', color: '#333', background: '#e3f2fd' } },
                { tagName: 'a', classes: ['atd-sidebar-item'], content: '📁 Projects', attributes: { href: '#' }, style: { display: 'block', padding: '12px 20px', 'text-decoration': 'none', color: '#333' } },
                { tagName: 'a', classes: ['atd-sidebar-item'], content: '⚙️ Settings', attributes: { href: '#' }, style: { display: 'block', padding: '12px 20px', 'text-decoration': 'none', color: '#333' } }
            ]
        }
    });
    
    // Breadcrumbs
    bm.add('breadcrumbs', {
        label: 'Breadcrumbs',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-breadcrumbs'],
            attributes: { 'aria-label': 'Breadcrumb' },
            style: {
                padding: '8px 0',
                'font-size': '14px'
            },
            components: [
                {
                    tagName: 'ol',
                    style: { display: 'flex', 'list-style': 'none', padding: '0', margin: '0', gap: '8px' },
                    components: [
                        { tagName: 'li', components: [{ tagName: 'a', content: 'Home', attributes: { href: '#' }, style: { color: '#1976d2' } }] },
                        { tagName: 'li', content: '/', style: { color: '#999' } },
                        { tagName: 'li', components: [{ tagName: 'a', content: 'Category', attributes: { href: '#' }, style: { color: '#1976d2' } }] },
                        { tagName: 'li', content: '/', style: { color: '#999' } },
                        { tagName: 'li', content: 'Current Page', style: { color: '#666' } }
                    ]
                }
            ]
        }
    });
    
    // Tabs Navigation
    bm.add('tabs-nav', {
        label: 'Tabs',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-tabs-nav'],
            style: {
                display: 'flex',
                'border-bottom': '2px solid #e0e0e0'
            },
            components: [
                { tagName: 'button', content: 'Tab 1', classes: ['atd-tab', 'active'], style: { padding: '12px 24px', border: 'none', background: 'transparent', 'border-bottom': '2px solid #1976d2', 'margin-bottom': '-2px', cursor: 'pointer' } },
                { tagName: 'button', content: 'Tab 2', classes: ['atd-tab'], style: { padding: '12px 24px', border: 'none', background: 'transparent', cursor: 'pointer' } },
                { tagName: 'button', content: 'Tab 3', classes: ['atd-tab'], style: { padding: '12px 24px', border: 'none', background: 'transparent', cursor: 'pointer' } }
            ]
        }
    });
    
    // Stepper / Wizard
    bm.add('stepper', {
        label: 'Stepper',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stepper'],
            style: {
                display: 'flex',
                'justify-content': 'space-between',
                'align-items': 'center',
                padding: '20px'
            },
            components: [
                { tagName: 'div', classes: ['atd-step', 'completed'], style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '✓', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#4caf50', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', margin: '0 auto 8px' } }, { tagName: 'span', content: 'Step 1' }] },
                { tagName: 'div', classes: ['atd-step-line'], style: { flex: '1', height: '2px', background: '#4caf50', margin: '0 8px' } },
                { tagName: 'div', classes: ['atd-step', 'active'], style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '2', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', margin: '0 auto 8px' } }, { tagName: 'span', content: 'Step 2' }] },
                { tagName: 'div', classes: ['atd-step-line'], style: { flex: '1', height: '2px', background: '#e0e0e0', margin: '0 8px' } },
                { tagName: 'div', classes: ['atd-step'], style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '3', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#e0e0e0', color: '#666', display: 'flex', 'align-items': 'center', 'justify-content': 'center', margin: '0 auto 8px' } }, { tagName: 'span', content: 'Step 3' }] }
            ]
        }
    });
    
    // Pagination
    bm.add('pagination', {
        label: 'Pagination',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-pagination'],
            style: {
                display: 'flex',
                gap: '4px',
                'justify-content': 'center'
            },
            components: [
                { tagName: 'button', content: '←', style: { padding: '8px 12px', border: '1px solid #e0e0e0', background: '#fff', 'border-radius': '4px', cursor: 'pointer' } },
                { tagName: 'button', content: '1', style: { padding: '8px 12px', border: '1px solid #1976d2', background: '#1976d2', color: '#fff', 'border-radius': '4px', cursor: 'pointer' } },
                { tagName: 'button', content: '2', style: { padding: '8px 12px', border: '1px solid #e0e0e0', background: '#fff', 'border-radius': '4px', cursor: 'pointer' } },
                { tagName: 'button', content: '3', style: { padding: '8px 12px', border: '1px solid #e0e0e0', background: '#fff', 'border-radius': '4px', cursor: 'pointer' } },
                { tagName: 'button', content: '→', style: { padding: '8px 12px', border: '1px solid #e0e0e0', background: '#fff', 'border-radius': '4px', cursor: 'pointer' } }
            ]
        }
    });
    
    // Back Button
    bm.add('back-button', {
        label: 'Back Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-back-button'],
            style: {
                display: 'flex',
                'align-items': 'center',
                gap: '8px',
                padding: '8px 16px',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                'font-size': '16px'
            },
            components: [
                { tagName: 'span', content: '←' },
                { tagName: 'span', content: 'Back' }
            ]
        }
    });
    
    // Hamburger Menu
    bm.add('hamburger-menu', {
        label: 'Hamburger Menu',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-hamburger'],
            attributes: { 'aria-label': 'Menu' },
            style: {
                display: 'flex',
                'flex-direction': 'column',
                gap: '4px',
                padding: '8px',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer'
            },
            components: [
                { tagName: 'span', style: { width: '24px', height: '3px', background: '#333', 'border-radius': '2px' } },
                { tagName: 'span', style: { width: '24px', height: '3px', background: '#333', 'border-radius': '2px' } },
                { tagName: 'span', style: { width: '24px', height: '3px', background: '#333', 'border-radius': '2px' } }
            ]
        }
    });
    
    // Overflow Menu
    bm.add('overflow-menu', {
        label: 'Overflow Menu',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-overflow-menu'],
            attributes: { 'aria-label': 'More options' },
            content: '⋮',
            style: {
                padding: '8px 12px',
                border: 'none',
                background: 'transparent',
                'font-size': '20px',
                cursor: 'pointer'
            }
        }
    });
    
    // Tree Navigation
    bm.add('tree-nav', {
        label: 'Tree Navigation',
        category,
        content: {
            tagName: 'ul',
            classes: ['atd-tree-nav'],
            style: {
                'list-style': 'none',
                padding: '0',
                margin: '0'
            },
            components: [
                {
                    tagName: 'li',
                    classes: ['atd-tree-item'],
                    components: [
                        { tagName: 'details', attributes: { open: true }, components: [
                            { tagName: 'summary', content: '📁 Parent Item', style: { padding: '8px', cursor: 'pointer' } },
                            { tagName: 'ul', style: { 'padding-left': '20px', 'list-style': 'none' }, components: [
                                { tagName: 'li', content: '📄 Child Item 1', style: { padding: '8px' } },
                                { tagName: 'li', content: '📄 Child Item 2', style: { padding: '8px' } }
                            ]}
                        ]}
                    ]
                }
            ]
        }
    });
    
    // Anchor Links
    bm.add('anchor-link', {
        label: 'Anchor Link',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-anchor-link'],
            content: 'Jump to section',
            attributes: { href: '#section-id' },
            style: {
                color: '#1976d2',
                'text-decoration': 'none'
            }
        }
    });
    
    // Floating Navigation
    bm.add('floating-nav', {
        label: 'Floating Nav',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-floating-nav'],
            style: {
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                display: 'flex',
                'flex-direction': 'column',
                gap: '8px'
            },
            components: [
                { tagName: 'button', content: '↑', style: { width: '48px', height: '48px', 'border-radius': '50%', border: 'none', background: '#1976d2', color: '#fff', cursor: 'pointer', 'font-size': '20px' } }
            ]
        }
    });
    
    // Navigation Rail
    bm.add('nav-rail', {
        label: 'Navigation Rail',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-nav-rail'],
            style: {
                width: '72px',
                padding: '8px 0',
                background: '#f5f5f5',
                display: 'flex',
                'flex-direction': 'column',
                'align-items': 'center',
                gap: '4px'
            },
            components: [
                { tagName: 'button', classes: ['atd-rail-item'], style: { width: '56px', height: '56px', border: 'none', background: 'transparent', 'border-radius': '16px', cursor: 'pointer', display: 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', gap: '4px' }, components: [{ tagName: 'span', content: '🏠', style: { 'font-size': '20px' } }, { tagName: 'span', content: 'Home', style: { 'font-size': '10px' } }] },
                { tagName: 'button', classes: ['atd-rail-item'], style: { width: '56px', height: '56px', border: 'none', background: 'transparent', 'border-radius': '16px', cursor: 'pointer', display: 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', gap: '4px' }, components: [{ tagName: 'span', content: '⚙️', style: { 'font-size': '20px' } }, { tagName: 'span', content: 'Settings', style: { 'font-size': '10px' } }] }
            ]
        }
    });
}
```

---

## Component Traits (Properties)

### Layout Component Traits

```javascript
// Register traits for layout components
editor.DomComponents.addType('frame', {
    model: {
        defaults: {
            traits: [
                { type: 'text', name: 'id', label: 'ID' },
                { type: 'select', name: 'device', label: 'Device', options: [
                    { id: 'mobile', name: 'Mobile (375x667)' },
                    { id: 'tablet', name: 'Tablet (768x1024)' },
                    { id: 'desktop', name: 'Desktop (1920x1080)' }
                ]},
                { type: 'color', name: 'background', label: 'Background' }
            ]
        }
    }
});

// Card traits
editor.DomComponents.addType('card', {
    model: {
        defaults: {
            traits: [
                { type: 'text', name: 'id', label: 'ID' },
                { type: 'select', name: 'elevation', label: 'Elevation', options: [
                    { id: '1', name: 'Low' },
                    { id: '2', name: 'Medium' },
                    { id: '3', name: 'High' }
                ]},
                { type: 'checkbox', name: 'clickable', label: 'Clickable' }
            ]
        }
    }
});
```

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
