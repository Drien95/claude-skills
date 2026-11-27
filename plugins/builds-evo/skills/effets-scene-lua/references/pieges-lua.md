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
| Prop du dupe « caché » côté client qui reste visible (A2 v13, 26/11/2026 : anneau propre autour du socle, trace « 1 redevenus visibles ») | `SetNoDraw` client sur une entité réseau est remis à zéro par le serveur : `RenderOverride` vide + `SetNoDraw` réappliqués chaque seconde ; vérifier le masquage par une trace console (trouvés, cachés, redevenus visibles) avant de juger une planche |
| Bord net et clair autour d'un objet posé sur le sable (A2 v13, 26/11/2026) | un quad plat ou un décal translucide ne prend ni la teinte ni la pénombre du sable et dessine un cercle propre : faire monter le vrai sable (hook de hauteur lu par le script du sol) |
| Pic de sable géant à un endroit précis (A2 v13, 26/11/2026) | `ents.FindByModel` rend aussi les `ClientsideModel` (qui s'accumulent à chaque rechargement à chaud) : pour les props du dupe, `ents.FindByClass("prop_physics")` puis filtrer le modèle ; un effet par objet trouvé se cumule au même point |
| Image sombre en sortant du build (A2 v13, 26/11/2026, vu par Adrien en jeu) | un `RenderScreenspaceEffects` (étalonnage de nuit) sans test de boîte s'applique partout : tout hook d'ambiance (écran, brouillard, ciel, lumière, son) commence par le test caméra dans la boîte relative au prop repère ; vérifier par une capture hors boîte (~3 000 u). Idem pour le rééclairage de nuit des props (`RenderOverride`) : seulement les props de la boîte, dessin normal dès que l'œil en sort |
| Rien dans le chat | messages seulement dans la console de celui qui a tapé la commande |
| Couches superposées d'un même maillage (base, détail, voile) à 0,08 u : fragments anguleux vus de haut (z-fighting, A2 26/11) | écart ≥ 0,3 u entre couches + `$decal 1` sur les couches du dessus ; changer le nom du matériau (`CreateMaterial` garde les anciens paramètres) ; diagnostic : le motif reste identique quelle que soit la texture |
| Autorefresh muet quand le jeu tourne en fond | ne pas s'y fier : bascule de map (tâche `bascule`) et une trace `print("[x] chargé vN")` en fin de script, vérifiée dans la console avant la planche |
| Sprites aplatis (hauteur < largeur) vus d'en haut : rangée de « dents » (A2, 26/11) | sprites ronds ou presque (rapport ≥ 0,8) dès qu'une vue plongeante est prévue |
| Pierres de résultat qui glissent derrière leur support : invisibles depuis la place (A2, 26/11) | animer vers le regard du joueur concerné |
| Scène livrée qui ne s'affiche pas sur EVO alors que le serveur avance (Lac noir, 26/11/2026) ; ancre ambiguë (A2 v14 : 9 plate5x5 de même teinte, choix par x+y faux si le build est tourné) | ancre reconnue par un **motif de props** du dupe (2 ou 3 modèles à leur position relative, dans le repère du candidat, tolérance ~6 u), jamais par « le seul prop de ce modèle » ni par la couleur ; même règle serveur et client ; commande MJ pour la désigner et commande `diag` côté joueur. Tester au banc avec des props parasites et le build tourné. Mieux (A2 v15, 26/11/2026) : **gravure d'usine**, 3 petits props dédiés invisibles et traversables à écarts, lacets et couleurs tirés de l'ID de la scène (`outils/gravure.py`, `gravure_lua/sh_gravure.lua`), 2 sur 3 suffisent, motif en secours |
| `attempt to call field 'x' (a nil value)` après copie à chaud d'un nouveau fichier partagé (A2, 26/11/2026) | l'autorefresh recharge les anciens fichiers dans l'ancien état Lua, le nouveau fichier n'est chargé qu'au changement de carte : appel protégé (`T.x and T.x()`) et bascule de carte avant de juger |
| Cubes roses en damier dans le ciel (Sumii P1 v18, 27/11/2026) : `CreateMaterial` sur `particle/smokesprites_0002` et `_0003`, textures venues d'un addon absent de l'éclair | lire le `$basetexture` réel dans le VMT (`smokesprites0001` sans tiret bas) et vérifier que la texture existe dans le jeu de base ou le contenu éclair ; regarder la 1re planche avant toute critique |
| Correction d'un `CreateMaterial` sans effet au rechargement (Sumii P1 v18, 27/11/2026) | le matériau reste en cache sous son nom : changer le nom (`_v2`, `_v3`) à chaque changement de paramètres |
| Nuages roses côté opposé au soleil, teinte différente d'une version à l'autre (Sumii P1 v14 à v18, 27/11/2026) | tout ce qui dérive avec le temps (`az + t * vitesse`) calcule sa teinte au dessin, pas à la construction |
| Modèles client (`ClientsideModel`) d'une version précédente encore à l'écran (Sumii P1 v16, 27/11/2026) | ils survivent au rechargement à chaud : au chargement, retirer ceux du script (`EntIndex() == -1` + modèle) |
| Cimes plus sombres avec `$color "[3.5 3.5 3.5]"` sur `UnlitGeneric` (Sumii P1 v17, 27/11/2026, hypothèse) | ne pas compter sur `$color` > 1 pour éclaircir : couleur de sommet = cible / couleur moyenne de la texture, plafonnée à 255 |
| Notes jaunes, orangées, roses invisibles sur des cartes de feuilles vertes teintées par `$color` (Sumii P1 v20 à v22, 27/11/2026) | `$color` multiplie la texture : sur du vert, l'orange donne de l'olive. Recolorer une texture neutre (`particle/leaf/leaf_nocolor`, addon #10). Une tige « noire » qui reste malgré le script peut être peinte dans la texture : regarder la texture (planche-contact `srctools.vtf`) et recadrer les UV |
