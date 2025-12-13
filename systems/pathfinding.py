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
    def a_star(start, goal, grid_obj, ignore_fog=True):
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
                        
                    # Logic: Cannot walk through fog if not ignoring it
                    if not ignore_fog and not tile.visible:
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
