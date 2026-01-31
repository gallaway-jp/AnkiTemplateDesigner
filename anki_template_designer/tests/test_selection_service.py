"""
Tests for selection service.

Plan 12: Tests for SelectionService and selection operations.
"""

import pytest
from unittest.mock import Mock

from anki_template_designer.services.selection_service import (
    SelectionState,
    SelectionService,
    get_selection_service,
    init_selection_service
)


class TestSelectionState:
    """Tests for SelectionState class."""
    
    def test_default_values(self):
        """Test default state values."""
        state = SelectionState()
        assert state.selected_ids == set()
        assert state.primary_id is None
        assert state.selection_order == []
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        state = SelectionState(
            selected_ids={"a", "b"},
            primary_id="b",
            selection_order=["a", "b"]
        )
        d = state.to_dict()
        assert set(d["selectedIds"]) == {"a", "b"}
        assert d["primaryId"] == "b"
        assert d["count"] == 2
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        d = {
            "selectedIds": ["x", "y", "z"],
            "primaryId": "y",
            "selectionOrder": ["x", "y", "z"]
        }
        state = SelectionState.from_dict(d)
        assert state.selected_ids == {"x", "y", "z"}
        assert state.primary_id == "y"
        assert state.selection_order == ["x", "y", "z"]
    
    def test_clear(self):
        """Test clearing state."""
        state = SelectionState(
            selected_ids={"a", "b"},
            primary_id="a",
            selection_order=["a", "b"]
        )
        state.clear()
        assert state.is_empty()
        assert state.primary_id is None
    
    def test_is_selected(self):
        """Test checking if component is selected."""
        state = SelectionState(selected_ids={"comp1", "comp2"})
        assert state.is_selected("comp1")
        assert state.is_selected("comp2")
        assert not state.is_selected("comp3")
    
    def test_count(self):
        """Test selection count."""
        state = SelectionState(selected_ids={"a", "b", "c"})
        assert state.count() == 3


class TestSelectionService:
    """Tests for SelectionService class."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = SelectionService()
        assert service.is_empty()
        assert service.count == 0
        assert service.primary_id is None
    
    def test_select_single(self):
        """Test single component selection."""
        service = SelectionService()
        result = service.select("comp1")
        
        assert result is True
        assert service.is_selected("comp1")
        assert service.primary_id == "comp1"
        assert service.count == 1
    
    def test_select_replaces_selection(self):
        """Test that select() replaces current selection."""
        service = SelectionService()
        service.select("comp1")
        service.select("comp2")
        
        assert not service.is_selected("comp1")
        assert service.is_selected("comp2")
        assert service.count == 1
    
    def test_select_same_returns_false(self):
        """Test selecting same component returns False."""
        service = SelectionService()
        service.select("comp1")
        result = service.select("comp1")
        
        assert result is False  # No change
    
    def test_select_empty_returns_false(self):
        """Test selecting empty string returns False."""
        service = SelectionService()
        assert service.select("") is False
        assert service.select(None) is False
    
    def test_add_to_selection(self):
        """Test adding to selection (multi-select)."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        service.add_to_selection("comp3")
        
        assert service.is_selected("comp1")
        assert service.is_selected("comp2")
        assert service.is_selected("comp3")
        assert service.count == 3
        assert service.primary_id == "comp3"  # Last added
    
    def test_add_duplicate_returns_false(self):
        """Test adding already selected component returns False."""
        service = SelectionService()
        service.select("comp1")
        result = service.add_to_selection("comp1")
        
        assert result is False
    
    def test_remove_from_selection(self):
        """Test removing from selection."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        
        result = service.remove_from_selection("comp1")
        
        assert result is True
        assert not service.is_selected("comp1")
        assert service.is_selected("comp2")
        assert service.count == 1
    
    def test_remove_updates_primary(self):
        """Test removing primary updates to last selected."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        service.add_to_selection("comp3")
        
        service.remove_from_selection("comp3")  # Remove primary
        
        assert service.primary_id == "comp2"
    
    def test_remove_nonexistent_returns_false(self):
        """Test removing non-selected component returns False."""
        service = SelectionService()
        service.select("comp1")
        
        result = service.remove_from_selection("comp2")
        assert result is False
    
    def test_toggle_selection(self):
        """Test toggling selection."""
        service = SelectionService()
        
        # Toggle on
        result = service.toggle_selection("comp1")
        assert result is True
        assert service.is_selected("comp1")
        
        # Toggle off
        result = service.toggle_selection("comp1")
        assert result is False
        assert not service.is_selected("comp1")
    
    def test_clear(self):
        """Test clearing all selection."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        
        result = service.clear()
        
        assert result is True
        assert service.is_empty()
        assert service.primary_id is None
    
    def test_clear_empty_returns_false(self):
        """Test clearing empty selection returns False."""
        service = SelectionService()
        result = service.clear()
        
        assert result is False
    
    def test_select_all(self):
        """Test selecting all specified components."""
        service = SelectionService()
        result = service.select_all(["a", "b", "c", "d"])
        
        assert result is True
        assert service.count == 4
        assert service.primary_id == "d"  # Last in list
    
    def test_select_all_empty_returns_false(self):
        """Test selecting empty list returns False."""
        service = SelectionService()
        result = service.select_all([])
        
        assert result is False
    
    def test_set_selection(self):
        """Test setting explicit selection."""
        service = SelectionService()
        service.select("old")
        
        service.set_selection(["x", "y", "z"], primary_id="y")
        
        assert service.selected_ids == ["x", "y", "z"] or set(service.selected_ids) == {"x", "y", "z"}
        assert service.primary_id == "y"
    
    def test_selection_order_preserved(self):
        """Test that selection order is preserved."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        service.add_to_selection("comp3")
        
        state = service.state
        assert state.selection_order == ["comp1", "comp2", "comp3"]


