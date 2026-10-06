# -*- coding: utf-8 -*-
"""3D model: boxes B + X-prisms P (single source for elevations, sections, roof plan and Blender)."""
import math
import json
from shapely.geometry import box as sbox, Polygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from frame6 import *
from plan6 import FLOORS, COURTS, find
from walls6 import model, side_of
from draw6 import columns, COL

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

def under(y): return roof_z(y) - ROOF_T

PSN = 'บันไดส่วนตัว Master'
MAIN = 'บันไดหลัก (โถงไม้)'
SKY = (8100, 12650, 21200, 14200)          # ridge skylight band in the north slope over the hall void

def roof_pieces():
    """asymmetric gable: (x0, x1, ya, yb, mat, cat) strips; slope planes from roof_z"""
    X0, X1 = BLK[0] - OVER_EW, BLK[2] + OVER_EW
    ys, yn = BLK[1] - OVER_S, BLK[3] + OVER_N
    out = [(X0, X1, ys, RIDGE_Y, 'roofmetal', 'roof')]
    out += [(X0, SKY[0], RIDGE_Y, yn, 'roofmetal', 'roof'), (SKY[2], X1, RIDGE_Y, yn, 'roofmetal', 'roof'),
            (SKY[0], SKY[2], RIDGE_Y, SKY[1], 'roofmetal', 'roof'), (SKY[0], SKY[2], SKY[3], yn, 'roofmetal', 'roof'),
            (SKY[0], SKY[2], SKY[1], SKY[3], 'glass', 'skylight')]
    return out

def slab_poly(ya, yb, t=ROOF_T, top=None):
    top = top or roof_z
    return [(ya, top(ya) - t), (yb, top(yb) - t), (yb, top(yb)), (ya, top(ya))]

