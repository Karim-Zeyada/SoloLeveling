"""
HUD (Heads-Up Display) for game information.
Enhanced with modern visual styling.
"""
import pygame
import math
import time
from config.settings import MAX_LEVELS, RESPONSIVE_SCALE, SHADOW_TYPES
from config.constants import WHITE, CYAN


class HUD:
    """Displays game information on screen with enhanced visuals."""
    
    # Color palette
    BG_COLOR = (15, 20, 30, 200)
    BORDER_COLOR = (0, 180, 200)
    TEXT_PRIMARY = (220, 230, 240)
    TEXT_SECONDARY = (140, 160, 180)
    TEXT_ACCENT = (0, 220, 255)
    TEXT_WARNING = (255, 200, 100)
    
    def __init__(self, font):
        self.font = font
        self.start_time = time.time()
        
        # Create custom fonts
        try:
            self.title_font = pygame.font.SysFont('Consolas', max(18, int(22 * RESPONSIVE_SCALE)), bold=True)
            self.body_font = pygame.font.SysFont('Consolas', max(14, int(16 * RESPONSIVE_SCALE)))
            self.small_font = pygame.font.SysFont('Consolas', max(12, int(14 * RESPONSIVE_SCALE)))
        except:
            self.title_font = self.font
            self.body_font = self.font
            self.small_font = self.font
    
    def render(self, screen, current_level, player, shadows, level_time):
        """Render enhanced HUD with game stats and controls."""
        padding = 12
        line_height = max(22, int(26 * RESPONSIVE_SCALE))
        
        # Calculate HUD dimensions
        hud_width = max(320, int(380 * RESPONSIVE_SCALE))
        hud_height = 6 * line_height + padding * 2 + 30
        hud_x = 10
        hud_y = 10
        
        # Draw HUD background
        hud_surf = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, self.BG_COLOR, (0, 0, hud_width, hud_height), border_radius=8)
        pygame.draw.rect(hud_surf, self.BORDER_COLOR, (0, 0, hud_width, hud_height), 2, border_radius=8)
        
        # Accent line at top
        pygame.draw.line(hud_surf, self.TEXT_ACCENT, (10, 4), (60, 4), 2)
        
        screen.blit(hud_surf, (hud_x, hud_y))
        
        # Text rendering
        y = hud_y + padding + 5
        
        # Level info (title style)
        level_text = f"LEVEL {current_level} / {MAX_LEVELS}"
        level_surf = self.title_font.render(level_text, True, self.TEXT_ACCENT)
        screen.blit(level_surf, (hud_x + padding, y))
        y += line_height + 5
        
        # Separator line
        pygame.draw.line(screen, (50, 60, 80), 
                        (hud_x + padding, y - 2), 
                        (hud_x + hud_width - padding, y - 2), 1)
        y += 8
        
        # Resources
        res_label = self.small_font.render("RESOURCES:", True, self.TEXT_SECONDARY)
        res_value = self.body_font.render(str(player.resources), True, self.TEXT_PRIMARY)
        screen.blit(res_label, (hud_x + padding, y))
        screen.blit(res_value, (hud_x + padding + 90, y))
        y += line_height
        
        # Shadows
        shadow_names = ', '.join([SHADOW_TYPES[s.shadow_type]['name'] for s in shadows]) if shadows else 'None'
        shd_label = self.small_font.render("SHADOWS:", True, self.TEXT_SECONDARY)
        shd_value = self.body_font.render(shadow_names[:20], True, self.TEXT_PRIMARY if shadows else self.TEXT_SECONDARY)
        screen.blit(shd_label, (hud_x + padding, y))
        screen.blit(shd_value, (hud_x + padding + 90, y))
        y += line_height
        
        # Time
        time_label = self.small_font.render("TIME:", True, self.TEXT_SECONDARY)
        time_value = self.body_font.render(f"{int(level_time)}s", True, self.TEXT_PRIMARY)
        screen.blit(time_label, (hud_x + padding, y))
        screen.blit(time_value, (hud_x + padding + 90, y))
        y += line_height + 10
        
        # Controls section
        pygame.draw.line(screen, (50, 60, 80), 
                        (hud_x + padding, y - 2), 
                        (hud_x + hud_width - padding, y - 2), 1)
        y += 8
        
        controls1 = "ARROWS: Move  |  SPACE: Scan"
        controls2 = "B: Wall  |  T: Trap  |  R: Arise"
        
        ctrl1_surf = self.small_font.render(controls1, True, self.TEXT_SECONDARY)
        ctrl2_surf = self.small_font.render(controls2, True, self.TEXT_SECONDARY)
        screen.blit(ctrl1_surf, (hud_x + padding, y))
        screen.blit(ctrl2_surf, (hud_x + padding, y + line_height - 5))
