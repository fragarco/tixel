#!/usr/bin/env python

"""
IMGCONV.PY by Javier Garcia

Module that helps convert pixel images to CPC coded images. The conversion depends
on the screen mode. As reference:

Mode 2, 640×200, 2 colors
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0	pixel 1	pixel 2	pixel 3	pixel 4	pixel 5	pixel 6	pixel 7

Mode 1, 320×200, 4 colors (2 bits x pixel: bit 1 then bit 0)
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0 pixel 1 pixel 2 pixel 3 pixel 0 pixel 1	pixel 2 pixel 3

Modo 0, 160×200, colors (4 bits x pixel: bit 0 bit 2 bit 1 bit 3)
bit 7	bit 6	bit 5	bit 4	bit 3	bit 2	bit 1	bit 0
pixel 0 pixel 1 pixel 0 pixel 1 pixel 0 pixel 1 pixel 0 pixel 1
"""

# Array of CPC colours in the following format:
# index     = firmware value (1-26) as it is used in INK basic instruction
# 1st value = hardware byte value (used in assembly to set colors in the PAL chip)
# (r, g, b) = tuple with RGB (0-255) values

CPC_FW_COLORS = [
(0x14, (0, 0, 0)),          # Black
(0x04, (0, 0, 128)),        # Blue
(0x15, (0, 0, 255)),        # Bright Blue
(0x1C, (128, 0, 0)),        # Red
(0x18, (128, 0, 128)),      # Magenta
(0x1D, (128, 0, 255)),      # Mauve
(0x0C, (255, 0, 0)),        # Bright Red
(0x05, (255, 0, 128)),      # Purple
(0x0D, (255, 0, 255)),      # Bright Magenta
(0x16, (0, 128, 0)),        # Green
(0x06, (0, 128, 128)),      # Cyan
(0x17, (0, 128, 255)),      # Sky Blue
(0x1E, (128, 128, 0)),      # Yellow
(0x00, (128, 128, 128)),    # White
(0x1F, (128, 128, 255)),    # Pastel Blue
(0x0E, (255, 128, 0)),      # Orange
(0x07, (255, 128, 128)),    # Pink
(0x0F, (255, 128, 255)),    # Pastel Magenta
(0x12, (0, 255, 0)),        # Bright Green
(0x02, (0, 255, 128)),      # Sea Green
(0x13, (0, 255, 255)),      # Bright Cyan
(0x1A, (128, 255, 0)),      # Lime
(0x19, (128, 255, 128)),    # Pastel Green
(0x1B, (128, 255, 255)),    # Pastel Cyan
(0x0A, (255, 255, 0)),      # Bright Yellow
(0x03, (255, 255, 128)),    # Pastel Yellow
(0x0B, (255, 255, 255)),    # Bright White
]

# Translates from HW color value to Firmware index
CPC_HW_COLORS = {
0x14: 0, 
0x04: 1,
0x15: 2,
0x1C: 3,
0x18: 4,
0x1D: 5,
0x0C: 6,
0x05: 7,
0x0D: 8,
0x16: 9,
0x06: 10,
0x17: 11,
0x1E: 12,
0x00: 13,
0x1F: 14,
0x0E: 15,
0x07: 16,
0x0F: 17,
0x12: 18,
0x02: 19,
0x13: 20,
0x1A: 21,
0x19: 22,
0x1B: 23,
0x0A: 24,
0x03: 25,
0x0B: 26
}

