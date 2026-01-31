"""Data models for template representation.

This module defines the core data structures used throughout
the template designer for representing templates, components,
and related data.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class ComponentType(Enum):
    """Enumeration of available component types."""
    CONTAINER = "container"
    ROW = "row"
    COLUMN = "column"
    TEXT = "text"
    HEADING = "heading"
    FIELD = "field"
    CLOZE = "cloze"
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class ComponentStyle:
    """Style properties for a component.
    
    Attributes:
        background: Background color or image.
        color: Text color.
        font_size: Font size (with units, e.g., "16px").
        font_family: Font family name.
        padding: Padding value.
        margin: Margin value.
        border: Border specification.
        border_radius: Border radius value.
        custom_css: Additional custom CSS.
    """
    background: Optional[str] = None
    color: Optional[str] = None
    font_size: Optional[str] = None
    font_family: Optional[str] = None
    padding: Optional[str] = None
    margin: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    custom_css: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in {
            "background": self.background,
            "color": self.color,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "padding": self.padding,
            "margin": self.margin,
            "border": self.border,
            "borderRadius": self.border_radius,
            "customCss": self.custom_css,
        }.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentStyle":
        """Create instance from dictionary."""
        return cls(
            background=data.get("background"),
            color=data.get("color"),
            font_size=data.get("fontSize"),
            font_family=data.get("fontFamily"),
            padding=data.get("padding"),
            margin=data.get("margin"),
            border=data.get("border"),
            border_radius=data.get("borderRadius"),
            custom_css=data.get("customCss"),
        )


@dataclass
class Component:
    """A template component (block).
    
    Attributes:
        id: Unique identifier for the component.
        type: Component type from ComponentType enum.
        content: Text content (for text-based components).
        field_name: Anki field name (for field components).
        style: Style properties.
        children: Child components (for containers).
        attributes: Additional attributes.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: ComponentType = ComponentType.CONTAINER
    content: str = ""
    field_name: Optional[str] = None
    style: ComponentStyle = field(default_factory=ComponentStyle)
    children: List["Component"] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "fieldName": self.field_name,
            "style": self.style.to_dict(),
            "children": [c.to_dict() for c in self.children],
            "attributes": self.attributes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        """Create instance from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            type=ComponentType(data.get("type", "container")),
            content=data.get("content", ""),
            field_name=data.get("fieldName"),
            style=ComponentStyle.from_dict(data.get("style", {})),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            attributes=data.get("attributes", {}),
        )


@dataclass
class TemplateSide:
    """One side (front or back) of a template.
    
    Attributes:
        html: Raw HTML content.
        components: Component tree representation.
    """
    html: str = ""
    components: List[Component] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "html": self.html,
            "components": [c.to_dict() for c in self.components],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateSide":
        """Create instance from dictionary."""
        return cls(
            html=data.get("html", ""),
            components=[Component.from_dict(c) for c in data.get("components", [])],
        )


@dataclass
class Template:
    """Complete Anki card template.
    
    Attributes:
        id: Unique template identifier.
        name: Template name.
        front: Front side of the card.
        back: Back side of the card.
        css: Shared CSS styles.
        note_type: Associated note type name.
        created_at: Creation timestamp.
        modified_at: Last modification timestamp.
        version: Template version number.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Template"
    front: TemplateSide = field(default_factory=TemplateSide)
    back: TemplateSide = field(default_factory=TemplateSide)
    css: str = ""
    note_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "front": self.front.to_dict(),
            "back": self.back.to_dict(),
            "css": self.css,
            "noteType": self.note_type,
            "createdAt": self.created_at.isoformat(),
            "modifiedAt": self.modified_at.isoformat(),
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create instance from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Template"),
            front=TemplateSide.from_dict(data.get("front", {})),
            back=TemplateSide.from_dict(data.get("back", {})),
            css=data.get("css", ""),
            note_type=data.get("noteType"),
            created_at=datetime.fromisoformat(data.get("createdAt", datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get("modifiedAt", datetime.now().isoformat())),
            version=data.get("version", 1),
        )
    
    def update_modified(self) -> None:
        """Update the modification timestamp."""
        self.modified_at = datetime.now()
        self.version += 1
