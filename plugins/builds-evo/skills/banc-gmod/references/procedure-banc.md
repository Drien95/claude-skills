# Procédure du banc (vérifiée du 16 au 26/11/2026)

## Lancer une série
1. Demander l'accord d'Adrien si GMod n'est pas déjà ouvert.
2. Un seul GMod sur gm_flatgrass solo, mode éclair. `gmod.exe -hijack ... +map gm_flatgrass` charge la carte dans un GMod déjà ouvert (c'est le banc qui le fait).
3. Hors focus, GMod ne dessine les props que si ce processus les a déjà dessinés une fois avec le focus : un build « contenu » (un exemplaire de chaque modèle), un seul passage au premier plan de 3 à 5 s avec l'accord d'Adrien, focus rendu (`banc.gmod_en_bas()`), puis toutes les tâches sans `--lancer` ni `--focus` dans ce même GMod. Un GMod neuf par tâche = captures vides.
4. Un GMod éclair n'a que le contenu de son build. Un modèle ajouté en cours de série (Sumii P1, 27/11/2026) : copier ses fichiers dans `addons/banc_contenu` SANS vider le dossier (`eclair.besoins` + `eclair._ecrire` sur le nouveau dupe) ; GMod le trouve au collage suivant, sans relance.
5. Vérifier sur une capture que le script est chargé AVANT la série.

## Où coller
- Loin du bâtiment central de gm_flatgrass : `--y -8000` pour une pièce, `--x 9000` pour un build de plus de 4 000 u ; vérifier sur les captures qu'il ne traverse rien.
- Pour tester le ciel 3D et le plafond : aux **vraies coordonnées de la zone de build** (coins (-15287, -7291, 14109) et (-7193, -15584, 16054) ; plafond à ~330 u de la limite du monde ±16 384). Ces coordonnées servent au banc, jamais dans un script de scène.

## Photos d'une pièce
- Forme en plein jour, dalle claire, joueurs repères (Kleiner) pour l'échelle ; effets de nuit.
- 10 à 13 vues fixes : face, dos, 2 côtés, profil strict, 3/4 gauche et droit, de près, hauteur de joueur, contre-plongée, plongée, de loin ; vue de départ toujours sur la pièce.
- Photos hors focus : rendu dans une cible hors écran depuis Think (`render.Capture` rend nil sans focus). Le script de démo peut prendre ses propres captures.
- Planche : toutes les vues en une image, avant/après, rangée dans `assets/<pièce>/<passe>/` et ouverte sur l'écran d'Adrien.
- Démo jouée en direct dans GMod sans voler le focus : format apprécié pour juger les sous-effets.

## Après
- Rangement des dupes (26/11/2026) : le banc copie ses essais dans `data/advdupe2/banc/` (vidable sans risque). Les versions finales vont dans un dossier par projet (`data/advdupe2/<projet>/`, ex. `a2-sable-du-fond/`, `lac-noir/`), jamais à la racine ; les anciennes versions dans `data/advdupe2_corbeille/`, hors du menu AdvDupe2.
- Nettoyer la map (`gmod_admin_cleanup`, ou une tâche avec un dupe inexistant : `game.CleanUpMap` passe avant la lecture du dupe).
- Retirer du banc les scripts des autres pièces pendant un essai (`_claude_stage/retires/`) : ils s'accrochent à la plaque repère.

## Sessions distantes
- Exiger un signe à chaque étape, au moins toutes les 3 minutes ; sans nouvelle depuis 3 minutes, interroger la session (ne pas la couper en pleine pièce).
- Ne jamais dire « ça tourne » sans preuve (capture, fichier, ligne de log).
- Décider avant combien d'essais on fait, puis s'arrêter et donner à Adrien la marche à suivre.
- Piège : un `device_commit_files` juste après une écriture dans `/mnt/project-files` peut déposer l'ANCIENNE version : attendre ~10 s et vérifier le md5 sur le PC avant de lancer.

## Solo seulement (pas sur EVO)
Limites de base : `sbox_maxprops 300; sbox_maxlights 20; sbox_maxlamps 10; sbox_maxemitters 20; sbox_maxeffects 50`. `MakeLight`/`MakeLamp` inversent `Toggle` : écrire `Toggle = false`.
