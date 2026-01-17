"""
Issue #51: Error Messages and Recovery System

Comprehensive error handling system with user-friendly messages,
recovery suggestions, error logging, and context-aware help.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json
import traceback


class ErrorSeverity(Enum):
    """Severity level of errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Category of error."""
    VALIDATION = "validation"
    COMPONENT = "component"
    TEMPLATE = "template"
    FILE = "file"
    OPERATION = "operation"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class RecoverySuggestion:
    """A recovery suggestion for an error."""
    id: str = ""
    title: str = ""
    description: str = ""
    action: str = ""
    is_automatic: bool = False
    priority: int = 0  # Higher = higher priority

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'action': self.action,
            'is_automatic': self.is_automatic,
            'priority': self.priority
        }


@dataclass
class ErrorLog:
    """A logged error entry."""
    id: str = ""
    message: str = ""
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.UNKNOWN
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    recovery_suggestions: List[RecoverySuggestion] = field(default_factory=list)
    is_resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'stack_trace': self.stack_trace,
            'recovery_suggestions': [s.to_dict() for s in self.recovery_suggestions],
            'is_resolved': self.is_resolved
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ErrorLog':
        """Create from dictionary."""
        return ErrorLog(
            id=data.get('id', ''),
            message=data.get('message', ''),
            severity=ErrorSeverity(data.get('severity', 'error')),
            category=ErrorCategory(data.get('category', 'unknown')),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            context=data.get('context', {}),
            stack_trace=data.get('stack_trace', ''),
            recovery_suggestions=[RecoverySuggestion(**s) for s in data.get('recovery_suggestions', [])],
            is_resolved=data.get('is_resolved', False)
        )


class ErrorSystem:
    """Comprehensive error handling and recovery system."""

    # Standard error message templates
    ERROR_MESSAGES = {
        'invalid_component_name': {
            'message': 'Component name must be unique and contain only alphanumeric characters',
            'severity': ErrorSeverity.WARNING,
            'category': ErrorCategory.VALIDATION,
            'suggestions': [
                RecoverySuggestion(
                    id='rename_component',
                    title='Rename component',
                    description='Choose a different unique name',
                    action='rename'
                ),
                RecoverySuggestion(
                    id='use_default_name',
                    title='Use auto-generated name',
                    description='Let the system generate a unique name',
                    action='auto_name',
                    is_automatic=True,
                    priority=1
                )
            ]
        },
        'duplicate_component': {
            'message': 'A component with this name already exists',
            'severity': ErrorSeverity.ERROR,
            'category': ErrorCategory.COMPONENT,
            'suggestions': [
                RecoverySuggestion(
                    id='rename_new',
                    title='Rename new component',
                    description='Give the new component a unique name',
                    action='rename'
                ),
                RecoverySuggestion(
                    id='delete_old',
                    title='Delete existing component',
                    description='Remove the component with the same name',
                    action='delete'
                )
            ]
        },
        'invalid_template': {
            'message': 'Template contains invalid syntax or structure',
            'severity': ErrorSeverity.ERROR,
            'category': ErrorCategory.TEMPLATE,
            'suggestions': [
                RecoverySuggestion(
                    id='view_error',
                    title='View error details',
                    description='See detailed error information and line numbers',
                    action='show_details'
                ),
                RecoverySuggestion(
                    id='undo_changes',
                    title='Undo recent changes',
                    description='Revert to last working version',
                    action='undo',
                    is_automatic=True,
                    priority=2
                )
            ]
        },
        'file_save_failed': {
            'message': 'Failed to save template file',
            'severity': ErrorSeverity.CRITICAL,
            'category': ErrorCategory.FILE,
            'suggestions': [
                RecoverySuggestion(
                    id='retry_save',
                    title='Retry save',
                    description='Try saving the file again',
                    action='retry',
                    is_automatic=False,
                    priority=1
                ),
                RecoverySuggestion(
                    id='save_as',
                    title='Save with different name',
                    description='Save to a different file location',
                    action='save_as'
                ),
                RecoverySuggestion(
                    id='check_permissions',
                    title='Check file permissions',
                    description='Verify write permissions for the file location',
                    action='check_permissions'
                )
            ]
        },
        'operation_timeout': {
            'message': 'Operation took too long to complete',
            'severity': ErrorSeverity.WARNING,
            'category': ErrorCategory.OPERATION,
            'suggestions': [
                RecoverySuggestion(
                    id='retry_operation',
                    title='Retry operation',
                    description='Try the operation again',
                    action='retry'
                ),
                RecoverySuggestion(
                    id='cancel_operation',
                    title='Cancel operation',
                    description='Stop the current operation',
                    action='cancel',
                    is_automatic=True,
                    priority=0
                )
            ]
        }
    }

    def __init__(self, max_error_logs: int = 100):
        """
        Initialize the error system.
        
        Args:
            max_error_logs: Maximum number of error logs to keep
        """
        self.error_logs: List[ErrorLog] = []
        self.max_error_logs = max_error_logs
        self.current_error: Optional[ErrorLog] = None
        self.error_handlers: Dict[str, Callable] = {}
        self.listeners: List[Callable] = []
        self.recovery_callbacks: Dict[str, Callable] = {}

    def register_error_template(self, error_key: str, template: Dict[str, Any]) -> None:
        """Register a custom error message template."""
        self.ERROR_MESSAGES[error_key] = template

    def log_error(self, error_key: str, context: Dict[str, Any] = None, 
                  exception: Exception = None) -> str:
        """
        Log an error with context and suggestions.
        
        Args:
            error_key: Key of predefined error message
            context: Additional context information
            exception: Optional exception object
            
        Returns:
            Error ID
        """
        if error_key not in self.ERROR_MESSAGES:
            return self._log_generic_error(error_key, context, exception)

        template = self.ERROR_MESSAGES[error_key]
        
        error_log = ErrorLog(
            id=self._generate_error_id(),
            message=template.get('message', 'An error occurred'),
            severity=template.get('severity', ErrorSeverity.ERROR),
            category=template.get('category', ErrorCategory.UNKNOWN),
            context=context or {},
            stack_trace=traceback.format_exc() if exception else '',
            recovery_suggestions=template.get('suggestions', [])
        )

        self.error_logs.append(error_log)
        self.current_error = error_log

        # Optimize storage
        if len(self.error_logs) > self.max_error_logs:
            self.error_logs = self.error_logs[-self.max_error_logs:]

        self._notify_listeners('error_logged', {'error': error_log.to_dict()})
        
        # Try to handle with registered handler
        if error_key in self.error_handlers:
            try:
                self.error_handlers[error_key](error_log)
            except Exception:
                pass

        return error_log.id

    def _log_generic_error(self, message: str, context: Dict[str, Any], 
                          exception: Exception) -> str:
        """Log a generic error not in templates."""
        error_log = ErrorLog(
            id=self._generate_error_id(),
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.UNKNOWN,
            context=context or {},
            stack_trace=traceback.format_exc() if exception else ''
        )

        self.error_logs.append(error_log)
        self.current_error = error_log
        self._notify_listeners('error_logged', {'error': error_log.to_dict()})
        
        return error_log.id

    def get_current_error(self) -> Optional[ErrorLog]:
        """Get the most recent error."""
        return self.current_error

    def get_error(self, error_id: str) -> Optional[ErrorLog]:
        """Get specific error by ID."""
        for log in self.error_logs:
            if log.id == error_id:
                return log
        return None

    def get_error_history(self, limit: int = 10) -> List[ErrorLog]:
        """Get recent error history."""
        return self.error_logs[-limit:]

    def get_unresolved_errors(self) -> List[ErrorLog]:
        """Get all unresolved errors."""
        return [log for log in self.error_logs if not log.is_resolved]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorLog]:
        """Get errors by severity level."""
        return [log for log in self.error_logs if log.severity == severity]

    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorLog]:
        """Get errors by category."""
        return [log for log in self.error_logs if log.category == category]

    def get_recovery_suggestions(self, error_id: str) -> List[RecoverySuggestion]:
        """Get recovery suggestions for an error."""
        error = self.get_error(error_id)
        if error:
            return sorted(error.recovery_suggestions, key=lambda s: s.priority, reverse=True)
        return []

    def apply_recovery(self, error_id: str, suggestion_id: str) -> bool:
        """
        Apply a recovery suggestion.
        
        Args:
            error_id: Error ID
            suggestion_id: Suggestion ID
            
        Returns:
            True if successful
        """
        error = self.get_error(error_id)
        if not error:
            return False

        # Find suggestion
        suggestion = None
        for s in error.recovery_suggestions:
            if s.id == suggestion_id:
                suggestion = s
                break

        if not suggestion:
            return False

        # Execute recovery callback if registered
        if suggestion.action in self.recovery_callbacks:
            try:
                self.recovery_callbacks[suggestion.action](error, suggestion)
                error.is_resolved = True
                self._notify_listeners('recovery_applied', {
                    'error_id': error_id,
                    'suggestion_id': suggestion_id
                })
                return True
            except Exception:
                return False

        error.is_resolved = True
        self._notify_listeners('recovery_applied', {
            'error_id': error_id,
            'suggestion_id': suggestion_id
        })
        return True

    def mark_resolved(self, error_id: str) -> bool:
        """Mark an error as resolved."""
        error = self.get_error(error_id)
        if error:
            error.is_resolved = True
            self._notify_listeners('error_resolved', {'error_id': error_id})
            return True
        return False

    def clear_errors(self) -> None:
        """Clear all error logs."""
        self.error_logs.clear()
        self.current_error = None
        self._notify_listeners('errors_cleared', {})

    def register_error_handler(self, error_key: str, handler: Callable) -> None:
        """Register handler for specific error type."""
        self.error_handlers[error_key] = handler

    def register_recovery_callback(self, action: str, callback: Callable) -> None:
        """Register callback for recovery action."""
        self.recovery_callbacks[action] = callback

    def add_listener(self, listener: Callable) -> None:
        """Add event listener."""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        """Remove event listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def _notify_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all listeners."""
        for listener in self.listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass

    def _generate_error_id(self) -> str:
        """Generate unique error ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        resolved = sum(1 for e in self.error_logs if e.is_resolved)
        by_severity = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in self.error_logs if e.severity == severity)
            by_severity[severity.value] = count

        by_category = {}
        for category in ErrorCategory:
            count = sum(1 for e in self.error_logs if e.category == category)
            by_category[category.value] = count

        return {
            'total_errors': len(self.error_logs),
            'resolved_errors': resolved,
            'unresolved_errors': len(self.error_logs) - resolved,
            'by_severity': by_severity,
            'by_category': by_category,
            'critical_count': by_severity.get('critical', 0)
        }

    def export_logs(self) -> List[Dict[str, Any]]:
        """Export error logs."""
        return [log.to_dict() for log in self.error_logs]

    def clear_old_logs(self, days: int = 7) -> int:
        """Clear error logs older than specified days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        initial_count = len(self.error_logs)
        self.error_logs = [log for log in self.error_logs if log.timestamp > cutoff]
        
        return initial_count - len(self.error_logs)
