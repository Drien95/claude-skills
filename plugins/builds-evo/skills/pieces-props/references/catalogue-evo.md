# Props EVO : où chercher, quoi éviter

- Addons EVO : Workshop, auteur Kali, `[EVO] Addon #1` à `#13` (`steamapps/workshop/content/4000`). Ids : 3663970485, 3672109807, 3526053336, 3672111098, 3573029716, 3672111658, 3593565720, 3620395110, 3620396302, 3624069138, 3668225050. En solo, être abonné à chaque addon utilisé.
- Catalogue 3D local : `C:\Project\Adler_lore\sites\catalogue-evo\index.html` ; métadonnées (champ `phy`) dans `catalogue-evo/tools/meta/models_*.json` ; géométrie mesurée dans `geo_catalogue.json`. Liste blanche du collage : `sites\gmod-build\catalogue-build\modeles_autorises.txt`.
- **Chercher large avant de dire qu'un asset n'existe pas** (63 masques d'Arrancar trouvés après un « il n'y en a pas »).
- Un modèle hors liste blanche peut être **dessiné par script** côté joueur (`ClientsideModel`, 0 posé) : masques EVO, décors impossibles en dupe.

## Utiles
- **Las Noches** (`models/propper/hueco_mundo_v1/`, Addon #10) : arches `s_45_0`, île/dais `s_57`, trône `watcher_group_props_hueco_13`, torches, stèles.
- **Rochers ardoise** (avec `.phy`) : `huecomundosetails200` (mesa), `201` (aiguille), `208` (bloc à gradins), `199` (montagne 2 700 u), `198` (nappe à une face), `101`, `88`, `17`, `100`.
- Dalles à sommet arrondi `hm197_18`, dalles `197_1`, arcade `208_1` (recettes du Lac noir).
- Lumière par props : plaques `debugwhite` teintées ; cristaux `models/arid_valley_v2/arid_crystal_01_test_01` (`_065`, `_045`), unlitgeneric, mais bleus et non teintables.

## Refusés (par EVO ou par Adrien)
- s_40 (bocal de labo), hm40 (cuivre non teintable), cristaux arid en décor coloré, éclats hm20 et cônes hm197_29 (grossiers), siège d'Espada s_71 (plat), velours rouge.
- Aucune épée seule au catalogue (seulement présentoirs, râteliers, panoplies) : la katana est faite en props.
- Le trône manque de beaux os EVO dans la liste blanche (cage costale, mâchoire…) : piste = demander au staff d'en ajouter.
- Particules EVO de tornade (rengoku_tornado, nezuko_firetornado…) : taille et couleur non modifiables, rendu mauvais ; dessiner en script.
