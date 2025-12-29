"""
Constraint system for layout - inspired by Android's ConstraintLayout
"""

import sys
import os
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass

# Add parent directory to path for imports when needed
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import LayoutDefaults


class ConstraintType(Enum):
    """Types of constraints"""
    LEFT_TO_LEFT = "left_to_left"
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"
    RIGHT_TO_RIGHT = "right_to_right"
    TOP_TO_TOP = "top_to_top"
    TOP_TO_BOTTOM = "top_to_bottom"
    BOTTOM_TO_TOP = "bottom_to_top"
    BOTTOM_TO_BOTTOM = "bottom_to_bottom"
    START_TO_START = "start_to_start"
    START_TO_END = "start_to_end"
    END_TO_START = "end_to_start"
    END_TO_END = "end_to_end"
    CENTER_HORIZONTAL = "center_horizontal"
    CENTER_VERTICAL = "center_vertical"


class ConstraintTarget(Enum):
    """Constraint target types"""
    PARENT = "parent"
    COMPONENT = "component"


@dataclass
class Constraint:
    """A single constraint between two anchors"""
    source_component_id: int  # id() of source component
    constraint_type: ConstraintType
    target: ConstraintTarget
    target_component_id: Optional[int] = None  # None if target is PARENT
    margin: int = 0  # Margin in pixels
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'source_component_id': self.source_component_id,
            'constraint_type': self.constraint_type.value,
            'target': self.target.value,
            'target_component_id': self.target_component_id,
            'margin': self.margin
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Constraint':
        """Create from dictionary"""
        return Constraint(
            source_component_id=data['source_component_id'],
            constraint_type=ConstraintType(data['constraint_type']),
            target=ConstraintTarget(data['target']),
            target_component_id=data.get('target_component_id'),
            margin=data.get('margin', 0)
        )


