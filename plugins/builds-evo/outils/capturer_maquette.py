#!/usr/bin/env python3
"""Exporte des PNG d'une maquette (faire_maquette.py) sans l'ouvrir : une capture par vue et par mode, puis la mesure DA.

Usage : python capturer_maquette.py maquette.html [--sortie dossier] [--modes gris rendu] [--fiche fiche-da.md] [--temps 8]
Nécessite Playwright (pip install playwright). Navigateur et three trouvés seuls (Chromium de /opt/pw-browsers en session cloud ; three@0.128.0 installé
par npm dans le dossier temporaire si le CDN est bloqué) ; sinon MAQUETTE_CHROME et MAQUETTE_THREE. Signale les vues bouchées (un prop entre la caméra et
sa cible) et ne cherche pas l'accent dans les vues `"sans_accent": true` de vues.json ni en mode gris. Les captures sont à lire par planche, après la mesure.
"""
import argparse
import base64
import os
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))


CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"


def trouver_chrome():
    """MAQUETTE_CHROME, sinon le Chromium préinstallé des sessions cloud (/opt/pw-browsers), sinon celui de Playwright."""
    if os.environ.get("MAQUETTE_CHROME"):
        return os.environ["MAQUETTE_CHROME"]
    import glob
    for motif in ("/opt/pw-browsers/chromium-*/**/chrome", "/opt/pw-browsers/chromium*/chrome-linux*/chrome"):
        trouves = sorted(glob.glob(motif, recursive=True))
        if trouves:
            return trouves[-1]
    return None


def trouver_three():
    """MAQUETTE_THREE, sinon un three r128 local connu ; si le CDN est bloqué (cloud), installe three@0.128.0 par npm dans le dossier temporaire."""
    import shutil
    import tempfile
    import urllib.request
    if os.environ.get("MAQUETTE_THREE"):
        return os.environ["MAQUETTE_THREE"]
    cache = Path(tempfile.gettempdir()) / "maquette-three"
    try:
        ici = Path(os.getcwd())
    except OSError:
        ici = cache
    for c in (ici / "node_modules" / "three", ICI / "maquette" / "node_modules" / "three", cache / "node_modules" / "three"):
        if (c / "build" / "three.min.js").exists():
            return str(c)
    try:
        urllib.request.urlopen(CDN, timeout=5).close()
        return None
    except Exception:
        pass
    if shutil.which("npm"):
        import subprocess
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "install", "--silent", "--prefix", str(cache), "three@0.128.0"], capture_output=True, timeout=180)
        if (cache / "node_modules" / "three" / "build" / "three.min.js").exists():
            return str(cache / "node_modules" / "three")
    print("three.js injoignable (CDN bloqué, pas de npm) : définir MAQUETTE_THREE", file=sys.stderr)
    return None


BOUCHEE = """() => { murs.updateMatrixWorld(true); const v = D.vues[vueCourante]; const cible = C(v.vise);
  const dir = cible.clone().sub(camera.position); const loin = dir.length();
  const h = new THREE.Raycaster(camera.position, dir.normalize(), 1, loin).intersectObjects(murs.children)[0];
  return h && h.distance < 0.6 * loin ? [D.props[murs.children.indexOf(h.object)].note || '?', Math.round(h.distance), Math.round(loin)] : null; }"""


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
    three = trouver_three()
    bouchees, sans_accent = [], []
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]}
        if trouver_chrome():
            kw["executable_path"] = trouver_chrome()
        nav = p.chromium.launch(**kw)
        page = nav.new_page(viewport={"width": 1280, "height": 720})
        if three:
            local = {"three.min.js": Path(three) / "build" / "three.min.js", "OrbitControls.js": Path(three) / "examples" / "js" / "controls" / "OrbitControls.js"}
            page.route("**/*", lambda r: r.fulfill(path=str(local[r.request.url.rsplit("/", 1)[-1]]), content_type="text/javascript")
                       if r.request.url.rsplit("/", 1)[-1] in local else r.continue_())
        page.goto(Path(a.maquette).resolve().as_uri())
        page.wait_for_function("window.maquette && window.maquette.pret", timeout=30000)
        nb = page.evaluate("maquette.vues.length")
        sans_accent = page.evaluate("maquette.vues.filter((v) => v.sans_accent).map((v) => v.nom)")
        for i in range(nb):
            page.evaluate("(i) => maquette.aller(i)", i)
            b = page.evaluate(BOUCHEE)
            if b:
                bouchees.append("vue bouchée : « %s » à %d u sur %d (caméra → cible) ; déplacer le prop ou la caméra" % (page.evaluate("(i) => maquette.vues[i].nom", i) + " » par « " + b[0], b[1], b[2]))
        for mode in a.modes:
            page.evaluate("([m, t]) => { maquette.mode(m); maquette.temps(t); }", [mode, a.temps])
            for i in range(nb):
                page.evaluate("(i) => maquette.aller(i)", i)
                nom = page.evaluate("(i) => maquette.vues[i].nom", i)
                png = page.evaluate("() => maquette.capture()").split(",", 1)[1]
                (sortie / ("%s_%s.png" % (mode, nom))).write_bytes(base64.b64decode(png))
        nav.close()
    print("captures : %d dans %s" % (nb * len(a.modes), sortie))
    for b in bouchees:
        print("ATTENTION : " + b)
    try:
        import mesure_da
        print(mesure_da.mesurer_dossier(str(sortie), a.fiche, sans_accent=sans_accent))
    except ImportError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
