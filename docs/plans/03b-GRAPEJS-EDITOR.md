# 03b - GrapeJS Editor: Initialization and Configuration

> **Purpose**: Detail GrapeJS editor setup, configuration options, and HTML structure.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

This document covers the GrapeJS editor initialization, configuration, and the main HTML file that hosts the editor inside QWebEngineView.

---

## Main HTML File

### `web/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anki Template Designer</title>
    
    <!-- GrapeJS Core CSS -->
    <link rel="stylesheet" href="grapesjs/grapes.min.css">
    
    <!-- Custom Designer CSS -->
    <link rel="stylesheet" href="designer.css">
    
    <!-- QWebChannel for Python bridge -->
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <!-- GrapeJS Editor Container -->
    <div id="gjs"></div>
    
    <!-- GrapeJS Core JS -->
    <script src="grapesjs/grapes.min.js"></script>
    
    <!-- Custom Blocks -->
    <script src="blocks/index.js"></script>
    
    <!-- Custom Traits -->
    <script src="traits/index.js"></script>
    
    <!-- Anki Plugin -->
    <script src="plugins/anki-plugin.js"></script>
    
    <!-- Python Bridge -->
    <script src="bridge.js"></script>
    
    <!-- Designer Initialization -->
    <script src="designer.js"></script>
</body>
</html>
```

---

## Designer Initialization

### `web/designer.js`

```javascript
/**
 * GrapeJS Editor Initialization for Anki Template Designer
 */

// Global editor instance
let editor = null;

// Python bridge instance (set by bridge.js)
let bridge = null;

/**
 * Initialize GrapeJS editor with Anki-specific configuration
 */
function initEditor() {
    editor = grapesjs.init({
        // Container element
        container: '#gjs',
        
        // Start with empty canvas
        fromElement: false,
        
        // Canvas dimensions (Anki card typical size)
        height: '100%',
        width: 'auto',
        
        // Storage configuration (disabled - we handle via Python)
        storageManager: false,
        
        // Asset manager configuration
        assetManager: {
            embedAsBase64: true,
            upload: false,  // No upload - use Anki's media
            assets: []
        },
        
        // Canvas configuration
        canvas: {
            styles: [
                // Base Anki styles
                'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap'
            ],
            scripts: []
        },
        
        // Panels configuration
        panels: {
            defaults: [
                {
                    id: 'panel-top',
                    el: '.panel__top',
                },
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
                        },
                        {
                            id: 'export',
                            className: 'btn-open-export',
                            label: 'Export',
                            command: 'export-template',
                        },
                        {
                            id: 'preview',
                            className: 'btn-preview',
                            label: 'Preview',
                            command: 'preview-card',
                        }
                    ],
                },
                {
                    id: 'panel-devices',
                    el: '.panel__devices',
                    buttons: [
                        {
                            id: 'device-desktop',
                            label: 'Desktop',
                            command: 'set-device-desktop',
                            active: true,
                            togglable: false,
                        },
                        {
                            id: 'device-mobile',
                            label: 'Mobile',
                            command: 'set-device-mobile',
                            togglable: false,
                        }
                    ],
                },
                {
                    id: 'layers',
                    el: '.panel__right',
                    resizable: {
                        maxDim: 350,
                        minDim: 200,
                        tc: 0, cr: 0, bc: 0, cl: 1,
                    },
                },
                {
                    id: 'panel-switcher',
                    el: '.panel__switcher',
                    buttons: [
                        {
                            id: 'show-layers',
                            active: true,
                            label: 'Layers',
                            command: 'show-layers',
                            togglable: false,
                        },
                        {
                            id: 'show-style',
                            label: 'Styles',
                            command: 'show-styles',
                            togglable: false,
                        },
                        {
                            id: 'show-traits',
                            label: 'Settings',
                            command: 'show-traits',
                            togglable: false,
                        },
                        {
                            id: 'show-blocks',
                            label: 'Blocks',
                            command: 'show-blocks',
                            togglable: false,
                        }
                    ],
                }
            ]
        },
        
        // Layer manager
        layerManager: {
            appendTo: '.layers-container'
        },
        
        // Block manager
        blockManager: {
            appendTo: '.blocks-container',
            blocks: []  // Blocks added by blocks/index.js
        },
        
        // Style manager
        styleManager: {
            appendTo: '.styles-container',
            sectors: getStyleSectors()
        },
        
        // Trait manager (component properties)
        traitManager: {
            appendTo: '.traits-container',
        },
        
        // Selector manager
        selectorManager: {
            appendTo: '.selectors-container'
        },
        
        // Device manager
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
        plugins: [
            'anki-plugin',
            // Add custom block plugins here
        ],
        
        pluginsOpts: {
            'anki-plugin': {
                // Plugin options
            }
        }
    });
    
    // Register custom commands
    registerCommands();
    
    // Register event handlers
    registerEventHandlers();
    
    // Load Anki-specific blocks
    loadAnkiBlocks();
    
    // Notify Python that editor is ready
    if (bridge) {
        bridge.log('Editor initialized');
    }
    
    return editor;
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
    commands.add('show-layers', {
        getRowEl(editor) {
            return editor.getContainer().closest('.editor-row');
        },
        run(editor, sender) {
            const lmEl = editor.Panels.getPanel('layers').el;
            if (lmEl) lmEl.style.display = '';
        },
        stop(editor, sender) {
            const lmEl = editor.Panels.getPanel('layers').el;
            if (lmEl) lmEl.style.display = 'none';
        },
    });
    
    commands.add('show-styles', {
        run(editor, sender) {
            const smEl = document.querySelector('.styles-container');
            if (smEl) smEl.style.display = '';
        },
        stop(editor, sender) {
            const smEl = document.querySelector('.styles-container');
            if (smEl) smEl.style.display = 'none';
        }
    });
    
    commands.add('show-traits', {
        run(editor, sender) {
            const trEl = document.querySelector('.traits-container');
            if (trEl) trEl.style.display = '';
        },
        stop(editor, sender) {
            const trEl = document.querySelector('.traits-container');
            if (trEl) trEl.style.display = 'none';
        }
    });
    
    commands.add('show-blocks', {
        run(editor, sender) {
            const bkEl = document.querySelector('.blocks-container');
            if (bkEl) bkEl.style.display = '';
        },
        stop(editor, sender) {
            const bkEl = document.querySelector('.blocks-container');
            if (bkEl) bkEl.style.display = 'none';
        }
    });
}

