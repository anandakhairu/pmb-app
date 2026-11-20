# ADMITRA (pmb-app)

Sistem informasi Penerimaan Mahasiswa Baru (PMB) berbasis web. Calon mahasiswa mendaftar, mengisi biodata, mengunggah berkas, dan melihat hasil seleksi. Panitia (admin) memverifikasi berkas dan menetapkan hasil.


## Teknologi

- Next.js (App Router) dengan JavaScript
- Tailwind CSS dan shadcn/ui
- Prisma ORM
- Supabase (database PostgreSQL, autentikasi, penyimpanan berkas)
- Deployment: Vercel

## Pengguna dan peran

| Pengguna | Area aplikasi | Fungsi utama |
|---|---|---|
| Calon mahasiswa (pendaftar) | `src/app/(mahasiswa)` | Biodata, unggah berkas, pantau status, lihat hasil seleksi |
| Admin (panitia) | `src/app/(admin)` | Analitik, antrean verifikasi berkas, master data |
| Publik | `src/app/(public)` | Landing page, login, register |

Tabel `admin` memiliki tiga level peran dengan hak akses berikut. Pemeriksaan peran dilakukan di sisi server pada setiap aksi yang mengubah data.

| Kemampuan | SUPER_ADMIN | VERIFIKATOR | PANITIA |
|---|---|---|---|
| Lihat dashboard analitik | ✓ | ✓ | ✓ |
| Lihat daftar pendaftar dan statusnya | ✓ | ✓ | ✓ |
| Buka dan lihat berkas pendaftar | ✓ | ✓ | lihat saja |
| Verifikasi berkas (ubah status, catatan revisi) | ✓ | ✓ | ✗ |
| Kirim notifikasi Web Push saat status berkas berubah | ✓ | ✓ | ✗ |
| Tetapkan hasil seleksi | ✓ | ✗ | ✓ |
| Kelola pengumuman dan jadwal | ✓ | ✗ | ✓ |
| Ekspor laporan | ✓ | ✗ | ✓ |
| Kelola master data (prodi, jalur, kuota) | ✓ | ✗ | ✗ |
| Kelola akun admin dan peran | ✓ | ✗ | ✗ |
| Pengaturan sistem | ✓ | ✗ | ✗ |

Prinsipnya: setiap peran hanya diberi akses yang dibutuhkan, dan yang memeriksa berkas dipisah dari yang menetapkan hasil seleksi.

## Cara menjalankan di komputer lokal

1. Clone repo dan masuk ke foldernya.
   ```bash
   git clone https://github.com/anandakhairu/pmb-app.git
   cd pmb-app
   ```
2. Pasang dependensi.
   ```bash
   npm install
   ```
3. Salin `.env.example` menjadi `.env`, lalu isi nilainya. Jangan commit file `.env`.

   | Variabel | Fungsi | Asal nilai |
   |---|---|---|
   | `DATABASE_URL` | Koneksi database saat aplikasi berjalan (transaction pooler, port 6543) | Supabase, connection string bagian Database |
   | `DIRECT_URL` | Koneksi untuk migrasi (session pooler, port 5432) | Supabase, connection string bagian Database |
   | `NEXT_PUBLIC_SUPABASE_URL` | Alamat proyek Supabase | Supabase, Project Settings > API |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Kunci publik untuk sisi browser | Supabase, Project Settings > API |
   | `SUPABASE_SERVICE_ROLE_KEY` | Kunci server dengan akses penuh. Rahasia, hanya dipakai di sisi server | Supabase, Project Settings > API |

   Ganti `PROJECT_REF`, `PASSWORD`, dan `REGION` pada contoh URL dengan nilai proyek Supabase tim. Minta nilai aslinya ke anggota tim yang mengelola Supabase.
4. Siapkan database. ** `prisma/constraints.sql`**
5. Jalankan server pengembangan.
   ```bash
   npm run dev
   ```
6. Buka `http://localhost:3000`.

## Struktur proyek

```
prisma/            Skema database, migrasi, dan constraint SQL
docs/ERD.md        Dokumentasi skema dan relasi tabel
src/app/           Halaman (route group: public, mahasiswa, admin)
src/components/    Komponen UI (landing, auth, mahasiswa, ui)
src/lib/           Utilitas dan data
```

## Alur kerja Git tim

1. `git checkout main` lalu `git pull origin main`.
2. Buat branch baru untuk tiap tugas: `git checkout -b feat/nama-tugas`.
3. Commit dan push ke branch tersebut.
4. Buka Pull Request ke `main`, lalu minta anggota lain meninjau sebelum merge.

## Status fitur

**Sudah selesai**
- Skema database dan constraint di level database.
- Landing page, halaman login dan register.
- Dashboard pendaftar: beranda dengan stepper status, biodata, unggah berkas, hasil seleksi.
- Deployment ke Vercel.
- dashboard admin, koneksi Supabase, akun pengujian

**Masih dalam pengerjaan atau keterbatasan**
- halaman pendaftar belum seluruhnya membaca data dari database
- unggah berkas ke storage belum tersambung
- status notifikasi Web Push dan background worker

## Anggota tim

| Nama | Bagian |
|---|---|
| Irfan  | Fondasi: skema database, setup, landing page, autentikasi |
|  Alya  | Dashboard pendaftar (mahasiswa) |
| Ananda | Dashboard admin |

## Dokumentasi tambahan
- Skema dan relasi tabel: `docs/ERD.md`
