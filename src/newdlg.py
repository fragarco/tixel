import tkinter as tk
from tkinter import ttk
from imgconv import CPC_RGB_COLORS, CPC_COLOR_NAMES

class NewDialog(tk.Toplevel):
    def __init__(self, defmode, defbgcolor):
        super().__init__()   
        self.color = defbgcolor
        self.size = (16,16)
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
        self.modes.current(1)
        self.modes.grid(row=0, column=1, columnspan=2, sticky='nw', pady=5)

        l = tk.Label(self.frame, text="Backgroun color:")
        l.grid(row=1, column=0, sticky='nw', pady=5)
        self.bgcolors = ttk.Combobox(
            self.frame,
            state="readonly",
            values=CPC_COLOR_NAMES
        )
        self.bgcolors.current(26)
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
        self.sizes = ttk.Combobox(
            self.frame,
            state="readonly",
            values=['8x8', '16x8', '16x16', '24x16', '16x24', '24x24']
        )
        self.sizes.current(2)
        self.sizes.grid(row=2, column=1, columnspan=2, sticky='nw', pady=5)

        b = tk.Button(self.frame, text="Create", command=self.on_create)
        b.grid(row=4, column=1, sticky='s', pady=10)
        self.frame.pack(expand=True)

    def on_create(self):
        self.mode = self.modes.current()
        sizes = [(8,8), (16,8), (16,16), (24,16), (16,24), (24,24)]
        self.size = sizes[self.sizes.current()]
        self.destroy()

    def onchange_bgcolor(self, event):
        colorid = self.bgcolors.current()
        rgb = CPC_RGB_COLORS[colorid]
        self.color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        self.colorbtn.configure(background=self.color)

    def get_mode(self):
        return self.mode
    
    def get_bgcolor(self):
        return self.color
    
    def get_size(self):
        return self.size