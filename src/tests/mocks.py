"""
Mock to test TixelController without using Tkinter real objects.

All calls to the view are stored in self.calls so we can check
later what dialogs where called.
"""

from model import Project
from constants import Change
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import TixelController

class MockView:

    def __init__(self) -> None:
        self.controller: "TixelController" | None = None
        self.calls: list[str] = []
        self.status_text: str = ""
        self.title_info: tuple[str | None, bool] | None = None
        self.toolbar_project: Project | None = None
        self.after_jobs: dict[int, object] = {}
        self._counter: int = 0
        self.animation_button_text: str = "Play"
        self.palette_color_return: int | None = 1
        self.new_project_return: tuple[int, int, int] | None = (0, 8, 8)
        self.confirm_return: bool = False
        self.confirm_discard_return: bool | None = None
        self.open_path_return: str = ""
        self.save_path_return: str = ""
        self.last_dialog_message: str = ""

    def set_controller(self, controller: "TixelController") -> None:
        self.controller = controller

    def sync(self, aspects: set[str], pixel: tuple[int, int] | None = None) -> None:
        label = ",".join(sorted(aspects))
        if pixel is not None:
            label += f"({pixel[0]},{pixel[1]})"
        self.calls.append(f"sync:{label}")
        if self.controller is not None and Change.META in aspects:
            self.toolbar_project = self.controller.project
            self.title_info = (self.controller.file_path, self.controller.dirty)

    def set_status(self, text: str) -> None:
        self.status_text = text
        self.calls.append(f"set_status:{text}")

    def set_animation_button_text(self, text: str) -> None:
        self.animation_button_text = text
        self.calls.append(f"anim_button:{text}")

    def info(self, title: str, message: str) -> None:
        self.last_dialog_message = message
        self.calls.append("info")

    def warn(self, title: str, message: str) -> None:
        self.last_dialog_message = message
        self.calls.append("warn")

    def error(self, title: str, message: str) -> None:
        self.last_dialog_message = message
        self.calls.append("error")

    def confirm(self, title: str, message: str) -> bool:
        self.last_dialog_message = message
        self.calls.append("confirm")
        return self.confirm_return

    def confirm_save_discard(self, title: str, message: str) -> bool | None:
        self.last_dialog_message = message
        self.calls.append("confirm3")
        return self.confirm_discard_return

    def pick_open_path(self, title: str) -> str:
        self.calls.append("pick_open")
        return self.open_path_return

    def pick_save_path(self, title: str, initialfile: str) -> str:
        self.calls.append("pick_save")
        return self.save_path_return

    def ask_palette_color(self, title: str, current: int | None = None, forbidden: list[int] = []) -> int | None:
        return self.palette_color_return

    def ask_new_project_settings(self) -> tuple[int, int, int] | None:
        return self.new_project_return

    def after(self, delay: int, func: object) -> int:
        self._counter += 1
        self.after_jobs[self._counter] = func
        return self._counter

    def after_cancel(self, job: int) -> None:
        self.after_jobs.pop(job, None)

    def destroy(self) -> None:
        self.calls.append("destroy")
