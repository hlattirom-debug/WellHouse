# -*- coding: utf-8 -*-
"""WELL KILN 30x30 (concept from Intrinsic / Chain10) — frame: site, levels, grid (global mm, X=East, Y=North, road on North)"""
LOT_W, LOT_D = 30000, 30000
ROAD_W = 8000                      # ASSUMED 8.00 m public road on the north (width not given)
DY = 0

SITE = 0
F1, F2, F3, F4 = 450, 3850, 7250, 10650
RF = 14050                         # roof slab top over F4
PARAPET = 14650
CORE_TOP = 14850                   # chimney (stair tower) crown and lounge vault crown (< 15.00)
VAULT_TOP = 14850
FF = 3400
SLAB = 200
CEIL_PLENUM = 400
RISE, TREAD = 170, 280
NRISE = FF // RISE                 # 20
STAIR_W = 1000
STAIR_LAND = 1000
GARAGE_Z = 150
PLINTH = F1 - SITE
RAMP_LEN = PLINTH * 12

def Y(v): return v + DY

BLK = (3500, 7500, 26500, 19500)               # main block 23.00 x 12.00 (E-W bar, long faces N/S)
BAR = BLK
UPPER = (3500, 7500, 26500, 19500)             # F3/F4 bounding box (NW part not built)
TOWER = (13100, 14900, 17100, 19500)           # brick stair+lift tower = "kiln chimney" (rises to +14.85)
STAIR_R = (13100, 14900, 15300, 19500)
LIFT = (15300, 17700, 17100, 19500)
LIFT_LOBBY = (15300, 14900, 17100, 17700)
FSTAIR = (21500, 5100, 26500, 7500)            # external steel fire-escape stair (ฉ.55 ข้อ 27), flights along X
GARAGE = (3500, 19500, 16500, 26000)
LINK = (16500, 19500, 18200, 26000)
DOME_SQ = (18200, 19500, 23800, 25100)         # brick dome foyer ("kiln")
DOME_C = (21000, 22300)
DOME_R = 2800                                  # outer radius, wall 240
DOME_T = 240
DOME_SPRING = F1 + 3000                        # +3.45 drum top
DOME_TOP = DOME_SPRING + DOME_R                # +6.25 crown (oculus)
OFFICE = (9300, 19500, 14100, 24900)           # F2 library pavilion over the garage
VAULT = (14300, 7500, 19700, 13300)            # F4 family lounge, barrel vault N-S axis

# legacy names used by shared modules
CORE_SQ = DOME_SQ
CORE_C = DOME_C
CORE_R = DOME_R

GX = {'1': 3500, '2': 8300, '3': 13100, '4': 17100, '5': 21900, '6': 26500}
GY = {'A': 7500, 'B': 13300, 'C': 15300, 'D': 19500, 'E': 26000}
GARAGE_COLS = [(3500, 26000), (16500, 26000), (9800, 24900), (13000, 24900)]

POOL = (4500, 1700, 18500, 4700)               # 14.00 x 3.00 lap pool (south garden)
POOL_DECK = (3800, 1000, 19300, 5400)
PAVILION = (0, 0, 0, 0)                        # pavilion program absorbed by F1 veranda (ใต้ถุน)
DRIVE = (3500, 26000, 16500, 30000)
WALK = (19800, 25100, 22200, 30000)
GEN_PAD = (600, 22000, 2600, 24000)
SEPTIC = (600, 18500, 2600, 20800)
AC_PAD = (600, 9000, 2600, 13000)
RAIN_TANK = (26800, 20500, 29300, 23000)
FENCE_H = 1800

if __name__ == '__main__':
    import math
    W = BLK[2] - BLK[0]; D = BLK[3] - BLK[1]
    print('lot %.2f m2 = %.2f sq.wa' % (LOT_W * LOT_D / 1e6, LOT_W * LOT_D / 4e6))
    print('block %.2f x %.2f setbacks W %.2f E %.2f S %.2f N(block) %.2f N(wing) %.2f N(dome) %.2f' % (W / 1000, D / 1000, BLK[0] / 1000,
          (LOT_W - BLK[2]) / 1000, BLK[1] / 1000, (LOT_D - BLK[3]) / 1000, (LOT_D - GARAGE[3]) / 1000, (LOT_D - DOME_SQ[3]) / 1000))
    print('risers', FF / RISE, '2R+T', 2 * RISE + TREAD, 'clear', (FF - SLAB - CEIL_PLENUM) / 1000)
    print('U-stair length', 9 * TREAD + 2 * STAIR_LAND, 'in tower', STAIR_R[3] - STAIR_R[1], 'width', 2 * STAIR_W + 100, '<=', STAIR_R[2] - STAIR_R[0])
    print('height roof %.2f parapet %.2f crown %.2f (<15.00)' % (RF / 1000, PARAPET / 1000, CORE_TOP / 1000))
    print('dome area %.2f crown %.2f' % (math.pi * (DOME_R / 1000) ** 2, DOME_TOP / 1000))
    print('fire stair to S/E boundary %.2f / %.2f' % (FSTAIR[1] / 1000, (LOT_W - FSTAIR[2]) / 1000))
    print('garage %.2f m2  clear width %.2f -> %d cars @3.10' % ((GARAGE[2] - GARAGE[0]) * (GARAGE[3] - GARAGE[1]) / 1e6, (GARAGE[2] - GARAGE[0]) / 1000, (GARAGE[2] - GARAGE[0]) // 3100))
    print('vault span %.2f rise %.2f' % ((VAULT[2] - VAULT[0]) / 1000, (VAULT_TOP - (RF - 250)) / 1000))
