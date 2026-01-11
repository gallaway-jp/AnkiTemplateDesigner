# 02 - Architecture Plan: GrapeJS-Based Anki Template Designer

> **Purpose**: Define the new addon architecture with GrapeJS integration, Python-JS bridge, and bidirectional converter.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

The new architecture uses GrapeJS as the visual design engine running inside a QWebEngineView. Python handles Anki integration, file I/O, and template conversion. JavaScript handles the visual editor, component blocks, and user interactions.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Anki Main Window                             │
├─────────────────────────────────────────────────────────────────────┤
│                      Template Designer Dialog                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    QWebEngineView                              │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │                    GrapeJS Editor                        │  │  │
│  │  │  ┌──────────┐ ┌────────────────────┐ ┌───────────────┐  │  │  │
│  │  │  │  Blocks  │ │      Canvas        │ │   Traits      │  │  │  │
│  │  │  │  Panel   │ │   (Design Area)    │ │   Panel       │  │  │  │
│  │  │  │          │ │                    │ │               │  │  │  │
│  │  │  │ 200+ UI  │ │  Drag & Drop       │ │  Properties   │  │  │  │
│  │  │  │ Elements │ │  Visual Editor     │ │  AnkiJSApi    │  │  │  │
│  │  │  │          │ │                    │ │  Behaviors    │  │  │  │
│  │  │  └──────────┘ └────────────────────┘ └───────────────┘  │  │  │
│  │  │  ┌─────────────────────────────────────────────────────┐  │  │  │
│  │  │  │              Layer Manager / Code View              │  │  │  │
│  │  │  └─────────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ [Import HTML] [Export HTML] [Preview] [Save to Note Type] [Help]││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
anki_template_designer/
│
├── __init__.py                 # Entry point - minimal, hooks only
├── manifest.json               # Anki addon metadata
├── config.json                 # User configuration defaults
├── config.schema.json          # Configuration validation schema
│
├── core/                       # Business logic (no Qt/Anki dependencies)
│   ├── __init__.py
│   ├── models.py               # Data models (Template, Component, Style)
│   ├── converter.py            # GrapeJS JSON <-> Anki HTML/CSS/JS
│   ├── parser.py               # Parse existing Anki templates to GrapeJS
│   ├── generator.py            # Generate Anki templates from GrapeJS
│   └── validator.py            # Template validation logic
│
├── gui/                        # Qt GUI components
│   ├── __init__.py
│   ├── designer_dialog.py      # Main dialog with QWebEngineView
│   ├── preview_dialog.py       # Card preview dialog
│   ├── import_dialog.py        # Import existing template dialog
│   ├── export_dialog.py        # Export options dialog
│   └── webview_bridge.py       # Python <-> JavaScript bridge
│
├── services/                   # Application services
│   ├── __init__.py
│   ├── downloader.py           # GrapeJS asset auto-downloader
│   ├── template_service.py     # Template CRUD operations
│   ├── anki_service.py         # Anki note type integration
│   └── ankijsapi_service.py    # AnkiJSApi behavior integration
│
├── hooks/                      # Anki hook handlers
│   ├── __init__.py
│   ├── menu.py                 # Tools menu integration
│   └── card_layout.py          # Card layout editor integration
│
├── utils/                      # Utilities (KEEP FROM OLD PROJECT)
│   ├── __init__.py
│   ├── security.py             # XSS protection, sanitization
│   ├── template_utils.py       # Template manipulation
│   ├── css_utils.py            # CSS parsing/generation
│   ├── note_utils.py           # Anki note utilities
│   ├── logging_utils.py        # Logging configuration
│   ├── exceptions.py           # Custom exceptions
│   └── performance.py          # Caching utilities
│
├── config/                     # Configuration (KEEP FROM OLD PROJECT)
│   ├── __init__.py
│   └── constants.py            # App constants
│
├── web/                        # Web assets for GrapeJS
│   ├── .gitignore              # Ignore downloaded files
│   ├── index.html              # Main designer HTML
│   ├── designer.js             # GrapeJS initialization & config
│   ├── designer.css            # Custom editor styling
│   ├── bridge.js               # Python-JS communication bridge
│   │
│   ├── grapesjs/               # Downloaded at runtime (gitignored)
│   │   ├── .gitkeep
│   │   ├── grapes.min.js       # Auto-downloaded
│   │   └── grapes.min.css      # Auto-downloaded
│   │
│   ├── blocks/                 # GrapeJS block definitions
│   │   ├── index.js            # Block registration entry
│   │   ├── layout.js           # Layout & Structure blocks
│   │   ├── navigation.js       # Navigation blocks
│   │   ├── inputs.js           # Input & Form blocks
│   │   ├── buttons.js          # Button & Action blocks
│   │   ├── data.js             # Data Display blocks
│   │   ├── feedback.js         # Feedback & Status blocks
│   │   ├── overlays.js         # Overlay & Popup blocks
│   │   ├── search.js           # Search & Filter blocks
│   │   ├── commerce.js         # Commerce blocks
│   │   ├── social.js           # Social & Collaboration blocks
│   │   ├── charts.js           # Chart & Visualization blocks
│   │   ├── accessibility.js    # Accessibility blocks
│   │   ├── system.js           # System & Meta blocks
│   │   ├── motion.js           # Motion & Interaction blocks
│   │   └── advanced.js         # Specialized blocks
│   │
│   ├── traits/                 # Custom trait (property) editors
│   │   ├── index.js
│   │   ├── anki-field.js       # Anki field selector trait
│   │   ├── anki-behavior.js    # AnkiJSApi behavior trait
│   │   └── responsive.js       # Responsive breakpoint trait
│   │
│   └── plugins/                # GrapeJS plugins
│       ├── anki-plugin.js      # Anki-specific functionality
│       └── ankijsapi-plugin.js # AnkiJSApi integration
│
├── templates/                  # Built-in template library
│   ├── __init__.py
│   ├── basic.json              # Basic card template
│   ├── cloze.json              # Cloze deletion template
│   ├── image-occlusion.json    # Image occlusion template
│   └── vocabulary.json         # Vocabulary card template
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_converter.py
│   │   ├── test_parser.py
│   │   ├── test_generator.py
│   │   └── test_validator.py
│   ├── integration/
│   │   └── test_anki_integration.py
│   └── fixtures/
│       ├── sample_grapejs.json
│       └── sample_anki_template.html
│
└── docs/
    └── plans/                  # Implementation plans (this folder)
