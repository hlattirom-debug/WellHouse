# -*- coding: utf-8 -*-
"""A2 sheet set (PDF) + DXF assembly for WELL-FORNO 30x30 (4 floors, concept from FORNO / Gruppo FON Architetti)."""
import os, math, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from PIL import Image
from cad6 import draw_mpl, scaled_axes, DXF, Rec
from frame6 import *
from proj6 import project, ground_line, levels, LV
from plan6 import FLOORS, PROGRAM, PROGRAM_NUA, PROGRAM_GFA, all_rooms, CORE_AREA
from walls6 import model, side_of
from draw6 import plan, grid, PLAN_VIEW, north_arrow, section_marks
from proj6 import elevation, section, SECTIONS
from site6 import site_plan, roof_plan
from verify6 import run, areas, cost

A2 = (594, 420)
OUT = '/mnt/user-data/outputs/forno6'
REND = '/mnt/user-data/uploads/WELL/WELL-FORNO-30x30/renders/FO6_'
PROJ = 'WELL-FORNO 30x30 · Executive Luxury Villa · บ้านเดี่ยว 4 ชั้น โครงไม้ภายนอก + หลังคาจั่วไม่สมมาตร + โถงไม้โปร่ง 4 ชั้น (แนวคิดจาก FORNO / Gruppo FON Architetti)'
SITE_TXT = 'ที่ดิน 30.00 x 30.00 ม. (225 ตร.ว.) · ถนน (สมมติ 8.00 ม.) ทิศเหนือ · โปรแกรม ARCHISPACE 6 ต.ค. 2569'
TODAY = '6 ต.ค. 2569'
TITLE_X = 516
PROG_BUDGET, PROG_LO, PROG_HI = 29.54, 26.00, 36.93

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
    ov.text(x, 386, 'WELL-FORNO 30x30', fontsize=8.5, fontweight='bold', va='top')
    ov.text(x, 381, 'Executive Luxury Villa\nบ้านเดี่ยว 4 ชั้น ผ่านเกณฑ์\nWELL for Residential (เจตนา)', fontsize=6.5, va='top', linespacing=1.35)
    ov.text(x, 365, 'ที่ดิน 30.00 x 30.00 ม. = 225 ตร.ว.\nถนนสาธารณะทิศเหนือ (สมมติ 8.00 ม.)', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [355, 355], lw=0.6, c='#111')
    ov.text(x, 352, 'แนวคิด', fontsize=6, color='#777', va='top')
    ov.text(x, 347, 'ตีความจาก FORNO (Gruppo FON):\nโครงไม้ glulam ภายนอกทุกชั้น + ค้ำเอียง\n+ หลังคาจั่วไม่สมมาตร ชายคาใต้ 3.00\n+ โถงไม้ "Forno hall" โปร่ง 4 ชั้น', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [326, 326], lw=0.6, c='#111')
    ov.text(x, 323, 'ระดับ', fontsize=6, color='#777', va='top')
    ov.text(x, 318, '±0.00 ถนน · F1 +0.45 · F2 +3.65\nF3 +6.85 · F4 +10.05\nหลังคาที่แนวผนัง +12.95\nสันหลังคา +14.95', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [298, 298], lw=0.6, c='#111')
    ov.text(x, 294, 'หมายเหตุ', fontsize=6, color='#777', va='top')
    ov.text(x, 289, '· หน่วยเป็นมิลลิเมตร เว้นแต่ระบุ\n· ระดับอ้างอิงถนนหน้าที่ดิน ±0.00\n· ห้ามวัดขนาดจากแบบ ใช้ตัวเลขกำกับ\n· แบบระดับ Design Development\n  ต้องให้สถาปนิกและวิศวกรผู้ได้รับ\n  ใบอนุญาตตรวจสอบและลงนาม\n  ก่อนยื่นขออนุญาต', fontsize=5.6, va='top', linespacing=1.4)
    ov.plot([TITLE_X, A2[0] - 8], [60, 60], lw=0.6, c='#111')
    ov.text(x, 57, 'ชื่อแผ่น', fontsize=6, color='#777', va='top')
    ov.text(x, 52, title, fontsize=7.5, fontweight='bold', va='top', linespacing=1.3, wrap=True)
    ov.plot([TITLE_X, A2[0] - 8], [30, 30], lw=0.6, c='#111')
    ov.text(x, 27, 'มาตราส่วน  %s' % scale_txt, fontsize=6, va='top')
    ov.text(x, 22, 'วันที่  %s   ฉบับ  v1 / DD' % TODAY, fontsize=6, va='top')
    ov.text(A2[0] - 11, 12, no, fontsize=20, fontweight='bold', ha='right', va='bottom')
    ov.text(12, 413, PROJ, fontsize=8, fontweight='bold', va='top')
    ov.text(12, 408.5, SITE_TXT, fontsize=6, color='#555', va='top')
    return fig, ov

def table(ov, x, y, cols, rows, fs=5.6, head=True, rh=None, title=None, colors=None):
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

def thai_len(s):
    return sum(0 if ('ั' == c or 'ิ' <= c <= 'ฺ' or '็' <= c <= '๎') else 1 for c in s)
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

def place(fig, R, view, x_mm, y_mm, sc):
    ax = scaled_axes(fig, x_mm, y_mm, view, sc)
    draw_mpl(ax, R, sc)
    return ax

def scalebar(ov, x, y, sc, m=5):
    L = m * 1000 / sc
    for i in range(m):
        ov.add_patch(Rectangle((x + i * L / m, y), L / m, 1.2, fc='#111' if i % 2 == 0 else 'white', ec='#111', lw=0.4))
    ov.text(x, y + 2, '0', fontsize=5.5, ha='center'); ov.text(x + L, y + 2, '%d ม.' % m, fontsize=5.5, ha='center')

def image(fig, ov, f, x, y, w, h, cap=None, cap_above=False):
    p = REND + f
    if os.path.exists(p):
        ax = fig.add_axes([x / A2[0], y / A2[1], w / A2[0], h / A2[1]]); ax.imshow(Image.open(p).convert('RGB'), aspect='auto'); ax.axis('off')
    if cap:
        if cap_above: ov.text(x, y + h + 1.5, cap, fontsize=6, va='bottom', color='#333')
        else: ov.text(x, y - 1.5, cap, fontsize=5.6, va='top', color='#333')

# ============================================================== data
RES, INFO = run()
M = model()
AR, PAV = areas()
C = cost()
CIRC = sum(r.a for r in all_rooms() if r.kind in ('circ', 'stair', 'lift'))
CORE4 = CORE_AREA * 4
LOGGIA3 = AR[2][2]
VERANDA = AR[0][2]
ENC = sum(a[1] for a in AR); SEMI = sum(a[2] for a in AR) + PAV; PARK = sum(a[3] for a in AR); FST = sum(a[4] for a in AR)
KIND = {'room': 'ห้องใช้งาน', 'wet': 'ห้องน้ำ/เปียก', 'svc': 'บริการ', 'circ': 'สัญจร', 'stair': 'บันได', 'lift': 'ลิฟต์', 'core': 'โดม (วงกลม)',
        'fstair': 'บันไดหนีไฟ', 'inb': 'กึ่งภายนอก', 'park': 'จอดรถ', 'void': 'ช่องโล่ง', 'shaft': 'ช่องท่อ'}

def room_rows(fl):
    rows = []
    for r in FLOORS[fl]:
        if 'ส่วนต่อเนื่อง' in r.name: continue
        a = r.a + sum(q.a for q in FLOORS[fl] if q.name == r.name + ' (ส่วนต่อเนื่อง)')
        if r.kind == 'core': a = CORE_AREA
        rows.append((r.code, r.name[:34], '%.2f x %.2f' % (r.w / 1000, r.d / 1000) if r.kind != 'core' else 'Ø 5.60', '%.2f' % a, KIND.get(r.kind, r.kind)))
    return rows

