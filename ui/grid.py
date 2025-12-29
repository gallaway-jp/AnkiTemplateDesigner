"""
Grid and snap-to-grid functionality for visual builder.

Provides visual grid overlay and snap-to-grid positioning.
"""

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor
from typing import Tuple
from config.constants import LayoutDefaults


class GridSettings:
    """Grid configuration settings."""
    
    # Grid size in pixels
    GRID_SIZE_SMALL = 5
    GRID_SIZE_MEDIUM = 10
    GRID_SIZE_LARGE = 20
    
    # Default grid size
    DEFAULT_GRID_SIZE = GRID_SIZE_MEDIUM
    
    # Grid colors
    GRID_COLOR_LIGHT = QColor(220, 220, 220)  # Light gray
    GRID_COLOR_DARK = QColor(100, 100, 100)   # Dark gray
    
    # Grid styles
    GRID_STYLE_DOTS = 'dots'
    GRID_STYLE_LINES = 'lines'
    GRID_STYLE_CROSS = 'cross'
    
    DEFAULT_GRID_STYLE = GRID_STYLE_LINES


class Grid:
    """
    Visual grid for design surface.
    
    Provides grid overlay and snap-to-grid functionality.
    """
    
    def __init__(self, scene: QGraphicsScene):
        """
        Initialize grid.
        
        Args:
            scene: Graphics scene to draw grid on
        """
        self.scene = scene
        self.grid_size = GridSettings.DEFAULT_GRID_SIZE
        self.grid_style = GridSettings.DEFAULT_GRID_STYLE
        self.grid_color = GridSettings.GRID_COLOR_LIGHT
        self.enabled = False
        self.visible = False
        
        self._grid_items = []
    
    def set_grid_size(self, size: int):
        """
        Set grid size.
        
        Args:
            size: Grid size in pixels
        """
        self.grid_size = size
        
        if self.visible:
            self.redraw()
    
    def set_grid_style(self, style: str):
        """
        Set grid style.
        
        Args:
            style: Grid style (dots, lines, cross)
        """
        self.grid_style = style
        
        if self.visible:
            self.redraw()
    
    def set_grid_color(self, color: QColor):
        """
        Set grid color.
        
        Args:
            color: Grid line color
        """
        self.grid_color = color
        
        if self.visible:
            self.redraw()
    
    def toggle_visibility(self):
        """Toggle grid visibility."""
        self.visible = not self.visible
        
        if self.visible:
            self.show()
        else:
            self.hide()
    
    def show(self):
        """Show the grid."""
        self.visible = True
        self.redraw()
    
    def hide(self):
        """Hide the grid."""
        self.visible = False
        self.clear()
    
    def toggle_snap(self):
        """Toggle snap-to-grid."""
        self.enabled = not self.enabled
        return self.enabled
    
    def enable_snap(self):
        """Enable snap-to-grid."""
        self.enabled = True
    
    def disable_snap(self):
        """Disable snap-to-grid."""
        self.enabled = False
    
    def is_snap_enabled(self) -> bool:
        """Check if snap-to-grid is enabled."""
        return self.enabled
    
    def snap_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """
        Snap coordinates to grid.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (snapped_x, snapped_y)
        """
        if not self.enabled:
            return (x, y)
        
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        
        return (snapped_x, snapped_y)
    
    def snap_point(self, point: QPointF) -> QPointF:
        """
        Snap a QPointF to grid.
        
        Args:
            point: Point to snap
            
        Returns:
            QPointF: Snapped point
        """
        x, y = self.snap_to_grid(point.x(), point.y())
        return QPointF(x, y)
    
    def snap_rect(self, rect: QRectF) -> QRectF:
        """
        Snap a rectangle to grid.
        
        Args:
            rect: Rectangle to snap
            
        Returns:
            QRectF: Snapped rectangle
        """
        x, y = self.snap_to_grid(rect.x(), rect.y())
        
        # Optionally snap width/height to grid multiples
        width = round(rect.width() / self.grid_size) * self.grid_size
        height = round(rect.height() / self.grid_size) * self.grid_size
        
        return QRectF(x, y, width, height)
    
    def redraw(self):
        """Redraw the grid."""
        self.clear()
        
        if not self.visible:
            return
        
        # Get scene bounds
        scene_rect = self.scene.sceneRect()
        
        if self.grid_style == GridSettings.GRID_STYLE_LINES:
            self._draw_grid_lines(scene_rect)
        elif self.grid_style == GridSettings.GRID_STYLE_DOTS:
            self._draw_grid_dots(scene_rect)
        elif self.grid_style == GridSettings.GRID_STYLE_CROSS:
            self._draw_grid_cross(scene_rect)
    
    def _draw_grid_lines(self, rect: QRectF):
        """Draw grid as lines."""
        pen = QPen(self.grid_color, 1, Qt.PenStyle.SolidLine)
        
        # Vertical lines
        x = rect.left()
        while x <= rect.right():
            line = QGraphicsLineItem(x, rect.top(), x, rect.bottom())
            line.setPen(pen)
            line.setZValue(-1000)  # Behind everything
            self.scene.addItem(line)
            self._grid_items.append(line)
            
            x += self.grid_size
        
        # Horizontal lines
        y = rect.top()
        while y <= rect.bottom():
            line = QGraphicsLineItem(rect.left(), y, rect.right(), y)
            line.setPen(pen)
            line.setZValue(-1000)
            self.scene.addItem(line)
            self._grid_items.append(line)
            
            y += self.grid_size
    
    def _draw_grid_dots(self, rect: QRectF):
        """Draw grid as dots."""
        pen = QPen(self.grid_color, 2, Qt.PenStyle.SolidLine)
        
        y = rect.top()
        while y <= rect.bottom():
            x = rect.left()
            while x <= rect.right():
                # Draw a small dot
                line = QGraphicsLineItem(x, y, x, y)
                line.setPen(pen)
                line.setZValue(-1000)
                self.scene.addItem(line)
                self._grid_items.append(line)
                
                x += self.grid_size
            
            y += self.grid_size
    
    def _draw_grid_cross(self, rect: QRectF):
        """Draw grid as crosses."""
        pen = QPen(self.grid_color, 1, Qt.PenStyle.SolidLine)
        cross_size = 2
        
        y = rect.top()
        while y <= rect.bottom():
            x = rect.left()
            while x <= rect.right():
                # Horizontal line
                h_line = QGraphicsLineItem(
                    x - cross_size, y,
                    x + cross_size, y
                )
                h_line.setPen(pen)
                h_line.setZValue(-1000)
                self.scene.addItem(h_line)
                self._grid_items.append(h_line)
                
                # Vertical line
                v_line = QGraphicsLineItem(
                    x, y - cross_size,
                    x, y + cross_size
                )
                v_line.setPen(pen)
                v_line.setZValue(-1000)
                self.scene.addItem(v_line)
                self._grid_items.append(v_line)
                
                x += self.grid_size
            
            y += self.grid_size
    
    def clear(self):
        """Clear all grid items."""
        for item in self._grid_items:
            self.scene.removeItem(item)
        
        self._grid_items.clear()


