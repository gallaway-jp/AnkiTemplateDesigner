"""
Custom exceptions for Anki Template Designer.

Plan 08: Defines a hierarchy of exceptions for different error types,
enabling precise error handling and user-friendly error messages.
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """Error codes for categorizing exceptions."""
    
    # General errors (1000-1099)
    UNKNOWN = 1000
    INTERNAL = 1001
    NOT_IMPLEMENTED = 1002
    
    # Template errors (1100-1199)
    TEMPLATE_NOT_FOUND = 1100
    TEMPLATE_INVALID = 1101
    TEMPLATE_SAVE_FAILED = 1102
    TEMPLATE_LOAD_FAILED = 1103
    TEMPLATE_DELETE_FAILED = 1104
    TEMPLATE_DUPLICATE_NAME = 1105
    
    # Component errors (1200-1299)
    COMPONENT_NOT_FOUND = 1200
    COMPONENT_INVALID = 1201
    COMPONENT_TYPE_UNKNOWN = 1202
    
    # Validation errors (1300-1399)
    VALIDATION_FAILED = 1300
    REQUIRED_FIELD_MISSING = 1301
    INVALID_FORMAT = 1302
    VALUE_OUT_OF_RANGE = 1303
    
    # Storage errors (1400-1499)
    STORAGE_READ_FAILED = 1400
    STORAGE_WRITE_FAILED = 1401
    STORAGE_PATH_INVALID = 1402
    STORAGE_PERMISSION_DENIED = 1403
    
    # Bridge/Communication errors (1500-1599)
    BRIDGE_NOT_CONNECTED = 1500
    BRIDGE_CALL_FAILED = 1501
    BRIDGE_TIMEOUT = 1502
    
    # UI errors (1600-1699)
    UI_RENDER_FAILED = 1600
    UI_COMPONENT_MISSING = 1601


class TemplateDesignerError(Exception):
    """Base exception for all Template Designer errors.
    
    Attributes:
        message: Human-readable error message.
        code: Error code for categorization.
        details: Optional dictionary with additional context.
        recoverable: Whether the error can be recovered from.
    """
    
    default_message = "An error occurred in Template Designer"
    default_code = ErrorCode.UNKNOWN
    
    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ) -> None:
        """Initialize the exception.
        
        Args:
            message: Human-readable error message.
            code: Error code for categorization.
            details: Optional dictionary with additional context.
            recoverable: Whether the error can be recovered from.
        """
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        self.recoverable = recoverable
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the error.
        """
        return {
            "error": True,
            "message": self.message,
            "code": self.code.value,
            "code_name": self.code.name,
            "details": self.details,
            "recoverable": self.recoverable
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"[{self.code.name}] {self.message} - {self.details}"
        return f"[{self.code.name}] {self.message}"


# Template-related exceptions

class TemplateError(TemplateDesignerError):
    """Base exception for template-related errors."""
    default_message = "A template error occurred"
    default_code = ErrorCode.TEMPLATE_INVALID


class TemplateNotFoundError(TemplateError):
    """Raised when a template cannot be found."""
    default_message = "Template not found"
    default_code = ErrorCode.TEMPLATE_NOT_FOUND
    
    def __init__(self, template_id: str, **kwargs) -> None:
        details = kwargs.pop("details", {})
        details["template_id"] = template_id
        super().__init__(
            message=f"Template not found: {template_id}",
            details=details,
            **kwargs
        )


class TemplateSaveError(TemplateError):
    """Raised when a template cannot be saved."""
    default_message = "Failed to save template"
    default_code = ErrorCode.TEMPLATE_SAVE_FAILED


class TemplateLoadError(TemplateError):
    """Raised when a template cannot be loaded."""
    default_message = "Failed to load template"
    default_code = ErrorCode.TEMPLATE_LOAD_FAILED


class TemplateValidationError(TemplateError):
    """Raised when template validation fails."""
    default_message = "Template validation failed"
    default_code = ErrorCode.TEMPLATE_INVALID


# Component-related exceptions

class ComponentError(TemplateDesignerError):
    """Base exception for component-related errors."""
    default_message = "A component error occurred"
    default_code = ErrorCode.COMPONENT_INVALID


class ComponentNotFoundError(ComponentError):
    """Raised when a component cannot be found."""
    default_message = "Component not found"
    default_code = ErrorCode.COMPONENT_NOT_FOUND
    
    def __init__(self, component_id: str, **kwargs) -> None:
        details = kwargs.pop("details", {})
        details["component_id"] = component_id
        super().__init__(
            message=f"Component not found: {component_id}",
            details=details,
            **kwargs
        )


class ComponentTypeError(ComponentError):
    """Raised when an unknown component type is encountered."""
    default_message = "Unknown component type"
    default_code = ErrorCode.COMPONENT_TYPE_UNKNOWN
    
    def __init__(self, component_type: str, **kwargs) -> None:
        details = kwargs.pop("details", {})
        details["component_type"] = component_type
        super().__init__(
            message=f"Unknown component type: {component_type}",
            details=details,
            **kwargs
        )


# Validation exceptions

class ValidationError(TemplateDesignerError):
    """Base exception for validation errors."""
    default_message = "Validation failed"
    default_code = ErrorCode.VALIDATION_FAILED


class RequiredFieldError(ValidationError):
    """Raised when a required field is missing."""
    default_message = "Required field is missing"
    default_code = ErrorCode.REQUIRED_FIELD_MISSING
    
    def __init__(self, field_name: str, **kwargs) -> None:
        details = kwargs.pop("details", {})
        details["field"] = field_name
        super().__init__(
            message=f"Required field missing: {field_name}",
            details=details,
            **kwargs
        )


class InvalidFormatError(ValidationError):
    """Raised when data format is invalid."""
    default_message = "Invalid data format"
    default_code = ErrorCode.INVALID_FORMAT


# Storage exceptions

class StorageError(TemplateDesignerError):
    """Base exception for storage-related errors."""
    default_message = "A storage error occurred"
    default_code = ErrorCode.STORAGE_READ_FAILED
    
    def __init__(self, message: Optional[str] = None, path: Optional[str] = None, **kwargs) -> None:
        details = kwargs.pop("details", {})
        if path:
            details["path"] = path
        super().__init__(message=message, details=details, **kwargs)


class StorageReadError(StorageError):
    """Raised when reading from storage fails."""
    default_message = "Failed to read from storage"
    default_code = ErrorCode.STORAGE_READ_FAILED


class StorageWriteError(StorageError):
    """Raised when writing to storage fails."""
    default_message = "Failed to write to storage"
    default_code = ErrorCode.STORAGE_WRITE_FAILED


class StoragePermissionError(StorageError):
    """Raised when storage permission is denied."""
    default_message = "Storage permission denied"
    default_code = ErrorCode.STORAGE_PERMISSION_DENIED
    recoverable = False


# Bridge/Communication exceptions

class BridgeError(TemplateDesignerError):
    """Base exception for bridge/communication errors."""
    default_message = "A bridge communication error occurred"
    default_code = ErrorCode.BRIDGE_CALL_FAILED


class BridgeNotConnectedError(BridgeError):
    """Raised when bridge is not connected."""
    default_message = "Bridge is not connected"
    default_code = ErrorCode.BRIDGE_NOT_CONNECTED


class BridgeTimeoutError(BridgeError):
    """Raised when a bridge call times out."""
    default_message = "Bridge call timed out"
    default_code = ErrorCode.BRIDGE_TIMEOUT


# UI exceptions

class UIError(TemplateDesignerError):
    """Base exception for UI-related errors."""
    default_message = "A UI error occurred"
    default_code = ErrorCode.UI_RENDER_FAILED
