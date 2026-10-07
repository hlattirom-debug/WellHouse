# -*- coding: utf-8 -*-
"""Furniture & fittings: LOD400 blocks (NACK HOUSE library) + simple parametric items."""
import math
from plan7 import find

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
        for cx_ in (11500, 15000, 18500, 21300): car(R, cx_, g.y0 + 400 + 2450, 0)
        R.rect(g.x0 + 200, g.y0 + 150, g.x0 + 700, g.y0 + 400, 'A-EQPM'); R.text((g.x0 + 450, g.y0 + 650), 'EV', 150, 'A-ANNO')
        fo = F('โถงต้อนรับใต้โค้งอิฐ (สูง 2 ชั้น)')
        bench(R, fo.x0 + 150, fo.y0 + 1200, fo.x0 + 600, fo.y0 + 3600); box(R, fo.x1 - 600, fo.y0 + 2500, fo.x1 - 150, fo.y1 - 900)
        plant(R, fo.x0 + 900, fo.y1 - 900, 400)
        me = F('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ')
        for i in range(4): R.rect(me.x0 + 300, me.y0 + 500 + i * 1300, me.x0 + 900, me.y0 + 1500 + i * 1300, 'A-EQPM')
        R.text(((me.x0 + me.x1) / 2 + 300, (me.y0 + me.y1) / 2), 'MDB / UPS\n/ ปั๊มน้ำ', 110, 'A-ANNO')
        gb = F('ห้องนอนแขก/ผู้สูงอายุ'); blk(R, 'BD_B003_B', gb, 'S', gb.x0 + 1700)
        gt = F('ห้องน้ำห้องแขก'); bath_set(R, gt, ('N', gt.x0 + 700), ('W', gt.y0 + 1500), ('N', gt.x1 - 650))
        gc = F('ตู้เสื้อผ้าห้องแขก'); wardrobe_run(R, gc, 'N', gc.x0 + 0, gc.x1)
        k = F('ครัวไทย (ครัวหนัก)')
        counter(R, k.x0 + 100, k.y0 + 100, k.x1 - 100, k.y0 + 700, hob=((k.x0 + k.x1) / 2, k.y0 + 400))
        R.rect(k.x0 + 600, k.y0 + 100, k.x1 - 600, k.y0 + 900, 'A-HIDD', ls='--'); R.text(((k.x0 + k.x1) / 2, k.y0 + 1100), 'ฮูดดูดควัน', 100, 'A-ANNO')
        counter(R, k.x0 + 1200, k.y0 + 2300, k.x1 - 1000, k.y0 + 3100, sink=((k.x0 + k.x1) / 2, k.y0 + 2700))
        l = F('ห้องซักรีด')
        for i in range(4):
            R.rect(l.x0 + 300 + i * 700, l.y1 - 720, l.x0 + 900 + i * 700, l.y1 - 120, 'A-EQPM'); R.circle((l.x0 + 600 + i * 700, l.y1 - 420), 220, 'A-EQPM')
        box(R, l.x0 + 1000, l.y0 + 500, l.x1 - 600, l.y0 + 1100)
        v = F('ศาลาริมสระ (ทะลุคอร์ต)')
        R.block('NK_SOFA3', (v.x0 + 2500, v.y0 + 900), 0); R.block('NK_ARMCH', (v.x0 + 800, v.y0 + 2200), -90); R.block('NK_ARMCH', (v.x0 + 4200, v.y0 + 2200), 90)
        R.rect(v.x0 + 1900, v.y0 + 1800, v.x0 + 3100, v.y0 + 2600, 'A-FURN')
        table(R, v.x0 + 2500, v.y0 + 5000, 2800, 1000, 3, ends=True)
        st = F('ห้องเก็บของ / อุปกรณ์สระ'); shelves(R, st.x0 + 100, st.y0 + 300, st.x0 + 500, st.y1 - 300, n=4)
        gy = F('ห้องฟิตเนส / โยคะ ริมสระ')
        for i in range(3): R.rect(gy.x0 + 600 + i * 1100, gy.y0 + 3200, gy.x0 + 1400 + i * 1100, gy.y0 + 5000, 'A-FURN')
        R.text((gy.x0 + 1700, gy.y0 + 4100), 'เสื่อโยคะ', 100, 'A-ANNO')
        for i in range(2): R.rect(gy.x1 - 1900, gy.y0 + 1000 + i * 1600, gy.x1 - 300, gy.y0 + 1800 + i * 1600, 'A-EQPM')
        eq = F('ห้องเครื่องสระ / เก็บของ')
        for i in range(2): R.circle((eq.x0 + 900 + i * 1200, eq.y0 + 1200), 450, 'A-EQPM')
        R.text(((eq.x0 + eq.x1) / 2, eq.y0 + 2300), 'ถังกรอง / ปั๊ม', 100, 'A-ANNO')
        mb = F('ห้องน้ำแม่บ้าน'); bath_set(R, mb, ('S', mb.x0 + 1200), ('S', mb.x0 + 2400), ('S', mb.x1 - 800))
        for nm in ('ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2'):
            m = F(nm); blk(R, 'BD_B018_B', m, 'E', (m.y0 + m.y1) / 2); blk(R, 'WR_WD030_A', m, 'S' if nm.endswith('1') else 'N', m.x0 + 1600)
        ga = F('แกลเลอรีริมคอร์ต ชั้น 1'); bench(R, ga.x0 + 4600, ga.y0 + 150, ga.x0 + 6600, ga.y0 + 550)
    if fl == 2:
        s = F('ครัวโชว์ + ไอส์แลนด์')
        counter(R, s.x0 + 100, s.y0 + 100, s.x1 - 100, s.y0 + 700, sink=(s.x0 + 1300, s.y0 + 400), hob=(s.x1 - 1200, s.y0 + 400))
        counter(R, s.x0 + 900, s.y0 + 2000, s.x1 - 900, s.y0 + 3000)
        for xx in (s.x0 + 1300, s.x0 + 2000, s.x0 + 2700): R.circle((xx, s.y0 + 3400), 200, 'A-FURN')
        p = F('Walk-in Pantry & ห้องเย็น')
        shelves(R, p.x0 + 100, p.y0 + 300, p.x0 + 500, p.y1 - 300, n=3); R.rect(p.x1 - 1500, p.y1 - 1200, p.x1 - 200, p.y1 - 150, 'A-EQPM')
        R.text((p.x1 - 850, p.y1 - 700), 'ห้องเย็น', 100, 'A-ANNO')
        d = F('ห้องรับประทานอาหาร'); table(R, (d.x0 + d.x1) / 2, (d.y0 + d.y1) / 2 - 300, 1100, 3600, 5, ends=True)
        lv = F('ห้องนั่งเล่น')
        cx, cy = (lv.x0 + lv.x1) / 2 + 1500, (lv.y0 + lv.y1) / 2 - 200
        R.block('NK_SOFA3', (cx, cy - 1500), 0); R.block('NK_SOFA3', (cx, cy + 1500), 180)
        R.block('NK_ARMCH', (cx - 1900, cy), -90); R.block('NK_ARMCH', (cx + 1900, cy), 90)
        R.rect(cx - 650, cy - 450, cx + 650, cy + 450, 'A-FURN')
        pw = F('ห้องน้ำแขก (Powder)'); bath_set(R, pw, ('W', pw.y0 + 700), ('W', pw.y0 + 2200))
        o = F('ห้องทำงาน & ห้องสมุด')
        R.block('FW_FW050_A', ((o.x0 + o.x1) / 2, o.y0 + 2200), 0)
        shelves(R, o.x1 - 500, o.y0 + 1500, o.x1 - 100, o.y1 - 300, n=6)
        table(R, (o.x0 + o.x1) / 2 - 200, o.y1 - 1500, 1600, 800, 2, ends=False)
        b2 = F('ห้องนอน Junior Suite 2'); blk(R, 'BD_B003_B', b2, 'E', (b2.y0 + b2.y1) / 2 + 300)
        c2 = F('ตู้เสื้อผ้า Junior Suite 2'); wardrobe_run(R, c2, 'W', c2.y0, c2.y1)
        t2 = F('ห้องน้ำ Junior Suite 2'); bath_set(R, t2, ('W', t2.y1 - 600), ('N', t2.x1 - 650))
        b3 = F('ห้องนอน Junior Suite 3'); blk(R, 'BD_B003_B', b3, 'E', (b3.y0 + b3.y1) / 2 + 400)
        c3 = F('ตู้เสื้อผ้า Junior Suite 3'); wardrobe_run(R, c3, 'S', c3.x0, c3.x1)
        t3 = F('ห้องน้ำ Junior Suite 3'); bath_set(R, t3, ('S', t3.x0 + 600), ('W', t3.y0 + 1300))
        w = F('ห้องไวน์ / ซิการ์'); shelves(R, w.x0 + 100, w.y0 + 300, w.x0 + 500, w.y1 - 300, n=6); shelves(R, w.x1 - 500, w.y0 + 300, w.x1 - 100, w.y1 - 300, n=6)
        R.block('NK_ARMCH', ((w.x0 + w.x1) / 2, w.y1 - 1300), 180)
        s2 = F('ห้องเก็บของชั้น 2'); shelves(R, s2.x0 + 100, s2.y0 + 300, s2.x1 - 100, s2.y0 + 700, n=2)
    if fl == 3:
        m = F('ห้องนอน Master Suite')
        blk(R, 'BD_B005_B', m, 'W', (m.y0 + m.y1) / 2)
        R.block('NK_SOFA2', (m.x1 - 1200, m.y0 + 2500), -90); R.rect(m.x1 - 2700, m.y0 + 2000, m.x1 - 2000, m.y0 + 3000, 'A-FURN')
        w = F('Walk-in Dressing (His & Hers)')
        wardrobe_run(R, w, 'S', w.x0 + 200, w.x1 - 200)
        box(R, (w.x0 + w.x1) / 2 - 900, w.y0 + 2700, (w.x0 + w.x1) / 2 + 900, w.y0 + 3600)
        b = F('ห้องน้ำ Spa + Jacuzzi')
        blk(R, 'SN_SN064_A', b, 'S', b.x0 + 2000); blk(R, 'SN_SN042_A', b, 'E', b.y0 + 3800)
        blk(R, 'SN_SN001_A', b, 'N', b.x1 - 800); blk(R, 'SN_SN018_A', b, 'W', b.y0 + 4300); blk(R, 'SN_SN018_A', b, 'W', b.y0 + 5300)
        lo = F('ลอจเจียตะวันออก (ใต้ลาน BBQ)')
        lounger(R, lo.x0 + 1500, lo.y0 + 2800, 0); lounger(R, lo.x0 + 2600, lo.y0 + 2800, 0); plant(R, lo.x1 - 2300, lo.y1 - 900, 450)
        s3 = F('ห้องเก็บของชั้น 3'); shelves(R, s3.x0 + 100, s3.y0 + 300, s3.x1 - 100, s3.y0 + 700, n=2)
    if fl == 4:
        t = F('ระเบียง Master (ในร่ม)')
        lounger(R, t.x0 + 1600, t.y0 + 1500, 90); plant(R, t.x1 - 1000, t.y0 + 1400, 450)
        R.rect(t.x0 + 3000, t.y0 + 500, t.x0 + 5000, t.y0 + 2500, 'A-EQPM'); R.text((t.x0 + 4000, t.y0 + 1500), 'อ่างแช่', 100, 'A-ANNO')
        c = F('Master Walk-in Closet ชั้น 4')
        wardrobe_run(R, c, 'W', c.y0 + 200, c.y1 - 200); wardrobe_run(R, c, 'N', c.x0 + 1200, c.x1 - 400)
        box(R, (c.x0 + c.x1) / 2 - 700, (c.y0 + c.y1) / 2 - 400, (c.x0 + c.x1) / 2 + 900, (c.y0 + c.y1) / 2 + 400)
        lg = F('ห้องนั่งเล่นครอบครัว')
        cx, cy = (lg.x0 + lg.x1) / 2, (lg.y0 + lg.y1) / 2 - 300
        R.block('NK_SOFA3', (cx, cy - 1300), 0); R.block('NK_ARMCH', (cx - 1700, cy + 200), -90); R.block('NK_ARMCH', (cx + 1700, cy + 200), 90)
        R.rect(cx - 600, cy - 300, cx + 600, cy + 500, 'A-FURN')
        wc = F('ห้องน้ำชั้น 4'); bath_set(R, wc, ('W', wc.y0 + 700), ('W', wc.y0 + 2200), ('S', wc.x1 - 600))
        th = F('ห้องโฮมเธียเตอร์')
        R.rect(th.x0 + 600, th.y1 - 300, th.x1 - 600, th.y1 - 150, 'A-EQPM'); R.text(((th.x0 + th.x1) / 2, th.y1 - 700), 'จอ 150"', 150, 'A-ANNO')
        for yy in (th.y0 + 3800, th.y0 + 1900): R.block('NK_SOFA3', ((th.x0 + th.x1) / 2, yy), 0)
        q = F('ลาน BBQ บนหลังคา (pergola)')
        counter(R, q.x1 - 2200, q.y0 + 600, q.x1 - 1600, q.y0 + 3600, hob=(q.x1 - 1900, q.y0 + 1500))
        R.text((q.x1 - 2500, q.y0 + 2100), 'BBQ', 140, 'A-ANNO', rot=90)
        table(R, q.x0 + 2300, q.y0 + 3800, 1000, 2600, 3, ends=True)
