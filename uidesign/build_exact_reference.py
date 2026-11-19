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

# Exact Reference Master Colors
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

FONT_FAMILY = "Plus Jakarta Sans"

doc = {
    'comments': [],
    'current_page': 1,
    'document_colors': [],
    'format': 'figcraft',
    'imageIndex': image_index,
    'name': 'PMB 2026 — Modern University Admission Platform',
    'next_id': 100,
    'nodes': {
        '1': {
            'background': {'a': 1.0, 'r': 0.9686, 'g': 0.9765, 'b': 0.9922}, # F7F9FD
            'children': [],
            'flows': [],
            'height': 0.0,
            'id': 1,
            'name': 'Page 1',
            'prototype': {'background': {'a': 1.0, 'r': 0.9686, 'g': 0.9765, 'b': 0.9922}, 'device': 'None', 'rotation': 'portrait'},
            'type': 'page',
            'width': 0.0
        }
    },
    'pages': [1],
    'styles': [],
    'variables': []
}

def alloc_id():
    cur = doc['next_id']
    doc['next_id'] += 1
    return cur

def add_frame(name, x, y, w=1440.0, h=1024.0, bg_hex=C_BACKGROUND):
    fid = alloc_id()
    doc['nodes'][str(fid)] = {
        'children': [],
        'clip': True,
        'fills': [{'blend': 'normal', 'color': hex_to_rgb(bg_hex), 'opacity': 1.0, 'type': 'solid', 'visible': True}],
        'height': float(h),
        'id': fid,
        'name': name,
        'parent': 1,
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'frame',
        'width': float(w)
    }
    doc['nodes']['1']['children'].append(fid)
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

# ==========================================
# 01. BERANDA — HERO & PORTAL PMB 2026 (X = 0)
# ==========================================
f1 = add_frame('01. Beranda — Hero & Portal PMB 2026', 0.0, 0.0)

