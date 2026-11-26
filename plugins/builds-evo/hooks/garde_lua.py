"""Hooks des scripts Lua de scène (Write / Edit / MultiEdit sur un fichier .lua).

Mode « pre » (PreToolUse), bloque :
  - les touches en dur (KEY_*, input.IsKeyDown..., PlayerButtonDown, PlayerBindPress) :
    des commandes + un bind au choix d'Adrien dans le README ;
  - les coordonnées de la zone de build du serveur écrites en dur :
    la boîte de scène est relative au prop repère du dupe ;
  - la musique (sound.PlayURL, chemins music/, ost, soundtrack, bgm, musique) :
    jamais de musique dans un script, les MJ la gèrent.
Mode « post » (PostToolUse), signale sans bloquer :
  - un Vector littéral très loin de l'origine (|x| ou |y| >= 8000) :
    vérifier qu'il est bien relatif au repère ;
  - avec LuaJIT (dans le PATH ou variable LUAJIT) sur le fichier écrit : erreur de syntaxe, et nom déclaré
    `local` dans le fichier mais lu comme globale (GGET) quelque part : fonction locale appelée avant sa
    déclaration, globale nil à l'exécution (construireRides, 26/11/2026).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun  # noqa: E402

# Zone de build EVO relevée le 19/11/2026 (marge de 600 u).
ZONE = ((-15287 - 600, -7193 + 600), (-15584 - 600, -7291 + 600), (14109 - 600, 16054 + 600))

TOUCHES = [
    (re.compile(r"\bKEY_[A-Z0-9_]+\b"), "constante de touche KEY_*"),
    (re.compile(r"\binput\.(IsKeyDown|IsButtonDown|WasKeyPressed|WasKeyReleased|WasKeyTyped|WasMousePressed|IsMouseDown)\b"), "lecture directe du clavier (input.*)"),
    (re.compile(r"[\"'](PlayerButtonDown|PlayerButtonUp|PlayerBindPress|KeyPress|KeyRelease)[\"']"), "hook de touche"),
]
MUSIQUE = [
    (re.compile(r"\bsound\.PlayURL\b"), "sound.PlayURL (flux audio)"),
    (re.compile(r"[\"'](?:[^\"'\n]*[/\\_\-.])?(music|musique|musics|ost|soundtrack|bgm)(?=[/\\_\-.\d\"'])", re.I), "chemin de musique"),
]
NOMBRE = r"\s*(-?\d+(?:\.\d+)?)\s*"
VECTEUR = re.compile(r"\bVector\s*\(" + NOMBRE + "," + NOMBRE + "," + NOMBRE + r"\)")


def texte_nouveau(entree):
    morceaux = []
    if "content" in entree:
        morceaux.append(entree.get("content") or "")
    if "new_string" in entree:
        morceaux.append(entree.get("new_string") or "")
    for e in entree.get("edits") or []:
        morceaux.append((e or {}).get("new_string") or "")
    return "\n".join(morceaux)


def sans_commentaires(code):
    code = re.sub(r"--\[(=*)\[.*?\]\1\]", "", code, flags=re.S)
    return "\n".join(re.sub(r"--.*$", "", l) for l in code.splitlines())


def dans_zone(x, y, z):
    (x0, x1), (y0, y1), (z0, z1) = ZONE
    return x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1


def problemes(code):
    code = sans_commentaires(code)
    trouve = []
    for motif, nom in TOUCHES:
        m = motif.search(code)
        if m:
            trouve.append("Touche en dur (%s : %s). Règle : jamais de touche en dur ; des concommand et un bind au choix dans le README." % (nom, m.group(0)))
            break
    for m in VECTEUR.finditer(code):
        x, y, z = (float(v) for v in m.groups())
        if dans_zone(x, y, z):
            trouve.append("Coordonnée de la zone de build du serveur en dur (%s). Règle : la boîte de scène est relative au prop repère du dupe, aucune coordonnée de map." % m.group(0))
            break
    for motif, nom in MUSIQUE:
        m = motif.search(code)
        if m:
            trouve.append("Musique dans le script (%s : %s). Règle : jamais de musique ni d'OST, seulement des sons ; les MJ gèrent la musique en jeu." % (nom, m.group(0).strip()[:60]))
            break
    return trouve


def avertissements(code):
    code = sans_commentaires(code)
    for m in VECTEUR.finditer(code):
        x, y, _ = (float(v) for v in m.groups())
        if abs(x) >= 8000 or abs(y) >= 8000:
            return ("Vérifier %s : un Vector littéral aussi loin ressemble à une coordonnée de map. "
                    "S'il s'agit d'un décalage depuis le repère (lointains, ciel 3D), c'est bon ; sinon le calculer depuis le prop repère." % m.group(0))
    return None


LOCALE = re.compile(r"\blocal\s+(?:function\s+)?([A-Za-z_][\w ,\t]*)")
GGET = re.compile(r"\bGGET\b.*;\s*\"([A-Za-z_]\w*)\"")


def noms_locaux(code):
    noms = set()
    for m in LOCALE.finditer(sans_commentaires(code)):
        for n in m.group(1).split(","):
            n = n.strip().split()[0] if n.strip() else ""
            if n and n != "function":
                noms.add(n)
    return noms


def controle_luajit(chemin):
    """Texte d'alerte, ou None (rien à signaler, ou pas de LuaJIT)."""
    exe = os.environ.get("LUAJIT") or shutil.which("luajit")
    if not exe or not os.path.isfile(chemin):
        return None
    try:
        r = subprocess.run([exe, "-bl", chemin], capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    sortie = r.stdout.decode("utf-8", "replace")
    if r.returncode != 0:
        return "LuaJIT refuse " + Path(chemin).name + " : " + r.stderr.decode("utf-8", "replace").strip()[:300]
    code = Path(chemin).read_text(encoding="utf-8", errors="replace")
    lus = set(GGET.findall(sortie)) & noms_locaux(code)
    if lus:
        return ("Nom local lu comme globale dans " + Path(chemin).name + " : " + ", ".join(sorted(lus)) +
                ". Une fonction locale appelée avant sa déclaration vaut nil à l'exécution : la déclarer avant "
                "(`local nom` en tête, puis `nom = function() ... end`).")
    return None


def main():
    if commun.desactive("garde_lua"):
        return
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre"
    ev = commun.lire_evenement()
    entree = ev.get("tool_input") or {}
    chemin = str(entree.get("file_path") or "")
    if not chemin.lower().endswith(".lua"):
        return
    code = texte_nouveau(entree)
    if mode == "pre":
        liste = problemes(code)
        if liste:
            commun.decision("PreToolUse", "deny", "Script de scène refusé (" + Path(chemin).name + ") :\n- " + "\n- ".join(liste))
    else:
        textes = [t for t in (avertissements(code), controle_luajit(chemin)) if t]
        if textes:
            commun.contexte("PostToolUse", "\n".join(textes))


if __name__ == "__main__":
    main()
