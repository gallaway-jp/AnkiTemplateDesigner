"""
Visual template builder with drag-and-drop interface
"""

from aqt.qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QFrame, QSplitter, Qt, QDrag, QMimeData, QPixmap,
    QApplication, QMenu, QAction
)
from aqt.theme import theme_manager

from .components import (
    Component, TextFieldComponent, ImageFieldComponent,
    DividerComponent, HeadingComponent, ContainerComponent,
    ConditionalComponent, ComponentType, Alignment
)
from .properties_panel import PropertiesPanel
from .multi_selection import SelectionManager, BulkOperations

from utils.logging_config import get_logger

logger = get_logger('ui.visual_builder')


class ComponentPalette(QWidget):
    """Palette of draggable components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """
        Initialize the component palette user interface.
        
        Creates the palette widget with:
        - Header label
        - List widget showing draggable component types
        - Instructions for drag-and-drop usage
        
        Components can be dragged onto the template canvas to build layouts.
        """
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>Component Palette</b>"))
        
        # Component list
        self.component_list = QListWidget()
        self.component_list.setDragEnabled(True)
        self.component_list.setMaximumWidth(200)
        
        # Add component types
        components = [
            ("Text Field", ComponentType.TEXT_FIELD),
            ("Image Field", ComponentType.IMAGE_FIELD),
            ("Divider", ComponentType.DIVIDER),
            ("Heading", ComponentType.HEADING),
            ("Container", ComponentType.CONTAINER),
            ("Conditional", ComponentType.CONDITIONAL),
        ]
        
        for name, comp_type in components:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, comp_type)
            self.component_list.addItem(item)
        
        layout.addWidget(self.component_list)
        
        # Instructions
        instructions = QLabel(
            "Drag components onto the canvas to build your template.\n\n"
            "Components will be rendered in the order they appear."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        layout.addWidget(instructions)


class CanvasComponent(QFrame):
    """Visual representation of a component on the canvas"""
    
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.component = component
        self.is_selected = False
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMinimumHeight(40)
        
        layout = QVBoxLayout(self)
        
        # Component type label
        type_label = self._get_type_label()
        self.label = QLabel(type_label)
        self.label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.label)
        
        # Field name if applicable
        if component.field_name:
            field_label = QLabel(f"Field: {component.field_name}")
            field_label.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(field_label)
        
        self.update_style()
    
    def _get_type_label(self):
        type_names = {
            ComponentType.TEXT_FIELD: "📝 Text Field",
            ComponentType.IMAGE_FIELD: "🖼️ Image Field",
            ComponentType.DIVIDER: "📏 Divider",
            ComponentType.HEADING: "📌 Heading",
            ComponentType.CONTAINER: "📦 Container",
            ComponentType.CONDITIONAL: "🔀 Conditional",
        }
        return type_names.get(self.component.type, "Unknown")
    
    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QFrame:hover {
                    background-color: #eeeeee;
                    border: 1px solid #999;
                }
            """)
    
    def select(self):
        self.is_selected = True
        self.update_style()
    
    def deselect(self):
        self.is_selected = False
        self.update_style()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Notify parent canvas
            parent = self.parent()
            while parent and not isinstance(parent, TemplateCanvas):
                parent = parent.parent()
            if parent:
                parent.select_component(self)
        super().mousePressEvent(event)


