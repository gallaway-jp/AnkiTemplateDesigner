"""
Design Surface - Enhanced canvas with zoom, pan, and grid
Inspired by Android Studio's DesignSurface
"""

import sys
import os
from aqt.qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPainter, QColor, QPen, QBrush, QRect, QPoint,
    Qt, QWheelEvent, QMouseEvent, QPaintEvent,
    QToolBar, QAction, QSlider, QLabel, QComboBox, QFrame
)
from typing import Optional, List, Callable
from .components import Component
from .layout_strategies import LayoutStrategy, FlowLayoutStrategy, ConstraintLayoutStrategy
from .grid import GridSettings

# Add parent directory to path for imports when needed
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import LayoutDefaults
from utils.logging_config import get_logger

logger = get_logger('ui.design_surface')


class DesignSurfaceCanvas(QWidget):
    """
    Canvas widget with zoom, pan, and grid support.
    Renders components with visual feedback.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.components: List[Component] = []
        self.selected_component: Optional[Component] = None
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        
        # Grid system - simple implementation for QWidget
        self.grid_size = GridSettings.DEFAULT_GRID_SIZE
        self.show_grid = False
        self.snap_to_grid = False
        
        self.canvas_width = LayoutDefaults.CARD_WIDTH
        self.canvas_height = LayoutDefaults.CARD_HEIGHT
        
        # Panning state
        self.is_panning = False
        self.last_mouse_pos = QPoint()
        
        # Component bounds cache
        self.component_bounds = {}
        
        # Layout strategy
        self.layout_strategy: LayoutStrategy = FlowLayoutStrategy()
        
        self.setMinimumSize(600, 800)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def set_components(self, components: List[Component]):
        """Set components to render"""
        self.components = components
        self.update_component_bounds()
        self.update()
    
    def set_zoom(self, zoom: float):
        """Set zoom level (0.1 to 4.0)"""
        self.zoom_level = max(
            LayoutDefaults.MIN_ZOOM, 
            min(LayoutDefaults.MAX_ZOOM, zoom)
        )
        self.update()
    
    def zoom_in(self):
        """Zoom in"""
        self.set_zoom(self.zoom_level * LayoutDefaults.ZOOM_STEP)
    
    def zoom_out(self):
        """Zoom out"""
        self.set_zoom(self.zoom_level / LayoutDefaults.ZOOM_STEP)
    
    def zoom_to_fit(self):
        """Zoom to fit all content"""
        if not self.components:
            self.set_zoom(1.0)
            return
        
        # Calculate required zoom to fit content
        available_width = self.width() - 40
        available_height = self.height() - 40
        
        zoom_x = available_width / self.canvas_width
        zoom_y = available_height / self.canvas_height
        
        self.set_zoom(min(zoom_x, zoom_y))
        self.pan_offset = QPoint(0, 0)
        self.update()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.set_zoom(1.0)
        self.pan_offset = QPoint(0, 0)
        self.update()
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.show_grid = not self.show_grid
        self.update()
    
    def toggle_snap_to_grid(self):
        """Toggle snap to grid"""
        self.snap_to_grid = not self.snap_to_grid
        self.update()
    
    def set_grid_size(self, size: int):
        """Set grid size"""
        self.grid_size = size
        self.update()
    
    def snap_point_to_grid(self, x: int, y: int) -> tuple:
        """Snap a point to the grid if snap is enabled"""
        if self.snap_to_grid:
            snapped_x = round(x / self.grid_size) * self.grid_size
            snapped_y = round(y / self.grid_size) * self.grid_size
            return (snapped_x, snapped_y)
        return (x, y)
    
    def snap_rect_to_grid(self, x: int, y: int, width: int, height: int) -> tuple:
        """Snap a rectangle to the grid if snap is enabled"""
        if self.snap_to_grid:
            snapped_x = round(x / self.grid_size) * self.grid_size
            snapped_y = round(y / self.grid_size) * self.grid_size
            return (snapped_x, snapped_y, width, height)
        return (x, y, width, height)
    
    def update_component_bounds(self):
        """Calculate bounds for each component using appropriate layout strategy"""
        self.component_bounds.clear()
        
        # Determine which layout strategy to use
        use_constraints = any(
            hasattr(comp, 'use_constraints') and comp.use_constraints
            for comp in self.components
        )
        
        # Select strategy
        if use_constraints:
            self.layout_strategy = ConstraintLayoutStrategy()
        else:
            self.layout_strategy = FlowLayoutStrategy()
        
        # Calculate bounds using strategy
        self.component_bounds = self.layout_strategy.calculate_bounds(
            self.components,
            self.canvas_width,
            self.canvas_height
        )
    
    def paintEvent(self, event: QPaintEvent):
        """Paint the canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(250, 250, 250))
        
        # Apply transformations
        painter.translate(self.width() / 2, 20)
        painter.translate(self.pan_offset)
        painter.scale(self.zoom_level, self.zoom_level)
        painter.translate(-self.canvas_width / 2, 0)
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter)
        
        # Draw canvas background
        canvas_rect = QRect(0, 0, self.canvas_width, self.canvas_height)
        painter.fillRect(canvas_rect, Qt.GlobalColor.white)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(canvas_rect)
        
        # Draw components
        for component in self.components:
            self._draw_component(painter, component)
        
        painter.end()
    
    def _draw_grid(self, painter: QPainter):
        """Draw grid lines"""
        if not self.show_grid:
            return
        
        # Draw grid lines
        pen = QPen(QColor(220, 220, 220))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Vertical lines
        x = 0
        while x <= self.canvas_width:
            painter.drawLine(int(x), 0, int(x), int(self.canvas_height))
            x += self.grid_size
        
        # Horizontal lines
        y = 0
        while y <= self.canvas_height:
            painter.drawLine(0, int(y), int(self.canvas_width), int(y))
            y += self.grid_size
    
    def _draw_component(self, painter: QPainter, component: Component):
        """Draw a component with proper styling"""
        comp_id = id(component)
        if comp_id not in self.component_bounds:
            return
        
        bounds = self.component_bounds[comp_id]
        
        # Determine if selected
        is_selected = component is self.selected_component
        
        # Draw component background
        bg_color = QColor(255, 255, 255)
        if hasattr(component, 'background_color') and component.background_color:
            try:
                bg_color = QColor(component.background_color)
            except (ValueError, TypeError) as e:
                logger.debug(f"Invalid background color '{component.background_color}': {e}")
                bg_color = QColor(255, 255, 255)  # Default white
        
        painter.fillRect(bounds, bg_color)
        
        # Draw selection highlight or normal border
        if is_selected:
            # Selection highlight
            painter.fillRect(bounds, QColor(200, 230, 255, 100))
            painter.setPen(QPen(QColor(33, 150, 243), 2))
        else:
            painter.setPen(QPen(QColor(180, 180, 180), 1))
        
        # Draw border if component has one
        if hasattr(component, 'border_width') and component.border_width > 0:
            border_color = QColor(component.border_color) if hasattr(component, 'border_color') else QColor(0, 0, 0)
            painter.setPen(QPen(border_color, component.border_width))
        
        painter.drawRect(bounds)
        
        # Draw component content based on type
        self._draw_component_content(painter, component, bounds, is_selected)
    
    def _draw_component_content(self, painter: QPainter, component: Component, bounds: QRect, is_selected: bool):
        """Draw component-specific content"""
        from .components import ComponentType
        
        # Set text color
        text_color = QColor(33, 150, 243) if is_selected else QColor(60, 60, 60)
        if hasattr(component, 'color') and component.color:
            try:
                text_color = QColor(component.color)
            except (ValueError, TypeError) as e:
                logger.debug(f"Invalid text color '{component.color}': {e}")
                text_color = QColor(33, 150, 243) if is_selected else QColor(60, 60, 60)
        
        painter.setPen(QPen(text_color))
        
        # Component type label
        type_name = component.type.value.replace('_', ' ').title()
        
        # Draw based on component type
        if component.type == ComponentType.TEXT_FIELD:
            # Text field - show field name and sample text
            if hasattr(component, 'field_name') and component.field_name:
                label = f"{{{{ {component.field_name} }}}}"
            else:
                label = type_name
            painter.drawText(bounds.adjusted(8, 5, -8, -5), 
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, 
                           label)
        
        elif component.type == ComponentType.IMAGE_FIELD:
            # Image field - show placeholder
            if hasattr(component, 'field_name') and component.field_name:
                label = f"[Image: {component.field_name}]"
            else:
                label = "[Image]"
            painter.drawText(bounds, Qt.AlignmentFlag.AlignCenter, label)
        
        elif component.type == ComponentType.DIVIDER:
            # Divider - draw a line
            y = bounds.center().y()
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.drawLine(bounds.left() + 10, y, bounds.right() - 10, y)
        
        elif component.type == ComponentType.HEADING:
            # Heading - larger text
            if hasattr(component, 'field_name') and component.field_name:
                label = f"{{{{ {component.field_name} }}}}"
            else:
                label = type_name
            
            # Use larger font for headings
            font = painter.font()
            font.setPointSize(14)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(bounds.adjusted(8, 5, -8, -5),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                           label)
        
        elif component.type == ComponentType.CONTAINER:
            # Container - draw border and label
            painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine))
            painter.drawRect(bounds.adjusted(2, 2, -2, -2))
            painter.drawText(bounds.adjusted(8, 5, -8, -5),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                           "[Container]")
        
        elif component.type == ComponentType.CONDITIONAL:
            # Conditional - show condition
            if hasattr(component, 'field_name') and component.field_name:
                label = f"{{{{# {component.field_name} }}}} ... {{{{/ {component.field_name} }}}}"
            else:
                label = "[Conditional]"
            painter.drawText(bounds.adjusted(8, 5, -8, -5),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                           label)
        else:
            # Generic component
            painter.drawText(bounds.adjusted(8, 5, -8, -5),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                           type_name)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.AltModifier):
            # Start panning
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.LeftButton:
            # Check for component selection
            component = self._get_component_at(event.pos())
            if component:
                self.select_component(component)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.MiddleButton or event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle wheel event for zooming"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def _get_component_at(self, pos: QPoint) -> Optional[Component]:
        """Get component at screen position"""
        # Transform screen coordinates to canvas coordinates
        # This is a simplified version - should match paintEvent transform
        canvas_x = (pos.x() - self.width() / 2 - self.pan_offset.x()) / self.zoom_level + self.canvas_width / 2
        canvas_y = (pos.y() - 20 - self.pan_offset.y()) / self.zoom_level
        
        # Check which component contains this point
        for component in reversed(self.components):  # Check from top to bottom
            comp_id = id(component)
            if comp_id in self.component_bounds:
                bounds = self.component_bounds[comp_id]
                if bounds.contains(int(canvas_x), int(canvas_y)):
                    return component
        
        return None
    
    def select_component(self, component: Optional[Component]):
        """Select a component"""
        self.selected_component = component
        self.update()
    
    def get_selected_component(self) -> Optional[Component]:
        """Get selected component"""
        return self.selected_component


