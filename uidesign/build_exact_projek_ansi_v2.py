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

# Exact Colors from Figma PROJEK-ANSI (Image #2)
C_BLUE = '#0284c7'          # Sky Blue CTA
C_DARK_BLUE = '#0369a1'     # Header Dark Blue
C_LIGHT_BLUE = '#e0f2fe'    # Navbar / Banner Light Sky
C_SECTION_BG = '#dce7f3'    # Tentang Kami Section Soft Blue-Gray
C_AMBER = '#f59e0b'         # Amber Accent
C_NAVY = '#0f172a'          # Dark Navy
C_WHITE = '#ffffff'         # Surface White
C_CANVAS = '#f8fafc'        # Page Canvas
C_BORDER = '#e2e8f0'        # Card Border
C_TEXT_PRIMARY = '#0f172a'  # Primary Dark Text
C_TEXT_SEC = '#334155'      # Secondary Text
C_TEXT_MUTED = '#64748b'    # Muted Slate
C_SUCCESS = '#059669'       # Green Success
C_SUCCESS_BG = '#ecfdf5'
C_SUCCESS_BORDER = '#a7f3d0'

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
            'background': {'a': 1.0, 'r': 0.941, 'g': 0.941, 'b': 0.941},
            'children': [],
            'flows': [],
            'height': 0.0,
            'id': 1,
            'name': 'Page 1',
            'prototype': {'background': {'a': 1.0, 'r': 0.941, 'g': 0.941, 'b': 0.941}, 'device': 'None', 'rotation': 'portrait'},
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

def add_frame(name, x, y, w, h, bg_hex=C_WHITE):
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

print('Exact setup ready.')

