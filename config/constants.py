"""
Configuration constants for the Anki Template Designer
Centralizes magic numbers and configuration values for better maintainability
"""

# UI Default Values
class UIDefaults:
    """Default values for UI components"""
    FONT_SIZE = 20  # Points, matches Anki default card font size
    FONT_FAMILY = "Arial, sans-serif"
    PADDING = 10  # Pixels, comfortable spacing for card content
    MARGIN = 0  # Pixels, no margin by default
    BORDER_WIDTH = 0  # Pixels, no border by default
    BORDER_RADIUS = 0  # Pixels, no rounded corners by default
    
    # Colors
    DEFAULT_TEXT_COLOR = "#000000"
    DEFAULT_BACKGROUND = "transparent"
    DEFAULT_BORDER_COLOR = "#000000"


# Layout Configuration
class LayoutDefaults:
    """Default values for layout and positioning"""
    CARD_WIDTH = 400  # Pixels, typical mobile card width
    CARD_HEIGHT = 600  # Pixels, maintains 3:2 aspect ratio
    GRID_SIZE = 8  # 8dp grid system (Material Design standard)
    
    # Constraint defaults
    DEFAULT_HORIZONTAL_BIAS = 0.5  # 0.0 = left, 0.5 = center, 1.0 = right
    DEFAULT_VERTICAL_BIAS = 0.5  # 0.0 = top, 0.5 = center, 1.0 = bottom
    MAX_CONSTRAINT_ITERATIONS = 3  # Sufficient for most constraint resolution
    
    # Zoom levels
    MIN_ZOOM = 0.1  # 10% minimum zoom
    MAX_ZOOM = 4.0  # 400% maximum zoom
    ZOOM_STEP = 1.2  # 20% zoom increment/decrement


# Component Type Specific Defaults
class ComponentDefaults:
    """Default values for specific component types"""
    # Heading
    HEADING_FONT_SIZE_H1 = 28
    HEADING_FONT_SIZE_H2 = 24
    HEADING_FONT_SIZE_H3 = 20
    HEADING_FONT_WEIGHT = "bold"
    
    # Divider
    DIVIDER_HEIGHT = "2px"
    DIVIDER_COLOR = "#cccccc"
    DIVIDER_MARGIN_TOP = 20
    DIVIDER_MARGIN_BOTTOM = 20
    
    # Image
    IMAGE_MAX_WIDTH = "100%"
    IMAGE_MAX_HEIGHT = "400px"
    IMAGE_OBJECT_FIT = "contain"
    
    # Container
    CONTAINER_FLEX_DIRECTION = "column"
    CONTAINER_DISPLAY = "flex"


# Window and Dialog Sizes
class WindowDefaults:
    """Default window and dialog dimensions"""
    DIALOG_WIDTH = 1600  # Pixels, wide enough to show all panels
    DIALOG_HEIGHT = 900  # Pixels, comfortable height for most screens
    CANVAS_MIN_WIDTH = 600
    CANVAS_MIN_HEIGHT = 800
    PREVIEW_WIDTH = 1600
    PREVIEW_HEIGHT = 900


# Spacing Values
class Spacing:
    """Common spacing values following Material Design principles"""
    EXTRA_SMALL = 4  # Pixels
    SMALL = 8  # Pixels
    MEDIUM = 16  # Pixels
    LARGE = 24  # Pixels
    EXTRA_LARGE = 32  # Pixels


# Animation and Interaction
class InteractionDefaults:
    """Defaults for user interactions"""
    PREVIEW_DEBOUNCE_MS = 300  # Milliseconds before preview updates
    DOUBLE_CLICK_THRESHOLD_MS = 300  # Milliseconds for double-click detection


# Import for backward compatibility
__all__ = [
    'UIDefaults',
    'LayoutDefaults',
    'ComponentDefaults',
    'WindowDefaults',
    'Spacing',
    'InteractionDefaults',
]
