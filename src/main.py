import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pixelgrid import PixelGrid, PixelGridMode
from toolframe import ToolFrame, Tools
from menu import AppMenu, MenuActions
from colorbar import ColorBar
from newdlg import NewDialog
from codedlg import CodeDialog
import json

class TixelApp:
    def __init__(self, root):
        self.width = 16
        self.height = 16
        self.scrnmode = 1
        self.current_prj = ""
        self.bgcolor = "#FFFFFF"

        self.root = root
        self.setup_menu()
        self.setup_canvas()
        self.setup_tools()

    def project_new(self):
        newwin = NewDialog(self.scrnmode, self.bgcolor)
        self.root.eval(f'tk::PlaceWindow {str(newwin)} center')
        self.root.wait_window(newwin)
        self.scrnmode = newwin.get_mode()
        self.width, self.height = newwin.get_size()
        self.bgcolor = newwin.get_bgcolor()
        self.newproject()

    def project_open(self):
        f = filedialog.askopenfilename(
            title = "Open Project",
            defaultextension=".tpj",
            filetypes = (("Tixel project","*.tpj"), ("all files","*.*"))
        )
        if f is not None:
            try:
                with open(f, 'r') as fd:
                    content = fd.readlines()
                    strcont = '\n'.join(content)
                    data = json.loads(strcont)
                    self.scrnmode = data['mode']
                    self.width = data['width']
                    self.height = data['height']
                    self.tool_frame.draw_color(0, data['btn1color'])
                    self.tool_frame.draw_color(1, data['btn2color'])
                    self.bgcolor = data['bgcolor']
                    self.tool_frame.erase_color(self.bgcolor)
                    self.canvas.set_pixels(data['pixels'])
                    self.canvas.set_color(0, data['btn1color'])
                    self.canvas.set_color(1, data['btn2color'])
                    self.canvas.set_bgcolor(self.bgcolor)
                self.current_prj = f
                self.updatetitle()
            except Exception as e:
                messagebox.showerror("Open error", str(e))

    def project_save(self, f):
        try:
            data = {}
            data['mode'] = self.scrnmode
            data['width'] = self.width
            data['height'] = self.height
            data['btn1color'], data['btn2color'] = self.tool_frame.get_currentcolors()
            data['bgcolor'] = self.bgcolor
            data['pixels'] = self.canvas.get_pixels()
            with open(f, 'w') as fd:
                content = json.dumps(data)
                fd.write(content)
            self.current_prj = f
            self.updatetitle()
        except Exception as e:
            messagebox.showerror("Save error", str(e))
            self.current_prj = ""

    def project_save_as(self):
        f = filedialog.asksaveasfilename(
            title = "Open Project",
            defaultextension=".tpj",
            filetypes = (("Tixel project","*.tpj"), ("all files","*.*"))
        )
        if f is not None:
            self.project_save(f)

    def menu_file_action(self, action):
        if action == MenuActions.FILE_NEW:
            self.project_new()
        elif action == MenuActions.FILE_OPEN:
            self.project_open()
        elif action == MenuActions.FILE_SAVE:
            if self.current_prj == "":
                self.project_save_as()
            else:
                self.project_save(self.current_prj)
        elif action == MenuActions.FILE_SAVE_AS:
            self.project_save_as()   
        elif action == MenuActions.FILE_EXIT:
            self.root.destroy()

    def menu_edit_action(self, action):
        if action == MenuActions.EDIT_UNDO:
            self.canvas.undo_pop()
            self.updatetitle()

    def menu_transform_action(self, action):
        if action == MenuActions.TRANSFORM_VERT:
            self.canvas.mirrorvert()
            self.updatetitle()
        elif action == MenuActions.TRANSFORM_HOR:
            self.canvas.mirrorhor()
            self.updatetitle()

    def code_view(self):
        codewin = CodeDialog()
        self.root.eval(f'tk::PlaceWindow {str(codewin)} center')
        self.root.wait_window(codewin)

    def menu_code_action(self, action):
        self.code_view()
        print("TODO code action:", action)

    def menu_help_action(self, action):
        print("TODO help action:", action)

    def tool_changed_action(self, newtool):
        if newtool == Tools.DRAW:
            self.canvas.set_behaviour(PixelGridMode.DRAWING)
        elif newtool == Tools.ERASE:
            self.canvas.set_behaviour(PixelGridMode.EREASING)
        elif newtool == Tools.REPLACE:
            self.canvas.set_behaviour(PixelGridMode.REPLACING)
        elif newtool == Tools.FILL:
            self.canvas.set_behaviour(PixelGridMode.FILLING)

    def newproject(self):
        self.canvas.set_bgcolor(self.bgcolor)
        self.canvas.reconfigure(self.scrnmode, self.width, self.height, self.bgcolor)
        self.tool_frame.erase_color(self.bgcolor)
        self.updatetitle()

    def setup_menu(self):
        self.menu = AppMenu(self.root)
        self.menu.init_file(self.menu_file_action)
        self.menu.init_edit(self.menu_edit_action)
        self.menu.init_transform(self.menu_transform_action)
        self.menu.init_code(self.menu_code_action)
        self.menu.init_help(self.menu_help_action)
        self.root.config(menu=self.menu.menu_main)

    def color_button_action(self, index, hexcol, button):
        self.canvas.set_color(button, hexcol)
        self.tool_frame.draw_color(button, hexcol)

    def setup_tools(self):
        self.tool_frame = ToolFrame(self.root)
        self.tool_frame.create_tools(self.tool_changed_action)
        self.tool_frame.grid(row=0, column=0, columnspan=2, sticky='n', padx=5)
        self.colorbar = ColorBar(self.root)
        self.colorbar.create_bar(self.color_button_action)
        self.colorbar.grid(row=1, column=0, columnspan=8, sticky='w', pady=5, padx=5)

    def setup_canvas(self):
        self.canvas = PixelGrid(self.root, self.scrnmode, self.width, self.height, self.bgcolor)
        self.canvas.grid(row=0, column=2, columnspan=5)

    def updatetitle(self):
        prj = self.current_prj if self.current_prj != "" else "unsaved"
        title = f"Tixel - {prj} ({self.width}x{self.height} mode {self.scrnmode})"
        self.root.title(title)

    def run(self):
        self.updatetitle()
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = TixelApp(root)
    app.run()

if __name__ == "__main__":
    main()