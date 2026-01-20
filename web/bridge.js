/**
 * Python Bridge Connection via QWebChannel
 * 
 * Establishes bidirectional communication between Python and JavaScript
 */

// Global bridge object
window.bridge = null;

// Global available fields and behaviors
window.availableFields = ['Front', 'Back', 'Extra'];
window.availableBehaviors = [];

/**
 * Create a mock bridge for standalone testing
 */
function createMockBridge() {
    return {
        saveProject: (jsonStr) => console.log('[Mock Bridge] Save:', jsonStr.length, 'bytes'),
        requestPreview: (jsonStr) => console.log('[Mock Bridge] Preview:', jsonStr.length, 'bytes'),
        exportTemplate: (format, jsonStr) => console.log('[Mock Bridge] Export:', format),
        log: (msg) => console.log('[Mock Bridge]', msg),
        showError: (msg) => console.error('[Mock Bridge]', msg),
        getAnkiFields: () => JSON.stringify(['Front', 'Back', 'Extra']),
        getAnkiBehaviors: () => JSON.stringify([])
    };
}

/**
 * Initialize QWebChannel bridge
 */
function initializeBridge(callback) {
    console.log('[Bridge] Starting bridge initialization...');
    
    // Check if running in Qt WebEngine
    if (typeof QWebChannel === 'undefined') {
        console.warn('[Bridge] QWebChannel not available - using mock bridge');
        window.bridge = createMockBridge();
        console.log('[Bridge] Mock bridge created, proceeding without Python backend');
        if (callback) {
            setTimeout(callback, 100); // Give UI time to update
        }
        return;
    }
    
    // Set up timeout for bridge connection
    let bridgeConnectTimeout = setTimeout(() => {
        console.error('[Bridge] Connection timeout - bridge not responding');
        console.log('[Bridge] Using mock bridge as fallback');
        window.bridge = createMockBridge();
        if (callback) callback();
    }, 3000);
    
    try {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            clearTimeout(bridgeConnectTimeout);
            
            console.log('[Bridge] QWebChannel connection established');
            
            // Get bridge object exposed by Python
            window.bridge = channel.objects.bridge;
            
            if (!window.bridge) {
                console.error('[Bridge] Bridge object not found in channel');
                window.bridge = createMockBridge();
                if (callback) callback();
                return;
            }
            
            console.log('[Bridge] Connected to Python backend');
            
            // Connect Python signals
            if (window.bridge.templateLoaded) {
                window.bridge.templateLoaded.connect(function(jsonStr) {
                    console.log('[Bridge] Template loaded from Python');
                    onTemplateLoaded(jsonStr);
                });
            }
            
            if (window.bridge.fieldsUpdated) {
                window.bridge.fieldsUpdated.connect(function(jsonStr) {
                    console.log('[Bridge] Fields updated from Python');
                    onFieldsUpdated(jsonStr);
                });
            }
            
            if (window.bridge.behaviorsUpdated) {
                window.bridge.behaviorsUpdated.connect(function(jsonStr) {
                    console.log('[Bridge] Behaviors updated from Python');
                    onBehaviorsUpdated(jsonStr);
                });
            }
            
            // Fetch initial data
            try {
                if (window.bridge.getAnkiFields) {
                    const fieldsJson = window.bridge.getAnkiFields();
                    window.availableFields = JSON.parse(fieldsJson);
                    console.log('[Bridge] Loaded fields:', window.availableFields);
                }
            } catch (e) {
                console.error('[Bridge] Failed to get fields:', e);
            }
            
            try {
                if (window.bridge.getAnkiBehaviors) {
                    const behaviorsJson = window.bridge.getAnkiBehaviors();
                    window.availableBehaviors = JSON.parse(behaviorsJson);
                    console.log('[Bridge] Loaded behaviors:', window.availableBehaviors.length);
                }
            } catch (e) {
                console.error('[Bridge] Failed to get behaviors:', e);
            }
            
            // Initialize editor after bridge is ready
            console.log('[Bridge] Bridge setup complete, calling callback');
            if (callback) callback();
        });
    } catch (e) {
        clearTimeout(bridgeConnectTimeout);
        console.error('[Bridge] Exception during QWebChannel setup:', e);
        window.bridge = createMockBridge();
        if (callback) callback();
    }
}

// ========== Signal Handlers ========== 

function onTemplateLoaded(jsonStr) {
    if (!window.editor) return;
    
    try {
        const data = JSON.parse(jsonStr);
        window.editor.loadProjectData(data);
        console.log('[Bridge] Loaded project data');
    } catch (e) {
        console.error('[Bridge] Failed to load template:', e);
        if (window.bridge) {
            window.bridge.showError('Failed to load template: ' + e.message);
        }
    }
}

function onFieldsUpdated(jsonStr) {
    try {
        window.availableFields = JSON.parse(jsonStr);
        console.log('[Bridge] Updated fields:', window.availableFields);
    } catch (e) {
        console.error('[Bridge] Failed to update fields:', e);
    }
}

function onBehaviorsUpdated(jsonStr) {
    try {
        window.availableBehaviors = JSON.parse(jsonStr);
        console.log('[Bridge] Updated behaviors:', window.availableBehaviors.length);
    } catch (e) {
        console.error('[Bridge] Failed to update behaviors:', e);
    }
}

// ========== Functions Called by Python ========== 

window.saveProject = function() {
    if (!window.editor) return;
    
    const data = window.editor.getProjectData();
    const jsonStr = JSON.stringify(data);
    
    if (window.bridge) {
        window.bridge.saveProject(jsonStr);
    }
};

window.requestPreview = function() {
    if (!window.editor) return;
    
    const data = window.editor.getProjectData();
    const jsonStr = JSON.stringify(data);
    
    if (window.bridge) {
        window.bridge.requestPreview(jsonStr);
    }
};

window.exportTemplate = function(formatType) {
    if (!window.editor) return;
    
    const data = window.editor.getProjectData();
    const jsonStr = JSON.stringify(data);
    
    if (window.bridge) {
        window.bridge.exportTemplate(formatType, jsonStr);
    }
};

window.loadTemplate = function(projectData) {
    if (!window.editor) return;
    window.editor.loadProjectData(projectData);
};

window.getProjectData = function() {
    if (!window.editor) return null;
    return window.editor.getProjectData();
};

// Utility: Log to Python console
window.log = function(message) {
    if (window.bridge) {
        window.bridge.log(message);
    }
    console.log(message);
};