```

---

## Core Module: Data Models

### `core/models.py`

```python
"""Data models for template representation."""
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

class CardSide(Enum):
    FRONT = "front"
    BACK = "back"

@dataclass
class AnkiBehavior:
    """Represents an AnkiJSApi behavior binding."""
    action: str                          # e.g., "showAnswer", "playAudio"
    trigger: str                         # e.g., "click", "load"
    target_selector: Optional[str] = None
    params: dict = field(default_factory=dict)

@dataclass
class ComponentStyle:
    """CSS styles for a component."""
    css_class: str = ""
    inline_styles: dict = field(default_factory=dict)
    responsive_styles: dict = field(default_factory=dict)  # breakpoint -> styles

@dataclass 
class Component:
    """Represents a UI component in the template."""
    id: str
    type: str                            # GrapeJS component type
    tag_name: str = "div"
    content: str = ""
    attributes: dict = field(default_factory=dict)
    style: ComponentStyle = field(default_factory=ComponentStyle)
    behaviors: list[AnkiBehavior] = field(default_factory=list)
    children: list["Component"] = field(default_factory=list)
    anki_field: Optional[str] = None     # Bound Anki field name

@dataclass
class TemplateCard:
    """Represents one card template (front/back pair)."""
    name: str
    front_components: list[Component] = field(default_factory=list)
    back_components: list[Component] = field(default_factory=list)
    shared_css: str = ""
    
@dataclass
class Template:
    """Complete Anki note type template."""
    name: str
    cards: list[TemplateCard] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    css: str = ""
    grapejs_data: Optional[dict] = None  # Raw GrapeJS project JSON
    version: str = "2.0.0"
```

---

## Core Module: Bidirectional Converter

### `core/converter.py`

The converter handles transformation between GrapeJS JSON and Anki HTML/CSS/JS.

```python
"""Bidirectional converter between GrapeJS JSON and Anki templates."""
from typing import Optional
from .models import Template, TemplateCard, Component, AnkiBehavior
from .parser import AnkiTemplateParser
from .generator import AnkiTemplateGenerator

class TemplateConverter:
    """Main converter class for bidirectional transformation."""
    
    def __init__(self):
        self.parser = AnkiTemplateParser()
        self.generator = AnkiTemplateGenerator()
    
    # ========== GrapeJS -> Anki ==========
    
    def grapejs_to_anki(self, grapejs_json: dict) -> Template:
        """
        Convert GrapeJS project JSON to Anki Template.
        
        Args:
            grapejs_json: GrapeJS editor.getProjectData() output
            
        Returns:
            Template object with HTML/CSS ready for Anki
        """
        return self.generator.generate(grapejs_json)
    
    def grapejs_to_html(self, grapejs_json: dict, card_side: str = "front") -> str:
        """
        Convert GrapeJS JSON to HTML string.
        
        Args:
            grapejs_json: GrapeJS component data
            card_side: "front" or "back"
            
        Returns:
            HTML string with Anki field placeholders
        """
        template = self.generator.generate(grapejs_json)
        if template.cards:
            card = template.cards[0]
            if card_side == "front":
                return self.generator.components_to_html(card.front_components)
            else:
                return self.generator.components_to_html(card.back_components)
        return ""
    
    def grapejs_to_css(self, grapejs_json: dict) -> str:
        """Extract CSS from GrapeJS project."""
        return self.generator.extract_css(grapejs_json)
    
    # ========== Anki -> GrapeJS ==========
    
    def anki_to_grapejs(self, html: str, css: str = "", 
                        js: str = "") -> dict:
        """
        Convert existing Anki template to GrapeJS project JSON.
        
        Args:
            html: Anki template HTML (with {{Field}} placeholders)
            css: Anki template CSS
            js: Optional JavaScript code
            
        Returns:
            GrapeJS project JSON for editor.loadProjectData()
        """
        return self.parser.parse(html, css, js)
    
    def html_to_components(self, html: str) -> list[Component]:
        """Parse HTML string into Component tree."""
        return self.parser.parse_html(html)
    
    # ========== Validation ==========
    
    def validate_grapejs(self, grapejs_json: dict) -> list[str]:
        """Validate GrapeJS JSON structure. Returns list of errors."""
        errors = []
        if not isinstance(grapejs_json, dict):
            errors.append("GrapeJS data must be a dictionary")
            return errors
        if "pages" not in grapejs_json and "components" not in grapejs_json:
            errors.append("Missing 'pages' or 'components' in GrapeJS data")
        return errors
    
    def validate_anki_template(self, html: str, css: str = "") -> list[str]:
        """Validate Anki template. Returns list of errors."""
        from ..utils.security import SecurityValidator
        validator = SecurityValidator()
        return validator.validate_template(html, css)
