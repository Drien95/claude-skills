"""Contrôle automatique d'un build AVANT le banc et la critique (0 token, moins d'une seconde).

Usage :  python controle_auto.py <dupe.txt | scene.json> [--budget N] [--boite DX DY DZ] [--autorises f.txt]
                                 [--bornes bornes_modeles.json] [--json]
Lit un dupe AdvDupe2 (révision 5, celui d'encode.py ou du jeu) ou le scene.json d'un générateur, et vérifie
ce qu'une critique ou Adrien relèverait à coup sûr :
  ERREUR    (le banc refuse la passe) : plus de 400 posés ou au-dessus du budget ; classe bloquée sur EVO
            (gmod_light, gmod_lamp, gmod_emitter, prop_effect) ; playermodel ; modèle hors liste autorisée ;
            deux props identiques au même endroit (z-fight) ; prop hors de la boîte de scène.
  ATTENTION (dit dans le rapport) : clé Frozen (le collage dégèle), prop qui flotte (ne touche ni le sol ni un
            autre prop, d'après les bornes), mot « hollow » ou « menos » dans un modèle, liste autorisée absente.
Sortie : au plus 12 lignes, code 1 s'il y a une erreur. Utilisé aussi par `banc_passe` (serveur MCP du banc).
"""
import argparse
import json
import lzma
import math
import os
import struct
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
BLOQUEES = {"gmod_light", "gmod_lamp", "gmod_emitter", "prop_effect"}
LIMITE = 400
TOL_DOUBLON, TOL_CONTACT, TOL_SOL = 0.5, 2.0, 4.0


# ---------- lecture AdvDupe2 (révision 5) ----------
class Lecteur:
    def __init__(self, b):
        self.b, self.i, self.tables = b, 0, []

    def octet(self):
        v = self.b[self.i]
        self.i += 1
        return v

    def lire(self, n):
        v = self.b[self.i:self.i + n]
        if len(v) < n:
            raise ValueError("dupe tronqué")
        self.i += n
        return v

    def valeur(self):
        t = self.octet()
        if t == 255:                       # table clé/valeur
            d = {}
            self.tables.append(d)
            while self.b[self.i] != 246:
                k = self.valeur()
                d[k] = self.valeur()
            self.i += 1
            return d
        if t == 254:                       # tableau
            l = []
            self.tables.append(l)
            while self.b[self.i] != 246:
                l.append(self.valeur())
            self.i += 1
            return {k + 1: v for k, v in enumerate(l)}
        if t == 253:
            return True
        if t == 252:
            return False
        if t == 251:
            return struct.unpack("<d", self.lire(8))[0]
        if t in (250, 249):
            return tuple(struct.unpack("<3d", self.lire(24)))
        if t == 248:
            n = struct.unpack("<I", self.lire(4))[0]
            return self.lire(n).decode("utf-8", "replace")
        if t == 247:                       # référence à une table déjà lue
            n = struct.unpack("<I", self.lire(4))[0]
            return self.tables[n - 1] if 0 < n <= len(self.tables) else {}
        if t < 246:
            return self.lire(t).decode("utf-8", "replace")
        raise ValueError("type inconnu %d à l'octet %d" % (t, self.i - 1))


def lire_dupe(chemin):
    data = Path(chemin).read_bytes()
    if not data.startswith(b"AD2F"):
        raise ValueError("pas un dupe AdvDupe2 (en-tête AD2F absent)")
    if data[4] != 5:
        raise ValueError("révision AdvDupe2 %d non lue (5 seulement)" % data[4])
    fin = data.find(b"\x02", 6)
    if fin < 0:
        raise ValueError("bloc d'infos du dupe illisible")
    comp = data[fin + 2:] if data[fin + 1:fin + 2] == b"\n" else data[fin + 1:]
    try:
        brut = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(comp)
    except lzma.LZMAError:
        # taille connue + marque de fin : certaines versions de liblzma (Windows) refusent ; taille « inconnue »
        comp = comp[:5] + b"\xff" * 8 + comp[13:]
        brut = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(comp)
    racine = Lecteur(brut).valeur()
    ents = []
    for e in (racine.get("Entities") or {}).values():
        if not isinstance(e, dict):
            continue
        phys = (e.get("PhysicsObjects") or {})
        p0 = phys.get(0) or phys.get(0.0) or phys.get(1) or phys.get(1.0) or {}
        mods = e.get("EntityMods") or {}
        couleur = ((mods.get("colour") or {}).get("Color") or {})
        ents.append({"classe": e.get("Class", "prop_physics"), "modele": str(e.get("Model", "")).lower(),
                     "pos": tuple(p0.get("Pos") or (0, 0, 0)), "ang": tuple(p0.get("Angle") or (0, 0, 0)),
                     "echelle": e.get("ModelScale") or 1, "fige": "Frozen" in p0, "alpha": couleur.get("a", 255),
                     "note": ""})
    return ents


