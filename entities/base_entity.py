"""
Base entity class providing common functionality for all game entities.
Uses composition over inheritance where possible.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from entities.grid import Grid
    from systems.pathfinding import Pathfinding


@dataclass
class Position:
    """2D position component."""
    x: int | float = 0
    y: int | float = 0
    
    def distance_to(self, other: Position) -> float:
        """Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def as_tuple(self) -> tuple[int, int]:
        """Return position as integer tuple."""
        return (int(self.x), int(self.y))


@dataclass
class HealthComponent:
    """Health and damage tracking component."""
    max_health: int
    current: int = field(init=False)
    armor: int = 0
    
    def __post_init__(self):
        self.current = self.max_health
    
    @property
    def is_dead(self) -> bool:
        return self.current <= 0
    
    @property
    def health_percentage(self) -> float:
        return self.current / self.max_health if self.max_health > 0 else 0.0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage accounting for armor. Returns actual damage dealt."""
        actual_damage = max(1, damage - self.armor)
        self.current = max(0, self.current - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal by amount. Returns actual healing done."""
        old_health = self.current
        self.current = min(self.max_health, self.current + amount)
        return self.current - old_health


@dataclass
class MovementComponent:
    """Movement and pathfinding component."""
    speed: float  # Move interval in seconds (lower = faster)
    path: list[tuple[int, int]] = field(default_factory=list)
    move_timer: float = 0.0
    
    @property
    def move_interval(self) -> float:
        """Alias for speed to match existing code."""
        return self.speed
    
    def can_move(self) -> bool:
        """Check if enough time has passed to move."""
        return self.move_timer >= self.speed and len(self.path) > 0
    
    def update_timer(self, dt: float) -> None:
        """Update the movement timer."""
        self.move_timer += dt
    
    def reset_timer(self) -> None:
        """Reset timer after moving."""
        self.move_timer = 0.0
    
    def get_next_position(self) -> tuple[int, int] | None:
        """Get and remove next position from path."""
        if self.path:
            return self.path.pop(0)
        return None


class BaseEntity:
    """
    Base class for all game entities.
    
    Provides common functionality through composition:
    - Position tracking
    - Health/damage system
    - Movement/pathfinding
    
    Subclasses should override update() for entity-specific logic.
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        health: int = 1,
        armor: int = 0,
        speed: float = 0.5,
        asset_key: str = ""
    ):
        self.x = x
        self.y = y
        self._health = HealthComponent(max_health=health, armor=armor)
        self._movement = MovementComponent(speed=speed)
        self.asset_key = asset_key
        
        # State tracking
        self.state: str = "IDLE"
        self.damage_animation_timer: float = 0.0
    
    # Health properties (for backward compatibility)
    @property
    def health(self) -> int:
        return self._health.current
    
    @health.setter
    def health(self, value: int) -> None:
        self._health.current = max(0, min(self._health.max_health, value))
    
    @property
    def max_health(self) -> int:
        return self._health.max_health
    
    @property
    def is_dead(self) -> bool:
        return self._health.is_dead
    
    @is_dead.setter
    def is_dead(self, value: bool) -> None:
        if value:
            self._health.current = 0
    
    @property
    def armor(self) -> int:
        return self._health.armor
    
    # Movement properties (for backward compatibility)
    @property
    def path(self) -> list[tuple[int, int]]:
        return self._movement.path
    
    @path.setter
    def path(self, value: list[tuple[int, int]]) -> None:
        self._movement.path = value
    
    @property
    def move_timer(self) -> float:
        return self._movement.move_timer
    
    @move_timer.setter
    def move_timer(self, value: float) -> None:
        self._movement.move_timer = value
    
    @property
    def move_interval(self) -> float:
        return self._movement.move_interval
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage dealt."""
        dmg = self._health.take_damage(damage)
        if dmg > 0:
            self.damage_animation_timer = 0.15  # Flash white for 0.15s
        return dmg
    
    def move_step(self, dt: float) -> None:
        """Move one step along the path if timer allows."""
        self._movement.update_timer(dt)
        if self._movement.can_move():
            next_pos = self._movement.get_next_position()
            if next_pos:
                self.x, self.y = next_pos
                self._movement.reset_timer()
    
    def update(self, dt: float, *args, **kwargs) -> None:
        """Override in subclasses for entity-specific update logic."""
        if self.damage_animation_timer > 0:
            self.damage_animation_timer -= dt
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, health={self.health}/{self.max_health})"
