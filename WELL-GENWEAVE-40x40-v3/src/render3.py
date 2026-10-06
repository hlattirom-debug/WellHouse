# -*- coding: utf-8 -*-
"""A2 sheet set (PDF) + DXF assembly for WELL-GENWEAVE 40x40 v3."""
import os, math, datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from PIL import Image
from cad3 import draw_mpl, scaled_axes, DXF, Rec
from frame3 import *
from plan3 import FLOORS, PROGRAM, PROGRAM_NUA, PROGRAM_GFA, all_rooms, COURTS
from walls3 import model, side_of
from draw3 import plan, grid, PLAN_VIEW, north_arrow, section_marks
from proj3 import elevation, section, SECTIONS
from site3 import site_plan, roof_plan
from verify3 import run, areas, cost

A2 = (594, 420)
OUT = '/mnt/user-data/outputs'
REND = '/mnt/user-data/uploads/WELL/WELL-GENWEAVE-40x40/v3/renders/'
PROJ = 'WELL-GENWEAVE 40x40 v3 · GENWEAVE Executive Luxury Villa · บ้านเดี่ยว 3 ชั้น "ลำต้น + กิ่ง" (TRUNK + BRANCH)'
SITE_TXT = 'ที่ดิน 40.00 x 40.00 ม. (400 ตร.ว.) · ถนน 8.00 ม. ทิศเหนือ · โปรแกรม ARCHISPACE 27 ก.ย. 2569'
TODAY = '1 ต.ค. 2569'
TITLE_X = 516

def sheet(no, title, scale_txt):
    fig = plt.figure(figsize=(A2[0] / 25.4, A2[1] / 25.4))
    ov = fig.add_axes([0, 0, 1, 1]); ov.set_xlim(0, A2[0]); ov.set_ylim(0, A2[1]); ov.axis('off')
    ov.add_patch(Rectangle((8, 8), A2[0] - 16, A2[1] - 16, fill=False, lw=1.0, ec='#111'))
    ov.add_patch(Rectangle((TITLE_X, 8), A2[0] - 8 - TITLE_X, A2[1] - 16, fill=False, lw=0.8, ec='#111'))
    x = TITLE_X + 3
    ov.text(x, 405, 'H3A DESIGN AND BUILD', fontsize=9, fontweight='bold', va='top')
    ov.text(x, 400, 'X-UNIT Architecture Lab', fontsize=7, va='top', color='#555')
    ov.plot([TITLE_X, A2[0] - 8], [394, 394], lw=0.6, c='#111')
    ov.text(x, 391, 'โครงการ', fontsize=6, color='#777', va='top')
    ov.text(x, 386, 'WELL-GENWEAVE 40x40 v3', fontsize=8.5, fontweight='bold', va='top')
    ov.text(x, 381, 'Executive Luxury Villa\nบ้านเดี่ยว 3 ชั้น ผ่านเกณฑ์\nWELL for Residential (เจตนา)', fontsize=6.5, va='top', linespacing=1.35)
    ov.text(x, 365, 'ที่ดิน 40.00 x 40.00 ม. = 400 ตร.ว.\nถนนสาธารณะ 8.00 ม. ทิศเหนือ', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [355, 355], lw=0.6, c='#111')
    ov.text(x, 352, 'แนวคิด', fontsize=6, color='#777', va='top')
    ov.text(x, 347, 'GENWEAVE: ลำต้น (แกนบันได+ปล่อง\nTermite) แตกกิ่ง 4 ทิศ รอบคอร์ต 2 แห่ง\nCrown bar ชั้น 3 = เรือนยอดบังแดด', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [330, 330], lw=0.6, c='#111')
    ov.text(x, 327, 'ระดับ', fontsize=6, color='#777', va='top')
    ov.text(x, 322, '±0.00 ถนน · F1 +0.60 · F2 +4.20\nF3 +7.80 · หลังคา +11.40\nparapet +12.00 · ปล่อง +14.00', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [304, 304], lw=0.6, c='#111')
    ov.text(x, 300, 'หมายเหตุ', fontsize=6, color='#777', va='top')
    ov.text(x, 295, '· หน่วยเป็นมิลลิเมตร เว้นแต่ระบุ\n· ระดับอ้างอิงถนนหน้าที่ดิน ±0.00\n· ห้ามวัดขนาดจากแบบ ใช้ตัวเลขกำกับ\n· แบบระดับ Design Development\n  ต้องให้สถาปนิกและวิศวกรผู้ได้รับ\n  ใบอนุญาตตรวจสอบและลงนาม\n  ก่อนยื่นขออนุญาต', fontsize=5.6, va='top', linespacing=1.4)
    ov.plot([TITLE_X, A2[0] - 8], [60, 60], lw=0.6, c='#111')
    ov.text(x, 57, 'ชื่อแผ่น', fontsize=6, color='#777', va='top')
    ov.text(x, 52, title, fontsize=7.5, fontweight='bold', va='top', linespacing=1.3, wrap=True)
    ov.plot([TITLE_X, A2[0] - 8], [30, 30], lw=0.6, c='#111')
    ov.text(x, 27, 'มาตราส่วน  %s' % scale_txt, fontsize=6, va='top')
    ov.text(x, 22, 'วันที่  %s   ฉบับ  v3 / DD' % TODAY, fontsize=6, va='top')
    ov.text(A2[0] - 11, 12, no, fontsize=20, fontweight='bold', ha='right', va='bottom')
    ov.text(12, 413, PROJ, fontsize=8, fontweight='bold', va='top')
    ov.text(12, 408.5, SITE_TXT, fontsize=6, color='#555', va='top')
    return fig, ov

def table(ov, x, y, cols, rows, fs=5.6, head=True, rh=None, title=None, wrapcol=None, colors=None):
    """cols = [(header, width_mm, align)], rows = list of tuples; y = top. returns bottom y"""
    if rh is None: rh = fs * 1.62 / 72 * 25.4
    if title:
        ov.text(x, y, title, fontsize=fs + 1.6, fontweight='bold', va='bottom'); y -= 1.2
    W = sum(c[1] for c in cols)
    yy = y
    if head:
        ov.add_patch(Rectangle((x, yy - rh), W, rh, fc='#1f3a5f', ec='none'))
        cx = x
        for h, w, al in cols:
            ov.text(cx + (1 if al == 'left' else (w / 2 if al == 'center' else w - 1)), yy - rh / 2, h, fontsize=fs, color='white', fontweight='bold', ha=al, va='center')
            cx += w
        yy -= rh
    for i, r in enumerate(rows):
        fc = '#f3f5f8' if i % 2 == 0 else 'white'
        if colors and colors[i]: fc = colors[i]
        ov.add_patch(Rectangle((x, yy - rh), W, rh, fc=fc, ec='none'))
        cx = x
        for (h, w, al), v in zip(cols, r):
            ov.text(cx + (1 if al == 'left' else (w / 2 if al == 'center' else w - 1)), yy - rh / 2, str(v), fontsize=fs, ha=al, va='center', clip_on=False)
            cx += w
        yy -= rh
    ov.add_patch(Rectangle((x, yy), W, y - yy, fill=False, lw=0.4, ec='#333'))
    return yy

