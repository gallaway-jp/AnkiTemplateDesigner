"""
Tests for configuration schema and service.

Plan 10: Tests for Config, ConfigService, and validation.
"""

import json
import pytest
import tempfile
from pathlib import Path

from anki_template_designer.core.config_schema import (
    Config,
    WindowSize,
    EditorSettings,
    Theme,
    LogLevel,
    CONFIG_SCHEMA
)
from anki_template_designer.services.config_service import (
    ConfigService,
    get_config_service,
    init_config_service
)


class TestWindowSize:
    """Tests for WindowSize class."""
    
    def test_default_values(self):
        """Test default window size values."""
        ws = WindowSize()
        assert ws.width == 1200
        assert ws.height == 800
    
    def test_custom_values(self):
        """Test custom window size values."""
        ws = WindowSize(width=1600, height=900)
        assert ws.width == 1600
        assert ws.height == 900
    
    def test_validate_valid(self):
        """Test validation with valid values."""
        ws = WindowSize(width=800, height=600)
        errors = ws.validate()
        assert errors == []
    
    def test_validate_width_too_small(self):
        """Test validation with width too small."""
        ws = WindowSize(width=200, height=600)
        errors = ws.validate()
        assert len(errors) == 1
        assert "width" in errors[0].lower()
    
    def test_validate_height_too_large(self):
        """Test validation with height too large."""
        ws = WindowSize(width=800, height=5000)
        errors = ws.validate()
        assert len(errors) == 1
        assert "height" in errors[0].lower()
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        ws = WindowSize(width=1000, height=700)
        d = ws.to_dict()
        assert d == {"width": 1000, "height": 700}
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        ws = WindowSize.from_dict({"width": 1400, "height": 850})
        assert ws.width == 1400
        assert ws.height == 850


class TestEditorSettings:
    """Tests for EditorSettings class."""
    
    def test_default_values(self):
        """Test default editor settings."""
        es = EditorSettings()
        assert es.showGrid is True
        assert es.snapToGrid is True
        assert es.gridSize == 10
    
    def test_validate_valid(self):
        """Test validation with valid settings."""
        es = EditorSettings(gridSize=20)
        errors = es.validate()
        assert errors == []
    
    def test_validate_grid_too_small(self):
        """Test validation with grid size too small."""
        es = EditorSettings(gridSize=0)
        errors = es.validate()
        assert len(errors) == 1
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        es = EditorSettings(showGrid=False, gridSize=15)
        d = es.to_dict()
        assert d["showGrid"] is False
        assert d["gridSize"] == 15


