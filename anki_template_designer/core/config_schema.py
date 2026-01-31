"""
Configuration schema for Anki Template Designer.

Plan 10: Defines configuration structure, defaults, and validation.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import json


class Theme(Enum):
    """UI theme options."""
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class LogLevel(Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class WindowSize:
    """Window dimensions configuration."""
    width: int = 1200
    height: int = 800
    
    def validate(self) -> List[str]:
        """Validate window size values.
        
        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []
        if self.width < 400:
            errors.append(f"Window width must be at least 400, got {self.width}")
        if self.width > 4000:
            errors.append(f"Window width must be at most 4000, got {self.width}")
        if self.height < 300:
            errors.append(f"Window height must be at least 300, got {self.height}")
        if self.height > 3000:
            errors.append(f"Window height must be at most 3000, got {self.height}")
        return errors
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {"width": self.width, "height": self.height}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WindowSize":
        """Create from dictionary."""
        return cls(
            width=int(data.get("width", 1200)),
            height=int(data.get("height", 800))
        )


@dataclass
class EditorSettings:
    """Editor-specific settings."""
    showGrid: bool = True
    snapToGrid: bool = True
    gridSize: int = 10
    showRulers: bool = True
    highlightOnHover: bool = True
    
    def validate(self) -> List[str]:
        """Validate editor settings.
        
        Returns:
            List of validation error messages.
        """
        errors = []
        if self.gridSize < 1:
            errors.append(f"Grid size must be at least 1, got {self.gridSize}")
        if self.gridSize > 100:
            errors.append(f"Grid size must be at most 100, got {self.gridSize}")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditorSettings":
        """Create from dictionary."""
        return cls(
            showGrid=bool(data.get("showGrid", True)),
            snapToGrid=bool(data.get("snapToGrid", True)),
            gridSize=int(data.get("gridSize", 10)),
            showRulers=bool(data.get("showRulers", True)),
            highlightOnHover=bool(data.get("highlightOnHover", True))
        )


