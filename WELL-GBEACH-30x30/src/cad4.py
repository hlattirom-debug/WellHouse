# -*- coding: utf-8 -*-
"""Primitive recorder -> DXF (ezdxf) + matplotlib (true scale). One geometry source, two outputs."""
import math
import ezdxf
from ezdxf.addons import importer
from ezdxf.math import Matrix44

LAYERS = {  # name: (aci colour, lineweight 1/100mm, pdf colour, pdf lw mm)
    'A-WALL':      (7, 50, '#111111', 0.50),
    'A-WALL-POCHE': (8, 0, '#2b2b2b', 0.0),
    'A-WALL-INT':  (7, 35, '#222222', 0.35),
    'A-COL':       (7, 50, '#111111', 0.50),
    'A-DOOR':      (3, 18, '#1a1a1a', 0.18),
    'A-GLAZ':      (4, 18, '#1f6fa8', 0.18),
    'A-RAIL':      (6, 18, '#444444', 0.18),
    'A-STAIR':     (2, 18, '#333333', 0.18),
    'A-FURN':      (8, 13, '#7a7a7a', 0.13),
    'A-EQPM':      (8, 13, '#7a7a7a', 0.13),
    'A-TEXT':      (7, 18, '#111111', 0.18),
    'A-ANNO':      (1, 13, '#b22222', 0.13),
    'A-DIMS':      (1, 13, '#b22222', 0.13),
    'A-GRID':      (1, 13, '#cc4444', 0.13),
    'A-AREA':      (8, 0, '#f2efe8', 0.0),
    'A-HIDD':      (8, 13, '#9a9a9a', 0.13),
    'A-ROOF':      (5, 25, '#222222', 0.25),
    'L-SITE':      (3, 18, '#3c6e3c', 0.18),
    'L-PLNT':      (3, 13, '#5f8f5f', 0.13),
    'L-WATR':      (5, 18, '#2f7fb5', 0.18),
    'L-PAVE':      (8, 13, '#8a8a8a', 0.13),
    'C-PROP':      (1, 35, '#c0392b', 0.35),
    'C-ROAD':      (8, 18, '#666666', 0.18),
    'E-ELEV':      (7, 25, '#1a1a1a', 0.25),
    'E-ELEV-FINE': (8, 13, '#555555', 0.13),
    'E-GLAS':      (4, 13, '#1f6fa8', 0.13),
    'S-CUT':       (7, 50, '#111111', 0.5),
    'S-CUT-POCHE': (8, 0, '#3a3a3a', 0.0),
    'A-TITLE':     (7, 25, '#111111', 0.25),
}

