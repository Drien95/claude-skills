# Performance (viser un serveur à ~30 joueurs)

« Les joueurs vont cramer sinon » (Adrien, 25/11) : chaque effet est mesuré avant/après.

- Mesurer en image moyenne, 1 % pire et pic, plus la mémoire créée par effet (un pic avec chute de 15 Mo = ramasse-miettes).
- Repère : Lac noir final 17,8 ms par image, 1 % pire 38 ms ; rideau et brouillards ≈ 0,05 ms ; cathédrale v9 : Lua 3,47 → 0,32 ms, 1 645 → 122 dessins/image.
- Étaler les apparitions (pas tout au même boum), plafonds de particules, LOD par distance et champ de vision, miroir basse résolution, ≤ 2 DynamicLight, convar de qualité côté joueur.
- Cache au repérage, jamais de recherche d'entités à chaque image.
- Moins de grosses particules valent mieux que beaucoup de petites transparentes (overdraw).
- Maillages construits une fois, animés par matrice.
- Lots de maillage ≤ 4 000 quads (limite 32 768 indices).
- Fiche détaillée : `09-technical-art.md`.
