import zipfile, hashlib, json, os
from PIL import Image

assets_dir = 'C:/projects/ta-pemweb/uidesign/assets'
images_meta = {}
for fname in os.listdir(assets_dir):
    fpath = os.path.join(assets_dir, fname)
    if os.path.isfile(fpath):
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

image_index = []
for fname, meta in images_meta.items():
    image_index.append({
        'hash': meta['hash'],
        'width': meta['width'],
        'height': meta['height']
    })

doc = {
    'comments': [],
    'current_page': 1,
    'document_colors': [],
    'format': 'figcraft',
    'imageIndex': image_index,
    'name': 'pmb-ui-concept',
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

def add_frame(name, x, y, w=1440.0, h=1000.0, bg_hex='#f8fafc'):
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

def add_text(parent_id, name, x, y, characters, font_size=13.0, color_hex='#0f172a', font_weight='Regular', font_family='Inter', width=None, height=None):
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

# Color Theme: UNNES Campus Portal Blue & White (Sesuai Figma PROJEK-ANSI)
C_BLUE = '#0284c7'         # Sky Blue Primary
C_DARK_BLUE = '#0369a1'    # Deep Blue
C_LIGHT_BLUE = '#e0f2fe'   # Soft Blue Accent
C_PRIMARY_SUBTLE = '#f0f9ff' # Sky Blue Subtle
C_AMBER = '#f59e0b'        # Gold / Amber Accent
C_NAVY = '#0f172a'         # Dark Navy Text/Bars
C_WHITE = '#ffffff'
C_CANVAS = '#f8fafc'
C_BORDER = '#e2e8f0'
C_TEXT_PRIMARY = '#0f172a'
C_TEXT_SEC = '#334155'
C_TEXT_MUTED = '#64748b'

# ==========================================
# 01. BERANDA PORTAL PMB (X = 0)
# ==========================================
f1 = add_frame('01. Beranda Portal PMB', 0.0, 0.0)

# Top Info Bar
add_rect(f1, 'F1 Top Bar', 0, 0, 1440, 36, fill_hex=C_DARK_BLUE)
add_text(f1, 'F1 Top L', 48, 10, 'Call Center: (024) 8508093  |  Email: pmb@mail.unnes.ac.id  |  Gedung Rektorat Kampus Sekaran', font_size=11, color_hex='#e0f2fe')
add_text(f1, 'F1 Top R', 1040, 10, 'Jadwal Seleksi TA 2026/2027  |  Buku Panduan PMB (PDF)', font_size=11, color_hex='#e0f2fe')

# Main Header
add_rect(f1, 'F1 Nav BG', 0, 36, 1440, 76, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_rect(f1, 'F1 Logo Badge', 48, 52, 42, 42, fill_hex=C_BLUE, radius=8)
add_text(f1, 'F1 Logo Txt', 57, 62, 'UN', font_size=16, color_hex=C_WHITE, font_weight='Bold')
add_text(f1, 'F1 Brand Name', 102, 53, 'PMB UNNES 2026', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f1, 'F1 Brand Sub', 102, 75, 'Penerimaan Mahasiswa Baru Universitas Negeri Semarang', font_size=11, color_hex=C_TEXT_MUTED)

navs = ['Beranda', 'Jalur Masuk', 'Program Studi', 'Biaya Kuliah', 'Pengumuman', 'Kontak']
nx = 580
for nv in navs:
    add_text(f1, f'F1 Nav {nv}', nx, 66, nv, font_size=13, color_hex=C_TEXT_SEC)
    nx += 105

add_rect(f1, 'F1 Btn Login', 1248, 53, 144, 42, fill_hex=C_BLUE, radius=8)
add_text(f1, 'F1 Btn Login Txt', 1278, 65, 'Masuk / Daftar', font_size=13, color_hex=C_WHITE, font_weight='Bold')

# Hero Banner with Real Campus Photo Background
add_image_rect(f1, 'F1 Hero Photo BG', 48, 132, 1344, 380, 'hero_campus.jpg', radius=16)
add_rect(f1, 'F1 Hero Gradient Overlay', 48, 132, 1344, 380, fill_hex=C_DARK_BLUE, opacity=0.82, radius=16)

add_rect(f1, 'F1 Hero Badge', 80, 165, 310, 26, fill_hex=C_WHITE, opacity=0.2, radius=13)
add_text(f1, 'F1 Hero Badge Txt', 94, 171, 'PENDAFTARAN MAHASISWA BARU TA 2026/2027', font_size=10, color_hex=C_WHITE, font_weight='Bold')

add_text(f1, 'F1 Hero Title 1', 80, 204, 'Selamat Datang di Portal PMB', font_size=32, color_hex=C_WHITE, font_weight='Bold')
add_text(f1, 'F1 Hero Title 2', 80, 246, 'Universitas Negeri Semarang', font_size=32, color_hex=C_AMBER, font_weight='Bold')

add_text(f1, 'F1 Hero Lead 1', 80, 300, 'Wujudkan impian studi di Kampus Konservasi Bereputasi Internasional.', font_size=14, color_hex='#e0f2fe')
add_text(f1, 'F1 Hero Lead 2', 80, 322, 'Sistem seleksi digital terpadu, verifikasi berkas cepat, dan notifikasi real-time.', font_size=14, color_hex='#e0f2fe')

add_rect(f1, 'F1 Hero Btn 1', 80, 365, 200, 48, fill_hex=C_AMBER, radius=8)
add_text(f1, 'F1 Hero Btn 1 Txt', 110, 380, 'Daftar Akun Baru →', font_size=13, color_hex=C_NAVY, font_weight='Bold')

add_rect(f1, 'F1 Hero Btn 2', 295, 365, 200, 48, fill_hex=C_WHITE, stroke_hex='#cbd5e1', radius=8)
add_text(f1, 'F1 Hero Btn 2 Txt', 325, 380, 'Panduan Pendaftaran', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

# Cutout Student Card & Telemetry on Hero
add_image_rect(f1, 'F1 Hero Student Img', 780, 160, 250, 320, 'student_hero.png', radius=14)

add_rect(f1, 'F1 Stat Card BG', 1055, 175, 305, 230, fill_hex=C_WHITE, radius=14)
add_text(f1, 'F1 Stat Card Title', 1080, 198, 'Statistik Seleksi Aktif', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f1, 'F1 Stat Card Div', 1080, 225, 255, 1, fill_hex=C_BORDER)

add_text(f1, 'F1 Stat 1 Lbl', 1080, 238, 'Total Pendaftar Terverifikasi:', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f1, 'F1 Stat 1 Val', 1080, 254, '1,428 Siswa', font_size=18, color_hex=C_BLUE, font_weight='Bold')

add_text(f1, 'F1 Stat 2 Lbl', 1080, 285, 'Pilihan Program Studi:', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f1, 'F1 Stat 2 Val', 1080, 301, '72 Program Studi (Unggul)', font_size=14, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

add_rect(f1, 'F1 Stat Pill', 1080, 335, 255, 32, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=6)
add_text(f1, 'F1 Stat Pill Txt', 1098, 344, 'Status Sistem: ONLINE • Pendaftaran Aktif', font_size=10, color_hex='#15803d', font_weight='Bold')

# 3 Feature Cards with Real Photography Headers (Jalur Seleksi)
add_text(f1, 'F1 Sec Title', 48, 535, 'PILIHAN JALUR SELEKSI PMB 2026', font_size=20, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f1, 'F1 Sec Sub', 48, 562, 'Pilih Jalur Masuk Sesuai Kualifikasi & Prestasi Akademik Anda', font_size=13, color_hex=C_TEXT_MUTED)

jalur_items = [
    ('card_snbp.jpg', 'SNBP (Jalur Prestasi Nasional)', 'Seleksi nasional berdasarkan prestasi nilai rapor semester 1-5 dan portofolio kejuaraan.', 'Jadwal: 10 Nov - 20 Des 2026', 'Bebas Biaya Pendaftaran', 48),
    ('card_snbt.jpg', 'SNBT (Jalur UTBK Nasional)', 'Seleksi nasional berbasis tes skolastik dan literasi terstandar yang diselenggarakan BPPP.', 'Jadwal: 15 Jan - 28 Feb 2027', 'Biaya Tes: Rp 200.000', 508),
    ('card_mandiri.jpg', 'SM-UNNES (Jalur Mandiri)', 'Seleksi mandiri perguruan tinggi berbasis ujian CBT terpadu UNNES dan prestasi unggul.', 'Jadwal: 01 Mar - 15 Apr 2027', 'Biaya Ujian: Rp 300.000', 968)
]
for jimg, jtitle, jdesc, jdate, jcost, jx in jalur_items:
    add_rect(f1, f'F1 JCard {jtitle} BG', jx, 595, 424, 320, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f1, f'F1 JCard {jtitle} Img', jx, 595, 424, 135, jimg, radius=[14, 14, 0, 0])
    
    add_text(f1, f'F1 JCard {jtitle} Title', jx + 20, 745, jtitle, font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f1, f'F1 JCard {jtitle} Desc', jx + 20, 768, jdesc, font_size=11, color_hex=C_TEXT_SEC, width=384, height=35)
    
    add_text(f1, f'F1 JCard {jtitle} Date', jx + 20, 812, jdate, font_size=11, color_hex=C_BLUE, font_weight='Bold')
    add_text(f1, f'F1 JCard {jtitle} Cost', jx + 20, 830, jcost, font_size=10, color_hex=C_TEXT_MUTED)
    
    add_rect(f1, f'F1 JCard {jtitle} Btn', jx + 20, 860, 384, 38, fill_hex=C_PRIMARY_SUBTLE, stroke_hex='#bae6fd', radius=8)
    add_text(f1, f'F1 JCard {jtitle} BtnTxt', jx + 130, 872, 'Lihat Informasi Selengkapnya →', font_size=11, color_hex=C_BLUE, font_weight='Bold')

# Footer
add_rect(f1, 'F1 Footer BG', 0, 935, 1440, 65, fill_hex=C_BLUE)
add_text(f1, 'F1 Footer Copy', 48, 960, '© 2026 Universitas Negeri Semarang — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi.', font_size=11, color_hex=C_WHITE)

# ==========================================
# 02. LOGIN & REGISTRASI AKUN (X = 1540)
# ==========================================
f2 = add_frame('02. Login & Registrasi Akun', 1540.0, 0.0)

# Full Left Wall with Real Library Background Photo
add_image_rect(f2, 'F2 Library Wall', 1540 - 1540, 0, 680, 1000, 'library_bg.jpg')
add_rect(f2, 'F2 Library Overlay', 0, 0, 680, 1000, fill_hex=C_NAVY, opacity=0.78)

# Glass Information Card on Left
add_rect(f2, 'F2 Glass Card', 64, 60, 552, 880, fill_hex=C_WHITE, stroke_hex='#ffffff40', radius=18, opacity=0.15)
add_text(f2, 'F2 Auth Brand', 96, 95, 'PMB UNNES 2026', font_size=20, color_hex=C_WHITE, font_weight='Bold')
add_text(f2, 'F2 Info Title', 96, 135, 'Pendaftaran Akun Baru PMB', font_size=24, color_hex=C_WHITE, font_weight='Bold')
add_text(f2, 'F2 Info Sub 1', 96, 172, 'Gunakan satu akun resmi untuk seluruh tahapan seleksi', font_size=13, color_hex='#e0f2fe')
add_text(f2, 'F2 Info Sub 2', 96, 192, 'penerimaan mahasiswa baru di Universitas Negeri Semarang.', font_size=13, color_hex='#e0f2fe')

steps_login = [
    ('1', 'Registrasi Akun Siswa', 'Daftarkan email aktif dan NISN Anda yang valid.'),
    ('2', 'Lengkapi Biodata Diri', 'Isi formulir biodata pribadi, keluarga, dan asal sekolah.'),
    ('3', 'Pilih Jalur & Prodi', 'Pilih jalur pendaftaran serta 2 pilihan program studi.'),
    ('4', 'Unggah Berkas Dokumen', 'Upload file Ijazah/SKL, KK, dan Pas Foto sesuai ketentuan.'),
    ('5', 'Finalisasi & Cetak Kartu', 'Periksa kebenaran data lalu cetak Kartu Peserta CBT.')
]
sy = 235
for num, stitle, sdesc in steps_login:
    add_rect(f2, f'F2 SBox {num}', 96, sy, 488, 76, fill_hex=C_WHITE, stroke_hex='#ffffff30', radius=10, opacity=0.12)
    add_rect(f2, f'F2 SNum BG {num}', 116, sy + 18, 40, 40, fill_hex=C_BLUE, radius=20)
    add_text(f2, f'F2 SNum {num}', 131, sy + 29, num, font_size=14, color_hex=C_WHITE, font_weight='Bold')
    add_text(f2, f'F2 STitle {num}', 172, sy + 18, stitle, font_size=13, color_hex=C_WHITE, font_weight='Bold')
    add_text(f2, f'F2 SDesc {num}', 172, sy + 40, sdesc, font_size=11, color_hex='#cbd5e1')
    sy += 88

add_rect(f2, 'F2 Help Box', 96, 860, 488, 48, fill_hex='#0369a1', radius=8)
add_text(f2, 'F2 Help Txt', 120, 876, 'Butuh bantuan? Hubungi WhatsApp Helpdesk: 0812-3456-7890', font_size=11, color_hex=C_WHITE, font_weight='Bold')

# Right Login Form Panel
add_rect(f2, 'F2 Right Panel', 680, 0, 760, 1000, fill_hex=C_WHITE)
add_text(f2, 'F2 Back Link', 740, 45, '← Kembali ke Beranda Portal', font_size=12, color_hex=C_BLUE, font_weight='Bold')

# Tab Switcher
add_rect(f2, 'F2 Tab Box', 740, 95, 600, 48, fill_hex='#f1f5f9', radius=10)
add_rect(f2, 'F2 Tab Active', 744, 99, 296, 40, fill_hex=C_WHITE, radius=8)
add_text(f2, 'F2 Tab 1 Txt', 835, 111, 'Masuk ke Akun', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f2, 'F2 Tab 2 Txt', 1130, 111, 'Daftar Akun Baru', font_size=13, color_hex=C_TEXT_MUTED)

add_text(f2, 'F2 Form Title', 740, 185, 'Masuk ke Akun PMB', font_size=24, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f2, 'F2 Form Sub', 740, 218, 'Masukkan email atau NISN dan kata sandi yang telah terdaftar.', font_size=13, color_hex=C_TEXT_MUTED)

# Inputs
add_text(f2, 'F2 Lbl 1', 740, 275, 'Alamat Email atau NISN *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f2, 'F2 Inp 1', 740, 300, 600, 48, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f2, 'F2 Inp 1 Val', 756, 315, 'irfan@mail.com atau 0058291042', font_size=13, color_hex=C_TEXT_PRIMARY)

add_text(f2, 'F2 Lbl 2', 740, 375, 'Kata Sandi (Password) *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f2, 'F2 Inp 2', 740, 400, 600, 48, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f2, 'F2 Inp 2 Val', 756, 415, '••••••••••••••••', font_size=13, color_hex=C_TEXT_PRIMARY)

add_text(f2, 'F2 Remember', 740, 470, '[X] Ingat Saya di Perangkat Ini', font_size=12, color_hex=C_TEXT_SEC)
add_text(f2, 'F2 Forgot', 1230, 470, 'Lupa Password?', font_size=12, color_hex=C_BLUE, font_weight='Bold')

add_rect(f2, 'F2 Submit Btn', 740, 515, 600, 50, fill_hex=C_BLUE, radius=8)
add_text(f2, 'F2 Submit Btn Txt', 980, 531, 'Masuk Sekarang →', font_size=14, color_hex=C_WHITE, font_weight='Bold')

add_rect(f2, 'F2 Div Line', 740, 610, 600, 1, fill_hex=C_BORDER)

# Register Callout
add_rect(f2, 'F2 Reg Callout', 740, 645, 600, 140, fill_hex='#f0f9ff', stroke_hex='#bae6fd', radius=12)
add_text(f2, 'F2 Reg CT', 768, 668, 'Belum memiliki akun pendaftaran?', font_size=14, color_hex=C_DARK_BLUE, font_weight='Bold')
add_text(f2, 'F2 Reg CD', 768, 692, 'Daftarkan diri Anda sekarang dengan NISN yang terdaftar di Dapodik Kemendikbud.', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f2, 'F2 Reg CBtn', 768, 722, 544, 42, fill_hex=C_WHITE, stroke_hex=C_BLUE, radius=8)
add_text(f2, 'F2 Reg CBtn Txt', 930, 734, 'Registrasi Akun Baru Siswa (Gratis)', font_size=12, color_hex=C_BLUE, font_weight='Bold')

add_text(f2, 'F2 Sec Footer', 740, 830, 'Sistem keamanan data terenkripsi SSL 256-bit dan mematuhi UU Perlindungan Data Pribadi (UU PDP).', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 03. FORMULIR PENDAFTARAN MULTI-STEP (X = 3080)
# ==========================================
f3 = add_frame('03. Formulir Pendaftaran Multi-Step', 3080.0, 0.0)

# Top Bar
add_rect(f3, 'F3 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f3, 'F3 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f3, 'F3 Title', 220, 24, 'Formulir Pendaftaran Calon Mahasiswa Baru TA 2026/2027', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f3, 'F3 Draft Badge', 1030, 18, 90, 28, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=14)
add_text(f3, 'F3 Draft Badge Txt', 1052, 24, 'DRAFT', font_size=11, color_hex='#b45309', font_weight='Bold')
add_text(f3, 'F3 User Pill', 1135, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Stepper Bar with Circles and Connectors
add_rect(f3, 'F3 Stepper BG', 48, 88, 1344, 76, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
steps_w = [
    ('1', 'Biodata Diri', True),
    ('2', 'Asal Sekolah', False),
    ('3', 'Pilihan Prodi', False),
    ('4', 'Unggah Berkas', False),
    ('5', 'Finalisasi', False)
]
wx = 80
for i, (wnum, wname, wactive) in enumerate(steps_w):
    s_bg = C_BLUE if wactive else '#f1f5f9'
    s_txt = C_WHITE if wactive else '#64748b'
    add_rect(f3, f'F3 SCircle {wnum}', wx, 106, 40, 40, fill_hex=s_bg, radius=20)
    add_text(f3, f'F3 SNum {wnum}', wx + 15, 117, wnum, font_size=13, color_hex=s_txt, font_weight='Bold')
    add_text(f3, f'F3 SName {wnum}', wx + 50, 117, wname, font_size=13, color_hex=C_TEXT_PRIMARY if wactive else C_TEXT_MUTED, font_weight='Bold' if wactive else 'Regular')
    
    if i < 4:
        add_rect(f3, f'F3 SLine {i}', wx + 175, 125, 75, 2, fill_hex='#cbd5e1')
    wx += 265

# Main Form Container
add_rect(f3, 'F3 Form BG', 48, 180, 1344, 740, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)
add_text(f3, 'F3 Step Title', 80, 210, 'Langkah 1: Biodata Pribadi Calon Mahasiswa', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f3, 'F3 Step Sub', 80, 238, 'Pastikan data yang Anda masukkan sesuai dengan Kartu Keluarga (KK) dan Ijazah asli Anda.', font_size=12, color_hex=C_TEXT_MUTED)

add_rect(f3, 'F3 Form Div', 80, 265, 1280, 1, fill_hex=C_BORDER)

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
    add_text(f3, f'F3 Lbl {lbl}', 80, fy, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f3, f'F3 Inp {lbl}', 80, fy + 20, 615, 42, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
    add_text(f3, f'F3 Val {lbl}', 96, fy + 32, val, font_size=12, color_hex=C_TEXT_PRIMARY)
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
    add_text(f3, f'F3 Lbl {lbl}', 745, fy2, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f3, f'F3 Inp {lbl}', 745, fy2 + 20, 615, 42, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
    add_text(f3, f'F3 Val {lbl}', 761, fy2 + 32, val, font_size=12, color_hex=C_TEXT_PRIMARY)
    fy2 += 82

add_rect(f3, 'F3 Bottom Bar Div', 80, 800, 1280, 1, fill_hex=C_BORDER)

add_rect(f3, 'F3 Btn Save Draft', 80, 825, 180, 46, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=8)
add_text(f3, 'F3 Btn Save Draft Txt', 120, 840, 'Simpan Draf', font_size=12, color_hex=C_TEXT_SEC)

add_rect(f3, 'F3 Btn Next', 1085, 825, 275, 46, fill_hex=C_BLUE, radius=8)
add_text(f3, 'F3 Btn Next Txt', 1115, 840, 'Simpan & Lanjut ke Tahap 2 →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

add_text(f3, 'F3 Footer', 48, 945, '© 2026 Universitas Negeri Semarang — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi.', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 04. UNGGAH BERKAS & KARTU PESERTA (X = 4620)
# ==========================================
f4 = add_frame('04. Unggah Berkas & Kartu Peserta', 4620.0, 0.0)

# Top Bar
add_rect(f4, 'F4 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f4, 'F4 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f4, 'F4 Sub', 220, 24, 'Unggah Berkas Dokumen Persyaratan & Penerbitan Kartu Tanda Peserta CBT', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f4, 'F4 Verified Badge', 1010, 18, 160, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f4, 'F4 Verified Txt', 1032, 24, 'TERVERIFIKASI', font_size=11, color_hex='#065f46', font_weight='Bold')
add_text(f4, 'F4 User Profile', 1185, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Left Column: Upload Documents Area (w: 690, h: 840)
add_rect(f4, 'F4 Up BG', 48, 95, 690, 840, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)
add_text(f4, 'F4 Up Title', 80, 125, 'Langkah 4: Unggah Dokumen Persyaratan', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f4, 'F4 Up Sub', 80, 152, 'Format file yang diperbolehkan: PDF / JPG / PNG (Maksimal 2 MB per file).', font_size=12, color_hex=C_TEXT_MUTED)

add_rect(f4, 'F4 Up Div', 80, 180, 626, 1, fill_hex=C_BORDER)

doc_uploads = [
    ('1. Ijazah SMA / Surat Keterangan Lulus (SKL) *', 'ijazah_irfan_2026.pdf (1.2 MB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('2. Kartu Keluarga (KK) Legalisir *', 'kk_keluarga_irfan.pdf (890 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('3. Pas Foto Resmi 4x6 Background Merah *', 'foto_formal_4x6.jpg (450 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('4. Sertifikat Prestasi / Portofolio Kejuaraan', 'sertifikat_osn_nasional.pdf (1.8 MB)', 'Tersimpan di Supabase Storage • Siap diverifikasi')
]
uy = 205
for dtitle, dfile, dnote in doc_uploads:
    add_rect(f4, f'F4 DRow {dtitle}', 80, uy, 626, 92, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=10)
    add_rect(f4, f'F4 DIcon BG {dtitle}', 98, uy + 24, 44, 44, fill_hex=C_PRIMARY_SUBTLE, stroke_hex='#bae6fd', radius=8)
    add_text(f4, f'F4 DIcon {dtitle}', 108, uy + 36, 'DOC', font_size=10, color_hex=C_BLUE, font_weight='Bold')
    
    add_text(f4, f'F4 DTitle {dtitle}', 155, uy + 16, dtitle, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f4, f'F4 DFile {dtitle}', 155, uy + 38, dfile, font_size=11, color_hex=C_BLUE, font_weight='Bold')
    add_text(f4, f'F4 DNote {dtitle}', 155, uy + 58, dnote, font_size=10, color_hex='#15803d')
    
    add_rect(f4, f'F4 DBtn {dtitle}', 596, uy + 28, 96, 36, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=6)
    add_text(f4, f'F4 DBtnTxt {dtitle}', 616, uy + 38, 'Ganti File', font_size=11, color_hex=C_TEXT_SEC)
    uy += 108

# Final Checklist & Submit Button
add_rect(f4, 'F4 Check Box', 80, 665, 626, 68, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f4, 'F4 Check Txt 1', 104, 680, '[X]  Saya menyatakan bahwa semua berkas dan data yang saya unggah adalah asli dan sah.', font_size=11, color_hex='#15803d', font_weight='Bold')
add_text(f4, 'F4 Check Txt 2', 104, 702, 'Apabila ditemukan data palsu, saya bersedia menerima sanksi pembatalan kepesertaan PMB.', font_size=10, color_hex=C_TEXT_MUTED)

add_rect(f4, 'F4 Final Btn', 80, 755, 626, 50, fill_hex=C_BLUE, radius=8)
add_text(f4, 'F4 Final Btn Txt', 225, 770, 'Finalisasi & Ajukan Pendaftaran Sekarang →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

add_text(f4, 'F4 Notice', 80, 825, 'Perhatian: Setelah finalisasi diajukan, data dan berkas pendaftaran terkunci untuk proses verifikasi panitia.', font_size=11, color_hex=C_TEXT_MUTED)

# Right Column: Official Kartu Peserta Ujian PMB (w: 622, h: 840)
add_rect(f4, 'F4 Pass BG', 770, 95, 622, 840, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=16)

# Kop Surat Universitas
add_rect(f4, 'F4 Kop Header', 770, 95, 622, 90, fill_hex='#f0f9ff', radius=[16, 16, 0, 0])
add_text(f4, 'F4 Kop 1', 800, 112, 'KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI', font_size=9, color_hex=C_TEXT_MUTED, font_weight='Bold')
add_text(f4, 'F4 Kop 2', 800, 130, 'UNIVERSITAS NEGERI SEMARANG', font_size=16, color_hex=C_DARK_BLUE, font_weight='Bold')
add_text(f4, 'F4 Kop 3', 800, 154, 'KARTU TANDA PESERTA SELEKSI PMB 2026 — JALUR MANDIRI PRESTASI UNGGUL', font_size=10, color_hex=C_BLUE, font_weight='Bold')
add_rect(f4, 'F4 Kop Line', 800, 185, 562, 2, fill_hex=C_BLUE)

# Student Photo & Data
add_image_rect(f4, 'F4 Real Student Photo', 800, 205, 120, 160, 'student_id_photo.jpg', radius=6)

p_labels = [
    ('Nomor Peserta PMB:', 'PMB-2026-08492'),
    ('Nama Lengkap Siswa:', 'MUHAMMAD IRFAN'),
    ('NISN / NIK:', '0058291042 / 3302192804040003'),
    ('Asal Sekolah:', 'SMA Negeri 1 Semarang'),
    ('Jalur Pendaftaran:', 'Seleksi Mandiri Prestasi Unggul')
]
py = 205
for plbl, pval in p_labels:
    add_text(f4, f'F4 PLbl {plbl}', 940, py, plbl, font_size=10, color_hex=C_TEXT_MUTED)
    add_text(f4, f'F4 PVal {plbl}', 940, py + 16, pval, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    py += 35

# Choice of Majors
add_rect(f4, 'F4 Pilihan Box', 800, 385, 562, 85, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f4, 'F4 Pilihan Header', 816, 398, 'PROGRAM STUDI PILIHAN:', font_size=10, color_hex=C_TEXT_MUTED, font_weight='Bold')
add_text(f4, 'F4 Prodi 1', 816, 418, '1. S1 Teknik Informatika (Fakultas Teknik) — Pilihan Utama', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f4, 'F4 Prodi 2', 816, 440, '2. S1 Sistem Informasi (Fakultas Teknik) — Pilihan Cadangan', font_size=12, color_hex=C_TEXT_SEC)

# CBT Schedule Box
add_rect(f4, 'F4 CBT Box', 800, 485, 562, 125, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f4, 'F4 CBT Header', 816, 498, 'JADWAL & LOKASI UJIAN TERTULIS (CBT):', font_size=10, color_hex='#15803d', font_weight='Bold')
add_text(f4, 'F4 Hari Tgl', 816, 518, 'Hari / Tanggal  : Sabtu, 18 April 2026', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f4, 'F4 Waktu Sesi', 816, 540, 'Waktu / Sesi   : Sesi 1 (Pagi) • Pukul 08.00 - 11.30 WIB', font_size=12, color_hex=C_TEXT_PRIMARY)
add_text(f4, 'F4 Ruang Ujian', 816, 562, 'Ruang / Sektor : Gedung E10 Lt. 3, Lab Komputer 02 FMIPA UNNES', font_size=12, color_hex=C_TEXT_PRIMARY)
add_text(f4, 'F4 Alamat CBT', 816, 584, 'Lokasi Kampus  : Kampus UNNES Sekaran, Gunungpati, Kota Semarang', font_size=11, color_hex='#15803d')

# QR Code Validation Area
add_rect(f4, 'F4 QR Box', 800, 625, 110, 110, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f4, 'F4 QR Dummy', 822, 670, '[ QR CODE ]', font_size=11, color_hex=C_TEXT_MUTED, font_weight='Bold')

add_text(f4, 'F4 QR Note 1', 930, 642, 'Validasi Keaslian Kartu Tanda Peserta:', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f4, 'F4 QR Note 2', 930, 664, 'Pindai kode QR untuk validasi keaslian kartu peserta', font_size=11, color_hex=C_TEXT_SEC)
add_text(f4, 'F4 QR Note 3', 930, 684, 'oleh petugas panitia pengawas di lokasi ujian.', font_size=11, color_hex=C_TEXT_SEC)
add_text(f4, 'F4 QR Note 4', 930, 706, 'Tanda tangan digital Admisi PMB: VALID (SHA-256 Verified)', font_size=10, color_hex=C_BLUE, font_weight='Bold')

# Print Button
add_rect(f4, 'F4 Btn Cetak', 800, 755, 562, 50, fill_hex=C_BLUE, radius=8)
add_text(f4, 'F4 Btn Cetak Txt', 980, 770, 'Unduh Kartu Peserta (PDF) ↓', font_size=13, color_hex=C_WHITE, font_weight='Bold')

add_text(f4, 'F4 Print Instruction', 800, 820, 'Cetak menggunakan kertas HVS A4 putih dan bawa bersama kartu identitas asli pada saat hari ujian.', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 05. PANEL VERIFIKASI PANITIA PMB (X = 6160)
# ==========================================
f5 = add_frame('05. Panel Verifikasi Panitia PMB', 6160.0, 0.0)

# Sidebar Left
add_rect(f5, 'F5 Side BG', 0, 0, 240, 1000, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_rect(f5, 'F5 Side Logo BG', 24, 24, 38, 38, fill_hex=C_BLUE, radius=8)
add_text(f5, 'F5 Side Logo Txt', 34, 34, 'UN', font_size=14, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Side Title', 72, 26, 'PMB Admin Panel', font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f5, 'F5 Side Sub', 72, 46, 'Sistem Verifikasi Berkas', font_size=10, color_hex=C_TEXT_MUTED)

add_rect(f5, 'F5 Side Div', 24, 76, 192, 1, fill_hex=C_BORDER)

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
    add_rect(f5, f'F5 Mnu {mtitle}', 16, smy, 208, 38, fill_hex=mbg, radius=6)
    add_text(f5, f'F5 MnuTxt {mtitle}', 32, smy + 11, mtitle, font_size=12, color_hex=mtxt, font_weight='Bold' if mact else 'Regular')
    smy += 44

add_rect(f5, 'F5 Admin Profile BG', 16, 920, 208, 60, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_rect(f5, 'F5 Admin Av', 28, 934, 32, 32, fill_hex=C_BLUE, radius=16)
add_text(f5, 'F5 Admin Av Txt', 40, 942, 'P', font_size=12, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Admin Name', 68, 933, 'Panitia Verifikator', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f5, 'F5 Admin Role', 68, 951, 'Staff Admisi PMB', font_size=10, color_hex=C_TEXT_MUTED)

# Main Area
add_rect(f5, 'F5 Header BG', 240, 0, 1200, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f5, 'F5 Header Title', 272, 22, 'Antrean Verifikasi Berkas Pendaftar', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

add_rect(f5, 'F5 Search Inp', 960, 14, 250, 36, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f5, 'F5 Search Inp Txt', 980, 24, 'Cari nomor pendaftaran, NISN...', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f5, 'F5 Filter Drop', 1225, 14, 180, 36, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=8)
add_text(f5, 'F5 Filter Drop Txt', 1242, 24, 'Status: Semua Berkas ▼', font_size=11, color_hex=C_TEXT_SEC)

# 4 Stat Cards
stats_admin = [
    ('Total Pendaftar Masuk', '1,428', C_TEXT_PRIMARY, C_BLUE),
    ('Menunggu Verifikasi', '42', '#b45309', '#f59e0b'),
    ('Perlu Revisi Dokumen', '15', '#be123c', '#ef4444'),
    ('Lulus / Terverifikasi', '1,371', '#15803d', '#10b981')
]
sx = 272
for stitle, sval, scolor, stop_color in stats_admin:
    add_rect(f5, f'F5 StatBG {stitle}', sx, 88, 267, 105, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
    add_rect(f5, f'F5 StatTop {stitle}', sx, 88, 267, 4, fill_hex=stop_color, radius=[12, 12, 0, 0])
    
    add_text(f5, f'F5 StatVal {stitle}', sx + 20, 112, sval, font_size=26, color_hex=scolor, font_weight='Bold')
    add_text(f5, f'F5 StatLbl {stitle}', sx + 20, 155, stitle, font_size=11, color_hex=C_TEXT_MUTED)
    sx += 287

# Antrean Table Container
add_rect(f5, 'F5 Table BG', 272, 215, 1128, 735, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f5, 'F5 Table Title', 296, 240, 'Antrean Pemeriksaan Dokumen Calon Mahasiswa Baru', font_size=14, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

# Table Blue Header
add_rect(f5, 'F5 Table Th', 296, 280, 1080, 42, fill_hex=C_BLUE, radius=[8, 8, 0, 0])
add_text(f5, 'F5 Th 1', 316, 294, 'NO. PENDAFTARAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Th 2', 480, 294, 'NAMA LENGKAP & NISN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Th 3', 720, 294, 'PROGRAM STUDI PILIHAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Th 4', 975, 294, 'STATUS BERKAS', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f5, 'F5 Th 5', 1210, 294, 'AKSI VERIFIKASI', font_size=11, color_hex=C_WHITE, font_weight='Bold')

# Data Rows
rows_panitia = [
    ('PMB-2026-08492', 'Muhammad Irfan', 'NISN: 0058291042', 'S1 Teknik Informatika', 'Jalur Mandiri Prestasi', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309', True),
    ('PMB-2026-08493', 'Siti Nurhaliza', 'NISN: 0057193821', 'S1 Sistem Informasi', 'Jalur SNBP (Prestasi)', 'PERLU REVISI', '#fff1f2', '#fecdd3', '#be123c', False),
    ('PMB-2026-08494', 'Budi Santoso', 'NISN: 0059281742', 'S1 Teknik Elektro', 'Jalur SNBT (UTBK)', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False),
    ('PMB-2026-08495', 'Annisa Rahmawati', 'NISN: 0056192841', 'S1 Pendidikan Matematika', 'Jalur Mandiri Reguler', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309', False),
    ('PMB-2026-08496', 'Dimas Arya Pratama', 'NISN: 0058918274', 'S1 Ilmu Komputer', 'Jalur Mandiri Prestasi', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False),
    ('PMB-2026-08497', 'Fadhilah Nurul Hidayah', 'NISN: 0057281932', 'S1 Farmasi', 'Jalur SNBP (Prestasi)', 'PERLU REVISI', '#fff1f2', '#fecdd3', '#be123c', False),
    ('PMB-2026-08498', 'Rizky Ramadhan', 'NISN: 0059182736', 'S1 Manajemen', 'Jalur SNBT (UTBK)', 'TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46', False)
]
ty = 322
for i, (rno, rname, rnisn, rprodi, rjalur, rst, rbg, rbrd, rtxt, rhl) in enumerate(rows_panitia):
    row_bg = '#f0f9ff' if rhl else (C_WHITE if i % 2 == 0 else '#f8fafc')
    add_rect(f5, f'F5 Row {rno}', 296, ty, 1080, 60, fill_hex=row_bg, stroke_hex='#f1f5f9')
    
    add_text(f5, f'F5 RNo {rno}', 316, ty + 22, rno, font_size=12, color_hex=C_BLUE, font_weight='Bold')
    
    add_text(f5, f'F5 RName {rno}', 480, ty + 14, rname, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f5, f'F5 RNISN {rno}', 480, ty + 34, rnisn, font_size=10, color_hex=C_TEXT_MUTED)
    
    add_text(f5, f'F5 RProdi {rno}', 720, ty + 14, rprodi, font_size=12, color_hex=C_TEXT_SEC)
    add_text(f5, f'F5 RJalur {rno}', 720, ty + 34, rjalur, font_size=10, color_hex=C_TEXT_MUTED)
    
    add_rect(f5, f'F5 RBadge {rno}', 975, ty + 17, 125, 26, fill_hex=rbg, stroke_hex=rbrd, radius=6)
    add_text(f5, f'F5 RBadgeTxt {rno}', 995, ty + 23, rst, font_size=10, color_hex=rtxt, font_weight='Bold')
    
    btn_fill = C_BLUE if rhl else C_WHITE
    btn_txt = C_WHITE if rhl else C_TEXT_PRIMARY
    add_rect(f5, f'F5 RBtn {rno}', 1210, ty + 13, 130, 34, fill_hex=btn_fill, stroke_hex=C_BORDER, radius=6)
    add_text(f5, f'F5 RBtnTxt {rno}', 1238, ty + 22, 'Periksa Berkas', font_size=11, color_hex=btn_txt, font_weight='Bold')
    
    ty += 60

add_text(f5, 'F5 Table Footer', 296, 895, 'Menampilkan 1 s.d. 7 dari total 42 antrean aktif', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 06. DASHBOARD PENDAFTAR & NOTIFIKASI WEB PUSH (X = 7700)
# ==========================================
f6 = add_frame('06. Dashboard Pendaftar & Notifikasi Web Push', 7700.0, 0.0)

# Top Bar
add_rect(f6, 'F6 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f6, 'F6 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')

add_text(f6, 'F6 Nav 1', 220, 24, 'Dashboard', font_size=13, color_hex=C_BLUE, font_weight='Bold')
add_rect(f6, 'F6 Nav Ind', 220, 62, 65, 2, fill_hex=C_BLUE)
add_text(f6, 'F6 Nav 2', 325, 24, 'Biodata Siswa', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f6, 'F6 Nav 3', 445, 24, 'Status Dokumen', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f6, 'F6 Nav 4', 575, 24, 'Jadwal CBT', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f6, 'F6 Nav 5', 680, 24, 'Pusat Bantuan', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f6, 'F6 Status Top Pill', 1020, 18, 175, 28, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=14)
add_text(f6, 'F6 Status Top Txt', 1038, 24, 'MENUNGGU VERIFIKASI', font_size=10, color_hex='#b45309', font_weight='Bold')
add_text(f6, 'F6 User Top Txt', 1215, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Welcome Hero Banner
add_rect(f6, 'F6 Hero BG', 48, 88, 1344, 160, fill_hex=C_BLUE, radius=16)
add_rect(f6, 'F6 Hero Tag', 80, 110, 260, 24, fill_hex=C_DARK_BLUE, radius=12)
add_text(f6, 'F6 Hero Tag Txt', 95, 115, 'PORTAL PENDAFTAR PMB TA 2026/2027', font_size=10, color_hex=C_WHITE, font_weight='Bold')

add_text(f6, 'F6 Hero Title', 80, 142, 'Selamat Datang Kembali, Muhammad Irfan!', font_size=24, color_hex=C_WHITE, font_weight='Bold')
add_text(f6, 'F6 Hero Sub', 80, 178, 'Pendaftaran Anda telah tercatat dengan Nomor: PMB-2026-08492 pada Program Studi S1 Teknik Informatika (Fakultas Teknik).', font_size=13, color_hex='#e0f2fe')
add_text(f6, 'F6 Hero Meta', 80, 204, 'Jalur Seleksi: Mandiri Prestasi Unggul (SM-UNNES)   |   Status Berkas: Dalam Antrean Verifikasi Panitia', font_size=11, color_hex='#bae6fd')

# Web Push Notification Telemetry Card (Technical Requirements #5)
add_rect(f6, 'F6 Push Card BG', 48, 265, 1344, 90, fill_hex='#f0fdf4', stroke_hex='#86efac', radius=12)
add_rect(f6, 'F6 Push Icon BG', 76, 286, 48, 48, fill_hex='#dcfce7', radius=24)
add_text(f6, 'F6 Push Icon Txt', 89, 301, 'NOTIF', font_size=9, color_hex='#166534', font_weight='Bold')

add_text(f6, 'F6 Push Title', 140, 286, 'Layanan Notifikasi Web Push Real-time Aktif', font_size=14, color_hex='#166534', font_weight='Bold')
add_text(f6, 'F6 Push Desc', 140, 310, 'Browser Anda terhubung ke Service Worker VAPID. Anda akan menerima notifikasi otomatis saat ada pembaruan status verifikasi atau catatan revisi dari panitia.', font_size=11, color_hex='#15803d')

add_rect(f6, 'F6 Push Pill', 1030, 295, 120, 30, fill_hex=C_WHITE, stroke_hex='#86efac', radius=15)
add_text(f6, 'F6 Push Pill Txt', 1048, 302, '● Terhubung Aktif', font_size=10, color_hex='#166534', font_weight='Bold')

add_rect(f6, 'F6 Push Test Btn', 1165, 290, 205, 40, fill_hex='#16a34a', radius=8)
add_text(f6, 'F6 Push Test Btn Txt', 1185, 302, 'Uji Coba Kirim Notifikasi Push →', font_size=11, color_hex=C_WHITE, font_weight='Bold')

# Left Column: Document Verification Status (w: 780, h: 560)
add_rect(f6, 'F6 Left Card BG', 48, 375, 780, 560, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f6, 'F6 Left Title', 76, 400, 'Tahapan Seleksi & Dokumen Berkas', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f6, 'F6 Left Sub', 76, 424, 'Perkembangan verifikasi berkas pendaftaran diperbarui langsung oleh panitia admisi.', font_size=11, color_hex=C_TEXT_MUTED)

# Stepper 5-Step Bar
dash_steps = [
    ('1. Biodata', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('2. Pilihan', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('3. Berkas', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('4. Verifikasi', 'Diproses', '#fef3c7', '#fde68a', '#b45309'),
    ('5. Pengumuman', '20 Des 2026', '#f8fafc', C_BORDER, C_TEXT_MUTED)
]
dsx = 76
for stitle, ssub, sbg, sbrd, stxt in dash_steps:
    add_rect(f6, f'F6 DStep {stitle}', dsx, 452, 134, 40, fill_hex=sbg, stroke_hex=sbrd, radius=8)
    add_text(f6, f'F6 DStepTitle {stitle}', dsx + 12, 460, stitle, font_size=11, color_hex=stxt, font_weight='Bold')
    add_text(f6, f'F6 DStepSub {stitle}', dsx + 12, 474, ssub, font_size=9, color_hex=stxt)
    dsx += 146

add_text(f6, 'F6 Docs Title', 76, 515, 'Daftar Berkas Persyaratan yang Diunggah (4 Dokumen):', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

dash_docs = [
    ('1. Ijazah SMA / Surat Keterangan Lulus (SKL)', 'ijazah_irfan_2026.pdf (1.2 MB) • Diunggah 10 Nov 2026', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('2. Kartu Keluarga (KK) Legalisir', 'kk_keluarga_irfan.pdf (890 KB) • Dalam proses peninjauan verifikator', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309'),
    ('3. Pas Foto Resmi 4x6 Background Merah', 'foto_formal_4x6.jpg (450 KB) • Resolusi sesuai standar kartu peserta', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('4. Sertifikat Prestasi / Portofolio Kejuaraan', 'sertifikat_osn_nasional.pdf (1.8 MB) • Juara 1 OSN Informatika Nasional', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46')
]
ddy = 540
for dname, dmeta, dst, dbg, dbrd, dtxt in dash_docs:
    row_bg = '#fffbeb' if 'MENUNGGU' in dst else '#f8fafc'
    row_brd = '#fde68a' if 'MENUNGGU' in dst else C_BORDER
    add_rect(f6, f'F6 DRow {dname}', 76, ddy, 724, 68, fill_hex=row_bg, stroke_hex=row_brd, radius=10)
    add_text(f6, f'F6 DRowName {dname}', 98, ddy + 16, dname, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f6, f'F6 DRowMeta {dname}', 98, ddy + 38, dmeta, font_size=10, color_hex=C_TEXT_MUTED)
    
    add_rect(f6, f'F6 DRowBadge {dname}', 680, ddy + 20, 105, 26, fill_hex=dbg, stroke_hex=dbrd, radius=6)
    add_text(f6, f'F6 DRowBadgeTxt {dname}', 705, ddy + 26, dst, font_size=10, color_hex=dtxt, font_weight='Bold')
    ddy += 76

add_rect(f6, 'F6 Alert Box', 76, 855, 724, 60, fill_hex='#eff6ff', stroke_hex='#bfdbfe', radius=8)
add_text(f6, 'F6 Alert T1', 96, 868, 'Catatan: Jika panitia menandai dokumen PERLU REVISI, notifikasi Web Push akan muncul di browser', font_size=11, color_hex='#1e40af', font_weight='Bold')
add_text(f6, 'F6 Alert T2', 96, 890, 'dan tombol Ganti File akan otomatis aktif pada dokumen terkait untuk upload ulang perbaikan.', font_size=11, color_hex='#2563eb')

# Right Column: CBT Schedule & Fast Actions (w: 544, h: 560)
add_rect(f6, 'F6 Right Card BG', 848, 375, 544, 560, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f6, 'F6 Right Title', 876, 400, 'Jadwal Seleksi CBT & Kartu Peserta', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f6, 'F6 Right Sub', 876, 424, 'Persiapkan diri Anda untuk pelaksanaan ujian tertulis di kampus UNNES.', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f6, 'F6 CBT Box', 876, 452, 488, 170, fill_hex='#f8fafc', stroke_hex='#cbd5e1', radius=10)
add_text(f6, 'F6 CBT Tag', 898, 470, 'JALUR MANDIRI PRESTASI UNGGUL', font_size=10, color_hex=C_BLUE, font_weight='Bold')
add_text(f6, 'F6 CBT Date', 898, 492, 'Sabtu, 18 April 2026', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f6, 'F6 CBT Time', 898, 522, 'Sesi 1 (Pagi) • Pukul 08.00 - 11.30 WIB (Hadir 30 menit sebelum)', font_size=11, color_hex=C_TEXT_SEC)
add_text(f6, 'F6 CBT Room', 898, 544, 'Ruang: Gedung E10 Lantai 3, Lab Komputer 02 FMIPA', font_size=11, color_hex=C_TEXT_SEC)
add_text(f6, 'F6 CBT Loc', 898, 566, 'Kampus UNNES Sekaran, Gunungpati, Kota Semarang', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f6, 'F6 CBT Note', 898, 590, 'Wajib membawa Kartu Tanda Peserta & KTP/Kartu Pelajar asli.', font_size=10, color_hex=C_BLUE, font_weight='Bold')

add_rect(f6, 'F6 DL Box', 876, 638, 488, 105, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=10)
add_text(f6, 'F6 DL Title', 898, 654, 'Kartu Tanda Peserta CBT Siap Dicetak', font_size=12, color_hex='#15803d', font_weight='Bold')
add_text(f6, 'F6 DL Desc', 898, 676, 'Cetak pada kertas HVS A4 putih dan simpan baik-baik nomor ujian Anda.', font_size=10, color_hex='#166534')
add_rect(f6, 'F6 DL Btn', 898, 698, 444, 34, fill_hex='#16a34a', radius=6)
add_text(f6, 'F6 DL Btn Txt', 1035, 708, 'Unduh Kartu Peserta (PDF) ↓', font_size=11, color_hex=C_WHITE, font_weight='Bold')

add_rect(f6, 'F6 Help Box', 876, 760, 488, 95, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=10)
add_text(f6, 'F6 Help Title', 898, 776, 'Pusat Layanan PMB UNNES', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f6, 'F6 Help WA', 898, 798, 'WhatsApp Helpdesk: 0812-3456-7890 (08:00 - 16:00 WIB)', font_size=10, color_hex=C_TEXT_SEC)
add_text(f6, 'F6 Help Mail', 898, 818, 'Email Resmi: pmb@mail.unnes.ac.id  |  Call Center: (024) 8508093', font_size=10, color_hex=C_TEXT_MUTED)

add_rect(f6, 'F6 Guide Btn', 876, 870, 488, 44, fill_hex=C_BLUE, radius=8)
add_text(f6, 'F6 Guide Btn Txt', 980, 883, 'Panduan & Tata Tertib Peserta CBT (PDF)', font_size=12, color_hex=C_WHITE, font_weight='Bold')

add_text(f6, 'F6 Footer', 48, 955, '© 2026 Universitas Negeri Semarang — Panitia PMB. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 07. DETAIL VERIFIKASI BERKAS & VALIDASI PANITIA (X = 9240)
# ==========================================
f7 = add_frame('07. Detail Verifikasi Berkas & Validasi Panitia', 9240.0, 0.0)

# Top Bar
add_rect(f7, 'F7 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f7, 'F7 Brand', 48, 22, 'PMB Admin Panel', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f7, 'F7 Breadcrumb', 220, 24, 'Antrean Verifikasi  /  Pemeriksaan Dokumen: PMB-2026-08492 (Muhammad Irfan)', font_size=12, color_hex=C_TEXT_MUTED)

add_rect(f7, 'F7 Back Btn', 1040, 16, 175, 34, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=6)
add_text(f7, 'F7 Back Btn Txt', 1060, 25, '← Kembali ke Antrean', font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
add_text(f7, 'F7 Admin User', 1235, 24, 'Panitia Verifikator (Admisi)', font_size=12, color_hex=C_TEXT_PRIMARY)

# Summary Header Banner
add_rect(f7, 'F7 Summary BG', 48, 88, 1344, 75, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
add_text(f7, 'F7 Student Name', 76, 102, 'Muhammad Irfan', font_size=17, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 Student Meta', 76, 128, 'No. Pendaftaran: PMB-2026-08492  |  NISN: 0058291042  |  NIK: 3302192804040003  |  Prodi: S1 Teknik Informatika (FT)  |  Jalur: Mandiri Prestasi', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f7, 'F7 Status Pill Right', 1140, 108, 225, 34, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=17)
add_text(f7, 'F7 Status Pill Txt', 1158, 117, 'STATUS: MENUNGGU VERIFIKASI', font_size=10, color_hex='#b45309', font_weight='Bold')

# Split Screen: Left Document Viewer, Right Decision Form
# Left Document Viewer (x: 48, w: 780, h: 775)
add_rect(f7, 'F7 Viewer BG', 48, 180, 780, 775, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)

# Document Tab Bar
tab_x7 = 68
dtabs7 = [
    ('Ijazah/SKL (Valid)', '#f8fafc', C_BORDER, '#15803d', 145),
    ('Kartu Keluarga (Aktif)', C_BLUE, None, C_WHITE, 165),
    ('Pas Foto 4x6 (Valid)', '#f8fafc', C_BORDER, '#15803d', 140),
    ('Portofolio (Valid)', '#f8fafc', C_BORDER, '#15803d', 140)
]
for dt, dbg, dbrd, dtxt, dw in dtabs7:
    add_rect(f7, f'F7 Tab {dt}', tab_x7, 196, dw, 34, fill_hex=dbg, stroke_hex=dbrd, radius=6)
    add_text(f7, f'F7 TabTxt {dt}', tab_x7 + 14, 205, dt, font_size=11, color_hex=dtxt, font_weight='Bold')
    tab_x7 += dw + 10

# Toolbar
add_text(f7, 'F7 Tool Info', 68, 244, 'File: kk_keluarga_irfan.pdf (890 KB) • Supabase Bucket: /berkas-pmb/kk_irfan.pdf', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f7, 'F7 Tool Controls', 550, 244, '[ - ]  100%  [ + ]   |   [ Buka Tab Baru ]   [ Unduh Asli ]', font_size=11, color_hex=C_BLUE, font_weight='Bold')

# Document Inspection Canvas
add_rect(f7, 'F7 Sheet BG', 68, 272, 740, 660, fill_hex='#f8fafc', stroke_hex='#cbd5e1', radius=8)

add_text(f7, 'F7 KK Kop', 96, 296, 'REPUBLIK INDONESIA — KARTU KELUARGA', font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 KK No', 96, 320, 'Nomor KK: 3302192804040003', font_size=13, color_hex=C_BLUE, font_weight='Bold')
add_text(f7, 'F7 KK Addr', 96, 342, 'Alamat: Jl. Sekaran Raya No. 42, RT 03 / RW 02, Kel. Sekaran, Kec. Gunungpati, Kota Semarang', font_size=11, color_hex=C_TEXT_MUTED)

# Family Table
add_rect(f7, 'F7 KK Th BG', 96, 368, 684, 28, fill_hex='#e2e8f0')
add_text(f7, 'F7 KK Th 1', 108, 375, 'No.   Nama Lengkap', font_size=10, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 KK Th 2', 290, 375, 'NIK', font_size=10, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 KK Th 3', 470, 375, 'Jenis Kelamin', font_size=10, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 KK Th 4', 595, 375, 'Hubungan Keluarga', font_size=10, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

rows_kk = [
    ('1.    Ahmad Subagio', '3302191508750001', 'Laki-laki', 'Kepala Keluarga', '#ffffff', C_TEXT_SEC),
    ('2.    Siti Aminah', '3302195211780002', 'Perempuan', 'Istri', '#f8fafc', C_TEXT_SEC),
    ('3.    Muhammad Irfan', '3302192804040003', 'Laki-laki', 'Anak Kandung (Pendaftar)', '#eff6ff', C_BLUE)
]
ry7 = 396
for c1, c2, c3, c4, rbg, rtxt in rows_kk:
    add_rect(f7, f'F7 KK Row {c1} BG', 96, ry7, 684, 28, fill_hex=rbg, stroke_hex='#f1f5f9')
    add_text(f7, f'F7 KK Row {c1} C1', 108, ry7 + 7, c1, font_size=10, color_hex=rtxt)
    add_text(f7, f'F7 KK Row {c1} C2', 290, ry7 + 7, c2, font_size=10, color_hex=rtxt)
    add_text(f7, f'F7 KK Row {c1} C3', 470, ry7 + 7, c3, font_size=10, color_hex=rtxt)
    add_text(f7, f'F7 KK Row {c1} C4', 595, ry7 + 7, c4, font_size=10, color_hex=rtxt)
    ry7 += 28

# Defect Callout Box inside Viewer
add_rect(f7, 'F7 Defect BG', 96, 500, 684, 215, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=10)
add_text(f7, 'F7 Defect Title', 118, 520, 'CATATAN TEMUAN VERIFIKATOR PADA DOKUMEN INI', font_size=12, color_hex='#be123c', font_weight='Bold')
add_text(f7, 'F7 Defect 1', 118, 548, '• Stempel legalisir kelurahan/kecamatan buram dan tidak terbaca jelas.', font_size=11, color_hex='#9f1239')
add_text(f7, 'F7 Defect 2', 118, 574, '• Barcode dinas kependudukan di pojok bawah dokumen terpotong saat scan scanner.', font_size=11, color_hex='#9f1239')
add_text(f7, 'F7 Defect 3', 118, 600, '• Rekomendasi Verifikator: Wajib meminta pendaftar mengunggah ulang scan KK asli yang jelas.', font_size=11, color_hex='#be123c', font_weight='Bold')
add_text(f7, 'F7 Defect 4', 118, 626, '• Batas Waktu Revisi: 20 Desember 2026 pukul 23:59 WIB sebelum finalisasi seleksi.', font_size=10, color_hex='#881337')
add_text(f7, 'F7 Defect 5', 118, 650, '• Dampak jika tidak direvisi: Pendaftaran dapat dibatalkan atau gugur seleksi administrasi.', font_size=10, color_hex='#9f1239')

# Right Column - Verification Decision Panel (w: 544, h: 775)
add_rect(f7, 'F7 Right Card BG', 848, 180, 544, 775, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f7, 'F7 Right Title', 876, 204, 'Formulir Keputusan Verifikasi Panitia', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 Right Sub', 876, 228, 'Tentukan keabsahan berkas dan kirimkan instruksi perbaikan ke calon mahasiswa.', font_size=11, color_hex=C_TEXT_MUTED)

# Checklist Box
add_rect(f7, 'F7 Check Box', 876, 255, 488, 110, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f7, 'F7 Check Title', 896, 270, 'Checklist Pemeriksaan Syarat Dokumen (KK):', font_size=11, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f7, 'F7 Check 1', 896, 294, '[X]  NIK siswa (3302192804040003) sesuai biodata Dapodik', font_size=11, color_hex='#15803d', font_weight='Bold')
add_text(f7, 'F7 Check 2', 896, 316, '[X]  Nama orang tua kandung terdaftar dalam susunan keluarga', font_size=11, color_hex='#15803d', font_weight='Bold')
add_text(f7, 'F7 Check 3', 896, 338, '[ ]  Keterbacaan stempel legalisir dan keutuhan barcode scan (GAGAL)', font_size=11, color_hex='#be123c', font_weight='Bold')

# Status Berkas Ini Section
add_text(f7, 'F7 Berkas Lbl', 876, 380, 'Status Dokumen Ini (Kartu Keluarga):', font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')

add_rect(f7, 'F7 Btn Valid', 876, 400, 140, 36, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=6)
add_text(f7, 'F7 Btn Valid Txt', 925, 410, 'VALID', font_size=11, color_hex=C_TEXT_MUTED, font_weight='Bold')

add_rect(f7, 'F7 Btn Revisi', 1026, 400, 185, 36, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=6)
add_text(f7, 'F7 Btn Revisi Txt', 1055, 410, 'PERLU REVISI', font_size=11, color_hex='#be123c', font_weight='Bold')

add_rect(f7, 'F7 Btn Tolak', 1221, 400, 143, 36, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=6)
add_text(f7, 'F7 Btn Tolak Txt', 1248, 410, 'TIDAK VALID', font_size=11, color_hex=C_TEXT_MUTED, font_weight='Bold')

# Status Pendaftaran Siswa
add_text(f7, 'F7 Pend Lbl', 876, 452, 'Update Status Keseluruhan Pendaftaran Siswa:', font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f7, 'F7 Pend Box', 876, 474, 488, 40, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=8)
add_text(f7, 'F7 Pend Txt', 896, 486, 'PERLU_REVISI  (Pendaftar Wajib Mengunggah Ulang Dokumen)', font_size=11, color_hex='#be123c', font_weight='Bold')

# Catatan Revisi Textarea
add_text(f7, 'F7 Catatan Lbl', 876, 528, 'Catatan Panitia / Instruksi Revisi (Wajib Diisi jika Perlu Revisi) *', font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f7, 'F7 Catatan Box', 876, 550, 488, 105, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f7, 'F7 Catatan L1', 894, 565, 'Scan Kartu Keluarga pada bagian stempel kelurahan buram dan', font_size=11, color_hex=C_TEXT_PRIMARY)
add_text(f7, 'F7 Catatan L2', 894, 585, 'barcode bagian bawah terpotong. Silakan unggah ulang scan KK asli', font_size=11, color_hex=C_TEXT_PRIMARY)
add_text(f7, 'F7 Catatan L3', 894, 605, 'yang utuh, tajam, dan tidak terpotong sebelum 20 Desember 2026.', font_size=11, color_hex=C_TEXT_PRIMARY)

# Web Push Trigger Box (Technical Requirements #5)
add_rect(f7, 'F7 Push Box', 876, 670, 488, 75, fill_hex='#f0fdf4', stroke_hex='#86efac', radius=10)
add_text(f7, 'F7 Push Txt 1', 896, 686, '[X]  Kirim Notifikasi Web Push Instan ke Smartphone/Browser Siswa', font_size=11, color_hex='#166534', font_weight='Bold')
add_text(f7, 'F7 Push Txt 2', 896, 708, 'Antrean BullMQ: `notification-queue` • Event: `STATUS_REVISI_BERKAS` via VAPID Web Push', font_size=10, color_hex='#15803d')

# Action Buttons
add_rect(f7, 'F7 Submit Btn', 876, 760, 488, 48, fill_hex='#be123c', radius=8)
add_text(f7, 'F7 Submit Txt', 975, 775, 'Simpan Keputusan Revisi & Kirim Web Push →', font_size=12, color_hex=C_WHITE, font_weight='Bold')

add_rect(f7, 'F7 Cancel Btn', 876, 818, 488, 40, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=8)
add_text(f7, 'F7 Cancel Txt', 1055, 830, 'Batal / Lewati Pendaftar Ini', font_size=12, color_hex=C_TEXT_MUTED)

add_text(f7, 'F7 Footer', 48, 965, 'Sistem Informasi Admisi & Verifikasi PMB UNNES — Panel Verifikator Admisi Kampus Konservasi.', font_size=11, color_hex=C_TEXT_MUTED)

# ==========================================
# 08. PENGUMUMAN KELULUSAN & REGISTRASI ULANG (X = 10780)
# ==========================================
f8 = add_frame('08. Pengumuman Kelulusan & Registrasi Ulang', 10780.0, 0.0)

# Top Bar
add_rect(f8, 'F8 Nav BG', 0, 0, 1440, 64, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f8, 'F8 Brand', 48, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f8, 'F8 Nav 1', 220, 24, 'Hasil Kelulusan', font_size=13, color_hex=C_BLUE, font_weight='Bold')
add_rect(f8, 'F8 Nav Ind', 220, 62, 90, 2, fill_hex=C_BLUE)
add_text(f8, 'F8 Nav 2', 340, 24, 'Surat Keputusan', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 Nav 3', 475, 24, 'Registrasi Ulang', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 Nav 4', 610, 24, 'Pembayaran UKT', font_size=13, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 Nav 5', 745, 24, 'Pusat Bantuan', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f8, 'F8 Status Top Pill', 1080, 18, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f8, 'F8 Status Top Txt', 1105, 24, 'LULUS SELEKSI', font_size=10, color_hex='#065f46', font_weight='Bold')
add_text(f8, 'F8 User Top', 1245, 24, 'Muhammad Irfan', font_size=12, color_hex=C_TEXT_PRIMARY)

# Green Success Banner
add_rect(f8, 'F8 Hero BG', 48, 88, 1344, 175, fill_hex='#059669', radius=16)
add_rect(f8, 'F8 Tag Badge', 80, 110, 360, 24, fill_hex='#047857', radius=12)
add_text(f8, 'F8 Tag Badge Txt', 95, 115, 'PENGUMUMAN HASIL KELULUSAN AKHIR PMB TA 2026/2027', font_size=10, color_hex=C_WHITE, font_weight='Bold')

add_text(f8, 'F8 Hero Title', 80, 145, 'SELAMAT! ANDA DINYATAKAN LULUS SELEKSI', font_size=26, color_hex=C_WHITE, font_weight='Bold')
add_text(f8, 'F8 Hero Sub', 80, 182, 'Universitas Negeri Semarang mengucapkan selamat bergabung dengan keluarga besar sivitas akademika UNNES Kampus Konservasi.', font_size=13, color_hex='#d1fae5')
add_text(f8, 'F8 Hero Reg', 80, 208, 'Nomor Peserta: PMB-2026-08492   •   Jalur Masuk: Seleksi Mandiri Prestasi Unggul (SM-UNNES Terpadu)', font_size=12, color_hex='#a7f3d0')

# Split Screen: Left Details, Right Re-registration
# Left Card (x: 48, w: 656, h: 630)
add_rect(f8, 'F8 Left Card BG', 48, 280, 656, 630, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f8, 'F8 Left Title', 80, 305, '1. Rincian Penetapan Program Studi & Kelulusan', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f8, 'F8 Left Sub', 80, 328, 'Data resmi berdasarkan Surat Keputusan Rektor UNNES tentang Penetapan Mahasiswa Baru 2026.', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f8, 'F8 Left Div', 80, 350, 592, 1, fill_hex=C_BORDER)

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
    add_text(f8, f'F8 Lbl {slbl}', 80, sdy, slbl, font_size=10, color_hex=C_TEXT_MUTED)
    txt_color = C_BLUE if 'Teknik' in sval or '4.500.000' in sval or 'Sah' in sval else C_TEXT_PRIMARY
    add_text(f8, f'F8 Val {slbl}', 310, sdy, sval, font_size=11, color_hex=txt_color, font_weight='Bold')
    add_rect(f8, f'F8 Div {slbl}', 80, sdy + 18, 592, 1, fill_hex='#f1f5f9')
    sdy += 34

add_rect(f8, 'F8 SKL Btn', 80, 835, 592, 48, fill_hex=C_BLUE, radius=8)
add_text(f8, 'F8 SKL Btn Txt', 235, 850, 'Unduh Surat Keterangan Lulus (SKL) Resmi (PDF) ↓', font_size=12, color_hex=C_WHITE, font_weight='Bold')

# Right Card (x: 736, w: 656, h: 630)
add_rect(f8, 'F8 Right Card BG', 736, 280, 656, 630, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f8, 'F8 Right Title', 768, 305, '2. Alur & Panduan Wajib Registrasi Ulang', font_size=16, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f8, 'F8 Right Sub', 768, 328, 'Selesaikan 3 langkah registrasi ulang sebelum batas waktu agar hak kepesertaan tidak gugur.', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f8, 'F8 Right Div', 768, 350, 592, 1, fill_hex=C_BORDER)

# Step 1: UKT
add_rect(f8, 'F8 S1 BG', 768, 365, 592, 115, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=10)
add_text(f8, 'F8 S1 Title', 790, 382, 'Langkah 1: Pembayaran Uang Kuliah Tunggal (UKT)', font_size=13, color_hex='#15803d', font_weight='Bold')
add_text(f8, 'F8 S1 Desc', 790, 404, 'Lakukan pembayaran sebesar Rp 4.500.000 melalui Virtual Account BNI (9880-0058-2910-4200)', font_size=11, color_hex='#166534')
add_text(f8, 'F8 S1 Desc 2', 790, 424, 'melalui ATM, Mobile Banking BNI, atau Teller Bank BNI terdekat di seluruh Indonesia.', font_size=11, color_hex='#166534')
add_text(f8, 'F8 S1 Note', 790, 448, 'Tenggat Waktu: 25 Juli 2026, 15:00 WIB (Sistem otomatis memverifikasi pelunasan).', font_size=10, color_hex='#15803d', font_weight='Bold')

# Step 2: SIMREG Online
add_rect(f8, 'F8 S2 BG', 768, 492, 592, 105, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=10)
add_text(f8, 'F8 S2 Title', 790, 508, 'Langkah 2: Registrasi Online & Pengisian Ukuran Jas Almamater', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f8, 'F8 S2 Desc', 790, 530, 'Isi data induk mahasiswa (SIMREG), riwayat kesehatan, dan ukuran jas almamater', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 S2 Desc 2', 790, 550, '(S / M / L / XL / XXL) melalui portal simreg.unnes.ac.id.', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 S2 Status', 790, 572, '[ Terbuka otomatis setelah Pembayaran UKT Langkah 1 tervalidasi ]', font_size=10, color_hex=C_BLUE, font_weight='Bold')

# Step 3: KTM & Orientation
add_rect(f8, 'F8 S3 BG', 768, 608, 592, 95, fill_hex='#f8fafc', stroke_hex=C_BORDER, radius=10)
add_text(f8, 'F8 S3 Title', 790, 624, 'Langkah 3: Pengambilan KTM & Orientasi Kampus (PKKMB)', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f8, 'F8 S3 Desc', 790, 646, 'Pengambilan Kartu Tanda Mahasiswa (KTM) ATM BNI & Jas Almamater di GSG UNNES.', font_size=11, color_hex=C_TEXT_MUTED)
add_text(f8, 'F8 S3 Desc 2', 790, 668, 'Jadwal PKKMB Universitas & Fakultas: 18 s.d. 20 Agustus 2026.', font_size=11, color_hex=C_TEXT_MUTED)

add_rect(f8, 'F8 Reg Online Btn', 768, 715, 592, 48, fill_hex=C_BLUE, radius=8)
add_text(f8, 'F8 Reg Online Btn Txt', 940, 730, 'Lanjut ke Portal Registrasi Online (SIMREG) →', font_size=12, color_hex=C_WHITE, font_weight='Bold')

add_rect(f8, 'F8 WA Group Btn', 768, 775, 592, 42, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f8, 'F8 WA Group Btn Txt', 900, 788, 'Bergabung ke Komunitas WhatsApp Mahasiswa Baru Informatika 2026', font_size=11, color_hex='#15803d', font_weight='Bold')

add_text(f8, 'F8 Help Text', 48, 940, 'Pusat Layanan Registrasi Mahasiswa Baru UNNES  |  Hotline Call Center: (024) 8508093  |  WhatsApp Helpdesk: 0812-3456-7890', font_size=11, color_hex=C_TEXT_MUTED)

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/pmb-ui-concept.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack into pmb-ui-concept.figcraft zip directly with images!
zip_path = 'C:/projects/ta-pemweb/uidesign/pmb-ui-concept.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully compiled pmb-ui-concept.figcraft with {len(doc["nodes"])} nodes and {len(images_meta)} images!')
