"""
From project source directory:

python3 -m unittest test/test_controller_project.py
"""

import unittest
from unittest.mock import MagicMock, patch
from .mocks import MockView
from controllers import TixelController
from model import Project


class TestTixelControllerProject(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def test_set_project(self) -> None:
        p = Project(width=8, height=8, video_mode=1, palette=[0, 1], name="Test")
        self.ctrl.selected_palette_index = 1
        self.ctrl.current_sprite_index = 1
        self.ctrl.dirty = True

        self.ctrl.set_project(p, "/tmp/fake.tixel")
        self.assertIs(self.ctrl.project, p)
        self.assertEqual(self.ctrl.file_path, "/tmp/fake.tixel")
        self.assertEqual(self.ctrl.current_sprite_index, 0)
        self.assertEqual(self.ctrl.selected_palette_index, 0)
        self.assertFalse(self.ctrl.dirty)
        self.assertIn("sync:meta,palette,pixels,sprites,tool", self.view.calls)
        self.assertIs(self.view.toolbar_project, p)
        self.assertEqual(self.view.title_info, ("/tmp/fake.tixel", False))

    @patch.object(TixelController, "confirm_discard", return_value=True)
    def test_new_project(self, mock_confirm: MagicMock) -> None:
        self.view.new_project_return = (1, 6, 6)
        self.ctrl.new_project()
        self.assertEqual(self.ctrl.project.width, 6)
        self.assertEqual(self.ctrl.project.video_mode, 1)
        mock_confirm.assert_called_once()

    def test_confirm_discard_not_dirty(self) -> None:
        self.ctrl.dirty = False
        self.assertTrue(self.ctrl.confirm_discard())

    def test_confirm_discard_cancel(self) -> None:
        self.view.confirm_discard_return = None
        self.ctrl.dirty = True
        self.assertFalse(self.ctrl.confirm_discard())
        self.assertIn("confirm3", self.view.calls)

    @patch.object(TixelController, "save_project", return_value=True)
    def test_confirm_discard_save(self, mock_save: MagicMock) -> None:
        self.view.confirm_discard_return = True
        self.ctrl.dirty = True
        self.assertTrue(self.ctrl.confirm_discard())
        self.assertIn("confirm3", self.view.calls)
        mock_save.assert_called_once()

    @patch.object(TixelController, "confirm_discard", return_value=False)
    def test_new_project_cancel_discard(self, mock_confirm: MagicMock) -> None:
        old_width = self.ctrl.project.width
        self.ctrl.new_project()
        self.assertEqual(self.ctrl.project.width, old_width)
        mock_confirm.assert_called_once()

    @patch.object(TixelController, "confirm_discard", return_value=True)
    def test_open_project_cancel_dialog(self, mock_confirm: MagicMock) -> None:
        old_project = self.ctrl.project
        self.view.open_path_return = ""
        self.ctrl.open_project()
        self.assertIs(self.ctrl.project, old_project)
        mock_confirm.assert_called_once()
        self.assertIn("pick_open", self.view.calls)

    def test_open_project_invalid_file(self) -> None:
        self.view.open_path_return = "/tmp/fake.tixel"
        with patch("persistence.load_project", side_effect=ValueError("bad")):
            self.ctrl.open_project()
            self.assertIn("error", self.view.calls)

    def test_save_project_as_cancel(self) -> None:
        self.view.save_path_return = ""
        self.assertFalse(self.ctrl.save_project_as())
        self.assertIn("pick_save", self.view.calls)

    def test_save_project_no_file_path_calls_save_as(self) -> None:
        self.ctrl.file_path = None
        with patch.object(self.ctrl, "save_project_as", return_value=True) as mock_save_as:
            self.assertTrue(self.ctrl.save_project())
            mock_save_as.assert_called_once()

    @patch("persistence.save_project", side_effect=OSError("disk full"))
    def test_write_project_error(self, mock_save: MagicMock) -> None:
        saved = self.ctrl._write_project("/tmp/fail.tixel")
        mock_save.assert_called_once()
        self.assertFalse(saved)
        self.assertIn("error", self.view.calls)


if __name__ == "__main__":
    unittest.main()
