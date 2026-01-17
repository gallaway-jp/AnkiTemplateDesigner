"""
Comprehensive tests for Selection Clarity System (Issue #52).
"""

import unittest
from services.selection_manager import (
    SelectionManager, SelectionMode, SelectionState, SelectionItem, BreadcrumbItem
)


class TestSelectionItem(unittest.TestCase):
    """Test SelectionItem functionality."""

    def test_create_item(self):
        """Test creating a selection item."""
        item = SelectionItem(
            id='comp_1',
            name='MyComponent',
            type='component',
            path='root/components'
        )
        self.assertEqual(item.id, 'comp_1')
        self.assertEqual(item.name, 'MyComponent')
        self.assertEqual(item.type, 'component')

    def test_item_to_dict(self):
        """Test converting item to dictionary."""
        item = SelectionItem(
            id='comp_1',
            name='Test',
            type='component',
            path='root/comp',
            properties={'color': 'red'}
        )
        d = item.to_dict()
        self.assertEqual(d['id'], 'comp_1')
        self.assertEqual(d['properties'], {'color': 'red'})

    def test_item_with_parent(self):
        """Test item with parent reference."""
        item = SelectionItem(
            id='child_1',
            parent_id='parent_1',
            type='child'
        )
        self.assertEqual(item.parent_id, 'parent_1')


class TestBreadcrumbItem(unittest.TestCase):
    """Test BreadcrumbItem functionality."""

    def test_create_breadcrumb(self):
        """Test creating breadcrumb."""
        breadcrumb = BreadcrumbItem(
            id='breadcrumb_1',
            name='Home',
            type='level',
            level=0
        )
        self.assertEqual(breadcrumb.name, 'Home')
        self.assertEqual(breadcrumb.level, 0)

    def test_breadcrumb_to_dict(self):
        """Test breadcrumb serialization."""
        breadcrumb = BreadcrumbItem(
            id='breadcrumb_1',
            name='Components',
            level=1
        )
        d = breadcrumb.to_dict()
        self.assertEqual(d['name'], 'Components')
        self.assertEqual(d['level'], 1)


class TestSelectionManagerBasics(unittest.TestCase):
    """Test basic SelectionManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item1 = SelectionItem(
            id='item_1',
            name='Item 1',
            type='component',
            path='root/items'
        )
        self.item2 = SelectionItem(
            id='item_2',
            name='Item 2',
            type='component',
            path='root/items'
        )

    def test_initialization(self):
        """Test manager initializes correctly."""
        self.assertEqual(len(self.manager.selected_items), 0)
        self.assertEqual(self.manager.selection_state, SelectionState.IDLE)
        self.assertEqual(self.manager.mode, SelectionMode.MULTIPLE)

    def test_select_single_item(self):
        """Test selecting a single item."""
        result = self.manager.select_item(self.item1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.selected_items), 1)
        self.assertEqual(self.manager.active_item, 'item_1')

    def test_select_multiple_items(self):
        """Test selecting multiple items."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        self.assertEqual(len(self.manager.selected_items), 2)
        self.assertEqual(self.manager.selection_state, SelectionState.MULTI_SELECTED)

    def test_deselect_item(self):
        """Test deselecting an item."""
        self.manager.select_item(self.item1)
        self.manager.deselect_item('item_1')
        
        self.assertEqual(len(self.manager.selected_items), 0)
        self.assertEqual(self.manager.selection_state, SelectionState.IDLE)

    def test_clear_selection(self):
        """Test clearing all selection."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        result = self.manager.clear_selection()
        self.assertTrue(result)
        self.assertEqual(len(self.manager.selected_items), 0)

    def test_get_selected_items(self):
        """Test retrieving selected items."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        items = self.manager.get_selected_items()
        self.assertEqual(len(items), 2)

    def test_is_selected(self):
        """Test checking if item is selected."""
        self.manager.select_item(self.item1)
        
        self.assertTrue(self.manager.is_selected('item_1'))
        self.assertFalse(self.manager.is_selected('item_2'))


