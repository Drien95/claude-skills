#!/usr/bin/env python3
"""Calibre les seuils de la mesure DA sur les notes d'Adrien : à chaque planche notée, on garde les mesures et la note.

Usage :
  python calibration.py noter <dossier de captures> <note /10> [--version v8] [--piece trone] [--journal calibration.jsonl]
  python calibration.py analyser [--journal calibration.jsonl]
Journal par défaut : `.claude/builds-evo/calibration.jsonl` (JSON par ligne : version, pièce, note, moyennes des mesures sur les vues).
Analyse (6 planches notées au moins) : corrélation de chaque mesure avec les notes, et seuil qui sépare les planches >= 7,5 des autres.
Les seuils de `mesure_da.py` viennent des fiches ; cette analyse dit lesquels collent aux goûts d'Adrien. Elle ne modifie rien seule.
"""
import argparse
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
DEFAUT = Path(".claude") / "builds-evo" / "calibration.jsonl"
CLES = ["luminance", "saturation", "contraste_focal", "yeux_plisses", "detail_concentre", "bruit", "figure_fond", "noir_pur", "gamut", "bords_sur_centre", "part_accent", "ecart_palette"]
MINI = 6


def mesures_dossier(dossier):
    import mesure_da
    vues = [mesure_da.mesurer(str(f)) for f in sorted(Path(dossier).iterdir())
            if f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith(("planche", "color_script"))]
    if not vues:
        raise ValueError("aucune capture dans %s" % dossier)
    return {k: round(sum(v[k] for v in vues if k in v) / len([v for v in vues if k in v]), 4) for k in CLES if any(k in v for v in vues)}, len(vues)


def noter(dossier, note, version=None, piece=None, journal=DEFAUT):
    if not 0 <= note <= 10:
        raise ValueError("note entre 0 et 10")
    moyennes, n = mesures_dossier(dossier)
    j = Path(journal)
    j.parent.mkdir(parents=True, exist_ok=True)
    ligne = {"version": version, "piece": piece, "note": note, "vues": n, "mesures": moyennes}
    with open(j, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    total = len(j.read_text(encoding="utf-8").splitlines())
    return "planche notée %s/10 enregistrée (%d vue(s), %d au journal)" % (note, n, total)


def correlation(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def analyser(journal=DEFAUT):
    j = Path(journal)
    if not j.is_file():
        return "aucun journal (%s) : noter des planches d'abord" % j
    lignes = [json.loads(l) for l in j.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lignes) < MINI:
        return "%d planche(s) notée(s) : %d minimum pour analyser" % (len(lignes), MINI)
    out = ["%d planches notées (moyenne %.1f/10)" % (len(lignes), sum(l["note"] for l in lignes) / len(lignes))]
    res = []
    for k in CLES:
        pts = [(l["mesures"][k], l["note"]) for l in lignes if k in l["mesures"]]
        if len(pts) < MINI:
            continue
        c = correlation([p[0] for p in pts], [p[1] for p in pts])
        bons = [x for x, n in pts if n >= 7.5]
        autres = [x for x, n in pts if n < 7.5]
        seuil = None
        if bons and autres:
            seuil = (sum(bons) / len(bons) + sum(autres) / len(autres)) / 2
        res.append((abs(c), k, c, seuil, len(pts)))
    for _, k, c, seuil, n in sorted(res, reverse=True):
        force = "forte" if abs(c) >= 0.6 else "moyenne" if abs(c) >= 0.35 else "faible"
        out.append("%-18s corrélation %+.2f (%s, %d planches)%s" % (k, c, force, n, ("  seuil 7,5 vers %.3f" % seuil) if seuil is not None and abs(c) >= 0.35 else ""))
    out.append("Corrélation forte = la mesure suit ses goûts : régler `mesure_da.py` sur le seuil proposé. Faible = l'alerte n'est pas un bon signal pour lui.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("noter")
    n.add_argument("dossier")
    n.add_argument("note", type=float)
    n.add_argument("--version")
    n.add_argument("--piece")
    n.add_argument("--journal", default=str(DEFAUT))
    a = sp.add_parser("analyser")
    a.add_argument("--journal", default=str(DEFAUT))
    x = ap.parse_args(argv)
    try:
        print(noter(x.dossier, x.note, x.version, x.piece, x.journal) if x.cmd == "noter" else analyser(x.journal))
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print("ERREUR : %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
