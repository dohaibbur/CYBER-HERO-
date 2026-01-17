"""
Mission Objectives HUD - Cyber Hero
Displays mission objectives overlay during gameplay
"""

import pygame
from typing import Dict, Optional


class MissionObjectivesHUD:
    """
    Heads-up display for mission objectives
    Shows objectives list and progress
    """

    def __init__(self, screen, mission):
        """
        Initialize mission HUD

        Args:
            screen: Pygame screen surface
            mission: Mission object (e.g., Mission1NetworkRecon)
        """
        self.screen = screen
        self.mission = mission
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors
        self.bg_color = (15, 20, 30, 200)  # Semi-transparent
        self.text_color = (200, 210, 220)
        self.complete_color = (0, 255, 100)
        self.incomplete_color = (255, 180, 0)
        self.border_color = (0, 255, 65)

        # Fonts
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(20 * self.scale))
            self.objective_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(16 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(20 * self.scale))
            self.objective_font = pygame.font.Font(None, int(16 * self.scale))

        # HUD position (top-right corner)
        self.hud_width = int(400 * self.scale_x)
        self.hud_x = self.screen_width - self.hud_width - int(20 * self.scale_x)
        self.hud_y = int(80 * self.scale_y)

        # Collapsed/expanded state
        self.is_expanded = True

    def draw(self):
        """Draw the mission objectives HUD"""
        # Simply return without drawing anything
        return
        if not self.is_expanded:
            # Draw minimized version
            self.draw_minimized()
            return

        # Get objectives
        objectives = self.mission.objectives
        completion = self.mission.get_completion_percentage()

        # Calculate HUD height based on number of objectives
        objective_height = int(30 * self.scale_y)
        header_height = int(60 * self.scale_y)
        padding = int(10 * self.scale_y)
        total_height = header_height + (len(objectives) * objective_height) + padding * 2

        # Create semi-transparent surface
        hud_surface = pygame.Surface((self.hud_width, total_height), pygame.SRCALPHA)
        hud_surface.fill(self.bg_color)

        # Draw border
        pygame.draw.rect(hud_surface, self.border_color, (0, 0, self.hud_width, total_height), 2)

        # Draw header
        title_text = self.title_font.render("OBJECTIFS MISSION", True, self.border_color)
        title_rect = title_text.get_rect(centerx=self.hud_width // 2, top=int(10 * self.scale_y))
        hud_surface.blit(title_text, title_rect)

        # Draw completion percentage
        completion_text = self.objective_font.render(f"Progression: {int(completion)}%", True, self.text_color)
        completion_rect = completion_text.get_rect(centerx=self.hud_width // 2, top=int(35 * self.scale_y))
        hud_surface.blit(completion_text, completion_rect)

        # Draw progress bar
        bar_width = int(350 * self.scale_x)
        bar_height = int(8 * self.scale_y)
        bar_x = (self.hud_width - bar_width) // 2
        bar_y = int(55 * self.scale_y)

        # Background bar
        pygame.draw.rect(hud_surface, (50, 60, 70), (bar_x, bar_y, bar_width, bar_height))

        # Progress bar
        progress_width = int(bar_width * (completion / 100))
        progress_color = self.complete_color if completion >= 100 else self.incomplete_color
        pygame.draw.rect(hud_surface, progress_color, (bar_x, bar_y, progress_width, bar_height))

        # Draw objectives
        y_offset = header_height + padding

        for obj_id, obj_data in objectives.items():
            # Checkbox
            checkbox_x = int(15 * self.scale_x)
            checkbox_size = int(16 * self.scale)
            checkbox_rect = pygame.Rect(checkbox_x, y_offset + int(5 * self.scale_y), checkbox_size, checkbox_size)

            # Checkbox background
            pygame.draw.rect(hud_surface, (30, 40, 50), checkbox_rect)
            pygame.draw.rect(hud_surface, self.border_color, checkbox_rect, 1)

            # Checkmark if completed
            if obj_data['completed']:
                check_color = self.complete_color
                # Draw checkmark
                pygame.draw.line(hud_surface, check_color,
                               (checkbox_rect.left + 3, checkbox_rect.centery),
                               (checkbox_rect.centerx, checkbox_rect.bottom - 4), 2)
                pygame.draw.line(hud_surface, check_color,
                               (checkbox_rect.centerx, checkbox_rect.bottom - 4),
                               (checkbox_rect.right - 3, checkbox_rect.top + 3), 2)

            # Objective text
            text_x = checkbox_x + checkbox_size + int(10 * self.scale_x)
            text_color = self.complete_color if obj_data['completed'] else self.text_color

            # Truncate long titles
            title = obj_data['title']
            if len(title) > 35:
                title = title[:32] + "..."

            obj_text = self.objective_font.render(title, True, text_color)
            hud_surface.blit(obj_text, (text_x, y_offset + int(8 * self.scale_y)))

            y_offset += objective_height

        # Blit HUD to main screen
        self.screen.blit(hud_surface, (self.hud_x, self.hud_y))

        # Draw toggle hint
        hint_text = self.objective_font.render("[TAB] Toggle Objectifs", True, (100, 110, 120))
        self.screen.blit(hint_text, (self.hud_x, self.hud_y + total_height + int(5 * self.scale_y)))

    def draw_minimized(self):
        """Draw minimized HUD (just completion percentage)"""
        # Small box with completion %
        mini_width = int(120 * self.scale_x)
        mini_height = int(40 * self.scale_y)

        mini_surface = pygame.Surface((mini_width, mini_height), pygame.SRCALPHA)
        mini_surface.fill(self.bg_color)
        pygame.draw.rect(mini_surface, self.border_color, (0, 0, mini_width, mini_height), 2)

        completion = self.mission.get_completion_percentage()
        completion_text = self.objective_font.render(f"{int(completion)}%", True, self.text_color)
        completion_rect = completion_text.get_rect(center=(mini_width // 2, mini_height // 2))
        mini_surface.blit(completion_text, completion_rect)

        self.screen.blit(mini_surface, (self.hud_x, self.hud_y))

        # Draw toggle hint
        hint_text = self.objective_font.render("[TAB] Objectifs", True, (100, 110, 120))
        self.screen.blit(hint_text, (self.hud_x, self.hud_y + mini_height + int(5 * self.scale_y)))

    def toggle_expanded(self):
        """Toggle between expanded and minimized"""
        self.is_expanded = not self.is_expanded

    def update(self, terminal_state: Dict):
        """
        Update mission progress

        Args:
            terminal_state: Current terminal state
        """
        self.mission.update_progress(terminal_state)
