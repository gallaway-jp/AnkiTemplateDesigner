# Plan 07: Undo/Redo System

## Objective
Implement a robust undo/redo system for template editing operations.

---

## Prerequisites
- [ ] Plans 01-06 completed and tested
- [ ] Template service working

---

## Step 7.1: Create History Manager

### Task
Implement the command pattern for undo/redo operations.

### Implementation

**anki_template_designer/services/undo_redo_manager.py**
```python
"""Undo/Redo manager using command pattern.

Provides unlimited undo/redo capability for template editing
operations with memory-efficient state snapshots.
"""

import copy
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("anki_template_designer.services.undo_redo_manager")

T = TypeVar("T")


@dataclass
class HistoryEntry:
    """A single history entry.
    
    Attributes:
        description: Human-readable description.
        timestamp: When the action occurred.
        state_before: State before the action.
        state_after: State after the action.
    """
    description: str
    timestamp: datetime
    state_before: Any
    state_after: Any


class UndoRedoManager(Generic[T]):
    """Manages undo/redo history for state changes.
    
    Uses a state-based approach where complete states are saved
    at each change point. Efficient for small to medium state sizes.
    
    Attributes:
        max_history: Maximum number of history entries.
    """
    
    DEFAULT_MAX_HISTORY = 100
    
    def __init__(
        self,
        max_history: int = DEFAULT_MAX_HISTORY,
        state_serializer: Optional[Callable[[T], Any]] = None,
        state_deserializer: Optional[Callable[[Any], T]] = None
    ) -> None:
        """Initialize the undo/redo manager.
        
        Args:
            max_history: Maximum history entries to keep.
            state_serializer: Optional function to serialize state.
            state_deserializer: Optional function to deserialize state.
        """
        self._history: List[HistoryEntry] = []
        self._current_index: int = -1
        self._max_history = max_history
        self._serializer = state_serializer or (lambda x: copy.deepcopy(x))
        self._deserializer = state_deserializer or (lambda x: copy.deepcopy(x))
        self._listeners: List[Callable[[str, bool, bool], None]] = []
        
        logger.info(f"UndoRedoManager initialized: max_history={max_history}")
    
    def push_state(
        self,
        state_before: T,
        state_after: T,
        description: str = "Edit"
    ) -> None:
        """Record a state change.
        
        Args:
            state_before: State before the change.
            state_after: State after the change.
            description: Description of the change.
        """
        # Clear any redo history beyond current position
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        # Create entry with serialized states
        entry = HistoryEntry(
            description=description,
            timestamp=datetime.now(),
            state_before=self._serializer(state_before),
            state_after=self._serializer(state_after)
        )
        
        self._history.append(entry)
        self._current_index = len(self._history) - 1
        
        # Trim history if exceeds max
        if len(self._history) > self._max_history:
            excess = len(self._history) - self._max_history
            self._history = self._history[excess:]
            self._current_index -= excess
        
        self._notify_listeners(description)
        logger.debug(f"State pushed: {description}")
    
    def undo(self) -> Optional[T]:
        """Undo the last action.
        
        Returns:
            The state before the last action, or None if nothing to undo.
        """
        if not self.can_undo:
            logger.debug("Nothing to undo")
            return None
        
        entry = self._history[self._current_index]
        self._current_index -= 1
        
        state = self._deserializer(entry.state_before)
        self._notify_listeners(f"Undo: {entry.description}")
        
        logger.debug(f"Undid: {entry.description}")
        return state
    
    def redo(self) -> Optional[T]:
        """Redo the last undone action.
        
        Returns:
            The state after the redone action, or None if nothing to redo.
        """
        if not self.can_redo:
            logger.debug("Nothing to redo")
            return None
        
        self._current_index += 1
        entry = self._history[self._current_index]
        
        state = self._deserializer(entry.state_after)
        self._notify_listeners(f"Redo: {entry.description}")
        
        logger.debug(f"Redid: {entry.description}")
        return state
    
    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._current_index >= 0
    
    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._current_index < len(self._history) - 1
    
    @property
    def undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if self.can_undo:
            return self._history[self._current_index].description
        return None
    
    @property
    def redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if self.can_redo:
            return self._history[self._current_index + 1].description
        return None
    
    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1
        self._notify_listeners("History cleared")
        logger.info("History cleared")
    
    def add_listener(
        self,
        listener: Callable[[str, bool, bool], None]
    ) -> None:
        """Add a change listener.
        
        Args:
            listener: Callback(description, can_undo, can_redo).
        """
        self._listeners.append(listener)
    
    def remove_listener(
        self,
        listener: Callable[[str, bool, bool], None]
    ) -> None:
        """Remove a change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def get_history_list(self) -> List[Dict[str, Any]]:
        """Get list of history entries.
        
        Returns:
            List of history entry metadata.
        """
        return [
            {
                "index": i,
                "description": entry.description,
                "timestamp": entry.timestamp.isoformat(),
                "isCurrent": i == self._current_index
            }
            for i, entry in enumerate(self._history)
        ]
    
    def _notify_listeners(self, description: str) -> None:
        """Notify all listeners of a change."""
        for listener in self._listeners:
            try:
                listener(description, self.can_undo, self.can_redo)
            except Exception as e:
                logger.error(f"Listener error: {e}")
```

