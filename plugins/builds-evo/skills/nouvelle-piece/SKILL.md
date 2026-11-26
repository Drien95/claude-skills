---
name: nouvelle-piece
description: "Ouvrir une nouvelle pièce de build EVO, à la demande d'Adrien (/nouvelle-piece <scène> <pièce>) ou quand un fil commence une pièce : crée sa fiche de pièce et sa ligne dans le journal de mesure."
argument-hint: <scène> <pièce> [budget]
---

# Ouvrir une pièce

Arguments : $ARGUMENTS (scène, pièce, budget de posés facultatif).

1. **Accord** : ne commence que si Adrien a demandé cette pièce. Sinon, demande-lui d'abord.
1 bis. **Cahier** : le cahier des charges de la scène doit être validé (`/builds-evo:cahier`) ; sinon le faire d'abord (le hook `budget` refuse le banc sans lui).
2. **Fiche de pièce** : copie le modèle `modeles/fiche-piece.md` du skill `build-evo` dans le dossier du build (`sites/<scène>/assets/<pièce>/fiche.md` ou à côté du `avancement.md` de la scène) et remplis ce que tu sais déjà : rôle, fonction de base, emprise, budget (sur 400, en tenant compte des posés déjà pris par la scène), 3 vues de jugement, critères « fini quand ». Laisse vide ce que tu ne sais pas et pose les questions à Adrien en une fois.
3. **Journal** : à partir du clone local du repo de skills (variable `CLAUDE_SKILLS_REPO`, sinon `C:\Project\claude-skills`), ajoute une ligne à `journal/mesures.md` : scène, pièce, date de début (AAAA-MM-JJ), budget, le reste vide. Jamais de changement de branche dans le clone (le plugin en est tiré) : travaille dans un worktree à part, branche `journal/<scène>-<pièce>`, comme à l'étape 2 de `/builds-evo:lecon` ; commit ; la PR se fera à la clôture de la pièce avec les chiffres finaux, puis retire le worktree.
4. **État pour la ligne d'état** : écris `.claude/builds-evo/piece.json` à la racine du projet (ex. `C:\Project\Adler_lore\.claude\builds-evo\piece.json`) : `{"scene": "...", "piece": "...", "version": 1, "budget": N, "poses_piece": 0, "poses_scene": <posés déjà pris>, "planche": 0, "note": null, "pieces_scene": <pièces prévues dans la scène>, "cahier_valide": "<date du cahier>", "plafond_passes": 5, "max_vues": 12}` (facultatifs pour le contrôle auto : `"boite": [dx, dy, dz]`, `"budget_scene": N`). `pieces_scene` donne l'avancement x/N du tableau de bord OPTIMUS. Les fils le mettent à jour à chaque version ; `compteurs.json` et `conso.json` sont tenus par les hooks.
5. **Bibliothèque** : regarde `references/bibliotheque.md` du skill `pieces-props` ; si une pièce validée s'en approche, propose de partir d'elle.
6. **Rappel de méthode** à Adrien en 3 lignes : 3 silhouettes en parallèle sur une planche, une décision par planche, arrêt à 7,5/10 (3 planches + 1 finition au plus), point avec lui toutes les 5 passes au plus.
7. Si la session a déjà servi à une autre étape : `/builds-evo:relais`, et ouvrir la pièce dans une session neuve (Sonnet pour les passes).
