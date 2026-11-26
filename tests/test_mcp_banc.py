"""Tests du serveur MCP du banc (avec un faux banc)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SERVEUR = RACINE / "plugins" / "builds-evo" / "mcp" / "banc_mcp.py"
FAUX = Path(__file__).resolve().parent / "faux" / "banc.py"


def dialogue(*messages):
    entree = "\n".join(json.dumps(m) for m in messages) + "\n"
    env = dict(os.environ, BANC_PY=str(FAUX))
    r = subprocess.run([sys.executable, str(SERVEUR)], input=entree.encode("utf-8"), capture_output=True, env=env, timeout=60)
    return [json.loads(l) for l in r.stdout.decode("utf-8").splitlines() if l.strip()]


def appel(nom, args=None):
    rep = dialogue({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": nom, "arguments": args or {}}})[0]
    return rep["result"]["content"][0]["text"], rep["result"]["isError"]


class Protocole(unittest.TestCase):
    def test_initialisation_et_outils(self):
        reps = dialogue({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                        {"jsonrpc": "2.0", "method": "notifications/initialized"},
                        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(reps[0]["result"]["serverInfo"]["name"], "banc")
        noms = {t["name"] for t in reps[1]["result"]["tools"]}
        self.assertEqual(noms, {"banc_etat", "banc_tester", "banc_nettoyer", "banc_planche", "banc_montrer"})


class Regles(unittest.TestCase):
    def test_lancer_sans_accord_refuse(self):
        texte, erreur = appel("banc_tester", {"dupe": "piece.txt", "lancer": True})
        self.assertTrue(erreur)
        self.assertIn("accord", texte)

    def test_commande_jamais_focus_toujours_eclair(self):
        texte, erreur = appel("banc_tester", {"dupe": "piece.txt", "lancer": True, "accord_adrien": True})
        self.assertFalse(erreur, texte)
        args = json.loads(texte.split("ARGS ", 1)[1])
        self.assertNotIn("--focus", args)
        for o in ("--lancer", "--eclair", "--garder"):
            self.assertIn(o, args)
        self.assertEqual(args[args.index("--y") + 1], "-8000.0")

    def test_sans_lancer(self):
        texte, _ = appel("banc_tester", {"dupe": "piece.txt", "vues": "v.json", "y": 500})
        args = json.loads(texte.split("ARGS ", 1)[1])
        self.assertNotIn("--lancer", args)
        self.assertNotIn("--eclair", args)
        self.assertIn("--vues", args)

    def test_nettoyer(self):
        texte, erreur = appel("banc_nettoyer")
        self.assertFalse(erreur, texte)
        self.assertIn("nettoyée", texte)


class Planche(unittest.TestCase):
    def test_planche_avant_apres(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow absent")
        with tempfile.TemporaryDirectory() as d:
            avant, apres = Path(d, "v1"), Path(d, "v2")
            avant.mkdir(); apres.mkdir()
            for nom in ("face", "dos", "profil"):
                Image.new("RGB", (64, 36), "red").save(avant / (nom + ".jpg"))
                Image.new("RGB", (64, 36), "blue").save(apres / (nom + ".jpg"))
            texte, erreur = appel("banc_planche", {"dossier": str(apres), "avant": str(avant)})
            self.assertFalse(erreur, texte)
            self.assertTrue((apres / "planche_avant_apres_1.jpg").is_file())
            texte, _ = appel("banc_planche", {"dossier": str(apres)})
            self.assertTrue((apres / "planche_1.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
