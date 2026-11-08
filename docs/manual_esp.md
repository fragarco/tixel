# Tixel - Manual de Usuario

## Introducción

**Tixel** es una sencilla aplicación escrita en Python para el diseño de sprites de hasta 48x48 píxeles para ordenadores **Amstrad CPC**. Su objetivo es no depender de librerías externas, de forma que se pueda utilizar en cualquier plataforma con un soporte estándar de Python 3.

Una vez completado el diseño de nuestros sprites, Tixel ofrece la posibilidad de mostrar el código necesario para usarlo en varios lenguajes: **C** (especialmente para su uso con la librería cpctelera), **ensamblador**, **BASIC** puro y **BASIC** para el compilador ABASC.

---

## Requisitos

Para ejecutar Tixel necesitas:

1. **Python 3.8+** instalado en tu sistema.
2. Soporte para la librería de interfaz de usuario `tkinter` (que viene incluida en la mayoría de distribuciones de Python).

---

## Instalación y ejecución

1. Descarga o clona el código de Tixel desde el repositorio correspondiente.
   ```bash
   git clone https://github.com/fragarco/tixel
   ```

2. Asegúrte de tener Python instalado correctamente:
   ```bash
   python --version
   ```

3. Ejecuta Tixel con el siguiente comando:
   ```bash
   python src/tixel.py
   ```

## Creación de un ejecutable

La idea detrás de Tixel es propociar una herramienta que pueda funcionar en cualquier entorno con soporte para Python 3. Por ello, no se hace uso de modulos externos más allá de Tcl/Tk, la biblioteca de interfaz de usuario por defecto. Por esa misma razón, no se suministra un sistema de "build" para generar ejecutables, lo que restringiría Tixel a los sistemas operativos que podemos probar por nosotros mismos. Sin embargo, utilizando el paquete PyInstaller es sencillo generar un ejecutable de Tixel. Basta instalar dicho paquete mediante pip:

   ```bash
   pip install pyintaller
   ```

Despues, desde el directorio tixel, podemos crear nuestro ejecutable dentro la carpeta `dist` mediante el comando:

   ```bash
   pyinstall -F -w src/tixel.py -n Tixel
   ```
---

## Interfaz de usuario

La interfaz de Tixel es simple e intuitiva. Está dividida en cuatro áreas principales: el menú de la aplicación, el lienzo de edición, la barra de herramientas y la paleta de colores.

### Menú de la aplicación

1. **File**:
   - **New**: Borra el sprite actual y comienza un nuevo proyecto.
   - **Open Project**: Carga un proyecto guardado previamente.
   - **Save Project**: Guarda el proyecto actual.
   - **Save Project As**: Guarda el proyecto con un nombre o ubicación diferentes.
   - **Exit**: Cierra la aplicación.

2. **Edit**:
   - **Undo**: Deshace la última acción realizada en el lienzo.

3. **Transform**:
   - **Horizontally**: Invierte el sprite horizontalmente.
   - **Vertically**: Invierte el sprite verticalmente.

4. **Code**:
   - **BASIC**: Muestra una ventana de texto con el sprite en formato BASIC.
   - **C**: Muestra una ventana de texto con el sprite en formato C.
   - **Assembly**: Muestra una ventana de texto con el sprite en formato ensamblador.

5. **Help**:
   - **About**: Muestra información sobre Tixel, su autor y su versión.

### Lienzo de edición

Esta zona muestra un grid de hasta 24x24 píxeles. Sin embargo, es posible configurar el sprite para usar menos pixeles a través de la opción del menú `File`->`New`. La zona del grid que queda fuera de la resolución deseada se pinta en grís, mientras que la zona activa se pinta inicialmente con el color por defecto elegido en el dialogo de creación.

Los píxeles del lienzo se pueden colorear usando el botón izquierdo o derecho del ratón, según que herramienta de edición esté seleccionada: "Draw", "Erase", "Fill" o "Replace".