class TestConfig:
    """Tests for Config class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        assert config.debugLogging is False
        assert config.logLevel == "INFO"
        assert config.autoSave is True
        assert config.autoSaveIntervalSeconds == 30
        assert config.theme == "system"
    
    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        config = Config()
        is_valid, errors = config.validate()
        assert is_valid is True
        assert errors == []
    
    def test_validate_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = Config(logLevel="INVALID")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert any("log level" in e.lower() for e in errors)
    
    def test_validate_invalid_theme(self):
        """Test validation with invalid theme."""
        config = Config(theme="invalid_theme")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert any("theme" in e.lower() for e in errors)
    
    def test_validate_autosave_interval_too_small(self):
        """Test validation with auto-save interval too small."""
        config = Config(autoSaveIntervalSeconds=2)
        is_valid, errors = config.validate()
        assert is_valid is False
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = Config(theme="dark", debugLogging=True)
        d = config.to_dict()
        assert d["theme"] == "dark"
        assert d["debugLogging"] is True
        assert "windowSize" in d
        assert "editor" in d
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "theme": "light",
            "autoSave": False,
            "windowSize": {"width": 1400, "height": 900}
        }
        config = Config.from_dict(data)
        assert config.theme == "light"
        assert config.autoSave is False
        assert config.windowSize.width == 1400
    
    def test_to_json_and_back(self):
        """Test JSON serialization round-trip."""
        config = Config(theme="dark", maxUndoSteps=100)
        json_str = config.to_json()
        
        restored = Config.from_json(json_str)
        assert restored.theme == "dark"
        assert restored.maxUndoSteps == 100
    
    def test_get_defaults(self):
        """Test getting default configuration."""
        defaults = Config.get_defaults()
        assert defaults.debugLogging is False
        assert defaults.theme == "system"
    
    def test_get_nested_value(self):
        """Test getting nested configuration value."""
        config = Config()
        width = config.get("windowSize.width")
        assert width == 1200
    
    def test_get_missing_key(self):
        """Test getting missing key returns default."""
        config = Config()
        value = config.get("nonexistent.key", "default")
        assert value == "default"
    
    def test_set_value(self):
        """Test setting configuration value."""
        config = Config()
        new_config = config.set("theme", "dark")
        assert new_config.theme == "dark"
        assert config.theme == "system"  # Original unchanged
    
    def test_set_nested_value(self):
        """Test setting nested configuration value."""
        config = Config()
        new_config = config.set("windowSize.width", 1600)
        assert new_config.get("windowSize.width") == 1600


class TestConfigService:
    """Tests for ConfigService class."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = ConfigService()
        assert service.config is not None
        assert service.is_loaded is False
    
    def test_load_defaults(self):
        """Test loading defaults when no config exists."""
        service = ConfigService()
        config = service.load()
        assert config.theme == "system"
        assert service.is_loaded is True
    
    def test_get_value(self):
        """Test getting configuration value."""
        service = ConfigService()
        service.load()
        theme = service.get("theme")
        assert theme == "system"
    
    def test_set_value(self):
        """Test setting configuration value."""
        service = ConfigService()
        service.load()
        
        result = service.set("theme", "dark")
        assert result is True
        assert service.get("theme") == "dark"
    
    def test_set_invalid_value(self):
        """Test setting invalid configuration value."""
        service = ConfigService()
        service.load()
        
        result = service.set("theme", "invalid_theme")
        assert result is False
        assert service.get("theme") == "system"  # Unchanged
    
    def test_reset_specific_key(self):
        """Test resetting specific configuration key."""
        service = ConfigService()
        service.load()
        service.set("theme", "dark")
        
        service.reset("theme")
        assert service.get("theme") == "system"
    
    def test_reset_all(self):
        """Test resetting all configuration."""
        service = ConfigService()
        service.load()
        service.set("theme", "dark")
        service.set("debugLogging", True)
        
        service.reset()
        assert service.get("theme") == "system"
        assert service.get("debugLogging") is False
    
    def test_listener_notification(self):
        """Test configuration change listener."""
        service = ConfigService()
        service.load()
        
        changes = []
        def listener(key, old_val, new_val):
            changes.append((key, old_val, new_val))
        
        service.add_listener(listener)
        service.set("theme", "dark")
        
        assert len(changes) == 1
        assert changes[0] == ("theme", "system", "dark")
    
    def test_remove_listener(self):
        """Test removing configuration change listener."""
        service = ConfigService()
        service.load()
        
        changes = []
        def listener(key, old_val, new_val):
            changes.append((key, old_val, new_val))
        
        service.add_listener(listener)
        service.remove_listener(listener)
        service.set("theme", "dark")
        
        assert len(changes) == 0
    
    def test_get_all(self):
        """Test getting all configuration values."""
        service = ConfigService()
        service.load()
        
        all_config = service.get_all()
        assert "theme" in all_config
        assert "debugLogging" in all_config
        assert "windowSize" in all_config
    
    def test_validate(self):
        """Test configuration validation."""
        service = ConfigService()
        service.load()
        
        is_valid, errors = service.validate()
        assert is_valid is True
        assert errors == []
    
    def test_add_recent_template(self):
        """Test adding recent template."""
        service = ConfigService()
        service.load()
        
        service.add_recent_template("template_1")
        service.add_recent_template("template_2")
        
        recent = service.get("recentTemplates")
        assert recent[0] == "template_2"  # Most recent first
        assert recent[1] == "template_1"
    
    def test_add_recent_template_deduplication(self):
        """Test recent template deduplication."""
        service = ConfigService()
        service.load()
        
        service.add_recent_template("template_1")
        service.add_recent_template("template_2")
        service.add_recent_template("template_1")  # Add again
        
        recent = service.get("recentTemplates")
        assert recent.count("template_1") == 1
        assert recent[0] == "template_1"  # Now first
    
    def test_clear_recent_templates(self):
        """Test clearing recent templates."""
        service = ConfigService()
        service.load()
        
        service.add_recent_template("template_1")
        service.clear_recent_templates()
        
        recent = service.get("recentTemplates")
        assert recent == []


class TestConfigFilePersistence:
    """Tests for configuration file persistence."""
    
    def test_save_and_load(self):
        """Test saving and loading configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save
            service1 = ConfigService(addon_dir=tmpdir)
            service1.load()
            service1.set("theme", "dark")
            service1.set("debugLogging", True)
            result = service1.save()
            assert result is True
            
            # Load in new service
            service2 = ConfigService(addon_dir=tmpdir)
            service2.load()
            assert service2.get("theme") == "dark"
            assert service2.get("debugLogging") is True
    
    def test_config_file_path(self):
        """Test config file path property."""
        service = ConfigService(addon_dir="/tmp/test_addon")
        assert service.config_file == Path("/tmp/test_addon/user_config.json")
    
    def test_config_file_none_without_dir(self):
        """Test config file is None without addon dir."""
        service = ConfigService()
        assert service.config_file is None


class TestGlobalFunctions:
    """Tests for global configuration functions."""
    
    def test_init_config_service(self):
        """Test initializing global config service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = init_config_service(addon_dir=tmpdir)
            assert service is not None
            assert service.is_loaded is True
    
    def test_get_config_service(self):
        """Test getting global config service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_config_service(addon_dir=tmpdir)
            service = get_config_service()
            assert service is not None


class TestConfigSchema:
    """Tests for CONFIG_SCHEMA metadata."""
    
    def test_schema_has_all_keys(self):
        """Test schema contains all config keys."""
        config = Config()
        config_dict = config.to_dict()
        
        # Check that documented keys exist in schema
        for key in ["debugLogging", "logLevel", "autoSave", "theme"]:
            assert key in CONFIG_SCHEMA
    
    def test_schema_has_types(self):
        """Test schema entries have type information."""
        for key, info in CONFIG_SCHEMA.items():
            assert "type" in info
            # Objects have properties instead of direct default
            if info["type"] != "object":
                assert "default" in info
