# -*- coding: utf-8 -*-
"""Site plan (1:200) and roof plan (1:100)."""
import math
from shapely.geometry import box as sbox
from shapely.ops import unary_union
from cad7 import Rec
from frame7 import *
from plan7 import FLOORS, COURTS, find
from model7 import build, TREES, INFO_PV
from proj7 import project_top
from draw7 import north_arrow, grid, PLAN_VIEW, columns, COL
from furn7 import car, plant, lounger

def tree_plan(R, x, y, r):
    pts = []
    for i in range(37):
        a = 2 * math.pi * i / 36
        rr = r * (1 + 0.07 * math.sin(9 * a))
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    R.fill(pts, 'A-AREA', color='#b7cf9d', alpha=0.55, z=2)
    R.pline(pts, 'L-PLNT')
    R.circle((x, y), 120, 'L-PLNT')
    for k in range(8):
        a = math.radians(k * 45)
        R.line((x + 150 * math.cos(a), y + 150 * math.sin(a)), (x + r * .55 * math.cos(a), y + r * .55 * math.sin(a)), 'L-PLNT', lw=0.08)

def roof_marks(R, labels=True):
    """spiral roof gardens + exterior helix stairs (all four) + courtyard"""
    from draw7 import helix_draw
    for nm, (x0, y0, x1, y1), z0, z1, d in HELIX:
        R.rect(x0, y0, x1, y1, 'A-STAIR', lw=0.25)
        n = 20
        for i in range(1, n):
            y = y0 + i * TREAD if d == 'N' else y1 - i * TREAD
            R.line((x0, y), (x1, y), 'A-STAIR', lw=0.08)
        xm = (x0 + x1) / 2
        a_, b_ = (y0 + 200, y1 - 300) if d == 'N' else (y1 - 200, y0 + 300)
        R.line((xm, a_), (xm, b_), 'A-ANNO', lw=0.25)
        sg = 1 if d == 'N' else -1
        R.pline([(xm - 160, b_ - sg * 280), (xm, b_), (xm + 160, b_ - sg * 280)], 'A-ANNO', lw=0.25)
        if labels:
            R.text((x1 + 150, (y0 + y1) / 2), '%s  %+.2f -> %+.2f' % (nm, z0 / 1000, z1 / 1000), 170, 'A-ANNO', ha='left')
    x0, y0, x1, y1 = COURT
    R.rect(x0, y0, x1, y1, 'A-HIDD', ls='--', lw=0.2)
    if labels:
        R.text(((x0 + x1) / 2 + 1800, (y0 + y1) / 2 + 600), 'คอร์ตกลาง (เปิดฟ้า) +0.45\nสระสะท้อนเงา + ต้นไม้', 200, 'A-TEXT')

SKIP_TOP = ('ground', 'road', 'column', 'wall', 'glass', 'door', 'band', 'rail', 'slab', 'plinth', 'opening', 'hang', 'trough', 'greenwall', 'helix', 'vault')

