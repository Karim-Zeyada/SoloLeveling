"""
Main isometric renderer for the game.
"""
import pygame
from config.settings import TILE_WIDTH, TILE_HEIGHT, ELEVATION_OFFSET, CAMERA_ZOOM, RESPONSIVE_SCALE
from config.constants import RED, GREEN, WHITE, CYAN

class Renderer:
    """Handles all isometric rendering for the game."""
    
    def __init__(self, assets):
        self.assets = assets
        self.hover_tile: tuple[int, int] | None = None
        self.preview_path: list[tuple[int, int]] = []  # Path preview tiles
    
    def render_game(self, screen, grid, player, enemies, shadows, camera, screen_width, screen_height):
        """Render the main game viewport."""
        world_offset = camera.get_world_offset(screen_width, screen_height)
        
        # Render tiles
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                iso_x, iso_y = camera.cart_to_iso(x, y)
                sx = iso_x + world_offset[0] + camera.x
                sy = iso_y + world_offset[1] + camera.y
                
                # Draw floor
                self._render_floor(screen, sx, sy)
                
                # Draw objects if visible
                if tile.visible:
                    self._render_tile_object(screen, tile, sx, sy)
                    
                    # Draw entity paths (debug)
                    for enemy in enemies:
                        if (x, y) in enemy.path:
                            pts = [(sx + 32, sy), (sx + 64, sy + 16), (sx + 32, sy + 32), (sx, sy + 16)]
                            pygame.draw.polygon(screen, (255, 0, 0, 100), pts, 2)
                
                # Draw entities
                if tile.visible:
                    # Draw player
                    if int(round(player.x)) == x and int(round(player.y)) == y:
                        self._render_player(screen, player, camera, world_offset, sx, sy)
                    
                    # Draw enemies
                    for enemy in enemies:
                        if enemy.x == x and enemy.y == y:
                            self._render_enemy(screen, enemy, sx, sy)
                    
                    # Draw shadows
                    for shadow in shadows:
                        if shadow.x == x and shadow.y == y:
                            self._render_shadow(screen, shadow, sx, sy)
                
                # Fog of war
                if not tile.visible:
                    self._render_fog(screen, sx, sy)
                
                # Hover highlight
                if self.hover_tile and self.hover_tile == (x, y):
                    self._render_hover_highlight(screen, sx, sy)
                
                # Path preview
                if (x, y) in self.preview_path:
                    self._render_path_preview(screen, sx, sy)
    
    def _render_floor(self, screen, sx, sy):
        """Render floor tile."""
        floor_img = self.assets.images['floor']
        floor_scaled_width = int(floor_img.get_width() * CAMERA_ZOOM)
        floor_scaled_height = int(floor_img.get_height() * CAMERA_ZOOM)
        if floor_scaled_width > 0 and floor_scaled_height > 0:
            floor_scaled = pygame.transform.scale(floor_img, (floor_scaled_width, floor_scaled_height))
            screen.blit(floor_scaled, (sx, sy))
    
    def _render_hover_highlight(self, screen, sx, sy):
        """Render hover highlight on a tile."""
        # Create isometric diamond shape
        half_w = int(TILE_WIDTH * CAMERA_ZOOM / 2)
        half_h = int(TILE_HEIGHT * CAMERA_ZOOM / 2)
        center_x = sx + half_w
        center_y = sy + half_h
        
        points = [
            (center_x, center_y - half_h),  # Top
            (center_x + half_w, center_y),   # Right
            (center_x, center_y + half_h),   # Bottom
            (center_x - half_w, center_y),   # Left
        ]
        
        # Draw filled highlight with transparency
        highlight_surf = pygame.Surface((half_w * 2, half_h * 2), pygame.SRCALPHA)
        local_points = [
            (half_w, 0),
            (half_w * 2, half_h),
            (half_w, half_h * 2),
            (0, half_h),
        ]
        pygame.draw.polygon(highlight_surf, (255, 255, 0, 60), local_points)
        pygame.draw.polygon(highlight_surf, (255, 255, 0, 200), local_points, 3)
        screen.blit(highlight_surf, (center_x - half_w, center_y - half_h))
    
    def _render_path_preview(self, screen, sx, sy):
        """Render path preview on a tile (cyan diamond)."""
        half_w = int(TILE_WIDTH * CAMERA_ZOOM / 2)
        half_h = int(TILE_HEIGHT * CAMERA_ZOOM / 2)
        center_x = sx + half_w
        center_y = sy + half_h
        
        # Draw filled highlight with transparency
        highlight_surf = pygame.Surface((half_w * 2, half_h * 2), pygame.SRCALPHA)
        local_points = [
            (half_w, 0),
            (half_w * 2, half_h),
            (half_w, half_h * 2),
            (0, half_h),
        ]
        pygame.draw.polygon(highlight_surf, (0, 200, 255, 40), local_points)
        pygame.draw.polygon(highlight_surf, (0, 200, 255, 150), local_points, 2)
        screen.blit(highlight_surf, (center_x - half_w, center_y - half_h))
    
    def _render_tile_object(self, screen, tile, sx, sy):
        """Render tile objects (wall, trap, resource, exit)."""
        img = None
        offset_y = 0
        
        if tile.type == 'wall':
            img = self.assets.images['wall']
            offset_y = int(ELEVATION_OFFSET * CAMERA_ZOOM)
        elif tile.type == 'trap':
            trap_key = tile.trap_type if tile.trap_type else 'trap_spike'
            if trap_key in self.assets.images:
                img = self.assets.images[trap_key]
            else:
                 # Fallback if specific type not loaded
                 img = self.assets.images.get('trap_spike')
        elif tile.type == 'resource':
            img = self.assets.images['resource']
        elif tile.type == 'exit':
            img = self.assets.images['exit']
            offset_y = int(ELEVATION_OFFSET * CAMERA_ZOOM)
        
        if img:
            # Scale image by zoom factor
            scaled_width = int(img.get_width() * CAMERA_ZOOM)
            scaled_height = int(img.get_height() * CAMERA_ZOOM)
            if scaled_width > 0 and scaled_height > 0:
                img_scaled = pygame.transform.scale(img, (scaled_width, scaled_height))
                screen.blit(img_scaled, (sx, sy - offset_y))
    
    def _render_player(self, screen, player, camera, world_offset, sx, sy):
        """Render player with smooth interpolation."""
        if player.moving:
            psx0, psy0 = camera.cart_to_iso(*player.move_start)
            psx1, psy1 = camera.cart_to_iso(*player.move_target)
            plerp = max(0.0, min(1.0, player.move_progress))
            p_iso_x = psx0 + (psx1 - psx0) * plerp
            p_iso_y = psy0 + (psy1 - psy0) * plerp
            p_sx = p_iso_x + world_offset[0] + camera.x
            p_sy = p_iso_y + world_offset[1] + camera.y
        else:
            p_sx = sx
            p_sy = sy
        
        if abs(p_sx - sx) < TILE_WIDTH and abs(p_sy - sy) < TILE_HEIGHT * 2:
            player_img = self.assets.images['player']
            p_scaled_width = int(player_img.get_width() * CAMERA_ZOOM)
            p_scaled_height = int(player_img.get_height() * CAMERA_ZOOM)
            if p_scaled_width > 0 and p_scaled_height > 0:
                player_scaled = pygame.transform.scale(player_img, (p_scaled_width, p_scaled_height))
                screen.blit(player_scaled, (p_sx, p_sy - int(ELEVATION_OFFSET * CAMERA_ZOOM)))
    
    def _render_enemy(self, screen, enemy, sx, sy):
        """Render enemy with health bar."""
        enemy_asset_key = enemy.asset_key
        if enemy_asset_key in self.assets.images:
            enemy_img = self.assets.images[enemy_asset_key]
            e_scaled_width = int(enemy_img.get_width() * CAMERA_ZOOM)
            e_scaled_height = int(enemy_img.get_height() * CAMERA_ZOOM)
            if e_scaled_width > 0 and e_scaled_height > 0:
                enemy_scaled = pygame.transform.scale(enemy_img, (e_scaled_width, e_scaled_height))
                screen.blit(enemy_scaled, (sx, sy - int(ELEVATION_OFFSET * CAMERA_ZOOM)))
                
                # Draw health bar above enemy
                health_percent = max(0, enemy.health / enemy.max_health)
                bar_width = int(e_scaled_width * 0.8)
                bar_height = int(6 * RESPONSIVE_SCALE)
                bar_x = sx + e_scaled_width // 2 - bar_width // 2
                bar_y = sy - int(ELEVATION_OFFSET * CAMERA_ZOOM) - int(15 * RESPONSIVE_SCALE)
                
                # Background (red)
                pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
                # Health (green)
                pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_percent), bar_height))
                # Border
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _render_shadow(self, screen, shadow, sx, sy):
        """Render shadow with health bar."""
        shadow_asset_key = shadow.asset_key
        if shadow_asset_key in self.assets.images:
            shadow_img = self.assets.images[shadow_asset_key]
            s_scaled_width = int(shadow_img.get_width() * CAMERA_ZOOM)
            s_scaled_height = int(shadow_img.get_height() * CAMERA_ZOOM)
            if s_scaled_width > 0 and s_scaled_height > 0:
                shadow_scaled = pygame.transform.scale(shadow_img, (s_scaled_width, s_scaled_height))
                screen.blit(shadow_scaled, (sx, sy - int(ELEVATION_OFFSET * CAMERA_ZOOM)))
                
                # Draw shadow health bar
                health_percent = max(0, shadow.health / shadow.max_health)
                bar_width = int(s_scaled_width * 0.8)
                bar_height = int(6 * RESPONSIVE_SCALE)
                bar_x = sx + s_scaled_width // 2 - bar_width // 2
                bar_y = sy - int(ELEVATION_OFFSET * CAMERA_ZOOM) - int(15 * RESPONSIVE_SCALE)
                
                # Background (red)
                pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
                # Health (cyan for shadow)
                pygame.draw.rect(screen, CYAN, (bar_x, bar_y, int(bar_width * health_percent), bar_height))
                # Border
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _render_fog(self, screen, sx, sy):
        """Render fog of war."""
        fog_scaled_width = int(self.assets.fog_surf.get_width() * CAMERA_ZOOM)
        fog_scaled_height = int(self.assets.fog_surf.get_height() * CAMERA_ZOOM)
        if fog_scaled_width > 0 and fog_scaled_height > 0:
            fog_scaled = pygame.transform.scale(self.assets.fog_surf, (fog_scaled_width, fog_scaled_height))
            screen.blit(fog_scaled, (sx, sy))
