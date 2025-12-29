"""
Keyboard shortcuts system for the template designer.

Provides a centralized system for managing keyboard shortcuts across the application.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Callable, Optional
from enum import Enum


class ShortcutAction(Enum):
    """Standard shortcut actions."""
    
    # File operations
    SAVE = "save"
    SAVE_AS = "save_as"
    EXPORT = "export"
    IMPORT = "import"
    
    # Edit operations
    UNDO = "undo"
    REDO = "redo"
    CUT = "cut"
    COPY = "copy"
    PASTE = "paste"
    DELETE = "delete"
    DUPLICATE = "duplicate"
    SELECT_ALL = "select_all"
    
    # View operations
    TOGGLE_PREVIEW = "toggle_preview"
    TOGGLE_CODE = "toggle_code"
    TOGGLE_VISUAL = "toggle_visual"
    TOGGLE_GRID = "toggle_grid"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ZOOM_RESET = "zoom_reset"
    TOGGLE_PROPERTIES = "toggle_properties"
    TOGGLE_TREE = "toggle_tree"
    
    # Component operations
    NEW_TEXT = "new_text"
    NEW_IMAGE = "new_image"
    NEW_DIVIDER = "new_divider"
    NEW_CONTAINER = "new_container"
    
    # Navigation
    NEXT_COMPONENT = "next_component"
    PREV_COMPONENT = "prev_component"
    PARENT_COMPONENT = "parent_component"
    
    # Alignment
    ALIGN_LEFT = "align_left"
    ALIGN_CENTER = "align_center"
    ALIGN_RIGHT = "align_right"
    ALIGN_TOP = "align_top"
    ALIGN_MIDDLE = "align_middle"
    ALIGN_BOTTOM = "align_bottom"
    
    # Other
    FIND = "find"
    HELP = "help"
    SETTINGS = "settings"


# Default keyboard shortcuts
DEFAULT_SHORTCUTS = {
    # File
    ShortcutAction.SAVE: "Ctrl+S",
    ShortcutAction.SAVE_AS: "Ctrl+Shift+S",
    ShortcutAction.EXPORT: "Ctrl+E",
    ShortcutAction.IMPORT: "Ctrl+I",
    
    # Edit
    ShortcutAction.UNDO: "Ctrl+Z",
    ShortcutAction.REDO: "Ctrl+Y",
    ShortcutAction.CUT: "Ctrl+X",
    ShortcutAction.COPY: "Ctrl+C",
    ShortcutAction.PASTE: "Ctrl+V",
    ShortcutAction.DELETE: "Del",
    ShortcutAction.DUPLICATE: "Ctrl+D",
    ShortcutAction.SELECT_ALL: "Ctrl+A",
    
    # View
    ShortcutAction.TOGGLE_PREVIEW: "Ctrl+Shift+P",
    ShortcutAction.TOGGLE_CODE: "Ctrl+Shift+C",
    ShortcutAction.TOGGLE_VISUAL: "Ctrl+Shift+V",
    ShortcutAction.TOGGLE_GRID: "Ctrl+G",
    ShortcutAction.ZOOM_IN: "Ctrl++",
    ShortcutAction.ZOOM_OUT: "Ctrl+-",
    ShortcutAction.ZOOM_RESET: "Ctrl+0",
    ShortcutAction.TOGGLE_PROPERTIES: "Ctrl+Shift+R",
    ShortcutAction.TOGGLE_TREE: "Ctrl+Shift+T",
    
    # Component
    ShortcutAction.NEW_TEXT: "Ctrl+T",
    ShortcutAction.NEW_IMAGE: "Ctrl+Shift+I",
    ShortcutAction.NEW_DIVIDER: "Ctrl+Shift+D",
    ShortcutAction.NEW_CONTAINER: "Ctrl+Shift+B",
    
    # Navigation
    ShortcutAction.NEXT_COMPONENT: "Tab",
    ShortcutAction.PREV_COMPONENT: "Shift+Tab",
    ShortcutAction.PARENT_COMPONENT: "Ctrl+Up",
    
    # Alignment
    ShortcutAction.ALIGN_LEFT: "Ctrl+Shift+L",
    ShortcutAction.ALIGN_CENTER: "Ctrl+Shift+H",
    ShortcutAction.ALIGN_RIGHT: "Ctrl+Shift+R",
    ShortcutAction.ALIGN_TOP: "Ctrl+Shift+T",
    ShortcutAction.ALIGN_MIDDLE: "Ctrl+Shift+M",
    ShortcutAction.ALIGN_BOTTOM: "Ctrl+Shift+B",
    
    # Other
    ShortcutAction.FIND: "Ctrl+F",
    ShortcutAction.HELP: "F1",
    ShortcutAction.SETTINGS: "Ctrl+,",
}


class ShortcutManager(QObject):
    """
    Manages keyboard shortcuts for the application.
    
    Provides a centralized way to register, modify, and handle keyboard shortcuts.
    """
    
    shortcut_triggered = pyqtSignal(ShortcutAction)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize shortcut manager.
        
        Args:
            parent: Parent widget for shortcuts
        """
        super().__init__(parent)
        self.parent_widget = parent
        self.shortcuts: Dict[ShortcutAction, QShortcut] = {}
        self.custom_shortcuts: Dict[ShortcutAction, str] = {}
        self.handlers: Dict[ShortcutAction, Callable] = {}
    
    def register_action(self, action: ShortcutAction, handler: Callable,
                       custom_key: Optional[str] = None) -> QShortcut:
        """
        Register a keyboard shortcut for an action.
        
        Args:
            action: The action to trigger
            handler: Callback function to execute
            custom_key: Custom key sequence (overrides default)
            
        Returns:
            QShortcut: The created shortcut
        """
        # Get key sequence
        key_sequence = custom_key if custom_key else DEFAULT_SHORTCUTS.get(action, "")
        
        if not key_sequence:
            raise ValueError(f"No key sequence defined for action {action}")
        
        # Create shortcut
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent_widget)
        shortcut.activated.connect(handler)
        shortcut.activated.connect(lambda: self.shortcut_triggered.emit(action))
        
        # Store shortcut and handler
        self.shortcuts[action] = shortcut
        self.handlers[action] = handler
        
        if custom_key:
            self.custom_shortcuts[action] = custom_key
        
        return shortcut
    
    def unregister_action(self, action: ShortcutAction):
        """
        Unregister a keyboard shortcut.
        
        Args:
            action: The action to unregister
        """
        if action in self.shortcuts:
            self.shortcuts[action].setEnabled(False)
            del self.shortcuts[action]
        
        if action in self.handlers:
            del self.handlers[action]
        
        if action in self.custom_shortcuts:
            del self.custom_shortcuts[action]
    
    def set_shortcut(self, action: ShortcutAction, key_sequence: str) -> bool:
        """
        Change the key sequence for an action.
        
        Args:
            action: The action to modify
            key_sequence: New key sequence
            
        Returns:
            bool: True if successful
        """
        if action not in self.shortcuts:
            return False
        
        # Update the shortcut
        self.shortcuts[action].setKey(QKeySequence(key_sequence))
        self.custom_shortcuts[action] = key_sequence
        return True
    
    def enable_action(self, action: ShortcutAction, enabled: bool = True):
        """
        Enable or disable a shortcut.
        
        Args:
            action: The action to enable/disable
            enabled: Whether to enable (True) or disable (False)
        """
        if action in self.shortcuts:
            self.shortcuts[action].setEnabled(enabled)
    
    def get_shortcut_text(self, action: ShortcutAction) -> str:
        """
        Get the key sequence text for an action.
        
        Args:
            action: The action to query
            
        Returns:
            str: Key sequence text (e.g., "Ctrl+S")
        """
        if action in self.custom_shortcuts:
            return self.custom_shortcuts[action]
        return DEFAULT_SHORTCUTS.get(action, "")
    
    def get_all_shortcuts(self) -> Dict[ShortcutAction, str]:
        """
        Get all registered shortcuts.
        
        Returns:
            Dict mapping actions to key sequences
        """
        result = {}
        for action in self.shortcuts.keys():
            result[action] = self.get_shortcut_text(action)
        return result
    
    def save_shortcuts(self) -> Dict[str, str]:
        """
        Save custom shortcuts to a dictionary.
        
        Returns:
            Dict suitable for JSON serialization
        """
        return {action.value: key for action, key in self.custom_shortcuts.items()}
    
    def load_shortcuts(self, shortcuts_dict: Dict[str, str]):
        """
        Load custom shortcuts from a dictionary.
        
        Args:
            shortcuts_dict: Dict mapping action names to key sequences
        """
        for action_name, key_sequence in shortcuts_dict.items():
            try:
                action = ShortcutAction(action_name)
                if action in self.shortcuts:
                    self.set_shortcut(action, key_sequence)
            except ValueError:
                # Unknown action, skip
                pass
    
    def reset_to_defaults(self):
        """Reset all shortcuts to their default values."""
        for action, shortcut in self.shortcuts.items():
            default_key = DEFAULT_SHORTCUTS.get(action, "")
            if default_key:
                shortcut.setKey(QKeySequence(default_key))
        
        self.custom_shortcuts.clear()
    
    def get_conflicting_shortcuts(self) -> Dict[str, list]:
        """
        Find shortcuts with conflicting key sequences.
        
        Returns:
            Dict mapping key sequences to lists of conflicting actions
        """
        conflicts = {}
        key_to_actions = {}
        
        for action, shortcut in self.shortcuts.items():
            key = shortcut.key().toString()
            if key:
                if key not in key_to_actions:
                    key_to_actions[key] = []
                key_to_actions[key].append(action)
        
        # Filter to only conflicts
        for key, actions in key_to_actions.items():
            if len(actions) > 1:
                conflicts[key] = actions
        
        return conflicts
