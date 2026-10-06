# -*- coding: utf-8 -*-
"""3D box model (single source for elevations, sections, roof plan and Blender)."""
import json
from shapely.geometry import box as sbox, Polygon, LineString, MultiLineString
from shapely.ops import unary_union
from frame3 import *
from plan3 import FLOORS, COURTS, find
from walls3 import model, side_of
from draw3 import columns, COL

FFL = {1: F1, 2: F2, 3: F3, 4: RF}
TOP = {1: F2 - SLAB, 2: F3 - SLAB, 3: RF - 250}     # underside of slab above
ROOF_T = 250

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

def build():
    M = model()
    BX = []
    add = lambda *a, **k: BX.append(B(*a, **k))
    # ---------------- ground plinth / F1 slab
    A1 = region(1)
    low = region(1, ('park',)) .union(sbox(*find('มุขรถเทียบ (Porte-cochère)').rect()))
    for r in rect_decompose(A1.difference(low)):
        add(r[0], r[1], -300, r[2], r[3], F1, 'stone', 'plinth')
    for r in rect_decompose(low):
        add(r[0], r[1], -300, r[2], r[3], GARAGE_Z, 'paving', 'plinth')
    # ---------------- floor slabs F2, F3
    for fl in (2, 3):
        for r in FLOORS[fl]:
            if r.kind == 'void': continue
            if r.kind == 'stair':
                add(r.x0, r.y1 - 1580, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab')
                continue
            add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab')
    # ---------------- roofs (A_k - A_k+1)
    A = {k: region(k) for k in (1, 2, 3)}
    A[4] = Polygon()
    ROOFS = []
    for k in (1, 2, 3):
        rg = A[k].difference(A[k + 1]) if not A[k + 1].is_empty else A[k]
        zr = FFL[k + 1]
        kind = 'green' if k < 3 else 'main'
        if k == 2: kind = 'green2'
        ROOFS.append((rg, zr, kind))
        for r in rect_decompose(rg):
            add(r[0], r[1], zr - ROOF_T, r[2], r[3], zr, 'concrete', 'roof', kind)
            if kind != 'main':
                add(r[0] + 1, r[1] + 1, zr, r[2] - 1, r[3] - 1, zr + 150, 'greenroof', 'groof')
        # parapets on edges not abutting higher mass
        bnd = rg.boundary
        if not A[k + 1].is_empty:
            bnd = bnd.difference(A[k + 1].buffer(30))
        lines = [bnd] if bnd.geom_type == 'LineString' else list(getattr(bnd, 'geoms', []))
        ph = 600 if kind == 'main' else 450
        for ln in lines:
            cs = list(ln.coords)
            for (xa, ya), (xb, yb) in zip(cs, cs[1:]):
                if abs(xa - xb) < 1 and abs(ya - yb) < 1: continue
                if abs(ya - yb) < 1:   # horizontal edge
                    inside_up = rg.contains(sbox(min(xa, xb) + 5, ya + 5, max(xa, xb) - 5, ya + 50)) if abs(xb - xa) > 20 else False
                    y0, y1 = (ya, ya + 150) if inside_up else (ya - 150, ya)
                    add(min(xa, xb), y0, zr, max(xa, xb), y1, zr + ph, 'render', 'parapet')
                else:
                    inside_r = rg.contains(sbox(xa + 5, min(ya, yb) + 5, xa + 50, max(ya, yb) - 5)) if abs(yb - ya) > 20 else False
                    x0, x1 = (xa, xa + 150) if inside_r else (xa - 150, xa)
                    add(x0, min(ya, yb), zr, x1, max(ya, yb), zr + ph, 'render', 'parapet')
    # ---------------- walls with openings
    MAT = {1: 'stone', 2: 'render', 3: 'render'}
    for fl in (1, 2, 3):
        segs, ops = M[fl]['segs'], M[fl]['ops']
        z0, z1 = FFL[fl], TOP[fl]
        H = z1 - z0
        for s in segs:
            if s.wt not in ('ext', 'int', 'wet', 'rail'): continue
            h = s.th / 2
            mat = MAT[fl] if s.wt == 'ext' else 'plaster'
            if s.wt == 'ext' and fl == 1 and s.a.kind in ('room', 'svc', 'wet') and s.a.y1 <= Y(13200) + 1:
                mat = 'stone'
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
                if s.a.kind == 'void' or (s.b is not None and s.b.kind == 'void'):
                    head = H
                wb(o.lo, o.hi, z0, z0 + sill)
                wb(o.lo, o.hi, z0 + head, z1)
                # infill
                if o.kind in ('win', 'glass', 'slide', 'slide1', 'louver'):
                    m = 'louver' if o.kind == 'louver' else 'glass'
                    if s.o == 'H': add(o.lo, s.c - 15, z0 + sill, o.hi, s.c + 15, z0 + head, m, 'glass', o.tag)
                    else: add(s.c - 15, o.lo, z0 + sill, s.c + 15, o.hi, z0 + head, m, 'glass', o.tag)
                elif o.kind in ('door', 'door2', 'lift'):
                    m = 'timber' if s.b is None or o.kind == 'door2' else 'door'
                    if s.o == 'H': add(o.lo, s.c - 25, z0, o.hi, s.c + 25, z0 + head, m, 'door', o.tag)
                    else: add(s.c - 25, o.lo, z0, s.c + 25, o.hi, z0 + head, m, 'door', o.tag)
                u = o.hi
            wb(u, s.hi + h, z0, z1)
            # slab-edge band in front of ext walls (spandrel) between z1 and next FFL
            if s.wt == 'ext':
                wb(s.lo - h, s.hi + h, z1, FFL[fl + 1] if fl < 3 else RF, 'concrete' if fl < 3 else 'render', 'band')
    # void / double-height: F2 voids walls already modelled (void is a room kind with ext walls)
    # ---------------- columns
    for fl in (1, 2, 3):
        for (x, y) in columns(fl):
            add(x - COL / 2, y - COL / 2, (0 if fl == 1 else FFL[fl]), x + COL / 2, y + COL / 2, FFL[fl + 1] if fl < 3 else RF, 'concrete', 'column')
    # ---------------- crown bar: CACTUS skin fins (south + west + east ends)
    bar_y0, bar_x0, bar_x1 = Y(6000), 9400, 34200
    x = bar_x0 + 300
    while x < bar_x1 - 200:
        add(x - 40, bar_y0 - 550, F3 - SLAB - 300, x + 40, bar_y0 - 100, RF + 600, 'timber', 'fin')
        x += 600
    for yy in range(int(bar_y0 + 400), int(Y(13200)), 600):
        add(bar_x0 - 550, yy - 40, F3 - SLAB - 300, bar_x0 - 100, yy + 40, RF + 600, 'timber', 'fin')
    # canopy over terrace edge already roof; F1 south deep eave (shading) — horizontal brise-soleil at +3.40
    add(14200, Y(6000) - 1200, F2 - 700, 26800, Y(6000), F2 - 550, 'timber', 'shade')
    # west service veranda screen (perforated / lattice) F1
    for yy in range(int(Y(13200) + 150), int(Y(24000)), 300):
        add(5800 - 100, yy - 40, F1, 5800 + 0, yy + 40, F2 - SLAB, 'timber', 'fin')
    # Junior suite west/east fins F2
    for yy in range(int(Y(17400) + 200), int(Y(24000)), 450):
        add(5800 - 450, yy - 35, F2 - 200, 5800 - 100, yy + 35, F3, 'timber', 'fin')
        add(34200 + 100, yy - 35, F2 - 200, 34200 + 450, yy + 35, F3, 'timber', 'fin')
    # ---------------- TERMITE solar chimney
    sh = find('ปล่องลม Termite', 1)
    add(sh.x0, sh.y0, RF, sh.x1, sh.y0 + 100, CHIMNEY, 'glass', 'chimney')
    add(sh.x0, sh.y1 - 100, RF, sh.x1, sh.y1, CHIMNEY, 'glass', 'chimney')
    add(sh.x0, sh.y0, RF, sh.x0 + 100, sh.y1, CHIMNEY, 'render', 'chimney')
    add(sh.x1 - 100, sh.y0, RF, sh.x1, sh.y1, CHIMNEY, 'louver', 'chimney')
    add(sh.x0 - 400, sh.y0 - 400, CHIMNEY, sh.x1 + 400, sh.y1 + 400, CHIMNEY + 200, 'concrete', 'chimney')
    # stair core vertical walls through roof? (core rises with roof +11.40 only)
    # ---------------- PV array on crown-bar roof (44 x 550 Wp)
    PV = []
    for row in (Y(6000) + 900, Y(6000) + 3700):
        x = 10100
        while x + 1000 < 33900:
            add(x, row, RF + 300, x + 1000, row + 2000, RF + 360, 'pv', 'pv')
            PV.append((x, row)); x += 1100
    # garage open front shown as shadow plane (elevation only)
    g = find('โรงจอดรถ 4 คัน')
    add(g.x0 + 200, g.y1 - 30, GARAGE_Z, g.x1 - 200, g.y1 - 10, F2 - SLAB, 'shadow', 'opening')
    # ---------------- stairs (stepped solids)
    st = find('บันไดหลัก', 1)
    xw0, xw1 = st.x0 + 100, st.x0 + 100 + STAIR_W
    xe0, xe1 = st.x1 - 100 - STAIR_W, st.x1 - 100
    yN = st.y1 - 1580; yS = yN - 9 * TREAD
    for fl in (1, 2):
        base = FFL[fl]
        for i in range(10):     # flight 1: west, going south (up)
            y_hi = yN - i * TREAD; y_lo = y_hi - TREAD
            if i == 9: y_lo = st.y0      # last tread runs into mid landing
            add(xw0, y_lo if i < 9 else yS - 1, base + i * RISE - 200, xw1, y_hi, base + (i + 1) * RISE, 'concrete', 'stair')
        add(st.x0, st.y0, base + 10 * RISE - SLAB, st.x1, yS, base + 10 * RISE, 'concrete', 'stair')    # mid landing
        for i in range(10):     # flight 2: east, going north
            y_lo = yS + i * TREAD; y_hi = y_lo + TREAD
            add(xe0, y_lo, base + 10 * RISE + i * RISE - 200, xe1, y_hi, base + 10 * RISE + (i + 1) * RISE, 'concrete', 'stair')
    # ---------------- site
    add(0, 0, -300, LOT_W, LOT_D, -1, 'lawn', 'ground')
    add(0, LOT_D, -300, LOT_W, LOT_D + ROAD_W, -1, 'asphalt', 'road')
    p = POOL; add(p[0], p[1], -1400, p[2], p[3], 40, 'water', 'pool')
    add(POOL_DECK[0], POOL_DECK[1], -300, POOL_DECK[2], POOL_DECK[3], 20, 'deck', 'deck')
    pv = PAVILION
    for (px, py) in ((pv[0] + 200, pv[1] + 200), (pv[2] - 200, pv[1] + 200), (pv[0] + 200, pv[3] - 200), (pv[2] - 200, pv[3] - 200)):
        add(px - 125, py - 125, 50, px + 125, py + 125, 2900, 'timber', 'pavilion')
    add(pv[0] - 600, pv[1] - 600, 2900, pv[2] + 600, pv[3] + 600, 3150, 'render', 'pavilion')
    add(pv[0], pv[1], -300, pv[2], pv[3], 150, 'deck', 'pavilion')
    for r in (DRIVE, WALK):
        add(r[0], r[1], -300, r[2], r[3], 20, 'paving', 'paving')
    add(RAMP[0], RAMP[1], -300, RAMP[2], RAMP[3], 300, 'paving', 'ramp')
    # courts: water + gravel
    wc = COURTS[0][1]
    add(wc[0] + 600, wc[1] + 600, -400, wc[2] - 600, wc[3] - 3200, COURT_Z - 100, 'water', 'pond')
    for nm, c in COURTS[1:]:
        add(c[0], c[1], -300, c[2], c[3], COURT_Z, 'gravel', 'court')
    add(wc[0], wc[1], -300, wc[2], wc[3], COURT_Z - 150, 'gravel', 'court')
    # boundary fence (S, E, W) + front fence with gates
    fh = FENCE_H
    add(0, 0, 0, LOT_W, 120, fh, 'render', 'fence')
    add(0, 0, 0, 120, LOT_D, fh, 'render', 'fence')
    add(LOT_W - 120, 0, 0, LOT_W, LOT_D, fh, 'render', 'fence')
    add(0, LOT_D - 120, 0, DRIVE[0], LOT_D, fh, 'render', 'fence')
    add(WALK[2], LOT_D - 120, 0, LOT_W, LOT_D, 1200, 'render', 'fence')
    return BX, ROOFS

TREES = [  # (x, y, canopy radius, height)
    (25400, Y(15300), 3200, 9000),     # rain tree in Termite court
    (3000, 37000, 2200, 7000), (37000, 37000, 2200, 7000), (37500, 26000, 2400, 7500), (37500, 13000, 2400, 7500),
    (3000, 4500, 2200, 6500), (9000, 2200, 1800, 6000), (31000, 9500 - 900, 1500, 5000), (2800, 21000, 1800, 6000),
]

if __name__ == '__main__':
    BX, ROOFS = build()
    from collections import Counter
    print(len(BX), Counter(b.cat for b in BX))
    for rg, z, k in ROOFS: print('roof', k, z, round(rg.area / 1e6, 2))
    json.dump(dict(boxes=[b.d() for b in BX], trees=TREES), open('gw3_model.json', 'w'))
    print('json', len(open('gw3_model.json').read()) // 1024, 'KB')
