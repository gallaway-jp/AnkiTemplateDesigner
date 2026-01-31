"""Grid and snap helpers for component positioning."""

from typing import Tuple, Optional


class GridSettings:
    """Configuration for grid snapping."""
    
    def __init__(self, grid_size: float = 10.0, snap_enabled: bool = True):
        self.grid_size = grid_size
        self.snap_enabled = snap_enabled


class SnapHelper:
    """Utilities for snapping components to grid."""
    
    def __init__(self, grid_settings: GridSettings):
        self.settings = grid_settings
    
    def snap_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Snap coordinates to grid."""
        if not self.settings.snap_enabled:
            return (x, y)
        
        grid = self.settings.grid_size
        snapped_x = round(x / grid) * grid
        snapped_y = round(y / grid) * grid
        return (snapped_x, snapped_y)


class Grid:
    """Grid management for layout."""
    
    def __init__(self, width: float = 100.0, height: float = 100.0, grid_size: float = 10.0):
        self.width = width
        self.height = height
        self.settings = GridSettings(grid_size=grid_size)
        self.snap_helper = SnapHelper(self.settings)
    
    def snap_position(self, x: float, y: float) -> Tuple[float, float]:
        """Snap a position to grid."""
        return self.snap_helper.snap_to_grid(x, y)


__all__ = ['Grid', 'GridSettings', 'SnapHelper']
