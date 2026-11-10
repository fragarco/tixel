"""
"Cutre" pixel-art icons for the toolbar.

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

from constants import Tool

TOOL_ICON_SIZE = 16

TOOL_ICON_COLORS: dict[str, str] = {
    "#": "#202020",  # outline
    "y": "#e0a020",  # pencil body
    "r": "#e07080",  # eraser
    "w": "#d8b878",  # wood tip
    "k": "#404040",  # graphite
    "b": "#4080c0",  # bucket body
    "d": "#ff8000",  # paint drop
}

TOOL_ICONS: dict[Tool, list[str]] = {
    Tool.PENCIL: [
        ".............###",
        "...........#rrr#",
        "..........#brrr#",
        ".........#ybbb#.",
        "........#yyyb#..",
        ".......#yyyy#...",
        "......#yyyy#....",
        ".....#yyyy#.....",
        "....#yyyy#......",
        "...#yyyy#.......",
        "..#yyyy#........",
        ".#yyyy#.........",
        "#yyyy#..........",
        "#kkk#...........",
        "#kk#............",
        "##..............",
    ],
    Tool.FILL: [
        "................",
        "......####......",
        ".....#....#.....",
        "....#......#....",
        "...#........#...",
        ".bb###########..",
        "bb#bbbb.....b#..",
        "b.#bbbbb...bb#..",
        "b.#bbbbbb.bbb#..",
        "..#bbbbbbbbbb#..",
        "b.#bbbbbbbbbb#..",
        "..#bbbbbbbbbb#..",
        "..#bbbbbbbbbb#..",
        "...#bbbbbbbb#...",
        "...##########...",
        "................",
    ],
    Tool.CIRCLE: [
        "................",
        "......dddd......",
        "....dd....dd....",
        "...d........d...",
        "..d..........d..",
        "..d..........d..",
        ".d............d.",
        ".d............d.",
        ".d............d.",
        ".d............d.",
        "..d..........d..",
        "..d..........d..",
        "...d........d...",
        "....dd....dd....",
        "......dddd......",
        "................",
    ],
}
