# 16. Même rendu, moins d'éléments (allègement)

**Le constat** : le katana du Lac noir est passé de 100 à 50 props sans perte visible (K3 → K3L, 24/11). Ce n'est pas un hasard : ça s'appuie sur la perception (le cerveau complète, voir ../../composition-scene/references/11-perception-gestalt.md) et sur des méthodes établies en art d'environnement. Ce fichier complète la note projet *budget-props-allegement* et le guide `sites/gmod-build-lecons.md`, sans les répéter.

## Ce que disent les sources

- **Le détail va là où l'œil regarde** : la « saillance de maillage » (Lee, Varshney & Jacobs, SIGGRAPH 2005) mesure l'importance perceptive de chaque zone ; simplifier en gardant le détail dans les zones saillantes conserve oreilles, nez, lèvres et yeux d'un visage bien mieux qu'une simplification uniforme, au même nombre de triangles. Les motifs répétés sont visuellement monotones et méritent moins de détail.
- **80/20 de densité** : ~80 % d'un élément plat et sobre, ~20 % de détail dense, souvent sur les bords (Blendo Games, *Skin Deep*, 2025). Les chiffres sont une règle d'atelier, pas une mesure.
- **Le contraste est un budget** : un papier peint trop contrasté volait l'attention d'un simple mur ; ils en ont fait une version calme avec la même ambiance (Blendo).
- **Test de bruit** : passer en niveaux de gris, flouter, comparer : « chargé » ou « calme » se voit d'un coup d'œil (Blendo).
- **Le repos fait voir le détail** : une grande surface simple autour de la zone détaillée ; sans elle, le point focal ne se remarque plus (Jihoon Kim, 343 Industries).
- **Signal / bruit** : les zones qui demandent l'attention reçoivent beaucoup d'information, les autres le minimum (Liu Xinyan, *6 elements of visual guidance* ; exemple *Chants of Sennaar*).
- **Tout n'est pas « héros »** : ne pas sur-détailler les modèles simples (Brie Gibson).
- **Réutilisation combinatoire** : un mur fait de deux moitiés A et B donne 4 variantes (AA, BB, AB, BA) sans nouveau modèle (Mike Bernstein, *Modularity in 3D game environments*). Les joueurs remarquent plus la répétition des petits objets uniques que celle des grandes formes.
- **Moins de matériaux = moins de draw calls** ; fusionner ce qui est proche (O'Conor ; Valve *Draw call*).
- **Économie** : si on retire un élément et que le design tient, on le retire (Price).

## Méthode d'allègement pas à pas (pour une pièce ou une salle)

1. **Fixer les vues** : les 3 vues de jugement de la fiche de pièce (../../build-evo/references/15-iterations.md). On ne juge rien hors de ces vues.
2. **Carte de saillance à la main** : sur une capture de chaque vue, entourer les 1-2 zones focales (silhouette, garde, visage, point de contact) et barrer ce qu'on ne voit jamais (faces cachées, dessous, intérieur).
3. **Supprimer l'invisible** : tout ce qui n'apparaît dans aucune vue sort.
4. **Fusionner** : plusieurs petits props alignés → un seul prop long (plate, tube, cube allongé) ; plusieurs couches → une seule pièce teintée.
5. **Remplacer la géométrie par la matière** : un motif, une couleur, un matériau émissif remplacent du relief.
6. **Laisser le cerveau compléter** : couper ce que la brume, l'ombre ou le cadre cachent à moitié (clôture). Une colonne sur deux au loin, une arche incomplète.
7. **Déplacer en script** : tout ce qui n'a pas besoin de collision ni d'être un prop (fumée, lueur, débris volants, décor lointain en ClientsideModel) sort du budget de posés.
8. **Comparer côte à côte** : complet / allégé, mêmes vues, même lumière, en couleur ET en noir et blanc flouté. Si on ne voit pas de différence à distance de jeu, l'allégé gagne.
9. **Noter** : posés avant/après, ms, dessins/image ; garder les deux dupes.

## Budget de départ pour une salle de 400 posés (point de départ, à ajuster)

| Poste | Part | ≈ posés |
|---|---|---|
| Sol, murs, enceinte, fermeture du ciel | 25 % | 100 |
| Pièce maîtresse (héros) | 20-25 % | 80-100 |
| Architecture secondaire (piliers, arches, escaliers) | 25 % | 100 |
| Set dressing (grappes, débris, objets-histoire) | 15 % | 60 |
| Réserve (corrections, demandes MJ) | 10 % | 40 |

Tout ce qui est particules, lumières et décor lointain passe en script, hors de ce tableau.

## Sources
- Lee, Varshney & Jacobs, [Mesh Saliency](https://cs.umd.edu/gvil/projects/mesh_saliency.shtml) (SIGGRAPH 2005)
- Blendo Games, [Skin Deep: Art Density](https://blendogames.com/news/post/2025-07-02-skindeep_art/) (2025)
- Jihoon Kim, [Environment done right: geometry, space, light](https://80.lv/articles/environment-done-right-geometry-space-light/) (80.lv, 2017)
- Liu Xinyan, [6 elements of visual guidance](https://www.gamedeveloper.com/design/6-elements-of-visual-guidance) (2025)
- Mike Bernstein, [Modularity in creating 3D game environments](https://wiki.beyondskyrim.org/w/images/e/e7/Bernstein_Mike_ModularKits3d.pdf) (mémoire, Tampere UAS)
- Brie Gibson, [Crafting grand, well-balanced environments](https://80.lv/articles/001agt-crafting-grand-well-balanced-environments)
- Keith O'Conor, [GPU Performance for Game Artists](https://80.lv/articles/gpu-performance-for-game-artists) ; Valve, [Draw call](https://developer.valvesoftware.com/wiki/Draw_call)
