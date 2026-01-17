"""
Interactive Desktop - CyberHero OS
Fully interactive desktop with clickable application icons
Replaces static image-based desktop with dynamic UI
"""

import pygame
import os
from datetime import datetime
from typing import Optional, Tuple, Dict, List

class InteractiveDesktop:
    """
    Interactive desktop interface with application icons and status bar
    """

    def __init__(self, screen, player_profile):
        """
        Initialize interactive desktop

        Args:
            screen: Pygame screen surface
            player_profile: Player's profile data
        """
        self.screen = screen
        self.player_profile = player_profile
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()

        # Calculate scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Import notification manager
        from src.systems.notification_manager import get_notification_manager
        self.notification_manager = get_notification_manager()

        # Colors - Cyberpunk theme
        self.bg_color = (10, 14, 39)           # #0a0e27
        self.title_bg = (26, 31, 58)           # #1a1f3a
        self.icon_bg = (26, 31, 58)            # #1a1f3a
        self.icon_hover = (42, 63, 90)         # #2a3f5a
        self.border_color = (42, 63, 90)       # #2a3f5a

        # Icon colors
        self.terminal_color = (0, 255, 65)     # #00ff41
        self.mail_color = (0, 212, 255)        # #00d4ff
        self.packet_color = (255, 149, 0)      # #ff9500
        self.network_color = (255, 0, 255)     # #ff00ff
        self.security_color = (255, 68, 68)    # #ff4444
        self.contracts_color = (255, 255, 0)   # #ffff00
        self.knowledge_color = (68, 68, 255)   # #4444ff
        self.shop_color = (68, 255, 68)        # #44ff44

        # Status colors
        self.credits_color = (255, 255, 0)     # Yellow
        self.rep_color = (0, 255, 65)          # Green
        self.alerts_color = (255, 68, 68)      # Red

        # Fonts - LARGER sizes for better readability
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * self.scale))
            self.icon_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
            self.status_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * self.scale))
            self.time_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * self.scale))
            self.icon_font = pygame.font.Font(None, int(32 * self.scale))
            self.status_font = pygame.font.Font(None, int(26 * self.scale))
            self.time_font = pygame.font.Font(None, int(32 * self.scale))

        # Application icons (3x3 grid - 9 core apps for Terminal Zero)
        self.icons = [
            {"name": "Terminal", "color": self.terminal_color, "action": "terminal"},
            {"name": "Net Scanner", "color": self.packet_color, "action": "net_scanner"},
            {"name": "Packet Lab", "color": self.network_color, "action": "packet_lab"},
            {"name": "Navigateur", "color": self.mail_color, "action": "browser"},
            {"name": "Firewall", "color": self.security_color, "action": "firewall"},
            {"name": "Logs", "color": self.contracts_color, "action": "logs"},
            {"name": "Notes", "color": self.knowledge_color, "action": "notes"},
            {"name": "Peripheriques", "color": self.shop_color, "action": "devices"},
            {"name": "Carriere", "color": (255, 215, 0), "action": "career"},
        ]

        # Calculate icon layout
        self.icon_width = int(240 * self.scale_x)
        self.icon_height = int(120 * self.scale_y)
        self.icon_spacing_x = int(25 * self.scale_x)
        self.icon_spacing_y = int(25 * self.scale_y)

        # Calculate grid positioning (centered)
        self.grid_cols = 3
        self.grid_rows = 3
        total_width = (self.icon_width * self.grid_cols) + (self.icon_spacing_x * (self.grid_cols - 1))
        total_height = (self.icon_height * self.grid_rows) + (self.icon_spacing_y * (self.grid_rows - 1))

        self.grid_start_x = (self.screen_width - total_width) // 2
        self.grid_start_y = int(100 * self.scale_y) + int((self.screen_height - 100 * self.scale_y - 80 * self.scale_y - total_height) // 2)

        # Hovered icon
        self.hovered_icon = None


        # Back button rect
        self.back_button_rect = None

        # Player stats (from profile)
        self.update_player_stats()

    def update_player_stats(self):
        """Update player statistics from profile"""
        progress = self.player_profile.get('progress', {})

        self.credits = progress.get('credits', 2500)
        self.reputation = progress.get('reputation', 3)
        self.level = progress.get('level', 'Debutant')

        # Count new contracts and alerts
        completed_missions = progress.get('missions_completed', [])
        unlocked_missions = progress.get('unlocked_missions', ['mission1'])

        self.new_contracts = len(unlocked_missions) - len(completed_missions)
        self.alerts = progress.get('alerts', 2)

    def draw_title_bar(self, mouse_pos):
        """Draw top title bar with time and settings icon"""
        # Title bar background
        title_bar_rect = pygame.Rect(0, 0, self.screen_width, int(70 * self.scale_y))
        pygame.draw.rect(self.screen, self.title_bg, title_bar_rect)

        # Retour Button (Top Right)
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        self.back_button_rect = pygame.Rect(self.screen_width - button_width - int(20 * self.scale_x), int(15 * self.scale_y), button_width, button_height)
        
        is_back_hovered = self.back_button_rect.collidepoint(mouse_pos)
        back_color = (200, 60, 60) if is_back_hovered else (160, 40, 40) # Reddish for exit
        
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=int(5 * self.scale))
        
        back_text = self.status_font.render("RETOUR", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Title text
        title_text = self.title_font.render("CYBER HERO OS", True, self.terminal_color)
        title_rect = title_text.get_rect(left=int(30 * self.scale_x), centery=int(35 * self.scale_y))
        self.screen.blit(title_text, title_rect)

        # Current time
        current_time = datetime.now().strftime("[%H:%M:%S]")
        time_text = self.time_font.render(current_time, True, self.terminal_color)
        time_rect = time_text.get_rect(right=self.back_button_rect.left - int(30 * self.scale_x), centery=int(35 * self.scale_y))
        self.screen.blit(time_text, time_rect)


    def draw_status_bar(self):
        """Draw bottom status bar with player stats - TEXT ONLY"""
        # Status bar background
        status_y = self.screen_height - int(80 * self.scale_y)
        status_rect = pygame.Rect(0, status_y, self.screen_width, int(80 * self.scale_y))
        pygame.draw.rect(self.screen, self.title_bg, status_rect)

        # Calculate total width needed for all stats
        spacing = int(50 * self.scale_x)
        
        # Credits
        credits_text = self.status_font.render(f"Credits: {self.credits}€", True, self.credits_color)
        credits_rect = credits_text.get_rect(left=int(30 * self.scale_x), centery=status_y + int(40 * self.scale_y))
        self.screen.blit(credits_text, credits_rect)

        # Reputation
        rep_text = self.status_font.render(f"Rep: {self.level}", True, self.rep_color)
        rep_rect = rep_text.get_rect(left=credits_rect.right + spacing, centery=status_y + int(40 * self.scale_y))
        self.screen.blit(rep_text, rep_rect)

        # New Contracts
        contracts_text = self.status_font.render(f"Nouveaux Contrats: {self.new_contracts}", True, self.mail_color)
        contracts_rect = contracts_text.get_rect(left=rep_rect.right + spacing, centery=status_y + int(40 * self.scale_y))
        self.screen.blit(contracts_text, contracts_rect)

        # Alerts
        alerts_text = self.status_font.render(f"Alertes: {self.alerts}", True, self.alerts_color)
        alerts_rect = alerts_text.get_rect(left=contracts_rect.right + spacing, centery=status_y + int(40 * self.scale_y))
        self.screen.blit(alerts_text, alerts_rect)

    def draw_icon_grid(self, mouse_pos):
        """Draw grid of application icons - TEXT ONLY"""
        icon_rects = []

        for idx, icon in enumerate(self.icons):
            row = idx // self.grid_cols
            col = idx % self.grid_cols

            x = self.grid_start_x + col * (self.icon_width + self.icon_spacing_x)
            y = self.grid_start_y + row * (self.icon_height + self.icon_spacing_y)

            # Create icon rect
            icon_rect = pygame.Rect(x, y, self.icon_width, self.icon_height)
            icon_rects.append((icon_rect, icon))

            # Check if hovered
            is_hovered = icon_rect.collidepoint(mouse_pos)

            # Background color
            bg_color = self.icon_hover if is_hovered else self.icon_bg

            # Draw icon background
            pygame.draw.rect(self.screen, bg_color, icon_rect, border_radius=int(8 * self.scale))

            # Draw border (highlighted if hovered)
            border_color = icon['color'] if is_hovered else self.border_color
            border_width = int(3 * self.scale) if is_hovered else int(2 * self.scale)
            pygame.draw.rect(self.screen, border_color, icon_rect, border_width, border_radius=int(8 * self.scale))

            # Draw icon name ONLY - centered in the box
            name_text = self.icon_font.render(icon['name'], True, icon['color'])
            name_rect = name_text.get_rect(center=icon_rect.center)
            self.screen.blit(name_text, name_rect)

        return icon_rects

    def draw(self, mouse_pos):
        """Draw the entire desktop"""
        # Background
        self.screen.fill(self.bg_color)

        # Title bar (with settings icon)
        self.draw_title_bar(mouse_pos)

        # Icon grid
        icon_rects = self.draw_icon_grid(mouse_pos)

        # Status bar
        self.draw_status_bar()

        return icon_rects

    def handle_click(self, mouse_pos, icon_rects) -> Optional[str]:
        """
        Handle click on desktop icons and settings

        Returns:
            Action string if an icon was clicked, None otherwise
        """
        # Check back button
        if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
            return "back_button"

        # Check application icons
        for icon_rect, icon in icon_rects:
            if icon_rect.collidepoint(mouse_pos):
                return icon['action']

        return None

    def show_confirmation_popup(self):
        """Show confirmation popup for returning to main menu"""
        # Create overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog dimensions
        dialog_width = int(500 * self.scale_x)
        dialog_height = int(250 * self.scale_y)
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        # Draw dialog background
        pygame.draw.rect(self.screen, self.title_bg,
                        (dialog_x, dialog_y, dialog_width, dialog_height), 
                        border_radius=int(15 * self.scale))
        pygame.draw.rect(self.screen, self.terminal_color,
                        (dialog_x, dialog_y, dialog_width, dialog_height), 
                        int(3 * self.scale), border_radius=int(15 * self.scale))
        
        # Question text
        question = self.status_font.render("Retour au menu principal ?", True, self.terminal_color)
        question_rect = question.get_rect(centerx=self.screen_width // 2, top=dialog_y + 40)
        self.screen.blit(question, question_rect)
        
        # Warning text
        warning_color = (220, 220, 225)  # Light gray for text
        warning = self.status_font.render("Les modifications non sauvegardées seront perdues.", True, warning_color)
        warning_rect = warning.get_rect(centerx=self.screen_width // 2, top=dialog_y + 75)
        self.screen.blit(warning, warning_rect)
        
        # Buttons
        button_width = int(140 * self.scale_x)
        button_height = int(50 * self.scale_y)
        button_y = dialog_y + dialog_height - 70
        
        oui_x = self.screen_width // 2 - button_width - 20
        non_x = self.screen_width // 2 + 20
        
        # Draw buttons
        oui_rect = pygame.Rect(oui_x, button_y, button_width, button_height)
        non_rect = pygame.Rect(non_x, button_y, button_width, button_height)
        
        # Button backgrounds
        pygame.draw.rect(self.screen, (30, 60, 30), oui_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, (60, 30, 30), non_rect, border_radius=int(8 * self.scale))
        
        # Button borders
        pygame.draw.rect(self.screen, self.rep_color, oui_rect,
                        int(2 * self.scale), border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.alerts_color, non_rect,
                        int(2 * self.scale), border_radius=int(8 * self.scale))
        
        # Button text
        oui_text = self.status_font.render("OUI", True, self.rep_color)
        non_text = self.status_font.render("NON", True, self.alerts_color)
        
        self.screen.blit(oui_text, oui_text.get_rect(center=oui_rect.center))
        self.screen.blit(non_text, non_text.get_rect(center=non_rect.center))
        
        pygame.display.flip()
        
        # Wait for input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y or event.key == pygame.K_o or event.key == pygame.K_RETURN:
                        return True  # OUI - exit game
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        return False  # NON - stay on desktop
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click only
                        if oui_rect.collidepoint(event.pos):
                            return True  # OUI - exit game
                        elif non_rect.collidepoint(event.pos):
                            return False  # NON - stay on desktop
        
        return False

    def run(self) -> Tuple[str, Optional[str]]:
        """
        Run the interactive desktop

        Returns:
            (result, action) tuple
            result: "exit", "action", "menu", "restart"
            action: clicked application action
        """
        running = True
        icon_rects = []

        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            mouse_pos = pygame.mouse.get_pos()

            # Update notification animation
            self.notification_manager.update(dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Show confirmation popup
                        confirmed = self.show_confirmation_popup()
                        if confirmed:  # User clicked OUI
                            return "restart", None  # Signal to restart the game
                        # If not confirmed (NON clicked), continue normally
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        action = self.handle_click(mouse_pos, icon_rects)
                        if action:
                            if action == "back_button":
                                confirmed = self.show_confirmation_popup()
                                if confirmed:
                                    return "restart", None
                                continue
                            return "action", action

            # Draw (this will clear the popup if NON was clicked)
            icon_rects = self.draw(mouse_pos)
            pygame.display.flip()

        return "exit", None