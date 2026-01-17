"""
Mission Complete Screen - Cyber Hero
Shows mission completion with rewards
"""

import pygame
from typing import Dict


class MissionCompleteScreen:
    """
    Screen showing mission completion and rewards
    """

    def __init__(self, screen, mission_name: str, rewards: Dict):
        """
        Initialize mission complete screen

        Args:
            screen: Pygame screen surface
            mission_name: Name of completed mission
            rewards: Reward dictionary with xp, badges, etc.
        """
        self.screen = screen
        self.mission_name = mission_name
        self.rewards = rewards
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors
        self.bg_color = (10, 15, 20)
        self.success_color = (0, 255, 100)
        self.text_color = (200, 210, 220)
        self.border_color = (0, 255, 65)

        # Fonts - Standardized sizes (matching desktop)
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * self.scale))
            self.subtitle_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
            self.text_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * self.scale))
            self.subtitle_font = pygame.font.Font(None, int(32 * self.scale))
            self.text_font = pygame.font.Font(None, int(26 * self.scale))

    def draw(self):
        """Draw the mission complete screen"""
        self.screen.fill(self.bg_color)

        # Calculate center
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Draw success box
        box_width = int(800 * self.scale_x)
        box_height = int(500 * self.scale_y)
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2

        # Box background
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((20, 30, 40, 240))
        pygame.draw.rect(box_surface, self.border_color, (0, 0, box_width, box_height), 3)

        # Title
        title_text = self.title_font.render("MISSION REUSSIE", True, self.success_color)
        title_rect = title_text.get_rect(centerx=box_width // 2, top=int(40 * self.scale_y))
        box_surface.blit(title_text, title_rect)

        # Mission name
        mission_text = self.subtitle_font.render(self.mission_name, True, self.text_color)
        mission_rect = mission_text.get_rect(centerx=box_width // 2, top=int(120 * self.scale_y))
        box_surface.blit(mission_text, mission_rect)

        # Rewards section
        y_offset = int(200 * self.scale_y)

        # XP reward
        xp = self.rewards.get('xp', 0)
        xp_text = self.text_font.render(f"+ {xp} XP", True, self.success_color)
        xp_rect = xp_text.get_rect(centerx=box_width // 2, top=y_offset)
        box_surface.blit(xp_text, xp_rect)
        y_offset += int(45 * self.scale_y)

        # Credits reward
        credits = self.rewards.get('credits', 0)
        if credits > 0:
            credits_text = self.text_font.render(f"+ {credits} Credits", True, (255, 215, 0))
            credits_rect = credits_text.get_rect(centerx=box_width // 2, top=y_offset)
            box_surface.blit(credits_text, credits_rect)
            y_offset += int(45 * self.scale_y)

        # Badges
        badges = self.rewards.get('badges', [])
        if badges:
            badge_text = self.text_font.render(f"Badge: {badges[0]}", True, (0, 200, 255))
            badge_rect = badge_text.get_rect(centerx=box_width // 2, top=y_offset)
            box_surface.blit(badge_text, badge_rect)
            y_offset += int(45 * self.scale_y)

        # Unlocked missions
        if "Mission 3" in self.mission_name:
            # Special message for Mission 3 completion
            end_text = self.text_font.render("Vous avez termine vos 3 missions.", True, self.text_color)
            end_rect = end_text.get_rect(centerx=box_width // 2, top=y_offset)
            box_surface.blit(end_text, end_rect)
            
            y_offset += int(35 * self.scale_y)
            wait_text = self.text_font.render("Attendez un futur email du professeur.", True, self.text_color)
            wait_rect = wait_text.get_rect(centerx=box_width // 2, top=y_offset)
            box_surface.blit(wait_text, wait_rect)
        else:
            unlocked = self.rewards.get('unlocked_missions', [])
            if unlocked:
                unlock_text = self.text_font.render(f"Nouvelle mission disponible!", True, self.text_color)
                unlock_rect = unlock_text.get_rect(centerx=box_width // 2, top=y_offset)
                box_surface.blit(unlock_text, unlock_rect)

        # Continue instruction
        continue_text = self.text_font.render("Appuyez sur ENTREE pour continuer", True, (100, 110, 120))
        continue_rect = continue_text.get_rect(centerx=box_width // 2, bottom=box_height - int(30 * self.scale_y))
        box_surface.blit(continue_text, continue_rect)

        # Blit box to screen
        self.screen.blit(box_surface, (box_x, box_y))

    def run(self) -> str:
        """
        Run mission complete screen

        Returns:
            "continue" when user presses enter
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        return "continue"

            self.draw()
            pygame.display.flip()

        return "continue"