import textwrap
def thai_len(s):
    return sum(0 if ('\u0e31' == c or '\u0e34' <= c <= '\u0e3a' or '\u0e47' <= c <= '\u0e4e') else 1 for c in s)
def wrap(s, w_mm, fs):
    per = max(10, int(w_mm / (fs * 0.185)))
    out = []
    for part in s.split('\n'):
        words = part.split(' ')
        cur = ''
        for wd in words:
            if thai_len(cur + ' ' + wd) > per and cur:
                out.append(cur); cur = '   ' + wd
            else:
                cur = (cur + ' ' + wd) if cur else wd
        out.append(cur)
    return out
def para(ov, x, y, w, title, lines, fs=6.0, gap=1.0, tcol='#1f3a5f'):
    lh = fs * 1.55 / 72 * 25.4
    if title:
        ov.text(x, y, title, fontsize=fs + 1.6, fontweight='bold', color=tcol, va='top'); y -= lh * 1.5
    for ln in lines:
        for sub in wrap(ln, w, fs):
            ov.text(x, y, sub, fontsize=fs, va='top')
            y -= lh * gap
    return y

def caption(ov, x, y, t, sc_txt):
    ov.text(x, y, t, fontsize=8.5, fontweight='bold', va='top')
    ov.text(x, y - 4.2, sc_txt, fontsize=6.2, color='#555', va='top')

def place(fig, R, view, x_mm, y_mm, sc):
    ax = scaled_axes(fig, x_mm, y_mm, view, sc)
    draw_mpl(ax, R, sc)
    return ax

def scalebar(ov, x, y, sc, m=5):
    L = m * 1000 / sc
    for i in range(m):
        ov.add_patch(Rectangle((x + i * L / m, y), L / m, 1.2, fc='#111' if i % 2 == 0 else 'white', ec='#111', lw=0.4))
    ov.text(x, y + 2, '0', fontsize=5.5, ha='center'); ov.text(x + L, y + 2, '%d ม.' % m, fontsize=5.5, ha='center')

# ============================================================== data
RES, INFO = run()
M = model()
AR, PAV = areas()
C = cost()

def room_rows(fl):
    rows = []
    seen = set()
    for r in FLOORS[fl]:
        if 'ส่วนต่อเนื่อง' in r.name or r.kind == 'void': continue
        a = r.a + sum(q.a for q in FLOORS[fl] if q.name == r.name + ' (ส่วนต่อเนื่อง)')
        kind = {'room': 'ห้องใช้งาน', 'wet': 'ห้องน้ำ/เปียก', 'svc': 'บริการ', 'circ': 'สัญจร', 'stair': 'บันได', 'lift': 'ลิฟต์', 'shaft': 'ปล่องลม',
                'inb': 'กึ่งภายนอก', 'park': 'จอดรถ'}[r.kind]
        rows.append((r.code, r.name[:34], '%.2f x %.2f' % (r.w / 1000, r.d / 1000), '%.2f' % a, kind))
    return rows

ROOMCOLS = [('รหัส', 9, 'center'), ('ห้อง', 52, 'left'), ('ขนาด ม.', 20, 'center'), ('ตร.ม.', 12, 'right'), ('ประเภท', 19, 'left')]

pages = []