class TemplateCanvas(QScrollArea):
    """Canvas for building the template visually"""
    
    def __init__(self, parent=None, on_selection_change=None):
        super().__init__(parent)
        self.on_selection_change = on_selection_change
        self.components = []
        self.selected_component = None
        
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        
        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Canvas area
        self.canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.canvas_layout.setSpacing(10)
        
        # Empty state
        self.empty_label = QLabel(
            "Drag components here to start building your template.\n\n"
            "Right-click on components for more options."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #999;
            font-size: 14px;
            padding: 50px;
            border: 2px dashed #ccc;
            border-radius: 8px;
            background-color: #fafafa;
        """)
        self.canvas_layout.addWidget(self.empty_label)
        
        container_layout.addWidget(self.canvas_widget)
        self.setWidget(container)
        
        self.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ccc;
                background-color: white;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        # Get component type from mime data
        comp_type_str = event.mimeData().text()
        
        # Create component based on type
        component = self._create_component(comp_type_str)
        if component:
            self.add_component(component)
            event.acceptProposedAction()
    
    def _create_component(self, type_str):
        """Create a component from type string"""
        try:
            comp_type = ComponentType(type_str)
            
            if comp_type == ComponentType.TEXT_FIELD:
                return TextFieldComponent("Front")
            elif comp_type == ComponentType.IMAGE_FIELD:
                return ImageFieldComponent("Image")
            elif comp_type == ComponentType.DIVIDER:
                return DividerComponent()
            elif comp_type == ComponentType.HEADING:
                return HeadingComponent("Title")
            elif comp_type == ComponentType.CONTAINER:
                return ContainerComponent()
            elif comp_type == ComponentType.CONDITIONAL:
                return ConditionalComponent("Extra")
        except (ValueError, TypeError, KeyError) as e:
            logger.debug(f"Failed to create component from type '{type_str}': {e}")
        return None
    
    def add_component(self, component):
        """Add a component to the canvas"""
        # Hide empty label
        if self.empty_label.isVisible():
            self.empty_label.hide()
        
        # Create visual representation
        canvas_comp = CanvasComponent(component, self.canvas_widget)
        canvas_comp.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        canvas_comp.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(canvas_comp, pos)
        )
        
        self.canvas_layout.addWidget(canvas_comp)
        self.components.append(canvas_comp)
        
        # Auto-select new component
        self.select_component(canvas_comp)
    
    def remove_component(self, canvas_comp):
        """Remove a component from canvas"""
        if canvas_comp in self.components:
            self.components.remove(canvas_comp)
            self.canvas_layout.removeWidget(canvas_comp)
            canvas_comp.deleteLater()
            
            # Show empty label if no components
            if not self.components:
                self.empty_label.show()
            
            # Clear selection
            if self.selected_component == canvas_comp:
                self.selected_component = None
                if self.on_selection_change:
                    self.on_selection_change(None)
    
    def select_component(self, canvas_comp):
        """Select a component"""
        # Deselect previous
        if self.selected_component:
            self.selected_component.deselect()
        
        # Select new
        self.selected_component = canvas_comp
        canvas_comp.select()
        
        # Notify
        if self.on_selection_change:
            self.on_selection_change(canvas_comp.component)
    
    def show_context_menu(self, canvas_comp, pos):
        """Show context menu for component"""
        menu = QMenu(self)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.remove_component(canvas_comp))
        menu.addAction(delete_action)
        
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_component(canvas_comp))
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        move_up_action = QAction("Move Up", self)
        move_up_action.triggered.connect(lambda: self.move_component_up(canvas_comp))
        menu.addAction(move_up_action)
        
        move_down_action = QAction("Move Down", self)
        move_down_action.triggered.connect(lambda: self.move_component_down(canvas_comp))
        menu.addAction(move_down_action)
        
        menu.exec(canvas_comp.mapToGlobal(pos))
    
    def duplicate_component(self, canvas_comp):
        """Duplicate a component"""
        new_component = canvas_comp.component.clone()
        self.add_component(new_component)
    
    def move_component_up(self, canvas_comp):
        """Move component up in order"""
        index = self.components.index(canvas_comp)
        if index > 0:
            self.components[index], self.components[index - 1] = \
                self.components[index - 1], self.components[index]
            self.canvas_layout.removeWidget(canvas_comp)
            self.canvas_layout.insertWidget(index - 1, canvas_comp)
    
    def move_component_down(self, canvas_comp):
        """Move component down in order"""
        index = self.components.index(canvas_comp)
        if index < len(self.components) - 1:
            self.components[index], self.components[index + 1] = \
                self.components[index + 1], self.components[index]
            self.canvas_layout.removeWidget(canvas_comp)
            self.canvas_layout.insertWidget(index + 1, canvas_comp)
    
    def clear(self):
        """Clear all components"""
        for comp in self.components[:]:
            self.remove_component(comp)
    
    def get_components(self):
        """Get all components"""
        return [canvas_comp.component for canvas_comp in self.components]
    
    def set_components(self, components):
        """Set components from a list"""
        self.clear()
        for component in components:
            self.add_component(component)


class VisualTemplateBuilder(QWidget):
    """Main visual template builder widget"""
    
    def __init__(self, parent=None, on_change_callback=None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback
        
        # Multi-selection support
        self.selection_manager = SelectionManager()
        self.bulk_operations = BulkOperations()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Add alignment toolbar
        self._add_alignment_toolbar(main_layout)
        
        # Horizontal layout for splitter
        layout = QHBoxLayout()
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Component palette
        self.palette = ComponentPalette()
        self.palette.setMinimumWidth(180)
        self.palette.setMaximumWidth(250)
        # Make list items draggable
        self.palette.component_list.setDragEnabled(True)
        self.palette.component_list.startDrag = self.start_drag
        splitter.addWidget(self.palette)
        
        # Center: Canvas
        self.canvas = TemplateCanvas(on_selection_change=self.on_component_selected)
        self.canvas.setMinimumWidth(400)
        splitter.addWidget(self.canvas)
        
        # Right: Properties panel
        self.properties = PropertiesPanel(on_change=self.on_property_changed)
        self.properties.setMinimumWidth(300)
        self.properties.setMaximumWidth(400)
        splitter.addWidget(self.properties)
        
        # Set splitter sizes - give canvas more space
        total_width = 1100  # Approximate
        splitter.setSizes([200, 600, 300])
        
        layout.addWidget(splitter)
        main_layout.addLayout(layout)
    
    def _add_alignment_toolbar(self, layout):
        """Add toolbar for multi-selection alignment operations"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        
        label = QLabel("<b>Align Selected:</b>")
        toolbar_layout.addWidget(label)
        
        # Alignment buttons
        align_buttons = [
            ("⬅️ Left", self._align_left),
            ("↔️ Center", self._align_center),
            ("➡️ Right", self._align_right),
            ("⬆️ Top", self._align_top),
            ("↕️ Middle", self._align_middle),
            ("⬇️ Bottom", self._align_bottom),
        ]
        
        for btn_text, callback in align_buttons:
            btn = QPushButton(btn_text)
            btn.setMaximumWidth(85)
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addWidget(QLabel("|"))
        
        # Distribute buttons
        dist_label = QLabel("<b>Distribute:</b>")
        toolbar_layout.addWidget(dist_label)
        
        dist_btn_h = QPushButton("↔️ Horizontal")
        dist_btn_h.setMaximumWidth(110)
        dist_btn_h.clicked.connect(self._distribute_horizontal)
        toolbar_layout.addWidget(dist_btn_h)
        
        dist_btn_v = QPushButton("↕️ Vertical")
        dist_btn_v.setMaximumWidth(95)
        dist_btn_v.clicked.connect(self._distribute_vertical)
        toolbar_layout.addWidget(dist_btn_v)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar_widget)
    
    # Alignment callbacks
    def _align_left(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_left(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _align_center(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_center_horizontal(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _align_right(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_right(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _align_top(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_top(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _align_middle(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_center_vertical(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _align_bottom(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 2:
            return
        self.bulk_operations.align_bottom(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _distribute_horizontal(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 3:
            return
        self.bulk_operations.distribute_horizontal(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def _distribute_vertical(self):
        selected = self.selection_manager.get_selected()
        if len(selected) < 3:
            return
        self.bulk_operations.distribute_vertical(selected)
        self.canvas.update()
        if self.on_change_callback:
            self.on_change_callback()
    
    def start_drag(self, supported_actions):
        """Start dragging a component from palette"""
        item = self.palette.component_list.currentItem()
        if item:
            comp_type = item.data(Qt.ItemDataRole.UserRole)
            
            drag = QDrag(self.palette.component_list)
            mime_data = QMimeData()
            mime_data.setText(comp_type.value)
            drag.setMimeData(mime_data)
            
            drag.exec(Qt.DropAction.CopyAction)
    
    def on_component_selected(self, component):
        """
        Handle component selection from canvas.
        
        Args:
            component: Selected Component object or None
        """
        self.properties.set_component(component)
    
    def on_property_changed(self):
        """
        Handle property changes from the properties panel.
        
        Triggers the change callback to notify parent widgets that
        component properties have been modified.
        """
        # Trigger change callback
        if self.on_change_callback:
            self.on_change_callback()
    
    def get_components(self):
        """
        Get all components from the canvas.
        
        Returns:
            List[Component]: List of all components on the canvas
        """
        return self.canvas.get_components()
    
    def set_components(self, components):
        """
        Set components on the canvas.
        
        Args:
            components (List[Component]): List of components to display
        """
        self.canvas.set_components(components)
    
    def clear(self):
        """
        Clear all components from the canvas.
        
        Removes all components, resetting the canvas to an empty state.
        """
        self.canvas.clear()
