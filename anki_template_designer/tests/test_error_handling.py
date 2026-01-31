"""
Tests for exceptions and error handler.

Plan 08: Comprehensive tests for error handling system.
"""

import pytest
from anki_template_designer.core.exceptions import (
    ErrorCode,
    TemplateDesignerError,
    TemplateError,
    TemplateNotFoundError,
    TemplateSaveError,
    TemplateLoadError,
    TemplateValidationError,
    ComponentError,
    ComponentNotFoundError,
    ComponentTypeError,
    ValidationError,
    RequiredFieldError,
    InvalidFormatError,
    StorageError,
    StorageReadError,
    StorageWriteError,
    StoragePermissionError,
    BridgeError,
    BridgeNotConnectedError,
    BridgeTimeoutError,
    UIError
)
from anki_template_designer.services.error_handler import (
    ErrorHandler,
    get_error_handler,
    handle_error,
    error_boundary
)


class TestErrorCode:
    """Tests for ErrorCode enum."""
    
    def test_error_codes_have_unique_values(self):
        """Test all error codes have unique values."""
        values = [code.value for code in ErrorCode]
        assert len(values) == len(set(values))
    
    def test_error_code_ranges(self):
        """Test error codes follow the defined ranges."""
        # General errors: 1000-1099
        assert 1000 <= ErrorCode.UNKNOWN.value < 1100
        assert 1000 <= ErrorCode.INTERNAL.value < 1100
        
        # Template errors: 1100-1199
        assert 1100 <= ErrorCode.TEMPLATE_NOT_FOUND.value < 1200
        assert 1100 <= ErrorCode.TEMPLATE_SAVE_FAILED.value < 1200
        
        # Component errors: 1200-1299
        assert 1200 <= ErrorCode.COMPONENT_NOT_FOUND.value < 1300
        
        # Validation errors: 1300-1399
        assert 1300 <= ErrorCode.VALIDATION_FAILED.value < 1400


class TestTemplateDesignerError:
    """Tests for base TemplateDesignerError."""
    
    def test_default_values(self):
        """Test exception with default values."""
        err = TemplateDesignerError()
        assert err.message == TemplateDesignerError.default_message
        assert err.code == ErrorCode.UNKNOWN
        assert err.details == {}
        assert err.recoverable is True
    
    def test_custom_values(self):
        """Test exception with custom values."""
        err = TemplateDesignerError(
            message="Custom error",
            code=ErrorCode.INTERNAL,
            details={"key": "value"},
            recoverable=False
        )
        assert err.message == "Custom error"
        assert err.code == ErrorCode.INTERNAL
        assert err.details == {"key": "value"}
        assert err.recoverable is False
    
    def test_to_dict(self):
        """Test to_dict serialization."""
        err = TemplateDesignerError(
            message="Test error",
            code=ErrorCode.INTERNAL,
            details={"foo": "bar"}
        )
        d = err.to_dict()
        
        assert d["error"] is True
        assert d["message"] == "Test error"
        assert d["code"] == ErrorCode.INTERNAL.value
        assert d["code_name"] == "INTERNAL"
        assert d["details"] == {"foo": "bar"}
        assert d["recoverable"] is True
    
    def test_str_representation(self):
        """Test string representation."""
        err = TemplateDesignerError(message="Test", code=ErrorCode.UNKNOWN)
        assert "[UNKNOWN] Test" in str(err)
        
        err_with_details = TemplateDesignerError(
            message="Test",
            code=ErrorCode.UNKNOWN,
            details={"x": 1}
        )
        assert "{'x': 1}" in str(err_with_details)


class TestTemplateExceptions:
    """Tests for template-related exceptions."""
    
    def test_template_not_found(self):
        """Test TemplateNotFoundError."""
        err = TemplateNotFoundError("test-id-123")
        
        assert "test-id-123" in err.message
        assert err.code == ErrorCode.TEMPLATE_NOT_FOUND
        assert err.details["template_id"] == "test-id-123"
    
    def test_template_save_error(self):
        """Test TemplateSaveError."""
        err = TemplateSaveError(message="Disk full")
        assert err.code == ErrorCode.TEMPLATE_SAVE_FAILED
        assert err.message == "Disk full"
    
    def test_template_load_error(self):
        """Test TemplateLoadError."""
        err = TemplateLoadError()
        assert err.code == ErrorCode.TEMPLATE_LOAD_FAILED
    
    def test_template_validation_error(self):
        """Test TemplateValidationError."""
        err = TemplateValidationError(details={"field": "name"})
        assert err.code == ErrorCode.TEMPLATE_INVALID
        assert err.details["field"] == "name"


