/**
 * Study Action Bar Component
 * Specialized toolbar for Anki review session controls
 */

export function registerStudyActionBar(editor) {
    const bm = editor.BlockManager;
    const category = 'Anki Special';
    
    // Study Action Bar - Flexible control bar for review sessions
    // NOTE: Component type must be registered first via registerStudyActionBarComponent()
    bm.add('study-action-bar', {
        label: 'Study Action Bar',
        category,
        content: {
            type: 'study-action-bar', // Uses custom component type defined in components/index.js
            components: [
                {
                    tagName: 'button',
                    content: 'Show Answer',
                    classes: ['study-btn'],
                    attributes: { 'data-action': 'ankiShowAnswer' },
                    script: function() {
                        this.addEventListener('click', () => {
                            if (typeof api !== 'undefined') {
                                api.ankiShowAnswer();
                            }
                        });
                    },
                    style: { 
                        padding: '8px 16px', 
                        background: '#1976d2', 
                        color: '#fff', 
                        border: 'none', 
                        'border-radius': '4px', 
                        cursor: 'pointer' 
                    }
                },
                {
                    tagName: 'button',
                    content: 'Mark Card',
                    classes: ['study-btn'],
                    attributes: { 'data-action': 'ankiMarkCard' },
                    script: function() {
                        this.addEventListener('click', () => {
                            if (typeof api !== 'undefined') {
                                api.ankiMarkCard();
                            }
                        });
                    },
                    style: { 
                        padding: '8px 16px', 
                        background: '#ff9800', 
                        color: '#fff', 
                        border: 'none', 
                        'border-radius': '4px', 
                        cursor: 'pointer' 
                    }
                },
                {
                    tagName: 'button',
                    content: 'Flag',
                    classes: ['study-btn'],
                    attributes: { 'data-action': 'ankiToggleFlag' },
                    script: function() {
                        this.addEventListener('click', () => {
                            if (typeof api !== 'undefined') {
                                api.ankiToggleFlag(1);
                            }
                        });
                    },
                    style: { 
                        padding: '8px 16px', 
                        background: '#f44336', 
                        color: '#fff', 
                        border: 'none', 
                        'border-radius': '4px', 
                        cursor: 'pointer' 
                    }
                }
            ]
            // Traits are inherited from component type definition
        }
    });
}
