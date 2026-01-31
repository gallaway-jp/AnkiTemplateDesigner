"""
UI Components module for AnkiTemplateDesigner.

This module provides the core component classes and types for building UI templates.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field


class ComponentType(Enum):
    """Enumeration of available component types."""
    TEXT_FIELD = "text_field"
    IMAGE_FIELD = "image_field"
    HEADING = "heading"
    CONTAINER = "container"
    DIVIDER = "divider"
    BUTTON = "button"
    CUSTOM = "custom"


@dataclass
class Component:
    """Base component class for all UI elements."""
    
    id: str
    type: ComponentType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['Component'] = field(default_factory=list)
    constraints: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'properties': self.properties,
            'children': [child.to_dict() for child in self.children],
            'constraints': self.constraints,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create component from dictionary representation."""
        component_type = ComponentType(data['type'])
        children = [cls.from_dict(child) for child in data.get('children', [])]
        
        return cls(
            id=data['id'],
            type=component_type,
            name=data['name'],
            properties=data.get('properties', {}),
            children=children,
            constraints=data.get('constraints'),
        )


@dataclass
class TextFieldComponent(Component):
    """Text field input component."""
    
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.TEXT_FIELD,
            name=name,
            **kwargs
        )


@dataclass
class ImageFieldComponent(Component):
    """Image field component."""
    
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.IMAGE_FIELD,
            name=name,
            **kwargs
        )


@dataclass
class HeadingComponent(Component):
    """Heading/title component."""
    
    def __init__(self, id: str, name: str, level: int = 1, **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.HEADING,
            name=name,
            properties={'level': level},
            **kwargs
        )


@dataclass
class ContainerComponent(Component):
    """Container component for grouping other components."""
    
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.CONTAINER,
            name=name,
            **kwargs
        )


@dataclass
class DividerComponent(Component):
    """Divider/separator component."""
    
    def __init__(self, id: str, name: str = "Divider", **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.DIVIDER,
            name=name,
            **kwargs
        )


@dataclass
class ButtonComponent(Component):
    """Button component."""
    
    def __init__(self, id: str, name: str, label: str = "", **kwargs):
        super().__init__(
            id=id,
            type=ComponentType.BUTTON,
            name=name,
            properties={'label': label},
            **kwargs
        )


def create_component(
    component_id: str,
    component_type: ComponentType,
    name: str,
    **properties
) -> Component:
    """
    Factory function to create components by type.
    
    Args:
        component_id: Unique identifier for the component
        component_type: Type of component to create
        name: Display name for the component
        **properties: Additional properties for the component
    
    Returns:
        An instance of the appropriate Component subclass
    """
    component_map = {
        ComponentType.TEXT_FIELD: TextFieldComponent,
        ComponentType.IMAGE_FIELD: ImageFieldComponent,
        ComponentType.HEADING: HeadingComponent,
        ComponentType.CONTAINER: ContainerComponent,
        ComponentType.DIVIDER: DividerComponent,
        ComponentType.BUTTON: ButtonComponent,
    }
    
    component_class = component_map.get(component_type, Component)
    return component_class(id=component_id, name=name, properties=properties)


__all__ = [
    'Component',
    'ComponentType',
    'TextFieldComponent',
    'ImageFieldComponent',
    'HeadingComponent',
    'ContainerComponent',
    'DividerComponent',
    'ButtonComponent',
    'create_component',
]