# ============================================================== A-01 concept + limitations
def A01():
    fig, ov = sheet('A-01', 'แนวคิด GENWEAVE\n+ โครงสร้าง + รายงานข้อจำกัด', 'ไม่มีมาตราส่วน')
    imgs = [('GW3_1_Aerial_SE.png', 'มุมมองทางอากาศ ทิศตะวันออกเฉียงใต้ — Crown bar ชั้น 3 ห่อด้วยครีบไม้ (CACTUS skin) + แผงโซลาร์ 23.1 kWp'),
            ('GW3_6_Aerial_SW.png', 'มุมมองทิศตะวันตกเฉียงใต้ — สระน้ำเกลือ ศาลาริมสระ หลังคาสวน และครีบไม้ฝั่งตะวันตก'),
            ('GW3_2_Garden_South.png', 'จากสวนทิศใต้ — ห้องนั่งเล่น/ห้องอาหารสูง 2 ชั้น กันสาดไม้ +3.50 ครีบไม้ชั้น 3'),
            ('GW3_5_Termite_Court.png', 'คอร์ตต้นไม้ (ปอด Termite) — ลมเย็นจากร่มไม้เข้าสู่ปล่องลมแกนลำต้น')]
    pos = [(12, 283, 160, 100), (176, 283, 160, 100), (12, 172, 160, 100), (176, 172, 160, 100)]
    for (f, cap), (x, y, w, h) in zip(imgs, pos):
        p = REND + f
        if os.path.exists(p):
            im = Image.open(p).convert('RGB')
            ax = fig.add_axes([x / A2[0], y / A2[1], w / A2[0], h / A2[1]]); ax.imshow(im, aspect='auto'); ax.axis('off')
        ov.text(x, y - 1.5, cap, fontsize=5.6, va='top', color='#333')
    concept_diagrams(fig, ov)
    ov.text(12, 400, 'ภาพจากโมเดล Blender (WELL-GENWEAVE-40x40-v3-model.blend) — โมเดลมวลอาคารระดับ DD สร้างจากข้อมูลชุดเดียวกับแบบ CAD', fontsize=6, color='#555', va='top')
    # concept table
    rows = [('01 TERMITE -> BREATH', 'ปล่องลมแกนลำต้น 1.80x3.20 ม. ทะลุ 3 ชั้นถึง +14.00 (solar chimney กระจก)', 'ลมเข้าจากคอร์ตต้นไม้/คอร์ตน้ำ ออกทางปล่อง (stack) — ต้องพิสูจน์ด้วย CFD'),
            ('02 TREE -> WEAVE', 'ไม่มีทางเดินยาว: ลำต้น (บันได+ลิฟต์+ปล่อง) แตก 4 กิ่ง', 'กิ่งเหนือ=ทางเข้า/จอดรถ กิ่งตะวันตก=บริการ กิ่งตะวันออก=แขก กิ่งใต้=ส่วนรวม'),
            ('03 BONE -> STRUCTURE', 'กริด 8 x 5 แนว ช่วง 2.50-5.80 ม. เสา 0.40x0.40', 'Crown bar ชั้น 3 วางบนแนวเสา A/B; คานถ่ายแรงโรงรถ 11.40 ม.'),
            ('04 CACTUS -> SKIN', 'ครีบไม้ 80x450 @600 ทิศใต้/ตะวันตก ของ Crown bar', 'กันสาดไม้ลึก 1.20 ม. ที่ +3.50 หน้าห้องนั่งเล่น-อาหาร; ผนังหินชั้น 1 หน่วงความร้อน'),
            ('05 BEETLE -> WATER', 'หลังคา 701 ตร.ม. ระบายลงถังใต้คอร์ตน้ำ 20 ลบ.ม.', 'สระน้ำเกลือ 16.0x4.5 ม. + บ่อในคอร์ตน้ำ เป็นตัวลดอุณหภูมิผิวอากาศ'),
            ('06 MANGROVE -> ECOSYSTEM', 'ยกพื้น +0.60 ม. จากถนน · ร่องซับน้ำ 1.00 ม. ทิศใต้/ตะวันออก', 'บึงประดิษฐ์บำบัดน้ำเทา · หลังคาสวน 460 ตร.ม. (66% ของหลังคา)')]
    yb = 400
    yb = table(ov, 342, yb, [('ระบบชีวภาพ', 30, 'left'), ('สิ่งที่อยู่ในแบบ v3', 140, 'left')], [(a, b) for a, b, c in rows], fs=5.4, title='GENWEAVE 6 ระบบ -> องค์ประกอบในแบบ v3')
    yb = table(ov, 342, yb - 2, [('ระบบชีวภาพ', 30, 'left'), ('บทบาท / สิ่งที่ยังต้องพิสูจน์', 140, 'left')], [(a, c) for a, b, c in rows], fs=5.4)
    yb = para(ov, 342, yb - 4, 170, 'ที่มาของแนวคิด (แยกข้อเท็จจริง / การตีความ)', [
        'ข้อเท็จจริง: เอกสาร GENWEAVE ในโฟลเดอร์ของผู้ใช้ (00-06 + Master) กำหนด 6 ระบบ และหลัก "ใช้ logic ของธรรมชาติ ไม่ copy รูปร่าง" (ข้อ 17)',
        'ข้อเท็จจริง: README ของเอกสารระบุที่มาเป็น ChatGPT Deep Research — เราไม่ได้ตรวจตัวเลข/งานวิจัยที่อ้างในเอกสารนั้นซ้ำ',
        'การตีความของเรา: แปล "Central Trunk + Branching Spaces" (ข้อ 08) เป็นแกนบันไดกลาง 5.80 ม. + 4 ปีก + สะพานกระจก 2 แห่ง',
        'การตีความของเรา: "Crown bar" ชั้น 3 = เรือนยอดไม้ที่บังแดดให้ส่วนรวมด้านล่าง — ไม่ใช่ข้อความในเอกสารต้นฉบับ',
        'ไม่ได้อ้างงานของสถาปนิกรายใด และไม่อ้างตัวเลขประสิทธิภาพที่ไม่ได้คำนวณในชุดนี้'], fs=5.6)
    # limitations
    xv = INFO['fans']
    lim = [
        '1. โปรแกรมขัดกันเอง: "Upper Master Terrace" ระบุชั้น 2 แต่ Master Suite อยู่ชั้น 3 -> วางระเบียง 28.08 ตร.ม. ชั้น 3 ติดห้องนอน (ถ้าอยู่ชั้น 2 จะขาดจากห้องนอน)',
        '2. โปรแกรมให้ห้อง MEP/Generator อยู่ชั้น 2 -> ย้ายลงชั้น 1 (15.96 ตร.ม.) ติดชานบริการ; เครื่องปั่นไฟวางลานบริการในกล่องเก็บเสียง (น้ำหนัก-น้ำมัน-เสียง-ซ่อมบำรุง)',
        '3. ความสูงเฉลี่ยในโปรแกรม 2.80 ม. -> ใช้พื้นถึงพื้น 3.60 ม. (โปร่ง 3.00 ม. หลังหักพื้น 0.20 + ฝ้า/งานระบบ 0.40) อาคารสูงถึงหลังคา 11.40 ม.',
        '4. GFA แบบ 1,077.78 ตร.ม. vs โปรแกรม 939.55 (+138.23 = +14.7%%): ทางสัญจรจริง %.2f ตร.ม. (โปรแกรมเผื่อ 89.88) จากลำต้น-สะพาน-โถงรอบคอร์ต' % sum(r.a for r in all_rooms() if r.kind in ('circ', 'stair', 'lift', 'shaft')),
        '   + มุขรถเทียบ 18.56 + ห้องเก็บจักรยาน 9.52 + ห้องอาบน้ำริมสระ 4.48 ที่ไม่มีในโปรแกรม; NUA ห้องตามโปรแกรม 770.46 vs 749.00 (+21.46)',
        '5. ห้องแม่บ้าน 2 ห้อง 13.20 ตร.ม./ห้อง (รวม +4.40) เพราะต้องกว้างทะลุปีก 6.00 ม. จากชานบริการถึงคอร์ต เพื่อให้มีช่องเปิด 2 ด้าน; ห้องน้ำแม่บ้านเข้าทางชานบริการ (หลังคาคลุม ไม่ปิดล้อม)',
        '6. โรงรถ 4 คัน กว้าง 11.40 ม. = ช่องละ 2.85 ม. (แคบสำหรับ SUV เปิดประตู; สบายจริง 3 คัน) และต้องใช้คานถ่ายแรงช่วง 11.40 ม. (PT/เหล็ก) รับหลังคาสวน',
        '7. ทางลาด 1:12 ยาว 7.20 ม. = ความชันสูงสุดพอดี; ประตูโรงรถ->โถง ต่างระดับ 0.45 ม. ใช้ขั้นบันได 3 ขั้น (ผู้ใช้วีลแชร์ต้องเข้าทางมุขรถเทียบ+ทางลาด)',
        '8. ห้องที่ช่องเปิดไม่ถึง 10%% ใช้พัดลมระบาย (ฉ.39 ข้อ 6 วรรคสอง): %s' % ', '.join(xv),
        '9. ห้องโฮมเธียเตอร์ลึก 6.00 ม. จากหน้าต่าง (ตั้งใจให้มืด) · ห้องทำงานชั้น 3 ลึก 4.05 ม. (ใกล้เกณฑ์ 4.20)',
        '10. คอร์ตเปิดฟ้า 2 แห่ง (124.08 ตร.ม.) ต้องมีรางระบายน้ำ/ตะแกรงของตัวเอง ต่อลงถังน้ำฝนใต้คอร์ตน้ำ',
        '11. ห้องสูง 2 ชั้น 7.20 ม. (อาหาร-นั่งเล่น 90.72 ตร.ม.) ภาระแอร์สูง: ลมธรรมชาติ/ปล่อง Termite ช่วยได้เฉพาะช่วงอากาศเย็น ไม่แทนแอร์ในกรุงเทพฯ',
        '12. หลังคาสวน 460 ตร.ม. น้ำหนักอิ่มน้ำ ~300 กก./ตร.ม. ต้องคิดในโครงสร้าง; ครีบไม้ 119 ชิ้นควรใช้อะลูมิเนียมลายไม้เพื่อลดการบำรุงรักษา',
        '13. ไม่ทราบผังเมืองรวมของที่ตั้ง (FAR/OSR/ระยะร่น) — ต้องตรวจก่อนยื่นขออนุญาต',
    ]
    para(ov, 342, yb - 3, 170, 'รายงานข้อจำกัด (ตรงไปตรงมา)', lim, fs=5.6, gap=1.0, tcol='#b22222')
    pages.append(fig)

