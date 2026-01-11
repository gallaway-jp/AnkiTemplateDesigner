# 04c - Component Library: Data Display, Feedback & Overlays

> **Purpose**: Define GrapeJS blocks for Data Display, Feedback, Status, and Overlay components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

This document defines blocks for:
- **Data Display Components** (30 components)
- **Feedback & Status Indicators** (16 components)
- **Overlays & Popups** (11 components)

---

## 5. Data Display Components

### `web/blocks/data.js`

```javascript
/**
 * Data Display Component Blocks
 */

export function registerDataBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Data Display';
    
    // ========== TEXT & CONTENT ==========
    
    // Heading
    bm.add('heading', {
        label: 'Heading',
        category,
        content: {
            tagName: 'h2',
            classes: ['atd-heading'],
            content: 'Heading Text',
            style: { 'font-size': '24px', 'font-weight': '600', margin: '0 0 16px' }
        }
    });
    
    // Paragraph
    bm.add('paragraph', {
        label: 'Paragraph',
        category,
        content: {
            tagName: 'p',
            classes: ['atd-paragraph'],
            content: 'This is a paragraph of text. You can edit this content directly in the canvas.',
            style: { 'line-height': '1.6', margin: '0 0 16px' }
        }
    });
    
    // Caption
    bm.add('caption', {
        label: 'Caption',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-caption'],
            content: 'Caption text',
            style: { 'font-size': '12px', color: '#666' }
        }
    });
    
    // Label
    bm.add('label', {
        label: 'Label',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-label'],
            content: 'Label',
            style: { 'font-size': '14px', 'font-weight': '500' }
        }
    });
    
    // Code Block
    bm.add('code-block', {
        label: 'Code Block',
        category,
        content: {
            tagName: 'pre',
            classes: ['atd-code-block'],
            style: { padding: '16px', background: '#1e1e1e', color: '#d4d4d4', 'border-radius': '8px', overflow: 'auto', 'font-family': 'monospace' },
            components: [
                { tagName: 'code', content: 'const greeting = "Hello, World!";\nconsole.log(greeting);' }
            ]
        }
    });
    
    // Inline Code
    bm.add('inline-code', {
        label: 'Inline Code',
        category,
        content: {
            tagName: 'code',
            classes: ['atd-inline-code'],
            content: 'inline code',
            style: { padding: '2px 6px', background: '#f5f5f5', 'border-radius': '4px', 'font-family': 'monospace', 'font-size': '14px' }
        }
    });
    
    // Blockquote
    bm.add('blockquote', {
        label: 'Blockquote',
        category,
        content: {
            tagName: 'blockquote',
            classes: ['atd-blockquote'],
            style: { margin: '16px 0', padding: '12px 20px', 'border-left': '4px solid #1976d2', background: '#f5f5f5', 'font-style': 'italic' },
            components: [
                { tagName: 'p', content: '"This is a quote."', style: { margin: '0' } }
            ]
        }
    });
    
    // ========== LISTS & TABLES ==========
    
    // Unordered List
    bm.add('unordered-list', {
        label: 'Unordered List',
        category,
        content: {
            tagName: 'ul',
            classes: ['atd-list'],
            style: { 'padding-left': '24px', margin: '0' },
            components: [
                { tagName: 'li', content: 'List item 1', style: { 'margin-bottom': '8px' } },
                { tagName: 'li', content: 'List item 2', style: { 'margin-bottom': '8px' } },
                { tagName: 'li', content: 'List item 3' }
            ]
        }
    });
    
    // Ordered List
    bm.add('ordered-list', {
        label: 'Ordered List',
        category,
        content: {
            tagName: 'ol',
            classes: ['atd-list'],
            style: { 'padding-left': '24px', margin: '0' },
            components: [
                { tagName: 'li', content: 'First item', style: { 'margin-bottom': '8px' } },
                { tagName: 'li', content: 'Second item', style: { 'margin-bottom': '8px' } },
                { tagName: 'li', content: 'Third item' }
            ]
        }
    });
    
    // List with Icons
    bm.add('icon-list', {
        label: 'Icon List',
        category,
        content: {
            tagName: 'ul',
            classes: ['atd-icon-list'],
            style: { 'list-style': 'none', padding: '0', margin: '0' },
            components: [
                { tagName: 'li', style: { display: 'flex', gap: '12px', 'margin-bottom': '12px' }, components: [{ tagName: 'span', content: '✓', style: { color: '#4caf50' } }, { tagName: 'span', content: 'Feature one' }] },
                { tagName: 'li', style: { display: 'flex', gap: '12px', 'margin-bottom': '12px' }, components: [{ tagName: 'span', content: '✓', style: { color: '#4caf50' } }, { tagName: 'span', content: 'Feature two' }] },
                { tagName: 'li', style: { display: 'flex', gap: '12px' }, components: [{ tagName: 'span', content: '✓', style: { color: '#4caf50' } }, { tagName: 'span', content: 'Feature three' }] }
            ]
        }
    });
    
    // Table
    bm.add('table', {
        label: 'Table',
        category,
        content: {
            tagName: 'table',
            classes: ['atd-table'],
            style: { width: '100%', 'border-collapse': 'collapse' },
            components: [
                { tagName: 'thead', components: [
                    { tagName: 'tr', components: [
                        { tagName: 'th', content: 'Header 1', style: { padding: '12px', 'text-align': 'left', 'border-bottom': '2px solid #e0e0e0', 'font-weight': '600' } },
                        { tagName: 'th', content: 'Header 2', style: { padding: '12px', 'text-align': 'left', 'border-bottom': '2px solid #e0e0e0', 'font-weight': '600' } },
                        { tagName: 'th', content: 'Header 3', style: { padding: '12px', 'text-align': 'left', 'border-bottom': '2px solid #e0e0e0', 'font-weight': '600' } }
                    ]}
                ]},
                { tagName: 'tbody', components: [
                    { tagName: 'tr', components: [
                        { tagName: 'td', content: 'Cell 1', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                        { tagName: 'td', content: 'Cell 2', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                        { tagName: 'td', content: 'Cell 3', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } }
                    ]},
                    { tagName: 'tr', components: [
                        { tagName: 'td', content: 'Cell 4', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                        { tagName: 'td', content: 'Cell 5', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                        { tagName: 'td', content: 'Cell 6', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } }
                    ]}
                ]}
            ]
        }
    });
    
    // Definition List
    bm.add('definition-list', {
        label: 'Definition List',
        category,
        content: {
            tagName: 'dl',
            classes: ['atd-definition-list'],
            components: [
                { tagName: 'dt', content: 'Term 1', style: { 'font-weight': '600', 'margin-bottom': '4px' } },
                { tagName: 'dd', content: 'Definition for term 1', style: { margin: '0 0 16px', color: '#666' } },
                { tagName: 'dt', content: 'Term 2', style: { 'font-weight': '600', 'margin-bottom': '4px' } },
                { tagName: 'dd', content: 'Definition for term 2', style: { margin: '0', color: '#666' } }
            ]
        }
    });
    
    // ========== MEDIA ==========
    
    // Image
    bm.add('image', {
        label: 'Image',
        category,
        content: {
            tagName: 'img',
            classes: ['atd-image'],
            attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"%3E%3Crect fill="%23e0e0e0" width="200" height="150"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage%3C/text%3E%3C/svg%3E', alt: 'Placeholder image' },
            style: { 'max-width': '100%', height: 'auto', 'border-radius': '8px' }
        }
    });
    
    // Image Gallery
    bm.add('image-gallery', {
        label: 'Image Gallery',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-gallery'],
            style: { display: 'grid', 'grid-template-columns': 'repeat(3, 1fr)', gap: '8px' },
            components: [
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23e0e0e0" width="100" height="100"/%3E%3C/svg%3E' }, style: { width: '100%', 'aspect-ratio': '1', 'object-fit': 'cover', 'border-radius': '4px' } },
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23e0e0e0" width="100" height="100"/%3E%3C/svg%3E' }, style: { width: '100%', 'aspect-ratio': '1', 'object-fit': 'cover', 'border-radius': '4px' } },
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23e0e0e0" width="100" height="100"/%3E%3C/svg%3E' }, style: { width: '100%', 'aspect-ratio': '1', 'object-fit': 'cover', 'border-radius': '4px' } }
            ]
        }
    });
    
    // Video Player
    bm.add('video-player', {
        label: 'Video Player',
        category,
        content: {
            tagName: 'video',
            classes: ['atd-video'],
            attributes: { controls: true },
            style: { width: '100%', 'border-radius': '8px', background: '#000' }
        }
    });
    
    // Audio Player
    bm.add('audio-player', {
        label: 'Audio Player',
        category,
        content: {
            tagName: 'audio',
            classes: ['atd-audio'],
            attributes: { controls: true },
            style: { width: '100%' }
        }
    });
    
    // Avatar
    bm.add('avatar', {
        label: 'Avatar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-avatar'],
            content: 'JD',
            style: { width: '48px', height: '48px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-weight': '600' }
        }
    });
    
    // Icon
    bm.add('icon', {
        label: 'Icon',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-icon'],
            content: '⭐',
            style: { 'font-size': '24px' }
        }
    });
}
```

