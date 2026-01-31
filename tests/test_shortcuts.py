"""
Unit tests for Shortcuts Manager (Plan 19).

Tests for ShortcutsManager, Shortcut, ShortcutProfile, and conflict detection.
"""

import json
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from anki_template_designer.services.shortcuts_manager import (
    Shortcut,
    ShortcutCategory,
    ShortcutConflict,
    ShortcutProfile,
    ShortcutScope,
    ShortcutsManager,
    DEFAULT_SHORTCUTS,
    get_shortcuts_manager,
    init_shortcuts_manager,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def manager():
    """Create shortcuts manager."""
    return ShortcutsManager()


@pytest.fixture
def shortcut():
    """Create sample shortcut."""
    return Shortcut(
        id="test_shortcut",
        name="Test Shortcut",
        description="A test shortcut",
        keys="Ctrl+T",
        action="test_action",
        category=ShortcutCategory.EDIT,
        scope=ShortcutScope.GLOBAL,
        is_customizable=True,
        is_enabled=True
    )


# ============================================================================
# Shortcut Tests
# ============================================================================

class TestShortcut:
    """Tests for Shortcut dataclass."""
    
    def test_create_shortcut(self, shortcut):
        """Test creating shortcut."""
        assert shortcut.id == "test_shortcut"
        assert shortcut.name == "Test Shortcut"
        assert shortcut.keys == "Ctrl+T"
        assert shortcut.category == ShortcutCategory.EDIT
    
    def test_to_dict(self, shortcut):
        """Test converting to dictionary."""
        result = shortcut.to_dict()
        assert result["id"] == "test_shortcut"
        assert result["name"] == "Test Shortcut"
        assert result["keys"] == "Ctrl+T"
        assert result["category"] == "edit"
        assert result["isCustomizable"] is True
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "from_dict",
            "name": "From Dict",
            "keys": "Ctrl+D",
            "action": "action",
            "category": "view",
            "scope": "editor"
        }
        shortcut = Shortcut.from_dict(data)
        assert shortcut.id == "from_dict"
        assert shortcut.category == ShortcutCategory.VIEW
        assert shortcut.scope == ShortcutScope.EDITOR
    
    def test_copy(self, shortcut):
        """Test copying shortcut."""
        copy = shortcut.copy()
        assert copy.id == shortcut.id
        assert copy.keys == shortcut.keys
        assert copy is not shortcut
    
    def test_default_values(self):
        """Test default values."""
        shortcut = Shortcut()
        assert shortcut.id == ""
        assert shortcut.category == ShortcutCategory.CUSTOM
        assert shortcut.scope == ShortcutScope.GLOBAL
        assert shortcut.is_customizable is True
        assert shortcut.is_enabled is True


# ============================================================================
# ShortcutProfile Tests
# ============================================================================

class TestShortcutProfile:
    """Tests for ShortcutProfile dataclass."""
    
    def test_create_profile(self):
        """Test creating profile."""
        profile = ShortcutProfile(
            id="test_profile",
            name="Test Profile",
            description="A test profile"
        )
        assert profile.id == "test_profile"
        assert profile.name == "Test Profile"
        assert profile.is_default is False
    
    def test_to_dict(self, shortcut):
        """Test converting to dictionary."""
        profile = ShortcutProfile(
            id="test",
            name="Test",
            shortcuts={"test": shortcut}
        )
        result = profile.to_dict()
        assert result["id"] == "test"
        assert "shortcuts" in result
        assert "test" in result["shortcuts"]
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "imported",
            "name": "Imported",
            "description": "Imported profile",
            "shortcuts": {},
            "isDefault": True,
            "createdAt": datetime.now().isoformat(),
            "modifiedAt": datetime.now().isoformat()
        }
        profile = ShortcutProfile.from_dict(data)
        assert profile.id == "imported"
        assert profile.is_default is True


# ============================================================================
# ShortcutConflict Tests
# ============================================================================

class TestShortcutConflict:
    """Tests for ShortcutConflict dataclass."""
    
    def test_create_conflict(self):
        """Test creating conflict."""
        conflict = ShortcutConflict(
            shortcut_id="s1",
            shortcut_name="Shortcut 1",
            conflicting_id="s2",
            conflicting_name="Shortcut 2",
            keys="Ctrl+S",
            severity="error"
        )
        assert conflict.shortcut_id == "s1"
        assert conflict.keys == "Ctrl+S"
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        conflict = ShortcutConflict(
            shortcut_id="s1",
            shortcut_name="S1",
            conflicting_id="s2",
            conflicting_name="S2",
            keys="Ctrl+X"
        )
        result = conflict.to_dict()
        assert result["shortcutId"] == "s1"
        assert result["keys"] == "Ctrl+X"


