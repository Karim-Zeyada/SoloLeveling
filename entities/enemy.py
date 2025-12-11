"""
Enemy entity with AI and combat capabilities.
Refactored to use BaseEntity for common functionality.
Enhanced with patrol routes.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import random

from .base_entity import BaseEntity
from config.game_config import get_enemy_config
from core.logger import get_logger

if TYPE_CHECKING:
    from .player import Player
    from .grid import Grid
    from systems.pathfinding import Pathfinding

logger = get_logger('enemy')


class Enemy(BaseEntity):
    """
    Enemy entity with type-based configuration.
    
    Inherits from BaseEntity which provides:
    - Health/damage system with armor
    - Movement with pathfinding
    - Position tracking
    
    States:
    - IDLE: Waiting at current position
    - PATROL: Moving between patrol points
    - HUNTING: Chasing the player
    """
    
    def __init__(self, x: int, y: int, enemy_type: str = 'security_agent'):
        # Get type-specific configuration (dataclass)
        config = get_enemy_config(enemy_type)
        
        # Initialize base entity with config values
        super().__init__(
            x=x,
            y=y,
            health=config.health,
            armor=config.armor,
            speed=config.speed,
            asset_key=config.asset
        )
        
        # Enemy-specific attributes
        self.enemy_type = enemy_type
        self.type_name = config.name
        self.damage = config.damage
        self.detection_range = config.detection_range
        
        # Combat state
        self.caught_player = False
        self.combat_timer = 0.0
        
        # Patrol state
        self.patrol_points: list[tuple[int, int]] = []
        self.current_patrol_index: int = 0
        self.patrol_wait_timer: float = 0.0
        self.patrol_wait_duration: float = 1.5  # Wait at each patrol point
        self.home_position: tuple[int, int] = (x, y)
        
        # Status effects
        self.frozen_timer: float = 0.0
        self.slow_timer: float = 0.0
        self.slow_factor: float = 1.0
        
        # Generate initial patrol route
        self._generate_patrol_route()

    def apply_effect(self, effect_type: str, duration: float) -> None:
        """Apply status effect to enemy."""
        if effect_type == 'freeze':
            self.frozen_timer = duration
            # Reset path when frozen to force re-evaluation after thaw
            self.path = []
        elif effect_type == 'slow':
            self.slow_timer = duration
            self.slow_factor = 0.5  # 50% slow
    
    def _generate_patrol_route(self) -> None:
        """Generate random patrol points around home position."""
        self.patrol_points = [self.home_position]
        
        # Generate 2-3 random patrol points nearby
        num_points = random.randint(2, 3)
        for _ in range(num_points):
            # Patrol within 3-5 tiles of home
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            patrol_x = self.home_position[0] + offset_x
            patrol_y = self.home_position[1] + offset_y
            
            # Ensure it's not the same point
            if (patrol_x, patrol_y) not in self.patrol_points:
                self.patrol_points.append((patrol_x, patrol_y))
    
    def update(self, player: 'Player', grid: 'Grid', pathfinding: 'Pathfinding') -> None:
        """Update enemy AI and movement."""
        if self.is_dead:
            return
        
        # Update status effects (timers decrease even if not moving logic yet)
        # But we do it in move_step or here? Usually update loop controls time.
        # Let's handle timers here if they are not movement related, but freeze stops movement.
        
        # We will handle timers in move_step where dt is passed often, or expected to be passed.
        # Wait, update receives dt? No, it receives player, grid, pathfinding.
        # move_step receives dt.
        pass

        # Manhattan distance check for detection
        dist = abs(self.x - player.x) + abs(self.y - player.y)
        
        if dist < self.detection_range:
            # Player detected - hunt them!
            self.state = "HUNTING"
            # Logic check: if frozen, maybe don't calculate path? 
            # Actually, we can calculate, but just not move.
            
            # Only recalculate path if not frozen to save perf? 
            # Or just let it be.
            self.path = pathfinding.a_star(
                (self.x, self.y), 
                (int(player.x), int(player.y)), 
                grid
            )
        else:
            # No player nearby - patrol
            if self.state == "HUNTING":
                # Just lost the player, return to patrol
                self.state = "PATROL"
                self.path = []
            
            self._update_patrol(grid, pathfinding)
    
    def _update_patrol(self, grid: 'Grid', pathfinding: 'Pathfinding') -> None:
        """Update patrol behavior."""
        if not self.patrol_points:
            self.state = "IDLE"
            return
        
        self.state = "PATROL"
        
        # Check if we've reached current patrol point
        current_target = self.patrol_points[self.current_patrol_index]
        if self.x == current_target[0] and self.y == current_target[1]:
            # At patrol point - wait a bit
            if self.patrol_wait_timer > 0:
                return  # Still waiting
            
            # Move to next patrol point
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.patrol_wait_timer = self.patrol_wait_duration
        
        # Generate path to current patrol point if needed
        if not self.path:
            target = self.patrol_points[self.current_patrol_index]
            # Validate target is in bounds
            if 0 <= target[0] < grid.width and 0 <= target[1] < grid.height:
                tile = grid.get_tile(target[0], target[1])
                if tile and tile.type != 'wall':
                    self.path = pathfinding.a_star(
                        (self.x, self.y),
                        target,
                        grid
                    )
    
    def move_step(self, dt: float) -> None:
        """Move one step along the path."""
        # Update status timers
        if self.frozen_timer > 0:
            self.frozen_timer -= dt
            return  # frozen = no movement
            
        if self.slow_timer > 0:
            self.slow_timer -= dt
            current_dt = dt * self.slow_factor
        else:
            current_dt = dt
            
        # Update patrol wait timer
        if self.patrol_wait_timer > 0:
            self.patrol_wait_timer -= current_dt
        
        # Call parent move step with potentially modified dt (for slow)
        # Note: BaseEntity.move_step uses self.speed to determine IF it should move.
        # It accumulates self.move_timer += dt.
        # So passing smaller dt makes it move slower. Correct.
        super().move_step(current_dt)
    
    def check_caught_player(self, player: 'Player') -> bool:
        """Check if enemy has caught the player."""
        if self.is_dead:
            return False
        # If frozen, cannot catch? Maybe logically yes.
        if self.frozen_timer > 0:
            return False
            
        return int(player.x) == self.x and int(player.y) == self.y
