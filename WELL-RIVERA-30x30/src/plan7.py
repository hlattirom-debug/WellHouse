# -*- coding: utf-8 -*-
"""WELL RIVERA 30x30 — rooms. Ring of 4 wings around a courtyard, stepping down in a spiral (F1 SWNE, F2 SNE, F3 SE, F4 S + E deck)."""
from frame7 import *

class R:
    __slots__ = ('name', 'x0', 'y0', 'x1', 'y1', 'kind', 'fl', 'code', 'lab')
    def __init__(s, name, rc, kind, code='', lab=None):
        s.name = name; s.x0, s.y0, s.x1, s.y1 = rc; s.kind = kind; s.code = code; s.lab = lab
    @property
    def a(s): return (s.x1 - s.x0) * (s.y1 - s.y0) / 1e6
    @property
    def w(s): return s.x1 - s.x0
    @property
    def d(s): return s.y1 - s.y0
    def rect(s): return (s.x0, s.y0, s.x1, s.y1)
    def __repr__(s): return '<%s %s %.2f>' % (s.code, s.name, s.a)

MAIN = 'บันไดหลัก (เกลียวใน)'
def core(fl, rear, rk):
    return [R(MAIN, STAIR_R, 'stair'), R('ลิฟต์บ้าน', LIFT, 'lift'), R(rear, CORE_R, rk)]

GAR = 'โรงจอดรถ 4 คัน'
FOY = 'โถงต้อนรับใต้โค้งอิฐ (สูง 2 ชั้น)'
F1R = [
    R(FOY, FOYER, 'circ'),
    R(GAR, GARAGE, 'park'),
    R('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ', (22500, YD, XD, YE), 'svc'),
    R('ห้องนอนแขก/ผู้สูงอายุ', (XA, YC, 8000, 16000), 'room'),
    R('ห้องน้ำห้องแขก', (XA, 16000, 6000, YD), 'wet'),
    R('ตู้เสื้อผ้าห้องแขก', (6000, 16000, 8000, YD), 'svc'),
    R('โถงทางเดินริมคอร์ต (ตะวันตก)', (8000, YC, XB, YD), 'circ'),
    R('ครัวไทย (ครัวหนัก)', (XA, YA, 8000, 9000), 'room'),
    R('ห้องซักรีด', (XA, 9000, 8000, YC), 'svc'),
    R('ศาลาริมสระ (ทะลุคอร์ต)', (8000, YA, 13000, YC), 'inb'),
    *core(1, 'ห้องเก็บของ / อุปกรณ์สระ', 'svc'),
    R('แกลเลอรีริมคอร์ต ชั้น 1', (13000, YB, XC, YC), 'circ'),
    R('ห้องฟิตเนส / โยคะ ริมสระ', (17000, YA, 23000, YB), 'room'),
    R('ห้องเครื่องสระ / เก็บของ', (23000, YA, XD, YB), 'svc'),
    R('โถงบริการ (ตะวันออก)', (XC, YB, 21500, YD), 'circ'),
    R('ห้องน้ำแม่บ้าน', (21500, YB, XD, YC), 'wet'),
    R('ห้องแม่บ้าน 2', (21500, YC, XD, 15500), 'room'),
    R('ห้องแม่บ้าน 1', (21500, 15500, XD, YD), 'room'),
]

F2R = [
    R('ครัวโชว์ + ไอส์แลนด์', (XA, YA, 8000, 9500), 'room'),
    R('Walk-in Pantry & ห้องเย็น', (XA, 9500, 8000, YC), 'svc'),
    R('ห้องรับประทานอาหาร', (8000, YA, 13000, YC), 'room'),
    *core(2, 'ห้องน้ำแขก (Powder)', 'wet'),
    R('แกลเลอรีริมคอร์ต ชั้น 2', (13000, YB, 21500, YC), 'circ'),
    R('ห้องนั่งเล่น', (17000, YA, 23500, YB), 'room'),
    R('ห้องนั่งเล่น (ส่วนต่อเนื่อง)', (23500, YA, XD, YB), 'room'),
    R('ห้องทำงาน & ห้องสมุด', (21500, YB, XD, 17000), 'room'),
    R('ทางเดินริมคอร์ต (ตะวันออก) ชั้น 2', (XC, YC, 21500, YD), 'circ'),
    R('ห้องน้ำ Junior Suite 3', (21500, 17000, 23700, YD), 'wet'),
    R('ตู้เสื้อผ้า Junior Suite 3', (23700, 17000, XD, YD), 'svc'),
    R('ช่องโล่งโถงต้อนรับ (โค้งอิฐ)', FOYER, 'void'),
    R('ทางเดินริมคอร์ต (เหนือ) ชั้น 2', (XB, YD, 21500, 20500), 'circ'),
    R('ตู้เสื้อผ้า Junior Suite 2', (XB, 20500, 12000, 22700), 'svc'),
    R('ห้องน้ำ Junior Suite 2', (XB, 22700, 12000, YE), 'wet'),
    R('ห้องนอน Junior Suite 2', (12000, 20500, 17000, YE), 'room'),
    R('ห้องไวน์ / ซิการ์', (17000, 20500, 20000, YE), 'svc'),
    R('ห้องเก็บของชั้น 2', (20000, 20500, 21500, YE), 'svc'),
    R('ห้องนอน Junior Suite 3', (21500, YD, XD, YE), 'room'),
]

