"""
Syntax highlighting for HTML and CSS in the code editor.

Provides syntax highlighting using Qt's QSyntaxHighlighter for HTML, CSS,
and Mustache template syntax.
"""

from PyQt6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont)
from PyQt6.QtCore import QRegularExpression
from typing import List, Tuple
import re


class HTMLHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for HTML with Mustache templates.
    
    Highlights HTML tags, attributes, strings, and Mustache placeholders.
    """
    
    def __init__(self, parent=None):
        """Initialize HTML highlighter."""
        super().__init__(parent)
        
        # Define formats
        self.formats = {}
        
        # HTML tag format
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#0000FF"))  # Blue
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.formats['tag'] = tag_format
        
        # HTML attribute format
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor("#FF0000"))  # Red
        self.formats['attribute'] = attr_format
        
        # String format (quoted values)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # Green
        self.formats['string'] = string_format
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)
        self.formats['comment'] = comment_format
        
        # Mustache placeholder format
        mustache_format = QTextCharFormat()
        mustache_format.setForeground(QColor("#9C27B0"))  # Purple
        mustache_format.setFontWeight(QFont.Weight.Bold)
        self.formats['mustache'] = mustache_format
        
        # Define highlighting rules
        self.rules: List[Tuple[QRegularExpression, str]] = []
        
        # HTML comments
        self.rules.append((
            QRegularExpression(r'<!--.*?-->'),
            'comment'
        ))
        
        # Mustache placeholders
        self.rules.append((
            QRegularExpression(r'\{\{[^}]+\}\}'),
            'mustache'
        ))
        
        # HTML tags
        self.rules.append((
            QRegularExpression(r'<\/?[\w\d]+'),
            'tag'
        ))
        self.rules.append((
            QRegularExpression(r'\/?>'),
            'tag'
        ))
        
        # HTML attributes
        self.rules.append((
            QRegularExpression(r'\b[\w-]+(?=\=)'),
            'attribute'
        ))
        
        # Quoted strings
        self.rules.append((
            QRegularExpression(r'"[^"]*"'),
            'string'
        ))
        self.rules.append((
            QRegularExpression(r"'[^']*'"),
            'string'
        ))
    
    def highlightBlock(self, text: str):
        """
        Highlight a block of text.
        
        Args:
            text: Text to highlight
        """
        # Apply each rule
        for pattern, format_name in self.rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, self.formats[format_name])


class CSSHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for CSS.
    
    Highlights selectors, properties, values, and comments.
    """
    
    def __init__(self, parent=None):
        """Initialize CSS highlighter."""
        super().__init__(parent)
        
        # Define formats
        self.formats = {}
        
        # Selector format
        selector_format = QTextCharFormat()
        selector_format.setForeground(QColor("#0000FF"))  # Blue
        selector_format.setFontWeight(QFont.Weight.Bold)
        self.formats['selector'] = selector_format
        
        # Property format
        property_format = QTextCharFormat()
        property_format.setForeground(QColor("#FF0000"))  # Red
        self.formats['property'] = property_format
        
        # Value format
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#008000"))  # Green
        self.formats['value'] = value_format
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)
        self.formats['comment'] = comment_format
        
        # Important format
        important_format = QTextCharFormat()
        important_format.setForeground(QColor("#FF4081"))  # Pink
        important_format.setFontWeight(QFont.Weight.Bold)
        self.formats['important'] = important_format
        
        # Color format
        color_format = QTextCharFormat()
        color_format.setForeground(QColor("#9C27B0"))  # Purple
        self.formats['color'] = color_format
        
        # Define highlighting rules
        self.rules: List[Tuple[QRegularExpression, str]] = []
        
        # CSS comments
        self.rules.append((
            QRegularExpression(r'/\*.*?\*/'),
            'comment'
        ))
        
        # !important
        self.rules.append((
            QRegularExpression(r'!important'),
            'important'
        ))
        
        # Colors (hex)
        self.rules.append((
            QRegularExpression(r'#[0-9A-Fa-f]{3,6}\b'),
            'color'
        ))
        
        # Colors (rgb/rgba)
        self.rules.append((
            QRegularExpression(r'rgba?\([^)]+\)'),
            'color'
        ))
        
        # Selectors (simplified - captures class and id selectors)
        self.rules.append((
            QRegularExpression(r'[\.#][\w-]+'),
            'selector'
        ))
        
        # Element selectors
        self.rules.append((
            QRegularExpression(r'\b[a-z][\w-]*(?=\s*\{)'),
            'selector'
        ))
        
        # Properties
        self.rules.append((
            QRegularExpression(r'\b[\w-]+(?=\s*:)'),
            'property'
        ))
        
        # Values (after colon, before semicolon)
        self.rules.append((
            QRegularExpression(r':\s*([^;]+)'),
            'value'
        ))
    
    def highlightBlock(self, text: str):
        """
        Highlight a block of text.
        
        Args:
            text: Text to highlight
        """
        # Apply each rule
        for pattern, format_name in self.rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                
                # For value rule, only highlight the captured group
                if format_name == 'value' and match.lastCapturedIndex() > 0:
                    start = match.capturedStart(1)
                    length = match.capturedLength(1)
                
                self.setFormat(start, length, self.formats[format_name])


