# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions [semver](https://semver.org/lang/fr/) par plugin.

## Non publié
- Goûts d'Adrien (composition-scene) : arbres en aplat vert, lisière en sucettes, démarcation au sol refusés ; herbe et fleurs en script aimées (Sumii P1, 27/11/2026).
- Leçon (pieces-props, banc-gmod) : arbres nt absents du PC, cerisier teinté vert ; ajout de contenu au banc éclair sans relance (Sumii P1, 27/11/2026).
- Leçon (effets-scene-lua, pièges Lua) : cache du test de boîte par image ET par œil ; ciel complet dessiné dans `PreDrawSkyBox` (Sumii P1, 27/11/2026).
- builds-evo : pièges construction étalée en coroutine, allocations par image (ramasse-miettes), halo pondéré par `util.PixelVisible` (Sumii P1, 27/11/2026).

- builds-evo : pieges-lua, bandes claires sur des sphères Mesh() sans élimination des faces arrière : maillage à part en CullMode CW (Sumii P1 v28, 27/11).
- builds-evo : pieges-lua, `$color` ne recolore pas une texture verte, partir d'une texture neutre ; tige peinte dans la texture, recadrer les UV (Sumii P1 v23, 27/11).
- builds-evo : pieges-lua, 5 pièges de Sumii P1 v16 à v18 (texture absente en damier, cache de CreateMaterial, teinte des nuages qui dérivent, modèles client persistants, $color plafonné).
- builds-evo : catalogue-evo, chercher un modèle absent dans les pakfiles des maps (nt/props_nature dans rp_shinonome_evo) avant de le substituer (Sumii P1, 27/11).

### Leçons du script de Sumii et de son banc (27/11/2026, demande d'Adrien)
- `pieges-lua.md` : relais après effacement, état « déjà construit » au recollage, repère confondu avec une voisine, rechargement à chaud partiel.
- `procedure-banc.md` : GMod au premier plan pendant une série.
- `economie.md` : relire les réponses avant de questionner ; 400 posés est la seule limite.

### Garde-fous après Sumii (27/11/2026, demande d'Adrien)
La maquette three.js (étape 7) a été sautée sur le monde intérieur de Sumii : une passation a envoyé la session de build directement au banc.
- Hook `budget` : `banc_passe` et `banc_tester` refusés tant que `piece.json` n'a pas `maquette_validee` (date ou `dispense` sur la parole d'Adrien) ; l'état au début de session dit si la maquette est validée. Tests : `Maquette` (4).
- `build-evo/SKILL.md` : liste des étapes 0 à 15 posée sur la checklist au début de chaque build ou reprise, cochée seulement quand son fichier existe ; étape 7 (maquette) remontée dans la partie « Écrire et maquetter avant de construire », validée par Adrien avant tout GMod (le classement dans « Construire une pièce » a permis de la passer).
- Modèle de relais et `/builds-evo:relais` : ligne obligatoire « étapes faites et restantes ».
- `journal/mesures.md` : ligne ouverte pour Sumii, P1 (sol, fermeture, ciel couchant).
- `/builds-evo:nouvelle-piece` (champ `maquette_validee` dans `piece.json`) et `economie.md` (règle 1, sorties de secours) alignés.

### Rétro de conception de l'A2 (27/11/2026)
- `composition-scene/references/conception-scene.md` : ce qui a marché dans la conception de l'A2 (contrainte du moteur retournée en mécanique RP, accent rare, formes porteuses de sens, tout tracé depuis la pièce de tête, décor à 3 niveaux, son et silence dans la fiche), pourquoi elle a plafonné à 6 ou 6,5, et la méthode en 6 points dans la fiche DA, sans passe de banc en plus. Lien dans `composition-scene/SKILL.md` ; ligne datée dans `gouts-adrien.md`.

