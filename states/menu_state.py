"""
Main menu state.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType

if TYPE_CHECKING:
    from game_engine import GameEngine


class MainMenuState(BaseState):
    """Main menu state - displayed at game start."""
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return StateType.PLAYING
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        return None
    
    def update(self, dt: float) -> StateType | None:
        """No updates needed for menu."""
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render main menu."""
        screen.fill((20, 20, 30))
        self.engine.main_menu.render_main_menu(screen, self.screen_width, self.screen_height)
