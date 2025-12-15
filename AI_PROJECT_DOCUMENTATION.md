# Solo Leveling AI Game - Technical Documentation

## Project Overview

**Solo Leveling: Monarch's Descent** is a strategy/stealth game that demonstrates core AI concepts including pathfinding algorithms, search algorithms, and finite state machines.

### Game Objective
- Infiltrate a grid-based dungeon
- Collect DATA nodes (resources)
- Avoid or eliminate enemies using AI-powered combat
- Reach the EXIT to advance levels

---

## AI Algorithms Implemented

### 1. A* Pathfinding Algorithm

**Location**: [pathfinding.py](systems/pathfinding.py) - `a_star()` method

**Purpose**: Enables enemies to find the optimal path to chase the player.

#### Algorithm Explanation

```
A* finds the shortest path by combining:
- g(n): Actual cost from start to current node
- h(n): Heuristic estimate from current to goal (Manhattan distance)
- f(n) = g(n) + h(n): Total estimated cost
```

#### Implementation Flow

```python
def a_star(start, goal, grid_obj):
    # 1. Initialize priority queue with start node
    frontier = []
    heapq.heappush(frontier, (0, start))  # (priority, node)
    
    # 2. Track visited nodes and costs
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    # 3. Main loop - explore nodes
    while frontier:
        _, current = heapq.heappop(frontier)  # Get lowest f(n)
        
        if current == goal:
            break  # Found the path!
        
        # 4. Explore neighbors (4-directional: up, down, left, right)
        for next_node in neighbors:
            new_cost = cost_so_far[current] + tile.cost
            
            # 5. Only explore if better path found
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(next_node, goal)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
    
    # 6. Reconstruct path by backtracking
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path
```

#### Heuristic Function (Manhattan Distance)

```python
def heuristic(a, b):
    """Manhattan distance - sum of absolute differences in x and y"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

**Why Manhattan?** Grid-based movement only allows 4 directions, making Manhattan distance the optimal heuristic (admissible and consistent).

#### Visual Representation in Game

- **Red path lines**: A* calculated path when enemy is HUNTING
- **Yellow path lines**: A* path during PATROL state
- **Numbered nodes**: Each step in the calculated path

---

### 2. Breadth-First Search (BFS)

**Location**: [pathfinding.py](systems/pathfinding.py) - `bfs_scan()` and `bfs_scan_layered()` methods

**Purpose**: Reveals fog of war tiles in expanding waves from player position.

#### Algorithm Explanation

```
BFS explores nodes layer by layer:
- Start at player position (distance 0)
- Explore all neighbors at distance 1
- Then all neighbors at distance 2
- Continue until radius limit reached
```

#### Implementation Flow

```python
def bfs_scan_layered(start_pos, grid_obj, radius=5):
    # 1. Initialize queue with starting position
    queue = deque([start_pos])
    visited = set([start_pos])
    distances = {start_pos: 0}
    
    # 2. Group tiles by distance for wave animation
    layers = [[] for _ in range(radius + 1)]
    layers[0].append(start_pos)
    
    # 3. Main BFS loop
    while queue:
        current = queue.popleft()  # FIFO - first in, first out
        current_dist = distances[current]
        
        if current_dist >= radius:
            continue  # Stop at radius limit
        
        # 4. Explore 4 neighbors
        for (nx, ny) in neighbors:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                new_dist = current_dist + 1
                distances[(nx, ny)] = new_dist
                queue.append((nx, ny))
                layers[new_dist].append((nx, ny))  # Group by layer
    
    return layers  # Returns tiles organized by BFS level
```

#### Visual Representation in Game

- **Cyan wave effect**: Tiles reveal layer-by-layer when pressing SPACE
- **"BFS SCAN - Layer X/Y"**: Shows current BFS expansion level
- **Animated expansion**: Demonstrates BFS exploring level by level

---

### 3. Finite State Machine (FSM)

**Location**: [enemy.py](entities/enemy.py) - `update()` method

**Purpose**: Controls enemy behavior transitions between states.

#### State Diagram

```
                    ┌──────────────┐
                    │    IDLE      │
                    │  (waiting)   │
                    └──────┬───────┘
                           │ patrol_points exist
                           ▼
┌──────────────┐    ┌──────────────┐
│   HUNTING    │◄───│   PATROL     │
│  (chasing)   │    │  (moving)    │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │ player leaves     │ player detected
       │ detection range   │ (dist < detection_range)
       │                   │
       └───────────────────┘
```

#### State Transitions in Code

```python
def update(self, dt, player, grid, pathfinding):
    # Calculate distance to player
    dist = abs(self.x - player.x) + abs(self.y - player.y)
    
    if dist < self.detection_range:
        # TRANSITION: Any state -> HUNTING
        if self.state != "HUNTING":
            self.state = "HUNTING"
        
        # Use A* to calculate path to player
        self.path = pathfinding.a_star(
            (self.x, self.y), 
            (player.x, player.y), 
            grid
        )
    else:
        # TRANSITION: HUNTING -> PATROL
        if self.state == "HUNTING":
            self.state = "PATROL"
            self.path = []
        
        # Continue patrol behavior
        self._update_patrol(grid, pathfinding)
