/**
 * GrapeJS Editor Initialization and Configuration
 * 
 * Sets up the visual template designer with Anki-specific customizations
 */

// Import tooltip manager
import { tooltipManager, initializeTooltips } from './tooltips.js';

// Import UI customization
import { initializeUICustomization } from './ui-customization.js';

// Restore theme settings immediately
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', restoreThemeSettings);
} else {
    restoreThemeSettings();
}

// Global editor instance
window.editor = null;

// Save notification handlers
window.notifySaveStart = function() {
    console.log('[Save] Save operation started');
    const saveBtn = document.querySelector('[data-action="save"]');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.classList.add('saving');
        saveBtn.setAttribute('aria-busy', 'true');
    }
    
    // Show save progress toast
    showToast('Saving template...', 'info', 3000);
};

window.notifySaveSuccess = function(templateName) {
    console.log('[Save] Save operation succeeded:', templateName);
    const saveBtn = document.querySelector('[data-action="save"]');
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.classList.remove('saving');
        saveBtn.setAttribute('aria-busy', 'false');
    }
    
    // Show success toast
    showToast(`✓ Template '${templateName}' saved successfully!`, 'success', 4000);
};

window.notifySaveError = function(errorMessage) {
    console.error('[Save] Save operation failed:', errorMessage);
    const saveBtn = document.querySelector('[data-action="save"]');
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.classList.remove('saving');
        saveBtn.setAttribute('aria-busy', 'false');
    }
    
    // Show error toast
    showToast(`✗ Save failed: ${errorMessage}`, 'error', 5000);
};

/**
 * Show a toast notification (temporary message)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Show toast
    requestAnimationFrame(() => {
        toast.classList.add('visible');
    });
    
    // Hide and remove after duration
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
    
    console.log(`[Toast] ${type.toUpperCase()}: ${message}`);
}

// Initialization steps for progress tracking
const INIT_STEPS = [
    { step: 1, message: 'Loading GrapeJS library...' },
    { step: 2, message: 'Creating editor instance...' },
    { step: 3, message: 'Configuring editor...' },
    { step: 4, message: 'Loading component library...' },
    { step: 5, message: 'Setting up traits...' },
    { step: 6, message: 'Registering devices...' },
    { step: 7, message: 'Loading Anki plugin...' },
    { step: 8, message: 'Initializing components...' },
    { step: 9, message: 'Ready!' }
];

/**
 * Update progress bar and status message
 */
function updateProgress(step, totalSteps) {
    const percent = Math.round((step / totalSteps) * 100);
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const statusText = document.getElementById('loading-status');
    
    if (progressBar) progressBar.style.width = percent + '%';
    if (progressText) progressText.textContent = percent + '%';
    if (statusText && step <= INIT_STEPS.length) {
        statusText.textContent = INIT_STEPS[step - 1].message;
    }
    
    console.log(`[Progress] Step ${step}/${totalSteps}: ${percent}%`);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
    }
}

/**
 * Initialize the GrapeJS editor
 */
function initializeEditor() {
    console.log('[Designer] Initializing GrapeJS editor...');
    updateProgress(1, INIT_STEPS.length);
    
    try {
        // Check if GrapeJS is available
        if (typeof grapesjs === 'undefined') {
            console.error('[Designer] GrapeJS library not loaded!');
            showError('GrapeJS library failed to load. Please check your installation.');
            return;
        }
        
        console.log('[Designer] GrapeJS library loaded, creating editor...');
        updateProgress(2, INIT_STEPS.length);
        
        try {
            // Initialize GrapeJS with minimal configuration
            window.editor = grapesjs.init({
                container: '#gjs',
                height: '100%',
                width: 'auto',
                storageManager: false
                // Note: plugins removed - will configure after init
            });
        } catch (initError) {
            console.error('ERROR during init: ' + initError.message);
            throw initError;
        }
        
        updateProgress(3, INIT_STEPS.length);
        console.log('[Designer] Editor created, configuring managers...');
        
        // Configure managers after initialization
        try {
            editor.LayerManager.getConfig().appendTo = '.layers-container';
            editor.BlockManager.getConfig().appendTo = '.blocks-container';
            editor.StyleManager.getConfig().appendTo = '.styles-container';
            editor.TraitManager.getConfig().appendTo = '.traits-container';
        } catch (e) {
            console.warn('[Designer] Could not configure manager targets:', e.message);
        }
        
        // Set up devices
        updateProgress(4, INIT_STEPS.length);
        try {
            editor.setDevice('Desktop');
            if (editor.Devices) {
                const desktopDevice = editor.Devices.get('desktop');
                if (!desktopDevice) {
                    editor.addDevice('Desktop', { width: '' });
                }
                const mobileDevice = editor.Devices.get('mobile');
                if (!mobileDevice) {
                    editor.addDevice('Mobile', { width: '320px', widthMedia: '480px' });
                }
            }
        } catch (e) {
            console.warn('[Designer] Could not configure devices:', e.message);
        }
        
        updateProgress(6, INIT_STEPS.length);
        console.log('[Designer] Managers configured');
        
        // Load anki plugin after editor creation
        updateProgress(7, INIT_STEPS.length);
        try {
            if (typeof ankiPlugin === 'function') {
                ankiPlugin(editor);
            }
        } catch (e) {
            console.warn('[Designer] Could not load anki-plugin:', e.message);
        }
        
        updateProgress(8, INIT_STEPS.length);
    
        // Schedule registration after modules have time to load
        setTimeout(() => {
            registerCustomizations(editor);
            updateProgress(9, INIT_STEPS.length);
            
            // Hide loading after a brief moment
            setTimeout(() => {
                hideLoading();
                initializeWelcome();  // Show welcome overlay for first-time users
            }, 300);
        }, 100);
    
        console.log('[Designer] Editor initialized');
        window.log('[Designer] GrapeJS editor ready');
    
    } catch (error) {
        console.error('[Designer] Failed to initialize editor:', error);
        console.error('[Designer] Stack:', error.stack);
        showError('Failed to initialize editor at: ' + error.message + '\n\nCheck browser console for full stack trace.');
        hideLoading();
    }
}

/**
 * Register all customizations (components, traits, blocks)
 * Called after a delay to allow ES6 modules time to load
 */
