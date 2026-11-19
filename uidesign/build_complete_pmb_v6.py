import zipfile, hashlib, json, os
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

# Exact Master V6 Colors
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
    'name': 'PMB 2026 — Modern University Admission Platform',
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

# Standard Desktop Navbar Builder Helper
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

# Standard Desktop Footer Builder Helper
def add_desktop_footer(frame_id, y_pos=960):
    add_rect(frame_id, 'Footer BG', 0, y_pos, 1440, 64, fill_hex=C_PRIMARY)
    add_text(frame_id, 'Footer Copy', 80, y_pos + 25, '© 2026 Universitas Indonesia — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex=C_SURFACE)

print('Base core helpers initialized.')

# ==========================================
# PAGE 1: 01 — Cover & Design Overview
# ==========================================
p1 = add_page(1, '01 — Cover & Design Overview')
f_cov = add_frame(p1, 'Cover Presentation & Project Overview', 0, 0, 1440, 1024, C_BACKGROUND)

add_rect(f_cov, 'Cov Hero BG', 80, 80, 1280, 480, fill_hex=C_PRIMARY, radius=24)
add_image_rect(f_cov, 'Cov Hero Photo', 80, 80, 1280, 480, 'hero_campus.jpg', radius=24, opacity=0.35)

add_rect(f_cov, 'Cov Tag Pill', 120, 120, 270, 32, fill_hex=C_SURFACE, radius=16)
add_text(f_cov, 'Cov Tag Txt', 140, 128, 'MASTER FIGMA DESIGN V6', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_cov, 'Cov Title 1', 120, 175, 'PMB 2026 — Modern University', font_size=48, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_cov, 'Cov Title 2', 120, 235, 'Admission Platform', font_size=48, color_hex=C_WARNING, font_weight='Bold')

add_text(f_cov, 'Cov Desc 1', 120, 305, 'Desktop Web Only · Applicant-Only · Complete End-to-End Higher Education Experience.', font_size=16, color_hex=C_MUTED_SURFACE)
add_text(f_cov, 'Cov Desc 2', 120, 332, 'Comprehensive design system, 15 dedicated pages, 48 connected routes, and strict visual authority.', font_size=16, color_hex=C_MUTED_SURFACE)

# Meta Box
add_rect(f_cov, 'Cov Meta Box', 120, 385, 1200, 130, fill_hex=C_SURFACE, radius=16)
cmetas = [
    ('SCOPE', 'Desktop Web Only (1440x1024)'),
    ('TARGET USER', 'Calon Mahasiswa (Applicant-Only)'),
    ('INSTITUTION', 'Universal PTN / PTS Template'),
    ('EXCLUSIONS', 'Zero Mobile • Zero Admin Interfaces')
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

add_text(f_cov, 'Cov Footer', 80, 975, '© 2026 PMB Master Design Specification V6 — End-to-End Prospective Student Experience.', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 2: 02 — Design Foundations
# ==========================================
p2 = add_page(2, '02 — Design Foundations')
f_fnd = add_frame(p2, 'Design Foundations — Tokens & Hierarchy', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f_fnd, 'Fnd Title', 80, 60, 'Design Foundations — Strict Color Tokens & Typographic Hierarchy', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_fnd, 'Fnd Sub', 80, 102, 'Sistem token desain resmi PMB 2026 yang menjadi acuan konsistensi seluruh 15 halaman.', font_size=15, color_hex=C_SECONDARY_TEXT)

# 12 Master Colors
add_text(f_fnd, 'Pal Header', 80, 150, '12 STRICT COLOR TOKENS', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

colors_v6 = [
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
for i, (cname, chex, ctxt) in enumerate(colors_v6):
    add_rect(f_fnd, f'Sw BG {cname}', cx, cy, 105, 110, fill_hex=chex, stroke_hex=C_BORDER, radius=12)
    add_text(f_fnd, f'Sw Name {cname}', cx + 8, cy + 68, cname, font_size=10, color_hex=ctxt, font_weight='Bold')
    add_text(f_fnd, f'Sw Hex {cname}', cx + 8, cy + 86, chex, font_size=11, color_hex=ctxt)
    cx += 116
    if (i + 1) % 6 == 0:
        cx = 80
        cy += 125

# Typography
add_text(f_fnd, 'Typo Header', 80, 460, 'TYPOGRAPHY SCALE (PLUS JAKARTA SANS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
tscales = [
    ('Hero Title (54px Bold)', 'Gerbang Menuju Perguruan Tinggi Impian Anda', 54, 'Bold'),
    ('Page Title (40px Bold)', 'Formulir Pendaftaran Siswa & Verifikasi Dokumen', 40, 'Bold'),
    ('Section Title (32px Bold)', 'Pilihan Jalur Masuk Seleksi Akademik 2026', 32, 'Bold'),
    ('Card Title (18px Semibold)', 'S1 Teknik Informatika — Akreditasi Unggul BAN-PT', 18, 'Bold'),
    ('Body Text (15px Regular)', 'Wujudkan impian studi dengan proses seleksi digital terintegrasi, transparan, dan terpercaya.', 15, 'Regular'),
    ('Supporting Label (12px Medium)', 'NOMOR INDUK KEPENDUDUKAN (NIK) SESUAI KTP / KK RESMI *', 12, 'Bold')
]
ty2 = 495
for tscale, tex, tsz, twg in tscales:
    add_text(f_fnd, f'TLbl {tscale}', 80, ty2, tscale, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_fnd, f'TEx {tscale}', 320, ty2, tex, font_size=tsz, color_hex=C_PRIMARY_TEXT, font_weight=twg)
    ty2 += int(tsz * 1.5) + 12

# Spacing
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

add_text(f_sys, 'Sys Title', 80, 60, 'Pustaka Komponen UI & Status Variants', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_sys, 'Sys Sub', 80, 102, 'Komponen pill-shaped, form input, dan 20 status badge pendaftaran yang dapat diedit.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Buttons
add_text(f_sys, 'Btn H', 80, 150, '1. PILL-SHAPED BUTTON SYSTEM', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
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

# 20 Status Badges (Section 17)
add_text(f_sys, 'Badge H', 80, 260, '2. APPLICATION STATUS COMPONENTS (20 VARIANTS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

status_20 = [
    ('Draft', C_MUTED_SURFACE, C_BORDER, C_SECONDARY_TEXT),
    ('Profile Incomplete', '#fffbeb', '#fde68a', '#b45309'),
    ('Documents Incomplete', '#fffbeb', '#fde68a', '#b45309'),
    ('Documents Pending', '#fef3c7', '#fde68a', '#b45309'),
    ('Documents Rejected', '#fff1f2', '#fecdd3', C_ERROR),
    ('Resubmission Required', '#fff1f2', '#fecdd3', C_ERROR),
    ('Payment Pending', '#fffbeb', '#fde68a', '#b45309'),
    ('Payment Verified', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Submitted', '#f0f9ff', '#bae6fd', C_PRIMARY),
    ('Under Review', '#fef3c7', '#fde68a', '#b45309'),
    ('Eligible', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Not Eligible', '#fff1f2', '#fecdd3', C_ERROR),
    ('Exam Scheduled', '#f0f9ff', '#bae6fd', C_PRIMARY),
    ('Selection Completed', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Result Pending', '#fef3c7', '#fde68a', '#b45309'),
    ('Accepted', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Not Accepted', '#fff1f2', '#fecdd3', C_ERROR),
    ('Waitlisted', '#fffbeb', '#fde68a', '#b45309'),
    ('Offer Accepted', '#ecfdf5', '#a7f3d0', C_SUCCESS),
    ('Re-registration Completed', '#ecfdf5', '#a7f3d0', C_SUCCESS)
]
sbx = 80
sby = 295
for i, (stxt, sbg, sbrd, scol) in enumerate(status_20):
    bw = len(stxt) * 8 + 32
    add_rect(f_sys, f'StBadge {stxt}', sbx, sby, bw, 32, fill_hex=sbg, stroke_hex=sbrd, radius=16)
    add_text(f_sys, f'StTxt {stxt}', sbx + 16, sby + 8, stxt, font_size=11, color_hex=scol, font_weight='Bold')
    sbx += bw + 14
    if (i + 1) % 5 == 0:
        sbx = 80
        sby += 46

# Stepper System
add_text(f_sys, 'Step H', 80, 520, '3. CONNECTED PROGRESS STEPPER (5 CHECKPOINTS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
step_examples = [
    ('1', 'Data Diri', 'Completed', C_SUCCESS),
    ('2', 'Dokumen', 'Active', C_PRIMARY),
    ('3', 'Pembayaran', 'Upcoming', C_SECONDARY_TEXT),
    ('4', 'Seleksi', 'Upcoming', C_SECONDARY_TEXT),
    ('5', 'Hasil', 'Upcoming', C_SECONDARY_TEXT)
]
sex = 80
for snum, stitle, sstate, scol in step_examples:
    sbg = scol if sstate in ['Completed', 'Active'] else C_MUTED_SURFACE
    stxt = C_SURFACE if sstate in ['Completed', 'Active'] else C_SECONDARY_TEXT
    add_rect(f_sys, f'SE Node {snum}', sex, 555, 42, 42, fill_hex=sbg, radius=21)
    add_text(f_sys, f'SE Num {snum}', sex + 15, 567, snum, font_size=13, color_hex=stxt, font_weight='Bold')
    add_text(f_sys, f'SE Title {snum}', sex + 52, 562, stitle, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold' if sstate=='Active' else 'Regular')
    add_text(f_sys, f'SE State {snum}', sex + 52, 582, sstate, font_size=11, color_hex=scol)
    if int(snum) < 5:
        add_rect(f_sys, f'SE Line {snum}', sex + 165, 574, 70, 2, fill_hex=C_BORDER)
    sex += 250

# ==========================================
# PAGE 4: 04 — Public Website (A01 — Homepage)
# ==========================================
p4 = add_page(4, '04 — Public Website')
f_pub = add_frame(p4, 'A01 — Homepage', 0, 0, 1440, 1024, C_BACKGROUND)

add_desktop_navbar(f_pub, active_nav='Beranda')

# Hero (w: 1280, x: 80, y: 110)
add_text(f_pub, 'P4 Hero 1', 80, 140, 'Penerimaan', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_pub, 'P4 Hero 2', 80, 205, 'Mahasiswa Baru', font_size=54, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_pub, 'P4 Hero 3', 80, 270, '2026', font_size=54, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_pub, 'P4 Sub 1', 80, 350, 'Wujudkan mimpi, raih masa depan', font_size=16, color_hex=C_SECONDARY_TEXT)
add_text(f_pub, 'P4 Sub 2', 80, 375, 'bersama Universitas Indonesia.', font_size=16, color_hex=C_SECONDARY_TEXT)

add_rect(f_pub, 'P4 Btn CTA', 80, 425, 195, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f_pub, 'P4 Btn CTA Txt', 115, 439, 'Daftar Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_text(f_pub, 'P4 Video CTA', 305, 439, '▶   Tonton Video', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Real Hero Students Photo on Right
add_image_rect(f_pub, 'P4 Real Photo', 680, 110, 680, 520, 'real_hero_students.png', radius=24)

# Floating Bottom White Ribbon Bar (x: 80, y: 670, w: 1280, h: 96)
add_rect(f_pub, 'P4 Ribbon BG', 80, 670, 1280, 96, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)

ribbon_items_p4 = [
    ('Periode Pendaftaran', '3 Jan - 30 Jun 2026', 'CAL', 120),
    ('Jalur Seleksi', 'SNBP, SNBT, Mandiri', 'CAP', 440),
    ('Program Studi', '100+ Pilihan', 'BOK', 760),
    ('Beasiswa', 'Hingga 100%', 'GFT', 1060)
]
for rlbl, rval, rico, rx in ribbon_items_p4:
    add_rect(f_pub, f'P4 RIco BG {rico}', rx, 696, 44, 44, fill_hex=C_MUTED_SURFACE, radius=10)
    add_text(f_pub, f'P4 RIco Txt {rico}', rx + 10, 709, rico, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f_pub, f'P4 RLbl {rlbl}', rx + 56, 700, rlbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_pub, f'P4 RVal {rval}', rx + 56, 720, rval, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# 3 Jalur Cards Below (y: 795)
add_text(f_pub, 'P4 Sec Jalur Title', 80, 795, 'JALUR SELEKSI PENERIMAAN 2026', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
jcards_p4 = [
    ('SNBP (Prestasi)', 'Nilai rapor semester 1-5 & portofolio.', '10 Nov - 20 Des 2026', 'card_snbp.jpg', 80),
    ('SNBT (UTBK)', 'Tes skolastik & literasi BPPP.', '15 Jan - 28 Feb 2027', 'card_snbt.jpg', 520),
    ('Mandiri Reguler', 'CBT terpadu & prestasi khusus.', '01 Mar - 15 Apr 2027', 'card_mandiri.jpg', 960)
]
for jtitle, jdesc, jdate, jimg, jx in jcards_p4:
    add_rect(f_pub, f'P4 JC BG {jtitle}', jx, 825, 400, 130, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
    add_image_rect(f_pub, f'P4 JC Img {jtitle}', jx, 825, 140, 130, jimg, radius=[14, 0, 0, 14])
    add_text(f_pub, f'P4 JC Title {jtitle}', jx + 155, 845, jtitle, font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_pub, f'P4 JC Desc {jtitle}', jx + 155, 870, jdesc, font_size=11, color_hex=C_SECONDARY_TEXT, width=230, height=30)
    add_text(f_pub, f'P4 JC Date {jtitle}', jx + 155, 915, jdate, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_desktop_footer(f_pub, y_pos=975)

# ==========================================
# PAGE 5: 05 — Program Discovery
# ==========================================
p5 = add_page(5, '05 — Program Discovery')
f_prog_dir = add_frame(p5, 'A02 — Program Directory', 0, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_prog_dir, active_nav='Program Studi')

add_text(f_prog_dir, 'F2 Title', 80, 120, 'Program Studi', font_size=38, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_prog_dir, 'F2 Sub', 80, 168, 'Temukan program studi yang sesuai dengan minat dan bakatmu.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Top Right Campus Photo
add_image_rect(f_prog_dir, 'F2 Bldg Hero', 780, 105, 580, 220, 'real_bldg_hero.png', radius=18)

# Search
add_rect(f_prog_dir, 'F2 Search Inp', 80, 215, 480, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f_prog_dir, 'F2 Search Icon', 102, 228, '🔍', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f_prog_dir, 'F2 Search Text', 130, 228, 'Cari program studi...', font_size=13, color_hex=C_SECONDARY_TEXT)

# Filter Pills
fpx2 = 80
for ptxt, pact in [('Semua', True), ('Fakultas ⌵', False), ('Jenjang ⌵', False), ('Akreditasi ⌵', False)]:
    pbg = C_PRIMARY if pact else C_SURFACE
    ptcol = C_SURFACE if pact else C_PRIMARY_TEXT
    pw = len(ptxt) * 9 + 30
    add_rect(f_prog_dir, f'F2 P {ptxt}', fpx2, 280, pw, 38, fill_hex=pbg, stroke_hex=None if pact else C_BORDER, radius=19)
    add_text(f_prog_dir, f'F2 PTxt {ptxt}', fpx2 + 15, 290, ptxt, font_size=12, color_hex=ptcol, font_weight='Bold' if pact else 'Regular')
    fpx2 += pw + 12

add_text(f_prog_dir, 'F2 See All', 1210, 290, 'Lihat Semua Program →', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# 3 Program Cards
cards_p5 = [
    ('Teknik Informatika', 'Fakultas Ilmu Komputer', 'S1', 'Akreditasi Unggul', 'real_bldg_ti.png', 80),
    ('Manajemen', 'Fakultas Ekonomi & Bisnis', 'S1', 'Akreditasi Unggul', 'real_bldg_mn.png', 520),
    ('Psikologi', 'Fakultas Psikologi', 'S1', 'Akreditasi A', 'real_bldg_ps.png', 960)
]
for ctitle, cfac, cdeg, cakred, cimg, cx in cards_p5:
    add_rect(f_prog_dir, f'F2 CardBG {ctitle}', cx, 360, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_image_rect(f_prog_dir, f'F2 CardImg {ctitle}', cx, 360, 400, 185, cimg, radius=[18, 18, 0, 0])
    add_text(f_prog_dir, f'F2 CardTitle {ctitle}', cx + 22, 565, ctitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_prog_dir, f'F2 CardFac {ctitle}', cx + 22, 592, cfac, font_size=13, color_hex=C_SECONDARY_TEXT)
    add_text(f_prog_dir, f'F2 CardDeg {ctitle}', cx + 22, 612, cdeg, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f_prog_dir, f'F2 AkredPill {ctitle}', cx + 22, 642, 135, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
    add_text(f_prog_dir, f'F2 AkredTxt {ctitle}', cx + 36, 648, f'● {cakred}', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
    add_rect(f_prog_dir, f'F2 ArrowCircle {ctitle}', cx + 340, 638, 36, 36, fill_hex=C_MUTED_SURFACE, radius=18)
    add_text(f_prog_dir, f'F2 ArrowTxt {ctitle}', cx + 352, 646, '→', font_size=15, color_hex=C_PRIMARY, font_weight='Bold')

# Program Detail Frame on Same Page (offset at X=1540)
f_prog_det = add_frame(p5, 'A03 — Program Detail', 1540, 0, 1440, 1024, C_BACKGROUND)
add_desktop_navbar(f_prog_det, active_nav='Program Studi')
add_text(f_prog_det, 'F5 Back Link', 80, 110, '← Kembali ke Program Studi', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_image_rect(f_prog_det, 'F5 Bldg Photo', 80, 140, 460, 300, 'real_bldg_detail.png', radius=18)
add_text(f_prog_det, 'F5 Major Title', 580, 160, 'Teknik Informatika', font_size=36, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_prog_det, 'F5 Major Fac', 580, 210, 'Fakultas Ilmu Komputer', font_size=16, color_hex=C_SECONDARY_TEXT)
add_rect(f_prog_det, 'F5 Akred Pill', 580, 245, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f_prog_det, 'F5 Akred Pill Txt', 594, 251, '● Akreditasi Unggul', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

add_text(f_prog_det, 'F5 Desc 1', 580, 290, 'Program studi Teknik Informatika membekali mahasiswa dengan kompetensi', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f_prog_det, 'F5 Desc 2', 580, 312, 'di bidang teknologi informasi, rekayasa perangkat lunak, dan kecerdasan buatan.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f_prog_det, 'F5 Btn Daftar', 580, 360, 180, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f_prog_det, 'F5 Btn Daftar Txt', 612, 374, 'Daftar Sekarang', font_size=13, color_hex=C_SURFACE, font_weight='Bold')
add_rect(f_prog_det, 'F5 Btn Kurikulum', 780, 360, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f_prog_det, 'F5 Btn Kurikulum Txt', 812, 374, 'Lihat Kurikulum', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Detail Tabs
dtx5 = 80
for dti in ['Overview', 'Kurikulum', 'Prospek Karir', 'Persyaratan']:
    is_act = (dti == 'Overview')
    add_text(f_prog_det, f'F5 DTab {dti}', dtx5, 490, dti, font_size=14, color_hex=C_PRIMARY if is_act else C_SECONDARY_TEXT, font_weight='Bold' if is_act else 'Regular')
    if is_act:
        add_rect(f_prog_det, 'F5 DTab Line', dtx5, 520, 65, 3, fill_hex=C_PRIMARY)
    dtx5 += 140

add_rect(f_prog_det, 'F5 Tabs Div Line', 80, 523, 1280, 1, fill_hex=C_BORDER)
add_text(f_prog_det, 'F5 About Title', 80, 555, 'Tentang Program Studi', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_prog_det, 'F5 About Desc 1', 80, 590, 'Teknik Informatika berfokus pada pengembangan teknologi digital, perancangan algoritma efisien, sistem cerdas,', font_size=14, color_hex=C_SECONDARY_TEXT)
add_text(f_prog_det, 'F5 About Desc 2', 80, 614, 'serta infrastruktur komputasi awan untuk masa depan yang lebih baik.', font_size=14, color_hex=C_SECONDARY_TEXT)

add_rect(f_prog_det, 'F5 Prog Info Box', 880, 555, 480, 180, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f_prog_det, 'F5 Prog Info Title', 905, 580, 'Informasi Program', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_prog_det, 'F5 Prog Info Div', 905, 608, 430, 1, fill_hex=C_BORDER)
add_text(f_prog_det, 'F5 Jenjang Lbl', 905, 625, 'Jenjang:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f_prog_det, 'F5 Jenjang Val', 905, 645, 'Sarjana (S1)', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_prog_det, 'F5 Fac Lbl', 1120, 625, 'Fakultas:', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f_prog_det, 'F5 Fac Val', 1120, 645, 'Ilmu Komputer', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

print('Pages 1-5 built!')
