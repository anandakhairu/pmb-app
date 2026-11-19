import { NextResponse } from "next/server";
import { kirimPesanAI } from "@/lib/ai/provider";
import { FAKULTAS_LIST, PRODI, TARIF_RUMPUN } from "@/lib/data-publik";

const rupiah = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
});

const PRODI_ALIASES = {
  mesin: "Teknik Mesin",
  sipil: "Teknik Sipil",
  elektro: "Teknik Elektro",
  industri: "Teknik Industri",
  kimia: "Teknik Kimia",
  arsitektur: "Arsitektur",
  kedokteran: "Pendidikan Dokter",
  dokter: "Pendidikan Dokter",
  informatika: "Teknik Informatika",
  ilkom: "Teknik Informatika",
  si: "Sistem Informasi",
  "sistem informasi": "Sistem Informasi",
  hukum: "Ilmu Hukum",
  manajemen: "Manajemen",
  akuntansi: "Akuntansi",
  farmasi: "Farmasi",
  gizi: "Gizi",
  perawat: "Keperawatan",
  keperawatan: "Keperawatan",
  psikologi: "Psikologi",
  "sains data": "Sains Data",
  "data science": "Sains Data",
};

function temukanProdiDariQuery(queryText) {
  const clean = queryText.toLowerCase();
  for (const [alias, namaTarget] of Object.entries(PRODI_ALIASES)) {
    if (new RegExp("\\b" + alias + "\\b", "i").test(clean) || clean.includes(alias)) {
      const match = PRODI.find(
        (p) => p.nama.toLowerCase() === namaTarget.toLowerCase()
      );
      if (match) return match;
    }
  }
  const sorted = [...PRODI].sort((a, b) => b.nama.length - a.nama.length);
  return sorted.find(
    (p) =>
      clean.includes(p.nama.toLowerCase()) ||
      clean.includes(p.value.replace(/-/g, " ")) ||
      clean.includes(p.value)
  );
}

// =============================================================================
// KNOWLEDGE BASE RESMI PMB ADMITRA (RAG SYSTEM CONTEXT)
// =============================================================================

const SYSTEM_PROMPT_KNOWLEDGE = `
Anda adalah perwakilan Pusat Informasi Resmi PMB (Penerimaan Mahasiswa Baru) Universitas ADMITRA 2027/2028.
Tugas Anda adalah melayani pertanyaan calon mahasiswa dengan ramah, santun, formal, dan faktual sesuai data resmi kampus.

Fakta Resmi Universitas ADMITRA:
1. JALUR PENDAFTARAN & JADWAL 2027/2028:
   - SNBP (Prestasi): 3 Februari s.d. 4 Maret 2027 (Gratis / Rp 0).
   - SNBT (Tes UTBK): 1 s.d. 15 April 2027 (Biaya Rp 200.000).
   - Seleksi Mandiri: 1 Mei s.d. 30 Juni 2027 (Biaya Rp 350.000, 2 gelombang CBT di kampus).
   - Pengumuman Kelulusan: 15 Juli 2027.
   - Registrasi Ulang: Mulai 1 Agustus 2027.

2. FAKULTAS & PROGRAM STUDI:
   Universitas ADMITRA memiliki 12 Fakultas dan 64 Program Studi yang aktif, antara lain:
   - Fakultas Teknik: Teknik Mesin, Teknik Sipil, Teknik Elektro, Teknik Industri, Teknik Kimia, Arsitektur, Teknik Lingkungan, PWK. (Teknik Mesin ADA dan dibuka!).
   - Fakultas Ilmu Komputer: Teknik Informatika, Sistem Informasi, Sains Data, Teknologi Informasi, Keamanan Siber.
   - Fakultas Ekonomi dan Bisnis: Akuntansi, Manajemen, Ekonomi Pembangunan, Bisnis Digital, Keuangan & Perbankan.
   - Fakultas Kedokteran & Ilmu Kesehatan: Pendidikan Dokter, Farmasi, Keperawatan, Gizi, Kebidanan.
   - Fakultas Hukum: Ilmu Hukum, Hukum Bisnis, Hukum Internasional.
   - Serta Fakultas MIPA, Pertanian, FISIP, Psikologi, FIB, dan FKIP.

3. KETENTUAN UKT (UANG KULIAH TUNGGAL):
   Ditentukan berdasarkan penghasilan orang tua per jumlah tanggungan:
   - Golongan 1: Rp 500.000 / semester (Semua prodi, penghasilan per tanggungan < Rp 1 juta)
   - Golongan 2: Rp 2.000.000 s.d. Rp 5.000.000 / semester (Teknik Mesin: Rp 3.000.000)
   - Golongan 3: Rp 4.000.000 s.d. Rp 14.000.000 / semester (Teknik Mesin: Rp 6.500.000)
   - Beasiswa KIP-Kuliah: Tersedia, UKT 100% ditanggung (Rp 0).

4. PERSYARATAN BERKAS:
   Pas foto formal (maks 5MB), scan KTP/KK (maks 5MB), ijazah/SKL resmi (maks 5MB), scan rapor semester 1-5 (PDF maks 5MB), serta slip gaji orang tua (khusus Mandiri).

ATURAN MENJAWAB:
- Jawab dengan jujur sesuai data di atas. Jangan pernah mengatakan prodi yang ada sebagai tidak dibuka.
- Jika ditanya UKT prodi spesifik, sebutkan nama prodi, fakultas, dan rincian tarif Golongan 1, 2, dan 3.
`;

