"""
Command pattern implementation for undo/redo functionality.

This module provides a command system that allows undoing and redoing
operations in the visual builder.
"""

from typing import Optional, List
from abc import ABC, abstractmethod
from .components import Component


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Commands encapsulate actions that can be undone and redone.
    Each command must implement execute() and undo() methods.
    """
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.
        
        Returns:
            bool: True if executed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command, reverting its effects.
        
        Returns:
            bool: True if undone successfully, False otherwise
        """
        pass
    
    def get_description(self) -> str:
        """Get a human-readable description of this command."""
        return self.__class__.__name__


class AddComponentCommand(Command):
    """Command to add a component to a parent."""
    
    def __init__(self, component: Component, parent: Optional[Component], index: int = -1):
        """
        Initialize add component command.
        
        Args:
            component: Component to add
            parent: Parent component (None for root level)
            index: Position to insert at (-1 for end)
        """
        self.component = component
        self.parent = parent
        self.index = index
        self._executed = False
    
    def execute(self) -> bool:
        """Add the component to its parent."""
        if self._executed:
            return True
        
        if self.parent:
            if self.index >= 0:
                self.parent.children.insert(self.index, self.component)
            else:
                self.parent.children.append(self.component)
            self.component.parent = self.parent
        
        self._executed = True
        return True
    
    def undo(self) -> bool:
        """Remove the component from its parent."""
        if not self._executed:
            return False
        
        if self.parent and self.component in self.parent.children:
            self.parent.children.remove(self.component)
            self.component.parent = None
        
        self._executed = False
        return True
    
    def get_description(self) -> str:
        return f"Add {self.component.type.value}"


class RemoveComponentCommand(Command):
    """Command to remove a component from its parent."""
    
    def __init__(self, component: Component):
        """
        Initialize remove component command.
        
        Args:
            component: Component to remove
        """
        self.component = component
        self.parent = component.parent
        self.index = -1
        self._executed = False
    
    def execute(self) -> bool:
        """Remove the component from its parent."""
        if self._executed:
            return True
        
        if self.parent and self.component in self.parent.children:
            self.index = self.parent.children.index(self.component)
            self.parent.children.remove(self.component)
            self.component.parent = None
            self._executed = True
            return True
        
        return False
    
    def undo(self) -> bool:
        """Re-add the component to its parent."""
        if not self._executed:
            return False
        
        if self.parent:
            if self.index >= 0 and self.index < len(self.parent.children):
                self.parent.children.insert(self.index, self.component)
            else:
                self.parent.children.append(self.component)
            self.component.parent = self.parent
        
        self._executed = False
        return True
    
    def get_description(self) -> str:
        return f"Remove {self.component.type.value}"


class MoveComponentCommand(Command):
    """Command to move a component to a new position."""
    
    def __init__(self, component: Component, new_x: int, new_y: int):
        """
        Initialize move component command.
        
        Args:
            component: Component to move
            new_x: New X coordinate
            new_y: New Y coordinate
        """
        self.component = component
        self.old_x = component.x
        self.old_y = component.y
        self.new_x = new_x
        self.new_y = new_y
    
    def execute(self) -> bool:
        """Move the component to the new position."""
        self.component.x = self.new_x
        self.component.y = self.new_y
        return True
    
    def undo(self) -> bool:
        """Restore the component to its original position."""
        self.component.x = self.old_x
        self.component.y = self.old_y
        return True
    
    def get_description(self) -> str:
        return f"Move {self.component.type.value}"


class ResizeComponentCommand(Command):
    """Command to resize a component."""
    
    def __init__(self, component: Component, new_width: int, new_height: int):
        """
        Initialize resize component command.
        
        Args:
            component: Component to resize
            new_width: New width
            new_height: New height
        """
        self.component = component
        self.old_width = component.width
        self.old_height = component.height
        self.new_width = new_width
        self.new_height = new_height
    
    def execute(self) -> bool:
        """Resize the component."""
        self.component.width = self.new_width
        self.component.height = self.new_height
        return True
    
    def undo(self) -> bool:
        """Restore the component to its original size."""
        self.component.width = self.old_width
        self.component.height = self.old_height
        return True
    
    def get_description(self) -> str:
        return f"Resize {self.component.type.value}"


class ModifyPropertyCommand(Command):
    """Command to modify a component property."""
    
    def __init__(self, component: Component, property_name: str, new_value):
        """
        Initialize modify property command.
        
        Args:
            component: Component to modify
            property_name: Name of the property to change
            new_value: New value for the property
        """
        self.component = component
        self.property_name = property_name
        self.old_value = getattr(component, property_name, None)
        self.new_value = new_value
    
    def execute(self) -> bool:
        """Set the property to the new value."""
        setattr(self.component, self.property_name, self.new_value)
        return True
    
    def undo(self) -> bool:
        """Restore the property to its original value."""
        setattr(self.component, self.property_name, self.old_value)
        return True
    
    def get_description(self) -> str:
        return f"Modify {self.property_name}"


class CommandHistory:
    """
    Manages command history for undo/redo functionality.
    
    Maintains separate stacks for undo and redo operations.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize command history.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history
    
    def execute(self, command: Command) -> bool:
        """
        Execute a command and add it to history.
        
        Args:
            command: Command to execute
            
        Returns:
            bool: True if executed successfully
        """
        if command.execute():
            self.undo_stack.append(command)
            # Clear redo stack when new command is executed
            self.redo_stack.clear()
            
            # Limit history size
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            
            return True
        return False
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            bool: True if undo was successful
        """
        if not self.can_undo():
            return False
        
        command = self.undo_stack.pop()
        if command.undo():
            self.redo_stack.append(command)
            return True
        else:
            # If undo fails, put it back
            self.undo_stack.append(command)
            return False
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            bool: True if redo was successful
        """
        if not self.can_redo():
            return False
        
        command = self.redo_stack.pop()
        if command.execute():
            self.undo_stack.append(command)
            return True
        else:
            # If redo fails, put it back
            self.redo_stack.append(command)
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of the next undo command."""
        if self.can_undo():
            return self.undo_stack[-1].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of the next redo command."""
        if self.can_redo():
            return self.redo_stack[-1].get_description()
        return None
    
    def clear(self):
        """Clear all command history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_history_size(self) -> int:
        """Get total number of commands in history."""
        return len(self.undo_stack) + len(self.redo_stack)
