import { PrismaClient } from "@prisma/client";

// Satu instance Prisma untuk seluruh aplikasi.
// Di mode development, Next.js memuat ulang modul berkali-kali; menyimpan
// instance di globalThis mencegah koneksi database menumpuk.
const globalForPrisma = globalThis;

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["warn", "error"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}