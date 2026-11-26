# 1. Composition / level design visuel

**Le métier** : en jeu, c'est le travail du *level designer* et de l'*environment artist*, hérité de la peinture et du cinéma. Il décide où l'œil va, dans quel ordre, et ce qu'il ressent. Différence avec un tableau : la caméra bouge. Une salle n'est donc pas UNE composition, mais **plusieurs petites compositions**, une par point de vue (Price, 2011).

## Principes clés

### 1. Trois plans + un sujet (Piaskiewicz, 2014)
- **Premier plan** : il cadre la vue, souvent en silhouette sombre (arche, rocher, pilier). Il donne l'échelle et la profondeur.
- **Centre d'intérêt (la « dominante »)** : l'élément le plus clair, le plus détaillé, le plus coloré, jamais caché. Il peut avoir un « contrepoint » plus discret.
- **Arrière-plan** : couleurs calmes, peu de détail, perspective atmosphérique (plus clair, moins saturé, teinté par la brume).
- **Staffage** : une silhouette (statue, personnage) à côté du sujet pour donner l'échelle et guider l'œil.

### 2. Hiérarchie des valeurs (clair/sombre)
- Le contraste le plus fort de l'image va sur le sujet, et nulle part ailleurs. Le poids visuel vient de la taille, du détail, du sombre, de la saturation et du contraste (Piaskiewicz).
- Test « yeux plissés » : réduis la capture en noir et blanc et en petit. Si le sujet ne saute pas aux yeux, aucune décoration ne le sauvera.
- *Framed Ink* (Mateu-Mestre) : on compose en **masses de valeur** (3 à 4 valeurs groupées), pas en objets.

### 3. Lignes et formes qui guident
- **Lignes directrices** : les horizontales calment et élargissent, les verticales donnent le monumental, les courbes adoucissent, les diagonales donnent de l'énergie (Piaskiewicz ; Orosz, 2020).
- Les diagonales qui penchent **vers** le joueur bloquent, celles qui partent **au loin** ouvrent et attirent (Orosz).
- Les lignes ne guident que s'il y a un vrai choix : dans un couloir unique, elles ne servent à rien (Unity, *Level design basics*).
- **Langage de formes** : formes stables et plates = calme ; verticales = puissance, mais menace si elles semblent pouvoir tomber ; pointes = danger, méfiance ; triangle inversé = instabilité (Orosz).

### 4. Équilibre et emplacement
- Dominante **symétrique** = architectural, sacré, synthétique. **Asymétrique**, avec une marge par rapport au bord = organique, vivant (Piaskiewicz).
- La symétrie se lit comme de la paix, l'asymétrie comme de la tension (Price).
- Règle des tiers / nombre d'or pour placer les éléments clés (Price). À utiliser comme point de départ, pas comme loi.
- **Économie** : si on retire un élément et que la composition tient encore, on le retire (Price).

### 5. Point de vue contrôlé
- On choisit l'angle de vue (bas, à hauteur, haut) et l'angle de composition (face, trois-quarts, profil ; le trois-quarts est le plus courant).
- On contrôle où le joueur se tient grâce aux **entonnoirs** (portes, couloirs, cols) : c'est là qu'on place la vue principale (Piaskiewicz).
- **Repère + récompense/refus** : on montre le but, on le cache, puis on le remontre plus près (Unity). Disney appelle ce repère un *weenie* (le château au bout de Main Street).
- Les joueurs regardent dans leur direction de marche et lèvent rarement les yeux, sauf si quelque chose les y pousse (Unity).
- Le mouvement attire l'œil : drapeaux, fumée, oiseaux renforcent la dominante (Piaskiewicz).

### 6. Grandes, moyennes, petites formes
- On construit et on juge d'abord les grandes masses, puis les formes moyennes, puis le détail. Le détail ne rattrape jamais une mauvaise silhouette.
- Proportion souvent citée en art : ~70 % de repos, ~20 % de détail moyen, ~10 % de détail fort, concentré au point focal. C'est une règle d'atelier, pas une mesure scientifique.

## Application GMod / EVO

- **Avant tout build** : désigner sur la maquette three.js le ou les **2-3 points de vue réels** (entrée, centre, moment fort). Chaque point de vue doit réussir le test « yeux plissés ». Le reste de la salle peut être plus pauvre.
- **Premier plan sombre** : un pilier, une arche, un rocher en bord de cadre, peints en noir (couleur du prop), coûtent 1 à 3 posés et ajoutent énormément de profondeur.
- **Le sujet reçoit le contraste** : la seule zone claire, la seule zone saturée (accent), et le détail. Les murs et le sol restent en valeurs moyennes, sans motif.
- **Fond = brume** : la brume du script (fog côté client) fait la perspective atmosphérique gratuitement. Ce qui est loin doit être plus clair et teinté par la brume, jamais noir pur.
- **Contre la boîte** : les props GMod sont carrés. Pour casser l'effet « immeuble/boîte » : incliner de quelques degrés, couper les angles, ajouter des ruptures (ruine, pignon, retrait), varier les hauteurs. Leçon de la cathédrale v10.
- **Échelle** : toujours un élément de taille humaine connue (porte, marche, statue de 72 u) près de la pièce géante. Sans repère, le géant paraît petit.
- **Contrôle** : capture de chaque point de vue → passage en noir et blanc → réduction → on doit trouver le sujet en moins de 2 secondes.

## Sources
- Mateusz Piaskiewicz, [Composition in Level Design](https://www.gamedeveloper.com/design/composition-in-level-design) (Game Developer, 2014)
- Jeremy Price, [Applying the Elements and Principles of Design in Level Art](https://www.gamedeveloper.com/art/applying-the-elements-of-design-and-principles-of-design-in-level-art) (2011)
- David Orosz, [Shaping Emotions: Shape Language and Symbols in Level Design](https://www.gamedeveloper.com/design/shaping-emotions-utilizing-shape-language-and-symbols-in-level-design) (2020)
- Unity, [Level design basics: guiding players without telling them](https://unity.com/blog/level-design-basics)
- David Shaver (Naughty Dog), [Invisible Intuition, GDC (director's cut)](http://davidshaver.net/DShaver_Invisible_Intuition_DirectorsCut.pdf)
- Ken Hartley, [Disney Tip #83: Forced Perspective](https://medium.com/@kenhartley/disney-tip-83-forced-perspective-disney-magic-e02bada72209)
- Livre : Marcos Mateu-Mestre, *Framed Ink* (Design Studio Press, 2010)
