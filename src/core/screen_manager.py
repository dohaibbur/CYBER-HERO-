"""
Screen Manager for CyberHero
Handles screen resolution, scaling, and display mode
"""

import pygame
import os

class ScreenManager:
    def __init__(self):
        # pygame.init()  # Remove this - will be called in main()
        self.original_width = 1920
        self.original_height = 1080
        
        # Get monitor info
        self.monitor_width = pygame.display.Info().current_w
        self.monitor_height = pygame.display.Info().current_h
        
        # Set window size to 80% of monitor size or original, whichever is smaller
        target_width = min(int(self.monitor_width * 0.8), self.original_width)
        target_height = min(int(self.monitor_height * 0.8), self.original_height)
        
        # Maintain aspect ratio
        target_aspect = self.original_width / self.original_height
        window_aspect = target_width / target_height
        
        if window_aspect > target_aspect:
            # Too wide
            target_width = int(target_height * target_aspect)
        else:
            # Too tall
            target_height = int(target_width / target_aspect)
        
        self.screen_width = target_width
        self.screen_height = target_height
        
        # Calculate scale factors
        self.scale_x = self.screen_width / self.original_width
        self.scale_y = self.screen_height / self.original_height
        
        print(f"[ScreenManager] Monitor: {self.monitor_width}x{self.monitor_height}")
        print(f"[ScreenManager] Window: {self.screen_width}x{self.screen_height}")
        print(f"[ScreenManager] Scale: {self.scale_x:.2f}x, {self.scale_y:.2f}y")
        
        # Cache for loaded images to prevent reloading
        self.image_cache = {}
        
    def set_mode(self, mode='windowed'):
        """Set the display mode"""
        if mode == 'fullscreen':
            return pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        elif mode == 'borderless':
            return pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        else:  # windowed
            return pygame.display.set_mode((self.screen_width, self.screen_height))
    
    def load_and_scale_image(self, path, force_reload=False):
        """
        Load an image, scale it to screen size, and cache it.
        Uses high-quality scaling for better results.
        """
        # Check cache first
        if path in self.image_cache and not force_reload:
            return self.image_cache[path]
        
        # Find the file
        found_path = self._find_file(path)
        if not found_path:
            print(f"[ScreenManager] Image not found: {path}")
            return None
        
        try:
            # Load the image
            original_image = pygame.image.load(found_path)
            
            # Convert to ensure alpha if needed
            if found_path.lower().endswith('.png'):
                original_image = original_image.convert_alpha()
            else:
                original_image = original_image.convert()
            
            # Calculate target size while maintaining aspect ratio
            original_width, original_height = original_image.get_size()
            target_width = int(original_width * self.scale_x)
            target_height = int(original_height * self.scale_y)
            
            # Use smoothscale for better quality
            scaled_image = pygame.transform.smoothscale(
                original_image, 
                (target_width, target_height)
            )
            
            # Cache the result
            self.image_cache[path] = scaled_image
            print(f"[ScreenManager] Loaded and scaled {path}: {original_width}x{original_height} -> {target_width}x{target_height}")
            
            return scaled_image
            
        except Exception as e:
            print(f"[ScreenManager] Error loading image {path}: {e}")
            return None
    
    def _find_file(self, path):
        """Try to find the file in various locations"""
        # Check the exact path first
        if os.path.exists(path):
            return path
        
        # Try relative to current directory
        if os.path.exists(os.path.join(".", path)):
            return os.path.join(".", path)
        
        # Try in assets directory
        assets_path = os.path.join("assets", path)
        if os.path.exists(assets_path):
            return assets_path
        
        # Try without assets/ prefix
        if path.startswith("assets/"):
            short_path = path[7:]  # Remove "assets/"
            if os.path.exists(short_path):
                return short_path
        
        return None
    
    def clear_cache(self):
        """Clear the image cache"""
        self.image_cache.clear()
        
    def get_scale_factors(self):
        """Get scale factors for UI elements"""
        return self.scale_x, self.scale_y
    
    def get_screen_center(self):
        """Get the center of the screen"""
        return self.screen_width // 2, self.screen_height // 2

    def apply_settings(self):
        """
        Apply settings changes to the screen
        This will be called after settings are saved
        """
        from src.core.settings_manager import settings_manager

        # Get current settings
        settings = settings_manager.get_settings()

        # Apply resolution if changed
        resolution = settings.get('resolution', '1920x1080')
        width, height = map(int, resolution.split('x'))

        # Only recreate screen if resolution changed
        if width != self.screen_width or height != self.screen_height:
            self.screen_width = width
            self.screen_height = height

            # Recalculate scale factors
            self.scale_x = self.screen_width / self.original_width
            self.scale_y = self.screen_height / self.original_height

            # Clear image cache since scale changed
            self.clear_cache()

            print(f"[ScreenManager] Applied resolution: {self.screen_width}x{self.screen_height}")
            print(f"[ScreenManager] New scale: {self.scale_x:.2f}x, {self.scale_y:.2f}y")

            # Recreate the screen
            display_mode = settings.get('display_mode', 'windowed')
            return self.set_mode(display_mode)

        # Apply display mode if changed
        display_mode = settings.get('display_mode', 'windowed')
        return self.set_mode(display_mode)