# -*- coding: utf-8 -*-
"""Wall engine: edges -> overlaps -> wall segments; Dijkstra door tree; windows; rails."""
import heapq
from plan7 import FLOORS, NOWALL, find

T_EXT, T_INT, T_WET = 200, 120, 150

class Seg:
    __slots__ = ('fl', 'a', 'b', 'o', 'c', 'lo', 'hi', 'out', 'wt', 'th', 'id')
    def __init__(s, fl, a, b, o, c, lo, hi, out=0):
        s.fl, s.a, s.b, s.o, s.c, s.lo, s.hi, s.out = fl, a, b, o, c, lo, hi, out
        s.wt = None; s.th = 0; s.id = None
    @property
    def L(s): return s.hi - s.lo
    def pt(s, t):  # point at coordinate t along seg
        return (t, s.c) if s.o == 'H' else (s.c, t)
    def __repr__(s):
        return '<Seg F%d %s %s|%s %s=%d %d-%d %s>' % (s.fl, s.o, s.a.name, s.b.name if s.b else 'EXT', 'y' if s.o == 'H' else 'x', s.c, s.lo, s.hi, s.wt)

class Op:
    __slots__ = ('fl', 'seg', 't', 'w', 'kind', 'sill', 'head', 'tag', 'into', 'hinge', 'room')
    def __init__(s, fl, seg, t, w, kind, sill=0, head=2400, into=None, hinge=-1, room=None):
        s.fl, s.seg, s.t, s.w, s.kind, s.sill, s.head = fl, seg, t, w, kind, sill, head
        s.into = into; s.hinge = hinge; s.tag = ''; s.room = room
    @property
    def lo(s): return s.t - s.w / 2
    @property
    def hi(s): return s.t + s.w / 2

def _sub(iv, cuts):
    res = [iv]
    for a, b in cuts:
        nr = []
        for x, y in res:
            if b <= x or a >= y: nr.append((x, y)); continue
            if a > x: nr.append((x, a))
            if b < y: nr.append((b, y))
        res = nr
    return [r for r in res if r[1] - r[0] > 1]

def sides(r):
    return [('H', r.y0, r.x0, r.x1, -1), ('H', r.y1, r.x0, r.x1, +1), ('V', r.x0, r.y0, r.y1, -1), ('V', r.x1, r.y0, r.y1, +1)]

def edges(fl):
    L = FLOORS[fl]
    pairs, ext = [], []
    for r in L:
        for o, c, lo, hi, out in sides(r):
            shared = []
            for q in L:
                if q is r: continue
                for o2, c2, lo2, hi2, out2 in sides(q):
                    if o2 == o and c2 == c and out2 == -out:
                        a, b = max(lo, lo2), min(hi, hi2)
                        if b - a > 1:
                            shared.append((a, b))
                            if r.code < q.code:
                                pairs.append(Seg(fl, r, q, o, c, a, b, out))
            for a, b in _sub((lo, hi), shared):
                ext.append(Seg(fl, r, None, o, c, a, b, out))
    return pairs, ext

NOWALL_SET = {frozenset(p) for p in NOWALL}
CIRC = {'circ', 'stair'}
MAIN = 'บันไดหลัก (เกลียวใน)'
TOWER_N = {'ลิฟต์บ้าน'}
from frame7 import XB, XC, YC, YD

def on_court(s):
    if s.b is not None: return False
    if s.o == 'H': return s.c in (YC, YD) and XB - 1 <= s.lo and s.hi <= XC + 1
    return s.c in (XB, XC) and YC - 1 <= s.lo and s.hi <= YD + 1

def wall_rule(s):
    a, b = s.a, s.b
    if b is None:
        k = a.kind
        if k == 'park': return 'none'
        if k == 'inb': return 'none' if s.fl == 1 else 'rail'
        return 'ext'
    if frozenset((a.name, b.name)) in NOWALL_SET: return 'none'
    S = {a.kind, b.kind}
    if S <= {'void'}: return 'none'
    if 'void' in S:
        other = b if a.kind == 'void' else a
        return 'rail' if other.kind == 'circ' else 'ext'
    if 'lift' in S:
        other = b if a.kind == 'lift' else a
        return 'int' if other.kind == 'circ' else 'ext'
    if S <= CIRC: return 'none'
    if S <= {'inb'}: return 'none'
    if 'inb' in S or 'park' in S: return 'ext'
    if 'stair' in S: return 'ext'
    if 'wet' in S: return 'wet'
    return 'int'

