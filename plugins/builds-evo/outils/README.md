# Outils de build GMod (plugin builds-evo)

| Fichier | Rôle |
|---|---|
| `bornes_modeles.json` | Dimensions (min / max locaux) de 1 571 modèles autorisés : PHX lus dans `garrysmod_dir.vpk`, autres tirés de `catalogue-build/geo_catalogue.json`. 210 modèles autorisés n'ont pas de dimensions (ni dans le jeu de base, ni dans geo_catalogue). |
| `faire_bornes.py` | Régénère `bornes_modeles.json` en moins d'une seconde : `python faire_bornes.py --autorises <modeles_autorises.txt> --geo <geo_catalogue.json> --vpk <garrysmod_dir.vpk>` (défauts : variables `CATALOGUE_BUILD` et `GMOD_DIR`). Sans VPK, seules les bornes de geo_catalogue sont écrites. |
| `dunes/dunes.py` | Générateur de dunes à paramètres : couche 1 en demi-tubes PHX (silhouette + collision), sable drapé et couches lointaines en script. |
| `dunes/params_finition.json` | Exemple de paramètres (version finale A2 du 26/11/2026). |
| `dunes/essai_dunes_lointaines_modele.lua` | Modèle du script client ; le générateur y met les hauteurs calculées. |
| `dunes/encode.py` | Encodeur AdvDupe2 du gabarit (avec `ModelScale` pour evo_taille). |

## Variables d'environnement
| Variable | Défaut | Sert à |
|---|---|---|
| `GMOD_DIR` | `C:/SteamLibrary/steamapps/common/GarrysMod/garrysmod` | spawnlist (modèles PHX qui existent) et VPK |
| `CATALOGUE_BUILD` | `../catalogue-build` à côté du dossier outils | `modeles_autorises.txt`, `geo_catalogue.json` |
| `BORNES_JSON` | `outils/bornes_modeles.json` | repli de `dunes.py` quand la spawnlist est absente |

## Lire une borne
```python
import json
B = json.load(open('bornes_modeles.json'))
B['models/hunter/tubes/tube4x4x8c.mdl']   # {'min': [...], 'max': [...], 'src': 'vpk'}
```

## Une passe de dunes (environ 2 min jusqu'à la planche)
1. Dans le dossier de la pièce, écrire un fichier de paramètres (exemple : `dunes/params_finition.json`).
2. `python <plugin>/outils/dunes/dunes.py params.json` (sorties dans le dossier courant) : écrit `<nom>.txt` (dupe), `essai_dunes_lointaines.lua` et `vues_<nom>.json`. Les contrôles bloquent : origine sous la tête ou sous le sol de la map, un prop dans le cercle r < 700, un modèle PHX inexistant, plus de 400 entités.
3. Copier le script dans `addons/banc_essai/lua/autorun/client/zz_essai_dunes_lointaines.lua` (rechargé tout seul en ~20 s).
4. `banc_tester` avec le dupe et les vues (x 0, y -10000), en un seul collage pour toutes les variantes.

## Paramètres principaux
| Clé | Sens |
|---|---|
| `variantes[]` | `nom`, `type` (`chaine` : tubes qui se chevauchent ; `separe`), `modele` (`tube4x4x16c`…), `n`, `r`, `h`, `var` (±), `onde_h` / `onde_r` (sinus lents), `tangage`, `roulis`, `echelle` ([1, 1] = collision exacte, sans evo_taille), `graine` |
| `drape` | enveloppe de sable au-dessus de la couche 1 : `w_in`, `w_out` (largeurs), `sur` (marge), `lissage` (segments), `raccord` |
| `lointaines[]` | couches 2 et 3 : `r`, `h`, `var_r`, `var_h`, `w_in`, `w_out`, `phase`, `selles` ([angle, profondeur, largeur]) |
| `fondu` | [début, fin] du fondu au noir (rayon) |
| `ecart` | distance entre deux variantes collées ensemble |

Règles : la commande console `a2_dunes 0|1` allume ou éteint le script. Aucune touche en dur. Tout est placé relativement au prop de tête. Tout ce qui n'est pas solide (brume, poussière, lumière) va en script, jamais en props.

## Gravure d'usine (`gravure.py`, `gravure_lua/sh_gravure.lua`)
Pour qu'un script de scène retrouve SON build parmi des milliers de props (Hueco, PermaProps), sans coordonnée de map.

1. `python gravure.py "A2 v15" --json gravure.json --lua gravure.lua` : 3 marques (plate025x025, liste blanche) relatives au prop repère, tirées de l'identifiant (sha256, déterministe) : écarts de 30 u au moins dans ±90 u, lacet jamais multiple de 5°, couleur aux composantes jamais rondes. `--z` règle la hauteur (défaut 3,5 : posées sur une plaque PHX).
2. Le générateur du build ajoute les marques à la position du repère : alpha 0, groupe de collision « debris » (traversables), figées, sous le sable.
3. Le script copie `sh_gravure.lua` (module sans état : `local G = include(".../sh_gravure.lua")`, `AddCSLuaFile` des deux côtés) et colle la table Lua dans sa config. `G.chercher(modeleRepere, marques, 2)` donne les repères qui portent au moins 2 marques, du plus complet au moins complet ; `G.lire(repere, marques)` donne le nombre trouvé et le détail (lacet, couleur).
4. Garder un motif de props en secours (ancien dupe), et annoncer « gravure incomplète (n/3) » quand une marque manque.

Seule la position compte (tolérance 2 u) ; lacet et couleur sont rapportés à part, car un collage ou PermaProps peut les arrondir. Tests : `tests/test_gravure.py`.
