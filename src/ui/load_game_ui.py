"""
Load Game UI - CyberHero (FIXED & COMPATIBLE VERSION)
Modern cyberpunk-style interface for loading saved game profiles
Compatible with SaveLoadManager from save_load.py
"""

import pygame
import os
from datetime import datetime
from typing import Optional, Tuple, List, Dict

class LoadGameUI:
    """
    Modern cyberpunk-style load game interface
    Shows saved profiles as interactive cards with delete buttons
    """
    
    def __init__(self, screen, save_manager):
        """
        Initialize the load game UI
        
        Args:
            screen: Pygame screen surface
            save_manager: SaveLoadManager instance
        """
        self.screen = screen
        self.save_manager = save_manager
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()
        
        # Calculate scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale_min = min(self.scale_x, self.scale_y)
        
        # Load background image
        self.background_image = None
        try:
            background_path = r"C:\Users\nasrellahhabchi\Documents\cyberhero\assets\ui\menu_background2.png"
            if os.path.exists(background_path):
                self.background_image = pygame.image.load(background_path).convert()
                # Scale background to fit screen
                self.background_image = pygame.transform.scale(self.background_image, 
                                                              (self.screen_width, self.screen_height))
            else:
                print(f"Background image not found at: {background_path}")
                self.background_image = None
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_image = None
        
        # IMPROVED COLORS - Easier on the eyes (CHANGED: Brighter green theme)
        self.primary_color = (0, 255, 0)          # Bright green for "CHARGER UNE PARTIE"
        self.secondary_color = (100, 255, 100)    # Lighter green
        self.accent_color = (255, 255, 0)         # Yellow
        self.error_color = (255, 50, 50)          # Red
        self.text_color = (220, 220, 220)         # Light gray
        self.text_dark = (160, 160, 160)          # Darker gray for less important text
        self.dark_bg = (15, 20, 15)               # Dark background
        self.panel_bg = (30, 40, 30)              # Panel background (darker green tint)
        self.card_bg = (35, 45, 35)               # Card background
        
        # Semi-transparent overlay color for better text readability on background
        self.overlay_color = (0, 0, 0, 180)  # Semi-transparent black
        
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
        
        # Animation states
        self.scanline_pos = 0
        self.pulse_alpha = 0
        self.pulse_dir = 1
        
        # Load profiles - list_profiles returns basic info, not full profile data
        self.profile_infos = self.save_manager.list_profiles()
        self.selected_index = 0 if self.profile_infos else -1
        
        # Load full profiles for stage display
        self.full_profiles = {}
        for profile_info in self.profile_infos:
            nickname = profile_info.get('nickname')
            full_profile = self.save_manager.load_profile(nickname)
            if full_profile:
                self.full_profiles[nickname] = full_profile
    
    def draw_background(self):
        """Draw background with image and overlay for better text readability"""
        # Draw background image if available
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Fallback to solid dark background if image not available
            self.screen.fill(self.dark_bg)
            
            # Subtle grid lines (only for fallback)
            grid_color = (30, 50, 30)  # Very subtle green
            grid_size = int(80 * self.scale_min)  # Larger grid
            
            for x in range(0, self.screen_width, grid_size):
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height), 1)
            
            for y in range(0, self.screen_height, grid_size):
                pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y), 1)
        
        # Add a semi-transparent overlay for better text readability
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        self.screen.blit(overlay, (0, 0))
        
        # Subtle scanline effect (works with both image and fallback)
        self.scanline_pos = (self.scanline_pos + 3) % self.screen_height
        pygame.draw.line(self.screen, (50, 100, 50, 100), 
                        (0, int(self.scanline_pos)), 
                        (self.screen_width, int(self.scanline_pos)), 1)
    
    def get_current_stage(self, progress_data):
        """Determine the current stage based on completed missions."""
        missions_completed = progress_data.get('missions_completed', [])
        mission1_completed = progress_data.get('mission1_completed', False)
        
        # Check if mission1 is completed (from boolean or array)
        has_mission1 = mission1_completed or "mission1" in missions_completed
        has_mission2 = "mission2" in missions_completed
        has_mission3 = "mission3" in missions_completed
        
        if not has_mission1:
            return "mission1: Reconnaissance de ton propre réseau"
        elif not has_mission2:
            return "mission2: Analyse de traffic"
        elif not has_mission3:
            return "mission3: Analyse de paquets"
        else:
            return "Toutes missions terminées!"
    
    def draw_profile_card(self, x, y, width, height, profile_info, is_selected=False, is_hovered=False, delete_hovered=False):
        """
        Draw a profile card with a delete button
        
        Args:
            profile_info: Basic profile info from list_profiles() - NOT full profile data
        
        Returns:
            Tuple[pygame.Rect, pygame.Rect]: (card_rect, delete_button_rect)
        """
        # Card background - slightly transparent for better integration with background
        card_bg_color = (*self.card_bg, 220)  # Add alpha for transparency
        if is_selected:
            card_bg_color = (50, 60, 50, 220)  # Slightly lighter for selection
        elif is_hovered:
            card_bg_color = (45, 55, 45, 220)  # Slightly lighter for hover
        
        # Create a surface for the card with alpha channel
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw background on card surface
        pygame.draw.rect(card_surface, card_bg_color, (0, 0, width, height), 
                        border_radius=int(10 * self.scale_min))
        
        # Border
        border_width = int(2 * self.scale_min)
        if is_selected:
            border_color = (*self.accent_color, 255)  # Yellow for selected
        elif is_hovered:
            border_color = (*self.secondary_color, 255)  # Green for hover
        else:
            border_color = (*self.primary_color, 255)  # Bright green for normal
        
        pygame.draw.rect(card_surface, border_color, (0, 0, width, height), 
                        border_width, border_radius=int(10 * self.scale_min))
        
        # Blit the card surface to screen
        self.screen.blit(card_surface, (x, y))
        
        # Extract profile info (from list_profiles structure)
        nickname = profile_info.get('nickname', 'Unknown')
        hacker_type = profile_info.get('hacker_type', 'unknown')
        saved_at = profile_info.get('saved_at', '')
        
        # Format saved date
        try:
            dt = datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = "Unknown"
        
        # Get full profile for stage information
        # Get full profile for stage information
        full_profile = self.full_profiles.get(nickname, {})
        progress_data = full_profile.get('progress', {})
        current_stage_text = self.get_current_stage(progress_data)
        
        # Calculate text positions to avoid overlap
        vertical_spacing = int(35 * self.scale_min)
        current_y = y + 25
        
        # Nickname (brighter, readable)
        name_text = self.heading_font.render(nickname, True, self.text_color)
        name_rect = name_text.get_rect(centerx=x + width // 2, top=current_y)
        self.screen.blit(name_text, name_rect)
        current_y += vertical_spacing
        
        # Type (softer colors)
        type_colors = {
            'white_hat': (120, 255, 120),   # Bright green
            'grey_hat': (255, 255, 120),    # Bright yellow
            'black_hat': (255, 120, 120)    # Bright red
        }
        type_color = type_colors.get(hacker_type, self.text_color)
        type_text = self.body_font.render(f"{hacker_type.replace('_', ' ').title()}", True, type_color)
        type_rect = type_text.get_rect(centerx=x + width // 2, top=current_y)
        self.screen.blit(type_text, type_rect)
        current_y += vertical_spacing
        
        # Current stage - wrap text if too long
        max_text_width = width - 40  # Leave 20px margin on each side
        stage_words = current_stage_text.split()
        stage_lines = []
        current_line = ""
        
        for word in stage_words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.body_font.render(test_line, True, self.text_color)
            if test_surface.get_width() <= max_text_width:
                current_line = test_line
            else:
                if current_line:
                    stage_lines.append(current_line)
                current_line = word
        
        if current_line:
            stage_lines.append(current_line)
        
        # Draw stage text (possibly multiple lines)
        stage_line_height = int(28 * self.scale_min)
        for i, line in enumerate(stage_lines):
            stage_text = self.body_font.render(line, True, self.text_color)
            stage_rect = stage_text.get_rect(centerx=x + width // 2, top=current_y + (i * stage_line_height))
            self.screen.blit(stage_text, stage_rect)
        
        current_y += (len(stage_lines) * stage_line_height) + 10
        
        # Last saved (darker text for less importance)
        saved_text = self.small_font.render(f"Dernière sauvegarde: {date_str}", True, self.text_dark)
        saved_rect = saved_text.get_rect(centerx=x + width // 2, bottom=y + height - 50)
        self.screen.blit(saved_text, saved_rect)
        
        # ===== DELETE BUTTON =====
        delete_btn_width = int(width * 0.8)
        delete_btn_height = int(35 * self.scale_y)
        delete_btn_x = x + (width - delete_btn_width) // 2
        delete_btn_y = y + height - delete_btn_height - 10
        
        delete_rect = pygame.Rect(delete_btn_x, delete_btn_y, delete_btn_width, delete_btn_height)
        
        # Delete button background
        if delete_hovered:
            btn_bg = (80, 30, 30, 220)
            btn_border = (*self.error_color, 255)
            btn_text_color = (255, 100, 100)
        else:
            btn_bg = (50, 20, 20, 220)
            btn_border = (150, 50, 50, 255)
            btn_text_color = self.error_color
        
        # Create delete button surface with alpha
        delete_surface = pygame.Surface((delete_btn_width, delete_btn_height), pygame.SRCALPHA)
        pygame.draw.rect(delete_surface, btn_bg, (0, 0, delete_btn_width, delete_btn_height), 
                        border_radius=int(5 * self.scale_min))
        pygame.draw.rect(delete_surface, btn_border, (0, 0, delete_btn_width, delete_btn_height), 
                        int(2 * self.scale_min), border_radius=int(5 * self.scale_min))
        self.screen.blit(delete_surface, (delete_btn_x, delete_btn_y))
        
        # Delete button text (using X emoji instead of trash can for compatibility)
        delete_text = self.small_font.render("✖ SUPPRIMER", True, btn_text_color)
        delete_text_rect = delete_text.get_rect(center=delete_rect.center)
        self.screen.blit(delete_text, delete_text_rect)
        
        return pygame.Rect(x, y, width, height), delete_rect
    
    def show_delete_confirmation(self, profile_info):
        """Show delete confirmation dialog"""
        nickname = profile_info.get('nickname', 'Unknown')
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog panel
        dialog_width = int(500 * self.scale_x)
        dialog_height = int(250 * self.scale_y)
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        # Create dialog surface with alpha
        dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        
        # Draw panel background on dialog surface
        pygame.draw.rect(dialog_surface, (*self.panel_bg, 240), 
                        (0, 0, dialog_width, dialog_height), 
                        border_radius=int(15 * self.scale_min))
        pygame.draw.rect(dialog_surface, (*self.primary_color, 255), 
                        (0, 0, dialog_width, dialog_height), 
                        int(3 * self.scale_min), border_radius=int(15 * self.scale_min))
        
        # Blit dialog surface
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        
        # Text
        title = self.heading_font.render("SUPPRIMER LE PROFIL", True, self.error_color)
        title_rect = title.get_rect(centerx=self.screen_width // 2, top=dialog_y + 30)
        self.screen.blit(title, title_rect)

        msg1 = self.body_font.render(f"Supprimer '{nickname}'?", True, self.text_color)
        msg1_rect = msg1.get_rect(centerx=self.screen_width // 2, top=dialog_y + 70)
        self.screen.blit(msg1, msg1_rect)

        msg2 = self.small_font.render("Cette action est irreversible !", True, self.error_color)
        msg2_rect = msg2.get_rect(centerx=self.screen_width // 2, top=dialog_y + 155)
        self.screen.blit(msg2, msg2_rect)
        
        # Buttons
        button_width = int(120 * self.scale_x)
        button_height = int(50 * self.scale_y)
        button_y = dialog_y + dialog_height - 70
        
        yes_x = self.screen_width // 2 - button_width - 20
        no_x = self.screen_width // 2 + 20
        
        # Draw buttons
        yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
        no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
        
        # Create button surfaces with alpha
        yes_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        no_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        
        # Button backgrounds
        pygame.draw.rect(yes_surface, (60, 30, 30, 240), (0, 0, button_width, button_height), 
                        border_radius=int(8 * self.scale_min))
        pygame.draw.rect(no_surface, (30, 60, 30, 240), (0, 0, button_width, button_height), 
                        border_radius=int(8 * self.scale_min))
        
        # Button borders
        pygame.draw.rect(yes_surface, (*self.error_color, 255), (0, 0, button_width, button_height), 
                        int(2 * self.scale_min), border_radius=int(8 * self.scale_min))
        pygame.draw.rect(no_surface, (*self.primary_color, 255), (0, 0, button_width, button_height), 
                        int(2 * self.scale_min), border_radius=int(8 * self.scale_min))
        
        # Blit button surfaces
        self.screen.blit(yes_surface, (yes_x, button_y))
        self.screen.blit(no_surface, (no_x, button_y))
        
        yes_text = self.body_font.render("SUPPRIMER", True, self.error_color)
        no_text = self.body_font.render("ANNULER", True, self.primary_color)
        
        self.screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
        self.screen.blit(no_text, no_text.get_rect(center=no_rect.center))
        
        pygame.display.flip()
        
        # Wait for input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y or event.key == pygame.K_RETURN:
                        return True
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_rect.collidepoint(event.pos):
                        return True
                    elif no_rect.collidepoint(event.pos):
                        return False
 
    def show_password_prompt(self, profile_info, stored_password):
        """
        Show password prompt when loading a profile

        Args:
            profile_info: Basic profile info
            stored_password: The actual password to verify against

        Returns:
            True if password correct, False if cancelled or max attempts reached
        """
        nickname = profile_info.get('nickname', 'Unknown')
        password_input = ""
        show_password = False
        error_message = ""
        attempts = 0
        max_attempts = 3
        
        clock = pygame.time.Clock()
        
        while True:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Dialog panel
            dialog_width = int(600 * self.scale_x)
            dialog_height = int(350 * self.scale_y)
            dialog_x = (self.screen_width - dialog_width) // 2
            dialog_y = (self.screen_height - dialog_height) // 2
            
            # Create dialog surface with alpha
            dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
            
            # Draw panel background on dialog surface
            pygame.draw.rect(dialog_surface, (*self.panel_bg, 240), 
                            (0, 0, dialog_width, dialog_height), 
                            border_radius=int(15 * self.scale_min))
            pygame.draw.rect(dialog_surface, (*self.primary_color, 255), 
                            (0, 0, dialog_width, dialog_height), 
                            int(3 * self.scale_min), border_radius=int(15 * self.scale_min))
            
            # Blit dialog surface
            self.screen.blit(dialog_surface, (dialog_x, dialog_y))
            
            # Title
            title = self.heading_font.render("ENTER PASSWORD", True, self.primary_color)
            title_rect = title.get_rect(centerx=self.screen_width // 2, top=dialog_y + 30)
            self.screen.blit(title, title_rect)
            
            # Nickname
            nickname_text = self.body_font.render(f"Profil: {nickname}", True, self.text_color)
            nickname_rect = nickname_text.get_rect(centerx=self.screen_width // 2, top=dialog_y + 80)
            self.screen.blit(nickname_text, nickname_rect)

            # Password field
            password_y = dialog_y + 140
            password_label = self.body_font.render("Mot de passe:", True, self.text_color)
            self.screen.blit(password_label, (dialog_x + 50, password_y))
            
            # Input box
            input_width = dialog_width - 100
            input_height = 50
            input_x = dialog_x + 50
            input_y = password_y + 40
            
            pygame.draw.rect(self.screen, (30, 40, 30, 240), 
                           (input_x, input_y, input_width, input_height),
                           border_radius=int(5 * self.scale_min))
            pygame.draw.rect(self.screen, (*self.primary_color, 255), 
                           (input_x, input_y, input_width, input_height), 2,
                           border_radius=int(5 * self.scale_min))
            
            # Password text (masked or visible)
            display_text = "*" * len(password_input) if not show_password else password_input
            password_surface = self.body_font.render(display_text, True, self.text_color)
            self.screen.blit(password_surface, (input_x + 10, input_y + 12))
            
            # Cursor
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = input_x + 10 + password_surface.get_width() + 5
                pygame.draw.line(self.screen, self.primary_color,
                               (cursor_x, input_y + 10),
                               (cursor_x, input_y + 40), 2)
            
            # Show/Hide toggle
            toggle_y = input_y + 52
            toggle_text = f"[ESPACE pour {'MASQUER' if show_password else 'AFFICHER'}]"
            toggle = self.small_font.render(toggle_text, True, self.text_dark)
            self.screen.blit(toggle, (input_x, toggle_y))
            
            # Error message
            if error_message:
                error = self.body_font.render(error_message, True, self.error_color)
                error_rect = error.get_rect(centerx=self.screen_width // 2, top=toggle_y + 30)
                self.screen.blit(error, error_rect)
                
                attempts_left = max_attempts - attempts
                attempts_text = self.small_font.render(f"Tentatives: {attempts_left}", True, self.error_color)
                attempts_rect = attempts_text.get_rect(centerx=self.screen_width // 2, top=error_rect.bottom + 5)
                self.screen.blit(attempts_text, attempts_rect)

            
            
            pygame.display.flip()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    
                    elif event.key == pygame.K_SPACE:
                        show_password = not show_password
                    
                    elif event.key == pygame.K_RETURN:
                        if password_input:
                            # Verify password
                            if password_input == stored_password:
                                return True  # Password correct
                            else:
                                attempts += 1
                                if attempts >= max_attempts:
                                    error_message = "Trop de tentatives echouees !"
                                    pygame.time.wait(1500)
                                    return False  # Max attempts reached
                                else:
                                    error_message = "Mot de passe incorrect !"
                                    password_input = ""  # Clear input
                        else:
                            error_message = "Veuillez entrer le mot de passe"
                    
                    elif event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                        error_message = ""
                    
                    else:
                        if event.unicode.isprintable() and len(password_input) < 30:
                            password_input += event.unicode
                            error_message = ""
            
            clock.tick(60)

    def run(self) -> Tuple[str, Optional[Dict]]:
        """
        Run the load game interface
        
        Returns:
            (result: str, profile: Optional[Dict])
            result can be: "load", "exit", "menu"
            
        IMPORTANT: When returning "load", this returns the FULL profile data
        loaded via save_manager.load_profile(), NOT just the basic info
        """
        if not self.profile_infos:
            # No profiles - show message
            running = True
            start_time = pygame.time.get_ticks()
            
            while running:
                self.clock.tick(60)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit", None
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        if pygame.time.get_ticks() - start_time > 1000:
                            return "menu", None
                
                self.draw_background()
                
                # Title - CHANGED to bright green
                title = self.title_font.render("CHARGER UNE PARTIE", True, self.primary_color)
                title_rect = title.get_rect(centerx=self.screen_width // 2, top=50)
                self.screen.blit(title, title_rect)
                
                # No profiles message
                msg1 = self.heading_font.render("Aucune partie sauvegardée", True, self.text_color)
                msg1_rect = msg1.get_rect(centerx=self.screen_width // 2, centery=self.screen_height // 2 - 50)
                self.screen.blit(msg1, msg1_rect)
                
                msg2 = self.body_font.render("Créez une nouvelle partie pour commencer!", True, self.text_dark)
                msg2_rect = msg2.get_rect(centerx=self.screen_width // 2, centery=self.screen_height // 2 + 20)
                self.screen.blit(msg2, msg2_rect)
                
                # Continue prompt (blinking)
                if pygame.time.get_ticks() % 1000 < 500:
                    prompt = self.small_font.render("Appuyez sur une touche pour revenir...", True, self.secondary_color)
                    prompt_rect = prompt.get_rect(centerx=self.screen_width // 2, bottom=self.screen_height - 50)
                    self.screen.blit(prompt, prompt_rect)
                
                pygame.display.flip()
            
            return "menu", None
        
        # Main loop
        running = True
        card_rects = []
        delete_rects = []
        
        while running:
            self.clock.tick(60)
            
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Calculate card layout
            card_width = int(350 * self.scale_x)
            card_height = int(280 * self.scale_y)  # Increased height for multi-line stage text
            cards_per_row = max(1, self.screen_width // (card_width + 50))
            start_x = (self.screen_width - (cards_per_row * card_width + (cards_per_row - 1) * 50)) // 2
            start_y = int(320 * self.scale_y)  # Increased from 200 to 320 for more top margin
            
            hovered_card_index = -1
            hovered_delete_index = -1
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu", None
                    elif event.key == pygame.K_RETURN:
                        if 0 <= self.selected_index < len(self.profile_infos):
                            # Load FULL profile data using nickname
                            nickname = self.profile_infos[self.selected_index]['nickname']
                            full_profile = self.save_manager.load_profile(nickname)

                            if full_profile:
                                # Check if profile has password (old profiles might not)
                                stored_password = full_profile.get('password', '')

                                if stored_password:
                                    # Show password prompt and verify
                                    password_correct = self.show_password_prompt(
                                        self.profile_infos[self.selected_index],
                                        stored_password
                                    )

                                    if password_correct:
                                        return "load", full_profile
                                    # If False (cancelled or wrong), just continue to show menu again
                                else:
                                    # No password set (old profile) - allow load without password
                                    return "load", full_profile
                            else:
                                # Error loading - refresh list and continue
                                self.profile_infos = self.save_manager.list_profiles()
                                self.selected_index = min(self.selected_index, len(self.profile_infos) - 1)
                                
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_d:
                        if 0 <= self.selected_index < len(self.profile_infos):
                            if self.show_delete_confirmation(self.profile_infos[self.selected_index]):
                                nickname = self.profile_infos[self.selected_index]['nickname']
                                success, msg = self.save_manager.delete_profile(nickname)
                                
                                if success:
                                    # Refresh profile list
                                    self.profile_infos = self.save_manager.list_profiles()
                                    self.selected_index = min(self.selected_index, len(self.profile_infos) - 1)
                                    if self.selected_index < 0:
                                        self.selected_index = 0 if self.profile_infos else -1
                                        
                    elif event.key == pygame.K_UP:
                        if self.selected_index >= cards_per_row:
                            self.selected_index -= cards_per_row
                    elif event.key == pygame.K_DOWN:
                        if self.selected_index + cards_per_row < len(self.profile_infos):
                            self.selected_index += cards_per_row
                    elif event.key == pygame.K_LEFT:
                        if self.selected_index > 0:
                            self.selected_index -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.selected_index < len(self.profile_infos) - 1:
                            self.selected_index += 1
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check if clicking delete button
                        clicked_delete = False
                        for i, delete_rect in enumerate(delete_rects):
                            if delete_rect and delete_rect.collidepoint(event.pos):
                                # Delete this profile
                                if self.show_delete_confirmation(self.profile_infos[i]):
                                    nickname = self.profile_infos[i]['nickname']
                                    success, msg = self.save_manager.delete_profile(nickname)
                                    
                                    if success:
                                        # Refresh profile list
                                        self.profile_infos = self.save_manager.list_profiles()
                                        self.selected_index = min(self.selected_index, len(self.profile_infos) - 1)
                                        if self.selected_index < 0:
                                            self.selected_index = 0 if self.profile_infos else -1
                                clicked_delete = True
                                break
                        
                        # If not delete button, check if clicking on card to load
                        if not clicked_delete:
                            for i, card_rect in enumerate(card_rects):
                                if card_rect and card_rect.collidepoint(event.pos):
                                    self.selected_index = i
                                    # Load FULL profile data
                                    nickname = self.profile_infos[i]['nickname']
                                    full_profile = self.save_manager.load_profile(nickname)

                                    if full_profile:
                                        # Check if profile has password
                                        stored_password = full_profile.get('password', '')

                                        if stored_password:
                                            # Show password prompt and verify
                                            password_correct = self.show_password_prompt(
                                                self.profile_infos[i],
                                                stored_password
                                            )

                                            if password_correct:
                                                return "load", full_profile
                                            # If False, continue to show menu again
                                        else:
                                            # No password (old profile) - allow load
                                            return "load", full_profile
            
            # Drawing
            self.draw_background()
            
            # Title - CHANGED to bright green
            title = self.title_font.render("CHARGER UNE PARTIE", True, self.primary_color)
            title_rect = title.get_rect(centerx=self.screen_width // 2, top=50)
            self.screen.blit(title, title_rect)

            # Subtitle - CHANGED to match green theme
            subtitle = self.small_font.render(f"{len(self.profile_infos)} partie(s) sauvegardée(s) - Cliquez pour charger, bouton Supprimer pour retirer",
                                            True, self.secondary_color)
            subtitle_rect = subtitle.get_rect(centerx=self.screen_width // 2, top=110)
            self.screen.blit(subtitle, subtitle_rect)
            
            # Clear and rebuild rects lists
            card_rects = []
            delete_rects = []
            
            # Draw profile cards
            for i, profile_info in enumerate(self.profile_infos):
                row = i // cards_per_row
                col = i % cards_per_row
                x = start_x + col * (card_width + 50)
                y = start_y + row * (card_height + 40)  # Increased vertical spacing between rows
                
                is_selected = (i == self.selected_index)
                
                # Create temporary rects for hover detection
                temp_card_rect = pygame.Rect(x, y, card_width, card_height)
                # Approximate delete button position for hover detection
                delete_btn_width = int(card_width * 0.8)
                delete_btn_height = int(35 * self.scale_y)
                delete_btn_x = x + (card_width - delete_btn_width) // 2
                delete_btn_y = y + card_height - delete_btn_height - 10
                temp_delete_rect = pygame.Rect(delete_btn_x, delete_btn_y, delete_btn_width, delete_btn_height)
                
                is_card_hovered = temp_card_rect.collidepoint(mouse_pos)
                is_delete_hovered = temp_delete_rect.collidepoint(mouse_pos)
                
                # Draw the card and get actual rects
                card_rect, delete_rect = self.draw_profile_card(
                    x, y, card_width, card_height, profile_info,
                    is_selected=is_selected,
                    is_hovered=is_card_hovered,
                    delete_hovered=is_delete_hovered
                )
                
                # Store rects for click detection
                card_rects.append(card_rect)
                delete_rects.append(delete_rect)
            
            # Instructions - CHANGED to match green theme
            instructions = self.small_font.render("ENTREE/CLIC: Charger  |  SUPPR/D: Retirer Sélection  |  ECHAP: Retour  |  Flèches: Naviguer",
                                                 True, self.secondary_color)
            instr_rect = instructions.get_rect(centerx=self.screen_width // 2, bottom=self.screen_height - 30)
            self.screen.blit(instructions, instr_rect)
            
            pygame.display.flip()
        
        return "menu", None