class DesignSurface(QWidget):
    """
    Main design surface with toolbar and canvas.
    Provides zoom controls, grid toggle, and view options.
    """
    
    def __init__(self, parent=None,
                 on_selection_change: Optional[Callable[[Optional[Component]], None]] = None):
        super().__init__(parent)
        self.on_selection_change = on_selection_change
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create canvas first (needed for toolbar connections)
        self.canvas = DesignSurfaceCanvas()
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Zoom controls
        zoom_out_action = QAction("Zoom Out (-)", self)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(150)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        toolbar.addWidget(self.zoom_slider)
        
        zoom_in_action = QAction("Zoom In (+)", self)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        toolbar.addWidget(self.zoom_label)
        
        toolbar.addSeparator()
        
        # Zoom presets
        zoom_combo = QComboBox()
        zoom_combo.addItems(["Fit", "25%", "50%", "75%", "100%", "150%", "200%"])
        zoom_combo.setCurrentText("100%")
        zoom_combo.currentTextChanged.connect(self.on_zoom_preset_selected)
        toolbar.addWidget(zoom_combo)
        
        toolbar.addSeparator()
        
        # Grid controls
        grid_action = QAction("Show Grid", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self.canvas.toggle_grid)
        toolbar.addAction(grid_action)
        
        snap_action = QAction("Snap to Grid", self)
        snap_action.setCheckable(True)
        snap_action.setChecked(False)
        snap_action.triggered.connect(self.canvas.toggle_snap_to_grid)
        toolbar.addAction(snap_action)
        
        # Grid size selector
        grid_size_label = QLabel("Grid:")
        toolbar.addWidget(grid_size_label)
        
        grid_size_combo = QComboBox()
        grid_size_combo.addItems(["4px", "8px", "16px", "32px"])
        grid_size_combo.setCurrentText("8px")
        grid_size_combo.currentTextChanged.connect(self.on_grid_size_changed)
        toolbar.addWidget(grid_size_combo)
        
        layout.addWidget(toolbar)
        
        # Canvas in scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        layout.addWidget(scroll)
    
    def on_zoom_slider_changed(self, value: int):
        """Handle zoom slider change"""
        zoom = value / 100.0
        self.canvas.set_zoom(zoom)
        self.zoom_label.setText(f"{value}%")
    
    def on_zoom_preset_selected(self, text: str):
        """Handle zoom preset selection"""
        if text == "Fit":
            self.canvas.zoom_to_fit()
            self.zoom_slider.setValue(int(self.canvas.zoom_level * 100))
        else:
            try:
                value = int(text.replace('%', ''))
                self.zoom_slider.setValue(value)
            except ValueError:
                pass
    
    def on_grid_size_changed(self, text: str):
        """Handle grid size change"""
        try:
            size = int(text.replace('px', ''))
            self.canvas.set_grid_size(size)
        except ValueError:
            pass
    
    def set_components(self, components: List[Component]):
        """Set components to display"""
        self.canvas.set_components(components)
    
    def select_component(self, component: Optional[Component]):
        """Select a component"""
        self.canvas.select_component(component)
        if self.on_selection_change:
            self.on_selection_change(component)
    
    def get_selected_component(self) -> Optional[Component]:
        """Get selected component"""
        return self.canvas.get_selected_component()
