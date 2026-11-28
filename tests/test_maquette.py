"""Tests de faire_maquette.py (maquette three.js générée) ; la capture headless n'est testée que si Playwright et un navigateur sont là."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

OUTILS = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils"
sys.path.insert(0, str(OUTILS))
import faire_maquette  # noqa: E402

CUBE = "models/hunter/blocks/cube1x1x1.mdl"


def scene(d, n=5):
    ents = [{"kind": "prop", "model": CUBE, "pos": [i * 100, 0, 23.7], "ang": [0, i * 20, 0], "color": [90, 95, 110], "mat": "x", "note": "tete" if i == 0 else "p%d" % i}
            for i in range(n)]
    f = Path(d) / "scene.json"
    f.write_text(json.dumps({"ents": ents, "fx": [], "head": "tete"}), encoding="utf-8")
    return f


class Maquette(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_effets_du_script_relatifs_au_repere(self):
        f = scene(self.d)
        d = json.loads(f.read_text(encoding="utf-8"))
        d["ents"][0]["pos"] = [100, 200, 0]
        d["script"] = [{"nom": "colonne", "forme": "cylindre", "pos": [100, 300, 0], "taille": [80, 80, 900], "debut": 10, "fin": 20}]
        f.write_text(json.dumps(d), encoding="utf-8")
        e = faire_maquette.donnees(f)["script"][0]
        self.assertEqual(e["pos"], [0, 0, -100])
        self.assertEqual((e["debut"], e["fin"], e["forme"]), (10, 20, "cylindre"))
        self.assertEqual(faire_maquette.donnees(scene(self.d))["script"], [])

    def test_donnees_et_repere(self):
        d = faire_maquette.donnees(scene(self.d))
        self.assertEqual(len(d["props"]), 5)
        self.assertEqual(len(d["props"][0]["m"]), 16)
        self.assertEqual(len(d["vues"]), 3)                       # caméras par défaut
        m = d["props"][1]["m"]                                    # prop à x = 100 relatif à la tête : translation three (x, y, z) = (100, 0, 0)
        self.assertAlmostEqual(m[3], 100, delta=1)
        self.assertAlmostEqual(m[7], 0, delta=1)
        self.assertAlmostEqual(d["sol"], -23.7, delta=1.5)        # sol sous le cube (pièce de tête posée dessus)

    def test_palette_et_sequence(self):
        f = Path(self.d) / "fiche.md"
        f.write_text("- **Palette en hex** : dominante `#112233` ; neutres `#445566` ; accent `#cc3322`\n", encoding="utf-8")
        s = Path(self.d) / "s.json"
        s.write_text(json.dumps({"sommet": 10, "courbe": [[0, 1], [10, 5]], "evenements": [{"t": 2, "nom": "x"}]}), encoding="utf-8")
        d = faire_maquette.donnees(scene(self.d), str(f), None, str(s))
        self.assertEqual(d["palette"]["dominante"], "#112233")
        self.assertEqual(d["palette"]["accent"], "#cc3322")
        self.assertEqual(d["evenements"][0]["nom"], "x")

    def test_cli_ecrit_le_html(self):
        sortie = Path(self.d) / "m.html"
        r = subprocess.run([sys.executable, str(OUTILS / "faire_maquette.py"), str(scene(self.d)), "--sortie", str(sortie)],
                           capture_output=True, text=True, encoding="utf-8", timeout=60, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stderr)
        t = sortie.read_text(encoding="utf-8")
        self.assertIn("const D = {", t)
        self.assertNotIn("__DONNEES__", t)


if __name__ == "__main__":
    unittest.main()


class CouleurDesProps(unittest.TestCase):
    """« color » du scene.json : [r, g, b] ou "#rrggbb" ; tout autre format refusé (un hex lu comme liste donnait du vert, 28/11/2026)."""

    def test_formats(self):
        self.assertEqual(faire_maquette.rgb("#c9c2b0"), [201, 194, 176])
        self.assertEqual(faire_maquette.rgb([90, 95.4, 110]), [90, 95, 110])
        self.assertIsNone(faire_maquette.rgb(None))
        for mauvais in ("osblanc", "#c9c2", [300, 0, 0], ["a", "b", "c"]):
            with self.assertRaises(ValueError):
                faire_maquette.rgb(mauvais, "p")


class CheminsSansCwd(unittest.TestCase):
    def test_absolu_sans_getcwd(self):
        import capturer_maquette
        from unittest import mock
        racine = Path(tempfile.gettempdir()).resolve()
        with mock.patch("os.getcwd", side_effect=FileNotFoundError), mock.patch.dict(os.environ, {"PWD": str(racine)}):
            self.assertEqual(capturer_maquette.absolu("passe/m.html"), racine / "passe" / "m.html")
        self.assertEqual(capturer_maquette.absolu(racine / "b"), racine / "b")
