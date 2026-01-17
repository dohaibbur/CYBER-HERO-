"""
Deep Web Loading Screen
Simulates connecting to Tor network before accessing forum
"""

import pygame
import random
from typing import List


class DeepWebLoader:
    """
    Loading screen that simulates connecting to deep web via Tor
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Colors
        self.bg_color = (8, 8, 10)  # Almost black
        self.text_color = (0, 220, 50)  # Matrix green
        self.text_dim = (0, 150, 30)
        self.text_success = (0, 255, 80)
        self.progress_bar_bg = (30, 30, 35)
        self.progress_bar_fill = (0, 220, 50)

        # Fonts - Standardized sizes (matching desktop)
        scale = min(self.width / 1920, self.height / 1080)
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * scale))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * scale))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(22 * scale))
            self.mono_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * scale))
            self.body_font = pygame.font.Font(None, int(26 * scale))
            self.small_font = pygame.font.Font(None, int(22 * scale))
            self.mono_font = pygame.font.Font(None, int(26 * scale))

        # Loading stages with durations (ms)
        self.stages = [
            ("Initialisation de Tor...", 1200, False),
            ("Connexion au reseau Onion...", 1800, False),
            ("Etablissement d'un circuit securise...", 1400, False),
            ("Verification de l'anonymat...", 1000, False),
            ("Connexion au Deep Web reussie!", 600, True)
        ]

        self.current_stage = 0
        self.stage_start_time = 0
        self.completed_stages = []
        self.background_capture = None

    def show_loading(self) -> str:
        """
        Show 'Connecting to Deep Web' loading animation

        Returns:
            "complete" when loading finished
            "exit" if user closed window
        """
        clock = pygame.time.Clock()
        self.stage_start_time = pygame.time.get_ticks()
        total_start_time = pygame.time.get_ticks()

        # Capture background for popup effect
        self.background_capture = self.screen.copy()

        # Generate random IP addresses for effect
        self.relay_ips = [
            f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            for _ in range(5)
        ]

        while True:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
                    elif event.key == pygame.K_SPACE:
                        # Skip all loading stages
                        return "complete"

            # Check if current stage is complete
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.stage_start_time

            if self.current_stage < len(self.stages):
                stage_duration = self.stages[self.current_stage][1]

                if elapsed >= stage_duration:
                    # Mark stage as completed
                    self.completed_stages.append(self.current_stage)
                    self.current_stage += 1
                    self.stage_start_time = current_time

            # Check if all stages complete
            if self.current_stage >= len(self.stages):
                # Wait a moment before returning
                if current_time - total_start_time > 6500:
                    return "complete"

            # Draw
            self._draw_loading_screen()
            pygame.display.flip()

        return "complete"

    def _draw_loading_screen(self):
        """Draw the loading screen with stages and progress"""

        # Draw background and overlay
        if self.background_capture:
            self.screen.blit(self.background_capture, (0, 0))
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill(self.bg_color)

        # Draw Popup Window
        popup_width = int(self.width * 0.6)
        popup_height = int(self.height * 0.7)
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, (15, 15, 20), popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.text_color, popup_rect, width=2, border_radius=10)

        # Title at top
        title_text = "TOR NETWORK"
        title_surf = self.title_font.render(title_text, True, self.text_color)
        title_x = popup_x + (popup_width - title_surf.get_width()) // 2
        title_y = popup_y + int(popup_height * 0.1)
        self.screen.blit(title_surf, (title_x, title_y))

        # Subtitle
        subtitle_text = "Connexion anonyme au Deep Web"
        subtitle_surf = self.small_font.render(subtitle_text, True, self.text_dim)
        subtitle_x = popup_x + (popup_width - subtitle_surf.get_width()) // 2
        subtitle_y = title_y + title_surf.get_height() + 10
        self.screen.blit(subtitle_surf, (subtitle_x, subtitle_y))

        # Draw stages list
        stage_y = popup_y + int(popup_height * 0.3)
        stage_x = popup_x + int(popup_width * 0.15)

        for i, (stage_text, duration, is_final) in enumerate(self.stages):
            # Determine color based on state
            if i < self.current_stage:
                # Completed
                color = self.text_success
                prefix = "[OK]"
            elif i == self.current_stage:
                # In progress (blinking effect)
                blink = (pygame.time.get_ticks() // 300) % 2
                color = self.text_color if blink else self.text_dim
                prefix = "[...]"
            else:
                # Not started
                color = self.text_dim
                prefix = "[ ]"

            # Draw stage text
            full_text = f"{prefix} {stage_text}"
            stage_surf = self.body_font.render(full_text, True, color)
            self.screen.blit(stage_surf, (stage_x, stage_y))

            stage_y += stage_surf.get_height() + 20

        # Overall progress bar
        progress_bar_y = popup_y + int(popup_height * 0.75)
        progress_bar_width = int(popup_width * 0.8)
        progress_bar_height = 30
        progress_bar_x = popup_x + (popup_width - progress_bar_width) // 2

        # Background
        bar_bg_rect = pygame.Rect(progress_bar_x, progress_bar_y,
                                   progress_bar_width, progress_bar_height)
        pygame.draw.rect(self.screen, self.progress_bar_bg, bar_bg_rect, border_radius=5)

        # Fill (based on completed stages)
        progress = len(self.completed_stages) / len(self.stages)
        fill_width = int(progress_bar_width * progress)

        if fill_width > 0:
            fill_rect = pygame.Rect(progress_bar_x, progress_bar_y,
                                    fill_width, progress_bar_height)
            pygame.draw.rect(self.screen, self.progress_bar_fill, fill_rect, border_radius=5)

        # Border
        pygame.draw.rect(self.screen, self.text_color, bar_bg_rect,
                        width=2, border_radius=5)

        # Percentage text
        percent_text = f"{int(progress * 100)}%"
        percent_surf = self.body_font.render(percent_text, True, self.text_color)
        percent_x = progress_bar_x + (progress_bar_width - percent_surf.get_width()) // 2
        percent_y = progress_bar_y + (progress_bar_height - percent_surf.get_height()) // 2
        self.screen.blit(percent_surf, (percent_x, percent_y))

        # Show relay IP addresses (matrix effect)
        if len(self.completed_stages) > 0:
            relay_y = progress_bar_y + progress_bar_height + 20
            relay_text = f"Relais actif: {self.relay_ips[len(self.completed_stages) - 1]}"
            relay_surf = self.small_font.render(relay_text, True, self.text_dim)
            relay_x = popup_x + (popup_width - relay_surf.get_width()) // 2
            self.screen.blit(relay_surf, (relay_x, relay_y))

        # Animated dots at bottom
        dots_count = (pygame.time.get_ticks() // 500) % 4
        dots_text = "." * dots_count
        dots_surf = self.body_font.render(dots_text, True, self.text_dim)
        dots_x = popup_x + (popup_width - dots_surf.get_width()) // 2
        dots_y = popup_y + popup_height - 40
        self.screen.blit(dots_surf, (dots_x, dots_y))


def show_deepweb_loading(screen: pygame.Surface) -> str:
    """
    Convenience function to show deep web loading screen

    Args:
        screen: Pygame screen surface

    Returns:
        "complete" when loading finished
        "exit" if user closed window
    """
    loader = DeepWebLoader(screen)
    return loader.show_loading()
