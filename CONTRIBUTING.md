# Travailler sur claude-skills

## Règles
1. **Jamais de commit direct sur `main`.** Une branche par changement (`lecon/…`, `skill/…`, `hook/…`, `journal/…`, `release/x.y.z`), une PR, **Adrien merge**.
2. **Chaque erreur corrigée en build devient une ligne dans le bon skill** (voir `plugins/builds-evo/skills/build-evo/references/capitaliser.md`, ou la commande `/builds-evo:lecon`). Format « ce qu'on a vu | cause | règle », daté, avec la source. On remplace une règle contredite au lieu d'empiler.
3. `SKILL.md` reste court (une page) : le détail va dans `references/`. Une leçon monte dans `SKILL.md` seulement si elle s'applique à chaque build.
4. Un interdit strict vérifiable sur une commande ou un fichier peut devenir un test de hook, **avec son test** dans `tests/`.
5. Descriptions des skills : une phrase « quoi + quand », bien distincte des autres skills (c'est elle qui déclenche le skill).
6. Pas de secret, pas de clé d'API (Adrien utilise son abonnement Max, pas l'API).

7. **Ménage tous les 3 ou 4 builds** (règle 4 du README) : PR `menage/AAAA-MM-JJ` qui supprime les règles mortes ou en double et fusionne ; une ligne « Ménage » dans le CHANGELOG (la rétro s'en sert pour savoir quand proposer le suivant).

## Avant chaque PR
```
python -m unittest discover -s tests
claude plugin validate plugins/builds-evo
claude plugin validate .
```
La vérification GitHub (`.github/workflows/verifier.yml`) relance les tests, la cohérence des versions et le CHANGELOG sur chaque PR.

## Versions et releases
- Semver par plugin : `x.y.z` dans `plugins/<plugin>/.claude-plugin/plugin.json` **et** dans l'entrée du plugin de `.claude-plugin/marketplace.json` (les deux doivent être égales ; le test le vérifie).
  - **z** : leçons, corrections de texte, ligne de journal.
  - **y** : nouveau skill, hook, agent ou commande ; règle qui change un comportement.
  - **x** : changement de structure (renommage de skill, déplacement de fichiers).
- `CHANGELOG.md` : tout va d'abord sous « Non publié ». À la release : PR `release/x.y.z` qui déplace ces lignes sous `## [x.y.z] - AAAA-MM-JJ` et monte les versions.
- Après le merge par Adrien : tag `builds-evo-vx.y.z` et release GitHub dont les notes reprennent **toute** la section du CHANGELOG (exhaustives, une ligne par changement).
- Sur le PC : `git pull` dans `C:\Project\claude-skills`, puis `/plugin marketplace update drien95`.
