"""Gravure d'usine d'une scène : 3 petits props dédiés, posés sur le prop repère du dupe, à des écarts, des angles et des
couleurs tirés de l'identifiant de la scène (« A2 v15 »). Le script de la scène reconnaît son build à cette gravure,
sans dépendre du décor ni de ce que voient les clients (voir gravure_lua/sh_gravure.lua).

Usage :
    python gravure.py "A2 v15" [--zone 90] [--z 1.75] [--json marques.json] [--lua marques.lua]

Sortie : les marques en coordonnées RELATIVES au prop repère (x, y, z, lacet, couleur), en JSON (pour le générateur du
build) et en table Lua (pour le script). Déterministe : le même identifiant donne toujours la même gravure.
"""
import argparse
import hashlib
import json
import math
import sys

MODELE = "models/hunter/plates/plate025x025.mdl"   # 12,4 x 12,4 x 3,5 u, liste blanche EVO
DEMI_EPAISSEUR = 1.75
ECART_MIN = 30.0          # entre deux marques (u) : jamais confondues, même à 6 u de tolérance
N_MAX_ESSAIS = 64


def _octets(identifiant, sel):
    return hashlib.sha256((identifiant.strip() + "|" + str(sel)).encode("utf-8")).digest()


def _lacet(b):
    """angle 5 à 85° (0,1° près), jamais un multiple de 5° : personne ne le pose ainsi par hasard"""
    a = 5 + (int.from_bytes(b[0:2], "big") % 800) / 10
    return a + 0.3 if abs(a / 5 - round(a / 5)) < 1e-9 else a


def _couleur(b):
    """couleur improbable : composantes 17 à 238, jamais rondes (multiples de 5)"""
    out = []
    for v in b[:3]:
        c = 17 + v % 222
        out.append(c + 1 if c % 5 == 0 else c)
    return out


def gravure(identifiant, n=3, zone=90.0, z=None, modele=MODELE):
    """n marques dans un carré de +/- zone autour du centre du repère, posées dessus (z = haut du repère + demi-épaisseur
    si z est None : à donner selon le modèle repère)."""
    if not identifiant or not identifiant.strip():
        raise ValueError("identifiant vide")
    if not (1 <= n <= 6):
        raise ValueError("n doit aller de 1 à 6")
    if zone < ECART_MIN:
        raise ValueError("zone trop petite pour écarter les marques")
    marques = []
    for k in range(n):
        for essai in range(N_MAX_ESSAIS):
            b = _octets(identifiant, f"{k}-{essai}")
            x = round(-zone + (int.from_bytes(b[3:5], "big") / 65535) * 2 * zone, 1)
            y = round(-zone + (int.from_bytes(b[5:7], "big") / 65535) * 2 * zone, 1)
            if all(math.hypot(x - m["x"], y - m["y"]) >= ECART_MIN for m in marques):
                break
        else:
            raise RuntimeError("pas de place pour la marque %d" % (k + 1))
        marques.append({"modele": modele, "x": x, "y": y, "z": z, "lacet": round(_lacet(b[7:9]), 1),
                        "couleur": _couleur(b[9:12])})
    return marques


def en_lua(marques, nom="GRAVURE"):
    lignes = [f"{nom} = {{   -- gravure d'usine (outils/gravure.py), relative au prop repère"]
    for m in marques:
        r, g, b = m["couleur"]
        lignes.append(f'  {{ modele = "{m["modele"]}", pos = Vector({m["x"]}, {m["y"]}, {m["z"]}), lacet = {m["lacet"]}, '
                      f'couleur = {{ {r}, {g}, {b} }} }},')
    lignes.append("}")
    return "\n".join(lignes)


def main(argv=None):
    p = argparse.ArgumentParser(description="Gravure d'usine d'une scène (3 marques tirées de l'identifiant)")
    p.add_argument("identifiant")
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--zone", type=float, default=90.0)
    p.add_argument("--z", type=float, default=2 * DEMI_EPAISSEUR, help="hauteur relative au centre du repère (défaut : posée sur une plaque PHX)")
    p.add_argument("--json")
    p.add_argument("--lua")
    a = p.parse_args(argv)
    m = gravure(a.identifiant, a.n, a.zone, a.z)
    if a.json:
        json.dump(m, open(a.json, "w", encoding="utf-8"), indent=1)
    if a.lua:
        open(a.lua, "w", encoding="utf-8").write(en_lua(m) + "\n")
    json.dump(m, sys.stdout, indent=1, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
