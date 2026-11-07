"""
Transform (flip) behaviour at the controller level.

From the project source directory:
python3 -m unittest tests/test_controller_transform.py
"""

import unittest
from controllers import TixelController
from model import Project, Sprite
from .mocks import MockView


class TestControllerTransform(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def _load(self, pixels: list[list[int]]) -> None:
        height = len(pixels)
        width = len(pixels[0])
        project = Project(
            width=width,
            height=height,
            video_mode=0,
            palette=[0, 1, 2, 3, 4, 5],
            sprites=[Sprite(width, height, pixels)]
        )
        self.ctrl.set_project(project, None)
        self.view.calls.clear()

    def test_flip_horizontal_current_sprite(self) -> None:
        self._load([[0, 1, 2], [3, 4, 5]])
        self.ctrl.flip_horizontal()
        self.assertEqual(self.ctrl.sprite.pixels, [[2, 1, 0], [5, 4, 3]])

    def test_flip_vertical_current_sprite(self) -> None:
        self._load([[0, 1, 2], [3, 4, 5]])
        self.ctrl.flip_vertical()
        self.assertEqual(self.ctrl.sprite.pixels, [[3, 4, 5], [0, 1, 2]])

    def test_flip_only_affects_current_sprite(self) -> None:
        first = Sprite(2, 2, [[0, 1], [2, 3]])
        second = Sprite(2, 2, [[0, 1], [2, 3]])
        project = Project(width=2, height=2, video_mode=0,
                          palette=[0, 1, 2, 3], sprites=[first, second])
        self.ctrl.set_project(project, None)
        self.ctrl.current_sprite_index = 1
        self.ctrl.flip_horizontal()
        self.assertEqual(first.pixels, [[0, 1], [2, 3]])
        self.assertEqual(second.pixels, [[1, 0], [3, 2]])

    def test_flip_is_one_undo_step(self) -> None:
        self._load([[0, 1, 2], [3, 4, 5]])
        self.ctrl.flip_horizontal()
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.pixels, [[0, 1, 2], [3, 4, 5]])

    def test_redo_reapplies_flip(self) -> None:
        self._load([[0, 1, 2], [3, 4, 5]])
        self.ctrl.flip_vertical()
        self.ctrl.undo()
        self.ctrl.redo()
        self.assertEqual(self.ctrl.sprite.pixels, [[3, 4, 5], [0, 1, 2]])

    def test_flip_marks_dirty_and_broadcasts_pixels(self) -> None:
        self._load([[0, 1], [2, 3]])
        self.ctrl.flip_horizontal()
        self.assertTrue(self.ctrl.dirty)
        self.assertIn("sync:meta,pixels", self.view.calls)

    def test_flip_preserves_selection(self) -> None:
        self._load([[0, 1], [2, 3]])
        self.ctrl.selected_palette_index = 2
        self.ctrl.flip_vertical()
        self.assertEqual(self.ctrl.current_sprite_index, 0)
        self.assertEqual(self.ctrl.selected_palette_index, 2)


if __name__ == "__main__":
    unittest.main()
