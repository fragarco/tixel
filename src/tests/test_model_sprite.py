"""
From project source directory:

python3 -m unittest test/test_model_sprite.py
"""

import unittest
from model import Sprite

class TestSprite(unittest.TestCase):
    def test_init_default(self) -> None:
        s = Sprite(4, 4)
        self.assertEqual(s.width, 4)
        self.assertEqual(s.height, 4)
        self.assertEqual(s.pixels, [[0] * 4 for _ in range(4)])

    def test_init_with_pixels(self) -> None:
        pixels = [[0, 1], [1, 0]]
        s = Sprite(2, 2, pixels)
        self.assertEqual(s.pixels, pixels)
        pixels[0][0] = 99
        self.assertNotEqual(s.pixels[0][0], 99)

    def test_clone_independence(self) -> None:
        s = Sprite(2, 2)
        s.set(1, 1, 1)
        c = s.clone()
        self.assertEqual(c.get(1, 1), 1)
        c.set(1, 1, 0)
        self.assertEqual(s.get(1, 1), 1)
        self.assertEqual(c.get(1, 1), 0)

    def test_clear(self) -> None:
        s = Sprite(3, 3)
        s.set(0, 0, 1)
        s.set(1, 1, 1)
        s.clear()
        for y in range(3):
            for x in range(3):
                self.assertEqual(s.get(x, y), 0)

    def test_get_set(self) -> None:
        s = Sprite(2, 2)
        s.set(0, 1, 2)
        self.assertEqual(s.get(0, 1), 2)
        s.set(1, 0, 3)
        self.assertEqual(s.get(1, 0), 3)

    def test_remap(self) -> None:
        s = Sprite(2, 2, [[0, 1], [1, 0]])
        s.remap({0: 1, 1: 0})
        self.assertEqual(s.pixels, [[1, 0], [0, 1]])
        s = Sprite(2, 2, [[0, 1], [2, 0]])
        s.remap({1: 2})
        self.assertEqual(s.get(0, 0), 0)
        self.assertEqual(s.get(1, 0), 2)

    def test_flood_fill_connected_component(self) -> None:
        s = Sprite(3, 3, [[0, 0, 1], [0, 1, 0], [1, 0, 0]])
        changed = s.flood_fill(0, 0, 2)
        self.assertEqual(changed, 3)
        self.assertEqual(s.pixels, [[2, 2, 1], [2, 1, 0], [1, 0, 0]])

    def test_flood_fill_is_four_connected(self) -> None:
        s = Sprite(2, 2, [[0, 1], [1, 0]])
        changed = s.flood_fill(0, 0, 2)
        self.assertEqual(changed, 1)
        self.assertEqual(s.get(1, 1), 0)

    def test_flood_fill_same_color_is_noop(self) -> None:
        s = Sprite(2, 2)
        self.assertEqual(s.flood_fill(0, 0, 0), 0)
        self.assertEqual(s.pixels, [[0, 0], [0, 0]])

    def test_flood_fill_out_of_bounds_is_noop(self) -> None:
        s = Sprite(2, 2)
        self.assertEqual(s.flood_fill(-1, 0, 1), 0)
        self.assertEqual(s.flood_fill(2, 2, 1), 0)
        self.assertEqual(s.pixels, [[0, 0], [0, 0]])

    def test_flip_horizontal(self) -> None:
        s = Sprite(3, 2, [[0, 1, 2], [3, 4, 5]])
        s.flip_horizontal()
        self.assertEqual(s.pixels, [[2, 1, 0], [5, 4, 3]])

    def test_flip_vertical(self) -> None:
        s = Sprite(3, 2, [[0, 1, 2], [3, 4, 5]])
        s.flip_vertical()
        self.assertEqual(s.pixels, [[3, 4, 5], [0, 1, 2]])

    def test_double_flip_restores_original(self) -> None:
        pixels = [[0, 1, 2], [3, 4, 5]]
        s = Sprite(3, 2, pixels)
        s.flip_horizontal()
        s.flip_horizontal()
        self.assertEqual(s.pixels, pixels)
        s.flip_vertical()
        s.flip_vertical()
        self.assertEqual(s.pixels, pixels)

    def test_to_dict(self) -> None:
        s = Sprite(2, 2, [[0, 1], [1, 0]])
        d = s.to_dict()
        self.assertEqual(d, {"width": 2, "height": 2, "pixels": [[0, 1], [1, 0]]})

    def test_from_dict_valid(self) -> None:
        s = Sprite.from_dict({"width": 2, "height": 2, "pixels": [[0, 1], [1, 0]]}, 2, 2, 2)
        self.assertEqual(s.get(1, 0), 1)

    def test_from_dict_invalid_not_dict(self) -> None:
        with self.assertRaises(ValueError):
            Sprite.from_dict("no dict", 2, 2, 2)  # type: ignore[arg-type]

    def test_from_dict_dimension_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            Sprite.from_dict({"width": 3, "height": 2, "pixels": [[0, 0], [0, 0]]}, 2, 2, 2)

    def test_from_dict_wrong_rows(self) -> None:
        with self.assertRaises(ValueError):
            Sprite.from_dict({"width": 2, "height": 2, "pixels": [[0, 0]]}, 2, 2, 2)

    def test_from_dict_wrong_cols(self) -> None:
        with self.assertRaises(ValueError):
            Sprite.from_dict({"width": 2, "height": 2, "pixels": [[0, 0], [0]]}, 2, 2, 2)

    def test_from_dict_pixel_outside_palette(self) -> None:
        with self.assertRaises(ValueError):
            Sprite.from_dict({"width": 2, "height": 2, "pixels": [[0, 5], [0, 0]]}, 2, 2, 2)

    def test_from_dict_pixel_not_int(self) -> None:
        with self.assertRaises((ValueError, TypeError)):
            Sprite.from_dict({"width": 2, "height": 2, "pixels": [[0, "a"], [0, 0]]}, 2, 2, 2)


if __name__ == "__main__":
    unittest.main()
