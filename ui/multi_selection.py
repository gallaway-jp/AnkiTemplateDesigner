"""
Multi-selection functionality for visual builder.

Enables selecting and manipulating multiple components simultaneously.
"""

from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import QPen, QBrush, QColor
from typing import List, Set, Optional, Dict, Any
from .components import Component


class SelectionManager(QObject):
    """
    Manager for multi-component selection.
    
    Tracks selected components and provides bulk operations.
    """
    
    # Signals
    selection_changed = pyqtSignal(list)  # List of selected components
    
    def __init__(self):
        """Initialize selection manager."""
        super().__init__()
        
        self._selected_components: Set[Component] = set()
        self._selection_mode = SelectionMode.REPLACE
    
    def select_component(self, component: Component, mode: 'SelectionMode' = None):
        """
        Select a component.
        
        Args:
            component: Component to select
            mode: Selection mode (REPLACE, ADD, REMOVE, TOGGLE)
        """
        if mode is None:
            mode = self._selection_mode
        
        if mode == SelectionMode.REPLACE:
            self._selected_components.clear()
            self._selected_components.add(component)
        
        elif mode == SelectionMode.ADD:
            self._selected_components.add(component)
        
        elif mode == SelectionMode.REMOVE:
            self._selected_components.discard(component)
        
        elif mode == SelectionMode.TOGGLE:
            if component in self._selected_components:
                self._selected_components.remove(component)
            else:
                self._selected_components.add(component)
        
        self.selection_changed.emit(self.get_selected_components())
    
    def select_multiple(self, components: List[Component], mode: 'SelectionMode' = None):
        """
        Select multiple components.
        
        Args:
            components: List of components to select
            mode: Selection mode
        """
        if mode is None:
            mode = self._selection_mode
        
        if mode == SelectionMode.REPLACE:
            self._selected_components.clear()
            self._selected_components.update(components)
        
        elif mode == SelectionMode.ADD:
            self._selected_components.update(components)
        
        elif mode == SelectionMode.REMOVE:
            for component in components:
                self._selected_components.discard(component)
        
        self.selection_changed.emit(self.get_selected_components())
    
    def clear_selection(self):
        """Clear all selections."""
        self._selected_components.clear()
        self.selection_changed.emit([])
    
    def get_selected_components(self) -> List[Component]:
        """Get list of selected components."""
        return list(self._selected_components)
    
    def is_selected(self, component: Component) -> bool:
        """Check if component is selected."""
        return component in self._selected_components
    
    def get_selection_count(self) -> int:
        """Get number of selected components."""
        return len(self._selected_components)
    
    def get_selection_bounds(self) -> Optional[QRectF]:
        """
        Get bounding rectangle of all selected components.
        
        Returns:
            QRectF or None if no selection
        """
        if not self._selected_components:
            return None
        
        min_x = min(c.x for c in self._selected_components)
        min_y = min(c.y for c in self._selected_components)
        max_x = max(c.x + c.width for c in self._selected_components)
        max_y = max(c.y + c.height for c in self._selected_components)
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)


class SelectionMode:
    """Selection mode constants."""
    REPLACE = 'replace'  # Replace current selection
    ADD = 'add'          # Add to selection (Shift+Click)
    REMOVE = 'remove'    # Remove from selection
    TOGGLE = 'toggle'    # Toggle selection state (Ctrl+Click)


