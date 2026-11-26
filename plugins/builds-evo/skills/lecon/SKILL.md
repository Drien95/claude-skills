---
name: lecon
description: Ranger une erreur corrigée pendant un build EVO dans le bon skill du repo claude-skills (une ligne « vu, cause, règle ») sur une branche, pour la PR d'Adrien. À lancer par Adrien (/lecon <ce qui s'est passé>) ou par un fil dès qu'une erreur a coûté une version, une capture ratée ou une remarque d'Adrien.
argument-hint: <ce qui s'est passé>
---

# Ranger une leçon

Leçon : $ARGUMENTS

1. Lis la table « Où l'écrire » dans `references/capitaliser.md` du skill `build-evo` et choisis **un** fichier cible.
2. Clone local du repo de skills : variable `CLAUDE_SKILLS_REPO`, sinon `C:\Project\claude-skills`. Ne change **jamais** de branche dans ce clone : le plugin installé en est tiré, et une branche `lecon/` oubliée y chargerait du travail pas encore mergé. Dans le clone : `git fetch origin main`, puis `git worktree add ../claude-skills-lecon-<sujet-court> -b lecon/<sujet-court> origin/main`. Toutes les étapes suivantes se font dans ce dossier à part.
3. Lis le fichier cible. Si une règle existante dit déjà la même chose, ajoute la date du jour sur sa ligne (c'est une **répétition**) ; si elle la contredit, remplace-la. N'empile pas de doublon.
4. Écris une ligne au format du fichier (souvent « ce qu'on a vu | cause | règle »), datée (JJ/MM/AAAA) avec la source (scène, pièce, version).
5. **Promotion** (règle 3 de `capitaliser.md`) : une ligne qui porte maintenant **2 dates** et qui est vérifiable sur une commande ou un fichier doit devenir un **hook** ; une méthode qui a marché **3 fois** doit monter dans `build-evo/SKILL.md`. Propose-le à Adrien. Plus largement, si c'est un **interdit strict** vérifiable sur une commande ou un fichier, propose aussi à Adrien un test dans un hook (`plugins/builds-evo/hooks/`) avec son test dans `tests/`, mais ne l'écris qu'avec son accord.
6. Ajoute une ligne dans `CHANGELOG.md` sous « Non publié ».
7. Commit, push, PR vers `main` avec Adrien en relecteur. Ne merge jamais toi-même. Puis, depuis le clone : `git worktree remove ../claude-skills-lecon-<sujet-court>` (la branche reste sur GitHub pour la PR).
8. Réponds à Adrien en 2 lignes : la règle ajoutée et le lien de la PR.
