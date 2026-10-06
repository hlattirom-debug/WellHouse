# -*- coding: utf-8 -*-
"""WELL-GENWEAVE 40x40 v3 — room rectangles (TRUNK + BRANCH plan). Design coords in local Y, converted with Y()."""
from frame3 import Y

class R:
    __slots__ = ('name', 'x0', 'y0', 'x1', 'y1', 'kind', 'fl', 'code', 'lab')
    def __init__(s, name, rc, kind, code='', lab=None):
        s.name = name; s.x0, s.y0, s.x1, s.y1 = rc[0], Y(rc[1]), rc[2], Y(rc[3]); s.kind = kind; s.code = code; s.lab = lab
    @property
    def a(s): return (s.x1 - s.x0) * (s.y1 - s.y0) / 1e6
    @property
    def w(s): return s.x1 - s.x0
    @property
    def d(s): return s.y1 - s.y0
    def rect(s): return (s.x0, s.y0, s.x1, s.y1)
    def __repr__(s): return '<%s %s %.2f>' % (s.code, s.name, s.a)

def spine(fl):
    n2 = {1: 'โถงเหนือ (เข้าลิฟต์-บันได)', 2: 'Upper Gallery (โถงชั้น 2)', 3: 'โถงบันไดชั้น 3'}[fl]
    return [
        R('ทางเดินลำต้น (Trunk)', (17200, 13200, 18600, 24000), 'circ'),
        R('โถงใต้', (18600, 13200, 23000, 15600), 'circ'),
        R('บันไดหลัก', (18600, 15600, 21200, 21000), 'stair'),
        R('ปล่องลม Termite', (21200, 15600, 23000, 18800), 'shaft'),
        R('ลิฟต์บ้าน', (21200, 18800, 23000, 21000), 'lift'),
        R(n2, (18600, 21000, 23000, 24000), 'circ'),
    ]

F1R = [
    # ---- North band (Y 24.0-31.4) ----
    R('โรงจอดรถ 4 คัน', (5800, 24000, 17200, 31400), 'park'),
    R('โถงต้อนรับสูง 2 ชั้น', (17200, 24000, 23000, 28200), 'circ'),
    R('มุขรถเทียบ (Porte-cochère)', (17200, 28200, 23000, 31400), 'inb'),
    R('ทางเดินปีกเหนือ', (23000, 24000, 34200, 25400), 'circ'),
    R('ห้องน้ำแขก (Powder)', (23000, 25400, 25800, 28000), 'wet'),
    R('ห้องเก็บจักรยาน/อุปกรณ์สวน', (23000, 28000, 25800, 31400), 'svc'),
    R('ห้องไวน์ / ซิการ์', (25800, 25400, 28200, 31400), 'svc'),
    R('ห้องโฮมเธียเตอร์', (28200, 25400, 34200, 31400), 'room'),
    # ---- West branch: service (X 5.8-13.0, Y 13.2-24.0) ----
    R('ชานบริการ/ตากผ้า', (5800, 13200, 7000, 24000), 'inb'),
    R('ห้องแม่บ้าน 1', (7000, 13200, 13000, 15400), 'room'),
    R('ห้องแม่บ้าน 2', (7000, 15400, 13000, 17600), 'room'),
    R('ห้องซักรีด', (7000, 17600, 13000, 20300), 'svc'),
    R('ห้องน้ำแม่บ้าน', (7000, 20300, 9400, 22900), 'wet'),
    R('ห้อง MEP / ไฟฟ้า', (9400, 20300, 13000, 24000), 'svc'),
    R('ห้อง MEP / ไฟฟ้า (ส่วนต่อเนื่อง)', (7000, 22900, 9400, 24000), 'svc'),
    # ---- Trunk ----
    *spine(1),
    # ---- East branch: guest (X 27.8-34.2, Y 17.4-24.0) ----
    R('ทางเดินห้องแขก', (27800, 17400, 29000, 24000), 'circ'),
    R('ห้องนอนแขก/ผู้สูงอายุ', (29000, 17400, 34200, 21600), 'room'),
    R('ห้องน้ำห้องแขก', (29000, 21600, 31800, 24000), 'wet'),
    R('ตู้เสื้อผ้าห้องแขก', (31800, 21600, 34200, 24000), 'svc'),
    # ---- South band (Y 6.0-13.2) ----
    R('ครัวไทย (ครัวหนัก)', (5800, 6000, 8600, 13200), 'room'),
    R('Walk-in Pantry/ห้องเย็น', (8600, 6000, 10300, 13200), 'svc'),
    R('ครัวโชว์ + ไอส์แลนด์', (10300, 6000, 14200, 13200), 'room'),
    R('ห้องรับประทานอาหาร', (14200, 6000, 19800, 13200), 'room'),
    R('ห้องนั่งเล่นสูง 2 ชั้น', (19800, 6000, 26800, 13200), 'room'),
    R('ระเบียงบาร์บีคิว', (26800, 6000, 34200, 10400), 'inb'),
    R('ระเบียงบาร์บีคิว (ส่วนต่อเนื่อง)', (26800, 10400, 32600, 13200), 'inb'),
    R('ห้องอาบน้ำริมสระ', (32600, 10400, 34200, 13200), 'wet'),
]