```

### `core/parser.py` - Anki HTML to GrapeJS

```python
"""Parse existing Anki templates into GrapeJS format."""
import re
from html.parser import HTMLParser
from typing import Optional
from .models import Component, AnkiBehavior, ComponentStyle

class AnkiHTMLParser(HTMLParser):
    """Parse HTML into component tree."""
    
    def __init__(self):
        super().__init__()
        self.root_components: list[Component] = []
        self.stack: list[Component] = []
        self.id_counter = 0
    
    def _generate_id(self) -> str:
        self.id_counter += 1
        return f"comp-{self.id_counter}"
    
    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]):
        attrs_dict = dict(attrs)
        component = Component(
            id=attrs_dict.pop("id", self._generate_id()),
            type=self._tag_to_type(tag),
            tag_name=tag,
            attributes=attrs_dict,
            style=ComponentStyle(css_class=attrs_dict.pop("class", ""))
        )
        
        if self.stack:
            self.stack[-1].children.append(component)
        else:
            self.root_components.append(component)
        
        if tag not in ("br", "hr", "img", "input", "meta", "link"):
            self.stack.append(component)
    
    def handle_endtag(self, tag: str):
        if self.stack and self.stack[-1].tag_name == tag:
            self.stack.pop()
    
    def handle_data(self, data: str):
        text = data.strip()
        if text and self.stack:
            # Check for Anki field placeholders
            anki_field = self._extract_anki_field(text)
            if anki_field:
                self.stack[-1].anki_field = anki_field
            else:
                self.stack[-1].content += text
    
    def _tag_to_type(self, tag: str) -> str:
        """Map HTML tags to GrapeJS component types."""
        mapping = {
            "div": "container",
            "section": "section",
            "header": "header",
            "footer": "footer",
            "nav": "navigation",
            "button": "button",
            "input": "input",
            "textarea": "textarea",
            "img": "image",
            "video": "video",
            "audio": "audio",
            "table": "table",
            "form": "form",
            "label": "label",
            "span": "text",
            "p": "paragraph",
            "h1": "heading",
            "h2": "heading",
            "h3": "heading",
            "a": "link",
            "ul": "list",
            "ol": "list",
            "li": "list-item",
        }
        return mapping.get(tag, "default")
    
    def _extract_anki_field(self, text: str) -> Optional[str]:
        """Extract Anki field name from {{Field}} syntax."""
        match = re.search(r"\{\{([^}]+)\}\}", text)
        if match:
            field = match.group(1)
            # Handle special fields like {{FrontSide}}, {{Tags}}, etc.
            return field.strip()
        return None


class AnkiTemplateParser:
    """Parse complete Anki templates to GrapeJS format."""
    
    ANKI_FIELD_PATTERN = re.compile(r"\{\{([^}]+)\}\}")
    
    def parse(self, html: str, css: str = "", js: str = "") -> dict:
        """
        Parse Anki template to GrapeJS project format.
        
        Returns:
            GrapeJS project JSON structure
        """
        parser = AnkiHTMLParser()
        parser.feed(html)
        
        components = self._components_to_grapejs(parser.root_components)
        styles = self._parse_css(css)
        
        return {
            "assets": [],
            "styles": styles,
            "pages": [{
                "id": "main",
                "frames": [{
                    "component": {
                        "type": "wrapper",
                        "components": components
                    }
                }]
            }],
            "symbols": [],
            "dataSources": []
        }
    
    def parse_html(self, html: str) -> list[Component]:
        """Parse HTML string into Component objects."""
        parser = AnkiHTMLParser()
        parser.feed(html)
        return parser.root_components
    
    def _components_to_grapejs(self, components: list[Component]) -> list[dict]:
        """Convert Component objects to GrapeJS component format."""
        result = []
        for comp in components:
            gjs_comp = {
                "type": comp.type,
                "tagName": comp.tag_name,
                "attributes": comp.attributes,
                "components": self._components_to_grapejs(comp.children)
            }
            
            if comp.content:
                gjs_comp["content"] = comp.content
            
            if comp.anki_field:
                gjs_comp["attributes"]["data-anki-field"] = comp.anki_field
                gjs_comp["content"] = f"{{{{{comp.anki_field}}}}}"
            
            if comp.style.css_class:
                gjs_comp["classes"] = comp.style.css_class.split()
            
            if comp.behaviors:
                gjs_comp["attributes"]["data-anki-behaviors"] = self._serialize_behaviors(comp.behaviors)
            
            result.append(gjs_comp)
        return result
    
    def _parse_css(self, css: str) -> list[dict]:
        """Parse CSS into GrapeJS styles format."""
        # Simplified CSS parsing - full implementation would use cssutils
        styles = []
        # Parse CSS rules and convert to GrapeJS style format
        # This is a placeholder - real implementation needs CSS parser
        return styles
    
    def _serialize_behaviors(self, behaviors: list[AnkiBehavior]) -> str:
        """Serialize behaviors to JSON string for data attribute."""
        import json
        return json.dumps([{
            "action": b.action,
            "trigger": b.trigger,
            "target": b.target_selector,
            "params": b.params
        } for b in behaviors])
