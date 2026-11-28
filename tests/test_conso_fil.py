"""Tests de outils/conso_fil.py (socle et croissance d'un fil)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils"))
import conso_fil  # noqa: E402


def ligne(i, ecrit, lu, sortie, modele="claude-sonnet-5-5"):
    return json.dumps({"type": "assistant", "timestamp": "2026-11-28T03:00:%02dZ" % i, "message": {
        "id": "m%d" % i, "model": modele, "usage": {"input_tokens": 2, "cache_creation_input_tokens": ecrit,
                                                    "cache_read_input_tokens": lu, "output_tokens": sortie},
        "content": [{"type": "tool_use", "name": "mcp__x__banc_passe"}]}})


class ConsoFil(unittest.TestCase):
    def test_resume(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "j.jsonl"
            f.write_text("\n".join([ligne(1, 40000, 50000, 300), ligne(2, 1000, 90000, 200), ligne(2, 1, 1, 1)]) + "\n", encoding="utf-8")
            r = conso_fil.resume(conso_fil.lire(str(f)))
        self.assertEqual(r["appels"], 2)   # même id de message compté une fois
        self.assertEqual(r["socle"], 90002)
        self.assertEqual(r["socle_en_cache"], 50000)
        self.assertEqual(r["contexte_fin"], 91002)
        self.assertEqual(r["modeles"], ["sonnet"])

    def test_vide(self):
        self.assertEqual(conso_fil.resume([]), {"appels": 0})


if __name__ == "__main__":
    unittest.main()
