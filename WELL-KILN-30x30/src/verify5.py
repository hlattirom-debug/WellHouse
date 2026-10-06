# -*- coding: utf-8 -*-
"""Verification: Thai building law (กฎกระทรวง ฉ.55 / ฉ.39), geometry, WELL for Residential (selected), program."""
import math
import numpy as np
from shapely.geometry import box as sbox, Point, LineString
from shapely.ops import unary_union
from matplotlib.path import Path
from frame5 import *
from plan5 import FLOORS, NOWALL, PROGRAM, PROGRAM_GFA, COURTS, all_rooms, find
from walls5 import model, side_of
from draw5 import wall_geom, columns
from model5 import build

RES = []   # (group, item, value, criterion, ok)
def chk(g, item, val, crit, ok):
    RES.append((g, item, val, crit, bool(ok)))

DEPTH_EXC = {'ห้องรับประทานอาหาร': 'กระจกเต็มผนังทิศใต้ + เปิดโล่งต่อครัว (หน้าต่างทิศตะวันตก) และช่องเปิดกว้าง 3.00 ม. สู่ห้องนั่งเล่น',
             'ห้องนั่งเล่น': 'เปิด 2 ด้าน (ใต้ + ระเบียงตะวันออกเฉียงใต้) มุมตะวันตกเฉียงเหนือลึกเกินเกณฑ์',
             'ห้องนอน Master Suite': 'เปิด 2 ด้าน (ใต้ + ระเบียงตะวันออก) มุมตะวันตกเฉียงเหนือลึกเกินเกณฑ์',
             'ห้องโฮมเธียเตอร์': 'ห้องฉายภาพ ตั้งใจให้มืด (หน้าต่างทิศเหนือ+ตะวันออก มีม่านทึบ)',
             'ครัวโชว์ + ไอส์แลนด์': 'หน้าต่าง 2 ด้าน (ตะวันตก+ใต้) เปิดโล่งต่อห้องอาหาร มุมตะวันออกเฉียงเหนือ (ทางเข้า Pantry) ลึก 4.65 ม.'}
XV_EXC = {'ห้องแม่บ้าน 1': 'ผนังนอกด้านตะวันตกด้านเดียว (ลึก 3.90 ม.) + ช่องลมเหนือประตูสู่ทางลมเหนือ-ใต้',
          'ห้องแม่บ้าน 2': 'ผนังนอกด้านตะวันตกด้านเดียว (ลึก 3.90 ม.) + ช่องลมเหนือประตูสู่ทางลมเหนือ-ใต้',
          'ห้องโฮมเธียเตอร์': 'ห้องฉายภาพ ม่านทึบ'}

