"""
AnkiDroid template renderer - simulates AnkiDroid card rendering
"""

from .base_renderer import BaseRenderer


class AnkiDroidRenderer(BaseRenderer):
    """Renderer for AnkiDroid templates"""
    
    def __init__(self):
        super().__init__()
        self.light_css = self._get_ankidroid_light_css()
        self.dark_css = self._get_ankidroid_dark_css()
    
    def _build_html(self, content_html, css, theme='light', **kwargs):
        """
        Build complete HTML for AnkiDroid
        
        Args:
            content_html: Rendered content HTML
            css: Template CSS
            theme: 'light' or 'dark'
            **kwargs: Additional options
        
        Returns:
            Complete HTML document
        """
        # Select theme CSS
        theme_css = self.dark_css if theme == 'dark' else self.light_css
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        {theme_css}
        {css}
    </style>
</head>
<body class="ankidroid-body">
    <div class="card ankidroid-card">
        {content_html}
    </div>
    
    <!-- AnkiDroid specific elements -->
    <script>
        // AnkiDroid JavaScript API simulation
        var AnkiDroidJS = {{
            version: "0.1.0",
            ankiPlatform: "android"
        }};
    </script>
</body>
</html>
"""
    
    def _get_ankidroid_light_css(self):
        """Get base CSS for AnkiDroid light theme"""
        return """
/* AnkiDroid Light Theme */
html {
    overflow-x: hidden;
    overflow-y: auto;
}

body.ankidroid-body {
    margin: 8px;
    padding: 0;
    background-color: #ffffff;
    font-family: "Roboto", "Droid Sans", Arial, sans-serif;
    font-size: 18px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

.card.ankidroid-card {
    background-color: #ffffff;
    color: #212121;
    padding: 0;
    margin: 0;
    text-align: center;
    min-height: 100vh;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
}

/* Code */
code, pre {
    font-family: "Roboto Mono", "Droid Sans Mono", "Courier New", monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 14px;
}

pre {
    padding: 8px;
    overflow-x: auto;
    white-space: pre-wrap;
}

/* Links */
a {
    color: #1976d2;
    text-decoration: none;
}

a:active {
    color: #0d47a1;
}

/* Lists */
ul, ol {
    text-align: left;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
}

th, td {
    border: 1px solid #e0e0e0;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #e0e0e0;
    margin: 10px 0;
    padding-left: 15px;
    color: #757575;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 20px 0;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    margin: 15px 0 10px 0;
    font-weight: 500;
}

p {
    margin: 10px 0;
}

/* Touch-friendly sizing */
button, input, select, textarea {
    min-height: 48px;
    font-size: 16px;
}
"""
    
    def _get_ankidroid_dark_css(self):
        """Get base CSS for AnkiDroid dark theme"""
        return """
/* AnkiDroid Dark Theme */
html {
    overflow-x: hidden;
    overflow-y: auto;
}

body.ankidroid-body {
    margin: 8px;
    padding: 0;
    background-color: #121212;
    font-family: "Roboto", "Droid Sans", Arial, sans-serif;
    font-size: 18px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

.card.ankidroid-card {
    background-color: #1e1e1e;
    color: #e0e0e0;
    padding: 0;
    margin: 0;
    text-align: center;
    min-height: 100vh;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
    opacity: 0.87;
}

/* Code */
code, pre {
    font-family: "Roboto Mono", "Droid Sans Mono", "Courier New", monospace;
    background-color: #2d2d2d;
    color: #d4d4d4;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 14px;
}

pre {
    padding: 8px;
    overflow-x: auto;
    white-space: pre-wrap;
}

/* Links */
a {
    color: #64b5f6;
    text-decoration: none;
}

a:active {
    color: #90caf9;
}

/* Lists */
ul, ol {
    text-align: left;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
}

th, td {
    border: 1px solid #424242;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #2d2d2d;
    font-weight: bold;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #424242;
    margin: 10px 0;
    padding-left: 15px;
    color: #9e9e9e;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 1px solid #424242;
    margin: 20px 0;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    margin: 15px 0 10px 0;
    font-weight: 500;
    color: #ffffff;
}

p {
    margin: 10px 0;
}

/* Touch-friendly sizing */
button, input, select, textarea {
    min-height: 48px;
    font-size: 16px;
}

/* Reduce bright whites */
* {
    color: #e0e0e0;
}

strong, b {
    color: #ffffff;
}
"""
