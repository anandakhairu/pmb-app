import { cache } from "react";

// =============================================================================
// DATA AREA MAHASISWA (placeholder)
// Bentuk datanya meniru kolom Prisma (calon_mahasiswa, formulir_pendaftaran,
// berkas_dokumen), sama seperti pendekatan data-publik.js. Saat Supabase Auth
// dan database siap, ganti isi getDataMahasiswa() dengan query Prisma
// (berdasarkan sesi login) tanpa mengubah komponen tampilan.
// =============================================================================

/** Dokumen yang diminta. `jenis` = nilai enum JenisDokumen di schema.prisma. */
export const DAFTAR_DOKUMEN = [
  { jenis: "PAS_FOTO", nama: "Pas foto", petunjuk: "Foto formal berlatar polos, format JPG atau PNG.", wajib: true },
  { jenis: "KTP_KK", nama: "KTP atau Kartu Keluarga", petunjuk: "Pindai dokumen asli. Seluruh tulisan harus terbaca jelas.", wajib: true },
  { jenis: "IJAZAH_SKL", nama: "Ijazah atau Surat Keterangan Lulus", petunjuk: "Unggah ijazah, atau SKL bila ijazah belum terbit.", wajib: true },
  { jenis: "RAPOR", nama: "Rapor", petunjuk: "Gabungkan halaman rapor semester 1 sampai 5 dalam satu PDF.", wajib: true },
  { jenis: "SURAT_KETERANGAN_PENGHASILAN", nama: "Surat keterangan penghasilan orang tua", petunjuk: "Dipakai untuk menentukan golongan UKT. Wajib untuk Seleksi Mandiri.", wajib: false },
];

const JENIS_WAJIB_MANDIRI = "SURAT_KETERANGAN_PENGHASILAN"; // untuk penentuan UKT (lihat persyaratan Seleksi Mandiri)

/** Apakah dokumen ini wajib untuk jalur yang dipilih pendaftar. */
export const apakahWajib = (dokumen, jalurKode) =>
  dokumen.wajib || (dokumen.jenis === JENIS_WAJIB_MANDIRI && jalurKode === "MANDIRI");

/* --------------------------------- SKENARIO -------------------------------- */
// Untuk melihat semua tampilan tanpa database, ubah SKENARIO_AKTIF di bawah:
// "draft" | "berkas" | "dikirim" | "review" | "revisi" | "terverifikasi" |
// "lulus" | "cadangan" | "tidak_lulus"
// Hapus blok ini saat query Prisma sudah dipasang.
const SKENARIO_AKTIF = "revisi";

const PRODI = { kode: "SI", nama: "Sistem Informasi", fakultas: "Fakultas Ilmu Komputer", jenjang: "S1", akreditasi: "Unggul" };
const JALUR = { kode: "MANDIRI", nama: "Seleksi Mandiri", tanggalPengumumanHasil: "2027-07-15T03:00:00.000Z" };

const mahasiswaDasar = {
  id: "11111111-1111-4111-8111-111111111111",
  namaLengkap: "Aulia Rahmawati",
  email: "aulia@example.com",
  nik: "3374012345670001",
  tempatLahir: "Semarang",
  tanggalLahir: "2008-03-14",
  jenisKelamin: "PEREMPUAN",
  noHp: "081234567890",
  alamat: "Jl. Sekaran Raya No. 12",
  kotaKabupaten: "Kota Semarang",
  provinsi: "Jawa Tengah",
};

const sekolahDasar = {
  namaSekolah: "SMA Negeri 1 Semarang",
  npsn: "20328876",
  jenisSekolah: "SMA",
  jurusan: "IPA",
  tahunLulus: 2027,
  nilaiRataRata: "86.40",
};

const formulirDasar = {
  tahunAkademik: "2027/2028",
  prodi: PRODI,
  jalur: JALUR,
  nomorPendaftaran: "PMB-2027-000123",
  langkahTerakhir: 4,
  statusBerkas: "DRAFT",
  statusKelulusan: "BELUM_DITETAPKAN",
  catatanRevisi: null,
  catatanKelulusan: null,
  finalisasiAt: "2027-05-20T02:15:00.000Z",
  diverifikasiAt: null,
  ditetapkanAt: null,
};

const berkas = (jenis, statusVerifikasi, extra = {}) => ({
  jenis,
  statusVerifikasi,
  catatan: null,
  namaFile: `${jenis.toLowerCase()}.pdf`,
  mimeType: "application/pdf",
  ukuranByte: 1_240_000,
  ...extra,
});

const semuaDengan = (status) =>
  DAFTAR_DOKUMEN.filter((d) => apakahWajib(d, JALUR.kode)).map((d) => berkas(d.jenis, status));

