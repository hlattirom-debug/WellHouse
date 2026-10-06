# -*- coding: utf-8 -*-
"""WELL FORNO 30x30 (concept from FORNO, Gruppo FON Architetti) — frame: site, levels, grid (global mm, X=East, Y=North, road on North)
RC primary frame + external glulam timber exoskeleton (frames @2.875 m, Y-struts at F1) + one asymmetric gable roof over the whole bar."""
LOT_W, LOT_D = 30000, 30000
ROAD_W = 8000                      # ASSUMED 8.00 m public road on the north (width not given)
DY = 0
SITE = 0
FF = 3200                          # floor to floor (slab 0.20 + ceiling/services 0.20 + clear 2.80)
F1, F2, F3, F4 = 450, 3650, 6850, 10050
EAVE = F4 + 2900                   # +12.95 roof TOP at the wall lines (underside +12.65 -> F4 clear 2.60 at the low walls)
RF = EAVE
RIDGE = 14950                      # roof TOP at the ridge (< 15.00)
PARAPET = EAVE
CORE_TOP = RIDGE
SLAB = 200
CEIL_PLENUM = 200
RISE, TREAD = 160, 290
NRISE = FF // RISE                 # 20
STAIR_W = 1000
STAIR_LAND = 1000
GARAGE_Z = 150
PLINTH = F1 - SITE
RAMP_LEN = PLINTH * 12

def Y(v): return v + DY

BLK = (3500, 7500, 26500, 20500)               # main bar 23.00 x 13.00 : S bar 5.00 | hall 3.00 | N bar 5.00
BAR = BLK
UPPER = BLK
SB = (7500, 12500); HALL = (12500, 15500); NB = (15500, 20500)
VOID = (8100, 12500, 21200, 14300)             # 4-storey "Forno hall" void under the ridge skylight (F2-F4)
GALLERY = (8100, 14300, 21200, 15500)
COURT_W = (3500, 12500, 8100, 15500)           # open light courts above F2 (F3-F4)
COURT_E = (21200, 12500, 26500, 15500)
STAIR_R = (16300, 15500, 18500, 20500)         # main stair (U along Y, floor landing south)
LIFT_LOBBY = (18500, 15500, 20300, 18700)
LIFT = (18500, 18700, 20300, 20500)
TOWER = (16300, 15500, 20300, 20500)
PSTAIR = (24300, 7500, 26500, 12500)           # private master stair F3-F4 (U along Y, floor landings north)
BRIDGE = {2: (16900, 12500, 18700, 14300), 3: (16900, 12500, 18700, 14300), 4: (9900, 12500, 11700, 14300)}  # timber bridges across the hall void
FSTAIR = (21300, 20500, 26300, 22900)          # external steel fire stair (ฉ.55 ข้อ 27), flights along X, landing east
GARAGE = (3500, 15500, 16300, 21500)
BALC = (3500, 6000, 26500, 7500)               # continuous south timber balcony layer F2-F4

# roof: asymmetric gable, ridge along X at y = RIDGE_Y
RIDGE_Y = 12500
ROOF_S = (EAVE, BLK[1])                        # south slope reaches EAVE at y 7500
SLOPE_S = (RIDGE - EAVE) / (RIDGE_Y - BLK[1])  # 0.40 (21.8 deg)
SLOPE_N = (RIDGE - EAVE) / (BLK[3] - RIDGE_Y)  # 0.25 (14.0 deg)
OVER_S, OVER_N, OVER_EW = 3000, 1000, 1000     # overhangs: south to y 4500, north to 21500, east/west 1.00
ROOF_T = 300
def roof_z(y):
    """TOP of roof at y (mm); underside = roof_z(y) - ROOF_T"""
    return RIDGE - SLOPE_S * (RIDGE_Y - y) if y <= RIDGE_Y else RIDGE - SLOPE_N * (y - RIDGE_Y)

