#!/usr/bin/env python3
"""Générateur de décor par grappes (fiches 04, 11, 20) : scene.json prêt pour `dunes/encode.py` et `controle_auto.py`.

Usage : python decor.py params.json   (sorties dans le dossier courant : decor_<nom>_<graine>.json, planche_<nom>.png si Pillow)

Règles : grappes de 3 (gros, moyen, petit, légèrement tournés), centres de grappes espacés (disque de Poisson par
rejet), couloir du chemin laissé libre, inclinaison bornée (2 à 8 degrés, jamais d'un décor porteur), graine pour refaire
exactement le même résultat, budget de posés = limite dure (la génération s'arrête, jamais de dépassement).

Paramètres : nom, graine, variantes (nombre de graines successives), zone {cx, cy, rayon}, z (sol),
chemin [[x, y], ...] + largeur_chemin, vocabulaire [{modele, rayon, demi_hauteur, poids}], n_grappes, ecart_grappes,
budget, inclinaison [min, max], couleur [r, v, b], materiau, tete (prop de départ, posé au centre).
"""
import json
import math
import random
import sys
from pathlib import Path


def dist_segment(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def sur_chemin(p, chemin, largeur):
    return any(dist_segment(p, a, b) < largeur for a, b in zip(chemin, chemin[1:]))


def generer(par, graine):
    rnd = random.Random(graine)
    zone = par["zone"]
    voc = sorted(par["vocabulaire"], key=lambda v: -v["rayon"])
    if len(voc) < 3:
        raise ValueError("vocabulaire : 3 modèles minimum (gros, moyen, petit)")
    budget = int(par.get("budget", 400))
    chemin, largeur = par.get("chemin") or [], par.get("largeur_chemin", 150)
    ecart = par.get("ecart_grappes", 220)
    lo, hi = par.get("inclinaison", [2, 8])
    couleur, mat = par.get("couleur", [90, 90, 95]), par.get("materiau", "models/debug/debugwhite")
    z0 = par.get("z", 0)
    tete = par.get("tete")
    ents = []
    if tete:
        ents.append({"kind": "prop", "model": tete["modele"], "pos": [zone["cx"], zone["cy"], z0 + tete.get("demi_hauteur", 0)],
                     "ang": [0, 0, 0], "color": couleur, "mat": mat, "note": "tete"})
    centres = []
    essais = 0
    while len(centres) < par.get("n_grappes", 20) and essais < 4000:
        essais += 1
        a, r = rnd.uniform(0, 2 * math.pi), zone["rayon"] * math.sqrt(rnd.random())
        c = (zone["cx"] + r * math.cos(a), zone["cy"] + r * math.sin(a))
        if sur_chemin(c, chemin, largeur) or any(math.hypot(c[0] - o[0], c[1] - o[1]) < ecart for o in centres):
            continue
        centres.append(c)
    for k, c in enumerate(centres):
        # une grappe = 1 gros, 1 moyen, 1 petit, légèrement tournés (fiche 04)
        for rang, (v, ech) in enumerate(((voc[0], 1.0), (voc[len(voc) // 2], 0.8), (voc[-1], 0.6))):
            if len(ents) >= budget:
                break
            d = 0 if rang == 0 else v["rayon"] + voc[0]["rayon"] * 0.6
            a = rnd.uniform(0, 2 * math.pi)
            p = (c[0] + d * math.cos(a), c[1] + d * math.sin(a))
            if sur_chemin(p, chemin, largeur):
                continue
            ents.append({"kind": "prop", "model": v["modele"], "pos": [round(p[0], 1), round(p[1], 1), round(z0 + v.get("demi_hauteur", 0), 1)],
                         "ang": [round(rnd.uniform(lo, hi) * rnd.choice((-1, 1)), 1), round(rnd.uniform(0, 360), 1), round(rnd.uniform(lo, hi) * rnd.choice((-1, 1)), 1)],
                         "color": couleur, "mat": mat, "note": "grappe%d_%d" % (k, rang)})
    return {"ents": ents, "fx": [], "head": "tete" if tete else (ents[0]["note"] if ents else "")}


def planche(par, scenes, chemin_png):
    from PIL import Image, ImageDraw
    n, l = len(scenes), 400
    cols = min(3, n)
    img = Image.new("RGB", (l * cols, l * ((n + cols - 1) // cols)), "black")
    d = ImageDraw.Draw(img)
    z = par["zone"]
    for i, (graine, s) in enumerate(scenes):
        ox, oy = (i % cols) * l, (i // cols) * l
        k = (l - 20) / (2.0 * z["rayon"])
        for a, b in zip(par.get("chemin") or [], (par.get("chemin") or [])[1:]):
            d.line([ox + l / 2 + (a[0] - z["cx"]) * k, oy + l / 2 + (a[1] - z["cy"]) * k, ox + l / 2 + (b[0] - z["cx"]) * k, oy + l / 2 + (b[1] - z["cy"]) * k], fill="darkred", width=3)
        for e in s["ents"]:
            x, y = ox + l / 2 + (e["pos"][0] - z["cx"]) * k, oy + l / 2 + (e["pos"][1] - z["cy"]) * k
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill="white")
        d.text((ox + 6, oy + 6), "graine %s : %d posés" % (graine, len(s["ents"])), fill="yellow")
    img.save(chemin_png)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage : python decor.py params.json", file=sys.stderr)
        return 2
    try:
        par = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        scenes = [(g, generer(par, g)) for g in range(par.get("graine", 1), par.get("graine", 1) + par.get("variantes", 6))]
    except (OSError, ValueError, KeyError) as e:
        print("ERREUR : %s" % e, file=sys.stderr)
        return 2
    nom = par.get("nom", "decor")
    for g, s in scenes:
        f = Path("decor_%s_%s.json" % (nom, g))
        f.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        print("%s : %d posés" % (f, len(s["ents"])))
    try:
        planche(par, scenes, "planche_%s.png" % nom)
        print("planche_%s.png" % nom)
    except ImportError:
        print("planche sautée (Pillow manque)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
