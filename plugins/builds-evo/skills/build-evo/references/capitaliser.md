# Chaque erreur corrigée devient une ligne dans le bon skill

Règle du repo : si une erreur a coûté une version, une capture ratée ou une remarque d'Adrien, elle ne doit pas se reproduire. On l'écrit **une fois, au bon endroit**, au format « ce qu'on a vu | cause | règle ».

## Où l'écrire
| L'erreur porte sur… | Skill | Fichier |
|---|---|---|
| l'image, la DA, la lumière, les goûts d'Adrien | composition-scene | `references/gouts-adrien.md` ou la fiche du domaine |
| un prop, le dupe, le collage, le budget, un matériau | pieces-props | `references/regles-dupe-evo.md` ou `recettes-pieces.md` |
| le Lua, un effet, la perf, la livraison serveur | effets-scene-lua | `references/pieges-lua.md` ou `recettes-effets.md` |
| le rythme, les séquences, la caméra, le son, la fiche MJ | mise-en-scene | la fiche du domaine |
| GMod, banc.py, l'Atelier, les captures, le focus | banc-gmod | `references/regles-banc.md` ou `procedure-banc.md` |
| la méthode, l'ordre des étapes, la note | build-evo | `SKILL.md` ou `boucle-piece.md` |

Si la règle est un **interdit strict** vérifiable sur une commande ou un fichier, proposer aussi un test dans un hook (`hooks/`), avec son test dans `tests/`.

## Comment
1. Dans le clone local du repo : nouvelle branche `lecon/<sujet-court>`.
2. Une ligne (ou une ligne de tableau) datée, avec la source (pièce, version).
3. Si la ligne contredit une règle existante : remplacer l'ancienne, ne pas empiler.
4. Ligne dans `CHANGELOG.md` sous « Non publié ».
5. PR ; Adrien merge. Les releases regroupent les leçons.

Garder `SKILL.md` court : une leçon y monte seulement si elle s'applique à chaque build.
