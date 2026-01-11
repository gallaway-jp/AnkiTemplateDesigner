/**
 * Overlay & Popup Component Blocks
 */

export function registerOverlayBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Overlays & Popups';
    
    // Modal
    bm.add('modal', {
        label: 'Modal',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-modal-overlay'],
            style: {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                background: 'rgba(0, 0, 0, 0.5)',
                display: 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                'z-index': '1000'
            },
            components: [
                {
                    tagName: 'div',
                    classes: ['atd-modal'],
                    style: {
                        'min-width': '300px',
                        'max-width': '90%',
                        padding: '24px',
                        background: '#ffffff',
                        'border-radius': '12px',
                        'box-shadow': '0 10px 40px rgba(0,0,0,0.2)'
                    },
                    components: [
                        { tagName: 'h3', content: 'Modal Title', style: { margin: '0 0 16px' } },
                        { tagName: 'p', content: 'Modal content goes here.', style: { margin: '0 0 20px' } },
                        { tagName: 'button', content: 'Close', style: { padding: '10px 20px', background: '#1976d2', color: '#fff', border: 'none', 'border-radius': '6px', cursor: 'pointer' } }
                    ]
                }
            ]
        }
    });
    
    // Drawer / Side Panel
    bm.add('drawer-overlay', {
        label: 'Drawer Overlay',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-drawer-overlay'],
            style: {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                background: 'rgba(0, 0, 0, 0.3)',
                'z-index': '999'
            },
            components: [
                {
                    tagName: 'aside',
                    classes: ['atd-drawer-panel'],
                    style: {
                        position: 'fixed',
                        top: '0',
                        right: '0',
                        width: '300px',
                        height: '100%',
                        padding: '24px',
                        background: '#ffffff',
                        'box-shadow': '-4px 0 12px rgba(0,0,0,0.15)',
                        'z-index': '1000'
                    },
                    components: [
                        { tagName: 'h3', content: 'Drawer Title' },
                        { tagName: 'p', content: 'Drawer content' }
                    ]
                }
            ]
        }
    });
    
    // Popover
    bm.add('popover', {
        label: 'Popover',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-popover-container'],
            style: { position: 'relative', display: 'inline-block' },
            components: [
                { tagName: 'button', content: 'Click me', style: { padding: '8px 16px' } },
                {
                    tagName: 'div',
                    classes: ['atd-popover'],
                    style: {
                        position: 'absolute',
                        top: '100%',
                        left: '0',
                        'margin-top': '8px',
                        padding: '12px 16px',
                        background: '#ffffff',
                        border: '1px solid #e0e0e0',
                        'border-radius': '8px',
                        'box-shadow': '0 4px 12px rgba(0,0,0,0.15)',
                        'z-index': '100',
                        display: 'none'
                    },
                    components: [
                        { tagName: 'p', content: 'Popover content', style: { margin: '0' } }
                    ]
                }
            ]
        }
    });
    
    // Dropdown Menu
    bm.add('dropdown-menu', {
        label: 'Dropdown Menu',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-dropdown'],
            style: { position: 'relative', display: 'inline-block' },
            components: [
                { tagName: 'button', content: 'Menu ▼', style: { padding: '8px 16px', cursor: 'pointer' } },
                {
                    tagName: 'div',
                    classes: ['atd-dropdown-menu'],
                    style: {
                        display: 'none',
                        position: 'absolute',
                        top: '100%',
                        left: '0',
                        'margin-top': '4px',
                        'min-width': '160px',
                        background: '#ffffff',
                        border: '1px solid #e0e0e0',
                        'border-radius': '6px',
                        'box-shadow': '0 4px 12px rgba(0,0,0,0.1)',
                        'z-index': '100'
                    },
                    components: [
                        { tagName: 'a', content: 'Option 1', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#424242', 'text-decoration': 'none' } },
                        { tagName: 'a', content: 'Option 2', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#424242', 'text-decoration': 'none' } },
                        { tagName: 'a', content: 'Option 3', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#424242', 'text-decoration': 'none' } }
                    ]
                }
            ]
        }
    });
    
    // Bottom Sheet
    bm.add('bottom-sheet', {
        label: 'Bottom Sheet',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-bottom-sheet-overlay'],
            style: {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                background: 'rgba(0, 0, 0, 0.3)',
                display: 'flex',
                'align-items': 'flex-end',
                'z-index': '1000'
            },
            components: [
                {
                    tagName: 'div',
                    classes: ['atd-bottom-sheet'],
                    style: {
                        width: '100%',
                        'max-height': '80%',
                        padding: '24px',
                        background: '#ffffff',
                        'border-radius': '20px 20px 0 0',
                        'box-shadow': '0 -4px 12px rgba(0,0,0,0.1)'
                    },
                    components: [
                        { tagName: 'h3', content: 'Bottom Sheet Title' },
                        { tagName: 'p', content: 'Content here' }
                    ]
                }
            ]
        }
    });
    
    // Lightbox
    bm.add('lightbox', {
        label: 'Lightbox',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-lightbox-overlay'],
            style: {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                background: 'rgba(0, 0, 0, 0.9)',
                display: 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                'z-index': '1000'
            },
            components: [
                {
                    tagName: 'img',
                    classes: ['atd-lightbox-image'],
                    attributes: { src: 'https://via.placeholder.com/800x600', alt: 'Lightbox image' },
                    style: { 'max-width': '90%', 'max-height': '90%', 'border-radius': '8px' }
                }
            ]
        }
    });
}
