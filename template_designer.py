"""
Main entry point for the Anki Template Designer add-on
"""

from aqt import mw, gui_hooks
from aqt.qt import QAction
from aqt.utils import showInfo


# Global service container (initialized on first use)
_service_container = None


def get_service_container():
    """Get or create the global service container."""
    global _service_container
    
    if _service_container is None:
        _service_container = _create_service_container()
    
    return _service_container


def _create_service_container():
    """Create and configure the service container."""
    # Import heavy modules only when needed
    from .services import ServiceContainer, TemplateService
    from .renderers import DesktopRenderer, AnkiDroidRenderer
    from .utils import SecurityValidator
    
    container = ServiceContainer()
    
    # Register singletons
    container.register_singleton('collection', mw.col)
    container.register_singleton('security_validator', SecurityValidator())
    
    # Register factories (creates new instance each time)
    container.register_factory('desktop_renderer', lambda: DesktopRenderer())
    container.register_factory('ankidroid_renderer', lambda: AnkiDroidRenderer())
    
    # Register template service (depends on collection and security validator)
    container.register_factory(
        'template_service',
        lambda: TemplateService(
            container.get('collection'),
            container.get('security_validator')
        )
    )
    
    return container


def show_template_designer():
    """Show the template designer dialog"""
    # Import dialog only when needed (lazy loading)
    from .ui.android_studio_dialog import AndroidStudioDesignerDialog
    
    # Get the current note type
    note_types = mw.col.models.all_names_and_ids()
    
    if not note_types:
        showInfo("No note types found. Please create a note type first.")
        return
    
    # Get service container
    services = get_service_container()
    
    # Create and show the designer dialog (Android Studio style)
    dialog = AndroidStudioDesignerDialog(services, mw)
    dialog.exec()


def setup_menu():
    """Setup menu items"""
    action = QAction("Template Designer (Visual Editor)", mw)
    action.triggered.connect(show_template_designer)
    mw.form.menuTools.addAction(action)


def init_addon():
    """Initialize the add-on"""
    setup_menu()
    
    # Add hook to card layout screen
    gui_hooks.card_layout_will_show.append(on_card_layout_show)


def on_card_layout_show(clayout):
    """Add Template Designer button to card layout screen"""
    from aqt.qt import QPushButton
    
    btn = QPushButton("Visual Designer", clayout)
    btn.clicked.connect(lambda: show_template_designer_for_note_type(clayout.model))
    
    # Add button to the card layout dialog
    if hasattr(clayout, 'buttons'):
        clayout.buttons.addWidget(btn)

# Import dialog only when needed (lazy loading)
    from .ui.android_studio_dialog import AndroidStudioDesignerDialog
    
    
def show_template_designer_for_note_type(note_type):
    """Show template designer for a specific note type."""
    services = get_service_container()
    dialog = AndroidStudioDesignerDialog(services, mw, note_type=note_type)
    dialog.exec()
