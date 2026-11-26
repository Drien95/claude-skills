# Copie versionnée du banc

`banc.py` est la copie du banc de test GMod d'Adrien, prise le 27/11/2026 (sha1 `b1ec30cc…`) sur le PC :
`C:\Project\Adler_lore\sites\gmod-build\banc\banc.py`. **Le banc utilisé reste celui du PC** (variable `BANC_PY`) : ce fichier ne sert qu'à garder l'historique et à revenir en arrière.

- `banc_etat` (serveur MCP `banc`) signale en une ligne quand le banc du PC diffère de cette copie.
- Après une modification voulue du banc : recopier le fichier ici par une PR (méthode de `/builds-evo:lecon`, dans un worktree à part), avec une ligne dans `CHANGELOG.md`.
- Pour revenir à une version : `git log -- plugins/builds-evo/banc/banc.py`, puis recopier la version voulue sur le PC avec l'accord d'Adrien.
