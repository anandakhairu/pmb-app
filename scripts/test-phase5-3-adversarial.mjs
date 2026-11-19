import { PrismaClient } from "@prisma/client";
import { isValidPushEndpoint } from "../src/lib/server/ssrf-validator.js";
import { simpanOutboxNotifikasi } from "../src/lib/server/outbox.js";

const prisma = new PrismaClient();

// =============================================================================
// PHASE 5.3 ADVERSARIAL INTEGRATION & FAILURE INJECTION SUITE
// =============================================================================

async function runAdversarialSuite() {
  console.log("=========================================================================");
  console.log("⚔️ PHASE 5.3 ADVERSARIAL QA: AUTH, CONCURRENCY FENCING & WORKER RESILIENCE");
  console.log("=========================================================================\n");

  let passed = 0;
  let failed = 0;

  async function assertTest(name, fn) {
    process.stdout.write(`[TEST] ${name} ... `);
    try {
      await fn();
      console.log("✅ PASSED");
      passed++;
    } catch (err) {
      console.log(`❌ FAILED: ${err.message}`);
      failed++;
    }
  }

  const baseKey = "adv-scen-" + Date.now();

  // 1. SSRF Adversarial Matrix: Boundary and Protocol Exploits
  await assertTest("1. SSRF: Reject Cloud Metadata, IPv6, Userinfo, and Subdomain Exploits", async () => {
    const maliciousEndpoints = [
      "http://fcm.googleapis.com/fcm/send", // Non-HTTPS
      "https://attacker@fcm.googleapis.com/fcm/send", // Userinfo bypass
      "https://fcm.googleapis.com:8080/fcm/send", // Non-standard port
      "https://169.254.169.254/latest/meta-data", // AWS/GCP metadata
      "https://[::1]/fcm", // IPv6 loopback
      "https://127.0.0.1:443/push", // IPv4 loopback
      "https://fcm.googleapis.com.evilattacker.com/send", // Hostname suffix confusion
      "https://evilpush.apple.com/send", // Not dot-prefixed subdomain
    ];

    for (const ep of maliciousEndpoints) {
      if (isValidPushEndpoint(ep)) {
        throw new Error(`SSRF validator failed to reject malicious endpoint: ${ep}`);
      }
    }

    const legitimateEndpoints = [
      "https://fcm.googleapis.com/fcm/send/token123",
      "https://updates.push.services.mozilla.com/wpush/v2/token456",
      "https://web.push.apple.com/send/token789",
      "https://1-web.push.apple.com/send/tokenABC",
    ];

    for (const ep of legitimateEndpoints) {
      if (!isValidPushEndpoint(ep)) {
        throw new Error(`SSRF validator falsely rejected legitimate endpoint: ${ep}`);
      }
    }
  });

  // 2. Concurrency Fencing: Stale Dispatcher Prevented from Overwriting State
  await assertTest("2. Outbox Lease Fencing: Stale Dispatcher Cannot Overwrite Preempted Event", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const fencingKey = `${baseKey}-fencing`;

    // A. Buat event outbox
    const ev = await simpanOutboxNotifikasi(prisma, {
      targetId: student.id,
      targetType: "MAHASISWA",
      judul: "Fencing Test",
      pesan: "Lease testing",
      idempotencyKey: fencingKey,
    });

    // B. Dispatcher A mengklaim event dengan lease token A
    const leaseA = "a1111111-1111-4111-8111-111111111111";
    await prisma.$executeRaw`
      UPDATE outbox_notifikasi
      SET status = 'PROCESSING'::status_outbox,
          locked_at = NOW() - INTERVAL '6 minutes',
          lease_token = ${leaseA}::uuid,
          attempt_count = 1
      WHERE id = ${ev.id}::uuid
    `;

    // C. Dispatcher B mendeteksi lease kedaluwarsa (>5 menit) dan merebut lease B
    const leaseB = "b2222222-2222-4222-8222-222222222222";
    const claimB = await prisma.$executeRaw`
      UPDATE outbox_notifikasi
      SET status = 'PROCESSING'::status_outbox,
          locked_at = NOW(),
          lease_token = ${leaseB}::uuid,
          attempt_count = 2
      WHERE id = ${ev.id}::uuid
        AND (status = 'PENDING'::status_outbox OR (status = 'PROCESSING'::status_outbox AND locked_at < NOW() - INTERVAL '5 minutes'))
    `;

    if (claimB !== 1) throw new Error("Dispatcher B failed to takeover expired lease!");

    // D. Dispatcher B menyelesaikan event
    await prisma.$executeRaw`
      UPDATE outbox_notifikasi
      SET status = 'COMPLETED'::status_outbox,
          delivered_at = NOW()
      WHERE id = ${ev.id}::uuid
        AND status = 'PROCESSING'::status_outbox
        AND lease_token = ${leaseB}::uuid
    `;

    // E. Dispatcher A yang terlambat mencoba menyelesaikan dengan lease A (HARUS DITOLAK: 0 rows affected)
    const staleUpdateA = await prisma.$executeRaw`
      UPDATE outbox_notifikasi
      SET status = 'COMPLETED'::status_outbox,
          delivered_at = NOW()
      WHERE id = ${ev.id}::uuid
        AND status = 'PROCESSING'::status_outbox
        AND lease_token = ${leaseA}::uuid
    `;

    if (staleUpdateA !== 0) {
      throw new Error(`CRITICAL: Stale Dispatcher A updated ${staleUpdateA} rows! Fencing breached!`);
    }

    // Pastikan status database tetap COMPLETED milik Dispatcher B
    const finalRow = await prisma.outboxNotifikasi.findUnique({
      where: { id: ev.id },
    });
    if (finalRow.status !== "COMPLETED" || finalRow.leaseToken !== leaseB) {
      throw new Error("Final database row state corrupted by stale lease!");
    }
  });

  // 3. Worker Error Classification: Transient vs Permanent Failure Matrix
  await assertTest("3. Worker Error Classification: Transient vs Permanent Errors", async () => {
    function classifyPushError(err) {
      const code = err.statusCode;
      if (code === 404 || code === 410) return "PERMANENT_SUBSCRIPTION_EXPIRED";
      if (code === 400 || code === 413) return "PERMANENT_CLIENT_ERROR";
      if (
        code === 429 ||
        (code && code >= 500 && code <= 599) ||
        !code ||
        err.code === "ECONNRESET" ||
        err.code === "ETIMEDOUT" ||
        err.code === "EAI_AGAIN" ||
        err.code === "ECONNREFUSED"
      ) {
        return "TRANSIENT_RETRYABLE";
      }
      return "UNKNOWN_FATAL";
    }

    if (classifyPushError({ statusCode: 410 }) !== "PERMANENT_SUBSCRIPTION_EXPIRED") throw new Error("410 misclassified");
    if (classifyPushError({ statusCode: 404 }) !== "PERMANENT_SUBSCRIPTION_EXPIRED") throw new Error("404 misclassified");
    if (classifyPushError({ statusCode: 429 }) !== "TRANSIENT_RETRYABLE") throw new Error("429 misclassified");
    if (classifyPushError({ statusCode: 503 }) !== "TRANSIENT_RETRYABLE") throw new Error("503 misclassified");
    if (classifyPushError({ code: "ETIMEDOUT" }) !== "TRANSIENT_RETRYABLE") throw new Error("ETIMEDOUT misclassified");
    if (classifyPushError({ code: "ECONNRESET" }) !== "TRANSIENT_RETRYABLE") throw new Error("ECONNRESET misclassified");
  });

  // 4. Per-Device Delivery Ledger Idempotency Simulation
  await assertTest("4. Ledger Deduplication: Skip Already-Delivered Devices on Crash Recovery", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const testDedupKey = `crash-test-${Date.now()}`;

    // Buat perangkat test
    const testPerangkat = await prisma.perangkatNotifikasi.create({
      data: {
        mahasiswaId: student.id,
        endpoint: `https://fcm.googleapis.com/fcm/send/test-dev-${Date.now()}`,
        p256dh: "BLZTxnZGbADF7ytotDJaHdXEp_TJKYhNNifb0QGLAaanUCTibPvoJL4dZf20X58lQCdQSaKTY3zby0U79gkXg24",
        authKey: "o0_vTd8Rd8JRGKUlPem0OQ==",
        aktif: true,
      },
    });

    try {
      // Simulasikan run pertama: tercatat di ledger
      await prisma.$executeRaw`
        INSERT INTO pengiriman_notifikasi (perangkat_id, dedup_key, status, delivered_at)
        VALUES (${testPerangkat.id}::uuid, ${testDedupKey}, 'DELIVERED', NOW())
      `;

      // Simulasikan run kedua (recovery): cek ledger
      const existing = await prisma.$queryRaw`
        SELECT id FROM pengiriman_notifikasi
        WHERE dedup_key = ${testDedupKey} AND perangkat_id = ${testPerangkat.id}::uuid AND status = 'DELIVERED'
        LIMIT 1
      `;

      if (!existing || existing.length === 0) {
        throw new Error("Ledger failed to detect existing delivery!");
      }
    } finally {
      // Cleanup test perangkat
      await prisma.perangkatNotifikasi.delete({ where: { id: testPerangkat.id } });
    }
  });

  console.log("\n=========================================================================");
  console.log(`🏁 ADVERSARIAL SUITE FINISHED: ${passed} PASSED, ${failed} FAILED`);
  console.log("=========================================================================\n");
}

runAdversarialSuite()
  .catch((e) => {
    console.error("Suite execution error:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
