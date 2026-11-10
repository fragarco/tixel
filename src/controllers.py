"""
Module that defines the Tixel controller object which connects
all the different views with the data model and the presistence methods.

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

import json
import os
from typing import TYPE_CHECKING, NamedTuple
from codeconv import CodeConverter

from constants import (
	APP_NAME,
	APP_VERSION,
	CPC_COLOR_NAMES,
	FILE_EXT,
	MAX_SIZE,
	MODE_LABELS,
    ANIMATION_DELAY,
    Change,
    Tool
)
import persistence
from model import Project, Sprite
from history import History, Snapshot

# Avoid circular import between views and controllers
if TYPE_CHECKING:
    from views import TixelView


class _LineAnchor(NamedTuple):
    """
    Origin of the Shift+click pencil line. It stores x,y position plus the
    color value.
    """
    x: int
    y: int
    value: int


class TixelController:
 
    view: "TixelView"
    project: Project
    file_path: str | None
    dirty: bool
    current_sprite_index: int
    selected_palette_index: int
    active_tool: Tool
    sprite_clipboard: Sprite | None
    animating: bool
    animation_job: str | None
    animation_frame: int
    history: History
    _changed: set[str]
    _pixel_hint: tuple[int, int] | None
    _stroke_recorded: bool
    _line_anchor: _LineAnchor | None

    def __init__(self, view: "TixelView") -> None:
        self.view = view
        self.file_path = None
        self.dirty = False
        self.current_sprite_index = 0
        self.selected_palette_index = 0
        self.active_tool = Tool.PENCIL
        self.sprite_clipboard = None
        self.animating = False
        self.animation_job = None
        self.animation_frame = 0
        self.history = History()
        self._changed = set()
        self._pixel_hint = None
        self._stroke_recorded = True
        self._line_anchor = None

        self.view.set_controller(self)
        self.set_project(Project(), None)


    @property
    def sprite(self) -> Sprite:
        return self.project.sprites[self.current_sprite_index]


    def _snapshot(self) -> Snapshot:
        """
        Serializable copy of the project plus the current selection.
        """
        return {
            "project": self.project.to_dict(),
            "sprite": self.current_sprite_index,
            "palette_sel": self.selected_palette_index,
        }

    def _restore(self, snapshot: Snapshot) -> None:
        self.project = Project.from_dict(snapshot["project"])
        self.current_sprite_index = min(int(snapshot["sprite"]), len(self.project.sprites) - 1)
        self.selected_palette_index = min(int(snapshot["palette_sel"]), len(self.project.palette) - 1)

    def undo(self) -> None:
        self.stop_animation()
        snapshot = self.history.undo(self._snapshot())
        if snapshot is None:
            self.view.set_status("Nothing to undo.")
            return
        self._restore(snapshot)
        self._reset_line_anchor()
        self.mark_dirty()
        self.mark(*Change.ALL)
        self.notify()

    def redo(self) -> None:
        self.stop_animation()
        snapshot = self.history.redo(self._snapshot())
        if snapshot is None:
            self.view.set_status("Nothing to redo.")
            return
        self._restore(snapshot)
        self._reset_line_anchor()
        self.mark_dirty()
        self.mark(*Change.ALL)
        self.notify()

    def mark(self, *aspects: str) -> None:
        """
        Queue view refresh aspects; call notify() once at the end of a use-case.
        """
        self._changed.update(aspects)

    def notify(self) -> None:
        """
        Broadcast the queued aspects to the view; the view decides what to repaint.
        """
        if not self._changed:
            return
        pixel = self._pixel_hint
        self._pixel_hint = None
        aspects = set(self._changed)
        self._changed.clear()
        self.view.sync(aspects, pixel)

    def mark_dirty(self, dirty: bool = True) -> None:
        self.dirty = dirty
        self.mark(Change.META)

    def _reset_line_anchor(self) -> None:
        """
        Forget the Shift+click line origin.
        """
        self._line_anchor = None

    def set_project(self, project: Project, file_path: str | None) -> None:
        self.stop_animation()
        self.project = project
        self.file_path = file_path
        self.current_sprite_index = 0
        self.selected_palette_index = 0
        self.active_tool = Tool.PENCIL
        self.sprite_clipboard = None
        self.dirty = False
        self._changed.clear()
        self._pixel_hint = None
        self.history.reset()
        self._stroke_recorded = True
        self._reset_line_anchor()
        self.mark(*Change.ALL)
        self.mark(Change.TOOL)
        self.notify()
        self.view.set_status("Pencil tool: left click paints with the selected color, right click paints "
                             "color 0. Shift+left click draws a line from the last pixel painted.")



    def on_canvas_click(self,
                        x: int,
                        y: int,
                        erase: bool = False,
                        stroke_start: bool = False,
                        shift: bool = False) -> None:
        """
        Dispatch a canvas click to the active tool. Shift+click with the
        pencil draws a line from the last pixel painted with the selected
        color. When that is not possible it behaves as a regular click.
        """
        if self.active_tool is Tool.FILL:
            if stroke_start:
                self.fill(x, y, erase)
            return
        if shift and stroke_start and not erase and self._draw_line_from_anchor(x, y):
            return
        self.on_paint(x, y, erase, stroke_start)

    def _draw_line_from_anchor(self, x: int, y: int) -> bool:
        """
        Paint the pencil line from the anchor to (x, y) with the selected
        palette color as one undo step. Returns False if it ends painting
        nothing.
        """
        if self.animating:
            return False
        if not (0 <= x < self.project.width and 0 <= y < self.project.height):
            return False
        value = self.selected_palette_index
        anchor = self._line_anchor
        if anchor is None or anchor.value != value:
            self.view.set_status("No line origin for this color: painted single pixel.")
            return False
        snapshot = self._snapshot()
        if self.sprite.draw_line(anchor.x, anchor.y, x, y, value) == 0:
            return False
        self.history.record(snapshot)
        self._line_anchor = _LineAnchor(x, y, value)
        self.mark(Change.PIXELS)
        self.mark_dirty()
        self.notify()
        self.view.set_status(f"Line ({anchor.x}, {anchor.y}) -> ({x}, {y}) with palette color {value}.")
        return True

    def on_paint(self, x: int, y: int, erase: bool = False, stroke_start: bool = False) -> None:
        if self.animating:
            return
        if not (0 <= x < self.project.width and 0 <= y < self.project.height):
            return
        value = 0 if erase else self.selected_palette_index
        if self.sprite.get(x, y) == value:
            return
        if stroke_start:
            self._stroke_recorded = False
        if not self._stroke_recorded:
            self.history.record(self._snapshot())
            self._stroke_recorded = True
        self.sprite.set(x, y, value)
        self._line_anchor = _LineAnchor(x, y, value)
        self.mark(Change.PIXELS)
        self._pixel_hint = (x, y)
        self.mark_dirty()
        self.notify()

    def fill(self, x: int, y: int, erase: bool = False) -> None:
        """
        Fill the connected region around (x, y) with one undo step.
        """
        if self.animating:
            return
        if not (0 <= x < self.project.width and 0 <= y < self.project.height):
            return
        value = 0 if erase else self.selected_palette_index
        if self.sprite.get(x, y) == value:
            return
        self.history.record(self._snapshot())
        self.sprite.flood_fill(x, y, value)
        self.mark(Change.PIXELS)
        self.mark_dirty()
        self.notify()

    def on_canvas_motion(self, x: int, y: int) -> None:
        if 0 <= x < self.project.width and 0 <= y < self.project.height:
            value = self.sprite.get(x, y)
            cpc = self.project.palette[value]
            self.view.set_status(f"Pixel ({x}, {y})  ->  palette {value} - {CPC_COLOR_NAMES[cpc]}")
        else:
            self.view.set_status("")

    
    def select_palette_index(self, index: int) -> None:
        if not 0 <= index < len(self.project.palette):
            return
        self.selected_palette_index = index
        self.mark(Change.PALETTE)
        self.notify()

    def select_tool(self, tool: Tool) -> None:
        if not isinstance(tool, Tool) or tool == self.active_tool:
            return
        self.active_tool = tool
        self.mark(Change.TOOL)
        self.notify()
        self.view.set_status(f"{tool.value} tool selected.")

    def add_palette_color(self) -> None:
        palette = self.project.palette
        if len(palette) >= self.project.max_colors:
            self.view.info(
                APP_NAME,
                f"{MODE_LABELS[self.project.video_mode]} only allows {self.project.max_colors} colors."
            )
            return
        chosen: int | None = self.view.ask_palette_color("Add color to the palette", forbidden=palette)
        if chosen is None:
            return
        self.history.record(self._snapshot())
        palette.append(chosen)
        self.selected_palette_index = len(palette) - 1
        self.mark_dirty()
        self.mark(Change.PALETTE)
        self.notify()

    def change_palette_color(self, index: int | None = None) -> None:
        if index is None:
            index = self.selected_palette_index
        if not 0 <= index < len(self.project.palette):
            return
        current = self.project.palette[index]
        forbidden = [c for i, c in enumerate(self.project.palette) if i != index]
        chosen: int | None = self.view.ask_palette_color(
            f"Change palette color {index}",
            current=current,
            forbidden=forbidden
        )
        if chosen is None or chosen == current:
            return
        self.history.record(self._snapshot())
        self.project.palette[index] = chosen
        self.mark_dirty()
        self.mark(Change.PALETTE, Change.PIXELS)
        self.notify()

    def remove_palette_color(self) -> None:
        palette = self.project.palette
        if len(palette) <= 1:
            self.view.info(APP_NAME, "The palette must keep at least one color.")
            return
        index = self.selected_palette_index
        yes = self.view.confirm(APP_NAME, f"Remove palette color {index}?\nPixels using it will be set to color 0.")
        if not yes:
            return
        self.history.record(self._snapshot())
        mapping: dict[int, int] = {}
        for i in range(len(palette)):
            if i == index:
                mapping[i] = 0
            elif i > index:
                mapping[i] = i - 1
            else:
                mapping[i] = i
        palette.pop(index)
        for sprite in self.project.sprites:
            sprite.remap(mapping)
        self.selected_palette_index = min(index, len(palette) - 1)
        self._reset_line_anchor()
        self.mark_dirty()
        self.mark(Change.PALETTE, Change.PIXELS)
        self.notify()


    def on_sprite_selected(self, index: int) -> None:
        if index == self.current_sprite_index:
            return
        self.current_sprite_index = index
        self._reset_line_anchor()
        self.mark(Change.PIXELS)
        self.notify()

    def select_sprite(self, index: int) -> None:
        # Internal helper: queues refreshes; the caller's public use-case notifies.
        self.current_sprite_index = max(0, min(index, len(self.project.sprites) - 1))
        self._reset_line_anchor()
        self.mark(Change.SPRITES, Change.PIXELS)

    def add_sprite(self) -> None:
        self.history.record(self._snapshot())
        self.project.sprites.insert(self.current_sprite_index + 1,
                                    Sprite(self.project.width, self.project.height))
        self.select_sprite(self.current_sprite_index + 1)
        self.mark_dirty()
        self.notify()

    def duplicate_sprite(self) -> None:
        self.history.record(self._snapshot())
        self.project.sprites.insert(self.current_sprite_index + 1, self.sprite.clone())
        self.select_sprite(self.current_sprite_index + 1)
        self.mark_dirty()
        self.notify()

    def delete_sprite(self) -> None:
        if len(self.project.sprites) <= 1:
            self.view.info(APP_NAME, "A project must always keep at least one sprite.")
            return
        if not self.view.confirm(APP_NAME, f"Delete sprite {self.current_sprite_index + 1}?"):
            return
        self.stop_animation()
        self.history.record(self._snapshot())
        self.project.sprites.pop(self.current_sprite_index)
        self.select_sprite(min(self.current_sprite_index, len(self.project.sprites) - 1))
        self.mark_dirty()
        self.notify()

    def move_sprite(self, offset: int) -> None:
        target = self.current_sprite_index + offset
        if not 0 <= target < len(self.project.sprites):
            return
        sprites = self.project.sprites
        self.history.record(self._snapshot())
        sprites[self.current_sprite_index], sprites[target] = sprites[target], sprites[self.current_sprite_index]
        self.select_sprite(target)
        self.mark_dirty()
        self.notify()

    def clear_sprite(self) -> None:
        self.history.record(self._snapshot())
        self.sprite.clear()
        self._reset_line_anchor()
        self.mark_dirty()
        self.mark(Change.PIXELS)
        self.notify()

    def flip_horizontal(self) -> None:
        self.history.record(self._snapshot())
        self.sprite.flip_horizontal()
        self.mark_dirty()
        self.mark(Change.PIXELS)
        self.notify()

    def flip_vertical(self) -> None:
        self.history.record(self._snapshot())
        self.sprite.flip_vertical()
        self.mark_dirty()
        self.mark(Change.PIXELS)
        self.notify()

    def copy_sprite(self) -> None:
        self.sprite_clipboard = self.sprite.clone()
        self.view.set_status(f"Sprite {self.current_sprite_index + 1} copied ({self.sprite.width}x{self.sprite.height}).")

    def paste_sprite(self) -> None:
        if self.sprite_clipboard is None:
            self.view.info(APP_NAME, "There is no copied sprite to paste.")
            return
        source = self.sprite_clipboard
        target = self.sprite
        if (source.width, source.height) != (target.width, target.height):
            self.view.warn(
                APP_NAME,
                f"Cannot paste: the copied sprite is {source.width}x{source.height} and this one is {target.width}x{target.height}."
            )
            return
        pasted = source.clone()
        # Do a clamp so any color out of current palette size goes to 0
        pasted.remap({i: i for i in range(len(self.project.palette))})
        self.history.record(self._snapshot())
        self.project.sprites[self.current_sprite_index] = pasted
        self._reset_line_anchor()
        self.mark_dirty()
        self.mark(Change.PIXELS)
        self.notify()
        self.view.set_status("Sprite pasted into sprite %d." % (self.current_sprite_index + 1))

    def toggle_animation(self) -> None:
        if self.animating:
            self.stop_animation()
        else:
            if len(self.project.sprites) < 2:
                self.view.info(APP_NAME, "Add more sprites to preview an animation.")
                return
            self.animating = True
            self.animation_frame = self.current_sprite_index
            self.view.set_animation_button_text("Stop")
            self._animate()

    def _animate(self) -> None:
        if not self.animating:
            return
        self.animation_frame = (self.animation_frame + 1) % len(self.project.sprites)
        self.mark(Change.PREVIEW)
        self.notify()
        self.animation_job = self.view.after(ANIMATION_DELAY, self._animate)

    def stop_animation(self) -> None:
        if self.animation_job is not None:
            self.view.after_cancel(self.animation_job)
            self.animation_job = None
        if self.animating:
            self.animating = False
            self.view.set_animation_button_text("Play")
            self.mark(Change.PREVIEW)
            self.notify()


    def confirm_discard(self) -> bool:
        if not self.dirty:
            return True
        answer: bool | None = self.view.confirm_save_discard(
            APP_NAME,
            "The project has unsaved changes.\nDo you want to save it now?"
        )
        if answer is None:
            return False
        if answer:
            return self.save_project()
        return True

    def new_project(self) -> None:
        if not self.confirm_discard():
            return
        settings: tuple[int, int, int] | None = self.view.ask_new_project_settings()
        if settings is None:
            return
        mode, width, height = settings
        self.set_project(Project(width, height, mode), None)

    def open_project(self) -> None:
        if not self.confirm_discard():
            return
        path: str = self.view.pick_open_path("Open Tixel Project")
        if not path:
            return
        try:
            project = persistence.load_project(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self.view.error(APP_NAME, f"Could not open the project:\n{error}")
            return
        self.set_project(project, path)
        self.view.set_status(f"Loaded {path}")

    def save_project(self) -> bool:
        if not self.file_path:
            return self.save_project_as()
        return self._write_project(self.file_path)

    def save_project_as(self) -> bool:
        path = self.view.pick_save_path("Save Tixel Project", self.project.name + FILE_EXT)
        if not path:
            return False
        return self._write_project(path)

    def _write_project(self, path: str) -> bool:
        try:
            self.project.name = os.path.splitext(os.path.basename(path))[0]
            persistence.save_project(path, self.project)
        except OSError as error:
            self.view.error(APP_NAME, f"Could not save the project:\n{error}")
            return False
        self.file_path = path
        self.mark_dirty(False)
        self.notify()
        self.view.set_status(f"Saved {path}")
        return True

    def code_generate_basic(self) -> None:
        conv = CodeConverter(self.project)
        code = conv.code_bas_pal(self.project.name)
        for i,sp in enumerate(self.project.sprites):
            code += conv.code_bas_img(sp, self.project.name + f"{i:02d}")
        self.view.code_show(code)

    def code_generate_abasc(self) -> None:
        conv = CodeConverter(self.project)
        code = conv.code_abasc_pal(self.project.name)
        for i,sp in enumerate(self.project.sprites):
            code += conv.code_abasc_img(sp, self.project.name + f"{i:02d}")
        self.view.code_show(code)

    def code_generate_c(self) -> None:
        conv = CodeConverter(self.project)
        code = conv.code_c_pal(self.project.name)
        for i,sp in enumerate(self.project.sprites):
            code += conv.code_c_img(sp, self.project.name + f"{i:02d}")
        self.view.code_show(code)

    def code_generate_asm(self) -> None:
        conv = CodeConverter(self.project)
        code = conv.code_asm_pal(self.project.name)
        for i,sp in enumerate(self.project.sprites):
            code += conv.code_asm_img(sp, self.project.name + f"{i:02d}")
        self.view.code_show(code)

    def show_help(self) -> None:
        self.view.info(
            f"{APP_NAME} - Quick Help",
            "File > New Project asks for the video mode and the resolution "
            f"(up to {MAX_SIZE}x{MAX_SIZE}). They cannot be changed afterwards.\n\n"
            "Bottom bar: the project palette. Add colors from the 27 available "
            "colors, up to the limit of the video mode (Mode 0: 16, Mode 1: 4, "
            "Mode 2: 2).\n\n"
            "Tools menu / toolbar: Pencil paints single pixels by dragging and "
            "Shift+left click draws a line from the last pixel painted with the "
            "selected color (polyline chaining is supported); Fill floods the "
            "connected region of the clicked color with the "
            "selected palette color.\n\n"
            "Work area: left click applies the active tool with the selected "
            "palette color, right click applies it with color 0.\n\n"
            "Transform > Flip Horizontally / Flip Vertically acts on the "
            "current sprite.\n\n"
            "Left bar: the sprites of the animation. Add, duplicate, reorder or "
            "delete them (at least one must remain) and preview the animation.\n\n"
            "Ctrl+N new, Ctrl+O open, Ctrl+S save, Ctrl+C copy sprite, "
            "Ctrl+V paste sprite, Ctrl+Z undo, Ctrl+Y redo.\n\n"
            "Undo/redo covers whole editing actions (a paint drag counts "
            "as one step); selection changes are not recorded."
        )

    def show_about(self) -> None:
        self.view.info(
            f"About {APP_NAME}",
            f"{APP_NAME} {APP_VERSION}\nSprite editor for Amstrad CPC.\n\n"
            f"Modes 0, 1 and 2, up to {MAX_SIZE}x{MAX_SIZE} pixels,\n"
            "palettes taken from the 27 Amstrad CPC colors."
        )


    def on_exit(self) -> None:
        if not self.confirm_discard():
            return
        self.stop_animation()
        self.view.destroy()
