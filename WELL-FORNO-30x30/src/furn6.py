# -*- coding: utf-8 -*-
"""Furniture & fittings: LOD400 blocks (NACK HOUSE library) + simple parametric items."""
import math
from plan6 import find

OFF = 80   # gap from wall line (half int wall + finish)
ROT = {'S': 0, 'N': 180, 'W': -90, 'E': 90}

def wallpt(r, wall, along, off=OFF):
    if wall == 'S': return (along, r.y0 + off)
    if wall == 'N': return (along, r.y1 - off)
    if wall == 'W': return (r.x0 + off, along)
    if wall == 'E': return (r.x1 - off, along)

def blk(R, name, r, wall, along, off=OFF):
    R.block(name, wallpt(r, wall, along, off), ROT[wall])

def box(R, x0, y0, x1, y1, ly='A-FURN', **k):
    R.rect(x0, y0, x1, y1, ly, **k)

def counter(R, x0, y0, x1, y1, sink=None, hob=None):
    box(R, x0, y0, x1, y1, 'A-EQPM')
    if sink:
        sx, sy = sink; R.rect(sx - 400, sy - 220, sx + 400, sy + 220, 'A-EQPM'); R.circle((sx, sy), 40, 'A-EQPM')
    if hob:
        hx, hy = hob
        R.rect(hx - 400, hy - 260, hx + 400, hy + 260, 'A-EQPM')
        for dx in (-200, 200):
            for dy in (-120, 120): R.circle((hx + dx, hy + dy), 90, 'A-EQPM')