class Rec:
    def __init__(s):
        s.items = []
    # geometry ------------------------------------------------------------
    def line(s, a, b, ly='A-WALL', ls='-', lw=None, c=None):
        s.items.append(('L', ly, (tuple(a), tuple(b)), dict(ls=ls, lw=lw, c=c)))
    def pline(s, pts, ly='A-WALL', closed=False, ls='-', lw=None, c=None):
        s.items.append(('P', ly, [tuple(p) for p in pts], dict(closed=closed, ls=ls, lw=lw, c=c)))
    def rect(s, x0, y0, x1, y1, ly='A-WALL', **k):
        s.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ly, closed=True, **k)
    def fill(s, pts, ly='A-WALL-POCHE', color=None, alpha=1.0, z=0, hatch=None, edge=None, holes=None):
        s.items.append(('F', ly, [tuple(p) for p in pts], dict(color=color, alpha=alpha, z=z, hatch=hatch, edge=edge,
                                                                holes=[[tuple(q) for q in h] for h in holes] if holes else None)))
    def fillpoly(s, poly, ly='A-AREA', **k):
        gs = [poly] if poly.geom_type == 'Polygon' else [g for g in getattr(poly, 'geoms', []) if g.geom_type == 'Polygon']
        for g in gs:
            if g.area < 1: continue
            s.fill(list(g.exterior.coords), ly, holes=[list(i.coords) for i in g.interiors], **k)
    def frect(s, x0, y0, x1, y1, ly='A-WALL-POCHE', **k):
        s.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ly, **k)
    def circle(s, c, r, ly='A-FURN', **k):
        s.items.append(('C', ly, (tuple(c), r), k))
    def arc(s, c, r, a0, a1, ly='A-DOOR', **k):  # degrees ccw
        s.items.append(('A', ly, (tuple(c), r, a0, a1), k))
    def text(s, p, t, h=250, ly='A-TEXT', ha='center', va='center', rot=0, bold=False, c=None):
        s.items.append(('T', ly, (tuple(p), str(t), h), dict(ha=ha, va=va, rot=rot, bold=bold, c=c)))
    def block(s, name, p, rot=0, sx=1, sy=1, ly='A-FURN'):
        s.items.append(('B', ly, (name, tuple(p), rot, sx, sy), {}))
    def dim(s, a, b, off, ly='A-DIMS', h=180, txt=None, ext=True):
        """aligned dimension between a and b, offset 'off' along left normal"""
        ax, ay = a; bx, by = b
        L = math.hypot(bx - ax, by - ay)
        if L < 1: return
        ux, uy = (bx - ax) / L, (by - ay) / L; nx, ny = -uy, ux
        pa = (ax + nx * off, ay + ny * off); pb = (bx + nx * off, by + ny * off)
        if ext:
            sg = 1 if off >= 0 else -1
            s.line((ax + nx * sg * 100, ay + ny * sg * 100), (pa[0] + nx * sg * 150, pa[1] + ny * sg * 150), ly)
            s.line((bx + nx * sg * 100, by + ny * sg * 100), (pb[0] + nx * sg * 150, pb[1] + ny * sg * 150), ly)
        s.line(pa, pb, ly)
        t = 120
        for p in (pa, pb):
            s.line((p[0] - (ux + nx) * t * .5, p[1] - (uy + ny) * t * .5), (p[0] + (ux + nx) * t * .5, p[1] + (uy + ny) * t * .5), ly, lw=0.3)
        ang = math.degrees(math.atan2(uy, ux))
        if ang > 90.1 or ang < -89.9: ang += 180
        mid = ((pa[0] + pb[0]) / 2 + nx * h * 0.75, (pa[1] + pb[1]) / 2 + ny * h * 0.75)
        s.text(mid, txt if txt is not None else '%d' % round(L), h, ly, rot=ang)
    def extend(s, other, dx=0, dy=0):
        if dx == 0 and dy == 0:
            s.items.extend(other.items); return
        for it in other.items:
            s.items.append(_move(it, dx, dy))
    def bbox(s):
        xs, ys = [], []
        for t, ly, d, k in s.items:
            if t == 'L': pts = d
            elif t in ('P', 'F'): pts = d
            elif t == 'C': pts = [(d[0][0] - d[1], d[0][1] - d[1]), (d[0][0] + d[1], d[0][1] + d[1])]
            elif t == 'A': pts = [(d[0][0] - d[1], d[0][1] - d[1]), (d[0][0] + d[1], d[0][1] + d[1])]
            else: pts = [d[0]] if t == 'T' else [d[1]]
            for p in pts: xs.append(p[0]); ys.append(p[1])
        return min(xs), min(ys), max(xs), max(ys)

def _move(it, dx, dy):
    t, ly, d, k = it
    mv = lambda p: (p[0] + dx, p[1] + dy)
    if t == 'F' and k.get('holes'):
        k = dict(k); k['holes'] = [[mv(p) for p in h] for h in k['holes']]
    if t == 'L': d = (mv(d[0]), mv(d[1]))
    elif t in ('P', 'F'): d = [mv(p) for p in d]
    elif t == 'C': d = (mv(d[0]), d[1])
    elif t == 'A': d = (mv(d[0]),) + tuple(d[1:])
    elif t == 'T': d = (mv(d[0]), d[1], d[2])
    elif t == 'B': d = (d[0], mv(d[1])) + tuple(d[2:])
    return (t, ly, d, k)

# ---------------------------------------------------------------- block library
BLK_SRC = '/mnt/user-data/uploads/NACK HOUSE/'
BLK_FILES = {'SN': 'Sanitary_Plan_Blocks_LOD400.dxf', 'BD': 'Bed_Plan_Blocks_LOD400_v2.dxf',
             'WR': 'Wardrobe_Plan_Blocks_LOD400.dxf', 'FW': 'Office_Desk_Chair_Plan_Blocks_LOD400.dxf',
             'NK': 'Extension_House_Furniture_10Options_LOD300.dxf'}
_docs = {}
_geo = {}
GEOM_T = ('LWPOLYLINE', 'LINE', 'ARC', 'CIRCLE', 'ELLIPSE', 'SPLINE', 'POLYLINE')

def _src(name):
    k = name.split('_')[0]
    if k not in _docs:
        _docs[k] = ezdxf.readfile(BLK_SRC + BLK_FILES[k])
    return _docs[k]

