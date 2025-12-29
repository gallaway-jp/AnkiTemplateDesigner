"""
Desktop template renderer - simulates Anki Desktop card rendering
"""

from .base_renderer import BaseRenderer


class DesktopRenderer(BaseRenderer):
    """Renderer for Anki Desktop templates"""
    
    def __init__(self):
        super().__init__()
        self.base_css = self._get_desktop_base_css()
    
    def _build_html(self, content_html, css, **kwargs):
        """
        Build complete HTML for Anki Desktop
        
        Args:
            content_html: Rendered content HTML
            css: Template CSS
            **kwargs: Additional options
        
        Returns:
            Complete HTML document
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self.base_css}
        {css}
    </style>
</head>
<body>
    <div class="card">
        {content_html}
    </div>
</body>
</html>
"""
    
    def _get_desktop_base_css(self):
        """Get base CSS that Anki Desktop applies"""
        return """
/* Anki Desktop base styles */
body {
    margin: 0;
    padding: 0;
    background-color: #f0f0f0;
    font-family: Arial, sans-serif;
    font-size: 20px;
}

.card {
    background-color: white;
    color: black;
    padding: 20px;
    margin: 0;
    text-align: center;
}

img {
    max-width: 100%;
    max-height: 95vh;
}

/* Night mode support */
.night_mode body {
    background-color: #1e1e1e;
}

.night_mode .card {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

/* Code highlighting */
code {
    font-family: "Courier New", monospace;
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 3px;
}

.night_mode code {
    background-color: #3a3a3a;
}

/* Links */
a {
    color: #0066cc;
}

.night_mode a {
    color: #6699ff;
}

/* Lists */
ul, ol {
    text-align: left;
    display: inline-block;
}
"""
