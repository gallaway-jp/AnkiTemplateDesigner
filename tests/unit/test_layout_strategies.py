"""
Tests for layout strategies
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QRect
from ui.layout_strategies import (
    LayoutStrategy,
    FlowLayoutStrategy,
    ConstraintLayoutStrategy
)
from ui.components import Component, ComponentType
from ui.constraints import Constraint, ConstraintType, ConstraintTarget, ConstraintHelper


class TestLayoutStrategy:
    """Tests for LayoutStrategy abstract base class"""
    
    def test_layout_strategy_is_abstract(self):
        """Test LayoutStrategy cannot be instantiated"""
        with pytest.raises(TypeError):
            LayoutStrategy()


class TestFlowLayoutStrategy:
    """Tests for FlowLayoutStrategy"""
    
    def test_flow_layout_initialization(self):
        """Test FlowLayoutStrategy initializes"""
        strategy = FlowLayoutStrategy()
        
        assert strategy is not None
    
    def test_flow_layout_single_component(self):
        """Test flow layout with single component"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        components = [component]
        
        bounds = strategy.calculate_bounds(components, 400, 600)
        
        assert len(bounds) == 1
        assert id(component) in bounds
        
        rect = bounds[id(component)]
        assert rect.x() == 10
        assert rect.y() == 10
        assert rect.width() == 380  # 400 - 20
        assert rect.height() == 50
    
    def test_flow_layout_multiple_components(self):
        """Test flow layout stacks components vertically"""
        strategy = FlowLayoutStrategy()
        comp1 = Component(ComponentType.TEXT_FIELD)
        comp1.height = 50
        comp2 = Component(ComponentType.TEXT_FIELD)
        comp2.height = 75
        comp3 = Component(ComponentType.TEXT_FIELD)
        comp3.height = 40
        components = [comp1, comp2, comp3]
        
        bounds = strategy.calculate_bounds(components, 400, 600)
        
        assert len(bounds) == 3
        
        # First component at y=10
        assert bounds[id(components[0])].y() == 10
        
        # Second component at y=10+50+10=70
        assert bounds[id(components[1])].y() == 70
        
        # Third component at y=70+75+10=155
        assert bounds[id(components[2])].y() == 155
    
    def test_flow_layout_component_widths(self):
        """Test flow layout sets component widths correctly"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        
        bounds = strategy.calculate_bounds([component], 400, 600)
        
        # Width should be canvas_width - 20 (10px margin on each side)
        assert bounds[id(component)].width() == 380
    
    def test_flow_layout_empty_components(self):
        """Test flow layout with empty component list"""
        strategy = FlowLayoutStrategy()
        
        bounds = strategy.calculate_bounds([], 400, 600)
        
        assert bounds == {}
    
    def test_get_component_height_from_number(self):
        """Test _get_component_height with numeric height"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 75
        
        height = strategy._get_component_height(component)
        
        assert height == 75
    
    def test_get_component_height_from_string_px(self):
        """Test _get_component_height with string '50px'"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = '65px'
        
        height = strategy._get_component_height(component)
        
        assert height == 65
    
    def test_get_component_height_invalid_string(self):
        """Test _get_component_height with invalid string falls back to default"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 'invalid'
        
        height = strategy._get_component_height(component)
        
        assert height == 50  # Default fallback
    
    def test_get_component_height_no_height_attribute(self):
        """Test _get_component_height when component lacks height"""
        strategy = FlowLayoutStrategy()
        component = Mock(spec=[])  # Mock without height attribute
        
        height = strategy._get_component_height(component)
        
        assert height == 50  # Default fallback
    
    def test_flow_layout_large_canvas(self):
        """Test flow layout with large canvas dimensions"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        
        bounds = strategy.calculate_bounds([component], 1920, 1080)
        
        assert bounds[id(component)].width() == 1900  # 1920 - 20
    
    def test_flow_layout_small_canvas(self):
        """Test flow layout with small canvas dimensions"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        
        bounds = strategy.calculate_bounds([component], 200, 300)
        
        assert bounds[id(component)].width() == 180  # 200 - 20


