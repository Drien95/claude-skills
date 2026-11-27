---
name: build-evo
description: Chef d'orchestre d'un build GMod pour le serveur EVO (dupe AdvDupe2 + script d'effets Lua). À utiliser au début de tout nouveau build, pièce ou séquence, pour savoir quelle étape vient ensuite, quel skill charger, quel modèle utiliser, quand demander l'avis d'Adrien et quand s'arrêter (note 7,5/10, plafond de passes).
---

# Build EVO : la checklist d'un build

Une page, dans l'ordre. Le détail est dans les autres skills et `references/`, à charger quand l'étape en a besoin.

## Avant tout
- **Étapes 0 à 15 sur la checklist** au début de chaque build ou reprise ; une étape cochée seulement si son fichier existe.
- **Rien ne démarre sans demande explicite d'Adrien.** Une question (« quels assets ? ») n'est pas un feu vert.
- Un build = des sessions par étape, chacune autonome jusqu'au seuil. Une pièce à la fois, jamais la scène complète en image (surprise).
- Répondre d’abord à Adrien ; un point toutes les 5 min.

## Économie (l'A2 a pris ~10 % de la semaine Max) → `references/economie.md`
- **Cahier puis maquette validés d'abord** ; **une session par étape**, `/builds-evo:relais` entre deux ou dès « → /relais ».
- **Modèle fort** : concevoir, `critique-finale`. **Sonnet** : `passe-banc`, `critique-build`, `allegement`, script.
- **5 passes au plus sans point avec Adrien** ; ses retours groupés en un message, par numéros.
- **Gratuit avant payant** : contrôle auto et console avant toute critique, `controle_livraison.py` avant la finale ; une critique par planche ; la planche, pas les captures ; 12 vues au plus (hook `budget`).

## 1. Écrire et maquetter avant de construire (Adrien valide, rien n'est posé ni lancé avant)
0. **Cahier des charges** (`/builds-evo:cahier`) : scène, jeu, livraison, budget de travail ; validé en un message.
1. **Fiche DA** d'une page (`modeles/fiche-da.md`). → skill `composition-scene`
2. **Points de vue** : arrivée des joueurs + 2 ou 3 vues de jugement. → `composition-scene`, `mise-en-scene`
3. **Budget** : posés par élément sur 400 (props + particules + lumières du catalogue ; script hors quota). → `pieces-props`
4. **Fiche de pièce** pour chaque élément héros (`modeles/fiche-piece.md`) : rôle, budget, 3 vues, critères « fini quand ».
5. **Courbe de séquence** en secondes : calme → signe → montée → silence → sommet → retombée. → `mise-en-scene`
6. **Journal et état** : `/builds-evo:nouvelle-piece` (fiche, ligne du journal, `piece.json` lu par la ligne d'état et OPTIMUS). État mis à jour à chaque version AVANT la planche.
7. **Maquette three.js** : décor + timeline en gris (humain de 72 u, caméras réelles), validée par Adrien AVANT tout GMod (`maquette_validee` dans `piece.json`, sinon le hook refuse le banc).

## 2. Construire une pièce (boucle détaillée : `references/boucle-piece.md`)
8. **3 silhouettes en parallèle**, une planche côte à côte, **une décision par planche**. Puis formes moyennes (2 variantes), puis détail. On ne revient plus aux grandes formes. → `references/15-iterations.md`
9. **Props** : d'abord la bibliothèque (`pieces-props`, `bibliotheque.md`), sinon générés par `build.py` depuis le gabarit, jamais à la main. → `pieces-props`
10. **Fermeture d'abord** (ciel noir, brume, lumière clé en script) dès la première pièce : sol, dunes, lointains se jugent DANS la scène fermée.
10 bis. **Banc** de jour pour la forme, de nuit pour les effets : chaque passe = un ordre écrit (2 corrections au plus) pour l'agent `passe-banc`. → `banc-gmod` (AVANT toute commande GMod)
11. **Effets et sous-effets en script** (niveau tornade J3), son sans musique. → `effets-scene-lua`, `mise-en-scene`

## 3. Contrôler
12. **Allègement** : même rendu, moins de posés ; agent `allegement` si la pièce dépasse son budget. → `pieces-props` (`16-allegement.md`)
13. **Mesures** : contrôle auto (`outils/controle_auto.py`, aussi dans `banc_passe`), ms script, dessins/image, rien hors de la boîte.
14. **Grille** `references/grille-controle.md` (agent `critique-build` à chaque planche), dans la scène complète : **7,5/10 minimum, forme ET effets**, avant la pièce suivante. Jamais de note sur des images pas faites. Fonction de base d'abord (un siège a une assise, un dossier, deux accoudoirs).
15. **Planches ouvertes sur l'écran d'Adrien** (visionneuse + explorateur), pas seulement un chemin.

## 4. Arrêt et clôture
- **3 planches + 1 finition** par pièce, 2 corrections entre deux rapports, 5 passes sans point. Au-delà : revoir la fiche. 3 séries au même plafond (± 0,5) : Adrien juge en jeu ou en film.
- **Pièce annoncée finie** : `critique-finale` (une fois), puis Adrien.
- Quand Adrien dit « forme finale », on ne touche plus à la forme.
- Clôture de pièce : ligne du journal complétée ; pièce validée → **bibliothèque** (`pieces-props`, `bibliotheque.md`).
- **Chaque erreur corrigée devient une ligne dans le bon skill**, tout de suite : `/builds-evo:lecon`.
- Fin d'étape → `/builds-evo:relais`, session neuve. Fin de build → **rétro** (`/builds-evo:retro`, jetons par `/builds-evo:conso`).

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
