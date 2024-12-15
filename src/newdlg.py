import tkinter as tk
from tkinter import ttk
from imgconv import CPC_RGB_COLORS, CPC_COLOR_NAMES

class NewDialog(tk.Toplevel):
    sizes = [(8,8), (8,16), (8,24), (16,8), (16,16), (16,24), (24,8), (24,16), (24,24)]

    def __init__(self, defmode, defsize, defbgcolor):
        super().__init__()   
        self.color = defbgcolor
        self.sizeindex = defsize
        self.size = self.sizes[defsize]
        self.mode = defmode

        self.wm_title('New Project')
        self.geometry('300x150')

        self.frame = tk.Frame(self, padx=5, pady=5)
        l = tk.Label(self.frame, text="Destination Mode:")
        l.grid(row=0, column=0, sticky='nw', pady=5)
        self.modes = ttk.Combobox(
            self.frame,
            state="readonly",
            values=['Mode 0', 'Mode 1', 'Mode 2']
        )
        self.modes.current(defmode)
        self.modes.grid(row=0, column=1, columnspan=2, sticky='nw', pady=5)

        l = tk.Label(self.frame, text="Backgroun color:")
        l.grid(row=1, column=0, sticky='nw', pady=5)
        self.bgcolors = ttk.Combobox(
            self.frame,
            state="readonly",
            values=CPC_COLOR_NAMES
        )
        self.bgcolors.current(self._hex2rgbindex(defbgcolor))
        self.bgcolors.bind("<<ComboboxSelected>>", self.onchange_bgcolor)
        self.bgcolors.grid(row=1, column=1, columnspan=2, sticky='nw', pady=5)
        self.colorbtn = tk.Frame(
                self.frame,
                width=20,
                height=20,
                background=self.color,
                highlightbackground='black',
                highlightthickness=1
            )
        self.colorbtn.grid(row=1, column=3, padx=5, pady=5)

        l = tk.Label(self.frame, text="Sprote size:")
        l.grid(row=2, column=0, sticky='nw', pady=5)
        self.sizescb = ttk.Combobox(
            self.frame,
            state="readonly",
            values=['8x8', '8x16', '8x24', '16x8', '16x16', '16x24', '24x8', '24x16', '24x24']
        )
        self.sizescb.current(defsize)
        self.sizescb.grid(row=2, column=1, columnspan=2, sticky='nw', pady=5)

        b = tk.Button(self.frame, text="Create", command=self.on_create)
        b.grid(row=4, column=1, sticky='s', pady=10)
        self.frame.pack(expand=True)

    def _hex2rgbindex(self, hexcolor):
        r = int(hexcolor[1:3], 16)
        g = int(hexcolor[3:5], 16)
        b = int(hexcolor[5:7], 16)
        return CPC_RGB_COLORS.index((r,g,b))

    def _rgbindex2hex(self, colorid):
        rgb = CPC_RGB_COLORS[colorid]
        return f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'

    def on_create(self):
        self.mode = self.modes.current()
        
        self.sizeindex = self.sizescb.current()
        self.size = self.sizes[self.sizeindex]
        self.destroy()

    def onchange_bgcolor(self, event):
        colorid = self.bgcolors.current()
        self.color = self._rgbindex2hex(colorid)
        self.colorbtn.configure(background=self.color)

    def get_mode(self):
        return self.mode
    
    def get_bgcolor(self):
        return self.color
    
    def get_size(self):
        return self.size, self.sizeindex