"""
Configuration service for Anki Template Designer.

Plan 10: Handles loading, saving, and validation of configuration.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..core.config_schema import Config


logger = logging.getLogger("anki_template_designer.services.config_service")


class ConfigService:
    """Service for managing addon configuration.
    
    Handles:
    - Loading configuration from file or Anki addon manager
    - Saving configuration changes
    - Validation of configuration values
    - Notification of configuration changes
    
    Example:
        service = ConfigService(addon_dir="/path/to/addon")
        service.load()
        
        # Get values
        theme = service.get("theme")
        
        # Set values
        service.set("theme", "dark")
        service.save()
    """
    
    def __init__(
        self,
        addon_dir: Optional[str] = None,
        config_filename: str = "user_config.json"
    ) -> None:
        """Initialize configuration service.
        
        Args:
            addon_dir: Addon directory path for config file storage.
            config_filename: Name of the user config file.
        """
        self._addon_dir = Path(addon_dir) if addon_dir else None
        self._config_filename = config_filename
        self._config: Config = Config.get_defaults()
        self._listeners: List[Callable[[str, Any, Any], None]] = []
        self._loaded = False
        self._anki_addon_manager: Any = None
        self._anki_addon_name: Optional[str] = None
    
    @property
    def config(self) -> Config:
        """Get current configuration."""
        return self._config
    
    @property
    def config_file(self) -> Optional[Path]:
        """Get path to user config file."""
        if self._addon_dir:
            return self._addon_dir / self._config_filename
        return None
    
    @property
    def is_loaded(self) -> bool:
        """Check if configuration has been loaded."""
        return self._loaded
    
    def set_anki_addon_manager(self, manager: Any, addon_name: str) -> None:
        """Set the Anki addon manager for config integration.
        
        Args:
            manager: Anki's addon manager instance.
            addon_name: Name of the addon (usually __name__).
        """
        self._anki_addon_manager = manager
        self._anki_addon_name = addon_name
    
    def load(self) -> Config:
        """Load configuration from storage.
        
        Tries to load from:
        1. Anki addon manager (if configured)
        2. User config file
        3. Falls back to defaults
        
        Returns:
            Loaded configuration.
        """
        config_dict: Dict[str, Any] = {}
        
        # Try Anki addon manager first
        if self._anki_addon_manager and self._anki_addon_name:
            try:
                anki_config = self._anki_addon_manager.getConfig(self._anki_addon_name)
                if anki_config:
                    config_dict = anki_config
                    logger.debug("Loaded config from Anki addon manager")
            except Exception as e:
                logger.warning(f"Failed to load from Anki addon manager: {e}")
        
        # Try user config file
        if not config_dict and self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_dict = json.load(f)
                logger.debug(f"Loaded config from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Parse and validate
        if config_dict:
            self._config = Config.from_dict(config_dict)
            is_valid, errors = self._config.validate()
            if not is_valid:
                logger.warning(f"Config validation errors: {errors}")
                # Merge with defaults to fix invalid values
                self._config = self._config.merge_with_defaults()
        else:
            self._config = Config.get_defaults()
            logger.debug("Using default configuration")
        
        self._loaded = True
        return self._config
    
    def save(self) -> bool:
        """Save configuration to storage.
        
        Saves to:
        1. Anki addon manager (if configured)
        2. User config file
        
        Returns:
            True if save was successful.
        """
        config_dict = self._config.to_dict()
        success = False
        
        # Save to Anki addon manager
        if self._anki_addon_manager and self._anki_addon_name:
            try:
                self._anki_addon_manager.writeConfig(self._anki_addon_name, config_dict)
                logger.debug("Saved config to Anki addon manager")
                success = True
            except Exception as e:
                logger.error(f"Failed to save to Anki addon manager: {e}")
        
        # Save to user config file
        if self.config_file:
            try:
                # Ensure directory exists
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2)
                logger.debug(f"Saved config to {self.config_file}")
                success = True
            except Exception as e:
                logger.error(f"Failed to save config file: {e}")
        
        return success
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation).
            default: Default value if not found.
            
        Returns:
            Configuration value.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = False) -> bool:
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation).
            value: New value.
            save: Whether to save immediately.
            
        Returns:
            True if set was successful.
        """
        old_value = self.get(key)
        
        try:
            new_config = self._config.set(key, value)
            
            # Validate new config
            is_valid, errors = new_config.validate()
            if not is_valid:
                logger.warning(f"Invalid config value: {errors}")
                return False
            
            self._config = new_config
            
            # Notify listeners
            self._notify_listeners(key, old_value, value)
            
            # Save if requested
            if save:
                self.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config value: {e}")
            return False
    
    def reset(self, key: Optional[str] = None) -> bool:
        """Reset configuration to defaults.
        
        Args:
            key: Optional specific key to reset. If None, resets all.
            
        Returns:
            True if reset was successful.
        """
        if key is None:
            old_config = self._config
            self._config = Config.get_defaults()
            
            # Notify for all changed keys
            old_dict = old_config.to_dict()
            new_dict = self._config.to_dict()
            for k in old_dict:
                if old_dict[k] != new_dict.get(k):
                    self._notify_listeners(k, old_dict[k], new_dict.get(k))
            
            return True
        else:
            defaults = Config.get_defaults()
            default_value = defaults.get(key)
            return self.set(key, default_value)
    
    def add_listener(self, callback: Callable[[str, Any, Any], None]) -> None:
        """Add a configuration change listener.
        
        Args:
            callback: Function called with (key, old_value, new_value).
        """
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[str, Any, Any], None]) -> None:
        """Remove a configuration change listener.
        
        Args:
            callback: Previously registered callback.
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, key: str, old_value: Any, new_value: Any) -> None:
        """Notify all listeners of a configuration change.
        
        Args:
            key: Changed configuration key.
            old_value: Previous value.
            new_value: New value.
        """
        for listener in self._listeners:
            try:
                listener(key, old_value, new_value)
            except Exception as e:
                logger.error(f"Config listener error: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values as dictionary.
        
        Returns:
            Complete configuration dictionary.
        """
        return self._config.to_dict()
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate current configuration.
        
        Returns:
            Tuple of (is_valid, error_messages).
        """
        return self._config.validate()
    
    def add_recent_template(self, template_id: str) -> None:
        """Add a template to recent templates list.
        
        Args:
            template_id: Template identifier to add.
        """
        recent = list(self._config.recentTemplates)
        
        # Remove if already exists
        if template_id in recent:
            recent.remove(template_id)
        
        # Add to front
        recent.insert(0, template_id)
        
        # Trim to max
        max_recent = self._config.maxRecentTemplates
        recent = recent[:max_recent]
        
        # Update config
        self.set("recentTemplates", recent)
    
    def clear_recent_templates(self) -> None:
        """Clear all recent templates."""
        self.set("recentTemplates", [])


# Global service instance
_global_service: Optional[ConfigService] = None


def get_config_service() -> Optional[ConfigService]:
    """Get the global configuration service instance.
    
    Returns:
        ConfigService instance or None if not initialized.
    """
    return _global_service


def init_config_service(addon_dir: Optional[str] = None) -> ConfigService:
    """Initialize the global configuration service.
    
    Args:
        addon_dir: Addon directory path.
        
    Returns:
        Initialized ConfigService.
    """
    global _global_service
    
    _global_service = ConfigService(addon_dir=addon_dir)
    _global_service.load()
    
    return _global_service
