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

# Exact Master V8.0 Colors
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
    'current_page': 0,
    'document_colors': [],
    'format': 'figcraft',
    'imageIndex': image_index,
    'name': 'PMB 2026 - Private University Admission Platform (v8.0 FINAL)',
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
        'background': {'a': 1.0, 'r': 0.9686, 'g': 0.9765, 'b': 0.9922},
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
    
    navs = ['Beranda', 'Program Studi ⌵', 'Informasi Admisi ⌵', 'Gelombang Pendaftaran ⌵', 'Biaya & Beasiswa']
    nx = 460
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

print('V8.0 Master Base Setup Complete.')

# ==========================================
# PAGE 00: 00 - Project Overview
# ==========================================
p0 = add_page(0, '00 - Project Overview')
f0 = add_frame(p0, 'Project Overview & Executive Summary', 0, 0, 1440, 1024, C_BACKGROUND)

add_rect(f0, 'P0 Hero BG', 80, 80, 1280, 480, fill_hex=C_PRIMARY, radius=24)
add_image_rect(f0, 'P0 Hero Photo', 80, 80, 1280, 480, 'hero_campus.jpg', radius=24, opacity=0.35)

add_rect(f0, 'P0 Tag Pill', 120, 120, 310, 32, fill_hex=C_SURFACE, radius=16)
add_text(f0, 'P0 Tag Txt', 140, 128, 'MASTER FIGMA DESIGN V8.0 FINAL', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f0, 'P0 Title 1', 120, 175, 'PMB 2026 — Private University', font_size=46, color_hex=C_SURFACE, font_weight='Bold')
add_text(f0, 'P0 Title 2', 120, 235, 'Admission Platform (PTS)', font_size=46, color_hex=C_WARNING, font_weight='Bold')

add_text(f0, 'P0 Desc 1', 120, 305, 'Single Admission Process · Multiple Registration Waves (Gelombang 1, 2, 3) · Single Primary Program Selection.', font_size=15, color_hex=C_MUTED_SURFACE)
add_text(f0, 'P0 Desc 2', 120, 330, 'Complete 19 Pages Architecture · 48 Defined Routes · Desktop Web Only · Applicant Role Only.', font_size=15, color_hex=C_MUTED_SURFACE)

