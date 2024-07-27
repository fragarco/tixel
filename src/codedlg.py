import tkinter as tk
from tkinter import ttk

class CodeDialog(tk.Toplevel):
    def __init__(self):
        super().__init__()   

        self.wm_title('Code')
        self.geometry('680x430')

        self.frame = tk.Frame(self, padx=5, pady=5)
        self.text = tk.Text(self.frame)
        self.text.grid(row=0, column=0, rowspan=10, columnspan=9)
        self.frame.pack(expand=True)

    def set_code(self, code):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, code)