F2R = [
    R('ทางเดิน Junior Suite 2', (11200, 17400, 12400, 24000), 'circ'),
    R('ห้องนอน Junior Suite 2', (5800, 17400, 11200, 21600), 'room'),
    R('ห้องน้ำ Junior Suite 2', (5800, 21600, 8400, 24000), 'wet'),
    R('ตู้เสื้อผ้า Junior Suite 2', (8400, 21600, 11200, 24000), 'svc'),
    R('สะพานกิ่งตะวันตก', (12400, 22200, 17200, 24000), 'circ'),
    *spine(2),
    R('สะพานกิ่งตะวันออก', (23000, 22200, 27800, 24000), 'circ'),
    R('ห้องนั่งเล่นครอบครัว', (23000, 24000, 28200, 31400), 'room'),
    R('ทางเดิน Junior Suite 3', (27800, 17400, 29000, 24000), 'circ'),
    R('ห้องนอน Junior Suite 3', (29000, 17400, 34200, 21600), 'room'),
    R('ห้องน้ำ Junior Suite 3', (29000, 21600, 31800, 24000), 'wet'),
    R('ตู้เสื้อผ้า Junior Suite 3', (31800, 21600, 34200, 24000), 'svc'),
    R('ช่องโล่งโถงต้อนรับ', (17200, 24000, 23000, 28200), 'void'),
    R('ช่องโล่งห้องอาหาร', (14200, 6000, 19800, 13200), 'void'),
    R('ช่องโล่งห้องนั่งเล่น', (19800, 6000, 26800, 13200), 'void'),
]

F3R = [
    *spine(3),
    R('ห้องทำงาน & ห้องสมุด', (9400, 6000, 13600, 12000), 'room'),
    R('Walk-in Dressing (His & Hers)', (13600, 6000, 19100, 12000), 'svc'),
    R('ห้องน้ำ Spa + Jacuzzi', (19100, 6000, 23700, 12000), 'wet'),
    R('ทางเดินชั้น 3', (9400, 12000, 23700, 13200), 'circ'),
    R('ห้องนอน Master Suite', (23700, 6000, 30300, 13200), 'room'),
    R('ระเบียง Master (หลังคาคลุม)', (30300, 6000, 34200, 13200), 'inb'),
]

FLOORS = {1: F1R, 2: F2R, 3: F3R}
for fl, L in FLOORS.items():
    for i, r in enumerate(L):
        r.fl = fl; r.code = '%d%02d' % (fl, i + 1)

# same room split into two rectangles (no wall between)
NOWALL = [('ห้อง MEP / ไฟฟ้า', 'ห้อง MEP / ไฟฟ้า (ส่วนต่อเนื่อง)'),
          ('ระเบียงบาร์บีคิว', 'ระเบียงบาร์บีคิว (ส่วนต่อเนื่อง)')]

# green roofs / flat roofs at +4.20 (over F1 where nothing above) — computed in draw; courts (open to sky)
COURTS = [('คอร์ตน้ำ (Beetle Water Court)', (13000, Y(13200), 17200, Y(24000))),
          ('คอร์ตต้นไม้ (Termite Lung Court)', (23000, Y(13200), 34200, Y(17400))),
          ('คอร์ตต้นไม้ (ส่วนต่อเนื่อง)', (23000, Y(17400), 27800, Y(24000)))]