```

### `core/generator.py` - GrapeJS to Anki HTML

```python
"""Generate Anki templates from GrapeJS format."""
import json
import re
from typing import Optional
from .models import Template, TemplateCard, Component, AnkiBehavior

class AnkiTemplateGenerator:
    """Generate Anki-compatible templates from GrapeJS data."""
    
    # Self-closing HTML tags
    VOID_ELEMENTS = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
    
    def generate(self, grapejs_json: dict) -> Template:
        """
        Generate complete Anki Template from GrapeJS project.
        
        Args:
            grapejs_json: GrapeJS editor.getProjectData() output
            
        Returns:
            Template object ready for Anki
        """
        template = Template(
            name="Generated Template",
            grapejs_data=grapejs_json
        )
        
        # Extract pages (each page = one card)
        pages = grapejs_json.get("pages", [])
        
        for i, page in enumerate(pages):
            card = TemplateCard(name=f"Card {i + 1}")
            
            # Get components from page frames
            frames = page.get("frames", [])
            if frames:
                wrapper = frames[0].get("component", {})
                components = wrapper.get("components", [])
                
                # Parse front and back (could be separate frames or marked sections)
                front_comps, back_comps = self._split_front_back(components)
                card.front_components = [self._grapejs_to_component(c) for c in front_comps]
                card.back_components = [self._grapejs_to_component(c) for c in back_comps]
            
            template.cards.append(card)
        
        # Extract CSS
        template.css = self.extract_css(grapejs_json)
        
        # Extract fields from components
        template.fields = self._extract_fields(template)
        
        return template
    
    def components_to_html(self, components: list[Component]) -> str:
        """Convert Component tree to HTML string."""
        html_parts = []
        for comp in components:
            html_parts.append(self._component_to_html(comp))
        return "\n".join(html_parts)
    
    def _component_to_html(self, component: Component, indent: int = 0) -> str:
        """Convert single component to HTML."""
        indent_str = "  " * indent
        tag = component.tag_name
        
        # Build attributes string
        attrs = []
        if component.style.css_class:
            attrs.append(f'class="{component.style.css_class}"')
        if component.attributes.get("id"):
            attrs.append(f'id="{component.attributes["id"]}"')
        for key, value in component.attributes.items():
            if key not in ("id", "class"):
                attrs.append(f'{key}="{value}"')
        
        # Add AnkiJSApi behavior attributes
        if component.behaviors:
            for behavior in component.behaviors:
                attrs.append(f'data-anki-{behavior.trigger}="{behavior.action}"')
        
        attrs_str = " " + " ".join(attrs) if attrs else ""
        
        # Handle self-closing tags
        if tag in self.VOID_ELEMENTS:
            return f"{indent_str}<{tag}{attrs_str} />"
        
        # Handle content
        content = component.content
        if component.anki_field:
            content = f"{{{{{component.anki_field}}}}}"
        
        # Handle children
        if component.children:
            children_html = "\n".join(
                self._component_to_html(child, indent + 1) 
                for child in component.children
            )
            return f"{indent_str}<{tag}{attrs_str}>\n{children_html}\n{indent_str}</{tag}>"
        elif content:
            return f"{indent_str}<{tag}{attrs_str}>{content}</{tag}>"
        else:
            return f"{indent_str}<{tag}{attrs_str}></{tag}>"
    
    def extract_css(self, grapejs_json: dict) -> str:
        """Extract CSS from GrapeJS project."""
        styles = grapejs_json.get("styles", [])
        css_parts = []
        
        for style in styles:
            selectors = style.get("selectors", [])
            properties = style.get("style", {})
            
            if not selectors or not properties:
                continue
            
            # Build selector string
            selector_strs = []
            for sel in selectors:
                if isinstance(sel, str):
                    selector_strs.append(f".{sel}")
                elif isinstance(sel, dict):
                    name = sel.get("name", "")
                    if sel.get("type") == "id":
                        selector_strs.append(f"#{name}")
                    else:
                        selector_strs.append(f".{name}")
            
            selector = ", ".join(selector_strs) or ".unknown"
            
            # Build properties string
            props = []
            for prop, value in properties.items():
                # Convert camelCase to kebab-case
                kebab_prop = re.sub(r'([A-Z])', r'-\1', prop).lower()
                props.append(f"  {kebab_prop}: {value};")
            
            css_parts.append(f"{selector} {{\n" + "\n".join(props) + "\n}")
        
        return "\n\n".join(css_parts)
    
    def _grapejs_to_component(self, gjs_comp: dict) -> Component:
        """Convert GrapeJS component dict to Component object."""
        comp = Component(
            id=gjs_comp.get("attributes", {}).get("id", f"comp-{id(gjs_comp)}"),
            type=gjs_comp.get("type", "default"),
            tag_name=gjs_comp.get("tagName", "div"),
            content=gjs_comp.get("content", ""),
            attributes=gjs_comp.get("attributes", {})
        )
        
        # Extract classes
        classes = gjs_comp.get("classes", [])
        if classes:
            class_names = []
            for cls in classes:
                if isinstance(cls, str):
                    class_names.append(cls)
                elif isinstance(cls, dict):
                    class_names.append(cls.get("name", ""))
            comp.style.css_class = " ".join(class_names)
        
        # Extract Anki field binding
        anki_field = gjs_comp.get("attributes", {}).get("data-anki-field")
        if anki_field:
            comp.anki_field = anki_field
        
        # Extract AnkiJSApi behaviors
        behaviors_json = gjs_comp.get("attributes", {}).get("data-anki-behaviors")
        if behaviors_json:
            try:
                behaviors_data = json.loads(behaviors_json)
                comp.behaviors = [
                    AnkiBehavior(
                        action=b["action"],
                        trigger=b["trigger"],
                        target_selector=b.get("target"),
                        params=b.get("params", {})
                    )
                    for b in behaviors_data
                ]
            except json.JSONDecodeError:
                pass
        
        # Recursively process children
        children = gjs_comp.get("components", [])
        comp.children = [self._grapejs_to_component(c) for c in children]
        
        return comp
    
    def _split_front_back(self, components: list[dict]) -> tuple[list[dict], list[dict]]:
        """
        Split components into front and back sections.
        
        Convention: Components with data-card-side="back" go to back,
        or components after a {{FrontSide}} marker.
        """
        front = []
        back = []
        in_back = False
        
        for comp in components:
            attrs = comp.get("attributes", {})
            content = comp.get("content", "")
            
            if attrs.get("data-card-side") == "back" or "{{FrontSide}}" in content:
                in_back = True
            
            if in_back:
                back.append(comp)
            else:
                front.append(comp)
        
        # If no back section found, use same components for both
        if not back:
            back = components
        
        return front, back
    
    def _extract_fields(self, template: Template) -> list[str]:
        """Extract all Anki field names from template."""
        fields = set()
        
        for card in template.cards:
            for comp in card.front_components + card.back_components:
                self._collect_fields(comp, fields)
        
        # Remove special fields
        special = {"FrontSide", "Tags", "Type", "Deck", "Subdeck", "CardFlag"}
        return sorted(fields - special)
    
    def _collect_fields(self, comp: Component, fields: set):
        """Recursively collect field names from component tree."""
        if comp.anki_field:
            fields.add(comp.anki_field)
        for child in comp.children:
            self._collect_fields(child, fields)