ROOMCOLS = [('รหัส', 9, 'center'), ('ห้อง', 52, 'left'), ('ขนาด ม.', 20, 'center'), ('ตร.ม.', 12, 'right'), ('ประเภท', 19, 'left')]
pages = []

# ============================================================== A-01 concept + limitations
def A01():
    fig, ov = sheet('A-01', 'แนวคิด FORNO -> บ้านโครงไม้\n+ รายงานข้อจำกัด', 'ไม่มีมาตราส่วน')
    imgs = [('CAM_1_Aerial_SE.png', 'มุมมองทางอากาศ ทิศตะวันออกเฉียงใต้ — หลังคาจั่วไม่สมมาตรคลุมแท่ง 23.00 x 13.00 ม. แผงโซลาร์ลาดใต้ ช่องแสงสันหลังคา'),
            ('CAM_6_Gable_West.png', 'หน้าจั่วทิศตะวันตก — ระแนงไม้ทแยง คอร์ตแสงหัวท้าย และเฟรมไม้ glulam ด้านใต้'),
            ('CAM_2_Garden_South.png', 'จากสวนสระทิศใต้ — เสาโครงไม้ภายนอก + ค้ำเอียงรับชายคา 3.00 ม. ระเบียงไม้ทุกชั้น ผนังกระจกเต็มบาน'),
            ('CAM_3_Street_North.png', 'จากถนนทิศเหนือ — เสาไม้หน้าโรงจอดรถ 4 คัน บันไดหนีไฟเหล็ก ทางเดินเข้าบ้านทิศตะวันออก')]
    pos = [(12, 283, 160, 100), (176, 283, 160, 100), (12, 172, 160, 100), (176, 172, 160, 100)]
    for (f, cap), (x, y, w, h) in zip(imgs, pos):
        image(fig, ov, f, x, y, w, h, cap)
    ov.text(12, 400, 'ภาพจากโมเดล Blender (WELL-FORNO-30x30-model.blend) — โมเดลมวลอาคารระดับ DD สร้างจากข้อมูลชุดเดียวกับแบบ CAD', fontsize=6, color='#555', va='top')
    concept_diagrams(fig, ov)
    X0, W0 = 342, 170
    facts = [('ผู้ออกแบบ', 'Gruppo FON Architetti'),
             ('ที่ตั้ง / ปี', 'Treviso อิตาลี · แล้วเสร็จ 2025'),
             ('ประเภท (Architizer)', 'Commercial: Retail / Restaurant & Bar / Community Center — ไม่ใช่บ้านพักอาศัย'),
             ('บริบท', 'ย่านชานเมืองทิศตะวันตกเฉียงเหนือที่พัฒนาเป็นหย่อม ๆ; อาคาร + ลานภายนอกเปิดให้สาธารณะ ใกล้ลานจอดรถขนาดใหญ่'),
             ('โครงการ', 'ธุรกิจเบเกอรี่/ค้าปลีกเอกชน ได้ทุนสนับสนุนผู้ประกอบการระดับภูมิภาค · เปิด 15 ชม./วัน 7 วัน'),
             ('สถาปัตยกรรม', '"light wooden architecture, transparent and strongly recognizable" (ข้อความโครงการ) — เป็นหมุดหมายของย่าน'),
             ('จากภาพที่เผยแพร่', 'โครงไม้ glulam + ค้ำเอียง/รูปตัว Y · หลังคาจั่วไม่สมมาตร ชายคายื่นลึก · ผนังกระจก · หน้าจั่วโครงไม้ทแยง · ด้านสูงหันสู่สวน'),
             ('ไม่เผยแพร่', 'พื้นที่ ขนาด แบบก่อสร้าง — ทุกมิติในชุดนี้ออกแบบใหม่')]
    yb = table(ov, X0, 398, [('หัวข้อ', 26, 'left'), ('ข้อเท็จจริงจากหน้า Architizer (ข้อความ + ภาพ)', 144, 'left')], facts, fs=5.7,
               title='FORNO — ข้อเท็จจริงที่ตรวจได้')
    interp = [('จั่วไม่สมมาตร', 'หลังคาจั่วเดียวคลุมทั้งแท่ง: ลาดใต้ 40% ชายคา 3.00 ม. คลุมระเบียง/piazza · ลาดเหนือ 25% · สัน +14.95'),
              ('โครงไม้ + ค้ำ Y', 'exoskeleton ทิศใต้ 9 เฟรม @2.875 ม.: เสา glulam 240x480 + ค้ำเอียงรับปลายชายคา + คานขอบระเบียงทุกชั้น'),
              ('โถงยาวเดียว', '"Forno hall" กว้าง 3.00 ม. ยาว 16.90 ม. โปร่ง 4 ชั้นถึงช่องแสงสันหลังคา มีสะพานไม้ข้ามชั้น 2-4'),
              ('ความโปร่งใส', 'ผนังกระจกเต็มบานหลังระเบียงไม้ทิศใต้ทุกห้องหลัก (ห้องอาหาร นั่งเล่น Master)'),
              ('หน้าจั่วทแยง', 'ระแนงไม้ทแยงหน้าจั่วตะวันออก/ตะวันตก + คอร์ตแสงหัวท้ายชั้น 3-4'),
              ('ลานสาธารณะ / เตาอบ', 'piazza ใต้ชายคา + ศาลาริมสระ + เตาอบฟืน (forno) + โต๊ะยาวในโถงกลาง'),
              ('ไม่นำมาใช้', 'ไม้เป็นโครงสร้างหลัก (บ้าน 4 ชั้นใช้ ค.ส.ล.) · กระจกรอบด้าน (ตะวันออก/ตะวันตกร้อน)')]
    yb = table(ov, X0, yb - 7, [('องค์ประกอบ', 26, 'left'), ('การตีความของเรา (ไม่ใช่คำอธิบายของสถาปนิก)', 144, 'left')], interp, fs=5.7,
               title='การตีความ -> แบบบ้านหลังนี้')
    lim = [
        '1. FORNO เป็นอาคารพาณิชย์ชั้นเดียว ไม่ใช่บ้าน — การแปลงเป็นบ้าน 4 ชั้นและทุกมิติเป็นการตีความของเรา',
        '2. "โครงไม้ภายนอกทุกชั้น" ไม่ใช่โครงสร้างหลัก: โครงหลัก ค.ส.ล. (อาคาร 3 ชั้นขึ้นไปต้องใช้โครงสร้างทนไฟ) ไม้รับระเบียง/ชายคา; โครงหลังคาและแปไม้ต้องให้วิศวกรตรวจอัตราทนไฟ',
        '3. โปรแกรมขัดกัน: Master ชั้น 3 แต่ Closet + Terrace ชั้น 4 -> Master duplex มีบันไดส่วนตัว; Pantry ชั้น 3 ย้ายไปชั้น 2 ติดครัว',
        '4. GFA %.2f vs โปรแกรม %.2f (%+.1f%%): กึ่งภายนอกชั้น 3 %.1f + ชั้น 4 %.1f ตร.ม. เพราะโปรแกรมชั้น 3 มีแค่ 120 ตร.ม. แต่แท่งอาคารทุกชั้นเท่ากัน' %
        (C['gfa'], PROGRAM_GFA, C['gfa'] / PROGRAM_GFA * 100 - 100, LOGGIA3, AR[3][2]),
        '5. เล็กกว่าโปรแกรมเกิน 10%: ไวน์ -31%, ห้องน้ำแม่บ้าน -25%, โถงต้อนรับ -21% (ความสูง 2 ชั้นได้จากโถงไม้ข้างกัน), เธียเตอร์ -14%, MEP -14%, โรงรถ -10% (A-11)',
        '6. ระยะชนเกณฑ์: สันหลังคา +14.95 (ต่ำกว่า 15.00 แค่ 0.05); ชั้น 4 โปร่ง 2.60 พอดีที่ผนังชายคา; ลิฟต์บ้านต้องเป็นรุ่น overhead <= 2.60 ม.',
        '7. ทางเข้าบันไดหนีไฟ ชั้น 2 ผ่านห้องทำงาน ชั้น 4 ผ่านห้องเธียเตอร์ (ห้ามล็อกประตู) — ต้องยืนยันข้อ 27 กับสำนักงานเขตสำหรับบ้านเดี่ยว',
        '8. โถงโปร่ง 4 ชั้นเชื่อมทุกชั้น — ควันไฟลามขึ้นได้: ต้องมีเครื่องตรวจจับควัน/ช่องระบายควันที่สันหลังคา; ช่องเปิดสู่โถงไม่นับเป็นช่องเปิด ฉ.39',
        '9. ห้องเปิดด้านเดียว/ลึกเกิน 4.20 ม. (ยกเว้นพร้อมเหตุผล): แม่บ้าน 1, Junior Suite 3, ห้องทำงาน, ห้องนั่งเล่นครอบครัว; ใช้พัดลมระบาย %d ห้อง (A-12)' % len(INFO['fans']),
        '10. ไม้ภายนอกในภูมิอากาศร้อนชื้น: ต้องอัดน้ำยากันปลวก/เชื้อรา เคลือบกัน UV ฐานเหล็กยกพ้นดิน 0.30 ม. และบำรุงรักษาทุก 2-3 ปี; คอร์ตเปิดหัวท้ายรับฝนสาด ต้องมีท่อระบายของตัวเอง',
        '11. ความกว้างถนนสมมติ 8.00 ม.; ทางลาดโรงรถ +0.15 -> +0.45 ยังไม่เขียน; ไม่ทราบผังเมืองรวม/ข้อบัญญัติท้องถิ่น — ต้องตรวจก่อนยื่น',
    ]
    yb = para(ov, X0, yb - 4, W0, 'รายงานข้อจำกัด (ตรงไปตรงมา)', lim, fs=5.9, gap=0.8, tcol='#b22222')
    para(ov, X0, yb - 3, W0, 'แหล่งข้อมูลอ้างอิง FORNO', [
        '· architizer.com/projects/forno-1 (ลิงก์ที่ผู้ใช้ให้มา) — อ่านข้อความโครงการและดูภาพเมื่อ 6 ต.ค. 2569',
        'ไม่ได้รับแบบจริงของโครงการ — ไม่มีขนาด/พื้นที่ของงานต้นแบบ'], fs=5.8)
    pages.append(fig)

