# -*- coding: utf-8 -*-
"""3D box model (single source for elevations, sections, roof plan and Blender)."""
import math
import json
from shapely.geometry import box as sbox, Polygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from frame4 import *
from plan4 import FLOORS, COURTS, find
from walls4 import model, side_of
from draw4 import columns, COL

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

def cyl_slices(z0, z1, mat='brick', cat='cylslice', n=40):
    """solid cylinder approximated by axis-aligned slices (for orthographic projection)"""
    import math
    cx, cy = CORE_C; R_ = CORE_R
    out = []
    for i in range(n):
        xa = cx - R_ + 2 * R_ * i / n; xb = cx - R_ + 2 * R_ * (i + 1) / n
        xm = (xa + xb) / 2
        h = math.sqrt(max(0, R_ * R_ - (xm - cx) ** 2))
        out.append(B(xa, cy - h, z0, xb, cy + h, z1, mat, cat))
    return out

OPEN_SKY = {'ระเบียงตะวันออก ชั้น 3', 'ระเบียง Master (ดาดฟ้า)', 'บันไดหนีไฟภายนอก'}

def build():
    M = model()
    BX = []
    add = lambda *a, **k: BX.append(B(*a, **k))
    # ---------------- ground slab: enclosed F1 at +0.45, garage/pilotis at +0.15
    A1 = region(1).difference(region(1, ('fstair',)))
    low = region(1, ('park', 'inb'))
    for r in rect_decompose(A1.difference(low).difference(sbox(*CORE_SQ))):
        add(r[0], r[1], -300, r[2], r[3], F1, 'stone', 'plinth')
    for r in rect_decompose(low):
        add(r[0], r[1], -300, r[2], r[3], GARAGE_Z, 'paving', 'plinth')
    # ---------------- floor slabs F2..F4 (incl. balconies, loggias, terraces)
    for fl in (2, 3, 4):
        for r in FLOORS[fl]:
            if r.kind in ('void', 'core', 'fstair'): continue
            if r.kind == 'stair':      # private stair: landing strip at the east (floor landing)
                add(r.x1 - 1500, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab'); continue
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
        lines = [bnd] if bnd.geom_type == 'LineString' else list(getattr(bnd, 'geoms', []))
        ph = 600 if kind == 'main' else 450
        for ln in lines:
            cs = list(ln.coords)
            for (xa, ya), (xb, yb) in zip(cs, cs[1:]):
                if abs(xa - xb) < 1 and abs(ya - yb) < 1: continue
                if abs(ya - yb) < 1:
                    inside_up = rg.contains(sbox(min(xa, xb) + 5, ya + 5, max(xa, xb) - 5, ya + 50)) if abs(xb - xa) > 20 else False
                    y0, y1 = (ya, ya + 150) if inside_up else (ya - 150, ya)
                    add(min(xa, xb), y0, zr, max(xa, xb), y1, zr + ph, 'render', 'parapet')
                else:
                    inside_r = rg.contains(sbox(xa + 5, min(ya, yb) + 5, xa + 50, max(ya, yb) - 5)) if abs(yb - ya) > 20 else False
                    x0, x1 = (xa, xa + 150) if inside_r else (xa - 150, xa)
                    add(x0, min(ya, yb), zr, x1, max(ya, yb), zr + ph, 'render', 'parapet')
    # ---------------- walls with openings
    for fl in FLS:
        segs, ops = M[fl]['segs'], M[fl]['ops']
        z0, z1 = FFL[fl], TOP[fl]
        H = z1 - z0
        for s in segs:
            if s.wt not in ('ext', 'int', 'wet', 'rail'): continue
            h = s.th / 2
            mat = ('glass_brick' if False else ('render' if fl > 1 else 'concrete')) if s.wt == 'ext' else 'plaster'
            def wb(u0, u1, za, zb, m=mat, cat='wall', tag=''):
                if u1 - u0 < 1 or zb - za < 1: return
                if s.o == 'H': add(u0, s.c - h, za, u1, s.c + h, zb, m, cat, tag)
                else: add(s.c - h, u0, za, s.c + h, u1, zb, m, cat, tag)
            if s.wt == 'rail':
                rm = 'steel' if 'fstair' in (s.a.kind, s.b.kind if s.b else '') else 'glass'
                if s.o == 'H': add(s.lo, s.c - 10, z0, s.hi, s.c + 10, z0 + 1100, rm, 'rail')
                else: add(s.c - 10, s.lo, z0, s.c + 10, s.hi, z0 + 1100, rm, 'rail')
                continue
            myops = sorted([o for o in ops if o.seg is s], key=lambda o: o.lo)
            u = s.lo - h
            for o in myops:
                wb(u, o.lo, z0, z1)
                sill = o.sill; head = min(o.head, H)
                if s.a.kind == 'void' or (s.b is not None and s.b.kind == 'void'): head = H
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
                wb(s.lo - h, s.hi + h, z1, FFL[fl + 1], 'concrete', 'band')
    # ---------------- columns (pilotis)
    for fl in FLS:
        for (x, y) in columns(fl):
            add(x - COL / 2, y - COL / 2, (0 if fl == 1 else FFL[fl]), x + COL / 2, y + COL / 2, FFL[fl + 1], 'concrete', 'column')
    # ---------------- cylindrical core (brick) up to CORE_TOP
    for b_ in cyl_slices(0, CORE_TOP, 'brick'): BX.append(b_)
    # ---------------- core U-stair inside the cylinder (floor landing south)
    cx, cy = CORE_C
    xa0, xa1 = cx - 1050, cx - 50; xb0, xb1 = cx + 50, cx + 1050
    yS = cy - 2260 + STAIR_LAND; yN = yS + 9 * TREAD
    for fl in (1, 2, 3):
        base = FFL[fl]
        for i in range(10):
            y_lo = yS + i * TREAD
            add(xa0, y_lo, base + i * RISE - 150, xa1, y_lo + TREAD, base + (i + 1) * RISE, 'concrete', 'cstair')
        add(cx - 1050, yN, base + 10 * RISE - 200, cx + 1050, yN + STAIR_LAND, base + 10 * RISE, 'concrete', 'cstair')
        for i in range(10):
            y_hi = yN - i * TREAD
            add(xb0, y_hi - TREAD, base + 10 * RISE + i * RISE - 150, xb1, y_hi, base + 10 * RISE + (i + 1) * RISE, 'concrete', 'cstair')
    Ri = CORE_R - 200
    for fl in (2, 3, 4):                     # floor landing clipped to the cylinder (strips), widened west to the 205deg door
        y = cy - Ri
        while y < cy - 500:
            y1 = min(y + 100, cy - 500); dmax = max(abs(y - cy), abs(y1 - cy))
            hw = math.sqrt(max(Ri * Ri - dmax * dmax, 0))
            if y1 <= yS + 1: add(cx - hw, y, FFL[fl] - SLAB, cx + hw, y1, FFL[fl], 'concrete', 'cstair')
            elif cx - hw < xa0: add(cx - hw, y, FFL[fl] - SLAB, xa0, y1, FFL[fl], 'concrete', 'cstair')
            y = y1
    # ---------------- west BRICK LATTICE screen (openwork brick, G-Beach) F2 -> parapet, gap at fire stair
    xs0, xs1 = BAR[0] - 450, BAR[0] - 335
    zt = PARAPET
    for (ya, yb, top) in ((BAR[1], FSTAIR[1] - 300, zt), (FSTAIR[3] + 300, BAR[3], F3 + 450)):
        y = ya + 60
        while y < yb - 60:
            add(xs0, y - 58, F2 - SLAB, xs1, y + 58, top, 'brick', 'lattice'); y += 290
        z = F2
        while z < top - 100:
            add(xs0 - 10, ya, z, xs1 + 10, yb, z + 65, 'brick', 'lattice'); z += 520
    # east perimeter terrace edge: slab nosing already from balcony slabs; pergola over master terrace
    mt = find('ระเบียง Master (ดาดฟ้า)')
    x = mt.x0 + 200
    while x < mt.x1:
        add(x - 40, mt.y0, RF - 250, x + 40, mt.y1, RF - 50, 'timber', 'pergola'); x += 450
    for (px, py) in ((mt.x0 + 150, mt.y0 + 150), (mt.x1 - 150, mt.y0 + 150)):
        add(px - 100, py - 100, F4, px + 100, py + 100, RF - 250, 'steel', 'pergola')
    # ---------------- skylights over F2 office (green roof +7.25)
    for (x0, x1) in ((11000, 12600), (12500 + 400, 14100)):
        add(x0, 22600, F3 - 50, x1, 24600, F3 + 350, 'glass', 'skylight')
    # ---------------- PV on main roof
    for row in (5200, 8400, 12300, 14500, 16700):
        x = 6300
        while x + 1000 < (20000 if row < 12000 else 18800):
            if not (row < 12000 and 11300 < x + 1000 and x < 15300):
                add(x, row, RF + 300, x + 1000, row + 2000, RF + 360, 'pv', 'pv')
            x += 1100
    # ---------------- external fire stair (steel)
    fs = find('บันไดหนีไฟภายนอก', 1)
    xa0, xa1 = fs.x0 + 100, fs.x0 + 1200; xb0, xb1 = fs.x1 - 1200, fs.x1 - 100
    yS = fs.y0 + 1200; yN = yS + 9 * TREAD
    for fl in (1, 2, 3):
        base = FFL[fl] if fl > 1 else 0
        rise = (FFL[fl + 1] - base) / 20
        for i in range(10):                      # flight A (west) going north
            y_lo = yS + i * TREAD
            add(xa0, y_lo, base + i * rise - 120, xa1, y_lo + TREAD, base + (i + 1) * rise, 'steel', 'stair')
        add(fs.x0 + 100, yN, base + 10 * rise - 150, fs.x1 - 100, yN + 1200, base + 10 * rise, 'steel', 'stair')
        for i in range(10):                      # flight B (east) going south
            y_hi = yN - i * TREAD
            add(xb0, y_hi - TREAD, base + 10 * rise + i * rise - 120, xb1, y_hi, base + 10 * rise + (i + 1) * rise, 'steel', 'stair')
        add(fs.x0 + 100, fs.y0, FFL[fl + 1] - 150, fs.x1 - 100, yS, FFL[fl + 1], 'steel', 'stair')
    for (px, py) in ((fs.x0 + 100, fs.y0 + 100), (fs.x0 + 100, yN + 1200), (fs.x1 - 200, fs.y0 + 100), (fs.x1 - 200, yN + 1200)):
        add(px, py - 100, 0, px + 100, py, F4 + 1100, 'steel', 'stair')
    # ---------------- private master stair F3 -> F4 (inside)
    ps = find('บันไดส่วนตัว Master', 3)
    x0s = ps.x0 + 500; xF = x0s + 9 * TREAD + 2 * STAIR_LAND
    for i in range(10):     # flight north part going west from floor landing (east)
        xa = xF - STAIR_LAND - (i + 1) * TREAD; xb = xa + TREAD
        add(xa, ps.y1 - STAIR_W, F3 + i * RISE - 150, xb, ps.y1, F3 + (i + 1) * RISE, 'concrete', 'stair')
    add(x0s, ps.y0, F3 + 10 * RISE - 150, x0s + STAIR_LAND, ps.y1, F3 + 10 * RISE, 'concrete', 'stair')
    for i in range(10):
        xa = x0s + STAIR_LAND + i * TREAD
        add(xa, ps.y0, F3 + 10 * RISE + i * RISE - 150, xa + TREAD, ps.y0 + STAIR_W, F3 + 10 * RISE + (i + 1) * RISE, 'concrete', 'stair')
    # ---------------- site
    add(0, 0, -300, LOT_W, LOT_D, -1, 'lawn', 'ground')
    add(-4000, LOT_D, -300, LOT_W + 4000, LOT_D + ROAD_W, -1, 'asphalt', 'road')
    p = POOL; add(p[0], p[1], -1400, p[2], p[3], 40, 'water', 'pool')
    add(POOL_DECK[0], POOL_DECK[1], -300, POOL_DECK[2], POOL_DECK[3], 20, 'deck', 'deck')
    pv = PAVILION
    for (px, py) in ((pv[0] + 200, pv[1] + 200), (pv[2] - 200, pv[1] + 200), (pv[0] + 200, pv[3] - 200), (pv[2] - 200, pv[3] - 200)):
        add(px - 125, py - 125, 50, px + 125, py + 125, 2900, 'concrete', 'pavilion')
    add(pv[0] - 500, pv[1] - 500, 2900, pv[2] + 500, pv[3] + 500, 3150, 'render', 'pavilion')
    add(pv[0], pv[1], -300, pv[2], pv[3], 150, 'deck', 'pavilion')
    for r in (DRIVE, WALK):
        add(r[0], r[1], -300, r[2], r[3], 20, 'paving', 'paving')
    fh = FENCE_H
    add(0, 0, 0, LOT_W, 120, fh, 'brick', 'fence')
    add(0, 0, 0, 120, LOT_D, fh, 'brick', 'fence')
    add(LOT_W - 120, 0, 0, LOT_W, LOT_D, fh, 'brick', 'fence')
    add(0, LOT_D - 120, 0, DRIVE[0], LOT_D, fh, 'brick', 'fence')
    add(WALK[2], LOT_D - 120, 0, LOT_W, LOT_D, 1200, 'brick', 'fence')
    return BX, ROOFS

TREES = [  # (x, y, canopy radius, height)
    (2200, 2400, 1800, 6500), (12500, 1800, 1700, 6000), (19500, 1800, 1500, 5500), (28200, 27500, 1600, 6000),
    (24800, 27600, 1700, 6500), (1800, 27800, 1500, 5500), (28400, 1500, 1200, 4500),
]

if __name__ == '__main__':
    BX, ROOFS = build()
    from collections import Counter
    print(len(BX), Counter(b.cat for b in BX))
    for rg, z, k in ROOFS: print('roof', k, z, round(rg.area / 1e6, 2))
    from draw4 import core_geom
    cyl = []
    def polys(g):
        return [g] if g.geom_type == 'Polygon' else [p for p in g.geoms if p.geom_type == 'Polygon']
    from shapely.geometry import box as _b
    for fl in (1, 2, 3, 4):
        ring = core_geom(fl)[0]
        z0 = 0 if fl == 1 else FFL[fl] - SLAB
        for p in polys(ring):
            if p.interiors:
                cx, cy = CORE_C
                for half in (_b(cx - 4000, cy - 4000, cx, cy + 4000), _b(cx, cy - 4000, cx + 4000, cy + 4000)):
                    for q in polys(p.intersection(half)): cyl.append(dict(pts=[list(c) for c in q.exterior.coords][:-1], z0=z0, z1=FFL[fl + 1]))
            else:
                cyl.append(dict(pts=[list(c) for c in p.exterior.coords][:-1], z0=z0, z1=FFL[fl + 1]))
    from shapely.geometry import Point as _P
    full = _P(*CORE_C).buffer(CORE_R, 96).difference(_P(*CORE_C).buffer(CORE_R - 200, 96))
    cx, cy = CORE_C
    for half in (_b(cx - 4000, cy - 4000, cx, cy + 4000), _b(cx, cy - 4000, cx + 4000, cy + 4000)):
        for q in polys(full.intersection(half)): cyl.append(dict(pts=[list(c) for c in q.exterior.coords][:-1], z0=RF - 250, z1=CORE_TOP))
    json.dump(dict(boxes=[[round(v) for v in b.d()['b']] + [b.mat, b.cat] for b in BX if b.cat != 'cylslice'], trees=TREES, cyl=cyl,
                   core=dict(c=list(CORE_C), r=CORE_R, top=CORE_TOP, gaps={str(k): v for k, v in __import__('draw4').CORE_DOORS.items()}, ffl=[0, F2 - SLAB, F3 - SLAB, F4 - SLAB, RF])), open('gb4_model.json', 'w'), separators=(',', ':'))
    print('json', len(open('gb4_model.json').read()) // 1024, 'KB')
