# -*- coding: utf-8 -*-
"""WELL KILN 30x30 — rooms. E-W block 23.00 x 12.00 + north wing (garage / link / brick dome foyer) + brick stair tower (chimney)."""
from frame5 import Y, DOME_SQ, LIFT, LIFT_LOBBY, STAIR_R, FSTAIR, GARAGE, LINK, OFFICE, PAVILION

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

MAIN = 'บันไดหลัก (ปล่องเตาเผา)'
def tower(fl):
    return [R(MAIN, STAIR_R, 'stair'),
            R('โถงลิฟต์' + ('' if fl == 1 else ' ชั้น %d' % fl), LIFT_LOBBY, 'circ'),
            R('ลิฟต์บ้าน', LIFT, 'lift'),
            R('บันไดหนีไฟภายนอก', FSTAIR, 'fstair')]

DOME = 'โถงต้อนรับโดมอิฐ (เตาเผา)'
GAR = 'โรงจอดรถ 4 คัน'
F1R = [
    R('ครัวไทย (ครัวหนัก)', (3500, 7500, 7400, 12600), 'room'),
    R('ห้องแม่บ้าน 2', (3500, 12600, 7400, 15500), 'room'),
    R('ห้องน้ำแม่บ้าน', (3500, 15500, 7400, 17000), 'wet'),
    R('ห้องแม่บ้าน 1', (3500, 17000, 7400, 19500), 'room'),
    R('ทางลมบริการ (เหนือ-ใต้)', (7400, 7500, 9000, 19500), 'circ'),
    R('ลานใต้ถุน / ศาลาริมสระ', (9000, 7500, 21900, 12000), 'inb'),
    R('ห้องซักรีด', (9000, 12000, 13100, 15300), 'svc'),
    R('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ', (9000, 15300, 13100, 19500), 'svc'),
    R('โถงกลาง', (13100, 12000, 21900, 14900), 'circ'),
    R('โถงทางเข้า (หลังโดม)', (17100, 14900, 21900, 19500), 'circ'),
    R('ห้องนอนแขก/ผู้สูงอายุ', (21900, 7500, 26500, 12000), 'room'),
    R('ตู้เสื้อผ้าห้องแขก', (21900, 12000, 24200, 14900), 'svc'),
    R('ห้องน้ำห้องแขก', (24200, 12000, 26500, 14900), 'wet'),
    R('ห้องเก็บเสื้อโค้ท', (21900, 14900, 26500, 17000), 'svc'),
    R('ห้องเก็บของ / จักรยาน', (21900, 17000, 26500, 19500), 'svc'),
    R(GAR, GARAGE, 'park'),
    R('โถงพักคอย (จากโรงรถ)', LINK, 'circ'),
    R(DOME, DOME_SQ, 'core'),
    *tower(1),
]

F2R = [
    R('ครัวโชว์ + ไอส์แลนด์', (3500, 7500, 8300, 13300), 'room'),
    R('ห้องรับประทานอาหาร', (8300, 7500, 15200, 13300), 'room'),
    R('ห้องนั่งเล่น', (15200, 7500, 23800, 13300), 'room'),
    R('ระเบียงตะวันออกเฉียงใต้ ชั้น 2', (23800, 7500, 26500, 13300), 'inb'),
    R('Walk-in Pantry & ห้องเย็น', (3500, 13300, 8300, 15300), 'svc'),
    R('ทางเดินชั้น 2 ตะวันตก', (8300, 13300, 13100, 15300), 'circ'),
    R('โถงบันได ชั้น 2', (13100, 13300, 17100, 14900), 'circ'),
    R('ทางเดินชั้น 2 ตะวันออก', (17100, 13300, 24000, 15300), 'circ'),
    R('ห้องน้ำแขก (Powder)', (24000, 13300, 26500, 15300), 'wet'),
    R('ห้องนอน Junior Suite 2', (3500, 15300, 8300, 19500), 'room'),
    R('ตู้เสื้อผ้า Junior Suite 2', (8300, 15300, 10700, 17400), 'svc'),
    R('ห้องน้ำ Junior Suite 2', (8300, 17400, 10700, 19500), 'wet'),
    R('แกลเลอรีหนังสือ', (10700, 15300, 13100, 19500), 'circ'),
    R('ห้องไวน์ / ซิการ์', (17100, 15300, 19300, 19500), 'svc'),
    R('ตู้เสื้อผ้า Junior Suite 3', (19300, 15300, 21700, 17400), 'svc'),
    R('ห้องน้ำ Junior Suite 3', (19300, 17400, 21700, 19500), 'wet'),
    R('ห้องนอน Junior Suite 3', (21700, 15300, 26500, 19500), 'room'),
    R('ห้องทำงาน & ห้องสมุด', OFFICE, 'room'),
    *tower(2),
]