### Audit du 27/11/2026 (demande d'Adrien : « aucune régression »)
- Hook `budget` : « lire la planche, pas chaque capture » ne s'applique plus que pendant un build (`piece.json` présent) ; hors build (Atelier, séance MJ), lire une capture reste libre. Tests : `test_hors_build_lecture_libre`, `test_hors_arbre_du_build_lecture_libre`.
- `/builds-evo:lecon`, `/builds-evo:nouvelle-piece` et `capitaliser` : jamais de changement de branche dans `C:\Project\claude-skills` (le plugin installé en est tiré) ; le travail se fait dans un worktree à part, retiré après la PR.
- Copie versionnée du banc : `banc/banc.py` (copie du 27/11 du banc du PC, qui reste celui utilisé) et `banc/README.md` ; `banc_etat` signale en une ligne un banc du PC différent de la copie. Tests : `CopieDuBanc` (5).
- `pieces-props/references/regles-dupe-evo.md` : ligne « salle cachée dans un rocher » (Exequias, 18/11), reprise de la note OPTIMUS `gmod-dupe-regles` avant son allègement.
- Vérification GitHub : LuaJIT installé sous Linux, les 8 tests de `garde_lua` et de `banc_passe` ne sont plus sautés.

### Modifié
- `performance` : tout dessin et tout parcours d'entités côté client derrière le test de boîte ; recherche serveur = revalider d'abord ; pas d'allocation par image dans les sprites (audit de perf A2, 26/11).

