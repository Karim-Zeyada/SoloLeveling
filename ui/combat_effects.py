"""
Combat effects and animations for visual feedback.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import pygame
import math

if TYPE_CHECKING:
    from rendering import Camera


@dataclass
class CombatEffect:
    """Base class for combat effects."""
    x: float
    y: float
    lifetime: float
    age: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        return self.age >= self.lifetime
    
    @property
    def progress(self) -> float:
        """Effect progress from 0.0 to 1.0."""
        return min(1.0, self.age / self.lifetime)


@dataclass
class SlashEffect(CombatEffect):
    """A slashing attack visual effect."""
    angle: float = 0.0  # Direction of slash
    color: tuple[int, int, int] = (255, 100, 100)
    lifetime: float = 0.3


@dataclass
class ImpactEffect(CombatEffect):
    """A hit impact visual effect."""
    color: tuple[int, int, int] = (255, 255, 255)
    lifetime: float = 0.2
    size: float = 20.0


class CombatEffectManager:
    """
    Manages combat visual effects.
    
    Usage:
        manager = CombatEffectManager()
        manager.add_slash(x, y, angle=0)
        manager.add_impact(x, y)
        manager.update(dt)
        manager.render(screen, camera, world_offset)
    """
    
    def __init__(self):
        self.effects: list[CombatEffect] = []
    
    def add_slash(
        self, 
        x: float, 
        y: float, 
        angle: float = 0.0,
        color: tuple[int, int, int] = (255, 100, 100)
    ) -> None:
        """Add a slash effect at world position."""
        self.effects.append(SlashEffect(
            x=x, y=y, angle=angle, color=color, lifetime=0.3
        ))
    
    def add_impact(
        self, 
        x: float, 
        y: float,
        color: tuple[int, int, int] = (255, 255, 255)
    ) -> None:
        """Add an impact effect at world position."""
        self.effects.append(ImpactEffect(
            x=x, y=y, color=color, lifetime=0.2
        ))
    
    def update(self, dt: float) -> None:
        """Update all effects."""
        for effect in self.effects:
            effect.age += dt
        
        # Remove expired effects
        self.effects = [e for e in self.effects if not e.is_expired]
    
    def render(
        self, 
        screen: pygame.Surface, 
        camera: 'Camera', 
        world_offset: tuple[int, int]
    ) -> None:
        """Render all effects."""
        for effect in self.effects:
            # Convert world coords to screen coords
            iso_x, iso_y = camera.cart_to_iso(effect.x, effect.y)
            sx = iso_x + world_offset[0] + camera.x + 32
            sy = iso_y + world_offset[1] + camera.y
            
            if isinstance(effect, SlashEffect):
                self._render_slash(screen, sx, sy, effect)
            elif isinstance(effect, ImpactEffect):
                self._render_impact(screen, sx, sy, effect)
    
    def _render_slash(
        self, 
        screen: pygame.Surface, 
        sx: float, 
        sy: float, 
        effect: SlashEffect
    ) -> None:
        """Render a slash effect."""
        # Arc that sweeps as progress increases
        progress = effect.progress
        alpha = int(255 * (1.0 - progress))
        
        # Create a surface for the slash
        size = 40
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw arc segments
        arc_start = effect.angle - 0.5 + progress * 0.5
        arc_end = effect.angle + 0.5 - progress * 0.3
        
        for i in range(8):
            t = i / 7.0
            angle = arc_start + t * (arc_end - arc_start)
            length = size * (0.5 + 0.5 * (1 - progress))
            
            x1 = size + math.cos(angle) * length * 0.3
            y1 = size + math.sin(angle) * length * 0.3
            x2 = size + math.cos(angle) * length
            y2 = size + math.sin(angle) * length
            
            color = (*effect.color, alpha)
            pygame.draw.line(surf, color, (x1, y1), (x2, y2), 3)
        
        screen.blit(surf, (sx - size, sy - size))
    
    def _render_impact(
        self, 
        screen: pygame.Surface, 
        sx: float, 
        sy: float, 
        effect: ImpactEffect
    ) -> None:
        """Render an impact effect (expanding ring)."""
        progress = effect.progress
        alpha = int(255 * (1.0 - progress))
        radius = int(effect.size * (0.3 + 0.7 * progress))
        
        # Create surface for impact
        size = int(effect.size * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center = size // 2
        color = (*effect.color, alpha)
        
        # Draw expanding circle
        if radius > 0:
            pygame.draw.circle(surf, color, (center, center), radius, 2)
        
        # Draw some particle lines
        for i in range(6):
            angle = i * math.pi / 3 + progress * 0.5
            length = radius * 0.8
            x1 = center + math.cos(angle) * radius * 0.3
            y1 = center + math.sin(angle) * radius * 0.3
            x2 = center + math.cos(angle) * length
            y2 = center + math.sin(angle) * length
            pygame.draw.line(surf, color, (x1, y1), (x2, y2), 2)
        
        screen.blit(surf, (sx - size // 2, sy - size // 2))
    
    def clear(self) -> None:
        """Clear all effects."""
        self.effects.clear()


# Singleton instance
_combat_manager: CombatEffectManager | None = None


def get_combat_manager() -> CombatEffectManager:
    """Get global combat effect manager."""
    global _combat_manager
    if _combat_manager is None:
        _combat_manager = CombatEffectManager()
    return _combat_manager


def reset_combat_manager() -> None:
    """Reset the combat manager."""
    global _combat_manager
    if _combat_manager:
        _combat_manager.clear()
    _combat_manager = None
