"""
Main entry point for the Anki Template Designer add-on
"""

import logging
import os

from aqt import mw
from aqt.utils import showInfo

from .utils import configure_logging, get_logger, install_exception_logging, install_qt_message_handler


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
    from .gui.designer_dialog import TemplateDesignerDialog
    
    # Get the current note type
    note_types = mw.col.models.all_names_and_ids()
    
    if not note_types:
        showInfo("No note types found. Please create a note type first.")
        return
    
    # Create and show the designer dialog
    dialog = TemplateDesignerDialog(mw)
    dialog.exec()


def _configure_addon_logging():
    """Configure logging based on add-on settings."""
    config = {}
    try:
        config = mw.addonManager.getConfig(__name__) if mw and hasattr(mw, 'addonManager') else {}
    except Exception:
        config = {}

    debug_logging = bool(config.get('debugLogging', False))
    log_level_name = str(config.get('logLevel', 'INFO')).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_file = None
    if mw and hasattr(mw, 'addonManager'):
        try:
            data_dir = mw.addonManager.addonDataFolder(__name__)
            log_dir = os.path.join(data_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'anki_template_designer.log')
        except Exception:
            log_file = None

    configure_logging(log_level=log_level, log_file=log_file, enable_file_logging=debug_logging)
    logger = get_logger('init')
    logger.info("Logging initialized", extra={"debugLogging": debug_logging, "logLevel": log_level_name})

    install_exception_logging(logger)
    install_qt_message_handler(logger)
