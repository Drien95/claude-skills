"""Tests des outils de build (faire_bornes.py, générateur de dunes) sans GMod."""
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
OUTILS = RACINE / "plugins" / "builds-evo" / "outils"


def lancer(args, cwd, env_plus=None):
    env = dict(os.environ, **(env_plus or {}))
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)


def mini_vpk(chemin, fichiers):
    """VPK v1 minimal : chaque .mdl porte ses bornes (hull min/max) à l'offset 104, données dans l'arbre (idx 0x7fff)."""
    # un dossier par fichier dans ce test (chaque entrée ferme son dossier par le \0 final)
    arbre, corps, decal = b"", b"", 0
    for nom, (mn, mx) in fichiers.items():
        dossier, base = nom.rsplit("/", 1)
        base = base[: -len(".mdl")]
        mdl = bytearray(160)
        struct.pack_into("<6f", mdl, 104, *mn, *mx)
        arbre += b"mdl\0" + dossier.encode() + b"\0" + base.encode() + b"\0"
        arbre += struct.pack("<IHHIIH", 0, 0, 0x7FFF, decal, len(mdl), 0xFFFF)
        arbre += b"\0\0"
        corps += bytes(mdl)
        decal += len(mdl)
    arbre += b"\0"
    Path(chemin).write_bytes(struct.pack("<III", 0x55AA1234, 1, len(arbre)) + arbre + corps)


class Bornes(unittest.TestCase):
    def test_vpk_et_geo(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "autorises.txt").write_text("# en-tête\nmodels/hunter/plates/plate1x1.mdl\nmodels/rochers/r1.mdl\nmodels/absent.mdl\n", encoding="utf-8")
            (d / "geo.json").write_text(json.dumps({"models/rochers/r1.mdl": {"pos": [-1, -2, -3, 4, 5, 6], "idx": []}}), encoding="utf-8")
            mini_vpk(d / "jeu_dir.vpk", {"models/hunter/plates/plate1x1.mdl": ((-23.7, -23.7, -1.5), (23.7, 23.7, 1.5))})
            r = lancer([str(OUTILS / "faire_bornes.py"), "--autorises", str(d / "autorises.txt"), "--geo", str(d / "geo.json"),
                        "--vpk", str(d / "jeu_dir.vpk"), "--sortie", str(d / "b.json")], cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            b = json.loads((d / "b.json").read_text(encoding="utf-8"))
            self.assertEqual(b["models/hunter/plates/plate1x1.mdl"]["src"], "vpk")
            self.assertAlmostEqual(b["models/hunter/plates/plate1x1.mdl"]["max"][0], 23.7, places=2)
            self.assertEqual(b["models/rochers/r1.mdl"], {"min": [-1, -2, -3], "max": [4, 5, 6], "src": "geo"})
            self.assertNotIn("models/absent.mdl", b)
            self.assertIn("1 sans bornes", r.stdout)

    def test_sans_vpk(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "autorises.txt").write_text("models/rochers/r1.mdl\n", encoding="utf-8")
            (d / "geo.json").write_text(json.dumps({"models/rochers/r1.mdl": {"pos": [0, 0, 0, 1, 1, 1], "idx": []}}), encoding="utf-8")
            r = lancer([str(OUTILS / "faire_bornes.py"), "--autorises", str(d / "autorises.txt"), "--geo", str(d / "geo.json"),
                        "--vpk", str(d / "absent.vpk"), "--sortie", str(d / "b.json")], cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(list(json.loads((d / "b.json").read_text(encoding="utf-8"))), ["models/rochers/r1.mdl"])


class Dunes(unittest.TestCase):
    def test_exemple_genere_dupe_script_vues(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            params = json.loads((OUTILS / "dunes" / "params_finition.json").read_text(encoding="utf-8"))
            params["nom"] = "essai"
            (d / "p.json").write_text(json.dumps(params), encoding="utf-8")
            # sans GMod : GMOD_DIR vide, la vérification des PHX passe par bornes_modeles.json
            r = lancer([str(OUTILS / "dunes" / "dunes.py"), "p.json"], cwd=d, env_plus={"GMOD_DIR": str(d / "pas_de_gmod")})
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            dupe = (d / "essai.txt").read_bytes()
            self.assertTrue(dupe.startswith(b"AD2F"))
            scene = json.loads((d / "scene.json").read_text(encoding="utf-8"))
            tubes = [e for e in scene["ents"] if e["note"] == "dune"]
            self.assertLessEqual(len(tubes), 12, "budget de la couche 1 en props")
            tete = next(e for e in scene["ents"] if e["note"] == "sol")
            self.assertTrue(all(e["pos"][2] >= tete["pos"][2] - 1e-6 for e in scene["ents"]))
            lua = (d / "essai_dunes_lointaines.lua").read_text(encoding="utf-8")
            self.assertNotIn("--[[DONNEES]]", lua)
            self.assertIn("a2_dunes", lua)
            for mot in ("KEY_", "input.IsKeyDown", "sound.PlayURL"):
                self.assertNotIn(mot, lua)
            vues = json.loads((d / "vues_essai.json").read_text(encoding="utf-8"))
            noms = {v["nom"] for v in vues["vues"]}
            self.assertIn("F_marche_dune", noms)
            self.assertLessEqual(len(vues["vues"]), 6)

    def test_prop_dans_le_cercle_interdit_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            params = json.loads((OUTILS / "dunes" / "params_finition.json").read_text(encoding="utf-8"))
            params["nom"] = "refus"
            params["variantes"][0]["r"] = 600
            (d / "p.json").write_text(json.dumps(params), encoding="utf-8")
            r = lancer([str(OUTILS / "dunes" / "dunes.py"), "p.json"], cwd=d, env_plus={"GMOD_DIR": str(d / "pas_de_gmod")})
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse((d / "refus.txt").exists())


if __name__ == "__main__":
    unittest.main()
