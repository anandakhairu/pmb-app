# ERD dan Dokumentasi Skema Database

Sistem Penerimaan Mahasiswa Baru (PMB). Database: PostgreSQL (Supabase), diakses lewat Prisma.
Sumber kebenaran skema: `prisma/schema.prisma`. Constraint tambahan: `prisma/constraints.sql`.

Catatan: kolom `created_at` dan `updated_at` ada di setiap tabel tetapi tidak digambar agar diagram tetap terbaca.

## Diagram

```mermaid
erDiagram
    calon_mahasiswa ||--o| data_asal_sekolah : "punya (1-1)"
    calon_mahasiswa ||--o{ formulir_pendaftaran : "mengisi"
    program_studi ||--o{ formulir_pendaftaran : "dipilih pada"
    jalur_pendaftaran ||--o{ formulir_pendaftaran : "dipilih pada"
    jalur_pendaftaran ||--o{ jadwal_ujian_cbt : "memiliki"
    jadwal_ujian_cbt |o--o{ formulir_pendaftaran : "diikuti oleh"
    admin |o--o{ formulir_pendaftaran : "memverifikasi"
    admin |o--o{ formulir_pendaftaran : "menetapkan hasil"
    formulir_pendaftaran ||--o{ berkas_dokumen : "melampirkan"
    formulir_pendaftaran ||--o{ tagihan_pembayaran : "ditagih"
    calon_mahasiswa |o--o{ perangkat_notifikasi : "mendaftarkan"
    admin |o--o{ perangkat_notifikasi : "mendaftarkan"
    admin |o--o{ pengumuman : "menulis"

    calon_mahasiswa {
        uuid id PK
        uuid auth_user_id UK "ke Supabase Auth"
        varchar email UK
        varchar nama_lengkap
        char nik UK "16 digit"
        varchar tempat_lahir
        date tanggal_lahir
        jenis_kelamin jenis_kelamin
        varchar no_hp
        text alamat
        varchar kota_kabupaten
        varchar provinsi
    }

    data_asal_sekolah {
        uuid id PK
        uuid mahasiswa_id FK, UK
        varchar nama_sekolah
        varchar npsn "8 digit"
        varchar jenis_sekolah
        varchar jurusan
        smallint tahun_lulus
        decimal nilai_rata_rata "0 sampai 100"
        text alamat_sekolah
    }

    program_studi {
        uuid id PK
        varchar kode UK
        varchar nama
        varchar fakultas
        jenjang_prodi jenjang
        varchar akreditasi
        int kuota
        text deskripsi
        jsonb tarif_ukt "golongan dan biaya"
        boolean aktif
    }

    jalur_pendaftaran {
        uuid id PK
        varchar kode UK
        varchar nama
        text deskripsi
        text_array persyaratan
        boolean butuh_ujian_cbt
        decimal biaya_pendaftaran
        timestamptz tanggal_buka
        timestamptz tanggal_tutup
        timestamptz tanggal_pengumuman_hasil
        boolean aktif
    }

    formulir_pendaftaran {
        uuid id PK
        varchar nomor_pendaftaran UK "terbit saat finalisasi"
        varchar tahun_akademik "unik per mahasiswa"
        uuid mahasiswa_id FK
        uuid prodi_id FK
        uuid jalur_id FK
        uuid jadwal_ujian_id FK
        uuid verifikator_id FK
        uuid penetap_id FK
        smallint langkah_terakhir "1 sampai 4"
        status_berkas status_berkas
        status_kelulusan status_kelulusan
        text catatan_revisi
        text catatan_kelulusan
        timestamptz finalisasi_at
        timestamptz diverifikasi_at
        timestamptz ditetapkan_at
    }

    berkas_dokumen {
        uuid id PK
        uuid formulir_id FK
        jenis_dokumen jenis "unik per formulir"
        varchar nama_file
        varchar storage_path
        varchar mime_type
        int ukuran_byte "maks 5 MB"
        status_verifikasi_berkas status_verifikasi
        text catatan
    }

    jadwal_ujian_cbt {
        uuid id PK
        uuid jalur_id FK
        varchar nama
        date tanggal
        time jam_mulai
        time jam_selesai
        varchar lokasi
        int kapasitas
        text tautan_ujian
        boolean aktif
    }

    tagihan_pembayaran {
        uuid id PK
        uuid formulir_id FK
        varchar nomor_tagihan UK
        varchar deskripsi
        decimal nominal
        status_tagihan status
        varchar metode
        text bukti_bayar_url
        timestamptz jatuh_tempo
        timestamptz dibayar_at
    }

    admin {
        uuid id PK
        uuid auth_user_id UK "ke Supabase Auth"
        varchar email UK
        varchar nama
        role_admin role
        boolean aktif
    }

    perangkat_notifikasi {
        uuid id PK
        uuid mahasiswa_id FK "salah satu terisi"
        uuid admin_id FK "salah satu terisi"
        text endpoint UK
        text p256dh
        text auth_key
        text user_agent
        boolean aktif
        timestamptz terakhir_dipakai
    }

    pengumuman {
        uuid id PK
        uuid admin_id FK
        varchar judul
        varchar slug UK
        varchar ringkasan
        text isi
        boolean dipublikasikan
        timestamptz published_at
    }
```

