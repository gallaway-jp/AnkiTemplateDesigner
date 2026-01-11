"""Core module for Anki Template Designer.

This module contains the core functionality for template management,
component definitions, and conversion logic.
"""

from .models import (
    CardSide,
    AnkiBehavior,
    ComponentStyle,
    Component,
    TemplateCard,
    Template,
)
from .converter import (
    AnkiHTMLParser,
    AnkiTemplateParser,
    AnkiTemplateGenerator,
)

__all__ = [
    "CardSide",
    "AnkiBehavior",
    "ComponentStyle",
    "Component",
    "TemplateCard",
    "Template",
    "AnkiHTMLParser",
    "AnkiTemplateParser",
    "AnkiTemplateGenerator",
]
