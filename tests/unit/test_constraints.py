"""
Unit tests for the constraint system (ui/constraints.py)

Tests cover:
- ConstraintType enum
- Constraint dataclass creation and serialization
- ConstraintSet operations
- ConstraintResolver position calculation
- ConstraintHelper utility methods
"""
import pytest
from ui.constraints import (
    ConstraintType, Constraint, ConstraintSet, 
    ConstraintResolver, ConstraintHelper, ConstraintTarget
)
from ui.components import Component


class TestConstraintType:
    """Test ConstraintType enum"""
    
    def test_all_types_defined(self):
        """Verify all constraint types exist"""
        expected_types = [
            'LEFT_TO_LEFT', 'LEFT_TO_RIGHT', 'RIGHT_TO_LEFT', 'RIGHT_TO_RIGHT',
            'TOP_TO_TOP', 'TOP_TO_BOTTOM', 'BOTTOM_TO_TOP', 'BOTTOM_TO_BOTTOM',
            'START_TO_START', 'START_TO_END', 'END_TO_START', 'END_TO_END',
            'CENTER_HORIZONTAL', 'CENTER_VERTICAL'
        ]
        
        for type_name in expected_types:
            assert hasattr(ConstraintType, type_name)
    
    def test_unique_values(self):
        """Ensure all constraint types have unique values"""
        values = [ct.value for ct in ConstraintType]
        assert len(values) == len(set(values))


