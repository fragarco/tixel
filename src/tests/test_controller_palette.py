"""
From project source directory:

python3 -m unittest test/test_palette_palette.py
"""

import unittest
import controllers
from unittest.mock import MagicMock, patch
from .mocks import MockView
from model import Project, Sprite


class TestTixelControllerPalette(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = controllers.TixelController(self.view)  # type: ignore[arg-type]

    def test_select_palette_index_valid(self) -> None:
        self.ctrl.select_palette_index(1)
        self.assertEqual(self.ctrl.selected_palette_index, 1)
        self.assertIn("sync:palette", self.view.calls)

    def test_select_palette_index_invalid(self) -> None:
        self.ctrl.select_palette_index(99)
        self.assertEqual(self.ctrl.selected_palette_index, 0)

    def test_add_palette_color(self) -> None:
        self.view.palette_color_return = 5
        before = len(self.ctrl.project.palette)
        self.ctrl.add_palette_color()
        self.assertEqual(len(self.ctrl.project.palette), before + 1)
        self.assertTrue(self.ctrl.dirty)

    def test_add_palette_color_max_reached(self) -> None:
        p = Project(width=4, height=4, video_mode=1, palette=[0, 1, 2, 3], name="X")
        self.ctrl.set_project(p, file_path=None)
        self.ctrl.add_palette_color()
        self.assertIn("info", self.view.calls)
        self.assertEqual(len(self.ctrl.project.palette), 4)

    def test_change_palette_color(self) -> None:
        self.ctrl.project.palette[0] = 0
        self.view.palette_color_return = 10
        self.ctrl.change_palette_color(0)
        self.assertEqual(self.ctrl.project.palette[0], 10)
        self.assertTrue(self.ctrl.dirty)

    def test_change_palette_color_cancel(self) -> None:
        self.view.palette_color_return = None
        before = list(self.ctrl.project.palette)
        self.ctrl.change_palette_color(0)
        self.assertEqual(self.ctrl.project.palette, before)

    def test_remove_palette_color(self) -> None:
        self.view.confirm_return = True
        self.ctrl.selected_palette_index = 1
        self.ctrl.sprite.set(0, 0, 1)
        before_len = len(self.ctrl.project.palette)
        self.ctrl.remove_palette_color()
        self.assertIn("confirm", self.view.calls)
        self.assertEqual(len(self.ctrl.project.palette), before_len - 1)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)

    def test_remove_palette_color_single(self) -> None:
        p = Project(width=2, height=2, video_mode=0, palette=[0], name="Single")
        self.ctrl.set_project(p, None)
        self.ctrl.remove_palette_color()
        self.assertIn("info", self.view.calls)
        self.assertEqual(len(self.ctrl.project.palette), 1)

if __name__ == "__main__":
    unittest.main()