/**
 * Register editor event handlers
 */
function registerEventHandlers() {
    // Component selected
    editor.on('component:selected', (component) => {
        console.log('Selected:', component.get('type'));
    });
    
    // Component updated
    editor.on('component:update', (component) => {
        // Auto-save could be triggered here
    });
    
    // Canvas ready
    editor.on('canvas:ready', () => {
        console.log('Canvas ready');
    });
    
    // Handle undo/redo
    editor.on('undo', () => {
        console.log('Undo performed');
    });
    
    editor.on('redo', () => {
        console.log('Redo performed');
    });
}

/**
 * Load Anki-specific component blocks
 * Blocks are defined in blocks/*.js files
 */
function loadAnkiBlocks() {
    // This function is called after blocks/index.js loads
    // which registers all the component blocks
    console.log('Anki blocks loaded');
}

// ============ Public API (called from Python via bridge) ============

/**
 * Save project - called by Python
 */
window.saveProject = function() {
    if (!editor) return;
    const projectData = editor.getProjectData();
    if (window.bridge) {
        window.bridge.saveProject(JSON.stringify(projectData));
    }
};

/**
 * Request preview - called by Python
 */
window.requestPreview = function() {
    if (!editor) return;
    const projectData = editor.getProjectData();
    if (window.bridge) {
        window.bridge.requestPreview(JSON.stringify(projectData));
    }
};

/**
 * Export template - called by Python
 * @param {string} format - Export format (html, json)
 */
window.exportTemplate = function(format) {
    if (!editor) return;
    const projectData = editor.getProjectData();
    if (window.bridge) {
        window.bridge.exportTemplate(format, JSON.stringify(projectData));
    }
};

/**
 * Load template from Python
 * @param {object} projectData - GrapeJS project data
 */
window.loadTemplate = function(projectData) {
    if (!editor) return;
    editor.loadProjectData(projectData);
};

/**
 * Get current project data
 * @returns {object} GrapeJS project data
 */
window.getProjectData = function() {
    if (!editor) return null;
    return editor.getProjectData();
};

/**
 * Get HTML output
 * @returns {string} Generated HTML
 */
window.getHtml = function() {
    if (!editor) return '';
    return editor.getHtml();
};

/**
 * Get CSS output
 * @returns {string} Generated CSS
 */
window.getCss = function() {
    if (!editor) return '';
    return editor.getCss();
};

/**
 * Update available Anki fields
 * @param {string[]} fields - Array of field names
 */
window.updateAnkiFields = function(fields) {
    // Update field selector trait options
    if (editor) {
        editor.getComponents().each((component) => {
            const trait = component.getTrait('anki-field');
            if (trait) {
                trait.set('options', fields.map(f => ({ id: f, name: f })));
            }
        });
    }
};

// ============ Initialization ============

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for bridge to be ready
    initializeBridge(() => {
        initEditor();
    });
});
```

---

## Custom CSS

### `web/designer.css`

```css
/**
 * Custom styles for Anki Template Designer
 */

/* Reset and base styles */
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Editor container */
#gjs {
    height: 100vh;
    width: 100%;
}

/* Panel customizations */
.gjs-one-bg {
    background-color: #1e1e1e;
}

.gjs-two-color {
    color: #ffffff;
}

.gjs-three-bg {
    background-color: #2d2d2d;
}

.gjs-four-color,
.gjs-four-color-h:hover {
    color: #4dabf7;
}

