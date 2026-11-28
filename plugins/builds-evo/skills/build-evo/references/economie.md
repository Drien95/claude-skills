# Économie de jetons d'un build (forfait Max, jamais d'API)

Adrien paie un forfait Max, remis à zéro le jeudi à 00 h 00. L'A2 « Le Sable du Fond » (26/11/2026) en a pris environ 10 % pour une scène. But proposé : diviser ce coût par 3 au moins, sans baisser le seuil de 7,5 (à vérifier au prochain build avec `/builds-evo:conso`).

## Ce qui a coûté sur l'A2 (diagnostic du 26/11)
| Poste | Ce qui s'est passé | Règle qui le coupe |
|---|---|---|
| Itérations | 15 versions du dupe, 8 séries, chaque passe = banc + 9 à 12 images + une critique | plafond de 5 passes sans point (hook), contrôle auto avant critique |
| Fil unique | ~3 h dans un seul fil : chaque message relit tout l'historique | une session par étape + relais de 2 Ko (hook au démarrage) |
| Exigences en route | détection, gravure, effacement total, console seulement : chacune a rouvert l'addon | cahier des charges validé avant la 1re passe (hook) |
| Critique qui plafonne | séries 5 à 8 entre 6 et 7 : la critique tournait en rond | Adrien juge en jeu ou en film après 3 séries au même plafond |
| Planches fausses | 2 planches notées avec le sable absent (erreur Lua) | console lue par `banc_passe`, planche refusée |
| Mesures à la main | bornes des modèles mesurées pièce par pièce | `bornes_modeles.json`, générateurs à paramètres |

## Les 10 règles (les hooks du plugin font respecter celles marquées ⚙)
1. ⚙ **Cahier des charges puis maquette three.js validés avant toute passe** (`/builds-evo:cahier`, étape 7) : `banc_passe` et `banc_tester` sont refusés tant que `piece.json` n'a pas `cahier_valide` et `maquette_validee`.
2. ⚙ **Une session (ou un fil) par étape** : conception, build d'une pièce, script, livraison. Fin d'étape ou ligne d'état « → /relais » (contexte ≥ 60 %) : `/builds-evo:relais`, puis session neuve. Le hook relit le relais au démarrage.
3. **Le bon modèle à chaque étape** (les agents portent leur modèle dans leur en-tête) :
   | Étape | Modèle |
   |---|---|
   | Cahier, fiche DA, fiches de pièces, choix de silhouette, séquence difficile | modèle fort (session principale) |
   | Passes du banc (agent `passe-banc`), critiques de passe (`critique-build`), allègement (`allegement`), script courant, livraison | Sonnet (`/model sonnet` pour la session de build) |
   | Note annoncée comme finale (agent `critique-finale`) | modèle fort, une fois par pièce |
4. ⚙ **Plafond de 5 passes sans point avec Adrien** (`plafond_passes` dans `piece.json`, 0 = sans plafond, sur son ordre seulement). Le message d'Adrien remet le compteur à 0.
5. **Retour groupé** : à chaque point, une planche ouverte sur son écran, la note, les défauts numérotés et 2 ou 3 options numérotées. Adrien répond une fois, par numéros (« 1 oui, 3 non, 4 : plus sombre »). Toutes les questions dans le même message, jamais une par une.
6. **Contrôles gratuits avant toute critique** : contrôle auto du dupe (`outils/controle_auto.py`, lancé par `banc_passe` : 400 posés, classes bloquées, playermodels, modèles hors liste, doublons, boîte, flottants), console Lua lue, puis `outils/controle_livraison.py` avant la critique finale. Une critique ne juge qu'une planche passée par ces contrôles.
7. ⚙ **Une critique par planche** (Sonnet), une critique finale par pièce (modèle fort). Pas de deuxième avis sur la même passe.
8. ⚙ **Images légères** : 12 vues au plus par passe ; lire la planche (une image), jamais chaque capture (une capture plein écran ≈ 1 800 jetons, la planche de 9 vues aussi). Vue de près demandée par Adrien : la copier dans `zoom/`.
9. **Briques communes d'abord** : bibliothèque de pièces (`pieces-props/references/bibliotheque.md`), générateurs à paramètres (`outils/dunes/`), `bornes_modeles.json`, gravure (`outils/gravure.py`, `gravure_lua/`), addon de l'A2 comme squelette (`creations-evo/a2-sable-du-fond` : commandes, effacement total, diag, état partagé, console). On copie et on adapte ; on ne réécrit pas.
10. ⚙ **Mesurer** : le hook `budget` compte les jetons de chaque session par scène, pièce et modèle (`conso.json`, 0 jeton) ; `/builds-evo:conso` à la rétro, colonne « Indice » du journal de mesure.

11. **Moins d'appels, pas moins de lecture** (mesuré le 28/11/2026 sur le test « Puits des Mues » : 66 % du coût = le contexte relu à chaque appel, socle ~82 k ; les images < 1 %) : regrouper les commandes (une seule pour plusieurs recherches), une passe = un appel (`maquette_passe`, `banc_passe`), lire le résumé des alertes et pas les sorties complètes.
12. **Sonnet dès la 4e passe** : jusqu'à 3 passes courtes (1 ou 2 appels chacune), les faire dans la session ; au-delà, ou pour un vrai travail de build, confier les passes à un agent Sonnet (`passe-banc`) avec un ordre écrit, car il recharge ~40 k de contexte à chaque lancement.

## Ordres de grandeur (26/11/2026)
- Une image lue : jusqu'à ~1 800 jetons (plein écran) ; une planche 3 × 3 de 640 × 360 : pareil pour 9 vues.
- Un agent : 10 000 à 30 000 jetons par passage (il relit ses fichiers) ; sur Sonnet, environ 3/5 du coût sur le modèle fort.
- Une session longue : chaque tour relit tout le contexte (en cache, moins cher, mais pas gratuit) ; à 60 % de contexte, un relais coûte moins que la suite.
- L'indice de `/builds-evo:conso` pondère les jetons par les prix API relatifs (Opus 5, Sonnet 3, Haiku 1 ; cache lu 0,1, écrit 1,25, sortie 5) : il compare deux builds, ce n'est pas un pourcentage du forfait.

## Sorties de secours (seulement sur la parole d'Adrien, dans le fil)
- `"plafond_passes": 0` (pas de plafond), `"max_vues": N`, `"cahier_valide": "dispense"`, `"maquette_validee": "dispense"` dans `piece.json`.
- `BUILDS_EVO_HOOKS_OFF=budget` coupe le hook entier (comptage compris).
- Le compteur de passes repart à 0 à chaque message reçu dans la session : dans une session pilotée par un autre fil (Remote Control), ce fil doit relayer le point d'Adrien, pas le simuler.
