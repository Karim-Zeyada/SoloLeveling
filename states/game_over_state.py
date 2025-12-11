"""
Game over state - player was caught.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType
from core.logger import get_logger

if TYPE_CHECKING:
    from game_engine import GameEngine

logger = get_logger('game_over')


class GameOverState(BaseState):
    """Game over state - player lost."""
    
    def enter(self) -> None:
        """Log game over."""
        logger.info("Game over!")
        self.engine.sounds.play('game_over')
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle input to restart or quit."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Restart current level
                self.engine.init_level(self.engine.current_level)
                return StateType.PLAYING
            if event.key == pygame.K_ESCAPE:
                return StateType.MAIN_MENU
        return None
    
    def update(self, dt: float) -> StateType | None:
        """No updates needed."""
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render game over screen."""
        screen.fill((40, 20, 20))
        
        font = pygame.font.Font(None, 72)
        title = font.render("GAME OVER", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title, title_rect)
        
        font_small = pygame.font.Font(None, 36)
        info = font_small.render("You were caught!", True, (255, 200, 200))
        info_rect = info.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(info, info_rect)
        
        prompt = font_small.render("ENTER: Retry  |  ESC: Main Menu", True, (150, 150, 150))
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, self.screen_height * 2 // 3))
        screen.blit(prompt, prompt_rect)