def block_geom(name):
    """flattened polylines (local coords) of the block, filtered: no text/attdef/hatch, no clearance box"""
    if name in _geo: return _geo[name]
    doc = _src(name); b = doc.blocks.get(name)
    out = []
    ents = [e for e in b if e.dxftype() in GEOM_T]
    for e in ents:
        try:
            if e.dxftype() == 'LINE':
                out.append([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])
            elif e.dxftype() == 'LWPOLYLINE':
                pts = [(p[0], p[1]) for p in e.get_points()]
                if e.closed: pts.append(pts[0])
                # drop big clearance rectangles in bed blocks
                if name.startswith('BD'):
                    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                    if max(xs) - min(xs) > 2300 or (max(ys) - min(ys) > 2600): continue
                out.append(pts)
            else:
                pts = [(v.x, v.y) for v in e.flattening(8)]
                out.append(pts)
        except Exception:
            pass
    _geo[name] = out
    return out

def block_xy(name, p, rot, sx=1, sy=1):
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    res = []
    for pl in block_geom(name):
        res.append([(p[0] + (x * sx) * c - (y * sy) * s_, p[1] + (x * sx) * s_ + (y * sy) * c) for x, y in pl])
    return res

# ---------------------------------------------------------------- DXF writer
class DXF:
    def __init__(s):
        s.doc = ezdxf.new('R2018', setup=True)
        s.doc.header['$INSUNITS'] = 4
        s.msp = s.doc.modelspace()
        for n, (aci, lw, _, _) in LAYERS.items():
            if n not in s.doc.layers:
                s.doc.layers.add(n, color=aci, lineweight=lw if lw else -3)
        if 'TH' not in s.doc.styles:
            s.doc.styles.add('TH', font='tahoma.ttf')
        s.imported = set()
        s.ims = {}
    def _imp(s, name):
        if name in s.imported: return
        src = _src(name)
        im = importer.Importer(src, s.doc)
        im.import_block(name)
        im.finalize()
        # strip attdefs/texts from imported block for cleaner plans
        b = s.doc.blocks.get(name)
        for e in list(b):
            if e.dxftype() in ('ATTDEF', 'TEXT', 'MTEXT'):
                b.delete_entity(e)
        s.imported.add(name)
    def add(s, rec, dx=0, dy=0, sc=1.0):
        m = s.msp
        P = lambda p: (p[0] * sc + dx, p[1] * sc + dy)
        for t, ly, d, k in rec.items:
            at = {'layer': ly}
            if k.get('c') and isinstance(k.get('c'), int): at['color'] = k['c']
            if t == 'L':
                m.add_line(P(d[0]), P(d[1]), dxfattribs=at)
            elif t == 'P':
                m.add_lwpolyline([P(p) for p in d], close=k.get('closed', False), dxfattribs=at)
            elif t == 'F':
                if ly in ('A-AREA',):
                    continue
                h = m.add_hatch(dxfattribs={'layer': ly})
                h.paths.add_polyline_path([P(p) for p in d], is_closed=True, flags=1)
                for hl in (k.get('holes') or []):
                    h.paths.add_polyline_path([P(p) for p in hl], is_closed=True, flags=0)
                if k.get('hatch'):
                    h.set_pattern_fill('ANSI31', scale=20 * sc if sc != 1 else 20)
                else:
                    h.set_solid_fill(color=8 if not k.get('color') else 254)
            elif t == 'C':
                m.add_circle(P(d[0]), d[1] * sc, dxfattribs=at)
            elif t == 'A':
                m.add_arc(P(d[0]), d[1] * sc, d[2], d[3], dxfattribs=at)
            elif t == 'T':
                at.update(style='TH', height=d[2] * sc * 0.75, rotation=k.get('rot', 0))
                tx = m.add_text(d[1].replace('\n', ' '), dxfattribs=at)
                al = {('center', 'center'): 'MIDDLE_CENTER', ('left', 'center'): 'MIDDLE_LEFT', ('right', 'center'): 'MIDDLE_RIGHT',
                      ('left', 'bottom'): 'BOTTOM_LEFT', ('center', 'bottom'): 'BOTTOM_CENTER', ('left', 'top'): 'TOP_LEFT',
                      ('right', 'bottom'): 'BOTTOM_RIGHT', ('center', 'top'): 'TOP_CENTER', ('right', 'top'): 'TOP_RIGHT'}
                tx.set_placement(P(d[0]), align=getattr(ezdxf.enums.TextEntityAlignment, al.get((k['ha'], k['va']), 'MIDDLE_CENTER')))
            elif t == 'B':
                name, p, rot, sx, sy = d
                s._imp(name)
                m.add_blockref(name, P(p), dxfattribs={'layer': ly, 'rotation': rot, 'xscale': sx * sc, 'yscale': sy * sc})
    def save(s, path):
        s.doc.saveas(path)

