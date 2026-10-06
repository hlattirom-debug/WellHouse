# -*- coding: utf-8 -*-
"""WELL FORNO 30x30 — rooms. Bar 23.00 x 13.00: S bar | 3.00 m timber hall (void F2-F4) | N bar; garage in N bar F1."""
from frame6 import *

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

MAIN = 'บันไดหลัก (โถงไม้)'
def core(fl):
    return [R(MAIN, STAIR_R, 'stair'),
            R('โถงลิฟต์' + ('' if fl == 1 else ' ชั้น %d' % fl), LIFT_LOBBY, 'circ'),
            R('ลิฟต์บ้าน', LIFT, 'lift'),
            R('บันไดหนีไฟภายนอก', FSTAIR, 'fstair')]

def hall(fl):
    """void + gallery + timber bridge of the 4-storey Forno hall (F2-F4)"""
    bx0, _, bx1, _ = BRIDGE[fl]
    return [R('ช่องโล่งโถงไม้ ชั้น %d' % fl, (VOID[0], VOID[1], bx0, VOID[3]), 'void'),
            R('สะพานไม้ ชั้น %d' % fl, BRIDGE[fl], 'circ'),
            R('ช่องโล่งโถงไม้ ชั้น %d (ส่วนต่อเนื่อง)' % fl, (bx1, VOID[1], VOID[2], VOID[3]), 'void'),
            R('ทางเดินแกลเลอรี ชั้น %d' % fl, GALLERY, 'circ')]

GAR = 'โรงจอดรถ 4 คัน'
HALL1 = 'โถงกลาง "Forno hall"'
FOY = 'โถงต้อนรับ (ทางเข้าทิศตะวันออก)'
F1R = [
    R('ห้องนอนแขก/ผู้สูงอายุ', (3500, 7500, 8100, 12500), 'room'),
    R('ลานใต้ชายคา / ศาลาริมสระ', (8100, 6000, 13700, 12500), 'inb'),
    R('ครัวไทย (ครัวหนัก)', (13700, 7500, 17900, 12500), 'room'),
    R('ห้องซักรีด', (17900, 7500, 21100, 12500), 'svc'),
    R('ห้องแม่บ้าน 1', (21100, 7500, 23800, 12500), 'room'),
    R('ห้องแม่บ้าน 2', (23800, 7500, 26500, 12500), 'room'),
    R('ห้องน้ำห้องแขก', (3500, 12500, 5800, 15500), 'wet'),
    R('ตู้เสื้อผ้าห้องแขก', (5800, 12500, 8100, 15500), 'svc'),
    R(HALL1, (8100, 12500, 25000, 15500), 'circ'),
    R('ห้องน้ำแม่บ้าน', (25000, 12500, 26500, 15500), 'wet'),
    R(GAR, GARAGE, 'park'),
    R('ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ', (20300, 15500, 22700, 20500), 'svc'),
    R(FOY, (22700, 15500, 26500, 20500), 'circ'),
    *core(1),
]

F2R = [
    R('ระเบียงไม้ทิศใต้ ชั้น 2', BALC, 'inb'),
    R('ครัวโชว์ + ไอส์แลนด์', (3500, 7500, 8900, 12500), 'room'),
    R('ห้องรับประทานอาหาร', (8900, 7500, 16900, 12500), 'room'),
    R('ห้องนั่งเล่น', (16900, 7500, 26500, 12500), 'room'),
    R('Walk-in Pantry & ห้องเย็น', (3500, 12500, 8100, 15500), 'svc'),
    *hall(2),
    R('ห้องไวน์ / ซิการ์', (21200, 12500, 24400, 15500), 'svc'),
    R('ห้องน้ำแขก (Powder)', (24400, 12500, 26500, 15500), 'wet'),
    R('ห้องนอน Junior Suite 2', (3500, 15500, 7500, 20500), 'room'),
    R('ตู้เสื้อผ้า Junior Suite 2', (7500, 15500, 9900, 17900), 'svc'),
    R('ห้องน้ำ Junior Suite 2', (7500, 17900, 9900, 20500), 'wet'),
    R('ตู้เสื้อผ้า Junior Suite 3', (9900, 15500, 12300, 17900), 'svc'),
    R('ห้องน้ำ Junior Suite 3', (9900, 17900, 12300, 20500), 'wet'),
    R('ห้องนอน Junior Suite 3', (12300, 15500, 16300, 20500), 'room'),
    R('ห้องทำงาน & ห้องสมุด', OFFICE, 'room'),
    *core(2),
]

