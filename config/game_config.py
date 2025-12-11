"""
Type-safe configuration using dataclasses.
Replaces dictionary-based configuration for better IDE support and validation.
"""
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class EntityConfig:
    """Base configuration for all entities."""
    name: str
    asset: str
    health: int
    damage: int
    speed: float  # Move interval in seconds
    description: str = ""


@dataclass(frozen=True)
class EnemyConfig(EntityConfig):
    """Configuration for enemy types."""
    detection_range: int = 8
    armor: int = 0


@dataclass(frozen=True)
class ShadowConfig(EntityConfig):
    """Configuration for shadow types."""
    cost: int = 10


@dataclass(frozen=True)
class LevelConfig:
    """Configuration for a game level."""
    grid_size: int
    start_resources: int
    resource_count: int
    enemies: tuple[tuple[str, int], ...]  # List of (enemy_type, count) tuples


@dataclass(frozen=True)
class BuildCosts:
    """Costs for building structures."""
    WALL: ClassVar[int] = 5
    TRAP: ClassVar[int] = 2


@dataclass(frozen=True)
class ScanConfig:
    """Configuration for scanning/fog of war."""
    RADIUS: ClassVar[int] = 5


@dataclass(frozen=True)
class CameraConfig:
    """Camera configuration."""
    EASE_SPEED: ClassVar[float] = 0.05
    ZOOM: ClassVar[float] = 0.25


@dataclass(frozen=True)
class TileConfig:
    """Tile rendering configuration."""
    WIDTH: ClassVar[int] = 677
    HEIGHT: ClassVar[int] = 369
    ELEVATION_OFFSET: ClassVar[int] = 150


# ============================================================================
# Pre-defined Configurations (replaces dictionaries in settings.py)
# ============================================================================

ENEMY_CONFIGS: dict[str, EnemyConfig] = {
    'security_agent': EnemyConfig(
        name='Security Agent',
        asset='enemy',
        health=30,
        damage=5,
        speed=0.5,
        detection_range=8,
        armor=0,
        description='Standard security - balanced threat'
    ),
    'elf': EnemyConfig(
        name='Elf Archer',
        asset='elf',
        health=20,
        damage=12,
        speed=0.35,
        detection_range=10,
        armor=1,
        description='Glass cannon - high damage, fragile'
    ),
    'alpha_bear': EnemyConfig(
        name='Alpha Bear',
        asset='alpha_bear',
        health=80,
        damage=8,
        speed=0.45,
        detection_range=6,
        armor=2,
        description='Tank - slow but extremely durable'
    ),
}

SHADOW_CONFIGS: dict[str, ShadowConfig] = {
    'shadow': ShadowConfig(
        name='Shadow Agent',
        asset='shadow',
        health=40,
        damage=5,
        speed=0.4,
        cost=15,
        description='Infantry - weak alone, strong in numbers'
    ),
    'igris': ShadowConfig(
        name='Igris',
        asset='igris',
        health=60,
        damage=15,
        speed=0.3,
        cost=40,
        description='Elite shadow warrior - swift and deadly'
    ),
    'beru': ShadowConfig(
        name='Beru',
        asset='beru',
        health=50,
        damage=20,
        speed=0.35,
        cost=50,
        description='Assassin - highest damage output'
    ),
}

LEVEL_CONFIGS: dict[int, LevelConfig] = {
    1: LevelConfig(
        grid_size=12, 
        start_resources=15, 
        resource_count=3,
        enemies=(('security_agent', 1),)
    ),
    2: LevelConfig(
        grid_size=14, 
        start_resources=12, 
        resource_count=4,
        enemies=(('security_agent', 1),)
    ),
    3: LevelConfig(
        grid_size=16, 
        start_resources=10, 
        resource_count=5,
        enemies=(('security_agent', 1), ('alpha_bear', 1))
    ),
    4: LevelConfig(
        grid_size=18, 
        start_resources=8, 
        resource_count=6,
        enemies=(('security_agent', 1), ('alpha_bear', 1))
    ),
    5: LevelConfig(
        grid_size=20, 
        start_resources=5, 
        resource_count=7,
        enemies=(('elf', 1), ('alpha_bear', 1), ('security_agent', 1))
    ),
}


def get_enemy_config(enemy_type: str) -> EnemyConfig:
    """Get enemy configuration with fallback to security_agent."""
    return ENEMY_CONFIGS.get(enemy_type, ENEMY_CONFIGS['security_agent'])


def get_shadow_config(shadow_type: str) -> ShadowConfig:
    """Get shadow configuration with fallback to base shadow."""
    return SHADOW_CONFIGS.get(shadow_type, SHADOW_CONFIGS['shadow'])


def get_level_config(level: int) -> LevelConfig | None:
    """Get level configuration or None if level doesn't exist."""
    return LEVEL_CONFIGS.get(level)
