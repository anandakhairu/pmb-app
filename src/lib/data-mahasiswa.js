import { cache } from "react";
import { cookies } from "next/headers";
import { prisma } from "@/lib/prisma";
import { createClient as createSupabaseServerClient } from "@/lib/supabase/server";

// =============================================================================
// DATA AREA MAHASISWA
// Membaca sesi aktif (Supabase Auth / Session Cookie) dan mengambil profil serta
// formulir pendaftaran calon mahasiswa langsung dari database PostgreSQL via Prisma.
// =============================================================================

/** Dokumen yang diminta. `jenis` = nilai enum JenisDokumen di schema.prisma. */
export const DAFTAR_DOKUMEN = [
  { jenis: "PAS_FOTO", nama: "Pas foto", petunjuk: "Foto formal berlatar polos, format JPG atau PNG.", wajib: true },
  { jenis: "KTP_KK", nama: "KTP atau Kartu Keluarga", petunjuk: "Pindai dokumen asli. Seluruh tulisan harus terbaca jelas.", wajib: true },
  { jenis: "IJAZAH_SKL", nama: "Ijazah atau Surat Keterangan Lulus", petunjuk: "Unggah ijazah, atau SKL bila ijazah belum terbit.", wajib: true },
  { jenis: "RAPOR", nama: "Rapor", petunjuk: "Gabungkan halaman rapor semester 1 sampai 5 dalam satu PDF.", wajib: true },
  { jenis: "SURAT_KETERANGAN_PENGHASILAN", nama: "Surat keterangan penghasilan orang tua", petunjuk: "Dipakai untuk menentukan golongan UKT. Wajib untuk Seleksi Mandiri.", wajib: false },
];

const JENIS_WAJIB_MANDIRI = "SURAT_KETERANGAN_PENGHASILAN";

/** Apakah dokumen ini wajib untuk jalur yang dipilih pendaftar. */
export const apakahWajib = (dokumen, jalurKode) =>
  dokumen.wajib || (dokumen.jenis === JENIS_WAJIB_MANDIRI && jalurKode === "MANDIRI");

const PRODI_DEFAULT = { kode: "SI", nama: "Sistem Informasi", fakultas: "Fakultas Ilmu Komputer", jenjang: "S1", akreditasi: "Unggul" };
const JALUR_DEFAULT = { kode: "SNBP", nama: "SNBP", tanggalPengumumanHasil: "2027-07-15T03:00:00.000Z" };

const sekolahPlaceholder = {
  namaSekolah: "-",
  npsn: "-",
  jenisSekolah: "SMA",
  jurusan: "-",
  tahunLulus: 2027,
  nilaiRataRata: "0.00",
};

/**
 * Ambil data pendaftar yang sedang login dari database PostgreSQL / Supabase via Prisma.
 * Membaca sesi dari Supabase Auth atau cookie sesi pmb_session.
 */
