"""
Mission 2 Notes UI - CyberHero
Popup window for collecting packet analysis information
"""

import pygame
from typing import Tuple, Dict, Optional, List


class Mission2NotesPopup:
    """
    Mission 2 notes popup for packet analysis
    Player fills in fields based on Wireshark analysis
    """

    def __init__(self, screen, profile_data: Dict, mission=None, persisted_data: Dict = None):
        """
        Initialize mission 2 notes popup

        Args:
            screen: Pygame screen surface
            profile_data: Player profile
            mission: Mission2PacketAnalysis instance (optional)
            persisted_data: Previously entered field data (to restore on reopen)
        """
        self.screen = screen
        self.profile_data = profile_data
        self.mission = mission
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors
        self.bg_color = (15, 15, 20, 230)  # Semi-transparent dark
        self.panel_bg = (25, 28, 35)
        self.border_color = (0, 180, 220)  # Cyber blue
        self.text_color = (200, 200, 210)
        self.label_color = (0, 180, 220)
        self.input_bg = (35, 38, 45)
        self.input_active = (45, 48, 55)
        self.success_color = (0, 220, 100)
        self.error_color = (220, 80, 80)
        self.warning_color = (220, 180, 50)

        # Fonts - Standardized sizes (matching desktop)
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

        # Mission 2 fields - Packet analysis
        # Correct answers based on the suspicious packets in Wireshark
        self.fields = {
            "suspicious_ip": {
                "label": "Adresse IP de l'intrus",
                "value": "",
                "correct": "192.168.1.66",
                "validated": False,
                "hint": "Regardez la colonne Source des paquets suspects"
            },
            "threat_telnet": {
                "label": "Port Telnet cible",
                "value": "",
                "correct": "23",
                "validated": False,
                "hint": "Port utilise pour les connexions Telnet"
            },
            "threat_ports": {
                "label": "Ports scannes (separes par virgule)",
                "value": "",
                "correct": "22,23,80,443,3389",
                "validated": False,
                "hint": "Liste des ports dans le scan de ports"
            },
            "printer_port": {
                "label": "Port d'exploitation imprimante",
                "value": "",
                "correct": "9100",
                "validated": False,
                "hint": "Port RAW pour imprimantes reseau"
            },
            "exfil_ip": {
                "label": "IP de destination exfiltration",
                "value": "",
                "correct": "185.234.72.100",
                "validated": False,
                "hint": "Adresse externe dans le paquet d'exfiltration"
            },
            "total_threats": {
                "label": "Nombre total de menaces",
                "value": "",
                "correct": "5",
                "validated": False,
                "hint": "Comptez tous les paquets suspects"
            }
        }

        # Restore persisted data if available
        if persisted_data:
            for key in self.fields:
                if key in persisted_data:
                    self.fields[key]["value"] = persisted_data[key].get("value", "")
                    self.fields[key]["validated"] = persisted_data[key].get("validated", False)

        self.active_field = None
        self.field_order = ["suspicious_ip", "threat_telnet", "threat_ports", "printer_port", "exfil_ip", "total_threats"]
        self.field_rects = {}

        # Buttons
        self.send_button_rect = None
        self.close_button_rect = None

    def get_progress(self):
        """Calculate progress percentage"""
        validated_count = sum(1 for field in self.fields.values() if field["validated"])
        total_count = len(self.fields)
        return int((validated_count / total_count) * 100)

    def validate_field(self, field_key: str) -> bool:
        """Validate a field's value"""
        field = self.fields[field_key]
        user_value = field["value"].strip()
        correct_value = field["correct"].strip()

        print(f"[DEBUG] Validating {field_key}: user='{user_value}' vs correct='{correct_value}'")

        # Special handling for ports list - order doesn't matter
        if field_key == "threat_ports":
            user_ports = set(p.strip() for p in user_value.split(",") if p.strip())
            correct_ports = set(p.strip() for p in correct_value.split(","))
            print(f"[DEBUG] Ports comparison: {user_ports} vs {correct_ports}")
            if user_ports == correct_ports:
                field["validated"] = True
                return True
            return False

        # Standard comparison for other fields
        if user_value.lower() == correct_value.lower():
            field["validated"] = True
            return True
        return False

    def all_fields_validated(self) -> bool:
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
        """Draw the mission 2 notes popup"""
        # Draw background overlay
        if background_surface:
            self.screen.blit(background_surface, (0, 0))

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))

        # Popup panel - larger for more fields
        panel_width = int(750 * self.scale_x)
        panel_height = int(720 * self.scale_y)
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=int(12 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, panel_rect, width=3, border_radius=int(12 * self.scale))

        # Title
        title_y = panel_y + int(20 * self.scale_y)
        title = self.title_font.render("RAPPORT D'ANALYSE DE PAQUETS", True, self.label_color)
        title_rect = title.get_rect(centerx=self.screen_width // 2, top=title_y)
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.small_font.render("Mission 2: Detection d'Intrusion", True, self.warning_color)
        subtitle_rect = subtitle.get_rect(centerx=self.screen_width // 2, top=title_rect.bottom + int(5 * self.scale_y))
        self.screen.blit(subtitle, subtitle_rect)

        # Progress bar
        progress_y = subtitle_rect.bottom + int(20 * self.scale_y)
        progress_width = int(650 * self.scale_x)
        progress_height = int(35 * self.scale_y)
        progress_x = (self.screen_width - progress_width) // 2

        progress_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
        pygame.draw.rect(self.screen, (30, 32, 40), progress_rect, border_radius=int(6 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, progress_rect, width=2, border_radius=int(6 * self.scale))

        # Progress fill
        progress = self.get_progress()
        fill_width = int((progress_width - 4) * (progress / 100))
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_x + 2, progress_y + 2, fill_width, progress_height - 4)
            pygame.draw.rect(self.screen, self.success_color, fill_rect, border_radius=int(4 * self.scale))

        # Progress text
        progress_text = self.body_font.render(f"Progression: {progress}%", True, self.text_color)
        progress_text_rect = progress_text.get_rect(center=progress_rect.center)
        self.screen.blit(progress_text, progress_text_rect)

        # Fields
        field_y = progress_rect.bottom + int(25 * self.scale_y)
        field_width = int(600 * self.scale_x)
        field_height = int(42 * self.scale_y)
        field_x = (self.screen_width - field_width) // 2

        mouse_pos = pygame.mouse.get_pos()
        self.field_rects = {}

        for field_key in self.field_order:
            field = self.fields[field_key]

            # Label
            label_text = self.body_font.render(field["label"] + ":", True, self.label_color)
            self.screen.blit(label_text, (field_x, field_y))

            # Input box
            input_y = field_y + label_text.get_height() + int(5 * self.scale_y)
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
                border_color = self.border_color if is_active else (60, 62, 70)

            pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=int(6 * self.scale))
            pygame.draw.rect(self.screen, border_color, input_rect, width=2, border_radius=int(6 * self.scale))

            # Input text or placeholder
            if field["value"]:
                input_text = self.body_font.render(field["value"], True, self.text_color)
            else:
                # Show hint as placeholder
                input_text = self.small_font.render(field["hint"], True, (80, 82, 90))

            self.screen.blit(input_text, (input_rect.x + int(12 * self.scale_x), input_rect.centery - input_text.get_height() // 2))

            # Validation checkmark
            if field["validated"]:
                check_text = self.heading_font.render("OK", True, self.success_color)
                self.screen.blit(check_text, (input_rect.right + int(12 * self.scale_x), input_rect.centery - check_text.get_height() // 2))

            field_y = input_rect.bottom + int(15 * self.scale_y)

        # Buttons
        button_width = int(220 * self.scale_x)
        button_height = int(55 * self.scale_y)
        button_y = panel_rect.bottom - button_height - int(20 * self.scale_y)

        # Send button
        send_x = self.screen_width // 2 - button_width - int(15 * self.scale_x)
        self.send_button_rect = pygame.Rect(send_x, button_y, button_width, button_height)

        is_send_enabled = self.all_fields_validated()
        is_send_hovered = self.send_button_rect.collidepoint(mouse_pos) and is_send_enabled

        if is_send_enabled:
            send_color = (0, 255, 120) if is_send_hovered else self.success_color
        else:
            send_color = (50, 52, 60)

        pygame.draw.rect(self.screen, send_color, self.send_button_rect, border_radius=int(8 * self.scale))

        send_text = self.heading_font.render("ENVOYER", True, (0, 0, 0) if is_send_enabled else (90, 90, 100))
        send_text_rect = send_text.get_rect(center=self.send_button_rect.center)
        self.screen.blit(send_text, send_text_rect)

        # Close button
        close_x = self.screen_width // 2 + int(15 * self.scale_x)
        self.close_button_rect = pygame.Rect(close_x, button_y, button_width, button_height)

        is_close_hovered = self.close_button_rect.collidepoint(mouse_pos)
        close_color = (70, 72, 80) if is_close_hovered else (50, 52, 60)

        pygame.draw.rect(self.screen, close_color, self.close_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, self.close_button_rect, width=2, border_radius=int(8 * self.scale))

        close_text = self.heading_font.render("FERMER", True, self.text_color)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        self.screen.blit(close_text, close_text_rect)

        # Instructions
        instructions = self.small_font.render("Cliquez sur un champ pour le remplir | TAB: Champ suivant | ECHAP: Fermer", True, (100, 102, 110))
        inst_rect = instructions.get_rect(centerx=self.screen_width // 2, top=panel_rect.bottom + int(12 * self.scale_y))
        self.screen.blit(instructions, inst_rect)

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
        Run the mission 2 notes popup

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
                    return "exit", self.fields

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "close", self.fields
                    else:
                        self.handle_keypress(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        action = self.handle_click(event.pos)
                        if action == "send":
                            # Return collected data
                            data = {key: field["value"] for key, field in self.fields.items()}
                            return "send", data
                        elif action == "close":
                            return "close", self.fields

            self.draw(background_surface)
            pygame.display.flip()

        return "close", self.fields