# ------------------------------------------------------------------ program (ARCHISPACE 2026-09-27)
PROGRAM = [  # (name, program floor, area, [design room names], our floor)
    ('Grand Double-Height Foyer', 1, 24, ['โถงต้อนรับสูง 2 ชั้น']),
    ('Formal Living Room', 1, 50, ['ห้องนั่งเล่นสูง 2 ชั้น']),
    ('Dining Room (10-12 Seats)', 1, 40, ['ห้องรับประทานอาหาร']),
    ('Powder Room', 1, 6, ['ห้องน้ำแขก (Powder)']),
    ('Home Theater / AV Lounge', 1, 36, ['ห้องโฮมเธียเตอร์']),
    ('Wine Cellar / Cigar Room', 1, 14, ['ห้องไวน์ / ซิการ์']),
    ('Master Suite Bedroom', 3, 48, ['ห้องนอน Master Suite']),
    ('Master Walk-in (His & Hers)', 3, 32, ['Walk-in Dressing (His & Hers)']),
    ('Spa Master Bath + Jacuzzi', 3, 28, ['ห้องน้ำ Spa + Jacuzzi']),
    ('Junior Suite 2 (bath+closet)', 2, 34, ['ห้องนอน Junior Suite 2', 'ห้องน้ำ Junior Suite 2', 'ตู้เสื้อผ้า Junior Suite 2']),
    ('Junior Suite 3 (bath+closet)', 2, 34, ['ห้องนอน Junior Suite 3', 'ห้องน้ำ Junior Suite 3', 'ตู้เสื้อผ้า Junior Suite 3']),
    ('Guest Suite (GF / elderly)', 1, 30, ['ห้องนอนแขก/ผู้สูงอายุ', 'ห้องน้ำห้องแขก', 'ตู้เสื้อผ้าห้องแขก']),
    ('Family Lounge & Upper Gallery', 2, 36, ['ห้องนั่งเล่นครอบครัว']),
    ('Executive Home Office & Library', 3, 26, ['ห้องทำงาน & ห้องสมุด']),
    ('Show Kitchen & Island Bar', 1, 28, ['ครัวโชว์ + ไอส์แลนด์']),
    ('Heavy Thai Kitchen', 1, 20, ['ครัวไทย (ครัวหนัก)']),
    ('Walk-in Pantry & Cold Storage', 1, 12, ['Walk-in Pantry/ห้องเย็น']),
    ('Laundry & Utility Room', 1, 16, ['ห้องซักรีด']),
    ('Maid Bedroom 1 & 2', 1, 22, ['ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2']),
    ('Maid Bathroom', 1, 6, ['ห้องน้ำแม่บ้าน']),
    ('MEP / Electrical / Generator', 2, 14, ['ห้อง MEP / ไฟฟ้า', 'ห้อง MEP / ไฟฟ้า (ส่วนต่อเนื่อง)']),
    ('Covered Garage 3-4 cars', 1, 85, ['โรงจอดรถ 4 คัน']),
    ('Covered Veranda & BBQ', 1, 45, ['ระเบียงบาร์บีคิว', 'ระเบียงบาร์บีคิว (ส่วนต่อเนื่อง)']),
    ('Upper Master Terrace', 2, 28, ['ระเบียง Master (หลังคาคลุม)']),
    ('Poolside Pavilion', 1, 35, ['__PAVILION__']),
]
PROGRAM_NUA, PROGRAM_GFA = 749.00, 939.55

def all_rooms():
    return [r for fl in (1, 2, 3) for r in FLOORS[fl]]

def find(name, fl=None):
    for r in all_rooms():
        if r.name == name and (fl is None or r.fl == fl):
            return r
    raise KeyError(name)

# ------------------------------------------------------------------ checks
if __name__ == '__main__':
    import numpy as np
    from frame3 import PAVILION
    step = 100
    ok = True
    for fl, L in FLOORS.items():
        xs = [v for r in L for v in (r.x0, r.x1)]; ys = [v for r in L for v in (r.y0, r.y1)]
        X0, Y0 = min(xs), min(ys); X1, Y1 = max(xs), max(ys)
        g = np.zeros(((Y1 - Y0) // step, (X1 - X0) // step), np.int16)
        for r in L:
            g[(r.y0 - Y0) // step:(r.y1 - Y0) // step, (r.x0 - X0) // step:(r.x1 - X0) // step] += 1
        ov = (g > 1).sum()
        tot = sum(r.a for r in L)
        cov = (g > 0).sum() * step * step / 1e6
        print('F%d rooms %d  sum %.2f  union %.2f  overlap cells %d' % (fl, len(L), tot, cov, ov))
        if ov or abs(tot - cov) > 0.01:
            ok = False
            for i, a in enumerate(L):
                for b in L[i + 1:]:
                    if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1:
                        print('   OVERLAP', a, b)
    print('tiling', 'OK' if ok else 'FAIL')
    # areas by kind
    for fl, L in FLOORS.items():
        k = {}
        for r in L: k[r.kind] = k.get(r.kind, 0) + r.a
        print('F%d' % fl, {a: round(b, 2) for a, b in k.items()})
    # program comparison
    pav = (PAVILION[2] - PAVILION[0]) * (PAVILION[3] - PAVILION[1]) / 1e6
    tp = td = 0
    for nm, pf, pa, rooms in PROGRAM:
        if rooms == ['__PAVILION__']: a = pav; f = 0
        else:
            rs = [r for r in all_rooms() if r.name in rooms]; a = sum(r.a for r in rs); f = rs[0].fl
        tp += pa; td += a
        print('%-36s prog F%d %6.2f  design F%d %6.2f  %+6.2f' % (nm, pf, pa, f, a, a - pa))
    print('NUA program %.2f design %.2f %+.2f' % (tp, td, td - tp))
    gfa = sum(r.a for r in all_rooms() if r.kind not in ('void',)) + pav
    gfa_enc = sum(r.a for r in all_rooms() if r.kind not in ('void', 'inb', 'park'))
    # shaft counted on each floor (it's a vertical duct) -> keep
    print('GFA (incl. semi-outdoor, garage, pavilion) %.2f  vs program %.2f  %+.2f (%+.1f%%)' % (gfa, PROGRAM_GFA, gfa - PROGRAM_GFA, (gfa / PROGRAM_GFA - 1) * 100))
    print('enclosed GFA %.2f' % gfa_enc)