def lire_scene(chemin):
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    ents = d.get("ents") or []
    tete = next((e for e in ents if e.get("note") == d.get("head")), ents[0] if ents else None)
    hp = tete["pos"] if tete else (0, 0, 0)
    sortie = []
    for e in ents:
        classe = "prop_effect" if e.get("kind") == "effect" else "prop_physics"
        sortie.append({"classe": classe, "modele": str(e.get("model", "")).lower(),
                       "pos": tuple(e["pos"][j] - hp[j] for j in range(3)), "ang": tuple(e.get("ang") or (0, 0, 0)),
                       "echelle": e.get("scale") or 1, "fige": False, "alpha": 255, "note": e.get("note", "")})
    for l in d.get("fx") or []:
        classe = {"light": "gmod_light", "lamp": "gmod_lamp"}.get(l.get("kind"), "gmod_emitter")
        sortie.append({"classe": classe, "modele": "", "pos": tuple(l["pos"][j] - hp[j] for j in range(3)),
                       "ang": (0, 0, 0), "echelle": 1, "fige": False, "alpha": 0, "note": l.get("kind", "")})
    return sortie


# ---------- géométrie ----------
def matrice(ang):
    p, y, r = (math.radians(a) for a in ang)
    sp, cp, sy, cy, sr, cr = math.sin(p), math.cos(p), math.sin(y), math.cos(y), math.sin(r), math.cos(r)
    # AngleMatrix de Source : colonnes = avant, gauche, haut
    return [[cp * cy, sr * sp * cy - cr * sy, cr * sp * cy + sr * sy],
            [cp * sy, sr * sp * sy + cr * cy, cr * sp * sy - sr * cy],
            [-sp, sr * cp, cr * cp]]


def boite_monde(e, bornes):
    b = bornes.get(e["modele"])
    if not b:
        return None
    s = e["echelle"] if isinstance(e["echelle"], (int, float)) else 1
    m = matrice(e["ang"])
    coins = [(x, y, z) for x in (b["min"][0], b["max"][0]) for y in (b["min"][1], b["max"][1]) for z in (b["min"][2], b["max"][2])]
    pts = [[e["pos"][i] + s * sum(m[i][k] * c[k] for k in range(3)) for i in range(3)] for c in coins]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def se_touchent(a, b, tol=TOL_CONTACT):
    return all(a[0][i] - tol <= b[1][i] and b[0][i] - tol <= a[1][i] for i in range(3))


def flottants(ents, bornes):
    boites = [boite_monde(e, bornes) for e in ents]
    if not ents or boites[0] is None:
        return []
    sol = boites[0][0][2]                          # la tête est posée sur le sol au collage
    connus = [i for i, b in enumerate(boites) if b is not None]
    portes = {i for i in connus if boites[i][0][2] <= sol + TOL_SOL}
    file = list(portes)
    while file:
        i = file.pop()
        for j in connus:
            if j not in portes and se_touchent(boites[i], boites[j]):
                portes.add(j)
                file.append(j)
    return [i for i in connus if i not in portes and ents[i]["alpha"] != 0]


# ---------- contrôle ----------
def trouver_autorises(chemin=None):
    for c in (chemin, os.environ.get("MODELES_AUTORISES"),
              os.path.join(os.environ.get("CATALOGUE_BUILD", str(ICI.parent / "catalogue-build")), "modeles_autorises.txt")):
        if c and Path(c).is_file():
            return {l.strip().lower() for l in Path(c).read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()}
    return None


def charger_bornes(chemin=None):
    c = Path(chemin or os.environ.get("BORNES_JSON") or ICI / "bornes_modeles.json")
    try:
        return {k.lower(): v for k, v in json.loads(c.read_text(encoding="utf-8")).items()}
    except (OSError, ValueError):
        return {}