---

## 6. Feedback & Status Indicators

### `web/blocks/feedback.js`

```javascript
/**
 * Feedback & Status Component Blocks
 */

export function registerFeedbackBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Feedback & Status';
    
    // Toast Notification
    bm.add('toast', {
        label: 'Toast',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-toast'],
            style: { display: 'flex', 'align-items': 'center', gap: '12px', padding: '12px 16px', background: '#323232', color: '#fff', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0,0,0,0.15)' },
            components: [
                { tagName: 'span', content: 'This is a toast message' },
                { tagName: 'button', content: '✕', style: { border: 'none', background: 'none', color: '#fff', cursor: 'pointer', 'margin-left': 'auto' } }
            ]
        }
    });
    
    // Snackbar
    bm.add('snackbar', {
        label: 'Snackbar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-snackbar'],
            style: { display: 'flex', 'align-items': 'center', 'justify-content': 'space-between', padding: '14px 16px', background: '#323232', color: '#fff', 'border-radius': '4px' },
            components: [
                { tagName: 'span', content: 'Message sent' },
                { tagName: 'button', content: 'UNDO', style: { border: 'none', background: 'none', color: '#bb86fc', cursor: 'pointer', 'font-weight': '600' } }
            ]
        }
    });
    
    // Alert - Info
    bm.add('alert-info', {
        label: 'Alert (Info)',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-info'],
            style: { display: 'flex', gap: '12px', padding: '16px', background: '#e3f2fd', border: '1px solid #90caf9', 'border-radius': '8px' },
            components: [
                { tagName: 'span', content: 'ℹ️' },
                { tagName: 'div', components: [
                    { tagName: 'strong', content: 'Information', style: { display: 'block', 'margin-bottom': '4px' } },
                    { tagName: 'span', content: 'This is an informational message.' }
                ]}
            ]
        }
    });
    
    // Alert - Success
    bm.add('alert-success', {
        label: 'Alert (Success)',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-success'],
            style: { display: 'flex', gap: '12px', padding: '16px', background: '#e8f5e9', border: '1px solid #a5d6a7', 'border-radius': '8px' },
            components: [
                { tagName: 'span', content: '✓' },
                { tagName: 'span', content: 'Operation completed successfully!' }
            ]
        }
    });
    
    // Alert - Warning
    bm.add('alert-warning', {
        label: 'Alert (Warning)',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-warning'],
            style: { display: 'flex', gap: '12px', padding: '16px', background: '#fff3e0', border: '1px solid #ffcc80', 'border-radius': '8px' },
            components: [
                { tagName: 'span', content: '⚠️' },
                { tagName: 'span', content: 'Please review before continuing.' }
            ]
        }
    });
    
    // Alert - Error
    bm.add('alert-error', {
        label: 'Alert (Error)',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-alert', 'atd-alert-error'],
            style: { display: 'flex', gap: '12px', padding: '16px', background: '#ffebee', border: '1px solid #ef9a9a', 'border-radius': '8px' },
            components: [
                { tagName: 'span', content: '✕' },
                { tagName: 'span', content: 'An error occurred. Please try again.' }
            ]
        }
    });
    
    // Banner
    bm.add('banner', {
        label: 'Banner',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-banner'],
            style: { display: 'flex', 'align-items': 'center', 'justify-content': 'center', gap: '12px', padding: '12px 20px', background: '#1976d2', color: '#fff' },
            components: [
                { tagName: 'span', content: '🎉 New feature available!' },
                { tagName: 'a', content: 'Learn more', attributes: { href: '#' }, style: { color: '#fff', 'font-weight': '600' } }
            ]
        }
    });
    
    // Badge
    bm.add('badge', {
        label: 'Badge',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-badge'],
            content: '5',
            style: { display: 'inline-flex', 'align-items': 'center', 'justify-content': 'center', 'min-width': '20px', height: '20px', padding: '0 6px', background: '#d32f2f', color: '#fff', 'border-radius': '10px', 'font-size': '12px', 'font-weight': '600' }
        }
    });
    
    // Status Pill
    bm.add('status-pill', {
        label: 'Status Pill',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-status-pill'],
            content: 'Active',
            style: { display: 'inline-flex', 'align-items': 'center', gap: '6px', padding: '4px 12px', background: '#e8f5e9', color: '#2e7d32', 'border-radius': '20px', 'font-size': '13px', 'font-weight': '500' }
        }
    });
    
    // Progress Bar
    bm.add('progress-bar', {
        label: 'Progress Bar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-progress'],
            style: { width: '100%', height: '8px', background: '#e0e0e0', 'border-radius': '4px', overflow: 'hidden' },
            components: [
                { tagName: 'div', classes: ['atd-progress-fill'], style: { width: '60%', height: '100%', background: '#1976d2', 'border-radius': '4px' } }
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
            style: { width: '48px', height: '48px', border: '4px solid #e0e0e0', 'border-top-color': '#1976d2', 'border-radius': '50%' }
        }
    });
    
    // Spinner
    bm.add('spinner', {
        label: 'Spinner',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-spinner'],
            content: '⟳',
            style: { 'font-size': '32px', color: '#1976d2' }
        }
    });
    
    // Skeleton Loader
    bm.add('skeleton', {
        label: 'Skeleton Loader',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-skeleton'],
            style: { display: 'flex', 'flex-direction': 'column', gap: '12px' },
            components: [
                { tagName: 'div', style: { width: '100%', height: '20px', background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', 'border-radius': '4px' } },
                { tagName: 'div', style: { width: '80%', height: '20px', background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', 'border-radius': '4px' } },
                { tagName: 'div', style: { width: '60%', height: '20px', background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)', 'border-radius': '4px' } }
            ]
        }
    });
    
    // Empty State
    bm.add('empty-state', {
        label: 'Empty State',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-empty-state'],
            style: { 'text-align': 'center', padding: '40px 20px' },
            components: [
                { tagName: 'div', content: '📭', style: { 'font-size': '48px', 'margin-bottom': '16px' } },
                { tagName: 'h3', content: 'No items yet', style: { margin: '0 0 8px', 'font-weight': '600' } },
                { tagName: 'p', content: 'Get started by adding your first item.', style: { color: '#666', margin: '0 0 16px' } },
                { tagName: 'button', content: 'Add Item', style: { padding: '10px 20px', border: 'none', 'border-radius': '6px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Error State
    bm.add('error-state', {
        label: 'Error State',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-error-state'],
            style: { 'text-align': 'center', padding: '40px 20px' },
            components: [
                { tagName: 'div', content: '❌', style: { 'font-size': '48px', 'margin-bottom': '16px' } },
                { tagName: 'h3', content: 'Something went wrong', style: { margin: '0 0 8px', 'font-weight': '600' } },
                { tagName: 'p', content: 'We couldn\'t load the content. Please try again.', style: { color: '#666', margin: '0 0 16px' } },
                { tagName: 'button', content: 'Retry', style: { padding: '10px 20px', border: 'none', 'border-radius': '6px', background: '#d32f2f', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
}
```

