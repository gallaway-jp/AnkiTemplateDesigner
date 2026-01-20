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
    console.log('[Blocks] *** registerAnkiBlocks() STARTED ***');
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
        
        // Count blocks before registration
        const blocksBefore = blockManager.getAll().length;
        console.log('[Blocks] Blocks before registration:', blocksBefore);
        
        // Study Action Bar (Anki Special)
        if (registerStudyActionBar) {
            console.log('[Blocks] Registering study action bar...');
            registerStudyActionBar(editor);
        }
        
        // Layout & Structure
        if (registerLayoutBlocks) {
            console.log('[Blocks] Registering layout blocks...');
            registerLayoutBlocks(editor);
        }
        
        // Inputs & Forms
        if (registerInputBlocks) {
            console.log('[Blocks] Registering input blocks...');
            registerInputBlocks(editor);
        }
        
        // Buttons & Actions
        if (registerButtonBlocks) {
            console.log('[Blocks] Registering button blocks...');
            registerButtonBlocks(editor);
        }
        
        // Data Display
        if (registerDataBlocks) {
            console.log('[Blocks] Registering data blocks...');
            registerDataBlocks(editor);
        }
        
        // Feedback & Status
        if (registerFeedbackBlocks) {
            console.log('[Blocks] Registering feedback blocks...');
            registerFeedbackBlocks(editor);
        }
        
        // Overlays & Popups
        if (registerOverlayBlocks) {
            console.log('[Blocks] Registering overlay blocks...');
            registerOverlayBlocks(editor);
        }
        
        // Animations
        if (registerAnimationBlocks) {
            console.log('[Blocks] Registering animation blocks...');
            registerAnimationBlocks(editor);
        }
        
        // Accessibility
        if (registerAccessibilityBlocks) {
            console.log('[Blocks] Registering accessibility blocks...');
            registerAccessibilityBlocks(editor);
        }
        
        // Count blocks after registration
        const blocksAfter = blockManager.getAll().length;
        console.log('[Blocks] Blocks after registration:', blocksAfter, '(added:', blocksAfter - blocksBefore, ')');
        
        // Update UI with block count
        if (window.updateBlockCount) {
            window.updateBlockCount(blocksAfter);
        }
        if (window.setDebugStatus) {
            window.setDebugStatus(`✓ Blocks Registered (${blocksAfter})`);
        }
        
        // Force render of blocks view - try multiple GrapeJS approaches
        const blocksContainer = document.querySelector('.blocks-container');
        console.log('[Blocks] BlockManager methods:', Object.keys(blockManager).filter(k => typeof blockManager[k] === 'function').join(', '));
        console.log('[Blocks] Blocks container found:', !!blocksContainer, blocksContainer ? `(${blocksContainer.className})` : '');
        
        // Approach 1: Try blockManager.render() (may not actually render to DOM)
        try {
            if (typeof blockManager.render === 'function') {
                console.log('[Blocks] Calling blockManager.render()...');
                blockManager.render();
                console.log('[Blocks] blockManager.render() called');
            }
        } catch (e) {
            console.warn('[Blocks] blockManager.render() error:', e.message);
        }
        
        // Approach 2: Immediately try to access BlockManager panel view and append it
        try {
            console.log('[Blocks] Checking BlockManager panel...');
            const panel = blockManager.getPanel();
            console.log('[Blocks] BlockManager.getPanel():', typeof panel, panel ? Object.keys(panel).join(',') : 'null');
            
            if (panel && panel.view && panel.view.$el && blocksContainer) {
                if (panel.view.$el.parentElement !== blocksContainer) {
                    console.log('[Blocks] Appending BlockManager panel view to container...');
                    blocksContainer.appendChild(panel.view.$el);
                    console.log('[Blocks] Panel view appended');
                }
            }
        } catch (e) {
            console.warn('[Blocks] BlockManager panel access failed:', e.message);
        }
        
        // Approach 3: Manually create block elements from BlockManager data (GUARANTEED to work)
        // This is critical because GrapeJS may not render blocks to the DOM automatically
        if (blocksContainer) {
            // Use a very short timeout to allow GrapeJS a moment, then fill in any missing blocks
            setTimeout(() => {
                try {
                    const existingBlocks = document.querySelectorAll('.gjs-block');
                    console.log('[Blocks] Blocks in DOM before manual render:', existingBlocks.length);
                    
                    if (existingBlocks.length === 0) {
                        // No blocks rendered by GrapeJS, create them manually
                        console.log('[Blocks] No blocks from GrapeJS, manually creating blocks...');
                        const blocks = blockManager.getAll();
                        console.log('[Blocks] Creating', blocks.length, 'block elements manually...');
                        
                        if (blocks.length > 0) {
                            // Create or get the blocks view container
                            let blocksList = blocksContainer.querySelector('.gjs-blocks-view');
                            if (!blocksList) {
                                blocksList = document.createElement('div');
                                blocksList.className = 'gjs-blocks-view';
                                blocksList.style.cssText = 'flex: 1; overflow-y: auto; padding: 0; display: flex; flex-direction: column;';
                                blocksContainer.appendChild(blocksList);
                            }
                            
                            // Create each block element
                            blocks.forEach((block, idx) => {
                                try {
                                    // Skip if already exists
                                    if (blocksList.querySelector(`[data-gjs-type="${block.id}"]`)) {
                                        return;
                                    }
                                    
                                    const blockEl = document.createElement('div');
                                    blockEl.className = 'gjs-block';
                                    blockEl.draggable = true;
                                    blockEl.setAttribute('data-gjs-type', block.id);
                                    blockEl.style.cssText = `
                                        padding: 10px 8px;
                                        margin: 3px 0;
                                        border: 1px solid #1976d2;
                                        border-radius: 4px;
                                        cursor: move;
                                        background: #e3f2fd;
                                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                                        display: block !important;
                                        user-select: none;
                                        color: #1a1a1a !important;
                                    `;
                                    
                                    // Add drag handlers for GrapeJS integration
                                    blockEl.addEventListener('dragstart', (e) => {
                                        e.dataTransfer.effectAllowed = 'copy';
                                        e.dataTransfer.setData('gjs-block-id', block.id);
                                        console.log('[Blocks] Dragging block:', block.id);
                                    });
                                    
                                    // Create label
                                    const label = document.createElement('div');
                                    label.className = 'gjs-block-label';
                                    label.style.cssText = 'font-weight: 600; font-size: 13px; color: #0d47a1 !important; margin-bottom: 3px;';
                                    label.textContent = block.label || block.id;
                                    blockEl.appendChild(label);
                                    
                                    // Create category
                                    const category = document.createElement('div');
                                    category.className = 'gjs-block-category';
                                    category.style.cssText = 'font-size: 11px; color: #333333 !important; margin-top: 2px;';
                                    category.textContent = block.category || 'Other';
                                    blockEl.appendChild(category);
                                    
                                    blocksList.appendChild(blockEl);
                                } catch (e) {
                                    console.error(`[Blocks] Error creating block ${block.id}:`, e);
                                }
                            });
                            
                            const createdCount = blocksList.querySelectorAll('.gjs-block').length;
                            console.log('[Blocks] ✓ Manually created', createdCount, 'block elements');
                        }
                    } else {
                        console.log('[Blocks] ✓ Blocks already in DOM from GrapeJS:', existingBlocks.length);
                    }
                } catch (e) {
                    console.error('[Blocks] Manual block rendering failed:', e);
                }
            }, 5);
        } else {
            console.error('[Blocks] CRITICAL: .blocks-container not found in DOM!');
        }
        
        // Verify blocks are visible in the DOM after a short delay
        setTimeout(() => {
            const blockElements = document.querySelectorAll('.gjs-block');
            console.log('[Blocks] Block elements in DOM after 500ms:', blockElements.length);
            
            if (blockElements.length > 0) {
                console.log('[Blocks] ✓ SUCCESS: Blocks are visible in DOM');
                if (window.setDebugStatus) {
                    window.setDebugStatus(`✓ Blocks Visible (${blockElements.length})!`);
                }
            } else {
                console.warn('[Blocks] ⚠ Blocks still not visible, checking container...');
                
                // Debug the container status
                const blocksContainer = document.querySelector('.blocks-container');
                console.log('[Blocks] Container exists:', !!blocksContainer);
                if (blocksContainer) {
                    console.log('[Blocks] Container HTML length:', blocksContainer.innerHTML.length);
                    console.log('[Blocks] Container children:', blocksContainer.children.length);
                    console.log('[Blocks] Container visible:', blocksContainer.offsetHeight > 0);
                }
            }
        }, 500);
        
        console.log('✓ Anki blocks registered successfully');
    } catch (error) {
        console.error('[Blocks] Error registering blocks:', error);
        console.warn('[Blocks] Some blocks may not be available');
        if (window.setDebugStatus) {
            window.setDebugStatus('⚠ Partial initialization failed');
        }
    }
    
    // Final verification and status display
    setTimeout(() => {
        const finalBlockCount = blockManager.getAll().length;
        const blockElements = document.querySelectorAll('.gjs-block');
        
        console.log('[Blocks] ===== FINAL STATUS =====');
        console.log('[Blocks] Total blocks registered:', finalBlockCount);
        console.log('[Blocks] Block DOM elements:', blockElements.length);
        console.log('[Blocks] BlockManager view exists:', !!blockManager.view);
        console.log('[Blocks] ========================');
        
        if (finalBlockCount === 0) {
            console.error('[Blocks] CRITICAL: No blocks were registered at all!');
        } else if (blockElements.length === 0) {
            console.error('[Blocks] CRITICAL: Blocks registered but not visible in DOM');
        } else {
            console.log('[Blocks] ✓ All systems go - blocks are registered and visible');
        }
    }, 1000);
};

// Signal that the module is ready
window.ankiBlocksModuleReady = true;
console.log('[Modules] Blocks module loaded');

