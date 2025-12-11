"""
Tile entity for the game grid.
Enhanced with trap mechanics.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from entities.enemy import Enemy
    from entities.shadow import Shadow


from config.settings import TRAP_TYPES

@dataclass
class TrapConfig:
    """Configuration for trap behavior."""
    COOLDOWN: float = 1.0  # seconds between triggers


class Tile:
    """Represents a single tile in the game grid."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type: str = 'floor'  # floor, wall, trap, resource, exit
        self.cost: int = 1  # Movement cost for pathfinding
        self.visible: bool = False  # Fog of War visibility
        
        # Trap state
        self.trap_type: str | None = None
        self.trap_cooldown: float = 0.0
        self.trap_triggered: bool = False
    
    def update(self, dt: float) -> None:
        """Update tile state."""
        if self.trap_cooldown > 0:
            self.trap_cooldown -= dt
            if self.trap_cooldown <= 0:
                self.trap_triggered = False
    
    def trigger_trap(self, entity: 'Enemy | Shadow') -> dict | None:
        """
        Trigger trap on an entity.
        
        Args:
            entity: The entity that stepped on the trap
            
        Returns:
            Effect dict or None if no trigger
        """
        if self.type != 'trap':
            return None
        
        if self.trap_cooldown > 0:
            return None
        
        # Default to spike if no type set (backward compatibility)
        trap_key = self.trap_type if self.trap_type else 'trap_spike'
        trap_data = TRAP_TYPES.get(trap_key, TRAP_TYPES['trap_spike'])
        
        # Trigger the trap
        self.trap_triggered = True
        self.trap_cooldown = TrapConfig.COOLDOWN
        
        # Apply immediate damage if any
        if trap_data['damage'] > 0:
            entity.take_damage(trap_data['damage'])
            
        return trap_data
    
    def __repr__(self) -> str:
        return f"Tile({self.x}, {self.y}, type={self.type})"
