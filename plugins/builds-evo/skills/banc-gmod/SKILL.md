---
name: banc-gmod
description: "Banc de test GMod solo sur le PC d'Adrien (banc.py, atelier.py jeu, captures, planches, démos, tournage). À lire AVANT toute commande qui lance, pilote, filme ou ferme GMod : mode éclair sans addons, focus jamais volé, un seul GMod, nettoyage de la map, accord d'Adrien pour lancer."
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

## Outils MCP du banc (à préférer aux commandes)
Le serveur MCP `banc` du plugin applique lui-même ces règles et renvoie des rapports courts :
| Outil | Rôle |
|---|---|
| `banc_etat` | GMod ouvert ? partie du banc ? dernière tâche. Ne lance rien. |
| `banc_tester` | colle un dupe (y = -8000 par défaut) et prend les vues ; `lancer` exige `accord_adrien`, toujours en éclair, GMod gardé ouvert |
| `banc_nettoyer` | nettoie la map après une série |
| `banc_planche` | planche des vues, ou avant/après (`avant=<dossier>`) |
| `banc_montrer` | ouvre les planches sur l'écran d'Adrien |

## Commandes usuelles (si le MCP n'est pas disponible)
| Besoin | Commande |
|---|---|
| Coller une pièce à côté de l'Atelier | `python atelier.py jeu <build> --cote --eclair` |
| Tester et capturer des vues | `python banc.py tester <dupe> --vues <json>` (dans le GMod ouvert) |
| Premier lancement d'une série | ajouter `--lancer --eclair`, **après accord d'Adrien** |
| Charger un nouveau script autorun | canal film du banc (`banc.py filmer <dupe> --lua …`) ou `include` depuis un fichier chargé |
| Filmer (fin de build seulement) | `references/filmer.md` |

Procédure complète, positions de collage et photos : `references/procedure-banc.md`.

## Cadence (A2, 26/11 : 25-30 min → 10 min par planche)
- Un seul collage pour toutes les variantes, sans recharger la map ; toutes les vues en un lot (4 à 6 par variante).
- Critique indépendante courte (note + 5 défauts), une fois, sur la planche finale de la passe.
- Planche valide seulement si la console GMod est vide d'erreur Lua entre le début et la fin de la tâche (`.lua:N:`, `attempt to`) : sinon un script a pu ne rien dessiner et la note ne vaut rien (A2, 26/11 : sable absent sur deux planches notées).
- Tache bleu-cyan floue en bas du cadre sur les vues rasantes : l'arme du joueur du banc, placé 64 u sous la caméra (pas la scène). Le dire à la critique pour qu'elle l'ignore (A2, 26/11).
- `banc_passe` avec un script modifié : le rechargement à chaud peut tomber pendant la 1re vue (A2 v4 : ciel de jour sur « arrivée »). Vérifier la 1re vue ; si elle est fausse, relancer la passe sans `scripts` (18 s) avant la critique.
- Critique : Sonnet suffit (essai du 26/11 sur la même planche : mêmes notes à 0,5 près et mêmes défauts que le modèle principal).
- Mesurer le temps de chaque passe et ce qui l'a pris ; le jeu lui-même compte peu (collage + 12 vues = 40 s), la mesure des bornes et l'écriture du build dominent : partir du catalogue des bornes et d'un générateur à paramètres.

## Ce qu'on livre à Adrien après une série
- Une planche (toutes les vues, avant/après) **ouverte sur son écran** (visionneuse + explorateur) : donner un chemin ne suffit pas.
- Ce qui n'a pas été testé en jeu, dit clairement.
- La map nettoyée.
