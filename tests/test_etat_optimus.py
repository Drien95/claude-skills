"""Tests du tableau de bord des builds écrit dans le coffre OPTIMUS après chaque planche."""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "plugins" / "builds-evo" / "mcp"))
import etat_optimus  # noqa: E402

PIECE = {"scene": "A2 Le Sable du Fond", "piece": "Dunes", "version": 5, "budget": 12, "pieces_scene": 12,
         "poses_piece": 10, "poses_scene": 41, "planche": 2, "note": 6.5}
FAUX_INDEX = "import pathlib\npathlib.Path('INDEX.md').write_text('regenere', encoding='utf-8')\n"


def taille(t):
    return len(t.encode("utf-8"))


class Tableau(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.coffre = self.tmp / "OPTIMUS"
        (self.coffre / "03-builds").mkdir(parents=True)
        (self.coffre / "scripts").mkdir()
        (self.coffre / "scripts" / "optimus.py").write_text(FAUX_INDEX, encoding="utf-8")
        (self.coffre / ".git" / "info").mkdir(parents=True)
        self.piece = self.tmp / "piece.json"
        self.ecrire_piece(PIECE)
        os.environ["OPTIMUS_DIR"] = str(self.coffre)
        os.environ["BUILDS_EVO_PIECE"] = str(self.piece)
        self.note = self.coffre / "03-builds" / "etat-builds.md"

    def tearDown(self):
        os.environ.pop("OPTIMUS_DIR", None)
        os.environ.pop("BUILDS_EVO_PIECE", None)

    def ecrire_piece(self, d):
        self.piece.write_text(json.dumps(d), encoding="utf-8")

    def lire(self):
        return self.note.read_text(encoding="utf-8")

    def test_creation_conforme_au_coffre(self):
        r = etat_optimus.ecrire([r"C:\x\planche_1.jpg"])
        self.assertIn("index du coffre régénéré", r)
        t = self.lire()
        entete = re.match(r"---\n(.*?)\n---\n", t, re.S).group(1)
        for champ in ("description:", "domaine: builds", "type: reference", "statut: actif", "maj: "):
            self.assertIn(champ, entete)
        self.assertTrue(t.split("---\n", 2)[2].lstrip().startswith("> [!resume] Pour le prochain fil"))
        self.assertNotIn("[[", t)  # aucun lien wiki : le contrôle du coffre ne voit pas de lien cassé

    def test_encadres_couleurs_et_barres(self):
        etat_optimus.ecrire(["a.jpg"])
        t = self.lire()
        self.assertIn("> [!warning]+ Dunes · v5 · note 6,5/10", t)
        self.assertIn("`██████▌░░░` 6,5 / 10", t)
        self.assertIn("> [!abstract]+ A2 Le Sable du Fond", t)
        self.assertIn("0/12 pièces validées", t)
        self.assertIn("41/400", t)
        self.ecrire_piece(dict(PIECE, note=8))
        etat_optimus.ecrire(["b.jpg"])
        self.assertIn("> [!success]+ Dunes · v5 · note 8/10", self.lire())
        self.assertIn("1/12 pièces validées", self.lire())
        self.ecrire_piece(dict(PIECE, piece="Dalle", note=4))
        etat_optimus.ecrire(["c.jpg"])
        t = self.lire()
        self.assertIn("> [!danger]+ Dalle", t)
        self.assertIn("> [!success]- Dunes", t)   # pièce précédente repliée, gardée
        self.ecrire_piece(dict(PIECE, piece="Ciel", note=None))
        etat_optimus.ecrire(["d.jpg"])
        self.assertIn("> [!note]+ Ciel · v5 · note ?/10", self.lire())

    def test_vignette_dans_le_coffre_hors_git(self):
        from PIL import Image
        planche = self.tmp / "planche_1.jpg"
        Image.new("RGB", (1920, 1080), "navy").save(planche)
        etat_optimus.ecrire([str(planche)])
        vignette = self.coffre / "03-builds" / "vignettes" / "a2-le-sable-du-fond--dunes.jpg"
        self.assertTrue(vignette.is_file())
        with Image.open(vignette) as img:
            self.assertEqual(img.size[0], etat_optimus.LARGEUR_VIGNETTE)
        self.assertIn("![planche|480](03-builds/vignettes/a2-le-sable-du-fond--dunes.jpg)", self.lire())
        exclude = (self.coffre / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        etat_optimus.ecrire([str(planche)])
        self.assertEqual(exclude.count("03-builds/vignettes/"), 1)

    def test_index_seulement_a_la_creation(self):
        etat_optimus.ecrire(["a.jpg"])
        (self.coffre / "INDEX.md").unlink()
        self.assertNotIn("index", etat_optimus.ecrire(["b.jpg"]))
        self.assertFalse((self.coffre / "INDEX.md").exists())

    def test_taille_bornee_avec_beaucoup_de_pieces(self):
        long = r"C:\Project\Adler_lore\sites\a2-sable-du-fond\dalle\captures\a2-dalle-v4\passe_%02d\planche_avant_apres_1.jpg"
        for i in range(40):
            self.ecrire_piece(dict(PIECE, scene="Scène %d" % (i // 12), piece="Pièce numéro %d" % i, note=5 + (i % 5)))
            etat_optimus.ecrire([long % i], maintenant=time.localtime(1_800_000_000 + i * 60))
        t = self.lire()
        self.assertLess(taille(t), 4000)
        self.assertIn("Pièce numéro 39", t)
        self.assertTrue(etat_optimus.DONNEES.search(t))

    def test_description_et_statut_stables(self):
        etat_optimus.ecrire(["a.jpg"])
        avant = self.lire().split("\n")[1:5]
        self.ecrire_piece(dict(PIECE, note=8, version=6))
        etat_optimus.ecrire(["b.jpg"])
        self.assertEqual(self.lire().split("\n")[1:5], avant)

    def test_reprend_l_ancienne_note_sans_donnees(self):
        ancien = "---\nx\n---\n\n## Dernières planches\n\n- 26/11/2026 19:36 · vieille ligne\n"
        self.note.write_text(ancien, encoding="utf-8")
        etat_optimus.ecrire(["a.jpg"])
        self.assertIn("vieille ligne", self.lire())

    def test_coffre_absent_ou_piece_illisible(self):
        os.environ["OPTIMUS_DIR"] = str(self.tmp / "nulle-part")
        self.assertIn("coffre OPTIMUS absent", etat_optimus.ecrire(["a.jpg"]))
        os.environ["OPTIMUS_DIR"] = str(self.coffre)
        self.piece.write_text("{pas du json", encoding="utf-8")
        self.assertIn("tableau des builds écrit", etat_optimus.ecrire(["a.jpg"]))
        self.assertIn("pièce inconnue", self.lire())


if __name__ == "__main__":
    unittest.main()
