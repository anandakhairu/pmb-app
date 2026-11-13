"use server";

import { z } from "zod";
import { prisma } from "../prisma.js";
import { enqueueNotificationJob } from "../queue/notifications.js";

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

      // 2. Update status formulir pendaftaran
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

      // 4. Enqueue BullMQ notification job
      if (kirimNotifikasi && formulirUpdate.mahasiswaId) {
        const pesanBody =
          statusBerkas === "TERVERIFIKASI"
            ? "Selamat! Berkas pendaftaran Anda telah dinyatakan VALID oleh panitia."
            : "Ada berkas yang memerlukan revisi. Silakan periksa catatan perbaikan di portal.";

        await enqueueNotificationJob({
          targetId: formulirUpdate.mahasiswaId,
          targetType: "MAHASISWA",
          title: statusBerkas === "TERVERIFIKASI" ? "Berkas Terverifikasi" : "Perlu Revisi Berkas",
          body: pesanBody,
          url: "/dashboard/berkas",
          tag: `pmb-verifikasi-${formulirId}`,
          deduplicationId: `${formulirId}-${statusBerkas}`,
        });
      }

      return formulirUpdate;
    });

    // Revalidate rute terkait
    await safeRevalidate("/admin");
    await safeRevalidate("/admin/verifikasi");
    await safeRevalidate(`/admin/verifikasi/${formulirId}`);
    await safeRevalidate("/dashboard");
    await safeRevalidate("/dashboard/berkas");

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
      // 1. Update profil mahasiswa
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
    });

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

      let nomor = formulir.nomorPendaftaran;
      if (!nomor) {
        try {
          const seqRes = await tx.$queryRaw`SELECT nextval('seq_nomor_pendaftaran') as seq`;
          const nextNum = Number(seqRes[0]?.seq || 1n);
          nomor = `PMB-2027-${String(nextNum).padStart(6, "0")}`;
        } catch {
          const count = await tx.formulirPendaftaran.count();
          nomor = `PMB-2027-${String(count + 1).padStart(6, "0")}`;
        }
      }

      return await tx.formulirPendaftaran.update({
        where: { id: formulirId },
        data: {
          nomorPendaftaran: nomor,
          statusBerkas: "DIKIRIM",
          finalisasiAt: new Date(),
          langkahTerakhir: 4,
        },
      });
    });

    await safeRevalidate("/dashboard/berkas");
    await safeRevalidate("/dashboard");
    await safeRevalidate("/admin/verifikasi");
    if (hasil.mahasiswaId) {
      await enqueueNotificationJob({
        targetId: hasil.mahasiswaId,
        targetType: "MAHASISWA",
        title: "Pendaftaran Berhasil Dikirim",
        body: `Formulir ${hasil.nomorPendaftaran} telah diterima panitia dan sedang antre verifikasi.`,
        url: "/dashboard",
        tag: `pmb-finalisasi-${formulirId}`,
        deduplicationId: `${formulirId}-finalisasi`,
      });
    }
    return { success: true, nomorPendaftaran: hasil.nomorPendaftaran };
  } catch (error) {
    console.error("Gagal finalisasi pendaftaran:", error);
    return {
      success: false,
      error: "Gagal memfinalisasi berkas pendaftaran. Silakan coba kembali.",
    };
  }
}
