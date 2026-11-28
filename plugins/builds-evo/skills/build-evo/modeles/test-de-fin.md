# Test de fin : <scène>

À copier dans le dossier du build, écrit dès la 1re pièce jouable et rejoué à chaque lot de script. Une case cochée = vue au banc (console, `diag` ou capture), jamais supposée.

## Wipe (`<nom>_tout_effacer`)
- [ ] Effacer : props du build retirés, décor script éteint chez tous, `diag` = « rien d'actif », 0 hook, 0 timer.
- [ ] Un build voisin aux mêmes modèles reste intact.
- [ ] Aucun envoi d'état après l'effacement (le relais ne rallume pas les clients).
- [ ] Recoller au même endroit : props ET décor script reviennent, à l'image.

## Visibilité (2 places : MJ + joueur)
- [ ] Ce qui est réservé au MJ (numéros, repères, commandes) : visible du MJ seul.
- [ ] Le joueur de la scène n'est ni admin ni MJ ; ses commandes éventuelles sont refusées côté serveur.
- [ ] Hors boîte : rien vu, rien entendu.
- [ ] Arrivée en cours de scène : état rattrapé.

## Coût
- [ ] Commande de mesure : ms par image moyenne et 1 % pire, dessins par image, avant et après chaque optimisation.
- [ ] Console vide d'erreur Lua sur toute la séquence.