def _match(s, n1, n2):
    A = s.a.name; B = s.b.name if s.b else 'EXT'
    return (A == n1 and B == n2) or (A == n2 and B == n1)

GAR = 'โรงจอดรถ 4 คัน'
FOY = 'โถงต้อนรับใต้โค้งอิฐ (สูง 2 ชั้น)'
PAV = 'ศาลาริมสระ (ทะลุคอร์ต)'
WH = 'โถงทางเดินริมคอร์ต (ตะวันตก)'
EH = 'โถงบริการ (ตะวันออก)'
PS = 'บันไดส่วนตัว Master'
CLO4 = 'Master Walk-in Closet ชั้น 4'
GAL = {1: 'แกลเลอรีริมคอร์ต ชั้น 1', 2: 'แกลเลอรีริมคอร์ต ชั้น 2', 3: 'แกลเลอรีริมคอร์ต ชั้น 3', 4: 'Upper Gallery (โถงบันได ชั้น 4)'}
GYM = 'ห้องฟิตเนส / โยคะ ริมสระ'
EQ = 'ห้องเครื่องสระ / เก็บของ'
MB = 'ห้องนอน Master Suite'
MH = 'โถงห้อง Master'
WI = 'Walk-in Dressing (His & Hers)'
SPA = 'ห้องน้ำ Spa + Jacuzzi'
LOGE = 'ลอจเจียตะวันออก (ใต้ลาน BBQ)'
BBQ = 'ลาน BBQ บนหลังคา (pergola)'
TER = 'ระเบียง Master (ในร่ม)'
LNG = 'ห้องนั่งเล่นครอบครัว'
THE = 'ห้องโฮมเธียเตอร์'
VOIDF = 'ช่องโล่งโถงต้อนรับ (โค้งอิฐ)'
EG2 = 'ทางเดินริมคอร์ต (ตะวันออก) ชั้น 2'
NG2 = 'ทางเดินริมคอร์ต (เหนือ) ชั้น 2'
FORCE = [  # (fl, room, other|'EXT', side or None, wall type)
    (1, GAR, 'EXT', 'S', 'ext'),
    (2, 'ครัวโชว์ + ไอส์แลนด์', 'ห้องรับประทานอาหาร', None, 'none'),
    (3, MH, GAL[3], None, 'int'),
    (3, LOGE, 'EXT', 'N', 'none'),
]

def side_of(s):
    if s.o == 'H': return 'N' if s.out > 0 else 'S'
    return 'E' if s.out > 0 else 'W'

def apply_force(segs):
    for s in segs:
        for fl, n1, n2, sd, wt in FORCE:
            if s.fl != fl: continue
            if n2 == 'EXT':
                if s.b is None and s.a.name == n1 and (sd is None or side_of(s) == sd): s.wt = wt
            elif s.b is not None and _match(s, n1, n2):
                s.wt = wt