```

---

## GUI Module: Python-JavaScript Bridge

### `gui/webview_bridge.py`

```python
"""Bridge for Python <-> JavaScript communication via QWebChannel."""
from typing import Callable, Any, Optional
from aqt.qt import QObject, pyqtSlot, pyqtSignal
import json

class WebViewBridge(QObject):
    """
    Bridge object exposed to JavaScript for bidirectional communication.
    
    JavaScript calls methods via: window.bridge.methodName(args)
    Python emits signals that JavaScript listens to.
    """
    
    # Signals (Python -> JavaScript)
    templateLoaded = pyqtSignal(str)        # Emit GrapeJS JSON to load
    fieldsUpdated = pyqtSignal(str)         # Emit available Anki fields
    behaviorsUpdated = pyqtSignal(str)      # Emit AnkiJSApi behaviors
    settingsUpdated = pyqtSignal(str)       # Emit editor settings
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._save_callback: Optional[Callable] = None
        self._preview_callback: Optional[Callable] = None
        self._export_callback: Optional[Callable] = None
    
    # ========== JavaScript -> Python Slots ==========
    
    @pyqtSlot(str)
    def saveProject(self, grapejs_json: str):
        """Called by JS when user saves the project."""
        if self._save_callback:
            try:
                data = json.loads(grapejs_json)
                self._save_callback(data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str)
    def requestPreview(self, grapejs_json: str):
        """Called by JS to request a card preview."""
        if self._preview_callback:
            try:
                data = json.loads(grapejs_json)
                self._preview_callback(data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str, str)
    def exportTemplate(self, format_type: str, grapejs_json: str):
        """Called by JS to export template."""
        if self._export_callback:
            try:
                data = json.loads(grapejs_json)
                self._export_callback(format_type, data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str)
    def log(self, message: str):
        """Called by JS for debug logging."""
        print(f"[GrapeJS] {message}")
    
    @pyqtSlot(str)
    def showError(self, message: str):
        """Called by JS to show error to user."""
        from aqt.utils import showWarning
        showWarning(message, title="Template Designer Error")
    
    @pyqtSlot(result=str)
    def getAnkiFields(self) -> str:
        """Called by JS to get available Anki fields."""
        from ..services.anki_service import AnkiService
        service = AnkiService()
        fields = service.get_available_fields()
        return json.dumps(fields)
    
    @pyqtSlot(result=str)
    def getAnkiBehaviors(self) -> str:
        """Called by JS to get AnkiJSApi behaviors."""
        from ..services.ankijsapi_service import AnkiJSApiService
        service = AnkiJSApiService()
        behaviors = service.get_available_behaviors()
        return json.dumps(behaviors)
    
    # ========== Python API ==========
    
    def set_save_callback(self, callback: Callable[[dict], None]):
        """Set callback for save action."""
        self._save_callback = callback
    
    def set_preview_callback(self, callback: Callable[[dict], None]):
        """Set callback for preview action."""
        self._preview_callback = callback
    
    def set_export_callback(self, callback: Callable[[str, dict], None]):
        """Set callback for export action."""
        self._export_callback = callback
    
    def load_template(self, grapejs_json: dict):
        """Load a template into the editor."""
        self.templateLoaded.emit(json.dumps(grapejs_json))
    
    def update_fields(self, fields: list[str]):
        """Update available Anki fields in editor."""
        self.fieldsUpdated.emit(json.dumps(fields))
    
    def update_behaviors(self, behaviors: list[dict]):
        """Update available AnkiJSApi behaviors in editor."""
        self.behaviorsUpdated.emit(json.dumps(behaviors))
