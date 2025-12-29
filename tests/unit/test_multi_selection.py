"""
Tests for multi-selection functionality.
"""

import pytest
from ui.multi_selection import SelectionManager, SelectionMode, BulkOperations
from ui.components import TextFieldComponent, ImageFieldComponent


class TestSelectionManager:
    """Test SelectionManager"""
    
    def test_select_component(self):
        """Test selecting a single component"""
        manager = SelectionManager()
        component = TextFieldComponent("Test")
        
        manager.select_component(component)
        
        assert manager.is_selected(component)
        assert manager.get_selection_count() == 1
    
    def test_select_replace_mode(self):
        """Test REPLACE selection mode"""
        manager = SelectionManager()
        comp1 = TextFieldComponent("Test1")
        comp2 = TextFieldComponent("Test2")
        
        manager.select_component(comp1, SelectionMode.REPLACE)
        manager.select_component(comp2, SelectionMode.REPLACE)
        
        assert not manager.is_selected(comp1)
        assert manager.is_selected(comp2)
        assert manager.get_selection_count() == 1
    
    def test_select_add_mode(self):
        """Test ADD selection mode"""
        manager = SelectionManager()
        comp1 = TextFieldComponent("Test1")
        comp2 = TextFieldComponent("Test2")
        
        manager.select_component(comp1, SelectionMode.ADD)
        manager.select_component(comp2, SelectionMode.ADD)
        
        assert manager.is_selected(comp1)
        assert manager.is_selected(comp2)
        assert manager.get_selection_count() == 2
    
    def test_select_toggle_mode(self):
        """Test TOGGLE selection mode"""
        manager = SelectionManager()
        component = TextFieldComponent("Test")
        
        manager.select_component(component, SelectionMode.TOGGLE)
        assert manager.is_selected(component)
        
        manager.select_component(component, SelectionMode.TOGGLE)
        assert not manager.is_selected(component)
    
    def test_select_multiple(self):
        """Test selecting multiple components"""
        manager = SelectionManager()
        components = [
            TextFieldComponent("Test1"),
            TextFieldComponent("Test2"),
            TextFieldComponent("Test3")
        ]
        
        manager.select_multiple(components)
        
        assert manager.get_selection_count() == 3
        for comp in components:
            assert manager.is_selected(comp)
    
    def test_clear_selection(self):
        """Test clearing selection"""
        manager = SelectionManager()
        components = [TextFieldComponent("Test1"), TextFieldComponent("Test2")]
        
        manager.select_multiple(components)
        manager.clear_selection()
        
        assert manager.get_selection_count() == 0
    
    def test_get_selection_bounds(self):
        """Test getting selection bounding box"""
        manager = SelectionManager()
        
        comp1 = TextFieldComponent("Test1")
        comp1.x = 0
        comp1.y = 0
        comp1.width = 100
        comp1.height = 50
        
        comp2 = TextFieldComponent("Test2")
        comp2.x = 200
        comp2.y = 100
        comp2.width = 100
        comp2.height = 50
        
        manager.select_multiple([comp1, comp2])
        bounds = manager.get_selection_bounds()
        
        assert bounds is not None
        assert bounds.x() == 0
        assert bounds.y() == 0
        assert bounds.width() == 300  # 200 + 100
        assert bounds.height() == 150  # 100 + 50


class TestBulkOperations:
    """Test BulkOperations"""
    
    def test_align_left(self):
        """Test aligning components to left"""
        comp1 = TextFieldComponent("Test1")
        comp1.x = 100
        
        comp2 = TextFieldComponent("Test2")
        comp2.x = 200
        
        BulkOperations.align_left([comp1, comp2])
        
        assert comp1.x == 100
        assert comp2.x == 100
    
    def test_align_center_horizontal(self):
        """Test aligning components to horizontal center"""
        comp1 = TextFieldComponent("Test1")
        comp1.x = 0
        comp1.width = 100
        
        comp2 = TextFieldComponent("Test2")
        comp2.x = 200
        comp2.width = 100
        
        BulkOperations.align_center_horizontal([comp1, comp2])
        
        # Center should be at (0 + 300) / 2 = 150
        # Each component should be centered at 150
        assert comp1.x == 100  # 150 - 50
        assert comp2.x == 100  # 150 - 50
    
    def test_align_right(self):
        """Test aligning components to right"""
        comp1 = TextFieldComponent("Test1")
        comp1.x = 100
        comp1.width = 100
        
        comp2 = TextFieldComponent("Test2")
        comp2.x = 200
        comp2.width = 100
        
        BulkOperations.align_right([comp1, comp2])
        
        # Rightmost edge is at 300
        assert comp1.x == 200  # 300 - 100
        assert comp2.x == 200  # 300 - 100
    
    def test_align_top(self):
        """Test aligning components to top"""
        comp1 = TextFieldComponent("Test1")
        comp1.y = 100
        
        comp2 = TextFieldComponent("Test2")
        comp2.y = 200
        
        BulkOperations.align_top([comp1, comp2])
        
        assert comp1.y == 100
        assert comp2.y == 100
    
    def test_align_bottom(self):
        """Test aligning components to bottom"""
        comp1 = TextFieldComponent("Test1")
        comp1.y = 100
        comp1.height = 50
        
        comp2 = TextFieldComponent("Test2")
        comp2.y = 200
        comp2.height = 50
        
        BulkOperations.align_bottom([comp1, comp2])
        
        # Bottommost edge is at 250
        assert comp1.y == 200  # 250 - 50
        assert comp2.y == 200  # 250 - 50
    
    def test_distribute_horizontal(self):
        """Test distributing components horizontally"""
        comp1 = TextFieldComponent("Test1")
        comp1.x = 0
        comp1.width = 50
        
        comp2 = TextFieldComponent("Test2")
        comp2.x = 100
        comp2.width = 50
        
        comp3 = TextFieldComponent("Test3")
        comp3.x = 200
        comp3.width = 50
        
        BulkOperations.distribute_horizontal([comp1, comp2, comp3])
        
        # Should evenly space them
        # (implementation detail - check spacing is uniform)
    
    def test_set_same_width(self):
        """Test setting same width for all components"""
        comp1 = TextFieldComponent("Test1")
        comp1.width = 100
        
        comp2 = TextFieldComponent("Test2")
        comp2.width = 200
        
        BulkOperations.set_same_width([comp1, comp2])
        
        assert comp1.width == 100
        assert comp2.width == 100
    
    def test_set_same_height(self):
        """Test setting same height for all components"""
        comp1 = TextFieldComponent("Test1")
        comp1.height = 50
        
        comp2 = TextFieldComponent("Test2")
        comp2.height = 100
        
        BulkOperations.set_same_height([comp1, comp2])
        
        assert comp1.height == 50
        assert comp2.height == 50
    
    def test_set_same_size(self):
        """Test setting same size for all components"""
        comp1 = TextFieldComponent("Test1")
        comp1.width = 100
        comp1.height = 50
        
        comp2 = TextFieldComponent("Test2")
        comp2.width = 200
        comp2.height = 100
        
        BulkOperations.set_same_size([comp1, comp2])
        
        assert comp1.width == 100
        assert comp1.height == 50
        assert comp2.width == 100
        assert comp2.height == 50
    
    def test_apply_property(self):
        """Test applying property to all components"""
        comp1 = TextFieldComponent("Test1")
        comp1.font_size = 12
        
        comp2 = TextFieldComponent("Test2")
        comp2.font_size = 14
        
        BulkOperations.apply_property([comp1, comp2], 'font_size', 16)
        
        assert comp1.font_size == 16
        assert comp2.font_size == 16
