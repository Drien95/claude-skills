# Pièges Lua 5.1 / GMod (vus en build)

| Piège | Règle |
|---|---|
| Limite de 200 locales par fonction (Lua 5.1) | nouvelles variables dans une table (`SC`, `Q`), modules dans des fonctions à part |
| Locale lue avant sa déclaration = globale nil (yeux d'Azeno V7, `construireRides` du sable A2) | déclarer les fonctions locales avant usage (`local nom` en tête, puis `nom = function`) ; le hook garde_lua le signale après chaque écriture si LuaJIT est là (GGET d'un nom déclaré `local`) |
| Une erreur dans un hook de dessin le relance à chaque image | `pcall` autour du dessin : à la première erreur, un seul message et le hook s'arrête |
| Nom masqué dans un module (`local SB, SC = 16, 64`) | ne pas réutiliser un nom de table partagée |
| « ambiguous syntax » | ligne qui commence par `(` après `end)` : mettre `;` devant |
| Deux scripts, même nom de hook | ils s'écrasent : noms distincts, préfixés par la scène |
| Autorefresh | un fichier déjà chargé se recharge seul ; un nouveau fichier autorun ne se charge pas à chaud (`include` depuis un fichier chargé, ou canal film du banc) ; les hooks de l'ancienne version restent (`hook.Remove`) |
| Gel des animations pendant une pause | deux horloges : temps de la scène (s'arrête) et temps des animations (continue) |
| Rejouer une séquence | remettre à zéro l'état joué (sons) sauf si on enchaîne la suivante |
| Sons coupés net | boucles en `CreateSound` + `FadeOut`, jamais `stopsound` au milieu |
| « too many indices for index buffer (32784>32768) » | un lot `mesh.Begin` / `render.StartBeam` ≤ 32 768 indices : lots de 4 000 quads max, compteur garde-fou |
| Id de DynamicLight déjà pris | il éteint l'autre lumière : réserver une plage d'id par pièce |
| `PreDrawSkyBox` qui renvoie true | supprime aussi `PostDraw2DSkyBox` : effacer le ciel dans `PostDraw2DSkyBox` |
| CullMode laissé en CCW | les effets à une face disparaissent : `MATERIAL_CULLMODE_NONE` le temps des effets, puis remettre |
| `render.Capture` rend nil sans focus | rendu dans une cible hors écran depuis Think |
| Lignes lumineuses qui ne se « rallument » pas | les dessiner en couleur pleine, sans l'éclairage de la map |
| Œil inactif encore visible | matériau noir mat quand il est éteint |
| Joueur noir dans la scène de nuit | normal : pas de lumière sur lui |
| Fondu coloré de 5 s qui couvre tout l'écran | flash court pour une couleur d'ambiance ; fondu seulement pour les fins et coupures |
| Script multijoueur / DarkRP | séparation `sv_` / `cl_` / `sh_config.lua` (renvoie sa table, pas de global), messages net ; le banc solo ne prouve pas le DarkRP |
| Rien dans le chat | messages seulement dans la console de celui qui a tapé la commande |
| Couches superposées d'un même maillage (base, détail, voile) à 0,08 u : fragments anguleux vus de haut (z-fighting, A2 26/11) | écart ≥ 0,3 u entre couches + `$decal 1` sur les couches du dessus ; changer le nom du matériau (`CreateMaterial` garde les anciens paramètres) ; diagnostic : le motif reste identique quelle que soit la texture |
| Autorefresh muet quand le jeu tourne en fond | ne pas s'y fier : bascule de map (tâche `bascule`) et une trace `print("[x] chargé vN")` en fin de script, vérifiée dans la console avant la planche |
| Sprites aplatis (hauteur < largeur) vus d'en haut : rangée de « dents » (A2, 26/11) | sprites ronds ou presque (rapport ≥ 0,8) dès qu'une vue plongeante est prévue |
| Pierres de résultat qui glissent derrière leur support : invisibles depuis la place (A2, 26/11) | animer vers le regard du joueur concerné |
