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
        
        # Combat logic
        self.attack_cooldown: float = 0.0
        self.damage_animation_timer: float = 0.0
        
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
        
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage dealt."""
        self.health -= damage
        if self.health < 0:
            self.health = 0
            
        # Trigger damage flash
        self.damage_animation_timer = 0.15
        
        return damage
    
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
            if tile and tile.type != 'wall' and tile.visible:
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
        
        # Cooldown management
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Animation timer
        if self.damage_animation_timer > 0:
            self.damage_animation_timer -= dt
            
    def attack(self, enemies: list) -> list:
        """
        Perform melee attack on adjacent enemies.
        
        Args:
            enemies: List of active enemies
            
        Returns:
            List of enemies hit
        """
        if self.attack_cooldown > 0:
            return []
            
        self.attack_cooldown = 0.5
        hit_enemies = []
        
        for enemy in enemies:
            # Check distance (adjacent or diagonal = ~1.414)
            dist = ((self.x - enemy.x)**2 + (self.y - enemy.y)**2)**0.5
            if dist <= 1.5:
                enemy.take_damage(self.damage)
                hit_enemies.append(enemy)
                
        return hit_enemies
        
    def skill_dagger_throw(self, target_pos: tuple[int, int], enemies: list):
        """
        Perform ranged dagger throw at target position.
        
        Args:
            target_pos: Tuple (x, y) of target tile
            enemies: List of active enemies
            
        Returns:
            Enemy hit or None
        """
        if self.attack_cooldown > 0:
            return None
            
        self.attack_cooldown = 1.0
        
        tx, ty = target_pos
        
        for enemy in enemies:
            # Check distance to target tile (relaxed hit detection)
            dist_to_target = ((enemy.x - tx)**2 + (enemy.y - ty)**2)**0.5
            
            # Revised logic:
            # 1. Check if enemy is close to target_pos (hit radius)
            # 2. Check if enemy is within range of player
            
            if dist_to_target < 1.0:
                 # Range check (max 4.5 tiles)
                dist_p = ((self.x - enemy.x)**2 + (self.y - enemy.y)**2)**0.5
                if dist_p <= 4.5:  # Slightly increased range
                    damage = self.damage * 2  # Double damage skill
                    enemy.take_damage(damage)
                    return enemy
                    
        return None
    
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
