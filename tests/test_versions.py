"""Cohérence du catalogue : versions égales, skills bien formés, CHANGELOG présent."""
import json
import re
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]


class Catalogue(unittest.TestCase):
    def setUp(self):
        self.marche = json.loads((RACINE / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    def test_versions_egales(self):
        for p in self.marche["plugins"]:
            manifeste = json.loads((RACINE / p["source"] / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(p["name"], manifeste["name"])
            self.assertEqual(p["version"], manifeste["version"], p["name"])

    def test_version_dans_changelog(self):
        log = (RACINE / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## Non publié", log)
        for p in self.marche["plugins"]:
            self.assertIn("[%s %s]" % (p["name"], p["version"]), log, "version absente du CHANGELOG")

    def test_skills(self):
        noms = set()
        for f in RACINE.glob("plugins/*/skills/*/SKILL.md"):
            t = f.read_text(encoding="utf-8")
            m = re.match(r"---\n(.*?)\n---\n", t, re.S)
            self.assertTrue(m, f)
            entete = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
            self.assertEqual(entete.get("name"), f.parent.name, f)
            self.assertTrue(40 <= len(entete.get("description", "")) <= 1024, f)
            self.assertNotIn(entete["name"], noms)
            noms.add(entete["name"])
            self.assertLess(len(t), 6500, "%s : SKILL.md doit tenir sur une page" % f)

    def test_liens_references(self):
        """Chaque references/xxx.md cité dans un SKILL.md existe."""
        for f in RACINE.glob("plugins/*/skills/*/SKILL.md"):
            for ref in re.findall(r"`(?:references|modeles)/([\w.-]+\.md)`", f.read_text(encoding="utf-8")):
                trouve = list(RACINE.glob("plugins/*/skills/*/references/" + ref)) + list(RACINE.glob("plugins/*/skills/*/modeles/" + ref))
                self.assertTrue(trouve, "%s cite %s introuvable" % (f, ref))


if __name__ == "__main__":
    unittest.main()
