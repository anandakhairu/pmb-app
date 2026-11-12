import { cache } from "react";

// =============================================================================
// DATA AREA ADMIN BACK-OFFICE
// Bentuk data disinkronkan 100% dengan skema Prisma 11 tabel:
// (admin, calon_mahasiswa, formulir_pendaftaran, berkas_dokumen, program_studi, jalur_pendaftaran)
// =============================================================================

export const ADMIN_AKTIF = {
  id: "adm-0000-1111-2222-333333333333",
  nama: "Budi Santoso, M.Kom.",
  email: "panitia.pmb@universitas.ac.id",
  role: "VERIFIKATOR", // SUPER_ADMIN | VERIFIKATOR | PANITIA
  nip: "198804152015041002",
};

export const DAFTAR_PENDAFTAR_MOCK = [
  {
    id: "f1a11111-0001-4000-8000-000000000001",
    mahasiswaId: "m1a11111-0001-4000-8000-000000000001",
    nomorPendaftaran: "PMB-2027-000123",
    tahunAkademik: "2027/2028",
    statusBerkas: "DIKIRIM", // Butuh verifikasi
    statusKelulusan: "BELUM_DITETAPKAN",
    catatanRevisi: null,
    finalisasiAt: "2027-02-14T08:30:00.000Z",
    diverifikasiAt: null,
    mahasiswa: {
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
      asalSekolah: {
        namaSekolah: "SMA Negeri 1 Semarang",
        npsn: "20328876",
        jurusan: "MIPA",
        tahunLulus: 2027,
        nilaiRataRata: "88.50",
      },
    },
    prodi: {
      kode: "SI",
      nama: "Sistem Informasi",
      fakultas: "Fakultas Ilmu Komputer",
      jenjang: "S1",
    },
    jalur: {
      kode: "MANDIRI",
      nama: "Seleksi Mandiri",
    },
    berkas: [
      {
        id: "b-001",
        jenis: "PAS_FOTO",
        namaFile: "pas_foto_aulia.jpg",
        storagePath: "berkas/f1/pas_foto.jpg",
        mimeType: "image/jpeg",
        ukuranByte: 245000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/admitra-mark.png",
      },
      {
        id: "b-002",
        jenis: "KTP_KK",
        namaFile: "ktp_kk_resmi.pdf",
        storagePath: "berkas/f1/ktp_kk.pdf",
        mimeType: "application/pdf",
        ukuranByte: 820000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/images/galeri-1.jpg",
      },
      {
        id: "b-003",
        jenis: "IJAZAH_SKL",
        namaFile: "skl_sma1_semarang.pdf",
        storagePath: "berkas/f1/skl.pdf",
        mimeType: "application/pdf",
        ukuranByte: 650000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/images/galeri-2.jpg",
      },
      {
        id: "b-004",
        jenis: "RAPOR",
        namaFile: "rapor_semester_1_5.pdf",
        storagePath: "berkas/f1/rapor.pdf",
        mimeType: "application/pdf",
        ukuranByte: 2400000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/images/galeri-3.jpg",
      },
      {
        id: "b-005",
        jenis: "SURAT_KETERANGAN_PENGHASILAN",
        namaFile: "slip_gaji_ortu.pdf",
        storagePath: "berkas/f1/penghasilan.pdf",
        mimeType: "application/pdf",
        ukuranByte: 410000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/images/kampus.jpg",
      },
    ],
  },
  {
    id: "f1a11111-0002-4000-8000-000000000002",
    mahasiswaId: "m1a11111-0002-4000-8000-000000000002",
    nomorPendaftaran: "PMB-2027-000124",
    tahunAkademik: "2027/2028",
    statusBerkas: "REVISI",
    statusKelulusan: "BELUM_DITETAPKAN",
    catatanRevisi: "Scan KTP terpotong di bagian NIK dan Pas Foto buram. Harap unggah ulang sebelum 20 Februari 2027.",
    finalisasiAt: "2027-02-13T10:15:00.000Z",
    diverifikasiAt: "2027-02-14T09:00:00.000Z",
    mahasiswa: {
      namaLengkap: "Rizky Dwi Pratama",
      email: "rizky.pratama@gmail.com",
      nik: "3301021908070002",
      tempatLahir: "Cilacap",
      tanggalLahir: "2007-08-19",
      jenisKelamin: "LAKI_LAKI",
      noHp: "085712349988",
      alamat: "Jl. Gatot Subroto No. 45",
      kotaKabupaten: "Kabupaten Cilacap",
      provinsi: "Jawa Tengah",
      asalSekolah: {
        namaSekolah: "SMK Negeri 2 Cilacap",
        npsn: "20301142",
        jurusan: "Rekayasa Perangkat Lunak",
        tahunLulus: 2027,
        nilaiRataRata: "85.20",
      },
    },
    prodi: {
      kode: "TI",
      nama: "Teknik Informatika",
      fakultas: "Fakultas Ilmu Komputer",
      jenjang: "S1",
    },
    jalur: {
      kode: "SNBT",
      nama: "Seleksi Nasional Berdasarkan Tes",
    },
    berkas: [
      {
        id: "b-006",
        jenis: "PAS_FOTO",
        namaFile: "foto_rizky.png",
        storagePath: "berkas/f2/pas_foto.png",
        mimeType: "image/png",
        ukuranByte: 180000,
        statusVerifikasi: "REVISI",
        catatan: "Foto buram dan resolusi terlalu kecil.",
        previewUrl: "/admitra-mark.png",
      },
      {
        id: "b-007",
        jenis: "KTP_KK",
        namaFile: "scan_ktp.pdf",
        storagePath: "berkas/f2/ktp.pdf",
        mimeType: "application/pdf",
        ukuranByte: 750000,
        statusVerifikasi: "REVISI",
        catatan: "NIK terpotong di tepi bawah.",
        previewUrl: "/images/galeri-1.jpg",
      },
      {
        id: "b-008",
        jenis: "IJAZAH_SKL",
        namaFile: "surat_keterangan_lulus.pdf",
        storagePath: "berkas/f2/skl.pdf",
        mimeType: "application/pdf",
        ukuranByte: 610000,
        statusVerifikasi: "VALID",
        catatan: null,
        previewUrl: "/images/galeri-2.jpg",
      },
    ],
  },
  {
    id: "f1a11111-0003-4000-8000-000000000003",
    mahasiswaId: "m1a11111-0003-4000-8000-000000000003",
    nomorPendaftaran: "PMB-2027-000125",
    tahunAkademik: "2027/2028",
    statusBerkas: "TERVERIFIKASI",
    statusKelulusan: "LULUS",
    catatanRevisi: null,
    finalisasiAt: "2027-02-12T14:20:00.000Z",
    diverifikasiAt: "2027-02-13T11:00:00.000Z",
    mahasiswa: {
      namaLengkap: "Dewi Safitri Anjani",
      email: "dewi.safitri@yahoo.com",
      nik: "3171055502080003",
      tempatLahir: "Jakarta Selatan",
      tanggalLahir: "2008-02-15",
      jenisKelamin: "PEREMPUAN",
      noHp: "081399887766",
      alamat: "Jl. Tebet Barat Dalam No. 8",
      kotaKabupaten: "Kota Jakarta Selatan",
      provinsi: "DKI Jakarta",
      asalSekolah: {
        namaSekolah: "SMA Negeri 8 Jakarta",
        npsn: "20107298",
        jurusan: "MIPA",
        tahunLulus: 2027,
        nilaiRataRata: "92.10",
      },
    },
    prodi: {
      kode: "DKV",
      nama: "Desain Komunikasi Visual",
      fakultas: "Fakultas Seni & Desain",
      jenjang: "S1",
    },
    jalur: {
      kode: "SNBP",
      nama: "Seleksi Nasional Berdasarkan Prestasi",
    },
    berkas: [
      {
        id: "b-009",
        jenis: "PAS_FOTO",
        namaFile: "foto_dewi_formal.jpg",
        storagePath: "berkas/f3/foto.jpg",
        mimeType: "image/jpeg",
        ukuranByte: 310000,
        statusVerifikasi: "VALID",
        catatan: null,
        previewUrl: "/admitra-mark.png",
      },
      {
        id: "b-010",
        jenis: "KTP_KK",
        namaFile: "kk_dewi_asli.pdf",
        storagePath: "berkas/f3/kk.pdf",
        mimeType: "application/pdf",
        ukuranByte: 950000,
        statusVerifikasi: "VALID",
        catatan: null,
        previewUrl: "/images/galeri-1.jpg",
      },
      {
        id: "b-011",
        jenis: "RAPOR",
        namaFile: "rapor_prestasi_dewi.pdf",
        storagePath: "berkas/f3/rapor.pdf",
        mimeType: "application/pdf",
        ukuranByte: 3100000,
        statusVerifikasi: "VALID",
        catatan: null,
        previewUrl: "/images/galeri-3.jpg",
      },
    ],
  },
  {
    id: "f1a11111-0004-4000-8000-000000000004",
    mahasiswaId: "m1a11111-0004-4000-8000-000000000004",
    nomorPendaftaran: "PMB-2027-000126",
    tahunAkademik: "2027/2028",
    statusBerkas: "DIKIRIM",
    statusKelulusan: "BELUM_DITETAPKAN",
    catatanRevisi: null,
    finalisasiAt: "2027-02-14T11:45:00.000Z",
    diverifikasiAt: null,
    mahasiswa: {
      namaLengkap: "Muhammad Bagas Prasetyo",
      email: "bagas.pras@gmail.com",
      nik: "3578011211070004",
      tempatLahir: "Surabaya",
      tanggalLahir: "2007-11-12",
      jenisKelamin: "LAKI_LAKI",
      noHp: "082133445566",
      alamat: "Jl. Rungkut Madya No. 99",
      kotaKabupaten: "Kota Surabaya",
      provinsi: "Jawa Timur",
      asalSekolah: {
        namaSekolah: "SMA Negeri 5 Surabaya",
        npsn: "20532189",
        jurusan: "MIPA",
        tahunLulus: 2027,
        nilaiRataRata: "90.75",
      },
    },
    prodi: {
      kode: "MN",
      nama: "Manajemen Bisnis",
      fakultas: "Fakultas Ekonomi & Bisnis",
      jenjang: "S1",
    },
    jalur: {
      kode: "MANDIRI",
      nama: "Seleksi Mandiri",
    },
    berkas: [
      {
        id: "b-012",
        jenis: "PAS_FOTO",
        namaFile: "pasfoto_bagas.jpg",
        storagePath: "berkas/f4/pasfoto.jpg",
        mimeType: "image/jpeg",
        ukuranByte: 280000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/admitra-mark.png",
      },
      {
        id: "b-013",
        jenis: "KTP_KK",
        namaFile: "ktp_bagas.pdf",
        storagePath: "berkas/f4/ktp.pdf",
        mimeType: "application/pdf",
        ukuranByte: 720000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/images/galeri-1.jpg",
      },
    ],
  },
  {
    id: "f1a11111-0005-4000-8000-000000000005",
    mahasiswaId: "m1a11111-0005-4000-8000-000000000005",
    nomorPendaftaran: "PMB-2027-000127",
    tahunAkademik: "2027/2028",
    statusBerkas: "DALAM_REVIEW",
    statusKelulusan: "BELUM_DITETAPKAN",
    catatanRevisi: null,
    finalisasiAt: "2027-02-14T07:10:00.000Z",
    diverifikasiAt: null,
    mahasiswa: {
      namaLengkap: "Siti Nurhaliza",
      email: "siti.nur@gmail.com",
      nik: "3273014506080005",
      tempatLahir: "Bandung",
      tanggalLahir: "2008-06-05",
      jenisKelamin: "PEREMPUAN",
      noHp: "087811223344",
      alamat: "Jl. Dago Asri No. 21",
      kotaKabupaten: "Kota Bandung",
      provinsi: "Jawa Barat",
      asalSekolah: {
        namaSekolah: "SMA Negeri 3 Bandung",
        npsn: "20219800",
        jurusan: "IPS",
        tahunLulus: 2027,
        nilaiRataRata: "87.30",
      },
    },
    prodi: {
      kode: "AK",
      nama: "Akuntansi Perpajakan",
      fakultas: "Fakultas Ekonomi & Bisnis",
      jenjang: "D4",
    },
    jalur: {
      kode: "SNBT",
      nama: "Seleksi Nasional Berdasarkan Tes",
    },
    berkas: [
      {
        id: "b-014",
        jenis: "PAS_FOTO",
        namaFile: "foto_siti.jpg",
        storagePath: "berkas/f5/foto.jpg",
        mimeType: "image/jpeg",
        ukuranByte: 290000,
        statusVerifikasi: "MENUNGGU",
        catatan: null,
        previewUrl: "/admitra-mark.png",
      },
      {
        id: "b-015",
        jenis: "IJAZAH_SKL",
        namaFile: "skl_siti.pdf",
        storagePath: "berkas/f5/skl.pdf",
        mimeType: "application/pdf",
        ukuranByte: 810000,
        statusVerifikasi: "VALID",
        catatan: null,
        previewUrl: "/images/galeri-2.jpg",
      },
    ],
  },
];

