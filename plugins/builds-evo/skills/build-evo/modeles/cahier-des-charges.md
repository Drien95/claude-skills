# Cahier des charges : <scène>

Rempli AVANT toute construction, validé par Adrien en UN message (il répond par numéro : « 3 non, 7 : 4 places »).
Une exigence absente d'ici et ajoutée en route = l'addon rouvert (A2 : détection, gravure, effacement total,
console seulement sont arrivés après coup et ont coûté une série chacun). Copier dans `<dossier du build>/cahier.md`.

## A. La scène (ce qu'on juge)
1. Phrase-titre, rôle dans la campagne, fiche DA (chemin) :
2. Pièces prévues (nom, budget de posés, héros ou non) et total sur 400 :
3. Ce qui passe en script (lumière, brume, sable, lointains, ciel) :
4. Vues de jugement (2 ou 3) + arrivée des joueurs ; nombre de vues par passe (12 au plus) :
5. Critères « fini quand » de la scène (3 à 5, vérifiables sur une planche) :
6. Ce qu'Adrien ne veut pas voir (goûts, références refusées) :

## B. Le jeu (ce que font les MJ et les joueurs)
7. Joueurs : combien, où ils se placent (places, assises), ce qu'ils peuvent toucher :
8. Séquences (calme → signe → montée → silence → sommet → retombée), en secondes :
9. Commandes MJ prévues (nom | arguments | qui | effet) ; commandes joueur (diag) :
10. Résultats de jet à traduire en effets (réussite, partiel, échec, fiasco, critique) :
11. Sons (sans musique) :

## C. Livraison (cochée par `outils/controle_livraison.py`)
12. Détection du build par gravure d'usine (`outils/gravure.py`) + ancre par motif en secours : oui / dispense d'Adrien
13. Effacement total `<nom>_tout_effacer` (double confirmation 10 s, props du build seulement, gravure, état, timers, hooks, effets et sons chez tous) : oui
14. Aucune notification à l'écran, console seulement : oui
15. Liste complète des commandes : README + `COMMANDES.md` + note OPTIMUS : oui
16. Boîte de scène (h × L × l relative au prop repère), aucune coordonnée de map, seuls les joueurs dedans voient et entendent : dimensions
17. Touches jamais en dur (bind suggérés dans le README) ; joueurs qui arrivent en cours rattrapés : oui
18. Où ça part : creations-evo/<dossier>, dupe dans advdupe2\<projet>\, test final par le staff sur EVO :

## D. Le budget de travail (ce qui coûte des jetons)
19. Plafond de passes sans point avec Adrien (défaut 5) ; versions visées par pièce (≤ 10) ; planches (3 + 1 finition) :
20. Découpage en sessions : conception (modèle fort) → build (Sonnet, agent passe-banc) → script (Sonnet) → critique finale (agent critique-finale) ; un relais court entre chaque (`/builds-evo:relais`).
21. Moments où Adrien juge lui-même (en jeu ou film de 30 s) plutôt qu'une critique de plus :

## Validation
- Validé par Adrien le : AAAA-MM-JJ (écrire la même date dans `piece.json` → `cahier_valide`)
- Changements après validation (date, quoi, pourquoi) : une ligne chacun ; un ajout de la partie C rouvre la livraison, le dire à Adrien avec son coût.
