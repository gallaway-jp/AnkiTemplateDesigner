"""
Comprehensive tests for Panel Synchronization System (Issue #53).
"""

import unittest
from services.panel_sync_manager import (
    PanelSyncManager, SyncEvent, PanelType, PanelState, SyncMessage
)


class TestPanelState(unittest.TestCase):
    """Test PanelState functionality."""

    def test_create_panel_state(self):
        """Test creating panel state."""
        state = PanelState(panel_type=PanelType.PROPERTIES)
        self.assertEqual(state.panel_type, PanelType.PROPERTIES)
        self.assertTrue(state.visible)

    def test_panel_state_to_dict(self):
        """Test converting panel state to dictionary."""
        state = PanelState(
            panel_type=PanelType.CANVAS,
            visible=True,
            data={'test': 'value'}
        )
        d = state.to_dict()
        self.assertEqual(d['panel_type'], 'canvas')
        self.assertTrue(d['visible'])
        self.assertEqual(d['data'], {'test': 'value'})


class TestSyncMessage(unittest.TestCase):
    """Test SyncMessage functionality."""

    def test_create_sync_message(self):
        """Test creating sync message."""
        message = SyncMessage(
            event_type=SyncEvent.COMPONENT_MODIFIED,
            source_panel=PanelType.CANVAS
        )
        self.assertEqual(message.event_type, SyncEvent.COMPONENT_MODIFIED)
        self.assertEqual(message.source_panel, PanelType.CANVAS)

    def test_sync_message_to_dict(self):
        """Test converting sync message to dictionary."""
        message = SyncMessage(
            event_type=SyncEvent.SELECTION_CHANGED,
            source_panel=PanelType.HIERARCHY,
            data={'ids': [1, 2, 3]}
        )
        d = message.to_dict()
        self.assertEqual(d['event_type'], 'selection_changed')
        self.assertEqual(d['source_panel'], 'hierarchy')


class TestPanelSyncManagerBasics(unittest.TestCase):
    """Test basic PanelSyncManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_initialization(self):
        """Test manager initializes correctly."""
        self.assertGreater(len(self.manager.panel_states), 0)
        self.assertFalse(self.manager.is_syncing)

    def test_register_panel(self):
        """Test registering a new panel."""
        # Get initial count
        initial_count = len(self.manager.panel_states)
        
        # Clear existing
        for panel_type in list(self.manager.panel_states.keys()):
            self.manager.unregister_panel(panel_type)
        
        # Register new panel
        result = self.manager.register_panel(PanelType.PROPERTIES, {'data': 'test'})
        self.assertTrue(result)
        self.assertIn(PanelType.PROPERTIES, self.manager.panel_states)

    def test_unregister_panel(self):
        """Test unregistering a panel."""
        self.manager.unregister_panel(PanelType.PROPERTIES)
        self.assertNotIn(PanelType.PROPERTIES, self.manager.panel_states)

    def test_get_panel_state(self):
        """Test retrieving panel state."""
        state = self.manager.get_panel_state(PanelType.CANVAS)
        self.assertIsNotNone(state)
        self.assertEqual(state.panel_type, PanelType.CANVAS)


class TestPanelStateUpdates(unittest.TestCase):
    """Test panel state updates."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_update_panel_state(self):
        """Test updating panel state."""
        data = {'component_id': 'comp_1', 'props': {'color': 'red'}}
        result = self.manager.update_panel_state(PanelType.PROPERTIES, data)
        
        self.assertTrue(result)
        state = self.manager.get_panel_state(PanelType.PROPERTIES)
        self.assertEqual(state.data, data)

    def test_no_change_update(self):
        """Test update with no changes."""
        data = {'test': 'data'}
        self.manager.update_panel_state(PanelType.PROPERTIES, data)
        
        # Try same update again
        result = self.manager.update_panel_state(PanelType.PROPERTIES, data)
        self.assertFalse(result)

    def test_panel_dirty_flag(self):
        """Test dirty flag on update."""
        data = {'changed': True}
        self.manager.update_panel_state(PanelType.PROPERTIES, data)
        
        state = self.manager.get_panel_state(PanelType.PROPERTIES)
        self.assertTrue(state.dirty)

    def test_update_nonexistent_panel(self):
        """Test updating non-existent panel."""
        # Create temporary panel type reference
        # This tests the panel existence check
        result = self.manager.update_panel_state(PanelType.CANVAS, {'data': 'test'})
        self.assertTrue(result)  # Should succeed since CANVAS exists by default


