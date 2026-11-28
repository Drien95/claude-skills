"""Tests des contrôles gratuits : controle_auto.py (dupe ou scene.json) et controle_livraison.py (addon)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

OUTILS = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "outils"
sys.path.insert(0, str(OUTILS))
import controle_auto  # noqa: E402
import controle_livraison  # noqa: E402

CUBE = "models/hunter/blocks/cube1x1x1.mdl"
BORNES = {CUBE: {"min": [-23.7, -23.7, -23.7], "max": [23.7, 23.7, 23.7]}}


def prop(note, pos, modele=CUBE, ang=(0, 0, 0)):
    return {"kind": "prop", "model": modele, "pos": list(pos), "ang": list(ang), "color": [200, 200, 200],
            "mat": "models/debug/debugwhite", "note": note}


def scene(d, ents, fx=None, tete="tete"):
    f = Path(d) / "scene.json"
    f.write_text(json.dumps({"ents": ents, "fx": fx or [], "head": tete}), encoding="utf-8")
    return f


def encoder(d, ents):
    """Dupe AdvDupe2 réel par l'encodeur du gabarit (outils/dunes/encode.py)."""
    scene(d, ents)
    r = subprocess.run([sys.executable, str(OUTILS / "dunes" / "encode.py"), "essai"], cwd=d, capture_output=True, timeout=60)
    assert r.returncode == 0, r.stderr.decode()
    return Path(d) / "build.txt"