---

## 7. Overlays & Popups

### `web/blocks/overlays.js`

```javascript
/**
 * Overlay & Popup Component Blocks
 */

export function registerOverlayBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Overlays & Popups';
    
    // Modal Dialog
    bm.add('modal-dialog', {
        label: 'Modal Dialog',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-modal-overlay'],
            style: { position: 'fixed', top: '0', left: '0', right: '0', bottom: '0', background: 'rgba(0,0,0,0.5)', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'z-index': '1000' },
            components: [{
                tagName: 'div',
                classes: ['atd-modal'],
                style: { width: '90%', 'max-width': '480px', background: '#fff', 'border-radius': '12px', overflow: 'hidden' },
                components: [
                    { tagName: 'div', classes: ['atd-modal-header'], style: { display: 'flex', 'justify-content': 'space-between', padding: '16px 20px', 'border-bottom': '1px solid #e0e0e0' }, components: [
                        { tagName: 'h3', content: 'Modal Title', style: { margin: '0', 'font-size': '18px' } },
                        { tagName: 'button', content: '✕', style: { border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } }
                    ]},
                    { tagName: 'div', classes: ['atd-modal-body'], style: { padding: '20px' }, components: [{ tagName: 'p', content: 'Modal content goes here.' }] },
                    { tagName: 'div', classes: ['atd-modal-footer'], style: { display: 'flex', 'justify-content': 'flex-end', gap: '8px', padding: '16px 20px', 'border-top': '1px solid #e0e0e0' }, components: [
                        { tagName: 'button', content: 'Cancel', style: { padding: '10px 20px', border: '1px solid #e0e0e0', 'border-radius': '6px', background: '#fff', cursor: 'pointer' } },
                        { tagName: 'button', content: 'Confirm', style: { padding: '10px 20px', border: 'none', 'border-radius': '6px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
                    ]}
                ]
            }]
        }
    });
    
    // Alert Dialog
    bm.add('alert-dialog', {
        label: 'Alert Dialog',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-dialog'],
            style: { width: '320px', padding: '24px', background: '#fff', 'border-radius': '12px', 'box-shadow': '0 10px 40px rgba(0,0,0,0.2)', 'text-align': 'center' },
            components: [
                { tagName: 'div', content: '⚠️', style: { 'font-size': '48px', 'margin-bottom': '16px' } },
                { tagName: 'h3', content: 'Are you sure?', style: { margin: '0 0 8px' } },
                { tagName: 'p', content: 'This action cannot be undone.', style: { color: '#666', margin: '0 0 20px' } },
                { tagName: 'button', content: 'OK', style: { width: '100%', padding: '12px', border: 'none', 'border-radius': '6px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Popover
    bm.add('popover', {
        label: 'Popover',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-popover'],
            style: { position: 'relative', display: 'inline-block', padding: '12px 16px', background: '#fff', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0,0,0,0.15)' },
            components: [
                { tagName: 'div', content: 'Popover content', style: { 'white-space': 'nowrap' } },
                { tagName: 'div', classes: ['atd-popover-arrow'], style: { position: 'absolute', bottom: '-6px', left: '50%', transform: 'translateX(-50%)', width: '12px', height: '12px', background: '#fff', 'box-shadow': '2px 2px 4px rgba(0,0,0,0.1)', transform: 'rotate(45deg)' } }
            ]
        }
    });
    
    // Tooltip
    bm.add('tooltip', {
        label: 'Tooltip',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-tooltip'],
            style: { padding: '6px 10px', background: '#333', color: '#fff', 'border-radius': '4px', 'font-size': '12px', 'white-space': 'nowrap' },
            components: [{ type: 'text', content: 'Tooltip text' }]
        }
    });
    
    // Context Menu
    bm.add('context-menu', {
        label: 'Context Menu',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-context-menu'],
            style: { 'min-width': '160px', background: '#fff', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0,0,0,0.15)', overflow: 'hidden' },
            components: [
                { tagName: 'button', content: '✂️ Cut', style: { display: 'block', width: '100%', padding: '10px 16px', border: 'none', background: 'none', 'text-align': 'left', cursor: 'pointer' } },
                { tagName: 'button', content: '📋 Copy', style: { display: 'block', width: '100%', padding: '10px 16px', border: 'none', background: 'none', 'text-align': 'left', cursor: 'pointer' } },
                { tagName: 'button', content: '📄 Paste', style: { display: 'block', width: '100%', padding: '10px 16px', border: 'none', background: 'none', 'text-align': 'left', cursor: 'pointer' } },
                { tagName: 'hr', style: { margin: '4px 0', border: 'none', 'border-top': '1px solid #e0e0e0' } },
                { tagName: 'button', content: '🗑️ Delete', style: { display: 'block', width: '100%', padding: '10px 16px', border: 'none', background: 'none', 'text-align': 'left', cursor: 'pointer', color: '#d32f2f' } }
            ]
        }
    });
    
    // Dropdown Menu
    bm.add('dropdown-menu', {
        label: 'Dropdown Menu',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-dropdown-menu'],
            style: { 'min-width': '180px', background: '#fff', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0,0,0,0.15)', padding: '4px 0' },
            components: [
                { tagName: 'a', content: 'Profile', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#333', 'text-decoration': 'none' } },
                { tagName: 'a', content: 'Settings', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#333', 'text-decoration': 'none' } },
                { tagName: 'hr', style: { margin: '4px 0', border: 'none', 'border-top': '1px solid #e0e0e0' } },
                { tagName: 'a', content: 'Logout', attributes: { href: '#' }, style: { display: 'block', padding: '10px 16px', color: '#d32f2f', 'text-decoration': 'none' } }
            ]
        }
    });
    
    // Bottom Sheet
    bm.add('bottom-sheet', {
        label: 'Bottom Sheet',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-bottom-sheet'],
            style: { position: 'fixed', bottom: '0', left: '0', right: '0', background: '#fff', 'border-radius': '16px 16px 0 0', 'box-shadow': '0 -4px 20px rgba(0,0,0,0.15)', padding: '20px' },
            components: [
                { tagName: 'div', classes: ['atd-sheet-handle'], style: { width: '40px', height: '4px', background: '#e0e0e0', 'border-radius': '2px', margin: '0 auto 16px' } },
                { tagName: 'h3', content: 'Bottom Sheet', style: { margin: '0 0 16px' } },
                { tagName: 'p', content: 'Sheet content goes here.' }
            ]
        }
    });
    
    // Lightbox
    bm.add('lightbox', {
        label: 'Lightbox',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-lightbox'],
            style: { position: 'fixed', top: '0', left: '0', right: '0', bottom: '0', background: 'rgba(0,0,0,0.9)', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'z-index': '1000' },
            components: [
                { tagName: 'button', content: '✕', style: { position: 'absolute', top: '20px', right: '20px', border: 'none', background: 'none', color: '#fff', 'font-size': '32px', cursor: 'pointer' } },
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="600" height="400"%3E%3Crect fill="%23333" width="600" height="400"/%3E%3C/svg%3E' }, style: { 'max-width': '90%', 'max-height': '90%' } }
            ]
        }
    });
    
    // Notification Panel
    bm.add('notification-panel', {
        label: 'Notification Panel',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-notification-panel'],
            style: { width: '320px', background: '#fff', 'border-radius': '12px', 'box-shadow': '0 4px 20px rgba(0,0,0,0.15)', overflow: 'hidden' },
            components: [
                { tagName: 'div', style: { padding: '16px', 'border-bottom': '1px solid #e0e0e0' }, components: [{ tagName: 'h3', content: 'Notifications', style: { margin: '0' } }] },
                { tagName: 'div', style: { 'max-height': '300px', overflow: 'auto' }, components: [
                    { tagName: 'div', style: { display: 'flex', gap: '12px', padding: '12px 16px', 'border-bottom': '1px solid #f0f0f0' }, components: [
                        { tagName: 'div', content: '🔔', style: { 'font-size': '20px' } },
                        { tagName: 'div', components: [{ tagName: 'p', content: 'New message received', style: { margin: '0 0 4px' } }, { tagName: 'span', content: '2 mins ago', style: { 'font-size': '12px', color: '#666' } }] }
                    ]}
                ]}
            ]
        }
    });
    
    // Coach Mark
    bm.add('coach-mark', {
        label: 'Coach Mark',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-coach-mark'],
            style: { position: 'relative' },
            components: [
                { tagName: 'div', classes: ['atd-coach-highlight'], style: { width: '100px', height: '40px', border: '3px solid #1976d2', 'border-radius': '8px' } },
                { tagName: 'div', classes: ['atd-coach-tooltip'], style: { position: 'absolute', top: '50px', left: '0', padding: '12px 16px', background: '#1976d2', color: '#fff', 'border-radius': '8px', 'max-width': '250px' }, components: [
                    { tagName: 'p', content: 'Click here to get started!', style: { margin: '0 0 8px' } },
                    { tagName: 'button', content: 'Got it', style: { padding: '6px 12px', border: 'none', 'border-radius': '4px', background: 'rgba(255,255,255,0.2)', color: '#fff', cursor: 'pointer' } }
                ]}
            ]
        }
    });
}
```

---

## Next Document

See [04d-COMPONENT-LIBRARY-ADVANCED.md](04d-COMPONENT-LIBRARY-ADVANCED.md) for Search, Commerce, Social, Charts, Accessibility, System, Motion, and Specialized components.
