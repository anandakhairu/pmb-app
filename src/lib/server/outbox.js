import { prisma } from "../prisma.js";

// =============================================================================
// TRANSACTIONAL OUTBOX HELPER (POSTGRESQL DURABLE NOTIFICATION INTENT)
// =============================================================================

/**
 * Menyimpan event notifikasi ke dalam tabel outbox_notifikasi secara atomik
 * di dalam transaksi database yang sama dengan mutasi bisnis.
 *
 * @param {import('@prisma/client').Prisma.TransactionClient} tx
 * @param {Object} event
 * @param {string} event.targetId - UUID penerima (CalonMahasiswa / Admin)
 * @param {'MAHASISWA'|'ADMIN'} event.targetType
 * @param {string} event.judul - Judul notifikasi (ringkas, bebas PII)
 * @param {string} event.pesan - Isi notifikasi
 * @param {string} [event.url] - Deep link internal
 * @param {string} [event.tag] - Tag grouping
 * @param {string} event.idempotencyKey - Kunci unik idempotensi
 */
export async function simpanOutboxNotifikasi(tx, {
  targetId,
  targetType = "MAHASISWA",
  judul,
  pesan,
  url = "/dashboard",
  tag = "pmb-status",
  idempotencyKey,
}) {
  const client = tx || prisma;

  return await client.outboxNotifikasi.upsert({
    where: { idempotencyKey },
    create: {
      targetId,
      targetType,
      judul,
      pesan,
      url,
      tag,
      idempotencyKey,
      status: "PENDING",
    },
    update: {
      // Idempotent: jika sudah ada, tidak menduplikasi
    },
  });
}
