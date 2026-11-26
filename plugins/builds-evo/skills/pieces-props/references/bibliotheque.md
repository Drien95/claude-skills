# Bibliothèque de pièces validées

Chaque pièce validée par Adrien (note ≥ 7,5, ou « forme finale ») devient un module réutilisable : un nouveau build part de là au lieu de repartir de zéro. **Chercher ici avant de concevoir une pièce.**

Règles :
- On ajoute une pièce à sa validation (ligne datée, avec ses chemins et ses chiffres) via `/builds-evo:lecon` ou une PR `bibliotheque/<pièce>`.
- On réutilise en **copiant** dans le nouveau build (jamais en modifiant l'original : il appartient à une scène livrée).
- Une pièce adaptée qui devient meilleure s'ajoute comme variante, l'ancienne reste.
- Chemins relatifs à `C:\Project\Adler_lore` (vérifier qu'ils existent avant de s'en servir ; certains viennent de la mémoire du projet).

| Pièce | Posés | Note | Ce qui la rend réutilisable | Dupe / build | Script d'effets |
|---|---|---|---|---|---|
| Katana noir (lame en V, fil carmin, sans dos) | 50 | 7,5 | toute épée plantée ou exposée ; garde et poignée réglables | `atelier\builds\lac_noir_katana` (variante 50) | effets posés sur les axes mesurés de la lame |
| Épée complète (katana + griffes P3 + socle) | 57 | 7,5 | épée héroïque au centre d'une scène | `atelier\builds\lac_noir_epee_retenue` | tornade J3 : `atelier\_claude_stage\lac_builds\essai_tornade_script_passe4.lua` (8,5/10) |
| Trône K5 (dais s_57, dossier fendu) | 27 | 8,5 | siège de pouvoir vide, lueur dans la fente | `atelier\builds\lac_noir_trone_k5` | fil de braise : `sites\lac-noir\assets\trone\custom_cadre_K5` |
| Île I4 (terrasse, 6 marches, rive en dalles penchées) | 16 | 7,5 | estrade ou îlot praticable pour ~12 joueurs | `atelier\builds\lac_noir_lac_demo` | veines qui courent dans la pierre (effet signature) |
| Lac noir miroir | 4 | 7,5 | toute eau noire ou sol miroir | `atelier\builds\lac_noir_lac_demo` | miroir au pochoir, veines 2 couches, onde de choc |
| Cathédrale de flèches noires v10 | ≤ 90 | 7,5 | arrière-plan gigantesque (façade props + ciel 3D) | `atelier\builds\lac_noir_cathedrale_P2` | ciel 3D 1/16 et 1/64, perspective aérienne |
| Scène Lac noir complète (v76) | 218 | final | référence d'assemblage d'une scène par modules et séquences | `Drien95/creations-evo` dossier `lac-noir` | addon `lac_noir_hueco` v85 |
| Segunda d'Azeno v16 (piliers v27) | – | final | salle à piliers qui s'allument en séquence, voix | `Drien95/creations-evo` dossier `azeno` | `atelier_segunda_azeno.lua` (figé, ne plus y toucher) |
| Sceau Hachigen en PHX (Exequias v15) | 10 | – | sceau lumineux au sol sans modèle `.phy` | `/mnt/project-files/exequias/` (build_v14/v15) | – |
