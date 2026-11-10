"""
Shift+click pencil line drawing tests (controller level, headless).

From project source directory:
python3 -m unittest tests/test_controller_line.py
"""

import unittest
import controllers
from constants import Tool
from .mocks import MockView

class TestTixelControllerLine(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = controllers.TixelController(self.view)  # type: ignore[arg-type]
        self.ctrl.selected_palette_index = 1

    def paint_anchor(self, x: int, y: int) -> None:
        """Simulate a regular pencil click (the anchor of the next line)."""
        self.ctrl.on_canvas_click(x, y, stroke_start=True)

    def shift_click(self, x: int, y: int) -> None:
        self.ctrl.on_canvas_click(x, y, stroke_start=True, shift=True)

    def test_shift_click_draws_line_from_anchor(self) -> None:
        self.paint_anchor(0, 0)
        self.view.calls.clear()
        self.shift_click(3, 3)
        for x, y in ((0, 0), (1, 1), (2, 2), (3, 3)):
            self.assertEqual(self.ctrl.sprite.get(x, y), 1)
        self.assertIn("sync:meta,pixels", self.view.calls)
        self.assertNotIn("sync:meta,pixels(3,3)", self.view.calls)
        self.assertIn("Line (0, 0)", self.view.status_text)

    def test_line_is_exactly_one_undo_step(self) -> None:
        self.paint_anchor(0, 0)
        self.shift_click(3, 3)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)
        self.assertEqual(self.ctrl.sprite.get(3, 3), 0)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertFalse(self.ctrl.history.can_undo)

    def test_shift_click_without_anchor_paints_single_pixel(self) -> None:
        self.shift_click(2, 2)
        self.assertEqual(self.ctrl.sprite.get(2, 2), 1)
        self.assertEqual(self.ctrl.sprite.get(1, 1), 0)
        self.assertIn("No line origin", self.view.status_text)

    def test_shift_click_color_mismatch_paints_single_pixel(self) -> None:
        self.view.palette_color_return = 3
        self.ctrl.add_palette_color()
        self.ctrl.selected_palette_index = 2
        self.paint_anchor(0, 0)
        self.ctrl.selected_palette_index = 1
        self.shift_click(4, 4)
        self.assertEqual(self.ctrl.sprite.get(4, 4), 1)
        self.assertEqual(self.ctrl.sprite.get(2, 2), 0)
        self.assertIn("No line origin", self.view.status_text)
        self.shift_click(6, 4)
        self.assertEqual(self.ctrl.sprite.get(5, 4), 1)
        self.assertEqual(self.ctrl.sprite.get(6, 4), 1)

    def test_chained_shift_clicks_draw_polyline(self) -> None:
        self.paint_anchor(0, 0)
        self.shift_click(3, 3)
        self.shift_click(6, 3)
        for x, y in ((4, 3), (5, 3), (6, 3)):
            self.assertEqual(self.ctrl.sprite.get(x, y), 1)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)

    def test_anchor_reset_when_switching_sprite(self) -> None:
        self.paint_anchor(0, 0)
        self.ctrl.add_sprite()
        self.shift_click(3, 3)
        self.assertEqual(self.ctrl.sprite.get(3, 3), 1)
        self.assertEqual(self.ctrl.sprite.get(1, 1), 0)
        self.assertIn("No line origin", self.view.status_text)

    def test_anchor_reset_after_undo(self) -> None:
        self.paint_anchor(0, 0)
        self.shift_click(3, 3)
        self.ctrl.undo()
        self.shift_click(6, 6)
        self.assertEqual(self.ctrl.sprite.get(6, 6), 1)
        self.assertEqual(self.ctrl.sprite.get(4, 4), 0)
        self.assertIn("No line origin", self.view.status_text)

    def test_shift_click_blocked_while_animating(self) -> None:
        self.paint_anchor(0, 0)
        self.ctrl.animating = True
        self.view.calls.clear()
        self.shift_click(3, 3)
        self.assertEqual(self.ctrl.sprite.get(3, 3), 0)
        self.assertEqual(self.view.calls, [])

    def test_shift_click_with_fill_tool_never_draws_line(self) -> None:
        self.paint_anchor(0, 0)
        self.ctrl.select_tool(Tool.FILL)
        self.shift_click(3, 3)
        self.assertEqual(self.ctrl.sprite.get(10, 10), 1)

    def test_noop_line_records_no_undo_step(self) -> None:
        self.paint_anchor(0, 0)
        self.view.calls.clear()
        self.shift_click(0, 0)
        self.assertEqual(self.view.calls, [])
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertFalse(self.ctrl.history.can_undo)

    def test_shift_click_out_of_bounds_is_ignored(self) -> None:
        self.paint_anchor(0, 0)
        self.view.calls.clear()
        self.shift_click(99, 99)
        self.assertEqual(self.view.calls, [])
        self.assertTrue(self.ctrl.dirty)


if __name__ == "__main__":
    unittest.main()
