"""Tests du générateur de gravure d'usine (outils/gravure.py), sans GMod."""
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
OUTILS = RACINE / "plugins" / "builds-evo" / "outils"
spec = importlib.util.spec_from_file_location("gravure", OUTILS / "gravure.py")
gravure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gravure)


class TestGravure(unittest.TestCase):
    def test_deterministe(self):
        self.assertEqual(gravure.gravure("A2 v15"), gravure.gravure("A2 v15"))

    def test_identifiants_differents(self):
        a, b = gravure.gravure("A2 v15"), gravure.gravure("A2 v16")
        self.assertNotEqual([(m["x"], m["y"]) for m in a], [(m["x"], m["y"]) for m in b])

    def test_marques_ecartees_et_dans_la_zone(self):
        for ident in ("A2 v15", "Lac noir v80", "x", "B3 v1"):
            m = gravure.gravure(ident, zone=90)
            self.assertEqual(len(m), 3)
            for i, p in enumerate(m):
                self.assertLessEqual(abs(p["x"]), 90)
                self.assertLessEqual(abs(p["y"]), 90)
                for q in m[i + 1:]:
                    self.assertGreaterEqual(math.hypot(p["x"] - q["x"], p["y"] - q["y"]), gravure.ECART_MIN)

    def test_lacets_et_couleurs_improbables(self):
        for p in gravure.gravure("A2 v15", n=6):
            self.assertTrue(5 <= p["lacet"] <= 85.5)
            self.assertNotAlmostEqual((p["lacet"] / 5) % 1, 0)
            for c in p["couleur"]:
                self.assertTrue(17 <= c <= 239)
                self.assertNotEqual(c % 5, 0)

    def test_refus(self):
        with self.assertRaises(ValueError):
            gravure.gravure("  ")
        with self.assertRaises(ValueError):
            gravure.gravure("A2", n=0)
        with self.assertRaises(ValueError):
            gravure.gravure("A2", zone=10)

    def test_cli_json_et_lua(self):
        with tempfile.TemporaryDirectory() as d:
            j, l = Path(d) / "m.json", Path(d) / "m.lua"
            r = subprocess.run([sys.executable, str(OUTILS / "gravure.py"), "A2 v15", "--json", str(j), "--lua", str(l)],
                               capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(j.read_text(encoding="utf-8")), gravure.gravure("A2 v15", z=3.5))
            lua = l.read_text(encoding="utf-8")
            self.assertIn("GRAVURE = {", lua)
            self.assertEqual(lua.count("modele ="), 3)


if __name__ == "__main__":
    unittest.main()
