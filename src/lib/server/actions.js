"use server";

import { z } from "zod";
import { prisma } from "../prisma.js";
import { simpanOutboxNotifikasi } from "./outbox.js";
import { jalankanOutboxDispatcher } from "./outbox-dispatcher.js";

// Safe wrapper untuk revalidatePath yang bekerja di Next.js maupun runner standalone test
async function safeRevalidate(path) {
  try {
    const { revalidatePath } = await import("next/cache");
    if (typeof revalidatePath === "function") {
      revalidatePath(path);
    }
  } catch {
    // Abaikan jika dipanggil dari luar runtime Next.js (mis. script pengujian QA)
  }
}

// =============================================================================
// SERVER ACTIONS: DATABASE PERSISTENCE & TIER 2 VALIDATION
// =============================================================================

const verifikasiSchema = z.object({
  formulirId: z.string().uuid("Formulir ID tidak valid"),
  statusBerkas: z.enum(["TERVERIFIKASI", "REVISI", "DALAM_REVIEW"]),
  catatanRevisi: z.string().nullable().optional(),
  hasilPerBerkas: z.record(
    z.string(),
    z.object({
      status: z.enum(["VALID", "REVISI", "MENUNGGU"]),
      catatan: z.string().optional().default(""),
    })
  ).optional(),
  kirimNotifikasi: z.boolean().default(true),
});

/**
 * Server Action: Menyimpan keputusan verifikasi berkas oleh admin ke database PostgreSQL.
 * Menggunakan transaksi atomik untuk mengupdate status formulir dan setiap berkas.
 */
export async function simpanVerifikasiBerkasAction(payload) {
  const parsed = verifikasiSchema.safeParse(payload);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.issues.map((i) => i.message).join(", "),
    };
  }

  const { formulirId, statusBerkas, catatanRevisi, hasilPerBerkas, kirimNotifikasi } = parsed.data;

  try {
    const hasil = await prisma.$transaction(async (tx) => {
      // 1. Ambil admin verifikator pertama yang aktif
      const admin = await tx.admin.findFirst({
        where: { aktif: true },
        select: { id: true, nama: true },
      });

      // 2. State Machine: Hanya formulir yang sudah dikirim yang dapat diverifikasi admin
      const existingForm = await tx.formulirPendaftaran.findUnique({
        where: { id: formulirId },
      });
      if (!existingForm) throw new Error("Formulir pendaftaran tidak ditemukan");
      if (existingForm.statusBerkas === "DRAFT") {
        throw new Error("Formulir masih berstatus DRAFT dan belum difinalisasi oleh pendaftar.");
      }

      // 3. Update status formulir pendaftaran
      const formulirUpdate = await tx.formulirPendaftaran.update({
        where: { id: formulirId },
        data: {
          statusBerkas,
          catatanRevisi: statusBerkas === "REVISI" ? catatanRevisi : null,
          verifikatorId: admin?.id || null,
          diverifikasiAt: new Date(),
        },
      });

      // 3. Update status verifikasi per-berkas jika ada data detail berkas
      if (hasilPerBerkas) {
        for (const [berkasId, detail] of Object.entries(hasilPerBerkas)) {
          await tx.berkasDokumen.updateMany({
            where: { id: berkasId, formulirId },
            data: {
              statusVerifikasi: detail.status,
              catatan: detail.catatan || null,
            },
          });
        }
      }

      // 4. Persist intent notifikasi secara atomik ke Transactional Outbox (PostgreSQL)
      if (kirimNotifikasi && formulirUpdate.mahasiswaId) {
        const pesanBody =
          statusBerkas === "TERVERIFIKASI"
            ? "Selamat! Berkas pendaftaran Anda telah dinyatakan VALID oleh panitia."
            : "Ada berkas yang memerlukan revisi. Silakan periksa catatan perbaikan di portal.";

        await simpanOutboxNotifikasi(tx, {
          targetId: formulirUpdate.mahasiswaId,
          targetType: "MAHASISWA",
          judul: statusBerkas === "TERVERIFIKASI" ? "Berkas Terverifikasi" : "Perlu Revisi Berkas",
          pesan: pesanBody,
          url: "/dashboard/berkas",
          tag: `pmb-verifikasi-${formulirId}`,
          idempotencyKey: `verif-${formulirId}-${statusBerkas}`,
        });
      }

      return formulirUpdate;
    }, { maxWait: 15000, timeout: 20000 });

    // Revalidate rute terkait
    await safeRevalidate("/admin");
    await safeRevalidate("/admin/verifikasi");
    await safeRevalidate(`/admin/verifikasi/${formulirId}`);
    await safeRevalidate("/dashboard");
    await safeRevalidate("/dashboard/berkas");

    // 5. Trigger outbox dispatcher di luar transaksi database (non-blocking)
    jalankanOutboxDispatcher(10).catch((err) => {
      console.warn("[Outbox] Dispatcher sweep deferred:", err.message);
    });

    return {
      success: true,
      data: {
        id: hasil.id,
        statusBerkas: hasil.statusBerkas,
        nomorPendaftaran: hasil.nomorPendaftaran,
      },
    };
  } catch (error) {
    console.error("Gagal simpan verifikasi berkas:", error);
    return {
      success: false,
      error: "Gagal menyimpan keputusan verifikasi. Silakan periksa kembali data Anda.",
    };
  }
}

