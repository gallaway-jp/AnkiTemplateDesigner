/**
 * Accessibility Component Blocks (Simplified per COMPONENT-AUDIT.md)
 */

export function registerAccessibilityBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Accessibility';
    
    // Screen Reader Only Text
    bm.add('sr-only', {
        label: 'Screen Reader Only',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-sr-only'],
            content: 'Screen reader only text',
            style: {
                position: 'absolute',
                width: '1px',
                height: '1px',
                padding: '0',
                margin: '-1px',
                overflow: 'hidden',
                clip: 'rect(0, 0, 0, 0)',
                'white-space': 'nowrap',
                border: '0'
            }
        }
    });
    
    // Accessible Field Wrapper
    bm.add('accessible-field', {
        label: 'Accessible Field',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-accessible-field'],
            components: [
                { tagName: 'label', attributes: { for: 'field-id' }, content: 'Field Label', style: { display: 'block', 'margin-bottom': '4px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'text', id: 'field-id', 'aria-describedby': 'field-help' }, style: { width: '100%', padding: '10px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px' } },
                { tagName: 'span', attributes: { id: 'field-help' }, content: 'Helper text for field', style: { display: 'block', 'margin-top': '4px', 'font-size': '14px', color: '#666' } }
            ]
        }
    });
    
    // Accessible Error Message
    bm.add('accessible-error', {
        label: 'Accessible Error',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-accessible-error'],
            attributes: { role: 'alert', 'aria-live': 'assertive' },
            content: 'Error message',
            style: {
                padding: '12px 16px',
                background: '#ffebee',
                border: '1px solid #f44336',
                'border-radius': '6px',
                color: '#b71c1c'
            }
        }
    });
    
    // Landmark Main
    bm.add('landmark-main', {
        label: 'Main Landmark',
        category,
        content: {
            tagName: 'main',
            classes: ['atd-landmark-main'],
            attributes: { role: 'main' },
            style: { padding: '20px' },
            components: [
                { type: 'text', content: 'Main content area' }
            ]
        }
    });
    
    // Focus Indicator
    bm.add('focus-indicator', {
        label: 'Focus Indicator',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-focus-indicator'],
            content: 'Focusable link',
            attributes: { href: '#' },
            style: {
                display: 'inline-block',
                padding: '8px 16px',
                color: '#1976d2',
                'text-decoration': 'none',
                'border-radius': '4px',
                outline: '2px solid transparent',
                'outline-offset': '2px',
                transition: 'outline 0.2s'
            }
        }
    });
}
