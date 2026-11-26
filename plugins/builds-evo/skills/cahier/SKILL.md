---
name: cahier
description: "Cahier des charges complet d'une scène EVO, rempli et validé par Adrien en un message AVANT toute construction (/builds-evo:cahier <scène>). Sans lui, le hook budget refuse les passes du banc. Évite les exigences ajoutées en route qui rouvrent l'addon."
argument-hint: <scène>
---

# Cahier des charges d'une scène

Scène : $ARGUMENTS

1. **Accord** : seulement si Adrien a demandé ce build. Sinon, demande-lui d'abord.
2. **Copier** le modèle `modeles/cahier-des-charges.md` du skill `build-evo` dans le dossier du build (`cahier.md`, à côté de la fiche DA).
3. **Remplir ce qui est déjà su** : note OPTIMUS du chantier (bloc « Pour le prochain fil » d'abord), fiche DA, fiches de scène du projet (`/mnt/project-files/<série>/`), règles permanentes du skill `build-evo` et de `effets-scene-lua/references/assemblage-livraison.md`. La partie C (livraison) est pré-cochée « oui » : ce sont les règles d'Adrien, il ne les redit pas.
4. **Une seule question à Adrien**, numérotée, avec une proposition par défaut pour chaque trou (« 7. 4 places en demi-cercle à 280 u ? »). Il répond par numéro. Pas de deuxième salve : ce qui reste flou part avec la valeur proposée, noté « par défaut ».
5. **Validation** : dès sa réponse, écrire la date dans le cahier et dans `.claude/builds-evo/piece.json` → `"cahier_valide": "AAAA-MM-JJ"` (et `"boite": [dx, dy, dz]`, `"budget_scene": N` si connus, pour le contrôle auto). Le hook `budget` bloque `banc_passe` et `banc_tester` tant que ce champ manque. `"cahier_valide": "dispense"` seulement si Adrien le dit (essai rapide).
6. **Changement après validation** : une ligne datée en bas du cahier ; si elle touche la partie C, dire à Adrien en une ligne ce qu'elle rouvre (fichiers, passes) avant de la faire.
7. Résumer à Adrien en 3 lignes : pièces et budget, ce qui est en script, découpage en sessions (partie D).
