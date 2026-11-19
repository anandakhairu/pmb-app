import { Queue } from "bullmq";
import { getProducerConnection } from "./redis.js";

// =============================================================================
// BULLMQ QUEUE & PRODUCER MODULE: PMB NOTIFICATIONS
// =============================================================================

export const QUEUE_NAME = "pmb-notifications";

let notificationQueue = null;

export function getNotificationQueue() {
  if (!notificationQueue) {
    notificationQueue = new Queue(QUEUE_NAME, {
      connection: getProducerConnection(),
      defaultJobOptions: {
        attempts: 3,
        backoff: {
          type: "exponential",
          delay: 2000,
        },
        removeOnComplete: {
          age: 86400, // Simpan histori sukses 24 jam
          count: 500,
        },
        removeOnFail: {
          age: 604800, // Simpan histori gagal 7 hari untuk audit
        },
      },
    });
  }
  return notificationQueue;
}

/**
 * Enqueue notification job to BullMQ
 * Menjamin idempotensi melalui jobId stabil
 *
 * @param {Object} params
 * @param {string} params.targetId - ID CalonMahasiswa atau Admin penerima
 * @param {'MAHASISWA'|'ADMIN'} params.targetType - Tipe penerima notifikasi
 * @param {string} params.title - Judul notifikasi (ringkas, formal)
 * @param {string} params.body - Isi notifikasi (tanpa PII sensitif)
 * @param {string} [params.url] - Deep link internal (misal: /dashboard/berkas)
 * @param {string} [params.tag] - Tag grouping notifikasi
 * @param {string} [params.deduplicationId] - ID unik event bisnis untuk mencegah notifikasi ganda
 */
export async function enqueueNotificationJob({
  targetId,
  targetType = "MAHASISWA",
  title,
  body,
  url = "/dashboard",
  tag = "pmb-status",
  deduplicationId,
}) {
  const queue = getNotificationQueue();

  const jobId = deduplicationId
    ? `notif-${targetId}-${deduplicationId}`
    : undefined;

  const jobPayload = {
    targetId,
    targetType,
    title,
    body,
    url,
    tag,
    timestamp: new Date().toISOString(),
  };

  try {
    const job = await queue.add("send-web-push", jobPayload, {
      jobId,
    });
    console.log(`[BullMQ] Job ${job.id} enqueued successfully for ${targetType}:${targetId}`);
    return { success: true, jobId: job.id };
  } catch (error) {
    console.error("[BullMQ] Gagal enqueue notifikasi:", error.message);
    // Kembalikan status gagal tanpa membatalkan transaksi bisnis utama
    return { success: false, error: error.message };
  }
}
