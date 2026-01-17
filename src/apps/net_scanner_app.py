"""
Net Scanner App - Tools Directory
Shows downloaded tools and allows launching them
"""

import pygame
from typing import Dict, Tuple, Optional, List


class NetScannerApp:
    """
    Net Scanner application - Acts as a tools directory
    Shows downloaded tools from the marketplace
    """

    def __init__(self, screen, profile_data: Dict):
        """
        Initialize Net Scanner

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

        # Colors
        self.bg_color = (15, 20, 25)
        self.panel_bg = (25, 30, 40)
        self.header_bg = (20, 25, 35)
        self.primary_color = (0, 200, 255)
        self.success_color = (0, 220, 100)
        self.text_color = (200, 200, 210)
        self.dim_color = (100, 105, 115)
        self.hover_color = (35, 40, 55)
        self.button_bg = (40, 45, 60)
        self.button_hover = (60, 65, 85)

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

        # Tool definitions - Network scanning and security tools
        # Wireshark is here for live packet capture/analysis
        # PCAP Analyzer is in Packet Lab for file analysis
        self.all_tools = {
            "wireshark": {
                "name": "Wireshark",
                "icon": "W",
                "description": "Analyseur de paquets",
                "app_id": "wireshark"
            },
            "nmap_pro": {
                "name": "Nmap Pro",
                "icon": "N",
                "description": "Scanner de ports avance",
                "app_id": "nmap_pro"
            },
            "metasploit": {
                "name": "Metasploit",
                "icon": "M",
                "description": "Framework d'exploitation",
                "app_id": "metasploit"
            },
            "burpsuite": {
                "name": "Burp Suite",
                "icon": "B",
                "description": "Proxy HTTP/HTTPS",
                "app_id": "burpsuite"
            },
            "hashcat": {
                "name": "Hashcat",
                "icon": "H",
                "description": "Cracker de mots de passe",
                "app_id": "hashcat"
            }
        }

        self.tool_rects = {}
        self.selected_tool = None
        self.back_button_rect = None  # Store the back button rectangle

    def get_downloaded_tools(self) -> List[str]:
        """Get list of downloaded tool IDs"""
        return self.profile_data.get('downloaded_tools', [])

    def draw_back_button(self, mouse_pos):
        """Draw the clickable back button"""
        # Button dimensions
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_x = self.screen_width - button_width - int(30 * self.scale_x)
        button_y = (int(60 * self.scale_y) - button_height) // 2  # Centered vertically in header

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
        """Draw the Net Scanner interface"""
        self.screen.fill(self.bg_color)

        # Header bar
        header_height = int(60 * self.scale_y)
        header_rect = pygame.Rect(0, 0, self.screen_width, header_height)
        pygame.draw.rect(self.screen, self.header_bg, header_rect)
        pygame.draw.line(self.screen, self.primary_color, (0, header_height), (self.screen_width, header_height), 2)

        # Title
        title = self.title_font.render("NET SCANNER - OUTILS", True, self.primary_color)
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
        content_y = header_height + int(20 * self.scale_y)
        content_x = int(40 * self.scale_x)
        content_width = self.screen_width - int(80 * self.scale_x)

        # Section: Installed Tools
        section_title = self.heading_font.render("Outils Installes", True, self.success_color)
        self.screen.blit(section_title, (content_x, content_y))

        downloaded = self.get_downloaded_tools()
        tools_y = content_y + int(50 * self.scale_y)

        self.tool_rects = {}

        if not downloaded:
            # No tools message
            no_tools_text = self.body_font.render("Aucun outil installe.", True, self.dim_color)
            self.screen.blit(no_tools_text, (content_x, tools_y))

            hint_text = self.small_font.render("Visitez le Marketplace dans le navigateur pour telecharger des outils.", True, self.dim_color)
            self.screen.blit(hint_text, (content_x, tools_y + int(30 * self.scale_y)))
        else:
            # Draw tool grid (like a file browser)
            tool_width = int(200 * self.scale_x)
            tool_height = int(180 * self.scale_y)
            spacing = int(30 * self.scale_x)
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

                pygame.draw.rect(self.screen, bg_color, tool_rect, border_radius=int(10 * self.scale))

                # Border
                border_color = self.primary_color if is_selected else self.success_color if is_hovered else (50, 55, 65)
                pygame.draw.rect(self.screen, border_color, tool_rect, width=2, border_radius=int(10 * self.scale))

                # Icon (large)
                icon_text = self.title_font.render(tool['icon'], True, self.text_color)
                icon_rect = icon_text.get_rect(centerx=tool_rect.centerx, top=tool_rect.top + int(25 * self.scale_y))
                self.screen.blit(icon_text, icon_rect)

                # Tool name
                name_text = self.body_font.render(tool['name'], True, self.text_color)
                name_rect = name_text.get_rect(centerx=tool_rect.centerx, top=icon_rect.bottom + int(15 * self.scale_y))
                self.screen.blit(name_text, name_rect)

                # Description
                desc_text = self.small_font.render(tool['description'], True, self.dim_color)
                desc_rect = desc_text.get_rect(centerx=tool_rect.centerx, top=name_rect.bottom + int(10 * self.scale_y))
                self.screen.blit(desc_text, desc_rect)

                # Launch hint
                if is_hovered:
                    launch_text = self.small_font.render("[Double-clic pour ouvrir]", True, self.success_color)
                    launch_rect = launch_text.get_rect(centerx=tool_rect.centerx, bottom=tool_rect.bottom - int(10 * self.scale_y))
                    self.screen.blit(launch_text, launch_rect)

                    # Change cursor to hand when hovering tools
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        # Footer with marketplace hint
        footer_y = self.screen_height - int(50 * self.scale_y)
        footer_text = self.small_font.render("Plus d'outils disponibles dans le Marketplace (Navigateur > Market)", True, self.dim_color)
        self.screen.blit(footer_text, (content_x, footer_y))

    def run(self) -> Tuple[str, Optional[str]]:
        """
        Run the Net Scanner app

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