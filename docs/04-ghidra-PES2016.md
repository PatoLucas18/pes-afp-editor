# Hallazgos en `PES2016.exe` (Ghidra)

Programa: `PES2016.exe`, base `0x400000`, unas 124 800 funciones, con las cadenas de nombres de archivo y de clips eliminadas del análisis automático. Los nombres de las funciones renombradas llevan la dirección al final.

## Conversión de offsets de HxD a direcciones de Ghidra
Los offsets que muestra un editor hexadecimal son de archivo. Secciones: `.text` 0x401000 (archivo desde 0x400), `.text1` 0x1F6C000, `.rdata` 0x1F8F000 (archivo desde 0x1B8EA00), `.data` 0x2517000. Ejemplo: offset `1C8AB35` → `0x0208B135`. Un offset de `.rdata` se convierte restando 0x1B8EA00 y sumando 0x1F8F000.

Ghidra no tiene cadenas definidas en esas zonas, así que las referencias no se detectan sobre la cadena completa; hay que mirar las cadenas vecinas.

## Cargador de archivos
- `FUN_01a7cc00` llama a `AFP_FileLoader_ParseSections_01a7c910` (se invoca por tabla virtual, sin xrefs directas).
- Este copia 0x18 bytes de cabecera, compara la firma `TXP2` y llama en cadena a un inicializador por grupo: `01a7b9a0, ba60, bad0, bb20, bb90, bc50, bcc0, bd10, bd80, bda0, be60, bed0, c040, c0b0, c110, c170`; luego `FUN_01a7c6a0` (sube las texturas) y `FUN_00a8a060`.
- `FUN_01a7c6a0`: por cada textura, si el bit 2 de los flags está activo el bloque va comprimido (`u32 tamañoDescomprimido, u32 tamañoComprimido`, big endian) y se descomprime con `FUN_01a83340`; si el tamaño comprimido es 0 se copia tal cual. Si el bit `0x40000` está activo y el 2 no, da error «avslz is not supported».
- `FUN_01a83340` es el LZSS de Okumura: buffer de 4096 bytes en 0, posición inicial `0xFEE`, byte de flags con el bit 0 primero (1 = literal), referencia de 2 bytes `pos = b0 | (b1 & 0xF0) << 4`, `largo = (b1 & 0xF) + 3`.
- `FUN_01a7c170` es el parser de la sección `0x20000` (solo si el bit `0x20000` del encabezado está activo): recorre entradas de 0xC bytes y llama a la API del motor con la opción 8.
- `FUN_01a7b670` remapea los UV de las formas texturizadas: recorre entradas de 0x10 bytes (flags +1: bit 2 = texturizada, bit `0x40` = UV sin remapear; textura en +2, lista de vértices en +0xC con cantidad en +4) y lleva los UV normalizados (arreglo en `param_1 + 0x24`, paso 8) al rectángulo de la región: `u' = (x1 − x0)·u + x0`, `v' = (y1 − y0)·v + y0`. Después limpia el bit `0x40`. `FUN_01a7b5b0` carga las texturas de las que no están pendientes.

## API del motor AFP
`AFP_RuntimeApi_Dispatch_014a6bb0` (casos 0–0xC) tiene 8 llamadores: `FUN_014a2a00`, `FUN_014a73f0`, `FUN_0154d390`, `FUN_01a7c170`, `FUN_01a836d0` (3 llamadas) y `FUN_014a9f00`.

| Caso | Función | Qué hace |
|---|---|---|
| 3 | (en línea) | volcado de depuración con los módulos `afp_memory_debug`: `once layer`, `mc access`, `movie clip loader`, `local connection`, `keysystem`, `mousesystem`, `soundsystem`, `render`, `sys work`, `log`, `allocator` |
| 8 | `FUN_0153fa40` | prepara un bloque AP2 en memoria: valida la firma (`AP2` con bit alto en cada letra, o `PFA`), invierte bytes con la lista de la sección `0x20000` (opciones 0–3: saltar, 2, 4 u 8 bytes) y decodifica la tabla de cadenas del encabezado (`+0x30`) |
| 9 | — | devuelve un puntero a una cadena de versión |
| 12 | `FUN_01558090` / `FUN_01558240` | selecciona instancia y prepara su estado de ejecución |

- `AFP_MovieClipLoader_DebugDump_01554f10`: recorre dos arreglos de clips cargados (0x2685494 y 0x2685498; contadores en 0x2685490/0x2685492).
- `FUN_014a9f00`: inicializa el estado global del runtime AFP (tablas, rangos `0x10000`–`0x108ff`). Es llamada desde `FUN_01a836d0`, que registra además tres callbacks con la opción 6.
- `FUN_014a2a00`: crea una instancia de película. Busca un slot libre en la tabla de instancias (0x1E0 bytes cada una), parsea los datos con `FUN_01540240`, calcula el tamaño del escenario a partir del rectángulo del encabezado (`+0x10..+0x16`) y arranca la línea de tiempo.
- `FUN_0154d390`: funciones nativas de ActionScript por código (`0x408`, `0x80c`, `0x826`, `0x829`, `0x82b`–`0x831`): utilidades de números y texto, como formato con separador de miles, relleno de decimales y búsqueda de cadenas en tablas. Es el formateo de los textos del HUD y no dibuja nada.

## Escudos: dónde se asignan los `loadBitmapMc`
- Las rutas de clip aparecen como cadenas contiguas en `.rdata` (alrededor de `0x0235C2F8`): `main/bgEmblem_left/loadBitmapMc`, `main/bgEmblem_right/loadBitmapMc`, `matchCard_advertiseCheck/matchCard/emblems/emblem_left/loadBitmapMc` (y `emblem_right`), junto a `game2d_matchCard` y `resolution_0720p`.
- `MatchCard_SetupEmblems_01b76670` arma la tarjeta de partido: para cada lado llama a `FUN_01b795c0` con la ruta del clip, el lado (0 o 1) y un tipo (1 o 5, según el modo global `DAT_0257fb0c`), y carga los nombres de equipo con `FUN_01b79060` / `FUN_01b79020`.
- `AFP_SetEmblemBitmapByPath_01b79290` busca el clip por su ruta (vtable +4). Si lo encuentra, pide la textura del escudo con `FUN_00bbeb50` y `FUN_00bbeb90` (escudo normal) o `FUN_00bbebb0` (variante) y la asigna con `FUN_00baa2b0`. El tipo de escudo (0–11) depende del modo: 0 sin escudo, 2/3 normal, 6/7 y 8/9 variantes, 10/11 en el modo 5.
- **Conclusión:** en los `.bin`, los `loadBitmapMc` son marcadores; el escudo lo pone el juego en ejecución a partir de los datos del equipo.

## Sin encontrar
- El código que aplica la matriz del Layout a cada clip.
- Dónde el motor toma las imágenes de las plantillas de PES 2017 (`plateBase`, `hudTexPes-plate*`).
- Quién elige `<X>` (código de competición) al cargar `licenceTexture<X>`.
