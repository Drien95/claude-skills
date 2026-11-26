---
name: retro
description: "Rétro de 5 minutes à la fin d'un build EVO (ou d'une pièce longue), à la demande d'Adrien (/retro <scène>) ou quand un fil clôt un build : complète le journal de mesure, tire 3 leçons et les range par PR."
argument-hint: <scène>
---

# Rétro de fin de build

Scène : $ARGUMENTS. Durée visée : 5 minutes, réponse courte.

1. **Chiffres** : complète les lignes de la scène dans `journal/mesures.md` du clone du repo de skills (`CLAUDE_SKILLS_REPO`, sinon `C:\Project\claude-skills`) : fin, heures, versions, planches, posés, note, cause si > 3 planches ou > 10 versions. Compare avec les builds précédents du journal.
2. **Trois questions**, une à trois lignes chacune :
   - Qu'est-ce qui a coûté le plus de versions, et pourquoi ?
   - Qu'est-ce qui a marché et doit être refait ?
   - Qu'est-ce qui manquait aux skills (règle absente, fiche introuvable, outil qui a manqué) ?
3. **Ranger** : chaque réponse utile devient une ligne via la méthode de `/builds-evo:lecon` (une seule branche `retro/<scène>` pour toute la rétro). Les pièces validées vont dans la bibliothèque (`pieces-props/references/bibliotheque.md`).
4. **Ménage** : si c'est le 3e ou 4e build depuis le dernier ménage (voir `CHANGELOG.md`, entrées « Ménage »), propose à Adrien de relire les skills pour supprimer les règles mortes ou en double.
5. PR vers `main`, Adrien merge. Réponds à Adrien : les chiffres clés en une ligne, les 3 leçons, le lien de la PR.
