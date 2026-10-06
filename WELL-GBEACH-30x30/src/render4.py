# -*- coding: utf-8 -*-
"""A2 sheet set (PDF) + DXF assembly for WELL-GBEACH 30x30 (4 floors)."""
import os, math, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from PIL import Image
from cad4 import draw_mpl, scaled_axes, DXF, Rec
from frame4 import *
from plan4 import FLOORS, PROGRAM, PROGRAM_NUA, PROGRAM_GFA, all_rooms, CORE_AREA
from walls4 import model, side_of
from draw4 import plan, grid, PLAN_VIEW, north_arrow, section_marks
from proj4 import elevation, section, SECTIONS
from site4 import site_plan, roof_plan
from verify4 import run, areas, cost

A2 = (594, 420)
OUT = '/mnt/user-data/outputs'
REND = '/mnt/user-data/uploads/WELL/WELL-GBEACH-30x30/renders/GB4r2_'
PROJ = 'WELL-GBEACH 30x30 · Executive Luxury Villa · บ้านเดี่ยว 4 ชั้น "แท่งบนเสาลอย + ทรงกระบอกอิฐ" (แนวคิดจาก G-Beach Residence)'
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
    ov.text(x, 386, 'WELL-GBEACH 30x30', fontsize=8.5, fontweight='bold', va='top')
    ov.text(x, 381, 'Executive Luxury Villa\nบ้านเดี่ยว 4 ชั้น ผ่านเกณฑ์\nWELL for Residential (เจตนา)', fontsize=6.5, va='top', linespacing=1.35)
    ov.text(x, 365, 'ที่ดิน 30.00 x 30.00 ม. = 225 ตร.ว.\nถนนสาธารณะทิศเหนือ (สมมติ 8.00 ม.)', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [355, 355], lw=0.6, c='#111')
    ov.text(x, 352, 'แนวคิด', fontsize=6, color='#777', va='top')
    ov.text(x, 347, 'จาก G-Beach Residence (B+D+M):\nแท่ง 15.00 x 22.50 ม. บนเสาลอย\n+ แกนบันไดทรงกระบอกอิฐ Ø5.40\n+ ผนังอิฐโปร่งทิศตะวันตก', fontsize=6, va='top', linespacing=1.35)
    ov.plot([TITLE_X, A2[0] - 8], [326, 326], lw=0.6, c='#111')
    ov.text(x, 323, 'ระดับ', fontsize=6, color='#777', va='top')
    ov.text(x, 318, '±0.00 ถนน · F1 +0.45 · F2 +3.85\nF3 +7.25 · F4 +10.65\nหลังคา +14.05 · parapet +14.65\nยอดทรงกระบอก +14.85', fontsize=6, va='top', linespacing=1.35)
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
ENC = sum(a[1] for a in AR); SEMI = sum(a[2] for a in AR) + PAV; PARK = sum(a[3] for a in AR); FST = sum(a[4] for a in AR)
KIND = {'room': 'ห้องใช้งาน', 'wet': 'ห้องน้ำ/เปียก', 'svc': 'บริการ', 'circ': 'สัญจร', 'stair': 'บันได', 'lift': 'ลิฟต์', 'core': 'แกนบันได',
        'fstair': 'บันไดหนีไฟ', 'inb': 'กึ่งภายนอก', 'park': 'จอดรถ', 'void': 'ช่องโล่ง', 'shaft': 'ช่องท่อ'}

def room_rows(fl):
    rows = []
    for r in FLOORS[fl]:
        if 'ส่วนต่อเนื่อง' in r.name: continue
        a = r.a + sum(q.a for q in FLOORS[fl] if q.name == r.name + ' (ส่วนต่อเนื่อง)')
        if r.kind == 'core': a = CORE_AREA
        rows.append((r.code, r.name[:34], '%.2f x %.2f' % (r.w / 1000, r.d / 1000) if r.kind != 'core' else 'Ø 5.40', '%.2f' % a, KIND.get(r.kind, r.kind)))
    return rows

ROOMCOLS = [('รหัส', 9, 'center'), ('ห้อง', 52, 'left'), ('ขนาด ม.', 20, 'center'), ('ตร.ม.', 12, 'right'), ('ประเภท', 19, 'left')]
pages = []

