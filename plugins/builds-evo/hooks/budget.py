"""Hooks d'économie du plugin builds-evo (0 token : ils ne parlent que pour bloquer ou au début d'une session).

Un seul script, cinq modes (voir hooks.json) :
  pre     PreToolUse   : cahier des charges ET maquette three.js validés avant toute passe du banc ; au plus N vues par passe ;
                         plafond de passes sans point avec Adrien ; une critique par planche ; lire la planche,
                         pas chaque capture ; compteurs et journal de consommation gérés par les hooks seuls.
  post    PostToolUse  : compte une passe du banc réussie.
  prompt  UserPromptSubmit : un message d'Adrien = un point ; le compteur de passes repart à 0.
  stop    Stop / SubagentStop : additionne les jetons du transcript (par modèle) dans conso.json, attribués à la
                         scène et à la pièce de piece.json. Aucune sortie : rien n'entre dans le contexte.
  debut   SessionStart : injecte le relais court (.claude/builds-evo/relais.md) et l'état des compteurs.
CLI : python budget.py rapport [scène]  -> consommation par scène et par pièce (pour /builds-evo:conso et la rétro).

Fichiers, dans `.claude/builds-evo/` cherché depuis le dossier de la session vers le haut (comme la ligne d'état) :
  piece.json      (écrit par les fils) : scene, piece, version, cahier_valide, maquette_validee, plafond_passes (défaut 5, 0 = sans
                  plafond, sur ordre d'Adrien seulement), max_vues (défaut 12)
  compteurs.json  (hooks seuls) : passes_depuis_point, passes_total, critique_passe, finale_passe, point
  conso.json      (hooks seuls) : jetons par scène / pièce / modèle, position lue dans chaque transcript
  relais.md       (écrit par /builds-evo:relais) : passation courte entre deux sessions
Python 3.8+, bibliothèque standard seulement.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun  # noqa: E402

DOSSIER = Path(".claude") / "builds-evo"
GERES = ("compteurs.json", "conso.json")
PLAFOND_DEFAUT, VUES_DEFAUT = 5, 12
OUTIL_PASSE = re.compile(r"(^|__)banc_(passe|tester)$")
IMAGES = (".jpg", ".jpeg", ".png")
RELAIS_MAX = 2500


# ---------- état ----------
def trouver_dossier(depart):
    d = Path(depart or ".").resolve()
    for dossier in [d, *d.parents]:
        if (dossier / DOSSIER).is_dir():
            return dossier / DOSSIER
    return None


def lire(f, defaut=None):
    try:
        return json.loads(Path(f).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {} if defaut is None else defaut


def ecrire(f, obj):
    tmp = Path(str(f) + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(str(tmp), str(f))


def maintenant():
    return time.strftime("%Y-%m-%d %H:%M")


def entier(v, defaut):
    try:
        return int(v)
    except (TypeError, ValueError):
        return defaut


# ---------- pre ----------
def nb_vues(chemin, cwd):
    p = Path(chemin)
    if not p.is_absolute():
        p = Path(cwd or ".") / p
    d = lire(p, defaut=None)
    if isinstance(d, dict):
        d = d.get("vues")
    return len(d) if isinstance(d, list) else None


def verifier_passe(outil_entree, dossier, cwd):
    piece = lire(dossier / "piece.json")
    if not piece:
        return None
    if not piece.get("cahier_valide"):
        return ("Pas de cahier des charges validé pour « %s » : lancer /builds-evo:cahier, faire valider la checklist par "
                "Adrien en un message, puis écrire \"cahier_valide\": \"AAAA-MM-JJ\" dans piece.json. Aucune passe du banc "
                "avant (A2 : les exigences ajoutées en route ont rouvert l'addon 4 fois)." % (piece.get("scene") or "?"))
    if not piece.get("maquette_validee"):
        return ("Pas de maquette three.js validée pour « %s » : étape 7 du skill build-evo (décor + timeline en gris, "
                "humain de 72 u, caméras réelles), montrée à Adrien, puis \"maquette_validee\": \"AAAA-MM-JJ\" dans "
                "piece.json. Aucun GMod avant (Sumii, 27/11 : étape sautée par une passation)." % (piece.get("scene") or "?"))
    vues = outil_entree.get("vues")
    max_vues = entier(piece.get("max_vues"), VUES_DEFAUT)
    if vues:
        n = nb_vues(vues, cwd)
        if n is not None and n > max_vues:
            return ("%d vues dans %s : %d au plus par passe (une planche de 9 à 12 vues ; chaque image lue coûte "
                    "~1 500 jetons). Garder les vues de jugement de la fiche." % (n, vues, max_vues))
    c = lire(dossier / "compteurs.json")
    plafond = entier(piece.get("plafond_passes"), PLAFOND_DEFAUT)
    faites = entier(c.get("passes_depuis_point"), 0)
    if plafond > 0 and faites >= plafond:
        return ("Plafond atteint : %d passes du banc sans point avec Adrien. Faire le point MAINTENANT, en un message : "
                "planche ouverte sur son écran, note, ce qui manque, 2 options numérotées (continuer avec telles "
                "corrections / s'arrêter là / revoir la fiche). Sa réponse remet le compteur à 0." % faites)
    return None


def verifier_critique(sorte, dossier):
    if not (dossier / "piece.json").is_file():
        return None
    c = lire(dossier / "compteurs.json")
    total = entier(c.get("passes_total"), 0)
    cle = "finale_passe" if sorte == "finale" else "critique_passe"
    if total and entier(c.get(cle), -1) == total:
        return ("Une critique par planche : la passe %d a déjà sa critique%s. Corriger puis refaire une passe, ou faire "
                "le point avec Adrien." % (total, " finale" if sorte == "finale" else ""))
    c[cle] = total
    ecrire(dossier / "compteurs.json", c)
    return None


def verifier_lecture(chemin):
    p = Path(chemin or "")
    if p.suffix.lower() not in IMAGES or p.name.lower().startswith("planche"):
        return None
    try:
        planches = [f for f in p.parent.iterdir() if f.name.lower().startswith("planche") and f.suffix.lower() in IMAGES]
    except OSError:
        return None
    if planches:
        return ("Lire la planche (%s) plutôt que chaque capture : une image au lieu de 9 à 12 (~1 500 jetons chacune). "
                "Pour regarder une vue de près à la demande d'Adrien : la copier dans un sous-dossier zoom/ et la lire là."
                % planches[0].name)
    return None


def pre(ev):
    outil, entree = ev.get("tool_name") or "", ev.get("tool_input") or {}
    cwd = ev.get("cwd")
    if outil in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        nom = Path(entree.get("file_path") or entree.get("notebook_path") or "").name
        if nom in GERES and "builds-evo" in str(entree.get("file_path") or "").replace("\\", "/"):
            return commun.decision("PreToolUse", "deny", "%s est tenu par les hooks du plugin, pas à la main." % nom)
        return None
    dossier = trouver_dossier(cwd)
    if dossier is None:
        return None
    if outil == "Read":
        # seulement pendant un build (piece.json) : hors build (Atelier, séance MJ), lire une capture reste libre
        if not (dossier / "piece.json").is_file():
            return None
        raison = verifier_lecture(entree.get("file_path"))
        return commun.decision("PreToolUse", "deny", raison) if raison else None
    if OUTIL_PASSE.search(outil):
        raison = verifier_passe(entree, dossier, cwd)
        return commun.decision("PreToolUse", "deny", raison) if raison else None
    if outil in ("Agent", "Task"):
        sorte = str(entree.get("subagent_type") or "")
        if sorte.endswith("critique-build") or sorte.endswith("critique-finale"):
            raison = verifier_critique("finale" if sorte.endswith("finale") else "build", dossier)
            return commun.decision("PreToolUse", "deny", raison) if raison else None
    return None


# ---------- post / prompt ----------
def reponse_ok(rep):
    if isinstance(rep, dict):
        if rep.get("isError"):
            return False
        rep = json.dumps(rep, ensure_ascii=False)
    if isinstance(rep, list):
        rep = json.dumps(rep, ensure_ascii=False)
    texte = str(rep or "")
    return "ERREUR" not in texte[:400]


def post(ev):
    if not OUTIL_PASSE.search(ev.get("tool_name") or ""):
        return
    dossier = trouver_dossier(ev.get("cwd"))
    if dossier is None or not (dossier / "piece.json").is_file() or not reponse_ok(ev.get("tool_response")):
        return
    c = lire(dossier / "compteurs.json")
    c["passes_depuis_point"] = entier(c.get("passes_depuis_point"), 0) + 1
    c["passes_total"] = entier(c.get("passes_total"), 0) + 1
    c["derniere_passe"] = maintenant()
    ecrire(dossier / "compteurs.json", c)


def prompt(ev):
    dossier = trouver_dossier(ev.get("cwd"))
    if dossier is None or not (dossier / "compteurs.json").is_file():
        return
    c = lire(dossier / "compteurs.json")
    if entier(c.get("passes_depuis_point"), 0):
        c["passes_depuis_point"] = 0
        c["point"] = maintenant()
        ecrire(dossier / "compteurs.json", c)


# ---------- stop : consommation ----------
def famille(modele):
    m = (modele or "").lower()
    for f in ("opus", "sonnet", "haiku", "fable"):
        if f in m:
            return f
    return m or "inconnu"


def lire_usage(chemin, depuis, deja):
    """Lit le transcript à partir de l'octet `depuis` ; renvoie (fin, {famille: [entree, ecr_cache, lu_cache, sortie]}, ids)."""
    totaux, ids = {}, []
    try:
        with open(chemin, "rb") as f:
            f.seek(depuis)
            for brut in f:
                if not brut.endswith(b"\n"):
                    break          # ligne en cours d'écriture : on la relira au prochain passage
                depuis += len(brut)
                if b'"usage"' not in brut:
                    continue        # la plupart des lignes : pas de jetons, pas de lecture JSON
                try:
                    ligne = json.loads(brut.decode("utf-8", "replace"))
                except ValueError:
                    continue
                msg = ligne.get("message") if isinstance(ligne, dict) else None
                if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
                    continue
                ident = msg.get("id") or ligne.get("uuid")
                if ident and (ident in deja or ident in ids):
                    continue        # un message de l'assistant est écrit en plusieurs lignes avec le même usage
                if ident:
                    ids.append(ident)
                u = msg["usage"]
                t = totaux.setdefault(famille(msg.get("model")), [0, 0, 0, 0])
                for i, cle in enumerate(("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")):
                    t[i] += entier(u.get(cle), 0)
    except OSError:
        return depuis, {}, []
    return depuis, totaux, ids


