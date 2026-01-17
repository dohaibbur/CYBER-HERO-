"""
Inbox System - Cyber Hero Terminal Zero
Mission delivery via mentor emails
"""

import pygame
from typing import Tuple, Optional, Dict, List


class Email:
    """Represents a mission email"""
    def __init__(self, id: str, sender: str, subject: str, body: str,
                 mission_id: str, attachments: List[str] = None, read: bool = False):
        self.id = id
        self.sender = sender
        self.subject = subject
        self.body = body
        self.mission_id = mission_id
        self.attachments = attachments or []
        self.read = read


class Inbox:
    """
    Email inbox app - Mission delivery system
    Opens automatically after login
    """

    def __init__(self, screen, profile_data: Dict):
        """
        Initialize inbox

        Args:
            screen: Pygame screen surface
            profile_data: Player profile with mission progress
        """
        self.screen = screen
        self.profile_data = profile_data
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors - Email client theme
        self.bg_color = (15, 20, 30)
        self.sidebar_bg = (25, 30, 40)
        self.email_item_bg = (30, 35, 45)
        self.email_item_hover = (40, 45, 55)
        self.email_selected = (50, 100, 50)
        self.unread_marker = (0, 255, 65)
        self.text_color = (200, 210, 220)
        self.text_dim = (120, 130, 140)
        self.border_color = (50, 60, 80)

        # Fonts - Standardized sizes (matching desktop)
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

        # Load emails based on progress
        self.emails = self.load_emails()
        self.selected_email_index = 0 if self.emails else None

        # Scroll position for email content
        self.content_scroll = 0
        self.max_scroll = 0  # Will be calculated based on content
        self.scroll_speed = int(30 * self.scale_y)

        # Get notification manager reference
        from src.systems.notification_manager import get_notification_manager
        self.notification_manager = get_notification_manager()

    def load_emails(self) -> List[Email]:
        """
        Load available emails based on mission progress

        Returns:
            List of Email objects
        """
        all_emails = [
            Email(
                id="email_001",
                sender="Le Professeur",
                subject="Mission 1: Reconnaissance Reseau",
                body="""Bienvenue dans le programme, recrue.

N'oublie pas de personnaliser ton profil sur le forum.

Voici les etapes a suivre pour ta premiere mission :
1. Retourne sur ton bureau.
2. Ouvre le TERMINAL.
3. Execute les commandes pour explorer le reseau. Tape 'help' pour apprendre les commandes disponibles.
4. Tu verras un bouton 'RAPPORT'. Clique dessus pour voir les champs ou tu devras entrer les informations demandees.
5. Une fois que tu as rempli toutes les informations, clique sur ENVOYER.

Elles arriveront dans ma boite de reception. J'attends. Bonne chance.

- Le Professeur""",
                mission_id="mission1",
                attachments=["network_diagram.txt"],
                read=False
            ),
            Email(
                id="email_002",
                sender="Le Professeur",
                subject="Mission 2: Analyse de Paquets et Detection d'Intrusion",
                body="""Excellent travail sur la Mission 1, recrue.

Un intrus s'est infiltre dans notre reseau. J'ai besoin que tu analyses le trafic capture pour l'identifier.

Voici les etapes a suivre :
1. Va sur le Navigateur, onglet Market, et telecharge 'Wireshark'.
2. Retourne sur le bureau et ouvre l'application 'Net Scanner'.
3. Lance l'outil Wireshark.
4. Analyse le trafic pour trouver l'intrus.
5. Clique sur le bouton 'RAPPORT' pour voir les champs a remplir.
6. Entre les informations demandees et clique sur ENVOYER.

J'attends ton rapport. Bonne chance.

- Le Professeur""",
                mission_id="mission2",
                attachments=["capture_reseau.pcap"],
                read=False
            ),
            Email(
                id="email_003",
                sender="Le Professeur",
                subject="Mission 3: Analyse de Fichier PCAP",
                body="""Tu progresses bien, recrue.

Cette fois, on passe a l'analyse forensique d'un fichier PCAP brut.

Voici les etapes a suivre :
1. Va sur le Navigateur, onglet Market, et telecharge 'PCAP Analyzer'.
2. Retourne sur le bureau et ouvre l'application 'Packet Lab'.
3. Lance l'outil PCAP Analyzer.
4. Analyse le dump hexadecimal.
5. Clique sur le bouton 'RAPPORT' pour voir les informations a extraire.
6. Remplis le formulaire et clique sur ENVOYER.

C'est le moment de prouver ta valeur. Bonne chance.

- Le Professeur""",
                mission_id="mission3",
                attachments=["suspicious_packet.pcap"],
                read=False
            )
        ]

        # Filter emails based on completed missions
        progress = self.profile_data.get('progress', {})
        completed = progress.get('missions_completed', [])
        available_emails = []

        # Add Le Professeur's welcome email if player has forum account
        player_name = self.profile_data.get('nickname', 'Recrue')
        if player_name != 'Nouveau Joueur':  # Player has registered on forum
            from src.data.professor_emails import get_welcome_email
            welcome_data = get_welcome_email(player_name)

            # Convert to Email object
            welcome_email = Email(
                id=welcome_data["id"],
                sender=welcome_data["sender"],
                subject=welcome_data["subject"],
                body=welcome_data["body"],
                mission_id=welcome_data["mission_id"],
                attachments=welcome_data["attachments"],
                read=welcome_data["read"]
            )
            available_emails.append(welcome_email)

        # Add Mission 1 success email if Mission 1 is complete
        print(f"[DEBUG INBOX] Checking mission1_completed: completed={completed}, mission1_completed={progress.get('mission1_completed', False)}")
        if 'mission1' in completed or progress.get('mission1_completed', False):
            from src.data.professor_emails import get_mission1_success_email
            success_data = get_mission1_success_email(player_name)

            # Check if we haven't already shown this email
            # (to avoid duplicates if it was added during mission completion)
            if not any(email.id == success_data["id"] for email in available_emails):
                success_email = Email(
                    id=success_data["id"],
                    sender=success_data["sender"],
                    subject=success_data["subject"],
                    body=success_data["body"],
                    mission_id=success_data["mission_id"],
                    attachments=success_data["attachments"],
                    read=success_data["read"]
                )
                available_emails.append(success_email)

        # Add Mission 2 email if Mission 1 is complete
        if 'mission1' in completed or progress.get('mission1_completed', False):
            from src.data.professor_emails import get_mission2_email
            mission2_data = get_mission2_email(player_name)

            # Check if we haven't already shown this email
            if not any(email.id == mission2_data["id"] for email in available_emails):
                mission2_email = Email(
                    id=mission2_data["id"],
                    sender=mission2_data["sender"],
                    subject=mission2_data["subject"],
                    body=mission2_data["body"],
                    mission_id=mission2_data["mission_id"],
                    attachments=mission2_data["attachments"],
                    read=mission2_data["read"]
                )
                available_emails.append(mission2_email)

        # OLD: Show Mission 2 if Mission 1 is complete (from old all_emails array)
        # if 'mission1' in completed:
        #     available_emails.append(all_emails[1])

        # Show Mission 3 if Mission 2 is complete
        if 'mission2' in completed:
            available_emails.append(all_emails[2])

        return available_emails

    def draw_sidebar(self, mouse_pos: Tuple[int, int]) -> List[pygame.Rect]:
        """
        Draw email list sidebar

        Args:
            mouse_pos: Current mouse position

        Returns:
            List of email item rects for click detection
        """
        sidebar_width = int(400 * self.scale_x)

        # Sidebar background
        sidebar_rect = pygame.Rect(0, 0, sidebar_width, self.screen_height)
        pygame.draw.rect(self.screen, self.sidebar_bg, sidebar_rect)

        # Header
        header_height = int(60 * self.scale_y)
        pygame.draw.rect(self.screen, self.bg_color, (0, 0, sidebar_width, header_height))

        inbox_title = self.title_font.render("INBOX", True, self.unread_marker)
        self.screen.blit(inbox_title, (int(20 * self.scale_x), int(15 * self.scale_y)))

        # Email count
        unread_count = sum(1 for email in self.emails if not email.read)
        count_text = self.small_font.render(f"{len(self.emails)} messages | {unread_count} non lus",
                                           True, self.text_dim)
        self.screen.blit(count_text, (int(20 * self.scale_x), int(45 * self.scale_y)))

        # Email items
        email_rects = []
        item_height = int(100 * self.scale_y)
        y_offset = header_height + int(10 * self.scale_y)

        for i, email in enumerate(self.emails):
            item_rect = pygame.Rect(int(10 * self.scale_x), y_offset,
                                   sidebar_width - int(20 * self.scale_x), item_height)

            # Background color (hover/selected)
            is_hovered = item_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_email_index)

            if is_selected:
                bg_color = self.email_selected
            elif is_hovered:
                bg_color = self.email_item_hover
            else:
                bg_color = self.email_item_bg

            pygame.draw.rect(self.screen, bg_color, item_rect, border_radius=int(5 * self.scale))

            # Unread marker
            if not email.read:
                marker_rect = pygame.Rect(item_rect.x + int(10 * self.scale_x),
                                         item_rect.y + int(10 * self.scale_y),
                                         int(8 * self.scale), int(8 * self.scale))
                pygame.draw.circle(self.screen, self.unread_marker, marker_rect.center, int(4 * self.scale))

            # Sender
            sender_text = self.heading_font.render(email.sender, True, self.text_color)
            self.screen.blit(sender_text, (item_rect.x + int(25 * self.scale_x),
                                          item_rect.y + int(10 * self.scale_y)))

            # Subject
            subject_text = self.body_font.render(email.subject[:40] + ("..." if len(email.subject) > 40 else ""),
                                                 True, self.text_color)
            self.screen.blit(subject_text, (item_rect.x + int(25 * self.scale_x),
                                           item_rect.y + int(40 * self.scale_y)))

            # Attachments indicator
            if email.attachments:
                attach_text = self.small_font.render(f"[+] {len(email.attachments)} fichier(s)",
                                                     True, self.text_dim)
                self.screen.blit(attach_text, (item_rect.x + int(25 * self.scale_x),
                                              item_rect.y + int(70 * self.scale_y)))

            email_rects.append(item_rect)
            y_offset += item_height + int(10 * self.scale_y)

        return email_rects

    def draw_content(self, mouse_pos):
        """Draw selected email content with scroll bar"""
        if self.selected_email_index is None or not self.emails:
            return

        email = self.emails[self.selected_email_index]

        # Content area starts after sidebar
        content_x = int(410 * self.scale_x)
        scrollbar_width = int(12 * self.scale_x)
        content_width = self.screen_width - content_x - int(30 * self.scale_x) - scrollbar_width

        # Header (fixed, not scrollable)
        header_y = int(20 * self.scale_y)

        subject_text = self.title_font.render(email.subject, True, self.text_color)
        self.screen.blit(subject_text, (content_x, header_y))

        from_text = self.body_font.render(f"De: {email.sender}", True, self.text_dim)
        self.screen.blit(from_text, (content_x, header_y + int(45 * self.scale_y)))

        # Divider
        divider_y = header_y + int(80 * self.scale_y)
        pygame.draw.line(self.screen, self.border_color,
                        (content_x, divider_y),
                        (content_x + content_width + scrollbar_width + int(10 * self.scale_x), divider_y), 2)

        # Scrollable content area
        body_start_y = divider_y + int(20 * self.scale_y)
        visible_height = self.screen_height - body_start_y - int(60 * self.scale_y)
        line_height = int(28 * self.scale_y)

        # Calculate total content height
        lines = email.body.split('\n')
        total_content_height = len(lines) * line_height

        # Add height for attachments
        if email.attachments:
            total_content_height += int(70 * self.scale_y) + (len(email.attachments) * int(30 * self.scale_y))

        # Calculate max scroll
        self.max_scroll = max(0, total_content_height - visible_height + int(50 * self.scale_y))

        # Clamp scroll position
        self.content_scroll = max(0, min(self.content_scroll, self.max_scroll))

        # Create clipping rect for scrollable area
        clip_rect = pygame.Rect(content_x, body_start_y, content_width + int(10 * self.scale_x), visible_height)
        self.screen.set_clip(clip_rect)

        # Draw body text
        for i, line in enumerate(lines):
            line_y = body_start_y + (i * line_height) - self.content_scroll
            if body_start_y - line_height < line_y < body_start_y + visible_height:
                if line.strip():
                    line_text = self.body_font.render(line, True, self.text_color)
                    self.screen.blit(line_text, (content_x, line_y))

        # Attachments
        if email.attachments:
            attach_y = body_start_y + (len(lines) * line_height) + int(30 * self.scale_y) - self.content_scroll

            attach_label = self.heading_font.render("FICHIERS JOINTS:", True, self.unread_marker)
            self.screen.blit(attach_label, (content_x, attach_y))

            for i, attachment in enumerate(email.attachments):
                attach_text = self.body_font.render(f"[+] {attachment}", True, self.text_color)
                self.screen.blit(attach_text, (content_x, attach_y + int(35 * self.scale_y) + (i * int(30 * self.scale_y))))

        # Remove clipping
        self.screen.set_clip(None)

        # Draw scroll bar (only if content is scrollable)
        if self.max_scroll > 0:
            scrollbar_x = self.screen_width - int(25 * self.scale_x)
            scrollbar_track_height = visible_height

            # Track background
            track_rect = pygame.Rect(scrollbar_x, body_start_y, scrollbar_width, scrollbar_track_height)
            pygame.draw.rect(self.screen, (40, 45, 55), track_rect, border_radius=int(4 * self.scale))

            # Calculate thumb size and position
            thumb_height = max(int(40 * self.scale_y), int(scrollbar_track_height * (visible_height / total_content_height)))
            scroll_ratio = self.content_scroll / self.max_scroll if self.max_scroll > 0 else 0
            thumb_y = body_start_y + int(scroll_ratio * (scrollbar_track_height - thumb_height))

            # Thumb
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            thumb_color = (0, 255, 65) if thumb_rect.collidepoint(mouse_pos) else (80, 100, 90)
            pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=int(4 * self.scale))

        # Reply button (for Le Professeur's Mission 1 email)
        if email.id == "prof_001_welcome":
            reply_button_y = self.screen_height - int(100 * self.scale_y)
            reply_button_width = int(200 * self.scale_x)
            reply_button_height = int(50 * self.scale_y)
            reply_button_x = content_x + (content_width - reply_button_width) // 2

            self.reply_button_rect = pygame.Rect(reply_button_x, reply_button_y, reply_button_width, reply_button_height)

            # Check if hovered
            is_reply_hovered = self.reply_button_rect.collidepoint(mouse_pos)

            # Button colors
            button_bg = (42, 63, 90) if is_reply_hovered else (26, 31, 58)
            button_border = (0, 255, 255) if is_reply_hovered else (42, 63, 90)

            # Draw button
            pygame.draw.rect(self.screen, button_bg, self.reply_button_rect, border_radius=int(8 * self.scale))
            pygame.draw.rect(self.screen, button_border, self.reply_button_rect, 3, border_radius=int(8 * self.scale))

            # Button text
            reply_text = self.body_font.render("REPONDRE", True, (0, 255, 255) if is_reply_hovered else (200, 200, 200))
            reply_text_rect = reply_text.get_rect(center=self.reply_button_rect.center)
            self.screen.blit(reply_text, reply_text_rect)
        else:
            self.reply_button_rect = None

        # Instructions at bottom
        instructions_y = self.screen_height - int(40 * self.scale_y)
        instructions = self.small_font.render("ENTREE: Lancer Mission | ECHAP: Retour Bureau | FLECHES: Navigation",
                                             True, self.border_color)
        instructions_rect = instructions.get_rect(centerx=(content_x + content_width // 2), top=instructions_y)
        self.screen.blit(instructions, instructions_rect)

    def run(self) -> Tuple[str, Optional[str]]:
        """
        Run the inbox interface

        Returns:
            Tuple of (result, mission_id)
            result: "exit", "desktop", "launch_mission"
            mission_id: Mission to launch (if result is "launch_mission")
        """
        clock = pygame.time.Clock()
        running = True
        email_rects = []

        # Clear notification badge when inbox is opened
        self.notification_manager.clear_notification()

        # Mark first email as read when inbox opens
        if self.emails and not self.emails[0].read:
            self.emails[0].read = True
            # Mark this email as read in notification manager
            self.notification_manager.mark_email_read(self.emails[0].id)

        while running:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "desktop", None

                    elif event.key == pygame.K_RETURN and self.selected_email_index is not None:
                        # Launch selected mission
                        email = self.emails[self.selected_email_index]
                        email.read = True
                        return "launch_mission", email.mission_id

                    elif event.key == pygame.K_UP and self.selected_email_index is not None:
                        self.selected_email_index = max(0, self.selected_email_index - 1)
                        if self.selected_email_index < len(self.emails):
                            email = self.emails[self.selected_email_index]
                            if not email.read:
                                email.read = True
                                self.notification_manager.mark_email_read(email.id)
                        self.content_scroll = 0

                    elif event.key == pygame.K_DOWN and self.selected_email_index is not None:
                        self.selected_email_index = min(len(self.emails) - 1, self.selected_email_index + 1)
                        if self.selected_email_index < len(self.emails):
                            email = self.emails[self.selected_email_index]
                            if not email.read:
                                email.read = True
                                self.notification_manager.mark_email_read(email.id)
                        self.content_scroll = 0

                elif event.type == pygame.MOUSEWHEEL:
                    # Scroll email content with mouse wheel
                    self.content_scroll -= event.y * self.scroll_speed
                    self.content_scroll = max(0, min(self.content_scroll, self.max_scroll))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check reply button first
                        if hasattr(self, 'reply_button_rect') and self.reply_button_rect and self.reply_button_rect.collidepoint(event.pos):
                            # Open email composer for Mission 1
                            from src.ui.email_composer import Mission1EmailComposer
                            composer = Mission1EmailComposer(self.screen)
                            composer_result, submitted_data = composer.run()

                            if composer_result == "sent" and submitted_data:
                                # Validate the submitted data
                                from src.core.network_simulation import get_network_simulator
                                player_name = self.profile_data.get('nickname', 'Player')
                                net_sim = get_network_simulator(player_name)
                                validation_results = net_sim.validate_mission1_data(submitted_data)

                                # Check if all fields are correct
                                all_correct = all(validation_results.values())

                                if all_correct:
                                    # Success! Award rewards and send completion email
                                    from src.data.professor_emails import get_mission1_success_email
                                    success_email_data = get_mission1_success_email(player_name)

                                    # Add success email to inbox
                                    success_email = Email(
                                        id=success_email_data["id"],
                                        sender=success_email_data["sender"],
                                        subject=success_email_data["subject"],
                                        body=success_email_data["body"],
                                        mission_id=success_email_data.get("mission_id"),
                                        attachments=success_email_data.get("attachments", []),
                                        read=False
                                    )
                                    self.emails.append(success_email)

                                    # Award rewards
                                    self.profile_data['progress']['xp'] += 100
                                    self.profile_data['progress']['level'] = 'Debutant'  # Reputation: Debutant
                                    if 'Network Scout' not in self.profile_data['progress']['badges']:
                                        self.profile_data['progress']['badges'].append('Network Scout')
                                    if 'mission1' not in self.profile_data['progress']['missions_completed']:
                                        self.profile_data['progress']['missions_completed'].append('mission1')

                                    # Show success message
                                    from src.ui.show_message import show_message
                                    show_message(self.screen, "[OK] Mission 1 completee! +100 XP, Badge obtenu!", (0, 255, 0), 3000)

                                    # Trigger notification for new email
                                    from src.systems.notification_manager import get_notification_manager
                                    notification_manager = get_notification_manager()
                                    notification_manager.add_notification(success_email.id)
                                else:
                                    # Show error message with which fields were wrong
                                    wrong_fields = [field for field, correct in validation_results.items() if not correct]
                                    error_msg = f"[X] Erreur: Verifiez {', '.join(wrong_fields)}"
                                    from src.ui.show_message import show_message
                                    show_message(self.screen, error_msg, (255, 0, 0), 3000)

                        # Check email list clicks
                        for i, rect in enumerate(email_rects):
                            if rect.collidepoint(event.pos):
                                self.selected_email_index = i
                                email = self.emails[i]
                                if not email.read:
                                    email.read = True
                                    self.notification_manager.mark_email_read(email.id)
                                self.content_scroll = 0

            # Drawing
            self.screen.fill(self.bg_color)

            # Draw sidebar with emails
            email_rects = self.draw_sidebar(mouse_pos)

            # Draw content
            self.draw_content(mouse_pos)

            pygame.display.flip()

        return "exit", None
