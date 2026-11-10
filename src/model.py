"""
This module describes the data managed by Tixel:
    - Projects
    - Sprites

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

from typing import Any

from constants import (
	CPC_RGB_COLORS,
    DEFAULT_PALETTES,
    DEFAULT_SIZE,
    MAX_SIZE,
    MODE_MAX_COLORS
)

class Sprite:
    """
    Describes single image, usually known as sprite.
    """

    width: int
    height: int
    pixels: list[list[int]]

    def __init__(self, width: int, height: int, pixels: list[list[int]] | None = None) -> None:
        self.width = width
        self.height = height
        if pixels is None:
            self.pixels = [[0] * width for _ in range(height)]
        else:
            self.pixels = [list(row) for row in pixels]

    def clone(self) -> "Sprite":
        return Sprite(self.width, self.height, self.pixels)

    def clear(self) -> None:
        self.pixels = [[0] * self.width for _ in range(self.height)]

    def get(self, x: int, y: int) -> int:
        return self.pixels[y][x]

    def set(self, x: int, y: int, value: int) -> None:
        self.pixels[y][x] = value

    def remap(self, mapping: dict[int, int]) -> None:
        """
        Replace every palette index using mapping dictionary (dict old -> new) or
        to 0 if the index is not included in mapping.
        """
        for y in range(self.height):
            row = self.pixels[y]
            for x in range(self.width):
                row[x] = mapping.get(row[x], 0)

    def flood_fill(self, x: int, y: int, value: int) -> int:
        """
        Fill the 4-connected region around (x, y) that shares the clicked
        pixel's original color with value. Returns the number of pixels changed.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        target = self.get(x, y)
        if target == value:
            return 0
        pending: list[tuple[int, int]] = [(x, y)]
        changed = 0
        while pending:
            px, py = pending.pop()
            if self.get(px, py) != target:
                continue
            self.set(px, py, value)
            changed += 1
            for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                if 0 <= nx < self.width and 0 <= ny < self.height and self.get(nx, ny) == target:
                    pending.append((nx, ny))
        return changed

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, value: int) -> int:
        """
        Paint with value the cells of the straight line that goes from (x0, y0)
        to (x1, y1). Returns the number of pixels changed.
        """
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        changed = 0
        while True:
            if 0 <= x < self.width and 0 <= y < self.height and self.get(x, y) != value:
                self.set(x, y, value)
                changed += 1
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return changed

    def draw_circle(self, cx: int, cy: int, radius: int, value: int) -> int:
        """
        Paint with value the cells of the circle centered at (cx, cy) using
        the midpoint circle algorithm.
        """
        changed = 0
        x = radius
        y = 0
        err = 1 - radius
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                if 0 <= px < self.width and 0 <= py < self.height and self.get(px, py) != value:
                    self.set(px, py, value)
                    changed += 1
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1
        return changed

    def flip_horizontal(self) -> None:
        self.pixels = [list(reversed(row)) for row in self.pixels]

    def flip_vertical(self) -> None:
        self.pixels.reverse()

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "pixels": [list(row) for row in self.pixels]   # detached copy,
        }                                                   # used by save & undo

    @staticmethod
    def from_dict(data: Any, width: int, height: int, palette_size: int) -> "Sprite":
        if not isinstance(data, dict):
            raise ValueError("Wrong Sprite format")
        if int(data.get("width", width)) != width or int(data.get("height", height)) != height:
            raise ValueError("Sprite dimensions do not match the project")
        rows = data.get("pixels")
        if not isinstance(rows, list) or len(rows) != height:
            raise ValueError("Sprite pixel data has a wrong number of rows")
        pixels: list[list[int]] = []
        for row in rows:
            if not isinstance(row, list) or len(row) != width:
                raise ValueError("Sprite pixel data has a wrong number of columns")
            clean: list[int] = []
            for value in row:
                value = int(value)
                if not 0 <= value < palette_size:
                    raise ValueError("Pixel value outside of the project palette")
                clean.append(value)
            pixels.append(clean)
        return Sprite(width, height, pixels)


class Project:
    """
    Describes a Tixel project which is composed by a list of Sprites and
    the CPC video mode that defines de colour palette max length.
    All Sprites in the project share the same width and height values. 
    """

    width: int
    height: int
    video_mode: int
    palette: list[int]
    sprites: list[Sprite]
    name: str

    def __init__(
        self,
        width: int = DEFAULT_SIZE,
        height: int = DEFAULT_SIZE,
        video_mode: int = 0,
        palette: list[int] | None = None,
        sprites: list[Sprite] | None = None,
        name: str = "Untitled",
    ) -> None:
        self.width = width
        self.height = height
        self.video_mode = video_mode
        if palette is None:
            palette = list(DEFAULT_PALETTES[video_mode])[:MODE_MAX_COLORS[video_mode]]
        self.palette = list(palette)
        self.sprites = list(sprites) if sprites else [Sprite(width, height)]
        self.name = name

    @property
    def max_colors(self) -> int:
        return MODE_MAX_COLORS[self.video_mode]

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "video_mode": self.video_mode,
            "palette": list(self.palette),
            "sprites": [s.to_dict() for s in self.sprites],
            "name": self.name,
        }

    @staticmethod
    def from_dict(data: Any) -> "Project":
        if not isinstance(data, dict):
            raise ValueError("Wrong project format")
        try:
            width = int(data["width"])
            height = int(data["height"])
            video_mode = int(data["video_mode"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Missing or invalid width, height or video_mode")
        if not 1 <= width <= MAX_SIZE or not 1 <= height <= MAX_SIZE:
            raise ValueError(f"Resolution must be between 1x1 and {MAX_SIZE}x{MAX_SIZE}")
        if video_mode not in MODE_MAX_COLORS:
            raise ValueError(f"Unknown video mode: {video_mode}")

        palette: Any = data.get("palette")
        if not isinstance(palette, list) or not palette:
            raise ValueError("The project palette is missing or empty")
        if len(palette) > MODE_MAX_COLORS[video_mode]:
            raise ValueError(f"The palette has more colors than mode {video_mode} allows")
        clean_palette: list[int] = []
        for entry in palette:
            entry = int(entry)
            if not 0 <= entry < len(CPC_RGB_COLORS):
                raise ValueError("Palette entries must be Amstrad CPC colors (0-26)")
            clean_palette.append(entry)

        sprites_data: Any = data.get("sprites")
        if not isinstance(sprites_data, list) or not sprites_data:
            raise ValueError("The project must contain at least one sprite")
        sprites: list[Sprite] = [Sprite.from_dict(s, width, height, len(clean_palette)) for s in sprites_data]

        name: str = str(data.get("name") or "Untitled")
        return Project(width, height, video_mode, clean_palette, sprites, name)
