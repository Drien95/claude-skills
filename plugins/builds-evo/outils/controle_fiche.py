#!/usr/bin/env python3
"""Contrôle gratuit d'une fiche DA (modèle build-evo/modeles/fiche-da.md) avant la maquette.

Usage : python controle_fiche.py fiche-da.md [--json]
Erreurs (code 1) : champ vide ou resté sur « … », palette hex absente, moins de 3 mots-images, moins de 3 indices.
Attentions : plus de 2 couleurs d'accent, accent non unique, lignes trop longues.
"""
import argparse
import re
import sys

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
CHAMPS = ["Phrase-titre", "3 mots-images", "Image maîtresse", "Palette en hex", "Langage de formes", "Ancrage",
          "Que s'est-il passé ici", "Lumière clé", "Son", "Arrivée des joueurs", "Budget global", "Boîte de scène"]


def lire(texte):
    """{étiquette: valeur} pour les lignes « - **Étiquette** (aide) : valeur »."""
    champs = {}
    for ligne in texte.splitlines():
        m = re.match(r"\s*[-*]\s+\*\*(.+?)\*\*(.*)$", ligne)
        if m:
            reste = m.group(2)
            valeur = reste.split(":", 1)[1] if ":" in reste else ""
            champs[m.group(1).strip()] = valeur.strip()
    return champs


def vide(v):
    return not re.sub(r"[…\.\s`()?\-]|\.\.\.", "", v)


def controler(texte):
    champs = lire(texte)
    erreurs, attentions = [], []
    for nom in CHAMPS:
        cle = next((k for k in champs if k.lower().startswith(nom.lower())), None)
        if cle is None:
            erreurs.append("champ absent : %s" % nom)
        elif vide(champs[cle]):
            erreurs.append("champ à remplir : %s" % nom)
    pal = next((v for k, v in champs.items() if k.lower().startswith("palette en hex")), "")
    couleurs = HEX.findall(pal)
    if pal and not vide(pal):
        if len(couleurs) < 3:
            erreurs.append("palette en hex : 3 couleurs minimum (dominante, neutre, accent), %d trouvée(s)" % len(couleurs))
        _, _, apres = pal.lower().rpartition("accent")
        if len(HEX.findall(apres)) > 1:
            attentions.append("plus d'un accent : l'accent est rare (1 ou 2 endroits)")
    mots = next((v for k, v in champs.items() if k.lower().startswith("3 mots")), "")
    if mots and not vide(mots) and len([m for m in re.split(r"[,;/]", mots) if m.strip()]) < 3:
        erreurs.append("3 mots-images : moins de 3 mots")
    ici = next((v for k, v in champs.items() if k.lower().startswith("que s'est")), "")
    if ici and not vide(ici) and len([m for m in re.split(r"[;,]", ici) if m.strip()]) < 3:
        erreurs.append("« que s'est-il passé ici » : 3 indices attendus (évident, discret, caché)")
    for k, v in champs.items():
        if len(v) > 400:
            attentions.append("champ trop long (%d signes) : %s" % (len(v), k[:40]))
    return erreurs, attentions


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("fiche")
    a = ap.parse_args(argv)
    try:
        texte = open(a.fiche, encoding="utf-8").read()
    except OSError as e:
        print("fiche illisible : %s" % e, file=sys.stderr)
        return 2
    erreurs, attentions = controler(texte)
    for e in erreurs:
        print("ERREUR : " + e)
    for t in attentions:
        print("ATTENTION : " + t)
    if not erreurs and not attentions:
        print("fiche DA complète")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
