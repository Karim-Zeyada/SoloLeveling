"""
Shadow selection menu UI.
"""
import pygame
from config.settings import SHADOW_TYPES, RESPONSIVE_SCALE
from config.constants import CYAN, WHITE, YELLOW, RED

class ShadowMenu:
    """Shadow selection menu overlay."""
    
    def __init__(self, assets, font, small_font, large_font):
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.large_font = large_font
        self.active = False
        self.shadow_options = list(SHADOW_TYPES.keys())
        self.selected_index = 0
    
    def open(self):
        """Open shadow menu."""
        self.active = True
        self.selected_index = 0
    
    def close(self):
        """Close shadow menu."""
        self.active = False
    
    def handle_input(self, key, player, shadows, sound_manager):
        """Handle keyboard input in shadow menu."""
        if not self.active:
            return
        
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.selected_index = (self.selected_index - 1) % len(self.shadow_options)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.selected_index = (self.selected_index + 1) % len(self.shadow_options)
        elif key == pygame.K_UP or key == pygame.K_w:
            self.selected_index = (self.selected_index - 1) % len(self.shadow_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_index = (self.selected_index + 1) % len(self.shadow_options)
        elif key == pygame.K_RETURN:
            selected_type = self.shadow_options[self.selected_index]
            type_config = SHADOW_TYPES[selected_type]
            if player.resources >= type_config['cost']:
                player.resources -= type_config['cost']
                # Import here to avoid circular dependency
                from entities import Shadow
                shadow = Shadow(int(player.x), int(player.y), shadow_type=selected_type)
                shadows.append(shadow)
                sound_manager.play('build')
            self.close()
        elif key == pygame.K_ESCAPE:
            self.close()
    
    def render(self, screen, screen_width, screen_height, player_resources):
        """Render shadow selection menu overlay with visual cards."""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu title
        title_text = self.large_font.render("SELECT YOUR SHADOW", True, CYAN)
        menu_center_x = screen_width // 2
        menu_top = int(80 * RESPONSIVE_SCALE)
        screen.blit(title_text, (menu_center_x - title_text.get_width() // 2, menu_top))
        
        # Calculate card layout
        num_shadows = len(self.shadow_options)
        card_width = int(200 * RESPONSIVE_SCALE)
        card_height = int(280 * RESPONSIVE_SCALE)
        spacing = int(30 * RESPONSIVE_SCALE)
        total_width = num_shadows * card_width + (num_shadows - 1) * spacing
        start_x = menu_center_x - total_width // 2
        card_y = menu_top + int(100 * RESPONSIVE_SCALE)
        
        # Draw shadow option cards
        for i, shadow_type in enumerate(self.shadow_options):
            config = SHADOW_TYPES[shadow_type]
            is_selected = (i == self.selected_index)
            is_affordable = player_resources >= config['cost']
            
            card_x = start_x + i * (card_width + spacing)
            
            # Card background with border
            card_color = (50, 50, 80) if not is_selected else (100, 100, 150)
            pygame.draw.rect(screen, card_color, (card_x, card_y, card_width, card_height))
            
            # Glowing border for selected
            if is_selected:
                pygame.draw.rect(screen, CYAN, (card_x, card_y, card_width, card_height), int(4 * RESPONSIVE_SCALE))
            else:
                pygame.draw.rect(screen, WHITE, (card_x, card_y, card_width, card_height), int(2 * RESPONSIVE_SCALE))
            
            # Shadow image
            if shadow_type in self.assets.images:
                shadow_img = self.assets.images[shadow_type]
                # Scale image to fit card
                img_display_size = int(120 * RESPONSIVE_SCALE)
                if shadow_img.get_width() > 0 and shadow_img.get_height() > 0:
                    shadow_scaled = pygame.transform.scale(shadow_img, (img_display_size, img_display_size))
                    
                    # Add scale effect on hover
                    if is_selected:
                        scale_factor = 1.15
                        shadow_scaled = pygame.transform.scale(shadow_img, (int(img_display_size * scale_factor), int(img_display_size * scale_factor)))
                        # Add glow effect
                        glow_surface = pygame.Surface((int(img_display_size * scale_factor + 20), int(img_display_size * scale_factor + 20)), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, (0, 200, 255, 100), (int(img_display_size * scale_factor + 10) // 2, int(img_display_size * scale_factor + 10) // 2), int(img_display_size * scale_factor // 2 + 10))
                        screen.blit(glow_surface, (card_x + card_width // 2 - int(img_display_size * scale_factor + 20) // 2, card_y + int(30 * RESPONSIVE_SCALE) - 10))
                    
                    img_x = card_x + card_width // 2 - shadow_scaled.get_width() // 2
                    img_y = card_y + int(30 * RESPONSIVE_SCALE)
                    screen.blit(shadow_scaled, (img_x, img_y))
            
            # Shadow name
            name_font = self.font if not is_selected else pygame.font.SysFont('Arial', max(18, int(22 * RESPONSIVE_SCALE)), bold=True)
            name_color = YELLOW if is_selected else WHITE
            name_text = name_font.render(config['name'], True, name_color)
            name_x = card_x + card_width // 2 - name_text.get_width() // 2
            name_y = card_y + int(160 * RESPONSIVE_SCALE)
            screen.blit(name_text, (name_x, name_y))
            
            # Cost and Speed
            stat_color = YELLOW if is_affordable else RED
            cost_text = self.small_font.render(f"Cost: {config['cost']}", True, stat_color)
            speed_text = self.small_font.render(f"Speed: {config['speed']}", True, WHITE)
            
            cost_x = card_x + card_width // 2 - cost_text.get_width() // 2
            speed_x = card_x + card_width // 2 - speed_text.get_width() // 2
            screen.blit(cost_text, (cost_x, card_y + int(195 * RESPONSIVE_SCALE)))
            screen.blit(speed_text, (speed_x, card_y + int(220 * RESPONSIVE_SCALE)))
            
            # Disabled indicator
            if not is_affordable:
                disabled_text = self.small_font.render("INSUFFICIENT", True, RED)
                disabled_x = card_x + card_width // 2 - disabled_text.get_width() // 2
                screen.blit(disabled_text, (disabled_x, card_y + int(245 * RESPONSIVE_SCALE)))
        
        # Instructions
        instr_y = card_y + card_height + int(40 * RESPONSIVE_SCALE)
        instr_text = self.small_font.render("← → Navigate | ENTER Select | ESC Cancel", True, CYAN)
        screen.blit(instr_text, (menu_center_x - instr_text.get_width() // 2, instr_y))
