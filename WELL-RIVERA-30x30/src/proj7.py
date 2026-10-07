# -*- coding: utf-8 -*-
"""Elevations & sections from the box model with exact hidden-surface removal (shapely)."""
from shapely.geometry import box as sbox, Polygon as SPoly, LineString
from shapely.ops import unary_union
from cad7 import Rec
from frame7 import *
from model7 import build, TREES, P

FILL = {'stone': '#d8cdb8', 'render': '#f3f1ec', 'plaster': '#eeeeea', 'concrete': '#dedcd6', 'glass': '#b9d3e3', 'louver': '#9fb7c4',
        'timber': '#a8743f', 'door': '#c9a77c', 'greenroof': '#9bbf7a', 'paving': '#d0ccc4', 'lawn': '#cfe0b8', 'water': '#8ec3df',
        'deck': '#c09a6b', 'brick': '#a9573a', 'calce': '#efe6d8', 'terracotta': '#c4703f', 'uglass': '#d5e3df', 'steel': '#8a9098', 'pv': '#2f3d5c', 'shadow': '#77736b', 'gravel': '#d9d4c7', 'asphalt': '#8a8a8a',
        'timberclad': '#c99d68', 'glulam': '#b5844c', 'roofmetal': '#5f646b', 'brickpave': '#c99a84', 'leaf': '#7fa865', 'leaf2': '#a9c98f'}
SKIPCAT = {'ground', 'road', 'groof'}

VIEWS = {   # name: (u(x,y), depth(x,y), normal side test)
    'S': dict(u=lambda x, y: x, d=lambda x, y: y, face='y0'),
    'N': dict(u=lambda x, y: LOT_W - x, d=lambda x, y: -y, face='y1'),
    'E': dict(u=lambda x, y: y, d=lambda x, y: -x, face='x1'),
    'W': dict(u=lambda x, y: LOT_D - y, d=lambda x, y: x, face='x0'),
}

def face_of(b, view):
    """front face rectangle (u0,u1,z0,z1) and depth for a box"""
    f = VIEWS[view]['face']
    if f == 'y0': return (b.x0, b.x1), b.y0
    if f == 'y1': return (LOT_W - b.x1, LOT_W - b.x0), -b.y1
    if f == 'x1': return (b.y0, b.y1), -b.x1
    if f == 'x0': return (LOT_D - b.y1, LOT_D - b.y0), b.x0

def pface(b, view):
    """projected silhouette polygon (u, z) and depth of a prism P"""
    if view == 'S': return sbox(b.x0, b.z0, b.x1, b.z1), b.y0
    if view == 'N': return sbox(LOT_W - b.x1, b.z0, LOT_W - b.x0, b.z1), -b.y1
    if view == 'E': return SPoly(b.poly).buffer(0), -b.x1
    if view == 'W': return SPoly([(LOT_D - y, z) for y, z in b.poly]).buffer(0), b.x0

THIN = ('glass', 'door', 'rail', 'pool', 'pond')