/** Mengambil ringkasan statistik metrik analytics */
export const getStatistikAdmin = cache(async () => {
  const total = DAFTAR_PENDAFTAR_MOCK.length;
  const perluVerifikasi = DAFTAR_PENDAFTAR_MOCK.filter(
    (p) => p.statusBerkas === "DIKIRIM" || p.statusBerkas === "DALAM_REVIEW"
  ).length;
  const revisi = DAFTAR_PENDAFTAR_MOCK.filter((p) => p.statusBerkas === "REVISI").length;
  const lulus = DAFTAR_PENDAFTAR_MOCK.filter((p) => p.statusKelulusan === "LULUS").length;
  const terverifikasi = DAFTAR_PENDAFTAR_MOCK.filter((p) => p.statusBerkas === "TERVERIFIKASI").length;

  return {
    totalPendaftar: 1420 + total,
    perluVerifikasi: 38 + perluVerifikasi,
    revisi: 14 + revisi,
    lulus: 412 + lulus,
    terverifikasi: 890 + terverifikasi,
    kuotaTotal: 1800,
    persentaseTerverifikasi: Math.round(((890 + terverifikasi) / (1420 + total)) * 100),
  };
});

/** Mengambil daftar pendaftar dengan filter */
export const getDaftarPendaftarAdmin = cache(
  async ({ status, jalur, prodi, q } = {}) => {
    let hasil = DAFTAR_PENDAFTAR_MOCK;

    if (status && status !== "SEMUA") {
      hasil = hasil.filter((p) => p.statusBerkas === status);
    }
    if (jalur && jalur !== "SEMUA") {
      hasil = hasil.filter((p) => p.jalur.kode === jalur);
    }
    if (prodi && prodi !== "SEMUA") {
      hasil = hasil.filter((p) => p.prodi.kode === prodi);
    }
    if (q) {
      const kataKunci = q.toLowerCase();
      hasil = hasil.filter(
        (p) =>
          p.mahasiswa.namaLengkap.toLowerCase().includes(kataKunci) ||
          p.nomorPendaftaran.toLowerCase().includes(kataKunci) ||
          p.mahasiswa.nik.toLowerCase().includes(kataKunci)
      );
    }

    return hasil;
  }
);

