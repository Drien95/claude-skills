#!/usr/bin/env python3
"""Rapport de profilage lisible (fiches 09, 19 et performance.md) : « ce qui coûte, où, quoi corriger ».

Usage : python rapport_perf.py mesures.json
Entrée : liste de mesures, une par version, par les mêmes caméras :
  [{"version": "v8", "poses": 210, "ms_script": 3.47, "dessins": 1645, "fps_moy": 60, "fps_1pct": 41, "dynlights": 3, "quads_max": 5200}, ...]
Seuls `version` est obligatoire ; les champs absents ne sont pas contrôlés. Le format d'entrée vient des mesures du banc ;
la sonde client qui l'écrit reste à brancher (non fournie ici).
Alertes : posés > 400, dynlights > 2, lot de maillage > 4 000 quads, ms ou dessins +50 % sur la version précédente, 1 % pire sous 60 % de la moyenne.
Référence de l'ordre de grandeur : cathédrale v9 = 0,32 ms et 122 dessins/image ; Lac noir final = 17,8 ms par image, 1 % pire 38 ms.
"""
import json
import sys


def controler(mesures):
    lignes, alertes = [], []
    prec = None
    for m in mesures:
        v = m.get("version", "?")
        champs = ["%s %s" % (k, m[k]) for k in ("poses", "ms_script", "dessins", "fps_moy", "fps_1pct", "dynlights", "quads_max") if k in m]
        lignes.append("%s : %s" % (v, ", ".join(champs) or "aucune mesure"))
        if m.get("poses", 0) > 400:
            alertes.append("%s : %d posés (limite 400) : alléger (fiche 16)" % (v, m["poses"]))
        if m.get("dynlights", 0) > 2:
            alertes.append("%s : %d lumières dynamiques (2 maximum) : passer en faux éclairage par la matière" % (v, m["dynlights"]))
        if m.get("quads_max", 0) > 4000:
            alertes.append("%s : lot de maillage de %d quads (4 000 maximum, limite 32 768 indices) : découper" % (v, m["quads_max"]))
        if m.get("fps_moy") and m.get("fps_1pct") and m["fps_1pct"] < 0.6 * m["fps_moy"]:
            alertes.append("%s : 1 %% pire à %s i/s pour %s en moyenne : pics (ramasse-miettes, apparitions simultanées)" % (v, m["fps_1pct"], m["fps_moy"]))
        if prec:
            for cle, nom in (("ms_script", "coût du script"), ("dessins", "dessins par image")):
                if prec.get(cle) and m.get(cle) and m[cle] > 1.5 * prec[cle]:
                    alertes.append("%s : %s %s -> %s (+%d %% depuis %s) : regrouper les dessins, couper hors de la boîte" % (
                        v, nom, prec[cle], m[cle], round(100 * (m[cle] / prec[cle] - 1)), prec.get("version", "?")))
        prec = m
    return lignes, alertes


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage : python rapport_perf.py mesures.json", file=sys.stderr)
        return 2
    try:
        mesures = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("mesures illisibles : %s" % e, file=sys.stderr)
        return 2
    lignes, alertes = controler(mesures)
    print("\n".join(lignes))
    print("\n".join("ATTENTION : " + a for a in alertes) or "aucune alerte de performance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
