"""
Tests for logging configuration.

Plan 09: Tests for LoggingConfig and logging utilities.
"""

import logging
import os
import pytest
import tempfile
from pathlib import Path

from anki_template_designer.utils.logging_config import (
    LoggingConfig,
    setup_logging,
    get_logging_config,
    get_logger,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_BYTES,
    DEFAULT_BACKUP_COUNT,
    LOG_FILE_NAME
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test log files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestLoggingConfigInit:
    """Tests for LoggingConfig initialization."""
    
    def test_default_initialization(self):
        """Test LoggingConfig with default values."""
        config = LoggingConfig()
        assert config._log_level == DEFAULT_LOG_LEVEL
        assert config._log_to_file is True
        assert config._log_to_console is True
        assert config._max_bytes == DEFAULT_MAX_BYTES
        assert config._backup_count == DEFAULT_BACKUP_COUNT
        assert config.debug_mode is False
    
    def test_custom_initialization(self):
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            addon_dir="/tmp/test",
            log_level=logging.DEBUG,
            log_to_file=False,
            log_to_console=False,
            max_bytes=1000,
            backup_count=5
        )
        assert config._log_level == logging.DEBUG
        assert config._log_to_file is False
        assert config._log_to_console is False
        assert config._max_bytes == 1000
        assert config._backup_count == 5
    
    def test_log_dir_property(self):
        """Test log_dir property."""
        config = LoggingConfig(addon_dir="/tmp/test_addon")
        assert config.log_dir == Path("/tmp/test_addon/logs")
    
    def test_log_file_property(self):
        """Test log_file property."""
        config = LoggingConfig(addon_dir="/tmp/test_addon")
        assert config.log_file == Path(f"/tmp/test_addon/logs/{LOG_FILE_NAME}")
    
    def test_log_dir_none_without_addon_dir(self):
        """Test log_dir is None when no addon_dir provided."""
        config = LoggingConfig()
        assert config.log_dir is None
        assert config.log_file is None


class TestLoggingConfigSetup:
    """Tests for LoggingConfig.setup()."""
    
    def test_setup_creates_log_directory(self, temp_dir):
        """Test setup creates log directory."""
        config = LoggingConfig(addon_dir=temp_dir)
        config.setup()
        
        try:
            assert config.log_dir.exists()
        finally:
            config.shutdown()
    
    def test_setup_creates_file_handler(self, temp_dir):
        """Test setup creates file handler."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
        config.setup()
        
        try:
            assert "file" in config._handlers
        finally:
            config.shutdown()
    
    def test_setup_creates_console_handler(self):
        """Test setup creates console handler."""
        config = LoggingConfig(log_to_file=False, log_to_console=True)
        config.setup()
        
        try:
            assert "console" in config._handlers
        finally:
            config.shutdown()
    
    def test_setup_without_file_logging(self):
        """Test setup without file logging."""
        config = LoggingConfig(log_to_file=False, log_to_console=True)
        config.setup()
        
        try:
            assert "file" not in config._handlers
        finally:
            config.shutdown()
    
    def test_setup_without_console_logging(self, temp_dir):
        """Test setup without console logging."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_file=True, log_to_console=False)
        config.setup()
        
        try:
            assert "console" not in config._handlers
        finally:
            config.shutdown()


class TestLoggingConfigGetLogger:
    """Tests for LoggingConfig.get_logger()."""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            logger = config.get_logger("test_module")
            assert isinstance(logger, logging.Logger)
        finally:
            config.shutdown()
    
    def test_get_logger_name_prefixed(self):
        """Test logger name is prefixed with addon name."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            logger = config.get_logger("my_module")
            assert logger.name == "anki_template_designer.my_module"
        finally:
            config.shutdown()


class TestLoggingConfigLogLevel:
    """Tests for log level management."""
    
    def test_set_log_level(self):
        """Test setting log level."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            config.set_log_level(logging.WARNING)
            assert config._log_level == logging.WARNING
        finally:
            config.shutdown()
    
    def test_set_log_level_updates_handlers(self):
        """Test set_log_level updates handler levels."""
        config = LoggingConfig(log_to_file=False, log_to_console=True)
        config.setup()
        
        try:
            config.set_log_level(logging.ERROR)
            
            for handler in config._handlers.values():
                assert handler.level == logging.ERROR
        finally:
            config.shutdown()


class TestDebugMode:
    """Tests for debug mode functionality."""
    
    def test_debug_mode_default_off(self):
        """Test debug mode is off by default."""
        config = LoggingConfig(log_to_file=False)
        assert config.debug_mode is False
    
    def test_enable_debug_mode(self):
        """Test enabling debug mode."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            config.set_debug_mode(True)
            
            assert config.debug_mode is True
            assert config._log_level == logging.DEBUG
        finally:
            config.shutdown()
    
    def test_disable_debug_mode(self):
        """Test disabling debug mode."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            config.set_debug_mode(True)
            config.set_debug_mode(False)
            
            assert config.debug_mode is False
            assert config._log_level == DEFAULT_LOG_LEVEL
        finally:
            config.shutdown()