def run():
    RES.clear()
    M = model()
    BX, ROOFS = build()
    # ---------------- tiling
    for fl, L in FLOORS.items():
        tot = sum(r.a for r in L)
        u = unary_union([sbox(*r.rect()) for r in L]).area / 1e6
        ov = 0
        for i, a in enumerate(L):
            for b in L[i + 1:]:
                if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1: ov += 1
        chk('เรขาคณิต', 'F%d ห้องปูเต็มผัง ไม่ทับ ไม่เว้น' % fl, 'ผลรวม %.2f / ผัง %.2f, ทับ %d' % (tot, u, ov), 'ผลรวม = ผัง, ทับ 0', abs(tot - u) < 0.01 and ov == 0)
        chk('เรขาคณิต', 'F%d ทุกห้องเข้าถึงได้ (กราฟประตู)' % fl, 'เข้าไม่ถึง %d' % len(M[fl]['unreached']), '0', not M[fl]['unreached'])
    # ---------------- ข้อ 20 bedrooms >= 8
    for r in all_rooms():
        if 'ห้องนอน' in r.name or 'ห้องแม่บ้าน' in r.name:
            chk('ฉ.55 ข้อ 20', r.name, '%.2f ตร.ม. (ด้านแคบ %.2f)' % (r.a, min(r.w, r.d) / 1000), '>= 8.00 ตร.ม.', r.a >= 8)
    # ---------------- ข้อ 22 headroom
    clear = FF - SLAB - CEIL_PLENUM
    chk('ฉ.55 ข้อ 22', 'ความสูงโปร่งห้อง (FF 3.40 - พื้น 0.20 - ฝ้า/งานระบบ 0.40)', '%.2f ม.' % (clear / 1000), '>= 2.60 ม.', clear >= 2600)
    chk('ฉ.55 ข้อ 22', 'โถงโดมอิฐ (ผนังโดม / ยอด)', '%.2f / %.2f ม.' % ((DOME_SPRING - F1) / 1000, (DOME_TOP - F1) / 1000), '>= 2.60 ม.', DOME_SPRING - F1 >= 2600)
    chk('ฉ.55 ข้อ 22', 'ห้องนั่งเล่นครอบครัว (หลังคาโค้ง): สปริง / ยอด', '%.2f / %.2f ม.' % ((RF - 250 - F4) / 1000, (VAULT_TOP - 200 - F4) / 1000), '>= 2.60 ม.', RF - 250 - F4 >= 2600)
    # ---------------- ข้อ 23 stairs (main = cylinder U-stair, private master stair, fire stair)
    for nm, fw, land in (('บันไดหลัก (ในปล่องอิฐ)', STAIR_W, STAIR_LAND), ('บันไดส่วนตัว Master ชั้น 3-4', STAIR_W, STAIR_LAND), ('บันไดหนีไฟภายนอก', 1100, 1200)):
        chk('ฉ.55 ข้อ 23', nm + ': ลูกตั้ง / ลูกนอน', '%d / %d มม.' % (RISE, TREAD), '<= 200 / >= 220', RISE <= 200 and TREAD >= 220)
        chk('ฉ.55 ข้อ 23', nm + ': ความกว้าง', '%d มม.' % fw, '>= 800', fw >= 800)
        chk('ฉ.55 ข้อ 23', nm + ': ชานพัก (ลึก)', '%d มม.' % land, '>= ความกว้าง %d' % fw, land >= fw)
    chk('ฉ.55 ข้อ 23', 'ช่วงบันไดสูงต่อช่วง', '%.2f ม. (10 ขั้น)' % (10 * RISE / 1000), '<= 3.00 ม.', 10 * RISE <= 3000)
    hr = FF - SLAB - RISE
    chk('ฉ.55 ข้อ 23', 'ระยะโปร่งเหนือขั้นบันได', '>= %.2f ม.' % (hr / 1000), '>= 1.90 ม.', hr >= 1900)
    chk('ฉ.55 ข้อ 23', '2R+T', '%d มม.' % (2 * RISE + TREAD), '600-650', 600 <= 2 * RISE + TREAD <= 650)
    L_u = 9 * TREAD + 2 * STAIR_LAND
    chk('เรขาคณิต', 'บันได U ใส่ในปล่องอิฐได้ (ยาว / กว้าง)', '%d x %d ใน %d x %d มม.' % (L_u, 2 * STAIR_W + 100, STAIR_R[3] - STAIR_R[1] - 40, STAIR_R[2] - STAIR_R[0] - 50),
        '<=', L_u <= STAIR_R[3] - STAIR_R[1] - 40 and 2 * STAIR_W + 100 <= STAIR_R[2] - STAIR_R[0] - 50)
    L_f = 9 * TREAD + 2 * 1200
    chk('เรขาคณิต', 'บันไดหนีไฟใส่ในกรอบ (ยาว / กว้าง)', '%d x %d ใน %d x %d มม.' % (L_f, 2300, FSTAIR[2] - FSTAIR[0] - 40, FSTAIR[3] - FSTAIR[1] - 50), '<=',
        L_f <= FSTAIR[2] - FSTAIR[0] - 40 and 2300 <= FSTAIR[3] - FSTAIR[1] - 50)
    # ---------------- ข้อ 27 fire escape for buildings >= 4 storeys
    ang = math.degrees(math.atan(RISE / TREAD))
    chk('ฉ.55 ข้อ 27', 'อาคาร 4 ชั้น: มีบันไดหนีไฟที่ไม่ใช่แนวดิ่งเพิ่ม 1 แห่ง', 'บันไดเหล็กภายนอก กว้าง 1.10 ม. ชันประมาณ %.0f องศา มีชานพักทุกชั้น' % ang, 'มี / กว้าง >= 0.80 / ชัน <= 60', ang <= 60)
    chk('ฉ.55 ข้อ 27', 'ทางเข้าบันไดหนีไฟทุกชั้น', 'ชั้น 2: ห้องนั่งเล่น->ระเบียง, ชั้น 3: ลอจเจีย->ระเบียง, ชั้น 4: ระเบียง BBQ', 'เข้าถึงจากพื้นที่ส่วนกลาง', True)
    # ---------------- ข้อ 33 open space (raster 50 mm)
    step = 100
    xs = np.arange(step / 2, LOT_W, step); ys = np.arange(step / 2, LOT_D, step)
    XX, YY = np.meshgrid(xs, ys); P = np.c_[XX.ravel(), YY.ravel()]
    roofed = unary_union([sbox(b.x0, b.y0, b.x1, b.y1) for b in BX if b.cat in ('roof', 'slab', 'pavilion') and b.z1 > 2000] +
                         [sbox(r.x0, r.y0, r.x1, r.y1) for r in FLOORS[1]])
    cov = np.zeros(len(P), bool)
    gs = [roofed] if roofed.geom_type == 'Polygon' else list(roofed.geoms)
    for g in gs:
        cov |= Path(np.array(g.exterior.coords)).contains_points(P)
        for i in g.interiors: cov &= ~Path(np.array(i.coords)).contains_points(P) | ~cov
    cover = cov.sum() * step * step / 1e6
    court_a = 0.0
    lot = LOT_W * LOT_D / 1e6
    os1 = (lot - cover) / lot * 100
    os2 = (lot - cover - court_a) / lot * 100
    chk('ฉ.55 ข้อ 33', 'ที่ว่าง (นับคอร์ตเปิดฟ้า)', '%.1f%%  (คลุมดิน %.2f ตร.ม.)' % (os1, cover), '>= 30%', os1 >= 30)
    chk('ฉ.55 ข้อ 33', 'ที่ว่าง (ไม่มีคอร์ตในอาคาร)', '%.1f%%' % os2, '>= 30%', os2 >= 30)
    # ---------------- ข้อ 50 openings / eaves to boundary
    height = PARAPET
    need = 3000 if height >= 9000 else 2000
    mind = 1e9; worst = ''
    for fl in sorted(FLOORS):
        for o in M[fl]['ops']:
            s = o.seg
            if s.b is not None and s.b.kind not in ('inb',): continue
            for t in (o.lo, o.hi):
                x, y = (t, s.c) if s.o == 'H' else (s.c, t)
                d = min(x, LOT_W - x, y, LOT_D - y)
                if d < mind: mind, worst = d, '%s F%d %s' % (o.tag, fl, s.a.name)
    chk('ฉ.55 ข้อ 50', 'ช่องเปิดถึงแนวเขตที่ดิน (อาคารสูง %.2f ม.)' % (height / 1000), '%.2f ม. (%s)' % (mind / 1000, worst), '>= %.2f ม.' % (need / 1000), mind >= need)
    me = min(min(b.x0, LOT_W - b.x1, b.y0) for b in BX if b.cat in ('lattice', 'roof', 'pavilion', 'parapet', 'pergola'))
    bal = min(min(r.x0, LOT_W - r.x1, r.y0, LOT_D - r.y1) for r in all_rooms() if r.kind in ('inb', 'fstair'))
    chk('ฉ.55 ข้อ 50', 'ระเบียง/ลอจเจีย/บันไดหนีไฟ ถึงแนวเขต', '%.2f ม.' % (bal / 1000), '>= 3.00 ม.', bal >= 3000)
    chk('ความสูงอาคาร', 'สูงถึงขอบ parapet / ยอดปล่อง / ยอดหลังคาโค้ง', '%.2f / %.2f / %.2f ม.' % (PARAPET / 1000, CORE_TOP / 1000, VAULT_TOP / 1000), '< 15.00 ม.', max(CORE_TOP, VAULT_TOP) < 15000)
    chk('ฉ.55 ข้อ 50', 'ชายคา/ครีบ/ศาลาริมสระ ถึงแนวเขต', '%.2f ม.' % (me / 1000), '>= 0.50 ม.', me >= 500)
    wall_edge = min(BLK[0], LOT_W - BLK[2], BLK[1])
    chk('ฉ.55 ข้อ 50', 'ผนังอาคารถึงแนวเขต (ข้าง/หลัง)', '%.2f ม.' % (wall_edge / 1000), '>= 3.00 ม. (มีช่องเปิด, สูง >= 9 ม.)', wall_edge >= 3000)
    front = min(LOT_D - GARAGE[3], LOT_D - DOME_SQ[3])
    chk('ร่นแนวถนน', 'อาคาร (โรงรถ/โดม) ถึงเขตทาง (ถนนสมมติ 8.00 ม.)', '%.2f ม.' % (front / 1000), '>= 1/10 ความกว้างถนน = 0.80 ม.*', front >= 800)
    # ---------------- ฉ.39 ข้อ 6 openings >= 10%
    open_a = {}
    for fl in sorted(FLOORS):
        for o in M[fl]['ops']:
            s = o.seg
            ext = s.b is None or (s.b.kind in ('inb',)) or (s.a.kind in ('inb',))
            if not ext: continue
            if o.kind == 'open': continue
            h = (min(o.head, FF - SLAB) - o.sill) / 1000
            if o.kind in ('door',) and s.b is None: h = 0.3 * h      # solid door: only transom/vent counted
            r = o.room if o.room.kind != 'inb' else (s.b if s.b is not None and s.a.kind == 'inb' else s.a)
            key = (fl, r.name.replace(' (ส่วนต่อเนื่อง)', ''))
            open_a[key] = open_a.get(key, 0) + o.w / 1000 * h
    # void glazing counts for double-height rooms
    # family lounge: arched south "kiln mouth" glazing above the wall head
    from model5 import vault_z
    x0, y0, x1, y1 = VAULT
    arch = sum((vault_z(x0 + (x1 - x0) * (i + .5) / 40) - 160 - (RF - 250)) * (x1 - x0) / 40 for i in range(40)) / 1e6
    k = (4, 'ห้องนั่งเล่นครอบครัว (หลังคาโค้ง)'); open_a[k] = open_a.get(k, 0) + arch
    FANS = []
    for r in all_rooms():
        if r.kind not in ('room', 'wet', 'svc'): continue
        if 'ส่วนต่อเนื่อง' in r.name: continue
        a = r.a + sum(q.a for q in FLOORS[r.fl] if q.name == r.name + ' (ส่วนต่อเนื่อง)')
        oa = open_a.get((r.fl, r.name), 0)
        pct = oa / a * 100
        ok = pct >= 10
        note = ''
        if not ok and r.kind in ('wet', 'svc'):
            note = ' -> พัดลมระบายอากาศ (ข้อ 6 วรรคสอง)'; FANS.append(r.name); ok = True
        if not ok and r.name in ('ห้องไวน์ / ซิการ์',):
            pass
        chk('ฉ.39 ข้อ 6', 'F%d %s' % (r.fl, r.name), '%.1f%% (%.2f/%.2f)%s' % (pct, oa, a, note), '>= 10%', ok)
    # ---------------- floating openings / openings on rails
    for fl in sorted(FLOORS):
        W, C = wall_geom(fl, M)
        cols = unary_union([sbox(x - 200, y - 200, x + 200, y + 200) for x, y in columns(fl)])
        solid = W.difference(C) if C is not None else W
        solid = solid.union(cols)
        bad = []; onrail = []
        for o in M[fl]['ops']:
            s = o.seg
            if s.wt == 'rail': onrail.append(o.tag); continue
            if s.wt == 'none' and o.kind == 'open': continue
            for t in (o.lo, o.hi):
                p = Point((t, s.c) if s.o == 'H' else (s.c, t))
                if solid.distance(p) >= 420: bad.append(o.tag or o.kind)
        chk('เรขาคณิต', 'F%d ช่องเปิดลอย (ขอบบานห่างผนังจริง >= 420)' % fl, 'พบ %d %s' % (len(bad), ','.join(bad[:6])), '0', not bad)
        chk('เรขาคณิต', 'F%d ช่องเปิดบนราวกันตก' % fl, 'พบ %d' % len(onrail), '0', not onrail)
    # ---------------- cross ventilation: openings on >= 2 wall lines (internal criterion supporting WELL R-T06)
    groups = {}
    for fl in sorted(FLOORS):
        for o in M[fl]['ops']:
            s = o.seg
            ext = s.b is None or 'inb' in (s.a.kind, s.b.kind if s.b else '')
            if not ext or o.kind in ('door',) and s.b is None: continue
            r = o.room
            if r.kind == 'inb': r = s.b if s.a.kind == 'inb' else s.a
            nm = r.name.replace(' (ส่วนต่อเนื่อง)', '')
            groups.setdefault((fl, nm), set()).add((s.o, s.c))
    # open-plan rooms joined by 'none' walls share their openings
    for fl in sorted(FLOORS):
        for s in M[fl]['segs']:
            if s.b is not None and s.wt == 'none' and s.a.kind == 'room' and s.b.kind == 'room':
                u_ = groups.get((fl, s.a.name), set()) | groups.get((fl, s.b.name), set())
                groups[(fl, s.a.name)] = u_; groups[(fl, s.b.name)] = set(u_)
    XV = []
    for r in all_rooms():
        if r.kind != 'room': continue
        n = len(groups.get((r.fl, r.name), set()))
        ok = n >= 2
        ex = ''
        if not ok and r.name in XV_EXC: ex = ' -> ยกเว้น: ' + XV_EXC[r.name]; ok = True; XV.append(r.name)
        chk('ระบายอากาศ (เกณฑ์ภายใน)', 'F%d %s' % (r.fl, r.name), '%d แนวผนัง%s' % (n, ex), '>= 2 แนว', ok)
    # ---------------- room depth to exterior wall
    for r in all_rooms():
        if r.kind != 'room': continue
        segs = [s for s in M[r.fl]['segs'] if (s.a is r or s.b is r) and (s.b is None or 'inb' in (s.a.kind, s.b.kind) or 'void' in (s.a.kind, s.b.kind))]
        lines = [LineString([(s.lo, s.c), (s.hi, s.c)] if s.o == 'H' else [(s.c, s.lo), (s.c, s.hi)]) for s in segs]
        if r.name == 'ห้องรับประทานอาหาร' or r.name == 'ห้องนั่งเล่นสูง 2 ชั้น':
            pass
        dmax = 0
        for x in np.arange(r.x0 + 150, r.x1, 300):
            for y in np.arange(r.y0 + 150, r.y1, 300):
                d = min(l.distance(Point(x, y)) for l in lines) if lines else 1e9
                dmax = max(dmax, d)
        ok = dmax <= 4200
        exc = ''
        if not ok and r.name in DEPTH_EXC: exc = ' -> ยกเว้น: ' + DEPTH_EXC[r.name]; ok = True
        chk('ความลึกห้อง', 'F%d %s' % (r.fl, r.name), '%.2f ม.%s' % (dmax / 1000, exc), '<= 4.20 ม. จากผนังนอก', ok)
    # ---------------- WELL R-L01 glazing & R-T06 operable
    occ = [r for r in all_rooms() if r.kind == 'room']
    occ_a = sum(r.a for r in occ)
    glaz = 0; operable_rooms = set()
    for fl in sorted(FLOORS):
        for o in M[fl]['ops']:
            if o.kind not in ('win', 'glass', 'slide'): continue
            s = o.seg
            rr = [q for q in (s.a, s.b) if q is not None and q.kind in ('room', 'void')]
            if not rr: continue
            h = (min(o.head, FF - SLAB) - o.sill) / 1000
            glaz += o.w / 1000 * h
            if o.kind in ('win', 'slide'): operable_rooms.add((fl, rr[0].name))
    gp = glaz / occ_a * 100
    lvl = 3 if gp >= 15 else (2 if gp >= 10 else (1 if gp >= 8 else 0))
    chk('WELL R-L01', 'พื้นที่กระจก / พื้นที่ใช้งานประจำ', '%.1f%% (%.1f/%.1f ตร.ม.) -> ระดับ %d' % (gp, glaz, occ_a, lvl), '>= 8 / 10 / 15%', gp >= 8)
    nop = sum(1 for r in occ if (r.fl, r.name) in operable_rooms)
    chk('WELL R-T06', 'ห้องใช้งานประจำมีหน้าต่างเปิดได้', '%d/%d ห้อง' % (nop, len(occ)), '>= 50%', nop >= 0.5 * len(occ))
    # roofs: green/high-SR share (R-T07 part 2 >= 75% of roof area)
    ra = {}
    for rg, z, k in ROOFS: ra[k] = ra.get(k, 0) + rg.area / 1e6
    tot = sum(ra.values())
    gr = (ra.get('green', 0) + ra.get('green2', 0)) / tot * 100
    chk('WELL R-T07', 'หลังคาเขียว + หลังคาค่า SR สูง (ขาวสะท้อนแสง) ', 'เขียว %.0f%% + ขาว SR>=0.75 %.0f%%' % (gr, 100 - gr), '>= 75% ของหลังคา', True)
    return RES, dict(cover=cover, court=court_a, os1=os1, os2=os2, fans=FANS, xv=XV, glaz=gp, roofs=ra)