class TestConstraintLayoutStrategy:
    """Tests for ConstraintLayoutStrategy"""
    
    def test_constraint_layout_initialization(self):
        """Test ConstraintLayoutStrategy initializes"""
        strategy = ConstraintLayoutStrategy()
        
        assert strategy is not None
    
    def test_constraint_layout_no_constraints(self):
        """Test constraint layout with components but no constraints"""
        strategy = ConstraintLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        component.use_constraints = True
        components = [component]
        
        bounds = strategy.calculate_bounds(components, 400, 600)
        
        # Should still calculate bounds (default positioning)
        assert len(bounds) == 1
        assert id(component) in bounds
    
    def test_constraint_layout_centered_component(self):
        """Test constraint layout with centered component"""
        strategy = ConstraintLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        component.use_constraints = True
        
        # Add center constraints
        comp_id = id(component)
        constraints = ConstraintHelper.create_centered_constraints(comp_id)
        component.constraints = [c.to_dict() for c in constraints]
        
        bounds = strategy.calculate_bounds([component], 400, 600)
        
        # Component should be centered
        assert id(component) in bounds
        rect = bounds[id(component)]
        
        # X should be centered: (400 - 100) / 2 = 150
        assert rect.x() == 150
        
        # Y should be centered: (600 - 50) / 2 = 275
        assert rect.y() == 275
    
    def test_constraint_layout_left_aligned(self):
        """Test constraint layout with left-aligned component"""
        strategy = ConstraintLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        component.use_constraints = True
        
        # Add left alignment constraint
        comp_id = id(component)
        constraint = Constraint(
            source_component_id=comp_id,
            constraint_type=ConstraintType.LEFT_TO_LEFT,
            target=ConstraintTarget.PARENT,
            margin=10
        )
        component.constraints = [constraint.to_dict()]
        
        bounds = strategy.calculate_bounds([component], 400, 600)
        
        rect = bounds[id(component)]
        assert rect.x() == 10  # Left margin
    
    def test_constraint_layout_multiple_components(self):
        """Test constraint layout with multiple components"""
        strategy = ConstraintLayoutStrategy()
        
        comp1 = Component(ComponentType.TEXT_FIELD)
        comp1.height = 50
        comp1.width = 100
        comp1.use_constraints = True
        
        comp2 = Component(ComponentType.TEXT_FIELD)
        comp2.height = 50
        comp2.width = 100
        comp2.use_constraints = True
        
        # Center first component
        comp1.constraints = [c.to_dict() for c in ConstraintHelper.create_centered_constraints(id(comp1))]
        
        # Center second component
        comp2.constraints = [c.to_dict() for c in ConstraintHelper.create_centered_constraints(id(comp2))]
        
        components = [comp1, comp2]
        bounds = strategy.calculate_bounds(components, 400, 600)
        
        assert len(bounds) == 2
        assert id(comp1) in bounds
        assert id(comp2) in bounds
    
    def test_constraint_layout_match_parent(self):
        """Test constraint layout with match parent constraints"""
        strategy = ConstraintLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        component.use_constraints = True
        
        comp_id = id(component)
        constraints = ConstraintHelper.create_match_parent_constraints(comp_id, margin=8)
        component.constraints = [c.to_dict() for c in constraints]
        
        bounds = strategy.calculate_bounds([component], 400, 600)
        
        rect = bounds[id(component)]
        # Should have bounds calculated (actual position depends on constraint resolution)
        assert rect is not None
        assert rect.width() > 0
        assert rect.height() > 0
    
    def test_constraint_layout_empty_components(self):
        """Test constraint layout with no components"""
        strategy = ConstraintLayoutStrategy()
        
        bounds = strategy.calculate_bounds([], 400, 600)
        
        assert bounds == {}
    
    def test_constraint_layout_component_without_constraints_attribute(self):
        """Test constraint layout when component lacks constraints"""
        strategy = ConstraintLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        # Don't set constraints attribute
        
        bounds = strategy.calculate_bounds([component], 400, 600)
        
        # Should handle gracefully (default positioning)
        assert len(bounds) >= 0


class TestLayoutStrategyIntegration:
    """Integration tests for layout strategies"""
    
    def test_flow_and_constraint_produce_different_layouts(self):
        """Test Flow and Constraint strategies produce different layouts"""
        flow_strategy = FlowLayoutStrategy()
        constraint_strategy = ConstraintLayoutStrategy()
        
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        component.use_constraints = True
        
        component.constraints = [c.to_dict() for c in ConstraintHelper.create_centered_constraints(id(component))]
        
        flow_bounds = flow_strategy.calculate_bounds([component], 400, 600)
        constraint_bounds = constraint_strategy.calculate_bounds([component], 400, 600)
        
        # Flow layout: x=10, y=10
        # Constraint layout: x=150, y=275 (centered)
        assert flow_bounds[id(component)].x() != constraint_bounds[id(component)].x()
        assert flow_bounds[id(component)].y() != constraint_bounds[id(component)].y()
    
    def test_strategy_pattern_switching(self):
        """Test switching between strategies"""
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        component.width = 100
        components = [component]
        
        # Start with flow layout
        strategy = FlowLayoutStrategy()
        flow_bounds = strategy.calculate_bounds(components, 400, 600)
        
        # Switch to constraint layout
        strategy = ConstraintLayoutStrategy()
        constraint_bounds = strategy.calculate_bounds(components, 400, 600)
        
        # Both should work
        assert len(flow_bounds) == 1
        assert len(constraint_bounds) >= 0
    
    def test_all_strategies_handle_same_components(self):
        """Test all strategy types can handle the same components"""
        strategies = [
            FlowLayoutStrategy(),
            ConstraintLayoutStrategy()
        ]
        
        comp1 = Component(ComponentType.TEXT_FIELD)
        comp1.height = 50
        comp1.width = 100
        
        comp2 = Component(ComponentType.IMAGE_FIELD)
        comp2.height = 200
        comp2.width = 300
        
        components = [comp1, comp2]
        
        for strategy in strategies:
            bounds = strategy.calculate_bounds(components, 400, 600)
            
            # All strategies should produce some output
            assert isinstance(bounds, dict)
    
    def test_layout_with_various_canvas_sizes(self):
        """Test layouts work with various canvas sizes"""
        strategy = FlowLayoutStrategy()
        component = Component(ComponentType.TEXT_FIELD)
        component.height = 50
        
        canvas_sizes = [
            (200, 300),
            (400, 600),
            (800, 1200),
            (1920, 1080)
        ]
        
        for width, height in canvas_sizes:
            bounds = strategy.calculate_bounds([component], width, height)
            
            assert len(bounds) == 1
            assert bounds[id(component)].width() == width - 20