F3R = [
    R('ห้องนอน Master Suite', (XA, YA, 10800, YC), 'room'),
    R('บันไดส่วนตัว Master', PSTAIR, 'stair'),
    R('โถงห้อง Master', (10800, YB, 13000, YC), 'circ'),
    *core(3, 'ห้องเก็บของชั้น 3', 'svc'),
    R('แกลเลอรีริมคอร์ต ชั้น 3', (13000, YB, 21500, YC), 'circ'),
    R('Walk-in Dressing (His & Hers)', (17000, YA, 21500, YB), 'svc'),
    R('ห้องน้ำ Spa + Jacuzzi', (21500, YA, XD, YC), 'wet'),
    R('ลอจเจียตะวันออก (ใต้ลาน BBQ)', WING['E'], 'inb'),
]

CLO4 = 'Master Walk-in Closet ชั้น 4'
F4R = [
    R('ระเบียง Master (ในร่ม)', (XA, YA, 10800, 7500), 'inb'),
    R(CLO4, (XA, 7500, 10800, YC), 'svc'),
    R('บันไดส่วนตัว Master', PSTAIR, 'stair'),
    R(CLO4 + ' (ส่วนต่อเนื่อง)', (10800, YB, 13000, YC), 'svc'),
    *core(4, 'ห้องน้ำชั้น 4', 'wet'),
    R('Upper Gallery (โถงบันได ชั้น 4)', (13000, YB, 21500, YC), 'circ'),
    R('ห้องนั่งเล่นครอบครัว', (17000, YA, 21500, YB), 'room'),
    R('ห้องโฮมเธียเตอร์', (21500, YA, XD, YC), 'room'),
    R('ลาน BBQ บนหลังคา (pergola)', WING['E'], 'inb'),
]

FLOORS = {1: F1R, 2: F2R, 3: F3R, 4: F4R}
for fl, L in FLOORS.items():
    for i, r in enumerate(L):
        r.fl = fl; r.code = '%d%02d' % (fl, i + 1)

NOWALL = [('ห้องนั่งเล่น', 'ห้องนั่งเล่น (ส่วนต่อเนื่อง)'), (CLO4, CLO4 + ' (ส่วนต่อเนื่อง)')]
COURTS = [('คอร์ตกลาง (เปิดฟ้า)', COURT)]

PROGRAM = [  # (name, program floor, area, [design rooms])
    ('Grand Double-Height Foyer', 1, 24, [FOY]),
    ('Formal Living Room', 2, 50, ['ห้องนั่งเล่น', 'ห้องนั่งเล่น (ส่วนต่อเนื่อง)']),
    ('Dining Room (10-12 Seats)', 2, 40, ['ห้องรับประทานอาหาร']),
    ('Powder Room', 2, 6, ['ห้องน้ำแขก (Powder)']),
    ('Home Theater / AV Lounge', 4, 36, ['ห้องโฮมเธียเตอร์']),
    ('Wine Cellar / Cigar Room', 2, 14, ['ห้องไวน์ / ซิการ์']),
    ('Master Suite Bedroom', 3, 48, ['ห้องนอน Master Suite']),
    ('Master Walk-in (His & Hers)', 3, 32, ['Walk-in Dressing (His & Hers)']),
    ('Spa Master Bath + Jacuzzi', 3, 28, ['ห้องน้ำ Spa + Jacuzzi']),
    ('Junior Suite 2 (bath+closet)', 2, 34, ['ห้องนอน Junior Suite 2', 'ห้องน้ำ Junior Suite 2', 'ตู้เสื้อผ้า Junior Suite 2']),
    ('Junior Suite 3 (bath+closet)', 2, 34, ['ห้องนอน Junior Suite 3', 'ห้องน้ำ Junior Suite 3', 'ตู้เสื้อผ้า Junior Suite 3']),
    ('Guest Suite (GF / elderly)', 1, 30, ['ห้องนอนแขก/ผู้สูงอายุ', 'ห้องน้ำห้องแขก', 'ตู้เสื้อผ้าห้องแขก']),
    ('Family Lounge & Upper Gallery', 4, 36, ['ห้องนั่งเล่นครอบครัว', 'Upper Gallery (โถงบันได ชั้น 4)']),
    ('Executive Home Office & Library', 2, 26, ['ห้องทำงาน & ห้องสมุด']),
    ('Master Walk-in Closet (U/L)', 4, 36, [CLO4, CLO4 + ' (ส่วนต่อเนื่อง)']),
    ('Show Kitchen & Island Bar', 2, 28, ['ครัวโชว์ + ไอส์แลนด์']),
    ('Heavy Thai Kitchen', 1, 20, ['ครัวไทย (ครัวหนัก)']),
    ('Walk-in Pantry & Cold Storage', 3, 12, ['Walk-in Pantry & ห้องเย็น']),
    ('Laundry & Utility Room', 1, 16, ['ห้องซักรีด']),
    ('Maid Bedroom 1 & 2', 1, 22, ['ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2']),
    ('Maid Bathroom', 1, 6, ['ห้องน้ำแม่บ้าน']),
    ('MEP / Electrical / Generator', 1, 14, ['ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ']),
    ('Covered Garage 3-4 cars', 1, 85, [GAR]),
    ('Covered Veranda & BBQ', 4, 45, ['ลาน BBQ บนหลังคา (pergola)']),
    ('Upper Master Terrace', 4, 28, ['ระเบียง Master (ในร่ม)']),
    ('Poolside Pavilion', 1, 35, ['ศาลาริมสระ (ทะลุคอร์ต)']),
]
PROGRAM_NUA, PROGRAM_GFA = 785.00, 984.70
PROGRAM_FLOOR_NET = {1: 252.0, 2: 232.0, 3: 120.0, 4: 181.0}

