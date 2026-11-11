-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "jenis_kelamin" AS ENUM ('LAKI_LAKI', 'PEREMPUAN');

-- CreateEnum
CREATE TYPE "jenjang_prodi" AS ENUM ('D3', 'D4', 'S1');

-- CreateEnum
CREATE TYPE "status_berkas" AS ENUM ('DRAFT', 'DIKIRIM', 'DALAM_REVIEW', 'REVISI', 'TERVERIFIKASI');

-- CreateEnum
CREATE TYPE "status_kelulusan" AS ENUM ('BELUM_DITETAPKAN', 'LULUS', 'CADANGAN', 'TIDAK_LULUS');

-- CreateEnum
CREATE TYPE "jenis_dokumen" AS ENUM ('PAS_FOTO', 'KTP_KK', 'IJAZAH_SKL', 'RAPOR', 'SURAT_KETERANGAN_PENGHASILAN', 'DOKUMEN_PENDUKUNG');

-- CreateEnum
CREATE TYPE "status_verifikasi_berkas" AS ENUM ('MENUNGGU', 'VALID', 'REVISI');

-- CreateEnum
CREATE TYPE "status_tagihan" AS ENUM ('BELUM_BAYAR', 'MENUNGGU_KONFIRMASI', 'LUNAS', 'KEDALUWARSA', 'DIBATALKAN');

-- CreateEnum
CREATE TYPE "role_admin" AS ENUM ('SUPER_ADMIN', 'VERIFIKATOR', 'PANITIA');

