"""Tests des hooks du plugin builds-evo : python -m unittest discover -s tests"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo" / "hooks"


def lancer(script, evenement, *args):
    r = subprocess.run([sys.executable, str(HOOKS / script), *args], input=json.dumps(evenement).encode("utf-8"),
                       capture_output=True, timeout=20)
    assert r.returncode == 0, r.stderr.decode()
    sortie = r.stdout.decode().strip()
    return json.loads(sortie)["hookSpecificOutput"] if sortie else None


def banc(commande, outil="Bash"):
    res = lancer("garde_banc.py", {"tool_name": outil, "tool_input": {"command": commande}})
    return res and res["permissionDecision"]


def lua(code, outil="Write", chemin="C:/Project/x/lua/autorun/scene.lua", mode="pre"):
    if outil == "Write":
        entree = {"file_path": chemin, "content": code}
    elif outil == "Edit":
        entree = {"file_path": chemin, "old_string": "a", "new_string": code}
    else:
        entree = {"file_path": chemin, "edits": [{"old_string": "a", "new_string": "local ok = 1"}, {"old_string": "b", "new_string": code}]}
    res = lancer("garde_lua.py", {"tool_name": outil, "tool_input": entree}, mode)
    if not res:
        return None
    return res.get("permissionDecision") or "remarque"


class GardeBanc(unittest.TestCase):
    def test_focus_interdit(self):
        self.assertEqual(banc("python banc.py tester piece.txt --vues v.json --focus"), "deny")
        self.assertEqual(banc("cd C:/Project && python atelier.py jeu trone --cote --eclair --focus"), "deny")

    def test_lancement_sans_eclair(self):
        self.assertEqual(banc("python banc.py tester piece.txt --lancer"), "deny")
        self.assertEqual(banc("python atelier.py jeu lac_noir --cote"), "deny")
        self.assertEqual(banc("py banc.py poser d.txt --cote 0,0,800,600"), "deny")

    def test_lancement_eclair_demande_accord(self):
        self.assertEqual(banc("python banc.py tester piece.txt --lancer --eclair"), "ask")
        self.assertEqual(banc("python banc.py filmer d.txt --lua a.lua --sortie f --lancer --eclair", "PowerShell"), "ask")

    def test_usages_permis(self):
        self.assertIsNone(banc("python atelier.py jeu trone --cote --eclair"))
        self.assertIsNone(banc("python banc.py tester piece.txt --vues v.json"))
        self.assertIsNone(banc("python banc.py poser d.txt --cote 0,0,800,600 --eclair"))
        self.assertIsNone(banc("grep -n focus banc.py"))
        self.assertIsNone(banc("cat sites/gmod-build/banc/banc.py | head"))
        self.assertIsNone(banc("tasklist | findstr gmod"))
        self.assertIsNone(banc("Get-Process gmod"))
        self.assertIsNone(banc("python atelier.py build lac_noir"))

    def test_lancement_direct_interdit(self):
        self.assertEqual(banc('"C:\\SteamLibrary\\steamapps\\common\\GarrysMod\\gmod.exe" -hijack +map gm_flatgrass'), "deny")
        self.assertEqual(banc('Start-Process "C:/SteamLibrary/steamapps/common/GarrysMod/gmod.exe" -ArgumentList "-noworkshop"', "PowerShell"), "deny")
        self.assertEqual(banc("start steam://rungameid/4000"), "deny")
        self.assertEqual(banc('"C:/Program Files (x86)/Steam/steam.exe" -applaunch 4000'), "deny")
        self.assertEqual(banc("cd x; ./hl2.exe -game garrysmod", "mcp__remote-devices__device_bash"), "deny")

    def test_fermer_gmod_demande_accord(self):
        self.assertEqual(banc("taskkill /IM gmod.exe /F"), "ask")
        self.assertEqual(banc("Stop-Process -Name gmod", "PowerShell"), "ask")


class GardeLua(unittest.TestCase):
    def test_touches_en_dur(self):
        self.assertEqual(lua("if input.IsKeyDown(KEY_F3) then go() end"), "deny")
        self.assertEqual(lua('hook.Add("PlayerButtonDown", "lac", function(p, b) end)'), "deny")
        self.assertEqual(lua("local t = KEY_PAD_1", "Edit"), "deny")
        self.assertEqual(lua('hook.Add("PlayerBindPress", "x", f)', "MultiEdit"), "deny")

    def test_commandes_permises(self):
        self.assertIsNone(lua('concommand.Add("lac_suivante", function() SC.suivante() end)'))
        self.assertIsNone(lua("-- bind F3 lac_suivante (au choix, voir README)\n-- KEY_F3 interdit ici\nlocal x = 1"))

    def test_coordonnees_zone(self):
        self.assertEqual(lua("local O = Vector(-11000, -11500, 14200)"), "deny")
        self.assertEqual(lua("local O = Vector( -15287 , -7291 , 14109.5 )"), "deny")

    def test_coordonnees_relatives(self):
        self.assertIsNone(lua("local p = repere:LocalToWorld(Vector(0, 2100, 40))"))
        self.assertIsNone(lua("local p = Vector(-11000, -11500, 40)"))

    def test_musique(self):
        self.assertEqual(lua('sound.PlayURL("https://x/y.mp3", "", f)'), "deny")
        self.assertEqual(lua('surface.PlaySound("music/hl2_song1.mp3")'), "deny")
        self.assertEqual(lua('CreateSound(e, "lac/ost_final.wav")'), "deny")
        self.assertEqual(lua("local s = 'sound/lac_noir/theme_bgm.ogg'"), "deny")

    def test_sons_permis(self):
        for son in ("ambient/wind/wind1.wav", "lac_noir/cloche.wav", "ghost/lost_soul.wav", "ambient/atmosphere/cave_hit1.wav"):
            self.assertIsNone(lua('CreateSound(e, "%s")' % son), son)

    def test_autres_fichiers_ignores(self):
        self.assertIsNone(lua("input.IsKeyDown(KEY_F3)", chemin="C:/notes/README.md"))
        self.assertIsNone(lua("KEY_F3", chemin="C:/x/build.py"))

    def test_avertissement_post(self):
        self.assertEqual(lua("local loin = Vector(0, 14000, 300)", mode="post"), "remarque")
        self.assertIsNone(lua("local pres = Vector(0, 1400, 300)", mode="post"))


if __name__ == "__main__":
    unittest.main()
