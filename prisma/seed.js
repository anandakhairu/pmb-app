/* eslint-disable no-console */

try { require("dotenv").config(); } catch { /* dotenv opsional */ }

const crypto = require("node:crypto");
const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();

const DOMAIN = "demo.admitra.id";
const PASSWORD_ADMIN = process.env.SEED_ADMIN_PASSWORD || "Admin12345";
const PASSWORD_MABA = process.env.SEED_MABA_PASSWORD || "Maba12345";
const TAHUN_AKADEMIK = "2027/2028";

const hariKe = (n) => new Date(Date.now() + n * 86_400_000);

/* -------------------------------------------------------------------------- */
/* Akun Supabase Auth                                                         */
/* -------------------------------------------------------------------------- */

function buatSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    console.warn("! Kunci Supabase tidak ada di .env: akun Auth TIDAK dibuat (data tidak bisa dipakai login).");
    return null;
  }
  try {
    const { createClient } = require("@supabase/supabase-js");
    return createClient(url, key, { auth: { autoRefreshToken: false, persistSession: false } });
  } catch {
    console.warn("! Paket @supabase/supabase-js belum terpasang (npm i @supabase/supabase-js): akun Auth TIDAK dibuat.");
    return null;
  }
}

// UUID tetap dari teks, dipakai bila Supabase tidak tersedia (agar tetap idempotent)
function uuidDariTeks(teks) {
  const h = crypto.createHash("sha1").update(`admitra-seed:${teks}`).digest("hex");
  const variant = ((parseInt(h.slice(16, 18), 16) & 0x3f) | 0x80).toString(16);
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-5${h.slice(13, 16)}-${variant}${h.slice(18, 20)}-${h.slice(20, 32)}`;
}

async function idAkunAuth(supabase, { email, password, nama }) {
  if (!supabase) return uuidDariTeks(email);

  const { data, error } = await supabase.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
    user_metadata: { nama_lengkap: nama },
  });
  if (!error) return data.user.id;

  // Akun sudah ada dari seed sebelumnya: ambil id-nya
  const { data: daftar, error: errDaftar } = await supabase.auth.admin.listUsers({ page: 1, perPage: 1000 });
  if (errDaftar) throw errDaftar;
  const ada = daftar.users.find((u) => u.email?.toLowerCase() === email.toLowerCase());
  if (!ada) throw error;
  return ada.id;
}

/* -------------------------------------------------------------------------- */
/* Data master                                                                */
/* -------------------------------------------------------------------------- */

// Format tarif_ukt: lihat komentar pada model ProgramStudi di schema.prisma
const tarifUkt = (g1, g2, g3) => [
  { golongan: 1, minPenghasilan: 0, maxPenghasilan: 2_000_000, biaya: g1 },
  { golongan: 2, minPenghasilan: 2_000_001, maxPenghasilan: 5_000_000, biaya: g2 },
  { golongan: 3, minPenghasilan: 5_000_001, maxPenghasilan: null, biaya: g3 },
];

const PRODI = [
  { kode: "SI", nama: "Sistem Informasi", fakultas: "Fakultas Ilmu Komputer", jenjang: "S1", akreditasi: "Unggul", kuota: 120, tarif: tarifUkt(500_000, 3_000_000, 6_500_000) },
  { kode: "TI", nama: "Teknik Informatika", fakultas: "Fakultas Ilmu Komputer", jenjang: "S1", akreditasi: "Unggul", kuota: 100, tarif: tarifUkt(500_000, 3_000_000, 6_500_000) },
  { kode: "ILKOM", nama: "Ilmu Komputer", fakultas: "Fakultas Ilmu Komputer", jenjang: "S1", akreditasi: "Baik Sekali", kuota: 80, tarif: tarifUkt(500_000, 2_750_000, 6_000_000) },
];

// Rentang tanggal sengaja mencakup hari ini agar jalur berstatus aktif
const buka = hariKe(-30);
const tutup = hariKe(60);
const pengumumanHasil = hariKe(75);

const JALUR = [
  {
    kode: "SNBP", nama: "SNBP", butuhUjianCbt: false, biayaPendaftaran: 0,
    deskripsi: "Seleksi berdasarkan prestasi akademik, tanpa tes.",
    persyaratan: ["Lulusan SMA, SMK, atau MA", "Nilai rapor semester 1 sampai 5", "Pas foto dan scan KTP atau KK"],
  },
  {
    kode: "SNBT", nama: "SNBT", butuhUjianCbt: true, biayaPendaftaran: 200_000,
    deskripsi: "Seleksi melalui tes berbasis komputer secara nasional.",
    persyaratan: ["Lulusan SMA, SMK, atau MA", "Mengikuti tes sesuai jadwal", "Ijazah atau surat keterangan lulus"],
  },
  {
    kode: "MANDIRI", nama: "Seleksi Mandiri CBT", butuhUjianCbt: true, biayaPendaftaran: 300_000,
    deskripsi: "Seleksi mandiri kampus dengan ujian CBT.",
    persyaratan: ["Lulusan SMA, SMK, MA, atau sederajat", "Mengikuti ujian CBT kampus", "Rapor atau transkrip nilai"],
  },
];

/* -------------------------------------------------------------------------- */
/* Pendaftar: 5 variasi status                                                */
/* -------------------------------------------------------------------------- */

const DOKUMEN = [
  { jenis: "PAS_FOTO", file: "pas-foto.jpg", mime: "image/jpeg", ukuran: 412_000 },
  { jenis: "KTP_KK", file: "ktp-kk.pdf", mime: "application/pdf", ukuran: 865_000 },
  { jenis: "IJAZAH_SKL", file: "ijazah-skl.pdf", mime: "application/pdf", ukuran: 1_240_000 },
  { jenis: "RAPOR", file: "rapor.pdf", mime: "application/pdf", ukuran: 2_100_000 },
];

const CATATAN_FOTO = "Pas foto kurang jelas. Unggah ulang dengan latar polos dan resolusi lebih tinggi.";

// Urutan status berkas mengikuti urutan DOKUMEN: [PAS_FOTO, KTP_KK, IJAZAH_SKL, RAPOR]
const MABA = [
  {
    email: "aulia@example.com", nama: "Aulia Rahmawati", jk: "PEREMPUAN", noHp: "081234567890",
    profil: { nik: "3374012345670001", tempatLahir: "Semarang", tanggalLahir: "2008-03-14", alamat: "Jl. Sekaran Raya No. 12", kotaKabupaten: "Kota Semarang", provinsi: "Jawa Tengah" },
    sekolah: { namaSekolah: "SMA Negeri 1 Semarang", npsn: "20328876", jurusan: "MIPA", nilai: "88.50" },
    prodi: "SI", jalur: "MANDIRI", langkah: 4, statusBerkas: "REVISI", nomor: "PMB-2027-000123",
    finalisasi: -8, verifikator: true,
    catatanRevisi: "Pemeriksaan QA: perbaikan scan rapor semester 3.",
    berkas: [["VALID"], ["VALID"], ["VALID"], ["REVISI", "Halaman semester 3 terpotong di bagian bawah."]],
  },
  {
    email: `nadia.putri@${DOMAIN}`, nama: "Nadia Putri Rahma", jk: "PEREMPUAN", noHp: "081234567801",
    // Biodata baru terisi sebagian: belum ada NIK, alamat, dan data sekolah
    profil: { tempatLahir: "Semarang", tanggalLahir: "2008-03-14" },
    sekolah: null,
    prodi: "SI", jalur: "SNBP", langkah: 2, statusBerkas: "DRAFT",
    berkas: [],
  },
  {
    email: `raka.aditya@${DOMAIN}`, nama: "Raka Aditya Pratama", jk: "LAKI_LAKI", noHp: "081234567802",
    profil: { nik: "3374010505080002", tempatLahir: "Semarang", tanggalLahir: "2008-05-05", alamat: "Jl. Pandanaran No. 21", kotaKabupaten: "Kota Semarang", provinsi: "Jawa Tengah" },
    sekolah: { namaSekolah: "SMA Negeri 3 Semarang", npsn: "20328852", jurusan: "IPA", nilai: "86.40" },
    prodi: "TI", jalur: "SNBT", langkah: 4, statusBerkas: "DIKIRIM", nomor: "PMB-2027-900002",
    finalisasi: -2,
    berkas: [["MENUNGGU"], ["MENUNGGU"], ["MENUNGGU"], ["MENUNGGU"]],
  },
  {
    email: `salsabila.ayu@${DOMAIN}`, nama: "Salsabila Ayu Lestari", jk: "PEREMPUAN", noHp: "081234567803",
    profil: { nik: "3374014409080003", tempatLahir: "Kendal", tanggalLahir: "2008-09-04", alamat: "Jl. Soekarno Hatta No. 8", kotaKabupaten: "Kendal", provinsi: "Jawa Tengah" },
    sekolah: { namaSekolah: "SMA Negeri 1 Kendal", npsn: "20301567", jurusan: "IPS", nilai: "88.75" },
    prodi: "SI", jalur: "SNBP", langkah: 4, statusBerkas: "DALAM_REVIEW", nomor: "PMB-2027-900003",
    finalisasi: -5, verifikator: true,
    berkas: [["VALID"], ["VALID"], ["MENUNGGU"], ["MENUNGGU"]],
  },
  {
    email: `dimas.ardiansyah@${DOMAIN}`, nama: "Dimas Ardiansyah", jk: "LAKI_LAKI", noHp: "081234567804",
    profil: { nik: "3374011212070004", tempatLahir: "Demak", tanggalLahir: "2007-12-12", alamat: "Jl. Sultan Fatah No. 15", kotaKabupaten: "Demak", provinsi: "Jawa Tengah" },
    sekolah: { namaSekolah: "SMK Negeri 2 Semarang", npsn: "20328911", jurusan: "Teknik Komputer dan Jaringan", nilai: "82.10" },
    prodi: "ILKOM", jalur: "MANDIRI", langkah: 4, statusBerkas: "REVISI", nomor: "PMB-2027-900004",
    finalisasi: -7, verifikator: true,
    catatanRevisi: CATATAN_FOTO,
    berkas: [["REVISI", CATATAN_FOTO], ["VALID"], ["VALID"], ["VALID"]],
  },
  {
    email: `anindya.kirana@${DOMAIN}`, nama: "Anindya Kirana Dewi", jk: "PEREMPUAN", noHp: "081234567805",
    profil: { nik: "3374015507080005", tempatLahir: "Salatiga", tanggalLahir: "2008-07-15", alamat: "Jl. Diponegoro No. 40", kotaKabupaten: "Salatiga", provinsi: "Jawa Tengah" },
    sekolah: { namaSekolah: "SMA Negeri 1 Salatiga", npsn: "20329174", jurusan: "IPA", nilai: "94.20" },
    prodi: "TI", jalur: "SNBP", langkah: 4, statusBerkas: "TERVERIFIKASI", statusKelulusan: "LULUS", nomor: "PMB-2027-900005",
    finalisasi: -14, diverifikasi: -10, ditetapkan: -2, verifikator: true, penetap: true,
    catatanKelulusan: "Selamat, Anda diterima di Teknik Informatika. Silakan lakukan registrasi ulang.",
    berkas: [["VALID"], ["VALID"], ["VALID"], ["VALID"]],
  },
  {
    email: "irfaannnnr@gmail.com", nama: "Irfan Fatkhurrizal", jk: "LAKI_LAKI", noHp: "081234567899",
    profil: { tempatLahir: "Semarang", tanggalLahir: "2006-01-01" },
    sekolah: null,
    prodi: "SI", jalur: "SNBP", langkah: 1, statusBerkas: "DRAFT",
    berkas: [],
  },
];

/* -------------------------------------------------------------------------- */
/* Eksekusi                                                                   */
/* -------------------------------------------------------------------------- */

async function main() {
  const supabase = buatSupabaseAdmin();

  // --- Admin ---
  const emailAdmin = `admin@${DOMAIN}`;
  const authAdmin = await idAkunAuth(supabase, { email: emailAdmin, password: PASSWORD_ADMIN, nama: "Panitia PMB ADMITRA" });
  const admin = await prisma.admin.upsert({
    where: { email: emailAdmin },
    create: { authUserId: authAdmin, email: emailAdmin, nama: "Panitia PMB ADMITRA", role: "SUPER_ADMIN", aktif: true },
    update: { authUserId: authAdmin, nama: "Panitia PMB ADMITRA", role: "SUPER_ADMIN", aktif: true },
  });

  // --- Program studi ---
  const idProdi = {};
  for (const p of PRODI) {
    const data = { nama: p.nama, fakultas: p.fakultas, jenjang: p.jenjang, akreditasi: p.akreditasi, kuota: p.kuota, tarifUkt: p.tarif, aktif: true };
    const row = await prisma.programStudi.upsert({ where: { kode: p.kode }, create: { kode: p.kode, ...data }, update: data });
    idProdi[p.kode] = row.id;
  }

  // --- Jalur pendaftaran ---
  const idJalur = {};
  for (const j of JALUR) {
    const data = {
      nama: j.nama, deskripsi: j.deskripsi, persyaratan: j.persyaratan,
      butuhUjianCbt: j.butuhUjianCbt, biayaPendaftaran: j.biayaPendaftaran,
      tanggalBuka: buka, tanggalTutup: tutup, tanggalPengumumanHasil: pengumumanHasil, aktif: true,
    };
    const row = await prisma.jalurPendaftaran.upsert({ where: { kode: j.kode }, create: { kode: j.kode, ...data }, update: data });
    idJalur[j.kode] = row.id;
  }

  // --- Calon mahasiswa, asal sekolah, formulir, berkas ---
  for (const m of MABA) {
    const authId = await idAkunAuth(supabase, { email: m.email, password: PASSWORD_MABA, nama: m.nama });

    const profil = {
      namaLengkap: m.nama, jenisKelamin: m.jk, noHp: m.noHp,
      nik: m.profil.nik ?? null,
      tempatLahir: m.profil.tempatLahir ?? null,
      tanggalLahir: m.profil.tanggalLahir ? new Date(m.profil.tanggalLahir) : null,
      alamat: m.profil.alamat ?? null,
      kotaKabupaten: m.profil.kotaKabupaten ?? null,
      provinsi: m.profil.provinsi ?? null,
    };
    const maba = await prisma.calonMahasiswa.upsert({
      where: { email: m.email },
      create: { authUserId: authId, email: m.email, ...profil },
      update: { authUserId: authId, ...profil },
    });

    if (m.sekolah) {
      const sekolah = {
        namaSekolah: m.sekolah.namaSekolah, npsn: m.sekolah.npsn, jenisSekolah: m.sekolah.namaSekolah.startsWith("SMK") ? "SMK" : "SMA",
        jurusan: m.sekolah.jurusan, tahunLulus: 2026, nilaiRataRata: m.sekolah.nilai,
      };
      await prisma.dataAsalSekolah.upsert({
        where: { mahasiswaId: maba.id },
        create: { mahasiswaId: maba.id, ...sekolah },
        update: sekolah,
      });
    }

    const formulirData = {
      nomorPendaftaran: m.nomor ?? null,
      prodiId: idProdi[m.prodi],
      jalurId: idJalur[m.jalur],
      verifikatorId: m.verifikator ? admin.id : null,
      penetapId: m.penetap ? admin.id : null,
      langkahTerakhir: m.langkah,
      statusBerkas: m.statusBerkas,
      statusKelulusan: m.statusKelulusan ?? "BELUM_DITETAPKAN",
      catatanRevisi: m.catatanRevisi ?? null,
      catatanKelulusan: m.catatanKelulusan ?? null,
      finalisasiAt: m.finalisasi != null ? hariKe(m.finalisasi) : null,
      diverifikasiAt: m.diverifikasi != null ? hariKe(m.diverifikasi) : null,
      ditetapkanAt: m.ditetapkan != null ? hariKe(m.ditetapkan) : null,
    };
    const formulir = await prisma.formulirPendaftaran.upsert({
      where: { mahasiswaId_tahunAkademik: { mahasiswaId: maba.id, tahunAkademik: TAHUN_AKADEMIK } },
      create: { mahasiswaId: maba.id, tahunAkademik: TAHUN_AKADEMIK, ...formulirData },
      update: formulirData,
    });

    // Berkas (metadata saja; file fisik tidak ada di Storage)
    for (let i = 0; i < m.berkas.length; i++) {
      const [status, catatan] = m.berkas[i];
      const d = DOKUMEN[i];
      const berkas = {
        namaFile: d.file,
        storagePath: `seed/${m.nomor}/${d.file}`,
        mimeType: d.mime,
        ukuranByte: d.ukuran,
        statusVerifikasi: status,
        catatan: catatan ?? null,
      };
      await prisma.berkasDokumen.upsert({
        where: { formulirId_jenis: { formulirId: formulir.id, jenis: d.jenis } },
        create: { formulirId: formulir.id, jenis: d.jenis, ...berkas },
        update: berkas,
      });
    }
  }

  // --- Pengumuman publik ---
  const PENGUMUMAN_DATA = [
    {
      slug: "jadwal-pendaftaran-2027",
      judul: "Jadwal pendaftaran mahasiswa baru 2027/2028 resmi dirilis",
      ringkasan: "Pendaftaran dibuka mulai Februari 2027 melalui tiga jalur.",
      isi: "Penerimaan Mahasiswa Baru ADMITRA Tahun Akademik 2027/2028 resmi dibuka. Terdapat tiga jalur seleksi utama: SNBP, SNBT, dan Seleksi Mandiri CBT.",
      dipublikasikan: true,
      publishedAt: new Date("2026-11-10T08:00:00.000Z"),
    },
    {
      slug: "beasiswa-kip-kuliah",
      judul: "Kuota KIP-Kuliah tersedia di seluruh program studi",
      ringkasan: "Calon mahasiswa dari keluarga kurang mampu dapat mengajukan lewat portal.",
      isi: "Program Indonesia Pintar melalui KIP-Kuliah dialokasikan untuk calon mahasiswa berprestasi yang membutuhkan dukungan finansial di seluruh program studi.",
      dipublikasikan: true,
      publishedAt: new Date("2026-11-02T08:00:00.000Z"),
    },
    {
      slug: "simulasi-ukt",
      judul: "Simulasi UKT kini tersedia di portal",
      ringkasan: "Hitung estimasi biaya kuliah sebelum mendaftar, tanpa perlu login.",
      isi: "Kalkulator interaktif penaksir UKT kini dapat diakses langsung pada beranda portal PMB ADMITRA untuk memberikan transparansi pembiayaan kuliah.",
      dipublikasikan: true,
      publishedAt: new Date("2026-10-25T08:00:00.000Z"),
    },
  ];

  for (const item of PENGUMUMAN_DATA) {
    await prisma.pengumuman.upsert({
      where: { slug: item.slug },
      create: { ...item, adminId: admin.id },
      update: { ...item, adminId: admin.id },
    });
  }

  // --- Jadwal CBT ---
  const mandiriRow = await prisma.jalurPendaftaran.findUnique({ where: { kode: "MANDIRI" } });
  if (mandiriRow) {
    const sesi = [
      {
        nama: "Gelombang 1 - Sesi Pagi",
        tanggal: new Date("2027-05-15"),
        jamMulai: new Date("1970-01-01T08:30:00.000Z"),
        jamSelesai: new Date("1970-01-01T11:30:00.000Z"),
        lokasi: "Lab Komputer Gedung B Lt. 3",
        kapasitas: 80,
      },
      {
        nama: "Gelombang 1 - Sesi Siang",
        tanggal: new Date("2027-05-15"),
        jamMulai: new Date("1970-01-01T13:00:00.000Z"),
        jamSelesai: new Date("1970-01-01T16:00:00.000Z"),
        lokasi: "Lab Komputer Gedung B Lt. 3",
        kapasitas: 80,
      },
    ];

    for (const s of sesi) {
      const existing = await prisma.jadwalUjianCbt.findFirst({
        where: { jalurId: mandiriRow.id, nama: s.nama },
      });
      if (!existing) {
        await prisma.jadwalUjianCbt.create({
          data: {
            jalurId: mandiriRow.id,
            ...s,
            aktif: true,
          },
        });
      }
    }
  }

  console.log("\nSeed selesai.\n");
  console.table([
    { peran: "Admin", email: emailAdmin, kataSandi: PASSWORD_ADMIN, status: "SUPER_ADMIN" },
    ...MABA.map((m) => ({
      peran: "Mahasiswa", email: m.email, kataSandi: PASSWORD_MABA,
      status: m.statusKelulusan ? `${m.statusBerkas} / ${m.statusKelulusan}` : m.statusBerkas,
    })),
  ]);
  if (!supabase) console.log("Catatan: akun belum dibuat di Supabase Auth, jadi belum bisa dipakai login.");
}

main()
  .catch((e) => {
    console.error("\nSeed gagal:", e.message ?? e);
    process.exitCode = 1;
  })
  .finally(() => prisma.$disconnect());