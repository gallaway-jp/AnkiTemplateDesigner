/**
 * Anki Custom Blocks for GrapeJS
 * Modular block registration system
 * 
 * NOTE: This file uses dynamic module loading to avoid blocking
 * It will be called by designer.js after modules are ready
 */

/**
 * Wait for all block modules to load, then register blocks
 * @param {object} editor - GrapeJS editor instance
 */
window.registerAnkiBlocks = async function(editor) {
    const blockManager = editor.BlockManager;
    
    try {
        // Dynamically import all block modules
        const [
            layoutModule,
            studyActionModule,
            inputModule,
            buttonModule,
            dataModule,
            feedbackModule,
            overlayModule,
            animationModule,
            accessibilityModule
        ] = await Promise.all([
            import('./layout.js').catch(e => {
                console.error('[Blocks] Failed to load layout:', e);
                return {};
            }),
            import('./study-action-bar.js').catch(e => {
                console.error('[Blocks] Failed to load study-action-bar:', e);
                return {};
            }),
            import('./inputs.js').catch(e => {
                console.error('[Blocks] Failed to load inputs:', e);
                return {};
            }),
            import('./buttons.js').catch(e => {
                console.error('[Blocks] Failed to load buttons:', e);
                return {};
            }),
            import('./data.js').catch(e => {
                console.error('[Blocks] Failed to load data:', e);
                return {};
            }),
            import('./feedback.js').catch(e => {
                console.error('[Blocks] Failed to load feedback:', e);
                return {};
            }),
            import('./overlays.js').catch(e => {
                console.error('[Blocks] Failed to load overlays:', e);
                return {};
            }),
            import('./animations.js').catch(e => {
                console.error('[Blocks] Failed to load animations:', e);
                return {};
            }),
            import('./accessibility.js').catch(e => {
                console.error('[Blocks] Failed to load accessibility:', e);
                return {};
            })
        ]);
        
        // Extract registration functions
        const {
            registerLayoutBlocks = () => {},
            registerStudyActionBar = () => {},
            registerInputBlocks = () => {},
            registerButtonBlocks = () => {},
            registerDataBlocks = () => {},
            registerFeedbackBlocks = () => {},
            registerOverlayBlocks = () => {},
            registerAnimationBlocks = () => {},
            registerAccessibilityBlocks = () => {}
        } = {
            registerLayoutBlocks: layoutModule.registerLayoutBlocks,
            registerStudyActionBar: studyActionModule.registerStudyActionBar,
            registerInputBlocks: inputModule.registerInputBlocks,
            registerButtonBlocks: buttonModule.registerButtonBlocks,
            registerDataBlocks: dataModule.registerDataBlocks,
            registerFeedbackBlocks: feedbackModule.registerFeedbackBlocks,
            registerOverlayBlocks: overlayModule.registerOverlayBlocks,
            registerAnimationBlocks: animationModule.registerAnimationBlocks,
            registerAccessibilityBlocks: accessibilityModule.registerAccessibilityBlocks
        };
        
        // ========== Anki Specific Blocks ==========
        
        // Anki Field Block
        blockManager.add('anki-field', {
            label: 'Anki Field',
            category: 'Anki Special',
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
            category: 'Anki Special',
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
            category: 'Anki Special',
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
        
        // ========== Register All Modular Block Categories ==========
        
        // Study Action Bar (Anki Special)
        if (registerStudyActionBar) registerStudyActionBar(editor);
        
        // Layout & Structure
        if (registerLayoutBlocks) registerLayoutBlocks(editor);
        
        // Inputs & Forms
        if (registerInputBlocks) registerInputBlocks(editor);
        
        // Buttons & Actions
        if (registerButtonBlocks) registerButtonBlocks(editor);
        
        // Data Display
        if (registerDataBlocks) registerDataBlocks(editor);
        
        // Feedback & Status
        if (registerFeedbackBlocks) registerFeedbackBlocks(editor);
        
        // Overlays & Popups
        if (registerOverlayBlocks) registerOverlayBlocks(editor);
        
        // Animations
        if (registerAnimationBlocks) registerAnimationBlocks(editor);
        
        // Accessibility
        if (registerAccessibilityBlocks) registerAccessibilityBlocks(editor);
        
        console.log('✓ Anki blocks registered successfully');
    } catch (error) {
        console.error('[Blocks] Error registering blocks:', error);
        console.warn('[Blocks] Some blocks may not be available');
    }
};

// Signal that the module is ready
window.ankiBlocksModuleReady = true;
console.log('[Modules] Blocks module loaded');

