# Tixel - User Manual

## Introduction

**Tixel** is a desktop sprite editor for creating graphics for **Amstrad CPC** games. It is written in pure Python with Tkinter and requires no other external libraries.

A Tixel project can contain a single sprite or a sequence of sprites. Once the design is finished, Tixel can generate the code needed to use the sprites from **C** (for example with cpctelera), **assembly**, pure **BASIC**, and **BASIC** for the ABASC compiler.

---

## Requirements

To run Tixel you need:

1. **Python 3.10 or later**.
2. Support for `tkinter`, the graphical interface library included in standard Python installations on Windows and macOS. On Linux, you usually need to install the `python3-tk` package.

---

## Installation and execution

1. Download or clone the Tixel repository.
2. Check that Python is installed correctly:

   ```bash
   python --version
   ```

3. Run the application from the repository root:

   ```bash
   python src/tixel.py
   ```

## Creating an executable (optional)

Tixel does not include its own build system. If you want to use the application as an executable, you can use **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller -F -w src/tixel.py -n Tixel
```

The executable will be generated inside the `dist` folder (for example, `dist/Tixel.exe` on Windows).

---

## User interface

The main window consists of these areas:

- **Menu bar**: File, Edit, Tools, Transform, View, Code and Help.
- **Toolbar**: shows information about the video mode, resolution, number of colors and the selected drawing tool.
- **Editing canvas**: the grid where the current sprite is displayed.
- **Left panel**: sprite list, management buttons, preview and animation control.
- **Palette**: bottom strip with the colors selected for the project.
- **Status bar**: information about the pixel under the cursor, application messages and the name of the tool when hovering over the icons.

The window title shows the project name and an asterisk (`*`) when there are unsaved changes.

### Menu bar

#### File

- **New Project...** (`Ctrl+N`): creates a new project. The dialog lets you choose the video mode and resolution. These parameters cannot be changed once the project is created.
- **Open Project...** (`Ctrl+O`): loads a `.tixel` file.
- **Save** (`Ctrl+S`): saves the current project.
- **Save As...**: saves the project under another name or in another location.
- **Exit**: closes the application.

If there are unsaved changes, when creating or opening another project (and when exiting) Tixel asks whether you want to save, discard the changes or cancel the operation.

#### Edit

- **Undo** (`Ctrl+Z`) and **Redo** (`Ctrl+Y`): undo and redo.
- **Copy Sprite** (`Ctrl+C`) and **Paste Sprite** (`Ctrl+V`): copy and paste the current sprite. Pasting is only possible if the copied sprite has the same dimensions as the target.
- **Add Sprite**: inserts an empty sprite after the current one.
- **Delete Sprite**: deletes the current sprite (at least one must always remain) after asking for confirmation.
- **Clear Sprite**: clears all the content of the current sprite.

Sprites can be reordered with the **Up** and **Down** buttons in the left panel, or duplicated with **Duplicate**.

#### Tools

- **Pencil**: pixel-by-pixel drawing tool (default).
- **Fill**: area fill tool.
- **Circle**: circle drawing tool.

With the Pencil selected, **Shift + left click** draws a straight line from the
last pixel painted with the currently selected palette color to the clicked
pixel. Consecutive Shift+clicks chain the segments, letting you draw polylines.
If there is no previous pixel, or it was painted with a different color, the
click simply paints the clicked pixel as usual.

The **Circle** tool draws a ring with two clicks: the first click sets the
center and the second one sets the radius (the distance to the clicked pixel).
Use the left button on the second click to paint the ring with the selected
palette color, or the right button to paint it with color **0**. Switching
tool or sprite, or undoing/redoing, discards a pending center: click again to
set a new one.

The same tools are available as icon buttons in the toolbar. The selected tool appears highlighted.

#### Transform

- **Flip Horizontally**: mirrors the current sprite from left to right.
- **Flip Vertically**: mirrors the current sprite from top to bottom.

Each transformation affects only the current sprite and can be undone with Ctrl+Z (Undo).

#### View

- **Grid** (`Ctrl+G`): shows or hides the canvas grid.

#### Code

- **BASIC**: generates pure BASIC.
- **BASIC (ABASC)**: generates BASIC compatible with the ABASC compiler and its BASE library.
- **C**: C code, for example usable with the cpctelera library and the SDCC compiler.
- **ASM**: assembly code with MAXAM syntax (usable with ABASM or WinApe).

The result is shown in a text window from which it can be copied.

#### Help

- **Quick Help**: quick summary of how the application works.
- **About Tixel**: information about the version and purpose of Tixel.

### Sprite editing area

The main window shows the current sprite with an optional grid. The maximum resolution is **48x48 pixels** and is chosen when creating the project; it cannot be changed afterwards. The cell size is adjusted automatically so that the sprite fits in the window.

To draw:

- **Left button**: applies the active tool with the selected palette color.
- **Right button**: applies the active tool with color **0**.
- **Shift + left button** (Pencil): draws a line from the last pixel painted with the selected color; see [Tools](#tools).
- **Two clicks** (Circle): first click sets the center, second click sets the radius and paints the ring; see [Tools](#tools).

While the animation is playing, the canvas does not accept changes.

### Sprite list and preview

The left panel contains the list of sprites that make up the animation:

- **Add**: adds an empty sprite after the current one.
- **Duplicate**: duplicates the current sprite and adds it immediately after it.
- **Delete**: deletes the current sprite (there must always be at least one).
- **Up / Down**: change the order of the sprite in the list.

All sprites in the project share the same resolution and the same palette. The preview shows the current sprite or, during animation, the corresponding frame. The **Play/Stop** button starts or stops the animation; at least two sprites are required to play it.

### Color palette

The project palette is shown at the bottom with a number for each color. Click an entry to select it. The selected color is used with the left mouse button.

- **Add Color...**: adds a color from the 27-color Amstrad CPC palette. The button is disabled when the maximum for the video mode is reached.
- **Change Color...**: changes the current color for another one. You can also double-click the palette entry. All pixels that use that index change to the new color.
- **Remove Color**: removes the selected color after confirmation. Pixels that used it change to color 0 and the higher indexes shift down by one position. The palette must keep at least one color.

The maximum number of colors depends on the video mode and Tixel enforces it while editing:

| Mode | Maximum colors |
| --- | --- |
| Mode 0 | 16 |
| Mode 1 | 4 |
| Mode 2 | 2 |

The initial palette contains two colors. The color at index 0 acts as the background color. Only colors from the official Amstrad CPC palette can be selected.

### Status bar

It shows contextual information:

- Pixel coordinates, palette index and color name when moving the mouse over the canvas.
- The name of the tool when hovering over the toolbar icons.
- Messages such as the project loaded or saved, or if there is nothing to undo or redo.

---

## Transformations

The **Transform** menu mirrors the current sprite:

- **Flip Horizontally**: swaps the columns from left to right.
- **Flip Vertically**: swaps the rows from top to bottom.

Transformations can be undone and do not affect the other sprites in the project.

---

## Creating a sprite step by step

1. **Create the project**:
   - `File > New Project...`.
   - Choose the video mode (0, 1 or 2) and the resolution (from 1x1 to 48x48).
   - Click **Create**. The mode and resolution can no longer be changed.

2. **Prepare the palette**:
   - The palette starts with two colors; add more with **Add Color...** up to the maximum allowed by the mode.
   - Select the color you want to draw with.

3. **Draw**:
   - Choose **Pencil** or **Fill** from the Tools menu or the toolbar.
   - Use the left button with the selected color and the right button to paint with color 0.
   - Use `Ctrl+Z`/`Ctrl+Y` to correct mistakes.

4. **Create the animation** (optional):
   - Add or duplicate sprites with the buttons in the right panel.
   - Reorder them with **Up/Down** and press **Play** to view the animation.

5. **Save the project**:
   - `File > Save` or `File > Save As...`. The file will have the `.tixel` extension.

6. **Export the code**:
   - Open the **Code** menu and choose BASIC, BASIC (ABASC), C or ASM.

---

## Code export

The **Code** menu generates the code for the palette and for each sprite in the project, taking into account the video mode and the Amstrad CPC video memory layout. The available formats are:

- **BASIC**: palette with `INK` instructions, `SYMBOL` definitions and a sprite printing example.
- **BASIC (ABASC)**: palette and image data for the ABASC compiler. Includes example code to draw the first sprite.
- **C**: `const unsigned char` arrays for the palette and for each sprite.
- **ASM**: labels and `db` directives for the palette and for each sprite.

Example of the generated C code:

```c
// Palette of 2 colors
const unsigned char PAL_MISPRITE[2] = { 0x04, 0x03 };

// mode 0, 8x4 pixels
const unsigned char SP_MISPRITE00[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};
```

Example of the generated assembly code:

```asm
; Palette of 2 colors
pal_misprite:
    db 0x04, 0x03

; mode 0, 8x4 pixels
sp_misprite00:
    db &00, &00, &00, &00, &00, &00, &00, &00
    db &00, &00, &00, &00, &00, &00, &00, &00
```

The names and number of bytes depend on the project name, its resolution and the video mode.

---

## License

Tixel was developed by Javier "Dwayne Hicks" García. This application is distributed under the **GNU GENERAL PUBLIC LICENSE version 3**. You are free to use, modify and distribute the program as you wish as long as you respect the terms of the license.

You can find the license text in the **LICENSE** file.
