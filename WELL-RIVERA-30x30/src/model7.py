# -*- coding: utf-8 -*-
"""3D model: boxes B + X-prisms P (single source for elevations, sections, roof plan and Blender)."""
import math
import json
from shapely.geometry import box as sbox, Polygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from frame7 import *
from plan7 import FLOORS, COURTS, find
from walls7 import model, side_of
from draw7 import columns, COL

FFL = {1: F1, 2: F2, 3: F3, 4: F4, 5: RF}
TOP = {1: F2 - SLAB, 2: F3 - SLAB, 3: F4 - SLAB, 4: RF - ROOF_T}  # underside of slab above (F4: per segment, roof)
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

class P:
    """prism extruded along X: polygon in (y, z) between x0 and x1 (sloped roof, raked walls, struts, rafters)"""
    __slots__ = ('x0', 'x1', 'poly', 'y0', 'y1', 'z0', 'z1', 'mat', 'cat', 'tag')
    def __init__(s, x0, x1, poly, mat, cat, tag=''):
        s.x0, s.x1 = min(x0, x1), max(x0, x1); s.poly = [(float(y), float(z)) for y, z in poly]
        ys = [p[0] for p in s.poly]; zs = [p[1] for p in s.poly]
        s.y0, s.y1, s.z0, s.z1 = min(ys), max(ys), min(zs), max(zs)
        s.mat, s.cat, s.tag = mat, cat, tag
    def d(s): return dict(x=[s.x0, s.x1], p=s.poly, m=s.mat, c=s.cat, t=s.tag)

def under(y): return RF - ROOF_T

PSN = 'บันไดส่วนตัว Master'
MAIN = 'บันไดหลัก (เกลียวใน)'
OPEN_SKY = {'ลาน BBQ บนหลังคา (pergola)'}
SKY = (0, 0, 0, 0)

def vault_z(y):
    """underside of the brick barrel vault over the foyer (spans N-S)"""
    import math as _m
    y0, y1 = VAULT[1], VAULT[3]
    s_ = y1 - y0; f = VAULT_TOP - VAULT_SPRING; Rr = (s_ * s_ / 4 + f * f) / (2 * f); ym = (y0 + y1) / 2
    return VAULT_TOP - (Rr - _m.sqrt(max(0, Rr * Rr - (y - ym) ** 2)))

def wall_mat(s, fl):
    if s.b is not None: return 'plaster'
    if s.o == 'V' and s.c in (XA, XD): return 'brick'           # outer side walls: exposed brick "party walls"
    if s.o == 'H' and s.c == YE: return 'brick'
    if s.o == 'H' and s.c == YA: return 'timberclad'
    return 'concrete'                                             # courtyard / stepped faces: fair-faced concrete

def helix_boxes(add):
    for nm, (x0, y0, x1, y1), z0, z1, d in HELIX:
        rise = (z1 - z0) / 20
        for i in range(20):
            if d == 'N': ya, yb = y0 + i * TREAD, y0 + (i + 1) * TREAD
            else: ya, yb = y1 - (i + 1) * TREAD, y1 - i * TREAD
            if i == 19: ya, yb = (y0 + 19 * TREAD, y1) if d == 'N' else (y0, y1 - 19 * TREAD)
            add(x0 + 60, ya, z0 + i * rise - 180, x1 - 60, yb, z0 + (i + 1) * rise, 'concrete', 'helix')
        L = y1 - y0
        for xx in (x0, x1 - 60):      # stringers as stepped plates + glass rails
            for i in range(10):
                ya, yb = y0 + L * i / 10, y0 + L * (i + 1) / 10
                t = (i + 0.5) / 10 if d == 'N' else 1 - (i + 0.5) / 10
                zc = z0 + (z1 - z0) * t
                add(xx, ya, zc - 350, xx + 60, yb, zc + 100, 'concrete', 'helix')
                add(xx, ya, zc + 100, xx + 20, yb, zc + 1000, 'glass', 'rail')

