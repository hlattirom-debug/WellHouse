# -*- coding: utf-8 -*-
"""WELL KILN 30x30 (concept: Intrinsic / Chain10) — Blender model builder.
E-W block (calce lime plaster over a firebrick base) + brick dome foyer ("kiln") + brick stair tower ("chimney")
+ terracotta vault over the F4 family lounge with an arched glazed "kiln mouth" + west terracotta baguette screen + U-glass loggia.
Reads WELL-KILN-30x30-geo.json (same model as the CAD set, X=East, Y=North, road on North, mm)."""
import bpy, bmesh, json, math, os
from mathutils import Vector
D = r'C:\Users\User\Downloads\WELL\WELL-KILN-30x30'
GEO = os.path.join(D, 'WELL-KILN-30x30-geo.json')
J = json.load(open(GEO, encoding='utf-8'))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
root = bpy.data.collections.new('KILN_30x30'); sc.collection.children.link(root)
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
        'bark': ((0.25, 0.18, 0.12), 0.9, 0, 0)}
def mat(n):
    m = bpy.data.materials.get('IN5_' + n)
    if m: return m
    base, rough, metal, trans = MATS.get(n, ((0.8, 0.8, 0.8), 0.6, 0, 0))
    m = bpy.data.materials.new('IN5_' + n); m.use_nodes = True
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
         'stair': 'Stairs', 'pv': 'Roof', 'plinth': 'Structure', 'chimney': 'Kiln_Chimney_Tower'}
V0 = J['vault']
G = {}
for x0, y0, z0, x1, y1, z1, mt, cat in J['boxes']:
    if cat == 'glass' and y0 <= V0['y0'] + 1 and y1 <= V0['y0'] + 70 and z0 >= V0['spring'] - 1 and V0['x0'] - 1 <= x0 and x1 <= V0['x1'] + 1:
        continue                                   # stepped arch glazing -> replaced by smooth arch below
    if cat == 'plinth' and mt == 'stone' and (x1 - x0) < 400 and J['dome']['c'][1] - J['dome']['r'] - 5 <= y0 and y1 <= J['dome']['c'][1] + J['dome']['r'] + 5:
        continue                                   # stepped dome floor slices -> replaced by a disc below
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

# ---- brick dome foyer: drum (door gaps) + hemispherical shell with oculus
Dm = J['dome']; cx, cy = Dm['c'][0] / 1000, Dm['c'][1] / 1000; Ro = Dm['r'] / 1000; Ri = Ro - Dm['t'] / 1000
z0, zs = Dm['z0'] / 1000, Dm['spring'] / 1000
bm = bmesh.new()
N = 96
gw = {270: 1.2, 180: 1.2, 90: 1.4}
def P(r, a, z): return bm.verts.new((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), z))
for i in range(N):
    a0 = 360 * i / N; a1 = 360 * (i + 1) / N; am = (a0 + a1) / 2
    gap = False
    for g, w in gw.items():
        half = math.degrees(w / (Ro - 0.12)) / 2
        if abs(((am - g + 180) % 360) - 180) < half: gap = True
    zt = zs
    zb = z0 + (2.7 if gap else 0)                   # door head 2.70 over the gaps
    o0b, o1b, o0t, o1t = P(Ro, a0, zb), P(Ro, a1, zb), P(Ro, a0, zt), P(Ro, a1, zt)
    i0b, i1b, i0t, i1t = P(Ri, a0, zb), P(Ri, a1, zb), P(Ri, a0, zt), P(Ri, a1, zt)
    for f in ((o0b, o1b, o1t, o0t), (i1b, i0b, i0t, i1t), (o0b, i0b, i1b, o1b), (o0t, o1t, i1t, i0t), (o0b, o0t, i0t, i0b), (o1b, i1b, i1t, o1t)):
        bm.faces.new(f)
M_LAT = 16
ocul = 0.4
for j in range(M_LAT):
    t0 = math.radians(90 * j / M_LAT); t1 = math.radians(90 * (j + 1) / M_LAT)
    if Ro * math.cos(t1) < ocul: t1 = math.acos(ocul / Ro)
    if t0 >= t1: break
    for i in range(N):
        a0 = 360 * i / N; a1 = 360 * (i + 1) / N
        def S(r, t, a): return bm.verts.new((cx + r * math.cos(t) * math.cos(math.radians(a)), cy + r * math.cos(t) * math.sin(math.radians(a)), zs + r * math.sin(t)))
        o00, o01, o10, o11 = S(Ro, t0, a0), S(Ro, t0, a1), S(Ro, t1, a0), S(Ro, t1, a1)
        i00, i01, i10, i11 = S(Ri, t0, a0), S(Ri, t0, a1), S(Ri, t1, a0), S(Ri, t1, a1)
        bm.faces.new((o00, o01, o11, o10)); bm.faces.new((i01, i00, i10, i11))
        if Ro * math.cos(t1) <= ocul + 1e-6: bm.faces.new((o10, o11, i11, i10))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
