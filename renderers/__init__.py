"""Renderers module for AnkiTemplateDesigner."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRenderer(ABC):
    """Base class for all renderers."""
    
    def __init__(self):
        """Initialize the renderer."""
        pass
    
    @abstractmethod
    def render(self, data: Dict[str, Any]) -> str:
        """Render data to output format."""
        pass
    
    @abstractmethod
    def supports_format(self, format_name: str) -> bool:
        """Check if renderer supports a specific format."""
        pass


__all__ = ['BaseRenderer']
