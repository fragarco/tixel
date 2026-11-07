"""
From project source directory:

python3 -m unittest test/test_model_project.py
"""
import unittest
from constants import DEFAULT_SIZE, MAX_SIZE
from model import Project, Sprite

class TestProject(unittest.TestCase):
    def test_init_defaults(self) -> None:
        p = Project()
        self.assertEqual(p.width, DEFAULT_SIZE)
        self.assertEqual(p.height, DEFAULT_SIZE)
        self.assertEqual(p.video_mode, 0)
        self.assertEqual(len(p.palette), 2)
        self.assertEqual(len(p.sprites), 1)
        self.assertEqual(p.name, "Untitled")

    def test_init_custom(self) -> None:
        p = Project(width=8, height=8, video_mode=1, palette=[0, 1], name="Test")
        self.assertEqual(p.width, 8)
        self.assertEqual(p.palette, [0, 1])

    def test_max_colors_property(self) -> None:
        self.assertEqual(Project(video_mode=0).max_colors, 16)
        self.assertEqual(Project(video_mode=1).max_colors, 4)
        self.assertEqual(Project(video_mode=2).max_colors, 2)

    def test_to_dict(self) -> None:
        p = Project(width=4, height=4, video_mode=0, palette=[0, 1], name="MyProj")
        d = p.to_dict()
        self.assertEqual(d["width"], 4)
        self.assertEqual(d["height"], 4)
        self.assertEqual(d["video_mode"], 0)
        self.assertEqual(d["palette"], [0, 1])
        self.assertEqual(d["name"], "MyProj")
        self.assertEqual(len(d["sprites"]), 1)

    def test_from_dict_valid(self) -> None:
        p = Project(width=4, height=4, video_mode=1, palette=[0, 1], name="X")
        p.sprites[0].set(0, 0, 1)
        data = p.to_dict()
        p2 = Project.from_dict(data)
        self.assertEqual(p2.width, 4)
        self.assertEqual(p2.sprites[0].get(0, 0), 1)
        self.assertEqual(p2.name, "X")

    def test_from_dict_invalid_width(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 0,
                "height": 4,
                "video_mode": 0,
                "palette": [0],
                "sprites": [{"width": 0, "height": 4, "pixels": []}]
            })

    def test_from_dict_invalid_height(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 99,
                "video_mode": 0,
                "palette": [0],
                "sprites": [{"width": 4, "height": 99, "pixels": []}]
            })

    def test_from_dict_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 99,
                "palette": [0],
                "sprites": [{"width": 4, "height": 4, "pixels": [[0]*4]*4}]
            })

    def test_from_dict_palette_missing(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 0,
                "palette": [],
                "sprites": [{"width": 4, "height": 4, "pixels": [[0]*4]*4}]
            })

    def test_from_dict_palette_too_large(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 1,
                "palette": [0, 1, 2, 3, 4],
                "sprites": [{"width": 4, "height": 4, "pixels": [[0]*4]*4}]
            })

    def test_from_dict_palette_invalid_color(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 0,
                "palette": [99],
                "sprites": [{"width": 4, "height": 4, "pixels": [[0]*4]*4}]
            })

    def test_from_dict_no_sprites(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 0,
                "palette": [0],
                "sprites": []
            })

    def test_from_dict_sprite_dimension_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict({
                "width": 4,
                "height": 4,
                "video_mode": 0,
                "palette": [0, 1],
                "sprites": [{"width": 2, "height": 2, "pixels": [[0]*2]*2}]
            })

    def test_from_dict_not_dict(self) -> None:
        with self.assertRaises(ValueError):
            Project.from_dict("not a dict")  # type: ignore[arg-type]

    def test_from_dict_max_size_boundary(self) -> None:
        p = Project.from_dict({
            "width": MAX_SIZE,
            "height": MAX_SIZE,
            "video_mode": 0,
            "palette": [0],
            "sprites": [{
                "width": MAX_SIZE,
                "height": MAX_SIZE,
                "pixels": [[0]*MAX_SIZE]*MAX_SIZE
            }]
        })
        self.assertEqual(p.width, MAX_SIZE)

    def test_roundtrip_preserves_all_sprites(self) -> None:
        p = Project(width=3, height=3, video_mode=0, palette=[0, 5, 10])
        p.sprites.append(Sprite(3, 3))
        p.sprites[1].set(1, 1, 2)
        data = p.to_dict()
        p2 = Project.from_dict(data)
        self.assertEqual(len(p2.sprites), 2)
        self.assertEqual(p2.sprites[1].get(1, 1), 2)


if __name__ == "__main__":
    unittest.main()
