# 10. Théorie de la couleur

**Le domaine** : pas un métier à part (c'est le travail du directeur artistique, du lighting artist et du coloriste), mais la base de toute ambiance. En jeu, la couleur dit l'humeur, guide l'œil et sépare ce qui compte du reste.

## Principes clés

- **L'humeur d'abord, la palette ensuite** : choisir l'émotion, puis en déduire les textures et la couleur des lumières. Exemple : marais inquiétant = teintes sombres, peu lumineuses, verts, avec un accent orange-brun pour une cabane (Valve, *Color Theory in Level Design*).
- **Harmonies** : analogues (voisines sur le cercle) = unité ; complémentaires (opposées) = contraste ; triadiques = accents. Changer une couleur change toutes les autres (Valve).
- **Une teinte domine, les autres sont des accents** : une triade fonctionne mieux avec une teinte dominante (Grasso) ; une teinte domine et sa complémentaire est réduite à de petits accents (guide VFX LoL).
- **Accent discordant** : une teinte qui détonne attire l'œil vers le moment clé (Grasso).
- **Tester ce qui attire réellement** : dans l'exemple Valve, une benne verte attirait les joueurs alors que la vraie porte de sortie, de couleur neutre, était ignorée.
- **Gamut limité** (James Gurney, *Color and Light*) : on choisit une zone restreinte du cercle chromatique pour toute l'image ; tout ce qui est hors de cette zone est exclu. Ça garantit l'harmonie et donne une « lumière » cohérente.
- **Perspective atmosphérique** (Gurney) : avec la distance, les contrastes baissent, les couleurs se désaturent et prennent la teinte de l'air (bleu de jour, couleur de la brume). Un objet lointain n'est jamais noir pur.
- **Ombres colorées** : les ombres gardent une teinte ; on remonte les noirs à ~95 % pour qu'ils gardent leur couleur (Gullion, *Bloodborne*).
- **Contraste de température** : désaturé et froid partout, saturation poussée seulement par les flammes et les braises (Gullion). Bleu pâle = hostile/froid (Citadelle de *Half-Life 2*), jaune chaud = refuge (Black Mesa East) (Valve).
- **Gris moyen + quelques accents** pour signaler les zones importantes (Jihoon Kim, 343 Industries, 80.lv).
- **Saturation = interactif** : dans *Assassin's Creed Valhalla*, les plantes ramassables sont plus saturées que les autres (Liu Xinyan, *6 elements of visual guidance*).

## Application GMod / EVO

- **Fiche palette** (dans la fiche DA) : 1 dominante, 1-2 neutres, 1 accent, en valeurs RVB des couleurs de props EVO et de la brume.
- **Méthode rapide** : régler d'abord la couleur de la brume (= l'air) ; teinter ensuite les props vers cette couleur (le décor « baigne » dedans) ; garder l'accent hors de cette famille, à 1-2 endroits seulement.
- **Exemples d'ambiances** : Hueco Mundo = sable pâle, ciel noir, os blanc, accent cyan ou vert spirituel ; Lac noir = noir bleuté, gris froid, accent unique (lueur, flamme) ; Enfer = brun-rouge, accent jaune-blanc.
- **Rien de noir pur au loin** : plus c'est loin, plus c'est clair et proche de la couleur de brume.
- **Test** : capture désaturée → la scène doit tenir en valeurs. Puis capture couleur → l'accent doit se trouver tout de suite.
- **Effets** plus saturés que le décor (voir ../../effets-scene-lua/references/06-vfx.md).

## Sources
- Valve Developer Community, [Color Theory in Level Design](https://developer.valvesoftware.com/wiki/Color_theory_(level_design))
- Adriano Grasso, [Lighting and visual composition](https://80.lv/articles/importance-of-lighting-and-visual-composition-in-a-video-game) (80.lv, 2022)
- James Gurney, [Gamut masking basics](https://gurneyjourney.blogspot.com/2022/05/color-wheel-masking-basics.html) (blog Gurney Journey) ; livre *Color and Light* (2010)
- Jason Gullion, [Recreating Nightmare Grand Cathedral](https://80.lv/articles/recreating-nightmare-grand-cathedral-from-bloodborne)
- Jihoon Kim, [Environment done right: geometry, space, light](https://80.lv/articles/environment-done-right-geometry-space-light/) (80.lv, 2017)
- Liu Xinyan, [6 elements of visual guidance](https://www.gamedeveloper.com/design/6-elements-of-visual-guidance) (2025)
- VFX Apprentice, [League of Legends VFX tips](https://www.vfxapprentice.com/blog/10-league-of-legends-vfx-design-tips)
