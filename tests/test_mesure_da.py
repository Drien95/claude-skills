"""Tests de outils/mesure_da.py (mesure d'une capture contre la fiche DA)."""
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
    return subprocess.run([sys.executable, str(OUTIL), *args], capture_output=True, text=True, encoding="utf-8", timeout=60)


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

    def test_fichier_absent(self):
        self.assertEqual(lancer(str(self.d / "rien.png")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
