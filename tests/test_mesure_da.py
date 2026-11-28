"""Tests de outils/mesure_da.py (mesure d'une capture contre la fiche DA)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

OUTIL = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils" / "mesure_da.py"


def lancer(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")  # sortie en UTF-8 aussi sous Windows
    return subprocess.run([sys.executable, str(OUTIL), *args], capture_output=True, text=True, encoding="utf-8", timeout=60, env=env)


@unittest.skipIf(Image is None, "Pillow absent")
class MesureDA(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def image(self, nom, fond, tache=None):
        im = Image.new("RGB", (160, 120), fond)
        if tache:
            for x in range(60, 100):
                for y in range(40, 80):
                    im.putpixel((x, y), tache)
        chemin = self.d / nom
        im.save(chemin)
        return str(chemin)

    def test_image_noire(self):
        r = lancer(self.image("n.png", (2, 2, 2)))
        self.assertEqual(r.returncode, 0)
        self.assertIn("presque noire", r.stdout)

    def test_point_focal_et_accent(self):
        c = self.image("f.png", (20, 25, 30), (200, 50, 40))
        r = lancer(c, "--palette", "#14191e", "--accent", "#c83228")
        self.assertNotIn("pas de point focal", r.stdout)
        self.assertNotIn("accent est absent", r.stdout)

    def test_fiche_lue(self):
        f = self.d / "fiche.md"
        f.write_text("- **Palette en hex** : dominante `#14191e` ; neutres `#202830` ; accent `#c83228`\n", encoding="utf-8")
        c = self.image("g.png", (20, 25, 30), (200, 50, 40))
        r = lancer(c, "--fiche", str(f), "--json")
        self.assertIn("part_accent", r.stdout)
        self.assertIn("ecart_palette", r.stdout)

    def test_dossier_ne_garde_que_les_alertes(self):
        self.image("a_vue1.png", (2, 2, 2))
        self.image("b_vue2.png", (20, 25, 30), (200, 50, 40))
        (self.d / "planche_1.jpg").write_bytes(b"pas une image")
        r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import mesure_da; print(mesure_da.mesurer_dossier(%r))" % (str(OUTIL.parent), str(self.d))], capture_output=True, text=True, encoding="utf-8", timeout=60,
                           env=dict(__import__("os").environ, PYTHONIOENCODING="utf-8"))
        self.assertIn("2 vue(s), 1 avec alerte", r.stdout)
        self.assertIn("a_vue1", r.stdout)
        self.assertNotIn("b_vue2", r.stdout)

    def test_mcp_da_mesurer(self):
        import json
        self.image("v1.png", (2, 2, 2))
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "da_mesurer", "arguments": {"dossier": str(self.d)}}}
        serveur = OUTIL.parents[1] / "mcp" / "banc_mcp.py"
        r = subprocess.run([sys.executable, str(serveur)], input=(json.dumps(msg) + "\n").encode(), capture_output=True, timeout=60)
        texte = json.loads(r.stdout.decode().splitlines()[0])["result"]["content"][0]["text"]
        self.assertIn("1 avec alerte", texte)

    def test_bruit_et_detail_reparti(self):
        import random
        random.seed(1)
        im = Image.new("RGB", (160, 120))
        im.putdata([(v, v, v) for v in (random.randint(60, 200) for _ in range(160 * 120))])
        chemin = self.d / "bruit.png"
        im.save(chemin)
        r = lancer(str(chemin))
        self.assertIn("image chargée", r.stdout)
        self.assertIn("détail réparti", r.stdout)

    def test_sortie_non_eclairee(self):
        c = self.image("s.png", (20, 25, 30), (230, 230, 230))   # tache claire au centre
        r = lancer(c, "--sortie", "0", "0", "0.2", "0.2")          # sortie dans un coin sombre
        self.assertIn("chemin non éclairé", r.stdout)
        r = lancer(c, "--sortie", "0.4", "0.3", "0.6", "0.7")      # sortie sur la tache claire
        self.assertNotIn("chemin non éclairé", r.stdout)

    def test_fichier_absent(self):
        self.assertEqual(lancer(str(self.d / "rien.png")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
