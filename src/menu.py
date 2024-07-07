import tkinter as tk
import enum

class MenuActions(enum.Enum):
    FILE_NEW = 10
    FILE_OPEN = 11
    FILE_SAVE = 12
    FILE_SAVE_AS = 13
    FILE_EXIT = 14

    EDIT_CUT = 20
    EDIT_COPY = 21
    EDIT_PASTE = 22

    CODE_BASIC = 30
    CODE_C = 31
    CODE_ASM = 32

    HELP_ABOUT = 90


class AppMenu:
    def __init__(self, root):
        self.root = root
        self.menu_main = tk.Menu(root)

    def init_file(self, listener):
        self.menu_file = tk.Menu(self.menu_main, tearoff=0)
        self.menu_file.add_command(label='New...', command=lambda: listener(MenuActions.FILE_NEW))
        self.menu_file.add_command(label="Open Project...", command=lambda: listener(MenuActions.FILE_OPEN))
        self.menu_file.add_command(label="Save Project", command=lambda: listener(MenuActions.FILE_SAVE))
        self.menu_file.add_command(label="Save Project As...", command=lambda: listener(MenuActions.FILE_SAVE_AS))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=lambda: listener(MenuActions.FILE_EXIT))
        self.menu_main.add_cascade(label="File", menu=self.menu_file)

    def init_edit(self, listener):
        self.menu_edit = tk.Menu(self.menu_main, tearoff=0)
        self.menu_edit.add_command(label="Cut", command=lambda: listener(MenuActions.EDIT_CUT))
        self.menu_edit.add_command(label="Copy", command=lambda: listener(MenuActions.EDIT_COPY))
        self.menu_edit.add_command(label="Paste", command=lambda: listener(MenuActions.EDIT_PASTE))
        self.menu_main.add_cascade(label="Edit", menu=self.menu_edit)

    def init_code(self, listener):
        self.menu_code = tk.Menu(self.menu_main, tearoff=0)
        self.menu_code.add_command(label="BASIC", command=lambda: listener(MenuActions.CODE_BASIC))
        self.menu_code.add_command(label="C", command=lambda: listener(MenuActions.CODE_C))
        self.menu_code.add_command(label="Assembly", command=lambda: listener(MenuActions.CODE_ASM))
        self.menu_main.add_cascade(label="Code", menu=self.menu_code)

    def init_help(self, listener):
        self.menu_help = tk.Menu(self.menu_main, tearoff=0)
        self.menu_help.add_command(label="About...", command=lambda: listener(MenuActions.HELP_ABOUT))
        self.menu_main.add_cascade(label="Help", menu=self.menu_help)