def chair(R, cx, cy, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    pts = [(-230, -230), (230, -230), (230, 230), (-230, 230)]
    R.pline([(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts], 'A-FURN', closed=True)
    R.line((cx + (-230) * c - 230 * s, cy + (-230) * s + 230 * c), (cx + 230 * c - 230 * s, cy + 230 * s + 230 * c), 'A-FURN', lw=0.3)

def table(R, cx, cy, w, d, n_long, ends=True, round_=False):
    """w along x, d along y"""
    if round_:
        R.circle((cx, cy), w / 2, 'A-FURN')
        for i in range(n_long):
            a = 360 * i / n_long
            chair(R, cx + (w / 2 + 320) * math.cos(math.radians(a)), cy + (w / 2 + 320) * math.sin(math.radians(a)), a + 90)
        return
    box(R, cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2)
    if w >= d:
        for i in range(n_long):
            x = cx - w / 2 + w * (i + .5) / n_long
            chair(R, x, cy + d / 2 + 260, 0); chair(R, x, cy - d / 2 - 260, 180)
        if ends:
            chair(R, cx - w / 2 - 260, cy, 90); chair(R, cx + w / 2 + 260, cy, -90)
    else:
        for i in range(n_long):
            y = cy - d / 2 + d * (i + .5) / n_long
            chair(R, cx + w / 2 + 260, y, -90); chair(R, cx - w / 2 - 260, y, 90)
        if ends:
            chair(R, cx, cy + d / 2 + 260, 0); chair(R, cx, cy - d / 2 - 260, 180)

def car(R, cx, cy, ang=0, L=4900, W=1900, dashed=False):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    T = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    ls = '--' if dashed else '-'
    hw, hl = W / 2, L / 2
    body = [(-hw + 120, -hl), (hw - 120, -hl), (hw, -hl + 250), (hw, hl - 350), (hw - 150, hl), (-hw + 150, hl), (-hw, hl - 350), (-hw, -hl + 250)]
    R.pline([T(x, y) for x, y in body], 'A-EQPM', closed=True, ls=ls)
    R.pline([T(x, y) for x, y in [(-hw + 150, hl - 1300), (hw - 150, hl - 1300), (hw - 250, hl - 2000), (-hw + 250, hl - 2000)]], 'A-EQPM', closed=True, ls=ls)
    R.pline([T(x, y) for x, y in [(-hw + 200, -hl + 700), (hw - 200, -hl + 700), (hw - 280, -hl + 1200), (-hw + 280, -hl + 1200)]], 'A-EQPM', closed=True, ls=ls)

def shelves(R, x0, y0, x1, y1, n=None, ly='A-FURN'):
    box(R, x0, y0, x1, y1, ly)
    if (x1 - x0) > (y1 - y0):
        k = n or max(1, int((x1 - x0) / 900))
        for i in range(1, k): R.line((x0 + (x1 - x0) * i / k, y0), (x0 + (x1 - x0) * i / k, y1), ly)
    else:
        k = n or max(1, int((y1 - y0) / 900))
        for i in range(1, k): R.line((x0, y0 + (y1 - y0) * i / k), (x1, y0 + (y1 - y0) * i / k), ly)

def wardrobe_run(R, r, wall, a0, a1, off=OFF):
    """2000-wide wardrobe blocks along a wall between a0..a1"""
    n = int((a1 - a0) // 2000)
    st = a0 + ((a1 - a0) - n * 2000) / 2
    for i in range(n):
        blk(R, 'WR_WD016_A', r, wall, st + 1000 + i * 2000, off)

def plant(R, cx, cy, rad=450):
    R.circle((cx, cy), rad, 'L-PLNT')
    for k in range(6):
        a = math.radians(k * 60)
        R.line((cx, cy), (cx + rad * .8 * math.cos(a), cy + rad * .8 * math.sin(a)), 'L-PLNT', lw=0.08)

def lounger(R, cx, cy, ang=0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    T = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    R.pline([T(x, y) for x, y in [(-330, -950), (330, -950), (330, 950), (-330, 950)]], 'A-FURN', closed=True)
    R.line(T(-330, 400), T(330, 400), 'A-FURN')

def arcs(R, x0, y0, x1, y1, n=5, seed=0):
    """curved ceramic-mosaic floor lines (Intrinsic: colored tiles in natural curved lines)"""
    import math
    for k in range(n):
        pts = []
        yb = y0 + (y1 - y0) * (k + 0.6) / (n + 0.2)
        amp = (y1 - y0) / (n * 2.2)
        for i in range(41):
            x = x0 + (x1 - x0) * i / 40
            pts.append((x, yb + amp * math.sin(2 * math.pi * (i / 40 * 1.3 + 0.17 * k + seed))))
        R.pline(pts, 'A-HIDD', lw=0.08, c='#b0805e')

def oven(R, cx, cy, r=700):
    """wood-fired oven (the 'forno') — dome on a masonry base"""
    R.rect(cx - r - 150, cy - r - 150, cx + r + 150, cy + r + 150, 'A-EQPM')
    R.circle((cx, cy), r, 'A-EQPM'); R.circle((cx, cy), r * 0.55, 'A-HIDD', lw=0.08)
    R.text((cx, cy), 'เตาอบ\nฟืน', 110, 'A-ANNO')

def bench(R, x0, y0, x1, y1):
    box(R, x0, y0, x1, y1)
    if (x1 - x0) > (y1 - y0):
        for x in range(int(x0) + 450, int(x1), 450): R.line((x, y0), (x, y1), 'A-FURN', lw=0.08)
    else:
        for y in range(int(y0) + 450, int(y1), 450): R.line((x0, y), (x1, y), 'A-FURN', lw=0.08)

def bath_set(R, b, wc, basin, shower=None, tub=None):
    """wc/basin/shower = (wall, along)"""
    blk(R, 'SN_SN001_A', b, *wc)
    blk(R, 'SN_SN018_A', b, *basin)
    if shower: blk(R, 'SN_SN039_A', b, *shower)
    if tub: blk(R, 'SN_SN034_A', b, *tub)

def furnish(R, fl):
    F = lambda n: find(n, fl)
    if fl == 1:
        g = F('โรงจอดรถ 4 คัน')
        for i in range(4):
            car(R, g.x0 + 1437 + i * 2875, g.y0 + 400 + 2450, 0)
        R.rect(g.x0 + 200, g.y0 + 150, g.x0 + 700, g.y0 + 400, 'A-EQPM'); R.text((g.x0 + 450, g.y0 + 650), 'EV', 150, 'A-ANNO')
        R.text((g.x1 - 650, g.y1 - 1500), 'ชั้นวาง\nจักรยาน', 110, 'A-ANNO')
        for i in range(3): R.rect(g.x1 - 1150 + i * 300, g.y0 + 600, g.x1 - 1100 + i * 300, g.y0 + 2600, 'A-EQPM')
        for nm in ('ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2'):
            m = F(nm)
            blk(R, 'BD_B018_B', m, 'W', m.y0 + 1500)
            blk(R, 'WR_WD030_A', m, 'E', m.y0 + 1400)
        mb = F('ห้องน้ำแม่บ้าน')
        bath_set(R, mb, ('N', mb.x0 + 750), ('E', mb.y0 + 1600), ('S', mb.x0 + 750))
        k = F('ครัวไทย (ครัวหนัก)')
        counter(R, k.x1 - 700, k.y0 + 100, k.x1 - 100, k.y1 - 1300, hob=(k.x1 - 400, k.y0 + 2000))
        R.rect(k.x1 - 900, k.y0 + 1300, k.x1 - 100, k.y0 + 2700, 'A-HIDD', ls='--'); R.text((k.x1 - 1150, k.y0 + 2000), 'ฮูดดูดควัน', 110, 'A-ANNO', rot=90)
        counter(R, k.x0 + 100, k.y0 + 1400, k.x0 + 700, k.y1 - 1300, sink=(k.x0 + 400, k.y0 + 2600))
        table(R, (k.x0 + k.x1) / 2, (k.y0 + k.y1) / 2 + 300, 1200, 800, 2, ends=False)
        l = F('ห้องซักรีด')
        for i in range(4):
            R.rect(l.x1 - 720, l.y0 + 900 + i * 700, l.x1 - 120, l.y0 + 1500 + i * 700, 'A-EQPM'); R.circle((l.x1 - 420, l.y0 + 1200 + i * 700), 220, 'A-EQPM')
        box(R, l.x0 + 150, l.y0 + 1000, l.x0 + 750, l.y0 + 3600); R.text((l.x0 + 450, l.y0 + 2300), 'โต๊ะพับผ้า', 110, 'A-ANNO', rot=90)
        me = F('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ')
        for i in range(4): R.rect(me.x1 - 550, me.y0 + 400 + i * 1000, me.x1 - 150, me.y0 + 1200 + i * 1000, 'A-EQPM')
        R.text((me.x0 + 900, (me.y0 + me.y1) / 2), 'MDB / UPS\n/ ปั๊มน้ำ', 110, 'A-ANNO')
        v = F('ลานใต้ชายคา / ศาลาริมสระ')
        R.block('NK_SOFA3', (v.x0 + 2800, v.y0 + 2600), 0); R.block('NK_ARMCH', (v.x0 + 1100, v.y0 + 3900), -90); R.block('NK_ARMCH', (v.x0 + 4500, v.y0 + 3900), 90)
        R.rect(v.x0 + 2200, v.y0 + 3500, v.x0 + 3400, v.y0 + 4300, 'A-FURN')
        oven(R, v.x1 - 1100, v.y0 + 1100, 600)
        lounger(R, v.x0 + 900, v.y0 + 1200, 90)
        h = F('โถงกลาง "Forno hall"')
        table(R, h.x0 + 4200, (h.y0 + h.y1) / 2, 4800, 1000, 5, ends=False)
        for xx in (h.x0 + 9000, h.x0 + 10600): plant(R, xx, h.y0 + 600, 380)
        bench(R, h.x0 + 11500, h.y0 + 150, h.x0 + 14000, h.y0 + 600)
        e = F('โถงต้อนรับ (ทางเข้าทิศตะวันออก)')
        box(R, e.x0 + 300, e.y1 - 600, e.x1 - 300, e.y1 - 150); R.text(((e.x0 + e.x1) / 2, e.y1 - 900), 'ตู้รองเท้า / เสื้อโค้ท', 110, 'A-ANNO')
        bench(R, e.x0 + 150, e.y0 + 1500, e.x0 + 600, e.y0 + 3300); plant(R, e.x1 - 700, e.y0 + 700, 380)
        gb = F('ห้องนอนแขก/ผู้สูงอายุ')
        blk(R, 'BD_B003_B', gb, 'W', (gb.y0 + gb.y1) / 2 - 400)
        R.block('NK_ARMCH', (gb.x1 - 1100, gb.y0 + 900), 0)
        gt = F('ห้องน้ำห้องแขก')
        bath_set(R, gt, ('W', gt.y0 + 2300), ('W', gt.y0 + 1200), ('N', gt.x1 - 900))
        gc = F('ตู้เสื้อผ้าห้องแขก'); wardrobe_run(R, gc, 'N', gc.x0 + 150, gc.x1 - 150)
    if fl == 2:
        s = F('ครัวโชว์ + ไอส์แลนด์')
        counter(R, s.x0 + 100, s.y0 + 600, s.x0 + 700, s.y1 - 300, sink=(s.x0 + 400, s.y0 + 2000), hob=(s.x0 + 400, s.y0 + 3800))
        counter(R, s.x0 + 2100, s.y0 + 1500, s.x0 + 3200, s.y0 + 4000)
        for yy in (s.y0 + 1900, s.y0 + 2750, s.y0 + 3600): R.circle((s.x0 + 3550, yy), 200, 'A-FURN')
        d = F('ห้องรับประทานอาหาร')
        table(R, (d.x0 + d.x1) / 2, (d.y0 + d.y1) / 2 + 100, 3600, 1100, 5, ends=True)
        lv = F('ห้องนั่งเล่น')
        cx, cy = (lv.x0 + lv.x1) / 2 + 600, (lv.y0 + lv.y1) / 2 - 100
        R.block('NK_SOFA3', (cx, cy - 1500), 0); R.block('NK_SOFA3', (cx, cy + 1500), 180)
        R.block('NK_ARMCH', (cx - 1900, cy), -90); R.block('NK_ARMCH', (cx + 1900, cy), 90)
        R.rect(cx - 650, cy - 450, cx + 650, cy + 450, 'A-FURN'); R.rect(cx - 1800, cy - 1800, cx + 1800, cy + 1800, 'A-HIDD', ls='--')
        b = F('ระเบียงไม้ทิศใต้ ชั้น 2')
        for xx in (b.x0 + 9500, b.x0 + 15000, b.x0 + 20500): R.block('NK_ARMCH', (xx, b.y0 + 750), 0); R.block('NK_ARMCH', (xx + 900, b.y0 + 750), 0)
        p = F('Walk-in Pantry & ห้องเย็น')
        shelves(R, p.x0 + 300, p.y1 - 550, p.x1 - 1600, p.y1 - 100, n=4); shelves(R, p.x0 + 100, p.y0 + 300, p.x0 + 500, p.y1 - 700, n=3)
        R.rect(p.x1 - 1500, p.y0 + 200, p.x1 - 200, p.y1 - 200, 'A-EQPM'); R.text((p.x1 - 850, (p.y0 + p.y1) / 2), 'ห้องเย็น', 110, 'A-ANNO', rot=90)
        w = F('ห้องไวน์ / ซิการ์')
        shelves(R, w.x0 + 1500, w.y1 - 500, w.x1 - 100, w.y1 - 100, n=5); shelves(R, w.x1 - 500, w.y0 + 300, w.x1 - 100, w.y1 - 600, n=5)
        R.block('NK_ARMCH', (w.x0 + 1300, w.y0 + 900), 0); R.block('NK_ARMCH', (w.x0 + 2300, w.y0 + 900), 0)
        pw = F('ห้องน้ำแขก (Powder)')
        bath_set(R, pw, ('N', pw.x0 + 700), ('E', pw.y0 + 1700))
        b2 = F('ห้องนอน Junior Suite 2'); blk(R, 'BD_B003_B', b2, 'W', b2.y0 + 2900); R.block('NK_ARMCH', (b2.x1 - 900, b2.y0 + 800), 0)
        c2 = F('ตู้เสื้อผ้า Junior Suite 2'); wardrobe_run(R, c2, 'E', c2.y0 + 1000, c2.y1)
        t2 = F('ห้องน้ำ Junior Suite 2'); bath_set(R, t2, ('E', t2.y0 + 1700), ('W', t2.y0 + 1300), ('N', t2.x0 + 700))
        c3 = F('ตู้เสื้อผ้า Junior Suite 3'); wardrobe_run(R, c3, 'W', c3.y0 + 300, c3.y1 - 200)
        t3 = F('ห้องน้ำ Junior Suite 3'); bath_set(R, t3, ('W', t3.y0 + 1700), ('E', t3.y0 + 1300), ('N', t3.x1 - 700))
        b3 = F('ห้องนอน Junior Suite 3'); blk(R, 'BD_B003_B', b3, 'E', b3.y0 + 2900); R.block('NK_ARMCH', (b3.x0 + 1700, b3.y1 - 800), 180)
        o = F('ห้องทำงาน & ห้องสมุด')
        R.block('FW_FW050_A', ((o.x0 + o.x1) / 2 + 600, o.y0 + 2400), 0)
        shelves(R, o.x1 - 500, o.y0 + 300, o.x1 - 100, o.y1 - 1500, n=6); shelves(R, o.x0 + 1200, o.y0 + 100, o.x0 + 3800, o.y0 + 450, n=3)
        table(R, o.x0 + 2000, o.y1 - 1700, 1600, 800, 2, ends=False)
    if fl == 3:
        w = F('Walk-in Dressing (His & Hers)')
        wardrobe_run(R, w, 'S', w.x0 + 300, w.x1 - 300)
        box(R, (w.x0 + w.x1) / 2 - 900, (w.y0 + w.y1) / 2 - 450, (w.x0 + w.x1) / 2 + 900, (w.y0 + w.y1) / 2 + 450)
        R.text(((w.x0 + w.x1) / 2, (w.y0 + w.y1) / 2), 'ไอส์แลนด์ลิ้นชัก', 100, 'A-ANNO')
        b = F('ห้องน้ำ Spa + Jacuzzi')
        blk(R, 'SN_SN064_A', b, 'S', b.x0 + 1800); blk(R, 'SN_SN042_A', b, 'W', b.y1 - 1300)
        blk(R, 'SN_SN001_A', b, 'N', b.x0 + 3300); blk(R, 'SN_SN018_A', b, 'N', b.x0 + 2200); blk(R, 'SN_SN018_A', b, 'N', b.x0 + 1300)
        m = F('ห้องนอน Master Suite')
        blk(R, 'BD_B005_B', m, 'W', m.y0 + 1900)
        R.block('NK_SOFA2', (m.x1 - 2200, m.y0 + 2200), 90); R.rect(m.x1 - 3600, m.y0 + 1700, m.x1 - 2900, m.y0 + 2700, 'A-FURN')
        bl = F('ระเบียงไม้ทิศใต้ ชั้น 3')
        for xx in (bl.x0 + 15600, bl.x0 + 16900): lounger(R, xx, bl.y0 + 750, 90)
        plant(R, bl.x0 + 1200, bl.y0 + 750, 450); plant(R, bl.x0 + 7000, bl.y0 + 750, 450)
        lg = F('ลอจเจียทิศเหนือ (ระแนงไม้)')
        table(R, lg.x0 + 7000, lg.y0 + 2600, 2400, 1000, 3, ends=True)
        lounger(R, lg.x0 + 2600, lg.y0 + 2600, 0); lounger(R, lg.x0 + 3500, lg.y0 + 2600, 0)
        for xx in (lg.x0 + 10600, lg.x1 - 900): plant(R, xx, lg.y1 - 900, 450)
        R.text(((lg.x0 + lg.x1) / 2, lg.y1 - 350), 'ระแนงไม้ (เกล็ดตั้ง 50x150 @150) แนวราวกันตก', 130, 'A-ANNO', va='top')
        ne = F('ลอจเจียตะวันออกเฉียงเหนือ')
        table(R, ne.x0 + 3400, ne.y0 + 2400, 900, 0, 4, round_=True); plant(R, ne.x1 - 800, ne.y0 + 800, 450)
    if fl == 4:
        c = F('Master Walk-in Closet ชั้น 4')
        wardrobe_run(R, c, 'S', c.x0 + 300, c.x1 - 300); wardrobe_run(R, c, 'E', c.y0 + 1300, c.y1 - 1500)
        box(R, (c.x0 + c.x1) / 2 - 800, (c.y0 + c.y1) / 2 - 300, (c.x0 + c.x1) / 2 + 800, (c.y0 + c.y1) / 2 + 600)
        R.rect(c.x0 + 300, c.y1 - 650, c.x0 + 1700, c.y1 - 150, 'A-FURN'); R.text((c.x0 + 1000, c.y1 - 400), 'โต๊ะเครื่องแป้ง', 100, 'A-ANNO')
        mt = F('ระเบียง Master (ใต้ชายคา)')
        lounger(R, mt.x0 + 1500, mt.y0 + 2600, 0); lounger(R, mt.x0 + 2600, mt.y0 + 2600, 0); plant(R, mt.x1 - 900, mt.y0 + 900, 450)
        R.rect(mt.x0 + 3400, mt.y0 + 3200, mt.x1 - 800, mt.y0 + 5200, 'A-EQPM'); R.text(((mt.x0 + mt.x1) / 2 + 1300, mt.y0 + 4200), 'อ่างแช่กลางแจ้ง', 110, 'A-ANNO')
        lg = F('ห้องนั่งเล่นครอบครัว & Upper Gallery')
        cx, cy = (lg.x0 + lg.x1) / 2 + 400, (lg.y0 + lg.y1) / 2 + 300
        R.block('NK_SOFA3', (cx, cy - 1400), 0); R.block('NK_ARMCH', (cx - 1700, cy), -90); R.block('NK_ARMCH', (cx + 1700, cy), 90)
        R.block('NK_TVCAB', (cx, lg.y1 - 120), 180); R.rect(cx - 600, cy - 400, cx + 600, cy + 400, 'A-FURN')
        shelves(R, lg.x0 + 100, lg.y0 + 1500, lg.x0 + 500, lg.y1 - 300, n=6)
        v = F('ระเบียง & BBQ (ใต้ชายคา)')
        counter(R, v.x1 - 700, v.y0 + 1000, v.x1 - 100, v.y1 - 1200, hob=(v.x1 - 400, v.y0 + 2600))
        R.text((v.x1 - 1100, v.y0 + 2600), 'BBQ', 140, 'A-ANNO', rot=90)
        oven(R, v.x1 - 1000, v.y1 - 800, 500)
        table(R, v.x0 + 3800, v.y0 + 3300, 3000, 1000, 4, ends=True)
        R.block('NK_SOFA3', (v.x0 + 3800, v.y0 + 1000), 0)
        av = F('ห้องอุปกรณ์ AV / เก็บของ'); shelves(R, av.x0 + 300, av.y1 - 550, av.x1 - 300, av.y1 - 100, n=5)
        wc = F('ห้องน้ำชั้น 4'); bath_set(R, wc, ('E', wc.y1 - 700), ('N', wc.x0 + 1200), ('N', wc.x0 + 2600) if False else None)
        t = F('ห้องโฮมเธียเตอร์')
        R.rect(t.x1 - 300, t.y0 + 600, t.x1 - 150, t.y1 - 600, 'A-EQPM'); R.text((t.x1 - 700, (t.y0 + t.y1) / 2), 'จอ 150"', 150, 'A-ANNO', rot=90)
        for xx in (t.x1 - 3200, t.x1 - 5000):
            R.block('NK_SOFA3', (xx, (t.y0 + t.y1) / 2), -90)