# ---------------------------------------------------------------- matplotlib emitter
import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc as MArc, Circle as MCircle
from matplotlib.collections import LineCollection
FONT_DIR = '/usr/share/fonts/opentype/tlwg/'
for f in ('Loma.otf', 'Loma-Bold.otf'):
    fm.fontManager.addfont(FONT_DIR + f)
plt.rcParams['font.family'] = 'Loma'
PT_PER_MM = 72 / 25.4

def draw_mpl(ax, rec, scale, dx=0, dy=0, only=None, skip=()):
    """scale = drawing scale denominator (100 for 1:100). Texts sized so model height h -> h/scale mm on paper."""
    lines = {}
    for t, ly, d, k in rec.items:
        if only and ly not in only: continue
        if ly in skip: continue
        _, _, pc, plw = LAYERS.get(ly, (7, 18, '#000', 0.18))
        col = k.get('c') if isinstance(k.get('c'), str) else pc
        lw = (k.get('lw') or plw) * PT_PER_MM
        if t == 'L':
            ls = k.get('ls', '-')
            if ls == '-':
                lines.setdefault((col, lw), []).append([(d[0][0] + dx, d[0][1] + dy), (d[1][0] + dx, d[1][1] + dy)])
            else:
                ax.plot([d[0][0] + dx, d[1][0] + dx], [d[0][1] + dy, d[1][1] + dy], color=col, lw=lw, ls=ls, zorder=3)
        elif t == 'P':
            pts = [(p[0] + dx, p[1] + dy) for p in d]
            if k.get('closed'): pts = pts + [pts[0]]
            ls = k.get('ls', '-')
            if ls == '-':
                lines.setdefault((col, lw), []).append(pts)
            else:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=lw, ls=ls, zorder=3)
        elif t == 'F':
            fc = k.get('color') or pc
            if k.get('holes'):
                from matplotlib.path import Path as MPath
                from matplotlib.patches import PathPatch
                rings = [[(p[0] + dx, p[1] + dy) for p in d]] + [[(p[0] + dx, p[1] + dy) for p in h] for h in k['holes']]
                verts, codes = [], []
                for rg in rings:
                    verts += rg + [rg[0]]; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(rg) - 1) + [MPath.CLOSEPOLY]
                ax.add_patch(PathPatch(MPath(verts, codes), fc=fc, ec='none', lw=0.1, alpha=k.get('alpha', 1), zorder=k.get('z', 0) + 1))
            else:
                ax.add_patch(Polygon([(p[0] + dx, p[1] + dy) for p in d], closed=True, fc=fc if not k.get('hatch') else 'none',
                                 ec=k.get('edge') or 'none', lw=0.1 if not k.get('edge') else 0.25, alpha=k.get('alpha', 1),
                                 zorder=k.get('z', 0) + 1, hatch=k.get('hatch')))
        elif t == 'C':
            ax.add_patch(MCircle((d[0][0] + dx, d[0][1] + dy), d[1], fill=False, ec=col, lw=lw, zorder=3))
        elif t == 'A':
            ax.add_patch(MArc((d[0][0] + dx, d[0][1] + dy), 2 * d[1], 2 * d[1], theta1=d[2], theta2=d[3], ec=col, lw=lw, zorder=3))
        elif t == 'T':
            fs = d[2] / scale * PT_PER_MM / 0.72
            ax.text(d[0][0] + dx, d[0][1] + dy, d[1], fontsize=fs, ha=k['ha'], va=k['va'], rotation=k.get('rot', 0),
                    color=col, fontweight='bold' if k.get('bold') else 'normal', zorder=6, rotation_mode='anchor', linespacing=1.15)
        elif t == 'B':
            name, p, rot, sx, sy = d
            for pl in block_xy(name, (p[0] + dx, p[1] + dy), rot, sx, sy):
                lines.setdefault((col, lw), []).append(pl)
    for (col, lw), segs in lines.items():
        ax.add_collection(LineCollection(segs, colors=col, linewidths=lw, zorder=3, capstyle='butt', joinstyle='miter'))

def scaled_axes(fig, x0_mm, y0_mm, view, scale):
    """place an axes on the figure at (x0_mm, y0_mm) from bottom-left of sheet, showing 'view'=(X0,Y0,X1,Y1) at 1:scale"""
    FW, FH = fig.get_size_inches()[0] * 25.4, fig.get_size_inches()[1] * 25.4
    w = (view[2] - view[0]) / scale; h = (view[3] - view[1]) / scale
    ax = fig.add_axes([x0_mm / FW, y0_mm / FH, w / FW, h / FH])
    ax.set_xlim(view[0], view[2]); ax.set_ylim(view[1], view[3])
    ax.set_aspect('equal'); ax.axis('off')
    return ax