function registerCustomizations(editor) {
    try {
        showDebug('Step 11: Modules loaded, registering customizations...');
        
        // Register custom component types (must be FIRST)
        if (typeof registerComponentTypes === 'function') {
            console.log('[Designer] Registering component types...');
            registerComponentTypes(editor);
            console.log('[Designer] Component types registered');
            showDebug('Step 12: Component types registered');
        } else {
            console.warn('[Designer] registerComponentTypes function not available');
            showDebug('WARNING: registerComponentTypes not available');
        }
        
        // Register custom traits (must be before blocks)
        if (typeof registerAnkiTraits === 'function') {
            console.log('[Designer] Registering traits...');
            registerAnkiTraits(editor);
            console.log('[Designer] Traits registered');
            showDebug('Step 13: Traits registered');
        } else {
            console.warn('[Designer] registerAnkiTraits function not available');
            showDebug('WARNING: registerAnkiTraits not available');
        }
        
        // Register custom blocks (async)
        if (typeof registerAnkiBlocks === 'function') {
            console.log('[Designer] Registering blocks...');
            registerAnkiBlocks(editor).then(() => {
                console.log('[Designer] Blocks registered');
                showDebug('Step 14: Blocks registered (async)');
                
                // Initialize component search system after blocks are loaded
                if (typeof initializeComponentSearch === 'function') {
                    console.log('[Designer] Initializing component search...');
                    initializeComponentSearch(editor);
                    showDebug('Step 14.1: Component search initialized');
                } else {
                    console.warn('[Designer] initializeComponentSearch function not available');
                }
            }).catch(error => {
                console.error('[Designer] Error registering blocks:', error);
                showDebug('ERROR: Blocks registration failed');
            });
            showDebug('Step 14: Blocks registration started (async)');
        } else {
            console.warn('[Designer] registerAnkiBlocks function not available');
            showDebug('WARNING: registerAnkiBlocks not available');
        }
        
        // Setup panels
        setupPanels(editor);
        showDebug('Step 15: Panels set up');
        
        // Register custom commands
        registerCommands();
        showDebug('Step 16: Commands registered');
        
        // Register event handlers
        registerEventHandlers();
        showDebug('Step 17: Event handlers registered');
        
        // Setup keyboard shortcuts
        setupKeyboardShortcuts();
        showDebug('Step 18: Keyboard shortcuts registered');
        
        // Initialize component help system
        initializeComponentHelp();
        showDebug('Step 19: Component help system initialized');
        
        // Initialize template validation system
        if (typeof initializeTemplateValidation === 'function') {
            console.log('[Designer] Initializing template validation...');
            initializeTemplateValidation(editor);
            showDebug('Step 19.1: Template validation initialized');
        } else {
            console.warn('[Designer] initializeTemplateValidation function not available');
        }
        
        // Initialize backup manager system
        if (typeof initializeBackupManager === 'function') {
            console.log('[Designer] Initializing backup manager...');
            initializeBackupManager(editor);
            showDebug('Step 19.2: Backup manager initialized');
        } else {
            console.warn('[Designer] initializeBackupManager function not available');
        }
        
        // Initialize undo/redo manager
        initializeUndoRedo();
        showDebug('Step 20: Undo/Redo manager initialized');
        
        // Initialize device preview
        initializeDevicePreview();
        showDebug('Step 21: Device preview initialized');
        
        // Initialize drag & drop feedback
        initializeDragDrop();
        showDebug('Step 22: Drag & drop feedback initialized');
        
        // Initialize template history
        initializeTemplateHistory();
        showDebug('Step 23: Template history initialized');
        
        // Initialize UI customization
        if (typeof initializeUICustomization === 'function') {
            initializeUICustomization(editor);
            showDebug('Step 25: UI Customization initialized');
        }
        
        // Initialize settings button
        initializeSettingsButton();
        showDebug('Step 26: Settings button initialized');
        
        // Initialize tooltips
        initializeTooltips();
        initializeUITooltips();
        showDebug('Step 27: Tooltips initialized');
        
        console.log('[Designer] All customizations loaded');
        hideDebug();
    } catch (error) {
        console.error('[Designer] Failed during customizations:', error);
        showError('Failed to load customizations: ' + error.message);
    }
}

/**
 * Get style manager sector configuration
 */
function getStyleSectors() {
    return [
        {
            name: 'Dimension',
            open: false,
            buildProps: ['width', 'height', 'max-width', 'min-height', 'margin', 'padding']
        },
        {
            name: 'Typography',
            open: false,
            buildProps: [
                'font-family', 'font-size', 'font-weight', 'letter-spacing',
                'color', 'line-height', 'text-align', 'text-decoration',
                'text-transform'
            ]
        },
        {
            name: 'Decorations',
            open: false,
            buildProps: [
                'background-color', 'border-radius', 'border',
                'box-shadow', 'opacity'
            ]
        },
        {
            name: 'Layout',
            open: false,
            buildProps: [
                'display', 'flex-direction', 'justify-content',
                'align-items', 'flex-wrap', 'gap'
            ]
        },
        {
            name: 'Position',
            open: false,
            buildProps: ['position', 'top', 'right', 'bottom', 'left', 'z-index']
        }
    ];
}

/**
 * Setup editor panels and buttons
 */
function setupPanels(editor) {
    const panels = editor.Panels;
    
    // Add top panel
    panels.addPanel({
        id: 'panel-top',
        el: '.panel__top'
    });
    
    // Add basic actions panel with buttons
    panels.addPanel({
        id: 'basic-actions',
        el: '.panel__basic-actions',
        buttons: [
            {
                id: 'visibility',
                active: true,
                className: 'btn-toggle-borders',
                label: '🔲',
                command: 'sw-visibility',
                attributes: { title: 'Toggle borders' }
            },
            {
                id: 'export',
                className: 'btn-export',
                label: '💾',
                command: 'export-template',
                attributes: { title: 'Export template' }
            },
            {
                id: 'preview',
                className: 'btn-preview',
                label: '👁',
                command: 'preview-card',
                attributes: { title: 'Preview card' }
            },
            {
                id: 'validate',
                className: 'btn-validate',
                label: '✓',
                command: 'validate-template',
                attributes: { title: 'Validate template' }
            }
        ]
    });
    
    // Add device switcher panel
    panels.addPanel({
        id: 'panel-devices',
        el: '.panel__devices',
        buttons: [
            {
                id: 'device-desktop',
                label: '🖥',
                command: 'set-device-desktop',
                active: true,
                togglable: false,
                attributes: { title: 'Desktop view' }
            },
            {
                id: 'device-mobile',
                label: '📱',
                command: 'set-device-mobile',
                togglable: false,
                attributes: { title: 'Mobile view' }
            }
        ]
    });
    
    // Add panel switcher (blocks/layers/styles/traits)
    panels.addPanel({
        id: 'panel-switcher',
        el: '.panel__switcher',
        buttons: [
            {
                id: 'show-blocks',
                active: true,
                label: 'Blocks',
                command: 'show-blocks',
                togglable: false
            },
            {
                id: 'show-layers',
                label: 'Layers',
                command: 'show-layers',
                togglable: false
            },
            {
                id: 'show-style',
                label: 'Styles',
                command: 'show-styles',
                togglable: false
            },
            {
                id: 'show-traits',
                label: 'Settings',
                command: 'show-traits',
                togglable: false
            }
        ]
    });
    
    // Add right panel
    panels.addPanel({
        id: 'layers',
        el: '.panel__right',
        resizable: {
            maxDim: 350,
            minDim: 200,
            tc: 0, cr: 0, bc: 0, cl: 1
        }
    });
}

