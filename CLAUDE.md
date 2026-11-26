# claude-skills : consignes pour Claude

Repo privé d'Adrien : catalogue de plugins Claude Code (`.claude-plugin/marketplace.json`), un dossier par plugin dans `plugins/`. Adrien écrit en français : réponds en français.

- Ne jamais commit sur `main` : branche + PR, Adrien merge (voir CONTRIBUTING.md).
- Toute modification d'un plugin : ligne dans `CHANGELOG.md` sous « Non publié ».
- Versions : `plugin.json` et l'entrée du `marketplace.json` toujours égales.
- `SKILL.md` = une page ; le détail dans `references/`. Ne pas renuméroter les fiches 01 à 21 (elles se citent par numéro).
- Un hook = un script Python (bibliothèque standard, Windows) + ses tests dans `tests/`.
- Avant une PR : `python -m unittest discover -s tests` et `claude plugin validate plugins/builds-evo`.
- Pas de secret ni de clé d'API.