def concept_diagrams(fig, ov):
    import math as _m
    R = Rec()
    zc = {'park': '#cfcfcf', 'inb': '#efe3c8', 'circ': '#f6d36b', 'stair': '#c99d68', 'lift': '#c99d68', 'fstair': '#8a9098',
          'room': '#a9cbe8', 'wet': '#cfe3ee', 'svc': '#d9d2e9', 'void': '#ffffff'}
    R.rect(0, 0, LOT_W, LOT_D, 'C-PROP', lw=0.4)
    R.frect(POOL[0], POOL[1], POOL[2], POOL[3], 'A-AREA', color='#7fb7d0', z=1)
    R.frect(PIAZZA[0], PIAZZA[1], PIAZZA[2], PIAZZA[3], 'A-AREA', color='#e6dccb', z=1)
    for r_ in FLOORS[1]:
        R.frect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-AREA', color=zc.get(r_.kind, '#ddd'), z=1)
        R.rect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-WALL-INT', lw=0.12)
    for x in FRAME_X: R.frect(x - 200, FRAME_S_Y - 600, x + 200, FRAME_S_Y, 'A-AREA', color='#8a5a2b', z=2)
    for x in FRAME_N_X: R.frect(x - 200, FRAME_N_Y - 300, x + 200, FRAME_N_Y + 300, 'A-AREA', color='#8a5a2b', z=2)
    R.rect(BLK[0] - OVER_EW, BLK[1] - OVER_S, BLK[2] + OVER_EW, BLK[3] + OVER_N, 'A-HIDD', ls='--', lw=0.3)
    R.text((16500, 14000), '"Forno hall"', 520, 'A-TEXT', bold=True)
    R.text((10900, 9300), 'ศาลา', 480, 'A-TEXT', bold=True)
    R.text((9800, 18300), 'โรงจอดรถ', 480, 'A-TEXT', bold=True)
    R.text((24600, 18000), 'ทางเข้า', 420, 'A-TEXT', bold=True)
    R.text((13000, 5350), 'piazza ใต้ชายคา 3.00 ม.', 420, 'A-TEXT', bold=True)
    R.text((13000, 28200), 'ถนน (ทิศเหนือ)', 520, 'A-TEXT', bold=True)
    R.text((12000, 2700), 'สระ', 480, 'A-TEXT', bold=True)
    north_arrow(R, (28200, 28000), 700)
    V = (-1000, -800, 31000, 31000)
    place(fig, R, V, 14, 22, 250)
    ov.text(14, 154, 'ไดอะแกรมผังชั้น 1 (1:250): ทางเข้าตะวันออก -> โถงไม้ยาว -> ศาลา/สระ; เสาโครงไม้ใต้-เหนือ; แนวชายคา (เส้นประ)', fontsize=6.3, fontweight='bold', va='top')
    from model6 import build
    BX, _ = build()
    S = project('W', BX, cut=('x', 14000), cutdepth=14000)
    ground_line(S, 'W', -1500, LOT_D + 1500)
    def arrow(a, b, lw=0.9, c='A-ANNO'):
        S.line(a, b, c, lw=lw)
        ang = _m.atan2(b[1] - a[1], b[0] - a[0])
        S.pline([(b[0] - 700 * _m.cos(ang - .4), b[1] - 700 * _m.sin(ang - .4)), b, (b[0] - 700 * _m.cos(ang + .4), b[1] - 700 * _m.sin(ang + .4))], c, lw=lw)
    u = lambda y: LOT_D - y
    arrow((u(500), 1800), (u(7000), 1900)); arrow((u(7000), 1900), (u(13000), 2300))
    for z in (5300, 8500): arrow((u(5500), z), (u(12800), z + 300), 0.6)
    arrow((u(13400), 3000), (u(13400), 13200)); arrow((u(13400), 13200), (u(13300), 15600))
    S.line((u(-2500), 17500), (u(4500), roof_z(4500) - 300), 'A-HIDD', lw=0.8, ls='--')
    S.text((u(-600), 16600), 'แดดสูง (ฤดูร้อน)\nถูกชายคา 3.00 ม. บัง', 330, 'A-ANNO')
    S.text((u(3500), 2700), 'ลมใต้/ตะวันตกเฉียงใต้', 380, 'A-ANNO')
    S.text((u(13300) - 200, 16200), 'ระบายที่ช่องแสงสันหลังคา', 380, 'A-ANNO')
    V2 = (-1800, -2800, 32500, 18600)
    place(fig, S, V2, 186, 30, 250)
    ov.text(186, 154, 'ไดอะแกรมรูปตัด B-B (x = 14.00, 1:250): ลมเข้าใต้ชายคา -> ห้องทิศใต้ -> โถงไม้ -> ลอยขึ้นตามช่องโล่ง (stack)', fontsize=6.3, fontweight='bold', va='top')
    ov.text(186, 26, 'ลูกศร = เจตนาการออกแบบ (ลมประจำกรุงเทพฯ ฤดูร้อน S/SW, หนาว NE) — ยังไม่ได้พิสูจน์ด้วย CFD/การจำลองความร้อน', fontsize=5.4, color='#b22222', va='top')