class TestComponentExceptions:
    """Tests for component-related exceptions."""
    
    def test_component_not_found(self):
        """Test ComponentNotFoundError."""
        err = ComponentNotFoundError("comp-abc")
        
        assert "comp-abc" in err.message
        assert err.code == ErrorCode.COMPONENT_NOT_FOUND
        assert err.details["component_id"] == "comp-abc"
    
    def test_component_type_error(self):
        """Test ComponentTypeError."""
        err = ComponentTypeError("invalid_type")
        
        assert "invalid_type" in err.message
        assert err.code == ErrorCode.COMPONENT_TYPE_UNKNOWN
        assert err.details["component_type"] == "invalid_type"


class TestValidationExceptions:
    """Tests for validation exceptions."""
    
    def test_validation_error(self):
        """Test base ValidationError."""
        err = ValidationError()
        assert err.code == ErrorCode.VALIDATION_FAILED
    
    def test_required_field_error(self):
        """Test RequiredFieldError."""
        err = RequiredFieldError("name")
        
        assert "name" in err.message
        assert err.code == ErrorCode.REQUIRED_FIELD_MISSING
        assert err.details["field"] == "name"
    
    def test_invalid_format_error(self):
        """Test InvalidFormatError."""
        err = InvalidFormatError(message="Expected JSON")
        assert err.code == ErrorCode.INVALID_FORMAT


class TestStorageExceptions:
    """Tests for storage exceptions."""
    
    def test_storage_error_with_path(self):
        """Test StorageError with path."""
        err = StorageError(path="/path/to/file")
        assert err.details["path"] == "/path/to/file"
    
    def test_storage_read_error(self):
        """Test StorageReadError."""
        err = StorageReadError(message="File not found", path="/test")
        assert err.code == ErrorCode.STORAGE_READ_FAILED
        assert err.details["path"] == "/test"
    
    def test_storage_write_error(self):
        """Test StorageWriteError."""
        err = StorageWriteError()
        assert err.code == ErrorCode.STORAGE_WRITE_FAILED
    
    def test_storage_permission_error(self):
        """Test StoragePermissionError."""
        err = StoragePermissionError()
        assert err.code == ErrorCode.STORAGE_PERMISSION_DENIED


class TestBridgeExceptions:
    """Tests for bridge/communication exceptions."""
    
    def test_bridge_not_connected(self):
        """Test BridgeNotConnectedError."""
        err = BridgeNotConnectedError()
        assert err.code == ErrorCode.BRIDGE_NOT_CONNECTED
    
    def test_bridge_timeout(self):
        """Test BridgeTimeoutError."""
        err = BridgeTimeoutError()
        assert err.code == ErrorCode.BRIDGE_TIMEOUT


class TestErrorHandler:
    """Tests for ErrorHandler class."""
    
    def test_initialization(self):
        """Test handler initializes correctly."""
        handler = ErrorHandler()
        assert handler.error_count == 0
        assert handler.get_history() == []
    
    def test_handle_custom_exception(self):
        """Test handling a TemplateDesignerError."""
        handler = ErrorHandler()
        err = TemplateNotFoundError("test-id")
        
        result = handler.handle(err, notify=False)
        
        assert result["error"] is True
        assert result["code"] == ErrorCode.TEMPLATE_NOT_FOUND.value
        assert "test-id" in result["message"]
        assert "timestamp" in result
        assert "error_id" in result
    
    def test_handle_standard_exception(self):
        """Test handling a standard Python exception."""
        handler = ErrorHandler()
        err = ValueError("Something went wrong")
        
        result = handler.handle(err, notify=False)
        
        assert result["error"] is True
        assert result["code"] == ErrorCode.UNKNOWN.value
        assert "Something went wrong" in result["message"]
        assert result["exception_type"] == "ValueError"
    
    def test_handle_with_context(self):
        """Test handling with context."""
        handler = ErrorHandler()
        err = TemplateDesignerError("Test")
        
        result = handler.handle(
            err,
            context={"action": "save", "template_id": "123"},
            notify=False
        )
        
        assert result["context"]["action"] == "save"
        assert result["context"]["template_id"] == "123"
    
    def test_recovery_suggestion(self):
        """Test recovery suggestions are added."""
        handler = ErrorHandler()
        err = TemplateNotFoundError("test")
        
        result = handler.handle(err, notify=False)
        
        assert "recovery_suggestion" in result
        assert "refresh" in result["recovery_suggestion"].lower()
    
    def test_error_history(self):
        """Test error history is maintained."""
        handler = ErrorHandler()
        
        handler.handle(TemplateDesignerError("Error 1"), notify=False)
        handler.handle(TemplateDesignerError("Error 2"), notify=False)
        handler.handle(TemplateDesignerError("Error 3"), notify=False)
        
        history = handler.get_history()
        assert len(history) == 3
        # Newest first
        assert "Error 3" in history[0]["message"]
        assert "Error 1" in history[2]["message"]
    
    def test_history_limit(self):
        """Test get_history with limit."""
        handler = ErrorHandler()
        
        for i in range(10):
            handler.handle(TemplateDesignerError(f"Error {i}"), notify=False)
        
        limited = handler.get_history(limit=3)
        assert len(limited) == 3
        assert "Error 9" in limited[0]["message"]
    
    def test_history_max_size(self):
        """Test history respects MAX_HISTORY."""
        handler = ErrorHandler()
        handler.MAX_HISTORY = 5
        
        for i in range(10):
            handler.handle(TemplateDesignerError(f"Error {i}"), notify=False)
        
        assert len(handler.get_history()) == 5
    
    def test_clear_history(self):
        """Test clearing history."""
        handler = ErrorHandler()
        handler.handle(TemplateDesignerError("Test"), notify=False)
        
        handler.clear_history()
        assert handler.get_history() == []
    
    def test_error_count(self):
        """Test error count increments."""
        handler = ErrorHandler()
        
        handler.handle(TemplateDesignerError("1"), notify=False)
        handler.handle(TemplateDesignerError("2"), notify=False)
        handler.handle(TemplateDesignerError("3"), notify=False)
        
        assert handler.error_count == 3
    
    def test_recent_errors(self):
        """Test recent_errors property."""
        handler = ErrorHandler()
        
        for i in range(10):
            handler.handle(TemplateDesignerError(f"Error {i}"), notify=False)
        
        recent = handler.recent_errors
        assert len(recent) == 5


