"""
Issue #49: Undo/Redo History System - Tests

Comprehensive test suite for undo/redo functionality with 30+ tests covering:
- Action recording and retrieval
- Undo/redo operations
- History branching
- Memory optimization
- Statistics tracking
- State persistence
"""

import unittest
from datetime import datetime
from services.undo_redo_manager import (
    UndoRedoManager, ActionData, ActionType, HistoryBranch, HistoryStatistics
)


class TestActionData(unittest.TestCase):
    """Tests for ActionData model."""

    def test_action_creation(self):
        """Test basic action creation."""
        action = ActionData(
            action_type=ActionType.COMPONENT_ADD,
            description="Add button component"
        )
        self.assertEqual(action.action_type, ActionType.COMPONENT_ADD)
        self.assertEqual(action.description, "Add button component")
        self.assertTrue(action.is_reversible)

    def test_action_serialization(self):
        """Test action to_dict conversion."""
        action = ActionData(
            action_type=ActionType.PROPERTY_CHANGE,
            description="Change color",
            before_state={'color': 'red'},
            after_state={'color': 'blue'}
        )
        data = action.to_dict()
        self.assertEqual(data['action_type'], 'property_change')
        self.assertEqual(data['before_state'], {'color': 'red'})
        self.assertEqual(data['after_state'], {'color': 'blue'})

    def test_action_deserialization(self):
        """Test creating action from dict."""
        data = {
            'id': 'test-123',
            'action_type': 'component_move',
            'description': 'Move component',
            'timestamp': datetime.now().isoformat(),
            'before_state': {'x': 10, 'y': 20},
            'after_state': {'x': 30, 'y': 40},
            'target_id': 'comp-1'
        }
        action = ActionData.from_dict(data)
        self.assertEqual(action.id, 'test-123')
        self.assertEqual(action.action_type, ActionType.COMPONENT_MOVE)
        self.assertEqual(action.before_state['x'], 10)

    def test_action_with_metadata(self):
        """Test action with metadata."""
        action = ActionData(
            action_type=ActionType.CUSTOM,
            description="Custom action",
            metadata={'user_id': 'user123', 'source': 'drag'}
        )
        self.assertEqual(action.metadata['user_id'], 'user123')
        data = action.to_dict()
        self.assertEqual(data['metadata']['source'], 'drag')


class TestHistoryBranch(unittest.TestCase):
    """Tests for HistoryBranch model."""

    def test_branch_creation(self):
        """Test branch creation."""
        branch = HistoryBranch(name="Test Branch")
        self.assertEqual(branch.name, "Test Branch")
        self.assertTrue(branch.is_main)
        self.assertEqual(len(branch.actions), 0)

    def test_branch_serialization(self):
        """Test branch to_dict."""
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        branch = HistoryBranch(name="Branch 1")
        branch.actions.append(action)
        data = branch.to_dict()
        self.assertEqual(data['name'], "Branch 1")
        self.assertEqual(len(data['actions']), 1)

    def test_branch_deserialization(self):
        """Test creating branch from dict."""
        data = {
            'id': 'branch-1',
            'name': 'Test Branch',
            'is_main': False,
            'actions': [],
            'created_at': datetime.now().isoformat()
        }
        branch = HistoryBranch.from_dict(data)
        self.assertEqual(branch.id, 'branch-1')
        self.assertEqual(branch.name, 'Test Branch')