class TestConstraint:
    """Test Constraint dataclass"""
    
    def test_constraint_creation(self):
        """Test creating a constraint"""
        c = Constraint(
            source_component_id="comp1",
            constraint_type=ConstraintType.LEFT_TO_LEFT,
            target=ConstraintTarget.PARENT,
            margin=10
        )
        
        assert c.source_component_id == "comp1"
        assert c.constraint_type == ConstraintType.LEFT_TO_LEFT
        assert c.target == ConstraintTarget.PARENT
        assert c.target_component_id is None
        assert c.margin == 10
    
    def test_constraint_to_component(self):
        """Test constraint to another component"""
        c = Constraint(
            source_component_id="comp1",
            constraint_type=ConstraintType.LEFT_TO_RIGHT,
            target=ConstraintTarget.COMPONENT,
            target_component_id="comp2",
            margin=5
        )
        
        assert c.target == ConstraintTarget.COMPONENT
        assert c.target_component_id == "comp2"
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        c = Constraint(
            source_component_id=123,
            constraint_type=ConstraintType.TOP_TO_BOTTOM,
            target=ConstraintTarget.COMPONENT,
            target_component_id=456,
            margin=15
        )
        
        d = c.to_dict()
        
        assert d['source_component_id'] == 123
        assert d['constraint_type'] == "top_to_bottom"  # Enum .value is lowercase
        assert d['target'] == "component"  # Enum .value is lowercase
        assert d['target_component_id'] == 456
        assert d['margin'] == 15
    
    def test_from_dict(self):
        """Test deserialization from dictionary"""
        d = {
            'source_component_id': 123,
            'constraint_type': 'right_to_right',  # Lowercase enum value
            'target': 'parent',  # Lowercase enum value
            'target_component_id': None,
            'margin': 20
        }
        
        c = Constraint.from_dict(d)
        
        assert c.source_component_id == 123
        assert c.constraint_type == ConstraintType.RIGHT_TO_RIGHT
        assert c.target == ConstraintTarget.PARENT
        assert c.margin == 20
    
    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves data"""
        original = Constraint(
            source_component_id="test",
            constraint_type=ConstraintType.CENTER_HORIZONTAL,
            target=ConstraintTarget.PARENT
        )
        
        reconstructed = Constraint.from_dict(original.to_dict())
        
        assert reconstructed.source_component_id == original.source_component_id
        assert reconstructed.constraint_type == original.constraint_type
        assert reconstructed.target == original.target
        assert reconstructed.margin == original.margin


class TestConstraintSet:
    """Test ConstraintSet manager"""
    
    def test_empty_set(self):
        """Test creating empty constraint set"""
        cs = ConstraintSet()
        assert len(cs.get_constraints("comp1")) == 0
    
    def test_add_constraint(self):
        """Test adding constraints"""
        cs = ConstraintSet()
        c = Constraint(
            source_component_id="comp1",
            constraint_type=ConstraintType.LEFT_TO_LEFT,
            target=ConstraintTarget.PARENT
        )
        
        cs.add_constraint(c)
        
        constraints = cs.get_constraints("comp1")
        assert len(constraints) == 1
        assert constraints[0].constraint_type == ConstraintType.LEFT_TO_LEFT
    
    def test_add_multiple_constraints(self):
        """Test adding multiple constraints to same component"""
        cs = ConstraintSet()
        
        cs.add_constraint(Constraint("comp1", ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint("comp1", ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint("comp2", ConstraintType.LEFT_TO_RIGHT, ConstraintTarget.COMPONENT, "comp1"))
        
        assert len(cs.get_constraints("comp1")) == 2
        assert len(cs.get_constraints("comp2")) == 1
        assert len(cs.get_constraints("comp3")) == 0
    
    def test_remove_constraint(self):
        """Test removing constraints"""
        cs = ConstraintSet()
        c1 = Constraint(123, ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT)
        c2 = Constraint(123, ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT)
        
        cs.add_constraint(c1)
        cs.add_constraint(c2)
        cs.remove_constraint(123, ConstraintType.LEFT_TO_LEFT)
        
        constraints = cs.get_constraints(123)
        assert len(constraints) == 1
        assert constraints[0].constraint_type == ConstraintType.TOP_TO_TOP
    
    def test_clear_constraints(self):
        """Test clearing all constraints for a component"""
        cs = ConstraintSet()
        
        cs.add_constraint(Constraint("comp1", ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint("comp1", ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT))
        
        cs.clear_constraints("comp1")
        
        assert len(cs.get_constraints("comp1")) == 0
    
    def test_to_dict(self):
        """Test serialization of constraint set"""
        cs = ConstraintSet()
        cs.add_constraint(Constraint("comp1", ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint("comp2", ConstraintType.TOP_TO_BOTTOM, ConstraintTarget.COMPONENT, "comp1"))
        
        d = cs.to_dict()
        
        assert 'comp1' in d
        assert 'comp2' in d
        assert len(d['comp1']) == 1
        assert len(d['comp2']) == 1
    
    def test_from_dict(self):
        """Test deserialization of constraint set"""
        d = {
            123: [
                {
                    'source_component_id': 123,
                    'constraint_type': 'left_to_left',  # Lowercase
                    'target': 'parent',  # Lowercase
                    'target_component_id': None,
                    'margin': 0
                }
            ]
        }
        
        cs = ConstraintSet.from_dict(d)
        
        assert len(cs.get_constraints(123)) == 1


class TestConstraintResolver:
    """Test ConstraintResolver position calculation"""
    
    def test_simple_parent_constraints(self):
        """Test component aligned to parent edges"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Test")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        
        cs = ConstraintSet()
        cs.add_constraint(Constraint(id(comp1), ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT, margin=10))
        cs.add_constraint(Constraint(id(comp1), ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT, margin=10))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        assert id(comp1) in positions
        pos = positions[id(comp1)]
        assert pos['x'] == 10
        assert pos['y'] == 10
        assert pos['width'] == 100
        assert pos['height'] == 50
    
    def test_right_edge_constraint(self):
        """Test component aligned to parent right edge"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Test")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        
        cs = ConstraintSet()
        cs.add_constraint(Constraint(id(comp1), ConstraintType.RIGHT_TO_RIGHT, ConstraintTarget.PARENT, margin=10))
        cs.add_constraint(Constraint(id(comp1), ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        pos = positions[id(comp1)]
        # Right edge should be at parent_width - margin
        # So x = (parent_width - margin) - width = 400 - 10 - 100 = 290
        assert pos['x'] == 290
    
    def test_component_to_component_constraint(self):
        """Test component positioned relative to another component"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Comp1")
        comp1.width = 100
        comp1.height = 50
        comp2 = TextFieldComponent(field_name="Comp2")
        comp2.width = 100
        comp2.height = 50
        components = [comp1, comp2]
        
        cs = ConstraintSet()
        # comp1 at top-left
        cs.add_constraint(Constraint(id(comp1), ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT, margin=10))
        cs.add_constraint(Constraint(id(comp1), ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT, margin=10))
        
        # comp2 below comp1
        cs.add_constraint(Constraint(id(comp2), ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT, margin=10))
        cs.add_constraint(Constraint(id(comp2), ConstraintType.TOP_TO_BOTTOM, ConstraintTarget.COMPONENT, target_component_id=id(comp1), margin=5))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        pos1 = positions[id(comp1)]
        pos2 = positions[id(comp2)]
        
        assert pos1['x'] == 10
        assert pos1['y'] == 10
        assert pos2['x'] == 10
        # comp2 should start 5px below comp1's bottom (10 + 50 + 5 = 65)
        assert pos2['y'] == 65
    
    def test_center_horizontal(self):
        """Test horizontal centering"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Test")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        
        cs = ConstraintSet()
        cs.add_constraint(Constraint(id(comp1), ConstraintType.CENTER_HORIZONTAL, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint(id(comp1), ConstraintType.TOP_TO_TOP, ConstraintTarget.PARENT))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        pos = positions[id(comp1)]
        # Centered: x = (400 - 100) / 2 = 150
        assert pos['x'] == 150
    
    def test_center_vertical(self):
        """Test vertical centering"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Test")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        
        cs = ConstraintSet()
        cs.add_constraint(Constraint(id(comp1), ConstraintType.LEFT_TO_LEFT, ConstraintTarget.PARENT))
        cs.add_constraint(Constraint(id(comp1), ConstraintType.CENTER_VERTICAL, ConstraintTarget.PARENT))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        pos = positions[id(comp1)]
        # Centered: y = (600 - 50) / 2 = 275
        assert pos['y'] == 275
    
    def test_bias_application(self):
        """Test horizontal and vertical bias"""
        from ui.components import TextFieldComponent
        
        comp = TextFieldComponent(field_name="Test")
        comp.width = 100
        comp.height = 50
        comp.constraint_horizontal_bias = 0.25
        comp.constraint_vertical_bias = 0.75
        components = [comp]
        
        cs = ConstraintSet()
        # No specific constraints, bias should apply
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        pos = positions[id(comp)]
        # With bias 0.25: x = (400 - 100) * 0.25 = 75
        # With bias 0.75: y = (600 - 50) * 0.75 = 412.5 -> 412
        assert pos['x'] == 75
        assert pos['y'] == 412


