# -*- coding: utf-8 -*-
"""WELL G-BEACH 30x30 — rooms (slab block on pilotis + cylindrical core + west brick lattice)."""
from frame4 import Y, CORE_SQ, LIFT, FSTAIR, PAVILION

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

def core(fl):
    return [R('แกนบันไดทรงกระบอก', CORE_SQ, 'core'),
            R('ลิฟต์บ้าน', LIFT, 'lift'),
            R('บันไดหนีไฟภายนอก', FSTAIR, 'fstair')]

F1R = [
    R('โรงจอดรถ 4 คัน (ใต้ Pilotis)', (5500, 20500, 20500, 26500), 'park'),
    R('ห้องแม่บ้าน 2', (5500, 4000, 10300, 6400), 'room'),
    R('ห้องแม่บ้าน 1', (5500, 6400, 7900, 11300), 'room'),
    R('ห้องน้ำแม่บ้าน', (7900, 6400, 10300, 8900), 'wet'),
    R('ทางเดินบริการ', (7900, 8900, 10300, 11300), 'circ'),
    R('ห้องซักรีด', (5500, 11300, 10300, 14700), 'svc'),
    R('ห้อง MEP / ไฟฟ้า', (5500, 14700, 10300, 17600), 'svc'),
    R('ห้องเก็บของ / คนขับรถ', (5500, 17600, 10300, 20500), 'svc'),
    R('ครัวไทย (ครัวหนัก)', (10300, 4000, 14100, 9300), 'room'),
    R('ใต้ถุน Pilotis / ลานซักล้าง', (14100, 4000, 16100, 11900), 'inb'),
    R('ใต้ถุน Pilotis / ลานซักล้าง (ส่วนต่อเนื่อง)', (10300, 9300, 14100, 11900), 'inb'),
    R('ห้องนอนแขก/ผู้สูงอายุ', (16100, 4000, 20500, 8400), 'room'),
    R('ตู้เสื้อผ้าห้องแขก', (16100, 8400, 18300, 11900), 'svc'),
    R('ห้องน้ำห้องแขก', (18300, 8400, 20500, 11900), 'wet'),
    R('โถงกลาง', (10300, 11900, 19100, 14050), 'circ'),
    R('โถงกลาง (ส่วนต่อเนื่อง)', (19100, 11900, 20500, 12450), 'circ'),
    R('ทางเดินบริการเหนือ', (10300, 14050, 11700, 20500), 'circ'),
    R('โถงต้อนรับสูง 2 ชั้น', (11700, 14050, 17300, 18350), 'circ'),
    R('โถงทางเข้า (Vestibule)', (11700, 18350, 17300, 20500), 'circ'),
    R('โถงลิฟต์', (17300, 14050, 19100, 16050), 'circ'),
    R('ห้องเก็บเสื้อโค้ท', (17300, 17850, 20500, 20500), 'svc'),
    *core(1),
]

F2R = [
    R('ครัวโชว์ + ไอส์แลนด์', (5500, 4000, 9050, 11900), 'room'),
    R('ห้องรับประทานอาหาร', (9050, 4000, 14100, 11900), 'room'),
    R('ห้องนั่งเล่น', (14100, 4000, 20500, 11900), 'room'),
    R('ระเบียงตะวันออก ชั้น 2', (20500, 4000, 21700, 11900), 'inb'),
    R('Walk-in Pantry & ห้องเย็น', (5500, 11900, 7700, 17300), 'svc'),
    R('ห้องไวน์ / ซิการ์', (7700, 11900, 10300, 17300), 'svc'),
    R('ทางเดินแกน (Spine)', (10300, 11900, 11700, 20500), 'circ'),
    R('โถงชั้น 2', (11700, 11900, 19100, 14050), 'circ'),
    R('โถงชั้น 2 (ส่วนต่อเนื่อง)', (19100, 11900, 20500, 12450), 'circ'),
    R('ช่องโล่งโถงต้อนรับ', (11700, 14050, 17300, 18350), 'void'),
    R('โถงลิฟต์ชั้น 2', (17300, 14050, 19100, 16050), 'circ'),
    R('แกลเลอรีเหนือ', (11700, 18350, 17300, 20500), 'circ'),
    R('แกลเลอรีตะวันออก', (17300, 17850, 20500, 20500), 'circ'),
    R('ห้องเก็บของ (ต่อจาก Pantry)', (5500, 17300, 7700, 19300), 'svc'),
    R('ห้องน้ำแขก (Powder)', (7700, 17300, 10300, 19300), 'wet'),
    R('ห้องน้ำ Junior Suite 2', (5500, 19300, 7700, 22300), 'wet'),
    R('ตู้เสื้อผ้า Junior Suite 2', (7700, 19300, 10300, 22300), 'svc'),
    R('ห้องนอน Junior Suite 2', (5500, 22300, 10300, 26500), 'room'),
    R('ห้องทำงาน & ห้องสมุด', (10300, 20500, 14700, 26500), 'room'),
    R('ตู้เสื้อผ้า Junior Suite 3', (14700, 20500, 18000, 22800), 'svc'),
    R('ห้องน้ำ Junior Suite 3', (18000, 20500, 20500, 22800), 'wet'),
    R('ห้องนอน Junior Suite 3', (14700, 22800, 20500, 26500), 'room'),
    *core(2),
]

