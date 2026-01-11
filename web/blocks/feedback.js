/**
 * Feedback & Status Component Blocks
 */

export function registerFeedbackBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Feedback & Status';
    
    // ========== ALERTS ==========
    
    // Info Alert
    bm.add('alert-info', {
        label: 'Info Alert',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-info'],
            content: 'This is an informational message.',
            style: {
                padding: '12px 16px',
                background: '#e3f2fd',
                border: '1px solid #2196f3',
                'border-radius': '6px',
                color: '#0d47a1',
                'margin-bottom': '16px'
            }
        }
    });
    
    // Success Alert
    bm.add('alert-success', {
        label: 'Success Alert',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-success'],
            content: 'Success! Operation completed.',
            style: {
                padding: '12px 16px',
                background: '#e8f5e9',
                border: '1px solid #4caf50',
                'border-radius': '6px',
                color: '#1b5e20',
                'margin-bottom': '16px'
            }
        }
    });
    
    // Warning Alert
    bm.add('alert-warning', {
        label: 'Warning Alert',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-warning'],
            content: 'Warning: Please review this information.',
            style: {
                padding: '12px 16px',
                background: '#fff3e0',
                border: '1px solid #ff9800',
                'border-radius': '6px',
                color: '#e65100',
                'margin-bottom': '16px'
            }
        }
    });
    
    // Error Alert
    bm.add('alert-error', {
        label: 'Error Alert',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-error'],
            content: 'Error: Something went wrong.',
            style: {
                padding: '12px 16px',
                background: '#ffebee',
                border: '1px solid #f44336',
                'border-radius': '6px',
                color: '#b71c1c',
                'margin-bottom': '16px'
            }
        }
    });
    
    // ========== BADGES & TAGS ==========
    
    // Badge
    bm.add('badge', {
        label: 'Badge',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-badge'],
            content: 'New',
            style: {
                display: 'inline-block',
                padding: '4px 8px',
                background: '#1976d2',
                color: '#ffffff',
                'border-radius': '12px',
                'font-size': '12px',
                'font-weight': '600'
            }
        }
    });
    
    // Tag
    bm.add('tag', {
        label: 'Tag',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-tag'],
            content: 'tag',
            style: {
                display: 'inline-block',
                padding: '4px 12px',
                background: '#f5f5f5',
                color: '#424242',
                'border-radius': '4px',
                'font-size': '14px'
            }
        }
    });
    
    // ========== PROGRESS INDICATORS ==========
    
    // Progress Bar
    bm.add('progress-bar', {
        label: 'Progress Bar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-progress'],
            style: { width: '100%', height: '8px', background: '#e0e0e0', 'border-radius': '4px', overflow: 'hidden' },
            components: [
                { tagName: 'div', classes: ['atd-progress-bar'], style: { width: '60%', height: '100%', background: '#1976d2', transition: 'width 0.3s' } }
            ]
        }
    });
    
    // Circular Progress
    bm.add('circular-progress', {
        label: 'Circular Progress',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-circular-progress'],
            style: { width: '48px', height: '48px', border: '4px solid #e0e0e0', 'border-top': '4px solid #1976d2', 'border-radius': '50%', animation: 'spin 1s linear infinite' },
            components: []
        }
    });
    
    // Spinner
    bm.add('spinner', {
        label: 'Spinner',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-spinner'],
            content: '⏳',
            style: { 'font-size': '24px', animation: 'spin 2s linear infinite' }
        }
    });
    
    // ========== TOOLTIPS & POPOVERS ==========
    
    // Tooltip
    bm.add('tooltip', {
        label: 'Tooltip',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-tooltip-trigger'],
            content: 'Hover me',
            style: { position: 'relative', display: 'inline-block', 'border-bottom': '1px dashed #999', cursor: 'help' },
            components: [
                { 
                    tagName: 'span', 
                    classes: ['atd-tooltip'],
                    content: 'Tooltip text',
                    style: { 
                        visibility: 'hidden',
                        position: 'absolute',
                        bottom: '100%',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        'margin-bottom': '8px',
                        padding: '6px 12px',
                        background: '#333',
                        color: '#fff',
                        'border-radius': '4px',
                        'font-size': '14px',
                        'white-space': 'nowrap'
                    }
                }
            ]
        }
    });
    
    // Toast Notification
    bm.add('toast', {
        label: 'Toast',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-toast'],
            content: 'Toast notification message',
            style: {
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                padding: '12px 20px',
                background: '#323232',
                color: '#ffffff',
                'border-radius': '6px',
                'box-shadow': '0 4px 12px rgba(0,0,0,0.3)',
                'z-index': '1000'
            }
        }
    });
    
    // ========== STATUS INDICATORS ==========
    
    // Status Dot
    bm.add('status-dot', {
        label: 'Status Dot',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-status-dot'],
            style: {
                display: 'inline-block',
                width: '10px',
                height: '10px',
                'border-radius': '50%',
                background: '#4caf50',
                'margin-right': '8px'
            }
        }
    });
    
    // Status Text
    bm.add('status-text', {
        label: 'Status Text',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-status-text'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px' },
            components: [
                { tagName: 'span', classes: ['atd-status-dot'], style: { display: 'inline-block', width: '8px', height: '8px', 'border-radius': '50%', background: '#4caf50' } },
                { tagName: 'span', content: 'Active' }
            ]
        }
    });
}
