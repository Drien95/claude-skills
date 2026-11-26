# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions [semver](https://semver.org/lang/fr/) par plugin.

## Non publié

### Modifié
- `assemblage-livraison` : toute scène livre la liste complète de ses commandes (README, `COMMANDES.md`, note OPTIMUS) et une commande d'effacement total à double confirmation (props, gravure, effets, sons, état, timers, hooks), testée au banc (demande d'Adrien, A2, 26/11).

### Modifié
- `banc-gmod` : rangement des dupes (essais du banc dans `advdupe2/banc/`, finales dans un dossier par projet, anciennes versions dans `advdupe2_corbeille/`).

## [builds-evo 0.3.0] - 2026-11-26

### Modifié
- Brique commune « gravure d'usine » : `outils/gravure.py` (3 marques tirées de l'identifiant de la scène, JSON et table Lua), module `outils/gravure_lua/sh_gravure.lua` (lecture côté serveur et client), doc dans `outils/README.md`, tests `tests/test_gravure.py`. Première scène : A2 v15 (banc : build tourné reconnu 3/3, marque retirée 2/3).
- Rétro A2 (26/11) : critique qui plafonne (3 séries au même plafond, faire juger Adrien en jeu ou en film) ; rééclairage de nuit des props limité à la boîte ; ancre par motif de props (Lac noir muet sur EVO, 9 plaques pareilles dans l'A2) ; appel protégé après copie à chaud d'un nouveau fichier partagé ; collisions des pièces dessinées en script par blocs invisibles ; contrôle gel/collisions avant livraison ; état partagé versionné et rattrapage à l'entrée dans la boîte. Journal de mesure A2 complété.
- Pièges Lua : masquage client d'un prop réseau à vérifier par trace (`SetNoDraw` remis à zéro par le serveur) ; bords nets des décals sur le sable, remplacés par une bosse du vrai sable (A2, 26/11).
- Note d'état OPTIMUS devenue tableau de bord Obsidian natif (sans plugin) : encadré par scène (avancement x/N pièces validées, jauge des posés /400), encadré par pièce coloré par la note (vert dès 7,5, orange dès 6, rouge, gris si pas notée) avec barres de note et de posés, vignette de la dernière planche (`03-builds/vignettes/`, exclue de git en local), historique. Données dans un commentaire `%% banc %%`, taille gardée sous 4 Ko. Nouveau champ facultatif `pieces_scene` dans `piece.json`.

### Ajouté
- `pieges-lua` et `recettes-pieces` : couches superposées d'un maillage (écart ≥ 0,3 u + `$decal`), diagnostic des fragments, autorefresh muet (bascule + trace de chargement).
- `banc_passe` (serveur MCP du banc) : une passe en un appel (générer, contrôler et installer les scripts, rechargement à chaud, coller + vues, console lue, planche, ouvrir, nettoyer) ; planche refusée si erreur Lua dans la console ; temps de chaque étape.
- LuaJIT cherché hors du dossier courant (garde_lua, banc_passe).
- `garde_lua` (après écriture) : avec LuaJIT, signale une erreur de syntaxe et un nom déclaré `local` lu comme globale (fonction appelée avant sa déclaration).
- `banc-gmod` : planche invalide si erreur Lua dans la console ; critiques sur Sonnet.
- `pieges-lua` : `pcall` autour des hooks de dessin.
- `build-evo` : la fermeture de la scène (ciel, brume, lumière clé) se pose avant de juger sol, dunes et lointains.
- Outils de build `plugins/builds-evo/outils/` : `faire_bornes.py` et `bornes_modeles.json` (bornes de 1 571 modèles autorisés, PHX lus dans le VPK de GMod, autres tirés de geo_catalogue ; chemins réglables par `--autorises`, `--geo`, `--vpk`, `--sortie`, `CATALOGUE_BUILD`, `GMOD_DIR`), générateur de dunes `dunes/dunes.py` (paramètres JSON vers dupe AdvDupe2, script client de sable drapé et vues du banc ; vérification des PHX par la spawnlist ou, sans GMod, par `bornes_modeles.json`), README d'usage. Tests `tests/test_outils.py` sans GMod.
- `pieces-props` : recette du sol de sable (A2) : surface en script sur des plaques, matières de dupe à éviter pour le sable, pièges du maillage (étoile polaire, rides en cible).
- `banc-gmod` : section Cadence (un collage, vues en lot, critique unique, temps mesuré).

- `banc_planche` écrit après chaque planche la note `03-builds/etat-builds.md` du coffre Obsidian OPTIMUS (`mcp/etat_optimus.py`, 0 token) : pièce, version, note, posés sur 400, lien vers la dernière planche, heure, 10 dernières planches. Lit le même `piece.json` que la ligne d'état. Coffre réglable par `OPTIMUS_DIR`, pièce par `BUILDS_EVO_PIECE`. Index du coffre régénéré à la création de la note. Obsidian Git la pousse sur main.
- README : le serveur MCP `banc` met à jour le tableau de bord OPTIMUS après chaque planche.
- `build-evo/references/boucle-piece.md` : `piece.json` à jour AVANT la planche, pour que le tableau de bord OPTIMUS montre la bonne note.
- `journal/mesures.md` : lignes de l'A2 (heures, versions, planches, posés, note).

### Tests
- `tests/test_gravure.py` (6 tests : déterminisme, écarts et zone, lacets et couleurs improbables, refus, sortie JSON et Lua de la CLI).
- `tests/test_etat_optimus.py` : tableau de bord OPTIMUS (encadrés, couleurs par note, jauges, taille sous 4 Ko).
- `tests/test_outils.py` : bornes des modèles et générateur de dunes, sans GMod.
- `tests/test_hooks.py` : `garde_lua` avec LuaJIT (syntaxe, locale lue comme globale).
- `tests/test_mcp_banc.py` et faux banc `tests/faux/banc.py` : `banc_passe` (console lue, planche refusée sur erreur Lua, temps des étapes).

### Corrigé
- Frontmatter YAML de 6 skills (`banc-gmod`, `composition-scene`, `mise-en-scene`, `nouvelle-piece`, `pieces-props`, `retro`) : descriptions mises entre guillemets ; le « : » dans le texte cassait la lecture et les skills se chargeaient sans métadonnées.

## [builds-evo 0.2.0] - 2026-11-26

### Ajouté
- Serveur MCP `banc` (`mcp/banc_mcp.py`, déclaré dans `.mcp.json`) qui enveloppe `banc.py` sans le modifier : `banc_etat`, `banc_tester` (jamais de focus, lancement seulement avec `accord_adrien`, toujours en éclair, GMod gardé ouvert, collage à y = -8000 par défaut), `banc_nettoyer`, `banc_planche` (planche simple ou avant/après), `banc_montrer` (ouvre les planches sur l'écran d'Adrien). Chemin du banc réglable par `BANC_PY`.
- Agent `allegement` : variante allégée d'une pièce à rendu égal (invisible, fusion, matière, Gestalt, script, gros modèle EVO), sans toucher à l'original.
- Ligne d'état (`statusline/ligne_etat.py`) : scène, pièce, version, posés/400, posés de la pièce/budget, planche, note (flèche sous 7,5), modèle, contexte. 0 token. Lit `.claude/builds-evo/piece.json`.
- Commande `/builds-evo:retro` : rétro de 5 min en fin de build (journal, 3 leçons, ménage).
- Les 5 règles d'amélioration continue validées par Adrien (README, `build-evo/references/capitaliser.md`, CONTRIBUTING) : leçon immédiate, rétro, promotion (2 fois → hook, 3 fois → checklist), ménage tous les 3-4 builds, bibliothèque de pièces.
- Bibliothèque de pièces validées (`pieces-props/references/bibliotheque.md`), amorcée avec les pièces du Lac noir, Azeno et le sceau de l'Exequias.
- Tests du serveur MCP (avec un faux banc) et de la ligne d'état ; Pillow installée dans la vérification GitHub pour tester les planches.

### Modifié
- `build-evo` : étapes qui citent la bibliothèque, l'état de pièce, les outils MCP du banc, les agents `critique-build` et `allegement`, la rétro.
- `banc-gmod` : table des outils MCP, à préférer aux commandes.
- `/builds-evo:nouvelle-piece` écrit aussi l'état de la ligne d'état et regarde la bibliothèque ; `/builds-evo:lecon` compte les répétitions et propose les promotions.

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
