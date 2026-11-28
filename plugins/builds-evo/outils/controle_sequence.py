#!/usr/bin/env python3
"""Contrôle gratuit d'une séquence (timeline de la maquette) avant le banc.

Usage : python controle_sequence.py sequence.json
Format : {"sommet": 10.0, "courbe": [[0,1],[8,3],[10,5]],
          "evenements": [{"t": 4, "type": "effet|son|lumiere|silence", "nom": "...", "primaire": true, "debut": 2, "pic": 4, "fin": 6}],
          "ponctuels": {"goutte": [3, 14, 30]}}
Règles (fiches 06, 08, 14) : un seul effet primaire à la fois ; anticipation avant le pic (>= 1 s) ; silence d'au moins 2 s
avant le sommet ; une seule nouveauté par palier avant le sommet ; courbe d'intensité croissante jusqu'au sommet ;
sons ponctuels espacés de 8 à 30 s. La courbe peut tomber pendant un événement « silence » (debut, fin) : c'est voulu.
"""
import json
import sys

SILENCE, ANTICIPATION, PIC_PROCHE, PALIER = 2.0, 1.0, 1.0, 0.5


def controler(seq):
    erreurs, attentions = [], []
    ev = seq.get("evenements") or []
    sommet = seq.get("sommet")
    if sommet is None:
        erreurs.append("pas de « sommet » (instant du temps fort)")
        return erreurs, attentions
    prim = [e for e in ev if e.get("primaire")]
    for e in prim:
        d, p, f = e.get("debut"), e.get("pic"), e.get("fin")
        if None in (d, p, f) or not d < p < f:
            erreurs.append("effet « %s » : debut < pic < fin attendu" % e.get("nom", "?"))
        elif p - d < ANTICIPATION:
            attentions.append("effet « %s » : anticipation de %.1f s (< %.0f s), le boum arrivera sans préparation" % (e.get("nom", "?"), p - d, ANTICIPATION))
    pics = sorted((e["pic"], e.get("nom", "?")) for e in prim if isinstance(e.get("pic"), (int, float)))
    for (t1, n1), (t2, n2) in zip(pics, pics[1:]):
        if t2 - t1 < PIC_PROCHE:
            erreurs.append("deux effets primaires au même instant (« %s » %.1f s et « %s » %.1f s) : un seul à la fois" % (n1, t1, n2, t2))
    avant = sorted(e["t"] for e in ev if e.get("type") != "silence" and isinstance(e.get("t"), (int, float)) and e["t"] < sommet)
    if avant and sommet - avant[-1] < SILENCE:
        erreurs.append("pas de silence avant le sommet : dernier événement à %.1f s, sommet à %.1f s (%.0f s de silence attendus)" % (avant[-1], sommet, SILENCE))
    groupes, courant = [], []
    for t in avant:
        if courant and t - courant[0] > PALIER:
            groupes.append(courant)
            courant = []
        courant.append(t)
    if courant:
        groupes.append(courant)
    for g in groupes:
        if len(g) > 1:
            attentions.append("%d nouveautés en même temps vers %.1f s : un palier ajoute une seule chose" % (len(g), g[0]))
    courbe = seq.get("courbe") or []
    silences = [(e["debut"], e["fin"]) for e in ev if e.get("type") == "silence" and isinstance(e.get("debut"), (int, float)) and isinstance(e.get("fin"), (int, float))]
    montee = [i for t, i in sorted(courbe) if t <= sommet and not any(d <= t <= f for d, f in silences)]
    if any(b < a for a, b in zip(montee, montee[1:])):
        attentions.append("la courbe d'intensité redescend avant le sommet (crescendo attendu)")
    for nom, ts in (seq.get("ponctuels") or {}).items():
        ts = sorted(ts)
        for a, b in zip(ts, ts[1:]):
            if not 8 <= b - a <= 30:
                attentions.append("ponctuel « %s » : %.0f s entre deux sons (8 à 30 s attendus)" % (nom, b - a))
                break
    return erreurs, attentions


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[0] + "\nUsage : python controle_sequence.py sequence.json", file=sys.stderr)
        return 2
    try:
        seq = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("séquence illisible : %s" % e, file=sys.stderr)
        return 2
    erreurs, attentions = controler(seq)
    for e in erreurs:
        print("ERREUR : " + e)
    for t in attentions:
        print("ATTENTION : " + t)
    if not erreurs and not attentions:
        print("séquence conforme aux règles de rythme")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
