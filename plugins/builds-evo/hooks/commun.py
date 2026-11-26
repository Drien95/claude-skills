"""Outils partagés par les hooks du plugin builds-evo.

Les hooks lisent l'événement JSON de Claude Code sur l'entrée standard et
répondent en JSON sur la sortie standard. Python 3.8+, bibliothèque standard
seulement (le PC d'Adrien est sous Windows).
"""
import json
import os
import sys


def lire_evenement():
    brut = sys.stdin.buffer.read()
    try:
        return json.loads(brut.decode("utf-8", errors="replace") or "{}")
    except ValueError:
        return {}


def _ecrire(obj):
    # ensure_ascii : sortie lisible quel que soit l'encodage de la console Windows
    sys.stdout.write(json.dumps(obj, ensure_ascii=True))
    sys.stdout.flush()


def decision(evenement, choix, raison):
    """choix : 'deny' (bloque) ou 'ask' (demande à Adrien)."""
    _ecrire({
        "hookSpecificOutput": {
            "hookEventName": evenement,
            "permissionDecision": choix,
            "permissionDecisionReason": raison,
        }
    })


def contexte(evenement, texte):
    """Ajoute une remarque pour Claude sans rien bloquer (PostToolUse)."""
    _ecrire({
        "hookSpecificOutput": {
            "hookEventName": evenement,
            "additionalContext": texte,
        }
    })


def desactive(nom):
    """BUILDS_EVO_HOOKS_OFF=garde_banc,garde_lua coupe un hook (à n'utiliser qu'avec l'accord d'Adrien)."""
    off = os.environ.get("BUILDS_EVO_HOOKS_OFF", "")
    return nom in [x.strip() for x in off.split(",")]
