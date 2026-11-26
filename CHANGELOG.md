# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions [semver](https://semver.org/lang/fr/) par plugin.

## Non publié

## [builds-evo 0.1.0] - 2026-11-26

### Ajouté
- Catalogue de plugins `drien95` (`.claude-plugin/marketplace.json`) avec le plugin `builds-evo`.
- Skill `build-evo` : checklist d'un build en une page (écrire avant de construire, boucle d'une pièce, contrôle, arrêt à 7,5/10, règles EVO permanentes), table des 21 fiches de recherche ; références `grille-controle.md`, `boucle-piece.md`, `journal-mesure.md`, `capitaliser.md`, fiches 15 (itérations), 19 (pipeline), 21 (critique) ; modèles `fiche-da.md` et `fiche-piece.md`.
- Skill `composition-scene` : 5 pratiques prioritaires, règles EVO (gigantisme, infini, lumières) ; référence `gouts-adrien.md` ; fiches 01, 02, 03, 05, 10, 11, 12, 13, 17.
- Skill `pieces-props` : règles dures du collage EVO, méthode, checklist avant envoi ; références `regles-dupe-evo.md`, `catalogue-evo.md`, `recettes-pieces.md` ; fiches 04, 16, 20.
- Skill `effets-scene-lua` : règles dures (touches, coordonnées, musique, boîte), méthode ; références `pieges-lua.md`, `recettes-effets.md`, `assemblage-livraison.md`, `performance.md` ; fiches 06, 09.
- Skill `mise-en-scene` : courbe, révélation, séquences, son, caméra, fiche MJ ; référence `cinema-entrees.md` ; fiches 07, 08, 14, 18.
- Skill `banc-gmod` : interdits du banc, commandes usuelles ; références `procedure-banc.md`, `filmer.md`.
- Commandes `/builds-evo:nouvelle-piece` (fiche de pièce + ligne du journal) et `/builds-evo:lecon` (leçon rangée dans le bon skill, par PR).
- Agent `critique-build` : note indépendante sur la grille 7,5, sans historique.
- Hook `garde_banc` (PreToolUse Bash, PowerShell, device_bash) : bloque `--focus`, les lancements sans `--eclair` et les lancements directs de GMod ; demande l'accord avant d'ouvrir ou de fermer GMod.
- Hook `garde_lua` (PreToolUse / PostToolUse sur `.lua`) : bloque les touches en dur, les coordonnées de la zone de build et la musique ; signale les `Vector` très loin du repère.
- Tests des hooks et de la cohérence des versions (`tests/`), vérification GitHub sur chaque PR.
- Journal de mesure `journal/mesures.md`, README, CONTRIBUTING.
