"""Contrôle de livraison d'un addon de scène (0 token, avant la PR creations-evo et avant la critique finale).

Usage :  python controle_livraison.py <dossier de la création ou de l'addon> [--sans-gravure]
Vérifie les exigences d'Adrien qui, ajoutées en route sur l'A2, ont rouvert l'addon plusieurs fois :
  ERREUR    : pas de commande <nom>_tout_effacer ; notification à l'écran (chat.AddText, notification.*,
              ChatPrint, PrintMessage en HUD_PRINTTALK / HUD_PRINTCENTER) ; touche en dur, coordonnée de map
              ou musique (mêmes règles que le hook garde_lua) ; COMMANDES.md absent ou commande absente de
              COMMANDES.md ; gravure d'usine absente (sauf --sans-gravure).
  ATTENTION : commande absente du README ; pas de commande diag ; pas de bind suggéré dans le README.
Sortie : au plus 14 lignes, code 1 s'il y a une erreur.
"""
import argparse
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "hooks"))
import garde_lua  # noqa: E402

COMMANDE = re.compile(r"concommand\.Add\s*\(\s*[\"']([\w.\-]+)[\"']")
ECRAN = re.compile(r"chat\.AddText|notification\.Add\w*|:ChatPrint\s*\(|PrintMessage\s*\(\s*HUD_PRINT(TALK|CENTER)"
                   r"|\bPrintMessage\s*\(\s*[34]\s*,")


def trouver(dossier, nom):
    """Premier fichier `nom` dans le dossier ou ses parents proches (README de la création au-dessus de l'addon)."""
    for d in [dossier, *list(dossier.parents)[:2]]:
        for f in d.glob(nom):
            return f
    return None


def controler(dossier, gravure=True):
    dossier = Path(dossier)
    luas = sorted(dossier.rglob("*.lua"))
    erreurs, attentions = [], []
    if not luas:
        return ["aucun fichier .lua dans %s" % dossier], [], "0 script"
    commandes, ecran, regles, grave = [], [], [], False
    for f in luas:
        code = f.read_text(encoding="utf-8", errors="replace")
        propre = garde_lua.sans_commentaires(code)
        commandes += COMMANDE.findall(propre)
        for m in ECRAN.finditer(propre):
            ecran.append("%s:%d %s" % (f.name, propre[:m.start()].count("\n") + 1, m.group(0)))
        regles += ["%s : %s" % (f.name, p.split(".")[0]) for p in garde_lua.problemes(code)]
        grave = grave or "sh_gravure" in propre or "gravure" in f.name.lower()
    commandes = sorted(set(commandes))
    if not any(c.endswith("_tout_effacer") for c in commandes):
        erreurs.append("pas de commande <nom>_tout_effacer (effacement total à double confirmation 10 s)")
    if ecran:
        erreurs.append("notification à l'écran (console seulement) : %s" % ", ".join(ecran[:3]))
    erreurs += regles[:3]
    if gravure and not grave:
        erreurs.append("gravure d'usine absente (outils/gravure_lua/sh_gravure.lua) ; --sans-gravure si Adrien l'a dispensée")
    cmd_md = trouver(dossier, "COMMANDES.md")
    if cmd_md is None:
        erreurs.append("COMMANDES.md absent (tableau nom | arguments | qui | ce qu'elle fait | exemple)")
    else:
        texte = cmd_md.read_text(encoding="utf-8", errors="replace")
        manquantes = [c for c in commandes if c not in texte]
        if manquantes:
            erreurs.append("%d commande(s) absente(s) de COMMANDES.md : %s" % (len(manquantes), ", ".join(manquantes[:4])))
    readme = trouver(dossier, "README.md")
    if readme is None:
        attentions.append("README.md absent")
    else:
        texte = readme.read_text(encoding="utf-8", errors="replace")
        manquantes = [c for c in commandes if c not in texte]
        if manquantes:
            attentions.append("%d commande(s) absente(s) du README : %s" % (len(manquantes), ", ".join(manquantes[:4])))
        if "bind" not in texte:
            attentions.append("aucun bind suggéré dans le README (touches au choix d'Adrien)")
    if not any(c.endswith("_diag") or c.endswith("diag") for c in commandes):
        attentions.append("pas de commande diag (le joueur vérifie ce qui est actif)")
    return erreurs, attentions, "%d script(s), %d commande(s)" % (len(luas), len(commandes))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dossier")
    ap.add_argument("--sans-gravure", action="store_true")
    a = ap.parse_args(argv)
    erreurs, attentions, resume = controler(a.dossier, gravure=not a.sans_gravure)
    lignes = ["contrôle livraison : %s, %s" % (resume, "%d erreur(s)" % len(erreurs) if erreurs else "aucune erreur")]
    lignes += ["ERREUR : " + e for e in erreurs] + ["ATTENTION : " + x for x in attentions]
    sys.stdout.buffer.write(("\n".join(lignes[:14]) + "\n").encode("utf-8"))
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
