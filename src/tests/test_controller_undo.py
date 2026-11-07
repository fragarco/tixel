"""
Undo/Redo behaviour at the controller level (headless, via MockView).

From the project source directory:
python3 -m unittest tests/test_controller_undo.py
"""

import unittest
from controllers import TixelController
from .mocks import MockView
from model import Project


class TestControllerUndo(unittest.TestCase):
    def setUp(self) -> None:
        self.view = MockView()
        self.ctrl = TixelController(self.view)  # type: ignore[arg-type]

    def test_paint_undo_redo(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(2, 3, erase=False, stroke_start=True)
        self.assertEqual(self.ctrl.sprite.get(2, 3), 1)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(2, 3), 0)
        self.ctrl.redo()
        self.assertEqual(self.ctrl.sprite.get(2, 3), 1)

    def test_stroke_is_one_undo_step(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True) 
        self.ctrl.on_paint(1, 0)
        self.ctrl.on_paint(2, 0)
        self.ctrl.on_paint(3, 0)
        self.ctrl.undo()
        for x in range(4):
            self.assertEqual(self.ctrl.sprite.get(x, 0), 0)

    def test_repaint_same_pixel_records_nothing(self) -> None:
        self.ctrl.selected_palette_index = 0
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.assertFalse(self.ctrl.history.can_undo)

    def test_erase_undo(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.on_paint(0, 0, erase=True, stroke_start=True)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)

    def test_add_sprite_undo(self) -> None:
        before = len(self.ctrl.project.sprites)
        self.ctrl.add_sprite()
        self.assertEqual(len(self.ctrl.project.sprites), before + 1)
        self.ctrl.undo()
        self.assertEqual(len(self.ctrl.project.sprites), before)

    def test_clear_sprite_undo_restores_pixels(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(1, 1, stroke_start=True)
        self.ctrl.clear_sprite()
        self.assertEqual(self.ctrl.sprite.get(1, 1), 0)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(1, 1), 1)

    def test_paste_sprite_undo(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.copy_sprite()
        self.ctrl.add_sprite()
        self.ctrl.paste_sprite()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 1)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.sprite.get(0, 0), 0)

    def test_move_sprite_undo(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.selected_palette_index = 1
        self.ctrl.current_sprite_index = 0
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.move_sprite(1)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.project.sprites[0].get(0, 0), 1)
        self.assertEqual(self.ctrl.project.sprites[1].get(0, 0), 0)

    def test_palette_remove_undo(self) -> None:
        self.view.confirm_return = True
        self.ctrl.selected_palette_index = 1
        self.ctrl.remove_palette_color()
        self.assertEqual(len(self.ctrl.project.palette), 1)
        self.ctrl.undo()
        self.assertEqual(len(self.ctrl.project.palette), 2)

    def test_palette_add_undo(self) -> None:
        self.view.palette_color_return = 5
        before = len(self.ctrl.project.palette)
        self.ctrl.add_palette_color()
        self.assertEqual(len(self.ctrl.project.palette), before + 1)
        self.ctrl.undo()
        self.assertEqual(len(self.ctrl.project.palette), before)

    def test_palette_change_undo(self) -> None:
        self.view.palette_color_return = 10
        self.ctrl.change_palette_color(0)
        self.assertEqual(self.ctrl.project.palette[0], 10)
        self.ctrl.undo()
        self.assertNotEqual(self.ctrl.project.palette[0], 10)

    def test_undo_on_empty_history(self) -> None:
        self.ctrl.undo()
        self.assertIn("Nothing to undo.", self.view.status_text)

    def test_new_edit_after_undo_clears_redo(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.undo()
        self.assertTrue(self.ctrl.history.can_redo)
        self.ctrl.selected_palette_index = 0
        self.ctrl.on_paint(5, 5, stroke_start=True)
        self.assertTrue(self.ctrl.history.can_redo)
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 1, stroke_start=True)
        self.assertFalse(self.ctrl.history.can_redo)

    def test_undo_restores_selection(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.select_sprite(0)
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.undo()
        self.assertEqual(self.ctrl.current_sprite_index, 0)

    def test_set_project_resets_history(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.assertTrue(self.ctrl.history.can_undo)
        self.ctrl.set_project(Project(), None)
        self.assertFalse(self.ctrl.history.can_undo)
        self.assertFalse(self.ctrl.history.can_redo)

    def test_undo_marks_dirty_and_broadcasts_all(self) -> None:
        self.ctrl.selected_palette_index = 1
        self.ctrl.on_paint(0, 0, stroke_start=True)
        self.ctrl.mark_dirty(False)
        self.view.calls.clear()
        self.ctrl.undo()
        self.assertTrue(self.ctrl.dirty)
        self.assertIn("sync:meta,palette,pixels,sprites", self.view.calls)

    def test_undo_stops_animation(self) -> None:
        self.ctrl.add_sprite()
        self.ctrl.toggle_animation()
        self.assertTrue(self.ctrl.animating)
        self.ctrl.undo()
        self.assertFalse(self.ctrl.animating)


if __name__ == "__main__":
    unittest.main()
