"""
Issue #50: Keyboard Shortcuts Manager - Tests

Comprehensive test suite for shortcuts management with 35+ tests covering:
- Shortcut creation and management
- Profile management
- Conflict detection
- Keyboard handling
- Search and filtering
- State persistence
"""

import unittest
from datetime import datetime
from services.shortcuts_manager import (
    ShortcutsManager, Shortcut, ShortcutProfile, ShortcutConflict,
    ShortcutScope, ShortcutCategory
)


class TestShortcut(unittest.TestCase):
    """Tests for Shortcut model."""

    def test_shortcut_creation(self):
        """Test creating a shortcut."""
        shortcut = Shortcut(
            id='test',
            name='Test',
            keys='Ctrl+T',
            action='test_action'
        )
        self.assertEqual(shortcut.id, 'test')
        self.assertEqual(shortcut.keys, 'Ctrl+T')
        self.assertTrue(shortcut.is_enabled)

    def test_shortcut_serialization(self):
        """Test shortcut to_dict."""
        shortcut = Shortcut(
            id='undo',
            name='Undo',
            keys='Ctrl+Z',
            category=ShortcutCategory.EDIT
        )
        data = shortcut.to_dict()
        self.assertEqual(data['name'], 'Undo')
        self.assertEqual(data['category'], 'edit')

    def test_shortcut_deserialization(self):
        """Test creating shortcut from dict."""
        data = {
            'id': 'save',
            'name': 'Save',
            'keys': 'Ctrl+S',
            'action': 'save',
            'category': 'file'
        }
        shortcut = Shortcut.from_dict(data)
        self.assertEqual(shortcut.id, 'save')
        self.assertEqual(shortcut.keys, 'Ctrl+S')

    def test_customizable_flag(self):
        """Test customizable flag."""
        custom = Shortcut(id='c1', name='Custom', is_customizable=True)
        non_custom = Shortcut(id='c2', name='Fixed', is_customizable=False)
        
        self.assertTrue(custom.is_customizable)
        self.assertFalse(non_custom.is_customizable)


class TestShortcutProfile(unittest.TestCase):
    """Tests for ShortcutProfile model."""

    def test_profile_creation(self):
        """Test creating a profile."""
        profile = ShortcutProfile(
            name='Test Profile',
            description='A test profile'
        )
        self.assertEqual(profile.name, 'Test Profile')
        self.assertEqual(len(profile.shortcuts), 0)

    def test_profile_serialization(self):
        """Test profile to_dict."""
        profile = ShortcutProfile(name='Test')
        profile.shortcuts['undo'] = Shortcut(id='undo', name='Undo')
        
        data = profile.to_dict()
        self.assertEqual(data['name'], 'Test')
        self.assertIn('undo', data['shortcuts'])

    def test_profile_deserialization(self):
        """Test creating profile from dict."""
        data = {
            'id': 'test',
            'name': 'Test Profile',
            'shortcuts': {
                'undo': {'id': 'undo', 'name': 'Undo', 'keys': 'Ctrl+Z'}
            },
            'created_at': datetime.now().isoformat()
        }
        profile = ShortcutProfile.from_dict(data)
        self.assertEqual(profile.name, 'Test Profile')
        self.assertIn('undo', profile.shortcuts)


