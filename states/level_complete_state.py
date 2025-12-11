"""
Level complete state - player reached the exit.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType
from core.logger import get_logger

if TYPE_CHECKING:
    from game_engine import GameEngine

logger = get_logger('level_complete')


class LevelCompleteState(BaseState):
    """Level complete state - player won the level."""
    
    def enter(self) -> None:
        """Log level completion."""
        logger.info("Level %d complete!", self.engine.current_level)
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle input to proceed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Advance to next level
                self.engine.current_level += 1
                self.engine.init_level(self.engine.current_level)
                
                # Check if we've won the game
                if self.engine.grid is None:
                    return StateType.VICTORY
                return StateType.PLAYING
        return None
    
    def update(self, dt: float) -> StateType | None:
        """No updates needed."""
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render level complete screen."""
        screen.fill((20, 40, 20))
        
        font = pygame.font.Font(None, 72)
        title = font.render("LEVEL COMPLETE", True, (100, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title, title_rect)
        
        font_small = pygame.font.Font(None, 36)
        info = font_small.render(f"Level {self.engine.current_level} cleared!", True, (200, 255, 200))
        info_rect = info.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(info, info_rect)
        
        prompt = font_small.render("Press ENTER to continue", True, (150, 150, 150))
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, self.screen_height * 2 // 3))
        screen.blit(prompt, prompt_rect)
