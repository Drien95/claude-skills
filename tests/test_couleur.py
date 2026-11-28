"""Tests de palette_ref.py et color_script.py."""
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


@unittest.skipIf(Image is None, "Pillow absent")
class Couleur(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def image(self, nom, fond, taches=()):
        im = Image.new("RGB", (120, 80), fond)
        for (x0, y0, x1, y1), c in taches:
            for x in range(x0, x1):
                for y in range(y0, y1):
                    im.putpixel((x, y), c)
        im.save(self.d / nom)
        return str(self.d / nom)

    def test_palette_dominante_neutres_accent(self):
        import palette_ref
        c = self.image("r.png", (30, 60, 90), [((0, 0, 120, 25), (120, 120, 120)), ((50, 30, 62, 42), (230, 120, 20))])
        tot = palette_ref.couleurs([c])
        dom, neutres, accent = palette_ref.choisir(tot)
        self.assertLess(abs(dom[2] - 90), 30)           # dominante bleutée
        self.assertIsNotNone(accent)
        self.assertGreater(accent[0], 180)              # accent orangé, d'une autre famille
        self.assertIn("accent", palette_ref.ligne(dom, neutres, accent))
        self.assertNotIn(accent, neutres)

    def test_ecriture_dans_la_fiche(self):
        import palette_ref
        c = self.image("r.png", (30, 60, 90), [((50, 30, 62, 42), (230, 120, 20))])
        f = self.d / "fiche.md"
        f.write_text("- **Palette en hex** (pour `outils/mesure_da.py`) : dominante `#……` ; neutres `#……` ; accent `#……`\n- **Autre** : x\n", encoding="utf-8")
        self.assertEqual(palette_ref.main([c, "--ecrire", str(f)]), 0)
        t = f.read_text(encoding="utf-8")
        self.assertNotIn("#……", t)
        self.assertIn("- **Autre** : x", t)

    def test_color_script_deux_temps_forts_semblables(self):
        import color_script
        self.image("a_calme.png", (30, 40, 60))
        self.image("b_tension.png", (32, 42, 62))
        self.image("c_sommet.png", (230, 90, 40))
        sortie = self.d / "cs.png"
        self.assertEqual(color_script.main([str(self.d), "--sortie", str(sortie)]), 0)
        self.assertTrue(sortie.is_file())
        noms = ["a_calme", "b_tension", "c_sommet"]
        ims = [Image.open(self.d / (n + ".png")).convert("RGB") for n in noms]
        al = color_script.analyser(noms, [color_script.empreinte(i) for i in ims])
        self.assertTrue(any("a_calme" in a and "b_tension" in a for a in al), al)
        self.assertFalse(any("la plus vive" in a for a in al), al)


if __name__ == "__main__":
    unittest.main()
