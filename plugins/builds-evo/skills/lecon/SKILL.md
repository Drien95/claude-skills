---
name: lecon
description: Ranger une erreur corrigée pendant un build EVO dans le bon skill du repo claude-skills (une ligne « vu, cause, règle ») sur une branche, pour la PR d'Adrien. À lancer par Adrien (/lecon <ce qui s'est passé>) ou par un fil dès qu'une erreur a coûté une version, une capture ratée ou une remarque d'Adrien.
argument-hint: <ce qui s'est passé>
---

# Ranger une leçon

Leçon : $ARGUMENTS

1. Lis la table « Où l'écrire » dans `references/capitaliser.md` du skill `build-evo` et choisis **un** fichier cible.
2. Ouvre le clone local du repo de skills (variable `CLAUDE_SKILLS_REPO`, sinon `C:\Project\claude-skills`). Mets `main` à jour (`git pull`), puis crée la branche `lecon/<sujet-court>`.
3. Lis le fichier cible. Si une règle existante dit déjà la même chose, précise-la ; si elle la contredit, remplace-la. N'empile pas de doublon.
4. Écris une ligne au format du fichier (souvent « ce qu'on a vu | cause | règle »), datée (JJ/MM/AAAA) avec la source (scène, pièce, version).
5. Si c'est un **interdit strict** vérifiable sur une commande ou un fichier, propose aussi à Adrien un test dans un hook (`plugins/builds-evo/hooks/`) avec son test dans `tests/`, mais ne l'écris qu'avec son accord.
6. Ajoute une ligne dans `CHANGELOG.md` sous « Non publié ».
7. Commit, push, PR vers `main` avec Adrien en relecteur. Ne merge jamais toi-même.
8. Réponds à Adrien en 2 lignes : la règle ajoutée et le lien de la PR.