# ============================================================== A-01 concept + limitations
def A01():
    fig, ov = sheet('A-01', 'แนวคิด G-Beach -> บ้าน 30x30\n+ รายงานข้อจำกัด', 'ไม่มีมาตราส่วน')
    imgs = [('CAM_1_Aerial_SE.png', 'มุมมองทางอากาศ ทิศตะวันออกเฉียงใต้ — แท่งอาคารบนเสาลอย, ทรงกระบอกอิฐ, ระเบียงทิศตะวันออก, สระ 3.80 x 16.00 ม.'),
            ('CAM_6_Aerial_SW.png', 'มุมมองทิศตะวันตกเฉียงใต้ — ผนังอิฐโปร่งทิศตะวันตก (บังแดดบ่าย) + บันไดหนีไฟเหล็กภายนอก'),
            ('CAM_3_Street_North.png', 'จากถนนทิศเหนือ — โรงจอดรถใต้เสาลอย (Pilotis) และโถงทางเข้า'),
            ('CAM_5_West_Lattice.png', 'ผนังอิฐโปร่ง (ครีบอิฐ 115 มม. @290 + แถบนอน @520) ห่างผนังอาคาร 0.34-0.45 ม.')]
    pos = [(12, 283, 160, 100), (176, 283, 160, 100), (12, 172, 160, 100), (176, 172, 160, 100)]
    for (f, cap), (x, y, w, h) in zip(imgs, pos):
        image(fig, ov, f, x, y, w, h, cap)
    ov.text(12, 400, 'ภาพจากโมเดล Blender (WELL-GBEACH-30x30-model.blend) — โมเดลมวลอาคารระดับ DD สร้างจากข้อมูลชุดเดียวกับแบบ CAD', fontsize=6, color='#555', va='top')
    concept_diagrams(fig, ov)
    X0, W0 = 342, 170
    facts = [('ที่ตั้ง / ปี', 'Jesolo อิตาลี · 2025 · 4,520 ตร.ม. (อาคารชุดพักอาศัย ไม่ใช่บ้านเดี่ยว)'),
             ('ผู้ออกแบบ', 'B+D+M Architetti (Alex Braggion, GianPaolo Di Benedetto)'),
             ('บริบท', 'ตั้งข้าง Hotel Bellevue (1956, Renzo Menegazzo) ที่อ้างถึงห้องสมุด Belo Horizonte ของ Niemeyer'),
             ('ผัง', 'แท่งยาว วางตั้งฉากกับโรงแรม ล้อมคอร์ต · ชั้นล่างกระจก บนเสาลอย (pilotis)'),
             ('ผิว / วัสดุ', 'คอนกรีต กระจก อิฐโชว์แนว · แผงอิฐโปร่ง (openwork brick lattice)'),
             ('องค์ประกอบ', 'แกนทรงกระบอก · ระเบียงรอบ · loggia ทิศตะวันตก · ดาดฟ้ามองได้ 360° · ที่จอดรถใต้ดิน')]
    yb = table(ov, X0, 398, [('หัวข้อ', 24, 'left'), ('ข้อเท็จจริงจากแหล่งที่เผยแพร่ (ArchDaily / whitemad / jidipi)', 146, 'left')], facts, fs=6.0,
               title='G-Beach Residence — ข้อเท็จจริงที่ตรวจได้')
    interp = [('แท่งบนเสาลอย', 'แท่ง 15.00 x 22.50 ม. วางแนวเหนือ-ใต้ ชั้น 1 เปิดโล่งเป็นโรงรถ+ใต้ถุน ชั้น 3-4 สั้นลงเหลือ 15.30 ม.'),
              ('ทรงกระบอก', 'แกนบันได U อิฐโชว์ Ø5.40 ม. ยื่นออกทิศตะวันออก สูง +14.85 ช่องแสงกระจกที่ยอด'),
              ('อิฐโปร่ง', 'ย้ายมาไว้ทิศตะวันตก = ทิศแดดบ่ายของกรุงเทพฯ หน้า loggia ชั้น 3 และผนังชั้น 2-4'),
              ('ระเบียง / loggia', 'ระเบียงลึก 1.20 ม. ทิศตะวันออก ชั้น 2-3 · loggia ตะวันตก+เหนือ ชั้น 3'),
              ('ดาดฟ้า 360°', 'ชั้น 4: ระเบียง Master เปิดฟ้า + ระเบียง BBQ หลังคาคลุม'),
              ('ไม่นำมาใช้', 'ที่จอดรถใต้ดิน (น้ำใต้ดินสูง/ค่าใช้จ่าย) -> จอดใต้เสาลอยที่ระดับดิน')]
    yb = table(ov, X0, yb - 7, [('องค์ประกอบ', 24, 'left'), ('การตีความของเรา (ไม่ใช่คำอธิบายของสถาปนิก)', 146, 'left')], interp, fs=6.0,
               title='การตีความ -> แบบบ้านหลังนี้')
    lim = [
        '1. โปรแกรมขัดกัน: Master Suite ชั้น 3 แต่ Closet 36 + Terrace 28 ชั้น 4 -> ทำ Master duplex มีบันไดส่วนตัวชั้น 3-4 (ตามที่เลือก)',
        '2. Pantry โปรแกรมอยู่ชั้น 3 ห่างจากครัว -> ย้ายไปชั้น 2 ติดครัวโชว์ (ตามที่เลือก)',
        '3. ความสูงชั้น 2.80 ในโปรแกรม = ระยะโปร่ง; ใช้พื้นถึงพื้น 3.40 ม. -> หลังคา +14.05, ยอดทรงกระบอก +14.85 ต่ำกว่า 15.00 ม. แค่ 0.15 ม. (ห้ามเพิ่มถังน้ำ/ห้องบนหลังคา)',
        '4. GFA %.2f vs โปรแกรม %.2f (%+.1f%%): ทรงกระบอก 4 ชั้น %.1f + บันไดหนีไฟ %.1f + สัญจร %.1f + loggia ชั้น 3 %.1f (ชั้น 4 ต้องการพื้นที่มากกว่าชั้น 3 ในโปรแกรม จึงเหลือเป็น loggia)' %
        (C['gfa'], PROGRAM_GFA, C['gfa'] / PROGRAM_GFA * 100 - 100, CORE4, FST, CIRC, LOGGIA3),
        '5. บันไดหนีไฟภายนอก (ฉ.55 ข้อ 27 สำหรับอาคาร 4 ชั้น) — ต้องยืนยันกับเจ้าพนักงานว่าบ้านเดี่ยวต้องมีหรือไม่; ชั้น 2 ทางหนีไฟผ่านครัวโชว์และ Pantry',
        '6. ค่าที่ชนเกณฑ์พอดี: บันไดหนีไฟห่างเขต 3.00 ม. (ข้อ 50), ชานพัก = ความกว้างบันได 1.00 ม., ทางลาด 1:12 ยังไม่ได้เขียน (โรงรถ +0.15 -> โถง +0.45)',
        '7. ความกว้างถนนไม่ทราบ — สมมติ 8.00 ม. (ระยะร่น 1/10 = 0.80 ม.; แบบร่นจริง 3.50 ม.)',
        '8. ห้องลึกเกิน 4.20 ม. (ยกเว้นพร้อมเหตุผล): ห้องอาหาร ห้องนั่งเล่น ห้องนอน Master ห้องนั่งเล่นครอบครัว ห้องทำงาน (แสงเหนือ+ช่องแสงหลังคา) เธียเตอร์',
        '9. ห้องที่ช่องเปิดไม่ถึง 10%% ใช้พัดลมระบาย (ฉ.39 ข้อ 6 วรรคสอง): %d ห้อง (รายชื่อใน A-12)' % len(INFO['fans']),
        '10. ทรงกระบอกอิฐ 4 ชั้น + ผนังอิฐโปร่ง ~%d ตร.ม. ต้องมีโครงเหล็ก/ค.ส.ล. รับแรงลม-แผ่นดินไหว (วิศวกรโครงสร้าง)' % round((BAR[3] - 4000) / 1000 * (PARAPET - F2) / 1000 * 0.6),
        '11. ไม่ทราบผังเมืองรวม/ข้อบัญญัติท้องถิ่น (FAR/OSR/ความสูง) — ต้องตรวจก่อนยื่น',
    ]
    yb = para(ov, X0, yb - 4, W0, 'รายงานข้อจำกัด (ตรงไปตรงมา)', lim, fs=6.6, gap=1.0, tcol='#b22222')
    para(ov, X0, yb - 5, W0, 'แหล่งข้อมูลอ้างอิง G-Beach', [
        '· archdaily.com/1042315 (G-Beach Residence / B+D+M Architetti)', '· whitemad.pl (บทความโครงการ G-Beach)', '· architectures.jidipi.com (G-Beach Residence)',
        '· architizer.com/projects/g-beach-residence (ลิงก์ที่ผู้ใช้ให้มา)',
        'ไม่ได้รับแบบจริงของโครงการ — สัดส่วน ขนาด และรายละเอียดทั้งหมดในชุดนี้เป็นการออกแบบใหม่ ไม่ใช่การคัดลอกหรือย่อส่วนอาคารต้นแบบ'], fs=6.2)
    pages.append(fig)

