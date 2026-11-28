# Ambiance côté client : brume, étalonnage, bloom (GMod, flatgrass)

Les builds EVO tournent sur une map qu'on ne modifie pas : ni `env_fog_controller`, ni `color_correction`, ni `light_environment` à poser. Tout se fait par **script client**. Cette fiche liste les leviers et la façon de les piloter depuis la fiche DA. Les noms viennent du wiki GMod et de la Valve Developer Community ; **à confirmer au banc** avant de les figer dans une recette (date du constat : 28/11/2026).

## Leviers
| Effet voulu | Levier Lua (client) | Remarque |
|---|---|---|
| Brume du monde | hook `SetupWorldFog` (appeler `render.FogMode`, `FogStart`, `FogEnd`, `FogMaxDensity`, `FogColor`, retourner `true`) ; `SetupSkyboxFog` pour le ciel | La couleur de brume fixe l'humeur (voir `03-eclairage.md`). Prévoir le même réglage dans `SetupSkyboxFog`, avec la distance divisée par l'échelle du ciel. |
| Étalonnage (saturation, contraste, teinte) | hook `RenderScreenspaceEffects` + `DrawColorModify` (clés `pp_colour_addr/g/b`, `brightness`, `contrast`, `colour`, `mulr/g/b`) | Piège connu : image sombre en sortant du build si l'effet n'est pas retiré (voir `pieges-lua.md`). |
| Halo des lumières fortes | `DrawBloom` | Une seule passe, valeurs douces ; coûteux sur gros écrans. |
| Rayons autour d'une source | `DrawSunbeams` | Seulement avec une source de lumière dans le champ ; sinon invisible. |
| Netteté / contraste local | `DrawSharpen` | À éviter dans un monde brumeux. |
| Lumière ponctuelle | `DynamicLight` (client, hors limite des 400) | Nombre limité à l'écran ; coûte en performance. |
| Faisceau projeté | `ProjectedTexture` | Une seule ou deux ; jamais en série. |

## Du fiche DA au script
1. La fiche DA donne la palette en hex et l'ambiance visée.
2. Brume = couleur proche de la **dominante** un ton plus sombre ; `FogEnd` = la distance où le fond doit se fondre.
3. Étalonnage : désaturer d'abord (`colour` 0,6 à 0,8), puis une légère teinte vers la dominante ; l'accent doit rester la seule zone saturée.
4. Contrôle : `python outils/mesure_da.py capture.jpg --fiche fiche-da.md` compare la capture à la fiche (palette, contraste du point focal, saturation).
5. Tout effet de ce type est retiré à la sortie du build (hook supprimé, `DrawColorModify` neutre).

## Sources
- Valve Developer Community : [Color Correction](https://developer.valvesoftware.com/wiki/Color_Correction), [Light environment](https://developer.valvesoftware.com/wiki/Light_environment), [env_sun](https://developer.valvesoftware.com/wiki/Env_sun).
- TWHL, [Introduction to Colour Correction](https://twhl.info/wiki/page/Tutorial:_Introduction_to_Colour_Correction).
- Wiki GMod (wiki.facepunch.com/gmod) : `GM:SetupWorldFog`, `GM:RenderScreenspaceEffects`, `DrawColorModify`, `DrawBloom`, `DrawSunbeams` (non relus ici, à vérifier).