def project(view, boxes, cut=None, cutdepth=None):
    """cut: None for elevation; for sections cut=(axis, value) (view S: beyond y > value; view W: beyond x > value)"""
    R = Rec()
    faces = []
    cuts = []
    for b in boxes:
        if b.cat in SKIPCAT: continue
        if cut is None and b.cat in ('fence', 'pool', 'pond', 'court'): continue
        if b.z1 <= 0: continue
        if isinstance(b, P):
            g, dep = pface(b, view)
            if g.is_empty or g.area < 1: continue
            if cut is not None:
                ax, val = cut
                pg = SPoly(b.poly).buffer(0)
                if ax == 'y':
                    if b.y0 < val < b.y1:
                        ln = pg.intersection(LineString([(val, -1e6), (val, 1e6)]))
                        if not ln.is_empty:
                            zl, zh = ln.bounds[1], ln.bounds[3]
                            cg = sbox(b.x0, zl, b.x1, max(zh, zl + 20))
                            cuts.append((cg, b, 'thin' if b.cat in THIN or b.mat == 'glass' else 'solid'))
                        bey = pg.intersection(sbox(val, -1e6, 1e7, 1e6))
                        if not bey.is_empty:
                            dd = bey.bounds[2] if b.cat in ('roof', 'rafter', 'skylight', 'ridge', 'pv') else val
                            faces.append((dd, sbox(b.x0, bey.bounds[1], b.x1, bey.bounds[3]), b))
                        continue
                    if b.y1 <= val: continue
                    if b.cat in ('roof', 'rafter', 'skylight', 'ridge', 'pv'): dep = b.y1      # soffit seen from inside: behind what stands under it
                else:
                    if b.x0 < val < b.x1:
                        cuts.append((g, b, 'thin' if b.cat in THIN or b.mat == 'glass' else 'solid'))
                        faces.append((val, g, b))
                        continue
                    if b.x1 <= val: continue
            if view == 'S' and b.cat in ('pv', 'skylight', 'ridge'): dep -= 1e5      # lies on the sloped roof facing the viewer
            faces.append((dep, g, b))
            continue
        (u0, u1), dep = face_of(b, view)
        if u1 - u0 < 1 or b.z1 - b.z0 < 1: continue
        if cut is not None:
            ax, val = cut
            lo, hi = (b.y0, b.y1) if ax == 'y' else (b.x0, b.x1)
            if lo < val < hi:
                if b.cat in ('glass', 'door', 'rail', 'fin', 'shade', 'groof', 'paving', 'court', 'pond', 'deck', 'pool'):
                    if b.cat in THIN:
                        cuts.append((sbox(u0, b.z0, u1, b.z1), b, 'thin'))
                    continue
                cuts.append((sbox(u0, b.z0, u1, b.z1), b, 'solid'))
                continue
            if dep < cutdepth: continue
        faces.append((dep, sbox(u0, b.z0, u1, b.z1), b))
    faces.sort(key=lambda t: (t[0], 0 if t[2].cat in ('glass', 'rail', 'door') else 1))
    occ = None
    # cut poche first (nearest)
    for g, b, k in cuts:
        if k == 'solid':
            R.fill(list(g.exterior.coords), 'S-CUT-POCHE', color='#2e2e2e', z=4)
            R.pline(list(g.exterior.coords), 'S-CUT')
        else:
            R.fill(list(g.exterior.coords), 'S-CUT-POCHE', color=FILL.get(b.mat, '#ccc'), z=4)
            R.pline(list(g.exterior.coords), 'E-ELEV-FINE')
    if cuts:
        occ = unary_union([g for g, b, k in cuts if k == 'solid'])
    for dep, g, b in faces:
        vis = g if occ is None else g.difference(occ)
        if vis.is_empty or vis.area < 10:
            if b.cat not in ('glass', 'rail'):
                occ = g if occ is None else occ.union(g)
            continue
        polys = [vis] if vis.geom_type == 'Polygon' else [p for p in getattr(vis, 'geoms', []) if p.geom_type == 'Polygon']
        col = FILL.get(b.mat, '#eeeeee')
        if cut is not None and b.cat == 'roof': col = '#dcc195'        # timber-boarded roof soffit seen from below
        ly = 'E-GLAS' if b.mat in ('glass', 'louver') else ('E-ELEV-FINE' if b.cat in ('fin', 'stair', 'parapet', 'band', 'rail') else 'E-ELEV')
        for p in polys:
            if p.area < 10: continue
            R.fill(list(p.exterior.coords), 'A-AREA', color=col, z=1, alpha=1.0, holes=[list(i.coords) for i in p.interiors])
            R.pline(list(p.exterior.coords), ly)
            for i in p.interiors: R.pline(list(i.coords), ly)
        if b.mat == 'glass' and b.cat == 'glass':
            # mullions every ~1500 for big panes, transom at 2400
            (u0, u1, z0, z1) = g.bounds
            n = max(1, int(round((u0 - u1) / -1500)))
            for i in range(1, n):
                uu = u0 + (u1 - u0) * i / n
                seg = sbox(uu - 15, z0, uu + 15, z1)
                sv = seg if occ is None else seg.difference(occ)
                if not sv.is_empty and sv.geom_type == 'Polygon':
                    R.pline(list(sv.exterior.coords), 'E-GLAS')
        if b.cat not in ('glass', 'rail'):
            occ = g if occ is None else occ.union(g)
        elif b.cat == 'glass':
            occ = g if occ is None else occ.union(g)
    return R

def ground_line(R, view, x0, x1, extra=None):
    R.line((x0, 0), (x1, 0), 'S-CUT', lw=0.6)
    R.frect(x0, -600, x1, 0, 'A-AREA', color='#e9e4d8', z=0)
    for x in range(int(x0), int(x1), 400):
        R.line((x, -600), (x + 300, -60), 'A-HIDD', lw=0.05)

def tree_elev(R, u, rad, h):
    import math
    R.line((u, 0), (u, h * 0.45), 'L-PLNT', lw=0.3)
    pts = []
    for i in range(0, 41):
        a = math.pi * i / 40
        rr = rad * (1 + 0.08 * math.sin(7 * a))
        pts.append((u + rr * math.cos(a), h * 0.45 + rr * 0.9 * math.sin(a) + (h * 0.55 - rad * 0.9) * 0))
    pts = [(p[0], h * 0.4 + (p[1] - h * 0.45) * (h * 0.6 / (rad * 0.9))) for p in pts]
    R.pline(pts + [pts[0]], 'L-PLNT', lw=0.15)

