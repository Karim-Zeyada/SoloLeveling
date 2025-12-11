"""
Input handling service for decoupled keyboard/mouse input processing.
Provides action-based input mapping and callbacks.
"""
from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
import pygame

if TYPE_CHECKING:
    from core.events import EventBus


class InputAction(Enum):
    """Enumeration of all input actions in the game."""
    # Movement
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    
    # Actions
    SCAN = auto()
    BUILD_WALL = auto()
    BUILD_TRAP = auto()
    
    # Shadow commands
    SUMMON_SHADOW = auto()
    DISMISS_SHADOW = auto()
    COMMAND_ATTACK = auto()
    
    # UI
    CONFIRM = auto()
    CANCEL = auto()
    PAUSE = auto()
    
    # Navigation (for menus)
    NAV_UP = auto()
    NAV_DOWN = auto()
    NAV_LEFT = auto()
    NAV_RIGHT = auto()


@dataclass
class InputBinding:
    """Maps a key to an action."""
    key: int
    action: InputAction
    modifiers: int = 0  # pygame.KMOD_* flags


class InputHandler:
    """
    Handles input mapping and action dispatching.
    
    Features:
    - Configurable key bindings
    - Action-based callbacks
    - Separate handling for key press vs key held
    
    Usage:
        handler = InputHandler()
        handler.bind_action(InputAction.MOVE_UP, on_move_up)
        handler.handle_event(event)
    """
    
    # Default key bindings
    DEFAULT_BINDINGS: list[InputBinding] = [
        # Movement (Arrow keys)
        InputBinding(pygame.K_UP, InputAction.MOVE_UP),
        InputBinding(pygame.K_DOWN, InputAction.MOVE_DOWN),
        InputBinding(pygame.K_LEFT, InputAction.MOVE_LEFT),
        InputBinding(pygame.K_RIGHT, InputAction.MOVE_RIGHT),
        
        # Movement (WASD) - for menus
        InputBinding(pygame.K_w, InputAction.NAV_UP),
        InputBinding(pygame.K_s, InputAction.NAV_DOWN),
        InputBinding(pygame.K_a, InputAction.NAV_LEFT),
        InputBinding(pygame.K_d, InputAction.NAV_RIGHT),
        
        # Actions
        InputBinding(pygame.K_SPACE, InputAction.SCAN),
        InputBinding(pygame.K_b, InputAction.BUILD_WALL),
        InputBinding(pygame.K_t, InputAction.BUILD_TRAP),
        
        # Shadow commands
        InputBinding(pygame.K_r, InputAction.SUMMON_SHADOW),
        InputBinding(pygame.K_u, InputAction.DISMISS_SHADOW),
        InputBinding(pygame.K_f, InputAction.COMMAND_ATTACK),
        
        # UI
        InputBinding(pygame.K_RETURN, InputAction.CONFIRM),
        InputBinding(pygame.K_ESCAPE, InputAction.CANCEL),
        InputBinding(pygame.K_ESCAPE, InputAction.PAUSE),
    ]
    
    def __init__(self):
        self._bindings: dict[int, InputAction] = {}
        self._action_callbacks: dict[InputAction, list[Callable[[], None]]] = {}
        
        # Load default bindings
        for binding in self.DEFAULT_BINDINGS:
            self._bindings[binding.key] = binding.action
    
    def bind_key(self, key: int, action: InputAction) -> None:
        """Bind a key to an action."""
        self._bindings[key] = action
    
    def unbind_key(self, key: int) -> None:
        """Remove a key binding."""
        self._bindings.pop(key, None)
    
    def on_action(self, action: InputAction, callback: Callable[[], None]) -> None:
        """Register a callback for an action."""
        if action not in self._action_callbacks:
            self._action_callbacks[action] = []
        self._action_callbacks[action].append(callback)
    
    def off_action(self, action: InputAction, callback: Callable[[], None]) -> None:
        """Remove a callback for an action."""
        if action in self._action_callbacks:
            try:
                self._action_callbacks[action].remove(callback)
            except ValueError:
                pass
    
    def clear_callbacks(self) -> None:
        """Clear all action callbacks."""
        self._action_callbacks.clear()
    
    def get_action_for_key(self, key: int) -> InputAction | None:
        """Get the action mapped to a key."""
        return self._bindings.get(key)
    
    def handle_key_down(self, key: int) -> InputAction | None:
        """
        Handle a key down event.
        Triggers callbacks and returns the action if bound.
        """
        action = self._bindings.get(key)
        if action and action in self._action_callbacks:
            for callback in self._action_callbacks[action]:
                callback()
        return action
    
    def handle_event(self, event: pygame.event.Event) -> InputAction | None:
        """
        Handle a pygame event.
        Returns the InputAction if this was a bound key press.
        """
        if event.type == pygame.KEYDOWN:
            return self.handle_key_down(event.key)
        return None
    
    def is_action_key(self, key: int, action: InputAction) -> bool:
        """Check if a key is bound to a specific action."""
        return self._bindings.get(key) == action


# Singleton instance for global access
_input_handler: InputHandler | None = None


def get_input_handler() -> InputHandler:
    """Get the global input handler instance."""
    global _input_handler
    if _input_handler is None:
        _input_handler = InputHandler()
    return _input_handler


def reset_input_handler() -> None:
    """Reset the global input handler."""
    global _input_handler
    _input_handler = None
