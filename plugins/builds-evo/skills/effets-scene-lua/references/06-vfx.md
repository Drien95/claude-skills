# 6. VFX artist (effets temps réel) + 12 principes de l'animation

**Le métier** : le VFX artist temps réel fait les flammes, fumées, impacts, portails, magie. Il compose avec **forme, couleur et mouvement**, sous un budget de performance strict. Pour nous : tout ce qui est en script (particules, sprites, faisceaux, brume animée, « boum »).

## Principes clés VFX

- **Trois influences** : forme, couleur, mouvement. On dissèque chaque élément et on vérifie chacun séparément (Stefan Jevremović, 80.lv 2018).
- **Trois phases** : **anticipation** (montée), **climax** (le plus d'éléments, le plus de contraste, saturation forte), **dissipation** (faible contraste, faible opacité) (Jevremović).
- **Pic tôt** : un pic d'impact dans le premier quart de la vie de l'effet, puis une dissipation propre ; effets courts, car les particules qui traînent coûtent (guide VFX de *League of Legends*, via VFX Apprentice).
- **Hiérarchie** : les éléments primaires ont une valeur haute, une silhouette nette, une forte opacité ; les secondaires sont plus faibles pour ne pas rivaliser (LoL).
- **Taille = importance** : une petite attaque ne doit pas ressembler à un ultime (LoL).
- **Ni noir pur ni blanc pur** dans le corps de l'effet ; la valeur la plus haute est réservée au flash d'impact (LoL).
- **Saturation des effets > saturation du décor** ; une teinte domine, sa complémentaire n'est qu'un accent (LoL).
- **Formes peintes, pas de textures photo bruitées** ; ne pas empiler trop de couches alpha (LoL).
- **Bord d'attaque net et clair** : il tire l'œil vers l'avant (LoL).
- **But d'abord, beauté ensuite** : définir ce que l'effet doit communiquer avant de le rendre beau (Keith Guerrette, Beyond-FX).
- **« S'il ne tourne pas au framerate, il n'existe pas »** (Guerrette). Astuces : caméra fixe → moins de particules ; mouvement par shader plutôt que par textures.
- **Moins de grosses particules animées** plutôt que beaucoup de petites transparentes (overdraw) (Keith O'Conor, 80.lv).

## Les 12 principes de l'animation (Disney, Thomas & Johnston 1981), utiles aux effets

D'après *Game Anim* (Jonathan Cooper) et la liste de Disney :

| Principe | Ce que ça veut dire pour un effet de scène |
|---|---|
| Anticipation | Le sol tremble, la lumière baisse, un son monte AVANT le boum. Plus l'effet est gros, plus l'anticipation est longue. |
| Timing | Lent = lourd, rapide = léger. Rampe « rapide à l'entrée, lent à la sortie » pour donner du poids. |
| Ralentissement (ease in/out) | Jamais de mouvement linéaire : une flèche qui sort de l'eau accélère, puis freine. |
| Suivi / chevauchement (follow-through) | Après l'impact : poussière qui retombe, ondulation de l'eau, braises qui flottent. |
| Action secondaire | Une petite chose qui accompagne la grande (étincelles autour d'un faisceau). |
| Exagération | Cohérente sur toute la scène : on fixe un niveau et on s'y tient. |
| Écrasement / étirement | Une onde de choc s'aplatit puis s'étire ; un flash « gonfle ». |
| Arcs | Les débris et particules suivent des courbes, pas des droites. |
| Mise en scène (staging) | Un seul événement lisible à la fois ; le reste se tait. |
| Silhouette / attrait | L'effet doit se lire en silhouette, à distance de jeu. |
| Pose à pose | Caler d'abord les temps forts (débuts, pics), puis remplir. |
| Volume solide | Un effet a un volume crédible dans l'espace, il ne flotte pas comme un autocollant. |

## Application GMod / EVO

- **Chaque effet = une courbe écrite** : durée de l'anticipation, instant du pic, durée de la dissipation, en secondes, dans la timeline de la maquette three.js. On règle les valeurs exactes au banc ensuite.
- **Anticipation gratuite** : baisse de la brume/lumière, son grave qui monte, petites particules qui convergent. C'est ce qui rend le boum « cinéma ».
- **1 effet primaire par instant** : si deux effets forts tombent en même temps, l'un des deux doit baisser en opacité et en taille.
- **Budget** : préférer quelques gros sprites animés à des centaines de petites particules ; mesurer en ms et en dessins/image (cathédrale : 3,47 → 0,32 ms ; 1 645 → 122 dessins/image).
- **Couleurs** : les effets sont plus saturés que le décor ; le décor reste désaturé pour que l'effet ressorte.
- **Vérifier au banc à distance de jeu**, pas en gros plan.

## Sources
- Stefan Jevremović, [VFX Staples: Shape, Color and Motion](https://80.lv/articles/vfx-staples-shape-color-and-motion/) (80.lv, 2018)
- VFX Apprentice, [10 Design Tips from the League of Legends VFX Style Guide](https://www.vfxapprentice.com/blog/10-league-of-legends-vfx-design-tips)
- Keith Guerrette, [Real-Time VFX overview](https://80.lv/articles/real-time-vfx-overview-from-keith-guerrette) (80.lv, 2018)
- Keith O'Conor, [GPU Performance for Game Artists](https://80.lv/articles/gpu-performance-for-game-artists) (80.lv, 2017)
- GDC Vault, [Visual Effects Bootcamp: Artistic Principles](https://gdcvault.com/play/1023943/Visual-Effects-Bootcamp-Artistic-Principles) ; communauté [realtimevfx.com](https://realtimevfx.com/t/artistic-principles-of-vfx/4081)
- Jonathan Cooper, [The 12 principles of animation in video games](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games) (extrait de *Game Anim*, 2019)
- Livre : Frank Thomas & Ollie Johnston, *The Illusion of Life: Disney Animation* (1981)
