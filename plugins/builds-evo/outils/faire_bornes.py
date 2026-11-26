"""Catalogue des bornes de tous les modèles autorisés (PHX lus dans garrysmod_dir.vpk, autres tirés de geo_catalogue.json).
Usage : python faire_bornes.py [--autorises F] [--geo F] [--vpk F] [--sortie F]  ->  bornes_modeles.json
Défauts : variables CATALOGUE_BUILD (dossier de modeles_autorises.txt et geo_catalogue.json), GMOD_DIR (dossier garrysmod).
Sans VPK, seules les bornes de geo_catalogue sont écrites.  {modele: {"min": [x,y,z], "max": [x,y,z], "src": "vpk"|"geo"}}
Lecture : json.load(open('bornes_modeles.json'))['models/hunter/tubes/tube4x4x8c.mdl']['min']"""
import argparse, json, os, struct
from pathlib import Path
ICI = Path(__file__).resolve().parent
_cat = Path(os.environ.get('CATALOGUE_BUILD', ICI.parent / 'catalogue-build'))
_gmod = Path(os.environ.get('GMOD_DIR', 'C:/SteamLibrary/steamapps/common/GarrysMod/garrysmod'))
ap = argparse.ArgumentParser()
ap.add_argument('--autorises', default=str(_cat / 'modeles_autorises.txt'))
ap.add_argument('--geo', default=str(_cat / 'geo_catalogue.json'))
ap.add_argument('--vpk', default=str(_gmod / 'garrysmod_dir.vpk'))
ap.add_argument('--sortie', default=str(ICI / 'bornes_modeles.json'))
A = ap.parse_args()
VPK = Path(A.vpk)
autorises = [l.strip().lower() for l in open(A.autorises, encoding='utf-8') if l.strip() and not l.startswith('#')]
voulus = set(autorises)
out = {}
data = VPK.read_bytes() if VPK.exists() else b''
sig, ver = struct.unpack_from('<II', data, 0) if data else (0, 1); tree_len = struct.unpack_from('<I', data, 8)[0] if data else 0
hdr = 12 if ver == 1 else 28
def lire(o):
    e = data.index(b'\0', o); return data[o:e].decode('latin-1'), e + 1
o = hdr
while data:
    ext, o = lire(o)
    if not ext: break
    while True:
        chemin, o = lire(o)
        if not chemin: break
        while True:
            nom, o = lire(o)
            if not nom: break
            crc, plen, idx, eoff, elen, term = struct.unpack_from('<IHHIIH', data, o)
            pre = data[o+18:o+18+plen]; o += 18 + plen
            f = f'{chemin}/{nom}.{ext}'.lower()
            if ext != 'mdl' or f not in voulus: continue
            if idx == 0x7fff:
                corps = data[hdr + tree_len + eoff: hdr + tree_len + eoff + elen]
            else:
                with open(VPK.with_name(VPK.name.replace('_dir', '_%03d' % idx)), 'rb') as fa:
                    fa.seek(eoff); corps = fa.read(max(0, 160 - plen))
            b = pre + corps
            v = struct.unpack_from('<6f', b, 104)
            out[f] = {'min': [round(x, 2) for x in v[:3]], 'max': [round(x, 2) for x in v[3:]], 'src': 'vpk'}
geo = json.load(open(A.geo)) if os.path.exists(A.geo) else {}
for m, g in geo.items():
    m2 = m.lower()
    if m2 in out or m2 not in voulus: continue
    p = g['pos']
    out[m2] = {'min': [round(min(p[i::3]), 2) for i in range(3)], 'max': [round(max(p[i::3]), 2) for i in range(3)], 'src': 'geo'}
json.dump(out, open(A.sortie, 'w'), indent=0, sort_keys=True)
manque = [m for m in autorises if m not in out]
print(len(out), 'modèles bornés ;', len(manque), 'sans bornes (ni VPK de base ni geo_catalogue)')
