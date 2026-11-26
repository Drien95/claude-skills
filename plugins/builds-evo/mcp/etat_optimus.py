"""Note d'état des builds dans le coffre Obsidian OPTIMUS, écrite par le banc après chaque planche (0 token).

Contrat :
  ecrire(planches, depart) -> str   une ligne de compte rendu ; ne lève jamais (la planche ne doit pas échouer
                                    à cause de la note).
  Entrées : l'état de la pièce `.claude/builds-evo/piece.json` (le même que la ligne d'état, cherché depuis
  `depart` vers le haut, sinon BUILDS_EVO_PIECE, sinon le projet Adler Lore) et les chemins des planches.
  Sortie : `<OPTIMUS>/03-builds/etat-builds.md` (OPTIMUS_DIR, sinon C:\\Project\\OPTIMUS), conforme au contrôle
  du coffre (en-tête YAML, résumé, moins de 4 Ko). Description et statut ne changent jamais : l'INDEX du coffre
  ne bouge qu'à la création de la note (on le régénère alors). Obsidian Git pousse la note sur main.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PIECE = Path(".claude") / "builds-evo" / "piece.json"
PIECE_DEFAUT = Path(r"C:\Project\Adler_lore") / PIECE
NOTE = Path("03-builds") / "etat-builds.md"
HISTORIQUE_MAX = 10  # lignes « Dernières planches » gardées (taille bornée)
DESCRIPTION = ("État des builds, écrit automatiquement par le banc après chaque planche : pièce, version, "
               "note, posés sur 400, dernière planche")
TITRE_HISTO = "## Dernières planches"


def coffre():
    return Path(os.environ.get("OPTIMUS_DIR", r"C:\Project\OPTIMUS"))


def trouver_piece(depart):
    if os.environ.get("BUILDS_EVO_PIECE"):
        return Path(os.environ["BUILDS_EVO_PIECE"])
    d = Path(depart or ".").resolve()
    for dossier in [d, *d.parents]:
        if (dossier / PIECE).is_file():
            return dossier / PIECE
    return PIECE_DEFAUT


def nombre(v):
    if isinstance(v, float):
        return ("%.1f" % v).rstrip("0").rstrip(".").replace(".", ",")
    return "?" if v is None else str(v)


def lien_fichier(chemin):
    return "[%s](<file:///%s>)" % (Path(chemin).name, str(chemin).replace("\\", "/"))


def historique(ancien):
    """Lignes « - ... » sous le titre de l'historique de l'ancienne note."""
    if TITRE_HISTO not in ancien:
        return []
    bloc = ancien.split(TITRE_HISTO, 1)[1]
    return [l for l in bloc.splitlines() if l.startswith("- ")]


def texte_note(e, planches, ancien, maintenant):
    titre = " › ".join(str(x) for x in (e.get("scene"), e.get("piece")) if x) or "pièce inconnue"
    version = "v%s" % e["version"] if e.get("version") is not None else ""
    note = e.get("note")
    sous_seuil = isinstance(note, (int, float)) and note < 7.5
    jour, heure = time.strftime("%d/%m/%Y", maintenant), time.strftime("%H:%M", maintenant)
    derniere = planches[0] if planches else ""
    ligne_histo = "- %s %s · %s %s · note %s · %s" % (jour, heure, titre, version, nombre(note),
                                                      lien_fichier(derniere) if derniere else "sans planche")
    histo = ([ligne_histo] + historique(ancien))[:HISTORIQUE_MAX]
    budget = "/%s" % e["budget"] if e.get("budget") is not None else ""
    l = ["---", 'description: "%s"' % DESCRIPTION, "domaine: builds", "type: reference", "statut: actif",
         "maj: %s" % time.strftime("%Y-%m-%d", maintenant), "---", "",
         "> [!resume] Pour le prochain fil",
         "> Écrite par le banc à chaque planche : ne pas éditer à la main. En cours : %s %s, note %s/10%s." % (
             titre, version, nombre(note), " (sous 7,5)" if sous_seuil else ""),
         "> Dernière planche le %s à %s." % (jour, heure), "",
         "# État des builds", "",
         "| | |", "|---|---|",
         "| Pièce | %s %s |" % (titre, version),
         "| Note | %s/10%s |" % (nombre(note), " ↓ sous 7,5" if sous_seuil else ""),
         "| Posés de la scène | %s/400 |" % nombre(e.get("poses_scene")),
         "| Posés de la pièce | %s%s |" % (nombre(e.get("poses_piece")), budget),
         "| Planche n° | %s/3 |" % nombre(e.get("planche")),
         "| Dernière planche | %s |" % (lien_fichier(derniere) if derniere else "aucune"),
         "| Mise à jour | %s à %s |" % (jour, heure), ""]
    if len(planches) > 1:
        l += ["Autres pages : " + ", ".join(lien_fichier(p) for p in planches[1:]), ""]
    l += [TITRE_HISTO, ""] + histo + [""]
    return "\n".join(l)


def ecrire_atomique(chemin, texte):
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(texte, encoding="utf-8", newline="\n")
    os.replace(tmp, chemin)


def regenerer_index(racine):
    script = racine / "scripts" / "optimus.py"
    if not script.is_file():
        return "index du coffre non régénéré (scripts/optimus.py absent)"
    r = subprocess.run([sys.executable, str(script), "index"], cwd=str(racine), capture_output=True, timeout=60,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return "index du coffre régénéré" if r.returncode == 0 else "ERREUR : index du coffre non régénéré"


def ecrire(planches, depart=None, maintenant=None):
    try:
        racine = coffre()
        if not (racine / "03-builds").is_dir():
            return "note d'état : coffre OPTIMUS absent (%s), rien écrit" % racine
        f = trouver_piece(depart)
        try:
            e = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
        except ValueError:
            e = {}
        if not isinstance(e, dict):
            e = {}
        cible = racine / NOTE
        nouvelle = not cible.exists()
        ancien = "" if nouvelle else cible.read_text(encoding="utf-8")
        ecrire_atomique(cible, texte_note(e, [str(p) for p in planches], ancien, maintenant or time.localtime()))
        suite = (" ; " + regenerer_index(racine)) if nouvelle else ""
        return "note d'état écrite : %s%s" % (cible, suite)
    except (OSError, subprocess.SubprocessError) as err:
        return "ERREUR note d'état : %s" % re.sub(r"\s+", " ", str(err))[:200]
