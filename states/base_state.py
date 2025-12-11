"""
Base state class providing shared functionality for all game states.
"""
from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
import pygame

from core.state_machine import State, StateType

if TYPE_CHECKING:
    from game_engine import GameEngine


class BaseState(State):
    """
    Base class for all game states with shared engine access.
    
    Provides:
    - Access to game engine and all its subsystems
    - Common helper methods for rendering
    - Default implementations for enter/exit
    """
    
    def __init__(self, engine: 'GameEngine'):
        super().__init__(engine)
        self.engine = engine
    
    def enter(self) -> None:
        """Called when entering this state. Override if needed."""
        pass
    
    def exit(self) -> None:
        """Called when leaving this state. Override if needed."""
        pass
    
    # Convenience accessors
    @property
    def screen(self) -> pygame.Surface:
        return self.engine.screen
    
    @property
    def screen_width(self) -> int:
        return self.engine.current_screen_width
    
    @property
    def screen_height(self) -> int:
        return self.engine.current_screen_height
