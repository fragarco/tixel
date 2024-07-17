import tkinter as tk
import enum

class MenuActions(enum.Enum):
    FILE_NEW = 10
    FILE_OPEN = 11
    FILE_SAVE = 12
    FILE_SAVE_AS = 13
    FILE_EXIT = 14

    EDIT_UNDO = 20

    TRANSFORM_VERT = 31
    TRANSFORM_HOR = 32

    CODE_BASIC = 40
    CODE_C = 41
    CODE_ASM = 42

    HELP_ABOUT = 90


class AppMenu:
    def __init__(self, root):
        self.menu_main = tk.Menu(root)
        root.configure(menu=self.menu_main)
        self.root = root

    def init_file(self, listener):
        self.menu_file = tk.Menu(self.menu_main, tearoff=0)
        self.menu_file.add_command(label='New...', command=lambda: listener(MenuActions.FILE_NEW))
        self.menu_file.add_command(label="Open Project...", command=lambda: listener(MenuActions.FILE_OPEN))
        self.menu_file.add_command(label="Save Project", accelerator='Ctrl+S', command=lambda: listener(MenuActions.FILE_SAVE))
        self.root.bind_all('<Control-s>', lambda ev: listener(MenuActions.FILE_SAVE))
        self.menu_file.add_command(label="Save Project As...", command=lambda: listener(MenuActions.FILE_SAVE_AS))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=lambda: listener(MenuActions.FILE_EXIT))
        self.menu_main.add_cascade(label="File", menu=self.menu_file)
        
    def init_edit(self, listener):
        self.menu_edit = tk.Menu(self.menu_main, tearoff=0)
        self.menu_edit.add_command(label="Undo", accelerator='Ctrl+Z', command=lambda: listener(MenuActions.EDIT_UNDO))
        self.root.bind_all('<Control-z>', lambda ev: listener(MenuActions.EDIT_UNDO))
        self.menu_main.add_cascade(label="Edit", menu=self.menu_edit)

    def init_transform(self, listener):
        self.menu_transform = tk.Menu(self.menu_main, tearoff=0)
        self.menu_transform.add_command(label="Vertically", command=lambda: listener(MenuActions.TRANSFORM_VERT))
        self.menu_transform.add_command(label="Horizontally", command=lambda: listener(MenuActions.TRANSFORM_HOR))
        self.menu_main.add_cascade(label="Transform", menu=self.menu_transform)

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