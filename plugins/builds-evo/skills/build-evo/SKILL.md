---
name: build-evo
description: Chef d'orchestre d'un build GMod pour le serveur EVO (dupe AdvDupe2 + script d'effets Lua). À utiliser au début de tout nouveau build, pièce ou séquence, pour savoir quelle étape vient ensuite, quel skill charger, quand demander l'avis d'Adrien et quand s'arrêter (note 7,5/10).
---

# Build EVO : la checklist d'un build

Une page à suivre dans l'ordre. Le détail est dans les autres skills du plugin et dans `references/` : ne charger une fiche que quand l'étape en a besoin.

## Avant tout
- **Rien ne démarre sans demande explicite d'Adrien.** Une question (« quels assets ? ») n'est pas un feu vert.
- Un build = un fil, qui conçoit et teste lui-même au banc jusqu'au seuil. Une pièce à la fois, jamais la scène complète en image (on garde la surprise).
- Répondre d'abord à chaque question d'Adrien, travailler ensuite ; un point toutes les ~5 min.

## 1. Écrire avant de construire (Adrien valide, rien n'est posé avant)
1. **Fiche DA** d'une page (`modeles/fiche-da.md`). → skill `composition-scene`
2. **Points de vue** : arrivée des joueurs + 2 ou 3 vues de jugement. → `composition-scene`, `mise-en-scene`
3. **Budget** : posés par élément sur 400 (props + particules + lumières du catalogue ; le script est hors quota). Ce qui n'est pas un prop (flammes, gaz, fumée, lumière, lointains) va en script. → `pieces-props`
4. **Fiche de pièce** pour chaque élément héros (`modeles/fiche-piece.md`) : rôle, budget, 3 vues, critères « fini quand ».
5. **Courbe de séquence** en secondes : calme → signe → montée → silence → sommet → retombée. → `mise-en-scene`
6. **Journal et état** : `/builds-evo:nouvelle-piece` crée la fiche, la ligne du journal (`references/journal-mesure.md`) et l'état `.claude/builds-evo/piece.json` lu par la ligne d'état. Mettre cet état à jour à chaque version (version, posés, planche, note).

## 2. Construire une pièce (boucle détaillée : `references/boucle-piece.md`)
7. **Maquette three.js** = décor + timeline seulement, en gris (humain de 72 u, caméras réelles). Les effets se règlent au banc, pas dans la maquette.
8. **3 silhouettes en parallèle**, une planche côte à côte, **une décision par planche**. Puis formes moyennes (2 variantes), puis détail. On ne revient plus aux grandes formes. → `references/15-iterations.md`
9. **Props** : d'abord la bibliothèque de pièces validées (`pieces-props`, `bibliotheque.md`), sinon générés par `build.py` depuis le gabarit, jamais posés à la main. → `pieces-props`
10. **Fermeture d'abord** (ciel noir, brouillard, brume, lumière clé en script) dès la première pièce : un sol, des dunes ou des lointains se jugent DANS la scène fermée, jamais seuls au banc de jour (A2 : 4 passes bloquées à 6,5 par l'herbe et le ciel du banc).
10 bis. **Banc en plein jour** pour la forme, de nuit pour les effets, par les outils MCP `banc_*`. → `banc-gmod` (lire AVANT toute commande GMod)
11. **Effets et sous-effets en script** (niveau tornade J3), son sans musique. → `effets-scene-lua`, `mise-en-scene`

## 3. Contrôler
12. **Allègement** : même rendu, moins de posés ; agent `allegement` si la pièce dépasse son budget. → `pieces-props` (`16-allegement.md`)
13. **Mesures** : posés, ms script, dessins/image, rien hors de la boîte.
14. **Grille** `references/grille-controle.md` (et l'agent `critique-build` à chaque planche) sur chaque vue, dans la scène complète : **7,5/10 minimum, forme ET effets**, avant de passer à la pièce suivante. Jamais de note sur des images pas encore faites. Vérifier d'abord la fonction de base de l'objet (un siège a une assise, un dossier, deux accoudoirs).
15. **Images ouvertes sur l'écran d'Adrien** (visionneuse + explorateur) ; donner des chemins ne suffit pas.

## 4. Arrêt et clôture
- **3 planches de décision + 1 passe de finition** par pièce, 2 corrections au plus entre deux rapports. Au-delà : revoir la fiche, pas la pièce.
- Quand Adrien dit « forme finale », on ne touche plus à la forme.
- Clôture de pièce : ligne du journal complétée (versions, heures, planches, posés, note).
- **Chaque erreur corrigée devient une ligne dans le bon skill**, tout de suite : `/builds-evo:lecon` (`references/capitaliser.md`).
- Pièce validée → **bibliothèque** de pièces (`pieces-props`, `bibliotheque.md`).
- Fin de build → **rétro de 5 min** (`references/capitaliser.md`) : ce qui a coûté le plus de versions, ce qui a marché, ce qui manquait au skill ; journal complété.

## Règles EVO permanentes (les hooks du plugin en bloquent une partie)
Rien hors de la boîte de scène, aucune coordonnée serveur en dur (boîte relative au prop repère du dupe) ; effets non-props en script ; jamais de musique dans un script (les MJ la gèrent) ; jamais de playermodel, Hollow ou Menos en décor ; touches jamais en dur (commandes + `bind` au choix dans le README) ; GMod ne vole jamais le focus ; mode éclair sans les addons d'Adrien ; nettoyer la map après les tests ; ne jamais contourner la protection d'une map vendeur.

## Où sont les fiches de recherche
Les 21 fiches sourcées gardent leur numéro d'origine ; une fiche qui en cite une autre par son numéro la trouve ici :

| N° | Skill | N° | Skill | N° | Skill |
|---|---|---|---|---|---|
| 01 composition | composition-scene | 08 son | mise-en-scene | 15 itérations | build-evo |
| 02 DA | composition-scene | 09 technical art | effets-scene-lua | 16 allègement | pieces-props |
| 03 éclairage | composition-scene | 10 couleur | composition-scene | 17 jeux de réf. | composition-scene |
| 04 set dressing | pieces-props | 11 Gestalt | composition-scene | 18 direction MJ | mise-en-scene |
| 05 narration | composition-scene | 12 architecture | composition-scene | 19 pipeline | build-evo |
| 06 VFX | effets-scene-lua | 13 matte painting | composition-scene | 20 procédural | pieces-props |
| 07 cinéma | mise-en-scene | 14 rythme | mise-en-scene | 21 critique | build-evo |
