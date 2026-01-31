"""
Anki Template Designer Add-on
Build and preview card templates for Anki Desktop and AnkiDroid

GrapeJS-based visual template builder with AnkiDroidJS API integration.
"""

# CRITICAL: This runs FIRST, before any other code
import sys
import os

trace_file = None
try:
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    trace_file = os.path.join(addon_dir, "addon_trace.txt")
    with open(trace_file, "w", encoding="utf-8") as f:
        f.write("ADDON __init__.py LOADED\n")
except Exception as trace_error:
    import traceback
    if trace_file:
        try:
            with open(trace_file, "a", encoding="utf-8") as f:
                f.write(f"ERROR WRITING TRACE: {trace_error}\n")
                f.write(traceback.format_exc())
        except:
            pass

# Only import when running within Anki environment
try:
    from aqt import mw, gui_hooks
    from aqt.utils import showInfo
    import logging
    
    with open(trace_file, "a") as f:
        f.write("Anki modules imported\n")
    
    # Initialize logging FIRST before anything else
    def _setup_logging():
        """Set up logging from addon settings."""
        with open(trace_file, "a") as f:
            f.write("_setup_logging() called\n")
        try:
            from .utils import configure_logging, get_logger, install_exception_logging, install_qt_message_handler
            
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

            # ALWAYS enable file logging, not just when debugLogging is set
            configure_logging(log_level=log_level, log_file=log_file, enable_file_logging=True)
            logger = get_logger('addon_init')
            logger.info("=" * 70)
            logger.info("Template Designer addon logging initialized")
            logger.info("=" * 70)
            
            with open(trace_file, "a") as f:
                f.write("Logging configured\n")

            install_exception_logging(logger)
            install_qt_message_handler(logger)
        except Exception as e:
            with open(trace_file, "a") as f:
                f.write(f"ERROR in _setup_logging: {e}\n")
                import traceback
                f.write(traceback.format_exc())
            raise

    # Try to set up logging early
    try:
        with open(trace_file, "a") as f:
            f.write("Calling _setup_logging()...\n")
        _setup_logging()
        with open(trace_file, "a") as f:
            f.write("_setup_logging() completed\n")
    except Exception as e:
        with open(trace_file, "a") as f:
            f.write(f"Failed to setup logging: {e}\n")
            import traceback
            f.write(traceback.format_exc())
    
    # Import and initialize only when Anki is fully loaded
    def on_profile_loaded():
        """Initialize add-on after profile is loaded."""
        with open(trace_file, "a") as f:
            f.write("on_profile_loaded() called\n")
        try:
            from .hooks.menu import setup_menu
            setup_menu()
            with open(trace_file, "a") as f:
                f.write("Menu setup complete\n")
            try:
                logger = get_logger('addon_init')
                logger.info("Addon initialized successfully")
            except:
                pass
        except Exception as e:
            with open(trace_file, "a") as f:
                f.write(f"ERROR in on_profile_loaded: {e}\n")
                import traceback
                f.write(traceback.format_exc())
            try:
                logger = get_logger('addon_init')
                logger.error("Initialization failed: %s", e, exc_info=True)
            except:
                pass
    
    # Wait for profile to load before initializing
    with open(trace_file, "a") as f:
        f.write("Registering profile_did_open hook\n")
    gui_hooks.profile_did_open.append(on_profile_loaded)
    with open(trace_file, "a") as f:
        f.write("Hook registered\n")
    
    __all__ = ['on_profile_loaded']
    
except ImportError as e:
    # Running in test environment or outside Anki
    with open(trace_file, "a") as f:
        f.write(f"ImportError (outside Anki): {e}\n")
    __all__ = []
except Exception as e:
    with open(trace_file, "a") as f:
        f.write(f"Unexpected error: {e}\n")
        import traceback
        f.write(traceback.format_exc())
    __all__ = []

