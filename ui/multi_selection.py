"""Multi-selection and selection management for AnkiTemplateDesigner."""

from typing import List, Set, Optional
from enum import Enum


class SelectionMode(Enum):
    """Modes for component selection."""
    SINGLE = "single"
    MULTIPLE = "multiple"
    RANGE = "range"


class SelectionManager:
    """Manages component selection."""
    
    def __init__(self, mode: SelectionMode = SelectionMode.SINGLE):
        self.mode = mode
        self.selected: Set[str] = set()
    
    def select(self, component_id: str) -> None:
        """Select a component."""
        if self.mode == SelectionMode.SINGLE:
            self.selected.clear()
        self.selected.add(component_id)
    
    def deselect(self, component_id: str) -> None:
        """Deselect a component."""
        self.selected.discard(component_id)
    
    def get_selected(self) -> List[str]:
        """Get list of selected components."""
        return list(self.selected)


class BulkOperations:
    """Handles bulk operations on selected components."""
    
    @staticmethod
    def delete(component_ids: List[str]) -> None:
        """Delete multiple components."""
        pass
    
    @staticmethod
    def move(component_ids: List[str], dx: float, dy: float) -> None:
        """Move multiple components."""
        pass
    
    @staticmethod
    def resize(component_ids: List[str], width: float, height: float) -> None:
        """Resize multiple components."""
        pass


__all__ = ['SelectionManager', 'SelectionMode', 'BulkOperations']
