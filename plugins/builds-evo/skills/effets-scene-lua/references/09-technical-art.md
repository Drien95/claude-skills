# 9. Technical artist / optimisation

**Le métier** : le technical artist fait le pont entre les artistes, les designers et les programmeurs. Il garantit la performance, la cohérence et un flux de travail efficace : shaders, scripts d'outils, pipeline, optimisation, parfois VFX (Melissa Robinson, Epic, 2018). Son but : atteindre le framerate visé **sans perte, ou avec un gain, de qualité visible**.

## Principes clés

- **« La performance est la responsabilité de tout le monde, quel que soit son rôle »** (Keith O'Conor, CTO de Romero Games).
- **Draw calls** : chaque changement d'état (texture, shader) demande un nouvel appel de dessin. Les jeux console visent ~2 000-3 000 par image ; les ombres en cascade peuvent doubler le compte (O'Conor).
- **Source** : les modèles (props, entités) sont la première source de draw calls ; **chaque matériau sur un prop ajoute un draw call**. Fusionner des props statiques a apporté ~40 % de gain sur les maps chargées en props (Valve Developer Community, *Draw call*).
- **Mesurer avant d'optimiser** : `vprof_counters 1` (avec sv_cheats) affiche le compte de draw calls ; `r_drawstaticprops`, `r_drawentities`, `r_drawparticles` permettent d'isoler ce qui coûte (VDC).
- **Overdraw** : les surfaces transparentes superposées coûtent cher. Moins de grosses particules animées valent mieux que beaucoup de petites transparentes (O'Conor).
- **Petits triangles** : un triangle d'un pixel gaspille 75 % du travail du GPU sur son bloc de 2×2 pixels. Éviter les triangles minuscules et longs et fins, utiliser des LOD (O'Conor).
- **Prototyper vite** : un prototype en scripts/nodes fonctionne en quelques jours (Robinson).
- **Écrire les règles** : guides de contenu, profils de performance, compromis négociés entre art et code (Robinson).

## Application GMod / EVO

- **Deux budgets séparés** : (1) posés ≤ 400 (props + particules + lumières du catalogue) ; (2) coût client du script : ms par image et dessins/image. La cathédrale v9 est passée de 3,47 à 0,32 ms et de 1 645 à 122 dessins/image : c'est notre référence de « bon » coût.
- **Mesure à chaque version** au banc, avec les mêmes caméras : nombre de posés, ms du script, dessins/image, FPS. Les chiffres vont dans le rapport de la pièce.
- **Un seul matériau par prop autant que possible** ; préférer les modèles EVO déjà utilisés ailleurs dans la scène (même matériau = cache chaud).
- **Script** : regrouper les dessins (même matériau dessiné en lot), couper ce qui est hors de vue ou trop loin (distance + test « joueur dans la boîte »), limiter les lumières dynamiques simultanées.
- **Particules** : peu, grosses, animées ; durée de vie courte ; aucun émetteur actif quand aucun joueur n'est dans la boîte.
- **Règles d'or EVO déjà établies** : rien hors de la boîte, aucune coordonnée serveur en dur, ciel 3D pour l'infini, nettoyage de la map après tests.
- Pour l'allègement des props (100 → 50 sans perte visible), voir **../../pieces-props/references/16-allegement.md** ; pour l'outillage automatique, voir **../../build-evo/references/19-pipeline-outillage.md**.

## Sources
- Melissa Robinson, [Jobs in Unreal Engine: Technical Artist](https://www.unrealengine.com/tech-blog/jobs-in-unreal-engine---technical-artist) (Epic, 2018)
- Keith O'Conor, [GPU Performance for Game Artists](https://80.lv/articles/gpu-performance-for-game-artists) (80.lv, 2017)
- Valve Developer Community, [Draw call](https://developer.valvesoftware.com/wiki/Draw_call)
- Valve Developer Community, [Optimization (level design)](https://developer.valvesoftware.com/wiki/Optimization_(level_design)) (page non lisible par nos outils ce jour, à consulter directement)
- GDC, [Technical Artist Summit](https://gdconf.com/technical-artist-summit)