# ============================================================== A-02 site
def A02():
    fig, ov = sheet('A-02', 'ผังบริเวณ + ตารางกฎหมาย\n+ ประมาณราคา', '1:150')
    R = site_plan()
    V = (-3300, -3200, 33800, 38300)
    place(fig, R, V, 12, 24, 150)
    ov.text(14, 20, 'ผังบริเวณ  SITE PLAN  1:150', fontsize=8.5, fontweight='bold', va='top')
    scalebar(ov, 120, 13, 150, 10)
    law = [r for r in RES if r[0].startswith('ฉ.55') or r[0] == 'ร่นแนวถนน']
    rows = [(g.replace('ฉ.55 ', ''), i[:46], v[:36], c[:26], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in law]
    yb = table(ov, 266, 400, [('ข้อ', 15, 'left'), ('รายการ', 72, 'left'), ('ค่าในแบบ', 54, 'left'), ('เกณฑ์', 38, 'left'), ('ผล', 11, 'center')], rows, fs=5.1,
               title='ตรวจกฎกระทรวง ฉบับที่ 55 (2543) และระยะร่น')
    ov.text(266, yb - 2, '* ร่นแนวถนน: อาคารสูงไม่เกิน 15 ม. ถนนกว้าง 6-20 ม. ร่น 1/10 ของความกว้างถนน (ความกว้างถนนเป็นค่าสมมติ — ตรวจซ้ำกับข้อบัญญัติท้องถิ่น)', fontsize=4.7, va='top', color='#555')
    rows = []
    for fl, enc, semi, park, fst in AR:
        rows.append(('ชั้น %d' % fl, '%.2f' % enc, '%.2f' % semi, '%.2f' % park if park else '-', '%.2f' % fst, '%.2f' % (enc + semi + park)))
    rows += [('รวม', '%.2f' % ENC, '%.2f' % SEMI, '%.2f' % PARK, '%.2f' % FST, '%.2f' % C['gfa']),
             ('โปรแกรม', '', '', '', '', '%.2f' % PROGRAM_GFA),
             ('ส่วนต่าง', '', '', '', '', '%+.2f (%+.1f%%)' % (C['gfa'] - PROGRAM_GFA, C['gfa'] / PROGRAM_GFA * 100 - 100))]
    yb = table(ov, 266, yb - 9, [('ชั้น', 26, 'left'), ('ปิดล้อม*', 28, 'right'), ('กึ่งภายนอก', 28, 'right'), ('จอดรถ', 24, 'right'), ('บันไดหนีไฟ', 26, 'right'), ('รวม ตร.ม.', 36, 'right')],
               rows, fs=5.0, title='พื้นที่อาคาร (คิดถึงแนวศูนย์กลางผนัง)')
    ov.text(266, yb - 1.5, '* ไม่นับช่องโล่งโถงไม้ · ลานใต้ชายคาชั้น 1 = ศาลาริมสระตามโปรแกรม (กึ่งภายนอก) · บันไดหนีไฟไม่รวม', fontsize=4.7, va='top', color='#555')
    rows = [('พื้นที่ดิน', '900.00 ตร.ม. (225 ตร.ว.)'), ('พื้นที่อาคารคลุมดิน (รวมชายคา/บันไดหนีไฟ)', '%.2f ตร.ม. (%.1f%%)' % (INFO['cover'], INFO['cover'] / 9)),
            ('ที่ว่าง', '%.1f%%  (เกณฑ์ >= 30%%)' % INFO['os1']), ('FAR (GFA ปิดล้อม / ที่ดิน)', '%.2f : 1' % (ENC / 900)),
            ('ความสูงอาคาร', 'ยอดผนังชั้นบนสุด 12.95 (วิธีวัดหลังคาจั่ว) / สันหลังคา 14.95 ม. (< 15.00)'),
            ('ที่ดินขั้นต่ำตามโปรแกรม', '113 ตร.ว. — ที่ดินจริง 225 ตร.ว.')]
    yb = table(ov, 266, yb - 9, [('รายการ', 62, 'left'), ('ค่า', 116, 'left')], rows, fs=5.0, title='ที่ว่างและการใช้ที่ดิน')
    rows = [('(ก) อัตราแยกมาตรฐาน', 'ปิดล้อม %.2f x 22,000 + กึ่งภายนอก %.2f x 11,000 + จอดรถ %.2f x 8,000' % (C['enc'], C['semi'], C['park']), '%.2f' % (C['std'] / 1e6)),
            ('(ข) อัตราแยก luxury', 'ปิดล้อม x 30,000 + กึ่งภายนอก x 15,000 + จอดรถ x 12,000', '%.2f' % (C['lux'] / 1e6)),
            ('(ค) อัตราเดียว (วิธีเดียวกับโปรแกรม)', 'GFA %.2f x 30,000' % C['gfa'], '%.2f' % (C['single'] / 1e6)),
            ('งานนอกอาคาร', 'สระ %.1f ตร.ม. x 35,000 + PV %.2f kWp x 45,000 + ภูมิทัศน์/รั้ว 1.80 + ลิฟต์ 0.90 + บันไดหนีไฟ 1.20 + โครงไม้/หลังคา glulam 2.50 ล.' % (C['pool'], C['kwp']), '%.2f' % (C['extra'] / 1e6)),
            ('โปรแกรม ARCHISPACE', '984.70 x 30,000 (ช่วง %.2f-%.2f ล้าน)' % (PROG_LO, PROG_HI), '%.2f' % PROG_BUDGET)]
    yb = table(ov, 266, yb - 9, [('วิธีคิด', 48, 'left'), ('สูตร (บาท/ตร.ม.)', 112, 'left'), ('ล้านบาท', 18, 'right')], rows, fs=4.9, title='ประมาณราคาค่าก่อสร้าง (ระดับแนวคิด)')
    para(ov, 266, yb - 3, 240, None, [
        'อัตราแยก vs อัตราเดียว: (ก) %.2f ล้าน ต่ำกว่างบโปรแกรม; (ข) %.2f ล้าน อยู่ในช่วง %.2f-%.2f; (ค) %.2f ล้าน แตะขอบบนของช่วง เพราะ GFA มากกว่าโปรแกรม %.1f%%' %
        (C['std'] / 1e6, C['lux'] / 1e6, PROG_LO, PROG_HI, C['single'] / 1e6, C['gfa'] / PROGRAM_GFA * 100 - 100),
        'รวมงานนอกอาคาร: (ข)+%.2f = %.2f ล้าน · (ค)+%.2f = %.2f ล้าน (เกินช่วงบนของโปรแกรม)' % (C['extra'] / 1e6, (C['lux'] + C['extra']) / 1e6, C['extra'] / 1e6, (C['single'] + C['extra']) / 1e6),
        'ยังไม่รวม: เสาเข็ม/ฐานราก (รอผลเจาะดิน), เฟอร์นิเจอร์ลอยตัว, ภาษี/ค่าธรรมเนียม, ค่าออกแบบ'], fs=4.9)
    pages.append(fig)

# ============================================================== plans
TITLES = {1: 'ผังพื้นชั้น 1  (FFL +0.45)', 2: 'ผังพื้นชั้น 2  (FFL +3.65)', 3: 'ผังพื้นชั้น 3  (FFL +6.85)', 4: 'ผังพื้นชั้น 4  (FFL +10.05)'}
NOTES = {1: ['· ทางเข้าหลักทิศตะวันออก (ทางเดินจากถนนข้างรั้ว) -> โถงต้อนรับ -> โถงกลาง "Forno hall" กว้าง 3.00 ม. โปร่งถึงช่องแสงสันหลังคา',
             '· โถงกลางเปิดบานเลื่อน 4.80 ม. สู่ศาลาริมสระ (piazza ใต้ชายคา) — โต๊ะยาว + เตาอบฟืน (forno) ตามแนวคิดเบเกอรี่',
             '· โรงจอดรถ 4 คัน ด้านหน้าเปิด เสาไม้ glulam @2.875 ม. เป็นช่องจอด (ช่องว่างระหว่างเสา 2.64 ม.) ประตูคู่สู่โถงกลาง; ทางลาด 1:12 ต้องเพิ่ม',
             '· ห้องนอนแขก (ผู้สูงอายุ) มุมตะวันตกเฉียงใต้ เข้าทางตู้เสื้อผ้า เปิดสู่ศาลา · ครัวไทยมีประตูบริการทิศใต้',
             '· จุดชาร์จรถไฟฟ้า (EV) 1 จุดในโรงรถ (WELL R-A09) · เสาไม้ทิศใต้ตั้งบนฐานเหล็กสูง 0.30 ม.'],
         2: ['· ส่วนรวมทิศใต้: ครัวโชว์ -> ห้องอาหาร 12 ที่นั่ง -> ห้องนั่งเล่น ผนังกระจกเต็มบานออกระเบียงไม้ยาว 23.00 ม.',
             '· สะพานไม้ข้ามโถงไม้จากแกลเลอรี (หน้าบันได) สู่ห้องนั่งเล่น; ห้องอาหาร/นั่งเล่นมีหน้าต่างภายในมองลงโถง',
             '· Pantry ย้ายจากชั้น 3 (โปรแกรม) มาติดครัวโชว์ · ห้องไวน์/ซิการ์ไม่มีหน้าต่าง (ตั้งใจ) เข้าจากแกลเลอรี',
             '· Junior Suite 2 เข้าผ่านตู้เสื้อผ้า (walk-through); Junior Suite 3 เข้าจากแกลเลอรี · ห้องทำงานมีทางออกบันไดหนีไฟ'],
         3: ['· ชั้น Master: สะพานไม้ -> ห้องนอน Master -> Walk-in -> ห้องน้ำ Spa; บันไดส่วนตัวปลายตะวันออกขึ้นชั้น 4 (Master duplex)',
             '· ระเบียงไม้ทิศใต้ชั้น 3 เป็นของ Master · ลอจเจียทิศเหนือ 12.80 x 5.00 ม. ราวระแนงไม้ (ส่วนเกินโปรแกรม -> ลานครอบครัวกึ่งภายนอก)',
             '· คอร์ตแสงหัวท้าย (พื้นกรวดบนหลังคาชั้น 2) เปิดด้านสกัดใต้หลังคา นำแสงเข้าโถงไม้ทางผนังกระจก',
             '· ทางหนีไฟชั้น 3: แกลเลอรี -> โถงลิฟต์ -> ลอจเจียตะวันออกเฉียงเหนือ -> บันไดหนีไฟ'],
         4: ['· ใต้หลังคาลาด: โปร่ง 2.60 ม. ที่ผนังชายคา สูงขึ้นถึง 4.60 ม. ที่สัน; แปไม้ glulam เปิดโชว์ทุกเฟรม',
             '· ระเบียง & BBQ (สาธารณะของบ้าน) เข้าจากสะพานไม้ชั้น 4; ผนังกั้นจากระเบียง Master · ระเบียง Master + อ่างแช่ เข้าจาก Closet',
             '· ห้องนั่งเล่นครอบครัวเปิด 2.40 ม. สู่แกลเลอรี (Upper Gallery) · ห้องโฮมเธียเตอร์มีทางออกบันไดหนีไฟ (ห้ามล็อก)',
             '· หลังคาลาดใต้: แผงโซลาร์ %d แผง = %.2f kWp' % (round(C['kwp'] / 0.55), C['kwp'])]}

def plan_sheet(no, fl):
    fig, ov = sheet(no, TITLES[fl].replace('  ', '\n'), '1:100')
    R = plan(fl)
    grid(R, PLAN_VIEW)
    north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 2200), 800)
    section_marks(R)
    place(fig, R, PLAN_VIEW, 12, 60, 100)
    ov.text(14, 55, TITLES[fl] + '   1:100', fontsize=9, fontweight='bold', va='top')
    scalebar(ov, 150, 49, 100, 5)
    rows = room_rows(fl)
    yb = table(ov, 382, 400, ROOMCOLS, rows, fs=5.5, title='ตารางห้อง ชั้น %d' % fl)
    _, enc, semi, park, fst = AR[fl - 1]
    yb = table(ov, 382, yb - 6, [('สรุปชั้น %d' % fl, 60, 'left'), ('ตร.ม.', 52, 'right')],
               [('พื้นที่ปิดล้อม', '%.2f' % enc), ('กึ่งภายนอก', '%.2f' % semi), ('จอดรถ', '%.2f' % park), ('รวม', '%.2f' % (enc + semi + park)),
                ('บันไดหนีไฟภายนอก (ไม่รวม)', '%.2f' % fst)], fs=5.2)
    para(ov, 382, yb - 6, 130, 'หมายเหตุ', NOTES[fl], fs=5.8)
    pages.append(fig)

