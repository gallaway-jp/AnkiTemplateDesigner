"""
Base Dialog for Template Designer

Extracts common functionality from dialog classes to reduce duplication.
Implements Template Method pattern for dialog lifecycle.
"""

from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Any, List

from aqt.qt import QDialog, QMessageBox
from aqt import mw
from aqt.utils import showInfo

from services import ServiceContainer, TemplateService
from renderers import BaseRenderer
from .template_converter import TemplateConverter
from .components import Component


# Create a combined metaclass to resolve the conflict
class QDialogABCMeta(type(QDialog), ABCMeta):
    """Combined metaclass for QDialog and ABC"""
    pass


class BaseTemplateDialog(QDialog, metaclass=QDialogABCMeta):
    """
    Abstract base class for template designer dialogs.
    
    Provides common functionality:
    - Service injection (DI)
    - Note type loading
    - Template saving
    - Preview management
    - Common lifecycle hooks
    
    Subclasses must implement:
    - setup_ui(): Create UI layout
    - sync_to_preview(): Update preview from current state
    """
    
    def __init__(
        self,
        services: ServiceContainer,
        parent: Optional[QDialog] = None,
        note_type: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the base dialog.
        
        Args:
            services: Service container for dependency injection
            parent: Parent widget
            note_type: Note type to edit (loads first if None)
        """
        super().__init__(parent)
        
        # Dependency injection
        self.services = services
        self.template_service: TemplateService = services.get('template_service')
        self.desktop_renderer: BaseRenderer = services.get('desktop_renderer')
        self.ankidroid_renderer: BaseRenderer = services.get('ankidroid_renderer')
        
        # State
        self.note_type = note_type
        self.config = mw.addonManager.getConfig(__name__.split('.')[0])
        self.current_side = 'front'
        
        # Template method pattern - call hooks in order
        self.setup_ui()
        self.load_note_type()
    
    @abstractmethod
    def setup_ui(self) -> None:
        """
        Setup the dialog UI.
        
        Subclasses must implement to create their specific layout.
        """
        pass
    
    @abstractmethod
    def sync_to_preview(self) -> None:
        """
        Sync current state to preview widget.
        
        Subclasses must implement to update preview from their
        specific editor (visual builder, code editor, etc.).
        """
        pass
    
    def load_note_type(self) -> None:
        """
        Load note type and templates.
        
        Common implementation that can be overridden if needed.
        """
        try:
            # Load note type if not provided
            if not self.note_type:
                self.note_type = self.template_service.load_note_type()
            
            if self.note_type:
                self.on_note_type_loaded()
            
        except Exception as e:
            import logging
            logging.error(f"Error loading note type: {e}")
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load note type: {e}"
            )
    
    def on_note_type_loaded(self) -> None:
        """
        Hook called after note type is successfully loaded.
        
        Subclasses can override to perform additional setup.
        Default implementation does nothing.
        """
        pass
    
    def save_to_anki(self) -> None:
        """
        Save templates back to Anki.
        
        Common implementation with proper validation and error handling.
        """
        if not self.note_type:
            showInfo("No note type selected.")
            return
        
        # Get templates from subclass
        templates = self.get_templates_to_save()
        
        if not templates:
            showInfo("No templates to save.")
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Save Templates",
            f"Save changes to note type '{self.note_type['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Use service to save (includes validation)
            self.template_service.save_templates(self.note_type, templates)
            showInfo("Templates saved successfully!")
            self.on_templates_saved()
            
        except Exception as e:
            import logging
            logging.error(f"Error saving templates: {e}")
            showInfo(f"Error saving templates: {str(e)}")
    
    @abstractmethod
    def get_templates_to_save(self) -> List[Dict[str, Any]]:
        """
        Get templates to save from current editor state.
        
        Subclasses must implement to return template list.
        
        Returns:
            List of template dictionaries
        """
        pass
    
    def on_templates_saved(self) -> None:
        """
        Hook called after templates are successfully saved.
        
        Subclasses can override to perform additional actions.
        Default implementation does nothing.
        """
        pass
    
    def get_sample_note(self) -> Optional[Any]:
        """
        Get a sample note for preview.
        
        Returns:
            Note instance or None
        """
        if not self.note_type:
            return None
        
        return self.template_service.get_sample_note(self.note_type)
    
    def set_side(self, side: str) -> None:
        """
        Set which side of the card to preview (front/back).
        
        Args:
            side: 'front' or 'back'
        """
        self.current_side = side
        self.on_side_changed()
    
    def on_side_changed(self) -> None:
        """
        Hook called when side changes.
        
        Subclasses can override to update UI.
        Default implementation updates preview.
        """
        self.sync_to_preview()
    
    def handle_validation_error(self, error: Exception) -> None:
        """
        Handle validation errors with user-friendly message.
        
        Args:
            error: Exception that occurred
        """
        QMessageBox.warning(
            self,
            "Validation Error",
            str(error)
        )
    
    def handle_error(self, error: Exception, operation: str = "operation") -> None:
        """
        Handle general errors with logging and user notification.
        
        Args:
            error: Exception that occurred
            operation: Description of operation that failed
        """
        import logging
        logging.error(f"Error during {operation}: {error}")
        QMessageBox.warning(
            self,
            "Error",
            f"Failed to {operation}: {str(error)}"
        )