const biodataSchema = z.object({
  mahasiswaId: z.string().uuid("Mahasiswa ID tidak valid"),
  namaLengkap: z.string().trim().min(3).max(150),
  nik: z.string().trim().regex(/^[0-9]{16}$/, "NIK harus 16 digit angka"),
  tempatLahir: z.string().trim().min(1).max(100),
  tanggalLahir: z.string().min(1),
  jenisKelamin: z.enum(["LAKI_LAKI", "PEREMPUAN"]),
  noHp: z.string().trim().regex(/^(\+62|62|0)8[0-9]{8,12}$/),
  alamat: z.string().trim().min(1),
  kotaKabupaten: z.string().trim().min(1).max(100),
  provinsi: z.string().trim().min(1).max(100),
  namaSekolah: z.string().trim().min(1).max(200),
  npsn: z.string().trim().regex(/^([0-9]{8})?$/).optional().nullable(),
  jenisSekolah: z.string().trim().min(1),
  jurusan: z.string().trim().min(1),
  tahunLulus: z.coerce.number().int().min(2000).max(2100),
  nilaiRataRata: z.coerce.number().min(0).max(100),
});

/**
 * Server Action: Menyimpan update biodata mahasiswa & data sekolah ke database.
 */
export async function simpanBiodataAction(formData) {
  const parsed = biodataSchema.safeParse(formData);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.issues.map((i) => i.message).join(", "),
    };
  }

  const data = parsed.data;

  try {
    await prisma.$transaction(async (tx) => {
      // 1. Verifikasi data calon mahasiswa dan kunci status
      const maba = await tx.calonMahasiswa.findUnique({
        where: { id: data.mahasiswaId },
        include: { formulir: true },
      });
      if (!maba) throw new Error("Data calon mahasiswa tidak ditemukan");
      if (maba.formulir?.[0]?.statusBerkas === "TERVERIFIKASI") {
        throw new Error("Biodata tidak dapat diubah karena formulir sudah terverifikasi.");
      }

      // 2. Update profil mahasiswa
      await tx.calonMahasiswa.update({
        where: { id: data.mahasiswaId },
        data: {
          namaLengkap: data.namaLengkap,
          nik: data.nik,
          tempatLahir: data.tempatLahir,
          tanggalLahir: new Date(data.tanggalLahir),
          jenisKelamin: data.jenisKelamin,
          noHp: data.noHp,
          alamat: data.alamat,
          kotaKabupaten: data.kotaKabupaten,
          provinsi: data.provinsi,
        },
      });

      // 2. Upsert data asal sekolah
      await tx.dataAsalSekolah.upsert({
        where: { mahasiswaId: data.mahasiswaId },
        update: {
          namaSekolah: data.namaSekolah,
          npsn: data.npsn || null,
          jenisSekolah: data.jenisSekolah,
          jurusan: data.jurusan,
          tahunLulus: data.tahunLulus,
          nilaiRataRata: data.nilaiRataRata,
        },
        create: {
          mahasiswaId: data.mahasiswaId,
          namaSekolah: data.namaSekolah,
          npsn: data.npsn || null,
          jenisSekolah: data.jenisSekolah,
          jurusan: data.jurusan,
          tahunLulus: data.tahunLulus,
          nilaiRataRata: data.nilaiRataRata,
        },
      });
    }, { maxWait: 15000, timeout: 20000 });

    await safeRevalidate("/dashboard/biodata");
    await safeRevalidate("/dashboard");

    return { success: true };
  } catch (error) {
    console.error("Gagal simpan biodata:", error);
    return {
      success: false,
      error: "Gagal menyimpan biodata. Silakan periksa kembali kelengkapan field.",
    };
  }
}

/**
 * Server Action: Finalisasi pengiriman berkas oleh pendaftar.
 */
