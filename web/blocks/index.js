/**
 * Anki Custom Blocks for GrapeJS
 * Modular block registration system
 */

import { registerLayoutBlocks } from './layout.js';
import { registerStudyActionBar } from './study-action-bar.js';
import { registerInputBlocks } from './inputs.js';
import { registerButtonBlocks } from './buttons.js';
import { registerDataBlocks } from './data.js';
import { registerFeedbackBlocks } from './feedback.js';
import { registerOverlayBlocks } from './overlays.js';
import { registerAnimationBlocks } from './animations.js';
import { registerAccessibilityBlocks } from './accessibility.js';

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
    registerStudyActionBar(editor);
    
    // Layout & Structure
    registerLayoutBlocks(editor);
    
    // Inputs & Forms
    registerInputBlocks(editor);
    
    // Buttons & Actions
    registerButtonBlocks(editor);
    
    // Data Display
    registerDataBlocks(editor);
    
    // Feedback & Status
    registerFeedbackBlocks(editor);
    
    // Overlays & Popups
    registerOverlayBlocks(editor);
    
    // Animations
    registerAnimationBlocks(editor);
    
    // Accessibility
    registerAccessibilityBlocks(editor);
    
    console.log('✓ Anki blocks registered successfully');
};

// Signal that the module is ready
window.ankiBlocksModuleReady = true;
console.log('[Modules] Blocks module loaded');