def levels(R, x, labels):
    prev = -1e9
    for z, t in labels:
        zt = z if z - prev > 450 else prev + 450
        prev = zt
        R.line((x - 600, z), (x + 3600, z), 'A-ANNO', ls='--', lw=0.1)
        R.pline([(x - 180, z), (x, z + 260), (x + 180, z), (x - 180, z)], 'A-ANNO')
        R.text((x + 300, zt + 160), t, 200, 'A-ANNO', ha='left', va='bottom')


import math
LV = [(0, '±0.00 ระดับดิน/ถนน'), (F1, '+0.45 FFL ชั้น 1 / คอร์ต'), (F2, '+3.65 FFL ชั้น 2 / สวนหลังคา W'), (F3, '+6.85 FFL ชั้น 3 / สวนหลังคา N'),
      (F4, '+10.05 FFL ชั้น 4 / ลาน BBQ'), (RF, '+13.25 สวนดาดฟ้า'), (PARAPET, '+14.35 ราวกันตกดาดฟ้า')]

def elevation(view):
    BX, ROOFS = build()
    R = project(view, BX)
    span = LOT_W if view in ('S', 'N') else LOT_D
    ground_line(R, view, -1500, span + 1500)
    if view in ('S', 'N'):
        bx0, bx1 = (BLK[0], BLK[2]) if view == 'S' else (LOT_W - BLK[2], LOT_W - BLK[0])
    else:
        bx0, bx1 = (BLK[1], BLK[3]) if view == 'E' else (LOT_D - BLK[3], LOT_D - BLK[1])
    for (x, y, rad, h) in TREES:
        u = VIEWS[view]['u'](x, y)
        if bx0 - rad * 0.5 < u < bx1 + rad * 0.5: continue
        tree_elev(R, u, rad * 0.8, h)
    levels(R, span + 400, LV)
    grid_marks(R, view)
    return R

def grid_marks(R, view, yb=-1750):
    from frame7 import GX, GY
    if view in ('S', 'N'):
        items = [(k, (v if view == 'S' else LOT_W - v)) for k, v in GX.items()]
    else:
        items = [(k, (v if view == 'E' else LOT_D - v)) for k, v in GY.items()]
    for k, u in items:
        R.line((u, -700), (u, yb + 450), 'A-GRID', lw=0.13, ls=(0, (8, 4)))
        R.circle((u, yb), 450, 'A-GRID'); R.text((u, yb), k, 300, 'A-GRID')

def section_labels(R, k):
    from plan7 import FLOORS
    from draw7 import SHORT
    S = SECTIONS[k]
    for fl, L in FLOORS.items():
        z = {1: F1, 2: F2, 3: F3, 4: F4}[fl]
        for r in L:
            if r.kind in ('shaft', 'lift', 'core', 'fstair', 'void', 'stair') or 'ส่วนต่อเนื่อง' in r.name: continue
            if S['axis'] == 'y' and r.y0 < S['val'] < r.y1:
                u = (r.x0 + r.x1) / 2 if r.w < 12000 else r.x0 + 3500
            elif S['axis'] == 'x' and r.x0 < S['val'] < r.x1:
                u = LOT_D - (r.y0 + r.y1) / 2
            else: continue
            nm = SHORT.get(r.name, r.name) or r.name
            if '\n' not in nm and len(nm) > 18 and ' ' in nm: nm = nm.replace(' ', '\n', 1)
            R.text((u, z + 1500), nm, 160, 'A-TEXT')
    if S['axis'] == 'y':
        R.text(((COURT[0] + COURT[2]) / 2 + 1500, F2 + 1500), 'คอร์ตกลาง (เปิดฟ้า)', 180, 'A-TEXT', bold=True)
        R.text(((XA + XB) / 2, F2 + 2200), 'สวนหลังคา W', 160, 'A-TEXT')
    else:
        R.text((LOT_D - (YD + YE) / 2, F3 + 2200), 'สวนหลังคา N', 160, 'A-TEXT')
        R.text((LOT_D - (YC + YD) / 2, F2 + 2200), 'สวนหลังคา W', 160, 'A-TEXT')
        R.text((LOT_D - (YA + YC) / 2, RF + 1500), 'สวนดาดฟ้า', 160, 'A-TEXT')