/**
 * Register custom editor commands
 */
function registerCommands() {
    const commands = editor.Commands;
    
    // Export template command
    commands.add('export-template', {
        run(editor) {
            const projectData = editor.getProjectData();
            if (window.bridge) {
                window.bridge.exportTemplate('html', JSON.stringify(projectData));
            }
        }
    });
    
    // Preview card command
    commands.add('preview-card', {
        run(editor) {
            const projectData = editor.getProjectData();
            if (window.bridge) {
                window.bridge.requestPreview(JSON.stringify(projectData));
            }
        }
    });
    
    // Device switching commands
    commands.add('set-device-desktop', {
        run(editor) {
            editor.setDevice('Desktop');
        }
    });
    
    commands.add('set-device-mobile', {
        run(editor) {
            editor.setDevice('Mobile');
        }
    });
    
    // Panel visibility commands
    commands.add('show-blocks', {
        run(editor) {
            showPanel('.blocks-container');
        }
    });
    
    commands.add('show-layers', {
        run(editor) {
            showPanel('.layers-container');
        }
    });
    
    commands.add('show-styles', {
        run(editor) {
            showPanel('.styles-container');
        }
    });
    
    commands.add('show-traits', {
        run(editor) {
            showPanel('.traits-container');
        }
    });
}

/**
 * Show a specific panel and hide others
 */
function showPanel(selector) {
    // Hide all panels
    document.querySelectorAll('.blocks-container, .layers-container, .styles-container, .traits-container').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show selected panel
    const panel = document.querySelector(selector);
    if (panel) {
        panel.style.display = '';
    }
}

/**
 * Register editor event handlers
 */
/**
 * Register editor event handlers
 */
function registerEventHandlers() {
    // Component selected
    editor.on('component:selected', (component) => {
        console.log('[Designer] Selected:', component.get('type'));
    });
    
    // Component updated
    editor.on('component:update', (component) => {
        // Could trigger auto-save here
    });
    
    // Canvas ready
    editor.on('canvas:ready', () => {
        console.log('[Designer] Canvas ready');
        hideLoading();
    });
    
    // Load event - hide loading spinner
    editor.on('load', () => {
        console.log('[Designer] Editor loaded');
        hideLoading();
    });
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
        console.log('[Designer] Loading indicator hidden');
    }
}

/**
 * Show debug message (overlay on the page)
 */
