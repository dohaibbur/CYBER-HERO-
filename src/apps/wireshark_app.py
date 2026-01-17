"""
Wireshark App - Packet Analyzer for Mission 2
Simplified Wireshark-like interface for analyzing network packets
"""

import pygame
from typing import Dict, Tuple, Optional, List
import random


class WiresharkApp:
    """
    Wireshark-style packet analyzer
    Used for Mission 2 packet analysis objectives
    """

    def __init__(self, screen, profile_data: Dict, mission=None):
        """
        Initialize Wireshark

        Args:
            screen: Pygame screen surface
            profile_data: Player profile
            mission: Active mission (optional)
        """
        self.screen = screen
        self.profile_data = profile_data
        self.mission = mission
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors (Wireshark-like theme)
        self.bg_color = (30, 30, 35)
        self.header_bg = (45, 45, 55)
        self.toolbar_bg = (40, 40, 50)
        self.packet_list_bg = (25, 25, 30)
        self.detail_bg = (35, 35, 42)
        self.hex_bg = (20, 20, 25)

        self.primary_color = (0, 180, 220)
        self.text_color = (220, 220, 225)
        self.dim_color = (120, 120, 130)
        self.success_color = (100, 220, 100)
        self.warning_color = (220, 180, 50)
        self.error_color = (220, 80, 80)
        self.button_bg = (40, 45, 60)
        self.button_hover = (60, 65, 85)

        # Packet type colors
        self.tcp_color = (180, 220, 255)
        self.udp_color = (180, 255, 200)
        self.http_color = (200, 255, 180)
        self.dns_color = (255, 220, 180)
        self.arp_color = (255, 200, 200)
        self.suspicious_color = (255, 100, 100)

        # Fonts - Standardized sizes (matching desktop)
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()

        try:
            self.title_font = settings.get_scaled_font(int(42 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.heading_font = settings.get_scaled_font(int(32 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.body_font = settings.get_scaled_font(int(26 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.small_font = settings.get_scaled_font(int(22 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.mono_font = settings.get_scaled_font(int(22 * self.scale))  # Monospace for hex
        except:
            self.title_font = settings.get_scaled_font(int(42 * self.scale))
            self.heading_font = settings.get_scaled_font(int(32 * self.scale))
            self.body_font = settings.get_scaled_font(int(26 * self.scale))
            self.small_font = settings.get_scaled_font(int(22 * self.scale))
            self.mono_font = settings.get_scaled_font(int(22 * self.scale))

        # Generate packet capture data
        self.packets = self.generate_capture_data()
        self.selected_packet = None
        self.packet_rects = {}
        self.scroll_offset = 0
        self.max_visible_packets = 11  # Reduced for larger row height

        # Filter
        self.filter_text = ""
        self.filter_active = False
        self.filtered_packets = self.packets.copy()

        # Notes button and persisted data
        self.notes_button_rect = None
        self.back_button_rect = None  # Added back button
        self.notes_persisted_data = None

    def generate_capture_data(self) -> List[Dict]:
        """Generate realistic packet capture data for Mission 2"""
        packets = []

        # Network devices (from our fixed network)
        devices = {
            "player": "192.168.1.120",
            "router": "192.168.1.1",
            "laptop": "192.168.1.75",
            "phone": "192.168.1.155",
            "tv": "192.168.1.185",
            "printer": "192.168.1.220",
            "suspicious": "192.168.1.66"  # Unknown suspicious device
        }

        external = ["8.8.8.8", "142.250.74.110", "151.101.1.140", "104.16.123.96"]

        packet_id = 1
        time_offset = 0.0

        # Generate normal traffic patterns
        for _ in range(25):
            time_offset += random.uniform(0.01, 0.15)

            # DNS queries
            if random.random() < 0.15:
                packets.append({
                    "id": packet_id,
                    "time": f"{time_offset:.6f}",
                    "src": devices["player"],
                    "dst": "8.8.8.8",
                    "protocol": "DNS",
                    "length": random.randint(60, 90),
                    "info": f"Standard query A {'google.com' if random.random() > 0.5 else 'example.com'}",
                    "suspicious": False
                })
                packet_id += 1
                time_offset += 0.02
                packets.append({
                    "id": packet_id,
                    "time": f"{time_offset:.6f}",
                    "src": "8.8.8.8",
                    "dst": devices["player"],
                    "protocol": "DNS",
                    "length": random.randint(90, 150),
                    "info": "Standard query response",
                    "suspicious": False
                })
                packet_id += 1

            # HTTP traffic
            elif random.random() < 0.3:
                ext_ip = random.choice(external)
                packets.append({
                    "id": packet_id,
                    "time": f"{time_offset:.6f}",
                    "src": devices["player"],
                    "dst": ext_ip,
                    "protocol": "HTTP",
                    "length": random.randint(200, 500),
                    "info": f"GET /index.html HTTP/1.1",
                    "suspicious": False
                })
                packet_id += 1

            # ARP
            elif random.random() < 0.2:
                dev = random.choice(list(devices.values()))
                packets.append({
                    "id": packet_id,
                    "time": f"{time_offset:.6f}",
                    "src": dev,
                    "dst": "ff:ff:ff:ff:ff:ff",
                    "protocol": "ARP",
                    "length": 42,
                    "info": f"Who has {devices['router']}? Tell {dev}",
                    "suspicious": False
                })
                packet_id += 1

            # TCP
            else:
                packets.append({
                    "id": packet_id,
                    "time": f"{time_offset:.6f}",
                    "src": devices["player"],
                    "dst": random.choice(external),
                    "protocol": "TCP",
                    "length": random.randint(54, 1500),
                    "info": f"{random.randint(40000, 60000)} -> 443 [ACK] Seq={random.randint(1000, 9999)}",
                    "suspicious": False
                })
                packet_id += 1

        # Add SUSPICIOUS packets for Mission 2
        suspicious_packets = [
            {
                "id": packet_id,
                "time": f"{time_offset + 0.5:.6f}",
                "src": devices["suspicious"],
                "dst": devices["router"],
                "protocol": "TCP",
                "length": 66,
                "info": "23 -> 23 [SYN] - TELNET CONNECTION ATTEMPT",
                "suspicious": True,
                "threat": "telnet_scan"
            },
            {
                "id": packet_id + 1,
                "time": f"{time_offset + 0.8:.6f}",
                "src": devices["suspicious"],
                "dst": devices["player"],
                "protocol": "TCP",
                "length": 54,
                "info": "Port scan detected: 22, 23, 80, 443, 3389",
                "suspicious": True,
                "threat": "port_scan"
            },
            {
                "id": packet_id + 2,
                "time": f"{time_offset + 1.2:.6f}",
                "src": devices["suspicious"],
                "dst": "255.255.255.255",
                "protocol": "UDP",
                "length": 342,
                "info": "Broadcast - Possible network discovery",
                "suspicious": True,
                "threat": "discovery"
            },
            {
                "id": packet_id + 3,
                "time": f"{time_offset + 1.5:.6f}",
                "src": devices["suspicious"],
                "dst": devices["printer"],
                "protocol": "TCP",
                "length": 156,
                "info": "9100 -> 9100 [PSH,ACK] - Printer exploitation attempt",
                "suspicious": True,
                "threat": "printer_exploit"
            },
            {
                "id": packet_id + 4,
                "time": f"{time_offset + 2.0:.6f}",
                "src": devices["suspicious"],
                "dst": "185.234.72.100",
                "protocol": "TCP",
                "length": 1248,
                "info": "443 -> 4444 [PSH,ACK] - DATA EXFILTRATION DETECTED",
                "suspicious": True,
                "threat": "exfiltration"
            }
        ]

        packets.extend(suspicious_packets)

        # Sort by time
        packets.sort(key=lambda x: float(x["time"]))

        return packets

    def apply_filter(self):
        """Apply filter to packets"""
        if not self.filter_text:
            self.filtered_packets = self.packets.copy()
        else:
            filter_lower = self.filter_text.lower()
            self.filtered_packets = [
                p for p in self.packets
                if (filter_lower in p["src"].lower() or
                    filter_lower in p["dst"].lower() or
                    filter_lower in p["protocol"].lower() or
                    filter_lower in p["info"].lower() or
                    (filter_lower == "suspicious" and p.get("suspicious", False)))
            ]
        self.scroll_offset = 0
        self.selected_packet = None

    def draw_back_button(self, mouse_pos):
        """Draw the clickable back button to return to Net Scanner"""
        # Button dimensions
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_x = self.screen_width - button_width - int(30 * self.scale_x)  # Right side
        button_y = int(10 * self.scale_y)  # Top of header

        # Create button rect
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Check if hovered
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)

        # Button background
        button_bg = self.button_hover if is_hovered else self.button_bg
        pygame.draw.rect(self.screen, button_bg, self.back_button_rect, border_radius=int(6 * self.scale))

        # Button border
        border_color = self.success_color if is_hovered else self.primary_color
        pygame.draw.rect(self.screen, border_color, self.back_button_rect, width=2, border_radius=int(6 * self.scale))

        # Button text
        back_text = self.body_font.render("RETOUR", True, self.text_color)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_rect)

        # Return hover state for cursor change
        return is_hovered

    def draw(self):
        """Draw the Wireshark interface"""
        self.screen.fill(self.bg_color)

        # Header/Menu bar - larger for bigger fonts
        header_height = int(60 * self.scale_y)  # Increased for back button
        pygame.draw.rect(self.screen, self.header_bg, (0, 0, self.screen_width, header_height))

        # Title
        title = self.title_font.render("Wireshark - Capture Analysis", True, self.primary_color)
        self.screen.blit(title, (int(15 * self.scale_x), header_height // 2 - title.get_height() // 2))

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Draw back button to return to Net Scanner directory
        is_back_hovered = self.draw_back_button(mouse_pos)

        # Change cursor if hovering back button
        if is_back_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Toolbar with filter - larger
        toolbar_y = header_height
        toolbar_height = int(55 * self.scale_y)
        pygame.draw.rect(self.screen, self.toolbar_bg, (0, toolbar_y, self.screen_width, toolbar_height))

        # Filter label
        filter_label = self.body_font.render("Filtre:", True, self.text_color)
        self.screen.blit(filter_label, (int(15 * self.scale_x), toolbar_y + toolbar_height // 2 - filter_label.get_height() // 2))

        # Filter input box - larger
        filter_x = int(100 * self.scale_x)
        filter_width = int(450 * self.scale_x)
        filter_height = int(38 * self.scale_y)
        filter_y = toolbar_y + (toolbar_height - filter_height) // 2
        filter_rect = pygame.Rect(filter_x, filter_y, filter_width, filter_height)

        filter_bg = (50, 50, 60) if self.filter_active else (40, 40, 50)
        pygame.draw.rect(self.screen, filter_bg, filter_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.primary_color if self.filter_active else (60, 60, 70), filter_rect, width=2, border_radius=5)

        # Filter text
        filter_display = self.filter_text if self.filter_text else "Tapez 'suspicious' pour filtrer"
        filter_color = self.text_color if self.filter_text else self.dim_color
        filter_text_surf = self.small_font.render(filter_display, True, filter_color)
        self.screen.blit(filter_text_surf, (filter_x + 10, filter_y + filter_height // 2 - filter_text_surf.get_height() // 2))

        # Hint - positioned to the right
        hint = self.small_font.render("Indice: filtrez par 'suspicious'", True, self.warning_color)
        self.screen.blit(hint, (filter_x + filter_width + int(30 * self.scale_x), toolbar_y + toolbar_height // 2 - hint.get_height() // 2))

        # Packet list header - larger
        list_y = toolbar_y + toolbar_height
        list_header_height = int(35 * self.scale_y)
        pygame.draw.rect(self.screen, self.header_bg, (0, list_y, self.screen_width, list_header_height))

        # Column headers - wider columns for bigger text
        cols = [
            ("No.", int(70 * self.scale_x)),
            ("Time", int(110 * self.scale_x)),
            ("Source", int(170 * self.scale_x)),
            ("Destination", int(170 * self.scale_x)),
            ("Protocol", int(100 * self.scale_x)),
            ("Length", int(80 * self.scale_x)),
            ("Info", int(550 * self.scale_x))
        ]

        col_x = int(10 * self.scale_x)
        for col_name, col_width in cols:
            col_text = self.small_font.render(col_name, True, self.text_color)
            self.screen.blit(col_text, (col_x, list_y + list_header_height // 2 - col_text.get_height() // 2))
            col_x += col_width

        # Packet list - adjusted height
        packet_list_y = list_y + list_header_height
        packet_list_height = int(380 * self.scale_y)
        pygame.draw.rect(self.screen, self.packet_list_bg, (0, packet_list_y, self.screen_width, packet_list_height))

        # Larger row height for bigger fonts
        row_height = int(32 * self.scale_y)
        self.packet_rects = {}

        visible_packets = self.filtered_packets[self.scroll_offset:self.scroll_offset + self.max_visible_packets]

        for i, packet in enumerate(visible_packets):
            row_y = packet_list_y + i * row_height
            row_rect = pygame.Rect(0, row_y, self.screen_width, row_height)
            self.packet_rects[packet["id"]] = row_rect

            # Row background
            is_selected = self.selected_packet == packet["id"]
            is_suspicious = packet.get("suspicious", False)

            if is_selected:
                row_bg = (60, 80, 120)
            elif is_suspicious:
                row_bg = (80, 40, 40)
            elif i % 2 == 0:
                row_bg = (28, 28, 33)
            else:
                row_bg = (32, 32, 38)

            pygame.draw.rect(self.screen, row_bg, row_rect)

            # Get protocol color
            protocol = packet["protocol"]
            if is_suspicious:
                proto_color = self.suspicious_color
            elif protocol == "TCP":
                proto_color = self.tcp_color
            elif protocol == "UDP":
                proto_color = self.udp_color
            elif protocol == "HTTP":
                proto_color = self.http_color
            elif protocol == "DNS":
                proto_color = self.dns_color
            elif protocol == "ARP":
                proto_color = self.arp_color
            else:
                proto_color = self.text_color

            # Draw columns
            col_x = int(10 * self.scale_x)
            values = [
                str(packet["id"]),
                packet["time"][:8],
                packet["src"],
                packet["dst"],
                packet["protocol"],
                str(packet["length"]),
                packet["info"][:55]  # Shorter to fit with larger font
            ]

            for j, (_, col_width) in enumerate(cols):
                val = values[j]
                color = proto_color if j != 0 else self.dim_color
                val_text = self.small_font.render(val, True, color)
                self.screen.blit(val_text, (col_x, row_y + row_height // 2 - val_text.get_height() // 2))
                col_x += col_width

        # Packet details panel - larger
        details_y = packet_list_y + packet_list_height + int(10 * self.scale_y)
        details_height = int(180 * self.scale_y)
        pygame.draw.rect(self.screen, self.detail_bg, (0, details_y, self.screen_width, details_height))

        # Details header
        details_title = self.body_font.render("Details du Paquet", True, self.primary_color)
        self.screen.blit(details_title, (int(15 * self.scale_x), details_y + int(10 * self.scale_y)))

        if self.selected_packet:
            packet = next((p for p in self.packets if p["id"] == self.selected_packet), None)
            if packet:
                detail_y = details_y + int(45 * self.scale_y)
                details = [
                    f"Frame {packet['id']}: {packet['length']} bytes",
                    f"Source: {packet['src']}",
                    f"Destination: {packet['dst']}",
                    f"Protocol: {packet['protocol']}",
                    f"Info: {packet['info']}"
                ]

                if packet.get("suspicious"):
                    details.append("")
                    details.append(f"ALERTE: Activite suspecte detectee!")
                    details.append(f"Type de menace: {packet.get('threat', 'unknown')}")

                for detail in details:
                    color = self.error_color if "ALERTE" in detail else self.text_color
                    detail_text = self.small_font.render(detail, True, color)
                    self.screen.blit(detail_text, (int(20 * self.scale_x), detail_y))
                    detail_y += int(22 * self.scale_y)

        # Status bar - larger
        status_y = self.screen_height - int(40 * self.scale_y)
        pygame.draw.rect(self.screen, self.header_bg, (0, status_y, self.screen_width, int(40 * self.scale_y)))

        status_text = f"Packets: {len(self.filtered_packets)} affiches | {len(self.packets)} total"
        if self.filter_text:
            status_text += f" | Filtre: {self.filter_text}"

        status = self.small_font.render(status_text, True, self.dim_color)
        self.screen.blit(status, (int(15 * self.scale_x), status_y + int(10 * self.scale_y)))

        # RAPPORT button (Bottom Right)
        btn_width = int(160 * self.scale_x)
        btn_height = int(50 * self.scale_y)
        btn_x = self.screen_width - btn_width - int(20 * self.scale_x)
        btn_y = self.screen_height - btn_height - int(60 * self.scale_y)

        self.notes_button_rect = pygame.Rect(
            btn_x, btn_y,
            btn_width,
            btn_height
        )
        is_notes_hovered = self.notes_button_rect.collidepoint(mouse_pos)
        notes_bg = (80, 60, 100) if is_notes_hovered else (55, 40, 85)
        pygame.draw.rect(self.screen, notes_bg, self.notes_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, self.notes_button_rect, width=2, border_radius=int(8 * self.scale))

        notes_text = self.body_font.render("RAPPORT", True, self.text_color)
        notes_text_rect = notes_text.get_rect(center=self.notes_button_rect.center)
        self.screen.blit(notes_text, notes_text_rect)

    def on_packet_selected(self, packet: Dict):
        """
        Called when a packet is selected - tracks mission progress

        Args:
            packet: The selected packet data
        """
        if packet.get("suspicious") and self.mission:
            # Track that player found a suspicious packet
            threat_type = packet.get("threat")
            if threat_type:
                # Report the threat to mission
                if hasattr(self.mission, 'report_threat_found'):
                    self.mission.report_threat_found(threat_type)

                # Check if player found the suspicious IP
                if hasattr(self.mission, 'submit_suspicious_ip'):
                    self.mission.submit_suspicious_ip(packet["src"])

    def open_notes_popup(self) -> Optional[str]:
        """
        Open the Mission 2 notes popup

        Returns:
            "mission_complete" if mission was completed, None otherwise
        """
        from src.ui.mission2_notes import Mission2NotesPopup

        # Capture current screen as background
        background = self.screen.copy()

        # Create and run notes popup
        notes_popup = Mission2NotesPopup(
            self.screen,
            self.profile_data,
            self.mission,
            self.notes_persisted_data
        )

        result, field_data = notes_popup.run(background)

        if result == "send":
            # Mission completed - all fields validated
            print("[DEBUG] Mission 2 report submitted successfully!")
            return "mission_complete"
        elif result == "close":
            # Save the field data for next time
            self.notes_persisted_data = field_data
        elif result == "exit":
            return "exit"

        return None

    def run(self) -> str:
        """
        Run the Wireshark app

        Returns:
            "desktop" to return to desktop, "exit" to quit game, "mission_complete" if mission done
        """
        clock = pygame.time.Clock()
        running = True

        # Mark Wireshark as opened for mission tracking
        if self.mission and hasattr(self.mission, 'mark_wireshark_opened'):
            self.mission.mark_wireshark_opened()

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC still works for keyboard users
                        return "desktop"

                    elif event.key == pygame.K_UP:
                        if self.scroll_offset > 0:
                            self.scroll_offset -= 1

                    elif event.key == pygame.K_DOWN:
                        if self.scroll_offset < len(self.filtered_packets) - self.max_visible_packets:
                            self.scroll_offset += 1

                    elif event.key == pygame.K_BACKSPACE:
                        if self.filter_text:
                            self.filter_text = self.filter_text[:-1]
                            self.apply_filter()

                    elif event.key == pygame.K_RETURN:
                        self.filter_active = not self.filter_active

                    elif event.unicode.isprintable() and len(self.filter_text) < 50:
                        self.filter_text += event.unicode
                        self.apply_filter()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check Back button click FIRST (to return to Net Scanner)
                        if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                            return "desktop"  # Returns to desktop, which will show Net Scanner again

                        # Check Notes button click
                        if self.notes_button_rect and self.notes_button_rect.collidepoint(event.pos):
                            result = self.open_notes_popup()
                            if result == "mission_complete":
                                return "mission_complete"
                            elif result == "exit":
                                return "exit"
                            continue

                        # Check packet clicks
                        for packet_id, rect in self.packet_rects.items():
                            if rect.collidepoint(event.pos):
                                self.selected_packet = packet_id
                                # Track mission progress when selecting suspicious packets
                                packet = next((p for p in self.packets if p["id"] == packet_id), None)
                                if packet:
                                    self.on_packet_selected(packet)
                                break

                    elif event.button == 4:  # Scroll up
                        if self.scroll_offset > 0:
                            self.scroll_offset -= 1

                    elif event.button == 5:  # Scroll down
                        if self.scroll_offset < len(self.filtered_packets) - self.max_visible_packets:
                            self.scroll_offset += 1

            self.draw()
            pygame.display.flip()

        return "desktop"