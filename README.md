# Tixel - Sprite Editor for Amstrad CPC

## Español:

Tixel es un editor ligero de sprites para crear gráficos para los ordenadores Amstrad CPC. Está escrito en Python puro con Tkinter y no requiere librerías de terceros.

Los proyectos se guardan como archivos JSON con la extensión `.tixel` y pueden contener un único sprite o una secuencia de sprites.

### Requisitos

- Python 3.10 o posterior
- Tkinter (incluido en las instalaciones estándar de Python en Windows y macOS, en Linux instala el paquete `python3-tk` de tu distribución).

### Uso

Desde la raíz del repositorio:

```bash
python src/tixel.py
```

Alternativamente:

```bash
cd src
python tixel.py
```

### Funciones

- Sprites de hasta 48x48 píxeles
- Varios sprites por proyecto con vista previa de animación
- Exportación de los sprites como código para BASIC, BASIC (ABASC), C o ASM

### Herramientas

- **Lápiz** (predeterminada): pinta píxeles con el color de paleta seleccionado.
- **Relleno**: haz clic en un píxel para rellenar la región del mismo color con el color de paleta seleccionado.
- Un clic derecho aplica la herramienta seleccionada, pero con el color 0 (efecto de "borrar").

### Atajos de teclado

| Acción | Atajo |
| --- | --- |
| Nuevo proyecto | Ctrl+N |
| Abrir proyecto | Ctrl+O |
| Guardar proyecto | Ctrl+S |
| Copiar sprite | Ctrl+C |
| Pegar sprite | Ctrl+V |
| Deshacer | Ctrl+Z |
| Rehacer | Ctrl+Y |
| Mostrar/ocultar cuadrícula | Ctrl+G |
| Dibujar línea desde el último píxel (Lápiz) | Shift+clic izquierdo |

### Licencia

Tixel es software libre; puedes redistribuirlo y/o modificarlo bajo los términos de la GNU General Public License versión 3, publicada por la Free Software Foundation.

Este software se distribuye con la esperanza de que sea útil, pero **SIN NINGUNA GARANTÍA**; ni siquiera la garantía implícita de COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la GNU General Public License (incluida en el archivo LICENSE) para obtener más detalles.

## English:

Tixel is a lightweight desktop sprite editor for creating graphics for Amstrad CPC games. It is written in pure Python with Tkinter and requires no third-party libraries.

Projects are saved as JSON files with the `.tixel` extension and can contain a single sprite or a sequence of sprites for animation.

### Requirements

- Python 3.10 or later
- Tkinter (included with standard Python installations on Windows and macOS, on Linux install your distribution's `python3-tk` package)

### Usage

From the repository root:

```bash
python src/tixel.py
```

Alternatively:

```bash
cd src
python tixel.py
```

### Features

- Sprites up to 48x48 pixels
- Multiple sprites per project with an animation preview
- Code export as BASIC, BASIC (ABASC), C or ASM byte arrays

### Tools

- **Pencil** (default): drag to paint pixels with the selected palette color.
- **Fill**: click a pixel to flood-fill the region of the same color with the selected palette color.
- Right click applies the active tool with color 0 (erase).

### Keyboard shortcuts

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
| Draw line from last pixel (Pencil) | Shift+left click |

### License

Tixel is free software; you may redistribute and/or modify it under the terms of the GNU General Public License version 3, as published by the Free Software Foundation.

This package is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License (included in the LICENSE file) for more details.
