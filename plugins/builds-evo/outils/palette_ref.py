#!/usr/bin/env python3
"""Extrait une palette (dominante, neutres, accent) d'images de référence, au format de la fiche DA.

Usage : python palette_ref.py image1.jpg [image2.png ...] | dossier  [--ecrire fiche-da.md]
Sortie : « dominante `#......` ; neutres `#......` `#......` ; accent `#......` ». Avec --ecrire, remplace la ligne
« Palette en hex » de la fiche. Règle des fiches 02 et 10 : 1 dominante, 1-2 neutres, 1 accent rare et d'une autre famille.
Nécessite Pillow ; une suggestion, jamais un verdict : la fiche reste validée par Adrien.
"""
import argparse
import colorsys
import re
import sys
from pathlib import Path

IMG = (".jpg", ".jpeg", ".png", ".webp")


def couleurs(chemins, n=8):
    from PIL import Image
    tot = {}
    for c in chemins:
        im = Image.open(c).convert("RGB")
        im.thumbnail((200, 200))
        q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT).convert("RGB")
        total = im.size[0] * im.size[1]
        for k, rgb in q.getcolors():
            tot[rgb] = tot.get(rgb, 0) + k / total
    s = sum(tot.values()) or 1
    return {c: v / s for c, v in tot.items()}


def hsv(c):
    return colorsys.rgb_to_hsv(*(x / 255 for x in c))


def hexa(c):
    return "#%02x%02x%02x" % c


def choisir(tot):
    """(dominante, [neutres], accent|None) à partir des parts de chaque couleur."""
    liste = sorted(tot.items(), key=lambda kv: -kv[1])
    colorees = [(c, p) for c, p in liste if hsv(c)[1] > 0.2 and hsv(c)[2] > 0.15] or liste
    dominante = colorees[0][0]
    hd = hsv(dominante)[0]
    accent = None
    candidats = [(c, p) for c, p in liste if p < 0.10 and hsv(c)[1] > 0.45 and hsv(c)[2] > 0.35
                 and min(abs(hsv(c)[0] - hd), 1 - abs(hsv(c)[0] - hd)) > 0.16]
    if candidats:
        accent = max(candidats, key=lambda cp: hsv(cp[0])[1] * hsv(cp[0])[2])[0]
    neutres = [c for c, p in liste if hsv(c)[1] <= 0.3 and c not in (dominante, accent)][:2]
    if not neutres:     # aucun gris dans les références : neutre dérivé de la dominante (désaturé, plus sombre)
        h, sa, v = hsv(dominante)
        neutres = [tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, sa * 0.3, v * 0.6))]
    return dominante, neutres, accent


def ligne(dominante, neutres, accent):
    t = "dominante `%s` ; neutres %s" % (hexa(dominante), " ".join("`%s`" % hexa(c) for c in neutres))
    return t + (" ; accent `%s`" % hexa(accent) if accent else " ; accent à choisir (aucune couleur rare et distincte trouvée)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--ecrire")
    a = ap.parse_args(argv)
    chemins = []
    for s in a.sources:
        p = Path(s)
        chemins += sorted(f for f in p.iterdir() if f.suffix.lower() in IMG) if p.is_dir() else [p]
    if not chemins:
        print("aucune image", file=sys.stderr)
        return 2
    try:
        l = ligne(*choisir(couleurs(chemins)))
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    except OSError as e:
        print("image illisible : %s" % e, file=sys.stderr)
        return 2
    print(l)
    if a.ecrire:
        f = Path(a.ecrire)
        texte = f.read_text(encoding="utf-8")
        nouveau, n = re.subn(r"(\*\*Palette en hex\*\*[^\n:]*:).*", lambda m: m.group(1) + " " + l, texte, count=1)
        if not n:
            print("ligne « Palette en hex » absente de %s" % f, file=sys.stderr)
            return 2
        f.write_text(nouveau, encoding="utf-8")
        print("fiche mise à jour : %s" % f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
