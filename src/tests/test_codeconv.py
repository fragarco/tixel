"""
From the project source directory:

python3 -m unittest tests/test_codeconv.py
"""

import unittest
from codeconv import CodeConverter
from model import Project, Sprite
from constants import CPC_HW_COLORS


def project(mode: int, width: int, height: int, palette: list[int]) -> Project:
    return Project(width=width, height=height, video_mode=mode, palette=palette, name="T")


class TestFlattenPixels(unittest.TestCase):
    def test_row_major_order_square(self) -> None:
        conv = CodeConverter(project(2, 2, 2, [0, 1]))
        sprite = Sprite(2, 2, [[1, 0],[0, 1]])
        self.assertEqual(list(conv._flatten_pixels(sprite.pixels)), [1, 0, 0, 1])

    def test_non_square_wide(self) -> None:
        conv = CodeConverter(project(2, 3, 2, [0, 1]))
        sprite = Sprite(3, 2, [[1, 0, 1],[0, 1, 0]])
        self.assertEqual(list(conv._flatten_pixels(sprite.pixels)), [1, 0, 1, 0, 1, 0])

    def test_non_square_tall(self) -> None:
        conv = CodeConverter(project(2, 2, 4, [0, 1]))
        sprite = Sprite(2, 4, [[1, 0], [0, 1], [1, 1], [0, 0]])
        self.assertEqual(list(conv._flatten_pixels(sprite.pixels)), [1, 0, 0, 1, 1, 1, 0, 0])


class TestBuildVideoImg(unittest.TestCase):
    def test_mode2_msb_first(self) -> None:
        """
        Pixel video encode for a Mode 2 8x1 sprite.
        """
        conv = CodeConverter(project(2, 8, 1, [0, 1]))
        sprite = Sprite(8, 1, [[1, 0, 1, 0, 1, 0, 1, 0]])
        data = list(conv._build_videoimg(sprite.pixels))
        self.assertEqual(data, [0xAA])

    def test_mode1_two_bits_per_pixel(self) -> None:
        """
        Pixel video encode for a Mode 1 4x1 sprite
        """
        conv = CodeConverter(project(1, 4, 1, [0, 1, 2, 3]))
        sprite = Sprite(4, 1, [[3, 2, 1, 0]])
        data = list(conv._build_videoimg(sprite.pixels))
        self.assertEqual(data, [0xCA])

    def test_mode0_four_bits_per_pixel(self) -> None:
        """
        Pixel video encode for a couple of Mode 0 2x1 sprites
        """
        conv = CodeConverter(project(0, 2, 1, list(range(16))))
        sprite_left = Sprite(2, 1, [[1, 0]])
        sprite_right = Sprite(2, 1, [[0, 1]])
        sprite_both = Sprite(2, 1, [[1, 1]])
        self.assertEqual(list(conv._build_videoimg(sprite_left.pixels)),  [0x80])
        self.assertEqual(list(conv._build_videoimg(sprite_right.pixels)), [0x40])
        self.assertEqual(list(conv._build_videoimg(sprite_both.pixels)),  [0xC0])


class TestCEmission(unittest.TestCase):
    def test_palette_line(self) -> None:
        conv = CodeConverter(project(2, 8, 8, [1, 24]))
        code = "".join(conv.code_c_pal("hero"))
        hw = [CPC_HW_COLORS[1], CPC_HW_COLORS[24]]
        self.assertIn(f"const unsigned char PAL_HERO[2] = {{ 0x{hw[0]:02X}, 0x{hw[1]:02X} }};", code)

    def test_image_single_chunked_line(self) -> None:
        conv = CodeConverter(project(2, 16, 1, [0, 1]))
        sprite = Sprite(16, 1, [[1] * 8 + [0] * 8])
        code = "".join(conv.code_c_img(sprite, "hero00"))
        self.assertIn("// mode 2, 16x1 pixels", code)
        self.assertIn("const unsigned char SP_HERO00[2] = {", code)
        self.assertIn("    0xFF, 0x00\n};\n", code)

    def test_image_one_byte_per_line_when_row_is_one(self) -> None:
        conv = CodeConverter(project(2, 8, 2, [0, 1]))
        sprite = Sprite(8, 2, [[1] * 8, [0] * 8])
        code = "".join(conv.code_c_img(sprite, "hero00"))
        self.assertIn("    0xFF,\n    0x00\n};\n", code)


class TestAsmEmission(unittest.TestCase):
    def test_asm_image_uses_ampersand_hex(self) -> None:
        conv = CodeConverter(project(2, 8, 1, [0, 1]))
        sprite = Sprite(8, 1, [[1, 0, 1, 0, 1, 0, 1, 0]])
        code = "".join(conv.code_asm_img(sprite, "Hero"))
        self.assertIn("; mode 2, 8x1 pixels", code)
        self.assertIn("sp_hero:", code)
        self.assertIn("    db &AA\n", code)

    def test_abasc_image_wraps_db_in_asm(self) -> None:
        conv = CodeConverter(project(2, 8, 1, [0, 1]))
        sprite = Sprite(8, 1, [[1, 0, 1, 0, 1, 0, 1, 0]])
        code = "".join(conv.code_abasc_img(sprite, "Hero"))
        self.assertIn("LABEL SP.HERO:", code)
        self.assertIn('    ASM("db &AA")\n', code)


class TestBasEmission(unittest.TestCase):
    def test_basic_palette_ink_commands(self) -> None:
        conv = CodeConverter(project(2, 8, 8, [1, 24]))
        code = "".join(conv.code_bas_pal("hero"))
        self.assertIn("INK 0,1", code)
        self.assertIn("INK 1,24", code)

    def test_abasc_palette_label(self) -> None:
        conv = CodeConverter(project(2, 8, 8, [1, 24]))
        code = "".join(conv.code_abasc_pal("hero"))
        self.assertIn("LABEL PAL.HERO:", code)
        self.assertIn("INK 0,1", code)

    def test_basic_symbol_encoding_golden(self) -> None:
        # 8x8 mode 2 (one cursor block). Top 4 rows inked 1, bottom 4 rows 0.
        conv = CodeConverter(project(2, 8, 8, [0, 1]))
        sprite = Sprite(8, 8, [[1] * 8] * 4 + [[0] * 8] * 4)
        code = "".join(conv.code_bas_img(sprite, "hero00"))
        self.assertIn("SYMBOL AFTER 254\n", code)
        self.assertIn("SYMBOL 254,0,0,0,0,255,255,255,255\n", code)
        self.assertIn("SYMBOL 255,255,255,255,255,0,0,0,0\n", code)
        self.assertIn("LOCATE 10,10: PRINT CHR$(15)+CHR$(0)+CHR$(254)\n", code)
        self.assertIn("LOCATE 10,10: PRINT CHR$(15)+CHR$(1)+CHR$(255)\n", code)
        self.assertIn("PRINT CHR$(22)+CHR$(0)\n", code)

    def test_basic_image_returns_empty_when_no_symbols_left(self) -> None:
        # 48x48 mode 0 with 16 colors: 36 cursor blocks x 16 inks go past
        # the 256-symbol limit -> guarded early return with no code.
        conv = CodeConverter(project(0, 48, 48, list(range(16))))
        sprite = Sprite(48, 48)
        self.assertEqual(conv.code_bas_img(sprite, "big"), [])


if __name__ == "__main__":
    unittest.main()
