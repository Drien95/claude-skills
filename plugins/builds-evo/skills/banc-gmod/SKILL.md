---
name: banc-gmod
description: Banc de test GMod solo sur le PC d'Adrien (banc.py, atelier.py jeu, captures, planches, démos, tournage). À lire AVANT toute commande qui lance, pilote, filme ou ferme GMod : mode éclair sans addons, focus jamais volé, un seul GMod, nettoyage de la map, accord d'Adrien pour lancer.
---

# Banc GMod (PC d'Adrien)

Le banc juge les pièces en vrai rendu Source, sur gm_flatgrass, en solo. Ce skill ne modifie **jamais** le banc ni l'Atelier : il dit comment s'en servir.

## Interdits (le hook `garde_banc` du plugin les bloque)
1. **GMod ne vole jamais le focus** : `--focus` est interdit. Un seul passage au premier plan de 3 à 5 s par série est toléré, avec l'accord d'Adrien et en prévenant juste avant.
2. **Jamais GMod avec les addons d'Adrien** : tout lancement passe par le mode **éclair** (`--eclair`, c.-à-d. `-noworkshop`, contenu copié par l'Atelier). Jamais `gmod.exe`, `hl2.exe` ou `steam -applaunch 4000` à la main.
3. **Ne jamais lancer ni relancer GMod sans l'accord d'Adrien** ; s'il l'a fermé, on ne rouvre rien. Vérifier qu'aucune commande (recollage compris) ne relance GMod toute seule.
4. **Ne jamais fermer le GMod du banc en pleine pièce** ni couper la session Remote Control : un GMod neuf hors focus ne dessine rien et tout le contexte est perdu. Si les images tardent, interroger, pas relancer.
5. **Un seul GMod ouvert** (`-hijack +map gm_flatgrass` charge la carte dans le GMod déjà ouvert).
6. **Nettoyer la map après les tests** (`gmod_admin_cleanup`, ou une tâche du banc : `game.CleanUpMap` passe en tête de tâche). Adrien a laggé le 16/11.
7. Le jeu ne doit pas être en pause (console ou Échap ouverts bloquent le banc).
8. Ne jamais contourner la protection d'une map vendeur (Hueco) : recréer la zone sur flatgrass.
9. Supprimer un fichier : corbeille Windows (`DeleteFile ... SendToRecycleBin` en PowerShell), jamais `rm`.

## Commandes usuelles
| Besoin | Commande |
|---|---|
| Coller une pièce à côté de l'Atelier | `python atelier.py jeu <build> --cote --eclair` |
| Tester et capturer des vues | `python banc.py tester <dupe> --vues <json>` (dans le GMod ouvert) |
| Premier lancement d'une série | ajouter `--lancer --eclair`, **après accord d'Adrien** |
| Charger un nouveau script autorun | canal film du banc (`banc.py filmer <dupe> --lua …`) ou `include` depuis un fichier chargé |
| Filmer (fin de build seulement) | `references/filmer.md` |

Procédure complète, positions de collage et photos : `references/procedure-banc.md`.

## Ce qu'on livre à Adrien après une série
- Une planche (toutes les vues, avant/après) **ouverte sur son écran** (visionneuse + explorateur) : donner un chemin ne suffit pas.
- Ce qui n'a pas été testé en jeu, dit clairement.
- La map nettoyée.
