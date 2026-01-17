"""
Issue #52: Selection Clarity Improvements

Visual feedback system for selected components with highlighting,
breadcrumbs, focus indicators, and selection state management.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime


class SelectionMode(Enum):
    """Selection mode types."""
    SINGLE = "single"
    MULTIPLE = "multiple"
    RANGE = "range"


class SelectionState(Enum):
    """Selection state types."""
    IDLE = "idle"
    SELECTING = "selecting"
    SELECTED = "selected"
    MULTI_SELECTED = "multi_selected"


@dataclass
class SelectionItem:
    """A selected item."""
    id: str = ""
    name: str = ""
    type: str = ""
    path: str = ""
    parent_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'parent_id': self.parent_id,
            'properties': self.properties,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class BreadcrumbItem:
    """A breadcrumb in the selection path."""
    id: str = ""
    name: str = ""
    type: str = ""
    level: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'level': self.level
        }


class SelectionManager:
    """
    Manages element selection with visual feedback,
    breadcrumb navigation, and multi-selection support.
    """

    def __init__(self, mode: SelectionMode = SelectionMode.MULTIPLE):
        """
        Initialize selection manager.
        
        Args:
            mode: Selection mode (single, multiple, range)
        """
        self.mode = mode
        self.selected_items: Dict[str, SelectionItem] = {}
        self.selection_state = SelectionState.IDLE
        self.active_item: Optional[str] = None
        self.breadcrumb_path: List[BreadcrumbItem] = []
        self.selection_history: List[Dict[str, SelectionItem]] = []
        self.max_history_size = 50
        self.listeners: List[Callable] = []
        self.focus_item: Optional[str] = None
        self.highlight_color = "#4CAF50"
        self.highlight_enabled = True
        self.last_selected_time: Optional[datetime] = None

    def select_item(self, item: SelectionItem, append: bool = False) -> bool:
        """
        Select an item.
        
        Args:
            item: Item to select
            append: Whether to append to existing selection
            
        Returns:
            True if successful
        """
        # Handle single selection mode
        if self.mode == SelectionMode.SINGLE and not append:
            self._clear_selection()

        # Add item to selection
        self.selected_items[item.id] = item
        self.active_item = item.id
        self.focus_item = item.id
        self.last_selected_time = datetime.now()
        self.selection_state = SelectionState.SELECTED if len(self.selected_items) == 1 else SelectionState.MULTI_SELECTED

        # Update breadcrumb path
        self._update_breadcrumbs(item)

        # Record in history
        self._save_selection_to_history()

        # Notify listeners
        self._notify_listeners('selection_changed', {
            'selected': list(self.selected_items.values()),
            'active': self.active_item
        })

        return True

    def deselect_item(self, item_id: str) -> bool:
        """
        Deselect an item.
        
        Args:
            item_id: ID of item to deselect
            
        Returns:
            True if successful
        """
        if item_id not in self.selected_items:
            return False

        del self.selected_items[item_id]

        # Update state
        if len(self.selected_items) == 0:
            self.selection_state = SelectionState.IDLE
            self.active_item = None
            self.breadcrumb_path.clear()
        else:
            self.selection_state = SelectionState.MULTI_SELECTED
            if self.active_item == item_id:
                self.active_item = list(self.selected_items.keys())[0]
                self._update_breadcrumbs(self.selected_items[self.active_item])

        self._save_selection_to_history()

        self._notify_listeners('selection_changed', {
            'selected': list(self.selected_items.values()),
            'active': self.active_item
        })

        return True

    def clear_selection(self) -> bool:
        """
        Clear all selected items.
        
        Returns:
            True if items were cleared
        """
        if len(self.selected_items) == 0:
            return False

        self._clear_selection()
        self._notify_listeners('selection_cleared', {})
        return True

    def _clear_selection(self) -> None:
        """Internal method to clear selection."""
        self.selected_items.clear()
        self.selection_state = SelectionState.IDLE
        self.active_item = None
        self.breadcrumb_path.clear()
        self._save_selection_to_history()

    def set_active_item(self, item_id: str) -> bool:
        """
        Set the active (focused) item in current selection.
        
        Args:
            item_id: ID of item to make active
            
        Returns:
            True if successful
        """
        if item_id not in self.selected_items:
            return False

        self.active_item = item_id
        self.focus_item = item_id
        self._update_breadcrumbs(self.selected_items[item_id])

        self._notify_listeners('active_item_changed', {
            'active_item_id': item_id,
            'active_item': self.selected_items[item_id].to_dict()
        })

        return True

    def _update_breadcrumbs(self, item: SelectionItem) -> None:
        """Update breadcrumb path for item."""
        self.breadcrumb_path.clear()

        # Parse path to create breadcrumbs
        if item.path:
            path_parts = item.path.split('/')
            for i, part in enumerate(path_parts):
                breadcrumb = BreadcrumbItem(
                    id=f"breadcrumb_{i}",
                    name=part,
                    type="path_component",
                    level=i
                )
                self.breadcrumb_path.append(breadcrumb)

        # Add item as final breadcrumb
        if item.name:
            breadcrumb = BreadcrumbItem(
                id=item.id,
                name=item.name,
                type=item.type,
                level=len(self.breadcrumb_path)
            )
            self.breadcrumb_path.append(breadcrumb)

    def get_selected_items(self) -> List[SelectionItem]:
        """Get list of selected items."""
        return list(self.selected_items.values())

    def get_active_item(self) -> Optional[SelectionItem]:
        """Get the active item."""
        if self.active_item:
            return self.selected_items.get(self.active_item)
        return None

    def get_selection_count(self) -> int:
        """Get number of selected items."""
        return len(self.selected_items)

    def is_selected(self, item_id: str) -> bool:
        """Check if item is selected."""
        return item_id in self.selected_items

    def get_breadcrumbs(self) -> List[BreadcrumbItem]:
        """Get breadcrumb path."""
        return self.breadcrumb_path.copy()

    def navigate_breadcrumb(self, breadcrumb_id: str) -> bool:
        """
        Navigate to breadcrumb location.
        
        Args:
            breadcrumb_id: ID of breadcrumb to navigate to
            
        Returns:
            True if successful
        """
        for breadcrumb in self.breadcrumb_path:
            if breadcrumb.id == breadcrumb_id:
                self._notify_listeners('breadcrumb_navigation', {
                    'breadcrumb': breadcrumb.to_dict(),
                    'level': breadcrumb.level
                })
                return True

        return False

    def set_highlight_color(self, color: str) -> None:
        """
        Set highlight color for selected items.
        
        Args:
            color: Color hex code or name
        """
        self.highlight_color = color
        self._notify_listeners('highlight_color_changed', {
            'color': color
        })

    def set_highlight_enabled(self, enabled: bool) -> None:
        """
        Enable/disable visual highlighting.
        
        Args:
            enabled: Whether to show highlights
        """
        self.highlight_enabled = enabled
        self._notify_listeners('highlight_enabled_changed', {
            'enabled': enabled
        })

    def _save_selection_to_history(self) -> None:
        """Save current selection to history."""
        snapshot = {item_id: item for item_id, item in self.selected_items.items()}
        self.selection_history.append(snapshot)

        if len(self.selection_history) > self.max_history_size:
            self.selection_history = self.selection_history[-self.max_history_size:]

    def undo_selection(self) -> bool:
        """
        Undo to previous selection state.
        
        Returns:
            True if successful
        """
        if len(self.selection_history) < 2:
            return False

        self.selection_history.pop()  # Remove current
        previous = self.selection_history[-1]

        self.selected_items = {item_id: item for item_id, item in previous.items()}

        if self.selected_items:
            self.active_item = list(self.selected_items.keys())[0]
            self.selection_state = SelectionState.SELECTED if len(self.selected_items) == 1 else SelectionState.MULTI_SELECTED
        else:
            self.selection_state = SelectionState.IDLE
            self.active_item = None

        self._notify_listeners('selection_undone', {
            'selected': list(self.selected_items.values())
        })

        return True

    def select_range(self, start_id: str, end_id: str) -> bool:
        """
        Select range of items (requires hierarchical structure).
        
        Args:
            start_id: Starting item ID
            end_id: Ending item ID
            
        Returns:
            True if successful
        """
        if self.mode != SelectionMode.RANGE:
            return False

        if start_id not in self.selected_items or end_id not in self.selected_items:
            return False

        # In a real hierarchical structure, select all items between
        # For now, just ensure both are selected
        self._notify_listeners('range_selected', {
            'start_id': start_id,
            'end_id': end_id,
            'count': len(self.selected_items)
        })

        return True

    def toggle_item(self, item: SelectionItem) -> bool:
        """
        Toggle item selection (select if not selected, deselect if selected).
        
        Args:
            item: Item to toggle
            
        Returns:
            True if now selected, False if now deselected
        """
        if item.id in self.selected_items:
            self.deselect_item(item.id)
            return False
        else:
            self.select_item(item, append=True)
            return True

    def invert_selection(self, all_items: List[SelectionItem]) -> None:
        """
        Invert selection (select unselected, deselect selected).
        
        Args:
            all_items: All available items to choose from
        """
        current_ids = set(self.selected_items.keys())
        all_ids = {item.id for item in all_items}

        self.selected_items.clear()

        for item in all_items:
            if item.id not in current_ids:
                self.selected_items[item.id] = item

        if self.selected_items:
            self.active_item = list(self.selected_items.keys())[0]
            self.selection_state = SelectionState.MULTI_SELECTED
        else:
            self.selection_state = SelectionState.IDLE
            self.active_item = None

        self._save_selection_to_history()

        self._notify_listeners('selection_inverted', {
            'selected': list(self.selected_items.values())
        })

    def select_by_type(self, item_type: str, all_items: List[SelectionItem]) -> int:
        """
        Select all items of a specific type.
        
        Args:
            item_type: Type of items to select
            all_items: All available items
            
        Returns:
            Number of items selected
        """
        count = 0
        for item in all_items:
            if item.type == item_type:
                self.selected_items[item.id] = item
                count += 1

        if self.selected_items:
            self.active_item = list(self.selected_items.keys())[0]
            self.selection_state = SelectionState.MULTI_SELECTED
        else:
            self.selection_state = SelectionState.IDLE
            self.active_item = None

        self._save_selection_to_history()

        self._notify_listeners('selection_by_type', {
            'type': item_type,
            'count': count
        })

        return count

    def set_selection_mode(self, mode: SelectionMode) -> None:
        """
        Change selection mode.
        
        Args:
            mode: New selection mode
        """
        self.mode = mode
        
        # Enforce single selection in single mode
        if mode == SelectionMode.SINGLE and len(self.selected_items) > 1:
            first_id = list(self.selected_items.keys())[0]
            self.selected_items = {first_id: self.selected_items[first_id]}
            self.active_item = first_id

        self._notify_listeners('selection_mode_changed', {
            'mode': mode.value
        })

    def add_listener(self, listener: Callable) -> None:
        """Add event listener."""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        """Remove event listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def _notify_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all listeners of event."""
        for listener in self.listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get selection statistics."""
        return {
            'total_selected': len(self.selected_items),
            'selection_state': self.selection_state.value,
            'selection_mode': self.mode.value,
            'has_active_item': self.active_item is not None,
            'breadcrumb_depth': len(self.breadcrumb_path),
            'history_size': len(self.selection_history),
            'highlight_enabled': self.highlight_enabled
        }

    def export_selection(self) -> Dict[str, Any]:
        """Export current selection state."""
        return {
            'items': [item.to_dict() for item in self.selected_items.values()],
            'active_item': self.active_item,
            'breadcrumbs': [b.to_dict() for b in self.breadcrumb_path],
            'mode': self.mode.value,
            'state': self.selection_state.value,
            'timestamp': datetime.now().isoformat()
        }

    def import_selection(self, data: Dict[str, Any]) -> bool:
        """
        Import selection state.
        
        Args:
            data: Exported selection data
            
        Returns:
            True if successful
        """
        try:
            self.selected_items.clear()

            for item_data in data.get('items', []):
                item = SelectionItem(
                    id=item_data['id'],
                    name=item_data['name'],
                    type=item_data['type'],
                    path=item_data.get('path', ''),
                    parent_id=item_data.get('parent_id'),
                    properties=item_data.get('properties', {})
                )
                self.selected_items[item.id] = item

            self.active_item = data.get('active_item')
            self.mode = SelectionMode(data.get('mode', 'multiple'))

            if self.selected_items:
                self.selection_state = SelectionState.SELECTED if len(self.selected_items) == 1 else SelectionState.MULTI_SELECTED
            else:
                self.selection_state = SelectionState.IDLE

            self._notify_listeners('selection_imported', {
                'count': len(self.selected_items)
            })

            return True

        except Exception:
            return False

    def focus_next(self, all_items: List[SelectionItem]) -> bool:
        """
        Move focus to next item.
        
        Args:
            all_items: List of all available items
            
        Returns:
            True if successful
        """
        if not self.focus_item or not all_items:
            return False

        current_index = -1
        for i, item in enumerate(all_items):
            if item.id == self.focus_item:
                current_index = i
                break

        if current_index == -1 or current_index >= len(all_items) - 1:
            return False

        next_item = all_items[current_index + 1]
        self.focus_item = next_item.id

        self._notify_listeners('focus_changed', {
            'focus_item': next_item.id
        })

        return True

    def focus_previous(self, all_items: List[SelectionItem]) -> bool:
        """
        Move focus to previous item.
        
        Args:
            all_items: List of all available items
            
        Returns:
            True if successful
        """
        if not self.focus_item or not all_items:
            return False

        current_index = -1
        for i, item in enumerate(all_items):
            if item.id == self.focus_item:
                current_index = i
                break

        if current_index <= 0:
            return False

        prev_item = all_items[current_index - 1]
        self.focus_item = prev_item.id

        self._notify_listeners('focus_changed', {
            'focus_item': prev_item.id
        })

        return True
