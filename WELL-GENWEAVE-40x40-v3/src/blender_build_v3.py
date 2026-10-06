# -*- coding: utf-8 -*-
"""WELL-GENWEAVE 40x40 v3 — Blender model builder (TRUNK + BRANCH scheme).
Reads WELL-GENWEAVE-40x40-v3-geo.json (same box model as the CAD set: X=East, Y=North, road on North, mm) and builds
one mesh per (category, material). Units: metres."""
import bpy, json, math, os
from mathutils import Vector
D = r'C:\Users\User\Downloads\WELL\WELL-GENWEAVE-40x40\v3'
J = json.load(open(os.path.join(D, 'WELL-GENWEAVE-40x40-v3-geo.json'), encoding='utf-8'))
# ---- clean scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
root = bpy.data.collections.new('GENWEAVE_v3'); sc.collection.children.link(root)
COLS = {}
def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); root.children.link(c); COLS[name] = c
    return COLS[name]
# ---- materials
MATS = {'stone': ((0.78, 0.72, 0.62), 0.85, 0, 0), 'render': ((0.93, 0.92, 0.89), 0.6, 0, 0), 'plaster': ((0.9, 0.9, 0.88), 0.7, 0, 0),
        'concrete': ((0.72, 0.71, 0.68), 0.8, 0, 0), 'glass': ((0.8, 0.9, 0.95), 0.02, 0, 1), 'louver': ((0.33, 0.37, 0.4), 0.4, 0.6, 0),
        'timber': ((0.42, 0.26, 0.13), 0.55, 0, 0), 'door': ((0.55, 0.38, 0.22), 0.5, 0, 0), 'greenroof': ((0.22, 0.4, 0.14), 1.0, 0, 0),
        'paving': ((0.7, 0.68, 0.64), 0.8, 0, 0), 'lawn': ((0.28, 0.48, 0.17), 1.0, 0, 0), 'water': ((0.08, 0.36, 0.45), 0.03, 0, 0.7),
        'deck': ((0.5, 0.33, 0.18), 0.6, 0, 0), 'gravel': ((0.76, 0.74, 0.69), 0.95, 0, 0), 'asphalt': ((0.14, 0.14, 0.14), 0.9, 0, 0),
        'pv': ((0.04, 0.06, 0.14), 0.15, 0.4, 0), 'leaf': ((0.17, 0.36, 0.12), 0.9, 0, 0), 'bark': ((0.25, 0.18, 0.12), 0.9, 0, 0)}
def mat(n):
    m = bpy.data.materials.get('GW3_' + n)
    if m: return m
    base, rough, metal, trans = MATS.get(n, ((0.8, 0.8, 0.8), 0.6, 0, 0))
    m = bpy.data.materials.new('GW3_' + n); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans:
        for k in ('Transmission Weight', 'Transmission'):
            if k in b.inputs: b.inputs[k].default_value = trans
        b.inputs['IOR'].default_value = 1.45 if n == 'glass' else 1.33
    m.diffuse_color = (*base, 0.35 if n == 'glass' else 1)
    return m
# ---- boxes grouped
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
    col({'wall': 'Walls', 'band': 'Walls', 'glass': 'Glazing', 'door': 'Doors', 'rail': 'Glazing', 'slab': 'Structure', 'roof': 'Roof', 'groof': 'Roof',
         'parapet': 'Roof', 'column': 'Structure', 'fin': 'Skin_Cactus', 'shade': 'Skin_Cactus', 'chimney': 'Termite_Chimney', 'stair': 'Structure',
         'pv': 'Roof', 'plinth': 'Structure'}.get(cat, 'Site')).objects.link(ob)
# ---- trees
for (x, y, r, h) in J['trees']:
    x, y, r, h = x / 1000, y / 1000, r / 1000, h / 1000
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18 + r * 0.03, depth=h * 0.55, location=(x, y, h * 0.275))
    t = bpy.context.object; t.data.materials.append(mat('bark')); t.name = 'tree_trunk'
    for c in t.users_collection: c.objects.unlink(t)
    col('Trees').objects.link(t)
    for k, (dx, dy, dz, s) in enumerate(((0, 0, 0.62, 1.0), (r * .35, r * .2, 0.55, .7), (-r * .3, -r * .25, 0.58, .75))):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * s, location=(x + dx, y + dy, h * dz + r * 0.3))
        c_ = bpy.context.object; c_.scale = (1, 1, 0.62); c_.data.materials.append(mat('leaf')); c_.name = 'tree_canopy'
        for c in c_.users_collection: c.objects.unlink(c_)
        col('Trees').objects.link(c_)
# ---- light + world
sun = bpy.data.lights.new('Sun_BKK', 'SUN'); sun.energy = 4.2; sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun_BKK', sun); root.objects.link(so)
so.rotation_euler = (math.radians(42), 0, math.radians(-140))     # afternoon sun from SW
w = sc.world or bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.62, 0.74, 0.88, 1); bg.inputs[1].default_value = 0.9
# ---- cameras
def cam(name, loc, tgt, lens=24):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_end = 500
    o = bpy.data.objects.new(name, c); col('Cameras').objects.link(o)
    o.location = Vector(loc); o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o
cam('CAM_1_Aerial_SE', (58, -24, 34), (20, 18, 2), 30)
cam('CAM_2_Garden_South', (11.0, 1.8, 1.7), (24, 14, 5.5), 18)
cam('CAM_3_Street_North', (8, 47, 1.7), (23, 32, 4.5), 20)
cam('CAM_4_Aerial_NW', (-16, 62, 34), (20, 18, 2), 30)
cam('CAM_5_Termite_Court', (31.8, 16.6, 1.75), (19, 21.5, 5.5), 16)
cam('CAM_6_Living_to_Pool', (25.8, 15.2, 2.2), (20, 4, 1.6), 16)
sc.camera = bpy.data.objects['CAM_1_Aerial_SE']
r = sc.render; r.resolution_x, r.resolution_y = 1800, 1100; r.resolution_percentage = 100
try:
    sc.eevee.taa_render_samples = 48
    sc.eevee.use_raytracing = True
except Exception: pass
sc.view_settings.view_transform = 'AgX' if 'AgX' in [v.identifier for v in type(sc.view_settings).bl_rna.properties['view_transform'].enum_items] else 'Filmic'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'WELL-GENWEAVE-40x40-v3-model.blend'))
result = {'objects': len(bpy.data.objects), 'groups': len(G), 'saved': bpy.data.filepath}
