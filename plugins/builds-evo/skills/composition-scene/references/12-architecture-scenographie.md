# 12. Architecture et scénographie de théâtre

**Les métiers** : l'**architecte** pense l'échelle, la lumière naturelle et le parcours dans un espace réel ; le **scénographe** de théâtre crée des lieux crédibles et forts avec très peu de moyens, et les transforme par la lumière. Ce sont nos deux meilleurs modèles : nous aussi devons faire **grand avec peu** (400 posés).

## Ce que le théâtre nous apprend

- **Volumes réels plutôt que perspective peinte** : Adolphe Appia (1862-1928) remplace les toiles peintes par des praticables en 3D (marches, plans inclinés) où l'acteur se déplace dans tout l'espace (UBC).
- **Quatre éléments de scène** : le décor vertical, l'organisation du sol, l'acteur, et la lumière (Appia).
- **La lumière construit** : lumière diffuse pour montrer, lumière concentrée pour modeler les formes. Appia supprime la rampe, qui aplatit l'image (UBC).
- **La lumière transforme le lieu** : dans le *Rheingold* de Bâle (1924), le Walhalla apparaît et disparaît par la lumière seule (Appia).
- **Le symbole plutôt que le littéral** : des arbres stylisés dans *Parsifal* créent mieux l'ambiance qu'une forêt réaliste (Appia).
- **Un seul espace, plusieurs humeurs** : Edward Gordon Craig (*Towards a New Theatre*, 1913) montre le même décor sous quatre lumières différentes ; pour lui la lumière est l'élément le plus « plastique » de la scène (UBC).

## Ce que l'architecture nous apprend

- **Le sublime** (Edmund Burke, 1757, repris par Boullée) : immensité, masse, sentiment d'infini, contraste lumière/ombre, répétition (Public Domain Review, *Designing the Sublime*).
- **Formes élémentaires** : Boullée et Ledoux construisent avec la sphère, le cube, la pyramide, qu'ils combinent « comme des notes d'une gamme ». Le cénotaphe de Newton (1784) : une sphère creuse percée de trous qui donnent, de jour, un ciel étoilé à l'intérieur.
- **« L'architecture des ombres »** (Boullée) : sur des formes nues, le contraste ombre/lumière fait le travail de l'ornement.
- **Variété dans la règle** : Ledoux dessine 55 barrières d'octroi toutes différentes à partir d'un vocabulaire restreint (fenêtres, colonnes doriques, bossages ; plans carré, cercle, croix). Il jugeait un modèle unique répété « ennuyeux ».
- **Architecture parlante** : le bâtiment exprime sa fonction par sa forme.
- **Perspective forcée** (Disney) : chaque étage plus petit que celui du dessous ; Main Street à ~2 étages se lit comme 3 ; le château paraît plus grand qu'il n'est (Ken Hartley).
- **Compression puis libération** : passer par un espace bas et étroit avant un grand volume rend le grand volume énorme. Principe classique (Frank Lloyd Wright) appliqué partout en level design.

## Application GMod / EVO

- **Grand avec peu** : quelques formes élémentaires énormes (plaques, cylindres, cônes EVO) + un fort contraste ombre/lumière valent mieux que beaucoup de petits détails. C'est « l'architecture des ombres ».
- **Vocabulaire restreint, combinaisons variées** (Ledoux) : choisir 5 à 8 props pour tout un build et les combiner (tourner, empiler, couper). Cohérence et moins de matériaux différents (= moins de draw calls).
- **Compression → libération** : un passage bas et sombre avant la salle principale. Coût : 5 à 10 posés, effet énorme.
- **Perspective forcée** : éléments de plus en plus petits vers le fond ou le haut (étages, colonnes, cathédrales lointaines du ciel 3D) pour paraître plus grand.
- **Le symbole plutôt que le littéral** : 3 arbres morts stylisés plutôt qu'une forêt ; un portique plutôt qu'un temple entier.
- **La lumière change le lieu** : prévoir dans le script 2 à 4 « humeurs » d'un même décor (brume + lumière + son) pour les différentes séquences. Le décor ne bouge pas, la scène change.

## Sources
- UBC, [Adolphe Appia & Gordon Craig](https://faculty.arts.ubc.ca/rfedoruk/craig/appia.htm) et [Edward Gordon Craig](https://faculty.arts.ubc.ca/rfedoruk/craig/craig.htm)
- Encyclopædia Britannica, [The influence of Appia and Craig](https://www.britannica.com/art/theater-building/The-influence-of-Appia-and-Craig)
- Hugh Aldersey-Williams, [Designing the Sublime: Boullée and Ledoux's Architectural Revolution](https://publicdomainreview.org/essay/designing-the-sublime) (Public Domain Review, 2025)
- ArchDaily, [AD Classics: Cenotaph for Newton](https://www.archdaily.com/544946/ad-classics-cenotaph-for-newton-etienne-louis-boullee)
- Ken Hartley, [Disney Tip #83: Forced Perspective](https://medium.com/@kenhartley/disney-tip-83-forced-perspective-disney-magic-e02bada72209)
- Livres : Francis D. K. Ching, *Architecture: Form, Space, and Order* ; Christopher W. Totten, *An Architectural Approach to Level Design* (2e éd., 2019)
