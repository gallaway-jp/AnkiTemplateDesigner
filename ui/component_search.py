"""
Component search functionality for component tree.

Provides search and filtering capabilities for finding components quickly.
"""

from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from typing import List, Optional
import re


class ComponentSearchWidget(QWidget):
    """
    Search widget for filtering components in tree.
    
    Provides text search with case-sensitivity toggle and regex support.
    """
    
    # Signals
    search_changed = pyqtSignal(str, bool, bool)  # (query, case_sensitive, use_regex)
    clear_search = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize component search widget."""
        super().__init__(parent)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Search icon/label
        self.search_label = QLabel("🔍")
        self.search_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search components...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        layout.addWidget(self.search_input, 1)
        
        # Case sensitivity toggle
        self.case_sensitive_btn = QPushButton("Aa")
        self.case_sensitive_btn.setCheckable(True)
        self.case_sensitive_btn.setChecked(False)
        self.case_sensitive_btn.setToolTip("Case Sensitive")
        self.case_sensitive_btn.setMaximumWidth(35)
        self.case_sensitive_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
            }
            QPushButton:checked {
                background: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
            }
        """)
        layout.addWidget(self.case_sensitive_btn)
        
        # Regex toggle
        self.regex_btn = QPushButton(".*")
        self.regex_btn.setCheckable(True)
        self.regex_btn.setChecked(False)
        self.regex_btn.setToolTip("Use Regular Expression")
        self.regex_btn.setMaximumWidth(35)
        self.regex_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
            }
            QPushButton:checked {
                background: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
            }
        """)
        layout.addWidget(self.regex_btn)
        
        # Match count label
        self.match_label = QLabel("")
        self.match_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.match_label)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.search_input.textChanged.connect(self._on_search_changed)
        self.case_sensitive_btn.toggled.connect(self._on_search_changed)
        self.regex_btn.toggled.connect(self._on_search_changed)
        self.search_input.textChanged.connect(lambda text: self.clear_search.emit() if not text else None)
    
    def _on_search_changed(self):
        """Handle search text or options changed."""
        query = self.search_input.text()
        case_sensitive = self.case_sensitive_btn.isChecked()
        use_regex = self.regex_btn.isChecked()
        
        self.search_changed.emit(query, case_sensitive, use_regex)
    
    def set_match_count(self, count: int, total: int):
        """
        Update match count label.
        
        Args:
            count: Number of matches
            total: Total number of items
        """
        if self.search_input.text():
            self.match_label.setText(f"{count}/{total}")
        else:
            self.match_label.setText("")
    
    def clear(self):
        """Clear the search input."""
        self.search_input.clear()
    
    def get_query(self) -> str:
        """Get current search query."""
        return self.search_input.text()
    
    def is_case_sensitive(self) -> bool:
        """Check if case-sensitive search is enabled."""
        return self.case_sensitive_btn.isChecked()
    
    def is_regex(self) -> bool:
        """Check if regex search is enabled."""
        return self.regex_btn.isChecked()


class ComponentFilter:
    """
    Filter logic for component tree.
    
    Handles matching components against search queries.
    """
    
    @staticmethod
    def matches_query(
        item_text: str,
        query: str,
        case_sensitive: bool = False,
        use_regex: bool = False
    ) -> bool:
        """
        Check if item text matches search query.
        
        Args:
            item_text: Text to search in
            query: Search query
            case_sensitive: Use case-sensitive matching
            use_regex: Treat query as regex pattern
            
        Returns:
            bool: True if matches
        """
        if not query:
            return True
        
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
                return bool(pattern.search(item_text))
            except re.error:
                # Invalid regex, fall back to plain text
                use_regex = False
        
        if not use_regex:
            if not case_sensitive:
                item_text = item_text.lower()
                query = query.lower()
            
            return query in item_text
        
        return False
    
    @staticmethod
    def filter_tree_items(
        tree: QTreeWidget,
        query: str,
        case_sensitive: bool = False,
        use_regex: bool = False
    ) -> int:
        """
        Filter tree widget items based on query.
        
        Args:
            tree: Tree widget to filter
            query: Search query
            case_sensitive: Use case-sensitive matching
            use_regex: Treat query as regex
            
        Returns:
            int: Number of visible items
        """
        if not query:
            # Show all items
            ComponentFilter._show_all_items(tree.invisibleRootItem())
            return ComponentFilter._count_visible_items(tree.invisibleRootItem())
        
        # Filter items
        visible_count = ComponentFilter._filter_item_recursive(
            tree.invisibleRootItem(),
            query,
            case_sensitive,
            use_regex
        )
        
        return visible_count
    
    @staticmethod
    def _filter_item_recursive(
        item: QTreeWidgetItem,
        query: str,
        case_sensitive: bool,
        use_regex: bool
    ) -> int:
        """
        Recursively filter tree items.
        
        Args:
            item: Tree item to filter
            query: Search query
            case_sensitive: Case-sensitive matching
            use_regex: Use regex
            
        Returns:
            int: Number of visible children
        """
        visible_count = 0
        
        # Process children first
        for i in range(item.childCount()):
            child = item.child(i)
            child_visible = ComponentFilter._filter_item_recursive(
                child,
                query,
                case_sensitive,
                use_regex
            )
            visible_count += child_visible
        
        # Check if this item matches
        if item.parent() or item.treeWidget():  # Not root
            item_text = item.text(0)
            matches = ComponentFilter.matches_query(
                item_text,
                query,
                case_sensitive,
                use_regex
            )
            
            # Show item if it matches OR has visible children
            should_show = matches or visible_count > 0
            item.setHidden(not should_show)
            
            if should_show:
                visible_count += 1
        
        return visible_count
    
    @staticmethod
    def _show_all_items(item: QTreeWidgetItem):
        """
        Recursively show all tree items.
        
        Args:
            item: Tree item
        """
        item.setHidden(False)
        
        for i in range(item.childCount()):
            ComponentFilter._show_all_items(item.child(i))
    
    @staticmethod
    def _count_visible_items(item: QTreeWidgetItem) -> int:
        """
        Count visible tree items.
        
        Args:
            item: Tree item
            
        Returns:
            int: Number of visible items
        """
        count = 0
        
        for i in range(item.childCount()):
            child = item.child(i)
            if not child.isHidden():
                count += 1
                count += ComponentFilter._count_visible_items(child)
        
        return count


class SearchableComponentTree:
    """
    Mixin to add search functionality to component tree.
    
    Can be used with existing ComponentTree class.
    """
    
    def add_search_widget(self, tree: QTreeWidget, layout: QVBoxLayout):
        """
        Add search widget to component tree layout.
        
        Args:
            tree: Tree widget to search
            layout: Layout to add search widget to
        """
        # Create search widget
        self.search_widget = ComponentSearchWidget()
        
        # Insert at top of layout
        layout.insertWidget(0, self.search_widget)
        
        # Connect signals
        self.search_widget.search_changed.connect(
            lambda q, cs, ur: self._on_search_changed(tree, q, cs, ur)
        )
        self.search_widget.clear_search.connect(
            lambda: self._on_search_cleared(tree)
        )
    
    def _on_search_changed(
        self,
        tree: QTreeWidget,
        query: str,
        case_sensitive: bool,
        use_regex: bool
    ):
        """Handle search query changed."""
        # Filter tree
        visible_count = ComponentFilter.filter_tree_items(
            tree,
            query,
            case_sensitive,
            use_regex
        )
        
        # Update match count
        total_count = self._count_total_items(tree.invisibleRootItem())
        self.search_widget.set_match_count(visible_count, total_count)
        
        # Expand all if searching
        if query:
            tree.expandAll()
    
    def _on_search_cleared(self, tree: QTreeWidget):
        """Handle search cleared."""
        # Show all items
        ComponentFilter._show_all_items(tree.invisibleRootItem())
        
        # Update count
        total_count = self._count_total_items(tree.invisibleRootItem())
        self.search_widget.set_match_count(total_count, total_count)
        
        # Collapse all
        tree.collapseAll()
    
    def _count_total_items(self, item: QTreeWidgetItem) -> int:
        """Count total items in tree."""
        count = 0
        
        for i in range(item.childCount()):
            count += 1
            count += self._count_total_items(item.child(i))
        
        return count
