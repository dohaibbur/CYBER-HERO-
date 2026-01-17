"""
Tutorial Popup Overlay
Shows mission instructions and guides player to specific desktop apps
"""

import pygame
from typing import Optional, Tuple


class TutorialPopup:
    """
    A popup overlay that displays tutorial messages and points to desktop icons
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Colors - sleek dark theme
        self.overlay_bg = (0, 0, 0, 180)  # Semi-transparent black
        self.popup_bg = (20, 20, 25)
        self.border_color = (0, 220, 50)  # Matrix green
        self.text_color = (220, 220, 220)
        self.text_highlight = (0, 240, 60)
        self.button_bg = (0, 200, 40)
        self.button_hover = (0, 240, 60)

        # Fonts - Standardized sizes (matching desktop)
        scale = min(self.width / 1920, self.height / 1080)
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * scale))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * scale))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(22 * scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * scale))
            self.body_font = pygame.font.Font(None, int(26 * scale))
            self.small_font = pygame.font.Font(None, int(22 * scale))

        # Button rect
        self.button_rect = None

    def show_navigator_prompt(self, navigator_icon_pos: Optional[Tuple[int, int]] = None, desktop=None) -> str:
        """
        Show prompt to open Navigator for first time

        Args:
            navigator_icon_pos: (x, y) position of Navigator icon to point arrow at
            desktop: Desktop instance to draw behind popup (optional)

        Returns:
            "continue" when player closes popup
        """
        clock = pygame.time.Clock()
        running = True

        # Draw desktop once and capture for blurring
        background_surface = None
        if desktop:
            # Get mouse position for desktop drawing
            initial_mouse_pos = pygame.mouse.get_pos()
            desktop.draw(initial_mouse_pos)
            pygame.display.flip()
            # Capture the desktop
            background_surface = self.screen.copy()

        while running:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        return "continue"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.button_rect and self.button_rect.collidepoint(event.pos):
                            return "continue"

            # Draw everything
            self._draw_navigator_prompt(mouse_pos, navigator_icon_pos, background_surface)
            pygame.display.flip()

        return "continue"

    def _draw_navigator_prompt(self, mouse_pos: Tuple[int, int],
                                icon_pos: Optional[Tuple[int, int]],
                                background_surface: Optional[pygame.Surface] = None):
        """Draw the navigator prompt overlay"""

        # Draw blurred background if provided
        if background_surface:
            # Draw the background
            self.screen.blit(background_surface, (0, 0))

            # Apply blur effect by drawing darkened semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # Dark with alpha for blur effect
            self.screen.blit(overlay, (0, 0))
        else:
            # Fallback: Create semi-transparent overlay over black
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill(self.overlay_bg)
            self.screen.blit(overlay, (0, 0))

        # Calculate popup dimensions
        popup_width = int(self.width * 0.5)
        popup_height = int(self.height * 0.4)
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2 - int(self.height * 0.1)

        # Draw popup box with glow effect
        for i in range(3):
            glow_rect = pygame.Rect(
                popup_x - i * 2,
                popup_y - i * 2,
                popup_width + i * 4,
                popup_height + i * 4
            )
            alpha = 30 - i * 10
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.border_color, alpha),
                           glow_surface.get_rect(), border_radius=15)
            self.screen.blit(glow_surface, glow_rect.topleft)

        # Main popup background
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, self.popup_bg, popup_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, popup_rect, width=3, border_radius=12)

        # Title
        title_text = "MISSION: ACCES AU RESEAU"
        title_surf = self.title_font.render(title_text, True, self.text_highlight)
        title_x = popup_x + (popup_width - title_surf.get_width()) // 2
        title_y = popup_y + int(popup_height * 0.12)
        self.screen.blit(title_surf, (title_x, title_y))

        # Divider line
        line_y = title_y + title_surf.get_height() + int(popup_height * 0.05)
        line_start = (popup_x + int(popup_width * 0.1), line_y)
        line_end = (popup_x + int(popup_width * 0.9), line_y)
        pygame.draw.line(self.screen, self.border_color, line_start, line_end, 2)

        # Body text
        body_lines = [
            "Pour commencer votre parcours de hacker,",
            "vous devez acceder au Deep Web.",
            "",
            "Ouvrez le NAVIGATEUR pour continuer."
        ]

        body_y = line_y + int(popup_height * 0.08)
        for line in body_lines:
            if line:
                body_surf = self.body_font.render(line, True, self.text_color)
                body_x = popup_x + (popup_width - body_surf.get_width()) // 2
                self.screen.blit(body_surf, (body_x, body_y))
            body_y += self.body_font.get_height() + 5

        # Button
        button_width = int(popup_width * 0.35)
        button_height = int(popup_height * 0.15)
        button_x = popup_x + (popup_width - button_width) // 2
        button_y = popup_y + popup_height - button_height - int(popup_height * 0.12)

        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Check hover
        is_hovered = self.button_rect.collidepoint(mouse_pos)
        button_color = self.button_hover if is_hovered else self.button_bg

        # Draw button
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, self.button_rect, width=2, border_radius=8)

        button_text = "COMPRIS"
        button_surf = self.body_font.render(button_text, True, (0, 0, 0))
        button_text_x = button_x + (button_width - button_surf.get_width()) // 2
        button_text_y = button_y + (button_height - button_surf.get_height()) // 2
        self.screen.blit(button_surf, (button_text_x, button_text_y))

        # Draw arrow pointing to Navigator icon (if position provided)
        if icon_pos:
            self._draw_arrow_to_icon(popup_rect, icon_pos)

    def _draw_arrow_to_icon(self, popup_rect: pygame.Rect, icon_pos: Tuple[int, int]):
        """Draw an animated arrow pointing from popup to icon"""

        # Calculate arrow start (bottom of popup)
        arrow_start_x = popup_rect.centerx
        arrow_start_y = popup_rect.bottom + 20

        # Arrow end (icon position)
        arrow_end_x, arrow_end_y = icon_pos

        # Animate arrow (pulse effect)
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0  # 0 to 1 to 0
        arrow_alpha = int(150 + pulse * 105)  # 150-255

        # Draw arrow line
        arrow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.line(arrow_surface, (*self.text_highlight, arrow_alpha),
                        (arrow_start_x, arrow_start_y),
                        (arrow_end_x, arrow_end_y), 4)

        # Draw arrowhead
        import math
        angle = math.atan2(arrow_end_y - arrow_start_y, arrow_end_x - arrow_start_x)
        arrow_size = 20

        point1 = (arrow_end_x, arrow_end_y)
        point2 = (
            arrow_end_x - arrow_size * math.cos(angle - math.pi/6),
            arrow_end_y - arrow_size * math.sin(angle - math.pi/6)
        )
        point3 = (
            arrow_end_x - arrow_size * math.cos(angle + math.pi/6),
            arrow_end_y - arrow_size * math.sin(angle + math.pi/6)
        )

        pygame.draw.polygon(arrow_surface, (*self.text_highlight, arrow_alpha),
                          [point1, point2, point3])

        self.screen.blit(arrow_surface, (0, 0))

        # Draw glow circle around icon
        glow_radius = int(40 + pulse * 15)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.text_highlight, int(50 + pulse * 50)),
                         (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surface, (arrow_end_x - glow_radius, arrow_end_y - glow_radius))


def show_tutorial_popup(screen: pygame.Surface, popup_type: str, desktop=None, **kwargs) -> str:
    """
    Convenience function to show tutorial popups

    Args:
        screen: Pygame screen surface
        popup_type: Type of popup ("navigator", "terminal", "email", etc.)
        desktop: Desktop instance for background (optional)
        **kwargs: Additional arguments (e.g., icon_pos)

    Returns:
        Result string ("continue", "exit", etc.)
    """
    popup = TutorialPopup(screen)

    if popup_type == "navigator":
        return popup.show_navigator_prompt(kwargs.get('icon_pos'), desktop)

    return "continue"
