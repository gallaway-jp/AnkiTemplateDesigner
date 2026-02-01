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
    
    All exceptions are caught and logged to prevent Anki error dialogs.
    """
    global _designer_dialog
    
    try:
        from .gui.designer_dialog import DesignerDialog
        from aqt import mw
        
        if _designer_dialog is None or not _designer_dialog.isVisible():
            _designer_dialog = DesignerDialog(mw)
        
        _designer_dialog.show()
        _designer_dialog.raise_()
        _designer_dialog.activateWindow()
        
    except Exception as e:
        import logging
        logger = logging.getLogger("anki_template_designer")
        logger.error(f"Failed to open designer dialog: {e}", exc_info=True)
        
        # Show user-friendly error in Anki instead of crash dialog
        try:
            from aqt.utils import showWarning
            showWarning(
                f"Failed to open Template Designer:\n\n{str(e)}\n\n"
                f"Check Tools → Add-ons → Template Designer → View Files → logs for details.",
                title="Template Designer Error"
            )
        except Exception:
            # If even showing warning fails, just log it
            logger.error("Could not display error dialog to user")


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
    All exceptions are caught and logged to prevent Anki error dialogs.
    """
    global _initialized
    
    if _initialized:
        return
    
    import logging
    logger = logging.getLogger("anki_template_designer")
    
    try:
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
        
        # Initialize performance optimizer
        from .services.performance import init_optimizer
        init_optimizer()
        logger.debug("Performance optimizer initialized")
        
        # Initialize backup manager
        from .services.backup_manager import init_backup_manager
        addon_dir = _get_addon_dir()
        backup_dir = os.path.join(addon_dir, "backups")
        templates_dir = os.path.join(addon_dir, "templates")
        init_backup_manager(backup_dir, templates_dir)
        logger.debug("Backup manager initialized")
        
        # Initialize plugin manager
        from .services.plugin_system import init_plugin_manager
        plugins_dir = os.path.join(addon_dir, "plugins")
        data_dir = os.path.join(addon_dir, "plugin_data")
        init_plugin_manager(plugins_dir, data_dir)
        logger.debug("Plugin manager initialized")
        
        # Initialize shortcuts manager
        from .services.shortcuts_manager import init_shortcuts_manager
        init_shortcuts_manager()
        logger.debug("Shortcuts manager initialized")
        
        _setup_menu()
        _initialized = True
        
        logger.debug("Anki Template Designer initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        # Don't raise - just log the error and continue
        # The addon menu item won't be added, but Anki will continue normally


# Only run initialization when in Anki environment
try:
    from aqt import gui_hooks
    import sys
    import io
    
    # Wrap all initialization in try-except to prevent error dialogs
    try:
        # Temporarily suppress stderr to prevent Anki error dialog
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        try:
            _setup_logging()
            _setup_config_service()
            gui_hooks.profile_did_open.append(_on_profile_loaded)
        finally:
            # Restore stderr
            sys.stderr = old_stderr
            
    except Exception as e:
        import logging
        # Restore stderr if it wasn't already
        if 'old_stderr' in locals():
            sys.stderr = old_stderr
        # Create a basic logger if setup_logging failed
        logging.basicConfig(level=logging.ERROR)
        logger = logging.getLogger("anki_template_designer")
        logger.error(f"Failed to initialize addon: {e}", exc_info=True)
        # Don't re-raise - let Anki continue
    
except ImportError:
    # Not running in Anki - allow for testing
    pass
