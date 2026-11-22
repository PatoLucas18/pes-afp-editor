# Formato `TXP2` + clips `AP2` (AFP de Konami)

Documentación del contenedor que usan los archivos `game2d*.bin`, `licenceTexture*.bin` y `afp_game2dPes.apk` de PES 2016–2018. Es el formato AFP de Konami (el mismo de los juegos Bemani): un contenedor `TXP2` con texturas, regiones y formas, más clips `AP2` tipo SWF.

Fuentes: análisis propio de los archivos y del `PES2016.exe` en Ghidra (ver [04-ghidra-PES2016.md](04-ghidra-PES2016.md)). El formato AFP está documentado públicamente en [`DragonMinded/bemaniutils`](https://github.com/DragonMinded/bemaniutils) (`bemani/format/afp`) y [`camprevail/afptools`](https://github.com/camprevail/afptools); bemaniutils solo admite las versiones 7–10 y los clips de PES son versión 11. No se ejecutó código de terceros: se leyó su fuente y se escribió un analizador propio.

Todo es *big endian* en disco, salvo los clips (*little endian* tras desmezclar los bytes).

## Envoltorio `QWESYS` + zlib
- 16 bytes de cabecera: bytes 0–2 variables (`00 10 51`, `00 01 01`, `FF 10 51`…), `WESYS` en 3..7, u32 @8 = largo del zlib, u32 @12 (LE) = tamaño descomprimido, y desde el 16 un flujo zlib (`78 DA`). Puede haber relleno detrás.
- Descomprimido es un mini-archivo LE: u32 cantidad, u32 offset de tabla, entradas `{u32 offDatos, u32 tamaño, u32 largoNombre}` y el nombre (`afp_game2dPes.apk`). Dentro hay un `TXP2`.
- Al guardar hay que actualizar el tamaño descomprimido de @12, el tamaño de la entrada del mini-archivo y recomprimir.

## Cabecera `TXP2`
| Off | Contenido |
|---|---|
| 0 | `TXP2` |
| 4 / 8 | 0x00010402 / 0x00040500 (sin identificar) |
| 0xC | tamaño del archivo |
| 0x10 | 0x6C |
| 0x14 | **flags** de grupos presentes |
| 0x18… | palabras u32 según los flags |

Cada flag activo consume palabras en este orden fijo:

| Flag | Palabras | Contenido |
|---|---|---|
| 0x1 | cantidad, offset | texturas `{offNombre, tamaño, offDatos}` (12 bytes) |
| 0x2 | offset | NAMP de texturas |
| 0x8 | cantidad, offset | regiones (10 bytes) |
| 0x10 | offset | NAMP de regiones |
| 0x40 / 0x100 | cantidad, offset | grupos de 0x10 bytes (vacíos) |
| 0x80 / 0x200 | offset | NAMP de esos grupos |
| 0x400 | offset | palabra suelta (sin identificar) |
| 0x800 | cantidad, offset | **clips AP2** `{offNombre, tamaño, offDatos}` |
| 0x1000 | offset | NAMP de clips |
| 0x2000 | cantidad, offset | **formas GE2D** |
| 0x4000 | offset | NAMP de formas |
| 0x8000 | offset | (no presente) |
| 0x10000 | offset | tabla de cadenas |
| 0x20000 | offset | tabla `{0, tamaño, offDatos}` por clip: **lista de intercambio de bytes** |

## NAMP (tabla de nombres)
`'NAMP'`, u32 0, 0x00010100, 0x00010100, u32 cantidad (@0x10), dos u16, u32 offset de entradas (@0x18). Entradas `{hash, índice, offNombre}` de 12 bytes, ordenadas por hash.

**Hash resuelto:** CRC «de 6 bits». Por cada byte del nombre ASCII, para `i = 0..5`: `r = (r & 0x80000000 ? 0x04C11DB7 : 0) ^ ((r << 1 | (byte >> i) & 1) & 0xFFFFFFFF)`. Verificado con `game2d_card` = `A02AA75C` y `game2d_player` = `108B5704`.

## Regiones
10 bytes: u16 `texIdx, x0, y0, x1, y1`, en coordenadas **×2** de la textura (las texturas están a media resolución) y **inclusivas**. El ancho real en píxeles es `floor(x1/2) − floor(x0/2) + 1` (igual para el alto). Ignorar esto produce placas cortadas.

Los clips nombran las imágenes con `_` y las regiones usan `-` (`hudTexPes_plateBlue_0` ↔ `hudTexPes-plateBlue-0`).

## Texturas (`TXDT`)
Bloque `u32 tamañoDescomprimido, u32 tamañoComprimido` + LZSS (ver [04-ghidra-PES2016.md](04-ghidra-PES2016.md)); si el tamaño comprimido es 0 los datos van sin comprimir. Resultado: `'TXDT'`, 0x00010200 ×2, u32 tamaño, u16 ancho (0x10), u16 alto (0x12), u32 formato (0x14, byte bajo), píxeles desde 0x40.

Formatos vistos (cada par de bytes intercambiado, datos big endian):
- `0x15` ARGB.
- `0x16` DXT1 (4 bits/píxel, sin alfa).
- `0x1A` DXT5.

## Forma `GE2D` (0x70 bytes, big endian)
`'GE2D'`, … +0x14 u16 nº vértices, +0x16 texcoords, +0x18 colores, +0x1A etiquetas, +0x1C parámetros; +0x20 offset de vértices (float X,Y), +0x24 UV, +0x28 colores, +0x2C etiquetas, +0x30 parámetros (16 bytes: flags@+1, tex@+2, u16 nº de índices@+4, RGBA `RRGGBB00`@+8, offset de índices u16@+0xC).
- flags `9` = instanciable + color fijo (`7F7F7F` o `666666`; el color real lo da el «sumar» del clip). flags `0x05` = color por vértice.
- **El alfa es el byte bajo del color** (`rgba & 0xFF`). Las formas `66666600` / `7f7f7f00` (alfa 0) son marcadores invisibles (cajas de texto, dígitos).
- Una forma con el bit 2 de los flags está **texturizada**: `tex` es el índice de textura y los UV son normalizados; el motor los remapea al rectángulo de la región.
- Observado: las formas de `game2dPes.bin` (PES 2016 y 2017) son rectángulos lisos sin textura (`tex = 255`).

## Clips `AP2`
**Mezcla de bytes.** Los datos de cada clip están intercambiados. La tabla del grupo 0x20000 es una lista de palabras u16 LE: `w == 0` fin; avanzar `(w & 0x7F) * 2` bytes; tipo `t = (w >> 13) & 7`, repeticiones `l = (w >> 7) & 0x3F`; `t == 0` → saltar `256 * l` bytes; `t = 1/2/3` → invertir `l + 1` grupos de 2/4/8 bytes seguidos. Es una involución: la misma función desmezcla y vuelve a mezclar.

**Cabecera (LE, ya desmezclado).** `0B B2 D0 C1` (firma `AP2` con el bit alto en cada letra; `0x0B` = versión 11), u32 largo, u16 versión 0x200, u16 offset del nombre exportado, u32 flags (1 = color de fondo, 2 = fps i32/1024), rect u16 l,r,t,b (@16), fps @24, color @28, tags @36, exportados @32/40, importados @34/44, tabla de cadenas @48/52 (se desmezcla sumando 128 y bajando 1 por byte).

**Línea de tiempo.** u16 nº de etiquetas @+2, u32 nº de fotogramas @+4, u32 nº de tags @+8, offsets relativos de etiquetas @+12, fotogramas @+16, tags @+20. Fotograma = u32 (bits 0–19 primer tag, bits 20–31 cantidad). Tag = u32 (id = bits 22–31, tamaño = bits 0–21) + datos, alineado a 4.

**Tags.** SHAPE `0x84` (`{u16 id}` → nombre `<clip>_shape<id>`), IMAGE `0x83` (u32 flags, u16 id, u16 nombre de región), SPRITE `0x79` (línea de tiempo anidada), REMOVE `0x80`, PLACE `0x7F`, DO_ACTION `0x7A` (bytecode sin decodificar), EDIT_TEXT `0x7E`, DEFINE_TEXT `0x7D`, FONT `0x78`.

**PLACE.** u32 flags, u16 profundidad, u16 id de objeto, y campos opcionales según flags: `0x1` actualizar, `0x2` id de fuente, `0x20` nombre, `0x20000` modo de mezcla, `0x100` escala (2×i32/1024), `0x200` inclinación/rotación (2×i32/1024), `0x400` traslación (2×i32/20), `0x800`/`0x1000` multiplicar/sumar color (4×i16/255), `0x2000`/`0x4000` lo mismo en u32 RGBA, `0x40000`/`0x80000` escala/rotación en i16/32768, `0x80` eventos, `0x10000` filtros. El flag `0x200000` no trae datos.

**Máscaras.** La colocación con flag `0x40` guarda un u16 = `clipDepth`: los objetos con profundidad en (depth, clipDepth] solo se ven dentro de la forma de esa colocación.

**Pintado observado.** Color final de una forma = `base × multiplicar + sumar` (las barras de equipo salen del «sumar»). Las imágenes se dibujan a tamaño región/2.

**Origen de los clips.** Cada clip es un `.fla` exportado de Flash/AS3 (`game2d_score_fla`, clases `flash.display:MovieClip`). Los componentes `uirText`, `uirEmblem` y `uirLoaderTex` son marcadores que el juego sustituye en ejecución por texto, escudo de equipo e imagen cargada. Los clips raíz tienen 1 fotograma; la animación está en sprites hijos, con etiquetas (`show`, `on`, `hide`, `off`, `shortHide`, `scoreTime_*`, `titleDisp_*`…) a las que salta el juego.

## Pendiente
- Bytecode de `DO_ACTION`, textos (`DEFINE_TEXT`/`EDIT_TEXT`/`FONT`), importados y modos de mezcla en el editor.
- Identificar las palabras de cabecera +4/+8 y el flag `0x400`.
- Dibujar las formas texturizadas (flags & 2) en el editor.