class ConstraintSet:
    """Collection of constraints for a layout"""
    
    def __init__(self):
        self.constraints: List[Constraint] = []
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint"""
        # Remove any existing constraint of the same type for the same component
        self.constraints = [
            existing_constraint for existing_constraint in self.constraints
            if not (existing_constraint.source_component_id == constraint.source_component_id and
                   existing_constraint.constraint_type == constraint.constraint_type)
        ]
        self.constraints.append(constraint)
    
    def remove_constraint(self, source_id: int, constraint_type: ConstraintType):
        """Remove a specific constraint"""
        self.constraints = [
            constraint for constraint in self.constraints
            if not (constraint.source_component_id == source_id and
                   constraint.constraint_type == constraint_type)
        ]
    
    def get_constraints_for_component(self, component_id: int) -> List[Constraint]:
        """Get all constraints for a component"""
        return [
            constraint for constraint in self.constraints 
            if constraint.source_component_id == component_id
        ]
    
    def get_constraints(self, component_id: int) -> List[Constraint]:
        """Alias for get_constraints_for_component for convenience"""
        return self.get_constraints_for_component(component_id)
    
    def clear_constraints_for_component(self, component_id: int):
        """Clear all constraints for a component"""
        self.constraints = [c for c in self.constraints if c.source_component_id != component_id]
    
    def clear_constraints(self, component_id: int):
        """Alias for clear_constraints_for_component for convenience"""
        self.clear_constraints_for_component(component_id)
    
    def has_constraint(self, source_id: int, constraint_type: ConstraintType) -> bool:
        """Check if a constraint exists"""
        return any(
            c.source_component_id == source_id and c.constraint_type == constraint_type
            for c in self.constraints
        )
    
    def to_dict_list(self) -> List[dict]:
        """Convert all constraints to dictionary list"""
        return [c.to_dict() for c in self.constraints]
    
    @staticmethod
    def from_dict_list(data: List[dict]) -> 'ConstraintSet':
        """Create from dictionary list"""
        constraint_set = ConstraintSet()
        constraint_set.constraints = [Constraint.from_dict(d) for d in data]
        return constraint_set
    
    def to_dict(self) -> Dict[int, List[dict]]:
        """Convert to dictionary grouped by component ID"""
        result = {}
        for constraint in self.constraints:
            comp_id = constraint.source_component_id
            if comp_id not in result:
                result[comp_id] = []
            result[comp_id].append(constraint.to_dict())
        return result
    
    @staticmethod
    def from_dict(data: Dict[int, List[dict]]) -> 'ConstraintSet':
        """Create from dictionary grouped by component ID"""
        constraint_set = ConstraintSet()
        for comp_id, constraint_dicts in data.items():
            for c_dict in constraint_dicts:
                constraint_set.constraints.append(Constraint.from_dict(c_dict))
        return constraint_set


class ConstraintResolver:
    """Resolves constraints to calculate actual positions"""
    
    def __init__(self, parent_width: int, parent_height: int):
        self.parent_width = parent_width
        self.parent_height = parent_height
        self.resolved_positions: Dict[int, dict] = {}
    
    def resolve(self, components: List, constraint_set: ConstraintSet) -> Dict[int, dict]:
        """
        Resolve all constraints and return calculated positions
        
        Returns:
            Dict mapping component id to {x, y, width, height}
        """
        self.resolved_positions = {}
        
        # Build component map
        component_map = {id(comp): comp for comp in components}
        
        # Initialize with default positions (apply bias if no constraints)
        for comp in components:
            comp_id = id(comp)
            width = getattr(comp, 'width', 100)
            height = getattr(comp, 'height', 50)
            
            # Convert width/height to integers if they're strings
            if isinstance(width, str):
                if width.endswith('px'):
                    width = int(width.replace('px', ''))
                elif width.endswith('%'):
                    width = int(self.parent_width * int(width.replace('%', '')) / 100)
                elif width == 'auto':
                    width = 100
                else:
                    width = int(width) if width.isdigit() else 100
            
            if isinstance(height, str):
                if height.endswith('px'):
                    height = int(height.replace('px', ''))
                elif height.endswith('%'):
                    height = int(self.parent_height * int(height.replace('%', '')) / 100)
                elif height == 'auto':
                    height = 50
                else:
                    height = int(height) if height.isdigit() else 50
            
            # Apply horizontal bias
            horizontal_bias = getattr(
                comp, 
                'constraint_horizontal_bias', 
                LayoutDefaults.DEFAULT_HORIZONTAL_BIAS
            )
            x = int((self.parent_width - width) * horizontal_bias)
            
            # Apply vertical bias
            vertical_bias = getattr(
                comp, 
                'constraint_vertical_bias', 
                LayoutDefaults.DEFAULT_VERTICAL_BIAS
            )
            y = int((self.parent_height - height) * vertical_bias)
            
            self.resolved_positions[comp_id] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
        
        # Resolve constraints (multiple passes may be needed for complex layouts)
        max_iterations = LayoutDefaults.MAX_CONSTRAINT_ITERATIONS
        for iteration in range(max_iterations):
            for component in components:
                comp_id = id(component)
                constraints = constraint_set.get_constraints_for_component(comp_id)
                
                for constraint in constraints:
                    self._apply_constraint(
                        comp_id,
                        constraint,
                        component_map
                    )
        
        return self.resolved_positions
    
    def _apply_constraint(self, comp_id: int, constraint: Constraint, component_map: dict):
        """
        Apply a single constraint to update component position.
        
        Modifies the position dictionary for the given component based on
        the constraint type and target. Supports both parent-relative and
        component-relative constraints.
        
        Constraint Types:
            Horizontal:
                - LEFT_TO_LEFT: Align left edges
                - LEFT_TO_RIGHT: Place left edge at target's right edge
                - RIGHT_TO_LEFT: Place right edge at target's left edge
                - RIGHT_TO_RIGHT: Align right edges
                - CENTER_HORIZONTAL: Center horizontally in target
            
            Vertical:
                - TOP_TO_TOP: Align top edges
                - TOP_TO_BOTTOM: Place top edge at target's bottom edge
                - BOTTOM_TO_TOP: Place bottom edge at target's top edge
                - BOTTOM_TO_BOTTOM: Align bottom edges
                - CENTER_VERTICAL: Center vertically in target
        
        Args:
            comp_id: ID of component being constrained
            constraint: Constraint to apply
            component_map: Map of component IDs to components
        
        Example:
            Component A constrained LEFT_TO_LEFT of parent with margin=10:
            - A's left edge will be at parent.x + 10
            
            Component B constrained LEFT_TO_RIGHT of A with margin=5:
            - B's left edge will be at A.right + 5
        """
        pos = self.resolved_positions[comp_id]
        
        # Get target bounds (parent container or another component)
        target_bounds = self._get_target_bounds(constraint)
        if not target_bounds:
            return  # Skip if target component doesn't exist
        
        # Apply constraint based on type
        margin = constraint.margin
        constraint_type = constraint.constraint_type
        
        # Horizontal constraints - affect X position
        if constraint_type == ConstraintType.LEFT_TO_LEFT:
            # Align left edge to target's left edge + margin
            pos['x'] = target_bounds['left'] + margin
        elif constraint_type == ConstraintType.LEFT_TO_RIGHT:
            # Place left edge at target's right edge + margin (component to the right)
            pos['x'] = target_bounds['right'] + margin
        elif constraint_type == ConstraintType.RIGHT_TO_LEFT:
            # Place right edge at target's left edge - margin (component to the left)
            pos['x'] = target_bounds['left'] - pos['width'] - margin
        elif constraint_type == ConstraintType.RIGHT_TO_RIGHT:
            # Align right edge to target's right edge - margin
            pos['x'] = target_bounds['right'] - pos['width'] - margin
        elif constraint_type == ConstraintType.CENTER_HORIZONTAL:
            # Center horizontally within target bounds
            pos['x'] = self._calculate_center_x(target_bounds, pos['width'])
        
        # Vertical constraints - affect Y position
        elif constraint_type == ConstraintType.TOP_TO_TOP:
            # Align top edge to target's top edge + margin
            pos['y'] = target_bounds['top'] + margin
        elif constraint_type == ConstraintType.TOP_TO_BOTTOM:
            # Place top edge at target's bottom edge + margin (component below)
            pos['y'] = target_bounds['bottom'] + margin
        elif constraint_type == ConstraintType.BOTTOM_TO_TOP:
            # Place bottom edge at target's top edge - margin (component above)
            pos['y'] = target_bounds['top'] - pos['height'] - margin
        elif constraint_type == ConstraintType.BOTTOM_TO_BOTTOM:
            # Align bottom edge to target's bottom edge - margin
            pos['y'] = target_bounds['bottom'] - pos['height'] - margin
        elif constraint_type == ConstraintType.CENTER_VERTICAL:
            # Center vertically within target bounds
            pos['y'] = self._calculate_center_y(target_bounds, pos['height'])
    
    def _get_target_bounds(self, constraint: Constraint) -> dict:
        """Extract target bounds calculation to separate method"""
        if constraint.target == ConstraintTarget.PARENT:
            return {
                'left': 0,
                'right': self.parent_width,
                'top': 0,
                'bottom': self.parent_height,
                'width': self.parent_width,
                'height': self.parent_height,
                'is_parent': True
            }
        else:
            if constraint.target_component_id not in self.resolved_positions:
                return None
            
            target_pos = self.resolved_positions[constraint.target_component_id]
            return {
                'left': target_pos['x'],
                'right': target_pos['x'] + target_pos['width'],
                'top': target_pos['y'],
                'bottom': target_pos['y'] + target_pos['height'],
                'width': target_pos['width'],
                'height': target_pos['height'],
                'is_parent': False
            }
    
    def _calculate_center_x(self, target_bounds: dict, width: int) -> int:
        """Calculate centered X position"""
        if target_bounds['is_parent']:
            return (self.parent_width - width) // 2
        else:
            target_center_x = (target_bounds['left'] + target_bounds['right']) // 2
            return target_center_x - width // 2
    
    def _calculate_center_y(self, target_bounds: dict, height: int) -> int:
        """Calculate centered Y position"""
        if target_bounds['is_parent']:
            return (self.parent_height - height) // 2
        else:
            target_center_y = (target_bounds['top'] + target_bounds['bottom']) // 2
            return target_center_y - height // 2


class ConstraintHelper:
    """Helper methods for constraint manipulation"""
    
    @staticmethod
    def create_centered_constraints(component_id: int) -> List[Constraint]:
        """Create constraints to center a component in parent"""
        return [
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.CENTER_HORIZONTAL,
                target=ConstraintTarget.PARENT
            ),
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.CENTER_VERTICAL,
                target=ConstraintTarget.PARENT
            )
        ]
    
    @staticmethod
    def create_match_parent_constraints(component_id: int, margin: int = 0) -> List[Constraint]:
        """Create constraints to match parent width/height"""
        return [
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.LEFT_TO_LEFT,
                target=ConstraintTarget.PARENT,
                margin=margin
            ),
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.RIGHT_TO_RIGHT,
                target=ConstraintTarget.PARENT,
                margin=margin
            ),
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.TOP_TO_TOP,
                target=ConstraintTarget.PARENT,
                margin=margin
            ),
            Constraint(
                source_component_id=component_id,
                constraint_type=ConstraintType.BOTTOM_TO_BOTTOM,
                target=ConstraintTarget.PARENT,
                margin=margin
            )
        ]
    
    @staticmethod
    def create_chain_constraints(component_ids: List[int], vertical: bool = False) -> List[Constraint]:
        """Create a chain of components"""
        constraints = []
        
        for i, comp_id in enumerate(component_ids):
            if i == 0:
                # First component - constrain to parent start
                if vertical:
                    constraints.append(Constraint(
                        source_component_id=comp_id,
                        constraint_type=ConstraintType.TOP_TO_TOP,
                        target=ConstraintTarget.PARENT
                    ))
                else:
                    constraints.append(Constraint(
                        source_component_id=comp_id,
                        constraint_type=ConstraintType.LEFT_TO_LEFT,
                        target=ConstraintTarget.PARENT
                    ))
            else:
                # Constrain to previous component
                prev_id = component_ids[i - 1]
                if vertical:
                    constraints.append(Constraint(
                        source_component_id=comp_id,
                        constraint_type=ConstraintType.TOP_TO_BOTTOM,
                        target=ConstraintTarget.COMPONENT,
                        target_component_id=prev_id,
                        margin=10
                    ))
                else:
                    constraints.append(Constraint(
                        source_component_id=comp_id,
                        constraint_type=ConstraintType.LEFT_TO_RIGHT,
                        target=ConstraintTarget.COMPONENT,
                        target_component_id=prev_id,
                        margin=10
                    ))
        
        return constraints
