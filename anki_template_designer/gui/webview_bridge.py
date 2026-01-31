"""WebView bridge for Python-JavaScript communication.

This module provides bidirectional communication between the Python
backend and the JavaScript frontend using QWebChannel.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

try:
    from aqt.qt import QObject, pyqtSlot, pyqtSignal, QWebChannel
    HAS_ANKI = True
except ImportError:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
    from PyQt6.QtWebChannel import QWebChannel
    HAS_ANKI = False

if TYPE_CHECKING:
    from ..services.template_service import TemplateService
    from ..services.undo_redo_manager import UndoRedoManager
    from ..services.error_handler import ErrorHandler

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
    inspectorToggleRequested = pyqtSignal()  # Request to toggle inspector
    
    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the bridge.
        
        Args:
            parent: Parent QObject.
        """
        super().__init__(parent)
        
        self._callbacks: Dict[str, Callable] = {}
        self._channel: Optional[QWebChannel] = None
        self._connected = False
        self._template_service: Optional["TemplateService"] = None
        self._undo_manager: Optional["UndoRedoManager"] = None
        self._error_handler: Optional["ErrorHandler"] = None
        
        logger.debug("WebViewBridge initialized")
    
    def set_template_service(self, service: "TemplateService") -> None:
        """Set the template service instance.
        
        Args:
            service: TemplateService instance.
        """
        self._template_service = service
        logger.debug("Template service connected to bridge")
    
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
        logger.debug("WebChannel setup complete")
    
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
        logger.debug(f"[JS] {message}")
        return json.dumps({"success": True})
    
    @pyqtSlot()
    def toggleInspector(self) -> None:
        """Toggle the inspector window.
        
        Called from JavaScript when Ctrl+Shift+I is pressed.
        Emits signal to parent dialog to show/hide inspector.
        """
        self.inspectorToggleRequested.emit()
    
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

    # ===== Template Service Methods =====
    
    @pyqtSlot(result=str)
    def listTemplates(self) -> str:
        """List all available templates.
        
        Returns:
            JSON-encoded list of template metadata.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            templates = self._template_service.list_templates()
            return json.dumps({"success": True, "templates": templates})
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def loadTemplate(self, template_id: str) -> str:
        """Load a template by ID.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            JSON-encoded template data.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            template = self._template_service.get_template(template_id)
            
            if template:
                self._template_service.set_current_template(template_id)
                self.templateLoaded.emit(template_id)
                return json.dumps({"success": True, "template": template.to_dict()})
            else:
                return json.dumps({"success": False, "error": "Template not found"})
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def saveTemplate(self, template_json: str) -> str:
        """Save a template.
        
        Args:
            template_json: JSON-encoded template data.
            
        Returns:
            JSON-encoded result.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            from ..core.models import Template
            data = json.loads(template_json)
            template = Template.from_dict(data)
            
            success = self._template_service.save_template(template)
            self.templateSaved.emit(template.id, success)
            return json.dumps({"success": success})
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def createTemplate(self, name: str) -> str:
        """Create a new template.
        
        Args:
            name: Name for the new template.
            
        Returns:
            JSON-encoded new template data.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            template = self._template_service.create_template(name)
            return json.dumps({"success": True, "template": template.to_dict()})
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def deleteTemplate(self, template_id: str) -> str:
        """Delete a template.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            JSON-encoded result.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            success = self._template_service.delete_template(template_id)
            return json.dumps({"success": success})
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(result=str)
    def getCurrentTemplate(self) -> str:
        """Get the current template.
        
        Returns:
            JSON-encoded current template data.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            template = self._template_service.current_template
            if template:
                return json.dumps({"success": True, "template": template.to_dict()})
            else:
                return json.dumps({"success": True, "template": None})
        except Exception as e:
            logger.error(f"Error getting current template: {e}")
            return json.dumps({"success": False, "error": str(e)})

    # ===== Undo/Redo Methods =====
    
    def set_undo_manager(self, manager: "UndoRedoManager") -> None:
        """Set the undo/redo manager.
        
        Args:
            manager: UndoRedoManager instance.
        """
        self._undo_manager = manager
        
        # Set up listener to notify JS of history changes
        def on_history_change(desc: str, can_undo: bool, can_redo: bool) -> None:
            self.send_to_js("historyChanged", {
                "description": desc,
                "canUndo": can_undo,
                "canRedo": can_redo
            })
        
        manager.add_listener(on_history_change)
        logger.debug("Undo manager connected to bridge")
    
    @pyqtSlot(str, str, str)
    def pushUndoState(self, state_before_json: str, state_after_json: str, description: str) -> None:
        """Push a state change to undo history.
        
        Args:
            state_before_json: JSON-encoded state before the change.
            state_after_json: JSON-encoded state after the change.
            description: Human-readable description of the change.
        """
        if self._undo_manager is None:
            logger.warning("Undo manager not initialized")
            return
        
        try:
            state_before = json.loads(state_before_json)
            state_after = json.loads(state_after_json)
            self._undo_manager.push_state(state_before, state_after, description)
            logger.debug(f"Pushed undo state: {description}")
        except Exception as e:
            logger.error(f"Error pushing undo state: {e}")
    
    @pyqtSlot(result=str)
    def undo(self) -> str:
        """Undo the last action.
        
        Returns:
            JSON-encoded result with state to restore.
        """
        if self._undo_manager is None:
            return json.dumps({"success": False, "error": "Undo not available"})
        
        try:
            state = self._undo_manager.undo()
            if state is not None:
                return json.dumps({"success": True, "state": state})
            return json.dumps({"success": False, "error": "Nothing to undo"})
        except Exception as e:
            logger.error(f"Error in undo: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(result=str)
    def redo(self) -> str:
        """Redo the last undone action.
        
        Returns:
            JSON-encoded result with state to restore.
        """
        if self._undo_manager is None:
            return json.dumps({"success": False, "error": "Redo not available"})
        
        try:
            state = self._undo_manager.redo()
            if state is not None:
                return json.dumps({"success": True, "state": state})
            return json.dumps({"success": False, "error": "Nothing to redo"})
        except Exception as e:
            logger.error(f"Error in redo: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(result=str)
    def getHistoryState(self) -> str:
        """Get current undo/redo history state.
        
        Returns:
            JSON-encoded history state with canUndo, canRedo, and descriptions.
        """
        if self._undo_manager is None:
            return json.dumps({
                "canUndo": False,
                "canRedo": False,
                "undoDescription": None,
                "redoDescription": None
            })
        
        return json.dumps({
            "canUndo": self._undo_manager.can_undo,
            "canRedo": self._undo_manager.can_redo,
            "undoDescription": self._undo_manager.undo_description,
            "redoDescription": self._undo_manager.redo_description
        })
    
    @pyqtSlot()
    def clearHistory(self) -> None:
        """Clear all undo/redo history."""
        if self._undo_manager is not None:
            self._undo_manager.clear()
            logger.debug("Undo history cleared")

    # ===== Error Handler Methods =====
    
    def set_error_handler(self, handler: "ErrorHandler") -> None:
        """Set the error handler.
        
        Args:
            handler: ErrorHandler instance.
        """
        self._error_handler = handler
        
        # Set up listener to notify JS of errors
        def on_error(error_info: dict) -> None:
            self.send_to_js("errorOccurred", error_info)
        
        handler.add_listener(on_error)
        logger.debug("Error handler connected to bridge")
    
    @pyqtSlot(str, str)
    def reportError(self, message: str, context_json: str) -> None:
        """Report an error from JavaScript.
        
        Args:
            message: Error message.
            context_json: JSON-encoded context dictionary.
        """
        if self._error_handler is None:
            logger.error(f"[JS Error] {message}")
            return
        
        try:
            context = json.loads(context_json) if context_json else {}
            context["source"] = "javascript"
            
            # Create a simple exception for the error handler
            from ..core.exceptions import TemplateDesignerError, ErrorCode
            error = TemplateDesignerError(
                message=message,
                code=ErrorCode.UI_RENDER_FAILED,
                details=context
            )
            self._error_handler.handle(error)
        except Exception as e:
            logger.error(f"Error reporting JS error: {e}")
    
    @pyqtSlot(result=str)
    def getRecentErrors(self) -> str:
        """Get recent errors for display.
        
        Returns:
            JSON-encoded list of recent errors.
        """
        if self._error_handler is None:
            return json.dumps({"errors": []})
        
        return json.dumps({
            "errors": self._error_handler.recent_errors,
            "total_count": self._error_handler.error_count
        })
    
    @pyqtSlot()
    def clearErrors(self) -> None:
        """Clear error history."""
        if self._error_handler is not None:
            self._error_handler.clear_history()
            logger.debug("Error history cleared")
    
    # =========================================================================
    # Logging Methods (Plan 09)
    # =========================================================================
    
    @pyqtSlot(result=str)
    def getLogStatus(self) -> str:
        """Get current logging status.
        
        Returns:
            JSON-encoded logging status information.
        """
        from ..utils.logging_config import get_logging_config
        
        config = get_logging_config()
        if config is None:
            return json.dumps({
                "initialized": False,
                "error": "Logging not initialized"
            })
        
        return json.dumps(config.get_status())
    
    @pyqtSlot(str, result=str)
    def setDebugMode(self, enabled_str: str) -> str:
        """Enable or disable debug logging mode.
        
        Args:
            enabled_str: "true" or "false" to enable/disable.
            
        Returns:
            JSON-encoded result with new status.
        """
        from ..utils.logging_config import get_logging_config
        
        config = get_logging_config()
        if config is None:
            return json.dumps({
                "success": False,
                "error": "Logging not initialized"
            })
        
        enabled = enabled_str.lower() == "true"
        config.set_debug_mode(enabled)
        
        logger.info(f"Debug mode {'enabled' if enabled else 'disabled'} via bridge")
        
        return json.dumps({
            "success": True,
            "debug_mode": config.debug_mode
        })
    
    @pyqtSlot(str, result=str)
    def getLogContents(self, lines_str: str) -> str:
        """Get recent log file contents.
        
        Args:
            lines_str: Number of lines to retrieve (as string).
            
        Returns:
            JSON-encoded log contents.
        """
        from ..utils.logging_config import get_logging_config
        
        config = get_logging_config()
        if config is None:
            return json.dumps({
                "success": False,
                "contents": "",
                "error": "Logging not initialized"
            })
        
        try:
            lines = int(lines_str) if lines_str else 100
        except ValueError:
            lines = 100
        
        contents = config.get_log_contents(lines=lines)
        
        return json.dumps({
            "success": True,
            "contents": contents,
            "lines_requested": lines
        })