# Meta Box
add_rect(f0, 'P0 Meta Box', 120, 385, 1200, 130, fill_hex=C_SURFACE, radius=16)
cmetas_v8 = [
    ('INSTITUTION TYPE', 'Private University (PTS) Model'),
    ('ADMISSION MODEL', 'Single Process • Multiple Waves'),
    ('PROGRAM SELECTION', 'Single Primary Choice (100% Focused)'),
    ('SCOPE RESTRICTION', 'Zero Mobile • Zero Admin Bleed')
]
cmx8 = 150
for clbl, cval in cmetas_v8:
    add_text(f0, f'P0 Lbl {clbl}', cmx8, 415, clbl, font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
    add_text(f0, f'P0 Val {clbl}', cmx8, 440, cval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    cmx8 += 280

# 3 Pillars
pillars_v8 = [
    ('Single Unified Admission', 'Satu proses seleksi admisi terpadu tanpa pemecahan jalur ganda; calon mahasiswa mengikuti alur seleksi yang konsisten.'),
    ('Multiple Registration Waves', 'Pendaftaran dibuka secara bertahap (Gelombang 1, 2, 3) dengan tanggal buka-tutup dan kuota transparan.'),
    ('Pill-Shaped Tactile Controls', 'Seluruh tombol aksi utama berbentuk rounded-full (pill) berstandar Plus Jakarta Sans dengan kontras tajam.')
]
plx8 = 80
for ptitle, pdesc in pillars_v8:
    add_rect(f0, f'P0 Pil BG {ptitle}', plx8, 600, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_rect(f0, f'P0 Pil Accent {ptitle}', plx8, 600, 400, 6, fill_hex=C_PRIMARY, radius=[18, 18, 0, 0])
    add_text(f0, f'P0 Pil Title {ptitle}', plx8 + 28, 635, ptitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f0, f'P0 Pil Desc {ptitle}', plx8 + 28, 675, pdesc, font_size=14, color_hex=C_SECONDARY_TEXT, width=344, height=60)
    plx8 += 440

add_text(f0, 'P0 Footer', 80, 975, '© 2026 PMB Master Design Specification V8.0 FINAL — Complete Private University Platform.', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 01: 01 - Six-Screen Design Board (2048 x 2048 Aspect Ratio 1:1)
# ==========================================
p1 = add_page(1, '01 - Six-Screen Design Board')
f_board = add_frame(p1, 'Six-Screen Design Board (2x3 Grid)', 0, 0, 2048, 2048, C_BACKGROUND)

add_rect(f_board, 'Board Header BG', 0, 0, 2048, 80, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f_board, 'Board Header Title', 64, 28, 'SIX-SCREEN DESKTOP OVERVIEW BOARD (2 COLUMNS x 3 ROWS) — APPLICANT DESKTOP WEB ONLY', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')

# 6 panels in 2 cols x 3 rows scaled to fit 2048x2048 cleanly:
# Col 1: X=64, Col 2: X=1040 (width: 940 each)
# Row 1: Y=110, Row 2: Y=750, Row 3: Y=1390 (height: 620 each)
six_panels = [
    ('01 - Homepage', 64, 110, 'real_hero_students.png', 'Penerimaan Mahasiswa Baru 2026', 'Wujudkan mimpi bersama Universitas Nusantara', 'Daftar Sekarang →'),
    ('02 - Program Directory', 1040, 110, 'real_bldg_hero.png', 'Eksplorasi Program Studi S1', 'Temukan 1 program studi pilihan utama sesuai minat', 'Lihat Semua Prodi →'),
    ('03 - Registration Waves', 64, 750, 'real_female_student.png', 'Gelombang Pendaftaran Aktif', 'Gelombang 1 (Early Bird) • Buka s.d. 28 Feb 2026', 'Pilih Gelombang →'),
    ('04 - Applicant Dashboard', 1040, 750, 'real_bldg_ti.png', 'Dashboard Pendaftar & Stepper', 'Halo, Andi Pratama • Pendaftaran Berhasil Diajukan', 'Lihat Detail Status →'),
    ('05 - Program Detail', 64, 1390, 'real_bldg_detail.png', 'Detail Program: Teknik Informatika', 'Fakultas Ilmu Komputer • Akreditasi Unggul', 'Daftar Sekarang →'),
    ('06 - Desktop Application Form', 1040, 1390, 'card_snbp.jpg', 'Formulir Pendaftaran Siswa Baru', 'Tahap 1: Pilih 1 Prodi & Periode Gelombang Seleksi', 'Simpan & Lanjut →')
]
for ptitle, px, py, pimg, ph1, psub, pbtn in six_panels:
    add_rect(f_board, f'PBG {ptitle}', px, py, 940, 620, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_rect(f_board, f'PTh {ptitle}', px, py, 940, 48, fill_hex=C_MUTED_SURFACE, radius=[18, 18, 0, 0])
    add_text(f_board, f'PTxt {ptitle}', px + 24, py + 16, ptitle, font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
    
    # Internal panel preview
    add_image_rect(f_board, f'PImg {ptitle}', px + 24, py + 68, 892, 320, pimg, radius=12)
    add_text(f_board, f'PH1 {ptitle}', px + 24, py + 410, ph1, font_size=20, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_board, f'PSub {ptitle}', px + 24, py + 442, psub, font_size=13, color_hex=C_SECONDARY_TEXT)
    
    add_rect(f_board, f'PBtn {ptitle}', px + 24, py + 490, 200, 44, fill_hex=C_PRIMARY, radius=22)
    add_text(f_board, f'PBtnT {ptitle}', px + 55, py + 503, pbtn, font_size=12, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 02: 02 - Design Foundations
# ==========================================
p2 = add_page(2, '02 - Design Foundations')
f2 = add_frame(p2, 'Design Foundations — Tokens & Hierarchy', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f2, 'F2 Title', 80, 60, 'Design Foundations — Strict Color Tokens & Typographic Scale', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f2, 'F2 Sub', 80, 102, 'Sistem token desain resmi PMB 2026 PTS yang menjadi acuan konsistensi seluruh antarmuka.', font_size=15, color_hex=C_SECONDARY_TEXT)

colors_v8 = [
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
cx2 = 80
cy2 = 180
for i, (cname, chex, ctxt) in enumerate(colors_v8):
    add_rect(f2, f'Sw BG {cname}', cx2, cy2, 105, 110, fill_hex=chex, stroke_hex=C_BORDER, radius=12)
    add_text(f2, f'Sw Name {cname}', cx2 + 8, cy2 + 68, cname, font_size=10, color_hex=ctxt, font_weight='Bold')
    add_text(f2, f'Sw Hex {cname}', cx2 + 8, cy2 + 86, chex, font_size=11, color_hex=ctxt)
    cx2 += 116
    if (i + 1) % 6 == 0:
        cx2 = 80
        cy2 += 125

tscales_v8 = [
    ('Hero Title (54px Bold)', 'Gerbang Menuju Perguruan Tinggi Swasta Unggulan', 54, 'Bold'),
    ('Page Title (40px Bold)', 'Formulir Pendaftaran Siswa & Pilihan Gelombang', 40, 'Bold'),
    ('Section Title (32px Bold)', 'Pilihan Program Studi & Daya Tampung Kelas 2026', 32, 'Bold'),
    ('Card Title (18px Semibold)', 'S1 Teknik Informatika — Akreditasi Unggul', 18, 'Bold'),
    ('Body Text (15px Regular)', 'Wujudkan impian studi dengan proses seleksi digital terintegrasi, transparan, dan terpercaya.', 15, 'Regular'),
    ('Supporting Label (12px Medium)', 'NOMOR INDUK KEPENDUDUKAN (NIK) SESUAI KTP / KK RESMI *', 12, 'Bold')
]
ty8_2 = 495
for tscale, tex, tsz, twg in tscales_v8:
    add_text(f2, f'TLbl {tscale}', 80, ty8_2, tscale, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f2, f'TEx {tscale}', 320, ty8_2, tex, font_size=tsz, color_hex=C_PRIMARY_TEXT, font_weight=twg)
    ty8_2 += int(tsz * 1.5) + 12

add_text(f2, 'Spc Header', 80, 890, 'SPACING SYSTEM (4px BASELINE LADDER)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
spx2 = 80
for sp in [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80]:
    add_rect(f2, f'SpcBox {sp}', spx2, 920, sp, sp, fill_hex=C_PRIMARY, radius=2)
    add_text(f2, f'SpcTxt {sp}', spx2, 920 + sp + 8, f'{sp}px', font_size=10, color_hex=C_SECONDARY_TEXT)
    spx2 += max(sp + 14, 38)

# ==========================================
# PAGE 03: 03 - Design System and Components
# ==========================================
p3 = add_page(3, '03 - Design System and Components')
f3 = add_frame(p3, 'Component Library & 21 Status Variants', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f3, 'F3 Title', 80, 60, 'Pustaka Komponen UI & Status Variants (V8.0 Master)', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f3, 'F3 Sub', 80, 102, 'Pill-shaped buttons, form inputs, dan 21 status pendaftaran lengkap (Section 17).', font_size=15, color_hex=C_SECONDARY_TEXT)

# Buttons
add_rect(f3, 'Btn 1', 80, 180, 200, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f3, 'Btn 1 T', 125, 195, 'Primary Default', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f3, 'Btn 2', 300, 180, 200, 48, fill_hex=C_PRIMARY_HOVER, radius=24)
add_text(f3, 'Btn 2 T', 345, 195, 'Primary Hover', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f3, 'Btn 3', 520, 180, 200, 48, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=24)
add_text(f3, 'Btn 3 T', 565, 195, 'Secondary Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f3, 'Btn 4', 740, 180, 200, 48, fill_hex=C_WARNING, radius=24)
add_text(f3, 'Btn 4 T', 785, 195, 'Amber Accent Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# 21 Status Badges
add_text(f3, 'Badge H', 80, 260, '2. APPLICATION STATUS VARIANTS (21 REQUIRED STATES - SECTION 17)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
status_21_v8 = [
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
sbx3 = 80
sby3 = 295
for i, (stxt, sbg, sbrd, scol) in enumerate(status_21_v8):
    bw = len(stxt) * 8 + 32
    add_rect(f3, f'StBadge {stxt}', sbx3, sby3, bw, 32, fill_hex=sbg, stroke_hex=sbrd, radius=16)
    add_text(f3, f'StTxt {stxt}', sbx3 + 16, sby3 + 8, stxt, font_size=11, color_hex=scol, font_weight='Bold')
    sbx3 += bw + 14
    if (i + 1) % 5 == 0:
        sbx3 = 80
        sby3 += 46

print('Pages 00-03 built!')

# ==========================================
# PAGE 04: 04 - Public Website
# ==========================================
p4 = add_page(4, '04 - Public Website')

# PUB-001: Homepage
f4 = add_frame(p4, 'PUB-001 — Homepage', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f4, active_nav='Beranda')
add_text(f4, 'F4 Hero 1', 80, 140, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4, 'F4 Hero 2', 80, 205, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f4, 'F4 Hero 3', 80, 270, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f4, 'F4 Sub 1', 80, 350, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f4, 'F4 Sub 2', 80, 375, 'bersama Universitas Nusantara.', font_size=16, color_hex=C_SECONDARY_TEXT)

add_rect(f4, 'F4 Btn CTA', 80, 425, 195, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f4, 'F4 Btn CTA T', 115, 439, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_text(f4, 'F4 Video CTA', 305, 439, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_image_rect(f4, 'F4 Real Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)

add_rect(f4, 'F4 Ribbon BG', 80, 670, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
for rlbl, rval, rico, rx in [('Periode Pendaftaran', 'Gelombang 1 s.d. 3', 'WAV', 120), ('Proses Seleksi', 'Satu Alur Terpadu', 'CAP', 440), ('Program Studi', '100+ Pilihan S1', 'BOK', 760), ('Beasiswa PTS', 'Hingga 100% Penuh', 'GFT', 1060)]:
    add_rect(f4, f'F4 RIco {rico}', rx, 696, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f4, f'F4 RIcoT {rico}', rx + 10, 709, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f4, f'F4 RLbl {rlbl}', rx + 56, 700, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f4, f'F4 RVal {rval}', rx + 56, 720, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_text(f4, 'F4 Sec Waves Title', 80, 795, 'GELOMBANG PENDAFTARAN AKTIF TA 2026/2027', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
for wname, wdates, wstat, wcost, wimg, wx in [('Gelombang 1 (Early Bird)', '01 Jan - 28 Feb 2026', 'SEDANG DIBUKA', 'Biaya: Rp 250.000 (Diskon UKT 20%)', 'card_snbp.jpg', 80), ('Gelombang 2 (Reguler)', '01 Mar - 30 Apr 2026', 'MENDATANG', 'Biaya: Rp 300.000', 'card_snbt.jpg', 520), ('Gelombang 3 (Penutup)', '01 Mei - 30 Jun 2026', 'MENDATANG', 'Biaya: Rp 350.000', 'card_mandiri.jpg', 960)]:
    add_rect(f4, f'F4 WC BG {wname}', wx, 825, 400, 130, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f4, f'F4 WC Img {wname}', wx, 825, 140, 130, wimg, radius=[14, 0, 0, 14])
    add_text(f4, f'F4 WC Title {wname}', wx + 155, 845, wname, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f4, f'F4 WC Dates {wname}', wx + 155, 868, wdates, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f4, f'F4 WC Cost {wname}', wx + 155, 888, wcost, font_size=10, color_hex=C_SUCCESS if 'Early' in wname else C_SECONDARY_TEXT)
    add_rect(f4, f'F4 WC Pill {wname}', wx + 155, 915, 110, 24, fill_hex='#ecfdf5' if 'DIBUKA' in wstat else C_MUTED_SURFACE, radius=12)
    add_text(f4, f'F4 WC PillTxt {wname}', wx + 170, 921, wstat, font_size=9, color_hex=C_SUCCESS if 'DIBUKA' in wstat else C_SECONDARY_TEXT, font_weight='Bold')
add_desktop_footer(f4, y_pos=975)

# ==========================================
# PAGE 05: 05 - University and Program Discovery
# ==========================================
p5 = add_page(5, '05 - University and Program Discovery')

# PUB-006: Program Directory
f5_dir = add_frame(p5, 'PUB-006 — Program Directory', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f5_dir, active_nav='Program Studi')
add_text(f5_dir, 'F5D Title', 80, 120, 'Program Studi', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f5_dir, 'F5D Sub', 80, 168, 'Temukan program studi yang sesuai dengan minat dan bakatmu. Pilih 1 Program Studi Utama.', font_size=15, color_hex=C_SECONDARY_TEXT)
add_image_rect(f5_dir, 'F5D Bldg Hero', 780, 105, 580, 220, 'real_bldg_hero.png', radius=18)
add_rect(f5_dir, 'F5D Search', 80, 215, 480, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f5_dir, 'F5D Search T', 102, 228, '🔍  Cari program studi...', font_size=13, color_hex=C_SECONDARY_TEXT)

fpx5 = 80
for ptxt, pact in [('Semua', True), ('Fakultas ⌵', False), ('Jenjang ⌵', False), ('Akreditasi ⌵', False)]:
    pbg = C_PRIMARY if pact else C_SURFACE
    ptcol = C_SURFACE if pact else C_PRIMARY_TEXT
    pw = len(ptxt) * 9 + 30
    add_rect(f5_dir, f'F5D P {ptxt}', fpx5, 280, pw, 38, fill_hex=pbg, stroke_hex=None if pact else C_BORDER, radius=19)
    add_text(f5_dir, f'F5D PTxt {ptxt}', fpx5 + 15, 290, ptxt, font_size=12, color_hex=ptcol, font_weight='Bold' if pact else 'Regular')
    fpx5 += pw + 12
add_text(f5_dir, 'F5D See All', 1210, 290, 'Lihat Semua Program →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

for ctitle, cfac, cdeg, cakred, cimg, cx in [('Teknik Informatika', 'Fakultas Ilmu Komputer', 'S1', 'Akreditasi Unggul', 'real_bldg_ti.png', 80), ('Manajemen', 'Fakultas Ekonomi & Bisnis', 'S1', 'Akreditasi Unggul', 'real_bldg_mn.png', 520), ('Psikologi', 'Fakultas Psikologi', 'S1', 'Akreditasi A', 'real_bldg_ps.png', 960)]:
    add_rect(f5_dir, f'F5D CardBG {ctitle}', cx, 360, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_image_rect(f5_dir, f'F5D CardImg {ctitle}', cx, 360, 400, 185, cimg, radius=[18, 18, 0, 0])
    add_text(f5_dir, f'F5D CardTitle {ctitle}', cx + 22, 565, ctitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f5_dir, f'F5D CardFac {ctitle}', cx + 22, 592, cfac, font_size=13, color_hex=C_SECONDARY_TEXT)
    add_text(f5_dir, f'F5D CardDeg {ctitle}', cx + 22, 612, cdeg, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f5_dir, f'F5D AkredPill {ctitle}', cx + 22, 642, 135, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
    add_text(f5_dir, f'F5D AkredTxt {ctitle}', cx + 36, 648, f'● {cakred}', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    add_rect(f5_dir, f'F5D ArrowCircle {ctitle}', cx + 340, 638, 36, 36, fill_hex=C_MUTED_SURFACE, radius=18)
    add_text(f5_dir, f'F5D ArrowTxt {ctitle}', cx + 352, 646, '→', font_size=15, color_hex=C_PRIMARY, font_weight='Bold')

# PUB-007: Program Detail (X=1540)
f5_det = add_frame(p5, 'PUB-007 — Program Detail', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f5_det, active_nav='Program Studi')
add_text(f5_det, 'F5T Back Link', 80, 110, '← Kembali ke Program Studi', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_image_rect(f5_det, 'F5T Bldg Photo', 80, 140, 460, 300, 'real_bldg_detail.png', radius=18)
add_text(f5_det, 'F5T Major Title', 580, 160, 'Teknik Informatika', font_size=36, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f5_det, 'F5T Major Fac', 580, 210, 'Fakultas Ilmu Komputer', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f5_det, 'F5T Akred Pill', 580, 245, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f5_det, 'F5T Akred Pill Txt', 594, 251, '● Akreditasi Unggul', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

add_text(f5_det, 'F5T Desc 1', 580, 290, 'Program studi Teknik Informatika membekali mahasiswa dengan kompetensi', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f5_det, 'F5T Desc 2', 580, 312, 'di bidang teknologi informasi, rekayasa perangkat lunak, dan kecerdasan buatan.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f5_det, 'F5T Btn Daftar', 580, 360, 180, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f5_det, 'F5T Btn Daftar Txt', 612, 374, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f5_det, 'F5T Btn Kurikulum', 780, 360, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f5_det, 'F5T Btn Kurikulum Txt', 812, 374, 'Lihat Kurikulum', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# ==========================================
# PAGE 06: 06 - Admission and Registration Waves (V7 Model!)
# ==========================================
p6 = add_page(6, '06 - Admission and Registration Waves')

# PUB-010: Registration Waves
f6_wav = add_frame(p6, 'PUB-010 & 011 — Registration Waves', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f6_wav, active_nav='Gelombang Pendaftaran')
add_text(f6_wav, 'F6W Title', 80, 120, 'Gelombang Pendaftaran Mahasiswa Baru 2026', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f6_wav, 'F6W Sub', 80, 168, 'Satu proses admisi terpadu dengan 3 periode gelombang pendaftaran (PTS Model).', font_size=15, color_hex=C_SECONDARY_TEXT)

# 3 Waves Cards
waves_detail = [
    ('GELOMBANG 1 (EARLY BIRD)', '01 Jan - 28 Feb 2026', 'SEDANG DIBUKA', 'Biaya Pendaftaran: Rp 250.000', 'Benefit Tambahan: Diskon UKT Semester 1 sebesar 20%', 'card_snbp.jpg', 80),
    ('GELOMBANG 2 (REGULER)', '01 Mar - 30 Apr 2026', 'MENDATANG', 'Biaya Pendaftaran: Rp 300.000', 'Benefit Tambahan: Jalur Bebas Tes untuk Nilai Rapor > 85', 'card_snbt.jpg', 520),
    ('GELOMBANG 3 (PENUTUP)', '01 Mei - 30 Jun 2026', 'MENDATANG', 'Biaya Pendaftaran: Rp 350.000', 'Benefit Tambahan: Kesempatan Terakhir Kuota Program Unggulan', 'card_mandiri.jpg', 960)
]
for wname, wdate, wstat, wcost, wben, wimg, wx in waves_detail:
    add_rect(f6_wav, f'F6W Card {wname}', wx, 220, 400, 480, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_image_rect(f6_wav, f'F6W Img {wname}', wx, 220, 400, 160, wimg, radius=[18, 18, 0, 0])
    
    add_text(f6_wav, f'F6W Name {wname}', wx + 20, 400, wname, font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f6_wav, f'F6W Date {wname}', wx + 20, 426, wdate, font_size=12, color_hex=C_PRIMARY, font_weight='Bold')
    
    add_rect(f6_wav, f'F6W Pill {wname}', wx + 20, 455, 120, 26, fill_hex='#ecfdf5' if 'DIBUKA' in wstat else C_MUTED_SURFACE, radius=13)
    add_text(f6_wav, f'F6W PillTxt {wname}', wx + 35, 461, wstat, font_size=10, color_hex=C_SUCCESS if 'DIBUKA' in wstat else C_SECONDARY_TEXT, font_weight='Bold')
    
    add_text(f6_wav, f'F6W Cost {wname}', wx + 20, 500, wcost, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f6_wav, f'F6W Ben {wname}', wx + 20, 524, wben, font_size=11, color_hex=C_SUCCESS if 'Early' in wname else C_SECONDARY_TEXT, width=360, height=35)
    
    add_rect(f6_wav, f'F6W Btn {wname}', wx + 20, 630, 360, 46, fill_hex=C_PRIMARY if 'DIBUKA' in wstat else C_MUTED_SURFACE, radius=23)
    add_text(f6_wav, f'F6W BtnTxt {wname}', wx + 120, 644, 'Pilih Gelombang Ini →' if 'DIBUKA' in wstat else 'Belum Dibuka', font_size=12, color_hex=C_SURFACE if 'DIBUKA' in wstat else C_SECONDARY_TEXT, font_weight='Bold')

# ==========================================
# PAGE 07: 07 - Authentication
# ==========================================
p7 = add_page(7, '07 - Authentication')

# AUTH-001 & 007: Login & Registration
f7 = add_frame(p7, 'AUTH-001 & 007 — Login & Registration', 0, 0, 1440, 1024, C_BACKGROUND)
add_image_rect(f7, 'F7 Lib Wall', 80, 60, 580, 900, 'library_bg.jpg', radius=20)
add_rect(f7, 'F7 Lib Overlay', 80, 60, 580, 900, fill_hex=C_PRIMARY_TEXT, opacity=0.76, radius=20)

add_rect(f7, 'F7 Glass Box', 110, 90, 520, 840, fill_hex=C_SURFACE, stroke_hex='#ffffff35', radius=16, opacity=0.15)
add_text(f7, 'F7 Brand', 140, 120, 'PMB UNNES 2026', font_size=20, color_hex=C_SURFACE, font_weight='Bold')
add_text(f7, 'F7 Info Title', 140, 160, 'Pendaftaran Akun Mahasiswa Baru', font_size=24, color_hex=C_SURFACE, font_weight='Bold')
add_text(f7, 'F7 Info Sub', 140, 195, 'Satu akun resmi untuk seluruh tahapan admisi perguruan tinggi swasta terakreditasi.', font_size=12, color_hex=C_MUTED_SURFACE, width=460, height=40)

steps_auth8 = [
    ('1', 'Registrasi Akun Siswa', 'Daftarkan email aktif dan 10 digit NISN valid.'),
    ('2', 'Pilih 1 Program Studi', 'Tentukan 1 program studi pilihan utama sesuai minat.'),
    ('3', 'Pilih Gelombang Pendaftaran', 'Pilih periode gelombang registrasi yang aktif.'),
    ('4', 'Unggah Dokumen Syarat', 'Upload file scan Ijazah/SKL, Kartu Keluarga, dan Foto.'),
    ('5', 'Finalisasi & Asesmen', 'Selesaikan pendaftaran dan ikuti asesmen masuk.')
]
p7_sy = 250
for pnum, pstitle, psdesc in steps_auth8:
    add_rect(f7, f'F7 SBox {pnum}', 140, p7_sy, 460, 74, fill_hex=C_SURFACE, stroke_hex='#ffffff25', radius=10, opacity=0.12)
    add_rect(f7, f'F7 SNumBG {pnum}', 158, p7_sy + 17, 40, 40, fill_hex=C_PRIMARY, radius=20)
    add_text(f7, f'F7 SNum {pnum}', 174, p7_sy + 28, pnum, font_size=14, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f7, f'F7 STitle {pnum}', 212, p7_sy + 17, pstitle, font_size=13, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f7, f'F7 SDesc {pnum}', 212, p7_sy + 39, psdesc, font_size=11, color_hex='#cbd5e1')
    p7_sy += 86

# Right Form Panel
add_rect(f7, 'F7 Form BG', 680, 60, 680, 900, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_text(f7, 'F7 Back Link', 720, 95, '← Kembali ke Beranda Portal', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f7, 'F7 Tab Container', 720, 135, 600, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f7, 'F7 Tab 1 Active', 724, 139, 296, 40, fill_hex=C_SURFACE, radius=20)
add_text(f7, 'F7 Tab 1 Txt', 815, 151, 'Masuk ke Akun', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7, 'F7 Tab 2 Txt', 1105, 151, 'Daftar Akun Baru', font_size=13, color_hex=C_SECONDARY_TEXT)

add_text(f7, 'F7 Form Title', 720, 220, 'Masuk ke Akun PMB', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f7, 'F7 Form Sub', 720, 255, 'Masukkan email atau NISN dan kata sandi yang telah terdaftar.', font_size=13, color_hex=C_SECONDARY_TEXT)

add_text(f7, 'F7 Lbl 1', 720, 305, 'Alamat Email atau NISN *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7, 'F7 Inp 1', 720, 330, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f7, 'F7 Inp 1 Val', 738, 345, 'irfan@mail.com atau 0058291042', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f7, 'F7 Lbl 2', 720, 405, 'Kata Sandi (Password) *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f7, 'F7 Inp 2', 720, 430, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f7, 'F7 Inp 2 Val', 738, 445, '••••••••••••••••', font_size=13, color_hex=C_PRIMARY_TEXT)

add_rect(f7, 'F7 Submit Btn', 720, 530, 600, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f7, 'F7 Submit Btn Txt', 960, 546, 'Masuk Sekarang →', font_size=14, color_hex=C_SURFACE, font_weight='Bold')

# ==========================================
# PAGE 08: 08 - Applicant Onboarding
# ==========================================
p8 = add_page(8, '08 - Applicant Onboarding')
f8_onb = add_frame(p8, 'ONB-001 to 007 — Applicant Onboarding Workflow', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f8_onb, active_nav='Beranda')
add_text(f8_onb, 'F8O Title', 80, 120, 'Orientasi Akun Pendaftar Baru (/onboarding)', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_onb, 'F8O Sub', 80, 165, 'Lengkapi profil dasar sebelum memulai pengisian formulir pendaftaran resmi.', font_size=15, color_hex=C_SECONDARY_TEXT)

add_rect(f8_onb, 'F8O Card BG', 80, 220, 1280, 720, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
add_text(f8_onb, 'F8O Welcome', 120, 260, 'Selamat Datang di Portal Penerimaan Mahasiswa Baru 2026', font_size=22, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_onb, 'F8O Welcome D', 120, 295, 'Akun Anda berhasil diverifikasi. Mari kita persiapkan profil Anda dalam beberapa langkah sederhana.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f8_onb, 'F8O Next Btn', 120, 840, 240, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f8_onb, 'F8O Next Btn Txt', 158, 854, 'Lanjut ke Formulir →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

print('Pages 04-08 built!')
