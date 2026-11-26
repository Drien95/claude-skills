# Encodeur AdvDupe2 (révision 5) — usage : python3 encode.py "Nom du build"
import json, struct, lzma, time
import sys
NAME = sys.argv[1] if len(sys.argv) > 1 else 'Mon build'
D = json.load(open('scene.json')); ents = D['ents']; FX = D['fx']
# l'entité de tête est posée sur le sol au collage : prendre la plus basse
head_i = next(i for i, e in enumerate(ents) if e.get('note') == D['head'])
ents.insert(0, ents.pop(head_i))
class Vec(tuple): pass
class Ang(tuple): pass
def ser(o, out):
    if isinstance(o, bool): out.append(bytes([253 if o else 252]))
    elif isinstance(o, Vec): out.append(bytes([250]) + struct.pack('<3d', *o))
    elif isinstance(o, Ang): out.append(bytes([249]) + struct.pack('<3d', *o))
    elif isinstance(o, (int, float)): out.append(bytes([251]) + struct.pack('<d', float(o)))
    elif isinstance(o, str):
        b = o.encode('utf-8')
        out.append((bytes([len(b)]) if len(b) < 246 else bytes([248]) + struct.pack('<I', len(b))) + b)
    elif isinstance(o, dict):
        out.append(bytes([255]))
        for k, v in o.items(): ser(k, out); ser(v, out)
        out.append(bytes([246]))
    else: raise TypeError(type(o))
hp = ents[0]['pos']
def rel(p): return Vec(round(p[j] - hp[j], 4) for j in range(3))
# pas de clé Frozen : dans AD2, Frozen = true veut dire « était mobile », et le collage le dégèle
def phys(p, a): return {0: {'Pos': rel(p), 'Angle': Ang(a)}}
E = {}; i = 0
for e in ents:
    i += 1
    if e['kind'] == 'effect':
        # CollisionGroup 1 (debris) : la petite boîte physique du prop_effect ne bloque plus les joueurs
        E[i] = {'Class': 'prop_effect', 'Model': e['model'], 'PhysicsObjects': phys(e['pos'], e['ang']), 'CollisionGroup': 1}
    else:
        E[i] = {'Class': 'prop_physics', 'Model': e['model'], 'PhysicsObjects': phys(e['pos'], e['ang'])}
        if e['kind'] == 'prop':
            r, g, b = e['color']
            E[i]['EntityMods'] = {'colour': {'Color': {'r': r, 'g': g, 'b': b, 'a': 255}, 'RenderMode': 0, 'RenderFX': 0},
                                  'material': {'MaterialOverride': e['mat']}}
            if e.get('cg'): E[i]['CollisionGroup'] = e['cg']
    if e.get('skin'): E[i]['Skin'] = e['skin']
    if e.get('scale'): E[i]['ModelScale'] = e['scale']   # evo_taille (x0,1 à x5), remis par duplicator.DoGeneric
for l in FX:
    i += 1
    ang = l.get('ang', (0, 0, 0))
    if l['kind'] == 'light':
        r, g, b = l['col']
        E[i] = {'Class': 'gmod_light', 'Model': 'models/maxofs2d/light_tubular.mdl', 'PhysicsObjects': phys(l['pos'], ang),
                'lightr': r, 'lightg': g, 'lightb': b, 'Brightness': l['bright'], 'Size': l['size'],
                'Toggle': False, 'on': True, 'KeyDown': 37}
        E[i]['EntityMods'] = {'colour': {'Color': {'r': r, 'g': g, 'b': b, 'a': 0}, 'RenderMode': 1, 'RenderFX': 0}}
    elif l['kind'] == 'lamp':
        r, g, b = l['col']
        E[i] = {'Class': 'gmod_lamp', 'Model': 'models/maxofs2d/lamp_projector.mdl', 'PhysicsObjects': phys(l['pos'], ang),
                'r': r, 'g': g, 'b': b, 'KeyDown': 38, 'Toggle': False, 'Texture': 'effects/flashlight001',
                'fov': l['fov'], 'distance': l['dist'], 'brightness': l['bright'], 'on': True}
        E[i]['EntityMods'] = {'colour': {'Color': {'r': r, 'g': g, 'b': b, 'a': 0}, 'RenderMode': 1, 'RenderFX': 0}}
    else:
        E[i] = {'Class': 'gmod_emitter', 'Model': 'models/props_lab/tpplug.mdl', 'PhysicsObjects': phys(l['pos'], ang),
                'key': 39, 'delay': l['delay'], 'toggle': True, 'effect': l['effect'], 'starton': True,
                'nocollide': True, 'scale': l['scale'],
                'EntityMods': {'colour': {'Color': {'r': 255, 'g': 255, 'b': 255, 'a': 0}, 'RenderMode': 1, 'RenderFX': 0}}}
for j in range(len(ents) + 1, i + 1):
    E[j]['CollisionGroup'] = 1   # lumières, projecteurs, émetteurs : on passe au travers
dupe = {'Entities': E, 'Constraints': {}, 'HeadEnt': {'Index': 1, 'Pos': Vec(hp), 'Z': 1.5},
        'Description': NAME}
assert not {v['Class'] for v in E.values()} & {'gmod_light', 'gmod_lamp', 'gmod_emitter', 'prop_effect'}, 'classe bloquée sur EVO'
out = []; ser(dupe, out); raw = b''.join(out)
comp = bytearray(lzma.compress(raw, format=lzma.FORMAT_ALONE, filters=[{'id': lzma.FILTER_LZMA1, 'dict_size': 1 << 20}]))
comp[5:13] = struct.pack('<Q', len(raw)); comp = bytes(comp)
info = {'name': NAME, 'time': time.strftime('%I:%M %p'), 'date': time.strftime('%d %B %Y'),
        'timezone': '+0100', 'check': '\r\n\t\n', 'size': str(len(comp))}
infos = ''.join(f'{k}\1{v}\1' for k, v in info.items()) + '\2'
data = b'AD2F' + bytes([5]) + b'\n' + infos.encode('utf-8') + b'\n' + comp
open('build.txt', 'wb').write(data)
print(len(E), 'entités', len(raw), len(comp), len(data))
