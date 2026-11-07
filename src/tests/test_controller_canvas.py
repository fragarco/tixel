"""
From project source directory:

python3 -m unittest test/test_controller_canvas.py
"""

import unittest
import controllers
from .mocks import MockView

class TestTixelControllerCanvas(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = controllers.TixelController(self.view)  # type: ignore[arg-type]

    def test_on_paint_within_bounds(self) -> None:
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, erase=False)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)
        self.assertTrue(self.ctrl.dirty)
        self.assertIn("sync:meta,pixels(0,0)", self.view.calls)

    def test_on_paint_out_of_bounds(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(-1, -1, erase=False)
        self.ctrl.on_paint(99, 99, erase=False)
        self.assertFalse(self.ctrl.dirty)

    def test_on_paint_when_animating_blocked(self) -> None:
        self.ctrl.animating = True
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, erase=False)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertFalse(self.ctrl.dirty)

    def test_on_paint_no_change_no_dirty(self) -> None:
        self.view.calls.clear()
        self.ctrl.selected_palette_index = 0
        self.ctrl.on_paint(0, 0, erase=False)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual(self.view.calls, [])

    def test_on_canvas_motion_inside_showinfo(self) -> None:
        self.ctrl.on_canvas_motion(0, 0)
        self.assertIn("Pixel (0, 0)", self.view.status_text)

    def test_on_canvas_motion_outside_emptyinfo(self) -> None:
        self.ctrl.on_canvas_motion(99, 99)
        self.assertEqual(self.view.status_text, "")

if __name__ == "__main__":
    unittest.main()