def build():
    M = model()
    BX = []
    add = lambda *a, **k: BX.append(B(*a, **k))
    addp = lambda *a, **k: BX.append(P(*a, **k))
    # ---------------- ground slab: F1 +0.45, garage +0.15, courtyard brick paving +0.45 (flush, with trench drain)
    A1 = unary_union([sbox(*r.rect()) for r in FLOORS[1] if r.kind not in ('fstair', 'core')])
    low = region(1, ('park',))
    for r in rect_decompose(A1.difference(low)):
        add(r[0], r[1], -300, r[2], r[3], F1, 'stone', 'plinth')
    for r in rect_decompose(low):
        add(r[0], r[1], -300, r[2], r[3], GARAGE_Z, 'paving', 'plinth')
    for r in rect_decompose(sbox(*COURT).difference(sbox(*REFLECT))):
        add(r[0], r[1], -300, r[2], r[3], F1, 'brickpave', 'court')
    rx0, ry0, rx1, ry1 = REFLECT
    add(rx0, ry0, -300, rx1, ry1, F1 - 300, 'concrete', 'court'); add(rx0, ry0, F1 - 300, rx1, ry1, F1 - 60, 'water', 'pool')
    for (px, py, pw, ph) in ((11400, 12300, 1800, 600), (18300, 18200, 1500, 600)):
        add(px, py, F1, px + pw, py + ph, F1 + 450, 'timber', 'court')
    # ---------------- floor slabs F2..F4
    for fl in (2, 3, 4):
        for r in FLOORS[fl]:
            if r.kind in ('void', 'core', 'fstair', 'lift'): continue
            if r.name == MAIN:          # floor landing at the north end only (stair opening)
                add(r.x0, r.y1 - 40 - STAIR_LAND, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab'); continue
            if r.name == PSN and fl == 4:
                add(r.x0, r.y1 - 40 - STAIR_LAND, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab'); continue
            m = 'deck' if r.kind == 'inb' else 'concrete'
            add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], m, 'slab', r.kind)
    # ---------------- roof gardens where nothing is above (spiral: W @ +3.65, N @ +6.85, top S @ +13.25)
    full = {k: unary_union([sbox(*r.rect()) for r in FLOORS[k] if r.kind not in ('fstair', 'core')]) for k in FLS}
    roofed = {k: unary_union([sbox(*r.rect()) for r in FLOORS[k] if r.kind not in ('fstair', 'core') and r.name not in OPEN_SKY]) for k in FLS}
    ROOFS = []
    for k in FLS:
        above = full[k + 1] if k < 4 else Polygon()
        rg = roofed[k].difference(above) if not above.is_empty else roofed[k]
        if rg.is_empty or rg.area < 1e5: continue
        zr = FFL[k + 1]
        kind = 'top' if k == 4 else 'garden'
        ROOFS.append((rg, zr, kind))
        for r in rect_decompose(rg):
            add(r[0], r[1], zr - ROOF_T, r[2], r[3], zr, 'concrete', 'roof', kind)
            add(r[0] + 1, r[1] + 1, zr, r[2] - 1, r[3] - 1, zr + 120, 'greenroof', 'groof')
        bnd = rg.boundary
        if not above.is_empty: bnd = bnd.difference(above.buffer(30))
        lines = [bnd] if bnd.geom_type == 'LineString' else list(getattr(bnd, 'geoms', []))
        for ln in lines:
            cs = list(ln.coords)
            for (xa, ya), (xb, yb) in zip(cs, cs[1:]):
                if abs(xa - xb) < 1 and abs(ya - yb) < 1: continue
                if abs(ya - yb) < 1:
                    inside_up = rg.contains(sbox(min(xa, xb) + 5, ya + 5, max(xa, xb) - 5, ya + 50)) if abs(xb - xa) > 20 else False
                    y0, y1 = (ya, ya + 300) if inside_up else (ya - 300, ya)
                    add(min(xa, xb), y0, zr, max(xa, xb), y1, zr + 450, 'concrete', 'parapet')
                    yg = y0 + 140
                    add(min(xa, xb), yg, zr + 450, max(xa, xb), yg + 20, zr + 1100, 'glass', 'rail')
                else:
                    inside_r = rg.contains(sbox(xa + 5, min(ya, yb) + 5, xa + 50, max(ya, yb) - 5)) if abs(yb - ya) > 20 else False
                    x0, x1 = (xa, xa + 300) if inside_r else (xa - 300, xa)
                    add(x0, min(ya, yb), zr, x1, max(ya, yb), zr + 450, 'concrete', 'parapet')
                    xg = x0 + 140
                    add(xg, min(ya, yb), zr + 450, xg + 20, max(ya, yb), zr + 1100, 'glass', 'rail')
    # planters on the roof gardens
    for (x0, y0, x1, y1, z) in ((XA + 1800, YC + 600, XB - 600, YC + 1600, F2), (XA + 1800, YD + 600, XB - 300, YD + 1400, F3),
                                (13000, YE - 1400, 22000, YE - 600, F3), (XA + 600, 9800, XD - 600, 10600, RF)):
        add(x0, y0, z, x1, y1, z + 500, 'timber', 'planter'); add(x0 + 60, y0 + 60, z + 500, x1 - 60, y1 - 60, z + 900, 'leaf', 'planter')
    # ---------------- walls with openings
    for fl in FLS:
        segs, ops = M[fl]['segs'], M[fl]['ops']
        z0 = FFL[fl]
        for s in segs:
            if s.wt not in ('ext', 'int', 'wet', 'rail'): continue
            h = s.th / 2
            z1 = TOP[fl]
            H = z1 - z0
            mat = wall_mat(s, fl) if s.wt == 'ext' else 'plaster'
            def wb(u0, u1, za, zb, m=mat, cat='wall', tag=''):
                if u1 - u0 < 1 or zb - za < 1: return
                if s.o == 'H': add(u0, s.c - h, za, u1, s.c + h, zb, m, cat, tag)
                else: add(s.c - h, u0, za, s.c + h, u1, zb, m, cat, tag)
            if s.wt == 'rail':
                if s.o == 'H': add(s.lo, s.c - 10, z0, s.hi, s.c + 10, z0 + 1100, 'glass', 'rail')
                else: add(s.c - 10, s.lo, z0, s.c + 10, s.hi, z0 + 1100, 'glass', 'rail')
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
                ztop = FFL[fl + 1] if fl < 4 else RF
                wb(s.lo - h, s.hi + h, z1, ztop, 'concrete', 'band')
    # ---------------- brick barrel vault over the double-height foyer (spans N-S, extruded along X)
    n = 24; ya, yb = VAULT[1], VAULT[3]
    inner = [(ya + (yb - ya) * i / n, vault_z(ya + (yb - ya) * i / n)) for i in range(n + 1)]
    outer = [(y, z + 240) for y, z in inner][::-1]
    addp(VAULT[0] + 100, VAULT[2] - 100, inner + outer, 'brick', 'vault')
    # ---------------- RC columns
    for fl in FLS:
        for (x, y) in columns(fl):
            zt = FFL[fl + 1] if fl < 4 else RF
            add(x - COL / 2, y - COL / 2, (0 if fl == 1 else FFL[fl]), x + COL / 2, y + COL / 2, zt, 'concrete', 'column')
    # ---------------- exterior helix (the second spiral) + vertical gardens on the brick side walls
    helix_boxes(add)
    for (x0, x1) in ((XA - 140, XA - 100), (XD + 100, XD + 140)):
        for (ya, yb, zt) in ((YA + 900, YA + 3900, RF), (YD + 900, YE - 900, F3)):
            add(x0, ya, F1 + 600, x1, yb, zt - 300, 'leaf', 'greenwall')
    # ---------------- hanging gardens: planter troughs on slab edges (south face + courtyard faces), trailing plants
    def trough(o, c, lo, hi, z, out):
        """o 'H' (along x at y=c) or 'V' (along y at x=c); out = +1/-1 outward side"""
        d0, d1 = (c, c + out * 450) if out > 0 else (c + out * 450, c)
        if o == 'H': add(lo, d0, z - 650, hi, d1, z - 200, 'concrete', 'trough')
        else: add(d0, lo, z - 650, d1, hi, z - 200, 'concrete', 'trough')
        u = lo + 250
        while u < hi - 300:
            L = 450 + ((int(u) // 500) * 37 % 7) * 140
            e0, e1 = (c + out * 380, c + out * 420) if out > 0 else (c + out * 420, c + out * 380)
            if o == 'H': add(u, e0, z - 650 - L, u + 110, e1, z - 650, 'leaf2', 'hang')
            else: add(e0, u, z - 650 - L, e1, u + 110, z - 650, 'leaf2', 'hang')
            u += 520
    for z in (F2, F3, F4, RF):
        trough('H', YA, XA, XD, z, -1)
        trough('H', YC, XB, XC, z, +1)
    for z in (F2, F3):
        trough('H', YD, XB, XC, z, -1)
    for z in (F2, F3, F4):
        trough('V', XC, YC, YD, z, -1)
    trough('V', XB, YC, YD, F2, +1)
    # ---------------- BBQ deck pergola (F4 level, on the E wing roof)
    ex0, ey0, ex1, ey1 = WING['E']
    x = ex0 + 300
    while x < ex1 - 1600:
        add(x - 40, ey0 + 200, F4 + 2600, x + 40, ey1 - 200, F4 + 2800, 'timber', 'pergola'); x += 500
    for (px, py) in ((ex0 + 200, ey0 + 300), (ex1 - 1600, ey0 + 300), (ex0 + 200, ey1 - 300), (ex1 - 1600, ey1 - 300)):
        add(px - 80, py - 80, F4, px + 80, py + 80, F4 + 2600, 'steel', 'pergola')
    # ---------------- PV on the top roof (one row of portrait modules)
    pv = 0
    for (x0, y0, x1, y1) in PV_ROWS:
        x = x0
        while x + 1130 <= x1:
            add(x, y0, RF + 300, x + 1130, y0 + 2280, RF + 360, 'pv', 'pv'); pv += 1; x += 1160
    INFO_PV['n'] = pv
    # ---------------- main stair (interior helix: U along Y, floor landing north)
    sx0 = STAIR_R[0] + 50
    xa0, xa1 = sx0, sx0 + STAIR_W; xb0, xb1 = sx0 + STAIR_W + 100, sx0 + 2 * STAIR_W + 100
    yN = STAIR_R[3] - 40 - STAIR_LAND; yS = yN - 9 * TREAD
    for fl in (1, 2, 3):
        base = FFL[fl]
        for i in range(10):
            add(xa0, yN - (i + 1) * TREAD, base + i * RISE - 150, xa1, yN - i * TREAD, base + (i + 1) * RISE, 'concrete', 'stair')
        add(xa0, yS - STAIR_LAND, base + 10 * RISE - 200, xb1, yS, base + 10 * RISE, 'concrete', 'stair')
        for i in range(10):
            add(xb0, yS + i * TREAD - TREAD, base + 10 * RISE + i * RISE - 150, xb1, yS + i * TREAD, base + 10 * RISE + (i + 1) * RISE, 'concrete', 'stair')
    # ---------------- private master stair F3 -> F4 (same geometry)
    ps = find(PSN, 3)
    pa0, pa1 = ps.x0 + 50, ps.x0 + 50 + STAIR_W; pb0, pb1 = pa1 + 100, pa1 + 100 + STAIR_W
    pN = ps.y1 - 40 - STAIR_LAND; pS = pN - 9 * TREAD
    for i in range(10):
        add(pa0, pN - (i + 1) * TREAD, F3 + i * RISE - 150, pa1, pN - i * TREAD, F3 + (i + 1) * RISE, 'timber', 'stair')
    add(pa0, pS - STAIR_LAND, F3 + 10 * RISE - 200, pb1, pS, F3 + 10 * RISE, 'timber', 'stair')
    for i in range(10):
        add(pb0, pS + i * TREAD - TREAD, F3 + 10 * RISE + i * RISE - 150, pb1, pS + i * TREAD, F3 + 10 * RISE + (i + 1) * RISE, 'timber', 'stair')
    # ---------------- site
    add(0, 0, -300, LOT_W, LOT_D, -1, 'lawn', 'ground')
    add(-4000, LOT_D, -300, LOT_W + 4000, LOT_D + ROAD_W, -1, 'asphalt', 'road')
    p = POOL; add(p[0], p[1], -1400, p[2], p[3], 40, 'water', 'pool')
    for r in rect_decompose(sbox(*POOL_DECK).difference(sbox(*p))):
        add(r[0], r[1], -300, r[2], r[3], 30, 'deck', 'deck')
    for r in (DRIVE, WALK):
        add(r[0], r[1], -300, r[2], r[3], 20, 'paving', 'paving')
    fh = FENCE_H
    add(0, 0, 0, LOT_W, 120, fh, 'brick', 'fence')
    add(0, 0, 0, 120, LOT_D, fh, 'brick', 'fence')
    add(LOT_W - 120, 0, 0, LOT_W, LOT_D, fh, 'brick', 'fence')
    add(0, LOT_D - 120, 0, WALK[0], LOT_D, 1200, 'brick', 'fence')
    add(DRIVE[2], LOT_D - 120, 0, LOT_W, LOT_D, 1200, 'brick', 'fence')
    return BX, ROOFS

INFO_PV = {}

TREES = [  # (x, y, canopy radius, height)
    (TREE_C[0], TREE_C[1], 1800, 7500), (2000, 2500, 1500, 6000), (23500, 2000, 1500, 6000), (28200, 6000, 1300, 5500),
    (28200, 26500, 1500, 6000), (1800, 27000, 1400, 5500), (1800, 12000, 1200, 5000),
]

if __name__ == '__main__':
    BX, ROOFS = build()
    from collections import Counter
    print(len(BX), Counter(b.cat for b in BX))
    for rg, z, k in ROOFS: print('roof', k, z, round(rg.area / 1e6, 2))
    print('PV modules', INFO_PV['n'], '-> %.1f kWp @0.55' % (INFO_PV['n'] * 0.55))
    json.dump(dict(boxes=[[round(v) for v in b.d()['b']] + [b.mat, b.cat] for b in BX if isinstance(b, B)],
                   prisms=[dict(x=[round(b.x0), round(b.x1)], p=[[round(y), round(z)] for y, z in b.poly], m=b.mat, c=b.cat) for b in BX if isinstance(b, P)],
                   trees=TREES), open('rv7_model.json', 'w'), separators=(',', ':'))
    print('json', len(open('rv7_model.json').read()) // 1024, 'KB')
