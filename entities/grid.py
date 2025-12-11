"""
Grid entity managing the game level layout.
"""
import random
from .tile import Tile

class Grid:
    """Game level grid with procedural generation."""
    
    def __init__(self, width, height, level=1):
        self.width = width
        self.height = height
        self.level = level
        self.tiles = [[Tile(x, y) for y in range(height)] for x in range(width)]
        self.generate_level()
    
    def generate_level(self):
        """Generate level layout with obstacles, resources, and exit."""
        # Add some random walls for obstacle variety
        num_walls = max(3, self.width // 4)
        for _ in range(num_walls):
            wx = random.randint(1, self.width - 2)
            wy = random.randint(1, self.height - 2)
            self.get_tile(wx, wy).type = 'wall'
    
    def get_tile(self, x, y):
        """Get tile at coordinates, returns None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return None
    
    def place_resources(self, count):
        """Place resources randomly on the grid."""
        placed = 0
        while placed < count:
            rx = random.randint(3, self.width - 3)
            ry = random.randint(3, self.height - 3)
            tile = self.get_tile(rx, ry)
            if tile and tile.type == 'floor':
                tile.type = 'resource'
                placed += 1
    
    def place_exit(self):
        """Place exit in far corner."""
        ex = self.width - 3
        ey = self.height - 3
        self.get_tile(ex, ey).type = 'exit'
