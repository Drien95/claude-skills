"""Tableau de bord des builds dans le coffre Obsidian OPTIMUS, écrit par le banc après chaque planche (0 token).

Contrat :
  ecrire(planches, depart, maintenant) -> str   une ligne de compte rendu ; ne lève jamais (la planche ne doit pas
                                                échouer à cause du tableau).
  Entrées : l'état de la pièce `.claude/builds-evo/piece.json` (le même que la ligne d'état, cherché depuis `depart`
  vers le haut, sinon BUILDS_EVO_PIECE, sinon le projet Adler Lore) et les chemins des planches.
  Champ facultatif de piece.json : `pieces_scene` (nombre de pièces prévues dans la scène) pour l'avancement x/N.
  Sortie : `<OPTIMUS>/03-builds/etat-builds.md` (OPTIMUS_DIR, sinon C:\\Project\\OPTIMUS), Obsidian natif sans plugin :
  encadrés (callouts) colorés par la note (vert dès 7,5, orange dès 6, rouge en dessous), barres en texte, vignette
  de la dernière planche. Les données des pièces vivent dans un commentaire Obsidian `%% banc: {...} %%` en fin de
  note (invisible à la lecture). Les vignettes vont dans `03-builds/vignettes/`, exclu de git en local
  (.git/info/exclude) : rien de lourd n'est poussé. Description et statut fixes : l'INDEX du coffre ne bouge qu'à la
  création de la note. Taille gardée sous la limite du contrôle du coffre.
"""
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

PIECE = Path(".claude") / "builds-evo" / "piece.json"
PIECE_DEFAUT = Path(r"C:\Project\Adler_lore") / PIECE
NOTE = Path("03-builds") / "etat-builds.md"
VIGNETTES = Path("03-builds") / "vignettes"
SEUIL = 7.5
LIMITE_POSES = 400
HISTORIQUE_MAX = 8      # lignes « Dernières planches »
SCENES_MAX = 4          # scènes gardées dans les données (la plus récente en détail)
TAILLE_VISEE = 3900     # sous l'alerte de 4000 octets du contrôle du coffre
LARGEUR_VIGNETTE = 960
DESCRIPTION = ("État des builds, écrit automatiquement par le banc après chaque planche : pièce, version, "
               "note, posés sur 400, dernière planche")
TITRE_HISTO = "## Dernières planches"
DONNEES = re.compile(r"^%% banc: (\{.*\}) %%$", re.M)


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


def barre(valeur, maximum, cases=10):
    if not isinstance(valeur, (int, float)) or not maximum:
        return "`" + "░" * cases + "`"
    plein = max(0.0, min(1.0, valeur / maximum)) * cases
    entier, demi = int(plein), (plein - int(plein)) >= 0.5
    return "`" + "█" * entier + ("▌" if demi else "") + "░" * (cases - entier - (1 if demi else 0)) + "`"


def couleur(note):
    if not isinstance(note, (int, float)):
        return "note"           # gris-bleu : pas encore notée
    return "success" if note >= SEUIL else "warning" if note >= 6 else "danger"


