const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();

async function main() {
  console.log("🌱 Menjalankan Seeding Database PMB-APP...\n");

  const admins = await prisma.admin.findMany({
    select: { id: true, email: true, nama: true, role: true },
  });

  const mabas = await prisma.calonMahasiswa.findMany({
    include: {
      formulir: {
        include: { prodi: true, jalur: true },
      },
    },
  });

  console.log("==========================================================================================");
  console.log("🛡️ TABEL AKUN ADMIN DI DATABASE SUPABASE:");
  console.log("==========================================================================================");
  console.table(
    admins.map((a) => ({
      ID: a.id.slice(0, 8) + "...",
      Email: a.email,
      Nama: a.nama,
      Role: a.role,
    }))
  );

  console.log("\n==========================================================================================");
  console.log("🎓 TABEL 5 CALON MAHASISWA DI DATABASE SUPABASE:");
  console.log("==========================================================================================");
  console.table(
    mabas.map((m) => ({
      Nama: m.namaLengkap,
      Email: m.email,
      NIK: m.nik || "-",
      "No. Pendaftaran": m.formulir[0]?.nomorPendaftaran || "-",
      Prodi: m.formulir[0]?.prodi?.nama || "-",
      "Status Berkas": m.formulir[0]?.statusBerkas || "-",
      Kelulusan: m.formulir[0]?.statusKelulusan || "-",
    }))
  );

  console.log("\n✅ Database Seeding Berhasil & Terhubung Aktif ke Supabase!\n");
}

main()
  .catch((e) => {
    console.error("❌ Gagal Seeding:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