def add_homepage(frame_id, is_logged_in=False):
    # Top Navbar (Soft Sky Blue)
    add_rect(frame_id, 'Nav BG', 0, 0, 1200, 60, fill_hex='#e0f2fe', stroke_hex='#bae6fd')
    add_text(frame_id, 'Brand', 60, 20, 'Universitas Y', font_size=18, color_hex=C_DARK_BLUE, font_weight='Bold')
    
    add_text(frame_id, 'Nav Home', 360, 22, 'Home', font_size=13, color_hex=C_BLUE, font_weight='Bold')
    add_text(frame_id, 'Nav Gelombang', 440, 22, 'Gelombang', font_size=13, color_hex=C_TEXT_SEC)
    add_text(frame_id, 'Nav Tentang', 545, 22, 'Tentang', font_size=13, color_hex=C_TEXT_SEC)
    add_text(frame_id, 'Nav Kontak', 635, 22, 'Kontak', font_size=13, color_hex=C_TEXT_SEC)
    
    if not is_logged_in:
        add_rect(frame_id, 'Btn Masuk', 1040, 12, 100, 36, fill_hex=C_BLUE, radius=18)
        add_text(frame_id, 'Btn Masuk Txt', 1058, 22, 'Daftar / Masuk', font_size=12, color_hex=C_WHITE, font_weight='Bold')
    else:
        add_rect(frame_id, 'Avatar', 1030, 14, 32, 32, fill_hex=C_BLUE, radius=16)
        add_text(frame_id, 'Avatar Txt', 1041, 22, 'M', font_size=12, color_hex=C_WHITE, font_weight='Bold')
        add_text(frame_id, 'User Name', 1070, 22, 'Muhammad Irfan', font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')

    # Hero Banner (h=680)
    add_image_rect(frame_id, 'Hero Campus BG', 0, 60, 1200, 680, 'hero_campus.jpg')
    add_rect(frame_id, 'Hero Blue Overlay', 0, 60, 1200, 680, fill_hex=C_DARK_BLUE, opacity=0.75)
    
    # Blue Circular Cutout Graphic on Right
    add_rect(frame_id, 'Hero Blue Circle', 680, 120, 460, 460, fill_hex=C_BLUE, radius=230)
    add_image_rect(frame_id, 'Hero Student Cutout', 720, 150, 380, 520, 'student_hero.png')
    
    # Left Hero Typography
    add_text(frame_id, 'Hero H1', 80, 180, 'Pendaftaran', font_size=42, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Hero H2', 80, 235, 'Mahasiswa', font_size=42, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Hero H3', 80, 290, 'Baru', font_size=42, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Hero H4', 80, 345, 'Telah Dibuka!', font_size=44, color_hex=C_AMBER, font_weight='Bold')
    
    add_text(frame_id, 'Hero Sub', 80, 420, 'Kuliah Berkualitas, Masa Depan Cerah Bersama Kampus Konservasi.', font_size=15, color_hex='#e0f2fe')
    add_text(frame_id, 'Hero Sub 2', 80, 445, 'Sistem registrasi digital terpadu, cepat, dan transparan.', font_size=14, color_hex='#e0f2fe')
    
    add_rect(frame_id, 'Hero CTA', 80, 495, 180, 46, fill_hex='#0ea5e9', radius=23)
    add_text(frame_id, 'Hero CTA Txt', 108, 510, 'Daftar Sekarang >', font_size=13, color_hex=C_WHITE, font_weight='Bold')

    # Section 2: Gelombang Pendaftaran (y=740, h=800, White BG)
    add_rect(frame_id, 'Gelombang BG', 0, 740, 1200, 800, fill_hex=C_WHITE)
    add_text(frame_id, 'Gelombang Title', 450, 780, 'Gelombang Pendaftaran', font_size=28, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    
    waves_data = [
        ('Gelombang 1', '10 Nov - 20 Des 2026', 'Biaya: Bebas Biaya', 'Jalur Prestasi Nilai Rapor', 80),
        ('Gelombang 2', '15 Jan - 28 Feb 2027', 'Biaya: Rp 200.000', 'Jalur Tes Skolastik Nasional', 440),
        ('Gelombang 3', '01 Mar - 15 Apr 2027', 'Biaya: Rp 300.000', 'Jalur Mandiri Ujian CBT', 800)
    ]
    for wname, wdate, wcost, wdesc, wx in waves_data:
        add_rect(frame_id, f'WCard BG {wname}', wx, 840, 320, 520, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
        add_image_rect(frame_id, f'WCard Img {wname}', wx, 840, 320, 180, 'real_hero_students.png', radius=[12, 12, 0, 0])
        add_text(frame_id, f'WCard Title {wname}', wx + 20, 1045, wname, font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
        add_text(frame_id, f'WCard Date {wname}', wx + 20, 1080, f'Jadwal: {wdate}', font_size=12, color_hex=C_BLUE, font_weight='Bold')
        add_text(frame_id, f'WCard Cost {wname}', wx + 20, 1105, wcost, font_size=12, color_hex=C_TEXT_SEC)
        add_text(frame_id, f'WCard Desc {wname}', wx + 20, 1130, wdesc, font_size=11, color_hex=C_TEXT_MUTED, width=280, height=40)
        add_rect(frame_id, f'WCard Btn {wname}', wx + 20, 1280, 280, 42, fill_hex=C_LIGHT_BLUE, stroke_hex='#bae6fd', radius=21)
        add_text(frame_id, f'WCard BtnTxt {wname}', wx + 105, 1293, 'Pilih Gelombang', font_size=12, color_hex=C_BLUE, font_weight='Bold')

    # Centered CTA button
    add_rect(frame_id, 'Gelombang Center Btn', 500, 1400, 200, 46, fill_hex=C_BLUE, radius=23)
    add_text(frame_id, 'Gelombang Center Btn Txt', 555, 1414, 'Lihat Selengkapnya', font_size=13, color_hex=C_WHITE, font_weight='Bold')

    # Section 3: Tentang Kami (y=1540, h=800, Soft Blue-Gray BG)
    add_rect(frame_id, 'Tentang BG', 0, 1540, 1200, 800, fill_hex=C_SECTION_BG)
    add_text(frame_id, 'Tentang Title', 525, 1580, 'Tentang Kami', font_size=28, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    
    about_cards = [
        ('Pendidikan Berkualitas Dan Kurikulum Sesuai Industri', 'Kurikulum dirancang bersama mitra industri global terkemuka.', 80),
        ('Agenda Terkait Mahasiswa Universitas Y', 'Kegiatan riset ilmiah, pertukaran pelajar, dan pengabdian masyarakat.', 440),
        ('Fasilitas Modern & Laboratorium Riset Terpadu', 'Laboratorium komputer berstandar internasional dan perpustakaan digital.', 800)
    ]
    for atitle, adesc, ax in about_cards:
        add_rect(frame_id, f'ACard BG {ax}', ax, 1640, 320, 520, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
        add_image_rect(frame_id, f'ACard Img {ax}', ax, 1640, 320, 180, 'hero_campus.jpg', radius=[12, 12, 0, 0])
        add_text(frame_id, f'ACard Title {ax}', ax + 20, 1845, atitle, font_size=15, color_hex=C_TEXT_PRIMARY, font_weight='Bold', width=280, height=45)
        add_text(frame_id, f'ACard Desc {ax}', ax + 20, 1910, adesc, font_size=12, color_hex=C_TEXT_MUTED, width=280, height=50)
        add_rect(frame_id, f'ACard Btn {ax}', ax + 20, 2080, 280, 42, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=21)
        add_text(frame_id, f'ACard BtnTxt {ax}', ax + 105, 2093, 'Pelajari Detail', font_size=12, color_hex=C_BLUE, font_weight='Bold')

    # Centered About CTA button
    add_rect(frame_id, 'Tentang Center Btn', 500, 2200, 200, 46, fill_hex=C_BLUE, radius=23)
    add_text(frame_id, 'Tentang Center Btn Txt', 545, 2214, 'Pelajari Lebih Lanjut', font_size=13, color_hex=C_WHITE, font_weight='Bold')

    # Footer (y=2340, h=260, Solid Cyan/Blue BG)
    add_rect(frame_id, 'Footer BG', 0, 2340, 1200, 260, fill_hex=C_BLUE)
    add_text(frame_id, 'Foot Brand', 80, 2380, 'Universitas Y', font_size=20, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Foot Address 1', 80, 2415, 'Jl. Raya Pendidikan No. 1, Kampus Terpadu', font_size=12, color_hex='#e0f2fe')
    add_text(frame_id, 'Foot Address 2', 80, 2435, 'Kota Semarang, Jawa Tengah, Indonesia', font_size=12, color_hex='#e0f2fe')
    add_text(frame_id, 'Foot Contact', 80, 2465, 'Telp: (024) 8508093 | Email: admisi@univ-y.ac.id', font_size=12, color_hex='#e0f2fe')
    
    add_text(frame_id, 'Foot Mid H', 520, 2380, 'Akreditasi Unggul BAN-PT', font_size=14, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Foot Mid D', 520, 2405, 'Reputasi institusi pendidikan tinggi berstandar mutu nasional dan internasional.', font_size=11, color_hex='#e0f2fe', width=300, height=40)
    
    add_text(frame_id, 'Foot Right H', 900, 2380, 'Media Sosial & Tautan', font_size=14, color_hex=C_WHITE, font_weight='Bold')
    add_text(frame_id, 'Foot Right D', 900, 2405, 'Instagram: @univ_y_official\nYouTube: Universitas Y Channel', font_size=11, color_hex='#e0f2fe')
    add_text(frame_id, 'Foot Copy', 420, 2550, '© 2026 Universitas Y. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex='#e0f2fe')

# 1. Homepage (Belum Login)
f_home_belum = add_frame('Homepage (Belum Login)', 0.0, 0.0, w=1200, h=2600)
add_homepage(f_home_belum, is_logged_in=False)

# 2. Homepage (Login)
f_home_login = add_frame('Homepage (Login)', 1300.0, 0.0, w=1200, h=2600)
add_homepage(f_home_login, is_logged_in=True)

# Helper function for split login/signup cards (900x560)
def add_auth_card(frame_id, is_signup=False, is_filled=False):
    # Left Half: Library Photo (w=450, h=560)
    add_image_rect(frame_id, 'Auth Lib BG', 0, 0, 450, 560, 'library_bg.jpg')
    add_rect(frame_id, 'Auth Lib Dark Overlay', 0, 0, 450, 560, fill_hex=C_NAVY, opacity=0.45)
    
    # Frosted Glassmorphism Card in Center
    add_rect(frame_id, 'Glass Card', 45, 120, 360, 310, fill_hex=C_WHITE, stroke_hex='#ffffff40', radius=12, opacity=0.92)
    add_text(frame_id, 'Glass Title', 75, 148, 'Selamat Datang!', font_size=17, color_hex=C_BLUE, font_weight='Bold')
    add_text(frame_id, 'Glass Sub', 75, 175, 'Silakan akses akun PMB Anda untuk proses:', font_size=11, color_hex=C_TEXT_MUTED)
    
    bullets = [
        'Pendaftaran Mahasiswa Baru',
        'Verifikasi data diri dan berkas',
        'Informasi jadwal seleksi CBT',
        'Status penetapan hasil kelulusan'
    ]
    by = 215
    for b in bullets:
        add_rect(frame_id, f'BDot {b}', 75, by + 4, 8, 8, fill_hex=C_BLUE, radius=4)
        add_text(frame_id, f'BTxt {b}', 92, by, b, font_size=12, color_hex=C_TEXT_PRIMARY)
        by += 38

    # Right Half: White Form Background (w=450, h=560)
    add_rect(frame_id, 'Form Right BG', 450, 0, 450, 560, fill_hex=C_WHITE)
    
    if not is_signup:
        add_text(frame_id, 'Form Title', 645, 110, 'Login', font_size=24, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
        
        # Email
        add_text(frame_id, 'Lbl Email', 510, 180, 'Email *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
        add_rect(frame_id, 'Inp Email', 510, 205, 330, 42, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=6)
        email_val = 'irfan@mail.unnes.ac.id' if is_filled else ''
        if email_val:
            add_text(frame_id, 'Val Email', 525, 218, email_val, font_size=12, color_hex=C_TEXT_PRIMARY)
        
        # Password
        add_text(frame_id, 'Lbl Pass', 510, 265, 'Password *', font_size=12, color_hex=C_TEXT_SEC, font_weight='Bold')
        add_rect(frame_id, 'Inp Pass', 510, 290, 330, 42, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=6)
        pass_val = '••••••••••••' if is_filled else ''
        if pass_val:
            add_text(frame_id, 'Val Pass', 525, 303, pass_val, font_size=12, color_hex=C_TEXT_PRIMARY)
        
        # Login Button
        add_rect(frame_id, 'Btn Submit', 720, 360, 120, 40, fill_hex=C_BLUE, radius=20)
        add_text(frame_id, 'Btn Submit Txt', 762, 372, 'Login', font_size=13, color_hex=C_WHITE, font_weight='Bold')
        
        add_text(frame_id, 'Link Toggle', 590, 435, 'Belum punya akun? Daftar', font_size=12, color_hex=C_TEXT_MUTED)
    else:
        add_text(frame_id, 'Form Title', 625, 80, 'Daftar Akun', font_size=24, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
        
        fields_signup = [
            ('Nama Lengkap *', 'Muhammad Irfan' if is_filled else ''),
            ('Email *', 'irfan@mail.unnes.ac.id' if is_filled else ''),
            ('Password *', '••••••••••••' if is_filled else ''),
            ('Konfirmasi Password *', '••••••••••••' if is_filled else '')
        ]
        sy = 135
        for flbl, fval in fields_signup:
            add_text(frame_id, f'Lbl {flbl}', 510, sy, flbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
            add_rect(frame_id, f'Inp {flbl}', 510, sy + 20, 330, 38, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=6)
            if fval:
                add_text(frame_id, f'Val {flbl}', 525, sy + 31, fval, font_size=11, color_hex=C_TEXT_PRIMARY)
            sy += 70
            
        add_rect(frame_id, 'Btn Submit', 720, 430, 120, 40, fill_hex=C_BLUE, radius=20)
        add_text(frame_id, 'Btn Submit Txt', 760, 442, 'Daftar', font_size=13, color_hex=C_WHITE, font_weight='Bold')
        add_text(frame_id, 'Link Toggle', 590, 495, 'Sudah punya akun? Login', font_size=12, color_hex=C_TEXT_MUTED)

# 3. Login (Top)
f_login_top = add_frame('Login', 2600.0, 0.0, w=900, h=560)
add_auth_card(f_login_top, is_signup=False, is_filled=False)

# 4. Login (Bottom - Filled)
f_login_bot = add_frame('Login (Filled)', 2600.0, 620.0, w=900, h=560)
add_auth_card(f_login_bot, is_signup=False, is_filled=True)

# 5. Sign Up (Top)
f_signup_top = add_frame('Sign Up', 3600.0, 0.0, w=900, h=560)
add_auth_card(f_signup_top, is_signup=True, is_filled=False)

# 6. Sign Up (Bottom - Filled)
f_signup_bot = add_frame('Sign Up (Filled)', 3600.0, 620.0, w=900, h=560)
add_auth_card(f_signup_bot, is_signup=True, is_filled=True)

print("Homepage, Login, and Sign Up frames built successfully!")

# ==========================================
# 07. Pendataan (Formulir Multi-Step Tahap 1)
# ==========================================
f_pendataan = add_frame('Pendataan', 4600.0, 0.0, w=1200, h=1400)

# Top Bar
add_rect(f_pendataan, 'P Nav BG', 0, 0, 1200, 60, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_pendataan, 'P Brand', 48, 20, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_pendataan, 'P Title', 220, 22, 'Formulir Pendaftaran Mahasiswa Baru', font_size=13, color_hex=C_TEXT_MUTED)

# Stepper (5 Steps)
add_rect(f_pendataan, 'P Stepper BG', 48, 80, 1104, 70, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=10)
steps_p = [('1', 'Biodata Diri', True), ('2', 'Pilihan Prodi', False), ('3', 'Unggah Berkas', False), ('4', 'Validasi', False), ('5', 'Pembayaran', False)]
px = 70
for i, (pnum, pname, pact) in enumerate(steps_p):
    p_bg = C_BLUE if pact else '#f1f5f9'
    p_txt = C_WHITE if pact else C_TEXT_MUTED
    add_rect(f_pendataan, f'P Circ {pnum}', px, 96, 36, 36, fill_hex=p_bg, radius=18)
    add_text(f_pendataan, f'P Num {pnum}', px + 14, 106, pnum, font_size=12, color_hex=p_txt, font_weight='Bold')
    add_text(f_pendataan, f'P Name {pnum}', px + 46, 106, pname, font_size=12, color_hex=C_TEXT_PRIMARY if pact else C_TEXT_MUTED, font_weight='Bold' if pact else 'Regular')
    if i < 4:
        add_rect(f_pendataan, f'P Line {i}', px + 155, 114, 50, 2, fill_hex='#cbd5e1')
    px += 220

# Form Container
add_rect(f_pendataan, 'P Form BG', 48, 170, 1104, 1180, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f_pendataan, 'P Form H', 80, 200, 'Langkah 1: Biodata Lengkap Calon Mahasiswa', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f_pendataan, 'P Div 1', 80, 235, 1040, 1, fill_hex=C_BORDER)

c1_p = [
    ('Nomor Induk Kependudukan (NIK) *', '3302192804040003'),
    ('Nomor Induk Siswa Nasional (NISN) *', '0058291042'),
    ('Nama Lengkap (Sesuai Ijazah) *', 'Muhammad Irfan'),
    ('Jenis Kelamin *', 'Laki-laki'),
    ('Tempat Lahir *', 'Semarang'),
    ('Tanggal Lahir *', '14 / 08 / 2005'),
    ('Nama Ibu Kandung *', 'Siti Aminah'),
    ('Penghasilan Orang Tua / Wali *', 'Rp 4.000.000 - Rp 6.000.000 / bulan')
]
py_inp = 255
for lbl, val in c1_p:
    add_text(f_pendataan, f'P Lbl {lbl}', 80, py_inp, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f_pendataan, f'P Inp {lbl}', 80, py_inp + 18, 500, 40, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=6)
    add_text(f_pendataan, f'P Val {lbl}', 95, py_inp + 29, val, font_size=12, color_hex=C_TEXT_PRIMARY)
    py_inp += 74

c2_p = [
    ('Agama *', 'Islam'),
    ('Nomor Handphone / WhatsApp *', '081234567890'),
    ('Email Siswa Aktif *', 'irfan@mail.unnes.ac.id'),
    ('Asal Sekolah (SMA/SMK/MA) *', 'SMAN 1 Semarang'),
    ('Jurusan Sekolah Asal *', 'IPA / MIPA'),
    ('Tahun Kelulusan *', '2026'),
    ('Alamat Lengkap Tempat Tinggal *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'),
    ('Kota / Kabupaten *', 'Kota Semarang, Jawa Tengah')
]
py_inp2 = 255
for lbl, val in c2_p:
    add_text(f_pendataan, f'P Lbl {lbl}', 620, py_inp2, lbl, font_size=11, color_hex=C_TEXT_SEC, font_weight='Bold')
    add_rect(f_pendataan, f'P Inp {lbl}', 620, py_inp2 + 18, 500, 40, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=6)
    add_text(f_pendataan, f'P Val {lbl}', 635, py_inp2 + 29, val, font_size=12, color_hex=C_TEXT_PRIMARY)
    py_inp2 += 74

add_rect(f_pendataan, 'P Div Bot', 80, 1260, 1040, 1, fill_hex=C_BORDER)
add_rect(f_pendataan, 'P Btn Next', 880, 1285, 240, 46, fill_hex=C_BLUE, radius=23)
add_text(f_pendataan, 'P Btn Next Txt', 915, 1299, 'Lanjut ke Pilihan Prodi →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

# ==========================================
# 08. Unggahan (4 Upload Boxes)
# ==========================================
f_unggahan = add_frame('Unggahan', 5900.0, 0.0, w=1200, h=1200)

add_rect(f_unggahan, 'U Nav BG', 0, 0, 1200, 60, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_unggahan, 'U Brand', 48, 20, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_unggahan, 'U Sub', 220, 22, 'Unggah Berkas Dokumen Persyaratan', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f_unggahan, 'U Card BG', 48, 80, 1104, 1080, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f_unggahan, 'U Card H', 80, 110, 'Langkah 3: Unggah Berkas Dokumen Persyaratan', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_unggahan, 'U Card S', 80, 135, 'Format: PDF / JPG / PNG (Maksimal 2 MB per berkas).', font_size=12, color_hex=C_TEXT_MUTED)
add_rect(f_unggahan, 'U Div', 80, 160, 1040, 1, fill_hex=C_BORDER)

up_docs = [
    ('1. Pas Foto Formal 4x6 Background Merah *', 'foto_formal_4x6.jpg (450 KB)', 'Berhasil diunggah • Format sesuai'),
    ('2. Scan Ijazah SMA / Surat Keterangan Lulus (SKL) *', 'ijazah_irfan_2026.pdf (1.2 MB)', 'Berhasil diunggah • Format sesuai'),
    ('3. Scan Kartu Keluarga (KK) Legalisir *', 'kk_keluarga_irfan.pdf (890 KB)', 'Berhasil diunggah • Format sesuai'),
    ('4. Surat Keterangan Penghasilan / Slip Gaji Orang Tua *', 'slip_penghasilan_ortu.pdf (620 KB)', 'Berhasil diunggah • Format sesuai')
]
uy_card = 180
for dtitle, dfile, dstat in up_docs:
    add_rect(f_unggahan, f'UBox {dtitle}', 80, uy_card, 1040, 180, fill_hex=C_CANVAS, stroke_hex=C_BORDER, stroke_width=1.5, radius=10)
    add_text(f_unggahan, f'UTitle {dtitle}', 110, uy_card + 25, dtitle, font_size=14, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f_unggahan, f'UFile {dtitle}', 110, uy_card + 55, dfile, font_size=13, color_hex=C_BLUE, font_weight='Bold')
    add_text(f_unggahan, f'UStat {dtitle}', 110, uy_card + 80, f'Status: {dstat}', font_size=11, color_hex='#15803d')
    add_rect(f_unggahan, f'UBtn {dtitle}', 110, uy_card + 115, 150, 38, fill_hex=C_BLUE, radius=19)
    add_text(f_unggahan, f'UBtnTxt {dtitle}', 142, uy_card + 127, 'Unggah Ulang', font_size=12, color_hex=C_WHITE, font_weight='Bold')
    uy_card += 205

add_rect(f_unggahan, 'U Btn Finish', 880, 1020, 240, 46, fill_hex=C_BLUE, radius=23)
add_text(f_unggahan, 'U Btn Finish Txt', 915, 1034, 'Lanjut ke Validasi Data →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

# ==========================================
# 09. Prodi (Pilihan Program Studi)
# ==========================================
f_prodi = add_frame('Prodi', 7200.0, 0.0, w=1200, h=900)

add_rect(f_prodi, 'Pr Nav BG', 0, 0, 1200, 60, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_prodi, 'Pr Brand', 48, 20, 'PMB UNNES 2026', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_prodi, 'Pr Sub', 220, 22, 'Pilihan Program Studi Calon Mahasiswa', font_size=13, color_hex=C_TEXT_MUTED)

add_rect(f_prodi, 'Pr Card BG', 48, 80, 1104, 780, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=14)
add_text(f_prodi, 'Pr Card H', 80, 110, 'Langkah 2: Tentukan Pilihan Program Studi S1', font_size=18, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_rect(f_prodi, 'Pr Div', 80, 145, 1040, 1, fill_hex=C_BORDER)

# Dropdown Pilihan 1
add_text(f_prodi, 'Pr Lbl 1', 80, 175, 'Pilihan Program Studi 1 (Prioritas Utama) *', font_size=13, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f_prodi, 'Pr Box 1', 80, 205, 1040, 50, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=8)
add_text(f_prodi, 'Pr Val 1', 105, 220, 'S1 - Teknik Informatika (Fakultas MIPA) — Akreditasi Unggul', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_prodi, 'Pr Arrow 1', 1090, 220, '▼', font_size=12, color_hex=C_TEXT_MUTED)

# Dropdown Pilihan 2
add_text(f_prodi, 'Pr Lbl 2', 80, 285, 'Pilihan Program Studi 2 (Pilihan Cadangan) *', font_size=13, color_hex=C_TEXT_SEC, font_weight='Bold')
add_rect(f_prodi, 'Pr Box 2', 80, 315, 1040, 50, fill_hex=C_CANVAS, stroke_hex=C_BORDER, radius=8)
add_text(f_prodi, 'Pr Val 2', 105, 330, 'S1 - Sistem Informasi (Fakultas MIPA) — Akreditasi Unggul', font_size=13, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
add_text(f_prodi, 'Pr Arrow 2', 1090, 330, '▼', font_size=12, color_hex=C_TEXT_MUTED)

# Kuota Daya Tampung Card
add_rect(f_prodi, 'Pr Stat Card', 80, 400, 1040, 140, fill_hex='#f0f9ff', stroke_hex='#bae6fd', radius=10)
add_text(f_prodi, 'Pr Stat H', 110, 425, 'Informasi Daya Tampung & Keketatan Seleksi Mandiri:', font_size=13, color_hex=C_BLUE, font_weight='Bold')
add_text(f_prodi, 'Pr Stat T1', 110, 455, '• Pilihan 1: Teknik Informatika — Daya Tampung: 120 Kursi  |  Peminat: 1,840 Siswa', font_size=12, color_hex=C_TEXT_PRIMARY)
add_text(f_prodi, 'Pr Stat T2', 110, 485, '• Pilihan 2: Sistem Informasi — Daya Tampung: 90 Kursi  |  Peminat: 1,120 Siswa', font_size=12, color_hex=C_TEXT_PRIMARY)

add_rect(f_prodi, 'Pr Btn Next', 880, 780, 240, 46, fill_hex=C_BLUE, radius=23)
add_text(f_prodi, 'Pr Btn Next Txt', 915, 794, 'Lanjut ke Unggah Berkas →', font_size=13, color_hex=C_WHITE, font_weight='Bold')

# ==========================================
# 10. Dokumen/Persuratan Admin (Panel Verifikasi)
# ==========================================
f_admin = add_frame('Dokumen/Persuratan Admin', 8500.0, 0.0, w=1200, h=900)

add_rect(f_admin, 'Adm Nav BG', 0, 0, 1200, 60, fill_hex=C_WHITE, stroke_hex=C_BORDER)
add_text(f_admin, 'Adm Brand', 48, 20, 'PMB Admin Panel', font_size=16, color_hex=C_BLUE, font_weight='Bold')
add_text(f_admin, 'Adm Sub', 220, 22, 'Verifikasi Berkas Calon Mahasiswa Baru', font_size=13, color_hex=C_TEXT_MUTED)

# Admin Table with Signature Blue Header
add_rect(f_admin, 'Adm Table BG', 48, 90, 1104, 750, fill_hex=C_WHITE, stroke_hex=C_BORDER, radius=12)
add_rect(f_admin, 'Adm Th BG', 48, 90, 1104, 44, fill_hex=C_BLUE, radius=[12, 12, 0, 0])
add_text(f_admin, 'Adm Th 1', 75, 105, 'NO. PENDAFTARAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'Adm Th 2', 260, 105, 'NAMA LENGKAP & NISN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'Adm Th 3', 520, 105, 'PROGRAM STUDI PILIHAN', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'Adm Th 4', 780, 105, 'STATUS BERKAS', font_size=11, color_hex=C_WHITE, font_weight='Bold')
add_text(f_admin, 'Adm Th 5', 980, 105, 'AKSI', font_size=11, color_hex=C_WHITE, font_weight='Bold')

admin_rows = [
    ('PMB-2026-08492', 'Muhammad Irfan', '0058291042', 'S1 Teknik Informatika', 'MENUNGGU', '#fef3c7', '#b45309'),
    ('PMB-2026-08493', 'Siti Nurhaliza', '0057193821', 'S1 Sistem Informasi', 'PERLU REVISI', '#fff1f2', '#be123c'),
    ('PMB-2026-08494', 'Budi Santoso', '0059281742', 'S1 Teknik Elektro', 'TERVERIFIKASI', '#ecfdf5', '#065f46'),
    ('PMB-2026-08495', 'Annisa Rahmawati', '0056192841', 'S1 Pend. Matematika', 'MENUNGGU', '#fef3c7', '#b45309'),
    ('PMB-2026-08496', 'Dimas Arya Pratama', '0058918274', 'S1 Ilmu Komputer', 'TERVERIFIKASI', '#ecfdf5', '#065f46'),
    ('PMB-2026-08497', 'Fadhilah Nurul H.', '0057281932', 'S1 Farmasi', 'PERLU REVISI', '#fff1f2', '#be123c'),
    ('PMB-2026-08498', 'Rizky Ramadhan', '0059182736', 'S1 Manajemen', 'TERVERIFIKASI', '#ecfdf5', '#065f46')
]
ry_adm = 134
for rno, rname, rnisn, rprodi, rstat, rbg, rcol in admin_rows:
    add_rect(f_admin, f'Adm Row {rno}', 48, ry_adm, 1104, 52, fill_hex=C_WHITE, stroke_hex='#f1f5f9')
    add_text(f_admin, f'Adm C1 {rno}', 75, ry_adm + 18, rno, font_size=11, color_hex=C_BLUE, font_weight='Bold')
    add_text(f_admin, f'Adm C2 {rno}', 260, ry_adm + 12, rname, font_size=12, color_hex=C_TEXT_PRIMARY, font_weight='Bold')
    add_text(f_admin, f'Adm C2S {rno}', 260, ry_adm + 28, f'NISN: {rnisn}', font_size=10, color_hex=C_TEXT_MUTED)
    add_text(f_admin, f'Adm C3 {rno}', 520, ry_adm + 18, rprodi, font_size=11, color_hex=C_TEXT_SEC)
    add_rect(f_admin, f'Adm C4 {rno}', 775, ry_adm + 12, 115, 26, fill_hex=rbg, radius=6)
    add_text(f_admin, f'Adm C4T {rno}', 795, ry_adm + 18, rstat, font_size=10, color_hex=rcol, font_weight='Bold')
    add_rect(f_admin, f'Adm C5 {rno}', 970, ry_adm + 10, 110, 32, fill_hex=C_BLUE, radius=6)
    add_text(f_admin, f'Adm C5T {rno}', 995, ry_adm + 19, 'Periksa', font_size=11, color_hex=C_WHITE, font_weight='Bold')
    ry_adm += 52

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/projek-ansi.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack into projek-ansi.figcraft zip directly with images!
zip_path = 'C:/projects/ta-pemweb/uidesign/projek-ansi.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully compiled exact PROJEK-ANSI replica into {zip_path} with {len(doc["nodes"])} nodes!')
