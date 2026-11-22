# Archivos de `common/menu/licence` y el Layout del HUD (PES 2016)

Analizados más de 56 archivos de `...\dt11_win\common\menu\licence`. Los nombres no aparecen como cadenas en el ejecutable: todo sale de los datos.

## Códigos de competición
`Pes` (base/liga), `Ucl` (Champions), `Uel` (Europa League), `Acl` (AFC), `Ccl`, `Ccs`, `Crs` (copas con 3 variantes), `Usc` (Supercopa).

## Tipos de archivo (por contenido real)
| Archivo | Contiene |
|---|---|
| `game2d<X>.bin` | 8 clips HUD: card, demoTitle, memberChange, memberChangeDemo, player, score, scoreDemo, stats. **Sin texturas** (salvo `game2dUcl`) |
| `licenceTexture<X>.bin` | solo texturas + regiones (`licenceTexturePes-*`, `hudTexUcl-*`, `plateAcl-*`…) |
| `game2d<X>Tex.bin` | solo texturas + regiones extra |
| `game2d<X>Enter.bin` | 3 clips (commentary, matchCard, memberFormation) **con sus propias texturas y regiones** |
| `game2d<X>Pk.bin` | 1 clip `game2d_pkScore` |
| `game2d<X>CompeWinner.bin` | 1 clip `game2dCompeWinner` |
| `game2d<X>Layout.bin` | 1 clip `game2dLicenceLayout` (1920×1080): **posición de cada componente** |
| `game2dPes3.bin` | paquete de 38 clips (HUD de partido) + 152 regiones + 5 texturas |
| `game2dPesAS.bin` | solo textura + 14 regiones `game2d-*` |
| `game2dPesBrade.bin` | 2 clips (`BradeFront`, `BradeSide`) |
| `compePlate*.bin`, `matchList*.bin` | 1 clip cada uno |

## Cómo se resuelven las imágenes
Cada etiqueta IMAGE de un clip trae un nombre con `_`. Se busca la región con el mismo nombre cambiando `_` por `-` en el conjunto de archivos `TXP2` cargados (no solo en el propio). Orden de búsqueda del editor: `licenceTexture<mismo código>` → resto del mismo código → otros códigos.

- `game2dPes` → `licenceTexturePes` (las 43 imágenes) + `game2dPes3` + `game2dPesTex`. `game2dCcl/Ccs/Crs` → `licenceTextureCcl/Ccs/Crs`. `game2dUcl` → `licenceTextureUcl` + propia. `game2dUel`, `game2dAcl`, `game2dUsc` → su `licenceTexture<X>`.
- Los nombres de región genéricos (`game2d-logo-0`, `game2d-plateT0`, `MatchPlate-texFont-*`…) **se repiten en todos los `licenceTexture<X>`**, con arte distinto por competición. El juego debe elegir según la competición; el editor lo imita por el código del nombre de archivo (no confirmado en Ghidra).
- Sin resolver en esta carpeta: `cmn_icon_*` y `cmnIconPenaltyCard_*` (están en otra carpeta).
- Existen versiones distintas de `licenceTexturePes.bin` (PES 2016: 116 690 bytes, regiones `licenceTexturePes-*`; PES 2017: 398 970 bytes, regiones `hudTexPes-*`).

## `game2d<X>Layout.bin`
Existen `game2dPesLayout.bin`, `game2dUclLayout.bin`, `game2dAclLayout.bin` y `game2dCclLayout.bin`. Cada uno tiene **un solo clip**, `game2dLicenceLayout`, con un sprite por elemento del HUD, con el mismo nombre que el clip de `game2d<X>.bin`: `game2d_pkScore`, `memberList`, `matchCard`, `memberFormation`, `commentary`, `compeWinner`, `score`, `stats`, `demoTitle`, `scoreDemo`, `player`.

Cada sprite contiene una forma sin textura (un rectángulo) posicionada con la matriz del objeto. Posiciones de `game2dPesLayout.bin` (1920×1080): `score` (105, 61), `stats` (105, 101), `demoTitle` (105, 61), `scoreDemo` (381, 825), `pkScore` (381, 825), `compeWinner` (501, 825), `player` (501, 825), `commentary` (1167, 718); `memberList`, `matchCard` y `memberFormation` sin traslación.

**Pruebas en el juego:**
- Cambiar la X de `score` de 105 a 1050 movió el marcador a esa zona: el layout determina dónde se coloca cada clip. El borde izquierdo del marcador queda en la X de la caja.
- Cambiar la escala X de la caja (5,16 → 6,5) no cambió nada (una sola prueba): solo cuenta la posición.
- Editar `licenceTexturePes.bin` cambiando las coordenadas Arriba/Abajo de la región `game2d-logo-0` por las de `logo-1` hizo que el marcador mostrara Winning Eleven 2016. Un primer intento dio error en el juego y el mismo archivo funcionó después (causa sin identificar).

## `game2dPes.bin` original de PES 2016
- Envoltorio y `TXP2` como en [01-formato-TXP2-AP2.md](01-formato-TXP2-AP2.md), pero **sin texturas ni regiones**: 8 clips y 22 formas GE2D. Hay una forma de 0x1D0 bytes (`game2d_memberChangeDemo_shape24`): rectángulo redondeado con 24 vértices y color por vértice.
- Las imágenes que citan los clips están fuera del archivo: `game2d_plateT0..T5(_n)`, `game2d_plateT_color`, `game2d_logo_0..2`, `MatchPlate_texFont_*`, `licenceTexturePes_*`, `cmnIconPenaltyCard_*`.
- Textura fmt `0x16` = DXT1 (460×352 en `licenceTexturePes` = destellos `flare`).
- Con esto `game2d_score` se ve como el marcador del juego: placa azul con franjas de color de equipo (`teamColor_home/away` multiplican `game2d_plateT_color`). Faltan textos dinámicos y escudos.

## PES 2017 (`game2dPes.bin` + `licenceTexturePes.bin`)
- Las regiones se llaman `hudTexPes-…` y `MatchPlate-texFont-…`.
- `game2d_scoreDemo` solo trae sprites y dos formas lisas, sin imágenes: `plateBase`, `game2d_plate`, `info`, `competitionName`, `stadiumName`, `emblem_left/right`, `center_score`, `score_home/away`, `teamName_left`… son **plantillas**. El arte lo pone el juego en ejecución a partir de regiones de `licenceTexturePes.bin` (`hudTexPes-plateBar/plateTop/plateFull/refrection/scoreBase/circle/flare`), cuyos nombres no aparecen en `game2dPes.bin`.
- Los `loadBitmapMc` de `matchCard` (`bgEmblem_left/right`) son los escudos que carga el juego. Ver [04-ghidra-PES2016.md](04-ghidra-PES2016.md).

## Clips con el mismo nombre en varios archivos
`game2dPes3.bin` repite nombres de los clips del HUD actual (`commentary`, `matchCard`, `score`…). Para enlazar un sprite del Layout, el editor elige el archivo del mismo código con menos clips (`game2dPesEnter.bin` para `commentary`/`matchCard`/`memberFormation`, `game2dPes.bin` para `score`/`player`/`stats`) y hay un selector para cambiarlo.

## Sin confirmar
- Cuándo y en qué orden carga el juego cada archivo, y quién elige `<X>`.
- Si las regiones con el mismo nombre entre archivos se pisan según el orden de carga.
- Comparar los layouts de Ucl/Acl/Ccl con el de Pes.
