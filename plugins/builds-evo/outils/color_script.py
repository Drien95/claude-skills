#!/usr/bin/env python3
"""Color script d'une séquence (fiches 02 et 07) : une capture par temps fort, côte à côte, et alerte si deux se ressemblent.

Usage : python color_script.py <dossier de captures, un fichier par temps fort, ordre alphabétique> [--sortie color_script.png]
Règles : « si deux temps forts se ressemblent, l'un des deux doit changer (couleur de brume, lumière) » ; le sommet garde la
couleur la plus vive (la dernière capture, ou celle du milieu si le dossier en a plus de 5, doit être la plus saturée).
Écrit une planche (bande de vignettes avec leur nom) et affiche les alertes. Nécessite Pillow.
"""
import argparse
import colorsys
import sys
from pathlib import Path

PROCHE = 0.12     # distance moyenne (0 à 1) sous laquelle deux temps forts « se ressemblent »


def empreinte(im):
    p = im.copy()
    p.thumbnail((64, 64))
    px = list(p.get_flattened_data()) if hasattr(p, "get_flattened_data") else list(p.getdata())
    n = len(px)
    m = [sum(c[i] for c in px) / n / 255 for i in range(3)]
    sat = sum(colorsys.rgb_to_hsv(*(x / 255 for x in c))[1] for c in px) / n
    return m, sat


def distance(a, b):
    return (sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5) / 3 ** 0.5


def analyser(noms, empreintes):
    alertes = []
    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            d = distance(empreintes[i][0], empreintes[j][0])
            if d < PROCHE:
                alertes.append("« %s » et « %s » se ressemblent (écart %.2f < %.2f) : changer la couleur de brume ou la lumière de l'un" % (noms[i], noms[j], d, PROCHE))
    if len(noms) >= 3:
        sats = [e[1] for e in empreintes]
        if sats.index(max(sats)) not in (len(noms) - 1, len(noms) // 2, len(noms) - 2):
            alertes.append("la couleur la plus vive n'est pas au sommet (« %s » est la plus saturée) : garder la plus forte couleur pour le temps fort" % noms[sats.index(max(sats))])
    return alertes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dossier")
    ap.add_argument("--sortie", default="color_script.png")
    a = ap.parse_args(argv)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    fichiers = sorted(f for f in Path(a.dossier).iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith(("planche", "color_script")))
    if len(fichiers) < 2:
        print("2 captures au moins (une par temps fort)", file=sys.stderr)
        return 2
    ims = [Image.open(f).convert("RGB") for f in fichiers]
    noms = [f.stem for f in fichiers]
    l, h = 320, 180
    bande = Image.new("RGB", (l * len(ims), h), "black")
    d = ImageDraw.Draw(bande)
    for i, (im, nom) in enumerate(zip(ims, noms)):
        bande.paste(im.resize((l, h)), (i * l, 0))
        d.rectangle([i * l, 0, i * l + 8 + 7 * len(nom), 20], fill="black")
        d.text((i * l + 4, 4), nom, fill="yellow")
    bande.save(a.sortie)
    alertes = analyser(noms, [empreinte(im) for im in ims])
    print("color script : %s (%d temps forts)" % (a.sortie, len(ims)))
    print("\n".join("ATTENTION : " + t for t in alertes) or "les temps forts se distinguent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
