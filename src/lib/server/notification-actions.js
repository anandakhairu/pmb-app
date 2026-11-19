"use server";

import { z } from "zod";
import { prisma } from "../prisma.js";
import { isValidPushEndpoint } from "./ssrf-validator.js";

// =============================================================================
// SERVER ACTIONS: SUBSCRIPTION LIFECYCLE (PERANGKAT NOTIFIKASI)
// =============================================================================



const subscriptionSchema = z.object({
  endpoint: z
    .string()
    .url("URL endpoint push tidak valid")
    .startsWith("https://", "Endpoint harus HTTPS")
    .refine((url) => isValidPushEndpoint(url), {
      message: "Endpoint bukan push service browser resmi yang diizinkan (SSRF Protection)",
    }),
  p256dh: z.string().min(60, "Kunci p256dh harus minimal 60 karakter base64url").max(150),
  authKey: z.string().min(16, "Kunci auth harus minimal 16 karakter base64url").max(60),
  userAgent: z.string().max(500).optional().nullable(),
  userType: z.enum(["MAHASISWA", "ADMIN"]).default("MAHASISWA"),
  userId: z.string().uuid("ID Pengguna tidak valid").optional(),
});

/**
 * Mendaftarkan atau memperbarui langganan Web Push perangkat di database
 */
export async function daftarkanPerangkatAction(payload) {
  const parsed = subscriptionSchema.safeParse(payload);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.issues.map((i) => i.message).join(", "),
    };
  }

  const { endpoint, p256dh, authKey, userAgent, userType, userId } = parsed.data;

  try {
    let targetMahasiswaId = null;
    let targetAdminId = null;

    if (userType === "ADMIN") {
      if (userId) {
        const admin = await prisma.admin.findUnique({ where: { id: userId, aktif: true } });
        if (!admin) throw new Error("Otorisasi admin tidak sah atau akun tidak aktif");
        targetAdminId = admin.id;
      } else {
        const admin = await prisma.admin.findFirst({ where: { aktif: true } });
        if (!admin) throw new Error("Akun admin tidak ditemukan");
        targetAdminId = admin.id;
      }
    } else {
      if (userId) {
        const maba = await prisma.calonMahasiswa.findUnique({ where: { id: userId } });
        if (!maba) throw new Error("Otorisasi calon mahasiswa tidak sah");
        targetMahasiswaId = maba.id;
      } else {
        const maba = await prisma.calonMahasiswa.findFirst();
        if (!maba) throw new Error("Akun calon mahasiswa tidak ditemukan");
        targetMahasiswaId = maba.id;
      }
    }

    // Upsert atomic: set one foreign key and explicitly null the other to satisfy chk_perangkat_pemilik
    const device = await prisma.perangkatNotifikasi.upsert({
      where: { endpoint },
      create: {
        mahasiswaId: targetMahasiswaId,
        adminId: targetAdminId,
        endpoint,
        p256dh,
        authKey,
        userAgent: userAgent || null,
        aktif: true,
        terakhirDipakai: new Date(),
      },
      update: {
        mahasiswaId: targetMahasiswaId,
        adminId: targetAdminId,
        p256dh,
        authKey,
        userAgent: userAgent || null,
        aktif: true,
        terakhirDipakai: new Date(),
      },
    });

    console.log(`[Subscription] Perangkat ${device.id.slice(0, 8)}... berhasil didaftarkan untuk ${userType}`);
    return {
      success: true,
      data: {
        id: device.id,
        aktif: device.aktif,
      },
    };
  } catch (error) {
    console.error("Gagal mendaftarkan perangkat notifikasi:", error);
    return {
      success: false,
      error: "Gagal menyimpan langganan notifikasi. Silakan periksa kembali perangkat Anda.",
    };
  }
}

/**
 * Mencabut atau menonaktifkan langganan Web Push perangkat
 */
export async function hapusPerangkatAction(endpoint) {
  if (!endpoint || typeof endpoint !== "string") {
    return { success: false, error: "Endpoint tidak valid" };
  }

  try {
    await prisma.perangkatNotifikasi.updateMany({
      where: { endpoint },
      data: {
        aktif: false,
      },
    });
    return { success: true };
  } catch (error) {
    console.error("Gagal menonaktifkan perangkat notifikasi:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Mengecek status apakah endpoint browser ini sudah terdaftar dan aktif
 */
export async function cekStatusPerangkatAction(endpoint) {
  if (!endpoint || typeof endpoint !== "string") {
    return { terdaftar: false };
  }

  try {
    const device = await prisma.perangkatNotifikasi.findUnique({
      where: { endpoint },
      select: { id: true, aktif: true, terakhirDipakai: true },
    });
    return { terdaftar: !!device && device.aktif, id: device?.id };
  } catch {
    return { terdaftar: false };
  }
}
