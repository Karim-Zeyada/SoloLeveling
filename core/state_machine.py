"""
State Machine pattern for game state management.
Provides clean transitions and state-specific update/render logic.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable
import pygame

if TYPE_CHECKING:
    from game_engine import GameEngine


class StateType(Enum):
    """Enumeration of all possible game states."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class State(ABC):
    """
    Abstract base class for game states.
    
    Each state handles its own:
    - Input processing
    - Update logic
    - Rendering
    """
    
    def __init__(self, engine: 'GameEngine'):
        self.engine = engine
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when leaving this state."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """
        Handle a pygame event.
        Returns a new StateType to transition to, or None to stay in current state.
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> StateType | None:
        """
        Update state logic.
        Returns a new StateType to transition to, or None to stay in current state.
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render this state to the screen."""
        pass


class StateMachine:
    """
    Manages game state transitions.
    
    Usage:
        machine = StateMachine()
        machine.register(StateType.MAIN_MENU, MainMenuState(engine))
        machine.transition_to(StateType.MAIN_MENU)
    """
    
    def __init__(self):
        self._states: dict[StateType, State] = {}
        self._current_state: State | None = None
        self._current_type: StateType | None = None
    
    def register(self, state_type: StateType, state: State) -> None:
        """Register a state with the machine."""
        self._states[state_type] = state
    
    def transition_to(self, state_type: StateType) -> None:
        """Transition to a new state."""
        if self._current_state:
            self._current_state.exit()
        
        self._current_state = self._states.get(state_type)
        self._current_type = state_type
        
        if self._current_state:
            self._current_state.enter()
    
    @property
    def current_type(self) -> StateType | None:
        return self._current_type
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Pass event to current state."""
        if self._current_state:
            new_state = self._current_state.handle_event(event)
            if new_state is not None:
                self.transition_to(new_state)
    
    def update(self, dt: float) -> None:
        """Update current state."""
        if self._current_state:
            new_state = self._current_state.update(dt)
            if new_state is not None:
                self.transition_to(new_state)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render current state."""
        if self._current_state:
            self._current_state.render(screen)
