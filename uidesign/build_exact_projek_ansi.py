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

# EXACT COLORS OF FIGMA PROJEK-ANSI
C_BLUE = '#0284c7'          # Primary Sky Blue
C_DARK_BLUE = '#0369a1'     # Deep Header Blue
C_LIGHT_BLUE = '#e0f2fe'    # Light Sky Accent
C_PRIMARY_SUBTLE = '#f0f9ff'# Subtle Sky Highlight
C_AMBER = '#f59e0b'         # Amber Accent
C_NAVY = '#0f172a'          # Dark Navy
C_WHITE = '#ffffff'         # Surface White
C_CANVAS = '#f8fafc'        # Page Canvas
C_BORDER = '#e2e8f0'        # Border Gray
C_TEXT_PRIMARY = '#0f172a'  # Primary Text
C_TEXT_SEC = '#334155'      # Secondary Slate Text
C_TEXT_MUTED = '#64748b'    # Muted Slate
C_SUCCESS = '#059669'       # Success Green
C_SUCCESS_BG = '#ecfdf5'    # Success Light
C_SUCCESS_BORDER = '#a7f3d0'# Success Border
C_WARNING_BG = '#fef3c7'    # Amber Light
C_WARNING_BORDER = '#fde68a'# Amber Border
C_WARNING_TEXT = '#b45309'  # Amber Dark
C_ERROR_BG = '#fff1f2'      # Red Light
C_ERROR_BORDER = '#fecdd3'  # Red Border
C_ERROR_TEXT = '#be123c'    # Red Dark

