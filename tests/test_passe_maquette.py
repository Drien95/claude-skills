"""Tests des corrections de fausses alertes (28/11/2026) : accent attendu, silence voulu, filtre du résumé de passe."""
import sys
import unittest
from pathlib import Path

OUTILS = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils"
sys.path.insert(0, str(OUTILS))
import controle_sequence  # noqa: E402
import mesure_da  # noqa: E402
import passe_maquette  # noqa: E402


class FaussesAlertes(unittest.TestCase):
    def test_accent_attendu(self):
        self.assertFalse(mesure_da.accent_attendu("gris_arrivee"))
        self.assertFalse(mesure_da.accent_attendu("rendu_canyon", ["canyon"]))
        self.assertTrue(mesure_da.accent_attendu("rendu_arrivee", ["canyon"]))

    def test_silence_voulu_avant_le_sommet(self):
        seq = {"sommet": 20, "courbe": [[0, 1], [10, 3], [15, 0], [17, 0], [20, 5]],
               "evenements": [{"t": 15, "type": "silence", "nom": "silence", "debut": 15, "fin": 17}]}
        self.assertNotIn("redescend", " ".join(controle_sequence.controler(seq)[1]))
        seq["evenements"] = []
        self.assertIn("redescend", " ".join(controle_sequence.controler(seq)[1]))

    def test_resume_garde_l_accent_au_sommet_seulement(self):
        l = "rendu_mj : lum 0.1 | l'accent est absent de la vue"
        self.assertEqual(passe_maquette.filtrer(l, False), "")
        self.assertEqual(passe_maquette.filtrer(l, True), l)
        self.assertEqual(passe_maquette.filtrer(l + " ; image très claire", False), "rendu_mj : lum 0.1 | image très claire")


if __name__ == "__main__":
    unittest.main()
