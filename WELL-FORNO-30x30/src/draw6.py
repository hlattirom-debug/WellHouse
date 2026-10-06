# -*- coding: utf-8 -*-
"""Plan drawings for F1-F3 (Rec), shared helpers."""
import math
from shapely.geometry import box, Polygon as SP, MultiPolygon
from shapely.ops import unary_union
from cad6 import Rec
from plan6 import FLOORS, COURTS, find
from frame6 import *
from walls6 import model, side_of, T_EXT

def poly_rings(g):
    gs = [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
    out = []
    for p in gs:
        if p.is_empty: continue
        out.append(list(p.exterior.coords))
        for i in p.interiors: out.append(list(i.coords))
    return out

def U(s, u, v):
    """local (u along seg, v along outward normal of room a) -> world"""
    if s.o == 'H': return (u, s.c + v)
    return (s.c + v, u)

def into_sign(s, room):
    """+1 if room lies on +v side (v measured in world +y for H, +x for V)"""
    cx, cy = (room.x0 + room.x1) / 2, (room.y0 + room.y1) / 2
    return (1 if cy > s.c else -1) if s.o == 'H' else (1 if cx > s.c else -1)

def arcpts(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def wall_geom(fl, M):
    segs, ops = M[fl]['segs'], M[fl]['ops']
    walls = []
    for s in segs:
        if s.wt in ('ext', 'int', 'wet'):
            h = s.th / 2
            if s.o == 'H': walls.append(box(s.lo - h, s.c - h, s.hi + h, s.c + h))
            else: walls.append(box(s.c - h, s.lo - h, s.c + h, s.hi + h))
    W = unary_union(walls)
    cuts = []
    for o in ops:
        s = o.seg
        if s.wt not in ('ext', 'int', 'wet'): continue
        h = s.th / 2 + 5
        if s.o == 'H': cuts.append(box(o.lo, s.c - h, o.hi, s.c + h))
        else: cuts.append(box(s.c - h, o.lo, s.c + h, o.hi))
    return W, unary_union(cuts) if cuts else None

def columns(fl):
    """grid intersections inside the F1 footprint and this floor (garage: long-span columns only)"""
    from shapely.geometry import Point
    fp = unary_union([box(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[1] if r.kind not in ('fstair', 'core')])
    here = unary_union([box(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1) for r in FLOORS[fl] if r.kind not in ('fstair', 'core')])
    pts = []
    for gx in GX.values():
        for gy in GY.values():
            if gy > BLK[3]: continue
            p = Point(gx, gy)
            if fp.buffer(1).contains(p) and here.contains(p): pts.append((gx, gy))
    return pts

COL = 400

def plan(fl, furn=True, labels=True):
    M = model()
    R = Rec()
    segs, ops = M[fl]['segs'], M[fl]['ops']
    rooms = FLOORS[fl]
    # ---- floor tone / special areas
    for r in rooms:
        if r.kind == 'void':
            R.rect(r.x0, r.y0, r.x1, r.y1, 'A-HIDD', ls='--')
            R.line((r.x0, r.y0), (r.x1, r.y1), 'A-HIDD', ls='--'); R.line((r.x0, r.y1), (r.x1, r.y0), 'A-HIDD', ls='--')
        elif r.kind in ('inb', 'park'):
            R.frect(r.x0, r.y0, r.x1, r.y1, 'A-AREA', color='#ebe7dc')
        elif r.kind == 'wet':
            R.frect(r.x0, r.y0, r.x1, r.y1, 'A-AREA', color='#e6eef2')
            # 300x300 tile grid
            for x in range(int(r.x0) + 300, int(r.x1), 300): R.line((x, r.y0), (x, r.y1), 'A-HIDD', lw=0.05, c='#c9d6dc')
            for y in range(int(r.y0) + 300, int(r.y1), 300): R.line((r.x0, y), (r.x1, y), 'A-HIDD', lw=0.05, c='#c9d6dc')
    # ---- roofs of lower floors seen from this floor
    if fl >= 2:
        here = unary_union([box(r.x0, r.y0, r.x1, r.y1) for r in rooms])
        for k in range(fl - 1, 0, -1):
            below = unary_union([box(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[k] if r.kind not in ('core', 'fstair')])
            higher = unary_union([box(r.x0, r.y0, r.x1, r.y1) for kk in range(k + 1, fl + 1) for r in FLOORS[kk]])
            vis = below.difference(higher)
            for g in ([vis] if vis.geom_type == 'Polygon' else [q for q in getattr(vis, 'geoms', []) if q.geom_type == 'Polygon']):
                if g.area < 1e6: continue
                R.fill(list(g.exterior.coords), 'A-AREA', color='#e3ecd6' if True else '#eee', z=0, holes=[list(i.coords) for i in g.interiors])
                R.pline(list(g.exterior.coords), 'A-HIDD', lw=0.13)
                p = g.representative_point()
                cn = [nm for nm, rc in COURTS if box(*rc).intersection(g).area > 0.5 * g.area]
                if cn:
                    R.text((p.x, p.y), cn[0].replace(' (', '\n(') + '\nพื้นสวนกรวด %+.2f' % ({1: F2, 2: F3, 3: F4}[k] / 1000), 170, 'L-SITE', bold=True)
                elif g.area > 8e6:
                    R.text((p.x, p.y), 'หลังคา %+.2f' % ({1: F2, 2: F3, 3: F4}[k] / 1000), 200, 'L-SITE')
    exo_plan(R, fl)
    # ---- walls
    W, C = wall_geom(fl, M)
    G = W.difference(C) if C is not None else W
    for ring in poly_rings(G):
        pass
    gs = [G] if G.geom_type == 'Polygon' else list(G.geoms)
    for p in gs:
        R.fill(list(p.exterior.coords), 'A-WALL-POCHE', color='#3a3a3a', z=2)
        for i in p.interiors: R.fill(list(i.coords), 'A-WALL-POCHE', color='#ffffff', z=2)
        R.pline(list(p.exterior.coords), 'A-WALL')
        for i in p.interiors: R.pline(list(i.coords), 'A-WALL')
    # ---- rails
    for s in segs:
        if s.wt == 'rail':
            for v in (-25, 25):
                R.line(U(s, s.lo, v), U(s, s.hi, v), 'A-RAIL')
    # ---- columns
    for (x, y) in columns(fl):
        R.frect(x - COL / 2, y - COL / 2, x + COL / 2, y + COL / 2, 'A-WALL-POCHE', color='#111111', z=3)
        R.rect(x - COL / 2, y - COL / 2, x + COL / 2, y + COL / 2, 'A-COL')
    # ---- cylindrical core (G-Beach cylinder) + pockets
    core_draw(R, fl)
    # ---- openings
    for o in ops:
        s = o.seg; h = max(s.th, 100) / 2
        sg = into_sign(s, o.into) if o.into is not None else 1
        lo, hi = o.lo, o.hi
        if o.kind in ('door', 'lift'):
            hv = sg * h
            hinge = U(s, lo, hv); tip = U(s, lo, hv + sg * o.w); close = U(s, hi, hv)
            R.line(hinge, tip, 'A-DOOR', lw=0.35)
            # arc from tip to closed position around hinge
            if s.o == 'H':
                a0 = 90 if sg > 0 else -90
                R.pline(arcpts(hinge, o.w, a0, 0), 'A-DOOR', lw=0.13)
            else:
                a0 = 0 if sg > 0 else 180
                R.pline(arcpts(hinge, o.w, a0, 90), 'A-DOOR', lw=0.13)
            R.line(U(s, lo, -h), U(s, lo, h), 'A-DOOR'); R.line(U(s, hi, -h), U(s, hi, h), 'A-DOOR')
            if o.kind == 'lift':
                pass
        elif o.kind == 'door2':
            hv = sg * h; m = o.t; ww = o.w / 2
            for hp, a_ in ((lo, 1), (hi, -1)):
                hinge = U(s, hp, hv)
                R.line(hinge, U(s, hp, hv + sg * ww), 'A-DOOR', lw=0.35)
                if s.o == 'H':
                    R.pline(arcpts(hinge, ww, 90 if sg > 0 else -90, 0 if a_ > 0 else (180 if sg > 0 else -180)), 'A-DOOR', lw=0.13)
                else:
                    R.pline(arcpts(hinge, ww, 0 if sg > 0 else 180, 90 if a_ > 0 else -90), 'A-DOOR', lw=0.13)
            R.line(U(s, lo, -h), U(s, lo, h), 'A-DOOR'); R.line(U(s, hi, -h), U(s, hi, h), 'A-DOOR')
        elif o.kind in ('slide', 'slide1'):
            n = 2 if o.kind == 'slide' else 1
            if o.kind == 'slide':
                R.line(U(s, lo, -30), U(s, o.t + 60, -30), 'A-GLAZ', lw=0.35)
                R.line(U(s, o.t - 60, 30), U(s, hi, 30), 'A-GLAZ', lw=0.35)
            else:
                R.line(U(s, lo, -30), U(s, hi, -30), 'A-DOOR', lw=0.35)
                R.line(U(s, lo + o.w * 0.6, 60), U(s, hi + o.w * 0.4, 60), 'A-DOOR', lw=0.2, ls='--')
            R.line(U(s, lo, -h), U(s, lo, h), 'A-DOOR'); R.line(U(s, hi, -h), U(s, hi, h), 'A-DOOR')
        elif o.kind == 'open':
            R.line(U(s, lo, -h), U(s, hi, -h), 'A-HIDD', ls='--'); R.line(U(s, lo, h), U(s, hi, h), 'A-HIDD', ls='--')
        elif o.kind in ('win', 'glass'):
            R.line(U(s, lo, -h), U(s, lo, h), 'A-GLAZ'); R.line(U(s, hi, -h), U(s, hi, h), 'A-GLAZ')
            R.line(U(s, lo, -15), U(s, hi, -15), 'A-GLAZ'); R.line(U(s, lo, 15), U(s, hi, 15), 'A-GLAZ')
            if o.sill > 0:
                R.line(U(s, lo, -h), U(s, hi, -h), 'A-WALL-INT', lw=0.18); R.line(U(s, lo, h), U(s, hi, h), 'A-WALL-INT', lw=0.18)
            # mullions
            nm = max(1, int(round(o.w / 1500)))
            for i in range(1, nm):
                u = lo + o.w * i / nm
                R.line(U(s, u, -h * .6), U(s, u, h * .6), 'A-GLAZ')
        elif o.kind == 'louver':
            R.line(U(s, lo, -h), U(s, lo, h), 'A-GLAZ'); R.line(U(s, hi, -h), U(s, hi, h), 'A-GLAZ')
            u = lo + 100
            while u < hi - 50:
                R.line(U(s, u, -h * .8), U(s, u + 120, h * .8), 'A-GLAZ'); u += 150
    # ---- stair / lift / shaft
    for r in rooms:
        if r.kind in ('stair', 'fstair'):
            stair_symbol(R, r, fl)
        elif r.kind == 'lift':
            cx0, cy0, cx1, cy1 = r.x0 + 250, r.y0 + 250, r.x1 - 250, r.y1 - 300
            R.rect(cx0, cy0, cx1, cy1, 'A-EQPM'); R.line((cx0, cy0), (cx1, cy1), 'A-EQPM'); R.line((cx0, cy1), (cx1, cy0), 'A-EQPM')
        elif r.kind == 'shaft':
            R.rect(r.x0 + 150, r.y0 + 150, r.x1 - 150, r.y1 - 150, 'A-HIDD', ls='--')
            for k in range(0, 8):
                yy = r.y0 + 300 + k * (r.d - 600) / 7
                R.line((r.x0 + 200, yy), (r.x1 - 200, yy + 250), 'A-HIDD', lw=0.08)
    # ---- furniture
    if furn:
        from furn6 import furnish
        furnish(R, fl)
    # ---- labels
    if labels:
        room_labels(R, fl)
    return R

def core_draw(R, fl):
    return

def exo_plan(R, fl):
    """glulam exoskeleton: south frame posts + balcony edge beam; north posts (garage front); roof edge above"""
    for x in FRAME_X:
        R.frect(x - POST_W / 2, FRAME_S_Y - POST_D, x + POST_W / 2, FRAME_S_Y, 'A-WALL-POCHE', color='#a0703c', z=3)
        R.rect(x - POST_W / 2, FRAME_S_Y - POST_D, x + POST_W / 2, FRAME_S_Y, 'A-COL')
    for x in FRAME_N_X:
        R.frect(x - POST_W / 2, FRAME_N_Y - POST_D / 2, x + POST_W / 2, FRAME_N_Y + POST_D / 2, 'A-WALL-POCHE', color='#a0703c', z=3)
        R.rect(x - POST_W / 2, FRAME_N_Y - POST_D / 2, x + POST_W / 2, FRAME_N_Y + POST_D / 2, 'A-COL')
    if fl >= 2:
        R.line((FRAME_X[0], FRAME_S_Y - POST_D / 2), (FRAME_X[-1], FRAME_S_Y - POST_D / 2), 'A-HIDD', lw=0.13)
    if fl in (1, 4):
        ex0, ey0, ex1, ey1 = BLK[0] - OVER_EW, BLK[1] - OVER_S, BLK[2] + OVER_EW, BLK[3] + OVER_N
        R.rect(ex0, ey0, ex1, ey1, 'A-HIDD', ls='--', lw=0.13)
        R.text((ex0 + 200, ey0 + 150), 'แนวชายคาเหนือศีรษะ (ยื่น 3.00 ม. ทิศใต้)', 150, 'A-ANNO', ha='left', va='bottom')
    if fl == 4:   # Y-struts seen from below (dashed) towards the south eave
        for x in FRAME_X:
            R.line((x, FRAME_S_Y - POST_D), (x, BLK[1] - OVER_S + 150), 'A-HIDD', ls='--', lw=0.13)
    if fl == 1:
        R.text((FRAME_X[4], FRAME_S_Y - POST_D - 250), 'เสาโครงไม้ glulam 240x480 @2.875 (exoskeleton) + ค้ำรูปตัว Y', 150, 'A-ANNO', va='top')

def stair_u(R, rect, axis, floor_end, fl, top=False, fw=1000, land=1000, gap=100, label=True):
    """generic U-stair. rect=(x0,y0,x1,y1) bounding the two flights + landings. axis = direction of flights.
    floor_end = side where the floor landing is ('S','N','E','W'). Flight A (left looking from floor landing) goes up."""
    x0, y0, x1, y1 = rect
    n = 9
    if axis == 'Y':
        L = y1 - y0
        if floor_end == 'S':
            fy0, fy1 = y0, y0 + land; my0, my1 = y1 - land, y1; s0, s1 = fy1, my0
        else:
            fy0, fy1 = y1 - land, y1; my0, my1 = y0, y0 + land; s0, s1 = my1, fy0
        ax0, ax1 = x0, x0 + fw; bx0, bx1 = x1 - fw, x1
        for i in range(n + 1):
            y = s0 + (s1 - s0) * i / n
            R.line((ax0, y), (ax1, y), 'A-STAIR'); R.line((bx0, y), (bx1, y), 'A-STAIR')
        R.line((ax1, s0), (ax1, s1), 'A-STAIR'); R.line((bx0, s0), (bx1 - fw, s1), 'A-STAIR')
        R.rect(ax1 + 10, s0, bx0 - 10, s1, 'A-STAIR')
        R.rect(x0, my0, x1, my1, 'A-STAIR', lw=0.08)
        up_start = (ax0 + ax1) / 2
        if not top:
            ys = s0 if floor_end == 'S' else s1
            ye = (my0 + my1) / 2
            R.line((up_start, ys + (300 if floor_end == 'S' else -300)), (up_start, ye), 'A-ANNO', lw=0.2)
            R.line((up_start, ye), ((bx0 + bx1) / 2, ye), 'A-ANNO', lw=0.2)
            ye2 = s0 + (s1 - s0) * (0.35 if floor_end == 'S' else 0.65)
            R.line(((bx0 + bx1) / 2, ye), ((bx0 + bx1) / 2, ye2), 'A-ANNO', lw=0.2)
            sgn = -1 if floor_end == 'S' else 1
            R.pline([((bx0 + bx1) / 2 - 110, ye2 - sgn * 200), ((bx0 + bx1) / 2, ye2), ((bx0 + bx1) / 2 + 110, ye2 - sgn * 200)], 'A-ANNO', lw=0.2)
            if label: R.text((up_start, (s0 + s1) / 2), 'ขึ้น', 150, 'A-ANNO', rot=90)
            cy_ = s0 + (s1 - s0) * 0.55
            R.line((ax0, cy_), (bx1, cy_ + 400), 'A-STAIR', lw=0.35)
        if fl > 1 and label:
            R.text(((bx0 + bx1) / 2, (s0 + s1) / 2 + (600 if floor_end == 'S' else -600)), 'ลง', 150, 'A-ANNO', rot=90)
    else:
        if floor_end == 'E':
            fx0, fx1 = x1 - land, x1; mx0, mx1 = x0, x0 + land; s0, s1 = mx1, fx0
        else:
            fx0, fx1 = x0, x0 + land; mx0, mx1 = x1 - land, x1; s0, s1 = fx1, mx0
        ay0, ay1 = y1 - fw, y1; by0, by1 = y0, y0 + fw
        for i in range(n + 1):
            x = s0 + (s1 - s0) * i / n
            R.line((x, ay0), (x, ay1), 'A-STAIR'); R.line((x, by0), (x, by1), 'A-STAIR')
        R.line((s0, ay0), (s1, ay0), 'A-STAIR'); R.line((s0, by1), (s1, by1), 'A-STAIR')
        R.rect(s0, by1 + 10, s1, ay0 - 10, 'A-STAIR')
        R.rect(mx0, y0, mx1, y1, 'A-STAIR', lw=0.08)
        if not top:
            xm = (mx0 + mx1) / 2; ya = (ay0 + ay1) / 2; yb = (by0 + by1) / 2
            xs = s1 - 300 if floor_end == 'E' else s0 + 300
            R.line((xs, ya), (xm, ya), 'A-ANNO', lw=0.2); R.line((xm, ya), (xm, yb), 'A-ANNO', lw=0.2)
            xe = s0 + (s1 - s0) * (0.65 if floor_end == 'E' else 0.35)
            R.line((xm, yb), (xe, yb), 'A-ANNO', lw=0.2)
            sgn = 1 if floor_end == 'E' else -1
            R.pline([(xe - sgn * 200, yb - 110), (xe, yb), (xe - sgn * 200, yb + 110)], 'A-ANNO', lw=0.2)
            if label: R.text(((s0 + s1) / 2, ya), 'ขึ้น', 150, 'A-ANNO')
        if fl > 1 and label:
            R.text(((s0 + s1) / 2, (by0 + by1) / 2), 'ลง', 150, 'A-ANNO')

def stair_symbol(R, r, fl):
    if r.name.startswith('บันไดหลัก'):      # timber hall U-stair, flights along Y, floor landing south (towards hall / gallery)
        stair_u(R, (r.x0 + 50, r.y0 + 40, r.x0 + 50 + 2 * STAIR_W + 100, r.y0 + 40 + 9 * TREAD + 2 * STAIR_LAND), 'Y', 'S', fl, top=(fl == 4), fw=STAIR_W, land=STAIR_LAND)
    elif r.kind == 'stair':                  # private master stair F3 -> F4 (flights along Y, floor landing north)
        y1 = r.y1 - 40
        stair_u(R, (r.x0 + 50, y1 - 9 * TREAD - 2 * STAIR_LAND, r.x0 + 50 + 2 * STAIR_W + 100, y1), 'Y', 'N', fl, top=(fl == 4), fw=STAIR_W, land=STAIR_LAND)
    elif r.kind == 'fstair':                 # steel fire stair, flights along X, floor landing east
        stair_u(R, (r.x0 + 40, r.y0 + 50, r.x0 + 40 + 9 * TREAD + 2300, r.y0 + 50 + 2300), 'X', 'E', fl, top=(fl == 4), fw=1100, land=1150)
        R.text(((r.x0 + r.x1) / 2, r.y1 + 200), 'บันไดหนีไฟ (เหล็ก เปิดโล่ง)', 150, 'A-ANNO', va='bottom')

LABOFF = {
    (1, 'ครัวไทย (ครัวหนัก)'): (0, 900), (1, 'ห้องแม่บ้าน 1'): (0, 1300), (1, 'ห้องแม่บ้าน 2'): (0, 1300), (1, 'ห้องนอนแขก/ผู้สูงอายุ'): (0, -1300),
    (1, 'ลานใต้ชายคา / ศาลาริมสระ'): (0, -1800), (1, 'โรงจอดรถ 4 คัน'): (0, -2300), (1, 'โถงกลาง "Forno hall"'): (-2500, 0), (1, 'ห้องซักรีด'): (0, 1300),
    (1, 'โถงต้อนรับ (ทางเข้าทิศตะวันออก)'): (0, -800),
    (2, 'ห้องนั่งเล่น'): (1500, -1900), (2, 'ห้องรับประทานอาหาร'): (0, -2000), (2, 'ครัวโชว์ + ไอส์แลนด์'): (900, -1700),
    (4, 'ช่องโล่งโถงไม้ ชั้น 4'): (7400, 0), (4, 'สะพานไม้ ชั้น 4'): (0, -300),
    (2, 'ห้องนอน Junior Suite 2'): (0, -1500), (2, 'ห้องนอน Junior Suite 3'): (0, -1300), (2, 'ห้องทำงาน & ห้องสมุด'): (600, 1500),
    (2, 'ทางเดินแกลเลอรี ชั้น 2'): (-3500, 0), (3, 'ทางเดินแกลเลอรี ชั้น 3'): (-3500, 0), (4, 'ทางเดินแกลเลอรี ชั้น 4'): (2500, 0),
    (3, 'ห้องนอน Master Suite'): (0, -1800), (3, 'Walk-in Dressing (His & Hers)'): (0, 1300), (3, 'ห้องน้ำ Spa + Jacuzzi'): (0, 1300),
    (3, 'ลอจเจียทิศเหนือ (ระแนงไม้)'): (0, 800), (3, 'ลอจเจียตะวันออกเฉียงเหนือ'): (0, 800), (4, 'ห้องโฮมเธียเตอร์'): (0, -1300),
    (4, 'Master Walk-in Closet ชั้น 4'): (0, 1300), (4, 'ห้องนั่งเล่นครอบครัว & Upper Gallery'): (0, -1400), (4, 'ระเบียง & BBQ (ใต้ชายคา)'): (0, 1400),
    (4, 'ระเบียง Master (ใต้ชายคา)'): (0, 1400),
}
SKIPLAB = {'ลิฟต์บ้าน'}
SHORT = {'ครัวไทย (ครัวหนัก)': 'ครัวไทย\n(ครัวหนัก)', 'ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ': 'ห้อง MEP\n/ ไฟฟ้า\n/ ปั่นไฟ', 'ห้องนอนแขก/ผู้สูงอายุ': 'ห้องนอนแขก\n/ผู้สูงอายุ',
         'ตู้เสื้อผ้าห้องแขก': 'ตู้เสื้อผ้า', 'ห้องน้ำห้องแขก': 'ห้องน้ำ', 'โรงจอดรถ 4 คัน': 'โรงจอดรถ 4 คัน (EV 1 จุด)', 'ห้องน้ำแม่บ้าน': 'ห้องน้ำ\nแม่บ้าน',
         'โถงต้อนรับ (ทางเข้าทิศตะวันออก)': 'โถงต้อนรับ\n(ทางเข้าตะวันออก)', 'โถงกลาง "Forno hall"': 'โถงกลาง "Forno hall"\n(โปร่ง 4 ชั้นถึงสันหลังคา)',
         'ลานใต้ชายคา / ศาลาริมสระ': 'ลานใต้ชายคา / ศาลาริมสระ', 'บันไดหลัก (โถงไม้)': '', 'บันไดหนีไฟภายนอก': '', 'บันไดส่วนตัว Master': '',
         'โถงลิฟต์': 'โถง\nลิฟต์', 'โถงลิฟต์ ชั้น 2': 'โถง\nลิฟต์', 'โถงลิฟต์ ชั้น 3': 'โถง\nลิฟต์', 'โถงลิฟต์ ชั้น 4': 'โถง\nลิฟต์',
         'ครัวโชว์ + ไอส์แลนด์': 'ครัวโชว์\n+ ไอส์แลนด์', 'Walk-in Pantry & ห้องเย็น': 'Pantry\n& ห้องเย็น', 'ห้องน้ำแขก (Powder)': 'Powder',
         'ห้องนอน Junior Suite 2': 'ห้องนอน\nJunior Suite 2', 'ตู้เสื้อผ้า Junior Suite 2': 'ตู้เสื้อผ้า', 'ห้องน้ำ Junior Suite 2': 'ห้องน้ำ',
         'ห้องไวน์ / ซิการ์': 'ห้องไวน์\n/ ซิการ์', 'ตู้เสื้อผ้า Junior Suite 3': 'ตู้เสื้อผ้า', 'ห้องน้ำ Junior Suite 3': 'ห้องน้ำ',
         'ห้องนอน Junior Suite 3': 'ห้องนอน\nJunior Suite 3', 'ห้องทำงาน & ห้องสมุด': 'ห้องทำงาน\n& ห้องสมุด', 'Walk-in Dressing (His & Hers)': 'Walk-in Dressing\n(His & Hers)',
         'ห้องน้ำ Spa + Jacuzzi': 'ห้องน้ำ Spa\n+ Jacuzzi', 'Master Walk-in Closet ชั้น 4': 'Master Walk-in\nCloset', 'ห้องอุปกรณ์ AV / เก็บของ': 'AV / เก็บของ',
         'ห้องน้ำชั้น 4': 'ห้องน้ำ', 'ห้องนั่งเล่นครอบครัว & Upper Gallery': 'ห้องนั่งเล่นครอบครัว\n& Upper Gallery',
         'ทางเดินแกลเลอรี ชั้น 2': 'แกลเลอรี', 'ทางเดินแกลเลอรี ชั้น 3': 'แกลเลอรี', 'ทางเดินแกลเลอรี ชั้น 4': 'แกลเลอรี',
         'สะพานไม้ ชั้น 2': 'สะพาน\nไม้', 'สะพานไม้ ชั้น 3': 'สะพาน\nไม้', 'สะพานไม้ ชั้น 4': 'สะพาน\nไม้',
         'ช่องโล่งโถงไม้ ชั้น 2': 'ช่องโล่งโถงไม้ (Forno hall)', 'ช่องโล่งโถงไม้ ชั้น 3': 'ช่องโล่งโถงไม้ (Forno hall)', 'ช่องโล่งโถงไม้ ชั้น 4': 'ช่องโล่งโถงไม้ (Forno hall)',
         'ระเบียงไม้ทิศใต้ ชั้น 2': 'ระเบียงไม้ทิศใต้ (โครงไม้ภายนอก)', 'ระเบียงไม้ทิศใต้ ชั้น 3': 'ระเบียงไม้ทิศใต้ (โครงไม้ภายนอก)',
         'ระเบียง & BBQ (ใต้ชายคา)': 'ระเบียง & BBQ\n(ใต้ชายคา)', 'ระเบียง Master (ใต้ชายคา)': 'ระเบียง Master\n(ใต้ชายคา)'}

def room_labels(R, fl):
    for r in FLOORS[fl]:
        if r.name in SKIPLAB or 'ส่วนต่อเนื่อง' in r.name: continue
        dx, dy = LABOFF.get((fl, r.name), (0, 0))
        cx, cy = (r.x0 + r.x1) / 2 + dx, (r.y0 + r.y1) / 2 + dy
        nm = SHORT.get(r.name, r.name)
        if nm == '': continue
        small = r.a < 12 or r.kind in ('circ',) and r.a < 16
        h = 190 if small else 240
        R.text((cx, cy + (90 if not small else 60)), nm, h, 'A-TEXT', va='bottom', bold=not small)
        if r.kind not in ('void',):
            # area of whole room incl. continuation
            a = r.a
            for q in FLOORS[fl]:
                if q.name == r.name + ' (ส่วนต่อเนื่อง)': a += q.a
            R.text((cx, cy - 20), '%.2f ตร.ม.  %s' % (a, r.code), 150 if small else 170, 'A-ANNO', va='top')
    # courts / roofs below
    if False:
        for nm, (x0, y0, x1, y1) in COURTS:
            if 'ส่วนต่อเนื่อง' in nm: continue
            R.text(((x0 + x1) / 2, y1 - 900), nm.replace(' (', '\n('), 200, 'L-SITE', bold=True)

def grid(R, view, fl=1):
    x0, y0, x1, y1 = view
    for k, gx in GX.items():
        R.line((gx, y0 + 1300), (gx, y1 - 1300), 'A-GRID', ls=(0, (12, 4, 2, 4)), lw=0.13)
        for yy in (y0 + 800, y1 - 800):
            R.circle((gx, yy), 450, 'A-GRID'); R.text((gx, yy), k, 300, 'A-GRID')
    for k, gy in GY.items():
        R.line((x0 + 1300, gy), (x1 - 1300, gy), 'A-GRID', ls=(0, (12, 4, 2, 4)), lw=0.13)
        for xx in (x0 + 800, x1 - 800):
            R.circle((xx, gy), 450, 'A-GRID'); R.text((xx, gy), k, 300, 'A-GRID')
    # chain dims
    xs = sorted(GX.values()); ys = sorted(GY.values())
    for a, b in zip(xs, xs[1:]):
        R.dim((a, y0 + 1700), (b, y0 + 1700), 0, h=200)
    R.dim((xs[0], y0 + 2500), (xs[-1], y0 + 2500), 0, h=220)
    for a, b in zip(ys, ys[1:]):
        R.dim((x1 - 1700, a), (x1 - 1700, b), 0, h=200)
    R.dim((x1 - 2500, ys[0]), (x1 - 2500, ys[-1]), 0, h=220)

PLAN_VIEW = (-1200, -600, 31200, 30400)

def level_tag(R, p, txt, h=200):
    x, y = p
    R.pline([(x - 180, y), (x, y + 260), (x + 180, y), (x - 180, y)], 'A-ANNO')
    R.text((x + 260, y + 120), txt, h, 'A-ANNO', ha='left')

def north_arrow(R, p, r=900):
    x, y = p
    R.circle((x, y), r, 'A-ANNO')
    R.fill([(x, y + r), (x - r * .35, y - r * .6), (x, y - r * .25)], 'A-WALL-POCHE', color='#111111', z=4)
    R.pline([(x, y + r), (x + r * .35, y - r * .6), (x, y - r * .25), (x, y + r)], 'A-ANNO')
    R.text((x, y + r + 350), 'N', 380, 'A-ANNO', bold=True)

def section_marks(R):
    from proj6 import SECTIONS
    for k, sec in SECTIONS.items():
        (ax, ay), (bx, by) = sec['a'], sec['b']
        R.line((ax, ay), (bx, by), 'A-ANNO', ls=(0, (14, 4, 2, 4)), lw=0.35)
        for (px, py) in ((ax, ay), (bx, by)):
            R.circle((px, py), 500, 'A-ANNO'); R.text((px, py), k, 360, 'A-ANNO', bold=True)
            # look direction arrow
            dx, dy = sec['look']
            R.fill([(px + dx * 900, py + dy * 900), (px + dy * 350, py - dx * 350), (px - dy * 350, py + dx * 350)], 'A-WALL-POCHE', color='#b22222', z=4)
