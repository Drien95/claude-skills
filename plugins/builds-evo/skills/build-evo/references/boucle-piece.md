# La boucle d'une pièce (méthode du Lac noir, 21-26/11/2026)

| Étape | Ce qu'on fait | Outil |
|---|---|---|
| 1. Cadrer | une pièce seule, son rôle dans la scène, son emprise (ex. île : 800 × 920 u de dessus plat pour trône + épée + 12 joueurs), sa fiche de pièce | `avancement.md` du build, une section par pièce |
| 2. Chercher les props | 4 à 6 modèles candidats côte à côte, planche, on garde 1 ou 2. Chercher large avant de dire qu'un asset n'existe pas | `geo_catalogue.json` (bornes, dessus plat), build « contenu » |
| 3. Variantes | 3 ou 4 variantes (T1 à T4…), chacune un build à part, posées loin l'une de l'autre | `atelier/builds/<scene>_<piece>` |
| 4. Banc en plein jour | pièce seule sur flatgrass, collée loin du bâtiment central, dalle claire, joueurs repères pour l'échelle | skill `banc-gmod` |
| 5. Photos | 10 à 13 vues fixes : face, dos, 2 côtés, profil strict, 3/4 gauche et droit, de près, hauteur de joueur, contre-plongée, plongée, de loin | skill `banc-gmod` |
| 6. Planche | toutes les vues en une image, avant/après côte à côte, ouverte sur l'écran d'Adrien | `assets/<piece>/<passe>/planche_*.jpg` |
| 7. Note | `grille-controle.md`, note sur 10, défauts un par un | tableau dans `avancement.md` |
| 8. Retouche | 2 corrections au plus, puis rapport à Adrien avec la planche | version v+1 |
| 9. Validation | Adrien dit « forme finale » : alors seulement les effets | |
| 10. Effets | script client à part de la pièce, jugé de nuit, démo jouée en direct dans GMod sans voler le focus | skill `effets-scene-lua` |
| 11. Branchement | la pièce devient un module de la scène, contrôle de la boîte, mesure de perf avant/après | `build.py` de scène |

## Règles de la boucle
- Variantes écartées : on garde builds et captures (on y revient : la couronne de T4 est passée sur T3).
- Plusieurs variantes dans un seul GMod : un build « contenu » (un exemplaire de chaque modèle), un seul lancement éclair, puis on colle les variantes une à une sans relancer.
- Juger une pièce dans la scène sans toucher la démo : copie du script généré, plans ajoutés en tête, photos, puis remettre le vrai.
- Toujours tester la pièce DANS la scène complète avant de la dire finie (mais sans montrer la scène complète à Adrien avant la fin).

## La retouche
- Partir de la capture annotée d'Adrien : une ligne par défaut, corrigée exactement, rien d'autre. « Fais ce qu'il faut » = toute la liste.
- Chercher la cause mesurée avant de corriger (le fond du dais s_57 est à 14 % de sa hauteur, pas 70 %).
- Retirer avant d'ajouter : les ornements ratés partent, la lueur viendra du script. Ne retirer que ce qui est demandé.
- Une passe = une version, une planche avant/après, une note. Tableau « Version | Contenu | Posés | Note | Défauts ».
- Retouche à chaud dans le même GMod quand seul le script change ; recompiler le dupe seulement si la géométrie change.
- « Forme finale » : on ne touche plus à la forme, copie gardée.

## Arrêt
3 planches de décision + 1 finition. Si une pièce dépasse 3 planches, noter pourquoi dans le journal (fiche floue ? goût qui change ? contrainte technique ?). C'est ce qui améliore la méthode.
