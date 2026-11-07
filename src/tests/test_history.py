"""
Unit tests for the History (undo/redo) stack.

From the project source directory:
python3 -m unittest tests/test_history.py
"""

import unittest
from constants import UNDO_LIMIT
from history import History, Snapshot


def snap(n: int) -> Snapshot:
    return {"project": {"marker": n}, "sprite": 0, "palette_sel": 0}


def unwrapped(snap_result: Snapshot | None) -> Snapshot:
    assert snap_result is not None
    return snap_result


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.hist = History(limit=3)

    def test_starts_empty(self) -> None:
        self.assertFalse(self.hist.can_undo)
        self.assertFalse(self.hist.can_redo)
        self.assertIsNone(self.hist.undo(snap(0)))
        self.assertIsNone(self.hist.redo(snap(0)))

    def test_record_undo_roundtrip(self) -> None:
        self.hist.record(snap(1))
        self.assertTrue(self.hist.can_undo)
        self.assertEqual(unwrapped(self.hist.undo(snap(2)))["project"]["marker"], 1)
        self.assertTrue(self.hist.can_redo)

    def test_redo_replays_undone_state(self) -> None:
        self.hist.record(snap(1))
        self.hist.undo(snap(2))
        self.assertEqual(unwrapped(self.hist.redo(snap(3)))["project"]["marker"], 2)
        self.assertTrue(self.hist.can_undo)

    def test_multiple_levels_lifo(self) -> None:
        self.hist.record(snap(1))
        self.hist.record(snap(2))
        self.assertEqual(unwrapped(self.hist.undo(snap(9)))["project"]["marker"], 2)
        self.assertEqual(unwrapped(self.hist.undo(snap(8)))["project"]["marker"], 1)
        self.assertIsNone(self.hist.undo(snap(7)))

    def test_record_clears_redo_stack(self) -> None:
        self.hist.record(snap(1))
        self.hist.undo(snap(2))
        self.assertTrue(self.hist.can_redo)
        self.hist.record(snap(3))
        self.assertFalse(self.hist.can_redo)

    def test_limit_evicts_oldest(self) -> None:
        for i in range(5):
            self.hist.record(snap(i))
        self.assertEqual(self.hist.limit, 3)
        self.assertEqual(unwrapped(self.hist.undo(snap(0)))["project"]["marker"], 4)
        self.assertEqual(unwrapped(self.hist.undo(snap(0)))["project"]["marker"], 3)
        self.assertEqual(unwrapped(self.hist.undo(snap(0)))["project"]["marker"], 2)
        self.assertIsNone(self.hist.undo(snap(0)))

    def test_reset_forgets_everything(self) -> None:
        self.hist.record(snap(1))
        self.hist.undo(snap(2))
        self.hist.reset()
        self.assertFalse(self.hist.can_undo)
        self.assertFalse(self.hist.can_redo)

    def test_default_limit_from_constants(self) -> None:
        self.assertEqual(History().limit, max(1, UNDO_LIMIT))

    def test_minimum_limit_is_one(self) -> None:
        self.assertEqual(History(limit=0).limit, 1)


if __name__ == "__main__":
    unittest.main()
