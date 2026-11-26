"""Serveur MCP « banc » du plugin builds-evo (stdio, Python seul, Windows).

Il enveloppe le banc existant (sites/gmod-build/banc/banc.py) sans le modifier
et porte lui-même les règles du banc :
  - jamais --focus (GMod ne vole jamais le focus) ;
  - tout lancement en mode éclair (--eclair, sans les addons d'Adrien),
    et seulement avec accord_adrien=true ; le GMod lancé reste ouvert (--garder)
    pour qu'il n'y en ait qu'un par série ;
  - collage loin du bâtiment central de gm_flatgrass par défaut (y = -8000) ;
  - réponses courtes (quelques lignes) pour garder le coût en tokens bas.

Chemin du banc : variable BANC_PY, sinon C:\\Project\\Adler_lore\\sites\\gmod-build\\banc\\banc.py.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import etat_optimus  # même dossier que ce script : note d'état du coffre OPTIMUS

BANC_PY = Path(os.environ.get("BANC_PY", r"C:\Project\Adler_lore\sites\gmod-build\banc\banc.py"))
# seuls les scripts de ce dossier (et dessous) peuvent être installés dans l'autorun du banc
SOURCES = Path(os.environ.get("BANC_SOURCES", r"C:\Project\Adler_lore"))
IMAGES = (".jpg", ".jpeg", ".png")

V2 = {"type": "number"}
OUTILS = [
    ("banc_etat", "État du banc : GMod ouvert ou non, partie solo du banc (carte, mode), dernière tâche. Ne lance rien.", {}),
    ("banc_tester",
     "Colle un dupe dans le GMod du banc et prend les vues (jamais de focus volé). Renvoie le résumé (entités créées, manquantes, "
     "dégelées, passages, erreurs) et le dossier des captures. Si GMod est fermé : lancer=true ET accord_adrien=true "
     "(Adrien a dit oui dans le fil) ; le lancement est toujours en mode éclair et GMod reste ouvert pour la suite de la série.",
     {"dupe": {"type": "string", "description": "chemin du dupe AdvDupe2 (.txt)"},
      "vues": {"type": "string", "description": "chemin du JSON des vues (facultatif)"},
      "x": V2, "y": {"type": "number", "description": "défaut -8000 : loin du bâtiment central de gm_flatgrass"},
      "type": {"type": "string", "description": "étiquette du dossier de captures (parcours, passe2...)"},
      "lancer": {"type": "boolean"}, "accord_adrien": {"type": "boolean"},
      "attente": {"type": "integer", "description": "secondes max (défaut 600)"}}),
    ("banc_nettoyer", "Nettoie la map du GMod du banc (game.CleanUpMap par une tâche vide). À faire après chaque série de tests.", {}),
    ("banc_planche",
     "Assemble les captures d'un dossier en une planche (3 x 3 par image). Avec avant=<dossier> : planche avant/après, "
     "chaque vue de l'ancienne passe à gauche de la même vue de la nouvelle. Renvoie le chemin des planches.",
     {"dossier": {"type": "string"}, "avant": {"type": "string"}}),
    ("banc_montrer",
     "Ouvre des images ou un dossier sur l'écran d'Adrien (visionneuse + explorateur). Règle : les planches s'ouvrent sur son écran, "
     "donner un chemin ne suffit pas.",
     {"chemins": {"type": "array", "items": {"type": "string"}}}),
    ("banc_passe",
     "Une passe entière en un appel : générer (facultatif) -> contrôler et installer les scripts client -> attendre "
     "le rechargement à chaud -> coller + vues -> lire la console (planche refusée s'il y a une erreur Lua) -> planche "
     "(avant/après si avant=) -> ouvrir sur l'écran d'Adrien -> nettoyer la map. Avant le collage, contrôle auto du dupe "
     "(400 posés ou budget, classes bloquées, playermodels, doublons, boîte) : passe refusée sur erreur, sans rien coller. GMod doit déjà tourner. Un script "
     "nouveau (jamais chargé) est refusé : il faut une bascule de map. Renvoie la planche et le temps de chaque étape.",
     {"generateur": {"type": "string", "description": "script Python du générateur (ex. dunes.py), lancé dans le dossier des params"},
      "params": {"type": "string", "description": "JSON de paramètres passé au générateur"},
      "scripts": {"type": "array", "description": "[{source, nom}] : fichier .lua -> addons/banc_essai/lua/autorun/client/<nom>",
                  "items": {"type": "object", "properties": {"source": {"type": "string"}, "nom": {"type": "string"}}}},
      "dupe": {"type": "string"}, "vues": {"type": "string"}, "x": V2, "y": V2, "type": {"type": "string"},
      "avant": {"type": "string", "description": "dossier de captures de la passe précédente (planche avant/après)"},
      "attente_rechargement": {"type": "integer", "description": "secondes après copie des scripts (défaut 25)"},
      "montrer": {"type": "boolean", "description": "défaut true"}, "nettoyer": {"type": "boolean", "description": "défaut true"},
      "controle": {"type": "boolean", "description": "défaut true : contrôle auto du dupe avant collage (outils/controle_auto.py)"}}),
]


def charger_banc():
    if not BANC_PY.is_file():
        raise RuntimeError("banc introuvable : %s (variable BANC_PY)" % BANC_PY)
    spec = importlib.util.spec_from_file_location("banc", str(BANC_PY))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gmod_ouvert():
    if os.name != "nt":
        return False
    sortie = subprocess.run(["tasklist", "/FI", "IMAGENAME eq gmod.exe", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True).stdout
    return "gmod.exe" in sortie.lower()


def commande_tester(a):
    """Construit la commande banc.py tester ; lève ValueError si une règle l'interdit."""
    dupe = a.get("dupe")
    if not dupe:
        raise ValueError("dupe manquant")
    cmd = [sys.executable, str(BANC_PY), "tester", str(dupe)]
    if a.get("vues"):
        cmd += ["--vues", str(a["vues"])]
    cmd += ["--x", str(float(a.get("x", 0))), "--y", str(float(a.get("y", -8000)))]
    if a.get("type"):
        cmd += ["--type", str(a["type"])]
    cmd += ["--attente", str(int(a.get("attente", 600)))]
    if a.get("lancer"):
        if not a.get("accord_adrien"):
            raise ValueError("GMod n'est lancé qu'avec l'accord d'Adrien : demande-le dans le fil, puis lancer=true et accord_adrien=true.")
        cmd += ["--lancer", "--eclair", "--garder"]
    return cmd