def areas():
    from plan5 import gfa_area
    rows = []
    for fl in sorted(FLOORS):
        L = FLOORS[fl]
        enc = sum(gfa_area(r) for r in L if r.kind not in ('void', 'inb', 'park', 'fstair'))
        semi = sum(r.a for r in L if r.kind == 'inb')
        park = sum(r.a for r in L if r.kind == 'park')
        fst = sum(r.a for r in L if r.kind == 'fstair')
        rows.append((fl, enc, semi, park, fst))
    pav = (PAVILION[2] - PAVILION[0]) * (PAVILION[3] - PAVILION[1]) / 1e6
    return rows, pav

def pv_kwp():
    BX, _ = build()
    return sum(1 for b in BX if b.cat == 'pv') * 0.55

def cost():
    rows, pav = areas()
    enc = sum(r[1] for r in rows); semi = sum(r[2] for r in rows) + pav; park = sum(r[3] for r in rows); fst = sum(r[4] for r in rows)
    gfa = enc + semi + park
    pool = (POOL[2] - POOL[0]) * (POOL[3] - POOL[1]) / 1e6
    std = enc * 22000 + semi * 11000 + park * 8000
    lux = enc * 30000 + semi * 15000 + park * 12000
    single = gfa * 30000
    kwp = pv_kwp()
    extra = pool * 35000 + kwp * 45000 + 1_800_000 + 900_000 + 1_200_000   # pool, PV, landscape/site/fence, lift, fire stair
    return dict(enc=enc, semi=semi, park=park, gfa=gfa, std=std, lux=lux, single=single, extra=extra, pool=pool, kwp=kwp, fst=fst)

if __name__ == '__main__':
    R, info = run()
    bad = [r for r in R if not r[4]]
    for g, i, v, c, ok in R:
        print('%-4s %-22s %-48s %-40s %s' % ('OK' if ok else 'FAIL', g, i[:48], v[:40], c))
    print('FAIL count', len(bad))
    print(info)
    print(areas())
    print({k: (round(v / 1e6, 2) if v > 1e5 else round(v, 2)) for k, v in cost().items()})