# ============================================================================
# ShortcutsManager Basic Tests
# ============================================================================

class TestShortcutsManagerBasics:
    """Tests for ShortcutsManager basics."""
    
    def test_create_manager(self, manager):
        """Test creating manager."""
        assert manager._current_profile is not None
        assert manager._current_profile.id == "default"
    
    def test_default_shortcuts_loaded(self, manager):
        """Test default shortcuts are loaded."""
        shortcuts = manager.get_all_shortcuts()
        assert len(shortcuts) > 0
        
        # Check common shortcuts exist
        ids = [s["id"] for s in shortcuts]
        assert "undo" in ids
        assert "redo" in ids
        assert "save" in ids
        assert "copy" in ids
        assert "paste" in ids
    
    def test_get_shortcut(self, manager):
        """Test getting specific shortcut."""
        shortcut = manager.get_shortcut("undo")
        assert shortcut is not None
        assert shortcut["keys"] == "Ctrl+Z"
    
    def test_get_shortcut_nonexistent(self, manager):
        """Test getting nonexistent shortcut."""
        shortcut = manager.get_shortcut("nonexistent")
        assert shortcut is None


# ============================================================================
# Shortcut Updates Tests
# ============================================================================

class TestShortcutUpdates:
    """Tests for updating shortcuts."""
    
    def test_update_shortcut(self, manager):
        """Test updating shortcut keys."""
        result = manager.update_shortcut("zoom_in", "Ctrl+Shift+Plus")
        assert result is True
        
        shortcut = manager.get_shortcut("zoom_in")
        assert shortcut["keys"] == "Ctrl+Shift+Plus"
    
    def test_update_non_customizable_shortcut(self, manager):
        """Test updating non-customizable shortcut fails."""
        result = manager.update_shortcut("delete", "Ctrl+Backspace")
        assert result is False
    
    def test_update_with_empty_keys(self, manager):
        """Test updating with empty keys fails."""
        result = manager.update_shortcut("undo", "")
        assert result is False
    
    def test_update_nonexistent_shortcut(self, manager):
        """Test updating nonexistent shortcut fails."""
        result = manager.update_shortcut("nonexistent", "Ctrl+X")
        assert result is False


# ============================================================================
# Conflict Detection Tests
# ============================================================================

class TestConflictDetection:
    """Tests for conflict detection."""
    
    def test_detect_conflict(self, manager):
        """Test conflict detection."""
        # Try to set zoom_in to same keys as undo
        result = manager.update_shortcut("zoom_in", "Ctrl+Z")
        assert result is False
        
        conflicts = manager.get_conflicts()
        assert len(conflicts) > 0
    
    def test_resolve_conflict_keep_shortcut(self, manager):
        """Test resolving conflict by keeping first shortcut."""
        # Create conflict
        manager.update_shortcut("zoom_in", "Ctrl+Z")
        
        # Resolve - this will clear zoom_in's keys since we keep undo
        result = manager.resolve_conflict("zoom_in", "undo", keep="conflicting")
        assert result is True
        
        # zoom_in should have no keys
        shortcut = manager.get_shortcut("zoom_in")
        assert shortcut["keys"] == ""


# ============================================================================
# Profile Management Tests
# ============================================================================

