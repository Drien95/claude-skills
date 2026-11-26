# Gabarit de build GMod (AdvDupe2) pour EVO — tiré de la Salle des Exequias (v14).
# Usage : python3 build.py  ->  scene.json ; puis python3 encode.py  ->  build.txt (à mettre dans garrysmod/data/advdupe2/)
# Repère : GMod (x, y, z), 1 P = 47,45 u (taille de base des PHX). Lire gmod-build-lecons.md avant de commencer.
import math, json, re
P = 47.45; PT = 3.0; Q = P / 4

def dims(model):
    m = re.search(r'/(plate|cube|circle|tube)([0-9x]+)', model)
    kind = m.group(1)
    def num(s): return {'025': 0.25, '05': 0.5, '075': 0.75, '125': 1.25, '150': 1.5, '175': 1.75}.get(s) or float(s)
    parts = [num(s) for s in m.group(2).split('x') if s]
    if kind in ('plate', 'circle'): return (parts[0]*P, parts[1]*P, PT)
    return tuple(p*P for p in parts)

def rot(p, y, r):
    p, y, r = map(math.radians, (p, y, r))
    def mul(A, B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    Rz = [[math.cos(y), -math.sin(y), 0], [math.sin(y), math.cos(y), 0], [0, 0, 1]]
    Ry = [[math.cos(p), 0, math.sin(p)], [0, 1, 0], [-math.sin(p), 0, math.cos(p)]]
    Rx = [[1, 0, 0], [0, math.cos(r), -math.sin(r)], [0, math.sin(r), math.cos(r)]]
    return mul(Rz, mul(Ry, Rx))

CANDS = [(0,0,0),(0,90,0),(90,0,0),(90,90,0),(0,0,90),(0,90,90)]
def solve(model, ext):
    d = dims(model)
    for a in CANDS:
        R = rot(*a)
        e = [sum(abs(R[i][k])*d[k] for k in range(3)) for i in range(3)]
        if all(abs(e[i]-ext[i]) < 0.6 for i in range(3)): return a
    raise SystemExit(f'pas d’orientation pour {model} -> {ext} (dims {d})')

C = {
  'nuit':    ((10, 11, 18), 'models/shiny'),
  'abime':   ((6, 10, 18), 'models/shiny'),
  'blanc':   ((232, 230, 224), 'models/shiny'),
  'glace':   ((225, 240, 255), 'models/player/shared/ice_player'),
  'noir':    ((12, 11, 14), 'models/shiny'),
  'or':      ((214, 168, 72), 'models/shiny'),   # gold_player est refusé par le serveur : doré en models/shiny
  'glow_bl': ((150, 185, 235), 'models/debug/debugwhite'),
  'glow_cy': ((225, 200, 232), 'models/debug/debugwhite'),   # lumière mauve pâle des sceaux Hachigen
  'glow_or': ((255, 190, 100), 'models/debug/debugwhite'),
  'lune':    ((235, 240, 255), 'models/debug/debugwhite'),
  'bouclier':((200, 225, 255), 'models/props_combine/com_shield001a'),
  'faisceau':((170, 195, 255), 'Models/effects/vol_light001'),
  'couloir': ((70, 72, 86), 'brick/brick_model'),
  'roche':   ((40, 43, 42), 'models/shiny'),   # la texture des rochers ne s'applique pas en override
}
ents = []
def put(model, pos, ang, style, note, cg=None):
    ang = tuple(round(a, 4) for a in ang)
    col, mat = C[style]
    ents.append(dict(kind='prop', model=model, pos=tuple(pos), ang=tuple(ang), color=col, mat=mat, style=style, note=note, cg=cg))
def box(model, x0, x1, y0, y1, z0, z1, style, note, cg=None):
    model = 'models/hunter/' + model + '.mdl'
    put(model, ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), solve(model, (x1-x0, y1-y0, z1-z0)), style, note, cg)