class TestLogFileOperations:
    """Tests for log file operations."""
    
    def test_get_log_contents(self, temp_dir):
        """Test reading log file contents."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
        config.setup()
        
        try:
            # Write some logs
            logger = config.get_logger("test")
            logger.warning("Test message 1")
            logger.warning("Test message 2")
            
            # Force flush
            for handler in config._handlers.values():
                handler.flush()
            
            contents = config.get_log_contents(lines=10)
            assert "Test message 1" in contents
            assert "Test message 2" in contents
        finally:
            config.shutdown()
    
    def test_get_log_contents_no_file(self):
        """Test get_log_contents when no log file exists."""
        config = LoggingConfig(log_to_file=False)
        contents = config.get_log_contents()
        assert contents == ""
    
    def test_clear_logs(self, temp_dir):
        """Test clearing log files."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
        config.setup()
        
        try:
            # Write some logs
            logger = config.get_logger("test")
            logger.warning("Test message")
            
            for handler in config._handlers.values():
                handler.flush()
            
            # Shutdown first to release file handles
            config.shutdown()
            
            # Re-setup to clear (since shutdown clears handlers)
            config2 = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
            result = config2.clear_logs()
            assert result is True
        except Exception:
            config.shutdown()
            raise
    
    def test_clear_logs_no_dir(self):
        """Test clear_logs when no log directory."""
        config = LoggingConfig(log_to_file=False)
        result = config.clear_logs()
        assert result is False


class TestGetStatus:
    """Tests for get_status()."""
    
    def test_get_status_returns_dict(self):
        """Test get_status returns a dictionary."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            status = config.get_status()
            assert isinstance(status, dict)
        finally:
            config.shutdown()
    
    def test_get_status_contains_required_fields(self):
        """Test get_status contains all required fields."""
        config = LoggingConfig(log_to_file=False)
        config.setup()
        
        try:
            status = config.get_status()
            
            assert "initialized" in status
            assert "debug_mode" in status
            assert "log_level" in status
            assert "log_to_file" in status
            assert "log_to_console" in status
            assert "handlers" in status
        finally:
            config.shutdown()
    
    def test_get_status_with_log_file(self, temp_dir):
        """Test get_status includes file size when log file exists."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
        config.setup()
        
        try:
            # Write a log
            logger = config.get_logger("test")
            logger.warning("Test")
            for handler in config._handlers.values():
                handler.flush()
            
            status = config.get_status()
            
            assert "log_file_size" in status
            assert status["log_file_size"] > 0
        finally:
            config.shutdown()


class TestShutdown:
    """Tests for shutdown functionality."""
    
    def test_shutdown_clears_handlers(self):
        """Test shutdown removes all handlers."""
        config = LoggingConfig(log_to_file=False, log_to_console=True)
        config.setup()
        
        assert len(config._handlers) > 0
        
        config.shutdown()
        
        assert len(config._handlers) == 0
    
    def test_shutdown_allows_directory_cleanup(self, temp_dir):
        """Test shutdown releases file handles for cleanup."""
        config = LoggingConfig(addon_dir=temp_dir, log_to_console=False)
        config.setup()
        
        logger = config.get_logger("test")
        logger.warning("Test message")
        
        config.shutdown()
        
        # Should be able to delete the log file now
        log_file = Path(temp_dir) / "logs" / LOG_FILE_NAME
        if log_file.exists():
            log_file.unlink()  # Should not raise


class TestGlobalFunctions:
    """Tests for global logging functions."""
    
    def test_setup_logging(self, temp_dir):
        """Test setup_logging function."""
        config = setup_logging(addon_dir=temp_dir, log_to_console=False)
        
        try:
            assert config is not None
            assert config.log_dir.exists()
        finally:
            config.shutdown()
    
    def test_setup_logging_debug_mode(self):
        """Test setup_logging with debug=True."""
        config = setup_logging(debug=True, log_to_file=False)
        
        try:
            assert config.debug_mode is True
            assert config._log_level == logging.DEBUG
        finally:
            config.shutdown()
    
    def test_get_logging_config(self):
        """Test get_logging_config after setup."""
        config = setup_logging(log_to_file=False)
        
        try:
            retrieved = get_logging_config()
            assert retrieved is config
        finally:
            config.shutdown()
    
    def test_get_logger_convenience(self):
        """Test get_logger convenience function."""
        config = setup_logging(log_to_file=False)
        
        try:
            logger = get_logger("test_module")
            assert isinstance(logger, logging.Logger)
            assert "test_module" in logger.name
        finally:
            config.shutdown()
    
    def test_get_logger_fallback(self):
        """Test get_logger works even without setup."""
        # Reset global config
        import anki_template_designer.utils.logging_config as lc
        lc._global_config = None
        
        logger = get_logger("fallback_test")
        assert isinstance(logger, logging.Logger)


class TestLogRotation:
    """Tests for log rotation functionality."""
    
    def test_rotation_config(self, temp_dir):
        """Test rotation configuration is set correctly."""
        config = LoggingConfig(
            addon_dir=temp_dir,
            max_bytes=1000,
            backup_count=2,
            log_to_console=False
        )
        config.setup()
        
        try:
            handler = config._handlers.get("file")
            assert handler is not None
            assert handler.maxBytes == 1000
            assert handler.backupCount == 2
        finally:
            config.shutdown()
