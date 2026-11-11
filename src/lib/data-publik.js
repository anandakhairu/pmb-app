// =============================================================================
// DATA HALAMAN PUBLIK (placeholder)
// Bentuk datanya meniru kolom database (program_studi, jalur_pendaftaran,
// pengumuman). Saat database siap, ganti isi file ini dengan query Prisma
// tanpa mengubah komponen tampilan.
// =============================================================================

/* ------------------------------- FOTO ------------------------------------- */
// Letakkan file foto di folder public/images/ dengan nama di bawah ini.
// Kalau file belum ada, tampil placeholder otomatis (tidak error).
export const GAMBAR = {
  hero: "/images/hero.jpg",
  heroKecil: "/images/hero-2.jpg",
  kampus: "/images/kampus.jpg",
  galeri: ["/images/galeri-1.jpg", "/images/galeri-2.jpg", "/images/galeri-3.jpg"],
};

/* --------------------------- PROGRAM STUDI (64) ---------------------------- */
// Tarif UKT per semester untuk golongan 1, 2, 3 menurut rumpun keilmuan.
export const TARIF_RUMPUN = {
  sosial: [500_000, 2_000_000, 4_000_000],
  ekonomi: [500_000, 2_250_000, 4_750_000],
  sains: [500_000, 2_500_000, 5_500_000],
  teknik: [500_000, 3_000_000, 6_500_000],
  kesehatan: [500_000, 3_500_000, 8_000_000],
  kedokteran: [500_000, 5_000_000, 14_000_000],
};

// Entri prodi berupa teks (ikut rumpun fakultas) atau [nama, rumpun].
const FAKULTAS = [
  { nama: "Fakultas Teknik", rumpun: "teknik", prodi: ["Teknik Sipil", "Teknik Mesin", "Teknik Elektro", "Teknik Industri", "Teknik Kimia", "Arsitektur", "Teknik Lingkungan", "Perencanaan Wilayah dan Kota"] },
  { nama: "Fakultas Ilmu Komputer", rumpun: "teknik", prodi: ["Teknik Informatika", "Sistem Informasi", "Sains Data", "Teknologi Informasi", "Keamanan Siber"] },
  { nama: "Fakultas Ekonomi dan Bisnis", rumpun: "ekonomi", prodi: ["Akuntansi", "Manajemen", "Ekonomi Pembangunan", "Bisnis Digital", "Keuangan dan Perbankan", "Kewirausahaan"] },
  { nama: "Fakultas Hukum", rumpun: "sosial", prodi: ["Ilmu Hukum", "Hukum Bisnis", "Hukum Internasional"] },
  { nama: "Fakultas Keguruan dan Ilmu Pendidikan", rumpun: "sosial", prodi: ["Pendidikan Guru Sekolah Dasar", "Pendidikan Guru PAUD", "Pendidikan Matematika", "Pendidikan Bahasa Indonesia", "Pendidikan Bahasa Inggris", "Pendidikan Biologi", "Pendidikan Jasmani"] },
  { nama: "Fakultas Kedokteran dan Ilmu Kesehatan", rumpun: "kesehatan", prodi: [["Pendidikan Dokter", "kedokteran"], "Keperawatan", "Kebidanan", "Farmasi", "Gizi"] },
  { nama: "Fakultas Kesehatan Masyarakat", rumpun: "kesehatan", prodi: ["Kesehatan Masyarakat", "Kesehatan Lingkungan", "Keselamatan dan Kesehatan Kerja"] },
  { nama: "Fakultas Matematika dan Ilmu Pengetahuan Alam", rumpun: "sains", prodi: ["Matematika", "Fisika", "Kimia", "Biologi", "Statistika", "Ilmu Lingkungan"] },
  { nama: "Fakultas Psikologi", rumpun: "sosial", prodi: ["Psikologi", "Bimbingan dan Konseling"] },
  { nama: "Fakultas Ilmu Sosial dan Ilmu Politik", rumpun: "sosial", prodi: ["Ilmu Komunikasi", "Hubungan Internasional", "Ilmu Pemerintahan", "Administrasi Publik", "Sosiologi", "Ilmu Politik"] },
  { nama: "Fakultas Ilmu Budaya", rumpun: "sosial", prodi: ["Sastra Indonesia", "Sastra Inggris", "Sastra Jepang", "Ilmu Sejarah", "Antropologi"] },
  { nama: "Fakultas Pertanian", rumpun: "sains", prodi: ["Agroteknologi", "Agribisnis", "Teknologi Pangan", "Peternakan", "Budidaya Perairan", "Kehutanan", "Teknik Pertanian", "Ilmu Tanah"] },
];

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
const PRODI_D4 = new Set(["Kebidanan", "Keselamatan dan Kesehatan Kerja"]);
const AKREDITASI = ["Unggul", "Baik Sekali", "Unggul", "Baik Sekali", "Baik"]; // placeholder

export const FAKULTAS_LIST = FAKULTAS.map((f) => f.nama);

export const PRODI = FAKULTAS.flatMap((f) =>
  f.prodi.map((p) => {
    const [nama, rumpun] = typeof p === "string" ? [p, f.rumpun] : p;
    return { nama, rumpun, fakultas: f.nama };
  }),
).map((p, i) => ({
  value: slug(p.nama),
  nama: p.nama,
  fakultas: p.fakultas,
  jenjang: PRODI_D4.has(p.nama) ? "D4" : "S1",
  akreditasi: AKREDITASI[i % AKREDITASI.length],
  ukt: TARIF_RUMPUN[p.rumpun], // [golongan 1, golongan 2, golongan 3]
}));

