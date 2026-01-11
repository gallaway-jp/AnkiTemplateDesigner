# 03c - GrapeJS Bridge: Python-JavaScript Communication

> **Purpose**: Detail the JavaScript bridge implementation for Python-JS communication.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

The bridge enables bidirectional communication between Python (Qt/PyQt) and JavaScript (GrapeJS) using QWebChannel. Python can call JavaScript functions, and JavaScript can call Python methods.

---

## JavaScript Bridge Implementation

### `web/bridge.js`

```javascript
/**
 * Python-JavaScript Bridge via QWebChannel
 * Handles communication between GrapeJS editor and Python backend
 */

// Bridge instance (set when channel is ready)
window.bridge = null;

// Callbacks for Python signals
const signalHandlers = {
    templateLoaded: [],
    fieldsUpdated: [],
    behaviorsUpdated: [],
    settingsUpdated: []
};

/**
 * Initialize the QWebChannel bridge
 * @param {function} callback - Called when bridge is ready
 */
function initializeBridge(callback) {
    // Check if running in Qt WebEngine
    if (typeof QWebChannel === 'undefined') {
        console.warn('QWebChannel not available - running in standalone mode');
        // Create mock bridge for testing outside Qt
        window.bridge = createMockBridge();
        if (callback) callback();
        return;
    }
    
    new QWebChannel(qt.webChannelTransport, function(channel) {
        // Get the bridge object registered from Python
        window.bridge = channel.objects.bridge;
        
        if (!window.bridge) {
            console.error('Bridge object not found in channel');
            return;
        }
        
        // Connect Python signals to JavaScript handlers
        connectSignals();
        
        console.log('Bridge initialized successfully');
        
        if (callback) callback();
    });
}

/**
 * Connect Python signals to JavaScript handlers
 */
function connectSignals() {
    if (!window.bridge) return;
    
    // Template loaded signal
    if (window.bridge.templateLoaded) {
        window.bridge.templateLoaded.connect(function(jsonStr) {
            try {
                const data = JSON.parse(jsonStr);
                handleTemplateLoaded(data);
            } catch (e) {
                console.error('Failed to parse template data:', e);
            }
        });
    }
    
    // Fields updated signal
    if (window.bridge.fieldsUpdated) {
        window.bridge.fieldsUpdated.connect(function(jsonStr) {
            try {
                const fields = JSON.parse(jsonStr);
                handleFieldsUpdated(fields);
            } catch (e) {
                console.error('Failed to parse fields data:', e);
            }
        });
    }
    
    // Behaviors updated signal
    if (window.bridge.behaviorsUpdated) {
        window.bridge.behaviorsUpdated.connect(function(jsonStr) {
            try {
                const behaviors = JSON.parse(jsonStr);
                handleBehaviorsUpdated(behaviors);
            } catch (e) {
                console.error('Failed to parse behaviors data:', e);
            }
        });
    }
    
    // Settings updated signal
    if (window.bridge.settingsUpdated) {
        window.bridge.settingsUpdated.connect(function(jsonStr) {
            try {
                const settings = JSON.parse(jsonStr);
                handleSettingsUpdated(settings);
            } catch (e) {
                console.error('Failed to parse settings data:', e);
            }
        });
    }
}

// ============ Signal Handlers ============

/**
 * Handle template loaded from Python
 * @param {object} projectData - GrapeJS project data
 */
function handleTemplateLoaded(projectData) {
    console.log('Template loaded from Python');
    
    if (window.editor) {
        window.editor.loadProjectData(projectData);
    }
    
    // Call registered handlers
    signalHandlers.templateLoaded.forEach(handler => {
        try {
            handler(projectData);
        } catch (e) {
            console.error('Template loaded handler error:', e);
        }
    });
}

/**
 * Handle Anki fields update from Python
 * @param {string[]} fields - Array of field names
 */
function handleFieldsUpdated(fields) {
    console.log('Fields updated:', fields);
    
    // Store globally for use in traits
    window.ankiFields = fields;
    
    // Update any field selector traits
    if (window.editor) {
        updateFieldTraits(fields);
    }
    
    // Call registered handlers
    signalHandlers.fieldsUpdated.forEach(handler => {
        try {
            handler(fields);
        } catch (e) {
            console.error('Fields updated handler error:', e);
        }
    });
}

/**
 * Handle AnkiJSApi behaviors update from Python
 * @param {object[]} behaviors - Array of behavior definitions
 */
function handleBehaviorsUpdated(behaviors) {
    console.log('Behaviors updated:', behaviors);
    
    // Store globally for use in traits
    window.ankiBehaviors = behaviors;
    
    // Update behavior selector traits
    if (window.editor) {
        updateBehaviorTraits(behaviors);
    }
    
    // Call registered handlers
    signalHandlers.behaviorsUpdated.forEach(handler => {
        try {
            handler(behaviors);
        } catch (e) {
            console.error('Behaviors updated handler error:', e);
        }
    });
}

/**
 * Handle settings update from Python
 * @param {object} settings - Editor settings
 */
function handleSettingsUpdated(settings) {
    console.log('Settings updated:', settings);
    
    // Apply settings to editor
    if (window.editor && settings) {
        if (settings.theme) {
            applyTheme(settings.theme);
        }
        if (settings.devicePreview) {
            window.editor.setDevice(settings.devicePreview);
        }
    }
    
    // Call registered handlers
    signalHandlers.settingsUpdated.forEach(handler => {
        try {
            handler(settings);
        } catch (e) {
            console.error('Settings updated handler error:', e);
        }
    });
}

// ============ Helper Functions ============

/**
 * Update field selector traits with new field list
 * @param {string[]} fields - Array of field names
 */
function updateFieldTraits(fields) {
    const options = fields.map(f => ({ id: f, name: f }));
    
    // Add special Anki fields
    options.unshift(
        { id: '', name: '(none)' },
        { id: 'FrontSide', name: '{{FrontSide}}' },
        { id: 'Tags', name: '{{Tags}}' },
        { id: 'Type', name: '{{Type}}' },
        { id: 'Deck', name: '{{Deck}}' }
    );
    
    // Update trait definitions
    const tm = window.editor.TraitManager;
    // Traits will pick up window.ankiFields when rendering
}

/**
 * Update behavior selector traits with new behavior list
 * @param {object[]} behaviors - Array of behavior definitions
 */
function updateBehaviorTraits(behaviors) {
    const options = behaviors.map(b => ({
        id: b.name,
        name: b.name,
        category: b.category
    }));
    
    options.unshift({ id: '', name: '(none)' });
    
    // Store for trait rendering
    window.ankiBehaviorOptions = options;
}

/**
 * Apply theme to editor
 * @param {string} theme - Theme name ('light' or 'dark')
 */
function applyTheme(theme) {
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(`theme-${theme}`);
}

// ============ Public API ============

/**
 * Register a handler for template loaded events
 * @param {function} handler - Callback function
 */
window.onTemplateLoaded = function(handler) {
    signalHandlers.templateLoaded.push(handler);
};

/**
 * Register a handler for fields updated events
 * @param {function} handler - Callback function
 */
window.onFieldsUpdated = function(handler) {
    signalHandlers.fieldsUpdated.push(handler);
};

/**
 * Register a handler for behaviors updated events
 * @param {function} handler - Callback function
 */
window.onBehaviorsUpdated = function(handler) {
    signalHandlers.behaviorsUpdated.push(handler);
};

/**
 * Request Anki fields from Python
 * @returns {Promise<string[]>} Array of field names
 */
window.requestAnkiFields = function() {
    return new Promise((resolve, reject) => {
        if (!window.bridge) {
            reject(new Error('Bridge not initialized'));
            return;
        }
        
        try {
            const result = window.bridge.getAnkiFields();
            resolve(JSON.parse(result));
        } catch (e) {
            reject(e);
        }
    });
};

/**
 * Request AnkiJSApi behaviors from Python
 * @returns {Promise<object[]>} Array of behavior definitions
 */
window.requestAnkiBehaviors = function() {
    return new Promise((resolve, reject) => {
        if (!window.bridge) {
            reject(new Error('Bridge not initialized'));
            return;
        }
        
        try {
            const result = window.bridge.getAnkiBehaviors();
            resolve(JSON.parse(result));
        } catch (e) {
            reject(e);
        }
    });
};

// ============ Mock Bridge for Testing ============

/**
 * Create a mock bridge for testing outside Qt
 * @returns {object} Mock bridge object
 */
function createMockBridge() {
    return {
        saveProject: function(json) {
            console.log('Mock: saveProject called');
            console.log(JSON.parse(json));
        },
        
        requestPreview: function(json) {
            console.log('Mock: requestPreview called');
        },
        
        exportTemplate: function(format, json) {
            console.log('Mock: exportTemplate called', format);
        },
        
        log: function(message) {
            console.log('Mock log:', message);
        },
        
        showError: function(message) {
            console.error('Mock error:', message);
            alert(message);
        },
        
        getAnkiFields: function() {
            // Return mock fields
            return JSON.stringify([
                'Front', 'Back', 'Extra', 'Image', 'Audio'
            ]);
        },
        
        getAnkiBehaviors: function() {
            // Return mock behaviors
            return JSON.stringify([
                { name: 'ankiShowAnswer', category: 'Card' },
                { name: 'ankiMarkCard', category: 'Card' },
                { name: 'ankiSuspendCard', category: 'Card' },
                { name: 'ankiAnswerEase3', category: 'Rating' },
                { name: 'ankiTtsSpeak', category: 'TTS' }
            ]);
        }
    };
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeBridge,
        signalHandlers
    };
}
```

