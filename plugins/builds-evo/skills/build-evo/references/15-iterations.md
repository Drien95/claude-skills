# 15. Ne plus faire 90 versions d'une pièce

**Le problème** : le trône et l'épée ont demandé des dizaines de versions (jusqu'à ~90). Chaque version corrigeait la précédente, une retouche à la fois. La recherche et les studios disent que **ce n'est pas le nombre d'essais qui compte, mais leur forme**.

## Ce que disent les études

- **Prototypes en parallèle > prototypes en série** (Steven Dow et al., Stanford, *ACM TOCHI* 2010). 33 designers, même temps, même nombre de prototypes, mêmes retours. Groupe « parallèle » : 3 versions, critique sur les 3 ensemble, puis 2 de plus. Groupe « série » : critique après chaque version. Résultats pour le groupe parallèle : notes d'experts 24,4 contre 21,7 ; 445 contre 398 clics par million d'affichages ; essais plus variés ; confiance en hausse ; et **aucun** participant mal à l'aise face aux critiques, contre près de la moitié en série.
- **Itérer au moins une fois vaut mieux qu'une seule passe, même pressé** (Dow, Heddleston & Klemmer, 2009) ; les débutants qui itèrent font aussi bien que les expérimentés qui n'itèrent pas.
- **Des contraintes claires aident la créativité** (Elaine Zhou, Stanford, 2015) : fixer les limites (public, format) oriente l'idéation ; des contraintes arrivées tard ont même donné des résultats plus originaux.
- **Les premières versions sont mauvaises, c'est normal** : le travail est de les faire passer « de nul à pas nul » ; le Braintrust de Pixar se réunit régulièrement avec une seule règle, la franchise (Ed Catmull, *Creativity, Inc.*).
- **« On perd plus par l'indécision que par une mauvaise décision »** (Ricky Baba, 2014).
- **Préparer le rythme avant de construire évite le travail jeté** (Mike Lopez, 2008).
- **Silhouette d'abord** : « la silhouette est une des choses les plus importantes » ; on commence par les grandes formes (Brie Gibson, 80.lv) ; on fixe les poses clés avant le détail (« pose à pose », *Game Anim*).
- **Gros plan sur les retours** : la méthode de critique de Feldman (décrire, analyser, interpréter, juger) donne des retours précis plutôt que « c'est pas ça ». Voir 21-critique-charge-cognitive.md.

## La méthode pour une pièce (trône, épée, statue…)

**Étape 0 : la fiche de pièce (10 min, validée par Adrien AVANT de construire)**
- Rôle dans la scène (héros ou décor ?), **budget de posés** (ex. épée ≤ 50), taille en unités.
- 3 mots-images + 1 image de référence maîtresse + 5-10 références.
- **Les 3 vues de jugement** (ex. depuis l'entrée, de trois-quarts à 3 m, en contre-plongée). On ne juge QUE sur ces vues.
- **Critères d'acceptation** : « c'est fini quand » (ex. silhouette reconnaissable à 20 m, garde lisible, ≤ 50 posés, note ≥ 7,5).

**Étape 1 : 3 silhouettes en parallèle (en gris, sans détail)**
- 3 pistes **vraiment différentes** (pas 3 variantes de la même), en maquette three.js ou au banc, en gris uniforme.
- Planche côte à côte, mêmes 3 vues, fond neutre. Adrien choisit une piste (ou en combine deux). **Une seule décision par planche.**

**Étape 2 : formes moyennes**
- Sur la piste choisie, 2 variantes des formes moyennes, côte à côte. Choix.
- **Règle : on ne revient plus aux grandes formes**, sauf erreur bloquante.

**Étape 3 : détail + matière**
- Détail concentré sur 1-2 zones focales (voir ../../pieces-props/references/16-allegement.md). Couleurs de props, lumière.

**Étape 4 : passe d'allègement + contrôle**
- Comparaison complet / allégé, vue par vue. Mesures. Note.

**Règles qui coupent les boucles**
- **Nombre de passes fixé d'avance** : 3 planches de décision + 1 passe de finition. Au-delà, on s'arrête pour revoir la fiche, pas la pièce.
- **Arrêt à 7,5** : quand la pièce atteint la note seuil sur les 3 vues, on passe à la suite. Le mieux se fait plus tard, dans la scène complète.
- **Toujours juger dans la scène**, avec la lumière et la brume finales, pas seul sur fond blanc.
- **Changement de goût = nouvelle piste**, pas une retouche : si Adrien dit « ce n'est pas ça », on revient à l'étape 1 avec 3 nouvelles silhouettes, au lieu de retoucher 20 fois.
- **Kill your darlings** : si une partie qu'on aime casse la silhouette ou le budget, elle sort.
- **Bibliothèque** : chaque pièce validée (garde, lame, accoudoir, pilier) va dans une bibliothèque de modules réutilisables (kitbash) avec son nombre de posés. La pièce suivante démarre de là.

## Sources
- Dow, Glassco, Kass, Schwarz, Schwartz & Klemmer, [Parallel Prototyping Leads to Better Design Results, More Divergence, and Increased Self-Efficacy](https://hci.stanford.edu/publications/2010/parallel-prototyping/ParallelPrototyping2010-submitted.pdf) (ACM TOCHI, 2010)
- Dow, Heddleston & Klemmer, [The Efficacy of Prototyping Under Time Constraints](https://hci.stanford.edu/publications/paper.php?id=59) (Creativity & Cognition, 2009)
- Elaine Zhou, [Bounding Creativity: Explicit and Implicit Constraints in the Design Process](https://purl.stanford.edu/tf829zy3088) (Stanford, 2015)
- Ed Catmull, [Inside the Pixar Braintrust](https://www.fastcompany.com/3027135/inside-the-pixar-braintrust) (Fast Company, 2014)
- Ricky Baba, [Art direction in video games](https://www.gamedeveloper.com/art/art-direction-in-video-games-a-roadmap-for-finishing-your-projects)
- Brie Gibson, [Crafting grand, well-balanced environments](https://80.lv/articles/001agt-crafting-grand-well-balanced-environments)
- Jonathan Cooper, [The 12 principles of animation in video games](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)
- Alitt Khaliq, [Rapid conceptual design with kitbashing](https://unity.com/blog/games/realizing-rapid-conceptual-design-with-kitbashing) (Unity, 2020)
