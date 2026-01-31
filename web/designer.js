/**
 * GrapeJS Editor Initialization and Configuration
 * 
 * Sets up the visual template designer with Anki-specific customizations
 */

// Ensure early logging
if (typeof logWithTimestamp === 'undefined') {
    window.logWithTimestamp = (msg) => console.log('[Designer] ' + msg);
}

logWithTimestamp('Designer.js loading');

// Note: tooltipManager and initializeTooltips will be loaded via external script
// Note: initializeUICustomization will be loaded via external script

// Restore theme settings after page fully loads (non-blocking)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(restoreThemeSettings, 100);
    });
} else {
    // Page already loaded, defer theme restoration
    setTimeout(restoreThemeSettings, 100);
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
 * Toast Queue Manager - Handles stacking and lifecycle of toast notifications
 */
const toastManager = {
    queue: [],
    visibleToasts: [],
    maxVisible: 3,
    toastHeight: 80, // Approximate height + margin
    
    /**
     * Add toast to queue and display
     */
    add(message, type = 'info', duration = 3000) {
        const toastId = Date.now() + Math.random();
        const toastObj = { id: toastId, message, type, duration };
        
        this.queue.push(toastObj);
        this.display(toastObj);
        
        console.log(`[Toast] ${type.toUpperCase()}: ${message}`);
        
        return toastId;
    },
    
    /**
     * Display toast with proper stacking
     */
    display(toastObj) {
        // Check if we already have max visible toasts
        if (this.visibleToasts.length >= this.maxVisible) {
            // Auto-dismiss oldest toast
            const oldestId = this.visibleToasts[0];
            this.remove(oldestId);
        }
        
        const toast = document.createElement('div');
        toast.id = `toast-${toastObj.id}`;
        toast.className = `toast toast-${toastObj.type}`;
        toast.setAttribute('role', 'status');
        toast.setAttribute('aria-live', toastObj.type === 'error' ? 'assertive' : 'polite');
        
        // For error toasts, don't add the icon prefix (CSS handles it)
        toast.textContent = toastObj.type === 'error' 
            ? toastObj.message.startsWith('✗') ? toastObj.message : toastObj.message
            : toastObj.message;
        
        // Calculate position based on visible toasts
        const stackIndex = this.visibleToasts.length;
        const bottomOffset = 24 + (stackIndex * this.toastHeight);
        toast.style.setProperty('--stack-index', stackIndex);
        toast.style.bottom = bottomOffset + 'px';
        
        document.body.appendChild(toast);
        this.visibleToasts.push(toastObj.id);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('visible');
        });
        
        // Auto-dismiss after duration
        setTimeout(() => {
            this.remove(toastObj.id);
        }, toastObj.duration);
    },
    
    /**
     * Remove toast from display and queue
     */
    remove(toastId) {
        const toast = document.getElementById(`toast-${toastId}`);
        if (!toast) return;
        
        // Animate out
        toast.classList.remove('visible');
        
        // Remove after animation completes
        setTimeout(() => {
            toast.remove();
            
            // Remove from visible array
            this.visibleToasts = this.visibleToasts.filter(id => id !== toastId);
            
            // Reposition remaining toasts
            this.repositionToasts();
            
            // Process next queue item if available
            const queuedToast = this.queue.find(t => t.id === toastId);
            if (queuedToast) {
                this.queue = this.queue.filter(t => t.id !== toastId);
            }
        }, 300);
    },
    
    /**
     * Reposition all visible toasts with smooth animation
     */
    repositionToasts() {
        this.visibleToasts.forEach((toastId, index) => {
            const toast = document.getElementById(`toast-${toastId}`);
            if (toast) {
                const bottomOffset = 24 + (index * this.toastHeight);
                toast.style.bottom = bottomOffset + 'px';
            }
        });
    },
    
    /**
     * Clear all toasts (useful on page navigation)
     */
    clearAll() {
        this.visibleToasts.forEach(id => this.remove(id));
        this.queue = [];
    }
};