def concept_diagrams(fig, ov):
    from shapely.geometry import box as sb
    R = Rec()
    zc = {'park': '#cfcfcf', 'inb': '#efe3c8', 'circ': '#f6d36b', 'stair': '#e0a526', 'lift': '#e0a526', 'shaft': '#c0392b', 'room': '#a9cbe8', 'wet': '#cfe3ee', 'svc': '#d9d2e9'}
    for r_ in FLOORS[1]:
        R.frect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-AREA', color=zc[r_.kind], z=1)
        R.rect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-WALL-INT', lw=0.15)
    for nm, c in COURTS:
        R.frect(c[0], c[1], c[2], c[3], 'A-AREA', color='#b9dca0', z=1)
    cx, cy = 20100, Y(18600)
    for (tx, ty, t) in ((cx, Y(29500), 'กิ่งเหนือ\nทางเข้า/รถ'), (8500, Y(18800), 'กิ่งตะวันตก\nบริการ'), (31500, Y(20500), 'กิ่งตะวันออก\nแขก'), (cx, Y(8000), 'กิ่งใต้ ส่วนรวม\n(ใต้ Crown bar)')):
        R.line((cx, cy), (tx, ty), 'A-ANNO', lw=0.6)
        R.text((tx, ty), t, 620, 'A-TEXT', bold=True)
    R.circle((cx, cy), 1400, 'A-ANNO', lw=0.6); R.text((cx, cy), 'ลำต้น', 600, 'A-ANNO', bold=True)
    R.text((15100, Y(19000)), 'คอร์ตน้ำ', 750, 'L-SITE'); R.text((25300, Y(19300)), 'คอร์ต\nต้นไม้', 750, 'L-SITE')
    V = (4800, Y(6000) - 1000, 35200, Y(31400) + 1000)
    place(fig, R, V, 14, 20, 250)
    ov.text(14, 147, 'ไดอะแกรม TREE -> WEAVE: ลำต้น + 4 กิ่ง รอบ 2 คอร์ต (ผังชั้น 1, 1:250)', fontsize=6.5, fontweight='bold', va='top')
    # section airflow diagram
    S = section('B')
    for (a, b) in (((15000, 1800), (21000, 2600)), ((27000, 1800), (20500, 2600)), ((20000, 3500), (20000, 12500)), ((20000, 12500), (19300, 14800))):
        S.line(a, b, 'A-ANNO', lw=0.8)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        S.pline([(b[0] - 600 * math.cos(ang - .4), b[1] - 600 * math.sin(ang - .4)), b, (b[0] - 600 * math.cos(ang + .4), b[1] - 600 * math.sin(ang + .4))], 'A-ANNO', lw=0.8)
    V2 = (2000, -1500, 42000, 15500)
    place(fig, S, V2, 176, 22, 250)
    ov.text(176, 147, 'ไดอะแกรม TERMITE -> BREATH: ลมเย็นจากคอร์ต -> โถง -> ปล่องลมลำต้น -> ออก +14.00 (รูปตัด B-B, 1:250)', fontsize=6.5, fontweight='bold', va='top')
    ov.text(176, 18, 'ลูกศรแดง = ทิศทางลมที่ "ตั้งใจ" ตามหลัก stack effect — ยังไม่ได้พิสูจน์ด้วย CFD', fontsize=5.6, color='#b22222', va='top')

