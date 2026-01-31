# Plan 04: WebView Bridge Communication

## Objective
Implement bidirectional communication between Python and JavaScript via QWebChannel.

---

## Prerequisites
- [ ] Plan 01-03 completed and tested
- [ ] Dialog with WebView loads HTML successfully

---

## Step 4.1: Create Python Bridge Class

### Task
Create a WebViewBridge class that exposes Python methods to JavaScript.

### Implementation

**anki_template_designer/gui/webview_bridge.py**
```python
"""WebView bridge for Python-JavaScript communication.

This module provides bidirectional communication between the Python
backend and the JavaScript frontend using QWebChannel.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional

try:
    from aqt.qt import QObject, pyqtSlot, pyqtSignal, QWebChannel
    HAS_ANKI = True
except ImportError:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
    from PyQt6.QtWebChannel import QWebChannel
    HAS_ANKI = False

logger = logging.getLogger("anki_template_designer.gui.webview_bridge")


class WebViewBridge(QObject):
    """Bridge for Python-JavaScript communication.
    
    Exposes Python methods to JavaScript and handles callbacks.
    Uses QWebChannel for bidirectional message passing.
    
    Signals:
        messageReceived: Emitted when a message is received from JS.
        templateLoaded: Emitted when a template is loaded.
        templateSaved: Emitted when a template is saved.
    """
    
    # Signals for JS -> Python communication
    messageReceived = pyqtSignal(str, str)  # (method, data)
    templateLoaded = pyqtSignal(str)  # template_id
    templateSaved = pyqtSignal(str, bool)  # template_id, success
    
    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the bridge.
        
        Args:
            parent: Parent QObject.
        """
        super().__init__(parent)
        
        self._callbacks: Dict[str, Callable] = {}
        self._channel: Optional[QWebChannel] = None
        self._connected = False
        
        logger.info("WebViewBridge initialized")
    
    def setup_channel(self, webview: Any) -> None:
        """Set up the QWebChannel with the WebView.
        
        Args:
            webview: QWebEngineView instance.
        """
        if webview is None:
            logger.error("Cannot setup channel: webview is None")
            return
        
        page = webview.page()
        if page is None:
            logger.error("Cannot setup channel: page is None")
            return
        
        self._channel = QWebChannel(page)
        self._channel.registerObject("bridge", self)
        page.setWebChannel(self._channel)
        
        self._connected = True
        logger.info("WebChannel setup complete")
    
    @property
    def is_connected(self) -> bool:
        """Check if bridge is connected.
        
        Returns:
            True if channel is set up and connected.
        """
        return self._connected
    
    # ===== Python -> JavaScript Methods =====
    
    def send_to_js(self, method: str, data: Any = None) -> None:
        """Send a message to JavaScript.
        
        Args:
            method: The method name to call in JS.
            data: Data to send (will be JSON serialized).
        """
        if not self._connected:
            logger.warning(f"Cannot send to JS: not connected. Method: {method}")
            return
        
        # This will be called from JavaScript side
        self.messageReceived.emit(method, json.dumps(data) if data else "")
    
    # ===== JavaScript -> Python Methods (exposed via QWebChannel) =====
    
    @pyqtSlot(str, result=str)
    def getConfig(self, key: str) -> str:
        """Get a configuration value.
        
        Args:
            key: Configuration key to retrieve.
            
        Returns:
            JSON-encoded configuration value.
        """
        logger.debug(f"getConfig called: {key}")
        
        try:
            from .. import _load_config
            config = _load_config()
            value = config.get(key)
            return json.dumps({"success": True, "value": value})
        except Exception as e:
            logger.error(f"Error in getConfig: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, str, result=str)
    def setConfig(self, key: str, value_json: str) -> str:
        """Set a configuration value.
        
        Args:
            key: Configuration key to set.
            value_json: JSON-encoded value to set.
            
        Returns:
            JSON-encoded result.
        """
        logger.debug(f"setConfig called: {key}")
        
        try:
            value = json.loads(value_json)
            # Config saving will be implemented in Plan 10
            return json.dumps({"success": True})
        except Exception as e:
            logger.error(f"Error in setConfig: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(result=str)
    def getVersion(self) -> str:
        """Get the addon version.
        
        Returns:
            JSON-encoded version string.
        """
        from .. import __version__
        return json.dumps({"version": __version__})
    
    @pyqtSlot(str, result=str)
    def log(self, message: str) -> str:
        """Log a message from JavaScript.
        
        Args:
            message: Message to log.
            
        Returns:
            JSON-encoded success result.
        """
        logger.info(f"[JS] {message}")
        return json.dumps({"success": True})
    
    @pyqtSlot(str, str, result=str)
    def handleAction(self, action: str, payload_json: str) -> str:
        """Handle an action from JavaScript.
        
        Generic action handler for extensibility.
        
        Args:
            action: Action name.
            payload_json: JSON-encoded action payload.
            
        Returns:
            JSON-encoded result.
        """
        logger.debug(f"handleAction: {action}")
        
        try:
            payload = json.loads(payload_json) if payload_json else {}
            
            # Dispatch to registered callback if exists
            if action in self._callbacks:
                result = self._callbacks[action](payload)
                return json.dumps({"success": True, "result": result})
            
            return json.dumps({"success": False, "error": f"Unknown action: {action}"})
        except Exception as e:
            logger.error(f"Error handling action {action}: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def register_action(self, action: str, callback: Callable) -> None:
        """Register a callback for an action.
        
        Args:
            action: Action name.
            callback: Function to call when action is received.
        """
        self._callbacks[action] = callback
        logger.debug(f"Registered action: {action}")
    
    def unregister_action(self, action: str) -> None:
        """Unregister an action callback.
        
        Args:
            action: Action name to unregister.
        """
        if action in self._callbacks:
            del self._callbacks[action]
            logger.debug(f"Unregistered action: {action}")
```

