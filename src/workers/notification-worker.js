import { Worker } from "bullmq";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const webpush = require("web-push");
import { prisma } from "../lib/prisma.js";
import { createRedisConnection } from "../lib/queue/redis.js";
import { QUEUE_NAME } from "../lib/queue/notifications.js";

// =============================================================================
// STANDALONE PMB BACKGROUND WORKER — WEB PUSH NOTIFICATION PROCESS
// Run: node src/workers/notification-worker.js (or npm run worker)
// =============================================================================

const VAPID_PUBLIC_KEY = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
const VAPID_PRIVATE_KEY = process.env.VAPID_PRIVATE_KEY;
const VAPID_SUBJECT = process.env.VAPID_SUBJECT || "mailto:panitia.pmb@universitas.ac.id";

if (!VAPID_PUBLIC_KEY || !VAPID_PRIVATE_KEY) {
  console.warn("⚠️ [Worker Warning] VAPID keys not configured in environment! Push dispatch will fail.");
} else {
  webpush.setVapidDetails(VAPID_SUBJECT, VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY);
  console.log("🔐 [Worker] VAPID authentication configured successfully.");
}

console.log("🚀 [Worker] Starting PMB Notification Worker...");
console.log(`📦 [Worker] Subscribing to BullMQ queue: "${QUEUE_NAME}"`);

const connection = createRedisConnection();

const worker = new Worker(
  QUEUE_NAME,
  async (job) => {
    const { targetId, targetType, title, body, url, tag } = job.data;
    console.log(`\n📨 [Worker Job #${job.id}] Processing notification for ${targetType}: ${targetId}`);
    console.log(`   Title: "${title}" | Body: "${body}" | URL: "${url}"`);

    const ownerFilter =
      targetType === "ADMIN"
        ? { adminId: targetId, aktif: true }
        : { mahasiswaId: targetId, aktif: true };

    // 1. Ambil semua perangkat aktif penerima dari database PostgreSQL
    const perangkatList = await prisma.perangkatNotifikasi.findMany({
      where: ownerFilter,
    });

    if (perangkatList.length === 0) {
      console.log(`ℹ️ [Worker] Tidak ada perangkat aktif untuk ${targetType} ID: ${targetId}`);
      return { sent: 0, reason: "NO_ACTIVE_DEVICES" };
    }

    console.log(`📱 [Worker] Ditemukan ${perangkatList.length} perangkat aktif untuk dikirimi Web Push.`);

    const notificationPayload = JSON.stringify({
      title,
      body,
      icon: "/admitra-mark.png",
      badge: "/admitra-mark-putih.png",
      tag: tag || "pmb-update",
      url: url || "/dashboard",
      timestamp: Date.now(),
    });

    let suksesCount = 0;
    let expiredCount = 0;

    for (const perangkat of perangkatList) {
      const pushSubscription = {
        endpoint: perangkat.endpoint,
        keys: {
          p256dh: perangkat.p256dh,
          auth: perangkat.authKey,
        },
      };

      try {
        await webpush.sendNotification(pushSubscription, notificationPayload);
        suksesCount++;
        // Update waktu terakhir dipakai
        await prisma.perangkatNotifikasi.update({
          where: { id: perangkat.id },
          data: { terakhirDipakai: new Date() },
        });
        console.log(`   ✅ [Push Sent] Endpoint ${perangkat.endpoint.slice(0, 35)}...`);
      } catch (err) {
        console.error(`   ❌ [Push Failed] Status: ${err.statusCode || "ERR"}, Message: ${err.message}`);

        // Jika endpoint sudah kedaluwarsa atau di-uninstall (HTTP 404 / 410 Gone)
        if (err.statusCode === 404 || err.statusCode === 410) {
          console.log(`   🧹 [Deactivating] Endpoint expired (HTTP ${err.statusCode}). Disabling record.`);
          await prisma.perangkatNotifikasi.update({
            where: { id: perangkat.id },
            data: { aktif: false },
          });
          expiredCount++;
        }
      }
    }

    console.log(`📊 [Worker Job #${job.id}] Selesai: ${suksesCount} terkirim, ${expiredCount} expired.\n`);
    return { sent: suksesCount, expired: expiredCount };
  },
  {
    connection,
    concurrency: 2,
    limiter: {
      max: 20,
      duration: 1000,
    },
  }
);

worker.on("completed", (job, returnvalue) => {
  console.log(`✨ [Worker] Job #${job.id} completed:`, returnvalue);
});

worker.on("failed", (job, err) => {
  console.error(`💥 [Worker] Job #${job.id} failed with error:`, err.message);
});

// Graceful shutdown handling
async function shutdown() {
  console.log("\n🛑 [Worker] Shutting down worker gracefully...");
  await worker.close();
  await connection.quit();
  await prisma.$disconnect();
  console.log("👋 [Worker] Exited cleanly.");
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
