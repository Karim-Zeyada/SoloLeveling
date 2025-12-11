"""
Core module containing shared infrastructure.
"""
from .events import EventBus, Event, get_event_bus, reset_event_bus
from .events import (
    EntityDiedEvent,
    DamageTakenEvent,
    ResourceCollectedEvent,
    LevelCompleteEvent,
    BuildEvent
)
from .protocols import Positionable, Damageable, Movable, Renderable, Updatable
from .state_machine import State, StateMachine, StateType
from .logger import get_logger, enable_debug_logging, enable_file_logging

__all__ = [
    # Event System
    'EventBus',
    'Event',
    'get_event_bus',
    'reset_event_bus',
    
    # Event Types
    'EntityDiedEvent',
    'DamageTakenEvent',
    'ResourceCollectedEvent',
    'LevelCompleteEvent',
    'BuildEvent',
    
    # Protocols
    'Positionable',
    'Damageable',
    'Movable',
    'Renderable',
    'Updatable',
    
    # State Machine
    'State',
    'StateMachine',
    'StateType',
    
    # Logging
    'get_logger',
    'enable_debug_logging',
    'enable_file_logging',
]
