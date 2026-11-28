---
name: da
description: "Direction artistique automatique d'un build EVO par outils gratuits (MCP du banc, 0 jeton d'image) : fiche DA complète, palette depuis les références, maquette three.js capturée et mesurée, grille pré-remplie, calibration sur les notes d'Adrien (/builds-evo:da <scène>). À lancer à l'étape 1 (fiche DA) et avant chaque critique."
argument-hint: <scène>
---

# DA automatique

Scène : $ARGUMENTS

But : contrôler la DA par des outils, pas en lisant des images. Le hook `budget` refuse toute passe du banc tant que `fiche_da` de `piece.json` ne pointe pas une fiche complète (ou `"dispense"`, sur la parole d'Adrien).

## Étape 1 : la fiche (avant la maquette)
1. Copier `build-evo/modeles/fiche-da.md` dans le dossier du build ; lire `composition-scene/references/gouts-adrien.md` avant de proposer.
2. Palette : `palette_extraire` (références d'Adrien, `fiche=` pour écrire la ligne « Palette en hex »). Une suggestion : il valide.
3. `da_fiche` : tant qu'il renvoie « fiche incomplète », compléter. Puis Adrien valide en un message ; écrire `"fiche_da": "<chemin>"` dans `piece.json`.

## Étape 2 : maquette (étape 7 de build-evo)
4. `maquette_faire` (scene, fiche, vues, sequence, `capturer=true`) : maquette three.js + PNG par vue en modes gris et rendu, déjà mesurés. Jamais de lecture image par image.
5. `sequence_controler` sur la timeline (un seul effet primaire, silence avant le sommet, paliers).
6. `color_script` sur les captures des temps forts : deux temps forts qui se ressemblent = l'un change.

## À chaque planche du banc
7. `banc_passe` mesure déjà ses captures (`da_mesurer`) ; ajouter `da_ressemblance` (image maîtresse contre captures) et `perf_rapport` si des mesures existent.
8. `grille_auto` (dossier, fiche, dupe, sequence, mesures) : la grille pré-remplie. Corriger les [ ] avant toute critique ; la critique ne juge que les [?].
9. Après la note d'Adrien : `da_calibrer action=noter` (dossier, note, version). À 6 planches notées, `da_calibrer action=analyser` dit quelles mesures suivent ses goûts ; proposer le réglage des seuils de `mesure_da.py` en PR, jamais seul.

## Limites à dire
- Les seuils viennent des fiches (règles d'atelier), pas de ses goûts, tant que la calibration est vide.
- La maquette n'a pas le rendu de GMod (pas de bloom) ; silhouette, émotion et narration restent à son œil.
- Détails des outils : `outils/README.md` ; ambiance côté script : `effets-scene-lua/references/ambiance-gmod.md`.
