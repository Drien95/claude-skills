"""Banc d'essai des builds GMod, en solo sur gm_flatgrass.

Usage (depuis n'importe où) :
  python banc.py installer                       copie l'addon dans garrysmod/addons/banc_essai
  python banc.py tester DUPE.txt [--vues V.json] [--lancer] [--attente 600] [--x 0 --y 0]
                                                 copie le dupe, écrit la tâche, attend les captures

--lancer démarre GMod en solo sur gm_flatgrass s'il ne tourne pas. Si GMod tourne déjà en solo
sur gm_flatgrass, la tâche part toute seule (l'addon regarde la tâche chaque seconde).
Les captures et rapport.json arrivent dans captures/<nom-du-dupe>/<type>_<id>/ à côté du dupe (--type, parcours par défaut).

Le plan (--vues, facultatif) est en coordonnées de scene.json (celles de build.py) :
  {"vues": [{"nom": "entree", "pos": [x, y, z_oeil], "vise": [x, y, z]},
            {"nom": "plafond", "pos": [...], "ang": [pitch, yaw, 0], "pave": [2]}],
   "passages": [{"nom": "verrou 1", "de": [x, y, z_pieds], "a": [x, y, z_pieds]}],
   "vues_auto": true}
"pave" appuie sur ces touches du pavé numérique juste avant la vue (les bascules restent jusqu'au prochain appui).
Un passage dit si un joueur (boîte 32 x 32 x 72) peut aller en ligne droite de "de" à "a", et ce qui le bloque.
Une simple liste de vues est aussi acceptée.
"""
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path

GMOD = Path(r"C:\SteamLibrary\steamapps\common\GarrysMod")
DATA = GMOD / "garrysmod" / "data"
ADDON_SRC = Path(__file__).resolve().parent / "addon"
ADDON_DST = GMOD / "garrysmod" / "addons" / "banc_essai"
PLACES_MAX = 2  # 20/11 : serveur local d'écoute de 2 places au plus (hôte + un bot), jamais un dédié ni un vrai serveur


def lancement(mode="sandbox", places=1, carte="gm_flatgrass", w=1600, h=900, sans_focus=False, eclair=False):
    """sans_focus (côte à côte) : fps_max_nofocus 60, GMod continue de dessiner quand l'Atelier a le focus
    (21/11 : engine_no_focus_sleep n'existe pas dans GMod ; fps_max_nofocus est dans engine.dll, effet à vérifier en jeu)."""
    return [str(GMOD / "bin" / "win64" / "gmod.exe"), "-steam", "-game", "garrysmod", "-windowed",
            "-noborder", "-w", str(int(w)), "-h", str(int(h)), "-novid", "-nojoy", "-condebug",
            "+gamemode", mode, "+maxplayers", str(places), "+map", carte] + (
            ["+fps_max_nofocus", "60"] if sans_focus else []) + (
            ["-noworkshop"] if eclair else [])   # 21/11 : GMod éclair, sans les addons du workshop (contenu utile copié par l'Atelier)



def lancer_sans_focus(cmd, **kw):
    """24/11 : un GMod fraîchement lancé prenait le premier plan (Windows active toute nouvelle fenêtre),
    même sans --focus. On le lance « affiché sans activation » (SW_SHOWNOACTIVATE).
    26/11 : en éclair (-noworkshop), les addons locaux d'Adrien sont coupés avant le lancement
    (-noworkshop ne touche pas garrysmod/addons) et remis dès que GMod se ferme."""
    eclair = "-noworkshop" in cmd
    if eclair:
        try:
            couper_addons_perso()
        except Exception:
            remettre_addons_perso()  # coupure à moitié faite : tout remettre avant de refuser
            raise
    si =subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = 4
    try:
        jeu = subprocess.Popen(cmd, startupinfo=si, **kw)
    except OSError:
        if eclair:
            remettre_addons_perso()
        raise
    if eclair:
        surveiller_fermeture()
    return jeu