class TestSingleSelectionMode(unittest.TestCase):
    """Test single selection mode."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager(mode=SelectionMode.SINGLE)
        self.item1 = SelectionItem(id='item_1', name='Item 1', type='component')
        self.item2 = SelectionItem(id='item_2', name='Item 2', type='component')

    def test_single_mode_replaces_selection(self):
        """Test single mode replaces previous selection."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2)
        
        self.assertEqual(len(self.manager.selected_items), 1)
        self.assertEqual(self.manager.active_item, 'item_2')

    def test_single_mode_with_append_false(self):
        """Test append=False clears selection."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=False)
        
        self.assertEqual(len(self.manager.selected_items), 1)
        self.assertFalse(self.manager.is_selected('item_1'))


class TestBreadcrumbs(unittest.TestCase):
    """Test breadcrumb functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item = SelectionItem(
            id='item_1',
            name='Component',
            type='component',
            path='root/pages/canvas'
        )

    def test_breadcrumb_creation(self):
        """Test breadcrumbs created on selection."""
        self.manager.select_item(self.item)
        breadcrumbs = self.manager.get_breadcrumbs()
        
        self.assertGreater(len(breadcrumbs), 0)
        self.assertEqual(breadcrumbs[-1].name, 'Component')

    def test_breadcrumb_hierarchy(self):
        """Test breadcrumb hierarchy levels."""
        self.manager.select_item(self.item)
        breadcrumbs = self.manager.get_breadcrumbs()
        
        for i, crumb in enumerate(breadcrumbs):
            self.assertEqual(crumb.level, i)

    def test_navigate_breadcrumb(self):
        """Test navigation via breadcrumb."""
        self.manager.select_item(self.item)
        breadcrumbs = self.manager.get_breadcrumbs()
        
        result = self.manager.navigate_breadcrumb(breadcrumbs[0].id)
        self.assertTrue(result)

    def test_breadcrumb_cleared_on_deselect(self):
        """Test breadcrumbs cleared when all items deselected."""
        self.manager.select_item(self.item)
        self.manager.clear_selection()
        
        self.assertEqual(len(self.manager.get_breadcrumbs()), 0)


class TestActiveItem(unittest.TestCase):
    """Test active item management."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item1 = SelectionItem(id='item_1', name='Item 1', type='component')
        self.item2 = SelectionItem(id='item_2', name='Item 2', type='component')

    def test_set_active_item(self):
        """Test setting active item."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        result = self.manager.set_active_item('item_2')
        self.assertTrue(result)
        self.assertEqual(self.manager.active_item, 'item_2')

    def test_get_active_item(self):
        """Test retrieving active item."""
        self.manager.select_item(self.item1)
        active = self.manager.get_active_item()
        
        self.assertIsNotNone(active)
        self.assertEqual(active.id, 'item_1')

    def test_focus_item_tracking(self):
        """Test focus item is tracked separately."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        self.assertEqual(self.manager.focus_item, 'item_2')


class TestSelectionToggle(unittest.TestCase):
    """Test toggle selection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item = SelectionItem(id='item_1', name='Item 1', type='component')

    def test_toggle_selects_unselected(self):
        """Test toggle selects unselected item."""
        result = self.manager.toggle_item(self.item)
        self.assertTrue(result)
        self.assertTrue(self.manager.is_selected('item_1'))

    def test_toggle_deselects_selected(self):
        """Test toggle deselects selected item."""
        self.manager.select_item(self.item)
        result = self.manager.toggle_item(self.item)
        
        self.assertFalse(result)
        self.assertFalse(self.manager.is_selected('item_1'))


class TestSelectionInversion(unittest.TestCase):
    """Test selection inversion."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.items = [
            SelectionItem(id='item_1', name='Item 1', type='component'),
            SelectionItem(id='item_2', name='Item 2', type='component'),
            SelectionItem(id='item_3', name='Item 3', type='component')
        ]

    def test_invert_selection(self):
        """Test inverting selection."""
        self.manager.select_item(self.items[0])
        self.manager.select_item(self.items[1], append=True)
        
        self.manager.invert_selection(self.items)
        
        self.assertFalse(self.manager.is_selected('item_1'))
        self.assertFalse(self.manager.is_selected('item_2'))
        self.assertTrue(self.manager.is_selected('item_3'))


class TestSelectByType(unittest.TestCase):
    """Test selecting by type."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.items = [
            SelectionItem(id='item_1', name='Item 1', type='component'),
            SelectionItem(id='item_2', name='Item 2', type='component'),
            SelectionItem(id='item_3', name='Item 3', type='container')
        ]

    def test_select_by_type(self):
        """Test selecting items by type."""
        count = self.manager.select_by_type('component', self.items)
        
        self.assertEqual(count, 2)
        self.assertEqual(len(self.manager.selected_items), 2)
        self.assertTrue(self.manager.is_selected('item_1'))
        self.assertTrue(self.manager.is_selected('item_2'))
        self.assertFalse(self.manager.is_selected('item_3'))

    def test_select_by_nonexistent_type(self):
        """Test selecting non-existent type."""
        count = self.manager.select_by_type('nonexistent', self.items)
        
        self.assertEqual(count, 0)