def roof_sheet():
    fig, ov = sheet('A-07', 'แปลนหลังคา', '1:100')
    R = roof_plan()
    grid(R, PLAN_VIEW)
    place(fig, R, PLAN_VIEW, 12, 60, 100)
    ov.text(14, 55, 'แปลนหลังคา  ROOF PLAN   1:100', fontsize=9, fontweight='bold', va='top')
    scalebar(ov, 150, 49, 100, 5)
    ra = INFO['roofs']
    rows = [('หลังคาจั่ว (แปลน รวมชายคา) 25.00 x 17.00 ม.', '%.2f' % ra['gable']), ('  - แผงโซลาร์บนลาดใต้', '%.2f' % ra['pv']),
            ('  - ช่องแสงสันหลังคา 13.10 x 1.55 ม.', '%.2f' % (13.1 * 1.55)),
            ('หลังคาโรงรถ +3.65 (ใต้ชายคา)', '%.2f' % ra.get('flat', 0)), ('พื้นคอร์ตแสง +6.85 (กรวด ใต้หลังคา)', '%.2f' % ra.get('court', 0))]
    yb = table(ov, 382, 400, [('หลังคา', 80, 'left'), ('ตร.ม.', 32, 'right')], rows, fs=5.4, title='พื้นที่หลังคา')
    rows = [('ฝนรายปีกรุงเทพฯ (ประมาณ)', '~1,500 มม./ปี'), ('น้ำฝนจากหลังคาจั่ว (C=0.9)', '%.0f ลบ.ม./ปี' % (ra['gable'] * 0.9 * 1.5)),
            ('ถังเก็บน้ำฝนใต้ดิน 3.00 x 2.50 ม.', '~12 ลบ.ม. (รดน้ำ/ชักโครก)'), ('แผงโซลาร์ %d x 550 Wp' % round(C['kwp'] / 0.55), '%.2f kWp ~ %s kWh/ปี*' % (C['kwp'], format(round(C['kwp'] * 1250, -2), ',.0f'))),
            ('ความลาด ใต้ / เหนือ', '40%% (%.1f°) / 25%% (%.1f°)' % (math.degrees(math.atan(SLOPE_S)), math.degrees(math.atan(SLOPE_N)))),
            ('ระดับ สัน / แนวผนัง / ปลายชายคาใต้ / เหนือ', '+%.2f / +%.2f / +%.2f / +%.2f' % (RIDGE / 1000, EAVE / 1000, roof_z(BLK[1] - OVER_S) / 1000, roof_z(BLK[3] + OVER_N) / 1000))]
    yb = table(ov, 382, yb - 8, [('รายการ', 62, 'left'), ('ค่า', 50, 'left')], rows, fs=5.0, title='น้ำฝน พลังงาน และระดับ')
    para(ov, 382, yb - 4, 130, 'ชั้นหลังคา', [
        '· หลังคาจั่ว: เหล็กรีดลอน standing seam เคลือบสีอ่อน (SR >= 0.75 — ต้องยืนยันสเปก) + ฉนวน PIR 75 มม. + แผ่นกันชื้น + ไม้ระแนงรองรับ + แปไม้ glulam',
        '· ฝ้าใต้หลังคา: ไม้สน/ซีดาร์ เคลือบกันไฟ (ต้องตรวจอัตราทนไฟ) · แปไม้ 160 x 400 ทุกเฟรม @2.875 ม. เปิดโชว์',
        '· ช่องแสงสันหลังคา: กระจก laminated Low-E ลาดตามหลังคา มีบานเปิดระบายอากาศ/ควันอัตโนมัติ (เจตนา stack effect)',
        '· รางน้ำเหล็กกล่องปลายชายคาทั้งสองด้าน -> ท่อลง RD ตามเสาไม้ -> รางรอบอาคาร -> ถังน้ำฝน',
        '· ปลายชายคาใต้ยื่น 3.00 ม. รับด้วยค้ำเอียงไม้จากเสาทุกเฟรม (สมดุลแรงลมยก ต้องให้วิศวกรตรวจ)',
        '* พลังงาน PV ประมาณ ~1,250 kWh/kWp/ปี ที่ความเอียง 21.8° หันใต้ — ต้องคำนวณจริงรวมเงาสันหลังคา'], fs=5.0)
    pages.append(fig)