### Quality Checks

#### Security
- [ ] Input validation on all pyqtSlot methods
- [ ] JSON parsing with exception handling
- [ ] No eval() or exec() on received data
- [ ] Logging doesn't expose sensitive data

#### Performance
- [ ] Lazy loading of config
- [ ] Lightweight slot methods
- [ ] No blocking operations

#### Best Practices
- [ ] Type hints throughout
- [ ] Clear signal/slot pattern
- [ ] Callback registration for extensibility

#### Maintainability
- [ ] Single responsibility methods
- [ ] Clear logging
- [ ] Docstrings on all public methods

#### Documentation
- [ ] Module-level docstring
- [ ] Class-level docstring with signals listed
- [ ] All methods documented

#### Testing
- [ ] Works without Anki (PyQt6 fallback)
- [ ] JSON serialization tested
- [ ] Error handling tested

#### Accessibility
- [ ] N/A for this module

#### Scalability
- [ ] Action registration allows extension
- [ ] Easy to add new pyqtSlot methods

#### Compatibility
- [ ] Anki and PyQt6 compatible
- [ ] Python 3.9+ syntax

#### Error Handling
- [ ] All exceptions caught and logged
- [ ] Error responses in JSON format
- [ ] Graceful degradation on connection issues

#### Complexity
- [ ] Simple message-based architecture

#### Architecture
- [ ] Clean separation of concerns
- [ ] Signal/slot pattern for decoupling

#### License
- [ ] N/A

#### Specification
- [ ] Follows Qt WebChannel patterns

---

## Step 4.2: Update Designer Dialog to Use Bridge

### Task
Integrate the bridge into the dialog and set up the channel.

### Implementation

Update **anki_template_designer/gui/designer_dialog.py**:

Add after imports:
```python
from .webview_bridge import WebViewBridge
```

Add to `__init__`:
```python
        self._bridge: Optional[WebViewBridge] = None
```

Add new method:
```python
    def _setup_bridge(self) -> None:
        """Set up the WebView bridge for Python-JS communication."""
        if self._webview is None:
            logger.error("Cannot setup bridge: webview not initialized")
            return
        
        self._bridge = WebViewBridge(self)
        self._bridge.setup_channel(self._webview)
        
        # Register default actions
        self._bridge.register_action("save_template", self._on_save_template)
        self._bridge.register_action("load_template", self._on_load_template)
        
        logger.info("Bridge setup complete")
    
    def _on_save_template(self, payload: dict) -> dict:
        """Handle save template action from JS.
        
        Args:
            payload: Template data to save.
            
        Returns:
            Result dictionary.
        """
        logger.info("Save template requested")
        # Actual implementation in Plan 06
        return {"saved": True}
    
    def _on_load_template(self, payload: dict) -> dict:
        """Handle load template action from JS.
        
        Args:
            payload: Contains template_id.
            
        Returns:
            Template data.
        """
        template_id = payload.get("template_id")
        logger.info(f"Load template requested: {template_id}")
        # Actual implementation in Plan 06
        return {"template_id": template_id, "content": ""}
    
    @property
    def bridge(self) -> Optional[WebViewBridge]:
        """Get the WebView bridge.
        
        Returns:
            The WebViewBridge instance.
        """
        return self._bridge
```

Update `_setup_ui` to call `_setup_bridge` after webview creation:
```python
    def _setup_ui(self) -> None:
        """Set up the user interface with WebView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._webview = QWebEngineView(self)
        layout.addWidget(self._webview)
        
        self.setLayout(layout)
        
        # Set up bridge after webview
        self._setup_bridge()
```

### Quality Checks
Same as Step 4.1 - ensure integration is clean.

---

## Step 4.3: Update HTML with QWebChannel Integration

### Task
Add QWebChannel JavaScript integration to index.html.

### Implementation

Update **anki_template_designer/web/index.html** - add before closing `</head>`:

```html
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
```

Replace the existing `<script>` section with:

