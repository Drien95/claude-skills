"""Tests du hook de rappel de passation (plugin optimus) : python -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "plugins" / "optimus" / "hooks" / "rappel_passation.py"


def outil(nom, entree):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": nom, "input": entree}]}})


class RappelPassation(unittest.TestCase):
    def setUp(self):
        self.session = "test-" + uuid.uuid4().hex
        self.dossier = tempfile.mkdtemp()

    def tearDown(self):
        m = os.path.join(tempfile.gettempdir(), "optimus_rappel_" + self.session)
        if os.path.exists(m):
            os.remove(m)

    def lancer(self, lignes, actif=False):
        chemin = os.path.join(self.dossier, "t.jsonl")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
        ev = {"session_id": self.session, "transcript_path": chemin, "stop_hook_active": actif}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(ev).encode(), capture_output=True, timeout=20)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        s = r.stdout.decode().strip()
        return json.loads(s) if s else None

    def test_rien_livre_rien_bloque(self):
        self.assertIsNone(self.lancer([outil("Bash", {"command": "git status"})]))

    def test_commit_sans_passation_bloque_une_fois(self):
        lignes = [outil("Bash", {"command": "git commit -m 'feat: x'"})]
        r = self.lancer(lignes)
        self.assertEqual(r["decision"], "block")
        self.assertIn("/optimus:passation", r["reason"])
        self.assertIsNone(self.lancer(lignes))          # deuxième tour : plus de rappel

    def test_pr_sans_passation_bloque(self):
        self.assertEqual(self.lancer([outil("PowerShell", {"command": "gh pr create --title x"})])["decision"], "block")

    def test_passation_deja_faite(self):
        lignes = [outil("Bash", {"command": "git commit -m x"}), outil("Skill", {"skill": "optimus:passation", "args": "a2"})]
        self.assertIsNone(self.lancer(lignes))

    def test_script_du_coffre_compte_comme_passation(self):
        lignes = [outil("Bash", {"command": "git commit -m x"}), outil("Bash", {"command": "python scripts/optimus.py passation a2"})]
        self.assertIsNone(self.lancer(lignes))

    def test_pas_de_boucle(self):
        self.assertIsNone(self.lancer([outil("Bash", {"command": "git commit -m x"})], actif=True))

    def test_transcript_absent(self):
        ev = {"session_id": self.session, "transcript_path": os.path.join(self.dossier, "absent.jsonl")}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(ev).encode(), capture_output=True, timeout=20)
        self.assertEqual((r.returncode, r.stdout), (0, b""))

    def test_texte_non_outil_ignore(self):
        texte = json.dumps({"type": "user", "message": {"content": "fais un git commit stp"}})
        self.assertIsNone(self.lancer([texte]))


if __name__ == "__main__":
    unittest.main()
