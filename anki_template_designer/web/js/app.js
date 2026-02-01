/**
 * Main Application
 * Initialization and event handlers
 */

// Settings Modal Functions
function openSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.remove('hidden');
        loadCurrentSettings();
    }
}

function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function loadCurrentSettings() {
    // Load settings from bridge
    if (window.bridge && window.bridge.getConfig) {
        window.bridge.getConfig((config) => {
            console.log('Loaded config:', config);
            document.getElementById('autoSaveCheckbox').checked = config.autoSave !== false;
            document.getElementById('autoSaveInterval').value = config.autoSaveIntervalSeconds || 30;
            document.getElementById('themeSelect').value = config.theme || 'system';
            document.getElementById('logLevelSelect').value = config.logLevel || 'INFO';
        });
    }
}

function saveSettings() {
    const autoSave = document.getElementById('autoSaveCheckbox').checked;
    const autoSaveInterval = parseInt(document.getElementById('autoSaveInterval').value) || 30;
    const theme = document.getElementById('themeSelect').value;
    const logLevel = document.getElementById('logLevelSelect').value;
    
    const settings = {
        autoSave: autoSave,
        autoSaveIntervalSeconds: autoSaveInterval,
        theme: theme,
        logLevel: logLevel
    };
    
    console.log('Saving settings:', settings);
    
    if (window.bridge && window.bridge.setConfig) {
        // Save each setting
        const settingsToSave = [
            { key: 'autoSave', value: String(autoSave) },
            { key: 'autoSaveIntervalSeconds', value: String(autoSaveInterval) },
            { key: 'theme', value: theme },
            { key: 'logLevel', value: logLevel }
        ];
        
        let saved = 0;
        settingsToSave.forEach((setting) => {
            window.bridge.setConfig(setting.key, setting.value, (result) => {
                saved++;
                if (saved === settingsToSave.length) {
                    window.debugUtils.showErrorToast('Settings', 'Settings saved successfully', 'success');
                    closeSettingsModal();
                }
            });
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Bridge not ready', 'error');
    }
}

// Toolbar button handlers
function handleSave() {
    console.log('Save clicked');
    if (window.bridge && window.bridge.save_template) {
        window.debugUtils.showErrorToast('Save', 'Saving template...', 'info');
        window.bridge.save_template((result) => {
            console.log('Save result:', result);
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Bridge not ready', 'error');
    }
}

function handleUndo() {
    console.log('Undo clicked');
    window.debugUtils.showErrorToast('Undo', 'Undo not yet implemented', 'info');
}

function handleRedo() {
    console.log('Redo clicked');
    window.debugUtils.showErrorToast('Redo', 'Redo not yet implemented', 'info');
}

function handlePreview() {
    console.log('Preview clicked');
    window.debugUtils.showErrorToast('Preview', 'Preview not yet implemented', 'info');
}

function handleExport() {
    console.log('Export clicked');
    window.debugUtils.showErrorToast('Export', 'Export not yet implemented', 'info');
}

function handleSettings() {
    console.log('Settings clicked');
    openSettingsModal();
}

function handleDebug() {
    console.log('Debug button clicked');
    if (typeof window.toggleDebugConsole === 'function') {
        window.toggleDebugConsole();
    } else {
        const debugConsole = document.getElementById('debugConsole');
        if (debugConsole) {
            debugConsole.classList.toggle('hidden');
        }
    }
}

// Initialize all toolbar buttons
function initializeToolbar() {
    console.log('Initializing toolbar...');
    
    const buttons = {
        'saveBtn': handleSave,
        'undoBtn': handleUndo,
        'redoBtn': handleRedo,
        'previewBtn': handlePreview,
        'exportBtn': handleExport,
        'settingsBtn': handleSettings,
        'debugBtn': handleDebug
    };
    
    for (const [id, handler] of Object.entries(buttons)) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', handler);
            console.log(`Attached handler to ${id}`);
        } else {
            console.warn(`Button not found: ${id}`);
        }
    }
}

// Initialize drag and drop on component items
function initializeDragAndDrop() {
    console.log('Initializing drag and drop...');
    
    const componentItems = document.querySelectorAll('.component-item');
    componentItems.forEach(item => {
        item.addEventListener('dragstart', window.canvasModule.onDragStart);
        item.addEventListener('dragend', window.canvasModule.onDragEnd);
    });
    
    console.log(`Drag and drop initialized for ${componentItems.length} components`);
}

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    console.log('Initializing keyboard shortcuts...');
    
    document.addEventListener('keydown', (e) => {
        // Ctrl+S - Save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            handleSave();
        }
        
        // Ctrl+Z - Undo
        if (e.ctrlKey && !e.shiftKey && e.key === 'z') {
            e.preventDefault();
            handleUndo();
        }
        
        // Ctrl+Y or Ctrl+Shift+Z - Redo
        if ((e.ctrlKey && e.key === 'y') || (e.ctrlKey && e.shiftKey && e.key === 'z')) {
            e.preventDefault();
            handleRedo();
        }
        
        // Ctrl+P - Preview
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            handlePreview();
        }
        
        // Ctrl+E - Export
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            handleExport();
        }
    });
    
    console.log('✓ Keyboard shortcuts initialized');
}