ENAMES = {'S': 'รูปด้านทิศใต้ (สวน/สระ — เฟรมไม้ภายนอก + ระเบียงไม้)', 'N': 'รูปด้านทิศเหนือ (ถนน — เสาไม้หน้าโรงรถ / บันไดหนีไฟ)',
          'E': 'รูปด้านทิศตะวันออก (หน้าจั่วไม่สมมาตร — ทางเข้า)', 'W': 'รูปด้านทิศตะวันตก (หน้าจั่ว + ระแนงไม้ทแยง)'}
ENOTES = ['วัสดุผิว (ระดับแนวคิด)', '· โครงไม้ภายนอก: glulam (สนยุโรป/ไม้ทนทาน) อัดน้ำยา + เคลือบกัน UV ฐานเหล็กยกพ้นดิน 0.30 ม.',
          '· ชั้น 1: ผนังปูนฉาบขาว (lime render) · ชั้น 2-4: ผนัง ค.ส.ล./บล็อก + ไม้กรุแนวตั้ง (มีช่องระบายอากาศหลังไม้)',
          '· หลังคา: เหล็กรีดลอน standing seam สีอ่อน + แผงโซลาร์ลาดใต้ + ช่องแสงสันหลังคา',
          '· หน้าจั่ว: ระแนงไม้ทแยง 60 x 80 @1.20 ม. (เหนือระดับ +12.00) · คอร์ตแสงหัวท้ายราวไม้ 1.10 ม.',
          '· กระจก Low-E laminated กรอบอะลูมิเนียมสีบรอนซ์ · ราวกระจก 1.10 ม. + มือจับไม้',
          '· บันไดหนีไฟ: เหล็กกัลวาไนซ์ทาสี ราว 1.10 ม.']

def elev_sheet(no, a, b, title):
    fig, ov = sheet(no, title, '1:100')
    for i, k in enumerate((a, b)):
        R = elevation(k) if k in 'SNEW' else section(k)
        V = (-2400, -3600 if k not in 'SNEW' else -2600, 32800, 16200)
        h = (V[3] - V[1]) / 100
        y0 = (397 - h) if i == 0 else 16
        place(fig, R, V, 12, y0, 100)
        nm = ENAMES[k] if k in ENAMES else SECTIONS[k]['title']
        ov.text(14, y0 + h + 0.5, nm + '   1:100', fontsize=7.5 if k in ENAMES else 6.6, fontweight='bold', va='bottom')
    scalebar(ov, 400, 14, 100, 5)
    if a in 'SNEW':
        para(ov, 382, 200, 130, None, ENOTES, fs=5.4)
    else:
        para(ov, 382, 200, 130, None, ['หมายเหตุรูปตัด', '· พื้นถึงพื้น 3.20 ม. = พื้น 0.20 + ฝ้า/งานระบบ 0.20 + โปร่ง 2.80 ม. (ชั้น 1-3)',
                                       '· ชั้น 4 ใต้หลังคาลาด: โปร่ง 2.60 ม. ที่ผนังชายคา ถึง 4.60 ม. ที่สัน (แปไม้เปิดโชว์)',
                                       '· รูปตัด A-A ตัดตามยาวผ่านโถงไม้ (ช่องโล่ง + สะพานไม้ + คอร์ตแสงหัวท้าย) · รูปตัด B-B ตัดขวางเห็นหลังคาจั่วไม่สมมาตร เสาไม้ + ค้ำเอียง และสระ',
                                       '· เสาเข็ม/ฐานรากเขียนเป็นสัญลักษณ์ — ขนาดจริงตามวิศวกรโครงสร้าง'], fs=5.4)
    pages.append(fig)

