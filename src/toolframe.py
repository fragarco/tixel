import tkinter as tk
import enum

class Tools(enum.Enum):
    DRAW    = 0
    ERASE   = 1
    REPLACE = 2
    FILL    = 3

class ToolFrame(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, pady=5, padx=5, text='Tools')
        self.color1 = '#FFFFFF'
        self.color2 = '#FFFFFF'
        self.bgcolor = '#FFFFFF'
        self.selected = tk.StringVar(master=self, value='Draw')
        self.tools=[]

    def _create_colorview(self, text, row, col, defcolor, defsize=40):
        auxframe = tk.LabelFrame(self, pady=5, padx=5, text=text)
        auxframe.grid(row=row, column=col, padx=5, pady=5)
        colorframe = tk.Frame(
                auxframe,
                width=defsize,
                height=defsize,
                background=defcolor,
                highlightbackground='black',
                highlightthickness=1
            )
        auxframe.grid_columnconfigure(0, weight=1)
        auxframe.grid_rowconfigure(0, weight=1)
        colorframe.grid(row=0, column=0)
        return colorframe

    def create_tools(self, listener):
        tool = tk.Radiobutton(self, text='Draw', value='Draw', variable=self.selected, command=lambda: listener(Tools.DRAW))
        tool.grid(row=0, column=0, sticky='w')
        self.tools.append(tool)
        tool = tk.Radiobutton(self, text='Erase', value='Erase', variable=self.selected, command=lambda: listener(Tools.ERASE))
        tool.grid(row=1, column=0, sticky='w')
        self.tools.append(tool)
        tool = tk.Radiobutton(self, text='Replace', value='Replace', variable=self.selected, command=lambda: listener(Tools.REPLACE))
        tool.grid(row=2, column=0, sticky='w')
        self.tools.append(tool)
        tool = tk.Radiobutton(self, text='Fill', value='Fill', variable=self.selected, command=lambda: listener(Tools.FILL))
        tool.grid(row=3, column=0, sticky='w')
        self.tools.append(tool)

        self.colorbtn1 = self._create_colorview('Button1 Color', 4, 0, self.color1)
        self.colorbtn2 = self._create_colorview('Button2 Color', 5, 0, self.color2)
        self.bgcolorbtn = self._create_colorview('Erase Color', 6, 0, self.bgcolor)

    def draw_color(self, button, color):
        if button == 0:
            self.color1 = color
            self.colorbtn1.configure(background=color)
        else:
            self.color2 = color
            self.colorbtn2.configure(background=color)

    def erase_color(self, color):
        self.bgcolor = color
        self.bgcolorbtn.configure(background=color)

    def get_currentcolors(self):
        return (self.color1, self.color2)
    