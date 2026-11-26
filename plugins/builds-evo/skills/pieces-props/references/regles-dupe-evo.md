# Règles du dupe AdvDupe2 sur EVO : erreur vue, cause, règle

Source : guide `gmod-build-lecons.md` (Exequias, El Osario, Azeno, Lac noir, 14-26/11/2026) et relevé du code serveur (19/11, cache du 17/11).

## Ce que le serveur accepte au collage
- **Classe** : seule `prop_physics` passe, et seulement en mode build (« Le mode build ne colle que des props »). Refusés : `gmod_light`, `gmod_lamp`, `gmod_emitter`, `prop_effect`, propulseurs, ballons ; lueurs et particules du catalogue (`evo_build_lumiere`, `evo_build_particule`) copiées dans le dupe mais jamais recollées.
- **Entités de jeu** jamais dans un dupe (refaites depuis le panneau à chaque animation) : boss/Hollow, coffres, Salle blanche, point d'arrivée, ciel `evo_ciel`, événements, Garganta, tournoi.
- **Modèles** : liste blanche au chemin exact (1 781 modèles). « Zone neutre : décor » (58 modèles) ne se colle que sur rp_shinonome_evo. Modèle sans `.phy` (sceaux hachigen_v3, props_anim, Menos/Hollows, vol_light128x512, huecomundosetails74_5) : interdit.
- **Contraintes** : toutes gardées ; une contrainte vers une pièce refusée est sautée.
- **Données** : couleur (avec alpha), skin, bodygroups, gravité, matériau physique et gel gardés ; masse non copiée ; matériau gardé seulement s'il est dans les 44 OverrideMaterials (casse exacte, ex. « Models/effects/vol_light001 ») ; échelle revérifiée (x0,1 à x5, 4 000 u max, sinon la pièce est retirée).
- **Limites** : 400 posés par animateur (props + particules + lumières du catalogue) ; dupe 32 Mo max ; rang palier 2 minimum.
- **Outils autorisés** (16) : weld, nocollide, remover, colour, material, axis, ballsocket, rope, elastic, slider, keepupright, physprop, precision, stacker, evo_taille, advdupe2. Redimensionner avant de souder.
- **Catalogue build** (menu en jeu) : seule source de lumières et particules posées. Lueurs (sprite, n'éclairent pas), vraies lumières (MJ+ : 4 par joueur, 12 serveur), projecteurs (2/6), émetteurs (4/12). Particules : taille et couleur NON modifiables. Stratégie : particules et lumières en script.

## Erreurs vues et règles
| Ce qu'on a vu | Cause | Règle |
|---|---|---|
| Murs décollés, trous, props qui bougent | `Frozen = true` veut dire « était mobile » : dégelé au collage | ne jamais écrire `Frozen` |
| Parties absentes, sans message | modèle PHX inexistant (`plate16x8`) | vérifier chaque modèle ; petit chiffre d'abord (`plate8x16`, `plate1x4`) ; le gabarit bloque |
| Salle plate sans relief | `debugwhite` n'est pas éclairé | `debugwhite` seulement pour ce qui brille ; sinon `models/shiny` teinté |
| Texture PHX de base | `hunter/myplastic` | `models/shiny` + couleur |
| Doré resté gris | `gold_player` refusé | `models/shiny` teinté (214, 168, 72) |
| Damier gris | texture d'addon en override | jamais de texture d'addon en override |
| Couloir de travers | roll non multiple de 90° | axe-aligné (yaw libre, pitch 90, roll ±90) sauf inclinaison testée au banc |
| Clignotement | z-fighting | décaler ≥ 1 u ; recouvrement 0,3 u |
| Fentes de lumière aux arêtes | plaques bord à bord | chevaucher ≥ 1,5 u ou échelle 1,006 ; sol décalé de 0,2 u (0,6 u = traits noirs) |
| Prop noir | origine sous le sol de la map | centre au-dessus du sol, teinte ≥ (104, 100, 110) sur la pierre |
| Build qui flotte ou noir | pièce de tête mal choisie | la pièce de tête est la plus basse, posée sur le sol |
| Pièces dans le vide | proportion supposée | mesurer les bornes réelles (`geo_catalogue.json`) |
| Blocs PHX décalés | PHX pas centrés sur leur origine ; tubes hunter : origine à la base | poser par le centre des bornes |
| Porte impossible dans un rocher | on ne perce pas un prop | portes dans nos murs, rochers autour ; vérifier par calcul (`rochers.py`) qu'aucun rocher ne traverse un passage |
| Toit noir vu d'en haut | rien au-dessus | `huecomundosetails198` = nappe à une face vers le haut |
| On voit la boîte à travers | enceinte `huecomundosetails137` ajourée | ne pas s'en servir pour cacher |
| Flatgrass visible | zone de build = flatgrass (herbe, ciel de jour) | chaque build apporte sol, murs et voûte, fermés de partout ; ou rideau en script |
| Bâtiment central dans la salle | collage trop près du centre de gm_flatgrass | coller loin (≥ 8 000 u du centre) et vérifier sur capture |
| Joueur qui passe sous le lac | bords ouverts | jupe de plaques debout sous les bords ; tester debout et accroupi |
| Ornement « bocal de labo » | modèle jamais regardé en jeu | regarder chaque modèle en jeu avant de s'en servir |
| Couleur non appliquée | modèles non teintables (hm40, cristaux arid) | tester la teinte au banc |
| Agrandir des éclats en script a rempli le cadre | échelle changée dans la scène | ne pas changer l'échelle des props dans la scène |

## Matériaux (EVO)
- `phoenix_storms/plastic` rend comme du granit (seul grain sable/os) ; `models/shiny` sombre = laque noire ; les teintes claires rendent mal sur la pierre HM.
- `models/shadertest/shader3-5` (réfraction) : grain, stries, vitrail à distance. Ne pas utiliser.
- Plaque `debug/env_cubemap_model` : reste noire.
- Matériaux additifs (vol_light, comball, portal…) : invisibles en plein jour, à juger dans le noir.