def concept_diagrams(fig, ov):
    R = Rec()
    zc = {'park': '#cfcfcf', 'inb': '#efe3c8', 'circ': '#f6d36b', 'stair': '#e0a526', 'lift': '#e0a526', 'core': '#b8674a', 'fstair': '#8a9098',
          'room': '#a9cbe8', 'wet': '#cfe3ee', 'svc': '#d9d2e9', 'void': '#ffffff'}
    R.rect(0, 0, LOT_W, LOT_D, 'C-PROP', lw=0.4)
    R.frect(POOL[0], POOL[1], POOL[2], POOL[3], 'A-AREA', color='#7fb7d0', z=1)
    R.frect(PAVILION[0], PAVILION[1], PAVILION[2], PAVILION[3], 'A-AREA', color='#efe3c8', z=1)
    for r_ in FLOORS[2]:
        if r_.kind == 'core': continue
        R.frect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-AREA', color=zc.get(r_.kind, '#ddd'), z=1)
        R.rect(r_.x0, r_.y0, r_.x1, r_.y1, 'A-WALL-INT', lw=0.12)
    pts = [(CORE_C[0] + CORE_R * math.cos(t / 40 * 2 * math.pi), CORE_C[1] + CORE_R * math.sin(t / 40 * 2 * math.pi)) for t in range(41)]
    R.fill(pts, 'A-AREA', color='#b8674a', z=2)
    R.rect(BAR[0] - 450, 4000, BAR[0] - 335, BAR[3], 'A-AREA', lw=0.6)
    R.text((CORE_C[0] + 3600, CORE_C[1] + 300), 'ทรงกระบอก\nอิฐ Ø5.40', 520, 'A-TEXT', bold=True)
    R.text((1600, 13000), 'อิฐโปร่ง\nทิศตะวันตก', 480, 'A-TEXT', bold=True)
    R.text((13000, 28300), 'ถนน (ทิศเหนือ)', 520, 'A-TEXT', bold=True)
    R.text(((POOL[0] + POOL[2]) / 2, 16800), 'สระ', 480, 'A-TEXT', bold=True)
    R.text((13000, 8000), 'แท่งอาคาร\n15.00 x 22.50', 560, 'A-TEXT', bold=True)
    north_arrow(R, (28200, 28000), 700)
    V = (-1000, -800, 31000, 31000)
    place(fig, R, V, 14, 22, 250)
    ov.text(14, 154, 'ไดอะแกรมผัง (ชั้น 2, 1:250): แท่งบนเสาลอย + ทรงกระบอก + ผนังอิฐโปร่ง + สวนสระทิศตะวันออก', fontsize=6.3, fontweight='bold', va='top')
    S = section('A')
    def arrow(a, b, lw=0.9):
        S.line(a, b, 'A-ANNO', lw=lw)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        S.pline([(b[0] - 700 * math.cos(ang - .4), b[1] - 700 * math.sin(ang - .4)), b, (b[0] - 700 * math.cos(ang + .4), b[1] - 700 * math.sin(ang + .4))], 'A-ANNO', lw=lw)
    for z in (5500, 9000, 12300):
        arrow((-1200, z + 2600), (4600, z))                       # west afternoon sun hits lattice
        arrow((31000, z - 300), (21900, z - 300), 0.6)           # east breeze through balconies
    S.text((-900, 16300), 'แดดบ่ายทิศตะวันตก -> ผนังอิฐโปร่ง', 420, 'A-ANNO', ha='left')
    S.text((31200, 15600), 'ลมตะวันออก/ตะวันออกเฉียงใต้ -> ระเบียง -> ทะลุห้อง', 420, 'A-ANNO', ha='right')
    V2 = (-1800, -2800, 32500, 17200)
    place(fig, S, V2, 186, 30, 250)
    ov.text(186, 154, 'ไดอะแกรมรูปตัด A-A (1:250): บังแดดตะวันตก / ระบายอากาศข้ามห้อง ตะวันออก-ตะวันตก', fontsize=6.3, fontweight='bold', va='top')
    ov.text(186, 26, 'ลูกศร = เจตนาการออกแบบ (ทิศลมประจำกรุงเทพฯ ฤดูร้อน S/SW, หนาว NE) — ยังไม่ได้พิสูจน์ด้วย CFD/การจำลองแสง', fontsize=5.4, color='#b22222', va='top')

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
    rows += [('ศาลาริมสระ', '-', '%.2f' % PAV, '-', '-', '%.2f' % PAV),
             ('รวม', '%.2f' % ENC, '%.2f' % SEMI, '%.2f' % PARK, '%.2f' % FST, '%.2f' % C['gfa']),
             ('โปรแกรม', '', '', '', '', '%.2f' % PROGRAM_GFA),
             ('ส่วนต่าง', '', '', '', '', '%+.2f (%+.1f%%)' % (C['gfa'] - PROGRAM_GFA, C['gfa'] / PROGRAM_GFA * 100 - 100))]
    yb = table(ov, 266, yb - 9, [('ชั้น', 26, 'left'), ('ปิดล้อม*', 28, 'right'), ('กึ่งภายนอก', 28, 'right'), ('จอดรถ', 24, 'right'), ('บันไดหนีไฟ', 26, 'right'), ('รวม ตร.ม.', 36, 'right')],
               rows, fs=5.0, title='พื้นที่อาคาร (คิดถึงแนวศูนย์กลางผนัง)')
    ov.text(266, yb - 1.5, '* รวมแกนทรงกระบอก %.2f ตร.ม./ชั้น (คิดเป็นวงกลม) · บันไดหนีไฟภายนอกไม่รวมใน GFA' % CORE_AREA, fontsize=4.7, va='top', color='#555')
    rows = [('พื้นที่ดิน', '900.00 ตร.ม. (225 ตร.ว.)'), ('พื้นที่อาคารคลุมดิน (รวมศาลา)', '%.2f ตร.ม. (%.1f%%)' % (INFO['cover'], INFO['cover'] / 9)),
            ('ที่ว่าง', '%.1f%%  (เกณฑ์ >= 30%%)' % INFO['os1']), ('FAR (GFA ปิดล้อม / ที่ดิน)', '%.2f : 1' % (ENC / 900)),
            ('ความสูงอาคาร', 'หลังคา 14.05 / parapet 14.65 / ยอดทรงกระบอก 14.85 ม. (< 15.00)'),
            ('ที่ดินขั้นต่ำตามโปรแกรม', '113 ตร.ว. — ที่ดินจริง 225 ตร.ว.')]
    yb = table(ov, 266, yb - 9, [('รายการ', 62, 'left'), ('ค่า', 116, 'left')], rows, fs=5.0, title='ที่ว่างและการใช้ที่ดิน')
    rows = [('(ก) อัตราแยกมาตรฐาน', 'ปิดล้อม %.2f x 22,000 + กึ่งภายนอก %.2f x 11,000 + จอดรถ %.2f x 8,000' % (C['enc'], C['semi'], C['park']), '%.2f' % (C['std'] / 1e6)),
            ('(ข) อัตราแยก luxury', 'ปิดล้อม x 30,000 + กึ่งภายนอก x 15,000 + จอดรถ x 12,000', '%.2f' % (C['lux'] / 1e6)),
            ('(ค) อัตราเดียว (วิธีเดียวกับโปรแกรม)', 'GFA %.2f x 30,000' % C['gfa'], '%.2f' % (C['single'] / 1e6)),
            ('งานนอกอาคาร', 'สระ %.1f ตร.ม. x 35,000 + PV %.2f kWp x 45,000 + ภูมิทัศน์/รั้ว 1.80 + ลิฟต์ 0.90 + บันไดหนีไฟ 1.20 ล.' % (C['pool'], C['kwp']), '%.2f' % (C['extra'] / 1e6)),
            ('โปรแกรม ARCHISPACE', '984.70 x 30,000 (ช่วง %.2f-%.2f ล้าน)' % (PROG_LO, PROG_HI), '%.2f' % PROG_BUDGET)]
    yb = table(ov, 266, yb - 9, [('วิธีคิด', 48, 'left'), ('สูตร (บาท/ตร.ม.)', 112, 'left'), ('ล้านบาท', 18, 'right')], rows, fs=4.9, title='ประมาณราคาค่าก่อสร้าง (ระดับแนวคิด)')
    para(ov, 266, yb - 3, 240, None, [
        'อัตราแยก vs อัตราเดียว: (ก) %.2f ล้าน ต่ำกว่างบโปรแกรม; (ข) %.2f ล้าน อยู่ในช่วง %.2f-%.2f; (ค) %.2f ล้าน แตะขอบบนของช่วง เพราะ GFA มากกว่าโปรแกรม %.1f%%' %
        (C['std'] / 1e6, C['lux'] / 1e6, PROG_LO, PROG_HI, C['single'] / 1e6, C['gfa'] / PROGRAM_GFA * 100 - 100),
        'รวมงานนอกอาคาร: (ข)+%.2f = %.2f ล้าน · (ค)+%.2f = %.2f ล้าน (เกินช่วงบนของโปรแกรม)' % (C['extra'] / 1e6, (C['lux'] + C['extra']) / 1e6, C['extra'] / 1e6, (C['single'] + C['extra']) / 1e6),
        'ยังไม่รวม: เสาเข็ม/ฐานราก (รอผลเจาะดิน), เฟอร์นิเจอร์ลอยตัว, ภาษี/ค่าธรรมเนียม, ค่าออกแบบ'], fs=4.9)
    pages.append(fig)

