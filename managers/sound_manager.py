"""
Sound manager for game audio effects.
"""
import pygame

class SoundManager:
    """Manages sound effects for the game."""
    
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        try:
            # Try to load sound files; gracefully skip if missing
            if pygame.mixer.get_init():
                self.sounds['move'] = pygame.mixer.Sound('assets/move.wav')
                self.sounds['collect'] = pygame.mixer.Sound('assets/collect.wav')
                self.sounds['build'] = pygame.mixer.Sound('assets/build.wav')
        except Exception as e:
            print(f"Note: Sound files not found ({e}), continuing without sounds.")
    
    def play(self, sound_name):
        """Play a sound if available."""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