class TestUndoRedoBasics(unittest.TestCase):
    """Tests for basic undo/redo functionality."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager()

    def test_manager_creation(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager.main_branch)
        self.assertEqual(self.manager.current_index, -1)
        self.assertFalse(self.manager.can_undo())

    def test_record_single_action(self):
        """Test recording a single action."""
        action = ActionData(
            action_type=ActionType.COMPONENT_ADD,
            description="Add component"
        )
        action_id = self.manager.record_action(action)
        self.assertEqual(action_id, action.id)
        self.assertEqual(len(self.manager.current_branch.actions), 1)
        self.assertTrue(self.manager.can_undo())

    def test_record_multiple_actions(self):
        """Test recording multiple actions."""
        for i in range(5):
            action = ActionData(
                action_type=ActionType.PROPERTY_CHANGE,
                description=f"Change property {i}"
            )
            self.manager.record_action(action)

        self.assertEqual(len(self.manager.current_branch.actions), 5)
        self.assertEqual(self.manager.current_index, 4)

    def test_undo_single_action(self):
        """Test undoing a single action."""
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        self.assertTrue(self.manager.can_undo())
        
        result = self.manager.undo()
        self.assertTrue(result)
        self.assertEqual(self.manager.current_index, -1)
        self.assertFalse(self.manager.can_undo())

    def test_undo_multiple_actions(self):
        """Test undoing multiple actions."""
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        # Undo all actions
        for i in range(5):
            self.assertTrue(self.manager.can_undo())
            self.manager.undo()

        self.assertEqual(self.manager.current_index, -1)
        self.assertFalse(self.manager.can_undo())

    def test_redo_after_undo(self):
        """Test redo after undo."""
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        
        self.manager.undo()
        self.assertFalse(self.manager.can_undo())
        self.assertTrue(self.manager.can_redo())
        
        self.manager.redo()
        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_redo_multiple(self):
        """Test redoing multiple actions."""
        for i in range(3):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        # Undo all
        for _ in range(3):
            self.manager.undo()

        # Redo all
        for _ in range(3):
            self.assertTrue(self.manager.can_redo())
            self.manager.redo()

        self.assertEqual(self.manager.current_index, 2)
        self.assertFalse(self.manager.can_redo())


class TestUndoRedoAdvanced(unittest.TestCase):
    """Tests for advanced undo/redo features."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager(enable_branching=True)

    def test_undo_to_specific_action(self):
        """Test undoing to a specific action."""
        action_ids = []
        for i in range(5):
            action = ActionData(
                action_type=ActionType.PROPERTY_CHANGE,
                description=f"Action {i}"
            )
            action_id = self.manager.record_action(action)
            action_ids.append(action_id)

        # Undo to third action
        self.manager.undo_to(action_ids[2])
        self.assertEqual(self.manager.current_index, 2)

    def test_redo_to_specific_action(self):
        """Test redoing to a specific action."""
        action_ids = []
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            action_id = self.manager.record_action(action)
            action_ids.append(action_id)

        # Go back and redo to specific action
        self.manager.current_index = 1
        self.manager.redo_to(action_ids[3])
        self.assertEqual(self.manager.current_index, 3)

    def test_get_current_action(self):
        """Test getting current action."""
        action = ActionData(
            action_type=ActionType.COMPONENT_ADD,
            description="Add component"
        )
        self.manager.record_action(action)
        
        current = self.manager.get_current_action()
        self.assertIsNotNone(current)
        self.assertEqual(current.description, "Add component")

    def test_get_history(self):
        """Test getting history."""
        for i in range(3):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        history = self.manager.get_history()
        self.assertEqual(len(history), 3)

    def test_get_future_history(self):
        """Test getting future history (redoable)."""
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        self.manager.current_index = 2
        future = self.manager.get_future_history()
        self.assertEqual(len(future), 2)


class TestHistoryBranching(unittest.TestCase):
    """Tests for history branching."""

    def setUp(self):
        """Set up test manager with branching enabled."""
        self.manager = UndoRedoManager(enable_branching=True)

    def test_branch_creation_on_new_action(self):
        """Test automatic branch creation."""
        # Record initial actions
        for i in range(3):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        initial_branch = self.manager.current_branch
        
        # Undo one step
        self.manager.undo()
        
        # Record new action (should create branch)
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)

        # Should have branched
        self.assertNotEqual(self.manager.current_branch.id, initial_branch.id)
        self.assertGreater(len(self.manager.branches), 1)

    def test_branch_tree(self):
        """Test getting branch tree."""
        # Create some actions
        for i in range(3):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        tree = self.manager.get_branch_tree()
        self.assertIn('id', tree)
        self.assertIn('name', tree)

    def test_switch_branch(self):
        """Test switching between branches."""
        # Create first branch with actions
        for i in range(3):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        first_branch_id = self.manager.current_branch.id

        # Create branch point
        self.manager.undo()
        
        # Create second branch
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        
        second_branch_id = self.manager.current_branch.id
        self.assertNotEqual(first_branch_id, second_branch_id)

        # Switch back to first branch
        result = self.manager.switch_branch(first_branch_id)
        self.assertTrue(result)
        self.assertEqual(self.manager.current_branch.id, first_branch_id)

    def test_get_branches(self):
        """Test getting all branches."""
        # Create branching structure
        for i in range(2):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        self.manager.undo()
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)

        branches = self.manager.get_branches()
        self.assertGreater(len(branches), 1)


class TestHistoryOptimization(unittest.TestCase):
    """Tests for history optimization."""

    def test_max_history_size(self):
        """Test maximum history size enforcement."""
        manager = UndoRedoManager(max_history_size=10)

        # Add more actions than max
        for i in range(15):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            manager.record_action(action)

        # Should have optimized
        self.assertLessEqual(len(manager.current_branch.actions), 10)

    def test_memory_efficient(self):
        """Test memory efficiency with large histories."""
        manager = UndoRedoManager(max_history_size=100)

        # Add large actions
        for i in range(50):
            action = ActionData(
                action_type=ActionType.PROPERTY_CHANGE,
                before_state={'data': 'x' * 100},
                after_state={'data': 'y' * 100}
            )
            manager.record_action(action)

        stats = manager.get_statistics()
        self.assertGreater(stats.memory_usage_bytes, 0)


