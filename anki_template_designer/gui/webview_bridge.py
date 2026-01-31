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
    
    # =========================================================================
    # Configuration Methods (Plan 10)
    # =========================================================================
    
    @pyqtSlot(result=str)
    def getConfig(self) -> str:
        """Get all configuration values.
        
        Returns:
            JSON-encoded configuration dictionary.
        """
        from ..services.config_service import get_config_service
        
        service = get_config_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Config service not initialized"
            })
        
        return json.dumps({
            "success": True,
            "config": service.get_all()
        })
    
    @pyqtSlot(str, result=str)
    def getConfigValue(self, key: str) -> str:
        """Get a specific configuration value.
        
        Args:
            key: Configuration key (supports dot notation).
            
        Returns:
            JSON-encoded result with value.
        """
        from ..services.config_service import get_config_service
        
        service = get_config_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Config service not initialized"
            })
        
        value = service.get(key)
        
        return json.dumps({
            "success": True,
            "key": key,
            "value": value
        })
    
    @pyqtSlot(str, str, result=str)
    def setConfigValue(self, key: str, value_json: str) -> str:
        """Set a configuration value.
        
        Args:
            key: Configuration key.
            value_json: JSON-encoded value.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.config_service import get_config_service
        
        service = get_config_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Config service not initialized"
            })
        
        try:
            value = json.loads(value_json)
        except json.JSONDecodeError:
            # Treat as string if not valid JSON
            value = value_json
        
        result = service.set(key, value, save=True)
        
        if result:
            logger.debug(f"Config set: {key} = {value}")
        
        return json.dumps({
            "success": result,
            "key": key,
            "value": value
        })
    
    @pyqtSlot(str, result=str)
    def resetConfig(self, key: str = "") -> str:
        """Reset configuration to defaults.
        
        Args:
            key: Specific key to reset, or empty for all.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.config_service import get_config_service
        
        service = get_config_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Config service not initialized"
            })
        
        if key:
            result = service.reset(key)
            logger.info(f"Config key reset: {key}")
        else:
            result = service.reset()
            logger.info("All config reset to defaults")
        
        service.save()
        
        return json.dumps({
            "success": result,
            "reset_key": key if key else "all"
        })
    
    @pyqtSlot(result=str)
    def saveConfig(self) -> str:
        """Save current configuration.
        
        Returns:
            JSON-encoded result.
        """
        from ..services.config_service import get_config_service
        
        service = get_config_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Config service not initialized"
            })
        
        result = service.save()
        
        return json.dumps({
            "success": result
        })
    
    # ===== Note Type Methods (Plan 11) =====
    
    @pyqtSlot(result=str)
    def getNoteTypes(self) -> str:
        """Get all available note types.
        
        Returns:
            JSON-encoded list of note types.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_types = service.get_all_note_types()
            return json.dumps({
                "success": True,
                "noteTypes": [nt.to_dict() for nt in note_types]
            })
        except Exception as e:
            logger.error(f"Error getting note types: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def getNoteType(self, note_type_id_str: str) -> str:
        """Get a specific note type by ID.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            
        Returns:
            JSON-encoded note type.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            note_type = service.get_note_type(note_type_id)
            if note_type is None:
                return json.dumps({
                    "success": False,
                    "error": f"Note type {note_type_id} not found"
                })
            return json.dumps({
                "success": True,
                "noteType": note_type.to_dict()
            })
        except Exception as e:
            logger.error(f"Error getting note type {note_type_id}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def getNoteTypeFields(self, note_type_id_str: str) -> str:
        """Get fields for a note type.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            
        Returns:
            JSON-encoded list of fields.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            fields = service.get_fields(note_type_id)
            if fields is None:
                return json.dumps({
                    "success": False,
                    "error": f"Note type {note_type_id} not found"
                })
            return json.dumps({
                "success": True,
                "fields": [f.to_dict() for f in fields]
            })
        except Exception as e:
            logger.error(f"Error getting fields for {note_type_id}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def getNoteTypeTemplates(self, note_type_id_str: str) -> str:
        """Get templates for a note type.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            
        Returns:
            JSON-encoded list of templates.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            templates = service.get_templates(note_type_id)
            if templates is None:
                return json.dumps({
                    "success": False,
                    "error": f"Note type {note_type_id} not found"
                })
            return json.dumps({
                "success": True,
                "templates": [t.to_dict() for t in templates]
            })
        except Exception as e:
            logger.error(f"Error getting templates for {note_type_id}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def getNoteTypeCss(self, note_type_id_str: str) -> str:
        """Get CSS for a note type.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            
        Returns:
            JSON-encoded CSS string.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            css = service.get_css(note_type_id)
            if css is None:
                return json.dumps({
                    "success": False,
                    "error": f"Note type {note_type_id} not found"
                })
            return json.dumps({
                "success": True,
                "css": css
            })
        except Exception as e:
            logger.error(f"Error getting CSS for {note_type_id}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, int, str, str, result=str)
    def updateTemplate(self, note_type_id_str: str, template_ordinal: int, 
                       front: str, back: str) -> str:
        """Update a card template.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            template_ordinal: The template index (0-based).
            front: New front template HTML.
            back: New back template HTML.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            # Allow empty string to mean "don't update"
            front_val = front if front else None
            back_val = back if back else None
            
            result = service.update_template(
                note_type_id, template_ordinal, 
                front=front_val, back=back_val
            )
            
            if result:
                logger.info(f"Updated template {template_ordinal} for note type {note_type_id}")
            
            return json.dumps({
                "success": result
            })
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, str, result=str)
    def updateNoteTypeCss(self, note_type_id_str: str, css: str) -> str:
        """Update CSS for a note type.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            css: New CSS content.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            result = service.update_css(note_type_id, css)
            
            if result:
                logger.info(f"Updated CSS for note type {note_type_id}")
            
            return json.dumps({
                "success": result
            })
        except Exception as e:
            logger.error(f"Error updating CSS: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, int, str, result=str)
    def renderPreview(self, note_type_id_str: str, template_ordinal: int, 
                      field_data_json: str) -> str:
        """Render a preview of a card.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            template_ordinal: The template index (0-based).
            field_data_json: JSON-encoded field data dict.
            
        Returns:
            JSON-encoded preview with front, back, and CSS.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            field_data = json.loads(field_data_json) if field_data_json else None
            preview = service.render_preview(note_type_id, template_ordinal, field_data)
            
            if preview is None:
                return json.dumps({
                    "success": False,
                    "error": f"Could not render preview for note type {note_type_id}"
                })
            
            return json.dumps({
                "success": True,
                "preview": preview
            })
        except Exception as e:
            logger.error(f"Error rendering preview: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def getSampleData(self, note_type_id_str: str) -> str:
        """Get sample field data for a note type.
        
        Args:
            note_type_id_str: The note type ID as string (to support 64-bit IDs).
            
        Returns:
            JSON-encoded sample data dict.
        """
        from ..services.note_type_service import get_note_type_service
        
        service = get_note_type_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Note type service not initialized"
            })
        
        try:
            note_type_id = int(note_type_id_str)
            sample = service.get_sample_data(note_type_id)
            
            if sample is None:
                return json.dumps({
                    "success": False,
                    "error": f"Note type {note_type_id} not found"
                })
            
            return json.dumps({
                "success": True,
                "sampleData": sample
            })
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    # ===== Selection Methods (Plan 12) =====
    
    @pyqtSlot(result=str)
    def getSelection(self) -> str:
        """Get current selection state.
        
        Returns:
            JSON-encoded selection state.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        return json.dumps({
            "success": True,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def selectComponent(self, component_id: str) -> str:
        """Select a single component (replacing current selection).
        
        Args:
            component_id: The component ID to select.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        result = service.select(component_id)
        return json.dumps({
            "success": True,
            "changed": result,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def addToSelection(self, component_id: str) -> str:
        """Add a component to selection (Ctrl+click).
        
        Args:
            component_id: The component ID to add.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        result = service.add_to_selection(component_id)
        return json.dumps({
            "success": True,
            "changed": result,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def removeFromSelection(self, component_id: str) -> str:
        """Remove a component from selection.
        
        Args:
            component_id: The component ID to remove.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        result = service.remove_from_selection(component_id)
        return json.dumps({
            "success": True,
            "changed": result,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def toggleSelection(self, component_id: str) -> str:
        """Toggle a component's selection state.
        
        Args:
            component_id: The component ID to toggle.
            
        Returns:
            JSON-encoded result with isSelected state.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        is_selected = service.toggle_selection(component_id)
        return json.dumps({
            "success": True,
            "isSelected": is_selected,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(result=str)
    def clearSelection(self) -> str:
        """Clear all selection.
        
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        result = service.clear()
        return json.dumps({
            "success": True,
            "changed": result,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def setSelection(self, selection_json: str) -> str:
        """Set selection to specific components.
        
        Args:
            selection_json: JSON with componentIds and optional primaryId.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        try:
            data = json.loads(selection_json)
            component_ids = data.get("componentIds", [])
            primary_id = data.get("primaryId")
            
            result = service.set_selection(component_ids, primary_id)
            return json.dumps({
                "success": True,
                "changed": result,
                "selection": service.get_state_dict()
            })
        except Exception as e:
            logger.error(f"Error setting selection: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def selectRange(self, to_component_id: str) -> str:
        """Select a range from primary to target (Shift+click).
        
        Args:
            to_component_id: The end component of the range.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        result = service.select_range(to_component_id)
        return json.dumps({
            "success": True,
            "changed": result,
            "selection": service.get_state_dict()
        })
    
    @pyqtSlot(str, result=str)
    def setComponentOrder(self, order_json: str) -> str:
        """Set component order for range selection.
        
        Args:
            order_json: JSON array of component IDs in display order.
            
        Returns:
            JSON-encoded result.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        try:
            order = json.loads(order_json)
            service.set_component_order(order)
            return json.dumps({
                "success": True,
                "count": len(order)
            })
        except Exception as e:
            logger.error(f"Error setting component order: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @pyqtSlot(str, result=str)
    def moveSelection(self, direction: str) -> str:
        """Move selection in a direction (keyboard navigation).
        
        Args:
            direction: "next", "prev", "first", or "last"
            
        Returns:
            JSON-encoded result with new selection.
        """
        from ..services.selection_service import get_selection_service
        
        service = get_selection_service()
        if service is None:
            return json.dumps({
                "success": False,
                "error": "Selection service not initialized"
            })
        
        new_id = service.move_selection(direction)
        return json.dumps({
            "success": True,
            "newId": new_id,
            "selection": service.get_state_dict()
        })