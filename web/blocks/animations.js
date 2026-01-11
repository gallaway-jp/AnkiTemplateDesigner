/**
 * Animation Component Blocks (Simplified per COMPONENT-AUDIT.md)
 * Only fade, slide, and stagger - removed bounce, shake, scale, rotate, parallax, scroll-reveal
 */

export function registerAnimationBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Animations';
    
    // Fade Container
    bm.add('fade-container', {
        label: 'Fade Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-fade-container'],
            style: {
                padding: '16px',
                opacity: '0',
                animation: 'fadeIn 0.5s ease-in forwards'
            },
            components: [
                { type: 'text', content: 'Content fades in' }
            ]
        }
    });
    
    // Slide Container
    bm.add('slide-container', {
        label: 'Slide Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-slide-container'],
            style: {
                padding: '16px',
                transform: 'translateY(20px)',
                opacity: '0',
                animation: 'slideUp 0.5s ease-out forwards'
            },
            components: [
                { type: 'text', content: 'Content slides up' }
            ]
        }
    });
    
    // Stagger Group (Sequential animations for child elements)
    bm.add('stagger-group', {
        label: 'Stagger Group',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stagger-group'],
            style: { padding: '16px' },
            components: [
                { tagName: 'div', classes: ['atd-stagger-item'], style: { opacity: '0', animation: 'fadeIn 0.5s ease-in 0s forwards' }, components: [{ type: 'text', content: 'Item 1' }] },
                { tagName: 'div', classes: ['atd-stagger-item'], style: { opacity: '0', animation: 'fadeIn 0.5s ease-in 0.1s forwards' }, components: [{ type: 'text', content: 'Item 2' }] },
                { tagName: 'div', classes: ['atd-stagger-item'], style: { opacity: '0', animation: 'fadeIn 0.5s ease-in 0.2s forwards' }, components: [{ type: 'text', content: 'Item 3' }] }
            ]
        }
    });
}
