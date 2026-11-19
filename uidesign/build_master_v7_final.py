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

# Exact Master V7 Colors
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
    'name': 'PMB 2026 — Private University Admission Platform (V7 Master)',
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
    add_text(frame_id, 'Logo Txt', 90, 28, 'UN', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
    add_text(frame_id, 'Brand Name', 128, 26, 'Universitas Nusantara', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    
    navs = ['Beranda', 'Program Studi ⌵', 'Informasi Pendaftaran ⌵', 'Gelombang Seleksi ⌵', 'Biaya & Beasiswa']
    nx = 480
    for ni in navs:
        is_act = (active_nav in ni)
        add_text(frame_id, f'Nav {ni}', nx, 28, ni, font_size=13, color_hex=C_PRIMARY if is_act else C_SECONDARY_TEXT, font_weight='Bold' if is_act else 'Regular')
        nx += 140
        
    add_text(frame_id, 'Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)
    add_rect(frame_id, 'Btn Daftar Nav', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
    add_text(frame_id, 'Btn Daftar Nav Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

def add_desktop_footer(frame_id, y_pos=960):
    add_rect(frame_id, 'Footer BG', 0, y_pos, 1440, 64, fill_hex=C_PRIMARY)
    add_text(frame_id, 'Footer Copy', 80, y_pos + 25, '© 2026 Universitas Nusantara (PTS) — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi.', font_size=11, color_hex=C_SURFACE)

print('V7 Master Scaffold Initialized.')

# ==========================================
# PAGE 1: 01 — Cover & Six-Screen Overview
# ==========================================
p1 = add_page(1, '01 — Cover & Six-Screen Overview')

# Frame 0: Cover Presentation
f_cov = add_frame(p1, '00. Master Cover — PMB 2026 PTS', 0, 0, 1440, 1024, C_BACKGROUND)
add_rect(f_cov, 'Cov Hero BG', 80, 80, 1280, 480, fill_hex=C_PRIMARY, radius=24)
add_image_rect(f_cov, 'Cov Hero Photo', 80, 80, 1280, 480, 'hero_campus.jpg', radius=24, opacity=0.35)

add_rect(f_cov, 'Cov Tag Pill', 120, 120, 310, 32, fill_hex=C_SURFACE, radius=16)
add_text(f_cov, 'Cov Tag Txt', 140, 128, 'MASTER PROMPT V7 · PRIVATE UNIVERSITY', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_cov, 'Cov Title 1', 120, 175, 'PMB 2026 — Private University', font_size=46, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_cov, 'Cov Title 2', 120, 235, 'Admission Platform (PTS)', font_size=46, color_hex=C_WARNING, font_weight='Bold')

add_text(f_cov, 'Cov Desc 1', 120, 305, 'Single Admission Process · Multiple Registration Waves (Gelombang 1, 2, 3) · Single Program Selection.', font_size=15, color_hex=C_MUTED_SURFACE)
add_text(f_cov, 'Cov Desc 2', 120, 330, 'Applicant Only · Desktop Web Only · Complete 15 Pages Architecture & 48 Connected Routes.', font_size=15, color_hex=C_MUTED_SURFACE)

# Meta Box
add_rect(f_cov, 'Cov Meta Box', 120, 385, 1200, 130, fill_hex=C_SURFACE, radius=16)
cmetas = [
    ('INSTITUTION TYPE', 'Private University (PTS) Model'),
    ('ADMISSION LOGIC', 'Single Process • Multiple Waves'),
    ('PROGRAM SELECTION', 'Single Primary Choice (No 2nd Choice)'),
    ('SCOPE RESTRICTION', 'Zero Mobile • Zero Admin Bleed')
]
cmx = 150
for clbl, cval in cmetas:
    add_text(f_cov, f'CM Lbl {clbl}', cmx, 415, clbl, font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'CM Val {clbl}', cmx, 440, cval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    cmx += 280

# 3 Pillars
pillars = [
    ('Single Unified Admission', 'Satu alur admisi terpadu tanpa pemecahan jalur ganda; semua calon mahasiswa mengikuti proses yang sama.'),
    ('Multiple Registration Waves', 'Penerimaan dibagi atas periode gelombang (Gelombang 1, 2, 3) dengan tanggal buka-tutup dan kuota transparan.'),
    ('Pill-Shaped Tactile Controls', 'Seluruh tombol aksi utama berbentuk rounded-full (pill) berstandar Plus Jakarta Sans dengan kontras tajam.')
]
plx = 80
for ptitle, pdesc in pillars:
    add_rect(f_cov, f'Pil BG {ptitle}', plx, 600, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_rect(f_cov, f'Pil Accent {ptitle}', plx, 600, 400, 6, fill_hex=C_PRIMARY, radius=[18, 18, 0, 0])
    add_text(f_cov, f'Pil Title {ptitle}', plx + 28, 635, ptitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'Pil Desc {ptitle}', plx + 28, 675, pdesc, font_size=14, color_hex=C_SECONDARY_TEXT, width=344, height=60)
    plx += 440

add_text(f_cov, 'Cov Footer', 80, 975, '© 2026 PMB Master Design Specification V7 — Private University Complete Platform.', font_size=12, color_hex=C_SECONDARY_TEXT)

# ----------------------------------------------------
# 2-COLUMN x 3-ROW SIX-PANEL DESIGNBOARD (V7 MANDATE)
# ----------------------------------------------------
# Panel 1 (Row 1, Col 1, X=1600, Y=0): Homepage / University Landing Page
f_p1 = add_frame(p1, 'Panel 1 — Homepage / University Landing Page', 1600, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p1, active_nav='Beranda')
add_text(f_p1, 'P1 Hero 1', 80, 140, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p1, 'P1 Hero 2', 80, 205, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p1, 'P1 Hero 3', 80, 270, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p1, 'P1 Sub 1', 80, 350, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f_p1, 'P1 Sub 2', 80, 375, 'bersama Universitas Nusantara.', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f_p1, 'P1 Btn CTA', 80, 425, 195, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f_p1, 'P1 Btn CTA Txt', 115, 439, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_p1, 'P1 Video CTA', 305, 439, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_image_rect(f_p1, 'P1 Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)

add_rect(f_p1, 'P1 Ribbon BG', 80, 670, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
for rlbl, rval, rico, rx in [('Periode Pendaftaran', 'Gelombang 1 s.d. 3', 'WAV', 120), ('Proses Seleksi', 'Satu Alur Terpadu', 'CAP', 440), ('Program Studi', '100+ Pilihan S1', 'BOK', 760), ('Beasiswa PTS', 'Hingga 100% Penuh', 'GFT', 1060)]:
    add_rect(f_p1, f'P1 RIco {rico}', rx, 696, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f_p1, f'P1 RIcoT {rico}', rx + 10, 709, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f_p1, f'P1 RLbl {rlbl}', rx + 56, 700, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_p1, f'P1 RVal {rval}', rx + 56, 720, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_text(f_p1, 'P1 Sec Waves Title', 80, 795, 'GELOMBANG PENDAFTARAN AKTIF TA 2026/2027', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
for wname, wdates, wstat, wcost, wimg, wx in [('Gelombang 1 (Early Bird)', '01 Jan - 28 Feb 2026', 'SEDANG DIBUKA', 'Biaya: Rp 250.000 (Diskon UKT 20%)', 'card_snbp.jpg', 80), ('Gelombang 2 (Reguler)', '01 Mar - 30 Apr 2026', 'MENDATANG', 'Biaya: Rp 300.000', 'card_snbt.jpg', 520), ('Gelombang 3 (Penutup)', '01 Mei - 30 Jun 2026', 'MENDATANG', 'Biaya: Rp 350.000', 'card_mandiri.jpg', 960)]:
    add_rect(f_p1, f'P1 WC BG {wname}', wx, 825, 400, 130, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f_p1, f'P1 WC Img {wname}', wx, 825, 140, 130, wimg, radius=[14, 0, 0, 14])
    add_text(f_p1, f'P1 WC Title {wname}', wx + 155, 845, wname, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_p1, f'P1 WC Dates {wname}', wx + 155, 868, wdates, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f_p1, f'P1 WC Cost {wname}', wx + 155, 888, wcost, font_size=10, color_hex=C_SUCCESS if 'Early' in wname else C_SECONDARY_TEXT)
    add_rect(f_p1, f'P1 WC Pill {wname}', wx + 155, 915, 110, 24, fill_hex='#ecfdf5' if 'DIBUKA' in wstat else C_MUTED_SURFACE, radius=12)
    add_text(f_p1, f'P1 WC PillTxt {wname}', wx + 170, 921, wstat, font_size=9, color_hex=C_SUCCESS if 'DIBUKA' in wstat else C_SECONDARY_TEXT, font_weight='Bold')
add_desktop_footer(f_p1, y_pos=975)

# Panel 2 (Row 1, Col 2, X=3140, Y=0): Program Directory
f_p2 = add_frame(p1, 'Panel 2 — Program Directory', 3140, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p2, active_nav='Program Studi')
add_text(f_p2, 'P2 Title', 80, 120, 'Program Studi', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p2, 'P2 Sub', 80, 168, 'Temukan program studi yang sesuai dengan minat dan bakatmu. Pilih 1 Program Studi Utama.', font_size=15, color_hex=C_SECONDARY_TEXT)
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

# Panel 3 (Row 2, Col 1, X=1600, Y=1124): Admission & Registration Waves (V7 PTS Model!)
f_p3 = add_frame(p1, 'Panel 3 — Admission & Registration Waves', 1600, 1124, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p3, active_nav='Gelombang Seleksi')
add_text(f_p3, 'P3 Title', 80, 130, 'Informasi Admisi & Gelombang Pendaftaran', font_size=40, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 Sub', 80, 178, 'Satu alur seleksi terpadu dengan pilihan periode pendaftaran bergelombang (PTS Model).', font_size=15, color_hex=C_SECONDARY_TEXT)

# Segmented Pill Waves
add_rect(f_p3, 'P3 Tab Box', 80, 230, 450, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f_p3, 'P3 Tab Act', 84, 234, 150, 40, fill_hex=C_SURFACE, radius=20)
add_text(f_p3, 'P3 Tab 1 T', 108, 245, 'Gelombang 1', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p3, 'P3 Tab 2 T', 255, 245, 'Gelombang 2', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f_p3, 'P3 Tab 3 T', 400, 245, 'Gelombang 3', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f_p3, 'P3 Detail Card', 80, 310, 560, 360, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_rect(f_p3, 'P3 Icon BG', 112, 342, 60, 60, fill_hex=C_MUTED_SURFACE, radius=14)
add_text(f_p3, 'P3 Icon T', 124, 362, 'WAVE', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p3, 'P3 CT', 112, 425, 'Gelombang 1 — Periode Early Bird', font_size=24, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 CS1', 112, 465, 'Periode pendaftaran awal dengan manfaat potongan biaya UKT.', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p3, 'P3 CS2', 112, 492, 'Batas Pendaftaran: 01 Jan s.d. 28 Feb 2026 • Kuota: 40% Daya Tampung', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f_p3, 'P3 Link', 112, 535, 'Biaya Pendaftaran: Rp 250.000 (Khusus Gelombang 1) →', font_size=12, color_hex=C_SUCCESS, font_weight='Bold')
add_rect(f_p3, 'P3 CTA', 112, 580, 220, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f_p3, 'P3 CTA T', 152, 595, 'Daftar Gelombang 1 →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_image_rect(f_p3, 'P3 Female Photo', 680, 130, 680, 560, 'real_female_student.png', radius=24)

# Panel 4 (Row 2, Col 2, X=3140, Y=1124): Applicant Dashboard (Single Program & Selected Wave)
f_p4 = add_frame(p1, 'Panel 4 — Applicant Dashboard', 3140, 1124, 1440, 1024, C_BACKGROUND)
add_rect(f_p4, 'P4 Top Nav', 0, 0, 1440, 70, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f_p4, 'P4 Logo', 80, 17, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f_p4, 'P4 Logo T', 90, 25, 'UN', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_p4, 'P4 Brand', 128, 24, 'Universitas Nusantara', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
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
add_text(f_p4, 'P4 Greet Sub', 280, 142, 'Program: S1 Teknik Informatika (Fakultas Ilmu Komputer)   •   Periode: Gelombang 1 (Early Bird)', font_size=13, color_hex=C_SECONDARY_TEXT)
add_image_rect(f_p4, 'P4 Accent', 1060, 90, 300, 85, 'real_bldg_ti.png', radius=12, opacity=0.7)

add_rect(f_p4, 'P4 Status Card', 280, 190, 1080, 320, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f_p4, 'P4 Card T', 312, 218, 'Status Pendaftaran (Proses Admisi Tunggal)', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

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
add_text(f_p4, 'P4 Succ T', 400, 376, 'Pendaftaran Berhasil Diajukan', font_size=16, color_hex='#15803d', font_weight='Bold')
add_text(f_p4, 'P4 Succ D', 400, 402, 'Pendaftaran Anda di Gelombang 1 telah tersimpan. Pantau jadwal asesmen dan pengumuman melalui portal ini.', font_size=13, color_hex='#166534')
add_text(f_p4, 'P4 Succ L', 1210, 390, 'Lihat Detail →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_p4, 'P4 Info H', 280, 545, 'Informasi Penting Gelombang 1', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_p4, 'P4 Info Card', 280, 580, 400, 90, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_rect(f_p4, 'P4 Info Ico BG', 302, 602, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
add_text(f_p4, 'P4 Info Ico T', 312, 614, 'CAL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_p4, 'P4 Info Name', 360, 604, 'Jadwal Asesmen Masuk', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p4, 'P4 Info Date', 360, 626, '05 Maret 2026', font_size=12, color_hex=C_SECONDARY_TEXT)

# Panel 5 (Row 3, Col 1, X=1600, Y=2248): Program Detail
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

# Panel 6 (Row 3, Col 2, X=3140, Y=2248): Desktop Application Form / Registration Wizard (V7 Single Program + Wave Picker)
f_p6 = add_frame(p1, 'Panel 6 — Desktop Application Form / Registration Wizard', 3140, 2248, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_p6, active_nav='Gelombang Seleksi')

add_text(f_p6, 'P6 Wizard Header', 80, 105, 'Formulir Pendaftaran Siswa Baru — Seleksi Terpadu 2026', font_size=20, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p6, 'P6 Wizard Sub', 80, 134, 'Satu alur pendaftaran terpadu: Pilih 1 Program Studi Utama dan Periode Gelombang Aktif.', font_size=13, color_hex=C_SECONDARY_TEXT)

# Stepper 5 Checkpoints
add_rect(f_p6, 'P6 Stepper BG', 80, 165, 1280, 72, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
p6_steps = [('1', 'Pilih Prodi & Gelombang', True), ('2', 'Data Pribadi', False), ('3', 'Asal Sekolah', False), ('4', 'Unggah Dokumen', False), ('5', 'Finalisasi', False)]
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
add_text(f_p6, 'P6 Step Title', 112, 285, 'Tahap 1: Pemilihan 1 Program Studi & Gelombang Pendaftaran', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_p6, 'P6 Step Sub', 112, 310, 'Pilih satu program studi utama dan periode gelombang yang sedang dibuka saat ini.', font_size=13, color_hex=C_SECONDARY_TEXT)
add_rect(f_p6, 'P6 Form Div', 112, 335, 1216, 1, fill_hex=C_BORDER)

# Two-column Inputs (V7 PTS Logic)
c1_p6 = [
    ('Pilihan Program Studi Utama (Tunggal) *', 'S1 - Teknik Informatika (Fakultas Ilmu Komputer)'),
    ('Pilihan Periode Gelombang Seleksi *', 'Gelombang 1 (Early Bird: 01 Jan - 28 Feb 2026)'),
    ('Nomor Induk Kependudukan (NIK) *', '3302192804040003 (16 digit sesuai KTP/KK)'),
    ('Nomor Induk Siswa Nasional (NISN) *', '0058291042 (10 digit terdaftar Dapodik)'),
    ('Nama Lengkap Sesuai Ijazah *', 'Muhammad Irfan (Tanpa singkatan)'),
    ('Jenis Kelamin *', 'Laki-laki (Pilihan Sesuai KTP)')
]
p6_fy = 355
for lbl, val in c1_p6:
    add_text(f_p6, f'P6 Lbl {lbl}', 112, p6_fy, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f_p6, f'P6 Inp {lbl}', 112, p6_fy + 20, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f_p6, f'P6 Val {lbl}', 128, p6_fy + 32, val, font_size=12, color_hex=C_PRIMARY_TEXT)
    p6_fy += 78

c2_p6 = [
    ('Tempat Lahir *', 'Kota Semarang'),
    ('Tanggal Lahir (DD/MM/YYYY) *', '14 / 08 / 2005'),
    ('Nomor Handphone / WhatsApp Aktif *', '081234567890'),
    ('Alamat Lengkap Domisili *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'),
    ('Kecamatan & Kelurahan *', 'Gunungpati / Sekaran'),
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
add_text(f_p6, 'P6 Btn Next T', 1080, 900, 'Simpan & Lanjut ke Dokumen →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 2: 02 — Design Foundations
# ==========================================
p2 = add_page(2, '02 — Design Foundations')
f_fnd = add_frame(p2, 'Design Foundations — Tokens & Hierarchy', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f_fnd, 'Fnd Title', 80, 60, 'Design Foundations — Strict Color Tokens & Typographic Scale', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_fnd, 'Fnd Sub', 80, 102, 'Sistem token desain resmi PMB 2026 PTS yang menjadi acuan konsistensi seluruh 15 halaman.', font_size=15, color_hex=C_SECONDARY_TEXT)

colors_v7 = [
    ('Primary Blue', '#1554B8', C_SURFACE),
    ('Primary Hover', '#10469B', C_SURFACE),
    ('Accent Blue', '#3689F5', C_SURFACE),
    ('Background', '#F7F9FD', C_PRIMARY_TEXT),
    ('Surface', '#FFFFFF', C_PRIMARY_TEXT),
    ('Muted Surface', '#EEF2FA', C_PRIMARY_TEXT),
    ('Primary Text', '#101A32', C_SURFACE),
    ('Secondary Text', '#63718A', C_SURFACE),
    ('Border', '#DFE6F2', C_PRIMARY_TEXT),
    ('Success Green', '#20A878', C_SURFACE),
    ('Warning Yellow', '#F2BF55', C_PRIMARY_TEXT),
    ('Error Red', '#D94A55', C_SURFACE)
]
cx = 80
cy = 180
for i, (cname, chex, ctxt) in enumerate(colors_v7):
    add_rect(f_fnd, f'Sw BG {cname}', cx, cy, 105, 110, fill_hex=chex, stroke_hex=C_BORDER, radius=12)
    add_text(f_fnd, f'Sw Name {cname}', cx + 8, cy + 68, cname, font_size=10, color_hex=ctxt, font_weight='Bold')
    add_text(f_fnd, f'Sw Hex {cname}', cx + 8, cy + 86, chex, font_size=11, color_hex=ctxt)
    cx += 116
    if (i + 1) % 6 == 0:
        cx = 80
        cy += 125

# Typography Scale
tscales = [
    ('Hero Title (54px Bold)', 'Gerbang Menuju Perguruan Tinggi Swasta Unggulan', 54, 'Bold'),
    ('Page Title (40px Bold)', 'Formulir Pendaftaran Siswa & Pilihan Gelombang', 40, 'Bold'),
    ('Section Title (32px Bold)', 'Pilihan Program Studi & Daya Tampung Kelas 2026', 32, 'Bold'),
    ('Card Title (18px Semibold)', 'S1 Teknik Informatika — Akreditasi Unggul', 18, 'Bold'),
    ('Body Text (15px Regular)', 'Wujudkan impian studi dengan proses seleksi digital terintegrasi, transparan, dan terpercaya.', 15, 'Regular'),
    ('Supporting Label (12px Medium)', 'NOMOR INDUK KEPENDUDUKAN (NIK) SESUAI KTP / KK RESMI *', 12, 'Bold')
]
ty2 = 495
for tscale, tex, tsz, twg in tscales:
    add_text(f_fnd, f'TLbl {tscale}', 80, ty2, tscale, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_fnd, f'TEx {tscale}', 320, ty2, tex, font_size=tsz, color_hex=C_PRIMARY_TEXT, font_weight=twg)
    ty2 += int(tsz * 1.5) + 12

# Spacing System
add_text(f_fnd, 'Spc Header', 80, 890, 'SPACING SYSTEM (4px BASELINE LADDER)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
spx = 80
for sp in [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80]:
    add_rect(f_fnd, f'SpcBox {sp}', spx, 920, sp, sp, fill_hex=C_PRIMARY, radius=2)
    add_text(f_fnd, f'SpcTxt {sp}', spx, 920 + sp + 8, f'{sp}px', font_size=10, color_hex=C_SECONDARY_TEXT)
    spx += max(sp + 14, 38)

# ==========================================
# PAGE 3: 03 — Design System & Components
# ==========================================
p3 = add_page(3, '03 — Design System & Components')
f_sys = add_frame(p3, 'Design System & Component Library', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f_sys, 'Sys Title', 80, 60, 'Pustaka Komponen UI & Status Variants (V7 Master)', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_sys, 'Sys Sub', 80, 102, 'Komponen pill-shaped, form input, dan 21 status badge pendaftaran resmi PTS.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Buttons
add_rect(f_sys, 'Btn 1', 80, 180, 200, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f_sys, 'Btn 1 T', 125, 195, 'Primary Default', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f_sys, 'Btn 2', 300, 180, 200, 48, fill_hex=C_PRIMARY_HOVER, radius=24)
add_text(f_sys, 'Btn 2 T', 345, 195, 'Primary Hover', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f_sys, 'Btn 3', 520, 180, 200, 48, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=24)
add_text(f_sys, 'Btn 3 T', 565, 195, 'Secondary Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_sys, 'Btn 4', 740, 180, 200, 48, fill_hex=C_WARNING, radius=24)
add_text(f_sys, 'Btn 4 T', 785, 195, 'Amber Accent Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_sys, 'Btn 5', 960, 180, 160, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_text(f_sys, 'Btn 5 T', 1005, 195, 'Ghost Pill', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# 21 Status Badges (V7 Section 17)
add_text(f_sys, 'Badge H', 80, 260, '2. APPLICATION STATUS VARIANTS (21 REQUIRED STATES - V7 SECTION 17)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
status_21 = [
    ('Draft', C_MUTED_SURFACE, C_BORDER, C_SECONDARY_TEXT),
    ('Profile Incomplete', '#fffbeb', '#fde68a', '#b45309'),
    ('Documents Incomplete', '#fffbeb', '#fde68a', '#b45309'),
    ('Documents Pending Review', '#fef3c7', '#fde68a', '#b45309'),
    ('Correction Required', '#fff1f2', '#fecdd3', C_ERROR),
    ('Documents Approved', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Payment Pending', '#fffbeb', '#fde68a', '#b45309'),
    ('Payment Verified', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Application Submitted', '#f0f9ff', '#bae6fd', C_PRIMARY),
    ('Under Review', '#fef3c7', '#fde68a', '#b45309'),
    ('Assessment Scheduled', '#f0f9ff', '#bae6fd', C_PRIMARY),
    ('Assessment Completed', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Final Evaluation', '#fef3c7', '#fde68a', '#b45309'),
    ('Result Pending', '#fef3c7', '#fde68a', '#b45309'),
    ('Accepted', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Not Accepted', '#fff1f2', '#fecdd3', C_ERROR),
    ('Waitlisted', '#fffbeb', '#fde68a', '#b45309'),
    ('Acceptance Confirmed', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Re-registration Pending', '#fffbeb', '#fde68a', '#b45309'),
    ('Re-registration Completed', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Admission Completed', '#ecfdf5', '#a7f3d0', C_SUCCESS)
]
sbx = 80
sby = 295
for i, (stxt, sbg, sbrd, scol) in enumerate(status_21):
    bw = len(stxt) * 8 + 32
    add_rect(f_sys, f'StBadge {stxt}', sbx, sby, bw, 32, fill_hex=sbg, stroke_hex=sbrd, radius=16)
    add_text(f_sys, f'StTxt {stxt}', sbx + 16, sby + 8, stxt, font_size=11, color_hex=scol, font_weight='Bold')
    sbx += bw + 14
    if (i + 1) % 5 == 0:
        sbx = 80
        sby += 46

print('Pages 1-3 built!')
