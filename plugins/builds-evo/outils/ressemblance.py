#!/usr/bin/env python3
"""Ressemblance d'ambiance entre captures et image maîtresse (fiche DA), pour 0 jeton d'image.

Usage : python ressemblance.py <image maîtresse> <capture ou dossier de captures>
Mesures (0 à 1, 1 = identique) : couleurs (intersection d'histogrammes teinte/saturation/valeur), clair-obscur (corrélation des valeurs sur 16 x 9)
et tonalité (écart de luminance moyenne). Seuils d'alerte : couleurs < 0,35, clair-obscur < 0,2, tonalité < 0,6. Ce n'est pas un jugement
d'ambiance : deux images peuvent se ressembler en couleur et différer en forme. Sert à repérer une scène qui s'éloigne de l'image visée.
Nécessite Pillow.
"""
import argparse
import colorsys
import sys
from pathlib import Path

IMG = (".jpg", ".jpeg", ".png", ".webp")


def _px(im):
    return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())


def histogramme(im):
    p = im.copy()
    p.thumbnail((96, 96))
    h = {}
    px = _px(p.convert("RGB"))
    for c in px:
        t, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
        cle = (int(t * 8) % 8 if s > 0.15 else -1, min(int(s * 3), 2), min(int(v * 4), 3))
        h[cle] = h.get(cle, 0) + 1 / len(px)
    return h


def clair_obscur(im):
    from PIL import Image
    return [x / 255 for x in _px(im.convert("L").resize((16, 9), Image.Resampling.BOX))]


def correlation(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** 0.5
    sb = sum((y - mb) ** 2 for y in b) ** 0.5
    return 0.0 if sa == 0 or sb == 0 else sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def comparer(ref, im):
    ha, hb = histogramme(ref), histogramme(im)
    couleurs = sum(min(ha.get(k, 0), hb.get(k, 0)) for k in set(ha) | set(hb))
    la, lb = clair_obscur(ref), clair_obscur(im)
    forme = max(0.0, correlation(la, lb))
    tonalite = 1 - abs(sum(la) / len(la) - sum(lb) / len(lb))
    al = []
    if couleurs < 0.35:
        al.append("couleurs éloignées de l'image maîtresse (%.2f)" % couleurs)
    if forme < 0.2:
        al.append("répartition clair/sombre différente (%.2f)" % forme)
    if tonalite < 0.6:
        al.append("tonalité générale trop différente (%.2f)" % tonalite)
    return {"couleurs": round(couleurs, 2), "clair_obscur": round(forme, 2), "tonalite": round(tonalite, 2), "alertes": al}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reference")
    ap.add_argument("captures")
    a = ap.parse_args(argv)
    try:
        from PIL import Image
        ref = Image.open(a.reference).convert("RGB")
        p = Path(a.captures)
        fichiers = sorted(f for f in p.iterdir() if f.suffix.lower() in IMG and not f.name.startswith(("planche", "color_script"))) if p.is_dir() else [p]
        if not fichiers:
            print("aucune capture", file=sys.stderr)
            return 2
        for f in fichiers:
            r = comparer(ref, Image.open(f).convert("RGB"))
            print("%s : couleurs %.2f, clair-obscur %.2f, tonalité %.2f%s" % (f.stem, r["couleurs"], r["clair_obscur"], r["tonalite"], (" | " + " ; ".join(r["alertes"])) if r["alertes"] else ""))
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    except OSError as e:
        print("image illisible : %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
