# -*- coding: utf-8 -*-
"""WELL G-BEACH 30x30 — frame: site, levels, grid, core (global mm, X=East, Y=North, road on North)"""
LOT_W, LOT_D = 30000, 30000
ROAD_W = 8000                      # ASSUMED 8.00 m public road on the north (width not given)
DY = 0

SITE = 0
F1, F2, F3, F4 = 450, 3850, 7250, 10650
RF = 14050                         # roof slab top over F4
PARAPET = 14650
CORE_TOP = 14850                   # cylinder crown (< 15.00)
FF = 3400
SLAB = 200
CEIL_PLENUM = 400
RISE, TREAD = 170, 280
NRISE = FF // RISE                 # 20
STAIR_W = 1000                     # flights inside the cylinder
STAIR_LAND = 1000
GARAGE_Z = 150
COURT_Z = 150
PLINTH = F1 - SITE
RAMP_LEN = PLINTH * 12

def Y(v): return v + DY

BAR = (5500, 4000, 20500, 26500)               # 15.00 x 22.50 slab block (G-Beach bar)
UPPER = (5500, 4000, 20500, 19300)             # F3 / F4 footprint
CORE_C = (21800, 15150)                        # cylinder centre
CORE_R = 2700                                  # outer radius (wall 200)
CORE_SQ = (19100, 12450, 24500, 17850)
LIFT = (17300, 16050, 19100, 17850)
FSTAIR = (3000, 15000, 5500, 20600)            # external fire-escape stair (ฉ.55 ข้อ 27)

GX = {'1': 5500, '2': 9700, '3': 13000, '4': 17300, '5': 20500}
GY = {'A': 4000, 'B': 11900, 'C': 14050, 'D': 19300, 'E': 20500, 'F': 26500}

BLD = BAR
POOL = (25000, 8800, 28800, 24800)             # 3.80 x 16.00 lap pool (east garden)
POOL_DECK = (24300, 8000, 29400, 25500)
PAVILION = (21300, 3000, 28800, 7700)          # 7.50 x 4.70 = 35.25 m2 poolside sala
DRIVE = (5500, 26500, 20500, 30000)
WALK = (20500, 26500, 23000, 30000)
SVC_YARD = (0, 4000, 3000, 26500)
GEN_PAD = (600, 22000, 2600, 24000)
SEPTIC = (600, 18500, 2600, 20800)
AC_PAD = (600, 6000, 2600, 10000)
RAIN_TANK = (21500, 20500, 24000, 23000)
FENCE_H = 1800

if __name__ == '__main__':
    W = BAR[2] - BAR[0]; D = BAR[3] - BAR[1]
    print('lot %.2f m2 = %.2f sq.wa' % (LOT_W * LOT_D / 1e6, LOT_W * LOT_D / 4e6))
    print('bar %.2f x %.2f  setbacks W %.2f E(bar) %.2f E(core) %.2f S %.2f N %.2f' % (W / 1000, D / 1000, BAR[0] / 1000, (LOT_W - BAR[2]) / 1000,
          (LOT_W - CORE_SQ[2]) / 1000, BAR[1] / 1000, (LOT_D - BAR[3]) / 1000))
    print('risers', FF / RISE, '2R+T', 2 * RISE + TREAD, 'clear', (FF - SLAB - CEIL_PLENUM) / 1000)
    import math
    hd = math.hypot((2 * STAIR_W + 100) / 2, (9 * TREAD + 2 * STAIR_LAND) / 2)
    print('U-stair half-diagonal %.0f vs inner radius %d' % (hd, CORE_R - 200))
    print('height roof %.2f parapet %.2f core %.2f (<15.00)' % (RF / 1000, PARAPET / 1000, CORE_TOP / 1000))
    print('fire stair to W boundary %.2f' % (FSTAIR[0] / 1000))
    print('pavilion m2 %.2f' % ((PAVILION[2] - PAVILION[0]) * (PAVILION[3] - PAVILION[1]) / 1e6))