def slug(texte):
    t = unicodedata.normalize("NFKD", str(texte)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "piece"


def lien_fichier(chemin):
    return "[%s](<file:///%s>)" % (Path(chemin).name, str(chemin).replace("\\", "/"))


# --- données ---------------------------------------------------------------------------------------------

def lire_donnees(ancien):
    m = DONNEES.search(ancien)
    if m:
        try:
            d = json.loads(m.group(1))
            if isinstance(d, dict):
                return {"scenes": d.get("scenes") or [], "histo": d.get("histo") or []}
        except ValueError:
            pass
    vieux = ancien.split(TITRE_HISTO, 1)[1].splitlines() if TITRE_HISTO in ancien else []
    return {"scenes": [], "histo": [l[2:] for l in vieux if l.startswith("- ")][:HISTORIQUE_MAX]}


def mettre_a_jour(donnees, e, planches, vignette, quand):
    nom_scene, nom_piece = e.get("scene") or "Scène inconnue", e.get("piece") or "pièce inconnue"
    scenes = [s for s in donnees["scenes"] if s.get("nom") != nom_scene]
    scene = next((s for s in donnees["scenes"] if s.get("nom") == nom_scene), {"nom": nom_scene, "pieces": []})
    pieces = [p for p in scene.get("pieces", []) if p.get("nom") != nom_piece]
    piece = {"nom": nom_piece, "v": e.get("version"), "note": e.get("note"), "pp": e.get("poses_piece"),
             "b": e.get("budget"), "pl": e.get("planche"), "q": quand, "img": vignette,
             "planche": planches[0] if planches else ""}
    scene.update(pieces=[piece] + pieces, poses=e.get("poses_scene"), q=quand)
    if e.get("pieces_scene"):
        scene["total"] = e["pieces_scene"]
    donnees["scenes"] = ([scene] + scenes)[:SCENES_MAX]
    ligne = "%s · %s › %s v%s · note %s · %s" % (quand, nom_scene, nom_piece, nombre(e.get("version")),
                                                 nombre(e.get("note")),
                                                 lien_fichier(planches[0]) if planches else "sans planche")
    donnees["histo"] = ([ligne] + donnees["histo"])[:HISTORIQUE_MAX]
    return donnees


# --- rendu -----------------------------------------------------------------------------------------------

def encadre_piece(p, ouverte):
    note = p.get("note")
    budget = p.get("b")
    titre = "%s · v%s · note %s/10" % (p["nom"], nombre(p.get("v")), nombre(note))
    l = ["> [!%s]%s %s" % (couleur(note), "+" if ouverte else "-", titre),
         "> Note %s %s / 10 · seuil 7,5%s" % (barre(note, 10), nombre(note),
                                              " ✓" if isinstance(note, (int, float)) and note >= SEUIL else ""),
         "> Posés %s %s%s · planche %s/3" % (barre(p.get("pp"), budget), nombre(p.get("pp")),
                                             "/%s" % budget if budget else "", nombre(p.get("pl"))),
         "> Mise à jour %s · %s" % (p.get("q", "?"), lien_fichier(p["planche"]) if p.get("planche") else "sans planche")]
    if ouverte and p.get("img"):
        l.append("> ![planche|%d](%s)" % (480, p["img"]))
    return l


def rendu(donnees, maintenant, detail_scenes=True, avec_histo=True):
    scenes = donnees["scenes"]
    courante = scenes[0] if scenes else None
    p0 = courante["pieces"][0] if courante and courante.get("pieces") else {}
    l = ["---", 'description: "%s"' % DESCRIPTION, "domaine: builds", "type: reference", "statut: actif",
         "maj: %s" % time.strftime("%Y-%m-%d", maintenant), "---", "",
         "> [!resume] Pour le prochain fil",
         "> Tableau écrit par le banc à chaque planche : ne pas éditer à la main. En cours : %s › %s v%s, note %s/10." % (
             courante["nom"] if courante else "aucune scène", p0.get("nom", "?"), nombre(p0.get("v")),
             nombre(p0.get("note"))),
         "> Dernière mise à jour le %s." % time.strftime("%d/%m/%Y à %H:%M", maintenant), "",
         "# Tableau de bord des builds", ""]
    for i, s in enumerate(scenes):
        valides = sum(1 for p in s.get("pieces", []) if isinstance(p.get("note"), (int, float)) and p["note"] >= SEUIL)
        total = s.get("total")
        avancement = ("%s %d/%s pièces validées" % (barre(valides, total), valides, total) if total
                      else "%d pièce(s) validée(s) sur %d suivie(s)" % (valides, len(s.get("pieces", []))))
        if i == 0 or detail_scenes:
            l += ["> [!abstract]%s %s" % ("+" if i == 0 else "-", s["nom"]),
                  "> Avancement %s" % avancement,
                  "> Posés de la scène %s %s/%d" % (barre(s.get("poses"), LIMITE_POSES), nombre(s.get("poses")),
                                                    LIMITE_POSES), ""]
        if i == 0:
            for j, p in enumerate(s.get("pieces", [])):
                l += encadre_piece(p, ouverte=(j == 0)) + [""]
        elif not detail_scenes:
            l += ["- %s : %s · %s/%d posés" % (s["nom"], avancement, nombre(s.get("poses")), LIMITE_POSES)]
    if avec_histo and donnees["histo"]:
        l += ["", TITRE_HISTO, ""] + ["- " + h for h in donnees["histo"]]
    l += ["", "%% banc: " + json.dumps(donnees, ensure_ascii=False, separators=(",", ":")) + " %%", ""]
    return "\n".join(l)


def texte_borne(donnees, maintenant):
    """Rendu le plus complet qui tient sous TAILLE_VISEE ; on retire d'abord l'historique, puis les vieilles
    scènes, puis les vieilles pièces de la scène courante."""
    essais = [dict(detail_scenes=True, avec_histo=True), dict(detail_scenes=False, avec_histo=True),
              dict(detail_scenes=False, avec_histo=False)]
    for opts in essais:
        t = rendu(donnees, maintenant, **opts)
        if len(t.encode("utf-8")) <= TAILLE_VISEE:
            return t
    while len(donnees["histo"]) > 2:
        donnees["histo"] = donnees["histo"][:-1]
        t = rendu(donnees, maintenant, detail_scenes=False, avec_histo=False)
        if len(t.encode("utf-8")) <= TAILLE_VISEE:
            return t
    while len(donnees["scenes"]) > 1 or len(donnees["scenes"][0].get("pieces", [])) > 1:
        if len(donnees["scenes"]) > 1:
            donnees["scenes"].pop()
        else:
            donnees["scenes"][0]["pieces"].pop()
        t = rendu(donnees, maintenant, detail_scenes=False, avec_histo=False)
        if len(t.encode("utf-8")) <= TAILLE_VISEE:
            return t
    return t


# --- fichiers --------------------------------------------------------------------------------------------

def ecrire_atomique(chemin, texte):
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(texte, encoding="utf-8", newline="\n")
    os.replace(tmp, chemin)


def exclure_vignettes(racine):
    """Les vignettes restent sur le PC : exclues de git dans le clone (pas dans le .gitignore du dépôt)."""
    exclude = racine / ".git" / "info" / "exclude"
    regle = VIGNETTES.as_posix() + "/"
    if exclude.parent.is_dir():
        contenu = exclude.read_text(encoding="utf-8") if exclude.is_file() else ""
        if regle not in contenu.splitlines():
            exclude.write_text(contenu.rstrip("\n") + ("\n" if contenu else "") + regle + "\n", encoding="utf-8")


def faire_vignette(racine, planche, e):
    """Copie réduite de la planche dans le coffre ; renvoie son chemin depuis la racine du coffre, ou ''."""
    try:
        from PIL import Image
    except ImportError:
        return ""
    if not planche or not Path(planche).is_file():
        return ""
    exclure_vignettes(racine)
    dossier = racine / VIGNETTES
    dossier.mkdir(exist_ok=True)
    nom = "%s--%s.jpg" % (slug(e.get("scene", "scene")), slug(e.get("piece", "piece")))
    with Image.open(planche) as img:
        img = img.convert("RGB")
        img.thumbnail((LARGEUR_VIGNETTE, LARGEUR_VIGNETTE))
        tmp = dossier / (nom + ".tmp")
        img.save(tmp, "JPEG", quality=80)
    os.replace(tmp, dossier / nom)
    return (VIGNETTES / nom).as_posix()


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
        maintenant = maintenant or time.localtime()
        f = trouver_piece(depart)
        try:
            e = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
        except ValueError:
            e = {}
        if not isinstance(e, dict):
            e = {}
        planches = [str(p) for p in planches]
        cible = racine / NOTE
        nouvelle = not cible.exists()
        donnees = lire_donnees("" if nouvelle else cible.read_text(encoding="utf-8"))
        try:
            vignette = faire_vignette(racine, planches[0] if planches else "", e)
        except OSError:
            vignette = ""
        quand = time.strftime("%d/%m/%Y %H:%M", maintenant)
        donnees = mettre_a_jour(donnees, e, planches, vignette, quand)
        ecrire_atomique(cible, texte_borne(donnees, maintenant))
        suite = (" ; " + regenerer_index(racine)) if nouvelle else ""
        return "tableau des builds écrit : %s%s" % (cible, suite)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as err:
        return "ERREUR tableau des builds : %s" % re.sub(r"\s+", " ", str(err))[:200]