```

### `gui/designer_dialog.py`

```python
"""Main designer dialog with QWebEngineView hosting GrapeJS."""
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QWebEngineView, QWebChannel, QUrl, QSize
)
from aqt import mw
from pathlib import Path
from .webview_bridge import WebViewBridge
from ..services.downloader import GrapeJSDownloader
from ..core.converter import TemplateConverter

class TemplateDesignerDialog(QDialog):
    """Main template designer dialog."""
    
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Anki Template Designer")
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        
        self.converter = TemplateConverter()
        self.bridge = WebViewBridge(self)
        self.webview: QWebEngineView = None
        
        self._setup_ui()
        self._setup_bridge()
        self._ensure_assets()
        self._load_editor()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView for GrapeJS
        self.webview = QWebEngineView(self)
        layout.addWidget(self.webview, stretch=1)
        
        # Bottom toolbar
        toolbar = QHBoxLayout()
        
        self.btn_import = QPushButton("Import HTML")
        self.btn_import.clicked.connect(self._on_import)
        toolbar.addWidget(self.btn_import)
        
        self.btn_export = QPushButton("Export to Anki")
        self.btn_export.clicked.connect(self._on_export)
        toolbar.addWidget(self.btn_export)
        
        toolbar.addStretch()
        
        self.btn_preview = QPushButton("Preview Card")
        self.btn_preview.clicked.connect(self._on_preview)
        toolbar.addWidget(self.btn_preview)
        
        self.btn_save = QPushButton("Save to Note Type")
        self.btn_save.clicked.connect(self._on_save)
        toolbar.addWidget(self.btn_save)
        
        layout.addLayout(toolbar)
    
    def _setup_bridge(self):
        """Setup QWebChannel for Python-JS communication."""
        channel = QWebChannel(self.webview.page())
        channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(channel)
        
        # Set callbacks
        self.bridge.set_save_callback(self._handle_save)
        self.bridge.set_preview_callback(self._handle_preview)
        self.bridge.set_export_callback(self._handle_export)
    
    def _ensure_assets(self):
        """Ensure GrapeJS assets are downloaded."""
        downloader = GrapeJSDownloader()
        if not downloader.assets_exist():
            downloader.download_assets()
    
    def _load_editor(self):
        """Load the GrapeJS editor HTML."""
        addon_path = Path(__file__).parent.parent
        html_path = addon_path / "web" / "index.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(html_path)))
    
    def _on_import(self):
        """Handle import button click."""
        from .import_dialog import ImportDialog
        dialog = ImportDialog(self)
        if dialog.exec():
            html, css = dialog.get_template()
            grapejs_data = self.converter.anki_to_grapejs(html, css)
            self.bridge.load_template(grapejs_data)
    
    def _on_export(self):
        """Handle export button click."""
        # Trigger JS to send current state
        self.webview.page().runJavaScript(
            "window.exportTemplate('html')"
        )
    
    def _on_preview(self):
        """Handle preview button click."""
        self.webview.page().runJavaScript(
            "window.requestPreview()"
        )
    
    def _on_save(self):
        """Handle save button click."""
        self.webview.page().runJavaScript(
            "window.saveProject()"
        )
    
    def _handle_save(self, grapejs_data: dict):
        """Handle save callback from JS."""
        template = self.converter.grapejs_to_anki(grapejs_data)
        # Save to Anki note type
        from ..services.anki_service import AnkiService
        service = AnkiService()
        service.save_template(template)
    
    def _handle_preview(self, grapejs_data: dict):
        """Handle preview callback from JS."""
        from .preview_dialog import PreviewDialog
        template = self.converter.grapejs_to_anki(grapejs_data)
        dialog = PreviewDialog(template, self)
        dialog.exec()
    
    def _handle_export(self, format_type: str, grapejs_data: dict):
        """Handle export callback from JS."""
        from .export_dialog import ExportDialog
        template = self.converter.grapejs_to_anki(grapejs_data)
        dialog = ExportDialog(template, format_type, self)
        dialog.exec()
    
    def load_existing_template(self, html: str, css: str = ""):
        """Load an existing Anki template for editing."""
        grapejs_data = self.converter.anki_to_grapejs(html, css)
        self.bridge.load_template(grapejs_data)
