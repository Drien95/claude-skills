---
name: passation
description: "Fin de fil sur un chantier du coffre OPTIMUS (/optimus:passation <note>) : met à jour le résumé, l'État, la Passation, le statut, maj et JOURNAL.md, régénère l'index, puis le script du coffre contrôle qu'il ne manque rien. À lancer avant de clore tout fil qui a fait avancer une note."
argument-hint: <nom-de-note>
---

# Passation de fin de fil

Note : $ARGUMENTS (nom sans `.md`, ex. `a2-sable-du-fond`).

1. **Coffre** : variable `OPTIMUS_DIR`, sinon `C:\Project\OPTIMUS` sur le PC, sinon le clone `optimus` du projet. Lis son `CLAUDE.md` si tu ne l'as pas lu dans ce fil.
2. **Note** : ouvre-la. Mets à jour, d'après ce qui s'est fait dans CE fil seulement :
   - le résumé `> [!resume] Pour le prochain fil` (2 ou 3 lignes : où on en est, la prochaine action, ce qui attend Adrien) ;
   - `## État` (version courante, fichiers, liens) ;
   - `## Passation` : `- Fait :`, `- À relire par Adrien :`, `- Suite :` ;
   - les décisions d'Adrien du fil (datées, **Pourquoi**, **Comment appliquer**) si elles n'y sont pas déjà ;
   - `statut` et `maj` (date du jour, AAAA-MM-JJ).
   Au-delà de 4 Ko : déplace les versions et essais dans `99-archives/historique/<nom>-historique.md`, sans rien perdre.
3. **Journal** : `python scripts/optimus.py journal TYPE "texte court [[<note>]]"` (types : build, atelier, plugin, lore, evo, adrien, coffre, outil).
4. **Contrôle, 0 jeton** : `python scripts/optimus.py index`, puis `python scripts/optimus.py passation <note>` et `python scripts/optimus.py verifier`. Corrige chaque « À FAIRE » et chaque erreur, relance jusqu'à « Passation complète. » et 0 erreur.
5. **Règle de build générale** apprise dans le fil : elle va aussi dans le plugin builds-evo (`/builds-evo:lecon`).
6. **Git** : branche + PR, Adrien merge (sauf s'il a autorisé le commit direct pour les seules notes). Sur le PC, Obsidian Git pousse lui-même : ne pas pousser en double.
7. Réponds à Adrien en 2 lignes : ce qui est noté et ce qui l'attend.