# Navbar (h: 76)
add_rect(f1, 'F1 Nav BG', 0, 0, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f1, 'F1 Logo Icon', 80, 20, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f1, 'F1 Logo Txt', 90, 28, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f1, 'F1 Brand Name', 128, 26, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

nav_items1 = ['Beranda', 'Program Studi ⌵', 'Jalur Masuk ⌵', 'Informasi ⌵']
nx1 = 520
for ni in nav_items1:
    add_text(f1, f'F1 Nav {ni}', nx1, 28, ni, font_size=13, color_hex=C_PRIMARY_TEXT if ni=='Beranda' else C_SECONDARY_TEXT, font_weight='Bold' if ni=='Beranda' else 'Regular')
    nx1 += 130

add_text(f1, 'F1 Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)

# Pill Button
add_rect(f1, 'F1 Btn Daftar Top', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f1, 'F1 Btn Daftar Top Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Hero Content Left (x: 80, y: 140)
add_text(f1, 'F1 Hero Line 1', 80, 150, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f1, 'F1 Hero Line 2', 80, 215, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f1, 'F1 Hero Line 3', 80, 280, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f1, 'F1 Hero Sub 1', 80, 360, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f1, 'F1 Hero Sub 2', 80, 385, 'bersama Universitas Indonesia.', font_size=16, color_hex=C_SECONDARY_TEXT)

# Hero CTA Buttons
add_rect(f1, 'F1 Hero Btn Prim', 80, 435, 185, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f1, 'F1 Hero Btn Prim Txt', 110, 449, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_text(f1, 'F1 Hero Video Btn', 290, 449, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Right Hero Photo (Authentic Students Looking Upwards)
add_image_rect(f1, 'F1 Real Hero Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)

# Floating Bottom White Ribbon Bar (x: 80, y: 680, w: 1280, h: 96)
add_rect(f1, 'F1 Ribbon BG', 80, 680, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)

ribbon_items = [
    ('Periode Pendaftaran', '3 Jan - 30 Jun 2026', 'CAL', 120),
    ('Jalur Seleksi', 'SNBP, SNBT, Mandiri', 'CAP', 440),
    ('Program Studi', '100+ Pilihan', 'BOK', 760),
    ('Beasiswa', 'Hingga 100%', 'GFT', 1060)
]
for rlbl, rval, rico, rx in ribbon_items:
    add_rect(f1, f'F1 RIco BG {rico}', rx, 706, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f1, f'F1 RIco Txt {rico}', rx + 10, 719, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f1, f'F1 RLbl {rlbl}', rx + 56, 710, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f1, f'F1 RVal {rval}', rx + 56, 730, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# ==========================================
# 02. PROGRAM STUDI — DISCOVERY & FILTER (X = 1540)
# ==========================================
f2 = add_frame('02. Program Studi — Discovery & Filter', 1540.0, 0.0)

# Top Bar
add_rect(f2, 'F2 Nav BG', 0, 0, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f2, 'F2 Logo Icon', 80, 20, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f2, 'F2 Logo Txt', 90, 28, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f2, 'F2 Brand Name', 128, 26, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

nav_items2 = ['Beranda', 'Program Studi ⌵', 'Jalur Masuk ⌵', 'Informasi ⌵']
nx2 = 520
for ni in nav_items2:
    add_text(f2, f'F2 Nav {ni}', nx2, 28, ni, font_size=13, color_hex=C_PRIMARY if 'Program Studi' in ni else C_SECONDARY_TEXT, font_weight='Bold' if 'Program Studi' in ni else 'Regular')
    nx2 += 130

add_text(f2, 'F2 Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)
add_rect(f2, 'F2 Btn Daftar Top', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f2, 'F2 Btn Daftar Top Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Section Header
add_text(f2, 'F2 Title', 80, 120, 'Program Studi', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f2, 'F2 Sub', 80, 168, 'Temukan program studi yang sesuai dengan minat dan bakatmu.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Top Right Faculty Campus Photo
add_image_rect(f2, 'F2 Bldg Hero Photo', 780, 105, 580, 220, 'real_bldg_hero.png', radius=18)

# Search Input Box with Icon
add_rect(f2, 'F2 Search Inp', 80, 215, 480, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f2, 'F2 Search Icon Inp', 102, 228, '🔍', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f2, 'F2 Search Placeholder', 130, 228, 'Cari program studi...', font_size=13, color_hex=C_SECONDARY_TEXT)

# Filter Pills Row
filter_pills = [
    ('Semua', True),
    ('Fakultas ⌵', False),
    ('Jenjang ⌵', False),
    ('Akreditasi ⌵', False)
]
fpx = 80
for ptxt, pact in filter_pills:
    pbg = C_PRIMARY if pact else C_SURFACE
    ptcol = C_SURFACE if pact else C_PRIMARY_TEXT
    pw = len(ptxt) * 9 + 30
    add_rect(f2, f'F2 Pill {ptxt}', fpx, 280, pw, 38, fill_hex=pbg, stroke_hex=None if pact else C_BORDER, radius=19)
    add_text(f2, f'F2 PillTxt {ptxt}', fpx + 15, 290, ptxt, font_size=12, color_hex=ptcol, font_weight='Bold' if pact else 'Regular')
    fpx += pw + 12

add_text(f2, 'F2 See All', 1210, 290, 'Lihat Semua Program →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# 3 Program Cards Grid
cards_data = [
    ('Teknik Informatika', 'Fakultas Ilmu Komputer', 'S1', 'Akreditasi Unggul', 'real_bldg_ti.png', 80),
    ('Manajemen', 'Fakultas Ekonomi & Bisnis', 'S1', 'Akreditasi Unggul', 'real_bldg_mn.png', 520),
    ('Psikologi', 'Fakultas Psikologi', 'S1', 'Akreditasi A', 'real_bldg_ps.png', 960)
]
for ctitle, cfac, cdeg, cakred, cimg, cx in cards_data:
    add_rect(f2, f'F2 CardBG {ctitle}', cx, 360, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_image_rect(f2, f'F2 CardImg {ctitle}', cx, 360, 400, 185, cimg, radius=[18, 18, 0, 0])
    
    add_text(f2, f'F2 CardTitle {ctitle}', cx + 22, 565, ctitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f2, f'F2 CardFac {ctitle}', cx + 22, 592, cfac, font_size=13, color_hex=C_SECONDARY_TEXT)
    add_text(f2, f'F2 CardDeg {ctitle}', cx + 22, 612, cdeg, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    
    # Accreditation Pill
    add_rect(f2, f'F2 AkredPill {ctitle}', cx + 22, 642, 135, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
    add_text(f2, f'F2 AkredTxt {ctitle}', cx + 36, 648, f'● {cakred}', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    
    # Arrow Button
    add_rect(f2, f'F2 ArrowCircle {ctitle}', cx + 340, 638, 36, 36, fill_hex=C_MUTED_SURFACE, radius=18)
    add_text(f2, f'F2 ArrowTxt {ctitle}', cx + 352, 646, '→', font_size=15, color_hex=C_PRIMARY, font_weight='Bold')

# ==========================================
# 03. JALUR MASUK — SNBP, SNBT, MANDIRI (X = 3080)
# ==========================================
f3 = add_frame('03. Jalur Masuk — SNBP, SNBT, Mandiri', 3080.0, 0.0)

# Top Bar
add_rect(f3, 'F3 Nav BG', 0, 0, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f3, 'F3 Logo Icon', 80, 20, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f3, 'F3 Logo Txt', 90, 28, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f3, 'F3 Brand Name', 128, 26, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

nav_items3 = ['Beranda', 'Program Studi ⌵', 'Jalur Masuk ⌵', 'Informasi ⌵']
nx3 = 520
for ni in nav_items3:
    add_text(f3, f'F3 Nav {ni}', nx3, 28, ni, font_size=13, color_hex=C_PRIMARY if 'Jalur Masuk' in ni else C_SECONDARY_TEXT, font_weight='Bold' if 'Jalur Masuk' in ni else 'Regular')
    nx3 += 130

add_text(f3, 'F3 Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)
add_rect(f3, 'F3 Btn Daftar Top', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f3, 'F3 Btn Daftar Top Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Title Header
add_text(f3, 'F3 Title', 80, 130, 'Jalur Masuk', font_size=40, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f3, 'F3 Sub', 80, 178, 'Pilih jalur seleksi yang sesuai denganmu.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Segmented Pill Tabs
add_rect(f3, 'F3 Tab Container', 80, 230, 420, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f3, 'F3 Tab Active', 84, 234, 136, 40, fill_hex=C_SURFACE, radius=20)
add_text(f3, 'F3 Tab 1 Txt', 132, 245, 'SNBP', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f3, 'F3 Tab 2 Txt', 270, 245, 'SNBT', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f3, 'F3 Tab 3 Txt', 405, 245, 'Mandiri', font_size=13, color_hex=C_SECONDARY_TEXT)

# Active Card Detail
add_rect(f3, 'F3 Detail Card BG', 80, 310, 560, 360, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_rect(f3, 'F3 Icon BG', 112, 342, 60, 60, fill_hex=C_MUTED_SURFACE, radius=14)
add_text(f3, 'F3 Icon Txt', 128, 362, 'SNBP', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f3, 'F3 Card Title', 112, 425, 'SNBP', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f3, 'F3 Card Sub 1', 112, 465, 'Seleksi Nasional Berdasarkan Prestasi', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f3, 'F3 Card Sub 2', 112, 492, 'untuk siswa berprestasi akademik dan non-akademik.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_text(f3, 'F3 Learn More', 112, 535, 'Pelajari Selengkapnya →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f3, 'F3 Card CTA', 112, 580, 220, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f3, 'F3 Card CTA Txt', 152, 595, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Right Hero Photo: Smiling Female Student
add_image_rect(f3, 'F3 Female Student Photo', 680, 130, 680, 560, 'real_female_student.png', radius=24)

# ==========================================
# 04. DASHBOARD PENDAFTAR — STATUS & STEPPER (X = 4620)
# ==========================================
f4 = add_frame('04. Dashboard Pendaftar — Status & Stepper', 4620.0, 0.0)

# Top Bar with User Avatar & Notification
add_rect(f4, 'F4 Top Nav BG', 0, 0, 1440, 70, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f4, 'F4 Logo Icon', 80, 17, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f4, 'F4 Logo Txt', 90, 25, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f4, 'F4 Brand Name', 128, 24, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_text(f4, 'F4 Notif Bell', 1260, 25, '🔔', font_size=16, color_hex=C_SECONDARY_TEXT)
add_image_rect(f4, 'F4 User Avatar', 1300, 16, 38, 38, 'student_id_photo.jpg', radius=19)

# Sidebar Left
add_rect(f4, 'F4 Side BG', 0, 70, 240, 930, fill_hex=C_SURFACE, stroke_hex=C_BORDER)

sidebar_items = [
    ('Dashboard', True),
    ('Profil', False),
    ('Pendaftaran', False),
    ('Dokumen', False),
    ('Pembayaran', False),
    ('Seleksi', False),
    ('Notifikasi', False),
    ('Keluar', False)
]
sby = 100
for sitem, sactive in sidebar_items:
    if sactive:
        add_rect(f4, f'F4 SActiveBar {sitem}', 0, sby, 4, 40, fill_hex=C_PRIMARY)
        add_rect(f4, f'F4 SActivePill {sitem}', 16, sby, 208, 40, fill_hex=C_MUTED_SURFACE, radius=8)
    
    add_text(f4, f'F4 SItem {sitem}', 40, sby + 11, sitem, font_size=13, color_hex=C_PRIMARY if sactive else C_SECONDARY_TEXT, font_weight='Bold' if sactive else 'Regular')
    sby += 46

# Main Dashboard Workspace (x: 270)
add_text(f4, 'F4 Greet', 280, 105, 'Halo, Andi Pratama 👋', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4, 'F4 Greet Sub', 280, 142, 'Selamat datang di dashboard pendaftaran PMB 2026', font_size=14, color_hex=C_SECONDARY_TEXT)

# Top Right Campus Header Illustration/Photo
add_image_rect(f4, 'F4 Dash Accent Photo', 1060, 90, 300, 85, 'real_bldg_ti.png', radius=12, opacity=0.7)

# Main Card: Status Pendaftaran (w: 1080, h: 320)
add_rect(f4, 'F4 Status Card BG', 280, 190, 1080, 320, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f4, 'F4 Status Card Title', 312, 218, 'Status Pendaftaran', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Stepper Checkpoints
dash_stepper = [
    ('Data Diri', True),
    ('Dokumen', True),
    ('Pembayaran', True),
    ('Seleksi', False),
    ('Hasil', False)
]
stx4 = 340
for i, (stitle, sdone) in enumerate(dash_stepper):
    c_fill = C_PRIMARY if sdone else C_MUTED_SURFACE
    c_txt = C_SURFACE if sdone else C_SECONDARY_TEXT
    c_sym = '✓' if sdone else ''
    
    add_rect(f4, f'F4 StepNode {stitle}', stx4, 260, 32, 32, fill_hex=c_fill, radius=16)
    if c_sym:
        add_text(f4, f'F4 StepSym {stitle}', stx4 + 10, 268, c_sym, font_size=12, color_hex=c_txt, font_weight='Bold')
    
    add_text(f4, f'F4 StepTxt {stitle}', stx4 - 15, 302, stitle, font_size=12, color_hex=C_PRIMARY_TEXT if sdone else C_SECONDARY_TEXT, font_weight='Bold' if sdone else 'Regular')
    
    if i < 4:
        add_rect(f4, f'F4 StepLine {i}', stx4 + 40, 275, 150, 2, fill_hex=C_PRIMARY if i < 2 else C_BORDER)
    stx4 += 190

# Green Success Banner Inside Card
add_rect(f4, 'F4 Success Banner BG', 312, 350, 1016, 120, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=14)
add_rect(f4, 'F4 Success Icon Circle', 336, 375, 48, 48, fill_hex=C_SUCCESS, radius=24)
add_text(f4, 'F4 Success Checkmark', 352, 388, '✓', font_size=18, color_hex=C_SURFACE, font_weight='Bold')

add_text(f4, 'F4 Success Title', 400, 376, 'Pendaftaran Berhasil', font_size=16, color_hex='#15803d', font_weight='Bold')
add_text(f4, 'F4 Success Desc', 400, 402, 'Terima kasih telah mendaftar. Pantau terus informasi terbaru melalui halaman ini.', font_size=13, color_hex='#166534')

add_text(f4, 'F4 Detail Link', 1210, 390, 'Lihat Detail →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Important Info Section Below
add_text(f4, 'F4 Info Title', 280, 545, 'Informasi Penting', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4, 'F4 Info See All', 1280, 545, 'Lihat Semua →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Info Card
add_rect(f4, 'F4 Info Card BG', 280, 580, 400, 90, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_rect(f4, 'F4 Info Icon BG', 302, 602, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
add_text(f4, 'F4 Info Icon Txt', 312, 614, 'CAL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f4, 'F4 Info Name', 360, 604, 'Jadwal Seleksi', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4, 'F4 Info Date', 360, 626, '25 Jun 2026', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# 05. DETAIL PROGRAM STUDI — KURIKULUM & OVERVIEW (X = 6160)
# ==========================================
f5 = add_frame('05. Detail Program Studi — Kurikulum & Overview', 6160.0, 0.0)

# Top Bar
add_rect(f5, 'F5 Nav BG', 0, 0, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f5, 'F5 Logo Icon', 80, 20, 36, 36, fill_hex=C_PRIMARY, radius=8)
add_text(f5, 'F5 Logo Txt', 90, 28, 'UI', font_size=15, color_hex=C_SURFACE, font_weight='Bold')
add_text(f5, 'F5 Brand Name', 128, 26, 'Universitas Indonesia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

nav_items5 = ['Beranda', 'Program Studi ⌵', 'Jalur Masuk ⌵', 'Informasi ⌵']
nx5 = 520
for ni in nav_items5:
    add_text(f5, f'F5 Nav {ni}', nx5, 28, ni, font_size=13, color_hex=C_PRIMARY if 'Program Studi' in ni else C_SECONDARY_TEXT, font_weight='Bold' if 'Program Studi' in ni else 'Regular')
    nx5 += 130

add_text(f5, 'F5 Search Icon', 1080, 28, '🔍', font_size=14, color_hex=C_SECONDARY_TEXT)
add_rect(f5, 'F5 Btn Daftar Top', 1140, 16, 160, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f5, 'F5 Btn Daftar Top Txt', 1172, 28, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Breadcrumb
add_text(f5, 'F5 Back Link', 80, 110, '← Kembali ke Program Studi', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Hero Faculty Detail Banner (x: 80, y: 140, w: 1280, h: 320)
add_image_rect(f5, 'F5 Bldg Photo', 80, 140, 460, 300, 'real_bldg_detail.png', radius=18)

# Right of Photo: Program Info Header
add_text(f5, 'F5 Major Title', 580, 160, 'Teknik Informatika', font_size=36, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f5, 'F5 Major Fac', 580, 210, 'Fakultas Ilmu Komputer', font_size=16, color_hex=C_SECONDARY_TEXT)

# Accreditation Pill
add_rect(f5, 'F5 Akred Pill', 580, 245, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f5, 'F5 Akred Pill Txt', 594, 251, '● Akreditasi Unggul', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

add_text(f5, 'F5 Major Desc 1', 580, 290, 'Program studi Teknik Informatika membekali mahasiswa dengan kompetensi', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f5, 'F5 Major Desc 2', 580, 312, 'di bidang teknologi informasi, rekayasa perangkat lunak, dan kecerdasan buatan.', font_size=14, color_hex=C_SECONDARY_TEXT)

# Pill Buttons
add_rect(f5, 'F5 Btn Daftar', 580, 360, 180, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f5, 'F5 Btn Daftar Txt', 612, 374, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f5, 'F5 Btn Kurikulum', 780, 360, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f5, 'F5 Btn Kurikulum Txt', 812, 374, 'Lihat Kurikulum', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Navigation Tabs Below (x: 80, y: 480)
detail_tabs = ['Overview', 'Kurikulum', 'Prospek Karir', 'Persyaratan']
dtx = 80
for dti in detail_tabs:
    is_act = (dti == 'Overview')
    add_text(f5, f'F5 DTab {dti}', dtx, 490, dti, font_size=14, color_hex=C_PRIMARY if is_act else C_SECONDARY_TEXT, font_weight='Bold' if is_act else 'Regular')
    if is_act:
        add_rect(f5, 'F5 DTab Line', dtx, 520, 65, 3, fill_hex=C_PRIMARY)
    dtx += 140

add_rect(f5, 'F5 Tabs Div Line', 80, 523, 1280, 1, fill_hex=C_BORDER)

# Detail Body Content
add_text(f5, 'F5 About Title', 80, 555, 'Tentang Program Studi', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f5, 'F5 About Desc 1', 80, 590, 'Teknik Informatika berfokus pada pengembangan teknologi digital, perancangan algoritma efisien, sistem cerdas,', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f5, 'F5 About Desc 2', 80, 614, 'serta infrastruktur komputasi awan untuk masa depan yang lebih baik.', font_size=14, color_hex=C_SECONDARY_TEXT)

# Right Sidebar Box: Informasi Program
add_rect(f5, 'F5 Prog Info Box', 880, 555, 480, 180, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f5, 'F5 Prog Info Title', 905, 580, 'Informasi Program', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f5, 'F5 Prog Info Div', 905, 608, 430, 1, fill_hex=C_BORDER)
add_text(f5, 'F5 Jenjang Lbl', 905, 625, 'Jenjang:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f5, 'F5 Jenjang Val', 905, 645, 'Sarjana (S1)', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_text(f5, 'F5 Fac Lbl', 1120, 625, 'Fakultas:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f5, 'F5 Fac Val', 1120, 645, 'Ilmu Komputer', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# ==========================================
# 06. MOBILE — BERANDA PORTAL PMB (390 × 844) (X = 7700)
# ==========================================
f6 = add_frame('06. Mobile — Beranda Portal PMB (390 × 844)', 7700.0, 0.0, 390.0, 844.0)

# Mobile Nav
add_rect(f6, 'M1 Nav BG', 0, 0, 390, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f6, 'M1 Logo Icon', 20, 18, 28, 28, fill_hex=C_PRIMARY, radius=6)
add_text(f6, 'M1 Logo Txt', 26, 23, 'UI', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_text(f6, 'M1 Brand', 56, 23, 'Universitas Indonesia', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6, 'M1 Hamburger', 345, 23, '☰', font_size=16, color_hex=C_PRIMARY_TEXT)

# Mobile Hero
add_text(f6, 'M1 Hero 1', 20, 95, 'Penerimaan', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6, 'M1 Hero 2', 20, 130, 'Mahasiswa Baru', font_size=28, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6, 'M1 Hero 3', 20, 165, '2026', font_size=28, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f6, 'M1 Sub 1', 20, 205, 'Wujudkan mimpi, raih masa depan', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f6, 'M1 Sub 2', 20, 225, 'bersama Universitas Indonesia.', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f6, 'M1 Btn', 20, 260, 350, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f6, 'M1 Btn Txt', 125, 273, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_image_rect(f6, 'M1 Photo', 20, 325, 350, 240, 'real_hero_students.png', radius=16)

# Mobile Ribbon Card
add_rect(f6, 'M1 Rib BG', 20, 585, 350, 210, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
m_ribbon = [
    ('Periode Pendaftaran', '3 Jan - 30 Jun 2026', 605),
    ('Jalur Seleksi', 'SNBP, SNBT, Mandiri', 655),
    ('Program Studi', '100+ Pilihan Program', 705),
    ('Beasiswa', 'Hingga 100% Bebas Biaya', 755)
]
for mlbl, mval, my in m_ribbon:
    add_text(f6, f'M1 RLbl {mlbl}', 40, my, mlbl, font_size=10, color_hex=C_SECONDARY_TEXT)
    add_text(f6, f'M1 RVal {mlbl}', 40, my + 14, mval, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# ==========================================
# 07. MOBILE — PROGRAM STUDI DISCOVERY (390 × 844) (X = 8130)
# ==========================================
f7 = add_frame('07. Mobile — Program Studi Discovery (390 × 844)', 8130.0, 0.0, 390.0, 844.0)

# Mobile Nav
add_rect(f7, 'M2 Nav BG', 0, 0, 390, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f7, 'M2 Title', 20, 23, 'Program Studi', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7, 'M2 Hamburger', 345, 23, '☰', font_size=16, color_hex=C_PRIMARY_TEXT)

# Search
add_rect(f7, 'M2 Search', 20, 85, 350, 42, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=21)
add_text(f7, 'M2 Search Txt', 40, 97, '🔍  Cari program studi...', font_size=12, color_hex=C_SECONDARY_TEXT)

# Pills
add_rect(f7, 'M2 P1', 20, 140, 85, 32, fill_hex=C_PRIMARY, radius=16)
add_text(f7, 'M2 P1 T', 45, 148, 'Semua', font_size=11, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f7, 'M2 P2', 115, 140, 105, 32, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f7, 'M2 P2 T', 135, 148, 'Fakultas ⌵', font_size=11, color_hex=C_PRIMARY_TEXT)

# Program Card 1
add_rect(f7, 'M2 Card 1', 20, 195, 350, 290, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_image_rect(f7, 'M2 C1 Img', 20, 195, 350, 150, 'real_bldg_ti.png', radius=[16, 16, 0, 0])
add_text(f7, 'M2 C1 T', 36, 360, 'Teknik Informatika', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7, 'M2 C1 F', 36, 384, 'Fakultas Ilmu Komputer • S1', font_size=12, color_hex=C_SECONDARY_TEXT)
add_rect(f7, 'M2 C1 Akred', 36, 412, 130, 26, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=13)
add_text(f7, 'M2 C1 AkredTxt', 48, 418, '● Akreditasi Unggul', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')

# Program Card 2 Preview
add_rect(f7, 'M2 Card 2', 20, 505, 350, 290, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_image_rect(f7, 'M2 C2 Img', 20, 505, 350, 150, 'real_bldg_mn.png', radius=[16, 16, 0, 0])
add_text(f7, 'M2 C2 T', 36, 670, 'Manajemen', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7, 'M2 C2 F', 36, 694, 'Fakultas Ekonomi & Bisnis • S1', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# 08. MOBILE — DASHBOARD PENDAFTAR (390 × 844) (X = 8560)
# ==========================================
f8 = add_frame('08. Mobile — Dashboard Pendaftar (390 × 844)', 8560.0, 0.0, 390.0, 844.0)

# Mobile Nav
add_rect(f8, 'M3 Nav BG', 0, 0, 390, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8, 'M3 Title', 20, 23, 'Dashboard', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8, 'M3 Hamburger', 345, 23, '☰', font_size=16, color_hex=C_PRIMARY_TEXT)

add_text(f8, 'M3 Greet', 20, 95, 'Halo, Andi Pratama 👋', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Stepper Card
add_rect(f8, 'M3 Card', 20, 135, 350, 310, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8, 'M3 Card T', 36, 155, 'Status Pendaftaran', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Stepper line
m_steps = [('Data Diri', True), ('Dokumen', True), ('Pembayaran', True)]
msx = 55
for sn, sa in m_steps:
    add_rect(f8, f'M3 SN {sn}', msx, 190, 26, 26, fill_hex=C_PRIMARY, radius=13)
    add_text(f8, f'M3 SN Txt {sn}', msx + 8, 196, '✓', font_size=10, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f8, f'M3 S Lbl {sn}', msx - 8, 222, sn, font_size=10, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    if sn != 'Pembayaran':
        add_rect(f8, f'M3 Line {sn}', msx + 30, 202, 70, 2, fill_hex=C_PRIMARY)
# Success Banner
add_rect(f8, 'M3 Succ BG', 36, 260, 318, 70, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=12)
add_text(f8, 'M3 Succ T', 52, 274, '✓  Pendaftaran Berhasil', font_size=13, color_hex='#15803d', font_weight='Bold')
add_text(f8, 'M3 Succ D', 52, 296, 'Terima kasih telah mendaftar.', font_size=11, color_hex='#166534')
add_text(f8, 'M3 Succ L', 255, 285, 'Lihat Detail →', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

# Informasi Penting on Mobile
add_text(f8, 'M3 Info H', 20, 470, 'Informasi Penting', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f8, 'M3 Info Card', 20, 500, 350, 80, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_rect(f8, 'M3 Info Icon', 36, 518, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
add_text(f8, 'M3 Info Icon T', 46, 530, 'CAL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8, 'M3 Info T', 92, 520, 'Jadwal Seleksi', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8, 'M3 Info D', 92, 542, '25 Jun 2026', font_size=12, color_hex=C_SECONDARY_TEXT)

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/pmb-ui-concept.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack directly into .figcraft zip
zip_path = 'C:/projects/ta-pemweb/uidesign/pmb-ui-concept.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully built master exact reference file {zip_path} with {len(doc["nodes"])} nodes across {len(doc["nodes"]["1"]["children"])} frames!')
