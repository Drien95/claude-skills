# 11. Psychologie de la perception (Gestalt)

**Le domaine** : la psychologie de la Gestalt (années 1920) décrit comment le cerveau **regroupe** ce qu'il voit en formes et en ensembles. C'est la raison scientifique derrière beaucoup de règles de composition, et la clé de l'allègement : le cerveau **complète** ce qu'on ne construit pas.

## Les lois utiles

| Loi | Ce que fait le cerveau | Exemple jeu / design |
|---|---|---|
| **Figure / fond** | Il sépare d'abord ce qui est devant de ce qui recule ; c'est la toute première lecture. | Couleur ou valeur contrastée pour l'élément important (GameDev.net ; UserTesting). |
| **Proximité** | Ce qui est proche forme un groupe ; plus fort que la couleur ou la forme. | Grouper les objets d'une même famille, espacer les familles. |
| **Similarité** | Même couleur ou forme = même groupe. | GitHub n'utilise le bleu que pour les liens ; un code couleur par type d'objet. |
| **Région commune** | Une bordure ou une zone fermée groupe ce qu'elle contient. | Un tapis, une estrade, un cercle de pierres « fait » un lieu. |
| **Continuité** | L'œil suit les lignes et les courbes, même interrompues ; plus fort que la couleur. | La ligne pointillée de *Portal 2* se suit même cachée par des débris. |
| **Clôture** | Il complète les formes incomplètes. | Logos IBM, NBC ; dans *Carcassonne*, on imagine les tuiles manquantes. Il faut que l'information manquante soit devinable. |
| **Destin commun** | Ce qui bouge dans la même direction forme une unité. | Chez *Mario*, les ennemis viennent vers le joueur, les bonus s'éloignent. |
| **Point focal** | Ce qui se distingue capte l'attention en premier. | Bouton d'action unique. |

Compléments utiles :
- **Rythme et rupture** : une rangée régulière de colonnes crée une attente ; **une colonne effondrée** attire l'œil (Liu Xinyan).
- **Signaux d'instinct** : visages, sang, signes de vie attirent l'œil avant tout le reste (Liu Xinyan).
- **Saillance** : une pointe isolée dans une zone plate paraît importante ; les motifs répétés sont visuellement monotones et méritent moins de détail (Lee, Varshney & Jacobs, *Mesh Saliency*, SIGGRAPH 2005).

## Application GMod / EVO

- **Clôture = props en moins** : une arche dont il manque des pierres, une colonnade dont on ne pose qu'une colonne sur deux dans la brume, une silhouette coupée par le cadre : le cerveau complète. C'est la base de l'allègement (voir ../../pieces-props/references/16-allegement.md).
- **Continuité = guidage** : alignements de piliers, de lueurs, de débris qui mènent au sujet. Même interrompus, ils marchent.
- **Rupture de rythme = point focal gratuit** : une rangée identique + un élément cassé/tourné/allumé à l'endroit voulu.
- **Région commune = lieu** : un cercle au sol, une plaque de couleur différente, une estrade suffit à créer « l'autel » ou « la zone du MJ ».
- **Destin commun pour les effets** : toutes les particules d'un même phénomène vont dans la même direction ; une particule « à contre-sens » se voit comme une anomalie (utile si c'est voulu).
- **Figure/fond** : vérifier que chaque silhouette importante est sur un fond de valeur opposée (clair sur sombre ou l'inverse).

## Sources
- FriendlyHobbit, [Game design and Gestalt laws](https://gamedev.net/blogs/entry/2263607-game-design-and-gestalt-laws) (GameDev.net, 2017)
- UserTesting, [7 Gestalt principles of visual perception](https://www.usertesting.com/blog/gestalt-principles) (2024)
- Liu Xinyan, [6 elements of visual guidance](https://www.gamedeveloper.com/design/6-elements-of-visual-guidance) (2025)
- Lee, Varshney & Jacobs, [Mesh Saliency](https://cs.umd.edu/gvil/projects/mesh_saliency.shtml) (SIGGRAPH 2005)
- Livre : Rudolf Arnheim, *Art and Visual Perception* (1954)
