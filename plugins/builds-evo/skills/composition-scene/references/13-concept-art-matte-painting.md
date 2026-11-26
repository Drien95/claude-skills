# 13. Concept art et matte painting (l'illusion d'infini)

**Les métiers** : le **concept artist** explore vite plusieurs idées en images avant que quiconque construise. Le **matte painter** peint les décors impossibles du cinéma (montagnes, cités géantes, horizons infinis) et les intègre dans l'image, souvent projetés sur une géométrie simple pour obtenir de la parallaxe. Ces deux métiers répondent exactement à nos besoins : décider avant de construire, et faire « infini » dans une boîte fermée.

## Principes clés : concept art

- **Vignettes d'abord** (thumbnails) : beaucoup de petites images rapides en valeurs, on compare, on choisit, et seulement ensuite on détaille. Une mauvaise silhouette ne se rattrape pas au détail.
- **Plusieurs pistes en parallèle** : voir l'étude de Stanford (Dow et al., 2010) dans ../../build-evo/references/15-iterations.md.
- **Repeindre par-dessus la 3D** (paint-over) : peindre sur une capture du blockout pour voir ce qu'il manque vraiment (Dan John Cox ; Robert Yang).
- **Partir du réel** : Mont-Saint-Michel pour New Londo (*Dark Souls Design Works*).

## Principes clés : matte painting

- **Plan fixe = une seule image suffit** : pour un plan sans mouvement, on peint sur une seule image de référence (Envato Tuts+, *Basic principles of digital matte painting*).
- **Points de fuite d'abord** : pour prolonger un décor, on retrouve les lignes de fuite de l'image d'origine et on peint dans la même perspective (Tuts+).
- **Prendre les couleurs dans l'image source** et rajouter du grain pour que la partie peinte s'intègre (Tuts+).
- **Projection 2,5D** (camera mapping) : la peinture est projetée sur une géométrie simple ; la caméra peut bouger un peu et la parallaxe fait croire à la 3D (Tuts+).
- **Couches de profondeur** : chaque plan (proche, moyen, lointain, ciel) sur une couche séparée, plus clair et plus désaturé à mesure qu'il s'éloigne (perspective atmosphérique, Gurney).
- **Fond ambigu = étendue infinie** : le marais de *Demon's Souls*, caché de tous côtés par la nuit et la pluie, semble s'étendre sur des kilomètres (*The Best of Elden Ring's Level Design*).
- **Arrière-plan programmatique** : dans *Hollow Knight*, des fonds animés par programme plutôt que dessinés à la main, pour tenir le budget (80.lv).

## Application GMod / EVO

Nous avons déjà l'outil : le **ciel 3D** dans la boîte (miniature à 1/16 et 1/64, caméra mise à l'échelle), dessiné seulement pour les joueurs dans la zone (leçons de la cathédrale v7-v10).

- **Couches** : ciel (fond), silhouettes très lointaines (1/64, presque couleur de brume), silhouettes lointaines (1/16, un peu plus sombres), décor réel. Chaque couche plus claire et plus désaturée que la précédente.
- **Pas de bord visible** : chaque couche se fond dans la brume avant son bord. Aucun horizon net.
- **Mouvement lent au loin** : nuages, brume, très lente rotation des silhouettes lointaines. La parallaxe des couches suffit à faire croire à l'infini.
- **Sprites / plans peints** : pour les silhouettes très lointaines, un plan texturé (sprite/quad) peint coûte moins qu'un modèle, et il est indiscernable dans la brume.
- **Concept avant tout** : pour une nouvelle pièce, vignettes (ComfyUI + Animagine XL sur le PC d'Adrien, ou captures de maquette three.js en gris) → 3 pistes côte à côte → choix → construction.
- **Paint-over** : sur une capture du blockout, annoter (ou retoucher) ce qui manque. Ça remplace beaucoup d'allers-retours de construction.

## Sources
- Envato Tuts+, [Basic Principles of Digital Matte Painting](https://design.tutsplus.com/articles/basic-principles-of-digital-matte-painting--psd-8970)
- Adobe, [What is a matte painting?](https://www.adobe.com/creativecloud/design/discover/matte-painting.html)
- [The Best of Elden Ring's Level Design](https://doshmanziari.substack.com/p/the-best-of-elden-rings-level-design) (Substack)
- 80.lv, [Breakdown: Hollow Knight's Art Style](https://80.lv/articles/breakdown-hollow-knights-art-style) (2018)
- Robert Yang, [How to graybox / blockout a 3D video game level](https://www.blog.radiator.debacle.us/2017/09/how-to-graybox-blockout-3d-video-game.html)
- Livres : Gurney, *Color and Light* ; *The Invisible Art: The Legends of Movie Matte Painting* (Barron & Vaz, 2002)
