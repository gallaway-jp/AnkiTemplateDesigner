/**
 * GrapeJS Editor Initialization and Configuration
 * 
 * Sets up the visual template designer with Anki-specific customizations
 */

// Global editor instance
window.editor = null;
window.availableFields = ['Front', 'Back', 'Extra'];
window.availableBehaviors = [];

function initializeEditor() {
    console.log('[Designer] Initializing GrapeJS editor...');
    
    // Initialize GrapeJS
    window.editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        width: 'auto',
        
        // Storage disabled - we manage it via Python bridge
        storageManager: false,
        
        // Panels configuration
        panels: {
            defaults: [
                {
                    id: 'basic-actions',
                    el: '.panel__basic-actions',
                    buttons: [
                        {
                            id: 'visibility',
                            active: true,
                            className: 'btn-toggle-borders',
                            label: '<i class="fa fa-clone"></i>',
                            command: 'sw-visibility',
                        }
                    ],
                },
                {
                    id: 'panel-devices',
                    el: '.panel__devices',
                    buttons: [
                        {
                            id: 'device-desktop',
                            label: '<i class="fa fa-desktop"></i>',
                            command: 'set-device-desktop',
                            active: true,
                            togglable: false,
                        },
                        {
                            id: 'device-mobile',
                            label: '<i class="fa fa-mobile"></i>',
                            command: 'set-device-mobile',
                            togglable: false,
                        }
                    ],
                }
            ]
        },
        
        // Layer Manager
        layerManager: {
            appendTo: '.layers-container'
        },
        
        // Blocks configuration
        blockManager: {
            appendTo: '.blocks-container',
            blocks: []
        },
        
        // Style Manager
        styleManager: {
            appendTo: '.styles-container',
            sectors: [
                {
                    name: 'Dimension',
                    open: false,
                    buildProps: ['width', 'min-height', 'padding', 'margin'],
                },
                {
                    name: 'Typography',
                    open: false,
                    buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-align'],
                },
                {
                    name: 'Decorations',
                    open: false,
                    buildProps: ['background-color', 'border-radius', 'border', 'box-shadow'],
                },
                {
                    name: 'Extra',
                    open: false,
                    buildProps: ['opacity', 'transition', 'transform'],
                }
            ]
        },
        
        // Trait Manager for component properties
        traitManager: {
            appendTo: '.traits-container',
        },
        
        // Canvas configuration
        canvas: {
            styles: [],
            scripts: [],
        },
        
        // Device Manager for responsive design
        deviceManager: {
            devices: [
                {
                    name: 'Desktop',
                    width: '',
                },
                {
                    name: 'Mobile',
                    width: '320px',
                    widthMedia: '480px',
                }
            ]
        },
        
        // Plugins
        plugins: [],
        pluginsOpts: {}
    });
    
    // Load Anki-specific blocks
    loadAnkiBlocks();
    
    // Setup custom commands
    setupCommands();
    
    // Fetch initial data from Python
    fetchInitialData();
    
    console.log('[Designer] Editor initialized');
    window.log('[Designer] GrapeJS editor ready');
}

function loadAnkiBlocks() {
    const blockManager = window.editor.BlockManager;
    
    // Basic Blocks
    blockManager.add('text', {
        label: 'Text',
        category: 'Basic',
        content: '<div data-gjs-type="text">Insert text here</div>',
        attributes: { class: 'fa fa-text-width' }
    });
    
    blockManager.add('image', {
        label: 'Image',
        category: 'Basic',
        content: { type: 'image' },
        attributes: { class: 'fa fa-image' }
    });
    
    blockManager.add('link', {
        label: 'Link',
        category: 'Basic',
        content: '<a href="#">Link</a>',
        attributes: { class: 'fa fa-link' }
    });
    
    // Anki Field Block
    blockManager.add('anki-field', {
        label: 'Anki Field',
        category: 'Anki',
        content: '<div class="anki-field" data-anki-field="Front">{{Front}}</div>',
        attributes: { class: 'fa fa-bookmark' }
    });
    
    // Layout Blocks
    blockManager.add('container', {
        label: 'Container',
        category: 'Layout',
        content: '<div class="container"></div>',
        attributes: { class: 'fa fa-square-o' }
    });
    
    blockManager.add('row', {
        label: 'Row',
        category: 'Layout',
        content: '<div class="row"><div class="col">Column 1</div><div class="col">Column 2</div></div>',
        attributes: { class: 'fa fa-columns' }
    });
}

function setupCommands() {
    const commands = window.editor.Commands;
    
    // Device switcher commands
    commands.add('set-device-desktop', {
        run: editor => editor.setDevice('Desktop')
    });
    
    commands.add('set-device-mobile', {
        run: editor => editor.setDevice('Mobile')
    });
}

function fetchInitialData() {
    // Request Anki fields from Python
    if (window.bridge) {
        try {
            const fieldsJson = window.bridge.getAnkiFields();
            window.availableFields = JSON.parse(fieldsJson);
            console.log('[Designer] Loaded Anki fields:', window.availableFields);
        } catch (e) {
            console.error('[Designer] Failed to get Anki fields:', e);
        }
        
        try {
            const behaviorsJson = window.bridge.getAnkiBehaviors();
            window.availableBehaviors = JSON.parse(behaviorsJson);
            console.log('[Designer] Loaded behaviors:', window.availableBehaviors.length);
        } catch (e) {
            console.error('[Designer] Failed to get behaviors:', e);
        }
    }
}

// Auto-save every 30 seconds
setInterval(() => {
    if (window.editor && window.bridge) {
        window.saveProject();
        console.log('[Designer] Auto-saved');
    }
}, 30000);
