# -*- coding: utf-8 -*-
"""Site plan (1:200) and roof plan (1:100)."""
import math
from shapely.geometry import box as sbox
from shapely.ops import unary_union
from cad3 import Rec
from frame3 import *
from plan3 import FLOORS, COURTS, find
from model3d import build, TREES
from proj3 import project_top
from draw3 import north_arrow, grid, PLAN_VIEW, columns, COL
from furn3 import car, plant, lounger

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

def site_plan():
    BX, ROOFS = build()
    R = Rec()
    # road
    R.frect(-3000, LOT_D, LOT_W + 3000, LOT_D + ROAD_W, 'A-AREA', color='#d6d6d6', z=0)
    R.line((-3000, LOT_D + ROAD_W / 2), (LOT_W + 3000, LOT_D + ROAD_W / 2), 'C-ROAD', ls=(0, (10, 6)))
    R.line((-3000, LOT_D + ROAD_W), (LOT_W + 3000, LOT_D + ROAD_W), 'C-ROAD')
    R.text((LOT_W / 2, LOT_D + ROAD_W / 2 + 900), 'ถนนสาธารณะ กว้าง 8.00 ม.', 380, 'C-ROAD', bold=True)
    R.frect(0, 0, LOT_W, LOT_D, 'A-AREA', color='#e9f0df', z=0)
    # top view of everything
    T = project_top(BX, cats_skip=('ground', 'road', 'column', 'wall', 'glass', 'door', 'stair', 'band', 'rail', 'slab', 'plinth', 'opening'))
    R.extend(T)
    # lot boundary
    R.pline([(0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D), (0, 0)], 'C-PROP', lw=0.5, ls=(0, (16, 4, 3, 4)))
    for (x, y) in ((0, 0), (LOT_W, 0), (LOT_W, LOT_D), (0, LOT_D)):
        R.circle((x, y), 250, 'C-PROP')
    R.text((LOT_W / 2, -1600), 'แนวเขตที่ดิน 40.00 x 40.00 ม. = 1,600 ตร.ม. (400 ตร.ว.)', 340, 'C-PROP', bold=True)
    R.dim((0, -2800), (LOT_W, -2800), 0, h=330)
    R.dim((-2800, 0), (-2800, LOT_D), 0, h=330)
    # setback lines 3.00 (openings, H >= 9 m)
    R.pline([(3000, 3000), (LOT_W - 3000, 3000), (LOT_W - 3000, LOT_D - 800), (3000, LOT_D - 800), (3000, 3000)], 'A-ANNO', ls=(0, (6, 6)), lw=0.13)
    R.text((LOT_W - 3200, 3300), 'แนวร่นช่องเปิด 3.00 ม. (อาคารสูง > 9 ม.)', 220, 'A-ANNO', ha='right', va='bottom')
    # building dims to boundary
    for (a, b, off) in [((0, Y(20000)), (BLD[0], Y(20000)), 0), ((BLD[2], Y(19000)), (LOT_W, Y(19000)), 0), ((25000, 0), (25000, BLD[1]), 0), ((30500, BLD[3]), (30500, LOT_D), 0)]:
        R.dim(a, b, off, h=260)
    # labels
    L = [((11500, 37000), 'ทางรถเข้า-ลานจอด'), ((20100, 37200), 'ทางเดินเข้า\nมุขรถเทียบ'), ((26600, Y(31400) + 2300), 'ทางลาด 1:12 ยาว 7.20 ม.'),
         ((20000, 4650), 'สระว่ายน้ำเกลือ 16.00 x 4.50 ม.'), ((32250, 4900), 'ศาลาริมสระ\n35.10 ตร.ม.'),
         ((2900, Y(19000)), 'ลาน\nบริการ'), ((2400, Y(25400)), 'เครื่อง\nปั่นไฟ'), ((2200, Y(28200)), 'ถังบำบัด'),
         ((2900, 12200), 'บึงประดิษฐ์\nบำบัดน้ำเทา'), ((37000, Y(20700)), 'VRF\nCDU'), ((20000, 500), 'ร่องซับน้ำ Mangrove bioswale กว้าง 1.00 ม.'),
         ((15100, Y(21000)), 'คอร์ตน้ำ\n(ถังเก็บน้ำฝน\nใต้ดิน 20 ลบ.ม.)'), ((25300, Y(20500)), 'คอร์ตต้นไม้\n(ปอดTermite)')]
    for p, t in L:
        R.text(p, t, 260, 'A-TEXT')
    for (x0, y0, x1, y1), nm in ((GEN_PAD, ''), (SEPTIC, ''), (AC_PAD, ''), (WETLAND, ''), (RAIN_TANK, '')):
        R.rect(x0, y0, x1, y1, 'A-ANNO', ls='--')
    R.rect(*SWALE_S, 'L-WATR', ls='--'); R.rect(*SWALE_E, 'L-WATR', ls='--')
    for (x, y, r, h) in TREES:
        tree_plan(R, x, y, r)
    for i in range(4):
        car(R, 5800 + 1425 + i * 2850, Y(31400) - 600 - 2450, 0)
    # gates
    R.line((DRIVE[0], LOT_D), (DRIVE[2], LOT_D), 'A-DOOR', lw=0.5)
    R.text(((DRIVE[0] + DRIVE[2]) / 2, LOT_D - 500), 'ประตูรั้วบานเลื่อน 11.40 ม.', 200, 'A-ANNO', va='top')
    R.text(((WALK[0] + WALK[2]) / 2, LOT_D - 500), 'ประตูคนเดิน', 200, 'A-ANNO', va='top')
    # roof level tags
    R.text((22000, Y(9600)), 'หลังคา Crown +11.40\n(แผงโซลาร์ 42 แผง 23.1 kWp)', 260, 'A-TEXT', bold=True)
    R.text((11500, Y(27800)), 'หลังคาสวน +4.20\n(เหนือโรงจอดรถ)', 240, 'A-TEXT')
    R.text((31200, Y(28400)), 'หลังคาสวน +4.20', 240, 'A-TEXT')
    R.text((20100, Y(19600)), 'แกนลำต้น\nปล่อง Termite\n+14.00', 220, 'A-TEXT', bold=True)
    R.text((-1400, LOT_D + 500), '±0.00', 200, 'A-ANNO')
    north_arrow(R, (LOT_W + 2600, LOT_D - 2500), 1000)
    return R