# timber exoskeleton frames
FRAME_X = [BLK[0] + k * 2875 for k in range(9)]
FRAME_S_Y = BALC[1]                            # south frame line (balcony edge)
FRAME_N_Y = GARAGE[3] - 120                    # north frame line = garage front / north eave edge
FRAME_N_X = FRAME_X[:6]                        # north posts x 3500..17875 (east part: steel fire stair)
POST_W, POST_D = 240, 480                      # glulam post (x, y)
YJOINT = F4                                    # raking strut springs from the south posts at F4 slab level
RAFTER_W, RAFTER_D = 160, 400                  # exposed glulam rafters on every frame line

# legacy names used by shared modules
DOME_SQ = (0, 0, 0, 0); DOME_C = (0, 0); DOME_R = 1; DOME_T = 1; DOME_SPRING = 0; DOME_TOP = 0
CORE_SQ = DOME_SQ; CORE_C = DOME_C; CORE_R = DOME_R
VAULT = (0, 0, 0, 0); VAULT_TOP = RIDGE
OFFICE = (20300, 15500, 26500, 20500)
LINK = (0, 0, 0, 0)

GX = {'1': 3500, '2': 8100, '3': 12300, '4': 16300, '5': 20300, '6': 26500}
GY = {'A': 7500, 'B': 12500, 'C': 15500, 'D': 20500}
GARAGE_COLS = []

POOL = (5000, 1200, 19000, 4200)               # 14.00 x 3.00 lap pool
POOL_DECK = (4300, 600, 19700, 4700)
PIAZZA = (3500, 4700, 21300, 6000)             # paved "piazza" strip between pool and porch
PAVILION = (0, 0, 0, 0)
DRIVE = (3500, 21500, 16300, 30000)
WALK = (26700, 15000, 29200, 30000)            # east side path from the road to the foyer (east door)
GEN_PAD = (600, 22000, 2600, 24000)
SEPTIC = (600, 17500, 2600, 19800)
AC_PAD = (600, 9000, 2600, 13000)
RAIN_TANK = (17200, 22500, 20200, 25000)
FENCE_H = 1800

if __name__ == '__main__':
    import math
    W = BLK[2] - BLK[0]; D = BLK[3] - BLK[1]
    print('lot %.2f m2 = %.2f sq.wa' % (LOT_W * LOT_D / 1e6, LOT_W * LOT_D / 4e6))
    print('bar %.2f x %.2f setbacks W %.2f E %.2f S(bar) %.2f S(balc) %.2f N(bar) %.2f N(garage) %.2f' % (W / 1000, D / 1000, BLK[0] / 1000,
          (LOT_W - BLK[2]) / 1000, BLK[1] / 1000, BALC[1] / 1000, (LOT_D - BLK[3]) / 1000, (LOT_D - GARAGE[3]) / 1000))
    print('risers', FF / RISE, '2R+T', 2 * RISE + TREAD, 'clear', (FF - SLAB - CEIL_PLENUM) / 1000)
    print('U-stair length', 9 * TREAD + 2 * STAIR_LAND, 'in', STAIR_R[3] - STAIR_R[1], 'width', 2 * STAIR_W + 100, '<=', STAIR_R[2] - STAIR_R[0])
    print('eave %.2f ridge %.2f (<15.00) slopes S %.1f deg N %.1f deg' % (EAVE / 1000, RIDGE / 1000, math.degrees(math.atan(SLOPE_S)), math.degrees(math.atan(SLOPE_N))))
    print('roof edge S z %.2f at y %.2f ; N z %.2f at y %.2f' % (roof_z(BLK[1] - OVER_S) / 1000, (BLK[1] - OVER_S) / 1000, roof_z(BLK[3] + OVER_N) / 1000, (BLK[3] + OVER_N) / 1000))
    print('fire stair to N/E boundary %.2f / %.2f' % ((LOT_D - FSTAIR[3]) / 1000, (LOT_W - FSTAIR[2]) / 1000))
    print('garage %.2f m2 width %.2f -> %d cars @3.20' % ((GARAGE[2] - GARAGE[0]) * (GARAGE[3] - GARAGE[1]) / 1e6, (GARAGE[2] - GARAGE[0]) / 1000, (GARAGE[2] - GARAGE[0]) // 3200))
    print('frames', FRAME_X)
