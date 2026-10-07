# -*- coding: utf-8 -*-
"""WELL RIVERA 30x30 (concept from Rivera Paradise, AtelierM, Buenos Aires 2026) — frame: site, levels, grid (global mm, X=East, Y=North, road on North)
Ring of four wings around a central courtyard; the ring steps down in a spiral (W wing ends at F1, N at F2, E at F3, S rises to F4)
so every roof is a garden and an exterior "helix" stair climbs the roof gardens around the courtyard (interior core = second helix)."""
LOT_W, LOT_D = 30000, 30000
ROAD_W = 8000                      # ASSUMED 8.00 m public road on the north (width not given)
DY = 0
SITE = 0
FF = 3200                          # floor to floor (slab 0.20 + ceiling/services 0.20 + clear 2.80)
F1, F2, F3, F4 = 450, 3650, 6850, 10050
RF = F4 + FF                       # +13.25 top roof garden (S wing)
EAVE = RF
PARAPET = RF + 1100                # +14.35 glass guard rail on the top roof garden
RIDGE = PARAPET
CORE_TOP = PARAPET
SLAB = 200
CEIL_PLENUM = 200
RISE, TREAD = 160, 290
NRISE = FF // RISE                 # 20
STAIR_W = 1000
STAIR_LAND = 1000
GARAGE_Z = 150
PLINTH = F1 - SITE
RAMP_LEN = PLINTH * 12
ROOF_T = 250

def Y(v): return v + DY

XA, XB, XC, XD = 4000, 10000, 20000, 26000      # W wing | courtyard | E wing
YA, YB, YC, YD, YE = 4500, 10500, 12000, 19000, 25000   # S rooms | S gallery | courtyard | N wing
BLK = (XA, YA, XD, YE)                           # outer ring 22.00 x 20.50
COURT = (XB, YC, XC, YD)                         # courtyard 10.00 x 7.00, open to the sky
WING = {'S': (XA, YA, XD, YC), 'W': (XA, YC, XB, YD), 'N': (XA, YD, XD, YE), 'E': (XC, YC, XD, YD)}
WINGS_AT = {1: 'SWNE', 2: 'SNE', 3: 'SE', 4: 'SE'}   # F4: S wing + E roof deck (BBQ)
ROOF_GARDEN = {'W': F2, 'N': F3, 'E': F4, 'S': RF}   # level of the garden on top of each wing (spiral)

STAIR_R = (13000, YA, 15200, YB)                 # main U-stair (flights along Y, floor landing north on the gallery)
LIFT = (15200, 8700, 17000, YB)
CORE_R = (15200, YA, 17000, 8700)
LIFT_LOBBY = (13000, YB, 17000, YC)
TOWER = (13000, YA, 17000, YC)
PSTAIR = (10800, YA, 13000, YB)                  # private master stair F3-F4 (flights along Y, floor landing north)
FOYER = (XA, YD, XB, YE)                         # double-height foyer under a brick barrel vault (spans N-S)
VAULT = (XA, YD, XB, YE)
VAULT_SPRING = F3 - SLAB - 1200                  # +5.45
VAULT_TOP = F3 - SLAB                            # +6.65 crown (underside of the N roof garden slab)
GARAGE = (XB, YD, 22500, YE)

# exterior helix: (name, rect, z from, z to, rising towards)
HELIX = [('H1', (XB, 12290, XB + 1200, YD), F1, F2, 'N'),      # courtyard -> W roof garden (+3.65)
         ('H2', (XA + 200, 13190, XA + 1400, 19000), F2, F3, 'N'), # W roof -> N roof garden (+6.85)
         ('H3', (24600, 19000, 25800, 24810), F3, F4, 'S'),        # N roof -> E roof deck (+10.05)
         ('H4', (24600, YC, 25800, 17810), F4, RF, 'S')]           # E roof -> top roof garden (+13.25)
HELIX_W = 1200

# legacy names used by shared modules
DOME_SQ = (0, 0, 0, 0); DOME_C = (0, 0); DOME_R = 1; DOME_T = 1; DOME_SPRING = 0; DOME_TOP = 0
CORE_SQ = DOME_SQ; CORE_C = DOME_C; CORE_R_ = DOME_R
OFFICE = (21500, YB, XD, 17000)
LINK = (0, 0, 0, 0)
FSTAIR = (0, 0, 0, 0)

GX = {'1': XA, '2': XB, '3': 13000, '4': 17000, '5': XC, '6': XD}
GY = {'A': YA, 'B': YC, 'C': YD, 'D': YE}
GARAGE_COLS = []

POOL = (6000, 900, 20000, 3600)                  # 14.00 x 2.70 lap pool along the south
POOL_DECK = (5300, 400, 20700, 4100)
REFLECT = (13500, 13000, 19200, 16000)           # courtyard reflecting pool
TREE_C = (16500, 17600)                           # courtyard tree
PAVILION = (0, 0, 0, 0)
DRIVE = (XB, YE, 22500, LOT_D)
WALK = (XA, YE, XB, LOT_D)                       # front path to the foyer door (north)
GEN_PAD = (600, 22000, 2600, 24000)
SEPTIC = (27400, 19500, 29400, 22500)
AC_PAD = (27400, 9000, 29400, 13000)
RAIN_TANK = (600, 15000, 3000, 18000)
FENCE_H = 1800
PV_ROWS = [(XA + 400, 4800, XD - 400, 7080)]     # one row of portrait modules on the top roof (S wing)

if __name__ == '__main__':
    import math
    print('lot %.2f m2 = %.2f sq.wa' % (LOT_W * LOT_D / 1e6, LOT_W * LOT_D / 4e6))
    W = XD - XA; D = YE - YA
    print('ring %.2f x %.2f  court %.2f x %.2f = %.1f m2' % (W / 1000, D / 1000, (XC - XB) / 1000, (YD - YC) / 1000, (XC - XB) * (YD - YC) / 1e6))
    for k, r in WING.items(): print(' wing', k, (r[2] - r[0]) / 1000, 'x', (r[3] - r[1]) / 1000, '=', (r[2] - r[0]) * (r[3] - r[1]) / 1e6)
    print('setbacks W %.2f E %.2f S %.2f N %.2f' % (XA / 1000, (LOT_W - XD) / 1000, YA / 1000, (LOT_D - YE) / 1000))
    print('risers', FF / RISE, '2R+T', 2 * RISE + TREAD, 'clear', (FF - SLAB - CEIL_PLENUM) / 1000, 'roof', RF / 1000, 'rail', PARAPET / 1000)
    for n, r, z0, z1, d in HELIX:
        run = (r[3] - r[1]); need = 19 * TREAD
        print(' helix', n, 'run', run, 'need', need, 'width', r[2] - r[0], 'rise', (z1 - z0) / 20)
    print('vault spring %.2f crown %.2f span %.2f' % (VAULT_SPRING / 1000, VAULT_TOP / 1000, (VAULT[3] - VAULT[1]) / 1000))
