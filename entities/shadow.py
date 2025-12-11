"""
Shadow companion entity with AI and combat capabilities.
Refactored to use BaseEntity for common functionality.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from .base_entity import BaseEntity
from config.game_config import get_shadow_config

if TYPE_CHECKING:
    from .player import Player
    from .enemy import Enemy
    from .grid import Grid
    from systems.pathfinding import Pathfinding


class Shadow(BaseEntity):
    """
    Shadow companion with type-based configuration.
    
    Inherits from BaseEntity which provides:
    - Health/damage system
    - Movement with pathfinding  
    - Position tracking
    """
    
    def __init__(self, x: int, y: int, shadow_type: str = 'shadow'):
        # Get type-specific configuration (dataclass)
        config = get_shadow_config(shadow_type)
        
        # Initialize base entity with config values
        super().__init__(
            x=x,
            y=y,
            health=config.health,
            armor=0,  # Shadows don't have armor by default
            speed=config.speed,
            asset_key=config.asset
        )
        
        # Shadow-specific attributes
        self.shadow_type = shadow_type
        self.type_name = config.name
        self.cost = config.cost
        self.damage = config.damage
        
        # Combat state
        self.target_enemy: Enemy | None = None
        self.combat_cooldown = 0.0
        self.damage_animation_timer = 0.0
    
    def take_damage(self, damage: int) -> bool:
        """
        Take damage and trigger animation.
        Returns True if the shadow died.
        """
        super().take_damage(damage)
        self.damage_animation_timer = 0.2  # Show damage for 0.2 seconds
        return self.is_dead
    
    def attack_enemy(self, enemy: Enemy) -> bool:
        """
        Attack an enemy at the same location.
        Returns True if damage was dealt.
        """
        if self.is_dead:
            return False
        if self.x != enemy.x or self.y != enemy.y:
            return False
        
        damage_dealt = enemy.take_damage(self.damage)
        self.combat_cooldown = 0.3  # Attack cooldown
        return damage_dealt > 0
    
    def update(
        self, 
        dt: float, 
        player: Player, 
        enemies: list[Enemy], 
        grid: Grid, 
        pathfinding: Pathfinding
    ) -> None:
        """Update shadow behavior based on state."""
        if self.is_dead:
            return
        
        # Update timers
        self._movement.update_timer(dt)
        self.combat_cooldown = max(0, self.combat_cooldown - dt)
        self.damage_animation_timer = max(0, self.damage_animation_timer - dt)
        
        if self.state == "IDLE":
            self._update_idle_state(player, pathfinding, grid)
        elif self.state == "ATTACK":
            self._update_attack_state(enemies, pathfinding, grid)
        
        # Move along path if timer ready
        if self._movement.can_move():
            next_pos = self._movement.get_next_position()
            if next_pos:
                self.x, self.y = next_pos
                self._movement.reset_timer()
    
    def _update_idle_state(
        self, 
        player: Player, 
        pathfinding: Pathfinding, 
        grid: Grid
    ) -> None:
        """Follow player, stay within 2 tiles."""
        dist_to_player = abs(self.x - player.x) + abs(self.y - player.y)
        if dist_to_player > 2:
            self.path = pathfinding.a_star(
                (self.x, self.y), 
                (int(player.x), int(player.y)), 
                grid
            )
    
    def _update_attack_state(
        self, 
        enemies: list[Enemy], 
        pathfinding: Pathfinding, 
        grid: Grid
    ) -> None:
        """Hunt closest enemy."""
        alive_enemies = [e for e in enemies if not e.is_dead]
        
        if not alive_enemies:
            self.state = "IDLE"
            self.path = []
            self.target_enemy = None
            return
        
        # Find closest alive enemy
        self.target_enemy = min(
            alive_enemies, 
            key=lambda e: abs(self.x - e.x) + abs(self.y - e.y)
        )
        
        dist_to_target = abs(self.x - self.target_enemy.x) + abs(self.y - self.target_enemy.y)
        
        if dist_to_target <= 1 and self.combat_cooldown <= 0:
            # Adjacent to enemy - attack
            self.attack_enemy(self.target_enemy)
        elif self.combat_cooldown <= 0:
            # Move toward enemy
            self.path = pathfinding.a_star(
                (self.x, self.y), 
                (self.target_enemy.x, self.target_enemy.y), 
                grid
            )
