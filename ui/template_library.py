"""Template library for AnkiTemplateDesigner."""

from typing import Dict, List, Optional
from .components import Component, ComponentType


class TemplateLibrary:
    """Manages a library of reusable templates."""
    
    def __init__(self):
        self.templates: Dict[str, Component] = {}
    
    def add_template(self, template_id: str, template: Component) -> None:
        """Add a template to the library."""
        self.templates[template_id] = template
    
    def get_template(self, template_id: str) -> Optional[Component]:
        """Retrieve a template from the library."""
        return self.templates.get(template_id)
    
    def list_templates(self, component_type: Optional[ComponentType] = None) -> List[str]:
        """List all available templates."""
        return list(self.templates.keys())
    
    def remove_template(self, template_id: str) -> bool:
        """Remove a template from the library."""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False


__all__ = ['TemplateLibrary']
