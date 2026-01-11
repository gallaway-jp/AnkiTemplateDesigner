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
            type: 'card',
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
    
    // ========== GRID LAYOUTS ==========
    
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
    
    // 2-Column Row
    bm.add('row-2-col', {
        label: '2 Columns',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-row'],
            style: {
                display: 'grid',
                'grid-template-columns': '1fr 1fr',
                gap: '16px'
            },
            components: [
                { tagName: 'div', classes: ['atd-col'], style: { padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Column 1' }] },
                { tagName: 'div', classes: ['atd-col'], style: { padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Column 2' }] }
            ]
        }
    });
    
    // 3-Column Row
    bm.add('row-3-col', {
        label: '3 Columns',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-row'],
            style: {
                display: 'grid',
                'grid-template-columns': '1fr 1fr 1fr',
                gap: '16px'
            },
            components: [
                { tagName: 'div', classes: ['atd-col'], style: { padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Column 1' }] },
                { tagName: 'div', classes: ['atd-col'], style: { padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Column 2' }] },
                { tagName: 'div', classes: ['atd-col'], style: { padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Column 3' }] }
            ]
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
                { tagName: 'div', style: { 'break-inside': 'avoid', 'margin-bottom': '16px', padding: '16px', background: '#f0f0f0' }, components: [{ type: 'text', content: 'Item 2' }] }
            ]
        }
    });
    
    // ========== FLEXBOX LAYOUTS ==========
    
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
    
    // ========== NAVIGATION HELPERS ==========
    
    // Tabs Navigation
    bm.add('tabs-nav', {
        label: 'Tabs',
        category,
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
    
    // Stepper
    bm.add('stepper', {
        label: 'Stepper',
        category,
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
    
    // Anchor Link
    bm.add('anchor-link', {
        label: 'Anchor Link',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-anchor-link'],
            content: 'Jump to section',
            attributes: { href: '#section-id' },
            style: { color: '#1976d2', 'text-decoration': 'none' }
        }
    });
}
