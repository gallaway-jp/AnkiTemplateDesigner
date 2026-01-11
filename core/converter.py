"""Template conversion between Anki HTML and GrapeJS formats.

This module handles bidirectional conversion:
- AnkiHTMLParser: Parse existing Anki templates to Component tree
- AnkiTemplateParser: Parse complete templates to GrapeJS project format
- AnkiTemplateGenerator: Generate Anki templates from GrapeJS data
"""

import re
import json
from html.parser import HTMLParser
from typing import Optional, List, Dict, Any
from .models import Template, TemplateCard, Component, ComponentStyle, AnkiBehavior, CardSide


class AnkiHTMLParser(HTMLParser):
    """Parse Anki template HTML into Component tree."""
    
    def __init__(self):
        super().__init__()
        self.root_components: List[Component] = []
        self._stack: List[Component] = []
        self._component_counter = 0
    
    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Handle opening HTML tags."""
        # Create component
        comp = Component(
            id=f"comp-{self._component_counter}",
            type=self._get_component_type(tag),
            tag_name=tag,
        )
        self._component_counter += 1
        
        # Parse attributes
        for attr_name, attr_value in attrs:
            if attr_name == "class":
                comp.style.css_class = attr_value
            elif attr_name == "id":
                comp.attributes["id"] = attr_value
            elif attr_name.startswith("data-anki-"):
                # Parse Anki behavior attributes
                trigger = attr_name.replace("data-anki-", "")
                behavior = AnkiBehavior(
                    action=attr_value,
                    trigger=trigger
                )
                comp.behaviors.append(behavior)
            else:
                comp.attributes[attr_name] = attr_value
        
        # Add to stack
        if self._stack:
            self._stack[-1].children.append(comp)
        else:
            self.root_components.append(comp)
        
        self._stack.append(comp)
    
    def handle_endtag(self, tag: str):
        """Handle closing HTML tags."""
        if self._stack and self._stack[-1].tag_name == tag:
            self._stack.pop()
    
    def handle_data(self, data: str):
        """Handle text content."""
        if not self._stack:
            return
        
        text = data.strip()
        if not text:
            return
        
        current = self._stack[-1]
        
        # Check for Anki field syntax {{Field}}
        anki_field = self._extract_anki_field(text)
        if anki_field:
            current.anki_field = anki_field
            current.content = text  # Keep original {{Field}} syntax
        else:
            current.content = text
    
    def _get_component_type(self, tag: str) -> str:
        """Map HTML tag to GrapeJS component type."""
        mapping = {
            "div": "default",
            "span": "text",
            "p": "text",
            "h1": "text",
            "h2": "text",
            "h3": "text",
            "h4": "text",
            "h5": "text",
            "h6": "text",
            "img": "image",
            "a": "link",
            "video": "video",
            "table": "table",
            "thead": "thead",
            "tbody": "tbody",
            "tr": "row",
            "td": "cell",
            "th": "cell",
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
        
        Args:
            html: Template HTML content
            css: Template CSS content
            js: Template JavaScript (for reference)
            
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
    
    def parse_html(self, html: str) -> List[Component]:
        """Parse HTML string into Component objects."""
        parser = AnkiHTMLParser()
        parser.feed(html)
        return parser.root_components
    
    def _components_to_grapejs(self, components: List[Component]) -> List[dict]:
        """Convert Component objects to GrapeJS component format."""
        result = []
        for comp in components:
            gjs_comp = {
                "type": comp.type,
                "tagName": comp.tag_name,
                "attributes": comp.attributes.copy(),
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
    
    def _parse_css(self, css: str) -> List[dict]:
        """Parse CSS into GrapeJS styles format."""
        # Simplified CSS parsing - full implementation would use cssutils
        # For now, return empty list and let GrapeJS handle inline styles
        return []
    
    def _serialize_behaviors(self, behaviors: List[AnkiBehavior]) -> str:
        """Serialize behaviors to JSON string for data attribute."""
        return json.dumps([{
            "action": b.action,
            "trigger": b.trigger,
            "target": b.target_selector,
            "params": b.params
        } for b in behaviors])


class AnkiTemplateGenerator:
    """Generate Anki-compatible templates from GrapeJS data."""
    
    # Self-closing HTML tags
    VOID_ELEMENTS = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
    
    def generate(self, grapejs_json: dict, template_name: str = "Generated Template") -> Template:
        """
        Generate complete Anki Template from GrapeJS project.
        
        Args:
            grapejs_json: GrapeJS editor.getProjectData() output
            template_name: Name for the generated template
            
        Returns:
            Template object ready for Anki
        """
        template = Template(
            name=template_name,
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
    
    def components_to_html(self, components: List[Component]) -> str:
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
            if key not in ("id", "class", "data-anki-field", "data-anki-behaviors"):
                attrs.append(f'{key}="{value}"')
        
        # Add AnkiDroidJS behavior attributes
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
            attributes=gjs_comp.get("attributes", {}).copy()
        )
        
        # Parse classes
        classes = gjs_comp.get("classes", [])
        if classes:
            if isinstance(classes, list):
                comp.style.css_class = " ".join(str(c) for c in classes)
            else:
                comp.style.css_class = str(classes)
        
        # Parse Anki field
        if "data-anki-field" in comp.attributes:
            comp.anki_field = comp.attributes["data-anki-field"]
        
        # Parse behaviors
        if "data-anki-behaviors" in comp.attributes:
            behaviors_json = comp.attributes["data-anki-behaviors"]
            behaviors_list = json.loads(behaviors_json)
            for b_dict in behaviors_list:
                behavior = AnkiBehavior(
                    action=b_dict.get("action", ""),
                    trigger=b_dict.get("trigger", "click"),
                    target_selector=b_dict.get("target", ""),
                    params=b_dict.get("params", {})
                )
                comp.behaviors.append(behavior)
        
        # Parse children
        children = gjs_comp.get("components", [])
        if isinstance(children, list):
            for child_dict in children:
                child_comp = self._grapejs_to_component(child_dict)
                comp.children.append(child_comp)
        
        return comp
    
    def _split_front_back(self, components: List[dict]) -> tuple[List[dict], List[dict]]:
        """Split components into front and back based on markers.
        
        For now, assumes all components are front. Real implementation would
        look for data-card-side attributes or special markers.
        """
        front = []
        back = []
        
        for comp in components:
            # Check for card side marker
            card_side = comp.get("attributes", {}).get("data-card-side", "front")
            if card_side == "back":
                back.append(comp)
            else:
                front.append(comp)
        
        # If no back components found, assume all are front
        if not back:
            return components, []
        
        return front, back
    
    def _extract_fields(self, template: Template) -> List[str]:
        """Extract all Anki field names from template components."""
        fields = set()
        
        for card in template.cards:
            self._collect_fields(card.front_components, fields)
            self._collect_fields(card.back_components, fields)
        
        return sorted(list(fields))
    
    def _collect_fields(self, components: List[Component], fields: set):
        """Recursively collect field names from component tree."""
        for comp in components:
            if comp.anki_field:
                fields.add(comp.anki_field)
            self._collect_fields(comp.children, fields)
