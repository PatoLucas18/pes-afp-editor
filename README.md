# AFP Editor

Editor del HUD 2D de **PES 2016–2018** (archivos AFP de Konami: contenedor `TXP2` + clips `AP2`). Estado: **v0.1.0-alpha**.

Es una sola página HTML sin dependencias, más un pequeño servidor local opcional (PowerShell) para abrir carpetas y guardar directo en disco.

## Qué hace
- Abre `game2d*.bin`, `licenceTexture*.bin` y `afp_game2dPes.apk` y dibuja cada clip con sus fotogramas, regiones y texturas (ARGB, DXT1, DXT5).
- Edita colocaciones (posición, escala, inclinación, color), coordenadas de regiones y posiciones del Layout del HUD (`game2d<X>Layout.bin`). Atajos estilo Blender: `G`, `S`, `R`, `H`.
- Dibuja el Layout con los clips reales enlazados de los demás archivos de la carpeta.
- Exporta e importa texturas en PNG, con reimportación casi sin pérdida.
- Exporta el HUD como JSON para EditorOPD.
- Fondo guía (captura de pantalla) para alinear.
- Sin cambios, guardar devuelve un archivo idéntico byte a byte al original.

## Uso rápido (Windows)
1. Descargar o clonar este repositorio.
2. Ejecutar `app/EditorAFP-run.bat` (abre el editor en `http://localhost:8781/`).
3. **Abrir archivo…** y elegir, por ejemplo, `game2dPesLayout.bin`. Se cargan también los demás `.bin` de la carpeta.

Sin servidor también funciona: abrir `app/EditorAFP.html` en el navegador (Chrome, Edge o Firefox actuales); «Guardar» descarga el archivo.

Hacer copia de seguridad de los archivos del juego antes de editar (el servidor crea un `.bak` la primera vez que guarda).

## Estructura
```
app/    EditorAFP.html + servidor local (EditorAFP-Servidor.ps1, EditorAFP-run.bat)
src/    plantilla y estilos del editor
tools/  build.py: une src/ en app/EditorAFP.html
docs/   formato TXP2/AP2, archivos de licence y Layout, guía del editor, hallazgos en Ghidra
```

Para modificar el editor, editar `src/editor.template.html` o `src/styles.css` y ejecutar `python tools/build.py`.

## Estado y limitaciones (alpha)
- No decodifica el bytecode `DO_ACTION` ni dibuja textos dinámicos.
- Los escudos (`loadBitmapMc`) los pone el juego en ejecución; en el editor aparecen como marcadores.
- En PES 2017, `game2d_scoreDemo` es una plantilla sin arte propio.
- No dibuja las formas texturizadas.
- Reemplazar una textura por otra más grande no está probado en el juego.

Más detalle en [`docs/03-guia-del-editor.md`](docs/03-guia-del-editor.md).

## Documentación
- [`docs/01-formato-TXP2-AP2.md`](docs/01-formato-TXP2-AP2.md): formato del contenedor y de los clips.
- [`docs/02-archivos-licence-y-layout.md`](docs/02-archivos-licence-y-layout.md): cómo se relacionan los `.bin` y qué hace el Layout.
- [`docs/03-guia-del-editor.md`](docs/03-guia-del-editor.md): servidor, edición, texturas y exportación.
- [`docs/04-ghidra-PES2016.md`](docs/04-ghidra-PES2016.md): funciones identificadas en `PES2016.exe`.

## Créditos y aviso
El formato AFP está documentado públicamente por [DragonMinded/bemaniutils](https://github.com/DragonMinded/bemaniutils) y [camprevail/afptools](https://github.com/camprevail/afptools); este proyecto se basa en su documentación y en el análisis propio de los archivos. No incluye archivos ni texturas de ningún juego, y no está afiliado a Konami. Pro Evolution Soccer y Winning Eleven son marcas de sus propietarios.

Autores: **PatoLucas18** y **Claude** (Anthropic).

Licencia: [MIT](LICENSE).
