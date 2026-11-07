"""
Tool selection and flood-fill behaviour at the controller level.

From the project source directory:
python3 -m unittest tests/test_controller_tools.py
"""

import unittest
from constants import Tool
from controllers import TixelController
from model import Project, Sprite
from .mocks import MockView


class TestControllerTools(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def _load_sprite(self, pixels: list[list[int]]) -> None:
        height = len(pixels)
        width = len(pixels[0])
        sprite = Sprite(width, height, pixels)
        project = Project(width=width, height=height, video_mode=0,
                          palette=[0, 1, 2], sprites=[sprite])
        self.ctrl.set_project(project, None)

    def test_initial_tool_is_pencil(self) -> None:
        self.assertIs(self.ctrl.active_tool, Tool.PENCIL)

    def test_select_tool_updates_state_and_notifies(self) -> None:
        self.view.calls.clear()
        self.ctrl.select_tool(Tool.FILL)
        self.assertIs(self.ctrl.active_tool, Tool.FILL)
        self.assertIn("sync:tool", self.view.calls)
        self.assertIn("Fill tool selected.", self.view.status_text)

    def test_select_same_tool_is_noop(self) -> None:
        self.view.calls.clear()
        self.ctrl.select_tool(Tool.PENCIL)
        self.assertEqual(self.view.calls, [])

    def test_select_invalid_tool_is_ignored(self) -> None:
        self.ctrl.select_tool("Fill")  # type: ignore[arg-type]
        self.assertIs(self.ctrl.active_tool, Tool.PENCIL)

    def test_on_canvas_click_dispatches_pencil(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_canvas_click(0, 0, stroke_start=True)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)

    def test_on_canvas_click_fill_ignores_motion(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.select_tool(Tool.FILL)
        self.ctrl.selected_palette_index = 1
        self.view.calls.clear()
        self.ctrl.on_canvas_click(0, 0, stroke_start=False)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual(self.view.calls, [])

    def test_on_canvas_click_fill_on_press(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.select_tool(Tool.FILL)
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_canvas_click(0, 0, stroke_start=True)
        self.assertEqual(self.ctrl.sprite.pixels, [[1, 1], [1, 1]])

    def test_fill_connected_region(self) -> None:
        self._load_sprite([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
        self.ctrl.selected_palette_index = 2
        self.ctrl.fill(0, 0)
        self.assertEqual(self.ctrl.sprite.pixels, [[2, 2, 1], [2, 1, 0], [1, 0, 0]])

    def test_fill_marks_dirty_and_notifies(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.selected_palette_index = 1
        self.view.calls.clear()
        self.ctrl.fill(0, 0)
        self.assertTrue(self.ctrl.dirty)
        self.assertIn("sync:meta,pixels", self.view.calls)

    def test_fill_is_one_undo_step(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.selected_palette_index = 1
        self.ctrl.fill(0, 0)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.pixels, [[0, 0], [0, 0]])

    def test_fill_same_color_is_noop(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.selected_palette_index = 0
        self.view.calls.clear()
        self.ctrl.fill(0, 0)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual(self.view.calls, [])

    def test_fill_out_of_bounds_is_noop(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.selected_palette_index = 1
        self.view.calls.clear()
        self.ctrl.fill(-1, 0)
        self.ctrl.fill(2, 2)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual(self.view.calls, [])

    def test_fill_blocked_while_animating(self) -> None:
        self._load_sprite([[0, 0], [0, 0]])
        self.ctrl.selected_palette_index = 1
        self.ctrl.animating = True
        self.ctrl.fill(0, 0)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertFalse(self.ctrl.dirty)

    def test_fill_erase_uses_color_zero(self) -> None:
        self._load_sprite([[1, 1], [1, 0]])
        self.ctrl.fill(0, 0, erase=True)
        self.assertEqual(self.ctrl.sprite.pixels, [[0, 0], [0, 0]])

    def test_set_project_resets_tool_to_pencil(self) -> None:
        self.ctrl.select_tool(Tool.FILL)
        self.view.calls.clear()
        self.ctrl.set_project(Project(), None)
        self.assertIs(self.ctrl.active_tool, Tool.PENCIL)
        self.assertIn("sync:meta,palette,pixels,sprites,tool", self.view.calls)


if __name__ == "__main__":
    unittest.main()