doc = {
    'comments': [],
    'current_page': 1,
    'document_colors': [],
    'format': 'figcraft',
    'imageIndex': image_index,
    'name': 'PROJEK-ANSI (Figma Duplicate)',
    'next_id': 100,
    'nodes': {
        '1': {
            'background': {'a': 1.0, 'r': 0.1176, 'g': 0.1176, 'b': 0.1176},
            'children': [],
            'flows': [],
            'height': 0.0,
            'id': 1,
            'name': 'Page 1',
            'prototype': {'background': {'a': 1.0, 'r': 0.1176, 'g': 0.1176, 'b': 0.1176}, 'device': 'None', 'rotation': 'portrait'},
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

def add_frame(name, x, y, w=1440.0, h=1000.0, bg_hex=C_CANVAS):
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

def add_text(parent_id, name, x, y, characters, font_size=13.0, color_hex=C_TEXT_PRIMARY, font_weight='Regular', font_family='Inter', width=None, height=None):
    nid = alloc_id()
    w = float(width) if width else float(len(characters) * font_size * 0.65)
    h = float(height) if height else float(font_size * 1.3)
    node = {
        'blend': 'normal',
        'characters': characters,
        'child_layout': {'absolute': False, 'grid_column': None, 'grid_column_span': 0, 'grid_row': None, 'grid_row_span': 0, 'max_h': None, 'max_w': None, 'min_h': None, 'min_w': None, 'sizing_h': 'hug' if width is None else 'fixed', 'sizing_v': 'hug' if height is None else 'fixed'},
        'fills': [{'blend': 'normal', 'color': hex_to_rgb(color_hex), 'opacity': 1.0, 'type': 'solid', 'visible': True}],
        'height': h,
        'id': nid,
        'name': name,
        'parent': parent_id,
        'style': {'case': 'original', 'decoration': 'none', 'fills': None, 'font_family': font_family, 'font_size': float(font_size), 'font_style': font_weight, 'letter_spacing': {'unit': 'percent', 'value': 0.0}, 'line_height': {'unit': 'auto'}, 'link': None},
        'transform': [1.0, 0.0, 0.0, 1.0, float(x), float(y)],
        'type': 'text',
        'width': w
    }
    doc['nodes'][str(nid)] = node
    doc['nodes'][str(parent_id)]['children'].append(nid)
    return nid

print('Exact PROJEK-ANSI builder initialized.')

# ==========================================
# 01. Homepage (Belum Login)
# ==========================================
f_home1 = add_frame('Homepage (Belum Login)', 0.0, 0.0)

# Top Bar
add_rect(f_home1, 'F1 Top Bar', 0, 0, 1440, 36, fill_hex=C_DARK_BLUE)
add_text(f_home1, 'F1 Top L', 48, 10, 'Call Center: (024) 8508093  |  Email: pmb@mail.unnes.ac.id  |  Gedung Rektorat Kampus Sekaran', font_size=11, color_hex='#e0f2fe')
add_text(f_home1, 'F1 Top R', 1040, 10, 'Jadwal Seleksi TA 2026/2027  |  Buku Panduan PMB (PDF)', font_size=11, color_hex='#e0f2fe')

# Main Header Navbar
add_rect(f_home1, 'F1 Nav BG', 0, 36, 1440, 76, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_rect(f_home1, 'F1 Logo Badge', 48, 52, 42, 42, fill_hex=C_BLUE, radius=8)
add_text(f_home1, 'F1 Logo Txt', 57, 62, 'UN', font_size=16, color_hex=C_WHITE, font_weight='Bold')
add_text(f_home1, 'F1 Brand Name', 102, 53, 'PMB UNNES 2026', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_home1, 'F1 Brand Sub', 102, 75, 'Penerimaan Mahasiswa Baru Universitas Negeri Semarang', font_size=11, color_hex=C_TEXT_MUTED)

navs_home = ['Beranda', 'Jalur Masuk', 'Program Studi', 'Biaya Kuliah', 'Pengumuman', 'Kontak']
nx = 580
for nv in navs_home:
    add_text(f_home1, f'F1 Nav {nv}', nx, 66, nv, font_size=13, color_hex=C_TEXT_SEC)
    nx += 105

add_rect(f_home1, 'F1 Btn Login', 1248, 53, 144, 42, fill_hex=C_BLUE, radius=8)
add_text(f_home1, 'F1 Btn Login Txt', 1278, 65, 'Masuk / Daftar', font_size=13, color_hex=C_WHITE, font_weight='Bold')

# Hero Banner with Campus Photo & Circular Cutout
add_image_rect(f_home1, 'F1 Hero Photo BG', 48, 132, 1344, 380, 'hero_campus.jpg', radius=16)
add_rect(f_home1, 'F1 Hero Gradient Overlay', 48, 132, 1344, 380, fill_hex=C_DARK_BLUE, opacity=0.82, radius=16)

add_rect(f_home1, 'F1 Hero Badge', 80, 165, 310, 26, fill_hex=C_WHITE, opacity=0.2, radius=13)
add_text(f_home1, 'F1 Hero Badge Txt', 94, 171, 'PENDAFTARAN MAHASISWA BARU TA 2026/2027', font_size=10, color_hex=C_WHITE, font_weight='Bold')

add_text(f_home1, 'F1 Hero Title 1', 80, 204, 'Pendaftaran Mahasiswa Baru', font_size=32, color_hex=C_WHITE, font_weight='Bold')
add_text(f_home1, 'F1 Hero Title 2', 80, 246, 'Telah Dibuka!', font_size=34, color_hex=C_AMBER, font_weight='Bold')

add_text(f_home1, 'F1 Hero Lead 1', 80, 300, 'Wujudkan impian studi di Kampus Konservasi Bereputasi Internasional.', font_size=14, color_hex='#e0f2fe')
add_text(f_home1, 'F1 Hero Lead 2', 80, 322, 'Sistem seleksi digital terpadu, verifikasi berkas cepat, dan notifikasi real-time.', font_size=14, color_hex='#e0f2fe')

add_rect(f_home1, 'F1 Hero Btn 1', 80, 365, 200, 48, fill_hex=C_AMBER, radius=8)
add_text(f_home1, 'F1 Hero Btn 1 Txt', 110, 380, 'Daftar Akun Baru →', font_size=13, color_hex=C_NAVY, font_weight='Bold')

add_rect(f_home1, 'F1 Hero Btn 2', 295, 365, 200, 48, fill_hex=C_WHITE, stroke_hex='#cbd5e1', radius=8)
add_text(f_home1, 'F1 Hero Btn 2 Txt', 325, 380, 'Panduan Pendaftaran', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

# Cutout Mahasiswi dengan Backdrop Lingkaran Biru
add_rect(f_home1, 'F1 Circle Backdrop', 760, 150, 260, 260, fill_hex=C_BLUE, radius=130)
add_image_rect(f_home1, 'F1 Hero Student Img', 770, 155, 240, 330, 'student_hero.png')

# Statistik Card
add_rect(f_home1, 'F1 Stat Card BG', 1055, 175, 305, 230, fill_hex=C_WHITE, radius=14)
add_text(f_home1, 'F1 Stat Card Title', 1080, 198, 'Statistik Seleksi Aktif', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f_home1, 'F1 Stat Card Div', 1080, 225, 255, 1, fill_hex=C_BORDER)

add_text(f_home1, 'F1 Stat 1 Lbl', 1080, 238, 'Total Pendaftar Terverifikasi:', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f_home1, 'F1 Stat 1 Val', 1080, 254, '1,428 Siswa', font_size=18, color_hex=C_BLUE, font_weight='Bold')

add_text(f_home1, 'F1 Stat 2 Lbl', 1080, 285, 'Pilihan Program Studi:', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f_home1, 'F1 Stat 2 Val', 1080, 301, '72 Program Studi (Unggul)', font_size=14, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

add_rect(f_home1, 'F1 Stat Pill', 1080, 335, 255, 32, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=6)
add_text(f_home1, 'F1 Stat Pill Txt', 1098, 344, 'Status Sistem: ONLINE • Pendaftaran Aktif', font_size=10, color_hex='#15803d', font_weight='Bold')

# Section: Gelombang Pendaftaran
add_text(f_home1, 'F1 Sec Title', 48, 535, 'GELOMBANG PENDAFTARAN PMB 2026', font_size=20, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_home1, 'F1 Sec Sub', 48, 562, 'Pilih Jalur Masuk Sesuai Kualifikasi & Prestasi Akademik Anda', font_size=13, color_hex=C_TEXT_MUTED)

jalur_items = [
    ('card_snbp.jpg', 'Gelombang 1 (SNBP Nasional)', 'Seleksi nasional berdasarkan prestasi nilai rapor semester 1-5 dan portofolio kejuaraan.', 'Jadwal: 10 Nov - 20 Des 2026', 'Bebas Biaya Pendaftaran', 48),
    ('card_snbt.jpg', 'Gelombang 2 (SNBT UTBK)', 'Seleksi nasional berbasis tes skolastik dan literasi terstandar yang diselenggarakan BPPP.', 'Jadwal: 15 Jan - 28 Feb 2027', 'Biaya Tes: Rp 200.000', 508),
    ('card_mandiri.jpg', 'Gelombang 3 (SM-UNNES Mandiri)', 'Seleksi mandiri perguruan tinggi berbasis ujian CBT terpadu UNNES dan prestasi unggul.', 'Jadwal: 01 Mar - 15 Apr 2027', 'Biaya Ujian: Rp 300.000', 968)
]
for jimg, jtitle, jdesc, jdate, jcost, jx in jalur_items:
    add_rect(f_home1, f'F1 JCard {jtitle} BG', jx, 595, 424, 320, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f_home1, f'F1 JCard {jtitle} Img', jx, 595, 424, 135, jimg, radius=[14, 14, 0, 0])
    add_text(f_home1, f'F1 JCard {jtitle} Title', jx + 20, 745, jtitle, font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f_home1, f'F1 JCard {jtitle} Desc', jx + 20, 768, jdesc, font_size=11, color_hex=C_TEXT_SEC, width=384, height=35)
    add_text(f_home1, f'F1 JCard {jtitle} Date', jx + 20, 812, jdate, font_size=11, color_hex=C_BLUE, font_weight='Bold')
    add_text(f_home1, f'F1 JCard {jtitle} Cost', jx + 20, 830, jcost, font_size=10, color_hex=C_TEXT_MUTED)
    add_rect(f_home1, f'F1 JCard {jtitle} Btn', jx + 20, 858, 384, 38, fill_hex=C_PRIMARY_SUBTLE, stroke_hex='#bae6fd', radius=6)
    add_text(f_home1, f'F1 JCard {jtitle} BtnTxt', jx + 130, 870, 'Lihat Informasi Selengkapnya →', font_size=11, color_hex=C_BLUE, font_weight='Bold')

add_rect(f_home1, 'F1 Footer BG', 0, 940, 1440, 60, fill_hex=C_DARK_BLUE)
add_text(f_home1, 'F1 Footer Copy', 48, 962, '© 2026 Universitas Negeri Semarang — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex=C_WHITE)

# ==========================================
# 02. Login & 03. Sign Up
# ==========================================
f_login = add_frame('Login', 1540.0, 0.0)

# Full Left Wall with Real Library Background Photo
add_image_rect(f_login, 'F2 Library Wall', 0, 0, 680, 1000, 'library_bg.jpg')
add_rect(f_login, 'F2 Library Overlay', 0, 0, 680, 1000, fill_hex=C_NAVY, opacity=0.74)

# Glassmorphism Box on Library Wall
add_rect(f_login, 'F2 Glass BG', 80, 160, 520, 680, fill_hex=C_WHITE, stroke_hex='#ffffff30', radius=16, opacity=0.15)
add_text(f_login, 'F2 Glass Brand', 115, 195, 'PORTAL ADMISI PMB UNNES 2026', font_size=13, color_hex=C_AMBER, font_weight='Bold')
add_text(f_login, 'F2 Glass H', 115, 230, 'Satu Akun Terpadu untuk Seluruh Tahapan Seleksi', font_size=24, color_hex=C_WHITE, font_weight='Bold', width=450, height=70)

login_rules = [
    ('1', 'Pendaftaran Akun Resmi', 'Gunakan NISN 10 digit dan alamat email aktif.'),
    ('2', 'Pengisian Biodata & Berkas', 'Isi data pribadi, orang tua, dan unggah syarat dokumen.'),
    ('3', 'Pembayaran Biaya Ujian', 'Pembayaran real-time melalui Virtual Account Bank.'),
    ('4', 'Ujian CBT & Verifikasi', 'Ikuti tes komputer dan pantau verifikasi berkas.'),
    ('5', 'Pengumuman & Registrasi', 'Lihat hasil kelulusan dan lanjutkan registrasi ulang.')
]
ry = 320
for rnum, rtitle, rdesc in login_rules:
    add_rect(f_login, f'F2 RCircle {rnum}', 115, ry, 36, 36, fill_hex=C_BLUE, radius=18)
    add_text(f_login, f'F2 RNum {rnum}', 128, ry + 9, rnum, font_size=13, color_hex=C_WHITE, font_weight='Bold')
    add_text(f_login, f'F2 RTitle {rnum}', 165, ry + 2, rtitle, font_size=13, color_hex=C_WHITE, font_weight='Bold')
    add_text(f_login, f'F2 RDesc {rnum}', 165, ry + 20, rdesc, font_size=11, color_hex='#cbd5e1')
    ry += 66

# Right Form Wall
add_rect(f_login, 'F2 Right Wall BG', 680, 0, 760, 1000, fill_hex=C_WHITE)
add_text(f_login, 'F2 Back Home', 740, 48, '← Kembali ke Beranda', font_size=12, color_hex=C_BLUE, font_weight='Bold')

add_text(f_login, 'F2 Form Title', 740, 140, 'Masuk ke Akun PMB', font_size=28, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_login, 'F2 Form Sub', 740, 178, 'Silakan masukkan NISN atau Email dan kata sandi yang telah terdaftar.', font_size=13, color_hex=C_TEXT_MUTED)

add_text(f_login, 'F2 Lbl User', 740, 240, 'Nomor Induk Siswa Nasional (NISN) / Email *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f_login, 'F2 Inp User', 740, 268, 620, 48, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f_login, 'F2 Val User', 758, 282, '0058291042 atau irfan@mail.unnes.ac.id', font_size=13, color_hex=C_TEXT_PRIMARY)

add_text(f_login, 'F2 Lbl Pass', 740, 342, 'Kata Sandi (Password) *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f_login, 'F2 Inp Pass', 740, 370, 620, 48, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f_login, 'F2 Val Pass', 758, 384, '••••••••••••••••', font_size=13, color_hex=C_TEXT_PRIMARY)

add_text(f_login, 'F2 Lupa Sandi', 1235, 432, 'Lupa kata sandi?', font_size=12, color_hex=C_BLUE, font_weight='Bold')

add_rect(f_login, 'F2 Btn Submit', 740, 475, 620, 50, fill_hex=C_BLUE, radius=8)
add_text(f_login, 'F2 Btn Submit Txt', 985, 490, 'Masuk Sekarang →', font_size=14, color_hex=C_WHITE, font_weight='Bold')

add_rect(f_login, 'F2 Alt Div', 740, 565, 620, 1, fill_hex=C_BORDER)
add_text(f_login, 'F2 Belum Punya', 935, 605, 'Belum memiliki akun PMB 2026?', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f_login, 'F2 Btn Go Register', 740, 635, 620, 48, fill_hex=C_WHITE, stroke_hex=C_BLUE, radius=8)
add_text(f_login, 'F2 Btn Go Register Txt', 960, 650, 'Buat Akun Siswa Baru', font_size=13, color_hex=C_BLUE, font_weight='Bold')

# ==========================================
# 04. Pendataan (Formulir Multi-Step)
# ==========================================
f_pendataan = add_frame('Pendataan', 3080.0, 0.0)

# Top Bar
add_rect(f_pendataan, 'F3 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_pendataan, 'F3 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_pendataan, 'F3 Title', 220, 24, 'Formulir Pendaftaran Calon Mahasiswa Baru TA 2026/2027', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f_pendataan, 'F3 Draft Badge', 1030, 18, 90, 28, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=14)
add_text(f_pendataan, 'F3 Draft Badge Txt', 1052, 24, 'DRAFT', font_size=11, color_hex='#b45309', font_weight='Bold')
add_text(f_pendataan, 'F3 User Pill', 1135, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Stepper Bar with Circles and Connectors
add_rect(f_pendataan, 'F3 Stepper BG', 48, 88, 1344, 76, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
steps_w = [
    ('1', 'Biodata Diri', True),
    ('2', 'Pilihan Prodi', False),
    ('3', 'Unggah Berkas', False),
    ('4', 'Validasi', False),
    ('5', 'Pembayaran', False)
]
wx = 80
for i, (wnum, wname, wactive) in enumerate(steps_w):
    s_bg = C_BLUE if wactive else '#f1f5f9'
    s_txt = C_WHITE if wactive else '#64748b'
    add_rect(f_pendataan, f'F3 SCircle {wnum}', wx, 106, 40, 40, fill_hex=s_bg, radius=20)
    add_text(f_pendataan, f'F3 SNum {wnum}', wx + 15, 117, wnum, font_size=13, color_hex=s_txt, font_weight='Bold')
    add_text(f_pendataan, f'F3 SName {wnum}', wx + 50, 117, wname, font_size=13, color_hex=C_TEXT_PRIMARY if wactive else C_TEXT_MUTED, font_weight='Bold' if wactive else 'Regular')
    if i < 4:
        add_rect(f_pendataan, f'F3 SLine {i}', wx + 175, 125, 75, 2, fill_hex='#cbd5e1')
    wx += 265

# Main Form Container
add_rect(f_pendataan, 'F3 Form BG', 48, 180, 1344, 740, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)
add_text(f_pendataan, 'F3 Step Title', 80, 210, 'Langkah 1: Biodata Pribadi Calon Mahasiswa', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_pendataan, 'F3 Step Sub', 80, 238, 'Pastikan data yang Anda masukkan sesuai dengan Kartu Keluarga (KK) dan Ijazah asli Anda.', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f_pendataan, 'F3 Form Div', 80, 265, 1280, 1, fill_hex=C_BORDER)

# Two-Column Fields Grid
c1_inputs = [
    ('Nomor Induk Kependudukan (NIK) *', '3302192804040003 (16 digit sesuai KTP/KK)'),
    ('Nomor Induk Siswa Nasional (NISN) *', '0058291042 (10 digit terdaftar di Dapodik)'),
    ('Nama Lengkap Calon Mahasiswa *', 'Muhammad Irfan (Sesuai Ijazah)'),
    ('Jenis Kelamin *', 'Laki-laki (Pilihan)'),
    ('Tempat Lahir *', 'Semarang'),
    ('Tanggal Lahir *', '14 / 08 / 2005 (DD/MM/YYYY)')
]
fy = 285
for lbl, val in c1_inputs:
    add_text(f_pendataan, f'F3 Lbl {lbl}', 80, fy, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f_pendataan, f'F3 Inp {lbl}', 80, fy + 20, 615, 42, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
    add_text(f_pendataan, f'F3 Val {lbl}', 96, fy + 32, val, font_size=12, color_hex=C_TEXT_PRIMARY)
    fy += 82

c2_inputs = [
    ('Agama *', 'Islam (Pilihan)'),
    ('Nomor Handphone / WhatsApp Aktif *', '081234567890'),
    ('Alamat Lengkap Tempat Tinggal *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'),
    ('Kelurahan / Desa *', 'Sekaran'),
    ('Kecamatan *', 'Gunungpati'),
    ('Kabupaten / Kota *', 'Kota Semarang, Jawa Tengah')
]
fy2 = 285
for lbl, val in c2_inputs:
    add_text(f_pendataan, f'F3 Lbl {lbl}', 745, fy2, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f_pendataan, f'F3 Inp {lbl}', 745, fy2 + 20, 615, 42, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
    add_text(f_pendataan, f'F3 Val {lbl}', 761, fy2 + 32, val, font_size=12, color_hex=C_TEXT_PRIMARY)
    fy2 += 82

add_rect(f_pendataan, 'F3 Bottom Bar Div', 80, 800, 1280, 1, fill_hex=C_BORDER)
add_rect(f_pendataan, 'F3 Btn Save Draft', 80, 825, 180, 46, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=8)
add_text(f_pendataan, 'F3 Btn Save Draft Txt', 120, 840, 'Simpan Draf', font_size=12, color_hex=C_TEXT_SEC)

add_rect(f_pendataan, 'F3 Btn Next', 1085, 825, 275, 46, fill_hex=C_BLUE, radius=8)
add_text(f_pendataan, 'F3 Btn Next Txt', 1115, 840, 'Simpan & Lanjut ke Tahap 2 →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

add_text(f_pendataan, 'F3 Footer', 48, 945, '© 2026 Universitas Negeri Semarang — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi.', font_size=11, color_hex=C_TEXT_MUTED)

print("Frames Part 1 defined successfully!")

# ==========================================
# 05. Unggahan (Upload Dokumen Persyaratan)
# ==========================================
f_unggah = add_frame('Unggahan', 4620.0, 0.0)

add_rect(f_unggah, 'F4 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_unggah, 'F4 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_unggah, 'F4 Sub', 220, 24, 'Unggah Berkas Dokumen Persyaratan & Penerbitan Kartu Tanda Peserta CBT', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f_unggah, 'F4 Verified Badge', 1010, 18, 160, 28, fill_hex=C_SUCCESS_BG, stroke_hex=C_SUCCESS_BORDER, radius=14)
add_text(f_unggah, 'F4 Verified Txt', 1032, 24, 'TERVERIFIKASI', font_size=11, color_hex='#065f46', font_weight='Bold')
add_text(f_unggah, 'F4 User Profile', 1185, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Upload Area Container
add_rect(f_unggah, 'F4 Up BG', 48, 95, 690, 840, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)
add_text(f_unggah, 'F4 Up Title', 80, 125, 'Langkah 3: Unggah Dokumen Persyaratan', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_unggah, 'F4 Up Sub', 80, 152, 'Format file yang diperbolehkan: PDF / JPG / PNG (Maksimal 2 MB per file).', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f_unggah, 'F4 Up Div', 80, 180, 626, 1, fill_hex=C_BORDER)

doc_uploads = [
    ('1. Ijazah SMA / Surat Keterangan Lulus (SKL) *', 'ijazah_irfan_2026.pdf (1.2 MB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('2. Kartu Keluarga (KK) Legalisir *', 'kk_keluarga_irfan.pdf (890 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('3. Pas Foto Resmi 4x6 Background Merah *', 'foto_formal_4x6.jpg (450 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('4. Sertifikat Prestasi / Portofolio Kejuaraan', 'sertifikat_osn_nasional.pdf (1.8 MB)', 'Juara 1 OSN Informatika Nasional • Jalur Mandiri Prestasi')
]
uy = 200
for dtitle, dfile, dnote in doc_uploads:
    add_rect(f_unggah, f'F4 Box {dtitle}', 80, uy, 626, 135, fill_hex='#f8fafc', stroke_hex=C_BORDER, stroke_width=1.5, radius=12)
    add_text(f_unggah, f'F4 Title {dtitle}', 104, uy + 16, dtitle, font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f_unggah, f'F4 File {dtitle}', 104, uy + 42, dfile, font_size=12, color_hex=C_BLUE, font_weight='Bold')
    add_text(f_unggah, f'F4 Note {dtitle}', 104, uy + 64, dnote, font_size=11, color_hex=C_TEXT_MUTED)
    add_rect(f_unggah, f'F4 Btn {dtitle}', 104, uy + 90, 140, 32, fill_hex=C_BLUE, radius=6)
    add_text(f_unggah, f'F4 BtnTxt {dtitle}', 130, uy + 98, 'Unggah Berkas', font_size=11, color_hex=C_WHITE, font_weight='Bold')
    uy += 155

# Right Column: Kartu Peserta Preview
add_rect(f_unggah, 'F4 Card BG', 768, 95, 624, 840, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)
add_text(f_unggah, 'F4 Card Title', 800, 125, 'Kartu Tanda Peserta Ujian PMB UNNES 2026', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_unggah, 'F4 Card Sub', 800, 152, 'Kartu ini wajib dicetak dan dibawa saat pelaksanaan Ujian CBT di kampus Sekaran.', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f_unggah, 'F4 Card Div', 800, 180, 560, 1, fill_hex=C_BORDER)

add_rect(f_unggah, 'F4 Pass Outer', 800, 205, 560, 530, fill_hex='#f0f9ff', stroke_hex='#bae6fd', radius=14)
add_rect(f_unggah, 'F4 Pass Header', 800, 205, 560, 64, fill_hex=C_DARK_BLUE, radius=[14, 14, 0, 0])
add_text(f_unggah, 'F4 Pass H1', 825, 218, 'KARTU TANDA PESERTA SELEKSI MANDIRI 2026', font_size=13, color_hex=C_WHITE, font_weight='Bold')
add_text(f_unggah, 'F4 Pass H2', 825, 238, 'UNIVERSITAS NEGERI SEMARANG (KAMPUS KONSERVASI)', font_size=10, color_hex='#e0f2fe')

add_image_rect(f_unggah, 'F4 Student Photo', 825, 290, 140, 185, 'student_id_photo.jpg', radius=8)
add_text(f_unggah, 'F4 P1 Lbl', 990, 295, 'Nomor Peserta Ujian:', font_size=10, color_hex=C_TEXT_MUTED)
add_text(f_unggah, 'F4 P1 Val', 990, 310, '26-3302-08492', font_size=15, color_hex=C_BLUE, font_weight='Bold')
add_text(f_unggah, 'F4 P2 Lbl', 990, 335, 'Nama Lengkap Mahasiswa:', font_size=10, color_hex=C_TEXT_MUTED)
add_text(f_unggah, 'F4 P2 Val', 990, 350, 'MUHAMMAD IRFAN', font_size=14, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_unggah, 'F4 P3 Lbl', 990, 375, 'Program Studi Pilihan Utama:', font_size=10, color_hex=C_TEXT_MUTED)
add_text(f_unggah, 'F4 P3 Val', 990, 390, 'S1 TEKNIK INFORMATIKA (FMIPA)', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

add_rect(f_unggah, 'F4 QR Code', 825, 495, 110, 110, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=6)
add_text(f_unggah, 'F4 QR Text', 840, 545, '[ BARCODE QR ]', font_size=9, color_hex=C_BLUE, font_weight='Bold')
add_text(f_unggah, 'F4 QR Desc', 955, 520, 'Kode Validasi Keaslian Sistem PMB Online:', font_size=10, color_hex=C_TEXT_MUTED)
add_text(f_unggah, 'F4 QR Hash', 955, 538, 'SHA256: 8a719d8ab694f5af87c48d9accede8a7', font_size=10, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

# ==========================================
# 06. Dokumen/Persuratan Admin (Panel Verifikasi)
# ==========================================
f_admin = add_frame('Dokumen/Persuratan Admin', 6160.0, 0.0)

# Sidebar Left
add_rect(f_admin, 'F5 Side BG', 0, 0, 240, 1000, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_rect(f_admin, 'F5 Side Logo BG', 24, 24, 38, 38, fill_hex=C_BLUE, radius=8)
add_text(f_admin, 'F5 Side Logo Txt', 34, 34, 'UN', font_size=14, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'F5 Side Title', 72, 26, 'PMB Admin Panel', font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_admin, 'F5 Side Sub', 72, 46, 'Sistem Verifikasi Berkas', font_size=10, color_hex=C_TEXT_MUTED)
add_rect(f_admin, 'F5 Side Div', 24, 76, 192, 1, fill_hex=C_BORDER)

admin_menus = [
    ('Dashboard Ringkasan', False),
    ('Antrean Verifikasi (42)', True),
    ('Data Seluruh Pendaftar', False),
    ('Master Program Studi', False),
    ('Jalur & Kuota Seleksi', False),
    ('Pengumuman Kelulusan', False),
    ('Audit Log & Laporan', False)
]
smy = 95
for mtitle, mact in admin_menus:
    mbg = C_PRIMARY_SUBTLE if mact else C_WHITE
    mtxt = C_BLUE if mact else C_TEXT_SEC
    add_rect(f_admin, f'F5 Mnu {mtitle}', 16, smy, 208, 38, fill_hex=mbg, radius=6)
    add_text(f_admin, f'F5 MnuTxt {mtitle}', 32, smy + 11, mtitle, font_size=12, color_hex=mtxt, font_weight='Bold' if mact else 'Regular')
    smy += 44

# Main Admin Table Area
add_rect(f_admin, 'F5 Header BG', 240, 0, 1200, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_admin, 'F5 Header Title', 272, 22, 'Antrean Verifikasi Berkas Pendaftar', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

add_rect(f_admin, 'F5 Table BG', 272, 95, 1128, 855, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_rect(f_admin, 'F5 Table Th', 296, 130, 1080, 42, fill_hex=C_BLUE, radius=[8, 8, 0, 0])
add_text(f_admin, 'F5 Th 1', 316, 144, 'NO. PENDAFTARAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'F5 Th 2', 480, 144, 'NAMA LENGKAP & NISN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'F5 Th 3', 720, 144, 'PROGRAM STUDI PILIHAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'F5 Th 4', 975, 144, 'STATUS BERKAS', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'F5 Th 5', 1210, 144, 'AKSI VERIFIKASI', font_size=11, color_hex=C_WHITE, font_weight='Bold')

rows_panitia = [
    ('PMB-2026-08492', 'Muhammad Irfan', 'NISN: 0058291042', 'S1 Teknik Informatika', 'Jalur Mandiri Prestasi', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309', True),
    ('PMB-2026-08493', 'Siti Nurhaliza', 'NISN: 0057193821', 'S1 Sistem Informasi', 'Jalur SNBP (Prestasi)', 'PERLU REVISI', '#fff1f2', '#fecdd3', '#be123c', False),
    ('PMB-2026-08494', 'Budi Santoso', 'NISN: 0059281742', 'S1 Teknik Elektro', 'Jalur SNBT (UTBK)', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False),
    ('PMB-2026-08495', 'Annisa Rahmawati', 'NISN: 0056192841', 'S1 Pendidikan Matematika', 'Jalur Mandiri Reguler', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309', False),
    ('PMB-2026-08496', 'Dimas Arya Pratama', 'NISN: 0058918274', 'S1 Ilmu Komputer', 'Jalur Mandiri Prestasi', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False),
    ('PMB-2026-08497', 'Fadhilah Nurul Hidayah', 'NISN: 0057281932', 'S1 Farmasi', 'Jalur SNBP (Prestasi)', 'PERLU REVISI', '#fff1f2', '#fecdd3', '#be123c', False),
    ('PMB-2026-08498', 'Rizky Ramadhan', 'NISN: 0059182736', 'S1 Manajemen', 'Jalur SNBT (UTBK)', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False)
]
ty = 172
for i, (rno, rname, rnisn, rprodi, rjalur, rst, rbg, rbrd, rtxt, rhl) in enumerate(rows_panitia):
    row_bg = '#f0f9ff' if rhl else (C_WHITE if i % 2 == 0 else '#f8fafc')
    add_rect(f_admin, f'F5 Row {rno}', 296, ty, 1080, 60, fill_hex=row_bg, stroke_hex='#f1f5f9')
    add_text(f_admin, f'F5 RNo {rno}', 316, ty + 22, rno, font_size=12, color_hex=C_BLUE, font_weight='Bold')
    add_text(f_admin, f'F5 RName {rno}', 480, ty + 14, rname, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f_admin, f'F5 RNISN {rno}', 480, ty + 34, rnisn, font_size=10, color_hex=C_TEXT_MUTED)
    add_text(f_admin, f'F5 RProdi {rno}', 720, ty + 14, rprodi, font_size=12, color_hex=C_TEXT_SEC)
    add_text(f_admin, f'F5 RJalur {rno}', 720, ty + 34, rjalur, font_size=10, color_hex=C_TEXT_MUTED)
    add_rect(f_admin, f'F5 RBadge {rno}', 975, ty + 17, 125, 26, fill_hex=rbg, stroke_hex=rbrd, radius=6)
    add_text(f_admin, f'F5 RBadgeTxt {rno}', 995, ty + 23, rst, font_size=10, color_hex=rtxt, font_weight='Bold')
    btn_fill = C_BLUE if rhl else C_WHITE
    btn_txt = C_WHITE if rhl else C_TEXT_PRIMARY
    add_rect(f_admin, f'F5 RBtn {rno}', 1210, ty + 13, 130, 34, fill_hex=btn_fill, stroke_hex=C_BORDER, radius=6)
    add_text(f_admin, f'F5 RBtnTxt {rno}', 1238, ty + 22, 'Periksa Berkas', font_size=11, color_hex=btn_txt, font_weight='Bold')
    ty += 60

# ==========================================
# 07. Pengumuman Kelulusan
# ==========================================
f_pengumuman = add_frame('Pengumuman', 7700.0, 0.0)

add_rect(f_pengumuman, 'F8 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_pengumuman, 'F8 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_pengumuman, 'F8 Nav 1', 220, 24, 'Hasil Kelulusan', font_size=13, color_hex=C_BLUE, font_weight='Bold')
add_rect(f_pengumuman, 'F8 Nav Ind', 220, 62, 90, 2, fill_hex=C_BLUE)

# Green Success Banner
add_rect(f_pengumuman, 'F8 Hero BG', 48, 88, 1344, 175, fill_hex='#059669', radius=16)
add_rect(f_pengumuman, 'F8 Tag Badge', 80, 110, 360, 24, fill_hex='#047857', radius=12)
add_text(f_pengumuman, 'F8 Tag Badge Txt', 95, 115, 'PENGUMUMAN HASIL KELULUSAN AKHIR PMB TA 2026/2027', font_size=10, color_hex=C_WHITE, font_weight='Bold')
add_text(f_pengumuman, 'F8 Hero Title', 80, 145, 'SELAMAT! ANDA DINYATAKAN LULUS SELEKSI', font_size=26, color_hex=C_WHITE, font_weight='Bold')
add_text(f_pengumuman, 'F8 Hero Sub', 80, 182, 'Universitas Negeri Semarang mengucapkan selamat bergabung dengan keluarga besar sivitas akademika UNNES.', font_size=13, color_hex='#d1fae5')
add_text(f_pengumuman, 'F8 Hero Reg', 80, 208, 'Nomor Peserta: PMB-2026-08492   •   Jalur Masuk: Seleksi Mandiri Prestasi Unggul (SM-UNNES)', font_size=12, color_hex='#a7f3d0')

# Left Student Details Card
add_rect(f_pengumuman, 'F8 Left Card BG', 48, 280, 656, 630, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f_pengumuman, 'F8 Left Title', 80, 305, '1. Rincian Penetapan Program Studi & Kelulusan', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f_pengumuman, 'F8 Left Div', 80, 350, 592, 1, fill_hex=C_BORDER)

student_details = [
    ('Nama Lengkap Mahasiswa', 'Muhammad Irfan'),
    ('Nomor Registrasi / Pendaftaran', 'PMB-2026-08492'),
    ('NISN / NIK', '0058291042 / 3302192804040003'),
    ('Program Studi Diterima', 'S1 - Teknik Informatika (Reguler)'),
    ('Fakultas Terpilih', 'Fakultas Matematika dan Ilmu Pengetahuan Alam (FMIPA)'),
    ('Jenjang Pendidikan', 'Sarjana (S1) — Akreditasi Unggul BAN-PT'),
    ('Kelompok UKT Ditetapkan', 'Golongan III (Rp 4.500.000 / semester)'),
    ('Nomor Virtual Account Bank', '9880-0058-2910-4200 (Bank BNI)'),
    ('Batas Waktu Pembayaran UKT', '25 Juli 2026, Pukul 15:00 WIB'),
    ('Status Verifikasi Dokumen', '100% Terverifikasi Lengkap (Sah)')
]
sdy = 365
for slbl, sval in student_details:
    add_text(f_pengumuman, f'F8 Lbl {slbl}', 80, sdy, slbl, font_size=10, color_hex=C_TEXT_MUTED)
    txt_color = C_BLUE if 'Teknik' in sval or '4.500.000' in sval or 'Sah' in sval else C_TEXT_PRIMARY
    add_text(f_pengumuman, f'F8 Val {slbl}', 310, sdy, sval, font_size=11, color_hex=txt_color, font_weight='Bold')
    add_rect(f_pengumuman, f'F8 Div {slbl}', 80, sdy + 18, 592, 1, fill_hex='#f1f5f9')
    sdy += 34

# Right Card: Re-registration steps
add_rect(f_pengumuman, 'F8 Right Card BG', 736, 280, 656, 630, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f_pengumuman, 'F8 Right Title', 768, 305, '2. Alur & Panduan Wajib Registrasi Ulang', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f_pengumuman, 'F8 Right Div', 768, 350, 592, 1, fill_hex=C_BORDER)

# Step 1: UKT
add_rect(f_pengumuman, 'F8 S1 BG', 768, 365, 592, 115, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=10)
add_text(f_pengumuman, 'F8 S1 Title', 790, 382, 'Langkah 1: Pembayaran Uang Kuliah Tunggal (UKT)', font_size=13, color_hex='#15803d', font_weight='Bold')
add_text(f_pengumuman, 'F8 S1 Desc', 790, 404, 'Lakukan pembayaran sebesar Rp 4.500.000 melalui Virtual Account BNI (9880-0058-2910-4200)', font_size=11, color_hex='#166534')
add_text(f_pengumuman, 'F8 S1 Note', 790, 448, 'Tenggat Waktu: 25 Juli 2026, 15:00 WIB (Sistem otomatis memverifikasi pelunasan).', font_size=10, color_hex='#15803d', font_weight='Bold')

# Step 2: SIMREG Online
add_rect(f_pengumuman, 'F8 S2 BG', 768, 492, 592, 105, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=10)
add_text(f_pengumuman, 'F8 S2 Title', 790, 508, 'Langkah 2: Registrasi Online & Pengisian Ukuran Jas Almamater', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_pengumuman, 'F8 S2 Desc', 790, 530, 'Isi data induk mahasiswa (SIMREG), riwayat kesehatan, dan ukuran jas almamater', font_size=11, color_hex=C_TEXT_MUTED)

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/projek-ansi.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack into projek-ansi.figcraft zip directly with images!
zip_path = 'C:/projects/ta-pemweb/uidesign/projek-ansi.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully compiled projek-ansi.figcraft with {len(doc["nodes"])} nodes and {len(images_meta)} images!')
