"""
Keyboard Shortcuts Manager for Anki Template Designer.

Plan 19: Comprehensive keyboard shortcuts system with customizable shortcuts,
conflict detection, profiles, and internationalization support.
"""

import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("anki_template_designer.services.shortcuts_manager")


class ShortcutScope(Enum):
    """Scope where shortcut is active."""
    GLOBAL = "global"
    EDITOR = "editor"
    PREVIEW = "preview"
    PROPERTIES = "properties"
    COMPONENT_LIBRARY = "component_library"


class ShortcutCategory(Enum):
    """Category of shortcut."""
    EDIT = "edit"
    VIEW = "view"
    NAVIGATION = "navigation"
    FILE = "file"
    HELP = "help"
    DEBUG = "debug"
    CUSTOM = "custom"


@dataclass
class Shortcut:
    """A keyboard shortcut definition."""
    id: str = ""
    name: str = ""
    description: str = ""
    keys: str = ""  # e.g., "Ctrl+S", "Ctrl+Shift+Z"
    action: str = ""
    category: ShortcutCategory = ShortcutCategory.CUSTOM
    scope: ShortcutScope = ShortcutScope.GLOBAL
    is_customizable: bool = True
    is_enabled: bool = True
    platform: Optional[str] = None  # "windows", "mac", "linux", or None for all
    conflicting_shortcuts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keys": self.keys,
            "action": self.action,
            "category": self.category.value,
            "scope": self.scope.value,
            "isCustomizable": self.is_customizable,
            "isEnabled": self.is_enabled,
            "platform": self.platform,
            "conflictingShortcuts": self.conflicting_shortcuts
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shortcut":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            keys=data.get("keys", ""),
            action=data.get("action", ""),
            category=ShortcutCategory(data.get("category", "custom")),
            scope=ShortcutScope(data.get("scope", "global")),
            is_customizable=data.get("isCustomizable", data.get("is_customizable", True)),
            is_enabled=data.get("isEnabled", data.get("is_enabled", True)),
            platform=data.get("platform"),
            conflicting_shortcuts=data.get("conflictingShortcuts", data.get("conflicting_shortcuts", []))
        )
    
    def copy(self) -> "Shortcut":
        """Create a deep copy."""
        return Shortcut(
            id=self.id,
            name=self.name,
            description=self.description,
            keys=self.keys,
            action=self.action,
            category=self.category,
            scope=self.scope,
            is_customizable=self.is_customizable,
            is_enabled=self.is_enabled,
            platform=self.platform,
            conflicting_shortcuts=self.conflicting_shortcuts.copy()
        )


@dataclass
class ShortcutProfile:
    """A profile containing multiple shortcuts."""
    id: str = ""
    name: str = ""
    description: str = ""
    shortcuts: Dict[str, Shortcut] = field(default_factory=dict)
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "shortcuts": {k: v.to_dict() for k, v in self.shortcuts.items()},
            "isDefault": self.is_default,
            "createdAt": self.created_at.isoformat(),
            "modifiedAt": self.modified_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShortcutProfile":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            shortcuts={
                k: Shortcut.from_dict(v)
                for k, v in data.get("shortcuts", {}).items()
            },
            is_default=data.get("isDefault", data.get("is_default", False)),
            created_at=datetime.fromisoformat(data.get("createdAt", data.get("created_at", datetime.now().isoformat()))),
            modified_at=datetime.fromisoformat(data.get("modifiedAt", data.get("modified_at", datetime.now().isoformat())))
        )


@dataclass
class ShortcutConflict:
    """Information about conflicting shortcuts."""
    shortcut_id: str = ""
    shortcut_name: str = ""
    conflicting_id: str = ""
    conflicting_name: str = ""
    keys: str = ""
    severity: str = "warning"  # "error", "warning", "info"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "shortcutId": self.shortcut_id,
            "shortcutName": self.shortcut_name,
            "conflictingId": self.conflicting_id,
            "conflictingName": self.conflicting_name,
            "keys": self.keys,
            "severity": self.severity
        }


