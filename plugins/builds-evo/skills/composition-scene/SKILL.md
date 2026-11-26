---
name: composition-scene
description: "Composition et direction artistique d'une scène ou d'une vue de build EVO : point focal, trois plans, lumière clé et brume, couleur, échelle et gigantisme, illusion d'infini, narration du décor, goûts d'Adrien. À utiliser pour concevoir la fiche DA, choisir les vues, ou critiquer une capture avant de toucher aux props."
---

# Composition de scène

Ce skill décide **ce que l'œil voit et dans quel ordre**. Il ne pose aucun prop (→ `pieces-props`) et n'écrit aucun effet (→ `effets-scene-lua`).

## Les 5 pratiques prioritaires
1. **Écrire avant de construire** : fiche DA (modèle dans le skill `build-evo`, `modeles/fiche-da.md`).
2. **Un point focal par vue** : seul endroit avec le fort contraste, l'accent de couleur et le détail ; le reste se repose.
3. **Trois plans** : premier plan sombre qui cadre, milieu = sujet, fond clair et brumeux (perspective atmosphérique).
4. **Une lumière clé + la brume** avant toute autre lumière ou effet.
5. **Le cerveau complète** : suggérer plutôt que tout construire (Gestalt), surtout pour le gigantesque.

## Règles propres à EVO et à Adrien
- Lire `references/gouts-adrien.md` avant de proposer une DA.
- Gigantisme : on ne voit jamais le tout (haut perdu dans la brume, cadrages bas qui coupent le haut, premier plan pour l'échelle) ; pas « un immeuble ».
- Infini dans une boîte : couches de parallaxe, perspective aérienne, aucun bord visible, perspective forcée, ciel 3D (miniature dans la boîte), jamais de géométrie hors zone.
- Lumière sur EVO : 4 vraies lumières par joueur max, lueurs du catalogue (n'éclairent pas), le reste en script (DynamicLight).

## Quelle fiche lire
| Question | Fiche |
|---|---|
| Où regarde l'œil, dans quel ordre ? | `references/01-composition.md` |
| Quelle règle visuelle unique ? (fiche DA) | `references/02-direction-artistique.md` |
| D'où vient la lumière ? | `references/03-eclairage.md` |
| Que s'est-il passé ici ? | `references/05-narration-environnementale.md` |
| Quelle teinte domine, où est l'accent ? | `references/10-couleur.md` |
| Que complète le cerveau tout seul ? | `references/11-perception-gestalt.md` |
| Comment faire grand avec peu ? | `references/12-architecture-scenographie.md` |
| Comment faire infini dans une boîte ? | `references/13-concept-art-matte-painting.md` |
| Que font Souls, Elden Ring, Hollow Knight ? | `references/17-jeux-reference.md` |

## Critiquer une capture
Méthode de Feldman (décrire, analyser, interpréter, juger) et grille de contrôle : skill `build-evo` (`references/21-critique-charge-cognitive.md`, `references/grille-controle.md`). Test rapide : capture réduite en noir et blanc, yeux plissés, le point focal en < 2 s.
