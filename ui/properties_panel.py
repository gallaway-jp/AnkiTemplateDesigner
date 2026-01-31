"""Properties panel for editing component properties."""

from typing import Dict, Any, Optional


class PropertiesPanel:
    """Panel for editing component properties."""
    
    def __init__(self):
        self.selected_component_id: Optional[str] = None
        self.properties: Dict[str, Any] = {}
    
    def set_component(self, component_id: str, properties: Dict[str, Any]) -> None:
        """Set the component being edited in the panel."""
        self.selected_component_id = component_id
        self.properties = properties.copy()
    
    def get_properties(self) -> Dict[str, Any]:
        """Get current properties from the panel."""
        return self.properties.copy()
    
    def update_property(self, key: str, value: Any) -> None:
        """Update a single property."""
        self.properties[key] = value
    
    def refresh(self) -> None:
        """Refresh the panel display."""
        pass


__all__ = ['PropertiesPanel']
