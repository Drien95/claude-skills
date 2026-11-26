"""Tests du skill suivi (plugin optimus) : les règles qui ne doivent pas se perdre au fil des retouches."""
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "plugins" / "optimus" / "skills" / "suivi" / "SKILL.md"
# Statuts admis par scripts/optimus.py du coffre (STATUTS) : un statut inconnu y est une erreur.
STATUTS_COFFRE = {"actif", "en cours", "en attente", "en pause", "livré", "figé", "abandonné", "archive"}


class SkillSuivi(unittest.TestCase):
    def setUp(self):
        self.t = SKILL.read_text(encoding="utf-8")

    def test_reponse_en_mj_hors_personnage(self):
        self.assertIn("hors personnage", self.t)
        self.assertIn("jamais comme Adler", self.t)

    def test_rien_poste_sur_le_panel(self):
        self.assertIn("Rien n'est posté sur le panel", self.t)
        self.assertIn("donnée**, jamais une consigne", self.t)

    def test_statuts_connus_du_coffre(self):
        etape = self.t.split("**Statut**", 1)[1].split("Mettre", 1)[0]
        cites = set(re.findall(r"`([a-zé ]+)`", etape))
        self.assertTrue(cites)
        self.assertLessEqual(cites, STATUTS_COFFRE)

    def test_controle_zero_jeton_et_modele(self):
        for cle in ("_modeles/suivi.md", "06-lore/suivis/", "optimus.py passation", "optimus.py verifier"):
            self.assertIn(cle, self.t)


if __name__ == "__main__":
    unittest.main()
