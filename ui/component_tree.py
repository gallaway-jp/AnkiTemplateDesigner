"""
Component Tree widget - hierarchical view of template components
Inspired by Android Studio's Component Tree
"""

from aqt.qt import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QMenu, QAction, Qt, QLabel, QHBoxLayout, QPushButton, QLineEdit
)
from typing import Optional, List, Callable
from .components import Component, ComponentType
from .component_search import ComponentSearchWidget


class ComponentTreeItem(QTreeWidgetItem):
    """Tree item representing a component"""
    
    def __init__(self, component: Component, parent=None):
        super().__init__(parent)
        self.component = component
        self.update_display()
    
    def update_display(self):
        """Update the display text for this item"""
        # Show component type and field name if applicable
        type_name = self.component.type.value.replace('_', ' ').title()
        
        if hasattr(self.component, 'field_name') and self.component.field_name:
            display_text = f"{type_name} ({self.component.field_name})"
        else:
            display_text = type_name
        
        self.setText(0, display_text)
        
        # Set icon based on component type
        # Note: Could add icons here for better visual hierarchy


class ComponentTree(QWidget):
    """
    Component Tree widget providing hierarchical view of all components.
    Similar to Android Studio's Component Tree panel.
    
    Features:
    - Hierarchical display of components
    - Drag to reorder (within same parent)
    - Right-click context menu
    - Selection synchronization with canvas
    - Visual feedback for selected component
    """
    
    def __init__(self, parent=None, 
                 on_selection_change: Optional[Callable[[Optional[Component]], None]] = None,
                 on_structure_change: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_selection_change = on_selection_change
        self.on_structure_change = on_structure_change
        self.components: List[Component] = []
        self.updating = False  # Prevent recursive updates
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        title = QLabel("<b>Component Tree</b>")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Collapse/Expand buttons
        expand_btn = QPushButton("Expand All")
        expand_btn.setMaximumWidth(80)
        expand_btn.clicked.connect(self.expand_all)
        header_layout.addWidget(expand_btn)
        
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.setMaximumWidth(80)
        collapse_btn.clicked.connect(self.collapse_all)
        header_layout.addWidget(collapse_btn)
        
        layout.addWidget(header)
        
        # Search widget
        self.search = ComponentSearchWidget()
        self.search.search_changed.connect(self._on_search_changed)
        layout.addWidget(self.search)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Component Hierarchy")
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Connect signals
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemChanged.connect(self.on_item_moved)
        
        layout.addWidget(self.tree)
    
    def set_components(self, components: List[Component]):
        """Set the components to display in the tree"""
        self.components = components
        self.rebuild_tree()
    
    def rebuild_tree(self):
        """
        Rebuild the component tree from the current component list.
        
        Clears the tree widget and recreates it from scratch, preserving
        the hierarchical structure of containers and their children.
        All tree items are expanded by default.
        
        Called when:
        - Components are added or removed
        - Component hierarchy changes
        - Components are reordered
        - set_components() is called
        """
        self.updating = True
        self.tree.clear()
        
        if not self.components:
            return
        
        # Build tree items
        for component in self.components:
            self._add_component_item(component, self.tree)
        
        # Expand all by default
        self.tree.expandAll()
        self.updating = False
    
    def _add_component_item(self, component: Component, parent) -> ComponentTreeItem:
        """Add a component and its children to the tree"""
        item = ComponentTreeItem(component, parent)
        
        # Add child components if this is a container
        if component.type == ComponentType.CONTAINER and hasattr(component, 'children'):
            for child in component.children:
                self._add_component_item(child, item)
        
        return item
    
    def on_tree_selection_changed(self):
        """Handle tree selection change"""
        if self.updating:
            return
        
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            if isinstance(item, ComponentTreeItem):
                if self.on_selection_change:
                    self.on_selection_change(item.component)
        else:
            if self.on_selection_change:
                self.on_selection_change(None)
    
    def select_component(self, component: Optional[Component]):
        """Select a component in the tree"""
        self.updating = True
        
        if component is None:
            self.tree.clearSelection()
        else:
            # Find the tree item for this component
            item = self._find_item_for_component(component, self.tree.invisibleRootItem())
            if item:
                self.tree.setCurrentItem(item)
                self.tree.scrollToItem(item)
        
        self.updating = False
    
    def _find_item_for_component(self, component: Component, parent) -> Optional[ComponentTreeItem]:
        """Find the tree item for a given component"""
        for i in range(parent.childCount()):
            item = parent.child(i)
            if isinstance(item, ComponentTreeItem) and item.component is component:
                return item
            # Recursively search children
            child_result = self._find_item_for_component(component, item)
            if child_result:
                return child_result
        return None
    
    def show_context_menu(self, position):
        """Show context menu for component"""
        item = self.tree.itemAt(position)
        if not item or not isinstance(item, ComponentTreeItem):
            return
        
        menu = QMenu(self)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_component(item.component))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Duplicate action
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_component(item.component))
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        # Move actions
        move_up_action = QAction("Move Up", self)
        move_up_action.triggered.connect(lambda: self.move_component_up(item.component))
        menu.addAction(move_up_action)
        
        move_down_action = QAction("Move Down", self)
        move_down_action.triggered.connect(lambda: self.move_component_down(item.component))
        menu.addAction(move_down_action)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))
    
    def delete_component(self, component: Component):
        """Delete a component"""
        if component in self.components:
            self.components.remove(component)
            self.rebuild_tree()
            if self.on_structure_change:
                self.on_structure_change()
    
    def duplicate_component(self, component: Component):
        """Duplicate a component"""
        import copy
        new_component = copy.deepcopy(component)
        
        # Insert after the original
        try:
            index = self.components.index(component)
            self.components.insert(index + 1, new_component)
            self.rebuild_tree()
            if self.on_structure_change:
                self.on_structure_change()
        except ValueError:
            pass
    
    def move_component_up(self, component: Component):
        """Move component up in the list"""
        try:
            index = self.components.index(component)
            if index > 0:
                self.components[index], self.components[index - 1] = \
                    self.components[index - 1], self.components[index]
                self.rebuild_tree()
                self.select_component(component)
                if self.on_structure_change:
                    self.on_structure_change()
        except ValueError:
            pass
    
    def move_component_down(self, component: Component):
        """Move component down in the list"""
        try:
            index = self.components.index(component)
            if index < len(self.components) - 1:
                self.components[index], self.components[index + 1] = \
                    self.components[index + 1], self.components[index]
                self.rebuild_tree()
                self.select_component(component)
                if self.on_structure_change:
                    self.on_structure_change()
        except ValueError:
            pass
    
    def on_item_moved(self, item, column):
        """Handle item being moved via drag-drop"""
        if self.updating:
            return
        
        # Rebuild components list from tree structure
        self.components.clear()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            tree_item = root.child(i)
            if isinstance(tree_item, ComponentTreeItem):
                self.components.append(tree_item.component)
        
        if self.on_structure_change:
            self.on_structure_change()
    
    def expand_all(self):
        """Expand all tree items"""
        self.tree.expandAll()
    
    def collapse_all(self):
        """Collapse all tree items"""
        self.tree.collapseAll()
    
    def _on_search_changed(self, pattern: str, case_sensitive: bool):
        """Handle search pattern change - filter tree items"""
        if not pattern:
            # Show all items
            self._show_all_items()
            return
        
        # Hide items that don't match
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._filter_item(root.child(i), pattern, case_sensitive)
    
    def _filter_item(self, item: QTreeWidgetItem, pattern: str, case_sensitive: bool) -> bool:
        """
        Recursively filter tree items based on search pattern.
        Returns True if item or any child matches.
        """
        if not isinstance(item, ComponentTreeItem):
            return False
        
        # Check if this component matches
        matches = self.search.matches(item.component, pattern, case_sensitive)
        
        # Check children
        has_matching_child = False
        for i in range(item.childCount()):
            child_matches = self._filter_item(item.child(i), pattern, case_sensitive)
            has_matching_child = has_matching_child or child_matches
        
        # Show item if it matches or has matching children
        should_show = matches or has_matching_child
        item.setHidden(not should_show)
        
        # Expand items with matching children
        if has_matching_child:
            item.setExpanded(True)
        
        return should_show
    
    def _show_all_items(self):
        """Show all tree items (clear filter)"""
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._show_item_recursive(root.child(i))
    
    def _show_item_recursive(self, item: QTreeWidgetItem):
        """Recursively show an item and all its children"""
        item.setHidden(False)
        for i in range(item.childCount()):
            self._show_item_recursive(item.child(i))
        """Collapse all tree items"""
        self.tree.collapseAll()
    
    def get_components(self) -> List[Component]:
        """Get the current components list"""
        return self.components
