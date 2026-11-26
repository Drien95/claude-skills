# 3. Éclairage (lighting artist)

**Le métier** : le lighting artist pose les lumières pour **montrer ce qui compte, cacher le reste, et fixer l'émotion**. En jeu, il guide aussi le joueur (sorties, chemin) et sépare les silhouettes du fond. C'est souvent ce qui transforme un bon blockout en belle scène.

## Principes clés

- **Une seule lumière maîtresse d'abord** : trouver une image de référence avec la couleur et l'ambiance voulues, et essayer de l'atteindre avec UNE lumière. Toutes les autres la servent. Si la scène devient « boueuse », tout effacer et repartir de la lumière clé (Gabe Betancourt, Naughty Dog, *The Last of Us*).
- **Peu de lumières** : un bon éclairage utilise une poignée de sources ; trop de lumières = directions confuses (Betancourt).
- **Ordre de travail** : lumière globale et ambiance (lune/soleil, ambiante) d'abord, puis le détail (Robert Yang & David Shaver, GDC 2018) ; directionnelle, puis ciel, puis lumières d'appoint (Dave Miragliotta, 80.lv).
- **Éclairer la progression** : les sorties et le chemin principal sont éclairés ; on classe les entrées par importance et on les éclaire différemment (Yang & Shaver ; Unity).
- **Contre-jour et fond pour les silhouettes** : pour un ennemi ou un moment fort, on éclaire derrière (rim/back light) pour que la silhouette se détache (Yang & Shaver).
- **Langage cohérent** : même type de chose = même type de lumière, partout (Yang & Shaver).
- **Lumière motivée** : chaque lumière a une source crédible dans le monde (Grasso). Le théoricien de théâtre Adolphe Appia est crédité de cette idée (une torche éclaire l'acte II de *Tristan*).
- **Les ombres gardent de la couleur** : remonter les ombres les plus noires à ~95 % de noir pour qu'elles gardent une teinte (Jason Gullion, recréation de la Grand Cathedral de *Bloodborne*).
- **Pas de saturation accidentelle** : une lampe « jaune » est presque blanche avec une teinte jaune (Valve, *Color Theory*).
- **Froid / chaud** : bleu pâle pour le froid et l'hostile (la Citadelle Combine de *Half-Life 2*), jaune chaud pour le refuge (Black Mesa East) (Valve).
- **Haute clé / basse clé** : « low key » = fort contraste et ombres profondes (horreur, drame) ; « high key » = faible contraste, pas forcément lumineux (OSU, *Mise en scène*).
- **Peindre la lumière, pas les objets** (Hartel) ; **tricher sur l'emplacement, pas sur la physique** (Hartel).

## Application GMod / EVO

Contraintes : l'éclairage de jour de la flatgrass reste sur les props ; gmod_light/lamp et les lumières du catalogue comptent dans les 400 posés ; le script peut ajouter des lumières dynamiques côté client (hors limite) mais elles coûtent en performance et Source en affiche un nombre limité à la fois.

- **La nuit se fabrique** : brume sombre teintée (fog du script) + couleur des props un ton plus sombre que voulu. La lumière se « peint » ensuite par des zones claires.
- **Lumière clé = 1 source script** bien placée (dynamique ou texture projetée), qui éclaire le sujet. On juge la scène avec elle seule avant d'ajouter quoi que ce soit.
- **Faux éclairage par la matière** : un prop clair ou émissif (sprite, matériau lumineux, debugwhite teinté) se lit comme « éclairé » sans vraie lumière. C'est la technique la moins chère et la plus fiable sur EVO.
- **Halo/sprite derrière le sujet** = contre-jour gratuit pour détacher une silhouette (entrée de Kuga, statue, trône).
- **Brume = lumière ambiante** : la couleur de la brume fixe l'humeur générale (bleu-vert froid pour Hueco/Lac noir, rouge pour l'Enfer).
- **Accent chaud dans un monde froid** : une flamme, une braise, un vitrail : la seule source chaude attire l'œil. Une seule zone.
- **Chemin éclairé** : la sortie ou la suite de la séquence est toujours la zone la plus claire vue depuis l'entrée.
- **Contrôle** : capture avec la seule lumière clé, puis avec tout. Si la deuxième n'est pas nettement meilleure, on supprime des lumières.

## Sources
- Alex Wawro, [Last of Us lighting artist: set the mood with a single light](https://www.gamedeveloper.com/art/-i-last-of-us-i-lighting-artist-offers-devs-a-tip-set-the-mood-with-a-single-light) (2017, citant Gabe Betancourt)
- Robert Yang, [GDC 2018: How To Light A Level (slides et transcription)](https://www.blog.radiator.debacle.us/2018/03/gdc-2018-how-to-light-level-slides-and.html), avec David Shaver
- Valve Developer Community, [Color Theory in Level Design](https://developer.valvesoftware.com/wiki/Color_theory_(level_design))
- Dave Miragliotta, [Planning: the key to environment design](https://80.lv/articles/planning-the-key-to-environment-design) (80.lv, 2017)
- Jason Gullion, [Recreating Nightmare Grand Cathedral from Bloodborne](https://80.lv/articles/recreating-nightmare-grand-cathedral-from-bloodborne) (80.lv, 2018)
- Drew Hartel, [15 tips for better lighting keys](https://www.creativebloq.com/advice/lighting-keys)
- Oklahoma State University, [Mise en scène (Intro to Film & TV)](https://open.library.okstate.edu/introfilmtv/part/mise-en-scene/)
- [Adolphe Appia & Gordon Craig](https://faculty.arts.ubc.ca/rfedoruk/craig/appia.htm) (UBC)
- Livre : James Gurney, *Color and Light* (2010)
