"""
Minimap display for navigation.
"""
import pygame
from config.settings import RESPONSIVE_SCALE
from config.constants import WHITE, RED, GREEN, YELLOW, CYAN

class Minimap:
    """Displays minimap in top-right corner."""
    
    def render(self, screen, grid, player, enemies, screen_width):
        """Render minimap with grid, player, and enemies."""
        minimap_tile_size = max(6, int(20 * RESPONSIVE_SCALE))  # pixels per grid tile
        minimap_padding = int(5 * RESPONSIVE_SCALE)
        minimap_width = grid.width * minimap_tile_size + minimap_padding * 2
        minimap_height = grid.height * minimap_tile_size + minimap_padding * 2
        minimap_x = screen_width - minimap_width - int(10 * RESPONSIVE_SCALE)
        minimap_y = int(10 * RESPONSIVE_SCALE)
        
        # Draw minimap background
        pygame.draw.rect(screen, (40, 40, 50), (minimap_x, minimap_y, minimap_width, minimap_height))
        pygame.draw.rect(screen, WHITE, (minimap_x, minimap_y, minimap_width, minimap_height), 2)
        
        # Draw grid tiles
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                mx = minimap_x + minimap_padding + x * minimap_tile_size
                my = minimap_y + minimap_padding + y * minimap_tile_size
                
                # Color by tile type
                if tile.type == 'wall':
                    color = (100, 100, 100)
                elif tile.type == 'trap':
                    color = RED
                elif tile.type == 'resource':
                    color = GREEN
                elif tile.type == 'exit':
                    color = YELLOW
                else:
                    color = (60, 60, 70)
                
                pygame.draw.rect(screen, color, (mx, my, minimap_tile_size, minimap_tile_size))
        
        # Draw player
        p_mx = minimap_x + minimap_padding + int(player.x) * minimap_tile_size
        p_my = minimap_y + minimap_padding + int(player.y) * minimap_tile_size
        pygame.draw.circle(screen, CYAN, (p_mx + minimap_tile_size // 2, p_my + minimap_tile_size // 2), 3)
        
        # Draw all enemies
        for enemy in enemies:
            e_mx = minimap_x + minimap_padding + enemy.x * minimap_tile_size
            e_my = minimap_y + minimap_padding + enemy.y * minimap_tile_size
            pygame.draw.circle(screen, RED, (e_mx + minimap_tile_size // 2, e_my + minimap_tile_size // 2), 3)
