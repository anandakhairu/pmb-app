import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function runQaTests() {
  console.log("=================================================================");
  console.log("🧪 PHASE 4 QA AUTOMATION TEST: DATABASE INTEGRATION & CUTOVER");
  console.log("=================================================================\n");

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

  // 1. Applicant Profile Retrieval
  await assertTest("1. Applicant Profile Retrieval from Supabase", async () => {
    const student = await prisma.calonMahasiswa.findFirst({
      where: { email: "anindya.kirana@demo.admitra.id" },
      include: { asalSekolah: true, formulir: true },
    });
    if (!student) throw new Error("Student record not found");
    if (!student.namaLengkap.includes("Anindya")) throw new Error("Unexpected name: " + student.namaLengkap);
  });

  // 2. Admin Applicant List Retrieval with Relations
  await assertTest("2. Admin Applicant List & Relations Retrieval", async () => {
    const list = await prisma.formulirPendaftaran.findMany({
      include: { mahasiswa: true, prodi: true, jalur: true, berkas: true },
    });
    if (list.length < 5) throw new Error(`Expected at least 5 seeded forms, got ${list.length}`);
    const withProdi = list.filter((f) => f.prodi && f.prodi.nama);
    if (withProdi.length !== list.length) throw new Error("Missing prodi relation on forms");
  });

  // 3. Applicant Detail Retrieval by Form ID
  let sampleFormId = null;
  await assertTest("3. Applicant Detail Retrieval by Form ID", async () => {
    const form = await prisma.formulirPendaftaran.findFirst({
      where: { nomorPendaftaran: "PMB-2027-900004" }, // Dimas (REVISI)
      include: { mahasiswa: true, berkas: true },
    });
    if (!form) throw new Error("Form PMB-2027-900004 not found");
    sampleFormId = form.id;
  });

  // 4. Admin Verification Mutation (Atomic Status Update)
  await assertTest("4. Admin Verification Mutation & Atomic Status Transition", async () => {
    if (!sampleFormId) throw new Error("sampleFormId required from previous test");
    
    // Update status to DALAM_REVIEW
    const updated = await prisma.formulirPendaftaran.update({
      where: { id: sampleFormId },
      data: {
        statusBerkas: "DALAM_REVIEW",
        catatanRevisi: "Berkas sedang dalam antrean review kedua panitia.",
        diverifikasiAt: new Date(),
      },
    });
    if (updated.statusBerkas !== "DALAM_REVIEW") throw new Error("Status was not updated");

    // Revert back to REVISI to preserve clean seed state
    await prisma.formulirPendaftaran.update({
      where: { id: sampleFormId },
      data: {
        statusBerkas: "REVISI",
        catatanRevisi: "Scan rapor semester 3 terpotong di bagian bawah.",
      },
    });
  });

  // 5. Database Constraint: 16-Digit NIK Check
  await assertTest("5. Database Layer 3 Constraint: Reject Invalid NIK", async () => {
    try {
      // NIK only 10 digits (violates chk_maba_nik_16_digit)
      await prisma.$executeRawUnsafe(`
        INSERT INTO calon_mahasiswa (auth_user_id, email, nama_lengkap, nik)
        VALUES (gen_random_uuid(), 'test.invalid.nik@test.com', 'Test Invalid NIK', '12345')
      `);
      throw new Error("Database failed to enforce 16-digit NIK constraint!");
    } catch (e) {
      if (e.message.includes("Database failed to enforce")) throw e;
      // Constraint violation caught successfully!
    }
  });

  // 6. Database Constraint: Foreign Key RESTRICT on Master Data
  await assertTest("6. Database Constraint: RESTRICT on referenced MasterProdi", async () => {
    const prodiInUse = await prisma.programStudi.findFirst({
      where: { formulir: { some: {} } },
    });
    if (!prodiInUse) throw new Error("No active prodi with applications found");

    try {
      await prisma.programStudi.delete({ where: { id: prodiInUse.id } });
      throw new Error("Database allowed deleting ProgramStudi referenced by Formulir!");
    } catch (e) {
      if (e.message.includes("Database allowed deleting")) throw e;
      // RESTRICT constraint working as expected!
    }
  });

  // 7. Isolated Test Record Creation & Cascade Deletion
  await assertTest("7. Isolated Test Record: Insert & Cascade Cleanup", async () => {
    const testAuthId = "a0000000-0000-4000-8000-000000000099";
    const testEmail = "qa.temp.test@demo.admitra.id";

    // Clean up if already exists
    await prisma.calonMahasiswa.deleteMany({ where: { email: testEmail } });

    // Insert isolated test student
    const created = await prisma.calonMahasiswa.create({
      data: {
        authUserId: testAuthId,
        email: testEmail,
        namaLengkap: "QA Test Transient Student",
        nik: "3374019999990099",
        asalSekolah: {
          create: {
            namaSekolah: "SMK QA Automated 1",
            tahunLulus: 2026,
            nilaiRataRata: 89.5,
          },
        },
      },
    });

    if (!created.id) throw new Error("Failed to insert test student");

    // Clean up test record immediately
    const deleted = await prisma.calonMahasiswa.delete({ where: { id: created.id } });
    if (!deleted) throw new Error("Failed to delete test student");
  });

  // 8. Server Action Validation: Reject Invalid Payload
  await assertTest("8. Server-Side Validation: Reject Malformed Verification Payload", async () => {
    const { simpanVerifikasiBerkasAction } = await import("../src/lib/server/actions.js");
    const badResult = await simpanVerifikasiBerkasAction({
      formulirId: "invalid-not-uuid",
      statusBerkas: "INVALID_STATUS_STRING",
    });
    if (badResult.success !== false) throw new Error("Server action accepted malformed payload!");
  });

  // 9. Master Data Consistency
  await assertTest("9. Master Data Consistency (Prodi & Jalur)", async () => {
    const prodis = await prisma.programStudi.findMany();
    const jalurs = await prisma.jalurPendaftaran.findMany();
    if (prodis.length === 0) throw new Error("Master Prodi is empty");
    if (jalurs.length === 0) throw new Error("Master Jalur is empty");
  });

  // 10. Database Connection Pool & PgBouncer Health
  await assertTest("10. Database Connection Health via PgBouncer Pooler", async () => {
    const result = await prisma.$queryRaw`SELECT 1 as ping`;
    if (!result || result[0].ping !== 1) throw new Error("Ping failed");
  });

  console.log("\n=================================================================");
  console.log(`📊 QA SUMMARY: ${passed} PASSED, ${failed} FAILED`);
  console.log(`   Final Verdict: ${failed === 0 ? "ALL PASS (10/10) 🎉" : "FAIL"}`);
  console.log("=================================================================");

  if (failed > 0) process.exit(1);
}

runQaTests()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
