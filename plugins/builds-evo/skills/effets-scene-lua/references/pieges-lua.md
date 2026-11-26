# Pièges Lua 5.1 / GMod (vus en build)

| Piège | Règle |
|---|---|
| Limite de 200 locales par fonction (Lua 5.1) | nouvelles variables dans une table (`SC`, `Q`), modules dans des fonctions à part |
| Locale lue avant sa déclaration = globale nil (yeux d'Azeno V7) | déclarer les fonctions locales avant usage ; `luajit -bl` et chercher les GGET après chaque passe |
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
| Prop du dupe « caché » côté client qui reste visible (A2 v13, 26/11/2026 : anneau propre autour du socle, trace « 1 redevenus visibles ») | `SetNoDraw` client sur une entité réseau est remis à zéro par le serveur : `RenderOverride` vide + `SetNoDraw` réappliqués chaque seconde ; vérifier le masquage par une trace console (trouvés, cachés, redevenus visibles) avant de juger une planche |
| Bord net et clair autour d'un objet posé sur le sable (A2 v13, 26/11/2026) | un quad plat ou un décal translucide ne prend ni la teinte ni la pénombre du sable et dessine un cercle propre : faire monter le vrai sable (hook de hauteur lu par le script du sol) |
| Rien dans le chat | messages seulement dans la console de celui qui a tapé la commande |
