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
# copie versionnée du banc, livrée avec le plugin (banc/README.md) : banc_etat signale un écart
COPIE_BANC = Path(__file__).resolve().parents[1] / "banc" / "banc.py"

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
    ("da_mesurer",
     "Mesure gratuite (0 token d'image) des captures d'un dossier contre la fiche DA : luminance, saturation, contraste du point "
     "focal, test yeux plissés, cadre sombre, palette hex et accent. Ne renvoie que les vues avec alerte. À lancer avant de lire une planche.",
     {"dossier": {"type": "string"}, "fiche": {"type": "string", "description": "fiche DA (.md) ; défaut : fiche_da de piece.json"},
      "sortie": {"type": "array", "items": {"type": "number"}, "description": "zone de la suite du chemin [x0, y0, x1, y1] en fractions de l'image : doit être des plus claires"}}),
    ("da_fiche",
     "Contrôle gratuit d'une fiche DA (modèle build-evo/modeles/fiche-da.md) : champs remplis, palette en hex, 3 mots-images, 3 indices. "
     "À lancer avant la maquette ; erreurs = fiche à compléter.",
     {"fiche": {"type": "string", "description": "chemin de la fiche DA (.md) ; défaut : fiche_da de piece.json"}}),
    ("sequence_controler",
     "Contrôle gratuit d'une séquence (JSON de la maquette) : un seul effet primaire à la fois, anticipation avant le pic, silence "
     "avant le sommet, une nouveauté par palier, crescendo, sons ponctuels espacés de 8 à 30 s. Format : outils/controle_sequence.py.",
     {"sequence": {"type": "string", "description": "chemin du sequence.json"}}),
    ("perf_rapport",
     "Rapport de profilage gratuit : lit un JSON de mesures (une par version : posés, ms du script, dessins, fps, lumières dynamiques, "
     "quads) et dit ce qui coûte et quoi corriger. Format : outils/rapport_perf.py.",
     {"mesures": {"type": "string", "description": "chemin du mesures.json"}}),
    ("grille_auto",
     "Pré-remplit la grille de contrôle (grille-controle.md) avec toutes les mesures gratuites : [x] respecté, [ ] à corriger "
     "(avec les vues), [?] à juger par un humain. Ne note jamais. À lancer avant la critique : elle ne juge que les [?].",
     {"dossier": {"type": "string", "description": "dossier de captures"}, "fiche": {"type": "string", "description": "fiche DA (.md) ; défaut : fiche_da de piece.json"},
      "dupe": {"type": "string"}, "sequence": {"type": "string"}, "mesures": {"type": "string"},
      "sortie": {"type": "array", "items": {"type": "number"}}}),
    ("palette_extraire",
     "Extrait dominante, neutres et accent d'images de référence (fiche DA, fiches 02 et 10) et, avec fiche=, écrit la ligne « Palette en hex ». "
     "Une suggestion à faire valider par Adrien.",
     {"sources": {"type": "array", "items": {"type": "string"}, "description": "images ou dossiers de références"},
      "fiche": {"type": "string", "description": "fiche DA à mettre à jour (facultatif)"}}),
    ("color_script",
     "Color script d'une séquence : une capture par temps fort, côte à côte (planche écrite dans le dossier), alerte si deux temps forts "
     "se ressemblent ou si la couleur la plus vive n'est pas au sommet.",
     {"dossier": {"type": "string"}}),
    ("maquette_faire",
     "Génère la maquette three.js d'une pièce (étape 7) depuis un dupe ou un scene.json, puis, avec capturer=true, exporte des PNG par vue et par "
     "mode (gris, rendu) et les mesure contre la fiche DA. 0 jeton d'image ; Playwright requis pour capturer.",
     {"scene": {"type": "string", "description": "dupe .txt ou scene.json"}, "fiche": {"type": "string"}, "vues": {"type": "string"},
      "sequence": {"type": "string"}, "sortie": {"type": "string", "description": "dossier de sortie (défaut : dossier de la scène)"},
      "capturer": {"type": "boolean"}, "temps": {"type": "number", "description": "instant de la séquence pour le mode rendu"}}),
    ("maquette_passe",
     "Une passe de maquette en un seul appel : maquette, captures gris et rendu aux temps forts, vues bouchées, mesures DA, grille pré-remplie au "
     "sommet, color script. Renvoie les alertes seulement. À préférer à maquette_faire + color_script + grille_auto (moins d'appels, moins de jetons).",
     {"scene": {"type": "string"}, "fiche": {"type": "string"}, "vues": {"type": "string"}, "sequence": {"type": "string"},
      "temps": {"type": "array", "items": {"type": "number"}, "description": "temps forts en s (défaut : 0 et le sommet)"},
      "vue_cs": {"type": "string", "description": "vue du color script (défaut : la dernière)"},
      "dossier": {"type": "string", "description": "dossier de sortie (défaut : passe/ à côté de la scène)"}}),
    ("da_calibrer",
     "Calibre la mesure DA sur les notes d'Adrien. action=noter : enregistre les mesures d'un dossier de captures avec la note /10 qu'il a donnée "
     "(à faire à chaque planche notée). action=analyser : dit quelles mesures corrèlent avec ses notes et quel seuil sépare >= 7,5 du reste.",
     {"action": {"type": "string", "description": "noter ou analyser"}, "dossier": {"type": "string"}, "note": {"type": "number"},
      "version": {"type": "string"}, "piece": {"type": "string"}, "journal": {"type": "string", "description": "défaut .claude/builds-evo/calibration.jsonl"}}),
    ("da_ressemblance",
     "Compare des captures à l'image maîtresse de la fiche DA (couleurs, répartition clair/sombre, tonalité) : repère une scène qui s'éloigne "
     "de l'ambiance visée. 0 jeton d'image ; une alerte est un signal, pas un jugement.",
     {"reference": {"type": "string", "description": "image maîtresse"}, "captures": {"type": "string", "description": "capture ou dossier de captures"}}),
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
      "montrer": {"type": "boolean", "description": "défaut true"}, "da": {"type": "boolean", "description": "défaut true : mesure DA des captures (outils/mesure_da.py, fiche_da de piece.json)"}, "nettoyer": {"type": "boolean", "description": "défaut true"},
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


