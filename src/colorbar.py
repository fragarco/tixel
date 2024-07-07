import tkinter as tk
from idlelib.tooltip import Hovertip
from imgconv import CPC_RGB_COLORS, CPC_COLOR_NAMES

class ColorBar(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text='Palette')
        self.color_buttons = []

    def tohex(self, rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def create_bar(self, listener):
        self.color_buttons = []
        for i, color in enumerate(CPC_RGB_COLORS):
            hexcol = self.tohex(color)
            action1 = lambda ind=i, c=hexcol: listener(ind, c, 0)
            action2 = lambda ind=i, c=hexcol: listener(ind, c, 1)
            button = tk.Frame(
                self,
                width=40,
                height=40,
                background=hexcol,
                highlightbackground='black',
                highlightthickness=1
            )
            button.bind("<Button-1>", action1)
            button.bind("<Button-2>", action2)
            button.bind("<Button-3>", action2)

            button.grid(column=i%14, row=int(i/14), padx=2, pady=2)
            Hovertip(button, CPC_COLOR_NAMES[i])
            self.color_buttons.append(button)
