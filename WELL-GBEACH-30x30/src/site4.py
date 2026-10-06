# -*- coding: utf-8 -*-
"""Site plan (1:200) and roof plan (1:100)."""
import math
from shapely.geometry import box as sbox
from shapely.ops import unary_union
from cad4 import Rec
from frame4 import *
from plan4 import FLOORS, COURTS, find
from model4 import build, TREES
from proj4 import project_top
from draw4 import north_arrow, grid, PLAN_VIEW, columns, COL
from furn4 import car, plant, lounger

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
    from shapely.geometry import Point
    c = Point(*CORE_C).buffer(CORE_R, 96); ci = Point(*CORE_C).buffer(CORE_R - 200, 96)
    R.fill(list(c.exterior.coords), 'A-AREA', color='#b8674a', z=3)
    R.pline(list(c.exterior.coords), 'A-ROOF', lw=0.35); R.pline(list(ci.exterior.coords), 'A-ROOF')
    sk = Point(*CORE_C).buffer(1200, 48)
    R.fill(list(sk.exterior.coords), 'A-AREA', color='#bcd6e6', z=4); R.pline(list(sk.exterior.coords), 'A-GLAZ')

def site_plan():
    BX, ROOFS = build()
    R = Rec()
    R.frect(-3000, LOT_D, LOT_W + 3000, LOT_D + ROAD_W, 'A-AREA', color='#d6d6d6', z=0)
    R.line((-3000, LOT_D + ROAD_W / 2), (LOT_W + 3000, LOT_D + ROAD_W / 2), 'C-ROAD', ls=(0, (10, 6)))
    R.line((-3000, LOT_D + ROAD_W), (LOT_W + 3000, LOT_D + ROAD_W), 'C-ROAD')
    R.text((LOT_W / 2, LOT_D + ROAD_W / 2 + 900), 'ถนนสาธารณะ (สมมติกว้าง 8.00 ม. - ต้องยืนยัน)', 330, 'C-ROAD', bold=True)
    R.frect(0, 0, LOT_W, LOT_D, 'A-AREA', color='#e9f0df', z=0)
    T = project_top(BX, cats_skip=('ground', 'road', 'column', 'wall', 'glass', 'door', 'band', 'rail', 'slab', 'plinth', 'opening', 'lattice', 'cylslice'))
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
    for (a, b) in [((0, 23000), (BAR[0], 23000)), ((BAR[2], 23500), (LOT_W, 23500)), ((CORE_SQ[2], 15150), (LOT_W, 15150)),
                   ((9000, 0), (9000, BAR[1])), ((9000, BAR[3]), (9000, LOT_D)), ((FSTAIR[0], 19000), (0, 19000))]:
        R.dim(a, b, 0, h=240)
    L = [((13000, 28300), 'ทางรถเข้า-ลานจอดใต้ Pilotis'), ((21800, 28300), 'ทางเดินเข้า'),
         ((26900, 16800), 'สระว่ายน้ำ\n3.80 x 16.00 ม.'), ((25050, 5350), 'ศาลาริมสระ 35.25 ตร.ม.'),
         ((1500, 13000), 'ลาน\nบริการ'), ((1600, 23000), 'เครื่อง\nปั่นไฟ'), ((1600, 19650), 'ถังบำบัด'), ((1600, 8000), 'CDU\nแอร์'),
         ((22750, 21750), 'ถังน้ำฝน\nใต้ดิน 15 ลบ.ม.'), ((21800, 15150), 'แกน\nทรงกระบอก\n+14.85'), ((13000, 12000), 'หลังคาชั้น 4 +14.05\n(แผงโซลาร์ 24 แผง 13.2 kWp)'),
         ((13000, 23000), 'หลังคาสวน +7.25\n(เหนือชั้น 2)'), ((13350, 6400), 'ระเบียง Master\n(ดาดฟ้า pergola)')]
    for p, t in L:
        R.text(p, t, 230, 'A-TEXT')
    for rr in (GEN_PAD, SEPTIC, AC_PAD, RAIN_TANK):
        R.rect(*rr, 'A-ANNO', ls='--')
    for (x, y, r, h) in TREES:
        tree_plan(R, x, y, r)
    R.line((DRIVE[0], LOT_D), (DRIVE[2], LOT_D), 'A-DOOR', lw=0.5)
    R.text(((DRIVE[0] + DRIVE[2]) / 2, LOT_D - 450), 'ประตูรั้วบานเลื่อน 15.00 ม.', 190, 'A-ANNO', va='top')
    R.text((-1400, LOT_D + 500), '±0.00', 200, 'A-ANNO')
    north_arrow(R, (LOT_W + 2600, LOT_D - 2500), 1000)
    return R

def roof_plan():
    BX, ROOFS = build()
    R = project_top(BX, cats_skip=('ground', 'road', 'fence', 'column', 'wall', 'glass', 'door', 'band', 'rail', 'slab', 'plinth', 'opening', 'pool', 'deck', 'pavilion', 'paving', 'cylslice'),
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
    TX = [((13000, 23300), 'หลังคาสวน (Green roof) +7.25\nเหนือ Junior Suite / ห้องทำงาน\nดินปลูก 150 มม. + แผ่นระบายน้ำ + กันซึม 2 ชั้น'),
          ((13000, 15800), 'หลังคาชั้น 4  +14.05\nค.ส.ล. + PU 50 มม. + สีสะท้อนแสง SR >= 0.75'),
          ((13350, 7200), 'ระเบียง Master +10.65\n(เปิดฟ้า ระแนงไม้ pergola)'),
          ((21800, 19200), 'แกนทรงกระบอก +14.85\n(ผนังอิฐ + ช่องแสงหลังคา)'), ((4250, 18300), 'บันไดหนีไฟ\n(เหล็ก เปิดโล่ง)'),
          ((21100, 8000), 'ระเบียง\nชั้น 3')]
    for p, t in TX:
        R.text(p, t, 210, 'A-TEXT')
    for (x, y) in ((6000, 4500), (20000, 4500), (6000, 18800), (20000, 18800), (6000, 26000), (20000, 26000)):
        R.circle((x, y), 150, 'A-ANNO'); R.text((x + 250, y + 50), 'RD', 150, 'A-ANNO', ha='left')
    def arrow(a, b):
        R.line(a, b, 'A-ANNO', lw=0.13)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        R.pline([(b[0] - 250 * math.cos(ang - .35), b[1] - 250 * math.sin(ang - .35)), b, (b[0] - 250 * math.cos(ang + .35), b[1] - 250 * math.sin(ang + .35))], 'A-ANNO', lw=0.13)
    arrow((10000, 14000), (7000, 14000)); arrow((16000, 14000), (19000, 14000))
    R.text((8500, 14350), 'ลาด 1:100', 150, 'A-ANNO'); R.text((17500, 14350), 'ลาด 1:100', 150, 'A-ANNO')
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 4500), 800)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad4 import draw_mpl, scaled_axes
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
