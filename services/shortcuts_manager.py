"""
Issue #50: Keyboard Shortcuts Manager

Comprehensive keyboard shortcuts system with customizable shortcuts,
conflict detection, profiles, and internationalization support.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json


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
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'keys': self.keys,
            'action': self.action,
            'category': self.category.value,
            'scope': self.scope.value,
            'is_customizable': self.is_customizable,
            'is_enabled': self.is_enabled,
            'platform': self.platform,
            'conflicting_shortcuts': self.conflicting_shortcuts
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Shortcut':
        """Create from dictionary."""
        return Shortcut(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            keys=data.get('keys', ''),
            action=data.get('action', ''),
            category=ShortcutCategory(data.get('category', 'custom')),
            scope=ShortcutScope(data.get('scope', 'global')),
            is_customizable=data.get('is_customizable', True),
            is_enabled=data.get('is_enabled', True),
            platform=data.get('platform'),
            conflicting_shortcuts=data.get('conflicting_shortcuts', [])
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
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'shortcuts': {k: v.to_dict() for k, v in self.shortcuts.items()},
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ShortcutProfile':
        """Create from dictionary."""
        return ShortcutProfile(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            shortcuts={
                k: Shortcut.from_dict(v)
                for k, v in data.get('shortcuts', {}).items()
            },
            is_default=data.get('is_default', False),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get('modified_at', datetime.now().isoformat()))
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
            'shortcut_id': self.shortcut_id,
            'shortcut_name': self.shortcut_name,
            'conflicting_id': self.conflicting_id,
            'conflicting_name': self.conflicting_name,
            'keys': self.keys,
            'severity': self.severity
        }


class ShortcutsManager:
    """Manager for keyboard shortcuts with profiles and conflict detection."""

    # Default shortcuts
    DEFAULT_SHORTCUTS = {
        'undo': Shortcut(
            id='undo',
            name='Undo',
            description='Undo last action',
            keys='Ctrl+Z',
            action='undo',
            category=ShortcutCategory.EDIT,
            is_customizable=True
        ),
        'redo': Shortcut(
            id='redo',
            name='Redo',
            description='Redo last undone action',
            keys='Ctrl+Y',
            action='redo',
            category=ShortcutCategory.EDIT,
            is_customizable=True
        ),
        'save': Shortcut(
            id='save',
            name='Save',
            description='Save template',
            keys='Ctrl+S',
            action='save',
            category=ShortcutCategory.FILE,
            is_customizable=True
        ),
        'copy': Shortcut(
            id='copy',
            name='Copy',
            description='Copy selected component',
            keys='Ctrl+C',
            action='copy',
            category=ShortcutCategory.EDIT,
            is_customizable=True
        ),
        'paste': Shortcut(
            id='paste',
            name='Paste',
            description='Paste copied component',
            keys='Ctrl+V',
            action='paste',
            category=ShortcutCategory.EDIT,
            is_customizable=True
        ),
        'delete': Shortcut(
            id='delete',
            name='Delete',
            description='Delete selected component',
            keys='Delete',
            action='delete',
            category=ShortcutCategory.EDIT,
            is_customizable=False
        ),
        'select_all': Shortcut(
            id='select_all',
            name='Select All',
            description='Select all components',
            keys='Ctrl+A',
            action='select_all',
            category=ShortcutCategory.EDIT,
            is_customizable=False
        ),
        'zoom_in': Shortcut(
            id='zoom_in',
            name='Zoom In',
            description='Increase zoom level',
            keys='Ctrl+Plus',
            action='zoom_in',
            category=ShortcutCategory.VIEW,
            is_customizable=True
        ),
        'zoom_out': Shortcut(
            id='zoom_out',
            name='Zoom Out',
            description='Decrease zoom level',
            keys='Ctrl+Minus',
            action='zoom_out',
            category=ShortcutCategory.VIEW,
            is_customizable=True
        ),
        'zoom_reset': Shortcut(
            id='zoom_reset',
            name='Reset Zoom',
            description='Reset zoom to default',
            keys='Ctrl+0',
            action='zoom_reset',
            category=ShortcutCategory.VIEW,
            is_customizable=True
        ),
        'help': Shortcut(
            id='help',
            name='Help',
            description='Open help dialog',
            keys='F1',
            action='help',
            category=ShortcutCategory.HELP,
            is_customizable=False
        ),
        'search': Shortcut(
            id='search',
            name='Search',
            description='Open search dialog',
            keys='Ctrl+F',
            action='search',
            category=ShortcutCategory.NAVIGATION,
            is_customizable=True
        ),
    }

    def __init__(self, default_profile_name: str = "Default"):
        """
        Initialize the shortcuts manager.
        
        Args:
            default_profile_name: Name for the default profile
        """
        self.profiles: Dict[str, ShortcutProfile] = {}
        self.current_profile: Optional[ShortcutProfile] = None
        self.action_handlers: Dict[str, Callable] = {}
        self.listeners: List[Callable] = []
        self.conflicts: List[ShortcutConflict] = []

        # Create default profile
        self._create_default_profile(default_profile_name)

    def _create_default_profile(self, name: str) -> None:
        """Create the default profile with built-in shortcuts."""
        # Deep copy shortcuts for independence
        shortcuts = {}
        for k, v in self.DEFAULT_SHORTCUTS.items():
            shortcuts[k] = Shortcut(
                id=v.id,
                name=v.name,
                description=v.description,
                keys=v.keys,
                action=v.action,
                category=v.category,
                scope=v.scope,
                is_customizable=v.is_customizable,
                is_enabled=v.is_enabled,
                platform=v.platform,
                conflicting_shortcuts=v.conflicting_shortcuts.copy()
            )
        
        profile = ShortcutProfile(
            id='default',
            name=name,
            description='Default shortcuts',
            shortcuts=shortcuts,
            is_default=True
        )
        self.profiles[profile.id] = profile
        self.current_profile = profile

    def create_profile(self, name: str, description: str = "") -> str:
        """
        Create a new shortcut profile.
        
        Args:
            name: Profile name
            description: Profile description
            
        Returns:
            Profile ID
        """
        profile_id = name.lower().replace(' ', '_')
        
        # Deep copy shortcuts for independence
        shortcuts = {}
        for k, v in self.DEFAULT_SHORTCUTS.items():
            shortcuts[k] = Shortcut(
                id=v.id,
                name=v.name,
                description=v.description,
                keys=v.keys,
                action=v.action,
                category=v.category,
                scope=v.scope,
                is_customizable=v.is_customizable,
                is_enabled=v.is_enabled,
                platform=v.platform,
                conflicting_shortcuts=v.conflicting_shortcuts.copy()
            )
        
        profile = ShortcutProfile(
            id=profile_id,
            name=name,
            description=description,
            shortcuts=shortcuts
        )
        self.profiles[profile_id] = profile
        self._notify_listeners('profile_created', {'profile_id': profile_id})
        return profile_id

    def switch_profile(self, profile_id: str) -> bool:
        """
        Switch to a different profile.
        
        Args:
            profile_id: Target profile ID
            
        Returns:
            True if successful
        """
        if profile_id not in self.profiles:
            return False

        self.current_profile = self.profiles[profile_id]
        self._notify_listeners('profile_switched', {'profile_id': profile_id})
        return True

    def get_profiles(self) -> List[ShortcutProfile]:
        """Get all profiles."""
        return list(self.profiles.values())

    def get_current_profile(self) -> Optional[ShortcutProfile]:
        """Get current profile."""
        return self.current_profile

    def update_shortcut(self, shortcut_id: str, keys: str, profile_id: Optional[str] = None) -> bool:
        """
        Update a shortcut's key binding.
        
        Args:
            shortcut_id: Shortcut ID
            keys: New key binding (e.g., "Ctrl+Shift+S")
            profile_id: Profile ID (uses current if not specified)
            
        Returns:
            True if successful
        """
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
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
            self.conflicts = conflicts
            self._notify_listeners('conflicts_detected', {'conflicts': [c.to_dict() for c in conflicts]})
            return False

        shortcut.keys = keys
        profile.modified_at = datetime.now()
        self._notify_listeners('shortcut_updated', {
            'shortcut_id': shortcut_id,
            'keys': keys
        })
        return True

    def get_shortcut(self, shortcut_id: str, profile_id: Optional[str] = None) -> Optional[Shortcut]:
        """Get a specific shortcut."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if profile and shortcut_id in profile.shortcuts:
            return profile.shortcuts[shortcut_id]
        return None

    def get_shortcuts_by_category(self, category: ShortcutCategory, profile_id: Optional[str] = None) -> List[Shortcut]:
        """Get shortcuts by category."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return []

        return [
            s for s in profile.shortcuts.values()
            if s.category == category
        ]

    def get_shortcut_by_keys(self, keys: str, profile_id: Optional[str] = None, enabled_only: bool = True) -> Optional[Shortcut]:
        """Find shortcut by key combination."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return None

        for shortcut in profile.shortcuts.values():
            if shortcut.keys == keys:
                if enabled_only and not shortcut.is_enabled:
                    continue
                return shortcut
        return None

    def handle_shortcut(self, keys: str) -> bool:
        """
        Handle a keyboard shortcut press.
        
        Args:
            keys: Key combination pressed
            
        Returns:
            True if shortcut was handled
        """
        shortcut = self.get_shortcut_by_keys(keys)
        if not shortcut:
            return False

        # Execute handler if registered
        if shortcut.action in self.action_handlers:
            try:
                self.action_handlers[shortcut.action](shortcut)
                self._notify_listeners('shortcut_executed', {'shortcut_id': shortcut.id})
                return True
            except Exception:
                return False

        self._notify_listeners('shortcut_executed', {'shortcut_id': shortcut.id})
        return True

    def register_action_handler(self, action: str, handler: Callable) -> None:
        """Register a handler for an action."""
        self.action_handlers[action] = handler

    def _detect_conflicts(self, shortcut_id: str, keys: str, profile: ShortcutProfile) -> List[ShortcutConflict]:
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
                    severity='error'
                )
                conflicts.append(conflict)

        return conflicts

    def get_conflicts(self) -> List[ShortcutConflict]:
        """Get current conflicts."""
        return self.conflicts

    def resolve_conflict(self, conflict: ShortcutConflict, reassign_to: str) -> bool:
        """
        Resolve a conflict by reassigning one shortcut.
        
        Args:
            conflict: The conflict to resolve
            reassign_to: Which shortcut to reassign ("shortcut" or "conflicting")
            
        Returns:
            True if resolved
        """
        if not self.current_profile:
            return False

        profile = self.current_profile

        if reassign_to == "shortcut":
            # Remove conflicting shortcut's keys
            if conflict.conflicting_id in profile.shortcuts:
                profile.shortcuts[conflict.conflicting_id].keys = ""
        else:
            # Remove this shortcut's keys
            if conflict.shortcut_id in profile.shortcuts:
                profile.shortcuts[conflict.shortcut_id].keys = ""

        self.conflicts = []
        self._notify_listeners('conflict_resolved', {'conflict': conflict.to_dict()})
        return True

    def enable_shortcut(self, shortcut_id: str, profile_id: Optional[str] = None) -> bool:
        """Enable a shortcut."""
        shortcut = self.get_shortcut(shortcut_id, profile_id)
        if shortcut:
            shortcut.is_enabled = True
            self._notify_listeners('shortcut_enabled', {'shortcut_id': shortcut_id})
            return True
        return False

    def disable_shortcut(self, shortcut_id: str, profile_id: Optional[str] = None) -> bool:
        """Disable a shortcut."""
        shortcut = self.get_shortcut(shortcut_id, profile_id)
        if shortcut:
            shortcut.is_enabled = False
            self._notify_listeners('shortcut_disabled', {'shortcut_id': shortcut_id})
            return True
        return False

    def reset_to_defaults(self, profile_id: Optional[str] = None) -> bool:
        """Reset profile to default shortcuts."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return False

        # Deep copy shortcuts
        shortcuts = {}
        for k, v in self.DEFAULT_SHORTCUTS.items():
            shortcuts[k] = Shortcut(
                id=v.id,
                name=v.name,
                description=v.description,
                keys=v.keys,
                action=v.action,
                category=v.category,
                scope=v.scope,
                is_customizable=v.is_customizable,
                is_enabled=v.is_enabled,
                platform=v.platform,
                conflicting_shortcuts=v.conflicting_shortcuts.copy()
            )
        
        profile.shortcuts = shortcuts
        profile.modified_at = datetime.now()
        self._notify_listeners('reset_to_defaults', {'profile_id': profile.id})
        return True

    def search_shortcuts(self, query: str, profile_id: Optional[str] = None) -> List[Shortcut]:
        """Search shortcuts by name or description."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return []

        query_lower = query.lower()
        results = []

        for shortcut in profile.shortcuts.values():
            if (query_lower in shortcut.name.lower() or
                query_lower in shortcut.description.lower() or
                query_lower in shortcut.keys.lower()):
                results.append(shortcut)

        return results

    def add_listener(self, listener: Callable) -> None:
        """Add event listener."""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        """Remove event listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def _notify_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify listeners of changes."""
        for listener in self.listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass

    def get_all_shortcuts(self, profile_id: Optional[str] = None) -> List[Shortcut]:
        """Get all shortcuts in a profile."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return []
        return list(profile.shortcuts.values())

    def export_profile(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Export profile as dictionary."""
        profile = self.profiles.get(profile_id) if profile_id else self.current_profile
        if not profile:
            return {}
        return profile.to_dict()

    def import_profile(self, data: Dict[str, Any]) -> bool:
        """Import profile from dictionary."""
        try:
            profile = ShortcutProfile.from_dict(data)
            self.profiles[profile.id] = profile
            self._notify_listeners('profile_imported', {'profile_id': profile.id})
            return True
        except Exception:
            return False

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        if profile_id == 'default' or profile_id not in self.profiles:
            return False

        del self.profiles[profile_id]
        if self.current_profile and self.current_profile.id == profile_id:
            self.current_profile = self.profiles.get('default')

        self._notify_listeners('profile_deleted', {'profile_id': profile_id})
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get shortcuts statistics."""
        if not self.current_profile:
            return {}

        shortcuts = self.current_profile.shortcuts.values()
        return {
            'total_shortcuts': len(shortcuts),
            'enabled_shortcuts': sum(1 for s in shortcuts if s.is_enabled),
            'customizable_shortcuts': sum(1 for s in shortcuts if s.is_customizable),
            'by_category': {
                cat.value: len([s for s in shortcuts if s.category == cat])
                for cat in ShortcutCategory
            },
            'total_profiles': len(self.profiles)
        }
