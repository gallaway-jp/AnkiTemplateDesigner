"""
Selection service for managing component selection.

Plan 12: Implements component selection, multi-selection, and selection events.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("anki_template_designer.services.selection_service")


@dataclass
class SelectionState:
    """Represents the current selection state.
    
    Attributes:
        selected_ids: Set of selected component IDs.
        primary_id: The primary (last selected) component ID.
        selection_order: Order in which components were selected.
    """
    selected_ids: Set[str] = field(default_factory=set)
    primary_id: Optional[str] = None
    selection_order: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "selectedIds": list(self.selected_ids),
            "primaryId": self.primary_id,
            "selectionOrder": self.selection_order,
            "count": len(self.selected_ids)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelectionState":
        """Create from dictionary."""
        return cls(
            selected_ids=set(data.get("selectedIds", [])),
            primary_id=data.get("primaryId"),
            selection_order=data.get("selectionOrder", [])
        )
    
    def clear(self) -> None:
        """Clear all selection."""
        self.selected_ids.clear()
        self.primary_id = None
        self.selection_order.clear()
    
    def is_empty(self) -> bool:
        """Check if selection is empty."""
        return len(self.selected_ids) == 0
    
    def is_selected(self, component_id: str) -> bool:
        """Check if a component is selected."""
        return component_id in self.selected_ids
    
    def count(self) -> int:
        """Get number of selected components."""
        return len(self.selected_ids)


# Type alias for selection change listeners
SelectionChangeListener = Callable[[SelectionState, SelectionState], None]


class SelectionService:
    """Service for managing component selection.
    
    Features:
    - Single selection
    - Multi-selection (Ctrl+click)
    - Selection range (Shift+click)
    - Selection persistence
    - Selection change events
    
    Example:
        service = SelectionService()
        
        # Listen for changes
        def on_change(old_state, new_state):
            print(f"Selection changed: {new_state.selected_ids}")
        service.add_listener(on_change)
        
        # Select components
        service.select("component-1")
        service.add_to_selection("component-2")
    """
    
    def __init__(self) -> None:
        """Initialize the selection service."""
        self._state = SelectionState()
        self._listeners: List[SelectionChangeListener] = []
        self._component_order: List[str] = []  # For shift-select range
        
        logger.debug("SelectionService initialized")
    
    @property
    def state(self) -> SelectionState:
        """Get current selection state (read-only copy)."""
        return SelectionState(
            selected_ids=self._state.selected_ids.copy(),
            primary_id=self._state.primary_id,
            selection_order=self._state.selection_order.copy()
        )
    
    @property
    def selected_ids(self) -> List[str]:
        """Get list of selected component IDs."""
        return list(self._state.selected_ids)
    
    @property
    def primary_id(self) -> Optional[str]:
        """Get the primary (last selected) component ID."""
        return self._state.primary_id
    
    @property
    def count(self) -> int:
        """Get number of selected components."""
        return self._state.count()
    
    def is_selected(self, component_id: str) -> bool:
        """Check if a component is selected.
        
        Args:
            component_id: The component ID to check.
            
        Returns:
            True if the component is selected.
        """
        return self._state.is_selected(component_id)
    
    def is_empty(self) -> bool:
        """Check if selection is empty.
        
        Returns:
            True if nothing is selected.
        """
        return self._state.is_empty()
    
    def add_listener(self, listener: SelectionChangeListener) -> None:
        """Add a selection change listener.
        
        Args:
            listener: Function called with (old_state, new_state) on changes.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
            logger.debug(f"Added selection listener, total: {len(self._listeners)}")
    
    def remove_listener(self, listener: SelectionChangeListener) -> None:
        """Remove a selection change listener.
        
        Args:
            listener: The listener to remove.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
            logger.debug(f"Removed selection listener, total: {len(self._listeners)}")
    
    def _notify_listeners(self, old_state: SelectionState, new_state: SelectionState) -> None:
        """Notify all listeners of selection change.
        
        Args:
            old_state: State before the change.
            new_state: State after the change.
        """
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in selection listener: {e}")
    
    def set_component_order(self, order: List[str]) -> None:
        """Set the component order for range selection.
        
        This should be called when components are rendered to enable
        shift-click range selection.
        
        Args:
            order: List of component IDs in display order.
        """
        self._component_order = order.copy()
        logger.debug(f"Set component order: {len(order)} components")
    
    def select(self, component_id: str) -> bool:
        """Select a single component (replacing current selection).
        
        Args:
            component_id: The component ID to select.
            
        Returns:
            True if selection changed.
        """
        if not component_id:
            return False
        
        old_state = self.state
        
        # Check if this is already the only selection
        if (self._state.selected_ids == {component_id} and 
            self._state.primary_id == component_id):
            return False
        
        self._state.selected_ids = {component_id}
        self._state.primary_id = component_id
        self._state.selection_order = [component_id]
        
        new_state = self.state
        self._notify_listeners(old_state, new_state)
        
        logger.debug(f"Selected: {component_id}")
        return True
    
    def add_to_selection(self, component_id: str) -> bool:
        """Add a component to selection (Ctrl+click behavior).
        
        Args:
            component_id: The component ID to add.
            
        Returns:
            True if selection changed.
        """
        if not component_id:
            return False
        
        if component_id in self._state.selected_ids:
            return False
        
        old_state = self.state
        
        self._state.selected_ids.add(component_id)
        self._state.primary_id = component_id
        self._state.selection_order.append(component_id)
        
        new_state = self.state
        self._notify_listeners(old_state, new_state)
        
        logger.debug(f"Added to selection: {component_id}, total: {self.count}")
        return True
    
    def remove_from_selection(self, component_id: str) -> bool:
        """Remove a component from selection.
        
        Args:
            component_id: The component ID to remove.
            
        Returns:
            True if selection changed.
        """
        if not component_id:
            return False
        
        if component_id not in self._state.selected_ids:
            return False
        
        old_state = self.state
        
        self._state.selected_ids.discard(component_id)
        
        if component_id in self._state.selection_order:
            self._state.selection_order.remove(component_id)
        
        # Update primary to last in order, or None
        if self._state.primary_id == component_id:
            if self._state.selection_order:
                self._state.primary_id = self._state.selection_order[-1]
            else:
                self._state.primary_id = None
        
        new_state = self.state
        self._notify_listeners(old_state, new_state)
        
        logger.debug(f"Removed from selection: {component_id}, remaining: {self.count}")
        return True
    
    def toggle_selection(self, component_id: str) -> bool:
        """Toggle a component's selection state.
        
        Args:
            component_id: The component ID to toggle.
            
        Returns:
            True if component is now selected, False if deselected.
        """
        if self.is_selected(component_id):
            self.remove_from_selection(component_id)
            return False
        else:
            self.add_to_selection(component_id)
            return True
    
    def select_range(self, to_component_id: str) -> bool:
        """Select a range from primary to target (Shift+click behavior).
        
        Uses component_order to determine the range. If no primary
        selection exists, just selects the target.
        
        Args:
            to_component_id: The end component of the range.
            
        Returns:
            True if selection changed.
        """
        if not to_component_id:
            return False
        
        # If no component order or no primary, just select the component
        if not self._component_order or not self._state.primary_id:
            return self.select(to_component_id)
        
        try:
            primary_idx = self._component_order.index(self._state.primary_id)
            target_idx = self._component_order.index(to_component_id)
        except ValueError:
            # Component not in order, just add to selection
            return self.add_to_selection(to_component_id)
        
        old_state = self.state
        
        # Get range indices
        start_idx = min(primary_idx, target_idx)
        end_idx = max(primary_idx, target_idx)
        
        # Select all components in range
        range_ids = self._component_order[start_idx:end_idx + 1]
        
        for cid in range_ids:
            self._state.selected_ids.add(cid)
            if cid not in self._state.selection_order:
                self._state.selection_order.append(cid)
        
        # Keep primary as is (the anchor for the range)
        
        new_state = self.state
        self._notify_listeners(old_state, new_state)
        
        logger.debug(f"Selected range: {len(range_ids)} components")
        return True
    
    def select_all(self, component_ids: List[str]) -> bool:
        """Select all specified components.
        
        Args:
            component_ids: List of component IDs to select.
            
        Returns:
            True if selection changed.
        """
        if not component_ids:
            return False
        
        old_state = self.state
        
        self._state.selected_ids = set(component_ids)
        self._state.selection_order = list(component_ids)
        self._state.primary_id = component_ids[-1] if component_ids else None
        
        new_state = self.state
        
        if old_state.selected_ids != new_state.selected_ids:
            self._notify_listeners(old_state, new_state)
            logger.debug(f"Selected all: {len(component_ids)} components")
            return True
        
        return False
    
    def clear(self) -> bool:
        """Clear all selection.
        
        Returns:
            True if selection changed.
        """
        if self._state.is_empty():
            return False
        
        old_state = self.state
        self._state.clear()
        new_state = self.state
        
        self._notify_listeners(old_state, new_state)
        
        logger.debug("Selection cleared")
        return True
    
    def set_selection(self, component_ids: List[str], primary_id: Optional[str] = None) -> bool:
        """Set selection to specific components.
        
        Args:
            component_ids: List of component IDs to select.
            primary_id: Optional primary component (defaults to last in list).
            
        Returns:
            True if selection changed.
        """
        old_state = self.state
        
        self._state.selected_ids = set(component_ids)
        self._state.selection_order = list(component_ids)
        
        if primary_id and primary_id in self._state.selected_ids:
            self._state.primary_id = primary_id
        elif component_ids:
            self._state.primary_id = component_ids[-1]
        else:
            self._state.primary_id = None
        
        new_state = self.state
        
        if (old_state.selected_ids != new_state.selected_ids or
            old_state.primary_id != new_state.primary_id):
            self._notify_listeners(old_state, new_state)
            logger.debug(f"Set selection: {len(component_ids)} components")
            return True
        
        return False
    
    def move_selection(self, direction: str) -> Optional[str]:
        """Move selection in a direction (keyboard navigation).
        
        Args:
            direction: "next", "prev", "first", or "last"
            
        Returns:
            The newly selected component ID, or None if no change.
        """
        if not self._component_order:
            return None
        
        current_idx = -1
        if self._state.primary_id:
            try:
                current_idx = self._component_order.index(self._state.primary_id)
            except ValueError:
                current_idx = -1
        
        new_idx: Optional[int] = None
        
        if direction == "next":
            new_idx = min(current_idx + 1, len(self._component_order) - 1)
        elif direction == "prev":
            new_idx = max(current_idx - 1, 0) if current_idx > 0 else 0
        elif direction == "first":
            new_idx = 0
        elif direction == "last":
            new_idx = len(self._component_order) - 1
        
        if new_idx is not None and 0 <= new_idx < len(self._component_order):
            new_id = self._component_order[new_idx]
            self.select(new_id)
            return new_id
        
        return None
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get selection state as dictionary.
        
        Returns:
            Dictionary representation of selection state.
        """
        return self._state.to_dict()
    
    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore selection from state dictionary.
        
        Args:
            state_dict: Dictionary from get_state_dict().
        """
        old_state = self.state
        self._state = SelectionState.from_dict(state_dict)
        new_state = self.state
        
        if old_state.selected_ids != new_state.selected_ids:
            self._notify_listeners(old_state, new_state)
            logger.debug("Selection state restored")


# Global instance
_selection_service: Optional[SelectionService] = None


def get_selection_service() -> Optional[SelectionService]:
    """Get the global selection service instance.
    
    Returns:
        The SelectionService instance, or None if not initialized.
    """
    return _selection_service


def init_selection_service() -> SelectionService:
    """Initialize the global selection service.
    
    Returns:
        The initialized SelectionService instance.
    """
    global _selection_service
    _selection_service = SelectionService()
    logger.debug("Selection service initialized")
    return _selection_service
