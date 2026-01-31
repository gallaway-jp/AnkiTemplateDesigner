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