# --- 26/11 : addons d'Adrien coupés pendant le GMod éclair du banc ---------------------------------
ADDONS = GMOD / "garrysmod" / "addons"
JOURNAL_ADDONS = Path(__file__).resolve().parent / "addons_coupes.json"
PREFIXE_BANC = "banc_"           # seuls les addons du banc restent chargés
MARQUES_ADDON = ("addon.json", "addon.txt", "lua", "models", "materials", "sound", "maps", "gamemodes",
                 "particles", "resource", "scripts")
ATTENTE_MAX_FERMETURE = 48 * 3600  # borne de la surveillance (s)


def est_addon(dossier):
    return dossier.is_dir() and any((dossier / m).exists() for m in MARQUES_ADDON)


def couper_addons_perso():
    """Préfixe « . » (convention GMod et addon_manager.py d'Adrien) devant chaque addon qui n'est pas du banc.
    Le journal est écrit AVANT chaque renommage : une coupure n'est jamais perdue."""
    remettre_addons_perso()  # reste d'un essai précédent : on repart propre
    if JOURNAL_ADDONS.is_file():
        raise RuntimeError("addons d'un essai précédent pas encore remis (addons_coupes.json) : lancement refusé")
    coupes = []
    for d in sorted(ADDONS.iterdir()):
        if d.name.startswith((".", PREFIXE_BANC)) or not est_addon(d):
            continue
        cible = ADDONS / ("." + d.name)
        if cible.exists():
            raise RuntimeError(f"addon déjà présent en version coupée : {cible.name} (à régler à la main)")
        coupes.append(d.name)
        JOURNAL_ADDONS.write_text(json.dumps(coupes, ensure_ascii=False, indent=1), encoding="utf-8")
        d.rename(cible)
    if not JOURNAL_ADDONS.is_file():
        JOURNAL_ADDONS.write_text("[]", encoding="utf-8")  # le journal porte aussi la coupure du workshop
    n_ws = couper_workshop()
    print(f"addons d'Adrien coupés le temps du banc : {len(coupes)} locaux, {n_ws} du workshop")


# Workshop : -noworkshop ne suffit pas (Steam signale les abonnements et GMod remonte tout, vu par l'Atelier
# le 21/11). Même méthode que atelier/moteur/workshop.py : tous les abonnements dans cfg/addonnomount.txt,
# l'original d'Adrien gardé à côté, remis seulement GMod fermé (GMod réécrit ce fichier en quittant).
WORKSHOP = GMOD.parent.parent / "workshop" / "content" / "4000"
NOMOUNT = GMOD / "garrysmod" / "cfg" / "addonnomount.txt"
NOMOUNT_BANC = NOMOUNT.with_name(NOMOUNT.name + ".banc")
NOMOUNT_ATELIER = NOMOUNT.with_name(NOMOUNT.name + ".atelier")


def couper_workshop():
    if NOMOUNT_ATELIER.exists():
        raise RuntimeError("workshop déjà coupé par l'Atelier (addonnomount.txt.atelier) : lancement refusé")
    ids = sorted(d.name for d in WORKSHOP.iterdir() if d.name.isdigit()) if WORKSHOP.is_dir() else []
    if not NOMOUNT_BANC.exists():  # jamais écraser l'original déjà gardé
        if NOMOUNT.exists():
            shutil.copy2(NOMOUNT, NOMOUNT_BANC)
        else:
            NOMOUNT_BANC.write_text('"addonnomount"\n{\n}\n', encoding="utf-8")
    NOMOUNT.write_text('"addonnomount"\n{\n' + "".join(f'\t"{i}"\t"1"\n' for i in ids) + "}\n",
                       encoding="utf-8", newline="\n")
    return len(ids)


def remettre_workshop():
    if NOMOUNT_BANC.exists():
        NOMOUNT_BANC.replace(NOMOUNT)


