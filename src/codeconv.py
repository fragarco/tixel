#!/usr/bin/env python

"""
Module that helps convert sprites to CPC coded images in
different languages.

The CPC video memory arrangement is a little bit 'special'.
As reference:

Mode 2, 640x200, 2 colors
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0	pixel 1	pixel 2	pixel 3	pixel 4	pixel 5	pixel 6	pixel 7

Mode 1, 320x200, 4 colors (2 bits x pixel: bit 1 then bit 0)
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0 pixel 1 pixel 2 pixel 3 pixel 0 pixel 1	pixel 2 pixel 3

Modo 0, 160x200, colors (4 bits x pixel: bit 0 bit 2 bit 1 bit 3)
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0 pixel 1 pixel 0 pixel 1 pixel 0 pixel 1 pixel 0 pixel 1

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

from model import Project, Sprite
from constants import CPC_HW_COLORS

# Hex bytes per emitted source line (C/ASM/ABASC image listings)
BYTES_PER_SOURCE_LINE = 16


class CodeConverter:
    def __init__(self, prj: Project) -> None:
        self.imgw = prj.width
        self.imgh = prj.height
        self.mode = prj.video_mode
        self.fwpal = prj.palette
        self.hwpal = [CPC_HW_COLORS[c] for c in self.fwpal]

    def _pixels_per_byte(self) -> int:
        """
        How many pixels share one video byte in the project video mode.
        """
        return 8 if self.mode == 2 else 4 if self.mode == 1 else 2

    def _bytes_per_line(self) -> int:
        """
        Video bytes emitted per source line (driven by the sprite width).
        """
        return min(BYTES_PER_SOURCE_LINE, int(self.imgw / self._pixels_per_byte()))

    def _chunk_lines(self, data: bytearray) -> list[bytearray]:
        """
        Split a video byte buffer into the chunks used by source listings.
        """
        row = self._bytes_per_line()
        return [data[i:i + row] for i in range(0, len(data), row)]

    def _flatten_pixels(self, pixels: list[list[int]]) -> bytearray:
        """
        Returns the pixel matrix WxH as a bytearray list.
        """
        img = bytearray()
        for y in range(0, self.imgh):
            for x in range(0, self.imgw):
                colorindex = pixels[y][x]
                img.extend(colorindex.to_bytes(1, 'little'))
        return img

    def _build_videoimg(self, pixels: list[list[int]]) -> bytearray:
        """
        Encodes color indexes depending on the screen mode video arrangement.
        """
        img = self._flatten_pixels(pixels)
        pixelxbyte = self._pixels_per_byte()
        totalbytes = int((self.imgh * self.imgw) / pixelxbyte)
        data = bytearray([0x00 for i in range(0, totalbytes)])
        for i in range(0, len(img)):
            video_byte = int(i / pixelxbyte)
            if self.mode == 2:
                pos = 7 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | (img[i] << pos)
            elif self.mode == 1:
                pos = 3 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | (img[i] & 0x02) << (pos+3) | (img[i] & 0x01) << pos
            else:
                pos = 1 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | \
                             (img[i] & 0x01) << (6 + pos) | \
                             (img[i] & 0x02) << (1 + pos) | \
                             (img[i] & 0x04) << (2 + pos) | \
                             (img[i] & 0x08) >> (3 - pos)
        return data

    def code_c_pal(self, name: str) -> list[str]:
        code: list[str] = []
        strpalette = '{ %s }' % ', '.join('0x%02X' % x for x in self.hwpal)
        code.append(f"// Palette of {len(self.hwpal)} colors\n")
        code.append(f"const unsigned char PAL_{name.upper()}[{len(self.hwpal)}] = {strpalette};\n\n")
        return code

    def code_c_img(self, sprite: Sprite, name: str) -> list[str]:
        data = self._build_videoimg(sprite.pixels)
        code: list[str] = []
        code.append(f"// mode {self.mode}, {self.imgw}x{self.imgh} pixels\n")
        code.append(f"const unsigned char SP_{name.upper()}[{len(data)}] = {{\n")
        lines = self._chunk_lines(data)
        for n, line in enumerate(lines):
            end = ',\n' if n < len(lines) - 1 else '\n'
            code.append('    ' + ', '.join('0x%02X' % x for x in line) + end)
        code.append('};\n\n')
        return code

    def code_asm_pal(self, name: str) -> list[str]:
        code: list[str] = []
        strpalette = ', '.join('0x%02X' % x for x in self.hwpal)
        code.append(f"; Palette of {len(self.hwpal)} colors\n")
        code.append(f"pal_{name.lower()}:\n")
        code.append('    ' + f"db {strpalette}\n\n")
        return code

    def code_asm_img(self, sprite: Sprite, name: str) -> list[str]:
        data = self._build_videoimg(sprite.pixels)
        code: list[str] = []
        code.append(f"; mode {self.mode}, {self.imgw}x{self.imgh} pixels\n")
        code.append(f"sp_{name.lower()}:\n")
        for line in self._chunk_lines(data):
            code.append('    db ' + ', '.join('&%02X' % x for x in line) + '\n')
        code.append('\n')
        return code

    def code_abasc_pal(self, name: str) -> list[str]:
        code: list[str] = []
        strpalette = ', '.join('0x%02X' % x for x in self.hwpal)
        code.append(f"' Palette of {len(self.hwpal)} colors\n")
        code.append(f"' " + ': '.join('INK %d,%d' % (i,x) for i,x in enumerate(self.fwpal)) + '\n')
        code.append(f"LABEL PAL.{name.upper()}:\n")
        code.append('    ' + f'ASM("db {strpalette}")\n\n')
        return code

    def code_abasc_img(self, sprite: Sprite, name: str) -> list[str]:
        data = self._build_videoimg(sprite.pixels)
        code: list[str] = []
        code.append(f"' mode {self.mode}, {self.imgw}x{self.imgh} pixels\n")
        code.append(f"LABEL SP.{name.upper()}:\n")
        for line in self._chunk_lines(data):
            code.append('    ASM("db ' + ', '.join('&%02X' % x for x in line) + '")\n')
        code.append('\n')
        return code

    def code_bas_pal(self, name: str) -> list[str]:
        code: list[str] = []
        code.append(f"' Palette of {len(self.fwpal)} colors, project {name}\n")
        code.append(f': '.join('INK %d,%d' % (i,x) for i,x in enumerate(self.fwpal)) + '\n')
        return code

    def code_bas_img(self, sprite: Sprite, name: str) -> list[str]:
        code: list[str] = []
        img = self._flatten_pixels(sprite.pixels)
        xcursors = int(self.imgw / 8)
        ycursors = int(self.imgh / 8)
        symbols = 256 - (len(self.fwpal) * xcursors * ycursors)
        if symbols < 0: return code
        code.append(f"SYMBOL AFTER {symbols}\n\n")
        printcmd = []
        for cindex in range(0,len(self.fwpal)):
            code.append(f"' Symbol definitions for INK {cindex}\n")
            for y in range(0, ycursors):
                printline = f"LOCATE 10,{10+y}: PRINT CHR$(15)+CHR$({cindex})"
                for x in range(0, xcursors):
                    symbol = []
                    for cline in range(0, 8):  # a cursor has 8 lines
                        imgpos = (x * 8) + (self.imgw * (y * 8 + cline))
                        # each of the 8 pixels of the line sets one bit,
                        # leftmost pixel being the most significant one
                        symval = 0
                        for k in range(8):
                            if img[imgpos + k] == cindex:
                                symval |= 0x80 >> k
                        symbol.append(symval)
                    code.append(f"SYMBOL {symbols}")
                    for v in symbol: code.append(f",{v}")
                    code.append("\n")
                    printline = printline + f"+CHR$({symbols})"
                    symbols = symbols + 1
                printcmd.append(printline + '\n')
        code.append(f"\n' Printing sprite example code\n")
        code.append(f"CLS\n")
        code.append(f"PRINT CHR$(22)+CHR$(0)\n")
        for pline in printcmd:
            code.append(pline)
        code.append("PRINT CHR$(22)+CHR$(0)\n\n")
        return code