/** Mengambil satu detail formulir pendaftar berdasarkan ID */
export const getDetailPendaftarAdmin = cache(async (id) => {
  const item = DAFTAR_PENDAFTAR_MOCK.find((p) => p.id === id);
  return item || null;
});

/** Master data program studi untuk filter & kelengkapan */
export const MASTER_PRODI = [
  { kode: "TI", nama: "Teknik Informatika", jenjang: "S1", fakultas: "Ilmu Komputer", kuota: 120, terisi: 95 },
  { kode: "SI", nama: "Sistem Informasi", jenjang: "S1", fakultas: "Ilmu Komputer", kuota: 100, terisi: 82 },
  { kode: "DKV", nama: "Desain Komunikasi Visual", jenjang: "S1", fakultas: "Seni & Desain", kuota: 80, terisi: 74 },
  { kode: "MN", nama: "Manajemen Bisnis", jenjang: "S1", fakultas: "Ekonomi & Bisnis", kuota: 150, terisi: 140 },
  { kode: "AK", nama: "Akuntansi Perpajakan", jenjang: "D4", fakultas: "Ekonomi & Bisnis", kuota: 90, terisi: 68 },
];

/** Master data jalur pendaftaran */
export const MASTER_JALUR = [
  { kode: "SNBP", nama: "Seleksi Nasional Berdasarkan Prestasi", biaya: 0, status: "TUTUP" },
  { kode: "SNBT", nama: "Seleksi Nasional Berdasarkan Tes", biaya: 200000, status: "BUKA" },
  { kode: "MANDIRI", nama: "Seleksi Mandiri Reguler", biaya: 350000, status: "BUKA" },
];