class TestSelectionRange:
    """Tests for range selection (Shift+click)."""
    
    def test_select_range(self):
        """Test selecting a range of components."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d", "e"])
        
        service.select("b")  # Start at b
        service.select_range("d")  # Shift-click d
        
        assert service.is_selected("b")
        assert service.is_selected("c")
        assert service.is_selected("d")
        assert not service.is_selected("a")
        assert not service.is_selected("e")
    
    def test_select_range_reverse(self):
        """Test selecting range in reverse direction."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d", "e"])
        
        service.select("d")
        service.select_range("b")
        
        assert service.is_selected("b")
        assert service.is_selected("c")
        assert service.is_selected("d")
    
    def test_select_range_no_order(self):
        """Test range selection without component order."""
        service = SelectionService()
        service.select("comp1")
        
        # Should just select the target
        service.select_range("comp2")
        
        assert service.is_selected("comp2")


class TestSelectionNavigation:
    """Tests for keyboard navigation."""
    
    def test_move_next(self):
        """Test moving selection to next component."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d"])
        service.select("b")
        
        result = service.move_selection("next")
        
        assert result == "c"
        assert service.primary_id == "c"
    
    def test_move_prev(self):
        """Test moving selection to previous component."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d"])
        service.select("c")
        
        result = service.move_selection("prev")
        
        assert result == "b"
        assert service.primary_id == "b"
    
    def test_move_first(self):
        """Test moving selection to first component."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d"])
        service.select("c")
        
        result = service.move_selection("first")
        
        assert result == "a"
    
    def test_move_last(self):
        """Test moving selection to last component."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c", "d"])
        service.select("b")
        
        result = service.move_selection("last")
        
        assert result == "d"
    
    def test_move_at_boundary(self):
        """Test moving at boundaries doesn't go out of range."""
        service = SelectionService()
        service.set_component_order(["a", "b", "c"])
        service.select("c")
        
        result = service.move_selection("next")
        
        assert result == "c"  # Stays at end
    
    def test_move_no_order_returns_none(self):
        """Test moving without component order returns None."""
        service = SelectionService()
        result = service.move_selection("next")
        
        assert result is None


class TestSelectionListeners:
    """Tests for selection change listeners."""
    
    def test_add_listener(self):
        """Test adding a listener."""
        service = SelectionService()
        listener = Mock()
        
        service.add_listener(listener)
        service.select("comp1")
        
        assert listener.called
    
    def test_listener_receives_states(self):
        """Test listener receives old and new states."""
        service = SelectionService()
        listener = Mock()
        service.add_listener(listener)
        
        service.select("comp1")
        
        old_state, new_state = listener.call_args[0]
        assert old_state.is_empty()
        assert "comp1" in new_state.selected_ids
    
    def test_remove_listener(self):
        """Test removing a listener."""
        service = SelectionService()
        listener = Mock()
        
        service.add_listener(listener)
        service.remove_listener(listener)
        service.select("comp1")
        
        assert not listener.called
    
    def test_listener_not_called_when_no_change(self):
        """Test listener not called when selection doesn't change."""
        service = SelectionService()
        listener = Mock()
        service.add_listener(listener)
        
        service.clear()  # Already empty
        
        assert not listener.called
    
    def test_multiple_listeners(self):
        """Test multiple listeners are all notified."""
        service = SelectionService()
        listener1 = Mock()
        listener2 = Mock()
        
        service.add_listener(listener1)
        service.add_listener(listener2)
        service.select("comp1")
        
        assert listener1.called
        assert listener2.called
    
    def test_listener_error_handled(self):
        """Test listener errors don't break other listeners."""
        service = SelectionService()
        
        def bad_listener(old, new):
            raise ValueError("Test error")
        
        good_listener = Mock()
        
        service.add_listener(bad_listener)
        service.add_listener(good_listener)
        
        # Should not raise
        service.select("comp1")
        
        # Good listener still called
        assert good_listener.called


class TestSelectionPersistence:
    """Tests for state persistence."""
    
    def test_get_state_dict(self):
        """Test getting state as dictionary."""
        service = SelectionService()
        service.select("comp1")
        service.add_to_selection("comp2")
        
        state_dict = service.get_state_dict()
        
        assert "selectedIds" in state_dict
        assert "primaryId" in state_dict
        assert state_dict["primaryId"] == "comp2"
    
    def test_restore_state(self):
        """Test restoring state from dictionary."""
        service = SelectionService()
        
        state_dict = {
            "selectedIds": ["a", "b", "c"],
            "primaryId": "b",
            "selectionOrder": ["a", "b", "c"]
        }
        
        service.restore_state(state_dict)
        
        assert service.is_selected("a")
        assert service.is_selected("b")
        assert service.is_selected("c")
        assert service.primary_id == "b"
    
    def test_restore_triggers_listener(self):
        """Test restoring state triggers listener if changed."""
        service = SelectionService()
        listener = Mock()
        service.add_listener(listener)
        
        service.restore_state({"selectedIds": ["x"], "primaryId": "x"})
        
        assert listener.called


class TestGlobalFunctions:
    """Tests for global service functions."""
    
    def test_init_selection_service(self):
        """Test initializing global service."""
        service = init_selection_service()
        
        assert service is not None
        assert isinstance(service, SelectionService)
    
    def test_get_selection_service(self):
        """Test getting global service."""
        init_selection_service()
        
        service = get_selection_service()
        assert service is not None
