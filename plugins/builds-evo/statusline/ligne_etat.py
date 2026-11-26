"""Ligne d'état Claude Code pour les builds EVO (0 token : elle tourne sur le PC).

Affiche :  Lac noir › Cathédrale v10 · 218/400 posés · pièce 74/90 · planche 2/3 · note 7,5 · Opus · contexte 34 %

Elle lit le fichier d'état de la pièce en cours, `.claude/builds-evo/piece.json`, cherché depuis le
dossier de la session vers le haut. Ce fichier est écrit par /builds-evo:nouvelle-piece et mis à jour
à chaque version (skill build-evo). Sans pièce en cours, seule la fin de la ligne s'affiche.

Installation (avec l'accord d'Adrien), dans ~/.claude/settings.json :
  "statusLine": {"type": "command",
                 "command": "python C:/Project/claude-skills/plugins/builds-evo/statusline/ligne_etat.py"}
"""
import json
import sys
from pathlib import Path

ETAT = Path(".claude") / "builds-evo" / "piece.json"


def trouver_etat(depart):
    d = Path(depart or ".").resolve()
    for dossier in [d, *d.parents]:
        f = dossier / ETAT
        if f.is_file():
            return f
    return None


def nombre(v):
    if isinstance(v, float):
        return ("%.1f" % v).rstrip("0").rstrip(".").replace(".", ",")
    return str(v)


def ligne(entree):
    morceaux = []
    dossier = (entree.get("workspace") or {}).get("current_dir") or entree.get("cwd")
    f = trouver_etat(dossier)
    if f:
        try:
            e = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            e = {}
        titre = " › ".join(x for x in (e.get("scene"), e.get("piece")) if x)
        if e.get("version"):
            titre += " v%s" % e["version"]
        if titre:
            morceaux.append(titre)
        if e.get("poses_scene") is not None:
            morceaux.append("%s/400 posés" % e["poses_scene"])
        if e.get("poses_piece") is not None:
            morceaux.append("pièce %s%s" % (e["poses_piece"], "/%s" % e["budget"] if e.get("budget") else ""))
        if e.get("planche") is not None:
            morceaux.append("planche %s/3" % e["planche"])
        if e.get("note") is not None:
            n = e["note"]
            marque = "" if not isinstance(n, (int, float)) or n >= 7.5 else " ↓"
            morceaux.append("note %s%s" % (nombre(n), marque))
    modele = (entree.get("model") or {}).get("display_name")
    if modele:
        morceaux.append(modele)
    ctx = entree.get("context_window") or {}
    pct = ctx.get("used_percentage")
    if pct is None and ctx.get("total_input_tokens") and ctx.get("context_window_size"):
        pct = 100.0 * ctx["total_input_tokens"] / ctx["context_window_size"]
    if pct is not None:
        morceaux.append("contexte %d %%" % round(pct))
    return " · ".join(morceaux)


def main():
    try:
        entree = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except ValueError:
        entree = {}
    texte = ligne(entree)
    sys.stdout.buffer.write(texte.encode("utf-8"))


if __name__ == "__main__":
    main()