```

---

## Services Module

### `services/downloader.py`

```python
"""Auto-downloader for GrapeJS assets."""
import urllib.request
import ssl
from pathlib import Path
from typing import Optional

class GrapeJSDownloader:
    """Download GrapeJS assets if not present."""
    
    ASSETS = [
        {
            "url": "https://unpkg.com/grapesjs",
            "filename": "grapes.min.js"
        },
        {
            "url": "https://unpkg.com/grapesjs/dist/css/grapes.min.css", 
            "filename": "grapes.min.css"
        }
    ]
    
    def __init__(self):
        self.addon_path = Path(__file__).parent.parent
        self.assets_dir = self.addon_path / "web" / "grapesjs"
    
    def assets_exist(self) -> bool:
        """Check if all required assets exist."""
        for asset in self.ASSETS:
            filepath = self.assets_dir / asset["filename"]
            if not filepath.exists():
                return False
        return True
    
    def download_assets(self, progress_callback: Optional[callable] = None):
        """Download all required assets."""
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SSL context for HTTPS
        ssl_context = ssl.create_default_context()
        
        for i, asset in enumerate(self.ASSETS):
            filepath = self.assets_dir / asset["filename"]
            
            if progress_callback:
                progress_callback(i, len(self.ASSETS), asset["filename"])
            
            if not filepath.exists():
                self._download_file(asset["url"], filepath, ssl_context)
        
        # Create .gitkeep
        gitkeep = self.assets_dir / ".gitkeep"
        gitkeep.touch()
    
    def _download_file(self, url: str, filepath: Path, ssl_context):
        """Download a single file."""
        try:
            with urllib.request.urlopen(url, context=ssl_context, timeout=30) as response:
                content = response.read()
                filepath.write_bytes(content)
        except Exception as e:
            raise RuntimeError(f"Failed to download {url}: {e}")
    
    def get_js_path(self) -> Path:
        """Get path to GrapeJS JavaScript file."""
        return self.assets_dir / "grapes.min.js"
    
    def get_css_path(self) -> Path:
        """Get path to GrapeJS CSS file."""
        return self.assets_dir / "grapes.min.css"
```

### `services/ankijsapi_service.py`

```python
"""AnkiJSApi integration service."""
from typing import Optional

class AnkiJSApiService:
    """Service for AnkiJSApi behavior integration."""
    
    # Available AnkiJSApi behaviors
    BEHAVIORS = [
        # Card Actions
        {"name": "showAnswer", "category": "Card", "description": "Show the answer side of the card"},
        {"name": "flipCard", "category": "Card", "description": "Flip between front and back"},
        {"name": "markCard", "category": "Card", "description": "Toggle card marked status"},
        {"name": "suspendCard", "category": "Card", "description": "Suspend the current card"},
        {"name": "buryCard", "category": "Card", "description": "Bury the current card"},
        
        # Rating Actions  
        {"name": "rateAgain", "category": "Rating", "description": "Rate card as Again"},
        {"name": "rateHard", "category": "Rating", "description": "Rate card as Hard"},
        {"name": "rateGood", "category": "Rating", "description": "Rate card as Good"},
        {"name": "rateEasy", "category": "Rating", "description": "Rate card as Easy"},
        
        # Audio Actions
        {"name": "playAudio", "category": "Audio", "description": "Play audio file"},
        {"name": "replayAudio", "category": "Audio", "description": "Replay all audio"},
        {"name": "pauseAudio", "category": "Audio", "description": "Pause audio playback"},
        {"name": "recordAudio", "category": "Audio", "description": "Record audio (if supported)"},
        
        # Navigation
        {"name": "undoAction", "category": "Navigation", "description": "Undo last action"},
        {"name": "editNote", "category": "Navigation", "description": "Open note editor"},
        {"name": "showDeckOverview", "category": "Navigation", "description": "Show deck overview"},
        
        # Display
        {"name": "toggleNightMode", "category": "Display", "description": "Toggle night mode"},
        {"name": "zoomIn", "category": "Display", "description": "Increase zoom level"},
        {"name": "zoomOut", "category": "Display", "description": "Decrease zoom level"},
        
        # Timer
        {"name": "startTimer", "category": "Timer", "description": "Start a timer"},
        {"name": "stopTimer", "category": "Timer", "description": "Stop the timer"},
        {"name": "resetTimer", "category": "Timer", "description": "Reset the timer"},
        
        # Custom
        {"name": "runCustomJS", "category": "Custom", "description": "Run custom JavaScript"},
        {"name": "showHint", "category": "Custom", "description": "Show hint content"},
        {"name": "hideElement", "category": "Custom", "description": "Hide an element"},
        {"name": "showElement", "category": "Custom", "description": "Show an element"},
        {"name": "toggleElement", "category": "Custom", "description": "Toggle element visibility"},
    ]
    
    def __init__(self):
        self._ankijsapi_available: Optional[bool] = None
    
    def is_available(self) -> bool:
        """Check if AnkiJSApi addon is installed."""
        if self._ankijsapi_available is None:
            try:
                # Try to import AnkiJSApi
                from aqt import mw
                addons = mw.addonManager.allAddons()
                self._ankijsapi_available = any(
                    "ankijsapi" in addon.lower() 
                    for addon in addons
                )
            except:
                self._ankijsapi_available = False
        return self._ankijsapi_available
    
    def get_available_behaviors(self) -> list[dict]:
        """Get list of available behaviors."""
        behaviors = self.BEHAVIORS.copy()
        
        # Mark behaviors as available/unavailable based on AnkiJSApi
        for behavior in behaviors:
            behavior["available"] = self.is_available()
        
        return behaviors
    
    def generate_behavior_js(self, action: str, params: dict = None) -> str:
        """Generate JavaScript code for a behavior."""
        params = params or {}
        
        if action == "showAnswer":
            return "pycmd('ans')"
        elif action == "flipCard":
            return "if(typeof pycmd !== 'undefined') pycmd('ans')"
        elif action.startswith("rate"):
            ease_map = {"rateAgain": 1, "rateHard": 2, "rateGood": 3, "rateEasy": 4}
            ease = ease_map.get(action, 3)
            return f"pycmd('ease{ease}')"
        elif action == "playAudio":
            return "pycmd('play:q:0')"
        elif action == "replayAudio":
            return "pycmd('replay')"
        elif action == "toggleElement":
            target = params.get("target", "this")
            return f"document.querySelector('{target}').classList.toggle('hidden')"
        elif action == "runCustomJS":
            return params.get("code", "")
        else:
            return f"// {action} - implement in AnkiJSApi"
