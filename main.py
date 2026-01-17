# -*- coding: utf-8 -*-
import cv2
import numpy as np
import sys
import os
import time
import pygame

# Initialize Pygame
pygame.init()

# --- EXE COMPATIBILITY FIX ---
if getattr(sys, 'frozen', False):
    # If running as compiled exe, change current directory to the temp folder
    # where assets are extracted (sys._MEIPASS)
    os.chdir(sys._MEIPASS)
    # Set persistent data path to the executable folder (where the .exe is)
    os.environ["CYBERHERO_DATA_DIR"] = os.path.dirname(sys.executable)
else:
    # Set persistent data path to the project folder
    os.environ["CYBERHERO_DATA_DIR"] = os.path.dirname(os.path.abspath(__file__))
# -----------------------------

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import screen manager FIRST
from src.core.screen_manager import ScreenManager

# Create global screen manager instance
screen_manager = ScreenManager()

# Import UI classes (ACTIVE)
from src.ui.interactive_desktop import InteractiveDesktop
from src.ui.welcome_sequence import WelcomeSequence
from src.ui.forum_browser import ForumBrowser
from src.ui.inbox import Inbox
from src.ui.settings import SettingsUI
from src.core.settings_manager import settings_manager
from src.apps.terminal_app import TerminalApp

# Import UI classes
from src.ui.load_game_ui import LoadGameUI

# Import game systems
from src.core.save_load import SaveLoadManager
from src.missions.mission_manager import MissionManager

# Set screen manager in UI modules
import src.ui.load_game_ui as load_game_ui_module
load_game_ui_module.screen_manager = screen_manager

import src.ui.settings as settings_module
settings_module.screen_manager = screen_manager

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
DARK_GREEN = (0, 100, 0)
HOVER_GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Button:
    """Interactive button class"""
    def __init__(self, x, y, width, height, text, font, scale_x=1.0, scale_y=1.0):
        self.rect = pygame.Rect(x * scale_x, y * scale_y, width * scale_x, height * scale_y)
        self.text = text
        self.font = font
        self.is_hovered = False
        
    def draw(self, screen):
        color = HOVER_GREEN if self.is_hovered else GREEN
        border_color = CYAN if self.is_hovered else GREEN
        
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(180)
        s.fill(BLACK)
        screen.blit(s, (self.rect.x, self.rect.y))
        
        pygame.draw.rect(screen, border_color, self.rect, 3)
        
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


def play_video_animation(screen, video_path):
    """
    Play a video animation MP4 (without skip option)
    
    Args:
        screen: Pygame Surface
        video_path: Path to MP4 file
    
    Returns:
        True if animation completed, False if cancelled
    """
    # Get current screen size
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"[WARNING] Video not found: {video_path}")
        return True
    
    # Open the video
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        clock = pygame.time.Clock()
        
        playing = True
        while playing:
            ret, frame = cap.read()
            
            # If video ended
            if not ret:
                cap.release()
                return True
            
            # Handle events (only QUIT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit(0)
            
            # Convert OpenCV frame (BGR) to Pygame (RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            
            # Scale to current screen size
            frame_surface = pygame.surfarray.make_surface(frame)
            frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))
            
            # Display
            screen.blit(frame_surface, (0, 0))
            
            pygame.display.flip()
            clock.tick(fps)
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"[ERROR] Could not play video: {e}")
        return True