### Quality Checks

#### Security
- [ ] Deep copy prevents reference issues
- [ ] No sensitive data in history descriptions

#### Performance
- [ ] Bounded history size
- [ ] Efficient list operations
- [ ] Optional serialization for large states

#### Best Practices
- [ ] Generic type support
- [ ] Observer pattern for UI updates

#### Maintainability
- [ ] Clear state management
- [ ] Comprehensive logging

#### Documentation
- [ ] All methods documented

#### Testing
- [ ] Undo/redo sequences testable
- [ ] Edge cases covered

#### Accessibility
- [ ] N/A

#### Scalability
- [ ] Configurable history size

#### Compatibility
- [ ] Python 3.9+ generics

#### Error Handling
- [ ] Listener errors don't break manager

#### Complexity
- [ ] Simple stack-based model

#### Architecture
- [ ] Clean separation from state

#### License
- [ ] N/A

#### Specification
- [ ] Matches expected undo/redo behavior

---

## Step 7.2: Integrate with Template Editing

### Task
Connect undo/redo to template changes.

### Implementation

Add to **anki_template_designer/gui/webview_bridge.py**:

```python
from ..services.undo_redo_manager import UndoRedoManager
from ..core.models import Template

# In __init__:
self._undo_manager: Optional[UndoRedoManager[dict]] = None

# Add method:
def set_undo_manager(self, manager: UndoRedoManager) -> None:
    """Set the undo/redo manager."""
    self._undo_manager = manager
    
    # Set up listener to notify JS
    def on_history_change(desc: str, can_undo: bool, can_redo: bool):
        self.send_to_js("historyChanged", {
            "description": desc,
            "canUndo": can_undo,
            "canRedo": can_redo
        })
    
    manager.add_listener(on_history_change)

@pyqtSlot(result=str)
def undo(self) -> str:
    """Undo last action."""
    if self._undo_manager is None:
        return json.dumps({"success": False, "error": "Undo not available"})
    
    state = self._undo_manager.undo()
    if state:
        return json.dumps({"success": True, "state": state})
    return json.dumps({"success": False, "error": "Nothing to undo"})

@pyqtSlot(result=str)
def redo(self) -> str:
    """Redo last undone action."""
    if self._undo_manager is None:
        return json.dumps({"success": False, "error": "Redo not available"})
    
    state = self._undo_manager.redo()
    if state:
        return json.dumps({"success": True, "state": state})
    return json.dumps({"success": False, "error": "Nothing to redo"})

@pyqtSlot(result=str)
def getHistoryState(self) -> str:
    """Get current history state."""
    if self._undo_manager is None:
        return json.dumps({"canUndo": False, "canRedo": False})
    
    return json.dumps({
        "canUndo": self._undo_manager.can_undo,
        "canRedo": self._undo_manager.can_redo,
        "undoDescription": self._undo_manager.undo_description,
        "redoDescription": self._undo_manager.redo_description
    })
```

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_undo_redo.py
"""Tests for undo/redo manager."""

import pytest
from anki_template_designer.services.undo_redo_manager import UndoRedoManager


class TestUndoRedo:
    def test_initial_state(self):
        manager = UndoRedoManager()
        assert not manager.can_undo
        assert not manager.can_redo
    
    def test_single_undo(self):
        manager = UndoRedoManager()
        manager.push_state({"a": 1}, {"a": 2}, "Change a")
        
        assert manager.can_undo
        assert not manager.can_redo
        
        state = manager.undo()
        assert state == {"a": 1}
        assert not manager.can_undo
        assert manager.can_redo
    
    def test_undo_redo_sequence(self):
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
    
    def test_new_action_clears_redo(self):
        manager = UndoRedoManager()
        manager.push_state({"x": 0}, {"x": 1}, "First")
        manager.push_state({"x": 1}, {"x": 2}, "Second")
        
        manager.undo()  # Back to x=1
        manager.push_state({"x": 1}, {"x": 3}, "New path")
        
        assert not manager.can_redo
    
    def test_max_history(self):
        manager = UndoRedoManager(max_history=3)
        
        for i in range(5):
            manager.push_state({"x": i}, {"x": i+1}, f"Change {i}")
        
        # Should only have last 3 entries
        history = manager.get_history_list()
        assert len(history) == 3
```

Run:
```bash
python -m pytest anki_template_designer/tests/test_undo_redo.py -v
```

### Manual Verification

1. [ ] Open Template Designer
2. [ ] Make several edits
3. [ ] Click Undo - verify state reverts
4. [ ] Click Redo - verify state restores
5. [ ] Verify Undo/Redo buttons enable/disable correctly
6. [ ] Make edit after undo - verify redo becomes unavailable

---

## Success Criteria

- [ ] Undo/redo works correctly
- [ ] History bounded to max size
- [ ] UI updates on state changes
- [ ] Tests pass

---

## Next Step

After successful completion, proceed to [08-ERROR-HANDLING.md](08-ERROR-HANDLING.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