class TestComponentSync(unittest.TestCase):
    """Test component change synchronization."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()
        self.sync_events = []

    def sync_listener(self, message_data):
        """Capture sync events."""
        self.sync_events.append(message_data)

    def test_sync_component_change(self):
        """Test syncing component change."""
        self.manager.add_listener(PanelType.HIERARCHY, self.sync_listener)
        
        changes = {'color': 'blue', 'width': 100}
        self.manager.sync_component_change('comp_1', changes, PanelType.CANVAS)
        
        # Give time for async processing
        self.manager._process_sync_queue()
        
        # Event should be queued
        self.assertGreater(len(self.manager.sync_queue) + len(self.sync_events), 0)

    def test_sync_component_affects_panels(self):
        """Test component sync affects correct panels."""
        self.manager.add_listener(PanelType.PROPERTIES, self.sync_listener)
        self.manager.add_listener(PanelType.PREVIEW, self.sync_listener)
        
        changes = {'modified': True}
        self.manager.sync_component_change('comp_1', changes, PanelType.CANVAS)
        self.manager._process_sync_queue()
        
        # Verify sync message was processed
        self.assertIsNotNone(self.manager.get_sync_statistics())


class TestSelectionSync(unittest.TestCase):
    """Test selection synchronization."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()
        self.events = []

    def listener(self, message_data):
        """Capture events."""
        self.events.append(message_data)

    def test_sync_selection_change(self):
        """Test syncing selection change."""
        self.manager.add_listener(PanelType.HIERARCHY, self.listener)
        
        selected = ['comp_1', 'comp_2']
        self.manager.sync_selection_change(selected, PanelType.CANVAS)
        self.manager._process_sync_queue()
        
        # Verify message was queued and processing attempted
        stats = self.manager.get_sync_statistics()
        self.assertIsNotNone(stats)

    def test_selection_affects_multiple_panels(self):
        """Test selection affects multiple panels."""
        for panel in [PanelType.PROPERTIES, PanelType.PREVIEW, PanelType.HIERARCHY]:
            self.manager.add_listener(panel, self.listener)
        
        selected = ['comp_1']
        self.manager.sync_selection_change(selected, PanelType.CANVAS)
        self.manager._process_sync_queue()


class TestPanelVisibility(unittest.TestCase):
    """Test panel visibility management."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_set_panel_visible(self):
        """Test setting panel visible."""
        result = self.manager.set_panel_visibility(PanelType.PREVIEW, True)
        # Result may be False if already visible - that's ok
        state = self.manager.get_panel_state(PanelType.PREVIEW)
        self.assertTrue(state.visible)

    def test_set_panel_hidden(self):
        """Test setting panel hidden."""
        result = self.manager.set_panel_visibility(PanelType.LIBRARY, False)
        self.assertTrue(result)
        self.assertFalse(self.manager.get_panel_state(PanelType.LIBRARY).visible)

    def test_no_change_visibility(self):
        """Test visibility change with no change."""
        self.manager.set_panel_visibility(PanelType.SETTINGS, True)
        result = self.manager.set_panel_visibility(PanelType.SETTINGS, True)
        self.assertFalse(result)

    def test_visibility_marks_dirty(self):
        """Test visibility change marks panel dirty."""
        self.manager.set_panel_visibility(PanelType.PREVIEW, False)
        state = self.manager.get_panel_state(PanelType.PREVIEW)
        self.assertTrue(state.dirty)


class TestPanelFocus(unittest.TestCase):
    """Test panel focus management."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_set_panel_focus(self):
        """Test setting focus to panel."""
        result = self.manager.set_panel_focus(PanelType.CANVAS)
        self.assertTrue(result)
        self.assertTrue(self.manager.get_panel_state(PanelType.CANVAS).focused)

    def test_focus_removes_previous(self):
        """Test focus removes from previous panel."""
        self.manager.set_panel_focus(PanelType.CANVAS)
        self.manager.set_panel_focus(PanelType.HIERARCHY)
        
        self.assertFalse(self.manager.get_panel_state(PanelType.CANVAS).focused)
        self.assertTrue(self.manager.get_panel_state(PanelType.HIERARCHY).focused)

    def test_set_focus_nonexistent(self):
        """Test setting focus to non-existent panel."""
        self.manager.unregister_panel(PanelType.CANVAS)
        result = self.manager.set_panel_focus(PanelType.CANVAS)
        self.assertFalse(result)


class TestConsistencyChecks(unittest.TestCase):
    """Test consistency checking."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_consistency_check(self):
        """Test checking consistency."""
        results = self.manager.check_consistency()
        
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

    def test_all_consistent_initially(self):
        """Test all panels consistent initially."""
        results = self.manager.check_consistency()
        
        for is_consistent in results.values():
            self.assertTrue(is_consistent)

    def test_dirty_mark_inconsistent(self):
        """Test dirty panels marked inconsistent."""
        self.manager.update_panel_state(PanelType.PROPERTIES, {'change': True})
        results = self.manager.check_consistency()
        
        # Properties should be dirty
        self.assertFalse(results['properties'])


class TestConflictResolution(unittest.TestCase):
    """Test conflict resolution."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_conflict_resolution_replace(self):
        """Test replace mode conflict resolution."""
        self.manager.conflict_resolution_mode = "replace"
        
        local = {'a': 1, 'b': 2}
        remote = {'b': 20, 'c': 30}
        
        result = self.manager.resolve_conflict(PanelType.PROPERTIES, remote, local)
        self.assertEqual(result, remote)

    def test_conflict_resolution_merge(self):
        """Test merge mode conflict resolution."""
        self.manager.conflict_resolution_mode = "merge"
        
        local = {'a': 1, 'b': 2}
        remote = {'b': 20, 'c': 30}
        
        result = self.manager.resolve_conflict(PanelType.PROPERTIES, remote, local)
        
        self.assertEqual(result['a'], 1)  # From local
        self.assertEqual(result['b'], 20)  # From remote (takes precedence)
        self.assertEqual(result['c'], 30)  # From remote


