---
name: conso
description: "Consommation de jetons d'un build EVO, par scène, pièce et modèle, comptée à 0 jeton par le hook budget (/builds-evo:conso [scène]). Pour la rétro, ou quand Adrien demande ce qu'a coûté un build."
argument-hint: "[scène]"
---

# Consommation d'un build

Lance, dans le dossier du projet (là où est `.claude/builds-evo/`) :

```
python <plugin>/hooks/budget.py rapport $ARGUMENTS
```
`<plugin>` : le dossier du plugin builds-evo (Glob `**/builds-evo/hooks/budget.py`, sinon `C:\Project\claude-skills\plugins\builds-evo`).

Recopie le résultat tel quel à Adrien, puis une ligne : la pièce la plus chère et pourquoi (passes, critiques, longueur de session), d'après le journal de mesure. L'indice compare deux builds entre eux ; ce n'est pas un pourcentage du forfait Max (la limite n'est pas publiée).
