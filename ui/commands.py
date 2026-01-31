"""Command pattern implementation for editor operations."""

from typing import Any, Optional, Callable
from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for editor commands."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class CommandRegistry:
    """Manages command registration and execution."""
    
    def __init__(self):
        self.commands: dict[str, type[Command]] = {}
    
    def register(self, name: str, command_class: type[Command]) -> None:
        """Register a command."""
        self.commands[name] = command_class
    
    def execute_command(self, name: str, **kwargs) -> Optional[Command]:
        """Execute a registered command."""
        if name in self.commands:
            command = self.commands[name](**kwargs)
            command.execute()
            return command
        return None


__all__ = ['Command', 'CommandRegistry']
