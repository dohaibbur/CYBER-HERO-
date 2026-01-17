"""
Forum Browser - CyberHero
Deepweb-style hacker forum interface with threads and posts
"""

import pygame
import os
import sys
from typing import Tuple, List, Dict, Optional
from datetime import datetime, timedelta
import random
from src.ui.forum_theme import ForumTheme


class ForumThread:
    """Represents a forum thread"""
    def __init__(self, id: int, category: str, title: str, author: str,
                 replies: int, views: int, last_post: str, pinned: bool = False):
        self.id = id
        self.category = category
        self.title = title
        self.author = author
        self.replies = replies
        self.views = views
        self.last_post = last_post
        self.pinned = pinned


class ForumBrowser:
    """
    Deepweb-style forum browser interface
    Mimics underground hacker forums with categories, threads, and posts
    """

    def __init__(self, screen, profile_data=None, is_logged_in=False):
        """
        Initialize forum browser

        Args:
            screen: Pygame screen surface
            profile_data: Player profile data (optional)
            is_logged_in: Whether user is already logged in (session persistence)
        """
        self.screen = screen
        self.profile_data = profile_data or {}
        self._session_logged_in = is_logged_in  # Store session state
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Apply unified forum theme colors
        ForumTheme.apply_to(self)

        # Fonts - using pygame directly for consistent sizes
        try:
            self.title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(38 * self.scale))
            self.heading_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(30 * self.scale))
            self.body_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(24 * self.scale))
            self.small_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(20 * self.scale))
            self.url_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(18 * self.scale))
        except:
            self.title_font = pygame.font.Font(None, int(38 * self.scale))
            self.heading_font = pygame.font.Font(None, int(30 * self.scale))
            self.body_font = pygame.font.Font(None, int(24 * self.scale))
            self.small_font = pygame.font.Font(None, int(20 * self.scale))
            self.url_font = pygame.font.Font(None, int(18 * self.scale))

        # Browser chrome measurements
        self.browser_bar_height = int(50 * self.scale_y)
        self.url_bar_height = int(35 * self.scale_y)
        self.top_bar_height = int(40 * self.scale_y)

        # Forum state
        # If already logged in from session, start on categories page
        if self._session_logged_in and self.profile_data.get('nickname', 'Nouveau Joueur') != 'Nouveau Joueur':
            self.current_page = "categories"
            self.logged_in = True
            self.username = self.profile_data.get('nickname')
        else:
            self.current_page = "welcome"
            self.logged_in = False
            self.username = None

        self.selected_category = None
        self.selected_thread = None
        self.selected_email_index = None
        self.scroll_offset = 0
        self.max_scroll = 0
        self.email_scroll = 0
        self.email_max_scroll = 0
        self.email_scroll_speed = int(25 * self.scale_y)

        # Profile editing state
        self.edit_mode = False
        self.temp_bio = ""
        self.selected_avatar = None
        self.active_field = None
        self.avatar_rects = []
        self.avatars = []
        
        # Avatar popup state
        self.avatar_popup_open = False
        self.change_avatar_button_rect = None
        
        # Dynamic avatar loading
        self.avatar_options = set()
        
        # Search paths for avatars (bundled and external)
        search_paths = [os.path.join("assets", "avatars")]
        if getattr(sys, 'frozen', False):
            data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
            search_paths.append(os.path.join(data_dir, "assets", "avatars"))
            
        for avatars_dir in search_paths:
            if os.path.exists(avatars_dir):
                try:
                    for f in os.listdir(avatars_dir):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                            self.avatar_options.add(f)
                except Exception as e:
                    print(f"Error listing avatars in {avatars_dir}: {e}")
        
        self.avatar_options = sorted(list(self.avatar_options))
        
        if not self.avatar_options:
            self.avatar_options = ["avatar_1.png", "avatar_2.png", "avatar_3.png", "avatar_4.png", "avatar_5.png", "avatar_6.png"]
            
        self.avatar_option_rects = []
        self.avatar_cache = {}
        
        # Bio editing state
        self.editing_bio = False
        self.temp_bio = ""
        self.edit_bio_btn_rect = None
        self.save_bio_btn_rect = None
        self.cancel_bio_btn_rect = None
        self.bio_input_rect = None
        self.exit_button_rect = None

        # Forum data
        self.categories = self.load_categories()
        self.threads = self.load_threads()
        self.emails = []  # Will be loaded from inbox
        self.category_rects = {}
        self.thread_rects = {}
        self.email_rects = {}
        self.login_button_rect = None
        self.register_button_rect = None

    def load_categories(self) -> List[Dict]:
        """Load forum categories"""
        return [
            {
                'id': 'welcome',
                'name': 'Bienvenue & Regles',
                'description': 'Nouvelles recrues, commencez ici',
                'threads': 12,
                'posts': 156,
                'icon': '[i]'
            },
            {
                'id': 'network_security',
                'name': 'Securite Reseau',
                'description': 'Firewalls, IDS, architecture reseau',
                'threads': 89,
                'posts': 1247,
                'icon': '[S]'
            },
            {
                'id': 'pentesting',
                'name': 'Pentest & Red Team',
                'description': 'Tests d\'intrusion, exploits, CTF',
                'threads': 156,
                'posts': 3421,
                'icon': '[P]'
            },
            {
                'id': 'crypto',
                'name': 'Cryptographie',
                'description': 'Chiffrement, hash, steganographie',
                'threads': 67,
                'posts': 892,
                'icon': '[C]'
            },
            {
                'id': 'malware',
                'name': 'Analyse Malware',
                'description': 'Reverse engineering, sandboxing',
                'threads': 134,
                'posts': 2103,
                'icon': '[M]'
            },
            {
                'id': 'resources',
                'name': 'Ressources & Tutos',
                'description': 'Guides, outils, documentation',
                'threads': 203,
                'posts': 4567,
                'icon': '[R]'
            },
            {
                'id': 'marketplace',
                'name': 'Marketplace',
                'description': 'Echange de services et outils',
                'threads': 78,
                'posts': 945,
                'icon': '[$]'
            },
            {
                'id': 'offtopic',
                'name': 'Off-Topic',
                'description': 'Discussion generale',
                'threads': 234,
                'posts': 5123,
                'icon': '[O]'
            }
        ]

    def load_threads(self) -> Dict[str, List[ForumThread]]:
        """Load forum threads by category"""
        threads = {}

        # Network Security threads
        threads['network_security'] = [
            ForumThread(1, 'network_security', '[GUIDE] Configurer un Firewall pfSense',
                       'Mentor', 45, 1234, '2h ago', True),
            ForumThread(2, 'network_security', 'Detecter un scan de port avec Snort',
                       'NetDefender', 23, 567, '5h ago'),
            ForumThread(3, 'network_security', 'VPN vs Tor: Quelle difference?',
                       'Anonymous42', 78, 2341, '1 jour', True),
            ForumThread(4, 'network_security', 'Mon routeur est-il securise?',
                       'n00bHacker', 12, 234, '3h ago'),
            ForumThread(5, 'network_security', 'Honeypot pour detecter les intrusions',
                       'SysAdmin_Elite', 34, 890, '6h ago'),
        ]

        # Pentesting threads
        threads['pentesting'] = [
            ForumThread(10, 'pentesting', '[STICKY] Outils essentiels pour le pentesting',
                       'Mentor', 156, 5678, '1 sem', True),
            ForumThread(11, 'pentesting', 'Metasploit vs Manual Exploit',
                       'RedTeamLead', 89, 2345, '2h ago'),
            ForumThread(12, 'pentesting', 'J\'ai root ma premiere machine!',
                       'Beginner2024', 23, 456, '4h ago'),
            ForumThread(13, 'pentesting', 'SQLi: Comment proteger son site',
                       'WebSecGuru', 67, 1890, '1 jour'),
        ]

        # Welcome threads
        threads['welcome'] = [
            ForumThread(20, 'welcome', '[REGLES] A lire avant de poster',
                       'Admin', 234, 12456, '3 mois', True),
            ForumThread(21, 'welcome', 'Presentation des nouveaux membres',
                       'Community_Manager', 345, 8901, '1h ago', True),
            ForumThread(22, 'welcome', 'Comment devenir un hacker ethique?',
                       'Curious_Mind', 56, 1234, '5h ago'),
        ]

        # Other categories (empty for now)
        for cat in self.categories:
            if cat['id'] not in threads:
                threads[cat['id']] = []

        return threads

    def draw_browser_chrome(self):
        """Draw browser window chrome"""
        # Browser top bar
        pygame.draw.rect(self.screen, self.browser_bar,
                        (0, 0, self.screen_width, self.browser_bar_height))

        # Retour Button (Top Right)
        button_width = int(100 * self.scale_x)
        button_height = int(30 * self.scale_y)
        self.exit_button_rect = pygame.Rect(self.screen_width - button_width - int(15 * self.scale_x), (self.browser_bar_height - button_height) // 2, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.exit_button_rect.collidepoint(mouse_pos)
        back_color = (200, 60, 60) if is_hovered else (160, 40, 40)
        
        pygame.draw.rect(self.screen, back_color, self.exit_button_rect, border_radius=int(5 * self.scale))
        
        back_text = self.small_font.render("RETOUR", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # URL bar
        url_bar_y = self.browser_bar_height
        pygame.draw.rect(self.screen, self.browser_bar,
                        (0, url_bar_y, self.screen_width, self.url_bar_height))

        # Back button (left of URL bar)
        back_button_size = int(28 * self.scale)
        back_button_x = int(15 * self.scale_x)
        back_button_y = url_bar_y + (self.url_bar_height - back_button_size) // 2
        self.back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_size, back_button_size)

        # Check if back button is hovered
        mouse_pos = pygame.mouse.get_pos()
        is_back_hovered = self.back_button_rect.collidepoint(mouse_pos)

        # Draw back button
        back_color = self.button_hover if is_back_hovered else self.button_bg
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=int(4 * self.scale))

        # Back arrow
        arrow_text = self.body_font.render("<", True, self.text_color)
        arrow_rect = arrow_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(arrow_text, arrow_rect)

        # Forward button (right of back button, but disabled)
        forward_button_x = back_button_x + back_button_size + int(5 * self.scale_x)
        forward_button_rect = pygame.Rect(forward_button_x, back_button_y, back_button_size, back_button_size)
        pygame.draw.rect(self.screen, self.button_bg, forward_button_rect, border_radius=int(4 * self.scale))
        forward_text = self.body_font.render(">", True, self.text_dim)
        forward_rect = forward_text.get_rect(center=forward_button_rect.center)
        self.screen.blit(forward_text, forward_rect)

        url_box_rect = pygame.Rect(
            int(130 * self.scale_x),  # Moved right to make room for buttons
            url_bar_y + int(6 * self.scale_y),
            self.screen_width - int(210 * self.scale_x),
            self.url_bar_height - int(12 * self.scale_y)
        )
        pygame.draw.rect(self.screen, self.content_bg, url_box_rect, border_radius=int(4 * self.scale))

        # Onion URL
        url_text = self.url_font.render("http://cxh3r0f0rum7k2j9d.onion/board", True, self.text_color)
        self.screen.blit(url_text, (url_box_rect.x + int(10 * self.scale_x),
                                    url_box_rect.centery - url_text.get_height() // 2))

        # Tor lock icon (before URL bar)
        lock_x = int(110 * self.scale_x)
        lock_text = self.small_font.render("[TOR]", True, self.primary_color)
        self.screen.blit(lock_text, (lock_x - lock_text.get_width() // 2,
                                     url_bar_y + self.url_bar_height // 2 - lock_text.get_height() // 2))

    def draw_top_navigation(self):
        """Draw forum navigation bar with PROFILE, FORUM, MARKET tabs"""
        nav_y = self.browser_bar_height + self.url_bar_height
        pygame.draw.rect(self.screen, self.post_bg,
                        (0, nav_y, self.screen_width, self.top_bar_height))
        pygame.draw.line(self.screen, self.border_color,
                        (0, nav_y + self.top_bar_height),
                        (self.screen_width, nav_y + self.top_bar_height), 1)

        # Forum title (smaller to make room for tabs)
        title_x = int(30 * self.scale_x)
        title = self.body_font.render("CYBER HERO", True, self.primary_color)
        self.screen.blit(title, (title_x, nav_y + self.top_bar_height // 2 - title.get_height() // 2))

        # Navigation tabs: PROFILE, FORUM, MARKET
        tab_start_x = int(250 * self.scale_x)
        tab_width = int(120 * self.scale_x)
        tab_height = int(40 * self.scale_y)
        tab_spacing = int(15 * self.scale_x)
        tab_y = nav_y + (self.top_bar_height - tab_height) // 2

        mouse_pos = pygame.mouse.get_pos()

        # Define tabs
        tabs = [
            ("PROFILE", "profile"),
            ("FORUM", "forum"),
            ("MARKET", "market"),
            ("EMAIL", "email")
        ]

        # Store tab rectangles for click detection
        if not hasattr(self, 'nav_tab_rects'):
            self.nav_tab_rects = {}

        for i, (tab_name, tab_id) in enumerate(tabs):
            tab_x = tab_start_x + i * (tab_width + tab_spacing)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            self.nav_tab_rects[tab_id] = tab_rect

            # Check if tab is active (forum is active when on categories/threads page)
            is_active = (tab_id == "forum" and self.current_page in ["categories", "threads"])

            # Check hover
            is_hovered = tab_rect.collidepoint(mouse_pos)

            # Draw tab background
            if is_active:
                tab_bg_color = self.primary_color
                text_color = (0, 0, 0)
            elif is_hovered:
                tab_bg_color = (30, 30, 35)
                text_color = self.primary_color
            else:
                tab_bg_color = (20, 20, 25)
                text_color = self.dim_text

            pygame.draw.rect(self.screen, tab_bg_color, tab_rect, border_radius=int(5 * self.scale))

            # Draw tab border
            if is_active:
                pygame.draw.rect(self.screen, self.primary_color, tab_rect, width=2, border_radius=int(5 * self.scale))
            else:
                pygame.draw.rect(self.screen, self.border_color, tab_rect, width=1, border_radius=int(5 * self.scale))

            # Draw tab text
            tab_text_surf = self.small_font.render(tab_name, True, text_color)
            tab_text_rect = tab_text_surf.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text_surf, tab_text_rect)

        # User info (right side)
        user_x = self.screen_width - int(220 * self.scale_x)
        if self.logged_in and self.username:
            user_text = self.small_font.render(f"[{self.username}]", True, self.primary_color)
        else:
            user_text = self.small_font.render("[Invite]", True, self.dim_text)
        self.screen.blit(user_text, (user_x, nav_y + self.top_bar_height // 2 - user_text.get_height() // 2))

    def draw_back_button(self, x: int, y: int, text: str = "< Retour") -> pygame.Rect:
        """
        Draw a back button and return its rect for click detection

        Args:
            x: X position
            y: Y position
            text: Button text (default "< Retour")

        Returns:
            pygame.Rect: Button rectangle for click detection
        """
        button_width = int(120 * self.scale_x)
        button_height = int(35 * self.scale_y)
        button_rect = pygame.Rect(x, y, button_width, button_height)

        # Hover effect
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)

        bg_color = self.button_hover if is_hovered else self.button_bg
        pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=int(4 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, button_rect, width=1, border_radius=int(4 * self.scale))

        # Button text
        text_surface = self.body_font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def draw_welcome_page(self):
        """Draw welcome page with login/register options"""
        # Back button (top left)
        back_btn_x = int(40 * self.scale_x)
        back_btn_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(15 * self.scale_y)
        self.welcome_back_button = self.draw_back_button(back_btn_x, back_btn_y, "< Bureau")

        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(60 * self.scale_y)
        content_x = (self.screen_width - int(700 * self.scale_x)) // 2

        # Welcome box
        box_width = int(700 * self.scale_x)
        box_height = int(450 * self.scale_y)
        box_rect = pygame.Rect(content_x, content_y, box_width, box_height)

        pygame.draw.rect(self.screen, self.post_bg, box_rect, border_radius=int(10 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, box_rect, 2, border_radius=int(10 * self.scale))

        # Title
        title_y = content_y + int(40 * self.scale_y)
        title = self.title_font.render("CYBER HERO FORUM", True, self.primary_color)
        title_rect = title.get_rect(centerx=self.screen_width // 2, top=title_y)
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle_y = title_rect.bottom + int(10 * self.scale_y)
        subtitle = self.body_font.render("L'Underground des Hackers Ethiques", True, self.accent_color)
        subtitle_rect = subtitle.get_rect(centerx=self.screen_width // 2, top=subtitle_y)
        self.screen.blit(subtitle, subtitle_rect)

        # Divider
        divider_y = subtitle_rect.bottom + int(30 * self.scale_y)
        pygame.draw.line(self.screen, self.border_color,
                        (content_x + int(50 * self.scale_x), divider_y),
                        (content_x + box_width - int(50 * self.scale_x), divider_y), 1)

        # Welcome message
        message_y = divider_y + int(30 * self.scale_y)
        messages = [
            "Bienvenue sur le forum underground de Cyber Hero.",
            "",
            "Pour acceder aux categories et aux discussions,",
            "tu dois d'abord creer un compte ou te connecter.",
            "",
            "Rejoins la communaute maintenant !"
        ]

        for msg in messages:
            if msg:
                msg_surface = self.body_font.render(msg, True, self.text_color)
                msg_rect = msg_surface.get_rect(centerx=self.screen_width // 2, top=message_y)
                self.screen.blit(msg_surface, msg_rect)
                message_y = msg_rect.bottom + int(15 * self.scale_y)
            else:
                message_y += int(10 * self.scale_y)

        # Buttons
        button_y = message_y + int(20 * self.scale_y)
        button_width = int(280 * self.scale_x)
        button_height = int(55 * self.scale_y)
        button_spacing = int(30 * self.scale_x)

        # Register button (primary)
        register_x = self.screen_width // 2 - button_width - button_spacing // 2
        self.register_button_rect = pygame.Rect(register_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        is_register_hovered = self.register_button_rect.collidepoint(mouse_pos)

        register_color = (0, 240, 60) if is_register_hovered else self.primary_color
        pygame.draw.rect(self.screen, register_color, self.register_button_rect, border_radius=int(6 * self.scale))

        register_text = self.heading_font.render("CREER UN COMPTE", True, (0, 0, 0))
        register_text_rect = register_text.get_rect(center=self.register_button_rect.center)
        self.screen.blit(register_text, register_text_rect)

        # Login button (secondary)
        login_x = self.screen_width // 2 + button_spacing // 2
        self.login_button_rect = pygame.Rect(login_x, button_y, button_width, button_height)

        is_login_hovered = self.login_button_rect.collidepoint(mouse_pos)

        login_bg = (35, 35, 35) if is_login_hovered else (25, 25, 25)
        pygame.draw.rect(self.screen, login_bg, self.login_button_rect, border_radius=int(6 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, self.login_button_rect, 2, border_radius=int(6 * self.scale))

        login_text = self.heading_font.render("SE CONNECTER", True, self.text_color)
        login_text_rect = login_text.get_rect(center=self.login_button_rect.center)
        self.screen.blit(login_text, login_text_rect)

        # Bottom info
        info_y = self.screen_height - int(60 * self.scale_y)
        info = self.small_font.render("Connexion securisee via Tor  |  100% Anonyme  |  Pas de tracking", True, self.dim_text)
        info_rect = info.get_rect(centerx=self.screen_width // 2, top=info_y)
        self.screen.blit(info, info_rect)

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ECHAP: Retour au bureau", True, self.dim_text)
        self.screen.blit(instructions, (int(30 * self.scale_x), instructions_y))

    def draw_categories_page(self):
        """Draw categories listing page"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button (only if not logged in - goes to welcome)
        if not self.logged_in:
            self.categories_back_button = self.draw_back_button(content_x, content_y, "< Accueil")
            title_y = content_y + int(50 * self.scale_y)
        else:
            self.categories_back_button = None
            title_y = content_y

        # Page title
        title = self.title_font.render("Catégories du Forum", True, self.primary_color)
        self.screen.blit(title, (content_x, title_y))

        # Category list
        category_y = title_y + int(50 * self.scale_y)
        self.category_rects = {}

        for category in self.categories:
            # Category box
            box_height = int(80 * self.scale_y)
            box_rect = pygame.Rect(content_x, category_y, content_width, box_height)
            self.category_rects[category['id']] = box_rect

            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = box_rect.collidepoint(mouse_pos)
            bg_color = self.post_bg if is_hovered else self.content_bg

            pygame.draw.rect(self.screen, bg_color, box_rect, border_radius=int(5 * self.scale))
            pygame.draw.rect(self.screen, self.border_color, box_rect, 1, border_radius=int(5 * self.scale))

            # Icon
            icon_x = box_rect.x + int(20 * self.scale_x)
            icon_text = self.heading_font.render(category['icon'], True, self.primary_color)
            self.screen.blit(icon_text, (icon_x, box_rect.centery - icon_text.get_height() // 2))

            # Category name
            name_x = icon_x + int(50 * self.scale_x)
            name_text = self.heading_font.render(category['name'], True, self.primary_color if is_hovered else self.text_color)
            self.screen.blit(name_text, (name_x, box_rect.y + int(15 * self.scale_y)))

            # Description
            desc_text = self.small_font.render(category['description'], True, self.dim_text)
            self.screen.blit(desc_text, (name_x, box_rect.y + int(42 * self.scale_y)))

            # Stats (right side)
            stats_x = box_rect.right - int(200 * self.scale_x)
            threads_text = self.small_font.render(f"Sujets: {category['threads']}", True, self.text_color)
            posts_text = self.small_font.render(f"Messages: {category['posts']}", True, self.dim_text)
            self.screen.blit(threads_text, (stats_x, box_rect.y + int(20 * self.scale_y)))
            self.screen.blit(posts_text, (stats_x, box_rect.y + int(45 * self.scale_y)))

            category_y += box_height + int(10 * self.scale_y)

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ECHAP: Retour | CLIC: Ouvrir categorie", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))

    def draw_threads_page(self):
        """Draw threads listing for selected category"""
        category = next((c for c in self.categories if c['id'] == self.selected_category), None)
        if not category:
            return

        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button
        self.threads_back_button = self.draw_back_button(content_x, content_y, "< Categories")
        header_y = content_y + int(50 * self.scale_y)

        # Category header
        header = self.title_font.render(f"{category['icon']} {category['name']}", True, self.primary_color)
        self.screen.blit(header, (content_x, header_y))

        desc = self.small_font.render(category['description'], True, self.dim_text)
        self.screen.blit(desc, (content_x, header_y + int(35 * self.scale_y)))

        # Thread list header
        list_y = header_y + int(80 * self.scale_y)
        header_rect = pygame.Rect(content_x, list_y, content_width, int(30 * self.scale_y))
        pygame.draw.rect(self.screen, self.post_bg, header_rect)

        # Column headers
        col_title = self.small_font.render("SUJET", True, self.accent_color)
        col_author = self.small_font.render("AUTEUR", True, self.accent_color)
        col_replies = self.small_font.render("REP.", True, self.accent_color)
        col_views = self.small_font.render("VUES", True, self.accent_color)
        col_last = self.small_font.render("DERNIER MESSAGE", True, self.accent_color)

        self.screen.blit(col_title, (content_x + int(20 * self.scale_x), list_y + int(8 * self.scale_y)))
        self.screen.blit(col_author, (content_x + int(500 * self.scale_x), list_y + int(8 * self.scale_y)))
        self.screen.blit(col_replies, (content_x + int(700 * self.scale_x), list_y + int(8 * self.scale_y)))
        self.screen.blit(col_views, (content_x + int(800 * self.scale_x), list_y + int(8 * self.scale_y)))
        self.screen.blit(col_last, (content_x + int(920 * self.scale_x), list_y + int(8 * self.scale_y)))

        # Thread list
        thread_y = list_y + int(35 * self.scale_y)
        self.thread_rects = {}

        threads = self.threads.get(self.selected_category, [])

        for thread in threads:
            row_height = int(50 * self.scale_y)
            row_rect = pygame.Rect(content_x, thread_y, content_width, row_height)
            self.thread_rects[thread.id] = row_rect

            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = row_rect.collidepoint(mouse_pos)
            bg_color = self.border_color if is_hovered else self.content_bg

            pygame.draw.rect(self.screen, bg_color, row_rect)
            pygame.draw.line(self.screen, self.border_color,
                           (content_x, thread_y + row_height),
                           (content_x + content_width, thread_y + row_height), 1)

            # Thread title
            title_color = self.pinned_color if thread.pinned else (self.link_color if is_hovered else self.text_color)
            prefix = "📌 " if thread.pinned else ""
            title_text = self.body_font.render(f"{prefix}{thread.title[:60]}", True, title_color)
            self.screen.blit(title_text, (row_rect.x + int(20 * self.scale_x),
                                         row_rect.centery - title_text.get_height() // 2))

            # Author
            author_text = self.small_font.render(thread.author, True, self.dim_text)
            self.screen.blit(author_text, (content_x + int(500 * self.scale_x),
                                          row_rect.centery - author_text.get_height() // 2))

            # Replies
            replies_text = self.small_font.render(str(thread.replies), True, self.dim_text)
            self.screen.blit(replies_text, (content_x + int(720 * self.scale_x),
                                           row_rect.centery - replies_text.get_height() // 2))

            # Views
            views_text = self.small_font.render(str(thread.views), True, self.dim_text)
            self.screen.blit(views_text, (content_x + int(820 * self.scale_x),
                                         row_rect.centery - views_text.get_height() // 2))

            # Last post
            last_text = self.small_font.render(thread.last_post, True, self.dim_text)
            self.screen.blit(last_text, (content_x + int(920 * self.scale_x),
                                        row_rect.centery - last_text.get_height() // 2))

            thread_y += row_height

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ECHAP: Retour aux categories | CLIC: Ouvrir sujet", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))

    def draw_market_page(self):
        """Draw marketplace page"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button
        self.market_back_button = self.draw_back_button(content_x, content_y, "< Categories")
        header_y = content_y + int(50 * self.scale_y)

        # Market header
        header = self.title_font.render("🛒 MARKETPLACE", True, self.primary_color)
        self.screen.blit(header, (content_x, header_y))

        desc_y = header_y + int(45 * self.scale_y)
        desc = self.body_font.render("Telechargez des outils pour vos missions de hacking.", True, self.text_dim)
        self.screen.blit(desc, (content_x, desc_y))

        # Initialize market tool rects if not exists
        if not hasattr(self, 'market_tool_rects'):
            self.market_tool_rects = {}

        # Get downloaded tools from profile
        downloaded_tools = self.profile_data.get('downloaded_tools', [])

        # Check which mission is completed to determine downloadable tools
        progress = self.profile_data.get('progress', {})
        missions_completed = progress.get('missions_completed', [])
        mission1_done = 'mission1' in missions_completed or progress.get('mission1_completed', False)
        mission2_done = 'mission2' in missions_completed

        # Available tools in market
        market_tools = [
            {
                "id": "wireshark",
                "name": "Wireshark",
                "icon": "W",
                "description": "Analyseur de paquets reseau professionnel",
                "size": "45.2 MB",
                "price": 300,  # Updated price
                "downloadable": mission1_done,  # Available after Mission 1
                "required_mission": "mission2"
            },
            {
                "id": "pcap_analyzer",
                "name": "PCAP Analyzer",
                "icon": "P",
                "description": "Analyseur de fichiers capture (hex dump)",
                "size": "8.5 MB",
                "price": 400,  # Updated price
                "downloadable": mission2_done,  # Available after Mission 2
                "required_mission": "mission3"
            },
            {
                "id": "nmap_pro",
                "name": "Nmap Pro",
                "icon": "N",
                "description": "Scanner de ports et vulnerabilites avance",
                "size": "12.8 MB",
                "price": 150,
                "downloadable": False,
                "required_mission": "mission4"
            },
            {
                "id": "metasploit",
                "name": "Metasploit Framework",
                "icon": "M",
                "description": "Framework d'exploitation et pentest",
                "size": "234.5 MB",
                "price": 0,
                "downloadable": False,
                "required_mission": "mission5"
            },
            {
                "id": "burpsuite",
                "name": "Burp Suite",
                "icon": "B",
                "description": "Proxy d'interception HTTP/HTTPS",
                "size": "89.1 MB",
                "price": 0,
                "downloadable": False,
                "required_mission": "mission6"
            },
            {
                "id": "hashcat",
                "name": "Hashcat",
                "icon": "H",
                "description": "Cracker de mots de passe GPU",
                "size": "28.4 MB",
                "price": 0,
                "downloadable": False,
                "required_mission": "mission7"
            },
        ]

        # Draw tools list
        tools_y = desc_y + int(50 * self.scale_y)
        self.market_tool_rects = {}
        
        # Get player credits
        player_credits = self.profile_data.get('progress', {}).get('credits', 0)

        for i, tool in enumerate(market_tools):
            tool_y = tools_y + (i * int(85 * self.scale_y))
            tool_height = int(75 * self.scale_y)
            tool_rect = pygame.Rect(content_x, tool_y, content_width, tool_height)

            # Check if already downloaded
            is_downloaded = tool['id'] in downloaded_tools

            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = tool_rect.collidepoint(mouse_pos)
            bg_color = self.hover_bg if is_hovered else self.post_bg

            pygame.draw.rect(self.screen, bg_color, tool_rect, border_radius=int(8 * self.scale))

            # Border color based on status
            if is_downloaded:
                border_col = (0, 200, 100)  # Green - downloaded
            elif tool['downloadable']:
                border_col = self.primary_color  # Cyan - available
            else:
                border_col = (80, 80, 90)  # Gray - locked

            pygame.draw.rect(self.screen, border_col, tool_rect, width=2, border_radius=int(8 * self.scale))

            # Icon
            icon_x = content_x + int(20 * self.scale_x)
            icon_text = self.title_font.render(tool['icon'], True, self.text_color)
            self.screen.blit(icon_text, (icon_x, tool_rect.centery - icon_text.get_height() // 2))

            # Name and description
            name_x = icon_x + int(50 * self.scale_x)
            name_text = self.heading_font.render(tool['name'], True, self.text_bright)
            self.screen.blit(name_text, (name_x, tool_y + int(12 * self.scale_y)))

            desc_text = self.small_font.render(tool['description'], True, self.text_dim)
            self.screen.blit(desc_text, (name_x, tool_y + int(38 * self.scale_y)))

            size_text = self.small_font.render(f"Taille: {tool['size']} | Prix: {tool['price']}$", True, self.text_dim)
            self.screen.blit(size_text, (name_x, tool_y + int(55 * self.scale_y)))

            # Download button / Status
            btn_width = int(140 * self.scale_x)
            btn_height = int(35 * self.scale_y)
            btn_x = tool_rect.right - btn_width - int(15 * self.scale_x)
            btn_y = tool_rect.centery - btn_height // 2
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

            if is_downloaded:
                # Already downloaded
                pygame.draw.rect(self.screen, (0, 100, 50), btn_rect, border_radius=int(4 * self.scale))
                btn_text = self.small_font.render("INSTALLE", True, (0, 200, 100))
            elif tool['downloadable']:
                # Can download
                can_afford = player_credits >= tool['price']
                if can_afford:
                    btn_hover = btn_rect.collidepoint(mouse_pos)
                    btn_color = (0, 180, 100) if btn_hover else (0, 140, 80)
                    btn_text = self.small_font.render("ACHETER", True, (255, 255, 255))  # Buy button
                    self.market_tool_rects[tool['id']] = btn_rect
                else:
                    btn_color = (100, 50, 50)
                    btn_text = self.small_font.render("FUNDS", True, (255, 200, 200))
                pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=int(4 * self.scale))
            else:
                # Locked
                pygame.draw.rect(self.screen, (50, 50, 55), btn_rect, border_radius=int(4 * self.scale))
                btn_text = self.small_font.render("VERROUILLE", True, (100, 100, 110))

            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            self.screen.blit(btn_text, btn_text_rect)

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ESC: Retour aux categories | Cliquez ACHETER pour installer un outil", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))

    def load_emails_from_inbox(self):
        """Load emails from the inbox system"""
        from src.ui.inbox import Inbox
        inbox = Inbox(self.screen, self.profile_data)
        self.emails = inbox.emails

        # Clear notifications when viewing inbox
        from src.systems.notification_manager import get_notification_manager
        notification_manager = get_notification_manager()
        notification_manager.clear_notification()

    def draw_inbox_page(self):
        """Draw inbox/email page"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button
        self.inbox_back_button = self.draw_back_button(content_x, content_y, "< Forum")
        header_y = content_y + int(50 * self.scale_y)

        # Header
        header = self.title_font.render("📧 MESSAGERIE", True, self.primary_color)
        self.screen.blit(header, (content_x, header_y))

        # Load emails if not already loaded
        if not self.emails:
            self.load_emails_from_inbox()

        # Email list
        list_y = header_y + int(60 * self.scale_y)
        self.email_rects = {}

        if not self.emails:
            # No emails message
            no_email_text = self.body_font.render("Aucun message pour le moment.", True, self.text_dim)
            self.screen.blit(no_email_text, (content_x, list_y))
        else:
            for i, email in enumerate(self.emails):
                email_height = int(70 * self.scale_y)
                email_rect = pygame.Rect(content_x, list_y, content_width, email_height)
                self.email_rects[i] = email_rect

                # Hover/selection effect
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = email_rect.collidepoint(mouse_pos)
                is_selected = (self.selected_email_index == i)

                if is_selected:
                    bg_color = self.button_hover
                elif is_hovered:
                    bg_color = self.hover_bg
                else:
                    bg_color = self.post_bg

                pygame.draw.rect(self.screen, bg_color, email_rect, border_radius=int(5 * self.scale))
                pygame.draw.rect(self.screen, self.border_color, email_rect, width=1, border_radius=int(5 * self.scale))

                # Unread indicator
                if not email.read:
                    unread_x = email_rect.x + int(15 * self.scale_x)
                    unread_y = email_rect.centery
                    pygame.draw.circle(self.screen, self.primary_color, (unread_x, unread_y), int(5 * self.scale))

                # Email info
                text_x = content_x + int(35 * self.scale_x)

                # Sender
                sender_text = self.body_font.render(f"De: {email.sender}", True, self.text_bright if not email.read else self.text_color)
                self.screen.blit(sender_text, (text_x, email_rect.y + int(10 * self.scale_y)))

                # Subject
                subject_text = self.body_font.render(email.subject, True, self.text_bright if not email.read else self.text_color)
                self.screen.blit(subject_text, (text_x, email_rect.y + int(35 * self.scale_y)))

                list_y += email_height + int(10 * self.scale_y)

            # If an email is selected, show its content
            if self.selected_email_index is not None and 0 <= self.selected_email_index < len(self.emails):
                self._draw_email_content(content_x, list_y, content_width)

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("CLIC: Lire l'email | ESC: Retour", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))

    def _draw_email_content(self, content_x: int, start_y: int, content_width: int):
        """Draw selected email content with scrolling"""
        if self.selected_email_index is None:
            return

        email = self.emails[self.selected_email_index]

        # Content panel
        panel_y = start_y + int(10 * self.scale_y)
        panel_height = self.screen_height - panel_y - int(60 * self.scale_y)
        scrollbar_width = int(12 * self.scale_x)
        panel_rect = pygame.Rect(content_x, panel_y, content_width, panel_height)

        pygame.draw.rect(self.screen, self.content_bg, panel_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, panel_rect, width=2, border_radius=int(8 * self.scale))

        # Email header (fixed)
        text_x = content_x + int(20 * self.scale_x)
        header_y = panel_y + int(20 * self.scale_y)

        from_text = self.body_font.render(f"De: {email.sender}", True, self.primary_color)
        self.screen.blit(from_text, (text_x, header_y))
        header_y += from_text.get_height() + int(10 * self.scale_y)

        subject_text = self.heading_font.render(email.subject, True, self.text_bright)
        self.screen.blit(subject_text, (text_x, header_y))
        header_y += subject_text.get_height() + int(15 * self.scale_y)

        # Divider
        pygame.draw.line(self.screen, self.border_color,
                        (text_x, header_y),
                        (content_x + content_width - int(20 * self.scale_x), header_y), 1)

        # Scrollable body area
        body_start_y = header_y + int(15 * self.scale_y)
        visible_height = panel_y + panel_height - body_start_y - int(20 * self.scale_y)
        max_width = content_width - int(60 * self.scale_x) - scrollbar_width

        # Calculate total content height
        body_lines = email.body.split('\n')
        total_height = 0
        line_height = self.body_font.get_height() + int(5 * self.scale_y)

        for line in body_lines:
            if line.strip():
                words = line.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.body_font.render(test_line, True, self.text_color)
                    if test_surface.get_width() > max_width:
                        if current_line:
                            total_height += line_height
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line:
                    total_height += line_height
            else:
                total_height += int(15 * self.scale_y)

        # Calculate max scroll
        self.email_max_scroll = max(0, total_height - visible_height + int(20 * self.scale_y))
        self.email_scroll = max(0, min(self.email_scroll, self.email_max_scroll))

        # Create clipping rect
        clip_rect = pygame.Rect(text_x, body_start_y, max_width + int(10 * self.scale_x), visible_height)
        self.screen.set_clip(clip_rect)

        # Draw email body with scroll
        text_y = body_start_y - self.email_scroll

        for line in body_lines:
            if line.strip():
                words = line.split(' ')
                current_line = ""

                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.body_font.render(test_line, True, self.text_color)

                    if test_surface.get_width() > max_width:
                        if current_line:
                            if body_start_y - line_height < text_y < body_start_y + visible_height:
                                line_surface = self.body_font.render(current_line.strip(), True, self.text_color)
                                self.screen.blit(line_surface, (text_x, text_y))
                            text_y += line_height
                        current_line = word + " "
                    else:
                        current_line = test_line

                if current_line:
                    if body_start_y - line_height < text_y < body_start_y + visible_height:
                        line_surface = self.body_font.render(current_line.strip(), True, self.text_color)
                        self.screen.blit(line_surface, (text_x, text_y))
                    text_y += line_height
            else:
                text_y += int(15 * self.scale_y)

        self.screen.set_clip(None)

        # Draw scroll bar if needed
        if self.email_max_scroll > 0:
            scrollbar_x = content_x + content_width - scrollbar_width - int(10 * self.scale_x)
            track_rect = pygame.Rect(scrollbar_x, body_start_y, scrollbar_width, visible_height)
            pygame.draw.rect(self.screen, (40, 45, 55), track_rect, border_radius=int(4 * self.scale))

            thumb_height = max(int(30 * self.scale_y), int(visible_height * (visible_height / total_height)))
            scroll_ratio = self.email_scroll / self.email_max_scroll if self.email_max_scroll > 0 else 0
            thumb_y = body_start_y + int(scroll_ratio * (visible_height - thumb_height))

            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            mouse_pos = pygame.mouse.get_pos()
            thumb_color = self.primary_color if thumb_rect.collidepoint(mouse_pos) else (80, 100, 90)
            pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=int(4 * self.scale))

    def handle_category_click(self, pos: Tuple[int, int]):
        """Handle click on category"""
        for cat_id, rect in self.category_rects.items():
            if rect.collidepoint(pos):
                self.selected_category = cat_id
                self.current_page = "threads"
                return

    def handle_thread_click(self, pos: Tuple[int, int]):
        """Handle click on thread"""
        for thread_id, rect in self.thread_rects.items():
            if rect.collidepoint(pos):
                # TODO: Open thread view page
                # For now, just print
                print(f"Thread {thread_id} clicked")
                return

    def handle_market_click(self, pos: Tuple[int, int]):
        """Handle click on market tool download buttons"""
        if not hasattr(self, 'market_tool_rects'):
            return

        for tool_id, rect in self.market_tool_rects.items():
            if rect.collidepoint(pos):
                # Start download
                self.start_tool_download(tool_id)
                return

    def start_tool_download(self, tool_id: str):
        """Start downloading a tool with progress bar animation"""
        import time

        # Tool info for display
        tool_names = {
            "wireshark": "Wireshark",
            "pcap_analyzer": "PCAP Analyzer",
            "nmap_pro": "Nmap Pro",
            "metasploit": "Metasploit Framework",
            "burpsuite": "Burp Suite",
            "hashcat": "Hashcat"
        }

        tool_name = tool_names.get(tool_id, tool_id)

        # Find tool price
        tool_price = 0
        # We need to reconstruct the market tools list to find the price or define it here
        # For simplicity, let's use the known prices
        if tool_id == "wireshark":
            tool_price = 300
        elif tool_id == "pcap_analyzer":
            tool_price = 400
        elif tool_id == "nmap_pro":
            tool_price = 150
            
        # Deduct credits
        if 'progress' in self.profile_data and 'credits' in self.profile_data['progress']:
            if self.profile_data['progress']['credits'] >= tool_price:
                self.profile_data['progress']['credits'] -= tool_price
            else:
                return # Should not happen due to UI check, but safety first

        # Download progress bar overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))

        # Progress bar dimensions
        bar_width = int(500 * self.scale_x)
        bar_height = int(30 * self.scale_y)
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2

        # Panel dimensions
        panel_width = int(600 * self.scale_x)
        panel_height = int(150 * self.scale_y)
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = self.screen_height // 2 - int(50 * self.scale_y)

        clock = pygame.time.Clock()

        # Simulate download progress
        progress = 0
        download_speed = 2.5  # Progress per frame

        while progress < 100:
            clock.tick(60)

            # Handle events (allow quit)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # Cancel download

            # Update progress (variable speed for realism)
            import random
            progress += download_speed + random.uniform(-0.5, 1.0)
            if progress > 100:
                progress = 100

            # Draw current market page behind overlay
            self.screen.fill(self.bg_color)
            self.draw_browser_chrome()
            self.draw_top_navigation()
            self.draw_market_page()

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw panel
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (25, 30, 40), panel_rect, border_radius=int(10 * self.scale))
            pygame.draw.rect(self.screen, (0, 200, 100), panel_rect, width=2, border_radius=int(10 * self.scale))

            # Title
            title_text = self.heading_font.render(f"Telechargement de {tool_name}...", True, (0, 220, 100))
            title_rect = title_text.get_rect(centerx=self.screen_width // 2, top=panel_y + int(20 * self.scale_y))
            self.screen.blit(title_text, title_rect)

            # Progress bar background
            bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (40, 45, 55), bar_bg_rect, border_radius=int(5 * self.scale))

            # Progress bar fill
            fill_width = int((progress / 100) * bar_width)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                pygame.draw.rect(self.screen, (0, 200, 100), fill_rect, border_radius=int(5 * self.scale))

            # Progress percentage
            percent_text = self.body_font.render(f"{int(progress)}%", True, (255, 255, 255))
            percent_rect = percent_text.get_rect(center=bar_bg_rect.center)
            self.screen.blit(percent_text, percent_rect)

            # Status text
            status_text = self.small_font.render("Connexion securisee... Ne pas fermer le navigateur", True, (150, 150, 160))
            status_rect = status_text.get_rect(centerx=self.screen_width // 2, top=bar_y + bar_height + int(15 * self.scale_y))
            self.screen.blit(status_text, status_rect)

            pygame.display.flip()

        # Download complete - add to profile
        if 'downloaded_tools' not in self.profile_data:
            self.profile_data['downloaded_tools'] = []

        if tool_id not in self.profile_data['downloaded_tools']:
            self.profile_data['downloaded_tools'].append(tool_id)

            # Save profile
            from src.core.save_load import SaveLoadManager
            save_mgr = SaveLoadManager()
            save_mgr.save_profile(self.profile_data)

        # Show completion message briefly
        complete_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - complete_start < 1500:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # Draw completion
            self.screen.fill(self.bg_color)
            self.draw_browser_chrome()
            self.draw_top_navigation()
            self.draw_market_page()

            self.screen.blit(overlay, (0, 0))

            # Panel
            pygame.draw.rect(self.screen, (25, 30, 40), panel_rect, border_radius=int(10 * self.scale))
            pygame.draw.rect(self.screen, (0, 200, 100), panel_rect, width=2, border_radius=int(10 * self.scale))

            # Success message
            success_text = self.heading_font.render(f"{tool_name} installe avec succes!", True, (0, 255, 100))
            success_rect = success_text.get_rect(centerx=self.screen_width // 2, centery=panel_rect.centery - int(10 * self.scale_y))
            self.screen.blit(success_text, success_rect)

            hint_text = self.body_font.render("Disponible dans Net Scanner sur le bureau", True, (150, 150, 160))
            hint_rect = hint_text.get_rect(centerx=self.screen_width // 2, centery=panel_rect.centery + int(25 * self.scale_y))
            self.screen.blit(hint_text, hint_rect)

            pygame.display.flip()

    def run(self) -> Tuple[str, str]:
        """
        Run the forum browser

        Returns:
            Tuple of (result, action)
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None

                elif event.type == pygame.KEYDOWN:
                    # Handle text input for bio
                    if self.current_page == "profile" and self.editing_bio:
                        if event.key == pygame.K_BACKSPACE:
                            self.temp_bio = self.temp_bio[:-1]
                        elif event.unicode.isprintable() and event.key != pygame.K_ESCAPE:
                            if len(self.temp_bio) < 200:
                                self.temp_bio += event.unicode
                        if event.key != pygame.K_ESCAPE:
                            continue

                    if event.key == pygame.K_ESCAPE:
                        if self.current_page == "profile" and self.avatar_popup_open:
                            self.avatar_popup_open = False
                            continue
                        
                        if self.current_page == "profile" and self.editing_bio:
                            self.editing_bio = False
                            continue

                        if self.current_page == "profile" and self.avatar_popup_open:
                            self.avatar_popup_open = False
                            continue

                        # Navigate back
                        if self.current_page == "threads":
                            self.current_page = "categories"
                            self.selected_category = None
                        elif self.current_page == "market":
                            self.current_page = "categories"
                        elif self.current_page == "inbox":
                            self.current_page = "categories"
                            self.selected_email_index = None
                        elif self.current_page == "profile":
                            self.current_page = "categories"
                            self.edit_mode = False
                        elif self.current_page == "categories":
                            if self.logged_in:
                                return "back", None
                            else:
                                self.current_page = "welcome"
                        elif self.current_page == "welcome":
                            return "back", None

                elif event.type == pygame.MOUSEWHEEL:
                    # Scroll email content if on inbox page with email selected
                    if self.current_page == "inbox" and self.selected_email_index is not None:
                        self.email_scroll -= event.y * self.email_scroll_speed
                        self.email_scroll = max(0, min(self.email_scroll, self.email_max_scroll))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check exit button
                        if self.exit_button_rect and self.exit_button_rect.collidepoint(event.pos):
                            return "back", None

                        # Check back button click (browser navigation)
                        if hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(event.pos):
                            # Navigate back based on current page
                            if self.current_page == "threads":
                                self.current_page = "categories"
                                self.selected_category = None
                            elif self.current_page == "categories":
                                if self.logged_in:
                                    # Stay on categories (main page when logged in)
                                    pass
                                else:
                                    self.current_page = "welcome"
                            elif self.current_page == "market":
                                self.current_page = "categories"
                            elif self.current_page == "thread_view":
                                self.current_page = "threads"
                            # Continue to prevent other click handlers from firing
                            continue

                        # Check navigation tab clicks (available on all pages)
                        if hasattr(self, 'nav_tab_rects'):
                            for tab_id, tab_rect in self.nav_tab_rects.items():
                                if tab_rect.collidepoint(event.pos):
                                    # If not logged in, show message requiring account
                                    if not self.logged_in:
                                        # User must create account first
                                        # Force them to welcome page
                                        if self.current_page != "welcome":
                                            self.current_page = "welcome"
                                    else:
                                        # Logged in, can navigate
                                        if tab_id == "forum":
                                            self.current_page = "categories"
                                            self.selected_category = None
                                        elif tab_id == "profile":
                                            # Show profile page within forum
                                            self.current_page = "profile"
                                        elif tab_id == "market":
                                            # Market page
                                            self.current_page = "market"
                                        elif tab_id == "email":
                                            # Open inbox page within forum
                                            self.current_page = "inbox"
                                    # Don't process other clicks if tab was clicked
                                    continue

                        # Check content back button clicks (page-specific back buttons)
                        if self.current_page == "welcome":
                            if hasattr(self, 'welcome_back_button') and self.welcome_back_button and self.welcome_back_button.collidepoint(event.pos):
                                return "back", None
                        elif self.current_page == "categories":
                            if hasattr(self, 'categories_back_button') and self.categories_back_button and self.categories_back_button.collidepoint(event.pos):
                                self.current_page = "welcome"
                                continue
                        elif self.current_page == "threads":
                            if hasattr(self, 'threads_back_button') and self.threads_back_button and self.threads_back_button.collidepoint(event.pos):
                                self.current_page = "categories"
                                self.selected_category = None
                                continue
                        elif self.current_page == "market":
                            if hasattr(self, 'market_back_button') and self.market_back_button and self.market_back_button.collidepoint(event.pos):
                                self.current_page = "categories"
                                continue
                        elif self.current_page == "inbox":
                            if hasattr(self, 'inbox_back_button') and self.inbox_back_button and self.inbox_back_button.collidepoint(event.pos):
                                self.current_page = "categories"
                                continue
                        elif self.current_page == "profile":
                            if self.avatar_popup_open:
                                for rect, avatar_name in self.avatar_option_rects:
                                    if rect.collidepoint(event.pos):
                                        self.profile_data['avatar'] = avatar_name
                                        self.avatar_popup_open = False
                                        break
                                continue

                            # Bio editing clicks
                            if self.editing_bio:
                                if self.save_bio_btn_rect and self.save_bio_btn_rect.collidepoint(event.pos):
                                    self.profile_data['bio'] = self.temp_bio
                                    self.editing_bio = False
                                    # Save profile to disk
                                    from src.core.save_load import SaveLoadManager
                                    SaveLoadManager().save_profile(self.profile_data)
                                    continue
                                    
                                if self.cancel_bio_btn_rect and self.cancel_bio_btn_rect.collidepoint(event.pos):
                                    self.editing_bio = False
                                    continue
                            else:
                                if self.edit_bio_btn_rect and self.edit_bio_btn_rect.collidepoint(event.pos):
                                    self.editing_bio = True
                                    self.temp_bio = self.profile_data.get('bio', '')
                                    continue

                            if hasattr(self, 'change_avatar_button_rect') and self.change_avatar_button_rect and self.change_avatar_button_rect.collidepoint(event.pos):
                                self.avatar_popup_open = True
                                continue

                            if hasattr(self, 'profile_back_button') and self.profile_back_button and self.profile_back_button.collidepoint(event.pos):
                                self.current_page = "categories"
                                self.edit_mode = False
                                continue

                        # Page-specific click handling
                        if self.current_page == "welcome":
                            # Handle login/register buttons
                            if self.login_button_rect and self.login_button_rect.collidepoint(event.pos):
                                from src.ui.forum_auth import ForumAuth
                                auth = ForumAuth(self.screen, mode="login")
                                result, profile_data = auth.run()

                                if result == "success" and profile_data:
                                    self.logged_in = True
                                    self.username = profile_data['nickname']
                                    self.profile_data = profile_data
                                    self.current_page = "categories"
                                elif result == "back":
                                    # Stay on welcome page
                                    pass
                                elif result == "exit":
                                    return "exit", None

                            elif self.register_button_rect and self.register_button_rect.collidepoint(event.pos):
                                from src.ui.forum_auth import ForumAuth
                                auth = ForumAuth(self.screen, mode="register")
                                result, profile_data = auth.run()

                                if result == "success" and profile_data:
                                    self.logged_in = True
                                    self.username = profile_data['nickname']
                                    self.profile_data = profile_data
                                    self.current_page = "categories"
                                    # Return to main game with profile data
                                    return "create_account", profile_data
                                elif result == "back":
                                    # Stay on welcome page
                                    pass
                                elif result == "exit":
                                    return "exit", None

                        elif self.current_page == "categories":
                            self.handle_category_click(event.pos)
                        elif self.current_page == "threads":
                            self.handle_thread_click(event.pos)
                        elif self.current_page == "inbox":
                            self.handle_email_click(event.pos)
                        elif self.current_page == "market":
                            self.handle_market_click(event.pos)

            # Drawing
            self.screen.fill(self.bg_color)
            self.draw_browser_chrome()
            self.draw_top_navigation()

            if self.current_page == "welcome":
                self.draw_welcome_page()
            elif self.current_page == "categories":
                self.draw_categories_page()
            elif self.current_page == "threads":
                self.draw_threads_page()
            elif self.current_page == "market":
                self.draw_market_page()
            elif self.current_page == "inbox":
                self.draw_inbox_page()
            elif self.current_page == "profile":
                self.draw_profile_page()

            pygame.display.flip()

        return "exit", None

    def load_emails_from_inbox(self):
        """Load emails from the inbox system"""
        from src.ui.inbox import Inbox
        inbox = Inbox(self.screen, self.profile_data)
        self.emails = inbox.emails

        # Clear notifications when viewing inbox
        from src.systems.notification_manager import get_notification_manager
        notification_manager = get_notification_manager()
        notification_manager.clear_notification()

    def draw_inbox_page(self):
        """Draw inbox/email page"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button
        self.inbox_back_button = self.draw_back_button(content_x, content_y, "< Forum")
        header_y = content_y + int(50 * self.scale_y)

        # Header
        header = self.title_font.render("MESSAGERIE", True, self.primary_color)
        self.screen.blit(header, (content_x, header_y))

        # Load emails if not already loaded
        if not self.emails:
            self.load_emails_from_inbox()

        # Email list
        list_y = header_y + int(60 * self.scale_y)
        self.email_rects = {}

        if not self.emails:
            # No emails message
            no_email_text = self.body_font.render("Aucun message pour le moment.", True, self.text_dim)
            self.screen.blit(no_email_text, (content_x, list_y))
        else:
            for i, email in enumerate(self.emails):
                email_height = int(70 * self.scale_y)
                email_rect = pygame.Rect(content_x, list_y, content_width, email_height)
                self.email_rects[i] = email_rect

                # Hover/selection effect
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = email_rect.collidepoint(mouse_pos)
                is_selected = (self.selected_email_index == i)

                if is_selected:
                    bg_color = self.button_hover
                elif is_hovered:
                    bg_color = self.hover_bg
                else:
                    bg_color = self.post_bg

                pygame.draw.rect(self.screen, bg_color, email_rect, border_radius=int(5 * self.scale))
                pygame.draw.rect(self.screen, self.border_color, email_rect, width=1, border_radius=int(5 * self.scale))

                # Unread indicator
                if not email.read:
                    unread_x = email_rect.x + int(15 * self.scale_x)
                    unread_y = email_rect.centery
                    pygame.draw.circle(self.screen, self.primary_color, (unread_x, unread_y), int(5 * self.scale))

                # Email info
                text_x = content_x + int(35 * self.scale_x)

                # Sender
                sender_text = self.body_font.render(f"De: {email.sender}", True, self.text_bright if not email.read else self.text_color)
                self.screen.blit(sender_text, (text_x, email_rect.y + int(10 * self.scale_y)))

                # Subject
                subject_text = self.body_font.render(email.subject, True, self.text_bright if not email.read else self.text_color)
                self.screen.blit(subject_text, (text_x, email_rect.y + int(35 * self.scale_y)))

                list_y += email_height + int(10 * self.scale_y)

            # If an email is selected, show its content
            if self.selected_email_index is not None and 0 <= self.selected_email_index < len(self.emails):
                self._draw_email_content(content_x, list_y, content_width)

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("CLIC: Lire l'email | ESC: Retour", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))

    def _draw_email_content(self, content_x: int, start_y: int, content_width: int):
        """Draw selected email content with scrolling"""
        if self.selected_email_index is None:
            return

        email = self.emails[self.selected_email_index]

        # Content panel
        panel_y = start_y + int(10 * self.scale_y)
        panel_height = self.screen_height - panel_y - int(60 * self.scale_y)
        scrollbar_width = int(12 * self.scale_x)
        panel_rect = pygame.Rect(content_x, panel_y, content_width, panel_height)

        pygame.draw.rect(self.screen, self.content_bg, panel_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, panel_rect, width=2, border_radius=int(8 * self.scale))

        # Email header (fixed)
        text_x = content_x + int(20 * self.scale_x)
        header_y = panel_y + int(20 * self.scale_y)

        from_text = self.body_font.render(f"De: {email.sender}", True, self.primary_color)
        self.screen.blit(from_text, (text_x, header_y))
        header_y += from_text.get_height() + int(10 * self.scale_y)

        subject_text = self.heading_font.render(email.subject, True, self.text_bright)
        self.screen.blit(subject_text, (text_x, header_y))
        header_y += subject_text.get_height() + int(15 * self.scale_y)

        # Divider
        pygame.draw.line(self.screen, self.border_color,
                        (text_x, header_y),
                        (content_x + content_width - int(20 * self.scale_x), header_y), 1)

        # Scrollable body area
        body_start_y = header_y + int(15 * self.scale_y)
        visible_height = panel_y + panel_height - body_start_y - int(20 * self.scale_y)
        max_width = content_width - int(60 * self.scale_x) - scrollbar_width

        # Calculate total content height
        body_lines = email.body.split('\n')
        total_height = 0
        line_height = self.body_font.get_height() + int(5 * self.scale_y)

        for line in body_lines:
            if line.strip():
                words = line.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.body_font.render(test_line, True, self.text_color)
                    if test_surface.get_width() > max_width:
                        if current_line:
                            total_height += line_height
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line:
                    total_height += line_height
            else:
                total_height += int(15 * self.scale_y)

        # Calculate max scroll
        self.email_max_scroll = max(0, total_height - visible_height + int(20 * self.scale_y))
        self.email_scroll = max(0, min(self.email_scroll, self.email_max_scroll))

        # Create clipping rect
        clip_rect = pygame.Rect(text_x, body_start_y, max_width + int(10 * self.scale_x), visible_height)
        self.screen.set_clip(clip_rect)

        # Draw email body with scroll
        text_y = body_start_y - self.email_scroll

        for line in body_lines:
            if line.strip():
                words = line.split(' ')
                current_line = ""

                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.body_font.render(test_line, True, self.text_color)

                    if test_surface.get_width() > max_width:
                        if current_line:
                            if body_start_y - line_height < text_y < body_start_y + visible_height:
                                line_surface = self.body_font.render(current_line.strip(), True, self.text_color)
                                self.screen.blit(line_surface, (text_x, text_y))
                            text_y += line_height
                        current_line = word + " "
                    else:
                        current_line = test_line

                if current_line:
                    if body_start_y - line_height < text_y < body_start_y + visible_height:
                        line_surface = self.body_font.render(current_line.strip(), True, self.text_color)
                        self.screen.blit(line_surface, (text_x, text_y))
                    text_y += line_height
            else:
                text_y += int(15 * self.scale_y)

        self.screen.set_clip(None)

        # Draw scroll bar if needed
        if self.email_max_scroll > 0:
            scrollbar_x = content_x + content_width - scrollbar_width - int(10 * self.scale_x)
            track_rect = pygame.Rect(scrollbar_x, body_start_y, scrollbar_width, visible_height)
            pygame.draw.rect(self.screen, (40, 45, 55), track_rect, border_radius=int(4 * self.scale))

            thumb_height = max(int(30 * self.scale_y), int(visible_height * (visible_height / total_height)))
            scroll_ratio = self.email_scroll / self.email_max_scroll if self.email_max_scroll > 0 else 0
            thumb_y = body_start_y + int(scroll_ratio * (visible_height - thumb_height))

            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            mouse_pos = pygame.mouse.get_pos()
            thumb_color = self.primary_color if thumb_rect.collidepoint(mouse_pos) else (80, 100, 90)
            pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=int(4 * self.scale))


    def draw_profile_page(self):
        """Draw profile page within forum"""
        content_y = self.browser_bar_height + self.url_bar_height + self.top_bar_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Back button
        self.profile_back_button = self.draw_back_button(content_x, content_y, "< Forum")
        header_y = content_y + int(50 * self.scale_y)

        # Header
        header_text = f"Profil de {self.profile_data.get('nickname', 'Joueur')}"
        header = self.title_font.render(header_text, True, self.primary_color)
        self.screen.blit(header, (content_x, header_y))

        # Simple profile view for now
        profile_y = header_y + int(60 * self.scale_y)
        
        # Avatar Section
        current_avatar = self.profile_data.get('avatar', 'avatar_1.png')
        
        # Draw Avatar Box (Placeholder if image not found)
        avatar_size = int(120 * self.scale)
        avatar_rect = pygame.Rect(content_x, profile_y, avatar_size, avatar_size)
        
        # Draw background
        pygame.draw.rect(self.screen, self.post_bg, avatar_rect, border_radius=int(10 * self.scale))
        
        # Try to load avatar image
        avatar_surf = self._get_avatar_image(current_avatar, avatar_size)
        
        if avatar_surf:
            # Draw image
            # Create a mask for rounded corners (simple blit for now)
            # For better rounded corners on images, we would need a mask surface, 
            # but drawing it directly inside the border works well enough for this style.
            self.screen.blit(avatar_surf, avatar_rect)
        else:
            # Fallback text
            avatar_text = self.heading_font.render(current_avatar[:2].upper(), True, self.primary_color)
            text_rect = avatar_text.get_rect(center=avatar_rect.center)
            self.screen.blit(avatar_text, text_rect)
            
        # Draw border
        pygame.draw.rect(self.screen, self.border_color, avatar_rect, 2, border_radius=int(10 * self.scale))
        
        # Change Avatar Button
        btn_width = int(200 * self.scale_x)
        btn_height = int(40 * self.scale_y)
        btn_x = content_x + avatar_size + int(30 * self.scale_x)
        btn_y = profile_y + int(15 * self.scale_y)
        
        self.change_avatar_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.change_avatar_button_rect.collidepoint(mouse_pos)
        btn_color = self.button_hover if is_hovered else self.button_bg
        
        pygame.draw.rect(self.screen, btn_color, self.change_avatar_button_rect, border_radius=int(5 * self.scale))
        pygame.draw.rect(self.screen, self.border_color, self.change_avatar_button_rect, 1, border_radius=int(5 * self.scale))
        
        btn_text = self.body_font.render("CHANGER AVATAR", True, self.text_color)
        btn_text_rect = btn_text.get_rect(center=self.change_avatar_button_rect.center)
        self.screen.blit(btn_text, btn_text_rect)
        
        # XP and Level Stats
        xp = self.profile_data.get('progress', {}).get('xp', 0)
        level = self.profile_data.get('progress', {}).get('level', 'Debutant')
        stats_text = self.body_font.render(f"Niveau: {level}  |  XP: {xp}", True, self.accent_color)
        self.screen.blit(stats_text, (btn_x, btn_y + btn_height + int(15 * self.scale_y)))
        
        profile_y += avatar_size + int(40 * self.scale_y)

        # Bio
        bio_title = self.heading_font.render("Biographie:", True, self.text_color)
        self.screen.blit(bio_title, (content_x, profile_y))
        
        # Edit Bio Button (if not editing)
        if not self.editing_bio:
            edit_btn_text = self.small_font.render("[MODIFIER]", True, self.accent_color)
            edit_btn_x = content_x + bio_title.get_width() + int(20 * self.scale_x)
            edit_btn_y = profile_y + (bio_title.get_height() - edit_btn_text.get_height()) // 2
            self.edit_bio_btn_rect = pygame.Rect(edit_btn_x, edit_btn_y, edit_btn_text.get_width(), edit_btn_text.get_height())
            
            # Hover effect
            if self.edit_bio_btn_rect.collidepoint(pygame.mouse.get_pos()):
                edit_btn_text = self.small_font.render("[MODIFIER]", True, self.primary_color)
                
            self.screen.blit(edit_btn_text, (edit_btn_x, edit_btn_y))
            
            profile_y += int(40 * self.scale_y)
            
            bio_text = self.profile_data.get('bio', 'Aucune biographie')
            bio_surface = self.body_font.render(bio_text, True, self.text_dim)
            self.screen.blit(bio_surface, (content_x, profile_y))
            
        else:
            # Editing mode
            profile_y += int(40 * self.scale_y)
            
            # Input box
            input_width = int(600 * self.scale_x)
            input_height = int(50 * self.scale_y)
            self.bio_input_rect = pygame.Rect(content_x, profile_y, input_width, input_height)
            
            pygame.draw.rect(self.screen, self.input_bg, self.bio_input_rect, border_radius=int(5 * self.scale))
            pygame.draw.rect(self.screen, self.primary_color, self.bio_input_rect, 1, border_radius=int(5 * self.scale))
            
            # Render text
            bio_surface = self.body_font.render(self.temp_bio, True, self.text_bright)
            self.screen.blit(bio_surface, (content_x + 10, profile_y + 10))
            
            # Cursor
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = content_x + 10 + bio_surface.get_width()
                cursor_y = profile_y + 10
                pygame.draw.line(self.screen, self.primary_color, (cursor_x, cursor_y), (cursor_x, cursor_y + bio_surface.get_height()), 2)
            
            # Save/Cancel buttons
            btn_y = profile_y + input_height + int(10 * self.scale_y)
            
            # Save
            save_text = self.small_font.render("[SAUVEGARDER]", True, self.primary_color)
            self.save_bio_btn_rect = pygame.Rect(content_x, btn_y, save_text.get_width(), save_text.get_height())
            self.screen.blit(save_text, (content_x, btn_y))
            
            # Cancel
            cancel_text = self.small_font.render("[ANNULER]", True, self.error_color)
            self.cancel_bio_btn_rect = pygame.Rect(content_x + save_text.get_width() + 20, btn_y, cancel_text.get_width(), cancel_text.get_height())
            self.screen.blit(cancel_text, (content_x + save_text.get_width() + 20, btn_y))

        # Instructions
        instructions_y = self.screen_height - int(35 * self.scale_y)
        instructions = self.small_font.render("ESC: Retour au forum", True, self.dim_text)
        self.screen.blit(instructions, (content_x, instructions_y))
        
        # Draw Popup if open
        if self.avatar_popup_open:
            self.draw_avatar_popup()

    def draw_avatar_popup(self):
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Popup Box
        popup_width = int(600 * self.scale_x)
        popup_height = int(400 * self.scale_y)
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, self.content_bg, popup_rect, border_radius=int(10 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, popup_rect, 2, border_radius=int(10 * self.scale))
        
        # Title
        title = self.heading_font.render("CHOISIR UN AVATAR", True, self.text_bright)
        title_rect = title.get_rect(centerx=popup_rect.centerx, top=popup_y + int(20 * self.scale_y))
        self.screen.blit(title, title_rect)
        
        # Avatar Grid
        grid_y = title_rect.bottom + int(30 * self.scale_y)
        grid_start_x = popup_x + int(50 * self.scale_x)
        
        self.avatar_option_rects = []
        
        # 3x2 grid
        cols = 3
        spacing_x = int(30 * self.scale_x)
        spacing_y = int(30 * self.scale_y)
        item_size = int(100 * self.scale)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, avatar_name in enumerate(self.avatar_options):
            row = i // cols
            col = i % cols
            
            x = grid_start_x + col * (item_size + spacing_x)
            y = grid_y + row * (item_size + spacing_y)
            
            rect = pygame.Rect(x, y, item_size, item_size)
            self.avatar_option_rects.append((rect, avatar_name))
            
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = self.profile_data.get('avatar') == avatar_name
            
            bg_color = self.button_hover if is_hovered else self.post_bg
            border_col = self.primary_color if is_selected else (self.accent_color if is_hovered else self.border_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=int(8 * self.scale))
            pygame.draw.rect(self.screen, border_col, rect, 2 if is_selected else 1, border_radius=int(8 * self.scale))
            
            # Draw avatar image
            avatar_surf = self._get_avatar_image(avatar_name, item_size)
            if avatar_surf:
                self.screen.blit(avatar_surf, rect)
            else:
                # Placeholder text for avatar image
                text = self.heading_font.render(str(i+1), True, self.text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
            
        # Close instruction
        close_text = self.small_font.render("Cliquer pour selectionner | ESC pour fermer", True, self.dim_text)
        close_rect = close_text.get_rect(centerx=popup_rect.centerx, bottom=popup_rect.bottom - int(20 * self.scale_y))
        self.screen.blit(close_text, close_rect)

    def _get_avatar_image(self, avatar_name: str, size: int) -> Optional[pygame.Surface]:
        """Get avatar image from cache or load it"""
        cache_key = (avatar_name, size)
        if cache_key in self.avatar_cache:
            return self.avatar_cache[cache_key]
            
        # Define search paths
        paths_to_check = [os.path.join("assets", "avatars", avatar_name)]
        
        if getattr(sys, 'frozen', False):
             data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
             paths_to_check.append(os.path.join(data_dir, "assets", "avatars", avatar_name))
             
        for path in paths_to_check:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    scaled = pygame.transform.smoothscale(img, (size, size))
                    self.avatar_cache[cache_key] = scaled
                    return scaled
                except Exception as e:
                    print(f"Error loading avatar {path}: {e}")
                
        # Cache None so we don't retry every frame if missing
        self.avatar_cache[cache_key] = None
        return None

    def handle_category_click(self, pos: Tuple[int, int]):
        """Handle click on category"""
        for cat_id, rect in self.category_rects.items():
            if rect.collidepoint(pos):
                self.selected_category = cat_id
                self.current_page = "threads"
                return

    def handle_thread_click(self, pos: Tuple[int, int]):
        """Handle click on thread"""
        for thread_id, rect in self.thread_rects.items():
            if rect.collidepoint(pos):
                # TODO: Open thread view page
                print(f"Thread {thread_id} clicked")
                return

    def handle_email_click(self, pos: Tuple[int, int]):
        """Handle click on email"""
        for email_idx, rect in self.email_rects.items():
            if rect.collidepoint(pos):
                self.selected_email_index = email_idx
                self.email_scroll = 0  # Reset scroll when selecting new email
                # Mark email as read
                if email_idx < len(self.emails):
                    self.emails[email_idx].read = True
                return