const SKENARIO = {
  draft: {
    formulir: { ...formulirDasar, langkahTerakhir: 2, nomorPendaftaran: null, finalisasiAt: null },
    berkas: [],
  },
  berkas: {
    formulir: { ...formulirDasar, nomorPendaftaran: null, finalisasiAt: null },
    berkas: [berkas("PAS_FOTO", "MENUNGGU", { namaFile: "pas-foto.jpg", mimeType: "image/jpeg", ukuranByte: 480_000 })],
  },
  dikirim: {
    formulir: { ...formulirDasar, statusBerkas: "DIKIRIM" },
    berkas: semuaDengan("MENUNGGU"),
  },
  review: {
    formulir: { ...formulirDasar, statusBerkas: "DALAM_REVIEW" },
    berkas: semuaDengan("MENUNGGU"),
  },
  revisi: {
    formulir: {
      ...formulirDasar,
      statusBerkas: "REVISI",
      catatanRevisi: "Scan rapor semester 3 terpotong di bagian bawah. Unggah ulang dengan halaman utuh.",
    },
    berkas: [
      berkas("PAS_FOTO", "VALID", { namaFile: "pas-foto.jpg", mimeType: "image/jpeg", ukuranByte: 480_000 }),
      berkas("KTP_KK", "VALID"),
      berkas("IJAZAH_SKL", "VALID"),
      berkas("RAPOR", "REVISI", { catatan: "Halaman semester 3 terpotong. Pindai ulang seluruh halaman." }),
      berkas("SURAT_KETERANGAN_PENGHASILAN", "VALID"),
    ],
  },
  terverifikasi: {
    formulir: { ...formulirDasar, statusBerkas: "TERVERIFIKASI", diverifikasiAt: "2027-05-28T07:30:00.000Z" },
    berkas: semuaDengan("VALID"),
  },
  lulus: {
    formulir: {
      ...formulirDasar,
      statusBerkas: "TERVERIFIKASI",
      statusKelulusan: "LULUS",
      diverifikasiAt: "2027-05-28T07:30:00.000Z",
      ditetapkanAt: "2027-07-15T03:00:00.000Z",
    },
    berkas: semuaDengan("VALID"),
  },
  cadangan: {
    formulir: {
      ...formulirDasar,
      statusBerkas: "TERVERIFIKASI",
      statusKelulusan: "CADANGAN",
      catatanKelulusan: "Kamu berada di daftar cadangan. Panitia akan menghubungi bila ada kursi yang kosong.",
      diverifikasiAt: "2027-05-28T07:30:00.000Z",
      ditetapkanAt: "2027-07-15T03:00:00.000Z",
    },
    berkas: semuaDengan("VALID"),
  },
  tidak_lulus: {
    formulir: {
      ...formulirDasar,
      statusBerkas: "TERVERIFIKASI",
      statusKelulusan: "TIDAK_LULUS",
      catatanKelulusan: "Skor seleksi belum mencapai batas kuota program studi pilihan.",
      diverifikasiAt: "2027-05-28T07:30:00.000Z",
      ditetapkanAt: "2027-07-15T03:00:00.000Z",
    },
    berkas: semuaDengan("VALID"),
  },
};

/**
 * Ambil data pendaftar yang sedang login.
 * TODO (setelah Supabase Auth): baca sesi, lalu
 *   prisma.calonMahasiswa.findUnique({
 *     where: { authUserId },
 *     include: { asalSekolah: true, formulir: { include: { prodi: true, jalur: true, berkas: true } } },
 *   })
 * Fungsi dibuat async agar bentuk pemanggilnya tidak berubah.
 */
// cache() dari React: layout dan halaman memanggil fungsi ini dalam satu request,
// tetapi query hanya dijalankan sekali.
export const getDataMahasiswa = cache(async () => {
  const s = SKENARIO[SKENARIO_AKTIF];
  return { mahasiswa: mahasiswaDasar, sekolah: sekolahDasar, formulir: s.formulir, berkas: s.berkas };
});

/* --------------------------------- HELPER ---------------------------------- */

/** Posisi pendaftar pada stepper 4 tahap: Draft, Berkas, Verifikasi, Hasil. */
export function hitungTahap(formulir) {
  const { statusBerkas, statusKelulusan, langkahTerakhir } = formulir;
  if (statusBerkas === "DRAFT") {
    return { indeks: langkahTerakhir >= 4 ? 1 : 0, peringatan: false };
  }
  if (statusBerkas === "TERVERIFIKASI") {
    return { indeks: statusKelulusan === "BELUM_DITETAPKAN" ? 3 : 4, peringatan: false };
  }
  return { indeks: 2, peringatan: statusBerkas === "REVISI" };
}

/** Gabungkan daftar dokumen dengan berkas yang sudah ada di database. */
export function gabungkanBerkas(berkasAda, jalurKode) {
  return DAFTAR_DOKUMEN.map((d) => {
    const ada = berkasAda.find((b) => b.jenis === d.jenis);
    return {
      ...d,
      wajib: apakahWajib(d, jalurKode),
      berkas: ada ?? null,
      status: ada ? ada.statusVerifikasi : "BELUM_ADA",
    };
  });
}

const tanggalFmt = new Intl.DateTimeFormat("id-ID", { dateStyle: "long", timeZone: "Asia/Jakarta" });
export const formatTanggal = (iso) => (iso ? tanggalFmt.format(new Date(iso)) : "-");

