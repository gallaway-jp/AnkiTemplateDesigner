"""Bridge for Python <-> JavaScript communication via QWebChannel."""

from typing import Callable, Any, Optional
import json

try:
    from aqt.qt import QObject, pyqtSlot, pyqtSignal
except ImportError:
    # Fallback for testing without Anki
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal


class WebViewBridge(QObject):
    """Bridge object exposed to JavaScript for bidirectional communication.
    
    JavaScript calls methods via: window.bridge.methodName(args)
    Python emits signals that JavaScript listens to.
    """
    
    # Signals (Python -> JavaScript)
    templateLoaded = pyqtSignal(str)        # Emit GrapeJS JSON to load
    fieldsUpdated = pyqtSignal(str)         # Emit available Anki fields
    behaviorsUpdated = pyqtSignal(str)      # Emit AnkiJSApi behaviors
    settingsUpdated = pyqtSignal(str)       # Emit editor settings
    
    def __init__(self, parent=None):
        """Initialize bridge with optional parent."""
        super().__init__(parent)
        self._save_callback: Optional[Callable] = None
        self._preview_callback: Optional[Callable] = None
        self._export_callback: Optional[Callable] = None
    
    # ========== JavaScript -> Python Slots ==========
    
    @pyqtSlot(str)
    def saveProject(self, grapejs_json: str):
        """Called by JS when user saves the project.
        
        Args:
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._save_callback:
            try:
                # Parse JSON
                data = json.loads(grapejs_json)
                
                # Validate template structure
                errors = self._validate_template_data(data)
                if errors:
                    error_message = self._format_error_message(errors)
                    self.showError(error_message)
                    return
                
                # Proceed with save
                self._save_callback(data)
                
            except json.JSONDecodeError as e:
                self.showError(
                    f"Invalid template data:\n\n"
                    f"The template couldn't be saved due to a data format error.\n"
                    f"Error: {e}\n\n"
                    f"Try:\n"
                    f"• Refresh the page and try again\n"
                    f"• Check the browser console for more details"
                )
            except Exception as e:
                self.showError(
                    f"Unexpected error while saving:\n\n"
                    f"{str(e)}\n\n"
                    f"Please try again or contact support if the problem persists."
                )
    
    def _validate_template_data(self, data: dict) -> list:
        """Validate template structure and return list of errors."""
        errors = []
        
        # Check if data is empty
        if not data:
            errors.append("Template data is empty")
            return errors
        
        # Check for components
        components = data.get('components', [])
        if not components:
            errors.append("Template must have at least one component")
        
        # Check for HTML
        html = data.get('html', '')
        if not html:
            errors.append("Template must have HTML content")
        
        # Check for Anki field syntax errors
        if '{{' in html:
            # Count opening and closing braces
            opening_braces = html.count('{{')
            closing_braces = html.count('}}')
            if opening_braces != closing_braces:
                errors.append(
                    f"Mismatched Anki field references: "
                    f"{opening_braces} opening '{{{{' but {closing_braces} closing '}}}}'\n"
                    f"• Check all field references have matching closing braces"
                )
        
        # Check for common issues
        if '<%' in html or '%>' in html:
            errors.append(
                "Template uses old-style template syntax (<% %>)\n"
                "• Use Anki field references instead: {{FieldName}}"
            )
        
        return errors
    
    def _format_error_message(self, errors: list) -> str:
        """Format error messages for display to user."""
        if not errors:
            return "Unknown error"
        
        if len(errors) == 1:
            return f"Cannot save template:\n\n{errors[0]}"
        
        error_list = "\n\n".join(f"• {e}" for e in errors)
        return f"Cannot save template:\n\n{error_list}\n\nFix these issues and try again."
    
    @pyqtSlot(str)
    def requestPreview(self, grapejs_json: str):
        """Called by JS to request a card preview.
        
        Args:
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._preview_callback:
            try:
                data = json.loads(grapejs_json)
                self._preview_callback(data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str, str)
    def exportTemplate(self, format_type: str, grapejs_json: str):
        """Called by JS to export template.
        
        Args:
            format_type: Export format ('html', 'json', etc.)
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._export_callback:
            try:
                data = json.loads(grapejs_json)
                self._export_callback(format_type, data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str)
    def log(self, message: str):
        """Called by JS for debug logging.
        
        Args:
            message: Log message from JavaScript
        """
        print(f"[GrapeJS] {message}")
    
    @pyqtSlot(str)
    def showError(self, message: str):
        """Called by JS to show error to user.
        
        Args:
            message: Error message to display
        """
        try:
            from aqt.utils import showWarning
            showWarning(message, title="Template Designer Error")
        except ImportError:
            # Fallback if Anki not available
            print(f"ERROR: {message}")
    
    @pyqtSlot(result=str)
    def getAnkiFields(self) -> str:
        """Called by JS to get available Anki fields.
        
        Returns:
            JSON string array of field names
        """
        # Placeholder - real implementation would query Anki
        fields = ["Front", "Back", "Extra", "Tags", "Type"]
        return json.dumps(fields)
    
    @pyqtSlot(result=str)
    def getAnkiBehaviors(self) -> str:
        """Called by JS to get AnkiJSApi behaviors.
        
        Returns:
            JSON string array of behavior objects
        """
        from ..services.ankijsapi_service import AnkiJSApiService
        service = AnkiJSApiService()
        behaviors = service.get_available_behaviors()
        return json.dumps(behaviors)
    
    # ========== Python API ==========
    
    def set_save_callback(self, callback: Callable[[dict], None]):
        """Set callback for save action.
        
        Args:
            callback: Function(grapejs_data: dict) -> None
        """
        self._save_callback = callback
    
    def set_preview_callback(self, callback: Callable[[dict], None]):
        """Set callback for preview action.
        
        Args:
            callback: Function(grapejs_data: dict) -> None
        """
        self._preview_callback = callback
    
    def set_export_callback(self, callback: Callable[[str, dict], None]):
        """Set callback for export action.
        
        Args:
            callback: Function(format_type: str, grapejs_data: dict) -> None
        """
        self._export_callback = callback
    
    def load_template(self, grapejs_json: dict):
        """Load a template into the editor.
        
        Args:
            grapejs_json: GrapeJS project data as dict
        """
        self.templateLoaded.emit(json.dumps(grapejs_json))
    
    def update_fields(self, fields: list):
        """Update available Anki fields in editor.
        
        Args:
            fields: List of field names
        """
        self.fieldsUpdated.emit(json.dumps(fields))
    
    def update_behaviors(self, behaviors: list):
        """Update available AnkiJSApi behaviors in editor.
        
        Args:
            behaviors: List of behavior dictionaries
        """
        self.behaviorsUpdated.emit(json.dumps(behaviors))