def A11():
    fig, ov = sheet('A-11', 'ตารางประตู-หน้าต่าง\n+ ตรวจช่องเปิด + เทียบโปรแกรม', 'ไม่มีมาตราส่วน')
    ops = [o for fl in (1, 2, 3, 4) for o in M[fl]['ops'] if o.tag]
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
    oc = [r for r in RES if r[0] == 'ฉ.39 ข้อ 6']
    rows = [(i[:34], v[:46], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in oc]
    yb = table(ov, 272, 402, [('ห้อง', 58, 'left'), ('ช่องเปิด/พื้นที่ห้อง', 64, 'left'), ('ผล', 10, 'center')], rows, fs=4.5, rh=4.0, title='ฉ.39 ข้อ 6 ช่องเปิด >= 10% ของพื้นที่ห้อง')
    cv = [r for r in RES if r[0] == 'ระบายอากาศ (เกณฑ์ภายใน)']
    dp = {r[1]: r[2] for r in RES if r[0] == 'ความลึกห้อง'}
    rows = [(i[:34], v[:22], dp.get(i, '')[:30], 'ผ่าน' if ok else 'ไม่ผ่าน') for g, i, v, c, ok in cv]
    yb = table(ov, 272, yb - 7, [('ห้องใช้งานประจำ', 58, 'left'), ('ช่องเปิด', 22, 'left'), ('ลึกจากผนังนอก', 42, 'left'), ('ผล', 10, 'center')], rows, fs=4.5, rh=4.0,
               title='ระบายอากาศ >= 2 แนวผนัง (เกณฑ์ภายใน สนับสนุน R-T06) / ลึก <= 4.20 ม.')
    geo = [r for r in RES if r[0] == 'เรขาคณิต']
    ng = sum(1 for r in geo if r[4])
    ov.text(272, yb - 2, 'ตรวจเรขาคณิตช่องเปิด (ลอย/ทับราวกันตก) %d รายการ: ผ่าน %d' % (len(geo), ng), fontsize=4.8, va='top')
    rows = []
    for nm, pf, pa, rooms in PROGRAM:
        if rooms == ['__PAVILION__']: a = PAV; f = 'สวน'
        else:
            rs = [r for r in all_rooms() if r.name in rooms]; a = sum((CORE_AREA if r.kind == 'core' else r.a) for r in rs); f = 'F%d' % rs[0].fl
        rows.append((nm[:34], 'F%d' % pf, '%.2f' % pa, f, '%.2f' % a, '%+.2f' % (a - pa)))
    tp = sum(p[2] for p in PROGRAM); td = sum(float(r[4]) for r in rows)
    rows.append(('รวม NUA', '', '%.2f' % tp, '', '%.2f' % td, '%+.2f' % (td - tp)))
    colors = [('#fde2e2' if (r[1] != r[3] and r[3] != 'สวน' and r[0] != 'รวม NUA') else None) for r in rows]
    yb = table(ov, 410, 402, [('รายการโปรแกรม', 44, 'left'), ('ชั้น', 7, 'center'), ('โปรแกรม', 13, 'right'), ('ชั้นแบบ', 9, 'center'), ('แบบ', 12, 'right'), ('ต่าง', 12, 'right')],
               rows, fs=4.9, rh=5.6, title='เทียบโปรแกรม ARCHISPACE (ตร.ม.)', colors=colors)
    para(ov, 410, yb - 2, 97, None, ['แถบชมพู = ชั้นในแบบต่างจากโปรแกรม (Pantry ชั้น 3 -> 2 ดู A-01 ข้อ 3) · ศาลาริมสระ = ลานใต้ชายคาชั้น 1',
                                     'ห้องจัดตามกริดเสาแท่งกว้าง 13.00 ม. (5.00 | 3.00 | 5.00) — ห้องที่เล็กกว่าโปรแกรมเกิน 10% ดูแถว "ต่าง" ติดลบ'], fs=4.7)
    pages.append(fig)

def A12():
    fig, ov = sheet('A-12', 'WELL for Residential\n+ วัสดุ + สิ่งที่ต้องทำต่อ', 'ไม่มีมาตราส่วน')
    wl = [r for r in RES if r[0].startswith('WELL')]
    gv = lambda k: [r[2] for r in wl if r[0] == k][0]
    feat = [
        ('R-A01 ระบบระบายอากาศ', 'พัดลมดูดเฉพาะจุดครัว/ห้องน้ำ/ห้องไม่มีหน้าต่าง %d ห้อง + ERV ห้องนอน' % len(INFO['fans']), 'ระบุในแบบงานระบบ', 'ต้องวัด'),
        ('R-A05 ลดการเผาไหม้', 'ครัวโชว์ชั้น 2 เตาไฟฟ้าเหนี่ยวนำ; ครัวไทย/เตาอบฟืนอยู่ชั้น 1 แยก มีฮูด เตาอบอยู่นอกอาคาร', 'ในแบบ', 'เอกสาร'),
        ('R-A09 จุดชาร์จ EV', '1 จุดในโรงจอดรถ (ท่อเผื่อ 4 ช่อง)', 'ในแบบ', 'ภาพถ่าย'),
        ('R-W03 น้ำที่ไม่ใช่น้ำดื่ม', 'ถังน้ำฝนใต้ดิน ~12 ลบ.ม. จากหลังคาจั่ว สำหรับรดน้ำ/ชักโครก', 'ในแบบ', 'แบบสุขาภิบาล'),
        ('R-L01 แสงธรรมชาติ', gv('WELL R-L01')[:44] + ' (ไม่นับกระจกสู่โถง)', 'คำนวณแล้ว', 'ต้องตรวจแสงจ้า'),
        ('R-L02 ควบคุมแสง', 'วงจรแยกทุกห้อง + ม่านทึบห้องนอน/เธียเตอร์ · ชายคาใต้ 3.00 ม. ลดแสงจ้า', 'ระบุ', 'แบบไฟฟ้า'),
        ('R-T06 หน้าต่างเปิดได้', gv('WELL R-T06'), 'คำนวณแล้ว', 'มุ้งลวด/ตัวล็อก'),
        ('R-T07 ความร้อนภายนอก', 'ชายคาใต้ 3.00 ม. + ระเบียงไม้บังแดด + หลังคาสีอ่อน + PV 23% ของหลังคา + ต้นไม้ร่ม', 'ในแบบ', 'ค่า SR วัสดุ'),
        ('R-V04 พื้นที่กิจกรรมกลางแจ้ง', 'สระ 14.00 x 3.00 ม. + piazza/ศาลา + ระเบียงไม้ทุกชั้น + ลอจเจีย + BBQ', 'ในแบบ', '-'),
        ('R-V07 ออกแบบบันได', 'บันไดหลักไม้เปิดโล่งสู่โถงไม้/แกลเลอรี ผนังกระจกทิศเหนือ อยู่หน้าลิฟต์ทุกชั้น', 'ในแบบ', 'ภาพถ่าย'),
        ('R-M01 ธรรมชาติและสถานที่', 'โครงไม้ glulam เปิดโชว์ภายใน-ภายนอก + มองสวนสระทุกชั้น + เตาอบฟืน (Forno)', 'ในแบบ', '-'),
        ('R-M04 พื้นที่จัดเก็บ', 'Walk-in 2 ชั้น (Master) + ตู้ทุกห้องนอน + Pantry + ห้อง AV/เก็บของ', 'ในแบบ', '-'),
        ('R-N01 การปรุงอาหาร', 'ครัว 2 ส่วน (โชว์/ไทย) + Pantry ห้องเย็นติดครัวโชว์ + โต๊ะยาวในโถงกลาง', 'ในแบบ', '-'),
        ('R-S01 แนวกั้นเสียง', 'โถงโปร่ง 4 ชั้นส่งเสียงข้ามชั้น -> ฝ้าไม้ซับเสียง + ประตูห้องนอนกันเสียง', 'ต้องระบุ STC', 'ทดสอบ'),
        ('R-C01 ออกแบบเพื่อทุกคน', 'ลิฟต์บ้านทุกชั้น + ห้องแขกชั้น 1; ทางลาด 1:12 ยังต้องเพิ่ม', 'บางส่วน', 'ดู A-01 ข้อ 11'),
        ('R-C06 ภัยพิบัติ', 'ยกพื้น +0.45 + บันไดหนีไฟ + เครื่องปั่นไฟ + ตรวจจับควันในโถงโปร่ง', 'ในแบบ', 'ระดับน้ำท่วมจริง?'),
        ('R-X02 วัสดุ', 'ไม้รับรอง FSC/PEFC กาวไร้ฟอร์มาลดีไฮด์ สี/เคลือบ VOC ต่ำ', 'สเปก', 'ใบสั่งซื้อ'),
    ]
    yb = table(ov, 12, 400, [('Feature (WELL for Residential)', 48, 'left'), ('การตอบสนองในแบบ', 118, 'left'), ('สถานะ', 25, 'left'), ('หลักฐานที่ต้องมี', 26, 'left')], feat, fs=7.0, rh=9.4,
               title='กลยุทธ์ WELL for Residential (รหัสตาม Guidebook ก.พ. 2026)')
    yb = para(ov, 12, yb - 4, 215, None, ['สถานะ = เจตนาการออกแบบ ยังไม่ใช่คะแนนรับรอง: WELL Residence ต้องลงทะเบียน IWBI ส่งเอกสาร และตรวจวัดจริงหลังก่อสร้าง',
                                         'ห้องที่ใช้พัดลมระบาย: ' + ', '.join(INFO['fans'])], fs=5.8)
    mats = [('โครงสร้างหลัก', 'ค.ส.ล. เสา 0.40x0.40 กริด 6 x 4 แนว · พื้นคานแบน 0.20 · ผนังรอบบันได/ลิฟต์ ค.ส.ล. · เสาเข็มเจาะ (รอผลเจาะดิน)'),
            ('โครงไม้ภายนอก', 'glulam เสา 240x480 @2.875 + ค้ำเอียง + คานขอบระเบียง · ตัวยึดสเตนเลส · ฐานเหล็กสูง 0.30 ม. · ไม่ใช่โครงสร้างหลัก'),
            ('หลังคา', 'แปไม้ glulam 160x400 ทุกเฟรม + standing seam สีอ่อน + PIR 75 + ฝ้าไม้ · ช่องแสงสันหลังคา laminated Low-E'),
            ('ผนังภายนอก', 'ชั้น 1 ปูนฉาบขาว · ชั้น 2-4 บล็อกมวลเบา 200 + ไม้กรุแนวตั้งบนโครงระบาย · ผนังภายใน 120 / ห้องน้ำ 150'),
            ('ระเบียง / สะพาน', 'พื้น ค.ส.ล. ยื่น 1.50 ม. ปูไม้ทนแดดฝน · สะพานข้ามโถงโครงเหล็ก+พื้นไม้ · ราวกระจก 1.10 ม.'),
            ('กระจก', 'Low-E laminated · SHGC <= 0.25 ทิศตะวันออก/ตะวันตก · กระจกสู่โถงเป็นกระจกนิรภัย'),
            ('พื้น', 'หินขัด/คอนกรีตขัดมัน (ชั้น 1 โถง/ศาลา) · ไม้เอ็นจิเนียร์ (ชั้น 2-4) · กระเบื้องกันลื่น R11'),
            ('ภายนอก', 'สระน้ำเกลือ 14.00 x 3.00 ลึก 1.40 ม. · ลาน piazza หินแกรนิต · เตาอบฟืน · บันไดหนีไฟเหล็กกัลวาไนซ์')]
    yb2 = table(ov, 236, 400, [('หมวด', 28, 'left'), ('ข้อกำหนด (ระดับแนวคิด)', 246, 'left')], mats, fs=6.4, rh=9.0, title='วัสดุหลัก')
    nxt = ['1. วิศวกรโครงสร้าง: โครง ค.ส.ล. + ชายคายื่น 3.00 ม. (แรงลมยก) + จุดต่อไม้-คอนกรีต + อัตราทนไฟโครงหลังคาไม้ + เสาเข็ม',
           '2. วิศวกรงานระบบ: VRF + ERV, ระบายควันโถงโปร่ง 4 ชั้น, พัดลมระบาย, น้ำฝน, ปั่นไฟ, โซลาร์ %.2f kWp' % C['kwp'],
           '3. ยืนยันกับสำนักงานเขต: ข้อ 27 บันไดหนีไฟบ้านเดี่ยว 4 ชั้น, การวัดความสูงหลังคาจั่ว, ความกว้างถนน, ผังเมืองรวม',
           '4. จำลอง CFD/ความร้อน: stack effect ในโถงไม้ (ยังเป็นสมมติฐาน); จำลองแสง/แสงจ้าห้องหลัก',
           '5. แบบขยาย: จุดต่อเสาไม้/ค้ำ, รางน้ำ, ช่องแสงสันหลังคา, สะพานไม้, หน้าจั่วระแนง, บันไดส่วนตัว, ทางลาด 1:12, เตาอบฟืน',
           '6. เลือกลิฟต์บ้านรุ่น overhead <= 2.60 ม. และหลุมลิฟต์ · แผนบำรุงรักษาไม้ภายนอก',
           '7. ลงทะเบียน WELL Residence · ประมาณราคาละเอียด (BOQ) หลังได้แบบโครงสร้าง-งานระบบ']
    yb2 = para(ov, 236, yb2 - 5, 274, 'สิ่งที่ต้องทำต่อ', nxt, fs=6.4)
    summ = ['ผลตรวจทั้งหมด %d รายการ: ผ่าน %d / ไม่ผ่าน %d (รายการ "ยกเว้น" มีเหตุผลกำกับ ดู A-11)' % (len(RES), sum(1 for r in RES if r[4]), sum(1 for r in RES if not r[4])),
            'แบบระดับ design development ต้องให้สถาปนิกและวิศวกรผู้ได้รับใบอนุญาตตรวจสอบและลงนามก่อนยื่นขออนุญาต']
    para(ov, 236, yb2 - 3, 274, 'สรุปการตรวจ', summ, fs=6.6, tcol='#b22222')
    image(fig, ov, 'CAM_4_Aerial_NW.png', 12, 16, 245, 150, 'มุมมองทิศตะวันตกเฉียงเหนือ — หน้าจั่วระแนงไม้ ลาดหลังคาทิศเหนือ เสาไม้หน้าโรงรถ', cap_above=True)
    image(fig, ov, 'CAM_2_Garden_South.png', 265, 16, 245, 150, 'จากสวนทิศใต้ — เฟรมไม้ glulam ค้ำเอียงรับชายคา ระเบียงไม้ ผนังกระจก', cap_above=True)
    pages.append(fig)

# ============================================================== DXF
def build_dxf(path):
    D = DXF()
    def title(x, y, t):
        R = Rec(); R.text((x, y), t, 600, 'A-TITLE', ha='left', bold=True); D.add(R)
    for i, fl in enumerate((1, 2, 3, 4)):
        R = plan(fl); grid(R, PLAN_VIEW); section_marks(R); north_arrow(R, (PLAN_VIEW[2] - 1500, PLAN_VIEW[3] - 2200), 800)
        D.add(R, dx=i * 36000)
        title(i * 36000 + PLAN_VIEW[0], PLAN_VIEW[1] - 1800, 'ผังพื้นชั้น %d  1:100' % fl)
    R = roof_plan(); grid(R, PLAN_VIEW); D.add(R, dx=4 * 36000)
    title(4 * 36000 + PLAN_VIEW[0], PLAN_VIEW[1] - 1800, 'แปลนหลังคา 1:100')
    R = site_plan(); D.add(R, dy=45000)
    title(-3000, 45000 - 5200, 'ผังบริเวณ (เขียนขนาดจริง)')
    for i, k in enumerate(('S', 'N', 'E', 'W')):
        R = elevation(k); D.add(R, dx=i * 38000, dy=-26000)
        title(i * 38000, -26000 - 4000, ENAMES[k] + ' 1:100')
    for i, k in enumerate(('A', 'B')):
        R = section(k); D.add(R, dx=i * 38000, dy=-50000)
        title(i * 38000, -50000 - 5000, 'รูปตัด %s-%s 1:100' % (k, k))
    D.save(path)

if __name__ == '__main__':
    A01(); A02()
    plan_sheet('A-03', 1); plan_sheet('A-04', 2); plan_sheet('A-05', 3); plan_sheet('A-06', 4)
    roof_sheet()
    elev_sheet('A-08', 'S', 'N', 'รูปด้านทิศใต้\n+ รูปด้านทิศเหนือ')
    elev_sheet('A-09', 'E', 'W', 'รูปด้านทิศตะวันออก\n+ รูปด้านทิศตะวันตก')
    elev_sheet('A-10', 'A', 'B', 'รูปตัด A-A\n+ รูปตัด B-B')
    A11(); A12()
    pdf = os.path.join(OUT, 'WELL-FORNO-30x30-drawings.pdf')
    with PdfPages(pdf) as pp:
        for f in pages:
            pp.savefig(f)
    if '--png' in sys.argv:
        for i, f in enumerate(pages):
            f.savefig('/tmp/well/fo6/sheet_%02d.png' % (i + 1), dpi=60)
    for f in pages: plt.close(f)
    print('pdf', pdf, len(pages))
    if '--dxf' in sys.argv:
        build_dxf(os.path.join(OUT, 'WELL-FORNO-30x30-CAD.dxf'))
        print('dxf ok')
