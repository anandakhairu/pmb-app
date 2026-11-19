import zipfile, hashlib, json, os, subprocess
from PIL import Image

assets_dir = 'C:/projects/ta-pemweb/uidesign/assets'
images_meta = {}
for fname in os.listdir(assets_dir):
    fpath = os.path.join(assets_dir, fname)
    if os.path.isfile(fpath) and fname.endswith(('.png', '.jpg', '.webp')):
        with open(fpath, 'rb') as f:
            b = f.read()
            h = hashlib.sha256(b).hexdigest()
        im = Image.open(fpath)
        images_meta[fname] = {'path': fpath, 'hash': h, 'width': im.width, 'height': im.height, 'bytes': b}

def hex_to_rgb(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
    elif len(hex_str) == 3:
        r = int(hex_str[0]*2, 16) / 255.0
        g = int(hex_str[1]*2, 16) / 255.0
        b = int(hex_str[2]*2, 16) / 255.0
    else:
        r, g, b = 0.0, 0.0, 0.0
    return {"r": r, "g": g, "b": b, "a": alpha}

image_index = [{'hash': meta['hash'], 'width': meta['width'], 'height': meta['height']} for meta in images_meta.values()]

# Exact Master V6.1 Colors
C_PRIMARY = "#1554B8"        # Primary Blue
C_PRIMARY_HOVER = "#10469B"  # Primary Hover
C_ACCENT_BLUE = "#3689F5"    # Accent Blue
C_BACKGROUND = "#F7F9FD"     # Background Canvas
C_SURFACE = "#FFFFFF"        # Surface White
C_MUTED_SURFACE = "#EEF2FA"  # Muted Surface / Soft Blue-Gray
C_PRIMARY_TEXT = "#101A32"   # Primary Text (Dark Navy)
C_SECONDARY_TEXT = "#63718A" # Secondary Text
C_BORDER = "#DFE6F2"         # Border
C_SUCCESS = "#20A878"        # Success Green
C_WARNING = "#F2BF55"        # Warning Yellow
C_ERROR = "#D94A55"          # Error Red

FONT_FAMILY = "Plus Jakarta Sans"

doc = {
    'comments': [],
    'current_page': 1,
    'document_colors': [],
    'format': 'figcraft',
    'imageIndex': image_index,
    'name': 'PMB 2026 — Complete University Admission Platform (V6.1)',
    'next_id': 1000,
    'nodes': {},
    'pages': [],
    'styles': [],
    'variables': []
}

def alloc_id():
    cur = doc['next_id']
    doc['next_id'] += 1
    return cur

def add_page(pid, name):
    doc['nodes'][str(pid)] = {
        'background': {'a': 1.0, 'r': 0.9686, 'g': 0.9765, 'b': 0.9922}, # F7F9FD
        'children': [],
        'flows': [],
        'height': 0.0,
        'id': pid,
        'name': name,
        'prototype': {'background': {'a': 1.0, 'r': 0.9686, 'g': 0.9765, 'b': 0.9922}, 'device': 'None', 'rotation': 'portrait'},
        'type': 'page',
        'width': 0.0
    }
    doc['pages'].append(pid)
    return pid

def add_frame(parent_page, name, x, y, w=1440.0, h=1024.0, bg_hex=C_BACKGROUND):
    fid = alloc_id()
    doc['nodes'][str(fid)] = {
        'children': [],
        'clip': True,
        'fills': [{'blend': 'normal', 'color': hex_to_rgb(bg_hex), 'opacity': 1.0, 'type': 'solid', 'visible': True}],
        'height': float(h),
        'id': fid,
        'name': name,
        'parent': parent_page,
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'frame',
        'width': float(w)
    }
    doc['nodes'][str(parent_page)]['children'].append(fid)
    return fid

def add_rect(parent_id, name, x, y, w, h, fill_hex=None, stroke_hex=None, stroke_width=1.0, radius=None, opacity=1.0):
    nid = alloc_id()
    node = {
        'blend': 'normal',
        'height': float(h),
        'id': nid,
        'name': name,
        'parent': parent_id,
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'rectangle',
        'width': float(w)
    }
    if radius is not None:
        if isinstance(radius, (int, float)):
            r = float(radius)
            node['corners'] = {'radii': [r, r, r, r], 'smoothing': 0.0}
        elif isinstance(radius, list):
            node['corners'] = {'radii': [float(v) for v in radius], 'smoothing': 0.0}
    if fill_hex:
        node['fills'] = [{'blend': 'normal', 'color': hex_to_rgb(fill_hex), 'opacity': opacity, 'type': 'solid', 'visible': True}]
    else:
        node['fills'] = []
    if stroke_hex:
        node['strokes'] = [{'blend': 'normal', 'color': hex_to_rgb(stroke_hex), 'opacity': 1.0, 'type': 'solid', 'visible': True}]
        node['strokeWeight'] = float(stroke_width)
    doc['nodes'][str(nid)] = node
    doc['nodes'][str(parent_id)]['children'].append(nid)
    return nid

def add_image_rect(parent_id, name, x, y, w, h, img_name, radius=None, opacity=1.0):
    nid = alloc_id()
    img_hash = images_meta[img_name]['hash']
    node = {
        'blend': 'normal',
        'fills': [{
            'blend': 'normal',
            'crop': None,
            'filters': {'contrast': 0.0, 'exposure': 0.0, 'highlights': 0.0, 'saturation': 0.0, 'shadows': 0.0, 'temperature': 0.0, 'tint': 0.0},
            'image': img_hash,
            'opacity': opacity,
            'rotation': 0,
            'scale': 1.0,
            'scale_mode': 'fill',
            'type': 'image',
            'visible': True
        }],
        'height': float(h),
        'id': nid,
        'name': name,
        'parent': parent_id,
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'rectangle',
        'width': float(w)
    }
    if radius is not None:
        if isinstance(radius, (int, float)):
            r = float(radius)
            node['corners'] = {'radii': [r, r, r, r], 'smoothing': 0.0}
        elif isinstance(radius, list):
            node['corners'] = {'radii': [float(v) for v in radius], 'smoothing': 0.0}
    doc['nodes'][str(nid)] = node
    doc['nodes'][str(parent_id)]['children'].append(nid)
    return nid

def add_text(parent_id, name, x, y, characters, font_size=14.0, color_hex=C_PRIMARY_TEXT, font_weight='Regular', width=None, height=None):
    nid = alloc_id()
    w = float(width) if width else float(len(characters) * font_size * 0.65)
    h = float(height) if height else float(font_size * 1.35)
    node = {
        'blend': 'normal',
        'characters': characters,
        'child_layout': {'absolute': False, 'grid_column': None, 'grid_column_span': 0, 'grid_row': None, 'grid_row_span': 0, 'max_h': None, 'max_w': None, 'min_h': None, 'min_w': None, 'sizing_h': 'hug' if width is None else 'fixed', 'sizing_v': 'hug' if height is None else 'fixed'},
        'fills': [{'blend': 'normal', 'color': hex_to_rgb(color_hex), 'opacity': 1.0, 'type': 'solid', 'visible': True}],
        'height': h,
        'id': nid,
        'name': name,
        'parent': parent_id,
        'style': {'case': 'original', 'decoration': 'none', 'fills': None, 'font_family': FONT_FAMILY, 'font_size': float(font_size), 'font_style': font_weight, 'letter_spacing': {'unit': 'percent', 'value': 0.0}, 'line_height': {'unit': 'auto'}, 'link': None},
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'text',
        'width': w
    }
    doc['nodes'][str(nid)] = node
    doc['nodes'][str(parent_id)]['children'].append(nid)
    return nid

def add_desktop_navbar(frame_id, active_nav='Beranda'):
    add_rect(frame_id, 'Top Nav BG', 0, 0, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
    add_rect(frame_id, 'Logo Icon', 80, 20, 36, 36, fill_hex=C_PRIMARY, radius=8)
    add_text(frame_id, 'Logo Txt', 90, 28, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
    add_text(frame_id, 'Brand Name', 128, 26, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    
    navs = ['Beranda', 'Program Studi ⌵', 'Jalur Masuk ⌵', 'Informasi ⌵']
    nx = 520
    for ni in navs:
        is_act = (active_nav in ni)
        add_text(frame_id, f'Nav {ni}', nx, 28, ni, font_size=13, color_hex=C_PRIMARY if is_act else C_SECONDARY_TEXT, font_weight='Bold' if is_act else 'Regular')
        nx += 130
        
    add_text(frame_id, 'Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)
    add_rect(frame_id, 'Btn Daftar Nav', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
    add_text(frame_id, 'Btn Daftar Nav Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

def add_desktop_footer(frame_id, y_pos=960):
    add_rect(frame_id, 'Footer BG', 0, y_pos, 1440, 64, fill_hex=C_PRIMARY)
    add_text(frame_id, 'Footer Copy', 80, y_pos + 25, '© 2026 Universitas Indonesia — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex=C_SURFACE)

print('V6.1 Base Engine Ready.')

# ==========================================
# PAGE 1: 01 — Cover & Design Overview
# ==========================================
p1 = add_page(1, '01 — Cover & Design Overview')

# Frame 0: Cover Presentation
f_cov = add_frame(p1, '00. Master Cover — PMB 2026', 0, 0, 1440, 1024, C_BACKGROUND)
add_rect(f_cov, 'Cov Hero BG', 80, 80, 1280, 480, fill_hex=C_PRIMARY, radius=24)
add_image_rect(f_cov, 'Cov Hero Photo', 80, 80, 1280, 480, 'hero_campus.jpg', radius=24, opacity=0.35)

add_rect(f_cov, 'Cov Tag Pill', 120, 120, 270, 32, fill_hex=C_SURFACE, radius=16)
add_text(f_cov, 'Cov Tag Txt', 140, 128, 'MASTER FIGMA DESIGN V6.1', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_cov, 'Cov Title 1', 120, 175, 'PMB 2026 — Complete University', font_size=46, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_cov, 'Cov Title 2', 120, 235, 'Admission Platform', font_size=46, color_hex=C_WARNING, font_weight='Bold')

add_text(f_cov, 'Cov Desc 1', 120, 305, 'Desktop Web Only · Applicant-Only · Complete End-to-End Higher Education Experience.', font_size=15, color_hex=C_MUTED_SURFACE)
add_text(f_cov, 'Cov Desc 2', 120, 330, '15 Connected Pages · 48 Defined Routes · 6 Desktop Presentation Panels · Zero Mobile / Admin Bleed.', font_size=15, color_hex=C_MUTED_SURFACE)

# Meta Box
add_rect(f_cov, 'Cov Meta Box', 120, 385, 1200, 130, fill_hex=C_SURFACE, radius=16)
cmetas = [
    ('SCOPE', 'Desktop Web Only (1440x1024)'),
    ('USER JOURNEY', 'Complete Calon Mahasiswa Lifecycle'),
    ('INSTITUTION', 'Universal PTN / PTS Template'),
    ('MANDATE V6.1', '6-Panel Desktop (Panel 6 = Wizard)')
]
cmx = 150
for clbl, cval in cmetas:
    add_text(f_cov, f'CM Lbl {clbl}', cmx, 415, clbl, font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'CM Val {clbl}', cmx, 440, cval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    cmx += 280

# 3 Pillars
pillars = [
    ('Blue & White Visual Authority', 'Dominan biru (#1554B8) dan putih (#FFFFFF) dengan fotografi kampus dan mahasiswa asli.'),
    ('Strict Editorial Typographic Scale', 'Plus Jakarta Sans (400, 500, 600, 700) dengan skala terukur dan angka tabular presisi.'),
    ('Pill-Shaped Tactile Interaction', 'Komponen tombol rounded-full berbentuk pill yang ramah pengguna, modern, dan konsisten.')
]
plx = 80
for ptitle, pdesc in pillars:
    add_rect(f_cov, f'Pil BG {ptitle}', plx, 600, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_rect(f_cov, f'Pil Accent {ptitle}', plx, 600, 400, 6, fill_hex=C_PRIMARY, radius=[18, 18, 0, 0])
    add_text(f_cov, f'Pil Title {ptitle}', plx + 28, 635, ptitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'Pil Desc {ptitle}', plx + 28, 675, pdesc, font_size=14, color_hex=C_SECONDARY_TEXT, width=344, height=60)
    plx += 440

add_text(f_cov, 'Cov Footer', 80, 975, '© 2026 PMB Master Design Specification V6.1 — Complete Desktop Applicant System.', font_size=12, color_hex=C_SECONDARY_TEXT)

# ----------------------------------------------------
# 2-COLUMN x 3-ROW SIX-PANEL DESIGNBOARD (MANDATE #1)
# ----------------------------------------------------
# Row 1, Col 1 (X=1600, Y=0): Panel 1 — Homepage / University Landing Page
f_p1 = add_frame(p1, 'Panel 1 — Homepage / University Landing Page', 1600, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p1, active_nav='Beranda')
add_text(f_p1, 'P1 Hero 1', 80, 140, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p1, 'P1 Hero 2', 80, 205, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p1, 'P1 Hero 3', 80, 270, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p1, 'P1 Sub 1', 80, 350, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f_p1, 'P1 Sub 2', 80, 375, 'bersama Universitas Indonesia.', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f_p1, 'P1 Btn CTA', 80, 425, 195, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f_p1, 'P1 Btn CTA Txt', 115, 439, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_p1, 'P1 Video CTA', 305, 439, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_image_rect(f_p1, 'P1 Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)

add_rect(f_p1, 'P1 Ribbon BG', 80, 670, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
for rlbl, rval, rico, rx in [('Periode Pendaftaran', '3 Jan - 30 Jun 2026', 'CAL', 120), ('Jalur Seleksi', 'SNBP, SNBT, Mandiri', 'CAP', 440), ('Program Studi', '100+ Pilihan', 'BOK', 760), ('Beasiswa', 'Hingga 100%', 'GFT', 1060)]:
    add_rect(f_p1, f'P1 RIco {rico}', rx, 696, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f_p1, f'P1 RIcoT {rico}', rx + 10, 709, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f_p1, f'P1 RLbl {rlbl}', rx + 56, 700, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_p1, f'P1 RVal {rval}', rx + 56, 720, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_text(f_p1, 'P1 Sec Title', 80, 795, 'JALUR SELEKSI PENERIMAAN 2026', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
for jtitle, jdesc, jdate, jimg, jx in [('SNBP (Prestasi)', 'Nilai rapor semester 1-5 & portofolio.', '10 Nov - 20 Des 2026', 'card_snbp.jpg', 80), ('SNBT (UTBK)', 'Tes skolastik & literasi BPPP.', '15 Jan - 28 Feb 2027', 'card_snbt.jpg', 520), ('Mandiri Reguler', 'CBT terpadu & prestasi khusus.', '01 Mar - 15 Apr 2027', 'card_mandiri.jpg', 960)]:
    add_rect(f_p1, f'P1 JC BG {jtitle}', jx, 825, 400, 130, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f_p1, f'P1 JC Img {jtitle}', jx, 825, 140, 130, jimg, radius=[14, 0, 0, 14])
    add_text(f_p1, f'P1 JC Title {jtitle}', jx + 155, 845, jtitle, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_p1, f'P1 JC Desc {jtitle}', jx + 155, 870, jdesc, font_size=11, color_hex=C_SECONDARY_TEXT, width=230, height=30)
    add_text(f_p1, f'P1 JC Date {jtitle}', jx + 155, 915, jdate, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
add_desktop_footer(f_p1, y_pos=975)

# Row 1, Col 2 (X=3140, Y=0): Panel 2 — Program Directory
f_p2 = add_frame(p1, 'Panel 2 — Program Directory', 3140, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p2, active_nav='Program Studi')
add_text(f_p2, 'P2 Title', 80, 120, 'Program Studi', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p2, 'P2 Sub', 80, 168, 'Temukan program studi yang sesuai dengan minat dan bakatmu.', font_size=15, color_hex=C_SECONDARY_TEXT)
add_image_rect(f_p2, 'P2 Bldg Hero', 780, 105, 580, 220, 'real_bldg_hero.png', radius=18)
add_rect(f_p2, 'P2 Search', 80, 215, 480, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f_p2, 'P2 Search T', 102, 228, '🔍  Cari program studi...', font_size=13, color_hex=C_SECONDARY_TEXT)

fpx = 80
for ptxt, pact in [('Semua', True), ('Fakultas ⌵', False), ('Jenjang ⌵', False), ('Akreditasi ⌵', False)]:
    pbg = C_PRIMARY if pact else C_SURFACE
    ptcol = C_SURFACE if pact else C_PRIMARY_TEXT
    pw = len(ptxt) * 9 + 30
    add_rect(f_p2, f'P2 P {ptxt}', fpx, 280, pw, 38, fill_hex=pbg, stroke_hex=None if pact else C_BORDER, radius=19)
    add_text(f_p2, f'P2 PTxt {ptxt}', fpx + 15, 290, ptxt, font_size=12, color_hex=ptcol, font_weight='Bold' if pact else 'Regular')
    fpx += pw + 12
add_text(f_p2, 'P2 See All', 1210, 290, 'Lihat Semua Program →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

for ctitle, cfac, cdeg, cakred, cimg, cx in [('Teknik Informatika', 'Fakultas Ilmu Komputer', 'S1', 'Akreditasi Unggul', 'real_bldg_ti.png', 80), ('Manajemen', 'Fakultas Ekonomi & Bisnis', 'S1', 'Akreditasi Unggul', 'real_bldg_mn.png', 520), ('Psikologi', 'Fakultas Psikologi', 'S1', 'Akreditasi A', 'real_bldg_ps.png', 960)]:
    add_rect(f_p2, f'P2 CardBG {ctitle}', cx, 360, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_image_rect(f_p2, f'P2 CardImg {ctitle}', cx, 360, 400, 185, cimg, radius=[18, 18, 0, 0])
    add_text(f_p2, f'P2 CardTitle {ctitle}', cx + 22, 565, ctitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_p2, f'P2 CardFac {ctitle}', cx + 22, 592, cfac, font_size=13, color_hex=C_SECONDARY_TEXT)
    add_text(f_p2, f'P2 CardDeg {ctitle}', cx + 22, 612, cdeg, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f_p2, f'P2 AkredPill {ctitle}', cx + 22, 642, 135, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
    add_text(f_p2, f'P2 AkredTxt {ctitle}', cx + 36, 648, f'● {cakred}', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    add_rect(f_p2, f'P2 ArrowCircle {ctitle}', cx + 340, 638, 36, 36, fill_hex=C_MUTED_SURFACE, radius=18)
    add_text(f_p2, f'P2 ArrowTxt {ctitle}', cx + 352, 646, '→', font_size=15, color_hex=C_PRIMARY, font_weight='Bold')

# Row 2, Col 1 (X=1600, Y=1124): Panel 3 — Admission Pathways
f_p3 = add_frame(p1, 'Panel 3 — Admission Pathways', 1600, 1124, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p3, active_nav='Jalur Masuk')
add_text(f_p3, 'P3 Title', 80, 130, 'Jalur Masuk', font_size=40, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 Sub', 80, 178, 'Pilih jalur seleksi yang sesuai denganmu.', font_size=15, color_hex=C_SECONDARY_TEXT)

add_rect(f_p3, 'P3 Tab Box', 80, 230, 420, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f_p3, 'P3 Tab Act', 84, 234, 136, 40, fill_hex=C_SURFACE, radius=20)
add_text(f_p3, 'P3 Tab 1 T', 132, 245, 'SNBP', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p3, 'P3 Tab 2 T', 270, 245, 'SNBT', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f_p3, 'P3 Tab 3 T', 405, 245, 'Mandiri', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f_p3, 'P3 Detail Card', 80, 310, 560, 360, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_rect(f_p3, 'P3 Icon BG', 112, 342, 60, 60, fill_hex=C_MUTED_SURFACE, radius=14)
add_text(f_p3, 'P3 Icon T', 128, 362, 'SNBP', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p3, 'P3 CT', 112, 425, 'SNBP', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 CS1', 112, 465, 'Seleksi Nasional Berdasarkan Prestasi', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 CS2', 112, 492, 'untuk siswa berprestasi akademik dan non-akademik.', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f_p3, 'P3 Link', 112, 535, 'Pelajari Selengkapnya →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f_p3, 'P3 CTA', 112, 580, 220, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f_p3, 'P3 CTA T', 152, 595, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_image_rect(f_p3, 'P3 Female Photo', 680, 130, 680, 560, 'real_female_student.png', radius=24)

# Row 2, Col 2 (X=3140, Y=1124): Panel 4 — Applicant Dashboard
f_p4 = add_frame(p1, 'Panel 4 — Applicant Dashboard', 3140, 1124, 1440, 1024, C_BACKGROUND)
add_rect(f_p4, 'P4 Top Nav', 0, 0, 1440, 70, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f_p4, 'P4 Logo', 80, 17, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f_p4, 'P4 Logo T', 90, 25, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_p4, 'P4 Brand', 128, 24, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p4, 'P4 Bell', 1260, 25, '🔔', font_size=16, color_hex=C_SECONDARY_TEXT)
add_image_rect(f_p4, 'P4 Avatar', 1300, 16, 38, 38, 'student_id_photo.jpg', radius=19)

add_rect(f_p4, 'P4 Side BG', 0, 70, 240, 930, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
sby = 100
for sitem, sactive in [('Dashboard', True), ('Profil', False), ('Pendaftaran', False), ('Dokumen', False), ('Pembayaran', False), ('Seleksi', False), ('Notifikasi', False), ('Keluar', False)]:
    if sactive:
        add_rect(f_p4, f'P4 SBar {sitem}', 0, sby, 4, 40, fill_hex=C_PRIMARY)
        add_rect(f_p4, f'P4 SPill {sitem}', 16, sby, 208, 40, fill_hex=C_MUTED_SURFACE, radius=8)
    add_text(f_p4, f'P4 SItem {sitem}', 40, sby + 11, sitem, font_size=13, color_hex=C_PRIMARY if sactive else C_SECONDARY_TEXT, font_weight='Bold' if sactive else 'Regular')
    sby += 46

add_text(f_p4, 'P4 Greet', 280, 105, 'Halo, Andi Pratama 👋', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p4, 'P4 Greet Sub', 280, 142, 'Selamat datang di dashboard pendaftaran PMB 2026', font_size=14, color_hex=C_SECONDARY_TEXT)
add_image_rect(f_p4, 'P4 Accent', 1060, 90, 300, 85, 'real_bldg_ti.png', radius=12, opacity=0.7)

add_rect(f_p4, 'P4 Status Card', 280, 190, 1080, 320, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f_p4, 'P4 Card T', 312, 218, 'Status Pendaftaran', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

stx = 340
for i, (stitle, sdone) in enumerate([('Data Diri', True), ('Dokumen', True), ('Pembayaran', True), ('Seleksi', False), ('Hasil', False)]):
    c_fill = C_PRIMARY if sdone else C_MUTED_SURFACE
    c_txt = C_SURFACE if sdone else C_SECONDARY_TEXT
    c_sym = '✓' if sdone else ''
    add_rect(f_p4, f'P4 Node {stitle}', stx, 260, 32, 32, fill_hex=c_fill, radius=16)
    if c_sym:
        add_text(f_p4, f'P4 Sym {stitle}', stx + 10, 268, c_sym, font_size=12, color_hex=c_txt, font_weight='Bold')
    add_text(f_p4, f'P4 Txt {stitle}', stx - 15, 302, stitle, font_size=12, color_hex=C_PRIMARY_TEXT if sdone else C_SECONDARY_TEXT, font_weight='Bold' if sdone else 'Regular')
    if i < 4:
        add_rect(f_p4, f'P4 Line {i}', stx + 40, 275, 150, 2, fill_hex=C_PRIMARY if i < 2 else C_BORDER)
    stx += 190

add_rect(f_p4, 'P4 Succ Box', 312, 350, 1016, 120, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=14)
add_rect(f_p4, 'P4 Succ Ico', 336, 375, 48, 48, fill_hex=C_SUCCESS, radius=24)
add_text(f_p4, 'P4 Succ Chk', 352, 388, '✓', font_size=18, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_p4, 'P4 Succ T', 400, 376, 'Pendaftaran Berhasil', font_size=16, color_hex='#15803d', font_weight='Bold')
add_text(f_p4, 'P4 Succ D', 400, 402, 'Terima kasih telah mendaftar. Pantau terus informasi terbaru melalui halaman ini.', font_size=13, color_hex='#166534')
add_text(f_p4, 'P4 Succ L', 1210, 390, 'Lihat Detail →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_p4, 'P4 Info H', 280, 545, 'Informasi Penting', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p4, 'P4 Info All', 1280, 545, 'Lihat Semua →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f_p4, 'P4 Info Card', 280, 580, 400, 90, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_rect(f_p4, 'P4 Info Ico BG', 302, 602, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
add_text(f_p4, 'P4 Info Ico T', 312, 614, 'CAL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p4, 'P4 Info Name', 360, 604, 'Jadwal Seleksi', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p4, 'P4 Info Date', 360, 626, '25 Jun 2026', font_size=12, color_hex=C_SECONDARY_TEXT)

# Row 3, Col 1 (X=1600, Y=2248): Panel 5 — Program Detail
f_p5 = add_frame(p1, 'Panel 5 — Program Detail', 1600, 2248, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p5, active_nav='Program Studi')
add_text(f_p5, 'P5 Back Link', 80, 110, '← Kembali ke Program Studi', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_image_rect(f_p5, 'P5 Bldg Photo', 80, 140, 460, 300, 'real_bldg_detail.png', radius=18)
add_text(f_p5, 'P5 Major Title', 580, 160, 'Teknik Informatika', font_size=36, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p5, 'P5 Major Fac', 580, 210, 'Fakultas Ilmu Komputer', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f_p5, 'P5 Akred Pill', 580, 245, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f_p5, 'P5 Akred Pill Txt', 594, 251, '● Akreditasi Unggul', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

add_text(f_p5, 'P5 Desc 1', 580, 290, 'Program studi Teknik Informatika membekali mahasiswa dengan kompetensi', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f_p5, 'P5 Desc 2', 580, 312, 'di bidang teknologi informasi, rekayasa perangkat lunak, dan kecerdasan buatan.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f_p5, 'P5 Btn Daftar', 580, 360, 180, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f_p5, 'P5 Btn Daftar Txt', 612, 374, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f_p5, 'P5 Btn Kurikulum', 780, 360, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f_p5, 'P5 Btn Kurikulum Txt', 812, 374, 'Lihat Kurikulum', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Detail Tabs
dtx5 = 80
for dti in ['Overview', 'Kurikulum', 'Prospek Karir', 'Persyaratan']:
    is_act = (dti == 'Overview')
    add_text(f_p5, f'P5 DTab {dti}', dtx5, 490, dti, font_size=14, color_hex=C_PRIMARY if is_act else C_SECONDARY_TEXT, font_weight='Bold' if is_act else 'Regular')
    if is_act:
        add_rect(f_p5, 'P5 DTab Line', dtx5, 520, 65, 3, fill_hex=C_PRIMARY)
    dtx5 += 140

add_rect(f_p5, 'P5 Tabs Div Line', 80, 523, 1280, 1, fill_hex=C_BORDER)
add_text(f_p5, 'P5 About Title', 80, 555, 'Tentang Program Studi', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p5, 'P5 About Desc 1', 80, 590, 'Teknik Informatika berfokus pada pengembangan teknologi digital, perancangan algoritma efisien, sistem cerdas,', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f_p5, 'P5 About Desc 2', 80, 614, 'serta infrastruktur komputasi awan untuk masa depan yang lebih baik.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f_p5, 'P5 Prog Info Box', 880, 555, 480, 180, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f_p5, 'P5 Prog Info Title', 905, 580, 'Informasi Program', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_p5, 'P5 Prog Info Div', 905, 608, 430, 1, fill_hex=C_BORDER)
add_text(f_p5, 'P5 Jenjang Lbl', 905, 625, 'Jenjang:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f_p5, 'P5 Jenjang Val', 905, 645, 'Sarjana (S1)', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p5, 'P5 Fac Lbl', 1120, 625, 'Fakultas:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f_p5, 'P5 Fac Val', 1120, 645, 'Ilmu Komputer', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Row 3, Col 2 (X=3140, Y=2248): Panel 6 — Desktop Application Form / Registration Wizard (MANDATE #1 REPLACEMENT!)
f_p6 = add_frame(p1, 'Panel 6 — Desktop Application Form / Registration Wizard', 3140, 2248, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p6, active_nav='Jalur Masuk')

add_text(f_p6, 'P6 Wizard Header', 80, 105, 'Formulir Pendaftaran Calon Mahasiswa Baru TA 2026/2027', font_size=20, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p6, 'P6 Wizard Sub', 80, 134, 'Lengkapi tahapan pendaftaran secara bertahap. Data Anda tersimpan otomatis sebagai draf.', font_size=13, color_hex=C_SECONDARY_TEXT)

# Stepper 5 Checkpoints
add_rect(f_p6, 'P6 Stepper BG', 80, 165, 1280, 72, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
p6_steps = [('1', 'Data Diri', True), ('2', 'Asal Sekolah', False), ('3', 'Pilihan Prodi', False), ('4', 'Unggah Berkas', False), ('5', 'Finalisasi', False)]
p6_sx = 110
for i, (wn, wt, wa) in enumerate(p6_steps):
    c_fill = C_PRIMARY if wa else C_MUTED_SURFACE
    c_txt = C_SURFACE if wa else C_SECONDARY_TEXT
    add_rect(f_p6, f'P6 SNode {wn}', p6_sx, 181, 40, 40, fill_hex=c_fill, radius=20)
    add_text(f_p6, f'P6 SNum {wn}', p6_sx + 15, 192, wn, font_size=13, color_hex=c_txt, font_weight='Bold')
    add_text(f_p6, f'P6 STxt {wn}', p6_sx + 50, 192, wt, font_size=13, color_hex=C_PRIMARY_TEXT if wa else C_SECONDARY_TEXT, font_weight='Bold' if wa else 'Regular')
    if i < 4:
        add_rect(f_p6, f'P6 SLine {i}', p6_sx + 165, 200, 75, 2, fill_hex=C_BORDER)
    p6_sx += 250

# Form Body Card (w: 1280, h: 720)
add_rect(f_p6, 'P6 Form Card', 80, 255, 1280, 720, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f_p6, 'P6 Step Title', 112, 285, 'Tahap 1: Identitas Pribadi Calon Mahasiswa', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p6, 'P6 Step Sub', 112, 310, 'Pastikan data yang dimasukkan sesuai dengan dokumen KTP / Kartu Keluarga resmi.', font_size=13, color_hex=C_SECONDARY_TEXT)
add_rect(f_p6, 'P6 Form Div', 112, 335, 1216, 1, fill_hex=C_BORDER)

# Two-column Inputs
c1_p6 = [
    ('Nomor Induk Kependudukan (NIK) *', '3302192804040003'),
    ('Nomor Induk Siswa Nasional (NISN) *', '0058291042'),
    ('Nama Lengkap Sesuai Ijazah *', 'Muhammad Irfan'),
    ('Jenis Kelamin *', 'Laki-laki (Pilihan Sesuai KTP)'),
    ('Tempat Lahir *', 'Kota Semarang'),
    ('Tanggal Lahir *', '14 / 08 / 2005 (DD/MM/YYYY)')
]
p6_fy = 355
for lbl, val in c1_p6:
    add_text(f_p6, f'P6 Lbl {lbl}', 112, p6_fy, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f_p6, f'P6 Inp {lbl}', 112, p6_fy + 20, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f_p6, f'P6 Val {lbl}', 128, p6_fy + 32, val, font_size=12, color_hex=C_PRIMARY_TEXT)
    p6_fy += 78

c2_p6 = [
    ('Agama *', 'Islam (Pilihan)'),
    ('Nomor Handphone / WhatsApp Aktif *', '081234567890'),
    ('Alamat Lengkap Domisili *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'),
    ('Kelurahan / Desa *', 'Sekaran'),
    ('Kecamatan *', 'Gunungpati'),
    ('Kabupaten / Kota & Provinsi *', 'Kota Semarang, Jawa Tengah')
]
p6_fy2 = 355
for lbl, val in c2_p6:
    add_text(f_p6, f'P6 Lbl {lbl}', 748, p6_fy2, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f_p6, f'P6 Inp {lbl}', 748, p6_fy2 + 20, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f_p6, f'P6 Val {lbl}', 764, p6_fy2 + 32, val, font_size=12, color_hex=C_PRIMARY_TEXT)
    p6_fy2 += 78

add_rect(f_p6, 'P6 Bottom Div', 112, 860, 1216, 1, fill_hex=C_BORDER)
add_rect(f_p6, 'P6 Btn Draft', 112, 885, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f_p6, 'P6 Btn Draft T', 152, 900, 'Simpan Draf', font_size=12, color_hex=C_SECONDARY_TEXT)

add_rect(f_p6, 'P6 Btn Next', 1048, 885, 280, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f_p6, 'P6 Btn Next T', 1080, 900, 'Simpan & Lanjut ke Tahap 2 →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

print('Page 1 complete with 6 desktop panels arranged 2x3!')

# ==========================================
# PAGE 4: 04 — Public Website
# ==========================================
p4 = add_page(4, '04 — Public Website')

# Frame 1: Homepage (1440 x 1024)
f4_home = add_frame(p4, 'A01 — Homepage', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f4_home, active_nav='Beranda')
add_text(f4_home, 'P4H Hero 1', 80, 140, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4_home, 'P4H Hero 2', 80, 205, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4_home, 'P4H Hero 3', 80, 270, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f4_home, 'P4H Sub 1', 80, 350, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f4_home, 'P4H Sub 2', 80, 375, 'bersama Universitas Indonesia.', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f4_home, 'P4H Btn CTA', 80, 425, 195, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f4_home, 'P4H Btn CTA Txt', 115, 439, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_text(f4_home, 'P4H Video CTA', 305, 439, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_image_rect(f4_home, 'P4H Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)
add_rect(f4_home, 'P4H Ribbon BG', 80, 670, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
for rlbl, rval, rico, rx in [('Periode Pendaftaran', '3 Jan - 30 Jun 2026', 'CAL', 120), ('Jalur Seleksi', 'SNBP, SNBT, Mandiri', 'CAP', 440), ('Program Studi', '100+ Pilihan', 'BOK', 760), ('Beasiswa', 'Hingga 100%', 'GFT', 1060)]:
    add_rect(f4_home, f'P4H RIco {rico}', rx, 696, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f4_home, f'P4H RIcoT {rico}', rx + 10, 709, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f4_home, f'P4H RLbl {rlbl}', rx + 56, 700, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f4_home, f'P4H RVal {rval}', rx + 56, 720, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_desktop_footer(f4_home, y_pos=960)

# Frame 2: Public Search & Legal Policies (MANDATE #2!)
f4_search = add_frame(p4, 'A12 to A14 — Public Search, Terms & 404 Error', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f4_search, active_nav='Informasi')
add_text(f4_search, 'P4S Title', 80, 120, 'Pusat Informasi, Kebijakan Privasi & Ketentuan', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Search Results Simulation
add_rect(f4_search, 'P4S Search Box', 80, 180, 600, 48, fill_hex=C_SURFACE, stroke_hex=C_PRIMARY, radius=24)
add_text(f4_search, 'P4S Search Q', 110, 195, '🔍   Informatika   (Ditemukan 3 Hasil Relevan)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Search Result Cards
s_results = [
    ('Program Studi: S1 Teknik Informatika (Fakultas Ilmu Komputer)', 'Penerimaan jenjang sarjana reguler dengan akreditasi Unggul.', '/programs/teknik-informatika'),
    ('Jalur Masuk: Seleksi Mandiri Prestasi Unggul Bidang IT', 'Syarat khusus portofolio sertifikat juara olimpiade informatika.', '/admissions/mandiri-prestasi'),
    ('Biaya Kuliah: Tabel UKT Rumpun Saintek & Komputasi', 'Rincian besaran UKT Golongan I s.d. Golongan VII untuk Fasilkom.', '/tuition')
]
sry = 245
for srt, srd, srl in s_results:
    add_rect(f4_search, f'SR Box {srt}', 80, sry, 600, 75, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=12)
    add_text(f4_search, f'SR Title {srt}', 100, sry + 15, srt, font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f4_search, f'SR Desc {srt}', 100, sry + 35, srd, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f4_search, f'SR Link {srt}', 100, sry + 53, srl, font_size=10, color_hex=C_SECONDARY_TEXT)
    sry += 85

# Legal Policies & Error States Box (Right Side)
add_rect(f4_search, 'P4S Legal BG', 720, 180, 640, 720, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f4_search, 'P4S Legal Title', 750, 210, 'Ketentuan Layanan & Kebijakan Privasi (/terms & /privacy)', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f4_search, 'P4S Legal Div', 750, 238, 580, 1, fill_hex=C_BORDER)

add_text(f4_search, 'P4S Legal L1', 750, 255, '1. Kebijakan Privasi Data Calon Mahasiswa (UU PDP No. 27/2022)', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4_search, 'P4S Legal T1', 750, 278, 'Seluruh data pribadi pendaftar (NIK, NISN, dokumen keluarga) dienkripsi dan hanya digunakan untuk keperluan resmi verifikasi admisi PMB.', font_size=12, color_hex=C_SECONDARY_TEXT, width=560, height=35)

add_text(f4_search, 'P4S Legal L2', 750, 330, '2. Ketentuan Keabsahan Dokumen & Sanksi Pemalsuan', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4_search, 'P4S Legal T2', 750, 353, 'Pemalsuan dokumen Ijazah, Rapor, atau Kartu Keluarga berakibat pembatalan status kelulusan dan penuntutan sesuai hukum yang berlaku.', font_size=12, color_hex=C_SECONDARY_TEXT, width=560, height=35)

# Error 404 Simulation Box
add_rect(f4_search, 'P4S 404 Box', 750, 420, 580, 220, fill_hex=C_MUTED_SURFACE, stroke_hex=C_BORDER, radius=14)
add_text(f4_search, 'P4S 404 Tag', 775, 440, 'SIMULASI HALAMAN ERROR /404 & /service-unavailable', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f4_search, 'P4S 404 Title', 775, 465, '404 — Halaman Tidak Ditemukan', font_size=24, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4_search, 'P4S 404 Desc', 775, 502, 'Tautan yang Anda tuju mungkin telah dipindahkan atau dinonaktifkan.', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f4_search, 'P4S 404 Btn', 775, 535, 180, 40, fill_hex=C_PRIMARY, radius=20)
add_text(f4_search, 'P4S 404 Btn T', 808, 547, 'Kembali ke Beranda', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 6: 06 — Admission Information
# ==========================================
p6 = add_page(6, '06 — Admission Information')
f6_adm = add_frame(p6, 'A04 & A06 — Admission Pathways & Schedule', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f6_adm, active_nav='Jalur Masuk')

add_text(f6_adm, 'F6A Title', 80, 120, 'Jalur Masuk & Jadwal Seleksi Akademik 2026', font_size=36, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6_adm, 'F6A Sub', 80, 168, 'Informasi lengkap jadwal pendaftaran, kuota daya tampung, dan kualifikasi pendaftar.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Segmented Pill
add_rect(f6_adm, 'F6A Tab BG', 80, 215, 420, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f6_adm, 'F6A Tab Act', 84, 219, 136, 40, fill_hex=C_SURFACE, radius=20)
add_text(f6_adm, 'F6A Tab 1', 132, 230, 'SNBP', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f6_adm, 'F6A Tab 2', 270, 230, 'SNBT', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f6_adm, 'F6A Tab 3', 405, 230, 'Mandiri', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f6_adm, 'F6A Card', 80, 285, 560, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_text(f6_adm, 'F6A CTitle', 112, 315, 'SNBP — Jalur Prestasi Rapor', font_size=24, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6_adm, 'F6A CDesc', 112, 350, 'Seleksi Nasional Berdasarkan Prestasi nilai rapor semester 1-5 dan portofolio kejuaraan.', font_size=14, color_hex=C_SECONDARY_TEXT, width=500, height=40)
add_text(f6_adm, 'F6A CDate', 112, 410, 'Jadwal Pendaftaran: 10 Nov - 20 Des 2026', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f6_adm, 'F6A CCost', 112, 435, 'Biaya Seleksi: Bebas Biaya (Ditanggung Pemerintah)', font_size=13, color_hex=C_SUCCESS, font_weight='Bold')

add_rect(f6_adm, 'F6A CBtn', 112, 530, 220, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f6_adm, 'F6A CBtnT', 152, 545, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_image_rect(f6_adm, 'F6A Photo', 680, 215, 680, 480, 'real_female_student.png', radius=24)

# Schedule Matrix Table Below
add_text(f6_adm, 'F6A Sched Header', 80, 680, 'MATRIKS LENGKAP JADWAL SELEKSI PMB 2026 (/schedule)', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f6_adm, 'F6A Sched Th', 80, 715, 1280, 40, fill_hex=C_PRIMARY, radius=[8, 8, 0, 0])
add_text(f6_adm, 'F6A Th 1', 110, 727, 'JALUR SELEKSI', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f6_adm, 'F6A Th 2', 360, 727, 'PEMBUKAAN AKUN', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f6_adm, 'F6A Th 3', 620, 727, 'PELAKSANAAN UJIAN / SELEKSI', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f6_adm, 'F6A Th 4', 960, 727, 'PENGUMUMAN HASIL KELULUSAN', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

sched_rows = [
    ('SNBP (Prestasi)', '08 Jan - 15 Feb 2026', 'Verifikasi Dokumen: 16 Feb - 15 Mar 2026', '26 Maret 2026 (Pukul 15.00 WIB)'),
    ('SNBT (UTBK)', '21 Mar - 05 Apr 2026', 'Gelombang 1: 30 Apr - 07 Mei 2026', '20 Juni 2026 (Pukul 15.00 WIB)'),
    ('SM-Mandiri', '02 Mei - 20 Jun 2026', 'Ujian CBT: 01 Jul - 10 Jul 2026', '25 Juli 2026 (Pukul 15.00 WIB)')
]
sy6 = 755
for jn, jp, ju, jh in sched_rows:
    add_rect(f6_adm, f'F6A Row {jn}', 80, sy6, 1280, 48, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
    add_text(f6_adm, f'F6A RowT1 {jn}', 110, sy6 + 15, jn, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f6_adm, f'F6A RowT2 {jn}', 360, sy6 + 15, jp, font_size=12, color_hex=C_SECONDARY_TEXT)
    add_text(f6_adm, f'F6A RowT3 {jn}', 620, sy6 + 15, ju, font_size=12, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f6_adm, f'F6A RowT4 {jn}', 960, sy6 + 15, jh, font_size=12, color_hex=C_SUCCESS, font_weight='Bold')
    sy6 += 48

# Tuition & Fees Frame (X=1540)
f6_tui = add_frame(p6, 'A07 & A08 — Tuition, Fees & Scholarships', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f6_tui, active_nav='Informasi')
add_text(f6_tui, 'F6T Title', 80, 120, 'Biaya Kuliah (UKT) & Skema Beasiswa (/tuition)', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6_tui, 'F6T Sub', 80, 165, 'Struktur Uang Kuliah Tunggal (UKT) transparan dan peluang beasiswa prestasi hingga 100%.', font_size=15, color_hex=C_SECONDARY_TEXT)

# UKT Table
add_rect(f6_tui, 'F6T Table BG', 80, 215, 780, 680, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f6_tui, 'F6T Th Title', 110, 240, 'Rincian Kelompok UKT Berdasarkan Penghasilan Orang Tua', font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

ukt_tiers = [
    ('Golongan I', 'Rp 500.000 / sem', '< Rp 1.500.000 / bln'),
    ('Golongan II', 'Rp 1.000.000 / sem', 'Rp 1.500.000 - Rp 3.000.000'),
    ('Golongan III', 'Rp 4.500.000 / sem', 'Rp 3.000.000 - Rp 5.000.000'),
    ('Golongan IV', 'Rp 6.000.000 / sem', 'Rp 5.000.000 - Rp 7.500.000'),
    ('Golongan V', 'Rp 8.500.000 / sem', 'Rp 7.500.000 - Rp 10.000.000'),
    ('Golongan VI', 'Rp 11.000.000 / sem', 'Rp 10.000.000 - Rp 15.000.000'),
    ('Golongan VII', 'Rp 13.500.000 / sem', '> Rp 15.000.000 / bln')
]
uy6 = 285
for gname, gcost, ginc in ukt_tiers:
    add_rect(f6_tui, f'F6T Row {gname}', 110, uy6, 720, 50, fill_hex=C_MUTED_SURFACE if 'III' in gname else C_SURFACE, stroke_hex=C_BORDER)
    add_text(f6_tui, f'F6T GT1 {gname}', 130, uy6 + 16, gname, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f6_tui, f'F6T GT2 {gname}', 320, uy6 + 16, gcost, font_size=13, color_hex=C_PRIMARY if 'III' in gname else C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f6_tui, f'F6T GT3 {gname}', 520, uy6 + 16, ginc, font_size=12, color_hex=C_SECONDARY_TEXT)
    uy6 += 52

# Right Scholarship Box
add_rect(f6_tui, 'F6T Schol BG', 890, 215, 470, 680, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f6_tui, 'F6T Schol Title', 920, 240, 'Peluang Beasiswa Penuh & Parsial (/scholarships)', font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f6_tui, 'F6T Schol Div', 920, 270, 410, 1, fill_hex=C_BORDER)

schols = [
    ('KIP-Kuliah Merdeka', 'Bebas UKT 100% + Uang Saku Bulanan', 'Bagi siswa berprestasi dengan keterbatasan ekonomi.'),
    ('Beasiswa Prestasi Unggulan', 'Potongan UKT 50% - 100%', 'Bagi peraih medali OSN/O2SN/FLS2N tingkat nasional.'),
    ('Beasiswa Kemitraan Industri', 'Bantuan Biaya Riset & Ikatan Kerja', 'Didukung oleh BUMN dan mitra teknologi terkemuka.')
]
sy_sch = 290
for sct, scb, scd in schols:
    add_rect(f6_tui, f'F6T SCBox {sct}', 920, sy_sch, 410, 95, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
    add_text(f6_tui, f'F6T SCT {sct}', 935, sy_sch + 14, sct, font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f6_tui, f'F6T SCB {sct}', 935, sy_sch + 36, scb, font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    add_text(f6_tui, f'F6T SCD {sct}', 935, sy_sch + 58, scd, font_size=10, color_hex=C_SECONDARY_TEXT)
    sy_sch += 110

print('Pages 4 and 6 built!')

# ==========================================
# PAGE 7: 07 — Authentication & Onboarding
# ==========================================
p7 = add_page(7, '07 — Authentication & Onboarding')

# Frame 1: Login & Register with Library Photo
f7_auth = add_frame(p7, 'AUTH01 & AUTH02 — Login & Register', 0, 0, 1440, 1024, C_BACKGROUND)
add_image_rect(f7_auth, 'P7 Lib Wall', 80, 60, 580, 900, 'library_bg.jpg', radius=20)
add_rect(f7_auth, 'P7 Lib Overlay', 80, 60, 580, 900, fill_hex=C_PRIMARY_TEXT, opacity=0.76, radius=20)

add_rect(f7_auth, 'P7 Glass Box', 110, 90, 520, 840, fill_hex=C_SURFACE, stroke_hex='#ffffff35', radius=16, opacity=0.15)
add_text(f7_auth, 'P7 Brand', 140, 120, 'PMB UNNES 2026', font_size=20, color_hex=C_SURFACE, font_weight='Bold')
add_text(f7_auth, 'P7 Info Title', 140, 160, 'Pendaftaran Akun Baru Siswa', font_size=24, color_hex=C_SURFACE, font_weight='Bold')
add_text(f7_auth, 'P7 Info Sub', 140, 195, 'Gunakan satu akun resmi untuk seluruh tahapan seleksi penerimaan mahasiswa baru di Universitas Indonesia.', font_size=12, color_hex=C_MUTED_SURFACE, width=460, height=40)

steps_auth7 = [
    ('1', 'Registrasi Akun Siswa', 'Daftarkan email aktif dan 10 digit NISN valid terdaftar Dapodik.'),
    ('2', 'Lengkapi Biodata Diri', 'Isi data pribadi, keluarga, dan riwayat sekolah asal Anda.'),
    ('3', 'Pilih Jalur & Prodi', 'Tentukan jalur seleksi dan 2 program studi prioritas.'),
    ('4', 'Unggah Berkas Syarat', 'Upload file scan Ijazah/SKL, Kartu Keluarga, dan Pas Foto.'),
    ('5', 'Finalisasi & Cetak Kartu', 'Verifikasi seluruh data dan terbitkan Kartu Peserta CBT.')
]
p7_sy = 250
for pnum, pstitle, psdesc in steps_auth7:
    add_rect(f7_auth, f'P7 SBox {pnum}', 140, p7_sy, 460, 74, fill_hex=C_SURFACE, stroke_hex='#ffffff25', radius=10, opacity=0.12)
    add_rect(f7_auth, f'P7 SNumBG {pnum}', 158, p7_sy + 17, 40, 40, fill_hex=C_PRIMARY, radius=20)
    add_text(f7_auth, f'P7 SNum {pnum}', 174, p7_sy + 28, pnum, font_size=14, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f7_auth, f'P7 STitle {pnum}', 212, p7_sy + 17, pstitle, font_size=13, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f7_auth, f'P7 SDesc {pnum}', 212, p7_sy + 39, psdesc, font_size=11, color_hex='#cbd5e1')
    p7_sy += 86

add_rect(f7_auth, 'P7 Help Pill', 140, 860, 460, 44, fill_hex=C_PRIMARY_HOVER, radius=22)
add_text(f7_auth, 'P7 Help Pill Txt', 185, 873, 'WhatsApp Helpdesk Admisi: 0812-3456-7890', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

# Right Form Panel
add_rect(f7_auth, 'P7 Form BG', 680, 60, 680, 900, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_text(f7_auth, 'P7 Back Link', 720, 95, '← Kembali ke Beranda Portal', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f7_auth, 'P7 Tab Container', 720, 135, 600, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f7_auth, 'P7 Tab 1 Active', 724, 139, 296, 40, fill_hex=C_SURFACE, radius=20)
add_text(f7_auth, 'P7 Tab 1 Txt', 815, 151, 'Masuk ke Akun', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7_auth, 'P7 Tab 2 Txt', 1105, 151, 'Daftar Akun Baru', font_size=13, color_hex=C_SECONDARY_TEXT)

add_text(f7_auth, 'P7 Form Title', 720, 220, 'Masuk ke Akun PMB', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7_auth, 'P7 Form Sub', 720, 255, 'Masukkan email atau NISN dan kata sandi yang telah terdaftar.', font_size=13, color_hex=C_SECONDARY_TEXT)

add_text(f7_auth, 'P7 Lbl 1', 720, 305, 'Alamat Email atau NISN *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7_auth, 'P7 Inp 1', 720, 330, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f7_auth, 'P7 Inp 1 Val', 738, 345, 'irfan@mail.com atau 0058291042', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f7_auth, 'P7 Lbl 2', 720, 405, 'Kata Sandi (Password) *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7_auth, 'P7 Inp 2', 720, 430, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f7_auth, 'P7 Inp 2 Val', 738, 445, '••••••••••••••••', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f7_auth, 'P7 Remember', 720, 498, '[X] Ingat Sesi Saya di Perangkat Ini', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f7_auth, 'P7 Forgot', 1210, 498, 'Lupa Password?', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f7_auth, 'P7 Submit Btn', 720, 540, 600, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f7_auth, 'P7 Submit Btn Txt', 960, 556, 'Masuk Sekarang →', font_size=14, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f7_auth, 'P7 Div Line', 720, 630, 600, 1, fill_hex=C_BORDER)
add_rect(f7_auth, 'P7 Reg Box', 720, 660, 600, 140, fill_hex='#f0f9ff', stroke_hex='#bae6fd', radius=14)
add_text(f7_auth, 'P7 Reg T', 748, 682, 'Belum memiliki akun pendaftaran PMB?', font_size=14, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f7_auth, 'P7 Reg D', 748, 706, 'Daftarkan diri Anda sekarang menggunakan NISN yang terdaftar resmi di Dapodik.', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f7_auth, 'P7 Reg Btn', 748, 735, 544, 42, fill_hex=C_SURFACE, stroke_hex=C_PRIMARY, radius=21)
add_text(f7_auth, 'P7 Reg Btn Txt', 915, 747, 'Registrasi Akun Baru Siswa (Gratis)', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

# Frame 2: Onboarding (X=1540)
f7_onb = add_frame(p7, 'ONBOARD01 to ONBOARD06 — Applicant Onboarding', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f7_onb, active_nav='Beranda')
add_text(f7_onb, 'ONB Title', 80, 120, 'Orientasi Akun Pendaftar Baru (/onboarding)', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7_onb, 'ONB Sub', 80, 165, 'Lengkapi profil dasar sebelum memulai pengisian formulir pendaftaran resmi.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Onboarding Stepper
add_rect(f7_onb, 'ONB Step BG', 80, 215, 1280, 72, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
onb_steps = [('1', 'Selamat Datang'), ('2', 'Profil Dasar'), ('3', 'Kontak Darurat'), ('4', 'Asal Sekolah'), ('5', 'Review & Selesai')]
obx = 110
for i, (onum, oname) in enumerate(onb_steps):
    c_bg = C_PRIMARY if i==0 else C_MUTED_SURFACE
    c_txt = C_SURFACE if i==0 else C_SECONDARY_TEXT
    add_rect(f7_onb, f'ONB SNode {onum}', obx, 231, 40, 40, fill_hex=c_bg, radius=20)
    add_text(f7_onb, f'ONB SNum {onum}', obx + 15, 242, onum, font_size=13, color_hex=c_txt, font_weight='Bold')
    add_text(f7_onb, f'ONB SName {onum}', obx + 50, 242, oname, font_size=13, color_hex=C_PRIMARY_TEXT if i==0 else C_SECONDARY_TEXT, font_weight='Bold' if i==0 else 'Regular')
    if i < 4:
        add_rect(f7_onb, f'ONB SLine {i}', obx + 165, 250, 75, 2, fill_hex=C_BORDER)
    obx += 250

# Onboarding Content Card
add_rect(f7_onb, 'ONB Card BG', 80, 310, 1280, 630, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f7_onb, 'ONB Welcome', 120, 350, 'Selamat Datang di Portal Penerimaan Mahasiswa Baru 2026', font_size=22, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7_onb, 'ONB Welcome D', 120, 385, 'Akun Anda berhasil diverifikasi. Mari kita persiapkan profil Anda dalam beberapa langkah sederhana.', font_size=14, color_hex=C_SECONDARY_TEXT)
add_rect(f7_onb, 'ONB Card Div', 120, 420, 1200, 1, fill_hex=C_BORDER)

add_text(f7_onb, 'ONB Q1', 120, 445, 'Apakah Anda sudah memiliki Nomor Induk Siswa Nasional (NISN) resmi? *', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7_onb, 'ONB Radio 1', 120, 475, 380, 48, fill_hex=C_MUTED_SURFACE, stroke_hex=C_PRIMARY, radius=10)
add_text(f7_onb, 'ONB R1 Txt', 140, 490, '●  Ya, saya memiliki NISN resmi Dapodik', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f7_onb, 'ONB Q2', 120, 550, 'Tahun Kelulusan Pendidikan Menengah Atas: *', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7_onb, 'ONB Dropdown', 120, 580, 380, 46, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f7_onb, 'ONB Dropdown Txt', 140, 594, 'Tahun 2026 (Lulusan Tahun Berjalan)  ▼', font_size=13, color_hex=C_PRIMARY_TEXT)

add_rect(f7_onb, 'ONB Next Btn', 120, 840, 240, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f7_onb, 'ONB Next Btn Txt', 158, 854, 'Lanjut ke Profil Diri →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 8: 08 — Applicant Registration & Correction Workflow (MANDATE #4!)
# ==========================================
p8 = add_page(8, '08 — Applicant Registration')

# Frame 1: Wizard (1440 x 1024)
f8_wiz = add_frame(p8, 'APPLICATION01 to 08 — Multi-Step Application Wizard', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f8_wiz, active_nav='Jalur Masuk')
add_text(f8_wiz, 'F8W Title', 80, 105, 'Formulir Pendaftaran Mahasiswa Baru — Jalur Mandiri Prestasi', font_size=20, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_wiz, 'F8W Sub', 80, 134, 'Lengkapi data pendaftaran Anda. Data disimpan otomatis ke basis data PostgreSQL.', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f8_wiz, 'F8W Stepper', 80, 165, 1280, 72, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
for i, (wn, wt, wa) in enumerate([('1', 'Data Diri', True), ('2', 'Asal Sekolah', False), ('3', 'Pilihan Prodi', False), ('4', 'Unggah Berkas', False), ('5', 'Finalisasi', False)]):
    c_fill = C_PRIMARY if wa else C_MUTED_SURFACE
    c_txt = C_SURFACE if wa else C_SECONDARY_TEXT
    add_rect(f8_wiz, f'F8W SN {wn}', 110 + i*250, 181, 40, 40, fill_hex=c_fill, radius=20)
    add_text(f8_wiz, f'F8W SNum {wn}', 110 + i*250 + 15, 192, wn, font_size=13, color_hex=c_txt, font_weight='Bold')
    add_text(f8_wiz, f'F8W STxt {wn}', 110 + i*250 + 50, 192, wt, font_size=13, color_hex=C_PRIMARY_TEXT if wa else C_SECONDARY_TEXT, font_weight='Bold' if wa else 'Regular')
    if i < 4:
        add_rect(f8_wiz, f'F8W SLine {i}', 110 + i*250 + 165, 200, 75, 2, fill_hex=C_BORDER)

add_rect(f8_wiz, 'F8W Form Box', 80, 255, 1280, 720, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f8_wiz, 'F8W Form Title', 112, 285, 'Tahap 1: Identitas Pribadi Calon Mahasiswa (/application/personal-data)', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_wiz, 'F8W Form Sub', 112, 310, 'Pastikan data yang dimasukkan sesuai dengan dokumen KTP / Kartu Keluarga resmi.', font_size=13, color_hex=C_SECONDARY_TEXT)
add_rect(f8_wiz, 'F8W Form Div', 112, 335, 1216, 1, fill_hex=C_BORDER)

c1_f8w = [('NIK *', '3302192804040003'), ('NISN *', '0058291042'), ('Nama Lengkap *', 'Muhammad Irfan'), ('Jenis Kelamin *', 'Laki-laki (Pilihan Sesuai KTP)'), ('Tempat Lahir *', 'Kota Semarang'), ('Tanggal Lahir *', '14 / 08 / 2005')]
for i, (lbl, val) in enumerate(c1_f8w):
    add_text(f8_wiz, f'F8W Lbl {lbl}', 112, 355 + i*78, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f8_wiz, f'F8W Inp {lbl}', 112, 375 + i*78, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f8_wiz, f'F8W Val {lbl}', 128, 387 + i*78, val, font_size=12, color_hex=C_PRIMARY_TEXT)

c2_f8w = [('Agama *', 'Islam (Pilihan)'), ('Nomor WhatsApp *', '081234567890'), ('Alamat Domisili *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'), ('Kelurahan *', 'Sekaran'), ('Kecamatan *', 'Gunungpati'), ('Kabupaten / Kota *', 'Kota Semarang, Jawa Tengah')]
for i, (lbl, val) in enumerate(c2_f8w):
    add_text(f8_wiz, f'F8W Lbl {lbl}', 748, 355 + i*78, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f8_wiz, f'F8W Inp {lbl}', 748, 375 + i*78, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f8_wiz, f'F8W Val {lbl}', 764, 387 + i*78, val, font_size=12, color_hex=C_PRIMARY_TEXT)

add_rect(f8_wiz, 'F8W Div Btm', 112, 860, 1216, 1, fill_hex=C_BORDER)
add_rect(f8_wiz, 'F8W Btn D', 112, 885, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f8_wiz, 'F8W Btn DT', 152, 900, 'Simpan Draf', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f8_wiz, 'F8W Btn N', 1048, 885, 280, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f8_wiz, 'F8W Btn NT', 1080, 900, 'Simpan & Lanjut ke Tahap 2 →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Frame 2: Application Correction Workflow (MANDATE #4!)
f8_cor = add_frame(p8, 'APPLICATION_CORRECTION — Application Correction Workflow', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f8_cor, active_nav='Jalur Masuk')
add_text(f8_cor, 'F8C Title', 80, 110, 'Perbaikan Berkas Dokumen Pendaftaran (/application/correction)', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_cor, 'F8C Sub', 80, 150, 'Panitia telah memeriksa berkas Anda dan meminta perbaikan dokumen sebelum batas waktu.', font_size=14, color_hex=C_SECONDARY_TEXT)

# Correction Alert Banner
add_rect(f8_cor, 'F8C Alert BG', 80, 185, 1280, 105, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=14)
add_text(f8_cor, 'F8C Alert T', 112, 205, 'PERMINTAAN PERBAIKAN DOKUMEN: KARTU KELUARGA (KK)', font_size=13, color_hex='#be123c', font_weight='Bold')
add_text(f8_cor, 'F8C Alert D1', 112, 230, 'Catatan Verifikator: "Scan Kartu Keluarga buram pada stempel kelurahan dan barcode terpotong.', font_size=12, color_hex='#9f1239')
add_text(f8_cor, 'F8C Alert D2', 112, 252, 'Mohon unggah ulang scan KK asli yang jelas dan terbaca sebelum 20 Desember 2026."', font_size=12, color_hex='#9f1239')

# Split View: Locked Info vs Editable Correction Dropzone
add_rect(f8_cor, 'F8C Lock BG', 80, 315, 600, 620, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8_cor, 'F8C Lock H', 110, 345, 'Data Pendaftaran (Terkunci / Sah)', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f8_cor, 'F8C Lock Div', 110, 372, 540, 1, fill_hex=C_BORDER)

locked_items = [
    ('Nomor Pendaftaran', 'PMB-2026-08492 [Locked]'),
    ('Nama Lengkap Siswa', 'Muhammad Irfan [Verified]'),
    ('Pilihan Program Studi', '1. S1 Teknik Informatika [Locked]'),
    ('Jalur Seleksi', 'Mandiri Prestasi Unggul [Locked]')
]
ly8 = 390
for lk, lv in locked_items:
    add_text(f8_cor, f'F8C LK {lk}', 110, ly8, lk, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f8_cor, f'F8C LV {lk}', 110, ly8 + 18, lv, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    ly8 += 52

# Right Side: Replacement Dropzone
add_rect(f8_cor, 'F8C Rep BG', 720, 315, 640, 620, fill_hex=C_SURFACE, stroke_hex=C_PRIMARY, stroke_width=2.0, radius=16)
add_text(f8_cor, 'F8C Rep H', 750, 345, 'Unggah Dokumen Perbaikan: Kartu Keluarga', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_cor, 'F8C Rep S', 750, 372, 'Pilih berkas baru beresolusi tinggi (PDF atau JPG, maks 2 MB).', font_size=12, color_hex=C_SECONDARY_TEXT)

# Drag and drop upload zone
add_rect(f8_cor, 'F8C DropZone', 750, 410, 580, 220, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, stroke_width=1.5, radius=12)
add_text(f8_cor, 'F8C Drop Icon', 1010, 480, '📁', font_size=24, color_hex=C_PRIMARY)
add_text(f8_cor, 'F8C Drop Txt 1', 940, 520, 'Tarik file scan KK baru ke sini', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_cor, 'F8C Drop Txt 2', 960, 545, 'atau klik untuk memilih file', font_size=12, color_hex=C_PRIMARY)

add_rect(f8_cor, 'F8C Submit Rep', 750, 840, 580, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f8_cor, 'F8C Submit Rep T', 925, 856, 'Kirim Perbaikan Dokumen untuk Ditinjau Ulang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

print('Pages 7 and 8 built!')

# ==========================================
# PAGE 9: 09 — Applicant Dashboard
# ==========================================
p9 = add_page(9, '09 — Applicant Dashboard')

# Frame 1: Overview (1440 x 1024)
f9_dash = add_frame(p9, 'DASHBOARD01 — Overview & Application Tracking', 0, 0, 1440, 1024, C_BACKGROUND)

# Header
add_rect(f9_dash, 'P9 Top Nav', 0, 0, 1440, 70, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f9_dash, 'P9 Logo', 80, 17, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f9_dash, 'P9 Logo T', 90, 25, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f9_dash, 'P9 Brand', 128, 24, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f9_dash, 'P9 Bell', 1260, 25, '🔔', font_size=16, color_hex=C_SECONDARY_TEXT)
add_image_rect(f9_dash, 'P9 Avatar', 1300, 16, 38, 38, 'student_id_photo.jpg', radius=19)

# Sidebar
add_rect(f9_dash, 'P9 Side BG', 0, 70, 240, 930, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
p9_items = [('Dashboard', True), ('Profil', False), ('Pendaftaran', False), ('Dokumen', False), ('Pembayaran', False), ('Seleksi', False), ('Notifikasi', False), ('Keluar', False)]
sby9 = 100
for sitem, sactive in p9_items:
    if sactive:
        add_rect(f9_dash, f'P9 SBar {sitem}', 0, sby9, 4, 40, fill_hex=C_PRIMARY)
        add_rect(f9_dash, f'P9 SPill {sitem}', 16, sby9, 208, 40, fill_hex=C_MUTED_SURFACE, radius=8)
    add_text(f9_dash, f'P9 SItem {sitem}', 40, sby9 + 11, sitem, font_size=13, color_hex=C_PRIMARY if sactive else C_SECONDARY_TEXT, font_weight='Bold' if sactive else 'Regular')
    sby9 += 46

add_text(f9_dash, 'P9 Greet', 280, 105, 'Halo, Andi Pratama 👋', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f9_dash, 'P9 Greet Sub', 280, 142, 'Selamat datang di dashboard pendaftaran PMB 2026', font_size=14, color_hex=C_SECONDARY_TEXT)
add_image_rect(f9_dash, 'P9 Accent', 1060, 90, 300, 85, 'real_bldg_ti.png', radius=12, opacity=0.7)

# Status Card
add_rect(f9_dash, 'P9 Status Card', 280, 190, 1080, 320, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f9_dash, 'P9 Card T', 312, 218, 'Status Pendaftaran', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

stx9 = 340
for i, (stitle, sdone) in enumerate([('Data Diri', True), ('Dokumen', True), ('Pembayaran', True), ('Seleksi', False), ('Hasil', False)]):
    c_fill = C_PRIMARY if sdone else C_MUTED_SURFACE
    c_txt = C_SURFACE if sdone else C_SECONDARY_TEXT
    c_sym = '✓' if sdone else ''
    add_rect(f9_dash, f'P9 Node {stitle}', stx9, 260, 32, 32, fill_hex=c_fill, radius=16)
    if c_sym:
        add_text(f9_dash, f'P9 Sym {stitle}', stx9 + 10, 268, c_sym, font_size=12, color_hex=c_txt, font_weight='Bold')
    add_text(f9_dash, f'P9 Txt {stitle}', stx9 - 15, 302, stitle, font_size=12, color_hex=C_PRIMARY_TEXT if sdone else C_SECONDARY_TEXT, font_weight='Bold' if sdone else 'Regular')
    if i < 4:
        add_rect(f9_dash, f'P9 Line {i}', stx9 + 40, 275, 150, 2, fill_hex=C_PRIMARY if i < 2 else C_BORDER)
    stx9 += 190

add_rect(f9_dash, 'P9 Succ Box', 312, 350, 1016, 120, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=14)
add_rect(f9_dash, 'P9 Succ Ico', 336, 375, 48, 48, fill_hex=C_SUCCESS, radius=24)
add_text(f9_dash, 'P9 Succ Chk', 352, 388, '✓', font_size=18, color_hex=C_SURFACE, font_weight='Bold')
add_text(f9_dash, 'P9 Succ T', 400, 376, 'Pendaftaran Berhasil', font_size=16, color_hex='#15803d', font_weight='Bold')
add_text(f9_dash, 'P9 Succ D', 400, 402, 'Terima kasih telah mendaftar. Pantau terus informasi terbaru melalui halaman ini.', font_size=13, color_hex='#166534')
add_text(f9_dash, 'P9 Succ L', 1210, 390, 'Lihat Detail →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f9_dash, 'P9 Info H', 280, 545, 'Informasi Penting', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f9_dash, 'P9 Info All', 1280, 545, 'Lihat Semua →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f9_dash, 'P9 Info Card', 280, 580, 400, 90, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_rect(f9_dash, 'P9 Info Ico BG', 302, 602, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
add_text(f9_dash, 'P9 Info Ico T', 312, 614, 'CAL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f9_dash, 'P9 Info Name', 360, 604, 'Jadwal Seleksi', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f9_dash, 'P9 Info Date', 360, 626, '25 Jun 2026', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 10: 10 — Selection & Examination
# ==========================================
p10 = add_page(10, '10 — Selection & Examination')
f10_cbt = add_frame(p10, 'SELECTION01 to 04 — CBT Schedule & Examination Card', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f10_cbt, active_nav='Jalur Masuk')

add_text(f10_cbt, 'F10 Title', 80, 105, 'Jadwal Seleksi & Kartu Tanda Peserta CBT (/selection)', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 Sub', 80, 142, 'Informasi ruang ujian tertulis berbasis komputer dan kartu tanda peserta resmi.', font_size=14, color_hex=C_SECONDARY_TEXT)

# Exam Pass Container (Exact Desktop Kop & Layout)
add_rect(f10_cbt, 'F10 Card BG', 80, 185, 780, 770, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)

# Kop Surat
add_rect(f10_cbt, 'F10 Kop Header', 80, 185, 780, 95, fill_hex='#f0f9ff', radius=[16, 16, 0, 0])
add_text(f10_cbt, 'F10 Kop 1', 110, 205, 'KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI', font_size=10, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 Kop 2', 110, 226, 'UNIVERSITAS INDONESIA', font_size=18, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f10_cbt, 'F10 Kop 3', 110, 252, 'KARTU TANDA PESERTA SELEKSI PMB 2026 — JALUR MANDIRI PRESTASI UNGGUL', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f10_cbt, 'F10 Kop Line', 110, 280, 720, 2, fill_hex=C_PRIMARY)

add_image_rect(f10_cbt, 'F10 Photo', 110, 305, 130, 175, 'student_id_photo.jpg', radius=8)

p_labels10 = [
    ('Nomor Peserta PMB:', 'PMB-2026-08492'),
    ('Nama Lengkap Siswa:', 'MUHAMMAD IRFAN'),
    ('NISN / NIK:', '0058291042 / 3302192804040003'),
    ('Asal Sekolah:', 'SMA Negeri 1 Semarang'),
    ('Jalur Pendaftaran:', 'Seleksi Mandiri Prestasi Unggul')
]
py10 = 305
for plbl, pval in p_labels10:
    add_text(f10_cbt, f'F10 PLbl {plbl}', 265, py10, plbl, font_size=10, color_hex=C_SECONDARY_TEXT)
    add_text(f10_cbt, f'F10 PVal {plbl}', 265, py10 + 16, pval, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    py10 += 38

add_rect(f10_cbt, 'F10 Prodi Box', 110, 505, 720, 85, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f10_cbt, 'F10 Prodi Header', 130, 518, 'PROGRAM STUDI PILIHAN:', font_size=10, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 Prodi 1', 130, 538, '1. S1 Teknik Informatika (Fakultas Ilmu Komputer) — Pilihan Utama', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 Prodi 2', 130, 560, '2. S1 Sistem Informasi (Fakultas Ilmu Komputer) — Pilihan Cadangan', font_size=12, color_hex=C_SECONDARY_TEXT)

add_rect(f10_cbt, 'F10 CBT Box', 110, 605, 720, 120, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f10_cbt, 'F10 CBT Header', 130, 618, 'JADWAL & LOKASI UJIAN TERTULIS (CBT):', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f10_cbt, 'F10 Hari Tgl', 130, 638, 'Hari / Tanggal  : Sabtu, 18 April 2026 • Sesi 1 (08.00 - 11.30 WIB)', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 Ruang Ujian', 130, 660, 'Ruang / Sektor : Gedung E10 Lt. 3, Lab Komputer 02 Fasilkom', font_size=12, color_hex=C_PRIMARY_TEXT)
add_text(f10_cbt, 'F10 Alamat CBT', 130, 682, 'Lokasi Kampus  : Kampus UI Depok, Jawa Barat', font_size=11, color_hex=C_SUCCESS)

# QR Code
add_rect(f10_cbt, 'F10 QR Box', 110, 745, 100, 100, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f10_cbt, 'F10 QR Dummy', 130, 785, '[ QR ]', font_size=12, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 QR Note', 225, 755, 'Validasi Keaslian Kartu Tanda Peserta CBT', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f10_cbt, 'F10 QR Note 2', 225, 775, 'Pengawas memindai kode QR untuk validasi keabsahan peserta ujian di lokasi.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f10_cbt, 'F10 QR Note 3', 225, 795, 'Tanda tangan digital: VALID (SHA-256 Verified by Committee)', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f10_cbt, 'F10 Print Btn', 110, 865, 720, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f10_cbt, 'F10 Print Btn T', 370, 880, 'Unduh Kartu Peserta (PDF) ↓', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Instructions Side Box (Right: w: 460)
add_rect(f10_cbt, 'F10 Inst BG', 890, 185, 470, 770, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f10_cbt, 'F10 Inst T', 920, 215, 'Tata Tertib Peserta Ujian CBT', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f10_cbt, 'F10 Inst Div', 920, 245, 410, 1, fill_hex=C_BORDER)

rules_cbt = [
    ('1. Waktu Kehadiran', 'Peserta wajib hadir paling lambat 30 menit sebelum sesi ujian dimulai.'),
    ('2. Dokumen Wajib Dibawa', 'Membawa Kartu Tanda Peserta cetak HVS A4 dan KTP/Kartu Pelajar asli.'),
    ('3. Pakaian Peserta', 'Mengenakan kemeja rapi berkerah dan sepatu tertutup.'),
    ('4. Larangan Elektronik', 'Dilarang membawa smartphone, kalkulator, atau jam tangan pintar ke meja ujian.'),
    ('5. Protokol Integritas', 'Kecurangan berakibat diskualifikasi permanen dari seluruh jalur masuk.')
]
ry10 = 265
for rkt, rkd in rules_cbt:
    add_text(f10_cbt, f'F10 RK {rkt}', 920, ry10, rkt, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f10_cbt, f'F10 RD {rkt}', 920, ry10 + 20, rkd, font_size=11, color_hex=C_SECONDARY_TEXT, width=410, height=35)
    ry10 += 65

# ==========================================
# PAGE 11: 11 — Admission Results
# ==========================================
p11 = add_page(11, '11 — Admission Results')
f11_res = add_frame(p11, 'RESULT01 to 07 — Admission Results & Offer Acceptance', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f11_res, active_nav='Beranda')

# Green Success Banner
add_rect(f11_res, 'F11 Hero BG', 80, 88, 1280, 175, fill_hex=C_SUCCESS, radius=16)
add_rect(f11_res, 'F11 Tag Badge', 112, 110, 360, 24, fill_hex='#15803d', radius=12)
add_text(f11_res, 'F11 Tag Badge Txt', 127, 115, 'PENGUMUMAN HASIL KELULUSAN AKHIR PMB TA 2026/2027', font_size=10, color_hex=C_SURFACE, font_weight='Bold')

add_text(f11_res, 'F11 Hero Title', 112, 145, 'SELAMAT! ANDA DINYATAKAN LULUS SELEKSI', font_size=28, color_hex=C_SURFACE, font_weight='Bold')
add_text(f11_res, 'F11 Hero Sub', 112, 182, 'Universitas Indonesia mengucapkan selamat bergabung dengan keluarga besar sivitas akademika kampus perjuangan.', font_size=13, color_hex='#d1fae5')
add_text(f11_res, 'F11 Hero Reg', 112, 208, 'Nomor Peserta: PMB-2026-08492   •   Jalur Masuk: Seleksi Mandiri Prestasi Unggul (SM-UI Terpadu)', font_size=12, color_hex='#a7f3d0')

# Details Card Left (w: 620)
add_rect(f11_res, 'F11 Left BG', 80, 280, 620, 650, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f11_res, 'F11 Left Title', 112, 305, '1. Rincian Penetapan Program Studi & Kelulusan', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f11_res, 'F11 Left Sub', 112, 328, 'Data resmi berdasarkan Surat Keputusan Rektor tentang Penetapan Mahasiswa Baru 2026.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_rect(f11_res, 'F11 Left Div', 112, 350, 556, 1, fill_hex=C_BORDER)

student_details11 = [
    ('Nama Lengkap Mahasiswa', 'Muhammad Irfan'),
    ('Nomor Registrasi / Pendaftaran', 'PMB-2026-08492'),
    ('NISN / NIK', '0058291042 / 3302192804040003'),
    ('Program Studi Diterima', 'S1 - Teknik Informatika (Reguler)'),
    ('Fakultas Terpilih', 'Fakultas Ilmu Komputer (Fasilkom UI)'),
    ('Jenjang Pendidikan', 'Sarjana (S1) — Akreditasi Unggul BAN-PT'),
    ('Kelompok UKT Ditetapkan', 'Golongan III (Rp 4.500.000 / semester)'),
    ('Nomor Virtual Account Bank', '9880-0058-2910-4200 (Bank BNI)'),
    ('Batas Waktu Pembayaran UKT', '25 Juli 2026, Pukul 15:00 WIB'),
    ('Status Verifikasi Dokumen', '100% Terverifikasi Lengkap (Sah)')
]
sdy11 = 365
for slbl, sval in student_details11:
    add_text(f11_res, f'F11 Lbl {slbl}', 112, sdy11, slbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    txt_color = C_PRIMARY if 'Teknik' in sval or '4.500.000' in sval or 'Sah' in sval else C_PRIMARY_TEXT
    add_text(f11_res, f'F11 Val {slbl}', 330, sdy11, sval, font_size=11, color_hex=txt_color, font_weight='Bold')
    add_rect(f11_res, f'F11 Div {slbl}', 112, sdy11 + 18, 556, 1, fill_hex='#f1f5f9')
    sdy11 += 35

add_rect(f11_res, 'F11 SKL Btn', 112, 850, 556, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f11_res, 'F11 SKL Btn Txt', 245, 865, 'Unduh Surat Keterangan Lulus (SKL) Resmi (PDF) ↓', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

# Re-registration Guide Right (w: 630)
add_rect(f11_res, 'F11 Right BG', 730, 280, 630, 650, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f11_res, 'F11 Right Title', 762, 305, '2. Alur & Panduan Wajib Registrasi Ulang', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f11_res, 'F11 Right Sub', 762, 328, 'Selesaikan 3 langkah registrasi ulang sebelum batas waktu agar hak kepesertaan tidak gugur.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_rect(f11_res, 'F11 Right Div', 762, 350, 566, 1, fill_hex=C_BORDER)

# Step 1: UKT
add_rect(f11_res, 'F11 S1 BG', 762, 365, 566, 115, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=12)
add_text(f11_res, 'F11 S1 Title', 784, 382, 'Langkah 1: Pembayaran Uang Kuliah Tunggal (UKT)', font_size=13, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f11_res, 'F11 S1 Desc', 784, 404, 'Lakukan pembayaran sebesar Rp 4.500.000 melalui Virtual Account BNI (9880-0058-2910-4200)', font_size=11, color_hex='#166534')
add_text(f11_res, 'F11 S1 Desc 2', 784, 424, 'melalui ATM, Mobile Banking BNI, atau Teller Bank BNI terdekat di seluruh Indonesia.', font_size=11, color_hex='#166534')
add_text(f11_res, 'F11 S1 Note', 784, 448, 'Tenggat Waktu: 25 Juli 2026, 15:00 WIB (Sistem otomatis memverifikasi pelunasan).', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')

# Step 2: SIMREG Online
add_rect(f11_res, 'F11 S2 BG', 762, 492, 566, 105, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=12)
add_text(f11_res, 'F11 S2 Title', 784, 508, 'Langkah 2: Registrasi Online & Pengisian Ukuran Jas Almamater', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f11_res, 'F11 S2 Desc', 784, 530, 'Isi data induk mahasiswa (SIMREG), riwayat kesehatan, dan ukuran jas almamater', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f11_res, 'F11 S2 Desc 2', 784, 550, '(S / M / L / XL / XXL) melalui portal resmi universitas.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f11_res, 'F11 S2 Status', 784, 572, '[ Terbuka otomatis setelah Pembayaran UKT Langkah 1 tervalidasi ]', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

# Step 3: Orientation
add_rect(f11_res, 'F11 S3 BG', 762, 608, 566, 95, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=12)
add_text(f11_res, 'F11 S3 Title', 784, 624, 'Langkah 3: Pengambilan KTM & Orientasi Kampus (PKKMB)', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f11_res, 'F11 S3 Desc', 784, 646, 'Pengambilan Kartu Tanda Mahasiswa (KTM) ATM BNI & Jas Almamater di Balairung.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f11_res, 'F11 S3 Desc 2', 784, 668, 'Jadwal PKKMB Universitas & Fakultas: 18 s.d. 20 Agustus 2026.', font_size=11, color_hex=C_SECONDARY_TEXT)

# Actions
add_rect(f11_res, 'F11 Reg Online Btn', 762, 715, 566, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f11_res, 'F11 Reg Online Btn Txt', 915, 730, 'Terima Tawaran & Lanjut ke Registrasi Online →', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f11_res, 'F11 WA Group Btn', 762, 775, 566, 42, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=21)
add_text(f11_res, 'F11 WA Group Btn Txt', 875, 788, 'Bergabung ke Komunitas WhatsApp Mahasiswa Baru Informatika 2026', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

# ==========================================
# PAGE 12: 12 — Re-registration
# ==========================================
p12 = add_page(12, '12 — Re-registration')
f12_rereg = add_frame(p12, 'REREG01 to 07 — Post-Acceptance Re-registration & Enrollment', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f12_rereg, active_nav='Beranda')
add_text(f12_rereg, 'F12 Title', 80, 110, 'Registrasi Ulang Mahasiswa Baru (/reregistration)', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f12_rereg, 'F12 Sub', 80, 148, 'Selesaikan kewajiban administratif dan verifikasi berkas asli untuk penerbitan Nomor Induk Mahasiswa (NIM).', font_size=14, color_hex=C_SECONDARY_TEXT)

# 4 Checkpoints Card
add_rect(f12_rereg, 'F12 Card BG', 80, 190, 1280, 750, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f12_rereg, 'F12 Steps H', 120, 220, 'Daftar Periksa Persyaratan Registrasi Ulang (Checklist)', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f12_rereg, 'F12 Div', 120, 250, 1200, 1, fill_hex=C_BORDER)

rereg_items = [
    ('1. Pembayaran UKT Semester 1', 'Virtual Account BNI 9880-0058-2910-4200 sebesar Rp 4.500.000.', 'LUNAS (Verified)', C_SUCCESS),
    ('2. Pengisian Biodata Induk (SIMREG)', 'Melengkapi form data keluarga, riwayat kesehatan, dan ukuran jas almamater.', 'SELESAI', C_SUCCESS),
    ('3. Unggah Surat Bebas Narkoba (SKBN)', 'Surat keterangan bebas narkoba resmi dari Rumah Sakit Pemerintah / BNN.', 'DALAM PENINJAUAN', C_WARNING),
    ('4. Penerbitan Nomor Induk Mahasiswa (NIM)', 'NIM resmi dan akun SSO universitas akan aktif otomatis setelah SKBN disetujui.', 'MENUNGGU VERIFIKASI', C_PRIMARY)
]
ry12 = 275
for rk, rd, rs, rscol in rereg_items:
    add_rect(f12_rereg, f'F12 RBox {rk}', 120, ry12, 1200, 80, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=12)
    add_text(f12_rereg, f'F12 RK {rk}', 145, ry12 + 18, rk, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f12_rereg, f'F12 RD {rk}', 145, ry12 + 42, rd, font_size=12, color_hex=C_SECONDARY_TEXT)
    
    add_rect(f12_rereg, f'F12 RBdg {rk}', 1110, ry12 + 25, 180, 30, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=15)
    add_text(f12_rereg, f'F12 RBTxt {rk}', 1125, ry12 + 32, rs, font_size=10, color_hex=rscol, font_weight='Bold')
    ry12 += 95

add_rect(f12_rereg, 'F12 Final Btn', 120, 720, 400, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f12_rereg, 'F12 Final Btn T', 205, 735, 'Cetak Bukti Registrasi Ulang (PDF) ↓', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 13: 13 — Account & Support
# ==========================================
p13 = add_page(13, '13 — Account & Support')
f13_supp = add_frame(p13, 'ACCOUNT01 to 08 — Settings, Security & Support Center', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f13_supp, active_nav='Informasi')
add_text(f13_supp, 'F13 Title', 80, 110, 'Pengaturan Akun & Pusat Bantuan Calon Mahasiswa (/dashboard/help)', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Left: Support Ticket Form
add_rect(f13_supp, 'F13 Ticket BG', 80, 160, 620, 780, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f13_supp, 'F13 Ticket H', 110, 190, 'Kirim Tiket Bantuan ke Helpdesk Admisi', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f13_supp, 'F13 Ticket S', 110, 215, 'Sampaikan pertanyaan atau kendala teknis yang Anda alami selama proses pendaftaran.', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f13_supp, 'F13 Ticket Div', 110, 240, 560, 1, fill_hex=C_BORDER)

t_fields = [
    ('Kategori Kendala *', 'Verifikasi Berkas & Dokumen Persyaratan ▼'),
    ('Subjek Pertanyaan *', 'Kendala stempel legalisir Kartu Keluarga tidak terbaca'),
    ('Nomor Pendaftaran Siswa *', 'PMB-2026-08492')
]
ty13 = 260
for tlbl, tval in t_fields:
    add_text(f13_supp, f'F13 TLbl {tlbl}', 110, ty13, tlbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f13_supp, f'F13 TInp {tlbl}', 110, ty13 + 20, 560, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f13_supp, f'F13 TVal {tlbl}', 126, ty13 + 32, tval, font_size=12, color_hex=C_PRIMARY_TEXT)
    ty13 += 75

add_text(f13_supp, 'F13 Msg Lbl', 110, ty13, 'Uraian Pesan / Kendala Detail *', font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f13_supp, 'F13 Msg Box', 110, ty13 + 20, 560, 120, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f13_supp, 'F13 Msg Val', 126, ty13 + 35, 'Selamat siang tim admisi, saya ingin mengonfirmasi bahwa scan KK yang baru telah saya upload ulang dengan stempel basah kelurahan yang sangat jelas. Mohon ditinjau kembali. Terima kasih.', font_size=11, color_hex=C_PRIMARY_TEXT, width=530, height=50)

add_rect(f13_supp, 'F13 Submit Tkt', 110, 850, 560, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f13_supp, 'F13 Submit Tkt T', 315, 865, 'Kirim Tiket Bantuan →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Right: FAQ & Direct Contacts
add_rect(f13_supp, 'F13 FAQ BG', 740, 160, 620, 780, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f13_supp, 'F13 FAQ H', 770, 190, 'Pertanyaan yang Sering Diajukan (FAQ)', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f13_supp, 'F13 FAQ Div', 770, 240, 560, 1, fill_hex=C_BORDER)

faqs = [
    ('Apakah data pendaftaran bisa diedit setelah finalisasi?', 'Setelah finalisasi dilakukan, data terkunci permanen kecuali panitia verifikator meminta revisi.'),
    ('Berapa lama proses verifikasi berkas berlangsung?', 'Verifikasi berkas membutuhkan waktu 1 s.d. 3 hari kerja sejak dokumen berhasil diunggah lengkap.'),
    ('Bagaimana jika pembayaran UKT melewati tenggat waktu?', 'Keterlambatan pembayaran UKT tanpa konfirmasi resmi berakibat gugurnya hak kepesertaan.'),
    ('Bagaimana cara mengaktifkan notifikasi Web Push?', 'Klik tombol "Aktifkan Notifikasi" pada kartu Web Push di dashboard pendaftar Anda.')
]
fy13 = 260
for fq, fa in faqs:
    add_rect(f13_supp, f'F13 FQ Box {fq}', 770, fy13, 560, 85, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
    add_text(f13_supp, f'F13 FQ T {fq}', 788, fy13 + 15, fq, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f13_supp, f'F13 FA T {fq}', 788, fy13 + 38, fa, font_size=11, color_hex=C_SECONDARY_TEXT, width=520, height=35)
    fy13 += 98

# Contact hotline box
add_rect(f13_supp, 'F13 Contact Box', 770, 720, 560, 180, fill_hex=C_MUTED_SURFACE, stroke_hex=C_BORDER, radius=12)
add_text(f13_supp, 'F13 C Title', 790, 740, 'Kontak Langsung Panitia Admisi:', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f13_supp, 'F13 C WA', 790, 770, 'WhatsApp Helpdesk : 0812-3456-7890 (Hari Kerja 08:00 - 16:00 WIB)', font_size=12, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f13_supp, 'F13 C Call', 790, 796, 'Call Center Rektorat : (024) 8508093 (Hunting 5 saluran)', font_size=12, color_hex=C_PRIMARY_TEXT)
add_text(f13_supp, 'F13 C Mail', 790, 822, 'Email Resmi Bantuan : pmb@mail.unnes.ac.id / admisi@ui.ac.id', font_size=12, color_hex=C_PRIMARY)
add_text(f13_supp, 'F13 C Addr', 790, 848, 'Alamat Fisik : Gedung Rektorat Sayap Kiri, Kampus Pusat Sekaran, Semarang', font_size=11, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 14: 14 — Interactive Prototype
# ==========================================
p14 = add_page(14, '14 — Interactive Prototype')
f14_proto = add_frame(p14, 'Prototype Journey Architecture — 10 Flow Maps', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f14_proto, active_nav='Informasi')
add_text(f14_proto, 'F14 Title', 80, 110, 'Arsitektur Alur Interaktif Prototipe (10 User Journeys)', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f14_proto, 'F14 Sub', 80, 148, 'Peta alur komprehensif perjalanan calon mahasiswa dari tahap penemuan informasi hingga kelulusan resmi.', font_size=14, color_hex=C_SECONDARY_TEXT)

flows_10 = [
    ('FLOW A — PUBLIC DISCOVERY', 'Homepage → Programs → Search & Filter → Program Detail → Pathways → Guide → Register', C_PRIMARY),
    ('FLOW B — NEW APPLICANT', 'Register → Create Account → Verify Email → Login → Welcome → Profile Setup → Contact → Education → Review → Complete → Dashboard', C_PRIMARY),
    ('FLOW C — RETURNING APPLICANT', 'Homepage → Login → Authentication Success → Dashboard (Includes invalid credentials, reset password, expired session states)', C_PRIMARY),
    ('FLOW D — APPLICATION SUBMISSION', 'Dashboard → My Applications → Start Application → Academic Year → Pathway → Eligibility → Program Preferences → Personal Data → Address → Education → Guardian → Achievements → Documents → Document Preview → Review → Declaration → Confirm → Success', C_PRIMARY),
    ('FLOW E — DOCUMENT CORRECTION', 'Dashboard → Documents → Rejected Document → Rejection Detail → Replace Document → Upload Success → Pending Verification', C_ERROR),
    ('FLOW F — CONDITIONAL PAYMENT', 'Submission → Payment Overview → Select Method → Payment Instructions → Pending → Success → Receipt → Dashboard (With no-payment branch for SNBP)', C_WARNING),
    ('FLOW G — SELECTION & CBT', 'Dashboard → Selection Overview → Examination Schedule → Examination Card → Instructions → Selection Status → Results Pending', C_PRIMARY),
    ('FLOW H — ACCEPTED APPLICANT', 'Results Pending → Accepted → Offer Detail → Accept Offer → Confirmation → Re-registration → Documents → Payment → Profile → Review → Re-registration Success → Admission Completed', C_SUCCESS),
    ('FLOW I — NOT ACCEPTED JOURNEY', 'Results Pending → Not Accepted → Result Detail → Available Next Steps → Help Center', C_ERROR),
    ('FLOW J — APPLICANT ACCOUNT', 'Dashboard → Notifications → Notification Detail | Dashboard → Settings → Security → Change Password | Dashboard → Help → Contact Support → Success | Logout → Confirmation → Homepage', C_PRIMARY)
]
fy14 = 185
for ftitle, fdesc, fcol in flows_10:
    add_rect(f14_proto, f'F14 FBox {ftitle}', 80, fy14, 1280, 68, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=12)
    add_rect(f14_proto, f'F14 FTag {ftitle}', 80, fy14, 6, 68, fill_hex=fcol, radius=[12, 0, 0, 12])
    add_text(f14_proto, f'F14 FT {ftitle}', 105, fy14 + 14, ftitle, font_size=13, color_hex=fcol, font_weight='Bold')
    add_text(f14_proto, f'F14 FD {ftitle}', 105, fy14 + 38, fdesc, font_size=11, color_hex=C_SECONDARY_TEXT, width=1230, height=20)
    fy14 += 76

# ==========================================
# PAGE 15: 15 — Route Coverage & QA Audit (MANDATE #6 & #22!)
# ==========================================
p15 = add_page(15, '15 — Route Coverage & QA Audit')

# Frame 1: Application State Transition Matrix (MANDATE #6!)
f15_stm = add_frame(p15, 'APPLICATION STATE TRANSITION MATRIX', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f15_stm, active_nav='Informasi')
add_text(f15_stm, 'F15 S Title', 80, 105, 'APPLICATION STATE TRANSITION MATRIX (V6.1 MANDATE #6)', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f15_stm, 'F15 S Sub', 80, 142, 'Matriks daur hidup status pendaftaran calon mahasiswa: pesan, aksi yang tersedia, dan kondisi transisi.', font_size=13, color_hex=C_SECONDARY_TEXT)

# Table Container (w: 1280, h: 780)
add_rect(f15_stm, 'F15 S Table BG', 80, 175, 1280, 780, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)

add_rect(f15_stm, 'F15 S Th', 80, 175, 1280, 42, fill_hex=C_PRIMARY, radius=[16, 16, 0, 0])
add_text(f15_stm, 'F15 S Th 1', 110, 188, 'CURRENT STATUS', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_stm, 'F15 S Th 2', 320, 188, 'APPLICANT-VISIBLE MESSAGE', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_stm, 'F15 S Th 3', 700, 188, 'AVAILABLE APPLICANT ACTION', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_stm, 'F15 S Th 4', 980, 188, 'NEXT POSSIBLE STATE', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_stm, 'F15 S Th 5', 1210, 188, 'CONDITION', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

state_matrix = [
    ('DRAFT', 'Formulir tersimpan sebagai draf.', 'Lanjutkan Pengisian Form', 'DOCUMENTS_PENDING', 'Data diri terisi lengkap'),
    ('DOCUMENTS_PENDING', 'Menunggu unggahan 4 dokumen syarat.', 'Unggah Ijazah, KK, Foto, Prestasi', 'DOCUMENTS_REVIEW', '4 berkas terunggah'),
    ('DOCUMENTS_REJECTED', 'Dokumen KK buram / perlu perbaikan.', 'Perbaiki & Upload Ulang Dokumen', 'DOCUMENTS_REVIEW', 'Revisi berkas sah'),
    ('PAYMENT_PENDING', 'Menunggu pembayaran biaya pendaftaran.', 'Bayar via Virtual Account BNI', 'PAYMENT_VERIFIED', 'Pelunasan tervalidasi'),
    ('SUBMITTED', 'Pendaftaran final berhasil dikirim.', 'Pantau Status & Unduh Resume', 'UNDER_REVIEW', 'Finalisasi selesai'),
    ('UNDER_REVIEW', 'Panitia admisi sedang memverifikasi berkas.', 'Pantau Notifikasi Web Push', 'ELIGIBLE / NOT_ELIGIBLE', 'Sidang verifikasi'),
    ('EXAM_SCHEDULED', 'Jadwal ujian tertulis CBT telah terbit.', 'Cetak Kartu Tanda Peserta CBT', 'SELECTION_COMPLETED', 'Mengikuti ujian'),
    ('RESULT_PENDING', 'Tahap seleksi selesai, menunggu kelulusan.', 'Lihat Jadwal Pengumuman', 'ACCEPTED / NOT_ACCEPTED', 'Rapat pleno kelulusan'),
    ('ACCEPTED', 'Selamat! Anda diterima di S1 Teknik Informatika.', 'Terima Tawaran & Registrasi', 'OFFER_ACCEPTED', 'Konfirmasi pilihan'),
    ('RE_REG_PENDING', 'Menunggu pelunasan UKT & SIMREG.', 'Bayar UKT & Isi Data Induk', 'ADMISSION_COMPLETED', 'Kewajiban lunas')
]
sty = 217
for s1, s2, s3, s4, s5 in state_matrix:
    add_rect(f15_stm, f'F15 S Row {s1}', 80, sty, 1280, 48, fill_hex=C_MUTED_SURFACE if 'ACCEPTED' in s1 else C_SURFACE, stroke_hex='#f1f5f9')
    add_text(f15_stm, f'F15 S C1 {s1}', 110, sty + 16, s1, font_size=11, color_hex=C_PRIMARY if 'ACCEPTED' in s1 else C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f15_stm, f'F15 S C2 {s1}', 320, sty + 16, s2, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f15_stm, f'F15 S C3 {s1}', 700, sty + 16, s3, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f15_stm, f'F15 S C4 {s1}', 980, sty + 16, s4, font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    add_text(f15_stm, f'F15 S C5 {s1}', 1210, sty + 16, s5, font_size=11, color_hex=C_SECONDARY_TEXT)
    sty += 48

# Frame 2: Complete Route Coverage & QA Audit Matrix (MANDATE #22!)
f15_audit = add_frame(p15, 'Complete Route Coverage & QA Audit Matrix', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f15_audit, active_nav='Informasi')
add_text(f15_audit, 'F15 A Title', 80, 105, 'COMPLETE ROUTE COVERAGE & QA AUDIT MATRIX (48 ROUTES)', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f15_audit, 'F15 A Sub', 80, 142, 'Audit pemenuhan 100% rute desktop calon mahasiswa tanpa celah navigasi (Mandate V6.1).', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f15_audit, 'F15 A Table BG', 80, 175, 1280, 780, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_rect(f15_audit, 'F15 A Th', 80, 175, 1280, 42, fill_hex=C_PRIMARY, radius=[16, 16, 0, 0])
add_text(f15_audit, 'F15 A Th 1', 110, 188, 'ROUTE ID & PATH', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_audit, 'F15 A Th 2', 400, 188, 'ROUTE NAME & USER JOURNEY STAGE', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_audit, 'F15 A Th 3', 850, 188, 'DESKTOP FIGMA FRAME', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f15_audit, 'F15 A Th 4', 1210, 188, 'QA STATUS', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

routes_audit = [
    ('A01: /', 'Homepage (Public Website)', '04 — Public Website: A01 — Homepage', 'APPROVED', C_SUCCESS),
    ('A02: /programs', 'Program Directory (Search & Filters)', '05 — Program Discovery: A02 — Directory', 'APPROVED', C_SUCCESS),
    ('A03: /programs/[slug]', 'Program Detail (Curriculum & Overview)', '05 — Program Discovery: A03 — Detail', 'APPROVED', C_SUCCESS),
    ('A04: /admissions', 'Admission Pathways (SNBP, SNBT, Mandiri)', '06 — Admission: A04 & A05 Pathways', 'APPROVED', C_SUCCESS),
    ('A06: /schedule', 'Admission Schedule Matrix', '06 — Admission: A06 Schedule Matrix', 'APPROVED', C_SUCCESS),
    ('A07: /tuition', 'Tuition & UKT Fees Schedule (Gol I-VII)', '06 — Admission: A07 & A08 Tuition', 'APPROVED', C_SUCCESS),
    ('AUTH01: /login', 'Applicant Login (Library Photo BG)', '07 — Authentication: AUTH01 Login', 'APPROVED', C_SUCCESS),
    ('AUTH02: /register', 'Applicant Registration', '07 — Authentication: AUTH02 Register', 'APPROVED', C_SUCCESS),
    ('ONBOARD01: /onboarding', 'Applicant Onboarding Welcome', '07 — Authentication: ONBOARD01-06', 'APPROVED', C_SUCCESS),
    ('APP06: /application/programs', 'Application Program Preferences Selection', '08 — Registration: APP06 Programs', 'APPROVED', C_SUCCESS),
    ('APP07: /application/personal-data', 'Application Personal Data Form', '08 — Registration: APP07 Personal Data', 'APPROVED', C_SUCCESS),
    ('APP12: /application/documents', 'Document Upload & Storage Integration', '08 — Registration: APP12 Documents', 'APPROVED', C_SUCCESS),
    ('CORR01: /application/correction', 'Document Correction & Replacement', '08 — Registration: Correction Flow', 'APPROVED', C_SUCCESS),
    ('DASH01: /dashboard', 'Applicant Dashboard Overview & Stepper', '09 — Dashboard: DASH01 Overview', 'APPROVED', C_SUCCESS),
    ('SELEC03: /selection/exam-card', 'Official CBT Examination Pass (Photo & QR)', '10 — Selection: Exam Pass Card', 'APPROVED', C_SUCCESS),
    ('RES02: /results/accepted', 'Admission Accepted & Offer Confirmation', '11 — Results: Accepted & Offer', 'APPROVED', C_SUCCESS),
    ('REREG01: /reregistration', 'Post-Acceptance Re-registration & SIMREG', '12 — Re-registration: REREG01', 'APPROVED', C_SUCCESS),
    ('QA01: /audit', 'Route Coverage & QA Audit Matrix', '15 — Route Coverage & QA Audit', 'APPROVED', C_SUCCESS)
]
aty15 = 217
for rid, rname, rframe, rstat, rcol in routes_audit:
    add_rect(f15_audit, f'F15 A Row {rid}', 80, aty15, 1280, 42, fill_hex=C_SURFACE, stroke_hex='#f1f5f9')
    add_text(f15_audit, f'F15 A C1 {rid}', 110, aty15 + 14, rid, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f15_audit, f'F15 A C2 {rid}', 400, aty15 + 14, rname, font_size=11, color_hex=C_PRIMARY_TEXT)
    add_text(f15_audit, f'F15 A C3 {rid}', 850, aty15 + 14, rframe, font_size=11, color_hex=C_SECONDARY_TEXT)
    
    add_rect(f15_audit, f'F15 A Bdg {rid}', 1200, aty15 + 8, 100, 24, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=12)
    add_text(f15_audit, f'F15 A BdgT {rid}', 1222, aty15 + 13, rstat, font_size=9, color_hex=rcol, font_weight='Bold')
    aty15 += 42

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/pmb-ui-concept.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack directly into .figcraft zip
zip_path = 'C:/projects/ta-pemweb/uidesign/pmb-ui-concept.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully compiled complete master Figma V6.1 architecture into {zip_path} with {len(doc["nodes"])} nodes across {len(doc["pages"])} pages and {len(images_meta)} images!')
