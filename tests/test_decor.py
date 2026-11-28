"""Tests du générateur de décor par grappes (outils/decor/decor.py)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DECOR = RACINE / "plugins" / "builds-evo" / "outils" / "decor" / "decor.py"
sys.path.insert(0, str(DECOR.parent))
import decor  # noqa: E402

PAR = {"nom": "t", "graine": 3, "variantes": 2, "zone": {"cx": 0, "cy": 0, "rayon": 2000}, "z": 0,
       "chemin": [[-2000, 0], [2000, 0]], "largeur_chemin": 200, "n_grappes": 15, "ecart_grappes": 250, "budget": 40,
       "vocabulaire": [{"modele": "models/a.mdl", "rayon": 90, "demi_hauteur": 40}, {"modele": "models/b.mdl", "rayon": 50, "demi_hauteur": 25},
                       {"modele": "models/c.mdl", "rayon": 25, "demi_hauteur": 12}],
       "tete": {"modele": "models/a.mdl", "demi_hauteur": 40}}


class Decor(unittest.TestCase):
    def test_graine_reproductible(self):
        self.assertEqual(decor.generer(PAR, 5), decor.generer(PAR, 5))
        self.assertNotEqual(decor.generer(PAR, 5), decor.generer(PAR, 6))

    def test_budget_limite_dure_et_tete(self):
        s = decor.generer(dict(PAR, budget=10), 1)
        self.assertEqual(len(s["ents"]), 10)
        self.assertEqual(s["ents"][0]["note"], "tete")

    def test_chemin_libre_et_inclinaison(self):
        s = decor.generer(PAR, 2)
        for e in s["ents"][1:]:
            self.assertGreaterEqual(abs(e["pos"][1]), 200 - 1)
            self.assertTrue(2 <= abs(e["ang"][0]) <= 8 and 2 <= abs(e["ang"][2]) <= 8)

    def test_cli(self):
        d = Path(tempfile.mkdtemp())
        (d / "p.json").write_text(json.dumps(PAR), encoding="utf-8")
        r = subprocess.run([sys.executable, str(DECOR), "p.json"], cwd=d, capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((d / "decor_t_3.json").is_file() and (d / "decor_t_4.json").is_file())

    def test_vocabulaire_trop_court(self):
        with self.assertRaises(ValueError):
            decor.generer(dict(PAR, vocabulaire=PAR["vocabulaire"][:2]), 1)


class Perf(unittest.TestCase):
    def test_alertes(self):
        sys.path.insert(0, str(DECOR.parents[1]))
        import rapport_perf
        _, a = rapport_perf.controler([
            {"version": "v1", "poses": 210, "ms_script": 0.3, "dessins": 120, "fps_moy": 60, "fps_1pct": 50, "dynlights": 2, "quads_max": 3000},
            {"version": "v2", "poses": 420, "ms_script": 3.4, "dessins": 1600, "fps_moy": 60, "fps_1pct": 20, "dynlights": 3, "quads_max": 5000}])
        texte = "\n".join(a)
        for mot in ("420 posés", "lumières dynamiques", "5000 quads", "1 % pire", "coût du script", "dessins par image"):
            self.assertIn(mot, texte)
        _, a = rapport_perf.controler([{"version": "v1", "poses": 100}])
        self.assertEqual(a, [])


if __name__ == "__main__":
    unittest.main()
