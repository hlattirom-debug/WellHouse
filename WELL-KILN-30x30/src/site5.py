# -*- coding: utf-8 -*-
"""Site plan (1:200) and roof plan (1:100)."""
import math
from shapely.geometry import box as sbox
from shapely.ops import unary_union
from cad5 import Rec
from frame5 import *
from plan5 import FLOORS, COURTS, find
from model5 import build, TREES
from proj5 import project_top
from draw5 import north_arrow, grid, PLAN_VIEW, columns, COL
from furn5 import car, plant, lounger

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

def cyl_top(R):
    """brick dome (top view) + tower chimney + vault"""
    from shapely.geometry import Point
    c = Point(*DOME_C).buffer(DOME_R, 96)
    R.fill(list(c.exterior.coords), 'A-AREA', color='#a9573a', z=3)
    R.pline(list(c.exterior.coords), 'A-ROOF', lw=0.35)
    for rr in (DOME_R * 0.8, DOME_R * 0.6, DOME_R * 0.4): R.circle(DOME_C, rr, 'A-ROOF', lw=0.08)
    R.circle(DOME_C, 400, 'A-GLAZ'); R.fill(list(Point(*DOME_C).buffer(400, 24).exterior.coords), 'A-AREA', color='#bcd6e6', z=4)
    x0, y0, x1, y1 = VAULT
    R.frect(x0, y0, x1, y1, 'A-AREA', color='#c4703f', z=3)
    R.rect(x0, y0, x1, y1, 'A-ROOF', lw=0.35)
    for k in range(1, 9):
        x = x0 + (x1 - x0) * k / 9
        R.line((x, y0), (x, y1), 'A-ROOF', lw=0.06)
    R.line(((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), 'A-ROOF', lw=0.25, ls='--')
    tx0, ty0, tx1, ty1 = TOWER
    R.frect(tx0, ty0, tx1, ty1, 'A-AREA', color='#a9573a', z=3); R.rect(tx0, ty0, tx1, ty1, 'A-ROOF', lw=0.35)
    R.frect(tx0 + 200, ty0 + 200, tx1 - 200, ty1 - 200, 'A-AREA', color='#bcd6e6', z=4); R.rect(tx0 + 200, ty0 + 200, tx1 - 200, ty1 - 200, 'A-GLAZ')

SKIP_TOP = ('ground', 'road', 'column', 'wall', 'glass', 'door', 'band', 'rail', 'slab', 'plinth', 'opening', 'domeslice', 'vaultslice', 'chimney')

def site_plan():
    BX, ROOFS = build()
    R = Rec()
    R.frect(-3000, LOT_D, LOT_W + 3000, LOT_D + ROAD_W, 'A-AREA', color='#d6d6d6', z=0)
    R.line((-3000, LOT_D + ROAD_W / 2), (LOT_W + 3000, LOT_D + ROAD_W / 2), 'C-ROAD', ls=(0, (10, 6)))
    R.line((-3000, LOT_D + ROAD_W), (LOT_W + 3000, LOT_D + ROAD_W), 'C-ROAD')
    R.text((LOT_W / 2, LOT_D + ROAD_W / 2 + 900), 'ถนนสาธารณะ (สมมติกว้าง 8.00 ม. - ต้องยืนยัน)', 330, 'C-ROAD', bold=True)
    R.frect(0, 0, LOT_W, LOT_D, 'A-AREA', color='#e9f0df', z=0)
    T = project_top(BX, cats_skip=SKIP_TOP + ('lattice',))
    R.extend(T)
    cyl_top(R)
    R.pline([(0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D), (0, 0)], 'C-PROP', lw=0.5, ls=(0, (16, 4, 3, 4)))
    for (x, y) in ((0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D)):
        R.circle((x, y), 250, 'C-PROP')
    R.text((LOT_W / 2, -1600), 'แนวเขตที่ดิน 30.00 x 30.00 ม. = 900 ตร.ม. (225 ตร.ว.)', 320, 'C-PROP', bold=True)
    R.dim((0, -2800), (LOT_W, -2800), 0, h=300)
    R.dim((-2800, 0), (-2800, LOT_D), 0, h=300)
    R.pline([(3000, 3000), (LOT_W - 3000, 3000), (LOT_W - 3000, LOT_D - 3000), (3000, LOT_D - 3000), (3000, 3000)], 'A-ANNO', ls=(0, (6, 6)), lw=0.13)
    R.text((LOT_W - 3200, 3300), 'แนวร่นช่องเปิด/ระเบียง 3.00 ม. (อาคารสูง > 9 ม.)', 200, 'A-ANNO', ha='right', va='bottom')
    for (a, b) in [((0, 12000), (BLK[0], 12000)), ((BLK[2], 15000), (LOT_W, 15000)), ((11000, 0), (11000, BLK[1])), ((5000, GARAGE[3]), (5000, LOT_D)),
                   ((21000, DOME_SQ[3]), (21000, LOT_D)), ((24000, 0), (24000, FSTAIR[1]))]:
        R.dim(a, b, 0, h=240)
    L = [((10000, 28300), 'ทางรถเข้า - โรงจอดรถ 4 คัน'), ((24600, 27600), 'ทางเดินเข้า\nสู่โดมอิฐ'),
         ((11500, 800), 'สระว่ายน้ำ 14.00 x 3.00 ม.'), ((15000, 6300), 'ลานใต้ถุน / ศาลาริมสระ (ใต้ชั้น 2)'),
         ((1700, 15000), 'ลาน\nบริการ'), ((1600, 23000), 'เครื่อง\nปั่นไฟ'), ((1600, 19650), 'ถังบำบัด'), ((1600, 11000), 'CDU\nแอร์'),
         ((28050, 21750), 'ถังน้ำฝน\nใต้ดิน'), ((DOME_C[0], DOME_C[1] - 900), 'โดมอิฐ\nยอด +6.25'), ((15100, 17200), 'ปล่องเตาเผา\n+14.85'),
         ((17000, 10400), 'หลังคาโค้ง\n+14.85'), ((6000, 17500), 'หลังคาสวน +7.25'), ((11700, 22000), 'หลังคาสวน\n+7.25'),
         ((22500, 10400), 'หลังคา +14.05\n(แผงโซลาร์)'), ((11900, 10400), 'ระเบียง Master\n(pergola)')]
    for p, t in L:
        R.text(p, t, 230, 'A-TEXT')
    for rr in (GEN_PAD, SEPTIC, AC_PAD, RAIN_TANK):
        R.rect(*rr, 'A-ANNO', ls='--')
    for (x, y, r, h) in TREES:
        tree_plan(R, x, y, r)
    R.line((DRIVE[0], LOT_D), (DRIVE[2], LOT_D), 'A-DOOR', lw=0.5)
    R.text(((DRIVE[0] + DRIVE[2]) / 2, LOT_D - 450), 'ประตูรั้วบานเลื่อน 13.00 ม.', 190, 'A-ANNO', va='top')
    R.text((-1400, LOT_D + 500), '±0.00', 200, 'A-ANNO')
    north_arrow(R, (LOT_W + 2600, LOT_D - 2500), 1000)
    return R

def roof_plan():
    BX, ROOFS = build()
    R = project_top(BX, cats_skip=SKIP_TOP + ('fence', 'pool', 'deck', 'pavilion', 'paving'),
                    clip=(PLAN_VIEW[0], PLAN_VIEW[1], PLAN_VIEW[2], PLAN_VIEW[3]))
    cyl_top(R)
    for rg, z, kind in ROOFS:
        if kind == 'main': continue
        gs = [rg] if rg.geom_type == 'Polygon' else [g for g in getattr(rg, 'geoms', []) if g.geom_type == 'Polygon']
        for g in gs:
            x0, y0, x1, y1 = g.bounds
            yy = y0 + 600
            while yy < y1 - 300:
                xx = x0 + 600 + ((yy // 600) % 2) * 300
                while xx < x1 - 300:
                    if g.contains(sbox(xx - 60, yy - 60, xx + 60, yy + 60)):
                        R.line((xx - 120, yy), (xx, yy + 160), 'L-PLNT', lw=0.08); R.line((xx, yy + 160), (xx + 120, yy), 'L-PLNT', lw=0.08)
                    xx += 900
                yy += 900
    TX = [((6500, 22800), 'หลังคาสวน +3.85\n(เหนือโรงจอดรถ)'), ((11700, 22000), 'หลังคาสวน +7.25\n(เหนือห้องทำงาน)'),
          ((7300, 17300), 'หลังคาสวน +7.25\n(เหนือ Junior Suite 2)'), ((28750, 15500), 'หลังคา\n+14.05\nค.ส.ล.\n+ PU 50\n+ สี SR\n>= 0.75\n+ แผง\nโซลาร์'),
          ((17000, 6900), 'หลังคาโค้ง (ห้องนั่งเล่นครอบครัว)\nกระเบื้องดินเผา บนเปลือก ค.ส.ล. สปริง +13.80 ยอด +14.85'),
          ((11900, 6900), 'ระเบียง Master +10.65\n(เปิดฟ้า pergola)'), ((15100, 14100), 'ปล่องเตาเผา +14.85 (บันได+ลิฟต์) ช่องแสง + เกล็ดระบายอากาศ'),
          ((DOME_C[0] + 3400, DOME_C[1] + 1500), 'โดมอิฐ +6.25\n(ช่องแสง oculus)'), ((24000, 4600), 'บันไดหนีไฟ (เหล็ก เปิดโล่ง)')]
    for p, t in TX:
        R.text(p, t, 200, 'A-TEXT')
    for (x, y) in ((4200, 8200), (25800, 8200), (4200, 14800), (25800, 18800), (9000, 18800), (4200, 25500), (16000, 25500)):
        R.circle((x, y), 150, 'A-ANNO'); R.text((x + 250, y + 50), 'RD', 150, 'A-ANNO', ha='left')
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 2200), 800)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad5 import draw_mpl, scaled_axes
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