# ============================================================== plans
TITLES = {1: 'ผังพื้นชั้น 1  (FFL +0.45)', 2: 'ผังพื้นชั้น 2  (FFL +3.85)', 3: 'ผังพื้นชั้น 3  (FFL +7.25)', 4: 'ผังพื้นชั้น 4  (FFL +10.65)'}
NOTES = {1: ['· ชั้น 1 = ใต้ถุนเสาลอย (Pilotis): โรงจอดรถ 4 คันใต้แท่งอาคาร (+0.15) และใต้ถุน/ลานซักล้างทิศใต้ เปิดโล่ง ระบายลม',
             '· โถงต้อนรับสูง 2 ชั้น (+0.45) เข้าจากโรงรถผ่านห้องพักคอย ประตูคู่ 2.00 ม.; ทางลาด 1:12 ยาว 3.60 ม. ต้องเพิ่มในแบบขยาย',
             '· แกนทรงกระบอกอิฐ Ø5.40 ม. (ภายใน Ø5.00): บันได U ลูกตั้ง 170 / ลูกนอน 280 กว้าง 1.00 ม. ประตูทิศ 205° (โถง) และ 0° (สวนสระ)',
             '· ปีกบริการทิศตะวันตก: ครัวไทย ห้องแม่บ้าน 2 ห้อง ซักรีด MEP ห้องเก็บของ/คนขับรถ — ต่อกับบันไดหนีไฟภายนอก',
             '· ห้องนอนแขก (ผู้สูงอายุ) ทิศใต้-ตะวันออก ประตูบานเลื่อนเข้าห้องน้ำ ใกล้ลิฟต์',
             '· จุดชาร์จรถไฟฟ้า (EV) 1 จุดในโรงรถ (WELL R-A09)'],
         2: ['· ส่วนรวมเรียงตามทิศใต้: ครัวโชว์ -> ห้องอาหาร -> ห้องนั่งเล่น -> ระเบียงตะวันออก 1.20 ม. (มองสระ)',
             '· Pantry ย้ายจากชั้น 3 (โปรแกรม) มาติดครัวโชว์ + ห้องเก็บของ; ห้องไวน์/ซิการ์ ไม่มีหน้าต่าง (ตั้งใจ ควบคุมอุณหภูมิ)',
             '· ช่องโล่งโถงต้อนรับ ราวกระจกสูง 1.10 ม.; Gallery ทิศเหนือ-ตะวันออก',
             '· Junior Suite 2-3 และห้องทำงานอยู่ใต้หลังคาสวน +7.25 ทิศเหนือ (ช่องแสงหลังคา 2 ชุดเหนือห้องทำงาน)',
             '· ทางหนีไฟชั้น 2: Pantry -> บันไดหนีไฟภายนอกทิศตะวันตก'],
         3: ['· ชั้นส่วนตัว Master: Walk-in -> ห้องน้ำ Spa + Jacuzzi -> ห้องนอน Master -> ระเบียงตะวันออก',
             '· บันไดส่วนตัว Master (ชั้น 3-4) ขึ้นสู่ Closet และระเบียงดาดฟ้า (Master duplex ตามที่เลือก)',
             '· Loggia ทิศตะวันตก (หลังผนังอิฐโปร่ง) และ Loggia ทิศเหนือ = พื้นที่กึ่งภายนอกบนหลังคาสวนชั้น 2',
             '· หลังคาสวน +7.25 เหนือ Junior Suite/ห้องทำงาน ทิศเหนือ'],
         4: ['· Master Walk-in Closet (U/L + ไอส์แลนด์) ต่อบันไดส่วนตัว และระเบียง Master เปิดฟ้า (pergola)',
             '· ระเบียง & BBQ หลังคาคลุม 5.40 x 7.90 ม. ทิศใต้-ตะวันออก มองสระ (ดาดฟ้า "360°" ตีความจาก G-Beach)',
             '· ห้องนั่งเล่นครอบครัว & Gallery ทิศตะวันตก หลังผนังอิฐโปร่ง · ห้องโฮมเธียเตอร์ทิศเหนือ หน้าต่าง 3.60 ม. + ม่านทึบ',
             '· หลังคา +14.05 เหนือชั้น 4: แผงโซลาร์ %d แผง = %.2f kWp' % (round(C['kwp'] / 0.55), C['kwp'])]}

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
               [('พื้นที่ปิดล้อม (รวมแกน)', '%.2f' % enc), ('กึ่งภายนอก', '%.2f' % semi), ('จอดรถ', '%.2f' % park), ('รวม', '%.2f' % (enc + semi + park)),
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
    ra = INFO['roofs']; tot = sum(ra.values())
    rows = [('หลังคาสวน +7.25 (เหนือชั้น 2 ทิศเหนือ)', '%.2f' % ra['green']), ('หลังคาหลัก +14.05 (ค.ส.ล. ขาว SR)', '%.2f' % ra['main']),
            ('รวม', '%.2f' % tot), ('สัดส่วนหลังคาเขียว', '%.0f%%' % (ra['green'] / tot * 100))]
    yb = table(ov, 382, 400, [('หลังคา', 80, 'left'), ('ตร.ม.', 32, 'right')], rows, fs=5.4, title='พื้นที่หลังคา')
    rows = [('ฝนรายปีกรุงเทพฯ (ประมาณ)', '~1,500 มม./ปี'), ('น้ำฝนเก็บได้ (แข็ง C=0.9, สวน C=0.4)', '%.0f ลบ.ม./ปี' % ((ra['main'] * 0.9 + ra['green'] * 0.4) * 1.5)),
            ('ถังเก็บน้ำฝนใต้ดิน 2.50 x 2.50 ม.', '~12 ลบ.ม. (รดน้ำ/ชักโครก)'), ('แผงโซลาร์ %d x 550 Wp' % round(C['kwp'] / 0.55), '%.2f kWp ~ %s kWh/ปี*' % (C['kwp'], format(round(C['kwp'] * 1250, -2), ',.0f'))),
            ('ยอดทรงกระบอก +14.85', 'ช่องแสงกระจก Ø5.30 ม.')]
    yb = table(ov, 382, yb - 8, [('รายการ', 70, 'left'), ('ค่า', 42, 'left')], rows, fs=5.0, title='น้ำฝน และพลังงาน')
    para(ov, 382, yb - 4, 130, 'ชั้นหลังคา', [
        '· หลังคาสวน: พืชคลุมดิน + ดินปลูก 150 มม. + แผ่นใยกรอง + แผ่นระบายน้ำ 20 มม. + แผ่นกันราก + กันซึม 2 ชั้น + ค.ส.ล. ลาด 1:100',
        '· หลังคาหลัก: สีสะท้อนแสง SR >= 0.75 + PU foam 50 มม. + กันซึม + ค.ส.ล. 200',
        '· ระเบียง Master ชั้น 4 (เปิดฟ้า): พื้นไม้เทียมบนขาตั้ง + pergola; ระเบียง BBQ: หลังคา ค.ส.ล. คลุม',
        '· Parapet สูง 0.60 ม.',
        '· RD = ท่อระบายน้ำฝน ลงรางรอบอาคาร -> ถังน้ำฝน',
        '* พลังงาน PV ประมาณ ~1,250 kWh/kWp/ปี — ต้องคำนวณจริงรวมเงาทรงกระบอก/pergola'], fs=5.0)
    pages.append(fig)

ENAMES = {'S': 'รูปด้านทิศใต้ (สวน/ใต้ถุน)', 'N': 'รูปด้านทิศเหนือ (ด้านถนน)', 'E': 'รูปด้านทิศตะวันออก (สระ/ทรงกระบอก)', 'W': 'รูปด้านทิศตะวันตก (ผนังอิฐโปร่ง/บันไดหนีไฟ)'}
ENOTES = ['วัสดุผิว (ระดับแนวคิด)', '· ผนังภายนอก: ฉาบเรียบสีขาว (render) บนบล็อกมวลเบา 200', '· ทรงกระบอก: อิฐโชว์แนว สีส้มอิฐ (brick) + ช่องแสงยอด',
          '· ผนังอิฐโปร่ง: ครีบอิฐ 115 @290 + แถบนอน @520 บนโครงเหล็กกัลวาไนซ์', '· เสาลอย ค.ส.ล. 0.40 x 0.40 ผิวคอนกรีตเปลือย',
          '· กระจก Low-E laminated กรอบอะลูมิเนียมสีเทาเข้ม', '· ราวกันตกกระจกสูง 1.10 ม.', '· บันไดหนีไฟ: เหล็กกัลวาไนซ์ทาสี ราว 1.10 ม.',
          '· แผงโซลาร์บนหลังคา +14.05 (มองไม่เห็นจากระดับถนน)']

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
        para(ov, 382, 200, 130, None, ['หมายเหตุรูปตัด', '· พื้นถึงพื้น 3.40 ม. = พื้น 0.20 + ฝ้า/งานระบบ 0.40 + โปร่ง 2.80 ม. (ตามความสูงในโปรแกรม)',
                                       '· เสาเข็ม/ฐานรากเขียนเป็นสัญลักษณ์ — ขนาดจริงตามวิศวกรโครงสร้าง', '· รูปตัด B-B เห็นแกนทรงกระบอกอิฐและบันไดภายในด้านหลัง',
                                       '· หลังคาสวน +7.25: ดินปลูก 150 มม. น้ำหนักอิ่มน้ำ ~250-300 กก./ตร.ม.'], fs=5.4)
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
            rs = [r for r in all_rooms() if r.name in rooms]; a = sum(r.a for r in rs); f = 'F%d' % rs[0].fl
        rows.append((nm[:34], 'F%d' % pf, '%.2f' % pa, f, '%.2f' % a, '%+.2f' % (a - pa)))
    tp = sum(p[2] for p in PROGRAM); td = sum(float(r[4]) for r in rows)
    rows.append(('รวม NUA', '', '%.2f' % tp, '', '%.2f' % td, '%+.2f' % (td - tp)))
    colors = [('#fde2e2' if (r[1] != r[3] and r[3] != 'สวน' and r[0] != 'รวม NUA') else None) for r in rows]
    yb = table(ov, 410, 402, [('รายการโปรแกรม', 44, 'left'), ('ชั้น', 7, 'center'), ('โปรแกรม', 13, 'right'), ('ชั้นแบบ', 9, 'center'), ('แบบ', 12, 'right'), ('ต่าง', 12, 'right')],
               rows, fs=4.9, rh=5.6, title='เทียบโปรแกรม ARCHISPACE (ตร.ม.)', colors=colors)
    para(ov, 410, yb - 2, 97, None, ['แถบชมพู = ชั้นในแบบต่างจากโปรแกรม (Pantry ชั้น 3 -> 2 ตามที่เลือก ดู A-01 ข้อ 2)',
                                     'ส่วนต่างพื้นที่ห้อง: ห้องตามกริดเสา 15.00 ม. ปัดขึ้น/ลง ±10-15% — ห้องที่เล็กกว่าโปรแกรมเกิน 10% ดูแถว "ต่าง" ติดลบ'], fs=4.7)
    pages.append(fig)

def A12():
    fig, ov = sheet('A-12', 'WELL for Residential\n+ วัสดุ + สิ่งที่ต้องทำต่อ', 'ไม่มีมาตราส่วน')
    wl = [r for r in RES if r[0].startswith('WELL')]
    gv = lambda k: [r[2] for r in wl if r[0] == k][0]
    feat = [
        ('R-A01 ระบบระบายอากาศ', 'พัดลมดูดเฉพาะจุดครัว/ห้องน้ำ/ห้องไม่มีหน้าต่าง %d ห้อง + ERV ห้องนอน' % len(INFO['fans']), 'ระบุในแบบงานระบบ', 'ต้องวัด'),
        ('R-A05 ลดการเผาไหม้', 'ครัวโชว์ชั้น 2 เตาไฟฟ้าเหนี่ยวนำ; ครัวไทยชั้น 1 แยก มีฮูด + เปิด 2 ด้าน', 'ในแบบ', 'เอกสาร'),
        ('R-A09 จุดชาร์จ EV', '1 จุดในโรงรถใต้เสาลอย (ท่อเผื่อ 4 ช่อง)', 'ในแบบ', 'ภาพถ่าย'),
        ('R-W03 น้ำที่ไม่ใช่น้ำดื่ม', 'ถังน้ำฝนใต้ดิน ~12 ลบ.ม. สำหรับรดน้ำ/ชักโครก', 'ในแบบ', 'แบบสุขาภิบาล'),
        ('R-L01 แสงธรรมชาติ', gv('WELL R-L01')[:44], 'คำนวณแล้ว', 'ต้องตรวจแสงจ้า'),
        ('R-L02 ควบคุมแสง', 'วงจรแยกทุกห้อง + ม่านทึบห้องนอน/เธียเตอร์', 'ระบุ', 'แบบไฟฟ้า'),
        ('R-T06 หน้าต่างเปิดได้', gv('WELL R-T06'), 'คำนวณแล้ว', 'มุ้งลวด/ตัวล็อก'),
        ('R-T07 ความร้อนภายนอก', 'หลังคาสวน + หลังคาขาว SR >= 0.75 + ผนังอิฐโปร่งทิศตะวันตก + ต้นไม้ร่ม', 'ในแบบ', 'ค่า SR วัสดุ'),
        ('R-V04 พื้นที่กิจกรรมกลางแจ้ง', 'สระ 3.80 x 16.00 ม. + ศาลา + ระเบียงทุกชั้น + ดาดฟ้า', 'ในแบบ', '-'),
        ('R-V07 ออกแบบบันได', 'บันไดในทรงกระบอก ประตูจากโถงทุกชั้น แสงจากยอด (ใช้ก่อนลิฟต์)', 'ในแบบ', 'ภาพถ่าย'),
        ('R-M01 ธรรมชาติและสถานที่', 'ห้องหลักมองสวนสระทิศตะวันออก; วัสดุอิฐ-ไม้', 'ในแบบ', '-'),
        ('R-M04 พื้นที่จัดเก็บ', 'Walk-in 2 ชั้น (Master) + ตู้ทุกห้องนอน + ห้องเก็บของทุกชั้น', 'ในแบบ', '-'),
        ('R-N01 การปรุงอาหาร', 'ครัว 2 ส่วน (โชว์/ไทย) + Pantry ห้องเย็นติดครัวโชว์', 'ในแบบ', '-'),
        ('R-S01 แนวกั้นเสียง', 'Master ทิศใต้ไกลถนน; Junior Suite ทิศเหนือใกล้ถนน -> กระจก 2 ชั้น', 'ต้องระบุ STC', 'ทดสอบ'),
        ('R-C01 ออกแบบเพื่อทุกคน', 'ลิฟต์บ้านทุกชั้น + ห้องแขกชั้น 1; ทางลาด 1:12 ยังต้องเพิ่ม', 'บางส่วน', 'ดู A-01 ข้อ 6'),
        ('R-C06 ภัยพิบัติ', 'ยกพื้น +0.45 + บันไดหนีไฟ + เครื่องปั่นไฟ', 'ในแบบ', 'ระดับน้ำท่วมจริง?'),
        ('R-X02 วัสดุ', 'สี/กาว VOC ต่ำ ไม้รับรอง FSC', 'สเปก', 'ใบสั่งซื้อ'),
    ]
    yb = table(ov, 12, 400, [('Feature (WELL for Residential)', 48, 'left'), ('การตอบสนองในแบบ', 118, 'left'), ('สถานะ', 25, 'left'), ('หลักฐานที่ต้องมี', 26, 'left')], feat, fs=7.0, rh=9.4,
               title='กลยุทธ์ WELL for Residential (รหัสตาม Guidebook ก.พ. 2026)')
    yb = para(ov, 12, yb - 4, 215, None, ['สถานะ = เจตนาการออกแบบ ยังไม่ใช่คะแนนรับรอง: WELL Residence ต้องลงทะเบียน IWBI ส่งเอกสาร และตรวจวัดจริงหลังก่อสร้าง',
                                         'ห้องที่ใช้พัดลมระบาย: ' + ', '.join(INFO['fans'])], fs=5.8)
    mats = [('โครงสร้าง', 'ค.ส.ล. เสา 0.40x0.40 กริด 5 x 6 แนว · พื้นไร้คาน/คานแบน 0.20 · ฐานรากเสาเข็มเจาะ (รอผลเจาะดิน)'),
            ('ทรงกระบอก', 'ผนัง ค.ส.ล. รับแรง + อิฐโชว์แนวกรุ (แบบแสดงหนา 200 — ต้องยืนยันความหนาจริง) · บันได ค.ส.ล.'),
            ('ผนังอิฐโปร่ง', 'อิฐ 115 มม. @290 + แถบนอน @520 ยึดโครงเหล็กกัลวาไนซ์ ห่างผนัง 0.34-0.45 ม.'),
            ('ผนังภายนอก', 'บล็อกมวลเบา 200 + ฉาบเรียบสีขาว · ผนังภายใน 120 / ห้องน้ำ 150'),
            ('กระจก', 'Low-E laminated · SHGC <= 0.25 ทิศ ตก/ออก · กรอบอะลูมิเนียมสีเทาเข้ม'),
            ('หลังคา', 'ค.ส.ล. + PU 50 + กันซึม + สี SR >= 0.75 · หลังคาสวน extensive 150 มม.'),
            ('พื้น', 'หินขัด (ชั้น 1) · ไม้เอ็นจิเนียร์ (ชั้น 2-4) · กระเบื้องกันลื่น R11 ห้องน้ำ'),
            ('ภายนอก', 'สระน้ำเกลือ 3.80 x 16.00 ลึก 1.40 ม. · พื้น WPC รอบสระ · บันไดหนีไฟเหล็กกัลวาไนซ์')]
    yb2 = table(ov, 236, 400, [('หมวด', 28, 'left'), ('ข้อกำหนด (ระดับแนวคิด)', 246, 'left')], mats, fs=6.6, rh=9.0, title='วัสดุหลัก')
    nxt = ['1. วิศวกรโครงสร้าง: ทรงกระบอก 4 ชั้น, ผนังอิฐโปร่ง (แรงลม), หลังคาสวน, เสาเข็ม',
           '2. วิศวกรงานระบบ: VRF + ERV, พัดลมระบาย, ระบบน้ำฝน, เครื่องปั่นไฟ, โซลาร์ %.2f kWp' % C['kwp'],
           '3. ยืนยันกับสำนักงานเขต: บันไดหนีไฟ (ข้อ 27) สำหรับบ้านเดี่ยว 4 ชั้น, ความกว้างถนนจริง, ผังเมืองรวม',
           '4. จำลองแสง/แสงจ้า และความร้อน: ผนังอิฐโปร่งลดแสงที่ loggia/ห้องนั่งเล่นครอบครัว (การคำนวณ R-L01 ยังไม่หักเงาอิฐ)',
           '5. แบบขยาย: ทางลาด 1:12, บันไดทรงกระบอก, บันไดส่วนตัว, ราวกันตก, ผนังอิฐโปร่ง, สระ',
           '6. ลงทะเบียน WELL Residence และเตรียมเอกสารตามตาราง',
           '7. ประมาณราคาละเอียด (BOQ) หลังได้แบบโครงสร้าง-งานระบบ']
    yb2 = para(ov, 236, yb2 - 5, 274, 'สิ่งที่ต้องทำต่อ', nxt, fs=6.6)
    summ = ['ผลตรวจทั้งหมด %d รายการ: ผ่าน %d / ไม่ผ่าน %d (รายการ "ยกเว้น" มีเหตุผลกำกับ ดู A-11)' % (len(RES), sum(1 for r in RES if r[4]), sum(1 for r in RES if not r[4])),
            'แบบระดับ design development ต้องให้สถาปนิกและวิศวกรผู้ได้รับใบอนุญาตตรวจสอบและลงนามก่อนยื่นขออนุญาต']
    para(ov, 236, yb2 - 3, 274, 'สรุปการตรวจ', summ, fs=6.6, tcol='#b22222')
    image(fig, ov, 'CAM_4_Aerial_NW.png', 12, 16, 245, 150, 'มุมมองทิศตะวันตกเฉียงเหนือ — หลังคาสวน +7.25, บันไดหนีไฟ, ผนังอิฐโปร่ง', cap_above=True)
    image(fig, ov, 'CAM_2_Garden_East.png', 265, 16, 245, 150, 'จากมุมสวนทิศตะวันออกเฉียงเหนือ — ทรงกระบอกอิฐริมสระ', cap_above=True)
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
    pdf = os.path.join(OUT, 'WELL-GBEACH-30x30-drawings.pdf')
    with PdfPages(pdf) as pp:
        for f in pages:
            pp.savefig(f)
    if '--png' in sys.argv:
        for i, f in enumerate(pages):
            f.savefig('/tmp/well/gb4/sheet_%02d.png' % (i + 1), dpi=60)
    for f in pages: plt.close(f)
    print('pdf', pdf, len(pages))
    if '--dxf' in sys.argv:
        build_dxf(os.path.join(OUT, 'WELL-GBEACH-30x30-CAD.dxf'))
        print('dxf ok')
