"""Faux banc pour les tests du serveur MCP : même interface que sites/gmod-build/banc/banc.py."""
import json
import sys
import tempfile
from pathlib import Path

import os

RACINE = Path(os.environ.get("FAUX_GMOD", Path(tempfile.gettempdir()) / "faux_gmod"))
DATA = RACINE / "data"
ADDON_DST = RACINE / "addons" / "banc_essai"


def gmod_tourne():
    return True


def partie():
    return {"carte": "gm_flatgrass", "mode": "sandbox", "solo": True}


def ecrire_tache(dupe, plan, x, y, *a, **k):
    (DATA / "banc_essai").mkdir(parents=True, exist_ok=True)
    (DATA / "banc_essai" / "tache.txt").write_text(json.dumps({"id": "t1", "dupe": dupe.name}), encoding="utf-8")
    return "t1"


def attendre_fait(fichier, tache_id, delai):
    return {"id": tache_id, "ok": False, "raison": "dupe introuvable"}


if __name__ == "__main__":
    print("entités : 12 créées sur 12")
    if os.environ.get("FAUX_CAPTURES"):
        d = Path(os.environ["FAUX_CAPTURES"])
        d.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        for nom in ("face", "dos"):
            Image.new("RGB", (64, 36), "gray").save(d / (nom + ".jpg"))
        print("captures : 2 dans %s" % d)
        with open(RACINE / "console.log", "a", encoding="utf-8") as f:
            f.write("[banc_essai] tâche\n")
            if os.environ.get("FAUX_ERREUR_LUA"):
                f.write("[banc_essai] addons/banc_essai/lua/autorun/client/zz_x.lua:175: attempt to call global 'f' (a nil value)\n")
    print("ARGS " + json.dumps(sys.argv[1:]))
