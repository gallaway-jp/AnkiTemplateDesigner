/**
 * Python Bridge Connection via QWebChannel
 * 
 * Establishes bidirectional communication between Python and JavaScript
 */

// Global bridge object
window.bridge = null;

// Initialize QWebChannel connection
new QWebChannel(qt.webChannelTransport, function(channel) {
    // Get bridge object exposed by Python
    window.bridge = channel.objects.bridge;
    
    console.log('[Bridge] Connected to Python');
    
    // Listen to Python signals
    bridge.templateLoaded.connect(function(jsonStr) {
        console.log('[Bridge] Template loaded from Python');
        onTemplateLoaded(jsonStr);
    });
    
    bridge.fieldsUpdated.connect(function(jsonStr) {
        console.log('[Bridge] Fields updated from Python');
        onFieldsUpdated(jsonStr);
    });
    
    bridge.behaviorsUpdated.connect(function(jsonStr) {
        console.log('[Bridge] Behaviors updated from Python');
        onBehaviorsUpdated(jsonStr);
    });
    
    // Initialize editor after bridge is ready
    if (typeof initializeEditor === 'function') {
        initializeEditor();
    }
});

// Global functions to be called by Python bridge signals
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
    if (!window.availableFields) window.availableFields = [];
    
    try {
        window.availableFields = JSON.parse(jsonStr);
        console.log('[Bridge] Updated fields:', window.availableFields);
    } catch (e) {
        console.error('[Bridge] Failed to update fields:', e);
    }
}

function onBehaviorsUpdated(jsonStr) {
    if (!window.availableBehaviors) window.availableBehaviors = [];
    
    try {
        window.availableBehaviors = JSON.parse(jsonStr);
        console.log('[Bridge] Updated behaviors:', window.availableBehaviors);
    } catch (e) {
        console.error('[Bridge] Failed to update behaviors:', e);
    }
}

// Functions called by Python to trigger exports
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

// Utility: Log to Python console
window.log = function(message) {
    if (window.bridge) {
        window.bridge.log(message);
    }
    console.log(message);
};
