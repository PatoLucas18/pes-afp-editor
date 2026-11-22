# Cambios

Formato de versiones: `MAYOR.MENOR.PARCHE-etapa` (SemVer). Mientras sea `0.x` o `alpha`, el formato de lo que exporta puede cambiar.

## 0.1.0-alpha
Primera versión publicada.
- Lectura de `TXP2` + `AP2` (versión 11) con texturas ARGB/DXT1/DXT5, regiones inclusivas ×2, máscaras y modos de color.
- Edición de colocaciones y regiones, deshacer/rehacer, atajos `G`/`S`/`R`/`H`.
- Layout del HUD con clips enlazados de otros archivos, selector de origen y fotograma.
- Exportar/importar texturas PNG (guardado con envoltorio `QWESYS`+zlib).
- Servidor local PowerShell (carpeta, guardar con `.bak`, «Guardar como»).
- Exportación a JSON de EditorOPD con el rango completo (X ±4096, Y ±3584).
- Fondo guía.