def stop(ev):
    dossier = trouver_dossier(ev.get("cwd"))
    if dossier is None:
        return
    chemins = [p for p in (ev.get("agent_transcript_path"), ev.get("transcript_path")) if p]
    if not chemins:
        return
    piece = lire(dossier / "piece.json")
    scene, nom_piece = piece.get("scene") or "hors build", piece.get("piece") or "(scène)"
    conso = lire(dossier / "conso.json")
    lus = conso.setdefault("lus", {})
    change = False
    for chemin in chemins:
        cle = str(Path(chemin))
        etat = lus.get(cle) or {"octet": 0, "ids": []}
        fin, totaux, ids = lire_usage(chemin, entier(etat.get("octet"), 0), set(etat.get("ids") or []))
        if fin == etat.get("octet"):
            continue
        lus[cle] = {"octet": fin, "ids": ((etat.get("ids") or []) + ids)[-200:], "maj": maintenant()}
        change = True
        p = conso.setdefault("scenes", {}).setdefault(scene, {}).setdefault(nom_piece, {})
        for fam, t in totaux.items():
            cumul = p.setdefault(fam, [0, 0, 0, 0])
            for i in range(4):
                cumul[i] += t[i]
    if change:
        if len(lus) > 300:   # garder les transcripts récents seulement
            for k in sorted(lus, key=lambda k: lus[k].get("maj", ""))[:len(lus) - 300]:
                del lus[k]
        ecrire(dossier / "conso.json", conso)