COST = {'circ': 0, 'stair': 0, 'core': 0, 'inb': 1, 'park': 2, 'room': 4, 'svc': 6, 'wet': 12, 'lift': 50, 'fstair': 60}
ROOT = {1: [FOY], 2: [MAIN], 3: [MAIN], 4: [MAIN, PS]}
NODOOR = [
    (1, PAV, MAIN), (1, MAIN, 'ห้องเก็บของ / อุปกรณ์สระ'), (2, MAIN, 'ห้องน้ำแขก (Powder)'), (3, MAIN, 'ห้องเก็บของชั้น 3'), (4, MAIN, 'ห้องน้ำชั้น 4'), (1, 'ห้องซักรีด', 'ห้องนอนแขก/ผู้สูงอายุ'), (1, 'ห้องน้ำห้องแขก', 'ตู้เสื้อผ้าห้องแขก'), (1, 'ห้องน้ำห้องแขก', WH),
    (1, 'ตู้เสื้อผ้าห้องแขก', WH), (1, 'ตู้เสื้อผ้าห้องแขก', FOY), (1, 'ห้องน้ำห้องแขก', FOY), (1, EH, GYM), (1, 'ห้องน้ำแม่บ้าน', EQ),
    (1, 'ห้องแม่บ้าน 1', 'ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ'), (1, 'ห้องแม่บ้าน 1', 'ห้องแม่บ้าน 2'), (1, 'ห้องแม่บ้าน 2', 'ห้องน้ำแม่บ้าน'),
    (1, 'ห้องเก็บของ / อุปกรณ์สระ', MAIN), (1, 'ห้องซักรีด', PAV), (1, 'ครัวไทย (ครัวหนัก)', 'ห้องซักรีด'),
    (2, 'Walk-in Pantry & ห้องเย็น', 'ห้องรับประทานอาหาร'), (2, 'ห้องน้ำ Junior Suite 3', EG2), (2, 'ตู้เสื้อผ้า Junior Suite 3', 'ห้องทำงาน & ห้องสมุด'),
    (2, 'ห้องน้ำ Junior Suite 3', 'ห้องทำงาน & ห้องสมุด'), (2, 'ตู้เสื้อผ้า Junior Suite 2', NG2), (2, 'ห้องน้ำ Junior Suite 2', 'ห้องนอน Junior Suite 2'),
    (2, 'ห้องไวน์ / ซิการ์', 'ห้องนอน Junior Suite 2'), (2, 'ห้องเก็บของชั้น 2', 'ห้องนอน Junior Suite 3'), (2, 'ห้องเก็บของชั้น 2', 'ห้องไวน์ / ซิการ์'),
    (2, 'ห้องนั่งเล่น (ส่วนต่อเนื่อง)', 'ห้องทำงาน & ห้องสมุด'), (2, 'ห้องนั่งเล่น', 'ห้องทำงาน & ห้องสมุด'), (2, 'ห้องรับประทานอาหาร', MAIN),
    (3, MB, PS), (3, SPA, GAL[3]), (3, SPA, LOGE), (3, MB, MAIN), (3, MH, MAIN),
    (4, CLO4 + ' (ส่วนต่อเนื่อง)', GAL[4]), (4, TER, PS), (4, LNG, THE), (4, THE, BBQ), (4, CLO4, PS),
]
NOWALL_PAIRS_EXTRA = []
DPOS = {(1, 'ห้องแม่บ้าน 1'): 0.5, (1, 'ห้องแม่บ้าน 2'): 0.5, (1, 'ห้องน้ำแม่บ้าน'): 0.5, (1, 'ห้องนอนแขก/ผู้สูงอายุ'): 0.5,
        (1, 'ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ'): 0.5, (2, 'ห้องทำงาน & ห้องสมุด'): 0.6, (2, 'ห้องนอน Junior Suite 3'): 0.5,
        (2, 'ห้องไวน์ / ซิการ์'): 0.5, (2, 'ห้องเก็บของชั้น 2'): 0.5, (4, THE): 0.5, (1, 'ครัวไทย (ครัวหนัก)'): 0.5}

