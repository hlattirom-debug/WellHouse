# -*- coding: utf-8 -*-
"""3D box model (single source for elevations, sections, roof plan and Blender)."""
import math
import json
from shapely.geometry import box as sbox, Polygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from frame5 import *
from plan5 import FLOORS, COURTS, find
from walls5 import model, side_of
from draw5 import columns, COL

FFL = {1: F1, 2: F2, 3: F3, 4: F4, 5: RF}
TOP = {1: F2 - SLAB, 2: F3 - SLAB, 3: F4 - SLAB, 4: RF - 250}     # underside of slab above
ROOF_T = 250
FLS = (1, 2, 3, 4)

class B:
    __slots__ = ('x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'mat', 'cat', 'tag')
    def __init__(s, x0, y0, z0, x1, y1, z1, mat, cat, tag=''):
        s.x0, s.x1 = min(x0, x1), max(x0, x1); s.y0, s.y1 = min(y0, y1), max(y0, y1); s.z0, s.z1 = min(z0, z1), max(z0, z1)
        s.mat, s.cat, s.tag = mat, cat, tag
    def d(s): return dict(b=[s.x0, s.y0, s.z0, s.x1, s.y1, s.z1], m=s.mat, c=s.cat, t=s.tag)

def region(fl, kinds=None):
    return unary_union([sbox(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[fl] if (kinds is None or r.kind in kinds)])

def rect_decompose(geom):
    """decompose a rectilinear polygon (or multi) into rectangles (row merging on the coordinate grid)"""
    if geom.is_empty: return []
    gs = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    out = []
    for g in gs:
        if g.geom_type != 'Polygon' or g.area < 1: continue
        xs = sorted({round(c[0]) for c in g.exterior.coords} | {round(c[0]) for i in g.interiors for c in i.coords})
        ys = sorted({round(c[1]) for c in g.exterior.coords} | {round(c[1]) for i in g.interiors for c in i.coords})
        for ya, yb in zip(ys, ys[1:]):
            run = None
            for xa, xb in zip(xs, xs[1:]):
                inside = g.buffer(-1).contains(sbox(xa + 2, ya + 2, xb - 2, yb - 2)) if (xb - xa > 4 and yb - ya > 4) else False
                if inside:
                    run = [run[0], xb] if run else [xa, xb]
                else:
                    if run: out.append((run[0], ya, run[1], yb)); run = None
            if run: out.append((run[0], ya, run[1], yb))
    return out

def dome_slices(n=44, m=22, cat='domeslice'):
    """brick drum + hemispherical dome approximated by axis-aligned slices (for orthographic projection only)"""
    cx, cy = DOME_C; R_ = DOME_R
    out = []
    for i in range(n):
        xa = cx - R_ + 2 * R_ * i / n; xb = cx - R_ + 2 * R_ * (i + 1) / n; xm = (xa + xb) / 2
        h = math.sqrt(max(0, R_ * R_ - (xm - cx) ** 2))
        out.append(B(xa, cy - h, F1, xb, cy + h, DOME_SPRING, 'brick', cat))
        for j in range(m):
            za = DOME_SPRING + R_ * j / m; zb = DOME_SPRING + R_ * (j + 1) / m; zm = (za + zb) / 2
            rz = math.sqrt(max(0, R_ * R_ - (zm - DOME_SPRING) ** 2))
            if abs(xm - cx) >= rz: continue
            hh = math.sqrt(rz * rz - (xm - cx) ** 2)
            out.append(B(xa, cy - hh, za, xb, cy + hh, zb, 'brick', cat))
    return out

def vault_z(x):
    x0, y0, x1, y1 = VAULT
    s = x1 - x0; f = VAULT_TOP - (RF - 250); Rr = (s * s / 4 + f * f) / (2 * f); xm = (x0 + x1) / 2
    return VAULT_TOP - (Rr - math.sqrt(max(0, Rr * Rr - (x - xm) ** 2)))

def vault_slices(n=27, cat='vaultslice'):
    x0, y0, x1, y1 = VAULT
    out = []
    zs = RF - 250
    for i in range(n):
        xa = x0 + (x1 - x0) * i / n; xb = x0 + (x1 - x0) * (i + 1) / n; z = vault_z((xa + xb) / 2)
        out.append(B(xa, y0 + 250, zs, xb, y1, z, 'terracotta', cat))                 # vault (terracotta tiles)
        out.append(B(xa, y0, zs, xb, y0 + 60, max(zs + 10, z - 160), 'glass', 'glass', 'arch'))   # arched "kiln mouth" glazing
        out.append(B(xa, y0, max(zs + 10, z - 160), xb, y0 + 250, z, 'brick', cat))  # brick arch rim
    return out

OPEN_SKY = {'ระเบียง Master (ดาดฟ้า)', 'บันไดหนีไฟภายนอก'}
MAIN = 'บันไดหลัก (ปล่องเตาเผา)'
PSN = 'บันไดส่วนตัว Master'
LOGN = 'ลอจเจียทิศเหนือ (ฉากกระจก U)'

def build():
    M = model()
    BX = []
    add = lambda *a, **k: BX.append(B(*a, **k))
    # ---------------- ground slab: F1 +0.45, garage +0.15, dome floor
    A1 = unary_union([sbox(*r.rect()) for r in FLOORS[1] if r.kind not in ('fstair', 'core')])
    low = region(1, ('park',))
    for r in rect_decompose(A1.difference(low)):
        add(r[0], r[1], -300, r[2], r[3], F1, 'stone', 'plinth')
    for r in rect_decompose(low):
        add(r[0], r[1], -300, r[2], r[3], GARAGE_Z, 'paving', 'plinth')
    cx, cy = DOME_C
    for i in range(16):
        xa = cx - DOME_R + 2 * DOME_R * i / 16; xb = cx - DOME_R + 2 * DOME_R * (i + 1) / 16
        h = math.sqrt(max(0, DOME_R ** 2 - ((xa + xb) / 2 - cx) ** 2))
        add(xa, cy - h, -300, xb, cy + h, F1, 'stone', 'plinth')
    # ---------------- floor slabs F2..F4
    for fl in (2, 3, 4):
        for r in FLOORS[fl]:
            if r.kind in ('void', 'core', 'fstair', 'lift'): continue
            if r.name == MAIN:          # floor landing at the south end only (stair shaft open)
                add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y0 + 40 + STAIR_LAND, FFL[fl], 'concrete', 'slab'); continue
            if r.kind == 'stair':       # private stair: landing strip at the east (floor landing)
                add(r.x1 - 1300, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab'); continue
            add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab', r.kind)
    # ---------------- roofs over each level where nothing is above
    A = {}
    for k in FLS:
        A[k] = unary_union([sbox(*r.rect()) for r in FLOORS[k] if r.kind not in ('fstair', 'core') and r.name not in OPEN_SKY])
    full = {k: unary_union([sbox(*r.rect()) for r in FLOORS[k] if r.kind not in ('fstair', 'core')]) for k in FLS}
    ROOFS = []
    for k in FLS:
        above = full[k + 1] if k < 4 else Polygon()
        rg = A[k].difference(above) if not above.is_empty else A[k]
        if k == 4: rg = rg.difference(sbox(*VAULT))
        zr = FFL[k + 1]
        kind = 'main' if k == 4 else 'green'
        if rg.is_empty or rg.area < 1e5: continue
        ROOFS.append((rg, zr, kind))
        for r in rect_decompose(rg):
            add(r[0], r[1], zr - ROOF_T, r[2], r[3], zr, 'concrete', 'roof', kind)
            if kind != 'main':
                add(r[0] + 1, r[1] + 1, zr, r[2] - 1, r[3] - 1, zr + 150, 'greenroof', 'groof')
        bnd = rg.boundary
        if not above.is_empty: bnd = bnd.difference(above.buffer(30))
        if k == 4: bnd = bnd.difference(sbox(*VAULT).buffer(30))
        lines = [bnd] if bnd.geom_type == 'LineString' else list(getattr(bnd, 'geoms', []))
        ph = 600 if kind == 'main' else 450
        for ln in lines:
            cs = list(ln.coords)
            for (xa, ya), (xb, yb) in zip(cs, cs[1:]):
                if abs(xa - xb) < 1 and abs(ya - yb) < 1: continue
                if abs(ya - yb) < 1:
                    inside_up = rg.contains(sbox(min(xa, xb) + 5, ya + 5, max(xa, xb) - 5, ya + 50)) if abs(xb - xa) > 20 else False
                    y0, y1 = (ya, ya + 150) if inside_up else (ya - 150, ya)
                    add(min(xa, xb), y0, zr, max(xa, xb), y1, zr + ph, 'calce', 'parapet')
                else:
                    inside_r = rg.contains(sbox(xa + 5, min(ya, yb) + 5, xa + 50, max(ya, yb) - 5)) if abs(yb - ya) > 20 else False
                    x0, x1 = (xa, xa + 150) if inside_r else (xa - 150, xa)
                    add(x0, min(ya, yb), zr, x1, max(ya, yb), zr + ph, 'calce', 'parapet')
    # ---------------- walls with openings (F1 firebrick base, upper floors calce lime plaster, tower brick)
    for fl in FLS:
        segs, ops = M[fl]['segs'], M[fl]['ops']
        z0, z1 = FFL[fl], TOP[fl]
        H = z1 - z0
        for s in segs:
            if s.wt not in ('ext', 'int', 'wet', 'rail'): continue
            h = s.th / 2
            tower = MAIN in (s.a.name, s.b.name if s.b else '') or 'ลิฟต์บ้าน' in (s.a.name, s.b.name if s.b else '')
            if s.wt == 'ext':
                mat = 'brick' if (tower or fl == 1) else 'calce'
            else:
                mat = 'brick' if tower else 'plaster'
            def wb(u0, u1, za, zb, m=mat, cat='wall', tag=''):
                if u1 - u0 < 1 or zb - za < 1: return
                if s.o == 'H': add(u0, s.c - h, za, u1, s.c + h, zb, m, cat, tag)
                else: add(s.c - h, u0, za, s.c + h, u1, zb, m, cat, tag)
            if s.wt == 'rail':
                if s.a.name == LOGN:                         # U-glass channel screen, panels 1200 / gaps 600
                    u = s.lo + 150
                    while u + 1200 <= s.hi - 100:
                        if s.o == 'H': add(u, s.c - 30, z0, u + 1200, s.c + 30, z1, 'uglass', 'glass', 'ug')
                        else: add(s.c - 30, u, z0, s.c + 30, u + 1200, z1, 'uglass', 'glass', 'ug')
                        u += 1800
                    if s.o == 'H': add(s.lo, s.c - 10, z0, s.hi, s.c + 10, z0 + 1100, 'glass', 'rail')
                    else: add(s.c - 10, s.lo, z0, s.c + 10, s.hi, z0 + 1100, 'glass', 'rail')
                    continue
                rm = 'steel' if 'fstair' in (s.a.kind, s.b.kind if s.b else '') else 'glass'
                if s.o == 'H': add(s.lo, s.c - 10, z0, s.hi, s.c + 10, z0 + 1100, rm, 'rail')
                else: add(s.c - 10, s.lo, z0, s.c + 10, s.hi, z0 + 1100, rm, 'rail')
                continue
            myops = sorted([o for o in ops if o.seg is s], key=lambda o: o.lo)
            u = s.lo - h
            for o in myops:
                wb(u, o.lo, z0, z1)
                sill = o.sill; head = min(o.head, H)
                wb(o.lo, o.hi, z0, z0 + sill); wb(o.lo, o.hi, z0 + head, z1)
                if o.kind in ('win', 'glass', 'slide', 'slide1', 'louver'):
                    mm = 'louver' if o.kind == 'louver' else 'glass'
                    if s.o == 'H': add(o.lo, s.c - 15, z0 + sill, o.hi, s.c + 15, z0 + head, mm, 'glass', o.tag)
                    else: add(s.c - 15, o.lo, z0 + sill, s.c + 15, o.hi, z0 + head, mm, 'glass', o.tag)
                elif o.kind in ('door', 'door2', 'lift'):
                    mm = 'timber' if s.b is None or o.kind == 'door2' else 'door'
                    if s.o == 'H': add(o.lo, s.c - 25, z0, o.hi, s.c + 25, z0 + head, mm, 'door', o.tag)
                    else: add(s.c - 25, o.lo, z0, s.c + 25, o.hi, z0 + head, mm, 'door', o.tag)
                u = o.hi
            wb(u, s.hi + h, z0, z1)
            if s.wt == 'ext':
                wb(s.lo - h, s.hi + h, z1, FFL[fl + 1], 'brick' if tower else 'concrete', 'band')
    # ---------------- columns
    for fl in FLS:
        for (x, y) in columns(fl):
            add(x - COL / 2, y - COL / 2, (0 if fl == 1 else FFL[fl]), x + COL / 2, y + COL / 2, FFL[fl + 1], 'concrete', 'column')
    # ---------------- brick dome foyer (drum + hemisphere) + north door + oculus
    for b_ in dome_slices(): BX.append(b_)
    add(cx - 700, cy + DOME_R - 60, F1, cx + 700, cy + DOME_R + 20, F1 + 2700, 'timber', 'door', 'dome')
    add(cx - 400, cy - 400, DOME_TOP - 60, cx + 400, cy + 400, DOME_TOP + 120, 'glass', 'skylight')
    # ---------------- brick tower ("kiln chimney") above the roof: walls to +14.85, louvre band, cap
    tx0, ty0, tx1, ty1 = TOWER
    for (a0, b0, a1, b1) in ((tx0, ty0, tx1, ty0 + 200), (tx0, ty1 - 200, tx1, ty1), (tx0, ty0, tx0 + 200, ty1), (tx1 - 200, ty0, tx1, ty1)):
        add(a0, b0, RF, a1, b1, CORE_TOP - 600, 'brick', 'chimney')
        add(a0, b0, CORE_TOP - 600, a1, b1, CORE_TOP - 200, 'louver', 'chimney')
        add(a0, b0, CORE_TOP - 200, a1, b1, CORE_TOP, 'brick', 'chimney')
    add(tx0 + 200, ty0 + 200, CORE_TOP - 250, tx1 - 200, ty1 - 200, CORE_TOP - 150, 'glass', 'skylight')
    # ---------------- F4 family lounge brick/terracotta vault with arched south glazing
    for b_ in vault_slices(): BX.append(b_)
    # ---------------- main stair in the tower (U along Y, floor landing south)
    sx0, sy0 = STAIR_R[0] + 50, STAIR_R[1] + 40
    xa0, xa1 = sx0, sx0 + STAIR_W; xb0, xb1 = sx0 + STAIR_W + 100, sx0 + 2 * STAIR_W + 100
    yS = sy0 + STAIR_LAND; yN = yS + 9 * TREAD
    for fl in (1, 2, 3):
        base = FFL[fl]
        for i in range(10):
            add(xa0, yS + i * TREAD, base + i * RISE - 150, xa1, yS + (i + 1) * TREAD, base + (i + 1) * RISE, 'concrete', 'stair')
        add(xa0, yN, base + 10 * RISE - 200, xb1, yN + STAIR_LAND, base + 10 * RISE, 'concrete', 'stair')
        for i in range(10):
            y_hi = yN - i * TREAD
            add(xb0, y_hi - TREAD, base + 10 * RISE + i * RISE - 150, xb1, y_hi, base + 10 * RISE + (i + 1) * RISE, 'concrete', 'stair')
    # ---------------- west terracotta baguette screen (ceramic grille) F2 -> parapet
    xs0, xs1 = BLK[0] - 450, BLK[0] - 335
    y = BLK[1] + 150
    while y < BLK[3] - 100:
        top = PARAPET if y < 15500 else F3 + 450
        add(xs0, y - 40, F2 - SLAB, xs1, y + 40, top, 'terracotta', 'lattice'); y += 300
    for z in (F2 - SLAB, F3 - SLAB, F4 - SLAB):
        add(xs0 - 20, BLK[1], z, xs1 + 20, BLK[3] if z < F3 else 15500, z + 120, 'steel', 'lattice')
    # ---------------- pergola over the master terrace
    mt = find('ระเบียง Master (ดาดฟ้า)')
    x = mt.x0 + 200
    while x < mt.x1:
        add(x - 40, mt.y0, RF - 250, x + 40, mt.y1, RF - 50, 'timber', 'pergola'); x += 450
    for (px, py) in ((mt.x0 + 150, mt.y0 + 150), (mt.x1 - 150, mt.y0 + 150)):
        add(px - 100, py - 100, F4, px + 100, py + 100, RF - 250, 'steel', 'pergola')
    # ---------------- PV on the main roof (rows 1.00 x 2.00, skip tower and edges)
    main = [rg for rg, z, k in ROOFS if k == 'main']
    if main:
        rg = main[0].difference(sbox(*TOWER).buffer(500)).buffer(-600)
        y = BLK[1] + 900
        while y + 2000 < BLK[3]:
            x = BLK[0] + 900
            while x + 1000 < BLK[2]:
                if rg.contains(sbox(x, y, x + 1000, y + 2000)):
                    add(x, y, RF + 300, x + 1000, y + 2000, RF + 360, 'pv', 'pv')
                x += 1100
            y += 2600
    # ---------------- external fire stair (steel, flights along X, floor landing east)
    fs = find('บันไดหนีไฟภายนอก', 1)
    X0, Y0 = fs.x0 + 40, fs.y0 + 50
    fx0 = X0 + 1200 + 9 * TREAD          # floor landing starts
    ay0, ay1 = Y0 + 1200, Y0 + 2300      # flight A (north) ; flight B (south) Y0..Y0+1100
    for fl in (1, 2, 3):
        base = FFL[fl] if fl > 1 else 0
        rise = (FFL[fl + 1] - base) / 20
        for i in range(10):
            xa = fx0 - (i + 1) * TREAD
            add(xa, ay0, base + i * rise - 120, xa + TREAD, ay1, base + (i + 1) * rise, 'steel', 'stair')
        add(X0, Y0, base + 10 * rise - 150, X0 + 1200, Y0 + 2300, base + 10 * rise, 'steel', 'stair')
        for i in range(10):
            xa = X0 + 1200 + i * TREAD
            add(xa, Y0, base + 10 * rise + i * rise - 120, xa + TREAD, Y0 + 1100, base + 10 * rise + (i + 1) * rise, 'steel', 'stair')
        add(fx0, Y0, FFL[fl + 1] - 150, fs.x1 - 40, Y0 + 2300, FFL[fl + 1], 'steel', 'stair')
    for (px, py) in ((X0, Y0), (X0, Y0 + 2200), (fs.x1 - 140, Y0), (fs.x1 - 140, Y0 + 2200)):
        add(px, py, 0, px + 100, py + 100, F4 + 1100, 'steel', 'stair')
    # ---------------- private master stair F3 -> F4 (flights along X, floor landing east)
    ps = find(PSN, 3)
    x0s = ps.x0 + 140; xF = x0s + 9 * TREAD + 2 * STAIR_LAND
    for i in range(10):
        xa = xF - STAIR_LAND - (i + 1) * TREAD
        add(xa, ps.y1 - 50 - STAIR_W, F3 + i * RISE - 150, xa + TREAD, ps.y1 - 50, F3 + (i + 1) * RISE, 'concrete', 'stair')
    add(x0s, ps.y0 + 50, F3 + 10 * RISE - 150, x0s + STAIR_LAND, ps.y1 - 50, F3 + 10 * RISE, 'concrete', 'stair')
    for i in range(10):
        xa = x0s + STAIR_LAND + i * TREAD
        add(xa, ps.y0 + 50, F3 + 10 * RISE + i * RISE - 150, xa + TREAD, ps.y0 + 50 + STAIR_W, F3 + 10 * RISE + (i + 1) * RISE, 'concrete', 'stair')
    # ---------------- site
    add(0, 0, -300, LOT_W, LOT_D, -1, 'lawn', 'ground')
    add(-4000, LOT_D, -300, LOT_W + 4000, LOT_D + ROAD_W, -1, 'asphalt', 'road')
    p = POOL; add(p[0], p[1], -1400, p[2], p[3], 40, 'water', 'pool')
    pd = POOL_DECK
    for r in rect_decompose(sbox(*pd).difference(sbox(*p))):
        add(r[0], r[1], -300, r[2], r[3], 30, 'deck', 'deck')
    for r in (DRIVE, WALK):
        add(r[0], r[1], -300, r[2], r[3], 20, 'paving', 'paving')
    fh = FENCE_H
    add(0, 0, 0, LOT_W, 120, fh, 'brick', 'fence')
    add(0, 0, 0, 120, LOT_D, fh, 'brick', 'fence')
    add(LOT_W - 120, 0, 0, LOT_W, LOT_D, fh, 'brick', 'fence')
    add(WALK[2], LOT_D - 120, 0, LOT_W, LOT_D, 1200, 'brick', 'fence')
    add(DRIVE[2], LOT_D - 120, 0, WALK[0], LOT_D, 1200, 'brick', 'fence')
    return BX, ROOFS

TREES = [  # (x, y, canopy radius, height)
    (1800, 5200, 1600, 6500), (20500, 2200, 1700, 6500), (28300, 3000, 1400, 5500), (28300, 11000, 1500, 6000),
    (28300, 17500, 1500, 6000), (25800, 27800, 1600, 6500), (1800, 28000, 1500, 5500), (28300, 24500, 1200, 5000),
]

if __name__ == '__main__':
    BX, ROOFS = build()
    from collections import Counter
    print(len(BX), Counter(b.cat for b in BX))
    for rg, z, k in ROOFS: print('roof', k, z, round(rg.area / 1e6, 2))
    x0, y0, x1, y1 = VAULT
    json.dump(dict(boxes=[[round(v) for v in b.d()['b']] + [b.mat, b.cat] for b in BX if b.cat not in ('domeslice', 'vaultslice')], trees=TREES,
                   dome=dict(c=list(DOME_C), r=DOME_R, t=DOME_T, z0=F1, spring=DOME_SPRING, top=DOME_TOP, doors=[270, 180, 90]),
                   vault=dict(x0=x0, y0=y0, x1=x1, y1=y1, spring=RF - 250, top=VAULT_TOP)),
              open('in5_model.json', 'w'), separators=(',', ':'))
    print('json', len(open('in5_model.json').read()) // 1024, 'KB')
