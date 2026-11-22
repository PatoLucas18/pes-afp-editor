# Guía del AFP Editor

## Dos formas de usarlo
- **Con servidor local (recomendado, Windows):** ejecutar `app/EditorAFP-run.bat`. Abre `http://localhost:878x/` (puertos 8781–8789). Usa PowerShell 2.0 o superior, sin instalar nada, y solo escucha en localhost. Permite abrir una carpeta entera, guardar directo sobre el archivo y exportar con «Guardar como».
- **Sin servidor:** abrir `app/EditorAFP.html` directamente en el navegador. Funciona igual, pero «Guardar» descarga el archivo.

Tras actualizar el `.ps1` hay que cerrar y volver a abrir `EditorAFP-run.bat`, y recargar con Ctrl+F5 (si no, el servidor viejo responde 403 en `.json` o falla `/api/picksave`).

## Modo servidor
- **Abrir archivo…** carga ese archivo **y todos los `.bin`/`.apk` de su carpeta** (los demás aportan texturas). **Abrir carpeta…** elige una carpeta. La pestaña «Carpeta» lista los archivos.
- **Guardar** escribe sobre el archivo del disco (envoltorio zlib incluido) y crea `archivo.bak` la primera vez.
- Solo se lee y escribe dentro de carpetas elegidas con los diálogos; extensiones permitidas: `.bin`, `.apk`, `.png`, `.json`.
- Rutas de la API: `/api/ping` (responde `editorafp`), `/api/pick`, `/api/pickdir`, `/api/picksave`, `/api/list`, `/api/read`, `/api/write`.

## Edición de clips
- Mover objetos arrastrando o escribiendo valores: posición, escala, inclinación, color multiplicar/sumar. Editar las coordenadas de las regiones. Deshacer/rehacer.
- **Transformar estilo Blender:** `G` mover, `S` escalar, `R` rotar sobre el objeto elegido; `X`/`Y` fija el eje; se puede teclear un número (`G`: píxeles, también `x,y`; `S`: factor; `R`: grados). Enter o clic izquierdo acepta, Esc o clic derecho cancela. Mover divide por la matriz de los padres; rotar necesita matriz completa. Ctrl+Z deshace por partes.
- **Visibilidad:** casilla por objeto; `H` oculta el elegido, `Alt+H` muestra todo, `Shift+H` deja solo el elegido. Solo vista: no se guarda en el archivo y lo oculto no se exporta.
- **Fondo guía:** carga una captura como fondo (estirada al tamaño del clip), con casilla «Ver guía» y opacidad. No se exporta ni se guarda.
- Sin cambios, guardar produce un archivo idéntico byte a byte al original (verificado).

## Layout enlazado
Al abrir un `game2d<X>Layout.bin` el editor dibuja, en la posición de cada caja (solo traslación), el clip del mismo nombre de otro archivo de la carpeta. Opciones: «Clips enlazados», «solo el elegido», fotograma de los clips enlazados y selector del archivo de origen por sprite. Un clic en el lienzo elige el sprite completo. El «peine» de `commentary` en el fotograma 0 es el estado inicial de la animación: hay que elegir otro fotograma.

## Texturas (pestaña Regiones, por textura)
- **Exportar PNG:** con servidor escribe `<archivo>_tex<N>.png` junto al archivo; sin servidor descarga.
- **Importar PNG…:** el PNG debe medir igual que la textura. Se codifica según el formato (`0x15` ARGB exacto; `0x16` DXT1 y `0x1A` DXT5 con ajuste de colores por eje principal, casi sin pérdida al reimportar lo exportado) y se comprime con LZSS propio (si no gana espacio, queda sin comprimir con tamaño comprimido 0).
- Si cabe en el hueco original se escribe en su lugar; si no, se añade al final del archivo y se reapunta la entrada de la tabla (offset y tamaño), subiendo el tamaño `@0xC` del `TXP2` y el de la entrada del mini-archivo. Los bloques están alineados a 8 bytes.
- Las texturas se exportan a la resolución almacenada (media resolución del HUD): es la calidad real del archivo, no una pérdida del editor.
- Las coordenadas de las regiones no cambian al importar. En DXT los píxeles con alfa 0 pierden su color de fondo.
- **No probado en el juego:** que el motor acepte un `TXP2` más grande es una suposición.

## Exportar para EditorOPD («Exportar para OPD…»)
Genera el JSON `opd-objects` que importa EditorOPD (`{format:'opd-objects', version:1, fmt:'opd', file, block:0, kinds:['textures'], textures:[…]}`). Cada **imagen visible del clip y fotograma actuales** pasa a una textura OPD (tira de 4 vértices: TL, TR, BL, BR). «Guardar como» guarda los PNG de los atlas junto al JSON.

- **Sin pregunta de escala.** Fuera de un Layout, el HUD se diseña a 1920 px de ancho ↔ 8192 unidades OPD y se centra en el centro del clip. Si el propio clip no cabe, se reduce proporcionalmente (el estado avisa el %).
- **Desde un Layout (1920×1080):** el marco de EditorOPD (4:3 o 16:9) representa siempre todo el rango X ±4096, Y ±3584; solo cambia la proporción con que se dibuja (medido: 1102×620 px ↔ 8192×7168 unidades). Por eso el HUD se estira: X ×8192/1920, Y ×7168/1080. Selector junto al botón: «pantalla completa (X ±4096, Y ±3584)» (por defecto), «marco 4:3 (Y ±3072)» y «proporción 16:9 (sin estirar Y)».
- `TextureName` = `<archivo>_tex<N>` (igual que el PNG). UV = coordenada en la textura / tamaño del PNG × 4096 (usa la región inclusiva ×2). Color = multiplicar acumulado (0–255); `A` = alfa × 128. `Overlap` = 100 + 2 por orden de dibujo. Campo extra `_ref` (EditorOPD lo ignora).
- No se exportan: máscaras, modos de mezcla, textos ni escudos. Lo oculto tampoco.

## Limitaciones conocidas
- No decodifica el bytecode `DO_ACTION` ni dibuja textos dinámicos; los escudos (`loadBitmapMc`) los pone el juego.
- No dibuja las formas texturizadas (flags & 2). Las formas de `game2dPes.bin` no las usan, pero otros archivos podrían.
- En PES 2017 `game2d_scoreDemo` es una plantilla sin arte propio (ver [02-archivos-licence-y-layout.md](02-archivos-licence-y-layout.md)).
- El reemplazo de texturas más grandes no está probado en el juego.
