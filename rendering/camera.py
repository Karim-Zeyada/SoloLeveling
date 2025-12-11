"""
Camera system for smooth player tracking.
"""
from config.settings import TILE_WIDTH, TILE_HEIGHT, CAMERA_ZOOM, CAMERA_EASE_SPEED

class Camera:
    """Camera with smooth easing for player tracking."""
    
    def __init__(self):
        # Camera offsets (pixels)
        self.x = 0
        self.y = 0
        # Eased camera targets
        self.target_x = 0
        self.target_y = 0
    
    def cart_to_iso(self, gx, gy):
        """Convert cartesian grid coordinates to isometric world coordinates."""
        iso_x = (gx - gy) * (TILE_WIDTH // 2) * CAMERA_ZOOM
        iso_y = (gx + gy) * (TILE_HEIGHT // 2) * CAMERA_ZOOM
        return iso_x, iso_y
    
    def update(self, player, screen_width, screen_height):
        """Update camera position to follow player smoothly."""
        world_offset = (screen_width // 2, screen_height // 3)
        
        # Calculate player's isometric position (with interpolation if moving)
        if player.moving:
            sx0, sy0 = self.cart_to_iso(*player.move_start)
            sx1, sy1 = self.cart_to_iso(*player.move_target)
            lerp = max(0.0, min(1.0, player.move_progress))
            player_iso_x = sx0 + (sx1 - sx0) * lerp
            player_iso_y = sy0 + (sy1 - sy0) * lerp
        else:
            player_iso_x, player_iso_y = self.cart_to_iso(player.x, player.y)
        
        # Calculate desired camera position to center player
        desired_screen_x = screen_width // 2
        desired_screen_y = screen_height // 2
        self.target_x = desired_screen_x - (player_iso_x + world_offset[0])
        self.target_y = desired_screen_y - (player_iso_y + world_offset[1])
        
        # Smooth easing toward target
        self.x += (self.target_x - self.x) * CAMERA_EASE_SPEED
        self.y += (self.target_y - self.y) * CAMERA_EASE_SPEED
    
    def get_world_offset(self, screen_width, screen_height):
        """Get world offset for rendering."""
        return (screen_width // 2, screen_height // 3)
