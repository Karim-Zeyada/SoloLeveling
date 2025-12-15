"""
Floating damage numbers and combat effects.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import pygame


@dataclass
class DamageNumber:
    """A floating damage number that fades and rises."""
    x: float
    y: float
    amount: int | str
    color: tuple[int, int, int]
    lifetime: float = 1.0
    age: float = 0.0
    rise_speed: float = 50.0  # pixels per second
    
    @property
    def is_expired(self) -> bool:
        return self.age >= self.lifetime
    
    @property
    def alpha(self) -> int:
        """Calculate alpha based on age."""
        remaining = 1.0 - (self.age / self.lifetime)
        return int(255 * remaining)


class DamageNumberManager:
    """
    Manages floating damage numbers on screen.
    
    Usage:
        manager = DamageNumberManager()
        manager.add(world_x, world_y, amount=5, color=(255, 0, 0))
        manager.update(dt)
        manager.render(screen, camera, world_offset)
    """
    
    def __init__(self):
        self.numbers: list[DamageNumber] = []
        self.font: pygame.font.Font | None = None
    
    def _ensure_font(self) -> None:
        """Initialize font if needed."""
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
    
    def add(
        self, 
        x: float, 
        y: float, 
        amount: int | str, 
        color: tuple[int, int, int] = (255, 100, 100),
        is_crit: bool = False
    ) -> None:
        """Add a damage number or text at world position."""
        num = DamageNumber(x=x, y=y, amount=amount, color=color)
        if is_crit:
            num.lifetime = 1.5  # Longer display time
        self.numbers.append(num)
    
    def update(self, dt: float) -> None:
        """Update all damage numbers."""
        for num in self.numbers:
            num.age += dt
            num.y -= num.rise_speed * dt
        
        # Remove expired numbers
        self.numbers = [n for n in self.numbers if not n.is_expired]
    
    def render(
        self, 
        screen: pygame.Surface, 
        camera, 
        world_offset: tuple[int, int]
    ) -> None:
        """Render all damage numbers."""
        self._ensure_font()
        
        for num in self.numbers:
            # Convert world coords to screen coords
            iso_x, iso_y = camera.cart_to_iso(num.x, num.y)
            sx = iso_x + world_offset[0] + camera.x
            sy = iso_y + world_offset[1] + camera.y
            
            # Render with alpha
            # Render with alpha
            if isinstance(num.amount, str):
                msg = num.amount
            else:
                msg = f"-{num.amount}"
                
            text = self.font.render(msg, True, num.color)
            text.set_alpha(num.alpha)
            
            # Center the text
            text_rect = text.get_rect(center=(sx + 32, sy - 20))
            screen.blit(text, text_rect)
    
    def clear(self) -> None:
        """Clear all damage numbers."""
        self.numbers.clear()


# Singleton instance
_damage_manager: DamageNumberManager | None = None


def get_damage_manager() -> DamageNumberManager:
    """Get global damage number manager."""
    global _damage_manager
    if _damage_manager is None:
        _damage_manager = DamageNumberManager()
    return _damage_manager


def reset_damage_manager() -> None:
    """Reset the damage manager."""
    global _damage_manager
    if _damage_manager:
        _damage_manager.clear()
    _damage_manager = None