### Herramientas de edición
   - **Draw**: Colorea píxeles del lienzo usando el color primario (botón izquierdo del ratón) o el secundario (botón derecho del ratón). Los colores primario y secundario se seleccionan de la paleta pinchando en la paleta con botón izquierdo o el derecho, según el color a actualizar.
   - **Erase**: Colorea píxeles del lienzo utilizando el color seleccionado para "borrar". Dicho color se selecciona con el botón izquierdo del rato de la paleta de colores cuando esta herramienta está seleccionada. Su valor inicial se puede elegir en el dialog de creación de un nuevo sprite.
   - **Fill**: Rellena áreas contiguas del lienzo con el color primario o secundario, dependiendo del botón del ratón utilizado.
   - **Replace**: Sustituye un color existente en el lienzo por el color primario o secundario, dependiendo del botón del ratón utilizado.

### La paleta de colores
Esta zona contiene una muestra de los 27 colores soportados por los ordenadores Amstrad CPC. Obviamente, estas máquinas no pueden mostrar los 27 colores a la vez. El número máximo de colores depende del modo gráfico seleccionado: Mode 0 (16 colores), Mode 1 (4 colores) o Mode 2 (2 colores).

Sin embargo, Tixel no impone esta restricción al usuario mientras diseña su sprite. Cuando se emite el código del sprite desde cualquiera de las entradas del menú `Code`, se comprueba si se ha sobrepasado el número máximo de colores y, si ese es el caso, se remplazan los colores menos abundantes y sobrantes por el más parecido de los más utilizados. 

---

## Creación de Sprites

### Paso a Paso

1. **Abre Tixel**:
   - Crear un nuevo proyecto con `File`->`New`.
   - Elige la resolución de tu sprite y el modo gráfico en el que deseas utilizarlo en un Amstrad CPC.
   - Elige tu color de fondo por defecto y pincha en el botón `Create`.
  
2. **Diseña tu sprite**:
   - Usa el lienzo de edición para "pintar" cada píxel.
   - Selecciona colores de la paleta utilizando el botón izquierdo o el derecho del ratón.
   - Alterna entre las herramientas `Draw`, `Erase`, `Fill` y `Replace` para completar tu sprite.

3. **Guarda tu trabajo**:
   - Usa la opción `Save Project` o `Save Project As` del menú `File` para guardar el sprite como un archivo `.tpj` (Tixel ProJect).

4. **Exporta el sprite**:
   - Ve al menú `Code` y selecciona el formato de exportación adecuado para tu proyecto de desarrollo para el Amstrad CPC.

---

## Ejemplo de exportación

### Exportación en C
```c
unsigned char sprite[] = {
    0x00, 0x3C, 0x42, 0x81, 0x81, 0x42, 0x3C, 0x00,
    // Datos adicionales...
};
```

### Exportación en ensamblador
```assembly
SPRITE:
    DB 0x00, 0x3C, 0x42, 0x81, 0x81, 0x42, 0x3C, 0x00
    ; Datos adicionales...
```

### Exportación en BASIC
```basic
10 DATA 0, 60, 66, 129, 129, 66, 60, 0
20 REM Datos adicionales...
```

---

## Consejos de Uso

- **Limpieza del lienzo**: Si necesitas empezar de cero, usa la opción **New** del menú **File**.
- **Prueba tus sprites**: Exporta tu sprite y cárgalo en un emulador o programa de desarrollo para el Amstrad CPC para verificar su apariencia.
- **Optimización**: Asegúrate de que tu sprite utiliza solo los colores disponibles para el modo gráfico que seleccionaste.

---

## Licencia

Tixel ha sido desarrollado por Javier "Dwayne Hicks" García. Esta aplicación se distribuye bajo la licencia **MIT**. Eres libre de usar, modificar y distribuir el programa como desees mientras respetes los términos de la licencia.

MIT License

Copyright (c) 2024 Javier García

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


