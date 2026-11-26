"""Hook PreToolUse : règles du banc GMod (commandes shell).

Bloque :
  - --focus sur banc.py / atelier.py (GMod ne vole jamais le focus) ;
  - tout lancement de GMod par le banc ou l'Atelier sans --eclair
    (jamais GMod avec les addons d'Adrien) ;
  - tout lancement direct de GMod (gmod.exe, hl2.exe, steam -applaunch 4000,
    steam://rungameid/4000) : passer par le banc.
Demande l'accord d'Adrien :
  - avant d'ouvrir un nouveau GMod (--lancer) ;
  - avant de fermer GMod (taskkill, Stop-Process...).
"""
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun  # noqa: E402

SEPARATEURS = re.compile(r"\|\||&&|[;|\n]")
LANCEURS = {"start", "start-process", "saps", "invoke-item", "ii", "explorer", "explorer.exe",
            "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe", "&", "call", "nohup"}
TUEURS = {"taskkill", "taskkill.exe", "stop-process", "spps", "kill", "pkill", "killall", "tskill"}
EXE_GMOD = re.compile(r"(^|[\\/\"'\s])(gmod|hl2)(\.exe)?(?=$|[\"'\s])", re.I)
STEAM_4000 = re.compile(r"(-applaunch\s+4000\b|steam://(run|rungameid)/4000\b)", re.I)
BANC = re.compile(r"\bbanc\.py\b", re.I)
ATELIER_JEU = re.compile(r"\batelier(\.py)?\b[^\n]*?\bjeu\b", re.I)


def mots(segment):
    try:
        return shlex.split(segment, posix=False)
    except ValueError:
        return segment.split()


def base(mot):
    return re.split(r"[\\/]", mot.strip("\"'"))[-1].lower()


def analyser(commande):
    """Renvoie (choix, raison) ou None. choix = 'deny' ou 'ask'."""
    demander = None
    for segment in SEPARATEURS.split(commande or ""):
        seg = segment.strip()
        if not seg:
            continue
        m = mots(seg)
        if not m:
            continue
        premier = base(m[0])
        banc = bool(BANC.search(seg)) and premier.startswith(("python", "py"))
        atelier = bool(ATELIER_JEU.search(seg)) and (premier.startswith(("python", "py")) or premier.startswith("atelier"))
        if banc or atelier:
            options = {x.lower() for x in m}
            if "--focus" in options:
                return ("deny", "Banc : --focus est interdit, GMod ne doit jamais voler le focus. "
                                "Un seul passage au premier plan de 3 à 5 s par série, avec l'accord d'Adrien (skill banc-gmod).")
            lance = "--lancer" in options or "--cote" in options or (banc and "poser" in options) \
                or (banc and "filmer" in options and "--lancer" in options)
            if lance and "--eclair" not in options:
                return ("deny", "Banc : ajouter --eclair. GMod ne doit jamais tourner avec les addons d'Adrien "
                                "(mode éclair = -noworkshop, contenu copié par l'Atelier).")
            if "--lancer" in options:
                demander = ("ask", "Cette commande ouvre un nouveau GMod (mode éclair). Règle : jamais lancer GMod sans l'accord d'Adrien.")
            continue
        lancement_direct = (EXE_GMOD.search(m[0]) is not None) or \
            (premier in LANCEURS and (EXE_GMOD.search(seg) or STEAM_4000.search(seg))) or \
            (premier.startswith("steam") and STEAM_4000.search(seg)) or \
            (premier in LANCEURS and re.search(r"steam://(run|rungameid)/4000", seg, re.I))
        if lancement_direct:
            return ("deny", "GMod ne se lance jamais à la main (risque : addons d'Adrien chargés, focus volé). "
                            "Passer par le banc : python atelier.py jeu <build> --cote --eclair, ou banc.py ... --lancer --eclair, "
                            "après accord d'Adrien.")
        if premier in TUEURS and re.search(r"\b(gmod|hl2)\b", seg, re.I):
            demander = ("ask", "Fermer GMod : règle du banc, ne jamais fermer le GMod du banc en pleine pièce sans l'accord d'Adrien.")
    return demander


def main():
    if commun.desactive("garde_banc"):
        return
    ev = commun.lire_evenement()
    commande = (ev.get("tool_input") or {}).get("command", "")
    res = analyser(commande)
    if res:
        commun.decision("PreToolUse", res[0], res[1])


if __name__ == "__main__":
    main()