```

#### States Explained

| State | Behavior | Visual Indicator |
|-------|----------|------------------|
| IDLE | No movement | Gray label |
| PATROL | Moves between waypoints | Yellow label, green dashed route |
| HUNTING | Chases player using A* | Red label, red path line |

---

## Game Architecture

### Project Structure

```
SoloLevelingAI/
├── main.py              # Entry point
├── game_engine.py       # Main game loop and state management
├── config/
│   ├── settings.py      # Game configuration
│   ├── constants.py     # Color constants
│   └── game_config.py   # Enemy/shadow/level configs
├── core/
│   ├── state_machine.py # Game state management (Menu, Playing, etc.)
│   ├── events.py        # Event system
│   └── logger.py        # Logging utilities
├── entities/
│   ├── player.py        # Player entity
│   ├── enemy.py         # Enemy with FSM and A* pathfinding
│   ├── shadow.py        # Shadow soldiers
│   ├── grid.py          # Game grid
│   └── tile.py          # Individual tile
├── systems/
│   ├── pathfinding.py   # A* and BFS implementations
│   ├── input_handler.py # Input processing
│   └── procgen.py       # Procedural map generation
├── rendering/
│   ├── renderer.py      # Isometric rendering + AI visualization
│   └── camera.py        # Camera system
├── states/
│   ├── playing_state.py # Main gameplay state
│   └── ...              # Other game states
└── ui/
    ├── hud.py           # Heads-up display
    └── ...              # Other UI components
```

### Game Flow

```
main.py
    └── GameEngine.__init__()
            ├── Initialize Pygame
            ├── Load assets
            ├── Create systems (pathfinding, camera, renderer)
            ├── Initialize first level
            └── Setup state machine
    
    └── GameEngine.run() [Main Loop]
            ├── handle_events() → Current state handles input
            ├── update(dt)
            │       ├── Player movement
            │       ├── BFS animation update
            │       ├── Enemy FSM update (→ A* pathfinding)
            │       ├── Combat checks
            │       └── Win/lose conditions
            └── render()
                    ├── Render tiles & entities
                    ├── Render AI paths
                    ├── Render BFS effects
                    └── Render AI stats panel
```

---

## AI Visualization Features

### 1. A* Path Visualization

**File**: [renderer.py](rendering/renderer.py) - `_render_enemy_paths()`

Shows real-time A* pathfinding:
- Red lines with arrow heads pointing toward player
- Node markers at each path step
- Updates every frame as player moves

### 2. BFS Wave Animation

**File**: [renderer.py](rendering/renderer.py) - `_render_bfs_glow()`, `update_bfs_animation()`

Animated fog reveal:
- Tiles reveal layer-by-layer (0.15s per layer)
- Cyan diamond glow on revealed tiles
- Label shows current layer count

### 3. Patrol Route Display

**File**: [renderer.py](rendering/renderer.py) - `_render_patrol_route()`

Enemy patrol visualization:
- Green dashed lines connecting waypoints
- Numbered markers (1, 2, 3...) showing route order
- Always visible to demonstrate constant AI behavior

### 4. AI Stats Panel

**File**: [renderer.py](rendering/renderer.py) - `render_ai_stats_panel()`

Real-time algorithm metrics:
- Enemies currently using A* tracking
- Enemies in patrol mode
- Total path nodes calculated
- Algorithm and heuristic names

---

## Key Code Sections

### Enemy Detection Logic

```python
# enemy.py - update() method
dist = abs(self.x - player.x) + abs(self.y - player.y)  # Manhattan distance

if dist < self.detection_range:
    self.state = "HUNTING"
    self.path = pathfinding.a_star(...)  # Calculate A* path
```

### Patrol Behavior

```python
# enemy.py - _update_patrol() method
def _update_patrol(self, grid, pathfinding):
    # Check if reached current waypoint
    if (self.x, self.y) == patrol_points[current_index]:
        # Move to next waypoint (circular)
        self.current_patrol_index = (index + 1) % len(patrol_points)
    
    # Calculate A* path to next waypoint
    self.path = pathfinding.a_star(current_pos, target_waypoint, grid)
```

### Movement Execution

```python
# base_entity.py - move_step() method
def move_step(self, dt):
    if self.path:
        self.move_timer += dt
        if self.move_timer >= self.speed:
            self.move_timer = 0
            next_pos = self.path.pop(0)
            self.x, self.y = next_pos
```

---

## Algorithm Complexity Analysis

| Algorithm | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| A* | O(b^d) where b=branching factor, d=depth | O(b^d) |
| BFS | O(V + E) where V=vertices, E=edges | O(V) |
| FSM | O(1) per update | O(1) |

**Practical Performance**:
- A* with Manhattan heuristic is optimal for grid-based pathfinding
- BFS guarantees shortest path in unweighted graphs
- FSM provides constant-time state transitions

---

## Controls Reference

| Key | Action |
|-----|--------|
| WASD/Arrows | Move player |
| SPACE | BFS Scan (reveal fog) |
| Q | Melee attack |
| Right-Click | Ranged attack |
| R | Summon shadow menu |
| T | Trap menu |
| B | Build wall |
| ESC | Pause |

---

## Conclusion

This project demonstrates practical AI concepts:

1. **A\* Pathfinding**: Optimal path finding with heuristic-guided search
2. **BFS**: Systematic exploration for fog of war revelation
3. **FSM**: Structured behavior management for game entities

The visual representations make these algorithms tangible and understandable, perfect for demonstrating AI concepts in an interactive environment.
