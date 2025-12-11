"""
Victory state - player beat all levels.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType
from core.logger import get_logger

if TYPE_CHECKING:
    from game_engine import GameEngine

logger = get_logger('victory')


class VictoryState(BaseState):
    """Victory state - player beat the game."""
    
    def enter(self) -> None:
        """Log victory."""
        logger.info("Victory! All levels completed!")
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle input to return to menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                # Reset to level 1 and go to menu
                self.engine.current_level = 1
                self.engine.init_level(1)
                return StateType.MAIN_MENU
        return None
    
    def update(self, dt: float) -> StateType | None:
        """No updates needed."""
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render victory screen."""
        screen.fill((20, 20, 50))
        
        font = pygame.font.Font(None, 72)
        title = font.render("VICTORY!", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title, title_rect)
        
        font_medium = pygame.font.Font(None, 48)
        subtitle = font_medium.render("ALL LEVELS COMPLETE", True, (200, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(subtitle, subtitle_rect)
        
        font_small = pygame.font.Font(None, 36)
        prompt = font_small.render("Press ENTER to return to menu", True, (150, 150, 150))
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, self.screen_height * 2 // 3))
        screen.blit(prompt, prompt_rect)
