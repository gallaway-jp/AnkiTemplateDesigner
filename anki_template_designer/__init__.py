"""
Anki Template Designer Add-on

A visual template designer for creating Anki flashcard templates.
Uses GrapeJS for drag-and-drop template building.

Author: Anki Template Designer Contributors
License: MIT
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Anki Template Designer Contributors"

import os
import sys
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .gui.designer_dialog import DesignerDialog

# Module-level variables for lazy initialization
_initialized: bool = False
_designer_dialog: Optional["DesignerDialog"] = None


def _get_addon_dir() -> str:
    """Get the addon directory path.
    
    Returns:
        Absolute path to the addon directory.
    """
    return os.path.dirname(os.path.abspath(__file__))


def _setup_logging() -> None:
    """Initialize logging for the addon.
    
    Sets up file and console logging using LoggingConfig.
    Should be called early in addon initialization.
    """
    from .utils.logging_config import setup_logging
    
    config = _load_config()
    debug = config.get("debugLogging", False)
    
    setup_logging(
        addon_dir=_get_addon_dir(),
        debug=debug,
        log_to_file=True,
        log_to_console=True
    )


def _setup_config_service() -> None:
    """Initialize the configuration service.
    
    Sets up ConfigService for centralized configuration management.
    """
    from .services.config_service import init_config_service
    
    init_config_service(addon_dir=_get_addon_dir())


def _load_config() -> dict:
    """Load addon configuration.
    
    Returns:
        Configuration dictionary with defaults merged with user settings.
    """
    import json
    
    config_path = os.path.join(_get_addon_dir(), "config.json")
    defaults = {
        "debugLogging": False,
        "logLevel": "INFO",
        "autoSave": True,
        "autoSaveIntervalSeconds": 30,
        "theme": "system",
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                defaults.update(user_config)
    except (json.JSONDecodeError, IOError) as e:
        import logging
        logging.getLogger("anki_template_designer").warning(
            f"Failed to load config: {e}"
        )
    
    return defaults


def open_designer() -> None:
    """Open the template designer dialog.
    
    Creates a new dialog instance or shows existing one.
    This is the main entry point for users.
    """
    global _designer_dialog
    
    from .gui.designer_dialog import DesignerDialog
    from aqt import mw
    
    if _designer_dialog is None or not _designer_dialog.isVisible():
        _designer_dialog = DesignerDialog(mw)
    
    _designer_dialog.show()
    _designer_dialog.raise_()
    _designer_dialog.activateWindow()


def _setup_menu() -> None:
    """Add addon menu item to Anki's Tools menu.
    
    Creates a menu action that opens the template designer.
    """
    from aqt import mw
    from aqt.qt import QAction
    
    action = QAction("Template Designer", mw)
    action.setShortcut("Ctrl+Shift+T")
    action.triggered.connect(open_designer)
    
    mw.form.menuTools.addAction(action)


def _on_profile_loaded() -> None:
    """Callback when Anki profile is loaded.
    
    Performs initialization that requires a loaded profile.
    """
    global _initialized
    
    if _initialized:
        return
    
    import logging
    logger = logging.getLogger("anki_template_designer")
    logger.debug("Anki Template Designer initializing...")
    
    # Initialize note type service with main window
    from .services.note_type_service import init_note_type_service
    from aqt import mw
    init_note_type_service(mw)
    logger.debug("Note type service initialized")
    
    # Initialize selection service
    from .services.selection_service import init_selection_service
    init_selection_service()
    logger.debug("Selection service initialized")
    
    _setup_menu()
    _initialized = True
    
    logger.debug("Anki Template Designer initialized successfully")


# Only run initialization when in Anki environment
try:
    from aqt import gui_hooks
    
    _setup_logging()
    _setup_config_service()
    gui_hooks.profile_did_open.append(_on_profile_loaded)
    
except ImportError:
    # Not running in Anki - allow for testing
    pass
