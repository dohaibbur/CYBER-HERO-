"""
PCAP Analyzer App - Raw Packet File Analyzer for Mission 3
Shows hex dump of packet capture with annotations
Player must extract data like MAC, IP, timestamps from raw bytes
"""

import pygame
from typing import Dict, Tuple, Optional, List


class PcapAnalyzerApp:
    """
    PCAP file analyzer - shows raw hex dump
    Used for Mission 3 packet file analysis
    """

    def __init__(self, screen, profile_data: Dict, mission=None):
        """
        Initialize PCAP Analyzer

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

        # Colors
        self.bg_color = (20, 15, 30)  # Dark purple background
        self.header_bg = (35, 28, 50)
        self.panel_bg = (28, 22, 42)
        self.hex_bg = (25, 20, 38)

        self.primary_color = (180, 130, 255)  # Purple accent
        self.text_color = (220, 215, 230)
        self.dim_color = (120, 115, 135)
        self.highlight_color = (255, 200, 100)  # Yellow highlight
        self.annotation_color = (100, 200, 255)  # Cyan for annotations
        self.success_color = (100, 220, 100)
        self.warning_color = (220, 180, 50)
        self.button_bg = (50, 40, 70)
        self.button_hover = (70, 60, 100)

        # Section colors (for different parts of the packet)
        self.pcap_header_color = (255, 180, 100)  # Orange - PCAP header
        self.packet_header_color = (100, 200, 255)  # Cyan - Packet header
        self.packet_data_color = (180, 255, 180)  # Green - Packet data

        # Fonts - Standardized sizes (matching desktop)
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()

        try:
            self.title_font = settings.get_scaled_font(int(46 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.heading_font = settings.get_scaled_font(int(36 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.body_font = settings.get_scaled_font(int(30 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.mono_font = settings.get_scaled_font(int(28 * self.scale))  # Monospace for hex
            self.small_font = settings.get_scaled_font(int(26 * self.scale))
        except:
            self.title_font = settings.get_scaled_font(int(46 * self.scale))
            self.heading_font = settings.get_scaled_font(int(36 * self.scale))
            self.body_font = settings.get_scaled_font(int(30 * self.scale))
            self.mono_font = settings.get_scaled_font(int(28 * self.scale))
            self.small_font = settings.get_scaled_font(int(26 * self.scale))

        # Generate packet capture data (raw hex)
        self.hex_data = self.generate_pcap_data()
        self.annotations = self.generate_annotations()

        # Scroll
        self.scroll_offset = 0
        self.max_visible_lines = 12  # Reduced for larger fonts

        # Notes button
        self.notes_button_rect = None
        self.back_button_rect = None  # Added back button
        self.notes_persisted_data = None

        # Guide button and popup
        self.guide_button_rect = None
        self.show_guide_popup = False
        self.guide_close_btn_rect = None

        # Decoder button and popup
        self.decoder_button_rect = None
        self.show_decoder_popup = False
        self.decoder_dropdown_open = False
        self.decoder_selected = None  # Currently selected decoder
        self.decoder_input = ""
        self.decoder_output = ""
        self.decoder_input_active = False
        self.decoder_close_btn_rect = None

        # Decoder types
        self.decoders = [
            {"id": "hex_dec", "name": "Hexadecimal -> Decimal decoder"},
            {"id": "hex_ip", "name": "Hexadecimal -> IP address (dotted decimal) decoder"},
            {"id": "mac_format", "name": "MAC address formatter"},
            {"id": "endian", "name": "Endianness decoder"},
            {"id": "protocol", "name": "Protocol number decoder"},
        ]
        self.decoder_rects = {}

        # Selected byte range for highlighting
        self.selected_range = None

    def generate_pcap_data(self) -> List[Dict]:
        """
        Generate realistic PCAP file hex dump with CORRECT byte alignment

        Structure:
        - PCAP Global Header: 24 bytes (0x00-0x17)
        - Packet Header: 16 bytes (0x18-0x27)
        - Packet Data starts at 0x28:
          - Ethernet Header: 14 bytes (Dest MAC 6, Src MAC 6, EtherType 2)
          - IP Header: 20 bytes (starts at 0x36)
          - TCP Header: 20+ bytes

        Correct answers to extract:
        - Dest MAC: 00:1e:ec:26:d2:ac (bytes 0x28-0x2D)
        - Src MAC: 26:02:06:49:6b:31 (bytes 0x2E-0x33)
        - EtherType: 08 00 = IPv4 (bytes 0x34-0x35)
        - IP Header starts at 0x36
        - Protocol: 06 = TCP (byte 0x3F)
        - Src IP: 46.105.99.163 = 2e.69.63.a3 (bytes 0x42-0x45)
        - Dst IP: 192.168.4.2 = c0.a8.04.02 (bytes 0x46-0x49)
        - Packet Length: 66 bytes (0x42) from packet header
        - Timestamp: 15/06/2024 from packet header
        """

        # Byte-accurate hex dump
        # Each line = 8 bytes, offsets are correct
        #
        # Key positions for extraction (VERIFIED):
        # 0x28-0x2D: Dest MAC (6 bytes) = 00:1e:ec:26:d2:ac
        # 0x2E-0x33: Src MAC (6 bytes) = 26:02:06:49:6b:31
        # 0x34-0x35: EtherType = 08 00 (IPv4)
        # 0x36: IP Version/IHL = 45 (IPv4, 20 byte header)
        # 0x3E: TTL = 80 (128)
        # 0x3F: Protocol = 06 (TCP)
        # 0x42-0x45: Src IP = 2e 69 63 a3 = 46.105.99.163
        # 0x46-0x49: Dst IP = c0 a8 04 02 = 192.168.4.2

        hex_lines = [
            # === PCAP Global Header (24 bytes: 0x00-0x17) ===
            {
                "offset": "0000",
                "hex": "d4 c3 b2 a1 02 00 04 00",
                "ascii": "........",
                "section": "pcap_header",
                "annotation": "Magic: d4c3b2a1 (Little Endian) | Ver: 2.4"
            },
            {
                "offset": "0008",
                "hex": "00 00 00 00 00 00 00 00",
                "ascii": "........",
                "section": "pcap_header",
                "annotation": "ThisZone + SigFigs (non utilise)"
            },
            {
                "offset": "0010",
                "hex": "ff ff 00 00 01 00 00 00",
                "ascii": "........",
                "section": "pcap_header",
                "annotation": "SnapLen: 65535 | LinkType: 1 (Ethernet)"
            },

            # === Packet Record Header (16 bytes: 0x18-0x27) ===
            {
                "offset": "0018",
                "hex": "a8 5d 76 66 00 00 00 00",
                "ascii": ".]vf....",
                "section": "packet_header",
                "annotation": "Timestamp sec (Little Endian) = 15/06/2024"
            },
            {
                "offset": "0020",
                "hex": "42 00 00 00 42 00 00 00",
                "ascii": "B...B...",
                "section": "packet_header",
                "annotation": "Captured: 0x42=66 bytes | Original: 66 bytes"
            },

            # === Ethernet Header (14 bytes: 0x28-0x35) ===
            # 0x28-0x2D: Dest MAC (6 bytes)
            # 0x2E-0x33: Src MAC (6 bytes)
            # 0x34-0x35: EtherType (2 bytes)
            {
                "offset": "0028",
                "hex": "00 1e ec 26 d2 ac 26 02",
                "ascii": "...&..&.",
                "section": "packet_data",
                "annotation": "Dest MAC: 00:1e:ec:26:d2:ac | Src MAC start..."
            },
            {
                "offset": "0030",
                "hex": "06 49 6b 31 08 00 45 00",
                "ascii": ".Ik1..E.",
                "section": "packet_data",
                "annotation": "...Src MAC: 26:02:06:49:6b:31 | EtherType:0800"
            },

            # === IP Header (20 bytes: 0x36-0x49) ===
            # Ethernet ends at 0x35 (EtherType 08 00)
            # IP Header starts at 0x36:
            #   0x36: Version/IHL = 45 (IPv4, 20-byte header)
            #   0x37: DSCP/ECN = 00
            #   0x38-0x39: Total Length
            #   0x3A-0x3B: Identification
            #   0x3C-0x3D: Flags/Fragment
            #   0x3E: TTL
            #   0x3F: Protocol = 06 (TCP)
            #   0x40-0x41: Header Checksum
            #   0x42-0x45: Src IP = 2e 69 63 a3 = 46.105.99.163
            #   0x46-0x49: Dst IP = c0 a8 04 02 = 192.168.4.2
            {
                "offset": "0038",
                "hex": "00 34 ab cd 00 00 80 06",
                "ascii": ".4......",
                "section": "packet_data",
                "annotation": "TotalLen:52 | ID | Flags | TTL:128 | Proto:06=TCP"
            },
            {
                "offset": "0040",
                "hex": "12 34 2e 69 63 a3 c0 a8",
                "ascii": ".4.ic...",
                "section": "packet_data",
                "annotation": "Chksum | [0x42] SrcIP: 2e.69.63.a3=46.105.99.163"
            },
            {
                "offset": "0048",
                "hex": "04 02 01 bb cc dd 00 00",
                "ascii": "........",
                "section": "packet_data",
                "annotation": "[0x46] DstIP: c0.a8.04.02=192.168.4.2 | TCP..."
            },

            # === TCP Header (20 bytes: starts 0x4A) ===
            {
                "offset": "0050",
                "hex": "00 01 5e 2c 77 0d 00 00",
                "ascii": "..^,w...",
                "section": "packet_data",
                "annotation": "DstPort:52445 | Seq number..."
            },
            {
                "offset": "0058",
                "hex": "00 00 50 10 ff ff a8 ee",
                "ascii": "..P.....",
                "section": "packet_data",
                "annotation": "Ack | DataOff:5 | Flags:0x10(ACK) | Window"
            },
            {
                "offset": "0060",
                "hex": "00 00 00 00 48 54 54 50",
                "ascii": "....HTTP",
                "section": "packet_data",
                "annotation": "Checksum | UrgPtr | Payload: 'HTTP'"
            },

            # === Application Data ===
            {
                "offset": "0068",
                "hex": "2f 31 2e 1 20 32 30 30",
                "ascii": "/1.1 200",
                "section": "packet_data",
                "annotation": "HTTP Response: '/1.1 200'"
            },
        ]

        return hex_lines

    def generate_annotations(self) -> Dict:
        """Generate helpful annotations for the packet structure"""
        return {
            "pcap_header": {
                "title": "En-tete PCAP Global (24 octets)",
                "description": "Identifie le format du fichier capture",
                "fields": [
                    "Magic Number: d4 c3 b2 a1 (Little Endian)",
                    "Version: 2.4",
                    "Link-Layer: Ethernet (0x00000001)"
                ]
            },
            "packet_header": {
                "title": "En-tete de Paquet (16 octets)",
                "description": "Metadonnees pour chaque paquet capture",
                "fields": [
                    "Timestamp (secondes + microsecondes)",
                    "Taille du paquet capture",
                    "Taille originale du paquet"
                ]
            },
            "packet_data": {
                "title": "Donnees du Paquet",
                "description": "Contenu brut du paquet reseau",
                "fields": [
                    "Ethernet Header (14 octets): MAC src/dst",
                    "IP Header (20 octets): IP src/dst, TTL",
                    "TCP/UDP Header: Ports, flags, checksum"
                ]
            }
        }

    def get_correct_answers(self) -> Dict:
        """Get the correct answers for Mission 3 validation"""
        return {
            "dest_mac": "00:1e:ec:26:d2:ac",
            "src_mac": "26:02:06:49:6b:31",
            "src_ip": "46.105.99.163",
            "dest_ip": "192.168.4.2",
            "timestamp": "15/06/2024 14:32:18",
            "packet_length": "66",
            "protocol": "TCP",
            "link_type": "Ethernet"
        }

    def draw_back_button(self, mouse_pos):
        """Draw the clickable back button to return to Packet Lab directory"""
        # Button dimensions
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_x = self.screen_width - button_width - int(25 * self.scale_x)  # Right side
        button_y = (int(70 * self.scale_y) - button_height) // 2  # Centered in header

        # Create button rect
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Check if hovered
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)

        # Button background
        button_bg = self.button_hover if is_hovered else self.button_bg
        pygame.draw.rect(self.screen, button_bg, self.back_button_rect, border_radius=int(8 * self.scale))

        # Button border
        border_color = self.success_color if is_hovered else self.primary_color
        pygame.draw.rect(self.screen, border_color, self.back_button_rect, width=2, border_radius=int(8 * self.scale))

        # Button text
        back_text = self.body_font.render("RETOUR", True, self.text_color)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_rect)

        # Return hover state for cursor change
        return is_hovered

    def draw(self):
        """Draw the PCAP Analyzer interface"""
        self.screen.fill(self.bg_color)

        # Header - larger for bigger fonts
        header_height = int(70 * self.scale_y)
        pygame.draw.rect(self.screen, self.header_bg, (0, 0, self.screen_width, header_height))

        # Title
        title = self.title_font.render("PCAP Analyzer - Analyse de Fichier", True, self.primary_color)
        self.screen.blit(title, (int(25 * self.scale_x), header_height // 2 - title.get_height() // 2))

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Draw back button to return to Packet Lab directory
        is_back_hovered = self.draw_back_button(mouse_pos)

        # Change cursor if hovering back button
        if is_back_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # File info bar - larger
        info_y = header_height
        info_height = int(45 * self.scale_y)
        pygame.draw.rect(self.screen, (30, 25, 45), (0, info_y, self.screen_width, info_height))

        file_info = self.body_font.render("Fichier: capture_suspect.pcap | Taille: 144 octets | Paquets: 2", True, self.dim_color)
        self.screen.blit(file_info, (int(25 * self.scale_x), info_y + info_height // 2 - file_info.get_height() // 2))

        # Main content area - split into hex view and legend
        content_y = info_y + info_height + int(10 * self.scale_y)
        content_height = self.screen_height - content_y - int(50 * self.scale_y)

        # Hex view panel (left side - 70%)
        hex_panel_width = int(self.screen_width * 0.68)
        hex_panel_rect = pygame.Rect(int(15 * self.scale_x), content_y, hex_panel_width, content_height)
        pygame.draw.rect(self.screen, self.hex_bg, hex_panel_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, hex_panel_rect, width=2, border_radius=int(8 * self.scale))

        # Hex column headers - wider spacing for larger fonts
        hex_header_y = content_y + int(15 * self.scale_y)
        col_offset_x = hex_panel_rect.x + int(20 * self.scale_x)
        col_hex_x = col_offset_x + int(90 * self.scale_x)
        col_ascii_x = col_hex_x + int(280 * self.scale_x)
        col_annot_x = col_ascii_x + int(120 * self.scale_x)

        offset_header = self.body_font.render("Offset", True, self.dim_color)
        hex_header = self.body_font.render("Hex", True, self.dim_color)
        ascii_header = self.body_font.render("ASCII", True, self.dim_color)
        annot_header = self.body_font.render("Annotation", True, self.dim_color)

        self.screen.blit(offset_header, (col_offset_x, hex_header_y))
        self.screen.blit(hex_header, (col_hex_x, hex_header_y))
        self.screen.blit(ascii_header, (col_ascii_x, hex_header_y))
        self.screen.blit(annot_header, (col_annot_x, hex_header_y))

        # Draw separator line
        sep_y = hex_header_y + offset_header.get_height() + int(8 * self.scale_y)
        pygame.draw.line(self.screen, self.dim_color, (hex_panel_rect.x + 10, sep_y), (hex_panel_rect.right - 10, sep_y), 1)

        # Draw hex lines - larger line height
        line_y = sep_y + int(12 * self.scale_y)
        line_height = int(42 * self.scale_y)

        visible_lines = self.hex_data[self.scroll_offset:self.scroll_offset + self.max_visible_lines]

        for i, line in enumerate(visible_lines):
            current_y = line_y + i * line_height

            # Get section color
            section = line.get("section", "")
            if section == "pcap_header":
                section_color = self.pcap_header_color
            elif section == "packet_header":
                section_color = self.packet_header_color
            elif section == "packet_data":
                section_color = self.packet_data_color
            else:
                section_color = self.text_color

            # Section indicator (colored bar on left)
            indicator_rect = pygame.Rect(hex_panel_rect.x + 5, current_y, 4, line_height - 4)
            pygame.draw.rect(self.screen, section_color, indicator_rect)

            # Offset
            offset_text = self.mono_font.render(line["offset"], True, self.dim_color)
            self.screen.blit(offset_text, (col_offset_x, current_y))

            # Hex bytes
            hex_text = self.mono_font.render(line["hex"], True, section_color)
            self.screen.blit(hex_text, (col_hex_x, current_y))

            # ASCII
            ascii_text = self.mono_font.render(line["ascii"], True, self.dim_color)
            self.screen.blit(ascii_text, (col_ascii_x, current_y))

            # Annotation
            annot_text = self.small_font.render(line.get("annotation", ""), True, self.annotation_color)
            self.screen.blit(annot_text, (col_annot_x, current_y))

        # Legend panel (right side - 30%)
        legend_x = hex_panel_rect.right + int(15 * self.scale_x)
        legend_width = self.screen_width - legend_x - int(15 * self.scale_x)
        legend_rect = pygame.Rect(legend_x, content_y, legend_width, content_height)
        pygame.draw.rect(self.screen, self.panel_bg, legend_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, legend_rect, width=2, border_radius=int(8 * self.scale))

        # Legend title
        legend_title = self.heading_font.render("Legende", True, self.primary_color)
        self.screen.blit(legend_title, (legend_x + int(15 * self.scale_x), content_y + int(15 * self.scale_y)))

        # Legend items - larger spacing
        legend_y = content_y + int(60 * self.scale_y)
        legend_items = [
            (self.pcap_header_color, "En-tete PCAP", "Format du fichier"),
            (self.packet_header_color, "En-tete Paquet", "Timestamp + taille"),
            (self.packet_data_color, "Donnees Paquet", "Ethernet + IP + TCP"),
        ]

        for color, title, desc in legend_items:
            # Color indicator - larger
            color_rect = pygame.Rect(legend_x + int(15 * self.scale_x), legend_y, int(24 * self.scale_x), int(24 * self.scale_y))
            pygame.draw.rect(self.screen, color, color_rect, border_radius=4)

            # Title
            item_title = self.body_font.render(title, True, self.text_color)
            self.screen.blit(item_title, (legend_x + int(50 * self.scale_x), legend_y))

            # Description
            item_desc = self.small_font.render(desc, True, self.dim_color)
            self.screen.blit(item_desc, (legend_x + int(50 * self.scale_x), legend_y + item_title.get_height() + 4))

            legend_y += int(70 * self.scale_y)

        # Extraction hints
        hints_y = legend_y + int(15 * self.scale_y)
        hints_title = self.heading_font.render("A Extraire:", True, self.warning_color)
        self.screen.blit(hints_title, (legend_x + int(15 * self.scale_x), hints_y))

        hints = [
            "- MAC destination",
            "- MAC source",
            "- IP source",
            "- IP destination",
            "- Protocole",
            "- Taille paquet"
        ]

        hint_y = hints_y + int(40 * self.scale_y)
        for hint in hints:
            hint_text = self.small_font.render(hint, True, self.text_color)
            self.screen.blit(hint_text, (legend_x + int(15 * self.scale_x), hint_y))
            hint_y += int(28 * self.scale_y)

        # Action buttons (GUIDE D'EXTRACTION, DECODEURS, RAPPORT) - Now all together
        btn_width = legend_width - int(30 * self.scale_x)
        btn_height = int(40 * self.scale_y)
        btn_spacing = int(10 * self.scale_y)

        # GUIDE D'EXTRACTION button
        guide_btn_y = hint_y + int(15 * self.scale_y)
        self.guide_button_rect = pygame.Rect(
            legend_x + int(15 * self.scale_x),
            guide_btn_y,
            btn_width,
            btn_height
        )

        is_guide_hovered = self.guide_button_rect.collidepoint(mouse_pos)
        guide_bg = (80, 100, 60) if is_guide_hovered else (55, 75, 45)
        pygame.draw.rect(self.screen, guide_bg, self.guide_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.success_color, self.guide_button_rect, width=2, border_radius=int(8 * self.scale))

        guide_text = self.body_font.render("GUIDE D'EXTRACTION", True, self.text_color)
        guide_text_rect = guide_text.get_rect(center=self.guide_button_rect.center)
        self.screen.blit(guide_text, guide_text_rect)

        # DECODEURS button
        decoder_btn_y = guide_btn_y + btn_height + btn_spacing
        self.decoder_button_rect = pygame.Rect(
            legend_x + int(15 * self.scale_x),
            decoder_btn_y,
            btn_width,
            btn_height
        )

        is_decoder_hovered = self.decoder_button_rect.collidepoint(mouse_pos)
        decoder_bg = (100, 80, 60) if is_decoder_hovered else (75, 55, 45)
        pygame.draw.rect(self.screen, decoder_bg, self.decoder_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.warning_color, self.decoder_button_rect, width=2, border_radius=int(8 * self.scale))

        decoder_text = self.body_font.render("DECODEURS", True, self.text_color)
        decoder_text_rect = decoder_text.get_rect(center=self.decoder_button_rect.center)
        self.screen.blit(decoder_text, decoder_text_rect)

        # RAPPORT button (moved here to be with other buttons)
        rapport_btn_y = decoder_btn_y + btn_height + btn_spacing
        self.notes_button_rect = pygame.Rect(
            legend_x + int(15 * self.scale_x),
            rapport_btn_y,
            btn_width,
            btn_height
        )

        is_notes_hovered = self.notes_button_rect.collidepoint(mouse_pos)
        rapport_bg = (80, 60, 100) if is_notes_hovered else (55, 40, 85)
        pygame.draw.rect(self.screen, rapport_bg, self.notes_button_rect, border_radius=int(8 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, self.notes_button_rect, width=2, border_radius=int(8 * self.scale))

        rapport_text = self.body_font.render("RAPPORT", True, self.text_color)
        rapport_text_rect = rapport_text.get_rect(center=self.notes_button_rect.center)
        self.screen.blit(rapport_text, rapport_text_rect)

        # Status bar - larger
        status_y = self.screen_height - int(50 * self.scale_y)
        pygame.draw.rect(self.screen, self.header_bg, (0, status_y, self.screen_width, int(50 * self.scale_y)))

        # Update status text (remove ESC instructions since we have back button)
        status_text = self.body_font.render("Fleches: Defiler | GUIDE: Aide | RAPPORT: Soumettre", True, self.dim_color)
        self.screen.blit(status_text, (int(25 * self.scale_x), status_y + int(12 * self.scale_y)))

        # Draw guide popup if active
        if self.show_guide_popup:
            self.draw_guide_popup()

        # Draw decoder popup if active
        if self.show_decoder_popup:
            self.draw_decoder_popup()

    def draw_decoder_popup(self):
        """Draw the decoder tools popup overlay"""
        mouse_pos = pygame.mouse.get_pos()

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Popup dimensions
        popup_width = int(600 * self.scale_x)  # Wider for decoder names
        popup_height = int(500 * self.scale_y)  # Taller for input/output
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2

        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Draw popup background
        pygame.draw.rect(self.screen, (30, 25, 45), popup_rect, border_radius=int(12 * self.scale))
        pygame.draw.rect(self.screen, self.warning_color, popup_rect, width=3, border_radius=int(12 * self.scale))

        # Title
        title = self.title_font.render("DECODEURS", True, self.warning_color)
        title_rect = title.get_rect(centerx=popup_rect.centerx, top=popup_y + int(15 * self.scale_y))
        self.screen.blit(title, title_rect)

        # Close button (X)
        close_btn_size = int(30 * self.scale)
        close_btn_x = popup_rect.right - close_btn_size - int(15 * self.scale_x)
        close_btn_y = popup_rect.top + int(15 * self.scale_y)
        self.decoder_close_btn_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.decoder_close_btn_rect.collidepoint(mouse_pos)
        btn_color = (200, 50, 50) if is_hovered else (150, 40, 40)
        pygame.draw.rect(self.screen, btn_color, self.decoder_close_btn_rect, border_radius=int(5 * self.scale))
        
        # Draw X
        start_pos1 = (self.decoder_close_btn_rect.left + 8, self.decoder_close_btn_rect.top + 8)
        end_pos1 = (self.decoder_close_btn_rect.right - 8, self.decoder_close_btn_rect.bottom - 8)
        pygame.draw.line(self.screen, (255, 255, 255), start_pos1, end_pos1, 2)
        start_pos2 = (self.decoder_close_btn_rect.left + 8, self.decoder_close_btn_rect.bottom - 8)
        end_pos2 = (self.decoder_close_btn_rect.right - 8, self.decoder_close_btn_rect.top + 8)
        pygame.draw.line(self.screen, (255, 255, 255), start_pos2, end_pos2, 2)

        # Decoder dropdown
        dropdown_y = title_rect.bottom + int(20 * self.scale_y)
        dropdown_width = popup_width - int(60 * self.scale_x)
        dropdown_height = int(40 * self.scale_y)
        dropdown_x = popup_x + int(30 * self.scale_x)

        # Dropdown label
        dropdown_label = self.body_font.render("Choisir un decodeur:", True, self.text_color)
        self.screen.blit(dropdown_label, (dropdown_x, dropdown_y))

        # Dropdown button
        dropdown_btn_y = dropdown_y + dropdown_label.get_height() + int(8 * self.scale_y)
        dropdown_btn_rect = pygame.Rect(dropdown_x, dropdown_btn_y, dropdown_width, dropdown_height)

        is_dropdown_hovered = dropdown_btn_rect.collidepoint(mouse_pos)
        dropdown_bg = (50, 45, 65) if is_dropdown_hovered or self.decoder_dropdown_open else (40, 35, 55)
        pygame.draw.rect(self.screen, dropdown_bg, dropdown_btn_rect, border_radius=int(6 * self.scale))
        pygame.draw.rect(self.screen, self.warning_color if self.decoder_dropdown_open else self.dim_color, dropdown_btn_rect, width=2, border_radius=int(6 * self.scale))

        # Selected decoder text
        selected_name = "-- Selectionnez --"
        if self.decoder_selected:
            for d in self.decoders:
                if d["id"] == self.decoder_selected:
                    selected_name = d["name"]
                    break

        selected_text = self.body_font.render(selected_name, True, self.text_color)
        self.screen.blit(selected_text, (dropdown_x + int(15 * self.scale_x), dropdown_btn_y + dropdown_height // 2 - selected_text.get_height() // 2))

        # Arrow indicator
        arrow = self.body_font.render("v" if not self.decoder_dropdown_open else "^", True, self.dim_color)
        self.screen.blit(arrow, (dropdown_x + dropdown_width - int(30 * self.scale_x), dropdown_btn_y + dropdown_height // 2 - arrow.get_height() // 2))

        # Store dropdown button rect for click detection
        self.decoder_dropdown_rect = dropdown_btn_rect

        # Dropdown menu (if open)
        self.decoder_rects = {}
        if self.decoder_dropdown_open:
            menu_y = dropdown_btn_y + dropdown_height
            menu_height = len(self.decoders) * int(45 * self.scale_y)  # Taller for longer names
            menu_rect = pygame.Rect(dropdown_x, menu_y, dropdown_width, menu_height)
            pygame.draw.rect(self.screen, (45, 40, 60), menu_rect, border_radius=int(6 * self.scale))
            pygame.draw.rect(self.screen, self.dim_color, menu_rect, width=1, border_radius=int(6 * self.scale))

            for i, decoder in enumerate(self.decoders):
                item_y = menu_y + i * int(45 * self.scale_y)
                item_rect = pygame.Rect(dropdown_x, item_y, dropdown_width, int(45 * self.scale_y))
                self.decoder_rects[decoder["id"]] = item_rect

                is_item_hovered = item_rect.collidepoint(mouse_pos)
                if is_item_hovered:
                    pygame.draw.rect(self.screen, (60, 55, 80), item_rect)

                item_text = self.small_font.render(decoder["name"], True, self.warning_color if is_item_hovered else self.text_color)
                self.screen.blit(item_text, (dropdown_x + int(15 * self.scale_x), item_y + int(12 * self.scale_y)))

        # Input/Output section (only if decoder selected)
        if self.decoder_selected and not self.decoder_dropdown_open:
            io_y = dropdown_btn_y + dropdown_height + int(30 * self.scale_y)

            # Input label
            input_label = self.body_font.render("Entree:", True, self.text_color)
            self.screen.blit(input_label, (dropdown_x, io_y))

            # Input field
            input_field_y = io_y + input_label.get_height() + int(8 * self.scale_y)
            input_field_rect = pygame.Rect(dropdown_x, input_field_y, dropdown_width, int(40 * self.scale_y))
            self.decoder_input_rect = input_field_rect

            input_bg = (50, 45, 65) if self.decoder_input_active else (40, 35, 55)
            pygame.draw.rect(self.screen, input_bg, input_field_rect, border_radius=int(6 * self.scale))
            pygame.draw.rect(self.screen, self.primary_color if self.decoder_input_active else self.dim_color, input_field_rect, width=2, border_radius=int(6 * self.scale))

            # Input text or placeholder
            input_display = self.decoder_input if self.decoder_input else self.get_decoder_placeholder()
            input_color = self.text_color if self.decoder_input else self.dim_color
            input_text = self.body_font.render(input_display[:40], True, input_color)
            self.screen.blit(input_text, (dropdown_x + int(15 * self.scale_x), input_field_y + int(10 * self.scale_y)))

            # Cursor blink for active input
            if self.decoder_input_active and pygame.time.get_ticks() % 1000 < 500:
                cursor_x = dropdown_x + int(15 * self.scale_x) + input_text.get_width() + 5
                cursor_y = input_field_y + int(10 * self.scale_y)
                cursor_height = input_text.get_height()
                pygame.draw.line(self.screen, self.primary_color,
                               (cursor_x, cursor_y),
                               (cursor_x, cursor_y + cursor_height), 2)

            # Output label
            output_y = input_field_y + int(55 * self.scale_y)
            output_label = self.body_font.render("Resultat:", True, self.text_color)
            self.screen.blit(output_label, (dropdown_x, output_y))

            # Output field
            output_field_y = output_y + output_label.get_height() + int(8 * self.scale_y)
            output_field_rect = pygame.Rect(dropdown_x, output_field_y, dropdown_width, int(60 * self.scale_y))

            pygame.draw.rect(self.screen, (35, 30, 50), output_field_rect, border_radius=int(6 * self.scale))
            pygame.draw.rect(self.screen, self.success_color, output_field_rect, width=2, border_radius=int(6 * self.scale))

            # Output text
            output_text = self.body_font.render(self.decoder_output if self.decoder_output else "...", True, self.success_color if self.decoder_output else self.dim_color)
            self.screen.blit(output_text, (dropdown_x + int(15 * self.scale_x), output_field_y + int(15 * self.scale_y)))

            # Hint for current decoder
            hint_y = output_field_y + int(75 * self.scale_y)
            hint_text = self.get_decoder_hint()
            hint_surface = self.small_font.render(hint_text, True, self.dim_color)
            self.screen.blit(hint_surface, (dropdown_x, hint_y))

            # Example text
            example_y = hint_y + int(25 * self.scale_y)
            example_text = self.get_decoder_example()
            example_surface = self.small_font.render(f"Exemple: {example_text}", True, self.warning_color)
            self.screen.blit(example_surface, (dropdown_x, example_y))

    def get_decoder_placeholder(self) -> str:
        """Get placeholder text for current decoder"""
        placeholders = {
            "hex_dec": "Ex: 2e ou a3 (hexadecimal sans 0x)",
            "hex_ip": "Ex: 2e 69 63 a3 (4 octets separes par espaces)",
            "mac_format": "Ex: 00 1e ec 26 d2 ac (6 octets)",
            "endian": "Ex: 42 00 00 00 (little endian -> big endian)",
            "protocol": "Ex: 06 ou 11 (numero decimal ou hex)",
        }
        return placeholders.get(self.decoder_selected, "Entrez une valeur...")

    def get_decoder_hint(self) -> str:
        """Get hint text for current decoder"""
        hints = {
            "hex_dec": "Convertit un octet hex en decimal (0-255)",
            "hex_ip": "Convertit 4 octets hex en adresse IP (dotted decimal)",
            "mac_format": "Formate 6 octets hex en adresse MAC (XX:XX:XX:XX:XX:XX)",
            "endian": "Inverse l'ordre des octets (Little Endian -> Big Endian)",
            "protocol": "Numero de protocole IP: 06=TCP, 11=UDP, 01=ICMP",
        }
        return hints.get(self.decoder_selected, "")

    def get_decoder_example(self) -> str:
        """Get example for current decoder"""
        examples = {
            "hex_dec": "2e -> 46",
            "hex_ip": "2e 69 63 a3 -> 46.105.99.163",
            "mac_format": "00 1e ec 26 d2 ac -> 00:1e:ec:26:d2:ac",
            "endian": "42 00 00 00 -> 00 00 00 42 = 66",
            "protocol": "06 -> TCP",
        }
        return examples.get(self.decoder_selected, "")

    def decode_value(self):
        """Decode the input value based on selected decoder"""
        if not self.decoder_input or not self.decoder_selected:
            self.decoder_output = ""
            return

        try:
            input_val = self.decoder_input.strip().lower()

            if self.decoder_selected == "hex_dec":
                # Hex to decimal - single or multiple bytes
                bytes_list = input_val.replace(":", " ").replace("-", " ").replace(".", " ").split()
                if not bytes_list:
                    self.decoder_output = "Erreur: entrez une valeur hex"
                    return
                    
                if len(bytes_list) == 1:
                    hex_val = bytes_list[0]
                    # Remove 0x prefix if present
                    if hex_val.startswith("0x"):
                        hex_val = hex_val[2:]
                    decimal = int(hex_val, 16)
                    self.decoder_output = f"{hex_val} = {decimal}"
                else:
                    decimals = []
                    for b in bytes_list:
                        if b.startswith("0x"):
                            b = b[2:]
                        decimals.append(str(int(b, 16)))
                    self.decoder_output = " | ".join(decimals)

            elif self.decoder_selected == "hex_ip":
                # Hex to IP address
                bytes_list = input_val.replace(":", " ").replace("-", " ").replace(".", " ").split()
                if len(bytes_list) < 4:
                    self.decoder_output = "Erreur: besoin de 4 octets hex"
                    return
                    
                ip_parts = []
                for b in bytes_list[:4]:
                    if b.startswith("0x"):
                        b = b[2:]
                    ip_parts.append(str(int(b, 16)))
                self.decoder_output = ".".join(ip_parts)

            elif self.decoder_selected == "mac_format":
                # Format MAC address
                bytes_list = input_val.replace(":", " ").replace("-", " ").replace(".", " ").split()
                if len(bytes_list) < 6:
                    self.decoder_output = "Erreur: besoin de 6 octets hex"
                    return
                    
                mac_parts = []
                for b in bytes_list[:6]:
                    if b.startswith("0x"):
                        b = b[2:]
                    mac_parts.append(b.zfill(2))
                self.decoder_output = ":".join(mac_parts)

            elif self.decoder_selected == "endian":
                # Endianness swap
                bytes_list = input_val.replace(":", " ").replace("-", " ").replace(".", " ").split()
                if not bytes_list:
                    self.decoder_output = "Erreur: entrez des valeurs hex"
                    return
                    
                # Clean bytes (remove 0x prefix)
                clean_bytes = []
                for b in bytes_list:
                    if b.startswith("0x"):
                        clean_bytes.append(b[2:].zfill(2))
                    else:
                        clean_bytes.append(b.zfill(2))
                
                reversed_bytes = clean_bytes[::-1]
                hex_str = "".join(reversed_bytes)
                decimal_val = int(hex_str, 16)
                self.decoder_output = f"{' '.join(reversed_bytes)} (0x{hex_str}) = {decimal_val}"

            elif self.decoder_selected == "protocol":
                # Protocol number lookup
                proto_val = input_val.replace(" ", "")
                if proto_val.startswith("0x"):
                    proto_num = int(proto_val[2:], 16)
                else:
                    try:
                        proto_num = int(proto_val, 16)  # Try hex first
                    except:
                        proto_num = int(proto_val)  # Try decimal
                
                protocols = {
                    1: "ICMP (Internet Control Message Protocol)",
                    6: "TCP (Transmission Control Protocol)",
                    17: "UDP (User Datagram Protocol)",
                    2: "IGMP (Internet Group Management Protocol)",
                    47: "GRE (Generic Routing Encapsulation)",
                    50: "ESP (Encapsulating Security Payload)",
                    51: "AH (Authentication Header)",
                    89: "OSPF (Open Shortest Path First)",
                }
                proto_name = protocols.get(proto_num, f"Inconnu (numero: {proto_num})")
                self.decoder_output = f"{proto_num} = {proto_name}"

        except ValueError as e:
            self.decoder_output = f"Erreur: valeur hex invalide"
        except Exception as e:
            self.decoder_output = f"Erreur: {str(e)[:30]}"

    def draw_guide_popup(self):
        """Draw the extraction guide popup overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Popup dimensions - larger to fit all 8 fields
        popup_width = int(1000 * self.scale_x)
        popup_height = int(850 * self.scale_y)
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2

        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Draw popup background
        pygame.draw.rect(self.screen, (25, 20, 40), popup_rect, border_radius=int(12 * self.scale))
        pygame.draw.rect(self.screen, self.primary_color, popup_rect, width=3, border_radius=int(12 * self.scale))

        # Title
        title = self.title_font.render("GUIDE D'EXTRACTION - RAPPORT", True, self.primary_color)
        title_rect = title.get_rect(centerx=popup_rect.centerx, top=popup_y + int(15 * self.scale_y))
        self.screen.blit(title, title_rect)

        # Close button (X)
        close_btn_size = int(30 * self.scale)
        close_btn_x = popup_rect.right - close_btn_size - int(15 * self.scale_x)
        close_btn_y = popup_rect.top + int(15 * self.scale_y)
        self.guide_close_btn_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.guide_close_btn_rect.collidepoint(mouse_pos)
        btn_color = (200, 50, 50) if is_hovered else (150, 40, 40)
        pygame.draw.rect(self.screen, btn_color, self.guide_close_btn_rect, border_radius=int(5 * self.scale))
        
        # Draw X
        start_pos1 = (self.guide_close_btn_rect.left + 8, self.guide_close_btn_rect.top + 8)
        end_pos1 = (self.guide_close_btn_rect.right - 8, self.guide_close_btn_rect.bottom - 8)
        pygame.draw.line(self.screen, (255, 255, 255), start_pos1, end_pos1, 2)
        start_pos2 = (self.guide_close_btn_rect.left + 8, self.guide_close_btn_rect.bottom - 8)
        end_pos2 = (self.guide_close_btn_rect.right - 8, self.guide_close_btn_rect.top + 8)
        pygame.draw.line(self.screen, (255, 255, 255), start_pos2, end_pos2, 2)

        # Guide content - All 8 report fields explained simply
        guide_items = [
            {
                "title": "1. MAC Destination",
                "color": self.packet_data_color,
                "where": "Offset 0x28 (6 octets)",
                "how": "Lire les 6 premiers octets des donnees",
                "format": "Separer par ':' -> XX:XX:XX:XX:XX:XX"
            },
            {
                "title": "2. MAC Source",
                "color": self.packet_data_color,
                "where": "Offset 0x2E (6 octets)",
                "how": "6 octets juste apres MAC Dest",
                "format": "Meme format -> XX:XX:XX:XX:XX:XX"
            },
            {
                "title": "3. IP Source",
                "color": self.annotation_color,
                "where": "Offset 0x42 (4 octets)",
                "how": "Convertir hex -> decimal",
                "format": "2e=46, 69=105, 63=99, a3=163"
            },
            {
                "title": "4. IP Destination",
                "color": self.annotation_color,
                "where": "Offset 0x46 (4 octets)",
                "how": "4 octets apres IP Source",
                "format": "c0=192, a8=168, 04=4, 02=2"
            },
            {
                "title": "5. Taille Paquet",
                "color": self.packet_header_color,
                "where": "Offset 0x20 (en-tete paquet)",
                "how": "Lire en Little Endian",
                "format": "42 00 00 00 = 0x42 = 66 octets"
            },
            {
                "title": "6. Protocole",
                "color": self.warning_color,
                "where": "Offset 0x3F (1 octet)",
                "how": "06=TCP, 11=UDP, 01=ICMP",
                "format": "Ecrire le nom: TCP, UDP..."
            },
            {
                "title": "7. Type Liaison",
                "color": self.pcap_header_color,
                "where": "Offset 0x14 (en-tete PCAP)",
                "how": "01 00 00 00 = Ethernet",
                "format": "Ecrire: Ethernet"
            },
            {
                "title": "8. Timestamp",
                "color": self.pcap_header_color,
                "where": "Offset 0x18 (en-tete paquet)",
                "how": "Voir annotation dans le dump",
                "format": "Format: JJ/MM/AAAA"
            }
        ]

        # Draw guide items in two columns (4 items each)
        content_y = title_rect.bottom + int(30 * self.scale_y)
        col_width = (popup_width - int(50 * self.scale_x)) // 2
        left_x = popup_x + int(20 * self.scale_x)
        right_x = left_x + col_width + int(15 * self.scale_x)
        item_height = int(180 * self.scale_y)

        for i, item in enumerate(guide_items):
            # 4 items per column
            if i < 4:
                item_x = left_x
                item_y = content_y + (i * item_height)
            else:
                item_x = right_x
                item_y = content_y + ((i - 4) * item_height)

            # Item background
            item_rect = pygame.Rect(item_x, item_y, col_width - int(10 * self.scale_x), item_height - int(10 * self.scale_y))
            pygame.draw.rect(self.screen, (35, 30, 50), item_rect, border_radius=int(8 * self.scale))

            # Colored left border
            border_rect = pygame.Rect(item_x, item_y, int(5 * self.scale_x), item_height - int(10 * self.scale_y))
            pygame.draw.rect(self.screen, item["color"], border_rect, border_radius=int(3 * self.scale))

            # Title
            item_title = self.body_font.render(item["title"], True, item["color"])
            self.screen.blit(item_title, (item_x + int(15 * self.scale_x), item_y + int(10 * self.scale_y)))

            # Where
            where_label = self.small_font.render("Ou:", True, self.dim_color)
            where_value = self.small_font.render(item["where"], True, self.text_color)
            self.screen.blit(where_label, (item_x + int(15 * self.scale_x), item_y + int(45 * self.scale_y)))
            self.screen.blit(where_value, (item_x + int(55 * self.scale_x), item_y + int(45 * self.scale_y)))

            # How
            how_label = self.small_font.render("Comment:", True, self.dim_color)
            how_value = self.small_font.render(item["how"], True, self.text_color)
            self.screen.blit(how_label, (item_x + int(15 * self.scale_x), item_y + int(75 * self.scale_y)))
            self.screen.blit(how_value, (item_x + int(100 * self.scale_x), item_y + int(75 * self.scale_y)))

            # Format/Example
            format_label = self.small_font.render("Resultat:", True, self.dim_color)
            format_value = self.small_font.render(item["format"], True, self.success_color)
            self.screen.blit(format_label, (item_x + int(15 * self.scale_x), item_y + int(105 * self.scale_y)))
            self.screen.blit(format_value, (item_x + int(100 * self.scale_x), item_y + int(105 * self.scale_y)))

        # Hex conversion reminder at bottom
        reminder_y = popup_y + popup_height - int(55 * self.scale_y)
        pygame.draw.rect(self.screen, (40, 35, 55), (popup_x + int(20 * self.scale_x), reminder_y, popup_width - int(40 * self.scale_x), int(40 * self.scale_y)), border_radius=int(6 * self.scale))

        reminder_text = self.small_font.render("Rappel Hex->Dec: 0-9 = 0-9 | a=10, b=11, c=12, d=13, e=14, f=15 | Ex: 2e = 2*16+14 = 46", True, self.warning_color)
        reminder_rect = reminder_text.get_rect(center=(popup_rect.centerx, reminder_y + int(20 * self.scale_y)))
        self.screen.blit(reminder_text, reminder_rect)

    def open_notes_popup(self) -> Optional[str]:
        """Open the Mission 3 notes popup"""
        from src.ui.mission3_notes import Mission3NotesPopup

        # Capture current screen as background
        background = self.screen.copy()

        # Create and run notes popup
        notes_popup = Mission3NotesPopup(
            self.screen,
            self.profile_data,
            self.mission,
            self.notes_persisted_data
        )

        result, field_data = notes_popup.run(background)

        if result == "send":
            print("[DEBUG] Mission 3 report submitted successfully!")
            return "mission_complete"
        elif result == "close":
            self.notes_persisted_data = field_data
        elif result == "exit":
            return "exit"

        return None

    def run(self) -> str:
        """
        Run the PCAP Analyzer app

        Returns:
            "desktop", "exit", or "mission_complete"
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
                        # ESC still works for keyboard users
                        return "desktop"
                    
                    elif self.show_decoder_popup and self.decoder_input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.decoder_input = self.decoder_input[:-1]
                            self.decode_value()
                        elif event.key == pygame.K_RETURN:
                            self.decode_value()
                        elif event.key == pygame.K_SPACE:
                            self.decoder_input += " "
                            self.decode_value()
                        elif event.unicode.isprintable() and len(event.unicode) > 0:
                            self.decoder_input += event.unicode
                            self.decode_value()
                    
                    elif event.key == pygame.K_UP:
                        if not self.show_guide_popup and not self.show_decoder_popup and self.scroll_offset > 0:
                            self.scroll_offset -= 1

                    elif event.key == pygame.K_DOWN:
                        if not self.show_guide_popup and not self.show_decoder_popup and self.scroll_offset < len(self.hex_data) - self.max_visible_lines:
                            self.scroll_offset += 1

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check Back button click FIRST (to return to Packet Lab)
                        if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                            return "desktop"  # Returns to desktop, which will show Packet Lab again

                        # If guide popup is open
                        if self.show_guide_popup:
                            if self.guide_close_btn_rect and self.guide_close_btn_rect.collidepoint(event.pos):
                                self.show_guide_popup = False
                            continue
                        
                        # If decoder popup is open
                        if self.show_decoder_popup:
                            if self.decoder_close_btn_rect and self.decoder_close_btn_rect.collidepoint(event.pos):
                                self.show_decoder_popup = False
                                continue

                            # Check for dropdown button click
                            if hasattr(self, 'decoder_dropdown_rect') and self.decoder_dropdown_rect.collidepoint(event.pos):
                                self.decoder_dropdown_open = not self.decoder_dropdown_open
                                continue
                            
                            # Check for decoder item selection
                            if self.decoder_dropdown_open:
                                for decoder_id, rect in self.decoder_rects.items():
                                    if rect.collidepoint(event.pos):
                                        self.decoder_selected = decoder_id
                                        self.decoder_dropdown_open = False
                                        self.decoder_input = ""
                                        self.decoder_output = ""
                                        continue
                            
                            # Check for input field click
                            if hasattr(self, 'decoder_input_rect') and self.decoder_input_rect.collidepoint(event.pos):
                                self.decoder_input_active = True
                            else:
                                self.decoder_input_active = False
                            
                            # Continue (don't close popup on internal clicks)
                            continue
                        
                        # Check Guide button
                        if self.guide_button_rect and self.guide_button_rect.collidepoint(event.pos):
                            self.show_guide_popup = True
                            self.show_decoder_popup = False
                            self.decoder_dropdown_open = False
                            continue
                        
                        # Check Decoder button
                        if self.decoder_button_rect and self.decoder_button_rect.collidepoint(event.pos):
                            self.show_decoder_popup = True
                            self.show_guide_popup = False
                            self.decoder_dropdown_open = False
                            self.decoder_input_active = False
                            continue
                        
                        # Check RAPPORT button (now with other action buttons)
                        if self.notes_button_rect and self.notes_button_rect.collidepoint(event.pos):
                            result = self.open_notes_popup()
                            if result == "mission_complete":
                                return "mission_complete"
                            elif result == "exit":
                                return "exit"
                    
                    elif event.button == 4:  # Scroll up
                        if not self.show_guide_popup and not self.show_decoder_popup and self.scroll_offset > 0:
                            self.scroll_offset -= 1

                    elif event.button == 5:  # Scroll down
                        if not self.show_guide_popup and not self.show_decoder_popup and self.scroll_offset < len(self.hex_data) - self.max_visible_lines:
                            self.scroll_offset += 1

            self.draw()
            pygame.display.flip()

        return "desktop"