def resume(texte, n=18):
    lignes = [l for l in texte.splitlines() if l.strip()]
    return "\n".join(lignes[-n:])


def tester(a, verifier=True):
    cmd = commande_tester(a)
    if verifier and not a.get("lancer") and os.name == "nt" and not gmod_ouvert():
        return "ERREUR : GMod est fermé. Demande l'accord d'Adrien pour le lancer (lancer=true, accord_adrien=true)."
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=int(a.get("attente", 600)) + 180, cwd=str(BANC_PY.parent))
    texte = resume((r.stdout or "") + "\n" + (r.stderr or ""))
    return ("ERREUR : " if r.returncode else "") + texte


def etat(_):
    lignes = ["GMod ouvert : %s" % ("oui" if gmod_ouvert() else "non")]
    try:
        banc = charger_banc()
        p = banc.partie()
        lignes.append("partie du banc : %s" % (json.dumps(p, ensure_ascii=False) if p else "aucune (GMod fermé, en pause ou hors banc)"))
        fait = banc.DATA / "banc_essai" / "fait.txt"
        if fait.is_file():
            lignes.append("dernière tâche : " + fait.read_text(encoding="utf-8", errors="replace")[:300])
    except Exception as e:  # le banc absent ne doit pas casser l'état
        lignes.append("banc : %s" % e)
    return "\n".join(lignes)


