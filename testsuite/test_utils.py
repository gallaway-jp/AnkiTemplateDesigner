"""
Test utilities and helpers
"""
from typing import List, Dict, Any
from ui.components import Component
from ui.constraints import Constraint, ConstraintType, ConstraintTarget


class ComponentFactory:
    """Factory for creating test components"""
    
    @staticmethod
    def create_text_field(
        id: str = "textfield",
        text: str = "{{Field}}",
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 50,
        **kwargs
    ) -> Component:
        """Create a TextField component"""
        return Component(
            id=id,
            type="TextField",
            text=text,
            x=x, y=y,
            width=width,
            height=height,
            **kwargs
        )
    
    @staticmethod
    def create_image_view(
        id: str = "imageview",
        image_field: str = "{{Image}}",
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 150,
        **kwargs
    ) -> Component:
        """Create an ImageView component"""
        return Component(
            id=id,
            type="ImageView",
            image_field=image_field,
            x=x, y=y,
            width=width,
            height=height,
            **kwargs
        )
    
    @staticmethod
    def create_button(
        id: str = "button",
        text: str = "Click",
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        **kwargs
    ) -> Component:
        """Create a Button component"""
        return Component(
            id=id,
            type="Button",
            text=text,
            x=x, y=y,
            width=width,
            height=height,
            **kwargs
        )
    
    @staticmethod
    def create_container(
        id: str = "container",
        x: int = 0,
        y: int = 0,
        width: int = 300,
        height: int = 400,
        **kwargs
    ) -> Component:
        """Create a Container component"""
        return Component(
            id=id,
            type="Container",
            x=x, y=y,
            width=width,
            height=height,
            **kwargs
        )
    
    @staticmethod
    def create_constrained_component(
        id: str = "constrained",
        type: str = "TextField",
        constraints: List[Dict] = None,
        h_bias: float = 0.5,
        v_bias: float = 0.5,
        **kwargs
    ) -> Component:
        """Create a component with constraints"""
        comp = Component(
            id=id,
            type=type,
            use_constraints=True,
            constraint_horizontal_bias=h_bias,
            constraint_vertical_bias=v_bias,
            **kwargs
        )
        
        if constraints:
            comp.constraints = constraints
        
        return comp


