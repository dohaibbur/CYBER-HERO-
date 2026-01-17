"""
Empty App - Placeholder for apps under development
Used for: Firewall, Logs, Notes, Peripheriques
"""

import pygame
from typing import Dict, Tuple, Optional


class EmptyApp:
    """
    Empty application placeholder
    Shows a "coming soon" style page
    """

    def __init__(self, screen, profile_data: Dict, app_name: str, app_description: str):
        """
        Initialize Empty App

        Args:
            screen: Pygame screen surface
            profile_data: Player profile data
            app_name: Display name of the app
            app_description: Description text
        """
        self.screen = screen
        self.profile_data = profile_data
        self.app_name = app_name
        self.app_description = app_description
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors
        self.bg_color = (15, 20, 25)
        self.panel_bg = (25, 30, 40)
        self.header_bg = (20, 25, 35)
        self.primary_color = (0, 200, 255)
        self.dim_color = (100, 105, 115)
        self.text_color = (200, 200, 210)
        self.button_bg = (40, 45, 60)
        self.button_hover = (60, 65, 85)
        self.success_color = (0, 220, 100)

        # Fonts
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * self.scale))
            self.heading_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * self.scale))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(22 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * self.scale))
            self.heading_font = pygame.font.Font(None, int(32 * self.scale))
            self.body_font = pygame.font.Font(None, int(26 * self.scale))
            self.small_font = pygame.font.Font(None, int(22 * self.scale))

        self.back_button_rect = None

    def draw_back_button(self, mouse_pos):
        """Draw the clickable back button"""
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_x = self.screen_width - button_width - int(30 * self.scale_x)
        button_y = (int(60 * self.scale_y) - button_height) // 2

        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)

        button_bg = self.button_hover if is_hovered else self.button_bg
        pygame.draw.rect(self.screen, button_bg, self.back_button_rect, border_radius=int(6 * self.scale))

        border_color = self.success_color if is_hovered else self.primary_color
        pygame.draw.rect(self.screen, border_color, self.back_button_rect, width=2, border_radius=int(6 * self.scale))

        back_text = self.body_font.render("RETOUR", True, self.text_color)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_rect)

        return is_hovered

    def draw(self):
        """Draw the empty app interface"""
        self.screen.fill(self.bg_color)

        # Header bar
        header_height = int(60 * self.scale_y)
        header_rect = pygame.Rect(0, 0, self.screen_width, header_height)
        pygame.draw.rect(self.screen, self.header_bg, header_rect)
        pygame.draw.line(self.screen, self.primary_color, (0, header_height), (self.screen_width, header_height), 2)

        # Title
        title = self.title_font.render(self.app_name.upper(), True, self.primary_color)
        self.screen.blit(title, (int(30 * self.scale_x), header_height // 2 - title.get_height() // 2))

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Draw back button
        is_back_hovered = self.draw_back_button(mouse_pos)

        if is_back_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Content area - centered message
        content_y = header_height + int(100 * self.scale_y)
        center_x = self.screen_width // 2

        # Main panel
        panel_width = int(600 * self.scale_x)
        panel_height = int(300 * self.scale_y)
        panel_x = center_x - panel_width // 2
        panel_y = content_y

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=int(10 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, panel_rect, width=2, border_radius=int(10 * self.scale))

        # App name in panel
        app_title = self.heading_font.render(self.app_name, True, self.primary_color)
        app_title_rect = app_title.get_rect(centerx=center_x, top=panel_y + int(40 * self.scale_y))
        self.screen.blit(app_title, app_title_rect)

        # Description
        desc_text = self.body_font.render(self.app_description, True, self.text_color)
        desc_rect = desc_text.get_rect(centerx=center_x, top=panel_y + int(100 * self.scale_y))
        self.screen.blit(desc_text, desc_rect)

        # Status message
        status_text = self.body_font.render("Aucun contenu disponible.", True, self.dim_color)
        status_rect = status_text.get_rect(centerx=center_x, top=panel_y + int(160 * self.scale_y))
        self.screen.blit(status_text, status_rect)

        # Hint
        hint_text = self.small_font.render("Cette fonctionnalite sera disponible prochainement.", True, self.dim_color)
        hint_rect = hint_text.get_rect(centerx=center_x, top=panel_y + int(220 * self.scale_y))
        self.screen.blit(hint_text, hint_rect)

    def run(self) -> str:
        """
        Run the empty app

        Returns:
            "desktop" to return to desktop
            "exit" if window closed
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        return "desktop"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                            return "desktop"

            self.draw()
            pygame.display.flip()

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return "desktop"