def roof_plan():
    BX, ROOFS = build()
    R = project_top(BX, cats_skip=('ground', 'road', 'fence', 'column', 'wall', 'glass', 'door', 'stair', 'band', 'rail', 'slab', 'plinth', 'opening', 'pool', 'deck', 'pavilion', 'paving', 'ramp'),
                    clip=(PLAN_VIEW[0], PLAN_VIEW[1], PLAN_VIEW[2], PLAN_VIEW[3]))
    # green roof hatch symbols
    from model3d import region
    hi = {1: region(2).union(region(3)), 2: region(3), 3: None}
    for rg, z, kind in ROOFS:
        kk = {'green': 1, 'green2': 2, 'main': 3}[kind]
        if hi[kk] is not None: rg = rg.difference(hi[kk])
        gs = [rg] if rg.geom_type == 'Polygon' else [g for g in getattr(rg, 'geoms', []) if g.geom_type == 'Polygon']
        for g in gs:
            c = g.representative_point()
            if kind == 'main':
                continue
            x0, y0, x1, y1 = g.bounds
            yy = y0 + 600
            while yy < y1 - 300:
                xx = x0 + 600 + ((yy // 600) % 2) * 300
                while xx < x1 - 300:
                    if g.contains(sbox(xx - 60, yy - 60, xx + 60, yy + 60)):
                        R.line((xx - 120, yy), (xx, yy + 160), 'L-PLNT', lw=0.08); R.line((xx, yy + 160), (xx + 120, yy), 'L-PLNT', lw=0.08)
                    xx += 900
                yy += 900
    # labels / slopes / drains
    TX = [((11600, Y(28000)), 'หลังคาสวน (Green roof) +4.20\nดินปลูก 150 มม. + แผ่นระบายน้ำ + กันซึม 2 ชั้น\nลาดเอียง 1:100 สู่ท่อระบาย'),
          ((31200, Y(28900)), 'หลังคาสวน +4.20\n(เหนือห้องเธียเตอร์)'), ((9400, Y(15900)), 'หลังคาสวน +4.20'),
          ((9300, Y(20900)), 'หลังคาสวน +7.80\n(เหนือ Junior Suite 2)'), ((31000, Y(20900)), 'หลังคาสวน +7.80\n(เหนือ Junior Suite 3)'),
          ((25600, Y(28200)), 'หลังคา +7.80\n(เหนือห้องนั่งเล่นครอบครัว)'), ((20100, Y(26100)), 'หลังคา +7.80\n(เหนือช่องโล่งโถง)'),
          ((7600, Y(9600)), 'หลังคาสวน +4.20\n(เหนือครัว)'), ((20000, Y(16800)), 'หลังคาแกนลำต้น +11.40'),
          ((22000, Y(12200)), 'หลังคา Crown bar +11.40  ค.ส.ล. + ฉนวน PU 50 มม. + สีสะท้อนแสง SR >= 0.75'),
          ((15100, Y(23000)), 'คอร์ตน้ำ\n(เปิดฟ้า)'), ((25300, Y(21800)), 'คอร์ตต้นไม้\n(เปิดฟ้า)')]
    for p, t in TX:
        R.text(p, t, 210, 'A-TEXT')
    sh = find('ปล่องลม Termite', 1)
    R.text(((sh.x0 + sh.x1) / 2 + 2600, sh.y1 + 900), 'ปล่องลม Termite +14.00\n(กระจก solar chimney + ฝาครอบ)', 190, 'A-ANNO')
    R.line(((sh.x0 + sh.x1) / 2 + 400, sh.y1), ((sh.x0 + sh.x1) / 2 + 1400, sh.y1 + 600), 'A-ANNO')
    # roof drains (RD) & slope arrows
    for (x, y) in ((10000, Y(6600)), (33600, Y(6600)), (10000, Y(12600)), (33600, Y(12600)), (6400, Y(30800)), (33600, Y(30800)), (6400, Y(14000)), (6400, Y(23400)), (33600, Y(23400))):
        R.circle((x, y), 150, 'A-ANNO'); R.text((x + 250, y + 50), 'RD', 150, 'A-ANNO', ha='left')
    def arrow(a, b):
        R.line(a, b, 'A-ANNO', lw=0.13)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        R.pline([(b[0] - 250 * math.cos(ang - .35), b[1] - 250 * math.sin(ang - .35)), b, (b[0] - 250 * math.cos(ang + .35), b[1] - 250 * math.sin(ang + .35))], 'A-ANNO', lw=0.13)
    arrow((16000, Y(9600) + 900), (12000, Y(9600) + 900)); arrow((28000, Y(9600) + 900), (32000, Y(9600) + 900))
    R.text((14000, Y(9600) + 1250), 'ลาด 1:100', 150, 'A-ANNO'); R.text((30000, Y(9600) + 1250), 'ลาด 1:100', 150, 'A-ANNO')
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 4500), 800)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad3 import draw_mpl, scaled_axes
    for nm, fn, sc in (('site', site_plan, 200), ('roof', roof_plan, 100)):
        R = fn()
        if nm == 'roof': grid(R, PLAN_VIEW)
        x0, y0, x1, y1 = R.bbox()
        V = (x0 - 500, y0 - 500, x1 + 500, y1 + 500)
        fig = plt.figure(figsize=((V[2] - V[0]) / sc / 25.4 + .2, (V[3] - V[1]) / sc / 25.4 + .2))
        ax = scaled_axes(fig, 2, 2, V, sc)
        draw_mpl(ax, R, sc)
        fig.savefig('prev_%s.png' % nm, dpi=170 if nm == 'site' else 120); plt.close(fig)
        print(nm, V)
