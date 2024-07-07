import tkinter as tk
import enum

MAX_XPIXELS = 24
MAX_YPIXELS = 24
PIXEL_SIZE = 30

class PixelGridMode(enum.Enum):
    DRAWING     = 0
    EREASING    = 1
    SELECTING   = 2
    FILLING     = 3

class PixelGrid(tk.Frame):
    def __init__(self, parent, mode, width, height, bgcolor):
        super().__init__(parent, bd=1, relief=tk.SUNKEN)
        self.width = width
        self.height = height
        self.size = PIXEL_SIZE
        self.scrnmode = mode
        self.fill_color1 = bgcolor
        self.fill_color2 = bgcolor
        self.fill_bg = bgcolor
        self.behaviour = PixelGridMode.DRAWING
        canvas_maxw = MAX_XPIXELS * self.size
        canvas_maxh = MAX_YPIXELS * self.size
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, width=canvas_maxw, height=canvas_maxh)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.draw_pixels()

    def draw_pixels(self):
        aspectx, aspecty = [(1, 0.5), (1, 1), (0.5, 1)][self.scrnmode]    
        for row in range(MAX_YPIXELS):
            for column in range(MAX_XPIXELS):
                x0, y0 = (column * self.size * aspectx), (row * self.size * aspecty)
                x1, y1 = (x0 + self.size * aspectx), (y0 + self.size * aspecty)
                if row < self.width and column < self.height:
                    self.canvas.create_rectangle(x0, y0, x1, y1,
                                                fill=self.fill_bg, outline="gray",
                                                tags=(self._tag(row, column), "cell"))
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#CCCCCC', tags=("out"))
                    
        self.canvas.tag_bind("cell", "<B1-Motion>", lambda e: self._paint(e, self.fill_color1))
        self.canvas.tag_bind("cell", "<Button-1>",  lambda e: self._paint(e, self.fill_color1))
        # Depending on the OS, right mouse button can be Button-2 or Button-3
        self.canvas.tag_bind("cell", "<B2-Motion>", lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<Button-2>",  lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<B3-Motion>", lambda e: self._paint(e, self.fill_color2))
        self.canvas.tag_bind("cell", "<Button-3>",  lambda e: self._paint(e, self.fill_color2))
    
    def _tag(self, row, column):
        # Return the tag for a given row and column
        tag = f"{row},{column}"
        return tag

    def get_pixels(self):
        pixels = []
        for row in range(self.height):
            for col in range(self.width):
                color = self.canvas.itemcget(self._tag(row, col), "fill")
                pixels.append(((row, col), color))
        return pixels            

    def set_pixels(self, pixels):
        for pixel in pixels:
            row, col = pixel[0]
            color = pixel[1]
            tag = self._tag(row, col)
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
        self.draw_pixels()

    def _paint(self, event, color):
        cell = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(cell)
        if 'out' not in tags:
            if self.behaviour == PixelGridMode.EREASING:
                self.canvas.itemconfigure(cell, fill=self.fill_bg)
            elif self.behaviour == PixelGridMode.DRAWING:
                self.canvas.itemconfigure(cell, fill=color)