@dataclass
class Config:
    """Main configuration class for Anki Template Designer.
    
    This defines all configurable options with their defaults and validation.
    """
    
    # Logging settings
    debugLogging: bool = False
    logLevel: str = "INFO"
    
    # Auto-save settings
    autoSave: bool = True
    autoSaveIntervalSeconds: int = 30
    
    # UI settings
    theme: str = "system"
    windowSize: WindowSize = field(default_factory=WindowSize)
    
    # Recent templates
    recentTemplates: List[str] = field(default_factory=list)
    maxRecentTemplates: int = 10
    
    # Editor settings
    editor: EditorSettings = field(default_factory=EditorSettings)
    
    # Undo/redo settings
    maxUndoSteps: int = 50
    
    # Performance settings
    enableAnimations: bool = True
    lazyLoadComponents: bool = True
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate entire configuration.
        
        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []
        
        # Validate log level
        valid_log_levels = [e.value for e in LogLevel]
        if self.logLevel not in valid_log_levels:
            errors.append(f"Invalid log level '{self.logLevel}', must be one of {valid_log_levels}")
        
        # Validate theme
        valid_themes = [e.value for e in Theme]
        if self.theme not in valid_themes:
            errors.append(f"Invalid theme '{self.theme}', must be one of {valid_themes}")
        
        # Validate auto-save interval
        if self.autoSaveIntervalSeconds < 5:
            errors.append(f"Auto-save interval must be at least 5 seconds, got {self.autoSaveIntervalSeconds}")
        if self.autoSaveIntervalSeconds > 600:
            errors.append(f"Auto-save interval must be at most 600 seconds, got {self.autoSaveIntervalSeconds}")
        
        # Validate max recent templates
        if self.maxRecentTemplates < 1:
            errors.append(f"Max recent templates must be at least 1, got {self.maxRecentTemplates}")
        if self.maxRecentTemplates > 50:
            errors.append(f"Max recent templates must be at most 50, got {self.maxRecentTemplates}")
        
        # Validate max undo steps
        if self.maxUndoSteps < 10:
            errors.append(f"Max undo steps must be at least 10, got {self.maxUndoSteps}")
        if self.maxUndoSteps > 500:
            errors.append(f"Max undo steps must be at most 500, got {self.maxUndoSteps}")
        
        # Validate nested objects
        errors.extend(self.windowSize.validate())
        errors.extend(self.editor.validate())
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of configuration.
        """
        return {
            "debugLogging": self.debugLogging,
            "logLevel": self.logLevel,
            "autoSave": self.autoSave,
            "autoSaveIntervalSeconds": self.autoSaveIntervalSeconds,
            "theme": self.theme,
            "windowSize": self.windowSize.to_dict(),
            "recentTemplates": self.recentTemplates[:],
            "maxRecentTemplates": self.maxRecentTemplates,
            "editor": self.editor.to_dict(),
            "maxUndoSteps": self.maxUndoSteps,
            "enableAnimations": self.enableAnimations,
            "lazyLoadComponents": self.lazyLoadComponents,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string.
        
        Args:
            indent: JSON indentation level.
            
        Returns:
            JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary.
        
        Args:
            data: Configuration dictionary.
            
        Returns:
            Config instance with values from dictionary.
        """
        # Handle nested objects
        window_size_data = data.get("windowSize", {})
        if isinstance(window_size_data, dict):
            window_size = WindowSize.from_dict(window_size_data)
        else:
            window_size = WindowSize()
        
        editor_data = data.get("editor", {})
        if isinstance(editor_data, dict):
            editor = EditorSettings.from_dict(editor_data)
        else:
            editor = EditorSettings()
        
        # Handle recent templates (ensure list)
        recent = data.get("recentTemplates", [])
        if not isinstance(recent, list):
            recent = []
        
        return cls(
            debugLogging=bool(data.get("debugLogging", False)),
            logLevel=str(data.get("logLevel", "INFO")),
            autoSave=bool(data.get("autoSave", True)),
            autoSaveIntervalSeconds=int(data.get("autoSaveIntervalSeconds", 30)),
            theme=str(data.get("theme", "system")),
            windowSize=window_size,
            recentTemplates=recent,
            maxRecentTemplates=int(data.get("maxRecentTemplates", 10)),
            editor=editor,
            maxUndoSteps=int(data.get("maxUndoSteps", 50)),
            enableAnimations=bool(data.get("enableAnimations", True)),
            lazyLoadComponents=bool(data.get("lazyLoadComponents", True)),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Config":
        """Create Config from JSON string.
        
        Args:
            json_str: JSON configuration string.
            
        Returns:
            Config instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def get_defaults(cls) -> "Config":
        """Get default configuration.
        
        Returns:
            Config instance with all default values.
        """
        return cls()
    
    def merge_with_defaults(self) -> "Config":
        """Create a new config with missing values filled from defaults.
        
        Returns:
            New Config with all values populated.
        """
        defaults = Config.get_defaults()
        merged_dict = defaults.to_dict()
        merged_dict.update(self.to_dict())
        return Config.from_dict(merged_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation for nested).
            default: Default value if key not found.
            
        Returns:
            Configuration value.
        """
        parts = key.split(".")
        value: Any = self.to_dict()
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> "Config":
        """Set a configuration value and return new Config.
        
        Args:
            key: Configuration key (supports dot notation).
            value: New value.
            
        Returns:
            New Config instance with updated value.
        """
        data = self.to_dict()
        parts = key.split(".")
        
        # Navigate to parent
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set value
        current[parts[-1]] = value
        
        return Config.from_dict(data)


# Schema metadata for documentation/UI generation
CONFIG_SCHEMA = {
    "debugLogging": {
        "type": "boolean",
        "default": False,
        "description": "Enable debug logging for troubleshooting"
    },
    "logLevel": {
        "type": "enum",
        "values": ["DEBUG", "INFO", "WARNING", "ERROR"],
        "default": "INFO",
        "description": "Minimum log level to record"
    },
    "autoSave": {
        "type": "boolean",
        "default": True,
        "description": "Automatically save templates while editing"
    },
    "autoSaveIntervalSeconds": {
        "type": "integer",
        "min": 5,
        "max": 600,
        "default": 30,
        "description": "Seconds between auto-saves"
    },
    "theme": {
        "type": "enum",
        "values": ["system", "light", "dark"],
        "default": "system",
        "description": "UI color theme"
    },
    "windowSize": {
        "type": "object",
        "properties": {
            "width": {"type": "integer", "min": 400, "max": 4000, "default": 1200},
            "height": {"type": "integer", "min": 300, "max": 3000, "default": 800}
        },
        "description": "Default window dimensions"
    },
    "maxRecentTemplates": {
        "type": "integer",
        "min": 1,
        "max": 50,
        "default": 10,
        "description": "Maximum number of recent templates to remember"
    },
    "maxUndoSteps": {
        "type": "integer",
        "min": 10,
        "max": 500,
        "default": 50,
        "description": "Maximum number of undo steps to keep"
    },
    "enableAnimations": {
        "type": "boolean",
        "default": True,
        "description": "Enable UI animations"
    },
    "lazyLoadComponents": {
        "type": "boolean",
        "default": True,
        "description": "Lazy load components for better performance"
    }
}