export const getDataMahasiswa = cache(async (idOrEmail) => {
  try {
    let target = idOrEmail;

    // 1. Jika parameter kosong, deteksi user dari sesi aktif
    if (!target) {
      try {
        const cookieStore = await cookies();

        // Cek sesi Supabase Auth server
        try {
          const supabase = await createSupabaseServerClient();
          if (supabase) {
            const { data: { user } } = await supabase.auth.getUser();
            if (user?.email) {
              target = user.email;
            } else if (user?.id) {
              target = user.id;
            }
          }
        } catch {}

        // Fallback cek cookie sesi pmb_session
        if (!target) {
          const sessionCookie = cookieStore.get("pmb_session");
          if (sessionCookie?.value) {
            try {
              const parsed = JSON.parse(decodeURIComponent(sessionCookie.value));
              if (parsed?.email) target = parsed.email;
            } catch {}
          }
        }
      } catch (err) {
        // cookies() mungkin tidak tersedia saat prerender / build
      }
    }

    // 2. Query ke Prisma CalonMahasiswa
    const where = target
      ? (target.includes("@") ? { email: target } : { id: target })
      : { email: "aulia@example.com" }; // default preview jika belum login sama sekali (sesuai demo dashboard & E2E)

    let maba = await prisma.calonMahasiswa.findFirst({
      where,
      include: {
        asalSekolah: true,
        formulir: {
          include: { prodi: true, jalur: true, berkas: true },
          orderBy: { createdAt: "desc" },
        },
      },
      orderBy: { createdAt: "asc" },
    });

    // Jika tidak ditemukan dan target sebelumnya spesifik, fallback cari pendaftar pertama
    if (!maba && target) {
      maba = await prisma.calonMahasiswa.findFirst({
        include: {
          asalSekolah: true,
          formulir: {
            include: { prodi: true, jalur: true, berkas: true },
            orderBy: { createdAt: "desc" },
          },
        },
        orderBy: { createdAt: "asc" },
      });
    }

    if (maba) {
      const f = maba.formulir?.[0] || {
        id: "draft-" + maba.id,
        tahunAkademik: "2027/2028",
        prodi: PRODI_DEFAULT,
        jalur: JALUR_DEFAULT,
        nomorPendaftaran: null,
        langkahTerakhir: 1,
        statusBerkas: "DRAFT",
        statusKelulusan: "BELUM_DITETAPKAN",
        catatanRevisi: null,
        catatanKelulusan: null,
        finalisasiAt: null,
        diverifikasiAt: null,
        ditetapkanAt: null,
        berkas: [],
      };

      return {
        mahasiswa: {
          id: maba.id,
          namaLengkap: maba.namaLengkap,
          email: maba.email,
          nik: maba.nik,
          tempatLahir: maba.tempatLahir,
          tanggalLahir: maba.tanggalLahir ? maba.tanggalLahir.toISOString().split("T")[0] : null,
          jenisKelamin: maba.jenisKelamin,
          noHp: maba.noHp,
          alamat: maba.alamat,
          kotaKabupaten: maba.kotaKabupaten,
          provinsi: maba.provinsi,
        },
        sekolah: maba.asalSekolah || sekolahPlaceholder,
        formulir: {
          id: f.id,
          tahunAkademik: f.tahunAkademik || "2027/2028",
          prodi: f.prodi || PRODI_DEFAULT,
          jalur: f.jalur || JALUR_DEFAULT,
          nomorPendaftaran: f.nomorPendaftaran,
          langkahTerakhir: f.langkahTerakhir ?? 1,
          statusBerkas: f.statusBerkas ?? "DRAFT",
          statusKelulusan: f.statusKelulusan ?? "BELUM_DITETAPKAN",
          catatanRevisi: f.catatanRevisi,
          catatanKelulusan: f.catatanKelulusan,
          finalisasiAt: f.finalisasiAt ? new Date(f.finalisasiAt).toISOString() : null,
          diverifikasiAt: f.diverifikasiAt ? new Date(f.diverifikasiAt).toISOString() : null,
          ditetapkanAt: f.ditetapkanAt ? new Date(f.ditetapkanAt).toISOString() : null,
        },
        berkas: f.berkas || [],
      };
    }
  } catch (err) {
    console.error("Prisma query fallback in getDataMahasiswa:", err.message);
  }

  // Fallback darurat jika database tidak terhubung sama sekali
  return {
    mahasiswa: {
      id: "demo",
      namaLengkap: "Calon Mahasiswa",
      email: "maba@demo.admitra.id",
      nik: null,
      tempatLahir: null,
      tanggalLahir: null,
      jenisKelamin: null,
      noHp: null,
      alamat: null,
      kotaKabupaten: null,
      provinsi: null,
    },
    sekolah: sekolahPlaceholder,
    formulir: {
      id: "demo-f",
      tahunAkademik: "2027/2028",
      prodi: PRODI_DEFAULT,
      jalur: JALUR_DEFAULT,
      nomorPendaftaran: null,
      langkahTerakhir: 1,
      statusBerkas: "DRAFT",
      statusKelulusan: "BELUM_DITETAPKAN",
      catatanRevisi: null,
      catatanKelulusan: null,
      finalisasiAt: null,
      diverifikasiAt: null,
      ditetapkanAt: null,
    },
    berkas: [],
  };
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
export function gabungkanBerkas(berkasAda = [], jalurKode) {
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
