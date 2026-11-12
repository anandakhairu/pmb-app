// Automated E2E Checkpoint Test for PMB-App
// Tests all active routes for 200 OK, exact semantic text markers, and component functionality.

const BASE_URL = "http://localhost:3000";

const routes = [
  {
    path: "/",
    name: "Landing Page Portal PMB",
    checks: [
      { text: "ADMITRA", desc: "Branding ADMITRA di header/navbar" },
      { text: "Mulai Perjalanan Akademikmu di Sini", desc: "Hero Headline" },
      { text: "Simulasi UKT", desc: "Komponen Kalkulator UKT Interaktif" },
      { text: "Program Studi", desc: "Navigasi/Seksi Program Studi" },
      { text: "Daftar Sekarang", desc: "Tombol CTA Pendaftaran" },
      { text: "Jadwal Penerimaan", desc: "Seksi Jadwal Seleksi PMB" },
    ],
  },
  {
    path: "/login",
    name: "Halaman Masuk (Login)",
    checks: [
      { text: "Masuk ke portal", desc: "Heading Halaman Login" },
      { text: "Belum punya akun?", desc: "Link Registrasi Akun" },
      { text: "Email", desc: "Label Input Email" },
      { text: "Kata sandi", desc: "Label Input Kata Sandi" },
      { text: "Lupa kata sandi?", desc: "Link Lupa Password" },
    ],
  },
  {
    path: "/register",
    name: "Halaman Registrasi Calon Mahasiswa",
    checks: [
      { text: "Buat akun pendaftar", desc: "Heading Halaman Registrasi" },
      { text: "Nama lengkap", desc: "Label Input Nama Lengkap" },
      { text: "Email aktif", desc: "Label Input Email Aktif" },
      { text: "Nomor WhatsApp", desc: "Label Input Nomor WhatsApp" },
      { text: "Kata sandi", desc: "Label Input Kata Sandi" },
      { text: "Ulangi kata sandi", desc: "Label Konfirmasi Password" },
      { text: "Buat akun", desc: "Tombol Submit Registrasi" },
    ],
  },
  {
    path: "/dashboard",
    name: "Dashboard Mahasiswa (Overview & Stepper)",
    checks: [
      { text: "Aulia Rahmawati", desc: "Nama Mahasiswa Pendaftar" },
      { text: "PMB-2027-000123", desc: "Nomor Pendaftaran Resmi" },
      { text: "Beranda", desc: "Menu Sidebar Beranda" },
      { text: "Biodata", desc: "Menu / Stepper Biodata" },
      { text: "Unggah Berkas", desc: "Menu / Stepper Unggah Berkas" },
      { text: "Ada berkas yang perlu diperbaiki", desc: "Alert Status Pendaftaran (Skenario Revisi)" },
    ],
  },
  {
    path: "/dashboard/biodata",
    name: "Dashboard Mahasiswa (Form Biodata)",
    checks: [
      { text: "Biodata", desc: "Heading Halaman Biodata" },
      { text: "Data pribadi", desc: "Legend Form Data Pribadi" },
      { text: "Asal sekolah", desc: "Legend Form Asal Sekolah" },
      { text: "Nama lengkap", desc: "Field Nama Lengkap" },
      { text: "NIK", desc: "Field NIK 16 digit" },
      { text: "SMA Negeri 1 Semarang", desc: "Value Nama Sekolah" },
    ],
  },
  {
    path: "/dashboard/berkas",
    name: "Dashboard Mahasiswa (Unggah Dokumen)",
    checks: [
      { text: "Unggah berkas", desc: "Heading Halaman Unggah Berkas" },
      { text: "Pas foto", desc: "Dokumen Pas Foto" },
      { text: "KTP atau Kartu Keluarga", desc: "Dokumen KTP / KK" },
      { text: "Ijazah atau Surat Keterangan Lulus", desc: "Dokumen Ijazah / SKL" },
      { text: "Kirim ulang perbaikan", desc: "Tombol Submit Perbaikan Berkas Revisi" },
    ],
  },
  {
    path: "/dashboard/kelulusan",
    name: "Dashboard Mahasiswa (Hasil Seleksi)",
    checks: [
      { text: "Hasil seleksi", desc: "Heading Halaman Hasil Seleksi" },
      { text: "Hasil belum tersedia", desc: "Status Hasil Berdasarkan Status Berkas" },
      { text: "Cek status berkas", desc: "Link Cek Status Berkas" },
    ],
  },
  {
    path: "/admin",
    name: "Admin Dashboard Analytics",
    checks: [
      { text: "Dashboard Analytics", desc: "Heading Admin Analytics" },
      { text: "Total Pendaftar", desc: "Kartu Metrik 1: Total Pendaftar" },
      { text: "Perlu Verifikasi", desc: "Kartu Metrik 2: Perlu Verifikasi" },
      { text: "Berkas Revisi", desc: "Kartu Metrik 3: Berkas Revisi" },
      { text: "Dinyatakan Lulus", desc: "Kartu Metrik 4: Dinyatakan Lulus" },
      { text: "Pendaftar Masuk Terbaru", desc: "Tabel Pendaftar Masuk Terbaru" },
    ],
  },
  {
    path: "/admin/verifikasi",
    name: "Admin Antrean Verifikasi",
    checks: [
      { text: "Antrean Verifikasi Berkas", desc: "Heading Antrean Verifikasi" },
      { text: "Semua Status", desc: "Filter Tab Semua Status" },
      { text: "Perlu Verifikasi", desc: "Filter Tab Perlu Verifikasi" },
      { text: "Kelengkapan Dokumen", desc: "Kolom Tabel Kelengkapan Dokumen" },
    ],
  },
  {
    path: "/admin/verifikasi/f1a11111-0001-4000-8000-000000000001",
    name: "Admin Split-View Verifikasi Detail",
    checks: [
      { text: "Aulia Rahmawati", desc: "Nama Pendaftar Terpilih" },
      { text: "PMB-2027-000123", desc: "Nomor Pendaftaran Terpilih" },
      { text: "Kembali ke Antrean", desc: "Tombol Kembali" },
      { text: "Keputusan Status Formulir", desc: "Pilihan Status Akhir Berkas" },
      { text: "Kirim Web Push Notification", desc: "Toggle Web Push Notification" },
      { text: "Simpan Hasil Verifikasi", desc: "Tombol Submit Keputusan Verifikasi" },
    ],
  },
  {
    path: "/admin/master-data",
    name: "Admin Master Data",
    checks: [
      { text: "Master Data PMB", desc: "Heading Master Data" },
      { text: "Katalog Program Studi", desc: "Seksi Program Studi" },
      { text: "Jalur Pendaftaran", desc: "Seksi Jalur Seleksi" },
    ],
  },
  {
    path: "/admin/pengaturan",
    name: "Admin Pengaturan & Integrasi",
    checks: [
      { text: "Pengaturan Sistem", desc: "Heading Pengaturan" },
      { text: "Web Push Notification", desc: "Status Web Push Requirement" },
      { text: "Validasi 3 Lapisan", desc: "Status Validasi 3 Lapisan" },
    ],
  },
];

