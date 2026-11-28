"""Tests de calibration.py : journal des mesures et des notes, analyse des corrélations."""
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

OUTILS = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils"
sys.path.insert(0, str(OUTILS))
import calibration  # noqa: E402


class Maths(unittest.TestCase):
    def test_correlation(self):
        self.assertAlmostEqual(calibration.correlation([1, 2, 3, 4], [2, 4, 6, 8]), 1.0)
        self.assertAlmostEqual(calibration.correlation([1, 2, 3, 4], [8, 6, 4, 2]), -1.0)
        self.assertEqual(calibration.correlation([1, 1, 1], [1, 2, 3]), 0.0)


@unittest.skipIf(Image is None, "Pillow absent")
class Journal(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.j = self.d / "cal.jsonl"

    def planche(self, nom, fond, tache):
        dossier = self.d / nom
        dossier.mkdir()
        im = Image.new("RGB", (160, 120), fond)
        for x in range(60, 100):
            for y in range(40, 80):
                im.putpixel((x, y), tache)
        im.save(dossier / "vue.png")
        return str(dossier)

    def test_pas_assez_de_planches(self):
        calibration.noter(self.planche("a", (20, 25, 30), (200, 50, 40)), 8, "v1", journal=self.j)
        self.assertIn("minimum pour analyser", calibration.analyser(self.j))

    def test_analyse_trouve_la_mesure_qui_suit_la_note(self):
        # plus la tache est claire par rapport au fond, plus Adrien note haut : contraste_focal doit ressortir
        for i, t in enumerate([40, 80, 120, 160, 200, 240]):
            calibration.noter(self.planche("p%d" % i, (20, 25, 30), (t, t, t)), 4 + i * 0.8, "v%d" % i, journal=self.j)
        texte = calibration.analyser(self.j)
        self.assertIn("6 planches notées", texte)
        ligne = next(l for l in texte.splitlines() if l.startswith("contraste_focal"))
        self.assertIn("forte", ligne)
        self.assertIn("seuil 7,5", ligne)

    def test_note_hors_bornes(self):
        with self.assertRaises(ValueError):
            calibration.noter(self.planche("z", (1, 1, 1), (9, 9, 9)), 11, journal=self.j)


if __name__ == "__main__":
    unittest.main()