# ============================================================== A-02 site
def A02():
    fig, ov = sheet('A-02', 'ผังบริเวณ + ตารางกฎหมาย\n+ ประมาณราคา', '1:200')
    R = site_plan()
    V = (-4000, -4200, 45000, 49000)
    place(fig, R, V, 14, 16, 200)
    caption(ov, 14, 293 + 0, '', '')
    ov.text(14, 14, 'ผังบริเวณ  SITE PLAN  1:200', fontsize=8.5, fontweight='bold', va='bottom')
    scalebar(ov, 120, 14, 200, 10)
    law = [r for r in RES if r[0].startswith('ฉ.55') or r[0] == 'ร่นแนวถนน']
    rows = [(g.replace('ฉ.55 ', ''), i[:46], v[:34], c[:26], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in law]
    yb = table(ov, 268, 400, [('ข้อ', 15, 'left'), ('รายการ', 70, 'left'), ('ค่าในแบบ', 52, 'left'), ('เกณฑ์', 40, 'left'), ('ผล', 11, 'center')], rows, fs=4.9,
               title='ตรวจกฎกระทรวง ฉบับที่ 55 (2543)')
    ov.text(268, yb - 2, '* ร่นแนวถนน: อาคารสูงไม่เกิน 15 ม. ถนน 6-20 ม. ใช้ 1/10 ของความกว้างถนน (ตรวจซ้ำกับข้อบัญญัติท้องถิ่น/ผังเมืองรวม)', fontsize=4.8, va='top', color='#555')
    enc = sum(a[1] for a in AR); semi = sum(a[2] for a in AR) + PAV; park = sum(a[3] for a in AR)
    rows = [('ชั้น 1', '%.2f' % AR[0][1], '%.2f' % AR[0][2], '%.2f' % AR[0][3], '%.2f' % sum(AR[0][1:])),
            ('ชั้น 2', '%.2f' % AR[1][1], '%.2f' % AR[1][2], '-', '%.2f' % sum(AR[1][1:])),
            ('ชั้น 3', '%.2f' % AR[2][1], '%.2f' % AR[2][2], '-', '%.2f' % sum(AR[2][1:])),
            ('ศาลาริมสระ', '-', '%.2f' % PAV, '-', '%.2f' % PAV),
            ('รวม', '%.2f' % enc, '%.2f' % semi, '%.2f' % park, '%.2f' % (enc + semi + park)),
            ('โปรแกรม', '', '', '', '%.2f' % PROGRAM_GFA), ('ส่วนต่าง', '', '', '', '%+.2f (%+.1f%%)' % (enc + semi + park - PROGRAM_GFA, (enc + semi + park) / PROGRAM_GFA * 100 - 100))]
    yb = table(ov, 268, yb - 10, [('ชั้น', 30, 'left'), ('ปิดล้อม', 30, 'right'), ('กึ่งภายนอก', 30, 'right'), ('จอดรถ', 30, 'right'), ('รวม ตร.ม.', 40, 'right')], rows, fs=5.2,
               title='พื้นที่อาคาร (คิดถึงแนวศูนย์กลางผนัง)')
    rows = [('พื้นที่ดิน', '1,600.00 ตร.ม. (400 ตร.ว.)'), ('พื้นที่อาคารคลุมดิน (รวมศาลา)', '%.2f ตร.ม. (%.1f%%)' % (INFO['cover'], INFO['cover'] / 16)),
            ('ที่ว่าง นับคอร์ตเปิดฟ้า', '%.1f%%  (เกณฑ์ >= 30%%)' % INFO['os1']), ('ที่ว่าง ไม่นับคอร์ต %.2f ตร.ม.' % INFO['court'], '%.1f%%' % INFO['os2']),
            ('FAR (GFA ปิดล้อม / ที่ดิน)', '%.2f : 1' % (enc / 1600)), ('ความสูงอาคาร (ถึงพื้นหลังคา)', '11.40 ม. (<15 ม. ไม่เป็นอาคารสูง/ขนาดใหญ่)')]
    yb = table(ov, 268, yb - 10, [('รายการ', 70, 'left'), ('ค่า', 90, 'left')], rows, fs=5.2, title='ที่ว่างและการใช้ที่ดิน')
    rows = [('(ก) อัตราแยกมาตรฐาน', 'ปิดล้อม %.2f x 22,000 + กึ่งภายนอก %.2f x 11,000 + จอดรถ %.2f x 8,000' % (C['enc'], C['semi'], C['park']), '%.2f' % (C['std'] / 1e6)),
            ('(ข) อัตราแยก luxury', 'ปิดล้อม x 30,000 + กึ่งภายนอก x 15,000 + จอดรถ x 12,000', '%.2f' % (C['lux'] / 1e6)),
            ('(ค) อัตราเดียว (วิธีเดียวกับโปรแกรม)', 'GFA %.2f x 30,000' % C['gfa'], '%.2f' % (C['single'] / 1e6)),
            ('งานนอกอาคาร', 'สระ 72 ตร.ม. x 35,000 + PV 23.1 kWp x 45,000 + ภูมิทัศน์/รั้ว/ระบบ 2.50 ล.', '%.2f' % (C['extra'] / 1e6)),
            ('โปรแกรม ARCHISPACE', '939.55 x 30,000 (ช่วง 24.80-35.23 ล้าน)', '28.19')]
    yb = table(ov, 268, yb - 10, [('วิธีคิด', 48, 'left'), ('สูตร (บาท/ตร.ม.)', 100, 'left'), ('ล้านบาท', 20, 'right')], rows, fs=5.0, title='ประมาณราคาค่าก่อสร้าง (ระดับแนวคิด)')
    para(ov, 268, yb - 4, 240, None, ['ตัวเลข "อยู่ในงบไหม" ขึ้นกับวิธีคิด ไม่ใช่ขึ้นกับแบบ: (ข) %.2f ล้าน อยู่ในช่วงโปรแกรม; (ค) %.2f ล้าน อยู่ในช่วงแต่สูงกว่าค่ากลาง; รวมงานนอกอาคาร (ค)+%.2f = %.2f ล้าน เกินช่วงบน' %
                                     (C['lux'] / 1e6, C['single'] / 1e6, C['extra'] / 1e6, (C['single'] + C['extra']) / 1e6),
                                     'ยังไม่รวม: ฐานราก/เสาเข็ม (ขึ้นกับผลเจาะสำรวจดิน), เฟอร์นิเจอร์ลอยตัว, ภาษี/ค่าธรรมเนียม, ค่าออกแบบ'], fs=5.0)
    pages.append(fig)

# ============================================================== plans
def plan_sheet(no, fl):
    titles = {1: 'ผังพื้นชั้น 1  (FFL +0.60)', 2: 'ผังพื้นชั้น 2  (FFL +4.20)', 3: 'ผังพื้นชั้น 3  (FFL +7.80)'}
    fig, ov = sheet(no, titles[fl].replace('  ', '\n'), '1:100')
    R = plan(fl)
    grid(R, PLAN_VIEW)
    if fl == 1:
        north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 4500), 800)
        section_marks(R)
    else:
        north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 4500), 800)
        section_marks(R)
    place(fig, R, PLAN_VIEW, 12, 52, 100)
    ov.text(14, 47, titles[fl] + '   1:100', fontsize=9, fontweight='bold', va='top')
    scalebar(ov, 150, 43, 100, 5)
    rows = room_rows(fl)
    yb = table(ov, 382, 400, ROOMCOLS, rows, fs=4.9, title='ตารางห้อง ชั้น %d' % fl)
    enc, semi, park = AR[fl - 1][1:]
    yb = table(ov, 382, yb - 6, [('สรุปชั้น %d' % fl, 60, 'left'), ('ตร.ม.', 52, 'right')],
               [('พื้นที่ปิดล้อม', '%.2f' % enc), ('กึ่งภายนอก', '%.2f' % semi), ('จอดรถ', '%.2f' % park), ('รวม', '%.2f' % (enc + semi + park))], fs=5.2)
    notes = {1: ['· ลำต้น (Trunk) = ทางเดิน 1.40 ม. + โถงเหนือ/ใต้ + บันได U 2 ช่วง (ลูกตั้ง 180 / ลูกนอน 280) + ลิฟต์บ้าน + ปล่องลม Termite',
                 '· คอร์ตน้ำ (ตะวันตก) 4.20 x 10.80 ม. — บ่อน้ำ + ถังเก็บน้ำฝนใต้ดิน 20 ลบ.ม.; คอร์ตต้นไม้ (ตะวันออก) รูปตัว L — ต้นจามจุรี/ต้นไม้ร่มใหญ่',
                 '· ห้องอาหาร-ห้องนั่งเล่น เปิดถึงกันใต้ช่องโล่งสูง 2 ชั้น (7.20 ม.) แบ่งด้วยแนวเสา 5',
                 '· ปีกบริการ: ชานบริการหลังคาคลุม 1.20 ม. ด้านตะวันตก (ระแนงไม้) เชื่อมครัวไทย-ห้องแม่บ้าน-ซักรีด-MEP-โรงรถ',
                 '· ห้องนอนแขก (ผู้สูงอายุ) ชั้น 1: ประตูบานเลื่อนเข้าห้องน้ำ 900 มม. ฝักบัวไม่มีขอบกั้น',
                 '· จุดชาร์จรถไฟฟ้า (EV) 1 จุดในโรงรถ (WELL R-A09)',
                 '· ช่องเปิดทุกบานมีรหัส D/SD/W ในตาราง A-10'],
             2: ['· สะพานกระจก 2 แห่ง (กิ่ง W / กิ่ง E) กว้าง 1.80 ม. ข้ามคอร์ต เชื่อม Upper Gallery กับ Junior Suite',
                 '· ห้องนั่งเล่นครอบครัวมองลงโถงต้อนรับสูง 2 ชั้นผ่านราวกระจก 1.10 ม.',
                 '· ช่องโล่งเหนือห้องอาหาร-นั่งเล่น (โครงสร้าง Crown bar ชั้น 3 อยู่เหนือ)',
                 '· หลังคาสวน +4.20 เหนือโรงรถ/ครัว/เธียเตอร์/ปีกบริการ — เข้าถึงเพื่อบำรุงรักษาทางช่องเปิดบนหลังคา',
                 '· ครีบไม้ผนังตะวันตก/ตะวันออกของ Junior Suite บังแดดบ่าย'],
             3: ['· Crown bar: ห้องทำงาน-Walk-in-ห้องน้ำ Spa-ห้องนอน Master-ระเบียง เรียงตะวันตก->ตะวันออก ทางเดินด้านเหนือ',
                 '· ครีบไม้ 80x450 @600 ห่างผนัง 100-550 มม. ด้านใต้และตะวันตกทั้งแถบ (บังแดดเที่ยง-บ่าย)',
                 '· ระเบียง Master 28.08 ตร.ม. หลังคาคลุม (หลังคา Crown ยื่นคลุม) ราวกระจก 3 ด้าน',
                 '· โปรแกรมระบุระเบียง Master ชั้น 2 — ย้ายมาชั้น 3 (ดู A-01 ข้อ 1)']}
    para(ov, 382, yb - 6, 130, 'หมายเหตุ', notes[fl], fs=5.0)
    pages.append(fig)