class TestShortcutsManagerBasics(unittest.TestCase):
    """Tests for basic shortcuts manager functionality."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_manager_initialization(self):
        """Test manager creates default profile."""
        self.assertIsNotNone(self.manager.current_profile)
        self.assertEqual(self.manager.current_profile.id, 'default')
        self.assertGreater(len(self.manager.current_profile.shortcuts), 0)

    def test_default_shortcuts_exist(self):
        """Test default shortcuts are created."""
        undo = self.manager.get_shortcut('undo')
        self.assertIsNotNone(undo)
        self.assertEqual(undo.name, 'Undo')

    def test_get_current_profile(self):
        """Test getting current profile."""
        profile = self.manager.get_current_profile()
        self.assertIsNotNone(profile)
        self.assertTrue(profile.is_default)

    def test_all_default_shortcuts(self):
        """Test all default shortcuts."""
        defaults = ['undo', 'redo', 'save', 'copy', 'paste', 'delete', 'help']
        for shortcut_id in defaults:
            shortcut = self.manager.get_shortcut(shortcut_id)
            self.assertIsNotNone(shortcut, f"{shortcut_id} should exist")

    def test_get_all_shortcuts(self):
        """Test getting all shortcuts."""
        shortcuts = self.manager.get_all_shortcuts()
        self.assertGreater(len(shortcuts), 0)

    def test_enable_disable_shortcut(self):
        """Test enabling/disabling shortcuts."""
        self.assertTrue(self.manager.enable_shortcut('undo'))
        shortcut = self.manager.get_shortcut('undo')
        self.assertTrue(shortcut.is_enabled)

        self.assertTrue(self.manager.disable_shortcut('undo'))
        shortcut = self.manager.get_shortcut('undo')
        self.assertFalse(shortcut.is_enabled)


class TestProfileManagement(unittest.TestCase):
    """Tests for profile management."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_create_profile(self):
        """Test creating a new profile."""
        profile_id = self.manager.create_profile('Gaming')
        self.assertIn(profile_id, self.manager.profiles)

    def test_create_multiple_profiles(self):
        """Test creating multiple profiles."""
        self.manager.create_profile('Profile 1')
        self.manager.create_profile('Profile 2')
        
        profiles = self.manager.get_profiles()
        self.assertGreaterEqual(len(profiles), 3)  # default + 2 new

    def test_switch_profile(self):
        """Test switching between profiles."""
        profile_id = self.manager.create_profile('Test Profile')
        current = self.manager.current_profile.id
        
        self.manager.switch_profile(profile_id)
        self.assertEqual(self.manager.current_profile.id, profile_id)
        
        # Switch back
        self.manager.switch_profile(current)
        self.assertEqual(self.manager.current_profile.id, current)

    def test_switch_nonexistent_profile(self):
        """Test switching to non-existent profile."""
        result = self.manager.switch_profile('nonexistent')
        self.assertFalse(result)

    def test_delete_profile(self):
        """Test deleting a profile."""
        profile_id = self.manager.create_profile('To Delete')
        self.manager.delete_profile(profile_id)
        
        self.assertNotIn(profile_id, self.manager.profiles)

    def test_cannot_delete_default(self):
        """Test cannot delete default profile."""
        result = self.manager.delete_profile('default')
        self.assertFalse(result)
        self.assertIn('default', self.manager.profiles)

    def test_export_profile(self):
        """Test exporting profile."""
        data = self.manager.export_profile()
        self.assertIn('name', data)
        self.assertIn('shortcuts', data)

    def test_import_profile(self):
        """Test importing profile."""
        # Export current
        data = self.manager.export_profile()
        
        # Change current
        self.manager.create_profile('New')
        
        # Import exported
        result = self.manager.import_profile(data)
        self.assertTrue(result)


class TestShortcutUpdating(unittest.TestCase):
    """Tests for updating shortcuts."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_update_shortcut(self):
        """Test updating a shortcut."""
        result = self.manager.update_shortcut('undo', 'Ctrl+Alt+Z')
        self.assertTrue(result)
        
        shortcut = self.manager.get_shortcut('undo')
        self.assertEqual(shortcut.keys, 'Ctrl+Alt+Z')

    def test_cannot_update_non_customizable(self):
        """Test cannot update non-customizable shortcut."""
        result = self.manager.update_shortcut('delete', 'NewKey')
        self.assertFalse(result)

    def test_conflict_prevents_update(self):
        """Test conflicts prevent updates."""
        # Try to set undo to same keys as redo
        self.manager.update_shortcut('redo', 'Ctrl+Y')
        result = self.manager.update_shortcut('undo', 'Ctrl+Y')
        
        # Should fail due to conflict
        self.assertFalse(result)
        self.assertGreater(len(self.manager.get_conflicts()), 0)

    def test_reset_to_defaults(self):
        """Test resetting to defaults."""
        self.manager.update_shortcut('undo', 'Ctrl+Alt+Z')
        self.manager.reset_to_defaults()
        
        shortcut = self.manager.get_shortcut('undo')
        self.assertEqual(shortcut.keys, 'Ctrl+Z')


class TestConflictDetection(unittest.TestCase):
    """Tests for conflict detection and resolution."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_detect_conflict(self):
        """Test detecting conflicting shortcuts."""
        # Change undo to conflict with redo
        original_redo = self.manager.get_shortcut('redo').keys
        
        result = self.manager.update_shortcut('undo', original_redo)
        self.assertFalse(result)
        
        conflicts = self.manager.get_conflicts()
        self.assertGreater(len(conflicts), 0)

    def test_conflict_details(self):
        """Test conflict contains correct details."""
        original_redo = self.manager.get_shortcut('redo').keys
        self.manager.update_shortcut('undo', original_redo)
        
        conflicts = self.manager.get_conflicts()
        self.assertTrue(any(c.shortcut_id == 'undo' for c in conflicts))

    def test_resolve_conflict(self):
        """Test resolving a conflict."""
        original_redo = self.manager.get_shortcut('redo').keys
        self.manager.update_shortcut('undo', original_redo)
        
        conflicts = self.manager.get_conflicts()
        if conflicts:
            result = self.manager.resolve_conflict(conflicts[0], 'shortcut')
            self.assertTrue(result)


