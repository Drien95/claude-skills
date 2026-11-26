# 19. Pipeline et outillage

**Le domaine** : c'est la moitié du métier de technical artist : automatiser ce qui se répète (captures, mesures, contrôles, export) pour que l'artiste passe son temps à décider, pas à manipuler. Ce fichier est une **liste de recommandations** ; il ne modifie ni l'Atelier ni le banc.

## Principes clés

- **« Si quelque chose casse plusieurs fois, c'est un problème de pipeline, pas d'artiste »** (Ryan Amos, lead technical artist, 80.lv 2026).
- **Valider tôt** : déplacer les contrôles et les retours le plus tôt possible dans la chaîne ; conventions de noms et de dossiers ; documentation tenue à jour et facile à trouver (Amos).
- **Budgets écrits** : définir des budgets de coût (lumières, ombres, matériaux) et fournir des réglages réutilisables (Amos).
- **Rapports de profilage lisibles** : transformer les mesures en rapport « ce qui coûte, où, quoi corriger » (Amos).
- **Automatiser** la mise en place, la validation, le nettoyage et les contrôles de performance (Amos).
- **D'abord : « ce qu'on a est-il suffisant ? »** Si oui, ne pas toucher ; le sur-outillage nuit. Quatre bonnes raisons de changer un flux : gagner du temps, gagner en fiabilité, réduire le stress aux moments critiques, améliorer la qualité (Jodie Azhar, Creative Assembly, GDC 2018).
- **Observer l'utilisateur** pour repérer les étapes lentes ou répétitives qu'un outil peut supprimer (Azhar).
- **Prototype rapide** : un outil en script fonctionne en quelques jours (Robinson, Epic).

## Recommandations pour nos builds (à décider avec Adrien, rien n'est lancé)

Par ordre de gain probable :

1. **Planche de captures automatique** : au banc, les 3 vues de jugement de la pièce (et les points de vue de la salle) capturées toujours aux mêmes positions, assemblées en une planche côte à côte avec la version précédente, et **ouvertes sur l'écran d'Adrien** (règle existante). C'est la base de la méthode des 3 silhouettes (15).
2. **Rapport de mesure à chaque version** : posés (props + particules + lumières catalogue), ms du script, dessins/image, FPS, contrôle « rien hors de la boîte ». Un fichier texte court à côté du dupe. Le contrôle de boîte existe déjà (`controle_boite.py`).
3. **Contrôles automatiques avant test** (« lint » de build) : budget dépassé, coordonnées absolues dans le script, son de musique, playermodel/Hollow en décor, touche en dur. Les règles EVO déjà apprises deviennent des vérifications.
4. **Journal de build** : versions et heures par pièce (skill build-evo, `references/journal-mesure.md`). C'est ce qui prouvera que la méthode réduit les itérations.
5. **Bibliothèque de modules** : chaque sous-ensemble validé (garde, pilier, arche, grappe de débris) rangé avec capture, nombre de posés et dupe. Recherche par nom.
6. **Maquette three.js → banc** : exporter de la maquette les positions des caméras et la timeline des séquences, pour que le banc et le script reprennent les mêmes valeurs.

Ces outils peuvent vivre comme commandes de l'Atelier ou comme scripts du banc ; un hook Claude peut lancer les contrôles 2 et 3 automatiquement après chaque version (voir le futur repo de skills).

## Sources
- Ryan Amos, [Technical artist on building tools, pipelines and blending art with engineering](https://80.lv/articles/technical-artist-on-building-tools-pipelines-and-blending-art-with-engineering) (80.lv, 2026)
- GDC, [Speaker Q&A: Jodie Azhar on formalizing technical art processes](https://gdconf.com/news/speaker-qa-jodie-azhar-advocates-formalizing-technical-art-processes) (2018)
- Melissa Robinson, [Jobs in Unreal Engine: Technical Artist](https://www.unrealengine.com/tech-blog/jobs-in-unreal-engine---technical-artist) (Epic, 2018)
- Valve, [Draw call](https://developer.valvesoftware.com/wiki/Draw_call) (mesure par vprof_counters)