class TestHistoryStatistics(unittest.TestCase):
    """Tests for history statistics."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager()

    def test_empty_statistics(self):
        """Test statistics for empty history."""
        stats = self.manager.get_statistics()
        self.assertEqual(stats.total_actions, 0)
        self.assertEqual(stats.undoable_actions, 0)
        self.assertEqual(stats.redoable_actions, 0)

    def test_statistics_with_actions(self):
        """Test statistics with recorded actions."""
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        stats = self.manager.get_statistics()
        self.assertEqual(stats.total_actions, 5)
        self.assertEqual(stats.undoable_actions, 5)
        self.assertEqual(stats.redoable_actions, 0)

    def test_statistics_after_undo(self):
        """Test statistics after undo."""
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        self.manager.undo()
        self.manager.undo()

        stats = self.manager.get_statistics()
        self.assertEqual(stats.undoable_actions, 3)
        self.assertEqual(stats.redoable_actions, 2)

    def test_action_type_statistics(self):
        """Test statistics about action types."""
        self.manager.record_action(ActionData(action_type=ActionType.COMPONENT_ADD))
        self.manager.record_action(ActionData(action_type=ActionType.COMPONENT_ADD))
        self.manager.record_action(ActionData(action_type=ActionType.PROPERTY_CHANGE))

        stats = self.manager.get_statistics()
        self.assertEqual(stats.total_actions, 3)
        self.assertEqual(stats.most_common_action_type, 'component_add')


class TestHistoryPersistence(unittest.TestCase):
    """Tests for saving and loading history."""

    def test_save_empty_history(self):
        """Test saving empty history."""
        manager = UndoRedoManager()
        state = manager.save_state()
        
        self.assertIn('main_branch', state)
        self.assertIn('current_index', state)
        self.assertEqual(state['current_index'], -1)

    def test_save_and_load_history(self):
        """Test saving and loading history."""
        manager1 = UndoRedoManager()
        
        # Create some history
        for i in range(3):
            action = ActionData(
                action_type=ActionType.PROPERTY_CHANGE,
                description=f"Action {i}"
            )
            manager1.record_action(action)

        manager1.undo()
        
        # Save state
        state = manager1.save_state()

        # Load in new manager
        manager2 = UndoRedoManager()
        result = manager2.load_state(state)
        
        self.assertTrue(result)
        self.assertEqual(manager2.current_index, manager1.current_index)
        self.assertEqual(len(manager2.current_branch.actions), 3)

    def test_load_invalid_state(self):
        """Test loading invalid state."""
        manager = UndoRedoManager()
        result = manager.load_state({})
        self.assertFalse(result)


class TestActionHandlers(unittest.TestCase):
    """Tests for action handlers."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager()
        self.handler_called = False

    def test_register_handler(self):
        """Test registering action handler."""
        def handler(action, is_undo):
            self.handler_called = True

        self.manager.register_action_handler(ActionType.COMPONENT_ADD, handler)
        self.assertIn(ActionType.COMPONENT_ADD, self.manager.action_handlers)

    def test_handler_invocation(self):
        """Test handler is called on undo."""
        def handler(action, is_undo):
            self.handler_called = True

        self.manager.register_action_handler(ActionType.COMPONENT_ADD, handler)
        
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        self.manager.undo()
        
        self.assertTrue(self.handler_called)


class TestListeners(unittest.TestCase):
    """Tests for event listeners."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager()
        self.events = []

    def test_add_listener(self):
        """Test adding listener."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        self.assertIn(listener, self.manager.listeners)

    def test_listener_notification(self):
        """Test listener is notified on action."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        
        self.assertIn('action_recorded', self.events)

    def test_undo_notification(self):
        """Test listener is notified on undo."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        
        action = ActionData(action_type=ActionType.COMPONENT_ADD)
        self.manager.record_action(action)
        self.manager.undo()
        
        self.assertIn('action_undone', self.events)

    def test_remove_listener(self):
        """Test removing listener."""
        def listener(event_type, data):
            self.events.append(event_type)

        self.manager.add_listener(listener)
        self.manager.remove_listener(listener)
        
        self.assertNotIn(listener, self.manager.listeners)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases."""

    def setUp(self):
        """Set up test manager."""
        self.manager = UndoRedoManager()

    def test_undo_empty_history(self):
        """Test undo on empty history."""
        result = self.manager.undo()
        self.assertFalse(result)

    def test_redo_empty_history(self):
        """Test redo on empty history."""
        result = self.manager.redo()
        self.assertFalse(result)

    def test_clear_history(self):
        """Test clearing history."""
        for i in range(5):
            action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
            self.manager.record_action(action)

        self.manager.clear_history()
        self.assertEqual(len(self.manager.current_branch.actions), 0)
        self.assertEqual(self.manager.current_index, -1)

    def test_irreversible_action(self):
        """Test handling irreversible actions."""
        action = ActionData(
            action_type=ActionType.CUSTOM,
            is_reversible=False
        )
        self.manager.record_action(action)
        
        result = self.manager.undo()
        self.assertFalse(result)

    def test_undo_to_nonexistent_action(self):
        """Test undo to non-existent action."""
        action = ActionData(action_type=ActionType.PROPERTY_CHANGE)
        self.manager.record_action(action)
        
        result = self.manager.undo_to("nonexistent-id")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