class TestShortcutLookup(unittest.TestCase):
    """Tests for finding shortcuts."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_get_by_keys(self):
        """Test finding shortcut by key combination."""
        shortcut = self.manager.get_shortcut_by_keys('Ctrl+Z')
        self.assertIsNotNone(shortcut)
        self.assertEqual(shortcut.id, 'undo')

    def test_get_by_keys_nonexistent(self):
        """Test finding non-existent key combination."""
        shortcut = self.manager.get_shortcut_by_keys('Ctrl+Shift+Alt+Q')
        self.assertIsNone(shortcut)

    def test_get_by_category(self):
        """Test getting shortcuts by category."""
        edit_shortcuts = self.manager.get_shortcuts_by_category(ShortcutCategory.EDIT)
        self.assertGreater(len(edit_shortcuts), 0)
        self.assertTrue(all(s.category == ShortcutCategory.EDIT for s in edit_shortcuts))

    def test_search_shortcuts(self):
        """Test searching shortcuts."""
        results = self.manager.search_shortcuts('undo')
        self.assertGreater(len(results), 0)
        self.assertTrue(any(r.id == 'undo' for r in results))

    def test_search_by_description(self):
        """Test searching by description."""
        results = self.manager.search_shortcuts('undo')
        self.assertGreater(len(results), 0)

    def test_search_by_keys(self):
        """Test searching by key combination."""
        results = self.manager.search_shortcuts('Ctrl+Z')
        self.assertGreater(len(results), 0)


class TestEventHandling(unittest.TestCase):
    """Tests for shortcut execution and event handling."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()
        self.action_called = False

    def test_register_handler(self):
        """Test registering action handler."""
        def handler(shortcut):
            self.action_called = True

        self.manager.register_action_handler('test_action', handler)
        self.assertIn('test_action', self.manager.action_handlers)

    def test_handle_shortcut(self):
        """Test handling a shortcut."""
        def handler(shortcut):
            self.action_called = True

        self.manager.register_action_handler('undo', handler)
        result = self.manager.handle_shortcut('Ctrl+Z')
        
        self.assertTrue(result)
        self.assertTrue(self.action_called)

    def test_handle_unknown_shortcut(self):
        """Test handling unknown shortcut."""
        result = self.manager.handle_shortcut('Ctrl+Shift+Alt+Q')
        self.assertFalse(result)


class TestListeners(unittest.TestCase):
    """Tests for event listeners."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()
        self.events = []

    def test_add_listener(self):
        """Test adding listener."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        self.assertIn(listener, self.manager.listeners)

    def test_listener_on_update(self):
        """Test listener receives update event."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        self.manager.update_shortcut('undo', 'Ctrl+Alt+Z')
        
        self.assertIn('shortcut_updated', self.events)

    def test_listener_on_profile_create(self):
        """Test listener receives profile creation event."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        self.manager.create_profile('Test')
        
        self.assertIn('profile_created', self.events)

    def test_remove_listener(self):
        """Test removing listener."""
        def listener(event_type, data):
            pass

        self.manager.add_listener(listener)
        self.manager.remove_listener(listener)
        self.assertNotIn(listener, self.manager.listeners)


class TestStatistics(unittest.TestCase):
    """Tests for statistics."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_get_statistics(self):
        """Test getting statistics."""
        stats = self.manager.get_statistics()
        self.assertIn('total_shortcuts', stats)
        self.assertIn('enabled_shortcuts', stats)
        self.assertGreater(stats['total_shortcuts'], 0)

    def test_statistics_after_disable(self):
        """Test statistics update after disabling."""
        before = self.manager.get_statistics()['enabled_shortcuts']
        self.manager.disable_shortcut('undo')
        after = self.manager.get_statistics()['enabled_shortcuts']
        
        self.assertEqual(before - 1, after)

    def test_statistics_by_category(self):
        """Test statistics by category."""
        stats = self.manager.get_statistics()
        self.assertIn('by_category', stats)
        self.assertIn('edit', stats['by_category'])


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ShortcutsManager()

    def test_empty_key_binding(self):
        """Test cannot set empty key binding."""
        result = self.manager.update_shortcut('undo', '')
        self.assertFalse(result)  # Should fail with empty keys
        
        shortcut = self.manager.get_shortcut('undo')
        self.assertEqual(shortcut.keys, 'Ctrl+Z')  # Should remain unchanged

    def test_special_characters_in_keys(self):
        """Test special characters in key binding."""
        result = self.manager.update_shortcut('undo', 'Ctrl+Shift+@')
        self.assertTrue(result)

    def test_multiple_profiles_independent(self):
        """Test shortcuts in profiles are independent."""
        profile_id = self.manager.create_profile('Test')
        
        # Update in default
        self.manager.update_shortcut('undo', 'Ctrl+Alt+Z')
        
        # Switch and check
        self.manager.switch_profile(profile_id)
        shortcut = self.manager.get_shortcut('undo')
        self.assertEqual(shortcut.keys, 'Ctrl+Z')  # Still default


if __name__ == '__main__':
    unittest.main()