def all_rooms():
    return [r for fl in sorted(FLOORS) for r in FLOORS[fl]]

def find(name, fl=None):
    for r in all_rooms():
        if r.name == name and (fl is None or r.fl == fl):
            return r
    raise KeyError(name)

import math
CORE_AREA = 0.0

def gfa_area(r):
    """area counted for GFA (dome counted as circle)"""
    if r.kind == 'core': return CORE_AREA
    return r.a

if __name__ == '__main__':
    import numpy as np
    step = 100; ok = True
    for fl, L in FLOORS.items():
        xs = [v for r in L for v in (r.x0, r.x1)]; ys = [v for r in L for v in (r.y0, r.y1)]
        X0, Y0 = min(xs), min(ys); X1, Y1 = max(xs), max(ys)
        g = np.zeros(((Y1 - Y0) // step, (X1 - X0) // step), np.int16)
        for r in L:
            g[(r.y0 - Y0) // step:(r.y1 - Y0) // step, (r.x0 - X0) // step:(r.x1 - X0) // step] += 1
        ov = (g > 1).sum(); tot = sum(r.a for r in L); cov = (g > 0).sum() * step * step / 1e6
        print('F%d rooms %d sum %.2f union %.2f overlap %d' % (fl, len(L), tot, cov, ov))
        if ov or abs(tot - cov) > 0.01:
            ok = False
            for i, a in enumerate(L):
                for b in L[i + 1:]:
                    if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1: print('  OVERLAP', a, b)
    from shapely.geometry import box as sb
    from shapely.ops import unary_union
    for fl in FLOORS:
        u = unary_union([sb(*r.rect()) for r in FLOORS[fl] if r.kind != 'fstair'])
        print('  F%d footprint %.2f  holes %d' % (fl, u.area / 1e6, sum(len(p.interiors) for p in ([u] if u.geom_type == 'Polygon' else u.geoms))))
    print('tiling', 'OK' if ok else 'FAIL')
    tp = td = 0
    for nm, pf, pa, rooms in PROGRAM:
        rs = [r for r in all_rooms() if r.name in rooms]; a = sum(gfa_area(r) for r in rs); f = rs[0].fl
        tp += pa; td += a
        print('%-34s F%d %6.2f  F%d %6.2f %+6.2f (%+.0f%%)' % (nm, pf, pa, f, a, a - pa, (a / pa - 1) * 100))
    print('NUA prog %.2f design %.2f %+.2f' % (tp, td, td - tp))
    gfa = sum(gfa_area(r) for r in all_rooms() if r.kind not in ('void', 'fstair'))
    enc = sum(gfa_area(r) for r in all_rooms() if r.kind not in ('void', 'inb', 'park', 'fstair'))
    print('GFA %.2f vs %.2f %+.2f (%+.1f%%) enclosed %.2f' % (gfa, PROGRAM_GFA, gfa - PROGRAM_GFA, (gfa / PROGRAM_GFA - 1) * 100, enc))
    for fl in FLOORS:
        k = {}
        for r in FLOORS[fl]: k[r.kind] = round(k.get(r.kind, 0) + gfa_area(r), 2)
        print(fl, k)
