# 14. Game design narratif et rythme (pacing)

**Le domaine** : le *pacing* est le rythme des moments forts et des moments calmes. Le narrative designer et le level designer le planifient sur une **courbe d'intensité**. Pour nos séquences scriptées (animations de scène, apparitions, effets), c'est ce qui fait la différence entre « une suite d'effets » et « un moment ».

## Principes clés

- **Planifier le rythme avant de construire** : un plan d'intensité et de rythme avant le level design ; le design « à la volée » mène à du travail jeté (Mike Lopez, 2008).
- **Alterner forts et calmes** : chaque événement d'action fort est **encadré par un calme avant et après** (dialogue, déplacement, vue panoramique) (Lopez).
- **Intensité croissante** : les pics se rapprochent ou restent réguliers, et l'intensité monte d'un niveau à l'autre (Lopez).
- **Faire plus d'idées que nécessaire** : imaginer 2 à 3 fois plus de lieux qu'on n'en construira, garder ceux qui ont au moins 3 événements (Lopez).
- **Quatre mesures du rythme** (Mark Davies, 2009) : **menace** (danger réel), **tension** (danger perçu), **élan** (envie d'avancer), **tempo** (quantité d'action).
- **Ce qui ralentit le joueur** : vues spectaculaires, obstacles, menace devant, dialogue, exposition. **Ce qui l'accélère** : menace derrière, objectif clair, limite de temps, couloirs étroits, objet qui attire l'œil (Davies).
- **La tension a besoin d'une menace compréhensible** : *Dead Space* montre tôt la conséquence (Davies).
- **Couplet / refrain** : alterner creux et pics, sans qu'aucun ne dure trop (Davies) ; les combats de boss montent en crescendo.
- **Moment de récompense voulu** : Anor Londo arrive juste après la forteresse de Sen pour que le joueur se dise « j'y suis arrivé » (*Dark Souls Design Works*).
- **Ouvrir sur du familier** avant d'assombrir le monde (Miyazaki, interview Vice 2016).
- **Une séquence spectaculaire = un mini-film à paliers**, avec une règle lisible d'un coup d'œil (note projet Kuga, 20/11).

## Application GMod / EVO

Chaque séquence scriptée a une **courbe écrite** dans la maquette three.js, avant tout réglage au banc :

```
Intensité
  5 |                    ██
  4 |                 ██ ██
  3 |           ██    ██ ██ ██
  2 |  ██    ██ ██    ██ ██ ██ ██
  1 |██ ██ ██ ██ ██ ░░ ██ ██ ██ ██ ██
    +---------------------------------> temps
     calme  signe  montée  SILENCE  SOMMET  retombée  calme
```

- **Structure type** (5 temps) : calme d'installation → premier signe (son, lueur au loin) → montée (2-3 paliers) → **silence / noir** (1-2 s) → sommet (UN effet primaire) → retombée (suivi : cendres, ondes) → calme final.
- **Paliers** : chaque palier ajoute UNE chose nouvelle (un son, une lumière, un mouvement), jamais trois en même temps.
- **Calme avant et après chaque sommet** : sans le calme, le sommet ne se voit pas.
- **Durées** : noter les secondes de chaque temps. Une séquence trop longue au sommet fatigue ; une anticipation trop courte rate l'effet.
- **Pour le MJ** : la courbe sert aussi de feuille de route en séance (quand parler, quand se taire, quand lancer la musique en jeu). Voir 18-direction-joueurs-mj.md.
- **Contrôle** : regarder la séquence en entier une fois sans le son, une fois sans l'image. Chacune des deux doit encore suivre la courbe.

## Sources
- Mike Lopez, [Gameplay Fundamentals Revisited, Part 2: Building a Pacing Structure](https://www.gamedeveloper.com/design/gameplay-fundamentals-revisited-part-2-building-a-pacing-structure) (2008)
- Mark Davies, [Examining Game Pace: How Single-Player Levels Tick](https://www.gamedeveloper.com/design/examining-game-pace-how-single-player-levels-tick) (2009)
- [Trinity, part 6: Intensity Ramps](https://www.gamedeveloper.com/design/trinity-part-6-intensity-ramps) (Game Developer)
- [Dark Souls 1 : Design Works Interview](https://darksouls.wiki.fextralife.com/Dark+Souls+1+-+Design+Works+Interview)
- Sayem Ahmed, [On the Sublime and Beautiful: Miyazaki interview](https://www.vice.com/en/article/on-the-sublime-and-beautiful-a-conversation-with-dark-souls-iii-director-hidetaka-miyazaki) (Vice, 2016)