function showDebug(message) {
    let debugDiv = document.getElementById('debug-messages');
    if (!debugDiv) {
        debugDiv = document.createElement('div');
        debugDiv.id = 'debug-messages';
        debugDiv.style.cssText = `
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            max-width: 90%;
            z-index: 20000;
            font-family: monospace;
            font-size: 12px;
            color: #333;
            max-height: 200px;
            overflow-y: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;
        document.body.appendChild(debugDiv);
    }
    
    const timestamp = new Date().toLocaleTimeString();
    debugDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
    debugDiv.scrollTop = debugDiv.scrollHeight;
    console.log('[Debug]', message);
}

/**
 * Hide debug messages
 */
function hideDebug() {
    const debugDiv = document.getElementById('debug-messages');
    if (debugDiv) {
        setTimeout(() => {
            debugDiv.style.display = 'none';
        }, 2000);
    }
}

/**
 * Show error message
 */
function showError(message) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.innerHTML = `
            <h2 style="color: #f44336;">Error Loading Editor</h2>
            <p style="margin-top: 10px; color: var(--text-primary);">${message}</p>
        `;
    }
    console.error('[Designer] Error:', message);
}

/**
 * Theme support - WCAG AAA Compliant
 */
window.setTheme = function(theme) {
    console.log('[Designer] Setting theme:', theme);
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('designer-theme', theme);
};

/**
 * High contrast mode support
 */
window.setHighContrast = function(enabled) {
    console.log('[Designer] Setting high contrast mode:', enabled);
    if (enabled) {
        document.body.setAttribute('data-high-contrast', 'true');
        localStorage.setItem('designer-high-contrast', 'true');
    } else {
        document.body.removeAttribute('data-high-contrast');
        localStorage.setItem('designer-high-contrast', 'false');
    }
};

/**
 * Load saved theme and high contrast settings
 */
function restoreThemeSettings() {
    const savedTheme = localStorage.getItem('designer-theme') || 'light';
    const highContrast = localStorage.getItem('designer-high-contrast') === 'true';
    
    document.body.setAttribute('data-theme', savedTheme);
    if (highContrast) {
        document.body.setAttribute('data-high-contrast', 'true');
    }
    
    console.log('[Designer] Restored theme settings:', { savedTheme, highContrast });
}

/**
 * Keyboard shortcuts configuration
 */
const KEYBOARD_SHORTCUTS = {
    'ctrl+z': {
        name: 'Undo',
        description: 'Undo last change',
        action: 'undo'
    },
    'ctrl+shift+z': {
        name: 'Redo',
        description: 'Redo last undone change',
        action: 'redo'
    },
    'ctrl+s': {
        name: 'Save',
        description: 'Save template to Anki',
        action: 'save'
    },
    'ctrl+e': {
        name: 'Export',
        description: 'Export template as HTML/CSS',
        action: 'export'
    },
    'delete': {
        name: 'Delete',
        description: 'Delete selected component',
        action: 'delete'
    },
    'escape': {
        name: 'Deselect',
        description: 'Deselect current component',
        action: 'deselect'
    },
    '?': {
        name: 'Help',
        description: 'Show keyboard shortcuts',
        action: 'help'
    }
};

/**
 * Component Help Guide - WCAG AAA Accessible Documentation
 * Provides helpful descriptions and usage information for all components
 */
const COMPONENT_GUIDE = {
    // Basic Components
    'text': {
        label: 'Text',
        category: 'Basic',
        description: 'Static text content (not dynamic)',
        help: 'Use for labels, instructions, or static content. Text components display exactly what you type and do not change based on field data.',
        examples: ['Labels', 'Instructions', 'Section headers'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'field': {
        label: 'Field',
        category: 'Basic',
        description: 'Dynamic content from Anki field',
        help: 'Displays the content of an Anki field (front, back, extra, etc.). The actual value depends on what you enter in the card during review.',
        examples: ['Card front', 'Card back', 'Extra info'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'image': {
        label: 'Image',
        category: 'Media',
        description: 'Display images from files',
        help: 'Shows images. You can reference images from your Anki collection media folder, or use base64 encoded data.',
        examples: ['Photos', 'Diagrams', 'Flashcard images'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'video': {
        label: 'Video',
        category: 'Media',
        description: 'Embed video content',
        help: 'Plays video media. Supports common formats like MP4, WebM, and Ogg Theora. Videos will play during review.',
        examples: ['Pronunciation guides', 'Demonstrations', 'Tutorials'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'audio': {
        label: 'Audio',
        category: 'Media',
        description: 'Play audio/sound files',
        help: 'Plays audio content. Perfect for pronunciation guides, vocabulary, language learning. Click to play during review.',
        examples: ['Pronunciation', 'Language lessons', 'Music'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'container': {
        label: 'Container',
        category: 'Layout',
        description: 'Group components together',
        help: 'A box to organize other components. Use containers to create sections and control layout. All styling applies to everything inside.',
        examples: ['Header section', 'Content area', 'Footer'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'row': {
        label: 'Row',
        category: 'Layout',
        description: 'Arrange items horizontally',
        help: 'Places items side-by-side in a row. Items automatically wrap to next line if there is not enough space.',
        examples: ['Two-column layout', 'Buttons in a line', 'Side-by-side images'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'column': {
        label: 'Column',
        category: 'Layout',
        description: 'Arrange items vertically',
        help: 'Stacks items on top of each other. Columns help organize information in a vertical list or section.',
        examples: ['Vertical list', 'Stacked content', 'Info blocks'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'cloze': {
        label: 'Cloze Deletion',
        category: 'Anki Features',
        description: 'Reveal hidden text (fill-in-the-blank)',
        help: 'Creates a cloze deletion - text that is hidden until revealed. Used for {{cloze:FieldName}} in Anki. Essential for cloze card types.',
        examples: ['Fill-in-the-blank questions', 'Study with hints', 'Progressive reveal'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html#cloze-deletion'
    },
    'hint': {
        label: 'Hint',
        category: 'Anki Features',
        description: 'Clickable hint text',
        help: 'Shows hint text that is revealed when clicked. Uses {{hint:FieldName}} in Anki. Great for subtle help without spoiling.',
        examples: ['Hints', 'Clues', 'Study aids'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'conditional': {
        label: 'Conditional',
        category: 'Anki Features',
        description: 'Show/hide based on field content',
        help: 'Shows or hides content based on whether a specific field has content. Uses {{#FieldName}}...{{/FieldName}} syntax.',
        examples: ['Optional fields', 'Extra info sections', 'Conditional content'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html#conditionals'
    },
    'button': {
        label: 'Button',
        category: 'Interactive',
        description: 'Clickable button element',
        help: 'A button for user interaction. Perfect for links, actions, or navigation. Style with colors and shapes.',
        examples: ['Navigation', 'Links', 'Actions'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'link': {
        label: 'Link',
        category: 'Interactive',
        description: 'Hyperlink to URL',
        help: 'Creates a clickable link to a URL or external resource. Great for references and further reading.',
        examples: ['References', 'Sources', 'External links'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'badge': {
        label: 'Badge',
        category: 'Visual',
        description: 'Small informational label',
        help: 'Small tag-like element to label or categorize information. Good for tags, status indicators, or labels.',
        examples: ['Tags', 'Categories', 'Status indicators'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'alert': {
        label: 'Alert',
        category: 'Visual',
        description: 'Highlighted warning/info box',
        help: 'Important notice box that stands out. Use for warnings, important information, or callouts.',
        examples: ['Important notes', 'Warnings', 'Key information'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    },
    'separator': {
        label: 'Separator',
        category: 'Visual',
        description: 'Divider line between sections',
        help: 'A horizontal line to visually separate sections of content. Helps organize and structure information.',
        examples: ['Section breaks', 'Visual dividers', 'Content separation'],
        moreLink: 'https://docs.ankiweb.net/templates/intro.html'
    }
};

/**
 * Device Definitions for Mobile Preview - WCAG Compliant Responsive Design
 */
const DEVICES = {
    DESKTOP: {
        id: 'desktop',
        name: 'Desktop',
        label: 'Desktop (1920×1080)',
        width: 'auto',
        height: 'auto',
        hasFrame: false,
        description: 'Full desktop view'
    },
    IPHONE_13: {
        id: 'iphone-13',
        name: 'iPhone 13',
        label: 'iPhone 13 (390×844)',
        width: 390,
        height: 844,
        hasFrame: true,
        safeArea: { top: 47, bottom: 34, left: 0, right: 0 },
        description: 'Portrait mode with notch'
    },
    IPHONE_13_LANDSCAPE: {
        id: 'iphone-13-landscape',
        name: 'iPhone 13 Landscape',
        label: 'iPhone 13 Landscape (844×390)',
        width: 844,
        height: 390,
        hasFrame: true,
        safeArea: { top: 0, bottom: 24, left: 47, right: 47 },
        description: 'Landscape mode'
    },
    IPAD: {
        id: 'ipad',
        name: 'iPad',
        label: 'iPad (768×1024)',
        width: 768,
        height: 1024,
        hasFrame: true,
        safeArea: { top: 20, bottom: 0, left: 0, right: 0 },
        description: 'Tablet portrait'
    },
    ANDROID_PHONE: {
        id: 'android',
        name: 'Android Phone',
        label: 'Android Phone (360×800)',
        width: 360,
        height: 800,
        hasFrame: true,
        safeArea: { top: 24, bottom: 0, left: 0, right: 0 },
        description: 'Standard Android device'
    }
};

/**
 * Setup keyboard shortcut handling
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Build shortcut string
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        parts.push(e.key.toLowerCase());
        
        const shortcut = parts.join('+');
        const handler = KEYBOARD_SHORTCUTS[shortcut];
        
        if (handler) {
            e.preventDefault();
            handleKeyboardAction(handler.action);
        }
    });
}

/**
 * Handle keyboard shortcut actions
 */
function handleKeyboardAction(action) {
    if (!editor) return;
    
    switch (action) {
        case 'undo':
            if (editor.UndoManager && editor.UndoManager.undo) {
                editor.UndoManager.undo();
                console.log('[Shortcuts] Undo executed');
            }
            break;
        case 'redo':
            if (editor.UndoManager && editor.UndoManager.redo) {
                editor.UndoManager.redo();
                console.log('[Shortcuts] Redo executed');
            }
            break;
        case 'save':
            if (window.bridge && editor.getProjectData) {
                window.bridge.saveProject(JSON.stringify(editor.getProjectData()));
                console.log('[Shortcuts] Save executed');
            }
            break;
        case 'export':
            if (window.bridge && editor.getProjectData) {
                window.bridge.exportTemplate('html', JSON.stringify(editor.getProjectData()));
                console.log('[Shortcuts] Export executed');
            }
            break;
        case 'delete':
            const selected = editor.getSelected && editor.getSelected();
            if (selected && selected.remove) {
                selected.remove();
                console.log('[Shortcuts] Delete executed');
            }
            break;
        case 'deselect':
            if (editor.selectRemove) {
                editor.selectRemove();
                console.log('[Shortcuts] Deselect executed');
            }
            break;
        case 'help':
            showKeyboardHelp();
            break;
    }
}

/**
 * Show keyboard shortcuts help dialog
 */
function showKeyboardHelp() {
    const shortcuts = Object.entries(KEYBOARD_SHORTCUTS)
        .map(([keys, info]) => `${keys.toUpperCase()}: ${info.description}`)
        .join('\n');
    
    const helpText = 'Keyboard Shortcuts:\n\n' + shortcuts;
    alert(helpText);
}

/**
 * Handle help link clicks in welcome overlay
 */
function handleHelpClick() {
    showKeyboardHelp();
}

/**
 * Component Help Manager - Displays help for components on hover
 */
class ComponentHelpManager {
    constructor() {
        this.helpPanel = null;
        this.currentComponent = null;
        this.setupHelpPanel();
    }
    
    setupHelpPanel() {
        // Create help panel if it doesn't exist
        if (!document.getElementById('component-help-panel')) {
            const panel = document.createElement('div');
            panel.id = 'component-help-panel';
            panel.className = 'help-panel hidden';
            panel.innerHTML = `
                <button class="help-panel-close" aria-label="Close help panel">&times;</button>
                <div class="help-panel-content">
                    <h3 class="help-panel-title" id="help-title">Component Help</h3>
                    <p class="help-panel-description" id="help-description"></p>
                    <div class="help-panel-examples" id="help-examples"></div>
                    <a class="help-panel-link" id="help-link" href="#" target="_blank" rel="noopener noreferrer">Learn more</a>
                </div>
            `;
            document.body.appendChild(panel);
            
            // Close button handler
            panel.querySelector('.help-panel-close').addEventListener('click', () => this.hide());
        }
        
        this.helpPanel = document.getElementById('component-help-panel');
    }
    
    show(componentId) {
        const guide = COMPONENT_GUIDE[componentId];
        if (!guide) return;
        
        const panel = this.helpPanel;
        document.getElementById('help-title').textContent = guide.label;
        document.getElementById('help-description').textContent = guide.help;
        
        // Build examples list
        const examplesDiv = document.getElementById('help-examples');
        if (guide.examples && guide.examples.length > 0) {
            examplesDiv.innerHTML = `<p><strong>Examples:</strong> ${guide.examples.join(', ')}</p>`;
        }
        
        // Set learn more link
        const link = document.getElementById('help-link');
        if (guide.moreLink) {
            link.href = guide.moreLink;
            link.style.display = 'block';
        } else {
            link.style.display = 'none';
        }
        
        panel.classList.remove('hidden');
        this.currentComponent = componentId;
    }
    
    hide() {
        if (this.helpPanel) {
            this.helpPanel.classList.add('hidden');
        }
        this.currentComponent = null;
    }
}

// Global help manager instance
window.componentHelpManager = null;

function initializeComponentHelp() {
    if (!window.componentHelpManager) {
        window.componentHelpManager = new ComponentHelpManager();
    }
}

/**
 * Undo/Redo Manager - Tracks and displays undo/redo button state
 */
class UndoRedoManager {
    constructor(editor) {
        this.editor = editor;
        this.undoBtn = null;
        this.redoBtn = null;
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready and editor to have undo manager
        setTimeout(() => {
            this.undoBtn = document.querySelector('[data-action="undo"]');
            this.redoBtn = document.querySelector('[data-action="redo"]');
            
            if (!this.undoBtn || !this.redoBtn) {
                console.warn('[UndoRedo] Undo/Redo buttons not found, trying again...');
                setTimeout(() => this.init(), 500);
                return;
            }
            
            // Add click handlers
            this.undoBtn.addEventListener('click', (e) => this.handleUndo(e));
            this.redoBtn.addEventListener('click', (e) => this.handleRedo(e));
            
            // Monitor editor changes to update button state
            if (this.editor) {
                this.editor.on('change', () => this.updateButtonState());
                this.editor.on('undo', () => this.notifyUndo());
                this.editor.on('redo', () => this.notifyRedo());
            }
            
            // Initial state
            this.updateButtonState();
            
            console.log('[UndoRedo] Manager initialized');
        }, 500);
    }
    
    updateButtonState() {
        if (!this.undoBtn || !this.redoBtn) return;
        
        // Get undo/redo availability from editor
        const hasUndo = this.editor && this.editor.UndoManager && this.editor.UndoManager.hasUndo();
        const hasRedo = this.editor && this.editor.UndoManager && this.editor.UndoManager.hasRedo();
        
        // Update button states
        this.undoBtn.disabled = !hasUndo;
        this.redoBtn.disabled = !hasRedo;
        
        // Update aria-disabled for accessibility
        this.undoBtn.setAttribute('aria-disabled', !hasUndo ? 'true' : 'false');
        this.redoBtn.setAttribute('aria-disabled', !hasRedo ? 'true' : 'false');
        
        // Update visual state
        if (hasUndo) {
            this.undoBtn.classList.remove('disabled');
        } else {
            this.undoBtn.classList.add('disabled');
        }
        
        if (hasRedo) {
            this.redoBtn.classList.remove('disabled');
        } else {
            this.redoBtn.classList.add('disabled');
        }
    }
    
    handleUndo(event) {
        event.preventDefault();
        if (this.editor && this.editor.UndoManager && this.editor.UndoManager.hasUndo()) {
            this.editor.UndoManager.undo();
            this.updateButtonState();
        }
    }
    
    handleRedo(event) {
        event.preventDefault();
        if (this.editor && this.editor.UndoManager && this.editor.UndoManager.hasRedo()) {
            this.editor.UndoManager.redo();
            this.updateButtonState();
        }
    }
    
    notifyUndo() {
        showToast('↶ Undo', 'info', 2000);
        this.updateButtonState();
    }
    
    notifyRedo() {
        showToast('↷ Redo', 'info', 2000);
        this.updateButtonState();
    }
}

// Global undo/redo manager instance
window.undoRedoManager = null;

function initializeUndoRedo() {
    if (!window.undoRedoManager && window.editor) {
        window.undoRedoManager = new UndoRedoManager(window.editor);
        console.log('[UndoRedo] Manager created');
    }
}

/**
 * Device Preview Manager - Responsive design testing
 */
class DevicePreviewManager {
    constructor(editor) {
        this.editor = editor;
        this.currentDevice = DEVICES.DESKTOP;
        this.previewContainer = null;
        this.init();
    }
    
    init() {
        this.setupDeviceButtons();
        this.setupPreviewContainer();
    }
    
    setupDeviceButtons() {
        // Create device preview toolbar
        const toolbar = document.querySelector('.panel__top');
        if (!toolbar) return;
        
        const deviceButtons = document.createElement('div');
        deviceButtons.className = 'device-preview-buttons';
        deviceButtons.setAttribute('role', 'group');
        deviceButtons.setAttribute('aria-label', 'Device preview options');
        
        // Add buttons for each device
        Object.values(DEVICES).forEach(device => {
            const btn = document.createElement('button');
            btn.className = 'device-btn';
            btn.textContent = device.name;
            btn.title = device.description;
            btn.setAttribute('data-device', device.id);
            btn.setAttribute('aria-pressed', 'false');
            
            if (device.id === 'desktop') {
                btn.setAttribute('aria-pressed', 'true');
                btn.classList.add('active');
            }
            
            btn.addEventListener('click', () => this.switchDevice(device));
            deviceButtons.appendChild(btn);
        });
        
        toolbar.appendChild(deviceButtons);
        console.log('[DevicePreview] Device buttons created');
    }
    
    setupPreviewContainer() {
        // Create container for device frames
        const canvas = document.querySelector('#gjs');
        if (!canvas) return;
        
        const container = document.createElement('div');
        container.className = 'device-preview-container';
        canvas.parentElement.insertBefore(container, canvas);
        
        this.previewContainer = container;
    }
    
    switchDevice(device) {
        this.currentDevice = device;
        
        // Update button states
        document.querySelectorAll('.device-btn').forEach(btn => {
            const isActive = btn.getAttribute('data-device') === device.id;
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
            btn.classList.toggle('active', isActive);
        });
        
        // Update canvas
        this.updateCanvasSize(device);
        
        showToast(`📱 Preview: ${device.label}`, 'info', 2000);
        console.log('[DevicePreview] Switched to', device.name);
    }
    
    updateCanvasSize(device) {
        if (!this.editor || !this.editor.Canvas) return;
        
        const canvas = document.querySelector('#gjs');
        const frame = document.querySelector('.gjs-frame');
        
        if (device.id === 'desktop') {
            // Reset to auto size
            if (canvas) {
                canvas.style.width = 'auto';
                canvas.style.height = 'auto';
            }
            if (frame) {
                frame.style.width = 'auto';
                frame.style.height = 'auto';
            }
        } else {
            // Set specific device size
            if (canvas) {
                canvas.style.width = device.width + 'px';
                canvas.style.height = device.height + 'px';
            }
            if (frame) {
                frame.style.width = device.width + 'px';
                frame.style.height = device.height + 'px';
            }
        }
    }
}

// Global device preview manager
window.devicePreviewManager = null;

/**
 * Drag & Drop Visual Feedback Manager
 * Provides visual feedback during drag and drop operations
 */
class DragDropManager {
    constructor(editor) {
        this.editor = editor;
        this.draggedElement = null;
        this.dropZones = [];
        this.dragImage = null;
        this.init();
    }
    
    init() {
        // Setup drag event listeners on editor
        if (!this.editor) return;
        
        // Monitor drag operations
        this.editor.on('component:drag:start', (e) => this.handleDragStart(e));
        this.editor.on('component:drag', (e) => this.handleDragMove(e));
        this.editor.on('component:drag:end', (e) => this.handleDragEnd(e));
        
        // Monitor drop zones
        this.setupDropZones();
        
        console.log('[DragDrop] Manager initialized');
    }
    
    setupDropZones() {
        // Setup drag enter/leave/drop on main canvas
        const canvas = document.querySelector('#gjs');
        if (!canvas) return;
        
        canvas.addEventListener('dragenter', (e) => this.handleDragEnter(e), false);
        canvas.addEventListener('dragover', (e) => this.handleDragOver(e), false);
        canvas.addEventListener('dragleave', (e) => this.handleDragLeave(e), false);
        canvas.addEventListener('drop', (e) => this.handleDrop(e), false);
        
        // Setup drag listeners on components panel
        const blocksPanel = document.querySelector('.blocks-container');
        if (blocksPanel) {
            blocksPanel.addEventListener('dragstart', (e) => this.handleBlockDragStart(e), false);
        }
    }
    
    handleDragStart(event) {
        console.log('[DragDrop] Drag started');
        this.draggedElement = event.target;
        
        // Create visual feedback
        this.showDragFeedback();
        
        // Mark dragged element
        if (this.draggedElement && this.draggedElement.el) {
            this.draggedElement.el.classList.add('dragging');
        }
        
        // Show drop zones
        this.highlightDropZones();
        
        showToast('🖱️ Dragging component...', 'info', 3000);
    }
    
    handleDragMove(event) {
        // Update drag feedback position (if needed)
        if (this.dragImage) {
            // Could animate feedback here
        }
    }
    
    handleDragEnd(event) {
        console.log('[DragDrop] Drag ended');
        
        // Clean up visual feedback
        this.clearDragFeedback();
        
        if (this.draggedElement && this.draggedElement.el) {
            this.draggedElement.el.classList.remove('dragging');
        }
        
        // Hide drop zones
        this.clearDropZoneHighlights();
    }
    
    handleDragEnter(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        
        // Highlight drop zone
        const canvas = document.querySelector('#gjs');
        if (canvas) {
            canvas.classList.add('drag-over');
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        return false;
    }
    
    handleDragLeave(event) {
        // Check if we're leaving the canvas entirely
        const canvas = document.querySelector('#gjs');
        if (event.target === canvas) {
            canvas.classList.remove('drag-over');
        }
    }
    
    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const canvas = document.querySelector('#gjs');
        if (canvas) {
            canvas.classList.remove('drag-over');
        }
        
        console.log('[DragDrop] Drop successful');
        showToast('✓ Component dropped successfully!', 'success', 2000);
        
        return false;
    }
    
    handleBlockDragStart(event) {
        // Visual feedback when dragging from blocks panel
        const block = event.target.closest('[data-gjs-block]');
        if (block) {
            console.log('[DragDrop] Block drag started');
            
            // Create custom drag image
            const dragImage = document.createElement('div');
            dragImage.className = 'drag-preview';
            dragImage.textContent = block.textContent.trim();
            document.body.appendChild(dragImage);
            
            event.dataTransfer.setDragImage(dragImage, 0, 0);
            
            // Clean up after drag
            setTimeout(() => dragImage.remove(), 0);
        }
    }
    
    showDragFeedback() {
        // Create visual feedback during drag
        const feedback = document.createElement('div');
        feedback.className = 'drag-feedback';
        feedback.id = 'drag-feedback-overlay';
        document.body.appendChild(feedback);
        
        this.dragImage = feedback;
    }
    
    clearDragFeedback() {
        if (this.dragImage) {
            this.dragImage.remove();
            this.dragImage = null;
        }
    }
    
    highlightDropZones() {
        // Highlight areas where components can be dropped
        const zones = document.querySelectorAll('.gjs-frame, .gjs-row, [data-gjs-type="default"]');
        zones.forEach(zone => {
            zone.classList.add('drop-zone-active');
        });
    }
    
    clearDropZoneHighlights() {
        const zones = document.querySelectorAll('.drop-zone-active');
        zones.forEach(zone => {
            zone.classList.remove('drop-zone-active');
        });
    }
}

// Global drag/drop manager
window.dragDropManager = null;

function initializeDragDrop() {
    if (!window.dragDropManager && window.editor) {
        window.dragDropManager = new DragDropManager(window.editor);
        console.log('[DragDrop] Manager created');
    }
}

/**
 * Template History Manager - Track and recover template versions
 */
class TemplateHistoryManager {
    constructor(editor) {
        this.editor = editor;
        this.history = [];
        this.maxHistorySize = 20;  // Keep last 20 versions
        this.currentIndex = -1;
        this.historyPanel = null;
        this.init();
    }
    
    init() {
        this.setupHistoryPanel();
        this.setupHistoryTracking();
        console.log('[TemplateHistory] Manager initialized');
    }
    
    setupHistoryPanel() {
        // Create history sidebar panel
        if (document.getElementById('template-history-panel')) {
            this.historyPanel = document.getElementById('template-history-panel');
            return;
        }
        
        const panel = document.createElement('div');
        panel.id = 'template-history-panel';
        panel.className = 'history-panel hidden';
        panel.setAttribute('role', 'region');
        panel.setAttribute('aria-label', 'Template version history');
        panel.innerHTML = `
            <div class="history-panel-header">
                <h3>Template History</h3>
                <button class="history-panel-close" aria-label="Close history panel">&times;</button>
            </div>
            <div class="history-panel-content">
                <div class="history-list" id="history-list"></div>
            </div>
        `;
        document.body.appendChild(panel);
        
        // Close button
        panel.querySelector('.history-panel-close').addEventListener('click', () => {
            this.hideHistory();
        });
        
        this.historyPanel = panel;
    }
    
    setupHistoryTracking() {
        // Track template changes
        if (!this.editor) return;
        
        // Capture state on significant changes
        this.editor.on('change', () => {
            this.captureSnapshot();
        });
        
        // Capture on component updates
        this.editor.on('component:create', () => this.captureSnapshot());
        this.editor.on('component:remove', () => this.captureSnapshot());
        this.editor.on('component:update', () => this.captureSnapshot());
    }
    
    captureSnapshot() {
        try {
            if (!this.editor) return;
            
            // Get current editor state
            const data = this.editor.getProjectData();
            const timestamp = new Date();
            
            // Create snapshot
            const snapshot = {
                id: Date.now(),
                timestamp: timestamp,
                label: `${timestamp.toLocaleTimeString()}`,
                data: JSON.stringify(data),  // Store as string for memory efficiency
                size: data ? JSON.stringify(data).length : 0
            };
            
            // Remove any "future" history if we're not at the end
            if (this.currentIndex < this.history.length - 1) {
                this.history = this.history.slice(0, this.currentIndex + 1);
            }
            
            // Add new snapshot
            this.history.push(snapshot);
            this.currentIndex++;
            
            // Enforce size limit
            if (this.history.length > this.maxHistorySize) {
                this.history.shift();  // Remove oldest
                this.currentIndex--;
            }
            
            console.log(`[TemplateHistory] Snapshot captured (${this.history.length}/${this.maxHistorySize})`);
            
        } catch (e) {
            console.error('[TemplateHistory] Error capturing snapshot:', e);
        }
    }
    
    showHistory() {
        if (!this.historyPanel) return;
        
        this.historyPanel.classList.remove('hidden');
        this.updateHistoryList();
    }
    
    hideHistory() {
        if (this.historyPanel) {
            this.historyPanel.classList.add('hidden');
        }
    }
    
    updateHistoryList() {
        const listContainer = document.getElementById('history-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        if (this.history.length === 0) {
            listContainer.innerHTML = '<p class="history-empty">No history yet</p>';
            return;
        }
        
        // Show history in reverse (newest first)
        this.history.slice().reverse().forEach((snapshot, index) => {
            const reverseIndex = this.history.length - 1 - index;
            const isActive = reverseIndex === this.currentIndex;
            
            const item = document.createElement('button');
            item.className = `history-item ${isActive ? 'active' : ''}`;
            item.setAttribute('aria-pressed', isActive ? 'true' : 'false');
            item.innerHTML = `
                <span class="history-time">${snapshot.label}</span>
                <span class="history-size">${(snapshot.size / 1024).toFixed(1)}KB</span>
            `;
            
            item.addEventListener('click', () => this.restoreSnapshot(reverseIndex));
            listContainer.appendChild(item);
        });
    }
    
    restoreSnapshot(index) {
        try {
            if (index < 0 || index >= this.history.length) {
                showToast('Invalid history index', 'error', 2000);
                return;
            }
            
            const snapshot = this.history[index];
            const data = JSON.parse(snapshot.data);
            
            // Restore editor state
            if (this.editor) {
                this.editor.setProjectData(data);
                this.currentIndex = index;
                this.updateHistoryList();
                
                showToast(`↶ Restored: ${snapshot.label}`, 'success', 3000);
                console.log('[TemplateHistory] Snapshot restored:', index);
            }
        } catch (e) {
            console.error('[TemplateHistory] Error restoring snapshot:', e);
            showToast('Failed to restore template version', 'error', 3000);
        }
    }
    
    toggleHistory() {
        if (this.historyPanel && this.historyPanel.classList.contains('hidden')) {
            this.showHistory();
        } else {
            this.hideHistory();
        }
    }
}

// Global template history manager
window.templateHistoryManager = null;

function initializeTemplateHistory() {
    if (!window.templateHistoryManager && window.editor) {
        window.templateHistoryManager = new TemplateHistoryManager(window.editor);
        console.log('[TemplateHistory] Manager created');
    }
}

function initializeDevicePreview() {
    if (!window.devicePreviewManager && window.editor) {
        window.devicePreviewManager = new DevicePreviewManager(window.editor);
        console.log('[DevicePreview] Manager created');
    }
}

/**
 * Initialize welcome overlay on first load
 */
function initializeWelcome() {
    const welcomeOverlay = document.getElementById('welcome-overlay');
    const closeBtn = document.getElementById('close-welcome');
    const getStartedBtn = document.getElementById('get-started');
    const showAgainCheckbox = document.getElementById('show-welcome-again');
    
    if (!welcomeOverlay) return;
    
    // Check if user has seen welcome before
    const hasSeenWelcome = localStorage.getItem('ankidesigner_welcome_seen');
    
    // Show welcome if not seen before
    if (!hasSeenWelcome) {
        welcomeOverlay.classList.remove('hidden');
    }
    
    // Close welcome function
    function closeWelcome() {
        welcomeOverlay.classList.add('hidden');
        
        // Save preference
        const showAgain = showAgainCheckbox?.checked ?? false;
        if (!showAgain) {
            localStorage.setItem('ankidesigner_welcome_seen', 'true');
        }
    }
    
    // Event listeners
    closeBtn?.addEventListener('click', closeWelcome);
    getStartedBtn?.addEventListener('click', closeWelcome);
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !welcomeOverlay.classList.contains('hidden')) {
            closeWelcome();
        }
    });
}

/**
 * Initialize settings button for UI customization
 */
function initializeSettingsButton() {
    const settingsBtn = document.getElementById('settings-button');
    if (!settingsBtn) {
        console.warn('[Settings] Settings button not found');
        return;
    }

    settingsBtn.addEventListener('click', () => {
        if (window.customizationManager) {
            window.customizationManager.toggleSettings();
        }
    });

    // Add tooltip
    tooltipManager.addTooltip(settingsBtn, 'Customize interface: panels, buttons, layout', { position: 'left' });

    console.log('[Settings] Settings button initialized');
}

/**
 * Initialize tooltips on UI buttons and controls
 */
function initializeUITooltips() {
    try {
        console.log('[Tooltips] Initializing UI tooltips...');
        
        // Add tooltips to basic action buttons
        const basicActions = [
            { selector: '[data-action="save"]', text: 'Save template to Anki' },
            { selector: '[data-action="export"]', text: 'Export template as HTML' },
            { selector: '[data-action="preview"]', text: 'Preview card appearance' },
            { selector: '[data-action="validate"]', text: 'Validate template syntax' },
            { selector: '[data-action="undo"]', text: 'Undo last change (Ctrl+Z)' },
            { selector: '[data-action="redo"]', text: 'Redo last change (Ctrl+Shift+Z)' }
        ];
        
        basicActions.forEach(({ selector, text }) => {
            const element = document.querySelector(selector);
            if (element) {
                tooltipManager.addTooltip(element, text, { position: 'bottom' });
                console.log(`[Tooltips] Added tooltip to ${selector}`);
            }
        });
        
        // Add tooltips to device buttons
        setTimeout(() => {
            const deviceButtons = document.querySelectorAll('[data-device]');
            deviceButtons.forEach((btn) => {
                const device = btn.getAttribute('data-device');
                const tooltips = {
                    'desktop': 'View on desktop (1920×1080)',
                    'iphone-13': 'View on iPhone 13 (390×844)',
                    'iphone-13-landscape': 'View on iPhone 13 Landscape (844×390)',
                    'ipad': 'View on iPad (768×1024)',
                    'android': 'View on Android Phone (360×800)'
                };
                
                if (tooltips[device] && !btn.querySelector('.tooltip-trigger')) {
                    tooltipManager.addTooltip(btn, tooltips[device], { position: 'bottom' });
                    console.log(`[Tooltips] Added tooltip to device button: ${device}`);
                }
            });
        }, 500);
        
        // Add tooltips to panel switcher buttons
        setTimeout(() => {
            const panelButtons = [
                { selector: '[data-panel="blocks"]', text: 'Browse available components' },
                { selector: '[data-panel="layers"]', text: 'View component hierarchy' },
                { selector: '[data-panel="styles"]', text: 'Edit CSS styles' },
                { selector: '[data-panel="traits"]', text: 'Configure component properties' }
            ];
            
            panelButtons.forEach(({ selector, text }) => {
                const element = document.querySelector(selector);
                if (element && !element.querySelector('.tooltip-trigger')) {
                    tooltipManager.addTooltip(element, text, { position: 'bottom' });
                    console.log(`[Tooltips] Added tooltip to ${selector}`);
                }
            });
        }, 500);
        
        // Add tooltip to history button
        setTimeout(() => {
            const historyBtn = document.querySelector('[data-action="history"]');
            if (historyBtn && !historyBtn.querySelector('.tooltip-trigger')) {
                tooltipManager.addTooltip(historyBtn, 'View template version history', { position: 'bottom' });
                console.log('[Tooltips] Added tooltip to history button');
            }
        }, 500);
        
        console.log('[Tooltips] UI tooltips initialization complete');
    } catch (error) {
        console.error('[Tooltips] Error initializing UI tooltips:', error);
    }
}

// ========== Initialization ========== 

// Wait for bridge to be ready, then initialize editor
if (typeof initializeBridge === 'function') {
    initializeBridge(() => {
        initializeEditor();
        // Fallback timeout to hide loading if editor doesn't fully initialize
        setTimeout(hideLoading, 5000);
    });
} else {
    // Fallback if bridge.js not loaded
    console.warn('[Designer] bridge.js not loaded, initializing without bridge');
    document.addEventListener('DOMContentLoaded', () => {
        restoreThemeSettings();
        initializeEditor();
        setTimeout(hideLoading, 5000);
    });
}