class MainMenu:
    """Main menu screen"""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Get current screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Calculate scaling factors
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        
        # Fonts (scaled)
        self.title_font = pygame.font.Font(None, int(74 * min(self.scale_x, self.scale_y)))
        self.button_font = pygame.font.Font(None, int(40 * min(self.scale_x, self.scale_y)))
        self.subtitle_font = pygame.font.Font(None, int(32 * min(self.scale_x, self.scale_y)))
        
        # Load background image (if exists)
        self.background = self.load_background()
        
        # Create buttons (scaled)
        button_width = 250 * self.scale_x
        button_height = 70 * self.scale_y
        button_x = 50 * self.scale_x
        start_y = 240 * self.scale_y
        spacing = 90 * self.scale_y
        
        self.buttons = [
            Button(50, 240, 250, 70, "Nouvelle Partie", self.button_font, self.scale_x, self.scale_y),
            Button(50, 330, 250, 70, "Charger", self.button_font, self.scale_x, self.scale_y),
            Button(50, 420, 250, 70, "Parametres", self.button_font, self.scale_x, self.scale_y),
            Button(50, 510, 250, 70, "Credits", self.button_font, self.scale_x, self.scale_y),
            Button(50, 600, 250, 70, "Quitter", self.button_font, self.scale_x, self.scale_y),
        ]
        
    def load_background(self):
        """Load background image from assets folder and scale to current screen"""
        possible_paths = [
            "assets/ui/menu_background.png",
            "assets/ui/menu_background.jpg",
            "assets/menu_background.png",
            "assets/main_menu.png",
            "assets/background.png",
            "menu_background.png",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    bg = pygame.image.load(path)
                    return pygame.transform.scale(bg, (self.screen_width, self.screen_height))
                except Exception as e:
                    print(f"[WARNING] Could not load background {path}: {e}")
        
        return None
    
    def draw_background(self):
        """Draw background - either image or gradient"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            for y in range(self.screen_height):
                color_value = int(20 - (y / self.screen_height) * 15)
                pygame.draw.line(self.screen, (color_value, color_value, color_value), 
                               (0, y), (self.screen_width, y))
    
    def draw_title(self):
        """Draw game title"""
        # Main title - aligned to the left (scaled)
        title_text = "CYBERHERO"
        title_surface = self.title_font.render(title_text, True, GREEN)
        title_x = 50 * self.scale_x
        title_y = 50 * self.scale_y
        
        # Title shadow
        shadow_surface = self.title_font.render(title_text, True, DARK_GREEN)
        self.screen.blit(shadow_surface, (title_x + 3 * self.scale_x, title_y + 3 * self.scale_y))
        self.screen.blit(title_surface, (title_x, title_y))
        
        # Subtitle - aligned to the left
        subtitle_text = "Jeu de Hacking et Cybersecurite"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, CYAN)
        self.screen.blit(subtitle_surface, (50 * self.scale_x, 120 * self.scale_y))

        # Tagline - aligned to the left
        tagline_text = "Apprendre. Hacker. Defendre."
        tagline_surface = self.subtitle_font.render(tagline_text, True, WHITE)
        self.screen.blit(tagline_surface, (50 * self.scale_x, 170 * self.scale_y))
    
    def run(self):
        """Main menu loop"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        if i == 0:
                            return "new_game"
                        elif i == 1:
                            return "load_game"
                        elif i == 2:
                            return "settings"
                        elif i == 3:
                            return "credits"
                        elif i == 4:
                            return "exit"
            
            self.draw_background()
            self.draw_title()
            
            for button in self.buttons:
                button.draw(self.screen)
            
            # Version text (scaled)
            version_text = "v0.1.0 Alpha"
            version_font = pygame.font.Font(None, int(24 * min(self.scale_x, self.scale_y)))
            version_surface = version_font.render(version_text, True, WHITE)
            self.screen.blit(version_surface, (10 * self.scale_x, self.screen_height - 30 * self.scale_y))
            
            pygame.display.flip()
        
        return "exit"


class CreditsScreen:
    """Écran des crédits"""
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()
        
        # Calculate scaling
        self.scale = min(self.screen_width / 1920, self.screen_height / 1080)
        
        # Fonts (scaled)
        self.font = pygame.font.Font(None, int(48 * self.scale))
        self.small_font = pygame.font.Font(None, int(32 * self.scale))
        
        # Load background image
        try:
            self.background = pygame.image.load(r"C:\Users\nasrellahhabchi\Documents\cyberhero\assets\ui\menu_background.png")
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except:
            self.background = None
        
        # Tweakable parameters
        self.left_margin = 100 * self.scale  # Distance from left edge
        self.top_margin = 150 * self.scale   # Distance from top
        self.line_spacing = 50 * self.scale  # Space between lines
        self.title_spacing = 100 * self.scale  # Space after title
        
    def run(self):
        """Afficher les crédits"""
        running = True
        
        while running:
            self.clock.tick(60)  # FPS
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return "menu"
            
            # Draw background or fill with black
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill((0, 0, 0))  # BLACK
            
            y_offset = self.top_margin
            
            # Title
            title = self.font.render("CRÉDITS", True, (0, 255, 0))  # GREEN
            self.screen.blit(title, (self.left_margin, y_offset))
            
            y_offset += self.title_spacing
            
            # Credits lines
            credits_lines = [
                "Programmé par : HABCHI NASRELLAH",
                "Équipe :",
                "AMINA BOUTARF",
                "NOUHAILA SABAFI",
                "DOHA IBBUR",
                "HALIMA JAMALEDDINE",
                "",
                "Un serious game pour l'éducation en cybersécurité",
                "",
                "Version : 0.1.0 - Alpha",
                "",
                "Merci d'avoir joué !",
            ]
            
            for line in credits_lines:
                text = self.small_font.render(line, True, (255, 255, 255))  # WHITE
                self.screen.blit(text, (self.left_margin, y_offset))
                y_offset += self.line_spacing
            
            # Bottom prompt
            prompt = self.small_font.render("Appuyez sur n'importe quelle touche pour revenir...", True, (0, 255, 255))  # CYAN
            self.screen.blit(prompt, (self.left_margin, self.screen_height - 100 * self.scale))
            
            pygame.display.flip()
        
        return "menu"


def show_message(screen, message, color=GREEN, duration=2000):
    """Display a temporary message on screen"""
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Scale font based on screen size
    scale = min(screen_width / 1920, screen_height / 1080)
    
    try:
        font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(32 * scale))
        title_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(42 * scale))
    except:
        font = pygame.font.Font(None, int(36 * scale))
        title_font = pygame.font.Font(None, int(48 * scale))
    
    # Capture current screen for background
    background = screen.copy()
    
    # Draw dimmed overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))
    
    # Draw message box
    box_width = int(900 * scale)
    box_height = int(250 * scale)
    box_rect = pygame.Rect((screen_width - box_width) // 2, (screen_height - box_height) // 2, box_width, box_height)
    
    pygame.draw.rect(screen, (20, 25, 35), box_rect, border_radius=int(15 * scale))
    pygame.draw.rect(screen, color, box_rect, int(3 * scale), border_radius=int(15 * scale))
    
    # Title
    title_text = "NOTIFICATION SYSTEME"
    title_surf = title_font.render(title_text, True, color)
    title_rect = title_surf.get_rect(centerx=box_rect.centerx, top=box_rect.top + int(30 * scale))
    screen.blit(title_surf, title_rect)
    
    # Divider
    line_y = title_rect.bottom + int(15 * scale)
    pygame.draw.line(screen, color, 
                    (box_rect.left + int(50 * scale), line_y),
                    (box_rect.right - int(50 * scale), line_y), 
                    int(2 * scale))
    
    # Message
    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(centerx=box_rect.centerx, top=line_y + int(30 * scale))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.time.wait(duration)


def main():
    """
    Main game loop with adaptive resolution using ScreenManager
    """
    print("Starting main function")

    # Use global screen manager
    print("Screen manager created")
    
    # Create screen with adaptive resolution using screen manager
    screen = screen_manager.set_mode('windowed')  # Options: 'windowed', 'fullscreen', 'borderless'
    pygame.display.set_caption("CyberHero - Cybersecurity")
    print("Screen created")
    
    # ===== AUDIO: Background music =====
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(BASE_DIR, "assets", "sounds", "menu_music.mp3")

        print("[AUDIO] Trying to load:", music_path)

        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)

            final_volume = (
                settings_manager.settings.get("master_volume", 70) / 100.0
            ) * (
                settings_manager.settings.get("music_volume", 60) / 100.0
            )


            pygame.mixer.music.set_volume(final_volume)
            pygame.mixer.music.play(-1)

            print("[AUDIO] Menu music started")
        else:
            print("[ERROR] Music file NOT FOUND")
    except Exception as e:
        print(f"[ERROR] Audio failed: {e}")



    # Load icon if exists
    icon_paths = ["assets/icon.png", "icon.png"]
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
                break
            except:
                pass
    
    # Initialize save/load manager
    save_manager = SaveLoadManager()
    print("Save manager initialized")
    
    # Initialize mission manager
    mission_manager = MissionManager(save_manager)
    print("Mission manager initialized")
    
    current_screen = "menu"
    print("Entering main loop")
    
    # Main loop
    while True:
        print(f"Current screen: {current_screen}")
        
        if current_screen == "menu":
            print("Creating MainMenu")
            menu = MainMenu(screen)
            print("Running MainMenu")
            choice = menu.run()
            print(f"Menu choice: {choice}")
            
            if choice == "new_game":
                # ===== Step 1: Play intro animation =====
                animation_path = os.path.join("assets", "ui", "start_animation.mp4")
                animation_completed = play_video_animation(screen, animation_path)

                if not animation_completed:
                    continue

                # Fade transition from animation
                screen_width = screen.get_width()
                screen_height = screen.get_height()
                for alpha in range(255, 0, -15):
                    s = pygame.Surface((screen_width, screen_height))
                    s.set_alpha(alpha)
                    s.fill(BLACK)
                    screen.blit(s, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(20)

                # ===== Step 1.5: Welcome Message Sequence =====
                welcome = WelcomeSequence(screen)
                welcome_completed = welcome.run()

                if not welcome_completed:
                    # User interrupted (ESC or closed window)
                    continue

                # ===== Step 2: Create temporary profile (forum comes later) =====
                # Initialize with basic profile for desktop
                temp_profile_data = {
                    'nickname': 'Nouveau Joueur',  # Will be updated after forum registration
                    'email': '',
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

                # ===== Main Desktop Loop (with back navigation) =====
                # Navigation stack: desktop -> apps (including Navigator/Forum)
                skip_deepweb = False
                show_tutorial = True  # Show tutorial popup on first desktop visit
                forum_registered = False  # Track if player has registered on forum
                current_screen = "desktop"  # Start at DESKTOP (not inbox!)

                # Email timer system (for delayed Le Professeur email)
                email_timer_start = None
                professor_email_sent = False

                # Mission tracking (for persistent mission state)
                current_mission = None
                current_mission_network = None

                while True:
                    if current_screen == "inbox":
                        # ===== Inbox Screen =====
                        inbox = Inbox(screen, temp_profile_data)
                        inbox_result, mission_id = inbox.run()

                        if inbox_result == "exit":
                            pygame.quit()
                            sys.exit(0)
                        elif inbox_result == "desktop":
                            current_screen = "desktop"
                        elif inbox_result == "launch_mission":
                            # Launch the selected mission
                            if mission_id == "mission1":
                                from src.missions.mission1_network_recon import Mission1NetworkRecon

                                # Create mission instance (generates network internally)
                                mission1 = Mission1NetworkRecon(temp_profile_data)

                                # Store mission and network for persistent access
                                current_mission = mission1
                                current_mission_network = mission1.network_config

                                # Launch terminal with mission and its network config
                                terminal = TerminalApp(screen, temp_profile_data, mission1.network_config, mission1)
                                terminal_result = terminal.run()

                                # Check if mission is complete
                                if mission1.is_mission_complete():
                                    # Award rewards
                                    rewards = mission1.award_completion_rewards()
                                    temp_profile_data = mission1.profile_data

                                    # Save profile with mission completion
                                    save_manager.save_profile(temp_profile_data)

                                    # Clear mission (completed)
                                    current_mission = None
                                    current_mission_network = None

                                    # Show completion screen
                                    from src.ui.mission_complete_screen import MissionCompleteScreen
                                    complete_screen = MissionCompleteScreen(screen, "Mission 1: Reconnaissance Reseau", rewards)
                                    complete_screen.run()

                                    # Add notification for Mission 2 email
                                    from src.systems.notification_manager import get_notification_manager
                                    notification_manager = get_notification_manager()
                                    notification_manager.add_notification("email_002")

                                # Return to desktop or inbox based on terminal result
                                if terminal_result == "desktop":
                                    current_screen = "desktop"
                                else:
                                    current_screen = "inbox"
                            else:
                                # Other missions not implemented yet
                                current_screen = "desktop"

                    elif current_screen == "desktop":
                        # ===== Desktop Screen =====
                        desktop = InteractiveDesktop(screen, temp_profile_data)

                        # Check email timer (deliver Le Professeur email after 5 seconds)
                        if email_timer_start and not professor_email_sent:
                            elapsed_seconds = (pygame.time.get_ticks() - email_timer_start) / 1000.0
                            if elapsed_seconds >= 5.0:
                                # Trigger email notification
                                from src.systems.notification_manager import get_notification_manager
                                notification_manager = get_notification_manager()
                                notification_manager.add_notification("prof_001_welcome")
                                professor_email_sent = True

                        # Auto-start Mission 1 if player has registered and mission not started yet
                        if (current_mission is None and
                            temp_profile_data.get('nickname') != 'Nouveau Joueur' and
                            'mission1' not in temp_profile_data.get('progress', {}).get('missions_completed', []) and
                            not temp_profile_data.get('progress', {}).get('mission1_completed', False)):
                            # Create Mission 1 instance
                            from src.missions.mission1_network_recon import Mission1NetworkRecon
                            current_mission = Mission1NetworkRecon(temp_profile_data)
                            current_mission_network = current_mission.network_config

                        # Show tutorial popup on first visit (after desktop draws once)
                        if show_tutorial:
                            from src.ui.tutorial_popup import show_tutorial_popup
                            # Desktop draws once so we can blur it
                            tutorial_result = show_tutorial_popup(screen, "navigator", desktop)

                            if tutorial_result == "exit":
                                pygame.quit()
                                sys.exit(0)

                            show_tutorial = False  # Don't show again

                        desktop_result, action = desktop.run()

                        if desktop_result == "exit":
                            pygame.quit()
                            sys.exit(0)
                        elif desktop_result == "restart":
                            # User confirmed return to main menu - save and restart
                            save_manager.save_profile(temp_profile_data)
                            current_screen = "main_menu"
                            temp_profile_data = None
                            current_mission = None
                            current_mission_network = None
                            professor_email_sent = False
                            email_timer_start = None
                            continue
                        elif desktop_result == "inbox":
                            # ESC pressed - go back to inbox
                            current_screen = "inbox"
                            continue
                        elif desktop_result == "action":
                            # Handle different desktop actions (9 core apps)
                            if action == "terminal":
                                # Terminal - Command line interface
                                # Pass mission if one is active
                                terminal = TerminalApp(screen, temp_profile_data, current_mission_network, current_mission)
                                terminal_result = terminal.run()

                                # Check if Mission 1 completed
                                if terminal_result == "mission_complete" and current_mission:
                                    # Award rewards
                                    rewards = current_mission.award_completion_rewards()
                                    temp_profile_data = current_mission.profile_data

                                    # Save profile with mission completion
                                    save_manager.save_profile(temp_profile_data)

                                    # Clear mission (completed)
                                    current_mission = None
                                    current_mission_network = None

                                    # Show completion screen
                                    from src.ui.mission_complete_screen import MissionCompleteScreen
                                    complete_screen = MissionCompleteScreen(screen, "Mission 1: Reconnaissance Reseau", rewards)
                                    complete_screen.run()

                                    # Add notification for Mission 2 email
                                    from src.systems.notification_manager import get_notification_manager
                                    notification_manager = get_notification_manager()
                                    notification_manager.add_notification("email_002")

                                if terminal_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                elif terminal_result == "desktop":
                                    continue

                            elif action == "net_scanner":
                                # Net Scanner - Tools directory for downloaded tools
                                from src.apps.net_scanner_app import NetScannerApp
                                net_scanner = NetScannerApp(screen, temp_profile_data)
                                scanner_result, tool_id = net_scanner.run()

                                if scanner_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                elif scanner_result == "launch_tool":
                                    # Launch the selected tool
                                    if tool_id == "wireshark":
                                        from src.apps.wireshark_app import WiresharkApp

                                        # Check if Mission 2 should be active
                                        mission2 = None
                                        progress = temp_profile_data.get('progress', {})
                                        mission1_complete = ('mission1' in progress.get('missions_completed', []) or
                                                           progress.get('mission1_completed', False))

                                        if mission1_complete and 'mission2' not in progress.get('missions_completed', []):
                                            # Mission 2 active - pass to Wireshark
                                            from src.missions.mission2_packet_analysis import Mission2PacketAnalysis
                                            mission2 = Mission2PacketAnalysis(temp_profile_data)

                                        wireshark = WiresharkApp(screen, temp_profile_data, mission2)
                                        wireshark_result = wireshark.run()

                                        # Check if Mission 2 completed (via notes popup)
                                        if wireshark_result == "mission_complete" and mission2:
                                            rewards = mission2.award_completion_rewards()
                                            temp_profile_data = mission2.profile_data

                                            # Save profile
                                            save_manager.save_profile(temp_profile_data)

                                            # Show completion screen
                                            from src.ui.mission_complete_screen import MissionCompleteScreen
                                            complete_screen = MissionCompleteScreen(screen, "Mission 2: Analyse de Paquets", rewards)
                                            complete_screen.run()

                                            # Add notification for Mission 3 email
                                            from src.systems.notification_manager import get_notification_manager
                                            notification_manager = get_notification_manager()
                                            notification_manager.add_notification("email_003")

                                        if wireshark_result == "exit":
                                            pygame.quit()
                                            sys.exit(0)

                                    elif tool_id == "pcap_analyzer":
                                        from src.apps.pcap_analyzer_app import PcapAnalyzerApp

                                        # Check if Mission 3 should be active
                                        mission3 = None
                                        progress = temp_profile_data.get('progress', {})
                                        mission2_complete = 'mission2' in progress.get('missions_completed', [])

                                        if mission2_complete and 'mission3' not in progress.get('missions_completed', []):
                                            from src.missions.mission3_pcap_analysis import Mission3PcapAnalysis
                                            mission3 = Mission3PcapAnalysis(temp_profile_data)

                                        pcap_app = PcapAnalyzerApp(screen, temp_profile_data, mission3)
                                        pcap_result = pcap_app.run()

                                        # Check if Mission 3 completed
                                        if pcap_result == "mission_complete" and mission3:
                                            rewards = mission3.award_completion_rewards()
                                            temp_profile_data = mission3.profile_data

                                            save_manager.save_profile(temp_profile_data)

                                            from src.ui.mission_complete_screen import MissionCompleteScreen
                                            complete_screen = MissionCompleteScreen(screen, "Mission 3: Analyse PCAP", rewards)
                                            complete_screen.run()

                                        if pcap_result == "exit":
                                            pygame.quit()
                                            sys.exit(0)

                                    else:
                                        show_message(screen, f"{tool_id} - En cours de developpement", YELLOW, 2000)
                                continue

                            elif action == "packet_lab":
                                # Packet Lab - Tools directory for PCAP file analysis
                                from src.apps.packet_lab_app import PacketLabApp
                                packet_lab = PacketLabApp(screen, temp_profile_data)
                                lab_result, tool_id = packet_lab.run()

                                if lab_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                elif lab_result == "launch_tool":
                                    # Launch the selected packet analysis tool
                                    if tool_id == "pcap_analyzer":
                                        from src.apps.pcap_analyzer_app import PcapAnalyzerApp

                                        # Check if Mission 3 should be active
                                        mission3 = None
                                        progress = temp_profile_data.get('progress', {})
                                        mission2_complete = 'mission2' in progress.get('missions_completed', [])

                                        if mission2_complete and 'mission3' not in progress.get('missions_completed', []):
                                            from src.missions.mission3_pcap_analysis import Mission3PcapAnalysis
                                            mission3 = Mission3PcapAnalysis(temp_profile_data)

                                        pcap_app = PcapAnalyzerApp(screen, temp_profile_data, mission3)
                                        pcap_result = pcap_app.run()

                                        # Check if Mission 3 completed
                                        if pcap_result == "mission_complete" and mission3:
                                            rewards = mission3.award_completion_rewards()
                                            temp_profile_data = mission3.profile_data

                                            save_manager.save_profile(temp_profile_data)

                                            from src.ui.mission_complete_screen import MissionCompleteScreen
                                            complete_screen = MissionCompleteScreen(screen, "Mission 3: Analyse PCAP", rewards)
                                            complete_screen.run()

                                        if pcap_result == "exit":
                                            pygame.quit()
                                            sys.exit(0)

                                    else:
                                        show_message(screen, f"{tool_id} - En cours de developpement", YELLOW, 2000)
                                continue

                            elif action == "browser":
                                # Browser - Mission sites/docs + forum access

                                # Show deep web loading screen (only first time)
                                if not skip_deepweb:
                                    from src.ui.deepweb_loading import show_deepweb_loading
                                    loading_result = show_deepweb_loading(screen)

                                    if loading_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)

                                    skip_deepweb = True  # Don't show loading again

                                # Open forum browser (pass session login state)
                                forum = ForumBrowser(screen, temp_profile_data, forum_registered)
                                forum_result, profile_data = forum.run()

                                if forum_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                elif forum_result == "back":
                                    # User pressed ESC, return to desktop
                                    # Update profile if it was modified
                                    if profile_data:
                                        temp_profile_data.update(profile_data)
                                    continue
                                elif forum_result == "open_inbox":
                                    # User clicked EMAIL button in forum, open inbox
                                    # Update profile if it was modified
                                    if profile_data:
                                        temp_profile_data.update(profile_data)
                                    current_screen = "inbox"
                                    continue
                                elif forum_result == "create_account" and profile_data:
                                    # User registered! Update profile and stay on desktop
                                    temp_profile_data = profile_data
                                    forum_registered = True

                                    # Save the profile
                                    success, message = save_manager.save_profile(temp_profile_data)
                                    if success:
                                        print(f"[INFO] Profile saved: {message}")
                                    else:
                                        print(f"[ERROR] Failed to save profile: {message}")

                                    # Start email timer (Le Professeur email in 5 seconds)
                                    email_timer_start = pygame.time.get_ticks()

                                    show_message(screen, "✓ Compte cree! Verifiez votre boite de reception.", GREEN, 2000)
                                    continue

                            elif action == "firewall":
                                # Firewall Config - Build allow/deny rules
                                from src.apps.empty_app import EmptyApp
                                firewall_app = EmptyApp(screen, temp_profile_data, "Firewall", "Configuration des regles de securite")
                                firewall_result = firewall_app.run()
                                if firewall_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                continue

                            elif action == "logs":
                                # Logs Viewer - System/network logs
                                from src.apps.empty_app import EmptyApp
                                logs_app = EmptyApp(screen, temp_profile_data, "Logs", "Journaux systeme et reseau")
                                logs_result = logs_app.run()
                                if logs_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                continue

                            elif action == "notes":
                                # Notes - Save clues manually
                                from src.apps.empty_app import EmptyApp
                                notes_app = EmptyApp(screen, temp_profile_data, "Notes", "Bloc-notes pour indices")
                                notes_result = notes_app.run()
                                if notes_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                continue

                            elif action == "devices":
                                # Device Trust List - Approve/flag devices
                                from src.apps.empty_app import EmptyApp
                                devices_app = EmptyApp(screen, temp_profile_data, "Peripheriques", "Liste des appareils du reseau")
                                devices_result = devices_app.run()
                                if devices_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                continue

                            elif action == "career":
                                # Career Dashboard - XP, badges, reputation
                                from src.apps.empty_app import EmptyApp
                                career_app = EmptyApp(screen, temp_profile_data, "Carriere", "Dashboard XP, badges et reputation")
                                career_result = career_app.run()
                                if career_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                continue

                            elif action == "settings":
                                # Settings - Open settings UI
                                settings_ui = SettingsUI(screen)
                                settings_result = settings_ui.run()

                                if settings_result == "exit":
                                    pygame.quit()
                                    sys.exit(0)
                                elif settings_result == "back":
                                    # Apply settings changes and recreate screen if needed
                                    new_screen = screen_manager.apply_settings()
                                    if new_screen:
                                        screen = new_screen
                                    # Return to desktop (will reinitialize with new screen size)
                                    continue

                            else:
                                # Unknown action, return to desktop
                                continue

                    # If we handled all actions, loop back to desktop
                    # This should never be reached as all actions either continue or change screen
                    continue

                    # ===== OLD CODE BELOW - DEAD CODE - SHOULD NEVER EXECUTE =====
                    # If execution reaches here, there's a logic error above
                    print("[CRITICAL ERROR] Reached dead code section - this should never happen!")
                    print(f"Current screen: {current_screen}, Action: {action if 'action' in locals() else 'None'}")
                    current_screen = "menu"
                    continue

                # ===== DEAD CODE - OLD PROFILE CREATION SYSTEM =====
                # This entire section is no longer used. Kept for reference only.
                # New flow: Desktop -> Navigator -> Forum Registration (built into ForumBrowser)

                """
                # ===== Step 3: Deep Web Browser (OLD - UNUSED) =====
                if not skip_deepweb:
                    try:
                        deepweb = DeepWebBrowser(screen)
                        deepweb_result = deepweb.run()

                        if deepweb_result == "exit":
                            pygame.quit()
                            sys.exit(0)
                        elif deepweb_result == "desktop":
                            continue
                        elif deepweb_result != "profile_creation":
                            continue
                    except ImportError as e:
                        print(f"[WARNING] Could not import DeepWebBrowser: {e}")
                        show_message(screen, "Browser module not available", RED)
                        continue

                # ===== Step 4: Profile Creation (OLD - UNUSED) =====
                try:
                    view = ProfileCreationUI(screen, save_manager)
                    result, player_profile = view.run()
                    
                    if player_profile:
                        # Profile data is already a dictionary, no need to call get_profile_data()
                        profile_data = player_profile
                        success, message = save_manager.save_profile(profile_data)
                        
                        # Show success message
                        screen_width = screen.get_width()
                        screen_height = screen.get_height()
                        scale = min(screen_width / 1920, screen_height / 1080)
                        font = pygame.font.Font(None, int(48 * scale))
                        small_font = pygame.font.Font(None, int(32 * scale))
                        screen.fill(BLACK)
                        text1 = font.render("Profile created successfully!", True, GREEN)
                        text2 = small_font.render("Loading mission terminal...", True, CYAN)
                        screen.blit(text1, (screen_width // 2 - text1.get_width() // 2, screen_height // 2 - 40))
                        screen.blit(text2, (screen_width // 2 - text2.get_width() // 2, screen_height // 2 + 20))
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        
                        # ===== Step 5: Mission Hub =====
                        hub_result = run_mission_hub(screen, profile_data, mission_manager)
                        
                        if hub_result == "exit":
                            pygame.quit()
                            sys.exit(0)
                        else:
                            continue
                    else:
                        # Profile creation was cancelled
                        show_message(screen, "Profile creation cancelled", YELLOW)

                except Exception as e:
                    show_message(screen, "Error occurred!", RED)
                    import traceback
                    traceback.print_exc()
                """
                # ===== END OF OLD DEAD CODE =====

            elif choice == "load_game":
                # Show load game UI
                load_ui = LoadGameUI(screen, save_manager)
                result, loaded_profile = load_ui.run()

                if result == "exit":
                    pygame.quit()
                    sys.exit(0)
                elif result == "load" and loaded_profile:
                    # Profile loaded successfully
                    print(f"[Main] Loaded profile: {loaded_profile.get('nickname')}")

                    # Show welcome back message
                    screen_width = screen.get_width()
                    screen_height = screen.get_height()
                    scale = min(screen_width / 1920, screen_height / 1080)
                    font = pygame.font.Font(None, int(48 * scale))
                    small_font = pygame.font.Font(None, int(32 * scale))
                    screen.fill(BLACK)

                    nickname = loaded_profile.get('nickname', 'Unknown')
                    level = loaded_profile.get('progress', {}).get('level', 'Debutant')

                    text1 = font.render(f"Bon retour, {nickname}!", True, GREEN)
                    text2 = small_font.render(f"Niveau {level} - Chargement du bureau...", True, CYAN)

                    screen.blit(text1, (screen_width // 2 - text1.get_width() // 2, screen_height // 2 - 40))
                    screen.blit(text2, (screen_width // 2 - text2.get_width() // 2, screen_height // 2 + 20))
                    pygame.display.flip()
                    pygame.time.wait(2000)

                    # Use loaded profile as temp_profile_data
                    temp_profile_data = loaded_profile

                    # Initialize desktop loop variables
                    skip_deepweb = True  # Skip deepweb loading since they've already seen it
                    show_tutorial = False  # Don't show tutorial again for loaded games
                    forum_registered = True  # Already registered

                    # Email timer system (disabled for loaded games)
                    email_timer_start = None
                    professor_email_sent = True  # Already received

                    # Mission tracking
                    current_mission = None
                    current_mission_network = None

                    # Auto-start Mission 1 if not completed yet
                    progress = temp_profile_data.get('progress', {})
                    if ('mission1' not in progress.get('missions_completed', []) and
                        not progress.get('mission1_completed', False)):
                        from src.missions.mission1_network_recon import Mission1NetworkRecon
                        current_mission = Mission1NetworkRecon(temp_profile_data)
                        current_mission_network = current_mission.network_config

                    # Start the desktop loop
                    current_screen = "desktop"

                    # Desktop loop - same as new game
                    while True:
                        if current_screen == "inbox":
                            # ===== Inbox Screen =====
                            inbox = Inbox(screen, temp_profile_data)
                            inbox_result, mission_id = inbox.run()

                            if inbox_result == "exit":
                                pygame.quit()
                                sys.exit(0)
                            elif inbox_result == "desktop":
                                current_screen = "desktop"
                            elif inbox_result == "launch_mission":
                                # Old mission launch code - no longer used
                                # Just return to desktop
                                current_screen = "desktop"

                        elif current_screen == "desktop":
                            # ===== Desktop Screen =====
                            desktop = InteractiveDesktop(screen, temp_profile_data)

                            # Auto-start Mission 1 if player has registered and mission not started yet
                            if (current_mission is None and
                                temp_profile_data.get('nickname') != 'Nouveau Joueur' and
                                'mission1' not in temp_profile_data.get('progress', {}).get('missions_completed', []) and
                                not temp_profile_data.get('progress', {}).get('mission1_completed', False)):
                                # Create Mission 1 instance
                                from src.missions.mission1_network_recon import Mission1NetworkRecon
                                current_mission = Mission1NetworkRecon(temp_profile_data)
                                current_mission_network = current_mission.network_config

                            desktop_result, action = desktop.run()

                            if desktop_result == "exit":
                                pygame.quit()
                                sys.exit(0)
                            elif desktop_result == "restart":
                                # User confirmed return to main menu - save and restart
                                save_manager.save_profile(temp_profile_data)
                                current_screen = "main_menu"
                                temp_profile_data = None
                                current_mission = None
                                current_mission_network = None
                                professor_email_sent = False
                                email_timer_start = None
                                continue
                            elif desktop_result == "inbox":
                                # ESC pressed - go back to inbox
                                current_screen = "inbox"
                                continue
                            elif desktop_result == "action":
                                # Handle different desktop actions
                                if action == "terminal":
                                    # Terminal - Command line interface
                                    # Pass mission if one is active
                                    terminal = TerminalApp(screen, temp_profile_data, current_mission_network, current_mission)
                                    terminal_result = terminal.run()

                                    # Check if Mission 1 completed
                                    if terminal_result == "mission_complete" and current_mission:
                                        # Award rewards
                                        rewards = current_mission.award_completion_rewards()
                                        temp_profile_data = current_mission.profile_data

                                        # Save profile with mission completion
                                        save_manager.save_profile(temp_profile_data)

                                        # Clear mission (completed)
                                        current_mission = None
                                        current_mission_network = None

                                        # Show completion screen
                                        from src.ui.mission_complete_screen import MissionCompleteScreen
                                        complete_screen = MissionCompleteScreen(screen, "Mission 1: Reconnaissance Reseau", rewards)
                                        complete_screen.run()

                                        # Add notification for Mission 2 email
                                        from src.systems.notification_manager import get_notification_manager
                                        notification_manager = get_notification_manager()
                                        notification_manager.add_notification("email_002")

                                    if terminal_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    elif terminal_result == "desktop":
                                        continue

                                elif action == "net_scanner":
                                    # Net Scanner - Tools directory for downloaded tools (includes Wireshark)
                                    from src.apps.net_scanner_app import NetScannerApp
                                    net_scanner = NetScannerApp(screen, temp_profile_data)
                                    scanner_result, tool_id = net_scanner.run()

                                    if scanner_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    elif scanner_result == "launch_tool":
                                        # Launch the selected tool
                                        if tool_id == "wireshark":
                                            from src.apps.wireshark_app import WiresharkApp

                                            # Check if Mission 2 should be active
                                            mission2 = None
                                            progress = temp_profile_data.get('progress', {})
                                            mission1_complete = ('mission1' in progress.get('missions_completed', []) or
                                                               progress.get('mission1_completed', False))

                                            if mission1_complete and 'mission2' not in progress.get('missions_completed', []):
                                                # Mission 2 active - pass to Wireshark
                                                from src.missions.mission2_packet_analysis import Mission2PacketAnalysis
                                                mission2 = Mission2PacketAnalysis(temp_profile_data)

                                            wireshark = WiresharkApp(screen, temp_profile_data, mission2)
                                            wireshark_result = wireshark.run()

                                            # Check if Mission 2 completed (via notes popup)
                                            if wireshark_result == "mission_complete" and mission2:
                                                rewards = mission2.award_completion_rewards()
                                                temp_profile_data = mission2.profile_data

                                                # Save profile
                                                save_manager.save_profile(temp_profile_data)

                                                # Show completion screen
                                                from src.ui.mission_complete_screen import MissionCompleteScreen
                                                complete_screen = MissionCompleteScreen(screen, "Mission 2: Analyse de Paquets", rewards)
                                                complete_screen.run()

                                                # Add notification for Mission 3 email
                                                from src.systems.notification_manager import get_notification_manager
                                                notification_manager = get_notification_manager()
                                                notification_manager.add_notification("email_003")

                                            if wireshark_result == "exit":
                                                pygame.quit()
                                                sys.exit(0)

                                        else:
                                            show_message(screen, f"{tool_id} - En cours de developpement", YELLOW, 2000)
                                    continue

                                elif action == "packet_lab":
                                    # Packet Lab - Tools directory for PCAP file analysis
                                    from src.apps.packet_lab_app import PacketLabApp
                                    packet_lab = PacketLabApp(screen, temp_profile_data)
                                    lab_result, tool_id = packet_lab.run()

                                    if lab_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    elif lab_result == "launch_tool":
                                        # Launch the selected packet analysis tool
                                        if tool_id == "pcap_analyzer":
                                            from src.apps.pcap_analyzer_app import PcapAnalyzerApp

                                            # Check if Mission 3 should be active
                                            mission3 = None
                                            progress = temp_profile_data.get('progress', {})
                                            mission2_complete = 'mission2' in progress.get('missions_completed', [])

                                            if mission2_complete and 'mission3' not in progress.get('missions_completed', []):
                                                from src.missions.mission3_pcap_analysis import Mission3PcapAnalysis
                                                mission3 = Mission3PcapAnalysis(temp_profile_data)

                                            pcap_app = PcapAnalyzerApp(screen, temp_profile_data, mission3)
                                            pcap_result = pcap_app.run()

                                            # Check if Mission 3 completed
                                            if pcap_result == "mission_complete" and mission3:
                                                rewards = mission3.award_completion_rewards()
                                                temp_profile_data = mission3.profile_data

                                                save_manager.save_profile(temp_profile_data)

                                                from src.ui.mission_complete_screen import MissionCompleteScreen
                                                complete_screen = MissionCompleteScreen(screen, "Mission 3: Analyse PCAP", rewards)
                                                complete_screen.run()

                                            if pcap_result == "exit":
                                                pygame.quit()
                                                sys.exit(0)

                                        else:
                                            show_message(screen, f"{tool_id} - En cours de developpement", YELLOW, 2000)
                                    continue

                                elif action == "browser":
                                    # Browser - Mission sites/docs + forum access

                                    # Show deep web loading screen (only first time)
                                    if not skip_deepweb:
                                        from src.ui.deepweb_loading import show_deepweb_loading
                                        loading_result = show_deepweb_loading(screen)

                                        if loading_result == "exit":
                                            pygame.quit()
                                            sys.exit(0)

                                        skip_deepweb = True  # Don't show loading again

                                    # Open forum browser (pass session login state)
                                    forum = ForumBrowser(screen, temp_profile_data, forum_registered)
                                    forum_result, profile_data = forum.run()

                                    if forum_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    elif forum_result == "back":
                                        # User pressed ESC, return to desktop
                                        # Update profile if it was modified
                                        if profile_data:
                                            temp_profile_data.update(profile_data)
                                        continue
                                    elif forum_result == "open_inbox":
                                        # User clicked EMAIL button in forum, open inbox
                                        # Update profile if it was modified
                                        if profile_data:
                                            temp_profile_data.update(profile_data)
                                        current_screen = "inbox"
                                        continue
                                    elif forum_result == "create_account" and profile_data:
                                        # User registered! Update profile and stay on desktop
                                        temp_profile_data = profile_data
                                        forum_registered = True

                                        # Save the profile
                                        success, message = save_manager.save_profile(temp_profile_data)
                                        if success:
                                            print(f"[INFO] Profile saved: {message}")
                                        else:
                                            print(f"[ERROR] Failed to save profile: {message}")

                                        show_message(screen, "✓ Compte cree! Verifiez votre boite de reception.", GREEN, 2000)
                                        continue

                                elif action == "firewall":
                                    # Firewall Config
                                    from src.apps.empty_app import EmptyApp
                                    firewall_app = EmptyApp(screen, temp_profile_data, "Firewall", "Configuration des regles de securite")
                                    firewall_result = firewall_app.run()
                                    if firewall_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    continue

                                elif action == "logs":
                                    # Logs Viewer
                                    from src.apps.empty_app import EmptyApp
                                    logs_app = EmptyApp(screen, temp_profile_data, "Logs", "Journaux systeme et reseau")
                                    logs_result = logs_app.run()
                                    if logs_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    continue

                                elif action == "notes":
                                    # Notes
                                    from src.apps.empty_app import EmptyApp
                                    notes_app = EmptyApp(screen, temp_profile_data, "Notes", "Bloc-notes pour indices")
                                    notes_result = notes_app.run()
                                    if notes_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    continue

                                elif action == "devices":
                                    # Peripheriques
                                    from src.apps.empty_app import EmptyApp
                                    devices_app = EmptyApp(screen, temp_profile_data, "Peripheriques", "Liste des appareils du reseau")
                                    devices_result = devices_app.run()
                                    if devices_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    continue

                                elif action == "career":
                                    # Carriere
                                    from src.apps.empty_app import EmptyApp
                                    career_app = EmptyApp(screen, temp_profile_data, "Carriere", "Dashboard XP, badges et reputation")
                                    career_result = career_app.run()
                                    if career_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    continue

                                elif action == "settings":
                                    # Settings - Open settings UI
                                    settings_ui = SettingsUI(screen)
                                    settings_result = settings_ui.run()

                                    if settings_result == "exit":
                                        pygame.quit()
                                        sys.exit(0)
                                    elif settings_result == "back":
                                        # Apply settings changes and recreate screen if needed
                                        new_screen = screen_manager.apply_settings()
                                        if new_screen:
                                            screen = new_screen
                                        # Return to desktop (will reinitialize with new screen size)
                                        continue

                                else:
                                    # Other apps not implemented yet
                                    from src.apps.empty_app import EmptyApp
                                    unknown_app = EmptyApp(screen, temp_profile_data, "Application", "Fonctionnalite en developpement")
                                    unknown_app.run()
                                    continue

                        # If we break from inner loop, return to menu
                        else:
                            break

                    # After desktop loop ends, return to menu
                    current_screen = "menu"
                    continue
                else:
                    # User went back to menu
                    continue
                
            elif choice == "settings":
                try:
                    settings_ui = SettingsUI(screen)
                    result = settings_ui.run()
                    if result == "menu":
                        continue
                    elif result == "exit":
                        pygame.quit()
                        sys.exit(0)
                except Exception as e:
                    print(f"[ERROR] Settings UI failed: {e}")
                    import traceback
                    traceback.print_exc()
                    show_message(screen, "Settings UI error", RED)
                
            elif choice == "credits":
                current_screen = "credits"
                
            elif choice == "exit":
                pygame.quit()
                sys.exit(0)
                
        elif current_screen == "credits":
            credits = CreditsScreen(screen)
            result = credits.run()
            
            if result == "menu":
                current_screen = "menu"
            elif result == "exit":
                pygame.quit()
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to show error in a simple window
        try:
            pygame.init()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            error_screen = pygame.display.set_mode((800, 400))
            pygame.display.set_caption("CyberHero - Fatal Error")
            

            
            font = pygame.font.Font(None, 36)
            small_font = pygame.font.Font(None, 24)
            
            error_screen.fill((20, 0, 0))
            
            title = font.render("FATAL ERROR", True, RED)
            error_text = small_font.render(f"Error: {str(e)}", True, YELLOW)
            instruction = small_font.render("Check console for details. Closing in 10 seconds...", True, WHITE)
            
            error_screen.blit(title, (400 - title.get_width() // 2, 50))
            error_screen.blit(error_text, (400 - error_text.get_width() // 2, 150))
            error_screen.blit(instruction, (400 - instruction.get_width() // 2, 250))
            
            pygame.display.flip()
            pygame.time.wait(10000)
        except:
            pass
        
        pygame.quit()
        sys.exit(1)