"""
Notification Manager - CyberHero
Handles visual notifications for inbox and other events
File: src/systems/notification_manager.py
"""

import pygame
from typing import List, Tuple

class NotificationManager:
    """
    Manages game notifications, especially for new emails
    """

    def __init__(self):
        """Initialize notification manager"""
        self.unread_emails = 0
        self.show_notification = False
        self.notification_email_ids = []  # Track which emails are unread

        # Animation state
        self.pulse_timer = 0
        self.pulse_speed = 2.0  # Speed of pulsing animation

    def add_notification(self, email_id: str = None):
        """
        Add a new notification

        Args:
            email_id: Optional email ID to track
        """
        self.unread_emails += 1
        self.show_notification = True

        if email_id and email_id not in self.notification_email_ids:
            self.notification_email_ids.append(email_id)

    def clear_notification(self):
        """Clear the notification badge (when inbox is opened)"""
        self.show_notification = False

    def mark_email_read(self, email_id: str):
        """
        Mark a specific email as read

        Args:
            email_id: Email ID that was read
        """
        if email_id in self.notification_email_ids:
            self.notification_email_ids.remove(email_id)
            self.unread_emails = max(0, self.unread_emails - 1)

            # Hide notification if no more unread emails
            if self.unread_emails == 0:
                self.show_notification = False

    def reset_notifications(self):
        """Reset all notifications"""
        self.unread_emails = 0
        self.show_notification = False
        self.notification_email_ids = []

    def update(self, dt: float):
        """
        Update notification animations

        Args:
            dt: Delta time in seconds
        """
        if self.show_notification:
            self.pulse_timer += dt * self.pulse_speed

    def draw_badge(self, screen: pygame.Surface, icon_rect: pygame.Rect, scale: float = 1.0):
        """
        Draw notification badge on an icon

        Args:
            screen: Pygame surface to draw on
            icon_rect: Rectangle of the icon to badge
            scale: Scale factor for UI elements
        """
        if not self.show_notification or self.unread_emails == 0:
            return

        # Badge properties
        badge_size = int(24 * scale)
        badge_x = icon_rect.right - int(8 * scale)
        badge_y = icon_rect.top + int(8 * scale)

        # Pulsing effect
        import math
        pulse = abs(math.sin(self.pulse_timer))
        alpha = int(200 + 55 * pulse)  # Pulse between 200-255

        # Draw badge circle
        badge_color = (220, 20, 60)  # Crimson red
        badge_center = (badge_x, badge_y)

        # Create a surface for the badge with alpha
        badge_surface = pygame.Surface((badge_size * 2, badge_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(badge_surface, (*badge_color, alpha), (badge_size, badge_size), badge_size)

        # Draw white border
        pygame.draw.circle(badge_surface, (255, 255, 255, alpha), (badge_size, badge_size), badge_size, 2)

        # Blit to screen
        badge_rect = badge_surface.get_rect(center=badge_center)
        screen.blit(badge_surface, badge_rect)

        # Draw number if > 0
        if self.unread_emails > 0:
            font_size = int(14 * scale)
            font = pygame.font.Font(None, font_size)

            # Limit display to 9+ for large numbers
            count_text = str(self.unread_emails) if self.unread_emails < 10 else "9+"
            text_surf = font.render(count_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=badge_center)
            screen.blit(text_surf, text_rect)

    def has_unread(self) -> bool:
        """Check if there are unread notifications"""
        return self.unread_emails > 0

    def get_unread_count(self) -> int:
        """Get number of unread emails"""
        return self.unread_emails


# Global instance
_notification_manager_instance = None

def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    global _notification_manager_instance
    if _notification_manager_instance is None:
        _notification_manager_instance = NotificationManager()
    return _notification_manager_instance