class TestProfileManagement:
    """Tests for profile management."""
    
    def test_create_profile(self, manager):
        """Test creating profile."""
        profile_id = manager.create_profile("Custom", "Custom shortcuts")
        assert profile_id == "custom"
        
        profiles = manager.get_profiles()
        assert len(profiles) == 2
    
    def test_switch_profile(self, manager):
        """Test switching profile."""
        manager.create_profile("Custom")
        result = manager.switch_profile("custom")
        assert result is True
        
        current = manager.get_current_profile()
        assert current["id"] == "custom"
    
    def test_switch_to_nonexistent_profile(self, manager):
        """Test switching to nonexistent profile fails."""
        result = manager.switch_profile("nonexistent")
        assert result is False
    
    def test_delete_profile(self, manager):
        """Test deleting profile."""
        manager.create_profile("ToDelete")
        result = manager.delete_profile("todelete")
        assert result is True
        
        profiles = manager.get_profiles()
        ids = [p["id"] for p in profiles]
        assert "todelete" not in ids
    
    def test_cannot_delete_default_profile(self, manager):
        """Test cannot delete default profile."""
        result = manager.delete_profile("default")
        assert result is False
    
    def test_export_profile(self, manager):
        """Test exporting profile."""
        data = manager.export_profile()
        assert data["id"] == "default"
        assert "shortcuts" in data
    
    def test_import_profile(self, manager):
        """Test importing profile."""
        data = {
            "id": "imported",
            "name": "Imported",
            "description": "Test",
            "shortcuts": {},
            "isDefault": False,
            "createdAt": datetime.now().isoformat(),
            "modifiedAt": datetime.now().isoformat()
        }
        result = manager.import_profile(data)
        assert result is True
        
        profiles = manager.get_profiles()
        ids = [p["id"] for p in profiles]
        assert "imported" in ids


# ============================================================================
# Shortcut Handling Tests
# ============================================================================

class TestShortcutHandling:
    """Tests for shortcut execution handling."""
    
    def test_handle_shortcut(self, manager):
        """Test handling shortcut press."""
        result = manager.handle_shortcut("Ctrl+Z")
        assert result is True
    
    def test_handle_unknown_shortcut(self, manager):
        """Test handling unknown shortcut."""
        result = manager.handle_shortcut("Ctrl+Shift+Alt+X")
        assert result is False
    
    def test_register_action_handler(self, manager):
        """Test registering action handler."""
        handler = MagicMock()
        manager.register_action_handler("undo", handler)
        
        manager.handle_shortcut("Ctrl+Z")
        handler.assert_called_once()
    
    def test_unregister_action_handler(self, manager):
        """Test unregistering action handler."""
        handler = MagicMock()
        manager.register_action_handler("test", handler)
        
        result = manager.unregister_action_handler("test")
        assert result is True
        
        result = manager.unregister_action_handler("nonexistent")
        assert result is False


# ============================================================================
# Enable/Disable Tests
# ============================================================================

class TestEnableDisable:
    """Tests for enabling/disabling shortcuts."""
    
    def test_disable_shortcut(self, manager):
        """Test disabling shortcut."""
        result = manager.disable_shortcut("undo")
        assert result is True
        
        shortcut = manager.get_shortcut("undo")
        assert shortcut["isEnabled"] is False
    
    def test_enable_shortcut(self, manager):
        """Test enabling shortcut."""
        manager.disable_shortcut("undo")
        result = manager.enable_shortcut("undo")
        assert result is True
        
        shortcut = manager.get_shortcut("undo")
        assert shortcut["isEnabled"] is True
    
    def test_disabled_shortcut_not_found_by_keys(self, manager):
        """Test disabled shortcut not found by keys."""
        manager.disable_shortcut("undo")
        
        shortcut = manager.get_shortcut_by_keys("Ctrl+Z", enabled_only=True)
        assert shortcut is None


# ============================================================================
# Search and Filter Tests
# ============================================================================

class TestSearchFilter:
    """Tests for search and filter operations."""
    
    def test_search_shortcuts_by_name(self, manager):
        """Test searching shortcuts by name."""
        results = manager.search_shortcuts("Undo")
        assert len(results) >= 1
    
    def test_search_shortcuts_by_keys(self, manager):
        """Test searching shortcuts by keys."""
        results = manager.search_shortcuts("Ctrl+Z")
        assert len(results) >= 1
    
    def test_search_no_results(self, manager):
        """Test search with no results."""
        results = manager.search_shortcuts("xyznonexistent")
        assert len(results) == 0
    
    def test_get_shortcuts_by_category(self, manager):
        """Test getting shortcuts by category."""
        results = manager.get_shortcuts_by_category("edit")
        assert len(results) > 0
        
        for shortcut in results:
            assert shortcut["category"] == "edit"
    
    def test_get_shortcuts_by_invalid_category(self, manager):
        """Test getting shortcuts by invalid category."""
        results = manager.get_shortcuts_by_category("invalid")
        assert results == []


# ============================================================================
# Reset and Statistics Tests
# ============================================================================

