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


def dialogue(*messages, env_plus=None):
    entree = "\n".join(json.dumps(m) for m in messages) + "\n"
    # OPTIMUS_DIR absent : les tests n'écrivent jamais dans le vrai coffre d'Adrien
    env = dict(os.environ, BANC_PY=str(FAUX), OPTIMUS_DIR=str(RACINE / "tests" / "faux" / "pas-de-coffre"),
               **(env_plus or {}))
    r = subprocess.run([sys.executable, str(SERVEUR)], input=entree.encode("utf-8"), capture_output=True, env=env, timeout=60)
    return [json.loads(l) for l in r.stdout.decode("utf-8").splitlines() if l.strip()]


def appel(nom, args=None, env_plus=None):
    rep = dialogue({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": nom, "arguments": args or {}}},
                   env_plus=env_plus)[0]
    return rep["result"]["content"][0]["text"], rep["result"]["isError"]


class Protocole(unittest.TestCase):
    def test_initialisation_et_outils(self):
        reps = dialogue({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                        {"jsonrpc": "2.0", "method": "notifications/initialized"},
                        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(reps[0]["result"]["serverInfo"]["name"], "banc")
        noms = {t["name"] for t in reps[1]["result"]["tools"]}
        self.assertEqual(noms, {"banc_etat", "banc_tester", "banc_nettoyer", "banc_planche", "banc_montrer", "banc_passe", "da_mesurer", "da_fiche", "sequence_controler"})


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
        texte, erreur = appel("banc_tester", {"dupe": "piece.txt", "vues": "v.json", "y": 500})
        sys.path.insert(0, str(SERVEUR.parent))
        import banc_mcp
        if banc_mcp.gmod_ouvert():
            self.skipTest("GMod est ouvert sur ce PC : le refus « GMod fermé » ne peut pas être vérifié")
        if os.name == "nt":
            # Sous Windows le serveur vérifie d'abord que GMod tourne : sans lui, il refuse au lieu de lancer.
            self.assertTrue(erreur)
            self.assertIn("GMod est fermé", texte)
            return
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


class ControleAvantCollage(unittest.TestCase):
    def test_dupe_en_erreur_refuse_sans_coller(self):
        cube = "models/hunter/blocks/cube1x1x1.mdl"
        ents = [{"kind": "prop", "model": cube, "pos": [0, 0, 23.7], "ang": [0, 0, 0], "color": [9, 9, 9],
                 "mat": "", "note": n} for n in ("tete", "double")]
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "scene.json").write_text(json.dumps({"ents": ents, "fx": [], "head": "tete"}), encoding="utf-8")
            subprocess.run([sys.executable, str(RACINE / "plugins" / "builds-evo" / "outils" / "dunes" / "encode.py"), "x"],
                           cwd=d, check=True, capture_output=True, timeout=60)
            texte, erreur = appel("banc_passe", {"dupe": str(Path(d) / "build.txt"), "montrer": False},
                                  {"FAUX_GMOD": str(Path(d) / "gmod"), "FAUX_CAPTURES": str(Path(d) / "captures")})
            self.assertTrue(erreur)
            self.assertIn("contrôle auto", texte)
            self.assertIn("double", texte)
            self.assertFalse((Path(d) / "captures").exists(), "rien ne doit être collé")


@unittest.skipUnless(__import__("shutil").which("luajit"), "LuaJIT absent")
class Passe(unittest.TestCase):
    """banc_passe avec le faux banc : faux dossier GMod, captures et console simulées."""

    def preparer(self, d, erreur=False):
        d = Path(d)
        gmod = d / "gmod"
        client = gmod / "addons" / "banc_essai" / "lua" / "autorun" / "client"
        client.mkdir(parents=True)
        (client / "zz_x.lua").write_text("-- ancienne version\n", encoding="utf-8")
        (d / "x.lua").write_text("local a = 1\nprint(a)\n", encoding="utf-8")
        env = {"FAUX_GMOD": str(gmod), "FAUX_CAPTURES": str(d / "captures"), "BANC_SOURCES": str(d)}
        if erreur:
            env["FAUX_ERREUR_LUA"] = "1"
        args = {"dupe": "piece.txt", "scripts": [{"source": str(d / "x.lua"), "nom": "zz_x.lua"}],
                "attente_rechargement": 0, "montrer": False}
        return args, env, client

    def test_passe_complete(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow absent")
        with tempfile.TemporaryDirectory() as d:
            args, env, client = self.preparer(d)
            texte, erreur = appel("banc_passe", args, env)
            self.assertFalse(erreur, texte)
            self.assertIn("aucune erreur Lua", texte)
            self.assertIn("planche_1.jpg", texte)
            self.assertEqual((client / "zz_x.lua").read_text(encoding="utf-8"), "local a = 1\nprint(a)\n")

    def test_erreur_lua_refuse_la_planche(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow absent")
        with tempfile.TemporaryDirectory() as d:
            args, env, _ = self.preparer(d, erreur=True)
            texte, erreur = appel("banc_passe", args, env)
            self.assertTrue(erreur)
            self.assertIn("attempt to call", texte)
            self.assertFalse((Path(d) / "captures" / "planche_1.jpg").exists())

    def test_source_hors_racine_refusee(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as ailleurs:
            args, env, _ = self.preparer(d)
            autre = Path(ailleurs) / "x.lua"
            autre.write_text("print(1)\n", encoding="utf-8")
            args["scripts"][0]["source"] = str(autre)
            texte, erreur = appel("banc_passe", args, env)
            self.assertTrue(erreur)
            self.assertIn("hors de", texte)

    def test_touche_en_dur_refusee(self):
        with tempfile.TemporaryDirectory() as d:
            args, env, _ = self.preparer(d)
            Path(args["scripts"][0]["source"]).write_text("if input.IsKeyDown(KEY_F3) then end\n", encoding="utf-8")
            texte, erreur = appel("banc_passe", args, env)
            self.assertTrue(erreur)
            self.assertIn("refusé", texte)

    def test_nouveau_script_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            args, env, client = self.preparer(d)
            (client / "zz_x.lua").unlink()
            texte, erreur = appel("banc_passe", args, env)
            self.assertTrue(erreur)
            self.assertIn("bascule", texte)


class CopieDuBanc(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SERVEUR.parent))
        import banc_mcp
        self.m = banc_mcp
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_copie_versionnee_livree(self):
        self.assertTrue(self.m.COPIE_BANC.is_file())
        self.assertIn("def ", self.m.COPIE_BANC.read_text(encoding="utf-8"))

    def test_identique_silencieux_meme_en_fins_de_ligne_windows(self):
        (self.d / "a.py").write_bytes(b"x = 1\r\ny = 2\r\n")
        (self.d / "b.py").write_bytes(b"x = 1\ny = 2\n")
        self.assertIsNone(self.m.ecart_copie(self.d / "a.py", self.d / "b.py"))

    def test_ecart_signale(self):
        (self.d / "a.py").write_text("x = 1\n", encoding="utf-8")
        (self.d / "b.py").write_text("x = 2\n", encoding="utf-8")
        self.assertIn("PR", self.m.ecart_copie(self.d / "a.py", self.d / "b.py"))

    def test_banc_absent_silencieux(self):
        self.assertIsNone(self.m.ecart_copie(self.d / "absent.py", self.d / "absent2.py"))

    def test_banc_etat_signale_l_ecart_du_faux_banc(self):
        texte, erreur = appel("banc_etat")
        self.assertFalse(erreur, texte)
        self.assertIn("copie versionnée", texte)


if __name__ == "__main__":
    unittest.main()