/**
 * Fallback cerdas berbasis aturan & Knowledge Base PMB ADMITRA
 * Aktif otomatis jika upstream LLM mengalami gangguan, limit, atau kuota habis.
 * @param {string} query
 * @returns {string}
 */
function cariJawabanFallback(query) {
  const q = query.toLowerCase();

  // 1. INTENT: JADWAL & WAKTU PEMBUKAAN PENDAFTARAN
  const isJadwal =
    q.includes("kapan") ||
    q.includes("jadwal") ||
    q.includes("buka") ||
    q.includes("pembukaan") ||
    q.includes("tutup") ||
    q.includes("periode") ||
    q.includes("tanggal") ||
    q.includes("gelombang") ||
    q.includes("batas") ||
    q.includes("waktu");

  if (isJadwal) {
    if (q.includes("mandiri")) {
      return (
        "Pendaftaran **Seleksi Mandiri** Universitas ADMITRA resmi dibuka mulai **1 Mei 2027** sampai **30 Juni 2027**.\n\n" +
        "Informasi Pelaksanaan Jalur Mandiri:\n" +
        "• **Periode Pendaftaran:** 1 Mei – 30 Juni 2027\n" +
        "• **Metode Seleksi:** Ujian Mandiri CBT di kampus (tersedia 2 Gelombang) dan seleksi berkas rapor\n" +
        "• **Biaya Pendaftaran:** Rp 350.000 (via Virtual Account bank mitra)\n" +
        "• **Pengumuman Kelulusan:** 15 Juli 2027\n\n" +
        "Anda sudah dapat membuat akun sekarang di menu Registrasi untuk melengkapi profil sebelum pendaftaran dibuka."
      );
    }

    if (q.includes("snbt") || q.includes("utbk") || q.includes("tes")) {
      return (
        "Pendaftaran **Jalur SNBT (Tes UTBK)** dibuka pada **1 April 2027** sampai **15 April 2027**.\n\n" +
        "• **Periode Pendaftaran:** 1 – 15 April 2027\n" +
        "• **Biaya Pendaftaran:** Rp 200.000\n" +
        "• **Metode Seleksi:** Ujian Tulis Berbasis Komputer (UTBK)\n" +
        "• **Pengumuman Hasil:** 15 Juli 2027"
      );
    }

    if (q.includes("snbp") || q.includes("prestasi")) {
      return (
        "Pendaftaran **Jalur SNBP (Prestasi)** dibuka pada **3 Februari 2027** sampai **4 Maret 2027**.\n\n" +
        "• **Periode Pendaftaran:** 3 Februari – 4 Maret 2027\n" +
        "• **Biaya Pendaftaran:** Gratis (Bebas Biaya)\n" +
        "• **Metode Seleksi:** Penilaian prestasi akademik nilai rapor semester 1–5 dan sertifikat prestasi."
      );
    }

    if (q.includes("pengumuman") || q.includes("hasil") || q.includes("lulus")) {
      return (
        "Pengumuman hasil seleksi seluruh jalur PMB Universitas ADMITRA diumumkan serentak pada **15 Juli 2027** langsung di dashboard akun masing-masing pendaftar."
      );
    }

    return (
      "Berikut adalah Jadwal Resmi Penerimaan Mahasiswa Baru Universitas ADMITRA 2027/2028:\n\n" +
      "1. **Jalur SNBP (Prestasi):** 3 Februari – 4 Maret 2027\n" +
      "2. **Jalur SNBT (Ujian UTBK):** 1 – 15 April 2027\n" +
      "3. **Seleksi Mandiri (CBT Kampus):** 1 Mei – 30 Juni 2027 (2 Gelombang)\n" +
      "4. **Pengumuman Kelulusan:** 15 Juli 2027\n" +
      "5. **Registrasi Ulang & UKT:** Mulai 1 Agustus 2027"
    );
  }

  // 2. INTENT: PERSYARATAN BERKAS & DOKUMEN WAJIB / ATURAN UPLOAD
  if (
    q.includes("berkas") ||
    q.includes("dokumen") ||
    q.includes("syarat") ||
    q.includes("persyaratan") ||
    q.includes("upload") ||
    q.includes("unggah") ||
    q.includes("ktp") ||
    q.includes("rapor") ||
    q.includes("ijazah") ||
    q.includes("skl") ||
    q.includes("format") ||
    q.includes("ukuran") ||
    q.includes("mb") ||
    q.includes("slip") ||
    q.includes("penghasilan") ||
    q.includes("foto")
  ) {
    // Sub-pertanyaan: Jika belum ada ijazah
    if (q.includes("belum") && (q.includes("ijazah") || q.includes("lulus"))) {
      return (
        "Bagi calon mahasiswa yang ijazahnya belum terbit (misal lulusan 2027):\n\n" +
        "• Anda dapat mengunggah **Surat Keterangan Lulus (SKL)** resmi dari sekolah yang memuat identitas dan nilai.\n" +
        "• Format file yang didukung: **PDF atau JPG** dengan ukuran maksimal **5MB**.\n" +
        "• Ijazah asli nantinya dapat disusulkan saat registrasi ulang setelah diterima."
      );
    }

    // Sub-pertanyaan: Format atau ukuran file
    if (q.includes("format") || q.includes("ukuran") || q.includes("mb") || q.includes("size")) {
      return (
        "Ketentuan format & ukuran file dokumen pendaftaran ADMITRA:\n\n" +
        "• **Pas Foto Formal:** Format JPG / PNG (maksimal 5MB).\n" +
        "• **KTP / Kartu Keluarga:** Format PDF / JPG (maksimal 5MB).\n" +
        "• **Ijazah / SKL:** Format PDF / JPG (maksimal 5MB).\n" +
        "• **Scan Rapor (Semester 1–5):** Wajib digabung menjadi 1 file PDF (maksimal 5MB).\n" +
        "• **Slip Penghasilan (Jalur Mandiri):** Format PDF / JPG (maksimal 5MB).\n\n" +
        "💡 Tips: Jika ukuran file Anda melebihi 5MB, silakan kompres terlebih dahulu sebelum mengunggah."
      );
    }

    // Sub-pertanyaan: Slip gaji / penghasilan
    if (q.includes("slip") || q.includes("penghasilan") || q.includes("gaji")) {
      return (
        "Ketentuan Surat Keterangan Penghasilan / Slip Gaji:\n\n" +
        "• **Wajib untuk:** Pendaftar **Jalur Mandiri** guna verifikasi penetapan kelompok UKT berkeadilan.\n" +
        "• **Dokumen yang diterima:** Slip gaji resmi orang tua dari instansi/kantor, ATAU Surat Keterangan Penghasilan dari Kelurahan/Desa bagi pekerja wiraswasta/informal.\n" +
        "• **Format:** PDF atau JPG (maksimal 5MB)."
      );
    }

    return (
      "Berikut adalah daftar dokumen persyaratan resmi yang wajib diunggah pada dashboard pendaftar:\n\n" +
      "📄 DOKUMEN UTAMA (SEMUA JALUR):\n" +
      "1. **Pas Foto Formal:** Berlatar belakang polos, pakaian rapi (format JPG/PNG, maks. 5MB).\n" +
      "2. **KTP / Kartu Keluarga:** Scan dokumen asli jelas terbaca (format PDF/JPG, maks. 5MB).\n" +
      "3. **Ijazah / SKL:** Ijazah SMA/SMK sederajat atau Surat Keterangan Lulus resmi bagi lulusan 2027.\n" +
      "4. **Scan Rapor:** Nilai rapor semester 1 sampai 5 digabung dalam 1 file PDF.\n\n" +
      "📑 DOKUMEN KHUSUS JALUR MANDIRI:\n" +
      "5. **Surat Keterangan Penghasilan:** Slip gaji atau surat keterangan penghasilan orang tua dari kelurahan (diperlukan untuk penentuan kelompok UKT berkeadilan).\n\n" +
      "💡 Ketentuan Unggah: Pastikan semua dokumen tidak buram, tidak terpotong, dan ukuran file di bawah 5MB agar verifikasi berkas berjalan cepat."
    );
  }

  // 3. INTENT: PENELUSURAN UKT & PROGRAM STUDI SPESIFIK (e.g. Teknik Mesin, Kedokteran, dll.)
  const prodiCocok = temukanProdiDariQuery(q);
  const isTanyaUktAtauBiaya =
    q.includes("ukt") ||
    q.includes("biaya") ||
    q.includes("kuliah") ||
    q.includes("spp") ||
    q.includes("bayar") ||
    q.includes("semester") ||
    q.includes("tarif") ||
    q.includes("berapa");

  if (prodiCocok && isTanyaUktAtauBiaya) {
    const [gol1, gol2, gol3] = prodiCocok.ukt;
    return (
      `Rincian Uang Kuliah Tunggal (UKT) Program Studi **${prodiCocok.jenjang} ${prodiCocok.nama}**:\n\n` +
      `• **Fakultas:** ${prodiCocok.fakultas}\n` +
      `• **Jenjang:** ${prodiCocok.jenjang}\n` +
      `• **Akreditasi:** ${prodiCocok.akreditasi}\n\n` +
      `Tarif UKT per Semester (Berdasarkan Kategori Penghasilan Keluarga per Tanggungan):\n` +
      `1. **Golongan 1:** ${rupiah.format(gol1)} / semester\n` +
      `   *(Penghasilan orang tua per tanggungan di bawah Rp 1.000.000/bulan)*\n` +
      `2. **Golongan 2:** ${rupiah.format(gol2)} / semester\n` +
      `   *(Penghasilan orang tua per tanggungan Rp 1.000.000 s.d. Rp 2.500.000/bulan)*\n` +
      `3. **Golongan 3:** ${rupiah.format(gol3)} / semester\n` +
      `   *(Penghasilan orang tua per tanggungan di atas Rp 2.500.000/bulan)*\n\n` +
      `💡 **Beasiswa KIP-Kuliah:** Mahasiswa penerima KIP-Kuliah dibebaskan dari biaya UKT (**Rp 0 / Gratis 100%**).\n\n` +
      `Anda juga dapat mencoba fitur Kalkulator Simulasi UKT di beranda utama untuk melihat estimasi pengelompokan biaya kuliah Anda secara otomatis.`
    );
  }

  if (prodiCocok) {
    return (
      `Program Studi **${prodiCocok.jenjang} ${prodiCocok.nama}** resmi dibuka pada PMB Universitas ADMITRA 2027/2028:\n\n` +
      `• **Fakultas:** ${prodiCocok.fakultas}\n` +
      `• **Jenjang:** ${prodiCocok.jenjang}\n` +
      `• **Akreditasi:** ${prodiCocok.akreditasi}\n` +
      `• **Tarif UKT:** ${rupiah.format(prodiCocok.ukt[0])} s.d. ${rupiah.format(prodiCocok.ukt[2])} / semester\n\n` +
      `Jalur seleksi yang dapat dipilih: **SNBP** (Prestasi rapor), **SNBT** (Tes UTBK), dan **Seleksi Mandiri** (Ujian CBT Kampus).`
    );
  }

  // 4. INTENT: BIAYA PENDAFTARAN JALUR SELEKSI
  if (
    q.includes("pendaftaran") ||
    q.includes("daftar") ||
    q.includes("formulir") ||
    q.includes("biaya") ||
    q.includes("tarif") ||
    q.includes("bayar") ||
    q.includes("rp")
  ) {
    return (
      "Rincian biaya pendaftaran PMB Universitas ADMITRA 2027/2028:\n\n" +
      "• **Jalur SNBP (Prestasi):** Gratis / Bebas Biaya Pendaftaran\n" +
      "• **Jalur SNBT (Ujian Tertulis):** Rp 200.000\n" +
      "• **Jalur Mandiri (CBT Mandiri):** Rp 350.000\n\n" +
      "Pembayaran dapat dilakukan melalui Virtual Account bank mitra resmi setelah Anda melengkapi biodata pendaftaran."
    );
  }

  // 5. INTENT: PERTANYAAN ALASAN / KENAPA GITU
  if (
    q.includes("kenapa") ||
    q.includes("mengapa") ||
    q.includes("alasannya") ||
    q.includes("gitu") ||
    q.includes("alasan")
  ) {
    return (
      "Penetapan golongan dan tarif UKT di Universitas ADMITRA didasarkan pada prinsip keadilan sosial dan kebutuhan pembelajaran:\n\n" +
      "1. **Prinsip Subsidi Silang:** Golongan 1 (Rp 500.000) dialokasikan agar calon mahasiswa berprestasi dari keluarga kurang mampu dapat menempuh pendidikan tinggi tanpa hambatan biaya.\n" +
      "2. **Kebutuhan Fasilitas & Praktikum:** Program studi rumpun teknik (seperti Teknik Mesin, Elektro, Sipil) dan kedokteran memiliki biaya praktikum mesin dan laboratorium yang lebih tinggi dibandingkan rumpun sosial.\n" +
      "3. **Evaluasi Finansial Objektif:** Golongan ditentukan murni dari pembagian total penghasilan kotor orang tua dengan jumlah tanggungan keluarga yang valid saat verifikasi berkas.\n\n" +
      "Ada hal lain seputar program studi atau pendaftaran yang ingin Anda ketahui?"
    );
  }

  // 6. INTENT: PROGRAM STUDI & FAKULTAS UMUM
  if (
    q.includes("prodi") ||
    q.includes("jurusan") ||
    q.includes("fakultas") ||
    q.includes("kuota") ||
    q.includes("program studi") ||
    q.includes("studi")
  ) {
    return (
      `Universitas ADMITRA membuka **64 Program Studi** yang tersebar di **12 Fakultas** untuk tahun akademik 2027/2028:\n\n` +
      `• **Fakultas Teknik:** Teknik Mesin, Teknik Sipil, Teknik Elektro, Teknik Industri, Arsitektur, dll.\n` +
      `• **Fakultas Ilmu Komputer:** Teknik Informatika, Sistem Informasi, Sains Data, Keamanan Siber, dll.\n` +
      `• **Fakultas Ekonomi dan Bisnis:** Akuntansi, Manajemen, Bisnis Digital, Ekonomi Pembangunan, dll.\n` +
      `• **Fakultas Kedokteran & Kesehatan:** Pendidikan Dokter, Farmasi, Keperawatan, Gizi, Kebidanan.\n` +
      `• **Fakultas Hukum:** Ilmu Hukum, Hukum Bisnis, Hukum Internasional.\n` +
      `• Serta Fakultas MIPA, Pertanian, FISIP, Psikologi, FIB, dan FKIP.\n\n` +
      `Ketik nama jurusan spesifik (misal: *\"UKT Teknik Mesin\"* atau *\"Syarat Kedokteran\"*) untuk informasi detail program studi!`
    );
  }

  // 7. INTENT: UKT SECARA UMUM
  if (
    q.includes("ukt") ||
    q.includes("kuliah") ||
    q.includes("spp") ||
    q.includes("semester")
  ) {
    return (
      "Penentuan Uang Kuliah Tunggal (UKT) di Universitas ADMITRA dihitung dari penghasilan orang tua dibagi jumlah tanggungan:\n\n" +
      "• **Golongan 1:** Rp 500.000 / semester (Semua prodi, jika per orang < Rp 1 juta)\n" +
      "• **Golongan 2:** Rp 2.000.000 – Rp 5.000.000 / semester (Tergantung rumpun keilmuan)\n" +
      "• **Golongan 3:** Rp 4.000.000 – Rp 14.000.000 / semester (Tergantung rumpun keilmuan)\n\n" +
      "💡 Calon mahasiswa dapat menggunakan fitur **Kalkulator Simulasi UKT** di beranda portal untuk menghitung estimasi golongan biaya kuliah Anda secara interaktif."
    );
  }

  // 8. DEFAULT PANDUAN RESMI
  return (
    "Halo! Selamat datang di Pusat Informasi PMB Universitas ADMITRA 2027/2028.\n\n" +
    "Kami siap memberikan informasi resmi mengenai:\n" +
    "• **Jadwal Pembukaan Jalur:** SNBP (3 Feb), SNBT (1 Apr), Mandiri (1 Mei)\n" +
    "• **Biaya Pendaftaran & Rincian UKT 64 Program Studi**\n" +
    "• **Daftar 12 Fakultas & Persyaratan Dokumen Pendaftaran**\n\n" +
    "Silakan ketik pertanyaan Anda (misal: *\"Berapa UKT Teknik Mesin?\"* atau *\"Kapan pembukaan Mandiri?\"*)!"
  );
}
export async function POST(request) {
  try {
    const body = await request.json();
    const { message, history = [] } = body;

    if (!message || typeof message !== "string" || message.trim().length === 0) {
      return NextResponse.json(
        { success: false, error: "Pesan tidak boleh kosong" },
        { status: 400 }
      );
    }

    // Format percakapan untuk LLM
    const formattedMessages = [
      { role: "system", content: SYSTEM_PROMPT_KNOWLEDGE },
      ...history.slice(-6).map((h) => ({
        role: h.sender === "user" ? "user" : "assistant",
        content: String(h.text || ""),
      })),
      { role: "user", content: message.trim() },
    ];

    const aiResult = await kirimPesanAI(formattedMessages);

    if (!aiResult.success) {
      console.warn("[AI Chat Falling back]: Upstream error:", aiResult.error);
      // Fallback cerdas agar pengunjung tetap terlayani secara mulus
      const fallbackText = cariJawabanFallback(message);
      return NextResponse.json({
        success: true,
        reply: fallbackText,
        model: "admitra-knowledge-base (offline-fallback)",
        fallback: true,
      });
    }

    return NextResponse.json({
      success: true,
      reply: aiResult.content,
      model: aiResult.model,
    });
  } catch (err) {
    console.error("API /api/ai/chat error:", err);
    return NextResponse.json(
      { success: false, error: "Terjadi kesalahan internal server." },
      { status: 500 }
    );
  }
}
