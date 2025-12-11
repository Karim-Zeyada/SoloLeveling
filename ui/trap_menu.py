"""
Trap selection menu UI.
"""
import pygame
from config.settings import TRAP_TYPES, RESPONSIVE_SCALE
from config.constants import CYAN, WHITE, YELLOW, RED

class TrapMenu:
    """Trap selection menu overlay."""
    
    def __init__(self, assets, font, small_font, large_font):
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.large_font = large_font
        self.active = False
        self.trap_options = list(TRAP_TYPES.keys())
        self.selected_index = 0
        # Callback for building, set by game state
        self.on_build_callback = None
    
    def open(self):
        """Open trap menu."""
        self.active = True
        self.selected_index = 0
    
    def close(self):
        """Close trap menu."""
        self.active = False
    
    def handle_input(self, key, player, sound_manager):
        """Handle keyboard input in trap menu."""
        if not self.active:
            return
        
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.selected_index = (self.selected_index - 1) % len(self.trap_options)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.selected_index = (self.selected_index + 1) % len(self.trap_options)
        elif key == pygame.K_UP or key == pygame.K_w:
            self.selected_index = (self.selected_index - 1) % len(self.trap_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_index = (self.selected_index + 1) % len(self.trap_options)
        elif key == pygame.K_RETURN:
            self.select_trap(player, sound_manager)
        elif key == pygame.K_ESCAPE:
            self.close()
            
    def select_trap(self, player, sound_manager):
        """Attempt to select and build current trap."""
        selected_type = self.trap_options[self.selected_index]
        type_config = TRAP_TYPES[selected_type]
        
        if player.resources >= type_config['cost']:
            # Signal to game state to build this trap
            if self.on_build_callback:
                # We pass the type back to the caller
                success = self.on_build_callback(selected_type)
                if success:
                    player.resources -= type_config['cost']
                    sound_manager.play('build')
                    self.close()
                else:
                    # Could not build (e.g. invalid tile)
                    pass
        else:
            # Play error sound?
            pass
    
    def render(self, screen, screen_width, screen_height, player_resources):
        """Render trap selection menu overlay."""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu title
        title_text = self.large_font.render("SELECT TRAP", True, CYAN)
        menu_center_x = screen_width // 2
        menu_top = int(80 * RESPONSIVE_SCALE)
        screen.blit(title_text, (menu_center_x - title_text.get_width() // 2, menu_top))
        
        # Calculate card layout
        num_options = len(self.trap_options)
        card_width = int(200 * RESPONSIVE_SCALE)
        card_height = int(280 * RESPONSIVE_SCALE)
        spacing = int(30 * RESPONSIVE_SCALE)
        total_width = num_options * card_width + (num_options - 1) * spacing
        start_x = menu_center_x - total_width // 2
        card_y = menu_top + int(100 * RESPONSIVE_SCALE)
        
        # Draw trap option cards
        for i, trap_type in enumerate(self.trap_options):
            config = TRAP_TYPES[trap_type]
            is_selected = (i == self.selected_index)
            is_affordable = player_resources >= config['cost']
            
            card_x = start_x + i * (card_width + spacing)
            
            # Card background
            card_color = (50, 50, 80) if not is_selected else (100, 100, 150)
            pygame.draw.rect(screen, card_color, (card_x, card_y, card_width, card_height))
            
            # Border
            if is_selected:
                pygame.draw.rect(screen, CYAN, (card_x, card_y, card_width, card_height), int(4 * RESPONSIVE_SCALE))
            else:
                pygame.draw.rect(screen, WHITE, (card_x, card_y, card_width, card_height), int(2 * RESPONSIVE_SCALE))
            
            # Trap image
            if trap_type in self.assets.images:
                img = self.assets.images[trap_type]
                # Scale image
                img_display_size = int(100 * RESPONSIVE_SCALE)
                if img.get_width() > 0:
                    scaled = pygame.transform.scale(img, (img_display_size, img_display_size))
                    
                    if is_selected:
                        # Scale up
                        scale_factor = 1.15
                        scaled = pygame.transform.scale(img, (int(img_display_size * scale_factor), int(img_display_size * scale_factor)))
                    
                    img_x = card_x + card_width // 2 - scaled.get_width() // 2
                    img_y = card_y + int(30 * RESPONSIVE_SCALE)
                    screen.blit(scaled, (img_x, img_y))
            
            # Name
            name_font = self.font if not is_selected else pygame.font.SysFont('Arial', max(18, int(22 * RESPONSIVE_SCALE)), bold=True)
            name_color = YELLOW if is_selected else WHITE
            name_text = name_font.render(config['name'], True, name_color)
            name_x = card_x + card_width // 2 - name_text.get_width() // 2
            name_y = card_y + int(150 * RESPONSIVE_SCALE)
            screen.blit(name_text, (name_x, name_y))
            
            # Stats (Damage/Effect)
            effect_text_str = f"Effect: {config['effect'].title()}"
            effect_text = self.small_font.render(effect_text_str, True, WHITE)
            screen.blit(effect_text, (card_x + int(10 * RESPONSIVE_SCALE), card_y + int(180 * RESPONSIVE_SCALE)))
            
            if config['damage'] > 0:
                dmg_text = self.small_font.render(f"Damage: {config['damage']}", True, WHITE)
                screen.blit(dmg_text, (card_x + int(10 * RESPONSIVE_SCALE), card_y + int(200 * RESPONSIVE_SCALE)))
            elif config['duration'] > 0:
                dur_text = self.small_font.render(f"Duration: {config['duration']}s", True, WHITE)
                screen.blit(dur_text, (card_x + int(10 * RESPONSIVE_SCALE), card_y + int(200 * RESPONSIVE_SCALE)))

            # Cost
            stat_color = YELLOW if is_affordable else RED
            cost_text = self.small_font.render(f"Cost: {config['cost']}", True, stat_color)
            cost_x = card_x + card_width // 2 - cost_text.get_width() // 2
            screen.blit(cost_text, (cost_x, card_y + int(230 * RESPONSIVE_SCALE)))

            # Insufficient
            if not is_affordable:
                disabled_text = self.small_font.render("INSUFFICIENT", True, RED)
                disabled_x = card_x + card_width // 2 - disabled_text.get_width() // 2
                screen.blit(disabled_text, (disabled_x, card_y + int(250 * RESPONSIVE_SCALE)))
        
        # Instructions
        instr_y = card_y + card_height + int(40 * RESPONSIVE_SCALE)
        instr_text = self.small_font.render("← → Navigate | ENTER Select | ESC Cancel", True, CYAN)
        screen.blit(instr_text, (menu_center_x - instr_text.get_width() // 2, instr_y))
