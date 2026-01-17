"""
Forum Authentication - Forum-style login and account creation
"""

import pygame
from typing import Tuple, Optional


class ForumAuth:
    """
    Forum-style authentication page for login and account creation
    """

    def __init__(self, screen, mode: str = "login"):
        """
        Initialize forum auth page

        Args:
            screen: Pygame screen surface
            mode: "login" or "register"
        """
        self.screen = screen
        self.mode = mode  # "login" or "register"
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors - Deepweb dark theme
        self.bg_color = (12, 12, 12)
        self.browser_bar = (25, 25, 25)
        self.content_bg = (18, 18, 18)
        self.post_bg = (22, 22, 22)
        self.border_color = (40, 40, 40)
        self.primary_color = (0, 220, 50)
        self.accent_color = (0, 180, 240)
        self.text_color = (180, 180, 180)
        self.dim_text = (120, 120, 120)
        self.error_color = (220, 50, 50)
        self.button_bg = (30, 30, 30)
        self.button_hover = (45, 45, 45)
        self.input_bg = (25, 25, 25)
        self.input_active = (35, 35, 35)

        # Fonts
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * self.scale))
            self.heading_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * self.scale))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(24 * self.scale))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(18 * self.scale))
            self.url_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(20 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(42 * self.scale))
            self.heading_font = pygame.font.Font(None, int(32 * self.scale))
            self.body_font = pygame.font.Font(None, int(24 * self.scale))
            self.small_font = pygame.font.Font(None, int(18 * self.scale))
            self.url_font = pygame.font.Font(None, int(20 * self.scale))

        # Browser chrome measurements
        self.browser_bar_height = int(50 * self.scale_y)
        self.url_bar_height = int(35 * self.scale_y)
        self.top_bar_height = int(40 * self.scale_y)

        # Form state
        self.username = ""
        self.password = ""
        self.email = ""
        self.active_field = "username"
        self.error_message = ""
        self.show_password = False

        # Button rects
        self.submit_button_rect = None
        self.switch_mode_rect = None
        self.toggle_password_rect = None

        # Input field rects
        self.username_field_rect = None
        self.password_field_rect = None
        self.email_field_rect = None

    def draw_browser_chrome(self):
        """Draw browser window chrome"""
        # Browser top bar
        pygame.draw.rect(self.screen, self.browser_bar,
                        (0, 0, self.screen_width, self.browser_bar_height))

        # Window controls
        button_size = int(10 * self.scale)
        button_y = self.browser_bar_height // 2 - button_size // 2
        button_spacing = int(18 * self.scale_x)

        pygame.draw.circle(self.screen, (200, 50, 50),
                          (int(15 * self.scale_x), button_y + button_size // 2), button_size // 2)
        pygame.draw.circle(self.screen, (200, 180, 50),
                          (int(15 * self.scale_x) + button_spacing, button_y + button_size // 2), button_size // 2)
        pygame.draw.circle(self.screen, (50, 200, 50),
                          (int(15 * self.scale_x) + button_spacing * 2, button_y + button_size // 2), button_size // 2)

        # URL bar
        url_bar_y = self.browser_bar_height
        pygame.draw.rect(self.screen, self.browser_bar,
                        (0, url_bar_y, self.screen_width, self.url_bar_height))

        url_box_rect = pygame.Rect(
            int(80 * self.scale_x),
            url_bar_y + int(6 * self.scale_y),
            self.screen_width - int(160 * self.scale_x),
            self.url_bar_height - int(12 * self.scale_y)
        )
        pygame.draw.rect(self.screen, self.content_bg, url_box_rect, border_radius=int(4 * self.scale))

        # URL changes based on mode
        url = "http://cxh3r0f0rum7k2j9d.onion/register" if self.mode == "register" else "http://cxh3r0f0rum7k2j9d.onion/login"
        url_text = self.url_font.render(url, True, self.text_color)
        self.screen.blit(url_text, (url_box_rect.x + int(10 * self.scale_x),
                                    url_box_rect.centery - url_text.get_height() // 2))

        # Tor lock icon
        lock_x = int(60 * self.scale_x)
        lock_text = self.small_font.render("[TOR]", True, self.primary_color)
        self.screen.blit(lock_text, (lock_x - lock_text.get_width() // 2,
                                     url_bar_y + self.url_bar_height // 2 - lock_text.get_height() // 2))

    def draw_top_navigation(self):
        """Draw forum navigation bar"""
        nav_y = self.browser_bar_height + self.url_bar_height
        pygame.draw.rect(self.screen, self.post_bg,
                        (0, nav_y, self.screen_width, self.top_bar_height))
        pygame.draw.line(self.screen, self.border_color,
                        (0, nav_y + self.top_bar_height),
                        (self.screen_width, nav_y + self.top_bar_height), 1)

        # Forum title
        title_x = int(30 * self.scale_x)
        title = self.heading_font.render("CYBER HERO FORUM", True, self.primary_color)
        self.screen.blit(title, (title_x, nav_y + self.top_bar_height // 2 - title.get_height() // 2))

        # Breadcrumb
        nav_x = int(400 * self.scale_x)
        breadcrumb = "Accueil > Inscription" if self.mode == "register" else "Accueil > Connexion"
        breadcrumb_text = self.small_font.render(breadcrumb, True, self.dim_text)
        self.screen.blit(breadcrumb_text, (nav_x, nav_y + self.top_bar_height // 2 - breadcrumb_text.get_height() // 2))

    def draw_input_field(self, x: int, y: int, width: int, height: int,
                        label: str, value: str, is_active: bool,
                        is_password: bool = False, placeholder: str = ""):
        """Draw an input field"""
        # Label
        label_text = self.body_font.render(label, True, self.text_color)
        self.screen.blit(label_text, (x, y - int(35 * self.scale_y)))

        # Field background
        bg_color = self.input_active if is_active else self.input_bg
        field_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, field_rect, border_radius=int(4 * self.scale))

        # Border
        border_color = self.primary_color if is_active else self.border_color
        pygame.draw.rect(self.screen, border_color, field_rect, 2, border_radius=int(4 * self.scale))

        # Value text
        if value:
            display_value = "●" * len(value) if (is_password and not self.show_password) else value
            text_color = self.text_color
        else:
            display_value = placeholder
            text_color = self.dim_text

        value_surface = self.body_font.render(display_value, True, text_color)
        self.screen.blit(value_surface, (x + int(15 * self.scale_x),
                                        y + height // 2 - value_surface.get_height() // 2))

        # Cursor if active
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = x + int(15 * self.scale_x) + value_surface.get_width() + int(2 * self.scale_x)
            pygame.draw.line(self.screen, self.primary_color,
                           (cursor_x, y + int(12 * self.scale_y)),
                           (cursor_x, y + height - int(12 * self.scale_y)), 2)

        return field_rect

    def draw_button(self, x: int, y: int, width: int, height: int, text: str, is_primary: bool = True):
        """Draw a button"""
        button_rect = pygame.Rect(x, y, width, height)

        # Hover effect
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)

        if is_primary:
            bg_color = self.primary_color if is_hovered else (0, 180, 40)
            text_color = (0, 0, 0)
        else:
            bg_color = self.button_hover if is_hovered else self.button_bg
            text_color = self.text_color

        pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=int(4 * self.scale))

        if not is_primary:
            pygame.draw.rect(self.screen, self.border_color, button_rect, 1, border_radius=int(4 * self.scale))

        # Button text
        button_text = self.body_font.render(text, True, text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)

        return button_rect

    def draw_auth_form(self):
        """Draw authentication form"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(40 * self.scale_y)
        content_x = (self.screen_width - int(600 * self.scale_x)) // 2
        form_width = int(600 * self.scale_x)

        # Form container
        form_height = int(550 * self.scale_y) if self.mode == "register" else int(450 * self.scale_y)
        form_rect = pygame.Rect(content_x, content_y, form_width, form_height)
        pygame.draw.rect(self.screen, self.post_bg, form_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, form_rect, 1, border_radius=int(8 * self.scale))

        # Title
        title_y = content_y + int(30 * self.scale_y)
        if self.mode == "register":
            title = self.title_font.render("Créer un Compte", True, self.primary_color)
            subtitle = self.small_font.render("Rejoins la communauté underground", True, self.dim_text)
        else:
            title = self.title_font.render("Connexion", True, self.primary_color)
            subtitle = self.small_font.render("Accède à ton compte", True, self.dim_text)

        title_rect = title.get_rect(centerx=self.screen_width // 2, top=title_y)
        self.screen.blit(title, title_rect)

        subtitle_rect = subtitle.get_rect(centerx=self.screen_width // 2, top=title_rect.bottom + int(5 * self.scale_y))
        self.screen.blit(subtitle, subtitle_rect)

        # Input fields
        field_width = int(500 * self.scale_x)
        field_height = int(50 * self.scale_y)
        field_x = content_x + int(50 * self.scale_x)
        field_y = subtitle_rect.bottom + int(40 * self.scale_y)

        # Username field
        self.username_field_rect = self.draw_input_field(field_x, field_y, field_width, field_height,
                             "Nom d'utilisateur:", self.username,
                             self.active_field == "username",
                             placeholder="ex: Gh0stH4ck3r")
        field_y += int(100 * self.scale_y)

        # Email field (register only)
        if self.mode == "register":
            self.email_field_rect = self.draw_input_field(field_x, field_y, field_width, field_height,
                                 "Email (optionnel):", self.email,
                                 self.active_field == "email",
                                 placeholder="ex: ghost@protonmail.com")
            field_y += int(100 * self.scale_y)
        else:
            self.email_field_rect = None

        # Password field
        self.password_field_rect = self.draw_input_field(field_x, field_y, field_width, field_height,
                                                     "Mot de passe:", self.password,
                                                     self.active_field == "password",
                                                     is_password=True,
                                                     placeholder="●●●●●●●●")

        # Show/Hide password toggle
        toggle_x = field_x + field_width + int(10 * self.scale_x)
        toggle_text = "[o]" if self.show_password else "[*]"
        toggle_surface = self.body_font.render(toggle_text, True, self.dim_text)
        self.toggle_password_rect = pygame.Rect(toggle_x, field_y, int(40 * self.scale_x), field_height)
        self.screen.blit(toggle_surface, (toggle_x, field_y + field_height // 2 - toggle_surface.get_height() // 2))

        field_y += int(80 * self.scale_y)

        # Error message
        if self.error_message:
            error_text = self.small_font.render(self.error_message, True, self.error_color)
            error_rect = error_text.get_rect(centerx=self.screen_width // 2, top=field_y)
            self.screen.blit(error_text, error_rect)
            field_y += int(30 * self.scale_y)

        # Submit button
        button_width = int(500 * self.scale_x)
        button_height = int(50 * self.scale_y)
        button_x = field_x
        button_text = "S'INSCRIRE" if self.mode == "register" else "SE CONNECTER"
        self.submit_button_rect = self.draw_button(button_x, field_y, button_width, button_height,
                                                   button_text, is_primary=True)

        field_y += int(70 * self.scale_y)

        # Switch mode link
        if self.mode == "register":
            switch_text = "Deja un compte? Connexion"
        else:
            switch_text = "Pas encore de compte? S'inscrire"

        switch_surface = self.small_font.render(switch_text, True, self.accent_color)
        switch_rect = switch_surface.get_rect(centerx=self.screen_width // 2, top=field_y)
        self.screen.blit(switch_surface, switch_rect)
        self.switch_mode_rect = switch_rect

        # Instructions at bottom
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ECHAP: Retour au forum | TAB: Champ suivant | ENTREE: Valider", True, self.dim_text)
        self.screen.blit(instructions, (int(30 * self.scale_x), instructions_y))

    def handle_text_input(self, char: str):
        """Handle character input"""
        if self.active_field == "username":
            if len(self.username) < 20:
                self.username += char
        elif self.active_field == "password":
            if len(self.password) < 30:
                self.password += char
        elif self.active_field == "email":
            if len(self.email) < 50:
                self.email += char

    def handle_backspace(self):
        """Handle backspace"""
        if self.active_field == "username" and self.username:
            self.username = self.username[:-1]
        elif self.active_field == "password" and self.password:
            self.password = self.password[:-1]
        elif self.active_field == "email" and self.email:
            self.email = self.email[:-1]

    def handle_tab(self):
        """Switch to next field"""
        if self.mode == "register":
            fields = ["username", "email", "password"]
        else:
            fields = ["username", "password"]

        current_idx = fields.index(self.active_field)
        self.active_field = fields[(current_idx + 1) % len(fields)]

    def validate_form(self) -> bool:
        """Validate form data"""
        if len(self.username) < 3:
            self.error_message = "Le nom d'utilisateur doit avoir au moins 3 caracteres"
            return False

        if len(self.password) < 4:
            self.error_message = "Le mot de passe doit avoir au moins 4 caracteres"
            return False

        if self.mode == "register" and self.email:
            if "@" not in self.email:
                self.error_message = "Format d'email invalide"
                return False

        self.error_message = ""
        return True

    def run(self) -> Tuple[str, Optional[dict]]:
        """
        Run forum auth page

        Returns:
            Tuple of (result, profile_data)
            result: "exit", "back", "success"
            profile_data: Created profile data if success
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back", None

                    elif event.key == pygame.K_TAB:
                        self.handle_tab()

                    elif event.key == pygame.K_RETURN:
                        if self.validate_form():
                            # Create profile data
                            profile_data = {
                                'nickname': self.username,
                                'email': self.email if self.mode == "register" else "",
                                'password': self.password,  # In real app, hash this!
                                'progress': {
                                    'xp': 0,
                                    'level': 'Debutant',
                                    'reputation': 1,
                                    'credits': 2500,
                                    'missions_completed': [],
                                    'unlocked_missions': ['mission1'],
                                    'badges': [],
                                    'alerts': 2
                                }
                            }
                            return "success", profile_data

                    elif event.key == pygame.K_BACKSPACE:
                        self.handle_backspace()

                    elif event.unicode.isprintable():
                        self.handle_text_input(event.unicode)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check input fields
                        if self.username_field_rect and self.username_field_rect.collidepoint(event.pos):
                            self.active_field = "username"
                        elif self.password_field_rect and self.password_field_rect.collidepoint(event.pos):
                            self.active_field = "password"
                        elif self.email_field_rect and self.email_field_rect.collidepoint(event.pos):
                            self.active_field = "email"

                        # Submit button
                        if self.submit_button_rect and self.submit_button_rect.collidepoint(event.pos):
                            if self.validate_form():
                                profile_data = {
                                    'nickname': self.username,
                                    'email': self.email if self.mode == "register" else "",
                                    'password': self.password,
                                    'progress': {
                                        'xp': 0,
                                        'level': 'Debutant',
                                        'reputation': 1,
                                        'credits': 2500,
                                        'missions_completed': [],
                                        'unlocked_missions': ['mission1'],
                                        'badges': [],
                                        'alerts': 2
                                    }
                                }
                                return "success", profile_data

                        # Switch mode link
                        if self.switch_mode_rect and self.switch_mode_rect.collidepoint(event.pos):
                            self.mode = "register" if self.mode == "login" else "login"
                            self.error_message = ""

                        # Toggle password visibility
                        if self.toggle_password_rect and self.toggle_password_rect.collidepoint(event.pos):
                            self.show_password = not self.show_password

            # Drawing
            self.screen.fill(self.bg_color)
            self.draw_browser_chrome()
            self.draw_top_navigation()
            self.draw_auth_form()

            pygame.display.flip()

        return "exit", None
