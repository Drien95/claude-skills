---
name: pieces-props
description: "Construire ou corriger une pièce en props pour un dupe AdvDupe2 du serveur EVO : règles du collage (prop_physics seul, liste blanche, 400 posés), modèles PHX et EVO, matériaux, géométrie mesurée, allègement, génération par build.py, recettes de pièces. À utiliser pour écrire un build.py, choisir des props ou alléger un build."
---

# Pièces en props (dupe AdvDupe2 pour EVO)

Ce skill fabrique la **forme** : tout ce qu'on touche ou voit de près. Tout le reste (lumière, flammes, gaz, fumée, brume, lointains, ce qui dépasse le plafond) va en script → `effets-scene-lua`.

## Règles dures (un dupe qui les viole casse en jeu)
1. Seule la classe `prop_physics` se colle, en mode build. `gmod_light`, `gmod_lamp`, `gmod_emitter`, `prop_effect` sont refusés. Les particules et lumières du catalogue se posent à la main après collage (et comptent dans les 400).
2. **400 posés au total** (props + particules + lumières du catalogue). Le script est hors quota. Donner le nombre de posés de chaque pièce d'office, budget fixé AVANT de construire.
3. Chaque modèle doit être dans la **liste blanche** EVO (chemin exact, minuscules) et avoir un `.phy`. Jamais de playermodel, Hollow, Menos (`models/evo/summons`, `characters`).
4. Ne **jamais** écrire `Frozen` dans le dupe (au collage, `Frozen = true` dégèle).
5. Matériau gardé seulement s'il est dans les 44 OverrideMaterials (casse exacte). Base : `models/shiny` teinté ; `debugwhite` seulement pour ce qui brille.
6. Échelle x0,1 à x5, 4 000 u max par pièce.
7. **Mesurer la géométrie réelle** (bornes de `geo_catalogue.json`) avant de poser ; certains PHX ne sont pas centrés sur leur origine.
8. Origine de chaque prop au-dessus du sol (sinon Source le rend noir) ; la pièce de tête est la plus basse.
9. Jamais bord à bord : chevaucher (≥ 1,5 u ou échelle 1,006), décaler les surfaces coplanaires (≥ 1 u).

Détail et causes : `references/regles-dupe-evo.md`.

## Méthode
- **D'abord la bibliothèque** de pièces validées (`references/bibliotheque.md`) : copier et adapter une pièce existante plutôt que repartir de zéro.
- On part du **gabarit** (`build.py` + `encode.py` + `rochers.py`, dossier `gmod-build/gabarit/` du projet) : le build est généré par Python, jamais posé à la main. Une version = un fichier numéroté, on garde les anciennes.
- 3 silhouettes en parallèle avant le détail (skill `build-evo`).
- **Masse générée, héros composé à la main** : `references/20-generation-procedurale.md`.
- **Allègement** (agent `allegement` si la pièce dépasse son budget) : le détail va où l'œil regarde ; une longue pièce plutôt que plusieurs petites ; la matière remplace le relief ; supprimer l'invisible ; comparer côte à côte complet vs allégé. `references/16-allegement.md`.
- **Set dressing** : grappes de 3, usure qui a une cause. `references/04-set-dressing.md`.
- Recettes qui ont marché (épée, trône, île, lac, cathédrale…) : `references/recettes-pieces.md`.
- Props EVO utiles et refusés : `references/catalogue-evo.md`.

## Checklist avant d'envoyer un dupe
1. Aucun `Frozen`. 2. Tous les modèles existent (PHX : petit chiffre d'abord) et sont dans la liste blanche avec `.phy`. 3. Total posés ≤ budget de la pièce et ≤ 400. 4. Axe-aligné sauf inclinaison voulue et testée. 5. Pas de coplanaire ni de fente. 6. Aucune classe bloquée. 7. Matériaux autorisés. 8. Rien ne traverse un endroit où l'on marche (calcul). 9. Pièce de tête la plus basse. 10. Le dupe se décode et la maquette three.js est à jour. 11. Rien hors de la boîte de scène. 12. Dire à Adrien ce qui n'a pas été testé en jeu.
