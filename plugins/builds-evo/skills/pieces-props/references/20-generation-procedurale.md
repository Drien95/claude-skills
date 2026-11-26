# 20. Génération par script (procédural)

**Le domaine** : générer par règles (et un peu de hasard) ce qu'on poserait à la main : rochers, piques, débris, colonnades, ruines. Bien fait, c'est un gain de temps énorme et de la variété gratuite. Mal fait, c'est « dix mille bols de porridge » : beaucoup de variantes que personne ne distingue.

## Principes clés

- **Cinq étapes pour un générateur** : comprendre l'espace de design, lister les contraintes, comprendre le processus (comment un artiste le ferait), choisir la méthode, itérer (Kate Compton, GDC 2017, rapporté par Katherine Cross).
- **Réduire la portée** : « je ne peux pas générer un roman, mais je peux générer un roman de fantasy urbaine de gare » (Compton). Pour nous : pas « un décor », mais « une grappe de piques d'os ».
- **Le catalogue des méthodes** : tuiles, grammaires (règles de composition), distribution aléatoire (Compton).
- **« Barnacling »** (bernaches) : placer des objets moyens contre les gros, puis des petits contre les moyens, pour une hiérarchie naturelle (Compton). C'est la règle des grappes du set dressing (04).
- **Choisir les bonnes graines** : *Spore* gardait une liste blanche de graines qui donnaient de belles planètes. « Pas besoin de faire ça proprement, fais ce qui marche » (Compton).
- **Problème des 10 000 bols de porridge** : peu de résultats vraiment distincts valent mieux que beaucoup d'indiscernables (Compton).
- **Distribution de Poisson** : le hasard uniforme fait des tas et des trous ; l'échantillonnage en disque de Poisson (Bridson, 2007) garantit une distance minimale entre deux objets. Une distribution par taille d'objet (serrée pour l'herbe, lâche pour les arbres) et une probabilité par type de sol (gregouar, GameDev.net 2020).
- **Rochers procéduraux** : forme de base simple + bruit (Worley pour la forme principale, autres bruits pour le détail) ; paramètres exposés et préréglages sauvegardés (Yvo von Berg, 80.lv 2016).
- **Le procédural sert la direction artistique** : chez EA SEED (PICA PICA), direction artistique et système procédural ont été conçus ensemble dès le début ; 3 artistes ont fait un système de placement fonctionnel en moins de 2 mois (Anastasia Opara, CEDEC 2018).

## Application GMod / EVO (recommandations)

Deux usages, très différents en coût :

**A. Générer des posés (dupe)** : un script hors jeu (Python, comme les outils du banc) produit un dupe AdvDupe2 à partir de règles.
- Bon pour : colonnades, escaliers, enceintes de rochers, champs de piques, ruines répétitives.
- Règles : un vocabulaire de 3-6 props EVO, une graine (pour refaire exactement le même résultat), distribution de Poisson, « barnacling » gros → moyens → petits, rotations et échelles dans des plages bornées, **budget de posés comme limite dure**.
- Sortie : 6 à 9 variantes en planche (graines différentes), on garde les 1 à 3 meilleures (liste blanche, comme *Spore*).

**B. Générer en script client (hors budget)** : le script de scène dessine des ClientsideModels ou des sprites selon des règles.
- Bon pour : débris lointains, piques du ciel 3D, cendres, champs de cristaux, tout ce qui n'a pas besoin de collision.
- Toujours avec graine fixe (même décor pour tous les joueurs), tout relatif au repère du dupe, coupé quand aucun joueur n'est dans la boîte.

Garde-fous : le générateur ne remplace pas la composition (le point focal reste posé à la main) ; on génère la **masse**, on compose le **héros**. Et on vérifie le résultat avec la grille de contrôle (skill build-evo, `references/grille-controle.md`) comme pour tout le reste.

## Sources
- Katherine Cross, [Practical procedural generation for everyone](https://www.gamedeveloper.com/design/practical-procedural-generation-for-everyone-) (2017, talk de Kate Compton) ; GDC Vault [Practical Procedural Generation for Everyone](https://gdcvault.com/play/1024213/Practical-Procedural-Generation-for)
- gregouar, [Poisson disk sampling for random entities placement](https://gamedev.net/blogs/entry/2270025-poisson-disk-sampling-for-random-entities-placement) (GameDev.net, 2020)
- Yvo von Berg, [Procedural rocks in games](https://80.lv/articles/yvo-von-berg-procedural-rocks-in-games) (80.lv, 2016)
- EA SEED, [CEDEC 2018: Functional symbiosis of art direction and proceduralism](https://www.ea.com/seed/news/cedec-2018-functional-symbiosis-of-art-direction-and-proceduralism)
- Guerrilla Games, [GPU-based procedural placement in Horizon Zero Dawn](https://www.slideshare.net/guerrillagames/gpubased-procedural-placement-in-horizon-zero-dawn) (GDC 2017)
