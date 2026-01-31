"""Base renderer class for AnkiTemplateDesigner."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRenderer(ABC):
    """Abstract base class for all template renderers."""
    
    def __init__(self):
        """Initialize the renderer."""
        self.name = "BaseRenderer"
    
    @abstractmethod
    def render(self, template_data: Dict[str, Any]) -> str:
        """
        Render template data.
        
        Args:
            template_data: Dictionary containing template data
        
        Returns:
            Rendered output as string
        """
        pass
    
    @abstractmethod
    def supports_format(self, format_name: str) -> bool:
        """
        Check if this renderer supports a specific format.
        
        Args:
            format_name: Name of the format to check
        
        Returns:
            True if supported, False otherwise
        """
        pass
    
    def validate_data(self, template_data: Dict[str, Any]) -> bool:
        """
        Validate template data before rendering.
        
        Args:
            template_data: Data to validate
        
        Returns:
            True if valid, False otherwise
        """
        return isinstance(template_data, dict)


__all__ = ['BaseRenderer']
