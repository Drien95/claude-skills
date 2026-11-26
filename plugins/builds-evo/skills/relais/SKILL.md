---
name: relais
description: "Passation courte (2 Ko) à la fin d'une étape d'un build EVO (conception, build d'une pièce, script, livraison), pour repartir dans une session neuve au lieu de traîner tout l'historique (/builds-evo:relais). Aussi quand la ligne d'état affiche « → /relais » (contexte ≥ 60 %)."
argument-hint: "[étape suivante]"
---

# Relais entre deux sessions

Étape suivante : $ARGUMENTS

Pourquoi : chaque message d'une longue session relit tout son historique ; l'A2 en un seul fil a coûté environ 10 % de la semaine Max. Une session neuve qui lit 2 Ko repart presque gratuitement.

1. Écrire `.claude/builds-evo/relais.md` (à côté de `piece.json`) d'après le modèle `modeles/relais.md` du skill `build-evo` : fait, décisions d'Adrien datées, fichiers clés (chemins), prochaine étape et modèle conseillé, ordre de la première passe, pièges en cours. 2 Ko au plus, des chemins plutôt que du contenu. Le hook `budget` le relit tout seul au début de la session suivante.
2. Mettre à jour la note OPTIMUS du chantier (bloc « Pour le prochain fil », État, Passation) si le coffre est là (`OPTIMUS_DIR`, sinon `C:\Project\optimus`) ; sinon le dire.
3. `piece.json` à jour (version, posés, planche, note).
4. Dire à Adrien, en 2 lignes : l'étape finie et sa note, puis « ouvre une nouvelle session (ou un nouveau fil) pour <étape suivante> : elle lira le relais ». Modèle conseillé : Sonnet pour le build et le script (`/model sonnet`), le modèle fort pour la conception et la critique finale.
5. Ne rien commencer de l'étape suivante dans cette session.
