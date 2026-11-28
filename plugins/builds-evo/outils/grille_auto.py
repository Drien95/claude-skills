#!/usr/bin/env python3
"""Pré-remplit la grille de contrôle (build-evo/references/grille-controle.md) avec toutes les mesures gratuites.

Usage : python grille_auto.py <dossier de captures> [--fiche fiche-da.md] [--dupe dupe.txt|scene.json] [--sequence sequence.json]
                              [--mesures mesures.json] [--sortie x0 y0 x1 y1]
Sortie : une case par critère, [x] respecté, [ ] à corriger (avec les vues ou la cause), [?] à juger par un humain.
Elle ne note jamais : la note sur 10 et les critères de jugement restent à la critique. Les seuils sont ceux des fiches
(règles d'atelier, pas des lois).
"""
import argparse
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))


def _vues(dossier, palette, accent, sortie, sans_accent=()):
    import mesure_da
    res = {}
    for f in sorted(Path(dossier).iterdir()):
        if f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith(("planche", "color_script")):
            attendu = mesure_da.accent_attendu(f.stem, sans_accent)
            res[f.stem] = mesure_da.mesurer(str(f), palette, accent if attendu else None, sortie)
            res[f.stem]["accent_attendu"] = attendu
    return res


def _critere(libelle, res, ok):
    """Une case par critère mesuré vue par vue : [x] si toutes les vues passent, sinon les vues en défaut."""
    mauvaises = [v for v, r in res.items() if not ok(r)]
    if not mauvaises:
        return "- [x] %s (%d vue(s))" % (libelle, len(res))
    return "- [ ] %s : %d vue(s) sur %d en défaut (%s)" % (libelle, len(mauvaises), len(res), ", ".join(mauvaises[:5]))


def grille(dossier=None, fiche=None, dupe=None, sequence=None, mesures=None, sortie=None, sans_accent=()):
    import mesure_da
    palette, accent = [], None
    if fiche:
        palette, accent = mesure_da.lire_fiche(fiche)
    out = ["## Grille pré-remplie (mesures gratuites ; la note et le jugement restent à la critique)"]
    out.append("### 1. Image")
    if dossier:
        res = _vues(dossier, palette, accent, sortie, sans_accent)
        if res:
            out.append(_critere("point focal en moins de 2 s (yeux plissés)", res, lambda r: r["yeux_plisses"] >= 1.8 or r["luminance"] < 0.04))
            out.append(_critere("3 plans : bords plus sombres que le centre", res, lambda r: r["bords_sur_centre"] <= 1.15))
            out.append(_critere("une couleur domine (gamut), pas de noir pur", res, lambda r: r["gamut"] >= 0.5 and r["noir_pur"] <= 0.25))
            if accent:
                out.append(_critere("l'accent est présent et rare (moins de 8 %)", res, lambda r: r.get("accent_attendu") is False or 0 < r.get("part_accent", 0) <= 0.08))
            if palette:
                out.append(_critere("couleurs proches de la palette de la fiche DA", res, lambda r: r.get("ecart_palette", 0) <= 0.25))
            out.append(_critere("silhouettes lisibles (figure/fond) et détail concentré", res, lambda r: r["figure_fond"] >= 0.04 and r["detail_concentre"] >= 0.25))
            out.append(_critere("image calme hors du point focal (bruit)", res, lambda r: r["bruit"] <= 0.10))
            if sortie:
                out.append(_critere("la suite du chemin est la zone la plus claire", res, lambda r: "sortie_lum" in r and not any("chemin non éclairé" in a for a in r["alertes"])))
        else:
            out.append("- [?] aucune capture dans %s" % dossier)
    else:
        out.append("- [?] pas de dossier de captures")
    controle = None
    if dupe:
        import controle_auto
        erreurs, att, resume = controle_auto.controler(dupe)
        controle = (erreurs, att, resume)
        droits = [a for a in att if "parfaitement droits" in a]
        out.append("- [ ] rien de « carré par défaut » : " + droits[0] if droits else "- [x] rien de « carré par défaut » (props inclinés)")
    out += ["- [?] chaque usure a une cause, au moins un détail raconte (narration) : à juger",
            "- [?] une seule lumière clé claire, le reste subordonné : à juger"]
    out.append("### 2. Construction")
    if controle:
        erreurs, att, _ = controle
        flot = [a for a in att if "flotter" in a]
        out.append("- [ ] rien ne flotte : " + flot[0] if flot else "- [x] rien ne flotte")
        dehors = [e for e in erreurs if "hors de la boîte" in e]
        out.append("- [ ] dans la boîte : " + dehors[0] if dehors else "- [x] dans la boîte (si la boîte est connue)")
        refus = [a for a in att if "refusé" in a]
        out.append("- [ ] aucun modèle refusé : " + refus[0] if refus else "- [x] aucun modèle refusé")
    out.append("- [?] remplit le cadre, profil lisible, pas de PHX visible, joints, praticable : à juger sur les vues dédiées")
    out.append("### 3. Effets et son")
    if sequence:
        e, a = __import__("controle_sequence").controler(json.loads(Path(sequence).read_text(encoding="utf-8")))
        out.append("- [x] hiérarchie, anticipation, silence avant le sommet, paliers, ponctuels" if not (e or a)
                   else "- [ ] rythme : " + " ; ".join((e + a)[:3]))
    else:
        out.append("- [?] pas de séquence fournie (hiérarchie, anticipation, silence) : à juger")
    out.append("### 4. Coût")
    if controle:
        erreurs, _, resume = controle
        out.append("- [ ] posés dans le budget : " + "; ".join(x for x in erreurs if "posés" in x) if any("posés" in x for x in erreurs) else "- [x] posés dans le budget (%s)" % resume)
    if mesures:
        _, alertes = __import__("rapport_perf").controler(json.loads(Path(mesures).read_text(encoding="utf-8")))
        out.append("- [ ] coût du script : " + " ; ".join(alertes[:2]) if alertes else "- [x] coût du script (aucune alerte de performance)")
    else:
        out.append("- [?] coût du script (ms, dessins/image, 1 % pire) : pas de mesures fournies")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dossier", nargs="?")
    ap.add_argument("--fiche")
    ap.add_argument("--dupe")
    ap.add_argument("--sequence")
    ap.add_argument("--mesures")
    ap.add_argument("--sortie", nargs=4, type=float)
    ap.add_argument("--sans-accent", nargs="*", default=[], help="vues où l'accent est absent exprès (ex. canyon d'arrivée)")
    a = ap.parse_args(argv)
    try:
        print(grille(a.dossier, a.fiche, a.dupe, a.sequence, a.mesures, a.sortie, a.sans_accent))
    except ImportError:
        print("Pillow manque : pip install pillow", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print("ERREUR : %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