class ConstraintFactory:
    """Factory for creating test constraints"""
    
    @staticmethod
    def create_parent_left(
        component_id: str,
        margin: int = 0
    ) -> Constraint:
        """Create left-to-parent-left constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.LEFT_TO_LEFT,
            target=ConstraintTarget.PARENT,
            margin=margin
        )
    
    @staticmethod
    def create_parent_top(
        component_id: str,
        margin: int = 0
    ) -> Constraint:
        """Create top-to-parent-top constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.TOP_TO_TOP,
            target=ConstraintTarget.PARENT,
            margin=margin
        )
    
    @staticmethod
    def create_parent_right(
        component_id: str,
        margin: int = 0
    ) -> Constraint:
        """Create right-to-parent-right constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.RIGHT_TO_RIGHT,
            target=ConstraintTarget.PARENT,
            margin=margin
        )
    
    @staticmethod
    def create_parent_bottom(
        component_id: str,
        margin: int = 0
    ) -> Constraint:
        """Create bottom-to-parent-bottom constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.BOTTOM_TO_BOTTOM,
            target=ConstraintTarget.PARENT,
            margin=margin
        )
    
    @staticmethod
    def create_component_constraint(
        source_id: str,
        target_id: str,
        constraint_type: ConstraintType,
        margin: int = 0
    ) -> Constraint:
        """Create component-to-component constraint"""
        return Constraint(
            source_component_id=source_id,
            constraint_type=constraint_type,
            target=ConstraintTarget.COMPONENT,
            target_component_id=target_id,
            margin=margin
        )
    
    @staticmethod
    def create_center_horizontal(component_id: str) -> Constraint:
        """Create horizontal centering constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.CENTER_HORIZONTAL,
            target=ConstraintTarget.PARENT
        )
    
    @staticmethod
    def create_center_vertical(component_id: str) -> Constraint:
        """Create vertical centering constraint"""
        return Constraint(
            source_component_id=component_id,
            constraint_type=ConstraintType.CENTER_VERTICAL,
            target=ConstraintTarget.PARENT
        )


class TemplateFactory:
    """Factory for creating test templates"""
    
    @staticmethod
    def create_basic_template() -> Dict[str, Any]:
        """Create a basic Anki template"""
        return {
            'name': 'Basic',
            'id': 1234567890,
            'css': '.card { font-family: arial; }',
            'tmpls': [
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
                    'ord': 0
                }
            ],
            'flds': [
                {'name': 'Front', 'ord': 0},
                {'name': 'Back', 'ord': 1}
            ]
        }
    
    @staticmethod
    def create_cloze_template() -> Dict[str, Any]:
        """Create a cloze deletion template"""
        return {
            'name': 'Cloze',
            'id': 1234567891,
            'css': '.card { font-family: arial; }',
            'tmpls': [
                {
                    'name': 'Cloze',
                    'qfmt': '{{cloze:Text}}',
                    'afmt': '{{cloze:Text}}<br>{{Extra}}',
                    'ord': 0
                }
            ],
            'flds': [
                {'name': 'Text', 'ord': 0},
                {'name': 'Extra', 'ord': 1}
            ]
        }
    
    @staticmethod
    def create_multi_card_template() -> Dict[str, Any]:
        """Create template with multiple cards"""
        return {
            'name': 'Multi-Card',
            'id': 1234567892,
            'css': '.card { font-family: arial; }',
            'tmpls': [
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{Back}}',
                    'ord': 0
                },
                {
                    'name': 'Card 2',
                    'qfmt': '{{Back}}',
                    'afmt': '{{Front}}',
                    'ord': 1
                }
            ],
            'flds': [
                {'name': 'Front', 'ord': 0},
                {'name': 'Back', 'ord': 1}
            ]
        }


class AssertionHelpers:
    """Helper methods for common assertions"""
    
    @staticmethod
    def assert_component_equal(comp1: Component, comp2: Component, check_id: bool = True):
        """Assert that two components are equal"""
        if check_id:
            assert comp1.id == comp2.id
        
        assert comp1.type == comp2.type
        assert comp1.x == comp2.x
        assert comp1.y == comp2.y
        assert comp1.width == comp2.width
        assert comp1.height == comp2.height
        
        if hasattr(comp1, 'text') and hasattr(comp2, 'text'):
            assert comp1.text == comp2.text
    
    @staticmethod
    def assert_constraint_equal(c1: Constraint, c2: Constraint):
        """Assert that two constraints are equal"""
        assert c1.source_component_id == c2.source_component_id
        assert c1.constraint_type == c2.constraint_type
        assert c1.target == c2.target
        assert c1.target_component_id == c2.target_component_id
        assert c1.margin == c2.margin
    
    @staticmethod
    def assert_position_near(pos1: Dict[str, int], pos2: Dict[str, int], tolerance: int = 2):
        """Assert that two positions are approximately equal"""
        assert abs(pos1['x'] - pos2['x']) <= tolerance
        assert abs(pos1['y'] - pos2['y']) <= tolerance
        assert abs(pos1['width'] - pos2['width']) <= tolerance
        assert abs(pos1['height'] - pos2['height']) <= tolerance
    
    @staticmethod
    def assert_html_contains_fields(html: str, fields: List[str]):
        """Assert that HTML contains Anki field references"""
        for field in fields:
            # Check for {{Field}} format
            assert f"{{{{{field}}}}}" in html or field in html
    
    @staticmethod
    def assert_css_contains_rules(css: str, rules: List[str]):
        """Assert that CSS contains specific rules"""
        for rule in rules:
            assert rule in css


def create_test_layout(layout_type: str) -> List[Component]:
    """
    Create predefined test layouts
    
    Args:
        layout_type: 'simple', 'two-column', 'header-content-footer', 'grid'
    
    Returns:
        List of components forming the layout
    """
    factory = ComponentFactory()
    
    if layout_type == 'simple':
        return [
            factory.create_text_field(id="title", text="{{Title}}", y=20, height=60),
            factory.create_text_field(id="content", text="{{Content}}", y=100, height=200)
        ]
    
    elif layout_type == 'two-column':
        return [
            factory.create_container(id="left", x=0, width=180),
            factory.create_container(id="right", x=200, width=180)
        ]
    
    elif layout_type == 'header-content-footer':
        return [
            factory.create_text_field(id="header", text="{{Header}}", y=0, height=50),
            factory.create_text_field(id="content", text="{{Content}}", y=60, height=300),
            factory.create_text_field(id="footer", text="{{Footer}}", y=370, height=30)
        ]
    
    elif layout_type == 'grid':
        components = []
        for i in range(4):
            for j in range(3):
                comp_id = f"cell_{i}_{j}"
                x = j * 120 + 10
                y = i * 100 + 10
                components.append(
                    factory.create_text_field(id=comp_id, text=f"Cell {i},{j}", x=x, y=y, width=100, height=80)
                )
        return components
    
    else:
        raise ValueError(f"Unknown layout type: {layout_type}")
