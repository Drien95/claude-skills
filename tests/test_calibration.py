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


@unittest.skipIf(Image is None, "Pillow absent")
class Ressemblance(unittest.TestCase):
    def test_meme_ambiance_et_ambiance_opposee(self):
        import ressemblance
        sombre = Image.new("RGB", (160, 90), (20, 30, 50))
        sombre2 = Image.new("RGB", (160, 90), (22, 32, 54))
        clair = Image.new("RGB", (160, 90), (240, 200, 90))
        for im in (sombre, sombre2, clair):
            for x in range(60, 100):
                for y in range(30, 60):
                    im.putpixel((x, y), (200, 200, 220) if im is not clair else (20, 20, 20))
        proche = ressemblance.comparer(sombre, sombre2)
        loin = ressemblance.comparer(sombre, clair)
        self.assertEqual(proche["alertes"], [])
        self.assertGreater(proche["couleurs"], loin["couleurs"])
        self.assertTrue(any("couleurs éloignées" in a for a in loin["alertes"]), loin)
        self.assertTrue(any("tonalité" in a for a in loin["alertes"]), loin)


if __name__ == "__main__":
    unittest.main()