SECTIONS = {
    'A': dict(a=(1000, 15000), b=(29000, 15000), look=(0, 1), axis='y', val=15000, view='S',
              title='รูปตัด A-A (ตัดตะวันออก-ตะวันตก ผ่านปีกตะวันตก-คอร์ตกลาง-ปีกตะวันออก: ห้องแขก / สวนหลังคา W + บันไดนอก H2 / คอร์ต + H1 / ลอจเจีย / ลาน BBQ + H4 มองไปทิศเหนือ)'),
    'B': dict(a=(7000, 1000), b=(7000, 29000), look=(1, 0), axis='x', val=7000, view='W',
              title='รูปตัด B-B (ตัดเหนือ-ใต้ ผ่านปีกใต้-ปีกตะวันตก-โถงต้อนรับโค้งอิฐ: ครัวไทย / ครัวโชว์ / ห้องนอน Master / Closet + ระเบียง / สวนหลังคา / เพดานโค้งอิฐ มองไปทิศตะวันออก)'),
}

def section(k):
    S = SECTIONS[k]
    BX, ROOFS = build()
    view = S['view']
    if S['axis'] == 'y':
        cd = S['val']                      # view S: depth = y ; beyond = y > val
    else:
        cd = S['val']                      # view W: depth = x ; beyond = x > val
    R = project(view, BX, cut=(S['axis'], S['val']), cutdepth=cd)
    span = LOT_W if view in ('S', 'N') else LOT_D
    ground_line(R, view, -1500, span + 1500)
    section_labels(R, k)
    grid_marks(R, view, -3300)
    # foundations: bored piles under cut column lines (schematic)
    from frame7 import GX, GY
    cols_u = [v for v in GX.values()] if S['axis'] == 'y' else [LOT_D - v for v in GY.values() if v <= BLK[3]]
    for u in cols_u:
        R.rect(u - 600, -1400, u + 600, -300, 'S-CUT', lw=0.3)
        R.line((u - 200, -1400), (u - 200, -2600), 'A-HIDD', ls='--'); R.line((u + 200, -1400), (u + 200, -2600), 'A-HIDD', ls='--')
    # foundations (bored piles / footings) under cut columns line — schematic
    levels(R, span + 400, LV)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad7 import draw_mpl, scaled_axes
    import sys
    for nm in (sys.argv[1:] or ['S', 'E', 'A', 'B']):
        R = elevation(nm) if nm in VIEWS else section(nm)
        x0, y0, x1, y1 = R.bbox()
        V = (x0 - 500, y0 - 500, x1 + 500, y1 + 500)
        fig = plt.figure(figsize=((V[2] - V[0]) / 100 / 25.4 + .2, (V[3] - V[1]) / 100 / 25.4 + .2))
        ax = scaled_axes(fig, 2, 2, V, 100)
        draw_mpl(ax, R, 100)
        fig.savefig('prev_%s.png' % nm, dpi=110); plt.close(fig)
        print('ok', nm, V)

def project_top(boxes, cats_skip=('ground', 'road', 'fence', 'column', 'wall', 'glass', 'door', 'stair', 'band', 'rail', 'slab', 'plinth'), clip=None, fill=True):
    """top view painter (nearest = highest z1). returns Rec"""
    R = Rec()
    items = [b for b in boxes if b.cat not in cats_skip]
    if clip is not None:
        items = [b for b in items if not (b.x1 < clip[0] or b.x0 > clip[2] or b.y1 < clip[1] or b.y0 > clip[3])]
    items.sort(key=lambda b: (0 if b.cat in ('pv', 'skylight', 'ridge', 'gutter') else 1, -b.z1))      # elements lying on the sloped roof first
    occ = None
    for b in items:
        g = sbox(b.x0, b.y0, b.x1, b.y1)
        vis = g if occ is None else g.difference(occ)
        if not vis.is_empty and vis.area > 10:
            polys = [vis] if vis.geom_type == 'Polygon' else [p for p in getattr(vis, 'geoms', []) if p.geom_type == 'Polygon']
            col = FILL.get(b.mat, '#eeeeee')
            if b.cat == 'roof': col = '#dfe9d2'
            ly = 'A-ROOF' if b.cat in ('roof', 'parapet', 'groof', 'chimney', 'domeslice', 'vaultslice') else ('L-WATR' if b.mat == 'water' else ('L-PAVE' if b.cat in ('paving', 'deck', 'ramp', 'court') else 'A-ROOF'))
            for p in polys:
                if fill: R.fill(list(p.exterior.coords), 'A-AREA', color=col, z=1, holes=[list(i.coords) for i in p.interiors])
                R.pline(list(p.exterior.coords), ly)
                for i in p.interiors:
                    R.pline(list(i.coords), ly)
        if b.cat not in ('glass',):
            occ = g if occ is None else occ.union(g)
    return R