EV5 = 'models/evo/props/'; HM = 'models/propper/hueco_mundo_v1/'
def evo(model, pos, ang, note, effect=False, skin=None):
    # EVO bloque prop_effect au collage (18/11/2026) : seuls les modèles AVEC .phy, en prop_physics.
    assert not effect, f'{model} : prop_effect bloqué sur EVO'
    ents.append(dict(kind='evo', model=model, pos=tuple(round(v, 3) for v in pos), ang=tuple(ang), note=note, skin=skin))
HG = 'models/evo/attacks/hachigen_v3/'


# ====================== LE BUILD ======================
# GÉNÉRATEUR DE DUNES (26/11). Usage : python dunes.py params.json  ->  dupe <nom>.txt, essai_dunes_lointaines.lua, vues_<nom>.json
# Une passe = changer les chiffres du JSON (variantes, hauteurs, variation, graine, couches lointaines), puis banc_tester.
# Base : planche 2 (26/11) : couche 1 seule en props (8 demi-tubes), variantes A (chaîne) et B (bouts enterrés),
# chacune sur sa copie du sol v3 figé. Couches 2 et 3 + drapé de sable : essai_dunes_lointaines.lua (hauteurs calculées ici).
import random, sys
PARAMS = json.load(open(sys.argv[1], encoding='utf-8'))
C['fond']      = ((75, 70, 64), 'models/shiny')
C['couronne']  = ((85, 79, 72), 'models/shiny')
C['exterieur'] = ((95, 88, 80), 'models/shiny')
C['dune']      = ((85, 79, 72), 'models/shiny')
FOND_Z = -60.0
R_IN, R_OUT = 280.0, 520.0
K = 16
TETE_Z = FOND_Z - PT/2
SOL_MAP = TETE_Z
R_INTERDIT = 700.0
def coins_dessus(model, pos, ang):
    dx, dy, dz = dims(model); R = rot(*ang)
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            l = (sx*dx/2, sy*dy/2, dz/2)
            out.append(tuple(pos[i] + sum(R[i][k]*l[k] for k in range(3)) for i in range(3)))
    return out
def fond(ox, tete):
    n, pas = 3, 226
    for i in range(n):
        for j in range(n):
            x = ox + (i-(n-1)/2)*pas; y = (j-(n-1)/2)*pas
            put('models/hunter/plates/plate5x5.mdl', (x, y, TETE_Z), (0, 0, 0), 'fond', 'sol' if (tete and i == 0 and j == 0) else 'fond')
def couronne(ox):
    m = 'models/hunter/plates/plate5x8.mdl'
    pente = math.atan2(-FOND_Z, R_OUT - R_IN); ang = math.degrees(pente)
    rc = (R_IN + R_OUT)/2; zdessus = FOND_Z/2
    nr, nz = -math.sin(pente), math.cos(pente)
    r0, z0 = rc - nr*PT/2, zdessus - nz*PT/2
    bord = []
    for q in range(K):
        a = q/K*360
        pos = (ox + math.cos(math.radians(a))*r0, math.sin(math.radians(a))*r0, z0)
        put(m, pos, (-ang, a, 0), 'couronne', 'couronne')
        bord.append(max(coins_dessus(m, pos, (-ang, a, 0)), key=lambda c: c[2]))
    zhaut = max(c[2] for c in bord)
    apo = max((c[0]-ox)*math.cos(math.radians(q/K*360)) + c[1]*math.sin(math.radians(q/K*360)) for q, c in enumerate(bord))
    return zhaut, apo
def exterieur(ox, zhaut, apo):
    m = 'models/hunter/plates/plate16x16.mdl'
    r = apo + dims(m)[0]/2
    for q in range(K):
        a = q/K*360
        dessus = zhaut + 0.2 + (0.2 if q % 2 else 0.0)
        put(m, (ox + math.cos(math.radians(a))*r, math.sin(math.radians(a))*r, dessus - PT/2), (0, a, 0), 'exterieur', 'exterieur')
def sol(ox, tete=False):
    fond(ox, tete); zh, apo = couronne(ox); exterieur(ox, zh, apo)
    return zh + 0.2

