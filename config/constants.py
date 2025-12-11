"""
Color constants and game state definitions for Solo Leveling game.
"""

# --- Color Constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
UI_BG = (30, 30, 40, 200)  # Dark Blue-Grey with alpha
GRAY = (128, 128, 128)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (200, 200, 0)
CYAN = (0, 200, 200)

# --- Game State Constants ---
class GameState:
    """Game state enumeration."""
    MAIN_MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    LEVEL_COMPLETE = 'level_complete'
    GAME_OVER = 'game_over'
    VICTORY = 'victory'