-- CreateTable
CREATE TABLE "calon_mahasiswa" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "auth_user_id" UUID NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "nama_lengkap" VARCHAR(150) NOT NULL,
    "nik" CHAR(16),
    "tempat_lahir" VARCHAR(100),
    "tanggal_lahir" DATE,
    "jenis_kelamin" "jenis_kelamin",
    "no_hp" VARCHAR(20),
    "alamat" TEXT,
    "kota_kabupaten" VARCHAR(100),
    "provinsi" VARCHAR(100),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "calon_mahasiswa_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "data_asal_sekolah" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "mahasiswa_id" UUID NOT NULL,
    "nama_sekolah" VARCHAR(200) NOT NULL,
    "npsn" VARCHAR(8),
    "jenis_sekolah" VARCHAR(50),
    "jurusan" VARCHAR(100),
    "tahun_lulus" SMALLINT NOT NULL,
    "nilai_rata_rata" DECIMAL(5,2) NOT NULL,
    "alamat_sekolah" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "data_asal_sekolah_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "program_studi" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "kode" VARCHAR(10) NOT NULL,
    "nama" VARCHAR(150) NOT NULL,
    "fakultas" VARCHAR(150) NOT NULL,
    "jenjang" "jenjang_prodi" NOT NULL,
    "akreditasi" VARCHAR(20),
    "kuota" INTEGER NOT NULL DEFAULT 0,
    "deskripsi" TEXT,
    "tarif_ukt" JSONB NOT NULL DEFAULT '[]',
    "aktif" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "program_studi_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "jalur_pendaftaran" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "kode" VARCHAR(20) NOT NULL,
    "nama" VARCHAR(100) NOT NULL,
    "deskripsi" TEXT,
    "persyaratan" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "butuh_ujian_cbt" BOOLEAN NOT NULL DEFAULT false,
    "biaya_pendaftaran" DECIMAL(12,2) NOT NULL DEFAULT 0,
    "tanggal_buka" TIMESTAMPTZ(6) NOT NULL,
    "tanggal_tutup" TIMESTAMPTZ(6) NOT NULL,
    "tanggal_pengumuman_hasil" TIMESTAMPTZ(6),
    "aktif" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "jalur_pendaftaran_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "formulir_pendaftaran" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "nomor_pendaftaran" VARCHAR(30),
    "tahun_akademik" VARCHAR(9) NOT NULL,
    "mahasiswa_id" UUID NOT NULL,
    "prodi_id" UUID NOT NULL,
    "jalur_id" UUID NOT NULL,
    "jadwal_ujian_id" UUID,
    "verifikator_id" UUID,
    "penetap_id" UUID,
    "langkah_terakhir" SMALLINT NOT NULL DEFAULT 1,
    "status_berkas" "status_berkas" NOT NULL DEFAULT 'DRAFT',
    "status_kelulusan" "status_kelulusan" NOT NULL DEFAULT 'BELUM_DITETAPKAN',
    "catatan_revisi" TEXT,
    "catatan_kelulusan" TEXT,
    "finalisasi_at" TIMESTAMPTZ(6),
    "diverifikasi_at" TIMESTAMPTZ(6),
    "ditetapkan_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "formulir_pendaftaran_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "berkas_dokumen" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "formulir_id" UUID NOT NULL,
    "jenis" "jenis_dokumen" NOT NULL,
    "nama_file" VARCHAR(255) NOT NULL,
    "storage_path" VARCHAR(500) NOT NULL,
    "mime_type" VARCHAR(100) NOT NULL,
    "ukuran_byte" INTEGER NOT NULL,
    "status_verifikasi" "status_verifikasi_berkas" NOT NULL DEFAULT 'MENUNGGU',
    "catatan" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "berkas_dokumen_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "jadwal_ujian_cbt" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "jalur_id" UUID NOT NULL,
    "nama" VARCHAR(150) NOT NULL,
    "tanggal" DATE NOT NULL,
    "jam_mulai" TIME(0) NOT NULL,
    "jam_selesai" TIME(0) NOT NULL,
    "lokasi" VARCHAR(200) NOT NULL,
    "kapasitas" INTEGER NOT NULL,
    "tautan_ujian" TEXT,
    "aktif" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "jadwal_ujian_cbt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "tagihan_pembayaran" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "formulir_id" UUID NOT NULL,
    "nomor_tagihan" VARCHAR(30) NOT NULL,
    "deskripsi" VARCHAR(200) NOT NULL,
    "nominal" DECIMAL(12,2) NOT NULL,
    "status" "status_tagihan" NOT NULL DEFAULT 'BELUM_BAYAR',
    "metode" VARCHAR(50),
    "bukti_bayar_url" TEXT,
    "jatuh_tempo" TIMESTAMPTZ(6) NOT NULL,
    "dibayar_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "tagihan_pembayaran_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "auth_user_id" UUID NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "nama" VARCHAR(150) NOT NULL,
    "role" "role_admin" NOT NULL DEFAULT 'PANITIA',
    "aktif" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "admin_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "perangkat_notifikasi" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "mahasiswa_id" UUID,
    "admin_id" UUID,
    "endpoint" TEXT NOT NULL,
    "p256dh" TEXT NOT NULL,
    "auth_key" TEXT NOT NULL,
    "user_agent" TEXT,
    "aktif" BOOLEAN NOT NULL DEFAULT true,
    "terakhir_dipakai" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "perangkat_notifikasi_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pengumuman" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "admin_id" UUID,
    "judul" VARCHAR(200) NOT NULL,
    "slug" VARCHAR(220) NOT NULL,
    "ringkasan" VARCHAR(300),
    "isi" TEXT NOT NULL,
    "dipublikasikan" BOOLEAN NOT NULL DEFAULT false,
    "published_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "pengumuman_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "calon_mahasiswa_auth_user_id_key" ON "calon_mahasiswa"("auth_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "calon_mahasiswa_email_key" ON "calon_mahasiswa"("email");

-- CreateIndex
CREATE UNIQUE INDEX "calon_mahasiswa_nik_key" ON "calon_mahasiswa"("nik");

-- CreateIndex
CREATE UNIQUE INDEX "data_asal_sekolah_mahasiswa_id_key" ON "data_asal_sekolah"("mahasiswa_id");

-- CreateIndex
CREATE UNIQUE INDEX "program_studi_kode_key" ON "program_studi"("kode");

-- CreateIndex
CREATE INDEX "program_studi_fakultas_idx" ON "program_studi"("fakultas");

-- CreateIndex
CREATE UNIQUE INDEX "jalur_pendaftaran_kode_key" ON "jalur_pendaftaran"("kode");

-- CreateIndex
CREATE UNIQUE INDEX "formulir_pendaftaran_nomor_pendaftaran_key" ON "formulir_pendaftaran"("nomor_pendaftaran");

-- CreateIndex
CREATE INDEX "formulir_pendaftaran_status_berkas_finalisasi_at_idx" ON "formulir_pendaftaran"("status_berkas", "finalisasi_at");

-- CreateIndex
CREATE INDEX "formulir_pendaftaran_prodi_id_status_kelulusan_idx" ON "formulir_pendaftaran"("prodi_id", "status_kelulusan");

-- CreateIndex
CREATE INDEX "formulir_pendaftaran_jalur_id_idx" ON "formulir_pendaftaran"("jalur_id");

-- CreateIndex
CREATE UNIQUE INDEX "formulir_pendaftaran_mahasiswa_id_tahun_akademik_key" ON "formulir_pendaftaran"("mahasiswa_id", "tahun_akademik");

-- CreateIndex
CREATE UNIQUE INDEX "berkas_dokumen_formulir_id_jenis_key" ON "berkas_dokumen"("formulir_id", "jenis");

-- CreateIndex
CREATE INDEX "jadwal_ujian_cbt_jalur_id_tanggal_idx" ON "jadwal_ujian_cbt"("jalur_id", "tanggal");

-- CreateIndex
CREATE UNIQUE INDEX "tagihan_pembayaran_nomor_tagihan_key" ON "tagihan_pembayaran"("nomor_tagihan");

-- CreateIndex
CREATE INDEX "tagihan_pembayaran_formulir_id_idx" ON "tagihan_pembayaran"("formulir_id");

-- CreateIndex
CREATE INDEX "tagihan_pembayaran_status_jatuh_tempo_idx" ON "tagihan_pembayaran"("status", "jatuh_tempo");

-- CreateIndex
CREATE UNIQUE INDEX "admin_auth_user_id_key" ON "admin"("auth_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "admin_email_key" ON "admin"("email");

-- CreateIndex
CREATE UNIQUE INDEX "perangkat_notifikasi_endpoint_key" ON "perangkat_notifikasi"("endpoint");

-- CreateIndex
CREATE INDEX "perangkat_notifikasi_mahasiswa_id_idx" ON "perangkat_notifikasi"("mahasiswa_id");

-- CreateIndex
CREATE INDEX "perangkat_notifikasi_admin_id_idx" ON "perangkat_notifikasi"("admin_id");

-- CreateIndex
CREATE UNIQUE INDEX "pengumuman_slug_key" ON "pengumuman"("slug");

-- CreateIndex
CREATE INDEX "pengumuman_dipublikasikan_published_at_idx" ON "pengumuman"("dipublikasikan", "published_at");

-- AddForeignKey
ALTER TABLE "data_asal_sekolah" ADD CONSTRAINT "data_asal_sekolah_mahasiswa_id_fkey" FOREIGN KEY ("mahasiswa_id") REFERENCES "calon_mahasiswa"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_mahasiswa_id_fkey" FOREIGN KEY ("mahasiswa_id") REFERENCES "calon_mahasiswa"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_prodi_id_fkey" FOREIGN KEY ("prodi_id") REFERENCES "program_studi"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_jalur_id_fkey" FOREIGN KEY ("jalur_id") REFERENCES "jalur_pendaftaran"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_jadwal_ujian_id_fkey" FOREIGN KEY ("jadwal_ujian_id") REFERENCES "jadwal_ujian_cbt"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_verifikator_id_fkey" FOREIGN KEY ("verifikator_id") REFERENCES "admin"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "formulir_pendaftaran" ADD CONSTRAINT "formulir_pendaftaran_penetap_id_fkey" FOREIGN KEY ("penetap_id") REFERENCES "admin"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "berkas_dokumen" ADD CONSTRAINT "berkas_dokumen_formulir_id_fkey" FOREIGN KEY ("formulir_id") REFERENCES "formulir_pendaftaran"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "jadwal_ujian_cbt" ADD CONSTRAINT "jadwal_ujian_cbt_jalur_id_fkey" FOREIGN KEY ("jalur_id") REFERENCES "jalur_pendaftaran"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tagihan_pembayaran" ADD CONSTRAINT "tagihan_pembayaran_formulir_id_fkey" FOREIGN KEY ("formulir_id") REFERENCES "formulir_pendaftaran"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "perangkat_notifikasi" ADD CONSTRAINT "perangkat_notifikasi_mahasiswa_id_fkey" FOREIGN KEY ("mahasiswa_id") REFERENCES "calon_mahasiswa"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "perangkat_notifikasi" ADD CONSTRAINT "perangkat_notifikasi_admin_id_fkey" FOREIGN KEY ("admin_id") REFERENCES "admin"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pengumuman" ADD CONSTRAINT "pengumuman_admin_id_fkey" FOREIGN KEY ("admin_id") REFERENCES "admin"("id") ON DELETE SET NULL ON UPDATE CASCADE;

 
-- =============================================================================
-- VALIDASI LAPIS 3: CONSTRAINT, TRIGGER, DAN RLS POSTGRESQL  (v2)
--
-- Cara pakai (satu migrasi saja, constraint ditempel DI AKHIR migrasi pertama):
--   1. npx prisma migrate dev --create-only --name init
--      (membuat prisma/migrations/<timestamp>_init/migration.sql, BELUM dijalankan)
--   2. Buka migration.sql itu, tempel SELURUH isi file ini di baris paling bawah.
--   3. npx prisma migrate dev
--      (menjalankan tabel + constraint + trigger sekaligus)
-- =============================================================================

-- ---------- calon_mahasiswa ----------
ALTER TABLE calon_mahasiswa
  ADD CONSTRAINT chk_maba_nik_16_digit CHECK (nik IS NULL OR nik ~ '^[0-9]{16}$'),
  ADD CONSTRAINT chk_maba_no_hp        CHECK (no_hp IS NULL OR no_hp ~ '^(\+62|62|0)8[0-9]{8,12}$'),
  ADD CONSTRAINT chk_maba_tgl_lahir    CHECK (tanggal_lahir IS NULL OR tanggal_lahir < CURRENT_DATE);

-- ---------- data_asal_sekolah ----------
ALTER TABLE data_asal_sekolah
  ADD CONSTRAINT chk_sekolah_nilai       CHECK (nilai_rata_rata BETWEEN 0 AND 100),
  ADD CONSTRAINT chk_sekolah_tahun_lulus CHECK (tahun_lulus BETWEEN 2000 AND 2100),
  ADD CONSTRAINT chk_sekolah_npsn        CHECK (npsn IS NULL OR npsn ~ '^[0-9]{8}$');

-- ---------- program_studi ----------
ALTER TABLE program_studi
  ADD CONSTRAINT chk_prodi_kuota       CHECK (kuota >= 0),
  ADD CONSTRAINT chk_prodi_tarif_array CHECK (jsonb_typeof(tarif_ukt) = 'array');

-- ---------- jalur_pendaftaran ----------
ALTER TABLE jalur_pendaftaran
  ADD CONSTRAINT chk_jalur_biaya      CHECK (biaya_pendaftaran >= 0),
  ADD CONSTRAINT chk_jalur_periode    CHECK (tanggal_tutup > tanggal_buka),
  ADD CONSTRAINT chk_jalur_pengumuman CHECK (tanggal_pengumuman_hasil IS NULL OR tanggal_pengumuman_hasil >= tanggal_tutup);

-- ---------- formulir_pendaftaran ----------
ALTER TABLE formulir_pendaftaran
  ADD CONSTRAINT chk_form_langkah        CHECK (langkah_terakhir BETWEEN 1 AND 4),
  ADD CONSTRAINT chk_form_tahun_akademik CHECK (tahun_akademik ~ '^[0-9]{4}/[0-9]{4}$'),
  -- Revisi wajib disertai catatan
  ADD CONSTRAINT chk_form_revisi_catatan CHECK (status_berkas <> 'REVISI' OR (catatan_revisi IS NOT NULL AND length(trim(catatan_revisi)) > 0)),
  -- Formulir yang sudah dikirim wajib punya nomor pendaftaran & waktu finalisasi
  ADD CONSTRAINT chk_form_nomor_final    CHECK (status_berkas = 'DRAFT' OR (nomor_pendaftaran IS NOT NULL AND finalisasi_at IS NOT NULL)),
  -- Hasil seleksi hanya boleh ditetapkan setelah berkas terverifikasi
  ADD CONSTRAINT chk_form_hasil_verified CHECK (status_kelulusan = 'BELUM_DITETAPKAN' OR (status_berkas = 'TERVERIFIKASI' AND ditetapkan_at IS NOT NULL AND penetap_id IS NOT NULL));

-- ---------- berkas_dokumen ----------
ALTER TABLE berkas_dokumen
  ADD CONSTRAINT chk_berkas_ukuran      CHECK (ukuran_byte > 0 AND ukuran_byte <= 5242880), -- maks 5 MB
  ADD CONSTRAINT chk_berkas_mime        CHECK (mime_type IN ('application/pdf','image/jpeg','image/png')),
  ADD CONSTRAINT chk_berkas_revisi_note CHECK (status_verifikasi <> 'REVISI' OR (catatan IS NOT NULL AND length(trim(catatan)) > 0));

-- ---------- tagihan_pembayaran ----------
ALTER TABLE tagihan_pembayaran
  ADD CONSTRAINT chk_tagihan_nominal CHECK (nominal >= 0),
  ADD CONSTRAINT chk_tagihan_lunas   CHECK (status <> 'LUNAS' OR dibayar_at IS NOT NULL);

-- ---------- jadwal_ujian_cbt ----------
ALTER TABLE jadwal_ujian_cbt
  ADD CONSTRAINT chk_jadwal_kapasitas CHECK (kapasitas > 0),
  ADD CONSTRAINT chk_jadwal_jam       CHECK (jam_selesai > jam_mulai);

-- ---------- perangkat_notifikasi: tepat satu pemilik (mahasiswa XOR admin) ----------
ALTER TABLE perangkat_notifikasi
  ADD CONSTRAINT chk_perangkat_pemilik CHECK ((mahasiswa_id IS NOT NULL)::int + (admin_id IS NOT NULL)::int = 1);

-- ---------- pengumuman ----------
ALTER TABLE pengumuman
  ADD CONSTRAINT chk_pengumuman_publish CHECK (NOT dipublikasikan OR published_at IS NOT NULL),
  ADD CONSTRAINT chk_pengumuman_slug    CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$');

-- =============================================================================
-- TRIGGER 1: Pendaftaran hanya dibuka sesuai jadwal jalur.
-- Hanya mengecek pengiriman PERTAMA (DRAFT -> DIKIRIM). Pengiriman ulang setelah
-- REVISI tetap diizinkan walau periode pendaftaran sudah ditutup.
-- =============================================================================
CREATE OR REPLACE FUNCTION fn_cek_jadwal_pendaftaran() RETURNS trigger AS $$
DECLARE
  j jalur_pendaftaran%ROWTYPE;
BEGIN
  IF NEW.status_berkas = 'DIKIRIM'
     AND (TG_OP = 'INSERT' OR OLD.status_berkas = 'DRAFT') THEN
    SELECT * INTO j FROM jalur_pendaftaran WHERE id = NEW.jalur_id;
    IF NOT j.aktif OR now() < j.tanggal_buka OR now() > j.tanggal_tutup THEN
      RAISE EXCEPTION 'Pendaftaran jalur % sedang ditutup', j.nama
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cek_jadwal_pendaftaran
  BEFORE INSERT OR UPDATE ON formulir_pendaftaran
  FOR EACH ROW EXECUTE FUNCTION fn_cek_jadwal_pendaftaran();

-- =============================================================================
-- TRIGGER 2: Kuota program studi tidak boleh terlampaui.
-- Mengunci baris program_studi (FOR UPDATE) sehingga dua penetapan LULUS yang
-- berjalan bersamaan untuk prodi yang sama dieksekusi bergantian (anti race condition).
-- =============================================================================
CREATE OR REPLACE FUNCTION fn_cek_kuota_prodi() RETURNS trigger AS $$
DECLARE
  v_kuota  integer;
  v_terisi integer;
BEGIN
  IF NEW.status_kelulusan = 'LULUS'
     AND (TG_OP = 'INSERT' OR OLD.status_kelulusan IS DISTINCT FROM 'LULUS') THEN
    SELECT kuota INTO v_kuota FROM program_studi WHERE id = NEW.prodi_id FOR UPDATE;

    SELECT count(*) INTO v_terisi
      FROM formulir_pendaftaran
     WHERE prodi_id = NEW.prodi_id
       AND tahun_akademik = NEW.tahun_akademik
       AND status_kelulusan = 'LULUS'
       AND id <> NEW.id;

    IF v_terisi >= v_kuota THEN
      RAISE EXCEPTION 'Kuota program studi sudah penuh'
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cek_kuota_prodi
  BEFORE INSERT OR UPDATE ON formulir_pendaftaran
  FOR EACH ROW EXECUTE FUNCTION fn_cek_kuota_prodi();

-- =============================================================================
-- Penomoran bukti pendaftaran (PMB-2026-000123). Dipanggil lewat nextval() di server.
-- =============================================================================
CREATE SEQUENCE IF NOT EXISTS seq_nomor_pendaftaran START 1;

-- =============================================================================
-- RLS: aktif pada semua tabel tanpa policy. Akses data HANYA lewat server
-- (Prisma memakai role postgres yang melewati RLS), jadi anon key Supabase
-- tidak bisa membaca/menulis tabel secara langsung.
-- =============================================================================
ALTER TABLE calon_mahasiswa      ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_asal_sekolah    ENABLE ROW LEVEL SECURITY;
ALTER TABLE program_studi        ENABLE ROW LEVEL SECURITY;
ALTER TABLE jalur_pendaftaran    ENABLE ROW LEVEL SECURITY;
ALTER TABLE formulir_pendaftaran ENABLE ROW LEVEL SECURITY;
ALTER TABLE berkas_dokumen       ENABLE ROW LEVEL SECURITY;
ALTER TABLE jadwal_ujian_cbt     ENABLE ROW LEVEL SECURITY;
ALTER TABLE tagihan_pembayaran   ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin                ENABLE ROW LEVEL SECURITY;
ALTER TABLE perangkat_notifikasi ENABLE ROW LEVEL SECURITY;
ALTER TABLE pengumuman           ENABLE ROW LEVEL SECURITY;