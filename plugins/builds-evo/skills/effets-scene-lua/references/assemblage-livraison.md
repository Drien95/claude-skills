# Assembler la scène et la livrer

## Boîte relative (règle Azeno, 25/11)
- Où qu'on colle le build, il a sa boîte h × L × l FIXE relative au **prop repère** du dupe. Repérage une fois par seconde sur ce prop ; tout ce qui vient de props figés (positions, axes) est mis en cache à ce moment.
- Jamais de coordonnées de map, même pour un wipe : le build est cherché autour du joueur ou par le repère.
- Tester au banc aux **vraies coordonnées de la zone** (une démo posée plus bas a masqué le plafond).
- Le banc a sa copie (porte flatgrass) ; la livraison garde la porte de la vraie map.

## Script de scène
- Un seul `build.py` de scène qui génère le script final par patchs `rep()` (chaque ancre présente une seule fois, sinon assert) ; un bloc `bloc_vNN.py` par retouche.
- Chaque pièce = un module (table + fonctions), à cause des 200 locales.
- Séquences en temps brut, commandes suivante / précédente / aller à N ; chaque séquence tient sa dernière image.

## Addon serveur
- `lua/autorun/<nom>_init.lua` (vérifie la map, `AddCSLuaFile`, `include`) + `lua/<nom>/sh_config.lua`, `sv_*.lua`, `cl_scene.lua` ; sons dans `sound/<nom>/` envoyés par `resource.AddFile`.
- Droits : `IsAdmin` + SteamID listés dans `sh_config`, revérifiés côté serveur ; convar d'accès. Joueurs qui arrivent en cours : état envoyé après `PlayerInitialSpawn`.
- Commandes : lancer, stop, séquence suivante/précédente/N, effacer (avec confirmation dans les 15 s). README avec `bind` suggérés, jamais imposés.
- Adrien a l'autorisation du staff pour un addon serveur ; le test final se fait sur EVO par le staff.

## Livraison
- Dossier `<création>/` dans `Drien95/creations-evo` (README, dupe.txt, scenario.md, addon) par PR.
- Vérifier qu'une PR n'est pas déjà mergée avant d'y pousser ; sinon nouvelle PR depuis main.
- Map protégée par son vendeur (Hueco) : pas de test local, ne jamais contourner. Recréer la zone sur flatgrass pour juger.
