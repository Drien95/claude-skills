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
- État partagé (A2, 26/11/2026) : le serveur tient l'état complet et un numéro de version ; il l'envoie aux joueurs dans la boîte qui n'ont pas la dernière version (relevé toutes les 0,5 s) : celui qui arrive ou entre dans la boîte est rattrapé ; le client redemande l'état à `InitPostEntity`. Sons rejoués seulement si l'événement vient de partir.
- Ancre par motif de props et commandes `ancre` (MJ) et `diag` (joueur) : voir `pieges-lua.md`.
- Commandes : lancer, stop, séquence suivante/précédente/N, effacer (avec confirmation dans les 15 s). README avec `bind` suggérés, jamais imposés.
- Toujours livrer (règle d'Adrien, A2, 26/11/2026) : (1) la liste complète des commandes, dans le README et dans un `COMMANDES.md` à part, en tableau « nom | arguments | qui peut la taper | ce qu'elle fait | exemple », plus la même liste dans la note OPTIMUS du build ; (2) une commande d'effacement TOTAL à double confirmation en 10 s (`<nom>_tout_effacer`) : supprime les props du build repéré et sa gravure (jamais ceux d'un autre build), vide l'état, les timers et les hooks côté serveur, et chez tous les clients les effets, particules, ClientsideModels, sons, maillages et ambiance ; le `diag` montre ensuite « aucun build, rien d'actif ». Distinguer clairement dans le README remise à zéro de séquence, retrait du build et effacement total. Test au banc : un build voisin reste intact, 0 hook ni timer restant.
- Adrien a l'autorisation du staff pour un addon serveur ; le test final se fait sur EVO par le staff.

## Livraison
- Dossier `<création>/` dans `Drien95/creations-evo` (README, dupe.txt, scenario.md, addon) par PR.
- Vérifier qu'une PR n'est pas déjà mergée avant d'y pousser ; sinon nouvelle PR depuis main.
- Avant de livrer (A2, 26/11/2026, question d'Adrien) : dupe figé (aucune clé `Frozen`), rien de mobile donc pas de bruit de props ni de soudure utile, collisions vérifiées au banc par trace (assises qui portent, décor traversable), puis perma par le staff (PermaProps).
- Map protégée par son vendeur (Hueco) : pas de test local, ne jamais contourner. Recréer la zone sur flatgrass pour juger.