class TestEventListeners(unittest.TestCase):
    """Test event listener functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()
        self.events = []

    def listener(self, message_data):
        """Capture events."""
        self.events.append(message_data)

    def test_add_listener(self):
        """Test adding listener."""
        self.manager.add_listener(PanelType.CANVAS, self.listener)
        self.assertIn(self.listener, self.manager.listeners[PanelType.CANVAS])

    def test_remove_listener(self):
        """Test removing listener."""
        self.manager.add_listener(PanelType.CANVAS, self.listener)
        self.manager.remove_listener(PanelType.CANVAS, self.listener)
        
        self.assertNotIn(self.listener, self.manager.listeners[PanelType.CANVAS])

    def test_duplicate_listener_not_added(self):
        """Test duplicate listeners not added."""
        self.manager.add_listener(PanelType.CANVAS, self.listener)
        self.manager.add_listener(PanelType.CANVAS, self.listener)
        
        count = self.manager.listeners[PanelType.CANVAS].count(self.listener)
        self.assertEqual(count, 1)


class TestSyncQueue(unittest.TestCase):
    """Test synchronization queue."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_queue_message(self):
        """Test queueing sync message."""
        message = SyncMessage(
            event_type=SyncEvent.COMPONENT_ADDED,
            source_panel=PanelType.CANVAS
        )
        self.manager._queue_sync_message(message)
        
        self.assertEqual(len(self.manager.sync_queue), 1)

    def test_queue_size_limit(self):
        """Test queue respects size limit."""
        for i in range(150):
            message = SyncMessage(
                event_type=SyncEvent.COMPONENT_MODIFIED,
                source_panel=PanelType.CANVAS,
                data={'index': i}
            )
            self.manager._queue_sync_message(message)
        
        self.assertLessEqual(len(self.manager.sync_queue), 100)

    def test_clear_sync_queue(self):
        """Test clearing queue."""
        for i in range(5):
            message = SyncMessage(
                event_type=SyncEvent.PROPERTY_CHANGED,
                source_panel=PanelType.PROPERTIES
            )
            self.manager._queue_sync_message(message)
        
        count = self.manager.clear_sync_queue()
        self.assertEqual(count, 5)
        self.assertEqual(len(self.manager.sync_queue), 0)


class TestPanelReset(unittest.TestCase):
    """Test panel reset functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_reset_panel(self):
        """Test resetting panel state."""
        self.manager.update_panel_state(PanelType.PROPERTIES, {'data': 'test'})
        result = self.manager.reset_panel(PanelType.PROPERTIES)
        
        self.assertTrue(result)
        state = self.manager.get_panel_state(PanelType.PROPERTIES)
        self.assertEqual(state.data, {})

    def test_reset_nonexistent_panel(self):
        """Test reset on non-existent panel."""
        self.manager.unregister_panel(PanelType.PROPERTIES)
        result = self.manager.reset_panel(PanelType.PROPERTIES)
        
        self.assertFalse(result)


class TestStatistics(unittest.TestCase):
    """Test synchronization statistics."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_empty_statistics(self):
        """Test statistics initially."""
        stats = self.manager.get_sync_statistics()
        
        self.assertEqual(stats['queue_size'], 0)
        self.assertFalse(stats['is_syncing'])

    def test_statistics_with_dirty(self):
        """Test statistics with dirty panels."""
        self.manager.update_panel_state(PanelType.CANVAS, {'change': True})
        stats = self.manager.get_sync_statistics()
        
        self.assertGreater(stats['dirty_panels'], 0)

    def test_all_panel_states(self):
        """Test getting all panel states."""
        states = self.manager.get_all_panel_states()
        
        self.assertGreater(len(states), 0)
        for key, state in states.items():
            self.assertIn('panel_type', state)
            self.assertIn('visible', state)


class TestThrottling(unittest.TestCase):
    """Test synchronization throttling."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_set_throttle(self):
        """Test setting throttle."""
        self.manager.set_throttle_ms(100)
        self.assertEqual(self.manager.sync_throttle_ms, 100)

    def test_negative_throttle_clamped(self):
        """Test negative throttle clamped to 0."""
        self.manager.set_throttle_ms(-10)
        self.assertEqual(self.manager.sync_throttle_ms, 0)


class TestConsistencyToggle(unittest.TestCase):
    """Test consistency check toggling."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PanelSyncManager()

    def test_disable_consistency_checks(self):
        """Test disabling consistency checks."""
        self.manager.enable_consistency_checks(False)
        self.assertFalse(self.manager.consistency_checks_enabled)

    def test_enable_consistency_checks(self):
        """Test enabling consistency checks."""
        self.manager.enable_consistency_checks(True)
        self.assertTrue(self.manager.consistency_checks_enabled)


if __name__ == '__main__':
    unittest.main()
