# -*- coding: utf-8 -*-
"""WELL G-BEACH 30x30 — Blender model builder.
Slab block on pilotis + brick cylinder core + west openwork-brick lattice + east balconies + roof terraces.
Reads WELL-GBEACH-30x30-geo.json (same model as the CAD set, X=East, Y=North, road on North, mm)."""
import bpy, bmesh, json, math, os
from mathutils import Vector
D = r'C:\Users\User\Downloads\WELL\WELL-GBEACH-30x30'
J = json.load(open(os.path.join(D, 'WELL-GBEACH-30x30-geo.json'), encoding='utf-8'))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
root = bpy.data.collections.new('GBEACH_30x30'); sc.collection.children.link(root)
COLS = {}
def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); root.children.link(c); COLS[name] = c
    return COLS[name]
MATS = {'stone': ((0.78, 0.72, 0.62), 0.85, 0, 0), 'render': ((0.94, 0.93, 0.9), 0.6, 0, 0), 'plaster': ((0.9, 0.9, 0.88), 0.7, 0, 0),
        'concrete': ((0.74, 0.73, 0.7), 0.8, 0, 0), 'glass': ((0.8, 0.9, 0.95), 0.02, 0, 1), 'louver': ((0.33, 0.37, 0.4), 0.4, 0.6, 0),
        'timber': ((0.42, 0.26, 0.13), 0.55, 0, 0), 'door': ((0.55, 0.38, 0.22), 0.5, 0, 0), 'greenroof': ((0.22, 0.4, 0.14), 1.0, 0, 0),
        'paving': ((0.7, 0.68, 0.64), 0.8, 0, 0), 'lawn': ((0.28, 0.48, 0.17), 1.0, 0, 0), 'water': ((0.08, 0.36, 0.45), 0.03, 0, 0.7),
        'deck': ((0.5, 0.33, 0.18), 0.6, 0, 0), 'asphalt': ((0.14, 0.14, 0.14), 0.9, 0, 0), 'brick': ((0.55, 0.25, 0.15), 0.85, 0, 0),
        'steel': ((0.35, 0.37, 0.4), 0.4, 0.8, 0), 'pv': ((0.04, 0.06, 0.14), 0.15, 0.4, 0), 'leaf': ((0.17, 0.36, 0.12), 0.9, 0, 0),
        'bark': ((0.25, 0.18, 0.12), 0.9, 0, 0)}
def mat(n):
    m = bpy.data.materials.get('GB4_' + n)
    if m: return m
    base, rough, metal, trans = MATS.get(n, ((0.8, 0.8, 0.8), 0.6, 0, 0))
    m = bpy.data.materials.new('GB4_' + n); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans:
        for k in ('Transmission Weight', 'Transmission'):
            if k in b.inputs: b.inputs[k].default_value = trans
        b.inputs['IOR'].default_value = 1.45 if n == 'glass' else 1.33
    m.diffuse_color = (*base, 0.35 if n == 'glass' else 1)
    return m
GROUP = {'wall': 'Walls', 'band': 'Walls', 'glass': 'Glazing', 'skylight': 'Glazing', 'door': 'Doors', 'rail': 'Glazing', 'slab': 'Structure',
         'roof': 'Roof', 'groof': 'Roof', 'parapet': 'Roof', 'column': 'Structure_Pilotis', 'lattice': 'Brick_Lattice', 'pergola': 'Roof',
         'stair': 'Stairs', 'cstair': 'Stairs', 'pv': 'Roof', 'plinth': 'Structure'}
G = {}
for x0, y0, z0, x1, y1, z1, mt, cat in J['boxes']:
    G.setdefault((cat, mt), []).append((x0 / 1000, y0 / 1000, z0 / 1000, x1 / 1000, y1 / 1000, z1 / 1000))
FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
for (cat, mt), bl in G.items():
    V, F = [], []
    for (x0, y0, z0, x1, y1, z1) in bl:
        k = len(V)
        V += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        F += [tuple(k + i for i in f) for f in FACES]
    me = bpy.data.meshes.new('%s_%s' % (cat, mt)); me.from_pydata(V, [], F); me.update()
    ob = bpy.data.objects.new('%s_%s' % (cat, mt), me); ob.data.materials.append(mat(mt))
    col(GROUP.get(cat, 'Site')).objects.link(ob)