### Ajouté
- Économie de jetons (demande d'Adrien, 26/11 : l'A2 a pris ~10 % de la semaine Max) : règles dans `build-evo/references/economie.md` (diagnostic de l'A2, 10 règles, ordres de grandeur, sorties de secours), section « Économie » de `build-evo/SKILL.md`.
- Hook `budget` (`hooks/budget.py`, 0 token) : passe du banc refusée sans cahier des charges validé (`cahier_valide` dans `piece.json`) ; 12 vues au plus par passe (`max_vues`) ; plafond de 5 passes sans point avec Adrien (`plafond_passes`, remis à 0 par son message) ; une critique par planche et une critique finale par passe ; lecture d'une capture refusée quand la planche existe (copie dans `zoom/` pour une vue de près) ; relais de session relu au démarrage ; jetons comptés par scène, pièce et modèle à la fin de chaque tour (`conso.json`), rapport `budget.py rapport`.
- Commandes `/builds-evo:cahier` (cahier des charges complet validé en un message, modèle `modeles/cahier-des-charges.md` : scène, jeu, livraison, budget de travail), `/builds-evo:relais` (passation de 2 Ko, modèle `modeles/relais.md`), `/builds-evo:conso`.
- Agents `passe-banc` (Sonnet : une passe d'après un ordre écrit, rapport de 10 lignes) et `critique-finale` (modèle fort, une fois par pièce, contre le cahier et la fiche).
- Contrôles gratuits : `outils/controle_auto.py` (lit un dupe AdvDupe2 rév. 5 ou un `scene.json` : 400 posés ou budget, classes bloquées, playermodels, modèles hors liste, doublons au même endroit, boîte, clé Frozen, props qui flottent d'après les bornes), lancé par `banc_passe` avant le collage (passe refusée sur erreur, rien n'est collé ; `controle: false` pour s'en passer) ; `outils/controle_livraison.py` (addon : `_tout_effacer`, aucune notification à l'écran, règles de `garde_lua`, gravure, `COMMANDES.md` et README complets, diag, bind).
- Ligne d'état : passes depuis le dernier point (« ⚠ point » au plafond), indice de consommation de la scène, « → /relais » à 60 % de contexte.

### Tests
- `tests/test_budget.py` (17 tests), `tests/test_controle.py` (10 tests), refus du contrôle auto dans `tests/test_mcp_banc.py`, ligne d'état (passes, indice, relais).

### Modifié
- Agents `critique-build` et `allegement` sur Sonnet (`model` dans l'en-tête) ; la critique lit la planche et le rapport du contrôle auto, réponse en 15 lignes au plus.
- `build-evo` : étape 0 cahier des charges, passes confiées à `passe-banc`, plafond de 5 passes, critique finale, relais en fin d'étape, consommation à la rétro ; `nouvelle-piece` écrit `cahier_valide`, `plafond_passes`, `max_vues` ; `retro` relève les jetons ; `banc-gmod` (Cadence) et `capitaliser` (où ranger un gaspillage) ; colonne « Indice » dans `journal/mesures.md`.
- `assemblage-livraison` : comment faire l'effacement total d'une scène (retrait par plan du dupe, registre des hooks client, serveur en veille), d'après `a2_tout_effacer` (A2, 26/11).
- `assemblage-livraison` : les scènes n'affichent aucune notification à l'écran (chat, `notification.*`, HUD), seulement du texte en console (Adrien, 26/11).
- `assemblage-livraison` : toute scène livre la liste complète de ses commandes (README, `COMMANDES.md`, note OPTIMUS) et une commande d'effacement total à double confirmation (props, gravure, effets, sons, état, timers, hooks), testée au banc (demande d'Adrien, A2, 26/11).
- `banc-gmod` : rangement des dupes (essais du banc dans `advdupe2/banc/`, finales dans un dossier par projet, anciennes versions dans `advdupe2_corbeille/`).

## [optimus 0.3.3] - 2026-11-27

### Modifié
- `/optimus:suivi` (demande d'Adrien) : relit tout l'historique du ticket et la section « Échanges » de la note avant un brouillon ; ne répète jamais ce qu'Adler a déjà envoyé, répond seulement au dernier message du joueur et à ce qui reste ; chaque message envoyé est noté dans « Échanges » avec son heure (Paris). Test : `test_ne_repete_pas_et_note_les_echanges`.

## [optimus 0.3.2] - 2026-11-27

### Modifié
- `/optimus:suivi` : grade minimum vérifié avec la grille des grades V1 (note `grades-v1` du coffre, optimus PR 18) : grade de la fiche converti (Shinigami ou Hollow, 1 à 16), noté dans `grade` ; un grade insuffisant est signalé à Adrien sans trancher, brouillon en suspens. Test : `test_grade_minimum_par_la_grille_des_grades`.

## [optimus 0.3.1] - 2026-11-27

### Modifié (décisions d'Adrien du 27/11/2026)
- `/optimus:suivi` : 72 h sans réponse du joueur = fermeture possible ; toute relance fixe `relance` à +72 h, l'échéance passée donne un brouillon de clôture puis le statut `abandonné`.
- `/optimus:suivi` : Reiryoku, d'abord la race ; l'école de l'Abîme (prérequis de la grille V1) vaut seulement pour les Arrancar, jamais Adler comme maître d'un Shinigami.
- `/optimus:suivi` : remplit `parcours`, `action` (30 caractères) et `priorite`, affichés par la vue Bases du coffre (optimus PR 15).
- `/optimus:suivi` : paliers jugés sur la grille des normes V1 (notes `grille-maitrise-v1` et `grille-maitrise-v1-soutien` du coffre, optimus PR 15) : section du parcours seulement, grade minimum, « Apprenti depuis 1 semaine », aiguiller sans donner la réponse.
- Tests : `test_fermeture_apres_72_h`, `test_ecole_de_l_abime_arrancar_seulement`, `test_paliers_sur_la_grille_v1`, `test_proprietes_de_la_vue`.

## [optimus 0.3.0] - 2026-11-27

### Ajouté
- Commande `/optimus:suivi <suivi ou texte collé>` (demande d'Adrien, 27/11/2026) : crée ou met à jour la note du suivi dans `06-lore/suivis/` du coffre (modèle `_modeles/suivi.md`, OPTIMUS PR 12), écrit un brouillon de réponse d'Adrien **en MJ, hors personnage** (jamais comme Adler), lie un build (`build: "[[...]]"`, note de chantier `en attente` créée au besoin), change le statut, puis contrôle à 0 jeton (`journal`, `index`, `passation`, `verifier`). Ne lit que la note du suivi ; rien n'est posté sur le panel staff. Pas de nouveau hook : le rappel de passation suffit. Tests : `tests/test_suivi.py` (4).

## [optimus 0.2.0] - 2026-11-27

### Ajouté
- Hook `Stop` `rappel_passation.py` : quand un fil a fait un `git commit` ou un `gh pr create` sans passation, la fin du tour est bloquée **une seule fois** avec la consigne de lancer `/optimus:passation <note>` (Adrien ne retient pas les commandes). Rien si la passation est faite (skill ou `optimus.py passation`), si le fil n'a rien livré, ou si le rappel a déjà eu lieu. Tests : `tests/test_rappel_passation.py` (8).

## [optimus 0.1.0] - 2026-11-27

### Ajouté
- Nouveau plugin `optimus` : commande `/optimus:passation <note>` (fin de fil sur un chantier du coffre : résumé, État, Passation, statut, maj, journal, index), contrôlée à 0 jeton par `python scripts/optimus.py passation <note>` du coffre (repo Drien95/optimus). Aucun hook.

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
