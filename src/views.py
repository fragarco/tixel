"""
Module that defines all Tixel views (TkInter dialogs)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in its version 3.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any
from controllers import TixelController
from model import Project

from constants import (
    APP_NAME,
    CPC_COLOR_NAMES,
    CPC_RGB_COLORS,
    MAX_SIZE,
    MODE_LABELS,
    FILE_EXT,
    FILE_TYPES,
    Tool,
    Change,
    contrast_color,
    hex_color,
)
from icons import TOOL_ICON_COLORS, TOOL_ICON_SIZE, TOOL_ICONS

class ModalDialog(tk.Toplevel):
    """
    Small helper for centred, modal dialogs.
    """

    result: Any

    def __init__(self, parent: tk.Misc, title: str) -> None:
        super().__init__(parent)
        self.transient(parent)  # type: ignore[call-overload]
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", lambda _: self.on_cancel())

    def show(self) -> Any | None:
        self.update_idletasks()
        parent: tk.Misc = self.master  # type: ignore[assignment]
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()
        self.wait_window(self)
        return self.result

    def on_cancel(self) -> None:
        self.result = None
        self.destroy()


class CPCColorDialog(ModalDialog):
    """
    Allow users to pick one of the 27 Amstrad CPC colors.
    """

    SWATCH  = 42
    COLUMNS = 9

    selected: int | None
    forbidden: list[int]
    swatches: dict[int, tk.Frame]
    info: tk.Label
    ok_button: ttk.Button

    def __init__(
        self,
        parent: tk.Misc,
        title = "Choose an Amstrad CPC color",
        current: int | None = None,
        forbidden: list[int] = [],
    ) -> None:
        super().__init__(parent, title)
        self.selected = current
        self.forbidden = list(forbidden)
        self.swatches = {}

        tk.Label(self, text="Only the 27 colors of the Amstrad CPC palette are available.",
                 anchor="w").pack(fill="x", padx=12, pady=(12, 6))

        grid: tk.Frame = tk.Frame(self, bd=1, relief="sunken")
        grid.pack(padx=12)
        for index in range(len(CPC_RGB_COLORS)):
            row, col = divmod(index, self.COLUMNS)
            holder = tk.Frame(grid, bd=3, relief="flat", background=grid.cget("background"))
            holder.grid(row=row, column=col, padx=2, pady=2)
            swatch = tk.Canvas(holder, width=self.SWATCH, height=self.SWATCH,
                               highlightthickness=1, highlightbackground="#555555",
                               background=hex_color(index), cursor="hand2")
            swatch.pack()
            if index in self.forbidden:
                swatch.create_line(2, 2, self.SWATCH, self.SWATCH,
                                   fill=contrast_color(index), width=2)
                swatch.create_line(2, self.SWATCH, self.SWATCH, 2,
                                   fill=contrast_color(index), width=2)
                swatch.configure(cursor="")
            else:
                swatch.bind("<Button-1>", lambda _, i=index: self.select(i))  # type: ignore[misc]
                swatch.bind("<Double-Button-1>", lambda _, i=index: self.on_ok(i))  # type: ignore[misc]
            self.swatches[index] = holder

        self.info = tk.Label(self, text="", anchor="w")
        self.info.pack(fill="x", padx=12, pady=(8, 0))

        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=12, pady=12)
        self.ok_button = ttk.Button(buttons, text="OK", command=self.on_ok)
        self.ok_button.pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.on_cancel).pack(side="right", padx=(0, 6))

        if self.selected is not None and self.selected not in self.forbidden:
            self.select(self.selected)
        else:
            self.selected = None
            self.update_info()

    def select(self, index: int) -> None:
        for holder in self.swatches.values():
            holder.configure(relief="flat", background=self.cget("background"))
        self.selected = index
        self.swatches[index].configure(relief="solid", background="#ff8000")
        self.update_info()

    def update_info(self) -> None:
        if self.selected is None:
            self.info.configure(text="No color selected")
            self.ok_button.state(["disabled"])
        else:
            r, g, b = CPC_RGB_COLORS[self.selected]
            self.info.configure(text=f"{self.selected} - {CPC_COLOR_NAMES[self.selected]}  RGB({r}, {g}, {b})")
            self.ok_button.state(["!disabled"])

    def on_ok(self, index: int | None = None) -> None:
        if index is not None:
            self.selected = index
        if self.selected is None:
            return
        self.result = self.selected
        self.destroy()


class NewProjectDialog(ModalDialog):
    """
    Asks for the video mode and the resolution of a new project.
    """

    mode_var: tk.StringVar
    width_var: tk.IntVar
    height_var: tk.IntVar

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, "New Project")

        body: tk.Frame = tk.Frame(self)
        body.pack(padx=14, pady=14)

        tk.Label(body, text="Video mode:").grid(row=0, column=0, sticky="w", pady=4)
        self.mode_var = tk.StringVar(value=MODE_LABELS[0])
        mode_box = ttk.Combobox(
            body,
            textvariable=self.mode_var,
            state="readonly",
            width=22,
            values=[MODE_LABELS[m] for m in (0, 1, 2)]
        )
        mode_box.grid(row=0, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(body, text="Width:").grid(row=1, column=0, sticky="w", pady=4)
        self.width_var = tk.IntVar(value=16)
        tk.Spinbox(
            body,
            from_=1,
            to=MAX_SIZE,
            width=6,
            textvariable=self.width_var).grid(row=1, column=1, sticky="w", pady=4)
        tk.Label(body, text=f"pixels (max {MAX_SIZE})").grid(row=1, column=2, sticky="w")

        tk.Label(body, text="Height:").grid(row=2, column=0, sticky="w", pady=4)
        self.height_var = tk.IntVar(value=16)
        tk.Spinbox(
            body,
            from_=1,
            to=MAX_SIZE,
            width=6,
            textvariable=self.height_var).grid(row=2, column=1, sticky="w", pady=4)
        tk.Label(body, text=f"pixels (max {MAX_SIZE})").grid(row=2, column=2, sticky="w")

        tk.Label(
            body,
            text="The mode and resolution cannot be changed later.",
            foreground="#804000").grid(row=3, column=0, columnspan=3,sticky="w", pady=(10, 0)
        )
        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=14, pady=(0, 14))
        ttk.Button(buttons, text="Create", command=self.on_ok).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.on_cancel).pack(side="right", padx=(0, 6))
        self.bind("<Return>", lambda _: self.on_ok())

    def on_ok(self) -> None:
        try:
            width = self.width_var.get()
            height = self.height_var.get()
        except (tk.TclError, ValueError):
            messagebox.showerror(APP_NAME, "Width and height must be whole numbers.", parent=self)
            return
        if not 1 <= width <= MAX_SIZE or not 1 <= height <= MAX_SIZE:
            messagebox.showerror(APP_NAME, f"Width and height must be between 1 and {MAX_SIZE}.", parent=self)
            return
        label = self.mode_var.get()
        mode  = next(m for m, text in MODE_LABELS.items() if text == label)
        self.result = (mode, width, height)
        self.destroy()


class CodeDialog(ModalDialog):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, "Code")
        self.geometry('680x430')

        body = tk.Frame(self, padx=5, pady=5)
        self.text = tk.Text(body)
        self.text.grid(row=0, column=0, rowspan=10, columnspan=9)
        body.pack(expand=True)

    def set_code(self, code: str) -> None:
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, code)




class TixelView(tk.Tk):
    """
    Main view class
    """

    PREVIEW_SIZE: int = 96

    ctrl: TixelController | None
    cell_size: int
    cell_ids: list[list[int]]
    palette_widgets: list[tk.Frame]
    grid_var: tk.BooleanVar
    tool_var: tk.StringVar
    tool_buttons: dict[Tool, tk.Radiobutton]
    tool_images: dict[Tool, tk.PhotoImage]
    mode_label: tk.Label
    resolution_label: tk.Label
    colors_label: tk.Label
    canvas: tk.Canvas
    sprite_list: tk.Listbox
    edit_menu: tk.Menu
    preview: tk.Canvas
    animation_button: ttk.Button
    palette_title: tk.Label
    remove_button: ttk.Button
    change_button: ttk.Button
    add_color_button: ttk.Button
    palette_area: tk.Frame
    status: tk.Label

    def __init__(self) -> None:
        super().__init__()
        self.ctrl = None
        self.title(APP_NAME)
        self.geometry("1000x740")
        self.minsize(860, 620)

        self.cell_size = 16
        self.cell_ids = []
        self.palette_widgets = []
        self.tool_var = tk.StringVar(value=Tool.PENCIL.value)
        self.tool_buttons = {}
        self.tool_images = {}

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._on_exit_requested)


    def set_controller(self, ctrl: TixelController) -> None:
        self.ctrl = ctrl

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self._build_menu_file(menubar)
        self._build_menu_edit(menubar)
        self._build_menu_tools(menubar)
        self._build_menu_transform(menubar)
        self._build_menu_view(menubar)
        self._build_menu_code(menubar)
        self._build_menu_help(menubar)

    def _build_menu_file(self, menubar: tk.Menu) -> None:
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="New Project...",
            accelerator="Ctrl+N",
            command=lambda: self.ctrl.new_project() if self.ctrl else None
        )
        file_menu.add_command(
            label="Open Project...",
            accelerator="Ctrl+O",
            command=lambda: self.ctrl.open_project() if self.ctrl else None
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save",
            accelerator="Ctrl+S",
            command=lambda: self.ctrl.save_project() if self.ctrl else None
        )
        file_menu.add_command(
            label="Save As...",
            command=lambda: self.ctrl.save_project_as() if self.ctrl else None
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.ctrl.on_exit() if self.ctrl else self.destroy())
        menubar.add_cascade(label="File", menu=file_menu)

    def _build_menu_edit(self, menubar: tk.Menu) -> None:
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="Undo",
            accelerator="Ctrl+Z",
            command=lambda: self.ctrl.undo() if self.ctrl else None
        )
        edit_menu.add_command(
            label="Redo",
            accelerator="Ctrl+Y",
            command=lambda: self.ctrl.redo() if self.ctrl else None
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Copy Sprite",
            accelerator="Ctrl+C",
            command=lambda: self.ctrl.copy_sprite() if self.ctrl else None
        )
        edit_menu.add_command(
            label="Paste Sprite",
            accelerator="Ctrl+V",
            command=lambda: self.ctrl.paste_sprite() if self.ctrl else None
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Add Sprite",
            command=lambda: self.ctrl.add_sprite() if self.ctrl else None
        )
        edit_menu.add_command(
            label="Delete Sprite",
            command=lambda: self.ctrl.delete_sprite() if self.ctrl else None
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Clear Sprite",
            command=lambda: self.ctrl.clear_sprite() if self.ctrl else None
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.edit_menu = edit_menu

    def _build_menu_tools(self, menubar: tk.Menu) -> None:
        tools_menu = tk.Menu(menubar, tearoff=0)
        for tool in Tool:
            tools_menu.add_radiobutton(
                label=tool.value,
                variable=self.tool_var,
                value=tool.value,
                command=lambda t=tool: self.ctrl.select_tool(t) if self.ctrl else None  # type: ignore[misc]
            )
        menubar.add_cascade(label="Tools", menu=tools_menu)

    def _build_menu_transform(self, menubar: tk.Menu) -> None:
        transform_menu = tk.Menu(menubar, tearoff=0)
        transform_menu.add_command(
            label="Flip Horizontally",
            command=lambda: self.ctrl.flip_horizontal() if self.ctrl else None
        )
        transform_menu.add_command(
            label="Flip Vertically",
            command=lambda: self.ctrl.flip_vertical() if self.ctrl else None
        )
        menubar.add_cascade(label="Transform", menu=transform_menu)

    def _build_menu_view(self, menubar: tk.Menu) -> None:
        self.grid_var = tk.BooleanVar(value=True)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(
            label="Grid",
            variable=self.grid_var,
            accelerator="Ctrl+G",
            command=lambda: self._redraw_canvas()
        )
        menubar.add_cascade(label="View", menu=view_menu)

    def _build_menu_code(self, menubar: tk.Menu) -> None:
        code_menu = tk.Menu(menubar, tearoff=0)
        code_menu.add_command(
            label="BASIC",
            command=lambda: self.ctrl.code_generate_basic() if self.ctrl else None
        )
        code_menu.add_command(
            label="BASIC (ABASC)",
            command=lambda: self.ctrl.code_generate_abasc() if self.ctrl else None
        )
        code_menu.add_command(
            label="C",
            command=lambda: self.ctrl.code_generate_c() if self.ctrl else None
        )
        code_menu.add_command(
            label="ASM",
            command=lambda: self.ctrl.code_generate_asm() if self.ctrl else None
        )
        menubar.add_cascade(label="Code", menu=code_menu)

    def _build_menu_help(self, menubar: tk.Menu) -> None:
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Quick Help",
            command=lambda: self.ctrl.show_help() if self.ctrl else None
        )
        help_menu.add_command(
            label=f"About {APP_NAME}",
            command=lambda: self.ctrl.show_about() if self.ctrl else None
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        self.configure(menu=menubar)

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self, bd=1, relief="raised")
        bar.pack(side="top", fill="x")

        self.mode_label = tk.Label(bar, text="", anchor="w", padx=8, pady=4)
        self.mode_label.pack(side="left")
        tk.Frame(bar, width=1, bg="#a0a0a0").pack(side="left", fill="y", pady=3)
        self.resolution_label = tk.Label(bar, text="", anchor="w", padx=8, pady=4)
        self.resolution_label.pack(side="left")
        tk.Frame(bar, width=1, bg="#a0a0a0").pack(side="left", fill="y", pady=3)
        self.colors_label = tk.Label(bar, text="", anchor="w", padx=8, pady=4)
        self.colors_label.pack(side="left")
        tk.Frame(bar, width=1, bg="#a0a0a0").pack(side="left", fill="y", pady=3)
        tk.Label(bar, text="Drawing Tool ", anchor="w", pady=4).pack(side="left", padx=(8, 4))
        for tool in Tool:
            image = self._build_tool_image(tool)
            self.tool_images[tool] = image
            button = tk.Radiobutton(
                bar,
                image=image,
                indicatoron=False,
                variable=self.tool_var,
                value=tool.value,
                command=lambda t=tool: self.ctrl.select_tool(t) if self.ctrl else None,  # type: ignore[misc]
                bd=1,
                relief="raised",
                selectcolor=self.cget("background"),
                cursor="hand2",
                takefocus=True,
                padx=1,
                pady=1
            )
            button.pack(side="left", padx=(0, 4))
            button.bind("<Enter>", lambda _e, t=tool: self.set_status(f"{t.value} tool"))  # type: ignore[misc]
            button.bind("<Leave>", lambda _e: self.set_status(""))  # type: ignore[misc]
            self.tool_buttons[tool] = button

    def _build_tool_image(self, tool: Tool) -> tk.PhotoImage:
        image = tk.PhotoImage(width=TOOL_ICON_SIZE, height=TOOL_ICON_SIZE)
        for y, row in enumerate(TOOL_ICONS[tool]):
            for x, char in enumerate(row):
                color = TOOL_ICON_COLORS.get(char)
                if color:
                    image.put(color, (x, y))
        return image

    def _build_body(self) -> None:
        body = tk.Frame(self)
        body.pack(side="top", fill="both", expand=True)

        work = tk.Frame(body, bg="#3c3c3c")
        work.pack(side="right", fill="both", expand=True)
        self.canvas = tk.Canvas(work, bg="#3c3c3c", highlightthickness=0, cursor="tcross")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas.bind("<Button-1>", lambda e: self._handle_paint_event(e, erase=False, stroke_start=True))
        self.canvas.bind("<B1-Motion>", lambda e: self._handle_paint_event(e, erase=False))
        self.canvas.bind("<Button-3>", lambda e: self._handle_paint_event(e, erase=True, stroke_start=True))
        self.canvas.bind("<B3-Motion>", lambda e: self._handle_paint_event(e, erase=True))
        self.canvas.bind("<Motion>", self._handle_motion_event)
        self.canvas.bind("<Leave>", lambda _e: self.set_status(""))
        work.bind("<Configure>", lambda _e: None)

        side = tk.Frame(body, bd=1, relief="groove", padx=6, pady=6)
        side.pack(side="left", fill="y")
        tk.Label(side, text="Sprites (animation)").pack(anchor="w")

        list_frame = tk.Frame(side)
        list_frame.pack(fill="both", expand=True, pady=4)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.sprite_list = tk.Listbox(list_frame, width=18, exportselection=False,
                                      activestyle="none", yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.sprite_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.sprite_list.pack(side="left", fill="both", expand=True)
        self.sprite_list.bind("<<ListboxSelect>>", self._on_sprite_selected)

        buttons = tk.Frame(side)
        buttons.pack(fill="x")
        ttk.Button(
            buttons,
            text="Add",
            width=8,
            command=lambda: self.ctrl.add_sprite() if self.ctrl else None).pack(side="left")
        ttk.Button(
            buttons,
            text="Delete",
            width=8,
            command=lambda: self.ctrl.delete_sprite() if self.ctrl else None).pack(side="right")
        order = tk.Frame(side)
        order.pack(fill="x", pady=(4, 0))
        ttk.Button(
            order,
            text="Up",
            width=8,
            command=lambda: self.ctrl.move_sprite(-1) if self.ctrl else None).pack(side="left")
        ttk.Button(
            order,
            text="Down",
            width=8,
            command=lambda: self.ctrl.move_sprite(1) if self.ctrl else None).pack(side="right")
        ttk.Button(
            side,
            text="Duplicate",
            command=lambda: self.ctrl.duplicate_sprite() if self.ctrl else None).pack(fill="x", pady=(4, 0))

        tk.Label(side, text="Preview").pack(anchor="w", pady=(12, 2))
        self.preview = tk.Canvas(side, width=self.PREVIEW_SIZE, height=self.PREVIEW_SIZE,
                                 bg="#000000", highlightthickness=1,
                                 highlightbackground="#808080")
        self.preview.pack()
        self.animation_button = ttk.Button(
            side,
            text="Play",
            command=lambda: self.ctrl.toggle_animation() if self.ctrl else None)
        self.animation_button.pack(fill="x", pady=(4, 0))

        palette_frame = tk.Frame(self, bd=1, relief="groove", padx=6, pady=6)
        palette_frame.pack(side="bottom", fill="x")
        header = tk.Frame(palette_frame)
        header.pack(fill="x")
        self.palette_title = tk.Label(header, text="Palette", anchor="w")
        self.palette_title.pack(side="left")
        self.remove_button = ttk.Button(
            header,
            text="Remove Color",
            command=lambda: self.ctrl.remove_palette_color() if self.ctrl else None)
        self.remove_button.pack(side="right")
        self.change_button = ttk.Button(
            header,
            text="Change Color...",
            command=lambda: self.ctrl.change_palette_color() if self.ctrl else None)
        self.change_button.pack(side="right", padx=6)
        self.add_color_button = ttk.Button(
            header,
            text="Add Color...",
            command=lambda: self.ctrl.add_palette_color() if self.ctrl else None)
        self.add_color_button.pack(side="right")
        self.palette_area = tk.Frame(palette_frame)
        self.palette_area.pack(fill="x", pady=(6, 0))

    def _build_statusbar(self) -> None:
        self.status = tk.Label(self, text="", anchor="w", bd=1, relief="sunken", padx=6)
        self.status.pack(side="bottom", fill="x")

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-n>", lambda _: self.ctrl.new_project() if self.ctrl else None)
        self.bind_all("<Control-N>", lambda _: self.ctrl.new_project() if self.ctrl else None)
        self.bind_all("<Control-o>", lambda _: self.ctrl.open_project() if self.ctrl else None)
        self.bind_all("<Control-O>", lambda _: self.ctrl.open_project() if self.ctrl else None)
        self.bind_all("<Control-s>", lambda _: self.ctrl.save_project() if self.ctrl else None)
        self.bind_all("<Control-S>", lambda _: self.ctrl.save_project() if self.ctrl else None)
        self.bind_all("<Control-c>", lambda _: self.ctrl.copy_sprite() if self.ctrl else None)
        self.bind_all("<Control-C>", lambda _: self.ctrl.copy_sprite() if self.ctrl else None)
        self.bind_all("<Control-v>", lambda _: self.ctrl.paste_sprite() if self.ctrl else None)
        self.bind_all("<Control-V>", lambda _: self.ctrl.paste_sprite() if self.ctrl else None)
        self.bind_all("<Control-z>", lambda _: self.ctrl.undo() if self.ctrl else None)
        self.bind_all("<Control-Z>", lambda _: self.ctrl.undo() if self.ctrl else None)
        self.bind_all("<Control-y>", lambda _: self.ctrl.redo() if self.ctrl else None)
        self.bind_all("<Control-Y>", lambda _: self.ctrl.redo() if self.ctrl else None)
        self.bind_all("<Control-g>", lambda _: self._on_view_grid())
        self.bind_all("<Control-G>", lambda _: self._on_view_grid())

    def _on_view_grid(self) -> None:
        self.grid_var.set(not self.grid_var.get())
        self._redraw_canvas()

    def _on_exit_requested(self) -> None:
        if self.ctrl:
            self.ctrl.on_exit()
        else:
            self.destroy()

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def _update_title(self, file_path: str | None, dirty: bool) -> None:
        name = os.path.basename(file_path) if file_path else f"Untitled{FILE_EXT}"
        self.title(f"{APP_NAME} - {name}{'*' if dirty else ''}")

    def _update_toolbar(self, project: Project) -> None:
        self.mode_label.configure(text=MODE_LABELS[project.video_mode])
        self.resolution_label.configure(text=f"Resolution: {project.width}x{project.height}")
        self.colors_label.configure(text=f"Colors: {len(project.palette)} / {project.max_colors}")


    def sync(self, aspects: set[str], pixel: tuple[int, int] | None = None) -> None:
        """
        Single refresh entry point. The controller broadcasts which model
        aspects changed and this method decides what to repaint.
        """
        if not self.ctrl:
            return
        if Change.SPRITES in aspects:
            self._refresh_sprite_list()
        if Change.PALETTE in aspects:
            self._rebuild_palette()
        if Change.PIXELS in aspects:
            if pixel is not None:
                self._redraw_pixel(pixel[0], pixel[1])
                self._redraw_preview()
            elif self._grid_matches_project():
                self._redraw_canvas()
            else:
                self._rebuild_canvas()   # grid shape must follow the (new) project
        if Change.TOOL in aspects:
            self._update_tool_selection()
        if Change.META in aspects:
            self._update_toolbar(self.ctrl.project)
            self._update_title(self.ctrl.file_path, self.ctrl.dirty)
            self._update_undo_redo_menu()
        if Change.PREVIEW in aspects:
            self._redraw_preview()

    def _grid_matches_project(self) -> bool:
        if not self.ctrl or not self.cell_ids:
            return False
        return (len(self.cell_ids) == self.ctrl.project.height and
                len(self.cell_ids[0]) == self.ctrl.project.width)

    def _update_tool_selection(self) -> None:
        if not self.ctrl:
            return
        self.tool_var.set(self.ctrl.active_tool.value)
        for tool, button in self.tool_buttons.items():
            button.configure(relief="sunken" if tool is self.ctrl.active_tool else "raised")


    def _update_undo_redo_menu(self) -> None:
        """
        Keep the Edit > Undo/Redo items in sync with the history stacks.
        """
        if not self.ctrl:
            return
        self.edit_menu.entryconfigure("Undo", state="normal" if self.ctrl.history.can_undo else "disabled")
        self.edit_menu.entryconfigure("Redo", state="normal" if self.ctrl.history.can_redo else "disabled")


    def _rebuild_canvas(self) -> None:
        if not self.ctrl:
            return
        width, height = self.ctrl.project.width, self.ctrl.project.height
        self.cell_size = max(6, min(24, 640 // max(width, height)))
        cell = self.cell_size
        self.canvas.delete("all")
        self.canvas.configure(width=width * cell, height=height * cell)
        outline = "#555555" if self.grid_var.get() else ""
        self.cell_ids = []
        for y in range(height):
            row: list[int] = []
            for x in range(width):
                row.append(self.canvas.create_rectangle(
                    x * cell, y * cell, (x + 1) * cell, (y + 1) * cell,
                    outline=outline, width=1))
            self.cell_ids.append(row)
        self._redraw_canvas()

    def _redraw_canvas(self) -> None:
        if not self.cell_ids or not self.ctrl:
            return
        outline = "#555555" if self.grid_var.get() else ""
        sprite  = self.ctrl.sprite  # type: ignore[assignment]
        for y in range(sprite.height):
            for x in range(sprite.width):
                self.canvas.itemconfigure(
                    self.cell_ids[y][x],
                    fill=self.palette_hex(sprite.get(x, y)),
                    outline=outline
                )
        self._redraw_preview()

    def _redraw_pixel(self, x: int, y: int) -> None:
        if not self.ctrl or not self.cell_ids:
            return
        self.canvas.itemconfigure(
            self.cell_ids[y][x],
            fill=self.palette_hex(self.ctrl.sprite.get(x, y))
        )

    def palette_hex(self, palette_index: int) -> str:
        if not self.ctrl:
            return "#000000"
        palette = self.ctrl.project.palette
        if 0 <= palette_index < len(palette):
            return hex_color(palette[palette_index])
        return hex_color(palette[0])

    def _handle_paint_event(self, event: tk.Event, erase: bool = False, stroke_start: bool = False) -> None:
        if not self.ctrl:
            return
        state = event.state if isinstance(event.state, int) else 0
        shift = bool(state & 0x0001)
        if shift and not stroke_start:
            return    # Do not paint stray pixels while dragging with Shift held
        cell = self.cell_size
        x = event.x // cell
        y = event.y // cell
        self.ctrl.on_canvas_click(x, y, erase, stroke_start, shift)

    def _handle_motion_event(self, event: tk.Event) -> None:
        if not self.ctrl:
            return
        cell = self.cell_size
        x = event.x // cell
        y = event.y // cell
        self.ctrl.on_canvas_motion(x, y)


    def _rebuild_palette(self) -> None:
        if not self.ctrl:
            return
        for widget in self.palette_area.winfo_children():
            widget.destroy()
        self.palette_widgets = []

        palette = self.ctrl.project.palette
        selected = self.ctrl.selected_palette_index
        if selected >= len(palette):
            selected = 0

        for index, cpc_index in enumerate(palette):
            holder = tk.Frame(
                self.palette_area,
                bd=3,
                relief="flat",
                background=self.palette_area.cget("background")
            )
            holder.grid(row=0, column=index, padx=3, pady=3)
            swatch = tk.Canvas(
                holder,
                width=40,
                height=34,
                highlightthickness=1,
                highlightbackground="#555555",
                background=hex_color(cpc_index),
                cursor="hand2"
            )
            swatch.create_text(20, 17, text=str(index), fill=contrast_color(cpc_index))
            swatch.pack()
            swatch.bind("<Button-1>", lambda _, i=index: self.ctrl.select_palette_index(i) if self.ctrl else None)  # type: ignore[misc]
            swatch.bind("<Double-Button-1>", lambda _, i=index: self.ctrl.change_palette_color(i) if self.ctrl else None)  # type: ignore[misc]
            self.palette_widgets.append(holder)

        self.colors_label.configure(text=f"Colors: {len(palette)} / {self.ctrl.project.max_colors}")
        self.palette_title.configure(text="Palette  (double click a color to change it)")
        self.add_color_button.state(
            ["disabled"] if len(palette) >= self.ctrl.project.max_colors else ["!disabled"]
        )
        self.remove_button.state(["disabled"] if len(palette) <= 1 else ["!disabled"])
        self._highlight_palette_selection(self.ctrl.selected_palette_index)

    def _highlight_palette_selection(self, index: int) -> None:
        if not 0 <= index < len(self.palette_widgets):
            return
        background = self.palette_area.cget("background")
        for i, holder in enumerate(self.palette_widgets):
            if i == index:
                holder.configure(relief="solid", background="#ff8000")
            else:
                holder.configure(relief="flat", background=background)

    def _refresh_sprite_list(self) -> None:
        if not self.ctrl:
            return
        self.sprite_list.delete(0, "end")
        for i in range(len(self.ctrl.project.sprites)):
            self.sprite_list.insert("end", " Sprite %d" % (i + 1))
        self.sprite_list.selection_clear(0, "end")
        self.sprite_list.selection_set(self.ctrl.current_sprite_index)
        self.sprite_list.see(self.ctrl.current_sprite_index)
        self.edit_menu.entryconfigure(
            "Delete Sprite",
            state="disabled" if len(self.ctrl.project.sprites) <= 1 else "normal"
        )

    def _on_sprite_selected(self, event: Any = None) -> None:
        if not self.ctrl:
            return
        selection = self.sprite_list.curselection()
        if not selection:
            return
        index = selection[0]
        self.ctrl.on_sprite_selected(index)


    def _redraw_preview(self) -> None:
        if not self.ctrl:
            return
        if self.ctrl.animating:
            idx = min(self.ctrl.animation_frame, len(self.ctrl.project.sprites) - 1)
            sprite = self.ctrl.project.sprites[idx]
        else:
            sprite = self.ctrl.sprite
        self.preview.delete("all")
        cell = max(1, self.PREVIEW_SIZE // max(sprite.width, sprite.height))
        offset_x = (self.PREVIEW_SIZE - cell * sprite.width) // 2
        offset_y = (self.PREVIEW_SIZE - cell * sprite.height) // 2
        for y in range(sprite.height):
            for x in range(sprite.width):
                self.preview.create_rectangle(
                    offset_x + x * cell,
                    offset_y + y * cell,
                    offset_x + (x + 1) * cell,
                    offset_y + (y + 1) * cell,
                    fill=self.palette_hex(sprite.get(x, y)),
                    width=0
                )

    def set_animation_button_text(self, text: str) -> None:
        self.animation_button.configure(text=text)


    def info(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message, parent=self)

    def warn(self, title: str, message: str) -> None:
        messagebox.showwarning(title, message, parent=self)

    def error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message, parent=self)

    def confirm(self, title: str, message: str) -> bool:
        return bool(messagebox.askyesno(title, message, parent=self))

    def confirm_save_discard(self, title: str, message: str) -> bool | None:
        """
        True = save, False = discard, None = cancel.
        """
        return messagebox.askyesnocancel(title, message, parent=self)

    def pick_open_path(self, title: str) -> str:
        return filedialog.askopenfilename(
            parent=self,
            title=title,
            defaultextension=FILE_EXT,
            filetypes=FILE_TYPES
        )

    def pick_save_path(self, title: str, initialfile: str) -> str:
        return filedialog.asksaveasfilename(
            parent=self,
            title=title,
            defaultextension=FILE_EXT,
            filetypes=FILE_TYPES,
            initialfile=initialfile
        )

    def ask_palette_color(self, title: str, current: int | None = None, forbidden: list[int] = []) -> int | None:
        dialog = CPCColorDialog(self, title, current=current, forbidden=forbidden)
        return dialog.show()

    def ask_new_project_settings(self) -> tuple[int, int, int] | None:
        dialog = NewProjectDialog(self)
        return dialog.show()

    def code_show(self, code:list[str]) -> None:
        dialog = CodeDialog(self)
        text = ''.join(code)
        dialog.set_code(text)
        dialog.show()