def ecart_copie(banc_py=None, copie=None):
    """Une ligne si le banc du PC diffère de la copie versionnée du plugin, sinon None (0 jeton quand tout va bien)."""
    banc_py, copie = Path(banc_py or BANC_PY), Path(copie or COPIE_BANC)
    try:
        if banc_py.read_bytes().replace(b"\r\n", b"\n") == copie.read_bytes().replace(b"\r\n", b"\n"):
            return None
    except OSError:
        return None
    return ("banc.py du PC différent de la copie versionnée du plugin (banc/banc.py) : si le changement est voulu, "
            "le reporter par PR (banc/README.md).")


def etat(_):
    lignes = ["GMod ouvert : %s" % ("oui" if gmod_ouvert() else "non")]
    ecart = ecart_copie()
    if ecart:
        lignes.append(ecart)
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


def mesure_da(dossier, fiche=None, sortie=None):
    """Mesure DA des captures (0 token). Renvoie le texte court, ou une ligne d'explication si impossible."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outils"))
    import mesure_da as m
    if not fiche:
        for d in [Path.cwd(), *Path.cwd().parents]:
            f = d / ".claude" / "builds-evo" / "piece.json"
            if f.is_file():
                try:
                    fiche = json.loads(f.read_text(encoding="utf-8")).get("fiche_da")
                except ValueError:
                    pass
                break
    if fiche and not Path(fiche).is_file():
        return "mesure DA : fiche introuvable (%s)" % fiche
    try:
        return m.mesurer_dossier(dossier, fiche, sortie=sortie)
    except ImportError:
        return "mesure DA : sautée (Pillow manque)"
    except OSError as e:
        return "mesure DA : sautée (%s)" % str(e)[:80]


def _outil(nom):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outils"))
    return __import__(nom)


def _rapport(erreurs, attentions, ok):
    lignes = ["ERREUR : " + e for e in erreurs] if erreurs else []
    return "\n".join(lignes + ["ATTENTION : " + t for t in attentions]) or ok


def da_fiche(a):
    fiche = a.get("fiche")
    if not fiche:
        for d in [Path.cwd(), *Path.cwd().parents]:
            f = d / ".claude" / "builds-evo" / "piece.json"
            if f.is_file():
                try:
                    fiche = json.loads(f.read_text(encoding="utf-8")).get("fiche_da")
                except ValueError:
                    pass
                break
    if not fiche or not Path(fiche).is_file():
        raise ValueError("fiche DA introuvable (donner `fiche` ou le champ fiche_da de piece.json)")
    erreurs, att = _outil("controle_fiche").controler(Path(fiche).read_text(encoding="utf-8"))
    # une fiche à compléter n'est pas une erreur du serveur : le texte commence par « fiche incomplète »
    return _rapport(erreurs, att, "fiche DA complète") if not erreurs else "fiche incomplète :\n" + _rapport(erreurs, att, "")


def sequence_controler(a):
    chemin = Path(a["sequence"])
    if not chemin.is_file():
        raise ValueError("séquence introuvable : %s" % chemin)
    try:
        seq = json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError("séquence illisible : %s" % e) from None
    erreurs, att = _outil("controle_sequence").controler(seq)
    return _rapport(erreurs, att, "séquence conforme aux règles de rythme") if not erreurs else "séquence à corriger :\n" + _rapport(erreurs, att, "")


def perf_rapport(a):
    chemin = Path(a["mesures"])
    if not chemin.is_file():
        raise ValueError("mesures introuvables : %s" % chemin)
    try:
        mesures = json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError("mesures illisibles : %s" % e) from None
    lignes, alertes = _outil("rapport_perf").controler(mesures)
    return "\n".join(lignes + ["ATTENTION : " + t for t in alertes] or ["aucune mesure"]) if alertes or lignes else "aucune mesure"


def grille_auto(a):
    fiche = a.get("fiche")
    if not fiche:
        for d in [Path.cwd(), *Path.cwd().parents]:
            f = d / ".claude" / "builds-evo" / "piece.json"
            if f.is_file():
                try:
                    fiche = json.loads(f.read_text(encoding="utf-8")).get("fiche_da")
                except ValueError:
                    pass
                break
    if fiche and not Path(fiche).is_file():
        fiche = None
    try:
        return _outil("grille_auto").grille(a.get("dossier"), fiche, a.get("dupe"), a.get("sequence"), a.get("mesures"), a.get("sortie"))
    except ImportError:
        raise ValueError("Pillow manque (pip install pillow)") from None


def palette_extraire(a):
    args = list(a.get("sources") or [])
    if not args:
        raise ValueError("`sources` : au moins une image ou un dossier")
    if a.get("fiche"):
        args += ["--ecrire", a["fiche"]]
    return _lancer_outil("palette_ref", args)


def color_script(a):
    return _lancer_outil("color_script", [a["dossier"], "--sortie", str(Path(a["dossier"]) / "color_script.png")])


def _lancer_outil(nom, args, delai=120):
    """Lance un outil en ligne de commande et renvoie sa sortie (erreur si code 2)."""
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "outils" / (nom + ".py")), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=delai, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if r.returncode:
        raise ValueError((r.stderr or r.stdout).strip()[:300] or "échec de %s" % nom)
    return r.stdout.strip()


def maquette_faire(a):
    sortie = Path(a.get("sortie") or Path(a["scene"]).resolve().parent)
    sortie.mkdir(parents=True, exist_ok=True)
    html = sortie / "maquette.html"
    args = [a["scene"], "--sortie", str(html)]
    for cle in ("fiche", "vues", "sequence"):
        if a.get(cle):
            args += ["--" + cle, a[cle]]
    texte = _lancer_outil("faire_maquette", args)
    if a.get("capturer"):
        cap = [str(html), "--sortie", str(sortie / "captures_maquette"), "--temps", str(a.get("temps", 0))]
        if a.get("fiche"):
            cap += ["--fiche", a["fiche"]]
        texte += "\n" + _lancer_outil("capturer_maquette", cap, delai=300)
    return texte


def maquette_passe(a):
    args = [a["scene"], "--dossier", a.get("dossier") or str(Path(a["scene"]).resolve().parent / "passe")]
    for cle in ("fiche", "vues", "sequence"):
        if a.get(cle):
            args += ["--" + cle, a[cle]]
    if a.get("vue_cs"):
        args += ["--vue-cs", a["vue_cs"]]
    if a.get("temps"):
        args += ["--temps", *[str(t) for t in a["temps"]]]
    return _lancer_outil("passe_maquette", args, delai=600)


def da_calibrer(a):
    act = a.get("action", "analyser")
    args = [act]
    if act == "noter":
        if "dossier" not in a or "note" not in a:
            raise ValueError("`dossier` et `note` obligatoires pour noter")
        args += [a["dossier"], str(a["note"])]
        for cle in ("version", "piece"):
            if a.get(cle):
                args += ["--" + cle, a[cle]]
    elif act != "analyser":
        raise ValueError("action : noter ou analyser")
    if a.get("journal"):
        args += ["--journal", a["journal"]]
    return _lancer_outil("calibration", args)


def da_ressemblance(a):
    return _lancer_outil("ressemblance", [a["reference"], a["captures"]])


def da_mesurer(a):
    return mesure_da(a["dossier"], a.get("fiche"), a.get("sortie"))


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
    mesure = mesure_da(captures) if a.get("da", True) else ""
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
    return "\n".join(lignes + ([controle] if controle else []) + ([mesure] if mesure else []) + ["console : aucune erreur Lua", "scripts : " + (", ".join(poses) or "aucun")]
                     + ["planche : " + i for i in images] + ["temps : " + ", ".join(temps)])


ACTIONS = {"banc_passe": passe, "banc_etat": etat, "banc_tester": tester, "banc_nettoyer": nettoyer, "banc_planche": planche, "banc_montrer": montrer, "da_mesurer": da_mesurer, "da_fiche": da_fiche, "sequence_controler": sequence_controler, "perf_rapport": perf_rapport, "grille_auto": grille_auto, "palette_extraire": palette_extraire, "color_script": color_script, "maquette_faire": maquette_faire, "maquette_passe": maquette_passe, "da_calibrer": da_calibrer, "da_ressemblance": da_ressemblance}


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
