"""
Visual component classes for drag-and-drop template building
"""

import html
import sys
import os
from functools import lru_cache
from aqt.qt import Qt
from enum import Enum

# Add parent directory to path for imports when needed
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import UIDefaults, ComponentDefaults, LayoutDefaults


class ComponentType(Enum):
    """
    Types of visual components available in the template designer.
    
    Attributes:
        TEXT_FIELD: Displays text from an Anki field using {{FieldName}} syntax
        IMAGE_FIELD: Displays images from a field with img tag
        DIVIDER: Horizontal line separator rendered as <hr>
        CONTAINER: Groups other components (can have children)
        HEADING: Styled heading text (h1-h6)
        BUTTON: Interactive button (reserved for future use)
        CONDITIONAL: Shows content conditionally using {{#Field}}...{{/Field}}
    """
    TEXT_FIELD = "text_field"
    IMAGE_FIELD = "image_field"
    DIVIDER = "divider"
    CONTAINER = "container"
    HEADING = "heading"
    BUTTON = "button"
    CONDITIONAL = "conditional"


class Alignment(Enum):
    """
    Text alignment options for components.
    
    Attributes:
        LEFT: Align text to the left (default for LTR languages)
        CENTER: Center text horizontally
        RIGHT: Align text to the right
        JUSTIFY: Justify text to fill the width
    """
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class Component:
    """
    Base class for all visual template components.
    
    Components are visual building blocks that can be placed on the template
    canvas and converted to HTML/CSS for use in Anki flashcards. They support
    two layout modes:
    
    1. Flow Layout: Traditional top-to-bottom stacking
    2. Constraint Layout: Android-style constraint-based positioning
    
    All components have visual properties (size, color, fonts) and can be
    styled independently. Container and Conditional components can have
    child components, forming a tree structure.
    
    Attributes:
        type (ComponentType): Component type (TEXT_FIELD, IMAGE_FIELD, etc.)
        field_name (str): Anki field name this component displays
        id (int): Unique identifier (set when added to canvas)
        
        width (str): Width with unit ("100%", "200px", "auto")
        height (str): Height with unit
        margin_* (int): Margins in pixels (top, right, bottom, left)
        padding_* (int): Padding in pixels (top, right, bottom, left)
        
        font_family (str): CSS font family
        font_size (int): Font size in pixels
        font_weight (str): "normal", "bold", etc.
        color (str): Text color (hex or named)
        text_align (Alignment): Text alignment enum
        background_color (str): Background color
        
        border_width (int): Border width in pixels
        border_style (str): "solid", "dashed", "dotted", etc.
        border_color (str): Border color
        border_radius (int): Corner radius in pixels
        
        use_constraints (bool): Use constraint layout vs flow layout
        constraints (List[dict]): List of constraint definitions
        constraint_horizontal_bias (float): Horizontal bias (0.0-1.0)
        constraint_vertical_bias (float): Vertical bias (0.0-1.0)
    
    Subclasses:
        TextFieldComponent: Displays text from an Anki field
        ImageFieldComponent: Displays images from a field
        HeadingComponent: Styled heading text (h1-h6)
        DividerComponent: Horizontal line separator
        ContainerComponent: Groups other components (can have children)
        ConditionalComponent: Conditionally shows content (can have children)
    
    Example:
        >>> comp = TextFieldComponent("Question")
        >>> comp.font_size = 24
        >>> comp.color = "#333333"
        >>> comp.text_align = Alignment.CENTER
        >>> html = comp.to_html()
        >>> print(html)
        <div class="text-field">{{Question}}</div>
    """
    
    def __init__(self, component_type, field_name=""):
        self.type = component_type
        self.field_name = field_name
        self.id = None  # Will be set when added to canvas
        
        # Visual properties
        self.width = "100%"
        self.height = "auto"
        self.margin_top = UIDefaults.MARGIN
        self.margin_right = UIDefaults.MARGIN
        self.margin_bottom = UIDefaults.MARGIN
        self.margin_left = UIDefaults.MARGIN
        self.padding_top = UIDefaults.PADDING
        self.padding_right = UIDefaults.PADDING
        self.padding_bottom = UIDefaults.PADDING
        self.padding_left = UIDefaults.PADDING
        
        # Constraint-based positioning (Android Studio style)
        self.use_constraints = True  # Use constraint layout instead of flow layout
        self.constraints = []  # List of constraint dictionaries
        self.constraint_horizontal_bias = LayoutDefaults.DEFAULT_HORIZONTAL_BIAS
        self.constraint_vertical_bias = LayoutDefaults.DEFAULT_VERTICAL_BIAS
        
        # Text properties
        self.font_family = UIDefaults.FONT_FAMILY
        self.font_size = UIDefaults.FONT_SIZE
        self.font_weight = "normal"
        self.font_style = "normal"
        self.text_align = Alignment.CENTER
        self.color = UIDefaults.DEFAULT_TEXT_COLOR
        self.background_color = UIDefaults.DEFAULT_BACKGROUND
        
        # Border properties
        self.border_width = UIDefaults.BORDER_WIDTH
        self.border_style = "solid"
        self.border_color = UIDefaults.DEFAULT_BORDER_COLOR
        self.border_radius = UIDefaults.BORDER_RADIUS
        
        # Layout properties
        self.display = "block"
        self.flex_direction = "column"
        self.justify_content = "flex-start"
        self.align_items = "stretch"
        
    def to_html(self):
        """
        Convert component to HTML markup.
        
        Returns:
            str: HTML representation of the component
        
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError
    
    def to_css(self, selector):
        """
        Generate CSS rules for this component.
        
        Args:
            selector (str): CSS selector to use for the rules
        
        Returns:
            str: CSS rules for this component
        """
        css_parts = []
        
        # Dimensions (with early skip for defaults)
        if self.width != "auto":
            css_parts.append(f"width: {self.width};")
        if self.height != "auto":
            css_parts.append(f"height: {self.height};")
        
        # Margins (single property for efficiency)
        if any([self.margin_top, self.margin_right, self.margin_bottom, self.margin_left]):
            css_parts.append(f"margin: {self.margin_top}px {self.margin_right}px {self.margin_bottom}px {self.margin_left}px;")
        
        # Padding (single property for efficiency)
        if any([self.padding_top, self.padding_right, self.padding_bottom, self.padding_left]):
            css_parts.append(f"padding: {self.padding_top}px {self.padding_right}px {self.padding_bottom}px {self.padding_left}px;")
        
        # Text properties (batch together)
        css_parts.extend([
            f"font-family: {self.font_family};",
            f"font-size: {self.font_size}px;",
            f"font-weight: {self.font_weight};",
            f"font-style: {self.font_style};",
            f"text-align: {self.text_align.value};",
            f"color: {self.color};"
        ])
        
        if self.background_color != "transparent":
            css_parts.append(f"background-color: {self.background_color};")
        
        # Border (combine into single property when possible)
        if self.border_width > 0:
            css_parts.append(f"border: {self.border_width}px {self.border_style} {self.border_color};")
        if self.border_radius > 0:
            css_parts.append(f"border-radius: {self.border_radius}px;")
        
        # Layout
        css_parts.append(f"display: {self.display};")
        
        # Optimized string joining (single join operation)
        return f"{selector} {{\n    " + "\n    ".join(css_parts) + "\n}"
    
    def clone(self):
        """Create a copy of this component"""
        import copy
        return copy.deepcopy(self)


class TextFieldComponent(Component):
    """Component for displaying a text field from the note"""
    
    def __init__(self, field_name="Front"):
        super().__init__(ComponentType.TEXT_FIELD, field_name)
        self.show_label = False
        self.label_text = ""
        
    def to_html(self):
        # Escape all user inputs to prevent XSS
        safe_field_name = html.escape(self.field_name)
        safe_field_lower = html.escape(self.field_name.lower())
        
        html_parts = []
        if self.show_label and self.label_text:
            safe_label = html.escape(self.label_text)
            html_parts.append(f'<div class="field-label">{safe_label}</div>')
        html_parts.append(f'<div class="field-content field-{safe_field_lower}">{{{{{safe_field_name}}}}}</div>')
        return '\n'.join(html_parts)


class ImageFieldComponent(Component):
    """Component for displaying an image field"""
    
    def __init__(self, field_name="Image"):
        super().__init__(ComponentType.IMAGE_FIELD, field_name)
        self.max_width = ComponentDefaults.IMAGE_MAX_WIDTH
        self.max_height = ComponentDefaults.IMAGE_MAX_HEIGHT
        self.object_fit = ComponentDefaults.IMAGE_OBJECT_FIT
        
    def to_html(self):
        # Escape field name to prevent XSS
        safe_field_name = html.escape(self.field_name)
        safe_alt = html.escape(self.field_name)
        return f'<div class="image-container"><img src="{{{{{safe_field_name}}}}}" class="field-image" alt="{safe_alt}"></div>'
    
    def to_css(self, selector):
        base_css = super().to_css(selector)
        img_css = f"""{selector} img {{
    max-width: {self.max_width};
    max-height: {self.max_height};
    object-fit: {self.object_fit};
    display: block;
    margin: 0 auto;
}}"""
        return base_css + "\n\n" + img_css


class DividerComponent(Component):
    """Horizontal divider/separator"""
    
    def __init__(self):
        super().__init__(ComponentType.DIVIDER)
        self.height = ComponentDefaults.DIVIDER_HEIGHT
        self.background_color = ComponentDefaults.DIVIDER_COLOR
        self.margin_top = ComponentDefaults.DIVIDER_MARGIN_TOP
        self.margin_bottom = ComponentDefaults.DIVIDER_MARGIN_BOTTOM
        
    def to_html(self):
        return '<hr class="divider">'


class HeadingComponent(Component):
    """Heading component"""
    
    def __init__(self, field_name="Title", level=2):
        super().__init__(ComponentType.HEADING, field_name)
        self.level = level  # h1, h2, h3, etc.
        # Set font size based on heading level
        if level == 1:
            self.font_size = ComponentDefaults.HEADING_FONT_SIZE_H1
        elif level == 2:
            self.font_size = ComponentDefaults.HEADING_FONT_SIZE_H2
        else:
            self.font_size = ComponentDefaults.HEADING_FONT_SIZE_H3
        self.font_weight = ComponentDefaults.HEADING_FONT_WEIGHT
        
    def to_html(self):
        # Escape field name to prevent XSS
        safe_field_name = html.escape(self.field_name)
        return f'<h{self.level} class="heading">{{{{{safe_field_name}}}}}</h{self.level}>'


class ContainerComponent(Component):
    """Container for grouping components"""
    
    def __init__(self):
        super().__init__(ComponentType.CONTAINER)
        self.children = []
        self.display = ComponentDefaults.CONTAINER_DISPLAY
        self.flex_direction = ComponentDefaults.CONTAINER_FLEX_DIRECTION
        
    def to_html(self):
        children_html = "\n".join(child.to_html() for child in self.children)
        return f'<div class="container">\n{children_html}\n</div>'
    
    def add_child(self, component):
        self.children.append(component)
    
    def remove_child(self, component):
        if component in self.children:
            self.children.remove(component)


class ConditionalComponent(Component):
    """Conditional component - shows content only if field has value"""
    
    def __init__(self, field_name="Extra"):
        super().__init__(ComponentType.CONDITIONAL, field_name)
        self.children = []
        self.invert = False  # If True, show when field is empty
        
    def to_html(self):
        # Escape field name to prevent XSS
        safe_field_name = html.escape(self.field_name)
        children_html = "\n".join(child.to_html() for child in self.children)
        symbol = "^" if self.invert else "#"
        return f'{{{{{symbol}{safe_field_name}}}}}\n{children_html}\n{{{{/{safe_field_name}}}}}'
    
    def add_child(self, component):
        self.children.append(component)
    
    def remove_child(self, component):
        if component in self.children:
            self.children.remove(component)
