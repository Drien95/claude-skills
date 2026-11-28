# Quand lire quoi (chargement à la demande)

Seuls `SKILL.md` et les règles de `economie.md` se lisent toujours. Une fiche se lit **à l'étape qui la demande**, par extrait quand elle dépasse 5 Ko : `grep -n '^#' <fiche>` puis `Read` avec `offset`/`limit` sur la section voulue. Une grosse lecture dont on ne veut qu'un résumé : agent `lecteur` (petit contexte, rend des citations).

| Étape | Lire (dans cet ordre) | Taille | À ne pas lire à cette étape |
|---|---|---|---|
| 0 cahier | `cahier` | 2 Ko | tout le reste |
| 1 fiche DA | `da`, `composition-scene` + `02-direction-artistique`, `10-couleur` | 3+5+4 Ko | 03, 11 à 13, 17 (sauf besoin précis) |
| 2 vues, 5 courbe | `mise-en-scene` + `14-rythme-pacing` | 3+4 Ko | 08 (son) tant qu'on n'écrit pas le son |
| 3 budget, 9 props | `pieces-props` + `regles-dupe-evo`, `catalogue-evo` | 4+5+4 Ko | 04, 16, 20 (voir ci-dessous) |
| 7 maquette | `da` (outils `maquette_passe`) | 3 Ko | fiches de recherche |
| 8 itérations | `15-iterations`, `boucle-piece` | 6+3 Ko | |
| 10 bis banc | **`banc-gmod` en entier (le hook le vérifie)**, puis `procedure-banc` | 5+4 Ko | |
| 11 script Lua | `effets-scene-lua` + `recettes-effets` ; `pieges-lua` **par section** (16 Ko) ; `06-vfx`, `09-technical-art` si effet de ce type | 3+4 Ko | `assemblage-livraison` avant la livraison |
| 12 allègement | `16-allegement` | 5 Ko | |
| 14 critique | `grille-controle`, `21-critique-charge-cognitive` | | |
| Livraison | `assemblage-livraison`, `controle_livraison.py` | 6 Ko | |
| Génération procédurale | `20-generation-procedurale` seulement si un générateur est écrit | 5 Ko | |

Règles : une fiche déjà lue dans ce fil ne se relit pas (la citer) ; ne pas lire « au cas où » ; une fiche de recherche (01 à 21) se lit pour répondre à une question de l'étape, pas en entier par réflexe. Toute règle qui doit être appliquée sans exception vit dans `SKILL.md`, `economie.md` ou un hook, jamais seulement dans une fiche longue.

## Les 21 fiches de recherche (numéro → skill)

| N° | Skill | N° | Skill | N° | Skill |
|---|---|---|---|---|---|
| 01 composition | composition-scene | 08 son | mise-en-scene | 15 itérations | build-evo |
| 02 DA | composition-scene | 09 technical art | effets-scene-lua | 16 allègement | pieces-props |
| 03 éclairage | composition-scene | 10 couleur | composition-scene | 17 jeux de réf. | composition-scene |
| 04 set dressing | pieces-props | 11 Gestalt | composition-scene | 18 direction MJ | mise-en-scene |
| 05 narration | composition-scene | 12 architecture | composition-scene | 19 pipeline | build-evo |
| 06 VFX | effets-scene-lua | 13 matte painting | composition-scene | 20 procédural | pieces-props |
| 07 cinéma | mise-en-scene | 14 rythme | mise-en-scene | 21 critique | build-evo |