# forced openings: (fl, room, other|'EXT', side, frac, width, kind, sill, head)
XDOOR = [(f, 'ลิฟต์บ้าน', GAL[f], None, 0.5, 900, 'lift', 0, 2100) for f in (1, 2, 3, 4)] + [
    # F1
    (1, FOY, 'EXT', 'N', 0.5, 1800, 'door2', 0, 2700),
    (1, FOY, GAR, None, 0.5, 900, 'door', 0, 2400),
    (1, WH, PAV, None, 0.5, 1600, 'slide', 0, 2700),
    (1, PAV, GAL[1], None, 0.5, 1200, 'slide', 0, 2700),
    (1, 'ห้องนอนแขก/ผู้สูงอายุ', 'ห้องน้ำห้องแขก', None, 0.3, 900, 'slide1', 0, 2100),
    (1, 'ห้องนอนแขก/ผู้สูงอายุ', 'ตู้เสื้อผ้าห้องแขก', None, 0.5, 900, 'door', 0, 2100),
    (1, 'ครัวไทย (ครัวหนัก)', 'EXT', 'W', 0.5, 900, 'door', 0, 2100),
    (1, 'ห้องซักรีด', 'EXT', 'W', 0.5, 900, 'door', 0, 2100),
    (1, 'ห้องซักรีด', 'ครัวไทย (ครัวหนัก)', None, 0.5, 900, 'door', 0, 2100),
    (1, GYM, GAL[1], None, 0.5, 1800, 'slide', 0, 2700),
    (1, GYM, 'EXT', 'S', 0.5, 3600, 'slide', 0, 2700),
    (1, GYM, EQ, None, 0.5, 900, 'door', 0, 2100),
    (1, GYM, 'ห้องเก็บของ / อุปกรณ์สระ', None, 0.3, 800, 'door', 0, 2100),
    (1, EQ, 'EXT', 'E', 0.5, 900, 'door', 0, 2100),
    (1, EH, GAR, None, 0.5, 900, 'door', 0, 2400),
    (1, 'ห้อง MEP / ไฟฟ้า / เครื่องปั่นไฟ', 'EXT', 'E', 0.5, 1200, 'door2', 0, 2100),
    (1, 'ห้องนอนแขก/ผู้สูงอายุ', 'EXT', 'W', 0.5, 2400, 'win', 600, 2400),
    # F2
    (2, 'ห้องรับประทานอาหาร', GAL[2], None, 0.5, 1200, 'open', 0, 2700),
    (2, 'ห้องรับประทานอาหาร', 'EXT', 'N', 0.13, 1500, 'slide', 0, 2700),
    (2, 'ครัวโชว์ + ไอส์แลนด์', 'Walk-in Pantry & ห้องเย็น', None, 0.5, 900, 'door', 0, 2100),
    (2, 'ห้องนั่งเล่น', GAL[2], None, 0.5, 2400, 'open', 0, 2700),
    (2, 'ห้องน้ำแขก (Powder)', 'ห้องนั่งเล่น', None, 0.5, 800, 'door', 0, 2100),
    (2, 'ห้องนั่งเล่น', 'EXT', 'S', 0.5, 4200, 'slide', 0, 2700),
    (2, 'ห้องรับประทานอาหาร', 'EXT', 'S', 0.5, 3600, 'slide', 0, 2700),
    (2, 'ห้องนอน Junior Suite 3', 'ห้องน้ำ Junior Suite 3', None, 0.5, 800, 'door', 0, 2100),
    (2, 'ห้องนอน Junior Suite 3', 'ตู้เสื้อผ้า Junior Suite 3', None, 0.5, 800, 'door', 0, 2100),
    (2, 'ห้องนอน Junior Suite 2', 'ตู้เสื้อผ้า Junior Suite 2', None, 0.5, 800, 'door', 0, 2100),
    (2, 'ตู้เสื้อผ้า Junior Suite 2', 'ห้องน้ำ Junior Suite 2', None, 0.5, 800, 'door', 0, 2100),
    (2, VOIDF, 'EXT', 'W', 0.5, 3600, 'win', 300, 1700),
    (2, VOIDF, 'EXT', 'N', 0.5, 3000, 'win', 300, 1700),
    # F3
    (3, MB, MH, None, 0.5, 1000, 'door', 0, 2400),
    (3, MH, GAL[3], None, 0.5, 1000, 'door', 0, 2400),
    (3, WI, GAL[3], None, 0.3, 900, 'door', 0, 2400),
    (3, WI, SPA, None, 0.5, 900, 'slide1', 0, 2400),
    (3, WI, 'ห้องเก็บของชั้น 3', None, 0.5, 800, 'door', 0, 2100),
    (3, LOGE, GAL[3], None, 0.5, 1200, 'slide', 0, 2700),
    (3, MB, 'EXT', 'S', 0.5, 4200, 'slide', 0, 2700),
    # F4
    (4, PS, CLO4 + ' (ส่วนต่อเนื่อง)', None, 0.5, 1000, 'open', 0, 2400),
    (4, CLO4, TER, None, 0.5, 2400, 'slide', 0, 2700),
    (4, LNG, GAL[4], None, 0.5, 2400, 'open', 0, 2700),
    (4, 'ห้องน้ำชั้น 4', LNG, None, 0.5, 800, 'door', 0, 2100),
    (4, BBQ, GAL[4], None, 0.5, 1200, 'slide', 0, 2700),
    (4, LNG, 'EXT', 'S', 0.5, 3000, 'slide', 0, 2700),
]
NOWIN = [(f, 'ลิฟต์บ้าน') for f in (1, 2, 3, 4)] + [(2, 'ห้องไวน์ / ซิการ์'), (2, VOIDF)]
NORAIL = []
NOWINSIDE = [(3, 'Walk-in Dressing (His & Hers)', 'S'), (4, 'ห้องโฮมเธียเตอร์', 'N')]

