# claude-skills

Catalogue privé de plugins Claude Code d'Adrien (Drien95). Chaque plugin regroupe un domaine : on l'active ou on le coupe d'un clic, et ses hooks ne tournent que quand il est actif.

| Plugin | Contenu | État |
|---|---|---|
| `builds-evo` | builds GMod pour le serveur EVO : 6 skills de méthode, 2 commandes, 1 agent critique, hooks des interdits du banc et des scripts | 0.1.0 |
| `mj-evo` | maîtrise MJ, personnage d'Adler, souffleur | prévu |

## Ce que fait `builds-evo`

**Skills** (chargés seulement quand la tâche en a besoin ; au démarrage, seules leurs descriptions coûtent des tokens, environ 550 en tout) :

| Skill | Quand Claude s'en sert |
|---|---|
| `build-evo` | chef d'orchestre : ordre des étapes, quel skill charger, quand demander l'avis d'Adrien, quand s'arrêter (7,5/10) |
| `composition-scene` | fiche DA, point focal, lumière clé, couleur, gigantisme, infini, goûts d'Adrien |
| `pieces-props` | build.py, règles du collage EVO, 400 posés, matériaux, allègement, recettes |
| `effets-scene-lua` | script Lua de scène : effets, pièges Lua, boîte relative, perf, livraison serveur |
| `mise-en-scene` | courbe de séquence, révélation, caméra et films, son sans musique, fiche MJ |
| `banc-gmod` | toute commande qui lance, pilote, filme ou ferme GMod |
| `nouvelle-piece` | `/builds-evo:nouvelle-piece <scène> <pièce>` : fiche de pièce + ligne du journal |
| `lecon` | `/builds-evo:lecon <ce qui s'est passé>` : range une erreur corrigée dans le bon skill, par PR |

Chaque skill a un `SKILL.md` d'une page et des fiches dans `references/` (les 21 fiches de recherche sourcées du 26/11/2026 gardent leur numéro ; la table de correspondance est dans `build-evo/SKILL.md`).

**Agent** `critique-build` : note les captures d'une pièce sur la grille 7,5 sans connaître son historique, pour éviter les notes trop gentilles. À lancer à chaque planche de décision.

**Hooks** (0 token, ils tournent sur le PC et ne parlent que pour bloquer) :

| Hook | Bloque | Demande l'accord d'Adrien |
|---|---|---|
| `garde_banc` (commandes Bash, PowerShell, device_bash) | `--focus` ; lancer GMod par le banc ou l'Atelier sans `--eclair` ; lancer `gmod.exe`, `hl2.exe` ou Steam app 4000 à la main | ouvrir un nouveau GMod (`--lancer --eclair`) ; fermer GMod |
| `garde_lua` (écriture d'un `.lua`) | touches en dur (`KEY_*`, `input.IsKeyDown`, `PlayerButtonDown`…) ; coordonnées de la zone de build du serveur ; musique (`sound.PlayURL`, chemins `music/`, `ost`, `bgm`…) | rien ; il signale seulement un `Vector` littéral très loin du repère |

Couper un hook ponctuellement, avec l'accord d'Adrien : variable d'environnement `BUILDS_EVO_HOOKS_OFF=garde_banc` (ou `garde_lua`, ou les deux séparés par une virgule).

## Installation sur le PC (Windows)

Prérequis : Claude Code, Git, Python 3.8+ accessible par `python`.

```powershell
cd C:\Project
git clone https://github.com/Drien95/claude-skills.git
```

Puis, dans Claude Code :

```
/plugin marketplace add C:\Project\claude-skills
/plugin install builds-evo@drien95
```

Le catalogue pointe sur le clone local : après un `git pull` (une PR mergée), `/plugin marketplace update drien95` recharge la nouvelle version. Les commandes `/builds-evo:lecon` et `/builds-evo:nouvelle-piece` écrivent dans ce clone (`CLAUDE_SKILLS_REPO` si le clone est ailleurs).

Vérifier que tout est chargé : `/plugin` (onglet Installed) et `/hooks`.

## Travailler sur le repo

Voir [CONTRIBUTING.md](CONTRIBUTING.md) : branche + PR, Adrien merge, release + tag, notes de version exhaustives ; chaque erreur corrigée en build devient une ligne dans le bon skill. Tests : `python -m unittest discover -s tests`. Validation : `claude plugin validate plugins/builds-evo`.

## Journal de mesure

[`journal/mesures.md`](journal/mesures.md) : une ligne par pièce (versions, planches, heures, posés, note). Objectif : ≤ 10 versions et ≤ 3 planches par pièce, note ≥ 7,5.