def controler(chemin, budget=None, boite=None, autorises=None, bornes=None):
    """Renvoie (erreurs, attentions, resume)."""
    chemin = Path(chemin)
    ents = lire_scene(chemin) if chemin.suffix.lower() == ".json" else lire_dupe(chemin)
    erreurs, attentions = [], []
    n = len(ents)
    plafond = min(LIMITE, int(budget)) if budget else LIMITE
    if n > plafond:
        erreurs.append("%d posés, plafond %d%s" % (n, plafond, " (budget de la pièce)" if budget and budget < LIMITE else ""))
    bloquees = sorted({e["classe"] for e in ents} & BLOQUEES)
    if bloquees:
        erreurs.append("classe bloquée sur EVO : %s (le faire en script)" % ", ".join(bloquees))
    joueurs = sorted({e["modele"] for e in ents if "/player/" in e["modele"] or "playermodel" in e["modele"]})
    if joueurs:
        erreurs.append("playermodel en décor : %s" % ", ".join(joueurs[:3]))
    douteux = sorted({e["modele"] for e in ents if "hollow" in e["modele"] or "menos" in e["modele"]})
    if douteux:
        attentions.append("modèle à vérifier (jamais de Hollow ni de Menos en décor) : %s" % ", ".join(douteux[:3]))
    liste = trouver_autorises(autorises)
    if liste is None:
        attentions.append("liste des modèles autorisés absente (CATALOGUE_BUILD) : modèles non vérifiés")
    else:
        hors = sorted({e["modele"] for e in ents if e["modele"] and e["modele"] not in liste})
        if hors:
            erreurs.append("%d modèle(s) hors liste autorisée : %s" % (len(hors), ", ".join(hors[:3])))
    vus, doublons = {}, []
    for i, e in enumerate(ents):
        cle = (e["modele"],) + tuple(round(v / TOL_DOUBLON) for v in e["pos"]) + tuple(round(a) % 360 for a in e["ang"])
        if cle in vus and e["modele"]:
            doublons.append(e["note"] or e["modele"].rsplit("/", 1)[-1])
        vus[cle] = i
    if doublons:
        erreurs.append("%d prop(s) en double au même endroit (z-fight) : %s" % (len(doublons), ", ".join(doublons[:3])))
    if boite:
        dehors = [e["note"] or e["modele"].rsplit("/", 1)[-1] for e in ents
                  if any(abs(e["pos"][i]) > boite[i] for i in range(3))]
        if dehors:
            erreurs.append("%d prop(s) hors de la boîte ±%s : %s" % (len(dehors), boite, ", ".join(dehors[:3])))
    if any(e["fige"] for e in ents):
        attentions.append("clé Frozen présente : le collage AdvDupe2 dégèle ces props")
    if bornes is None:
        bornes = charger_bornes()
    f = flottants(ents, bornes)
    if f:
        attentions.append("%d prop(s) semblent flotter (ni sol ni contact) : %s"
                          % (len(f), ", ".join(ents[i]["note"] or ents[i]["modele"].rsplit("/", 1)[-1] for i in f[:4])))
    # fiche 04 : dernière passe « de travers » (décor non porteur tourné de 2 à 8°)
    modeles = [e for e in ents if e["modele"]]
    droits = [e for e in modeles if all(abs(a - 90 * round(a / 90)) < 0.5 for a in e["ang"])]
    if len(modeles) >= 20 and len(droits) / len(modeles) > 0.85:
        attentions.append("%d %% des props sont parfaitement droits : une dernière passe « de travers » (2 à 8° sur le décor non porteur) "
                          "évite l'effet boîte" % round(100 * len(droits) / len(modeles)))
    return erreurs, attentions, "%d posés (plafond %d)" % (n, plafond)


def rapport(erreurs, attentions, resume):
    lignes = ["contrôle auto : %s, %s" % (resume, "%d erreur(s)" % len(erreurs) if erreurs else "aucune erreur")]
    lignes += ["ERREUR : " + e for e in erreurs] + ["ATTENTION : " + a for a in attentions]
    return "\n".join(lignes[:12])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("fichier")
    ap.add_argument("--budget", type=int)
    ap.add_argument("--boite", type=float, nargs=3, metavar=("DX", "DY", "DZ"))
    ap.add_argument("--autorises")
    ap.add_argument("--bornes")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        erreurs, attentions, resume = controler(a.fichier, a.budget, a.boite, a.autorises,
                                                charger_bornes(a.bornes) if a.bornes else None)
    except (OSError, ValueError, lzma.LZMAError) as e:
        print("contrôle auto : fichier illisible (%s)" % e)
        return 2
    if a.json:
        print(json.dumps({"erreurs": erreurs, "attentions": attentions, "resume": resume}, ensure_ascii=False))
    else:
        sys.stdout.buffer.write((rapport(erreurs, attentions, resume) + "\n").encode("utf-8"))
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
