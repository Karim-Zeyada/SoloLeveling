"""
Configuration settings for Solo Leveling game.
Contains all game constants, registries, and configuration values.
"""
import subprocess

# --- Game Story Context ---
GAME_TITLE = "System Override: Digital Architect"
GAME_STORY = """
You are a rogue AI navigating a corporate firewall.
Collect DATA nodes (resources) to strengthen your presence.
Build FIREWALLS to block SECURITY AGENTS (enemies).
Plant TRAPS to delay pursuers.
Reach the EXIT to access the next system layer.
Complete all levels to escape corporate surveillance.
"""

# --- Screen Configuration ---
# Dynamic screen sizing: use 80% of monitor resolution for windowed mode
try:
    # Try to get monitor resolution on Windows
    result = subprocess.run(['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width'], 
                          capture_output=True, text=True, timeout=2)
    screen_width = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 1920
    result = subprocess.run(['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height'], 
                          capture_output=True, text=True, timeout=2)
    screen_height = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 1080
    
    # Use 80% of screen size for windowed mode (leaves room for taskbar and title bar)
    SCREEN_WIDTH = int(screen_width * 0.8)
    SCREEN_HEIGHT = int(screen_height * 0.8)
except:
    # Fallback to reasonable default
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

# Ensure minimum size
SCREEN_WIDTH = max(1024, SCREEN_WIDTH)
SCREEN_HEIGHT = max(600, SCREEN_HEIGHT)

# Single unified scale factor based on screen size relative to base 1920x1440
RESPONSIVE_SCALE = min(SCREEN_WIDTH / 1920, SCREEN_HEIGHT / 1440)

# --- Game Settings ---
FPS = 60
START_LEVEL = 1
MAX_LEVELS = 5
WINDOW_RESIZABLE = True
WINDOW_FULLSCREEN = False

# --- Isometric Tile Settings ---
# Original high-res assets: 677x369
# Keep at actual asset size - zoom is handled separately
TILE_WIDTH = 677
TILE_HEIGHT = 369
ELEVATION_OFFSET = 150

# --- Camera Settings ---
CAMERA_EASE_SPEED = 0.15  # Lerp factor per frame (0-1, lower = smoother)
CAMERA_ZOOM = 0.25  # Zoom factor: scale the tiles down for visibility

# --- Enemy Type Registry ---
ENEMY_TYPES = {
    'security_agent': {
        'name': 'Security Agent',
        'asset': 'enemy',
        'health': 3,
        'damage': 1,
        'speed': 0.5,
        'detection_range': 8,
        'armor': 0,
        'description': 'Standard security - balanced threat'
    },
    'elf': {
        'name': 'Elf Archer',
        'asset': 'elf',
        'health': 5,
        'damage': 2,
        'speed': 0.35,
        'detection_range': 10,
        'armor': 1,
        'description': 'Strongest enemy - high damage and range'
    },
    'alpha_bear': {
        'name': 'Alpha Bear',
        'asset': 'alpha_bear',
        'health': 7,
        'damage': 1,
        'speed': 0.45,
        'detection_range': 6,
        'armor': 2,
        'description': 'Tanky threat - slow but durable'
    }
}

# --- Shadow Type Registry ---
SHADOW_TYPES = {
    'shadow': {
        'name': 'Shadow Agent',
        'asset': 'shadow',
        'speed': 0.4,
        'cost': 10,
        'health': 5,
        'damage': 2,
        'description': 'Basic shadow servant - loyal companion'
    },
    'igris': {
        'name': 'Igris',
        'asset': 'igris',
        'speed': 0.3,  # Faster than base shadow
        'cost': 25,
        'health': 8,
        'damage': 3,
        'description': 'Elite shadow warrior - swift and deadly'
    },
    'beru': {
        'name': 'Beru',
        'asset': 'beru',
        'speed': 0.35,  # Between shadow and igris
        'cost': 20,
        'health': 6,
        'damage': 2,
        'description': 'Versatile shadow - balanced power'
    }
}

# --- Level Progression Settings ---
LEVEL_CONFIGS = {
    1: {'grid_size': 12, 'start_resources': 15, 'enemies': [('security_agent', 1)], 'resource_count': 3},
    2: {'grid_size': 14, 'start_resources': 12, 'enemies': [('security_agent', 1)], 'resource_count': 4},
    3: {'grid_size': 16, 'start_resources': 10, 'enemies': [('security_agent', 1), ('alpha_bear', 1)], 'resource_count': 5},
    4: {'grid_size': 18, 'start_resources': 8, 'enemies': [('security_agent', 1), ('alpha_bear', 1)], 'resource_count': 6},
    5: {'grid_size': 20, 'start_resources': 5, 'enemies': [('elf', 1), ('alpha_bear', 1), ('security_agent', 1)], 'resource_count': 7},
}

# --- Trap Type Registry ---
TRAP_TYPES = {
    'trap_bind': {
        'name': 'Bind Trap',
        'asset': 'trap_bind',
        'cost': 15,
        'damage': 0,
        'effect': 'freeze',
        'duration': 3.0,
        'description': 'Freezes enemy for 3s'
    },
    'trap_spike': {
        'name': 'Ice Spike',
        'asset': 'trap_spike',
        'cost': 10,
        'damage': 5,
        'effect': 'damage',
        'duration': 0.0,
        'description': 'Deals instant damage'
    },
    'trap_gravity': {
        'name': 'Gravity Well',
        'asset': 'trap_gravity',
        'cost': 20,
        'damage': 1,
        'effect': 'slow',
        'duration': 5.0,
        'description': 'Slows enemies by 50%'
    }
}