class SelectionRectangle(QGraphicsRectItem):
    """
    Visual selection rectangle for drag-selection.
    
    Shows a rubber-band rectangle during drag selection.
    """
    
    def __init__(self, parent=None):
        """Initialize selection rectangle."""
        super().__init__(parent)
        
        # Styling
        pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
        self.setPen(pen)
        
        brush = QBrush(QColor(0, 120, 215, 30))
        self.setBrush(brush)
        
        self.setZValue(1000)  # Always on top
        self.hide()
    
    def start_selection(self, x: float, y: float):
        """
        Start drag selection.
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        self.setRect(x, y, 0, 0)
        self.show()
    
    def update_selection(self, x: float, y: float):
        """
        Update selection rectangle.
        
        Args:
            x: Current X coordinate
            y: Current Y coordinate
        """
        rect = self.rect()
        width = x - rect.x()
        height = y - rect.y()
        
        # Handle negative dimensions (dragging left/up)
        if width < 0:
            rect.setX(x)
            width = -width
        
        if height < 0:
            rect.setY(y)
            height = -height
        
        rect.setWidth(width)
        rect.setHeight(height)
        self.setRect(rect)
    
    def end_selection(self) -> QRectF:
        """
        End drag selection.
        
        Returns:
            QRectF: Final selection rectangle
        """
        rect = self.rect()
        self.hide()
        return rect


class BulkOperations:
    """
    Bulk operations for multiple selected components.
    
    Provides alignment, distribution, and group manipulation.
    """
    
    @staticmethod
    def align_left(components: List[Component]):
        """
        Align components to leftmost edge.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        min_x = min(c.x for c in components)
        
        for component in components:
            component.x = min_x
    
    @staticmethod
    def align_center_horizontal(components: List[Component]):
        """
        Align components to horizontal center.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        # Calculate center X
        min_x = min(c.x for c in components)
        max_x = max(c.x + c.width for c in components)
        center_x = (min_x + max_x) / 2
        
        for component in components:
            component.x = center_x - (component.width / 2)
    
    @staticmethod
    def align_right(components: List[Component]):
        """
        Align components to rightmost edge.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        max_x = max(c.x + c.width for c in components)
        
        for component in components:
            component.x = max_x - component.width
    
    @staticmethod
    def align_top(components: List[Component]):
        """
        Align components to topmost edge.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        min_y = min(c.y for c in components)
        
        for component in components:
            component.y = min_y
    
    @staticmethod
    def align_center_vertical(components: List[Component]):
        """
        Align components to vertical center.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        # Calculate center Y
        min_y = min(c.y for c in components)
        max_y = max(c.y + c.height for c in components)
        center_y = (min_y + max_y) / 2
        
        for component in components:
            component.y = center_y - (component.height / 2)
    
    @staticmethod
    def align_bottom(components: List[Component]):
        """
        Align components to bottommost edge.
        
        Args:
            components: List of components to align
        """
        if not components:
            return
        
        max_y = max(c.y + c.height for c in components)
        
        for component in components:
            component.y = max_y - component.height
    
    @staticmethod
    def distribute_horizontal(components: List[Component]):
        """
        Distribute components evenly horizontally.
        
        Args:
            components: List of components to distribute
        """
        if len(components) < 3:
            return
        
        # Sort by X position
        sorted_components = sorted(components, key=lambda c: c.x)
        
        # Calculate spacing
        min_x = sorted_components[0].x
        max_x = sorted_components[-1].x + sorted_components[-1].width
        total_width = sum(c.width for c in sorted_components)
        available_space = max_x - min_x - total_width
        spacing = available_space / (len(sorted_components) - 1)
        
        # Distribute
        current_x = min_x
        for component in sorted_components:
            component.x = current_x
            current_x += component.width + spacing
    
    @staticmethod
    def distribute_vertical(components: List[Component]):
        """
        Distribute components evenly vertically.
        
        Args:
            components: List of components to distribute
        """
        if len(components) < 3:
            return
        
        # Sort by Y position
        sorted_components = sorted(components, key=lambda c: c.y)
        
        # Calculate spacing
        min_y = sorted_components[0].y
        max_y = sorted_components[-1].y + sorted_components[-1].height
        total_height = sum(c.height for c in sorted_components)
        available_space = max_y - min_y - total_height
        spacing = available_space / (len(sorted_components) - 1)
        
        # Distribute
        current_y = min_y
        for component in sorted_components:
            component.y = current_y
            current_y += component.height + spacing
    
    @staticmethod
    def set_same_width(components: List[Component], width: Optional[float] = None):
        """
        Set all components to same width.
        
        Args:
            components: List of components
            width: Width to set (None = use first component's width)
        """
        if not components:
            return
        
        if width is None:
            width = components[0].width
        
        for component in components:
            component.width = width
    
    @staticmethod
    def set_same_height(components: List[Component], height: Optional[float] = None):
        """
        Set all components to same height.
        
        Args:
            components: List of components
            height: Height to set (None = use first component's height)
        """
        if not components:
            return
        
        if height is None:
            height = components[0].height
        
        for component in components:
            component.height = height
    
    @staticmethod
    def set_same_size(components: List[Component]):
        """
        Set all components to same size (width and height).
        
        Args:
            components: List of components
        """
        if not components:
            return
        
        width = components[0].width
        height = components[0].height
        
        for component in components:
            component.width = width
            component.height = height
    
    @staticmethod
    def apply_property(components: List[Component], property_name: str, value: Any):
        """
        Apply a property value to all components.
        
        Args:
            components: List of components
            property_name: Name of property to set
            value: Value to set
        """
        for component in components:
            if hasattr(component, property_name):
                setattr(component, property_name, value)
