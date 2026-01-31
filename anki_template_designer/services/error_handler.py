"""
Centralized Error Handler for Anki Template Designer.

Plan 08: Provides a central point for error handling, logging,
and user notification. Implements error recovery mechanisms.
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict, List
from functools import wraps
from datetime import datetime

from ..core.exceptions import (
    TemplateDesignerError,
    ErrorCode
)

logger = logging.getLogger("anki_template_designer.services.error_handler")


# Type for error listeners
ErrorListener = Callable[[Dict[str, Any]], None]


class ErrorHandler:
    """Centralized error handler with logging and notification support.
    
    Provides:
    - Centralized error logging with context
    - Error history for debugging
    - Listener pattern for UI notifications
    - Error recovery suggestions
    
    Example usage:
        handler = ErrorHandler()
        handler.add_listener(lambda err: show_error_toast(err))
        
        try:
            do_something()
        except Exception as e:
            handler.handle(e, context={"action": "save_template"})
    """
    
    # Maximum errors to keep in history
    MAX_HISTORY = 50
    
    # Recovery suggestions by error code
    RECOVERY_SUGGESTIONS: Dict[ErrorCode, str] = {
        ErrorCode.TEMPLATE_NOT_FOUND: "The template may have been deleted. Try refreshing the template list.",
        ErrorCode.TEMPLATE_SAVE_FAILED: "Check if you have write permissions. Try saving with a different name.",
        ErrorCode.TEMPLATE_LOAD_FAILED: "The template file may be corrupted. Try creating a new template.",
        ErrorCode.STORAGE_WRITE_FAILED: "Check disk space and permissions. Restart Anki and try again.",
        ErrorCode.STORAGE_READ_FAILED: "The file may be missing or corrupted. Check the templates folder.",
        ErrorCode.STORAGE_PERMISSION_DENIED: "Anki doesn't have permission to access this location.",
        ErrorCode.BRIDGE_NOT_CONNECTED: "The editor connection was lost. Try closing and reopening the designer.",
        ErrorCode.BRIDGE_TIMEOUT: "The operation took too long. Try again or restart the designer.",
        ErrorCode.VALIDATION_FAILED: "Please check your input and try again.",
        ErrorCode.REQUIRED_FIELD_MISSING: "Please fill in all required fields.",
    }
    
    def __init__(self) -> None:
        """Initialize the error handler."""
        self._listeners: List[ErrorListener] = []
        self._history: List[Dict[str, Any]] = []
        self._error_count: int = 0
        
        logger.debug("ErrorHandler initialized")
    
    def handle(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        notify: bool = True
    ) -> Dict[str, Any]:
        """Handle an error with logging and optional notification.
        
        Args:
            error: The exception to handle.
            context: Optional context dictionary with additional info.
            notify: Whether to notify listeners (default True).
            
        Returns:
            Error dictionary with all relevant information.
        """
        self._error_count += 1
        
        # Build error info
        error_info = self._build_error_info(error, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Add to history
        self._add_to_history(error_info)
        
        # Notify listeners if requested
        if notify:
            self._notify_listeners(error_info)
        
        return error_info
    
    def _build_error_info(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a comprehensive error info dictionary.
        
        Args:
            error: The exception.
            context: Optional context.
            
        Returns:
            Error information dictionary.
        """
        # Get base info from exception
        if isinstance(error, TemplateDesignerError):
            error_info = error.to_dict()
        else:
            # Convert standard exception
            error_info = {
                "error": True,
                "message": str(error),
                "code": ErrorCode.UNKNOWN.value,
                "code_name": ErrorCode.UNKNOWN.name,
                "details": {},
                "recoverable": True
            }
        
        # Add timestamp
        error_info["timestamp"] = datetime.now().isoformat()
        error_info["error_id"] = self._error_count
        
        # Add context
        if context:
            error_info["context"] = context
        
        # Add recovery suggestion
        code = ErrorCode(error_info["code"]) if isinstance(error_info["code"], int) else error_info["code"]
        if code in self.RECOVERY_SUGGESTIONS:
            error_info["recovery_suggestion"] = self.RECOVERY_SUGGESTIONS[code]
        
        # Add exception type
        error_info["exception_type"] = type(error).__name__
        
        # Add traceback for internal errors (not sent to UI)
        error_info["_traceback"] = traceback.format_exc()
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """Log the error with appropriate level.
        
        Args:
            error_info: Error information dictionary.
        """
        # Build log message
        msg = f"[{error_info['code_name']}] {error_info['message']}"
        
        if error_info.get("context"):
            msg += f" | Context: {error_info['context']}"
        
        # Log with traceback for debugging
        if error_info.get("recoverable", True):
            logger.error(msg)
        else:
            logger.critical(msg)
        
        # Log traceback at debug level
        if error_info.get("_traceback"):
            logger.debug(f"Traceback:\n{error_info['_traceback']}")
    
    def _add_to_history(self, error_info: Dict[str, Any]) -> None:
        """Add error to history, maintaining max size.
        
        Args:
            error_info: Error information dictionary.
        """
        # Create a copy without internal fields
        public_info = {k: v for k, v in error_info.items() if not k.startswith("_")}
        
        self._history.append(public_info)
        
        # Trim if needed
        if len(self._history) > self.MAX_HISTORY:
            self._history = self._history[-self.MAX_HISTORY:]
    
    def _notify_listeners(self, error_info: Dict[str, Any]) -> None:
        """Notify all registered listeners.
        
        Args:
            error_info: Error information dictionary.
        """
        # Create a copy without internal fields for listeners
        public_info = {k: v for k, v in error_info.items() if not k.startswith("_")}
        
        for listener in self._listeners:
            try:
                listener(public_info)
            except Exception as e:
                logger.error(f"Error in error listener: {e}")
    
    def add_listener(self, listener: ErrorListener) -> None:
        """Add an error listener.
        
        Args:
            listener: Callback function receiving error info dict.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
            logger.debug(f"Added error listener (total={len(self._listeners)})")
    
    def remove_listener(self, listener: ErrorListener) -> None:
        """Remove an error listener.
        
        Args:
            listener: The listener to remove.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
            logger.debug(f"Removed error listener (total={len(self._listeners)})")
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get error history.
        
        Args:
            limit: Optional limit on number of errors to return.
            
        Returns:
            List of error info dictionaries, newest first.
        """
        history = list(reversed(self._history))
        if limit:
            return history[:limit]
        return history
    
    def clear_history(self) -> None:
        """Clear error history."""
        self._history.clear()
        logger.debug("Error history cleared")
    
    @property
    def error_count(self) -> int:
        """Get total error count since initialization."""
        return self._error_count
    
    @property
    def recent_errors(self) -> List[Dict[str, Any]]:
        """Get the 5 most recent errors."""
        return self.get_history(limit=5)


# Global error handler instance
_global_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create the global error handler instance.
    
    Returns:
        The global ErrorHandler instance.
    """
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
    return _global_handler


def handle_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    notify: bool = True
) -> Dict[str, Any]:
    """Handle an error using the global handler.
    
    Convenience function for quick error handling.
    
    Args:
        error: The exception to handle.
        context: Optional context dictionary.
        notify: Whether to notify listeners.
        
    Returns:
        Error information dictionary.
    """
    return get_error_handler().handle(error, context, notify)


def error_boundary(
    context_key: str = "action",
    reraise: bool = False,
    default_return: Any = None
) -> Callable:
    """Decorator for automatic error handling.
    
    Wraps a function to catch and handle exceptions automatically.
    
    Args:
        context_key: Key for the context dict (function name used as value).
        reraise: Whether to re-raise the exception after handling.
        default_return: Value to return on error (if not reraising).
        
    Returns:
        Decorator function.
    
    Example:
        @error_boundary(context_key="operation")
        def save_template(template):
            # ... may raise exceptions
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {context_key: func.__name__}
                handle_error(e, context=context)
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator
