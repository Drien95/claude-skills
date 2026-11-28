# Recettes d'effets (script client, Lac noir et Azeno)

| Effet | Technique |
|---|---|
| Veines / fissures (effet signature) | marche au hasard tirée vers une cible, ramifiée (fourches, brins), qui suit les joints ; couche floue au fond + cœur net ; tête de braise qui court (650 u/s) ; largeur qui décroît avec la distance |
| Fissures du ciel (Sumii, 27/11/2026) : des rubans blancs à longs segments ont été jugés « grossiers, pas beaux » | repartir de la recette veines ci-dessus : points tous les ~1,3 degré, fourches puis brins, affinées vers la pointe ; 4 couches (halo fondu, bord sombre, braise carmin, cœur orangé) et tête de braise |
| Fissures sur un .mdl | chaque point posé par rayon contre les triangles (`util.GetModelMeshes`, rangés par tranche de hauteur) |
| Allumage par onde | arrivée = boum + distance au centre / 900 u/s, fondu 0,5 s, flash à l'arrivée ; rien ne s'allume avant le boum |
| Onde de choc | 3 vagues amorties, anneaux irréguliers d'épaisseur variable, mur d'eau + crête d'écume, gerbes de gouttes, anneau d'air (sprites/heatwave), brume chassée qui revient |
| Tornade de feu (J3, 8,5/10) | langues de feu 2 couches + brasier + colonne de chaleur + fumée rouge en haut, matériaux du jeu de base, ~650 particules ; flammes à ≥ 120 u de la lame, côté spectateur à 5 % d'opacité (suit chaque joueur), grandit 2 s puis tourne |
| Fil de braise (fente du trône) | quad plein + halo doux, continu sur toute la fente (pas de textures en tirets) |
| Flamme bleue | 7 langues en faisceaux, texture continue d'un segment à l'autre, bleu profond, aura réduite (fire_cloud1 teinté = rose et blanc) |
| Miroir du lac | stencil sur l'eau visible + copies `ClientsideModel` à l'envers (matrice z négative, CullMode CW) ; Fresnel plafonné à 0,62 ; ciel renvoyé assombri ; basse résolution |
| Brume | grosses particules très transparentes, nombreuses ; nappe basse z +3 à +12 ; bancs en sprites ; plans verticaux seulement vus de face ; brouillard par `SetupWorldFog` / `SetupSkyboxFog` |
| Cacher la map | rideau opaque autour de la boîte (sans écrire la profondeur), sol sombre jusqu'à 60 000 u, mur de brume noire en anneau ; stencil pour redessiner les lointains ; `ClearBuffersObeyStencil` remet la profondeur au loin |
| Ciel 3D (gigantisme) | géométrie à taille réelle dessinée en miniature 1/16 dans la boîte avec une caméra mise à l'échelle ; silhouettes à 1/64 ; même brume que le monde au raccord ; dessiné seulement pour les joueurs dans la boîte |
| Éclipse et lune | disque dessiné après le colormod, à 14 000 u derrière la cathédrale ; mers, cratères à rebord clair, bord assombri, ombre douce |
| Cascade de sang | 10 filets en arc, `effects/bloodstream` qui défile, voile, halo, flaque, anneaux, têtes brillantes |
| Cendres et braises | maillages fixes construits une fois, mis en mouvement par une matrice (pas de particule par image) |
| Battement | lub-dub toutes les 1,6 s, calé sur le son ; il fait respirer veines et fente |
| Sons | `CreateSound` en boucle, `FadeOut` à l'extinction ; cloche synthétisée (partiels d'église) ; fond + ponctuels aléatoires + séquence |
| Lumières | `DynamicLight` en file par priorité selon une convar de qualité, ≤ 2 actives, plage d'id réservée par pièce |
| Masques EVO hors liste blanche | `ClientsideModel` côté joueur (0 posé) |
| Vague de poussière (A2, 26/11) | anneau de sprites ronds (hauteur = 0,8 × largeur) plus clairs que le sable (+50), front net et traîne tirée vers l'intérieur ; rides derrière = anneaux de quads ondulés (3 sinus sur le rayon, largeur et opacité variables) : réguliers, ils font une « cible » ; quads à une face : `CullMode NONE` sinon invisibles d'en haut |
| Point focal de nuit sans éclairer la map (A2, 26/11) | pénombre peinte : maillage en anneau couleur brouillard posé sur le sable, alpha 0 au bord du cercle de lumière puis ~200 ; la dalle et les pierres restent les seules zones claires |
| Objet « tenu » par un joueur (A2, 26/11) | impossible sur EVO (pas de grab) : l'objet est lié à la place (relatif au prop de tête) et la tenue reste narrative (/me) |