```html
    <script>
        // Bridge reference
        let bridge = null;
        
        // Initialize WebChannel when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            initWebChannel();
        });
        
        function initWebChannel() {
            if (typeof QWebChannel === 'undefined') {
                console.warn('QWebChannel not available - running outside Anki?');
                updateStatus('Standalone Mode');
                hideLoading();
                return;
            }
            
            new QWebChannel(qt.webChannelTransport, function(channel) {
                bridge = channel.objects.bridge;
                
                if (!bridge) {
                    console.error('Bridge not found in channel');
                    updateStatus('Bridge Error');
                    return;
                }
                
                console.log('WebChannel connected');
                
                // Get version to verify connection
                bridge.getVersion(function(response) {
                    try {
                        const data = JSON.parse(response);
                        console.log('Addon version:', data.version);
                        updateStatus('Connected (v' + data.version + ')');
                    } catch (e) {
                        console.error('Failed to parse version:', e);
                    }
                });
                
                // Log connection via bridge
                bridge.log('WebChannel initialized from JavaScript');
                
                hideLoading();
            });
        }
        
        function updateStatus(text) {
            const status = document.getElementById('status');
            if (status) {
                status.textContent = text;
            }
        }
        
        function hideLoading() {
            const loading = document.getElementById('loading');
            if (loading) {
                loading.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">Bridge connected. Editor components will be added in later steps.</p>';
            }
        }
        
        // Utility functions for bridge communication
        function callBridge(method, params, callback) {
            if (!bridge) {
                console.error('Bridge not available');
                if (callback) callback({success: false, error: 'Bridge not available'});
                return;
            }
            
            const paramsJson = JSON.stringify(params || {});
            
            bridge.handleAction(method, paramsJson, function(response) {
                try {
                    const result = JSON.parse(response);
                    if (callback) callback(result);
                } catch (e) {
                    console.error('Failed to parse response:', e);
                    if (callback) callback({success: false, error: 'Parse error'});
                }
            });
        }
        
        function getConfig(key, callback) {
            if (!bridge) {
                console.error('Bridge not available');
                return;
            }
            
            bridge.getConfig(key, function(response) {
                try {
                    const result = JSON.parse(response);
                    if (callback) callback(result);
                } catch (e) {
                    console.error('Failed to parse config:', e);
                }
            });
        }
        
        // Expose ready signal
        window.editorReady = function() {
            return bridge !== null;
        };
    </script>
```

### Quality Checks

#### Security
- [ ] No eval() on received data
- [ ] JSON.parse with try/catch
- [ ] No inline event handlers

#### Performance
- [ ] Channel initialized once
- [ ] Callbacks are lightweight

#### Best Practices
- [ ] Error handling on all bridge calls
- [ ] Console logging for debugging

#### Maintainability
- [ ] Utility functions for common patterns
- [ ] Clear function names

#### Documentation
- [ ] Comments explain purpose

#### Testing
- [ ] Works without QWebChannel (standalone mode)
- [ ] Shows appropriate status

#### Accessibility
- [ ] Status updates visible

#### Scalability
- [ ] `callBridge` utility allows easy extension

#### Compatibility
- [ ] Works with Qt WebEngine
- [ ] Fallback for standalone testing

#### Error Handling
- [ ] All errors caught and logged
- [ ] User-visible error states

#### Complexity
- [ ] Simple initialization flow

#### Architecture
- [ ] Clean separation of channel setup and usage

#### License
- [ ] qwebchannel.js is from Qt (LGPL)

#### Specification
- [ ] Follows Qt WebChannel documentation

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_bridge.py
"""Tests for WebView bridge."""

import pytest
import json


def test_bridge_initialization():
    """Test bridge can be created."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    assert bridge is not None
    assert not bridge.is_connected


def test_action_registration():
    """Test action registration."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    
    test_result = {"called": False}
    
    def test_callback(payload):
        test_result["called"] = True
        return {"success": True}
    
    bridge.register_action("test_action", test_callback)
    
    # Simulate calling the action
    result = bridge.handleAction("test_action", "{}")
    data = json.loads(result)
    
    assert data["success"]
    assert test_result["called"]


def test_unknown_action():
    """Test handling of unknown action."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.handleAction("nonexistent", "{}")
    data = json.loads(result)
    
    assert not data["success"]
    assert "error" in data


def test_get_version():
    """Test version retrieval."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.getVersion()
    data = json.loads(result)
    
    assert "version" in data


def test_log():
    """Test logging from JS."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.log("Test message")
    data = json.loads(result)
    
    assert data["success"]
```

Run tests:
```bash
python -m pytest anki_template_designer/tests/test_bridge.py -v
```

### Manual Verification in Anki

1. [ ] Open Template Designer
2. [ ] Check header shows "Connected (v2.0.0)"
3. [ ] Open Anki console (Help > Debug Console or Ctrl+Shift+;)
4. [ ] Verify no JavaScript errors
5. [ ] Verify Python log shows "WebChannel initialized from JavaScript"
6. [ ] Close and reopen dialog
7. [ ] Verify reconnection works

### Developer Console Test

In Anki's debug console or browser dev tools:
```javascript
// Test bridge communication
callBridge('test', {}, function(result) {
    console.log('Result:', result);
});
```

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Automated tests pass
- [ ] Bridge connects in Anki
- [ ] Version displayed in header
- [ ] Console shows no errors
- [ ] Bidirectional communication works

---

## Next Step

After successful completion, proceed to [05-BASIC-UI-SHELL.md](05-BASIC-UI-SHELL.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
