# -*- coding: utf-8 -*-
"""A2 sheet set (PDF) + DXF assembly for WELL-RIVERA 30x30 (4 floors, concept from Rivera Paradise / AtelierM)."""
import os, math, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from PIL import Image
from cad7 import draw_mpl, scaled_axes, DXF, Rec
from frame7 import *
from proj7 import project, ground_line, levels, LV
from plan7 import FLOORS, PROGRAM, PROGRAM_NUA, PROGRAM_GFA, all_rooms, CORE_AREA
from walls7 import model, side_of
from draw7 import plan, grid, PLAN_VIEW, north_arrow, section_marks
from proj7 import elevation, section, SECTIONS
from site7 import site_plan, roof_plan
from verify7 import run, areas, cost

A2 = (594, 420)
OUT = '/mnt/user-data/outputs/rivera7'
REND = '/mnt/user-data/uploads/WELL/WELL-RIVERA-30x30/renders/RV7_'
PROJ = 'WELL-RIVERA 30x30 · Executive Luxury Villa · บ้านเดี่ยว 4 ชั้น รอบคอร์ตกลาง ปีกลดชั้นแบบเกลียว + บันไดเกลียวคู่ (ใน/นอก) + หลังคาสวนทุกชั้น (แนวคิดจาก Rivera Paradise / AtelierM)'
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
    ov.text(x, 386, 'WELL-RIVERA 30x30', fontsize=8.5, fontweight='bold', va='top')
    ov.text(x, 381, 'Executive Luxury Villa\nบ้านเดี่ยว 4 ชั้น ผ่านเกณฑ์\nWELL for Residential (เจตนา)', fontsize=6.5, va='top', linespacing=1.35)
    ov.text(x, 365, 'ที่ดิน 30.00 x 30.00 ม. = 225 ตร.ว.\nถนนสาธารณะทิศเหนือ (สมมติ 8.00 ม.)', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [355, 355], lw=0.6, c='#111')
    ov.text(x, 352, 'แนวคิด', fontsize=6, color='#777', va='top')
    ov.text(x, 347, 'ตีความจาก Rivera Paradise (AtelierM):\nคอร์ตกลาง + บันไดเกลียวคู่ (ใน/นอก)\n+ ปีกลดชั้นแบบเกลียว หลังคาสวนทุกชั้น\n+ ผนังอิฐโชว์ + เพดานโค้งอิฐ', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [326, 326], lw=0.6, c='#111')
    ov.text(x, 323, 'ระดับ', fontsize=6, color='#777', va='top')
    ov.text(x, 318, '±0.00 ถนน · F1 +0.45 · F2 +3.65\nF3 +6.85 · F4 +10.05\nดาดฟ้า +13.25 · ราว +14.35\nโค้งอิฐ สปริง +5.45 ยอด +6.65', fontsize=6, va='top', linespacing=1.35)
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
    fig, ov = sheet('A-01', 'แนวคิด Rivera Paradise\n-> บ้านเกลียวคู่รอบคอร์ต + ข้อจำกัด', 'ไม่มีมาตราส่วน')
    imgs = [('CAM_2_Aerial_NW.png', 'มุมมองทิศตะวันตกเฉียงเหนือ — ปีกลดชั้นแบบเกลียว: W 1 ชั้น -> N 2 ชั้น -> E 3 ชั้น -> S 4 ชั้น ทุกหลังคาเป็นสวน + บันไดนอก'),
            ('CAM_1_Aerial_SE.png', 'มุมมองทิศตะวันออกเฉียงใต้ — ปีกใต้ 4 ชั้นหันสระ รางต้นไม้ห้อยทุกขอบพื้น ผนังอิฐโชว์ + สวนแนวตั้ง'),
            ('CAM_3_Courtyard.png', 'ในคอร์ตกลาง — มองขึ้นผ่านขอบพื้นที่มีต้นไม้ห้อย ลาน BBQ ชั้น 4 และบันไดนอก'),
            ('CAM_6_Street_North.png', 'จากถนนทิศเหนือ — ปีกเหนือ 2 ชั้น (โรงรถ + Junior Suite) ผนังอิฐ หลังคาสวน และปีกใต้สูงด้านหลัง')]
    pos = [(12, 283, 160, 100), (176, 283, 160, 100), (12, 172, 160, 100), (176, 172, 160, 100)]
    for (f, cap), (x, y, w, h) in zip(imgs, pos):
        image(fig, ov, f, x, y, w, h, cap)
    ov.text(12, 400, 'ภาพจากโมเดล Blender (WELL-RIVERA-30x30-model.blend) — โมเดลมวลอาคารระดับ DD สร้างจากข้อมูลชุดเดียวกับแบบ CAD', fontsize=6, color='#555', va='top')
    concept_diagrams(fig, ov)
    X0, W0 = 342, 170
    facts = [('ผู้ออกแบบ', 'AtelierM (สถาปนิกหลัก Matias Mosquera) · ภูมิสถาปัตย์ Valeria Lennon'),
             ('ที่ตั้ง / ปี / ขนาด', 'ย่าน Coghlan บัวโนสไอเรส อาร์เจนตินา · 2026 · 200 ตร.ม. (ArchDaily)'),
             ('ข้อจำกัดที่ดิน', 'ที่ดินแคบระหว่างอาคารข้างเคียง ในเขตอนุรักษ์ (APH) ต้องคงอาคารเดิม 30%'),
             ('สิ่งที่เก็บไว้', 'ผนังอิฐโชว์ร่วมกับเพื่อนบ้าน (party walls) และเพดานโค้งอิฐสูง 2 ชั้นของเดิม'),
             ('คอร์ต', '"a large central courtyard that articulates the entire house" — แสง ลม ความลึก + บานกระจกเลื่อน + เงาสะท้อนน้ำ'),
             ('การสัญจร', 'ได้แรงบันดาลใจจากบันไดเกลียวคู่ Château de Chambord: ทางในตามชั้น + ทางนอกไต่ขึ้นตามหลังคาสวนขั้นบันได (อิสระแต่ซ้อนกัน)'),
             ('สีเขียว', 'หลังคาเขียว + สวนแนวตั้ง เปลี่ยนผนังข้างเคียงเป็นสวน สร้าง microclimate'),
             ('จากภาพ / แบบ', 'คอร์ตปูอิฐ กระบะต้นไม้ ต้นไม้ห้อยจากขอบพื้นคอนกรีตโค้งมน ผนังไม้ เพดานอิฐ · ผังชั้นล่าง / ชั้นลอย / ชั้นบน')]
    yb = table(ov, X0, 398, [('หัวข้อ', 26, 'left'), ('ข้อเท็จจริงจาก Architizer / ArchDaily (ข้อความ + ภาพ)', 144, 'left')], facts, fs=5.6,
               title='Rivera Paradise — ข้อเท็จจริงที่ตรวจได้')
    interp = [('คอร์ตกลาง', 'คอร์ต 10.00 x 7.00 ม. เปิดฟ้า ปูอิฐ สระสะท้อนเงา ต้นไม้ · ทุกปีกหันกระจกเต็มบานเข้าคอร์ต'),
              ('เกลียวคู่ Chambord', 'เกลียวใน = บันไดหลัก + ลิฟต์ในปีกใต้ · เกลียวนอก = บันไดนอก H1-H4 ไต่สวนหลังคารอบคอร์ต'),
              ('หลังคาสวนขั้นบันได', 'ปีกลดชั้นแบบเกลียว: W 1 ชั้น (สวน +3.65) -> N 2 ชั้น (+6.85) -> E 3 ชั้น (ลาน BBQ +10.05) -> S 4 ชั้น (ดาดฟ้า +13.25)'),
              ('อิฐเดิม 30%', 'ไม่มีอาคารเดิม: ผนังอิฐโชว์ด้านข้าง E/W + เพดานโค้งอิฐเหนือโถงสูง 2 ชั้น (ของใหม่ เป็นการอ้างถึง)'),
              ('ต้นไม้ห้อย / แนวตั้ง', 'รางต้นไม้ขอบพื้นทุกชั้น (ด้านใต้ + รอบคอร์ต) + สวนแนวตั้งบนผนังอิฐ'),
              ('ไม่นำมาใช้', 'ขอบพื้นโค้งมน (แบบนี้มุมฉาก — ต้องพัฒนาในแบบขยาย) · ชั้นลอยแบบทาวน์เฮาส์แคบ')]
    yb = table(ov, X0, yb - 7, [('องค์ประกอบ', 26, 'left'), ('การตีความของเรา (ไม่ใช่คำอธิบายของสถาปนิก)', 144, 'left')], interp, fs=5.6,
               title='การตีความ -> แบบบ้านหลังนี้')
    lim = [
        '1. ต้นแบบเป็นบ้าน 200 ตร.ม. บนที่ดินแคบในเขตอนุรักษ์ — บ้านนี้ใหญ่กว่าราว 5 เท่าและไม่มีอาคารเดิม อิฐ/โค้งอิฐเป็นการตีความของเรา',
        '2. โปรแกรมขัดกัน: Master ชั้น 3 แต่ Closet + Terrace ชั้น 4 -> Master duplex มีบันไดส่วนตัว; Pantry ชั้น 3 ย้ายไปชั้น 2 ติดครัว',
        '3. GFA %.2f vs โปรแกรม %.2f (%+.1f%%): ส่วนเกิน = ห้องฟิตเนส 36 + ห้องเครื่องสระ 18 (ชั้น 1) + ลอจเจียชั้น 3 42 ตร.ม. (รองรับลาน BBQ) — ผลจากรูปวงแหวน' %
        (C['gfa'], PROGRAM_GFA, C['gfa'] / PROGRAM_GFA * 100 - 100),
        '4. เล็กกว่าโปรแกรมเกิน 10%: ครัวโชว์ -29%, ระเบียง Master -27%, ซักรีด -25%, Pantry -17%, Walk-in -16%, โรงรถ -12%; ใหญ่กว่า: โถงต้อนรับ +50%, MEP +50%, แม่บ้าน +43%',
        '5. ทางหนีไฟ = บันไดนอกเกลียว H4->H1 ผ่านสวนหลังคา ลงคอร์ต -> ศาลา -> สวน: ต้องยืนยันข้อ 27 กับเขตว่ายอมรับเส้นทางผ่านดาดฟ้า/คอร์ตได้',
        '6. บันไดนอกเข้าถึงทุกชั้นจากสวน: ประตูสู่สวนหลังคาต้องล็อกจากภายในแต่เปิดออกได้ทันที (panic) + ไฟส่องสว่าง/กล้อง',
        '7. ชั้น 3: Walk-in และ Spa อยู่อีกฟากของแกนบันได ต้องเดินผ่านแกลเลอรี (ชั้น 3 ใช้เฉพาะ Master)',
        '8. ห้องเปิดด้านเดียว/ลึกเกิน 4.20 ม. (ยกเว้นพร้อมเหตุผล) 10 ห้อง; ห้องที่ช่องเปิดไม่ถึง 10%% ใช้พัดลมระบาย %d ห้อง (A-12)' % len(INFO['fans']),
        '9. หลังคาสวน 339 ตร.ม. ดินอิ่มน้ำ ~250-300 กก./ตร.ม. + กันซึม/กันรากทุกชั้น; คอร์ตปิดล้อม 4 ด้าน ต้องมีท่อระบายและบ่อพักของตัวเอง',
        '10. ผนังอิฐทิศตะวันออก/ตะวันตกรับแดดบ่าย ต้องมีช่องอากาศ + ฉนวน; รางต้นไม้ห้อยต้องมีระบบน้ำหยดและทางเข้าดูแล',
        '11. ความกว้างถนนสมมติ 8.00 ม.; ทางลาดโรงรถ +0.15 -> +0.45 ยังไม่เขียน; ไม่ทราบผังเมืองรวม/ข้อบัญญัติท้องถิ่น',
    ]
    yb = para(ov, X0, yb - 4, W0, 'รายงานข้อจำกัด (ตรงไปตรงมา)', lim, fs=5.8, gap=0.8, tcol='#b22222')
    para(ov, X0, yb - 3, W0, 'แหล่งข้อมูลอ้างอิง', [
        '· architizer.com/projects/rivera-paradise (ลิงก์ที่ผู้ใช้ให้มา) · archdaily.com/1054061 (ข้อมูลโครงการ + ภาพ/แบบ)',
        'ไม่ได้รับแบบจริงของโครงการ — ทุกมิติในชุดนี้ออกแบบใหม่'], fs=5.7)
    pages.append(fig)

