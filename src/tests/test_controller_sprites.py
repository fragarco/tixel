"""
From project source directory:

python3 -m unittest test/test_controller_sprites.py
"""

import unittest
from controllers import TixelController
from unittest.mock import MagicMock, patch
from .mocks import MockView
from model import Sprite

class TestTixelControllerSprites(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def test_add_sprite(self) -> None:
        before = len(self.ctrl.project.sprites)
        self.ctrl.add_sprite()
        self.assertEqual(len(self.ctrl.project.sprites), before + 1)
        self.assertEqual(self.ctrl.current_sprite_index, 1)
        self.assertTrue(self.ctrl.dirty)

    def test_on_sprite_selected(self) -> None:
        self.ctrl.add_sprite()
        self.view.calls.clear()
        self.ctrl.on_sprite_selected(0)
        self.assertEqual(self.ctrl.current_sprite_index, 0)
        self.assertIn("sync:pixels", self.view.calls)

    def test_select_sprite_clamped(self) -> None:
        self.ctrl.select_sprite(99)
        self.assertEqual(self.ctrl.current_sprite_index, len(self.ctrl.project.sprites) - 1)
        self.ctrl.select_sprite(-5)
        self.assertEqual(self.ctrl.current_sprite_index, 0)

    def test_duplicate_sprite(self) -> None:
        self.ctrl.sprite.set(0, 0, 1)
        self.ctrl.duplicate_sprite()
        self.assertEqual(len(self.ctrl.project.sprites), 2)
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)

    def test_delete_sprite(self) -> None:
        self.view.confirm_return = True
        self.ctrl.add_sprite()
        before = len(self.ctrl.project.sprites)
        self.ctrl.delete_sprite()
        self.assertIn("confirm", self.view.calls)
        self.assertEqual(len(self.ctrl.project.sprites), before - 1)

    def test_delete_sprite_single_error(self) -> None:
        self.assertEqual(len(self.ctrl.project.sprites), 1)
        self.ctrl.delete_sprite()
        self.assertIn("info", self.view.calls)

    def test_move_sprite(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.add_sprite()
        self.ctrl.current_sprite_index = 2
        self.ctrl.move_sprite(-1)
        self.assertEqual(self.ctrl.current_sprite_index, 1)
        self.assertTrue(self.ctrl.dirty)

    def test_move_sprite_out_of_bounds(self) -> None:
        self.ctrl.current_sprite_index = 0
        self.ctrl.move_sprite(-1)
        self.assertEqual(self.ctrl.current_sprite_index, 0)
        self.assertFalse(self.ctrl.dirty)

    def test_clear_sprite(self) -> None:
        self.ctrl.sprite.set(0, 0, 1)
        self.ctrl.clear_sprite()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertTrue(self.ctrl.dirty)
        self.assertIn("sync:meta,pixels", self.view.calls)

    def test_copy_sprite(self) -> None:
        self.ctrl.sprite.set(0, 0, 1)
        self.ctrl.copy_sprite()
        self.assertIsNotNone(self.ctrl.sprite_clipboard)
        self.assertEqual(self.ctrl.sprite_clipboard.get(0,0), 1) # type: ignore[union-attr]
        self.assertIn("copied", self.view.status_text)

    def test_paste_sprite_no_clipboard(self) -> None:
        self.ctrl.sprite_clipboard = None
        self.ctrl.paste_sprite()
        self.assertIn("info", self.view.calls)
        self.assertFalse(self.ctrl.dirty)

    def test_paste_sprite_dimension_mismatch(self) -> None:
        self.ctrl.sprite_clipboard = Sprite(99, 99)
        self.ctrl.paste_sprite()
        self.assertIn("warn", self.view.calls)
        self.assertFalse(self.ctrl.dirty)

    def test_paste_sprite_success(self) -> None:
        self.ctrl.copy_sprite()
        self.ctrl.sprite.set(0, 0, 1)
        self.ctrl.paste_sprite()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)
        self.assertTrue(self.ctrl.dirty)

    def test_toggle_animation_not_enough_sprites(self) -> None:
        self.assertEqual(len(self.ctrl.project.sprites), 1)
        self.ctrl.toggle_animation()
        self.assertIn("info", self.view.calls)
        self.assertFalse(self.ctrl.animating)

    def test_toggle_animation_start_stop(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.toggle_animation()
        self.assertTrue(self.ctrl.animating)
        self.assertEqual(self.view.animation_button_text, "Stop")
        self.ctrl.toggle_animation()
        self.assertFalse(self.ctrl.animating)
        self.assertEqual(self.view.animation_button_text, "Play")

    def test_animate(self) -> None:
        self.ctrl.add_sprite()
        self.view.calls.clear()
        self.ctrl.animating = True
        self.ctrl.animation_frame = 0
        self.ctrl._animate()
        self.assertEqual(self.ctrl.animation_frame, 1)
        self.assertIn("sync:preview", self.view.calls)
        self.assertIsNotNone(self.ctrl.animation_job)

    def test_stop_animation(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.toggle_animation()
        self.ctrl.stop_animation()
        self.assertFalse(self.ctrl.animating)
        self.assertIsNone(self.ctrl.animation_job)


if __name__ == "__main__":
    unittest.main()
