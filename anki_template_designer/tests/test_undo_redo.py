"""
Tests for Undo/Redo Manager.

Plan 07: Comprehensive tests for UndoRedoManager functionality.
"""

import pytest
from anki_template_designer.services.undo_redo_manager import (
    UndoRedoManager,
    HistoryEntry
)


class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""
    
    def test_create_entry(self):
        """Test creating a history entry."""
        entry = HistoryEntry(
            state_before={"x": 1},
            state_after={"x": 2},
            description="Changed x"
        )
        assert entry.state_before == {"x": 1}
        assert entry.state_after == {"x": 2}
        assert entry.description == "Changed x"


class TestUndoRedoManagerInitialization:
    """Tests for UndoRedoManager initialization."""
    
    def test_initial_state(self):
        """Test manager starts with empty history."""
        manager = UndoRedoManager()
        assert not manager.can_undo
        assert not manager.can_redo
        assert manager.history_size == 0
    
    def test_custom_max_history(self):
        """Test custom max history setting."""
        manager = UndoRedoManager(max_history=5)
        assert manager.history_size == 0
    
    def test_undo_description_when_empty(self):
        """Test undo description returns None when empty."""
        manager = UndoRedoManager()
        assert manager.undo_description is None
    
    def test_redo_description_when_empty(self):
        """Test redo description returns None when empty."""
        manager = UndoRedoManager()
        assert manager.redo_description is None


class TestPushState:
    """Tests for push_state functionality."""
    
    def test_push_single_state(self):
        """Test pushing a single state."""
        manager = UndoRedoManager()
        manager.push_state({"a": 1}, {"a": 2}, "Change a")
        
        assert manager.can_undo
        assert not manager.can_redo
        assert manager.history_size == 1
        assert manager.undo_description == "Change a"
    
    def test_push_multiple_states(self):
        """Test pushing multiple states."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        manager.push_state({"x": 2}, {"x": 3}, "Third")
        
        assert manager.history_size == 3
        assert manager.undo_description == "Third"
    
    def test_push_clears_redo_history(self):
        """Test that pushing a new state clears redo history."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        # Undo once
        manager.undo()
        assert manager.can_redo
        
        # Push new state should clear redo
        manager.push_state({"x": 1}, {"x": 3}, "New path")
        assert not manager.can_redo
        assert manager.history_size == 2  # First + New path
    
    def test_deep_copy_on_push(self):
        """Test that states are deep copied when pushed."""
        manager = UndoRedoManager()
        state = {"nested": {"value": 1}}
        
        manager.push_state({"old": True}, state, "Test")
        
        # Modify original
        state["nested"]["value"] = 999
        
        # History should have original value
        manager.undo()
        result = manager.redo()
        assert result["nested"]["value"] == 1


class TestUndo:
    """Tests for undo functionality."""
    
    def test_single_undo(self):
        """Test single undo operation."""
        manager = UndoRedoManager()
        manager.push_state({"a": 1}, {"a": 2}, "Change a")
        
        state = manager.undo()
        assert state == {"a": 1}
        assert not manager.can_undo
        assert manager.can_redo
    
    def test_multiple_undo(self):
        """Test multiple undo operations."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        manager.push_state({"x": 2}, {"x": 3}, "Third")
        
        state = manager.undo()
        assert state == {"x": 2}
        
        state = manager.undo()
        assert state == {"x": 1}
        
        state = manager.undo()
        assert state == {"x": 0}
        assert not manager.can_undo
    
    def test_undo_returns_none_when_empty(self):
        """Test undo returns None when nothing to undo."""
        manager = UndoRedoManager()
        assert manager.undo() is None
    
    def test_undo_returns_deep_copy(self):
        """Test that undo returns a deep copy."""
        manager = UndoRedoManager()
        manager.push_state({"nested": {"value": 1}}, {"nested": {"value": 2}}, "Test")
        
        result = manager.undo()
        result["nested"]["value"] = 999
        
        # Redo should still have original value
        manager.redo()
        result2 = manager.undo()
        assert result2["nested"]["value"] == 1


class TestRedo:
    """Tests for redo functionality."""
    
    def test_single_redo(self):
        """Test single redo operation."""
        manager = UndoRedoManager()
        manager.push_state({"a": 1}, {"a": 2}, "Change a")
        manager.undo()
        
        state = manager.redo()
        assert state == {"a": 2}
        assert manager.can_undo
        assert not manager.can_redo
    
    def test_multiple_redo(self):
        """Test multiple redo operations."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        # Undo both
        manager.undo()
        manager.undo()
        
        # Redo both
        state = manager.redo()
        assert state == {"x": 1}
        
        state = manager.redo()
        assert state == {"x": 2}
        assert not manager.can_redo
    
    def test_redo_returns_none_when_empty(self):
        """Test redo returns None when nothing to redo."""
        manager = UndoRedoManager()
        manager.push_state({"a": 1}, {"a": 2}, "Change a")
        assert manager.redo() is None
    
    def test_redo_description(self):
        """Test redo description after undo."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First change")
        manager.undo()
        
        assert manager.redo_description == "First change"


class TestUndoRedoSequence:
    """Tests for undo/redo sequences."""
    
    def test_undo_redo_cycle(self):
        """Test undo followed by redo returns to same state."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        
        before_undo = {"x": 1}
        manager.undo()
        after_redo = manager.redo()
        
        assert after_redo == before_undo
    
    def test_interleaved_undo_redo(self):
        """Test interleaved undo and redo operations."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        # Undo twice
        state = manager.undo()
        assert state == {"x": 1}
        state = manager.undo()
        assert state == {"x": 0}
        
        # Redo once
        state = manager.redo()
        assert state == {"x": 1}
        
        # Undo again
        state = manager.undo()
        assert state == {"x": 0}
        
        # Redo twice
        state = manager.redo()
        assert state == {"x": 1}
        state = manager.redo()
        assert state == {"x": 2}


class TestMaxHistory:
    """Tests for max history limit."""
    
    def test_respects_max_history(self):
        """Test that max history limit is enforced."""
        manager = UndoRedoManager(max_history=3)
        
        for i in range(5):
            manager.push_state({"x": i}, {"x": i + 1}, f"Change {i}")
        
        # Should only have last 3 entries
        assert manager.history_size == 3
    
    def test_oldest_entries_removed(self):
        """Test that oldest entries are removed when limit exceeded."""
        manager = UndoRedoManager(max_history=3)
        
        for i in range(5):
            manager.push_state({"x": i}, {"x": i + 1}, f"Change {i}")
        
        history = manager.get_history_list()
        assert history == ["Change 2", "Change 3", "Change 4"]
    
    def test_can_still_undo_after_trim(self):
        """Test undo still works after history is trimmed."""
        manager = UndoRedoManager(max_history=2)
        
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        manager.push_state({"x": 2}, {"x": 3}, "Third")
        
        # Can undo remaining entries
        state = manager.undo()
        assert state == {"x": 2}
        
        state = manager.undo()
        assert state == {"x": 1}
        
        # No more to undo
        assert not manager.can_undo


class TestClear:
    """Tests for clear functionality."""
    
    def test_clear_empties_history(self):
        """Test clear removes all history."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        manager.clear()
        
        assert not manager.can_undo
        assert not manager.can_redo
        assert manager.history_size == 0
    
    def test_clear_when_already_empty(self):
        """Test clear on empty history doesn't error."""
        manager = UndoRedoManager()
        manager.clear()  # Should not raise
        assert manager.history_size == 0


