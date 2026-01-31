"""Design surface for component editing."""

from typing import Optional, Any, Tuple


class DesignSurface:
    """Main design surface for editing components."""
    
    def __init__(self, width: float = 800, height: float = 600):
        self.width = width
        self.height = height
        self.components = []
        self.selected_component: Optional[str] = None
    
    def add_component(self, component: Any) -> None:
        """Add a component to the design surface."""
        self.components.append(component)
    
    def remove_component(self, component_id: str) -> None:
        """Remove a component from the design surface."""
        self.components = [c for c in self.components if c.id != component_id]
    
    def select_component(self, component_id: str) -> None:
        """Select a component on the design surface."""
        self.selected_component = component_id
    
    def get_component_at(self, x: float, y: float) -> Optional[Any]:
        """Get component at specified coordinates."""
        return None
    
    def render(self) -> str:
        """Render the design surface to HTML."""
        return "<div></div>"


__all__ = ['DesignSurface']
