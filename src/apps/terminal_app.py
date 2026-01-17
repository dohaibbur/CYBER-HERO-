"""
Terminal App - Cyber Hero Terminal Zero
Command-line interface for mission operations
"""

import pygame
from typing import Tuple, List, Dict, Optional
from src.systems.network_generator import get_network_generator


class TerminalApp:
    """
    Terminal application - Command line interface
    Simulates realistic terminal commands for cybersecurity tasks
    """

    def __init__(self, screen, profile_data: Dict, network_config: Dict = None, mission=None):
        """
        Initialize terminal app

        Args:
            screen: Pygame screen surface
            profile_data: Player profile
            network_config: Current network configuration (for Mission 1)
            mission: Mission object for tracking objectives (optional)
        """
        self.screen = screen
        self.profile_data = profile_data
        self.network_config = network_config
        self.mission = mission
        self.mission_hud = None
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors - Terminal theme
        self.bg_color = (10, 15, 20)
        self.text_color = (0, 255, 65)  # Hacker green
        self.input_color = (0, 200, 255)  # Cyan for user input
        self.error_color = (255, 80, 80)
        self.warning_color = (255, 200, 0)
        self.success_color = (0, 255, 100)

        # Fonts - Standardized sizes (matching desktop) - Monospace for terminal
        try:
            self.terminal_font = pygame.font.Font("assets/fonts/Cyberpunk.ttf", int(26 * self.scale))
        except:
            self.terminal_font = pygame.font.SysFont('courier', int(26 * self.scale))

        # Terminal state
        self.output_lines = []
        self.input_text = ""
        self.command_history = []
        self.history_index = -1
        self.scroll_offset = 0
        self.max_lines = 30

        # Current working directory simulation
        self.cwd = "~"

        # Network state (for Mission 1)
        if not self.network_config:
            # Generate network if not provided
            gen = get_network_generator()
            self.network_config = gen.generate_mission1_network()

        self.blocked_ports = []
        self.isolated_devices = []

        # Mission tracking state
        self.network_scanned = False
        self.devices_discovered = []
        self.commands_history = []  # Track all commands used

        # Notes button
        self.notes_button_rect = None
        self.back_button_rect = None
        self.mission_completed = False

        # Persistent notes data (so it's not lost when closing popup)
        self.mission_notes_data = None

        # Boot sequence
        self.print_boot_sequence()

        # Initialize mission HUD if mission provided
        if self.mission:
            from src.ui.mission_objectives_hud import MissionObjectivesHUD
            self.mission_hud = MissionObjectivesHUD(screen, mission)

    def print_boot_sequence(self):
        """Print initial boot messages"""
        self.output_lines = [
            "CyberHero Terminal v2.7.3",
            "Kernel 5.15.0-cyber",
            "Copyright (C) 2024 CyberHero Foundation",
            "",
            "Bienvenue dans le Terminal.",
            "Tapez 'help' pour voir les commandes disponibles.",
            ""
        ]

    def print_line(self, text: str, color_code: str = "normal"):
        """
        Add line to output

        Args:
            text: Text to print
            color_code: "normal", "error", "warning", "success"
        """
        self.output_lines.append((text, color_code))

        # Limit output history
        if len(self.output_lines) > 1000:
            self.output_lines = self.output_lines[-1000:]

    def get_prompt(self) -> str:
        """Get command prompt string"""
        username = self.profile_data.get('nickname', 'user')
        return f"{username}@cyberhero:{self.cwd}$ "

    def execute_command(self, command: str):
        """
        Execute a terminal command

        Args:
            command: Command string
        """
        command = command.strip()

        if not command:
            return

        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Track command for mission objectives
        self.commands_history.append(command.lower())

        # Echo command
        self.print_line(self.get_prompt() + command, "normal")

        # Parse command
        parts = command.lower().split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Execute command
        if cmd == "help":
            self.cmd_help()
        elif cmd == "clear":
            self.cmd_clear()
        elif cmd == "ipconfig":
            self.cmd_ipconfig(args)
        elif cmd == "ifconfig":
            self.cmd_ifconfig(args)
        elif cmd == "arp":
            self.cmd_arp(args)
        elif cmd == "route":
            self.cmd_route(args)
        elif cmd == "scan":
            self.cmd_scan(args)
        elif cmd == "show":
            self.cmd_show(args)
        elif cmd == "block":
            self.cmd_block(args)
        elif cmd == "allow":
            self.cmd_allow(args)
        elif cmd == "isolate":
            self.cmd_isolate(args)
        elif cmd == "open":
            self.cmd_open(args)
        elif cmd == "check":
            self.cmd_check(args)
        elif cmd == "audit":
            self.cmd_audit()
        elif cmd == "exit":
            self.cmd_exit()
        else:
            self.print_line(f"bash: {cmd}: commande introuvable", "error")
            self.print_line("Tapez 'help' pour voir les commandes disponibles.", "normal")

        self.print_line("", "normal")  # Empty line after command

        # Update mission progress if mission is active
        if self.mission:
            self.mission.update_progress(self.get_state())

    def cmd_help(self):
        """Show help"""
        help_text = [
            "Commandes disponibles:",
            "",
            "=== COMMANDES RESEAU (Mission 1) ===",
            "  ipconfig /all         - Configuration IP complete (Windows)",
            "  ifconfig              - Configuration IP (Linux/Mac)",
            "  arp -a                - Table ARP (appareils connectes)",
            "  route print           - Table de routage (Windows)",
            "  route -n              - Table de routage (Linux/Mac)",
            "",
            "=== COMMANDES MISSION ===",
            "  scan network          - Scanner le reseau local",
            "  show ipconfig         - Afficher configuration IP",
            "  show devices          - Lister les peripheriques",
            "  block port <NUM>      - Bloquer un port",
            "  allow port <NUM>      - Autoriser un port",
            "  isolate device <MAC>  - Isoler un peripherique",
            "  open packet <ID>      - Ouvrir un paquet pour analyse",
            "  check logs            - Verifier les logs systeme",
            "  audit system          - Audit de securite complet",
            "",
            "=== COMMANDES SYSTEME ===",
            "  clear                 - Effacer l'ecran",
            "  help                  - Afficher cette aide",
            "  exit                  - Quitter le terminal",
            ""
        ]
        for line in help_text:
            self.print_line(line, "normal")

    def cmd_clear(self):
        """Clear screen"""
        self.output_lines = []
        self.print_line("", "normal")

    def cmd_scan(self, args: List[str]):
        """Scan network"""
        if not args or args[0] != "network":
            self.print_line("Usage: scan network", "error")
            return

        # Mark network as scanned
        self.network_scanned = True

        self.print_line("Initialisation du scan reseau...", "normal")
        self.print_line("", "normal")

        for device in self.network_config['devices']:
            status = "[ISOLE]" if device['mac'] in self.isolated_devices else "[OK]"
            trust = "FIABLE" if device['is_trusted'] else "INCONNU"

            self.print_line(f"Peripherique trouve: {device['name']}", "success")
            self.print_line(f"  IP:    {device['ip']}", "normal")
            self.print_line(f"  MAC:   {device['mac']}", "normal")
            self.print_line(f"  Type:  {device['type']}", "normal")
            self.print_line(f"  Statut: {trust} {status}", "normal")
            self.print_line(f"  Ports: {', '.join(map(str, device['open_ports']))}", "normal")
            self.print_line("", "normal")

            # Track discovered devices
            if device['mac'] not in self.devices_discovered:
                self.devices_discovered.append(device['mac'])

        self.print_line(f"Scan termine. {len(self.network_config['devices'])} peripheriques trouves.", "success")

    def cmd_show(self, args: List[str]):
        """Show system information"""
        if not args:
            self.print_line("Usage: show [ipconfig|devices]", "error")
            return

        # Use NetworkSimulator for consistent data
        from src.core.network_simulation import get_network_simulator
        player_name = self.profile_data.get('nickname', 'Player')
        net_sim = get_network_simulator(player_name)

        if args[0] == "ipconfig":
            self.print_line("Configuration IP:", "normal")
            self.print_line(f"  Subnet:  {net_sim.network_data['network']['cidr']}", "normal")
            self.print_line(f"  Gateway: {net_sim.network_data['player']['default_gateway']}", "normal")
            self.print_line("", "normal")

        elif args[0] == "devices":
            # Count total devices (router + player + other devices)
            total = net_sim.network_data['network']['total_devices']
            self.print_line(f"Peripheriques sur le reseau ({total}):", "normal")
            self.print_line("", "normal")

            # Show router
            router = net_sim.network_data['router']
            self.print_line(f"  {router['hostname']:<20} {router['ip_address']:<15} [ACTIF]", "normal")

            # Show player
            player = net_sim.network_data['player']
            self.print_line(f"  {player['hostname']:<20} {player['ip_address']:<15} [ACTIF]", "normal")

            # Show other devices
            for device in net_sim.network_data['devices']:
                self.print_line(f"  {device.hostname:<20} {device.ip_address:<15} [ACTIF]", "normal")

        else:
            self.print_line(f"Option inconnue: {args[0]}", "error")

    def cmd_ipconfig(self, args: List[str]):
        """Windows ipconfig command - show network configuration"""
        # Check if player has network simulator (Mission 1)
        player_name = self.profile_data.get('nickname', 'Player')

        # Import network simulator
        from src.core.network_simulation import get_network_simulator
        net_sim = get_network_simulator(player_name)

        # Check for /all flag
        show_all = len(args) > 0 and args[0] == "/all"

        if show_all:
            # Show full output
            output = net_sim.get_ipconfig_output()
            for line in output.split('\n'):
                self.print_line(line, "normal")
        else:
            # Show basic output
            player = net_sim.network_data["player"]
            self.print_line("", "normal")
            self.print_line("Configuration IP de Windows", "normal")
            self.print_line("", "normal")
            self.print_line(f"Carte Ethernet {player['adapter_name']} :", "normal")
            self.print_line("", "normal")
            self.print_line(f"   Adresse IPv4. . . . . . . . . . . . . : {player['ip_address']}", "normal")
            self.print_line(f"   Masque de sous-reseau . . . . . . . : {player['subnet_mask']}", "normal")
            self.print_line(f"   Passerelle par defaut . . . . . . . : {player['default_gateway']}", "normal")
            self.print_line("", "normal")

    def cmd_ifconfig(self, args: List[str]):
        """Linux/Mac ifconfig command - show network configuration"""
        player_name = self.profile_data.get('nickname', 'Player')

        from src.core.network_simulation import get_network_simulator
        net_sim = get_network_simulator(player_name)

        # Show ifconfig output
        output = net_sim.get_ifconfig_output()
        for line in output.split('\n'):
            self.print_line(line, "normal")

    def cmd_arp(self, args: List[str]):
        """ARP command - show address resolution table"""
        player_name = self.profile_data.get('nickname', 'Player')

        from src.core.network_simulation import get_network_simulator
        net_sim = get_network_simulator(player_name)

        # Check for -a flag
        if len(args) > 0 and args[0] == "-a":
            # Show ARP table
            output = net_sim.get_arp_output()
            for line in output.split('\n'):
                self.print_line(line, "normal")
        else:
            self.print_line("Usage: arp -a", "normal")

    def cmd_route(self, args: List[str]):
        """Route command - show routing table"""
        player_name = self.profile_data.get('nickname', 'Player')

        from src.core.network_simulation import get_network_simulator
        net_sim = get_network_simulator(player_name)

        # Check for print flag (Windows) or -n flag (Linux)
        if len(args) > 0 and (args[0] == "print" or args[0] == "-n"):
            # Show routing table
            output = net_sim.get_route_output()
            for line in output.split('\n'):
                self.print_line(line, "normal")
        else:
            self.print_line("Usage: route print (Windows) ou route -n (Linux)", "normal")

    def cmd_block(self, args: List[str]):
        """Block a port"""
        if len(args) < 2 or args[0] != "port":
            self.print_line("Usage: block port <NUM>", "error")
            return

        try:
            port = int(args[1])
            if port in self.blocked_ports:
                self.print_line(f"Le port {port} est deja bloque.", "warning")
            else:
                self.blocked_ports.append(port)
                self.print_line(f"[FIREWALL] Port {port} bloque avec succes.", "success")
        except ValueError:
            self.print_line("Numero de port invalide.", "error")

    def cmd_allow(self, args: List[str]):
        """Allow a port"""
        if len(args) < 2 or args[0] != "port":
            self.print_line("Usage: allow port <NUM>", "error")
            return

        try:
            port = int(args[1])
            if port not in self.blocked_ports:
                self.print_line(f"Le port {port} n'est pas bloque.", "warning")
            else:
                self.blocked_ports.remove(port)
                self.print_line(f"[FIREWALL] Port {port} autorise.", "success")
        except ValueError:
            self.print_line("Numero de port invalide.", "error")

    def cmd_isolate(self, args: List[str]):
        """Isolate a device"""
        if len(args) < 2 or args[0] != "device":
            self.print_line("Usage: isolate device <MAC>", "error")
            return

        mac = args[1].upper()

        # Find device
        device_found = None
        for device in self.network_config['devices']:
            if device['mac'] == mac:
                device_found = device
                break

        if not device_found:
            self.print_line(f"Peripherique avec MAC {mac} introuvable.", "error")
            return

        if mac in self.isolated_devices:
            self.print_line(f"Le peripherique {device_found['name']} est deja isole.", "warning")
        else:
            self.isolated_devices.append(mac)
            self.print_line(f"[SECURITE] Peripherique {device_found['name']} isole du reseau.", "success")

    def cmd_open(self, args: List[str]):
        """Open packet for analysis"""
        if len(args) < 2 or args[0] != "packet":
            self.print_line("Usage: open packet <ID>", "error")
            return

        packet_id = args[1]
        self.print_line(f"Ouverture du paquet {packet_id}...", "normal")
        self.print_line("", "normal")
        self.print_line("[Cette fonctionnalite est disponible dans Packet Lab]", "warning")

    def cmd_check(self, args: List[str]):
        """Check logs"""
        if not args or args[0] != "logs":
            self.print_line("Usage: check logs", "error")
            return

        self.print_line("Verification des logs systeme...", "normal")
        self.print_line("", "normal")
        self.print_line("[Cette fonctionnalite est disponible dans Logs Viewer]", "warning")

    def cmd_audit(self):
        """Run security audit"""
        self.print_line("=== AUDIT DE SECURITE ===", "normal")
        self.print_line("", "normal")

        # Check for risky ports
        risky_open = []
        for device in self.network_config['devices']:
            for port in device['open_ports']:
                if port == 23 and port not in self.blocked_ports:
                    risky_open.append(f"{device['name']} - Port {port} (Telnet)")

        if risky_open:
            self.print_line("[CRITIQUE] Ports dangereux ouverts:", "error")
            for item in risky_open:
                self.print_line(f"  - {item}", "error")
        else:
            self.print_line("[OK] Aucun port dangereux ouvert", "success")

        self.print_line("", "normal")

        # Check for untrusted devices
        untrusted_active = []
        for device in self.network_config['devices']:
            if not device['is_trusted'] and device['mac'] not in self.isolated_devices:
                untrusted_active.append(device['name'])

        if untrusted_active:
            self.print_line("[CRITIQUE] Peripheriques non fiables actifs:", "error")
            for name in untrusted_active:
                self.print_line(f"  - {name}", "error")
        else:
            self.print_line("[OK] Aucun peripherique non fiable actif", "success")

        self.print_line("", "normal")

        # Final verdict
        if not risky_open and not untrusted_active:
            self.print_line("=== RESEAU SECURISE ===", "success")
        else:
            self.print_line("=== RESEAU VULNERABLE ===", "error")

    def cmd_exit(self):
        """Exit terminal (will be handled in run loop)"""
        pass

    def draw(self):
        """Draw terminal interface"""
        self.screen.fill(self.bg_color)

        # Calculate visible lines
        line_height = int(22 * self.scale)
        max_visible = (self.screen_height - int(100 * self.scale_y)) // line_height

        # Draw output lines
        y = int(20 * self.scale_y)
        start_line = max(0, len(self.output_lines) - max_visible - self.scroll_offset)
        end_line = len(self.output_lines) - self.scroll_offset

        for i in range(start_line, end_line):
            if i < 0 or i >= len(self.output_lines):
                continue

            line_data = self.output_lines[i]

            if isinstance(line_data, tuple):
                text, color_code = line_data
                if color_code == "error":
                    color = self.error_color
                elif color_code == "warning":
                    color = self.warning_color
                elif color_code == "success":
                    color = self.success_color
                else:
                    color = self.text_color
            else:
                text = line_data
                color = self.text_color

            text_surface = self.terminal_font.render(text, True, color)
            self.screen.blit(text_surface, (int(20 * self.scale_x), y))
            y += line_height

        # Draw input line
        input_y = self.screen_height - int(60 * self.scale_y)
        pygame.draw.line(self.screen, self.text_color,
                        (0, input_y - int(10 * self.scale_y)),
                        (self.screen_width, input_y - int(10 * self.scale_y)), 2)

        prompt_text = self.get_prompt()
        prompt_surface = self.terminal_font.render(prompt_text, True, self.text_color)
        self.screen.blit(prompt_surface, (int(20 * self.scale_x), input_y))

        # Draw user input
        input_surface = self.terminal_font.render(self.input_text, True, self.input_color)
        input_x = int(20 * self.scale_x) + prompt_surface.get_width()
        self.screen.blit(input_surface, (input_x, input_y))

        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_x + input_surface.get_width()
            pygame.draw.rect(self.screen, self.input_color,
                           (cursor_x, input_y, int(10 * self.scale_x), int(20 * self.scale_y)))

        # Draw RETOUR button (Top Right)
        back_btn_width = int(120 * self.scale_x)
        back_btn_height = int(40 * self.scale_y)
        back_btn_x = self.screen_width - back_btn_width - int(20 * self.scale_x)
        back_btn_y = int(15 * self.scale_y)
        
        self.back_button_rect = pygame.Rect(back_btn_x, back_btn_y, back_btn_width, back_btn_height)
        
        mouse_pos = pygame.mouse.get_pos()
        is_back_hovered = self.back_button_rect.collidepoint(mouse_pos)
        
        back_color = (200, 60, 60) if is_back_hovered else (160, 40, 40)
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=int(5 * self.scale))
        
        back_text = self.terminal_font.render("RETOUR", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Draw RAPPORT button (Mission 1 only) - Bottom Right
        if self.mission and not self.mission_completed:
            button_width = int(150 * self.scale_x)
            button_height = int(45 * self.scale_y)
            button_x = self.screen_width - button_width - int(20 * self.scale_x)
            button_y = self.screen_height - button_height - int(80 * self.scale_y)

            self.notes_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = self.notes_button_rect.collidepoint(mouse_pos)

            button_color = (0, 255, 120) if is_hovered else (0, 220, 50)
            pygame.draw.rect(self.screen, button_color, self.notes_button_rect, border_radius=int(6 * self.scale))

            # Button text
            button_text = self.terminal_font.render("RAPPORT", True, (0, 0, 0))
            text_rect = button_text.get_rect(center=self.notes_button_rect.center)
            self.screen.blit(button_text, text_rect)

        # Instructions
        if self.mission:
            help_text = "ESC: Retour | ENTREE: Executer | Fleches: Historique | TAB: Toggle Objectifs"
        else:
            help_text = "ESC: Retour | ENTREE: Executer | Fleches: Historique"
        help_surface = self.terminal_font.render(help_text, True, (100, 100, 100))
        self.screen.blit(help_surface, (int(20 * self.scale_x), self.screen_height - int(25 * self.scale_y)))

        # Draw mission HUD if active
        if self.mission_hud:
            self.mission_hud.draw()

    def run(self) -> str:
        """
        Run terminal application

        Returns:
            "exit" or "desktop"
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "desktop"

                    elif event.key == pygame.K_RETURN:
                        if self.input_text.strip() == "exit":
                            return "desktop"
                        self.execute_command(self.input_text)
                        self.input_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]

                    elif event.key == pygame.K_UP:
                        # Command history - previous
                        if self.history_index > 0:
                            self.history_index -= 1
                            self.input_text = self.command_history[self.history_index]

                    elif event.key == pygame.K_DOWN:
                        # Command history - next
                        if self.history_index < len(self.command_history) - 1:
                            self.history_index += 1
                            self.input_text = self.command_history[self.history_index]
                        else:
                            self.history_index = len(self.command_history)
                            self.input_text = ""

                    elif event.key == pygame.K_TAB:
                        # Toggle mission HUD
                        if self.mission_hud:
                            self.mission_hud.toggle_expanded()

                    elif event.unicode.isprintable():
                        self.input_text += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check back button
                        if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                            return "desktop"

                        # Check notes button
                        if self.notes_button_rect and self.notes_button_rect.collidepoint(event.pos):
                            result = self.open_mission_notes()
                            if result == "mission_complete":
                                return "mission_complete"

            self.draw()
            pygame.display.flip()

        return "desktop"

    def open_mission_notes(self):
        """Open mission notes popup"""
        from src.ui.mission_notes import MissionNotesPopup
        from src.core.network_simulation import get_network_simulator

        # Capture background
        background = self.screen.copy()

        # Get NetworkSimulator data for validation
        player_name = self.profile_data.get('nickname', 'Player')
        net_sim = get_network_simulator(player_name)
        network_data = net_sim.network_data

        # Create and run notes popup with persisted data
        notes_popup = MissionNotesPopup(self.screen, self.profile_data, network_data, self.mission_notes_data)
        result, data = notes_popup.run(background)

        # Always save the data (even if just closing) so it persists
        if result == "close":
            self.mission_notes_data = data
            return  # Just close, don't do anything else

        if result == "send":
            # Mission completed!
            self.mission_completed = True
            self.print_line("", "success")
            self.print_line("=" * 60, "success")
            self.print_line("MISSION 1 TERMINEE AVEC SUCCES!", "success")
            self.print_line("=" * 60, "success")
            self.print_line("", "success")
            self.print_line("Rapport envoye au Professeur.", "success")
            self.print_line("Consultez vos emails pour sa reponse.", "success")
            self.print_line("", "success")

            # Return success status so main.py can show the completion popup
            return "mission_complete"

    def get_state(self) -> Dict:
        """
        Get current terminal state for mission tracking

        Returns:
            Dictionary with terminal state
        """
        return {
            'commands_history': self.commands_history,
            'blocked_ports': self.blocked_ports,
            'isolated_devices': self.isolated_devices,
            'network_scanned': self.network_scanned,
            'devices_discovered': self.devices_discovered,
            'mission_completed': self.mission_completed
        }
