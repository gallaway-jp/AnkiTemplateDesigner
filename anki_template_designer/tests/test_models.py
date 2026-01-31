"""Tests for data models."""

import pytest
from datetime import datetime
from anki_template_designer.core.models import (
    Component, ComponentType, ComponentStyle, 
    Template, TemplateSide
)


class TestComponentStyle:
    """Tests for ComponentStyle dataclass."""
    
    def test_default_style(self):
        """Test default style has all None values."""
        style = ComponentStyle()
        assert style.background is None
        assert style.color is None
        assert style.font_size is None
    
    def test_to_dict_excludes_none(self):
        """Test to_dict excludes None values."""
        style = ComponentStyle(color="#333")
        data = style.to_dict()
        assert data == {"color": "#333"}
        assert "background" not in data
    
    def test_from_dict_round_trip(self):
        """Test from_dict creates correct instance."""
        original = ComponentStyle(
            color="#333",
            font_size="16px",
            padding="10px"
        )
        data = original.to_dict()
        restored = ComponentStyle.from_dict(data)
        
        assert restored.color == original.color
        assert restored.font_size == original.font_size
        assert restored.padding == original.padding


class TestComponent:
    """Tests for Component dataclass."""
    
    def test_default_component(self):
        """Test default component has sensible defaults."""
        component = Component()
        assert component.type == ComponentType.CONTAINER
        assert component.content == ""
        assert len(component.id) == 8
    
    def test_component_serialization(self):
        """Test component round-trip serialization."""
        component = Component(
            type=ComponentType.TEXT,
            content="Hello World",
            style=ComponentStyle(color="#333", font_size="16px")
        )
        
        data = component.to_dict()
        restored = Component.from_dict(data)
        
        assert restored.type == component.type
        assert restored.content == component.content
        assert restored.style.color == "#333"
    
    def test_component_with_children(self):
        """Test component with children serialization."""
        child = Component(type=ComponentType.TEXT, content="Child")
        parent = Component(
            type=ComponentType.CONTAINER,
            children=[child]
        )
        
        data = parent.to_dict()
        restored = Component.from_dict(data)
        
        assert len(restored.children) == 1
        assert restored.children[0].content == "Child"
    
    def test_component_types(self):
        """Test all component types are valid."""
        for comp_type in ComponentType:
            component = Component(type=comp_type)
            data = component.to_dict()
            restored = Component.from_dict(data)
            assert restored.type == comp_type


class TestTemplateSide:
    """Tests for TemplateSide dataclass."""
    
    def test_default_side(self):
        """Test default side is empty."""
        side = TemplateSide()
        assert side.html == ""
        assert side.components == []
    
    def test_side_serialization(self):
        """Test template side serialization."""
        component = Component(type=ComponentType.TEXT, content="Front")
        side = TemplateSide(
            html="<div>Front</div>",
            components=[component]
        )
        
        data = side.to_dict()
        restored = TemplateSide.from_dict(data)
        
        assert restored.html == side.html
        assert len(restored.components) == 1


class TestTemplate:
    """Tests for Template dataclass."""
    
    def test_default_template(self):
        """Test default template has sensible defaults."""
        template = Template()
        assert template.name == "Untitled Template"
        assert template.version == 1
        assert template.css == ""
    
    def test_template_serialization(self):
        """Test template round-trip serialization."""
        template = Template(name="Test Template")
        template.css = "body { color: red; }"
        
        data = template.to_dict()
        restored = Template.from_dict(data)
        
        assert restored.name == template.name
        assert restored.css == template.css
        assert restored.id == template.id
    
    def test_template_update_modified(self):
        """Test update_modified updates timestamp and version."""
        template = Template()
        original_version = template.version
        original_time = template.modified_at
        
        # Small delay to ensure time difference
        import time
        time.sleep(0.01)
        
        template.update_modified()
        
        assert template.version == original_version + 1
        assert template.modified_at > original_time
    
    def test_template_with_sides(self):
        """Test template with front and back sides."""
        front = TemplateSide(html="<div>Front</div>")
        back = TemplateSide(html="<div>Back</div>")
        
        template = Template(
            name="Two Sided",
            front=front,
            back=back
        )
        
        data = template.to_dict()
        restored = Template.from_dict(data)
        
        assert restored.front.html == "<div>Front</div>"
        assert restored.back.html == "<div>Back</div>"
