"""
Logging configuration for Template Designer
"""

import logging
import logging.handlers
import os
import sys
import threading


def configure_logging(log_level=logging.INFO, log_file=None, enable_file_logging=True, enable_console_logging=True):
    """
    Configure application-wide logging.
    
    Args:
        log_level: Minimum logging level (default: INFO)
        log_file: Optional log file path (default: template_designer.log in user dir)
    
    Returns:
        Root logger for template_designer
    """
    # Root logger for template_designer
    logger = logging.getLogger('template_designer')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    if enable_console_logging:
        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        ))
        logger.addHandler(console)
    
    # File handler (DEBUG+) with rotation
    if enable_file_logging:
        if log_file is None:
            # Try to use user's home directory, fall back to temp
            try:
                home = os.path.expanduser('~')
                log_dir = os.path.join(home, '.anki_template_designer')
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, 'template_designer.log')
            except Exception:
                # Fall back to current directory
                log_file = 'template_designer.log'
        
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(file_handler)
        except Exception as e:
            # If file handler fails, at least log to console
            logger.warning(f"Could not create log file handler: {e}")
    
    logger.debug("Logging configured")
    return logger


def install_exception_logging(logger=None):
    """
    Install global exception handlers to capture uncaught exceptions.
    """
    if logger is None:
        logger = get_logger('exceptions')

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    if hasattr(threading, 'excepthook'):
        def handle_thread_exception(args):
            logger.exception(
                "Uncaught thread exception",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
            )
        threading.excepthook = handle_thread_exception


def install_qt_message_handler(logger=None):
    """
    Install Qt message handler to capture Qt warnings/errors.
    """
    if logger is None:
        logger = get_logger('qt')

    try:
        try:
            from aqt.qt import qInstallMessageHandler, QtMsgType
        except Exception:
            from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

        def handler(msg_type, context, message):
            # Filter out harmless Qt warnings about signal disconnections
            # These are normal during widget cleanup and don't indicate actual problems
            if "QObject::disconnect: wildcard call disconnects" in message:
                return  # Silently ignore these
            
            if msg_type == QtMsgType.QtCriticalMsg:
                logger.error("Qt critical: %s", message)
            elif msg_type == QtMsgType.QtFatalMsg:
                logger.error("Qt fatal: %s", message)
            elif msg_type == QtMsgType.QtWarningMsg:
                logger.warning("Qt warning: %s", message)
            elif msg_type == QtMsgType.QtInfoMsg:
                logger.info("Qt info: %s", message)
            else:
                logger.debug("Qt debug: %s", message)

        qInstallMessageHandler(handler)
    except Exception as e:
        logger.warning("Failed to install Qt message handler: %s", e)


def get_logger(name):
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (will be prefixed with 'template_designer.')
    
    Returns:
        Logger instance
    
    Example:
        >>> logger = get_logger('ui.designer_dialog')
        >>> logger.info("Dialog opened")
    """
    if not name.startswith('template_designer.'):
        name = f'template_designer.{name}'
    return logging.getLogger(name)


# Configure on import with default settings
configure_logging()
