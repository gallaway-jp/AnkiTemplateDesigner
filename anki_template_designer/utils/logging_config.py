"""
Logging configuration for Anki Template Designer.

Plan 09: Implements comprehensive logging with configurable levels,
file output, rotation, and debug mode toggle.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from pathlib import Path


# Module-level constants
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_BACKUP_COUNT = 3
LOG_FILE_NAME = "template_designer.log"

# Global state
_initialized = False
_debug_mode = False
_log_dir: Optional[Path] = None
_file_handler: Optional[RotatingFileHandler] = None


class LoggingConfig:
    """Manages logging configuration for the addon.
    
    Provides:
    - Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File-based logging with rotation
    - Console logging for development
    - Debug mode toggle for verbose output
    - Structured log format
    
    Example usage:
        # Initialize logging
        config = LoggingConfig(addon_dir="/path/to/addon")
        config.setup()
        
        # Enable debug mode
        config.set_debug_mode(True)
        
        # Get a logger
        logger = config.get_logger("my_module")
        logger.info("Hello world")
    """
    
    def __init__(
        self,
        addon_dir: Optional[str] = None,
        log_level: int = DEFAULT_LOG_LEVEL,
        log_to_file: bool = True,
        log_to_console: bool = True,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT
    ) -> None:
        """Initialize logging configuration.
        
        Args:
            addon_dir: Addon directory for log file storage.
            log_level: Initial logging level.
            log_to_file: Whether to write logs to file.
            log_to_console: Whether to output logs to console.
            max_bytes: Maximum log file size before rotation.
            backup_count: Number of backup files to keep.
        """
        self._addon_dir = Path(addon_dir) if addon_dir else None
        self._log_level = log_level
        self._log_to_file = log_to_file
        self._log_to_console = log_to_console
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._debug_mode = False
        self._handlers: Dict[str, logging.Handler] = {}
        self._root_logger_name = "anki_template_designer"
    
    @property
    def log_dir(self) -> Optional[Path]:
        """Get the log directory path."""
        if self._addon_dir:
            return self._addon_dir / "logs"
        return None
    
    @property
    def log_file(self) -> Optional[Path]:
        """Get the log file path."""
        if self.log_dir:
            return self.log_dir / LOG_FILE_NAME
        return None
    
    @property
    def debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self._debug_mode
    
    def setup(self) -> None:
        """Set up logging handlers and configuration.
        
        Creates the log directory if needed and configures handlers.
        """
        global _initialized, _log_dir
        
        # Get root logger for our addon
        root_logger = logging.getLogger(self._root_logger_name)
        root_logger.setLevel(logging.DEBUG)  # Capture all, handlers filter
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        
        # Set up file handler
        if self._log_to_file and self.log_dir:
            self._setup_file_handler(formatter)
        
        # Set up console handler
        if self._log_to_console:
            self._setup_console_handler(formatter)
        
        _initialized = True
        _log_dir = self.log_dir
        
        # Log startup message
        logger = self.get_logger("logging_config")
        logger.info(f"Logging initialized (level={logging.getLevelName(self._log_level)})")
        if self.log_file:
            logger.debug(f"Log file: {self.log_file}")
    
    def _setup_file_handler(self, formatter: logging.Formatter) -> None:
        """Set up the rotating file handler.
        
        Args:
            formatter: Log formatter to use.
        """
        global _file_handler
        
        try:
            # Create log directory if needed
            if self.log_dir and not self.log_dir.exists():
                self.log_dir.mkdir(parents=True, exist_ok=True)
            
            if self.log_file:
                handler = RotatingFileHandler(
                    filename=str(self.log_file),
                    maxBytes=self._max_bytes,
                    backupCount=self._backup_count,
                    encoding="utf-8"
                )
                handler.setLevel(self._log_level)
                handler.setFormatter(formatter)
                
                root_logger = logging.getLogger(self._root_logger_name)
                root_logger.addHandler(handler)
                
                self._handlers["file"] = handler
                _file_handler = handler
                
        except Exception as e:
            # Can't log this error to file, use stderr
            print(f"Failed to setup file logging: {e}", file=sys.stderr)
    
    def _setup_console_handler(self, formatter: logging.Formatter) -> None:
        """Set up the console (stderr) handler.
        
        Args:
            formatter: Log formatter to use.
        """
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(self._log_level)
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger(self._root_logger_name)
        root_logger.addHandler(handler)
        
        self._handlers["console"] = handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module.
        
        Args:
            name: Module name (will be prefixed with addon name).
            
        Returns:
            Logger instance.
        """
        full_name = f"{self._root_logger_name}.{name}"
        return logging.getLogger(full_name)
    
    def set_log_level(self, level: int) -> None:
        """Set the log level for all handlers.
        
        Args:
            level: Logging level (e.g., logging.DEBUG).
        """
        self._log_level = level
        
        for handler in self._handlers.values():
            handler.setLevel(level)
        
        logger = self.get_logger("logging_config")
        logger.info(f"Log level changed to {logging.getLevelName(level)}")
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode.
        
        Debug mode sets log level to DEBUG for verbose output.
        
        Args:
            enabled: Whether to enable debug mode.
        """
        self._debug_mode = enabled
        
        if enabled:
            self.set_log_level(logging.DEBUG)
        else:
            self.set_log_level(DEFAULT_LOG_LEVEL)
        
        logger = self.get_logger("logging_config")
        logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
    
    def get_log_contents(self, lines: int = 100) -> str:
        """Get recent log file contents.
        
        Args:
            lines: Number of lines to retrieve.
            
        Returns:
            Last N lines of the log file.
        """
        if not self.log_file or not self.log_file.exists():
            return ""
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except Exception as e:
            return f"Error reading log file: {e}"
    
    def clear_logs(self) -> bool:
        """Clear all log files.
        
        Returns:
            True if successful.
        """
        if not self.log_dir:
            return False
        
        try:
            for log_file in self.log_dir.glob("*.log*"):
                log_file.unlink()
            
            logger = self.get_logger("logging_config")
            logger.info("Log files cleared")
            return True
        except Exception as e:
            print(f"Failed to clear logs: {e}", file=sys.stderr)
            return False
    
    def shutdown(self) -> None:
        """Shutdown logging and close all handlers.
        
        Call this before cleanup to release file handles.
        """
        global _initialized, _file_handler
        
        root_logger = logging.getLogger(self._root_logger_name)
        
        # Close and remove all handlers
        for name, handler in list(self._handlers.items()):
            try:
                handler.close()
                root_logger.removeHandler(handler)
            except Exception:
                pass
        
        self._handlers.clear()
        _file_handler = None
        _initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current logging status.
        
        Returns:
            Dictionary with logging status information.
        """
        status = {
            "initialized": _initialized,
            "debug_mode": self._debug_mode,
            "log_level": logging.getLevelName(self._log_level),
            "log_to_file": self._log_to_file,
            "log_to_console": self._log_to_console,
            "log_file": str(self.log_file) if self.log_file else None,
            "handlers": list(self._handlers.keys())
        }
        
        # Add file size if exists
        if self.log_file and self.log_file.exists():
            status["log_file_size"] = self.log_file.stat().st_size
        
        return status


