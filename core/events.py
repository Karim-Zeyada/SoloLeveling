"""
Simple event system for decoupling game components.
Allows entities and systems to communicate without direct references.
"""
from typing import Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Event:
    """Base event class - all events inherit from this."""
    pass


@dataclass
class EntityDiedEvent(Event):
    """Fired when an entity dies."""
    entity_type: str  # 'enemy', 'shadow', 'player'
    position: tuple[int, int]
    

@dataclass
class DamageTakenEvent(Event):
    """Fired when an entity takes damage."""
    entity_type: str
    damage: int
    remaining_health: int
    position: tuple[int, int]


@dataclass
class ResourceCollectedEvent(Event):
    """Fired when player collects a resource."""
    amount: int
    total_resources: int
    position: tuple[int, int]


@dataclass
class LevelCompleteEvent(Event):
    """Fired when player reaches the exit."""
    level: int
    time_taken: float
    resources_remaining: int


@dataclass
class BuildEvent(Event):
    """Fired when player builds something."""
    build_type: str  # 'wall', 'trap', 'shadow'
    cost: int
    position: tuple[int, int]


class EventBus:
    """
    Central event bus for publish/subscribe pattern.
    
    Usage:
        bus = EventBus()
        bus.subscribe(EntityDiedEvent, on_entity_died)
        bus.publish(EntityDiedEvent(entity_type='enemy', position=(5, 5)))
    """
    
    def __init__(self):
        self._subscribers: dict[type[Event], list[Callable[[Event], None]]] = defaultdict(list)
    
    def subscribe(self, event_type: type[Event], callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type with a callback function."""
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: type[Event], callback: Callable[[Event], None]) -> None:
        """Unsubscribe a callback from an event type."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)
        for callback in self._subscribers[event_type]:
            callback(event)
    
    def clear(self) -> None:
        """Clear all subscriptions."""
        self._subscribers.clear()


# Global event bus instance (singleton pattern)
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _event_bus
    if _event_bus:
        _event_bus.clear()
    _event_bus = None