---

## Python Bridge Class (Complete)

### `gui/webview_bridge.py` (Full Implementation)

```python
"""
Python side of the QWebChannel bridge.
Handles communication between Qt and GrapeJS JavaScript.
"""
from typing import Callable, Any, Optional, List, Dict
from aqt.qt import QObject, pyqtSlot, pyqtSignal
import json
import logging

logger = logging.getLogger(__name__)


class WebViewBridge(QObject):
    """
    Bridge object exposed to JavaScript via QWebChannel.
    
    JavaScript calls methods via: window.bridge.methodName(args)
    Python emits signals that JavaScript can connect to.
    
    Usage:
        bridge = WebViewBridge()
        channel = QWebChannel(page)
        channel.registerObject("bridge", bridge)
        page.setWebChannel(channel)
    """
    
    # ========== Signals (Python -> JavaScript) ==========
    
    # Emitted to load a template into the editor
    templateLoaded = pyqtSignal(str)
    
    # Emitted when available Anki fields change
    fieldsUpdated = pyqtSignal(str)
    
    # Emitted when available behaviors change
    behaviorsUpdated = pyqtSignal(str)
    
    # Emitted when editor settings change
    settingsUpdated = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Callbacks for JavaScript actions
        self._save_callback: Optional[Callable[[dict], None]] = None
        self._preview_callback: Optional[Callable[[dict], None]] = None
        self._export_callback: Optional[Callable[[str, dict], None]] = None
        
        # Cached data
        self._cached_fields: List[str] = []
        self._cached_behaviors: List[Dict] = []
    
    # ========== Slots (JavaScript -> Python) ==========
    
    @pyqtSlot(str)
    def saveProject(self, grapejs_json: str) -> None:
        """
        Called by JavaScript when user saves the project.
        
        Args:
            grapejs_json: JSON string of GrapeJS project data
        """
        logger.debug("saveProject called from JavaScript")
        
        if not self._save_callback:
            logger.warning("No save callback registered")
            return
        
        try:
            data = json.loads(grapejs_json)
            self._save_callback(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in saveProject: {e}")
            self.showError(f"Failed to save: Invalid project data")
    
    @pyqtSlot(str)
    def requestPreview(self, grapejs_json: str) -> None:
        """
        Called by JavaScript to request a card preview.
        
        Args:
            grapejs_json: JSON string of current project data
        """
        logger.debug("requestPreview called from JavaScript")
        
        if not self._preview_callback:
            logger.warning("No preview callback registered")
            return
        
        try:
            data = json.loads(grapejs_json)
            self._preview_callback(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in requestPreview: {e}")
            self.showError(f"Failed to preview: Invalid project data")
    
    @pyqtSlot(str, str)
    def exportTemplate(self, format_type: str, grapejs_json: str) -> None:
        """
        Called by JavaScript to export template.
        
        Args:
            format_type: Export format ('html', 'json', 'anki')
            grapejs_json: JSON string of project data
        """
        logger.debug(f"exportTemplate called: format={format_type}")
        
        if not self._export_callback:
            logger.warning("No export callback registered")
            return
        
        try:
            data = json.loads(grapejs_json)
            self._export_callback(format_type, data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in exportTemplate: {e}")
            self.showError(f"Failed to export: Invalid project data")
    
    @pyqtSlot(str)
    def log(self, message: str) -> None:
        """
        Called by JavaScript for debug logging.
        
        Args:
            message: Log message
        """
        logger.info(f"[JS] {message}")
    
    @pyqtSlot(str)
    def showError(self, message: str) -> None:
        """
        Called by JavaScript to show error to user.
        
        Args:
            message: Error message to display
        """
        logger.error(f"[JS Error] {message}")
        from aqt.utils import showWarning
        showWarning(message, title="Template Designer Error")
    
    @pyqtSlot(str)
    def showInfo(self, message: str) -> None:
        """
        Called by JavaScript to show info message.
        
        Args:
            message: Info message to display
        """
        from aqt.utils import showInfo
        showInfo(message, title="Template Designer")
    
    @pyqtSlot(result=str)
    def getAnkiFields(self) -> str:
        """
        Called by JavaScript to get available Anki fields.
        
        Returns:
            JSON string of field names array
        """
        if not self._cached_fields:
            from ..services.anki_service import AnkiService
            service = AnkiService()
            self._cached_fields = service.get_available_fields()
        
        return json.dumps(self._cached_fields)
    
    @pyqtSlot(result=str)
    def getAnkiBehaviors(self) -> str:
        """
        Called by JavaScript to get AnkiJSApi behaviors.
        
        Returns:
            JSON string of behavior definitions array
        """
        if not self._cached_behaviors:
            from ..services.ankijsapi_service import AnkiJSApiService
            service = AnkiJSApiService()
            self._cached_behaviors = service.get_available_behaviors()
        
        return json.dumps(self._cached_behaviors)
    
    @pyqtSlot(str, result=str)
    def getNoteTypeFields(self, note_type_name: str) -> str:
        """
        Get fields for a specific note type.
        
        Args:
            note_type_name: Name of the note type
            
        Returns:
            JSON string of field names array
        """
        from ..services.anki_service import AnkiService
        service = AnkiService()
        fields = service.get_note_type_fields(note_type_name)
        return json.dumps(fields)
    
    @pyqtSlot(result=str)
    def getNoteTypes(self) -> str:
        """
        Get all available note types.
        
        Returns:
            JSON string of note type names array
        """
        from ..services.anki_service import AnkiService
        service = AnkiService()
        note_types = service.get_note_types()
        return json.dumps(note_types)
    
    # ========== Python API (for calling from dialog) ==========
    
    def set_save_callback(self, callback: Callable[[dict], None]) -> None:
        """Set callback for save action."""
        self._save_callback = callback
    
    def set_preview_callback(self, callback: Callable[[dict], None]) -> None:
        """Set callback for preview action."""
        self._preview_callback = callback
    
    def set_export_callback(self, callback: Callable[[str, dict], None]) -> None:
        """Set callback for export action."""
        self._export_callback = callback
    
    def load_template(self, grapejs_data: dict) -> None:
        """
        Load a template into the JavaScript editor.
        
        Args:
            grapejs_data: GrapeJS project data dictionary
        """
        json_str = json.dumps(grapejs_data)
        self.templateLoaded.emit(json_str)
    
    def update_fields(self, fields: List[str]) -> None:
        """
        Update available Anki fields in editor.
        
        Args:
            fields: List of field names
        """
        self._cached_fields = fields
        self.fieldsUpdated.emit(json.dumps(fields))
    
    def update_behaviors(self, behaviors: List[Dict]) -> None:
        """
        Update available AnkiJSApi behaviors in editor.
        
        Args:
            behaviors: List of behavior definition dicts
        """
        self._cached_behaviors = behaviors
        self.behaviorsUpdated.emit(json.dumps(behaviors))
    
    def update_settings(self, settings: dict) -> None:
        """
        Update editor settings.
        
        Args:
            settings: Settings dictionary
        """
        self.settingsUpdated.emit(json.dumps(settings))
    
    def clear_cache(self) -> None:
        """Clear cached data."""
        self._cached_fields = []
        self._cached_behaviors = []
```