class TestHighlighting(unittest.TestCase):
    """Test highlighting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()

    def test_highlight_color(self):
        """Test setting highlight color."""
        self.manager.set_highlight_color('#FF0000')
        self.assertEqual(self.manager.highlight_color, '#FF0000')

    def test_highlight_enabled(self):
        """Test enabling/disabling highlighting."""
        self.assertTrue(self.manager.highlight_enabled)
        self.manager.set_highlight_enabled(False)
        self.assertFalse(self.manager.highlight_enabled)


class TestSelectionMode(unittest.TestCase):
    """Test selection mode switching."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager(mode=SelectionMode.MULTIPLE)
        self.item1 = SelectionItem(id='item_1', name='Item 1', type='component')
        self.item2 = SelectionItem(id='item_2', name='Item 2', type='component')

    def test_change_selection_mode(self):
        """Test changing selection mode."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        self.manager.set_selection_mode(SelectionMode.SINGLE)
        
        # Should enforce single selection
        self.assertEqual(len(self.manager.selected_items), 1)

    def test_mode_reflects_in_statistics(self):
        """Test mode appears in statistics."""
        self.manager.set_selection_mode(SelectionMode.RANGE)
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['selection_mode'], 'range')


class TestUndoSelection(unittest.TestCase):
    """Test selection undo functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item1 = SelectionItem(id='item_1', name='Item 1', type='component')
        self.item2 = SelectionItem(id='item_2', name='Item 2', type='component')

    def test_undo_selection(self):
        """Test undoing selection."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        result = self.manager.undo_selection()
        self.assertTrue(result)
        self.assertEqual(len(self.manager.selected_items), 1)

    def test_undo_at_start(self):
        """Test undo when no history."""
        result = self.manager.undo_selection()
        self.assertFalse(result)

    def test_selection_history_size(self):
        """Test selection history respects max size."""
        for i in range(60):
            item = SelectionItem(id=f'item_{i}', name=f'Item {i}', type='component')
            self.manager.select_item(item)
        
        self.assertLessEqual(len(self.manager.selection_history), 50)


class TestEventListeners(unittest.TestCase):
    """Test event listener functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.events = []

    def listener(self, event_type, data):
        """Capture events."""
        self.events.append((event_type, data))

    def test_add_listener(self):
        """Test adding listener."""
        self.manager.add_listener(self.listener)
        self.assertEqual(len(self.manager.listeners), 1)

    def test_selection_changed_event(self):
        """Test event fired on selection change."""
        self.manager.add_listener(self.listener)
        item = SelectionItem(id='item_1', name='Item 1', type='component')
        self.manager.select_item(item)
        
        self.assertGreater(len(self.events), 0)
        self.assertEqual(self.events[0][0], 'selection_changed')

    def test_remove_listener(self):
        """Test removing listener."""
        self.manager.add_listener(self.listener)
        self.manager.remove_listener(self.listener)
        
        self.assertEqual(len(self.manager.listeners), 0)


class TestExportImport(unittest.TestCase):
    """Test export/import functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item1 = SelectionItem(id='item_1', name='Item 1', type='component')
        self.item2 = SelectionItem(id='item_2', name='Item 2', type='component')

    def test_export_selection(self):
        """Test exporting selection state."""
        self.manager.select_item(self.item1)
        self.manager.select_item(self.item2, append=True)
        
        exported = self.manager.export_selection()
        
        self.assertEqual(len(exported['items']), 2)
        self.assertIsNotNone(exported['timestamp'])

    def test_import_selection(self):
        """Test importing selection state."""
        self.manager.select_item(self.item1)
        exported = self.manager.export_selection()
        
        new_manager = SelectionManager()
        result = new_manager.import_selection(exported)
        
        self.assertTrue(result)
        self.assertEqual(len(new_manager.selected_items), 1)

    def test_import_empty_selection(self):
        """Test importing empty selection."""
        data = {
            'items': [],
            'active_item': None,
            'mode': 'multiple',
            'state': 'idle',
            'timestamp': ''
        }
        
        result = self.manager.import_selection(data)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.selected_items), 0)


class TestFocusNavigation(unittest.TestCase):
    """Test focus navigation."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.items = [
            SelectionItem(id='item_1', name='Item 1', type='component'),
            SelectionItem(id='item_2', name='Item 2', type='component'),
            SelectionItem(id='item_3', name='Item 3', type='component')
        ]

    def test_focus_next(self):
        """Test moving focus to next item."""
        self.manager.focus_item = 'item_1'
        result = self.manager.focus_next(self.items)
        
        self.assertTrue(result)
        self.assertEqual(self.manager.focus_item, 'item_2')

    def test_focus_previous(self):
        """Test moving focus to previous item."""
        self.manager.focus_item = 'item_2'
        result = self.manager.focus_previous(self.items)
        
        self.assertTrue(result)
        self.assertEqual(self.manager.focus_item, 'item_1')

    def test_focus_next_at_end(self):
        """Test focus next at end of list."""
        self.manager.focus_item = 'item_3'
        result = self.manager.focus_next(self.items)
        
        self.assertFalse(result)


class TestStatistics(unittest.TestCase):
    """Test statistics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SelectionManager()
        self.item = SelectionItem(id='item_1', name='Item 1', type='component')

    def test_empty_statistics(self):
        """Test statistics with no selection."""
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_selected'], 0)
        self.assertEqual(stats['selection_state'], 'idle')

    def test_selection_statistics(self):
        """Test statistics with selection."""
        self.manager.select_item(self.item)
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_selected'], 1)
        self.assertEqual(stats['selection_state'], 'selected')
        self.assertTrue(stats['has_active_item'])


if __name__ == '__main__':
    unittest.main()