class TestResetStatistics:
    """Tests for reset and statistics."""
    
    def test_reset_to_defaults(self, manager):
        """Test resetting to defaults."""
        # Change a shortcut
        manager.update_shortcut("zoom_in", "Ctrl+Shift+Plus")
        
        # Reset
        result = manager.reset_to_defaults()
        assert result is True
        
        # Check it's back to default
        shortcut = manager.get_shortcut("zoom_in")
        assert shortcut["keys"] == "Ctrl+Plus"
    
    def test_get_statistics(self, manager):
        """Test getting statistics."""
        stats = manager.get_statistics()
        
        assert "totalShortcuts" in stats
        assert "enabledShortcuts" in stats
        assert "customizableShortcuts" in stats
        assert "byCategory" in stats
        assert "totalProfiles" in stats


# ============================================================================
# Custom Shortcut Tests
# ============================================================================

class TestCustomShortcuts:
    """Tests for custom shortcuts."""
    
    def test_add_custom_shortcut(self, manager):
        """Test adding custom shortcut."""
        result = manager.add_custom_shortcut(
            shortcut_id="custom_1",
            name="Custom Action",
            keys="Ctrl+Shift+K",
            action="custom_action",
            description="A custom shortcut"
        )
        assert result is True
        
        shortcut = manager.get_shortcut("custom_1")
        assert shortcut is not None
        assert shortcut["keys"] == "Ctrl+Shift+K"
    
    def test_add_duplicate_custom_shortcut(self, manager):
        """Test adding duplicate custom shortcut fails."""
        manager.add_custom_shortcut("custom_1", "Custom", "Ctrl+K", "action")
        result = manager.add_custom_shortcut("custom_1", "Custom 2", "Ctrl+L", "action2")
        assert result is False
    
    def test_remove_custom_shortcut(self, manager):
        """Test removing custom shortcut."""
        manager.add_custom_shortcut("custom_1", "Custom", "Ctrl+K", "action")
        
        result = manager.remove_custom_shortcut("custom_1")
        assert result is True
        
        shortcut = manager.get_shortcut("custom_1")
        assert shortcut is None
    
    def test_cannot_remove_builtin_shortcut(self, manager):
        """Test cannot remove built-in shortcut."""
        result = manager.remove_custom_shortcut("undo")
        assert result is False


# ============================================================================
# Event Listener Tests
# ============================================================================

class TestEventListeners:
    """Tests for event listeners."""
    
    def test_add_listener(self, manager):
        """Test adding listener."""
        listener = MagicMock()
        manager.add_listener(listener)
        
        manager.update_shortcut("zoom_in", "Ctrl+Shift+Plus")
        listener.assert_called()
    
    def test_remove_listener(self, manager):
        """Test removing listener."""
        listener = MagicMock()
        manager.add_listener(listener)
        manager.remove_listener(listener)
        
        manager.update_shortcut("zoom_in", "Ctrl+Shift+Plus")
        listener.assert_not_called()


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety:
    """Tests for thread safety."""
    
    def test_concurrent_shortcut_access(self, manager):
        """Test concurrent shortcut access."""
        errors = []
        
        def access_shortcuts():
            try:
                for _ in range(10):
                    manager.get_all_shortcuts()
                    manager.get_shortcut("undo")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=access_shortcuts)
            for _ in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


# ============================================================================
# Global Instance Tests
# ============================================================================

class TestGlobalInstance:
    """Tests for global instance functions."""
    
    def test_init_and_get_shortcuts_manager(self):
        """Test initializing and getting manager."""
        manager = init_shortcuts_manager("Test Profile")
        assert manager is not None
        
        retrieved = get_shortcuts_manager()
        assert retrieved is manager


# ============================================================================
# Default Shortcuts Tests
# ============================================================================

class TestDefaultShortcuts:
    """Tests for default shortcuts."""
    
    def test_default_shortcuts_exist(self):
        """Test default shortcuts are defined."""
        assert len(DEFAULT_SHORTCUTS) > 0
        assert "undo" in DEFAULT_SHORTCUTS
        assert "redo" in DEFAULT_SHORTCUTS
        assert "save" in DEFAULT_SHORTCUTS
    
    def test_default_shortcut_categories(self):
        """Test default shortcuts have proper categories."""
        edit_shortcuts = [s for s in DEFAULT_SHORTCUTS.values() 
                        if s.category == ShortcutCategory.EDIT]
        assert len(edit_shortcuts) > 0
        
        file_shortcuts = [s for s in DEFAULT_SHORTCUTS.values() 
                         if s.category == ShortcutCategory.FILE]
        assert len(file_shortcuts) > 0