def site_plan():
    BX, ROOFS = build()
    R = Rec()
    R.frect(-3000, LOT_D, LOT_W + 3000, LOT_D + ROAD_W, 'A-AREA', color='#d6d6d6', z=0)
    R.line((-3000, LOT_D + ROAD_W / 2), (LOT_W + 3000, LOT_D + ROAD_W / 2), 'C-ROAD', ls=(0, (10, 6)))
    R.line((-3000, LOT_D + ROAD_W), (LOT_W + 3000, LOT_D + ROAD_W), 'C-ROAD')
    R.text((LOT_W / 2, LOT_D + ROAD_W / 2 + 900), 'ถนนสาธารณะ (สมมติกว้าง 8.00 ม. - ต้องยืนยัน)', 330, 'C-ROAD', bold=True)
    R.frect(0, 0, LOT_W, LOT_D, 'A-AREA', color='#e9f0df', z=0)
    T = project_top(BX, cats_skip=SKIP_TOP)
    R.extend(T)
    roof_marks(R, labels=False)
    R.pline([(0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D), (0, 0)], 'C-PROP', lw=0.5, ls=(0, (16, 4, 3, 4)))
    for (x, y) in ((0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D)):
        R.circle((x, y), 250, 'C-PROP')
    R.text((LOT_W / 2, -1600), 'แนวเขตที่ดิน 30.00 x 30.00 ม. = 900 ตร.ม. (225 ตร.ว.)', 320, 'C-PROP', bold=True)
    R.dim((0, -2800), (LOT_W, -2800), 0, h=300)
    R.dim((-2800, 0), (-2800, LOT_D), 0, h=300)
    R.pline([(3000, 3000), (LOT_W - 3000, 3000), (LOT_W - 3000, LOT_D - 3000), (3000, LOT_D - 3000), (3000, 3000)], 'A-ANNO', ls=(0, (6, 6)), lw=0.13)
    R.text((LOT_W - 3200, 3300), 'แนวร่นช่องเปิด/ระเบียง 3.00 ม. (ความสูงถึงยอดผนัง 12.95 > 9 ม.)', 200, 'A-ANNO', ha='right', va='bottom')
    for (a, b) in [((0, 10000), (BLK[0], 10000)), ((BLK[2], 15000), (LOT_W, 15000)), ((21000, 0), (21000, BLK[1])), ((23500, GARAGE[3]), (23500, LOT_D))]:
        R.dim(a, b, 0, h=240)
    L = [((16200, 27500), 'ทางรถเข้า - โรงจอดรถ 4 คัน'), ((7000, 27500), 'ทางเดินเข้า\nโถงต้อนรับ'),
         ((13000, 2250), 'สระว่ายน้ำ 14.00 x 2.70 ม.'), ((1600, 23000), 'เครื่อง\nปั่นไฟ'), ((28400, 21000), 'ถัง\nบำบัด'), ((28400, 11000), 'CDU\nแอร์'),
         ((1800, 16500), 'ถังน้ำฝน\nใต้ดิน'), ((15000, 8600), 'สวนดาดฟ้า +13.25 (แผงโซลาร์ 1 แถว)'), ((7000, 15500), 'สวนหลังคา W\n+3.65'),
         ((14000, 22000), 'สวนหลังคา N +6.85'), ((22200, 14000), 'ลาน BBQ\n+10.05')]
    for p, t in L:
        R.text(p, t, 230, 'A-TEXT')
    for rr in (GEN_PAD, SEPTIC, AC_PAD, RAIN_TANK):
        R.rect(*rr, 'A-ANNO', ls='--')
    for (x, y, r, h) in TREES:
        tree_plan(R, x, y, r)
    R.line((DRIVE[0], LOT_D), (DRIVE[2], LOT_D), 'A-DOOR', lw=0.5)
    R.text(((DRIVE[0] + DRIVE[2]) / 2, LOT_D - 450), 'ประตูรั้วบานเลื่อน %.2f ม.' % ((DRIVE[2] - DRIVE[0]) / 1000), 190, 'A-ANNO', va='top')
    R.text((-1400, LOT_D + 500), '±0.00', 200, 'A-ANNO')
    north_arrow(R, (LOT_W + 2600, LOT_D - 2500), 1000)
    return R

def roof_plan():
    BX, ROOFS = build()
    R = project_top(BX, cats_skip=SKIP_TOP + ('fence', 'pool', 'deck', 'pavilion', 'paving', 'court'),
                    clip=(PLAN_VIEW[0], PLAN_VIEW[1], PLAN_VIEW[2], PLAN_VIEW[3]))
    roof_marks(R)
    TX = [((15000, 3900), 'แผงโซลาร์ %d แผง (~%.1f kWp) บนดาดฟ้า' % (INFO_PV['n'], INFO_PV['n'] * 0.55)),
          ((15000, 8700), 'สวนดาดฟ้า +13.25 (ปลายบันไดนอก H4) ราวกระจก 1.10 ม.'),
          ((7600, 17900), 'สวนหลังคา W +3.65\n(หลังคาปีกตะวันตก)'), ((14000, 22300), 'สวนหลังคา N +6.85 (หลังคาปีกเหนือ / เหนือเพดานโค้งอิฐ)'),
          ((22200, 15600), 'ลาน BBQ +10.05\n(pergola ไม้)')]
    for p, t in TX:
        R.text(p, t, 200, 'A-TEXT')
    for (x, y) in ((XA + 300, YA + 300), (XD - 300, YA + 300), (XA + 300, YD - 300), (XA + 300, YE - 300), (XD - 300, YE - 300), (XD - 300, YC + 300)):
        R.circle((x, y), 150, 'A-ANNO'); R.text((x + 250, y + 50), 'RD', 150, 'A-ANNO', ha='left')
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 2200), 800)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad7 import draw_mpl, scaled_axes
    for nm, fn, sc in (('site', site_plan, 200), ('roof', roof_plan, 100)):
        R = fn()
        if nm == 'roof': grid(R, PLAN_VIEW)
        x0, y0, x1, y1 = R.bbox()
        V = (x0 - 500, y0 - 500, x1 + 500, y1 + 500)
        fig = plt.figure(figsize=((V[2] - V[0]) / sc / 25.4 + .2, (V[3] - V[1]) / sc / 25.4 + .2))
        ax = scaled_axes(fig, 2, 2, V, sc)
        draw_mpl(ax, R, sc)
        fig.savefig('prev_%s.png' % nm, dpi=170 if nm == 'site' else 110); plt.close(fig)
        print(nm, V)
