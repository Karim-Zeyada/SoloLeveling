"""
Menu screens (main menu, game over, victory, etc.).
Enhanced with modern visual design.
"""
import pygame
import math
import time
from config.settings import GAME_TITLE, GAME_STORY, RESPONSIVE_SCALE
from config.constants import CYAN, WHITE, GREEN, YELLOW, RED


class MenuScreens:
    """Handles all menu screen rendering with enhanced visuals."""
    
    # Color palette
    DARK_BG = (15, 15, 25)
    DARKER_BG = (8, 8, 15)
    ACCENT_CYAN = (0, 220, 255)
    ACCENT_PURPLE = (150, 100, 255)
    GLOW_CYAN = (0, 255, 255)
    TEXT_DIM = (120, 120, 140)
    TEXT_BRIGHT = (220, 220, 240)
    SUCCESS_GREEN = (80, 255, 120)
    DANGER_RED = (255, 80, 100)
    GOLD = (255, 215, 0)
    
    def __init__(self, font, large_font):
        self.font = font
        self.large_font = large_font
        self.start_time = time.time()
        
        # Create custom fonts - use larger base sizes for readability
        try:
            # Title: 56-72pt, Subtitle: 20-24pt, Body: 18-22pt, Button: 24-28pt
            self.title_font = pygame.font.SysFont('Consolas', max(56, int(72 * RESPONSIVE_SCALE)), bold=True)
            self.subtitle_font = pygame.font.SysFont('Consolas', max(20, int(24 * RESPONSIVE_SCALE)))
            self.body_font = pygame.font.SysFont('Consolas', max(18, int(22 * RESPONSIVE_SCALE)))
            self.button_font = pygame.font.SysFont('Consolas', max(24, int(28 * RESPONSIVE_SCALE)), bold=True)
        except:
            self.title_font = self.large_font
            self.subtitle_font = self.font
            self.body_font = self.font
            self.button_font = self.font
    
    def _get_time(self) -> float:
        """Get elapsed time for animations."""
        return time.time() - self.start_time
    
    def _draw_gradient_bg(self, screen, screen_width, screen_height):
        """Draw a gradient background."""
        for y in range(0, screen_height, 4):
            ratio = y / screen_height
            r = int(self.DARK_BG[0] * (1 - ratio) + self.DARKER_BG[0] * ratio)
            g = int(self.DARK_BG[1] * (1 - ratio) + self.DARKER_BG[1] * ratio)
            b = int(self.DARK_BG[2] * (1 - ratio) + self.DARKER_BG[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen_width, y))
    
    def _draw_grid_lines(self, screen, screen_width, screen_height):
        """Draw subtle tech grid lines."""
        t = self._get_time()
        grid_color = (30, 30, 50, 50)
        spacing = 40
        
        surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Horizontal lines
        for y in range(0, screen_height, spacing):
            alpha = int(20 + 10 * math.sin(t * 0.5 + y * 0.01))
            pygame.draw.line(surf, (30, 30, 50, alpha), (0, y), (screen_width, y), 1)
        
        # Vertical lines
        for x in range(0, screen_width, spacing):
            alpha = int(20 + 10 * math.sin(t * 0.5 + x * 0.01))
            pygame.draw.line(surf, (30, 30, 50, alpha), (x, 0), (x, screen_height), 1)
        
        screen.blit(surf, (0, 0))
    
    def _draw_glow_text(self, screen, text, font, color, glow_color, pos, center=True):
        """Draw text with a glow effect."""
        # Render glow
        glow_surf = font.render(text, True, glow_color)
        
        # Create blur effect by blitting multiple times with alpha
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2), (0, 3), (0, -3), (3, 0), (-3, 0)]:
            glow_rect = glow_surf.get_rect()
            if center:
                glow_rect.center = (pos[0] + offset[0], pos[1] + offset[1])
            else:
                glow_rect.topleft = (pos[0] + offset[0], pos[1] + offset[1])
            
            alpha_surf = glow_surf.copy()
            alpha_surf.set_alpha(30)
            screen.blit(alpha_surf, glow_rect)
        
        # Render main text
        main_surf = font.render(text, True, color)
        main_rect = main_surf.get_rect()
        if center:
            main_rect.center = pos
        else:
            main_rect.topleft = pos
        screen.blit(main_surf, main_rect)
    
    def _draw_animated_button(self, screen, text, pos, screen_width):
        """Draw an animated pulsing button."""
        t = self._get_time()
        pulse = 0.7 + 0.3 * math.sin(t * 3)
        
        # Button colors with pulse
        btn_color = (
            int(0 + 80 * pulse),
            int(180 * pulse),
            int(200 * pulse)
        )
        
        text_surf = self.button_font.render(text, True, btn_color)
        text_rect = text_surf.get_rect(center=pos)
        
        # Draw bracket decorations
        bracket_color = (0, int(150 * pulse), int(180 * pulse))
        bracket_width = text_rect.width + 60
        bracket_height = text_rect.height + 20
        
        # Left bracket
        pygame.draw.lines(screen, bracket_color, False, [
            (pos[0] - bracket_width // 2, pos[1] - 5),
            (pos[0] - bracket_width // 2, pos[1] - bracket_height // 2),
            (pos[0] - bracket_width // 2 + 15, pos[1] - bracket_height // 2),
        ], 2)
        pygame.draw.lines(screen, bracket_color, False, [
            (pos[0] - bracket_width // 2, pos[1] + 5),
            (pos[0] - bracket_width // 2, pos[1] + bracket_height // 2),
            (pos[0] - bracket_width // 2 + 15, pos[1] + bracket_height // 2),
        ], 2)
        
        # Right bracket
        pygame.draw.lines(screen, bracket_color, False, [
            (pos[0] + bracket_width // 2, pos[1] - 5),
            (pos[0] + bracket_width // 2, pos[1] - bracket_height // 2),
            (pos[0] + bracket_width // 2 - 15, pos[1] - bracket_height // 2),
        ], 2)
        pygame.draw.lines(screen, bracket_color, False, [
            (pos[0] + bracket_width // 2, pos[1] + 5),
            (pos[0] + bracket_width // 2, pos[1] + bracket_height // 2),
            (pos[0] + bracket_width // 2 - 15, pos[1] + bracket_height // 2),
        ], 2)
        
        screen.blit(text_surf, text_rect)
    
    def _draw_scanlines(self, screen, screen_width, screen_height):
        """Draw subtle CRT scanline effect."""
        surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for y in range(0, screen_height, 3):
            pygame.draw.line(surf, (0, 0, 0, 20), (0, y), (screen_width, y), 1)
        screen.blit(surf, (0, 0))
    
    def render_main_menu(self, screen, screen_width, screen_height):
        """Render enhanced main menu."""
        # Background
        self._draw_gradient_bg(screen, screen_width, screen_height)
        self._draw_grid_lines(screen, screen_width, screen_height)
        
        center_x = screen_width // 2
        t = self._get_time()
        
        # Animated title with glow
        title_y = int(80 * RESPONSIVE_SCALE) + int(5 * math.sin(t * 1.5))
        self._draw_glow_text(
            screen, GAME_TITLE, self.title_font,
            self.ACCENT_CYAN, (0, 100, 150),
            (center_x, title_y)
        )
        
        # Subtitle line
        subtitle = "[ INFILTRATION PROTOCOL ACTIVE ]"
        sub_color = (int(80 + 40 * math.sin(t * 2)), 100, 120)
        sub_surf = self.subtitle_font.render(subtitle, True, sub_color)
        sub_rect = sub_surf.get_rect(center=(center_x, title_y + 60))
        screen.blit(sub_surf, sub_rect)
        
        # Decorative line under title
        line_width = int(300 * RESPONSIVE_SCALE)
        line_y = title_y + 70
        pygame.draw.line(screen, (40, 60, 80), 
                        (center_x - line_width // 2, line_y),
                        (center_x + line_width // 2, line_y), 1)
        
        # Animated accent on the line
        accent_x = center_x - line_width // 2 + int((line_width) * ((t * 0.3) % 1.0))
        pygame.draw.circle(screen, self.ACCENT_CYAN, (accent_x, line_y), 3)
        
        # Story text in a styled box
        story_lines = GAME_STORY.strip().split('\n')
        box_padding = 25
        line_height = max(28, int(32 * RESPONSIVE_SCALE))  # Larger line height
        box_height = len(story_lines) * line_height + box_padding * 2
        box_y = int(220 * RESPONSIVE_SCALE) + 50  # Move down to avoid overlap
        box_width = max(650, int(700 * RESPONSIVE_SCALE))  # Wider box
        
        # Draw story box background
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (20, 25, 35, 180), (0, 0, box_width, box_height), border_radius=5)
        pygame.draw.rect(box_surf, (50, 60, 80), (0, 0, box_width, box_height), 1, border_radius=5)
        screen.blit(box_surf, (center_x - box_width // 2, box_y))
        
        # Story text
        y = box_y + box_padding
        for i, line in enumerate(story_lines):
            # Fade in effect based on index
            alpha = min(255, int(255 * (1 - i * 0.05)))
            color = (
                int(self.TEXT_BRIGHT[0] * (alpha / 255)),
                int(self.TEXT_BRIGHT[1] * (alpha / 255)),
                int(self.TEXT_BRIGHT[2] * (alpha / 255))
            )
            text = self.body_font.render(line, True, color)
            screen.blit(text, (center_x - box_width // 2 + box_padding, y))
            y += line_height
        
        # Animated start button
        button_y = screen_height - int(80 * RESPONSIVE_SCALE)
        self._draw_animated_button(screen, "PRESS ENTER TO START", (center_x, button_y), screen_width)
        
        # Version/credits at bottom
        version = "v1.0 // Digital Architect"
        ver_surf = self.subtitle_font.render(version, True, self.TEXT_DIM)
        screen.blit(ver_surf, (10, screen_height - 25))
        
        # Scanline effect
        self._draw_scanlines(screen, screen_width, screen_height)
    
    def render_paused_overlay(self, screen, screen_width, screen_height):
        """Render enhanced pause overlay."""
        # Dark overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Paused title with glow
        self._draw_glow_text(
            screen, "PAUSED", self.title_font,
            self.GOLD, (100, 80, 0),
            (center_x, center_y - 50)
        )
        
        # Resume prompt
        self._draw_animated_button(screen, "PRESS ESC TO RESUME", (center_x, center_y + 50), screen_width)
    
    def render_level_complete(self, screen, screen_width, screen_height, level_time, player_resources):
        """Render enhanced level complete screen."""
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 20, 0, 200))
        screen.blit(overlay, (0, 0))
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Title with glow
        self._draw_glow_text(
            screen, "LEVEL COMPLETE", self.title_font,
            self.SUCCESS_GREEN, (0, 100, 50),
            (center_x, center_y - 80)
        )
        
        # Stats
        stats_text = f"Time: {int(level_time)}s  |  Resources: {player_resources}"
        stats_surf = self.button_font.render(stats_text, True, self.TEXT_BRIGHT)
        stats_rect = stats_surf.get_rect(center=(center_x, center_y))
        screen.blit(stats_surf, stats_rect)
        
        # Continue button
        self._draw_animated_button(screen, "PRESS ENTER TO CONTINUE", (center_x, center_y + 80), screen_width)
    
    def render_game_over(self, screen, screen_width, screen_height):
        """Render enhanced game over screen."""
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((20, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Title with glow
        self._draw_glow_text(
            screen, "DETECTED", self.title_font,
            self.DANGER_RED, (100, 0, 0),
            (center_x, center_y - 60)
        )
        
        # Message
        msg = "Security protocols activated. Connection terminated."
        msg_surf = self.body_font.render(msg, True, self.TEXT_DIM)
        msg_rect = msg_surf.get_rect(center=(center_x, center_y + 10))
        screen.blit(msg_surf, msg_rect)
        
        # Retry button
        self._draw_animated_button(screen, "PRESS ENTER TO RETRY", (center_x, center_y + 80), screen_width)
    
    def render_victory(self, screen, screen_width, screen_height):
        """Render enhanced victory screen."""
        # Gradient overlay
        self._draw_gradient_bg(screen, screen_width, screen_height)
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        t = self._get_time()
        
        # Animated victory text
        title_y = center_y - 60 + int(8 * math.sin(t * 2))
        self._draw_glow_text(
            screen, "VICTORY", self.title_font,
            self.GOLD, (150, 120, 0),
            (center_x, title_y)
        )
        
        # Success message
        msg = "System Override Complete. Network Access Granted."
        msg_surf = self.body_font.render(msg, True, self.SUCCESS_GREEN)
        msg_rect = msg_surf.get_rect(center=(center_x, center_y + 20))
        screen.blit(msg_surf, msg_rect)
        
        # Restart button
        self._draw_animated_button(screen, "PRESS ENTER TO RESTART", (center_x, center_y + 100), screen_width)