def build(fl):
    pairs, ext = edges(fl)
    segs = pairs + ext
    for s in segs:
        s.wt = wall_rule(s)
    apply_force(segs)
    for s in segs:
        s.th = {'ext': T_EXT, 'int': T_INT, 'wet': T_WET, 'rail': 50, 'none': 0}[s.wt]
    for i, s in enumerate(segs): s.id = i
    ops = []
    nodoor = {frozenset((a, b)) for f, a, b in NODOOR if f == fl}
    # forced openings first
    used = {}
    for f, n1, n2, sd, frac, w, kind, sill, head in XDOOR:
        if f != fl: continue
        cand = []
        for s in segs:
            if n2 == 'EXT':
                if s.b is None and s.a.name == n1 and side_of(s) == sd: cand.append(s)
            elif s.b is not None and _match(s, n1, n2): cand.append(s)
        if not cand:
            raise SystemExit('XDOOR no seg: %s %s %s' % (fl, n1, n2))
        s = max(cand, key=lambda q: q.L)
        if w > s.L - 300: w = s.L - 300
        t = s.lo + frac * s.L
        t = min(max(t, s.lo + w / 2 + 150), s.hi - w / 2 - 150)
        into = find(n1, fl) if (n2 == 'EXT' or kind in ('open',)) else (find(n2, fl) if n2 != 'EXT' else None)
        op = Op(fl, s, t, w, kind, sill, head, into=find(n1, fl), room=find(n1, fl))
        if s.wt == 'none' and kind != 'open': s.wt = 'ext' if s.b is None or 'inb' in {s.a.kind, s.b.kind} else 'int'; s.th = T_EXT if s.wt == 'ext' else T_INT
        ops.append(op)
        if s.b is not None: used[frozenset((s.a.name, s.b.name))] = True
    # Dijkstra door tree
    L = [r for r in FLOORS[fl] if r.kind not in ('void', 'shaft')]
    adj = {r.name: [] for r in L}
    for s in pairs:
        if s.a.kind in ('void', 'shaft') or s.b.kind in ('void', 'shaft'): continue
        if s.wt == 'rail': continue
        if s.wt == 'ext' and ({s.a.name, s.b.name} & TOWER_N): continue     # no doors through the brick chimney walls
        if s.L < 1000 and s.wt != 'none': continue
        adj[s.a.name].append((s.b, s)); adj[s.b.name].append((s.a, s))
    for o in ops:
        s = o.seg
        if s.b is not None and s.a.name in adj and s.b.name in adj:
            adj[s.a.name].append((s.b, s)); adj[s.b.name].append((s.a, s))
    xd = {frozenset((o.seg.a.name, o.seg.b.name)) for o in ops if o.seg.b is not None}
    roots = ROOT[fl]
    root = roots[0]
    dist = {r_: 0 for r_ in roots}; par = {}
    pq = [(0, r_) for r_ in roots]
    rk = {r.name: r for r in L}
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist.get(n, 1e18): continue
        for q, s in adj[n]:
            pk = frozenset((n, q.name))
            isx = pk in xd
            if pk in nodoor and s.wt != 'none' and not isx:
                continue
            # rooms are leaves: do not route THROUGH room/wet/svc (except via 'none' joins or forced openings)
            if rk[n].kind in ('room', 'wet', 'svc', 'lift', 'fstair') and n not in roots and s.wt != 'none' and not isx:
                continue
            nd = d + COST[q.kind] + (0 if (s.wt == 'none' or isx) else 1)
            if nd < dist.get(q.name, 1e18):
                dist[q.name] = nd; par[q.name] = (n, s); heapq.heappush(pq, (nd, q.name))
    unreached = [r.name for r in L if r.name not in dist and not (r.kind == 'fstair' and fl == 1)]
    for child, (pn, s) in par.items():
        if s.wt == 'none': continue
        if frozenset((child, pn)) in used: continue
        ck = rk[child].kind
        w = {'room': 900, 'wet': 800, 'svc': 800, 'circ': 900, 'park': 900, 'inb': 900, 'lift': 900, 'stair': 900, 'core': 900, 'fstair': 900}[ck]
        if ck == 'lift': kind = 'lift'
        else: kind = 'door'
        # position: near the end of seg furthest from the other room's centre? use 600 from lo end by default
        t = s.lo + w / 2 + 250
        if s.L > 3000: t = s.lo + w / 2 + 450
        fr = DPOS.get((fl, child))
        if fr is not None:
            t = min(max(s.lo + fr * s.L, s.lo + w / 2 + 150), s.hi - w / 2 - 150)
        op = Op(fl, s, t, w, kind, 0, 2100 if ck in ('wet', 'svc') else 2400, into=rk[child], room=rk[child])
        ops.append(op)
    return segs, ops, unreached

