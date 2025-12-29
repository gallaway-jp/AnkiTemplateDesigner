"""
Properties panel for editing component properties
"""

from typing import Optional
from aqt.qt import (
    QWidget, QVBoxLayout, QFormLayout, QScrollArea,
    QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QColorDialog, QGroupBox, QHBoxLayout, Qt, QSlider
)

from .components import Component, Alignment


class PropertiesPanel(QWidget):
    """Panel for editing component properties"""
    
    def __init__(self, parent=None, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.current_component = None
        self.updating = False  # Prevent recursive updates
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>Properties</b>"))
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(350)
        
        # Properties container
        self.props_widget = QWidget()
        self.props_layout = QVBoxLayout(self.props_widget)
        
        # Empty state
        self.empty_label = QLabel("Select a component to edit its properties")
        self.empty_label.setStyleSheet("color: #999; padding: 20px;")
        self.props_layout.addWidget(self.empty_label)
        
        # Component-specific properties will be added dynamically
        self.field_name_edit = None
        self.controls = {}
        
        self.props_layout.addStretch()
        
        scroll.setWidget(self.props_widget)
        layout.addWidget(scroll)
    
    def set_component(self, component: Optional[Component]) -> None:
        """
        Set the component to edit.
        
        Args:
            component (Optional[Component]): Component to display properties for,
                                           or None to show empty state
        """
        self.current_component = component
        self.rebuild_ui()
    
    def rebuild_ui(self):
        """
        Rebuild the properties panel for the current component.
        
        Dynamically generates appropriate controls based on the component
        type and its available properties. Clears existing controls and
        creates new ones.
        
        Property groups shown:
        - Field settings (for components with field_name)
        - Layout properties (width, height, margins, padding)
        - Constraint properties (if use_constraints enabled)
        - Spacing properties
        - Text properties (font, color, alignment)
        - Style properties (background, borders)
        
        Called when:
        - Component selection changes
        - Component type changes
        - Constraint mode toggles
        """
        self._clear_widgets()
        
        if not self.current_component:
            self._show_empty_state()
            return
        
        self.updating = True
        
        self._build_field_settings()
        self._build_layout_properties()
        self._build_constraint_properties()
        self._build_spacing_properties()
        self._build_text_properties()
        self._build_style_properties()
        
        self.props_layout.addStretch()
        self.updating = False
    
    def _clear_widgets(self):
        """
        Clear all property widgets from the panel.
        
        Removes and deletes all widgets from the properties layout,
        preparing for new controls to be added.
        """
        while self.props_layout.count():
            item = self.props_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.controls = {}
    
    def _show_empty_state(self):
        """
        Display empty state message when no component is selected.
        
        Shows a placeholder message instructing the user to select
        a component to view and edit its properties.
        """
        self.empty_label = QLabel("Select a component to edit its properties")
        self.empty_label.setStyleSheet("color: #999; padding: 20px;")
        self.props_layout.addWidget(self.empty_label)
    
    def _build_field_settings(self):
        """
        Build field name editor controls.
        
        Creates a text input for editing the Anki field name that this
        component displays. Only shown for components that have a field_name
        attribute (TextFieldComponent, ImageFieldComponent, etc.).
        """
        comp = self.current_component
        if not comp.field_name:
            return
        
        field_group = self._create_group("Field Settings")
        field_layout = field_group.layout()
        
        self.field_name_edit = QLineEdit(comp.field_name)
        self.field_name_edit.textChanged.connect(self._on_field_name_changed)
        field_layout.addRow("Field Name:", self.field_name_edit)
        
        self.props_layout.addWidget(field_group)
    
    def _build_layout_properties(self):
        """Build width/height editors"""
        comp = self.current_component
        layout_group = self._create_group("Layout")
        layout_layout = layout_group.layout()
        
        self.controls['width'] = QLineEdit(str(comp.width))
        self.controls['width'].textChanged.connect(self._on_width_changed)
        layout_layout.addRow("Width:", self.controls['width'])
        
        self.controls['height'] = QLineEdit(str(comp.height))
        self.controls['height'].textChanged.connect(self._on_height_changed)
        layout_layout.addRow("Height:", self.controls['height'])
        
        self.props_layout.addWidget(layout_group)
    
    def _build_constraint_properties(self):
        """Build constraint controls if component supports constraints"""
        comp = self.current_component
        if not hasattr(comp, 'use_constraints'):
            return
        
        constraints_group = self._create_group("Constraints")
        constraints_layout = constraints_group.layout()
        
        self.controls['use_constraints'] = QCheckBox()
        self.controls['use_constraints'].setChecked(comp.use_constraints)
        self.controls['use_constraints'].stateChanged.connect(self._on_use_constraints_changed)
        constraints_layout.addRow("Use Constraints:", self.controls['use_constraints'])
        
        # Horizontal bias
        self.controls['h_bias'] = QSlider(Qt.Orientation.Horizontal)
        self.controls['h_bias'].setMinimum(0)
        self.controls['h_bias'].setMaximum(100)
        self.controls['h_bias'].setValue(int(comp.constraint_horizontal_bias * 100))
        self.controls['h_bias'].valueChanged.connect(self._on_h_bias_changed)
        constraints_layout.addRow("Horizontal Bias:", self.controls['h_bias'])
        
        # Vertical bias
        self.controls['v_bias'] = QSlider(Qt.Orientation.Horizontal)
        self.controls['v_bias'].setMinimum(0)
        self.controls['v_bias'].setMaximum(100)
        self.controls['v_bias'].setValue(int(comp.constraint_vertical_bias * 100))
        self.controls['v_bias'].valueChanged.connect(self._on_v_bias_changed)
        constraints_layout.addRow("Vertical Bias:", self.controls['v_bias'])
        
        # Quick constraint buttons
        constraint_btn_container = QWidget()
        constraint_btn_layout = QHBoxLayout(constraint_btn_container)
        constraint_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        center_btn = QPushButton("Center in Parent")
        center_btn.clicked.connect(self._on_center_in_parent)
        constraint_btn_layout.addWidget(center_btn)
        
        match_parent_btn = QPushButton("Match Parent")
        match_parent_btn.clicked.connect(self._on_match_parent)
        constraint_btn_layout.addWidget(match_parent_btn)
        
        constraints_layout.addRow("Quick:", constraint_btn_container)
        
        self.props_layout.addWidget(constraints_group)
    
    def _build_spacing_properties(self):
        """Build margin and padding controls"""
        comp = self.current_component
        spacing_group = self._create_group("Spacing")
        spacing_layout = spacing_group.layout()
        
        margin_widget = self._create_spacing_controls('margin', comp, self._on_margin_changed)
        spacing_layout.addRow("Margin (px):", margin_widget)
        
        padding_widget = self._create_spacing_controls('padding', comp, self._on_padding_changed)
        spacing_layout.addRow("Padding (px):", padding_widget)
        
        self.props_layout.addWidget(spacing_group)
    
    def _build_text_properties(self):
        """Build text formatting controls"""
        comp = self.current_component
        text_group = self._create_group("Text")
        text_layout = text_group.layout()
        
        self.controls['font_family'] = QComboBox()
        self.controls['font_family'].addItems([
            "Arial, sans-serif",
            "Georgia, serif",
            "Courier New, monospace",
            "Verdana, sans-serif",
            "Times New Roman, serif",
            "Comic Sans MS, cursive"
        ])
        self.controls['font_family'].setCurrentText(comp.font_family)
        self.controls['font_family'].currentTextChanged.connect(self._on_font_family_changed)
        text_layout.addRow("Font:", self.controls['font_family'])
        
        self.controls['font_size'] = QSpinBox()
        self.controls['font_size'].setRange(8, 72)
        self.controls['font_size'].setValue(comp.font_size)
        self.controls['font_size'].valueChanged.connect(self._on_font_size_changed)
        text_layout.addRow("Size (px):", self.controls['font_size'])
        
        self.controls['font_weight'] = QComboBox()
        self.controls['font_weight'].addItems(["normal", "bold", "lighter", "bolder"])
        self.controls['font_weight'].setCurrentText(comp.font_weight)
        self.controls['font_weight'].currentTextChanged.connect(self._on_font_weight_changed)
        text_layout.addRow("Weight:", self.controls['font_weight'])
        
        self.controls['text_align'] = QComboBox()
        self.controls['text_align'].addItems(["left", "center", "right", "justify"])
        self.controls['text_align'].setCurrentText(comp.text_align.value)
        self.controls['text_align'].currentTextChanged.connect(self._on_text_align_changed)
        text_layout.addRow("Align:", self.controls['text_align'])
        
        color_widget = self._create_color_picker(
            'color',
            comp.color,
            self._on_color_changed,
            self._pick_text_color
        )
        text_layout.addRow("Color:", color_widget)
        
        self.props_layout.addWidget(text_group)
    
    def _build_style_properties(self):
        """Build background and border controls"""
        comp = self.current_component
        style_group = self._create_group("Background & Border")
        style_layout = style_group.layout()
        
        bg_widget = self._create_color_picker(
            'background_color',
            comp.background_color,
            self._on_bg_color_changed,
            self._pick_bg_color
        )
        style_layout.addRow("Background:", bg_widget)
        
        self.controls['border_width'] = QSpinBox()
        self.controls['border_width'].setRange(0, 20)
        self.controls['border_width'].setValue(comp.border_width)
        self.controls['border_width'].valueChanged.connect(self._on_border_changed)
        style_layout.addRow("Border Width:", self.controls['border_width'])
        
        self.controls['border_radius'] = QSpinBox()
        self.controls['border_radius'].setRange(0, 50)
        self.controls['border_radius'].setValue(comp.border_radius)
        self.controls['border_radius'].valueChanged.connect(self._on_border_radius_changed)
        style_layout.addRow("Border Radius:", self.controls['border_radius'])
        
        self.props_layout.addWidget(style_group)
    
    def _create_spacing_controls(self, property_prefix, component, callback):
        """Create TRBL (Top-Right-Bottom-Left) spacing controls.
        
        Args:
            property_prefix: 'margin' or 'padding'
            component: Component with spacing properties
            callback: Callback function when value changes
        
        Returns:
            Widget container with 4 spinboxes
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for side in ['top', 'right', 'bottom', 'left']:
            prop_name = f'{property_prefix}_{side}'
            value = getattr(component, prop_name)
            
            layout.addWidget(QLabel(f"{side[0].upper()}:"))
            
            spinbox = QSpinBox()
            spinbox.setRange(0, 200)
            spinbox.setValue(value)
            spinbox.valueChanged.connect(callback)
            self.controls[prop_name] = spinbox
            
            layout.addWidget(spinbox)
        
        return container
    
    def _create_color_picker(self, property_name, current_value, on_change_callback, on_pick_callback):
        """Create a color picker widget (text field + button).
        
        Args:
            property_name: Name for controls dict
            current_value: Current color value
            on_change_callback: Called when text changes
            on_pick_callback: Called when pick button clicked
        
        Returns:
            Widget container with color controls
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        color_edit = QLineEdit(current_value)
        color_edit.textChanged.connect(on_change_callback)
        self.controls[property_name] = color_edit
        
        pick_btn = QPushButton("Pick")
        pick_btn.clicked.connect(on_pick_callback)
        
        layout.addWidget(color_edit)
        layout.addWidget(pick_btn)
        
        return container
    
    def _create_group(self, title):
        """Create a property group"""
        group = QGroupBox(title)
        layout = QFormLayout()
        group.setLayout(layout)
        return group
    
    def _notify_change(self):
        """Notify that a property changed"""
        if not self.updating and self.on_change:
            self.on_change()
    
    # Event handlers
    def _on_field_name_changed(self, text):
        if self.current_component:
            self.current_component.field_name = text
            self._notify_change()
    
    def _on_width_changed(self, text):
        if self.current_component:
            self.current_component.width = text
            self._notify_change()
    
    def _on_height_changed(self, text):
        if self.current_component:
            self.current_component.height = text
            self._notify_change()
    
    def _on_margin_changed(self):
        if self.current_component:
            self.current_component.margin_top = self.controls['margin_top'].value()
            self.current_component.margin_right = self.controls['margin_right'].value()
            self.current_component.margin_bottom = self.controls['margin_bottom'].value()
            self.current_component.margin_left = self.controls['margin_left'].value()
            self._notify_change()
    
    def _on_padding_changed(self):
        if self.current_component:
            self.current_component.padding_top = self.controls['padding_top'].value()
            self.current_component.padding_right = self.controls['padding_right'].value()
            self.current_component.padding_bottom = self.controls['padding_bottom'].value()
            self.current_component.padding_left = self.controls['padding_left'].value()
            self._notify_change()
    
    def _on_font_family_changed(self, text):
        if self.current_component:
            self.current_component.font_family = text
            self._notify_change()
    
    def _on_font_size_changed(self, value):
        if self.current_component:
            self.current_component.font_size = value
            self._notify_change()
    
    def _on_font_weight_changed(self, text):
        if self.current_component:
            self.current_component.font_weight = text
            self._notify_change()
    
    def _on_use_constraints_changed(self, state):
        if self.current_component:
            self.current_component.use_constraints = bool(state)
            self._notify_change()
    
    def _on_h_bias_changed(self, value):
        if self.current_component:
            self.current_component.constraint_horizontal_bias = value / 100.0
            self._notify_change()
    
    def _on_v_bias_changed(self, value):
        if self.current_component:
            self.current_component.constraint_vertical_bias = value / 100.0
            self._notify_change()
    
    def _on_center_in_parent(self):
        """Apply center in parent constraints"""
        if self.current_component:
            from .constraints import ConstraintHelper, ConstraintType, ConstraintTarget
            
            # Clear existing position constraints
            self.current_component.constraints = []
            
            # Add center constraints
            comp_id = id(self.current_component)
            constraints = ConstraintHelper.create_centered_constraints(comp_id)
            self.current_component.constraints = [c.to_dict() for c in constraints]
            
            self._notify_change()
    
    def _on_match_parent(self):
        """Apply match parent constraints"""
        if self.current_component:
            from .constraints import ConstraintHelper
            
            # Clear existing constraints
            self.current_component.constraints = []
            
            # Add match parent constraints
            comp_id = id(self.current_component)
            constraints = ConstraintHelper.create_match_parent_constraints(comp_id, margin=8)
            self.current_component.constraints = [c.to_dict() for c in constraints]
            
            self._notify_change()
    
    def _on_text_align_changed(self, text):
        if self.current_component:
            self.current_component.text_align = Alignment(text)
            self._notify_change()
    
    def _on_color_changed(self, text):
        if self.current_component:
            self.current_component.color = text
            self._notify_change()
    
    def _on_bg_color_changed(self, text):
        if self.current_component:
            self.current_component.background_color = text
            self._notify_change()
    
    def _on_border_changed(self):
        if self.current_component:
            self.current_component.border_width = self.controls['border_width'].value()
            self._notify_change()
    
    def _on_border_radius_changed(self, value):
        if self.current_component:
            self.current_component.border_radius = value
            self._notify_change()
    
    def _pick_text_color(self):
        """Open color picker for text color"""
        if self.current_component:
            from aqt.qt import QColor
            initial_color = QColor(self.current_component.color)
            color = QColorDialog.getColor(initial_color, self)
            if color.isValid():
                self.controls['color'].setText(color.name())
    
    def _pick_bg_color(self):
        """Open color picker for background color"""
        if self.current_component:
            from aqt.qt import QColor
            initial_color = QColor(self.current_component.background_color) \
                if self.current_component.background_color != "transparent" \
                else QColor("#ffffff")
            color = QColorDialog.getColor(initial_color, self)
            if color.isValid():
                self.controls['background_color'].setText(color.name())
