"""
Welcome Sequence - CyberHero
Displays introductory typing animation before desktop
"""

import pygame


class WelcomeSequence:
    """
    Displays welcome messages with typing animation effect
    """

    def __init__(self, screen):
        """
        Initialize welcome sequence

        Args:
            screen: Pygame screen surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Colors
        self.black = (0, 0, 0)
        self.hacker_green = (0, 255, 65)  # #00ff41

        # Scaling
        self.scale = min(self.screen_width / 1920, self.screen_height / 1080)

        # Welcome messages
        self.messages = [
            "He, futur cyber-heros ?",
            "On est ravis de t'avoir avec nous !",
            "Bienvenue à bord sur votre bureau,",
            "l'endroit d'ou tu tireras toutes les ficelles."
        ]

        # Animation settings
        self.typing_speed = 30  # Milliseconds per character
        self.pause_between_lines = 2000  # 2 seconds between lines
        self.final_hold = 2000  # 2 seconds final hold

        # Load font
        self.load_font()

    def load_font(self):
        """Load appropriate font for messages - Standardized sizes (matching desktop)"""
        try:
            # Try Cyberpunk font first
            self.font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
        except:
            try:
                # Try Arial (supports French characters)
                self.font = pygame.font.SysFont('arial', int(32 * self.scale))
            except:
                # Fallback to default font
                self.font = pygame.font.Font(None, int(32 * self.scale))
                # Use ASCII-safe messages for default font
                self.messages = [
                    "Hey, futur cyber-heros ?",
                    "On est ravis de t'avoir avec nous !",
                    "Mais avant tout, laisse-nous te montrer ton environnement hacker,",
                    "l'endroit d'ou tu tireras toutes les ficelles."
                ]

    def type_message(self, message, displayed_lines, line_height, start_y):
        """
        Type out a single message character by character

        Args:
            message: Text to type
            displayed_lines: List of already displayed lines
            line_height: Height of each line
            start_y: Starting Y position

        Returns:
            True if completed, False if interrupted
        """
        current_text = ""

        for char in message:
            # Check for quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Skip to end of current line
                        current_text = message
                        break

            current_text += char

            # Clear screen
            self.screen.fill(self.black)

            # Draw all previously completed lines
            for i, completed_line in enumerate(displayed_lines):
                text_surface = self.font.render(completed_line, True, self.hacker_green)
                text_rect = text_surface.get_rect(centerx=self.screen_width // 2,
                                                  top=start_y + i * line_height)
                self.screen.blit(text_surface, text_rect)

            # Draw current typing line with cursor
            typing_line = current_text + "█"  # Block cursor
            text_surface = self.font.render(typing_line, True, self.hacker_green)
            text_rect = text_surface.get_rect(centerx=self.screen_width // 2,
                                              top=start_y + len(displayed_lines) * line_height)
            self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

            # Wait before next character
            if current_text != message:  # Don't wait if we skipped
                pygame.time.wait(self.typing_speed)

        return True

    def run(self):
        """
        Run the welcome sequence

        Returns:
            True if completed successfully, False if interrupted
        """
        displayed_lines = []
        line_height = int(50 * self.scale)

        # Type each message
        for message_index, message in enumerate(self.messages):
            # Calculate vertical centering
            total_lines = len(displayed_lines) + 1
            total_height = total_lines * line_height
            start_y = (self.screen_height - total_height) // 2

            # Type the message
            completed = self.type_message(message, displayed_lines, line_height, start_y)

            if not completed:
                return False

            # Add completed message to list
            displayed_lines.append(message)

            # Redraw without cursor
            self.screen.fill(self.black)
            total_height = len(displayed_lines) * line_height
            start_y = (self.screen_height - total_height) // 2

            for i, line in enumerate(displayed_lines):
                text_surface = self.font.render(line, True, self.hacker_green)
                text_rect = text_surface.get_rect(centerx=self.screen_width // 2,
                                                  top=start_y + i * line_height)
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

            # Pause between lines (except after last line)
            if message_index < len(self.messages) - 1:
                # Check for skip during pause
                start_time = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start_time < self.pause_between_lines:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                return False
                            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                                # Skip pause
                                break
                    pygame.time.wait(10)

        # Final hold
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < self.final_hold:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Skip final hold
                        break
            pygame.time.wait(10)

        # Fade out
        self.fade_out()

        return True

    def fade_out(self):
        """Fade out to black"""
        for alpha in range(255, 0, -15):
            s = pygame.Surface((self.screen_width, self.screen_height))
            s.set_alpha(alpha)
            s.fill(self.black)
            self.screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)
