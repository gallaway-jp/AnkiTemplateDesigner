"""
Layout strategies for component positioning
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from PyQt6.QtCore import QRect


class LayoutStrategy(ABC):
    """Abstract base for layout strategies"""
    
    @abstractmethod
    def calculate_bounds(
        self,
        components: List,
        canvas_width: int,
        canvas_height: int
    ) -> Dict[int, QRect]:
        """Calculate component bounds
        
        Args:
            components: List of components to layout
            canvas_width: Width of canvas
            canvas_height: Height of canvas
        
        Returns:
            Dictionary mapping component id to QRect bounds
        """
        pass


class FlowLayoutStrategy(LayoutStrategy):
    """Traditional top-to-bottom flow layout"""
    
    def calculate_bounds(self, components, canvas_width, canvas_height):
        """Calculate bounds using simple flow layout"""
        bounds = {}
        y_offset = 10
        
        for component in components:
            height = self._get_component_height(component)
            width = canvas_width - 20
            
            bounds[id(component)] = QRect(10, y_offset, width, height)
            y_offset += height + 10
        
        return bounds
    
    def _get_component_height(self, component) -> int:
        """Extract height from component, handling string values"""
        base_height = getattr(component, 'height', 50)
        if isinstance(base_height, str) and base_height.endswith('px'):
            try:
                return int(base_height.replace('px', ''))
            except ValueError:
                pass
        try:
            return int(base_height)
        except (ValueError, TypeError):
            return 50


class ConstraintLayoutStrategy(LayoutStrategy):
    """
    Android-style constraint-based layout strategy.
    
    Resolves component positions using a constraint resolution algorithm
    similar to Android's ConstraintLayout. Components define relationships
    to other components or to the parent container.
    
    Algorithm:
        1. Initialize all component positions to default (0, 0)
        2. Build constraint set from component constraint definitions
        3. Iterate through components and apply constraints
        4. Handle centering and bias calculations
        5. Return resolved positions as QRect bounds
    
    Supports constraint types:
        - Edge alignment (LEFT_TO_LEFT, TOP_TO_TOP, etc.)
        - Edge placement (LEFT_TO_RIGHT, TOP_TO_BOTTOM, etc.)
        - Centering (CENTER_HORIZONTAL, CENTER_VERTICAL)
    
    Example:
        >>> strategy = ConstraintLayoutStrategy()
        >>> components = [comp1, comp2]  # with constraints defined
        >>> bounds = strategy.calculate_bounds(components, 800, 600)
        >>> print(bounds[id(comp1)])
        QRect(10, 10, 200, 50)
    
    See Also:
        FlowLayoutStrategy: Simpler top-to-bottom layout
        ConstraintResolver: Core constraint resolution logic
        Constraint: Individual constraint definition
    """
    
    def calculate_bounds(self, components, canvas_width, canvas_height):
        """
        Calculate component bounds using constraint resolution.
        
        Builds a constraint set from all components' constraint definitions,
        resolves positions using ConstraintResolver, and converts the results
        to QRect bounds for rendering.
        
        Args:
            components (List[Component]): Components to layout
            canvas_width (int): Width of canvas in pixels
            canvas_height (int): Height of canvas in pixels
        
        Returns:
            Dict[int, QRect]: Mapping from component id() to QRect bounds
        
        Notes:
            - Components without constraints default to (0, 0)
            - Constraint resolution happens in component order
            - Invalid target references are skipped
            - Parent constraints use canvas dimensions
        """
        from .constraints import ConstraintSet, ConstraintResolver, Constraint
        
        # Build constraint set from all components
        constraint_set = ConstraintSet()
        for comp in components:
            if hasattr(comp, 'constraints') and comp.constraints:
                for c_dict in comp.constraints:
                    constraint_set.add_constraint(Constraint.from_dict(c_dict))
        
        # Resolve positions using constraint algorithm
        resolver = ConstraintResolver(canvas_width, canvas_height)
        positions = resolver.resolve(components, constraint_set)
        
        # Convert position dictionaries to QRect objects
        bounds = {}
        for comp in components:
            comp_id = id(comp)
            if comp_id in positions:
                pos = positions[comp_id]
                bounds[comp_id] = QRect(
                    pos['x'], pos['y'],
                    pos['width'], pos['height']
                )
        
        return bounds
