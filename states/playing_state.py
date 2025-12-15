"""
Playing state - handles active gameplay.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from .base_state import BaseState
from core.state_machine import StateType
from config import BuildCosts, get_level_config, GRAY
from core.logger import get_logger

if TYPE_CHECKING:
    from game_engine import GameEngine

logger = get_logger('playing_state')


class PlayingState(BaseState):
    """
    Active gameplay state.
    
    Handles:
    - Player movement and input
    - Enemy and shadow updates
    - Build actions
    - Win/lose condition checks
    """
    
    def enter(self) -> None:
        """Called when entering playing state."""
        logger.debug("Entering playing state")
        # Register callbacks
        self.engine.trap_menu.on_build_callback = self._build_trap
    
    def exit(self) -> None:
        """Called when leaving playing state."""
        logger.debug("Exiting playing state")
    
    def handle_event(self, event: pygame.event.Event) -> StateType | None:
        """Handle gameplay input events."""
        if event.type == pygame.KEYDOWN:
            # Escape - pause or close menus
            if event.key == pygame.K_ESCAPE:
                if self.engine.shadow_menu.active:
                    self.engine.shadow_menu.close()
                elif self.engine.trap_menu.active:
                    self.engine.trap_menu.close()
                else:
                    return StateType.PAUSED
            
            # Shadow menu input
            if self.engine.shadow_menu.active:
                self.engine.shadow_menu.handle_input(
                    event.key, 
                    self.engine.player, 
                    self.engine.shadows, 
                    self.engine.sounds
                )
                return None

            # Trap menu input
            if self.engine.trap_menu.active:
                self.engine.trap_menu.handle_input(
                    event.key,
                    self.engine.player,
                    self.engine.sounds
                )
                return None
            
            # Movement
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.engine.player.move(0, -1, self.engine.grid)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.engine.player.move(0, 1, self.engine.grid)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.engine.player.move(-1, 0, self.engine.grid)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.engine.player.move(1, 0, self.engine.grid)
            
            # Actions
            elif event.key == pygame.K_SPACE:
                self._perform_scan()
            elif event.key == pygame.K_b:
                self._build_action('wall')
            elif event.key == pygame.K_t:
                self.engine.trap_menu.open()
            
            # Shadow commands
            elif event.key == pygame.K_r:
                self.engine.shadow_menu.open()
            elif event.key == pygame.K_u:
                self._dismiss_shadow()
            elif event.key == pygame.K_f:
                self._toggle_shadow_attack()

            # Combat commands
            elif event.key == pygame.K_z or event.key == pygame.K_q:
                self._perform_melee_attack()
            elif event.key == pygame.K_x:
                self._perform_skill_attack_key()
        
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left Click - Move
                self._handle_mouse_click(event.pos)
            elif event.button == 3:  # Right Click - Skill
                self._perform_skill_attack_mouse(event.pos)
        
        # Mouse movement - update hover tile
        if event.type == pygame.MOUSEMOTION:
            self._update_hover_tile(event.pos)
        
        return None
    
    def update(self, dt: float) -> StateType | None:
        """Update gameplay logic."""
        self.engine.level_time += dt
        
        # Update player
        self.engine.player.update(dt, self.engine.grid)
        if not self.engine.player.moving and self.engine.player.path:
            nx, ny = self.engine.player.path.pop(0)
            self.engine.player.start_move_to(nx, ny, self.engine.grid)
        
        # Update BFS animation
        self.engine.renderer.update_bfs_animation(dt, self.engine.grid)
        
        # Update enemies
        self.engine.enemy_timer += dt
        for enemy in self.engine.enemies:
            enemy.update(dt, self.engine.player, self.engine.grid, self.engine.pathfinding)
            enemy.move_step(dt)
            
            # Check if caught
            if enemy.check_caught_player(self.engine.player):
                dmg = enemy.attack_player(self.engine.player)
                if dmg > 0:
                    self.engine.damage_manager.add(
                        self.engine.player.x, self.engine.player.y, 
                        dmg, color=(200, 0, 0)
                    )
                    logger.info("Enemy %s hit player for %d damage", enemy.type_name, dmg)
                    
                    # Check player death
                    if self.engine.player.is_dead:
                        return StateType.GAME_OVER
        
        if self.engine.enemy_timer > 0.1:
            self.engine.enemy_timer = 0.0
        
        # Grant resources for killed enemies before removing them
        for enemy in self.engine.enemies:
            if enemy.is_dead:
                # Resource drop based on enemy type
                resource_drops = {
                    'security_agent': 10,
                    'elf': 20,
                    'alpha_bear': 12
                }
                drop_amount = resource_drops.get(enemy.enemy_type, 10)
                self.engine.player.resources += drop_amount
                
                # Show resource pickup notification at player position (more visible)
                self.engine.damage_manager.add(
                    self.engine.player.x, self.engine.player.y,
                    f"+{drop_amount} DATA",
                    color=(50, 255, 50),  # Green for resources
                    is_crit=True  # Make it larger
                )
                logger.info("Enemy %s killed! Gained %d resources", enemy.type_name, drop_amount)
        
        # Remove dead enemies
        self.engine.enemies = [e for e in self.engine.enemies if not e.is_dead]
        
        # Check traps on enemies
        self._check_trap_triggers()
        
        # Update tiles (trap cooldowns)
        if self.engine.grid:
            for y in range(self.engine.grid.height):
                for x in range(self.engine.grid.width):
                    tile = self.engine.grid.get_tile(x, y)
                    if tile:
                        tile.update(dt)
        
        # Update damage numbers
        self.engine.damage_manager.update(dt)
        
        # Update combat effects
        self.engine.combat_manager.update(dt)
        
        # Update shadows
        for shadow in self.engine.shadows:
            shadow.update(dt, self.engine.player, self.engine.enemies, 
                         self.engine.grid, self.engine.pathfinding)
        
        # Remove dead shadows
        self.engine.shadows = [s for s in self.engine.shadows if not s.is_dead]
        
        # Update camera
        self.engine.camera.update(self.engine.player, self.screen_width, self.screen_height)
        
        # Check win condition
        exit_pos = self._get_exit_pos()
        if (int(self.engine.player.x), int(self.engine.player.y)) == exit_pos:
            return StateType.LEVEL_COMPLETE
        
        return None
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the game."""
        screen.fill((20, 20, 30))
        
        self.engine.renderer.render_game(
            screen, self.engine.grid, self.engine.player, 
            self.engine.enemies, self.engine.shadows,
            self.engine.camera, self.screen_width, self.screen_height
        )
        
        # Render damage numbers
        world_offset = self.engine.camera.get_world_offset(
            self.screen_width, self.screen_height
        )
        self.engine.damage_manager.render(screen, self.engine.camera, world_offset)
        self.engine.combat_manager.render(screen, self.engine.camera, world_offset)
        
        self.engine.hud.render(
            screen, self.engine.current_level, self.engine.player, 
            self.engine.shadows, self.engine.level_time
        )
        # Minimap removed per user request
        self.engine.shadow_menu.render(
            screen, self.screen_width, self.screen_height, 
            self.engine.player.resources
        )
        self.engine.trap_menu.render(
            screen, self.screen_width, self.screen_height,
            self.engine.player.resources
        )
        
        # Render AI stats panel (top-right)
        self.engine.renderer.render_ai_stats_panel(
            screen, self.engine.enemies, self.screen_width
        )
    
    # Private helper methods
    def _perform_scan(self) -> None:
        """Perform animated BFS scan to reveal tiles around player."""
        # Use layered BFS for wave animation
        layers = self.engine.pathfinding.bfs_scan_layered(
            (int(self.engine.player.x), int(self.engine.player.y)), 
            self.engine.grid, radius=5
        )
        # Start the animation in renderer
        self.engine.renderer.start_bfs_animation(layers)
    
    def _build_action(self, type_str: str) -> None:
        """Build wall at player position."""
        tile = self.engine.grid.get_tile(
            int(self.engine.player.x), 
            int(self.engine.player.y)
        )
        if not tile:
            return
        
        if type_str == 'wall':
            cost = BuildCosts.WALL
            if self.engine.player.resources >= cost and tile.type == 'floor':
                self.engine.player.resources -= cost
                tile.type = 'wall'
                tile.cost = 999
                self.engine.sounds.play('build')
    
    def _build_trap(self, trap_type: str) -> bool:
        """
        Build a specific trap at player position.
        Callback for TrapMenu.
        
        Returns:
            bool: True if built successfully
        """
        tile = self.engine.grid.get_tile(
            int(self.engine.player.x),
            int(self.engine.player.y)
        )
        if not tile:
            return False
            
        if tile.type == 'floor':
            # Cost is handled by caller (TrapMenu) or here? 
            # TrapMenu logic says: if callback returns True, deduct cost.
            # So here we just validate tile.
            
            tile.type = 'trap'
            tile.trap_type = trap_type
            tile.cost = 5
            return True
            
        return False
    
    def _dismiss_shadow(self) -> None:
        """Dismiss last shadow and refund resources."""
        if self.engine.shadows:
            dismissed = self.engine.shadows.pop()
            self.engine.player.resources += dismissed.cost
            self.engine.sounds.play('build')
    
    def _toggle_shadow_attack(self) -> None:
        """Toggle all shadows to attack mode."""
        for shadow in self.engine.shadows:
            shadow.state = "ATTACK" if shadow.state == "IDLE" else "IDLE"

    def _perform_melee_attack(self) -> None:
        """Execute player melee attack."""
        hits = self.engine.player.attack(self.engine.enemies)
        if hits:
            self.engine.sounds.play('build')  # Reuse build sound
            for enemy in hits:
                # Visual effect
                self.engine.combat_manager.add_slash(enemy.x, enemy.y)
                
                # Add damage number
                self.engine.damage_manager.add(
                    enemy.x, enemy.y, 
                    self.engine.player.damage, 
                    color=(255, 50, 50)
                )
                logger.info("Player hit %s for %d damage (HP: %d)", 
                          enemy.type_name, self.engine.player.damage, enemy.health)

    def _perform_skill_attack_key(self) -> None:
        """Execute player ranged skill attack (Key binding)."""
        target_pos = self.engine.renderer.hover_tile
        if not target_pos:
            return
        self._execute_skill_at(target_pos)

    def _perform_skill_attack_mouse(self, pos: tuple[int, int]) -> None:
        """Execute player ranged skill attack (Mouse click)."""
        # Convert screen pos to grid pos
        from config import TILE_WIDTH, TILE_HEIGHT
        
        mx, my = pos
        world_offset = self.engine.camera.get_world_offset(
            self.screen_width, self.screen_height
        )
        world_x = mx - world_offset[0] - self.engine.camera.x
        world_y = my - world_offset[1] - self.engine.camera.y
        fx = world_x / (TILE_WIDTH / 2)
        fy = world_y / (TILE_HEIGHT / 2)
        gx = int(round((fx + fy) / 2))
        gy = int(round((fy - fx) / 2))
        
        self._execute_skill_at((gx, gy))

    def _execute_skill_at(self, target_pos: tuple[int, int]) -> None:
        """Helper to run skill logic."""
        hit_enemy = self.engine.player.skill_dagger_throw(target_pos, self.engine.enemies)
        if hit_enemy:
            self.engine.sounds.play('build')
            
            # Impact effect
            self.engine.combat_manager.add_slash(hit_enemy.x, hit_enemy.y)
            
            # Add damage number (Crit)
            self.engine.damage_manager.add(
                hit_enemy.x, hit_enemy.y, 
                self.engine.player.damage * 2, 
                color=(255, 0, 0),
                is_crit=True
            )
            logger.info("Player SKILL hit %s for %d damage (HP: %d)", 
                      hit_enemy.type_name, self.engine.player.damage * 2, hit_enemy.health)
        else:
            # Miss feedback
            target_grid_x, target_grid_y = target_pos
            self.engine.damage_manager.add(
                target_grid_x, target_grid_y, 
                "MISS", 
                color=GRAY
            )
            # Optional: play 'swish' sound if available
            # self.engine.sounds.play('swing')
    
    def _check_trap_triggers(self) -> None:
        """Check if any enemies are standing on traps and trigger damage."""
        for enemy in self.engine.enemies:
            tile = self.engine.grid.get_tile(enemy.x, enemy.y)
            if tile and tile.type == 'trap':
                effect_data = tile.trigger_trap(enemy)
                if effect_data:
                    # Apply status effect
                    if effect_data['effect'] in ['freeze', 'slow']:
                        enemy.apply_effect(effect_data['effect'], effect_data['duration'])
                        
                    # Add floating damage number if damage was dealt
                    if effect_data['damage'] > 0:
                        self.engine.damage_manager.add(
                            enemy.x, enemy.y, 
                            effect_data['damage'], 
                            color=(255, 150, 50)  # Orange for trap damage
                        )
                        logger.debug("Trap %s dealt %d damage to %s", 
                                   tile.trap_type, effect_data['damage'], enemy.type_name)
    
    def _handle_mouse_click(self, pos: tuple[int, int]) -> None:
        """Handle mouse click for pathfinding movement."""
        from config import TILE_WIDTH, TILE_HEIGHT
        
        mx, my = pos
        world_offset = self.engine.camera.get_world_offset(
            self.screen_width, self.screen_height
        )
        world_x = mx - world_offset[0] - self.engine.camera.x
        world_y = my - world_offset[1] - self.engine.camera.y
        fx = world_x / (TILE_WIDTH / 2)
        fy = world_y / (TILE_HEIGHT / 2)
        gx = int(round((fx + fy) / 2))
        gy = int(round((fy - fx) / 2))
        
        if 0 <= gx < self.engine.grid.width and 0 <= gy < self.engine.grid.height:
            path = self.engine.pathfinding.a_star(
                (int(self.engine.player.x), int(self.engine.player.y)), 
                (gx, gy), 
                self.engine.grid
            )
            if path:
                self.engine.player.path = path
                if not self.engine.player.moving:
                    nx, ny = self.engine.player.path.pop(0)
                    self.engine.player.start_move_to(nx, ny, self.engine.grid)
    
    def _get_exit_pos(self) -> tuple[int, int]:
        """Find exit position on grid."""
        for y in range(self.engine.grid.height):
            for x in range(self.engine.grid.width):
                tile = self.engine.grid.get_tile(x, y)
                if tile and tile.type == 'exit':
                    return (x, y)
        return (self.engine.grid.width - 1, self.engine.grid.height - 1)
    
    def _update_hover_tile(self, pos: tuple[int, int]) -> None:
        """Update the hovered tile based on mouse position."""
        from config import TILE_WIDTH, TILE_HEIGHT
        
        mx, my = pos
        world_offset = self.engine.camera.get_world_offset(
            self.screen_width, self.screen_height
        )
        world_x = mx - world_offset[0] - self.engine.camera.x
        world_y = my - world_offset[1] - self.engine.camera.y
        fx = world_x / (TILE_WIDTH / 2)
        fy = world_y / (TILE_HEIGHT / 2)
        gx = int(round((fx + fy) / 2))
        gy = int(round((fy - fx) / 2))
        
        # Update renderer's hover tile
        if 0 <= gx < self.engine.grid.width and 0 <= gy < self.engine.grid.height:
            self.engine.renderer.hover_tile = (gx, gy)
            
            # Calculate preview path
            path = self.engine.pathfinding.a_star(
                (int(self.engine.player.x), int(self.engine.player.y)),
                (gx, gy),
                self.engine.grid
            )
            self.engine.renderer.preview_path = path if path else []
        else:
            self.engine.renderer.hover_tile = None
            self.engine.renderer.preview_path = []