def roof_sheet():
    fig, ov = sheet('A-06', 'แปลนหลังคา', '1:100')
    R = roof_plan()
    grid(R, PLAN_VIEW)
    place(fig, R, PLAN_VIEW, 12, 52, 100)
    ov.text(14, 47, 'แปลนหลังคา  ROOF PLAN   1:100', fontsize=9, fontweight='bold', va='top')
    scalebar(ov, 150, 43, 100, 5)
    ra = INFO['roofs']
    rows = [('หลังคาสวน +4.20 (เหนือชั้น 1)', '%.2f' % ra['green']), ('หลังคาสวน +7.80 (เหนือชั้น 2)', '%.2f' % ra['green2']), ('หลังคา Crown +11.40 (ค.ส.ล. ขาว SR)', '%.2f' % ra['main']),
            ('รวม', '%.2f' % sum(ra.values())), ('สัดส่วนหลังคาเขียว', '%.0f%%' % ((ra['green'] + ra['green2']) / sum(ra.values()) * 100))]
    yb = table(ov, 382, 400, [('หลังคา', 80, 'left'), ('ตร.ม.', 32, 'right')], rows, fs=5.4, title='พื้นที่หลังคา')
    tot = sum(ra.values())
    rows = [('ฝนรายปีกรุงเทพฯ (ประมาณ)', '~1,500 มม./ปี'), ('น้ำฝนเก็บได้ (หลังคาแข็ง C=0.9, สวน C=0.4)', '%.0f ลบ.ม./ปี' % ((ra['main'] * 0.9 + (ra['green'] + ra['green2']) * 0.4) * 1.5)),
            ('ถังเก็บน้ำฝนใต้คอร์ตน้ำ', '20 ลบ.ม. (รดน้ำสวน/ชักโครก)'), ('แผงโซลาร์ 42 x 550 Wp', '23.1 kWp ~ 29,000 kWh/ปี*'), ('ปล่องลม Termite', 'สูง +14.00 กระจกด้านเหนือ-ใต้')]
    yb = table(ov, 382, yb - 8, [('รายการ', 70, 'left'), ('ค่า', 42, 'left')], rows, fs=5.0, title='น้ำฝน (BEETLE) และพลังงาน')
    para(ov, 382, yb - 4, 130, 'ชั้นหลังคา', [
        '· หลังคาสวน: พืชคลุมดิน + ดินปลูก 150 มม. + แผ่นใยกรอง + แผ่นระบายน้ำ 20 มม.',
        '  + แผ่นกันรากทะลุ + กันซึม 2 ชั้น + ค.ส.ล. ลาด 1:100',
        '· หลังคา Crown: สีสะท้อนแสง SR >= 0.75 + PU foam 50 มม. + กันซึม + ค.ส.ล. 250',
        '· Parapet สูง 0.60 ม. (Crown) / 0.45 ม. (หลังคาสวน)',
        '· RD = ท่อระบายน้ำฝนหลังคา ลงรางรอบอาคาร -> ถังน้ำฝน -> ร่องซับน้ำ',
        '* พลังงาน PV ประมาณด้วย ~1,250 kWh/kWp/ปี — ต้องคำนวณจริงด้วยเงาจากครีบและปล่อง'], fs=5.0)
    pages.append(fig)

def elev_sheet(no, a, b, title):
    fig, ov = sheet(no, title, '1:100')
    names = {'S': 'รูปด้านทิศใต้ (มองจากสวน/สระ)', 'N': 'รูปด้านทิศเหนือ (ด้านถนน)', 'E': 'รูปด้านทิศตะวันออก', 'W': 'รูปด้านทิศตะวันตก (ลานบริการ)',
             'A': SECTIONS['A']['title'], 'B': SECTIONS['B']['title']}
    for i, k in enumerate((a, b)):
        R = elevation(k) if k in 'SNEW' else section(k)
        V = (-2000, -2700 if k in 'SNEW' else -4000, 46200, 14700)
        h = (V[3] - V[1]) / 100
        y0 = (400 - h) if i == 0 else 14
        place(fig, R, V, 12, y0, 100)
        ov.text(14, y0 + h - 1, names[k] + '   1:100', fontsize=8.5, fontweight='bold', va='top')
    scalebar(ov, 420, 14, 100, 5)
    pages.append(fig)

