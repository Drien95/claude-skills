"""Tests de controle_fiche.py et controle_sequence.py (contrôles gratuits de DA)."""
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
OUTILS = RACINE / "plugins" / "builds-evo" / "outils"
sys.path.insert(0, str(OUTILS))
import controle_fiche as cf  # noqa: E402
import controle_sequence as cs  # noqa: E402

MODELE = (RACINE / "plugins" / "builds-evo" / "skills" / "build-evo" / "modeles" / "fiche-da.md").read_text(encoding="utf-8")


class Fiche(unittest.TestCase):
    def test_modele_vide_refuse(self):
        erreurs, _ = cf.controler(MODELE)
        self.assertGreaterEqual(len(erreurs), 10)

    def test_fiche_remplie_passe(self):
        t = MODELE
        for etiquette, valeur in [
            ("Phrase-titre", "Le deuil qui ne finit pas"), ("3 mots-images", "froid, immobile, sacré"),
            ("Image maîtresse", "ref/maitresse.jpg"), ("Langage de formes", "pointes et os"), ("Ancrage", "la cathédrale"),
            ("Lumière clé", "lune basse bleue"), ("Son", "vent, silence avant le sommet"),
            ("Arrivée des joueurs", "au bout du couloir"), ("Budget global", "300 / 400"), ("Boîte de scène", "40 x 40 x 20")]:
            t = "\n".join(("- **%s** : %s" % (etiquette, valeur)) if l.startswith("- **%s" % etiquette) else l for l in t.splitlines())
        t = t.replace("dominante `#……` ; neutres `#……` `#……` ; accent `#……`", "dominante `#112233` ; neutres `#445566` `#778899` ; accent `#cc3322`")
        t = t.replace("(3 indices : évident, discret, caché) :", "(3 indices : évident, discret, caché) : une lame plantée ; des traces ; un nom gravé")
        erreurs, _ = cf.controler(t)
        self.assertEqual(erreurs, [])


class Sequence(unittest.TestCase):
    BON = {"sommet": 10, "courbe": [[0, 1], [5, 3], [10, 5]],
           "evenements": [{"t": 2, "type": "son", "nom": "grondement"}, {"t": 6, "type": "lumiere", "nom": "baisse"},
                          {"t": 8, "type": "effet", "nom": "boum", "primaire": True, "debut": 7, "pic": 10, "fin": 13}],
           "ponctuels": {"goutte": [3, 14, 30]}}

    def test_bonne_sequence(self):
        e, a = cs.controler(self.BON)
        self.assertEqual((e, a), ([], []))

    def test_pas_de_silence(self):
        s = dict(self.BON, evenements=self.BON["evenements"] + [{"t": 9.5, "type": "son", "nom": "x"}])
        e, _ = cs.controler(s)
        self.assertTrue(any("silence" in x for x in e))

    def test_deux_primaires_simultanes(self):
        s = dict(self.BON, evenements=self.BON["evenements"] + [{"t": 8, "type": "effet", "nom": "autre", "primaire": True, "debut": 6, "pic": 10.4, "fin": 12}])
        e, _ = cs.controler(s)
        self.assertTrue(any("au même instant" in x for x in e))

    def test_ponctuels_et_courbe(self):
        s = dict(self.BON, ponctuels={"goutte": [0, 3]}, courbe=[[0, 3], [5, 1], [10, 5]])
        _, a = cs.controler(s)
        self.assertTrue(any("ponctuel" in x for x in a))
        self.assertTrue(any("redescend" in x for x in a))


class Mcp(unittest.TestCase):
    def test_outils_par_mcp(self):
        import json
        import subprocess
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "s.json").write_text(json.dumps(Sequence.BON), encoding="utf-8")
        (d / "f.md").write_text(MODELE, encoding="utf-8")
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "sequence_controler", "arguments": {"sequence": str(d / "s.json")}}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "da_fiche", "arguments": {"fiche": str(d / "f.md")}}}]
        r = subprocess.run([sys.executable, str(RACINE / "plugins" / "builds-evo" / "mcp" / "banc_mcp.py")],
                           input=("\n".join(json.dumps(m) for m in msgs) + "\n").encode(), capture_output=True, timeout=60)
        rep = [json.loads(l)["result"]["content"][0]["text"] for l in r.stdout.decode("utf-8").splitlines()]
        self.assertIn("conforme", rep[0])
        self.assertIn("fiche incomplète", rep[1])


if __name__ == "__main__":
    unittest.main()