def win_side(s):
    """(room that receives the opening, other-side kind) for an 'ext' segment, else (None, None)"""
    if s.wt != 'ext': return None, None
    if s.b is None: return s.a, 'EXT'
    ka, kb = s.a.kind, s.b.kind
    for r, q in ((s.a, s.b), (s.b, s.a)):
        if q.kind in ('inb', 'void') and r.kind not in ('inb', 'void', 'park', 'fstair', 'lift'):
            return r, q.kind
    return None, None

def add_windows(fl, segs, ops):
    nowin = {n for f, n in NOWIN if f == fl}
    for s in segs:
        r, ok = win_side(s)
        if r is None or r.name in nowin: continue
        rs = ('N' if s.c >= r.y1 else 'S') if s.o == 'H' else ('E' if s.c >= r.x1 else 'W')
        if (fl, r.name, rs) in NOWINSIDE: continue
        taken = [(o.lo - 200, o.hi + 200) for o in ops if o.seg is s]
        mg = 150 if s.L < 2000 else 300
        free = _sub((s.lo + mg, s.hi - mg), taken)
        court = on_court(s)
        for a, b in free:
            Lf = b - a
            k = r.kind
            if court and k in ('room', 'circ') and Lf >= 900:
                ops.append(Op(fl, s, (a + b) / 2, Lf, 'glass', 0, 2700, into=r, room=r)); continue
            if k == 'room':
                if Lf < 900: continue
                w = min(Lf, max(900, round(Lf * 0.72 / 300) * 300))
                kind, sill, head = 'win', 600, 2400
                if ok == 'void': kind, sill, head = 'win', 900, 2700
                if ok == 'inb': w, kind, sill, head = Lf, 'glass', 0, 2700      # FORNO: full-height glazing behind the timber balcony layer
            elif k == 'void':
                if Lf < 900: continue
                w = Lf; kind, sill, head = 'glass', 0, 3000
            elif k == 'wet':
                if Lf < 700: continue
                w = min(Lf, 1200 if Lf >= 1500 else 600); kind, sill, head = 'win', 1500, 2100
            elif k == 'svc':
                if Lf < 900: continue
                w = min(Lf, 1200); kind, sill, head = 'win', 1500, 2100
            elif k == 'circ':
                if Lf < 900: continue
                w = Lf; kind, sill, head = 'glass', 0, 2700
            elif k == 'stair':
                if Lf < 900: continue
                w = Lf; kind, sill, head = 'glass', 0, 3000
            else:
                continue
            ops.append(Op(fl, s, (a + b) / 2, w, kind, sill, head, into=r, room=r))
    return ops

def tag_ops(all_ops):
    dn = wn = sn = 0
    for o in all_ops:
        if o.kind in ('door', 'door2', 'lift'):
            dn += 1; o.tag = 'D%02d' % dn
        elif o.kind in ('slide', 'slide1'):
            sn += 1; o.tag = 'SD%02d' % sn
        elif o.kind in ('win', 'glass', 'louver'):
            wn += 1; o.tag = 'W%02d' % wn
        else:
            o.tag = ''

MODEL = {}
def model():
    if MODEL: return MODEL
    allops = []
    for fl in sorted(FLOORS):
        segs, ops, un = build(fl)
        ops = add_windows(fl, segs, ops)
        MODEL[fl] = dict(segs=segs, ops=ops, unreached=un)
        allops += ops
    tag_ops(allops)
    return MODEL

if __name__ == '__main__':
    M = model()
    for fl in sorted(FLOORS):
        segs, ops, un = M[fl]['segs'], M[fl]['ops'], M[fl]['unreached']
        print('F%d segs %d ops %d unreached %s' % (fl, len(segs), len(ops), un))
        for o in ops:
            if o.kind in ('door', 'door2', 'lift', 'slide', 'slide1', 'open'):
                s = o.seg
                print('   %-5s %-6s w%4d  %s | %s' % (o.tag, o.kind, o.w, s.a.name, s.b.name if s.b else 'EXT-' + side_of(s)))