export async function finalisasiPendaftaranAction(formulirId) {
  try {
    const hasil = await prisma.$transaction(async (tx) => {
      const formulir = await tx.formulirPendaftaran.findUnique({
        where: { id: formulirId },
        include: { berkas: true },
      });

      if (!formulir) throw new Error("Formulir tidak ditemukan");
      if (formulir.statusBerkas !== "DRAFT" && formulir.statusBerkas !== "REVISI") {
        throw new Error(`Pendaftaran tidak dapat difinalisasi karena status saat ini: ${formulir.statusBerkas}`);
      }

      let nomor = formulir.nomorPendaftaran;
      if (!nomor) {
        const seqRes = await tx.$queryRaw`SELECT nextval('seq_nomor_pendaftaran') as seq`;
        const nextNum = Number(seqRes[0]?.seq || 1n);
        nomor = `PMB-2027-${String(nextNum).padStart(6, "0")}`;
      }

      const updatedForm = await tx.formulirPendaftaran.update({
        where: { id: formulirId },
        data: {
          nomorPendaftaran: nomor,
          statusBerkas: "DIKIRIM",
          finalisasiAt: new Date(),
          langkahTerakhir: 4,
        },
      });

      // Persist intent notifikasi secara atomik ke Outbox
      if (updatedForm.mahasiswaId) {
        await simpanOutboxNotifikasi(tx, {
          targetId: updatedForm.mahasiswaId,
          targetType: "MAHASISWA",
          judul: "Pendaftaran Berhasil Dikirim",
          pesan: `Formulir ${updatedForm.nomorPendaftaran} telah diterima panitia dan sedang antre verifikasi.`,
          url: "/dashboard",
          tag: `pmb-finalisasi-${formulirId}`,
          idempotencyKey: `finalisasi-${formulirId}`,
        });
      }

      return updatedForm;
    }, { maxWait: 15000, timeout: 20000 });

    await safeRevalidate("/dashboard/berkas");
    await safeRevalidate("/dashboard");
    await safeRevalidate("/admin/verifikasi");
    // Trigger outbox dispatcher di luar transaksi database (non-blocking)
    jalankanOutboxDispatcher(10).catch((err) => {
      console.warn("[Outbox] Dispatcher sweep deferred:", err.message);
    });
    return { success: true, nomorPendaftaran: hasil.nomorPendaftaran };
  } catch (error) {
    console.error("Gagal finalisasi pendaftaran:", error);
    return {
      success: false,
      error: "Gagal memfinalisasi berkas pendaftaran. Silakan coba kembali.",
    };
  }
}

const toggleJalurSchema = z.object({
  kodeJalur: z.string().min(1, "Kode jalur wajib diisi"),
  aktif: z.boolean(),
  biayaPendaftaran: z.number().nonnegative().optional(),
});

/**
 * Server Action: Admin membuka atau menutup jalur pendaftaran (misal: Seleksi Mandiri)
 */
export async function toggleJalurPendaftaranAction(payload) {
  const parsed = toggleJalurSchema.safeParse(payload);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.issues[0]?.message || "Payload tidak valid",
    };
  }

  const { kodeJalur, aktif, biayaPendaftaran } = parsed.data;

  try {
    const updated = await prisma.jalurPendaftaran.update({
      where: { kode: kodeJalur },
      data: {
        aktif,
        ...(biayaPendaftaran !== undefined ? { biayaPendaftaran } : {}),
      },
    });

    await safeRevalidate("/admin/master-data");
    await safeRevalidate("/");
    await safeRevalidate("/dashboard");

    return {
      success: true,
      data: {
        kode: updated.kode,
        nama: updated.nama,
        aktif: updated.aktif,
        biaya: Number(updated.biayaPendaftaran),
      },
    };
  } catch (error) {
    console.error("Gagal mengubah status jalur pendaftaran:", error);
    return {
      success: false,
      error: "Gagal memperbarui status pendaftaran jalur: " + error.message,
    };
  }
}

/**
 * Server Action: Mendaftarkan profil CalonMahasiswa baru ke database Prisma
 */
export async function registrasiAkunAction({ authUserId, email, namaLengkap, noHp }) {
  try {
    const existing = await prisma.calonMahasiswa.findUnique({ where: { email } });
    if (existing) {
      return { success: false, error: "Email sudah terdaftar di sistem." };
    }

    const maba = await prisma.calonMahasiswa.create({
      data: {
        authUserId: authUserId || crypto.randomUUID(),
        email,
        namaLengkap,
        noHp,
      },
    });

    return { success: true, data: { id: maba.id, email: maba.email } };
  } catch (error) {
    console.error("Gagal registrasi akun:", error);
    return { success: false, error: "Gagal menyimpan data akun: " + error.message };
  }
}

/**
 * Server Action: Mengambil profil lengkap pengguna (nama lengkap asli sesuai database)
 */
export async function ambilProfilPenggunaAction(email) {
  if (!email) return null;
  const emailLower = email.toLowerCase().trim();

  try {
    // 1. Cek tabel Admin
    const admin = await prisma.admin.findFirst({
      where: { email: emailLower },
      select: { id: true, nama: true, email: true, role: true },
    });
    if (admin) {
      return {
        id: admin.id,
        email: admin.email,
        nama: admin.nama,
        role: "ADMIN",
      };
    }

    // 2. Cek tabel CalonMahasiswa (nama lengkap sesuai ijazah/biodata)
    const maba = await prisma.calonMahasiswa.findFirst({
      where: { email: emailLower },
      select: { id: true, namaLengkap: true, email: true },
    });
    if (maba) {
      return {
        id: maba.id,
        email: maba.email,
        nama: maba.namaLengkap,
        role: "PENDAFTAR",
      };
    }
  } catch (err) {
    console.error("Gagal ambil profil pengguna:", err.message);
  }

  // Fallback jika tidak ada di DB
  return {
    email: emailLower,
    nama: emailLower.split("@")[0],
    role: emailLower.includes("admin") ? "ADMIN" : "PENDAFTAR",
  };
}


