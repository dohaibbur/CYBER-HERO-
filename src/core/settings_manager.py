"""
Settings Manager - CyberHero
Centralized settings management for the entire game
File: src/core/settings_manager.py
"""

import json
import os
import pygame

class SettingsManager:
    """
    Singleton class to manage game settings
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Use persistent data directory
        data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
        self.settings_file = os.path.join(data_dir, "settings.json")
        self.settings = self.load_settings()
        self._initialized = True
    
    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            # Audio
            "master_volume": 70,
            "sound_effects": 85,
            "music_volume": 60,
            # Appearance
            "luminosity": 80,
            "text_size": "medium",
            # Gameplay
            "hints": True,
            "difficulty": "normal",  # easy, normal, hard
            "text_speed": "normal",  # slow, normal, fast
            "auto_scroll": True,
            "show_command_hints": True,
            "educational_mode": True  # Show educational notes
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in default_settings:
                        if key not in loaded:
                            loaded[key] = default_settings[key]
                    return loaded
            except Exception as e:
                print(f"[SettingsManager] Error loading settings: {e}")
        
        # Fallback to bundled settings.json if persistent doesn't exist
        elif os.path.exists("settings.json"):
            try:
                with open("settings.json", 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in default_settings:
                        if key not in loaded:
                            loaded[key] = default_settings[key]
                    return loaded
            except:
                pass
        
        return default_settings
    
    def reload(self):
        """Reload settings from file"""
        self.settings = self.load_settings()
    
    # ===== AUDIO =====
    def get_master_volume(self):
        """Get master volume (0.0 to 1.0)"""
        return self.settings.get("master_volume", 70) / 100.0
    
    def get_sound_effects_volume(self):
        """Get sound effects volume (0.0 to 1.0)"""
        master = self.get_master_volume()
        sfx = self.settings.get("sound_effects", 85) / 100.0
        return master * sfx
    
    def get_music_volume(self):
        """Get music volume (0.0 to 1.0)"""
        master = self.get_master_volume()
        music = self.settings.get("music_volume", 60) / 100.0
        return master * music
    
    def set_pygame_volume(self):
        """Apply volume to pygame mixer"""
        try:
            # Set music volume (master * music)
            music_vol = self.get_music_volume()
            pygame.mixer.music.set_volume(music_vol)
        except:
            pass
    
    # ===== HINTS =====
    def are_hints_enabled(self):
        """Check if hints are enabled"""
        return self.settings.get("hints", True)
    
    # ===== LUMINOSITY (BRIGHTNESS) =====
    def get_luminosity(self):
        """Get brightness value (0-100)"""
        return self.settings.get("luminosity", 80)
    
    def get_brightness_multiplier(self):
        """Get brightness as a multiplier (0.0 to 1.0)"""
        return self.settings.get("luminosity", 80) / 100.0
    
    def apply_brightness_to_surface(self, surface):
        """Apply brightness filter to a surface"""
        brightness = self.get_brightness_multiplier()
        if brightness < 1.0:
            # Create a dark overlay
            dark_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = int((1.0 - brightness) * 200)  # Max 200 alpha for darkness
            dark_overlay.fill((0, 0, 0, alpha))
            surface.blit(dark_overlay, (0, 0))
        return surface
    
    # ===== TEXT SIZE =====
    def get_text_size(self):
        """Get text size setting"""
        return self.settings.get("text_size", "medium")
    
    def get_font_size(self, base_size):
        """Get scaled font size based on text_size setting"""
        sizes = {
            "small": 0.8,
            "medium": 1.0,
            "large": 1.3
        }
        multiplier = sizes.get(self.get_text_size(), 1.0)
        return int(base_size * multiplier)
    
    def get_scaled_font(self, base_size, font_path=None):
        """Get a font scaled to current text size setting"""
        scaled_size = self.get_font_size(base_size)
        if font_path:
            return pygame.font.Font(font_path, scaled_size)
        else:
            return pygame.font.Font(None, scaled_size)
    
    # ===== DIFFICULTY =====
    def get_difficulty(self):
        """Get difficulty level"""
        return self.settings.get("difficulty", "normal")

    def get_hint_cooldown(self):
        """Get hint cooldown time in seconds based on difficulty"""
        difficulty = self.get_difficulty()
        cooldowns = {
            "easy": 10,
            "normal": 30,
            "hard": 60
        }
        return cooldowns.get(difficulty, 30)

    def get_max_hints(self):
        """Get maximum hints available based on difficulty"""
        difficulty = self.get_difficulty()
        max_hints = {
            "easy": 999,  # Unlimited
            "normal": 5,
            "hard": 3
        }
        return max_hints.get(difficulty, 5)

    # ===== TEXT SPEED =====
    def get_text_speed(self):
        """Get text speed setting"""
        return self.settings.get("text_speed", "normal")

    def get_typing_delay(self):
        """Get delay between characters for typing effect (ms)"""
        speed = self.get_text_speed()
        delays = {
            "slow": 50,
            "normal": 20,
            "fast": 0  # Instant
        }
        return delays.get(speed, 20)

    # ===== AUTO SCROLL =====
    def is_auto_scroll_enabled(self):
        """Check if auto scroll is enabled"""
        return self.settings.get("auto_scroll", True)

    # ===== COMMAND HINTS =====
    def show_command_hints(self):
        """Check if command hints should be shown"""
        return self.settings.get("show_command_hints", True)

    # ===== EDUCATIONAL MODE =====
    def is_educational_mode(self):
        """Check if educational notes should be shown"""
        return self.settings.get("educational_mode", True)

    # ===== GENERAL GETTERS =====
    def get(self, key, default=None):
        """Get any setting value"""
        return self.settings.get(key, default)

    def get_all(self):
        """Get all settings"""
        return self.settings.copy()


# Create global instance
settings_manager = SettingsManager()