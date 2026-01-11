"""Data models for template representation.

This module defines the core data structures for representing Anki templates,
components, styles, and behaviors in the GrapeJS-based designer.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


class CardSide(Enum):
    """Enum for card sides."""
    FRONT = "front"
    BACK = "back"


@dataclass
class AnkiBehavior:
    """Represents an AnkiDroidJS API behavior binding.
    
    Attributes:
        action: AnkiDroidJS API method (e.g., "ankiShowAnswer", "ankiMarkCard")
        trigger: Event trigger (e.g., "click", "load", "keypress")
        target_selector: Optional CSS selector for event delegation
        params: Additional parameters for the action
    """
    action: str
    trigger: str = "click"
    target_selector: Optional[str] = None
    params: dict = field(default_factory=dict)


@dataclass
class ComponentStyle:
    """CSS styles for a component.
    
    Attributes:
        css_class: Space-separated CSS class names
        inline_styles: Dictionary of CSS properties for inline styling
        responsive_styles: Breakpoint-specific styles (e.g., {'mobile': {...}})
    """
    css_class: str = ""
    inline_styles: dict = field(default_factory=dict)
    responsive_styles: dict = field(default_factory=dict)


@dataclass
class Component:
    """Represents a UI component in the template.
    
    This is the core building block that maps to GrapeJS components.
    
    Attributes:
        id: Unique component identifier
        type: GrapeJS component type (e.g., 'text', 'button', 'container')
        tag_name: HTML tag name (e.g., 'div', 'button', 'span')
        content: Text content or inner HTML
        attributes: HTML attributes (e.g., {'href': 'url', 'data-field': 'Front'})
        style: ComponentStyle object containing CSS information
        behaviors: List of AnkiDroidJS API behavior bindings
        children: Child components for hierarchical structure
        anki_field: Bound Anki field name for data binding (e.g., 'Front', 'Back')
    """
    id: str
    type: str
    tag_name: str = "div"
    content: str = ""
    attributes: dict = field(default_factory=dict)
    style: ComponentStyle = field(default_factory=ComponentStyle)
    behaviors: list[AnkiBehavior] = field(default_factory=list)
    children: list["Component"] = field(default_factory=list)
    anki_field: Optional[str] = None


@dataclass
class TemplateCard:
    """Represents one card template (front/back pair).
    
    Attributes:
        name: Card template name (e.g., 'Card 1', 'Reverse Card')
        front_components: List of components for the front side
        back_components: List of components for the back side
        shared_css: CSS shared between front and back
    """
    name: str
    front_components: list[Component] = field(default_factory=list)
    back_components: list[Component] = field(default_factory=list)
    shared_css: str = ""


@dataclass
class Template:
    """Complete Anki note type template.
    
    Represents the full template structure that can be exported to Anki
    or loaded from Anki note types.
    
    Attributes:
        name: Template/Note type name
        cards: List of card templates (front/back pairs)
        fields: List of Anki field names (e.g., ['Front', 'Back', 'Audio'])
        css: Global CSS for all cards
        grapejs_data: Raw GrapeJS project JSON (for round-trip editing)
        version: Template format version for migration compatibility
    """
    name: str
    cards: list[TemplateCard] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    css: str = ""
    grapejs_data: Optional[dict] = None
    version: str = "2.0.0"
