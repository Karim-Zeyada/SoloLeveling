"""
Pathfinding algorithms for entity movement.
Includes A* and BFS for fog of war scanning.
"""
import heapq
import collections

class Pathfinding:
    """Utility class for pathfinding algorithms."""
    
    @staticmethod
    def bfs_scan(start_pos, grid_obj, radius=4):
        """
        Breadth-first search to reveal tiles within radius.
        Returns a list of tile coordinates to reveal.
        """
        queue = collections.deque([start_pos])
        visited = set([start_pos])
        revealed_tiles = []
        
        # Track distance to limit radius
        distances = {start_pos: 0}
        
        while queue:
            current = queue.popleft()
            revealed_tiles.append(current)
            
            if distances[current] >= radius:
                continue
            
            cx, cy = current
            neighbors = [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)
            ]
            
            for nx, ny in neighbors:
                if 0 <= nx < grid_obj.width and 0 <= ny < grid_obj.height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        distances[(nx, ny)] = distances[current] + 1
                        queue.append((nx, ny))
        return revealed_tiles
    
    @staticmethod
    def bfs_scan_layered(start_pos, grid_obj, radius=5):
        """
        BFS scan that returns tiles grouped by distance (layers).
        Used for animated wave visualization of BFS algorithm.
        
        Returns:
            list[list[tuple]]: List of layers, each containing tiles at that distance
        """
        queue = collections.deque([start_pos])
        visited = set([start_pos])
        distances = {start_pos: 0}
        
        # Group tiles by distance
        layers = [[] for _ in range(radius + 1)]
        layers[0].append(start_pos)
        
        while queue:
            current = queue.popleft()
            current_dist = distances[current]
            
            if current_dist >= radius:
                continue
            
            cx, cy = current
            neighbors = [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)
            ]
            
            for nx, ny in neighbors:
                if 0 <= nx < grid_obj.width and 0 <= ny < grid_obj.height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        new_dist = current_dist + 1
                        distances[(nx, ny)] = new_dist
                        queue.append((nx, ny))
                        if new_dist <= radius:
                            layers[new_dist].append((nx, ny))
        
        return layers
    
    @staticmethod
    def a_star(start, goal, grid_obj):
        """
        A* pathfinding algorithm.
        Returns path from start to goal as list of coordinates.
        """
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                break
            
            cx, cy = current
            neighbors = [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)
            ]
            
            for next_node in neighbors:
                nx, ny = next_node
                # Check bounds
                if 0 <= nx < grid_obj.width and 0 <= ny < grid_obj.height:
                    tile = grid_obj.get_tile(nx, ny)
                    
                    # Logic: Cannot walk through walls
                    if tile.type == 'wall':
                        continue
                        
                    new_cost = cost_so_far[current] + tile.cost
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + Pathfinding.heuristic(next_node, goal)
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current
        
        # Reconstruct path
        path = []
        if goal in came_from:
            cur = goal
            while cur != start:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
        return path
    
    @staticmethod
    def heuristic(a, b):
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
