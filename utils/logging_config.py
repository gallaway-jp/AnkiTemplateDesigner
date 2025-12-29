"""
Logging configuration for Template Designer
"""

import logging
import logging.handlers
import os


def configure_logging(log_level=logging.INFO, log_file=None):
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
    
    # Console handler (INFO+)
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    ))
    logger.addHandler(console)
    
    # File handler (DEBUG+) with rotation
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
