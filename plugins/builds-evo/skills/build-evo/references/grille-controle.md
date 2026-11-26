# Grille de contrôle (≥ 7,5/10 avant la pièce suivante)

À appliquer à chaque passe, vue par vue, sur des captures réelles (jamais sur des images pas encore faites). Une note par vue, défauts listés un par un. Seuil : 7,5/10 pour la forme ET pour les effets/sous-effets.

## 0. Fonction de base (avant tout le reste)
- L'objet fait-il ce qu'il est ? Siège : assise à hauteur de genou, dossier, deux accoudoirs, posé au sol, profil lisible. Épée : lame, garde, poignée, pointe. Un « cadre dans le vide » est un échec, quelle que soit l'ambiance (leçon du trône C1, 25/11).

## 1. Image (composition)
- [ ] Le point focal se trouve en < 2 s sur une capture réduite en noir et blanc, yeux plissés.
- [ ] 3 plans lisibles (premier plan sombre qui cadre, milieu = sujet, fond clair et brumeux).
- [ ] Une couleur domine, l'accent n'existe qu'à 1 ou 2 endroits.
- [ ] Silhouettes lisibles contre le fond (valeurs opposées).
- [ ] Rien de « carré par défaut » : chaque grosse forme a une variation (inclinaison, rupture, ruine). Pas « un immeuble », pas « debug » : pas de grands pans lisses, pas de blocs nus, pas de symétrie parfaite.
- [ ] Chaque usure ou débris a une cause ; au moins 1 détail raconte quelque chose.
- [ ] Une seule lumière clé claire ; le reste est subordonné.

## 2. Construction (vues dédiées)
| Critère | Comment on le vérifie |
|---|---|
| Remplit le cadre, se lit de loin | vue de loin et depuis la position des joueurs |
| Rien ne flotte | bornes réelles + vue 3/4 basse ; le build fait un assert (centre ≥ sol) |
| Profil lisible | profil strict : une façade ne doit pas être une feuille |
| Pas de PHX visible | vues de dessus et de dos |
| Pas de joint, z-fight ni fente | vue rasante sur les joints |
| Praticable | dessus plat, marches de 14 à 15 u, passages debout et accroupi |
| Dans la boîte | contrôle de boîte (code 1 si un élément sort) |
| Couloir des caméras libre | aucune pièce ne bouche les plans prévus |

## 3. Effets et son
- [ ] Hiérarchie : 1 effet primaire à la fois ; un temps fort précédé d'un calme.
- [ ] Anticipation → pic tôt → dissipation.
- [ ] Ambiance sonore en couches, sans musique, qui se tait avant le sommet.

## 4. Coût
- [ ] Posés ≤ budget de la pièce (et ≤ 400 pour la scène), coût script mesuré (ms, dessins/image, 1 % pire), rien hors de la boîte.

## Barème indicatif
- 5 : l'objet est reconnaissable mais « posé », plat ou bricolé.
- 6 : lisible, mais un défaut saute aux yeux sur au moins une vue.
- 7 : propre sur toutes les vues, mais n'impressionne pas encore.
- 7,5 : seuil. Rien ne gêne, la vue principale marque.
- 8,5+ : Adrien dirait « magnifique » (ex. tornade J3, trône K5).

Sois sévère : une note gonflée coûte plus cher qu'une note basse (le trône à « 6,5 » qui n'avait pas d'accoudoirs).