def A10():
    fig, ov = sheet('A-10', 'ตารางประตู-หน้าต่าง\n+ ตรวจช่องเปิด + เทียบโปรแกรม', 'ไม่มีมาตราส่วน')
    ops = [o for fl in (1, 2, 3) for o in M[fl]['ops'] if o.tag]
    kinds = {'door': 'ประตูบานเปิดเดี่ยว', 'door2': 'ประตูบานเปิดคู่', 'lift': 'ประตูลิฟต์', 'slide': 'ประตูบานเลื่อนกระจก', 'slide1': 'ประตูบานเลื่อนเดี่ยว',
             'win': 'หน้าต่าง', 'glass': 'ผนังกระจก', 'louver': 'เกล็ดระบายอากาศ'}
    rows = []
    for o in ops:
        s = o.seg
        where = '%s | %s' % (s.a.name[:16], (s.b.name[:14] if s.b else 'ภายนอก-' + side_of(s)))
        rows.append((o.tag, 'F%d' % o.fl, kinds.get(o.kind, o.kind), '%d' % o.w, '%d' % o.sill, '%d' % min(o.head, 3400), where))
    cols = [('รหัส', 9, 'left'), ('ชั้น', 6, 'center'), ('ชนิด', 25, 'left'), ('กว้าง', 9, 'right'), ('ขอบล่าง', 10, 'right'), ('ขอบบน', 9, 'right'), ('ตำแหน่ง', 56, 'left')]
    n = len(rows); per = (n + 1) // 2
    rh = min(5.5, 380 / (per + 1))
    table(ov, 12, 402, cols, rows[:per], fs=4.6, rh=rh, title='ตารางช่องเปิด (%d รายการ) — หน่วย มม. วัดจาก FFL' % n)
    table(ov, 142, 402, cols, rows[per:], fs=4.6, rh=rh)
    # opening check
    oc = [r for r in RES if r[0] == 'ฉ.39 ข้อ 6']
    rows = [(i[:34], v[:46], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in oc]
    yb = table(ov, 272, 402, [('ห้อง', 58, 'left'), ('ช่องเปิด/พื้นที่ห้อง', 64, 'left'), ('ผล', 10, 'center')], rows, fs=4.7, rh=4.3, title='ฉ.39 ข้อ 6 ช่องเปิด >= 10% ของพื้นที่ห้อง')
    cv = [r for r in RES if r[0] in ('ระบายอากาศ (เกณฑ์ภายใน)',)]
    dp = {r[1]: r[2] for r in RES if r[0] == 'ความลึกห้อง'}
    rows = [(i[:34], v, dp.get(i, '')[:30], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in cv]
    yb = table(ov, 272, yb - 7, [('ห้องใช้งานประจำ', 58, 'left'), ('ช่องเปิด', 22, 'left'), ('ลึกจากผนังนอก', 42, 'left'), ('ผล', 10, 'center')], rows, fs=4.7, rh=4.3,
               title='ระบายอากาศข้ามห้อง >= 2 แนวผนัง (เกณฑ์ภายใน สนับสนุน WELL R-T06) และความลึกห้อง <= 4.20 ม.')
    geo = [r for r in RES if r[0] == 'เรขาคณิต']
    rows = [(i[:44], v[:30], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in geo]
    yb = table(ov, 272, yb - 7, [('ตรวจเรขาคณิต', 70, 'left'), ('ผล', 52, 'left'), ('', 10, 'center')], rows, fs=4.7, rh=4.3)
    # program
    rows = []
    for nm, pf, pa, rooms in PROGRAM:
        if rooms == ['__PAVILION__']: a = PAV; f = 'สวน'
        else:
            rs = [r for r in all_rooms() if r.name in rooms]; a = sum(r.a for r in rs); f = 'F%d' % rs[0].fl
        rows.append((nm[:34], 'F%d' % pf, '%.2f' % pa, f, '%.2f' % a, '%+.2f' % (a - pa)))
    tp = sum(p[2] for p in PROGRAM); td = sum(float(r[4]) for r in rows)
    rows.append(('รวม NUA', '', '%.2f' % tp, '', '%.2f' % td, '%+.2f' % (td - tp)))
    colors = [('#fde2e2' if (r[1] != r[3] and r[3] != 'สวน' and r[0] != 'รวม NUA') else None) for r in rows]
    table(ov, 410, 402, [('รายการโปรแกรม', 44, 'left'), ('ชั้น', 7, 'center'), ('โปรแกรม', 13, 'right'), ('ชั้นแบบ', 9, 'center'), ('แบบ', 12, 'right'), ('ต่าง', 12, 'right')],
          rows, fs=5.0, rh=6.0, title='เทียบโปรแกรม ARCHISPACE (ตร.ม.)', colors=colors)
    ov.text(410, 402 - 6.0 * 28 - 4, 'แถบสีชมพู = ชั้นในแบบต่างจากโปรแกรม (ดูเหตุผล A-01 ข้อ 1-2)', fontsize=4.8, va='top', color='#b22222')
    pages.append(fig)

def A11():
    fig, ov = sheet('A-11', 'WELL for Residential\n+ วัสดุ + สิ่งที่ต้องทำต่อ', 'ไม่มีมาตราส่วน')
    wl = [r for r in RES if r[0].startswith('WELL')]
    feat = [
        ('R-A01 ระบบระบายอากาศ', 'พัดลมดูดเฉพาะจุดครัว/ห้องน้ำทุกห้อง + ERV ห้องนอน', 'ระบุในแบบงานระบบ', 'ต้องวัด'),
        ('R-A05 ลดการเผาไหม้', 'ครัวโชว์ใช้เตาไฟฟ้าเหนี่ยวนำ; ครัวไทยแยกปีก มีฮูด >= 510 ลบ.ม./ชม.', 'ในแบบ', 'เอกสาร'),
        ('R-A09 จุดชาร์จ EV', '1 จุดในโรงรถ (ท่อเผื่อ 4 ช่อง)', 'ในแบบ', 'ภาพถ่าย'),
        ('R-W03 น้ำที่ไม่ใช่น้ำดื่ม', 'ถังน้ำฝน 20 ลบ.ม. ใต้คอร์ตน้ำ สำหรับรดน้ำ/ชักโครก', 'ในแบบ', 'แบบสุขาภิบาล'),
        ('R-L01 แสงธรรมชาติ', [r[2] for r in wl if r[0] == 'WELL R-L01'][0][:40], 'คำนวณแล้ว', 'ต้องตรวจแสงจ้า'),
        ('R-L02 ควบคุมแสง', 'วงจรแยกทุกห้อง + ม่านทึบห้องนอน/เธียเตอร์', 'ระบุ', 'แบบไฟฟ้า'),
        ('R-T06 หน้าต่างเปิดได้', [r[2] for r in wl if r[0] == 'WELL R-T06'][0], 'คำนวณแล้ว', 'มุ้งลวด/ตัวล็อก'),
        ('R-T07 ความร้อนภายนอก', 'หลังคาสวน 66% + หลังคาขาว SR >= 0.75 + ต้นไม้ร่มใหญ่ 9 ต้น', 'ในแบบ', 'ค่า SR วัสดุ'),
        ('R-V04 พื้นที่กิจกรรมกลางแจ้ง', 'สระ 16 ม. + ศาลา + คอร์ต 2 แห่ง + สวนรอบอาคาร', 'ในแบบ', '-'),
        ('R-V07 ออกแบบบันได', 'บันไดลำต้นติดผนังกระจกคอร์ตน้ำ เห็นจากโถง ใช้ก่อนลิฟต์', 'ในแบบ', 'ภาพถ่าย'),
        ('R-M01 ธรรมชาติและสถานที่', 'ทุกห้องหลักเห็นคอร์ต/สวน/น้ำ; วัสดุไม้-หิน', 'ในแบบ', '-'),
        ('R-M04 พื้นที่จัดเก็บ', 'Walk-in 33.00 + ตู้เสื้อผ้าทุกห้องนอน + ห้องเก็บ', 'ในแบบ', '-'),
        ('R-N01 การปรุงอาหาร', 'ครัว 2 ส่วน (โชว์/ไทย) + Pantry ห้องเย็น', 'ในแบบ', '-'),
        ('R-S01 แนวกั้นเสียง', 'ห้องนอนหลักไกลถนน 18-25 ม.; เธียเตอร์ผนังกันเสียง', 'ต้องระบุ STC', 'ทดสอบ'),
        ('R-C01 ออกแบบเพื่อทุกคน', 'ทางลาด 1:12 + ลิฟต์ + ห้องนอนแขกชั้น 1', 'ในแบบ', 'ดู A-01 ข้อ 7'),
        ('R-C06 ภัยพิบัติ', 'ยกพื้น +0.60 + ร่องซับน้ำ + เครื่องปั่นไฟ', 'ในแบบ', 'ระดับน้ำท่วมจริง?'),
        ('R-X02 วัสดุ', 'สี/กาว VOC ต่ำ ไม้รับรอง FSC', 'สเปก', 'ใบสั่งซื้อ'),
    ]
    yb = table(ov, 12, 400, [('Feature (WELL for Residential)', 50, 'left'), ('การตอบสนองในแบบ v3', 116, 'left'), ('สถานะ', 25, 'left'), ('หลักฐานที่ต้องมี', 26, 'left')], feat, fs=6.8, rh=8.6,
               title='กลยุทธ์ WELL for Residential (รหัสตาม Guidebook ก.พ. 2026 ในโฟลเดอร์ WELL)')
    para(ov, 12, yb - 4, 215, None, ['สถานะ = เจตนาการออกแบบ ยังไม่ใช่คะแนนรับรอง: WELL Residence ต้องลงทะเบียน IWBI ส่งเอกสาร และตรวจวัดจริงหลังก่อสร้าง (อากาศ น้ำ เสียง แสง)',
                                    'ไม่ได้ประเมินคะแนนรวม — ไม่อ้างว่า "ผ่าน" จนกว่าจะมีผลตรวจ'], fs=6.4)
    mats = [('โครงสร้าง', 'ค.ส.ล. fc\' 280 กก./ตร.ซม. เสา 0.40x0.40 กริด 8x5 · คานถ่ายแรงโรงรถ 11.40 ม. PT/เหล็ก · ฐานรากเสาเข็มเจาะ (รอผลเจาะดิน)'),
            ('ผนังภายนอก', 'บล็อกมวลเบา 200 มม. + ฉาบเรียบสีขาว (ชั้น 2-3) / หินทรายกรุ (ชั้น 1) · ผนังภายใน 120 / ห้องน้ำ 150'),
            ('กระจก', 'Low-E laminated 2 ชั้น · SHGC <= 0.25 ทิศ ตก/ออก, <= 0.35 ทิศใต้หลังครีบ · กรอบอะลูมิเนียมสีเทาเข้ม'),
            ('ผิวอาคาร (CACTUS)', 'ครีบอะลูมิเนียมลายไม้ 80x450 @600 (Crown bar) · ระแนงไม้ 80 @300 ชานบริการ · กันสาดไม้ลึก 1.20 ม.'),
            ('หลังคา', 'ค.ส.ล. + PU 50 + กันซึม + สี SR >= 0.75 · หลังคาสวนระบบ extensive 150 มม.'),
            ('พื้น', 'หินขัดเทอร์ราซโซ (ชั้น 1) · ไม้สักจริงเอ็นจิเนียร์ (ชั้น 2-3) · กระเบื้องกันลื่น R11 ห้องน้ำ'),
            ('ภายนอก', 'สระน้ำเกลือ 16.00x4.50 ลึก 1.40 ม. · พื้นไม้เทียม WPC รอบสระ · ทางรถ หินแกรนิตพ่นทราย')]
    yb2 = table(ov, 236, 400, [('หมวด', 30, 'left'), ('ข้อกำหนด (ระดับแนวคิด)', 244, 'left')], mats, fs=6.2, rh=8.0, title='วัสดุหลัก')
    nxt = ['1. วิศวกรโครงสร้าง: Crown bar เหนือห้องสูง 2 ชั้น, คานโรงรถ 11.40 ม., น้ำหนักหลังคาสวน, เสาเข็ม (ดินอ่อนกรุงเทพฯ)',
           '2. วิศวกรงานระบบ: VRF + ERV, ฮูดครัวไทย, ระบบน้ำฝน/น้ำเทา, เครื่องปั่นไฟ, โซลาร์ 23.1 kWp (คิดเงาครีบ)',
           '3. CFD + จำลองความร้อน: ยืนยันการไหลของลมผ่านปล่อง Termite และคอร์ต (ยังเป็นสมมติฐาน)',
           '4. จำลองแสงและแสงจ้า: พื้นที่กระจกสูง 70% ของพื้นที่ใช้งาน -> ต้องคุมแสงจ้า/ความร้อน',
           '5. ตรวจผังเมืองรวม/ข้อบัญญัติท้องถิ่นของที่ตั้งจริง (FAR, OSR, ระยะร่น, ความสูง)',
           '6. สำรวจระดับดิน-ระดับน้ำท่วมสูงสุด เพื่อยืนยันพื้น +0.60',
           '7. แบบขยาย: บันได, ราวกันตก, ครีบ, สะพานกระจก, ห้องน้ำ Spa, ปล่องลม, สระ',
           '8. ลงทะเบียน WELL Residence และเตรียมเอกสารตามรายการด้านซ้าย',
           '9. ประมาณราคาละเอียด (BOQ) หลังได้แบบโครงสร้าง-งานระบบ']
    yb2 = para(ov, 236, yb2 - 6, 274, 'สิ่งที่ต้องทำต่อ', nxt, fs=6.4)
    summ = ['ผลตรวจทั้งหมด %d รายการ: ผ่าน %d / ไม่ผ่าน %d' % (len(RES), sum(1 for r in RES if r[4]), sum(1 for r in RES if not r[4])),
            'ห้องที่ใช้พัดลมระบาย (ช่องเปิด < 10%%): %s' % ', '.join(INFO['fans']),
            'แบบระดับ design development ต้องให้สถาปนิกและวิศวกรผู้ได้รับใบอนุญาตตรวจสอบและลงนามก่อนยื่นขออนุญาต']
    para(ov, 236, yb2 - 4, 274, 'สรุปการตรวจ', summ, fs=6.4, tcol='#b22222')
    for (f, cap), (x, y, w, h) in zip((('GW3_4_Aerial_NW.png', 'มุมมองทิศตะวันตกเฉียงเหนือ — หลังคาสวน +4.20/+7.80 และแกนลำต้น'), ('GW3_3_Street_North.png', 'จากถนนทิศเหนือ — มุขรถเทียบและโรงรถ 4 คัน')),
                                      ((12, 18, 240, 130), (262, 18, 248, 130))):
        p = REND + f
        if os.path.exists(p):
            ax = fig.add_axes([x / A2[0], y / A2[1], w / A2[0], h / A2[1]]); ax.imshow(Image.open(p).convert('RGB'), aspect='auto'); ax.axis('off')
        ov.text(x, y + h + 1.5, cap, fontsize=6, va='bottom', color='#333')
    pages.append(fig)

# ============================================================== DXF
def build_dxf(path):
    D = DXF()
    m = D.msp
    def title(x, y, t):
        R = Rec(); R.text((x, y), t, 600, 'A-TITLE', ha='left', bold=True); D.add(R)
    # plans side by side
    for i, fl in enumerate((1, 2, 3)):
        R = plan(fl); grid(R, PLAN_VIEW); section_marks(R)
        D.add(R, dx=i * 45000)
        title(i * 45000 + PLAN_VIEW[0], PLAN_VIEW[1] - 1800, 'ผังพื้นชั้น %d  1:100' % fl)
    R = roof_plan(); grid(R, PLAN_VIEW); D.add(R, dx=3 * 45000)
    title(3 * 45000 + PLAN_VIEW[0], PLAN_VIEW[1] - 1800, 'แปลนหลังคา 1:100')
    R = site_plan(); D.add(R, dy=60000)
    title(-3000, 60000 - 5200, 'ผังบริเวณ 1:200 (เขียนขนาดจริง)')
    for i, k in enumerate(('S', 'N', 'E', 'W')):
        R = elevation(k); D.add(R, dx=i * 52000, dy=-30000)
        title(i * 52000, -30000 - 4000, {'S': 'รูปด้านทิศใต้', 'N': 'รูปด้านทิศเหนือ', 'E': 'รูปด้านทิศตะวันออก', 'W': 'รูปด้านทิศตะวันตก'}[k] + ' 1:100')
    for i, k in enumerate(('A', 'B')):
        R = section(k); D.add(R, dx=i * 52000, dy=-60000)
        title(i * 52000, -60000 - 4600, 'รูปตัด %s-%s 1:100' % (k, k))
    D.save(path)

if __name__ == '__main__':
    import sys
    A01(); A02()
    plan_sheet('A-03', 1); plan_sheet('A-04', 2); plan_sheet('A-05', 3)
    roof_sheet()
    elev_sheet('A-07', 'S', 'N', 'รูปด้านทิศใต้\n+ รูปด้านทิศเหนือ')
    elev_sheet('A-08', 'E', 'W', 'รูปด้านทิศตะวันออก\n+ รูปด้านทิศตะวันตก')
    elev_sheet('A-09', 'A', 'B', 'รูปตัด A-A\n+ รูปตัด B-B')
    A10(); A11()
    pdf = os.path.join(OUT, 'WELL-GENWEAVE-40x40-v3-drawings.pdf')
    with PdfPages(pdf) as pp:
        for f in pages:
            pp.savefig(f)
    if '--png' in sys.argv:
        for i, f in enumerate(pages):
            f.savefig('/tmp/well/gw3/sheet_%02d.png' % (i + 1), dpi=60)
    for f in pages: plt.close(f)
    print('pdf', pdf, len(pages))
    if '--dxf' in sys.argv:
        build_dxf(os.path.join(OUT, 'WELL-GENWEAVE-40x40-v3-CAD.dxf'))
        print('dxf ok')
