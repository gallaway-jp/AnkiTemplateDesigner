"""Desktop renderer for rendering templates for desktop/web display."""

from typing import Dict, Any
from .base_renderer import BaseRenderer


class DesktopRenderer(BaseRenderer):
    """Renderer for desktop/web display formats."""
    
    def __init__(self):
        """Initialize the desktop renderer."""
        super().__init__()
        self.name = "DesktopRenderer"
    
    def render(self, template_data: Dict[str, Any]) -> str:
        """
        Render template for desktop display.
        
        Args:
            template_data: Dictionary containing template data
        
        Returns:
            HTML string suitable for desktop display
        """
        if not self.validate_data(template_data):
            return "<div>Invalid template data</div>"
        
        # Basic rendering - just return empty div
        return "<div class='template-desktop'></div>"
    
    def supports_format(self, format_name: str) -> bool:
        """
        Check if desktop format is supported.
        
        Args:
            format_name: Format name to check
        
        Returns:
            True for 'html', 'web', 'desktop' formats
        """
        return format_name.lower() in ['html', 'web', 'desktop']
    
    def render_with_styles(self, template_data: Dict[str, Any], styles: Dict[str, str]) -> str:
        """Render template with custom styles."""
        return "<div class='template-desktop'></div>"


__all__ = ['DesktopRenderer']