// Initialize error handling
function initializeErrorHandling() {
    console.log('Initializing error handling...');
    
    // Global error handler for uncaught exceptions
    window.addEventListener('error', (event) => {
        console.error('Uncaught error:', event.error);
        
        const errorMsg = event.error?.message || String(event.message);
        const errorSource = event.filename || 'unknown';
        const errorLine = event.lineno || '?';
        
        window.debugUtils.handleError(
            event.error || new Error(errorMsg),
            `${errorSource}:${errorLine}`
        );
        
        // Also send to bridge for logging
        if (window.bridge && window.bridge.reportError) {
            window.bridge.reportError('JavaScript Error', {
                message: errorMsg,
                source: errorSource,
                line: errorLine,
                stack: event.error?.stack || 'No stack trace'
            });
        }
    });
    
    // Global unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        
        const errorMsg = event.reason?.message || String(event.reason);
        
        window.debugUtils.handleError(
            event.reason instanceof Error ? event.reason : new Error(errorMsg),
            'Unhandled Promise Rejection'
        );
        
        // Prevent browser default handling
        event.preventDefault();
        
        // Send to bridge
        if (window.bridge && window.bridge.reportError) {
            window.bridge.reportError('Unhandled Promise', {
                message: errorMsg,
                reason: event.reason
            });
        }
    });
    
    console.log('✓ Error handling initialized');
}

// Main initialization
async function initializeApp() {
    console.log('=== Anki Template Designer Starting ===');
    console.log('Version: 1.0.0');
    console.log('Press Ctrl+Alt+D to toggle debug console');
    
    try {
        // Initialize debug console
        window.debugUtils.createDebugConsole();
        console.log('✓ Debug console ready');
        
        // Initialize bridge
        console.log('Initializing bridge...');
        await window.bridgeModule.initializeBridge();
        console.log('✓ Bridge connected');
        
        // Test bridge
        await window.bridgeModule.testBridge();
        console.log('✓ Bridge test passed');
        
        // Initialize UI components
        window.componentsModule.initializeComponents();
        console.log('✓ Components initialized');
        
        window.canvasModule.initializeCanvas();
        console.log('✓ Canvas initialized');
        
        window.propertiesModule.initializePropertiesPanel();
        console.log('✓ Properties panel initialized');
        
        initializeToolbar();
        console.log('✓ Toolbar initialized');
        
        initializeDragAndDrop();
        console.log('✓ Drag and drop initialized');
        
        initializeKeyboardShortcuts();
        
        initializeErrorHandling();
        
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        console.log('=== Application Ready ===');
        
        window.debugUtils.showErrorToast(
            'Ready',
            'Anki Template Designer is ready to use',
            'success',
            'Drag components from the sidebar to the canvas'
        );
        
        // Notify that editor is ready
        if (typeof window.editorReady === 'function') {
            window.editorReady();
        }
        
    } catch (error) {
        console.error('Initialization failed:', error);
        window.debugUtils.handleError(error, 'Application Initialization');
        
        // Show error in UI
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = 'Failed to initialize. Check console for details.';
            loadingText.style.color = '#e74c3c';
        }
    }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Signal that editor is ready (called from Python)
window.editorReady = function() {
    console.log('editorReady callback triggered');
};
