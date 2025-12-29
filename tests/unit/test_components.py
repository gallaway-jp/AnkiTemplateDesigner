"""
Unit tests for Component class (ui/components.py)

Tests cover:
- Component creation and initialization
- Component property management
- Constraint-related fields
"""
import pytest
from ui.components import (
    Component, ComponentType, TextFieldComponent, ImageFieldComponent,
    HeadingComponent, ContainerComponent, Alignment
)


class TestComponentCreation:
    """Test Component instantiation"""
    
    def test_basic_component_creation(self):
        """Test creating a basic component"""
        comp = TextFieldComponent(field_name="Front")
        
        assert comp.type == ComponentType.TEXT_FIELD
        assert comp.field_name == "Front"
        assert comp.width == "100%"
        assert comp.height == "auto"
    
    def test_component_with_defaults(self):
        """Test default values are applied"""
        comp = Component(ComponentType.BUTTON, field_name="TestButton")
        
        assert comp.type == ComponentType.BUTTON
        assert comp.field_name == "TestButton"
        assert comp.font_family == "Arial, sans-serif"
        assert comp.font_size == 20
    
    def test_all_component_types(self):
        """Test creating each supported component type"""
        # TextFieldComponent
        text_comp = TextFieldComponent("Test")
        assert text_comp.type == ComponentType.TEXT_FIELD
        
        # ImageFieldComponent
        img_comp = ImageFieldComponent("Image")
        assert img_comp.type == ComponentType.IMAGE_FIELD
        
        # HeadingComponent
        heading_comp = HeadingComponent("Title", level=1)
        assert heading_comp.type == ComponentType.HEADING
        
        # ContainerComponent
        container_comp = ContainerComponent()
        assert container_comp.type == ComponentType.CONTAINER


class TestComponentProperties:
    """Test component property management"""
    
    def test_text_field_properties(self):
        """Test TextField-specific properties"""
        comp = TextFieldComponent(field_name="Front")
        comp.font_family = "Arial"
        comp.font_size = 14
        comp.color = "#000000"
        comp.font_weight = "bold"
        
        assert comp.font_family == "Arial"
        assert comp.font_size == 14
        assert comp.color == "#000000"
        assert comp.font_weight == "bold"
    
    def test_image_view_properties(self):
        """Test ImageView-specific properties"""
        comp = ImageFieldComponent(field_name="Image")
        comp.max_width = "300px"
        comp.max_height = "200px"
        
        assert comp.max_width == "300px"
        assert comp.max_height == "200px"
    
    def test_heading_properties(self):
        """Test Heading-specific properties"""
        comp = HeadingComponent(field_name="Title", level=2)
        
        assert comp.level == 2
        assert comp.font_weight == "bold"
        assert comp.font_size == 24  # h2 default
    
    def test_property_updates(self):
        """Test updating component properties"""
        comp = TextFieldComponent(field_name="Test")
        
        comp.field_name = "Updated"
        comp.font_size = 18
        comp.color = "#ff0000"
        
        assert comp.field_name == "Updated"
        assert comp.font_size == 18
        assert comp.color == "#ff0000"


class TestConstraintFields:
    """Test constraint-related component fields"""
    
    def test_default_constraint_fields(self):
        """Test default constraint field values"""
        comp = TextFieldComponent(field_name="Test")
        
        assert hasattr(comp, 'use_constraints')
        assert hasattr(comp, 'constraints')
        assert hasattr(comp, 'constraint_horizontal_bias')
        assert hasattr(comp, 'constraint_vertical_bias')
        
        assert comp.use_constraints is True
        assert comp.constraints == []
        assert comp.constraint_horizontal_bias == 0.5
        assert comp.constraint_vertical_bias == 0.5
    
    def test_enable_constraints(self):
        """Test enabling constraint layout"""
        comp = TextFieldComponent(field_name="Test")
        comp.use_constraints = True
        
        assert comp.use_constraints is True
    
    def test_add_constraints(self):
        """Test adding constraints to component"""
        comp = TextFieldComponent(field_name="Test")
        
        comp.constraints.append({
            'source_component_id': id(comp),
            'constraint_type': 'LEFT_TO_LEFT',
            'target': 'PARENT',
            'margin': 10
        })
        
        assert len(comp.constraints) == 1
        assert comp.constraints[0]['constraint_type'] == 'LEFT_TO_LEFT'
    
    def test_bias_values(self):
        """Test setting bias values"""
        comp = TextFieldComponent(field_name="Test")
        comp.constraint_horizontal_bias = 0.25
        comp.constraint_vertical_bias = 0.75
        
        assert comp.constraint_horizontal_bias == 0.25
        assert comp.constraint_vertical_bias == 0.75
    
    def test_bias_range_validation(self):
        """Test that bias values are between 0 and 1"""
        comp = TextFieldComponent(field_name="Test")
        
        # Valid values
        comp.constraint_horizontal_bias = 0.0
        assert comp.constraint_horizontal_bias == 0.0
        
        comp.constraint_horizontal_bias = 1.0
        assert comp.constraint_horizontal_bias == 1.0
        
        comp.constraint_horizontal_bias = 0.5
        assert comp.constraint_horizontal_bias == 0.5


class TestComponentHierarchy:
    """Test component parent-child relationships"""
    
    def test_container_children(self):
        """Test container with multiple children"""
        container = ContainerComponent()
        child1 = TextFieldComponent(field_name="Child1")
        child2 = TextFieldComponent(field_name="Child2")
        
        container.add_child(child1)
        container.add_child(child2)
        
        assert len(container.children) == 2
        assert child1 in container.children
        assert child2 in container.children


class TestComponentMethods:
    """Test component methods"""
    
    def test_to_html(self):
        """Test HTML generation"""
        comp = TextFieldComponent(field_name="Front")
        html = comp.to_html()
        
        assert html is not None
        assert "{{Front}}" in html
    
    def test_to_css(self):
        """Test CSS generation"""
        comp = TextFieldComponent(field_name="Front")
        comp.font_size = 16
        comp.color = "#333333"
        
        css = comp.to_css(".test-selector")
        
        assert css is not None
        assert ".test-selector" in css
        assert "font-size: 16px" in css
        assert "color: #333333" in css
    
    def test_clone(self):
        """Test component cloning"""
        comp = TextFieldComponent(field_name="Original")
        comp.font_size = 18
        comp.color = "#ff0000"
        
        cloned = comp.clone()
        
        assert cloned.field_name == comp.field_name
        assert cloned.font_size == comp.font_size
        assert cloned.color == comp.color
        assert cloned is not comp  # Different instance