class TestHistoryList:
    """Tests for get_history_list functionality."""
    
    def test_empty_history_list(self):
        """Test history list is empty initially."""
        manager = UndoRedoManager()
        assert manager.get_history_list() == []
    
    def test_history_list_order(self):
        """Test history list is in chronological order."""
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        manager.push_state({"x": 2}, {"x": 3}, "Third")
        
        history = manager.get_history_list()
        assert history == ["First", "Second", "Third"]


class TestListeners:
    """Tests for listener functionality."""
    
    def test_add_listener(self):
        """Test adding a listener."""
        manager = UndoRedoManager()
        notifications = []
        
        def listener(desc, can_undo, can_redo):
            notifications.append((desc, can_undo, can_redo))
        
        manager.add_listener(listener)
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        
        assert len(notifications) == 1
        assert notifications[0] == ("Change", True, False)
    
    def test_listener_on_undo(self):
        """Test listener is notified on undo."""
        manager = UndoRedoManager()
        notifications = []
        
        def listener(desc, can_undo, can_redo):
            notifications.append((desc, can_undo, can_redo))
        
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        manager.add_listener(listener)
        manager.undo()
        
        assert len(notifications) == 1
        assert notifications[0] == ("Undo: Change", False, True)
    
    def test_listener_on_redo(self):
        """Test listener is notified on redo."""
        manager = UndoRedoManager()
        notifications = []
        
        def listener(desc, can_undo, can_redo):
            notifications.append((desc, can_undo, can_redo))
        
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        manager.undo()
        manager.add_listener(listener)
        manager.redo()
        
        assert len(notifications) == 1
        assert notifications[0] == ("Redo: Change", True, False)
    
    def test_remove_listener(self):
        """Test removing a listener."""
        manager = UndoRedoManager()
        notifications = []
        
        def listener(desc, can_undo, can_redo):
            notifications.append(desc)
        
        manager.add_listener(listener)
        manager.push_state({"x": 0}, {"x": 1}, "First")
        
        manager.remove_listener(listener)
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        # Only notified for First
        assert notifications == ["First"]
    
    def test_multiple_listeners(self):
        """Test multiple listeners are notified."""
        manager = UndoRedoManager()
        results1 = []
        results2 = []
        
        manager.add_listener(lambda d, u, r: results1.append(d))
        manager.add_listener(lambda d, u, r: results2.append(d))
        
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        
        assert results1 == ["Change"]
        assert results2 == ["Change"]
    
    def test_listener_error_does_not_affect_others(self):
        """Test that a failing listener doesn't prevent others."""
        manager = UndoRedoManager()
        results = []
        
        def bad_listener(desc, can_undo, can_redo):
            raise ValueError("Test error")
        
        def good_listener(desc, can_undo, can_redo):
            results.append(desc)
        
        manager.add_listener(bad_listener)
        manager.add_listener(good_listener)
        
        # Should not raise, and good_listener should still be called
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        assert results == ["Change"]
    
    def test_listener_on_clear(self):
        """Test listener is notified on clear."""
        manager = UndoRedoManager()
        notifications = []
        
        def listener(desc, can_undo, can_redo):
            notifications.append((desc, can_undo, can_redo))
        
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        manager.add_listener(listener)
        manager.clear()
        
        assert len(notifications) == 1
        assert notifications[0] == ("History cleared", False, False)
    
    def test_add_same_listener_twice(self):
        """Test adding same listener twice only registers once."""
        manager = UndoRedoManager()
        count = [0]
        
        def listener(desc, can_undo, can_redo):
            count[0] += 1
        
        manager.add_listener(listener)
        manager.add_listener(listener)
        
        manager.push_state({"x": 0}, {"x": 1}, "Change")
        
        # Should only be notified once
        assert count[0] == 1
