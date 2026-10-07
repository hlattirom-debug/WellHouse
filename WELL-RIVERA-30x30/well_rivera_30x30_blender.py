# -*- coding: utf-8 -*-
"""WELL RIVERA 30x30 (concept: Rivera Paradise, AtelierM, Buenos Aires 2026) — Blender model builder.
Ring of four wings around an open courtyard, stepping down in a spiral (F1 SWNE, F2 SNE, F3 SE, F4 S + E deck):
every roof is a garden, an exterior "helix" stair climbs the roof gardens, exposed-brick side walls, brick barrel vault over the foyer,
hanging planters on slab edges, reflecting pool in the courtyard.
Reads WELL-RIVERA-30x30-geo.json (same model as the CAD set, X=East, Y=North, road on North, mm): boxes + X-prisms."""
import bpy, bmesh, json, math, os
from mathutils import Vector
D = r'C:\Users\User\Downloads\WELL\WELL-RIVERA-30x30'
GEO = os.path.join(D, 'WELL-RIVERA-30x30-geo.json')
J = json.load(open(GEO, encoding='utf-8'))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
root = bpy.data.collections.new('RIVERA_30x30'); sc.collection.children.link(root)
COLS = {}
def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); root.children.link(c); COLS[name] = c
    return COLS[name]
MATS = {'stone': ((0.74, 0.69, 0.6), 0.85, 0, 0), 'render': ((0.94, 0.93, 0.9), 0.6, 0, 0), 'plaster': ((0.9, 0.9, 0.88), 0.7, 0, 0),
        'calce': ((0.9, 0.85, 0.77), 0.9, 0, 0), 'concrete': ((0.72, 0.71, 0.68), 0.8, 0, 0), 'glass': ((0.8, 0.9, 0.95), 0.02, 0, 1),
        'uglass': ((0.84, 0.92, 0.9), 0.35, 0, 0.6), 'louver': ((0.33, 0.37, 0.4), 0.4, 0.6, 0), 'timber': ((0.42, 0.26, 0.13), 0.55, 0, 0),
        'door': ((0.55, 0.38, 0.22), 0.5, 0, 0), 'greenroof': ((0.22, 0.4, 0.14), 1.0, 0, 0), 'paving': ((0.7, 0.68, 0.64), 0.8, 0, 0),
        'lawn': ((0.28, 0.48, 0.17), 1.0, 0, 0), 'water': ((0.08, 0.36, 0.45), 0.03, 0, 0.7), 'deck': ((0.5, 0.33, 0.18), 0.6, 0, 0),
        'asphalt': ((0.14, 0.14, 0.14), 0.9, 0, 0), 'brick': ((0.47, 0.2, 0.12), 0.85, 0, 0), 'terracotta': ((0.7, 0.36, 0.18), 0.75, 0, 0),
        'steel': ((0.35, 0.37, 0.4), 0.4, 0.8, 0), 'pv': ((0.04, 0.06, 0.14), 0.15, 0.4, 0), 'leaf': ((0.17, 0.36, 0.12), 0.9, 0, 0),
        'bark': ((0.25, 0.18, 0.12), 0.9, 0, 0), 'timberclad': ((0.66, 0.47, 0.28), 0.65, 0, 0), 'glulam': ((0.72, 0.52, 0.31), 0.55, 0, 0),
        'roofmetal': ((0.78, 0.79, 0.8), 0.35, 0.7, 0), 'gravel': ((0.75, 0.73, 0.68), 0.95, 0, 0),
        'brickpave': ((0.6, 0.36, 0.28), 0.85, 0, 0), 'leaf2': ((0.36, 0.55, 0.25), 0.9, 0, 0)}
def mat(n):
    m = bpy.data.materials.get('RV7_' + n)
    if m: return m
    base, rough, metal, trans = MATS.get(n, ((0.8, 0.8, 0.8), 0.6, 0, 0))
    m = bpy.data.materials.new('RV7_' + n); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans:
        for k in ('Transmission Weight', 'Transmission'):
            if k in b.inputs: b.inputs[k].default_value = trans
        b.inputs['IOR'].default_value = 1.45 if n in ('glass', 'uglass') else 1.33
    m.diffuse_color = (*base, 0.35 if n == 'glass' else 1)
    return m
