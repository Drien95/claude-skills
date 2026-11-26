# Performance (viser un serveur à ~30 joueurs)

« Les joueurs vont cramer sinon » (Adrien, 25/11) : chaque effet est mesuré avant/après.

- Mesurer en image moyenne, 1 % pire et pic, plus la mémoire créée par effet (un pic avec chute de 15 Mo = ramasse-miettes).
- Repère : Lac noir final 17,8 ms par image, 1 % pire 38 ms ; rideau et brouillards ≈ 0,05 ms ; cathédrale v9 : Lua 3,47 → 0,32 ms, 1 645 → 122 dessins/image.
- Étaler les apparitions (pas tout au même boum), plafonds de particules, LOD par distance et champ de vision, miroir basse résolution, ≤ 2 DynamicLight, convar de qualité côté joueur.
- Cache au repérage, jamais de recherche d'entités à chaque image.
- **Tout dessin et tout parcours d'entités côté client derrière le test de boîte** (A2, 26/11/2026, audit : sable + dunes = ~160 000 triangles dessinés par tous les joueurs de la map dès qu'un build existait, et `ents.FindByClass("prop_physics")` sur la map entière chaque seconde chez chacun). Le premier test d'un hook de dessin est « caméra dans la boîte (ou à une marge près pour le décor lointain) », calculé une fois par image ; un parcours d'entités passe par `ents.FindInBox` de la boîte, avec une liste gardée et refaite seulement quand une entité est créée. Clé de cache = identité du repère, jamais une chaîne recréée à chaque image.
- **Recherche serveur = revalider d'abord** (A2, 26/11/2026) : tant que l'ancre est valide, la revalider (IsValid + quelques sondes) ; recherche complète seulement si elle est perdue ou si un prop d'un modèle du repère est créé (`OnEntityCreated` filtré sur `prop_physics`, modèle lu au `timer.Simple(0)`, anti-rebond).
- Pas d'allocation par image dans les boucles de sprites : une couleur réutilisée (`Color` modifiée, plafonnée à 255 comme `Color()`), tables constantes (filtre `DrawColorModify`).
- Moins de grosses particules valent mieux que beaucoup de petites transparentes (overdraw).
- Maillages construits une fois, animés par matrice.
- Lots de maillage ≤ 4 000 quads (limite 32 768 indices).
- Fiche détaillée : `09-technical-art.md`.