/* Block categories */
.gjs-block-category {
    border-bottom: 1px solid #3d3d3d;
}

.gjs-block-category .gjs-title {
    background-color: #252525;
    color: #cccccc;
    font-weight: 500;
    padding: 10px 15px;
}

/* Blocks */
.gjs-block {
    width: 45%;
    min-height: 70px;
    margin: 5px 2.5%;
    padding: 10px;
    border-radius: 4px;
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    transition: all 0.2s ease;
}

.gjs-block:hover {
    background-color: #3d3d3d;
    border-color: #4dabf7;
}

.gjs-block__media {
    margin-bottom: 5px;
}

.gjs-block-label {
    font-size: 11px;
    color: #cccccc;
}

/* Anki-specific block styling */
.gjs-block[data-category="anki"] {
    border-left: 3px solid #4dabf7;
}

.gjs-block[data-category="layout"] {
    border-left: 3px solid #51cf66;
}

.gjs-block[data-category="input"] {
    border-left: 3px solid #fcc419;
}

.gjs-block[data-category="navigation"] {
    border-left: 3px solid #ff6b6b;
}

/* Traits panel */
.gjs-trt-trait {
    padding: 8px 10px;
    border-bottom: 1px solid #3d3d3d;
}

.gjs-trt-trait__wrp-title {
    color: #aaaaaa;
    font-size: 11px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* Anki field trait */
.gjs-trt-trait[data-trait="anki-field"] {
    background-color: rgba(77, 171, 247, 0.1);
    border-left: 3px solid #4dabf7;
}

/* Anki behavior trait */
.gjs-trt-trait[data-trait="anki-behavior"] {
    background-color: rgba(81, 207, 102, 0.1);
    border-left: 3px solid #51cf66;
}

/* Style manager */
.gjs-sm-sector {
    border-bottom: 1px solid #3d3d3d;
}

.gjs-sm-sector-title {
    background-color: #252525;
    color: #cccccc;
}

/* Layer manager */
.gjs-layer {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
}

.gjs-layer:hover {
    background-color: #3d3d3d;
}

.gjs-layer.gjs-selected {
    background-color: #4dabf7;
}

/* Canvas */
.gjs-cv-canvas {
    background-color: #1a1a1a;
}

/* Frame (design surface) */
.gjs-frame-wrapper {
    background-color: #ffffff;
    border-radius: 4px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Selected component highlight */
.gjs-selected {
    outline: 2px solid #4dabf7 !important;
    outline-offset: -2px;
}

/* Hover highlight */
.gjs-hovered {
    outline: 1px dashed #4dabf7 !important;
}

/* Toolbar */
.gjs-toolbar {
    background-color: #2d2d2d;
    border-radius: 4px;
}

.gjs-toolbar-item {
    color: #ffffff;
}

/* Resizer handles */
.gjs-resizer-h {
    border-color: #4dabf7;
    background-color: #4dabf7;
}

/* Custom Anki field placeholder styling in canvas */
.anki-field-placeholder {
    background-color: rgba(77, 171, 247, 0.2);
    border: 1px dashed #4dabf7;
    padding: 4px 8px;
    border-radius: 4px;
    font-family: monospace;
    color: #4dabf7;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1e1e1e;
}

::-webkit-scrollbar-thumb {
    background: #4d4d4d;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #5d5d5d;
}
```

---

## Keyboard Shortcuts

### Default GrapeJS Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo |
| `Ctrl+C` | Copy component |
| `Ctrl+V` | Paste component |
| `Delete` / `Backspace` | Delete selected |
| `Ctrl+A` | Select all |
| `Escape` | Deselect / Close modal |
| `Ctrl+S` | Save (custom handler) |

### Custom Shortcuts (Added in designer.js)

```javascript
// Add custom keyboard shortcuts
editor.Keymaps.add('custom:save', 'ctrl+s', (editor) => {
    window.saveProject();
});

editor.Keymaps.add('custom:preview', 'ctrl+p', (editor) => {
    window.requestPreview();
});

editor.Keymaps.add('custom:export', 'ctrl+e', (editor) => {
    window.exportTemplate('html');
});
```

---

## Editor API Reference

### Key Methods Used

| Method | Purpose |
|--------|---------|
| `editor.getProjectData()` | Get full project JSON |
| `editor.loadProjectData(data)` | Load project from JSON |
| `editor.getHtml()` | Get HTML output |
| `editor.getCss()` | Get CSS output |
| `editor.getComponents()` | Get all components |
| `editor.getSelected()` | Get selected component |
| `editor.select(component)` | Select a component |
| `editor.runCommand(name)` | Run a command |
| `editor.undo()` | Undo last action |
| `editor.redo()` | Redo last action |

---

## Next Document

See [03c-GRAPEJS-BRIDGE.md](03c-GRAPEJS-BRIDGE.md) for the JavaScript bridge implementation connecting GrapeJS to Python.