class ControleAuto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = self._tmp.name
        self.liste = Path(self.d) / "autorises.txt"
        self.liste.write_text(CUBE + "\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def ctrl(self, f, **k):
        k.setdefault("autorises", str(self.liste))
        k.setdefault("bornes", BORNES)
        return controle_auto.controler(f, **k)

    def test_dupe_reel_lu_et_propre(self):
        dupe = encoder(self.d, [prop("tete", (0, 0, 23.7)), prop("haut", (0, 0, 71.1)), prop("cote", (47.4, 0, 23.7))])
        erreurs, attentions, res = self.ctrl(dupe)
        self.assertEqual(erreurs, [])
        self.assertEqual(attentions, [])
        self.assertIn("3 posés", res)

    def test_doublon_et_flottant(self):
        ents = [prop("tete", (0, 0, 23.7)), prop("double", (0, 0, 23.7)), prop("ciel", (0, 0, 400))]
        erreurs, attentions, _ = self.ctrl(encoder(self.d, ents))
        self.assertTrue(any("double" in e for e in erreurs), erreurs)
        self.assertTrue(any("flotter" in a and "cube1x1x1" in a for a in attentions), attentions)

    def test_props_trop_droits(self):
        droit = [prop("p%d" % i, (i * 60, 0, 23.7)) for i in range(24)]
        _, attentions, _ = self.ctrl(scene(self.d, droit))
        self.assertTrue(any("parfaitement droits" in a for a in attentions), attentions)
        torts = [prop("p%d" % i, (i * 60, 0, 23.7), ang=(0, 3 + i % 5, 0)) for i in range(24)]
        _, attentions, _ = self.ctrl(scene(self.d, torts))
        self.assertFalse(any("parfaitement droits" in a for a in attentions), attentions)

    def test_modeles_refuses(self):
        ents = [prop("a", (0, 0, 23.7)), prop("b", (60, 0, 23.7), modele="models/propper/hueco_mundo_v1/s_40.mdl"),
                prop("c", (120, 0, 23.7), modele="models/propper/hueco_mundo_v1/s_400.mdl")]
        _, attentions, _ = self.ctrl(scene(self.d, ents))
        refus = [a for a in attentions if "refusé" in a]
        self.assertEqual(len(refus), 1, attentions)
        self.assertIn("s_40.mdl", refus[0])
        self.assertNotIn("s_400", refus[0])

    def test_budget_boite_et_liste(self):
        ents = [prop("tete", (0, 0, 23.7))] + [prop("p%d" % i, (60 * i, 0, 23.7)) for i in range(1, 6)]
        ents.append(prop("intrus", (0, 60, 23.7), modele="models/props_c17/oildrum001.mdl"))
        erreurs, _, _ = self.ctrl(scene(self.d, ents), budget=5, boite=[200, 500, 500])
        texte = " | ".join(erreurs)
        self.assertIn("plafond 5", texte)
        self.assertIn("hors de la boîte", texte)
        self.assertIn("hors liste autorisée", texte)

    def test_classes_bloquees_et_playermodel(self):
        ents = [prop("tete", (0, 0, 23.7)), prop("pnj", (60, 0, 0), modele="models/player/kleiner.mdl")]
        fx = [{"kind": "light", "pos": [0, 0, 80], "col": [255, 0, 0], "bright": 2, "size": 200}]
        erreurs, _, _ = self.ctrl(scene(self.d, ents, fx))
        texte = " | ".join(erreurs)
        self.assertIn("gmod_light", texte)
        self.assertIn("playermodel", texte)

    def test_cli_code_de_sortie(self):
        f = scene(self.d, [prop("tete", (0, 0, 23.7)), prop("double", (0, 0, 23.7))])
        r = subprocess.run([sys.executable, str(OUTILS / "controle_auto.py"), str(f), "--autorises", str(self.liste)],
                           capture_output=True, timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ERREUR", r.stdout.decode("utf-8"))
        self.assertLessEqual(len(r.stdout.decode("utf-8").splitlines()), 12)

    def test_fichier_illisible(self):
        f = Path(self.d) / "faux.txt"
        f.write_bytes(b"pas un dupe")
        r = subprocess.run([sys.executable, str(OUTILS / "controle_auto.py"), str(f)], capture_output=True, timeout=30)
        self.assertEqual(r.returncode, 2)


class ControleLivraison(unittest.TestCase):
    def addon(self, d, lua, commandes_md=True, readme=True):
        d = Path(d)
        (d / "lua" / "autorun").mkdir(parents=True)
        (d / "lua" / "autorun" / "a3_init.lua").write_text(lua, encoding="utf-8")
        if commandes_md:
            (d / "COMMANDES.md").write_text("| a3_lancer | | MJ | lance |\n| a3_tout_effacer | | MJ | efface |\n| a3_diag | | tous | état |\n",
                                            encoding="utf-8")
        if readme:
            (d / "README.md").write_text("a3_lancer a3_tout_effacer a3_diag ; bind F6 a3_lancer", encoding="utf-8")
        return d

    BON = ('local G = include("a3/sh_gravure.lua")\n'
           'concommand.Add("a3_lancer", function(ply) ply:PrintMessage(HUD_PRINTCONSOLE, "ok") end)\n'
           'concommand.Add("a3_tout_effacer", function() print("effacé") end)\n'
           'concommand.Add("a3_diag", function() MsgC(Color(255,255,255), "rien") end)\n')

    def test_addon_conforme(self):
        with tempfile.TemporaryDirectory() as d:
            erreurs, attentions, _ = controle_livraison.controler(self.addon(d, self.BON))
            self.assertEqual(erreurs, [])
            self.assertEqual(attentions, [])

    def test_exigences_d_adrien(self):
        lua = ('concommand.Add("a3_lancer", function(ply) chat.AddText("go") end)\n'
               'concommand.Add("a3_nouvelle", function(ply) ply:PrintMessage(HUD_PRINTTALK, "x") end)\n'
               'hook.Add("Think", "x", function() if input.IsKeyDown(KEY_F) then end end)\n')
        with tempfile.TemporaryDirectory() as d:
            erreurs, _, _ = controle_livraison.controler(self.addon(d, lua))
            texte = " | ".join(erreurs)
            for attendu in ("tout_effacer", "notification à l'écran", "Touche en dur", "gravure", "a3_nouvelle"):
                self.assertIn(attendu, texte)

    def test_sans_commandes_md(self):
        with tempfile.TemporaryDirectory() as d:
            erreurs, _, _ = controle_livraison.controler(self.addon(d, self.BON, commandes_md=False))
            self.assertTrue(any("COMMANDES.md absent" in e for e in erreurs))

    def test_dispense_de_gravure(self):
        with tempfile.TemporaryDirectory() as d:
            lua = self.BON.replace('local G = include("a3/sh_gravure.lua")\n', "")
            self.assertTrue(controle_livraison.controler(self.addon(d, lua))[0])
            self.assertEqual(controle_livraison.controler(Path(d), gravure=False)[0], [])


if __name__ == "__main__":
    unittest.main()