class TestConstraintHelper:
    """Test ConstraintHelper utility methods"""
    
    def test_create_centered_constraints(self):
        """Test creating constraints for centering"""
        comp_id = 123
        constraints = ConstraintHelper.create_centered_constraints(comp_id)
        
        assert len(constraints) == 2
        
        # Check for CENTER_HORIZONTAL and CENTER_VERTICAL
        types = [c.constraint_type for c in constraints]
        assert ConstraintType.CENTER_HORIZONTAL in types
        assert ConstraintType.CENTER_VERTICAL in types
        
        for c in constraints:
            assert c.source_component_id == comp_id
            assert c.target == ConstraintTarget.PARENT
    
    def test_create_match_parent_constraints(self):
        """Test creating constraints to match parent size"""
        comp_id = 456
        constraints = ConstraintHelper.create_match_parent_constraints(comp_id, margin=8)
        
        assert len(constraints) == 4
        
        # Should have all four edges constrained
        types = [c.constraint_type for c in constraints]
        assert ConstraintType.LEFT_TO_LEFT in types
        assert ConstraintType.TOP_TO_TOP in types
        assert ConstraintType.RIGHT_TO_RIGHT in types
        assert ConstraintType.BOTTOM_TO_BOTTOM in types
        
        # All should have the specified margin
        for c in constraints:
            assert c.margin == 8
    
    def test_create_chain_constraints_horizontal(self):
        """Test creating horizontal chain"""
        comp_ids = [111, 222, 333]
        constraints = ConstraintHelper.create_chain_constraints(comp_ids, vertical=False)
        
        # Should create constraints linking each component to the next
        assert len(constraints) > 0
        
        # First component should be anchored to parent left
        first_constraints = [c for c in constraints if c.source_component_id == 111]
        assert any(c.constraint_type == ConstraintType.LEFT_TO_LEFT for c in first_constraints)
        
        # Middle component should be anchored to previous component's right
        middle_constraints = [c for c in constraints if c.source_component_id == 222]
        assert any(
            c.constraint_type == ConstraintType.LEFT_TO_RIGHT and 
            c.target_component_id == 111
            for c in middle_constraints
        )
    
    def test_create_chain_constraints_vertical(self):
        """Test creating vertical chain"""
        comp_ids = [111, 222, 333]
        constraints = ConstraintHelper.create_chain_constraints(comp_ids, vertical=True)
        
        # First component should be anchored to parent top
        first_constraints = [c for c in constraints if c.source_component_id == 111]
        assert any(c.constraint_type == ConstraintType.TOP_TO_TOP for c in first_constraints)
        
        # Middle component should be anchored to previous component's bottom
        middle_constraints = [c for c in constraints if c.source_component_id == 222]
        assert any(
            c.constraint_type == ConstraintType.TOP_TO_BOTTOM and 
            c.target_component_id == 111
            for c in middle_constraints
        )


class TestConstraintEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_circular_dependency_handling(self):
        """Test that circular dependencies don't crash resolver"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Comp1")
        comp1.width = 100
        comp1.height = 50
        comp2 = TextFieldComponent(field_name="Comp2")
        comp2.width = 100
        comp2.height = 50
        components = [comp1, comp2]
        
        cs = ConstraintSet()
        # Create circular dependency
        cs.add_constraint(Constraint(id(comp1), ConstraintType.LEFT_TO_RIGHT, ConstraintTarget.COMPONENT, target_component_id=id(comp2)))
        cs.add_constraint(Constraint(id(comp2), ConstraintType.LEFT_TO_RIGHT, ConstraintTarget.COMPONENT, target_component_id=id(comp1)))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        
        # Should not crash, should return fallback positions
        positions = resolver.resolve(components, cs)
        assert len(positions) == 2
    
    def test_missing_target_component(self):
        """Test constraint referencing non-existent component"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Comp1")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        
        cs = ConstraintSet()
        cs.add_constraint(Constraint(id(comp1), ConstraintType.LEFT_TO_RIGHT, ConstraintTarget.COMPONENT, target_component_id=999999))
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        # Should still return a position (fallback)
        assert id(comp1) in positions
    
    def test_empty_components_list(self):
        """Test resolver with no components"""
        components = []
        cs = ConstraintSet()
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        assert positions == {}
    
    def test_no_constraints(self):
        """Test components with no constraints use default positions"""
        from ui.components import TextFieldComponent
        
        comp1 = TextFieldComponent(field_name="Test")
        comp1.width = 100
        comp1.height = 50
        components = [comp1]
        cs = ConstraintSet()
        
        resolver = ConstraintResolver(parent_width=400, parent_height=600)
        positions = resolver.resolve(components, cs)
        
        # Should use component's default position
        assert id(comp1) in positions
        pos = positions[id(comp1)]
        assert 'x' in pos
        assert 'y' in pos
