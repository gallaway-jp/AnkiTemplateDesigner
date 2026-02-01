/**
 * Layout & Structure Blocks
 * Containers, spacing, grid, and flexbox components
 * 
 * Updated Feb 1, 2026: Removed 9 unsuitable blocks (modal, drawer, split-view, 
 * accordion, tabs, stepper, masonry, frame). Added container. Now 16 blocks.
 * Also imports and registers 6 Anki-specific template syntax blocks.
 */

import { registerAnkiBlocks } from './anki-blocks.js';

export function registerLayoutBlocks(editor) {
    const bm = editor.BlockManager;
    
    // Register Anki-specific blocks
    registerAnkiBlocks(editor);
    
    // ========== LAYOUT & STRUCTURE CONTAINERS ==========
    
    // Section
    bm.add('section', {
        label: 'Section',
        category: 'Layout & Structure',
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
    
    bm.add('panel', {
        label: 'Panel',
        category: 'Layout & Structure',
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
    
    bm.add('card', {
        label: 'Card',
        category: 'Layout & Structure',
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
    
    bm.add('surface', {
        label: 'Surface',
        category: 'Layout & Structure',
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
    
    // Container (centered, max-width wrapper)
    bm.add('container', {
        label: 'Container',
        category: 'Layout & Structure',
        content: {
            tagName: 'div',
            classes: ['atd-container'],
            style: {
                maxWidth: '800px',
                margin: '0 auto',
                padding: '0 16px'
            },
            components: [
                { type: 'text', content: 'Container content' }
            ]
        }
    });
    
    // ========== GRID LAYOUTS ==========
    
    // Grid
    bm.add('grid', {
        label: 'Grid',
        category: 'Grid & Columns',
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
        category: 'Grid & Columns',
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
        category: 'Grid & Columns',
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
    
    // Flow Layout (auto-wrapping grid)
    bm.add('flow-layout', {
        label: 'Flow Layout',
        category: 'Grid & Columns',
        content: {
            tagName: 'div',
            classes: ['atd-flow'],
            style: {
                display: 'flex',
                'flex-wrap': 'wrap',
                gap: '16px'
            },
            components: []
        }
    });
    
    // ========== FLEXBOX LAYOUTS ==========
    
    // Horizontal Stack
    bm.add('h-stack', {
        label: 'H-Stack',
        category: 'Flexbox',
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
        category: 'Flexbox',
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
    
    
    // Center (flex center)
    bm.add('center', {
        label: 'Center',
        category: 'Flexbox',
        content: {
            tagName: 'div',
            classes: ['atd-spacer'],
            style: {
                height: '24px',
                width: '100%'
            }
        }
    });
    
    
    // ========== SPACING & DIVIDERS ==========
    
    // Spacer
    bm.add('spacer', {
        label: 'Spacer',
        category: 'Spacing',
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
        category: 'Spacing',
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
        category: 'Spacing',
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
        category: 'Flexbox',
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
    
    // Anchor Link
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
}
