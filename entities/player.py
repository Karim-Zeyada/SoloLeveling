"""
Player entity with movement and resource management.
Refactored with type hints and logging.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    from entities.grid import Grid

# Module logger
logger = get_logger('player')


class Player:
    """Main player character with smooth movement interpolation."""
    
    def __init__(self, x: int, y: int) -> None:
        self.x: int | float = x
        self.y: int | float = y
        self.resources: int = 10  # Starting 'Data'
        
        # Combat stats (Hell Mode)
        self.health: int = 100
        self.max_health: int = 100
        self.damage: int = 25
        
        # Movement interpolation state (for smooth movement)
        self.moving: bool = False
        self.move_start: tuple[int | float, int | float] = (x, y)
        self.move_target: tuple[int | float, int | float] = (x, y)
        self.move_progress: float = 0.0
        self.move_duration: float = 0.12  # seconds per tile
        self.path: list[tuple[int, int]] = []
    
    def move(self, dx: int, dy: int, grid: 'Grid') -> bool:
        """
        Move player by delta coordinates.
        
        Args:
            dx: X direction (-1, 0, or 1)
            dy: Y direction (-1, 0, or 1)
            grid: Game grid to check bounds and tiles
            
        Returns:
            True if movement started, False otherwise
        """
        new_x = int(self.x) + dx
        new_y = int(self.y) + dy
        
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            tile = grid.get_tile(new_x, new_y)
            if tile and tile.type != 'wall':
                # Start interpolated movement rather than teleport
                if not self.moving:
                    self.moving = True
                    self.move_start = (self.x, self.y)
                    self.move_target = (new_x, new_y)
                    self.move_progress = 0.0
                    return True
        return False
    
    def update(self, dt: float, grid: 'Grid') -> None:
        """
        Update player state (movement interpolation).
        
        Args:
            dt: Delta time since last update
            grid: Game grid for tile interactions
        """
        # Advance movement interpolation
        if self.moving:
            self.move_progress += dt / max(self.move_duration, 1e-6)
            if self.move_progress >= 1.0:
                # Finish movement
                self.x, self.y = self.move_target
                self.moving = False
                
                # Interact with tile after movement
                tile = grid.get_tile(int(self.x), int(self.y))
                if tile:
                    if tile.type == 'resource':
                        tile.type = 'floor'
                        self.resources += 10
                        logger.info("Data Collected! Resources: %d", self.resources)
                    elif tile.type == 'exit':
                        logger.info("LEVEL COMPLETE - UPLOAD SUCCESSFUL")
    
    def start_move_to(self, tx: int, ty: int, grid: 'Grid') -> bool:
        """
        Start movement to target tile coordinates.
        
        Args:
            tx: Target X coordinate
            ty: Target Y coordinate
            grid: Game grid to validate movement
            
        Returns:
            True if movement started, False otherwise
        """
        if 0 <= tx < grid.width and 0 <= ty < grid.height:
            tile = grid.get_tile(tx, ty)
            if tile and tile.type != 'wall':
                if not self.moving:
                    self.moving = True
                    self.move_start = (self.x, self.y)
                    self.move_target = (tx, ty)
                    self.move_progress = 0.0
                    return True
        return False
    
    def __repr__(self) -> str:
        return f"Player(x={self.x}, y={self.y}, resources={self.resources})"