me = bpy.data.meshes.new('dome_brick'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('Dome_Kiln_Brick', me); ob.data.materials.append(mat('brick')); col('Dome_Kiln').objects.link(ob)
for p in ob.data.polygons: p.use_smooth = True
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=Ro, depth=0.75, location=(cx, cy, z0 - 0.375))
fl_ = bpy.context.object; fl_.name = 'Dome_Floor_Plinth'; fl_.data.materials.append(mat('stone')); link(fl_, 'Dome_Kiln')
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=ocul, depth=0.06, location=(cx, cy, zs + math.sqrt(Ro ** 2 - ocul ** 2) + 0.02))
cap = bpy.context.object; cap.name = 'Dome_Oculus'; cap.data.materials.append(mat('glass')); link(cap, 'Dome_Kiln')
# ---- terracotta vault over the F4 lounge + smooth arched glazing at the south end
x0, y0, x1, y1 = V0['x0'] / 1000, V0['y0'] / 1000, V0['x1'] / 1000, V0['y1'] / 1000
spr, top = V0['spring'] / 1000, V0['top'] / 1000
s_ = x1 - x0; f_ = top - spr; Rr = (s_ * s_ / 4 + f_ * f_) / (2 * f_); xm = (x0 + x1) / 2
vz = lambda x: top - (Rr - math.sqrt(max(0, Rr * Rr - (x - xm) ** 2)))
bm = bmesh.new(); n = 36; th = 0.2
rows = []
for i in range(n + 1):
    x = x0 + s_ * i / n; z = vz(x)
    rows.append([bm.verts.new((x, yy, zz)) for (yy, zz) in ((y0, z), (y1, z), (y0, z - th), (y1, z - th))])
for i in range(n):
    a, b = rows[i], rows[i + 1]
    bm.faces.new((a[0], a[1], b[1], b[0])); bm.faces.new((a[2], b[2], b[3], a[3]))
    bm.faces.new((a[0], b[0], b[2], a[2])); bm.faces.new((a[1], a[3], b[3], b[1]))
me = bpy.data.meshes.new('vault'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('Vault_Terracotta', me); ob.data.materials.append(mat('terracotta')); col('Vault_Lounge').objects.link(ob)
for p in ob.data.polygons: p.use_smooth = True
bm = bmesh.new()
pts = [bm.verts.new((x0 + s_ * i / n, y0 + 0.03, spr)) for i in range(n + 1)]
arc = [bm.verts.new((x0 + s_ * i / n, y0 + 0.03, vz(x0 + s_ * i / n) - th)) for i in range(n + 1)]
for i in range(n): bm.faces.new((pts[i], pts[i + 1], arc[i + 1], arc[i]))
me = bpy.data.meshes.new('vault_glass'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('Vault_Arch_Glazing', me); ob.data.materials.append(mat('glass')); col('Vault_Lounge').objects.link(ob)
for (yy, nm) in ((y0, 'S'), (y1, 'N')):         # arch ribs at both ends
    bm = bmesh.new()
    a1 = [bm.verts.new((x0 + s_ * i / n, yy, vz(x0 + s_ * i / n))) for i in range(n + 1)]
    a2 = [bm.verts.new((x0 + s_ * i / n, yy, vz(x0 + s_ * i / n) - 0.35)) for i in range(n + 1)]
    b1 = [bm.verts.new((x0 + s_ * i / n, yy + (0.25 if nm == 'S' else -0.25), vz(x0 + s_ * i / n))) for i in range(n + 1)]
    b2 = [bm.verts.new((x0 + s_ * i / n, yy + (0.25 if nm == 'S' else -0.25), vz(x0 + s_ * i / n) - 0.35)) for i in range(n + 1)]
    for i in range(n):
        bm.faces.new((a1[i], a1[i + 1], a2[i + 1], a2[i])); bm.faces.new((b1[i], b2[i], b2[i + 1], b1[i + 1]))
        bm.faces.new((a1[i], b1[i], b1[i + 1], a1[i + 1])); bm.faces.new((a2[i], a2[i + 1], b2[i + 1], b2[i]))
    me = bpy.data.meshes.new('rib_' + nm); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('Vault_Brick_Rib_' + nm, me); ob.data.materials.append(mat('brick')); col('Vault_Lounge').objects.link(ob)
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
cam('CAM_1_Aerial_SE', (48, -20, 30), (15, 14, 5), 34)
cam('CAM_2_Garden_South', (15, -13, 8.5), (15, 11, 6.5), 24)
cam('CAM_3_Street_North', (24, 37.5, 1.7), (15, 22, 5.5), 20)
cam('CAM_4_Aerial_NW', (-18, 50, 30), (15, 15, 5), 34)
cam('CAM_5_Dome_Entry', (23.6, 29.6, 1.6), (20.6, 22.5, 3.8), 18)
cam('CAM_6_Aerial_SW', (-16, -14, 22), (15, 14, 5), 32)
sc.camera = bpy.data.objects['CAM_1_Aerial_SE']
r = sc.render; r.resolution_x, r.resolution_y = 1800, 1100; r.resolution_percentage = 100
try:
    sc.eevee.taa_render_samples = 48; sc.eevee.use_raytracing = True
except Exception: pass
try:
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'WELL-KILN-30x30-model.blend'))
result = {'objects': len(bpy.data.objects), 'groups': len(G), 'saved': bpy.data.filepath}
