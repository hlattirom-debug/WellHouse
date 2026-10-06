# -*- coding: utf-8 -*-
"""Furniture & fittings: LOD400 blocks (NACK HOUSE library) + simple parametric items."""
import math
from plan5 import find

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

def furnish(R, fl):
    F = lambda n: find(n, fl)
    if fl == 1:
        g = F('โรงจอดรถ 4 คัน')
        for i in range(4):
            car(R, g.x0 + 1500 + i * 3200, g.y0 + 400 + 2450, 0)
        R.rect(g.x0 + 200, g.y0 + 150, g.x0 + 700, g.y0 + 400, 'A-EQPM'); R.text((g.x0 + 450, g.y0 + 650), 'EV', 150, 'A-ANNO')
        for nm in ('ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2'):
            m = F(nm)
            blk(R, 'BD_B018_B', m, 'N', m.x0 + 900)
            blk(R, 'WR_WD030_A', m, 'S', m.x1 - 1400) if m.d > 2600 else None
        mb = F('ห้องน้ำแม่บ้าน')
        blk(R, 'SN_SN001_A', mb, 'N', mb.x0 + 600); blk(R, 'SN_SN018_A', mb, 'N', mb.x0 + 1500); blk(R, 'SN_SN039_A', mb, 'S', mb.x0 + 1200)
        k = F('ครัวไทย (ครัวหนัก)')
        counter(R, k.x0 + 100, k.y0 + 100, k.x1 - 100, k.y0 + 700, hob=((k.x0 + k.x1) / 2, k.y0 + 400))
        counter(R, k.x0 + 100, k.y0 + 700, k.x0 + 700, k.y1 - 1600, sink=(k.x0 + 400, k.y0 + 2400))
        R.rect(k.x0 + 200, k.y0 + 100, k.x1 - 200, k.y0 + 900, 'A-HIDD', ls='--'); R.text(((k.x0 + k.x1) / 2, k.y0 + 1100), 'ฮูดดูดควัน', 110, 'A-ANNO')
        table(R, (k.x0 + k.x1) / 2 + 300, k.y1 - 1500, 1200, 800, 2, ends=False)
        l = F('ห้องซักรีด')
        for i in range(4):
            R.rect(l.x0 + 300 + i * 700, l.y1 - 720, l.x0 + 900 + i * 700, l.y1 - 120, 'A-EQPM'); R.circle((l.x0 + 600 + i * 700, l.y1 - 420), 220, 'A-EQPM')
        box(R, l.x0 + 800, l.y0 + 600, l.x0 + 3200, l.y0 + 1200); R.text((l.x0 + 2000, l.y0 + 900), 'โต๊ะพับผ้า', 120, 'A-ANNO')
        me = F('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ')
        for i in range(3): R.rect(me.x0 + 400 + i * 1000, me.y1 - 550, me.x0 + 1200 + i * 1000, me.y1 - 150, 'A-EQPM')
        R.text(((me.x0 + me.x1) / 2, me.y1 - 900), 'MDB / UPS / ปั๊มน้ำ', 120, 'A-ANNO')
        v = F('ลานใต้ถุน / ศาลาริมสระ')
        arcs(R, v.x0 + 200, v.y0 + 200, v.x1 - 200, v.y1 - 200, 5)
        R.block('NK_SOFA3', (v.x0 + 3000, v.y0 + 900), 0); R.block('NK_ARMCH', (v.x0 + 1300, v.y0 + 2300), -90); R.block('NK_ARMCH', (v.x0 + 4700, v.y0 + 2300), 90)
        R.rect(v.x0 + 2400, v.y0 + 1900, v.x0 + 3600, v.y0 + 2700, 'A-FURN')
        table(R, v.x0 + 8800, v.y0 + 2300, 2400, 1000, 3, ends=True)
        R.block('NK_DAYBED', (v.x1 - 1600, v.y0 + 1500), 0) if False else lounger(R, v.x1 - 1500, v.y0 + 2200, 0)
        h = F('โถงกลาง'); arcs(R, h.x0 + 200, h.y0 + 200, h.x1 - 200, h.y1 - 200, 3, 0.4)
        e = F('โถงทางเข้า (หลังโดม)'); arcs(R, e.x0 + 200, e.y0 + 200, e.x1 - 200, e.y1 - 200, 4, 0.8)
        box(R, e.x0 + 300, e.y0 + 800, e.x0 + 750, e.y0 + 3200); plant(R, e.x1 - 700, e.y0 + 900, 400)
        gb = F('ห้องนอนแขก/ผู้สูงอายุ')
        blk(R, 'BD_B003_B', gb, 'E', (gb.y0 + gb.y1) / 2)
        R.block('NK_ARMCH', (gb.x0 + 1000, gb.y0 + 900), 0)
        gt = F('ห้องน้ำห้องแขก')
        blk(R, 'SN_SN001_A', gt, 'E', gt.y1 - 600); blk(R, 'SN_SN018_A', gt, 'N', gt.x0 + 800); blk(R, 'SN_SN043_A', gt, 'E', gt.y0 + 1000)
        gc = F('ตู้เสื้อผ้าห้องแขก'); wardrobe_run(R, gc, 'W', gc.y0 + 400, gc.y1)
        c = F('ห้องเก็บเสื้อโค้ท'); shelves(R, c.x0 + 300, c.y1 - 650, c.x1 - 300, c.y1 - 100, n=4)
        st = F('ห้องเก็บของ / จักรยาน')
        for i in range(4): R.rect(st.x0 + 600 + i * 900, st.y0 + 300, st.x0 + 700 + i * 900, st.y0 + 2000, 'A-EQPM')
        R.text(((st.x0 + st.x1) / 2, st.y1 - 400), 'ราวจักรยาน', 110, 'A-ANNO')
        import math
        cx, cy = 21000, 22300
        table(R, cx, cy - 300, 1100, 0, 0, round_=True)
        lk = F('โถงพักคอย (จากโรงรถ)'); box(R, lk.x0 + 200, lk.y0 + 3500, lk.x0 + 650, lk.y1 - 600)
    if fl == 2:
        s = F('ครัวโชว์ + ไอส์แลนด์')
        counter(R, s.x0 + 100, s.y0 + 100, s.x0 + 700, s.y1 - 300, sink=(s.x0 + 400, s.y0 + 2000), hob=(s.x0 + 400, s.y0 + 4200))
        counter(R, s.x0 + 1900, s.y0 + 1800, s.x0 + 3000, s.y0 + 4400)
        for yy in (s.y0 + 2200, s.y0 + 3100, s.y0 + 4000): R.circle((s.x0 + 3350, yy), 200, 'A-FURN')
        d = F('ห้องรับประทานอาหาร')
        table(R, (d.x0 + d.x1) / 2, (d.y0 + d.y1) / 2 - 200, 3600, 1100, 5, ends=True)
        R.text(((d.x0 + d.x1) / 2, d.y0 + 900), 'โคมไฟเซรามิก (เศษเซรามิกรีไซเคิล)', 110, 'A-ANNO')
        lv = F('ห้องนั่งเล่น')
        cx, cy = (lv.x0 + lv.x1) / 2, (lv.y0 + lv.y1) / 2 - 200
        R.block('NK_SOFA3', (cx, cy - 1500), 0); R.block('NK_SOFA3', (cx, cy + 1500), 180)
        R.block('NK_ARMCH', (cx - 1900, cy), -90); R.block('NK_ARMCH', (cx + 1900, cy), 90)
        R.rect(cx - 650, cy - 450, cx + 650, cy + 450, 'A-FURN'); R.rect(cx - 1800, cy - 1800, cx + 1800, cy + 1800, 'A-HIDD', ls='--')
        b = F('ระเบียงตะวันออกเฉียงใต้ ชั้น 2'); lounger(R, b.x0 + 800, b.y0 + 2500, 0); plant(R, b.x1 - 700, b.y1 - 900, 400)
        p = F('Walk-in Pantry & ห้องเย็น')
        shelves(R, p.x0 + 300, p.y1 - 550, p.x1 - 1600, p.y1 - 100, n=4)
        R.rect(p.x1 - 1500, p.y0 + 200, p.x1 - 200, p.y1 - 200, 'A-EQPM'); R.text((p.x1 - 850, (p.y0 + p.y1) / 2), 'ห้องเย็น', 110, 'A-ANNO')
        w = F('ห้องไวน์ / ซิการ์')
        shelves(R, w.x0 + 100, w.y0 + 300, w.x0 + 500, w.y1 - 300, n=8); shelves(R, w.x1 - 500, w.y0 + 1500, w.x1 - 100, w.y1 - 300, n=6)
        R.block('NK_ARMCH', ((w.x0 + w.x1) / 2, w.y0 + 1900), 0)
        pw = F('ห้องน้ำแขก (Powder)')
        blk(R, 'SN_SN001_A', pw, 'E', pw.y0 + 600); blk(R, 'SN_SN018_A', pw, 'N', pw.x1 - 900)
        b2 = F('ห้องนอน Junior Suite 2'); blk(R, 'BD_B003_B', b2, 'S', b2.x0 + 1600); R.block('NK_ARMCH', (b2.x0 + 900, b2.y1 - 900), 180)
        c2 = F('ตู้เสื้อผ้า Junior Suite 2'); wardrobe_run(R, c2, 'E', c2.y0 + 100, c2.y1)
        t2 = F('ห้องน้ำ Junior Suite 2'); blk(R, 'SN_SN001_A', t2, 'E', t2.y0 + 600); blk(R, 'SN_SN018_A', t2, 'N', t2.x0 + 800); blk(R, 'SN_SN039_A', t2, 'W', t2.y1 - 650)
        ga = F('แกลเลอรีหนังสือ'); shelves(R, ga.x0 + 100, ga.y0 + 400, ga.x0 + 450, ga.y1 - 1600, n=6); shelves(R, ga.x1 - 450, ga.y0 + 400, ga.x1 - 100, ga.y1 - 400, n=7)
        o = F('ห้องทำงาน & ห้องสมุด')
        R.block('FW_FW050_A', ((o.x0 + o.x1) / 2, o.y1 - 1600), 180)
        shelves(R, o.x0 + 100, o.y0 + 1500, o.x0 + 500, o.y1 - 300, n=6)
        table(R, (o.x0 + o.x1) / 2 + 400, o.y0 + 2200, 1600, 800, 2, ends=False)
        c3 = F('ตู้เสื้อผ้า Junior Suite 3'); wardrobe_run(R, c3, 'W', c3.y0 + 100, c3.y1)
        t3 = F('ห้องน้ำ Junior Suite 3'); blk(R, 'SN_SN001_A', t3, 'W', t3.y0 + 600); blk(R, 'SN_SN018_A', t3, 'N', t3.x1 - 800); blk(R, 'SN_SN039_A', t3, 'E', t3.y1 - 650)
        b3 = F('ห้องนอน Junior Suite 3'); blk(R, 'BD_B003_B', b3, 'N', (b3.x0 + b3.x1) / 2 + 300); R.block('NK_ARMCH', (b3.x1 - 900, b3.y0 + 900), 0)
    if fl == 3:
        w = F('Walk-in Dressing (His & Hers)')
        wardrobe_run(R, w, 'W', w.y0 + 300, w.y1 - 300); wardrobe_run(R, w, 'S', w.x0 + 900, w.x1 - 300)
        box(R, (w.x0 + w.x1) / 2 - 500, (w.y0 + w.y1) / 2 - 450, (w.x0 + w.x1) / 2 + 1000, (w.y0 + w.y1) / 2 + 450)
        b = F('ห้องน้ำ Spa + Jacuzzi')
        blk(R, 'SN_SN034_A', b, 'S', b.x0 + 1500); blk(R, 'SN_SN042_A', b, 'E', b.y1 - 1600)
        blk(R, 'SN_SN064_A', b, 'N', b.x0 + 1500); blk(R, 'SN_SN001_A', b, 'W', b.y1 - 700)
        m = F('ห้องนอน Master Suite')
        blk(R, 'BD_B005_B', m, 'W', (m.y0 + m.y1) / 2 + 900)
        R.block('NK_SOFA2', ((m.x0 + m.x1) / 2 + 1500, m.y0 + 400), 0)
        R.block('NK_TVCAB', (m.x1 - 1500, m.y1 - 120), 180)
        bl = F('ระเบียง Master ชั้น 3'); lounger(R, bl.x0 + 1000, bl.y0 + 2500, 0); lounger(R, bl.x0 + 2300, bl.y0 + 2500, 0)
        st = F('ห้องเก็บของชั้น 3'); shelves(R, st.x0 + 300, st.y1 - 550, st.x1 - 300, st.y1 - 100, n=5)
        lg = F('ลอจเจียทิศเหนือ (ฉากกระจก U)')
        table(R, lg.x0 + 2600, lg.y0 + 3600, 900, 0, 4, round_=True)
        R.block('NK_DAYBED', (lg.x1 - 2200, lg.y1 - 1300), 0) if False else lounger(R, lg.x1 - 1800, lg.y1 - 1600, 90)
        for xx in (lg.x0 + 5200, lg.x1 - 900): plant(R, xx, lg.y0 + 2600, 450)
        R.text(((lg.x0 + lg.x1) / 2, lg.y1 + 250), 'ฉากกระจกตัว U (U-glass) โปร่งแสง สลับช่องเปิด', 140, 'A-ANNO', va='bottom')
    if fl == 4:
        c = F('Master Walk-in Closet ชั้น 4')
        wardrobe_run(R, c, 'S', c.x0 + 300, c.x1 - 300); wardrobe_run(R, c, 'W', c.y0 + 900, c.y1 - 200)
        box(R, (c.x0 + c.x1) / 2 - 800, (c.y0 + c.y1) / 2 - 450, (c.x0 + c.x1) / 2 + 800, (c.y0 + c.y1) / 2 + 450)
        R.rect(c.x1 - 1600, c.y1 - 650, c.x1 - 200, c.y1 - 150, 'A-FURN'); R.text((c.x1 - 900, c.y1 - 400), 'โต๊ะเครื่องแป้ง', 100, 'A-ANNO')
        mt = F('ระเบียง Master (ดาดฟ้า)'); lounger(R, mt.x0 + 1200, mt.y0 + 2200, 0); lounger(R, mt.x0 + 2500, mt.y0 + 2200, 0); plant(R, mt.x1 - 800, mt.y1 - 1300, 450)
        lg = F('ห้องนั่งเล่นครอบครัว (หลังคาโค้ง)')
        cx, cy = (lg.x0 + lg.x1) / 2, (lg.y0 + lg.y1) / 2
        R.block('NK_SOFA3', (cx, cy - 1400), 0); R.block('NK_ARMCH', (cx - 1700, cy), -90); R.block('NK_ARMCH', (cx + 1700, cy), 90)
        R.block('NK_TVCAB', (cx, lg.y1 - 120), 180); R.rect(cx - 600, cy - 400, cx + 600, cy + 400, 'A-FURN')
        for xx in (lg.x0 + 150, cx, lg.x1 - 150):
            R.line((xx, lg.y0 + 100), (xx, lg.y1 - 100), 'A-HIDD', ls='--', lw=0.1)
        R.text((cx, lg.y1 - 1000), 'หลังคาโค้งอิฐ (เหนือศีรษะ) สปริง +13.80 ยอด +14.85', 110, 'A-ANNO')
        v = F('ระเบียง & BBQ (หลังคาคลุม)')
        counter(R, v.x1 - 700, v.y0 + 1500, v.x1 - 100, v.y1 - 600, hob=(v.x1 - 400, v.y0 + 2800))
        R.text((v.x1 - 1100, v.y0 + 3200), 'BBQ', 140, 'A-ANNO', rot=90)
        table(R, v.x0 + 2400, v.y0 + 3000, 1000, 2400, 3, ends=True)
        av = F('ห้องอุปกรณ์ AV / เก็บของ'); shelves(R, av.x0 + 300, av.y1 - 550, av.x1 - 300, av.y1 - 100, n=5)
        wc = F('ห้องน้ำชั้น 4'); blk(R, 'SN_SN001_A', wc, 'E', wc.y0 + 600); blk(R, 'SN_SN018_A', wc, 'S', wc.x1 - 900)
        t = F('ห้องโฮมเธียเตอร์')
        R.rect(t.x0 + 150, t.y0 + 600, t.x0 + 300, t.y1 - 600, 'A-EQPM'); R.text((t.x0 + 700, (t.y0 + t.y1) / 2), 'จอ 150"', 150, 'A-ANNO', rot=90)
        for xx in (t.x0 + 3600, t.x0 + 5500):
            R.block('NK_SOFA3', (xx, (t.y0 + t.y1) / 2), 90)
