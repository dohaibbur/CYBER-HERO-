"""
Settings UI - CyberHero
Interface de paramètres cyberpunk simplifiée
File: src/ui/settings_ui.py
"""

import pygame
import json
import os

# Try to import settings manager if available
try:
    from src.core.settings_manager import settings_manager
    SETTINGS_MANAGER_AVAILABLE = True
except ImportError:
    SETTINGS_MANAGER_AVAILABLE = False
    print("[SettingsUI] Settings manager not available - settings won't apply automatically")

# Global screen manager - will be set by main.py
screen_manager = None

class SettingsUI:
    """
    Interface de paramètres cyberpunk simplifiée
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()
        
        # Calculate scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale_min = min(self.scale_x, self.scale_y)
        
        # Colors
        self.primary_color = (0, 255, 0)
        self.secondary_color = (0, 255, 255)
        self.accent_color = (255, 255, 0)
        self.error_color = (255, 0, 0)
        self.text_color = (220, 220, 220)
        self.dark_bg = (10, 15, 10)
        
        # Load background image
        try:
            self.background = pygame.image.load(r"C:\Users\nasrellahhabchi\Documents\cyberhero\assets\ui\menu_background.png")
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except:
            self.background = None
            print("[SettingsUI] Could not load background image")
        
        # Tweakable layout parameters
        self.left_margin = 150 * self.scale_x  # Distance from left edge
        self.top_margin = 100 * self.scale_y   # Distance from top
        self.section_spacing = 80 * self.scale_y  # Space between sections
        self.item_spacing = 70 * self.scale_y     # Space between items
        self.header_spacing = 50 * self.scale_y   # Space after header
        self.control_width = 400 * self.scale_x   # Width of sliders/dropdowns
        
        # Fonts - Standardized sizes (matching desktop)
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * self.scale_min))
            self.heading_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale_min))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * self.scale_min))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(22 * self.scale_min))
        except:
            self.title_font = pygame.font.Font(None, int(42 * self.scale_min))
            self.heading_font = pygame.font.Font(None, int(32 * self.scale_min))
            self.body_font = pygame.font.Font(None, int(26 * self.scale_min))
            self.small_font = pygame.font.Font(None, int(22 * self.scale_min))
        
        # Load settings
        self.settings = self.load_settings()
        
        # Animation
        self.scanline_pos = 0
        
        # Interaction tracking
        self.dragging_slider = None
        self.interactive_elements = {}
        
    def load_settings(self):
        """Load settings from file or create defaults"""
        # Use persistent data directory
        data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
        settings_file = os.path.join(data_dir, "settings.json")
        
        # Fallback to bundled settings if persistent doesn't exist
        if not os.path.exists(settings_file) and os.path.exists("settings.json"):
            settings_file = "settings.json"
        
        default_settings = {
            # Audio Section
            "master_volume": 70,  # 0-100
            "sound_effects": 85,  # 0-100
            "music_volume": 60,  # 0-100
            
            # Appearance Section
            "luminosity": 80,  # 0-100 (brightness)
        }
        
        if settings_file:
            try:
                with open(settings_file, 'r') as f:
                    loaded = json.load(f)
                    
                    # MIGRATION: Convert old format to new format
                    if isinstance(loaded.get("audio"), dict):
                        print("[SettingsUI] Migration de l'ancien format...")
                        new_settings = {
                            "master_volume": loaded.get("audio", {}).get("master_volume", 70),
                            "sound_effects": loaded.get("audio", {}).get("sfx_volume", 85),
                            "music_volume": loaded.get("audio", {}).get("music_volume", 60),
                            "luminosity": loaded.get("luminosity", 80),
                        }
                        loaded = new_settings
                    
                    # Merge with defaults for any missing keys
                    for key in default_settings:
                        if key not in loaded:
                            loaded[key] = default_settings[key]
                    
                    return loaded
            except Exception as e:
                print(f"[SettingsUI] Erreur lors du chargement : {e}")
                pass
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file and apply them"""
        try:
            # Use persistent data directory
            data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
            settings_file = os.path.join(data_dir, "settings.json")
            
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            # Apply settings immediately if manager is available
            if SETTINGS_MANAGER_AVAILABLE:
                settings_manager.reload()
                self.apply_settings()
            
            return True
        except Exception as e:
            print(f"[SettingsUI] Erreur lors de la sauvegarde : {e}")
            return False
    
    def apply_settings(self):
        """Apply settings to the game immediately"""
        if not SETTINGS_MANAGER_AVAILABLE:
            return
        
        # Apply audio volume
        try:
            settings_manager.set_pygame_volume()
            print(f"[SettingsUI] Volume audio appliqué : {self.settings['master_volume']}%")
        except:
            pass
        
        print("[SettingsUI] Paramètres appliqués avec succès")
    
    def draw_background(self):
        """Draw background with optional overlay"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Fallback: dark background with grid
            self.screen.fill((15, 20, 15))
            
            # Grid (optimized)
            grid_size = int(80 * self.scale_min)
            for x in range(0, self.screen_width, grid_size):
                pygame.draw.line(self.screen, (0, 40, 0), (x, 0), (x, self.screen_height), 1)
            for y in range(0, self.screen_height, grid_size):
                pygame.draw.line(self.screen, (0, 40, 0), (0, y), (self.screen_width, y), 1)
        
        # Scanline effect
        self.scanline_pos = (self.scanline_pos + 4) % self.screen_height
        pygame.draw.line(self.screen, (0, 255, 0, 100), (0, int(self.scanline_pos)), (self.screen_width, int(self.scanline_pos)), 2)
    
    def draw_slider(self, x, y, width, value, min_val, max_val, label, element_id):
        """Draw a slider control"""
        # Label
        label_text = self.body_font.render(label, True, self.text_color)
        self.screen.blit(label_text, (x, y - 40 * self.scale_y))
        
        # Slider bar
        bar_height = int(12 * self.scale_y)
        pygame.draw.rect(self.screen, (0, 50, 0), (x, y, width, bar_height), border_radius=int(6 * self.scale_min))
        
        # Fill
        fill_width = int((value - min_val) / (max_val - min_val) * width)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.primary_color, (x, y, fill_width, bar_height), border_radius=int(6 * self.scale_min))
        
        # Handle
        handle_x = x + fill_width
        handle_radius = int(18 * self.scale_min)
        pygame.draw.circle(self.screen, self.secondary_color, (handle_x, y + bar_height // 2), handle_radius)
        pygame.draw.circle(self.screen, self.primary_color, (handle_x, y + bar_height // 2), handle_radius - 3)
        
        # Value text
        value_text = self.body_font.render(str(int(value)), True, self.accent_color)
        self.screen.blit(value_text, (x + width + 30 * self.scale_x, y - 8 * self.scale_y))
        
        # Store interactive area
        slider_rect = pygame.Rect(x, y - bar_height, width, bar_height * 3)
        self.interactive_elements[element_id] = {
            'type': 'slider',
            'rect': slider_rect,
            'x': x,
            'width': width,
            'min_val': min_val,
            'max_val': max_val
        }
        
        return slider_rect
    
    def draw_toggle(self, x, y, enabled, label, element_id):
        """Draw a toggle switch with ACTIF/NON ACTIF"""
        # Label
        label_text = self.body_font.render(label, True, self.text_color)
        self.screen.blit(label_text, (x, y))
        
        # Status text
        status_x = x + label_text.get_width() + 40 * self.scale_x
        status_text = "ACTIF" if enabled else "NON ACTIF"
        status_color = self.primary_color if enabled else self.error_color
        status_surface = self.body_font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (status_x, y))
        
        # Toggle switch
        switch_width = int(70 * self.scale_x)
        switch_height = int(35 * self.scale_y)
        switch_x = status_x + status_surface.get_width() + 30 * self.scale_x
        
        # Background
        bg_color = self.primary_color if enabled else (100, 100, 100)
        pygame.draw.rect(self.screen, bg_color, (switch_x, y, switch_width, switch_height), border_radius=int(17 * self.scale_min))
        
        # Handle
        handle_radius = int(14 * self.scale_min)
        handle_x = switch_x + switch_width - handle_radius - 5 if enabled else switch_x + handle_radius + 5
        handle_y = y + switch_height // 2
        pygame.draw.circle(self.screen, self.accent_color if enabled else (150, 150, 150), (handle_x, handle_y), handle_radius)
        
        # Store interactive area
        toggle_rect = pygame.Rect(switch_x, y, switch_width, switch_height)
        self.interactive_elements[element_id] = {
            'type': 'toggle',
            'rect': toggle_rect
        }
        
        return toggle_rect
    
    def draw_dropdown(self, x, y, width, options, selected, label, element_id):
        """Draw a dropdown selector"""
        # Label
        label_text = self.body_font.render(label, True, self.text_color)
        self.screen.blit(label_text, (x, y - 45 * self.scale_y))
        
        # Dropdown box
        box_height = int(50 * self.scale_y)
        pygame.draw.rect(self.screen, (0, 50, 0), (x, y, width, box_height), border_radius=int(10 * self.scale_min))
        pygame.draw.rect(self.screen, self.primary_color, (x, y, width, box_height), 3, border_radius=int(10 * self.scale_min))
        
        # Selected value
        value_text = self.body_font.render(str(selected).upper(), True, self.accent_color)
        value_rect = value_text.get_rect(centerx=x + width // 2, centery=y + box_height // 2)
        self.screen.blit(value_text, value_rect)
        
        # Arrows
        arrow_size = int(10 * self.scale_min)
        left_arrow_x = x + 20 * self.scale_x
        right_arrow_x = x + width - 20 * self.scale_x
        arrow_y = y + box_height // 2
        
        # Left arrow
        pygame.draw.polygon(self.screen, self.secondary_color, [
            (left_arrow_x, arrow_y),
            (left_arrow_x + arrow_size, arrow_y - arrow_size),
            (left_arrow_x + arrow_size, arrow_y + arrow_size)
        ])
        
        # Right arrow
        pygame.draw.polygon(self.screen, self.secondary_color, [
            (right_arrow_x, arrow_y),
            (right_arrow_x - arrow_size, arrow_y - arrow_size),
            (right_arrow_x - arrow_size, arrow_y + arrow_size)
        ])
        
        # Store interactive areas
        dropdown_rect = pygame.Rect(x, y, width, box_height)
        left_arrow_rect = pygame.Rect(x, y, int(60 * self.scale_x), box_height)
        right_arrow_rect = pygame.Rect(x + width - int(60 * self.scale_x), y, int(60 * self.scale_x), box_height)
        
        self.interactive_elements[element_id] = {
            'type': 'dropdown',
            'rect': dropdown_rect,
            'left_arrow': left_arrow_rect,
            'right_arrow': right_arrow_rect,
            'options': options
        }
        
        return dropdown_rect
    
    def draw_button(self, x, y, width, height, text, is_hovered=False):
        """Draw a button"""
        color = self.secondary_color if is_hovered else self.primary_color
        
        # Button background
        pygame.draw.rect(self.screen, color, (x, y, width, height), 3, border_radius=int(10 * self.scale_min))
        
        # Button text
        text_surface = self.body_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_section_header(self, x, y, text):
        """Draw a section header"""
        header_text = self.heading_font.render(text, True, self.secondary_color)
        self.screen.blit(header_text, (x, y))
        
        # Draw underline
        line_width = int(500 * self.scale_x)
        line_y = y + header_text.get_height() + int(5 * self.scale_y)
        pygame.draw.line(self.screen, self.secondary_color, (x, line_y), (x + line_width, line_y), 2)
        
        return header_text.get_height() + int(20 * self.scale_y)
    
    def handle_slider_interaction(self, element_id, mouse_x):
        """Update slider value based on mouse position"""
        element = self.interactive_elements[element_id]
        slider_x = element['x']
        slider_width = element['width']
        min_val = element['min_val']
        max_val = element['max_val']
        
        # Calculate new value
        relative_x = max(0, min(mouse_x - slider_x, slider_width))
        value = min_val + (relative_x / slider_width) * (max_val - min_val)
        value = max(min_val, min(max_val, value))
        
        # Update settings based on element_id
        if element_id == "master_volume":
            old_value = self.settings["master_volume"]
            self.settings["master_volume"] = int(value)
            
            # Apply audio change in real-time for preview
            if SETTINGS_MANAGER_AVAILABLE and old_value != int(value):
                try:
                    pygame.mixer.music.set_volume(int(value) / 100.0)
                except:
                    pass
        
        elif element_id == "sound_effects":
            self.settings["sound_effects"] = int(value)
        
        elif element_id == "music_volume":
            old_value = self.settings["music_volume"]
            self.settings["music_volume"] = int(value)
            
            # Apply music volume in real-time
            if old_value != int(value):
                try:
                    # Apply both master and music volume
                    final_volume = (self.settings["master_volume"] / 100.0) * (int(value) / 100.0)
                    pygame.mixer.music.set_volume(final_volume)
                except:
                    pass
        
        elif element_id == "luminosity":
            self.settings["luminosity"] = int(value)
    
    def handle_toggle_interaction(self, element_id):
        """Toggle a boolean setting"""
        if element_id == "fullscreen":
            self.settings["fullscreen"] = not self.settings["fullscreen"]
    
    def handle_dropdown_interaction(self, element_id, direction):
        """Change dropdown value (direction: -1 for left, 1 for right)"""
        pass
    
    def run(self):
        """Run the settings UI"""
        running = True
        
        while running:
            self.clock.tick(60)
            
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = mouse_pos
            
            # Button positions (left aligned)
            button_width = int(180 * self.scale_x)
            button_height = int(60 * self.scale_y)
            button_y = int(self.screen_height - 120 * self.scale_y)
            save_x = int(self.left_margin)
            back_x = int(self.left_margin + button_width + 30)
            
            save_hover = pygame.Rect(save_x, button_y, button_width, button_height).collidepoint(mouse_pos)
            back_hover = pygame.Rect(back_x, button_y, button_width, button_height).collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings()
                    return "exit"
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_settings()
                        return "back"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if save_hover:
                            self.save_settings()
                            return "back"
                        elif back_hover:
                            self.save_settings()
                            return "back"
                        else:
                            # Check for interactions with settings controls
                            for element_id, element_data in self.interactive_elements.items():
                                if element_data['type'] == 'slider':
                                    if element_data['rect'].collidepoint(mouse_pos):
                                        self.dragging_slider = element_id
                                        self.handle_slider_interaction(element_id, mouse_x)
                                
                                elif element_data['type'] == 'toggle':
                                    if element_data['rect'].collidepoint(mouse_pos):
                                        self.handle_toggle_interaction(element_id)
                                
                                elif element_data['type'] == 'dropdown':
                                    if element_data['left_arrow'].collidepoint(mouse_pos):
                                        self.handle_dropdown_interaction(element_id, -1)
                                    elif element_data['right_arrow'].collidepoint(mouse_pos):
                                        self.handle_dropdown_interaction(element_id, 1)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click released
                        self.dragging_slider = None
                
                elif event.type == pygame.MOUSEMOTION:
                    # Handle slider dragging
                    if self.dragging_slider:
                        self.handle_slider_interaction(self.dragging_slider, mouse_x)
            
            # Clear interactive elements for this frame
            self.interactive_elements = {}
            
            # Drawing
            self.draw_background()
            
            # Title (left aligned)
            title = self.title_font.render("PARAMÈTRES", True, self.primary_color)
            self.screen.blit(title, (self.left_margin, self.top_margin))
            
            # Settings content - organized by sections (all left-aligned)
            x = int(self.left_margin)
            y = int(self.top_margin + 100 * self.scale_y)
            
            # ===== AUDIO SECTION =====
            y += self.draw_section_header(x, y, "AUDIO")
            y += self.header_spacing
            
            # Volume Principal slider
            self.draw_slider(x, y, int(self.control_width), 
                           self.settings["master_volume"], 0, 100, "Volume Principal", "master_volume")
            y += self.item_spacing
            
            # Effets Sonores slider
            self.draw_slider(x, y, int(self.control_width), 
                           self.settings["sound_effects"], 0, 100, "Effets Sonores", "sound_effects")
            y += self.item_spacing
            
            # Volume Musique slider
            self.draw_slider(x, y, int(self.control_width), 
                           self.settings["music_volume"], 0, 100, "Volume Musique", "music_volume")
            y += self.section_spacing
            
            # ===== APPARENCE SECTION =====
            y += self.draw_section_header(x, y, "APPARENCE")
            y += self.header_spacing
            
            # Luminosité slider
            self.draw_slider(x, y, int(self.control_width), 
                           self.settings["luminosity"], 0, 100, "Luminosité", "luminosity")
            y += self.section_spacing
            
            # Buttons (left aligned)
            self.draw_button(save_x, button_y, button_width, button_height, "SAUVEGARDER", save_hover)
            self.draw_button(back_x, button_y, button_width, button_height, "RETOUR", back_hover)
            
            # Instructions (left aligned)
            instructions = self.small_font.render("ESC: Retour au Menu  |  Sauvegarde Automatique", True, (150, 150, 150))
            self.screen.blit(instructions, (self.left_margin, self.screen_height - 30))
            
            # Apply luminosity effect in real-time for preview
            brightness = self.settings["luminosity"] / 100.0
            if brightness < 1.0:
                dark_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                alpha = int((1.0 - brightness) * 200)
                dark_overlay.fill((0, 0, 0, alpha))
                self.screen.blit(dark_overlay, (0, 0))
            
            pygame.display.flip()
        
        return "menu"