def build():
    M = model()
    BX = []
    add = lambda *a, **k: BX.append(B(*a, **k))
    addp = lambda *a, **k: BX.append(P(*a, **k))
    # ---------------- ground slab: F1 +0.45, garage +0.15
    A1 = unary_union([sbox(*r.rect()) for r in FLOORS[1] if r.kind not in ('fstair', 'core')])
    low = region(1, ('park',))
    for r in rect_decompose(A1.difference(low)):
        add(r[0], r[1], -300, r[2], r[3], F1, 'stone', 'plinth')
    for r in rect_decompose(low):
        add(r[0], r[1], -300, r[2], r[3], GARAGE_Z, 'paving', 'plinth')
    # ---------------- floor slabs F2..F4 (timber deck on balconies / bridges)
    for fl in (2, 3, 4):
        for r in FLOORS[fl]:
            if r.kind in ('void', 'core', 'fstair', 'lift'): continue
            if r.name == MAIN:          # floor landing at the south end only (stair shaft open)
                add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y0 + 40 + STAIR_LAND, FFL[fl], 'concrete', 'slab'); continue
            if r.name == PSN and fl == 4:   # private stair: only the north floor landing at F4
                add(r.x0, r.y1 - 40 - STAIR_LAND, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], 'concrete', 'slab'); continue
            m = 'deck' if (r.kind == 'inb' or r.name.startswith('สะพานไม้')) else 'concrete'
            add(r.x0, r.y0, FFL[fl] - SLAB, r.x1, r.y1, FFL[fl], m, 'slab', r.kind)
    # ---------------- flat roofs where nothing is above (garage canopy strip, light-court floors) - F4 has the gable
    full = {k: unary_union([sbox(*r.rect()) for r in FLOORS[k] if r.kind not in ('fstair', 'core')]) for k in FLS}
    ROOFS = []
    for k in (1, 2, 3):
        rg = full[k].difference(full[k + 1])
        if rg.is_empty or rg.area < 1e5: continue
        zr = FFL[k + 1]
        kind = 'court' if k == 2 else 'flat'
        ROOFS.append((rg, zr, kind))
        for r in rect_decompose(rg):
            add(r[0], r[1], zr - 250, r[2], r[3], zr, 'concrete', 'roof', kind)
            add(r[0] + 1, r[1] + 1, zr, r[2] - 1, r[3] - 1, zr + 100, 'gravel' if kind == 'court' else 'greenroof', 'groof')
        bnd = rg.boundary.difference(full[k + 1].buffer(30))
        lines = [bnd] if bnd.geom_type == 'LineString' else list(getattr(bnd, 'geoms', []))
        ph = 450 if kind == 'flat' else 1100
        for ln in lines:
            cs = list(ln.coords)
            for (xa, ya), (xb, yb) in zip(cs, cs[1:]):
                if abs(xa - xb) < 1 and abs(ya - yb) < 1: continue
                if abs(ya - yb) < 1:
                    inside_up = rg.contains(sbox(min(xa, xb) + 5, ya + 5, max(xa, xb) - 5, ya + 50)) if abs(xb - xa) > 20 else False
                    y0, y1 = (ya, ya + 120) if inside_up else (ya - 120, ya)
                    add(min(xa, xb), y0, zr, max(xa, xb), y1, zr + ph, 'timber' if kind == 'court' else 'render', 'parapet')
                else:
                    inside_r = rg.contains(sbox(xa + 5, min(ya, yb) + 5, xa + 50, max(ya, yb) - 5)) if abs(yb - ya) > 20 else False
                    x0, x1 = (xa, xa + 120) if inside_r else (xa - 120, xa)
                    add(x0, min(ya, yb), zr, x1, max(ya, yb), zr + ph, 'timber' if kind == 'court' else 'render', 'parapet')
    # ---------------- walls with openings (F1 white lime render base, F2-F4 timber-clad RC/block, F4 walls follow the roof)
    for fl in FLS:
        segs, ops = M[fl]['segs'], M[fl]['ops']
        z0 = FFL[fl]
        for s in segs:
            if s.wt not in ('ext', 'int', 'wet', 'rail'): continue
            h = s.th / 2
            if fl < 4:
                z1 = TOP[fl]; z1v = None
            elif s.o == 'H':
                z1 = under(s.c); z1v = None
            else:
                z1 = min(under(s.lo - s.th / 2), under(s.hi + s.th / 2)); z1v = True
            H = z1 - z0
            if s.wt == 'ext':
                mat = 'render' if fl == 1 else 'timberclad'
            else:
                mat = 'plaster'
            def wb(u0, u1, za, zb, m=mat, cat='wall', tag=''):
                if u1 - u0 < 1 or zb - za < 1: return
                if s.o == 'H': add(u0, s.c - h, za, u1, s.c + h, zb, m, cat, tag)
                else: add(s.c - h, u0, za, s.c + h, u1, zb, m, cat, tag)
            if s.wt == 'rail':
                rm = 'steel' if 'fstair' in (s.a.kind, s.b.kind if s.b else '') else 'glass'
                if s.o == 'H': add(s.lo, s.c - 10, z0, s.hi, s.c + 10, z0 + 1100, rm, 'rail')
                else: add(s.c - 10, s.lo, z0, s.c + 10, s.hi, z0 + 1100, rm, 'rail')
                if rm == 'glass':       # timber handrail cap
                    if s.o == 'H': add(s.lo, s.c - 40, z0 + 1050, s.hi, s.c + 40, z0 + 1120, 'timber', 'rail')
                    else: add(s.c - 40, s.lo, z0 + 1050, s.c + 40, s.hi, z0 + 1120, 'timber', 'rail')
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
            if z1v:       # raked infill up to the roof underside (gable walls / walls across the slope)
                ya, yb = s.lo - h, s.hi + h
                pts = [(ya, z1), (yb, z1), (yb, under(yb))]
                if ya < RIDGE_Y < yb: pts.append((RIDGE_Y, under(RIDGE_Y)))
                pts.append((ya, under(ya)))
                addp(s.c - h, s.c + h, pts, mat, 'wall')
            if s.wt == 'ext' and fl < 4:
                wb(s.lo - h, s.hi + h, z1, FFL[fl + 1], 'timber' if fl > 1 else 'concrete', 'band')
    # ---------------- RC columns
    for fl in FLS:
        for (x, y) in columns(fl):
            zt = FFL[fl + 1] if fl < 4 else under(y + (COL / 2 if y < RIDGE_Y else -COL / 2) * 0)
            add(x - COL / 2, y - COL / 2, (0 if fl == 1 else FFL[fl]), x + COL / 2, y + COL / 2, min(zt, under(y)) if fl == 4 else zt, 'concrete', 'column')
    # ---------------- asymmetric gable roof + ridge skylight + gutters
    for (x0, x1, ya, yb, m, c) in roof_pieces():
        pts = slab_poly(ya, yb, ROOF_T if c == 'roof' else 120)
        if ya < RIDGE_Y < yb: pts = [pts[0], (RIDGE_Y, under(RIDGE_Y)), pts[1], pts[2], (RIDGE_Y, RIDGE), pts[3]]
        if c == 'skylight':
            pts = [(ya, roof_z(ya) - 60), (yb, roof_z(yb) - 60), (yb, roof_z(yb) + 40), (ya, roof_z(ya) + 40)]
        addp(x0, x1, pts, m, c)
    X0, X1 = BLK[0] - OVER_EW, BLK[2] + OVER_EW
    ys, yn = BLK[1] - OVER_S, BLK[3] + OVER_N
    add(X0, ys - 200, roof_z(ys) - 350, X1, ys, roof_z(ys) - 50, 'steel', 'gutter')
    add(X0, yn, roof_z(yn) - 350, X1, yn + 200, roof_z(yn) - 50, 'steel', 'gutter')
    add(X0, RIDGE_Y - 150, RIDGE - 10, X1, RIDGE_Y + 150, RIDGE + 60, 'roofmetal', 'ridge')
    # ---------------- PV on the south slope (2 rows of 1.13 x 2.28 m modules, portrait)
    pv = 0
    ly = 2280 * math.cos(math.atan(SLOPE_S))
    for ya in (BLK[1] + 300, BLK[1] + 300 + ly + 150):
        yb = ya + ly
        x = BLK[0] + 400
        while x + 1130 <= BLK[2] - 400:
            addp(x, x + 1130, [(ya, roof_z(ya) + 60), (yb, roof_z(yb) + 60), (yb, roof_z(yb) + 100), (ya, roof_z(ya) + 100)], 'pv', 'pv')
            pv += 1; x += 1160
    INFO_PV['n'] = pv
    # ---------------- timber exoskeleton: south posts + raking struts, north posts, rafters on every frame line, edge beams
    for x in FRAME_X:
        yp0, yp1 = FRAME_S_Y - POST_D, FRAME_S_Y
        add(x - POST_W / 2, yp0, 0, x + POST_W / 2, yp1, under(yp0), 'glulam', 'exo')
        add(x - POST_W / 2 - 60, yp0 - 60, 0, x + POST_W / 2 + 60, yp1 + 60, 300, 'steel', 'exo')      # steel shoe on footing
        ye = ys + 200
        zs = YJOINT
        addp(x - POST_W / 2 + 20, x + POST_W / 2 - 20, [(yp0, zs), (yp0, zs + 360), (ye + 180, under(ye + 180)), (ye, under(ye))], 'glulam', 'exo')
        # exposed rafter under the roof from eave to eave
        pts = [(ys + 100, under(ys + 100) - RAFTER_D), (RIDGE_Y, under(RIDGE_Y) - RAFTER_D), (yn - 100, under(yn - 100) - RAFTER_D),
               (yn - 100, under(yn - 100)), (RIDGE_Y, under(RIDGE_Y)), (ys + 100, under(ys + 100))]
        addp(x - RAFTER_W / 2, x + RAFTER_W / 2, pts, 'glulam', 'rafter')
    for x in FRAME_N_X:
        add(x - POST_W / 2, FRAME_N_Y - POST_D / 2, GARAGE_Z, x + POST_W / 2, FRAME_N_Y + POST_D / 2, under(FRAME_N_Y + POST_D / 2), 'glulam', 'exo')
    for z in (F2, F3, F4):
        add(BLK[0] - 120, FRAME_S_Y - POST_D, z - 500, BLK[2] + 120, FRAME_S_Y - POST_D + 200, z, 'glulam', 'exo')     # balcony edge beam
    add(BLK[0] - 120, FRAME_N_Y - 100, F2 - 600, FRAME_N_X[-1] + 120, FRAME_N_Y + 100, F2 - 100, 'glulam', 'exo')          # garage front beam
    # gable lattice (diagonal timber slats) at both ends above the F4 walls / open terraces
    for xg in (BLK[0] - 200, BLK[2] + 140):
        for k in range(-12, 20):
            ya = ys + k * 1200
            for sgn in (1, -1):
                pts = []
                # slat from (ya, zb) rising at 45 deg in +/-y until it hits the roof underside
                zb = EAVE - ROOF_T - 900
                y_a, z_a = ya, zb
                L = 6000
                y_b, z_b = ya + sgn * L, zb + L
                # clip to y range and roof underside: march
                seg = []
                n = 60
                for i in range(n + 1):
                    t = i / n
                    yy, zz = y_a + (y_b - y_a) * t, z_a + (z_b - z_a) * t
                    if ys + 150 <= yy <= yn - 150 and zz <= under(yy) - 20: seg.append((yy, zz))
                if len(seg) < 2: continue
                (y1_, z1_), (y2_, z2_) = seg[0], seg[-1]
                if abs(y2_ - y1_) < 300: continue
                addp(xg, xg + 60, [(y1_ - 40, z1_), (y1_ + 40, z1_), (y2_ + 40, z2_), (y2_ - 40, z2_)], 'glulam', 'lattice')
        add(xg, ys + 100, EAVE - ROOF_T - 1000, xg + 60, yn - 100, EAVE - ROOF_T - 900, 'glulam', 'lattice')
    # ---------------- main stair (U along Y, floor landing south)
    sx0, sy0 = STAIR_R[0] + 50, STAIR_R[1] + 40
    xa0, xa1 = sx0, sx0 + STAIR_W; xb0, xb1 = sx0 + STAIR_W + 100, sx0 + 2 * STAIR_W + 100
    yS = sy0 + STAIR_LAND; yN = yS + 9 * TREAD
    for fl in (1, 2, 3):
        base = FFL[fl]
        for i in range(10):
            add(xa0, yS + i * TREAD, base + i * RISE - 150, xa1, yS + (i + 1) * TREAD, base + (i + 1) * RISE, 'timber', 'stair')
        add(xa0, yN, base + 10 * RISE - 200, xb1, yN + STAIR_LAND, base + 10 * RISE, 'timber', 'stair')
        for i in range(10):
            y_hi = yN - i * TREAD
            add(xb0, y_hi - TREAD, base + 10 * RISE + i * RISE - 150, xb1, y_hi, base + 10 * RISE + (i + 1) * RISE, 'timber', 'stair')
    # ---------------- private master stair F3 -> F4 (U along Y, floor landings north)
    ps = find(PSN, 3)
    pa0, pa1 = ps.x0 + 50, ps.x0 + 50 + STAIR_W; pb0, pb1 = pa1 + 100, pa1 + 100 + STAIR_W
    pN = ps.y1 - 40 - STAIR_LAND; pS = pN - 9 * TREAD
    for i in range(10):
        add(pa0, pN - (i + 1) * TREAD, F3 + i * RISE - 150, pa1, pN - i * TREAD, F3 + (i + 1) * RISE, 'timber', 'stair')
    add(pa0, pS - STAIR_LAND, F3 + 10 * RISE - 200, pb1, pS, F3 + 10 * RISE, 'timber', 'stair')
    for i in range(10):
        add(pb0, pS + i * TREAD - TREAD, F3 + 10 * RISE + i * RISE - 150, pb1, pS + i * TREAD, F3 + 10 * RISE + (i + 1) * RISE, 'timber', 'stair')
    # ---------------- external fire stair (steel, flights along X, floor landing east)
    fs = find('บันไดหนีไฟภายนอก', 1)
    X0_, Y0_ = fs.x0 + 40, fs.y0 + 50
    fx0 = X0_ + 1150 + 9 * TREAD
    ay0, ay1 = Y0_ + 1200, Y0_ + 2300
    for fl in (1, 2, 3):
        base = FFL[fl] if fl > 1 else 0
        rise = (FFL[fl + 1] - base) / 20
        for i in range(10):
            xa = fx0 - (i + 1) * TREAD
            add(xa, ay0, base + i * rise - 120, xa + TREAD, ay1, base + (i + 1) * rise, 'steel', 'stair')
        add(X0_, Y0_, base + 10 * rise - 150, X0_ + 1150, Y0_ + 2300, base + 10 * rise, 'steel', 'stair')
        for i in range(10):
            xa = X0_ + 1150 + i * TREAD
            add(xa, Y0_, base + 10 * rise + i * rise - 120, xa + TREAD, Y0_ + 1100, base + 10 * rise + (i + 1) * rise, 'steel', 'stair')
        add(fx0, Y0_, FFL[fl + 1] - 150, fs.x1 - 40, Y0_ + 2300, FFL[fl + 1], 'steel', 'stair')
    for (px, py) in ((X0_, Y0_), (X0_, Y0_ + 2200), (fs.x1 - 140, Y0_), (fs.x1 - 140, Y0_ + 2200)):
        add(px, py, 0, px + 100, py + 100, F4 + 1100, 'steel', 'stair')
    # ---------------- site
    add(0, 0, -300, LOT_W, LOT_D, -1, 'lawn', 'ground')
    add(-4000, LOT_D, -300, LOT_W + 4000, LOT_D + ROAD_W, -1, 'asphalt', 'road')
    p = POOL; add(p[0], p[1], -1400, p[2], p[3], 40, 'water', 'pool')
    pd = POOL_DECK
    for r in rect_decompose(sbox(*pd).difference(sbox(*p))):
        add(r[0], r[1], -300, r[2], r[3], 30, 'deck', 'deck')
    for r in (DRIVE, WALK, PIAZZA):
        add(r[0], r[1], -300, r[2], r[3], 20, 'paving', 'paving')
    fh = FENCE_H
    add(0, 0, 0, LOT_W, 120, fh, 'render', 'fence')
    add(0, 0, 0, 120, LOT_D, fh, 'render', 'fence')
    add(LOT_W - 120, 0, 0, LOT_W, LOT_D, fh, 'render', 'fence')
    add(WALK[2], LOT_D - 120, 0, LOT_W, LOT_D, 1200, 'timber', 'fence')
    add(0, LOT_D - 120, 0, DRIVE[0], LOT_D, 1200, 'timber', 'fence')
    add(DRIVE[2], LOT_D - 120, 0, WALK[0], LOT_D, 1200, 'timber', 'fence')
    return BX, ROOFS

INFO_PV = {}

TREES = [  # (x, y, canopy radius, height)
    (1800, 5200, 1600, 6500), (21800, 2400, 1700, 6500), (28300, 3000, 1400, 5500), (28300, 10500, 1500, 6000),
    (1700, 26500, 1500, 5500), (25800, 27800, 1600, 6500), (1800, 15000, 1200, 5000),
]

if __name__ == '__main__':
    BX, ROOFS = build()
    from collections import Counter
    print(len(BX), Counter(b.cat for b in BX))
    for rg, z, k in ROOFS: print('roof', k, z, round(rg.area / 1e6, 2))
    print('PV modules', INFO_PV['n'], '-> %.1f kWp @0.55' % (INFO_PV['n'] * 0.55))
    json.dump(dict(boxes=[[round(v) for v in b.d()['b']] + [b.mat, b.cat] for b in BX if isinstance(b, B)],
                   prisms=[dict(x=[round(b.x0), round(b.x1)], p=[[round(y), round(z)] for y, z in b.poly], m=b.mat, c=b.cat) for b in BX if isinstance(b, P)],
                   trees=TREES), open('fo6_model.json', 'w'), separators=(',', ':'))
    print('json', len(open('fo6_model.json').read()) // 1024, 'KB')
