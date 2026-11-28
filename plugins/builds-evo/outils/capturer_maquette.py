#!/usr/bin/env python3
"""Exporte des PNG d'une maquette (faire_maquette.py) sans l'ouvrir : une capture par vue et par mode, puis la mesure DA.

Usage : python capturer_maquette.py maquette.html [--sortie dossier] [--modes gris rendu] [--fiche fiche-da.md] [--temps 8]
Nécessite Playwright (pip install playwright ; playwright install chromium). Variables : MAQUETTE_CHROME (chemin d'un Chrome / Chromium),
MAQUETTE_THREE (dossier d'un `npm install three@0.128.0` pour travailler hors ligne). Les captures sont à lire par planche, après la mesure.
"""
import argparse
import base64
import os
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("maquette")
    ap.add_argument("--sortie", default="captures_maquette")
    ap.add_argument("--modes", nargs="+", default=["gris", "rendu"])
    ap.add_argument("--fiche")
    ap.add_argument("--temps", type=float, default=0.0, help="instant de la séquence (s) pour le mode rendu")
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright manque : pip install playwright && playwright install chromium", file=sys.stderr)
        return 2
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    three = os.environ.get("MAQUETTE_THREE")
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]}
        if os.environ.get("MAQUETTE_CHROME"):
            kw["executable_path"] = os.environ["MAQUETTE_CHROME"]
        nav = p.chromium.launch(**kw)
        page = nav.new_page(viewport={"width": 1280, "height": 720})
        if three:
            local = {"three.min.js": Path(three) / "build" / "three.min.js", "OrbitControls.js": Path(three) / "examples" / "js" / "controls" / "OrbitControls.js"}
            page.route("**/*", lambda r: r.fulfill(path=str(local[r.request.url.rsplit("/", 1)[-1]]), content_type="text/javascript")
                       if r.request.url.rsplit("/", 1)[-1] in local else r.continue_())
        page.goto(Path(a.maquette).resolve().as_uri())
        page.wait_for_function("window.maquette && window.maquette.pret", timeout=30000)
        nb = page.evaluate("maquette.vues.length")
        for mode in a.modes:
            page.evaluate("([m, t]) => { maquette.mode(m); maquette.temps(t); }", [mode, a.temps])
            for i in range(nb):
                page.evaluate("(i) => maquette.aller(i)", i)
                nom = page.evaluate("(i) => maquette.vues[i].nom", i)
                png = page.evaluate("() => maquette.capture()").split(",", 1)[1]
                (sortie / ("%s_%s.png" % (mode, nom))).write_bytes(base64.b64decode(png))
        nav.close()
    print("captures : %d dans %s" % (nb * len(a.modes), sortie))
    try:
        import mesure_da
        print(mesure_da.mesurer_dossier(str(sortie), a.fiche))
    except ImportError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