# ---- brick cylinder core: ring segments per floor, door gaps left open
C = J['core']; cx0, cy0 = C['c'][0] / 1000, C['c'][1] / 1000; Ro = C['r'] / 1000; Ri = Ro - 0.2
ffl = [z / 1000 for z in C['ffl']] + [C['top'] / 1000]
gw = math.degrees(1.0 / (Ro - 0.1)) / 2
bm = bmesh.new()
N = 96
for k in range(5):
    z0, z1 = ffl[k], ffl[k + 1]
    gaps = C['gaps'].get(str(k + 1), []) if k < 4 else []
    for i in range(N):
        a0 = 360 * i / N; a1 = 360 * (i + 1) / N; am = (a0 + a1) / 2
        if any(abs(((am - g + 180) % 360) - 180) < gw for g in gaps): continue
        p = lambda r, a, z: bm.verts.new((cx0 + r * math.cos(math.radians(a)), cy0 + r * math.sin(math.radians(a)), z))
        o0b, o1b, o0t, o1t = p(Ro, a0, z0), p(Ro, a1, z0), p(Ro, a0, z1), p(Ro, a1, z1)
        i0b, i1b, i0t, i1t = p(Ri, a0, z0), p(Ri, a1, z0), p(Ri, a0, z1), p(Ri, a1, z1)
        for f in ((o0b, o1b, o1t, o0t), (i1b, i0b, i0t, i1t), (o0t, o1t, i1t, i0t), (o1b, o0b, i0b, i1b), (o0b, o0t, i0t, i0b), (o1b, i1b, i1t, o1t)):
            bm.faces.new(f)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
me = bpy.data.meshes.new('core_cylinder_brick'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('Core_Cylinder_Brick', me); ob.data.materials.append(mat('brick')); col('Core_Cylinder').objects.link(ob)
cx, cy = J['core']['c'][0] / 1000, J['core']['c'][1] / 1000
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=J['core']['r'] / 1000 - 0.05, depth=0.12, location=(cx, cy, J['core']['top'] / 1000 - 0.06))
cap = bpy.context.object; cap.name = 'Core_Skylight'; cap.data.materials.append(mat('glass'))
for c in cap.users_collection: c.objects.unlink(cap)
col('Core_Cylinder').objects.link(cap)
# ---- trees
for (x, y, r, h) in J['trees']:
    x, y, r, h = x / 1000, y / 1000, r / 1000, h / 1000
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15 + r * 0.03, depth=h * 0.55, location=(x, y, h * 0.275))
    t = bpy.context.object; t.data.materials.append(mat('bark'))
    for c in t.users_collection: c.objects.unlink(t)
    col('Trees').objects.link(t)
    for (dx, dy, dz, s) in ((0, 0, 0.62, 1.0), (r * .35, r * .2, 0.55, .7), (-r * .3, -r * .25, 0.58, .75)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * s, location=(x + dx, y + dy, h * dz + r * 0.3))
        c_ = bpy.context.object; c_.scale = (1, 1, 0.62); c_.data.materials.append(mat('leaf'))
        for c in c_.users_collection: c.objects.unlink(c_)
        col('Trees').objects.link(c_)
# ---- light, world, cameras
sun = bpy.data.lights.new('Sun_BKK', 'SUN'); sun.energy = 6.0; sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun_BKK', sun); root.objects.link(so)
so.rotation_euler = (math.radians(48), 0, math.radians(-135))
w = sc.world or bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.62, 0.74, 0.88, 1); bg.inputs[1].default_value = 0.45
def cam(name, loc, tgt, lens=24):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_end = 500
    o = bpy.data.objects.new(name, c); col('Cameras').objects.link(o)
    o.location = Vector(loc); o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cam('CAM_1_Aerial_SE', (48, -20, 30), (14, 15, 5), 34)
cam('CAM_2_Garden_East', (29.6, 27.5, 2.2), (19, 8, 6.5), 20)
cam('CAM_3_Street_North', (24, 37.5, 1.7), (13, 22, 6.5), 20)
cam('CAM_4_Aerial_NW', (-18, 50, 30), (14, 15, 5), 34)
cam('CAM_5_West_Lattice', (-6, 4, 2.5), (8, 16, 7), 22)
cam('CAM_6_Aerial_SW', (-16, -14, 20), (14, 15, 5), 32)
sc.camera = bpy.data.objects['CAM_1_Aerial_SE']
r = sc.render; r.resolution_x, r.resolution_y = 1800, 1100; r.resolution_percentage = 100
try:
    sc.eevee.taa_render_samples = 48; sc.eevee.use_raytracing = True
except Exception: pass
try:
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'WELL-GBEACH-30x30-model.blend'))
result = {'objects': len(bpy.data.objects), 'groups': len(G), 'saved': bpy.data.filepath}
