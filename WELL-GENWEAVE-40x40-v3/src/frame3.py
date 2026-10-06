# -*- coding: utf-8 -*-
"""WELL-GENWEAVE 40x40 v3 — frame: site, levels, grid, wings (global mm, X=East, Y=North, road on North)"""
LOT_W, LOT_D = 40000, 40000
ROAD_W = 8000                      # road north (Y > 40000)
DY = 2600                          # building shift north (all building Y below already include DY)

# ---- levels (mm above site ±0.00 = road crown) ----
SITE = 0
F1, F2, F3 = 600, 4200, 7800       # finished floor levels
RF = 11400                         # main roof slab top (crown bar + spine)
PARAPET = 12000
CHIMNEY = 13800                    # Termite solar chimney top
GROOF = 4200                       # green roofs over F1 (same as F2 FFL)
GPAR = 4800                        # green-roof parapet
FF = 3600                          # floor to floor
SLAB = 200
CEIL_PLENUM = 400                  # MEP plenum under slab
RISE, TREAD = 180, 280
NRISE = FF // RISE                 # 20 risers / floor
STAIR_W = 1200
PLINTH = F1 - SITE                 # 600 plinth (Mangrove principle: raised above flood)
RAMP_LEN = PLINTH * 12             # 1:12
COURT_Z = 150
GARAGE_Z = 150

def Y(v):  # local (design) Y -> global
    return v + DY

# ---- structural grid (global) ----
GX = {'1': 5800, '2': 9400, '3': 13000, '4': 17200, '5': 23000, '6': 27800, '7': 30300, '8': 34200}
GY = {'A': Y(6000), 'B': Y(13200), 'C': Y(17400), 'D': Y(24000), 'E': Y(31400)}

BLD = (5800, Y(6000), 34200, Y(31400))   # bounding box of F1

# ---- external works (global mm) ----
POOL = (12000, 2400, 28000, 6900)        # 16.0 x 4.5 saltwater pool (BEETLE -> water)
POOL_DECK = (10800, 1200, 29200, 8600)
PAVILION = (29000, 2200, 35500, 7600)    # 6.5 x 5.4 = 35.1 m2 poolside sala
DRIVE = (5800, Y(31400), 17200, 40000)   # garage apron to road
WALK = (17200, Y(31400), 23000, 40000)   # porch to gate
RAMP = (23000, Y(31400), 23000 + RAMP_LEN, Y(31400) + 1500)   # 1:12 ramp, falls east->west? (rises toward porch)
SVC_YARD = (0, Y(13200), 5800, Y(24000))
SWALE_S = (0, 0, 40000, 1000)            # mangrove bioswale south
SWALE_E = (39000, 1000, 40000, 30000)
RAIN_TANK = (13800, Y(14000), 16400, Y(16600))   # 2.6 x 2.6 x 3.0 underground ~20 m3 under W court
SEPTIC = (1000, Y(27000), 3400, Y(29400))
WETLAND = (1000, 9000, 4800, Y(12000))           # constructed wetland (greywater)
GEN_PAD = (1200, Y(24600), 3600, Y(26200))       # generator in acoustic enclosure (service yard)
AC_PAD = (35400, Y(17400), 38600, Y(24000))      # VRF condensers east side yard
FENCE_H = 1800

if __name__ == '__main__':
    W = BLD[2] - BLD[0]; D = BLD[3] - BLD[1]
    print('lot %.2f m2 = %.2f sq.wa' % (LOT_W * LOT_D / 1e6, LOT_W * LOT_D / 1e6 / 4))
    print('bbox %.2f x %.2f' % (W / 1000, D / 1000))
    print('setbacks W %.2f E %.2f S %.2f N %.2f' % (BLD[0] / 1000, (LOT_W - BLD[2]) / 1000, BLD[1] / 1000, (LOT_D - BLD[3]) / 1000))
    print('risers', FF / RISE, 'ok' if FF % RISE == 0 else 'NOT INTEGER')
    print('2R+T', 2 * RISE + TREAD, 'ok' if 600 <= 2 * RISE + TREAD <= 650 else 'BAD')
    print('clear F1', (FF - SLAB - CEIL_PLENUM) / 1000, 'ok' if FF - SLAB - CEIL_PLENUM >= 2600 else 'BAD')
    print('height to roof %.2f, parapet %.2f, chimney %.2f  (>9.00 -> openings >=3.00 from boundary)' % (RF / 1000, PARAPET / 1000, CHIMNEY / 1000))
    print('ramp 1:12 length', RAMP_LEN)
    print('pool', (POOL[2] - POOL[0]) / 1000, (POOL[3] - POOL[1]) / 1000, 'pavilion m2', (PAVILION[2] - PAVILION[0]) * (PAVILION[3] - PAVILION[1]) / 1e6)
    print('pavilion gap to S/E boundary', PAVILION[1] / 1000, (LOT_W - PAVILION[2]) / 1000, 'gap to bld', (BLD[1] - PAVILION[3]) / 1000)