/* ------------------------------- LAINNYA ---------------------------------- */

export const STATISTIK = [
  { nilai: String(FAKULTAS_LIST.length), label: "Fakultas" },
  { nilai: String(PRODI.length), label: "Program Studi" },
  { nilai: "85%", label: "Serapan Lulusan" },
  { nilai: "Tersedia", label: "KIP-Kuliah" },
];

export const PROFIL = {
  judul: "Kampus yang menyiapkan kamu untuk bekerja dan berkarya",
  deskripsi: [
    "Kurikulum disusun bersama dunia industri agar lulusan siap bekerja dan siap melanjutkan studi. Kelas kecil, dosen yang mudah dijumpai, dan fasilitas yang dipakai setiap hari.",
    "Penerimaan mahasiswa baru dilakukan secara daring dan transparan, dari pendaftaran sampai pengumuman hasil seleksi.",
  ],
  nilai: [
    { judul: "Kurikulum terkini", isi: "Dirancang bersama praktisi industri." },
    { judul: "Dosen berpengalaman", isi: "Mayoritas bergelar magister dan doktor." },
    { judul: "Biaya terjangkau", isi: "UKT bergolongan dan beasiswa KIP-Kuliah." },
  ],
};

export const JALUR = [
  {
    id: "snbp",
    nama: "SNBP",
    subjudul: "Seleksi berdasarkan prestasi",
    deskripsi: "Jalur tanpa tes untuk siswa berprestasi. Penilaian memakai nilai rapor dan rekam jejak akademik selama SMA atau sederajat.",
    biaya: 0,
    periode: "3 Februari sampai 4 Maret 2027",
    persyaratan: ["Lulusan SMA, SMK, atau MA tahun 2025 sampai 2027", "Nilai rapor semester 1 sampai 5 terunggah", "Peringkat terbaik di sekolah sesuai kuota", "Pas foto dan scan KTP atau KK"],
  },
  {
    id: "snbt",
    nama: "SNBT",
    subjudul: "Tes nasional berbasis komputer",
    deskripsi: "Seleksi melalui tes kemampuan akademik secara nasional, untuk calon mahasiswa yang percaya diri dengan hasil tesnya.",
    biaya: 200_000,
    periode: "1 sampai 15 April 2027",
    persyaratan: ["Lulusan SMA, SMK, atau MA tahun 2025 sampai 2027", "Mengikuti tes berbasis komputer sesuai jadwal", "Ijazah atau surat keterangan lulus", "Pas foto dan scan KTP atau KK"],
  },
  {
    id: "mandiri",
    nama: "Seleksi Mandiri",
    subjudul: "Ujian dan seleksi kampus",
    deskripsi: "Seleksi yang diselenggarakan langsung oleh kampus, dengan ujian CBT dan kuota terpisah di setiap program studi.",
    biaya: 300_000,
    periode: "1 Mei sampai 30 Juni 2027",
    persyaratan: ["Lulusan SMA, SMK, MA, atau sederajat", "Mengikuti ujian CBT kampus", "Rapor atau transkrip nilai", "Surat keterangan penghasilan orang tua untuk penentuan UKT"],
  },
];

export const JADWAL = [
  { tanggal: "3 Februari 2027", tahap: "Pendaftaran SNBP dibuka", ket: "Isi formulir dan unggah berkas." },
  { tanggal: "1 April 2027", tahap: "Pendaftaran SNBT dibuka", ket: "Pilih jadwal tes CBT." },
  { tanggal: "1 Mei 2027", tahap: "Pendaftaran Seleksi Mandiri dibuka", ket: "Tersedia dua gelombang." },
  { tanggal: "15 Juli 2027", tahap: "Pengumuman hasil seleksi", ket: "Hasil tampil di akun pendaftar." },
  { tanggal: "1 Agustus 2027", tahap: "Registrasi ulang", ket: "Pembayaran UKT dan pengambilan jas almamater." },
];

export const PENGUMUMAN = [
  { slug: "jadwal-pendaftaran-2027", tanggal: "10 November 2026", judul: "Jadwal pendaftaran mahasiswa baru 2027/2028 resmi dirilis", ringkasan: "Pendaftaran dibuka mulai Februari 2027 melalui tiga jalur." },
  { slug: "beasiswa-kip-kuliah", tanggal: "2 November 2026", judul: "Kuota KIP-Kuliah tersedia di seluruh program studi", ringkasan: "Calon mahasiswa dari keluarga kurang mampu dapat mengajukan lewat portal." },
  { slug: "simulasi-ukt", tanggal: "25 Oktober 2026", judul: "Simulasi UKT kini tersedia di portal", ringkasan: "Hitung estimasi biaya kuliah sebelum mendaftar, tanpa perlu login." },
];

// Kontak placeholder, ganti dengan data institusi sebenarnya.
export const KONTAK = [
  "Jl. Pendidikan No. 1, Semarang, Jawa Tengah",
  "(024) 000 0000",
  "pmb@admitra.ac.id",
  "Senin sampai Jumat, 08.00 sampai 15.00 WIB",
];