F3R = [
    R('ระเบียงไม้ทิศใต้ ชั้น 3', BALC, 'inb'),
    R('ห้องน้ำ Spa + Jacuzzi', (3500, 7500, 8900, 12500), 'wet'),
    R('Walk-in Dressing (His & Hers)', (8900, 7500, 14700, 12500), 'svc'),
    R('ห้องนอน Master Suite', (14700, 7500, 24300, 12500), 'room'),
    R('บันไดส่วนตัว Master', PSTAIR, 'stair'),
    *hall(3),
    R('ลอจเจียทิศเหนือ (ระแนงไม้)', (3500, 15500, 16300, 20500), 'inb'),
    R('ลอจเจียตะวันออกเฉียงเหนือ', (20300, 15500, 26500, 20500), 'inb'),
    *core(3),
]

CLO4 = 'Master Walk-in Closet ชั้น 4'
F4R = [
    R('ระเบียง & BBQ (ใต้ชายคา)', (3500, 6000, 12300, 12500), 'inb'),
    R('ระเบียง Master (ใต้ชายคา)', (12300, 6000, 17300, 12500), 'inb'),
    R('ระเบียง Master (ใต้ชายคา) (ส่วนต่อเนื่อง)', (17300, 6000, 26500, 7500), 'inb'),
    R(CLO4, (17300, 7500, 24300, 12500), 'svc'),
    R('บันไดส่วนตัว Master', PSTAIR, 'stair'),
    *hall(4),
    R('ห้องนั่งเล่นครอบครัว & Upper Gallery', (3500, 15500, 12500, 20500), 'room'),
    R('ห้องน้ำชั้น 4', (12500, 15500, 16300, 18000), 'wet'),
    R('ห้องอุปกรณ์ AV / เก็บของ', (12500, 18000, 16300, 20500), 'svc'),
    R('ห้องโฮมเธียเตอร์', (20300, 15500, 26500, 20500), 'room'),
    *core(4),
]

FLOORS = {1: F1R, 2: F2R, 3: F3R, 4: F4R}
for fl, L in FLOORS.items():
    for i, r in enumerate(L):
        r.fl = fl; r.code = '%d%02d' % (fl, i + 1)

NOWALL = [('ระเบียง Master (ใต้ชายคา)', 'ระเบียง Master (ใต้ชายคา) (ส่วนต่อเนื่อง)')] + [('ช่องโล่งโถงไม้ ชั้น %d' % f, 'ช่องโล่งโถงไม้ ชั้น %d (ส่วนต่อเนื่อง)' % f) for f in (2, 3, 4)]
COURTS = [('คอร์ตแสงทิศตะวันตก (เปิดฟ้า ชั้น 3-4)', COURT_W), ('คอร์ตแสงทิศตะวันออก (เปิดฟ้า ชั้น 3-4)', COURT_E)]

PROGRAM = [  # (name, program floor, area, [design rooms])
    ('Grand Double-Height Foyer', 1, 24, ['โถงต้อนรับ (ทางเข้าทิศตะวันออก)']),
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
    ('Family Lounge & Upper Gallery', 4, 36, ['ห้องนั่งเล่นครอบครัว & Upper Gallery']),
    ('Executive Home Office & Library', 2, 26, ['ห้องทำงาน & ห้องสมุด']),
    ('Master Walk-in Closet (U/L)', 4, 36, [CLO4]),
    ('Show Kitchen & Island Bar', 2, 28, ['ครัวโชว์ + ไอส์แลนด์']),
    ('Heavy Thai Kitchen', 1, 20, ['ครัวไทย (ครัวหนัก)']),
    ('Walk-in Pantry & Cold Storage', 3, 12, ['Walk-in Pantry & ห้องเย็น']),
    ('Laundry & Utility Room', 1, 16, ['ห้องซักรีด']),
    ('Maid Bedroom 1 & 2', 1, 22, ['ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2']),
    ('Maid Bathroom', 1, 6, ['ห้องน้ำแม่บ้าน']),
    ('MEP / Electrical / Generator', 1, 14, ['ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ']),
    ('Covered Garage 3-4 cars', 1, 85, [GAR]),
    ('Covered Veranda & BBQ', 4, 45, ['ระเบียง & BBQ (ใต้ชายคา)']),
    ('Upper Master Terrace', 4, 28, ['ระเบียง Master (ใต้ชายคา)', 'ระเบียง Master (ใต้ชายคา) (ส่วนต่อเนื่อง)']),
    ('Poolside Pavilion', 1, 35, ['ลานใต้ชายคา / ศาลาริมสระ']),
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