async function runTests() {
  console.log("=================================================");
  console.log("🚀 CHECKPOINT E2E TESTING (PMB-APP)");
  console.log(`🌐 Base URL: ${BASE_URL}`);
  console.log("=================================================\n");

  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;

  for (const route of routes) {
    const url = `${BASE_URL}${route.path}`;
    process.stdout.write(`Testing [${route.path}] ${route.name} ... `);

    try {
      const startTime = Date.now();
      const res = await fetch(url, { headers: { "User-Agent": "PMB-E2E-Tester/1.0" } });
      const elapsed = Date.now() - startTime;

      if (res.status !== 200) {
        console.log(`❌ GAGAL! HTTP Status: ${res.status}`);
        failedTests++;
        continue;
      }

      const html = await res.text();
      let routeChecksPassed = true;
      const issues = [];

      for (const check of route.checks) {
        totalTests++;
        if (html.includes(check.text)) {
          passedTests++;
        } else {
          routeChecksPassed = false;
          failedTests++;
          issues.push(`Marker "${check.text}" (${check.desc}) TIDAK DITEMUKAN`);
        }
      }

      if (routeChecksPassed) {
        console.log(`✅ OK (${elapsed}ms, ${route.checks.length}/${route.checks.length} assertions passed)`);
      } else {
        console.log(`⚠️ SEBAGIAN GAGAL:`);
        issues.forEach((iss) => console.log(`   - ❌ ${iss}`));
      }
    } catch (err) {
      console.log(`❌ KONEKSI GAGAL: ${err.message}`);
      failedTests++;
    }
  }

  console.log("\n=================================================");
  console.log("📊 HASIL CHECKPOINT E2E TESTING:");
  console.log(`   Total Assertions: ${totalTests}`);
  console.log(`   Berhasil: ${passedTests}`);
  console.log(`   Gagal: ${failedTests}`);
  console.log(`   Status Akhir: ${failedTests === 0 ? "PASSED (100% HIJAU) 🎉" : "FAILED"}`);
  console.log("=================================================");

  if (failedTests > 0) {
    process.exit(1);
  }
}

runTests();
