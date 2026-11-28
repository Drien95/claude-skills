"""Coût réel d'un fil Claude Code, lu dans son journal .jsonl (0 jeton).

Usage : python conso_fil.py <journal.jsonl> [--lignes]
Affiche : socle au 1er appel (cache lu + écrit), croissance du contexte, totaux par modèle et indice pondéré
(prix relatifs : entrée 1, cache lu 0,1, cache écrit 1,25, sortie 5 ; Opus x5, Sonnet x3, Haiku x1 comme /builds-evo:conso).
"""
import json
import sys

PRIX_MODELE = {"opus": 5, "sonnet": 3, "haiku": 1}


def famille(m):
    m = (m or "").lower()
    return next((k for k in PRIX_MODELE if k in m), "autre")


def lire(chemin):
    vus, lignes = set(), []
    with open(chemin, encoding="utf-8", errors="replace") as f:
        for l in f:
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("type") != "assistant":
                continue
            m = d.get("message") or {}
            u, mid = m.get("usage"), m.get("id")
            if not u or mid in vus:
                continue
            vus.add(mid)
            lignes.append({
                "t": (d.get("timestamp") or "")[11:19], "modele": m.get("model") or "",
                "entree": u.get("input_tokens", 0), "ecrit": u.get("cache_creation_input_tokens", 0),
                "lu": u.get("cache_read_input_tokens", 0), "sortie": u.get("output_tokens", 0),
                "outils": [c.get("name", "").split("__")[-1] for c in m.get("content") or [] if c.get("type") == "tool_use"],
            })
    return lignes


def indice(l):
    return (l["entree"] + 0.1 * l["lu"] + 1.25 * l["ecrit"] + 5 * l["sortie"]) * PRIX_MODELE.get(famille(l["modele"]), 3) / 5


def resume(lignes):
    if not lignes:
        return {"appels": 0}
    p = lignes[0]
    socle = p["entree"] + p["ecrit"] + p["lu"]
    contexte = [l["entree"] + l["ecrit"] + l["lu"] for l in lignes]
    return {
        "appels": len(lignes), "socle": socle, "socle_en_cache": p["lu"], "socle_ecrit": p["ecrit"],
        "contexte_fin": contexte[-1], "croissance_par_appel": round((contexte[-1] - socle) / max(1, len(lignes) - 1)),
        "lu": sum(l["lu"] for l in lignes), "ecrit": sum(l["ecrit"] for l in lignes), "sortie": sum(l["sortie"] for l in lignes),
        "indice_k": round(sum(indice(l) for l in lignes) / 1000),
        "modeles": sorted({famille(l["modele"]) for l in lignes}),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    L = lire(sys.argv[1])
    r = resume(L)
    print(json.dumps(r, ensure_ascii=False))
    if "--lignes" in sys.argv:
        for l in L:
            print(l["t"], l["entree"], l["ecrit"], l["lu"], l["sortie"], famille(l["modele"]), ",".join(l["outils"]))
