"""
Asset manager for loading and managing game assets.
"""
import pygame
import sys
from config.settings import TILE_WIDTH, TILE_HEIGHT

class AssetManager:
    """Manages loading and storage of game assets (images)."""
    
    def __init__(self):
        self.images = {}
        try:
            # Try to load with new asset names first, fall back to iso_ prefix if not found
            asset_files = {
                'floor': ['floor.png', 'iso_floor.png'],
                'wall': ['wall.png', 'iso_wall.png'],
                'player': ['player.png', 'iso_player.png'],
                'enemy': ['enemy.png', 'iso_enemy.png'],
                'elf': ['elf.png', 'elf.png'],                # Elf enemy asset
                'alpha_bear': ['alpha_bear.png', 'alpha_bear.png'],  # Alpha Bear enemy asset
                'trap': ['trap.png', 'iso_trap.png'],
                'resource': ['resource.png', 'iso_resource.png'],
                'exit': ['exit.png', 'iso_exit.png'],
                'shadow': ['shadow.png', 'shadow.png'],  # Base shadow asset
                'igris': ['igris.png', 'igris.png'],      # Igris shadow asset
                'beru': ['beru.png', 'beru.png'],          # Beru shadow asset
                'trap_bind': ['trap_bind.png', 'trap_bind.png'],
                'trap_spike': ['trap_spike.png', 'trap_spike.png'],
                'trap_gravity': ['trap_gravity.png', 'trap_gravity.png.png'],
            }
            
            # Load images with fallback
            for key, file_list in asset_files.items():
                loaded = False
                for filename in file_list:
                    try:
                        self.images[key] = pygame.image.load(f'assets/{filename}').convert_alpha()
                        loaded = True
                        break
                    except:
                        continue
                if not loaded:
                    print(f"WARNING: Could not load {key} asset")
            
            # Simple fog texture (semi-transparent black diamond)
            self.fog_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT * 2), pygame.SRCALPHA)
            pygame.draw.polygon(self.fog_surf, (0, 0, 0, 230), [
                (TILE_WIDTH // 2, 0),
                (TILE_WIDTH, TILE_HEIGHT // 2),
                (TILE_WIDTH // 2, TILE_HEIGHT),
                (0, TILE_HEIGHT // 2)
            ])
            
        except Exception as e:
            print(f"ERROR LOADING ASSETS: {e}")
            print("Make sure you have the 'assets' folder with image files.")
            sys.exit()
