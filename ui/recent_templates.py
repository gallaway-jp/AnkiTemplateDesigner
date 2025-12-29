"""
Recent templates menu functionality.

Tracks recently opened templates and provides quick access.
"""

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QObject
from typing import List, Optional
from pathlib import Path
import json
from utils.logging_config import get_logger

logger = get_logger(__name__)


class RecentTemplatesManager(QObject):
    """
    Manager for recent templates history.
    
    Tracks recently opened templates and provides menu integration.
    """
    
    # Signals
    template_selected = pyqtSignal(str)  # (file_path)
    
    # Constants
    MAX_RECENT = 10
    RECENT_FILE = "recent_templates.json"
    
    def __init__(self, config_dir: str = None):
        """
        Initialize recent templates manager.
        
        Args:
            config_dir: Directory to store recent templates file
        """
        super().__init__()
        
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to user's config directory
            from pathlib import Path
            self.config_dir = Path.home() / ".anki_template_designer"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.recent_file = self.config_dir / self.RECENT_FILE
        
        self.recent_templates: List[str] = []
        self._load_recent()
    
    def add_template(self, file_path: str):
        """
        Add a template to recent list.
        
        Args:
            file_path: Path to template file
        """
        # Convert to absolute path
        file_path = str(Path(file_path).resolve())
        
        # Remove if already exists (to move to top)
        if file_path in self.recent_templates:
            self.recent_templates.remove(file_path)
        
        # Add to front of list
        self.recent_templates.insert(0, file_path)
        
        # Trim to max size
        self.recent_templates = self.recent_templates[:self.MAX_RECENT]
        
        # Save
        self._save_recent()
        
        logger.debug(f"Added {file_path} to recent templates")
    
    def remove_template(self, file_path: str):
        """
        Remove a template from recent list.
        
        Args:
            file_path: Path to template file
        """
        file_path = str(Path(file_path).resolve())
        
        if file_path in self.recent_templates:
            self.recent_templates.remove(file_path)
            self._save_recent()
            logger.debug(f"Removed {file_path} from recent templates")
    
    def clear_recent(self):
        """Clear all recent templates."""
        self.recent_templates.clear()
        self._save_recent()
        logger.debug("Cleared recent templates")
    
    def get_recent_templates(self, max_count: int = None) -> List[str]:
        """
        Get list of recent templates.
        
        Args:
            max_count: Maximum number to return (None for all)
            
        Returns:
            List of file paths
        """
        # Filter out non-existent files
        self.recent_templates = [
            path for path in self.recent_templates
            if Path(path).exists()
        ]
        
        if max_count:
            return self.recent_templates[:max_count]
        
        return self.recent_templates.copy()
    
    def _load_recent(self):
        """Load recent templates from file."""
        try:
            if self.recent_file.exists():
                with open(self.recent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_templates = data.get('recent', [])
                    
                    # Filter out non-existent files
                    self.recent_templates = [
                        path for path in self.recent_templates
                        if Path(path).exists()
                    ]
                    
                    logger.debug(f"Loaded {len(self.recent_templates)} recent templates")
        
        except Exception as e:
            logger.error(f"Failed to load recent templates: {e}")
            self.recent_templates = []
    
    def _save_recent(self):
        """Save recent templates to file."""
        try:
            data = {
                'recent': self.recent_templates
            }
            
            with open(self.recent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.recent_templates)} recent templates")
        
        except Exception as e:
            logger.error(f"Failed to save recent templates: {e}")
    
    def create_menu(self, parent_menu: QMenu) -> QMenu:
        """
        Create a "Recent Templates" submenu.
        
        Args:
            parent_menu: Parent menu to add submenu to
            
        Returns:
            QMenu: Created submenu
        """
        recent_menu = QMenu("Recent Templates", parent_menu)
        self.update_menu(recent_menu)
        return recent_menu
    
    def update_menu(self, menu: QMenu):
        """
        Update menu with recent templates.
        
        Args:
            menu: Menu to update
        """
        menu.clear()
        
        recent = self.get_recent_templates()
        
        if not recent:
            # No recent templates
            action = QAction("No Recent Templates", menu)
            action.setEnabled(False)
            menu.addAction(action)
        else:
            # Add recent templates
            for i, file_path in enumerate(recent):
                path = Path(file_path)
                
                # Create action with number shortcut (1-9)
                if i < 9:
                    action = QAction(f"{i+1}. {path.name}", menu)
                    action.setShortcut(f"Ctrl+{i+1}")
                else:
                    action = QAction(path.name, menu)
                
                action.setToolTip(str(path))
                action.setData(str(path))
                action.triggered.connect(
                    lambda checked=False, p=str(path): self._on_template_selected(p)
                )
                menu.addAction(action)
            
            # Add separator
            menu.addSeparator()
            
            # Add "Clear Recent" action
            clear_action = QAction("Clear Recent Templates", menu)
            clear_action.triggered.connect(self._on_clear_recent)
            menu.addAction(clear_action)
    
    def _on_template_selected(self, file_path: str):
        """Handle template selection from menu."""
        self.template_selected.emit(file_path)
    
    def _on_clear_recent(self):
        """Handle clear recent action."""
        self.clear_recent()


class RecentTemplatesMenuManager:
    """
    Helper class to integrate recent templates into application menu.
    
    Manages the File → Recent Templates submenu.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize menu manager.
        
        Args:
            config_dir: Directory for config files
        """
        self.manager = RecentTemplatesManager(config_dir)
        self.recent_menu: Optional[QMenu] = None
    
    def setup_menu(self, file_menu: QMenu, insert_before: QAction = None):
        """
        Setup recent templates submenu in File menu.
        
        Args:
            file_menu: File menu to add submenu to
            insert_before: Optional action to insert before
        """
        # Create submenu
        self.recent_menu = QMenu("Recent Templates", file_menu)
        
        # Add to file menu
        if insert_before:
            file_menu.insertMenu(insert_before, self.recent_menu)
        else:
            file_menu.addMenu(self.recent_menu)
        
        # Update menu
        self.update_menu()
        
        # Connect to show event to update menu when opened
        self.recent_menu.aboutToShow.connect(self.update_menu)
    
    def update_menu(self):
        """Update the recent templates menu."""
        if self.recent_menu:
            self.manager.update_menu(self.recent_menu)
    
    def add_template(self, file_path: str):
        """
        Add template to recent list.
        
        Args:
            file_path: Path to template file
        """
        self.manager.add_template(file_path)
        self.update_menu()
    
    def get_manager(self) -> RecentTemplatesManager:
        """Get the underlying manager."""
        return self.manager
    
    def connect_template_selected(self, callback):
        """
        Connect callback to template selection.
        
        Args:
            callback: Callback function(file_path)
        """
        self.manager.template_selected.connect(callback)


def create_recent_templates_menu(
    file_menu: QMenu,
    config_dir: str = None,
    on_template_selected=None,
    insert_before: QAction = None
) -> RecentTemplatesMenuManager:
    """
    Convenience function to create recent templates menu.
    
    Args:
        file_menu: File menu to add submenu to
        config_dir: Directory for config files
        on_template_selected: Callback for template selection
        insert_before: Optional action to insert before
        
    Returns:
        RecentTemplatesMenuManager: Created menu manager
    """
    manager = RecentTemplatesMenuManager(config_dir)
    manager.setup_menu(file_menu, insert_before)
    
    if on_template_selected:
        manager.connect_template_selected(on_template_selected)
    
    return manager