F3R = [
    R('Walk-in Dressing (His & Hers)', (5500, 4000, 11000, 9800), 'svc'),
    R('บันไดส่วนตัว Master', (5500, 9800, 11000, 11900), 'stair'),
    R('ห้องน้ำ Spa + Jacuzzi', (11000, 4000, 14600, 11900), 'wet'),
    R('ห้องนอน Master Suite', (14600, 4000, 20500, 11900), 'room'),
    R('ระเบียงตะวันออก ชั้น 3', (20500, 4000, 21700, 11900), 'inb'),
    R('โถงชั้น 3', (11000, 11900, 19100, 14050), 'circ'),
    R('โถงชั้น 3 (ส่วนต่อเนื่อง)', (19100, 11900, 20500, 12450), 'circ'),
    R('ลอจเจียตะวันตก (ผนังอิฐโปร่ง)', (5500, 11900, 11000, 19300), 'inb'),
    R('ลอจเจียทิศเหนือ', (11000, 14050, 17300, 19300), 'inb'),
    R('โถงลิฟต์ชั้น 3', (17300, 14050, 19100, 16050), 'circ'),
    R('ห้องเก็บของชั้น 3', (17300, 17850, 20500, 19300), 'svc'),
    *core(3),
]

F4R = [
    R('Master Walk-in Closet ชั้น 4', (5500, 4000, 11600, 9800), 'svc'),
    R('Master Walk-in Closet ชั้น 4 (ส่วนต่อเนื่อง)', (11000, 9800, 11600, 11900), 'svc'),
    R('บันไดส่วนตัว Master', (5500, 9800, 11000, 11900), 'stair'),
    R('ระเบียง Master (ดาดฟ้า)', (11600, 4000, 15100, 11900), 'inb'),
    R('ระเบียง & BBQ (หลังคาคลุม)', (15100, 4000, 20500, 11900), 'inb'),
    R('ห้องนั่งเล่นครอบครัว & Upper Gallery', (5500, 11900, 11000, 17300), 'room'),
    R('ห้องนั่งเล่นครอบครัว & Upper Gallery (ส่วนต่อเนื่อง)', (7900, 17300, 11000, 19300), 'room'),
    R('ห้องน้ำชั้น 4', (5500, 17300, 7900, 19300), 'wet'),
    R('โถงชั้น 4', (11000, 11900, 19100, 14050), 'circ'),
    R('โถงชั้น 4 (ส่วนต่อเนื่อง)', (19100, 11900, 20500, 12450), 'circ'),
    R('ห้องโฮมเธียเตอร์', (11000, 14050, 17300, 19300), 'room'),
    R('โถงลิฟต์ชั้น 4', (17300, 14050, 19100, 16050), 'circ'),
    R('ห้องอุปกรณ์ AV / เก็บของ', (17300, 17850, 20500, 19300), 'svc'),
    *core(4),
]

FLOORS = {1: F1R, 2: F2R, 3: F3R, 4: F4R}
for fl, L in FLOORS.items():
    for i, r in enumerate(L):
        r.fl = fl; r.code = '%d%02d' % (fl, i + 1)

NOWALL = [('ใต้ถุน Pilotis / ลานซักล้าง', 'ใต้ถุน Pilotis / ลานซักล้าง (ส่วนต่อเนื่อง)'),
          ('Master Walk-in Closet ชั้น 4', 'Master Walk-in Closet ชั้น 4 (ส่วนต่อเนื่อง)'),
          ('ห้องนั่งเล่นครอบครัว & Upper Gallery', 'ห้องนั่งเล่นครอบครัว & Upper Gallery (ส่วนต่อเนื่อง)')]