def remettre_addons_perso():
    """Remet les addons du journal. Ne fait rien si GMod tourne (dossiers en cours d'usage)."""
    if not JOURNAL_ADDONS.is_file() and not NOMOUNT_BANC.exists():
        return 0
    if gmod_tourne():
        return -1
    remettre_workshop()
    if not JOURNAL_ADDONS.is_file():
        return 0
    coupes = json.loads(JOURNAL_ADDONS.read_text(encoding="utf-8"))
    restent = []
    for nom in coupes:
        coupe, propre = ADDONS / ("." + nom), ADDONS / nom
        if coupe.is_dir() and not propre.exists():
            try:
                coupe.rename(propre)
            except OSError:
                restent.append(nom)
        elif coupe.is_dir():
            restent.append(nom)  # les deux existent : on ne choisit pas à la place d'Adrien
    if restent:
        JOURNAL_ADDONS.write_text(json.dumps(restent, ensure_ascii=False, indent=1), encoding="utf-8")
        print("addons non remis (voir addons_coupes.json) :", ", ".join(restent))
    else:
        JOURNAL_ADDONS.unlink()
    return len(coupes) - len(restent)


def surveiller_fermeture():
    """Processus caché et détaché qui attend la fermeture de GMod puis remet les addons
    (pas de console visible ; sorties fermées pour ne pas bloquer le MCP qui lit celles du banc)."""
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "remettre", "--attendre"],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)


def remettre(a):
    if a.attendre:
        fin = time.monotonic() + ATTENTE_MAX_FERMETURE
        time.sleep(30)  # laisser GMod apparaître dans la liste des processus
        while gmod_tourne() and time.monotonic() < fin:
            time.sleep(5)
    n = remettre_addons_perso()
    print("GMod ouvert : addons laissés coupés" if n == -1 else f"addons remis : {n}")

def garder_focus(duree):
    """24/11 : même lancé sans activation, le moteur Source se met lui-même au premier plan (console « focus true »).
    Garde-fou : pendant le test, dès que GMod prend le premier plan, on le rend à la fenêtre qu'Adrien avait avant.
    (Rendu : sans focus, GMod peut ne plus dessiner les props ; captures vides = le dire, ne pas forcer.)"""
    import ctypes, threading
    u = ctypes.windll.user32
    avant = u.GetForegroundWindow()
    arret = threading.Event()

    def boucle():
        fin = time.monotonic() + duree; n = 0
        while not arret.is_set() and time.monotonic() < fin:
            g = fenetre_gmod()
            if g and avant and u.GetForegroundWindow() == g and u.IsWindow(avant):
                u.keybd_event(0x12, 0, 0, 0)
                u.SetForegroundWindow(avant)
                u.keybd_event(0x12, 0, 2, 0)
                gmod_en_bas(); n += 1
                if n == 1:
                    print("garde-focus : GMod a pris le premier plan, rendu à la fenêtre d'avant")
            arret.wait(0.2)
        if n:
            print(f"garde-focus : premier plan rendu {n} fois")

    threading.Thread(target=boucle, daemon=True).start()
    return arret


def partie():
    """État de la partie ouverte, écrit chaque seconde par l'addon (carte, mode, places, solo)."""
    f = DATA / "banc_essai" / "partie.txt"
    try:
        etat = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return etat if time.time() - etat.get("heure", 0) < 10 else None


def installer():
    # 16/11 : copie par-dessus, sans effacer le dossier (GMod ne voit pas un fichier recréé),
    # avec une date neuve (copy2 gardait l'ancienne) : le Lua se recharge alors dans le jeu ouvert.
    shutil.copytree(ADDON_SRC, ADDON_DST, copy_function=shutil.copy, dirs_exist_ok=True)
    for f in ADDON_DST.rglob("*.lua"):
        f.touch()
    print("addon installé :", ADDON_DST)


def gmod_tourne():
    sortie = subprocess.run(["tasklist", "/FI", "IMAGENAME eq gmod.exe", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True).stdout
    return "gmod.exe" in sortie.lower()


def ecrire_tache(dupe, plan, x, y, focus=False, carte="gm_flatgrass", poser=False, origine=None, attente_vue=1.5, film=None):
    tache_id = time.strftime("%Y%m%d-%H%M%S")
    if isinstance(plan, list):
        plan = {"vues": plan}
    tache = {"id": tache_id, "dupe": "banc/" + dupe.name, "carte": carte, "x": x, "y": y,
             "attente": attente_vue, "pause": 3, "vues": plan.get("vues", []),
             "passages": plan.get("passages", []), "rayons": plan.get("rayons", []), "vues_auto": plan.get("vues_auto", True),
             "convars_client": plan.get("convars_client", {}), "focus": focus, "poser": poser, "origine": origine,
             "film": film}
    dossier = DATA / "banc_essai"
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "tache.txt").write_text(json.dumps(tache, ensure_ascii=False), encoding="utf-8")
    return tache_id


