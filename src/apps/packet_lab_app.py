"""
Packet Lab App - Tools Directory for Packet Analysis
Shows downloaded packet analysis tools and allows launching them
Similar to Net Scanner but for packet/PCAP related tools
"""

import pygame
from typing import Dict, Tuple, Optional, List


class PacketLabApp:
    """
    Packet Lab application - Acts as a tools directory for packet analysis
    Shows downloaded packet analysis tools from the marketplace
    """

    def __init__(self, screen, profile_data: Dict):
        """
        Initialize Packet Lab

        Args:
            screen: Pygame screen surface
            profile_data: Player profile with downloaded_tools list
        """
        self.screen = screen
        self.profile_data = profile_data
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Scaling
        self.scale_x = self.screen_width / 1920
        self.scale_y = self.screen_height / 1080
        self.scale = min(self.scale_x, self.scale_y)

        # Colors - Purple theme for packet analysis
        self.bg_color = (20, 15, 30)
        self.panel_bg = (30, 25, 45)
        self.header_bg = (25, 20, 40)
        self.primary_color = (180, 130, 255)  # Purple
        self.success_color = (100, 220, 100)
        self.text_color = (220, 215, 230)
        self.dim_color = (120, 115, 140)
        self.hover_color = (45, 38, 65)
        self.button_bg = (50, 40, 70)
        self.button_hover = (70, 60, 100)

        # Fonts - Standardized sizes (matching desktop)
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()

        try:
            self.title_font = settings.get_scaled_font(int(42 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.heading_font = settings.get_scaled_font(int(32 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.body_font = settings.get_scaled_font(int(26 * self.scale), "assets/fonts/Cyberpunk.ttf")
            self.small_font = settings.get_scaled_font(int(22 * self.scale), "assets/fonts/Cyberpunk.ttf")
        except:
            self.title_font = settings.get_scaled_font(int(42 * self.scale))
            self.heading_font = settings.get_scaled_font(int(32 * self.scale))
            self.body_font = settings.get_scaled_font(int(26 * self.scale))
            self.small_font = settings.get_scaled_font(int(22 * self.scale))

        # Packet analysis tool definitions - PCAP file analysis tools
        # Wireshark is in Net Scanner for live capture
        self.all_tools = {
            "pcap_analyzer": {
                "name": "PCAP Analyzer",
                "icon": "P",
                "description": "Analyseur de fichiers PCAP bruts",
                "app_id": "pcap_analyzer"
            },
            "tcpdump": {
                "name": "TCPDump",
                "icon": "T",
                "description": "Capture de paquets en ligne",
                "app_id": "tcpdump"
            },
            "netflow": {
                "name": "NetFlow Analyzer",
                "icon": "N",
                "description": "Analyse de flux reseau",
                "app_id": "netflow"
            }
        }

        self.tool_rects = {}
        self.selected_tool = None
        self.back_button_rect = None  # Store the back button rectangle

    def get_downloaded_tools(self) -> List[str]:
        """Get list of downloaded packet analysis tool IDs"""
        downloaded = self.profile_data.get('downloaded_tools', [])
        # Filter to only packet file analysis tools (not Wireshark - that's in Net Scanner)
        packet_tools = ["pcap_analyzer", "tcpdump", "netflow"]
        return [t for t in downloaded if t in packet_tools]

    def draw_back_button(self, mouse_pos):
        """Draw the clickable back button"""
        # Button dimensions
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_x = self.screen_width - button_width - int(30 * self.scale_x)
        button_y = (int(70 * self.scale_y) - button_height) // 2  # Centered vertically in header

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
        """Draw the Packet Lab interface"""
        self.screen.fill(self.bg_color)

        # Header bar
        header_height = int(70 * self.scale_y)
        header_rect = pygame.Rect(0, 0, self.screen_width, header_height)
        pygame.draw.rect(self.screen, self.header_bg, header_rect)
        pygame.draw.line(self.screen, self.primary_color, (0, header_height), (self.screen_width, header_height), 2)

        # Title
        title = self.title_font.render("PACKET LAB - OUTILS D'ANALYSE", True, self.primary_color)
        self.screen.blit(title, (int(30 * self.scale_x), header_height // 2 - title.get_height() // 2))

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Draw back button (replaces ESC instructions)
        is_back_hovered = self.draw_back_button(mouse_pos)

        # Change cursor if hovering back button
        if is_back_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Content area
        content_y = header_height + int(25 * self.scale_y)
        content_x = int(50 * self.scale_x)
        content_width = self.screen_width - int(100 * self.scale_x)

        # Section: Installed Tools
        section_title = self.heading_font.render("Outils Installes", True, self.success_color)
        self.screen.blit(section_title, (content_x, content_y))

        downloaded = self.get_downloaded_tools()
        tools_y = content_y + int(60 * self.scale_y)

        self.tool_rects = {}

        if not downloaded:
            # No tools message
            no_tools_text = self.body_font.render("Aucun outil d'analyse installe.", True, self.dim_color)
            self.screen.blit(no_tools_text, (content_x, tools_y))

            hint_text = self.small_font.render("Visitez le Marketplace pour telecharger des outils.", True, self.dim_color)
            self.screen.blit(hint_text, (content_x, tools_y + int(40 * self.scale_y)))

            hint_text2 = self.small_font.render("Navigateur > Market > PCAP Analyzer", True, self.primary_color)
            self.screen.blit(hint_text2, (content_x, tools_y + int(75 * self.scale_y)))
        else:
            # Draw tool grid (like a file browser)
            tool_width = int(260 * self.scale_x)
            tool_height = int(220 * self.scale_y)
            spacing = int(40 * self.scale_x)
            cols = max(1, (content_width + spacing) // (tool_width + spacing))

            for i, tool_id in enumerate(downloaded):
                if tool_id not in self.all_tools:
                    continue

                tool = self.all_tools[tool_id]
                row = i // cols
                col = i % cols

                tool_x = content_x + col * (tool_width + spacing)
                tool_y_pos = tools_y + row * (tool_height + spacing)

                tool_rect = pygame.Rect(tool_x, tool_y_pos, tool_width, tool_height)
                self.tool_rects[tool_id] = tool_rect

                # Hover effect
                is_hovered = tool_rect.collidepoint(mouse_pos)
                is_selected = self.selected_tool == tool_id
                bg_color = self.hover_color if is_hovered or is_selected else self.panel_bg

                pygame.draw.rect(self.screen, bg_color, tool_rect, border_radius=int(12 * self.scale))

                # Border
                border_color = self.primary_color if is_selected else self.success_color if is_hovered else (60, 55, 80)
                pygame.draw.rect(self.screen, border_color, tool_rect, width=3, border_radius=int(12 * self.scale))

                # Icon (large letter)
                icon_text = self.title_font.render(tool['icon'], True, self.primary_color)
                icon_rect = icon_text.get_rect(centerx=tool_rect.centerx, top=tool_rect.top + int(30 * self.scale_y))
                self.screen.blit(icon_text, icon_rect)

                # Tool name
                name_text = self.body_font.render(tool['name'], True, self.text_color)
                name_rect = name_text.get_rect(centerx=tool_rect.centerx, top=icon_rect.bottom + int(20 * self.scale_y))
                self.screen.blit(name_text, name_rect)

                # Description
                desc_text = self.small_font.render(tool['description'], True, self.dim_color)
                desc_rect = desc_text.get_rect(centerx=tool_rect.centerx, top=name_rect.bottom + int(12 * self.scale_y))
                self.screen.blit(desc_text, desc_rect)

                # Launch hint
                if is_hovered:
                    launch_text = self.small_font.render("[Double-clic pour ouvrir]", True, self.success_color)
                    launch_rect = launch_text.get_rect(centerx=tool_rect.centerx, bottom=tool_rect.bottom - int(15 * self.scale_y))
                    self.screen.blit(launch_text, launch_rect)

                    # Change cursor to hand when hovering tools
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        # Footer with marketplace hint
        footer_y = self.screen_height - int(60 * self.scale_y)
        footer_text = self.small_font.render("Plus d'outils disponibles dans le Marketplace (Navigateur > Market)", True, self.dim_color)
        self.screen.blit(footer_text, (content_x, footer_y))

    def run(self) -> Tuple[str, Optional[str]]:
        """
        Run the Packet Lab app

        Returns:
            Tuple of (result, tool_id)
            result: "desktop" to return, "launch_tool" to open a tool
            tool_id: ID of tool to launch (if result is "launch_tool")
        """
        clock = pygame.time.Clock()
        running = True
        last_click_time = 0
        last_click_tool = None

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "desktop", None

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        current_time = pygame.time.get_ticks()

                        # Check back button click FIRST
                        if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                            return "desktop", None

                        # Check tool clicks
                        for tool_id, rect in self.tool_rects.items():
                            if rect.collidepoint(event.pos):
                                # Check for double click
                                if (tool_id == last_click_tool and
                                    current_time - last_click_time < 400):
                                    # Double click - launch tool
                                    return "launch_tool", tool_id

                                # Single click - select
                                self.selected_tool = tool_id
                                last_click_tool = tool_id
                                last_click_time = current_time
                                break
                        else:
                            # Clicked outside tools - deselect
                            self.selected_tool = None

            self.draw()
            pygame.display.flip()

        return "desktop", None