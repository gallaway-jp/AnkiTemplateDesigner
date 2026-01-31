"""
Undo/Redo Manager for Template Designer.

Plan 07: Implements a state-based undo/redo system with observer pattern
for UI updates.
"""

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Callable, List
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class HistoryEntry(Generic[T]):
    """Represents a single entry in the undo/redo history."""
    state_before: T
    state_after: T
    description: str


HistoryListener = Callable[[str, bool, bool], None]  # (description, can_undo, can_redo)


class UndoRedoManager(Generic[T]):
    """
    Manages undo/redo history for state changes.
    
    Uses a state-based approach where each entry stores the complete
    state before and after a change. This is simpler and more reliable
    than command-based patterns for template editing.
    
    Example usage:
        manager = UndoRedoManager[dict](max_history=100)
        
        # When user makes a change
        old_state = get_current_state()
        # ... apply change ...
        new_state = get_current_state()
        manager.push_state(old_state, new_state, "Changed text color")
        
        # Undo
        if manager.can_undo:
            state = manager.undo()
            apply_state(state)
        
        # Redo
        if manager.can_redo:
            state = manager.redo()
            apply_state(state)
    """
    
    def __init__(self, max_history: int = 100) -> None:
        """
        Initialize the undo/redo manager.
        
        Args:
            max_history: Maximum number of history entries to keep.
                        Oldest entries are removed when limit is exceeded.
        """
        self._history: List[HistoryEntry[T]] = []
        self._current_index: int = -1  # Points to current position in history
        self._max_history: int = max_history
        self._listeners: List[HistoryListener] = []
        
        logger.debug(f"UndoRedoManager initialized with max_history={max_history}")
    
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
        """Get description of the action that would be undone."""
        if self.can_undo:
            return self._history[self._current_index].description
        return None
    
    @property
    def redo_description(self) -> Optional[str]:
        """Get description of the action that would be redone."""
        if self.can_redo:
            return self._history[self._current_index + 1].description
        return None
    
    @property
    def history_size(self) -> int:
        """Get current number of history entries."""
        return len(self._history)
    
    def push_state(self, state_before: T, state_after: T, description: str) -> None:
        """
        Record a state change in history.
        
        This clears any redo history (entries after current position)
        and adds the new entry. If max_history is exceeded, the oldest
        entry is removed.
        
        Args:
            state_before: State before the change (deep copied)
            state_after: State after the change (deep copied)
            description: Human-readable description of the change
        """
        # Clear redo history (any entries after current position)
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
            logger.debug("Cleared redo history")
        
        # Create new entry with deep copies to avoid reference issues
        entry = HistoryEntry(
            state_before=deepcopy(state_before),
            state_after=deepcopy(state_after),
            description=description
        )
        
        # Add to history
        self._history.append(entry)
        self._current_index = len(self._history) - 1
        
        # Trim if exceeding max history
        if len(self._history) > self._max_history:
            excess = len(self._history) - self._max_history
            self._history = self._history[excess:]
            self._current_index -= excess
            logger.debug(f"Trimmed {excess} oldest history entries")
        
        logger.debug(f"Pushed state: '{description}' (index={self._current_index}, total={len(self._history)})")
        
        self._notify_listeners(description)
    
    def undo(self) -> Optional[T]:
        """
        Undo the last action.
        
        Returns:
            The state before the undone action, or None if nothing to undo.
        """
        if not self.can_undo:
            logger.debug("Nothing to undo")
            return None
        
        entry = self._history[self._current_index]
        self._current_index -= 1
        
        logger.debug(f"Undo: '{entry.description}' (index now {self._current_index})")
        
        self._notify_listeners(f"Undo: {entry.description}")
        
        return deepcopy(entry.state_before)
    
    def redo(self) -> Optional[T]:
        """
        Redo the last undone action.
        
        Returns:
            The state after the redone action, or None if nothing to redo.
        """
        if not self.can_redo:
            logger.debug("Nothing to redo")
            return None
        
        self._current_index += 1
        entry = self._history[self._current_index]
        
        logger.debug(f"Redo: '{entry.description}' (index now {self._current_index})")
        
        self._notify_listeners(f"Redo: {entry.description}")
        
        return deepcopy(entry.state_after)
    
    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1
        
        logger.debug("History cleared")
        
        self._notify_listeners("History cleared")
    
    def get_history_list(self) -> List[str]:
        """
        Get list of action descriptions in history order.
        
        Returns:
            List of descriptions from oldest to newest.
        """
        return [entry.description for entry in self._history]
    
    def add_listener(self, listener: HistoryListener) -> None:
        """
        Add a listener to be notified of history changes.
        
        The listener receives: (description, can_undo, can_redo)
        
        Args:
            listener: Callback function to be notified
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
            logger.debug(f"Added history listener (total={len(self._listeners)})")
    
    def remove_listener(self, listener: HistoryListener) -> None:
        """
        Remove a previously added listener.
        
        Args:
            listener: The listener to remove
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
            logger.debug(f"Removed history listener (total={len(self._listeners)})")
    
    def _notify_listeners(self, description: str) -> None:
        """Notify all listeners of a history change."""
        for listener in self._listeners:
            try:
                listener(description, self.can_undo, self.can_redo)
            except Exception as e:
                logger.error(f"Error notifying history listener: {e}")
