"""Hook Stop du plugin optimus : rappelle la passation une fois par fil.

Adrien ne retient pas les commandes (27/11/2026). Quand un fil a livré quelque
chose (commit ou PR) et n'a pas encore fait la passation du coffre OPTIMUS, la
fin du tour est bloquée une seule fois avec la consigne de lancer
/optimus:passation. 0 jeton tant que rien n'est livré.

Entrée : l'événement JSON de Claude Code (session_id, transcript_path,
stop_hook_active). Sortie : rien, ou {"decision": "block", "reason": ...}.
Python 3.8+, bibliothèque standard seulement.
"""
import json
import os
import sys
import tempfile

LIVRE = ("git commit", "gh pr create")
FAITE = ("optimus.py passation", "optimus:passation")
MAX_LIGNES = 20000                     # transcript borné : on lit au plus les dernières lignes
RAISON = ("Ce fil a livré du travail (commit ou PR) sans passation OPTIMUS. "
          "Lance maintenant /optimus:passation <note> sur la note du chantier concerné "
          "(devine-la d'après le dossier et le travail du fil ; coffre : OPTIMUS_DIR, sinon C:\\Project\\OPTIMUS). "
          "Si aucune note du coffre ne correspond à ce travail, dis-le en une ligne et termine.")


def lire_evenement():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except ValueError:
        return {}


def textes_outils(ligne):
    """Textes des appels d'outils d'une ligne du transcript (commandes, skill)."""
    try:
        obj = json.loads(ligne)
    except ValueError:
        return []
    msg = obj.get("message") if isinstance(obj, dict) else None
    contenu = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(contenu, list):
        return []
    sortie = []
    for bloc in contenu:
        if isinstance(bloc, dict) and bloc.get("type") == "tool_use":
            entree = bloc.get("input") or {}
            sortie.append(" ".join(str(entree.get(k, "")) for k in ("command", "skill", "args")))
    return sortie


def etat_du_fil(chemin):
    """(a livré, passation faite) d'après le transcript."""
    livre = faite = False
    try:
        with open(chemin, encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()[-MAX_LIGNES:]
    except OSError:
        return False, False
    for ligne in lignes:
        if "tool_use" not in ligne:
            continue
        for t in textes_outils(ligne):
            livre = livre or any(m in t for m in LIVRE)
            faite = faite or any(m in t for m in FAITE)
    return livre, faite


def marque(session):
    nom = "".join(c for c in str(session) if c.isalnum() or c in "-_")[:80] or "inconnue"
    return os.path.join(tempfile.gettempdir(), "optimus_rappel_" + nom)


def main():
    ev = lire_evenement()
    if ev.get("stop_hook_active"):
        return                           # déjà relancé par un hook : pas de boucle
    m = marque(ev.get("session_id"))
    if os.path.exists(m):
        return                           # rappel déjà fait dans ce fil
    livre, faite = etat_du_fil(ev.get("transcript_path") or "")
    if not livre or faite:
        return
    try:
        open(m, "w").close()
    except OSError:
        return                           # sans marque, on ne bloque pas (sinon rappel à chaque tour)
    sys.stdout.write(json.dumps({"decision": "block", "reason": RAISON}, ensure_ascii=True))


if __name__ == "__main__":
    main()
