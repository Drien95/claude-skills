#!/usr/bin/env python3
"""Maquette three.js jetable d'une pièce (étape 7 de build-evo) générée depuis le dupe ou le scene.json : 0 jeton.

Usage : python faire_maquette.py <dupe.txt|scene.json> [--fiche fiche-da.md] [--vues vues.json] [--sequence sequence.json]
                                 [--sortie maquette.html] [--brume 0.00035] [--titre Nom]
Contenu : chaque prop en boîte d'après `bornes_modeles.json` (gris) ; un humain de 72 u ; les caméras de `vues.json` (format du banc :
{"vues": [{"nom", "pos", "vise", "fov"?}]}, coordonnées relatives à la pièce de tête) ; mode « rendu » (brume, lumière clé et accent tirés de la palette en hex
de la fiche DA, courbe d'intensité de la séquence). Effets du script (`"script"` du scene.json : nom, forme boite|cylindre, pos, taille [x, y, h], lacet,
couleur, debut, fin en s) dessinés en volumes lumineux, en mode rendu seulement, pendant leur fenêtre : 0 posé, juste pour juger la timeline.
`"brumes": [[t, "#hex"], ...]` dans sequence.json : couleur de brume et de ciel par palier (sinon la dominante), pour que le color script juge les temps forts. Sans vues, des caméras par défaut (entrée, 3/4, dessus) sont posées.
Ouvrir le .html dans un navigateur, ou `capturer_maquette.py` pour exporter des PNG sans rien ouvrir. Bornes absentes : boîte de 47,4 u.
"""
import argparse
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import controle_auto  # noqa: E402

C3 = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]    # Source (x, y, z haut) -> three (x, z, -y)


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _t(a):
    return [list(r) for r in zip(*a)]


def prop(e, bornes):
    b = bornes.get(e["modele"]) or {"min": [-23.7] * 3, "max": [23.7] * 3}
    mn, mx = b["min"], b["max"]
    s = e["echelle"] or 1
    m = controle_auto.matrice(e["ang"])
    Mt = _mul(_mul(C3, m), _t(C3))
    cl = [sum(C3[i][k] * (mn[k] + mx[k]) / 2 for k in range(3)) for i in range(3)]
    taille = [abs(sum(C3[i][k] * (mx[k] - mn[k]) for k in range(3))) * s for i in range(3)]
    pos = [sum(C3[i][k] * e["pos"][k] for k in range(3)) for i in range(3)]
    # matrice monde 4x4 (rangées) : T(pos) · R(Mt) · translation(s · cl)
    t = [pos[i] + sum(Mt[i][k] * s * cl[k] for k in range(3)) for i in range(3)]
    flat = Mt[0] + [t[0]] + Mt[1] + [t[1]] + Mt[2] + [t[2]] + [0, 0, 0, 1]
    haut = sum(abs(Mt[1][k]) * taille[k] / 2 for k in range(3))
    return {"taille": [round(x, 2) for x in taille], "m": [round(x, 4) for x in flat]}, t[1] - haut


def donnees(chemin, fiche=None, vues=None, sequence=None, brume=0.00035, titre=None):
    ents = controle_auto.lire_scene(chemin) if str(chemin).lower().endswith(".json") else controle_auto.lire_dupe(chemin)
    bornes = controle_auto.charger_bornes()
    props, bas = [], []
    scene_couleurs = {}
    if str(chemin).lower().endswith(".json"):
        for e in json.loads(Path(chemin).read_text(encoding="utf-8")).get("ents") or []:
            scene_couleurs[(e.get("note"), str(e.get("model", "")).lower())] = e.get("color")
    for e in ents:
        if not e["modele"]:
            continue
        p, b = prop(e, bornes)
        p["couleur"] = scene_couleurs.get((e["note"], e["modele"]))
        p["note"] = e["note"] or e["modele"].rsplit("/", 1)[-1]
        props.append(p)
        bas.append(b)
    palette = {"dominante": None, "neutres": [], "accent": None}
    if fiche:
        import mesure_da
        base, accent = mesure_da.lire_fiche(fiche)
        palette = {"dominante": base[0] if base else None, "neutres": base[1:3], "accent": accent}
    v = []
    if vues:
        v = json.loads(Path(vues).read_text(encoding="utf-8")).get("vues") or []
    if not v:
        v = [{"nom": "entree", "pos": [-900, 0, 63], "vise": [0, 0, 150]}, {"nom": "trois_quarts", "pos": [-700, -700, 300], "vise": [0, 0, 100]},
             {"nom": "dessus", "pos": [0, -300, 1800], "vise": [0, 0, 0]}]
    seq = json.loads(Path(sequence).read_text(encoding="utf-8")) if sequence else {}
    script = []
    if str(chemin).lower().endswith(".json"):
        d = json.loads(Path(chemin).read_text(encoding="utf-8"))
        tete = next((e for e in d.get("ents") or [] if e.get("note") == d.get("head")), None)
        hp = tete["pos"] if tete else (0, 0, 0)
        for x in d.get("script") or []:
            r = [x["pos"][j] - hp[j] for j in range(3)]
            script.append({"nom": x.get("nom", "?"), "forme": x.get("forme", "boite"), "pos": [sum(C3[i][k] * r[k] for k in range(3)) for i in range(3)],
                           "taille": x.get("taille", [50, 50, 50]), "couleur": x.get("couleur") or palette["accent"] or "#ffffff",
                           "lacet": x.get("lacet", 0), "debut": x.get("debut", 0), "fin": x.get("fin", 1e9)})
    ev = [{"t": e.get("t", 0), "nom": e.get("nom", "?")} for e in seq.get("evenements") or []]
    return {"titre": titre or Path(chemin).stem, "props": props, "sol": round(min(bas), 2) if bas else 0, "humain": [-250, -120, 0], "palette": palette,
            "vues": v, "courbe": seq.get("courbe") or [], "brumes": seq.get("brumes") or [], "evenements": ev, "duree": seq.get("sommet", 10) * 1.3 if seq else 10,
            "brume": brume, "accent_pos": [0, 0, 150], "script": script}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scene")
    ap.add_argument("--fiche")
    ap.add_argument("--vues")
    ap.add_argument("--sequence")
    ap.add_argument("--sortie", default="maquette.html")
    ap.add_argument("--brume", type=float, default=0.00035)
    ap.add_argument("--titre")
    a = ap.parse_args(argv)
    try:
        d = donnees(a.scene, a.fiche, a.vues, a.sequence, a.brume, a.titre)
    except (OSError, ValueError, KeyError) as e:
        print("ERREUR : %s" % e, file=sys.stderr)
        return 2
    html = (ICI / "maquette" / "modele.html").read_text(encoding="utf-8")
    html = html.replace("__TITRE__", d["titre"].replace("<", "")).replace("__DONNEES__", json.dumps(d, ensure_ascii=False))
    Path(a.sortie).write_text(html, encoding="utf-8")
    print("maquette : %s (%d props, %d vues)" % (a.sortie, len(d["props"]), len(d["vues"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
