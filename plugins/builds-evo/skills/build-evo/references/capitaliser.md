# Amélioration continue (validé par Adrien le 26/11/2026)

Il manquera toujours des choses : on ne les découvre qu'en construisant. Le système apprend tout seul par 5 règles :

1. **Capturer chaque erreur tout de suite** : `/builds-evo:lecon` après chaque correction. L'erreur devient une ligne dans le bon skill, sur une branche, pour la PR d'Adrien.
2. **Rétro de 5 min en fin de build** : ce qui a coûté le plus de versions, ce qui a marché, ce qui manquait au skill. Le journal de mesure dit si on progresse (versions, heures, planches). Les conclusions partent en `/builds-evo:lecon`.
3. **Promouvoir ce qui revient** : une même erreur vue **2 fois** devient un **hook** qui la bloque ; une méthode qui marche **3 fois** monte dans la checklist d'une page (`build-evo/SKILL.md`).
4. **Ménage tous les 3 ou 4 builds** : relire les skills, supprimer les règles mortes ou en double, fusionner. Un skill court et à jour vaut mieux qu'un gros (chaque ligne recoûte des tokens).
5. **Bibliothèque de pièces validées** : chaque pièce réussie devient un module réutilisable (`pieces-props/references/bibliotheque.md`) ; chaque build part de plus haut.

Pour compter les répétitions (règle 3), chaque leçon porte sa date ; une leçon qui revient reçoit une 2e date sur la même ligne au lieu d'une nouvelle ligne.

# Chaque erreur corrigée devient une ligne dans le bon skill

Règle du repo : si une erreur a coûté une version, une capture ratée ou une remarque d'Adrien, elle ne doit pas se reproduire. On l'écrit **une fois, au bon endroit**, au format « ce qu'on a vu | cause | règle ».

## Où l'écrire
| L'erreur porte sur… | Skill | Fichier |
|---|---|---|
| l'image, la DA, la lumière, les goûts d'Adrien | composition-scene | `references/gouts-adrien.md` ou la fiche du domaine |
| un prop, le dupe, le collage, le budget, un matériau | pieces-props | `references/regles-dupe-evo.md` ou `recettes-pieces.md` |
| le Lua, un effet, la perf, la livraison serveur | effets-scene-lua | `references/pieges-lua.md` ou `recettes-effets.md` |
| le rythme, les séquences, la caméra, le son, la fiche MJ | mise-en-scene | la fiche du domaine |
| GMod, banc.py, l'Atelier, les captures, le focus | banc-gmod | `references/procedure-banc.md` |
| la méthode, l'ordre des étapes, la note | build-evo | `SKILL.md` ou `boucle-piece.md` |
| un gaspillage de jetons (passe inutile, session trop longue, image en trop, exigence oubliée au cahier) | build-evo | `references/economie.md` ou `modeles/cahier-des-charges.md` (contrôle gratuit possible : `outils/controle_auto.py`, `controle_livraison.py`) |

Si la règle est un **interdit strict** vérifiable sur une commande ou un fichier, proposer aussi un test dans un hook (`hooks/`), avec son test dans `tests/`.

## Comment
1. Dans un worktree à part du clone local (jamais de changement de branche dans le clone, d'où vient le plugin) : nouvelle branche `lecon/<sujet-court>` (détail : `/builds-evo:lecon`, étape 2).
2. Une ligne (ou une ligne de tableau) datée, avec la source (pièce, version).
3. Si la ligne contredit une règle existante : remplacer l'ancienne, ne pas empiler.
4. Ligne dans `CHANGELOG.md` sous « Non publié ».
5. PR ; Adrien merge. Les releases regroupent les leçons.

Garder `SKILL.md` court : une leçon y monte seulement si elle s'applique à chaque build.