def concept_diagrams(fig, ov):
    import math as _m
    R = Rec()
    hc = {1: '#e9d8c6', 2: '#d9b48f', 3: '#c08a5a', 4: '#8f5a33'}
    R.rect(0, 0, LOT_W, LOT_D, 'C-PROP', lw=0.4)
    R.frect(POOL[0], POOL[1], POOL[2], POOL[3], 'A-AREA', color='#7fb7d0', z=1)
    hts = {'W': 1, 'N': 2, 'E': 3, 'S': 4}
    for k, (x0, y0, x1, y1) in WING.items():
        R.frect(x0, y0, x1, y1, 'A-AREA', color=hc[hts[k]], z=1); R.rect(x0, y0, x1, y1, 'A-WALL-INT', lw=0.2)
        R.text(((x0 + x1) / 2, (y0 + y1) / 2 - 900), '%s : %d ชั้น\nสวน %+.2f' % (k, hts[k], ROOF_GARDEN[k] / 1000), 420, 'A-TEXT', bold=True)
    cx0, cy0, cx1, cy1 = COURT
    R.frect(cx0, cy0, cx1, cy1, 'A-AREA', color='#f3ece4', z=1)
    R.text(((cx0 + cx1) / 2, (cy0 + cy1) / 2), 'คอร์ต', 480, 'A-TEXT', bold=True)
    for nm, (x0, y0, x1, y1), z0, z1, d in HELIX:
        R.frect(x0, y0, x1, y1, 'A-AREA', color='#b22222', z=2)
        R.text((x0 - 700 if x0 > 20000 else x1 + 700, (y0 + y1) / 2), nm, 380, 'A-TEXT', bold=True)
    R.text((13000, 28500), 'ถนน (ทิศเหนือ)', 520, 'A-TEXT', bold=True)
    R.text((13000, 2200), 'สระ', 480, 'A-TEXT', bold=True)
    north_arrow(R, (28200, 28000), 700)
    place(fig, R, (-1000, -800, 31000, 31000), 14, 22, 250)
    ov.text(14, 154, 'ไดอะแกรมเกลียว (1:250): ปีก W-N-E-S สูง 1-2-3-4 ชั้น; บันไดนอก H1-H4 (แดง) ไต่สวนหลังคาตามเข็มนาฬิกา', fontsize=6.3, fontweight='bold', va='top')
    from model7 import build
    BX, _ = build()
    S = project('S', BX, cut=('y', 15000), cutdepth=15000)
    ground_line(S, 'S', -1500, LOT_W + 1500)
    def arrow(a, b, lw=0.9):
        S.line(a, b, 'A-ANNO', lw=lw)
        ang = _m.atan2(b[1] - a[1], b[0] - a[0])
        S.pline([(b[0] - 700 * _m.cos(ang - .4), b[1] - 700 * _m.sin(ang - .4)), b, (b[0] - 700 * _m.cos(ang + .4), b[1] - 700 * _m.sin(ang + .4))], 'A-ANNO', lw=lw)
    arrow((11500, 1500), (15000, 1500)); arrow((15000, 1500), (15000, 12500)); arrow((15000, 12500), (15000, 15500))
    arrow((10600, F1 + 300), (10600, F2 + 300), 0.6); arrow((4800, F2 + 300), (4800, F3 + 300), 0.6)
    S.text((15300, 8000), 'อากาศร้อนลอยออก\nทางคอร์ตเปิดฟ้า', 360, 'A-ANNO', ha='left')
    S.text((1200, F3 + 900), 'เกลียวนอก H1 -> H2', 340, 'A-ANNO', ha='left')
    place(fig, S, (-1800, -2800, 32500, 17600), 186, 30, 250)
    ov.text(186, 154, 'ไดอะแกรมรูปตัด A-A (y = 15.00, 1:250): คอร์ตเป็นปล่องลม + บันไดนอกไต่ขั้นสวนหลังคา', fontsize=6.3, fontweight='bold', va='top')
    ov.text(186, 26, 'ลูกศร = เจตนาการออกแบบ (ลมประจำกรุงเทพฯ ฤดูร้อน S/SW) — ยังไม่ได้พิสูจน์ด้วย CFD/การจำลองความร้อน', fontsize=5.4, color='#b22222', va='top')

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
    ov.text(266, yb - 1.5, '* ไม่นับช่องโล่งโถงต้อนรับและคอร์ต · ศาลาริมสระ / ลอจเจีย / ลาน BBQ / ระเบียง = กึ่งภายนอก · สวนหลังคาไม่นับ', fontsize=4.7, va='top', color='#555')
    rows = [('พื้นที่ดิน', '900.00 ตร.ม. (225 ตร.ว.)'), ('พื้นที่อาคารคลุมดิน (ไม่รวมคอร์ต)', '%.2f ตร.ม. (%.1f%%)' % (INFO['cover'], INFO['cover'] / 9)),
            ('ที่ว่าง', '%.1f%%  (เกณฑ์ >= 30%%)' % INFO['os1']), ('FAR (GFA ปิดล้อม / ที่ดิน)', '%.2f : 1' % (ENC / 900)),
            ('ความสูงอาคาร', 'พื้นดาดฟ้า 13.25 / ราวกันตก 14.35 ม. (< 15.00)'),
            ('ที่ดินขั้นต่ำตามโปรแกรม', '113 ตร.ว. — ที่ดินจริง 225 ตร.ว.')]
    yb = table(ov, 266, yb - 9, [('รายการ', 62, 'left'), ('ค่า', 116, 'left')], rows, fs=5.0, title='ที่ว่างและการใช้ที่ดิน')
    rows = [('(ก) อัตราแยกมาตรฐาน', 'ปิดล้อม %.2f x 22,000 + กึ่งภายนอก %.2f x 11,000 + จอดรถ %.2f x 8,000' % (C['enc'], C['semi'], C['park']), '%.2f' % (C['std'] / 1e6)),
            ('(ข) อัตราแยก luxury', 'ปิดล้อม x 30,000 + กึ่งภายนอก x 15,000 + จอดรถ x 12,000', '%.2f' % (C['lux'] / 1e6)),
            ('(ค) อัตราเดียว (วิธีเดียวกับโปรแกรม)', 'GFA %.2f x 30,000' % C['gfa'], '%.2f' % (C['single'] / 1e6)),
            ('งานนอกอาคาร', 'สระ %.1f ตร.ม. x 35,000 + PV %.2f kWp x 45,000 + ภูมิทัศน์/รั้ว 1.80 + ลิฟต์ 0.90 + บันไดนอก 1.40 + สวนหลังคา 1.19 ล.' % (C['pool'], C['kwp']), '%.2f' % (C['extra'] / 1e6)),
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
NOTES = {1: ['· ทางเข้าทิศเหนือ -> โถงต้อนรับสูง 2 ชั้นใต้เพดานโค้งอิฐ -> โถงทางเดินกระจกริมคอร์ต -> ศาลาริมสระ -> แกลเลอรี -> บันไดหลัก/ลิฟต์',
             '· คอร์ตกลาง 10.00 x 7.00 ม. เปิดฟ้า พื้นอิฐ สระสะท้อนเงา ต้นไม้ · บันไดนอก H1 เริ่มที่คอร์ตขึ้นสวนหลังคาปีกตะวันตก',
             '· ศาลาริมสระทะลุจากสระถึงคอร์ต (ทางลมใต้-เหนือ) · ห้องฟิตเนส/โยคะริมสระ (ไม่อยู่ในโปรแกรม — ส่วนเกินจากรูปวงแหวน)',
             '· ฝั่งบริการตะวันออก: แม่บ้าน 2 ห้อง ห้องน้ำ ห้องเครื่องสระ ต่อโรงรถ · ครัวไทย/ซักรีดเปิดสู่ลานบริการทิศตะวันตก',
             '· โรงจอดรถ 4 คัน @3.10 ม. ลึก 6.00 ม. + จุดชาร์จ EV (WELL R-A09); ทางลาด 1:12 ต้องเพิ่ม'],
         2: ['· ปีกใต้: ครัวโชว์ -> ห้องอาหาร 12 ที่นั่ง -> แกลเลอรี -> ห้องนั่งเล่น หันสระ บานเลื่อนทิศใต้ + กระจกเต็มบานสู่คอร์ต',
             '· ห้องอาหารเปิดสู่สวนหลังคาปีกตะวันตก (+3.65) = จุดเริ่มเกลียวนอก H2 · Pantry ย้ายจากชั้น 3 มาติดครัว',
             '· ปีกเหนือ: Junior Suite 2-3 ห้องไวน์ ห้องเก็บของ เข้าจากทางเดินกระจกริมคอร์ต · ช่องโล่งโถงต้อนรับใต้โค้งอิฐ',
             '· ปีกตะวันออก: ทางเดินริมคอร์ต + ห้องทำงาน & ห้องสมุด (มุมตะวันออกเฉียงใต้)'],
         3: ['· ชั้น Master: ห้องนอน (ตะวันตก) — แกนบันได — Walk-in + Spa (ตะวันออก) ต่อกันด้วยแกลเลอรีริมคอร์ต; บันไดส่วนตัวขึ้นชั้น 4',
             '· สวนหลังคาปีกเหนือ (+6.85) เหนือเพดานโค้งอิฐ: บันไดนอก H3 ขึ้นลาน BBQ',
             '· ลอจเจียตะวันออกใต้ลาน BBQ (ส่วนเกินโปรแกรม) เชื่อมแกลเลอรีกับสวนหลังคาเหนือ = ทางหนีไฟชั้น 3',
             '· ห้องที่หันคอร์ตใช้ม่าน/ฟิล์มเพื่อความเป็นส่วนตัวจากบันไดนอก'],
         4: ['· Master duplex: บันไดส่วนตัว -> Closet -> ระเบียง Master ในร่มทิศใต้ (อ่างแช่)',
             '· Upper Gallery -> ห้องนั่งเล่นครอบครัว / ห้องโฮมเธียเตอร์ / ลาน BBQ บนหลังคาปีกตะวันออก (+10.05, pergola)',
             '· บันไดนอก H4 จากลาน BBQ ขึ้นสวนดาดฟ้า +13.25 (แผงโซลาร์ %d แผง %.2f kWp)' % (round(C['kwp'] / 0.55), C['kwp']),
             '· ทางหนีไฟชั้น 4: แกลเลอรี -> ลาน BBQ -> H3 -> H2 -> H1 -> คอร์ต -> ศาลา -> สวน']}

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
    fig, ov = sheet('A-07', 'แปลนหลังคา\n(สวนหลังคาแบบเกลียว)', '1:100')
    R = roof_plan()
    grid(R, PLAN_VIEW)
    place(fig, R, PLAN_VIEW, 12, 60, 100)
    ov.text(14, 55, 'แปลนหลังคา  ROOF PLAN   1:100', fontsize=9, fontweight='bold', va='top')
    scalebar(ov, 150, 49, 100, 5)
    rows = [('สวนหลังคา W +3.65 (ปีกตะวันตก)', '42.00'), ('สวนหลังคา N +6.85 (ปีกเหนือ)', '132.00'), ('ลาน BBQ E +10.05 (พื้นไม้ บนหลังคาชั้น 3)', '42.00'),
            ('สวนดาดฟ้า S +13.25 (รวมแผงโซลาร์)', '165.00'), ('รวมหลังคาสวน', '339.00'), ('คอร์ตกลาง (เปิดฟ้า ไม่มีหลังคา)', '70.00')]
    yb = table(ov, 382, 400, [('หลังคา', 80, 'left'), ('ตร.ม.', 32, 'right')], rows, fs=5.4, title='พื้นที่หลังคา')
    rows = [('ฝนรายปีกรุงเทพฯ (ประมาณ)', '~1,500 มม./ปี'), ('น้ำฝนจากหลังคาสวน (C=0.4) + คอร์ต (C=0.9)', '%.0f ลบ.ม./ปี' % ((339 * 0.4 + 70 * 0.9) * 1.5)),
            ('ถังเก็บน้ำฝนใต้ดิน 2.40 x 3.00 ม.', '~12 ลบ.ม. (รดน้ำ/ชักโครก)'), ('แผงโซลาร์ %d x 550 Wp' % round(C['kwp'] / 0.55), '%.2f kWp ~ %s kWh/ปี*' % (C['kwp'], format(round(C['kwp'] * 1300, -2), ',.0f'))),
            ('บันไดนอก H1-H4', 'กว้าง 1.20 ม. 20 ลูกตั้ง x 160 / 290 มม.')]
    yb = table(ov, 382, yb - 8, [('รายการ', 62, 'left'), ('ค่า', 50, 'left')], rows, fs=5.0, title='น้ำฝน พลังงาน บันไดนอก')
    para(ov, 382, yb - 4, 130, 'ชั้นหลังคาสวน', [
        '· พืชคลุมดิน/ไม้พุ่ม + ดินปลูก 150-450 มม. + แผ่นใยกรอง + แผ่นระบายน้ำ 20 มม. + แผ่นกันราก + กันซึม 2 ชั้น + ค.ส.ล. ลาด 1:100',
        '· ขอบสวน: คอนกรีตสูง 0.45 + ราวกระจก laminated 1.10 ม. · กระบะไม้ปลูกต้นไม้ใหญ่',
        '· ลาน BBQ: พื้นไม้บนขาตั้ง + pergola ไม้ + เตา BBQ แก๊ส/ไฟฟ้า',
        '· ทุกสวนหลังคาใช้เป็นเส้นทางหนีไฟ — ห้ามวางสิ่งกีดขวางบนแนวบันไดนอก',
        '· RD = ท่อระบายน้ำฝน ลงรางรอบอาคาร -> ถังน้ำฝน; คอร์ตมีรางระบายรอบ + บ่อพัก',
        '* PV ~1,300 kWh/kWp/ปี ติดตั้งเอียง 10° บนดาดฟ้า — ต้องคำนวณจริงรวมเงาราว/ต้นไม้'], fs=5.0)
    pages.append(fig)

ENAMES = {'S': 'รูปด้านทิศใต้ (สวน/สระ — ปีกใต้ 4 ชั้น รางต้นไม้ห้อย)', 'N': 'รูปด้านทิศเหนือ (ถนน — ปีกเหนือ 2 ชั้น / ปีกใต้ด้านหลัง)',
          'E': 'รูปด้านทิศตะวันออก (ขั้นเกลียว + บันไดนอก H3/H4)', 'W': 'รูปด้านทิศตะวันตก (ขั้นเกลียว + บันไดนอก H2)'}
ENOTES = ['วัสดุผิว (ระดับแนวคิด)', '· ผนังข้าง E/W และด้านถนน: อิฐมอญโชว์แนว (ช่องอากาศ + ฉนวนด้านใน) + สวนแนวตั้ง',
          '· ด้านสระ: ไม้กรุแนวตั้ง + กระจกบานเลื่อน · ขอบพื้น/หน้าคอร์ต: คอนกรีตเปลือยสีขาว',
          '· รางต้นไม้คอนกรีตยื่น 0.45 ม. ทุกขอบพื้น + ไม้เลื้อยห้อย (ระบบน้ำหยด)',
          '· บันไดนอก: คอนกรีตหล่อ + ราวกระจก 1.00 ม. · ราวสวนหลังคา: กระจก 1.10 ม.',
          '· กระจก Low-E laminated กรอบอะลูมิเนียมสีดำ · ลาน BBQ: pergola ไม้']

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
        para(ov, 382, 200, 130, None, ['หมายเหตุรูปตัด', '· พื้นถึงพื้น 3.20 ม. = พื้น 0.20 + ฝ้า/งานระบบ 0.20 + โปร่ง 2.80 ม.',
                                       '· รูปตัด A-A ตัดผ่านคอร์ต: เห็นขั้นเกลียว ปีก W 1 ชั้น -> ลาน BBQ ชั้น 4 และบันไดนอก H1/H2/H4',
                                       '· รูปตัด B-B ตัดผ่านโถงต้อนรับ: เพดานโค้งอิฐช่วง 6.00 ม. (สปริง +5.45 ยอด +6.65) ใต้สวนหลังคา N',
                                       '· สวนหลังคา: ดินปลูก 150-450 มม. น้ำหนักอิ่มน้ำ ~250-300 กก./ตร.ม. · เสาเข็มเป็นสัญลักษณ์'], fs=5.4)
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
    para(ov, 410, yb - 2, 97, None, ['แถบชมพู = ชั้นในแบบต่างจากโปรแกรม (Pantry ชั้น 3 -> 2 ดู A-01 ข้อ 2) · ศาลาริมสระ = ศาลาทะลุคอร์ตชั้น 1',
                                     'ห้องจัดตามปีกวงแหวน (ลึก 6.00-7.50 ม.) — ห้องที่เล็กกว่าโปรแกรมเกิน 10% ดูแถว "ต่าง" ติดลบ · ฟิตเนส/ห้องเครื่องสระ/ลอจเจียชั้น 3 = ส่วนเกิน'], fs=4.7)
    pages.append(fig)

def A12():
    fig, ov = sheet('A-12', 'WELL for Residential\n+ วัสดุ + สิ่งที่ต้องทำต่อ', 'ไม่มีมาตราส่วน')
    wl = [r for r in RES if r[0].startswith('WELL')]
    gv = lambda k: [r[2] for r in wl if r[0] == k][0]
    feat = [
        ('R-A01 ระบบระบายอากาศ', 'พัดลมดูดเฉพาะจุดครัว/ห้องน้ำ/ห้องไม่มีหน้าต่าง %d ห้อง + ERV ห้องนอน' % len(INFO['fans']), 'ระบุในแบบงานระบบ', 'ต้องวัด'),
        ('R-A05 ลดการเผาไหม้', 'ครัวโชว์ชั้น 2 เตาไฟฟ้าเหนี่ยวนำ; ครัวไทยชั้น 1 แยก มีฮูด เปิดสู่ลานบริการ', 'ในแบบ', 'เอกสาร'),
        ('R-A09 จุดชาร์จ EV', '1 จุดในโรงจอดรถ (ท่อเผื่อ 4 ช่อง)', 'ในแบบ', 'ภาพถ่าย'),
        ('R-W03 น้ำที่ไม่ใช่น้ำดื่ม', 'ถังน้ำฝนใต้ดิน ~12 ลบ.ม. รดสวนหลังคา/ชักโครก + ระบบน้ำหยดรางต้นไม้', 'ในแบบ', 'แบบสุขาภิบาล'),
        ('R-L01 แสงธรรมชาติ', gv('WELL R-L01')[:44], 'คำนวณแล้ว', 'ต้องตรวจแสงจ้า'),
        ('R-L02 ควบคุมแสง', 'วงจรแยกทุกห้อง + ม่านทึบห้องนอน/เธียเตอร์ + ม่านโปร่งด้านคอร์ต', 'ระบุ', 'แบบไฟฟ้า'),
        ('R-T06 หน้าต่างเปิดได้', gv('WELL R-T06'), 'คำนวณแล้ว', 'มุ้งลวด/ตัวล็อก'),
        ('R-T07 ความร้อนภายนอก', 'หลังคาสวน 339 ตร.ม. (100% ของหลังคา) + สวนแนวตั้ง + รางต้นไม้ + คอร์ตต้นไม้', 'ในแบบ', 'ภาพถ่าย'),
        ('R-V04 พื้นที่กิจกรรมกลางแจ้ง', 'สวนหลังคา 4 ระดับ + คอร์ต + สระ 14.00 x 2.70 ม. + ลาน BBQ', 'ในแบบ', '-'),
        ('R-V07 ออกแบบบันได', 'บันไดหลักอยู่หน้าลิฟต์ทุกชั้น เปิดสู่แกลเลอรีริมคอร์ต + บันไดนอกเกลียวไต่สวน', 'ในแบบ', 'ภาพถ่าย'),
        ('R-M01 ธรรมชาติและสถานที่', 'คอร์ตต้นไม้ + หลังคาสวนทุกชั้น + อิฐ/ไม้/น้ำ ทุกห้องเห็นต้นไม้', 'ในแบบ', '-'),
        ('R-M04 พื้นที่จัดเก็บ', 'Walk-in 2 ชั้น (Master) + ตู้ทุกห้องนอน + Pantry + ห้องเก็บของทุกชั้น', 'ในแบบ', '-'),
        ('R-N01 การปรุงอาหาร', 'ครัว 2 ส่วน (โชว์/ไทย) + Pantry ห้องเย็นติดครัวโชว์ + กระบะผักสวนหลังคา', 'ในแบบ', '-'),
        ('R-S01 แนวกั้นเสียง', 'คอร์ตปิดล้อมสะท้อนเสียง -> ฝ้าดูดซับเสียงแกลเลอรี + กระจก 2 ชั้นห้องนอน', 'ต้องระบุ STC', 'ทดสอบ'),
        ('R-C01 ออกแบบเพื่อทุกคน', 'ลิฟต์บ้านทุกชั้น + ห้องแขกชั้น 1; ทางลาด 1:12 ยังต้องเพิ่ม', 'บางส่วน', 'ดู A-01 ข้อ 11'),
        ('R-C06 ภัยพิบัติ', 'ยกพื้น +0.45 + ทางหนีไฟเกลียวนอก + เครื่องปั่นไฟ', 'ในแบบ', 'ยืนยันข้อ 27'),
        ('R-X02 วัสดุ', 'อิฐมอญ คอนกรีต ไม้รับรอง FSC สี VOC ต่ำ', 'สเปก', 'ใบสั่งซื้อ'),
    ]
    yb = table(ov, 12, 400, [('Feature (WELL for Residential)', 48, 'left'), ('การตอบสนองในแบบ', 118, 'left'), ('สถานะ', 25, 'left'), ('หลักฐานที่ต้องมี', 26, 'left')], feat, fs=7.0, rh=9.4,
               title='กลยุทธ์ WELL for Residential (รหัสตาม Guidebook ก.พ. 2026)')
    yb = para(ov, 12, yb - 4, 215, None, ['สถานะ = เจตนาการออกแบบ ยังไม่ใช่คะแนนรับรอง: WELL Residence ต้องลงทะเบียน IWBI ส่งเอกสาร และตรวจวัดจริงหลังก่อสร้าง',
                                         'ห้องที่ใช้พัดลมระบาย: ' + ', '.join(INFO['fans'])], fs=5.8)
    mats = [('โครงสร้าง', 'ค.ส.ล. เสา 0.40x0.40 กริด 6 x 4 แนว · พื้นคานแบน 0.20 · พื้นสวนหลังคารับน้ำหนักดินอิ่มน้ำ · เสาเข็มเจาะ (รอผลเจาะดิน)'),
            ('ผนัง', 'ผนังข้าง/ด้านถนน อิฐมอญโชว์ 2 ชั้น + ช่องอากาศ · ด้านสระไม้กรุ · หน้าคอร์ตคอนกรีตเปลือย + กระจกบานเลื่อน · ภายใน 120 / ห้องน้ำ 150'),
            ('เพดานโค้งอิฐ', 'โค้งอิฐ (barrel vault) ช่วง 6.00 ม. สูงโค้ง 1.20 ม. บนคาน ค.ส.ล. รับแรงถีบ — ต้องให้วิศวกรออกแบบ'),
            ('สวน / ราง', 'สวนหลังคา 4 ระดับ + รางต้นไม้คอนกรีตยื่น 0.45 ม. + สวนแนวตั้งบนโครงสเตนเลส + น้ำหยดอัตโนมัติ'),
            ('บันไดนอก', 'คอนกรีตหล่อ กว้าง 1.20 ม. ราวกระจก + มือจับ · ผิวกันลื่น R11 · ไฟส่องทางทุกขั้น'),
            ('กระจก', 'Low-E laminated · SHGC <= 0.25 ทิศตะวันออก/ตะวันตก · กรอบอะลูมิเนียมสีดำ'),
            ('พื้น', 'อิฐปูพื้น (คอร์ต/ศาลา) · ไม้เอ็นจิเนียร์ (ชั้น 2-4) · กระเบื้องกันลื่น R11'),
            ('ภายนอก', 'สระน้ำเกลือ 14.00 x 2.70 ลึก 1.40 ม. · สระสะท้อนเงาในคอร์ตลึก 0.30 ม. · รั้วอิฐ')]
    yb2 = table(ov, 236, 400, [('หมวด', 28, 'left'), ('ข้อกำหนด (ระดับแนวคิด)', 246, 'left')], mats, fs=6.4, rh=9.0, title='วัสดุหลัก')
    nxt = ['1. วิศวกรโครงสร้าง: พื้นสวนหลังคา (น้ำหนักดิน) + รางต้นไม้ยื่น + เพดานโค้งอิฐ + บันไดนอก 4 ช่วง + เสาเข็ม',
           '2. วิศวกรงานระบบ: VRF + ERV, พัดลมระบาย, ระบบน้ำฝน/น้ำหยด, ระบายน้ำคอร์ต, ปั่นไฟ, โซลาร์ %.2f kWp' % C['kwp'],
           '3. ยืนยันกับสำนักงานเขต: ข้อ 27 (บันไดนอกผ่านสวนหลังคาเป็นทางหนีไฟ), ความกว้างถนน, ผังเมืองรวม',
           '4. จำลอง CFD/ความร้อน: คอร์ตเป็นปล่องลม (ยังเป็นสมมติฐาน); จำลองแสง/แสงจ้าห้องหันคอร์ต',
           '5. แบบขยาย: ขอบพื้นโค้งมนรอบคอร์ต, รางต้นไม้, บันไดนอก, ประตู panic สู่สวน, เพดานโค้งอิฐ, ทางลาด 1:12',
           '6. ลงทะเบียน WELL Residence และเตรียมเอกสารตามตาราง',
           '7. ประมาณราคาละเอียด (BOQ) หลังได้แบบโครงสร้าง-งานระบบ']
    yb2 = para(ov, 236, yb2 - 5, 274, 'สิ่งที่ต้องทำต่อ', nxt, fs=6.4)
    summ = ['ผลตรวจทั้งหมด %d รายการ: ผ่าน %d / ไม่ผ่าน %d (รายการ "ยกเว้น" มีเหตุผลกำกับ ดู A-11)' % (len(RES), sum(1 for r in RES if r[4]), sum(1 for r in RES if not r[4])),
            'แบบระดับ design development ต้องให้สถาปนิกและวิศวกรผู้ได้รับใบอนุญาตตรวจสอบและลงนามก่อนยื่นขออนุญาต']
    para(ov, 236, yb2 - 3, 274, 'สรุปการตรวจ', summ, fs=6.6, tcol='#b22222')
    image(fig, ov, 'CAM_5_Roof_Garden_W.png', 12, 16, 245, 150, 'จากสวนหลังคาปีกตะวันตก (+3.65) — มองคอร์ต ลาน BBQ และขั้นสวนที่สูงขึ้น', cap_above=True)
    image(fig, ov, 'CAM_4_Garden_South.png', 265, 16, 245, 150, 'จากสวนทิศใต้ — ปีกใต้ 4 ชั้น รางต้นไม้ห้อยทุกขอบพื้น', cap_above=True)
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
    pdf = os.path.join(OUT, 'WELL-RIVERA-30x30-drawings.pdf')
    with PdfPages(pdf) as pp:
        for f in pages:
            pp.savefig(f)
    if '--png' in sys.argv:
        for i, f in enumerate(pages):
            f.savefig('/tmp/well/rv7/sheet_%02d.png' % (i + 1), dpi=60)
    for f in pages: plt.close(f)
    print('pdf', pdf, len(pages))
    if '--dxf' in sys.argv:
        build_dxf(os.path.join(OUT, 'WELL-RIVERA-30x30-CAD.dxf'))
        print('dxf ok')
