"""
Issue #49: Undo/Redo History System - Main Manager

Comprehensive undo/redo system with history branching, memory optimization,
and recovery capabilities. Allows users to reverse and reapply actions with
full support for complex template design workflows.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import uuid
import json


class ActionType(Enum):
    """Types of actions that can be undone/redone."""
    TEMPLATE_EDIT = "template_edit"
    COMPONENT_ADD = "component_add"
    COMPONENT_REMOVE = "component_remove"
    COMPONENT_MOVE = "component_move"
    COMPONENT_RESIZE = "component_resize"
    PROPERTY_CHANGE = "property_change"
    CONSTRAINT_ADD = "constraint_add"
    CONSTRAINT_REMOVE = "constraint_remove"
    STYLE_CHANGE = "style_change"
    LAYOUT_CHANGE = "layout_change"
    CUSTOM = "custom"


@dataclass
class ActionData:
    """Data for a single action that can be undone/redone."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.CUSTOM
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    before_state: Dict[str, Any] = field(default_factory=dict)
    after_state: Dict[str, Any] = field(default_factory=dict)
    target_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_reversible: bool = True
    affected_components: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'action_type': self.action_type.value,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'before_state': self.before_state,
            'after_state': self.after_state,
            'target_id': self.target_id,
            'metadata': self.metadata,
            'is_reversible': self.is_reversible,
            'affected_components': self.affected_components
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ActionData':
        """Create from dictionary."""
        return ActionData(
            id=data.get('id', str(uuid.uuid4())),
            action_type=ActionType(data.get('action_type', 'custom')),
            description=data.get('description', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            before_state=data.get('before_state', {}),
            after_state=data.get('after_state', {}),
            target_id=data.get('target_id'),
            metadata=data.get('metadata', {}),
            is_reversible=data.get('is_reversible', True),
            affected_components=data.get('affected_components', [])
        )


@dataclass
class HistoryBranch:
    """A branch in the undo/redo history tree."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Branch"
    parent_branch_id: Optional[str] = None
    actions: List[ActionData] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_main: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'parent_branch_id': self.parent_branch_id,
            'actions': [a.to_dict() for a in self.actions],
            'created_at': self.created_at.isoformat(),
            'is_main': self.is_main
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HistoryBranch':
        """Create from dictionary."""
        return HistoryBranch(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'Branch'),
            parent_branch_id=data.get('parent_branch_id'),
            actions=[ActionData.from_dict(a) for a in data.get('actions', [])],
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            is_main=data.get('is_main', True)
        )


@dataclass
class HistoryStatistics:
    """Statistics about undo/redo history."""
    total_actions: int = 0
    total_branches: int = 0
    main_branch_depth: int = 0
    memory_usage_bytes: int = 0
    oldest_action: Optional[datetime] = None
    newest_action: Optional[datetime] = None
    most_common_action_type: Optional[str] = None
    undoable_actions: int = 0
    redoable_actions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_actions': self.total_actions,
            'total_branches': self.total_branches,
            'main_branch_depth': self.main_branch_depth,
            'memory_usage_bytes': self.memory_usage_bytes,
            'oldest_action': self.oldest_action.isoformat() if self.oldest_action else None,
            'newest_action': self.newest_action.isoformat() if self.newest_action else None,
            'most_common_action_type': self.most_common_action_type,
            'undoable_actions': self.undoable_actions,
            'redoable_actions': self.redoable_actions
        }


class UndoRedoManager:
    """Main manager for undo/redo functionality with branching support."""

    def __init__(self, max_history_size: int = 100, enable_branching: bool = True):
        """
        Initialize the undo/redo manager.
        
        Args:
            max_history_size: Maximum number of actions to keep in history
            enable_branching: Whether to allow history branching
        """
        self.main_branch = HistoryBranch(name="Main", is_main=True)
        self.current_branch = self.main_branch
        self.branches: Dict[str, HistoryBranch] = {self.main_branch.id: self.main_branch}
        
        self.current_index = -1
        self.max_history_size = max_history_size
        self.enable_branching = enable_branching
        
        self.action_handlers: Dict[ActionType, Callable] = {}
        self.listeners: List[Callable] = []

    def register_action_handler(self, action_type: ActionType, handler: Callable) -> None:
        """Register a handler for specific action type."""
        self.action_handlers[action_type] = handler

    def add_listener(self, listener: Callable) -> None:
        """Add a listener for history changes."""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        """Remove a listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def _notify_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all listeners of a change."""
        for listener in self.listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass

    def record_action(self, action: ActionData) -> str:
        """
        Record a new action in the history.
        
        Args:
            action: The action to record
            
        Returns:
            The action ID
        """
        # Remove any redoable actions
        if self.current_index < len(self.current_branch.actions) - 1:
            if self.enable_branching:
                # Create new branch for alternative history
                self._create_branch_from_current()
            else:
                # Delete future actions
                self.current_branch.actions = self.current_branch.actions[:self.current_index + 1]

        # Add new action
        self.current_branch.actions.append(action)
        self.current_index += 1

        # Apply memory optimization if needed
        if len(self.current_branch.actions) > self.max_history_size:
            self._optimize_history()

        self._notify_listeners('action_recorded', {'action': action.to_dict()})
        return action.id

    def undo(self) -> bool:
        """
        Undo the last action.
        
        Returns:
            True if undo was successful
        """
        if not self.can_undo():
            return False

        action = self.current_branch.actions[self.current_index]

        if action.is_reversible:
            # Execute undo via handler if available
            if action.action_type in self.action_handlers:
                try:
                    self.action_handlers[action.action_type](action, is_undo=True)
                except Exception:
                    pass

            self.current_index -= 1
            self._notify_listeners('action_undone', {'action': action.to_dict()})
            return True

        return False

    def redo(self) -> bool:
        """
        Redo the next action.
        
        Returns:
            True if redo was successful
        """
        if not self.can_redo():
            return False

        next_index = self.current_index + 1
        action = self.current_branch.actions[next_index]

        if action.is_reversible:
            # Execute redo via handler if available
            if action.action_type in self.action_handlers:
                try:
                    self.action_handlers[action.action_type](action, is_undo=False)
                except Exception:
                    pass

            self.current_index += 1
            self._notify_listeners('action_redone', {'action': action.to_dict()})
            return True

        return False

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.current_index < len(self.current_branch.actions) - 1

    def undo_to(self, action_id: str) -> bool:
        """
        Undo to a specific action.
        
        Args:
            action_id: The target action ID
            
        Returns:
            True if successful
        """
        # Find the action index
        target_index = -1
        for i, action in enumerate(self.current_branch.actions):
            if action.id == action_id:
                target_index = i
                break

        if target_index == -1:
            return False

        # Undo actions until we reach target
        while self.current_index > target_index:
            if not self.undo():
                return False

        self._notify_listeners('undo_to_action', {'action_id': action_id})
        return True

    def redo_to(self, action_id: str) -> bool:
        """
        Redo to a specific action.
        
        Args:
            action_id: The target action ID
            
        Returns:
            True if successful
        """
        # Find the action index
        target_index = -1
        for i, action in enumerate(self.current_branch.actions):
            if action.id == action_id:
                target_index = i
                break

        if target_index == -1 or target_index <= self.current_index:
            return False

        # Redo actions until we reach target
        while self.current_index < target_index:
            if not self.redo():
                return False

        self._notify_listeners('redo_to_action', {'action_id': action_id})
        return True

    def clear_history(self) -> None:
        """Clear all history."""
        self.current_branch.actions.clear()
        self.current_index = -1
        self._notify_listeners('history_cleared', {})

    def get_current_action(self) -> Optional[ActionData]:
        """Get the current action."""
        if 0 <= self.current_index < len(self.current_branch.actions):
            return self.current_branch.actions[self.current_index]
        return None

    def get_next_action(self) -> Optional[ActionData]:
        """Get the next action (for redo)."""
        next_index = self.current_index + 1
        if next_index < len(self.current_branch.actions):
            return self.current_branch.actions[next_index]
        return None

    def get_history(self) -> List[ActionData]:
        """Get all actions up to current position."""
        return self.current_branch.actions[:self.current_index + 1]

    def get_future_history(self) -> List[ActionData]:
        """Get all redoable actions."""
        return self.current_branch.actions[self.current_index + 1:]

    def _create_branch_from_current(self) -> str:
        """
        Create a new branch from current position.
        
        Returns:
            The new branch ID
        """
        new_branch = HistoryBranch(
            name=f"Branch {len(self.branches)}",
            parent_branch_id=self.current_branch.id,
            actions=self.current_branch.actions[:self.current_index + 1].copy()
        )
        self.branches[new_branch.id] = new_branch
        self.current_branch = new_branch
        self.current_index = len(new_branch.actions) - 1
        self._notify_listeners('branch_created', {'branch_id': new_branch.id})
        return new_branch.id

    def switch_branch(self, branch_id: str) -> bool:
        """
        Switch to a different branch.
        
        Args:
            branch_id: The target branch ID
            
        Returns:
            True if successful
        """
        if branch_id not in self.branches:
            return False

        branch = self.branches[branch_id]
        self.current_branch = branch
        self.current_index = len(branch.actions) - 1
        self._notify_listeners('branch_switched', {'branch_id': branch_id})
        return True

    def get_branches(self) -> List[HistoryBranch]:
        """Get all branches."""
        return list(self.branches.values())

    def get_branch_tree(self) -> Dict[str, Any]:
        """Get the branch tree structure."""
        def build_tree(branch: HistoryBranch) -> Dict[str, Any]:
            children = [
                build_tree(self.branches[bid])
                for bid in self.branches
                if self.branches[bid].parent_branch_id == branch.id
            ]
            return {
                'id': branch.id,
                'name': branch.name,
                'is_current': branch.id == self.current_branch.id,
                'depth': len(branch.actions),
                'created_at': branch.created_at.isoformat(),
                'children': children
            }

        return build_tree(self.main_branch)

    def _optimize_history(self) -> None:
        """Optimize history by compressing old actions."""
        # Keep only most recent actions
        excess = len(self.current_branch.actions) - self.max_history_size
        if excess > 0:
            self.current_branch.actions = self.current_branch.actions[excess:]
            self.current_index = max(0, self.current_index - excess)

    def get_statistics(self) -> HistoryStatistics:
        """Get history statistics."""
        all_actions = []
        for branch in self.branches.values():
            all_actions.extend(branch.actions)

        action_counts = {}
        for action in all_actions:
            action_type = action.action_type.value
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        most_common = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None

        # Calculate memory usage (rough estimate)
        memory_bytes = sum(len(json.dumps(a.to_dict()).encode()) for a in all_actions)

        timestamps = [a.timestamp for a in all_actions if a.timestamp]

        return HistoryStatistics(
            total_actions=len(all_actions),
            total_branches=len(self.branches),
            main_branch_depth=len(self.main_branch.actions),
            memory_usage_bytes=memory_bytes,
            oldest_action=min(timestamps) if timestamps else None,
            newest_action=max(timestamps) if timestamps else None,
            most_common_action_type=most_common,
            undoable_actions=self.current_index + 1,
            redoable_actions=len(self.current_branch.actions) - self.current_index - 1
        )

    def save_state(self) -> Dict[str, Any]:
        """Save complete history state."""
        return {
            'main_branch': self.main_branch.to_dict(),
            'branches': {bid: b.to_dict() for bid, b in self.branches.items()},
            'current_branch_id': self.current_branch.id,
            'current_index': self.current_index,
            'max_history_size': self.max_history_size,
            'enable_branching': self.enable_branching
        }

    def load_state(self, state: Dict[str, Any]) -> bool:
        """Load history state."""
        try:
            self.main_branch = HistoryBranch.from_dict(state['main_branch'])
            self.branches = {bid: HistoryBranch.from_dict(b) for bid, b in state['branches'].items()}
            self.current_branch = self.branches[state['current_branch_id']]
            self.current_index = state['current_index']
            self.max_history_size = state['max_history_size']
            self.enable_branching = state['enable_branching']
            return True
        except Exception:
            return False