# Global logging config instance
_global_config: Optional[LoggingConfig] = None


def setup_logging(
    addon_dir: Optional[str] = None,
    debug: bool = False,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> LoggingConfig:
    """Set up global logging configuration.
    
    Convenience function for initializing logging.
    
    Args:
        addon_dir: Addon directory path.
        debug: Whether to enable debug mode.
        log_to_file: Whether to log to file.
        log_to_console: Whether to log to console.
        
    Returns:
        LoggingConfig instance.
    """
    global _global_config
    
    config = LoggingConfig(
        addon_dir=addon_dir,
        log_level=logging.DEBUG if debug else DEFAULT_LOG_LEVEL,
        log_to_file=log_to_file,
        log_to_console=log_to_console
    )
    config.setup()
    
    if debug:
        config.set_debug_mode(True)
    
    _global_config = config
    return config


def get_logging_config() -> Optional[LoggingConfig]:
    """Get the global logging configuration.
    
    Returns:
        LoggingConfig instance or None if not initialized.
    """
    return _global_config


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module.
    
    Convenience function that uses global config if available.
    
    Args:
        name: Module name.
        
    Returns:
        Logger instance.
    """
    if _global_config:
        return _global_config.get_logger(name)
    
    # Fallback to standard logger
    return logging.getLogger(f"anki_template_designer.{name}")