def focus_gmod():
    """Met la fenêtre GMod au premier plan : sans le focus, GMod n'appelle plus ses hooks de rendu (16/11)."""
    import ctypes
    u = ctypes.windll.user32
    trouvee = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def visiter(h, _):
        titre = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, titre, 256)
        if titre.value.startswith("Garry's Mod") and u.IsWindowVisible(h):
            trouvee.append(h)
        return True

    u.EnumWindows(visiter, 0)
    if not trouvee or u.GetForegroundWindow() == trouvee[0]:
        return
    u.keybd_event(0x12, 0, 0, 0)   # Alt : Windows autorise alors le changement de premier plan
    u.ShowWindow(trouvee[0], 9)
    u.SetForegroundWindow(trouvee[0])
    u.keybd_event(0x12, 0, 2, 0)


def gmod_en_bas():
    """Met GMod tout en bas de la pile des fenêtres, sans l'activer (19/11) : quand Adrien ferme ou réduit
    une fenêtre, Windows active la suivante dans la pile ; GMod, mis devant une fois, était cette suivante."""
    import ctypes
    u = ctypes.windll.user32
    trouvees = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def visiter(h, _):
        titre = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, titre, 256)
        if titre.value.startswith("Garry's Mod") and u.IsWindowVisible(h):
            trouvees.append(h)
        return True

    u.EnumWindows(visiter, 0)
    for h in trouvees:
        if u.GetForegroundWindow() != h:  # jamais toucher à la fenêtre qu'Adrien utilise
            u.SetWindowPos(ctypes.c_void_p(h), ctypes.c_void_p(1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)


def attendre(tache_id, delai, focus=False):
    fait = DATA / "banc_essai" / "fait.txt"
    fin = time.monotonic() + delai
    while time.monotonic() < fin:
        # 19/11 : sans le focus, GMod ne dessine pas les props (console : 302 props reçus, rien à l'image).
        # Seulement avec --focus : Adrien ne veut pas qu'on lui vole le focus sans prévenir (16/11).
        if focus:
            focus_gmod()
        else:
            gmod_en_bas()
        if fait.exists():
            try:
                etat = json.loads(fait.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                etat = {}
            if etat.get("id") == tache_id:
                return etat
        time.sleep(2)
    return None


def basculer(dupe, mode, carte):
    """20/11 : change le mode de jeu du GMod ouvert (même nombre de places) par une petite tâche
    que l'addon serveur exécute (gamemode puis changelevel), et attend que la partie le confirme."""
    etat = partie()
    if etat is None:
        sys.exit("GMod ouvert, mais l'addon du banc ne répond pas (pas en partie, ou partie refusée par le banc)")
    if etat.get("mode") == mode and etat.get("carte") == carte:
        return
    print(f"bascule : {etat.get('mode')} sur {etat.get('carte')} vers {mode} sur {carte}")
    tache_id = time.strftime("bascule-%Y%m%d-%H%M%S")
    (DATA / "banc_essai" / "tache.txt").write_text(json.dumps(
        {"id": tache_id, "dupe": "banc/" + dupe.name, "bascule": {"mode": mode, "carte": carte}}), encoding="utf-8")
    fin = time.monotonic() + 240
    while time.monotonic() < fin:
        time.sleep(3)
        etat = partie()
        if etat and etat.get("mode") == mode and etat.get("carte") == carte:
            print("bascule faite :", etat)
            time.sleep(10)  # laisser les addons finir de charger
            return
    sys.exit(f"bascule non confirmée (tâche {tache_id})")


def recuperer(tache_id, dupe, type_essai):
    # un dossier par version et par essai : rien n'est jamais écrasé
    source = DATA / "banc_essai" / "sortie" / tache_id
    cible = dupe.parent / "captures" / dupe.stem / f"{type_essai}_{tache_id}"
    shutil.copytree(source, cible)
    return cible


def erreurs_console():
    log = GMOD / "garrysmod" / "console.log"
    if not log.exists():
        return
    lignes = log.read_text(encoding="utf-8", errors="replace").splitlines()[-4000:]
    vues = [l for l in lignes if "banc_essai" in l or "[ERROR]" in l or "lua/" in l and "error" in l.lower()]
    for l in vues[-25:]:
        print("  console :", l[:200])


def planches(cible):
    """Planches de 9 captures, pour tout relire d'un coup."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    images = sorted(f for f in cible.glob("*.jpg") if not f.name.startswith("planche"))
    l, h = 640, 360
    for k in range(0, len(images), 9):
        planche = Image.new("RGB", (l * 3, h * 3))
        dessin = ImageDraw.Draw(planche)
        for i, f in enumerate(images[k:k + 9]):
            x, y = (i % 3) * l, (i // 3) * h
            planche.paste(Image.open(f).resize((l, h)), (x, y))
            dessin.rectangle([x, y, x + 260, y + 22], fill="black")
            dessin.text((x + 4, y + 4), f.stem, fill="yellow")
        planche.save(cible / f"planche_{k // 9 + 1}.jpg", quality=85)


def resumer(cible):
    r = json.loads((cible / "rapport.json").read_text(encoding="utf-8"))
    print(f"entités : {r.get('entites_creees')} créées sur {r.get('entites_dupe')}")
    for m in r.get("manquantes", []):
        print("  MANQUANTE :", m.get("classe"), m.get("modele"))
    for m in r.get("mobiles", []):
        print("  DÉGELÉE :", m.get("classe"), m.get("modele"))
    for p in r.get("passages", []):
        etat = f"BLOQUÉ par {p.get('par')}" if p.get("bloque") else "libre"
        print(f"  passage {p.get('nom')} : {etat}")
    for e in r.get("etats", []):
        print(f"  pavé {e.get('touches') or '-'} : {e.get('lumieres_allumees')} lumières allumées après relâche, {e.get('pendant_appui')} pendant l'appui, {e.get('en_bascule')} en mode bascule")
    for e in r.get("erreurs", []):
        print("  ERREUR :", e)
    print("captures :", len(r.get("captures", [])), "dans", cible)
    planches(cible)


def tester(a):
    dupe = Path(a.dupe).resolve()
    if not dupe.is_file():
        sys.exit(f"dupe introuvable : {dupe}")
    if not 1 <= a.places <= PLACES_MAX:
        sys.exit(f"--places : 1 à {PLACES_MAX} seulement")
    if not 0.3 <= a.attente_vue <= 5:
        sys.exit("--attente-vue : 0.3 à 5 secondes")
    vues = json.loads(Path(a.vues).read_text(encoding="utf-8")) if a.vues else []
    (DATA / "advdupe2" / "banc").mkdir(parents=True, exist_ok=True)
    shutil.copy2(dupe, DATA / "advdupe2" / "banc" / dupe.name)
    jeu = None
    if gmod_tourne():
        basculer(dupe, a.mode, a.carte)
    else:
        if not a.lancer:
            sys.exit("GMod ne tourne pas : relancer avec --lancer")
        jeu = lancer_sans_focus(lancement(a.mode, a.places, a.carte, sans_focus=True, eclair=a.eclair), cwd=str(GMOD))
        print(f"GMod lancé : {a.mode}, {a.places} place(s), {a.carte}" + (", éclair" if a.eclair else ""))
    tache_id = ecrire_tache(dupe, vues, a.x, a.y, a.focus, a.carte, attente_vue=a.attente_vue)
    print("tâche", tache_id, "écrite")
    garde = None if a.focus else garder_focus(a.attente + 60)
    try:
        etat = attendre(tache_id, a.attente, a.focus)
        if not a.focus:
            gmod_en_bas()
    finally:
        # le GMod lancé par le banc ne reste jamais ouvert derrière Adrien (16/11 : 1 fps en arrière-plan)
        if garde is not None:
            garde.set()
        if jeu is not None and not a.garder:
            jeu.kill()
            print("GMod du banc fermé")
    if etat is None:
        sys.exit("pas de réponse de GMod (GMod en solo sur gm_flatgrass ? addon installé ?)")
    if not etat.get("ok"):
        sys.exit(f"échec : {etat.get('raison')}")
    resumer(recuperer(tache_id, dupe, a.type))
    if a.console:
        erreurs_console()


def fenetre_gmod():
    """Fenêtre visible de GMod (titre « Garry's Mod »), ou None."""
    import ctypes
    u = ctypes.windll.user32
    trouvees = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def visiter(h, _):
        titre = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, titre, 256)
        if titre.value.startswith("Garry's Mod") and u.IsWindowVisible(h):
            trouvees.append(h)
        return True

    u.EnumWindows(visiter, 0)
    return trouvees[0] if trouvees else None


def placer_gmod(x, y, w, h, delai=180):
    """Place la fenêtre de GMod sans l'activer (jamais voler le focus) ; attend qu'elle existe. True si placée."""
    import ctypes
    fin = time.monotonic() + delai
    while time.monotonic() < fin:
        f = fenetre_gmod()
        if f:
            # SWP_NOZORDER | SWP_NOACTIVATE
            return bool(ctypes.windll.user32.SetWindowPos(ctypes.c_void_p(f), None, int(x), int(y), int(w), int(h), 0x0004 | 0x0010))
        time.sleep(1)
    return False


def attendre_fait(fichier, tache_id, delai):
    """Attend {"id": tache_id, ...} dans fichier (écrit par GMod) ; None après delai secondes."""
    fin = time.monotonic() + delai
    while time.monotonic() < fin:
        try:
            etat = json.loads(fichier.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            etat = {}
        if etat.get("id") == tache_id:
            return etat
        time.sleep(2)
    return None


def filmer(a):
    """21/11 (onglet En jeu) : colle le dupe dans le GMod solo du banc, joue le film de l'Atelier (fichier Lua de
    l'export, mêmes caméras) et l'enregistre (video.Record de GMod). La vidéo est déplacée dans --sortie."""
    dupe, lua = Path(a.dupe).resolve(), Path(a.lua).resolve()
    if not dupe.is_file() or not lua.is_file():
        sys.exit(f"introuvable : {dupe if not dupe.is_file() else lua}")
    if not re.fullmatch(r"atelier_[\w\-]+\.lua", lua.name, re.ASCII):
        sys.exit("--lua : un fichier atelier_<build>.lua exporté par l'Atelier")
    sortie = Path(a.sortie).resolve(); sortie.mkdir(parents=True, exist_ok=True)
    (DATA / "advdupe2" / "banc").mkdir(parents=True, exist_ok=True)
    shutil.copy2(dupe, DATA / "advdupe2" / "banc" / dupe.name)
    shutil.copy2(lua, GMOD / "garrysmod" / "lua" / lua.name)
    jeu = None
    if gmod_tourne():
        etat = partie()
        if etat is None or not etat.get("solo"):
            sys.exit("GMod est déjà ouvert hors du banc (sur un serveur ?) : ferme-le d'abord, je n'y touche pas")
        basculer(dupe, a.mode, a.carte)
    elif a.lancer:
        jeu = lancer_sans_focus(lancement(a.mode, 1, a.carte, 1920, 1080, sans_focus=True, eclair=a.eclair), cwd=str(GMOD))
        print("GMod lancé : 1920 x 1080" + (", éclair" if a.eclair else ""))
    else:
        sys.exit("GMod ne tourne pas : relancer avec --lancer")
    vues = json.loads(Path(a.vues).read_text(encoding="utf-8")) if a.vues else []
    tache_id = ecrire_tache(dupe, vues, a.x, a.y, False, a.carte, poser=True, film=lua.name)
    print("tâche", tache_id, "écrite")
    try:
        etat = attendre_fait(DATA / "banc_essai" / "fait.txt", tache_id, a.attente)
        if etat is None:
            sys.exit("pas de réponse de GMod (addon du banc ?)")
        if not etat.get("ok"):
            sys.exit(f"échec : {etat.get('raison')}")
        print("build posé, tournage")
        fait = attendre_fait(DATA / "atelier_film" / "fait.txt", tache_id, a.duree * 4 + 120)   # GMod rend plus lentement que le film (une image par 1/30 s)
        if fait is None:
            sys.exit("le film n'a pas fini (Lua du film chargé ? console.log)")
        if not fait.get("ok"):
            sys.exit(f"tournage raté : {fait.get('raison')}")
        source = GMOD / "garrysmod" / fait["video"]
        for _ in range(30):                              # GMod finit d'écrire le fichier
            if source.is_file() and source.stat().st_size > 0:
                break
            time.sleep(1)
        cible = sortie / source.name
        shutil.move(str(source), str(cible))
        print(f"vidéo : {cible} ({fait.get('largeur')} x {fait.get('hauteur')}, {cible.stat().st_size / 1e6:.1f} Mo)")
    finally:
        if jeu is not None and not a.garder:
            jeu.kill()
            print("GMod du banc fermé")


def poser(a):
    """21/11 (côte à côte) : colle le dupe dans le GMod solo du banc, sans photos, et range GMod dans le rectangle
    --cote x,y,w,h. GMod reste ouvert. Refuse si un GMod tourne sans l'addon du banc (par exemple sur EVO)."""
    dupe = Path(a.dupe).resolve()
    if not dupe.is_file():
        sys.exit(f"dupe introuvable : {dupe}")
    x0, y0, w, h = (int(float(v)) for v in a.cote.split(","))
    if not (320 <= w <= 8000 and 240 <= h <= 8000):
        sys.exit("--cote : taille de fenêtre invalide")
    (DATA / "advdupe2" / "banc").mkdir(parents=True, exist_ok=True)
    shutil.copy2(dupe, DATA / "advdupe2" / "banc" / dupe.name)
    if gmod_tourne():
        etat = partie()
        if etat is None or not etat.get("solo"):
            sys.exit("GMod est déjà ouvert hors du banc (sur un serveur ?) : ferme-le d'abord, je n'y touche pas")
        basculer(dupe, a.mode, a.carte)
    else:
        rw, rh = (int(v) for v in a.rendu.lower().split("x")) if a.rendu else (w, h)   # 21/11 : rendu 1920x1080, fenêtre réduite
        if not (320 <= rw <= 8000 and 240 <= rh <= 8000):
            sys.exit("--rendu : taille invalide")
        lancer_sans_focus(lancement(a.mode, 1, a.carte, rw, rh, sans_focus=True, eclair=a.eclair), cwd=str(GMOD))
        print(f"GMod lancé : {a.mode}, {a.carte}, {w} x {h}")
    print("GMod placé" if placer_gmod(x0, y0, w, h) else "fenêtre de GMod introuvable : non placée")
    origine = [float(v) for v in a.origine.split(",")] if a.origine else None
    if origine is not None and len(origine) != 3:
        sys.exit("--origine : x,y,z")
    vues = json.loads(Path(a.vues).read_text(encoding="utf-8")) if a.vues else []   # 21/11 : 1er plan du film = où regarder
    tache_id = ecrire_tache(dupe, vues, a.x, a.y, False, a.carte, poser=True, origine=origine)
    print("tâche", tache_id, "écrite")
    fait = DATA / "banc_essai" / "fait.txt"
    fin = time.monotonic() + a.attente
    while time.monotonic() < fin:
        try:
            etat = json.loads(fait.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            etat = {}
        if etat.get("id") == tache_id:
            if not etat.get("ok"):
                sys.exit(f"échec : {etat.get('raison')}")
            print("build posé dans GMod")
            return
        time.sleep(2)
    sys.exit("pas de réponse de GMod (addon du banc installé ?)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="cmd", required=True)
    sous.add_parser("installer")
    t = sous.add_parser("tester")
    t.add_argument("dupe")
    t.add_argument("--vues")
    t.add_argument("--lancer", action="store_true")
    t.add_argument("--type", default="parcours", help="étiquette du dossier de captures (parcours, pave...)")
    t.add_argument("--garder", action="store_true", help="laisser ouvert le GMod lancé par le banc")
    t.add_argument("--console", action="store_true", help="afficher les erreurs Lua de console.log")
    t.add_argument("--attente", type=int, default=600)
    t.add_argument("--focus", action="store_true", help="remettre GMod au premier plan pendant le test (prévenir Adrien avant)")
    t.add_argument("--mode", default="sandbox", help="mode de jeu (sandbox, darkrp...) ; le GMod ouvert bascule si besoin")
    t.add_argument("--carte", default="gm_flatgrass")
    t.add_argument("--attente-vue", type=float, default=1.5,
                   help="secondes entre la pose de la caméra et la photo (0.3 à 5 ; la 1re vue a en plus la pause de 3 s)")
    t.add_argument("--eclair", action="store_true", help="avec --lancer : GMod sans le workshop (contenu copié par l'Atelier)")
    t.add_argument("--places", type=int, default=1, help=f"places du serveur local lancé par --lancer (1 à {PLACES_MAX})")
    t.add_argument("--x", type=float, default=0)
    t.add_argument("--y", type=float, default=0)
    f = sous.add_parser("filmer", help="joue le film de l'Atelier dans le GMod du banc et l'enregistre")
    f.add_argument("dupe")
    f.add_argument("--lua", required=True, help="atelier_<build>.lua de l'export")
    f.add_argument("--sortie", required=True, help="dossier où ranger la vidéo")
    f.add_argument("--duree", type=float, default=120, help="durée du film (secondes)")
    f.add_argument("--vues", help="fichier JSON des vues (le joueur est posé à la première)")
    f.add_argument("--lancer", action="store_true"); f.add_argument("--eclair", action="store_true")
    f.add_argument("--garder", action="store_true", help="laisser ouvert le GMod lancé")
    f.add_argument("--mode", default="sandbox"); f.add_argument("--carte", default="gm_flatgrass")
    f.add_argument("--attente", type=int, default=600)
    f.add_argument("--x", type=float, default=0); f.add_argument("--y", type=float, default=0)
    o = sous.add_parser("poser", help="côte à côte : colle le dupe sans photos, GMod rangé dans --cote x,y,w,h")
    o.add_argument("dupe")
    o.add_argument("--cote", required=True, help="rectangle de la fenêtre de GMod : x,y,largeur,hauteur")
    o.add_argument("--mode", default="sandbox")
    o.add_argument("--carte", default="gm_flatgrass")
    o.add_argument("--attente", type=int, default=300)
    o.add_argument("--eclair", action="store_true", help="GMod sans le workshop (-noworkshop)")
    o.add_argument("--rendu", help="LxH : résolution de rendu de GMod (la fenêtre est ensuite réduite au rectangle --cote)")
    o.add_argument("--vues", help="fichier JSON des vues (le joueur est posé à la première)")
    o.add_argument("--origine", help="x,y,z : où poser l'origine de la scène de l'Atelier (map de l'Atelier)")
    o.add_argument("--x", type=float, default=0)
    o.add_argument("--y", type=float, default=0)
    r = sous.add_parser("remettre", help="remet les addons d'Adrien coupés par un GMod éclair (si GMod est fermé)")
    r.add_argument("--attendre", action="store_true", help="attendre d'abord la fermeture de GMod")
    a = p.parse_args()
    if a.cmd != "remettre":
        remettre_addons_perso()  # filet : addons restés coupés après un GMod fermé sans surveillance
    {"installer": lambda: installer(), "tester": lambda: tester(a), "poser": lambda: poser(a), "filmer": lambda: filmer(a),
     "remettre": lambda: remettre(a)}[a.cmd]()


if __name__ == "__main__":
    main()