CPC_RGB_COLORS = [
(0, 0, 0),          # Black
(0, 0, 128),        # Blue
(0, 0, 255),        # Bright Blue
(128, 0, 0),        # Red
(128, 0, 128),      # Magenta
(128, 0, 255),      # Mauve
(255, 0, 0),        # Bright Red
(255, 0, 128),      # Purple
(255, 0, 255),      # Bright Magenta
(0, 128, 0),        # Green
(0, 128, 128),      # Cyan
(0, 128, 255),      # Sky Blue
(128, 128, 0),      # Yellow
(128, 128, 128),    # White
(128, 128, 255),    # Pastel Blue
(255, 128, 0),      # Orange
(255, 128, 128),    # Pink
(255, 128, 255),    # Pastel Magenta
(0, 255, 0),        # Bright Green
(0, 255, 128),      # Sea Green
(0, 255, 255),      # Bright Cyan
(128, 255, 0),      # Lime
(128, 255, 128),    # Pastel Green
(128, 255, 255),    # Pastel Cyan
(255, 255, 0),      # Bright Yellow
(255, 255, 128),    # Pastel Yellow
(255, 255, 255),    # Bright White
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

class ConversionError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
    

class ImgConverter:
    def __init__(self, w, h, mode):
        self.mode = mode
        self.palette = []
        self.img = bytearray()
        self.imgw = w
        self.imgh = h
        self.hex2index = {}
        for i, rgb in enumerate(CPC_RGB_COLORS):
            self.hex2index[f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'] = i
                 
    def _colors_per_mode(self, mode):
        if mode == 0: return 16
        return 4 if mode == 1 else 2

    def _palette2colors(self):
        colors = []
        for hwid in self.palette:
            fwid = CPC_HW_COLORS[hwid]
            colors.append(CPC_FW_COLORS[fwid][1])
        return colors

    def _get_color_distance(self, col1, col2):
        """ colors expected as (r, g, b) values"""
        return abs(col1[0] - col2[0]) + abs(col1[1] - col2[1]) + abs(col1[2] - col2[2])
    
    def _findcolor(self, hexpixel, cpccolors):
        nearest = (999, -1)
        h = hexpixel.lstrip('#')
        rgbpixel = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        for i in range(0, len(cpccolors)):
            diff = (self._get_color_distance(rgbpixel, cpccolors[i]), i)
            nearest = min(nearest, diff)
        return nearest

    def _img2mode(self):
        pixelxbyte = 8 if self.mode == 2 else 4 if self.mode == 1 else 2
        totalbytes = int((self.imgh * self.imgw) / pixelxbyte)
        data = bytearray([0x00 for i in range(0, totalbytes)])
        for i in range(0, len(self.img)):
            video_byte = int(i / pixelxbyte)
            if self.mode == 2:
                pos = 7 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | (self.img[i] << pos)
            elif self.mode == 1:
                pos = 3 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | (self.img[i] & 0x02) << (pos+3) | (self.img[i] & 0x01) << pos
            else:
                pos = 1 - (i % pixelxbyte)
                data[video_byte] = data[video_byte] | \
                             (self.img[i] & 0x01) << (6 + pos) | \
                             (self.img[i] & 0x02) << (1 + pos) | \
                             (self.img[i] & 0x04) << (2 + pos) | \
                             (self.img[i] & 0x08) >> (3 - pos)
        return data

    def _build_palette(self, sprite):
        """
        Assigns each pixel in the image to a CPC color. When
        all pixels are assigned, the method retains the colors with more
        assignements and builds the palette. The mode sets the max number
        of allowed entries.
        """
        ocurrences = [(0, i) for i in range(0, len(CPC_RGB_COLORS))]
        for row in range(self.imgh):
            for col in range(self.imgw):
                pixel = sprite[self.imgw * row + col][1]
                index = self.hex2index[pixel]
                ocurrences[index] = (ocurrences[index][0] + 1, index)
        palette = list(filter(lambda item: item[0] > 0, ocurrences))
        palette.sort(reverse=True)
        colors = self._colors_per_mode(self.mode)
        self.palette = list(map(lambda item: CPC_FW_COLORS[item[1]][0], palette[0:colors]))

    def _build_cpcimg(self, sprite):
        """
        Convert each RGB value to a CPC HW color value included in the
        palette. If more colors that allowed were used, the method selects
        the nearest valid color.
        """
        self._build_palette(sprite)
        palettecolors = self._palette2colors()
        self.img = bytearray()
        for y in range(0, self.imgh):
            for x in range(0, self.imgw):
                pixel = sprite[self.imgw * y + x][1]
                _, colorindex = self._findcolor(pixel, palettecolors)
                self.img.extend(colorindex.to_bytes(1, 'little'))
        
    def code_c(self, sprite, name):
        self._build_cpcimg(sprite)
        data = self._img2mode()
        code = []
        strpalette = '{ %s }' % ', '.join('0x%02X' % x for x in self.palette)
        code.append("// C format sprite created with Tixel\n")
        code.append(f"// mode {self.mode}, width {self.imgw}, height {self.imgh}\n\n")
        code.append(f"const unsigned char {name.upper()}_PAL[{len(self.palette)}] = {strpalette};\n\n")
        code.append(f"const unsigned char {name.upper()}_IMG[{len(sprite)}] = {{\n")
        pixbyte = 8 if self.mode == 2 else 4 if self.mode == 1 else 2
        row = min(16, int(self.imgw / pixbyte))
        while len(data) > 0:
            line = data[0:row]
            end = ',\n' if len(data) > row else '\n'
            code.append('    ' + ', '.join('0x%02X' % x for x in line) + end)
            data = data[row:]
        code.append('};\n')
        return code
        

    def code_asm(self, sprite, name):
        self._build_cpcimg(sprite)
        data = self._img2mode()
        code = []
        strpalette = ', '.join('0x%02X' % x for x in self.palette)
        code.append("; Assembly format sprite created with Tixel\n")
        code.append(f"; mode {self.mode}, width {self.imgw}, height {self.imgh}\n\n")
        code.append(f"{name.lower()}_pal:\n")
        code.append(f"\tdb {strpalette}\n\n")
        code.append(f"{name.lower()}_img:\n")
        pixbyte = 8 if self.mode == 2 else 4 if self.mode == 1 else 2
        row = min(16, int(self.imgw / pixbyte))
        while len(data) > 0:
            line = data[0:row]
            code.append('\tdb ' + ', '.join('&%02X' % x for x in line) + '\n')
            data = data[row:]
        code.append('\n')
        return code
        
    def code_bas(self, sprite, name):
        if name == "": name = "unnamed"
        self._build_cpcimg(sprite)
        code = []
        strpalette = ': '.join('INK %d,%d' % (i,CPC_HW_COLORS[x]) for i,x in enumerate(self.palette))
        code.append("10 ' BASIC formated sprite created with Tixel\n")
        code.append(f"20 ' {name}: mode {self.mode}, width {self.imgw}, height {self.imgh}\n")
        code.append("30 ' Palette:\n")
        code.append(f"40 ' {strpalette} \n")
        code.append("50 ' \n")
        xcursors = int(self.imgw / 8)
        ycursors = int(self.imgh / 8)
        symbols = 256 - (len(self.palette) * xcursors * ycursors)
        code.append(f"60 SYMBOL AFTER {symbols}\n")
        # I know, I know... the next code is not very elegant
        line = 70
        for cindex in range(0,len(self.palette)):
            code.append(f"{line} ' Symbol definitions for INK {cindex}\n")
            line = line + 10
            for y in range(0, ycursors):
                for x in range(0, xcursors):
                    symbol = []
                    for cline in range(0, 8):  # a cursor has 8 lines
                        imgpos = (x * 8) + (self.imgw * (y * 8 + cline))
                        symval = 0
                        symval = symval + (128 if self.img[imgpos] == cindex else 0)
                        symval = symval + (64 if self.img[imgpos+1] == cindex else 0)
                        symval = symval + (32 if self.img[imgpos+2] == cindex else 0)
                        symval = symval + (16 if self.img[imgpos+3] == cindex else 0)
                        symval = symval + (8 if self.img[imgpos+4] == cindex else 0)
                        symval = symval + (4 if self.img[imgpos+5] == cindex else 0)
                        symval = symval + (2 if self.img[imgpos+6] == cindex else 0)
                        symval = symval + (1 if self.img[imgpos+7] == cindex else 0)
                        symbol.append(symval)
                    code.append(f"{line} SYMBOL {symbols}")
                    line = line + 10
                    for v in symbol: code.append(f",{v}")
                    code.append("\n")
                    symbols = symbols + 1
        return code