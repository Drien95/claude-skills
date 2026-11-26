---
name: effets-scene-lua
description: Écrire, déboguer ou optimiser le script Lua d'une scène GMod pour EVO (effets côté client, particules dessinées, faisceaux, brume, DynamicLight, sons, ciel 3D, miroir, séquences, addon serveur). Couvre les pièges Lua 5.1/GMod, la boîte relative au prop repère, la performance pour ~30 joueurs et la livraison sur creations-evo.
---

# Effets de scène en Lua (GMod, EVO)

Tout ce qui n'est pas un prop se fait ici : flammes, gaz, fumée, brume, lumière, veines, reflets, lointains, ciel 3D. C'est gratuit en budget de posés, mais pas en millisecondes.

## Règles dures (les hooks du plugin bloquent les trois premières)
1. **Touches jamais en dur** : pas de `KEY_*`, `input.IsKeyDown`, `PlayerButtonDown`, `PlayerBindPress`. Des commandes (`concommand.Add`) et un `bind` au choix d'Adrien dans le README.
2. **Aucune coordonnée serveur en dur** : la boîte de scène (h × L × l fixe) est relative au **prop repère** du dupe, trouvé au repérage. Où qu'on colle le build, tout s'y joue (effets, sons, ciel 3D, caméra, test « joueur dedans »), même le wipe.
3. **Jamais de musique** (ni `sound.PlayURL`, ni `music/`) : des sons seulement, la musique est gérée en jeu par les MJ.
4. Seuls les joueurs **dans la boîte** voient et entendent la scène. Rien ne déborde de la boîte, même en script (plafond de zone à ~330 u de la limite du monde) : le gigantesque passe par un ciel 3D.
5. Une commande d'effacement retire le build ET éteint tout (scène, sons, horizon, ciel) chez tous.
6. Les effets EVO (aura, magic_flame…) rendent mal : dessiner soi-même (beams, sprites, quads, maillages).

## Méthode
- Effets en trois temps : **anticipation → pic tôt → dissipation** ; un primaire à la fois ; ni noir pur ni blanc pur sauf le flash. `references/06-vfx.md`.
- Chaque pièce a **effets ET sous-effets** (niveau tornade J3) ; jugés **de nuit**, en démo jouée en direct dans GMod sans voler le focus.
- Posés sur le **point fonctionnel mesuré** du modèle (lame, foyer), pas au jugé.
- Une scène se mène **séquence par séquence** (suivante, précédente, aller à N), chaque séquence tient sa dernière image. Rythme : skill `mise-en-scene`.
- Après chaque passe : `luajit -bl` et chercher les GGET (locale lue avant sa déclaration = globale nil).

## Fiches
| Besoin | Fiche |
|---|---|
| Pièges Lua 5.1 / GMod déjà rencontrés | `references/pieges-lua.md` |
| Recettes d'effets qui ont marché (veines, onde, miroir, brume, ciel 3D, cascade…) | `references/recettes-effets.md` |
| Assembler la scène, boîte relative, addon serveur, livraison | `references/assemblage-livraison.md` |
| Mesurer et optimiser (~30 joueurs) | `references/performance.md`, `references/09-technical-art.md` |
| Principes VFX et 12 principes de l'animation | `references/06-vfx.md` |
