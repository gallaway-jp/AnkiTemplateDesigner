"""AnkiDroid renderer for rendering templates for mobile/AnkiDroid display."""

from typing import Dict, Any
from .base_renderer import BaseRenderer


class AnkiDroidRenderer(BaseRenderer):
    """Renderer for AnkiDroid mobile display format."""
    
    def __init__(self):
        """Initialize the AnkiDroid renderer."""
        super().__init__()
        self.name = "AnkiDroidRenderer"
    
    def render(self, template_data: Dict[str, Any]) -> str:
        """
        Render template for AnkiDroid display.
        
        Args:
            template_data: Dictionary containing template data
        
        Returns:
            HTML/CSS string suitable for AnkiDroid display
        """
        if not self.validate_data(template_data):
            return "<div>Invalid template data</div>"
        
        # Basic rendering - just return empty div
        return "<div class='template-ankidroid'></div>"
    
    def supports_format(self, format_name: str) -> bool:
        """
        Check if AnkiDroid format is supported.
        
        Args:
            format_name: Format name to check
        
        Returns:
            True for 'ankidroid', 'mobile', 'android' formats
        """
        return format_name.lower() in ['ankidroid', 'mobile', 'android']
    
    def render_responsive(self, template_data: Dict[str, Any], screen_width: int) -> str:
        """Render template responsively for different screen sizes."""
        return "<div class='template-ankidroid'></div>"
    
    def optimize_for_performance(self, template_data: Dict[str, Any]) -> str:
        """Render template optimized for mobile performance."""
        return "<div class='template-ankidroid-optimized'></div>"


__all__ = ['AnkiDroidRenderer']