/**
 * Show a toast notification (temporary message) - Public API
 */
function showToast(message, type = 'info', duration = 3000) {
    // Increase duration for errors so users have time to read
    if (type === 'error') {
        duration = Math.max(duration, 5000);
    }
    return toastManager.add(message, type, duration);
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
function updateProgress(step, totalSteps, customMessage = null) {
    const percent = Math.round((step / totalSteps) * 100);
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const statusText = document.getElementById('loading-status');
    
    // Update progress bar width with smooth animation
    if (progressBar) {
        progressBar.style.transition = 'width 0.3s ease-in-out';
        progressBar.style.width = percent + '%';
    }
    
    if (progressText) progressText.textContent = percent + '%';
    
    if (statusText) {
        if (customMessage) {
            statusText.textContent = customMessage;
        } else if (step <= INIT_STEPS.length) {
            statusText.textContent = INIT_STEPS[step - 1].message;
        }
    }
    
    console.log(`[Progress] Step ${step}/${totalSteps}: ${percent}%${customMessage ? ' - ' + customMessage : ''}`);
}

/**
 * Update progress with more granular file loading information
 */
function updateFileLoadingProgress(currentFile, totalFiles, percentComplete) {
    const statusText = document.getElementById('loading-status');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    // Calculate overall progress (assuming file loading is 40-90% of total)
    const baseProgress = 40;
    const fileLoadingRange = 50;
    const overallProgress = baseProgress + (percentComplete / 100) * fileLoadingRange;
    
    if (progressBar) {
        progressBar.style.transition = 'width 0.2s ease-out';
        progressBar.style.width = overallProgress + '%';
    }
    
    if (progressText) {
        progressText.textContent = Math.round(overallProgress) + '%';
    }
    
    if (statusText) {
        statusText.textContent = `Loading files: ${currentFile}/${totalFiles} (${percentComplete}%)`;
    }
    
    console.log(`[File Loading] ${currentFile}/${totalFiles}: ${percentComplete}%`);
}

/**
 * Listen for real-time file loading progress from backend
 */
function initializeFileLoadingProgressListener() {
    if (window.bridge && window.bridge.onFileLoadProgress) {
        window.bridge.onFileLoadProgress((progressData) => {
            if (progressData && typeof progressData.percent !== 'undefined') {
                updateFileLoadingProgress(
                    progressData.current_file || 0,
                    progressData.total_files || 1,
                    progressData.percent
                );
            }
        });
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    console.log('[Designer] Hiding loading overlay...');
    
    // Initialize file loading progress listener for future operations
    initializeFileLoadingProgressListener();
    
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
        console.log('[Designer] Loading overlay hidden');
    } else {
        console.warn('[Designer] Loading element not found');
    }
    
    // Clear any pending initialization timeouts
    if (window.initializationTimeout) {
        clearTimeout(window.initializationTimeout);
    }
}

/**
 * Initialize the GrapeJS editor
 */
function initializeEditor() {
    logWithTimestamp('initializeEditor() called');
    console.log('[Designer] Initializing GrapeJS editor...');
    updateProgress(1, INIT_STEPS.length);
    
    try {
        logWithTimestamp('Checking if grapesjs is defined...');
        // Check if GrapeJS is available
        if (typeof grapesjs === 'undefined') {
            logWithTimestamp('GrapeJS NOT defined!');
            console.error('[Designer] GrapeJS library not loaded!');
            // Attempt to reload GrapeJS
            console.log('[Designer] Attempting to reload GrapeJS...');
            const script = document.createElement('script');
            script.src = 'grapesjs/grapes.min.js';
            script.onload = () => {
                console.log('[Designer] GrapeJS reloaded successfully');
                setTimeout(() => initializeEditor(), 500);
            };
            script.onerror = () => {
                console.error('[Designer] Failed to load GrapeJS');
                showError('GrapeJS library failed to load. Please check your installation.');
                hideLoading();
            };
            document.head.appendChild(script);
            return;
        }
        
        logWithTimestamp('GrapeJS is defined, proceeding with initialization');
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
            
            if (!window.editor) {
                throw new Error('grapesjs.init returned undefined');
            }
            
            console.log('[Designer] ✓ Editor instance created successfully');
        } catch (initError) {
            console.error('ERROR during GrapeJS init: ' + initError.message);
            console.error('Stack: ' + initError.stack);
            console.log('[Designer] ✗ FATAL ERROR - returning from startEditorInit');
            showError('Failed to initialize GrapeJS: ' + initError.message);
            hideLoading();
            return;
        }
        
        console.log('[Designer] Proceeding to configure managers...');
        
        // Configure managers after initialization
        console.log('[Designer] About to configure LayerManager, BlockManager, etc...');
        try {
            if (window.editor.LayerManager) {
                window.editor.LayerManager.getConfig().appendTo = '.layers-container';
            }
            if (window.editor.BlockManager) {
                const blockConfig = window.editor.BlockManager.getConfig();
                blockConfig.appendTo = '.blocks-container';
                console.log('[Designer] BlockManager configured to append to:', blockConfig.appendTo);
                
                // Ensure the BlockManager view is rendered
                // In GrapeJS, we need to explicitly render the blocks view
                try {
                    const blocksContainer = document.querySelector('.blocks-container');
                    if (blocksContainer && window.editor.BlockManager.view) {
                        blocksContainer.innerHTML = '';
                        if (window.editor.BlockManager.render) {
                            window.editor.BlockManager.render();
                            console.log('[Designer] BlockManager view rendered');
                        }
                    }
                } catch (e) {
                    console.warn('[Designer] Could not render BlockManager view:', e.message);
                }
            }
            if (window.editor.StyleManager) {
                window.editor.StyleManager.getConfig().appendTo = '.styles-container';
            }
            if (window.editor.TraitManager) {
                window.editor.TraitManager.getConfig().appendTo = '.traits-container';
            }
        } catch (e) {
            console.warn('[Designer] Could not configure manager targets:', e.message);
        }
        
        console.log('[Designer] Manager configuration complete, setting up devices...');
        
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
        console.log('[Designer] ✓ Devices configured, Managers ready');
        
        // Load anki plugin after editor creation
        console.log('[Designer] Loading anki plugin...');
        updateProgress(7, INIT_STEPS.length);
        try {
            if (typeof ankiPlugin === 'function') {
                ankiPlugin(editor);
            }
        } catch (e) {
            console.warn('[Designer] Could not load anki-plugin:', e.message);
        }
        
        console.log('[Designer] ✓ Anki plugin loaded (or not available)');
        updateProgress(8, INIT_STEPS.length);
    
        // Schedule registration after modules have time to load
        console.log('[Designer] Scheduling registerCustomizations with 100ms timeout...');
        setTimeout(() => {
            console.log('[Designer] setTimeout callback executing - calling registerCustomizations');
            try {
                registerCustomizations(editor);
                updateProgress(9, INIT_STEPS.length);
                
                // Hide loading after a brief moment
                setTimeout(() => {
                    hideLoading();
                    initializeWelcome();  // Show welcome overlay for first-time users
                }, 300);
            } catch (regError) {
                console.error('[Designer] Error during customization registration:', regError);
                hideLoading();
                showError('Failed to register customizations: ' + regError.message);
            }
        }, 100);
    
        console.log('[Designer] Editor initialization sequence started');
    
    } catch (error) {
        console.error('[Designer] Failed to initialize editor:', error);
        console.error('[Designer] Stack:', error.stack);
        showError('Failed to initialize editor: ' + error.message + '\n\nCheck browser console for full stack trace.');
        hideLoading();
    }
}

