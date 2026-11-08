# Tixel - Sprite Editor for Amstrad CPC

Tixel is a lightweight desktop sprite editor for creating graphics for Amstrad CPC games. It is written in pure Python with Tkinter and requires no third-party runtime dependencies.

Projects are saved as JSON files with the `.tixel` extension and can contain a single sprite or a sequence of sprites for animation.

## Requirements

- Python 3.10 or later
- Tkinter (included with standard Python installations on Windows and macOS, on Linux install your distribution's `python3-tk` package)

## Usage

From the repository root:

```bash
python src/tixel.py
```

Alternatively:

```bash
cd src
python tixel.py
```

## Features

- Resolutions up to 48x48 pixels, fixed when a project is created
- Multiple sprites per project with an animation preview
- Code export as BASIC, BASIC (ABASC), C or ASM byte arrays

## Tools

- **Pencil** (default): drag to paint pixels with the selected palette color.
- **Fill**: click a pixel to flood-fill the region of the same color with the selected palette color.
- Right click applies the active tool with color 0 (erase).

## Keyboard shortcuts

| Action | Shortcut |
| --- | --- |
| New project | Ctrl+N |
| Open project | Ctrl+O |
| Save project | Ctrl+S |
| Copy sprite | Ctrl+C |
| Paste sprite | Ctrl+V |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Toggle grid | Ctrl+G |

## License

Tixel is free software; you may redistribute and/or modify it under the terms of the GNU General Public License version 3, as published by the Free Software Foundation.

This package is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License (included in the LICENSE file) for more details.
