import zipfile, hashlib, json, os, subprocess
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

image_index = [{'hash': meta['hash'], 'width': meta['width'], 'height': meta['height']} for meta in images_meta.values()]

# Exact Master Prompt Colors
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
    'current_page': 4, # Open directly on Public Website (Page 4)
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

# ==========================================
# PAGE 1: 01 — Cover & Design Direction
# ==========================================
p1 = add_page(1, '01 — Cover & Design Direction')
f_cov = add_frame(p1, 'Cover Presentation', 0, 0, 1440, 1024, C_BACKGROUND)

# Cover Header Card
add_rect(f_cov, 'Cov Hero BG', 80, 80, 1280, 480, fill_hex=C_PRIMARY, radius=24)
add_image_rect(f_cov, 'Cov Hero Photo', 80, 80, 1280, 480, 'hero_campus.jpg', radius=24, opacity=0.35)

add_rect(f_cov, 'Cov Tag Pill', 120, 120, 240, 32, fill_hex=C_SURFACE, radius=16)
add_text(f_cov, 'Cov Tag Txt', 140, 128, 'FIGMA DESIGN SPECIFICATION', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_cov, 'Cov Title 1', 120, 175, 'PMB 2026 — Modern University', font_size=48, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_cov, 'Cov Title 2', 120, 235, 'Admission Platform', font_size=48, color_hex=C_WARNING, font_weight='Bold')

add_text(f_cov, 'Cov Desc 1', 120, 305, 'Strict Design Reference · High-Fidelity · Figma Native Component Architecture.', font_size=16, color_hex=C_MUTED_SURFACE)
add_text(f_cov, 'Cov Desc 2', 120, 332, 'Comprehensive design system and interface system for higher education admissions.', font_size=16, color_hex=C_MUTED_SURFACE)

