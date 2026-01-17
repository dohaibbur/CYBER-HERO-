"""
Forum Theme - Unified color scheme for all forum/browser pages
Ensures consistent dark theme across Navigator, Forum, Profile, Auth
"""

# UNIFIED FORUM/BROWSER COLOR SCHEME
# All forum-related pages should use these colors

class ForumTheme:
    """Centralized color constants for forum browser pages"""

    # Background colors
    BG_COLOR = (12, 12, 12)           # Almost black - main background
    BROWSER_BAR = (25, 25, 25)        # Dark gray - browser chrome
    CONTENT_BG = (18, 18, 18)         # Slightly lighter black - content areas
    POST_BG = (22, 22, 22)            # Post/panel background
    INPUT_BG = (25, 25, 25)           # Input field background
    INPUT_ACTIVE = (35, 35, 35)       # Active input field
    BUTTON_BG = (30, 30, 30)          # Button background
    BUTTON_HOVER = (45, 45, 45)       # Button hover state
    HOVER_BG = (30, 30, 30)           # General hover state

    # Border colors
    BORDER_COLOR = (40, 40, 40)       # Subtle borders

    # Text colors
    TEXT_COLOR = (180, 180, 180)      # Primary gray text
    TEXT_DIM = (120, 120, 120)        # Dimmed/secondary text
    TEXT_BRIGHT = (220, 220, 220)     # Bright text (headers)

    # Accent colors
    PRIMARY_COLOR = (0, 220, 50)      # Matrix green - primary actions
    ACCENT_COLOR = (0, 180, 240)      # Cyan - secondary actions
    LINK_COLOR = (80, 150, 255)       # Blue - links
    ERROR_COLOR = (220, 50, 50)       # Red - errors
    WARNING_COLOR = (220, 180, 0)     # Gold - warnings
    SUCCESS_COLOR = (0, 200, 100)     # Green - success messages

    # Special colors
    PINNED_COLOR = (200, 50, 50)      # Red - pinned threads
    MOD_COLOR = (220, 180, 0)         # Gold - moderator badges

    @classmethod
    def apply_to(cls, obj):
        """
        Apply theme colors to an object

        Usage:
            ForumTheme.apply_to(self)
        """
        # Background colors
        obj.bg_color = cls.BG_COLOR
        obj.browser_bar = cls.BROWSER_BAR
        obj.content_bg = cls.CONTENT_BG
        obj.post_bg = cls.POST_BG
        obj.panel_bg = cls.CONTENT_BG  # Alias
        obj.input_bg = cls.INPUT_BG
        obj.input_active_bg = cls.INPUT_ACTIVE
        obj.button_bg = cls.BUTTON_BG
        obj.button_hover = cls.BUTTON_HOVER
        obj.hover_bg = cls.HOVER_BG

        # Borders
        obj.border_color = cls.BORDER_COLOR

        # Text
        obj.text_color = cls.TEXT_COLOR
        obj.text_dim = cls.TEXT_DIM
        obj.dim_text = cls.TEXT_DIM  # Alias
        obj.text_bright = cls.TEXT_BRIGHT

        # Accents
        obj.primary_color = cls.PRIMARY_COLOR
        obj.accent_color = cls.ACCENT_COLOR
        obj.link_color = cls.LINK_COLOR
        obj.error_color = cls.ERROR_COLOR
        obj.warning_color = cls.WARNING_COLOR
        obj.success_color = cls.SUCCESS_COLOR

        # Special
        obj.pinned_color = cls.PINNED_COLOR
        obj.mod_color = cls.MOD_COLOR


# Convenience function
def get_forum_colors():
    """Get forum color scheme as a dictionary"""
    return {
        'bg_color': ForumTheme.BG_COLOR,
        'browser_bar': ForumTheme.BROWSER_BAR,
        'content_bg': ForumTheme.CONTENT_BG,
        'post_bg': ForumTheme.POST_BG,
        'input_bg': ForumTheme.INPUT_BG,
        'input_active': ForumTheme.INPUT_ACTIVE,
        'button_bg': ForumTheme.BUTTON_BG,
        'button_hover': ForumTheme.BUTTON_HOVER,
        'hover_bg': ForumTheme.HOVER_BG,
        'border_color': ForumTheme.BORDER_COLOR,
        'text_color': ForumTheme.TEXT_COLOR,
        'text_dim': ForumTheme.TEXT_DIM,
        'text_bright': ForumTheme.TEXT_BRIGHT,
        'primary_color': ForumTheme.PRIMARY_COLOR,
        'accent_color': ForumTheme.ACCENT_COLOR,
        'link_color': ForumTheme.LINK_COLOR,
        'error_color': ForumTheme.ERROR_COLOR,
        'warning_color': ForumTheme.WARNING_COLOR,
        'success_color': ForumTheme.SUCCESS_COLOR,
        'pinned_color': ForumTheme.PINNED_COLOR,
        'mod_color': ForumTheme.MOD_COLOR,
    }
