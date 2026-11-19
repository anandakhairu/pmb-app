import { prisma } from "../prisma.js";
import { enqueueNotificationJob } from "../queue/notifications.js";

// =============================================================================
// TRANSACTIONAL OUTBOX DISPATCHER WITH LEASE FENCING & OPTIMISTIC CONCURRENCY
// =============================================================================

/**
 * Menyapu event outbox berstatus PENDING atau macet (PROCESSING > 5 menit lalu),
 * menggunakan Lease Token unik per-klaim untuk mencegah stale dispatcher overwrite.
 *
 * @param {number} batchSize - Jumlah maksimal event per-sweep (default: 25)
 * @returns {Promise<{ diproses: number, sukses: number, gagal: number, preempted: number }>}
 */
export async function jalankanOutboxDispatcher(batchSize = 25) {
  try {
    // 1. Klaim baris secara atomik menggunakan PostgreSQL FOR UPDATE SKIP LOCKED
    // Setiap klaim menghasilkan lease_token baru (gen_random_uuid()) untuk fencing.
    const events = await prisma.$queryRaw`
      UPDATE outbox_notifikasi
      SET status = 'PROCESSING'::status_outbox,
          locked_at = NOW(),
          lease_token = gen_random_uuid(),
          attempt_count = attempt_count + 1,
          updated_at = NOW()
      WHERE id IN (
        SELECT id FROM outbox_notifikasi
        WHERE status = 'PENDING'::status_outbox
           OR (status = 'PROCESSING'::status_outbox AND locked_at < NOW() - INTERVAL '5 minutes' AND attempt_count < 5)
        ORDER BY created_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT ${batchSize}
      )
      RETURNING 
        id, 
        target_id as "targetId", 
        target_type as "targetType", 
        judul, 
        pesan, 
        url, 
        tag, 
        idempotency_key as "idempotencyKey", 
        attempt_count as "attemptCount",
        lease_token as "leaseToken";
    `;

    if (!events || events.length === 0) {
      return { diproses: 0, sukses: 0, gagal: 0, preempted: 0 };
    }

    let sukses = 0;
    let gagal = 0;
    let preempted = 0;

    for (const ev of events) {
      // 2. Publikasikan ke antrean BullMQ
      const res = await enqueueNotificationJob({
        outboxId: ev.id,
        targetId: ev.targetId,
        targetType: ev.targetType,
        title: ev.judul,
        body: ev.pesan,
        url: ev.url,
        tag: ev.tag || undefined,
        deduplicationId: ev.idempotencyKey,
      });

      if (res.success) {
        // 3. Conditional state transition: HANYA update jika lease_token dan status masih cocok!
        const updateResult = await prisma.$executeRaw`
          UPDATE outbox_notifikasi
          SET status = 'COMPLETED'::status_outbox,
              delivered_at = NOW(),
              updated_at = NOW()
          WHERE id = ${ev.id}::uuid
            AND status = 'PROCESSING'::status_outbox
            AND lease_token = ${ev.leaseToken}::uuid
        `;

        if (updateResult === 1) {
          sukses++;
        } else {
          // Lease telah diambil alih oleh dispatcher lain (preempted)!
          console.warn(`⚠️ [Outbox Fencing] Dispatcher kehilangan lease untuk event #${ev.id}. Pemilik lease baru dilindungi.`);
          preempted++;
        }
      } else {
        // Gagal enqueue ke Redis. Kembalikan ke PENDING dengan memverifikasi lease
        const retryResult = await prisma.$executeRaw`
          UPDATE outbox_notifikasi
          SET status = 'PENDING'::status_outbox,
              last_error = ${res.error || "Gagal enqueue ke Redis"},
              lease_token = NULL,
              updated_at = NOW()
          WHERE id = ${ev.id}::uuid
            AND status = 'PROCESSING'::status_outbox
            AND lease_token = ${ev.leaseToken}::uuid
        `;

        if (retryResult === 1) {
          gagal++;
        } else {
          console.warn(`⚠️ [Outbox Fencing] Gagal melepas lease retry untuk event #${ev.id} (telah di-takeover).`);
          preempted++;
        }
      }
    }

    return { diproses: events.length, sukses, gagal, preempted };
  } catch (err) {
    console.error("[OutboxDispatcher] Error during sweep:", err.message);
    return { diproses: 0, sukses: 0, gagal: 0, preempted: 0, error: err.message };
  }
}
