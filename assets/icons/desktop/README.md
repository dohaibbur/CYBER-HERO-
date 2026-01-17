# Desktop Icons

This folder contains icon images for the interactive desktop.

## Supported Formats (in order of preference):

1. **SVG** - Vector graphics (recommended, scalable)
2. **PNG** - Raster graphics with transparency
3. **Emoji** - Automatic fallback if no file found

## Required Icons:

The system will try to load icons in this order: `{name}.svg` → `{name}.png` → emoji fallback

1. **tor_browser** (.svg or .png) - Tor Browser icon (Green theme)
2. **terminal** (.svg or .png) - Terminal/Command Line icon (Green theme)
3. **directories** (.svg or .png) - File Manager/Directories icon (Orange theme)
4. **guides** (.svg or .png) - Guides/Documentation icon (Blue theme)
5. **settings** (.svg or .png) - Settings/Configuration icon (Cyan theme)
6. **trash** (.svg or .png) - Trash/Recycle Bin icon (Red theme)
7. **notes** (.svg or .png) - Notes/Text Editor icon (Yellow theme)

## Fallback Behavior:

If an icon file is not found, the system will automatically use emoji fallbacks:
- Tor Browser: 🌐
- Terminal: 💻
- Directories: 📁
- Guides: 📖
- Settings: ⚙️
- Trash: 🗑️
- Notes: 📝

## Icon Guidelines:

### For SVG (Recommended):
- **Format**: SVG vector graphics
- **Size**: Any size (will be scaled automatically to 64x64)
- **Style**: Cyberpunk/hacker aesthetic with clean lines
- **Colors**: Match theme colors or use monochrome
- **Background**: Transparent
- **Free SVG Sources**:
  - [Heroicons](https://heroicons.com/) - MIT License
  - [Feather Icons](https://feathericons.com/) - MIT License
  - [Iconify](https://iconify.design/) - Various licenses
  - [SVG Repo](https://www.svgrepo.com/) - Various licenses

### For PNG:
- **Format**: PNG with alpha transparency
- **Size**: 64x64 pixels minimum (will be scaled)
- **Style**: Cyberpunk/hacker aesthetic
- **Colors**: Match theme colors
- **Background**: Transparent

## Installation for SVG Support:

To enable SVG icon loading, install cairosvg:
```bash
pip install cairosvg
```

If cairosvg is not installed, the system will skip SVG files and try PNG files instead.

## Color Themes:

- Tor Browser: #00ff41 (Green)
- Terminal: #00ff41 (Green)
- Directories: #ff9500 (Orange)
- Guides: #4444ff (Blue)
- Settings: #00d4ff (Cyan)
- Trash: #ff4444 (Red)
- Notes: #ffff00 (Yellow)
