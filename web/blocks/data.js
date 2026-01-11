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
    
    // Definition List
    bm.add('definition-list', {
        label: 'Definition List',
        category,
        content: {
            tagName: 'dl',
            classes: ['atd-dl'],
            components: [
                { tagName: 'dt', content: 'Term 1', style: { 'font-weight': '600', 'margin-bottom': '4px' } },
                { tagName: 'dd', content: 'Definition 1', style: { 'margin-left': '0', 'margin-bottom': '12px' } },
                { tagName: 'dt', content: 'Term 2', style: { 'font-weight': '600', 'margin-bottom': '4px' } },
                { tagName: 'dd', content: 'Definition 2', style: { 'margin-left': '0' } }
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
                {
                    tagName: 'thead',
                    components: [{
                        tagName: 'tr',
                        components: [
                            { tagName: 'th', content: 'Header 1', style: { padding: '12px', 'border-bottom': '2px solid #e0e0e0', 'text-align': 'left' } },
                            { tagName: 'th', content: 'Header 2', style: { padding: '12px', 'border-bottom': '2px solid #e0e0e0', 'text-align': 'left' } }
                        ]
                    }]
                },
                {
                    tagName: 'tbody',
                    components: [
                        {
                            tagName: 'tr',
                            components: [
                                { tagName: 'td', content: 'Cell 1', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                                { tagName: 'td', content: 'Cell 2', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } }
                            ]
                        },
                        {
                            tagName: 'tr',
                            components: [
                                { tagName: 'td', content: 'Cell 3', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } },
                                { tagName: 'td', content: 'Cell 4', style: { padding: '12px', 'border-bottom': '1px solid #e0e0e0' } }
                            ]
                        }
                    ]
                }
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
            attributes: { src: 'https://via.placeholder.com/400x300', alt: 'Placeholder image' },
            style: { 'max-width': '100%', height: 'auto', 'border-radius': '8px' }
        }
    });
    
    // Video
    bm.add('video', {
        label: 'Video',
        category,
        content: {
            tagName: 'video',
            classes: ['atd-video'],
            attributes: { controls: true, src: 'video.mp4' },
            style: { width: '100%', 'max-width': '100%', 'border-radius': '8px' }
        }
    });
    
    // Link
    bm.add('link', {
        label: 'Link',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-link'],
            content: 'Link text',
            attributes: { href: '#' },
            style: { color: '#1976d2', 'text-decoration': 'none' }
        }
    });
    
    // ========== DATA DISPLAY ==========
    
    // Key-Value Pair
    bm.add('key-value', {
        label: 'Key-Value Pair',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-key-value'],
            style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' },
            components: [
                { tagName: 'span', classes: ['atd-key'], content: 'Key:', style: { 'font-weight': '500' } },
                { tagName: 'span', classes: ['atd-value'], content: 'Value' }
            ]
        }
    });
    
    // Stat Display
    bm.add('stat-display', {
        label: 'Stat Display',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stat'],
            style: { 'text-align': 'center', padding: '16px' },
            components: [
                { tagName: 'div', classes: ['atd-stat-value'], content: '42', style: { 'font-size': '32px', 'font-weight': '700', color: '#1976d2' } },
                { tagName: 'div', classes: ['atd-stat-label'], content: 'Total Items', style: { 'font-size': '14px', color: '#666', 'margin-top': '4px' } }
            ]
        }
    });
}