GROUP = {'wall': 'Walls', 'band': 'Walls', 'glass': 'Glazing', 'skylight': 'Glazing', 'door': 'Doors', 'rail': 'Glazing', 'slab': 'Structure',
         'roof': 'Roof', 'groof': 'Roof', 'parapet': 'Roof', 'column': 'Structure', 'lattice': 'Terracotta_Screen', 'pergola': 'Roof',
         'stair': 'Stairs', 'pv': 'Roof', 'plinth': 'Structure', 'exo': 'Timber_Exoskeleton', 'rafter': 'Timber_Exoskeleton',
         'gutter': 'Roof', 'ridge': 'Roof', 'helix': 'Helix_Stairs', 'hang': 'Hanging_Gardens', 'trough': 'Hanging_Gardens',
         'greenwall': 'Hanging_Gardens', 'planter': 'Roof_Gardens', 'vault': 'Brick_Vault', 'court': 'Courtyard', 'pool': 'Courtyard'}
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

def link(ob, cname):
    for c in ob.users_collection: c.objects.unlink(ob)
    col(cname).objects.link(ob)

# ---- X-prisms: sloped roof planes, skylight, PV, raked gable walls, raking struts, rafters, gable lattice
PG = {}
for p in J['prisms']:
    PG.setdefault((p['c'], p['m']), []).append(p)
for (cat, mt), pl in PG.items():
    bm = bmesh.new()
    for p in pl:
        x0, x1 = p['x'][0] / 1000, p['x'][1] / 1000
        pts = [(y / 1000, z / 1000) for y, z in p['p']]
        clean = []
        for q in pts:
            if not clean or abs(q[0] - clean[-1][0]) + abs(q[1] - clean[-1][1]) > 1e-4: clean.append(q)
        if len(clean) > 2 and abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-4: clean.pop()
        if len(clean) < 3: continue
        area = sum(clean[i][0] * clean[(i + 1) % len(clean)][1] - clean[(i + 1) % len(clean)][0] * clean[i][1] for i in range(len(clean)))
        if area < 0: clean = clean[::-1]
        A = [bm.verts.new((x0, y, z)) for y, z in clean]
        B = [bm.verts.new((x1, y, z)) for y, z in clean]
        n = len(clean)
        try:
            bm.faces.new(A[::-1]); bm.faces.new(B)
        except Exception: pass
        for i in range(n):
            j = (i + 1) % n
            try: bm.faces.new((A[i], A[j], B[j], B[i]))
            except Exception: pass
    me = bpy.data.meshes.new('P_%s_%s' % (cat, mt)); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('P_%s_%s' % (cat, mt), me); ob.data.materials.append(mat(mt))
    col(GROUP.get(cat, 'Site')).objects.link(ob)

# ---- trees
for (x, y, r, h) in J['trees']:
    x, y, r, h = x / 1000, y / 1000, r / 1000, h / 1000
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15 + r * 0.03, depth=h * 0.55, location=(x, y, h * 0.275))
    t = bpy.context.object; t.data.materials.append(mat('bark')); link(t, 'Trees')
    for (dx, dy, dz, s) in ((0, 0, 0.62, 1.0), (r * .35, r * .2, 0.55, .7), (-r * .3, -r * .25, 0.58, .75)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * s, location=(x + dx, y + dy, h * dz + r * 0.3))
        c_ = bpy.context.object; c_.scale = (1, 1, 0.62); c_.data.materials.append(mat('leaf')); link(c_, 'Trees')
# ---- light, world, cameras
sun = bpy.data.lights.new('Sun_BKK', 'SUN'); sun.energy = 6.0; sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun_BKK', sun); root.objects.link(so)
so.rotation_euler = (math.radians(48), 0, math.radians(-150))
w = sc.world or bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.62, 0.74, 0.88, 1); bg.inputs[1].default_value = 0.45
def cam(name, loc, tgt, lens=24):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_end = 500
    o = bpy.data.objects.new(name, c); col('Cameras').objects.link(o)
    o.location = Vector(loc); o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cam('CAM_1_Aerial_SE', (48, -18, 32), (15, 14, 5), 34)
cam('CAM_2_Aerial_NW', (-20, 48, 30), (15, 14, 5), 34)
cam('CAM_3_Courtyard', (11.6, 12.6, 1.6), (17.5, 18.0, 7.5), 16)
cam('CAM_4_Garden_South', (21.0, 0.6, 1.7), (11.0, 10.0, 6.5), 18)
cam('CAM_5_Roof_Garden_W', (5.2, 12.4, 5.4), (20.0, 17.5, 9.5), 18)
cam('CAM_6_Street_North', (20.0, 38.5, 1.7), (12.0, 21.0, 5.0), 20)
sc.camera = bpy.data.objects['CAM_1_Aerial_SE']
r = sc.render; r.resolution_x, r.resolution_y = 1800, 1100; r.resolution_percentage = 100
try:
    sc.eevee.taa_render_samples = 48; sc.eevee.use_raytracing = True
except Exception: pass
try:
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'WELL-RIVERA-30x30-model.blend'))
result = {'objects': len(bpy.data.objects), 'groups': len(G), 'prism_groups': len(PG), 'saved': bpy.data.filepath}
