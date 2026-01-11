/**
 * Anki Custom Blocks for GrapeJS
 * Defines all custom component blocks for Anki templates
 */

(function() {
    'use strict';
    
    /**
     * Register all Anki blocks
     * @param {object} editor - GrapeJS editor instance
     */
    window.registerAnkiBlocks = function(editor) {
        const blockManager = editor.BlockManager;
        
        // ========== Anki Specific Blocks ========== 
        
        // Anki Field Block
        blockManager.add('anki-field', {
            label: 'Anki Field',
            category: 'Anki',
            content: {
                type: 'text',
                content: '{{Front}}',
                attributes: {
                    'data-anki-field': 'Front',
                    'class': 'anki-field'
                },
                traits: [
                    {
                        type: 'anki-field-select',
                        label: 'Field',
                        name: 'data-anki-field'
                    }
                ]
            },
            attributes: {
                class: 'fa fa-bookmark'
            }
        });
        
        // Cloze Deletion Block
        blockManager.add('anki-cloze', {
            label: 'Cloze',
            category: 'Anki',
            content: {
                type: 'text',
                content: '{{cloze:Text}}',
                attributes: {
                    'class': 'anki-cloze'
                }
            },
            attributes: {
                class: 'fa fa-eye-slash'
            }
        });
        
        // Hint Block
        blockManager.add('anki-hint', {
            label: 'Hint',
            category: 'Anki',
            content: {
                type: 'text',
                content: '{{hint:Hint Text}}',
                attributes: {
                    'class': 'anki-hint'
                }
            },
            attributes: {
                class: 'fa fa-question-circle'
            }
        });
        
        // Study Action Bar
        blockManager.add('study-action-bar', {
            label: 'Action Bar',
            category: 'Anki',
            content: {
                type: 'default',
                tagName: 'div',
                attributes: {
                    'class': 'study-action-bar',
                    'data-position': 'top',
                    'data-movable': 'true',
                    'data-visible-on': 'front',
                    'data-button-style': 'default'
                },
                components: [
                    {
                        type: 'button',
                        content: 'Show Answer',
                        attributes: {
                            'data-anki-click': 'showAnswer'
                        }
                    },
                    {
                        type: 'button',
                        content: 'Toggle Flag',
                        attributes: {
                            'data-anki-click': 'toggleFlag'
                        }
                    }
                ],
                traits: [
                    {
                        type: 'select',
                        label: 'Position',
                        name: 'data-position',
                        options: [
                            { value: 'top', name: 'Top' },
                            { value: 'bottom', name: 'Bottom' },
                            { value: 'left', name: 'Left' },
                            { value: 'right', name: 'Right' }
                        ]
                    },
                    {
                        type: 'checkbox',
                        label: 'Movable',
                        name: 'data-movable'
                    },
                    {
                        type: 'select',
                        label: 'Visible On',
                        name: 'data-visible-on',
                        options: [
                            { value: 'front', name: 'Front Only' },
                            { value: 'back', name: 'Back Only' },
                            { value: 'both', name: 'Both Sides' }
                        ]
                    }
                ]
            },
            attributes: {
                class: 'fa fa-bars'
            }
        });
        
        // ========== Basic HTML Blocks ========== 
        
        blockManager.add('text', {
            label: 'Text',
            category: 'Basic',
            content: {
                type: 'text',
                content: 'Insert your text here',
                activeOnRender: 1
            },
            attributes: {
                class: 'fa fa-font'
            }
        });
        
        blockManager.add('image', {
            label: 'Image',
            category: 'Basic',
            content: {
                type: 'image',
                attributes: {
                    src: 'https://via.placeholder.com/350x250/78c5d6/fff'
                }
            },
            attributes: {
                class: 'fa fa-image'
            }
        });
        
        blockManager.add('link', {
            label: 'Link',
            category: 'Basic',
            content: {
                type: 'link',
                content: 'Link',
                attributes: {
                    href: '#'
                }
            },
            attributes: {
                class: 'fa fa-link'
            }
        });
        
        blockManager.add('video', {
            label: 'Video',
            category: 'Basic',
            content: {
                type: 'video',
                attributes: {
                    src: '',
                    poster: 'https://via.placeholder.com/350x250/78c5d6/fff'
                }
            },
            attributes: {
                class: 'fa fa-video-camera'
            }
        });
        
        blockManager.add('button', {
            label: 'Button',
            category: 'Basic',
            content: {
                type: 'button',
                content: 'Button',
                attributes: {
                    type: 'button'
                }
            },
            attributes: {
                class: 'fa fa-square'
            }
        });
        
        // ========== Layout Blocks ========== 
        
        blockManager.add('container', {
            label: 'Container',
            category: 'Layout',
            content: {
                type: 'default',
                tagName: 'div',
                attributes: {
                    class: 'container'
                },
                components: '<p>Container</p>'
            },
            attributes: {
                class: 'fa fa-square-o'
            }
        });
        
        blockManager.add('row', {
            label: '2 Columns',
            category: 'Layout',
            content: {
                type: 'default',
                tagName: 'div',
                attributes: {
                    class: 'row'
                },
                components: [
                    {
                        type: 'default',
                        tagName: 'div',
                        attributes: { class: 'col' },
                        components: '<p>Column 1</p>'
                    },
                    {
                        type: 'default',
                        tagName: 'div',
                        attributes: { class: 'col' },
                        components: '<p>Column 2</p>'
                    }
                ]
            },
            attributes: {
                class: 'fa fa-columns'
            }
        });
        
        blockManager.add('row-3', {
            label: '3 Columns',
            category: 'Layout',
            content: {
                type: 'default',
                tagName: 'div',
                attributes: {
                    class: 'row'
                },
                components: [
                    {
                        type: 'default',
                        tagName: 'div',
                        attributes: { class: 'col' },
                        components: '<p>Column 1</p>'
                    },
                    {
                        type: 'default',
                        tagName: 'div',
                        attributes: { class: 'col' },
                        components: '<p>Column 2</p>'
                    },
                    {
                        type: 'default',
                        tagName: 'div',
                        attributes: { class: 'col' },
                        components: '<p>Column 3</p>'
                    }
                ]
            },
            attributes: {
                class: 'fa fa-th'
            }
        });
        
        // ========== Form Blocks ========== 
        
        blockManager.add('input', {
            label: 'Input',
            category: 'Forms',
            content: {
                type: 'input',
                attributes: {
                    type: 'text',
                    placeholder: 'Enter text'
                }
            },
            attributes: {
                class: 'fa fa-i-cursor'
            }
        });
        
        blockManager.add('textarea', {
            label: 'Textarea',
            category: 'Forms',
            content: {
                type: 'textarea',
                attributes: {
                    rows: 4,
                    placeholder: 'Enter text'
                }
            },
            attributes: {
                class: 'fa fa-text-height'
            }
        });
        
        blockManager.add('select', {
            label: 'Select',
            category: 'Forms',
            content: {
                type: 'select',
                components: [
                    { type: 'option', content: 'Option 1' },
                    { type: 'option', content: 'Option 2' }
                ]
            },
            attributes: {
                class: 'fa fa-caret-square-o-down'
            }
        });
        
        console.log('[Blocks] Registered all Anki blocks');
    };
})();