```

---

## Entry Point Updates

### `__init__.py`

```python
"""Anki Template Designer - GrapeJS-based visual template builder."""
from aqt import gui_hooks, mw
from aqt.utils import showInfo

def on_profile_loaded():
    """Initialize addon after profile loads."""
    try:
        from .hooks.menu import setup_menu
        setup_menu()
    except Exception as e:
        showInfo(f"Template Designer initialization error: {e}")

gui_hooks.profile_did_open.append(on_profile_loaded)
```

### `hooks/menu.py`

```python
"""Menu integration for Template Designer."""
from aqt import mw
from aqt.qt import QAction

def setup_menu():
    """Add Template Designer to Tools menu."""
    action = QAction("Template Designer", mw)
    action.setShortcut("Ctrl+Shift+T")
    action.triggered.connect(open_designer)
    mw.form.menuTools.addAction(action)

def open_designer():
    """Open the template designer dialog."""
    from ..gui.designer_dialog import TemplateDesignerDialog
    dialog = TemplateDesignerDialog(mw)
    dialog.exec()
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                    │
└──────────────────────────────────────────────────────────────────────────┘

IMPORT EXISTING TEMPLATE:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│ Anki HTML   │────▶│ parser.py    │────▶│ GrapeJS JSON │────▶│ JS Editor │
│ + CSS       │     │ (parse)      │     │              │     │           │
└─────────────┘     └──────────────┘     └──────────────┘     └───────────┘

EXPORT TO ANKI:
┌───────────┐     ┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│ JS Editor │────▶│ generator.py │────▶│ Template obj  │────▶│ Anki HTML   │
│           │     │ (generate)   │     │               │     │ + CSS + JS  │
└───────────┘     └──────────────┘     └───────────────┘     └─────────────┘

SAVE PROJECT:
┌───────────┐     ┌──────────────┐     ┌──────────────────┐
│ JS Editor │────▶│ bridge.py    │────▶│ .atd JSON file   │
│           │     │ (save)       │     │ (GrapeJS format) │
└───────────┘     └──────────────┘     └──────────────────┘

COMMUNICATION:
┌─────────────────────────────────────────────────────────────────────────┐
│                         QWebChannel Bridge                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   Python                           JavaScript                    │   │
│  │   ──────                           ──────────                    │   │
│  │   bridge.templateLoaded ──────▶ window.onTemplateLoaded()       │   │
│  │   bridge.fieldsUpdated  ──────▶ window.onFieldsUpdated()        │   │
│  │                                                                   │   │
│  │   bridge.saveProject()  ◀────── window.bridge.saveProject()     │   │
│  │   bridge.requestPreview()◀───── window.bridge.requestPreview()  │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

1. **HTML Sanitization**: All imported HTML passes through `utils/security.py`
2. **No eval()**: Never evaluate user-provided JavaScript in Python
3. **CSP Headers**: Set Content-Security-Policy in webview
4. **Input Validation**: Validate all GrapeJS JSON before processing
5. **File Path Validation**: Validate asset paths to prevent directory traversal

---

## Next Plan

See [03-GRAPEJS-INTEGRATION.md](03-GRAPEJS-INTEGRATION.md) for detailed GrapeJS setup, auto-downloader implementation, and JavaScript initialization.
