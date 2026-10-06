# -*- coding: utf-8 -*-
"""Furniture & fittings: LOD400 blocks (NACK HOUSE library) + simple parametric items."""
import math
from plan3 import find

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

def furnish(R, fl):
    F = lambda n: find(n, fl)
    if fl == 1:
        g = F('โรงจอดรถ 4 คัน')
        for i in range(4):
            car(R, g.x0 + 1425 + i * 2850, g.y1 - 600 - 2450, 0, L=4900, W=1900)
            R.line((g.x0 + 2850 * (i + 1), g.y1 - 200), (g.x0 + 2850 * (i + 1), g.y1 - 1500), 'A-ANNO', lw=0.13) if i < 3 else None
        R.rect(g.x0 + 2850 * 3 + 1100, g.y0 + 150, g.x0 + 2850 * 3 + 1600, g.y0 + 400, 'A-EQPM')
        R.text((g.x0 + 2850 * 3 + 1350, g.y0 + 650), 'EV', 150, 'A-ANNO')
        f = F('โถงต้อนรับสูง 2 ชั้น')
        shelves(R, f.x0 + 120, f.y0 + 2200, f.x0 + 720, f.y1 - 300, n=3)
        table(R, (f.x0 + f.x1) / 2 + 500, (f.y0 + f.y1) / 2 + 300, 1200, 0, 0, round_=True)
        plant(R, f.x1 - 700, f.y1 - 700, 400)
        p = F('มุขรถเทียบ (Porte-cochère)')
        car(R, (p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2 + 200, 0, dashed=True)
        pw = F('ห้องน้ำแขก (Powder)')
        blk(R, 'SN_SN001_A', pw, 'N', pw.x0 + 700); blk(R, 'SN_SN018_A', pw, 'E', pw.y0 + 700)
        b = F('ห้องเก็บจักรยาน/อุปกรณ์สวน')
        for i in range(3): R.rect(b.x0 + 300 + i * 650, b.y1 - 2000, b.x0 + 400 + i * 650, b.y1 - 200, 'A-EQPM')
        shelves(R, b.x1 - 520, b.y0 + 200, b.x1 - 100, b.y1 - 200, n=3)
        w = F('ห้องไวน์ / ซิการ์')
        shelves(R, w.x0 + 100, w.y0 + 1200, w.x0 + 500, w.y1 - 200, n=8)
        shelves(R, w.x1 - 500, w.y0 + 1200, w.x1 - 100, w.y1 - 200, n=8)
        R.block('NK_ARMCH', ((w.x0 + w.x1) / 2, w.y1 - 1500), 180)
        t = F('ห้องโฮมเธียเตอร์')
        R.rect(t.x1 - 250, t.y0 + 900, t.x1 - 100, t.y1 - 900, 'A-EQPM')       # screen east wall
        R.text((t.x1 - 500, (t.y0 + t.y1) / 2), 'จอ 150"', 150, 'A-ANNO', rot=90)
        for k, x in enumerate((t.x0 + 1500, t.x0 + 2900)):
            R.block('NK_SOFA3', (x, (t.y0 + t.y1) / 2), -90)
        R.rect(t.x0 + 3500, (t.y0 + t.y1) / 2 - 400, t.x0 + 4000, (t.y0 + t.y1) / 2 + 400, 'A-FURN')
        # ---- service wing
        for nm in ('ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2'):
            m = F(nm)
            R.block('BD_B018_B', (m.x1 - 80, m.y0 + 1100), 90)
            blk(R, 'WR_WD030_A', m, 'N', m.x0 + 2600) if nm.endswith('1') else blk(R, 'WR_WD030_A', m, 'S', m.x0 + 2600)
        l = F('ห้องซักรีด')
        for i in range(4):
            R.rect(l.x0 + 1100 + i * 700, l.y1 - 720, l.x0 + 1700 + i * 700, l.y1 - 120, 'A-EQPM'); R.circle((l.x0 + 1400 + i * 700, l.y1 - 420), 220, 'A-EQPM')
        counter(R, l.x0 + 4000, l.y1 - 720, l.x1 - 300, l.y1 - 120, sink=(l.x0 + 4500, l.y1 - 420))
        box(R, l.x0 + 1500, l.y0 + 300, l.x0 + 3900, l.y0 + 900, 'A-FURN')
        R.text((l.x0 + 2700, l.y0 + 600), 'โต๊ะพับผ้า', 120, 'A-ANNO')
        mb = F('ห้องน้ำแม่บ้าน')
        blk(R, 'SN_SN001_A', mb, 'E', mb.y0 + 600); blk(R, 'SN_SN018_A', mb, 'E', mb.y0 + 1500); blk(R, 'SN_SN039_A', mb, 'N', mb.x0 + 1500)
        me = F('ห้อง MEP / ไฟฟ้า')
        for i in range(3): R.rect(me.x0 + 300 + i * 900, me.y1 - 500, me.x0 + 1100 + i * 900, me.y1 - 150, 'A-EQPM')
        R.text(((me.x0 + me.x1) / 2, me.y1 - 800), 'MDB / UPS / BMS', 120, 'A-ANNO')
        R.rect(me.x1 - 1400, me.y0 + 300, me.x1 - 200, me.y0 + 1500, 'A-EQPM'); R.text((me.x1 - 800, me.y0 + 900), 'ปั๊มน้ำ', 110, 'A-ANNO')
        # ---- kitchens
        k = F('ครัวไทย (ครัวหนัก)')
        counter(R, k.x0 + 100, k.y0 + 100, k.x1 - 100, k.y0 + 700, hob=((k.x0 + k.x1) / 2, k.y0 + 400))
        counter(R, k.x1 - 700, k.y0 + 700, k.x1 - 100, k.y0 + 4200, sink=(k.x1 - 400, k.y0 + 2600))
        R.rect(k.x0 + 200, k.y0 + 100, k.x1 - 200, k.y0 + 900, 'A-HIDD', ls='--')     # hood
        table(R, (k.x0 + k.x1) / 2 - 200, k.y1 - 1700, 800, 1200, 2, ends=False)
        p = F('Walk-in Pantry/ห้องเย็น')
        shelves(R, p.x0 + 100, p.y0 + 1300, p.x0 + 550, p.y1 - 200, n=6); shelves(R, p.x1 - 550, p.y0 + 200, p.x1 - 100, p.y1 - 1600, n=6)
        R.rect(p.x0 + 150, p.y0 + 150, p.x1 - 150, p.y0 + 1100, 'A-EQPM'); R.text(((p.x0 + p.x1) / 2, p.y0 + 620), 'ห้องเย็น', 110, 'A-ANNO')
        s = F('ครัวโชว์ + ไอส์แลนด์')
        counter(R, s.x0 + 100, s.y0 + 100, s.x1 - 100, s.y0 + 700, sink=((s.x0 + s.x1) / 2 + 600, s.y0 + 400))
        counter(R, s.x0 + 100, s.y0 + 3000, s.x0 + 700, s.y1 - 300, hob=(s.x0 + 400, s.y0 + 4700))
        R.rect(s.x0 + 100, s.y0 + 5600, s.x0 + 700, s.y1 - 300, 'A-EQPM'); R.text((s.x0 + 400, s.y0 + 6300), 'ตู้เย็น', 100, 'A-ANNO', rot=90)
        counter(R, s.x0 + 1700, s.y0 + 2300, s.x0 + 2800, s.y0 + 5300)
        for yy in (s.y0 + 2800, s.y0 + 3800, s.y0 + 4800): R.circle((s.x0 + 3150, yy), 220, 'A-FURN')
        d = F('ห้องรับประทานอาหาร')
        table(R, (d.x0 + d.x1) / 2, (d.y0 + d.y1) / 2 + 200, 1100, 3600, 5, ends=True)
        shelves(R, d.x0 + 300, d.y0 + 100, d.x0 + 1800, d.y0 + 550, n=2)
        lv = F('ห้องนั่งเล่นสูง 2 ชั้น')
        cx, cy = (lv.x0 + lv.x1) / 2, (lv.y0 + lv.y1) / 2 + 300
        R.block('NK_SOFA3', (cx, cy - 1500), 0); R.block('NK_SOFA3', (cx, cy + 1500), 180)
        R.block('NK_ARMCH', (cx - 1800, cy), -90); R.block('NK_ARMCH', (cx + 1800, cy), 90)
        R.rect(cx - 650, cy - 450, cx + 650, cy + 450, 'A-FURN')
        R.rect(cx - 1700, cy - 1700, cx + 1700, cy + 1700, 'A-HIDD', ls='--')       # rug
        plant(R, lv.x0 + 700, lv.y0 + 700)
        v = F('ระเบียงบาร์บีคิว')
        counter(R, v.x1 - 700, v.y0 + 300, v.x1 - 100, v.y0 + 3600, hob=(v.x1 - 400, v.y0 + 1500))
        R.text((v.x1 - 1100, v.y0 + 1900), 'BBQ', 140, 'A-ANNO', rot=90)
        table(R, v.x0 + 2600, v.y0 + 2200, 2400, 1000, 3, ends=True)
        lounger(R, v.x0 + 5200, (v.y0 + v.y1) / 2, 0) if False else None
        ps = F('ห้องอาบน้ำริมสระ')
        blk(R, 'SN_SN001_A', ps, 'E', ps.y0 + 600); blk(R, 'SN_SN039_A', ps, 'N', ps.x0 + 800, 80)
        # guest suite (elderly)
        gb = F('ห้องนอนแขก/ผู้สูงอายุ')
        blk(R, 'BD_B003_B', gb, 'N', (gb.x0 + gb.x1) / 2 + 200)
        R.rect(gb.x0 + 300, gb.y0 + 300, gb.x0 + 1600, gb.y0 + 900, 'A-FURN')
        gt = F('ห้องน้ำห้องแขก')
        blk(R, 'SN_SN001_A', gt, 'E', gt.y0 + 700); blk(R, 'SN_SN018_A', gt, 'N', gt.x0 + 1900); blk(R, 'SN_SN043_A', gt, 'W', gt.y0 + 1200)
        gc = F('ตู้เสื้อผ้าห้องแขก'); wardrobe_run(R, gc, 'N', gc.x0, gc.x1)
        # trunk / gallery bench
        tr = F('ทางเดินลำต้น (Trunk)')
        R.rect(tr.x0 + 150, tr.y0 + 4200, tr.x0 + 600, tr.y0 + 6600, 'A-FURN')
    if fl == 2:
        for sfx in ('2', '3'):
            b = F('ห้องนอน Junior Suite ' + sfx)
            blk(R, 'BD_B003_B', b, 'N', (b.x0 + b.x1) / 2 + (-100 if sfx == '2' else 100))
            R.block('FW_FW001_A', (b.x0 + 900 if sfx == '2' else b.x1 - 900, b.y0 + 1500), 90 if sfx == '2' else -90) if False else None
            R.block('NK_ARMCH', (b.x0 + 900 if sfx == '2' else b.x1 - 900, b.y0 + 1200), 0)
            t = F('ห้องน้ำ Junior Suite ' + sfx)
            blk(R, 'SN_SN001_A', t, 'N', t.x0 + 600); blk(R, 'SN_SN060_A', t, 'N', t.x0 + 1700) if t.w > 2700 else blk(R, 'SN_SN018_A', t, 'N', t.x0 + 1700)
            blk(R, 'SN_SN030_A', t, 'S', (t.x0 + t.x1) / 2)
            c = F('ตู้เสื้อผ้า Junior Suite ' + sfx); wardrobe_run(R, c, 'N', c.x0, c.x1)
        lg = F('ห้องนั่งเล่นครอบครัว')
        cx, cy = (lg.x0 + lg.x1) / 2, (lg.y0 + lg.y1) / 2 + 600
        R.block('NK_SOFA3', (cx, cy - 1300), 0); R.block('NK_ARMCH', (cx - 1700, cy), -90); R.block('NK_ARMCH', (cx + 1700, cy), 90)
        R.block('NK_TVCAB', (cx, lg.y1 - 120), 180)
        R.rect(cx - 600, cy - 400, cx + 600, cy + 400, 'A-FURN')
        shelves(R, lg.x1 - 500, lg.y0 + 300, lg.x1 - 100, lg.y0 + 3300, n=4)
        g = F('Upper Gallery (โถงชั้น 2)')
        R.block('NK_DAYBED', (g.x0 + 1600, g.y0 + 100), 0)
    if fl == 3:
        o = F('ห้องทำงาน & ห้องสมุด')
        R.block('FW_FW050_A', ((o.x0 + o.x1) / 2 + 300, o.y0 + 1700), 0)
        shelves(R, o.x0 + 100, o.y0 + 1200, o.x0 + 500, o.y1 - 300, n=6)
        table(R, (o.x0 + o.x1) / 2 + 300, o.y1 - 1500, 1800, 900, 2, ends=False)
        w = F('Walk-in Dressing (His & Hers)')
        wardrobe_run(R, w, 'S', w.x0 + 200, w.x1 - 200); wardrobe_run(R, w, 'N', w.x0 + 200, w.x1 - 1300)
        box(R, (w.x0 + w.x1) / 2 - 900, (w.y0 + w.y1) / 2 - 450, (w.x0 + w.x1) / 2 + 900, (w.y0 + w.y1) / 2 + 450)
        R.text(((w.x0 + w.x1) / 2, (w.y0 + w.y1) / 2), 'ไอส์แลนด์', 110, 'A-ANNO')
        b = F('ห้องน้ำ Spa + Jacuzzi')
        blk(R, 'SN_SN034_A', b, 'S', b.x0 + 1100)
        blk(R, 'SN_SN042_A', b, 'S', b.x1 - 950)
        blk(R, 'SN_SN064_A', b, 'N', b.x0 + 2600)
        blk(R, 'SN_SN001_A', b, 'W', b.y1 - 900)
        R.rect(b.x0 + 60, b.y1 - 1500, b.x0 + 1100, b.y1 - 1450, 'A-WALL-INT')
        m = F('ห้องนอน Master Suite')
        blk(R, 'BD_B005_B', m, 'W', (m.y0 + m.y1) / 2 + 700)
        R.block('NK_SOFA2', ((m.x0 + m.x1) / 2 + 1500, m.y0 + 300), 0)
        R.block('NK_TVCAB', (m.x1 - 120, (m.y0 + m.y1) / 2 + 1400), 90)
        t = F('ระเบียง Master (หลังคาคลุม)')
        lounger(R, t.x0 + 1200, t.y0 + 2000, 0); lounger(R, t.x0 + 2600, t.y0 + 2000, 0)
        for yy in (t.y0 + 4300, t.y0 + 5600): plant(R, t.x1 - 700, yy, 450)
        table(R, t.x0 + 1700, t.y1 - 1500, 800, 0, 2, round_=True)
