"""
Mission Notes UI - CyberHero
Popup window for collecting mission information
"""

import pygame
from typing import Tuple, Dict, Optional


class MissionNotesPopup:
    """
    Mission notes popup for Mission 1
    Shows progress bar, objectives, and input fields
    """

    def __init__(self, screen, profile_data: Dict, network_config: Dict, persisted_data: Dict = None):
        """
        Initialize mission notes popup

        Args:
            screen: Pygame screen surface
            profile_data: Player profile
            network_config: Network configuration with correct answers
            persisted_data: Previously entered field data (to restore on reopen)
        """
        self.screen = screen
        self.profile_data = profile_data
        self.network_config = network_config
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors
        self.bg_color = (15, 15, 15, 230)  # Semi-transparent dark
        self.panel_bg = (25, 25, 30)
        self.border_color = (0, 220, 50)  # Matrix green
        self.text_color = (200, 200, 200)
        self.label_color = (0, 220, 50)
        self.input_bg = (35, 35, 40)
        self.input_active = (45, 45, 50)
        self.success_color = (0, 255, 100)
        self.error_color = (255, 80, 80)

        # Fonts - Match terminal sizes
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()

        try:
            self.title_font = settings.get_scaled_font(int(42 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.heading_font = settings.get_scaled_font(int(32 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.body_font = settings.get_scaled_font(int(26 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.small_font = settings.get_scaled_font(int(22 * self.scale), "assets/fonts/Cyberpunk.ttf")
        except:
            self.title_font = settings.get_scaled_font(int(42 * self.scale))
            self.heading_font = settings.get_scaled_font(int(32 * self.scale))
            self.body_font = settings.get_scaled_font(int(26 * self.scale))
            self.small_font = settings.get_scaled_font(int(22 * self.scale))

        # Mission fields - NetworkSimulator data structure
        # network_config should be from NetworkSimulator.network_data
        player_data = self.network_config.get("player", {})
        router_data = self.network_config.get("router", {})
        network_data = self.network_config.get("network", {})

        self.fields = {
            "ip_address": {"label": "Votre adresse IP", "value": "", "correct": player_data.get("ip_address", "192.168.1.100"), "validated": False},
            "mac_address": {"label": "Votre adresse MAC", "value": "", "correct": player_data.get("mac_address", "00:00:00:00:00:00"), "validated": False},
            "subnet_mask": {"label": "Masque de sous-reseau", "value": "", "correct": player_data.get("subnet_mask", "255.255.255.0"), "validated": False},
            "gateway": {"label": "Passerelle par defaut", "value": "", "correct": player_data.get("default_gateway", "192.168.1.1"), "validated": False},
            "device_count": {"label": "Nombre de peripheriques", "value": "", "correct": str(network_data.get("total_devices", 5)), "validated": False},
            "router_name": {"label": "Nom du routeur", "value": "", "correct": router_data.get("hostname", "HOME-ROUTER"), "validated": False}
        }

        # Restore persisted data if available
        if persisted_data:
            for key in self.fields:
                if key in persisted_data:
                    self.fields[key]["value"] = persisted_data[key]["value"]
                    self.fields[key]["validated"] = persisted_data[key]["validated"]

        self.active_field = None
        self.field_order = ["ip_address", "mac_address", "subnet_mask", "gateway", "device_count", "router_name"]
        self.field_rects = {}

        # Buttons
        self.send_button_rect = None
        self.close_button_rect = None

    def get_progress(self):
        """Calculate progress percentage"""
        validated_count = sum(1 for field in self.fields.values() if field["validated"])
        total_count = len(self.fields)
        return int((validated_count / total_count) * 100)

    def validate_field(self, field_key: str):
        """Validate a field's value"""
        field = self.fields[field_key]
        user_value = field["value"].strip()
        correct_value = field["correct"].strip()

        # Debug output
        print(f"[DEBUG] Validating {field_key}: user='{user_value}' vs correct='{correct_value}'")

        # Special handling for MAC address - accept both : and - separators
        if field_key == "mac_address":
            user_mac = user_value.upper().replace("-", ":")
            correct_mac = correct_value.upper().replace("-", ":")
            print(f"[DEBUG] MAC comparison: '{user_mac}' vs '{correct_mac}'")
            if user_mac == correct_mac:
                field["validated"] = True
                return True
            return False

        # Standard string comparison for other fields
        if user_value.lower() == correct_value.lower():
            field["validated"] = True
            return True
        return False

    def all_fields_validated(self):
        """Check if all fields are validated"""
        return all(field["validated"] for field in self.fields.values())

    def handle_keypress(self, event):
        """Handle keyboard input"""
        if self.active_field is None:
            return

        if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
            # Validate current field
            self.validate_field(self.active_field)

            # Move to next field
            current_index = self.field_order.index(self.active_field)
            if current_index < len(self.field_order) - 1:
                self.active_field = self.field_order[current_index + 1]
            else:
                self.active_field = None

        elif event.key == pygame.K_BACKSPACE:
            field = self.fields[self.active_field]
            field["value"] = field["value"][:-1]
            field["validated"] = False
            self.validate_field(self.active_field)

        elif event.unicode.isprintable():
            field = self.fields[self.active_field]
            if len(field["value"]) < 50:  # Max length
                field["value"] += event.unicode
                field["validated"] = False
                self.validate_field(self.active_field)

    def draw(self, background_surface: pygame.Surface = None):
        """Draw the mission notes popup"""
        # Draw background overlay
        if background_surface:
            self.screen.blit(background_surface, (0, 0))

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))

        # Popup panel (MUCH larger for bigger fonts)
        panel_width = int(850 * self.scale_x)  # Increased from 800
        panel_height = int(950 * self.scale_y)  # Increased from 800 (needs more space)
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=int(10 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, panel_rect, width=3, border_radius=int(10 * self.scale))

        # Title
        title_y = panel_y + int(30 * self.scale_y)
        title = self.title_font.render("📝 NOTES DE MISSION", True, self.label_color)
        title_rect = title.get_rect(centerx=self.screen_width // 2, top=title_y)
        self.screen.blit(title, title_rect)

        # Progress bar
        progress_y = title_rect.bottom + int(30 * self.scale_y)
        progress_width = int(600 * self.scale_x)
        progress_height = int(40 * self.scale_y)
        progress_x = (self.screen_width - progress_width) // 2

        progress_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
        pygame.draw.rect(self.screen, (30, 30, 35), progress_rect, border_radius=int(5 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, progress_rect, width=2, border_radius=int(5 * self.scale))

        # Progress fill
        progress = self.get_progress()
        fill_width = int((progress_width - 4) * (progress / 100))
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_x + 2, progress_y + 2, fill_width, progress_height - 4)
            pygame.draw.rect(self.screen, self.success_color, fill_rect, border_radius=int(3 * self.scale))

        # Progress text
        progress_text = self.body_font.render(f"{progress}%", True, self.text_color)
        progress_text_rect = progress_text.get_rect(center=progress_rect.center)
        self.screen.blit(progress_text, progress_text_rect)

        # Fields - START HIGHER to make room for buttons
        field_y = progress_rect.bottom + int(40 * self.scale_y)
        field_width = int(700 * self.scale_x)  # Increased from 650
        field_height = int(55 * self.scale_y)  # Increased from 50
        field_x = (self.screen_width - field_width) // 2

        mouse_pos = pygame.mouse.get_pos()
        self.field_rects = {}

        for field_key in self.field_order:
            field = self.fields[field_key]

            # Label
            label_text = self.body_font.render(field["label"] + ":", True, self.label_color)
            self.screen.blit(label_text, (field_x, field_y))

            # Input box
            input_y = field_y + label_text.get_height() + int(10 * self.scale_y)
            input_rect = pygame.Rect(field_x, input_y, field_width, field_height)
            self.field_rects[field_key] = input_rect

            is_active = (field_key == self.active_field)
            bg_color = self.input_active if is_active else self.input_bg

            # Validation color
            if field["validated"]:
                border_color = self.success_color
            elif field["value"] and not field["validated"]:
                border_color = self.error_color
            else:
                border_color = self.border_color if is_active else (60, 60, 65)

            pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=int(5 * self.scale))
            pygame.draw.rect(self.screen, border_color, input_rect, width=2, border_radius=int(5 * self.scale))

            # Input text
            if field["value"]:
                input_text = self.body_font.render(field["value"], True, self.text_color)
                self.screen.blit(input_text, (input_rect.x + int(15 * self.scale_x), input_rect.centery - input_text.get_height() // 2))

            # Validation checkmark
            if field["validated"]:
                check_text = self.heading_font.render("[OK]", True, self.success_color)
                self.screen.blit(check_text, (input_rect.right + int(15 * self.scale_x), input_rect.centery - check_text.get_height() // 2))

            field_y = input_rect.bottom + int(35 * self.scale_y)  # Increased from 30

        # Buttons - MOVE DOWN to prevent overlapping
        button_width = int(240 * self.scale_x)  # Increased from 220
        button_height = int(65 * self.scale_y)  # Increased from 60
        button_y = panel_rect.bottom - button_height - int(20 * self.scale_y)  # Moved down (reduced margin)
        
        # Make sure buttons don't go above fields
        if button_y < field_y + 50:
            button_y = field_y + 50

        # Send button
        send_x = self.screen_width // 2 - button_width - int(20 * self.scale_x)  # More spacing
        self.send_button_rect = pygame.Rect(send_x, button_y, button_width, button_height)

        is_send_enabled = self.all_fields_validated()
        is_send_hovered = self.send_button_rect.collidepoint(mouse_pos) and is_send_enabled

        if is_send_enabled:
            send_color = (0, 255, 120) if is_send_hovered else self.success_color
        else:
            send_color = (60, 60, 65)

        pygame.draw.rect(self.screen, send_color, self.send_button_rect, border_radius=int(8 * self.scale))

        send_text = self.heading_font.render("ENVOYER", True, (0, 0, 0) if is_send_enabled else (100, 100, 100))
        send_text_rect = send_text.get_rect(center=self.send_button_rect.center)
        self.screen.blit(send_text, send_text_rect)

        # Close button
        close_x = self.screen_width // 2 + int(20 * self.scale_x)  # More spacing
        self.close_button_rect = pygame.Rect(close_x, button_y, button_width, button_height)

        is_close_hovered = self.close_button_rect.collidepoint(mouse_pos)
        close_color = (70, 70, 75) if is_close_hovered else (50, 50, 55)

        pygame.draw.rect(self.screen, close_color, self.close_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, self.close_button_rect, width=2, border_radius=int(8 * self.scale))

        close_text = self.heading_font.render("FERMER", True, self.text_color)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        self.screen.blit(close_text, close_text_rect)

        # Instructions - MOVE DOWN BELOW BUTTONS
        instructions_y = button_y + button_height + int(20 * self.scale_y)
        instructions1 = self.small_font.render("Cliquez sur un champ pour le remplir | TAB: Champ suivant", True, (120, 120, 120))
        inst1_rect = instructions1.get_rect(centerx=self.screen_width // 2, top=instructions_y)
        self.screen.blit(instructions1, inst1_rect)

        # Hint about closing
        instructions2 = self.small_font.render("ECHAP: Fermer (vos donnees seront sauvegardees)", True, (0, 220, 50))
        inst2_rect = instructions2.get_rect(centerx=self.screen_width // 2, top=inst1_rect.bottom + int(10 * self.scale_y))
        self.screen.blit(instructions2, inst2_rect)

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click, return action if any"""
        # Check field clicks
        for field_key, rect in self.field_rects.items():
            if rect.collidepoint(pos):
                self.active_field = field_key
                return None

        # Check send button
        if self.send_button_rect and self.send_button_rect.collidepoint(pos):
            if self.all_fields_validated():
                return "send"

        # Check close button
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            return "close"

        # Click outside fields deactivates
        self.active_field = None
        return None

    def run(self, background_surface: pygame.Surface = None) -> Tuple[str, Dict]:
        """
        Run the mission notes popup

        Returns:
            Tuple of (result, field_values)
            result can be "send", "close", or "exit"
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Return current state even on quit
                    return "exit", self.fields

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Save current state when closing
                        return "close", self.fields
                    else:
                        self.handle_keypress(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        action = self.handle_click(event.pos)
                        if action == "send":
                            # Return collected data (keep original format for send)
                            data = {key: field["value"] for key, field in self.fields.items()}
                            return "send", data
                        elif action == "close":
                            # Save current state when closing
                            return "close", self.fields

            self.draw(background_surface)
            pygame.display.flip()

        return "close", self.fields