---

## Communication Sequence Diagrams

### Save Project Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │         │ GrapeJS  │         │  Bridge  │         │  Python  │
│          │         │   (JS)   │         │          │         │  Dialog  │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ Click Save         │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ getProjectData()   │                    │
     │                    │<───────────────────│                    │
     │                    │                    │                    │
     │                    │ saveProject(json)  │                    │
     │                    │───────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ pyqtSlot called    │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │                    │ Convert to
     │                    │                    │                    │ Anki format
     │                    │                    │                    │
     │                    │                    │                    │ Save to
     │                    │                    │                    │ note type
     │                    │                    │                    │
     │<───────────────────────────────────────────────────────────── 
     │ Show success                                                  
     │                                                               
```

### Load Template Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Python  │         │  Bridge  │         │ GrapeJS  │         │  Canvas  │
│  Dialog  │         │          │         │   (JS)   │         │          │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ load_template(data)│                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ emit templateLoaded│                    │
     │                    │───────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ loadProjectData()  │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │                    │ Render
     │                    │                    │                    │ components
     │                    │                    │                    │
```

---

## Error Handling

### JavaScript Error Handling

```javascript
// Wrap bridge calls in try-catch
function safeBridgeCall(method, ...args) {
    if (!window.bridge) {
        console.error('Bridge not available');
        return null;
    }
    
    try {
        return window.bridge[method](...args);
    } catch (e) {
        console.error(`Bridge call failed: ${method}`, e);
        return null;
    }
}
```

### Python Error Handling

```python
@pyqtSlot(str)
def saveProject(self, grapejs_json: str) -> None:
    try:
        data = json.loads(grapejs_json)
        self._save_callback(data)
    except json.JSONDecodeError:
        self.showError("Invalid project data format")
    except Exception as e:
        logger.exception("Save failed")
        self.showError(f"Save failed: {str(e)}")
```

---

## Testing the Bridge

### Test in Browser (Mock Mode)

```javascript
// In browser console
initializeBridge(() => {
    console.log('Bridge ready (mock mode)');
    
    // Test save
    window.saveProject();
    
    // Test field request
    window.requestAnkiFields().then(fields => {
        console.log('Fields:', fields);
    });
});
```

### Test from Python

```python
def test_bridge():
    from gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    
    # Set up test callback
    received_data = []
    bridge.set_save_callback(lambda d: received_data.append(d))
    
    # Simulate JS call
    bridge.saveProject('{"test": true}')
    
    assert len(received_data) == 1
    assert received_data[0] == {"test": True}
```

---

## Next Plan

See [04-COMPONENT-LIBRARY.md](04-COMPONENT-LIBRARY.md) for the complete list of 200+ UI components organized as GrapeJS blocks.