for k in (1, 2, 3, 4):
    nm = {1: 'โถงกลาง', 2: 'โถงชั้น 2', 3: 'โถงชั้น 3', 4: 'โถงชั้น 4'}[k]
    NOWALL.append((nm, nm + ' (ส่วนต่อเนื่อง)'))

COURTS = []

PROGRAM = [  # (name, program floor, area, [design rooms])
    ('Grand Double-Height Foyer', 1, 24, ['โถงต้อนรับสูง 2 ชั้น']),
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
    ('Family Lounge & Upper Gallery', 4, 36, ['ห้องนั่งเล่นครอบครัว & Upper Gallery', 'ห้องนั่งเล่นครอบครัว & Upper Gallery (ส่วนต่อเนื่อง)']),
    ('Executive Home Office & Library', 2, 26, ['ห้องทำงาน & ห้องสมุด']),
    ('Master Walk-in Closet (U/L)', 4, 36, ['Master Walk-in Closet ชั้น 4', 'Master Walk-in Closet ชั้น 4 (ส่วนต่อเนื่อง)']),
    ('Show Kitchen & Island Bar', 2, 28, ['ครัวโชว์ + ไอส์แลนด์']),
    ('Heavy Thai Kitchen', 1, 20, ['ครัวไทย (ครัวหนัก)']),
    ('Walk-in Pantry & Cold Storage', 3, 12, ['Walk-in Pantry & ห้องเย็น']),
    ('Laundry & Utility Room', 1, 16, ['ห้องซักรีด']),
    ('Maid Bedroom 1 & 2', 1, 22, ['ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2']),
    ('Maid Bathroom', 1, 6, ['ห้องน้ำแม่บ้าน']),
    ('MEP / Electrical / Generator', 1, 14, ['ห้อง MEP / ไฟฟ้า']),
    ('Covered Garage 3-4 cars', 1, 85, ['โรงจอดรถ 4 คัน (ใต้ Pilotis)']),
    ('Covered Veranda & BBQ', 4, 45, ['ระเบียง & BBQ (หลังคาคลุม)']),
    ('Upper Master Terrace', 4, 28, ['ระเบียง Master (ดาดฟ้า)']),
    ('Poolside Pavilion', 1, 35, ['__PAVILION__']),
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
from frame4 import CORE_R
CORE_AREA = math.pi * (CORE_R / 1000) ** 2

def gfa_area(r):
    """area counted for GFA (cylinder counted as circle)"""
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
    # bar coverage per floor
    from frame4 import BAR, UPPER
    for fl, box in ((1, BAR), (2, BAR), (3, UPPER), (4, UPPER)):
        inside = sum(max(0, min(r.x1, box[2]) - max(r.x0, box[0])) * max(0, min(r.y1, box[3]) - max(r.y0, box[1])) for r in FLOORS[fl]) / 1e6
        print('  F%d inside block %.2f / %.2f' % (fl, inside, (box[2] - box[0]) * (box[3] - box[1]) / 1e6))
    print('tiling', 'OK' if ok else 'FAIL')
    pav = (PAVILION[2] - PAVILION[0]) * (PAVILION[3] - PAVILION[1]) / 1e6
    tp = td = 0
    for nm, pf, pa, rooms in PROGRAM:
        if rooms == ['__PAVILION__']: a, f = pav, 0
        else:
            rs = [r for r in all_rooms() if r.name in rooms]; a = sum(r.a for r in rs); f = rs[0].fl
        tp += pa; td += a
        print('%-34s F%d %6.2f  F%d %6.2f %+6.2f' % (nm, pf, pa, f, a, a - pa))
    print('NUA prog %.2f design %.2f %+.2f' % (tp, td, td - tp))
    gfa = sum(gfa_area(r) for r in all_rooms() if r.kind not in ('void',)) + pav
    enc = sum(gfa_area(r) for r in all_rooms() if r.kind not in ('void', 'inb', 'park', 'fstair'))
    print('GFA %.2f vs %.2f %+.2f (%+.1f%%) enclosed %.2f' % (gfa, PROGRAM_GFA, gfa - PROGRAM_GFA, (gfa / PROGRAM_GFA - 1) * 100, enc))
    for fl in FLOORS:
        k = {}
        for r in FLOORS[fl]: k[r.kind] = round(k.get(r.kind, 0) + gfa_area(r), 2)
        print(fl, k)
