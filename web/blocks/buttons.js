/**
 * Button & Action Component Blocks (Consolidated)
 */

export function registerButtonBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Buttons & Actions';
    
    // Primary Button (Primary action, Answer reveal, etc.)
    bm.add('primary-button', {
        label: 'Primary Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-primary'],
            content: 'Primary Action',
            style: {
                padding: '12px 24px',
                background: '#1976d2',
                color: '#ffffff',
                border: 'none',
                'border-radius': '6px',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer',
                transition: 'background 0.2s'
            }
        }
    });
    
    // Secondary Button (Secondary actions, Cancel, etc.)
    bm.add('secondary-button', {
        label: 'Secondary Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-secondary'],
            content: 'Secondary Action',
            style: {
                padding: '12px 24px',
                background: '#ffffff',
                color: '#1976d2',
                border: '1px solid #1976d2',
                'border-radius': '6px',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer',
                transition: 'background 0.2s'
            }
        }
    });
    
    // Icon Button (Compact button with icon)
    bm.add('icon-button', {
        label: 'Icon Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-icon'],
            content: '⭐',
            style: {
                width: '40px',
                height: '40px',
                padding: '0',
                background: '#f5f5f5',
                color: '#424242',
                border: 'none',
                'border-radius': '50%',
                'font-size': '20px',
                cursor: 'pointer',
                display: 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                transition: 'background 0.2s'
            }
        }
    });
    
    // Destructive Button (Delete, Suspend, etc.)
    bm.add('destructive-button', {
        label: 'Destructive Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-destructive'],
            content: 'Delete',
            style: {
                padding: '12px 24px',
                background: '#d32f2f',
                color: '#ffffff',
                border: 'none',
                'border-radius': '6px',
                'font-size': '16px',
                'font-weight': '500',
                cursor: 'pointer',
                transition: 'background 0.2s'
            }
        }
    });
    
    // Link Button (Styled as link but behaves as button)
    bm.add('link-button', {
        label: 'Link Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-btn', 'atd-btn-link'],
            content: 'Link Action',
            style: {
                padding: '0',
                background: 'none',
                color: '#1976d2',
                border: 'none',
                'font-size': '16px',
                'text-decoration': 'underline',
                cursor: 'pointer'
            }
        }
    });
}