class TestErrorListeners:
    """Tests for error listener functionality."""
    
    def test_add_listener(self):
        """Test adding a listener."""
        handler = ErrorHandler()
        notifications = []
        
        handler.add_listener(lambda err: notifications.append(err))
        handler.handle(TemplateDesignerError("Test"))
        
        assert len(notifications) == 1
        assert "Test" in notifications[0]["message"]
    
    def test_listener_receives_public_info_only(self):
        """Test listeners don't receive internal fields."""
        handler = ErrorHandler()
        received = []
        
        handler.add_listener(lambda err: received.append(err))
        handler.handle(TemplateDesignerError("Test"))
        
        # _traceback should not be in listener data
        assert "_traceback" not in received[0]
    
    def test_remove_listener(self):
        """Test removing a listener."""
        handler = ErrorHandler()
        notifications = []
        listener = lambda err: notifications.append(err)
        
        handler.add_listener(listener)
        handler.handle(TemplateDesignerError("First"), notify=True)
        
        handler.remove_listener(listener)
        handler.handle(TemplateDesignerError("Second"), notify=True)
        
        assert len(notifications) == 1
    
    def test_notify_false(self):
        """Test notify=False skips listeners."""
        handler = ErrorHandler()
        notifications = []
        
        handler.add_listener(lambda err: notifications.append(err))
        handler.handle(TemplateDesignerError("Test"), notify=False)
        
        assert len(notifications) == 0
    
    def test_listener_error_isolation(self):
        """Test failing listener doesn't affect others."""
        handler = ErrorHandler()
        results = []
        
        def bad_listener(err):
            raise RuntimeError("Listener failed")
        
        def good_listener(err):
            results.append(err["message"])
        
        handler.add_listener(bad_listener)
        handler.add_listener(good_listener)
        
        # Should not raise
        handler.handle(TemplateDesignerError("Test"))
        
        assert len(results) == 1


class TestGlobalHandler:
    """Tests for global handler functions."""
    
    def test_get_error_handler_singleton(self):
        """Test get_error_handler returns same instance."""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        assert handler1 is handler2
    
    def test_handle_error_convenience(self):
        """Test handle_error convenience function."""
        result = handle_error(
            TemplateDesignerError("Test"),
            context={"test": True},
            notify=False
        )
        
        assert result["error"] is True
        assert result["context"]["test"] is True


class TestErrorBoundaryDecorator:
    """Tests for error_boundary decorator."""
    
    def test_successful_function(self):
        """Test decorator doesn't affect successful functions."""
        @error_boundary()
        def success():
            return "ok"
        
        assert success() == "ok"
    
    def test_catches_exception(self):
        """Test decorator catches exceptions."""
        @error_boundary(default_return="error_occurred")
        def failing():
            raise ValueError("boom")
        
        result = failing()
        assert result == "error_occurred"
    
    def test_reraise_option(self):
        """Test reraise=True re-raises the exception."""
        @error_boundary(reraise=True)
        def failing():
            raise ValueError("boom")
        
        with pytest.raises(ValueError):
            failing()
    
    def test_context_includes_function_name(self):
        """Test context includes function name."""
        handler = ErrorHandler()
        errors = []
        handler.add_listener(lambda e: errors.append(e))
        
        # Replace global handler temporarily
        import anki_template_designer.services.error_handler as eh
        original = eh._global_handler
        eh._global_handler = handler
        
        try:
            @error_boundary(context_key="operation")
            def my_operation():
                raise ValueError("fail")
            
            my_operation()
            
            assert len(errors) == 1
            assert errors[0]["context"]["operation"] == "my_operation"
        finally:
            eh._global_handler = original
