"""
Protocol definitions for type safety and interface contracts.
Uses Python's Protocol (structural subtyping) for duck typing with type hints.
"""
from typing import Protocol, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class Positionable(Protocol):
    """Entity that has a position on the grid."""
    x: int | float
    y: int | float


@runtime_checkable
class Damageable(Protocol):
    """Entity that can take damage and die."""
    health: int
    max_health: int
    is_dead: bool
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage dealt."""
        ...


@runtime_checkable
class Movable(Protocol):
    """Entity that can move on the grid."""
    path: list[tuple[int, int]]
    move_timer: float
    move_interval: float
    
    def move_step(self, dt: float) -> None:
        """Move one step along the path."""
        ...


@runtime_checkable
class Renderable(Protocol):
    """Entity that can be rendered with an asset."""
    asset_key: str


@runtime_checkable
class Updatable(Protocol):
    """Entity that updates each frame."""
    
    @abstractmethod
    def update(self, dt: float, *args, **kwargs) -> None:
        """Update entity state."""
        ...
