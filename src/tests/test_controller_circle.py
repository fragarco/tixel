"""
Two-click Circle tool tests (controller level, headless).

From project source directory:

python3 -m unittest tests/test_controller_circle.py
"""

import unittest
import controllers
from constants import Tool
from .mocks import MockView

class TestTixelControllerCircle(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = controllers.TixelController(self.view)  # type: ignore[arg-type]
        self.ctrl.selected_palette_index = 1
        self.ctrl.select_tool(Tool.CIRCLE)

    def click(self, x: int, y: int, erase: bool = False) -> None:
        self.ctrl.on_canvas_click(x, y, erase=erase, stroke_start=True)

    def test_first_click_only_sets_center(self) -> None:
        self.view.calls.clear()
        self.click(5, 5)
        self.assertEqual(self.ctrl.sprite.get(5, 5), 0)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual([c for c in self.view.calls if c.startswith("sync")], [])
        self.assertIn("Circle: click the edge", self.view.status_text)

    def test_two_clicks_draw_circle(self) -> None:
        self.click(5, 5)
        self.click(7, 5)
        for x, y in ((7, 5), (3, 5), (5, 7), (5, 3), (6, 7), (4, 3)):
            self.assertEqual(self.ctrl.sprite.get(x, y), 1)
        self.assertEqual(self.ctrl.sprite.get(6, 4), 0)
        self.assertIn("sync:meta,pixels", self.view.calls)
        self.assertIn("Circle centered at (5, 5) with radius 2", self.view.status_text)

    def test_circle_is_one_undo_step(self) -> None:
        self.click(5, 5)
        self.click(7, 5)
        self.ctrl.undo()
        for x, y in ((7, 5), (3, 5), (5, 7), (5, 3)):
            self.assertEqual(self.ctrl.sprite.get(x, y), 0)
        self.assertFalse(self.ctrl.history.can_undo)

    def test_center_cleared_after_completed_circle(self) -> None:
        self.click(5, 5)
        self.click(7, 5)
        self.click(9, 9)
        self.assertEqual(self.ctrl.sprite.get(9, 9), 0)
        self.assertIn("Circle: click the edge", self.view.status_text)

    def test_right_button_second_click_uses_color_zero(self) -> None:
        self.ctrl.select_tool(Tool.FILL)
        self.ctrl.on_canvas_click(10, 10, stroke_start=True)
        self.ctrl.select_tool(Tool.CIRCLE)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 1)
        self.click(5, 5)
        self.click(7, 5, erase=True)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 0)
        self.assertEqual(self.ctrl.sprite.get(6, 4), 1)

    def test_radius_is_chebyshev_for_diagonal_edge_click(self) -> None:
        self.click(5, 5)
        self.click(7, 7)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 1)
        self.assertEqual(self.ctrl.sprite.get(9, 5), 0)

    def test_pending_center_invalidated_by_tool_change(self) -> None:
        self.click(5, 5)
        self.ctrl.select_tool(Tool.PENCIL)
        self.ctrl.select_tool(Tool.CIRCLE)
        self.click(7, 5)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 0)
        self.click(9, 5)
        self.assertEqual(self.ctrl.sprite.get(9, 5), 1)
        self.assertEqual(self.ctrl.sprite.get(3, 5), 0)

    def test_pending_center_invalidated_by_sprite_change(self) -> None:
        self.click(5, 5)
        self.ctrl.add_sprite()
        self.click(7, 5)
        self.click(9, 5)
        self.assertEqual(self.ctrl.sprite.get(9, 5), 1)
        self.assertEqual(self.ctrl.sprite.get(3, 5), 0)

    def test_pending_center_invalidated_by_undo(self) -> None:
        self.ctrl.select_tool(Tool.PENCIL)
        self.ctrl.on_canvas_click(0, 0, stroke_start=True)
        self.ctrl.select_tool(Tool.CIRCLE)
        self.click(5, 5)
        self.ctrl.undo()
        self.click(5, 5)
        self.assertEqual(self.ctrl.sprite.get(5, 5), 0)

    def test_blocked_while_animating(self) -> None:
        self.click(5, 5)
        self.ctrl.animating = True
        self.view.calls.clear()
        self.click(7, 5)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 0)
        self.assertEqual(self.view.calls, [])

    def test_out_of_bounds_clicks_ignored(self) -> None:
        self.click(5, 5)
        self.click(99, 99)
        self.click(7, 5)
        self.assertEqual(self.ctrl.sprite.get(7, 5), 1)

    def test_motion_between_clicks_ignored(self) -> None:
        self.click(5, 5)
        self.ctrl.on_canvas_click(7, 7, stroke_start=False)
        self.assertEqual(self.ctrl.sprite.get(7, 7), 0)
        self.click(9, 5)
        self.assertEqual(self.ctrl.sprite.get(9, 5), 1)

    def test_noop_second_click_keeps_center_and_records_nothing(self) -> None:
        self.click(5, 5)
        self.click(7, 5)
        self.click(5, 5)
        self.view.calls.clear()
        self.click(7, 5)
        self.assertEqual(self.view.calls, [])
        self.click(9, 5)
        self.assertEqual(self.ctrl.sprite.get(9, 5), 1)


if __name__ == "__main__":
    unittest.main()
