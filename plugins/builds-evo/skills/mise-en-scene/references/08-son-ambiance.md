# 8. Sound design d'ambiance

**Le métier** : le sound designer d'ambiance construit ce qu'on entend « quand rien ne se passe » : le vent, la salle, l'eau, les bruits lointains. Une bonne ambiance fait croire à la taille et à la matière d'un lieu que l'œil ne voit pas en entier. Rappel : **jamais de musique dans nos scripts**, la musique est gérée par les MJ en jeu.

## Principes clés

- **L'ambiance passe derrière** : elle doit laisser la place aux sons importants. On creuse les médiums (~350 Hz à 2 kHz) et on calme les basses pour que les impacts gardent leur force (Michael Theiler, *Designing Sound*, 2012).
- **Moins, c'est plus** : retirer tout ce qui « sort » du fond ; espacer les sons ponctuels pour éviter l'encombrement (Theiler).
- **Ordre de travail** : d'abord répétition et timing, puis l'égalisation, puis la propagation et l'espace. Ajouter de la réverbération ne suffit pas (Theiler, *LA Noire / Banner Saga*).
- **Distance** : un son lointain = surtout de la réverbération, peu de son direct, et les aigus coupés (Theiler).
- **Échos = surfaces** : des échos à ~300 ms et ~600 ms suggèrent des montagnes (Banner Saga) ; le timbre de l'écho dit la matière (bois, verre, pierre) (Theiler).
- **Couche aléatoire** : un tapis continu + des clips ponctuels tirés au hasard (position, volume, délai) pour éviter la boucle reconnaissable (Banner Saga sous FMOD).
- **Choisir le bon son vaut mieux que traiter un mauvais** : ~75 % du temps à chercher, ~25 % à traiter (commentaire de Randy Thom, sound designer de cinéma).
- **Le son guide aussi** : les joueurs se tournent vers un son ou un mouvement (Unity, *Level design basics*).
- **Le silence est un outil** : couper l'ambiance juste avant un moment fort le rend énorme (note projet Kuga : « noir + silence juste avant »).

## Application GMod / EVO

Structure d'ambiance en 3 couches, toutes dans la boîte du build, entendues seulement par les joueurs dedans :

1. **Lit de fond** (boucle continue, bas volume) : vent, eau, grondement de salle. 1 à 2 sons maximum.
2. **Ponctuels aléatoires** : gouttes, craquements, cris lointains, cloche. Tirés au hasard toutes les 8 à 30 s, à une position aléatoire dans la boîte, volume variable. C'est ce qui donne la vie et la taille.
3. **Sons de séquence** : montée (anticipation), impact, retombée, calés sur la timeline des effets (voir ../../effets-scene-lua/references/06-vfx.md).

Conseils pratiques :
- **Distance par le traitement** : Source propose des presets DSP (réverbération de grande salle, de canyon). Pour un son « lointain » : volume bas + niveau sonore (soundlevel) bas + DSP de grande salle.
- **Silence avant le sommet** : couper la couche 1 et 2 une à deux secondes avant l'impact principal.
- **Vérifier la répétition** : écouter 3 minutes d'ambiance les yeux fermés. Si on reconnaît la boucle, il faut plus de variation dans la couche 2.
- **Cohérence matière** : salle de pierre = échos longs et clairs ; eau = graves étouffés ; Hueco Mundo = vent sec, sable, vide.

## Sources
- Michael Theiler, [Creating the spaces of ambience](https://designingsound.org/2012/12/29/creating-the-spaces-of-ambience/) (Designing Sound, 2012)
- Michael Theiler, [Creating Ambient Audio for LA Noire & The Banner Saga](https://www.gamedeveloper.com/audio/creating-ambient-audio-for-la-noire-the-banner-saga) (Game Developer, 2012)
- Audiokinetic, [Designing ambience systems in Wwise](https://blog.audiokinetic.com/en/designing-ambience-systems-in-wwise/)
- Unity, [Level design basics](https://unity.com/blog/level-design-basics)
- Valve Developer Community, [DSP presets](https://developer.valvesoftware.com/wiki/Dsp_presets) et [Soundscapes](https://developer.valvesoftware.com/wiki/Soundscapes)
