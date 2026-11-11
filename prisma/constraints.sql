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