#!/usr/bin/env python3
"""Une passe de maquette en UNE commande (un seul appel du modèle) : maquette, captures aux temps forts, mesures, grille, color script.

Usage : python passe_maquette.py scene.json --fiche fiche-da.md --vues vues.json --sequence sequence.json
                                 [--temps 60 700 1012] [--vue-cs mj] [--dossier passe] [--titre Nom]
Écrit <dossier>/maquette.html, <dossier>/t<temps>/ (captures rendu), <dossier>/gris/ (forme), <dossier>/grille.md, <dossier>/color_script.png
et imprime un résumé court : alertes seulement. Sans --temps : le sommet de la séquence (et 0 s). Lire ce résumé, pas les images ;
la planche ne se lit qu'à la critique.
"""
import argparse
import contextlib
import io
import json
import shutil
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))


def _taire(f, *a, **k):
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        code = f(*a, **k)
    return code, tampon.getvalue()


def filtrer(ligne, au_sommet):
    """Hors du sommet, l'accent absent est normal (l'effet n'a pas commencé) : on retire cette alerte, et la ligne si elle n'a plus rien."""
    if au_sommet or "|" not in ligne:
        return ligne
    tete, _, alertes = ligne.partition(" | ")
    reste = [x for x in alertes.split(" ; ") if x != "l'accent est absent de la vue"]
    return tete + " | " + " ; ".join(reste) if reste else ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scene")
    ap.add_argument("--fiche")
    ap.add_argument("--vues")
    ap.add_argument("--sequence")
    ap.add_argument("--temps", nargs="*", type=float)
    ap.add_argument("--vue-cs", help="vue du color script (défaut : la dernière)")
    ap.add_argument("--dossier", default="passe")
    ap.add_argument("--titre")
    a = ap.parse_args(argv)
    import capturer_maquette
    import faire_maquette
    import grille_auto
    d = Path(a.dossier)
    d.mkdir(parents=True, exist_ok=True)
    opt = sum((["--" + k, v] for k, v in (("fiche", a.fiche), ("vues", a.vues), ("sequence", a.sequence), ("titre", a.titre)) if v), [])
    code, _ = _taire(faire_maquette.main, [a.scene, "--sortie", str(d / "maquette.html")] + opt)
    if code:
        return code
    seq = json.loads(Path(a.sequence).read_text(encoding="utf-8")) if a.sequence else {}
    temps = a.temps or sorted({0.0, float(seq.get("sommet", 0))})
    vues = json.loads(Path(a.vues).read_text(encoding="utf-8")).get("vues", []) if a.vues else []
    sans_accent = [v["nom"] for v in vues if v.get("sans_accent")]
    resume = []
    code, sortie = _taire(capturer_maquette.main, [str(d / "maquette.html"), "--sortie", str(d / "gris"), "--modes", "gris"])
    if code:
        return code
    resume += [l for l in sortie.splitlines() if l.startswith("ATTENTION")]
    cs = d / "color_script"
    shutil.rmtree(cs, ignore_errors=True)
    cs.mkdir()
    t_sommet = min(temps, key=lambda x: abs(x - float(seq.get("sommet", max(temps)))))
    vue_cs = a.vue_cs or (vues[-1]["nom"] if vues else None)
    for t in temps:
        sous = d / ("t%04d" % t)
        code, sortie = _taire(capturer_maquette.main, [str(d / "maquette.html"), "--sortie", str(sous), "--modes", "rendu", "--temps", str(t)] + (["--fiche", a.fiche] if a.fiche else []))
        if code:
            return code
        resume += ["t %g s : %s" % (t, l) for l in (filtrer(x, t == t_sommet) for x in sortie.splitlines() if "|" in x) if l]
        img = sous / ("rendu_%s.png" % vue_cs) if vue_cs else next(sous.glob("rendu_*.png"), None)
        if img and img.exists():
            shutil.copy(img, cs / ("t%04d.png" % t))
    sommet = d / ("t%04d" % t_sommet)
    try:
        g = grille_auto.grille(str(sommet), a.fiche, a.scene, a.sequence, None, None, sans_accent)
    except ImportError:
        g = "Pillow manque : pip install pillow"
    (d / "grille.md").write_text(g, encoding="utf-8")
    resume += [l for l in g.splitlines() if l.startswith("- [ ]")]
    if len(list(cs.iterdir())) >= 2:
        import color_script
        _, sortie = _taire(color_script.main, [str(cs), "--sortie", str(d / "color_script.png")])
        resume += [l for l in sortie.splitlines() if l.startswith("ATTENTION")]
    print("passe : %s (%d temps, %d alerte(s)) ; détail dans grille.md" % (d, len(temps), len(resume)))
    print("\n".join(resume) if resume else "aucune alerte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
