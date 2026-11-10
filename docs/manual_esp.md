# Tixel - Manual de Usuario

## Introducción

**Tixel** es un editor de sprites de escritorio para crear gráficos destinados a juegos para los **Amstrad CPC**. Está escrito en Python puro con Tkinter y no requiere de otras librerías externas.

Un proyecto de Tixel puede contener un único sprite o una secuencia de sprites. Una vez terminado el diseño, Tixel puede generar el ódigo
necesario para usar los sprites desde **C** (por ejemplo con cpctelera), **ensamblador**, **BASIC** puro y **BASIC** para el compilador ABASC.

---

## Requisitos

Para ejecutar Tixel necesitas:

1. **Python 3.10 o posterior**.
2. Soporte para `tkinter`, la librería de interfaz gráfica incluida en las instalaciones estándar de Python en Windows y macOS. En Linux suele ser necesario instalar el paquete `python3-tk`.

---

## Instalación y ejecución

1. Descarga o clona el repositorio de Tixel.
2. Comprueba que Python está instalado correctamente:

   ```bash
   python --version
   ```

3. Ejecuta la aplicación desde la raíz del repositorio:

   ```bash
   python src/tixel.py
   ```

## Creación de un ejecutable (opcional)

Tixel no incluye un sistema de compilación propio. Si quieres utilizar la aplicación como un ejecutable, puedes usar **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller -F -w src/tixel.py -n Tixel
```

El ejecutable se generará dentro de la carpeta `dist` (por ejemplo, `dist/Tixel.exe` en Windows).

---

## Interfaz de usuario

La ventana principal está formada por estas áreas:

- **Barra de menús**: File, Edit, Tools, Transform, View, Code y Help.
- **Barra de herramientas**: muestra la información sobre el modo de vídeo, resolución, número de colores y la herramienta de pintado seleccionada.
- **Lienzo de edición**: la cuadrícula donde se muestra el sprite actual.
- **Panel izquierdo**: lista de sprites, botones de gestión, vista previa y control de animación.
- **Paleta**: franja inferior con los colores seleccionados para el proyecto.
- **Barra de estado**: información del píxel bajo el cursor, mensajes de la aplicación y nombre de la herramienta al pasar por los iconos.

El título de la ventana muestra el nombre del proyecto y un asterisco (`*`) cuando hay cambios sin guardar.

### Barra de menús

#### File

- **New Project...** (`Ctrl+N`): crea un proyecto nuevo. El diálogo permite elegir el modo de vídeo y la resolución. Estos parámetros no se pueden cambiar una vez se crea el proyecto.
- **Open Project...** (`Ctrl+O`): carga un archivo `.tixel`.
- **Save** (`Ctrl+S`): guarda el proyecto actual.
- **Save As...**: guarda el proyecto con otro nombre o en otra ubicación.
- **Exit**: cierra la aplicación.

Si hay cambios sin guardar, al crear o abrir otro proyecto (y al salir) Tixel pregunta si deseas guardar, descartar los cambios o cancelar la operación.

#### Edit

- **Undo** (`Ctrl+Z`) y **Redo** (`Ctrl+Y`): deshacer y rehacer.
- **Copy Sprite** (`Ctrl+C`) y **Paste Sprite** (`Ctrl+V`): copian y pegan el sprite actual. El pegado solo es posible si el sprite copiado tiene las mismas dimensiones que el destino.
- **Add Sprite**: inserta un sprite vacío después del actual.
- **Delete Sprite**: elimina el sprite actual (siempre debe quedar al menos uno) tras pedir confirmación.
- **Clear Sprite**: borra todo el contenido del sprite actual.

Los sprites se pueden reordenar con los botones **Up** y **Down** del panel izquierdo, o duplicar con **Duplicate**.

#### Tools

- **Pencil**: herramienta de dibujo píxel a píxel (predeterminada).
- **Fill**: herramienta de relleno de un área.
- **Circle**: herramienta de dibujo de circunferencias.

Con **Pencil** seleccionada, **Shift + clic izquierdo** dibuja una línea
recta desde el último píxel pintado con el color de paleta seleccionado hasta
el píxel pulsado. Si encadenas varios clics con Shift dibujarás polilíneas.
Si no hay un píxel anterior, o este se pintó con otro color, el clic pinta
simplemente el píxel pulsado como de costumbre.

La herramienta **Circle** dibuja una circunferencia con dos clics: el primero
fija el centro y el segundo fija el radio (la distancia al píxel pulsado).
Usa el botón izquierdo en el segundo clic para pintar la circunferencia con el
color de paleta seleccionado, o el botón derecho para pintarla con el color
**0**. Cambiar de herramienta o de sprite, o deshacer/rehacer, descarta un
centro pendiente: vuelve a hacer clic para fijar uno nuevo.

Las mismas herramientas están disponibles como botones de icono en la barra de herramientas. La herramienta seleccionada aparece resaltada.

#### Transform

- **Flip Horizontally**: refleja el sprite actual de izquierda a derecha.
- **Flip Vertically**: refleja el sprite actual de arriba abajo.

Cada transformación afecta solo al sprite actual y se puede deshacer con Ctrl+Z (Undo).

#### View

- **Grid** (`Ctrl+G`): muestra u oculta la cuadrícula del lienzo.

#### Code

- **BASIC**: genera BASIC puro.
- **BASIC (ABASC)**: genera BASIC compatible con el compilador ABASC y su librería BASE.
- **C**: código en C, por ejemplo, utilizable con la librería cpctelera y el compilador SDCC.
- **ASM**: código en ensamblador con sintáxis MAXAM (utilizable con ABASM o WinApe).

El resultado se muestra en una ventana de texto desde la que se puede copiar.

#### Help

- **Quick Help**: resumen rápido del funcionamiento de la aplicación.
- **About Tixel**: información sobre la versión y el propósito de Tixel.

### Area edición de Sprites

La ventana principal muestra el sprite actual con una cuadrícula opcional. La resolución máxima es de **48x48 píxeles** y se elige al crear el proyecto; no se puede cambiar después. El tamaño de las celdas se ajusta automáticamente para que el sprite quepa en la ventana.

Para dibujar:

- **Botón izquierdo**: aplica la herramienta activa con el color de paleta seleccionado.
- **Botón derecho**: aplica la herramienta activa con el color **0**.
- **Shift + botón izquierdo** (Pencil): dibuja una línea desde el último píxel pintado con el color seleccionado; ver [Tools](#tools).
- **Doble clic** (Circle): el primer clic fija el centro y el segundo fija el radio y pinta la circunferencia; ver [Tools](#tools).

Mientras se reproduce la animación, el lienzo no acepta cambios.

### Lista de sprites y vista previa

El panel izquierdo contiene la lista de sprites que forman la animación:

- **Add**: añade un sprite vacío después del actual.
- **Duplicate**: duplica el sprite actual y lo añade justo a continuación.
- **Delete**: elimina el sprite actual (siempre debe haber uno como mínimo).
- **Up / Down**: cambian el orden del sprite en la lista.

Todos los sprites del proyecto comparten la misma resolución y la misma paleta. La vista previa muestra el sprite actual o, durante la animación, el fotograma correspondiente. El botón **Play/Stop** inicia o detiene la animación; para reproducirla se necesitan al menos dos sprites.

### Paleta de colores

La paleta del proyecto se muestra en la parte inferior con un número por color. Haz clic en una entrada para seleccionarla. El color seleccionado se usa con el botón izquierdo del ratón.

- **Add Color...**: añade un color de la paleta de 27 colores del Amstrad CPC. El botón se desactiva al alcanzar el máximo del modo de vídeo.
- **Change Color...**: cambia el color actual por otro. También se puede hacer doble clic sobre la entrada de la paleta. Todos los píxeles que usan ese índice cambian al nuevo color.
- **Remove Color**: elimina el color seleccionado tras confirmarlo. Los píxeles que lo usaban pasan al color 0 y los índices superiores se desplazan una posición. La paleta debe conservar al menos un color.

El máximo de colores depende del modo de vídeo y Tixel lo aplica mientras se edita:

| Modo | Colores máximos |
| --- | --- |
| Mode 0 | 16 |
| Mode 1 | 4 |
| Mode 2 | 2 |

La paleta inicial contiene dos colores. El color de índice 0 actúa como color de fondo. Solo se pueden elegir colores de la paleta oficial del Amstrad CPC.

### Barra de estado

Muestra información contextual:

- Coordenadas del píxel, índice de paleta y nombre del color al mover el ratón sobre el lienzo.
- Nombre de la herramienta al pasar sobre los iconos de la barra.
- Mensajes como el proyecto cargado o guardado, o si no hay nada que deshacer o rehacer.

---

## Transformaciones

El menú **Transform** refleja (modo espejo) el sprite actual:

- **Flip Horizontally**: intercambia las columnas de izquierda a derecha.
- **Flip Vertically**: intercambia las filas de arriba abajo.

Las transformaciones se pueden deshacer y no afectan a los demás sprites del proyecto.

---

## Creación de un sprite paso a paso

1. **Crea el proyecto**:
   - `File > New Project...`.
   - Elige el modo de vídeo (0, 1 o 2) y la resolución (de 1x1 a 48x48).
   - Pulsa **Create**. El modo y la resolución ya no se podrán cambiar.

2. **Prepara la paleta**:
   - La paleta empieza con dos colores; añade más con **Add Color...** hasta el máximo permitido por el modo.
   - Selecciona el color con el que quieres dibujar.

3. **Dibuja**:
   - Elige **Pencil** o **Fill** en el menú Tools o en la barra de herramientas.
   - Usa el botón izquierdo con el color seleccionado y el derecho para pintar con el color 0.
   - Usa `Ctrl+Z`/`Ctrl+Y` para corregir.

4. **Crea la animación** (opcional):
   - Añade o duplica sprites con los botones del panel derecho.
   - Reordénalos con **Up/Down** y pulsa **Play** para ver la animación.

5. **Guarda el proyecto**:
   - `File > Save` o `File > Save As...`. El archivo tendrá extensión `.tixel`.

6. **Exporta el código**:
   - Abre el menú **Code** y elige BASIC, BASIC (ABASC), C o ASM.

---

## Exportación de código

El menú **Code** genera el código de la paleta y de cada sprite del proyecto, teniendo en cuenta el modo de vídeo y la disposición de la memoria de vídeo del Amstrad CPC. Los formatos disponibles son:

- **BASIC**: paleta con instrucciones `INK`, definiciones `SYMBOL` y un ejemplo de impresión del sprite.
- **BASIC (ABASC)**: paleta y datos de imagen para el compilador ABASC. Añade código de ejemplo para pintar el primer sprite.
- **C**: arrays `const unsigned char` para la paleta y para cada sprite.
- **ASM**: etiquetas y directivas `db` para la paleta y para cada sprite.

Ejemplo del código generado en C:

```c
// Palette of 2 colors
const unsigned char PAL_MISPRITE[2] = { 0x04, 0x03 };

// mode 0, 8x4 pixels
const unsigned char SP_MISPRITE00[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};
```

Ejemplo del código generado en ensamblador:

```asm
; Palette of 2 colors
pal_misprite:
    db 0x04, 0x03

; mode 0, 8x4 pixels
sp_misprite00:
    db &00, &00, &00, &00, &00, &00, &00, &00
    db &00, &00, &00, &00, &00, &00, &00, &00
```

Los nombres y el número de bytes dependen del nombre del proyecto, de su resolución y del modo de vídeo.

---

## Licencia

Tixel ha sido desarrollado por Javier "Dwayne Hicks" García. Esta aplicación se distribuye bajo la licencia **GNU GENERAL PUBLIC LICENSE versión 3**. Eres libre de usar, modificar y distribuir el programa como desees mientras respetes los términos de la licencia.

Puedes encontrar el texto de la licencia en el fichero **LICENSE**.