# Indice relatif (pas la limite Max, qui n'est pas publiée) : prix API relatifs, pour comparer deux builds.
POIDS_FAMILLE = {"opus": 5.0, "fable": 5.0, "sonnet": 3.0, "haiku": 1.0}
POIDS_TYPE = (1.0, 1.25, 0.1, 5.0)


def indice(fam, t):
    return POIDS_FAMILLE.get(fam, 5.0) * sum(p * v for p, v in zip(POIDS_TYPE, t)) / 1e6


def millions(n):
    return ("%.2f" % (n / 1e6)).replace(".", ",") + " M"


def rapport(dossier, scene=None):
    conso = lire(dossier / "conso.json")
    scenes = conso.get("scenes") or {}
    if scene:
        scenes = {k: v for k, v in scenes.items() if k.lower() == scene.lower()}
    if not scenes:
        return "Aucune consommation notée%s." % (" pour " + scene if scene else "")
    lignes = []
    for s, pieces in scenes.items():
        tot_s = 0.0
        lignes.append("## %s" % s)
        for p, fams in pieces.items():
            parts, tot_p = [], 0.0
            for fam, t in sorted(fams.items()):
                tot_p += indice(fam, t)
                parts.append("%s %s lus en cache, %s écrits, %s en entrée, %s en sortie"
                             % (fam, millions(t[2]), millions(t[1]), millions(t[0]), millions(t[3])))
            tot_s += tot_p
            lignes.append("- %s : indice %.1f ; %s" % (p, tot_p, " | ".join(parts)))
        lignes.append("- total %s : indice %.1f" % (s, tot_s))
    lignes.append("Indice = jetons pondérés par les prix API relatifs (Opus 5, Sonnet 3, Haiku 1 ; cache lu 0,1, écrit 1,25, "
                  "sortie 5) : sert à comparer deux builds, ce n'est pas un pourcentage du forfait Max.")
    return "\n".join(lignes)


