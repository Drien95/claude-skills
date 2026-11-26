"""Tests de la ligne d'état."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "statusline" / "ligne_etat.py"


def ligne(entree):
    r = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(entree).encode("utf-8"), capture_output=True, timeout=20)
    assert r.returncode == 0, r.stderr.decode()
    return r.stdout.decode("utf-8")


class LigneEtat(unittest.TestCase):
    def test_piece_en_cours(self):
        with tempfile.TemporaryDirectory() as d:
            etat = Path(d, ".claude", "builds-evo")
            etat.mkdir(parents=True)
            (etat / "piece.json").write_text(json.dumps({"scene": "Lac noir", "piece": "Cathédrale", "version": 10, "budget": 90,
                                                        "poses_piece": 74, "poses_scene": 218, "planche": 2, "note": 7.0}), encoding="utf-8")
            sous = Path(d, "sites", "lac-noir")
            sous.mkdir(parents=True)
            texte = ligne({"workspace": {"current_dir": str(sous)}, "model": {"display_name": "Opus"},
                           "context_window": {"used_percentage": 34.4}})
            self.assertEqual(texte, "Lac noir › Cathédrale v10 · 218/400 posés · pièce 74/90 · planche 2/3 · note 7 ↓ · Opus · contexte 34 %")

    def test_passes_indice_et_relais(self):
        with tempfile.TemporaryDirectory() as d:
            etat = Path(d, ".claude", "builds-evo")
            etat.mkdir(parents=True)
            (etat / "piece.json").write_text(json.dumps({"scene": "A3", "piece": "Arche", "plafond_passes": 5}), encoding="utf-8")
            (etat / "compteurs.json").write_text(json.dumps({"passes_depuis_point": 5, "passes_total": 7}), encoding="utf-8")
            (etat / "conso.json").write_text(json.dumps({"scenes": {"A3": {"Arche": {"sonnet": [0, 0, 0, 1000000]}}}}),
                                             encoding="utf-8")
            texte = ligne({"cwd": d, "context_window": {"used_percentage": 64}})
            self.assertEqual(texte, "A3 › Arche · passes 5/5 ⚠ point · indice 15 · contexte 64 % → /relais")

    def test_sans_piece(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ligne({"cwd": d, "model": {"display_name": "Opus"}}), "Opus")

    def test_entree_vide(self):
        self.assertEqual(ligne({}), "")


if __name__ == "__main__":
    unittest.main()
