"""Tests de la note d'état des builds écrite dans le coffre OPTIMUS après chaque planche."""
import json
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "plugins" / "builds-evo" / "mcp"))
import etat_optimus  # noqa: E402

PIECE = {"scene": "A2 Le Sable du Fond", "piece": "Dunes", "version": 5, "budget": 12,
         "poses_piece": 10, "poses_scene": 41, "planche": 2, "note": 6.5}
FAUX_INDEX = "import pathlib\npathlib.Path('INDEX.md').write_text('regenere', encoding='utf-8')\n"


class NoteEtat(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.coffre = self.tmp / "OPTIMUS"
        (self.coffre / "03-builds").mkdir(parents=True)
        (self.coffre / "scripts").mkdir()
        (self.coffre / "scripts" / "optimus.py").write_text(FAUX_INDEX, encoding="utf-8")
        self.piece = self.tmp / "piece.json"
        self.piece.write_text(json.dumps(PIECE), encoding="utf-8")
        os.environ["OPTIMUS_DIR"] = str(self.coffre)
        os.environ["BUILDS_EVO_PIECE"] = str(self.piece)
        self.note = self.coffre / "03-builds" / "etat-builds.md"

    def tearDown(self):
        os.environ.pop("OPTIMUS_DIR", None)
        os.environ.pop("BUILDS_EVO_PIECE", None)

    def test_creation_conforme_au_coffre(self):
        r = etat_optimus.ecrire([r"C:\x\planche_1.jpg"])
        self.assertIn("index du coffre régénéré", r)
        t = self.note.read_text(encoding="utf-8")
        entete = re.match(r"---\n(.*?)\n---\n", t, re.S).group(1)
        for champ in ("description:", "domaine: builds", "type: reference", "statut: actif", "maj: "):
            self.assertIn(champ, entete)
        self.assertTrue(t.split("---\n", 2)[2].lstrip().startswith("> [!resume] Pour le prochain fil"))
        self.assertIn("| Note | 6,5/10 ↓ sous 7,5 |", t)
        self.assertIn("| Posés de la scène | 41/400 |", t)
        self.assertIn("file:///C:/x/planche_1.jpg", t)

    def test_index_seulement_a_la_creation(self):
        etat_optimus.ecrire(["a.jpg"])
        (self.coffre / "INDEX.md").unlink()
        r = etat_optimus.ecrire(["b.jpg"])
        self.assertNotIn("index", r)
        self.assertFalse((self.coffre / "INDEX.md").exists())

    def test_historique_borne_et_taille(self):
        for i in range(25):
            etat_optimus.ecrire([r"C:\Project\Adler_lore\sites\a2\captures\passe_%02d\planche_1.jpg" % i],
                                maintenant=time.localtime(1_800_000_000 + i * 60))
        t = self.note.read_text(encoding="utf-8")
        lignes = [l for l in t.split(etat_optimus.TITRE_HISTO)[1].splitlines() if l.startswith("- ")]
        self.assertEqual(len(lignes), etat_optimus.HISTORIQUE_MAX)
        self.assertIn("passe_24", lignes[0])
        self.assertLess(len(t.encode("utf-8")), 4000)

    def test_description_et_statut_stables(self):
        etat_optimus.ecrire(["a.jpg"])
        avant = self.note.read_text(encoding="utf-8").split("\n")[1:5]
        self.piece.write_text(json.dumps(dict(PIECE, note=8, version=6)), encoding="utf-8")
        etat_optimus.ecrire(["b.jpg"])
        self.assertEqual(self.note.read_text(encoding="utf-8").split("\n")[1:5], avant)

    def test_coffre_absent_ou_piece_illisible(self):
        os.environ["OPTIMUS_DIR"] = str(self.tmp / "nulle-part")
        self.assertIn("coffre OPTIMUS absent", etat_optimus.ecrire(["a.jpg"]))
        os.environ["OPTIMUS_DIR"] = str(self.coffre)
        self.piece.write_text("{pas du json", encoding="utf-8")
        r = etat_optimus.ecrire(["a.jpg"])
        self.assertIn("note d'état écrite", r)
        self.assertIn("pièce inconnue", self.note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