# ---------- couche 1 : demi-tubes (axe = z local, bombé vers -x local, origine au centre de l'axe) ----------
TUBES = {'models/hunter/tubes/tube4x4x8c.mdl': (95.2, 380.1), 'models/hunter/tubes/tube4x4x16c.mdl': (95.2, 759.8)}
def axe(ang):
    R = rot(*ang)
    return tuple(R[i][2] for i in range(3)), tuple(-R[i][0] for i in range(3))   # direction de l'axe, « haut » du demi-tube
COUCHE1 = []      # (variante, ox, centre, direction, rayon, demi-longueur)
def tube(var, ox, g, m, a, r, h, s, tangage, roulis, lacet_plus=0.0):
    R0, L0 = TUBES[m]; Rt = R0*s
    assert g + h - Rt >= SOL_MAP - 1e-6, f'{var} : origine sous le sol de la map ({g + h - Rt:.1f})'
    ra = math.radians(a)
    pos = (ox + math.cos(ra)*r, math.sin(ra)*r, g + h - Rt)
    # pitch 90 couche le tube (z local -> horizontal), lacet a+90 le met en tangente ; tangage / roulis ensuite (≤ 5°)
    R = rot(90, a + 90 + lacet_plus, 0)
    Rp = rot(tangage, 0, roulis)
    M = [[sum(R[i][k]*Rp[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    p = math.degrees(math.asin(max(-1, min(1, -M[2][0]))))
    if abs(math.cos(math.radians(p))) > 1e-6:
        y = math.degrees(math.atan2(M[1][0], M[0][0])); rr = math.degrees(math.atan2(M[2][1], M[2][2]))
    else:
        y = math.degrees(math.atan2(-M[0][1], M[1][1])); rr = 0.0
    ang = (p, y, rr)
    Rv = rot(*ang)
    assert all(abs(Rv[i][j] - M[i][j]) < 1e-6 for i in range(3) for j in range(3)), 'angles mal convertis'
    put(m, pos, ang, 'dune', 'dune'); ents[-1]['scale'] = round(s, 3)
    d, _ = axe(ang)
    COUCHE1.append((var, ox, pos, d, Rt, L0*s/2))
    # rien dans le cercle r < 700 (boîte du demi-tube : axe ± demi-longueur, rayon)
    for t in (-1, 1):
        bout = [pos[i] + t*d[i]*L0*s/2 for i in range(3)]
        rb = math.hypot(bout[0]-ox, bout[1]) - Rt
        assert rb >= R_INTERDIT, f'{var} : un bout de tube à r {rb:.0f}'
    assert r - Rt >= R_INTERDIT

def variante(v, ox, g):
    # v : {nom, type: "chaine"|"separe", modele, graine, n, r, h, var (±), tangage, roulis, lacet, decal, echelle: [min, max]}
    rnd = random.Random(v.get('graine', 1))
    m = 'models/hunter/tubes/' + v['modele'] + '.mdl'
    R0 = TUBES[m][0]
    n, var = v.get('n', 8), v.get('var', 0.2)
    for q in range(n):
        a = q*360/n + v.get('decal', 11) + rnd.uniform(-v.get('jitter_angle', 4), v.get('jitter_angle', 4))
        h = v.get('h', 55)*rnd.uniform(1 - var, 1 + var)
        ra = math.radians(a); ph = v.get('phase', 0.0)
        lent = lambda x: 0.65*math.sin(2*x + ph) + 0.35*math.sin(3*x + 1.7*ph + 0.9)    # sinus lents (2 et 3 par tour)
        h = h*(1 + v.get('onde_h', 0.0)*lent(ra))
        r_onde = v.get('onde_r', 0.0)*lent(ra + 1.1)
        smax = (h + g - SOL_MAP)/R0
        s = smax if v['type'] == 'separe' else min(smax, rnd.uniform(*v.get('echelle', [0.95, 1.2])))
        tg = v.get('tangage', 5); tg = (tg if q % 2 else -tg)*rnd.uniform(0.7, 1.0) if v['type'] == 'separe' else rnd.uniform(-tg, tg)
        rl = v.get('roulis', 5)
        tube(v['nom'], ox, g, m, a, v.get('r', 880) + r_onde + rnd.uniform(-v.get('jitter_r', 20), v.get('jitter_r', 20)), h, s,
             tg, rnd.uniform(-rl, rl), rnd.uniform(-v.get('lacet', 0), v.get('lacet', 0)))

ECART = PARAMS.get('ecart', 4000.0)
VARS = []
for k, v in enumerate(PARAMS['variantes']):
    ox = k*ECART
    g = sol(ox, tete=(k == 0)); variante(v, ox, g); VARS.append((v['nom'], ox, g))
_tete = next(e for e in ents if e['note'] == 'sol')
assert all(e['pos'][2] >= _tete['pos'][2] - 1e-6 for e in ents), 'un prop a son origine sous la tête'
for v, ox, g in VARS:
    print(v, ':', sum(1 for c in COUCHE1 if c[0] == v), 'posés ; échelles', [e['scale'] for e in ents if e.get('scale') and abs(e['pos'][0] - ox) < 2000])

# ---------- hauteurs du sable (drapé couche 1 + couches 2 et 3), écrites dans le script ----------
def onde(a, ph):
    return 0.55*math.sin(3*a + ph) + 0.3*math.sin(7*a + 2.1*ph + 1) + 0.15*math.sin(13*a + 3.3*ph + 2)
def bosse(r, rc, H, w_in, w_out):
    w = w_in if r < rc else w_out
    return H*math.exp(-((r - rc)/w)**2)
def lointaines(r, a):
    z = 0.0
    for c in PARAMS.get('lointaines', []):   # {r, h, var_r, var_h, w_in, w_out, phase}
        ph = c.get('phase', 0.0)
        H = c['h']*(1 + c.get('var_h', 0.2)*onde(a, ph + 1.3))
        for (ad, prof, larg) in c.get('selles', []):          # selle : creux de crête centré sur ad (degrés)
            dd = (math.degrees(a) - ad + 180) % 360 - 180
            H *= 1 - prof*math.exp(-(dd/larg)**2)
        z = max(z, bosse(r, c['r'] + c.get('var_r', 30)*onde(a, ph), H, c.get('w_in', 160), c.get('w_out', 100)))
    return z
def dessus_tube(px, py, c, gonfle):
    _, ox, C0, d, Rt, demi = c
    R2 = Rt + gonfle
    # point (px, py, z) à distance R2 de l'axe : |w|² - (w.d)² = R2², w = Q - C0 ; quadratique en z
    wx, wy = px - C0[0], py - C0[1]
    A = 1 - d[2]**2
    wd0 = wx*d[0] + wy*d[1]
    B = -2*wd0*d[2]                     # termes en z (w_z = z - C0z) : |w|² = wx²+wy²+wz² ; (w.d) = wd0 + wz d2
    Cq = wx*wx + wy*wy - wd0*wd0 - R2*R2
    disc = B*B - 4*A*Cq
    if disc < 0: return None
    wz = (-B + math.sqrt(disc))/(2*A)
    t = wd0 + wz*d[2]
    if abs(t) > demi + gonfle*0.6: return None
    return C0[2] + wz
def softmax(a, b, k):
    m = max(a, b); return m + k*math.log(math.exp((a - m)/k) + math.exp((b - m)/k))
ANNEAUX = []
_r = 620.0
while _r <= 1750:
    ANNEAUX.append(_r); _r += 12 if _r < 1000 else (20 if _r < 1400 else 35)
SEG_D = 256
def grille(var, ox, g):
    tubes = [c for c in COUCHE1 if c[0] == var]
    n = len(ANNEAUX)
    Z1 = [[0.0]*SEG_D for _ in range(n)]
    for i, r in enumerate(ANNEAUX):
        for j in range(SEG_D):
            a = j/SEG_D*2*math.pi
            px, py = ox + r*math.cos(a), r*math.sin(a)
            for c in tubes:
                zt = dessus_tube(px, py, c, PARAMS.get('gonfle', 10.0))
                if zt is not None: Z1[i][j] = max(Z1[i][j], zt - g + 3.0)   # 3 u au-dessus du tube gonflé de 10 u
    # pied adouci : 5 passes de max(z, moyenne des 4 voisins) -> congé qui se fond dans le sol
    for _ in range(PARAMS.get('passes_pied', 5)):
        Z2 = [row[:] for row in Z1]
        for i in range(n):
            for j in range(SEG_D):
                v = [Z1[i][(j-1) % SEG_D], Z1[i][(j+1) % SEG_D], Z1[i-1][j] if i > 0 else 0.0, Z1[i+1][j] if i < n-1 else 0.0]
                Z2[i][j] = max(Z1[i][j], sum(v)/4)
        Z1 = Z2
    D = PARAMS.get('drape')
    if D:
        # sommet du tube et son rayon pour chaque angle, puis moyenne glissante en angle : plus de jonction ni de gouttière
        hm = [max(Z1[i][j] for i in range(n)) for j in range(SEG_D)]
        rm = [ANNEAUX[max(range(n), key=lambda i: Z1[i][j])] for j in range(SEG_D)]
        k = D.get('lissage', 8)
        def glisse(t, poids):
            out = []
            for j in range(SEG_D):
                sw = sum(poids[(j+u) % SEG_D] for u in range(-k, k+1)) or 1
                out.append(sum(t[(j+u) % SEG_D]*poids[(j+u) % SEG_D] for u in range(-k, k+1))/sw)
            return out
        hl = glisse([max(h, 1.0) for h in hm], [1.0]*SEG_D)
        hl = [max(a, b*D.get('plancher', 0.8)) for a, b in zip(hl, hm)]
        rl = glisse(rm, [max(h, 1.0) for h in hm])
        for i, r in enumerate(ANNEAUX):
            for j in range(SEG_D):
                b = bosse(r, rl[j], hl[j] + D.get('sur', 8), D.get('w_in', 120), D.get('w_out', 95))
                t = min(1.0, max(0.0, (r - ANNEAUX[0])/D.get('raccord', 140))); b *= t*t*(3 - 2*t)   # raccord au sol du creux
                Z1[i][j] = max(b, Z1[i][j])
    assert max(Z1[0]) < 0.5, 'le drapé de la couche 1 touche le bord intérieur'
    return [[round(max(Z1[i][j], lointaines(ANNEAUX[i], j/SEG_D*2*math.pi)), 1) for j in range(SEG_D)] for i in range(n)]
LUA_DONNEES = []
for v, ox, g in VARS:
    L = grille(v, ox, g)
    LUA_DONNEES.append((v, ox, L))
FX = []

# ====================== CONTRÔLES ======================
import glob as _g
# modèles PHX qui existent : spawnlist de GMod (GMOD_DIR = dossier garrysmod), sinon bornes_modeles.json (BORNES_JSON)
import os as _os
_S = set()
_gmod = _os.environ.get('GMOD_DIR', 'C:/SteamLibrary/steamapps/common/GarrysMod/garrysmod')
for _f in _g.glob(_os.path.join(_gmod, 'settings', 'spawnlist_default', '*.txt')):
    _S |= set(re.findall(r'models/[a-z0-9_/]+\.mdl', open(_f, errors='ignore').read().lower()))
if not _S:
    _b = _os.environ.get('BORNES_JSON', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'bornes_modeles.json'))
    if _os.path.exists(_b):
        _S = set(json.load(open(_b, encoding='utf-8')))
assert _S, 'ni spawnlist GMod (GMOD_DIR) ni bornes_modeles.json (BORNES_JSON) : impossible de vérifier les modèles PHX'
_bad = sorted({e['model'] for e in ents if 'hunter' in e['model'] and e['model'].lower() not in _S})
assert not _bad, f'modèles PHX inexistants : {_bad}'
assert not FX, 'gmod_light / gmod_lamp / gmod_emitter bloqués sur EVO'
_n = len(ents) + len(FX)
assert _n <= 400, f'{_n} entités : la limite est 400'
HEAD_NOTE = 'sol'   # l'entité posée sur le sol au collage (le point le plus bas du build)
assert any(e['note'] == HEAD_NOTE for e in ents)
json.dump(dict(ents=ents, fx=FX, head=HEAD_NOTE), open('scene.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(_n, 'entités', Counter(e['kind'] for e in ents), Counter(f['kind'] for f in FX))

# données du script : un anneau par ligne, hauteurs au-dessus du sol extérieur
NL = chr(10)
with open('dunes_donnees.lua', 'w', encoding='utf-8') as f:
    f.write('-- généré par build_p2.py : ne pas éditer' + NL)
    f.write('return { anneaux = { %s }, seg = %d, fondu = { %g, %g }, variantes = {' % (', '.join('%g' % r for r in ANNEAUX), SEG_D, *PARAMS.get('fondu', [1350, 1750])) + NL)
    for v, ox, L in LUA_DONNEES:
        f.write('  { nom = "%s", ox = %g, z = {' % (v, ox) + NL)
        for row in L: f.write('    "%s",' % ' '.join('%g' % z for z in row) + NL)
        f.write('  } },' + NL)
    f.write('} }' + NL)
print('dunes_donnees.lua :', len(ANNEAUX), 'anneaux x', SEG_D)

# ---------- sorties du générateur : script, dupe, vues ----------
import subprocess, os
_ICI = os.path.dirname(os.path.abspath(__file__))
_modele = open(os.path.join(_ICI, 'essai_dunes_lointaines_modele.lua'), encoding='utf-8').read()
_d = open('dunes_donnees.lua', encoding='utf-8').read().split(NL, 1)[1].strip()
assert _d.startswith('return ')
open('essai_dunes_lointaines.lua', 'w', encoding='utf-8').write(_modele.replace('local DONNEES = nil --[[DONNEES]]', 'local DONNEES = ' + _d[len('return '):]))
NOM = PARAMS.get('nom', 'a2-dunes')
subprocess.run([sys.executable, os.path.join(_ICI, 'encode.py'), NOM], check=True)
os.replace('build.txt', NOM + '.txt')
_copies = 'a2_sable_copies ' + ' '.join('%g' % ox for _, ox, _ in VARS)
V, RAYS = [], []
for k, (v, ox, g) in enumerate(VARS):
    V += [dict(nom=f'{v}_arrivee_ext', pos=[ox-600, 0, 63], vise=[ox-1600, 0, 80], **({'commande': _copies} if k == 0 else {})),
          dict(nom=f'{v}_assis_ext', pos=[ox-280, 0, -24], vise=[ox-1300, 0, 80]),
          dict(nom=f'{v}_centre_horizon', pos=[ox, 0, 4], vise=[ox, 1300, 60]),
          dict(nom=f'{v}_loin34', pos=[ox-2300, -2300, 1100], vise=[ox, 0, 0])]
    # joueur qui marche sur la dune : œil 64 u au-dessus du sable drapé (tube + 13 u)
    c = next(c for c in COUCHE1 if c[0] == v)
    C0, d, Rt = c[2], c[3], c[4]
    s = Rt/95.2
    haut_coll = C0[2] + 95.2          # si la collision garde le rayon de base
    haut_vis = C0[2] + Rt
    tx, ty = d[0], d[1]
    _L = next(L for vv, oo, L in LUA_DONNEES if vv == v)
    _px, _py = C0[0] - tx*150 - ox, C0[1] - ty*150
    _i = min(range(len(ANNEAUX)), key=lambda i: abs(ANNEAUX[i] - math.hypot(_px, _py)))
    _j = int(round((math.atan2(_py, _px) % (2*math.pi))/(2*math.pi)*SEG_D)) % SEG_D
    z_sable = g + 2.07 + _L[_i][_j]
    V.append(dict(nom=f'{v}_marche_dune', pos=[C0[0] - tx*150, C0[1] - ty*150, z_sable + 64], vise=[C0[0] + tx*400, C0[1] + ty*400, z_sable + 40]))
    RAYS.append({'nom': f'{v}_tube1_x{s:.3f}_vis{haut_vis:.1f}_coll{haut_coll:.1f}', 'de': [C0[0], C0[1], 400], 'cibles': [[C0[0], C0[1], -100]]})
json.dump({'vues_auto': False, 'vues': V, 'rayons': RAYS}, open('vues_' + NOM + '.json', 'w'), indent=0)
print('sorties :', NOM + '.txt', 'essai_dunes_lointaines.lua', 'vues_' + NOM + '.json')