def nettoyer(_):
    banc = charger_banc()
    if not banc.gmod_tourne():
        return "GMod est fermé : rien à nettoyer."
    p = banc.partie()
    if not p or not p.get("solo"):
        return "ERREUR : le GMod ouvert n'est pas une partie solo du banc ; je n'y touche pas."
    tache_id = banc.ecrire_tache(Path("__nettoyage__.txt"), [], 0, 0)
    etat_fait = banc.attendre_fait(banc.DATA / "banc_essai" / "fait.txt", tache_id, 60)
    if etat_fait is None:
        return "ERREUR : le banc n'a pas répondu en 60 s (jeu en pause ? console ouverte ?)."
    return "Map nettoyée (game.CleanUpMap ; la tâche vide se termine par : %s)." % etat_fait.get("raison", "ok")


def _images(dossier):
    return sorted(f for f in Path(dossier).iterdir() if f.suffix.lower() in IMAGES and not f.name.startswith("planche"))


def planche(a):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return "ERREUR : Pillow manque (pip install pillow)."
    dossier = Path(a["dossier"])
    nouvelles = _images(dossier)
    if not nouvelles:
        return "ERREUR : aucune image dans %s" % dossier
    avant = a.get("avant")
    if avant:
        anciennes = {f.stem: f for f in _images(avant)}
        cases = [c for f in nouvelles for c in (anciennes.get(f.stem), f)]
        colonnes, par_page, modele = 2, 12, "planche_avant_apres_%d.jpg"
    else:
        cases, colonnes, par_page, modele = list(nouvelles), 3, 9, "planche_%d.jpg"
    l, h = 640, 360
    sorties = []
    for k in range(0, len(cases), par_page):
        lot = cases[k:k + par_page]
        rangs = (len(lot) + colonnes - 1) // colonnes
        img = Image.new("RGB", (l * colonnes, h * rangs), "black")
        dessin = ImageDraw.Draw(img)
        for i, f in enumerate(lot):
            x, y = (i % colonnes) * l, (i // colonnes) * h
            if f is None:
                dessin.text((x + 8, y + 8), "(pas de vue avant)", fill="gray")
                continue
            img.paste(Image.open(f).convert("RGB").resize((l, h)), (x, y))
            etiquette = ("AVANT " if avant and i % 2 == 0 else "") + f.stem
            dessin.rectangle([x, y, x + 8 + 7 * len(etiquette), y + 22], fill="black")
            dessin.text((x + 4, y + 4), etiquette, fill="yellow")
        nom = dossier / (modele % (k // par_page + 1))
        img.save(nom, quality=85)
        sorties.append(str(nom))
    # 26/11 : note d'état dans le coffre OPTIMUS (0 token), poussée sur main par Obsidian Git
    return "Planches :\n" + "\n".join(sorties) + "\n" + etat_optimus.ecrire(sorties, os.getcwd())


def montrer(a):
    chemins = [Path(c) for c in a.get("chemins") or []]
    manquants = [str(c) for c in chemins if not c.exists()]
    if manquants:
        return "ERREUR : introuvable : " + ", ".join(manquants)
    if os.name != "nt":
        return "ERREUR : ouverture d'images seulement sur le PC Windows d'Adrien."
    dossiers = set()
    for c in chemins:
        os.startfile(str(c))  # visionneuse par défaut (ou explorateur pour un dossier)
        dossiers.add(c if c.is_dir() else c.parent)
        time.sleep(0.3)
    for d in dossiers - set(chemins):
        os.startfile(str(d))
    return "Ouvert sur l'écran d'Adrien : %d élément(s)." % len(chemins)


ERREUR_LUA = re.compile(r"\.lua:\d+:|attempt to (call|index|perform|compare|concatenate)|stack traceback")


def erreurs_lua(texte, n=3):
    """Lignes d'erreur Lua d'un morceau de console.log (au plus n)."""
    return [l.strip() for l in texte.splitlines() if ERREUR_LUA.search(l)][:n]


def _console(banc):
    return Path(banc.DATA).parent / "console.log"


def trouver_luajit():
    """LuaJIT de confiance : LUAJIT (chemin absolu) ou PATH sans le dossier courant ; jamais dans le dossier courant."""
    os.environ["NoDefaultCurrentDirectoryInExePath"] = "1"   # Windows : which() ne cherche plus dans le dossier courant
    exe = os.environ.get("LUAJIT") or shutil.which("luajit")
    if not exe or not os.path.isabs(exe) or not os.path.isfile(exe):
        return None
    if Path(os.path.realpath(exe)).parent == Path(os.path.realpath(os.getcwd())):
        return None
    return exe


def _installer(banc, scripts):
    """Contrôle (LuaJIT si présent) puis copie ; renvoie la liste des noms installés. Lève ValueError."""
    dossier = Path(banc.ADDON_DST) / "lua" / "autorun" / "client"
    luajit = trouver_luajit()
    if not luajit:
        raise ValueError("LuaJIT introuvable (PATH ou variable LUAJIT) : banc_passe n'installe pas de script non contrôlé")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
    import garde_lua  # mêmes règles que le hook : touches, coordonnées de map, musique
    racine = SOURCES.resolve()
    poses = []
    for sc in scripts:
        src, nom = Path(sc.get("source", "")), str(sc.get("nom", ""))
        if not src.is_file() or src.suffix.lower() != ".lua":
            raise ValueError("script .lua introuvable : %s" % src)
        try:
            src.resolve().relative_to(racine)
        except ValueError:
            raise ValueError("script hors de %s (variable BANC_SOURCES) : %s" % (racine, src)) from None
        refus = garde_lua.problemes(src.read_text(encoding="utf-8", errors="replace"))
        if refus:
            raise ValueError("script refusé (%s) : %s" % (src.name, refus[0]))
        if not re.fullmatch(r"[\w.\-]+\.lua", nom):
            raise ValueError("nom de script invalide : %r" % nom)
        cible = dossier / nom
        if not cible.is_file():
            raise ValueError("%s n'a jamais été chargé : un nouveau fichier autorun demande une bascule de map, pas un rechargement à chaud" % nom)
        r = subprocess.run([luajit, "-b", str(src), os.devnull], capture_output=True)
        if r.returncode:
            premiere = (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[0]
            raise ValueError("LuaJIT refuse %s : %s" % (src.name, premiere.rsplit(":", 1)[-1].strip()[:120]))
        shutil.copyfile(src, cible)
        poses.append(nom)
    return poses


def controle_dupe(dupe):
    """Contrôle auto (0 token) avant de coller : renvoie (erreur ou None, ligne de rapport)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outils"))
    import controle_auto
    piece = {}
    for d in [Path.cwd(), *Path.cwd().parents]:
        f = d / ".claude" / "builds-evo" / "piece.json"
        if f.is_file():
            try:
                piece = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                pass
            break
    boite = piece.get("boite") if isinstance(piece.get("boite"), list) and len(piece["boite"]) == 3 else None
    try:
        erreurs, attentions, res = controle_auto.controler(dupe, piece.get("budget_scene"), boite)
    except Exception as e:  # dupe illisible : on ne bloque pas, on le dit
        return None, "contrôle auto : sauté (%s)" % str(e)[:80]
    texte = controle_auto.rapport(erreurs, attentions, res)
    return ("ERREUR : passe refusée par le contrôle auto, rien n'a été collé :\n" + texte) if erreurs else None, texte


def passe(a):
    banc = charger_banc()
    if not banc.gmod_tourne():
        return "ERREUR : GMod est fermé. banc_passe ne lance jamais GMod : demande l'accord d'Adrien et lance-le avec banc_tester."
    temps, t0 = [], time.time()

    def etape(nom):
        nonlocal t0
        temps.append("%s %.0f s" % (nom, time.time() - t0))
        t0 = time.time()

    if a.get("generateur"):
        racine = SOURCES.resolve()
        gen, params = Path(a["generateur"]).resolve(), Path(a.get("params") or "").resolve()
        for f, ext in ((gen, ".py"), (params, ".json")):
            if not f.is_file() or f.suffix.lower() != ext:
                raise ValueError("fichier %s introuvable : %s" % (ext, f))
            try:
                f.relative_to(racine)
            except ValueError:
                raise ValueError("%s hors de %s (variable BANC_SOURCES)" % (f, racine)) from None
        r = subprocess.run([sys.executable, str(gen), str(params)], cwd=str(params.parent), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=600)
        if r.returncode:
            return "ERREUR : le générateur a échoué :\n" + resume((r.stdout or "") + "\n" + (r.stderr or ""), 8)
        etape("générer")
    controle = ""
    if a.get("dupe") and a.get("controle", True) and Path(a["dupe"]).is_file():
        refus, controle = controle_dupe(a["dupe"])
        if refus:
            return refus
        etape("contrôle")
    poses = _installer(banc, a.get("scripts") or [])
    if poses:
        time.sleep(int(a.get("attente_rechargement", 25)))
        etape("scripts")
    console = _console(banc)
    debut = console.stat().st_size if console.is_file() else 0
    sortie = tester({k: a[k] for k in ("dupe", "vues", "x", "y", "type") if k in a}, verifier=False)   # gmod_tourne vérifié plus haut
    etape("coller + vues")
    if sortie.startswith("ERREUR"):
        return sortie
    m = re.search(r"captures : \d+ dans (.+)", sortie)
    if not m:
        return "ERREUR : pas de dossier de captures dans la sortie du banc :\n" + sortie
    captures = m.group(1).strip()
    erreurs = []
    if console.is_file():
        with open(console, "rb") as f:
            f.seek(debut)
            erreurs = erreurs_lua(f.read().decode("utf-8", "replace"))
    lignes = [l for l in sortie.splitlines() if l.startswith("entit")]
    if erreurs:
        if a.get("nettoyer", True):
            nettoyer({})
        return ("ERREUR : planche refusée, erreur Lua dans la console pendant la passe (un script a pu ne rien dessiner) :\n"
                + "\n".join(erreurs) + "\ncaptures (à ne pas juger) : " + captures)
    res = planche({"dossier": captures, "avant": a["avant"]} if a.get("avant") else {"dossier": captures})
    etape("planche")
    if res.startswith("ERREUR"):
        return res
    images = res.splitlines()[1:]
    if a.get("montrer", True):
        montrer({"chemins": images})
    if a.get("nettoyer", True):
        nettoyer({})
        etape("nettoyer")
    return "\n".join(lignes + ([controle] if controle else []) + ["console : aucune erreur Lua", "scripts : " + (", ".join(poses) or "aucun")]
                     + ["planche : " + i for i in images] + ["temps : " + ", ".join(temps)])


ACTIONS = {"banc_passe": passe, "banc_etat": etat, "banc_tester": tester, "banc_nettoyer": nettoyer, "banc_planche": planche, "banc_montrer": montrer}


def repondre(i, res=None, err=None):
    m = {"jsonrpc": "2.0", "id": i}
    if err:
        m["error"] = {"code": -32603, "message": err}
    else:
        m["result"] = res
    sys.stdout.write(json.dumps(m, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    for ligne in sys.stdin:
        if not ligne.strip():
            continue
        try:
            msg = json.loads(ligne)
        except ValueError:
            continue
        meth, i = msg.get("method"), msg.get("id")
        if i is None:
            continue
        if meth == "initialize":
            repondre(i, {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                         "capabilities": {"tools": {}}, "serverInfo": {"name": "banc", "version": "0.2.0"}})
        elif meth == "tools/list":
            repondre(i, {"tools": [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p}}
                                   for n, d, p in OUTILS]})
        elif meth == "tools/call":
            p = msg.get("params", {})
            action = ACTIONS.get(p.get("name"))
            if not action:
                repondre(i, err="outil inconnu : %s" % p.get("name"))
                continue
            try:
                texte = action(p.get("arguments") or {})
            except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as e:
                texte = "ERREUR : %s" % e
            repondre(i, {"content": [{"type": "text", "text": texte}], "isError": texte.startswith("ERREUR")})
        elif meth == "ping":
            repondre(i, {})
        else:
            repondre(i, err="méthode inconnue : %s" % meth)


if __name__ == "__main__":
    main()