# Default shortcuts
DEFAULT_SHORTCUTS = {
    "undo": Shortcut(
        id="undo",
        name="Undo",
        description="Undo last action",
        keys="Ctrl+Z",
        action="undo",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "redo": Shortcut(
        id="redo",
        name="Redo",
        description="Redo last undone action",
        keys="Ctrl+Y",
        action="redo",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "redo_alt": Shortcut(
        id="redo_alt",
        name="Redo (Alt)",
        description="Redo last undone action",
        keys="Ctrl+Shift+Z",
        action="redo",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "save": Shortcut(
        id="save",
        name="Save",
        description="Save template",
        keys="Ctrl+S",
        action="save",
        category=ShortcutCategory.FILE,
        is_customizable=True
    ),
    "copy": Shortcut(
        id="copy",
        name="Copy",
        description="Copy selected component",
        keys="Ctrl+C",
        action="copy",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "cut": Shortcut(
        id="cut",
        name="Cut",
        description="Cut selected component",
        keys="Ctrl+X",
        action="cut",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "paste": Shortcut(
        id="paste",
        name="Paste",
        description="Paste copied component",
        keys="Ctrl+V",
        action="paste",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "delete": Shortcut(
        id="delete",
        name="Delete",
        description="Delete selected component",
        keys="Delete",
        action="delete",
        category=ShortcutCategory.EDIT,
        is_customizable=False
    ),
    "select_all": Shortcut(
        id="select_all",
        name="Select All",
        description="Select all components",
        keys="Ctrl+A",
        action="select_all",
        category=ShortcutCategory.EDIT,
        is_customizable=False
    ),
    "deselect": Shortcut(
        id="deselect",
        name="Deselect",
        description="Deselect all components",
        keys="Escape",
        action="deselect",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "duplicate": Shortcut(
        id="duplicate",
        name="Duplicate",
        description="Duplicate selected component",
        keys="Ctrl+D",
        action="duplicate",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "zoom_in": Shortcut(
        id="zoom_in",
        name="Zoom In",
        description="Increase zoom level",
        keys="Ctrl+Plus",
        action="zoom_in",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "zoom_out": Shortcut(
        id="zoom_out",
        name="Zoom Out",
        description="Decrease zoom level",
        keys="Ctrl+Minus",
        action="zoom_out",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "zoom_reset": Shortcut(
        id="zoom_reset",
        name="Reset Zoom",
        description="Reset zoom to default",
        keys="Ctrl+0",
        action="zoom_reset",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "zoom_fit": Shortcut(
        id="zoom_fit",
        name="Fit to View",
        description="Fit canvas to view",
        keys="Ctrl+1",
        action="zoom_fit",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "toggle_preview": Shortcut(
        id="toggle_preview",
        name="Toggle Preview",
        description="Toggle preview panel",
        keys="Ctrl+P",
        action="toggle_preview",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "toggle_properties": Shortcut(
        id="toggle_properties",
        name="Toggle Properties",
        description="Toggle properties panel",
        keys="Ctrl+I",
        action="toggle_properties",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "help": Shortcut(
        id="help",
        name="Help",
        description="Open help dialog",
        keys="F1",
        action="help",
        category=ShortcutCategory.HELP,
        is_customizable=False
    ),
    "search": Shortcut(
        id="search",
        name="Search",
        description="Open search dialog",
        keys="Ctrl+F",
        action="search",
        category=ShortcutCategory.NAVIGATION,
        is_customizable=True
    ),
    "new_template": Shortcut(
        id="new_template",
        name="New Template",
        description="Create new template",
        keys="Ctrl+N",
        action="new_template",
        category=ShortcutCategory.FILE,
        is_customizable=True
    ),
    "open_template": Shortcut(
        id="open_template",
        name="Open Template",
        description="Open existing template",
        keys="Ctrl+O",
        action="open_template",
        category=ShortcutCategory.FILE,
        is_customizable=True
    ),
    "close_template": Shortcut(
        id="close_template",
        name="Close Template",
        description="Close current template",
        keys="Ctrl+W",
        action="close_template",
        category=ShortcutCategory.FILE,
        is_customizable=True
    ),
    "move_up": Shortcut(
        id="move_up",
        name="Move Up",
        description="Move component up in layer order",
        keys="Ctrl+Up",
        action="move_up",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "move_down": Shortcut(
        id="move_down",
        name="Move Down",
        description="Move component down in layer order",
        keys="Ctrl+Down",
        action="move_down",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "move_to_front": Shortcut(
        id="move_to_front",
        name="Move to Front",
        description="Move component to front",
        keys="Ctrl+Shift+Up",
        action="move_to_front",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "move_to_back": Shortcut(
        id="move_to_back",
        name="Move to Back",
        description="Move component to back",
        keys="Ctrl+Shift+Down",
        action="move_to_back",
        category=ShortcutCategory.EDIT,
        is_customizable=True
    ),
    "toggle_grid": Shortcut(
        id="toggle_grid",
        name="Toggle Grid",
        description="Toggle grid visibility",
        keys="Ctrl+G",
        action="toggle_grid",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
    "toggle_snap": Shortcut(
        id="toggle_snap",
        name="Toggle Snap",
        description="Toggle snap to grid",
        keys="Ctrl+Shift+G",
        action="toggle_snap",
        category=ShortcutCategory.VIEW,
        is_customizable=True
    ),
}


class ShortcutsManager:
    """Manager for keyboard shortcuts with profiles and conflict detection."""

    def __init__(self, default_profile_name: str = "Default"):
        """Initialize the shortcuts manager.
        
        Args:
            default_profile_name: Name for the default profile.
        """
        self._profiles: Dict[str, ShortcutProfile] = {}
        self._current_profile: Optional[ShortcutProfile] = None
        self._action_handlers: Dict[str, Callable] = {}
        self._listeners: List[Callable] = []
        self._conflicts: List[ShortcutConflict] = []
        self._lock = threading.RLock()

        # Create default profile
        self._create_default_profile(default_profile_name)
        
        logger.info("ShortcutsManager initialized")

    def _create_default_profile(self, name: str) -> None:
        """Create the default profile with built-in shortcuts."""
        shortcuts = {k: v.copy() for k, v in DEFAULT_SHORTCUTS.items()}
        
        profile = ShortcutProfile(
            id="default",
            name=name,
            description="Default shortcuts",
            shortcuts=shortcuts,
            is_default=True
        )
        self._profiles[profile.id] = profile
        self._current_profile = profile

    def create_profile(self, name: str, description: str = "") -> str:
        """Create a new shortcut profile.
        
        Args:
            name: Profile name.
            description: Profile description.
            
        Returns:
            Profile ID.
        """
        with self._lock:
            profile_id = name.lower().replace(" ", "_")
            
            # Deep copy shortcuts
            shortcuts = {k: v.copy() for k, v in DEFAULT_SHORTCUTS.items()}
            
            profile = ShortcutProfile(
                id=profile_id,
                name=name,
                description=description,
                shortcuts=shortcuts
            )
            self._profiles[profile_id] = profile
            self._notify_listeners("profile_created", {"profileId": profile_id})
            
            logger.info(f"Created profile: {profile_id}")
            return profile_id

    def switch_profile(self, profile_id: str) -> bool:
        """Switch to a different profile.
        
        Args:
            profile_id: Target profile ID.
            
        Returns:
            True if successful.
        """
        with self._lock:
            if profile_id not in self._profiles:
                return False

            self._current_profile = self._profiles[profile_id]
            self._notify_listeners("profile_switched", {"profileId": profile_id})
            
            logger.info(f"Switched to profile: {profile_id}")
            return True

    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all profiles.
        
        Returns:
            List of profile info dictionaries.
        """
        with self._lock:
            return [p.to_dict() for p in self._profiles.values()]

    def get_current_profile(self) -> Optional[Dict[str, Any]]:
        """Get current profile.
        
        Returns:
            Current profile as dictionary or None.
        """
        with self._lock:
            return self._current_profile.to_dict() if self._current_profile else None

    def update_shortcut(self, shortcut_id: str, keys: str,
                       profile_id: Optional[str] = None) -> bool:
        """Update a shortcut's key binding.
        
        Args:
            shortcut_id: Shortcut ID.
            keys: New key binding.
            profile_id: Profile ID (uses current if not specified).
            
        Returns:
            True if successful.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile or shortcut_id not in profile.shortcuts:
                return False

            shortcut = profile.shortcuts[shortcut_id]
            if not shortcut.is_customizable:
                return False

            # Prevent empty keys
            if not keys or not keys.strip():
                return False

            # Check for conflicts
            conflicts = self._detect_conflicts(shortcut_id, keys, profile)
            if conflicts:
                self._conflicts = conflicts
                self._notify_listeners("conflicts_detected", {
                    "conflicts": [c.to_dict() for c in conflicts]
                })
                return False

            shortcut.keys = keys
            profile.modified_at = datetime.now()
            self._notify_listeners("shortcut_updated", {
                "shortcutId": shortcut_id,
                "keys": keys
            })
            
            logger.debug(f"Updated shortcut {shortcut_id} to {keys}")
            return True

    def get_shortcut(self, shortcut_id: str,
                    profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific shortcut.
        
        Args:
            shortcut_id: Shortcut ID.
            profile_id: Optional profile ID.
            
        Returns:
            Shortcut as dictionary or None.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if profile and shortcut_id in profile.shortcuts:
                return profile.shortcuts[shortcut_id].to_dict()
            return None

    def get_shortcuts_by_category(self, category: str,
                                  profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get shortcuts by category.
        
        Args:
            category: Category name.
            profile_id: Optional profile ID.
            
        Returns:
            List of shortcuts.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return []

            try:
                cat = ShortcutCategory(category)
                return [
                    s.to_dict() for s in profile.shortcuts.values()
                    if s.category == cat
                ]
            except ValueError:
                return []

    def get_shortcut_by_keys(self, keys: str,
                            profile_id: Optional[str] = None,
                            enabled_only: bool = True) -> Optional[Dict[str, Any]]:
        """Find shortcut by key combination.
        
        Args:
            keys: Key combination.
            profile_id: Optional profile ID.
            enabled_only: Only return enabled shortcuts.
            
        Returns:
            Shortcut as dictionary or None.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return None

            for shortcut in profile.shortcuts.values():
                if shortcut.keys == keys:
                    if enabled_only and not shortcut.is_enabled:
                        continue
                    return shortcut.to_dict()
            return None

    def handle_shortcut(self, keys: str) -> bool:
        """Handle a keyboard shortcut press.
        
        Args:
            keys: Key combination pressed.
            
        Returns:
            True if shortcut was handled.
        """
        with self._lock:
            shortcut_dict = self.get_shortcut_by_keys(keys)
            if not shortcut_dict:
                return False

            action = shortcut_dict.get("action", "")
            shortcut_id = shortcut_dict.get("id", "")

            # Execute handler if registered
            if action in self._action_handlers:
                try:
                    self._action_handlers[action](shortcut_dict)
                    self._notify_listeners("shortcut_executed", {"shortcutId": shortcut_id})
                    logger.debug(f"Executed shortcut: {shortcut_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error executing shortcut {shortcut_id}: {e}")
                    return False

            self._notify_listeners("shortcut_executed", {"shortcutId": shortcut_id})
            return True

    def register_action_handler(self, action: str, handler: Callable) -> None:
        """Register a handler for an action.
        
        Args:
            action: Action name.
            handler: Handler function.
        """
        with self._lock:
            self._action_handlers[action] = handler
            logger.debug(f"Registered handler for action: {action}")

    def unregister_action_handler(self, action: str) -> bool:
        """Unregister an action handler.
        
        Args:
            action: Action name.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if action in self._action_handlers:
                del self._action_handlers[action]
                return True
            return False

    def _detect_conflicts(self, shortcut_id: str, keys: str,
                         profile: ShortcutProfile) -> List[ShortcutConflict]:
        """Detect conflicts with other shortcuts."""
        conflicts = []

        for sid, shortcut in profile.shortcuts.items():
            if sid == shortcut_id:
                continue
            if shortcut.keys == keys and shortcut.is_enabled:
                conflict = ShortcutConflict(
                    shortcut_id=shortcut_id,
                    shortcut_name=profile.shortcuts[shortcut_id].name,
                    conflicting_id=sid,
                    conflicting_name=shortcut.name,
                    keys=keys,
                    severity="error"
                )
                conflicts.append(conflict)

        return conflicts

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get current conflicts.
        
        Returns:
            List of conflict dictionaries.
        """
        with self._lock:
            return [c.to_dict() for c in self._conflicts]

    def resolve_conflict(self, shortcut_id: str, conflicting_id: str,
                        keep: str = "shortcut") -> bool:
        """Resolve a conflict by clearing one shortcut's keys.
        
        Args:
            shortcut_id: First shortcut ID.
            conflicting_id: Second shortcut ID.
            keep: Which to keep ("shortcut" or "conflicting").
            
        Returns:
            True if resolved.
        """
        with self._lock:
            if not self._current_profile:
                return False

            profile = self._current_profile

            if keep == "shortcut":
                # Clear conflicting shortcut's keys
                if conflicting_id in profile.shortcuts:
                    profile.shortcuts[conflicting_id].keys = ""
            else:
                # Clear this shortcut's keys
                if shortcut_id in profile.shortcuts:
                    profile.shortcuts[shortcut_id].keys = ""

            self._conflicts = []
            self._notify_listeners("conflict_resolved", {
                "shortcutId": shortcut_id,
                "conflictingId": conflicting_id
            })
            return True

    def enable_shortcut(self, shortcut_id: str,
                       profile_id: Optional[str] = None) -> bool:
        """Enable a shortcut.
        
        Args:
            shortcut_id: Shortcut ID.
            profile_id: Optional profile ID.
            
        Returns:
            True if enabled.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if profile and shortcut_id in profile.shortcuts:
                profile.shortcuts[shortcut_id].is_enabled = True
                self._notify_listeners("shortcut_enabled", {"shortcutId": shortcut_id})
                return True
            return False

    def disable_shortcut(self, shortcut_id: str,
                        profile_id: Optional[str] = None) -> bool:
        """Disable a shortcut.
        
        Args:
            shortcut_id: Shortcut ID.
            profile_id: Optional profile ID.
            
        Returns:
            True if disabled.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if profile and shortcut_id in profile.shortcuts:
                profile.shortcuts[shortcut_id].is_enabled = False
                self._notify_listeners("shortcut_disabled", {"shortcutId": shortcut_id})
                return True
            return False

    def reset_to_defaults(self, profile_id: Optional[str] = None) -> bool:
        """Reset profile to default shortcuts.
        
        Args:
            profile_id: Optional profile ID.
            
        Returns:
            True if reset.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return False

            profile.shortcuts = {k: v.copy() for k, v in DEFAULT_SHORTCUTS.items()}
            profile.modified_at = datetime.now()
            self._notify_listeners("reset_to_defaults", {"profileId": profile.id})
            
            logger.info(f"Reset profile to defaults: {profile.id}")
            return True

    def search_shortcuts(self, query: str,
                        profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search shortcuts by name or description.
        
        Args:
            query: Search query.
            profile_id: Optional profile ID.
            
        Returns:
            List of matching shortcuts.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return []

            query_lower = query.lower()
            results = []

            for shortcut in profile.shortcuts.values():
                if (query_lower in shortcut.name.lower() or
                    query_lower in shortcut.description.lower() or
                    query_lower in shortcut.keys.lower()):
                    results.append(shortcut.to_dict())

            return results

    def add_listener(self, listener: Callable) -> None:
        """Add event listener.
        
        Args:
            listener: Callback function(event_type, data).
        """
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        """Remove event listener.
        
        Args:
            listener: Callback to remove.
        """
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def _notify_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify listeners of changes."""
        for listener in self._listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                logger.error(f"Listener error: {e}")

    def get_all_shortcuts(self, profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all shortcuts in a profile.
        
        Args:
            profile_id: Optional profile ID.
            
        Returns:
            List of shortcuts.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return []
            return [s.to_dict() for s in profile.shortcuts.values()]

    def export_profile(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Export profile as dictionary.
        
        Args:
            profile_id: Optional profile ID.
            
        Returns:
            Profile dictionary.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return {}
            return profile.to_dict()

    def import_profile(self, data: Dict[str, Any]) -> bool:
        """Import profile from dictionary.
        
        Args:
            data: Profile data.
            
        Returns:
            True if imported.
        """
        with self._lock:
            try:
                profile = ShortcutProfile.from_dict(data)
                self._profiles[profile.id] = profile
                self._notify_listeners("profile_imported", {"profileId": profile.id})
                logger.info(f"Imported profile: {profile.id}")
                return True
            except Exception as e:
                logger.error(f"Failed to import profile: {e}")
                return False

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile.
        
        Args:
            profile_id: Profile to delete.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            if profile_id == "default" or profile_id not in self._profiles:
                return False

            del self._profiles[profile_id]
            if self._current_profile and self._current_profile.id == profile_id:
                self._current_profile = self._profiles.get("default")

            self._notify_listeners("profile_deleted", {"profileId": profile_id})
            logger.info(f"Deleted profile: {profile_id}")
            return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get shortcuts statistics.
        
        Returns:
            Statistics dictionary.
        """
        with self._lock:
            if not self._current_profile:
                return {}

            shortcuts = list(self._current_profile.shortcuts.values())
            return {
                "totalShortcuts": len(shortcuts),
                "enabledShortcuts": sum(1 for s in shortcuts if s.is_enabled),
                "customizableShortcuts": sum(1 for s in shortcuts if s.is_customizable),
                "byCategory": {
                    cat.value: len([s for s in shortcuts if s.category == cat])
                    for cat in ShortcutCategory
                },
                "totalProfiles": len(self._profiles)
            }

    def add_custom_shortcut(self, shortcut_id: str, name: str, keys: str,
                           action: str, description: str = "",
                           profile_id: Optional[str] = None) -> bool:
        """Add a custom shortcut.
        
        Args:
            shortcut_id: Unique ID for the shortcut.
            name: Display name.
            keys: Key combination.
            action: Action to execute.
            description: Optional description.
            profile_id: Optional profile ID.
            
        Returns:
            True if added.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile:
                return False

            if shortcut_id in profile.shortcuts:
                return False  # Already exists

            # Check for conflicts
            conflicts = self._detect_conflicts(shortcut_id, keys, profile)
            if conflicts:
                self._conflicts = conflicts
                return False

            shortcut = Shortcut(
                id=shortcut_id,
                name=name,
                description=description,
                keys=keys,
                action=action,
                category=ShortcutCategory.CUSTOM,
                is_customizable=True,
                is_enabled=True
            )
            
            profile.shortcuts[shortcut_id] = shortcut
            profile.modified_at = datetime.now()
            self._notify_listeners("shortcut_added", {"shortcutId": shortcut_id})
            
            logger.info(f"Added custom shortcut: {shortcut_id}")
            return True

    def remove_custom_shortcut(self, shortcut_id: str,
                              profile_id: Optional[str] = None) -> bool:
        """Remove a custom shortcut.
        
        Args:
            shortcut_id: Shortcut ID.
            profile_id: Optional profile ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            profile = self._profiles.get(profile_id) if profile_id else self._current_profile
            if not profile or shortcut_id not in profile.shortcuts:
                return False

            shortcut = profile.shortcuts[shortcut_id]
            if shortcut.category != ShortcutCategory.CUSTOM:
                return False  # Can only remove custom shortcuts

            del profile.shortcuts[shortcut_id]
            profile.modified_at = datetime.now()
            self._notify_listeners("shortcut_removed", {"shortcutId": shortcut_id})
            
            logger.info(f"Removed custom shortcut: {shortcut_id}")
            return True


# Global instance
_shortcuts_manager: Optional[ShortcutsManager] = None


def get_shortcuts_manager() -> Optional[ShortcutsManager]:
    """Get the global shortcuts manager.
    
    Returns:
        ShortcutsManager or None if not initialized.
    """
    return _shortcuts_manager


def init_shortcuts_manager(default_profile_name: str = "Default") -> ShortcutsManager:
    """Initialize the global shortcuts manager.
    
    Args:
        default_profile_name: Name for the default profile.
        
    Returns:
        Initialized ShortcutsManager.
    """
    global _shortcuts_manager
    _shortcuts_manager = ShortcutsManager(default_profile_name)
    return _shortcuts_manager
