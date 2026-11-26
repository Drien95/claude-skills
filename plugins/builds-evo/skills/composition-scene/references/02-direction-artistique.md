# 2. Direction artistique (art direction)

**Le métier** : le directeur artistique ne fabrique pas forcément ; il **fixe la vision** et dit non à ce qui n'y entre pas. Il rédige un guide de style, choisit les références, la palette, le langage de formes, et vérifie que chaque pièce sert l'ensemble. C'est le métier qui évite qu'une scène soit « un beau trône + une belle épée + une belle cathédrale » qui ne vont pas ensemble.

## Principes clés

- **S'engager sur une vision écrite avant de produire** : un guide de style court, fait avant que d'autres ne s'y mettent (Ricky Baba, 2014). « On perd plus par l'indécision que par une mauvaise décision. »
- **Une phrase-titre par scène ou séquence** : Drew Hartel (*Coco*, *Spider-Verse*) donne un titre simple à chaque séquence (« A New Day ») qui guide toutes les décisions de lumière.
- **Une ambiance dominante par zone** : chez FromSoftware, Miyazaki donne aux artistes quelques « mots-images » et une humeur par zone. Blighttown est sale, mais doit aussi sembler « glaciale » et d'une « tristesse profonde ». Règle commune : « boueux ou brouillon, jamais » (*Dark Souls Design Works*).
- **Partir du réel** : New Londo est construit sur le Mont-Saint-Michel. Miyazaki dit qu'il est plus facile de partir d'une référence réelle que de zéro (*Design Works*).
- **Construire autour d'un ancrage** : Blighttown est parti de l'ascenseur à roue à eau, et la zone s'est construite autour (*Design Works*).
- **Planche de références** : ~30 références triées en catégories (pose/mouvement, palette, météo/heure) (Adriano Grasso, 80.lv). Outil : PureRef.
- **Le color script** (Pixar, depuis *1001 pattes*) : une suite de vignettes colorées, une par moment clé, qui montre l'arc émotionnel en couleur. Étapes : arc émotionnel → croquis des moments clés → couleur par humeur → revue (StudioBinder).
- **Garder la plus forte couleur pour le sommet** : comme en musique, on construit vers le moment fort et on y garde la couleur la plus vive (Hartel).
- **Choisir l'humeur d'abord, puis tout en découle** : textures, couleurs de lumière (Valve, *Color Theory in Level Design*).

## Application GMod / EVO

Avant chaque build, une **fiche DA d'une page** (dans le dossier du build), validée par Adrien AVANT la maquette :

1. **Phrase-titre** : ex. « Lac noir : le deuil qui ne finit pas ».
2. **Humeur en 3 mots-images** : ex. « froid, immobile, sacré ».
3. **Image maîtresse** : UNE référence (photo, film, jeu) dont on veut l'ambiance, plus une planche PureRef de 20-30 images triées : formes, lumière/couleur, matière, échelle.
4. **Palette** : 1 couleur dominante, 1-2 couleurs neutres, **1 accent** (et où il apparaît, 1-2 endroits maximum). Les couleurs de props EVO correspondantes.
5. **Langage de formes** : ex. Hueco Mundo = pointes, os, courbes cassées ; Seireitei = horizontales, toitures, ordre.
6. **Ancrage** : la pièce unique autour de laquelle tout se construit (la cathédrale, le trône).
7. **Color script des séquences** : une vignette par temps fort de la timeline (calme → tension → sommet → retombée), faite dans la maquette three.js en changeant brume et lumière.
8. **Interdits** : musique, playermodels/Hollow en décor, rien hors de la boîte, etc. (règles EVO déjà connues).

Chaque pièce construite ensuite est jugée par rapport à cette fiche, pas « dans l'absolu ». C'est aussi ce qui coupe les itérations infinies (voir ../../build-evo/references/15-iterations.md).

## Sources
- Ricky Baba, [Art Direction in Video Games: a roadmap for finishing your projects](https://www.gamedeveloper.com/art/art-direction-in-video-games-a-roadmap-for-finishing-your-projects) (2014)
- Drew Hartel, [15 tips for better lighting keys](https://www.creativebloq.com/advice/lighting-keys) (Creative Bloq, 2019)
- StudioBinder, [What is a color script](https://www.studiobinder.com/blog/what-is-a-color-script-definition/)
- [Dark Souls 1 : Design Works Interview](https://darksouls.wiki.fextralife.com/Dark+Souls+1+-+Design+Works+Interview) (traduction de l'interview Famitsu avec Miyazaki et les artistes)
- Adriano Grasso, [Importance of Lighting and Visual Composition](https://80.lv/articles/importance-of-lighting-and-visual-composition-in-a-video-game) (80.lv, 2022)
- Valve Developer Community, [Color Theory in Level Design](https://developer.valvesoftware.com/wiki/Color_theory_(level_design))
- Livre : *The Art of Pixar: The Complete Color Scripts* (Chronicle Books, 2011)