def total_scene(dossier, scene):
    pieces = (lire(dossier / "conso.json").get("scenes") or {}).get(scene) or {}
    return sum(indice(f, t) for fams in pieces.values() for f, t in fams.items())


# ---------- debut ----------
def debut(ev):
    dossier = trouver_dossier(ev.get("cwd"))
    if dossier is None:
        return
    morceaux = []
    relais = dossier / "relais.md"
    if relais.is_file():
        texte = relais.read_text(encoding="utf-8", errors="replace").strip()
        if len(texte) > RELAIS_MAX:
            texte = texte[:RELAIS_MAX] + "\n[relais coupé à %d caractères : le raccourcir]" % RELAIS_MAX
        morceaux.append("Relais de la session précédente (%s) :\n%s" % (relais, texte))
    piece = lire(dossier / "piece.json")
    if piece:
        c = lire(dossier / "compteurs.json")
        plafond = entier(piece.get("plafond_passes"), PLAFOND_DEFAUT)
        etat = "Build en cours : %s › %s v%s ; passes depuis le dernier point %s/%s ; cahier %s ; maquette %s." % (
            piece.get("scene"), piece.get("piece"), piece.get("version"), entier(c.get("passes_depuis_point"), 0),
            plafond if plafond > 0 else "sans plafond", "validé le %s" % piece["cahier_valide"] if piece.get("cahier_valide")
            else "NON validé (/builds-evo:cahier avant toute passe)",
            "validée le %s" % piece["maquette_validee"] if piece.get("maquette_validee")
            else "NON validée (three.js, étape 7, avant tout GMod)")
        morceaux.append(etat + " Règles d'économie : skill build-evo, `references/economie.md`.")
    if morceaux:
        commun.contexte("SessionStart", "\n\n".join(morceaux))


MODES = {"pre": pre, "post": post, "prompt": prompt, "stop": stop, "debut": debut}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "rapport":
        dossier = trouver_dossier(os.getcwd())
        texte = rapport(dossier, sys.argv[2] if len(sys.argv) > 2 else None) if dossier else \
            "Pas de dossier .claude/builds-evo ici ni au-dessus."
        sys.stdout.buffer.write((texte + "\n").encode("utf-8"))
        return
    if mode not in MODES or commun.desactive("budget"):
        return
    try:
        MODES[mode](commun.lire_evenement())
    except Exception as e:  # un hook d'économie ne doit jamais casser une session
        sys.stderr.write("budget.py %s : %s\n" % (mode, e))


if __name__ == "__main__":
    main()