# Cover Metadata Box
add_rect(f_cov, 'Cov Meta Box', 120, 385, 1200, 130, fill_hex=C_SURFACE, radius=16)
cmetas = [
    ('PRODUCT', 'PMB 2026 Portal'),
    ('INSTITUTION', 'Universal University Template'),
    ('TARGET AUDIENCE', 'Prospective Students & Committee'),
    ('DESIGN SYSTEM', 'Plus Jakarta Sans • 4px Grid')
]
cmx = 150
for clbl, cval in cmetas:
    add_text(f_cov, f'CM Lbl {clbl}', cmx, 415, clbl, font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'CM Val {clbl}', cmx, 440, cval, font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    cmx += 280

# 3 Core Pillars Below
pillars = [
    ('Clean University Aesthetic', 'Dominan biru (#1554B8) dan putih dengan fotografi mahasiswa asli yang autentik dan berwibawa.'),
    ('Strict Typographic Hierarchy', 'Plus Jakarta Sans (400, 500, 600, 700) dengan skala terukur dan angka tabular presisi.'),
    ('Pill-Shaped Tactile Controls', 'Komponen tombol rounded-full berbentuk pill yang modern, ramah pengguna, dan responsif.')
]
plx = 80
for ptitle, pdesc in pillars:
    add_rect(f_cov, f'Pil BG {ptitle}', plx, 600, 400, 340, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_rect(f_cov, f'Pil Accent {ptitle}', plx, 600, 400, 6, fill_hex=C_PRIMARY, radius=[18, 18, 0, 0])
    add_text(f_cov, f'Pil Title {ptitle}', plx + 28, 635, ptitle, font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_cov, f'Pil Desc {ptitle}', plx + 28, 675, pdesc, font_size=14, color_hex=C_SECONDARY_TEXT, width=344, height=60)
    plx += 440

add_text(f_cov, 'Cov Footer', 80, 975, '© 2026 PMB Master Design Specification — Dedicated to Academic Excellence & Modern UX.', font_size=12, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 2: 02 — Foundations
# ==========================================
p2 = add_page(2, '02 — Foundations')
f_fnd = add_frame(p2, 'Foundations & Design Tokens', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f_fnd, 'Fnd Title', 80, 60, 'Design Foundations — Color, Typography & Spatial Grid', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_fnd, 'Fnd Sub', 80, 102, 'Sistem token desain resmi PMB 2026 yang menjadi acuan konsistensi seluruh antarmuka.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Color Palette Grid (11 Swatches)
add_text(f_fnd, 'Pal Header', 80, 150, 'COLOR PALETTE (STRICT TOKENS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

colors_list = [
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
    ('Warning Yellow', '#F2BF55', C_PRIMARY_TEXT)
]

cx = 80
cy = 180
for i, (cname, chex, ctxt) in enumerate(colors_list):
    add_rect(f_fnd, f'Sw BG {cname}', cx, cy, 105, 110, fill_hex=chex, stroke_hex=C_BORDER, radius=12)
    add_text(f_fnd, f'Sw Name {cname}', cx + 8, cy + 68, cname, font_size=10, color_hex=ctxt, font_weight='Bold')
    add_text(f_fnd, f'Sw Hex {cname}', cx + 8, cy + 86, chex, font_size=11, color_hex=ctxt)
    cx += 116
    if (i + 1) % 6 == 0:
        cx = 80
        cy += 125

# Typography Hierarchy
add_text(f_fnd, 'Typo Header', 80, 460, 'TYPOGRAPHY HIERARCHY (PLUS JAKARTA SANS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

type_scales = [
    ('Hero Title (52px Bold)', 'Gerbang Menuju Perguruan Tinggi Impian Anda', 52, 'Bold'),
    ('Page Title (40px Bold)', 'Formulir Pendaftaran Siswa & Verifikasi Dokumen', 40, 'Bold'),
    ('Section Title (32px Bold)', 'Pilihan Jalur Masuk Seleksi Akademik 2026', 32, 'Bold'),
    ('Card Title (18px Semibold)', 'S1 Teknik Informatika — Akreditasi Unggul', 18, 'Bold'),
    ('Body Text (15px Regular)', 'Wujudkan impian studi di perguruan tinggi dengan proses pendaftaran digital yang terstruktur, transparan, dan terpercaya.', 15, 'Regular'),
    ('Label / Caption (12px Medium)', 'NOMOR INDUK KEPENDUDUKAN (NIK) SESUAI KARTU KELUARGA *', 12, 'Bold')
]
ty = 495
for tscale, tex, tsz, twg in type_scales:
    add_text(f_fnd, f'TLbl {tscale}', 80, ty, tscale, font_size=11, color_hex=C_SECONDARY_TEXT)
    add_text(f_fnd, f'TEx {tscale}', 320, ty, tex, font_size=tsz, color_hex=C_PRIMARY_TEXT, font_weight=twg)
    ty += int(tsz * 1.5) + 12

# Spacing System Ladder
add_text(f_fnd, 'Spc Header', 80, 890, 'SPACING SYSTEM (4px GRID LADDER)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
spacers = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80]
spx = 80
for sp in spacers:
    add_rect(f_fnd, f'SpcBox {sp}', spx, 920, sp, sp, fill_hex=C_PRIMARY, radius=2)
    add_text(f_fnd, f'SpcTxt {sp}', spx, 920 + sp + 8, f'{sp}px', font_size=10, color_hex=C_SECONDARY_TEXT)
    spx += max(sp + 14, 38)

# ==========================================
# PAGE 3: 03 — Design System
# ==========================================
p3 = add_page(3, '03 — Design System')
f_sys = add_frame(p3, 'Component Library & Variants', 0, 0, 1440, 1024, C_BACKGROUND)

add_text(f_sys, 'Sys Title', 80, 60, 'Core Component System & Interaction Variants', font_size=32, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_sys, 'Sys Sub', 80, 102, 'Pustaka komponen antarmuka pill-shaped, input form, status badges, dan kartu data.', font_size=15, color_hex=C_SECONDARY_TEXT)

# Component Section 1: Buttons
add_text(f_sys, 'Btn Header', 80, 150, '1. BUTTON COMPONENTS (PILL SHAPED)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Primary Pill Buttons
add_rect(f_sys, 'Btn Prim Default', 80, 180, 200, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f_sys, 'Btn Prim Def Txt', 125, 195, 'Primary Default', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f_sys, 'Btn Prim Hover', 300, 180, 200, 48, fill_hex=C_PRIMARY_HOVER, radius=24)
add_text(f_sys, 'Btn Prim Hov Txt', 345, 195, 'Primary Hover', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f_sys, 'Btn Sec Default', 520, 180, 200, 48, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=24)
add_text(f_sys, 'Btn Sec Def Txt', 565, 195, 'Secondary Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_rect(f_sys, 'Btn Amber Accent', 740, 180, 200, 48, fill_hex=C_WARNING, radius=24)
add_text(f_sys, 'Btn Amber Txt', 785, 195, 'Amber CTA Pill', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_rect(f_sys, 'Btn Ghost', 960, 180, 160, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_text(f_sys, 'Btn Ghost Txt', 1005, 195, 'Ghost Pill', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f_sys, 'Btn Disabled', 1140, 180, 160, 48, fill_hex='#e2e8f0', radius=24)
add_text(f_sys, 'Btn Dis Txt', 1180, 195, 'Disabled Pill', font_size=13, color_hex='#94a3b8', font_weight='Bold')

# Component Section 2: Input Fields
add_text(f_sys, 'Inp Header', 80, 260, '2. FORM INPUT COMPONENTS (14-20px RADIUS)', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_sys, 'Inp 1 Lbl', 80, 290, 'Alamat Email Siswa (Default) *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_sys, 'Inp 1 Box', 80, 312, 380, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=10)
add_text(f_sys, 'Inp 1 Val', 96, 326, 'irfan@mail.com', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f_sys, 'Inp 2 Lbl', 500, 290, 'Nomor Induk Siswa Nasional (Focus) *', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f_sys, 'Inp 2 Box', 500, 312, 380, 46, fill_hex=C_SURFACE, stroke_hex=C_PRIMARY, stroke_width=2.0, radius=10)
add_text(f_sys, 'Inp 2 Val', 516, 326, '0058291042', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f_sys, 'Inp 3 Lbl', 920, 290, 'Konfirmasi Kata Sandi (Error) *', font_size=12, color_hex='#be123c', font_weight='Bold')
add_rect(f_sys, 'Inp 3 Box', 920, 312, 380, 46, fill_hex='#fff1f2', stroke_hex='#fecdd3', stroke_width=1.5, radius=10)
add_text(f_sys, 'Inp 3 Val', 936, 326, 'Kata sandi tidak cocok!', font_size=13, color_hex='#be123c')

# Component Section 3: Status Pills & Badges
add_text(f_sys, 'Badge Header', 80, 390, '3. STATUS PILLS & BADGES', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

badges = [
    ('TERVERIFIKASI', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('MENUNGGU VERIFIKASI', '#fef3c7', '#fde68a', '#b45309'),
    ('PERLU REVISI', '#fff1f2', '#fecdd3', '#be123c'),
    ('LULUS SELEKSI', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('DRAFT TERSIMPAN', '#f1f5f9', '#e2e8f0', '#64748b'),
    ('JALUR SNBP DIBUKA', '#f0f9ff', '#bae6fd', C_PRIMARY)
]
bx = 80
for btxt, bbg, bbrd, bcol in badges:
    bw = len(btxt) * 8 + 36
    add_rect(f_sys, f'Bdg {btxt}', bx, 420, bw, 32, fill_hex=bbg, stroke_hex=bbrd, radius=16)
    add_text(f_sys, f'BdgTxt {btxt}', bx + 18, 428, btxt, font_size=11, color_hex=bcol, font_weight='Bold')
    bx += bw + 16

# Component Section 4: Stepper Nodes
add_text(f_sys, 'Step Header', 80, 490, '4. STEP WIZARD NODES & PROGRESS CONNECTOR', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
step_samples = [
    ('1', 'Biodata Diri', 'Completed', C_SUCCESS),
    ('2', 'Asal Sekolah', 'Active', C_PRIMARY),
    ('3', 'Pilihan Prodi', 'Upcoming', '#63718A'),
    ('4', 'Unggah Berkas', 'Upcoming', '#63718A'),
    ('5', 'Finalisasi', 'Upcoming', '#63718A')
]
stx = 80
for snum, stitle, sstate, scol in step_samples:
    sbg = scol if sstate in ['Completed', 'Active'] else '#EEF2FA'
    stxt = C_SURFACE if sstate in ['Completed', 'Active'] else '#63718A'
    add_rect(f_sys, f'SN Node {snum}', stx, 525, 44, 44, fill_hex=sbg, radius=22)
    add_text(f_sys, f'SN Num {snum}', stx + 16, 537, snum, font_size=14, color_hex=stxt, font_weight='Bold')
    add_text(f_sys, f'SN Title {snum}', stx + 56, 532, stitle, font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold' if sstate=='Active' else 'Regular')
    add_text(f_sys, f'SN State {snum}', stx + 56, 552, sstate, font_size=11, color_hex=scol)
    
    if int(snum) < 5:
        add_rect(f_sys, f'SN Line {snum}', stx + 175, 545, 60, 2, fill_hex=C_BORDER)
    stx += 250

# Component Section 5: Card Containers
add_text(f_sys, 'Card Header', 80, 615, '5. CARD CONTAINERS WITH 16PX RADIUS & SOFT SHADOWS', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')

# Card 1: Standard White
add_rect(f_sys, 'C1 Surface', 80, 645, 380, 320, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f_sys, 'C1 T', 108, 675, 'Surface Container', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_sys, 'C1 D', 108, 705, 'Warna latar #FFFFFF dengan border hairline #DFE6F2. Digunakan untuk modul form dan tabel data.', font_size=13, color_hex=C_SECONDARY_TEXT, width=320, height=50)
add_rect(f_sys, 'C1 Pill Btn', 108, 890, 160, 40, fill_hex=C_PRIMARY, radius=20)
add_text(f_sys, 'C1 Btn T', 145, 902, 'Pill Button', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

# Card 2: Muted Blue Surface
add_rect(f_sys, 'C2 Muted', 500, 645, 380, 320, fill_hex=C_MUTED_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f_sys, 'C2 T', 528, 675, 'Muted Blue Surface', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_sys, 'C2 D', 528, 705, 'Warna latar #EEF2FA untuk mengelompokkan area sekunder, catatan info penting, atau panel bantuan.', font_size=13, color_hex=C_SECONDARY_TEXT, width=320, height=50)

# Card 3: Primary Dark Identity
add_rect(f_sys, 'C3 Dark', 920, 645, 380, 320, fill_hex=C_PRIMARY, radius=16)
add_text(f_sys, 'C3 T', 948, 675, 'Primary Blue Identity', font_size=18, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_sys, 'C3 D', 948, 705, 'Warna identitas #1554B8 untuk banner utama, kop universitas, dan penanda brand primer.', font_size=13, color_hex=C_MUTED_SURFACE, width=320, height=50)

# ==========================================
# PAGE 4: 04 — Public Website (1440 × 1024, Margins: 80px)
# ==========================================
p4 = add_page(4, '04 — Public Website')
f_pub = add_frame(p4, 'Desktop — 01. Beranda Portal PMB', 0, 0, 1440, 1024, C_BACKGROUND)

# Top Bar (Exact 80px Margins)
add_rect(f_pub, 'P4 Top Strip', 0, 0, 1440, 36, fill_hex=C_PRIMARY)
add_text(f_pub, 'P4 Top L', 80, 10, 'Call Center: (024) 8508093   |   Email: pmb@mail.unnes.ac.id   |   Gedung Rektorat Kampus Sekaran', font_size=11, color_hex=C_MUTED_SURFACE)
add_text(f_pub, 'P4 Top R', 1020, 10, 'Jadwal Seleksi TA 2026/2027   |   Buku Panduan PMB (PDF)', font_size=11, color_hex=C_MUTED_SURFACE)

# Main Navbar
add_rect(f_pub, 'P4 Nav BG', 0, 36, 1440, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_rect(f_pub, 'P4 Brand Badge', 80, 52, 44, 44, fill_hex=C_PRIMARY, radius=10)
add_text(f_pub, 'P4 Brand Badge Txt', 92, 64, 'UN', font_size=16, color_hex=C_SURFACE, font_weight='Bold')

add_text(f_pub, 'P4 Brand Name', 136, 53, 'PMB UNNES 2026', font_size=19, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_pub, 'P4 Brand Sub', 136, 76, 'Penerimaan Mahasiswa Baru Universitas Negeri Semarang', font_size=12, color_hex=C_SECONDARY_TEXT)

p4_navs = ['Beranda', 'Jalur Masuk', 'Program Studi', 'Biaya Kuliah', 'Pengumuman', 'Kontak']
p4_nx = 620
for nv in p4_navs:
    add_text(f_pub, f'P4 Nav {nv}', p4_nx, 66, nv, font_size=13, color_hex=C_SECONDARY_TEXT)
    p4_nx += 105

# Pill Shaped Action Button
add_rect(f_pub, 'P4 Btn Login', 1210, 53, 150, 44, fill_hex=C_PRIMARY, radius=22)
add_text(f_pub, 'P4 Btn Login Txt', 1245, 65, 'Masuk / Daftar', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Hero Section (Width: 1280px, Margins: 80px, Height: 410px)
add_image_rect(f_pub, 'P4 Hero Photo BG', 80, 132, 1280, 410, 'hero_campus.jpg', radius=18)
add_rect(f_pub, 'P4 Hero Overlay', 80, 132, 1280, 410, fill_hex=C_PRIMARY, opacity=0.84, radius=18)

add_rect(f_pub, 'P4 Hero Tag', 115, 165, 305, 26, fill_hex=C_SURFACE, opacity=0.2, radius=13)
add_text(f_pub, 'P4 Hero Tag Txt', 130, 171, 'PENDAFTARAN MAHASISWA BARU TA 2026/2027', font_size=10, color_hex=C_SURFACE, font_weight='Bold')

add_text(f_pub, 'P4 Hero Title 1', 115, 205, 'Selamat Datang di Portal PMB', font_size=36, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_pub, 'P4 Hero Title 2', 115, 252, 'Universitas Negeri Semarang', font_size=36, color_hex=C_WARNING, font_weight='Bold')

add_text(f_pub, 'P4 Hero Lead 1', 115, 312, 'Wujudkan impian studi di Kampus Konservasi Bereputasi Internasional.', font_size=15, color_hex='#e0f2fe')
add_text(f_pub, 'P4 Hero Lead 2', 115, 336, 'Sistem seleksi digital terpadu, verifikasi berkas cepat, dan notifikasi real-time.', font_size=15, color_hex='#e0f2fe')

# Pill Buttons
add_rect(f_pub, 'P4 Hero Btn 1', 115, 385, 210, 48, fill_hex=C_WARNING, radius=24)
add_text(f_pub, 'P4 Hero Btn 1 Txt', 142, 400, 'Daftar Akun Baru Siswa →', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_rect(f_pub, 'P4 Hero Btn 2', 340, 385, 210, 48, fill_hex=C_SURFACE, stroke_hex='#cbd5e1', radius=24)
add_text(f_pub, 'P4 Hero Btn 2 Txt', 372, 400, 'Panduan Pendaftaran', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

# Cutout Student Card on Right
add_image_rect(f_pub, 'P4 Student Cutout', 760, 160, 250, 340, 'student_hero.png', radius=16)

# Floating Telemetry Card
add_rect(f_pub, 'P4 Stat Card', 1030, 180, 290, 240, fill_hex=C_SURFACE, radius=16)
add_text(f_pub, 'P4 Stat Title', 1055, 204, 'Statistik Seleksi Aktif', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_pub, 'P4 Stat Div', 1055, 230, 240, 1, fill_hex=C_BORDER)

add_text(f_pub, 'P4 Stat 1 Lbl', 1055, 244, 'Total Pendaftar Terverifikasi:', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f_pub, 'P4 Stat 1 Val', 1055, 262, '1,428 Siswa', font_size=20, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_pub, 'P4 Stat 2 Lbl', 1055, 295, 'Pilihan Program Studi:', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f_pub, 'P4 Stat 2 Val', 1055, 313, '72 Prodi (Akreditasi Unggul)', font_size=14, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

add_rect(f_pub, 'P4 Status Pill', 1055, 350, 240, 34, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f_pub, 'P4 Status Pill Txt', 1072, 359, 'Status Sistem: ONLINE • Pendaftaran Aktif', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')

# 3 Jalur Masuk Feature Cards (Width 1280px total)
add_text(f_pub, 'P4 Sec Title', 80, 565, 'PILIHAN JALUR SELEKSI PMB 2026', font_size=24, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_pub, 'P4 Sec Sub', 80, 595, 'Pilih Jalur Masuk Sesuai Kualifikasi & Prestasi Akademik Anda', font_size=14, color_hex=C_SECONDARY_TEXT)

p4_cards = [
    ('card_snbp.jpg', 'SNBP (Jalur Prestasi Nasional)', 'Seleksi nasional berdasarkan prestasi nilai rapor semester 1-5 dan portofolio kejuaraan.', 'Jadwal: 10 Nov - 20 Des 2026', 'Bebas Biaya Pendaftaran', 80),
    ('card_snbt.jpg', 'SNBT (Jalur UTBK Nasional)', 'Seleksi nasional berbasis tes skolastik dan literasi terstandar yang diselenggarakan BPPP.', 'Jadwal: 15 Jan - 28 Feb 2027', 'Biaya Tes: Rp 200.000', 520),
    ('card_mandiri.jpg', 'SM-UNNES (Jalur Mandiri)', 'Seleksi mandiri perguruan tinggi berbasis ujian CBT terpadu UNNES dan prestasi unggul.', 'Jadwal: 01 Mar - 15 Apr 2027', 'Biaya Ujian: Rp 300.000', 960)
]
for pimg, ptitle, pdesc, pdate, pcost, px in p4_cards:
    add_rect(f_pub, f'P4 JCard {ptitle} BG', px, 630, 400, 315, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
    add_image_rect(f_pub, f'P4 JCard {ptitle} Img', px, 630, 400, 130, pimg, radius=[16, 16, 0, 0])
    
    add_text(f_pub, f'P4 JCard {ptitle} T', px + 20, 775, ptitle, font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f_pub, f'P4 JCard {ptitle} D', px + 20, 798, pdesc, font_size=11, color_hex=C_SECONDARY_TEXT, width=360, height=34)
    
    add_text(f_pub, f'P4 JCard {ptitle} Date', px + 20, 842, pdate, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f_pub, f'P4 JCard {ptitle} Cost', px + 20, 860, pcost, font_size=10, color_hex=C_SECONDARY_TEXT)
    
    add_rect(f_pub, f'P4 JCard {ptitle} Btn', px + 20, 888, 360, 38, fill_hex=C_MUTED_SURFACE, stroke_hex='#bae6fd', radius=19)
    add_text(f_pub, f'P4 JCard {ptitle} BtnTxt', px + 115, 899, 'Lihat Informasi Selengkapnya →', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

# Footer
add_rect(f_pub, 'P4 Footer', 0, 960, 1440, 64, fill_hex=C_PRIMARY)
add_text(f_pub, 'P4 Footer Txt', 80, 985, '© 2026 Universitas Negeri Semarang — Panitia Penerimaan Mahasiswa Baru. Seluruh hak cipta dilindungi undang-undang.', font_size=11, color_hex=C_SURFACE)

# ==========================================
# PAGE 7: 07 — Authentication (Split Wallpaper Library)
# ==========================================
p7 = add_page(7, '07 — Authentication')
f_auth = add_frame(p7, 'Desktop — 04. Login & Registrasi Akun', 0, 0, 1440, 1024, C_BACKGROUND)

# Left Side: Library Wall Photo with Dark Blue Overlay
add_image_rect(f_auth, 'P7 Lib Wall', 80, 60, 580, 900, 'library_bg.jpg', radius=20)
add_rect(f_auth, 'P7 Lib Overlay', 80, 60, 580, 900, fill_hex=C_PRIMARY_TEXT, opacity=0.76, radius=20)

# Frosted Glass Information Box
add_rect(f_auth, 'P7 Glass Box', 110, 90, 520, 840, fill_hex=C_SURFACE, stroke_hex='#ffffff35', radius=16, opacity=0.15)
add_text(f_auth, 'P7 Brand', 140, 120, 'PMB UNNES 2026', font_size=20, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_auth, 'P7 Info Title', 140, 160, 'Pendaftaran Akun Baru Siswa', font_size=24, color_hex=C_SURFACE, font_weight='Bold')
add_text(f_auth, 'P7 Info Sub', 140, 195, 'Gunakan satu akun resmi untuk seluruh tahapan seleksi penerimaan mahasiswa baru di Universitas Negeri Semarang.', font_size=12, color_hex=C_MUTED_SURFACE, width=460, height=40)

steps_auth7 = [
    ('1', 'Registrasi Akun Siswa', 'Daftarkan email aktif dan 10 digit NISN valid terdaftar Dapodik.'),
    ('2', 'Lengkapi Biodata Diri', 'Isi data pribadi, keluarga, dan riwayat sekolah asal Anda.'),
    ('3', 'Pilih Jalur & Prodi', 'Tentukan jalur seleksi dan 2 program studi prioritas.'),
    ('4', 'Unggah Berkas Syarat', 'Upload file scan Ijazah/SKL, Kartu Keluarga, dan Pas Foto.'),
    ('5', 'Finalisasi & Cetak Kartu', 'Verifikasi seluruh data dan terbitkan Kartu Peserta CBT.')
]
p7_sy = 250
for pnum, pstitle, psdesc in steps_auth7:
    add_rect(f_auth, f'P7 SBox {pnum}', 140, p7_sy, 460, 74, fill_hex=C_SURFACE, stroke_hex='#ffffff25', radius=10, opacity=0.12)
    add_rect(f_auth, f'P7 SNumBG {pnum}', 158, p7_sy + 17, 40, 40, fill_hex=C_PRIMARY, radius=20)
    add_text(f_auth, f'P7 SNum {pnum}', 174, p7_sy + 28, pnum, font_size=14, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f_auth, f'P7 STitle {pnum}', 212, p7_sy + 17, pstitle, font_size=13, color_hex=C_SURFACE, font_weight='Bold')
    add_text(f_auth, f'P7 SDesc {pnum}', 212, p7_sy + 39, psdesc, font_size=11, color_hex='#cbd5e1')
    p7_sy += 86

add_rect(f_auth, 'P7 Help Pill', 140, 860, 460, 44, fill_hex=C_PRIMARY_HOVER, radius=22)
add_text(f_auth, 'P7 Help Pill Txt', 185, 873, 'WhatsApp Helpdesk Admisi: 0812-3456-7890', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

# Right Side: Auth Form Container (w: 640px)
add_rect(f_auth, 'P7 Form BG', 680, 60, 680, 900, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=20)
add_text(f_auth, 'P7 Back Link', 720, 95, '← Kembali ke Beranda Portal', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

# Segmented Pill Switcher
add_rect(f_auth, 'P7 Tab Container', 720, 135, 600, 48, fill_hex=C_MUTED_SURFACE, radius=24)
add_rect(f_auth, 'P7 Tab 1 Active', 724, 139, 296, 40, fill_hex=C_SURFACE, radius=20)
add_text(f_auth, 'P7 Tab 1 Txt', 815, 151, 'Masuk ke Akun', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_auth, 'P7 Tab 2 Txt', 1105, 151, 'Daftar Akun Baru', font_size=13, color_hex=C_SECONDARY_TEXT)

add_text(f_auth, 'P7 Form Title', 720, 220, 'Masuk ke Akun PMB', font_size=26, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f_auth, 'P7 Form Sub', 720, 255, 'Masukkan email atau NISN dan kata sandi yang telah terdaftar.', font_size=13, color_hex=C_SECONDARY_TEXT)

# Input 1: Email / NISN
add_text(f_auth, 'P7 Lbl 1', 720, 305, 'Alamat Email atau NISN *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_auth, 'P7 Inp 1', 720, 330, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f_auth, 'P7 Inp 1 Val', 738, 345, 'irfan@mail.com atau 0058291042', font_size=13, color_hex=C_PRIMARY_TEXT)

# Input 2: Password
add_text(f_auth, 'P7 Lbl 2', 720, 405, 'Kata Sandi (Password) *', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f_auth, 'P7 Inp 2', 720, 430, 600, 48, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f_auth, 'P7 Inp 2 Val', 738, 445, '••••••••••••••••', font_size=13, color_hex=C_PRIMARY_TEXT)

add_text(f_auth, 'P7 Remember', 720, 498, '[X] Ingat Sesi Saya di Perangkat Ini', font_size=12, color_hex=C_SECONDARY_TEXT)
add_text(f_auth, 'P7 Forgot', 1210, 498, 'Lupa Password?', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

# Pill Submit Button
add_rect(f_auth, 'P7 Submit Btn', 720, 540, 600, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f_auth, 'P7 Submit Btn Txt', 960, 556, 'Masuk Sekarang →', font_size=14, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f_auth, 'P7 Div Line', 720, 630, 600, 1, fill_hex=C_BORDER)

# Registration Promo Box
add_rect(f_auth, 'P7 Reg Box', 720, 660, 600, 140, fill_hex='#f0f9ff', stroke_hex='#bae6fd', radius=14)
add_text(f_auth, 'P7 Reg T', 748, 682, 'Belum memiliki akun pendaftaran PMB?', font_size=14, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f_auth, 'P7 Reg D', 748, 706, 'Daftarkan diri Anda sekarang menggunakan NISN yang terdaftar resmi di Dapodik.', font_size=12, color_hex=C_SECONDARY_TEXT)

add_rect(f_auth, 'P7 Reg Btn', 748, 735, 544, 42, fill_hex=C_SURFACE, stroke_hex=C_PRIMARY, radius=21)
add_text(f_auth, 'P7 Reg Btn Txt', 915, 747, 'Registrasi Akun Baru Siswa (Gratis)', font_size=12, color_hex=C_PRIMARY, font_weight='Bold')

add_text(f_auth, 'P7 Sec Disclaimer', 720, 835, 'Keamanan Terjamin: Transmisi data dilindungi enkripsi SSL 256-bit dan mematuhi UU PDP.', font_size=11, color_hex=C_SECONDARY_TEXT)

# ==========================================
# PAGE 8: 08 — Applicant Portal
# ==========================================
p8 = add_page(8, '08 — Applicant Portal')

# Frame 1: Multi-Step Registration Form
f8_reg = add_frame(p8, 'Desktop — 05. Formulir Pendaftaran Multi-Step (Biodata)', 0, 0, 1440, 1024, C_BACKGROUND)

# Top Bar
add_rect(f8_reg, 'F8R Nav BG', 0, 0, 1440, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8_reg, 'F8R Brand', 80, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_reg, 'F8R Title', 250, 24, 'Formulir Pendaftaran Siswa Baru — Jalur Mandiri Prestasi Unggul', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f8_reg, 'F8R Draft Badge', 1010, 18, 90, 28, fill_hex=C_MUTED_SURFACE, stroke_hex=C_BORDER, radius=14)
add_text(f8_reg, 'F8R Draft Badge Txt', 1032, 24, 'DRAFT', font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f8_reg, 'F8R User', 1115, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_PRIMARY_TEXT)

# Stepper with Connected Circles
add_rect(f8_reg, 'F8R Stepper BG', 80, 88, 1280, 76, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
steps_w8 = [
    ('1', 'Biodata Diri', True),
    ('2', 'Asal Sekolah', False),
    ('3', 'Pilihan Prodi', False),
    ('4', 'Unggah Berkas', False),
    ('5', 'Finalisasi', False)
]
w8x = 110
for i, (wn, wt, wa) in enumerate(steps_w8):
    c_bg = C_PRIMARY if wa else C_MUTED_SURFACE
    c_txt = C_SURFACE if wa else C_SECONDARY_TEXT
    add_rect(f8_reg, f'F8R SCircle {wn}', w8x, 106, 40, 40, fill_hex=c_bg, radius=20)
    add_text(f8_reg, f'F8R SNum {wn}', w8x + 15, 117, wn, font_size=13, color_hex=c_txt, font_weight='Bold')
    add_text(f8_reg, f'F8R STxt {wn}', w8x + 50, 117, wt, font_size=13, color_hex=C_PRIMARY_TEXT if wa else C_SECONDARY_TEXT, font_weight='Bold' if wa else 'Regular')
    
    if i < 4:
        add_rect(f8_reg, f'F8R SLine {i}', w8x + 165, 125, 75, 2, fill_hex=C_BORDER)
    w8x += 250

# Form Box
add_rect(f8_reg, 'F8R Form BG', 80, 180, 1280, 760, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8_reg, 'F8R Form H', 112, 210, 'Langkah 1: Identitas & Biodata Pribadi Calon Mahasiswa', font_size=20, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_reg, 'F8R Form S', 112, 238, 'Pastikan seluruh data yang dimasukkan sesuai dengan Kartu Keluarga (KK) dan Ijazah asli Anda.', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f8_reg, 'F8R Form Div', 112, 265, 1216, 1, fill_hex=C_BORDER)

c1_f8 = [
    ('Nomor Induk Kependudukan (NIK) *', '3302192804040003 (16 digit sesuai KTP/KK)'),
    ('Nomor Induk Siswa Nasional (NISN) *', '0058291042 (10 digit terdaftar di Dapodik)'),
    ('Nama Lengkap Sesuai Ijazah *', 'Muhammad Irfan (Sesuai Ijazah Resmi)'),
    ('Jenis Kelamin *', 'Laki-laki (Pilihan)'),
    ('Tempat Lahir *', 'Kota Semarang'),
    ('Tanggal Lahir *', '14 / 08 / 2005 (DD/MM/YYYY)')
]
f8y = 285
for lbl, val in c1_f8:
    add_text(f8_reg, f'F8R Lbl {lbl}', 112, f8y, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f8_reg, f'F8R Inp {lbl}', 112, f8y + 20, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f8_reg, f'F8R Val {lbl}', 128, f8y + 32, val, font_size=12, color_hex=C_PRIMARY_TEXT)
    f8y += 82

c2_f8 = [
    ('Agama *', 'Islam (Pilihan)'),
    ('Nomor Handphone / WhatsApp Aktif *', '081234567890'),
    ('Alamat Lengkap Tempat Tinggal *', 'Jl. Sekaran Raya No. 42, RT 03 / RW 02'),
    ('Kelurahan / Desa *', 'Sekaran'),
    ('Kecamatan *', 'Gunungpati'),
    ('Kabupaten / Kota *', 'Kota Semarang, Jawa Tengah')
]
f8y2 = 285
for lbl, val in c2_f8:
    add_text(f8_reg, f'F8R Lbl {lbl}', 748, f8y2, lbl, font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_rect(f8_reg, f'F8R Inp {lbl}', 748, f8y2 + 20, 580, 42, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
    add_text(f8_reg, f'F8R Val {lbl}', 764, f8y2 + 32, val, font_size=12, color_hex=C_PRIMARY_TEXT)
    f8y2 += 82

add_rect(f8_reg, 'F8R Bottom Div', 112, 810, 1216, 1, fill_hex=C_BORDER)

add_rect(f8_reg, 'F8R Btn Draft', 112, 835, 180, 46, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=23)
add_text(f8_reg, 'F8R Btn Draft Txt', 152, 850, 'Simpan Draf', font_size=12, color_hex=C_SECONDARY_TEXT)

add_rect(f8_reg, 'F8R Btn Next', 1048, 835, 280, 46, fill_hex=C_PRIMARY, radius=23)
add_text(f8_reg, 'F8R Btn Next Txt', 1080, 850, 'Simpan & Lanjut ke Tahap 2 →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Frame 2: Upload & Kartu Peserta
f8_pass = add_frame(p8, 'Desktop — 06. Unggah Berkas & Kartu Peserta CBT', 1540, 0, 1440, 1024, C_BACKGROUND)

add_rect(f8_pass, 'F8P Nav BG', 0, 0, 1440, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8_pass, 'F8P Brand', 80, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_pass, 'F8P Sub', 250, 24, 'Unggah Dokumen Syarat & Penerbitan Kartu Tanda Peserta CBT', font_size=13, color_hex=C_SECONDARY_TEXT)

# Left Column: Upload Zones (w: 650)
add_rect(f8_pass, 'F8P Up BG', 80, 95, 650, 850, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8_pass, 'F8P Up Title', 112, 125, 'Langkah 4: Unggah Dokumen Persyaratan', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P Up Sub', 112, 152, 'Format yang didukung: PDF / JPG / PNG (Maksimal 2.0 MB per berkas).', font_size=12, color_hex=C_SECONDARY_TEXT)

up_docs8 = [
    ('1. Ijazah SMA / Surat Keterangan Lulus (SKL) *', 'ijazah_irfan_2026.pdf (1.2 MB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('2. Kartu Keluarga (KK) Legalisir *', 'kk_keluarga_irfan.pdf (890 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('3. Pas Foto Resmi 4x6 Background Merah *', 'foto_formal_4x6.jpg (450 KB)', 'Tersimpan di Supabase Storage • Siap diverifikasi'),
    ('4. Sertifikat Portofolio Prestasi Juara', 'sertifikat_osn_nasional.pdf (1.8 MB)', 'Tersimpan di Supabase Storage • Siap diverifikasi')
]
uy8 = 190
for dtitle, dfile, dnote in up_docs8:
    add_rect(f8_pass, f'F8P DRow {dtitle}', 112, uy8, 586, 92, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
    add_rect(f8_pass, f'F8P DIcon {dtitle}', 130, uy8 + 24, 44, 44, fill_hex=C_MUTED_SURFACE, radius=8)
    add_text(f8_pass, f'F8P DIconTxt {dtitle}', 140, uy8 + 36, 'DOC', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
    
    add_text(f8_pass, f'F8P DTitle {dtitle}', 188, uy8 + 16, dtitle, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f8_pass, f'F8P DFile {dtitle}', 188, uy8 + 38, dfile, font_size=11, color_hex=C_PRIMARY, font_weight='Bold')
    add_text(f8_pass, f'F8P DNote {dtitle}', 188, uy8 + 58, dnote, font_size=10, color_hex=C_SUCCESS)
    
    add_rect(f8_pass, f'F8P DBtn {dtitle}', 586, uy8 + 28, 96, 36, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=18)
    add_text(f8_pass, f'F8P DBtnTxt {dtitle}', 608, uy8 + 38, 'Ganti File', font_size=11, color_hex=C_SECONDARY_TEXT)
    uy8 += 108

# Integrity statement & Finalize button
add_rect(f8_pass, 'F8P Check Box', 112, 650, 586, 68, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f8_pass, 'F8P Check Txt 1', 134, 665, '[X]  Saya menyatakan bahwa semua berkas dan data yang saya unggah adalah asli dan sah.', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_pass, 'F8P Check Txt 2', 134, 687, 'Apabila ditemukan data palsu, saya bersedia menerima sanksi pembatalan kepesertaan PMB.', font_size=10, color_hex=C_SECONDARY_TEXT)

add_rect(f8_pass, 'F8P Final Btn', 112, 740, 586, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f8_pass, 'F8P Final Btn Txt', 240, 756, 'Finalisasi & Ajukan Pendaftaran Sekarang →', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Right Column: Official Kartu Peserta Ujian CBT (w: 600)
add_rect(f8_pass, 'F8P Pass BG', 760, 95, 600, 850, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)

# Kop Surat
add_rect(f8_pass, 'F8P Kop Header', 760, 95, 600, 90, fill_hex='#f0f9ff', radius=[16, 16, 0, 0])
add_text(f8_pass, 'F8P Kop 1', 790, 112, 'KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI', font_size=9, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P Kop 2', 790, 130, 'UNIVERSITAS NEGERI SEMARANG', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_pass, 'F8P Kop 3', 790, 154, 'KARTU TANDA PESERTA SELEKSI PMB 2026 — JALUR MANDIRI PRESTASI UNGGUL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f8_pass, 'F8P Kop Line', 790, 185, 540, 2, fill_hex=C_PRIMARY)

# Photo & Data
add_image_rect(f8_pass, 'F8P Photo', 790, 205, 120, 160, 'student_id_photo.jpg', radius=8)

p_labels8 = [
    ('Nomor Peserta PMB:', 'PMB-2026-08492'),
    ('Nama Lengkap Siswa:', 'MUHAMMAD IRFAN'),
    ('NISN / NIK:', '0058291042 / 3302192804040003'),
    ('Asal Sekolah:', 'SMA Negeri 1 Semarang'),
    ('Jalur Pendaftaran:', 'Seleksi Mandiri Prestasi Unggul')
]
py8 = 205
for plbl, pval in p_labels8:
    add_text(f8_pass, f'F8P PLbl {plbl}', 930, py8, plbl, font_size=10, color_hex=C_SECONDARY_TEXT)
    add_text(f8_pass, f'F8P PVal {plbl}', 930, py8 + 16, pval, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    py8 += 35

# Majors Choice
add_rect(f8_pass, 'F8P Prodi Box', 790, 385, 540, 85, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f8_pass, 'F8P Prodi Header', 806, 398, 'PROGRAM STUDI PILIHAN:', font_size=10, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P Prodi 1', 806, 418, '1. S1 Teknik Informatika (Fakultas Teknik) — Pilihan Utama', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P Prodi 2', 806, 440, '2. S1 Sistem Informasi (Fakultas Teknik) — Pilihan Cadangan', font_size=12, color_hex=C_SECONDARY_TEXT)

# CBT Exam Box
add_rect(f8_pass, 'F8P CBT Box', 790, 485, 540, 125, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=8)
add_text(f8_pass, 'F8P CBT Header', 806, 498, 'JADWAL & LOKASI UJIAN TERTULIS (CBT):', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_pass, 'F8P Hari Tgl', 806, 518, 'Hari / Tanggal  : Sabtu, 18 April 2026', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P Waktu Sesi', 806, 540, 'Waktu / Sesi   : Sesi 1 (Pagi) • Pukul 08.00 - 11.30 WIB', font_size=12, color_hex=C_PRIMARY_TEXT)
add_text(f8_pass, 'F8P Ruang Ujian', 806, 562, 'Ruang / Sektor : Gedung E10 Lt. 3, Lab Komputer 02 FMIPA UNNES', font_size=12, color_hex=C_PRIMARY_TEXT)
add_text(f8_pass, 'F8P Alamat CBT', 806, 584, 'Lokasi Kampus  : Kampus UNNES Sekaran, Gunungpati, Kota Semarang', font_size=11, color_hex=C_SUCCESS)

# QR Validation Box
add_rect(f8_pass, 'F8P QR Box', 790, 625, 110, 110, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f8_pass, 'F8P QR Dummy', 812, 670, '[ QR CODE ]', font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')

add_text(f8_pass, 'F8P QR Note 1', 920, 642, 'Validasi Keaslian Kartu Tanda Peserta:', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_pass, 'F8P QR Note 2', 920, 664, 'Pindai kode QR untuk validasi keaslian kartu peserta', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_pass, 'F8P QR Note 3', 920, 684, 'oleh petugas panitia pengawas di lokasi ujian.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_pass, 'F8P QR Note 4', 920, 706, 'Tanda tangan digital Admisi PMB: VALID (SHA-256 Verified)', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

# Pill Download Button
add_rect(f8_pass, 'F8P Btn Cetak', 790, 765, 540, 50, fill_hex=C_PRIMARY, radius=25)
add_text(f8_pass, 'F8P Btn Cetak Txt', 950, 780, 'Unduh Kartu Peserta (PDF) ↓', font_size=13, color_hex=C_SURFACE, font_weight='Bold')

# Frame 3: Dashboard Pendaftar & Web Push
f8_dash = add_frame(p8, 'Desktop — 07. Dashboard Pendaftar & Notifikasi Web Push', 3080, 0, 1440, 1024, C_BACKGROUND)

# Top Bar
add_rect(f8_dash, 'F8D Nav BG', 0, 0, 1440, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8_dash, 'F8D Brand', 80, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_dash, 'F8D Nav 1', 250, 24, 'Dashboard', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f8_dash, 'F8D Nav Ind', 250, 62, 65, 2, fill_hex=C_PRIMARY)
add_text(f8_dash, 'F8D Nav 2', 355, 24, 'Biodata Siswa', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D Nav 3', 475, 24, 'Status Dokumen', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D Nav 4', 605, 24, 'Jadwal CBT', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D Nav 5', 710, 24, 'Pusat Bantuan', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f8_dash, 'F8D Status Top Pill', 1040, 18, 175, 28, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=14)
add_text(f8_dash, 'F8D Status Top Txt', 1058, 24, 'MENUNGGU VERIFIKASI', font_size=10, color_hex='#b45309', font_weight='Bold')
add_text(f8_dash, 'F8D User Top Txt', 1235, 24, 'Muhammad Irfan (0058291042)', font_size=12, color_hex=C_PRIMARY_TEXT)

# Welcome Banner
add_rect(f8_dash, 'F8D Hero BG', 80, 88, 1280, 160, fill_hex=C_PRIMARY, radius=16)
add_rect(f8_dash, 'F8D Hero Tag', 112, 110, 260, 24, fill_hex=C_PRIMARY_HOVER, radius=12)
add_text(f8_dash, 'F8D Hero Tag Txt', 127, 115, 'PORTAL PENDAFTAR PMB TA 2026/2027', font_size=10, color_hex=C_SURFACE, font_weight='Bold')

add_text(f8_dash, 'F8D Hero Title', 112, 142, 'Selamat Datang Kembali, Muhammad Irfan!', font_size=24, color_hex=C_SURFACE, font_weight='Bold')
add_text(f8_dash, 'F8D Hero Sub', 112, 178, 'Pendaftaran Anda telah tercatat dengan Nomor: PMB-2026-08492 pada Program Studi S1 Teknik Informatika (Fakultas Teknik).', font_size=13, color_hex='#e0f2fe')
add_text(f8_dash, 'F8D Hero Meta', 112, 204, 'Jalur Seleksi: Mandiri Prestasi Unggul (SM-UNNES)   |   Status Berkas: Dalam Antrean Verifikasi Panitia', font_size=11, color_hex='#bae6fd')

# Web Push Notification Telemetry Card
add_rect(f8_dash, 'F8D Push Card BG', 80, 265, 1280, 90, fill_hex='#f0fdf4', stroke_hex='#86efac', radius=12)
add_rect(f8_dash, 'F8D Push Icon BG', 108, 286, 48, 48, fill_hex='#dcfce7', radius=24)
add_text(f8_dash, 'F8D Push Icon Txt', 121, 301, 'NOTIF', font_size=9, color_hex='#166534', font_weight='Bold')

add_text(f8_dash, 'F8D Push Title', 170, 286, 'Layanan Notifikasi Web Push Real-time Aktif', font_size=14, color_hex='#166534', font_weight='Bold')
add_text(f8_dash, 'F8D Push Desc', 170, 310, 'Browser Anda terhubung ke Service Worker VAPID. Anda akan menerima notifikasi otomatis saat ada pembaruan status verifikasi atau revisi.', font_size=11, color_hex=C_SUCCESS)

add_rect(f8_dash, 'F8D Push Pill', 990, 295, 130, 30, fill_hex=C_SURFACE, stroke_hex='#86efac', radius=15)
add_text(f8_dash, 'F8D Push Pill Txt', 1010, 302, '● Terhubung Aktif', font_size=10, color_hex='#166534', font_weight='Bold')

add_rect(f8_dash, 'F8D Push Test Btn', 1135, 290, 205, 40, fill_hex=C_SUCCESS, radius=20)
add_text(f8_dash, 'F8D Push Test Btn Txt', 1155, 302, 'Uji Coba Kirim Notifikasi Push →', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

# Left Column: Document Verification Status (w: 740, h: 560)
add_rect(f8_dash, 'F8D Left Card BG', 80, 375, 740, 560, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_text(f8_dash, 'F8D Left Title', 108, 400, 'Tahapan Seleksi & Dokumen Berkas', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_dash, 'F8D Left Sub', 108, 424, 'Perkembangan verifikasi berkas pendaftaran diperbarui langsung oleh panitia admisi.', font_size=11, color_hex=C_SECONDARY_TEXT)

# Stepper 5-Step Bar
dash_steps8 = [
    ('1. Biodata', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('2. Pilihan', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('3. Berkas', 'Selesai', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('4. Verifikasi', 'Diproses', '#fef3c7', '#fde68a', '#b45309'),
    ('5. Pengumuman', '20 Des 2026', C_BACKGROUND, C_BORDER, C_SECONDARY_TEXT)
]
dsx8 = 108
for stitle, ssub, sbg, sbrd, stxt in dash_steps8:
    add_rect(f8_dash, f'F8D DStep {stitle}', dsx8, 452, 130, 40, fill_hex=sbg, stroke_hex=sbrd, radius=8)
    add_text(f8_dash, f'F8D DStepTitle {stitle}', dsx8 + 12, 460, stitle, font_size=11, color_hex=stxt, font_weight='Bold')
    add_text(f8_dash, f'F8D DStepSub {stitle}', dsx8 + 12, 474, ssub, font_size=9, color_hex=stxt)
    dsx8 += 140

add_text(f8_dash, 'F8D Docs Title', 108, 515, 'Status 4 Dokumen Persyaratan yang Diunggah:', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')

dash_docs8 = [
    ('1. Ijazah SMA / Surat Keterangan Lulus (SKL)', 'ijazah_irfan_2026.pdf (1.2 MB) • Diunggah 10 Nov 2026', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('2. Kartu Keluarga (KK) Legalisir', 'kk_keluarga_irfan.pdf (890 KB) • Dalam proses peninjauan verifikator', 'MENUNGGU', '#fef3c7', '#fde68a', '#b45309'),
    ('3. Pas Foto Resmi 4x6 Background Merah', 'foto_formal_4x6.jpg (450 KB) • Resolusi sesuai standar kartu peserta', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46'),
    ('4. Sertifikat Prestasi / Portofolio Kejuaraan', 'sertifikat_osn_nasional.pdf (1.8 MB) • Juara 1 OSN Informatika Nasional', 'VALID', '#ecfdf5', '#a7f3d0', '#065f46')
]
ddy8 = 540
for dname, dmeta, dst, dbg, dbrd, dtxt in dash_docs8:
    row_bg = '#fffbeb' if 'MENUNGGU' in dst else C_BACKGROUND
    row_brd = '#fde68a' if 'MENUNGGU' in dst else C_BORDER
    add_rect(f8_dash, f'F8D DRow {dname}', 108, ddy8, 684, 68, fill_hex=row_bg, stroke_hex=row_brd, radius=10)
    add_text(f8_dash, f'F8D DRowName {dname}', 128, ddy8 + 16, dname, font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
    add_text(f8_dash, f'F8D DRowMeta {dname}', 128, ddy8 + 38, dmeta, font_size=10, color_hex=C_SECONDARY_TEXT)
    
    add_rect(f8_dash, f'F8D DRowBadge {dname}', 650, ddy8 + 20, 115, 26, fill_hex=dbg, stroke_hex=dbrd, radius=6)
    add_text(f8_dash, f'F8D DRowBadgeTxt {dname}', 672, ddy8 + 26, dst, font_size=10, color_hex=dtxt, font_weight='Bold')
    ddy8 += 76

# Right Column: CBT Info & Fast Actions (w: 520, h: 560)
add_rect(f8_dash, 'F8D Right Card BG', 840, 375, 520, 560, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_text(f8_dash, 'F8D Right Title', 868, 400, 'Jadwal Seleksi CBT & Kartu Peserta', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_dash, 'F8D Right Sub', 868, 424, 'Persiapkan diri Anda untuk pelaksanaan ujian tertulis di kampus UNNES.', font_size=11, color_hex=C_SECONDARY_TEXT)

add_rect(f8_dash, 'F8D CBT Box', 868, 452, 464, 170, fill_hex=C_BACKGROUND, stroke_hex='#cbd5e1', radius=10)
add_text(f8_dash, 'F8D CBT Tag', 890, 470, 'JALUR MANDIRI PRESTASI UNGGUL', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_dash, 'F8D CBT Date', 890, 492, 'Sabtu, 18 April 2026', font_size=18, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_dash, 'F8D CBT Time', 890, 522, 'Sesi 1 (Pagi) • Pukul 08.00 - 11.30 WIB (Hadir 30 menit sebelum)', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D CBT Room', 890, 544, 'Ruang: Gedung E10 Lantai 3, Lab Komputer 02 FMIPA', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D CBT Loc', 890, 566, 'Kampus UNNES Sekaran, Gunungpati, Kota Semarang', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D CBT Note', 890, 590, 'Wajib membawa Kartu Tanda Peserta & KTP/Kartu Pelajar asli.', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f8_dash, 'F8D DL Box', 868, 638, 464, 105, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=10)
add_text(f8_dash, 'F8D DL Title', 890, 654, 'Kartu Tanda Peserta CBT Siap Dicetak', font_size=12, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_dash, 'F8D DL Desc', 890, 676, 'Cetak pada kertas HVS A4 putih dan simpan baik-baik nomor ujian Anda.', font_size=10, color_hex='#166534')
add_rect(f8_dash, 'F8D DL Btn', 890, 698, 420, 36, fill_hex=C_SUCCESS, radius=18)
add_text(f8_dash, 'F8D DL Btn Txt', 1015, 709, 'Unduh Kartu Peserta (PDF) ↓', font_size=11, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f8_dash, 'F8D Help Box', 868, 760, 464, 95, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=10)
add_text(f8_dash, 'F8D Help Title', 890, 776, 'Pusat Layanan PMB UNNES', font_size=12, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_dash, 'F8D Help WA', 890, 798, 'WhatsApp Helpdesk: 0812-3456-7890 (08:00 - 16:00 WIB)', font_size=10, color_hex=C_SECONDARY_TEXT)
add_text(f8_dash, 'F8D Help Mail', 890, 818, 'Email Resmi: pmb@mail.unnes.ac.id  |  Call Center: (024) 8508093', font_size=10, color_hex=C_SECONDARY_TEXT)

# Frame 4: Detail Verifikasi Berkas & Validasi Panitia (Admin)
f8_ver = add_frame(p8, 'Desktop — 08. Detail Verifikasi Berkas & Validasi Panitia', 4620, 0, 1440, 1024, C_BACKGROUND)

# Top Bar
add_rect(f8_ver, 'F8V Nav BG', 0, 0, 1440, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8_ver, 'F8V Brand', 80, 22, 'PMB Admin Panel', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_ver, 'F8V Breadcrumb', 240, 24, 'Antrean Verifikasi  /  Pemeriksaan Dokumen: PMB-2026-08492 (Muhammad Irfan)', font_size=12, color_hex=C_SECONDARY_TEXT)

add_rect(f8_ver, 'F8V Back Btn', 1040, 16, 175, 34, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=17)
add_text(f8_ver, 'F8V Back Btn Txt', 1060, 25, '← Kembali ke Antrean', font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')
add_text(f8_ver, 'F8V Admin User', 1235, 24, 'Panitia Verifikator (Admisi)', font_size=12, color_hex=C_PRIMARY_TEXT)

# Summary Header Banner
add_rect(f8_ver, 'F8V Summary BG', 80, 88, 1280, 75, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=12)
add_text(f8_ver, 'F8V Student Name', 108, 102, 'Muhammad Irfan', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_ver, 'F8V Student Meta', 108, 128, 'No. Pendaftaran: PMB-2026-08492  |  NISN: 0058291042  |  NIK: 3302192804040003  |  Prodi: S1 Teknik Informatika (FT)  |  Jalur: Mandiri Prestasi', font_size=11, color_hex=C_SECONDARY_TEXT)

add_rect(f8_ver, 'F8V Status Pill Right', 1090, 108, 235, 34, fill_hex='#fef3c7', stroke_hex='#fde68a', radius=17)
add_text(f8_ver, 'F8V Status Pill Txt', 1110, 117, 'STATUS: MENUNGGU VERIFIKASI', font_size=10, color_hex='#b45309', font_weight='Bold')

# Left Viewer (w: 730)
add_rect(f8_ver, 'F8V Viewer BG', 80, 180, 730, 775, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)

tab_x8v = 100
dtabs8v = [
    ('Ijazah/SKL (Valid)', C_BACKGROUND, C_BORDER, C_SUCCESS, 140),
    ('Kartu Keluarga (Aktif)', C_PRIMARY, None, C_SURFACE, 160),
    ('Pas Foto 4x6 (Valid)', C_BACKGROUND, C_BORDER, C_SUCCESS, 135),
    ('Portofolio (Valid)', C_BACKGROUND, C_BORDER, C_SUCCESS, 135)
]
for dt, dbg, dbrd, dtxt, dw in dtabs8v:
    add_rect(f8_ver, f'F8V Tab {dt}', tab_x8v, 196, dw, 34, fill_hex=dbg, stroke_hex=dbrd, radius=17)
    add_text(f8_ver, f'F8V TabTxt {dt}', tab_x8v + 14, 205, dt, font_size=11, color_hex=dtxt, font_weight='Bold')
    tab_x8v += dw + 10

add_text(f8_ver, 'F8V Tool Info', 100, 244, 'File: kk_keluarga_irfan.pdf (890 KB) • Supabase Bucket: /berkas-pmb/kk_irfan.pdf', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_ver, 'F8V Tool Controls', 520, 244, '[ - ]  100%  [ + ]   |   [ Buka Tab Baru ]   [ Unduh Asli ]', font_size=11, color_hex=C_PRIMARY, font_weight='Bold')

add_rect(f8_ver, 'F8V Sheet BG', 100, 272, 690, 660, fill_hex=C_BACKGROUND, stroke_hex='#cbd5e1', radius=8)
add_text(f8_ver, 'F8V KK Kop', 124, 296, 'REPUBLIK INDONESIA — KARTU KELUARGA', font_size=15, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_ver, 'F8V KK No', 124, 320, 'Nomor KK: 3302192804040003', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_ver, 'F8V KK Addr', 124, 342, 'Alamat: Jl. Sekaran Raya No. 42, RT 03 / RW 02, Kel. Sekaran, Kec. Gunungpati, Kota Semarang', font_size=11, color_hex=C_SECONDARY_TEXT)

# Defect Box
add_rect(f8_ver, 'F8V Defect BG', 124, 500, 642, 215, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=10)
add_text(f8_ver, 'F8V Defect Title', 144, 520, 'CATATAN TEMUAN VERIFIKATOR PADA DOKUMEN INI', font_size=12, color_hex='#be123c', font_weight='Bold')
add_text(f8_ver, 'F8V Defect 1', 144, 548, '• Stempel legalisir kelurahan/kecamatan buram dan tidak terbaca jelas.', font_size=11, color_hex='#9f1239')
add_text(f8_ver, 'F8V Defect 2', 144, 574, '• Barcode dinas kependudukan di pojok bawah dokumen terpotong saat scan scanner.', font_size=11, color_hex='#9f1239')
add_text(f8_ver, 'F8V Defect 3', 144, 600, '• Rekomendasi Verifikator: Wajib meminta pendaftar mengunggah ulang scan KK asli yang jelas.', font_size=11, color_hex='#be123c', font_weight='Bold')
add_text(f8_ver, 'F8V Defect 4', 144, 626, '• Batas Waktu Revisi: 20 Desember 2026 pukul 23:59 WIB sebelum finalisasi seleksi.', font_size=10, color_hex='#881337')
add_text(f8_ver, 'F8V Defect 5', 144, 650, '• Dampak jika tidak direvisi: Pendaftaran dapat dibatalkan atau gugur seleksi administrasi.', font_size=10, color_hex='#9f1239')

# Right Decision Form (w: 520)
add_rect(f8_ver, 'F8V Right BG', 840, 180, 520, 775, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=14)
add_text(f8_ver, 'F8V Right Title', 868, 204, 'Formulir Keputusan Verifikasi Panitia', font_size=16, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_ver, 'F8V Right Sub', 868, 228, 'Tentukan keabsahan berkas dan kirimkan instruksi perbaikan ke calon mahasiswa.', font_size=11, color_hex=C_SECONDARY_TEXT)

# Checklist Box
add_rect(f8_ver, 'F8V Check Box', 868, 255, 464, 110, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f8_ver, 'F8V Check Title', 888, 270, 'Checklist Pemeriksaan Syarat Dokumen (KK):', font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_ver, 'F8V Check 1', 888, 294, '[X]  NIK siswa (3302192804040003) sesuai biodata Dapodik', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_ver, 'F8V Check 2', 888, 316, '[X]  Nama orang tua kandung terdaftar dalam susunan keluarga', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_ver, 'F8V Check 3', 888, 338, '[ ]  Keterbacaan stempel legalisir dan keutuhan barcode scan (GAGAL)', font_size=11, color_hex='#be123c', font_weight='Bold')

add_text(f8_ver, 'F8V Berkas Lbl', 868, 380, 'Status Dokumen Ini (Kartu Keluarga):', font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f8_ver, 'F8V Btn Valid', 868, 400, 135, 36, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=18)
add_text(f8_ver, 'F8V Btn Valid Txt', 910, 410, 'VALID', font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')

add_rect(f8_ver, 'F8V Btn Revisi', 1013, 400, 175, 36, fill_hex='#fff1f2', stroke_hex='#fecdd3', radius=18)
add_text(f8_ver, 'F8V Btn Revisi Txt', 1045, 410, 'PERLU REVISI', font_size=11, color_hex='#be123c', font_weight='Bold')

add_rect(f8_ver, 'F8V Btn Tolak', 1198, 400, 134, 36, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=18)
add_text(f8_ver, 'F8V Btn Tolak Txt', 1225, 410, 'TIDAK VALID', font_size=11, color_hex=C_SECONDARY_TEXT, font_weight='Bold')

# Catatan Revisi Textarea
add_text(f8_ver, 'F8V Catatan Lbl', 868, 452, 'Catatan Panitia / Instruksi Revisi (Wajib Diisi jika Perlu Revisi) *', font_size=11, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_rect(f8_ver, 'F8V Catatan Box', 868, 474, 464, 110, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=8)
add_text(f8_ver, 'F8V Catatan L1', 886, 490, 'Scan Kartu Keluarga pada bagian stempel kelurahan buram dan', font_size=11, color_hex=C_PRIMARY_TEXT)
add_text(f8_ver, 'F8V Catatan L2', 886, 510, 'barcode bagian bawah terpotong. Silakan unggah ulang scan KK asli', font_size=11, color_hex=C_PRIMARY_TEXT)
add_text(f8_ver, 'F8V Catatan L3', 886, 530, 'yang utuh, tajam, dan tidak terpotong sebelum 20 Desember 2026.', font_size=11, color_hex=C_PRIMARY_TEXT)

# Web Push Trigger Box (Technical Requirements #5)
add_rect(f8_ver, 'F8V Push Box', 868, 600, 464, 75, fill_hex='#f0fdf4', stroke_hex='#86efac', radius=10)
add_text(f8_ver, 'F8V Push Txt 1', 888, 616, '[X]  Kirim Notifikasi Web Push Instan ke Smartphone/Browser Siswa', font_size=11, color_hex='#166534', font_weight='Bold')
add_text(f8_ver, 'F8V Push Txt 2', 888, 638, 'Antrean BullMQ: `notification-queue` • Event: `STATUS_REVISI_BERKAS` via VAPID Web Push', font_size=10, color_hex=C_SUCCESS)

# Pill Submit Button
add_rect(f8_ver, 'F8V Submit Btn', 868, 695, 464, 50, fill_hex='#be123c', radius=25)
add_text(f8_ver, 'F8V Submit Txt', 960, 710, 'Simpan Keputusan Revisi & Kirim Web Push →', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f8_ver, 'F8V Cancel Btn', 868, 755, 464, 40, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=20)
add_text(f8_ver, 'F8V Cancel Txt', 1035, 767, 'Batal / Lewati Pendaftar Ini', font_size=12, color_hex=C_SECONDARY_TEXT)

# Frame 5: Pengumuman Kelulusan & Registrasi Ulang
f8_grad = add_frame(p8, 'Desktop — 09. Pengumuman Kelulusan & Registrasi Ulang', 6160, 0, 1440, 1024, C_BACKGROUND)

# Top Bar
add_rect(f8_grad, 'F8G Nav BG', 0, 0, 1440, 64, fill_hex=C_SURFACE, stroke_hex=C_BORDER)
add_text(f8_grad, 'F8G Brand', 80, 22, 'PMB UNNES 2026', font_size=16, color_hex=C_PRIMARY, font_weight='Bold')
add_text(f8_grad, 'F8G Nav 1', 250, 24, 'Hasil Kelulusan', font_size=13, color_hex=C_PRIMARY, font_weight='Bold')
add_rect(f8_grad, 'F8G Nav Ind', 250, 62, 90, 2, fill_hex=C_PRIMARY)
add_text(f8_grad, 'F8G Nav 2', 370, 24, 'Surat Keputusan', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f8_grad, 'F8G Nav 3', 505, 24, 'Registrasi Ulang', font_size=13, color_hex=C_SECONDARY_TEXT)
add_text(f8_grad, 'F8G Nav 4', 640, 24, 'Pembayaran UKT', font_size=13, color_hex=C_SECONDARY_TEXT)

add_rect(f8_grad, 'F8G Status Top Pill', 1100, 18, 140, 28, fill_hex='#ecfdf5', stroke_hex='#a7f3d0', radius=14)
add_text(f8_grad, 'F8G Status Top Txt', 1125, 24, 'LULUS SELEKSI', font_size=10, color_hex='#065f46', font_weight='Bold')
add_text(f8_grad, 'F8G User Top', 1260, 24, 'Muhammad Irfan', font_size=12, color_hex=C_PRIMARY_TEXT)

# Green Hero Announcement Banner
add_rect(f8_grad, 'F8G Hero BG', 80, 88, 1280, 175, fill_hex=C_SUCCESS, radius=16)
add_rect(f8_grad, 'F8G Tag Badge', 112, 110, 360, 24, fill_hex='#15803d', radius=12)
add_text(f8_grad, 'F8G Tag Badge Txt', 127, 115, 'PENGUMUMAN HASIL KELULUSAN AKHIR PMB TA 2026/2027', font_size=10, color_hex=C_SURFACE, font_weight='Bold')

add_text(f8_grad, 'F8G Hero Title', 112, 145, 'SELAMAT! ANDA DINYATAKAN LULUS SELEKSI', font_size=28, color_hex=C_SURFACE, font_weight='Bold')
add_text(f8_grad, 'F8G Hero Sub', 112, 182, 'Universitas Negeri Semarang mengucapkan selamat bergabung dengan keluarga besar sivitas akademika UNNES Kampus Konservasi.', font_size=13, color_hex='#d1fae5')
add_text(f8_grad, 'F8G Hero Reg', 112, 208, 'Nomor Peserta: PMB-2026-08492   •   Jalur Masuk: Seleksi Mandiri Prestasi Unggul (SM-UNNES Terpadu)', font_size=12, color_hex='#a7f3d0')

# Left Details (w: 620)
add_rect(f8_grad, 'F8G Left BG', 80, 280, 620, 650, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8_grad, 'F8G Left Title', 112, 305, '1. Rincian Penetapan Program Studi & Kelulusan', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_grad, 'F8G Left Sub', 112, 328, 'Data resmi berdasarkan Surat Keputusan Rektor UNNES tentang Penetapan Mahasiswa Baru 2026.', font_size=11, color_hex=C_SECONDARY_TEXT)

add_rect(f8_grad, 'F8G Left Div', 112, 350, 556, 1, fill_hex=C_BORDER)

student_details8 = [
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
sdy8 = 365
for slbl, sval in student_details8:
    add_text(f8_grad, f'F8G Lbl {slbl}', 112, sdy8, slbl, font_size=11, color_hex=C_SECONDARY_TEXT)
    txt_color = C_PRIMARY if 'Teknik' in sval or '4.500.000' in sval or 'Sah' in sval else C_PRIMARY_TEXT
    add_text(f8_grad, f'F8G Val {slbl}', 330, sdy8, sval, font_size=11, color_hex=txt_color, font_weight='Bold')
    add_rect(f8_grad, f'F8G Div {slbl}', 112, sdy8 + 18, 556, 1, fill_hex='#f1f5f9')
    sdy8 += 35

# Pill Download SKL Button
add_rect(f8_grad, 'F8G SKL Btn', 112, 850, 556, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f8_grad, 'F8G SKL Btn Txt', 245, 865, 'Unduh Surat Keterangan Lulus (SKL) Resmi (PDF) ↓', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

# Right Re-registration Guide (w: 630)
add_rect(f8_grad, 'F8G Right BG', 730, 280, 630, 650, fill_hex=C_SURFACE, stroke_hex=C_BORDER, radius=16)
add_text(f8_grad, 'F8G Right Title', 762, 305, '2. Alur & Panduan Wajib Registrasi Ulang', font_size=17, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_grad, 'F8G Right Sub', 762, 328, 'Selesaikan 3 langkah registrasi ulang sebelum batas waktu agar hak kepesertaan tidak gugur.', font_size=11, color_hex=C_SECONDARY_TEXT)

add_rect(f8_grad, 'F8G Right Div', 762, 350, 566, 1, fill_hex=C_BORDER)

# Step 1: UKT
add_rect(f8_grad, 'F8G S1 BG', 762, 365, 566, 115, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=12)
add_text(f8_grad, 'F8G S1 Title', 784, 382, 'Langkah 1: Pembayaran Uang Kuliah Tunggal (UKT)', font_size=13, color_hex=C_SUCCESS, font_weight='Bold')
add_text(f8_grad, 'F8G S1 Desc', 784, 404, 'Lakukan pembayaran sebesar Rp 4.500.000 melalui Virtual Account BNI (9880-0058-2910-4200)', font_size=11, color_hex='#166534')
add_text(f8_grad, 'F8G S1 Desc 2', 784, 424, 'melalui ATM, Mobile Banking BNI, atau Teller Bank BNI terdekat di seluruh Indonesia.', font_size=11, color_hex='#166534')
add_text(f8_grad, 'F8G S1 Note', 784, 448, 'Tenggat Waktu: 25 Juli 2026, 15:00 WIB (Sistem otomatis memverifikasi pelunasan).', font_size=10, color_hex=C_SUCCESS, font_weight='Bold')

# Step 2: SIMREG Online
add_rect(f8_grad, 'F8G S2 BG', 762, 492, 566, 105, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=12)
add_text(f8_grad, 'F8G S2 Title', 784, 508, 'Langkah 2: Registrasi Online & Pengisian Ukuran Jas Almamater', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_grad, 'F8G S2 Desc', 784, 530, 'Isi data induk mahasiswa (SIMREG), riwayat kesehatan, dan ukuran jas almamater', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_grad, 'F8G S2 Desc 2', 784, 550, '(S / M / L / XL / XXL) melalui portal simreg.unnes.ac.id.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_grad, 'F8G S2 Status', 784, 572, '[ Terbuka otomatis setelah Pembayaran UKT Langkah 1 tervalidasi ]', font_size=10, color_hex=C_PRIMARY, font_weight='Bold')

# Step 3: Orientation
add_rect(f8_grad, 'F8G S3 BG', 762, 608, 566, 95, fill_hex=C_BACKGROUND, stroke_hex=C_BORDER, radius=12)
add_text(f8_grad, 'F8G S3 Title', 784, 624, 'Langkah 3: Pengambilan KTM & Orientasi Kampus (PKKMB)', font_size=13, color_hex=C_PRIMARY_TEXT, font_weight='Bold')
add_text(f8_grad, 'F8G S3 Desc', 784, 646, 'Pengambilan Kartu Tanda Mahasiswa (KTM) ATM BNI & Jas Almamater di GSG UNNES.', font_size=11, color_hex=C_SECONDARY_TEXT)
add_text(f8_grad, 'F8G S3 Desc 2', 784, 668, 'Jadwal PKKMB Universitas & Fakultas: 18 s.d. 20 Agustus 2026.', font_size=11, color_hex=C_SECONDARY_TEXT)

# Pill Actions
add_rect(f8_grad, 'F8G Reg Online Btn', 762, 715, 566, 48, fill_hex=C_PRIMARY, radius=24)
add_text(f8_grad, 'F8G Reg Online Btn Txt', 915, 730, 'Lanjut ke Portal Registrasi Online (SIMREG) →', font_size=12, color_hex=C_SURFACE, font_weight='Bold')

add_rect(f8_grad, 'F8G WA Group Btn', 762, 775, 566, 42, fill_hex='#f0fdf4', stroke_hex='#bbf7d0', radius=21)
add_text(f8_grad, 'F8G WA Group Btn Txt', 875, 788, 'Bergabung ke Komunitas WhatsApp Mahasiswa Baru Informatika 2026', font_size=11, color_hex=C_SUCCESS, font_weight='Bold')

# Save document.json
with open('C:/projects/ta-pemweb/uidesign/pmb-ui-concept.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, indent=2)

# Pack into pmb-ui-concept.figcraft zip directly with images!
zip_path = 'C:/projects/ta-pemweb/uidesign/pmb-ui-concept.figcraft'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('document.json', json.dumps(doc).encode('utf-8'))
    for fname, meta in images_meta.items():
        z.writestr(f'images/{meta["hash"]}', meta['bytes'])

print(f'Successfully compiled complete master Figma architecture into {zip_path} with {len(doc["nodes"])} nodes across {len(doc["pages"])} pages and {len(images_meta)} images!')
