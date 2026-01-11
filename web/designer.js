/**
 * GrapeJS Editor Initialization and Configuration
 * 
 * Sets up the visual template designer with Anki-specific customizations
 */

// Global editor instance
window.editor = null;

/**
 * Initialize the GrapeJS editor
 */
function initializeEditor() {
    console.log('[Designer] Initializing GrapeJS editor...');
    
    try {
        // Check if GrapeJS is available
        if (typeof grapesjs === 'undefined') {
            console.error('[Designer] GrapeJS library not loaded!');
            showError('GrapeJS library failed to load. Please check your installation.');
            return;
        }
        
        console.log('[Designer] GrapeJS library loaded, creating editor...');
        
        // Initialize GrapeJS
        window.editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        width: 'auto',
        
        // Storage disabled - we manage it via Python bridge
        storageManager: false,
        
        // Asset manager disabled - Anki handles media
        assetManager: {
            upload: false,
            embedAsBase64: true
        },
        
        // Canvas configuration
        canvas: {
            styles: [],
            scripts: []
        },
        
        // Layer Manager
        layerManager: {
            appendTo: '.layers-container'
        },
        
        // Block Manager
        blockManager: {
            appendTo: '.blocks-container',
            blocks: []
        },
        
        // Style Manager
        styleManager: {
            appendTo: '.styles-container',
            sectors: getStyleSectors()
        },
        
        // Trait Manager
        traitManager: {
            appendTo: '.traits-container'
        },
        
        // Selector Manager
        selectorManager: {
            appendTo: '.selectors-container'
        },
        
        // Device Manager
        deviceManager: {
            devices: [
                {
                    name: 'Desktop',
                    width: ''
                },
                {
                    name: 'Mobile',
                    width: '320px',
                    widthMedia: '480px'
                }
            ]
        },
        
        // Plugins
        plugins: ['anki-plugin'],
        pluginsOpts: {
            'anki-plugin': {
                validateOnSave: true,
                autoSaveInterval: 30000
            }
        }
    });
    
    // Register custom component types (must be FIRST)
    if (typeof registerComponentTypes === 'function') {
        console.log('[Designer] Registering component types...');
        registerComponentTypes(editor);
        console.log('[Designer] Component types registered');
    } else {
        console.warn('[Designer] registerComponentTypes function not available');
    }
    
    // Register custom traits (must be before blocks)
    if (typeof registerAnkiTraits === 'function') {
        console.log('[Designer] Registering traits...');
        registerAnkiTraits(editor);
        console.log('[Designer] Traits registered');
    } else {
        console.warn('[Designer] registerAnkiTraits function not available');
    }
    
    // Register custom blocks
    if (typeof registerAnkiBlocks === 'function') {
        console.log('[Designer] Registering blocks...');
        registerAnkiBlocks(editor);
        console.log('[Designer] Blocks registered');
    } else {
        console.warn('[Designer] registerAnkiBlocks function not available');
    }
    
    // Setup panels
    setupPanels(editor);
    
    // Register custom commands
    registerCommands();
    
    // Register event handlers
    registerEventHandlers();
    
    console.log('[Designer] Editor initialized');
    window.log('[Designer] GrapeJS editor ready');
    
    } catch (error) {
        console.error('[Designer] Failed to initialize editor:', error);
        showError('Failed to initialize editor: ' + error.message);
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
 * Theme support
 */
window.setTheme = function(theme) {
    console.log('[Designer] Setting theme:', theme);
    document.body.setAttribute('data-theme', theme);
};

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
        initializeEditor();
        setTimeout(hideLoading, 5000);
    });
}
