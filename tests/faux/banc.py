"""Faux banc pour les tests du serveur MCP : même interface que sites/gmod-build/banc/banc.py."""
import json
import sys
import tempfile
from pathlib import Path

DATA = Path(tempfile.gettempdir()) / "faux_banc_data"


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
    print("ARGS " + json.dumps(sys.argv[1:]))