F3R = [
    R('Walk-in Dressing (His & Hers)', (3500, 7500, 9500, 13300), 'svc'),
    R('ห้องน้ำ Spa + Jacuzzi', (9500, 7500, 14300, 13300), 'wet'),
    R('ห้องนอน Master Suite', (14300, 7500, 22600, 13300), 'room'),
    R('ระเบียง Master ชั้น 3', (22600, 7500, 26500, 13300), 'inb'),
    R('บันไดส่วนตัว Master', (3500, 13300, 8300, 15500), 'stair'),
    R('ห้องเก็บของชั้น 3', (8300, 13300, 13100, 15500), 'svc'),
    R('โถงบันได ชั้น 3', (13100, 13300, 17100, 14900), 'circ'),
    R('ลอจเจียทิศเหนือ (ฉากกระจก U)', (17100, 13300, 26500, 19500), 'inb'),
    *tower(3),
]

F4R = [
    R('Master Walk-in Closet ชั้น 4', (3500, 7500, 9500, 13300), 'svc'),
    R('ระเบียง Master (ดาดฟ้า)', (9500, 7500, 14300, 13300), 'inb'),
    R('ห้องนั่งเล่นครอบครัว (หลังคาโค้ง)', (14300, 7500, 19700, 13300), 'room'),
    R('ระเบียง & BBQ (หลังคาคลุม)', (19700, 7500, 26500, 13300), 'inb'),
    R('บันไดส่วนตัว Master', (3500, 13300, 8300, 15500), 'stair'),
    R('ห้องอุปกรณ์ AV / เก็บของ', (8300, 13300, 13100, 15500), 'svc'),
    R('โถงบันได ชั้น 4', (13100, 13300, 17100, 14900), 'circ'),
    R('ทางเดินชั้น 4', (17100, 13300, 24000, 15300), 'circ'),
    R('ห้องน้ำชั้น 4', (24000, 13300, 26500, 15300), 'wet'),
    R('ห้องโฮมเธียเตอร์', (17100, 15300, 26500, 19500), 'room'),
    *tower(4),
]

FLOORS = {1: F1R, 2: F2R, 3: F3R, 4: F4R}
for fl, L in FLOORS.items():
    for i, r in enumerate(L):
        r.fl = fl; r.code = '%d%02d' % (fl, i + 1)

NOWALL = []
COURTS = []

PROGRAM = [  # (name, program floor, area, [design rooms])
    ('Grand Double-Height Foyer', 1, 24, [DOME]),
    ('Formal Living Room', 2, 50, ['ห้องนั่งเล่น']),
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
    ('Family Lounge & Upper Gallery', 4, 36, ['ห้องนั่งเล่นครอบครัว (หลังคาโค้ง)']),
    ('Executive Home Office & Library', 2, 26, ['ห้องทำงาน & ห้องสมุด']),
    ('Master Walk-in Closet (U/L)', 4, 36, ['Master Walk-in Closet ชั้น 4']),
    ('Show Kitchen & Island Bar', 2, 28, ['ครัวโชว์ + ไอส์แลนด์']),
    ('Heavy Thai Kitchen', 1, 20, ['ครัวไทย (ครัวหนัก)']),
    ('Walk-in Pantry & Cold Storage', 3, 12, ['Walk-in Pantry & ห้องเย็น']),
    ('Laundry & Utility Room', 1, 16, ['ห้องซักรีด']),
    ('Maid Bedroom 1 & 2', 1, 22, ['ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2']),
    ('Maid Bathroom', 1, 6, ['ห้องน้ำแม่บ้าน']),
    ('MEP / Electrical / Generator', 1, 14, ['ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ']),
    ('Covered Garage 3-4 cars', 1, 85, [GAR]),
    ('Covered Veranda & BBQ', 4, 45, ['ระเบียง & BBQ (หลังคาคลุม)']),
    ('Upper Master Terrace', 4, 28, ['ระเบียง Master (ดาดฟ้า)']),
    ('Poolside Pavilion', 1, 35, ['ลานใต้ถุน / ศาลาริมสระ']),
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
from frame5 import DOME_R
CORE_AREA = math.pi * (DOME_R / 1000) ** 2

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
