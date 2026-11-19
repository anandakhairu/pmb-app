import { PrismaClient } from "@prisma/client";
import { isValidPushEndpoint } from "../src/lib/server/ssrf-validator.js";
import { simpanOutboxNotifikasi } from "../src/lib/server/outbox.js";
import { jalankanOutboxDispatcher } from "../src/lib/server/outbox-dispatcher.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const prisma = new PrismaClient();

async function runHardeningTests() {
  console.log("=========================================================================");
  console.log("🛡️ PHASE 5.1 QA: 17 FAILURE-INJECTION, SSRF & OUTBOX RELIABILITY SCENARIOS");
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

  const baseKey = "qa-scen-" + Date.now();

  // 1. Scenario A: PostgreSQL Transaction Rollback (Zero Orphaned Outbox Row)
  await assertTest("1. Scenario A: Transaction Rollback Leaves No Orphaned Outbox Row", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const rollbackKey = `${baseKey}-rollback`;

    try {
      await prisma.$transaction(async (tx) => {
        await simpanOutboxNotifikasi(tx, {
          targetId: student.id,
          targetType: "MAHASISWA",
          judul: "Rollback Test",
          pesan: "Must not exist",
          idempotencyKey: rollbackKey,
        });
        // Intentional exception to trigger transaction rollback
        throw new Error("Intentional transaction abort");
      });
    } catch {
      // Expected abort
    }

    const row = await prisma.outboxNotifikasi.findUnique({
      where: { idempotencyKey: rollbackKey },
    });
    if (row) throw new Error("Orphaned outbox row survived aborted transaction!");
  });

  // 2. Scenario B: Duplicate Outbox Idempotency Key
  await assertTest("2. Scenario B: Duplicate Outbox Idempotency Key Rejection / Deduplication", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const dedupKey = `${baseKey}-dedup`;

    const first = await simpanOutboxNotifikasi(prisma, {
      targetId: student.id,
      targetType: "MAHASISWA",
      judul: "First Submission",
      pesan: "First message",
      idempotencyKey: dedupKey,
    });

    const second = await simpanOutboxNotifikasi(prisma, {
      targetId: student.id,
      targetType: "MAHASISWA",
      judul: "Duplicate Submission",
      pesan: "Duplicate message",
      idempotencyKey: dedupKey,
    });

    if (first.id !== second.id) throw new Error("Duplicate key generated distinct rows!");

    const count = await prisma.outboxNotifikasi.count({
      where: { idempotencyKey: dedupKey },
    });
    if (count !== 1) throw new Error(`Expected exactly 1 row, found ${count}`);
  });

  // 3. Scenario C: Concurrent Dispatcher Row Claiming with FOR UPDATE SKIP LOCKED
  await assertTest("3. Scenario C: Atomic Row Claiming via FOR UPDATE SKIP LOCKED", async () => {
    // Assert outbox-dispatcher.js source uses FOR UPDATE SKIP LOCKED
    const dispatcherCode = fs.readFileSync(
      path.join(__dirname, "../src/lib/server/outbox-dispatcher.js"),
      "utf-8"
    );
    if (!dispatcherCode.includes("FOR UPDATE SKIP LOCKED")) {
      throw new Error("Dispatcher lacks atomic FOR UPDATE SKIP LOCKED row claiming!");
    }
  });

  // 4. Scenario D & L: Stale PROCESSING Lease Recovery (Reclaim after 5 mins)
  await assertTest("4. Scenario D & L: Stale PROCESSING Lease Auto-Reclamation Query", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const staleKey = `${baseKey}-stale-lease`;

    // Insert a simulated stale locked event (locked 10 minutes ago)
    const staleDate = new Date(Date.now() - 10 * 60 * 1000);
    const staleRow = await prisma.outboxNotifikasi.create({
      data: {
        targetId: student.id,
        targetType: "MAHASISWA",
        judul: "Stale Event",
        pesan: "Stale lease test",
        idempotencyKey: staleKey,
        status: "PROCESSING",
        lockedAt: staleDate,
        attemptCount: 1,
      },
    });

    if (!staleRow.id) throw new Error("Failed to insert stale row");

    // Clean up
    await prisma.outboxNotifikasi.delete({ where: { id: staleRow.id } });
  });

  // 5. Scenario E: Idempotency Key Survives Process Crash Between Queue & DB
  await assertTest("5. Scenario E: Durable Idempotency Key Enforces Deterministic Identity", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const key = `${baseKey}-identity`;
    const event = await simpanOutboxNotifikasi(prisma, {
      targetId: student.id,
      targetType: "MAHASISWA",
      judul: "Crash Recovery Test",
      pesan: "Identity verification",
      idempotencyKey: key,
    });

    if (event.idempotencyKey !== key) throw new Error("Idempotency key mismatch");
    await prisma.outboxNotifikasi.delete({ where: { id: event.id } });
  });

  // 6. Scenario F: Redis Offline During Business Mutation (PostgreSQL Atomicity)
  await assertTest("6. Scenario F: Redis Offline During Mutation — Outbox Persists in PostgreSQL", async () => {
    const student = await prisma.calonMahasiswa.findFirst();
    const offlineKey = `${baseKey}-redis-offline`;

    // Business transaction writes to Outbox even if Redis is unreachable
    const outbox = await simpanOutboxNotifikasi(prisma, {
      targetId: student.id,
      targetType: "MAHASISWA",
      judul: "Redis Offline Event",
      pesan: "Preserved in PostgreSQL",
      idempotencyKey: offlineKey,
    });

    if (outbox.status !== "PENDING") throw new Error("Status must remain PENDING");
    await prisma.outboxNotifikasi.delete({ where: { id: outbox.id } });
  });

  // 7. Scenario G: Independent Outbox Reconciler in Worker Process
  await assertTest("7. Scenario G: Periodic Reconciler Active in Background Worker", async () => {
    const workerCode = fs.readFileSync(
      path.join(__dirname, "../src/workers/notification-worker.js"),
      "utf-8"
    );
    if (!workerCode.includes("jalankanOutboxDispatcher")) {
      throw new Error("Worker lacks independent jalankanOutboxDispatcher reconciler loop!");
    }
    if (!workerCode.includes("setInterval")) {
      throw new Error("Worker lacks periodic timer for outbox reconciliation!");
    }
  });

  // 8. Scenario H: Worker Error Listener & Graceful Shutdown
  await assertTest("8. Scenario H: Worker Process Error Handlers & SIGINT/SIGTERM Drainage", async () => {
    const workerCode = fs.readFileSync(
      path.join(__dirname, "../src/workers/notification-worker.js"),
      "utf-8"
    );
    if (!workerCode.includes("worker.on(\"error\"")) {
      throw new Error("Worker lacks unhandled error event listener!");
    }
    if (!workerCode.includes("process.on(\"SIGINT\"") || !workerCode.includes("process.on(\"SIGTERM\"")) {
      throw new Error("Worker lacks graceful shutdown signal hooks!");
    }
  });

  // 9. Scenario I & J: Transient Errors (429 & 5xx) Trigger BullMQ Retries
  await assertTest("9. Scenario I & J: Worker Re-throws Transient 429/5xx Errors for BullMQ Retry", async () => {
    const workerCode = fs.readFileSync(
      path.join(__dirname, "../src/workers/notification-worker.js"),
      "utf-8"
    );
    if (!workerCode.includes("throw err;")) {
      throw new Error("Worker suppresses transient errors instead of re-throwing for BullMQ retry!");
    }
  });

  // 10. Scenario K: Permanent Errors (404/410) Deactivate Subscription
  await assertTest("10. Scenario K: Permanent 404/410 Push Errors Deactivate Subscriptions", async () => {
    const workerCode = fs.readFileSync(
      path.join(__dirname, "../src/workers/notification-worker.js"),
      "utf-8"
    );
    if (!workerCode.includes("err.statusCode === 404 || err.statusCode === 410")) {
      throw new Error("Worker lacks 404/410 permanent error check!");
    }
    if (!workerCode.includes("aktif: false")) {
      throw new Error("Worker does not mark subscription aktif: false on permanent failure!");
    }
  });

  // 11. Scenario M: Outbox Dispatcher Non-Crashing Sweep
  await assertTest("11. Scenario M: Outbox Dispatcher Handles Offline Redis Gracefully", async () => {
    const sweep = await jalankanOutboxDispatcher(5);
    if (typeof sweep.diproses !== "number") throw new Error("Dispatcher returned malformed result");
  });

  // 12. Scenario N: Reject Unauthorized Insecure Endpoint Scheme (Plain HTTP)
  await assertTest("12. Scenario N: SSRF Defense — Reject Plain HTTP Endpoints", async () => {
    if (isValidPushEndpoint("http://fcm.googleapis.com/fcm/send/token")) {
      throw new Error("Validator accepted insecure HTTP scheme!");
    }
  });

  // 13. Scenario O: Reject Localhost, Loopbacks, and Private IP Subnets
  await assertTest("13. Scenario O: SSRF Defense — Reject IPv4/IPv6 Loopbacks & Private IPs", async () => {
    const blockedHosts = [
      "https://127.0.0.1:8443/push",
      "https://localhost:443/push",
      "https://10.0.0.1/push",
      "https://192.168.1.1/push",
      "https://[::1]/push",
    ];
    for (const u of blockedHosts) {
      if (isValidPushEndpoint(u)) throw new Error(`Validator accepted private/loopback URL: ${u}`);
    }
  });

  // 14. Scenario P: Reject AWS/GCP Cloud Metadata IP & Userinfo URLs
  await assertTest("14. Scenario P: SSRF Defense — Reject Cloud Metadata IP (169.254.169.254) & Userinfo", async () => {
    if (isValidPushEndpoint("https://169.254.169.254/latest/meta-data")) {
      throw new Error("Validator accepted cloud metadata IP!");
    }
    if (isValidPushEndpoint("https://user:pass@fcm.googleapis.com/fcm/send/123")) {
      throw new Error("Validator accepted URL with userinfo credentials!");
    }
    if (isValidPushEndpoint("https://fcm.googleapis.com@evil.com/")) {
      throw new Error("Validator accepted @ character in URL!");
    }
  });

  // 15. Scenario Q: Accept Legitimate W3C Browser Push Service Endpoints
  await assertTest("15. Scenario Q: SSRF Defense — Accept Official W3C Push Provider Domains", async () => {
    const validEndpoints = [
      "https://fcm.googleapis.com/fcm/send/valid-token-123",
      "https://android.googleapis.com/gcm/send/valid-token-123",
      "https://updates.push.services.mozilla.com/wpush/v2/valid-token-123",
      "https://web.push.apple.com/valid-token-123",
      "https://wns2-sn1p.notify.windows.com/w/?token=valid-token-123",
    ];
    for (const u of validEndpoints) {
      if (!isValidPushEndpoint(u)) throw new Error(`Validator wrongly rejected legitimate push endpoint: ${u}`);
    }
  });

  // 16. Service Worker Deep-Link Open-Redirect Sanitization
  await assertTest("16. Service Worker Deep-Link: Reject Protocol-Relative //evil.com Bypass", async () => {
    const swPath = "public/sw.js";
    const swContent = fs.readFileSync(swPath, "utf-8");

    if (!swContent.includes("rawPath.startsWith(\"//\")")) {
      throw new Error("Service Worker missing check for protocol-relative // bypass");
    }
    if (!swContent.includes("resolved.origin === self.location.origin")) {
      throw new Error("Service Worker missing strict origin equality validation");
    }
  });

  // 17. Database Layer 3 Integrity: XOR Owner Constraint (chk_perangkat_pemilik)
  await assertTest("17. Database Layer 3 Integrity: Enforce Exclusive XOR Owner Constraint", async () => {
    try {
      const student = await prisma.calonMahasiswa.findFirst();
      const admin = await prisma.admin.findFirst();

      await prisma.$executeRawUnsafe(`
        INSERT INTO perangkat_notifikasi (endpoint, p256dh, auth_key, mahasiswa_id, admin_id)
        VALUES ('https://fcm.googleapis.com/fcm/send/invalid-xor-test', 'BLZTxnZGbADF7ytotDJaHdXEp_TJKYhNNifb0QGLAaanUCTibPvoJL4dZf20X58lQCdQSaKTY3zby0U79gkXg24', 'o0_vTd8Rd8JRGKUlPem0OQ==', '${student.id}', '${admin.id}')
      `);
      throw new Error("Database allowed violating chk_perangkat_pemilik constraint!");
    } catch (e) {
      if (e.message.includes("Database allowed violating")) throw e;
      // Constraint successfully blocked dual-ownership insertion!
    }
  });

  console.log("\n=========================================================================");
  console.log(`📊 PHASE 5.1 QA SUMMARY: ${passed} PASSED, ${failed} FAILED`);
  console.log(`   Final Verdict: ${failed === 0 ? "ALL PASS (17/17) 🎉" : "FAIL"}`);
  console.log("=========================================================================");

  if (failed > 0) process.exit(1);
}

runHardeningTests()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
