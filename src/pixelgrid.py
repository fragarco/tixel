import tkinter as tk
import enum

MAX_XPIXELS = 24
MAX_YPIXELS = 24
PIXEL_SIZE = 30

class PixelGridMode(enum.Enum):
    DRAWING     = 0
    EREASING    = 1
    REPLACING   = 2
    FILLING     = 3

class PixelGrid(tk.Frame):
    def __init__(self, parent, mode, width, height, bgcolor, pxsize = 30):
        super().__init__(parent, bd=1, relief=tk.SUNKEN)
        self.width = width
        self.height = height
        self.pxsize = pxsize
        self.scrnmode = mode
        self.fill_color1 = bgcolor
        self.fill_color2 = bgcolor
        self.fill_bg = bgcolor
        self.behaviour = PixelGridMode.DRAWING
        canvas_maxw = MAX_XPIXELS * self.pxsize
        canvas_maxh = MAX_YPIXELS * self.pxsize
        self.undo_stack = []
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, width=canvas_maxw, height=canvas_maxh)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._draw_pixels()

    def _draw_pixels(self):
        aspectx, aspecty = [(1, 0.5), (1, 1), (0.5, 1)][self.scrnmode]    
        for row in range(MAX_YPIXELS):
            for column in range(MAX_XPIXELS):
                x0, y0 = (column * self.pxsize * aspectx), (row * self.pxsize * aspecty)
                x1, y1 = (x0 + self.pxsize * aspectx), (y0 + self.pxsize * aspecty)
                if column < self.width and row < self.height:
                    self.canvas.create_rectangle(x0, y0, x1, y1,
                                                fill=self.fill_bg, outline="gray",
                                                tags=(self._tag(column, row), "cell"))
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#CCCCCC', tags=("out"))
                    
        self.canvas.tag_bind("cell", "<B1-Motion>", lambda e: self._paint(e, self.fill_color1))
        self.canvas.tag_bind("cell", "<Button-1>",  lambda e: self._paint(e, self.fill_color1))
        # Depending on the OS, right mouse button can be Button-2 or Button-3
        self.canvas.tag_bind("cell", "<B2-Motion>", lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<Button-2>",  lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<B3-Motion>", lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<Button-3>",  lambda e: self._paint(e, self.fill_color2))
    
    def _tag(self, x, y):
        # Return the tag for a given row and column
        tag = f"{x},{y}"
        return tag

    def _paint(self, event, color):
        cell = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(cell)
        if 'out' not in tags:
            if self.behaviour == PixelGridMode.EREASING:
                oldcolor = self.canvas.itemcget(cell, "fill")
                if oldcolor != color:
                    self.undo_append()
                    self.canvas.itemconfigure(cell, fill=self.fill_bg)
            elif self.behaviour == PixelGridMode.DRAWING:
                oldcolor = self.canvas.itemcget(cell, "fill")
                if oldcolor != color:
                    self.undo_append()
                    self.canvas.itemconfigure(cell, fill=color)
            elif self.behaviour == PixelGridMode.REPLACING:
                self.undo_append()
                self.replace_color(cell, color)
            elif self.behaviour == PixelGridMode.FILLING:
                pos = tags[0].split(',')
                pixels = [(int(pos[0]), int(pos[1]))]
                oldcolor = self.canvas.itemcget(cell, "fill")
                self.undo_append()
                self.fill_color(pixels, oldcolor, color)

    def get_pixels(self):
        pixels = []
        for y in range(self.height):
            for x in range(self.width):
                color = self.canvas.itemcget(self._tag(x, y), "fill")
                pixels.append(((x, y), color))
        return pixels            

    def set_pixels(self, pixels):
        for pixel in pixels:
            x, y = pixel[0]
            color = pixel[1]
            tag = self._tag(x, y)
            self.canvas.itemconfigure(tag, fill=color)

    def set_color(self, button, hexcol):
        if button == 0:
            self.fill_color1 = hexcol
        else:
            self.fill_color2 = hexcol

    def set_bgcolor(self, bgcolor):
        self.fill_bg = bgcolor

    def set_behaviour(self, mode):
        self.behaviour = mode

    def reconfigure(self, mode, width, height, bgcolor):
        self.scrnmode = mode
        self.width = width
        self.height = height
        self.fill_bg = bgcolor
        self.canvas.delete('all')
        self._draw_pixels()

    def mirrorvert(self):
        self.undo_append()
        pixels = self.get_pixels()
        mirror = []
        max_x = self.width - 1
        for i in range(0, len(pixels)):
            mirror.append(((max_x - pixels[i][0][0], pixels[i][0][1]), pixels[i][1]))
        self.set_pixels(mirror)

    def mirrorhor(self):
        self.undo_append()
        pixels = self.get_pixels()
        mirror = []
        max_y = self.height - 1
        for i in range(0, len(pixels)):
            mirror.append(((pixels[i][0][0], max_y - pixels[i][0][1]), pixels[i][1]))
        self.set_pixels(mirror)

    def replace_color(self, cell, color):
        oldcolor = self.canvas.itemcget(cell, "fill")
        pixels = self.get_pixels()
        replaced = []
        for p in pixels:
            if p[1] == oldcolor:
                replaced.append((p[0], color))
            else:
                replaced.append(p)
        self.set_pixels(replaced)

    def fill_color(self, cells, oldcolor, newcolor):
        if oldcolor != newcolor:
            while len(cells) > 0:
                cx, cy = cells[0]
                cells = cells[1:]
                self.canvas.itemconfigure(self._tag(cx, cy), fill=newcolor)
                neighbours = [
                    (cx-1, cy-1),
                    (cx  , cy-1),
                    (cx+1, cy-1),
                    (cx-1, cy),
                    (cx+1, cy),
                    (cx-1, cy+1),
                    (cx  , cy+1),
                    (cx+1, cy+1)
                ]
                for x,y in neighbours:
                    if x > -1 and x < self.width and y > -1 and y < self.height:
                        tag = self._tag(x, y)
                        color = self.canvas.itemcget(tag, "fill")
                        if color == oldcolor and (x,y) not in cells:
                            cells.append((x,y))                

    def undo_reset(self):
        self.undo_stack = []

    def undo_append(self):
        pixels = self.get_pixels()
        self.undo_stack.append(pixels)
        if len(self.undo_stack) > 5:
            self.undo_stack = self.undo_stack[1:]

    def undo_pop(self):
        if len(self.undo_stack) > 0:
            pixels = self.undo_stack[-1]
            self.set_pixels(pixels)
            self.undo_stack = self.undo_stack[0:-1]