class SnapHelper:
    """
    Helper for snapping components to grid and other components.
    
    Provides smart snapping with visual feedback.
    """
    
    def __init__(self, grid: Grid):
        """
        Initialize snap helper.
        
        Args:
            grid: Grid instance
        """
        self.grid = grid
        self.snap_threshold = 5  # Pixels
    
    def snap_component_position(
        self,
        x: float,
        y: float,
        other_components: list = None
    ) -> Tuple[float, float]:
        """
        Snap component position to grid and nearby components.
        
        Args:
            x: Component X position
            y: Component Y position
            other_components: List of other components to snap to
            
        Returns:
            Tuple of (snapped_x, snapped_y)
        """
        # First, snap to grid if enabled
        if self.grid.is_snap_enabled():
            x, y = self.grid.snap_to_grid(x, y)
        
        # Then, snap to other components if close enough
        if other_components:
            x = self._snap_to_nearby_x(x, other_components)
            y = self._snap_to_nearby_y(y, other_components)
        
        return (x, y)
    
    def _snap_to_nearby_x(self, x: float, components: list) -> float:
        """Snap X coordinate to nearby component edges."""
        for component in components:
            # Left edge
            if abs(x - component.x) < self.snap_threshold:
                return component.x
            
            # Right edge
            comp_right = component.x + component.width
            if abs(x - comp_right) < self.snap_threshold:
                return comp_right
        
        return x
    
    def _snap_to_nearby_y(self, y: float, components: list) -> float:
        """Snap Y coordinate to nearby component edges."""
        for component in components:
            # Top edge
            if abs(y - component.y) < self.snap_threshold:
                return component.y
            
            # Bottom edge
            comp_bottom = component.y + component.height
            if abs(y - comp_bottom) < self.snap_threshold:
                return comp_bottom
        
        return y
