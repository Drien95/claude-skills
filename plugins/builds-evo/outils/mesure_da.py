#!/usr/bin/env python3
"""Mesure gratuite d'une capture contre la fiche DA, avant la critique payante.

Usage : python mesure_da.py capture.jpg [--fiche fiche-da.md] [--palette #112233 #445566 ...] [--accent #cc3322] [--json]

Mesure : couleurs dominantes, luminance moyenne, saturation moyenne, contraste du point focal
(case la plus lumineuse sur une grille 8x6 contre la médiane), part d'accent, écart à la palette.
Ce sont des alertes, pas un verdict : le jugement reste à la critique. Nécessite Pillow (pip install pillow).
"""
import argparse
import colorsys
import json
import re
import sys

HEX = re.compile(r"#([0-9a-fA-F]{6})\b")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lire_fiche(chemin):
    """Palette et accent depuis la ligne « Palette en hex » de la fiche DA."""
    texte = open(chemin, encoding="utf-8").read()
    ligne = next((l for l in texte.splitlines() if "Palette en hex" in l), "")
    if "accent" in ligne.lower():
        avant, _, apres = ligne.lower().rpartition("accent")
        accent = HEX.findall(apres)
        base = HEX.findall(ligne[: len(avant)])
    else:
        accent, base = [], HEX.findall(ligne)
    return ["#" + h for h in base], ("#" + accent[0]) if accent else None


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def mesurer(chemin, palette=(), accent=None):
    from PIL import Image
    im = Image.open(chemin).convert("RGB")
    im.thumbnail((320, 320))
    px = list(im.getdata())
    n = len(px)
    lums = [lum(p) for p in px]
    sats = [colorsys.rgb_to_hsv(*(c / 255 for c in p))[1] for p in px]
    q = im.quantize(colors=6, method=Image.Quantize.MEDIANCUT).convert("RGB")
    comptes = sorted(q.getcolors(), reverse=True)
    dom = [("#%02x%02x%02x" % c, round(k / n, 3)) for k, c in comptes]
    w, h = im.size
    cases = []
    for gy in range(6):
        for gx in range(8):
            c = [lums[y * w + x] for y in range(gy * h // 6, (gy + 1) * h // 6) for x in range(gx * w // 8, (gx + 1) * w // 8)]
            cases.append(sum(c) / len(c))
    med = sorted(cases)[len(cases) // 2]
    # test « yeux plissés » : image réduite à 16 x 9 en gris, le sommet doit se détacher de la moyenne
    petit = im.convert("L").resize((16, 9), Image.Resampling.BOX)
    gris = list(petit.getdata())
    moy = sum(gris) / len(gris)
    sigma = (sum((g - moy) ** 2 for g in gris) / len(gris)) ** 0.5
    plissé = (max(gris) - moy) / sigma if sigma > 1 else 0.0
    # cadre : les bords doivent être plus sombres que le centre (premier plan qui cadre)
    bord = [gris[y * 16 + x] for y in range(9) for x in range(16) if x in (0, 1, 14, 15) or y in (0, 8)]
    centre = [gris[y * 16 + x] for y in range(2, 7) for x in range(4, 12)]
    cadre = (sum(bord) / len(bord)) / max(1.0, sum(centre) / len(centre))
    res = {
        "dominantes": dom,
        "luminance": round(sum(lums) / n / 255, 3),
        "saturation": round(sum(sats) / n, 3),
        "contraste_focal": round((max(cases) - med) / 255, 3),
        "yeux_plisses": round(plissé, 2),
        "bords_sur_centre": round(cadre, 2),
        "alertes": [],
    }
    if accent:
        a = hex_rgb(accent)
        res["part_accent"] = round(sum(1 for p in px if dist(p, a) < 60) / n, 3)
    if palette:
        pal = [hex_rgb(c) for c in palette]
        e = sum(min(dist(hex_rgb(c), p) for p in pal) * k for c, k in dom) / 255
        res["ecart_palette"] = round(e, 3)
    al = res["alertes"]
    if res["luminance"] < 0.04:
        al.append("image presque noire : rien ne se lit")
    if res["luminance"] > 0.6:
        al.append("image très claire pour un monde sombre")
    if res["contraste_focal"] < 0.08:
        al.append("pas de point focal net (la zone la plus claire ressemble au reste)")
    if res["yeux_plisses"] < 1.8 and res["luminance"] >= 0.04:
        al.append("yeux plissés : aucun sommet net en 16 x 9, le sujet ne ressort pas en moins de 2 s")
    if res["bords_sur_centre"] > 1.15:
        al.append("bords plus clairs que le centre : pas de premier plan sombre qui cadre")
    if res["saturation"] > 0.55:
        al.append("saturation moyenne forte : l'accent ne sera pas seul à ressortir")
    if accent and res["part_accent"] > 0.08:
        al.append("l'accent couvre plus de 8 % de l'image : il n'est plus rare")
    if accent and res["part_accent"] == 0:
        al.append("l'accent est absent de la vue")
    if palette and res["ecart_palette"] > 0.25:
        al.append("couleurs éloignées de la palette de la fiche DA")
    return res


def mesurer_dossier(dossier, fiche=None, palette=(), accent=None):
    """Mesure toutes les captures d'un dossier ; renvoie un texte court (une ligne par vue, alertes seulement)."""
    from pathlib import Path
    if fiche:
        p2, a2 = lire_fiche(fiche)
        palette, accent = list(palette) or p2, accent or a2
    images = sorted(f for f in Path(dossier).iterdir()
                    if f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("planche"))
    if not images:
        return "aucune capture dans %s" % dossier
    lignes, nb = [], 0
    for f in images:
        r = mesurer(str(f), palette, accent)
        nb += bool(r["alertes"])
        lignes.append("%s : lum %.2f sat %.2f focal %.2f plissé %.1f%s" % (
            f.stem, r["luminance"], r["saturation"], r["contraste_focal"], r["yeux_plisses"],
            (" | " + " ; ".join(r["alertes"])) if r["alertes"] else ""))
    entete = "mesure DA : %d vue(s), %d avec alerte%s" % (
        len(images), nb, "" if (palette or accent) else " (sans palette : ni écart ni accent mesurés)")
    return "\n".join([entete] + [l for l in lignes if "|" in l] if nb else [entete])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("capture")
    ap.add_argument("--fiche")
    ap.add_argument("--palette", nargs="*", default=[])
    ap.add_argument("--accent")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    pal, acc = list(a.palette), a.accent
    if a.fiche:
        p2, a2 = lire_fiche(a.fiche)
        pal, acc = pal or p2, acc or a2
    try:
        res = mesurer(a.capture, pal, acc)
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    except OSError as e:
        print("capture illisible : %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for k, v in res.items():
            if k != "alertes":
                print("%-16s %s" % (k, v))
        print("\n".join("ATTENTION : " + t for t in res["alertes"]) or "aucune alerte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