class MustacheHighlighter(QSyntaxHighlighter):
    """
    Dedicated highlighter for Mustache template syntax.
    
    Highlights placeholders, conditionals, and loops.
    """
    
    def __init__(self, parent=None):
        """Initialize Mustache highlighter."""
        super().__init__(parent)
        
        # Define formats
        self.formats = {}
        
        # Variable format
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("#9C27B0"))  # Purple
        variable_format.setFontWeight(QFont.Weight.Bold)
        self.formats['variable'] = variable_format
        
        # Section format (conditionals, loops)
        section_format = QTextCharFormat()
        section_format.setForeground(QColor("#FF5722"))  # Deep Orange
        section_format.setFontWeight(QFont.Weight.Bold)
        self.formats['section'] = section_format
        
        # Inverted section format
        inverted_format = QTextCharFormat()
        inverted_format.setForeground(QColor("#F44336"))  # Red
        inverted_format.setFontWeight(QFont.Weight.Bold)
        self.formats['inverted'] = inverted_format
        
        # Delimiter format
        delimiter_format = QTextCharFormat()
        delimiter_format.setForeground(QColor("#607D8B"))  # Blue Gray
        self.formats['delimiter'] = delimiter_format
        
        # Define highlighting rules
        self.rules: List[Tuple[QRegularExpression, str]] = []
        
        # Section tags ({{#...}})
        self.rules.append((
            QRegularExpression(r'\{\{#[^}]+\}\}'),
            'section'
        ))
        
        # Closing section tags ({{/...}})
        self.rules.append((
            QRegularExpression(r'\{\{/[^}]+\}\}'),
            'section'
        ))
        
        # Inverted sections ({{^...}})
        self.rules.append((
            QRegularExpression(r'\{\{\^[^}]+\}\}'),
            'inverted'
        ))
        
        # Regular variables ({{...}})
        self.rules.append((
            QRegularExpression(r'\{\{[^#/\^][^}]*\}\}'),
            'variable'
        ))
        
        # Unescaped variables ({{{...}}})
        self.rules.append((
            QRegularExpression(r'\{\{\{[^}]+\}\}\}'),
            'variable'
        ))
    
    def highlightBlock(self, text: str):
        """
        Highlight a block of text.
        
        Args:
            text: Text to highlight
        """
        # Apply each rule
        for pattern, format_name in self.rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, self.formats[format_name])


# Theme definitions
class HighlighterTheme:
    """Color themes for syntax highlighting."""
    
    LIGHT_THEME = {
        'tag': '#0000FF',
        'attribute': '#FF0000',
        'string': '#008000',
        'comment': '#808080',
        'mustache': '#9C27B0',
        'selector': '#0000FF',
        'property': '#FF0000',
        'value': '#008000',
        'important': '#FF4081',
        'color': '#9C27B0',
        'section': '#FF5722',
        'inverted': '#F44336',
        'variable': '#9C27B0',
    }
    
    DARK_THEME = {
        'tag': '#569CD6',
        'attribute': '#9CDCFE',
        'string': '#CE9178',
        'comment': '#6A9955',
        'mustache': '#C586C0',
        'selector': '#D7BA7D',
        'property': '#9CDCFE',
        'value': '#CE9178',
        'important': '#F48771',
        'color': '#C586C0',
        'section': '#DCDCAA',
        'inverted': '#F48771',
        'variable': '#C586C0',
    }
    
    @staticmethod
    def apply_theme(highlighter, theme_name: str = 'light'):
        """
        Apply a color theme to a highlighter.
        
        Args:
            highlighter: Highlighter instance
            theme_name: Theme name ('light' or 'dark')
        """
        theme = HighlighterTheme.DARK_THEME if theme_name == 'dark' else HighlighterTheme.LIGHT_THEME
        
        for format_name, color in theme.items():
            if format_name in highlighter.formats:
                highlighter.formats[format_name].setForeground(QColor(color))