/**
 * Register all customizations (components, traits, blocks)
 * Called after a delay to allow ES6 modules time to load
 */
function registerCustomizations(editor) {
    console.log('[Designer] *** registerCustomizations() STARTED ***');
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
        
        // Pre-initialize BlockManager view before registering blocks
        console.log('[Designer] Pre-initializing BlockManager before block registration...');
        try {
            if (editor.BlockManager) {
                const blockManager = editor.BlockManager;
                const blocksContainer = document.querySelector('.blocks-container');
                
                // Ensure BlockManager view exists and is appended
                if (blockManager.view && blocksContainer) {
                    const viewEl = blockManager.view.$el || blockManager.view.el;
                    if (viewEl && viewEl.parentElement !== blocksContainer) {
                        console.log('[Designer] Pre-appending BlockManager view to container...');
                        blocksContainer.appendChild(viewEl);
                    }
                }
            }
        } catch (e) {
            console.warn('[Designer] Error pre-initializing BlockManager:', e.message);
        }
        
        // Register custom blocks (async)
        if (typeof registerAnkiBlocks === 'function') {
            console.log('[Designer] Registering blocks...');
            if (window.setDebugStatus) {
                window.setDebugStatus('Registering blocks...');
            }
            registerAnkiBlocks(editor).then(() => {
                console.log('[Designer] Blocks registered');
                showDebug('Step 14: Blocks registered (async)');
                
                // Initialize component search system after blocks are loaded
                if (typeof initializeComponentSearch === 'function') {
                    console.log('[Designer] Initializing component search...');
                    if (window.setDebugStatus) {
                        window.setDebugStatus('✓ Ready!');
                    }
                    initializeComponentSearch(editor);
                    showDebug('Step 14.1: Component search initialized');
                } else {
                    console.warn('[Designer] initializeComponentSearch function not available');
                }
            }).catch(error => {
                console.error('[Designer] Error registering blocks:', error);
                if (window.setDebugStatus) {
                    window.setDebugStatus('❌ Error: ' + error.message);
                }
                showDebug('ERROR: Blocks registration failed');
            });
            showDebug('Step 14: Blocks registration started (async)');
        } else {
            console.warn('[Designer] registerAnkiBlocks function not available');
            if (window.setDebugStatus) {
                window.setDebugStatus('❌ ERROR: registerAnkiBlocks not found');
            }
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
        
        // Initialize data loss prevention system
        if (typeof initializeDataLossPrevention === 'function') {
            console.log('[Designer] Initializing data loss prevention...');
            initializeDataLossPrevention(editor);
            showDebug('Step 19.3: Data loss prevention initialized');
        } else {
            console.warn('[Designer] initializeDataLossPrevention function not available');
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
                label: '🔲 Borders',
                command: 'sw-visibility',
                attributes: { title: 'Toggle element borders' }
            },
            {
                id: 'export',
                className: 'btn-export',
                label: '💾 Export',
                command: 'export-template',
                attributes: { title: 'Export template as HTML' }
            },
            {
                id: 'preview',
                className: 'btn-preview',
                label: '👁 Preview',
                command: 'preview-card',
                attributes: { title: 'Preview card appearance' }
            },
            {
                id: 'validate',
                className: 'btn-validate',
                label: '✓ Validate',
                command: 'validate-template',
                attributes: { title: 'Validate template syntax' }
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
                label: '🖥 Desktop',
                command: 'set-device-desktop',
                active: true,
                togglable: false,
                attributes: { title: 'Desktop view (1920×1080)' }
            },
            {
                id: 'device-mobile',
                label: '📱 Mobile',
                command: 'set-device-mobile',
                togglable: false,
                attributes: { title: 'Mobile view (390×844)' }
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
            showResponsivePreview(editor);
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
 * Show debug message in new debug panel (redirects from old dialog)
 */
function showDebug(message) {
    // Redirect to new debug panel if available
    if (typeof addDebugLog === 'function') {
        const timestamp = new Date().toLocaleTimeString();
        addDebugLog(`[${timestamp}] ${message}`);
    } else {
        // Fallback to console only if debug panel not ready
        console.log('[Debug]', message);
    }
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
 * 
 * NOTE: This is now dynamically populated with i18n translations.
 * Use window.i18nComponentGuide.getTranslatedComponentGuide() instead.
 */
const getComponentGuide = () => {
    // Try to use i18n if available
    if (typeof window.i18nComponentGuide !== 'undefined' && window.i18nComponentGuide.getTranslatedComponentGuide) {
        return window.i18nComponentGuide.getTranslatedComponentGuide();
    }
    
    // Fallback to English
    return {
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
};

// For backward compatibility, provide COMPONENT_GUIDE as a getter that dynamically pulls translations
Object.defineProperty(window, 'COMPONENT_GUIDE', {
    get: getComponentGuide,
    enumerable: true,
    configurable: true
});

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
    
    init(attempt = 0) {
        // Wait for DOM to be ready and editor to have undo manager
        setTimeout(() => {
            this.undoBtn = document.querySelector('[data-action="undo"]');
            this.redoBtn = document.querySelector('[data-action="redo"]');
            
            if (!this.undoBtn || !this.redoBtn) {
                // Only retry a few times (max 10 attempts = 5 seconds total)
                if (attempt < 10) {
                    console.log('[UndoRedo] Buttons not found (attempt ' + (attempt + 1) + '/10), retrying...');
                    setTimeout(() => this.init(attempt + 1), 500);
                } else {
                    console.log('[UndoRedo] Undo/Redo buttons not found after 10 attempts, giving up');
                }
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

/**
 * Show responsive preview modal with device options
 */
function showResponsivePreview(editor) {
    // Create modal HTML
    const modal = document.createElement('div');
    modal.className = 'responsive-preview-modal';
    modal.innerHTML = `
        <div class="preview-modal-overlay" onclick="this.parentElement.remove()"></div>
        <div class="preview-modal-content">
            <div class="preview-modal-header">
                <h2>Responsive Preview</h2>
                <button class="preview-close-btn" onclick="this.closest('.responsive-preview-modal').remove()">✕</button>
            </div>
            <div class="preview-devices">
                <div class="device-selector">
                    <label>Select Device:</label>
                    <select id="device-select" class="device-select">
                        <optgroup label="Mobile">
                            <option value="mobile-375">Mobile (375×667)</option>
                            <option value="mobile-390">iPhone 13 (390×844)</option>
                            <option value="mobile-414">Mobile Large (414×896)</option>
                        </optgroup>
                        <optgroup label="Tablet">
                            <option value="tablet-768">iPad (768×1024)</option>
                            <option value="tablet-1024">iPad Pro (1024×1366)</option>
                        </optgroup>
                        <optgroup label="Desktop">
                            <option value="desktop-1280" selected>Desktop (1280×720)</option>
                            <option value="desktop-1440">Desktop (1440×900)</option>
                            <option value="desktop-1920">Desktop (1920×1080)</option>
                        </optgroup>
                    </select>
                </div>
                <div class="device-controls">
                    <button id="rotate-device" class="device-btn" title="Rotate device">
                        🔄 Rotate
                    </button>
                    <button id="zoom-in" class="device-btn" title="Zoom in">
                        🔍+
                    </button>
                    <button id="zoom-out" class="device-btn" title="Zoom out">
                        🔍-
                    </button>
                    <button id="reset-zoom" class="device-btn" title="Reset zoom">
                        Reset
                    </button>
                </div>
            </div>
            <div class="preview-container">
                <div class="device-frame" id="device-frame">
                    <div class="device-notch"></div>
                    <div class="device-screen" id="device-screen">
                        <iframe id="preview-iframe" class="preview-iframe"></iframe>
                    </div>
                    <div class="device-home-indicator"></div>
                </div>
            </div>
            <div class="preview-info">
                <span id="preview-dims">375 × 667</span>
                <span id="preview-zoom">100%</span>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Device dimensions
    const deviceDimensions = {
        'mobile-375': { width: 375, height: 667, mobile: true },
        'mobile-390': { width: 390, height: 844, mobile: true },
        'mobile-414': { width: 414, height: 896, mobile: true },
        'tablet-768': { width: 768, height: 1024, mobile: false },
        'tablet-1024': { width: 1024, height: 1366, mobile: false },
        'desktop-1280': { width: 1280, height: 720, mobile: false },
        'desktop-1440': { width: 1440, height: 900, mobile: false },
        'desktop-1920': { width: 1920, height: 1080, mobile: false }
    };

    let currentDevice = 'desktop-1280';
    let currentZoom = 100;
    let isLandscape = false;

    const deviceSelect = modal.querySelector('#device-select');
    const frame = modal.querySelector('#device-frame');
    const screen = modal.querySelector('#device-screen');
    const iframe = modal.querySelector('#preview-iframe');
    const rotateBtn = modal.querySelector('#rotate-device');
    const zoomInBtn = modal.querySelector('#zoom-in');
    const zoomOutBtn = modal.querySelector('#zoom-out');
    const resetZoomBtn = modal.querySelector('#reset-zoom');
    const dimsSpan = modal.querySelector('#preview-dims');
    const zoomSpan = modal.querySelector('#preview-zoom');

    function updateDevicePreview() {
        const dims = deviceDimensions[currentDevice];
        if (!dims) return;

        const width = isLandscape ? dims.height : dims.width;
        const height = isLandscape ? dims.width : dims.height;

        screen.style.width = (width * currentZoom / 100) + 'px';
        screen.style.height = (height * currentZoom / 100) + 'px';

        dimsSpan.textContent = `${width} × ${height}`;
        zoomSpan.textContent = `${currentZoom}%`;

        // Add mobile styling
        frame.classList.toggle('is-mobile', deviceDimensions[currentDevice].mobile);
        frame.classList.toggle('landscape', isLandscape);
    }

    function loadPreview() {
        const projectData = editor.getProjectData();
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: system-ui; padding: 16px; }
                </style>
            </head>
            <body>${projectData.html || '<p>No content to preview</p>'}</body>
            </html>
        `;

        iframe.srcdoc = htmlContent;
    }

    deviceSelect.addEventListener('change', (e) => {
        currentDevice = e.target.value;
        isLandscape = false;
        updateDevicePreview();
        loadPreview();
    });

    rotateBtn.addEventListener('click', () => {
        isLandscape = !isLandscape;
        updateDevicePreview();
    });

    zoomInBtn.addEventListener('click', () => {
        currentZoom = Math.min(200, currentZoom + 10);
        updateDevicePreview();
    });

    zoomOutBtn.addEventListener('click', () => {
        currentZoom = Math.max(50, currentZoom - 10);
        updateDevicePreview();
    });

    resetZoomBtn.addEventListener('click', () => {
        currentZoom = 100;
        updateDevicePreview();
    });

    // Initial load
    updateDevicePreview();
    loadPreview();
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

console.log('[Designer] Initialization section reached');

// Make sure logWithTimestamp exists
if (typeof logWithTimestamp === 'undefined') {
    window.logWithTimestamp = (msg) => console.log('[Designer] ' + msg);
}

// Immediately try to initialize the editor
function startEditorInit() {
    console.log('[Designer] startEditorInit() called');
    
    // Check if GrapeJS is available
    if (typeof grapesjs === 'undefined') {
        console.error('[Designer] GrapeJS not available');
        
        // Show visible error
        const msg = document.getElementById('loading-status');
        if (msg) {
            msg.textContent = 'ERROR: GrapeJS library not loaded';
            msg.style.color = '#ff6666';
        }
        
        console.error('[Designer] GrapeJS not available, waiting 500ms and retrying');
        setTimeout(startEditorInit, 500);
        return;
    }
    
    console.log('[Designer] GrapeJS available, initializing editor');
    console.log('[Designer] grapesjs type:', typeof grapesjs);
    console.log('[Designer] grapesjs.init type:', typeof grapesjs.init);
    console.log('[Designer] grapesjs keys:', Object.keys(grapesjs));
    
    try {
        const container = document.getElementById('gjs');
        if (!container) {
            console.error('[Designer] Container #gjs not found');
            return;
        }
        
        console.log('[Designer] Container found, details:');
        console.log('[Designer]   - clientWidth:', container.clientWidth);
        console.log('[Designer]   - clientHeight:', container.clientHeight);
        console.log('[Designer]   - offsetParent:', container.offsetParent);
        console.log('[Designer]   - display:', getComputedStyle(container).display);
        console.log('[Designer]   - visibility:', getComputedStyle(container).visibility);
        
        const config = {
            container: '#gjs',
            height: '100%',
            width: 'auto',
            storageManager: false
        };
        
        console.log('[Designer] About to call grapesjs.init with config:');
        console.log('[Designer]', config);
        
        // Initialize GrapeJS with minimal configuration
        const result = grapesjs.init(config);
        
        console.log('[Designer] grapesjs.init returned:', result);
        console.log('[Designer] Result type:', typeof result);
        console.log('[Designer] Result is falsy?:', !result);
        console.log('[Designer] Result is null?:', result === null);
        console.log('[Designer] Result is undefined?:', result === undefined);
        
        if (result) {
            window.editor = result;
            console.log('[Designer] Editor instance created successfully');
            console.log('[Designer] window.editor type:', typeof window.editor);
            console.log('[Designer] window.editor.getComponents:', typeof window.editor.getComponents);
        } else {
            console.error('[Designer] grapesjs.init() returned falsy value:', result);
            
            // Try to get error from browser console
            console.log('[Designer] Trying alternate init methods...');
            
            // Check if there's an error handler
            try {
                const alt = grapesjs.init({ container: '#gjs' });
                console.log('[Designer] Minimal config result:', alt);
            } catch (altError) {
                console.error('[Designer] Minimal config threw error:', altError);
            }
        }
        
        // Hide loading screen
        if (typeof hideLoading === 'function') {
            hideLoading();
            console.log('[Designer] Loading screen hidden');
        }
        
        // NOW register customizations after editor is ready
        console.log('[Designer] Scheduling registerCustomizations...');
        setTimeout(() => {
            console.log('[Designer] Calling registerCustomizations now');
            if (typeof registerCustomizations === 'function') {
                try {
                    registerCustomizations(window.editor);
                    console.log('[Designer] registerCustomizations completed');
                } catch (regError) {
                    console.error('[Designer] registerCustomizations threw error:', regError);
                }
            } else {
                console.error('[Designer] registerCustomizations not available!');
            }
        }, 100);
        
    } catch (error) {
        console.error('[Designer] EXCEPTION during editor creation:', error);
        console.error('[Designer] Error name:', error.name);
        console.error('[Designer] Error message:', error.message);
        console.error('[Designer] Error stack:', error.stack);
        
        // Store error in window for debugging
        window.editorInitError = error;
        
        // Show error on page
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'position: fixed; top: 10%; left: 5%; right: 5%; background: #ffe6e6; padding: 20px; border: 3px solid red; border-radius: 8px; font-family: monospace; z-index: 9999; max-height: 80%; overflow: auto;';
        errorDiv.innerHTML = '<h2 style="margin: 0 0 10px 0; color: red;">🔴 EXCEPTION DURING INITIALIZATION</h2>' +
            '<p style="margin: 5px 0;"><strong>Error Type:</strong> ' + error.name + '</p>' +
            '<p style="margin: 5px 0;"><strong>Message:</strong> ' + error.message + '</p>' +
            '<p style="margin: 5px 0;"><strong>Stack:</strong></p>' +
            '<pre style="background: #fff; padding: 10px; overflow: auto; max-height: 300px;">' + (error.stack || 'No stack trace') + '</pre>';
        document.body.appendChild(errorDiv);
        
        // Hide loading since we have an error
        if (typeof hideLoading === 'function') {
            hideLoading();
        }
    }
}

// NOTE: Do NOT call startEditorInit() here!
// The index.html page will call startEditorInit() after all scripts are loaded.
// Calling it here would be too early and could cause grapesjs to not be available yet.

console.log('[Designer] Designer script loaded successfully');
