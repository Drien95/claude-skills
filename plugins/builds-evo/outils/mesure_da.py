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


def donnees(im):
    """Pixels d'une image (getdata est annoncé comme supprimé dans Pillow 14)."""
    return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else donnees(im)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lire_fiche(chemin):
    """Palette et accent depuis la ligne « Palette en hex » de la fiche DA."""
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
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


def mesurer(chemin, palette=(), accent=None, sortie=None):
    """`sortie` : zone [x0, y0, x1, y1] en fractions de l'image (où se trouve la suite du chemin), facultative."""
    from PIL import Image
    im = Image.open(chemin).convert("RGB")
    im.thumbnail((320, 320))
    px = donnees(im)
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
    gris = donnees(petit)
    moy = sum(gris) / len(gris)
    sigma = (sum((g - moy) ** 2 for g in gris) / len(gris)) ** 0.5
    plissé = (max(gris) - moy) / sigma if sigma > 1 else 0.0
    # cadre : les bords doivent être plus sombres que le centre (premier plan qui cadre)
    bord = [gris[y * 16 + x] for y in range(9) for x in range(16) if x in (0, 1, 14, 15) or y in (0, 8)]
    centre = [gris[y * 16 + x] for y in range(2, 7) for x in range(4, 12)]
    cadre = (sum(bord) / len(bord)) / max(1.0, sum(centre) / len(centre))
    # densité de détail (fiches 01 et 16) : part de l'énergie de gradient dans les 10 % de cases les plus riches
    fin = im.convert("L").resize((64, 36), Image.Resampling.BOX)
    g = donnees(fin)
    grad = [[abs(g[y * 64 + x] - g[y * 64 + min(x + 1, 63)]) + abs(g[y * 64 + x] - g[min(y + 1, 35) * 64 + x]) for x in range(64)] for y in range(36)]
    cell = []
    for gy in range(9):
        for gx in range(16):
            cell.append(sum(grad[y][x] for y in range(gy * 4, gy * 4 + 4) for x in range(gx * 4, gx * 4 + 4)))
    total = sum(cell) or 1
    top = sum(sorted(cell, reverse=True)[:max(1, len(cell) // 10)]) / total
    bruit = sum(cell) / (64 * 36 * 255.0)
    # figure/fond (fiche 11) : la case la plus claire contre ses voisines
    lc = [lum(p) for p in donnees(petit.convert("RGB"))]
    ib = max(range(len(lc)), key=lambda i: lc[i])
    bx, by = ib % 16, ib // 16
    voisins = [lc[y * 16 + x] for y in range(max(0, by - 1), min(9, by + 2)) for x in range(max(0, bx - 1), min(16, bx + 2)) if (x, y) != (bx, by)]
    figure = abs(lc[ib] - sum(voisins) / len(voisins)) / 255 if voisins else 0.0
    # fiche 10 : les noirs gardent une teinte (jamais de noir pur) ; gamut limité (une zone restreinte du cercle chromatique)
    noir_pur = sum(1 for p in px if max(p) < 6) / n
    teintes = [colorsys.rgb_to_hsv(*(c / 255 for c in p)) for p in px]
    colores = [h for h, sa, v in teintes if sa > 0.25 and v > 0.15]
    gamut = 1.0
    if len(colores) > n * 0.05:
        hist = [0] * 12
        for h in colores:
            hist[int(h * 12) % 12] += 1
        gamut = max(hist[i] + hist[(i + 1) % 12] for i in range(12)) / len(colores)   # part dans 2 secteurs voisins de 30 degrés
    res = {
        "dominantes": dom,
        "luminance": round(sum(lums) / n / 255, 3),
        "saturation": round(sum(sats) / n, 3),
        "contraste_focal": round((max(cases) - med) / 255, 3),
        "yeux_plisses": round(plissé, 2),
        "detail_concentre": round(top, 2),
        "bruit": round(bruit, 3),
        "figure_fond": round(figure, 3),
        "noir_pur": round(noir_pur, 3),
        "gamut": round(gamut, 2),
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
    if res["luminance"] >= 0.04 and res["detail_concentre"] < 0.25:
        al.append("détail réparti partout (10 %% des cases portent %d %% du détail, 25 %%+ attendus) : le détail doit se concentrer au point focal" % round(100 * res["detail_concentre"]))
    if res["bruit"] > 0.10:
        al.append("image chargée (bruit %.2f) : trop d'information hors du point focal" % res["bruit"])
    if res["luminance"] >= 0.04 and res["figure_fond"] < 0.04:
        al.append("figure/fond : la zone la plus claire ne se détache pas de ses voisines")
    if sortie:
        x0, y0, x1, y1 = sortie
        zone = [lc[y * 16 + x] for y in range(int(y0 * 9), max(int(y0 * 9) + 1, int(y1 * 9 + 0.999))) for x in range(int(x0 * 16), max(int(x0 * 16) + 1, int(x1 * 16 + 0.999)))]
        res["sortie_lum"] = round(sum(zone) / len(zone) / 255, 3)
        if sum(zone) / len(zone) < 0.6 * max(lc):
            al.append("chemin non éclairé : la sortie est bien moins claire que la zone la plus claire de la vue")
    if res["noir_pur"] > 0.25:
        al.append("%d %% de noir pur : remonter les noirs vers ~95 %% pour qu'ils gardent une teinte (fiche 10)" % round(100 * res["noir_pur"]))
    if res["gamut"] < 0.5:
        al.append("couleurs dispersées sur le cercle chromatique (%d %% dans une zone de 60 degrés) : une teinte domine, le reste en accents" % round(100 * res["gamut"]))
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


def mesurer_dossier(dossier, fiche=None, palette=(), accent=None, sortie=None):
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
        r = mesurer(str(f), palette, accent, sortie)
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
    ap.add_argument("--sortie", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"), help="zone de la suite du chemin (fractions de l'image)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    pal, acc = list(a.palette), a.accent
    if a.fiche:
        p2, a2 = lire_fiche(a.fiche)
        pal, acc = pal or p2, acc or a2
    try:
        res = mesurer(a.capture, pal, acc, a.sortie)
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
