# -*- coding: utf-8 -*-
"""Site plan (1:200) and roof plan (1:100)."""
import math
from shapely.geometry import box as sbox
from shapely.ops import unary_union
from cad6 import Rec
from frame6 import *
from plan6 import FLOORS, COURTS, find
from model6 import build, TREES, INFO_PV
from proj6 import project_top
from draw6 import north_arrow, grid, PLAN_VIEW, columns, COL
from furn6 import car, plant, lounger

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
    """asymmetric gable: seams, ridge, slope arrows, skylight, PV field, gutters"""
    from model6 import SKY, roof_pieces
    X0, X1 = BLK[0] - OVER_EW, BLK[2] + OVER_EW
    ys, yn = BLK[1] - OVER_S, BLK[3] + OVER_N
    x = X0 + 450
    while x < X1:
        for ya, yb in ((ys, RIDGE_Y), (RIDGE_Y, yn)):
            R.line((x, ya), (x, yb), 'A-ROOF', lw=0.05, c='#9aa0a6')
        x += 450
    R.line((X0, RIDGE_Y), (X1, RIDGE_Y), 'A-ROOF', lw=0.5)
    R.rect(X0, ys, X1, yn, 'A-ROOF', lw=0.4)
    R.frect(SKY[0], SKY[1], SKY[2], SKY[3], 'A-AREA', color='#bcd6e6', z=4); R.rect(SKY[0], SKY[1], SKY[2], SKY[3], 'A-GLAZ')
    for xx in range(SKY[0] + 1200, SKY[2], 1200): R.line((xx, SKY[1]), (xx, SKY[3]), 'A-GLAZ', lw=0.08)
    for (x0, yy0, x1, yy1) in ((X0, ys, X1, ys + 200), (X0, yn - 200, X1, yn)):
        R.frect(x0, yy0, x1, yy1, 'A-AREA', color='#8a9098', z=4)
    for xx in (X0 + 400, (X0 + X1) / 2, X1 - 400):
        for yy in (ys + 100, yn - 100):
            R.circle((xx, yy), 120, 'A-ANNO')
    if not labels: return
    def arrow(x, y0, y1, t):
        R.line((x, y0), (x, y1), 'A-ANNO', lw=0.3)
        sg = 1 if y1 > y0 else -1
        R.pline([(x - 180, y1 - sg * 350), (x, y1), (x + 180, y1 - sg * 350)], 'A-ANNO', lw=0.3)
        R.text((x + 250, (y0 + y1) / 2), t, 190, 'A-ANNO', ha='left', rot=90)
    for x in (3000, 26900):
        arrow(x, RIDGE_Y - 400, ys + 700, 'ลาดลง 40%% (%.1f°)' % math.degrees(math.atan(SLOPE_S)))
        arrow(x, RIDGE_Y + 400, yn - 700, 'ลาดลง 25%% (%.1f°)' % math.degrees(math.atan(SLOPE_N)))
    R.text((X0 + 300, RIDGE_Y + 250), 'สันหลังคา +%.2f' % (RIDGE / 1000), 200, 'A-ANNO', ha='left', va='bottom', bold=True)
    R.text(((SKY[0] + SKY[2]) / 2, (SKY[1] + SKY[3]) / 2), 'ช่องแสงสันหลังคา (กระจก laminated Low-E) เหนือโถงไม้ "Forno hall"', 180, 'A-ANNO')
    R.text((X0 + 300, ys + 300), 'รางน้ำ +%.2f · ท่อลง RD' % (roof_z(ys) / 1000), 170, 'A-ANNO', ha='left', va='bottom')
    R.text((X0 + 300, yn - 300), 'รางน้ำ +%.2f · ท่อลง RD' % (roof_z(yn) / 1000), 170, 'A-ANNO', ha='left', va='top')

SKIP_TOP = ('ground', 'road', 'column', 'wall', 'glass', 'door', 'band', 'rail', 'slab', 'plinth', 'opening', 'rafter', 'exo', 'lattice', 'gutter', 'ridge', 'skylight')

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
    for (a, b) in [((0, 10000), (BLK[0], 10000)), ((BLK[2], 11000), (LOT_W, 11000)), ((11000, 0), (11000, FRAME_S_Y - POST_D)), ((13500, 0), (13500, BLK[1])),
                   ((5000, GARAGE[3]), (5000, LOT_D)), ((23800, FSTAIR[3]), (23800, LOT_D)), ((BLK[0] - OVER_EW, 14500), (0, 14500))]:
        R.dim(a, b, 0, h=240)
    L = [((10000, 26300), 'ทางรถเข้า - โรงจอดรถ 4 คัน'), ((27950, 26300), 'ทางเดิน\nเข้าบ้าน\n(ทาง\nทิศ\nตะวันออก)'),
         ((12000, 800), 'สระว่ายน้ำ 14.00 x 3.00 ม.'), ((12400, 5350), 'ลาน "piazza" ใต้ชายคา'),
         ((1600, 23000), 'เครื่อง\nปั่นไฟ'), ((1600, 18650), 'ถังบำบัด'), ((1600, 11000), 'CDU\nแอร์'),
         ((18700, 23750), 'ถังน้ำฝน\nใต้ดิน'), ((15000, 6700), 'หลังคาจั่วไม่สมมาตร ลาด 40% + แผงโซลาร์'),
         ((15000, 17800), 'หลังคาลาด 25% · ช่องแสงสันหลังคา'), ((16500, 13000), 'สันหลังคา +14.95')]
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
    R = project_top(BX, cats_skip=SKIP_TOP + ('fence', 'pool', 'deck', 'pavilion', 'paving'),
                    clip=(PLAN_VIEW[0], PLAN_VIEW[1], PLAN_VIEW[2], PLAN_VIEW[3]))
    roof_marks(R)
    for rg, z, kind in ROOFS:
        gs = [rg] if rg.geom_type == 'Polygon' else [g for g in getattr(rg, 'geoms', []) if g.geom_type == 'Polygon']
        for g in gs:
            R.pline(list(g.exterior.coords), 'A-HIDD', ls='--', lw=0.13)
    TX = [((15000, 6600), 'แผงโซลาร์ %d แผง (~%.1f kWp) บนหลังคาลาดทิศใต้' % (INFO_PV['n'], INFO_PV['n'] * 0.55)),
          ((15000, 18100), 'หลังคาเหล็กรีดลอน standing seam + ฉนวน PIR 75 + ฝ้าไม้ซีดาร์/สน ใต้หลังคา (โครงแปไม้ glulam)'),
          ((10000, 21000), 'หลังคาโรงรถ +3.65 (ค.ส.ล. + สวนแนวราบ) ใต้ชายคา'),
          ((15000, 5000), 'ชายคายื่น 3.00 ม. (ปลายชายคา +%.2f) · เสาโครงไม้ + ค้ำเอียงรับปลายชายคา' % (roof_z(BLK[1] - OVER_S) / 1000)),
          ((5800, 14000), 'คอร์ตแสงทิศตะวันตก\n(ใต้หลังคา เปิดด้านสกัด)'), ((23850, 14000), 'คอร์ตแสงทิศตะวันออก\n(ใต้หลังคา เปิดด้านสกัด)'),
          ((23800, 23700), 'บันไดหนีไฟ (เหล็ก เปิดโล่ง)')]
    for p, t in TX:
        R.text(p, t, 200, 'A-TEXT')
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 2200), 800)
    return R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from cad6 import draw_mpl, scaled_axes
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
