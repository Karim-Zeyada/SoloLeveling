"""
Main game engine orchestrating all systems.
Refactored to use StateMachine pattern for game states.
"""
import pygame
from config import *
from entities import Grid, Player, Enemy, Shadow
from managers import AssetManager, SoundManager
from systems import Pathfinding
from rendering import Camera, Renderer
from ui import HUD, Minimap, ShadowMenu, MenuScreens
from core.state_machine import StateMachine, StateType
from core.logger import get_logger
from config.game_config import get_level_config

logger = get_logger('game_engine')


class GameEngine:
    """
    Main game engine coordinating all systems.
    
    Uses StateMachine pattern to delegate state-specific logic
    to individual State classes, keeping this class focused on
    initialization and the main loop.
    """
    
    def __init__(self):
        pygame.init()
        logger.info("Initializing game engine")
        
        # Create resizable window
        flags = pygame.RESIZABLE if WINDOW_RESIZABLE else 0
        if WINDOW_FULLSCREEN:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.SysFont('Arial', max(16, int(20 * RESPONSIVE_SCALE)))
        self.small_font = pygame.font.SysFont('Arial', max(10, int(12 * RESPONSIVE_SCALE)))
        self.large_font = pygame.font.SysFont('Arial', max(30, int(40 * RESPONSIVE_SCALE)), bold=True)
        
        # Managers
        self.assets = AssetManager()
        self.sounds = SoundManager()
        
        # Systems
        self.pathfinding = Pathfinding()
        self.camera = Camera()
        self.renderer = Renderer(self.assets)
        
        # UI Components
        self.hud = HUD(self.font)
        self.minimap = Minimap()
        from ui.trap_menu import TrapMenu  # Local import to avoid circular dependency
        self.trap_menu = TrapMenu(self.assets, self.font, self.small_font, self.large_font)
        self.shadow_menu = ShadowMenu(self.assets, self.font, self.small_font, self.large_font)
        self.main_menu = MenuScreens(self.font, self.large_font)
        self.menu_screens = self.main_menu  # Alias for compatibility
        
        # Game data
        self.current_level = START_LEVEL
        self.level_time = 0.0
        self.enemy_timer = 0.0
        
        # Track current screen size for responsive resizing
        self.current_screen_width = SCREEN_WIDTH
        self.current_screen_height = SCREEN_HEIGHT
        
        # Entity data
        self.grid = None
        self.player = None
        self.enemies = []
        self.shadows = []
        
        # Damage numbers
        from ui import get_damage_manager, get_combat_manager
        self.damage_manager = get_damage_manager()
        self.combat_manager = get_combat_manager()
        
        # Initialize first level
        self.init_level(self.current_level)
        
        # Setup state machine
        self._setup_state_machine()
        
        logger.info("Game engine initialized")
    
    def _setup_state_machine(self):
        """Initialize and register all game states."""
        from states import (
            PlayingState, MainMenuState, PausedState,
            LevelCompleteState, GameOverState, VictoryState
        )
        
        self.state_machine = StateMachine()
        
        # Register all states
        self.state_machine.register(StateType.MAIN_MENU, MainMenuState(self))
        self.state_machine.register(StateType.PLAYING, PlayingState(self))
        self.state_machine.register(StateType.PAUSED, PausedState(self))
        self.state_machine.register(StateType.LEVEL_COMPLETE, LevelCompleteState(self))
        self.state_machine.register(StateType.GAME_OVER, GameOverState(self))
        self.state_machine.register(StateType.VICTORY, VictoryState(self))
        
        # Start at main menu
        self.state_machine.transition_to(StateType.MAIN_MENU)
    
    def init_level(self, level_num: int) -> None:
        """Initialize a new level with randomized positions."""
        import random
        import time
        
        # Seed random with current time for truly random positions each run/level
        random.seed(time.time())
        
        config = get_level_config(level_num)
        if config is None:
            logger.info("No more levels - victory!")
            self.grid = None
            return
        
        logger.info("Initializing level %d", level_num)
    
        # Procedural map generation
        from systems.procgen import CellularAutomataGenerator
        # Make map bigger for more exploration
        gen_width = int(config.grid_size * 1.5)
        gen_height = int(config.grid_size * 1.5)
        
        generator = CellularAutomataGenerator(gen_width, gen_height)
        layout = generator.generate(wall_prob=0.38, iterations=3)
        
        self.grid = Grid(gen_width, gen_height, level=level_num, layout=layout)
        
        # Use largest region for spawning
        largest_region = generator.largest_region if generator.largest_region else []
        
        # Player spawns near top-left of region
        if largest_region:
            # Sort by distance from (2,2) to find a good starting spot
            sorted_by_start = sorted(largest_region, key=lambda p: (p[0]**2 + p[1]**2))
            spawn_x, spawn_y = sorted_by_start[0]
        else:
            spawn_x, spawn_y = 2, 2
        
        self.player = Player(spawn_x, spawn_y)
        self.player.resources = config.start_resources
        
        # Exit spawns at a random position far from player (not always the farthest)
        if largest_region:
            # Get candidates that are at least half the map away from player
            far_candidates = [p for p in largest_region 
                            if abs(p[0]-spawn_x) + abs(p[1]-spawn_y) > config.grid_size // 2]
            if far_candidates:
                # Randomly pick from far candidates for variety
                exit_x, exit_y = random.choice(far_candidates)
            else:
                # Fallback to farthest point
                sorted_by_dist = sorted(largest_region, key=lambda p: abs(p[0]-spawn_x) + abs(p[1]-spawn_y), reverse=True)
                exit_x, exit_y = sorted_by_dist[0]
            exit_tile = self.grid.get_tile(exit_x, exit_y)
            if exit_tile:
                exit_tile.type = 'exit'
        else:
            self.grid.place_exit()
        
        # Place resources in the connected region
        self.grid.place_resources(config.resource_count)
        
        # Create enemies at random positions (far from player)
        self.enemies = []
        if largest_region:
            # Get candidates far from player and exit
            enemy_candidates = [p for p in largest_region 
                               if abs(p[0]-spawn_x) + abs(p[1]-spawn_y) > config.grid_size // 3]
            # Remove exit position from candidates
            if (exit_x, exit_y) in enemy_candidates:
                enemy_candidates.remove((exit_x, exit_y))
            # Shuffle for randomness
            random.shuffle(enemy_candidates)
        else:
            enemy_candidates = []
        
        enemy_index = 0
        for enemy_type, count in config.enemies:
            for i in range(count):
                if enemy_candidates and enemy_index < len(enemy_candidates):
                    ex, ey = enemy_candidates[enemy_index]
                else:
                    # Fallback positions
                    ex = random.randint(3, self.grid.width - 4)
                    ey = random.randint(3, self.grid.height - 4)
                
                enemy = Enemy(ex, ey, enemy_type=enemy_type)
                self.enemies.append(enemy)
                enemy_index += 1
        
        # Reset shadows
        self.shadows = []
        
        # Reset timers
        self.enemy_timer = 0.0
        self.level_time = 0.0
        
        # Initial scan
        self._perform_initial_scan()
    
    def _perform_initial_scan(self) -> None:
        """Reveal tiles around player starting position."""
        if self.player and self.grid:
            revealed = self.pathfinding.bfs_scan(
                (self.player.x, self.player.y), 
                self.grid, 
                radius=5
            )
            for rx, ry in revealed:
                tile = self.grid.get_tile(rx, ry)
                if tile:
                    tile.visible = True
    
    def handle_events(self) -> bool:
        """
        Handle pygame events.
        Returns False if game should quit.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Window resize
            if event.type == pygame.VIDEORESIZE:
                self.current_screen_width = event.w
                self.current_screen_height = event.h
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), 
                    pygame.RESIZABLE
                )
            
            # Delegate to current state
            self.state_machine.handle_event(event)
        
        return True
    
    def update(self, dt: float) -> None:
        """Update game logic via current state."""
        self.state_machine.update(dt)
    
    def render(self) -> None:
        """Render game via current state."""
        self.state_machine.render(self.screen)
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        logger.info("Starting game loop")
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update(dt)
            
            # Render
            self.render()
        
        logger.info("Game loop ended")
        pygame.quit()
