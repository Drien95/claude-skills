# claude-skills

Catalogue privé de plugins Claude Code d'Adrien (Drien95). Chaque plugin regroupe un domaine : on l'active ou on le coupe d'un clic, et ses hooks ne tournent que quand il est actif.

| Plugin | Contenu | État |
|---|---|---|
| `builds-evo` | builds GMod pour le serveur EVO : 6 skills de méthode, 3 commandes, 2 agents, hooks des interdits du banc et des scripts, serveur MCP du banc, ligne d'état | 0.2.0 |
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
| `retro` | `/builds-evo:retro <scène>` : rétro de 5 min en fin de build |

Chaque skill a un `SKILL.md` d'une page et des fiches dans `references/` (les 21 fiches de recherche sourcées du 26/11/2026 gardent leur numéro ; la table de correspondance est dans `build-evo/SKILL.md`).

**Agents** (chacun coûte de 10 000 à 30 000 tokens par passage, à lancer aux bons moments) :
- `critique-build` : note les captures d'une pièce sur la grille 7,5 sans connaître son historique, pour éviter les notes trop gentilles. À chaque planche de décision.
- `allegement` : propose une variante allégée d'une pièce à rendu égal (méthode du katana 100 → 50). Quand une pièce dépasse son budget.

**Serveur MCP `banc`** (outils chargés à la demande, rapports de quelques lignes) : `banc_etat`, `banc_tester`, `banc_nettoyer`, `banc_planche`, `banc_montrer`. Il enveloppe `sites\gmod-build\banc\banc.py` sans le modifier et applique lui-même les règles : jamais de focus, lancement en éclair seulement avec l'accord d'Adrien, un seul GMod gardé ouvert, collage loin du bâtiment central. Chemin du banc : variable `BANC_PY`. Pillow est nécessaire pour les planches. L'Atelier a déjà son propre MCP (`atelier\mcp_atelier.py`).

**Ligne d'état** (0 token) : `Lac noir › Cathédrale v10 · 218/400 posés · pièce 74/90 · planche 2/3 · note 7 ↓ · Opus · contexte 34 %`. Elle lit `.claude/builds-evo/piece.json`, écrit par `/builds-evo:nouvelle-piece` et tenu à jour par les fils.

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

Ligne d'état (les plugins ne peuvent pas la poser eux-mêmes), dans `%USERPROFILE%\.claude\settings.json` :

```json
"statusLine": { "type": "command", "command": "python C:/Project/claude-skills/plugins/builds-evo/statusline/ligne_etat.py" }
```

Vérifier que tout est chargé : `/plugin` (onglet Installed), `/hooks` et `/mcp` (serveur `banc`).

## Amélioration continue (5 règles, validées le 26/11/2026)

1. **Capturer chaque erreur tout de suite** : `/builds-evo:lecon` après chaque correction ; l'erreur devient une ligne dans le bon skill, sur une branche, pour la PR d'Adrien.
2. **Rétro de 5 min en fin de build** (`/builds-evo:retro`) : ce qui a coûté le plus de versions, ce qui a marché, ce qui manquait ; le journal de mesure dit si on progresse.
3. **Promouvoir ce qui revient** : une erreur vue 2 fois devient un hook ; une méthode qui marche 3 fois monte dans la checklist d'une page.
4. **Ménage tous les 3 ou 4 builds** : supprimer les règles mortes ou en double. Un skill court et à jour vaut mieux qu'un gros.
5. **Bibliothèque de pièces validées** (`pieces-props/references/bibliotheque.md`) : chaque build part de plus haut que le précédent.

## Travailler sur le repo

Voir [CONTRIBUTING.md](CONTRIBUTING.md) : branche + PR, Adrien merge, release + tag, notes de version exhaustives ; chaque erreur corrigée en build devient une ligne dans le bon skill. Tests : `python -m unittest discover -s tests`. Validation : `claude plugin validate plugins/builds-evo`.

## Journal de mesure

[`journal/mesures.md`](journal/mesures.md) : une ligne par pièce (versions, planches, heures, posés, note). Objectif : ≤ 10 versions et ≤ 3 planches par pièce, note ≥ 7,5.
