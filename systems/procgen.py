"""
Procedural map generator using Cellular Automata (Conway's Game of Life rules).
Generates organic, cave-like structures.
"""
import random
import collections

class CellularAutomataGenerator:
    """
    Generates cave-like maps using cellular automata.
    """
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def generate(self, wall_prob=0.25, iterations=2):
        """
        Generate a boolean map where True = Wall, False = Floor.
        
        Args:
            wall_prob (float): Initial probability of a cell being a wall.
            iterations (int): Number of smoothing iterations.
            
        Returns:
            list[list[bool]]: Map grid.
        """
        # 1. Initialize random map
        map_grid = [[False for _ in range(self.height)] for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                # Edges are always walls
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    map_grid[x][y] = True
                else:
                    map_grid[x][y] = (random.random() < wall_prob)
                    
        # 2. Iterate smoothing (Cellular Automata rules)
        for _ in range(iterations):
            map_grid = self._smooth_map(map_grid)
            
        # 3. Ensure connectivity (fill isolated caves)
        map_grid, self.largest_region = self._connect_caves(map_grid)
        
        # 4. Add strategic pillar obstacles for difficulty
        map_grid = self._add_pillars(map_grid, count=max(3, self.width // 6))
        
        return map_grid
    
    def _add_pillars(self, map_grid, count=5):
        """Add small wall clusters (pillars) as interior obstacles."""
        placed = 0
        attempts = 0
        max_attempts = count * 20
        
        while placed < count and attempts < max_attempts:
            attempts += 1
            # Random position in middle region
            px = random.randint(3, self.width - 4)
            py = random.randint(3, self.height - 4)
            
            # Check if area is clear (floor)
            if not map_grid[px][py]:
                # Place a small pillar (1-2 tiles)
                map_grid[px][py] = True
                # Maybe add adjacent wall for variety
                if random.random() > 0.5:
                    direction = random.choice([(1,0), (0,1), (-1,0), (0,-1)])
                    nx, ny = px + direction[0], py + direction[1]
                    if 1 < nx < self.width - 2 and 1 < ny < self.height - 2:
                        map_grid[nx][ny] = True
                placed += 1
                
        return map_grid
    
    def _smooth_map(self, map_grid):
        """Apply smoothing rules."""
        new_map = [[False for _ in range(self.height)] for _ in range(self.width)]
        
        for x in range(self.width):
            for y in range(self.height):
                neighbor_wall_count = self._get_surrounding_wall_count(x, y, map_grid)
                
                # Rule: 4-5 Rule (Modified for caves)
                # If cell is alive (wall) (or dead), and has > 4 wall neighbors -> become wall
                if neighbor_wall_count > 4:
                    new_map[x][y] = True
                elif neighbor_wall_count < 4:
                    new_map[x][y] = False
                else:
                    new_map[x][y] = map_grid[x][y]  # Keep state
        
        return new_map
        
    def _get_surrounding_wall_count(self, x, y, map_grid):
        """Count wall neighbors in 3x3 area."""
        count = 0
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if nx == x and ny == y:
                    continue
                # Out of bounds counts as wall
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    count += 1
                elif map_grid[nx][ny]:
                    count += 1
        return count

    def _connect_caves(self, map_grid):
        """Identify regions and fill all but the largest one."""
        regions = self._get_regions(map_grid, False) # Get floor regions
        
        if not regions:
            return map_grid, []
            
        # Sort by size (largest first)
        regions.sort(key=len, reverse=True)
        
        # Keep largest region, fill others
        largest_region = regions[0]
        
        # Create final map: Walls everywhere unless it's in the largest region
        final_map = [[True for _ in range(self.height)] for _ in range(self.width)]
        
        for pos in largest_region:
            final_map[pos[0]][pos[1]] = False
            
        return final_map, largest_region
    
    def _get_regions(self, map_grid, tile_type):
        """Get list of regions (list of coords) of a specific tile type (True/False)."""
        regions = []
        visited = set()
        
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in visited and map_grid[x][y] == tile_type:
                    new_region = self._get_region_tiles(x, y, tile_type, map_grid)
                    regions.append(new_region)
                    for tile in new_region:
                        visited.add(tile)
                        
        return regions
        
    def _get_region_tiles(self, start_x, start_y, tile_type, map_grid):
        """Flood fill to find all tiles in this region."""
        tiles = []
        queue = collections.deque([(start_x, start_y)])
        visited = set([(start_x, start_y)])
        
        while queue:
            cx, cy = queue.popleft()
            tiles.append((cx, cy))
            
            neighbors = [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)
            ]
            
            for nx, ny in neighbors:
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited and map_grid[nx][ny] == tile_type:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
        return tiles
