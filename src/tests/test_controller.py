"""
From project source directory:

python3 -m unittest test/test_controller.py
"""

import unittest
from controllers import TixelController
from unittest.mock import MagicMock, patch
from .mocks import MockView

class TestTixelController(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def test_initial_state(self) -> None:
        self.assertIsNotNone(self.ctrl.project)
        self.assertGreater(len(self.ctrl.project.palette), 1)
        self.assertIsNone(self.ctrl.file_path)
        self.assertFalse(self.ctrl.dirty)
        self.assertEqual(self.ctrl.current_sprite_index, 0)
        self.assertEqual(self.ctrl.selected_palette_index, 0)
        self.assertIsNone(self.ctrl.sprite_clipboard)

    def test_mark_dirty(self) -> None:
        self.ctrl.mark_dirty(True)
        self.assertTrue(self.ctrl.dirty)
        self.ctrl.notify()
        self.assertIn("sync:meta", self.view.calls)

    def test_show_help(self) -> None:
        self.ctrl.show_help()
        self.assertIn("info", self.view.calls)

    def test_show_about(self) -> None:
        self.ctrl.show_about()
        self.assertIn("info", self.view.calls)

    def test_on_exit(self) -> None:
        with patch.object(self.ctrl, "confirm_discard", return_value=True):
            self.ctrl.on_exit()
            self.assertIn("destroy", self.view.calls)


if __name__ == "__main__":
    unittest.main()
