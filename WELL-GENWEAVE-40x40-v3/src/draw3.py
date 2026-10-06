# -*- coding: utf-8 -*-
"""Plan drawings for F1-F3 (Rec), shared helpers."""
import math
from shapely.geometry import box, Polygon as SP, MultiPolygon
from shapely.ops import unary_union
from cad3 import Rec
from plan3 import FLOORS, COURTS, find
from frame3 import *
from walls3 import model, side_of, T_EXT

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
    """grid intersections inside/on floor footprint (F1 footprint for all floors where slab exists)"""
    L = [r for r in FLOORS[fl] if r.kind != 'void' or fl > 1]
    fp = unary_union([box(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[1]])
    here = unary_union([box(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1) for r in FLOORS[fl]])
    pts = []
    skip = {(9400, GY['E']), (13000, GY['E'])}           # garage front: 11.40 m transfer beam, no posts
    for gx in GX.values():
        for gy in GY.values():
            if (gx, gy) in skip: continue
            from shapely.geometry import Point
            p = Point(gx, gy)
            if fp.buffer(1).contains(p) and here.contains(p):
                pts.append((gx, gy))
    # crown bar posts beyond F1 slab (none) ; spine/foyer extras
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
            below = unary_union([box(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[k]])
            higher = unary_union([box(r.x0, r.y0, r.x1, r.y1) for kk in range(k + 1, fl + 1) for r in FLOORS[kk]])
            vis = below.difference(higher)
            for g in ([vis] if vis.geom_type == 'Polygon' else [q for q in getattr(vis, 'geoms', []) if q.geom_type == 'Polygon']):
                if g.area < 1e6: continue
                R.fill(list(g.exterior.coords), 'A-AREA', color='#e3ecd6' if True else '#eee', z=0, holes=[list(i.coords) for i in g.interiors])
                R.pline(list(g.exterior.coords), 'A-HIDD', lw=0.13)
                p = g.representative_point()
                if g.area > 8e6:
                    R.text((p.x, p.y), 'หลังคาสวน %s' % ('+4.20' if k == 1 else '+7.80'), 200, 'L-SITE')
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
        if r.kind == 'stair':
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
        from furn3 import furnish
        furnish(R, fl)
    # ---- labels
    if labels:
        room_labels(R, fl)
    return R

def stair_symbol(R, r, fl):
    """U-stair: two flights N-S, floor landing north, mid landing south"""
    xw0, xw1 = r.x0 + 100, r.x0 + 100 + STAIR_W        # west flight
    xe0, xe1 = r.x1 - 100 - STAIR_W, r.x1 - 100        # east flight
    yN = r.y1 - 1580; yS = yN - 9 * TREAD               # flight extents
    for i in range(10):
        y = yN - i * TREAD
        R.line((xw0, y), (xw1, y), 'A-STAIR'); R.line((xe0, y), (xe1, y), 'A-STAIR')
    R.line((xw1, yS), (xw1, yN), 'A-STAIR'); R.line((xe0, yS), (xe0, yN), 'A-STAIR')
    R.rect(xw1 + 20, yS, xe0 - 20, yN, 'A-STAIR')
    # up arrow on west flight (from this floor) ; F3 = top: both flights shown down
    if fl < 3:
        R.line(((xw0 + xw1) / 2, yN), ((xw0 + xw1) / 2, yS - 600), 'A-ANNO', lw=0.2)
        R.line(((xw0 + xw1) / 2, yS - 600), ((xe0 + xe1) / 2, yS - 600), 'A-ANNO', lw=0.2)
        R.line(((xe0 + xe1) / 2, yS - 600), ((xe0 + xe1) / 2, yN - 1200), 'A-ANNO', lw=0.2)
        ax_, ay_ = (xe0 + xe1) / 2, yN - 1200
        R.pline([(ax_ - 120, ay_ - 220), (ax_, ay_), (ax_ + 120, ay_ - 220)], 'A-ANNO', lw=0.2)
        R.text(((xw0 + xw1) / 2, yN - 700), 'ขึ้น', 170, 'A-ANNO')
        # cut line
        R.line((xw0, yS + 1200), (xe1, yS + 1700), 'A-STAIR', lw=0.35)
    if fl > 1:
        R.text(((xe0 + xe1) / 2, yS + 900), 'ลง', 170, 'A-ANNO')
    R.text(((xw1 + xe0) / 2 + 1, (yS + yN) / 2), '20R x %d\nT %d' % (RISE, TREAD), 120, 'A-ANNO', rot=90)

LABOFF = {  # (fl, name): (dx, dy) label offset from centre
    (1, 'ห้องนั่งเล่นสูง 2 ชั้น'): (0, -1500),
    (1, 'ห้องรับประทานอาหาร'): (0, -2400),
    (1, 'ครัวโชว์ + ไอส์แลนด์'): (0, 2100),
    (1, 'โรงจอดรถ 4 คัน'): (0, -2600),
    (1, 'ห้องโฮมเธียเตอร์'): (0, 1900),
    (1, 'ห้องนอนแขก/ผู้สูงอายุ'): (-1200, -1100),
    (2, 'ห้องนอน Junior Suite 2'): (-1300, -1200),
    (2, 'ห้องนอน Junior Suite 3'): (-1200, -1200),
    (3, 'ห้องนอน Master Suite'): (0, -2600),
    (1, 'ระเบียงบาร์บีคิว'): (0, 600),
    (2, 'ห้องนั่งเล่นครอบครัว'): (0, 1900),
    (3, 'ห้องทำงาน & ห้องสมุด'): (600, 300),
    (3, 'Walk-in Dressing (His & Hers)'): (0, 1300),
    (3, 'ห้องน้ำ Spa + Jacuzzi'): (0, -1800),
    (1, 'ครัวไทย (ครัวหนัก)'): (0, -2200),
    (1, 'บันไดหลัก'): (0, 0),
    (1, 'ห้องแม่บ้าน 1'): (-800, -300), (1, 'ห้องแม่บ้าน 2'): (-800, -300),
    (1, 'ห้องนอนแขก/ผู้สูงอายุ'): (-1000, -1300), (1, 'ทางเดินห้องแขก'): (0, -1800), (1, 'โถงเหนือ (เข้าลิฟต์-บันได)'): (0, 500),
    (1, 'ห้องซักรีด'): (900, 300),
}
SKIPLAB = {'ระเบียงบาร์บีคิว (ส่วนต่อเนื่อง)', 'ห้อง MEP / ไฟฟ้า (ส่วนต่อเนื่อง)', 'บันไดหลัก', 'ลิฟต์บ้าน', 'ปล่องลม Termite'}
SHORT = {'ทางเดินลำต้น (Trunk)': 'ทางเดิน\nลำต้น', 'ชานบริการ/ตากผ้า': 'ชานบริการ', 'ทางเดินห้องแขก': 'ทางเดิน', 'ทางเดิน Junior Suite 2': 'ทางเดิน',
         'ทางเดิน Junior Suite 3': 'ทางเดิน', 'ห้องอาบน้ำริมสระ': 'ห้องอาบน้ำ\nริมสระ', 'Walk-in Pantry/ห้องเย็น': 'Pantry\nห้องเย็น',
         'ห้องเก็บจักรยาน/อุปกรณ์สวน': 'เก็บจักรยาน\n/อุปกรณ์สวน', 'ห้องน้ำแขก (Powder)': 'ห้องน้ำแขก\n(Powder)', 'ห้องน้ำแม่บ้าน': 'ห้องน้ำ\nแม่บ้าน',
         'ห้อง MEP / ไฟฟ้า': 'ห้อง MEP\n/ไฟฟ้า', 'ตู้เสื้อผ้าห้องแขก': 'ตู้\nเสื้อผ้า', 'ตู้เสื้อผ้า Junior Suite 2': 'ตู้เสื้อผ้า', 'ตู้เสื้อผ้า Junior Suite 3': 'ตู้\nเสื้อผ้า',
         'ห้องน้ำห้องแขก': 'ห้องน้ำ', 'ห้องน้ำ Junior Suite 2': 'ห้องน้ำ', 'ห้องน้ำ Junior Suite 3': 'ห้องน้ำ', 'ครัวไทย (ครัวหนัก)': 'ครัวไทย\n(ครัวหนัก)',
         'ห้องไวน์ / ซิการ์': 'ห้องไวน์\n/ซิการ์', 'ห้องนอนแขก/ผู้สูงอายุ': 'ห้องนอนแขก\n/ผู้สูงอายุ', 'มุขรถเทียบ (Porte-cochère)': 'มุขรถเทียบ',
         'โถงเหนือ (เข้าลิฟต์-บันได)': 'โถง', 'Upper Gallery (โถงชั้น 2)': 'Upper\nGallery', 'โถงบันไดชั้น 3': 'โถง', 'โถงใต้': 'โถง',
         'สะพานกิ่งตะวันตก': 'สะพานกิ่ง (W)', 'สะพานกิ่งตะวันออก': 'สะพานกิ่ง (E)', 'ห้องนอน Junior Suite 2': 'ห้องนอน\nJunior Suite 2',
         'ห้องนอน Junior Suite 3': 'ห้องนอน\nJunior Suite 3', 'Walk-in Dressing (His & Hers)': 'Walk-in Dressing\n(His & Hers)',
         'ห้องน้ำ Spa + Jacuzzi': 'ห้องน้ำ Spa\n+ Jacuzzi', 'ระเบียง Master (หลังคาคลุม)': 'ระเบียง\nMaster', 'ห้องทำงาน & ห้องสมุด': 'ห้องทำงาน\n& ห้องสมุด',
         'ช่องโล่งห้องอาหาร': 'ช่องโล่ง\nห้องอาหาร', 'ช่องโล่งห้องนั่งเล่น': 'ช่องโล่ง ห้องนั่งเล่น', 'ช่องโล่งโถงต้อนรับ': 'ช่องโล่งโถงต้อนรับ',
         'ห้องซักรีด': 'ห้องซักรีด', 'ทางเดินปีกเหนือ': 'ทางเดิน', 'ห้องนั่งเล่นสูง 2 ชั้น': 'ห้องนั่งเล่น (สูง 2 ชั้น)', 'โถงต้อนรับสูง 2 ชั้น': 'โถงต้อนรับ\n(สูง 2 ชั้น)'}

def room_labels(R, fl):
    lvl = {1: F1, 2: F2, 3: F3}[fl]
    for r in FLOORS[fl]:
        if r.name in SKIPLAB: continue
        dx, dy = LABOFF.get((fl, r.name), (0, 0))
        cx, cy = (r.x0 + r.x1) / 2 + dx, (r.y0 + r.y1) / 2 + dy
        nm = SHORT.get(r.name, r.name)
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
    if fl == 1:
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

PLAN_VIEW = (1800, Y(6000) - 4200, 38200, Y(31400) + 3000)

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
    from proj3 import SECTIONS
    for k, sec in SECTIONS.items():
        (ax, ay), (bx, by) = sec['a'], sec['b']
        R.line((ax, ay), (bx, by), 'A-ANNO', ls=(0, (14, 4, 2, 4)), lw=0.35)
        for (px, py) in ((ax, ay), (bx, by)):
            R.circle((px, py), 500, 'A-ANNO'); R.text((px, py), k, 360, 'A-ANNO', bold=True)
            # look direction arrow
            dx, dy = sec['look']
            R.fill([(px + dx * 900, py + dy * 900), (px + dy * 350, py - dx * 350), (px - dy * 350, py + dx * 350)], 'A-WALL-POCHE', color='#b22222', z=4)
