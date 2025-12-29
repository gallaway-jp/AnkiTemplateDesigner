"""
Tests for grid and snap-to-grid functionality.
"""

import pytest
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from ui.grid import Grid, GridSettings, SnapHelper


# Initialize QApplication for tests
app = QApplication.instance() or QApplication([])


class TestGrid:
    """Test Grid"""
    
    def test_grid_initialization(self):
        """Test grid initialization"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        
        assert grid.grid_size == GridSettings.DEFAULT_GRID_SIZE
        assert not grid.enabled
        assert not grid.visible
    
    def test_set_grid_size(self):
        """Test setting grid size"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        
        grid.set_grid_size(20)
        
        assert grid.grid_size == 20
    
    def test_toggle_visibility(self):
        """Test toggling grid visibility"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        
        assert not grid.visible
        
        grid.toggle_visibility()
        assert grid.visible
        
        grid.toggle_visibility()
        assert not grid.visible
    
    def test_toggle_snap(self):
        """Test toggling snap-to-grid"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        
        assert not grid.enabled
        
        result = grid.toggle_snap()
        assert result is True
        assert grid.enabled
        
        result = grid.toggle_snap()
        assert result is False
        assert not grid.enabled
    
    def test_snap_to_grid(self):
        """Test snapping coordinates to grid"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        grid.enable_snap()
        
        # Test exact grid point
        x, y = grid.snap_to_grid(50, 50)
        assert x == 50
        assert y == 50
        
        # Test rounding down
        x, y = grid.snap_to_grid(54, 54)
        assert x == 50
        assert y == 50
        
        # Test rounding up
        x, y = grid.snap_to_grid(56, 56)
        assert x == 60
        assert y == 60
    
    def test_snap_disabled(self):
        """Test that snap is disabled when not enabled"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        grid.disable_snap()
        
        # Should return original coordinates
        x, y = grid.snap_to_grid(54.3, 54.7)
        assert x == 54.3
        assert y == 54.7
    
    def test_snap_point(self):
        """Test snapping QPointF to grid"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        grid.enable_snap()
        
        point = QPointF(54, 56)
        snapped = grid.snap_point(point)
        
        assert snapped.x() == 50
        assert snapped.y() == 60
    
    def test_snap_rect(self):
        """Test snapping QRectF to grid"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        grid.enable_snap()
        
        rect = QRectF(54, 56, 104, 106)
        snapped = grid.snap_rect(rect)
        
        assert snapped.x() == 50
        assert snapped.y() == 60
        assert snapped.width() == 100
        assert snapped.height() == 110


class TestGridSettings:
    """Test GridSettings"""
    
    def test_grid_sizes(self):
        """Test grid size constants"""
        assert GridSettings.GRID_SIZE_SMALL == 5
        assert GridSettings.GRID_SIZE_MEDIUM == 10
        assert GridSettings.GRID_SIZE_LARGE == 20
    
    def test_default_grid_size(self):
        """Test default grid size"""
        assert GridSettings.DEFAULT_GRID_SIZE == GridSettings.GRID_SIZE_MEDIUM
    
    def test_grid_styles(self):
        """Test grid style constants"""
        assert GridSettings.GRID_STYLE_DOTS == 'dots'
        assert GridSettings.GRID_STYLE_LINES == 'lines'
        assert GridSettings.GRID_STYLE_CROSS == 'cross'


class TestSnapHelper:
    """Test SnapHelper"""
    
    def test_snap_helper_initialization(self):
        """Test snap helper initialization"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        
        helper = SnapHelper(grid)
        
        assert helper.grid == grid
        assert helper.snap_threshold == 5
    
    def test_snap_to_grid_only(self):
        """Test snapping to grid only"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.grid_size = 10
        grid.enable_snap()
        
        helper = SnapHelper(grid)
        
        x, y = helper.snap_component_position(54, 56)
        
        assert x == 50
        assert y == 60
    
    def test_snap_without_grid(self):
        """Test snapping when grid is disabled"""
        scene = QGraphicsScene()
        grid = Grid(scene)
        grid.disable_snap()
        
        helper = SnapHelper(grid)
        
        x, y = helper.snap_component_position(54.3, 56.7)
        
        assert x == 54.3
        assert y == 56.7
