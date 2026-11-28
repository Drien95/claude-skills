"""Tests du hook d'économie budget.py (cahier, vues, plafond de passes, critique, planche, consommation, relais)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE_PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "builds-evo"
HOOK = RACINE_PLUGIN / "hooks" / "budget.py"
PASSE = "mcp__plugin_builds-evo_banc__banc_passe"


def lancer(mode, evenement, cwd=None):
    r = subprocess.run([sys.executable, str(HOOK), mode], input=json.dumps(evenement).encode("utf-8"),
                       capture_output=True, timeout=20, cwd=cwd)
    assert r.returncode == 0, r.stderr.decode()
    sortie = r.stdout.decode("utf-8").strip()
    return json.loads(sortie)["hookSpecificOutput"] if sortie else None


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        self.etat = self.racine / ".claude" / "builds-evo"
        self.etat.mkdir(parents=True)
        self.sous = self.racine / "sites" / "scene"
        self.sous.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def piece(self, **k):
        d = {"scene": "A3", "piece": "Arche", "version": 2, "cahier_valide": "2026-11-27", "maquette_validee": "2026-11-27",
             "fiche_da": "dispense"}
        d.update(k)
        (self.etat / "piece.json").write_text(json.dumps(d), encoding="utf-8")

    def compteurs(self):
        return json.loads((self.etat / "compteurs.json").read_text(encoding="utf-8"))

    def pre(self, outil, entree):
        res = lancer("pre", {"tool_name": outil, "tool_input": entree, "cwd": str(self.sous)})
        return res and res["permissionDecision"], res and res.get("permissionDecisionReason", "")

    def passe_reussie(self):
        lancer("post", {"tool_name": PASSE, "tool_input": {}, "tool_response": [{"type": "text", "text": "planche : x"}],
                        "cwd": str(self.sous)})


class Cahier(Base):
    def test_sans_build_rien_ne_bloque(self):
        (self.etat / "piece.json").unlink(missing_ok=True)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_passe_refusee_sans_cahier(self):
        self.piece(cahier_valide=None)
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("/builds-evo:cahier", raison)
        self.assertEqual(self.pre("mcp__plugin_builds-evo_banc__banc_tester", {"dupe": "a.txt"})[0], "deny")

    def test_passe_permise_avec_cahier(self):
        self.piece()
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)
        self.assertEqual(self.pre("mcp__plugin_builds-evo_banc__banc_planche", {"dossier": "x"})[0], None)


class Maquette(Base):
    def test_passe_refusee_sans_maquette(self):
        self.piece(maquette_validee=None)
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("three.js", raison)
        self.assertEqual(self.pre("mcp__plugin_builds-evo_banc__banc_tester", {"dupe": "a.txt"})[0], "deny")

    def test_planche_libre_sans_maquette(self):
        self.piece(maquette_validee=None)
        self.assertEqual(self.pre("mcp__plugin_builds-evo_banc__banc_planche", {"dossier": "x"})[0], None)

    def test_dispense(self):
        self.piece(maquette_validee="dispense")
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_debut_signale_maquette(self):
        self.piece(maquette_validee=None)
        res = lancer("debut", {"cwd": str(self.sous)})
        self.assertIn("maquette NON validée", res["additionalContext"])


class FicheDA(Base):
    def test_passe_refusee_sans_fiche(self):
        self.piece(fiche_da=None)
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("/builds-evo:da", raison)

    def test_fiche_introuvable_et_incomplete(self):
        self.piece(fiche_da="fiche.md")
        self.assertIn("introuvable", self.pre(PASSE, {"dupe": "a.txt"})[1])
        modele = (RACINE_PLUGIN / "skills" / "build-evo" / "modeles" / "fiche-da.md").read_text(encoding="utf-8")
        (self.racine / "fiche.md").write_text(modele, encoding="utf-8")
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("incomplète", raison)

    def test_dispense_et_planche_libre(self):
        self.piece(fiche_da="dispense")
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)
        self.piece(fiche_da=None)
        self.assertEqual(self.pre("mcp__plugin_builds-evo_banc__banc_planche", {"dossier": "x"})[0], None)

    def test_debut_signale_fiche(self):
        self.piece(fiche_da=None)
        self.assertIn("Fiche DA : NON déclarée", lancer("debut", {"cwd": str(self.sous)})["additionalContext"])


class Focus(Base):
    VOL = [{"type": "text", "text": "garde-focus : GMod a pris le premier plan, rendu à la fenêtre d'avant\nplanche : x"}]

    def passe_avec(self, rep):
        lancer("post", {"tool_name": PASSE, "tool_input": {}, "tool_response": rep, "cwd": str(self.sous)})

    def test_vol_de_focus_bloque_la_passe_suivante(self):
        self.piece()
        self.passe_avec(self.VOL)
        self.assertEqual(self.compteurs()["focus_vols"], 1)
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("premier plan 1 fois", raison)

    def test_message_d_adrien_remet_a_zero(self):
        self.piece()
        self.passe_avec(self.VOL)
        lancer("prompt", {"cwd": str(self.sous)})
        self.assertEqual(self.compteurs()["focus_vols"], 0)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_dispense(self):
        self.piece(focus_ok="dispense")
        self.passe_avec(self.VOL)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_sans_vol_rien_ne_change(self):
        self.piece()
        self.passe_avec([{"type": "text", "text": "planche : x"}])
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)


class ModeleDeSession(Base):
    def test_modele_signale_au_debut(self):
        self.piece()
        res = lancer("debut", {"cwd": str(self.sous), "model": "claude-opus-5-5"})
        self.assertIn("claude-opus-5-5", res["additionalContext"])
        self.assertIn("/model sonnet", res["additionalContext"])
        res = lancer("debut", {"cwd": str(self.sous), "model": "claude-sonnet-5-5"})
        self.assertNotIn("⚠", res["additionalContext"])

    def test_modele_absent(self):
        self.piece()
        res = lancer("debut", {"cwd": str(self.sous)})
        self.assertIn("non fourni", res["additionalContext"])


class Vues(Base):
    def test_trop_de_vues(self):
        self.piece()
        (self.sous / "v.json").write_text(json.dumps({"vues": [{"nom": str(i)} for i in range(14)]}), encoding="utf-8")
        choix, raison = self.pre(PASSE, {"dupe": "a.txt", "vues": "v.json"})
        self.assertEqual(choix, "deny")
        self.assertIn("14 vues", raison)
        self.piece(max_vues=16)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt", "vues": "v.json"})[0], None)


class Plafond(Base):
    def test_plafond_puis_point_d_adrien(self):
        self.piece(plafond_passes=3)
        for _ in range(3):
            self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)
            self.passe_reussie()
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("point", raison)
        lancer("prompt", {"prompt": "1 oui, 2 non", "cwd": str(self.sous)})
        self.assertEqual(self.compteurs()["passes_depuis_point"], 0)
        self.assertEqual(self.compteurs()["passes_total"], 3)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_passe_en_erreur_non_comptee(self):
        self.piece()
        lancer("post", {"tool_name": PASSE, "tool_response": [{"type": "text", "text": "ERREUR : GMod est fermé"}],
                        "cwd": str(self.sous)})
        self.assertFalse((self.etat / "compteurs.json").exists())

    def test_sans_plafond_sur_ordre(self):
        self.piece(plafond_passes=0)
        for _ in range(7):
            self.passe_reussie()
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)


class Critique(Base):
    def test_une_critique_par_planche(self):
        self.piece()
        self.passe_reussie()
        agent = {"subagent_type": "builds-evo:critique-build", "prompt": "planche"}
        self.assertEqual(self.pre("Agent", agent)[0], None)
        self.assertEqual(self.pre("Agent", agent)[0], "deny")
        finale = {"subagent_type": "builds-evo:critique-finale", "prompt": "planche"}
        self.assertEqual(self.pre("Agent", finale)[0], None)
        self.passe_reussie()
        self.assertEqual(self.pre("Task", agent)[0], None)

    def test_autres_agents_libres(self):
        self.piece()
        self.assertEqual(self.pre("Agent", {"subagent_type": "Explore"})[0], None)


class Images(Base):
    def test_lire_la_planche_pas_les_captures(self):
        self.piece()
        cap = self.racine / "captures"
        cap.mkdir()
        (cap / "face.jpg").write_bytes(b"x")
        self.assertEqual(self.pre("Read", {"file_path": str(cap / "face.jpg")})[0], None)
        (cap / "planche_1.jpg").write_bytes(b"x")
        choix, raison = self.pre("Read", {"file_path": str(cap / "face.jpg")})
        self.assertEqual(choix, "deny")
        self.assertIn("zoom", raison)
        self.assertEqual(self.pre("Read", {"file_path": str(cap / "planche_1.jpg")})[0], None)

    def captures_avec_planche(self):
        cap = self.racine / "captures"
        cap.mkdir()
        (cap / "face.jpg").write_bytes(b"x")
        (cap / "planche_1.jpg").write_bytes(b"x")
        return cap / "face.jpg"

    def test_hors_build_lecture_libre(self):
        # .claude/builds-evo existe mais aucune pièce en cours (Atelier, séance MJ) : rien n'est refusé
        self.assertEqual(self.pre("Read", {"file_path": str(self.captures_avec_planche())})[0], None)

    def test_hors_arbre_du_build_lecture_libre(self):
        face = self.captures_avec_planche()
        self.piece()
        with tempfile.TemporaryDirectory() as ailleurs:
            res = lancer("pre", {"tool_name": "Read", "tool_input": {"file_path": str(face)}, "cwd": ailleurs})
        self.assertIsNone(res)

    def test_fichiers_des_hooks_proteges(self):
        self.assertEqual(self.pre("Write", {"file_path": str(self.etat / "compteurs.json"), "content": "{}"})[0], "deny")
        self.assertEqual(self.pre("Edit", {"file_path": str(self.etat / "piece.json")})[0], None)


class Conso(Base):
    def transcript(self, f, lignes):
        with open(f, "a", encoding="utf-8") as t:
            for l in lignes:
                t.write(json.dumps(l) + "\n")

    def msg(self, ident, modele, entree, sortie, lu=0):
        return {"type": "assistant", "message": {"id": ident, "model": modele, "usage": {
            "input_tokens": entree, "output_tokens": sortie, "cache_read_input_tokens": lu, "cache_creation_input_tokens": 0}}}

    def test_compte_par_modele_sans_double(self):
        self.piece()
        t = self.racine / "session.jsonl"
        m1 = self.msg("m1", "claude-opus-5-5", 100, 50, 1000)
        self.transcript(t, [{"type": "user", "message": {"content": "x"}}, m1, m1, self.msg("m2", "claude-sonnet-5-5", 10, 5)])
        lancer("stop", {"transcript_path": str(t), "cwd": str(self.sous)})
        lancer("stop", {"transcript_path": str(t), "cwd": str(self.sous)})   # relu : rien de plus
        self.transcript(t, [self.msg("m3", "claude-opus-5-5", 1, 1)])
        lancer("stop", {"transcript_path": str(t), "cwd": str(self.sous)})
        conso = json.loads((self.etat / "conso.json").read_text(encoding="utf-8"))
        arche = conso["scenes"]["A3"]["Arche"]
        self.assertEqual(arche["opus"], [101, 0, 1000, 51])
        self.assertEqual(arche["sonnet"], [10, 0, 0, 5])
        r = subprocess.run([sys.executable, str(HOOK), "rapport", "A3"], capture_output=True, cwd=str(self.sous), timeout=20)
        texte = r.stdout.decode("utf-8")
        self.assertIn("Arche", texte)
        self.assertIn("indice", texte)

    def test_sous_agent(self):
        self.piece()
        t = self.racine / "agent.jsonl"
        self.transcript(t, [self.msg("a1", "claude-sonnet-5-5", 20, 10)])
        lancer("stop", {"transcript_path": str(self.racine / "absent.jsonl"), "agent_transcript_path": str(t),
                        "cwd": str(self.sous)})
        conso = json.loads((self.etat / "conso.json").read_text(encoding="utf-8"))
        self.assertEqual(conso["scenes"]["A3"]["Arche"]["sonnet"], [20, 0, 0, 10])

    def test_stop_ne_dit_rien(self):
        self.piece()
        t = self.racine / "s.jsonl"
        self.transcript(t, [self.msg("m1", "claude-opus-5-5", 1, 1)])
        self.assertIsNone(lancer("stop", {"transcript_path": str(t), "cwd": str(self.sous)}))


class Debut(Base):
    def test_relais_et_etat_injectes(self):
        self.piece(cahier_valide=None)
        (self.etat / "relais.md").write_text("# Relais : A3 › conception → arche\n- Prochaine étape : arche v1", encoding="utf-8")
        res = lancer("debut", {"source": "startup", "cwd": str(self.sous)})
        self.assertEqual(res["hookEventName"], "SessionStart")
        self.assertIn("arche v1", res["additionalContext"])
        self.assertIn("NON validé", res["additionalContext"])

    def test_relais_trop_long_coupe(self):
        self.piece()
        (self.etat / "relais.md").write_text("x" * 5000, encoding="utf-8")
        res = lancer("debut", {"cwd": str(self.sous)})
        self.assertLess(len(res["additionalContext"]), 3500)
        self.assertIn("raccourcir", res["additionalContext"])

    def test_hors_build_silencieux(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(lancer("debut", {"cwd": d}))


if __name__ == "__main__":
    unittest.main()


class ModeleEtDepense(Base):
    def transcript(self, modele, lu_banc=True):
        f = self.racine / "t.jsonl"
        lignes = [json.dumps({"type": "user", "message": {}})]
        if lu_banc:
            lignes.append(json.dumps({"type": "assistant", "message": {"model": modele, "id": "m0", "usage": {}, "content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "/x/skills/banc-gmod/SKILL.md"}}]}}))
        lignes.append(json.dumps({"type": "assistant", "message": {"model": modele, "id": "m1", "usage": {}}}))
        f.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        return str(f)

    def pre_t(self, modele):
        res = lancer("pre", {"tool_name": PASSE, "tool_input": {"dupe": "a.txt"}, "cwd": str(self.sous), "transcript_path": self.transcript(modele)})
        return res and res["permissionDecision"], res and res.get("permissionDecisionReason", "")

    def test_passe_refusee_sur_opus(self):
        self.piece()
        choix, raison = self.pre_t("claude-opus-5-5")
        self.assertEqual(choix, "deny")
        self.assertIn("Sonnet", raison)
        self.assertEqual(self.pre_t("claude-sonnet-5-5")[0], None)

    def test_dispense_de_modele(self):
        self.piece(modele_banc="dispense")
        self.assertEqual(self.pre_t("claude-opus-5-5")[0], None)

    def test_plafond_de_depense(self):
        self.piece(plafond_depense=10)
        (self.etat / "conso.json").write_text(json.dumps({"scenes": {"A3": {"Arche": {"opus": [0, 0, 0, 3000000]}}}}), encoding="utf-8")
        choix, raison = self.pre(PASSE, {"dupe": "a.txt"})
        self.assertEqual(choix, "deny")
        self.assertIn("Plafond de dépense", raison)
        self.piece(plafond_depense=0)
        self.assertEqual(self.pre(PASSE, {"dupe": "a.txt"})[0], None)

    def test_debut_affiche_depense_et_modele(self):
        self.piece()
        ctx = lancer("debut", {"cwd": str(self.sous), "model": "claude-opus-5-5"})["additionalContext"]
        self.assertIn("Dépense de la scène", ctx)
        self.assertIn("refusées hors Sonnet", ctx)


class FicheBancLue(ModeleEtDepense):
    def test_refus_sans_lecture_du_skill_banc(self):
        self.piece()
        t = self.transcript("claude-sonnet-5-5", lu_banc=False)
        res = lancer("pre", {"tool_name": PASSE, "tool_input": {"dupe": "a.txt"}, "cwd": str(self.sous), "transcript_path": t})
        self.assertEqual(res["permissionDecision"], "deny")
        self.assertIn("banc-gmod", res["permissionDecisionReason"])

    def test_skill_appele_compte(self):
        self.piece()
        t = self.racine / "t2.jsonl"
        t.write_text(json.dumps({"type": "assistant", "message": {"model": "claude-sonnet-5-5", "id": "a", "usage": {}, "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "builds-evo:banc-gmod"}}]}}) + "\n", encoding="utf-8")
        res = lancer("pre", {"tool_name": PASSE, "tool_input": {"dupe": "a.txt"}, "cwd": str(self.sous), "transcript_path": str(t)})
        self.assertIsNone(res)

    def test_transcript_absent_ne_refuse_pas(self):
        self.piece()
        self.assertIsNone(self.pre(PASSE, {"dupe": "a.txt"})[0])
