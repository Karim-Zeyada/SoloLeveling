"""
Paused state - game is paused.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType

if TYPE_CHECKING:
    from game_engine import GameEngine


class PausedState(BaseState):
    """Paused state - game frozen with overlay."""
    
    def __init__(self, engine: 'GameEngine'):
        super().__init__(engine)
        self.selected_option = 0
        self.options = ['Resume', 'Quit']
    
    def enter(self) -> None:
        """Reset selection when entering pause."""
        self.selected_option = 0
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle pause menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return StateType.PLAYING
            
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            
            if event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Resume
                    return StateType.PLAYING
                elif self.selected_option == 1:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        return None
    
    def update(self, dt: float) -> StateType | None:
        """No updates needed while paused."""
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render pause overlay."""
        # First render the game behind
        screen.fill((20, 20, 30))
        self.engine.renderer.render_game(
            screen, self.engine.grid, self.engine.player,
            self.engine.enemies, self.engine.shadows,
            self.engine.camera, self.screen_width, self.screen_height
        )
        
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        title = font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title, title_rect)
        
        # Menu options
        font_small = pygame.font.Font(None, 48)
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = font_small.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + i * 60))
            screen.blit(text, text_rect)