## Fungsi tiap tabel

| Tabel | Fungsi |
|---|---|
| `calon_mahasiswa` | Profil pendaftar. Terhubung ke akun Supabase Auth lewat `auth_user_id`. |
| `data_asal_sekolah` | Data sekolah asal, relasi 1-1 dengan pendaftar. |
| `program_studi` | Master program studi, termasuk kuota dan tarif UKT per golongan (JSON). |
| `jalur_pendaftaran` | Master jalur: persyaratan, biaya, periode buka dan tutup, tanggal pengumuman hasil, serta penanda butuh ujian CBT. |
| `formulir_pendaftaran` | Transaksi inti. Menyimpan pilihan prodi dan jalur, status berkas, status kelulusan, catatan revisi, nomor pendaftaran, dan admin pemroses. |
| `berkas_dokumen` | Metadata berkas yang diunggah (file asli di Supabase Storage privat). |
| `jadwal_ujian_cbt` | Sesi ujian CBT per jalur. |
| `tagihan_pembayaran` | Tagihan biaya pendaftaran per formulir. |
| `admin` | Akun panitia beserta peran (`SUPER_ADMIN`, `VERIFIKATOR`, `PANITIA`). |
| `perangkat_notifikasi` | Subscription Web Push milik pendaftar atau admin. |
| `pengumuman` | Pengumuman yang dikelola admin dan tampil di halaman publik. |

## Relasi penting

- Satu pendaftar punya paling banyak satu `data_asal_sekolah`.
- Satu pendaftar hanya boleh punya satu formulir per tahun akademik (unik pada `mahasiswa_id` + `tahun_akademik`).
- `formulir_pendaftaran` menunjuk dua kali ke `admin`: `verifikator_id` (yang memeriksa berkas) dan `penetap_id` (yang menetapkan hasil).
- Satu formulir hanya boleh punya satu berkas per jenis dokumen (unik pada `formulir_id` + `jenis`).
- Satu baris `perangkat_notifikasi` dimiliki tepat satu pihak: pendaftar atau admin.
- Menghapus pendaftar menghapus formulir, berkas, tagihan, dan perangkat notifikasinya (`ON DELETE CASCADE`). Prodi dan jalur yang sudah dipakai formulir tidak bisa dihapus (`RESTRICT`).

## Constraint tingkat database (validasi lapis 3)

- NIK 16 digit, nomor HP format Indonesia, NPSN 8 digit, nilai rata-rata 0 sampai 100.
- Periode jalur valid: `tanggal_tutup > tanggal_buka`, pengumuman hasil tidak sebelum penutupan.
- Status `REVISI` wajib disertai catatan.
- Formulir yang sudah dikirim wajib punya nomor pendaftaran dan waktu finalisasi.
- Hasil seleksi hanya boleh ditetapkan setelah berkas `TERVERIFIKASI`.
- Berkas maksimal 5 MB, hanya PDF, JPG, atau PNG.
- Trigger: pengiriman pertama formulir ditolak di luar periode jalur.
- Trigger: penetapan `LULUS` ditolak bila kuota prodi penuh (baris prodi dikunci agar aman dari race condition).
- Row Level Security aktif di semua tabel; akses data hanya lewat server.

## Nilai enum

| Enum | Nilai |
|---|---|
| `status_berkas` | DRAFT, DIKIRIM, DALAM_REVIEW, REVISI, TERVERIFIKASI |
| `status_kelulusan` | BELUM_DITETAPKAN, LULUS, CADANGAN, TIDAK_LULUS |
| `jenis_dokumen` | PAS_FOTO, KTP_KK, IJAZAH_SKL, RAPOR, SURAT_KETERANGAN_PENGHASILAN, DOKUMEN_PENDUKUNG |
| `status_verifikasi_berkas` | MENUNGGU, VALID, REVISI |
| `status_tagihan` | BELUM_BAYAR, MENUNGGU_KONFIRMASI, LUNAS, KEDALUWARSA, DIBATALKAN |
| `role_admin` | SUPER_ADMIN, VERIFIKATOR, PANITIA |
| `jenjang_prodi` | D3, D4, S1 |
| `jenis_kelamin` | LAKI_LAKI, PEREMPUAN |