"""
Module that defines contants and helpers used by Tixel application

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in its version 3.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
"""

from enum import Enum

APP_NAME    = "Tixel"
APP_VERSION = "1.0"
FILE_EXT    = ".tixel"
FILE_TYPES  = [("Tixel project", "*.tixel"), ("All files", "*.*")]

MAX_SIZE        = 48
DEFAULT_SIZE    = 16
ANIMATION_DELAY = 150
UNDO_LIMIT      = 50

class Change:
    """
    Aspects that are dirty and must be updated by views.
    """
    PIXELS  = "pixels"
    PALETTE = "palette"
    SPRITES = "sprites"
    META    = "meta"
    PREVIEW = "preview"
    TOOL    = "tool"
    ALL     = frozenset({PIXELS, PALETTE, SPRITES, META})

class Tool(Enum):
    """
    Editing tools. The enum value is the user-visible label.
    """
    PENCIL = "Pencil"
    FILL   = "Fill"

# List of colors in Firmware order (0..26)
CPC_RGB_COLORS = [
    (0, 0, 0),          # 0  - Black
    (0, 0, 128),        # 1  - Blue
    (0, 0, 255),        # 2  - Bright Blue
    (128, 0, 0),        # 3  - Red
    (128, 0, 128),      # 4  - Magenta
    (128, 0, 255),      # 5  - Mauve
    (255, 0, 0),        # 6  - Bright Red
    (255, 0, 128),      # 7  - Purple
    (255, 0, 255),      # 8  - Bright Magenta
    (0, 128, 0),        # 9  - Green
    (0, 128, 128),      # 10 - Cyan
    (0, 128, 255),      # 11 - Sky Blue
    (128, 128, 0),      # 12 - Yellow
    (128, 128, 128),    # 13 - White
    (128, 128, 255),    # 14 - Pastel Blue
    (255, 128, 0),      # 15 - Orange
    (255, 128, 128),    # 16 - Pink
    (255, 128, 255),    # 17 - Pastel Magenta
    (0, 255, 0),        # 18 - Bright Green
    (0, 255, 128),      # 19 - Sea Green
    (0, 255, 255),      # 20 - Bright Cyan
    (128, 255, 0),      # 21 - Lime
    (128, 255, 128),    # 22 - Pastel Green
    (128, 255, 255),    # 23 - Pastel Cyan
    (255, 255, 0),      # 24 - Bright Yellow
    (255, 255, 128),    # 25 - Pastel Yellow
    (255, 255, 255),    # 26 - Bright White
]

CPC_COLOR_NAMES = [
    "Black",
    "Blue",
    "Bright Blue",
    "Red",
    "Magenta",
    "Mauve",
    "Bright Red",
    "Purple",
    "Bright Magenta",
    "Green",
    "Cyan",
    "Sky Blue",
    "Yellow",
    "White",
    "Pastel Blue",
    "Orange",
    "Pink",
    "Pastel Magenta",
    "Bright Green",
    "Sea Green",
    "Bright Cyan",
    "Lime",
    "Pastel Green",
    "Pastel Cyan",
    "Bright Yellow",
    "Pastel Yellow",
    "Bright White",
]

# Translates Firmware index to HW color
CPC_HW_COLORS = [
    0x14, 
    0x04,
    0x15,
    0x1C,
    0x18,
    0x1D,
    0x0C,
    0x05,
    0x0D,
    0x16,
    0x06,
    0x17,
    0x1E,
    0x00,
    0x1F,
    0x0E,
    0x07,
    0x0F,
    0x12,
    0x02,
    0x13,
    0x1A,
    0x19,
    0x1B,
    0x0A,
    0x03,
    0x0B
]

MODE_MAX_COLORS = {
    0: 16,  # MODE 0
    1: 4,   # MODE 1
    2: 2    # MODE 2
}

MODE_LABELS = {
    0: "Mode 0 (16 colors)",
    1: "Mode 1 (4 colors)",
    2: "Mode 2 (2 colors)",
}

# Default palettes (indexes into CPC_RGB_COLORS); entry 0 acts as background.
DEFAULT_PALETTES = {
    0: [1, 24],
    1: [1, 24],
    2: [1, 24],
}

def hex_color(cpc_index: int) -> str:
    r: int
    g: int
    b: int
    r, g, b = CPC_RGB_COLORS[cpc_index]
    return "#%02x%02x%02x" % (r, g, b)


def contrast_color(cpc_index: int) -> str:
    r: int
    g: int
    b: int
    r, g, b = CPC_RGB_COLORS[cpc_index]
    return "#000000" if (r * 299 + g * 587 + b * 114) / 1000 > 128 else "#ffffff"
