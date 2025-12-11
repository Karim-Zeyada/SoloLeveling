"""
Entity factory for creating game entities.
Centralizes entity creation logic and configuration lookup.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from config.game_config import (
    get_enemy_config, 
    get_shadow_config, 
    get_level_config,
    LevelConfig
)

if TYPE_CHECKING:
    from entities.enemy import Enemy
    from entities.shadow import Shadow
    from entities.player import Player
    from entities.grid import Grid


class EntityFactory:
    """
    Factory for creating game entities.
    
    Benefits:
    - Centralized creation logic
    - Easy to mock for testing
    - Configuration lookup in one place
    """
    
    @staticmethod
    def create_enemy(x: int, y: int, enemy_type: str = 'security_agent') -> 'Enemy':
        """
        Create an enemy at the specified position.
        
        Args:
            x: Grid x position
            y: Grid y position
            enemy_type: Type of enemy (security_agent, elf, alpha_bear)
            
        Returns:
            Configured Enemy instance
        """
        from entities.enemy import Enemy
        return Enemy(x, y, enemy_type=enemy_type)
    
    @staticmethod
    def create_shadow(x: int, y: int, shadow_type: str = 'shadow') -> 'Shadow':
        """
        Create a shadow at the specified position.
        
        Args:
            x: Grid x position
            y: Grid y position
            shadow_type: Type of shadow (shadow, igris, beru)
            
        Returns:
            Configured Shadow instance
        """
        from entities.shadow import Shadow
        return Shadow(x, y, shadow_type=shadow_type)
    
    @staticmethod
    def create_player(x: int, y: int, resources: int = 10) -> 'Player':
        """
        Create a player at the specified position.
        
        Args:
            x: Grid x position
            y: Grid y position
            resources: Starting resources
            
        Returns:
            Configured Player instance
        """
        from entities.player import Player
        player = Player(x, y)
        player.resources = resources
        return player
    
    @staticmethod
    def create_grid(width: int, height: int, level: int = 1) -> 'Grid':
        """
        Create a game grid.
        
        Args:
            width: Grid width
            height: Grid height
            level: Current level number
            
        Returns:
            Configured Grid instance
        """
        from entities.grid import Grid
        return Grid(width, height, level=level)
    
    @staticmethod
    def create_enemies_for_level(level_config: LevelConfig, grid_width: int, grid_height: int) -> list['Enemy']:
        """
        Create all enemies for a level based on configuration.
        
        Args:
            level_config: Level configuration with enemy definitions
            grid_width: Width of the grid
            grid_height: Height of the grid
            
        Returns:
            List of Enemy instances positioned on the grid
        """
        from entities.enemy import Enemy
        
        enemies = []
        enemy_index = 0
        
        for enemy_type, count in level_config.enemies:
            for _ in range(count):
                # Position enemies in the far corner, spread out
                ex = grid_width - 3 - enemy_index * 2
                ey = grid_height - 3 - enemy_index * 2
                enemy = Enemy(ex, ey, enemy_type=enemy_type)
                enemies.append(enemy)
                enemy_index += 1
        
        return enemies
